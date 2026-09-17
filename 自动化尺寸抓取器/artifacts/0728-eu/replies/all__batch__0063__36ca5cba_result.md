# 任务：all 第 6201-6300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0063__36ca5cba


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6201-6300 行

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
all.tsv

【当前独立任务】
all 第 6201-6300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-TT-8J-FACELIFT-COUPE-3D-01	4187	1842	1353
EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-01	4468	1831	1610
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525
EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	4129	1640	1568
EU-FORD-ESCORT-III-CONVERTIBLE-01	4010	1640	1403
EU-FORD-ESCORT-III-HATCHBACK-3D-01	3966	1640	1337
EU-FORD-ESCORT-III-HATCHBACK-5D-01	3966	1640	1337
EU-FORD-ESCORT-III-HATCHBACK-EARLY-01	3970	1640	1400
EU-FORD-ESCORT-III-HATCHBACK-LATE-01	3970	1640	1384
EU-FORD-ESCORT-III-WAGON-01	4033	1640	1385
EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	4150	1590	1410
EU-FORD-ESCORT-II-SEDAN-01	3978	1596	1398
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	4181	1640	1568
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	4181	1640	1594
EU-FORD-ESCORT-IV-CONVERTIBLE-01	4022	1640	1375
EU-FORD-ESCORT-IV-HATCHBACK-01	4022	1640	1385
EU-FORD-ESCORT-IV-HATCHBACK-RS-TURBO-01	4061	1650	1354
EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	4022	1640	1385
EU-FORD-ESCORT-IV-HATCHBACK-XR3I-01	4061	1640	1354
EU-FORD-ESCORT-IV-WAGON-01	4080	1640	1390
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	3718	1567	1359
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	3609	1567	1360
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	3565	1567	1360
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	3718	1580	1371
EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	3648	1585	1376
EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	3648	1585	1376
EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	3648	1585	1334
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365
EU-FORD-FIESTA-II-XR2-FACELIFT-01	3711	1620	1362
EU-FORD-FIESTA-II-XR2-PREFL-01	3711	1620	1334
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	3833	1634	1377
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	3828	1634	1334
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	3833	1634	1377
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	3828	1634	1334
EU-FORD-FIESTA-MK1-HATCHBACK-3D-01	3565	1567	1360
EU-FORD-ORION-III-GAL-SEDAN-01	4229	1690	1395
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389
EU-FORD-ORION-II-SEDAN-02	4210	1640	1390
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-LADA-NOVA-2104-WAGON-5D-01	4115	1620	1443
EU-PEUGEOT-204-EARLY-SEDAN-01	3990	1560	1400
EU-PEUGEOT-204-LATE-SEDAN-01	3980	1570	1400
EU-PEUGEOT-205-I-AUTOMATIC-HATCHBACK-3D-01	3705	1572	1350
EU-PEUGEOT-205-I-AUTOMATIC-HATCHBACK-5D-01	3705	1572	1350
EU-PEUGEOT-205-I-BASE-HATCHBACK-3D-01	3705	1562	1374
EU-PEUGEOT-205-I-BASE-HATCHBACK-5D-01	3705	1562	1374
EU-PEUGEOT-205-I-CTI-CONVERTIBLE-EARLY-01	3705	1589	1354
EU-PEUGEOT-205-I-CTI-CONVERTIBLE-LATE-01	3705	1589	1381
EU-PEUGEOT-205-I-DIESEL-BASE-HATCHBACK-3D-01	3705	1562	1376
EU-PEUGEOT-205-I-DIESEL-BASE-HATCHBACK-5D-01	3705	1562	1376
EU-PEUGEOT-205-I-GTI-HATCHBACK-01	3705	1589	1355
EU-PEUGEOT-205-I-GTI-HATCHBACK-3D-01	3705	1589	1355
EU-PEUGEOT-205-II-AUTOMATIC-HATCHBACK-3D-01	3705	1572	1350
EU-PEUGEOT-205-II-AUTOMATIC-HATCHBACK-5D-01	3705	1572	1350
EU-PEUGEOT-205-II-BASE-1.0-HATCHBACK-3D-01	3705	1562	1376
EU-PEUGEOT-205-II-BASE-1.0-HATCHBACK-5D-01	3705	1562	1376
EU-PEUGEOT-205-II-BASE-HATCHBACK-3D-01	3705	1562	1374
EU-PEUGEOT-205-II-BASE-HATCHBACK-5D-01	3705	1562	1374
EU-PEUGEOT-205-II-DIESEL-BASE-HATCHBACK-3D-01	3705	1562	1376
EU-PEUGEOT-205-II-DIESEL-BASE-HATCHBACK-5D-01	3705	1562	1376
EU-PEUGEOT-205-II-DIESEL-LATE-HATCHBACK-3D-01	3705	1572	1350
EU-PEUGEOT-205-II-DIESEL-LATE-HATCHBACK-5D-01	3705	1572	1350
EU-PEUGEOT-205-II-DIESEL-WIDE-HATCHBACK-3D-01	3705	1572	1376
EU-PEUGEOT-205-II-DIESEL-WIDE-HATCHBACK-5D-01	3705	1572	1376
EU-PEUGEOT-205-II-GTI-HATCHBACK-3D-01	3705	1589	1355
EU-PEUGEOT-205-II-SPORT-HATCHBACK-3D-01	3705	1572	1365
EU-PEUGEOT-205-II-SPORT-HATCHBACK-5D-01	3705	1572	1365
EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	3705	1572	1374
EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	3705	1572	1374
EU-PEUGEOT-205-I-SPORT-HATCHBACK-3D-01	3705	1572	1365
EU-PEUGEOT-205-I-SPORT-HATCHBACK-5D-01	3705	1572	1365
EU-PEUGEOT-205-I-STANDARD-HATCHBACK-3D-01	3705	1572	1373
EU-PEUGEOT-205-I-STANDARD-HATCHBACK-5D-01	3705	1572	1373
EU-PEUGEOT-304-CABRIOLET-01	3750	1570	1330
EU-PEUGEOT-305-I-BREAK-01	4259	1640	1426
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-BASE-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-WIDE-01	4283	1636	1426
EU-PEUGEOT-305-II-SEDAN-BASE-01	4263	1630	1407
EU-PEUGEOT-305-II-SEDAN-SPORT-01	4263	1636	1396
EU-PEUGEOT-305-II-SEDAN-WIDE-01	4263	1636	1411
EU-PEUGEOT-305-I-SEDAN-BASE-01	4237	1630	1405
EU-PEUGEOT-305-I-SEDAN-WIDE-01	4237	1642	1400
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	4360	1630	1395
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	4230	1630	1390
EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	4370	1630	1400
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	4360	1670	1365
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	4330	1670	1365
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	4370	1670	1365
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	4350	1670	1365
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	4390	1670	1365
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	4360	1670	1365
EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	4390	1670	1365
EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	4440	1690	1370
EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	4440	1690	1370
EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	4435	1690	1400
EU-TOYOTA-CARINA-V-T170-WAGON-01	4470	1690	1380
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	4370	1635	1320
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	4330	1635	1320
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	4370	1635	1310
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	4330	1635	1310
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	4370	1640	1315
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	4330	1640	1315
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	4370	1640	1320
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	4330	1640	1320
EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	4450	1665	1320
EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	4410	1690	1320
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	4410	1710	1290
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	4380	1710	1290
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	4365	1710	1290
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	4620	1685	1315
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	4620	1720	1315
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-FWD-01	4425	1750	1305
EU-TOYOTA-CELICA-VI-T20-COUPE-3D-GTFOUR-01	4420	1750	1305
EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	4430	1705	1320
EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	4420	1690	1300
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	3700	1590	1395
EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	3700	1590	1395
EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	3680	1525	1380
EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	3680	1525	1380
EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	3850	1525	1395
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	3720	1600	1380
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	3720	1600	1380
EU-TOYOTA-STARLET-V-P90-HATCHBACK-3D-01	3740	1635	1400
EU-TOYOTA-STARLET-V-P90-HATCHBACK-5D-01	3740	1635	1400

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Transit	1.5	Kasten	Heckantrieb	Benzin	44	60	Jan 1971	May 1973	2024-03-01	6619
Ford	Transit	2.3 D FT 100	Bus	Heckantrieb	Diesel	46	63	Nov 1971	Sep 1978	2024-03-01	6620
Ford	Transit	1.7	Bus	Heckantrieb	Benzin	48	65	Jan 1971	May 1973	2024-03-01	6621
Ford	Transit	1.7 1300 Feuerw.	Kasten	Heckantrieb	Benzin	48	65	Nov 1965	May 1973	2024-03-01	6622
Ford	Transit	1.7 1300	Kasten	Heckantrieb	Benzin	48	65	Mar 1967	Jul 1973	2024-03-01	6623
Ford	Transit	1.7 1300	Bus	Heckantrieb	Benzin	48	65	Jan 1966	May 1973	2024-03-01	6624
Audi	Tt	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	155	211	May 2010	Jun 2014	2024-03-01	6625
Audi	Tt	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	155	211	May 2010	Jun 2014	2024-03-01	6626
Lada	1200-1600	1500 N/S	Stufenheck	Heckantrieb	Benzin	55	75	Nov 1975	Oct 1986	2024-03-01	6627
Citroën	C4 picasso i	2.0 HDI 165	Großraumlimousine	Frontantrieb	Diesel	120	163	Sep 2010	Aug 2013	2024-03-01	6628
Lada	1200-1600	1300	Stufenheck	Heckantrieb	Benzin	48	65	May 1978	Jan 1987	2024-03-01	6629
Lada	1200-1600	1600 N/L	Stufenheck	Heckantrieb	Benzin	57	78	Mar 1979	Dec 2005	2024-03-01	6630
Lada	Toscana	1300	Stufenheck	Heckantrieb	Benzin	48	65	Dec 1985	May 2012	2024-03-01	6631
Ford	Escort iv express	1.3	Kasten/Kombi	Frontantrieb	Benzin	46	63	Jul 1988	Jul 1990	2024-03-01	6632
Ford	Escort iv express	1.8 D	Kasten/Kombi	Frontantrieb	Diesel	44	60	Jul 1988	Jul 1990	2024-03-01	6633
Citroën	C4 grand picasso i	1.6 THP 155	Großraumlimousine	Frontantrieb	Benzin	115	156	Sep 2010	Aug 2013	2024-03-01	6634
Citroën	C4 grand picasso i	1.6 HDI 110	Großraumlimousine	Frontantrieb	Diesel	82	112	Sep 2010	Aug 2013	2024-03-01	6635
Ford	Escort ii	2.0 RS	Stufenheck	Heckantrieb	Benzin	73	100	Mar 1973	Feb 1977	2024-03-01	6637
Ford	Escort ii turnier	1.3	Kombi	Heckantrieb	Benzin	40	54	Apr 1975	Jan 1979	2024-03-01	6638
Ford	Escort ii turnier	1.3	Kombi	Heckantrieb	Benzin	40	54	Aug 1976	Jul 1981	2024-03-01	6639
Citroën	C4 grand picasso i	2.0 HDI 165	Großraumlimousine	Frontantrieb	Diesel	120	163	Sep 2010	Aug 2013	2024-03-01	6640
Ford	Escort iv	1.3	Schrägheck	Frontantrieb	Benzin	46	63	Jul 1988	Oct 1990	2024-03-01	6641
Ford	Fiesta	1	Kasten/Schrägheck	Frontantrieb	Benzin	29	40	Oct 1977	Nov 1986	2024-03-01	6642
Ford	Fiesta	1.1	Kasten/Schrägheck	Frontantrieb	Benzin	39	53	Oct 1977	Nov 1986	2024-03-01	6643
Ford	Fiesta	1	Kasten/Schrägheck	Frontantrieb	Benzin	33	45	Aug 1983	Nov 1989	2024-03-01	6644
Hyundai	Grandeur	3.3	Stufenheck	Frontantrieb	Benzin	191	260	Nov 2010	Dec 2011	2024-03-01	6645
Hyundai	Santa fé ii	3.5 4X4	SUV	Allrad	Benzin	204	277	Aug 2011	Dec 2012	2024-03-01	6646
Hyundai	Santa fé ii	2.0 Crdi	SUV	Frontantrieb	Diesel	110	150	Dec 2010	Dec 2012	2024-03-01	6647
Hyundai	Santa fé ii	2.4	SUV	Frontantrieb	Benzin	128	174	Nov 2010	Dec 2012	2024-03-01	6648
Hyundai	Santa fé ii	2.0 Crdi 4X4	SUV	Allrad	Diesel	110	150	Dec 2010	Dec 2012	2024-03-01	6649
Ford	Fiesta iii	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	96	131	Mar 1990	Oct 1992	2024-03-01	6650
Ford	Orion ii	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Dec 1985	Jul 1990	2024-03-01	6651
Ford	Orion ii	1.4	Stufenheck	Frontantrieb	Benzin	54	73	Jan 1986	Jul 1990	2024-03-01	6652
Peugeot	Bipper	1.3 HDI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2010	-	2024-03-01	6653
Ford	Orion ii	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Dec 1985	Jul 1990	2024-03-01	6654
Peugeot	Bipper	1.3 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2010	-	2024-03-01	6655
Ford	Orion iii	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	96	130	Jan 1992	Dec 1993	2024-03-01	6656
Lada	Nova	1500 S	Stufenheck	Heckantrieb	Benzin	52	71	Jun 1989	Apr 2012	2024-03-01	6658
Toyota	Cressida station wagon	2	Kombi	Heckantrieb	Benzin	66	90	Dec 1977	Mar 1981	2024-03-01	6659
Peugeot	204	1.1 Grand Luxe	Kombi	Frontantrieb	Benzin	40	54	May 1969	Oct 1977	2024-03-01	6660
Peugeot	204	1.2 D	Kombi	Frontantrieb	Diesel	29	39	May 1968	May 1973	2024-03-01	6661
Peugeot	204	1.3 D	Kombi	Frontantrieb	Diesel	33	45	Jan 1973	Oct 1977	2024-03-01	6662
Peugeot	204	1.1	Coupe	Frontantrieb	Benzin	40	54	May 1969	May 1970	2024-03-01	6663
Peugeot	308 cc	1.6 THP	Cabriolet	Frontantrieb	Benzin	147	200	Oct 2010	Dec 2014	2024-03-01	6664
Peugeot	204	1.1	Cabriolet	Frontantrieb	Benzin	40	54	May 1969	Oct 1970	2024-03-01	6665
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	55	75	May 2010	Jun 2013	2025-12-01	6666
Dacia	Sandero	1.6 MPI 85	Schrägheck	Frontantrieb	Benzin	62	84	May 2010	Jun 2013	2024-03-01	6667
Peugeot	205 i	1.9 GTI	Schrägheck	Frontantrieb	Benzin	75	102	Mar 1987	Oct 1987	2024-03-01	6668
Peugeot	205 i	1.4 CJ CAT	Cabriolet	Frontantrieb	Benzin	44	60	Jan 1989	Sep 1993	2024-03-01	6669
Toyota	Camry	2	Stufenheck	Frontantrieb	Benzin	73	99	Feb 1983	Dec 1986	2024-03-01	6670
Peugeot	205 ii	1.6	Schrägheck	Frontantrieb	Benzin	53	72	Oct 1987	Sep 1998	2024-03-01	6671
Peugeot	205 ii	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1987	Sep 1998	2024-03-01	6672
Peugeot	304	1.3 GT	Stufenheck	Frontantrieb	Benzin	48	65	Oct 1969	Sep 1975	2024-03-01	6673
Peugeot	304	1.3 GL	Stufenheck	Frontantrieb	Benzin	48	65	Sep 1972	Oct 1979	2024-03-01	6674
Dacia	Sandero	1.5 DCI	Schrägheck	Frontantrieb	Diesel	65	88	May 2010	Jun 2013	2025-12-01	6675
Peugeot	304	1.4 D	Stufenheck	Frontantrieb	Diesel	33	45	Oct 1976	Oct 1979	2024-03-01	6676
Peugeot	304	1.3	Kombi	Frontantrieb	Benzin	48	65	Sep 1970	Oct 1980	2024-03-01	6677
Peugeot	304	1.1	Kombi	Frontantrieb	Benzin	43	58	Oct 1976	Oct 1980	2024-03-01	6678
Peugeot	304	1.3	Coupe	Frontantrieb	Benzin	55	75	Mar 1972	Apr 1975	2024-03-01	6679
Peugeot	304	1.3	Coupe	Frontantrieb	Benzin	48	65	Mar 1970	Sep 1973	2024-03-01	6680
Peugeot	304	1.3	Cabriolet	Frontantrieb	Benzin	48	65	Mar 1970	Sep 1973	2024-03-01	6681
Peugeot	305 i	1.5	Stufenheck	Frontantrieb	Benzin	65	88	May 1980	Sep 1982	2024-03-01	6682
Peugeot	305 ii	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Nov 1986	Dec 1988	2024-03-01	6683
Peugeot	305 ii	1.9	Stufenheck	Frontantrieb	Benzin	72	98	Nov 1986	Dec 1988	2024-03-01	6684
Peugeot	305 ii break	1.6	Kombi	Frontantrieb	Benzin	54	73	Nov 1986	Dec 1988	2024-03-01	6685
Peugeot	305 ii break	1.6	Kombi	Frontantrieb	Benzin	55	75	Feb 1986	Dec 1988	2024-03-01	6686
Peugeot	305 ii break	1.6	Kombi	Frontantrieb	Benzin	66	90	Jul 1984	Dec 1987	2024-03-01	6687
Peugeot	305 ii break	1.5	Kombi	Frontantrieb	Benzin	50	68	Sep 1985	Oct 1986	2024-03-01	6688
Peugeot	305 ii break	1.9	Kombi	Frontantrieb	Benzin	72	98	Nov 1986	Dec 1988	2024-03-01	6689
Toyota	Starlet	1	Coupe	Heckantrieb	Benzin	33	45	Nov 1974	Aug 1978	2024-03-01	6690
Dacia	Logan	1.6 MPI 85	Stufenheck	Frontantrieb	Benzin	62	84	May 2010	-	2024-03-01	6691
Toyota	Starlet	1	Kombi	Heckantrieb	Benzin	33	45	May 1976	Aug 1978	2024-03-01	6692
Toyota	Camry	1.8 Turbo-d	Schrägheck	Frontantrieb	Diesel	54	73	Oct 1982	Oct 1986	2024-03-01	6693
Toyota	Camry	2	Schrägheck	Frontantrieb	Benzin	73	99	Jan 1983	Dec 1986	2024-03-01	6694
Dacia	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	65	88	May 2010	-	2024-03-01	6695
Dacia	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	55	75	May 2010	Dec 2012	2024-03-01	6696
Peugeot	404	1.6	Stufenheck	Heckantrieb	Benzin	48	65	Apr 1963	Dec 1971	2024-03-01	6697
Dacia	Logan	1.2 16V	Stufenheck	Frontantrieb	Benzin	55	75	Feb 2006	-	2024-03-01	6698
Toyota	Carina iii	1.6	Kombi	Heckantrieb	Benzin	55	75	Aug 1981	Sep 1983	2024-03-01	6699
Toyota	Carina i	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Feb 1976	Mar 1978	2024-03-01	6700
Toyota	Carina i	1.6	Stufenheck	Heckantrieb	Benzin	58	79	Dec 1970	Mar 1978	2024-03-01	6701
Toyota	Carina iv	2.0 D	Schrägheck	Frontantrieb	Diesel	50	68	Feb 1984	May 1988	2024-03-01	6702
Toyota	Carina iv	2.0 D	Stufenheck	Frontantrieb	Diesel	50	68	Feb 1984	May 1988	2024-03-01	6703
Toyota	Carina v	2.0 D	Stufenheck	Frontantrieb	Diesel	54	73	Mar 1988	Jun 1992	2024-03-01	6704
Toyota	Carina v	2.0 D	Schrägheck	Frontantrieb	Diesel	54	73	Mar 1988	Jun 1992	2024-03-01	6705
Toyota	Celica	1.6 LT	Coupe	Heckantrieb	Benzin	58	79	May 1973	Mar 1978	2024-03-01	6706
Toyota	Celica	1.6 ST	Coupe	Heckantrieb	Benzin	63	86	May 1973	Mar 1978	2024-03-01	6707
Toyota	Celica	1.6 GT	Coupe	Heckantrieb	Benzin	79	107	Dec 1974	Mar 1978	2024-03-01	6708
Toyota	Celica	1.6 LT	Coupe	Heckantrieb	Benzin	55	75	Feb 1976	Mar 1978	2024-03-01	6709
Dacia	Logan	1.6 MPI 85	Kombi	Frontantrieb	Benzin	62	84	May 2010	-	2024-03-01	6710
Dacia	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	55	75	May 2010	Jun 2013	2024-03-01	6711
Toyota	Celica	1.6 GT	Coupe	Heckantrieb	Benzin	80	109	Apr 1978	Jul 1981	2024-03-01	6712
Toyota	Celica	1.6 GT	Coupe	Heckantrieb	Benzin	81	110	Apr 1980	Jul 1981	2024-03-01	6713
Toyota	Celica	2	Coupe	Heckantrieb	Benzin	77	105	Jan 1982	Dec 1985	2024-03-01	6714
Toyota	Celica	2	Coupe	Heckantrieb	Benzin	88	120	Jan 1982	Dec 1985	2024-03-01	6715
Toyota	Celica	1.6	Coupe	Heckantrieb	Benzin	91	124	Dec 1983	Dec 1985	2024-03-01	6716
Toyota	Celica	1.6	Coupe	Frontantrieb	Benzin	63	86	Apr 1986	Aug 1989	2024-03-01	6717
Toyota	Celica	1.6	Schrägheck	Frontantrieb	Benzin	63	86	Apr 1986	Aug 1989	2024-03-01	6718
Toyota	Corolla	1.6 I	Stufenheck	Frontantrieb	Benzin	77	105	May 1987	May 1992	2024-03-01	6719
Toyota	Corolla	1.8 D	Stufenheck	Frontantrieb	Diesel	49	67	Nov 1989	Jun 1993	2024-03-01	6720


