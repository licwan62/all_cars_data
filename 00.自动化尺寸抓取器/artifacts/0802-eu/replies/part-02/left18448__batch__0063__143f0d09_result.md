# 任务：left18448 第 6201-6300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0063__143f0d09


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6201-6300 行

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
left18448 第 6201-6300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	4972	1986	2020
EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	4972	1986	2389
EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	5339	1986	2017
EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	5339	1986	2381
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H1-FACELIFT-01	4973	1986	2020
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L1-H2-FACELIFT-01	4973	1986	2389
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H1-FACELIFT-01	5340	1986	2017
EU-FORD-TRANSIT-CUSTOM-V362-MPV-L2-H2-FACELIFT-01	5340	1986	2381
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H1-FACELIFT-01	4973	1986	2000
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L1-H2-FACELIFT-01	4973	1986	2366
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H1-FACELIFT-01	5340	1986	1979
EU-FORD-TRANSIT-CUSTOM-V362-VAN-L2-H2-FACELIFT-01	5340	1986	2343

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Transit custom v362	2.2 Tdci	Kasten	Frontantrieb	Diesel	Sep 2012	Dec 2015	58545
Ford	Transit custom v710	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Oct 2023	-	152502
Ford	Transit custom v710	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Oct 2023	-	152503
Ford	Transit custom v710	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Oct 2023	-	152505
Ford	Transit custom v710	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Oct 2023	-	152506
Ford	Transit custom v710	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Apr 2024	-	156272
Ford	Transit custom v710	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Apr 2024	-	156273
Ford	Transit custom v710	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Apr 2024	-	156275
Ford	Transit custom v710	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Apr 2024	-	156276
Ford	Transit custom v710	2.0 Ecoblue AWD	Kasten	Allrad	Diesel	Oct 2023	-	152504
Ford	Transit custom v710	2.0 Ecoblue AWD	Kasten	Allrad	Diesel	Oct 2023	-	152507
Ford	Transit custom v710	2.0 Ecoblue AWD	Bus	Allrad	Diesel	Apr 2024	-	156274
Ford	Transit custom v710	2.0 Ecoblue AWD	Bus	Allrad	Diesel	Apr 2024	-	156277
Ford	Transit custom v710	2.5 Duratec Plug-in-hybrid	Kasten	Frontantrieb	Benzin/Elektro	Apr 2024	-	156208
Ford	Transit custom v710	2.5 Duratec Plug-in-hybrid	Bus	Frontantrieb	Benzin/Elektro	Apr 2024	-	156278
Ford	Transit custom v710	E-transit Custom	Kasten	Heckantrieb	Elektro	Aug 2024	-	156963
Ford	Transit custom v710	E-transit Custom	Kasten	Heckantrieb	Elektro	Aug 2024	-	156964
Ford	Transit custom v710	E-transit Custom	Bus	Heckantrieb	Elektro	Aug 2024	-	156965
Ford	Transit custom v710	E-transit Custom	Kasten	Heckantrieb	Elektro	Apr 2024	-	156967
Ford	Transit custom v710	E-transit Custom	Bus	Heckantrieb	Elektro	Aug 2024	-	157679
Ford	Transit custom v710	E-transit Custom AWD	Kasten	Allrad	Elektro	Dec 2025	-	802761
Ford	Transit custom v710	E-transit Custom AWD	Kasten	Allrad	Elektro	Dec 2025	-	802762
Ford	Transit custom v710	E-transit Custom AWD	Kasten	Allrad	Elektro	Dec 2025	-	802763
Ford	Transit custom v710	E-transit Custom AWD	Bus	Allrad	Elektro	Dec 2025	-	802764
Ford	Transit custom v710	E-transit Custom AWD	Bus	Allrad	Elektro	Dec 2025	-	802899
Ford	Transit v363	2.0 Ecoblue	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 2021	-	144673
Ford	Transit v363	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Jan 2021	-	144674
Ford	Transit v363	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Oct 2021	-	145764
Ford	Transit v363	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	May 2022	-	152699
Ford	Transit v363	2.0 Ecoblue	Pritsche/Fahrgestell	Frontantrieb	Diesel	May 2022	-	152700
Ford	Transit v363	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	Jul 2023	-	155574
Ford	Transit v363	2.0 Ecoblue	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2023	-	155576
Ford	Transit v363	2.0 Ecoblue	Bus	Frontantrieb	Diesel	Jul 2023	-	155578
Ford	Transit v363	2.0 Ecoblue 4X4	Kasten	Allrad	Diesel	Jul 2023	-	155575
Ford	Transit v363	2.0 Ecoblue 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2023	-	155577
Ford	Transit v363	2.0 Ecoblue Mhev	Bus	Frontantrieb	Diesel/Elektro	Oct 2021	-	145763
Ford	Transit v363	2.0 Ecoblue RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	May 2022	-	148379
Ford	Transit v363	2.0 Ecoblue RWD	Bus	Heckantrieb	Diesel	May 2022	-	152697
Ford	Transit v363	2.0 Ecoblue RWD	Kasten	Heckantrieb	Diesel	May 2022	-	152698
Ford	Transit v363	2.2 Tdci	Kasten	Frontantrieb	Diesel	Aug 2013	Dec 2018	101104
Ford	Transit v363	2.2 Tdci	Kasten	Frontantrieb	Diesel	Aug 2013	Dec 2018	101108
Ford	Transit v363	2.2 Tdci	Kasten	Frontantrieb	Diesel	Aug 2013	Dec 2018	101110
Ford	Transit v363	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2013	Dec 2018	101112
Ford	Transit v363	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2013	Dec 2018	101114
Ford	Transit v363	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 2013	Dec 2018	101118
Ford	Transit v363	2.2 Tdci	Bus	Frontantrieb	Diesel	Aug 2013	Dec 2018	107811
Ford	Transit v363	2.2 Tdci	Bus	Frontantrieb	Diesel	Aug 2013	Dec 2018	107814
Ford	Transit v363	2.2 Tdci	Bus	Frontantrieb	Diesel	Dec 2014	Dec 2018	115815
Ford	Transit v363	2.2 Tdci 4X4	Kasten	Allrad	Diesel	Aug 2015	Dec 2018	101103
Ford	Transit v363	2.2 Tdci 4X4	Kasten	Allrad	Diesel	Aug 2013	Dec 2018	101109
Ford	Transit v363	2.2 Tdci 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Aug 2013	Dec 2018	101117
Ford	Transit v363	2.2 Tdci 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Aug 2013	Dec 2018	101122
Ford	Transit v363	2.2 Tdci 4X4	Bus	Allrad	Diesel	Aug 2013	Dec 2018	107819
Ford	Transit v363	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	Aug 2013	Dec 2018	101100
Ford	Transit v363	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	Aug 2013	Dec 2018	101101
Ford	Transit v363	2.2 Tdci RWD	Kasten	Heckantrieb	Diesel	Aug 2013	Dec 2018	101102
Ford	Transit v363	2.2 Tdci RWD	Kasten	Heckantrieb	Diesel	Aug 2013	Dec 2018	101106
Ford	Transit v363	2.2 Tdci RWD	Kasten	Heckantrieb	Diesel	Aug 2013	Dec 2018	101111
Ford	Transit v363	2.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 2013	Dec 2018	101113
Ford	Transit v363	2.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 2013	Dec 2018	101115
Ford	Transit v363	2.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Aug 2013	Dec 2018	101119
Ford	Transit v363	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	Aug 2013	Dec 2018	107657
Ford	Transit v363	E-transit	Kasten	Heckantrieb	Elektro	Mar 2022	Jun 2025	147339
Ford	Transit v363	E-transit	Kasten	Heckantrieb	Elektro	Mar 2022	Jun 2025	147340
Ford	Transit v363	E-transit	Pritsche/Fahrgestell	Heckantrieb	Elektro	Mar 2022	Jun 2025	147357
Ford	Transit v363	E-transit	Pritsche/Fahrgestell	Heckantrieb	Elektro	Mar 2022	Jun 2025	147358
Ford	Transit v363	E-transit	Kasten	Heckantrieb	Elektro	Jul 2025	-	802564
Ford	Transit v363	E-transit	Kasten	Heckantrieb	Elektro	Jul 2025	-	802565
Ford	Transit v363	E-transit	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2025	-	802566
Ford	Transit v363	E-transit	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2025	-	802567
Ford USA	Bronco	2.7 4X4	Geländewagen offen	Allrad	Benzin	Sep 2020	-	152107
Ford USA	Bronco	5.8 4WD	SUV	Allrad	Benzin	Sep 1995	Dec 1996	52532
Ford USA	E-350 cutaway van	4.9	Kasten	Heckantrieb	Benzin	Sep 1982	Dec 1986	803197
Ford USA	Edge	2	SUV	Frontantrieb	Benzin	Sep 2014	-	109691
Ford USA	Edge	2	SUV	Frontantrieb	Benzin	Jan 2015	-	122033
Ford USA	Edge	3.5	SUV	Frontantrieb	Benzin	Jan 2010	Dec 2015	57804
Ford USA	Edge	2.0 AWD	SUV	Allrad	Benzin	Sep 2011	-	54159
Ford USA	Edge	2.0 AWD	SUV	Allrad	Benzin	Jan 2015	-	122034
Ford USA	Edge	2.0 Tdci AWD	SUV	Allrad	Diesel	Aug 2015	Jul 2018	117197
Ford USA	Edge	2.0 Tdci Bi-turbo AWD	SUV	Allrad	Diesel	Aug 2015	Jul 2018	117198
Ford USA	Edge	3.5 AWD	SUV	Allrad	Benzin	Jan 2010	-	57803
Ford USA	Edge	3.5 AWD	SUV	Allrad	Benzin	Aug 2006	-	57806
Ford USA	Edge	3.7 AWD	SUV	Allrad	Benzin	Sep 2010	Dec 2013	50304
Ford USA	Escape	2.3 Hybrid 4X4	SUV	Allrad	Benzin/Elektro	Sep 2005	Jul 2007	41134
Ford USA	Explorer	4.6	SUV	Heckantrieb	Benzin	Sep 2001	Dec 2005	59389
Ford USA	Explorer	3.5 4WD	SUV	Allrad	Benzin	Oct 2010	-	54167
Ford USA	Explorer	3.5 Ecoboost 4WD	SUV	Allrad	Benzin	Sep 2013	-	107221
Ford USA	Explorer	4.0 4WD	SUV	Allrad	Benzin	May 2006	Dec 2010	58109
Ford USA	Explorer	4.0 4WD	SUV	Allrad	Benzin	Sep 1998	Dec 2001	127741
Ford USA	Explorer	4.0 Flexfuel 4WD	SUV	Allrad	Benzin/Ethanol	Sep 2003	Dec 2005	41205
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	Oct 1996	Dec 2001	10594
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	Oct 1998	Dec 2001	14433
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	Nov 1994	Dec 2002	57899
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	Jun 2000	Dec 2001	108689
Ford USA	Explorer	4.9 4WD	SUV	Allrad	Benzin	Jan 1996	Dec 2001	8007
Ford USA	Explorer	EV	SUV	Heckantrieb	Elektro	Jun 2024	-	158272
Ford USA	Explorer	EV	SUV	Heckantrieb	Elektro	Jun 2024	-	158273
Ford USA	Explorer	EV	SUV	Heckantrieb	Elektro	Sep 2024	-	800866
Ford USA	Explorer	EV	SUV	Heckantrieb	Elektro	Mar 2026	-	803193
Ford USA	Explorer	EV 4X4	SUV	Allrad	Elektro	Jun 2024	-	158274


