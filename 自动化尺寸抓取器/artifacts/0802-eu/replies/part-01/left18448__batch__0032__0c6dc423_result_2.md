# 任务：left18448 第 3101-3200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0032__0c6dc423


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3101-3200 行

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
left18448 第 3101-3200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	3880	1670	1495
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	3880	1670	1495
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Chevrolet	Aveo / kalos	1.4 16V	Schrägheck	Frontantrieb	Benzin	May 2003	May 2008	18534
Chevrolet	Bel air	5.7	Stufenheck	Heckantrieb	Benzin	Sep 1972	Dec 1975	36473
Chevrolet	Blazer s10	4.3 AWD	Geländewagen geschlossen	Allrad	Benzin	Sep 1994	Sep 2005	36537
Chevrolet	Blazer s10	4.3 AWD	Geländewagen geschlossen	Allrad	Benzin	Oct 1994	Aug 2002	57227
Chevrolet	C1500 extended cab pickup	4.3	Pick-up	Heckantrieb	Benzin	Sep 1995	Dec 1998	111501
Chevrolet	C1500 standard cab pickup	4.3	Pick-up	Heckantrieb	Benzin	Sep 1995	Dec 1998	111489
Chevrolet	Camaro	2.8	Coupe	Heckantrieb	Benzin	Sep 1984	Dec 1992	36807
Chevrolet	Camaro	3.1	Coupe	Heckantrieb	Benzin	Sep 1989	Dec 1992	36813
Chevrolet	Camaro	3.6	Coupe	Heckantrieb	Benzin	Jan 2011	Dec 2015	9974
Chevrolet	Camaro	3.6	Cabriolet	Heckantrieb	Benzin	Jan 2011	-	9996
Chevrolet	Camaro	3.6	Cabriolet	Heckantrieb	Benzin	Sep 2011	-	56319
Chevrolet	Camaro	3.6	Coupe	Heckantrieb	Benzin	Sep 2011	Dec 2015	57405
Chevrolet	Camaro	3.8	Coupe	Heckantrieb	Benzin	Jul 1998	Dec 2002	11169
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	Jul 1998	Dec 2002	11170
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	Sep 1971	Dec 1976	112828
Chevrolet	Camaro	6.2	Coupe	Heckantrieb	Benzin	Sep 2009	Dec 2015	9975
Chevrolet	Camaro	6.2	Coupe	Heckantrieb	Benzin	Sep 2009	Dec 2015	9976
Chevrolet	Camaro	6.2	Cabriolet	Heckantrieb	Benzin	Jan 2011	-	9977
Chevrolet	Camaro	6.2	Cabriolet	Heckantrieb	Benzin	Jan 2011	-	9978
Chevrolet	Camaro	6.2	Coupe	Heckantrieb	Benzin	Sep 2015	-	116322
Chevrolet	Camaro	6.2	Cabriolet	Heckantrieb	Benzin	Jan 2016	-	119806
Chevrolet	Camaro	6.2	Coupe	Heckantrieb	Benzin	Jun 2016	-	120496
Chevrolet	Camaro	6.2	Cabriolet	Heckantrieb	Benzin	Jun 2016	-	120497
Chevrolet	Camaro	2.0 Turbo	Coupe	Heckantrieb	Benzin	Aug 2016	-	121704
Chevrolet	Camaro	2.0 Turbo	Cabriolet	Heckantrieb	Benzin	Aug 2016	-	121706
Chevrolet	Camaro	3.4 V6	Coupe	Heckantrieb	Benzin	Dec 1992	Jul 1998	11919
Chevrolet	Camaro	3.8 V6	Cabriolet	Heckantrieb	Benzin	Jul 1998	Dec 2002	11171
Chevrolet	Camaro	5.7 V8	Coupe	Heckantrieb	Benzin	Dec 1992	Jul 1998	11920
Chevrolet	Camaro	5.7 Z28	Cabriolet	Heckantrieb	Benzin	Sep 1986	Sep 1988	36796
Chevrolet	Camaro	6.2 ZL1	Coupe	Heckantrieb	Benzin	Sep 2012	Dec 2015	54446
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	Sep 1976	Dec 1987	57239
Chevrolet	Caprice	5.7	Coupe	Heckantrieb	Benzin	Sep 1976	Dec 1979	52186
Chevrolet	Caprice	5.7	Stufenheck	Heckantrieb	Benzin	Sep 1974	Dec 1975	125527
Chevrolet	Caprice	6.6	Coupe	Heckantrieb	Benzin	Sep 1974	Dec 1976	36834
Chevrolet	Caprice	6.6	Stufenheck	Heckantrieb	Benzin	Sep 1973	Dec 1974	112859
Chevrolet	Captiva	2.2 D 4WD	SUV	Allrad	Diesel	Mar 2011	-	10032
Chevrolet	Captiva	2.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Jan 2007	-	34972
Chevrolet	Captiva	2.4 LPG 4WD	SUV	Allrad	Benzin/Autogas (LPG)	Jan 2007	Feb 2011	34973
Chevrolet	Captiva	Vcdi	Kasten/SUV	Frontantrieb	Diesel	Oct 2006	Dec 2009	142562
Chevrolet	Captiva	Vcdi Allrad	Kasten/SUV	Allrad	Diesel	Jul 2006	Feb 2011	142561
Chevrolet	Celebrity	2.8	Stufenheck	Frontantrieb	Benzin	Sep 1981	Dec 1986	36934
Chevrolet	Cheyenne crew cab pickup	6.2 4WD	Pick-up	Allrad	Benzin	Sep 2013	-	107586
Chevrolet	Cheyenne standard cab pickup	6.2 4WD	Pick-up	Allrad	Benzin	Sep 2013	-	107583
Chevrolet	Colorado	2.8	Pick-up	Heckantrieb	Benzin	Sep 2006	Dec 2006	37001
Chevrolet	Colorado	2.8	Pick-up	Heckantrieb	Benzin	Sep 2003	Dec 2006	37009
Chevrolet	Colorado	2.8	Pick-up	Heckantrieb	Benzin	Sep 2003	Dec 2006	111735
Chevrolet	Colorado	2.9	Pick-up	Heckantrieb	Benzin	Sep 2006	Dec 2012	37005
Chevrolet	Colorado	3.5	Pick-up	Heckantrieb	Benzin	Sep 2003	Dec 2006	37003
Chevrolet	Colorado	3.5	Pick-up	Heckantrieb	Benzin	Sep 2003	Dec 2006	111737
Chevrolet	Colorado	3.5	Pick-up	Heckantrieb	Benzin	Sep 2003	Dec 2006	111739
Chevrolet	Colorado	3.7	Pick-up	Heckantrieb	Benzin	Sep 2006	Dec 2012	37007
Chevrolet	Colorado	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2003	Dec 2006	37004
Chevrolet	Colorado	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2003	Dec 2006	111738
Chevrolet	Colorado	3.5 4WD	Pick-up	Allrad	Benzin	Sep 2003	Dec 2006	111740
Chevrolet	Colorado	3.7 4WD	Pick-up	Allrad	Benzin	Sep 2006	Dec 2012	37008
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	Sep 1997	Sep 2004	11168
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1975	Dec 1977	37049
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1977	Dec 1978	111827
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1983	Dec 1984	111831
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1986	Dec 1989	111833
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1987	Dec 1991	111834
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	Sep 1997	Dec 2000	111836
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1997	Dec 2000	111837
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1974	Dec 1975	125500
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1989	Dec 1990	125504
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	Sep 1989	Dec 1990	125505
Chevrolet	Corvette	6	Coupe	Heckantrieb	Benzin	Sep 2004	Aug 2013	17835
Chevrolet	Corvette	6.2	Coupe	Heckantrieb	Benzin	Apr 2014	Dec 2019	105639
Chevrolet	Corvette	6.2	Cabriolet	Heckantrieb	Benzin	Apr 2014	Dec 2019	105640
Chevrolet	Corvette	6.2	Coupe	Heckantrieb	Benzin	Jan 2022	-	146989
Chevrolet	Corvette	6.2	Cabriolet	Heckantrieb	Benzin	Jan 2022	-	146990
Chevrolet	Corvette	7.4	Coupe	Heckantrieb	Benzin	Sep 1971	Dec 1974	112573
Chevrolet	Corvette	5.7 Zr-1	Coupe	Heckantrieb	Benzin	Sep 1989	Dec 1990	37057
Chevrolet	Corvette	6.2 E-ray AWD	Coupe	Allrad	Benzin/Elektro	Dec 2024	-	802180
Chevrolet	Corvette	6.2 E-ray AWD	Cabriolet	Allrad	Benzin/Elektro	Dec 2024	-	802181
Chevrolet	Corvette	6.2 Z06	Cabriolet	Heckantrieb	Benzin	Sep 2014	Nov 2019	107980
Chevrolet	Corvette	6.2 Z06	Coupe	Heckantrieb	Benzin	Sep 2014	Nov 2019	107981
Chevrolet	Corvette	6.2 ZR1	Cabriolet	Heckantrieb	Benzin	Sep 2008	Apr 2010	100274
Chevrolet	Corvette	Z06 5.5	Cabriolet	Heckantrieb	Benzin	Jul 2022	-	150627
Chevrolet	Corvette	Z06 5.5	Coupe	Heckantrieb	Benzin	Jul 2022	-	150628
Chevrolet	Corvette	Z06 5.5	Coupe	Heckantrieb	Benzin	Jul 2022	-	156315
Chevrolet	Corvette	Z06 5.5	Cabriolet	Heckantrieb	Benzin	Mar 2023	-	800931
Chevrolet	Corvette	Z06 7.0	Cabriolet	Heckantrieb	Benzin	Jun 2012	Aug 2013	56759
Chevrolet	Cruze	1.4	Stufenheck	Frontantrieb	Benzin	Sep 2010	-	51391
Chevrolet	Cruze	1.4	Stufenheck	Frontantrieb	Benzin	Jul 2013	-	55461
Chevrolet	Cruze	1.4	Schrägheck	Frontantrieb	Benzin	Jul 2013	Dec 2015	55465
Chevrolet	Cruze	1.4	Kombi	Frontantrieb	Benzin	Jul 2013	Dec 2015	55475
Chevrolet	Cruze	1.4	Kombi	Frontantrieb	Benzin	Aug 2012	-	55798
Chevrolet	Cruze	1.4	Schrägheck	Frontantrieb	Benzin	Jun 2012	-	56753
Chevrolet	Cruze	1.6	Stufenheck	Frontantrieb	Benzin	May 2009	-	8711
Chevrolet	Cruze	1.6	Stufenheck	Frontantrieb	Benzin	May 2009	-	8771
Chevrolet	Cruze	1.6	Schrägheck	Frontantrieb	Benzin	Jun 2011	-	10352
Chevrolet	Cruze	1.6	Kombi	Frontantrieb	Benzin	Aug 2012	Dec 2015	55799
Chevrolet	Cruze	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2012	-	57414
Chevrolet	Cruze	1.6	Kombi	Frontantrieb	Benzin	Dec 2012	Dec 2015	57419
Chevrolet	Cruze	1.8	Schrägheck	Frontantrieb	Benzin	Jun 2011	-	10351
Chevrolet	Cruze	1.8	Kombi	Frontantrieb	Benzin	Aug 2012	-	55800
Chevrolet	Cruze	1.7 D	Stufenheck	Frontantrieb	Diesel	Jan 2012	-	13909
Chevrolet	Cruze	1.7 D	Schrägheck	Frontantrieb	Diesel	Jan 2012	Dec 2015	13914
Chevrolet	Cruze	1.7 TD	Schrägheck	Frontantrieb	Diesel	Aug 2013	Dec 2015	35426


--- Round 1 / 首次发送 ---
## 更新点