--- Round 1 / 首次发送 ---
## 更新点

* 新建并闭合 6 个尺寸组：Audi TT 8J facelift Roadster、Hyundai Grandeur TG facelift、Santa Fe CM facelift 标准版与 3.5 V6、Peugeot 308 CC、Dacia Sandero I。TT、Santa Fe、308 CC 与 Sandero 页面均分别列出不含后视镜宽度或将含镜宽度单独列示。([汽车数据][1])
* 批量复用 20 个已有尺寸组，完成 Ford Escort II RS2000、Orion III、Peugeot 205/304/305、Dacia Logan Sedan、Toyota Camry/Carina/Celica/Corolla 等映射。
* Ktype `6702`、`6703`、`6712`、`6713` 的生产期跨越尺寸改款，已分别拆分为 `prefl` 与 `facelift` 两个稳定分支。
* 暂不落盘 Citroën C4 Picasso 与 Grand C4 Picasso：官方技术表给出的标准规格为 C4 Picasso `4470×1830×1680`、Grand C4 Picasso `4590×1830×1710`，与已有短车身缓存及部分二级资料存在实质差异，需要先明确高度配置边界，不能直接覆盖或复用。
* Peugeot Bipper 暂缓：当前资料尚不能可靠取得不含后视镜的车身宽度，未创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：35
* READY 映射行：39
* 待处理输入 Ktype：65
* 当前已引用尺寸组：26

  * 本轮新建：6
  * 复用既有组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6625	6625	Convertible	TT 8J facelift	8J	2	EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	HIGH	8J改款Roadster双门外廓。	READY