--- Round 1 / 首次发送 ---
更新点

* 闭合前 25 个输入 Ktype，共形成 52 条映射行。
* `58545` 按 V362 改款前的 L1H1、L1H2、L2H1、L2H2 四种物理外廓拆分，直接复用跨批次已有尺寸组，不重复建组。
* Transit Custom V710 的 Kasten 与 Bus 分别按 Van、MPV 建组；官方资料确认 L1、L2 两种长度，车身宽度均为不含后视镜的 `2032 mm`。高度采用官方区间的最大外部高度端点：L1=`2040 mm`、L2=`2031 mm`。
* V710 柴油、PHEV、纯电及 AWD 配置均可覆盖相应 L1/L2 外廓，因此各 Ktype 拆分为两个稳定长度分支。([福特德国][1])
* V710 Kasten 使用车身代码 `NRN`，Bus 使用 `NXN`。([Rameder][2])

当前批次进度

* 已处理输入 Ktype：25 / 100
* READY 映射：52 行
* 尚待处理输入 Ktype：75
* 本轮引用尺寸组：8 个，其中复用既有组 4 个、新建组 4 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58545_l1h1	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	MEDIUM	L1H1 物理外廓分支。	READY
58545_l1h2	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	MEDIUM	L1H2 物理外廓分支。	READY
58545_l2h1	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	MEDIUM	L2H1 物理外廓分支。	READY
58545_l2h2	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	MEDIUM	L2H2 物理外廓分支。	READY
152502_l1h1	152502	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152502_l2h1	152502	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152503_l1h1	152503	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152503_l2h1	152503	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152505_l1h1	152505	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152505_l2h1	152505	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152506_l1h1	152506	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152506_l2h1	152506	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156272_l1h1	156272	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156272_l2h1	156272	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156273_l1h1	156273	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156273_l2h1	156273	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156275_l1h1	156275	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156275_l2h1	156275	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156276_l1h1	156276	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156276_l2h1	156276	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152504_l1h1	152504	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152504_l2h1	152504	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152507_l1h1	152507	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152507_l2h1	152507	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156274_l1h1	156274	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156274_l2h1	156274	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156277_l1h1	156277	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156277_l2h1	156277	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156208_l1h1	156208	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156208_l2h1	156208	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156278_l1h1	156278	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156278_l2h1	156278	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156963_l1h1	156963	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156963_l2h1	156963	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156964_l1h1	156964	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156964_l2h1	156964	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156965_l1h1	156965	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156965_l2h1	156965	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156967_l1h1	156967	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156967_l2h1	156967	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
157679_l1h1	157679	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
157679_l2h1	157679	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802761_l1h1	802761	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802761_l2h1	802761	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802762_l1h1	802762	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802762_l2h1	802762	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802763_l1h1	802763	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802763_l2h1	802763	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802764_l1h1	802764	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802764_l2h1	802764	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802899_l1h1	802899	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802899_l2h1	802899	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	5050	2032	2040	Ford Transit Custom official price list (Kastenwagen LKW)	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-neue-ford-transit-custom.pdf
EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	5450	2032	2031	Ford Transit Custom official price list (Kastenwagen LKW)	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-neue-ford-transit-custom.pdf
EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	5050	2032	2040	Ford Transit Custom Kombi PKW official price list	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-Ford-Transit-Custom-KombiPKW.pdf
EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	5450	2032	2031	Ford Transit Custom Kombi PKW official price list	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-Ford-Transit-Custom-KombiPKW.pdf
```

下一步优先处理

1. 集中闭合 Transit V363 的 Van、Bus、Pritsche/Fahrgestell 三类物理车身。
2. 一次性确认 V363 各 L1/L2/L3/L4、H1/H2/H3 与驱动形式造成的外廓边界。
3. 尺寸组闭合后，批量关联对应的柴油、MHEV 和 E-Transit Ktype，不逐发动机重复抓取。

推进信号：CONTINUE

[1]: https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-neue-ford-transit-custom.pdf "FordTransitCustomKastenwagenLKWDoppelkabineLKWMultiCab_DE_2038_20052026104110_v3.indd"
[2]: https://www.rameder.eu/towbars/ford/transit-custom-v710/?utm_source=chatgpt.com "Ford TRANSIT CUSTOM V710 towbars | RAMEDER"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 新增闭合 9 个 Transit V363 Ktype，共新增 40 条 READY 映射。
* Transit V363 Van 按 FWD、RWD/AWD、L2/L3/L4、H2/H3，以及 L4H3 的 SRW/DRW 外廓拆分；Ford 官方规格明确列出对应长度、不含后视镜宽度和最大高度。
* FWD Bus 按 Kombi PKW M1 的 L2H2、L2H3、L3H2、L3H3 建组。
* RWD Bus 按 Minibus 的 L2H2、L3H2、L3H3、L4H3 DRW 建组。

当前批次进度

* 已处理输入 Ktype：34 / 100
* READY 映射：92 行
* 待处理输入 Ktype：66
* 当前批次已引用尺寸组：26 个
* 本轮首次创建尺寸组：18 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144674_l2h2	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
144674_l2h3	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
144674_l3h2	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
144674_l3h3	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
145764_l2h2	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
145764_l2h3	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
145764_l3h2	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
145764_l3h3	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
152699_l2h2	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
152699_l2h3	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
152699_l3h2	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
152699_l3h3	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
155574_l2h2	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
155574_l2h3	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
155574_l3h2	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
155574_l3h3	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
155578_l2h2	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
155578_l2h3	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
155578_l3h2	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
155578_l3h3	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
155575_l2h2	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	MEDIUM	L2H2 RWD/AWD physical branch.	READY
155575_l2h3	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	MEDIUM	L2H3 RWD/AWD physical branch.	READY
155575_l3h2	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	MEDIUM	L3H2 RWD/AWD physical branch.	READY
155575_l3h3	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	MEDIUM	L3H3 RWD/AWD physical branch.	READY
155575_l4h3_srw	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	MEDIUM	L4H3 RWD/AWD SRW physical branch.	READY
155575_l4h3_drw	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	MEDIUM	L4H3 RWD/AWD DRW physical branch.	READY
145763_l2h2	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
145763_l2h3	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
145763_l3h2	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
145763_l3h3	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
152697_l2h2	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-RWD-01	MEDIUM	L2H2 RWD passenger-body branch.	READY
152697_l3h2	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-RWD-01	MEDIUM	L3H2 RWD passenger-body branch.	READY
152697_l3h3	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-RWD-01	MEDIUM	L3H3 RWD passenger-body branch.	READY
152697_l4h3_drw	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L4-H3-RWD-DRW-01	MEDIUM	L4H3 RWD DRW passenger-body branch.	READY
152698_l2h2	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	MEDIUM	L2H2 RWD/AWD physical branch.	READY
152698_l2h3	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	MEDIUM	L2H3 RWD/AWD physical branch.	READY
152698_l3h2	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	MEDIUM	L3H2 RWD/AWD physical branch.	READY
152698_l3h3	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	MEDIUM	L3H3 RWD/AWD physical branch.	READY
152698_l4h3_srw	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	MEDIUM	L4H3 RWD/AWD SRW physical branch.	READY
152698_l4h3_drw	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	MEDIUM	L4H3 RWD/AWD DRW physical branch.	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	5531	2059	2533	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	5531	2059	2769	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	5981	2059	2530	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	5981	2059	2767	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	5531	2059	2534	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	5531	2059	2771	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	5981	2059	2533	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	5981	2059	2769	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	6704	2059	2778	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	6704	2126	2778	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	5531	2059	2530	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	5531	2059	2766	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	5981	2059	2526	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	5981	2059	2762	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H2-RWD-01	5531	2059	2484	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H2-RWD-01	5981	2059	2528	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-RWD-01	5981	2059	2764	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L4-H3-RWD-DRW-01	6704	2126	2757	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
```

下一步优先处理

1. 闭合 Transit V363 的 Pritsche/Fahrgestell，按单排/双排驾驶室、L1-L5、FWD/RWD/AWD、SRW/DRW 外廓拆分。
2. 批量关联 `144673`、`152700`、`155576`、`155577`、`148379`，不重复核对已建立的 Van 和 MPV 尺寸组。
3. 随后处理 2013-2018 年 2.2 TDCi 与 E-Transit Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增闭合 Transit V363 的 5 个 `Pritsche/Fahrgestell` Ktype：`144673`、`152700`、`155576`、`155577`、`148379`，共新增 74 条 READY 映射。
* 输入车身类型同时包含 `Pritsche` 与 `Fahrgestell`，因此不能只保留一种外廓；本轮分别建立裸底盘 `Chassis Cab` 与原厂平板货厢 `Pickup` 分支，并继续按单排/双排、L2–L5、FWD/RWD/AWD、SRW/DRW 拆分。Ford 官方尺寸表分别提供底盘与含平板货厢的总长、不含后视镜宽度和最大高度。
* AWD 型号按官方车型可用性只关联 L2–L4 的 SRW 外廓；未创建猜测性的 AWD DRW 或 L5 分支。
* RWD 与 AWD 在三维完全一致的 SRW 外廓上复用同一 `RWD-AWD` 尺寸组；仅新增一次尺寸事实。

## 当前批次进度