* 已确认 `18534` 对应 Aveo/Kalos T200 五门掀背车，直接复用跨批次已有的五门尺寸组，不重复输出尺寸来源。([Red Desguace][1])
* 已闭合 Cruze I 的 `J300` 四门、`J305` 五门掀背和 `J308` 旅行车边界；其中 `57414` 为 2012 年末开始的 J305 型式，`55461`、`55465` 分别为 2013 年 7 月开始的 J300/J305 型式。([Alufelgen Sportfahrwerke und mehr][2])
* `13914` 的输入生产区间覆盖 J305 改款前后两套外廓，因此拆分为 `prefl` 和 `facelift` 两条映射；改款前、改款后掀背车长度分别为 4510 mm 和 4514 mm。相关三维分别由 GM 规格表和 Chevrolet 官方车型手册闭合。([Alufelgen Sportfahrwerke und mehr][3])
* 本轮首次创建 4 个 Cruze 尺寸组；Aveo/Kalos 已有组未重复输出。

## 当前批次进度

* READY 映射行：12
* 已闭合输入 Ktype：11
* PENDING 输入 Ktype：89
* 已确认且被引用尺寸组：5（复用已有组 1 个，本轮新增 4 个）
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18534	18534	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	HIGH	T200五门掀背外廓。	READY
55461	55461	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	HIGH	改款后J300四门外廓。	READY
55465	55465	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
55475	55475	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
55798	55798	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
57414	57414	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	2012年末起型式，按改款后J305五门外廓。	READY
55799	55799	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
57419	57419	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
55800	55800	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
13914_prefl	13914	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
13914_facelift	13914	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
35426	35426	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	4603	1797	1477	Chevrolet UK 2014 Cruze 4-Door official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-4-Door-UK.pdf
EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	4514	1797	1477	Chevrolet UK 2014 Cruze 5-Door official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-5-Door-UK.pdf
EU-CHEVROLET-CRUZE-I-WAGON-01	4681	1797	1521	Chevrolet UK 2014 Cruze Station Wagon official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-Station-Wagon-UK.pdf
EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	4510	1797	1477	GM Chevrolet Cruze Hatchback Specifications and Features	https://media.gm.com/content/dam/Media/documents/CN/Vehicle_Spec/Chevrolet/Chevrolet%20Cruze%20Hatchback%20Specifications%20and%20Features.pdf
```

## 下一步优先处理

1. 按代际和 Coupe/Convertible 聚类处理 Camaro，优先闭合高复用的第五代、第六代尺寸组。
2. 按 C3、C4、C5、C6、C7、C8 聚类处理 Corvette，并单独核对 Z06、ZR1、E-Ray 等宽体或特殊外廓。
3. 随后处理 Captiva，以及 Colorado、C1500、Cheyenne 的驾驶室和货斗分支。

推进信号：CONTINUE

[1]: https://www.reddesguace.com/pieza/chevrolet/kalos/539000_sistema-audio-radio-cd-96454094?utm_source=chatgpt.com "SISTEMA AUDIO / RADIO CD CHEVROLET KALOS 1.4 CAT ..."
[2]: https://www.jms-fahrzeugteile.com/en/brake-technology/ebc-brake-discsbrake-pads/ebc-standard-bremsbelaege-fuer/chevrolet/cruze/vavornefront/1155532/ebc-blackstuff-pads-dpx2067-7652-fits-for-chevrolet-cruze-j305?utm_source=chatgpt.com "EBC Blackstuff pads DPX2067(7652) fits for Chevrolet Cruze J305 | JMS Fahrzeugteile"
[3]: https://www.jms-fahrzeugteile.com/en/brake-technology/ebc-brake-discsbrake-pads/ebc-standard-bremsbelaege-fuer/chevrolet/cruze/hahintenrear/1155516/ebc-blackstuff-pads-dpx2066-7636-fits-for-chevrolet-cruze-j305?utm_source=chatgpt.com "EBC Blackstuff pads DPX2066(7636) fits for Chevrolet Cruze J305 | JMS Fahrzeugteile"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Camaro V 中明确覆盖 2014 改款前后的 7 个 Ktype，按 `prefl`、`facelift` 拆分为 14 条映射。
* Camaro V 改款前 Coupe/Convertible 外廓为 `4836 × 1918 × 1376/1389 mm`；2014 改款后车身长度增至 `4841 mm`，Coupe 与 Convertible 高度仍分别为 `1376 mm`、`1389 mm`。([PR Newswire][1])
* `9977`、`9978` 的 Ktype 适用资料明确对应第五代 Camaro Convertible，并覆盖至第五代后期，因此同步建立改款前后分支。([NAP Sportauspuff][2])
* 本轮首次创建 4 个 Camaro V 尺寸组；其余已闭合 Aveo/Kalos、Cruze 尺寸组未重复输出。

## 当前批次进度

* READY 映射行：26
* 已闭合输入 Ktype：18
* PENDING 输入 Ktype：82
* 已确认且被引用尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9974_prefl	9974	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9974_facelift	9974	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
57405_prefl	57405	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
57405_facelift	57405	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9975_prefl	9975	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9975_facelift	9975	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9976_prefl	9976	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9976_facelift	9976	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9977_prefl	9977	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9977_facelift	9977	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
9978_prefl	9978	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9978_facelift	9978	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
54446_prefl	54446	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	ZL1改款前外廓。	READY
54446_facelift	54446	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	ZL1改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	4836	1918	1376	General Motors 2011 Camaro Coupe and Convertible specifications	https://www.prnewswire.com/news-releases/new-camaro-convertible-blends-top-down-driving-fun-with-precise-engineering-108379814.html
EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	4836	1918	1389	General Motors 2011 Camaro Coupe and Convertible specifications	https://www.prnewswire.com/news-releases/new-camaro-convertible-blends-top-down-driving-fun-with-precise-engineering-108379814.html
EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	4841	1918	1376	GM Canada 2014 Camaro Quick Facts; Chevrolet 2015 Camaro ZL1 official specifications	https://media.gm.ca/content/dam/Media/microsites/product/canada_retiree/Documents/en/Products/Pamphlets/2014/2014_Chevrolet_Camaro.pdf;https://autoinfo.jp/release/MY15_Camaro_ZL1.pdf
EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	4841	1918	1389	GM Canada 2014 Camaro Quick Facts; Chevrolet 2015 Camaro ZL1 official specifications	https://media.gm.ca/content/dam/Media/microsites/product/canada_retiree/Documents/en/Products/Pamphlets/2014/2014_Chevrolet_Camaro.pdf;https://autoinfo.jp/release/MY15_Camaro_ZL1.pdf
```

## 下一步优先处理

1. 闭合 `9996`、`56319` 两个 Camaro V 3.6 Convertible Ktype 的改款覆盖边界。
2. 处理 Camaro VI，区分普通 Coupe、Convertible 与后期改款或特殊外观套件。
3. 随后聚类处理 Camaro III、Camaro IV，再转入 Corvette 高复用代际组。

推进信号：CONTINUE

[1]: https://www.prnewswire.com/news-releases/new-camaro-convertible-blends-top-down-driving-fun-with-precise-engineering-108379814.html "New Camaro Convertible Blends Top-Down Driving Fun With Precise Engineering"
[2]: https://www.nap-sportauspuff.com/shop/nap-klappenauspuff-chevrolet-camaro-2015-x-pipeedelstahlnap-automatic-valve-control/?utm_source=chatgpt.com "NAP Klappenauspuff passend für Chevrolet Camaro (Gen. 5)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 补齐 `9996`、`56319` 的 Camaro V Convertible 改款前后分支，直接复用已闭合的两个敞篷尺寸组。
* 闭合 Camaro VI 的普通 Coupe 与 Convertible 外廓，共关联 6 个 Ktype。
* Camaro VI 标准 Coupe/Convertible 在 2016 与 2019 年资料中的长度、宽度及对应车身高度一致，因此不按 2019 外观改款重复拆组。2019 官方目录列明普通 LS/LT/SS 长度 `188.3 in`、宽度 `74.7 in`，Coupe 高度 `53.1 in`、Convertible 高度 `52.9 in`；2016 规格资料明确宽度为不含后视镜口径。

## 当前批次进度

* READY 映射行：36
* 已闭合输入 Ktype：26
* PENDING 输入 Ktype：74
* 已确认且被引用尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9996_prefl	9996	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9996_facelift	9996	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
56319_prefl	56319	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
56319_facelift	56319	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
116322	116322	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
119806	119806	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
120496	120496	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
120497	120497	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
121704	121704	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
121706	121706	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-VI-COUPE-01	4783	1897	1349	Chevrolet 2019 Camaro official catalog; Car and Driver 2016 Camaro Coupe specifications	https://dealerinspire-brochure.s3.amazonaws.com/1785.pdf;https://www.caranddriver.com/chevrolet/camaro/specs/2016/chevrolet_camaro_chevrolet-camaro-ss-coupe_2016
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4783	1897	1344	Chevrolet 2019 Camaro official catalog; Car and Driver 2016 Camaro Convertible specifications	https://dealerinspire-brochure.s3.amazonaws.com/1785.pdf;https://www.caranddriver.com/chevrolet/camaro/specs/2016/chevrolet_camaro_chevrolet-camaro-ss-convertible_2016
```

## 下一步优先处理

1. 闭合 Camaro III：普通 Coupe 与 Convertible，核对 1984—1992 年改款是否造成外廓变化。
2. 闭合 Camaro IV：1993—1997 与 1998—2002 前后期 Coupe/Convertible。
3. 处理 Camaro II 后，转入 Corvette，并按 C3—C8 及 Z06、ZR1、E-Ray 特殊外廓聚类。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Camaro III 的 2.8 Coupe、3.1 Coupe 和 Z28 Convertible；`36813` 横跨 1990 年外廓与 1991–1992 改款外廓，拆分为 `prefl`、`facelift` 两条映射。([汽车目录][1])
* 已闭合 Camaro IV 的 1993–1997 Coupe、1998–2002 Coupe 与 1998–2002 Convertible 外廓。([汽车目录档案][2])

## 当前批次进度

* READY 映射行：45
* 已闭合输入 Ktype：34
* PENDING 输入 Ktype：66
* 已确认且被引用尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
36807	36807	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-BASE-PREFL-01	HIGH	2.8基础Coupe外廓。	READY
36813_prefl	36813	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-RS-PREFL-01	HIGH	1990款RS Coupe外廓。	READY
36813_facelift	36813	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-RS-FACELIFT-01	HIGH	1991至1992款RS Coupe外廓。	READY
11169	11169	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	HIGH	1998至2002款Coupe外廓。	READY
11170	11170	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	HIGH	1998至2002款Coupe外廓。	READY
11919	11919	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	HIGH	3.4 V6改款前Coupe外廓。	READY
11171	11171	Convertible	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-CONVERTIBLE-FACELIFT-01	HIGH	1998至2002款Convertible外廓。	READY
11920	11920	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	HIGH	5.7 LT1改款前Coupe外廓。	READY
36796	36796	Convertible	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-CONVERTIBLE-Z28-PREFL-01	HIGH	Z28 Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-III-COUPE-BASE-PREFL-01	4775	1849	1270	Automobile-Catalog 1985 Chevrolet Camaro Sport Coupe specifications	https://www.automobile-catalog.com/car/1985/458690/chevrolet_camaro_sport_coupe_2_8l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-III-COUPE-RS-PREFL-01	4877	1849	1278	Automobile-Catalog 1990 Chevrolet Camaro RS specifications	https://www.automobile-catalog.com/car/1990/459935/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-III-COUPE-RS-FACELIFT-01	4892	1839	1280	Automobile-Catalog 1991 Chevrolet Camaro RS specifications	https://www.automobile-catalog.com/car/1991/460130/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	4915	1882	1303	GM Heritage 1998 Chevrolet Camaro vehicle information kit; Automobile-Catalog 1998 Camaro specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Camaro.pdf;https://www.automobile-catalog.com/car/1998/473135/chevrolet_camaro_z28_ss.html
EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	4907	1882	1303	GM Heritage 1993 Chevrolet Camaro vehicle information kit; Automobile-Catalog 1995 Camaro specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1993-Chevrolet-Camaro.pdf;https://www.automobile-catalog.com/car/1995/1503620/chevrolet_camaro_z28.html
EU-CHEVROLET-CAMARO-IV-CONVERTIBLE-FACELIFT-01	4915	1882	1321	GM Heritage 1998 Chevrolet Camaro vehicle information kit; Edmunds 1998 Camaro Convertible specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Camaro.pdf;https://www.edmunds.com/chevrolet/camaro/1998/convertible/features-specs/
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-Z28-PREFL-01	4877	1849	1278	Automobile-Catalog 1987 Chevrolet Camaro Z28 Convertible specifications	https://www.automobile-catalog.com/car/1987/459290/chevrolet_camaro_z28_convertible_5_0l_v-8.html
```

