# 任务：left18448 第 10801-10900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0109__7f4de138


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 10801-10900 行

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
left18448 第 10801-10900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	Vario	812 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2010	34209
Mercedes-benz	Vario	812 DT	Triebkopf	Heckantrieb	Diesel	Sep 1996	Jun 2006	100252
Mercedes-benz	Vario	813 D, 814 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34210
Mercedes-benz	Vario	813 D, 814 D	Kasten	Heckantrieb	Diesel	Sep 1996	Dec 2013	34211
Mercedes-benz	Vario	813 D, 814 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34212
Mercedes-benz	Vario	813 D, 814 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34390
Mercedes-benz	Vario	813 D, 814 D	Kasten	Heckantrieb	Diesel	Sep 1996	Dec 2013	34391
Mercedes-benz	Vario	813 D, 814 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34392
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34216
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Kasten	Allrad	Diesel	Sep 1996	Dec 2013	34217
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34218
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34396
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Kasten	Allrad	Diesel	Sep 1996	Dec 2013	34397
Mercedes-benz	Vario	813 DA, 814 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34398
Mercedes-benz	Vario	814 DT	Triebkopf	Heckantrieb	Diesel	Sep 1996	Jun 2006	34227
Mercedes-benz	Vario	815 D, 816 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2010	34213
Mercedes-benz	Vario	815 D, 816 D	Kasten	Heckantrieb	Diesel	Sep 1996	Dec 2010	34214
Mercedes-benz	Vario	815 D, 816 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	-	34215
Mercedes-benz	Vario	815 D, 816 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34393
Mercedes-benz	Vario	815 D, 816 D	Kasten	Heckantrieb	Diesel	Sep 1996	Dec 2013	34394
Mercedes-benz	Vario	815 D, 816 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 1996	Dec 2013	34395
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2010	34219
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Kasten	Allrad	Diesel	Sep 1996	Dec 2010	34220
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2010	34221
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34399
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Kasten	Allrad	Diesel	Sep 1996	Dec 2013	34400
Mercedes-benz	Vario	815 DA, 816 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 1996	Dec 2013	34401
Mercedes-benz	Vario	816 DT	Triebkopf	Heckantrieb	Diesel	Sep 1996	Jun 2006	34228
Mercedes-benz	Vario	818 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	-	34333
Mercedes-benz	Vario	818 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2006	-	34335
Mercedes-benz	Vario	818 D	Kasten	Heckantrieb	Diesel	Sep 2006	Dec 2013	34337
Mercedes-benz	Vario	818 DA 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Sep 2006	-	34334
Mercedes-benz	Vario	818 DA 4X4	Kipper	Allrad	Diesel	Sep 2006	-	34336
Mercedes-benz	Vario	O 810	Bus	Heckantrieb	Diesel	Sep 1996	Dec 2010	34222
Mercedes-benz	Vario	O 812	Bus	Heckantrieb	Diesel	Sep 1996	Dec 2010	34223
Mercedes-benz	Vario	O 813	Bus	Heckantrieb	Diesel	Jan 2006	Dec 2013	100307
Mercedes-benz	Vario	O 814	Bus	Heckantrieb	Diesel	Sep 1996	Dec 2010	34224
Mercedes-benz	Vario	O 815	Bus	Heckantrieb	Diesel	Sep 1996	Dec 2010	34225
Mercedes-benz	Vario	O 816 D	Bus	Heckantrieb	Diesel	Jan 2006	Dec 2013	100308
Mercedes-benz	Vario	O 818 D	Bus	Heckantrieb	Diesel	Sep 2006	-	100309
Mercedes-benz	Viano	3.2	Bus	Heckantrieb	Benzin	Sep 2003	-	17408
Mercedes-benz	Viano	3.2	Bus	Heckantrieb	Benzin	Sep 2003	-	17409
Mercedes-benz	Viano	3.7	Bus	Heckantrieb	Benzin	Jun 2004	-	18721
Mercedes-benz	Viano	3.7	Bus	Heckantrieb	Benzin	Jun 2004	Jul 2007	56150
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	Sep 2003	-	17410
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	Sep 2003	-	17411
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	Sep 2010	-	145126
Mercedes-benz	Viano	CDI 2.2 4-matic	Bus	Allrad	Diesel	Mar 2006	-	56751
Mercedes-benz	Vito	119	Bus	Heckantrieb	Benzin	Sep 2003	-	17416
Mercedes-benz	Vito	122	Bus	Heckantrieb	Benzin	Sep 2003	-	17419
Mercedes-benz	Vito	123	Bus	Heckantrieb	Benzin	Jun 2004	Jul 2008	18720
Mercedes-benz	Vito	123	Bus	Heckantrieb	Benzin	Jun 2004	Jul 2008	56151
Mercedes-benz	Vito	108 CDI 2.2	Bus	Frontantrieb	Diesel	Mar 1999	Jul 2003	11419
Mercedes-benz	Vito	108 CDI 2.2	Kasten	Frontantrieb	Diesel	Mar 1999	Jul 2003	14005
Mercedes-benz	Vito	108 D 2.3	Kasten	Frontantrieb	Diesel	Mar 1997	Jul 2003	11097
Mercedes-benz	Vito	109 CDI	Bus	Heckantrieb	Diesel	Sep 2003	-	18102
Mercedes-benz	Vito	109 CDI	Kasten	Frontantrieb	Diesel	Oct 2014	-	107503
Mercedes-benz	Vito	110 CDI	Kasten	Heckantrieb	Diesel	Oct 2021	-	145732
Mercedes-benz	Vito	110 CDI 2.2	Bus	Frontantrieb	Diesel	Mar 1999	Jul 2003	11420
Mercedes-benz	Vito	110 CDI 2.2	Kasten	Frontantrieb	Diesel	Mar 1999	Jul 2003	14006
Mercedes-benz	Vito	110 D 2.3	Kasten	Frontantrieb	Diesel	Mar 1997	Jul 2003	11098
Mercedes-benz	Vito	111 CDI	Bus	Heckantrieb	Diesel	Sep 2003	-	17417
Mercedes-benz	Vito	111 CDI	Kasten	Frontantrieb	Diesel	Oct 2014	-	107505
Mercedes-benz	Vito	112 CDI 2.2	Bus	Frontantrieb	Diesel	Mar 1999	Jul 2003	11421
Mercedes-benz	Vito	112 CDI 2.2	Kasten	Frontantrieb	Diesel	Mar 1999	Jul 2003	14007
Mercedes-benz	Vito	113 2.0	Kasten	Frontantrieb	Benzin	Mar 1997	Jul 2003	11099
Mercedes-benz	Vito	114 2.3	Bus	Frontantrieb	Benzin	Dec 1996	Jul 2003	7842
Mercedes-benz	Vito	114 2.3	Kasten	Frontantrieb	Benzin	Mar 1997	Jul 2003	11100
Mercedes-benz	Vito	114 CDI	Kasten	Heckantrieb	Diesel	Oct 2014	-	107506
Mercedes-benz	Vito	114 CDI 4X4	Kasten	Allrad	Diesel	Jul 2015	-	116117
Mercedes-benz	Vito	115 CDI	Bus	Heckantrieb	Diesel	Sep 2003	-	17418
Mercedes-benz	Vito	116 CDI	Kasten	Heckantrieb	Diesel	Oct 2014	-	107508
Mercedes-benz	Vito	116 CDI 4X4	Kasten	Allrad	Diesel	Jul 2015	-	116118
Mercedes-benz	Vito	119 CDI / Bluetec	Kasten	Heckantrieb	Diesel	Oct 2014	-	107510
Mercedes-benz	Vito	119 CDI / Bluetec 4X4	Kasten	Allrad	Diesel	Jul 2015	-	116119
Mercedes-benz	Vito	E-cell	Bus	Frontantrieb	Elektro	Mar 2012	-	59487
Mercedes-benz	Vito	Evito	Kasten	Frontantrieb	Elektro	Mar 2025	-	801624
Mercedes-benz	Vito / mixto	119	Kasten	Heckantrieb	Benzin	Sep 2003	Jul 2008	17414
Mercedes-benz	Vito / mixto	122	Kasten	Heckantrieb	Benzin	Sep 2003	Sep 2004	17415
Mercedes-benz	Vito / mixto	123	Kasten	Heckantrieb	Benzin	Jun 2004	Jul 2008	56153
Mercedes-benz	Vito / mixto	109 CDI	Kasten	Heckantrieb	Diesel	Sep 2003	Jul 2006	18101
Mercedes-benz	Vito / mixto	111 CDI	Kasten	Heckantrieb	Diesel	Sep 2003	Aug 2007	17413
Mercedes-benz	Vito / mixto	113 CDI 4X4	Kasten	Allrad	Diesel	Sep 2010	Aug 2014	59426
Mercedes-benz	Vito / mixto	115 CDI	Kasten	Heckantrieb	Diesel	Sep 2003	Aug 2014	17412
Mercedes-benz	Vito / mixto	116 CDI 4X4	Kasten	Allrad	Diesel	Sep 2010	Aug 2014	59428
Mercedes-benz	Vito / mixto	E-cell	Kasten	Frontantrieb	Elektro	Jan 2011	Aug 2014	59486
Mercedes-benz	Vito mixto	124	Kasten	Heckantrieb	Benzin/Elektro	May 2024	-	158825
Mercedes-benz	Vito mixto	109 CDI	Kasten	Frontantrieb	Diesel	Oct 2014	-	107511
Mercedes-benz	Vito mixto	110 CDI	Kasten	Heckantrieb	Diesel	Oct 2021	-	145733
Mercedes-benz	Vito mixto	111 CDI	Kasten	Frontantrieb	Diesel	Oct 2014	-	107512
Mercedes-benz	Vito mixto	114 CDI	Kasten	Heckantrieb	Diesel	Oct 2014	-	107513
Mercedes-benz	Vito mixto	114 CDI 4-matic	Kasten	Allrad	Diesel	Jul 2015	-	116120
Mercedes-benz	Vito mixto	116 CDI	Kasten	Heckantrieb	Diesel	Oct 2014	-	107514
Mercedes-benz	Vito mixto	116 CDI 4-matic	Kasten	Allrad	Diesel	Jul 2015	-	116121
Mercedes-benz	Vito mixto	119 Bluetec	Kasten	Heckantrieb	Diesel	Oct 2014	-	107515
Mercedes-benz	Vito mixto	119 Bluetec 4-matic	Kasten	Allrad	Diesel	Jul 2015	-	109296
Mercedes-benz	Vito mixto	124 CDI	Kasten	Heckantrieb	Diesel	Jan 2021	-	143284
Mercedes-benz	Vito mixto	124 CDI 4-matic	Kasten	Allrad	Diesel	Jan 2021	-	143285
Mercedes-benz	Vito tourer	124	Bus	Heckantrieb	Benzin/Elektro	May 2024	-	158821
Mercedes-benz	Vito tourer	109 CDI / 109 Bluetec	Bus	Frontantrieb	Diesel	Oct 2014	-	107516


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 **Viano W639** 车型簇的物理分支拆分，共闭合 8 个输入 Ktype、19 条 READY 映射。
* 已区分普通后驱与 4MATIC：4MATIC 车身高度明显不同，不能复用普通后驱尺寸组。
* 已按 Compact、Long、Extra Long 建立 8 个尺寸组。Mercedes-Benz 官方资料确认普通版 Compact/Long/Extra Long 车身代码边界及对应尺寸；TecDoc 车型目录用于确认各 Ktype 实际覆盖的车身代码。([marsClassic][1])
* Ktype `17408`、`17409`、`56150`、`18721`、`17410` 等覆盖范围已按车身代码拆分，未按发动机或普通配置重复建组。([Meyer Motoren][2])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：8
* READY 映射：19
* 待处理输入 Ktype：92
* 已确认尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17408_compact	17408	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支；同尺寸639.711 FUN包含在该分支。	READY
17408_long	17408	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
17409_long	17409	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支；同尺寸639.713 FUN包含在该分支。	READY
17409_extralong	17409	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18721	18721	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Ktype仅覆盖639.815 Extra Long车身。	READY
56150_compact	56150	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56150_long	56150	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
56150_extralong	56150	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17410_compact	17410	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支；同尺寸639.711 FUN包含在该分支。	READY
17410_long	17410	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支；同尺寸639.713 FUN包含在该分支。	READY
17410_extralong	17410	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17411_compact	17411	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支；同尺寸639.711 FUN包含在该分支。	READY
17411_long	17411	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支；同尺寸639.713 FUN包含在该分支。	READY
17411_extralong	17411	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
145126_compact	145126	MPV	Viano W639	639.711	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-FACELIFT-01	HIGH	改款后Compact FUN物理分支。	READY
145126_long	145126	MPV	Viano W639	639.713	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-FACELIFT-01	HIGH	改款后Long FUN物理分支。	READY
56751_compact	56751	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-4MATIC-PREFL-01	HIGH	4MATIC Compact分支；同尺寸639.711 FUN包含在该分支。	READY
56751_long	56751	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-4MATIC-PREFL-01	HIGH	4MATIC Long分支；同尺寸639.713 FUN包含在该分支。	READY
56751_extralong	56751	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-4MATIC-PREFL-01	HIGH	4MATIC Extra Long物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	4748	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 compact, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2003---2010.xhtml?oid=193898981
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	4993	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 long, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2003---2010.xhtml?oid=193898982
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	5223	1901	1872	Mercedes-Benz Public Archive - Viano CDI 2.2 extra long, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-extra-long-2003---2010.xhtml?oid=193898983
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-FACELIFT-01	4763	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 compact, 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2010---2014.xhtml?oid=193897440
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-FACELIFT-01	5008	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 long, 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2010---2014.xhtml?oid=193897441
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-4MATIC-PREFL-01	4748	1901	1942	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC compact, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-compact-2006---2010.xhtml?oid=193898984
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-4MATIC-PREFL-01	4993	1901	1942	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC long, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-long-2006---2010.xhtml?oid=193898985
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-4MATIC-PREFL-01	5223	1901	1939	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC extra long, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-extra-long-2006---2010.xhtml?oid=193898986
```

## 下一步优先处理

1. 闭合 Vito W638 的 Bus/Kasten 共用车壳和车身代码边界。
2. 按 Compact、Long、Extra Long及标准顶/高顶，批量处理 Vito W639 Bus、Kasten、Mixto 和 E-cell。
3. 处理 Vito W447 普通版、4×4、Mixto、Tourer、eVito及2024年后的更新分支。
4. 最后集中处理 Vario 的多轴距、标准顶/高顶、Kasten、底盘、Triebkopf及Bus分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2003---2010.xhtml?oid=193898981 "Viano CDI 2.2 compact, 2003 - 2010"
[2]: https://www.meyermotoren.de/fahrzeuge/17410/mercedes-benz/viano_w639_/cdi_2_2_639_711_639_713_639_811_639_813_639_815_17410?utm_source=chatgpt.com "CDI 2.2 (639.711, 639.713, 639.811, 639.813, 639.815) | Viano (W639) | Mercedes-Benz | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 Vito W638 改款后乘用客车车身簇，新增 3 个 Ktype 映射并共用一个尺寸组。Mercedes-Benz 官方档案确认 W638 Vito 与同期 V-Class 基本采用相同规格；官方 V 220 CDI 数据给出四门车身及 `4660 × 1880 × 1844 mm` 外廓。([marsClassic][1])
* `7842` 横跨改款前后，暂不在本轮建立单一映射，避免覆盖可能存在的改款前宽度差异。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：11
* READY 映射：22
* PENDING 输入 Ktype：89
* 已确认尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11419	11419	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638改款后乘用客车车身。	READY
11420	11420	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638改款后乘用客车车身。	READY
11421	11421	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638改款后乘用客车车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	4660	1880	1844	Mercedes-Benz Public Archive - 638 series V-Class Multi Purpose Vehicles 1999-2003; Mercedes-Benz Public Archive - V 220 CDI 1999-2003	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/638-series-V-Class-Multi-Purpose-Vehicles-1999---2003.xhtml?oid=5635;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/V-220-CDI-1999---2003.xhtml?oid=193665761
```