* 已处理输入 Ktype：39 / 100
* READY 映射：166 行
* 待处理输入 Ktype：61
* 当前批次累计引用尺寸组：68 个
* 本轮首次创建尺寸组：42 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144673_chassis_sc_l2_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
144673_chassis_sc_l3_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
144673_chassis_sc_l4_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
144673_pickup_sc_l2_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
144673_pickup_sc_l3_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
144673_pickup_sc_l4_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
144673_chassis_dc_l2_fwd_srw	144673	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
144673_chassis_dc_l3_fwd_srw	144673	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
144673_pickup_dc_l2_fwd_srw	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
144673_pickup_dc_l3_fwd_srw	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
152700_chassis_sc_l2_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
152700_chassis_sc_l3_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
152700_chassis_sc_l4_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
152700_pickup_sc_l2_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
152700_pickup_sc_l3_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
152700_pickup_sc_l4_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
152700_chassis_dc_l2_fwd_srw	152700	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
152700_chassis_dc_l3_fwd_srw	152700	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
152700_pickup_dc_l2_fwd_srw	152700	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
152700_pickup_dc_l3_fwd_srw	152700	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
155576_chassis_sc_l2_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
155576_chassis_sc_l3_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
155576_chassis_sc_l4_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
155576_pickup_sc_l2_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
155576_pickup_sc_l3_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
155576_pickup_sc_l4_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
155576_chassis_dc_l2_fwd_srw	155576	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
155576_chassis_dc_l3_fwd_srw	155576	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
155576_pickup_dc_l2_fwd_srw	155576	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
155576_pickup_dc_l3_fwd_srw	155576	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
155577_chassis_sc_l2_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 AWD SRW chassis branch.	READY
155577_chassis_sc_l3_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 AWD SRW chassis branch.	READY
155577_chassis_sc_l4_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 AWD SRW chassis branch.	READY
155577_pickup_sc_l2_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 AWD SRW dropside branch.	READY
155577_pickup_sc_l3_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 AWD SRW dropside branch.	READY
155577_pickup_sc_l4_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 AWD SRW dropside branch.	READY
155577_chassis_dc_l2_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 AWD SRW chassis branch.	READY
155577_chassis_dc_l3_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 AWD SRW chassis branch.	READY
155577_chassis_dc_l4_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 AWD SRW chassis branch.	READY
155577_pickup_dc_l2_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 AWD SRW dropside branch.	READY
155577_pickup_dc_l3_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 AWD SRW dropside branch.	READY
155577_pickup_dc_l4_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 AWD SRW dropside branch.	READY
148379_chassis_sc_l2_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
148379_chassis_sc_l2_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
148379_chassis_sc_l3_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
148379_chassis_sc_l3_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
148379_chassis_sc_l4_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
148379_chassis_sc_l4_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
148379_chassis_sc_l5_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-SRW-01	MEDIUM	Single-cab L5 RWD SRW chassis branch.	READY
148379_chassis_sc_l5_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-DRW-01	MEDIUM	Single-cab L5 RWD DRW chassis branch.	READY
148379_pickup_sc_l2_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
148379_pickup_sc_l2_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
148379_pickup_sc_l3_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
148379_pickup_sc_l3_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
148379_pickup_sc_l4_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
148379_pickup_sc_l4_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
148379_pickup_sc_l5_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-SRW-01	MEDIUM	Single-cab L5 RWD SRW dropside branch.	READY
148379_pickup_sc_l5_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-DRW-01	MEDIUM	Single-cab L5 RWD DRW dropside branch.	READY
148379_chassis_dc_l2_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 RWD SRW chassis branch.	READY
148379_chassis_dc_l2_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-DRW-01	MEDIUM	Double-cab L2 RWD DRW chassis branch.	READY
148379_chassis_dc_l3_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 RWD SRW chassis branch.	READY
148379_chassis_dc_l3_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-DRW-01	MEDIUM	Double-cab L3 RWD DRW chassis branch.	READY
148379_chassis_dc_l4_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 RWD SRW chassis branch.	READY
148379_chassis_dc_l4_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-DRW-01	MEDIUM	Double-cab L4 RWD DRW chassis branch.	READY
148379_chassis_dc_l5_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-SRW-01	MEDIUM	Double-cab L5 RWD SRW chassis branch.	READY
148379_chassis_dc_l5_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-DRW-01	MEDIUM	Double-cab L5 RWD DRW chassis branch.	READY
148379_pickup_dc_l2_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 RWD SRW dropside branch.	READY
148379_pickup_dc_l2_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-DRW-01	MEDIUM	Double-cab L2 RWD DRW dropside branch.	READY
148379_pickup_dc_l3_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 RWD SRW dropside branch.	READY
148379_pickup_dc_l3_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-DRW-01	MEDIUM	Double-cab L3 RWD DRW dropside branch.	READY
148379_pickup_dc_l4_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 RWD SRW dropside branch.	READY
148379_pickup_dc_l4_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-DRW-01	MEDIUM	Double-cab L4 RWD DRW dropside branch.	READY
148379_pickup_dc_l5_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-SRW-01	MEDIUM	Double-cab L5 RWD SRW dropside branch.	READY
148379_pickup_dc_l5_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-DRW-01	MEDIUM	Double-cab L5 RWD DRW dropside branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	5572	2052	2200	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	6022	2052	2194	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	6579	2052	2195	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	5767	2098	2200	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	6204	2098	2194	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	6797	2098	2195	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	5572	2066	2236	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	6022	2066	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	5767	2098	2236	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	6204	2098	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	5572	2052	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-DRW-01	5572	2111	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	6022	2052	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-DRW-01	6022	2111	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	6579	2052	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-DRW-01	6579	2111	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	5767	2098	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-DRW-01	5767	2198	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	6204	2098	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-DRW-01	6204	2198	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	6797	2098	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-DRW-01	6797	2198	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	5572	2066	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-DRW-01	5572	2111	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	6022	2066	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-DRW-01	6022	2111	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	6404	2066	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-DRW-01	6404	2111	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	5767	2098	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-DRW-01	5767	2198	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	6204	2098	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-DRW-01	6204	2198	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	6587	2098	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-DRW-01	6587	2198	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-SRW-01	7577	2052	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-DRW-01	7577	2111	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-SRW-01	7797	2098	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-DRW-01	7797	2198	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-SRW-01	7394	2066	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-DRW-01	7394	2111	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-SRW-01	7612	2098	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-DRW-01	7612	2198	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
```

## 下一步优先处理

1. 对 2013–2018 年 Transit V363 2.2 TDCi 只做一次改款前外廓边界核对，确认无三维变化后批量复用现有 Van、MPV、Chassis Cab 与 Pickup 尺寸组。
2. 单独闭合 E-Transit 的电动车最大高度差异，再批量关联 `147339`、`147340`、`147357`、`147358`、`802564`–`802567`。
3. 完成 Transit V363 后转入 Bronco、Edge、Escape、Explorer 聚类。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 8 个 Transit V363 E-Transit Ktype，共新增 36 条 READY 映射。
* E-Transit Kastenwagen 的 L2H2、L2H3、L3H2、L3H3、L4H3 三维与已建立的 V363 RWD/AWD Van 尺寸组完全一致，全部直接复用。
* E-Transit `Pritsche/Fahrgestell` 仅关联官方明确提供的单排驾驶室 L3、L4 裸底盘及原厂平板分支；三维与已建立尺寸组完全一致，不新建尺寸组。官方表明确给出不含后视镜宽度。

## 当前批次进度

* 已处理输入 Ktype：47 / 100
* READY 映射：202 行
* PENDING 输入 Ktype：53
* 已确认尺寸组：68 个
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
147339_l2h2	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
147339_l2h3	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
147339_l3h2	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
147339_l3h3	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
147339_l4h3_srw	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
147340_l2h2	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
147340_l2h3	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
147340_l3h2	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
147340_l3h3	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
147340_l4h3_srw	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
147357_chassis_sc_l3	147357	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
147357_chassis_sc_l4	147357	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
147357_pickup_sc_l3	147357	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
147357_pickup_sc_l4	147357	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
147358_chassis_sc_l3	147358	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
147358_chassis_sc_l4	147358	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
147358_pickup_sc_l3	147358	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
147358_pickup_sc_l4	147358	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
802564_l2h2	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
802564_l2h3	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
802564_l3h2	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
802564_l3h3	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
802564_l4h3_srw	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
802565_l2h2	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
802565_l2h3	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
802565_l3h2	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
802565_l3h3	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
802565_l4h3_srw	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
802566_chassis_sc_l3	802566	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
802566_chassis_sc_l4	802566	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
802566_pickup_sc_l3	802566	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
802566_pickup_sc_l4	802566	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
802567_chassis_sc_l3	802567	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
802567_chassis_sc_l4	802567	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
802567_pickup_sc_l3	802567	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
802567_pickup_sc_l4	802567	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

集中处理 2013–2018 年 Transit V363 2.2 TDCi：先按 Van、Bus、`Pritsche/Fahrgestell` 和 FWD/RWD/AWD 聚类，确认改款前高度边界后批量关联全部剩余 Transit Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 7 个 Transit V363 2.2 TDCi `Kasten` Ktype，共新增 38 条 READY 映射。
* 2013–2018 年 Van 外廓按 L2H2、L2H3、L3H2、L3H3，以及 RWD 专属 L4H3 SRW/DRW 拆分；FWD、RWD、AWD 三维完全相同的 L2/L3 分支复用同一尺寸组。官方车型矩阵显示 AWD 不覆盖 L4。
* L4H3 SRW 的不含后视镜宽度采用 Ford New Zealand 官方规格中的 `2059 mm`；DRW 为 `2126 mm`。

## 当前批次进度

* 已处理输入 Ktype：54 / 100
* READY 映射：240 行
* PENDING 输入 Ktype：46
* 已确认尺寸组：74 个
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
101104_l2h2	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101104_l2h3	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101104_l3h2	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101104_l3h3	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101108_l2h2	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101108_l2h3	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101108_l3h2	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101108_l3h3	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101110_l2h2	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101110_l2h3	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101110_l3h2	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101110_l3h3	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101103_l2h2	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift AWD branch.	READY
101103_l2h3	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift AWD branch.	READY
101103_l3h2	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift AWD branch.	READY
101103_l3h3	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift AWD branch.	READY
101109_l2h2	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift AWD branch.	READY
101109_l2h3	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift AWD branch.	READY
101109_l3h2	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift AWD branch.	READY
101109_l3h3	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift AWD branch.	READY
101102_l2h2	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101102_l2h3	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101102_l3h2	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101102_l3h3	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101102_l4h3_srw	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101102_l4h3_drw	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
101106_l2h2	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101106_l2h3	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101106_l3h2	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101106_l3h3	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101106_l4h3_srw	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101106_l4h3_drw	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
101111_l2h2	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101111_l2h3	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101111_l3h2	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101111_l3h3	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101111_l4h3_srw	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101111_l4h3_drw	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	5531	2059	2550	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	5531	2059	2789	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	5981	2059	2547	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	5981	2059	2786	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	6704	2059	2781	Ford Transit official UK brochure MY2014; Ford Transit Cargo official New Zealand brochure	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf; https://www.forddealers.co.nz/i/files/transit_cargo_brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	6704	2126	2781	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
```

## 下一步优先处理

集中闭合 2013–2018 年 Transit V363 的 Bus 与 `Pritsche/Fahrgestell` Ktype，优先复用本轮已确认的改款前 L2/L3/L4物理边界，仅为客车或底盘/平板外廓新建必要尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Transit V363 2.2 TDCi RWD 的 3 个 Bus Ktype：`101100`、`101101`、`107657`，新增 9 条 READY 映射。
* 按官方 Minibus 车身矩阵拆分为 L3H2、L3H3 和 L4H3 DRW；对应长度分别为 `5981 / 5981 / 6704 mm`，不含后视镜宽度分别为 `2059 / 2059 / 2126 mm`。
* 高度区间按最大外部高度端点落盘：L3H2=`2517 mm`、L3H3=`2756 mm`、L4H3 DRW=`2674 mm`。