## 下一步优先处理

* 闭合第二代 Camaro `112828`，随后按 C3、C4、C5、C6、C7、C8 聚类处理 Corvette，并单独处理 Z06、ZR1、E-Ray 等特殊外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/458690/chevrolet_camaro_sport_coupe_2_8l_v-6_mfi_automatic.html?utm_source=chatgpt.com "1985 Chevrolet Camaro Sport Coupe 2.8L V-6 MFI automatic Specs Review (100.5 kW / 137 PS / 135 hp) (since November 1984 for North America )"
[2]: https://autocatalogarchive.com/wp-content/uploads/2016/07/Chevrolet-Camaro-1993.pdf?utm_source=chatgpt.com "Chevrolet Camaro (1993)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Corvette C8 Stingray、Z06、E-Ray 的 Coupe 与 Convertible 外廓，共新增 8 条映射、6 个尺寸组。Stingray 官方欧洲规格分别列出两种车身的三维；Z06 与 E-Ray 官方欧洲规格给出长度区间，本轮依照“最大车身外部长度”口径取上限 `4734 mm`。
* Z06 与 E-Ray 均明确提供 Coupe 和硬顶 Convertible，因车身高度不同分别建组；同车型的重复 Ktype 直接复用对应尺寸组。([雪佛兰新闻中心][1])

## 当前批次进度

* READY 映射行：53
* 已闭合输入 Ktype：42
* PENDING 输入 Ktype：58
* 已确认且被引用尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146989	146989	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-STINGRAY-01	HIGH	C8 Stingray双门Coupe外廓。	READY
146990	146990	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-STINGRAY-01	HIGH	C8 Stingray双门Convertible外廓。	READY
802180	802180	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-ERAY-01	HIGH	C8 E-Ray宽体Coupe外廓。	READY
802181	802181	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-ERAY-01	HIGH	C8 E-Ray宽体Convertible外廓。	READY
150627	150627	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	HIGH	C8 Z06宽体Convertible外廓。	READY
150628	150628	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	HIGH	C8 Z06宽体Coupe外廓。	READY
156315	156315	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	HIGH	C8 Z06宽体Coupe外廓。	READY
800931	800931	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	HIGH	C8 Z06宽体Convertible外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORVETTE-C8-COUPE-STINGRAY-01	4634	1934	1235	Chevrolet Corvette Stingray official European technical specifications; Edmunds 2022 Corvette Coupe specifications	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-TechSpecs_EN.pdf;https://www.edmunds.com/chevrolet/corvette/2022/coupe/features-specs/
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-STINGRAY-01	4634	1934	1234	Chevrolet Corvette Stingray official European technical specifications; Edmunds 2022 Corvette Convertible specifications	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-TechSpecs_EN.pdf;https://www.edmunds.com/chevrolet/corvette/2022/convertible/st-401899994/features-specs/
EU-CHEVROLET-CORVETTE-C8-COUPE-ERAY-01	4734	2024	1237	Chevrolet Europe Corvette E-Ray official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_E-Ray_Specifications.pdf
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-ERAY-01	4734	2024	1236	Chevrolet Europe Corvette E-Ray official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_E-Ray_Specifications.pdf
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	4734	2024	1236	Chevrolet Europe Corvette Z06 official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_Z06_Specifications_2025.pdf
EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	4734	2024	1237	Chevrolet Europe Corvette Z06 official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_Z06_Specifications_2025.pdf
```

## 下一步优先处理

1. 按 C3、C4、C5、C6、C7 聚类闭合其余 Corvette Ktype。
2. 单独核对 C7 Z06 与 C6 ZR1、Z06 等特殊宽体外廓，避免误用标准代际尺寸组。
3. Corvette 完成后处理 Captiva 与剩余 Chevrolet 轿车、SUV、皮卡车型簇。

推进信号：CONTINUE

[1]: https://news.chevrolet.com/newsroom.detail.html/Pages/news/us/en/2021/oct/1026-corvette-z06.html "2023 Chevrolet Corvette Z06 Elevates the American Supercar"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 Corvette C5、C6、C7 的标准 Coupe/Convertible，以及 C6 Z06、C6 ZR1、C7 Z06 特殊外廓。C6 官方规格明确区分标准窄体与 Z06/ZR1 宽体，C7 官方资料分别给出 Stingray 与 Z06 的不含后视镜宽度。([Edmunds][1])
* `100274` 与 `56759` 的输入 `Cabriolet` 标注和量产 ZR1/Z06 车身形式冲突，本轮按实际 Coupe 物理外廓落盘；两者分别使用独立的 ZR1、Z06 尺寸组。([汽车目录][2])

## 当前批次进度

* READY 映射行：63
* 已闭合输入 Ktype：52
* PENDING 输入 Ktype：48
* 已确认且被引用尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11168	11168	Convertible	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	HIGH	C5双门Convertible外廓。	READY
111836	111836	Convertible	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	HIGH	C5双门Convertible外廓。	READY
111837	111837	Coupe	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-COUPE-01	HIGH	C5双门Coupe外廓。	READY
17835	17835	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-01	HIGH	C6标准Coupe外廓。	READY
100274	100274	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	HIGH	输入Cabriolet与量产ZR1车身冲突，按Coupe外廓。	READY
56759	56759	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	HIGH	输入Cabriolet与量产Z06车身冲突，按Coupe外廓。	READY
105639	105639	Coupe	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-COUPE-STINGRAY-01	HIGH	C7 Stingray双门Coupe外廓。	READY
105640	105640	Convertible	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-STINGRAY-01	HIGH	C7 Stingray双门Convertible外廓。	READY
107980	107980	Convertible	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-Z06-01	HIGH	C7 Z06宽体Convertible外廓。	READY
107981	107981	Coupe	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-COUPE-Z06-01	HIGH	C7 Z06宽体Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	4564	1869	1214	Edmunds 2004 Chevrolet Corvette Convertible specifications	https://www.edmunds.com/chevrolet/corvette/2004/convertible/features-specs/
EU-CHEVROLET-CORVETTE-C5-COUPE-01	4564	1869	1212	Edmunds 2004 Chevrolet Corvette Coupe specifications	https://www.edmunds.com/chevrolet/corvette/2004/coupe/features-specs/
EU-CHEVROLET-CORVETTE-C6-COUPE-01	4435	1844	1247	Chevrolet 2013 Corvette official order guide	https://www.corvetteactioncenter.com/specs/c6/2013/2013_Corvette_Order_Guide.pdf
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4476	1928	1244	Automobile-Catalog 2009 Chevrolet Corvette ZR1 specifications	https://www.automobile-catalog.com/car/2009/479435/chevrolet_corvette_zr1.html
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237	Chevrolet 2013 Corvette official order guide	https://www.corvetteactioncenter.com/specs/c6/2013/2013_Corvette_Order_Guide.pdf
EU-CHEVROLET-CORVETTE-C7-COUPE-STINGRAY-01	4492	1872	1239	Chevrolet Corvette Stingray official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-Technical-Data_en.pdf
EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-STINGRAY-01	4492	1872	1243	Chevrolet Corvette Stingray official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-Technical-Data_en.pdf
EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-Z06-01	4514	1965	1243	Chevrolet Corvette Z06 official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/corvette-z06/Tech-Data-Chevrolet-Corvette-Z06.pdf
EU-CHEVROLET-CORVETTE-C7-COUPE-Z06-01	4514	1965	1239	Chevrolet Corvette Z06 official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/corvette-z06/Tech-Data-Chevrolet-Corvette-Z06.pdf
```

## 下一步优先处理

1. 闭合 Corvette C3、C4 的年份和前后期外廓。
2. 完成第二代 Camaro `112828`。
3. 随后处理 Captiva、Blazer S10 与其余轿车、皮卡车型簇。

推进信号：CONTINUE

[1]: https://www.edmunds.com/chevrolet/corvette/2004/convertible/features-specs/ "Used 2004 Chevrolet Corvette Convertible Specs & Features | Edmunds"
[2]: https://www.automobile-catalog.com/car/2009/479435/chevrolet_corvette_zr1.html?utm_source=chatgpt.com "2009 Chevrolet Corvette ZR1 Specs Review (476 kW / 647 PS / 638 hp) (since mid-year 2008 for North America )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Corvette C3 的 1975、1976–1977 和 1978 三个物理阶段。1978 年外部车身边界发生变化，因此即使三维相同，仍独立建立尺寸组。官方年款资料确认长度为 185.2 in、宽度为 69.0 in，高度分别为 48.1 in 或 48.0 in。
* 已闭合 Corvette C4 标准 Coupe 改款前、1991 改款后及 ZR-1 宽体外廓；`111834` 覆盖 1991 外观改款边界，拆分为两条派生映射。

## 当前批次进度