## 下一步优先处理

1. 闭合 Vito W638 Kasten 标准顶外廓。
2. 核对 `7842`、`11097`、`11098`、`11099`、`11100` 是否需要按改款前后拆分。
3. 随后批量处理 Vito W639 Compact、Long、Extra Long 的 Bus、Kasten 与 Mixto 分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/638-series-V-Class-Multi-Purpose-Vehicles-1999---2003.xhtml?oid=5635 "638 series V-Class Multi Purpose Vehicles, 1999 - 2003"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合剩余 **Vito W638** 输入车型，包括早期/后期 Bus 与 Kasten，共新增 8 个 READY 映射。
* W638 标准车身在1996—2003年间保持 `4660 × 1880 × 1844 mm` 外廓；发动机及1999年前后动力更新未形成新的标准车身尺寸分支，因此全部复用现有 W638 尺寸组。Mercedes-Benz 官方档案和 Auto-Data 的代际规格相互支持该判断。([marsClassic][1])
* Kasten 与 Bus 的封闭侧板、座椅及内部用途差异不改变车身最大外廓，本轮未重复创建同尺寸组。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：19
* READY 映射：30
* PENDING 输入 Ktype：81
* 已确认尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14005	14005	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11097	11097	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten；生产期跨越车型更新但外廓不变。	READY
14006	14006	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11098	11098	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten；生产期跨越车型更新但外廓不变。	READY
14007	14007	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11099	11099	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten；生产期跨越车型更新但外廓不变。	READY
7842	7842	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Bus；生产期跨越车型更新但外廓不变。	READY
11100	11100	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten；生产期跨越车型更新但外廓不变。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 按 Compact、Long、Extra Long 聚类处理 Vito W639 Bus。
2. 闭合 W639 Kasten、Mixto 与 E-cell 的标准顶和高顶边界。
3. 复用已确认的 W639 长度和宽度缓存，仅对 Vito 特有车高分支首次建组。
4. 随后处理 Vito W447 普通版、4×4、Mixto、Tourer及电动车分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/V-230-Turbodiesel-1996---1999.xhtml?oid=193665765&utm_source=chatgpt.com "V 230 Turbodiesel, 1996 - 1999"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Vito W639 的 Bus、Mixto、4X4 与 E-CELL 车型簇，新增 17 个已完成输入 Ktype、48 条 READY 映射。
* Bus 的 `639.701 / 639.703 / 639.705` 与 Mixto 的 `639.601 / 639.603 / 639.605` 分别对应 Compact、Long、Extra Long 物理分支。([Meyer Motoren][1])
* W639 改款前后车身长度分别按 `4748 / 4993 / 5223 mm` 与 `4763 / 5008 / 5238 mm` 建组；普通标准顶高度为 `1902 / 1902 / 1900 mm`。([Yumpu][2])
* E-CELL 统一为 Long 外廓 `5008 × 1901 × 1895 mm`；Kasten 与 Bus 复用同一物理尺寸组。
* W639 4X4 Kasten/Mixto 的 Compact、Long、Extra Long 高度分别闭合为 `1962 / 1962 / 1960 mm`。([Дром][3])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：36
* READY 映射：78
* PENDING 输入 Ktype：64
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17416_compact	17416	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17416_long	17416	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17416_extralong	17416	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17419_compact	17419	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17419_long	17419	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17419_extralong	17419	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18720	18720	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	仅覆盖Compact物理分支。	READY
56151_compact	56151	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56151_long	56151	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
56151_extralong	56151	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18102_compact	18102	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
18102_long	18102	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
18102_extralong	18102	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17417_compact	17417	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17417_long	17417	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17417_extralong	17417	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17418_compact	17418	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17418_long	17418	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17418_extralong	17418	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
59487	59487	MPV	Vito W639		4	EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	HIGH	E-CELL仅提供Long物理外廓。	READY
17414_compact	17414	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17414_long	17414	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17414_extralong	17414	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17415_compact	17415	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17415_long	17415	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17415_extralong	17415	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
56153_compact	56153	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56153_long	56153	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
56153_extralong	56153	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18101_compact	18101	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
18101_long	18101	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
18101_extralong	18101	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17413_compact	17413	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17413_long	17413	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17413_extralong	17413	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
59426_compact	59426	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	HIGH	4X4 Compact物理分支。	READY
59426_long	59426	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	HIGH	4X4 Long物理分支。	READY
59426_extralong	59426	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	HIGH	4X4 Extra Long物理分支。	READY
17412_compact_prefl	17412	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact改款前物理分支。	READY
17412_long_prefl	17412	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long改款前物理分支。	READY
17412_extralong_prefl	17412	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long改款前物理分支。	READY
17412_compact_facelift	17412	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-FACELIFT-01	HIGH	Compact改款后物理分支。	READY
17412_long_facelift	17412	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-FACELIFT-01	HIGH	Long改款后物理分支。	READY
17412_extralong_facelift	17412	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-FACELIFT-01	HIGH	Extra Long改款后物理分支。	READY
59428_compact	59428	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	HIGH	4X4 Compact物理分支。	READY
59428_long	59428	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	HIGH	4X4 Long物理分支。	READY
59428_extralong	59428	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	HIGH	4X4 Extra Long物理分支。	READY
59486	59486	Van	Vito W639		4	EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	HIGH	E-CELL仅提供Long物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	4748	1901	1902	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	4993	1901	1902	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	5223	1901	1900	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-FACELIFT-01	4763	1901	1902	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-FACELIFT-01	5008	1901	1902	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-FACELIFT-01	5238	1901	1900	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	4763	1901	1962	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L1H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77840/
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	5008	1901	1962	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L2H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77843/
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	5238	1901	1960	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L3H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77846/
EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	5008	1901	1895	Mercedes-Benz Vito E-CELL official brochure, 2011	https://manuals.plus/m/c431d8edfab37ad189fb516dad48accb05609bbc2732ac567b2cd43a41d1769d.pdf
```

## 下一步优先处理

1. 按 Compact、Long、Extra Long 聚类闭合 Vito W447 Kasten、Mixto 与 Tourer。
2. 独立处理 W447 4MATIC、2021动力更新、2024混动与2025 eVito 分支。
3. 完成后集中处理 Vario 的底盘、厢式、4X4、Triebkopf、Bus及多轴距/车顶组合。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/fahrzeuge/17417/mercedes-benz/vito_bus_w639_/111_cdi_639_701_639_703_639_705_17417?utm_source=chatgpt.com "111 CDI (639.701, 639.703, 639.705) | Vito Bus (W639) | Mercedes-Benz | Herstellerübersicht | Meyer Motoren"
[2]: https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france?utm_source=chatgpt.com "FOUR.VITO 109/111/115 CDI-03-06 (Page 1) - Mercedes-Benz France"
[3]: https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77840/?utm_source=chatgpt.com "Mercedes-Benz Vito 113 CDI 4x4 AT L1H1 (03.2010 - 10.2014) - технические характеристики"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Vito W447 柴油 Kasten、Mixto 与 Tourer 车型簇，共新增 21 个输入 Ktype、63 条 READY 映射。
* Kasten 使用 `447.601 / 447.603 / 447.605`，Mixto 与 Tourer 使用 `447.701 / 447.703 / 447.705`，依次对应 Compact、Long、Extra Long。([AUTODOC][1])
* 三种基础外廓统一闭合为 `4895 / 5140 / 5370 × 1928 × 1910 mm`。官方尺寸图同时给出了含镜宽度和 `1928 mm` 车身宽度，可确认本轮 WidthMM 为不含后视镜口径。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：57
* READY 映射：141
* PENDING 输入 Ktype：43
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
107503_compact	107503	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107503_long	107503	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107503_extralong	107503	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
145732_compact	145732	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
145732_long	145732	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
145732_extralong	145732	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
107505_compact	107505	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107505_long	107505	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107505_extralong	107505	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
107506_compact	107506	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107506_long	107506	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107506_extralong	107506	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116117_compact	116117	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116117_long	116117	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116117_extralong	116117	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
107508_compact	107508	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107508_long	107508	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107508_extralong	107508	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116118_compact	116118	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116118_long	116118	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116118_extralong	116118	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
107510_compact	107510	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107510_long	107510	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107510_extralong	107510	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116119_compact	116119	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116119_long	116119	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116119_extralong	116119	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
107511_compact	107511	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
107511_long	107511	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
107511_extralong	107511	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
145733_compact	145733	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
145733_long	145733	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
145733_extralong	145733	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
107512_compact	107512	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
107512_long	107512	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
107512_extralong	107512	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
107513_compact	107513	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
107513_long	107513	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
107513_extralong	107513	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
116120_compact	116120	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
116120_long	116120	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
116120_extralong	116120	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
107514_compact	107514	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
107514_long	107514	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
107514_extralong	107514	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
116121_compact	116121	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
116121_long	116121	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
116121_extralong	116121	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
107515_compact	107515	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
107515_long	107515	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
107515_extralong	107515	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
109296_compact	109296	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
109296_long	109296	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
109296_extralong	109296	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
143284_compact	143284	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Mixto Compact物理分支。	READY
143284_long	143284	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
143284_extralong	143284	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
143285_compact	143285	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
143285_long	143285	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
143285_extralong	143285	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
107516_compact	107516	MPV	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Tourer Compact物理分支。	READY
107516_long	107516	MPV	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Tourer Long物理分支。	READY
107516_extralong	107516	MPV	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Tourer Extra Long物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure, December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	5140	1928	1910	Mercedes-Benz Vito Panel and Crew Van official brochure, July 2023	https://bluesky-cogcms.cdn.imgeng.in/media/zbsgqv1o/64464-007-mb-vito-panel-van-and-crew-van-july-2023-aw-v3-final-270623.pdf
EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	5370	1928	1910	Mercedes-Benz Vito Panel and Crew Van official brochure, July 2023	https://bluesky-cogcms.cdn.imgeng.in/media/zbsgqv1o/64464-007-mb-vito-panel-van-and-crew-van-july-2023-aw-v3-final-270623.pdf
```