## 当前批次进度

* 已处理输入 Ktype：57 / 100
* READY 映射：249 行
* PENDING 输入 Ktype：43
* 已确认尺寸组：77 个
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
101100_l3h2	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
101100_l3h3	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
101100_l4h3_drw	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
101101_l3h2	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
101101_l3h3	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
101101_l4h3_drw	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
107657_l3h2	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
107657_l3h3	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
107657_l4h3_drw	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	5981	2059	2517	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	5981	2059	2756	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	6704	2126	2674	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
```

## 下一步优先处理

集中闭合 2013–2018 年 Transit V363 的 `Pritsche/Fahrgestell` FWD、RWD 和 AWD Ktype；按已核对的 L2–L4、SRW/DRW 底盘与原厂平板外廓批量建组和关联。随后处理尚未闭合的 FWD/AWD Bus。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 5 个 Transit V363 2.2 TDCi `Pritsche/Fahrgestell` Ktype：`101112`、`101114`、`101118`、`101117`、`101122`，新增 26 条 READY 映射。
* FWD 单排驾驶室覆盖 L2、L3、L4；AWD 单排驾驶室覆盖 L2、L3。裸底盘和原厂平板货厢分别拆分。
* 相同长度的 FWD 与 AWD SRW 外廓三维一致，因此复用同一改款前尺寸组，不按驱动形式重复建组。官方尺寸表同时给出了总长、不含后视镜宽度、最大高度及平板货厢外廓。

## 当前批次进度

* 已处理输入 Ktype：62 / 100
* READY 映射：275 行
* PENDING 输入 Ktype：38
* 已确认尺寸组：83 个
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
101112_chassis_sc_l2	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101112_chassis_sc_l3	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101112_chassis_sc_l4	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101112_pickup_sc_l2	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101112_pickup_sc_l3	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101112_pickup_sc_l4	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
101114_chassis_sc_l2	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101114_chassis_sc_l3	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101114_chassis_sc_l4	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101114_pickup_sc_l2	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101114_pickup_sc_l3	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101114_pickup_sc_l4	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
101118_chassis_sc_l2	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101118_chassis_sc_l3	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101118_chassis_sc_l4	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101118_pickup_sc_l2	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101118_pickup_sc_l3	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101118_pickup_sc_l4	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
101117_chassis_sc_l2	101117	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD chassis branch.	READY
101117_chassis_sc_l3	101117	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD chassis branch.	READY
101117_pickup_sc_l2	101117	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD dropside branch.	READY
101117_pickup_sc_l3	101117	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD dropside branch.	READY
101122_chassis_sc_l2	101122	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD chassis branch.	READY
101122_chassis_sc_l3	101122	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD chassis branch.	READY
101122_pickup_sc_l2	101122	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD dropside branch.	READY
101122_pickup_sc_l3	101122	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD dropside branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	5572	2052	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	6022	2052	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	6579	2052	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	5767	2098	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	6204	2098	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	6797	2098	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
```

## 下一步优先处理

闭合 `101113`、`101115`、`101119` 三个 RWD `Pritsche/Fahrgestell` Ktype，补齐 L1–L4、SRW/DRW、单排/双排分支；随后处理剩余 FWD/AWD Bus。

推进信号：CONTINUE


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 `101113`、`101115`、`101119` 三个 Transit V363 2.2 TDCi RWD `Pritsche/Fahrgestell` Ktype，共新增 42 条 READY 映射。
* L2–L4 SRW 直接复用既有改款前尺寸组；本轮仅首次创建 L1 SRW 以及 L2–L4 DRW 的底盘和原厂平板尺寸组。
* 官方 MY2014 尺寸表确认单排驾驶室 RWD 覆盖 L1–L4，并分别列出底盘、平板货厢以及 SRW/DRW 的总长、不含后视镜宽度和最大高度。

## 当前批次进度

* 已处理输入 Ktype：65 / 100
* READY 映射：317 行
* PENDING 输入 Ktype：35
* 已确认尺寸组：91 个
* 本轮首次创建尺寸组：8 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
101113_chassis_sc_l1_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101113_chassis_sc_l2_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101113_chassis_sc_l2_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101113_chassis_sc_l3_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101113_chassis_sc_l3_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101113_chassis_sc_l4_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101113_chassis_sc_l4_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101113_pickup_sc_l1_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101113_pickup_sc_l2_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101113_pickup_sc_l2_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101113_pickup_sc_l3_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101113_pickup_sc_l3_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101113_pickup_sc_l4_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101113_pickup_sc_l4_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
101115_chassis_sc_l1_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101115_chassis_sc_l2_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101115_chassis_sc_l2_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101115_chassis_sc_l3_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101115_chassis_sc_l3_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101115_chassis_sc_l4_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101115_chassis_sc_l4_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101115_pickup_sc_l1_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101115_pickup_sc_l2_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101115_pickup_sc_l2_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101115_pickup_sc_l3_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101115_pickup_sc_l3_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101115_pickup_sc_l4_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101115_pickup_sc_l4_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
101119_chassis_sc_l1_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101119_chassis_sc_l2_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101119_chassis_sc_l2_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101119_chassis_sc_l3_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101119_chassis_sc_l3_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101119_chassis_sc_l4_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101119_chassis_sc_l4_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101119_pickup_sc_l1_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101119_pickup_sc_l2_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101119_pickup_sc_l2_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101119_pickup_sc_l3_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101119_pickup_sc_l3_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101119_pickup_sc_l4_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101119_pickup_sc_l4_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	5205	2052	2219	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	5357	2098	2219	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	5572	2111	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	5767	2198	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	6022	2111	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	6204	2198	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	6579	2111	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	6797	2198	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
```

## 下一步优先处理

闭合剩余 `107811`、`107814`、`115815` FWD Bus 与 `107819` AWD Bus，确认 Kombi/Bus 的 L2/L3 和 H2/H3 边界后批量关联；随后进入 Ford USA Bronco、Edge、Escape、Explorer 聚类。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合剩余 4 个 Transit V363 2.2 TDCi Bus Ktype：`107811`、`107814`、`115815`、`107819`，新增 16 条 READY 映射。
* FWD 与 AWD Bus 均按 L2H2、L2H3、L3H2、L3H3 四种 Kombi 外廓拆分。
* 官方车型矩阵确认 Transit Kombi 提供 FWD/AWD 的 L2、L3 配置；其外部长度、宽度和高度与同代 Van 壳体一致，因此直接复用已闭合的四个改款前尺寸组，不重复建组。

## 当前批次进度

* 已处理输入 Ktype：69 / 100
* READY 映射：333 行
* PENDING 输入 Ktype：31
* 已确认尺寸组：91 个
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
107811_l2h2	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
107811_l2h3	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
107811_l3h2	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
107811_l3h3	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
107814_l2h2	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
107814_l2h3	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
107814_l3h2	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
107814_l3h3	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
115815_l2h2	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
115815_l2h3	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
115815_l3h2	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
115815_l3h3	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
107819_l2h2	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift AWD passenger-body branch.	READY
107819_l2h3	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift AWD passenger-body branch.	READY
107819_l3h2	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift AWD passenger-body branch.	READY
107819_l3h3	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift AWD passenger-body branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

集中闭合 Ford USA Bronco、E-350 Cutaway Van 与 Edge：先按车型代际和车身边界各建一次尺寸组，再批量关联相同代际的发动机及驱动版本。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合全部 10 个 Ford USA Edge Ktype，新增 10 条 READY 映射。
* Edge 第一代按改款前与改款后拆成两个外廓：改款前为 `4717×1925×1702 mm`，改款后为 `4679×1930×1702 mm`。两套尺寸均采用不含后视镜宽度。([汽车目录档案][1])
* Edge 第二代区分北美与欧洲外廓：北美版为 `4779×1928×1742 mm`，欧洲柴油版因保险杠和车身设定不同，为 `4808×1928×1692 mm`。([艾德蒙顿城市福特][2])
* 同一代际内 FWD、AWD、汽油发动机和不同功率版本直接复用对应尺寸组，未重复建组。

## 当前批次进度

* 已处理输入 Ktype：79 / 100
* READY 映射：343 行
* PENDING 输入 Ktype：21
* 已确认尺寸组：95 个
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
109691	109691	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
122033	122033	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
57804	57804	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
54159	54159	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
122034	122034	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
117197	117197	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-EU-01	HIGH	European-market diesel exterior.	READY
117198	117198	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-EU-01	HIGH	European-market diesel exterior.	READY
57803	57803	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
57806	57806	SUV	Edge I pre-facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-PREFL-01	HIGH	First-generation pre-facelift exterior.	READY
50304	50304	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-EDGE-II-SUV-NA-01	4779	1928	1742	Ford Edge official brochure MY2015	https://www.cityfordsales.com/new/2016/pdfs/2015-ford-edge.pdf
EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	4679	1930	1702	Ford Edge official brochure MY2011	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Edge-2011.pdf
EU-FORD-USA-EDGE-II-SUV-EU-01	4808	1928	1692	Ford Edge official UK brochure MY2017	https://www.winfordroadgarages.co.uk/pdf/edge.pdf
EU-FORD-USA-EDGE-I-SUV-PREFL-01	4717	1925	1702	Ford Edge official brochures MY2008/MY2010	https://xr793.com/wp-content/uploads/2016/10/2008-Ford-Edge.pdf; https://www.centuryu.com/uploads/1/4/4/6/144698822/2010_edge.pdf
```

## 下一步优先处理

1. 闭合 Escape Hybrid 与 Explorer 的 1990年代、第三代、第四代和第五代外廓。
2. 将 Explorer EV 单独按欧洲电动车平台建组，不与美国燃油 Explorer 复用。
3. Bronco 2.7 需要拆分两门、四门及宽体越野套件；E-350 Cutaway 需先确认裸底盘长度和不含后视镜宽度，再进入 READY。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Edge-2010.pdf?utm_source=chatgpt.com "Ford-Edge-2010.pdf"
[2]: https://www.cityfordsales.com/new/2016/pdfs/2015-ford-edge.pdf?utm_source=chatgpt.com "2015-ford-edge.pdf"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Escape Hybrid `41134`：按 4WD 外廓建立单一尺寸组。Ford 官方手册明确给出车身宽度、不含后视镜口径及 4WD 最大高度。
* 闭合 Explorer V 的 `54167`、`107221`。两项 Ktype 均归入 U502，目录覆盖改款前后年份，因此分别拆分为 `prefl` 与 `facelift` 外廓。([auto-doc.at][1])
* 闭合 Explorer IV `58109`，以及 5 个 Explorer EV Ktype。
* Explorer EV 的 RWD 与 AWD 长度、车身宽度相同，但 AWD 高度增加至 `1639 mm`，因此独立建组。