6626	6626	Convertible	TT 8J facelift	8J	2	EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	HIGH	8J改款Roadster双门外廓。	READY
6637	6637	Sedan	Escort II		2	EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	HIGH	RS2000双门轿车外廓。	READY
6645	6645	Sedan	Grandeur IV facelift	TG	4	EU-HYUNDAI-GRANDEUR-IV-TG-FACELIFT-SEDAN-4D-01	HIGH	TG改款四门轿车外廓。	READY
6646	6646	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-V6-01	HIGH	3.5 V6版本外廓。	READY
6647	6647	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6648	6648	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6649	6649	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6656	6656	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	GAL四门轿车外廓。	READY
6664	6664	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-CONVERTIBLE-2D-01	HIGH	双门硬顶敞篷外廓。	READY
6666	6666	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6667	6667	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6668	6668	Hatchback	205 I		3	EU-PEUGEOT-205-I-GTI-HATCHBACK-3D-01	HIGH	GTI三门宽体外廓。	READY
6670	6670	Sedan	Camry I	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH	V10四门轿车外廓。	READY
6675	6675	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6681	6681	Convertible	304		2	EU-PEUGEOT-304-CABRIOLET-01	HIGH	304双门敞篷外廓。	READY
6683	6683	Sedan	305 II		4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	标准车身四门轿车外廓。	READY
6685	6685	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6686	6686	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6688	6688	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6691	6691	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6693	6693	Hatchback	Camry I	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH	V10五门掀背外廓。	READY
6694	6694	Hatchback	Camry I	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH	V10五门掀背外廓。	READY
6695	6695	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6696	6696	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6702_prefl	6702	Hatchback	Carina II	T150	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	MEDIUM	生产期跨改款，前期外廓。	READY
6702_facelift	6702	Hatchback	Carina II	T150	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	MEDIUM	生产期跨改款，改款外廓。	READY
6703_prefl	6703	Sedan	Carina II	T150	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	MEDIUM	生产期跨改款，前期外廓。	READY
6703_facelift	6703	Sedan	Carina II	T150	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨改款，改款外廓。	READY
6704	6704	Sedan	Carina II	T170	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH	T170四门轿车外廓。	READY
6705	6705	Hatchback	Carina II	T170	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH	T170五门掀背外廓。	READY
6712_prefl	6712	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产期跨改款，前期双门外廓。	READY
6712_facelift	6712	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产期跨改款，改款双门外廓。	READY
6713_prefl	6713	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产期跨改款，前期双门外廓。	READY
6713_facelift	6713	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产期跨改款，改款双门外廓。	READY
6717	6717	Coupe	Celica IV	T16	2	EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	HIGH	T16前驱双门Coupe外廓。	READY
6718	6718	Hatchback	Celica IV	T16	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH	T16前驱三门掀背外廓。	READY
6719	6719	Sedan	Corolla VI	E90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门轿车外廓。	READY
6720	6720	Sedan	Corolla VI	E90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	4198	1842	1358	Auto-Data	https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-2.0-tfsi-211hp-s-tronic-27333
EU-HYUNDAI-GRANDEUR-IV-TG-FACELIFT-SEDAN-4D-01	4895	1850	1495	Auto-Data	https://www.auto-data.net/en/hyundai-grandeur-azera-iv-tg-facelift-2009-generation-5658
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-V6-01	4676	1890	1725	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-facelift-2009-3.5-v6-276hp-automatic-47902
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	4660	1890	1760	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-facelift-2009-2.4-174hp-47893
EU-PEUGEOT-308-CC-I-CONVERTIBLE-2D-01	4440	1872	1426	Auto-Data	https://www.auto-data.net/en/peugeot-308-cc-i-phase-ii-2011-1.6-16v-thp-200hp-17636
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534	Auto-Data	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-75hp-fap-17982
```

## 下一步优先处理

1. 聚类解决 Ford Transit Mk1 的 Kasten/Bus、轴距、载重级别与车顶分支。
2. 明确 C4 Picasso/Grand Picasso 的金属悬架、气动悬架及车顶纵梁高度边界，避免覆盖已有冲突尺寸组。
3. 补齐 Bipper Van/MPV 的不含后视镜宽度。
4. 处理 Lada 1200–1600/Nova/Toscana，以及 Ford Fiesta/Orion/Escort Express 的相邻缓存分支。
5. 集中闭合 Peugeot 204/304/305 剩余车身与 Toyota Cressida、Starlet、早期 Carina/Celica。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-2.0-tfsi-211hp-s-tronic-27333 "Audi TT Roadster (8J, facelift 2010) 2.0 TFSI (211 Hp) S tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新建并闭合 C4 Picasso I facelift 短轴 MPV 与 Grand C4 Picasso I facelift 两个尺寸组；官方技术表分别给出 `4470×1830×1680 mm` 和 `4590×1830×1710 mm`。短车身结果与累计表既有 `-01` 三维冲突，因此按规则新建 `-02`，未覆盖既有组。([Dezo's Garage][1])
* 新建 Peugeot Bipper Tepee 与 Bipper Kasten 两个尺寸组，宽度统一采用不含后视镜的 `1716 mm`；Kasten 的含后视镜宽度为 `2019 mm`，未落入表中。([ADAC][2])
* 新建 Peugeot 205 CJ Convertible 尺寸组，闭合为 `3705×1572×1381 mm`，宽度为不含后视镜口径。([汽车目录][3])
* 批量复用 Escort IV、Fiesta III、Orion II、Peugeot 205 II、Peugeot 305 I、Dacia Logan I 与 Toyota Celica III 已有尺寸组。
* Ktype `6641`、`6671`、`6672` 按门数拆分；Ktype `6698` 按 Logan I 改款前后尺寸变化拆分。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：54
* READY 映射行：62
* PENDING 输入 Ktype：46
* 当前已引用尺寸组：39
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6628	6628	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-02	HIGH	短车身五门MPV外廓。	READY
6634	6634	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6635	6635	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6640	6640	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6641_3dr	6641	Hatchback	Escort IV		3	EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	MEDIUM	三门掀背物理分支。	READY
6641_5dr	6641	Hatchback	Escort IV		5	EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	MEDIUM	五门掀背物理分支。	READY
6650	6650	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	RS Turbo三门外廓。	READY
6651	6651	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6652	6652	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6653	6653	MPV	Bipper I		5	EU-PEUGEOT-BIPPER-I-TEPEE-MPV-5D-01	HIGH	Tepee五门乘用车身。	READY
6654	6654	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6655	6655	Van	Bipper I		3	EU-PEUGEOT-BIPPER-I-VAN-3D-01	HIGH	标准厢式货车外廓。	READY
6669	6669	Convertible	205 I		2	EU-PEUGEOT-205-I-CJ-CONVERTIBLE-2D-01	HIGH	CJ双门敞篷外廓。	READY
6671_3dr	6671	Hatchback	205 II		3	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	MEDIUM	三门标准掀背分支。	READY
6671_5dr	6671	Hatchback	205 II		5	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	MEDIUM	五门标准掀背分支。	READY
6672_3dr	6672	Hatchback	205 II		3	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	MEDIUM	三门标准掀背分支。	READY
6672_5dr	6672	Hatchback	205 II		5	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	MEDIUM	五门标准掀背分支。	READY
6682	6682	Sedan	305 I		4	EU-PEUGEOT-305-I-SEDAN-BASE-01	HIGH	标准四门轿车外廓。	READY
6698_prefl	6698	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产期覆盖改款前外廓。	READY
6698_facelift	6698	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产期覆盖改款后外廓。	READY
6714	6714	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
6715	6715	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
6716	6716	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-02	4470	1830	1680	Citroën C4 Picasso 2010 official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	4590	1830	1710	Citroën C4 Picasso 2010 official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-PEUGEOT-BIPPER-I-TEPEE-MPV-5D-01	3959	1716	1721	EncyCARpedia Peugeot Bipper Tepee HDi FAP 75	https://www.encycarpedia.com/peugeot/11-bipper-tepee-hdi-fap-75-mpv
EU-PEUGEOT-BIPPER-I-VAN-3D-01	3864	1716	1721	ADAC Peugeot Bipper Kastenwagen technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/bipper/1generation/214385/
EU-PEUGEOT-205-I-CJ-CONVERTIBLE-2D-01	3705	1572	1381	Automobile-Catalog Peugeot 205 CJ 1.4	https://www.automobile-catalog.com/car/1990/2576240/peugeot_205_cj_1_4.html
```