## 下一步优先处理

1. 闭合 `801624` eVito Kasten 的 Long、Extra Long 分支。
2. 闭合 `158825` Vito Mixto 124 与 `158821` Vito Tourer 124 的2024年改款分支。
3. 随后集中处理剩余40个 Vario Ktype 的底盘、Kasten、4X4、Triebkopf及Bus多轴距外廓。

推进信号：CONTINUE

[1]: https://www.auto-doc.ie/car-parts/sensor-exterior-temperature-10894/mercedes-benz/vito/vito-box-w447/107503-109-cdi-447-601-447-603-447-605?srsltid=AfmBOoqLbCD9hBic8_ktOhbASp2Pxf2rZIKdmTzA8rrcS6c8qgodcOL7&utm_source=chatgpt.com "Mercedes Vito W447 109 CDI 1.6 Sensor, exterior ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 3 个 Vito W447 特殊动力 Ktype，共新增 6 条 READY 映射。
* `158821` 与 `158825` 均仅覆盖 `447.703`、`447.705`，分别对应 Long、Extra Long；`801624` 仅覆盖 Kasten 的 `447.603`、`447.605`。([Electronicx][1])
* 三者均关联既有 W447 标准 Long、Extra Long 尺寸组，不因轻混或电动动力形式重复建组。Mercedes-Benz 官方 eVito 资料确认其仍采用 5140 mm、5370 mm 两种车长；既有组的 1928 mm 不含镜宽度及 1910 mm 高度继续有效。([Mercedes-Benz][2])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：60
* READY 映射：147
* PENDING 输入 Ktype：40
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
801624_long	801624	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	eVito Long物理分支。	READY
801624_extralong	801624	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	eVito Extra Long物理分支。	READY
158825_long	158825	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
158825_extralong	158825	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
158821_long	158821	MPV	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Tourer Long物理分支。	READY
158821_extralong	158821	MPV	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Tourer Extra Long物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 按 Vario 底盘轴距和驾驶室外廓，集中闭合 Pritsche/Fahrgestell。
2. 处理 Vario Kasten 的轴距及车顶高度分支。
3. 处理 4X4、Kipper、Triebkopf 与 Bus 特殊外廓。
4. Vario 全部闭合后立即执行一次机械收尾，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://electronicx.de/4x-RDKS-Sensoren-Gummi-Mercedes-Sprinter-907-910-012018-122021-TPMS-Reifendruck?srsltid=AfmBOorH4ehkvYGQk-bwRlThBEJjZ-guC2hPtX_9MjW7gXxp1s1YwhQx&utm_source=chatgpt.com "4x RDKS Sensoren Gummi ▶ Mercedes Sprinter 907/910 ..."
[2]: https://www.mercedes-benz.co.uk/vans/models/evito/panel-van/overview.html "eVito Electric Panel Van | Medium Van | Mercedes-Benz Vans UK"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Vario W670 后驱 Kasten 车型簇：`34211`、`34391`、`34214`、`34394`、`34337`。
* `670.351 / 670.352 / 670.353` 分别对应 3150、3700、4250 mm 轴距；按标准顶/高顶拆为 L1H1、L1H2、L2H1、L2H2、L3H2 五种物理外廓。五个 Ktype 均覆盖相同车身代码组合，因此统一复用五个尺寸组。([梅赛德斯-奔驰 Vario][1])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：65
* READY 映射：172
* PENDING 输入 Ktype：35
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34211_l1h1	34211	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34211_l1h2	34211	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34211_l2h1	34211	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34211_l2h2	34211	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34211_l3h2	34211	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34391_l1h1	34391	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34391_l1h2	34391	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34391_l2h1	34391	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34391_l2h2	34391	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34391_l3h2	34391	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34214_l1h1	34214	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34214_l1h2	34214	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34214_l2h1	34214	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34214_l2h2	34214	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34214_l3h2	34214	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34394_l1h1	34394	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34394_l1h2	34394	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34394_l2h1	34394	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34394_l2h2	34394	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34394_l3h2	34394	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34337_l1h1	34337	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34337_l1h2	34337	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34337_l2h1	34337	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34337_l2h2	34337	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34337_l3h2	34337	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	5450	2206	2710	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	5450	2206	2865	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	6330	2206	2775	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	6330	2206	2930	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	7210	2206	2935	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
```

## 下一步优先处理

1. 闭合 Vario 4X4 Kasten 的 `670.451 / 670.452 / 670.453` 轴距、车顶与宽度分支。
2. 批量处理后驱及四驱 Pritsche/Fahrgestell 的标准驾驶室、双排驾驶室和轴距组合。
3. 最后处理 Triebkopf、Kipper 与 `670.373 / 670.374` Bus 分支。

推进信号：CONTINUE

[1]: https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf "Aufbaurichtlinien Vario - Stand 08.09.2009"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合 Vario W670 四驱 Kasten 车型簇：`34217`、`34397`、`34220`、`34400`。
* `670.451 / 670.452 / 670.453` 分别对应 3150、3700、4250 mm 轴距；Mercedes-Benz 官方尺寸图注明 Kasten 的车辆外廓数据同样适用于四驱版本，因此直接复用既有五个尺寸组，不重复建组。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：69
* READY 映射：192
* PENDING 输入 Ktype：31
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34217_l1h1	34217	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34217_l1h2	34217	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34217_l2h1	34217	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34217_l2h2	34217	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34217_l3h2	34217	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34397_l1h1	34397	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34397_l1h2	34397	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34397_l2h1	34397	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34397_l2h2	34397	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34397_l3h2	34397	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34220_l1h1	34220	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34220_l1h2	34220	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34220_l2h1	34220	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34220_l2h2	34220	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34220_l3h2	34220	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34400_l1h1	34400	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34400_l1h2	34400	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34400_l2h1	34400	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34400_l2h2	34400	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34400_l3h2	34400	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量闭合 `670.421 / 670.422 / 670.423` 四驱 Fahrgestell 标准驾驶室分支。
2. 处理 `670.431 / 670.432` 四驱 Kipper 分支。
3. 随后闭合后驱 Pritsche/Fahrgestell、Triebkopf 和 Bus。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 Vario W670 四驱 Kipper 车型簇中的 `34218`、`34398`、`34221`、`34401`。
* `670.431` 对应 3150 mm 轴距标准驾驶室；`670.432` 对应 3700 mm 轴距，并存在标准驾驶室和双排驾驶室两种不同外廓。([PartSouq][1])
* 官方尺寸图确认 Kipper 的车辆尺寸同样适用于四驱版本；本轮新增短轴标准驾驶室、中轴标准驾驶室和中轴双排驾驶室三个尺寸组。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：73
* READY 映射：204
* PENDING 输入 Ktype：27
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34218_l1_std	34218	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34218_l2_std	34218	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34218_l2_crew	34218	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34398_l1_std	34398	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34398_l2_std	34398	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34398_l2_crew	34398	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34221_l1_std	34221	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34221_l2_std	34221	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34221_l2_crew	34221	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34401_l1_std	34401	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34401_l2_std	34401	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34401_l2_crew	34401	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	5330	2206	2395	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	6230	2240	2505	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	6250	2240	2515	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK
```