## 当前批次进度

* 已处理输入 Ktype：88 / 100
* READY 映射：354 行
* PENDING 输入 Ktype：12
* 已确认尺寸组：101 个
* 本轮首次创建尺寸组：6 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
41134	41134	SUV	Escape I facelift		5	EU-FORD-USA-ESCAPE-I-SUV-FACELIFT-01	HIGH	4WD hybrid exterior.	READY
54167_prefl	54167	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	MEDIUM	Pre-facelift exterior branch.	READY
54167_facelift	54167	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	MEDIUM	Facelift exterior branch.	READY
107221_prefl	107221	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	MEDIUM	Pre-facelift exterior branch.	READY
107221_facelift	107221	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	MEDIUM	Facelift exterior branch.	READY
58109	58109	SUV	Explorer IV		5	EU-FORD-USA-EXPLORER-IV-SUV-01	HIGH	Fourth-generation exterior.	READY
158272	158272	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
158273	158273	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
800866	800866	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
803193	803193	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
158274	158274	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-AWD-01	HIGH	AWD electric exterior.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-ESCAPE-I-SUV-FACELIFT-01	4442	1780	1784	Ford Escape HEV official owner guide MY2005	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/05hevog1e.pdf
EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	5006	2004	1788	Ford Explorer official brochure MY2011	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2011.pdf
EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	5047	2004	1778	Ford Explorer official brochure MY2019	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2019.pdf
EU-FORD-USA-EXPLORER-IV-SUV-01	4912	1872	1849	Ford Explorer official brochure MY2009	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2009.pdf
EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	4468	1871	1630	Ford All-Electric Explorer official fact sheet	https://www.fromtheroad.ford.com/content/dam/fordmediasite/at/de/library/2024/neuer-vollelektrischer-ford-explorer--weltrekord-zum-verkaufsstart/2024Ford_ChargeAroundTheGlobe_FactSheet_EU.pdf
EU-FORD-USA-EXPLORER-EV-I-SUV-AWD-01	4468	1871	1639	Ford All-Electric Explorer official fact sheet	https://www.fromtheroad.ford.com/content/dam/fordmediasite/at/de/library/2024/neuer-vollelektrischer-ford-explorer--weltrekord-zum-verkaufsstart/2024Ford_ChargeAroundTheGlobe_FactSheet_EU.pdf
```

## 下一步优先处理

闭合剩余 12 个 Ktype：优先按代际批量处理 Explorer II、III 及早期 Explorer；随后单独处理 Bronco 两门、四门和宽体分支，以及 E-350 Cutaway 的不同轴距裸底盘外廓。

推进信号：CONTINUE

[1]: https://www.auto-doc.at/autoteile/steuerkette-10511/ford-usa/explorer/explorer-2010/54167-3-5-4wd?utm_source=chatgpt.com "Steuerkette FORD USA Explorer Mk5 (U502) 3.5 4WD 294 ..."


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 机械复核发现上一轮累计计数少计 1 个输入 Ktype：上一轮实际为 `89 / 100`，本轮闭合 8 个旧款 Explorer 后为 `97 / 100`。
* `59389`、`41205` 均属于 Explorer III `U152`，复用同一五门 SUV 外廓。Ford MY2003 官方资料给出 `189.5 × 72.1 × 71.4 in`。([AUTODOC][1])
* Explorer II `UN105` 按实际外廓变化拆成三个稳定阶段：

  * 1995–1997：`188.5 × 70.2 × 67.5 in`
  * 1998–1999：`189.5 × 70.2 × 67.5 in`
  * 2000–2001：`190.7 × 70.2 × 67.5 in`
* `10594`、`57899`、`8007` 覆盖三个外廓阶段；`127741`、`14433` 覆盖后两个阶段；`108689` 只覆盖 2000–2001 外廓。相关 Ktype 均归入 Explorer II `UN105`。([买汽车配件][2])

## 当前批次进度

* 已处理输入 Ktype：97 / 100
* READY 映射：370 行
* PENDING 输入 Ktype：3
* 已确认尺寸组：105 个
* 本轮首次创建尺寸组：4 个
* 剩余：`152107`、`52532`、`803197`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59389	59389	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-SUV-01	HIGH	U152 five-door exterior.	READY
127741_facelift98	127741	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
127741_facelift00	127741	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
41205	41205	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-SUV-01	HIGH	U152 five-door exterior.	READY
10594_prefl	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
10594_facelift98	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
10594_facelift00	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
14433_facelift98	14433	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
14433_facelift00	14433	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
57899_prefl	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
57899_facelift98	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
57899_facelift00	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
108689	108689	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	HIGH	2000-2001 exterior.	READY
8007_prefl	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
8007_facelift98	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
8007_facelift00	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-EXPLORER-III-SUV-01	4813	1831	1814	Ford Explorer official brochure MY2003	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2003.pdf
EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	4788	1783	1715	Ford Explorer official brochure MY1996	https://xr793.com/wp-content/uploads/2022/12/1996-Ford-Explorer.pdf
EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	4813	1783	1715	Ford Explorer official brochure MY1998	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_1998.pdf
EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	4844	1783	1715	Ford Explorer official brochure MY2000	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2000.pdf
```

## 下一步优先处理