* READY 映射行：73
* 已闭合输入 Ktype：61
* PENDING 输入 Ktype：39
* 已确认且被引用尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
37049	37049	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1976-1977-01	HIGH	1976至1977款C3 Coupe外廓。	READY
111827	111827	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1978-01	HIGH	1978款C3 Coupe外廓。	READY
111831	111831	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	改款前C4 Coupe外廓。	READY
111833	111833	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	改款前C4 Coupe外廓。	READY
111834_prefl	111834	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖1991改款前外廓。	READY
111834_facelift	111834	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖1991改款后外廓。	READY
125500	125500	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	HIGH	1975款C3 Coupe外廓。	READY
125504	125504	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	1990款标准C4 Coupe外廓。	READY
125505	125505	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	1990款标准C4 Coupe外廓。	READY
37057	37057	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-ZR1-01	HIGH	C4 ZR-1宽体Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORVETTE-C3-COUPE-1976-1977-01	4704	1753	1219	GM Heritage 1976 Chevrolet Corvette vehicle information kit;GM Heritage 1977 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1976-Chevrolet-Corvette.pdf;https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1977-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C3-COUPE-1978-01	4704	1753	1219	GM Heritage 1978 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	4483	1803	1186	Automobile-Catalog 1984 Chevrolet Corvette specifications;Chevrolet 1989 Corvette brochure	https://www.automobile-catalog.com/car/1984/29570/chevrolet_corvette.html;https://autocatalogarchive.com/wp-content/uploads/2016/07/Chevrolet-Corvette-1989-.pdf
EU-CHEVROLET-CORVETTE-C4-COUPE-FACELIFT-01	4483	1803	1186	GM Heritage 1991 Chevrolet Corvette vehicle information kit;Corvsport 1991 Corvette specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1991-Chevrolet-Corvette.pdf;https://www.corvsport.com/1991-corvette-specifications/
EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	4704	1753	1222	GM Heritage 1975 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1975-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C4-COUPE-ZR1-01	4506	1880	1189	Automobile-Catalog 1990 Chevrolet Corvette ZR-1 specifications	https://www.automobile-catalog.com/car/1990/463655/chevrolet_corvette_zr-1.html
```

## 下一步优先处理

1. 闭合跨越多个 C3 外观阶段的 `112573`，按确认后的物理边界完整派生。
2. 闭合第二代 Camaro `112828` 的年份和改款分支。
3. 随后处理 Captiva、Blazer S10、Bel Air、Caprice 与 Celebrity 车型簇。

推进信号：CONTINUE


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合 `112573` 覆盖的 1972、1973、1974 三个 Corvette C3 年款外廓；三年长度分别为 182.5、184.7、185.5 英寸，按年款拆分。([CorvSport.com][1])
* 已闭合 `112828` 覆盖的 1972—1976 Camaro II。1972、1973 长度不同；1974 更换保险杠后长度增至 195.4 英寸；1975 的环绕式后窗改变物理车身边界；1976 官方规格高度变为 49.2 英寸，因此按五个年款分支落盘。([汽车目录档案][2])
* 已闭合 Captiva I 改款前 C100 与改款后 C140 两个外廓；四个早期 Ktype 复用 C100 组，`10032` 使用 C140 组。改款后官方规格为 `4673 × 1849 × 1727 mm`。([汽车目录][3])

## 当前批次进度

* READY 映射行：86
* 已闭合输入 Ktype：68
* PENDING 输入 Ktype：32
* 已确认且被引用尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
112573_1972	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1972-01	HIGH	1972款C3 Coupe外廓。	READY
112573_1973	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1973-01	HIGH	1973款C3 Coupe外廓。	READY
112573_1974	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1974-01	HIGH	1974款C3 Coupe外廓。	READY
112828_1972	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1972-01	HIGH	1972款Coupe外廓。	READY
112828_1973	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1973-01	HIGH	1973款Coupe外廓。	READY
112828_1974	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1974-01	HIGH	1974款保险杠外廓。	READY
112828_1975	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1975-01	HIGH	1975款环绕式后窗外廓。	READY
112828_1976	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1976-01	HIGH	1976款Coupe外廓。	READY
10032	10032	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-SUV-FACELIFT-01	HIGH	C140改款后五门SUV外廓。	READY
34972	34972	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	MEDIUM	2.4 LPG对应C100外廓。	READY
34973	34973	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	C100改款前五门SUV外廓。	READY
142562	142562	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	商用登记不改变C100外部车身。	READY
142561	142561	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	商用登记不改变C100外部车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORVETTE-C3-COUPE-1972-01	4636	1753	1214	Chevrolet 1972 Corvette official brochure;Corvsport 1972 Corvette specifications	https://xr793.com/wp-content/uploads/2017/07/1972-Chevrolet-Corvette.pdf;https://www.corvsport.com/1972-corvette-specifications/
EU-CHEVROLET-CORVETTE-C3-COUPE-1973-01	4691	1753	1212	Chevrolet 1973 Corvette official brochure	https://xr793.com/wp-content/uploads/2017/07/1973-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C3-COUPE-1974-01	4712	1753	1214	Chevrolet 1974 Corvette official brochure;Carfolio 1974 Corvette specifications	https://autocatalogarchive.com/wp-content/uploads/2018/02/Chevrolet-Corvette-1974-USA.pdf;https://www.carfolio.com/chevrolet-corvette-stingray-90013
EU-CHEVROLET-CAMARO-II-COUPE-1972-01	4775	1890	1247	Chevrolet 1972 Camaro official brochure;Automobile-Catalog 1972 Camaro SS specifications	https://autocatalogarchive.com/wp-content/uploads/2024/09/Chevrolet-Camaro-1972-USA.pdf;https://www.automobile-catalog.com/car/1972/101480/chevrolet_camaro_ss_396.html
EU-CHEVROLET-CAMARO-II-COUPE-1973-01	4785	1890	1247	Chevrolet 1973 Camaro official brochure;Automobile-Catalog 1973 Camaro specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Chevrolet-Camaro-1973.pdf;https://www.automobile-catalog.com/make/chevrolet_usa/camaro_2gen/camaro_2gen_lt/1973.html
EU-CHEVROLET-CAMARO-II-COUPE-1974-01	4963	1890	1247	Chevrolet 1974 Camaro official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/09/Chevrolet-Camaro-1974-USA-.pdf
EU-CHEVROLET-CAMARO-II-COUPE-1975-01	4963	1890	1247	Chevrolet 1975 Camaro official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/10/Chevrolet-Camaro-1975-USA.pdf
EU-CHEVROLET-CAMARO-II-COUPE-1976-01	4963	1890	1250	Chevrolet 1976 Camaro official brochure;Automobile-Catalog 1976 Camaro specifications	https://autocatalogarchive.com/wp-content/uploads/2024/10/Chevrolet-Camaro-1976-USA.pdf;https://www.automobile-catalog.com/car/1976/205475/chevrolet_camaro_type_lt_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Europe Captiva specifications;Auto-Data Chevrolet Captiva I specifications	https://www.automobile-catalog.com/make/chevrolet_europe/windstorm_captiva_europe/windstorm_captiva_eu/2007.html;https://www.auto-data.net/en/chevrolet-captiva-model-1623
EU-CHEVROLET-CAPTIVA-I-SUV-FACELIFT-01	4673	1849	1727	Chevrolet UK 2014 Captiva official specifications	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Captiva-UK.pdf
```

## 下一步优先处理

* 闭合 Blazer S10 两个 Ktype，以及 Bel Air、Caprice、Celebrity 等传统乘用车；随后集中处理 C1500、Cheyenne、Colorado 的驾驶室、轴距和货斗分支。

推进信号：CONTINUE

[1]: https://www.corvsport.com/1972-corvette-specifications/?utm_source=chatgpt.com "1972 Corvette Performance & Specifications"
[2]: https://autocatalogarchive.com/wp-content/uploads/2024/09/Chevrolet-Camaro-1972-USA.pdf?utm_source=chatgpt.com "Chevrolet Camaro (1972)"
[3]: https://www.automobile-catalog.com/make/chevrolet_europe/windstorm_captiva_europe/windstorm_captiva_eu/2007.html?utm_source=chatgpt.com "2007 Chevrolet (Europe) Captiva Series I 4WD full range ..."


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已补齐 Cruze I 剩余 7 个 Ktype。AIC 目录确认 `51391`、`8711`、`8771`、`13909` 属于 J300 四门车身，`10351`、`10352` 属于 J305 五门车身，且适用期跨越 Cruze I 外观改款，因此分别拆为 `prefl` 与 `facelift` 映射。([AIC德国汽车零部件][1])
* `56753` 为 2012 年开始的 J305 1.4 Turbo，直接关联已存在的改款后五门尺寸组，不重复输出该尺寸组。([AIC德国汽车零部件][2])
* 首次创建 Cruze I 改款前四门 Sedan 尺寸组，三维为 `4597 × 1788 × 1477 mm`，宽度为不含后视镜口径。([汽车目录档案][3])

## 当前批次进度

* READY 映射行：99
* 已闭合输入 Ktype：75
* PENDING 输入 Ktype：25
* 已确认且被引用尺寸组：50
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
51391_prefl	51391	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
51391_facelift	51391	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
8711_prefl	8711	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
8711_facelift	8711	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
8771_prefl	8771	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
8771_facelift	8771	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
10352_prefl	10352	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
10352_facelift	10352	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
10351_prefl	10351	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
10351_facelift	10351	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
13909_prefl	13909	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
13909_facelift	13909	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
56753	56753	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	4597	1788	1477	Chevrolet Cruze 2010 official brochure; Automobile-Catalog 2009 Chevrolet Cruze 1.6 specifications	https://autocatalogarchive.com/wp-content/uploads/2021/11/Chevrolet-Cruze-2010-IN.pdf;https://www.automobile-catalog.com/car/2009/1210010/chevrolet_cruze_1_6.html
```

## 下一步优先处理

* 闭合 Blazer S10 两个 Ktype，并处理 Bel Air、Celebrity 与 Caprice 传统乘用车簇；随后集中处理 C1500、Cheyenne、Colorado 的驾驶室和货斗物理分支。

推进信号：CONTINUE

[1]: https://aic-germany.de/en/product-catalogue/12873?utm_source=chatgpt.com "Product catalogue from AIC Germany"
[2]: https://www.aic-germany.de/en/product-catalogue/12960?utm_source=chatgpt.com "Product catalogue from AIC Germany"
[3]: https://autocatalogarchive.com/wp-content/uploads/2021/11/Chevrolet-Cruze-2010-IN.pdf?utm_source=chatgpt.com "Chevrolet-Cruze-2010-IN.pdf"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 `36473` 的 1973—1975 Chevrolet Bel Air 四门 Sedan。美国市场该阶段仅有四门 Sedan 与 Wagon；1974 年保险杠使长度增加，1975 年又更换车顶和前部外廓，因此拆成三个年款分支。([维基百科][1])
* 已闭合 Caprice II 的 `112859`、`125527` 和 `36834`。Sedan 按 1974、1975 年外廓分别建组；Coupe 按 1975、1976 年前部造型和长度变化拆分。([汽车目录档案][2])

## 当前批次进度

* READY 映射行：106
* 已闭合输入 Ktype：79
* PENDING 输入 Ktype：21
* 已确认且被引用尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
36473_1973	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1973-01	HIGH	1973款四门Sedan外廓。	READY
36473_1974	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1974-01	HIGH	1974款四门Sedan保险杠外廓。	READY
36473_1975	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1975-01	HIGH	1975款四门Sedan车顶及前部外廓。	READY
112859	112859	Sedan	Caprice II	B-body	4	EU-CHEVROLET-CAPRICE-II-SEDAN-1974-01	HIGH	1974款四门Sedan外廓。	READY
125527	125527	Sedan	Caprice II	B-body	4	EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	HIGH	1975款四门Sedan外廓。	READY
36834_1975	36834	Coupe	Caprice II	B-body	2	EU-CHEVROLET-CAPRICE-II-COUPE-1975-01	HIGH	1975款双门Coupe外廓。	READY
36834_1976	36834	Coupe	Caprice II	B-body	2	EU-CHEVROLET-CAPRICE-II-COUPE-1976-01	HIGH	1976款双门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1973-01	5636	2019	1384	Chevrolet 1973 Caprice/Impala/Bel Air official brochure;Automobile-Catalog 1973 Chevrolet Bel Air 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2021/01/1973-Chevrolet-Caprice-Impala-Bel-Air-v2.pdf;https://www.automobile-catalog.com/car/1973/115955/chevrolet_bel_air_4-door_sedan_350-4_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1974-01	5657	2019	1384	Chevrolet 1974 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1974 Chevrolet Bel Air 4-Door Sedan specifications	https://autocatalogarchive.com/wp-content/uploads/2025/09/Chevrolet-Caprice-Impala-1974-USA.pdf;https://www.automobile-catalog.com/car/1974/116705/chevrolet_bel_air_4-door_sedan_454-4_v-8_turbo-jet_hydra-matic.html
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1975-01	5659	2019	1384	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Bel Air 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117410/chevrolet_bel_air_4-door_sedan_350-4_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-SEDAN-1974-01	5657	2019	1384	Chevrolet 1974 Caprice Classic/Impala/Bel Air official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/09/Chevrolet-Caprice-Impala-1974-USA.pdf
EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	5659	2019	1384	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Caprice Classic 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117695/chevrolet_caprice_4-door_sedan_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-COUPE-1975-01	5659	2019	1364	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Caprice Classic Coupe specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117815/chevrolet_caprice_coupe_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-COUPE-1976-01	5662	2019	1364	Chevrolet 1976 Caprice Classic/Impala official brochure;Automobile-Catalog 1976 Chevrolet Caprice Classic Coupe specifications	https://xr793.com/wp-content/uploads/2017/07/1976-Chevroloet-Caprice-Classic-Impala.pdf;https://www.automobile-catalog.com/car/1976/207440/chevrolet_caprice_classic_coupe_400-4_v-8_turbo-jet_hydra-matic.html
```

## 下一步优先处理