## 下一步优先处理

1. 闭合 `34216`、`34396`、`34219`、`34399`、`34334` 的 `670.421 / 670.422 / 670.423` 四驱 Fahrgestell 分支。
2. 补齐 `34336` 818 DA 4X4 Kipper 的明确车身代码边界后复用本轮尺寸组。
3. 随后批量处理后驱 Pritsche/Fahrgestell、Triebkopf 和 Bus。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=2&cname=M++-+Engine&q=&srsltid=AfmBOoqAXPyGigUDzq9x3ViuRx4oHFH_xzJExygetLdJkXBJ8uI8D7zk&ssd=%24%2AKwGCtqexwvTzwPvI_9-TttrO7un3homEhZe4i8PF9vj1_MjrmZSN8PCAgYeFhITc1sOFz9X3y5PCltPFo-iTmpXdk4zanIuXnJPRlYrfw9iFmoXG1N73y5PAltOJjtzdmpXd0pSOy9HMgIWFhpKdlMeKxcGSk5qV3dqUjsvWqJKdlNTek4yW2dG-kp2UwdOTjJbaxYYAAAAAU6hkvQ%3D%3D%24&vid=0&utm_source=chatgpt.com "Mercedes-Benz VARIO 814DA Standard, Japan 670.431 Parts ..."


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 Vario W670 四驱 Fahrgestell 车型簇：`34216`、`34396`、`34219`、`34399`、`34334`。
* `670.421 / 670.422 / 670.423` 分别对应 3150、3700、4250 mm 轴距；每个轴距均按标准驾驶室与双排驾驶室拆分。Mercedes-Benz 官方尺寸图同时确认车辆高度数据适用于四驱版本。([PartSouq][1])
* 已将 `34336` 818 DA 4X4 Kipper 关联到现有短轴标准驾驶室、中轴标准驾驶室和中轴双排驾驶室尺寸组，未重复建组。其车型属于与既有 Kipper 相同的 4×4 外廓体系。([Allopneus][2])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：79
* READY 映射：237
* PENDING 输入 Ktype：21
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34216_l1_std	34216	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34216_l1_crew	34216	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34216_l2_std	34216	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34216_l2_crew	34216	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34216_l3_std	34216	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34216_l3_crew	34216	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34396_l1_std	34396	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34396_l1_crew	34396	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34396_l2_std	34396	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34396_l2_crew	34396	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34396_l3_std	34396	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34396_l3_crew	34396	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34219_l1_std	34219	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34219_l1_crew	34219	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34219_l2_std	34219	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34219_l2_crew	34219	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34219_l3_std	34219	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34219_l3_crew	34219	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34399_l1_std	34399	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34399_l1_crew	34399	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34399_l2_std	34399	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34399_l2_crew	34399	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34399_l3_std	34399	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34399_l3_crew	34399	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34334_l1_std	34334	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34334_l1_crew	34334	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34334_l2_std	34334	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34334_l2_crew	34334	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34334_l3_std	34334	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34334_l3_crew	34334	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34336_l1_std	34336	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34336_l2_std	34336	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34336_l2_crew	34336	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	5175	2206	2400	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	5175	2206	2405	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	6055	2240	2500	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	6055	2240	2505	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	6935	2240	2465	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	6935	2240	2470	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
```

## 下一步优先处理

1. 批量闭合后驱 `670.321 / 670.322 / 670.323 / 670.324` Pritsche/Fahrgestell 分支。
2. 处理 `34209`、`34210`、`34212`、`34390`、`34392`、`34213`、`34215`、`34393`、`34395`、`34333`、`34335`。
3. 最后闭合 Triebkopf 与 `670.373 / 670.374` Bus 分支。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0001550176&srsltid=AfmBOor_F0o4_Z6UR1JfG8wBFUmN0qPp3OjuNapp-YaN2P--_C3gCjJk&ssd=%24%2AKwHg1MXKuLacgpG5k_u9sbisjIuV5Ovm5_Xa6aGnlJqXnqqJ-_bvkpLk5eLi4eO7tK7kraKwupOv9P2no7ymuLn-8bm1qb-75OTk4eDi9vqp9vrw6fb3_vG5vam_u-OA9vnwsLr0saep5Jb2-fClt_Sxp6rwrgAAAAClUdN9%24&utm_source=chatgpt.com "Mercedes-Benz VARIO 814DA / 815DA Standard, Japan ..."
[2]: https://www.allopneus.com/vehicule/mercedes-benz/vario/vario-camion-basculant?utm_source=chatgpt.com "Pneu MERCEDES-BENZ VARIO Camion basculant : Pression et dimensions des pneus - Allopneus.com"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已闭合剩余后驱 Fahrgestell 与 Kipper 车型簇，共新增 **11 个输入 Ktype、58 条 READY 映射**。
* 已按精确车型代码区分：

  * Fahrgestell：`670.321 / 670.322 / 670.323 / 670.324`
  * Kipper：`670.331 / 670.332`
  * `34335` 为特殊的 818 D Kipper，覆盖 `670.321 / 670.322`。([Meyer Motoren][1])
* 后驱底盘按四种轴距及标准/双排驾驶室拆分；Kipper 按短轴标准驾驶室、中轴标准驾驶室和中轴双排驾驶室拆分。外廓依据 Mercedes-Benz 官方尺寸图及官方规格表闭合。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：90
* READY 映射：295
* PENDING 输入 Ktype：10
* 已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34209_l1_std	34209	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34209_l2_std	34209	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34209_l2_crew	34209	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34210_l1_std	34210	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34210_l1_crew	34210	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34210_l2_std	34210	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34210_l2_crew	34210	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34210_l3_std	34210	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34210_l3_crew	34210	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34210_l4_std	34210	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室底盘分支。	READY
34210_l4_crew	34210	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室底盘分支。	READY
34212_l1_std	34212	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34212_l2_std	34212	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34212_l2_crew	34212	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34390_l1_std	34390	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34390_l1_crew	34390	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34390_l2_std	34390	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34390_l2_crew	34390	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34390_l3_std	34390	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34390_l3_crew	34390	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34390_l4_std	34390	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室底盘分支。	READY
34390_l4_crew	34390	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室底盘分支。	READY
34392_l1_std	34392	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34392_l2_std	34392	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34392_l2_crew	34392	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34213_l1_std	34213	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34213_l1_crew	34213	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34213_l2_std	34213	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34213_l2_crew	34213	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34213_l3_std	34213	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34213_l3_crew	34213	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34213_l4_std	34213	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室底盘分支。	READY
34213_l4_crew	34213	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室底盘分支。	READY
34215_l1_std	34215	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34215_l2_std	34215	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34215_l2_crew	34215	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34393_l1_std	34393	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34393_l1_crew	34393	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34393_l2_std	34393	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34393_l2_crew	34393	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34393_l3_std	34393	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34393_l3_crew	34393	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34393_l4_std	34393	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室底盘分支。	READY
34393_l4_crew	34393	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室底盘分支。	READY
34395_l1_std	34395	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34395_l2_std	34395	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34395_l2_crew	34395	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34333_l1_std	34333	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34333_l1_crew	34333	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34333_l2_std	34333	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34333_l2_crew	34333	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34333_l3_std	34333	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34333_l3_crew	34333	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34333_l4_std	34333	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室底盘分支。	READY
34333_l4_crew	34333	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室底盘分支。	READY
34335_l1_std	34335	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34335_l2_std	34335	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34335_l2_crew	34335	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	5175	2206	2400	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	5175	2206	2405	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	6055	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	6055	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	6935	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	6935	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	7485	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	7485	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	5330	2320	2395	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	6230	2320	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	6250	2320	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
```