闭合最后 3 个 Ktype：`152107` 按 Bronco VI 两门、四门及宽体外廓拆分；`52532` 建立 1995–1996 Bronco 五代三门组；`803197` 按 E-350 Cutaway 的不同轴距裸底盘分支闭合。完成后立即进行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/oil-filter-10359/ford-usa/explorer/explorer/59389-4-6?utm_source=chatgpt.com "FORD USA Explorer III Off-Road (U152) 4.6 Oil filter"
[2]: https://www.buycarparts.co.uk/ford-usa/explorer-u2/10594/10289/doors-parts?utm_source=chatgpt.com "Door parts for Ford Explorer U2 4.0 V6 4WD 207 hp Petrol"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6201-6300_ktype_dimension_mapping_final.tsv
- left18448_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 最后 3 个 Ktype 已闭合：`152107` 拆分为 Bronco VI 两门、四门及对应宽体分支；`52532` 映射至 Bronco V 三门外廓；`803197` 拆分为 E-350 Cutaway 的 138 英寸 SRW、138 英寸 DRW 和 158 英寸 DRW 分支。([福特之路][1])
* 已完成轻量机械检查：映射表严格为 10 列，尺寸组表严格为 6 列；`id`、`DIMENSION_GROUP_ID` 均唯一；所有映射引用闭合；不存在孤立尺寸组、空三维、空来源或 `PENDING`。
* 两个任务指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：378 行
* PENDING：0
* DIMENSION_GROUP：113 个
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58545_l1h1	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	MEDIUM	L1H1 物理外廓分支。	READY
58545_l1h2	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	MEDIUM	L1H2 物理外廓分支。	READY
58545_l2h1	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	MEDIUM	L2H1 物理外廓分支。	READY
58545_l2h2	58545	Van	Transit Custom V362			EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	MEDIUM	L2H2 物理外廓分支。	READY
152502_l1h1	152502	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152502_l2h1	152502	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152503_l1h1	152503	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152503_l2h1	152503	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152505_l1h1	152505	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152505_l2h1	152505	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152506_l1h1	152506	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152506_l2h1	152506	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156272_l1h1	156272	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156272_l2h1	156272	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156273_l1h1	156273	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156273_l2h1	156273	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156275_l1h1	156275	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156275_l2h1	156275	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156276_l1h1	156276	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156276_l2h1	156276	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152504_l1h1	152504	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152504_l2h1	152504	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
152507_l1h1	152507	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
152507_l2h1	152507	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156274_l1h1	156274	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156274_l2h1	156274	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156277_l1h1	156277	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156277_l2h1	156277	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156208_l1h1	156208	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156208_l2h1	156208	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156278_l1h1	156278	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156278_l2h1	156278	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156963_l1h1	156963	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156963_l2h1	156963	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156964_l1h1	156964	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156964_l2h1	156964	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156965_l1h1	156965	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156965_l2h1	156965	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
156967_l1h1	156967	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
156967_l2h1	156967	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
157679_l1h1	157679	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
157679_l2h1	157679	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802761_l1h1	802761	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802761_l2h1	802761	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802762_l1h1	802762	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802762_l2h1	802762	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802763_l1h1	802763	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802763_l2h1	802763	Van	Transit Custom V710	NRN		EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802764_l1h1	802764	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802764_l2h1	802764	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
802899_l1h1	802899	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	HIGH	L1H1 物理外廓分支。	READY
802899_l2h1	802899	MPV	Transit Custom V710	NXN		EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	HIGH	L2H1 物理外廓分支。	READY
144673_chassis_sc_l2_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
144673_chassis_sc_l3_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
144673_chassis_sc_l4_fwd_srw	144673	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
144673_pickup_sc_l2_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
144673_pickup_sc_l3_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
144673_pickup_sc_l4_fwd_srw	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
144673_chassis_dc_l2_fwd_srw	144673	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
144673_chassis_dc_l3_fwd_srw	144673	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
144673_pickup_dc_l2_fwd_srw	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
144673_pickup_dc_l3_fwd_srw	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
144674_l2h2	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
144674_l2h3	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
144674_l3h2	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
144674_l3h3	144674	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
145764_l2h2	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
145764_l2h3	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
145764_l3h2	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
145764_l3h3	145764	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
152699_l2h2	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
152699_l2h3	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
152699_l3h2	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
152699_l3h3	152699	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
152700_chassis_sc_l2_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
152700_chassis_sc_l3_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
152700_chassis_sc_l4_fwd_srw	152700	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
152700_pickup_sc_l2_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
152700_pickup_sc_l3_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
152700_pickup_sc_l4_fwd_srw	152700	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
152700_chassis_dc_l2_fwd_srw	152700	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
152700_chassis_dc_l3_fwd_srw	152700	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
152700_pickup_dc_l2_fwd_srw	152700	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
152700_pickup_dc_l3_fwd_srw	152700	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
155574_l2h2	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	MEDIUM	L2H2 FWD physical branch.	READY
155574_l2h3	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	MEDIUM	L2H3 FWD physical branch.	READY
155574_l3h2	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	MEDIUM	L3H2 FWD physical branch.	READY
155574_l3h3	155574	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	MEDIUM	L3H3 FWD physical branch.	READY
155576_chassis_sc_l2_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW chassis branch.	READY
155576_chassis_sc_l3_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW chassis branch.	READY
155576_chassis_sc_l4_fwd_srw	155576	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW chassis branch.	READY
155576_pickup_sc_l2_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	MEDIUM	Single-cab L2 FWD SRW dropside branch.	READY
155576_pickup_sc_l3_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	MEDIUM	Single-cab L3 FWD SRW dropside branch.	READY
155576_pickup_sc_l4_fwd_srw	155576	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	MEDIUM	Single-cab L4 FWD SRW dropside branch.	READY
155576_chassis_dc_l2_fwd_srw	155576	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW chassis branch.	READY
155576_chassis_dc_l3_fwd_srw	155576	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW chassis branch.	READY
155576_pickup_dc_l2_fwd_srw	155576	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	MEDIUM	Double-cab L2 FWD SRW dropside branch.	READY
155576_pickup_dc_l3_fwd_srw	155576	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	MEDIUM	Double-cab L3 FWD SRW dropside branch.	READY
155578_l2h2	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
155578_l2h3	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
155578_l3h2	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
155578_l3h3	155578	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
155575_l2h2	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	MEDIUM	L2H2 RWD/AWD physical branch.	READY
155575_l2h3	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	MEDIUM	L2H3 RWD/AWD physical branch.	READY
155575_l3h2	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	MEDIUM	L3H2 RWD/AWD physical branch.	READY
155575_l3h3	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	MEDIUM	L3H3 RWD/AWD physical branch.	READY
155575_l4h3_srw	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	MEDIUM	L4H3 RWD/AWD SRW physical branch.	READY
155575_l4h3_drw	155575	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	MEDIUM	L4H3 RWD/AWD DRW physical branch.	READY
155577_chassis_sc_l2_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 AWD SRW chassis branch.	READY
155577_chassis_sc_l3_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 AWD SRW chassis branch.	READY
155577_chassis_sc_l4_awd_srw	155577	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 AWD SRW chassis branch.	READY
155577_pickup_sc_l2_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 AWD SRW dropside branch.	READY
155577_pickup_sc_l3_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 AWD SRW dropside branch.	READY
155577_pickup_sc_l4_awd_srw	155577	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 AWD SRW dropside branch.	READY
155577_chassis_dc_l2_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 AWD SRW chassis branch.	READY
155577_chassis_dc_l3_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 AWD SRW chassis branch.	READY
155577_chassis_dc_l4_awd_srw	155577	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 AWD SRW chassis branch.	READY
155577_pickup_dc_l2_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 AWD SRW dropside branch.	READY
155577_pickup_dc_l3_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 AWD SRW dropside branch.	READY
155577_pickup_dc_l4_awd_srw	155577	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 AWD SRW dropside branch.	READY
145763_l2h2	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	MEDIUM	L2H2 FWD passenger-body branch.	READY
145763_l2h3	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	MEDIUM	L2H3 FWD passenger-body branch.	READY
145763_l3h2	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	MEDIUM	L3H2 FWD passenger-body branch.	READY
145763_l3h3	145763	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	MEDIUM	L3H3 FWD passenger-body branch.	READY
148379_chassis_sc_l2_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
148379_chassis_sc_l2_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
148379_chassis_sc_l3_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
148379_chassis_sc_l3_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
148379_chassis_sc_l4_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
148379_chassis_sc_l4_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
148379_chassis_sc_l5_rwd_srw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-SRW-01	MEDIUM	Single-cab L5 RWD SRW chassis branch.	READY
148379_chassis_sc_l5_rwd_drw	148379	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-DRW-01	MEDIUM	Single-cab L5 RWD DRW chassis branch.	READY
148379_pickup_sc_l2_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
148379_pickup_sc_l2_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
148379_pickup_sc_l3_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
148379_pickup_sc_l3_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
148379_pickup_sc_l4_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
148379_pickup_sc_l4_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
148379_pickup_sc_l5_rwd_srw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-SRW-01	MEDIUM	Single-cab L5 RWD SRW dropside branch.	READY
148379_pickup_sc_l5_rwd_drw	148379	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-DRW-01	MEDIUM	Single-cab L5 RWD DRW dropside branch.	READY
148379_chassis_dc_l2_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 RWD SRW chassis branch.	READY
148379_chassis_dc_l2_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-DRW-01	MEDIUM	Double-cab L2 RWD DRW chassis branch.	READY
148379_chassis_dc_l3_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 RWD SRW chassis branch.	READY
148379_chassis_dc_l3_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-DRW-01	MEDIUM	Double-cab L3 RWD DRW chassis branch.	READY
148379_chassis_dc_l4_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 RWD SRW chassis branch.	READY
148379_chassis_dc_l4_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-DRW-01	MEDIUM	Double-cab L4 RWD DRW chassis branch.	READY
148379_chassis_dc_l5_rwd_srw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-SRW-01	MEDIUM	Double-cab L5 RWD SRW chassis branch.	READY
148379_chassis_dc_l5_rwd_drw	148379	Chassis Cab	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-DRW-01	MEDIUM	Double-cab L5 RWD DRW chassis branch.	READY
148379_pickup_dc_l2_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	MEDIUM	Double-cab L2 RWD SRW dropside branch.	READY
148379_pickup_dc_l2_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-DRW-01	MEDIUM	Double-cab L2 RWD DRW dropside branch.	READY
148379_pickup_dc_l3_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	MEDIUM	Double-cab L3 RWD SRW dropside branch.	READY
148379_pickup_dc_l3_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-DRW-01	MEDIUM	Double-cab L3 RWD DRW dropside branch.	READY
148379_pickup_dc_l4_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	MEDIUM	Double-cab L4 RWD SRW dropside branch.	READY
148379_pickup_dc_l4_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-DRW-01	MEDIUM	Double-cab L4 RWD DRW dropside branch.	READY
148379_pickup_dc_l5_rwd_srw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-SRW-01	MEDIUM	Double-cab L5 RWD SRW dropside branch.	READY
148379_pickup_dc_l5_rwd_drw	148379	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-DRW-01	MEDIUM	Double-cab L5 RWD DRW dropside branch.	READY
152697_l2h2	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L2-H2-RWD-01	MEDIUM	L2H2 RWD passenger-body branch.	READY
152697_l3h2	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H2-RWD-01	MEDIUM	L3H2 RWD passenger-body branch.	READY
152697_l3h3	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L3-H3-RWD-01	MEDIUM	L3H3 RWD passenger-body branch.	READY
152697_l4h3_drw	152697	MPV	Transit V363			EU-FORD-TRANSIT-V363-MPV-L4-H3-RWD-DRW-01	MEDIUM	L4H3 RWD DRW passenger-body branch.	READY
152698_l2h2	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	MEDIUM	L2H2 RWD/AWD physical branch.	READY
152698_l2h3	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	MEDIUM	L2H3 RWD/AWD physical branch.	READY
152698_l3h2	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	MEDIUM	L3H2 RWD/AWD physical branch.	READY
152698_l3h3	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	MEDIUM	L3H3 RWD/AWD physical branch.	READY
152698_l4h3_srw	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	MEDIUM	L4H3 RWD/AWD SRW physical branch.	READY
152698_l4h3_drw	152698	Van	Transit V363			EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	MEDIUM	L4H3 RWD/AWD DRW physical branch.	READY
101104_l2h2	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101104_l2h3	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101104_l3h2	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101104_l3h3	101104	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101108_l2h2	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101108_l2h3	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101108_l3h2	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101108_l3h3	101108	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101110_l2h2	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift physical branch.	READY
101110_l2h3	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift physical branch.	READY
101110_l3h2	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift physical branch.	READY
101110_l3h3	101110	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift physical branch.	READY
101112_chassis_sc_l2	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101112_chassis_sc_l3	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101112_chassis_sc_l4	101112	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101112_pickup_sc_l2	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101112_pickup_sc_l3	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101112_pickup_sc_l4	101112	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
101114_chassis_sc_l2	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101114_chassis_sc_l3	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101114_chassis_sc_l4	101114	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101114_pickup_sc_l2	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101114_pickup_sc_l3	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101114_pickup_sc_l4	101114	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
101118_chassis_sc_l2	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 chassis branch.	READY
101118_chassis_sc_l3	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 chassis branch.	READY
101118_chassis_sc_l4	101118	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 chassis branch.	READY
101118_pickup_sc_l2	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 dropside branch.	READY
101118_pickup_sc_l3	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 dropside branch.	READY
101118_pickup_sc_l4	101118	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 dropside branch.	READY
107811_l2h2	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
107811_l2h3	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
107811_l3h2	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
107811_l3h3	107811	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
107814_l2h2	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
107814_l2h3	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
107814_l3h2	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
107814_l3h3	107814	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
115815_l2h2	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift passenger-body branch.	READY
115815_l2h3	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift passenger-body branch.	READY
115815_l3h2	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift passenger-body branch.	READY
115815_l3h3	115815	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift passenger-body branch.	READY
101103_l2h2	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift AWD branch.	READY
101103_l2h3	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift AWD branch.	READY
101103_l3h2	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift AWD branch.	READY
101103_l3h3	101103	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift AWD branch.	READY
101109_l2h2	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift AWD branch.	READY
101109_l2h3	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift AWD branch.	READY
101109_l3h2	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift AWD branch.	READY
101109_l3h3	101109	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift AWD branch.	READY
101117_chassis_sc_l2	101117	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD chassis branch.	READY
101117_chassis_sc_l3	101117	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD chassis branch.	READY
101117_pickup_sc_l2	101117	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD dropside branch.	READY
101117_pickup_sc_l3	101117	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD dropside branch.	READY
101122_chassis_sc_l2	101122	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD chassis branch.	READY
101122_chassis_sc_l3	101122	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD chassis branch.	READY
101122_pickup_sc_l2	101122	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 AWD dropside branch.	READY
101122_pickup_sc_l3	101122	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 AWD dropside branch.	READY
107819_l2h2	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	MEDIUM	L2H2 pre-facelift AWD passenger-body branch.	READY
107819_l2h3	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	MEDIUM	L2H3 pre-facelift AWD passenger-body branch.	READY
107819_l3h2	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	MEDIUM	L3H2 pre-facelift AWD passenger-body branch.	READY
107819_l3h3	107819	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	MEDIUM	L3H3 pre-facelift AWD passenger-body branch.	READY
101100_l3h2	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
101100_l3h3	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
101100_l4h3_drw	101100	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
101101_l3h2	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
101101_l3h3	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
101101_l4h3_drw	101101	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
101102_l2h2	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101102_l2h3	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101102_l3h2	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101102_l3h3	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101102_l4h3_srw	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101102_l4h3_drw	101102	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
101106_l2h2	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101106_l2h3	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101106_l3h2	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101106_l3h3	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101106_l4h3_srw	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101106_l4h3_drw	101106	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
101111_l2h2	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	HIGH	L2H2 pre-facelift RWD branch.	READY
101111_l2h3	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	HIGH	L2H3 pre-facelift RWD branch.	READY
101111_l3h2	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	HIGH	L3H2 pre-facelift RWD branch.	READY
101111_l3h3	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	HIGH	L3H3 pre-facelift RWD branch.	READY
101111_l4h3_srw	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	HIGH	L4H3 pre-facelift SRW branch.	READY
101111_l4h3_drw	101111	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	HIGH	L4H3 pre-facelift DRW branch.	READY
101113_chassis_sc_l1_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101113_chassis_sc_l2_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101113_chassis_sc_l2_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101113_chassis_sc_l3_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101113_chassis_sc_l3_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101113_chassis_sc_l4_srw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101113_chassis_sc_l4_drw	101113	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101113_pickup_sc_l1_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101113_pickup_sc_l2_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101113_pickup_sc_l2_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101113_pickup_sc_l3_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101113_pickup_sc_l3_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101113_pickup_sc_l4_srw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101113_pickup_sc_l4_drw	101113	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
101115_chassis_sc_l1_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101115_chassis_sc_l2_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101115_chassis_sc_l2_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101115_chassis_sc_l3_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101115_chassis_sc_l3_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101115_chassis_sc_l4_srw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101115_chassis_sc_l4_drw	101115	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101115_pickup_sc_l1_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101115_pickup_sc_l2_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101115_pickup_sc_l2_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101115_pickup_sc_l3_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101115_pickup_sc_l3_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101115_pickup_sc_l4_srw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101115_pickup_sc_l4_drw	101115	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
101119_chassis_sc_l1_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW chassis branch.	READY
101119_chassis_sc_l2_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW chassis branch.	READY
101119_chassis_sc_l2_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW chassis branch.	READY
101119_chassis_sc_l3_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW chassis branch.	READY
101119_chassis_sc_l3_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW chassis branch.	READY
101119_chassis_sc_l4_srw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW chassis branch.	READY
101119_chassis_sc_l4_drw	101119	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW chassis branch.	READY
101119_pickup_sc_l1_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	MEDIUM	Single-cab L1 RWD SRW dropside branch.	READY
101119_pickup_sc_l2_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	MEDIUM	Single-cab L2 RWD SRW dropside branch.	READY
101119_pickup_sc_l2_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	MEDIUM	Single-cab L2 RWD DRW dropside branch.	READY
101119_pickup_sc_l3_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	MEDIUM	Single-cab L3 RWD SRW dropside branch.	READY
101119_pickup_sc_l3_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	MEDIUM	Single-cab L3 RWD DRW dropside branch.	READY
101119_pickup_sc_l4_srw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	MEDIUM	Single-cab L4 RWD SRW dropside branch.	READY
101119_pickup_sc_l4_drw	101119	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	MEDIUM	Single-cab L4 RWD DRW dropside branch.	READY
107657_l3h2	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	MEDIUM	L3H2 RWD pre-facelift minibus branch.	READY
107657_l3h3	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	MEDIUM	L3H3 RWD pre-facelift minibus branch.	READY
107657_l4h3_drw	107657	MPV	Transit V363	V363		EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	MEDIUM	L4H3 RWD DRW pre-facelift minibus branch.	READY
147339_l2h2	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
147339_l2h3	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
147339_l3h2	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
147339_l3h3	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
147339_l4h3_srw	147339	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
147340_l2h2	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
147340_l2h3	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
147340_l3h2	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
147340_l3h3	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
147340_l4h3_srw	147340	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
147357_chassis_sc_l3	147357	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
147357_chassis_sc_l4	147357	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
147357_pickup_sc_l3	147357	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
147357_pickup_sc_l4	147357	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
147358_chassis_sc_l3	147358	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
147358_chassis_sc_l4	147358	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
147358_pickup_sc_l3	147358	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
147358_pickup_sc_l4	147358	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
802564_l2h2	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
802564_l2h3	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
802564_l3h2	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
802564_l3h3	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
802564_l4h3_srw	802564	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
802565_l2h2	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	HIGH	L2H2 electric van branch.	READY
802565_l2h3	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	HIGH	L2H3 electric van branch.	READY
802565_l3h2	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	HIGH	L3H2 electric van branch.	READY
802565_l3h3	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	HIGH	L3H3 electric van branch.	READY
802565_l4h3_srw	802565	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	HIGH	L4H3 SRW electric van branch.	READY
802566_chassis_sc_l3	802566	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
802566_chassis_sc_l4	802566	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
802566_pickup_sc_l3	802566	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
802566_pickup_sc_l4	802566	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
802567_chassis_sc_l3	802567	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric chassis branch.	READY
802567_chassis_sc_l4	802567	Chassis Cab	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric chassis branch.	READY
802567_pickup_sc_l3	802567	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	HIGH	Single-cab L3 electric dropside branch.	READY
802567_pickup_sc_l4	802567	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	HIGH	Single-cab L4 electric dropside branch.	READY
152107_2dr	152107	Convertible	Bronco VI		2	EU-FORD-USA-BRONCO-VI-CONVERTIBLE-2D-STANDARD-01	MEDIUM	Two-door standard-width removable-roof exterior.	READY
152107_2dr_widebody	152107	Convertible	Bronco VI		2	EU-FORD-USA-BRONCO-VI-CONVERTIBLE-2D-WIDEBODY-01	MEDIUM	Two-door widebody off-road exterior.	READY
152107_4dr	152107	Convertible	Bronco VI		4	EU-FORD-USA-BRONCO-VI-CONVERTIBLE-4D-STANDARD-01	MEDIUM	Four-door standard-width removable-roof exterior.	READY
152107_4dr_widebody	152107	Convertible	Bronco VI		4	EU-FORD-USA-BRONCO-VI-CONVERTIBLE-4D-WIDEBODY-01	MEDIUM	Four-door widebody off-road exterior.	READY
52532	52532	SUV	Bronco V		3	EU-FORD-USA-BRONCO-V-SUV-3D-01	HIGH	1995–1996 three-door exterior.	READY
803197_138_srw	803197	Van	E-Series III		2	EU-FORD-USA-E350-III-CUTAWAY-138-SRW-01	MEDIUM	138-inch wheelbase SRW commercial cutaway.	READY
803197_138_drw	803197	Van	E-Series III		2	EU-FORD-USA-E350-III-CUTAWAY-138-DRW-01	MEDIUM	138-inch wheelbase DRW commercial cutaway.	READY
803197_158_drw	803197	Van	E-Series III		2	EU-FORD-USA-E350-III-CUTAWAY-158-DRW-01	MEDIUM	158-inch wheelbase DRW commercial cutaway.	READY
109691	109691	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
122033	122033	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
57804	57804	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
54159	54159	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
122034	122034	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-NA-01	HIGH	North American second-generation exterior.	READY
117197	117197	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-EU-01	HIGH	European-market diesel exterior.	READY
117198	117198	SUV	Edge II	CD539	5	EU-FORD-USA-EDGE-II-SUV-EU-01	HIGH	European-market diesel exterior.	READY
57803	57803	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
57806	57806	SUV	Edge I pre-facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-PREFL-01	HIGH	First-generation pre-facelift exterior.	READY
50304	50304	SUV	Edge I facelift	U387	5	EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	HIGH	First-generation facelift exterior.	READY
41134	41134	SUV	Escape I facelift		5	EU-FORD-USA-ESCAPE-I-SUV-FACELIFT-01	HIGH	4WD hybrid exterior.	READY
59389	59389	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-SUV-01	HIGH	U152 five-door exterior.	READY
54167_prefl	54167	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	MEDIUM	Pre-facelift exterior branch.	READY
54167_facelift	54167	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	MEDIUM	Facelift exterior branch.	READY
107221_prefl	107221	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	MEDIUM	Pre-facelift exterior branch.	READY
107221_facelift	107221	SUV	Explorer V	U502	5	EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	MEDIUM	Facelift exterior branch.	READY
58109	58109	SUV	Explorer IV		5	EU-FORD-USA-EXPLORER-IV-SUV-01	HIGH	Fourth-generation exterior.	READY
127741_facelift98	127741	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
127741_facelift00	127741	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
41205	41205	SUV	Explorer III	U152	5	EU-FORD-USA-EXPLORER-III-SUV-01	HIGH	U152 five-door exterior.	READY
10594_prefl	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
10594_facelift98	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
10594_facelift00	10594	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
14433_facelift98	14433	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
14433_facelift00	14433	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
57899_prefl	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
57899_facelift98	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
57899_facelift00	57899	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
108689	108689	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	HIGH	2000-2001 exterior.	READY
8007_prefl	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	MEDIUM	1995-1997 exterior branch.	READY
8007_facelift98	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	MEDIUM	1998-1999 exterior branch.	READY
8007_facelift00	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	MEDIUM	2000-2001 exterior branch.	READY
158272	158272	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
158273	158273	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
800866	800866	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
803193	803193	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	HIGH	RWD electric exterior.	READY
158274	158274	SUV	Explorer EV I		5	EU-FORD-USA-EXPLORER-EV-I-SUV-AWD-01	HIGH	AWD electric exterior.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6201-6300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CUSTOM-V362-L1-H1-PREFL-01	4972	1986	2020	Ford Transit Custom official Body and Equipment Mounting Manual (2013 platform)	https://www.ford.co.kr/content/dam/Ford/website-assets/ap/au/owner/vehicle-support/body-equipment-manuals/2013_TransitCustom_FAPA_04_2017_BEMM.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L1-H2-PREFL-01	4972	1986	2389	Ford Transit Custom official Body and Equipment Mounting Manual (2013 platform)	https://www.ford.co.kr/content/dam/Ford/website-assets/ap/au/owner/vehicle-support/body-equipment-manuals/2013_TransitCustom_FAPA_04_2017_BEMM.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H1-PREFL-01	5339	1986	2017	Ford Transit Custom official Body and Equipment Mounting Manual (2013 platform)	https://www.ford.co.kr/content/dam/Ford/website-assets/ap/au/owner/vehicle-support/body-equipment-manuals/2013_TransitCustom_FAPA_04_2017_BEMM.pdf
EU-FORD-TRANSIT-CUSTOM-V362-L2-H2-PREFL-01	5339	1986	2381	Ford Transit Custom official Body and Equipment Mounting Manual (2013 platform)	https://www.ford.co.kr/content/dam/Ford/website-assets/ap/au/owner/vehicle-support/body-equipment-manuals/2013_TransitCustom_FAPA_04_2017_BEMM.pdf
EU-FORD-TRANSIT-CUSTOM-V710-VAN-L1-H1-01	5050	2032	2040	Ford Transit Custom official price list (Kastenwagen LKW)	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-neue-ford-transit-custom.pdf
EU-FORD-TRANSIT-CUSTOM-V710-VAN-L2-H1-01	5450	2032	2031	Ford Transit Custom official price list (Kastenwagen LKW)	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-neue-ford-transit-custom.pdf
EU-FORD-TRANSIT-CUSTOM-V710-MPV-L1-H1-01	5050	2032	2040	Ford Transit Custom Kombi PKW official price list	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-Ford-Transit-Custom-KombiPKW.pdf
EU-FORD-TRANSIT-CUSTOM-V710-MPV-L2-H1-01	5450	2032	2031	Ford Transit Custom Kombi PKW official price list	https://www.ford.de/content/dam/guxeu/de/documents/price-list/commercial-vehicles/transit-custom/PL-der-Ford-Transit-Custom-KombiPKW.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-FWD-SRW-01	5572	2052	2200	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-FWD-SRW-01	6022	2052	2194	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-FWD-SRW-01	6579	2052	2195	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-FWD-SRW-01	5767	2098	2200	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-FWD-SRW-01	6204	2098	2194	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-FWD-SRW-01	6797	2098	2195	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-FWD-SRW-01	5572	2066	2236	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-FWD-SRW-01	6022	2066	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-FWD-SRW-01	5767	2098	2236	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-FWD-SRW-01	6204	2098	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H2-FWD-01	5531	2059	2533	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-FWD-01	5531	2059	2769	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-FWD-01	5981	2059	2530	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-FWD-01	5981	2059	2767	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H2-FWD-01	5531	2059	2530	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H3-FWD-01	5531	2059	2766	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H2-FWD-01	5981	2059	2526	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-FWD-01	5981	2059	2762	Ford Transit official brochure (Kombi PKW M1 dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H2-RWD-AWD-01	5531	2059	2534	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-RWD-AWD-01	5531	2059	2771	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-RWD-AWD-01	5981	2059	2533	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-RWD-AWD-01	5981	2059	2769	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-SRW-01	6704	2059	2778	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-RWD-AWD-DRW-01	6704	2126	2778	Ford Transit official brochure (Van dimensions, 25.5MY)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit/ford-bro-transit_van_2025_ebroschure.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-SRW-01	5572	2052	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-SRW-01	6022	2052	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-SRW-01	6579	2052	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-SRW-01	5767	2098	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-SRW-01	6204	2098	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-SRW-01	6797	2098	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-SRW-01	5572	2066	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-SRW-01	6022	2066	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-SRW-01	6404	2066	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-SRW-01	5767	2098	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-SRW-01	6204	2098	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-SRW-01	6587	2098	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-RWD-AWD-DRW-01	5572	2111	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-RWD-AWD-DRW-01	6022	2111	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-RWD-AWD-DRW-01	6579	2111	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-SRW-01	7577	2052	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L5-RWD-AWD-DRW-01	7577	2111	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-RWD-AWD-DRW-01	5767	2198	2220	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-RWD-AWD-DRW-01	6204	2198	2214	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-RWD-AWD-DRW-01	6797	2198	2215	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-SRW-01	7797	2098	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L5-RWD-AWD-DRW-01	7797	2198	2208	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L2-RWD-AWD-DRW-01	5572	2111	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L3-RWD-AWD-DRW-01	6022	2111	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L4-RWD-AWD-DRW-01	6404	2111	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-SRW-01	7394	2066	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DC-L5-RWD-AWD-DRW-01	7394	2111	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L2-RWD-AWD-DRW-01	5767	2198	2241	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L3-RWD-AWD-DRW-01	6204	2198	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L4-RWD-AWD-DRW-01	6587	2198	2233	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-SRW-01	7612	2098	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-PICKUP-DC-L5-RWD-AWD-DRW-01	7612	2198	2230	Ford Transit Fahrgestell und Pritschenwagen official brochure (MY 2025.5)	https://www.ford.de/content/dam/guxeu/de/documents/brochures/commercial-vehicles/transit-fahrgestelle-und-pritschenwagen/BRO-ford_transit_fahrgestelle_pritschenwagen.pdf
EU-FORD-TRANSIT-V363-MPV-L2-H2-RWD-01	5531	2059	2484	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H2-RWD-01	5981	2059	2528	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-RWD-01	5981	2059	2764	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-MPV-L4-H3-RWD-DRW-01	6704	2126	2757	Ford Transit Minibus official brochure (25.5MY)	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H2-PREFL-01	5531	2059	2550	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L2-H3-PREFL-01	5531	2059	2789	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H2-PREFL-01	5981	2059	2547	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-VAN-L3-H3-PREFL-01	5981	2059	2786	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-SRW-01	5572	2052	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-SRW-01	6022	2052	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-SRW-01	6579	2052	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-SRW-01	5767	2098	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-SRW-01	6204	2098	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-SRW-01	6797	2098	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H2-PREFL-RWD-01	5981	2059	2517	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
EU-FORD-TRANSIT-V363-MPV-L3-H3-PREFL-RWD-01	5981	2059	2756	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
EU-FORD-TRANSIT-V363-MPV-L4-H3-PREFL-RWD-DRW-01	6704	2126	2674	Ford Transit Minibus official brochure	https://motorlib.carsireland.ie/brand-dealers/ford/commercials/brochures/Transit-Minibus.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-SRW-01	6704	2059	2781	Ford Transit official UK brochure MY2014; Ford Transit Cargo official New Zealand brochure	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf; https://www.forddealers.co.nz/i/files/transit_cargo_brochure.pdf
EU-FORD-TRANSIT-V363-VAN-L4-H3-PREFL-DRW-01	6704	2126	2781	Ford Transit official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Transit-Van-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L1-PREFL-SRW-01	5205	2052	2219	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L2-PREFL-DRW-01	5572	2111	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L3-PREFL-DRW-01	6022	2111	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SC-L4-PREFL-DRW-01	6579	2111	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L1-PREFL-SRW-01	5357	2098	2219	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L2-PREFL-DRW-01	5767	2198	2214	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L3-PREFL-DRW-01	6204	2198	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-TRANSIT-V363-PICKUP-SC-L4-PREFL-DRW-01	6797	2198	2207	Ford Transit Chassis Cabs official UK brochure MY2014	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Chassis-Cabs-UK.pdf
EU-FORD-USA-BRONCO-VI-CONVERTIBLE-2D-STANDARD-01	4412	1928	1826	Ford Bronco official technical specifications MY2025	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025-Ford-Bronco-Technical-Specifications.pdf
EU-FORD-USA-BRONCO-VI-CONVERTIBLE-2D-WIDEBODY-01	4412	2017	2004	Ford Bronco official technical specifications MY2025	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025-Ford-Bronco-Technical-Specifications.pdf
EU-FORD-USA-BRONCO-VI-CONVERTIBLE-4D-STANDARD-01	4811	1928	1854	Ford Bronco official technical specifications MY2025	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025-Ford-Bronco-Technical-Specifications.pdf
EU-FORD-USA-BRONCO-VI-CONVERTIBLE-4D-WIDEBODY-01	4811	2017	1999	Ford Bronco official technical specifications MY2025	https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025-Ford-Bronco-Technical-Specifications.pdf
EU-FORD-USA-BRONCO-V-SUV-3D-01	4663	2009	1890	Ford Bronco official brochure MY1996; Automobile-Catalog	https://www.auto-brochures.com/makes/Ford/Bronco/Ford_US%20Bronco_1996.pdf; https://www.automobile-catalog.com/car/1996/884915/ford_bronco_5_8l_efi_v-8_automatic.html
EU-FORD-USA-E350-III-CUTAWAY-138-SRW-01	5867	2029	2024	Ford Econoline official Chassis-Cab brochure MY1984	https://xr793.com/wp-content/uploads/2022/10/1984-Ford-Chassis-Cab.pdf
EU-FORD-USA-E350-III-CUTAWAY-138-DRW-01	5867	2029	1986	Ford Econoline official Chassis-Cab brochure MY1984	https://xr793.com/wp-content/uploads/2022/10/1984-Ford-Chassis-Cab.pdf
EU-FORD-USA-E350-III-CUTAWAY-158-DRW-01	6375	2029	1989	Ford Econoline official Chassis-Cab brochure MY1984	https://xr793.com/wp-content/uploads/2022/10/1984-Ford-Chassis-Cab.pdf
EU-FORD-USA-EDGE-II-SUV-NA-01	4779	1928	1742	Ford Edge official brochure MY2015	https://www.cityfordsales.com/new/2016/pdfs/2015-ford-edge.pdf
EU-FORD-USA-EDGE-I-SUV-FACELIFT-01	4679	1930	1702	Ford Edge official brochure MY2011	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Edge-2011.pdf
EU-FORD-USA-EDGE-II-SUV-EU-01	4808	1928	1692	Ford Edge official UK brochure MY2017	https://www.winfordroadgarages.co.uk/pdf/edge.pdf
EU-FORD-USA-EDGE-I-SUV-PREFL-01	4717	1925	1702	Ford Edge official brochures MY2008/MY2010	https://xr793.com/wp-content/uploads/2016/10/2008-Ford-Edge.pdf; https://www.centuryu.com/uploads/1/4/4/6/144698822/2010_edge.pdf
EU-FORD-USA-ESCAPE-I-SUV-FACELIFT-01	4442	1780	1784	Ford Escape HEV official owner guide MY2005	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/05hevog1e.pdf
EU-FORD-USA-EXPLORER-III-SUV-01	4813	1831	1814	Ford Explorer official brochure MY2003	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2003.pdf
EU-FORD-USA-EXPLORER-V-SUV-PREFL-01	5006	2004	1788	Ford Explorer official brochure MY2011	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2011.pdf
EU-FORD-USA-EXPLORER-V-SUV-FACELIFT-01	5047	2004	1778	Ford Explorer official brochure MY2019	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2019.pdf
EU-FORD-USA-EXPLORER-IV-SUV-01	4912	1872	1849	Ford Explorer official brochure MY2009	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2009.pdf
EU-FORD-USA-EXPLORER-II-SUV-FACELIFT98-01	4813	1783	1715	Ford Explorer official brochure MY1998	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_1998.pdf
EU-FORD-USA-EXPLORER-II-SUV-FACELIFT00-01	4844	1783	1715	Ford Explorer official brochure MY2000	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_2000.pdf
EU-FORD-USA-EXPLORER-II-SUV-PREFL-01	4788	1783	1715	Ford Explorer official brochure MY1996	https://xr793.com/wp-content/uploads/2022/12/1996-Ford-Explorer.pdf
EU-FORD-USA-EXPLORER-EV-I-SUV-RWD-01	4468	1871	1630	Ford All-Electric Explorer official fact sheet	https://www.fromtheroad.ford.com/content/dam/fordmediasite/at/de/library/2024/neuer-vollelektrischer-ford-explorer--weltrekord-zum-verkaufsstart/2024Ford_ChargeAroundTheGlobe_FactSheet_EU.pdf
EU-FORD-USA-EXPLORER-EV-I-SUV-AWD-01	4468	1871	1639	Ford All-Electric Explorer official fact sheet	https://www.fromtheroad.ford.com/content/dam/fordmediasite/at/de/library/2024/neuer-vollelektrischer-ford-explorer--weltrekord-zum-verkaufsstart/2024Ford_ChargeAroundTheGlobe_FactSheet_EU.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6201-6300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2025/specs/2025-Ford-Bronco-Technical-Specifications.pdf "2025 Bronco Tech Specs"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3190 行）
- 累计尺寸组：dimension_groups_final.tsv（752 行）