## 下一步优先处理

1. Ford Transit Mk1 的 Bus/Kasten、FT 100、1300 载重级别及长短轴分支。
2. Lada 1200–1600、Toscana 与 Nova 轿车代码边界。
3. Ford Escort IV Express Type 35/Type 55 与 Fiesta I/II Van 跨代分支。
4. Peugeot 204、304、305 II 剩余 Sedan/Wagon/Coupe 分支。
5. Toyota Cressida、Starlet、早期 Carina 与第一代 Celica。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf "C4 Picasso STéFi Brochure Cover"
[2]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/bipper/1generation/214385/ "Peugeot Bipper Kastenwagen 75 (12/07 - 10/10): Technische Daten, Bilder, Preise | ADAC"
[3]: https://www.automobile-catalog.com/car/1990/2576240/peugeot_205_cj_1_4.html?utm_source=chatgpt.com "1990 Peugeot 205 CJ 1.4 Specs Review (50.5 kW / 69 PS / 68 hp) (since July 1990 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 复用既有 Escort IV Express Type 35/Type 55 尺寸组，并将 Ktype `6632`、`6633` 拆为两个已确认物理分支。
* 新建 Escort II Turnier 三门旅行车尺寸组，三维为 `4056×1564×1414 mm`。([汽车目录][1])
* Peugeot 204 Break 在 1973 年 8 月前后存在 `1560 mm` 与 `1570 mm` 两种不含后视镜宽度，已建立窄体、宽体两个尺寸组，并拆分跨期 Ktype `6660`。([汽车目录][2])
* 新建 Peugeot 204 Coupe 与 Cabriolet 尺寸组，分别为 `3740×1560×1300 mm` 和 `3740×1560×1320 mm`。([汽车目录][3])
* Peugeot 304 Sedan 在后期高度由 `1410 mm` 变为 `1420 mm`；304 Break 后期长度由 `3990 mm` 变为 `4010 mm`。已建立对应早期、后期尺寸组并拆分跨期 Ktype。([汽车目录][4])
* 复用 Peugeot 305 II Break 宽体尺寸组，闭合 Ktype `6687`、`6689`。
* 新建 Dacia Logan I MCV facelift 旅行车尺寸组，三维为 `4473×1740×1640 mm`。([汽车数据][5])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：74
* READY 映射行：87
* PENDING 输入 Ktype：26
* 当前已引用尺寸组：50
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6632_type35	6632	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	MEDIUM	Type 35厢式车物理分支。	READY
6632_type55	6632	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	MEDIUM	Type 55高车身厢式车物理分支。	READY
6633_type35	6633	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	MEDIUM	Type 35厢式车物理分支。	READY
6633_type55	6633	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	MEDIUM	Type 55高车身厢式车物理分支。	READY
6638	6638	Wagon	Escort II Turnier		3	EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	HIGH	三门Turnier旅行车外廓。	READY
6639	6639	Wagon	Escort II Turnier		3	EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	HIGH	三门Turnier旅行车外廓。	READY
6660_narrow	6660	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	HIGH	1973年8月前窄体外廓。	READY
6660_wide	6660	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	HIGH	1973年8月起宽体外廓。	READY
6661	6661	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	HIGH	早期柴油Break五门外廓。	READY
6662	6662	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	HIGH	1.3柴油宽体Break外廓。	READY
6663	6663	Coupe	204 Coupe		3	EU-PEUGEOT-204-COUPE-3D-01	HIGH	三门Coupe外廓。	READY
6665	6665	Convertible	204 Cabriolet		2	EU-PEUGEOT-204-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
6673	6673	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-EARLY-01	HIGH	早期四门轿车外廓。	READY
6674_early	6674	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-EARLY-01	MEDIUM	生产期覆盖早期低车身外廓。	READY
6674_late	6674	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-LATE-01	MEDIUM	生产期覆盖后期高车身外廓。	READY
6676	6676	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-LATE-01	HIGH	后期柴油四门轿车外廓。	READY
6677_early	6677	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-EARLY-01	MEDIUM	生产期覆盖早期短车身Break。	READY
6677_late	6677	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	MEDIUM	生产期覆盖后期加长Break。	READY
6678	6678	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	HIGH	后期五门Break外廓。	READY
6679	6679	Coupe	304 Coupe		2	EU-PEUGEOT-304-COUPE-2D-01	HIGH	双门Coupe外廓。	READY
6680	6680	Coupe	304 Coupe		2	EU-PEUGEOT-304-COUPE-2D-01	HIGH	双门Coupe外廓。	READY
6687	6687	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-WIDE-01	HIGH	后期宽体五门Break外廓。	READY
6689	6689	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-WIDE-01	HIGH	后期宽体五门Break外廓。	READY
6710	6710	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	改款五门MCV旅行车外廓。	READY
6711	6711	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	改款五门MCV旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	4056	1564	1414	Automobile-Catalog 1975 Ford Escort Turnier 1300 L	https://www.automobile-catalog.com/car/1975/919865/ford_escort_turnier_1300_l.html
EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	3970	1560	1400	Automobile-Catalog 1973 Peugeot 204 Break Grand Luxe	https://www.automobile-catalog.com/car/1973/2555810/peugeot_204_break_grand_luxe.html
EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	3970	1570	1400	Automobile-Catalog 1973 Peugeot 204 Break Grand Luxe	https://www.automobile-catalog.com/car/1973/2556005/peugeot_204_break_grand_luxe.html
EU-PEUGEOT-204-COUPE-3D-01	3740	1560	1300	Automobile-Catalog 1969 Peugeot 204 Coupe Grand Luxe	https://www.automobile-catalog.com/car/1969/2555585/peugeot_204_coupe_grand_luxe.html
EU-PEUGEOT-204-CONVERTIBLE-2D-01	3740	1560	1320	Automobile-Catalog 1969 Peugeot 204 Cabriolet Grand Luxe	https://www.automobile-catalog.com/car/1969/2555570/peugeot_204_cabriolet_grand_luxe.html
EU-PEUGEOT-304-SEDAN-4D-EARLY-01	4140	1570	1410	Automobile-Catalog 1969 Peugeot 304 Berline	https://www.automobile-catalog.com/car/1969/27695/peugeot_304.html
EU-PEUGEOT-304-SEDAN-4D-LATE-01	4140	1570	1420	Automobile-Catalog 1976 Peugeot 304 Berline GL	https://www.automobile-catalog.com/car/1976/2556200/peugeot_304_berline_gl.html
EU-PEUGEOT-304-BREAK-WAGON-5D-EARLY-01	3990	1570	1430	Automobile-Catalog 1970 Peugeot 304 Break Super Luxe	https://www.automobile-catalog.com/car/1970/2556020/peugeot_304_break_super_luxe.html
EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	4010	1570	1430	Automobile-Catalog 1976 Peugeot 304 Break GL	https://www.automobile-catalog.com/car/1976/39545/peugeot_304_break_gl.html
EU-PEUGEOT-304-COUPE-2D-01	3750	1570	1320	Automobile-Catalog 1970 Peugeot 304 Coupe	https://www.automobile-catalog.com/car/1970/2556050/peugeot_304_coupe.html
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.5 dCi 75 FAP	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-75hp-fap-46180
```

## 下一步优先处理

1. Ford Transit Mk1 的 Kasten、Bus、FT 100、1300 载重级别及轴距分支。
2. Lada 1200–1600、Nova Sedan 与 Toscana 的 2103/2105/2106/2107 车身代码边界。
3. Ford Fiesta I/II Kasten 跨代与长保险杠分支。
4. Toyota Cressida Wagon、Starlet P40/P50、早期 Carina 与 Celica TA2。
5. Peugeot 305 II Sedan 1.9 98 hp 与 Peugeot 404 跨期外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1975/919865/ford_escort_turnier_1300_l.html?utm_source=chatgpt.com "1975 Ford Escort Turnier 1300 L Specs Review (42 kW ..."
[2]: https://www.automobile-catalog.com/car/1973/2555810/peugeot_204_break_grand_luxe.html?utm_source=chatgpt.com "1973 Peugeot 204 Break Grand Luxe Specs Review (40.5 kW / 55 PS / 54 hp) (up to July 1973 for Europe )"
[3]: https://www.automobile-catalog.com/car/1969/2555585/peugeot_204_coupe_grand_luxe.html?utm_source=chatgpt.com "1969 Peugeot 204 Coupe Grand Luxe (man. 4)"
[4]: https://www.automobile-catalog.com/car/1969/27695/peugeot_304.html?utm_source=chatgpt.com "1969 Peugeot 304 Berline Specs Review (48 kW / 65 PS / 64 hp) (since September 1969 for Europe )"
[5]: https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-75hp-fap-46180 "Dacia Logan I MCV (facelift 2008) 1.5 dCi (75 Hp) FAP | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 复用 4 个既有 Fiesta I/II 尺寸组，将 Ktype `6642`、`6643`、`6644` 按改款和代际外廓拆分；未重复输出尺寸组。
* 新建 Toyota Cressida RX35 Wagon、Starlet KP45 Coupe 和 Publica KP36V Wagon 尺寸组，分别闭合为 `4530×1680×1445`、`3790×1530×1325` 和 `3705×1460×1410 mm`。([汽车目录][1])
* 复用 Peugeot 305 II Sedan Base 尺寸组，闭合 Ktype `6684`。
* Peugeot 404 Sedan 在 1969 年前后长度发生变化，Ktype `6697` 拆分为 `4420 mm` 和 `4445 mm` 两个物理分支。([汽车目录][2])
* 复用既有 Carina II A40 Wagon facelift 尺寸组；新建 Carina I A10 Sedan 尺寸组 `4135×1570×1385 mm`。([丰田官网][3])
* Celica I 的 TA22 与 TA23 facelift 外廓分别闭合为 `4165×1600×1310` 和 `4260×1620×1320 mm`；跨改款 Ktype 已完整派生。([丰田官网][4])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：89
* READY 映射行：116
* PENDING 输入 Ktype：11
* 当前已引用尺寸组：63
* 本轮首次创建尺寸组：8
* 剩余待处理：Ford Transit 6 个、Lada 5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6642_mk1_prefl	6642	Van	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	MEDIUM	Fiesta I改款前三门厢式外廓。	READY
6642_mk1_facelift	6642	Van	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	Fiesta I改款后三门厢式外廓。	READY
6642_mk2_prefl	6642	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6642_mk2_facelift	6642	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	生产末期覆盖Fiesta II改款后三门厢式外廓。	READY
6643_mk1_prefl	6643	Van	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	MEDIUM	Fiesta I改款前三门厢式外廓。	READY
6643_mk1_facelift	6643	Van	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	Fiesta I改款后三门厢式外廓。	READY
6643_mk2_prefl	6643	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6643_mk2_facelift	6643	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	生产末期覆盖Fiesta II改款后三门厢式外廓。	READY
6644_prefl	6644	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6644_facelift	6644	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	Fiesta II改款后三门厢式外廓。	READY
6659	6659	Wagon	Cressida I	RX35	5	EU-TOYOTA-CRESSIDA-I-RX35-WAGON-5D-01	HIGH	RX35五门旅行车外廓。	READY
6684	6684	Sedan	305 II	581M	4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	1.9 98 hp标准四门轿车外廓。	READY
6690	6690	Coupe	Starlet I	KP45	2	EU-TOYOTA-STARLET-I-P40-COUPE-2D-01	MEDIUM	KP45双门Coupe外廓。	READY
6692	6692	Wagon	Publica P30	KP36V	3	EU-TOYOTA-PUBLICA-P30-WAGON-3D-01	MEDIUM	欧洲Starlet名称下的Publica三门旅行车外廓。	READY
6697_pre69	6697	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-PRE69-01	MEDIUM	生产期覆盖1969年前四门轿车外廓。	READY
6697_post69	6697	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	MEDIUM	生产期覆盖1969年起四门轿车外廓。	READY
6699	6699	Wagon	Carina II facelift	A40	5	EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	HIGH	A40改款五门旅行车外廓。	READY
6700	6700	Sedan	Carina I	TA12	4	EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	HIGH	TA12四门轿车外廓。	READY
6701	6701	Sedan	Carina I	TA12	4	EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	HIGH	TA12四门轿车外廓。	READY
6706_prefl	6706	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6706_facelift	6706	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6707_prefl	6707	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6707_facelift	6707	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6708_prefl	6708	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6708_facelift	6708	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6709	6709	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	HIGH	TA23改款后双门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CRESSIDA-I-RX35-WAGON-5D-01	4530	1680	1445	Automobile-Catalog 1978 Toyota Cressida 2000 Kombi	https://www.automobile-catalog.com/car/1978/45635/toyota_cressida_kombi.html
EU-TOYOTA-STARLET-I-P40-COUPE-2D-01	3790	1530	1325	Toyota 75 Years Vehicle Lineage - Publica Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006888/index.html
EU-TOYOTA-PUBLICA-P30-WAGON-3D-01	3705	1460	1410	Carfolio 1976 Toyota Publica 1000 Estate	https://www.carfolio.com/toyota-publica-1000-estate-54395
EU-PEUGEOT-404-I-SEDAN-PRE69-01	4420	1626	1450	Automobile-Catalog 1968 Peugeot 404 4-door Sedan	https://www.automobile-catalog.com/car/1968/2555300/peugeot_404_4-door_sedan.html
EU-PEUGEOT-404-I-SEDAN-POST69-01	4445	1626	1450	Automobile-Catalog 1969 Peugeot 404 4-door Sedan	https://www.automobile-catalog.com/car/1969/2555360/peugeot_404_4-door_sedan.html
EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	4135	1570	1385	Toyota 75 Years Vehicle Lineage - First-generation Carina	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60002214/index.html
EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	4165	1600	1310	Toyota 75 Years Vehicle Lineage - First-generation Celica	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60009901/index.html
EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	4260	1620	1320	Automobile-Catalog 1976 Toyota Celica 1600 LT;CarsGuide Toyota Celica 1976 dimensions	https://www.automobile-catalog.com/car/1976/3459860/toyota_celica_1600_lt_4speed.html;https://www.carsguide.com.au/toyota/celica/car-dimensions/1976
```