## 下一步优先处理

1. 闭合 `100252`、`34227`、`34228` 三个 `670.398` Triebkopf 分支。
2. 闭合 `34222`、`34223`、`100307`、`34224`、`34225`、`100308`、`100309` 的 `670.373 / 670.374 / 670.674` Bus 分支。
3. 剩余 10 个 Ktype 全部闭合后，下一条回复直接执行机械收尾并输出两张完整 TSV、指定下载链接及 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/fahrzeuge/34213/mercedes-benz/vario_fahrgestell_b670_b668_b667_/815_d_816_d_670_321_670_322_670_323_670_324_?utm_source=chatgpt.com "815 D, 816 D (670.321, 670.322, 670.323, 670.324) | Vario Fahrgestell (B670, B668, B667) | Mercedes-Benz | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已闭合 Vario W670 的 7 个 Bus Ktype，并按 `670.373` 短轴与 `670.374 / 670.674` 长轴拆分，共新增 14 条 READY 映射。
* 短轴 Bus 外廓为 `6215 × 2205 × 2830 mm`，长轴 Bus 外廓为 `7210 × 2205 × 2820 mm`；官方规格表明确标注宽度为不含后视镜口径。
* 剩余 `100252`、`34227`、`34228` 均为 `670.398` Triebkopf。现有资料能确认车身代码和动力版本，但尚缺同一完整配置下可直接落盘的外部长度、宽度和高度，因此本轮不创建猜测性尺寸组。([梅尔摩托车][1])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：97
* READY 映射：309
* PENDING 输入 Ktype：3
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34222_l1	34222	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34222_l2	34222	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34223_l1	34223	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34223_l2	34223	MPV	Vario W670	670.674		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100307_l1	100307	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100307_l2	100307	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34224_l1	34224	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34224_l2	34224	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34225_l1	34225	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34225_l2	34225	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100308_l1	100308	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100308_l2	100308	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100309_l1	100309	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100309_l2	100309	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	6215	2205	2830	Mercedes-Benz The Vario official specification sheet 2004 - passenger carrying conversion	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	7210	2205	2820	Mercedes-Benz The Vario official specification sheet 2004 - passenger carrying conversion	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
```

## 下一步优先处理

1. 仅补查 `670.398` Triebkopf/cab-with-engine 的完整外部三维，重点确认整体长度与标准状态高度。
2. 三个 Triebkopf Ktype 共用同一物理外廓；首次闭合后一次性映射 `100252`、`34227`、`34228`，不按发动机功率重复建组。
3. 若获得完整同配置三维，下一条回复直接执行机械收尾并输出两张最终完整 TSV、指定下载链接及 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/34228/mercedes-benz/vario_triebkopf/816_dt_670_398_34228?utm_source=chatgpt.com "Mercedes-Benz Vario Triebkopf 816 DT (670.398)"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已完成 `670.398` Triebkopf 的定向核查，但本轮未形成可落盘的新尺寸组。
* Mercedes-Benz 原厂旧版 Vario brochure 明确列出 Triebkopf 为特殊出厂形式，但其技术尺寸页只提供 Kastenwagen、Pritschenwagen、Kipper 和 Fahrgestell，没有给出 Triebkopf 的完整长宽高。
* 零件目录确认 `670.398` 是独立的 **VARIOCHASSIS FRONT END WITH CAB**，不能直接套用完整 Fahrgestell 的总长；现有资料仍不足以确认同一标准交付状态下的完整三维，因此未猜测建组。([PartSouq][1])

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：97
* READY 映射：309
* PENDING 输入 Ktype：3
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅查找 Mercedes-Benz `670.398` 原厂 Angebotszeichnung、type approval 或出厂运输尺寸资料。
2. 必须取得 Triebkopf 标准交付状态的完整外部长度、不含后视镜宽度和高度后，才创建唯一尺寸组。
3. 尺寸组闭合后一次性关联 `100252`、`34227`、`34228`；随后立即输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=&q=&srsltid=AfmBOoq3FsVWck-lB3JQJw5FdyDJ6hfXSquHHI7ryQJRj9oa-itbXcPQ&ssd=%24%2AKwGrn47jrt_A-ump2vWPqfPnx8Der6CtrL6Rours39Hc1eHCsL2k2dmvrqigra31_uCo5un78djkv7bs6Pft8_K1uvL-4vTwr6-vraCgvbHivbG7or28tbry9uL08KjLvbK7-_G_-uzir929srvu_L_67OG75QAAAAB32tBA%24&vid=0&utm_source=chatgpt.com "Mercedes-Benz VARIO 810 DT Standard, Japan 670.398 Parts ..."


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已确认 `100252`、`34227`、`34228` 均对应 `670.398`，其原厂形态属于未完成式 **Vario Chassis Cowl / Triebkopf**。官方规格表仅给出轴距、整体长度和 `2206 mm` 不含后视镜宽度，没有定义整车外部高度；尺寸图也显示车身上部需由后续改装厂完成。现阶段不能以普通 Fahrerhaus 的高度代填。([PartSouq][1])
* 三个 Ktype 已正式补入映射表并保持 PENDING；未创建缺少 HeightMM 的尺寸组。

## 当前批次进度

* 输入 Ktype 总数：100
* 已闭合输入 Ktype：97
* READY 映射：309
* PENDING 映射：3
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100252	100252	Chassis Cowl	Vario W670	670.398			HIGH	未完成式Triebkopf；原厂完整外部高度未定义。	PENDING: 670.398原厂资料缺少可落盘的完整外部高度
34227	34227	Chassis Cowl	Vario W670	670.398			HIGH	未完成式Triebkopf；原厂完整外部高度未定义。	PENDING: 670.398原厂资料缺少可落盘的完整外部高度
34228	34228	Chassis Cowl	Vario W670	670.398			HIGH	未完成式Triebkopf；原厂完整外部高度未定义。	PENDING: 670.398原厂资料缺少可落盘的完整外部高度
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 定向查找 `670.398` 出厂 Angebotszeichnung、EG type approval 或运输状态尺寸图，确认未完成式 Triebkopf 的最高外部点。
2. 若官方定义多个轴距交付分支，同时闭合各分支长度、宽度和高度；不得用普通驾驶室或完成后客车的高度拼接。
3. 三个映射全部转为 READY 后，立即输出最终两张完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://partsouq.com/shop/product/A6706302410-mercedes-pillar/19173815?utm_source=chatgpt.com "PILLAR A6706302410 | MERCEDES Parts | PartSouq"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* Mercedes-Benz 原厂 Vario Chassis Cowl 规格表确认该类未完成式车辆提供 `6055 / 6935 / 7485 mm` 总长和 `2206 mm` 车身宽度，但尺寸表没有定义整体高度；结构图显示驾驶室后部及车顶由后续车身制造商完成，仍无法组成符合规则的完整三维尺寸组。([Scribd][1])
* 本轮未修改既有 PENDING 映射，也未使用普通驾驶室、Bus 或改装后车身高度代填。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：97
* READY 映射：309
* PENDING 映射：3
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 继续定向查找 `670.398` 的原厂 Angebotszeichnung、EG 型式批准或运输状态尺寸文件。
2. 重点确认 Triebkopf 标准交付状态的最高外部点，以及 `670.398` 是否存在多个可独立落盘的长度分支。
3. 完整三维闭合后，一次性更新 `100252`、`34227`、`34228`，随后直接进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK "Vario Specifications for Mercedes-Benz Vans | PDF | Truck | Vehicles"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10801-10900_ktype_dimension_mapping_final.tsv
- left18448_10801-10900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 最后 3 个 `670.398` Triebkopf 已闭合。EPC 将其定义为带完整驾驶室的前端总成；原厂尺寸图对应 `2040 × 2206 × 2405 mm`，宽度为不含后视镜口径。([猫车][1])
* 已完成机械检查：表头固定、312 个 `id` 唯一、50 个尺寸组唯一、全部映射引用闭合、无孤立尺寸组、三维及来源完整。
* 已生成两个指定文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：312
* PENDING 映射：0
* DIMENSION_GROUP：50
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34209_l1_std	34209	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34209_l2_std	34209	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34209_l2_crew	34209	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
100252	100252	Chassis Cab	Vario W670	670.398	2	EU-MERCEDES-BENZ-VARIO-W670-TRIEBKOPF-01	HIGH	完整驾驶室前端总成。	READY
34210_l1_std	34210	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34210_l1_crew	34210	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室分支。	READY
34210_l2_std	34210	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34210_l2_crew	34210	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34210_l3_std	34210	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室分支。	READY
34210_l3_crew	34210	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室分支。	READY
34210_l4_std	34210	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室分支。	READY
34210_l4_crew	34210	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室分支。	READY
34211_l1h1	34211	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34211_l1h2	34211	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34211_l2h1	34211	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34211_l2h2	34211	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34211_l3h2	34211	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34212_l1_std	34212	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34212_l2_std	34212	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34212_l2_crew	34212	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34390_l1_std	34390	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34390_l1_crew	34390	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室分支。	READY
34390_l2_std	34390	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34390_l2_crew	34390	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34390_l3_std	34390	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室分支。	READY
34390_l3_crew	34390	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室分支。	READY
34390_l4_std	34390	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室分支。	READY
34390_l4_crew	34390	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室分支。	READY
34391_l1h1	34391	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34391_l1h2	34391	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34391_l2h1	34391	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34391_l2h2	34391	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34391_l3h2	34391	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34392_l1_std	34392	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34392_l2_std	34392	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34392_l2_crew	34392	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34216_l1_std	34216	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34216_l1_crew	34216	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34216_l2_std	34216	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34216_l2_crew	34216	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34216_l3_std	34216	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34216_l3_crew	34216	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34217_l1h1	34217	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34217_l1h2	34217	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34217_l2h1	34217	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34217_l2h2	34217	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34217_l3h2	34217	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34218_l1_std	34218	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34218_l2_std	34218	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34218_l2_crew	34218	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34396_l1_std	34396	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34396_l1_crew	34396	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34396_l2_std	34396	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34396_l2_crew	34396	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34396_l3_std	34396	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34396_l3_crew	34396	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34397_l1h1	34397	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34397_l1h2	34397	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34397_l2h1	34397	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34397_l2h2	34397	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34397_l3h2	34397	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34398_l1_std	34398	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34398_l2_std	34398	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34398_l2_crew	34398	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34227	34227	Chassis Cab	Vario W670	670.398	2	EU-MERCEDES-BENZ-VARIO-W670-TRIEBKOPF-01	HIGH	完整驾驶室前端总成。	READY
34213_l1_std	34213	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34213_l1_crew	34213	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室分支。	READY
34213_l2_std	34213	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34213_l2_crew	34213	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34213_l3_std	34213	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室分支。	READY
34213_l3_crew	34213	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室分支。	READY
34213_l4_std	34213	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室分支。	READY
34213_l4_crew	34213	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室分支。	READY
34214_l1h1	34214	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34214_l1h2	34214	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34214_l2h1	34214	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34214_l2h2	34214	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34214_l3h2	34214	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34215_l1_std	34215	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34215_l2_std	34215	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34215_l2_crew	34215	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34393_l1_std	34393	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34393_l1_crew	34393	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室分支。	READY
34393_l2_std	34393	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34393_l2_crew	34393	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34393_l3_std	34393	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室分支。	READY
34393_l3_crew	34393	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室分支。	READY
34393_l4_std	34393	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室分支。	READY
34393_l4_crew	34393	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室分支。	READY
34394_l1h1	34394	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34394_l1h2	34394	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34394_l2h1	34394	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34394_l2h2	34394	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34394_l3h2	34394	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34395_l1_std	34395	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34395_l2_std	34395	Pickup	Vario W670	670.331	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34395_l2_crew	34395	Pickup	Vario W670	670.332	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34219_l1_std	34219	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34219_l1_crew	34219	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34219_l2_std	34219	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34219_l2_crew	34219	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34219_l3_std	34219	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34219_l3_crew	34219	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34220_l1h1	34220	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34220_l1h2	34220	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34220_l2h1	34220	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34220_l2h2	34220	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34220_l3h2	34220	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34221_l1_std	34221	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34221_l2_std	34221	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34221_l2_crew	34221	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34399_l1_std	34399	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34399_l1_crew	34399	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34399_l2_std	34399	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34399_l2_crew	34399	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34399_l3_std	34399	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34399_l3_crew	34399	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34400_l1h1	34400	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	4X4短轴标准顶物理分支。	READY
34400_l1h2	34400	Van	Vario W670	670.451		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	4X4短轴高顶物理分支。	READY
34400_l2h1	34400	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	4X4中轴标准顶物理分支。	READY
34400_l2h2	34400	Van	Vario W670	670.452		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	4X4中轴高顶物理分支。	READY
34400_l3h2	34400	Van	Vario W670	670.453		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	4X4长轴高顶物理分支。	READY
34401_l1_std	34401	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34401_l2_std	34401	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34401_l2_crew	34401	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34228	34228	Chassis Cab	Vario W670	670.398	2	EU-MERCEDES-BENZ-VARIO-W670-TRIEBKOPF-01	HIGH	完整驾驶室前端总成。	READY
34333_l1_std	34333	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34333_l1_crew	34333	Pickup	Vario W670	670.321	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	HIGH	短轴双排驾驶室分支。	READY
34333_l2_std	34333	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34333_l2_crew	34333	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34333_l3_std	34333	Pickup	Vario W670	670.323	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	HIGH	长轴标准驾驶室分支。	READY
34333_l3_crew	34333	Pickup	Vario W670	670.323	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	HIGH	长轴双排驾驶室分支。	READY
34333_l4_std	34333	Pickup	Vario W670	670.324	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	HIGH	超长轴标准驾驶室分支。	READY
34333_l4_crew	34333	Pickup	Vario W670	670.324	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	HIGH	超长轴双排驾驶室分支。	READY
34335_l1_std	34335	Pickup	Vario W670	670.321	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	HIGH	短轴标准驾驶室分支。	READY
34335_l2_std	34335	Pickup	Vario W670	670.322	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	HIGH	中轴标准驾驶室分支。	READY
34335_l2_crew	34335	Pickup	Vario W670	670.322	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	HIGH	中轴双排驾驶室分支。	READY
34337_l1h1	34337	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	HIGH	短轴标准顶物理分支。	READY
34337_l1h2	34337	Van	Vario W670	670.351		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	HIGH	短轴高顶物理分支。	READY
34337_l2h1	34337	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	HIGH	中轴标准顶物理分支。	READY
34337_l2h2	34337	Van	Vario W670	670.352		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	HIGH	中轴高顶物理分支。	READY
34337_l3h2	34337	Van	Vario W670	670.353		EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	HIGH	长轴高顶物理分支。	READY
34334_l1_std	34334	Pickup	Vario W670	670.421	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室底盘分支。	READY
34334_l1_crew	34334	Pickup	Vario W670	670.421	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	HIGH	短轴双排驾驶室底盘分支。	READY
34334_l2_std	34334	Pickup	Vario W670	670.422	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室底盘分支。	READY
34334_l2_crew	34334	Pickup	Vario W670	670.422	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室底盘分支。	READY
34334_l3_std	34334	Pickup	Vario W670	670.423	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	HIGH	长轴标准驾驶室底盘分支。	READY
34334_l3_crew	34334	Pickup	Vario W670	670.423	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	HIGH	长轴双排驾驶室底盘分支。	READY
34336_l1_std	34336	Pickup	Vario W670	670.431	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	HIGH	短轴标准驾驶室Kipper分支。	READY
34336_l2_std	34336	Pickup	Vario W670	670.432	2	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	HIGH	中轴标准驾驶室Kipper分支。	READY
34336_l2_crew	34336	Pickup	Vario W670	670.432	4	EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	HIGH	中轴双排驾驶室Kipper分支。	READY
34222_l1	34222	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34222_l2	34222	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34223_l1	34223	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34223_l2	34223	MPV	Vario W670	670.674		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100307_l1	100307	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100307_l2	100307	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34224_l1	34224	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34224_l2	34224	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
34225_l1	34225	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
34225_l2	34225	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100308_l1	100308	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100308_l2	100308	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
100309_l1	100309	MPV	Vario W670	670.373		EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	HIGH	短轴乘用客车物理分支。	READY
100309_l2	100309	MPV	Vario W670	670.374		EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	HIGH	长轴乘用客车物理分支。	READY
17408_compact	17408	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17408_long	17408	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
17409_long	17409	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
17409_extralong	17409	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18721	18721	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
56150_compact	56150	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56150_long	56150	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
56150_extralong	56150	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17410_compact	17410	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17410_long	17410	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
17410_extralong	17410	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17411_compact	17411	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17411_long	17411	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	HIGH	Long物理分支。	READY
17411_extralong	17411	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
145126_compact	145126	MPV	Viano W639	639.711	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-FACELIFT-01	HIGH	改款后Compact物理分支。	READY
145126_long	145126	MPV	Viano W639	639.713	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-FACELIFT-01	HIGH	改款后Long物理分支。	READY
56751_compact	56751	MPV	Viano W639	639.811	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-4MATIC-PREFL-01	HIGH	4MATIC Compact物理分支。	READY
56751_long	56751	MPV	Viano W639	639.813	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-4MATIC-PREFL-01	HIGH	4MATIC Long物理分支。	READY
56751_extralong	56751	MPV	Viano W639	639.815	4	EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-4MATIC-PREFL-01	HIGH	4MATIC Extra Long物理分支。	READY
17416_compact	17416	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17416_long	17416	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17416_extralong	17416	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17419_compact	17419	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17419_long	17419	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17419_extralong	17419	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18720	18720	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	仅覆盖Compact物理分支。	READY
56151_compact	56151	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56151_long	56151	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
56151_extralong	56151	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
11419	11419	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Bus。	READY
14005	14005	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11097	11097	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
18102_compact	18102	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
18102_long	18102	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
18102_extralong	18102	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
107503_compact	107503	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107503_long	107503	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107503_extralong	107503	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
145732_compact	145732	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
145732_long	145732	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
145732_extralong	145732	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
11420	11420	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Bus。	READY
14006	14006	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11098	11098	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
17417_compact	17417	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17417_long	17417	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17417_extralong	17417	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
107505_compact	107505	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107505_long	107505	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107505_extralong	107505	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
11421	11421	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Bus。	READY
14007	14007	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
11099	11099	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
7842	7842	MPV	Vito W638		4	EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Bus。	READY
11100	11100	Van	Vito W638			EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	MEDIUM	W638标准车身Kasten。	READY
107506_compact	107506	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107506_long	107506	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107506_extralong	107506	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116117_compact	116117	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116117_long	116117	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116117_extralong	116117	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
17418_compact	17418	MPV	Vito W639	639.701	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17418_long	17418	MPV	Vito W639	639.703	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17418_extralong	17418	MPV	Vito W639	639.705	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
107508_compact	107508	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107508_long	107508	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107508_extralong	107508	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116118_compact	116118	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116118_long	116118	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116118_extralong	116118	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
107510_compact	107510	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107510_long	107510	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107510_extralong	107510	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116119_compact	116119	Van	Vito W447	447.601		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Compact物理分支。	READY
116119_long	116119	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Long物理分支。	READY
116119_extralong	116119	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Extra Long物理分支。	READY
59487	59487	MPV	Vito W639		4	EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	HIGH	E-CELL Long物理外廓。	READY
801624_long	801624	Van	Vito W447	447.603		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	eVito Long物理分支。	READY
801624_extralong	801624	Van	Vito W447	447.605		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	eVito Extra Long物理分支。	READY
17414_compact	17414	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17414_long	17414	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17414_extralong	17414	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17415_compact	17415	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17415_long	17415	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17415_extralong	17415	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
56153_compact	56153	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
56153_long	56153	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
56153_extralong	56153	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
18101_compact	18101	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
18101_long	18101	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
18101_extralong	18101	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
17413_compact	17413	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact物理分支。	READY
17413_long	17413	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long物理分支。	READY
17413_extralong	17413	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long物理分支。	READY
59426_compact	59426	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	HIGH	4X4 Compact物理分支。	READY
59426_long	59426	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	HIGH	4X4 Long物理分支。	READY
59426_extralong	59426	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	HIGH	4X4 Extra Long物理分支。	READY
17412_compact_prefl	17412	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	HIGH	Compact改款前物理分支。	READY
17412_long_prefl	17412	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	HIGH	Long改款前物理分支。	READY
17412_extralong_prefl	17412	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	HIGH	Extra Long改款前物理分支。	READY
17412_compact_facelift	17412	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-FACELIFT-01	HIGH	Compact改款后物理分支。	READY
17412_long_facelift	17412	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-FACELIFT-01	HIGH	Long改款后物理分支。	READY
17412_extralong_facelift	17412	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-FACELIFT-01	HIGH	Extra Long改款后物理分支。	READY
59428_compact	59428	Van	Vito W639	639.601	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	HIGH	4X4 Compact物理分支。	READY
59428_long	59428	Van	Vito W639	639.603	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	HIGH	4X4 Long物理分支。	READY
59428_extralong	59428	Van	Vito W639	639.605	4	EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	HIGH	4X4 Extra Long物理分支。	READY
59486	59486	Van	Vito W639		4	EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	HIGH	E-CELL Long物理外廓。	READY
158825_long	158825	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Mixto Long物理分支。	READY
158825_extralong	158825	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Mixto Extra Long物理分支。	READY
107511_compact	107511	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107511_long	107511	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107511_extralong	107511	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
145733_compact	145733	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
145733_long	145733	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
145733_extralong	145733	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
107512_compact	107512	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107512_long	107512	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107512_extralong	107512	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
107513_compact	107513	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107513_long	107513	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107513_extralong	107513	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116120_compact	116120	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
116120_long	116120	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
116120_extralong	116120	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
107514_compact	107514	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107514_long	107514	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107514_extralong	107514	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
116121_compact	116121	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
116121_long	116121	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
116121_extralong	116121	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
107515_compact	107515	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107515_long	107515	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107515_extralong	107515	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
109296_compact	109296	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
109296_long	109296	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
109296_extralong	109296	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
143284_compact	143284	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
143284_long	143284	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
143284_extralong	143284	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
143285_compact	143285	Van	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	4MATIC Mixto Compact物理分支。	READY
143285_long	143285	Van	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	4MATIC Mixto Long物理分支。	READY
143285_extralong	143285	Van	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	4MATIC Mixto Extra Long物理分支。	READY
158821_long	158821	MPV	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Tourer Long物理分支。	READY
158821_extralong	158821	MPV	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Tourer Extra Long物理分支。	READY
107516_compact	107516	MPV	Vito W447	447.701		EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	HIGH	Compact物理分支。	READY
107516_long	107516	MPV	Vito W447	447.703		EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	HIGH	Long物理分支。	READY
107516_extralong	107516	MPV	Vito W447	447.705		EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	HIGH	Extra Long物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_10801-10900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-PREFL-01	4748	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 compact, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2003---2010.xhtml?oid=193898981
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-PREFL-01	4993	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 long, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2003---2010.xhtml?oid=193898982
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-PREFL-01	5223	1901	1872	Mercedes-Benz Public Archive - Viano CDI 2.2 extra long, 2003-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-extra-long-2003---2010.xhtml?oid=193898983
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-FACELIFT-01	4763	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 compact, 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2010---2014.xhtml?oid=193897440
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-FACELIFT-01	5008	1901	1875	Mercedes-Benz Public Archive - Viano CDI 2.2 long, 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2010---2014.xhtml?oid=193897441
EU-MERCEDES-BENZ-VIANO-W639-MPV-COMPACT-4MATIC-PREFL-01	4748	1901	1942	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC compact, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-compact-2006---2010.xhtml?oid=193898984
EU-MERCEDES-BENZ-VIANO-W639-MPV-LONG-4MATIC-PREFL-01	4993	1901	1942	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC long, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-long-2006---2010.xhtml?oid=193898985
EU-MERCEDES-BENZ-VIANO-W639-MPV-EXTRALONG-4MATIC-PREFL-01	5223	1901	1939	Mercedes-Benz Public Archive - Viano CDI 2.2 4MATIC extra long, 2006-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-extra-long-2006---2010.xhtml?oid=193898986
EU-MERCEDES-BENZ-VITO-W638-MPV-FACELIFT-01	4660	1880	1844	Mercedes-Benz Public Archive - 638 series V-Class Multi Purpose Vehicles 1999-2003; Mercedes-Benz Public Archive - V 220 CDI 1999-2003	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/638-series-V-Class-Multi-Purpose-Vehicles-1999---2003.xhtml?oid=5635;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/V-220-CDI-1999---2003.xhtml?oid=193665761
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-PREFL-01	4748	1901	1902	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-PREFL-01	4993	1901	1902	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-PREFL-01	5223	1901	1900	Mercedes-Benz France Vito 109/111/115 CDI bodybuilder sheet	https://www.yumpu.com/fr/document/view/22842049/fourvito-109-111-115-cdi-03-06-page-1-mercedes-benz-france
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-FACELIFT-01	4763	1901	1902	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-FACELIFT-01	5008	1901	1902	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-FACELIFT-01	5238	1901	1900	Mercedes-Benz Australia/Pacific Vito brochure, August 2013	https://vandimensions.com/media/pages/database/mercedes/vito-2/b45771c978-1628161086/mercedesbenz_vito_w639_brochure_201308.pdf
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-COMPACT-4X4-FACELIFT-01	4763	1901	1962	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L1H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77840/
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-LONG-4X4-FACELIFT-01	5008	1901	1962	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L2H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77843/
EU-MERCEDES-BENZ-VITO-W639-STANDARDROOF-EXTRALONG-4X4-FACELIFT-01	5238	1901	1960	Drom Mercedes-Benz Vito W639 113 CDI 4x4 AT L3H1	https://www.drom.ru/catalog/lcv/mercedes-benz/vito/77846/
EU-MERCEDES-BENZ-VITO-W639-E-CELL-LONG-FACELIFT-01	5008	1901	1895	Mercedes-Benz Vito E-CELL official brochure, 2011	https://manuals.plus/m/c431d8edfab37ad189fb516dad48accb05609bbc2732ac567b2cd43a41d1769d.pdf
EU-MERCEDES-BENZ-VITO-W447-STANDARD-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure, December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-STANDARD-LONG-01	5140	1928	1910	Mercedes-Benz Vito Panel and Crew Van official brochure, July 2023	https://bluesky-cogcms.cdn.imgeng.in/media/zbsgqv1o/64464-007-mb-vito-panel-van-and-crew-van-july-2023-aw-v3-final-270623.pdf
EU-MERCEDES-BENZ-VITO-W447-STANDARD-EXTRALONG-01	5370	1928	1910	Mercedes-Benz Vito Panel and Crew Van official brochure, July 2023	https://bluesky-cogcms.cdn.imgeng.in/media/zbsgqv1o/64464-007-mb-vito-panel-van-and-crew-van-july-2023-aw-v3-final-270623.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H1-01	5450	2206	2710	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L1H2-01	5450	2206	2865	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H1-01	6330	2206	2775	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L2H2-01	6330	2206	2930	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-VAN-RWD-L3H2-01	7210	2206	2935	Mercedes-Benz Vario official brochure 2011; Mercedes-Benz Vario bodybuilder guidelines 2009	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://mercedes-vario.de/dl/arl_vario_de_20090908.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L1-STDCAB-01	5330	2206	2395	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-STDCAB-01	6230	2240	2505	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-4X4-L2-CREWCAB-01	6250	2240	2515	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-STDCAB-01	5175	2206	2400	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L1-CREWCAB-01	5175	2206	2405	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-STDCAB-01	6055	2240	2500	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L2-CREWCAB-01	6055	2240	2505	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-STDCAB-01	6935	2240	2465	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-4X4-L3-CREWCAB-01	6935	2240	2470	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-STDCAB-01	5175	2206	2400	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L1-CREWCAB-01	5175	2206	2405	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-STDCAB-01	6055	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L2-CREWCAB-01	6055	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-STDCAB-01	6935	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L3-CREWCAB-01	6935	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-STDCAB-01	7485	2206	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-RWD-L4-CREWCAB-01	7485	2206	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L1-STDCAB-01	5330	2320	2395	Mercedes-Benz The Vario official brochure 2011	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-STDCAB-01	6230	2320	2405	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TIPPER-RWD-L2-CREWCAB-01	6250	2320	2410	Mercedes-Benz The Vario official brochure 2011; Mercedes-Benz Vario official specification sheet 2004	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-BUS-L1-01	6215	2205	2830	Mercedes-Benz The Vario official specification sheet 2004 - passenger carrying conversion	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-BUS-L2-01	7210	2205	2820	Mercedes-Benz The Vario official specification sheet 2004 - passenger carrying conversion	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-TRIEBKOPF-01	2040	2206	2405	Mercedes-Benz EPC model description mirror - 670.398 Vario chassis front end with cab; Mercedes-Benz Vario Chassis Cab official specification sheet 2004	https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en;https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_10801-10900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en "https://www.catcar.info/mercedes/?l=Y2xhc3M9PTN8fGNvdW50cnk9PTF8fHN0PT0yMHx8c3RzPT17IjEwIjoiQXNzb3J0bWVudCBjbGFzcyIsIjIwIjoiVmFuLUV1cm9wZSJ9&lang=en"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1599 行）
- 累计尺寸组：dimension_groups_final.tsv（430 行）