* 集中闭合 `57239`、`52186` 的第三代 Caprice 年款分支，以及 Blazer S10 的两门、四门和前后期外廓；随后处理 C1500、Cheyenne、Colorado 皮卡驾驶室与货斗分支。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Chevrolet_Bel_Air?utm_source=chatgpt.com "Chevrolet Bel Air"
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/09/Chevrolet-Caprice-Impala-1974-USA.pdf?utm_source=chatgpt.com "1974 Chevrolet - Caprice Classic /Impala / Bel Air"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已闭合 `57239` 覆盖的 Caprice III 四门 Sedan。因外廓尺寸在 1977、1978、1980 和 1985 年分别发生变化，拆为 `1977`、`1978-1979`、`1980-1984`、`1985-1987` 四个稳定分支。主要变化包括宽度由 `1918 mm` 增至 `1930 mm`、随后调整为 `1913 mm`，1985 年起长度和宽度变为 `5405 × 1915 mm`。([汽车目录][1])
* 已闭合 `52186` 的 Caprice III 5.7 Coupe。1977 与 1978—1979 年款宽度分别为 `1918 mm` 和 `1930 mm`，因此拆为两个物理外廓分支。([汽车目录][2])

## 当前批次进度

* READY 映射行：112
* 已闭合输入 Ktype：81
* PENDING 输入 Ktype：19
* 已确认且被引用尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57239_1977	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	HIGH	1977款四门Sedan外廓。	READY
57239_1978-1979	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	HIGH	1978至1979款四门Sedan外廓。	READY
57239_1980-1984	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1980-1984-01	HIGH	1980至1984款四门Sedan外廓。	READY
57239_1985-1987	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1985-1987-01	HIGH	1985至1987款四门Sedan外廓。	READY
52186_1977	52186	Coupe	Caprice III	B-body	2	EU-CHEVROLET-CAPRICE-III-COUPE-1977-01	HIGH	1977款双门Coupe外廓。	READY
52186_1978-1979	52186	Coupe	Caprice III	B-body	2	EU-CHEVROLET-CAPRICE-III-COUPE-1978-1979-01	HIGH	1978至1979款双门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	5387	1918	1422	Automobile-Catalog 1977 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1977/208100/chevrolet_caprice_classic_sedan_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	5387	1930	1422	Automobile-Catalog 1979 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1979/208910/chevrolet_caprice_classic_sedan_4_1l_automatic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1980-1984-01	5387	1913	1420	Automobile-Catalog 1980 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1980/209465/chevrolet_caprice_classic_sedan_4_4l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1985-1987-01	5405	1915	1433	Automobile-Catalog 1985 Chevrolet Caprice Classic Sedan 5.0L specifications	https://www.automobile-catalog.com/car/1985/461825/chevrolet_caprice_classic_sedan_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-COUPE-1977-01	5387	1918	1405	Automobile-Catalog 1977 Chevrolet Caprice Classic Coupe 5.7 specifications	https://www.automobile-catalog.com/car/1977/208055/chevrolet_caprice_classic_coupe_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-COUPE-1978-1979-01	5387	1930	1405	Automobile-Catalog 1978 Chevrolet Caprice Classic Coupe 5.7 specifications	https://www.automobile-catalog.com/car/1978/208430/chevrolet_caprice_classic_coupe_350-4_v-8_automatic.html
```

## 下一步优先处理

* 集中闭合 Blazer S10 的两门、四门以及 1998 外观改款前后分支；随后处理 Celebrity，并进入 C1500、Cheyenne、Colorado 的驾驶室和货斗组合。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/208100/chevrolet_caprice_classic_sedan_350-4_v-8_hydra-matic.html?utm_source=chatgpt.com "1977 Chevrolet Caprice Classic Sedan 350-4 V-8 Hydra-Matic Specs Review (126.5 kW / 172 PS / 170 hp) (since October 1976 for North America )"
[2]: https://www.automobile-catalog.com/car/1977/208055/chevrolet_caprice_classic_coupe_350-4_v-8_hydra-matic.html?utm_source=chatgpt.com "1977 Chevrolet Caprice Classic Coupe 350-4 V-8 Hydra-Matic Specs Review (126.5 kW / 172 PS / 170 hp) (since October 1976 for North America )"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已闭合 `36934` 的 Celebrity I 四门 Sedan。该 Ktype 覆盖 1982—1986 年款：1982—1983 为 `4783 × 1748 × 1364 mm`，1984—1985 调整为 `4783 × 1760 × 1369 mm`，1986 高度进一步变为 `1374 mm`，因此拆为三个稳定物理分支。
* Blazer S10 两个 Ktype 的欧洲出口门数覆盖边界尚未完全闭合，本轮未创建猜测性映射或尺寸组。

## 当前批次进度

* READY 映射行：115
* 已闭合输入 Ktype：82
* PENDING 输入 Ktype：18
* 已确认且被引用尺寸组：66
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
36934_1982-1983	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1982-1983-01	HIGH	1982至1983款四门Sedan外廓。	READY
36934_1984-1985	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1984-1985-01	HIGH	1984至1985款四门Sedan外廓。	READY
36934_1986	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1986-01	HIGH	1986款四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CELEBRITY-I-SEDAN-1982-1983-01	4783	1748	1364	Chevrolet 1982 Celebrity official brochure;Automobile-Catalog 1983 Chevrolet Celebrity Sedan 2.8L specifications	https://xr793.com/wp-content/uploads/2017/07/1982-Chevrolet-Celebrity.pdf;https://www.automobile-catalog.com/car/1983/456335/chevrolet_celebrity_sedan_2_8l_v-6_automatic.html
EU-CHEVROLET-CELEBRITY-I-SEDAN-1984-1985-01	4783	1760	1369	Automobile-Catalog 1984 Chevrolet Celebrity Sedan 2.8L specifications;Chevrolet 1985 Celebrity official brochure	https://www.automobile-catalog.com/car/1984/456605/chevrolet_celebrity_sedan_2_8l_v-6_high_output_automatic.html;https://xr793.com/wp-content/uploads/2017/07/1985-Chevrolet-Celebrity.pdf
EU-CHEVROLET-CELEBRITY-I-SEDAN-1986-01	4783	1760	1374	Automobile-Catalog 1986 Chevrolet Celebrity Sedan 2.8L specifications	https://www.automobile-catalog.com/car/1986/457280/chevrolet_celebrity_sedan_2_8l_v-6_automatic.html
```

## 下一步优先处理

1. 闭合 `36537`、`57227` 对欧洲出口 Blazer S10 II 三门、五门车身及 1998 年外观更新边界。
2. 随后集中处理 C1500、Cheyenne 与 Colorado 的驾驶室、货斗和轴距分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已完成 12 个 Colorado Ktype 的驾驶室归属：`37001/37003/37004/37005/37007/37008` 为 Crew Cab，`37009/111737/111738` 为 Extended Cab，`111735/111739/111740` 为 Standard Cab；驱动形式按输入分别落入 2WD 或 4WD 外廓。([Refako][1])
* 首次闭合 Colorado I（GMT355）的 6 个驾驶室/驱动尺寸组。4WD 车型因轮眉及悬架外廓与对应 2WD 车型不同，分别建组；所有宽度均采用不含后视镜口径。

## 当前批次进度