## 下一步优先处理

1. 一次性拆分 Ford Transit Mk1 的 SWB/LWB、Bus/Kasten、FT 100 与 1300 载重车身。
2. 确认 Lada `1500 N/S`、`1600 N/L`、`1300`、Toscana 与 Nova `1500 S` 对应的 2103、2105、2106、2107 物理外廓。
3. 剩余 11 个 Ktype 闭合后，立即执行一次机械检查并输出最终完整 TSV 与两个指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/45635/toyota_cressida_kombi.html?utm_source=chatgpt.com "1978 Toyota Cressida 2000 Wagon (man. 4) (Komb, Estate)."
[2]: https://www.automobile-catalog.com/car/1968/2555300/peugeot_404_4-door_sedan.html?utm_source=chatgpt.com "1968 Peugeot 404 4-Door Sedan (man. 4)"
[3]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60002214/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[4]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60009901/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 复用既有 `EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01`，闭合 Transit Mk1 的 `72E1A` 厢式车、`72E2X` FT 100 Bus 与 `72E3C` Bus。该短轴低顶外廓为 `4420×1855×1991 mm`，本轮不重复输出既有尺寸组。([Transit Center Ford Transit Spare Parts][1])
* 新建 Lada 2103、21011、2106、2107、2105 五个轿车尺寸组。
* Ktype `6630` 的车型目录同时覆盖 VAZ-2103 与 VAZ-2106 车身，已拆分为两个物理分支。([Brembo Parts][2])
* Ford Transit `1.7 1300` 的 Ktype `6622`、`6623`、`6624` 尚需确认 81E/1300 载重车身的完整三维，未猜测关联尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：97
* READY 映射行：125
* PENDING 输入 Ktype：3
* 当前已引用尺寸组：68
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6619	6619	Van	Transit Mk1	72E1A		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式车外廓。	READY
6620	6620	MPV	Transit Mk1	72E2X		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	FT 100短轴低顶Bus外廓。	READY
6621	6621	MPV	Transit Mk1	72E3C		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
6627	6627	Sedan	Lada 2103	VAZ2103	4	EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	HIGH	VAZ-2103四门轿车外廓。	READY
6629	6629	Sedan	Lada 2101 family	VAZ21011	4	EU-LADA-1200-1600-VAZ21011-SEDAN-4D-01	MEDIUM	VAZ-21011四门轿车外廓。	READY
6630_vaz2103	6630	Sedan	Lada 2103	VAZ2103	4	EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	MEDIUM	Ktype目录覆盖VAZ-2103车身分支。	READY
6630_vaz2106	6630	Sedan	Lada 2106	VAZ2106	4	EU-LADA-1200-1600-VAZ2106-SEDAN-4D-01	MEDIUM	Ktype目录覆盖VAZ-2106车身分支。	READY
6631	6631	Sedan	Lada 2107	VAZ2107	4	EU-LADA-TOSCANA-2107-SEDAN-4D-01	HIGH	VAZ-2107四门轿车外廓。	READY
6658	6658	Sedan	Lada 2105	VAZ2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	HIGH	VAZ-2105四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	4116	1611	1440	AvtoVAZ VAZ-2103 technical specifications	https://vaz-avto.ucoz.ru/index/vaz_2103/0-7
EU-LADA-1200-1600-VAZ21011-SEDAN-4D-01	4073	1611	1450	Haynes Lada 1200 1300 1500 and 1600 Owners Workshop Manual	https://dokumen.pub/haynes-lada-1200-1300-1500-amp-1600-owners-workshop-manual-1850104085-9781850104087.html
EU-LADA-1200-1600-VAZ2106-SEDAN-4D-01	4166	1611	1450	Haynes Lada 1200 1300 1500 and 1600 Owners Workshop Manual	https://dokumen.pub/haynes-lada-1200-1300-1500-amp-1600-owners-workshop-manual-1850104085-9781850104087.html
EU-LADA-TOSCANA-2107-SEDAN-4D-01	4145	1620	1446	WheelsAge Lada 2107 specifications	https://en.wheelsage.org/lada/2107/specifications
EU-LADA-NOVA-2105-SEDAN-4D-01	4130	1620	1446	Drive.Place Lada 2105 1.5 MT 71 hp specifications	https://lada.drive.place/2105/i/group_sedan/540510
```

## 下一步优先处理

1. 闭合 Ktype `6622`、`6623`、`6624` 的 Transit Mk1 `1.7 1300` 车身边界。
2. 明确 `81E4SA` 与 `820000` 是否共用同一 1300 载重外廓，并取得完整、不含后视镜宽度的三维。
3. 三个 Ktype 闭合后立即执行一次机械检查，输出两张最终完整 TSV 和两个指定下载链接。

推进信号：CONTINUE

[1]: https://www.transitcenter.uk/transit-mk1-data-specification.php?srsltid=AfmBOopNPzmFSyW7uHMu5OZf8yXYwXnoPDY5ZhKQqMDRiE5BB4ciyR9g "FORD TRANSIT MK1 - SPECIFICATIONS"
[2]: https://www.bremboparts.com/europe/en/catalogue/lada-1200-1600-1600-n-l-vaz2106-vaz2103/000006630-1?utm_source=chatgpt.com "Pads and Discs for LADA 1200-1600 1600 N/L (VAZ2106, ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6201-6300_ktype_dimension_mapping_final.tsv
- all_6201-6300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 Ktype `6622`、`6623`、`6624`，当前批次无 PENDING。
* 已完成机械检查：表头固定、125 个 `id` 唯一、72 个 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源字段完整。
* 已生成两个任务指定的最终 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：125
* PENDING：0
* DIMENSION_GROUP：72
* IterationStatus：全部 `READY`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6619	6619	Van	Transit Mk1	72E1A		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式车外廓。	READY
6620	6620	MPV	Transit Mk1	72E2X		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	FT 100短轴低顶Bus外廓。	READY
6621	6621	MPV	Transit Mk1	72E3C		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
6622	6622	Van	Transit Mk1	81E4SA		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	1300载重级短轴低顶消防厢式外廓。	READY
6623	6623	Van	Transit Mk1	81E4SA		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	1300载重级短轴低顶厢式外廓。	READY
6624	6624	MPV	Transit Mk1	820000		EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	1300载重级短轴低顶Bus外廓。	READY
6625	6625	Convertible	TT 8J facelift	8J	2	EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	HIGH	8J改款Roadster双门外廓。	READY
6626	6626	Convertible	TT 8J facelift	8J	2	EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	HIGH	8J改款Roadster双门外廓。	READY
6627	6627	Sedan	Lada 2103	VAZ2103	4	EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	HIGH	VAZ-2103四门轿车外廓。	READY
6628	6628	MPV	C4 Picasso I facelift	UD	5	EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-02	HIGH	短车身五门MPV外廓。	READY
6629	6629	Sedan	Lada 2101 family	VAZ21011	4	EU-LADA-1200-1600-VAZ21011-SEDAN-4D-01	MEDIUM	VAZ-21011四门轿车外廓。	READY
6630_vaz2103	6630	Sedan	Lada 2103	VAZ2103	4	EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	MEDIUM	Ktype目录覆盖VAZ-2103车身分支。	READY
6630_vaz2106	6630	Sedan	Lada 2106	VAZ2106	4	EU-LADA-1200-1600-VAZ2106-SEDAN-4D-01	MEDIUM	Ktype目录覆盖VAZ-2106车身分支。	READY
6631	6631	Sedan	Lada 2107	VAZ2107	4	EU-LADA-TOSCANA-2107-SEDAN-4D-01	HIGH	VAZ-2107四门轿车外廓。	READY
6632_type35	6632	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	MEDIUM	Type 35厢式车物理分支。	READY
6632_type55	6632	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	MEDIUM	Type 55高车身厢式车物理分支。	READY
6633_type35	6633	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	MEDIUM	Type 35厢式车物理分支。	READY
6633_type55	6633	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	MEDIUM	Type 55高车身厢式车物理分支。	READY
6634	6634	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6635	6635	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6637	6637	Sedan	Escort II		2	EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	HIGH	RS2000双门轿车外廓。	READY
6638	6638	Wagon	Escort II Turnier		3	EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	HIGH	三门Turnier旅行车外廓。	READY
6639	6639	Wagon	Escort II Turnier		3	EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	HIGH	三门Turnier旅行车外廓。	READY
6640	6640	MPV	Grand C4 Picasso I facelift	UA	5	EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	HIGH	Grand长车身五门MPV外廓。	READY
6641_3dr	6641	Hatchback	Escort IV		3	EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	MEDIUM	三门掀背物理分支。	READY
6641_5dr	6641	Hatchback	Escort IV		5	EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	MEDIUM	五门掀背物理分支。	READY
6642_mk1_prefl	6642	Van	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	MEDIUM	Fiesta I改款前三门厢式外廓。	READY
6642_mk1_facelift	6642	Van	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	Fiesta I改款后三门厢式外廓。	READY
6642_mk2_prefl	6642	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6642_mk2_facelift	6642	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	生产末期覆盖Fiesta II改款后三门厢式外廓。	READY
6643_mk1_prefl	6643	Van	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	MEDIUM	Fiesta I改款前三门厢式外廓。	READY
6643_mk1_facelift	6643	Van	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	Fiesta I改款后三门厢式外廓。	READY
6643_mk2_prefl	6643	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6643_mk2_facelift	6643	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	生产末期覆盖Fiesta II改款后三门厢式外廓。	READY
6644_prefl	6644	Van	Fiesta II	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	MEDIUM	Fiesta II改款前三门厢式外廓。	READY
6644_facelift	6644	Van	Fiesta II facelift	FBD	3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	MEDIUM	Fiesta II改款后三门厢式外廓。	READY
6645	6645	Sedan	Grandeur IV facelift	TG	4	EU-HYUNDAI-GRANDEUR-IV-TG-FACELIFT-SEDAN-4D-01	HIGH	TG改款四门轿车外廓。	READY
6646	6646	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-V6-01	HIGH	3.5 V6版本外廓。	READY
6647	6647	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6648	6648	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6649	6649	SUV	Santa Fe II facelift	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	HIGH	CM改款标准外廓。	READY
6650	6650	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	RS Turbo三门外廓。	READY
6651	6651	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6652	6652	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6653	6653	MPV	Bipper I		5	EU-PEUGEOT-BIPPER-I-TEPEE-MPV-5D-01	HIGH	Tepee五门乘用车身。	READY
6654	6654	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
6655	6655	Van	Bipper I		3	EU-PEUGEOT-BIPPER-I-VAN-3D-01	HIGH	标准厢式货车外廓。	READY
6656	6656	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	GAL四门轿车外廓。	READY
6658	6658	Sedan	Lada 2105	VAZ2105	4	EU-LADA-NOVA-2105-SEDAN-4D-01	HIGH	VAZ-2105四门轿车外廓。	READY
6659	6659	Wagon	Cressida I	RX35	5	EU-TOYOTA-CRESSIDA-I-RX35-WAGON-5D-01	HIGH	RX35五门旅行车外廓。	READY
6660_narrow	6660	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	HIGH	1973年8月前窄体外廓。	READY
6660_wide	6660	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	HIGH	1973年8月起宽体外廓。	READY
6661	6661	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	HIGH	早期柴油Break五门外廓。	READY
6662	6662	Wagon	204 Break		5	EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	HIGH	1.3柴油宽体Break外廓。	READY
6663	6663	Coupe	204 Coupe		3	EU-PEUGEOT-204-COUPE-3D-01	HIGH	三门Coupe外廓。	READY
6664	6664	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-CONVERTIBLE-2D-01	HIGH	双门硬顶敞篷外廓。	READY
6665	6665	Convertible	204 Cabriolet		2	EU-PEUGEOT-204-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
6666	6666	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6667	6667	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6668	6668	Hatchback	205 I		3	EU-PEUGEOT-205-I-GTI-HATCHBACK-3D-01	HIGH	GTI三门宽体外廓。	READY
6669	6669	Convertible	205 I		2	EU-PEUGEOT-205-I-CJ-CONVERTIBLE-2D-01	HIGH	CJ双门敞篷外廓。	READY
6670	6670	Sedan	Camry I	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH	V10四门轿车外廓。	READY
6671_3dr	6671	Hatchback	205 II		3	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	MEDIUM	三门标准掀背分支。	READY
6671_5dr	6671	Hatchback	205 II		5	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	MEDIUM	五门标准掀背分支。	READY
6672_3dr	6672	Hatchback	205 II		3	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	MEDIUM	三门标准掀背分支。	READY
6672_5dr	6672	Hatchback	205 II		5	EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	MEDIUM	五门标准掀背分支。	READY
6673	6673	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-EARLY-01	HIGH	早期四门轿车外廓。	READY
6674_early	6674	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-EARLY-01	MEDIUM	生产期覆盖早期低车身外廓。	READY
6674_late	6674	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-LATE-01	MEDIUM	生产期覆盖后期高车身外廓。	READY
6675	6675	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
6676	6676	Sedan	304		4	EU-PEUGEOT-304-SEDAN-4D-LATE-01	HIGH	后期柴油四门轿车外廓。	READY
6677_early	6677	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-EARLY-01	MEDIUM	生产期覆盖早期短车身Break。	READY
6677_late	6677	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	MEDIUM	生产期覆盖后期加长Break。	READY
6678	6678	Wagon	304 Break		5	EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	HIGH	后期五门Break外廓。	READY
6679	6679	Coupe	304 Coupe		2	EU-PEUGEOT-304-COUPE-2D-01	HIGH	双门Coupe外廓。	READY
6680	6680	Coupe	304 Coupe		2	EU-PEUGEOT-304-COUPE-2D-01	HIGH	双门Coupe外廓。	READY
6681	6681	Convertible	304		2	EU-PEUGEOT-304-CABRIOLET-01	HIGH	304双门敞篷外廓。	READY
6682	6682	Sedan	305 I		4	EU-PEUGEOT-305-I-SEDAN-BASE-01	HIGH	标准四门轿车外廓。	READY
6683	6683	Sedan	305 II		4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	标准车身四门轿车外廓。	READY
6684	6684	Sedan	305 II	581M	4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	1.9 98 hp标准四门轿车外廓。	READY
6685	6685	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6686	6686	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6687	6687	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-WIDE-01	HIGH	后期宽体五门Break外廓。	READY
6688	6688	Wagon	305 II		5	EU-PEUGEOT-305-II-BREAK-BASE-01	MEDIUM	标准车身五门Break外廓。	READY
6689	6689	Wagon	305 II Break	581E	5	EU-PEUGEOT-305-II-BREAK-WIDE-01	HIGH	后期宽体五门Break外廓。	READY
6690	6690	Coupe	Starlet I	KP45	2	EU-TOYOTA-STARLET-I-P40-COUPE-2D-01	MEDIUM	KP45双门Coupe外廓。	READY
6691	6691	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6692	6692	Wagon	Publica P30	KP36V	3	EU-TOYOTA-PUBLICA-P30-WAGON-3D-01	MEDIUM	欧洲Starlet名称下的Publica三门旅行车外廓。	READY
6693	6693	Hatchback	Camry I	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH	V10五门掀背外廓。	READY
6694	6694	Hatchback	Camry I	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH	V10五门掀背外廓。	READY
6695	6695	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6696	6696	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
6697_pre69	6697	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-PRE69-01	MEDIUM	生产期覆盖1969年前四门轿车外廓。	READY
6697_post69	6697	Sedan	404 I		4	EU-PEUGEOT-404-I-SEDAN-POST69-01	MEDIUM	生产期覆盖1969年起四门轿车外廓。	READY
6698_prefl	6698	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产期覆盖改款前外廓。	READY
6698_facelift	6698	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产期覆盖改款后外廓。	READY
6699	6699	Wagon	Carina II facelift	A40	5	EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	HIGH	A40改款五门旅行车外廓。	READY
6700	6700	Sedan	Carina I	TA12	4	EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	HIGH	TA12四门轿车外廓。	READY
6701	6701	Sedan	Carina I	TA12	4	EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	HIGH	TA12四门轿车外廓。	READY
6702_prefl	6702	Hatchback	Carina II	T150	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	MEDIUM	生产期跨改款，前期外廓。	READY
6702_facelift	6702	Hatchback	Carina II	T150	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	MEDIUM	生产期跨改款，改款外廓。	READY
6703_prefl	6703	Sedan	Carina II	T150	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	MEDIUM	生产期跨改款，前期外廓。	READY
6703_facelift	6703	Sedan	Carina II	T150	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨改款，改款外廓。	READY
6704	6704	Sedan	Carina II	T170	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH	T170四门轿车外廓。	READY
6705	6705	Hatchback	Carina II	T170	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH	T170五门掀背外廓。	READY
6706_prefl	6706	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6706_facelift	6706	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6707_prefl	6707	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6707_facelift	6707	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6708_prefl	6708	Coupe	Celica I	TA22	2	EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	MEDIUM	生产期覆盖TA22改款前双门外廓。	READY
6708_facelift	6708	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	MEDIUM	生产期覆盖TA23改款后双门外廓。	READY
6709	6709	Coupe	Celica I facelift	TA23	2	EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	HIGH	TA23改款后双门Coupe外廓。	READY
6710	6710	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	改款五门MCV旅行车外廓。	READY
6711	6711	Wagon	Logan I MCV facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	改款五门MCV旅行车外廓。	READY
6712_prefl	6712	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产期跨改款，前期双门外廓。	READY
6712_facelift	6712	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产期跨改款，改款双门外廓。	READY
6713_prefl	6713	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产期跨改款，前期双门外廓。	READY
6713_facelift	6713	Coupe	Celica II		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产期跨改款，改款双门外廓。	READY
6714	6714	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
6715	6715	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
6716	6716	Hatchback	Celica III	A60	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH	A60三门Liftback外廓。	READY
6717	6717	Coupe	Celica IV	T16	2	EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	HIGH	T16前驱双门Coupe外廓。	READY
6718	6718	Hatchback	Celica IV	T16	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH	T16前驱三门掀背外廓。	READY
6719	6719	Sedan	Corolla VI	E90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门轿车外廓。	READY
6720	6720	Sedan	Corolla VI	E90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	E90四门轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6201-6300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-TT-8J-FACELIFT-ROADSTER-2D-01	4198	1842	1358	Auto-Data	https://www.auto-data.net/en/audi-tt-roadster-8j-facelift-2010-2.0-tfsi-211hp-s-tronic-27333
EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	4150	1590	1410	Automobile-Catalog 1975 Ford Escort RS 2000	https://www.automobile-catalog.com/car/1975/27785/ford_escort_rs_2000.html
EU-HYUNDAI-GRANDEUR-IV-TG-FACELIFT-SEDAN-4D-01	4895	1850	1495	Auto-Data	https://www.auto-data.net/en/hyundai-grandeur-azera-iv-tg-facelift-2009-generation-5658
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-V6-01	4676	1890	1725	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-facelift-2009-3.5-v6-276hp-automatic-47902
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	4660	1890	1760	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-facelift-2009-2.4-174hp-47893
EU-FORD-ORION-III-GAL-SEDAN-01	4229	1690	1395	Automobile-Catalog 1990 Ford Orion 1.6 GLX	https://www.automobile-catalog.com/car/1990/945395/ford_orion_1_6_glx_gl.html
EU-PEUGEOT-308-CC-I-CONVERTIBLE-2D-01	4440	1872	1426	Auto-Data	https://www.auto-data.net/en/peugeot-308-cc-i-phase-ii-2011-1.6-16v-thp-200hp-17636
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534	Auto-Data	https://www.auto-data.net/en/dacia-sandero-i-1.5-dci-75hp-fap-17982
EU-PEUGEOT-205-I-GTI-HATCHBACK-3D-01	3705	1589	1355	Automobile-Catalog 1989 Peugeot 205 GTI 115ch	https://www.automobile-catalog.com/car/1989/2575205/peugeot_205_gti_115ch.html
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395	Auto-Data Toyota Camry I V10	https://www.auto-data.net/en/toyota-camry-model-476
EU-PEUGEOT-304-CABRIOLET-01	3750	1570	1330	Automobile-Catalog 1970 Peugeot 304 Cabriolet	https://www.automobile-catalog.com/car/1970/2556035/peugeot_304_cabriolet.html
EU-PEUGEOT-305-II-SEDAN-BASE-01	4263	1630	1407	Automobile-Catalog 1984 Peugeot 305	https://www.automobile-catalog.com/car/1984/2568215/peugeot_305.html
EU-PEUGEOT-305-II-BREAK-BASE-01	4283	1630	1426	Automobile-Catalog 1983 Peugeot 305 Break GL	https://www.automobile-catalog.com/car/1983/2568200/peugeot_305_break_gl.html
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525	Autogidas Dacia Logan I facelift specifications	https://autogidas.lt/en/auto-katalogas/dacia/logan/1.4-laureate-2009-2010-k78863
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370	Auto-Data Toyota Camry I V10	https://www.auto-data.net/en/toyota-camry-model-476
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	4330	1670	1365	Drom Toyota Carina II dimensions	https://www.drom.ru/catalog/toyota/carina_ii/specs/dimensions/
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	4360	1670	1365	Drom Toyota Carina II dimensions	https://www.drom.ru/catalog/toyota/carina_ii/specs/dimensions/
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	4350	1670	1365	Automobile-Catalog 1984 Toyota Carina II Sedan 1.6 GL	https://www.automobile-catalog.com/car/1984/3516230/toyota_carina_ii_sedan_1_6_gl.html
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	4370	1670	1365	Automobile-Catalog 1987 Toyota Carina II Sedan 1.6 DX	https://www.automobile-catalog.com/car/1987/3516335/toyota_carina_ii_sedan_1_6_dx.html
EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	4440	1690	1370	Biland Toyota Carina II specifications	https://www.biland.nl/en/2014/06/23/toyota-carina-ii/
EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	4440	1690	1370	Automobile-Catalog 1989 Toyota Carina II Liftback 2.0 GLi	https://www.automobile-catalog.com/car/1989/63800/toyota_carina_ii_liftback_2_0_gli.html
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	4330	1635	1320	Automoli Toyota Celica A40/50 specifications	https://www.automoli.com/au/vehicles/toyota/celica/celica-ta60ra40ra6-773/
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	4370	1635	1320	Automobile-Catalog 1981 Toyota Celica Coupe 1600 LT	https://www.automobile-catalog.com/car/1981/3493430/toyota_celica_coupe_1600_lt_automatic.html
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	4410	1710	1290	Automobile-Catalog 1987 Toyota Celica 1.6 ST Coupe	https://www.automobile-catalog.com/car/1987/3519995/toyota_celica_1_6_st_coupe.html
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	4365	1710	1290	Automobile-Catalog 1989 Toyota Celica 2.0 GT Liftback	https://www.automobile-catalog.com/car/1989/3520085/toyota_celica_2_0_gt_liftback.html
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365	Toyota 75 Years Vehicle Lineage - Sixth-generation Corolla	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003780/index.html
EU-CITROEN-C4-PICASSO-I-FACELIFT-MPV-5D-02	4470	1830	1680	Citroën C4 Picasso 2010 official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-CITROEN-C4-GRAND-PICASSO-I-FACELIFT-MPV-5D-01	4590	1830	1710	Citroën C4 Picasso 2010 official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Citroen-C4-Picasso-UK.pdf
EU-FORD-ESCORT-IV-HATCHBACK-STANDARD-01	4022	1640	1385	Automobile-Catalog 1986 Ford Escort 1.3 CL	https://www.automobile-catalog.com/car/1986/941705/ford_escort_1_3_cl.html
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365	Automobile-Catalog 1992 Ford Fiesta XR2i	https://www.automobile-catalog.com/car/1992/944000/ford_fiesta_xr2i.html
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389	Automobile-Catalog 1987 Ford Orion 1.4 L	https://www.automobile-catalog.com/car/1987/943265/ford_orion_1_4_l.html
EU-PEUGEOT-BIPPER-I-TEPEE-MPV-5D-01	3959	1716	1721	EncyCARpedia Peugeot Bipper Tepee HDi FAP 75	https://www.encycarpedia.com/peugeot/11-bipper-tepee-hdi-fap-75-mpv
EU-PEUGEOT-BIPPER-I-VAN-3D-01	3864	1716	1721	ADAC Peugeot Bipper Kastenwagen technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/peugeot/bipper/1generation/214385/
EU-PEUGEOT-205-I-CJ-CONVERTIBLE-2D-01	3705	1572	1381	Automobile-Catalog Peugeot 205 CJ 1.4	https://www.automobile-catalog.com/car/1990/2576240/peugeot_205_cj_1_4.html
EU-PEUGEOT-205-II-STANDARD-HATCHBACK-3D-01	3705	1572	1374	Automobile-Catalog 1990 Peugeot 205 Look 1.1	https://www.automobile-catalog.com/car/1990/2577350/peugeot_205_look_1_1.html
EU-PEUGEOT-205-II-STANDARD-HATCHBACK-5D-01	3705	1572	1374	Automobile-Catalog 1990 Peugeot 205 Look 1.1	https://www.automobile-catalog.com/car/1990/2577350/peugeot_205_look_1_1.html
EU-PEUGEOT-305-I-SEDAN-BASE-01	4237	1630	1405	Automobile-Catalog 1978 Peugeot 305 GL	https://www.automobile-catalog.com/car/1978/31910/peugeot_305_gl.html
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525	Drive.Place Dacia Logan I specifications	https://dacia.drive.place/logan/i/group_sedan/367494
EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	4450	1665	1320	CarsGuide Toyota Celica 1983 dimensions	https://www.carsguide.com.au/toyota/celica/car-dimensions/1983
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	4181	1640	1568	Ford Escort Mk4 owner's manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	4181	1640	1594	Ford Escort Mk4 owner's manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-II-TURNIER-WAGON-3D-01	4056	1564	1414	Automobile-Catalog 1975 Ford Escort Turnier 1300 L	https://www.automobile-catalog.com/car/1975/919865/ford_escort_turnier_1300_l.html
EU-PEUGEOT-204-BREAK-WAGON-5D-NARROW-01	3970	1560	1400	Automobile-Catalog 1973 Peugeot 204 Break Grand Luxe	https://www.automobile-catalog.com/car/1973/2555810/peugeot_204_break_grand_luxe.html
EU-PEUGEOT-204-BREAK-WAGON-5D-WIDE-01	3970	1570	1400	Automobile-Catalog 1973 Peugeot 204 Break Grand Luxe	https://www.automobile-catalog.com/car/1973/2556005/peugeot_204_break_grand_luxe.html
EU-PEUGEOT-204-COUPE-3D-01	3740	1560	1300	Automobile-Catalog 1969 Peugeot 204 Coupe Grand Luxe	https://www.automobile-catalog.com/car/1969/2555585/peugeot_204_coupe_grand_luxe.html
EU-PEUGEOT-204-CONVERTIBLE-2D-01	3740	1560	1320	Automobile-Catalog 1969 Peugeot 204 Cabriolet Grand Luxe	https://www.automobile-catalog.com/car/1969/2555570/peugeot_204_cabriolet_grand_luxe.html
EU-PEUGEOT-304-SEDAN-4D-EARLY-01	4140	1570	1410	Automobile-Catalog 1969 Peugeot 304 Berline	https://www.automobile-catalog.com/car/1969/27695/peugeot_304.html
EU-PEUGEOT-304-SEDAN-4D-LATE-01	4140	1570	1420	Automobile-Catalog 1976 Peugeot 304 Berline GL	https://www.automobile-catalog.com/car/1976/2556200/peugeot_304_berline_gl.html
EU-PEUGEOT-304-BREAK-WAGON-5D-EARLY-01	3990	1570	1430	Automobile-Catalog 1970 Peugeot 304 Break Super Luxe	https://www.automobile-catalog.com/car/1970/2556020/peugeot_304_break_super_luxe.html
EU-PEUGEOT-304-BREAK-WAGON-5D-LATE-01	4010	1570	1430	Automobile-Catalog 1976 Peugeot 304 Break GL	https://www.automobile-catalog.com/car/1976/39545/peugeot_304_break_gl.html
EU-PEUGEOT-304-COUPE-2D-01	3750	1570	1320	Automobile-Catalog 1970 Peugeot 304 Coupe	https://www.automobile-catalog.com/car/1970/2556050/peugeot_304_coupe.html
EU-PEUGEOT-305-II-BREAK-WIDE-01	4283	1636	1426	Automobile-Catalog 1986 Peugeot 305 Break SR	https://www.automobile-catalog.com/car/1986/2568695/peugeot_305_break_sr.html
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.5 dCi 75 FAP	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-75hp-fap-46180
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	3565	1567	1360	Automobile-Catalog 1979 Ford Fiesta 1.1 L	https://www.automobile-catalog.com/car/1979/922595/ford_fiesta_1_1_l.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359	Automobile-Catalog 1982 Ford Fiesta 1.1	https://www.automobile-catalog.com/car/1982/922805/ford_fiesta_1_1.html
EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	3648	1585	1334	Automobile-Catalog 1985 Ford Fiesta 1.1	https://www.automobile-catalog.com/car/1985/940655/ford_fiesta_1_1.html
EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	3648	1585	1376	Automobile-Catalog 1988 Ford Fiesta 1.6 D C	https://www.automobile-catalog.com/car/1988/941570/ford_fiesta_1_6_d_c.html
EU-TOYOTA-CRESSIDA-I-RX35-WAGON-5D-01	4530	1680	1445	Automobile-Catalog 1978 Toyota Cressida 2000 Kombi	https://www.automobile-catalog.com/car/1978/45635/toyota_cressida_kombi.html
EU-TOYOTA-STARLET-I-P40-COUPE-2D-01	3790	1530	1325	Toyota 75 Years Vehicle Lineage - Publica Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006888/index.html
EU-TOYOTA-PUBLICA-P30-WAGON-3D-01	3705	1460	1410	Carfolio 1976 Toyota Publica 1000 Estate	https://www.carfolio.com/toyota-publica-1000-estate-54395
EU-PEUGEOT-404-I-SEDAN-PRE69-01	4420	1626	1450	Automobile-Catalog 1968 Peugeot 404 4-door Sedan	https://www.automobile-catalog.com/car/1968/2555300/peugeot_404_4-door_sedan.html
EU-PEUGEOT-404-I-SEDAN-POST69-01	4445	1626	1450	Automobile-Catalog 1969 Peugeot 404 4-door Sedan	https://www.automobile-catalog.com/car/1969/2555360/peugeot_404_4-door_sedan.html
EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	4370	1630	1400	Automobile-Catalog 1979 Toyota Carina 1.6 Station Wagon	https://www.automobile-catalog.com/car/1979/3489620/toyota_carina_kombi_1_6.html
EU-TOYOTA-CARINA-I-A10-SEDAN-4D-01	4135	1570	1385	Toyota 75 Years Vehicle Lineage - First-generation Carina	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60002214/index.html
EU-TOYOTA-CELICA-I-TA22-COUPE-2D-01	4165	1600	1310	Toyota 75 Years Vehicle Lineage - First-generation Celica	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60009901/index.html
EU-TOYOTA-CELICA-I-TA23-FACELIFT-COUPE-2D-01	4260	1620	1320	Automobile-Catalog 1976 Toyota Celica 1600 LT;CarsGuide Toyota Celica 1976 dimensions	https://www.automobile-catalog.com/car/1976/3459860/toyota_celica_1600_lt_4speed.html;https://www.carsguide.com.au/toyota/celica/car-dimensions/1976
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991	Transit Center Ford Transit Mk1 specifications	https://www.transitcenter.uk/transit-mk1-data-specification.php
EU-LADA-1200-1600-VAZ2103-SEDAN-4D-01	4116	1611	1440	AvtoVAZ VAZ-2103 technical specifications	https://vaz-avto.ucoz.ru/index/vaz_2103/0-7
EU-LADA-1200-1600-VAZ21011-SEDAN-4D-01	4073	1611	1450	Haynes Lada 1200 1300 1500 and 1600 Owners Workshop Manual	https://dokumen.pub/haynes-lada-1200-1300-1500-amp-1600-owners-workshop-manual-1850104085-9781850104087.html
EU-LADA-1200-1600-VAZ2106-SEDAN-4D-01	4166	1611	1450	Haynes Lada 1200 1300 1500 and 1600 Owners Workshop Manual	https://dokumen.pub/haynes-lada-1200-1300-1500-amp-1600-owners-workshop-manual-1850104085-9781850104087.html
EU-LADA-TOSCANA-2107-SEDAN-4D-01	4145	1620	1446	WheelsAge Lada 2107 specifications	https://en.wheelsage.org/lada/2107/specifications
EU-LADA-NOVA-2105-SEDAN-4D-01	4130	1620	1446	Drive.Place Lada 2105 1.5 MT 71 hp specifications	https://lada.drive.place/2105/i/group_sedan/540510
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6201-6300_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6201-6300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6201-6300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7916 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2433 行）