* READY 映射行：127
* 已闭合输入 Ktype：94
* PENDING 输入 Ktype：6
* 已确认且被引用尺寸组：72
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
37001	37001	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37009	37009	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	HIGH	Extended Cab长货斗2WD外廓。	READY
111735	111735	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	HIGH	Standard Cab长货斗2WD外廓。	READY
37005	37005	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37003	37003	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
111737	111737	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	HIGH	Extended Cab长货斗2WD外廓。	READY
111739	111739	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	HIGH	Standard Cab长货斗2WD外廓。	READY
37007	37007	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37004	37004	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	HIGH	Crew Cab短货斗4WD外廓。	READY
111738	111738	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-4WD-01	HIGH	Extended Cab长货斗4WD外廓。	READY
111740	111740	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-4WD-01	HIGH	Standard Cab长货斗4WD外廓。	READY
37008	37008	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	HIGH	Crew Cab短货斗4WD外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	5260	1717	1656	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Crew Cab specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/crew-cab/features-specs/
EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	5260	1717	1648	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Extended Cab Base specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/extended-cab/st-100563864/features-specs/
EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	4887	1717	1648	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Regular Cab Work Truck specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/regular-cab/st-100563860/features-specs/
EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	5260	1742	1725	Chevrolet 2004 Colorado official brochure;Edmunds 2010 Chevrolet Colorado Crew Cab 4WD specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2010/crew-cab/features-specs/
EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-4WD-01	5260	1742	1717	Chevrolet 2004 Colorado official brochure;Edmunds 2010 Chevrolet Colorado Extended Cab 4WD specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2010/extended-cab/features-specs/
EU-CHEVROLET-COLORADO-I-STANDARD-CAB-4WD-01	4887	1742	1717	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Regular Cab 4WD Work Truck specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/st-100563861/features-specs/
```

## 下一步优先处理

* 仅剩 6 个 Ktype：先闭合 `36537`、`57227` 的 Blazer S10 II 门数及改款分支，再处理 `111501`、`111489` 的 C1500 和 `107586`、`107583` 的 Cheyenne 驾驶室/货斗组合。

推进信号：CONTINUE

[1]: https://www.refako.dk/vehicles/190111735?utm_source=chatgpt.com "CHEVROLET COLORADO Standard Cab Pickup 2.8 - Refako Autodele"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3101-3200_ktype_dimension_mapping_final.tsv
- left18448_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 最后 6 个 Ktype 已闭合：Blazer S10 按三门/五门和 1998 改款前后拆分；C1500 Extended Cab 与 Standard Cab 分别覆盖短货斗、长货斗；Cheyenne 分别关联 Crew Cab 与 Standard Cab 短货斗 4WD 外廓。1996 C/K 资料与 KBB 条目分别覆盖 Extended/Regular Cab 及短、长货斗配置。([Edmunds][1])
* Cheyenne 资料明确包含单排驾驶室与 Crew Cab；对应 Crew Cab 短货斗尺寸亦由 GM 规格资料交叉闭合。([汽车列表][2])
* 已完成机械检查：固定表头正确、137 个 `id` 唯一、82 个 `DIMENSION_GROUP_ID` 唯一、100 个输入 Ktype 全覆盖、映射引用完全闭合、无孤立尺寸组、尺寸与来源字段均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：137
* PENDING：0
* DIMENSION_GROUP：82
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18534	18534	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	HIGH	T200五门掀背外廓。	READY
36473_1973	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1973-01	HIGH	1973款四门Sedan外廓。	READY
36473_1974	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1974-01	HIGH	1974款四门Sedan保险杠外廓。	READY
36473_1975	36473	Sedan	Bel Air VII	B-body	4	EU-CHEVROLET-BEL-AIR-VII-SEDAN-1975-01	HIGH	1975款四门Sedan车顶及前部外廓。	READY
36537_prefl	36537	SUV	Blazer S10 II	GMT330	3	EU-CHEVROLET-BLAZER-S10-II-SUV-3D-PREFL-01	MEDIUM	三门车身，1998改款前外廓。	READY
36537_facelift	36537	SUV	Blazer S10 II	GMT330	3	EU-CHEVROLET-BLAZER-S10-II-SUV-3D-FACELIFT-01	MEDIUM	三门车身，1998改款后外廓。	READY
57227_prefl	57227	SUV	Blazer S10 II	GMT330	5	EU-CHEVROLET-BLAZER-S10-II-SUV-5D-PREFL-01	MEDIUM	五门车身，1998改款前外廓。	READY
57227_facelift	57227	SUV	Blazer S10 II	GMT330	5	EU-CHEVROLET-BLAZER-S10-II-SUV-5D-FACELIFT-01	MEDIUM	五门车身，1998改款后外廓。	READY
111501_swb	111501	Pickup	C/K IV	GMT400	2	EU-CHEVROLET-C1500-GMT400-EXTENDED-CAB-SWB-2WD-01	MEDIUM	Extended Cab短货斗外廓。	READY
111501_lwb	111501	Pickup	C/K IV	GMT400	2	EU-CHEVROLET-C1500-GMT400-EXTENDED-CAB-LWB-2WD-01	MEDIUM	Extended Cab长货斗外廓。	READY
111489_swb	111489	Pickup	C/K IV	GMT400	2	EU-CHEVROLET-C1500-GMT400-STANDARD-CAB-SWB-2WD-01	MEDIUM	Standard Cab短货斗外廓。	READY
111489_lwb	111489	Pickup	C/K IV	GMT400	2	EU-CHEVROLET-C1500-GMT400-STANDARD-CAB-LWB-2WD-01	MEDIUM	Standard Cab长货斗外廓。	READY
36807	36807	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-BASE-PREFL-01	HIGH	2.8基础Coupe外廓。	READY
36813_prefl	36813	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-RS-PREFL-01	HIGH	1990款RS Coupe外廓。	READY
36813_facelift	36813	Coupe	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-COUPE-RS-FACELIFT-01	HIGH	1991至1992款RS Coupe外廓。	READY
9974_prefl	9974	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9974_facelift	9974	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9996_prefl	9996	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9996_facelift	9996	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
56319_prefl	56319	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
56319_facelift	56319	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
57405_prefl	57405	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
57405_facelift	57405	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
11169	11169	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	HIGH	1998至2002款Coupe外廓。	READY
11170	11170	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	HIGH	1998至2002款Coupe外廓。	READY
112828_1972	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1972-01	HIGH	1972款Coupe外廓。	READY
112828_1973	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1973-01	HIGH	1973款Coupe外廓。	READY
112828_1974	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1974-01	HIGH	1974款保险杠外廓。	READY
112828_1975	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1975-01	HIGH	1975款环绕式后窗外廓。	READY
112828_1976	112828	Coupe	Camaro II	F-body	2	EU-CHEVROLET-CAMARO-II-COUPE-1976-01	HIGH	1976款Coupe外廓。	READY
9975_prefl	9975	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9975_facelift	9975	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9976_prefl	9976	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Coupe外廓。	READY
9976_facelift	9976	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Coupe外廓。	READY
9977_prefl	9977	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9977_facelift	9977	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
9978_prefl	9978	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	MEDIUM	同一Ktype覆盖改款前Convertible外廓。	READY
9978_facelift	9978	Convertible	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后Convertible外廓。	READY
116322	116322	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
119806	119806	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
120496	120496	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
120497	120497	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
121704	121704	Coupe	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	Alpha双门Coupe外廓。	READY
121706	121706	Convertible	Camaro VI	Alpha	2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	Alpha双门Convertible外廓。	READY
11919	11919	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	HIGH	3.4 V6改款前Coupe外廓。	READY
11171	11171	Convertible	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-CONVERTIBLE-FACELIFT-01	HIGH	1998至2002款Convertible外廓。	READY
11920	11920	Coupe	Camaro IV	F-body	2	EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	HIGH	5.7 LT1改款前Coupe外廓。	READY
36796	36796	Convertible	Camaro III	F-body	2	EU-CHEVROLET-CAMARO-III-CONVERTIBLE-Z28-PREFL-01	HIGH	Z28 Convertible外廓。	READY
54446_prefl	54446	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	MEDIUM	ZL1改款前外廓。	READY
54446_facelift	54446	Coupe	Camaro V	Zeta	2	EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	MEDIUM	ZL1改款后外廓。	READY
57239_1977	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	HIGH	1977款四门Sedan外廓。	READY
57239_1978-1979	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	HIGH	1978至1979款四门Sedan外廓。	READY
57239_1980-1984	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1980-1984-01	HIGH	1980至1984款四门Sedan外廓。	READY
57239_1985-1987	57239	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-1985-1987-01	HIGH	1985至1987款四门Sedan外廓。	READY
52186_1977	52186	Coupe	Caprice III	B-body	2	EU-CHEVROLET-CAPRICE-III-COUPE-1977-01	HIGH	1977款双门Coupe外廓。	READY
52186_1978-1979	52186	Coupe	Caprice III	B-body	2	EU-CHEVROLET-CAPRICE-III-COUPE-1978-1979-01	HIGH	1978至1979款双门Coupe外廓。	READY
125527	125527	Sedan	Caprice II	B-body	4	EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	HIGH	1975款四门Sedan外廓。	READY
36834_1975	36834	Coupe	Caprice II	B-body	2	EU-CHEVROLET-CAPRICE-II-COUPE-1975-01	HIGH	1975款双门Coupe外廓。	READY
36834_1976	36834	Coupe	Caprice II	B-body	2	EU-CHEVROLET-CAPRICE-II-COUPE-1976-01	HIGH	1976款双门Coupe外廓。	READY
112859	112859	Sedan	Caprice II	B-body	4	EU-CHEVROLET-CAPRICE-II-SEDAN-1974-01	HIGH	1974款四门Sedan外廓。	READY
10032	10032	SUV	Captiva I	C140	5	EU-CHEVROLET-CAPTIVA-I-SUV-FACELIFT-01	HIGH	C140改款后五门SUV外廓。	READY
34972	34972	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	MEDIUM	2.4 LPG对应C100外廓。	READY
34973	34973	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	C100改款前五门SUV外廓。	READY
142562	142562	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	商用登记不改变C100外部车身。	READY
142561	142561	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	HIGH	商用登记不改变C100外部车身。	READY
36934_1982-1983	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1982-1983-01	HIGH	1982至1983款四门Sedan外廓。	READY
36934_1984-1985	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1984-1985-01	HIGH	1984至1985款四门Sedan外廓。	READY
36934_1986	36934	Sedan	Celebrity I	A-body	4	EU-CHEVROLET-CELEBRITY-I-SEDAN-1986-01	HIGH	1986款四门Sedan外廓。	READY
107586	107586	Pickup	Cheyenne III	K2XX	4	EU-CHEVROLET-CHEYENNE-III-CREW-CAB-SHORTBOX-4WD-01	HIGH	双排驾驶室短货斗4WD外廓。	READY
107583	107583	Pickup	Cheyenne III	K2XX	2	EU-CHEVROLET-CHEYENNE-III-STANDARD-CAB-SHORTBOX-4WD-01	MEDIUM	单排驾驶室短货斗4WD外廓。	READY
37001	37001	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37009	37009	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	HIGH	Extended Cab长货斗2WD外廓。	READY
111735	111735	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	HIGH	Standard Cab长货斗2WD外廓。	READY
37005	37005	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37003	37003	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
111737	111737	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	HIGH	Extended Cab长货斗2WD外廓。	READY
111739	111739	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	HIGH	Standard Cab长货斗2WD外廓。	READY
37007	37007	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	HIGH	Crew Cab短货斗2WD外廓。	READY
37004	37004	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	HIGH	Crew Cab短货斗4WD外廓。	READY
111738	111738	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-4WD-01	HIGH	Extended Cab长货斗4WD外廓。	READY
111740	111740	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-STANDARD-CAB-4WD-01	HIGH	Standard Cab长货斗4WD外廓。	READY
37008	37008	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	HIGH	Crew Cab短货斗4WD外廓。	READY
11168	11168	Convertible	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	HIGH	C5双门Convertible外廓。	READY
37049	37049	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1976-1977-01	HIGH	1976至1977款C3 Coupe外廓。	READY
111827	111827	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1978-01	HIGH	1978款C3 Coupe外廓。	READY
111831	111831	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	改款前C4 Coupe外廓。	READY
111833	111833	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	改款前C4 Coupe外廓。	READY
111834_prefl	111834	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	MEDIUM	同一Ktype覆盖1991改款前外廓。	READY
111834_facelift	111834	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-FACELIFT-01	MEDIUM	同一Ktype覆盖1991改款后外廓。	READY
111836	111836	Convertible	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	HIGH	C5双门Convertible外廓。	READY
111837	111837	Coupe	Corvette C5		2	EU-CHEVROLET-CORVETTE-C5-COUPE-01	HIGH	C5双门Coupe外廓。	READY
125500	125500	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	HIGH	1975款C3 Coupe外廓。	READY
125504	125504	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	1990款标准C4 Coupe外廓。	READY
125505	125505	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	HIGH	1990款标准C4 Coupe外廓。	READY
17835	17835	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-01	HIGH	C6标准Coupe外廓。	READY
105639	105639	Coupe	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-COUPE-STINGRAY-01	HIGH	C7 Stingray双门Coupe外廓。	READY
105640	105640	Convertible	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-STINGRAY-01	HIGH	C7 Stingray双门Convertible外廓。	READY
146989	146989	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-STINGRAY-01	HIGH	C8 Stingray双门Coupe外廓。	READY
146990	146990	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-STINGRAY-01	HIGH	C8 Stingray双门Convertible外廓。	READY
112573_1972	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1972-01	HIGH	1972款C3 Coupe外廓。	READY
112573_1973	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1973-01	HIGH	1973款C3 Coupe外廓。	READY
112573_1974	112573	Coupe	Corvette C3		2	EU-CHEVROLET-CORVETTE-C3-COUPE-1974-01	HIGH	1974款C3 Coupe外廓。	READY
37057	37057	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-ZR1-01	HIGH	C4 ZR-1宽体Coupe外廓。	READY
802180	802180	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-ERAY-01	HIGH	C8 E-Ray宽体Coupe外廓。	READY
802181	802181	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-ERAY-01	HIGH	C8 E-Ray宽体Convertible外廓。	READY
107980	107980	Convertible	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-Z06-01	HIGH	C7 Z06宽体Convertible外廓。	READY
107981	107981	Coupe	Corvette C7		2	EU-CHEVROLET-CORVETTE-C7-COUPE-Z06-01	HIGH	C7 Z06宽体Coupe外廓。	READY
100274	100274	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	HIGH	输入Cabriolet与量产ZR1车身冲突，按Coupe外廓。	READY
150627	150627	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	HIGH	C8 Z06宽体Convertible外廓。	READY
150628	150628	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	HIGH	C8 Z06宽体Coupe外廓。	READY
156315	156315	Coupe	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	HIGH	C8 Z06宽体Coupe外廓。	READY
800931	800931	Convertible	Corvette C8		2	EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	HIGH	C8 Z06宽体Convertible外廓。	READY
56759	56759	Coupe	Corvette C6		2	EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	HIGH	输入Cabriolet与量产Z06车身冲突，按Coupe外廓。	READY
51391_prefl	51391	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
51391_facelift	51391	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
55461	55461	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	HIGH	改款后J300四门外廓。	READY
55465	55465	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
55475	55475	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
55798	55798	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
56753	56753	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
8711_prefl	8711	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
8711_facelift	8711	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
8771_prefl	8771	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
8771_facelift	8771	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
10352_prefl	10352	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
10352_facelift	10352	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
55799	55799	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
57414	57414	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	2012年末起型式，按改款后J305五门外廓。	READY
57419	57419	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
10351_prefl	10351	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
10351_facelift	10351	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
55800	55800	Wagon	Cruze I	J308	5	EU-CHEVROLET-CRUZE-I-WAGON-01	HIGH	J308五门旅行车外廓。	READY
13909_prefl	13909	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	MEDIUM	同一Ktype覆盖改款前J300四门外廓。	READY
13909_facelift	13909	Sedan	Cruze I	J300	4	EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J300四门外廓。	READY
13914_prefl	13914	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	MEDIUM	同一Ktype覆盖改款前J305五门外廓。	READY
13914_facelift	13914	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	MEDIUM	同一Ktype覆盖改款后J305五门外廓。	READY
35426	35426	Hatchback	Cruze I	J305	5	EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	HIGH	改款后J305五门外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_3101-3200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	3880	1670	1495	Auto-Data Chevrolet Kalos T200 specifications;Automobile-Catalog 2005 Chevrolet Aveo 5-Door specifications	https://www.auto-data.net/en/chevrolet-kalos-model-3938;https://www.automobile-catalog.com/car/2005/478595/chevrolet_aveo_5-door.html
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1973-01	5636	2019	1384	Chevrolet 1973 Caprice/Impala/Bel Air official brochure;Automobile-Catalog 1973 Chevrolet Bel Air 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2021/01/1973-Chevrolet-Caprice-Impala-Bel-Air-v2.pdf;https://www.automobile-catalog.com/car/1973/115955/chevrolet_bel_air_4-door_sedan_350-4_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1974-01	5657	2019	1384	Chevrolet 1974 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1974 Chevrolet Bel Air 4-Door Sedan specifications	https://autocatalogarchive.com/wp-content/uploads/2025/09/Chevrolet-Caprice-Impala-1974-USA.pdf;https://www.automobile-catalog.com/car/1974/116705/chevrolet_bel_air_4-door_sedan_454-4_v-8_turbo-jet_hydra-matic.html
EU-CHEVROLET-BEL-AIR-VII-SEDAN-1975-01	5659	2019	1384	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Bel Air 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117410/chevrolet_bel_air_4-door_sedan_350-4_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-BLAZER-S10-II-SUV-3D-PREFL-01	4437	1722	1699	GM Heritage 1995 Chevrolet Blazer vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-Blazer.pdf
EU-CHEVROLET-BLAZER-S10-II-SUV-3D-FACELIFT-01	4437	1736	1770	Automobile-Catalog 1998 Chevrolet Blazer 2-Door 4WD specifications	https://www.automobile-catalog.com/car/1998/483860/chevrolet_blazer_2-door_4wd_automatic.html
EU-CHEVROLET-BLAZER-S10-II-SUV-5D-PREFL-01	4602	1722	1702	GM Heritage 1995 Chevrolet Blazer vehicle information kit	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-Blazer.pdf
EU-CHEVROLET-BLAZER-S10-II-SUV-5D-FACELIFT-01	4656	1722	1633	Auto-Data Chevrolet Blazer II 4-door facelift 1998 specifications	https://www.auto-data.net/en/chevrolet-blazer-ii-4-door-facelift-1998-generation-8282
EU-CHEVROLET-C1500-GMT400-EXTENDED-CAB-SWB-2WD-01	5548	1951	1788	Kelley Blue Book 1996 Chevrolet 1500 Extended Cab Short Bed specifications	https://www.kbb.com/chevrolet/1500-extended-cab/1996/short-bed/
EU-CHEVROLET-C1500-GMT400-EXTENDED-CAB-LWB-2WD-01	6022	1951	1788	Chevrolet 1996 C/K official brochure;Edmunds 1996 Chevrolet C/K 1500 Extended Cab specifications	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf;https://www.edmunds.com/chevrolet/ck-1500-series/1996/extended-cab/features-specs/
EU-CHEVROLET-C1500-GMT400-STANDARD-CAB-SWB-2WD-01	4940	1951	1788	Edmunds 1996 Chevrolet C/K 1500 Series Regular Cab specifications	https://www.edmunds.com/chevrolet/ck-1500-series/1996/features-specs/
EU-CHEVROLET-C1500-GMT400-STANDARD-CAB-LWB-2WD-01	5413	1951	1788	Edmunds 1996 Chevrolet C/K 1500 Series Regular Cab Long Bed specifications	https://www.edmunds.com/chevrolet/ck-1500-series/1996/regular-cab/st-14005/features-specs/
EU-CHEVROLET-CAMARO-III-COUPE-BASE-PREFL-01	4775	1849	1270	Automobile-Catalog 1985 Chevrolet Camaro Sport Coupe specifications	https://www.automobile-catalog.com/car/1985/458690/chevrolet_camaro_sport_coupe_2_8l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-III-COUPE-RS-PREFL-01	4877	1849	1278	Automobile-Catalog 1990 Chevrolet Camaro RS specifications	https://www.automobile-catalog.com/car/1990/459935/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-III-COUPE-RS-FACELIFT-01	4892	1839	1280	Automobile-Catalog 1991 Chevrolet Camaro RS specifications	https://www.automobile-catalog.com/car/1991/460130/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-V-COUPE-PREFL-01	4836	1918	1376	General Motors 2011 Camaro Coupe and Convertible specifications	https://www.prnewswire.com/news-releases/new-camaro-convertible-blends-top-down-driving-fun-with-precise-engineering-108379814.html
EU-CHEVROLET-CAMARO-V-COUPE-FACELIFT-01	4841	1918	1376	GM Canada 2014 Camaro Quick Facts;Chevrolet 2015 Camaro ZL1 official specifications	https://media.gm.ca/content/dam/Media/microsites/product/canada_retiree/Documents/en/Products/Pamphlets/2014/2014_Chevrolet_Camaro.pdf;https://autoinfo.jp/release/MY15_Camaro_ZL1.pdf
EU-CHEVROLET-CAMARO-V-CONVERTIBLE-PREFL-01	4836	1918	1389	General Motors 2011 Camaro Coupe and Convertible specifications	https://www.prnewswire.com/news-releases/new-camaro-convertible-blends-top-down-driving-fun-with-precise-engineering-108379814.html
EU-CHEVROLET-CAMARO-V-CONVERTIBLE-FACELIFT-01	4841	1918	1389	GM Canada 2014 Camaro Quick Facts;Chevrolet 2015 Camaro ZL1 official specifications	https://media.gm.ca/content/dam/Media/microsites/product/canada_retiree/Documents/en/Products/Pamphlets/2014/2014_Chevrolet_Camaro.pdf;https://autoinfo.jp/release/MY15_Camaro_ZL1.pdf
EU-CHEVROLET-CAMARO-IV-COUPE-FACELIFT-01	4915	1882	1303	GM Heritage 1998 Chevrolet Camaro vehicle information kit;Automobile-Catalog 1998 Camaro specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Camaro.pdf;https://www.automobile-catalog.com/car/1998/473135/chevrolet_camaro_z28_ss.html
EU-CHEVROLET-CAMARO-II-COUPE-1972-01	4775	1890	1247	Chevrolet 1972 Camaro official brochure;Automobile-Catalog 1972 Camaro SS specifications	https://autocatalogarchive.com/wp-content/uploads/2024/09/Chevrolet-Camaro-1972-USA.pdf;https://www.automobile-catalog.com/car/1972/101480/chevrolet_camaro_ss_396.html
EU-CHEVROLET-CAMARO-II-COUPE-1973-01	4785	1890	1247	Chevrolet 1973 Camaro official brochure;Automobile-Catalog 1973 Camaro specifications	https://autocatalogarchive.com/wp-content/uploads/2016/07/Chevrolet-Camaro-1973.pdf;https://www.automobile-catalog.com/make/chevrolet_usa/camaro_2gen/camaro_2gen_lt/1973.html
EU-CHEVROLET-CAMARO-II-COUPE-1974-01	4963	1890	1247	Chevrolet 1974 Camaro official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/09/Chevrolet-Camaro-1974-USA-.pdf
EU-CHEVROLET-CAMARO-II-COUPE-1975-01	4963	1890	1247	Chevrolet 1975 Camaro official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/10/Chevrolet-Camaro-1975-USA.pdf
EU-CHEVROLET-CAMARO-II-COUPE-1976-01	4963	1890	1250	Chevrolet 1976 Camaro official brochure;Automobile-Catalog 1976 Camaro specifications	https://autocatalogarchive.com/wp-content/uploads/2024/10/Chevrolet-Camaro-1976-USA.pdf;https://www.automobile-catalog.com/car/1976/205475/chevrolet_camaro_type_lt_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAMARO-VI-COUPE-01	4783	1897	1349	Chevrolet 2019 Camaro official catalog;Car and Driver 2016 Camaro Coupe specifications	https://dealerinspire-brochure.s3.amazonaws.com/1785.pdf;https://www.caranddriver.com/chevrolet/camaro/specs/2016/chevrolet_camaro_chevrolet-camaro-ss-coupe_2016
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4783	1897	1344	Chevrolet 2019 Camaro official catalog;Car and Driver 2016 Camaro Convertible specifications	https://dealerinspire-brochure.s3.amazonaws.com/1785.pdf;https://www.caranddriver.com/chevrolet/camaro/specs/2016/chevrolet_camaro_chevrolet-camaro-ss-convertible_2016
EU-CHEVROLET-CAMARO-IV-COUPE-PREFL-01	4907	1882	1303	GM Heritage 1993 Chevrolet Camaro vehicle information kit;Automobile-Catalog 1995 Camaro specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1993-Chevrolet-Camaro.pdf;https://www.automobile-catalog.com/car/1995/1503620/chevrolet_camaro_z28.html
EU-CHEVROLET-CAMARO-IV-CONVERTIBLE-FACELIFT-01	4915	1882	1321	GM Heritage 1998 Chevrolet Camaro vehicle information kit;Edmunds 1998 Camaro Convertible specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Camaro.pdf;https://www.edmunds.com/chevrolet/camaro/1998/convertible/features-specs/
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-Z28-PREFL-01	4877	1849	1278	Automobile-Catalog 1987 Chevrolet Camaro Z28 Convertible specifications	https://www.automobile-catalog.com/car/1987/459290/chevrolet_camaro_z28_convertible_5_0l_v-8.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1977-01	5387	1918	1422	Automobile-Catalog 1977 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1977/208100/chevrolet_caprice_classic_sedan_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1978-1979-01	5387	1930	1422	Automobile-Catalog 1979 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1979/208910/chevrolet_caprice_classic_sedan_4_1l_automatic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1980-1984-01	5387	1913	1420	Automobile-Catalog 1980 Chevrolet Caprice Classic Sedan specifications	https://www.automobile-catalog.com/car/1980/209465/chevrolet_caprice_classic_sedan_4_4l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-III-SEDAN-1985-1987-01	5405	1915	1433	Automobile-Catalog 1985 Chevrolet Caprice Classic Sedan 5.0L specifications	https://www.automobile-catalog.com/car/1985/461825/chevrolet_caprice_classic_sedan_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-COUPE-1977-01	5387	1918	1405	Automobile-Catalog 1977 Chevrolet Caprice Classic Coupe 5.7 specifications	https://www.automobile-catalog.com/car/1977/208055/chevrolet_caprice_classic_coupe_350-4_v-8_hydra-matic.html
EU-CHEVROLET-CAPRICE-III-COUPE-1978-1979-01	5387	1930	1405	Automobile-Catalog 1978 Chevrolet Caprice Classic Coupe 5.7 specifications	https://www.automobile-catalog.com/car/1978/208430/chevrolet_caprice_classic_coupe_350-4_v-8_automatic.html
EU-CHEVROLET-CAPRICE-II-SEDAN-1975-01	5659	2019	1384	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Caprice Classic 4-Door Sedan specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117695/chevrolet_caprice_4-door_sedan_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-COUPE-1975-01	5659	2019	1364	Chevrolet 1975 Caprice Classic/Impala/Bel Air official brochure;Automobile-Catalog 1975 Chevrolet Caprice Classic Coupe specifications	https://xr793.com/wp-content/uploads/2017/07/1975-Chevrolet-Caprice-Impala-Bel-Air.pdf;https://www.automobile-catalog.com/car/1975/117815/chevrolet_caprice_coupe_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-COUPE-1976-01	5662	2019	1364	Chevrolet 1976 Caprice Classic/Impala official brochure;Automobile-Catalog 1976 Chevrolet Caprice Classic Coupe specifications	https://xr793.com/wp-content/uploads/2017/07/1976-Chevroloet-Caprice-Classic-Impala.pdf;https://www.automobile-catalog.com/car/1976/207440/chevrolet_caprice_classic_coupe_400-4_v-8_turbo-jet_hydra-matic.html
EU-CHEVROLET-CAPRICE-II-SEDAN-1974-01	5657	2019	1384	Chevrolet 1974 Caprice Classic/Impala/Bel Air official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/09/Chevrolet-Caprice-Impala-1974-USA.pdf
EU-CHEVROLET-CAPTIVA-I-SUV-FACELIFT-01	4673	1849	1727	Chevrolet UK 2014 Captiva official specifications	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Captiva-UK.pdf
EU-CHEVROLET-CAPTIVA-I-SUV-PREFL-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Europe Captiva specifications;Auto-Data Chevrolet Captiva I specifications	https://www.automobile-catalog.com/make/chevrolet_europe/windstorm_captiva_europe/windstorm_captiva_eu/2007.html;https://www.auto-data.net/en/chevrolet-captiva-model-1623
EU-CHEVROLET-CELEBRITY-I-SEDAN-1982-1983-01	4783	1748	1364	Chevrolet 1982 Celebrity official brochure;Automobile-Catalog 1983 Chevrolet Celebrity Sedan 2.8L specifications	https://xr793.com/wp-content/uploads/2017/07/1982-Chevrolet-Celebrity.pdf;https://www.automobile-catalog.com/car/1983/456335/chevrolet_celebrity_sedan_2_8l_v-6_automatic.html
EU-CHEVROLET-CELEBRITY-I-SEDAN-1984-1985-01	4783	1760	1369	Automobile-Catalog 1984 Chevrolet Celebrity Sedan 2.8L specifications;Chevrolet 1985 Celebrity official brochure	https://www.automobile-catalog.com/car/1984/456605/chevrolet_celebrity_sedan_2_8l_v-6_high_output_automatic.html;https://xr793.com/wp-content/uploads/2017/07/1985-Chevrolet-Celebrity.pdf
EU-CHEVROLET-CELEBRITY-I-SEDAN-1986-01	4783	1760	1374	Automobile-Catalog 1986 Chevrolet Celebrity Sedan 2.8L specifications	https://www.automobile-catalog.com/car/1986/457280/chevrolet_celebrity_sedan_2_8l_v-6_automatic.html
EU-CHEVROLET-CHEYENNE-III-CREW-CAB-SHORTBOX-4WD-01	5847	2032	1872	Lista de Carros Chevrolet Cheyenne 2015 dimensions;Automobile-Catalog 2014 Chevrolet Silverado 1500 Crew Cab Short Box 4x4 6.2L specifications	https://www.listadecarros.com/chevrolet/chevrolet-cheyenne-2015-capacidad-lujo-y-elegancia/;https://www.automobile-catalog.com/car/2014/3077300/chevrolet_silverado_1500_crew_cab_short_box_4x4_6_2-liter_v-8.html
EU-CHEVROLET-CHEYENNE-III-STANDARD-CAB-SHORTBOX-4WD-01	5222	2029	1869	Lista de Carros Chevrolet Cheyenne 2015 dimensions	https://www.listadecarros.com/chevrolet/chevrolet-cheyenne-2015-capacidad-lujo-y-elegancia/
EU-CHEVROLET-COLORADO-I-CREW-CAB-2WD-01	5260	1717	1656	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Crew Cab specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/crew-cab/features-specs/
EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-2WD-01	5260	1717	1648	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Extended Cab Base specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/extended-cab/st-100563864/features-specs/
EU-CHEVROLET-COLORADO-I-STANDARD-CAB-2WD-01	4887	1717	1648	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Regular Cab Work Truck specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/regular-cab/st-100563860/features-specs/
EU-CHEVROLET-COLORADO-I-CREW-CAB-4WD-01	5260	1742	1725	Chevrolet 2004 Colorado official brochure;Edmunds 2010 Chevrolet Colorado Crew Cab 4WD specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2010/crew-cab/features-specs/
EU-CHEVROLET-COLORADO-I-EXTENDED-CAB-4WD-01	5260	1742	1717	Chevrolet 2004 Colorado official brochure;Edmunds 2010 Chevrolet Colorado Extended Cab 4WD specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2010/extended-cab/features-specs/
EU-CHEVROLET-COLORADO-I-STANDARD-CAB-4WD-01	4887	1742	1717	Chevrolet 2004 Colorado official brochure;Edmunds 2006 Chevrolet Colorado Regular Cab 4WD Work Truck specifications	https://www.auto-brochures.com/makes/Chevrolet/Colorado/Chevrolet_US%20Colorado_2004.pdf;https://www.edmunds.com/chevrolet/colorado/2006/st-100563861/features-specs/
EU-CHEVROLET-CORVETTE-C5-CONVERTIBLE-01	4564	1869	1214	Edmunds 2004 Chevrolet Corvette Convertible specifications	https://www.edmunds.com/chevrolet/corvette/2004/convertible/features-specs/
EU-CHEVROLET-CORVETTE-C3-COUPE-1976-1977-01	4704	1753	1219	GM Heritage 1976 Chevrolet Corvette vehicle information kit;GM Heritage 1977 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1976-Chevrolet-Corvette.pdf;https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1977-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C3-COUPE-1978-01	4704	1753	1219	GM Heritage 1978 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1978-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C4-COUPE-PREFL-01	4483	1803	1186	Automobile-Catalog 1984 Chevrolet Corvette specifications;Chevrolet 1989 Corvette brochure	https://www.automobile-catalog.com/car/1984/29570/chevrolet_corvette.html;https://autocatalogarchive.com/wp-content/uploads/2016/07/Chevrolet-Corvette-1989-.pdf
EU-CHEVROLET-CORVETTE-C4-COUPE-FACELIFT-01	4483	1803	1186	GM Heritage 1991 Chevrolet Corvette vehicle information kit;Corvsport 1991 Corvette specifications	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1991-Chevrolet-Corvette.pdf;https://www.corvsport.com/1991-corvette-specifications/
EU-CHEVROLET-CORVETTE-C5-COUPE-01	4564	1869	1212	Edmunds 2004 Chevrolet Corvette Coupe specifications	https://www.edmunds.com/chevrolet/corvette/2004/coupe/features-specs/
EU-CHEVROLET-CORVETTE-C3-COUPE-1975-01	4704	1753	1222	GM Heritage 1975 Chevrolet Corvette vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1975-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C6-COUPE-01	4435	1844	1247	Chevrolet 2013 Corvette official order guide	https://www.corvetteactioncenter.com/specs/c6/2013/2013_Corvette_Order_Guide.pdf
EU-CHEVROLET-CORVETTE-C7-COUPE-STINGRAY-01	4492	1872	1239	Chevrolet Corvette Stingray official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-Technical-Data_en.pdf
EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-STINGRAY-01	4492	1872	1243	Chevrolet Corvette Stingray official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-Technical-Data_en.pdf
EU-CHEVROLET-CORVETTE-C8-COUPE-STINGRAY-01	4634	1934	1235	Chevrolet Corvette Stingray official European technical specifications;Edmunds 2022 Corvette Coupe specifications	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-TechSpecs_EN.pdf;https://www.edmunds.com/chevrolet/corvette/2022/coupe/features-specs/
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-STINGRAY-01	4634	1934	1234	Chevrolet Corvette Stingray official European technical specifications;Edmunds 2022 Corvette Convertible specifications	https://media.chevrolet.com/content/dam/Media/documents/INTL/chevrolet/tech-data/corvette-stingray/Chevrolet-Corvette-Stingray-TechSpecs_EN.pdf;https://www.edmunds.com/chevrolet/corvette/2022/convertible/st-401899994/features-specs/
EU-CHEVROLET-CORVETTE-C3-COUPE-1972-01	4636	1753	1214	Chevrolet 1972 Corvette official brochure;Corvsport 1972 Corvette specifications	https://xr793.com/wp-content/uploads/2017/07/1972-Chevrolet-Corvette.pdf;https://www.corvsport.com/1972-corvette-specifications/
EU-CHEVROLET-CORVETTE-C3-COUPE-1973-01	4691	1753	1212	Chevrolet 1973 Corvette official brochure	https://xr793.com/wp-content/uploads/2017/07/1973-Chevrolet-Corvette.pdf
EU-CHEVROLET-CORVETTE-C3-COUPE-1974-01	4712	1753	1214	Chevrolet 1974 Corvette official brochure;Carfolio 1974 Corvette specifications	https://autocatalogarchive.com/wp-content/uploads/2018/02/Chevrolet-Corvette-1974-USA.pdf;https://www.carfolio.com/chevrolet-corvette-stingray-90013
EU-CHEVROLET-CORVETTE-C4-COUPE-ZR1-01	4506	1880	1189	Automobile-Catalog 1990 Chevrolet Corvette ZR-1 specifications	https://www.automobile-catalog.com/car/1990/463655/chevrolet_corvette_zr-1.html
EU-CHEVROLET-CORVETTE-C8-COUPE-ERAY-01	4734	2024	1237	Chevrolet Europe Corvette E-Ray official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_E-Ray_Specifications.pdf
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-ERAY-01	4734	2024	1236	Chevrolet Europe Corvette E-Ray official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_E-Ray_Specifications.pdf
EU-CHEVROLET-CORVETTE-C7-CONVERTIBLE-Z06-01	4514	1965	1243	Chevrolet Corvette Z06 official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/corvette-z06/Tech-Data-Chevrolet-Corvette-Z06.pdf
EU-CHEVROLET-CORVETTE-C7-COUPE-Z06-01	4514	1965	1239	Chevrolet Corvette Z06 official technical data	https://media.gm.com/content/dam/Media/documents/INTL/chevrolet/2019/vehicles/corvette-z06/Tech-Data-Chevrolet-Corvette-Z06.pdf
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4476	1928	1244	Automobile-Catalog 2009 Chevrolet Corvette ZR1 specifications	https://www.automobile-catalog.com/car/2009/479435/chevrolet_corvette_zr1.html
EU-CHEVROLET-CORVETTE-C8-CONVERTIBLE-Z06-01	4734	2024	1236	Chevrolet Europe Corvette Z06 official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_Z06_Specifications_2025.pdf
EU-CHEVROLET-CORVETTE-C8-COUPE-Z06-01	4734	2024	1237	Chevrolet Europe Corvette Z06 official specifications	https://www.chevroleteurope.com/content/dam/chevrolet/eu/master/en/index/share-assets/pdf/specs/Chevrolet_Corvette_Z06_Specifications_2025.pdf
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237	Chevrolet 2013 Corvette official order guide	https://www.corvetteactioncenter.com/specs/c6/2013/2013_Corvette_Order_Guide.pdf
EU-CHEVROLET-CRUZE-I-SEDAN-PREFL-01	4597	1788	1477	Chevrolet Cruze 2010 official brochure;Automobile-Catalog 2009 Chevrolet Cruze 1.6 specifications	https://autocatalogarchive.com/wp-content/uploads/2021/11/Chevrolet-Cruze-2010-IN.pdf;https://www.automobile-catalog.com/car/2009/1210010/chevrolet_cruze_1_6.html
EU-CHEVROLET-CRUZE-I-SEDAN-FACELIFT-01	4603	1797	1477	Chevrolet UK 2014 Cruze 4-Door official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-4-Door-UK.pdf
EU-CHEVROLET-CRUZE-I-HATCHBACK-FACELIFT-01	4514	1797	1477	Chevrolet UK 2014 Cruze 5-Door official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-5-Door-UK.pdf
EU-CHEVROLET-CRUZE-I-WAGON-01	4681	1797	1521	Chevrolet UK 2014 Cruze Station Wagon official brochure	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Cruze-Station-Wagon-UK.pdf
EU-CHEVROLET-CRUZE-I-HATCHBACK-PREFL-01	4510	1797	1477	GM Chevrolet Cruze Hatchback Specifications and Features	https://media.gm.com/content/dam/Media/documents/CN/Vehicle_Spec/Chevrolet/Chevrolet%20Cruze%20Hatchback%20Specifications%20and%20Features.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_3101-3200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.edmunds.com/chevrolet/ck-1500-series/1996/extended-cab/st-14003/features-specs/ "https://www.edmunds.com/chevrolet/ck-1500-series/1996/extended-cab/st-14003/features-specs/"
[2]: https://www.listadecarros.com/chevrolet/chevrolet-cheyenne-2015-capacidad-lujo-y-elegancia/ "https://www.listadecarros.com/chevrolet/chevrolet-cheyenne-2015-capacidad-lujo-y-elegancia/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3741 行）
- 累计尺寸组：dimension_groups_final.tsv（1083 行）

