# 任务：all 第 401-500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0005__20ef7fc3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 401-500 行

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
all 第 401-500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C8-SEDAN-01	4939	1886	1457
EU-BMW-3-G20-SEDAN-01	4709	1827	1442
EU-BMW-3-G21-WAGON-01	4709	1827	1440
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480
EU-HYUNDAI-TUCSON-I-SUV-01	4325	1795	1680
EU-PORSCHE-911-9971-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-9972-TARGA-4S-01	4435	1852	1300
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	5075	2070	2307
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	5075	2070	2500
EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	5575	2070	2499
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	6225	2070	2488
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	6225	2070	2744
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Mar 2020	-	2024-03-01	139745
VW	Golf viii	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Dec 2019	-	2024-03-01	139749
Skoda	Octavia	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2020	-	2024-03-01	139764
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Mar 2020	-	2024-03-01	139765
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2020	-	2024-03-01	139766
Hyundai	H100	2.5 TCI	Pritsche/Fahrgestell	Heckantrieb	Diesel	74	100	Jan 2004	Dec 2012	2024-03-01	139767
Nissan	Cedric	2.8	Stufenheck	Heckantrieb	Benzin	108	147	Jan 1980	Feb 1983	2024-03-01	139779
Bestune	T77	PRO 280 TID	SUV	Frontantrieb	Benzin	124	169	Mar 2020	-	2024-03-01	139781
KIA	Sorento iv	2.2 Crdi	SUV	Frontantrieb	Diesel	148	201	Mar 2020	-	2024-03-01	139786
KIA	Sorento iv	2.2 Crdi 4WD	SUV	Allrad	Diesel	148	201	Mar 2020	-	2024-03-01	139787
Aston Martin	Vantage	V8	Cabriolet	Heckantrieb	Benzin	375	510	Feb 2020	-	2024-03-01	139788
Volvo	S90 ii	B4 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2024-03-01	139795
Volvo	S90 ii	B5 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	139796
Volvo	S90 ii	B6 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139797
Volvo	V90 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2024-03-01	139799
Volvo	V90 ii	B5 Mild-hybrid	Kombi	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	139800
Volvo	V90 ii	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139801
Volvo	V90 ii cross country	B5 Mild Hybrid AWD	Kombi	Allrad	Benzin/Elektro	184	250	Mar 2020	-	2025-06-01	139802
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	478	650	Mar 2020	May 2025	2026-03-01	139813
Porsche	911	3.8 Turbo S	Cabriolet	Allrad	Benzin	478	650	Mar 2020	May 2024	2024-08-01	139814
Ford	Ecosport	1.5 Ecoblue Tdci	SUV	Frontantrieb	Diesel	74	100	Nov 2017	-	2024-03-01	139824
Bentley	Continental	4.0 V8 AWD	Cabriolet	Allrad	Benzin	404	549	Jun 2019	-	2024-03-01	139829
Bentley	Continental	4.0 V8 AWD	Coupe	Allrad	Benzin	404	549	Jun 2019	-	2025-02-03	139830
Hyundai	I10 iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	100	Feb 2020	-	2024-03-01	139834
Hyundai	Elantra vii	1.6	Stufenheck	Frontantrieb	Benzin	90	123	Mar 2020	-	2024-03-01	139857
Volvo	V90 ii	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	256	348	Mar 2020	-	2024-03-01	139880
Volvo	Xc60 ii	B6 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139881
Citroën	Berlingo	Electric	Großraumlimousine	Frontantrieb	Elektro	49	67	Sep 2017	Dec 2018	2026-05-01	139908
Mercedes-benz	Sprinter 4-T tourer	414 CDI	Bus	Heckantrieb	Diesel	105	143	Sep 2019	Dec 2021	2024-08-01	139926
Land Rover	Defender van	2.0 P300 SI4 4X4	Kasten/Geländewagen geschlossen	Allrad	Benzin	221	300	Feb 2020	-	2024-03-01	139927
Land Rover	Defender van	3.0 P400 I6 Mhev 4X4	Kasten/Geländewagen geschlossen	Allrad	Benzin/Elektro	294	400	Feb 2020	-	2024-03-01	139928
Land Rover	Defender van	2.0 D200 SD4 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel	147	200	Feb 2020	-	2024-03-01	139929
Land Rover	Defender van	2.0 D240 SD4 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel	177	241	Feb 2020	-	2024-03-01	139930
Citroën	Berlingo	Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jan 2018	Dec 2018	2026-05-01	139939
VW	Golf viii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	66	90	Feb 2020	-	2024-03-01	140003
VW	Golf viii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Feb 2020	-	2024-03-01	140004
BMW	3	316 D	Stufenheck	Heckantrieb	Diesel	90	122	Mar 2020	-	2024-03-01	140024
Opel	Insignia b grand sport	1.5 Cdti	Schrägheck	Frontantrieb	Diesel	90	122	Feb 2020	-	2024-03-01	140030
Opel	Insignia b sports tourer	1.5 Cdti	Kombi	Frontantrieb	Diesel	90	122	Feb 2020	-	2024-03-01	140031
Suzuki	Ignis iii	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	61	83	Apr 2020	-	2024-03-01	140066
Suzuki	Ignis iii	1.2 Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	61	83	Apr 2020	-	2024-03-01	140067
Mclaren	765lt	4	Coupe	Heckantrieb	Benzin	563	765	Mar 2020	-	2024-03-01	140071
Mclaren	Speedtail	4.0 Hybrid	Coupe	Heckantrieb	Benzin/Elektro	787	1070	Dec 2019	-	2024-05-01	140074
Ferrari	Roma	3.9	Coupe	Heckantrieb	Benzin	456	620	Apr 2020	-	2024-03-01	140095
Toyota	Rav 4 v	2.5 Hybrid AWD	SUV	Allrad	Benzin/Elektro	163	222	Dec 2018	-	2024-03-01	140099
Seat	Leon	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	140109
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	339	461	Jan 2019	May 2023	2026-03-01	140119
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	340	462	May 2017	May 2023	2026-03-01	140120
Seat	Leon	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	110	150	Mar 2020	-	2024-03-01	140121
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Apr 2020	-	2024-03-01	140122
Morgan	Plus four	2	Cabriolet	Heckantrieb	Benzin	190	258	Mar 2020	-	2024-03-01	140123
Morgan	Plus six	3	Cabriolet	Heckantrieb	Benzin	250	340	Mar 2019	-	2024-03-01	140124
Renault	Master iii	2.3 DCI 180 FWD	Bus	Frontantrieb	Diesel	132	179	Jul 2019	Dec 2024	2026-03-01	140210
Hyundai	Tucson	2.0 Allrad	SUV	Allrad	Benzin	114	155	Jun 2015	Sep 2020	2024-03-01	140308
Mercedes-benz	Sprinter 3,5-T	Esprinter 312	Kasten	Frontantrieb	Elektro	85	116	Feb 2020	Dec 2023	2025-12-01	140321
Piaggio	Porter	1.3 LPG	Bus	Heckantrieb	Benzin/Autogas (LPG)	61	83	Nov 2015	-	2024-03-01	140328
Lexus	Es	300h	Stufenheck	Frontantrieb	Benzin/Elektro	160	218	Jul 2018	-	2024-03-01	140357
Lexus	Lc	500h	Coupe	Heckantrieb	Benzin/Elektro	264	359	May 2017	-	2025-06-01	140360
Lexus	Rx	450h	SUV	Frontantrieb	Benzin/Elektro	220	299	Mar 2009	Sep 2015	2025-12-01	140361
Lexus	Rx	450h AWD	SUV	Allrad	Benzin/Elektro	220	299	Mar 2009	Sep 2015	2025-12-01	140362
Lexus	Ls	500h AWD	Stufenheck	Allrad	Benzin/Elektro	264	359	Nov 2017	-	2024-03-01	140365
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	128	174	Apr 2020	-	2024-03-01	140366
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	128	174	Apr 2020	-	2024-03-01	140367
Lexus	Ux	300e	SUV	Frontantrieb	Elektro	150	204	Apr 2020	-	2024-03-01	140369
Opel	Insignia b grand sport	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	107	145	Apr 2020	-	2024-03-01	140375
Opel	Insignia b grand sport	2	Schrägheck	Frontantrieb	Benzin	147	200	Apr 2020	-	2024-03-01	140376
Opel	Insignia b grand sport	2.0 GSI 4X4	Schrägheck	Allrad	Benzin	169	230	Apr 2020	-	2024-03-01	140377
Opel	Insignia b sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	128	174	Apr 2020	-	2024-03-01	140378
Opel	Insignia b sports tourer	2	Kombi	Frontantrieb	Benzin	147	200	Apr 2020	-	2024-03-01	140379
Opel	Insignia b sports tourer	2.0 4X4	Kombi	Allrad	Benzin	169	230	Apr 2020	-	2024-03-01	140380
E.go	Life	60	Schrägheck	Heckantrieb	Elektro	57	77	Apr 2019	-	2024-03-01	140382
Toyota	Proace	2.0 D4D 4X4	Bus	Allrad	Diesel	110	150	Apr 2018	Dec 2022	2026-01-01	140383
Alpina	B3	Biturbo Allrad	Stufenheck	Allrad	Benzin	340	462	Sep 2019	Dec 2025	2026-06-01	140384
Dacia	Sandero	1.0 TCE 100	Schrägheck	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140386
Dacia	Sandero	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140387
Dacia	Duster	1.0 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jan 2019	-	2024-03-01	140388
Dacia	Logan	1.0 TCE 100	Stufenheck	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140389
Dacia	Logan	1.0 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140390
Dacia	Logan	1.0 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140391
Dacia	Logan	1.0 TCE 100	Kombi	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140392
Audi	A6 c8 avant	30 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	100	136	Jan 2019	-	2024-03-01	140393
Audi	A6 c8	30 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	100	136	Jan 2019	-	2024-03-01	140394
Mercedes-benz	Sprinter 4-T	411 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	140395
Xpeng	P7	EV	Stufenheck	Heckantrieb	Elektro	196	266	Apr 2020	-	2024-03-01	140398
Xpeng	P7	EV Allrad	Stufenheck	Allrad	Elektro	316	430	Apr 2020	-	2026-04-01	140399
Jeep	Renegade	1.3 Phev 4XE	SUV	Allrad	Benzin/Elektro	177	240	Aug 2020	-	2024-03-01	140402
Jeep	Compass	1.3 Hybrid 4X4	SUV	Allrad	Benzin/Elektro	177	240	Apr 2020	-	2024-03-01	140403
Renault	Clio v	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jun 2019	-	2026-05-01	140404
Renault	Captur ii	LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jan 2020	-	2024-03-01	140405
Mercedes-benz	Vito tourer	124 CDI	Bus	Heckantrieb	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140406
Mercedes-benz	Vito tourer	124 CDI 4-matic	Bus	Allrad	Diesel	176	239	Apr 2020	-	2025-02-03	140408
Mercedes-benz	Vito mixto	124 CDI	Kasten	Heckantrieb	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140412
Mercedes-benz	Vito mixto	124 CDI 4-matic	Kasten	Allrad	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140413
Suzuki	Sx4 s-Cross	1.4 Hybrid	Schrägheck	Allrad	Benzin/Elektro	95	129	Aug 2019	Jun 2022	2025-06-01	140414
Suzuki	Sx4 s-Cross	1.4 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	95	129	Aug 2019	Jun 2022	2025-06-01	140416
Suzuki	Vitara	1.4 Hybrid	SUV	Allrad	Benzin/Elektro	95	129	Jul 2019	-	2024-03-01	140419
Suzuki	Vitara	1.4 Hybrid	SUV	Frontantrieb	Benzin/Elektro	95	129	Jul 2019	-	2024-03-01	140420
Ligier	Js50	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140426
Ligier	Js50	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140427
Microcar	M.go	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140428


--- Round 1 / 首次发送 ---
## 更新点

* 已按跨批次索引直接复用 7 个既有尺寸组：Seat Leon IV KL Hatchback/Wagon、Volvo S90 II、Volvo V90 II、Hyundai i10 III、BMW 3 G20 Sedan、Audi A6 C8 Sedan。
* 首次闭合并创建 3 个尺寸组：

  * Volkswagen Golf VIII Hatchback：4284 × 1789 × 1456 mm。
  * Škoda Octavia IV 五门 Liftback：4689 × 1829 × 1470 mm。
  * Kia Sorento IV MQ4：4810 × 1900 × 1700 mm。([Volkswagen Newsroom][1])
* 发动机、功率及驱动形式不同但外廓相同的记录均复用同一尺寸组，没有重复建组。
* 商用车、多轴距、多车顶及车身范围不明确的记录本轮未猜测性落盘。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：22
* READY 映射：22
* PENDING Ktype：78
* 已确认并引用尺寸组：10
* 其中跨批次复用：7
* 本轮首次创建：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139745	139745	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
139749	139749	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
139764	139764	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139765	139765	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139766	139766	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139786	139786	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
139787	139787	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
139795	139795	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139796	139796	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139797	139797	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139799	139799	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139800	139800	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139801	139801	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139834	139834	Hatchback	i10 III	AC3	5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH		READY
139880	139880	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
140003	140003	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
140004	140004	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
140024	140024	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
140109	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140121	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140122	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140394	140394	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VIII-CD1-HATCHBACK-01	4284	1789	1456	Volkswagen Newsroom - The new Golf: Design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609/design-and-dimensions-5618
EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	4689	1829	1470	ŠKODA OCTAVIA official technical specifications, 16 March 2020	https://cdn.skoda-storyboard.com/2020/03/TD-OCTAVIA-petrol-diesel-en.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700	Kia Sorento 2020 official catalogue	https://www.kia.com/content/dam/kwcms/bn/en/pdf/New-Sorento-e-Catalogue.pdf
```

## 下一步优先处理

1. 批量闭合 Porsche 911 Turbo S、Bentley Continental GT、Aston Martin Vantage、McLaren、Ferrari、Morgan 等边界明确的双门车型。
2. 闭合 Opel Insignia B Grand Sport/Sports Tourer、Lexus、Suzuki、Dacia、Jeep、Renault 等可批量复用的乘用车尺寸组。
3. 最后集中拆解 H100、Sprinter、Defender Van、Berlingo、Master、Proace、Vito 等多轴距、多车顶或客货两用分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609/design-and-dimensions-5618?utm_source=chatgpt.com "Design and dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 6 个尺寸组：Volvo V90 Cross Country、Volvo XC60 II、Opel Insignia B Grand Sport、Opel Insignia B Sports Tourer、Toyota RAV4 V、Suzuki Vitara IV。尺寸及不含后视镜宽度均已按官方资料确认。([沃尔沃汽车][1])
* 新增 15 条 READY 映射；同车身不同发动机、功率或驱动形式直接复用已闭合尺寸组。
* 未重复输出上一轮已创建的 Golf VIII、Octavia IV、Sorento IV 等尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：37
* READY 映射：37
* PENDING Ktype：63
* 已确认尺寸组：16
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139802	139802	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高车身外廓。	READY
139881	139881	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
140030	140030	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140031	140031	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140099	140099	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
140366	140366	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140367	140367	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140375	140375	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140376	140376	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140377	140377	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140378	140378	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140379	140379	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140380	140380	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140419	140419	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-01	HIGH		READY
140420	140420	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo Cars Support - V90 Cross Country Dimensions	https://www.volvocars.com/jp/support/car/v90-cross-country/18w17/article/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars Support - XC60 Dimensions	https://www.volvocars.com/jp/support/car/xc60/20w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall Insignia Model Year 2020 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/Insignia_Spec_ePG_24_July_2019_Library-1566912107.pdf
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514	Vauxhall Insignia Model Year 2020 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/Insignia_Spec_ePG_24_July_2019_Library-1566912107.pdf
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1650	Toyota Media Site - The New Toyota RAV4	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-SUZUKI-VITARA-IV-LY-SUV-01	4175	1755	1610	Global Suzuki - All-new VITARA official specifications	https://www.globalsuzuki.com/globalnews/2014/1003.html
```

## 下一步优先处理

优先批量闭合 Porsche 911 Turbo S Coupe/Cabriolet、Bentley Continental GT/GTC、Aston Martin Vantage Roadster、Ferrari Roma、McLaren 765LT/Speedtail；随后处理 Lexus 五个尺寸组及 Xpeng P7。

推进信号：CONTINUE

[1]: https://www.volvocars.com/jp/support/car/xc60/20w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/ "XC60 寸法 | Volvo Support JP"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Lexus ES VII、LC I、RX III、LS V AWD、UX 300e，以及 Porsche 911 Turbo S 992.1 Coupé/Cabriolet，共 7 个尺寸组。
* RX 450h 前驱与四驱的车身代码不同，但三维完全一致，复用同一尺寸组。
* 911 Turbo S Coupé 与 Cabriolet 高度不同，分别建组。厂商资料明确标示车宽为不含后视镜 1900 mm。([丰田官网][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：45
* READY 映射：45
* PENDING Ktype：55
* 已确认尺寸组：23
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139813	139813	Coupe	911 (992.1)	992	2	EU-PORSCHE-911-9921-TURBO-S-COUPE-01	HIGH		READY
139814	139814	Convertible	911 (992.1)	992	2	EU-PORSCHE-911-9921-TURBO-S-CONVERTIBLE-01	HIGH		READY
140357	140357	Sedan	ES VII		4	EU-LEXUS-ES-VII-SEDAN-01	HIGH		READY
140360	140360	Coupe	LC I		2	EU-LEXUS-LC-I-COUPE-01	HIGH		READY
140361	140361	SUV	RX III	GYL10W	5	EU-LEXUS-RX-III-SUV-01	HIGH	前驱车身代码。	READY
140362	140362	SUV	RX III	GYL15W	5	EU-LEXUS-RX-III-SUV-01	HIGH	四驱车身代码。	READY
140365	140365	Sedan	LS V	GVF55	4	EU-LEXUS-LS-V-AWD-SEDAN-01	HIGH	AWD车身高度边界。	READY
140369	140369	SUV	UX I		5	EU-LEXUS-UX-I-300E-SUV-01	HIGH	UX 300e电动车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-9921-TURBO-S-COUPE-01	4535	1900	1303	Porsche 911 Turbo S official brochure, effective March 2020	https://files.porsche.com/filestore/download/international/en/model-series-911-turbo-downloads-catalogue-opf/default/9e5f7775-7e4f-11ea-80c9-005056bbdc38/911-Turbo-S-brochure.pdf
EU-PORSCHE-911-9921-TURBO-S-CONVERTIBLE-01	4535	1900	1301	Porsche 911 Turbo S official brochure, effective March 2020	https://files.porsche.com/filestore/download/international/en/model-series-911-turbo-downloads-catalogue-opf/default/9e5f7775-7e4f-11ea-80c9-005056bbdc38/911-Turbo-S-brochure.pdf
EU-LEXUS-ES-VII-SEDAN-01	4975	1865	1445	Toyota Global Newsroom - The All-New Lexus ES Goes on Sale in Japan	https://global.toyota/en/newsroom/lexus/24945579.html
EU-LEXUS-LC-I-COUPE-01	4770	1920	1345	Lexus Europe - The LC Series Press Kit	https://newsroom.lexus.eu/the-lc-series-press-kit/
EU-LEXUS-RX-III-SUV-01	4770	1885	1690	Toyota GAZOO official vehicle catalogue - Lexus RX 450h	https://gazoo.com/catalog/maker/LEXUS/RX/200901/10053388/
EU-LEXUS-LS-V-AWD-SEDAN-01	5235	1900	1460	Toyota GAZOO official vehicle catalogue - Lexus LS 500h AWD	https://gazoo.com/catalog/maker/LEXUS/LS/201710/10112382/
EU-LEXUS-UX-I-300E-SUV-01	4495	1840	1545	Lexus Media Site - Lexus's First EV, the UX 300e	https://media.lexus.co.uk/lexuss-first-ev-the-ux-300e/
```

## 下一步优先处理

优先闭合 Aston Martin Vantage Roadster、Ferrari Roma、McLaren 765LT/Speedtail、Bentley Continental GT/GTC；随后批量处理 Suzuki S-Cross、Renault Clio/Captur、Jeep Renegade/Compass 和 Dacia 系列。

推进信号：CONTINUE

[1]: https://global.toyota/en/newsroom/lexus/24945579.html?utm_source=chatgpt.com "The All-New Lexus ES Goes on Sale in Japan | Lexus | Global Newsroom | Toyota Motor Corporation Official Global Website"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 首次闭合 Aston Martin Vantage Roadster、Bentley Continental GT III Coupé/Convertible、Ferrari Roma、McLaren Speedtail、XPeng P7 I，共 6 个尺寸组。
* XPeng P7 后驱与四驱版本外廓相同，共用一个尺寸组。
* McLaren 765LT 暂未落盘：现有可靠资料对 Coupé 高度存在 `1157/1159 mm` 冲突，本轮不强行选值。其余新建组已确认采用不含后视镜宽度。([Ultimate Specs][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：52
* READY 映射：52
* PENDING Ktype：48
* 已确认尺寸组：29
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139788	139788	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	HIGH	Roadster双门外廓。	READY
139829	139829	Convertible	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-CONVERTIBLE-01	HIGH	第三代Convertible外廓。	READY
139830	139830	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代Coupé外廓。	READY
140074	140074	Coupe	Speedtail		2	EU-MCLAREN-SPEEDTAIL-COUPE-01	HIGH	Speedtail三座双门固定外廓。	READY
140095	140095	Coupe	Roma I		2	EU-FERRARI-ROMA-I-COUPE-01	HIGH	Roma双门2+2外廓。	READY
140398	140398	Sedan	P7 I	E28	4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代后驱外廓。	READY
140399	140399	Sedan	P7 I	E28	4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代四驱与后驱共用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	4465	1942	1273	UltimateSpecs - Aston Martin Vantage Roadster 2020 V8	https://www.ultimatespecs.com/car-specs/Aston-Martin/127774/Aston-Martin-Vantage-Roadster-2020-V8.html
EU-BENTLEY-CONTINENTAL-GT-III-CONVERTIBLE-01	4850	1954	1399	Automobile-Catalog - 2019 Bentley Continental GT Convertible	https://www.automobile-catalog.com/car/2019/2974940/bentley_continental_gt_convertible.html
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	4850	1954	1405	Automobile-Catalog - 2019 Bentley Continental GT Coupe	https://www.automobile-catalog.com/car/2019/2606630/bentley_continental_gt.html
EU-MCLAREN-SPEEDTAIL-COUPE-01	5137	2000	1120	Auto-Data - McLaren Speedtail	https://www.auto-data.net/en/mclaren-speedtail-generation-7489
EU-FERRARI-ROMA-I-COUPE-01	4656	1974	1301	Ferrari official - Ferrari Roma technical specifications	https://www.ferrari.com/en-EN/auto/ferrari-roma
EU-XPENG-P7-I-SEDAN-01	4880	1896	1450	Auto-Data - XPENG P7 I	https://www.auto-data.net/en/xpeng-p7-generation-8996
```

## 下一步优先处理

优先批量闭合 Suzuki SX4 S-Cross、Renault Clio V/Captur II、Jeep Renegade/Compass 和 Dacia 车型；随后处理 McLaren 765LT 高度冲突及剩余商用车多轴距、车顶分支。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Aston-Martin/M11946/Vantage-Roadster-2020?utm_source=chatgpt.com "Specs for all Aston Martin Vantage Roadster 2020 versions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 首次闭合 Suzuki SX4 S-Cross Hybrid、Renault Clio V、Renault Captur II、Dacia Sandero II、Duster II、Logan II Sedan 和 Logan II MCV 共 7 个尺寸组。
* 同车身不同燃料或驱动版本直接复用尺寸组，本轮新增 11 条 READY 映射。
* 三维及不含后视镜宽度已由 Suzuki、Renault 和 Dacia 规格资料闭合。([铃木汽车][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：63
* READY 映射：63
* PENDING Ktype：37
* 已确认尺寸组：36
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140386	140386	Hatchback	Sandero II		5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH	普通版五门车身，不含Stepway。	READY
140387	140387	Hatchback	Sandero II		5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH	普通版五门车身，不含Stepway。	READY
140388	140388	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-2WD-01	HIGH	前驱车身高度边界。	READY
140389	140389	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-01	HIGH	四门轿车外廓。	READY
140390	140390	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-01	HIGH	四门轿车外廓。	READY
140391	140391	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	MCV五门旅行车外廓。	READY
140392	140392	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	MCV五门旅行车外廓。	READY
140404	140404	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	五门掀背车外廓。	READY
140405	140405	Hatchback	Captur II		5	EU-RENAULT-CAPTUR-II-HATCHBACK-01	HIGH	输入车身类型为Schrägheck。	READY
140414	140414	Hatchback	SX4 S-Cross I Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	HIGH	四驱与前驱共用车身外廓。	READY
140416	140416	Hatchback	SX4 S-Cross I Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	HIGH	前驱与四驱共用车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-SANDERO-II-HATCHBACK-01	4069	1733	1519	Dacia Sandero official brochure, May 2020	https://cdn.group.renault.com/dac/fr/brochures/mai-2020/Brochure_Sandero_052020.pdf
EU-DACIA-DUSTER-II-SUV-2WD-01	4341	1804	1693	Dacia Duster official brochure, May 2020	https://cdn.group.renault.com/dac/fr/brochures/mai-2020/Brochure_Duster_052020.pdf
EU-DACIA-LOGAN-II-SEDAN-01	4358	1733	1517	Dacia Logan official brochure	https://cdn.group.renault.com/dac/es/modelos/logan/catalogo/catalogo_logan.pdf
EU-DACIA-LOGAN-II-MCV-WAGON-01	4501	1733	1552	Dacia Logan MCV official brochure	https://cdn.group.renault.com/dac/ie/transversal-assets/brochures/model-brochures/logan-mcv-brochure-oct.pdf
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault Clio official price and specification guide, August 2019	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-08-2019.pdf
EU-RENAULT-CAPTUR-II-HATCHBACK-01	4227	1797	1576	Renault Captur official price and specification guide, July 2020	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/captur/captur-prijslijst-07-2020.pdf
EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	4300	1785	1585	Suzuki S-Cross 48V SHVS Mild Hybrid official brochure	https://suzukiauto.mk/brochures/S-CROSSBROCHURE.pdf
```

## 下一步优先处理

优先闭合 Ford EcoSport、Hyundai Elantra VII、Bestune T77、Porsche Cayenne III、E.Go Life、Morgan Plus Four/Plus Six；随后处理 Citroën Berlingo、Defender Van、Master、Sprinter、Vito 等需要拆分车身边界的记录。

推进信号：CONTINUE

[1]: https://suzukiauto.mk/brochures/S-CROSSBROCHURE.pdf?utm_source=chatgpt.com "All photographs in this brochure were taken with ... - Suzuki"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 首次闭合 Bestune T77 Pro、Ford EcoSport II Facelift、Hyundai Elantra VII、Porsche Cayenne III E-Hybrid、Morgan Plus Four 和 Morgan Plus Six，共 6 个尺寸组。
* 新增 7 条 READY 映射；两条 Cayenne E-Hybrid Ktype 复用同一物理尺寸组。
* Ford 和 Porsche 资料分别列出车身宽度与含后视镜宽度；其余车型采用厂商技术规格中的整车外廓宽度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：70
* READY 映射：70
* PENDING Ktype：30
* 已确认尺寸组：42
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139781	139781	SUV	T77 I		5	EU-BESTUNE-T77-I-SUV-01	HIGH	T77 Pro五门SUV外廓。	READY
139824	139824	SUV	EcoSport II Facelift	B515	5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	2017年改款后的欧洲版外廓。	READY
139857	139857	Sedan	Elantra VII	CN7	4	EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	HIGH	CN7四门轿车外廓。	READY
140119	140119	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	HIGH	第三代标准SUV版E-Hybrid外廓。	READY
140120	140120	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	HIGH	第三代标准SUV版E-Hybrid外廓。	READY
140123	140123	Convertible	CX-Generation Plus Four	CX	2	EU-MORGAN-PLUS-FOUR-CX-CONVERTIBLE-01	HIGH	CX-Generation双门敞篷外廓。	READY
140124	140124	Convertible	CX-Generation Plus Six	CX	2	EU-MORGAN-PLUS-SIX-CX-CONVERTIBLE-01	HIGH	CX-Generation双门敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BESTUNE-T77-I-SUV-01	4525	1845	1615	Bestune T77 official brochure	https://www.bestune.bh/brochure/bestune-t77.pdf
EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	4096	1765	1653	Ford EcoSport official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-ECOSPORT.pdf
EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	4676	1826	1415	Hyundai Motor America 2021 Elantra Specifications	https://www.hyundainews.com/assets/documents/original/50451-446532021ElantraSpecifications20220713.pdf
EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	4918	1983	1696	Porsche Cayenne E-Hybrid official technical data MY N 04/2021	https://newsroom.porsche.com/dam/jcr%3Ac8bd6fb1-ba9e-4d7b-baef-a1cfbe33b565/PAG_Cayenne_E-Hybrid_TD_EN.pdf
EU-MORGAN-PLUS-FOUR-CX-CONVERTIBLE-01	3830	1650	1250	Morgan Plus Four official technical specification	https://morgan-motor.com/models/plus/plus-four/
EU-MORGAN-PLUS-SIX-CX-CONVERTIBLE-01	3890	1756	1220	Morgan Plus Six official technical specification	https://morgan-motor.com/models/past-models/plus-six/
```

## 下一步优先处理

优先闭合 Audi A6 C8 Avant、Alpina B3 G20、Jeep Renegade/Compass、McLaren 765LT、Ligier JS50 和 Microcar M.Go；随后集中拆解 Berlingo、Defender Van、Sprinter、Master、Proace、Vito 等多轴距或客货车分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 首次闭合 Audi A6 C8 Avant、Alpina B3 G20 Sedan 和 Ligier JS50 I Facelift；两条 Ligier Ktype 复用同一尺寸组。([audi.com][1])
* Jeep Renegade 4xe 240 hp 与 Compass 4xe 240 hp 均覆盖标准高度和 Trailhawk 高车身，分别拆为两个物理分支，不保留无后缀基础行。([Top Gear][2])
* 本轮新增 8 条 READY 映射、7 个尺寸组；未重复输出此前已闭合尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：76
* READY 映射：78
* PENDING Ktype：24
* 已确认尺寸组：49
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140384	140384	Sedan	B3 G20	G20	4	EU-ALPINA-B3-G20-SEDAN-01	HIGH		READY
140393	140393	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-WAGON-01	HIGH		READY
140402_standard	140402	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-SUV-STANDARD-01	HIGH	240 hp标准高度分支。	READY
140402_trailhawk	140402	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-SUV-TRAILHAWK-01	HIGH	Trailhawk加高外廓分支。	READY
140403_standard	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-SUV-STANDARD-01	HIGH	240 hp标准高度分支。	READY
140403_trailhawk	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-SUV-TRAILHAWK-01	HIGH	Trailhawk加高外廓分支。	READY
140426	140426	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
140427	140427	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B3-G20-SEDAN-01	4719	1827	1440	CarExpert - 2020 BMW Alpina B3 specifications	https://www.carexpert.com.au/bmw-alpina/b3/2020-3l-sedan-4x4-petrol-automatic-joooafwm20210701
EU-AUDI-A6-C8-WAGON-01	4939	1886	1467	Audi official A6 Avant dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-avant-1400
EU-JEEP-RENEGADE-I-FACELIFT-SUV-STANDARD-01	4236	1805	1692	Jeep Renegade 4xe PHEV Series 0 product guide	https://www.nearyslusk.ie/images/new-brands/jeep/renegade-phev.brochure.pdf
EU-JEEP-RENEGADE-I-FACELIFT-SUV-TRAILHAWK-01	4236	1805	1718	Auto Express - Jeep Renegade 4xe 240 Trailhawk specifications	https://www.autoexpress.co.uk/jeep/renegade/prices-specs/94034/1.3-turbo-4xe-phev-240-trailhawk-5dr-auto
EU-JEEP-COMPASS-II-SUV-STANDARD-01	4394	1819	1649	Jeep Netherlands Compass 4xe official price and specification list, August 2020	https://www.jeep.nl/content/dam/jeep/nl/brochure/compass/pricelist/Jeep-Compass-4xe-1-augustus-2020.pdf
EU-JEEP-COMPASS-II-SUV-TRAILHAWK-01	4394	1819	1664	Jeep Netherlands Compass 4xe official price and specification list, August 2020	https://www.jeep.nl/content/dam/jeep/nl/brochure/compass/pricelist/Jeep-Compass-4xe-1-augustus-2020.pdf
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	2890	1500	1466	Ligier official JS50 technical specifications	https://small-cars.ligier.fr/product/js50/
```

## 下一步优先处理

优先闭合 Suzuki Ignis III、Hyundai Tucson、E.Go Life、Nissan Cedric 和 Piaggio Porter；随后解决 McLaren 765LT 的 `1157/1193 mm` 高度冲突，并集中拆分 Berlingo、Defender Van、Sprinter、Master、Proace 与 Vito 的多轴距或车顶分支。([automobile-catalog.com][3])

推进信号：CONTINUE

[1]: https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-a6-avant-tfsi-e-1401/download?utm_source=chatgpt.com "A6 Avant TFSI e MA Abmessungen 0523"
[2]: https://www.topgear.com/car-reviews/jeep/renegade/13-turbo-4xe-phev-240-trailhawk-5dr-auto/spec?utm_source=chatgpt.com "Jeep Renegade 1.3 Turbo 4xe PHEV 240 Trailhawk 5dr Auto"
[3]: https://www.automobile-catalog.com/car/2021/2975465/mclaren_765lt_coupe.html?utm_source=chatgpt.com "2021 McLaren 765LT (d-cl. 7) (model for Europe North ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Suzuki Ignis III 两种真实外廓：基础 SZ3 为 1660 mm 宽，SZ-T/SZ5 为 1690 mm 宽。前驱 Ktype 拆成两个派生分支；Allgrip 只关联 1690 mm 宽组。([Acorn Group][1])
* 闭合 McLaren 765LT Coupé，采用 Automobile-Catalog 明确标注的不含后视镜宽度 1930 mm，解决此前把折叠后视镜宽度误作车宽的冲突。([汽车目录][2])
* 闭合 Hyundai Tucson III TL；官方技术资料给出长度 4475 mm、车身宽度 1850 mm，并单独列出含后视镜宽度 2065 mm。
* 闭合 e.GO Life 60；采用对应 2020 年 21.5 kWh、57 kW 版本的不含后视镜宽度。([汽车目录档案][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：81
* READY 映射：84
* PENDING Ktype：19
* 已确认尺寸组：54
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140066_sz3	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	HIGH	SZ3基础版1660 mm车身宽度分支。	READY
140066_szt_sz5	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	HIGH	SZ-T及SZ5的1690 mm车身宽度分支。	READY
140067	140067	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	HIGH	Allgrip对应1690 mm宽外廓。	READY
140071	140071	Coupe	765LT		2	EU-MCLAREN-765LT-COUPE-01	HIGH		READY
140308	140308	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
140382	140382	Hatchback	Life I		3	EU-EGO-LIFE-I-HATCHBACK-01	MEDIUM	Life 60的21.5 kWh、57 kW车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	3700	1660	1605	Suzuki Ignis official UK brochure	https://www.acorn-group.co.uk/uploads/brochures/suzuki_ignis_brochure.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	3700	1690	1605	Suzuki Ignis official UK brochure	https://www.acorn-group.co.uk/uploads/brochures/suzuki_ignis_brochure.pdf
EU-MCLAREN-765LT-COUPE-01	4600	1930	1157	Automobile-Catalog - 2020 McLaren 765LT Coupe	https://www.automobile-catalog.com/car/2020/2975465/mclaren_765lt_coupe.html
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1650	Hyundai Tucson official technical data, December 2019	https://www.hyundai.news/newsroom/dam/eu/uk/20200115_presskits_update/hyundai_tucson_technical_data_dec19.pdf
EU-EGO-LIFE-I-HATCHBACK-01	3345	1728	1588	e.GO Life official product information; Engine in Detail - e.GO Life 60 21.5 kWh 2020	https://autocatalogarchive.com/wp-content/uploads/2019/09/e.GO-Life-2019-INT.pdf;https://www.engineindetail.com/pae/e-go-life-60-21-5-kwh-2020
```

## 下一步优先处理

集中处理剩余 19 个 Ktype：先闭合 Nissan Cedric、Microcar M.Go 和 Piaggio Porter；随后按轴距、车顶及客货版本统一拆解 Citroën Berlingo、Land Rover Defender Van、Renault Master、Mercedes-Benz Sprinter/eSprinter/Vito 与 Toyota Proace。

推进信号：CONTINUE

[1]: https://www.acorn-group.co.uk/uploads/brochures/suzuki_ignis_brochure.pdf?utm_source=chatgpt.com "Suzuki Ignis Brochure"
[2]: https://www.automobile-catalog.com/car/2020/2975465/mclaren_765lt_coupe.html?utm_source=chatgpt.com "2020 McLaren 765LT Coupe (d-cl. 7)"
[3]: https://autocatalogarchive.com/wp-content/uploads/2019/09/e.GO-Life-2019-INT.pdf?utm_source=chatgpt.com "Product information"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 首次闭合 Microcar M.Go IV（M.Go 6）和 Piaggio Porter Window Van 两个尺寸组，新增 2 条 READY 映射。
* M.Go 0.5 的 2020 起始时间、6 kW 动力及 M.Go 6 外廓已对应闭合；官方资料给出 2999 × 1500 × 1560 mm。
* Porter Bus 按四座 Window Van 物理车身落盘，外廓为 3400 × 1395 × 1870 mm。Piaggio 资料将 Window Van 与其他底盘形式分别列示。
* Nissan Cedric 430 暂未落盘：欧洲出口车型的保险杠外廓与日产本土 430 Sedan 数据存在市场边界差异，不能直接复用本土尺寸。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* READY 映射：86
* PENDING Ktype：17
* 已确认尺寸组：56
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140328	140328	MPV	Porter I Facelift		5	EU-PIAGGIO-PORTER-I-FACELIFT-WINDOW-VAN-01	HIGH	四座Window Van客货车外廓。	READY
140428	140428	Hatchback	M.Go IV		3	EU-MICROCAR-MGO-IV-HATCHBACK-01	HIGH	M.Go 6三门轻型四轮车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PIAGGIO-PORTER-I-FACELIFT-WINDOW-VAN-01	3400	1395	1870	Piaggio Porter ElectricPower official brochure - Window Van technical specifications	https://piaggiocommercialuk.com/wp-content/uploads/2018/02/Brochure-Porter_Electric-Power.pdf
EU-MICROCAR-MGO-IV-HATCHBACK-01	2999	1500	1560	Ligier Group Deutschland Microcar DUÉ-M.GO official price and equipment list, May 2022	https://www.ligier.de/wp-content/uploads/sites/6/2022/05/PreiseAusstattung_Microcar_DUE_MGO_2022_05.pdf
```

## 下一步优先处理

集中拆解剩余 17 个 Ktype：先解决 Nissan Cedric 欧洲出口外廓和 Citroën Berlingo B9 客货边界；随后一次性闭合 Defender Van 90/110、Master、Sprinter/eSprinter、Proace及Vito的轴距、车顶和客货版本分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 首次闭合 Nissan Cedric 430 出口版 280C Sedan、Citroën E-Berlingo Multispace、Citroën Berlingo II Multispace PureTech 110 和 Mercedes-Benz eSprinter 312 L2H2，共 4 个尺寸组。
* E-Berlingo 电动版官方资料确认车身高度为 1822 mm，不能与高度 1801 mm 的普通 B9 Multispace 共用尺寸组。两者车宽均为不含后视镜的 1810 mm。
* Cedric 本轮采用与输入 2.8 L、1980–1983 时段对应的欧洲出口版 Datsun 280C Sedan 外廓，不再使用日本市场 2.0 L Hardtop 数据。([汽车目录][1])
* eSprinter 312 的 85 kW、L2H2 固定外廓已由对应型式认证记录闭合。([SwissCarInfo][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* READY 映射：90
* PENDING Ktype：13
* 已确认尺寸组：60
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139779	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-01	HIGH	欧洲出口版Datsun 280C四门轿车外廓。	READY
139908	139908	MPV	Berlingo II Facelift	B9	5	EU-CITROEN-BERLINGO-II-B9-ELECTRIC-MPV-01	HIGH	E-Berlingo Multispace电动乘用版外廓。	READY
139939	139939	MPV	Berlingo II Facelift	B9	5	EU-CITROEN-BERLINGO-II-B9-MULTISPACE-MPV-01	HIGH	PureTech 110 Multispace乘用版外廓。	READY
140321	140321	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-ESPRINTER-L2H2-VAN-01	HIGH	eSprinter 312固定L2H2前驱厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-CEDRIC-430-SEDAN-01	4815	1715	1430	Automobile-Catalog - 1980 Datsun 280C Sedan	https://www.automobile-catalog.com/car/1980/2148455/datsun_280c_sedan.html
EU-CITROEN-BERLINGO-II-B9-ELECTRIC-MPV-01	4380	1810	1822	Citroën E-Berlingo Multispace official brochure, April 2017	https://www.citroen.es/content/dam/citroen/spain/pdf/catalogos/E_BERLINGO_ELECTRIC.pdf
EU-CITROEN-BERLINGO-II-B9-MULTISPACE-MPV-01	4380	1810	1801	Automobile-Catalog - 2018 Citroën Berlingo Multispace PureTech 110	https://www.automobile-catalog.com/car/2018/2560235/citroen_berlingo_multispace_puretech_110.html
EU-MERCEDES-BENZ-SPRINTER-III-W910-ESPRINTER-L2H2-VAN-01	5932	2020	2638	SwissCarInfo - Mercedes-Benz eSprinter 85 kW EU type approval e1*2007/46*1760*06	https://swisscarinfo.ch/en/vehicle/eu-359414-mercedes-benz-esprinter
```

## 下一步优先处理

集中闭合剩余 13 个 Ktype：先拆分 Defender Van 90/110；随后按长度、轴距和车顶处理 Sprinter Tourer/Chassis Cab、Master Bus、Proace Bus 与 Vito Tourer/Mixto，最后解决 Hyundai H100 Pritsche/Fahrgestell 的驾驶室和轴距边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/2148455/datsun_280c_sedan.html?utm_source=chatgpt.com "1980 Datsun 280C Sedan Specs Review (92 kW / 125 PS ..."
[2]: https://swisscarinfo.ch/en/vehicle/eu-359414-mercedes-benz-esprinter?utm_source=chatgpt.com "e1*2007/46*1760*06 - Mercedes-Benz eSprinter Electric 85 kW | SwissCarInfo"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已确认 4 个 Defender Van Ktype 均覆盖 **Defender 90 与 Defender 110 两种物理外廓**，因此每个 Ktype 拆分为两个派生映射，不保留无后缀基础行。
* Land Rover 2020 官方技术规格分别列出 90 和 110，并确认 P300、P400、D200、D240 四套动力均存在于两种车身中。90 采用含原厂后置备胎的最大长度 4583 mm、车身无后视镜宽度 1996 mm、最大标准高度 1974 mm；110 为 5018 × 1996 × 1967 mm。
* 本轮新增 8 条 READY 映射、2 个尺寸组；未重复输出此前尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射：98
* PENDING Ktype：9
* 已确认尺寸组：62
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139927_90	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139927_110	139927	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139928_90	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139928_110	139928	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139929_90	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139929_110	139929	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139930_90	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139930_110	139930	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	4583	1996	1974	Land Rover 2020 Model Year Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	5018	1996	1967	Land Rover 2020 Model Year Defender 110 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
```

## 下一步优先处理

集中闭合剩余 9 个 Ktype：优先按 Compact/Long/Extra Long 拆分 Vito Tourer 与 Vito Mixto；随后处理 Renault Master Bus、Toyota Proace Bus、Sprinter Tourer、Sprinter Chassis Cab 和 Hyundai H100 的轴距、车顶及底盘分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已确认 Vito 124 CDI Tourer 与 Mixto 均覆盖 Compact、Long、Extra Long 三种物理外廓；后驱和 4MATIC 不改变对应长度分支的标准车身三维。
* 四个 Ktype 各拆分为三个稳定派生映射，共新增 12 条 READY 映射。
* 三种外廓统一复用 3 个尺寸组：4895、5140、5370 mm；车身宽度均为不含后视镜 1928 mm，标准高度均为 1910 mm。奔驰 2020 年 Tourer 资料的尺寸图同时列明 1928 mm 车身宽度和 2249 mm 含后视镜宽度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射：110
* PENDING Ktype：5
* 已确认尺寸组：65
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140406_compact	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	Compact短车身外廓。	READY
140406_long	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	Long车身外廓。	READY
140406_extralong	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	Extra Long长轴车身外廓。	READY
140408_compact	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	4MATIC Compact短车身外廓。	READY
140408_long	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	4MATIC Long车身外廓。	READY
140408_extralong	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	4MATIC Extra Long长轴车身外廓。	READY
140412_compact	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	Mixto Compact短车身外廓。	READY
140412_long	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	Mixto Long车身外廓。	READY
140412_extralong	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	Mixto Extra Long长轴车身外廓。	READY
140413_compact	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	4MATIC Mixto Compact短车身外廓。	READY
140413_long	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	4MATIC Mixto Long车身外廓。	READY
140413_extralong	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	4MATIC Mixto Extra Long长轴车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	5140	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
```

## 下一步优先处理

集中闭合最后 5 个 Ktype：Hyundai H100 Pritsche/Fahrgestell、Mercedes-Benz Sprinter 4-T Tourer、Renault Master III Bus、Toyota Proace Bus 和 Mercedes-Benz Sprinter 4-T Pritsche/Fahrgestell；优先复用既有 Master 尺寸组，再拆解 Sprinter、Proace 与 H100 的轴距和车身分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* Ktype `140210` 已闭合：`2.3 dCi 180 FWD` 在对应时期只配置于 **9 座 Master Kombi L2H2**，可直接复用既有 `EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01`，无需重新抓取或创建尺寸组。([uniqehorn.eu][1])
* Toyota Proace 4×4 已锁定为 Medium 车身，但型式认证只给出 `1881–1940 mm` 高度范围，尚不能落盘单一标准高度。
* Sprinter Tourer、Sprinter Pritsche/Fahrgestell 与 Hyundai H100 仍存在长度、车顶或驾驶室分支，未进行猜测性合并。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射：111
* PENDING Ktype：4
* 已确认尺寸组：65
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140210	140210	MPV	Master III Phase III			EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	HIGH	9座Kombi L2H2外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

优先确认 Toyota Proace Medium 4×4 的单一量产高度；随后拆解 Mercedes-Benz Sprinter 414 CDI Tourer、Sprinter 411 CDI Pritsche/Fahrgestell，以及 Hyundai H100 的轴距、驾驶室和货台分支。

推进信号：CONTINUE

[1]: https://www.uniqehorn.eu/carmanager/res/files/PL_Master_VP_NEU_01_20.pdf "PL_Master_VP_01_20"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 闭合 Hyundai H100/Porter II `HR` 的 4 个 2.5 TCI 工厂外廓分支：标准驾驶室长轴低货台、标准驾驶室长轴高货台、双排驾驶室长轴低货台、标准驾驶室超长轴低货台。2.5 柴油不纳入仅限 2.6 发动机的超长轴 Super Cab。整车宽度均为不含后视镜 1740 mm，高度均为 1970 mm。
* 闭合 Toyota Proace Verso 4×4 的 Medium 与 Long 两种乘用车外廓。Dangel 四驱改装提高离地间隙 40 mm，对应官方规格中的 1940 mm 高度；两种长度的无后视镜宽度均为 1920 mm。
* 本轮新增 6 条 READY 映射和 6 个尺寸组，未重复输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：117
* PENDING Ktype：2
* 已确认尺寸组：71
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139767_std_lwb_lowdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-LOWDECK-01	HIGH	标准驾驶室、长轴、低货台外廓。	READY
139767_std_lwb_highdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-HIGHDECK-01	HIGH	标准驾驶室、长轴、高货台外廓。	READY
139767_double_lwb_lowdeck	139767	Pickup	H100 II	HR	4	EU-HYUNDAI-H100-II-HR-PICKUP-DOUBLE-LWB-LOWDECK-01	HIGH	双排驾驶室、长轴、低货台外廓。	READY
139767_std_xlwb_lowdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-XLWB-LOWDECK-01	HIGH	标准驾驶室、超长轴、低货台外廓。	READY
140383_medium	140383	MPV	Proace II	V61T	5	EU-TOYOTA-PROACE-II-VERSO-4X4-MEDIUM-01	HIGH	Medium四驱乘用版外廓。	READY
140383_long	140383	MPV	Proace II	V61T	5	EU-TOYOTA-PROACE-II-VERSO-4X4-LONG-01	HIGH	Long四驱乘用版外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-LOWDECK-01	4850	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-HIGHDECK-01	4850	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-DOUBLE-LWB-LOWDECK-01	4810	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-STD-XLWB-LOWDECK-01	5175	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-TOYOTA-PROACE-II-VERSO-4X4-MEDIUM-01	4959	1920	1940	Toyota Austria Proace Verso official price and specification list, September 2021; Toyota Austria Proace Verso official dimensions	https://www.denzel.at/sites/denzel.at/files/downloads/Toyota%20Proace%20Verso%20Preisliste%20Stand%2009-2021.pdf;https://localform.toyota.at/pdf/pricelist/2023/WEB_PL_Proace_Verso_2308.pdf
EU-TOYOTA-PROACE-II-VERSO-4X4-LONG-01	5309	1920	1940	Toyota Austria Proace Verso official price and specification list, September 2021; Toyota Austria Proace Verso official dimensions	https://www.denzel.at/sites/denzel.at/files/downloads/Toyota%20Proace%20Verso%20Preisliste%20Stand%2009-2021.pdf;https://localform.toyota.at/pdf/pricelist/2023/WEB_PL_Proace_Verso_2308.pdf
```

## 下一步优先处理

集中闭合最后 2 个 Ktype：`139926` Sprinter 414 CDI 4-T Tourer 与 `140395` Sprinter 411 CDI 4-T Pritsche/Fahrgestell；按实际可用长度、轴距、车顶及驾驶室分支拆分。完成后立即执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* `139926` 已按实际覆盖的 Sprinter 4-T Tourer 车身拆为 4 个分支：L1H1、L2H1、L2H2、L3H2。对应车身代码分别为 `907.741`、`907.743`、`907.743`、`907.745`；官方资料确认三种车长、两种车顶高度及 2020 mm 不含后视镜车宽。([DENSO][1])
* `140395` 已按 `910.141/910.143` 覆盖范围拆为 L1 底盘驾驶室、L2 底盘驾驶室和 L2 原厂平板货车三个分支。官方尺寸图分别给出车长、车身宽度和高度，并单独标示含后视镜宽度 2345 mm。([Schaeffler 车辆寿命解决方案][2])
* 最后 2 个 PENDING Ktype 已全部闭合，当前数据阶段达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：124
* PENDING Ktype：0
* 已确认尺寸组：78
* 本轮首次创建尺寸组：7
* 数据阶段完成；下一轮只执行一次机械收尾并输出最终完整 TSV 与指定下载链接。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139926_l1h1	139926	MPV	Sprinter III	907.741		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	HIGH	L1H1短轴标准顶Tourer外廓。	READY
139926_l2h1	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	HIGH	L2H1中轴标准顶Tourer外廓。	READY
139926_l2h2	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	HIGH	L2H2中轴高顶Tourer外廓。	READY
139926_l3h2	139926	MPV	Sprinter III	907.745		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	HIGH	L3H2长轴高顶Tourer外廓。	READY
140395_l1_chassis	140395	Pickup	Sprinter III	910.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L1-01	HIGH	L1前驱单排底盘驾驶室。	READY
140395_l2_chassis	140395	Pickup	Sprinter III	910.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L2-01	HIGH	L2前驱单排底盘驾驶室。	READY
140395_l2_dropside	140395	Pickup	Sprinter III	910.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-DROPSIDE-L2-01	HIGH	L2前驱原厂单排平板货车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	5267	2020	2360	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	5932	2020	2360	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	5932	2020	2633	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	6967	2020	2633	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L1-01	5321	2020	2302	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L2-01	5986	2020	2292	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-DROPSIDE-L2-01	6146	2099	2266	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
```

## 下一步优先处理

执行唯一一次轻量机械收尾：汇总全部 124 条映射与 78 个被引用尺寸组，检查固定表头、主键唯一、引用闭合及来源非空，然后直接生成两张最终完整 TSV 和两个指定 sandbox 下载文件。

推进信号：CONTINUE

[1]: https://www.denso-am.eu/catalog/pv/139926?utm_source=chatgpt.com "Car parts for MERCEDES-BENZ SPRINTER 4-t Tourer Bus ..."
[2]: https://vehiclelifetimesolutions.schaeffler.com/en/catalog/spare-parts/mercedes-benz/sprinter-4-t-platform-chassis-b907-b910/s-TA-38713?page=2&utm_source=chatgpt.com "Schaeffler Vehicle Lifetime Solutions"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 已完成唯一一次机械收尾。
* Ktype 映射表：124 行，覆盖 100 个输入 Ktype，`id` 全部唯一，全部为 `READY`。
* DIMENSION_GROUP 表：79 个唯一尺寸组。此前口头统计的 78 未计入复用的 Master L2H2 组，本次已按实际引用修正。
* 124 条映射引用全部闭合；尺寸组无孤立记录，三维、来源和 URL 均非空。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* READY Ktype：100
* READY 映射：124
* PENDING：0
* DIMENSION_GROUP：79
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139745	139745	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
139749	139749	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
139764	139764	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139765	139765	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139766	139766	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	HIGH	五门liftback外廓。	READY
139767_std_lwb_lowdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-LOWDECK-01	HIGH	标准驾驶室、长轴、低货台外廓。	READY
139767_std_lwb_highdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-HIGHDECK-01	HIGH	标准驾驶室、长轴、高货台外廓。	READY
139767_double_lwb_lowdeck	139767	Pickup	H100 II	HR	4	EU-HYUNDAI-H100-II-HR-PICKUP-DOUBLE-LWB-LOWDECK-01	HIGH	双排驾驶室、长轴、低货台外廓。	READY
139767_std_xlwb_lowdeck	139767	Pickup	H100 II	HR	2	EU-HYUNDAI-H100-II-HR-PICKUP-STD-XLWB-LOWDECK-01	HIGH	标准驾驶室、超长轴、低货台外廓。	READY
139779	139779	Sedan	Cedric V	430	4	EU-NISSAN-CEDRIC-430-SEDAN-01	HIGH	欧洲出口版Datsun 280C四门轿车外廓。	READY
139781	139781	SUV	T77 I		5	EU-BESTUNE-T77-I-SUV-01	HIGH	T77 Pro五门SUV外廓。	READY
139786	139786	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
139787	139787	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH		READY
139788	139788	Convertible	Vantage (2018)		2	EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	HIGH	Roadster双门外廓。	READY
139795	139795	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139796	139796	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139797	139797	Sedan	S90 II	SPA	4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
139799	139799	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139800	139800	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139801	139801	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139802	139802	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高车身外廓。	READY
139813	139813	Coupe	911 (992.1)	992	2	EU-PORSCHE-911-9921-TURBO-S-COUPE-01	HIGH		READY
139814	139814	Convertible	911 (992.1)	992	2	EU-PORSCHE-911-9921-TURBO-S-CONVERTIBLE-01	HIGH		READY
139824	139824	SUV	EcoSport II Facelift	B515	5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH	2017年改款后的欧洲版外廓。	READY
139829	139829	Convertible	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-CONVERTIBLE-01	HIGH	第三代Convertible外廓。	READY
139830	139830	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代Coupé外廓。	READY
139834	139834	Hatchback	i10 III	AC3	5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH		READY
139857	139857	Sedan	Elantra VII	CN7	4	EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	HIGH	CN7四门轿车外廓。	READY
139880	139880	Wagon	V90 II	SPA	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
139881	139881	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
139908	139908	MPV	Berlingo II Facelift	B9	5	EU-CITROEN-BERLINGO-II-B9-ELECTRIC-MPV-01	HIGH	E-Berlingo Multispace电动乘用版外廓。	READY
139926_l1h1	139926	MPV	Sprinter III	907.741		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	HIGH	L1H1短轴标准顶Tourer外廓。	READY
139926_l2h1	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	HIGH	L2H1中轴标准顶Tourer外廓。	READY
139926_l2h2	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	HIGH	L2H2中轴高顶Tourer外廓。	READY
139926_l3h2	139926	MPV	Sprinter III	907.745		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	HIGH	L3H2长轴高顶Tourer外廓。	READY
139927_90	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139927_110	139927	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139928_90	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139928_110	139928	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139929_90	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139929_110	139929	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139930_90	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	HIGH	90三门短轴外廓。	READY
139930_110	139930	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	HIGH	110五门长轴外廓。	READY
139939	139939	MPV	Berlingo II Facelift	B9	5	EU-CITROEN-BERLINGO-II-B9-MULTISPACE-MPV-01	HIGH	PureTech 110 Multispace乘用版外廓。	READY
140003	140003	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
140004	140004	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
140024	140024	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
140030	140030	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140031	140031	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140066_sz3	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	HIGH	SZ3基础版1660 mm车身宽度分支。	READY
140066_szt_sz5	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	HIGH	SZ-T及SZ5的1690 mm车身宽度分支。	READY
140067	140067	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	HIGH	Allgrip对应1690 mm宽外廓。	READY
140071	140071	Coupe	765LT		2	EU-MCLAREN-765LT-COUPE-01	HIGH		READY
140074	140074	Coupe	Speedtail		2	EU-MCLAREN-SPEEDTAIL-COUPE-01	HIGH	Speedtail三座双门固定外廓。	READY
140095	140095	Coupe	Roma I		2	EU-FERRARI-ROMA-I-COUPE-01	HIGH	Roma双门2+2外廓。	READY
140099	140099	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
140109	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140119	140119	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	HIGH	第三代标准SUV版E-Hybrid外廓。	READY
140120	140120	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	HIGH	第三代标准SUV版E-Hybrid外廓。	READY
140121	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140122	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140123	140123	Convertible	CX-Generation Plus Four	CX	2	EU-MORGAN-PLUS-FOUR-CX-CONVERTIBLE-01	HIGH	CX-Generation双门敞篷外廓。	READY
140124	140124	Convertible	CX-Generation Plus Six	CX	2	EU-MORGAN-PLUS-SIX-CX-CONVERTIBLE-01	HIGH	CX-Generation双门敞篷外廓。	READY
140210	140210	MPV	Master III Phase III			EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	HIGH	9座Kombi L2H2外廓。	READY
140308	140308	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
140321	140321	Van	Sprinter III	W910		EU-MERCEDES-BENZ-SPRINTER-III-W910-ESPRINTER-L2H2-VAN-01	HIGH	eSprinter 312固定L2H2前驱厢式车外廓。	READY
140328	140328	MPV	Porter I Facelift		5	EU-PIAGGIO-PORTER-I-FACELIFT-WINDOW-VAN-01	HIGH	四座Window Van客货车外廓。	READY
140357	140357	Sedan	ES VII		4	EU-LEXUS-ES-VII-SEDAN-01	HIGH		READY
140360	140360	Coupe	LC I		2	EU-LEXUS-LC-I-COUPE-01	HIGH		READY
140361	140361	SUV	RX III	GYL10W	5	EU-LEXUS-RX-III-SUV-01	HIGH	前驱车身代码。	READY
140362	140362	SUV	RX III	GYL15W	5	EU-LEXUS-RX-III-SUV-01	HIGH	四驱车身代码。	READY
140365	140365	Sedan	LS V	GVF55	4	EU-LEXUS-LS-V-AWD-SEDAN-01	HIGH	AWD车身高度边界。	READY
140366	140366	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140367	140367	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140369	140369	SUV	UX I		5	EU-LEXUS-UX-I-300E-SUV-01	HIGH	UX 300e电动车身外廓。	READY
140375	140375	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140376	140376	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140377	140377	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140378	140378	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140379	140379	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140380	140380	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer五门旅行车外廓。	READY
140382	140382	Hatchback	Life I		3	EU-EGO-LIFE-I-HATCHBACK-01	MEDIUM	Life 60的21.5 kWh、57 kW车身外廓。	READY
140383_medium	140383	MPV	Proace II	V61T	5	EU-TOYOTA-PROACE-II-VERSO-4X4-MEDIUM-01	HIGH	Medium四驱乘用版外廓。	READY
140383_long	140383	MPV	Proace II	V61T	5	EU-TOYOTA-PROACE-II-VERSO-4X4-LONG-01	HIGH	Long四驱乘用版外廓。	READY
140384	140384	Sedan	B3 G20	G20	4	EU-ALPINA-B3-G20-SEDAN-01	HIGH		READY
140386	140386	Hatchback	Sandero II		5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH	普通版五门车身，不含Stepway。	READY
140387	140387	Hatchback	Sandero II		5	EU-DACIA-SANDERO-II-HATCHBACK-01	HIGH	普通版五门车身，不含Stepway。	READY
140388	140388	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-2WD-01	HIGH	前驱车身高度边界。	READY
140389	140389	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-01	HIGH	四门轿车外廓。	READY
140390	140390	Sedan	Logan II		4	EU-DACIA-LOGAN-II-SEDAN-01	HIGH	四门轿车外廓。	READY
140391	140391	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	MCV五门旅行车外廓。	READY
140392	140392	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	MCV五门旅行车外廓。	READY
140393	140393	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-WAGON-01	HIGH		READY
140394	140394	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-SEDAN-01	HIGH		READY
140395_l1_chassis	140395	Pickup	Sprinter III	910.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L1-01	HIGH	L1前驱单排底盘驾驶室。	READY
140395_l2_chassis	140395	Pickup	Sprinter III	910.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L2-01	HIGH	L2前驱单排底盘驾驶室。	READY
140395_l2_dropside	140395	Pickup	Sprinter III	910.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-DROPSIDE-L2-01	HIGH	L2前驱原厂单排平板货车。	READY
140398	140398	Sedan	P7 I	E28	4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代后驱外廓。	READY
140399	140399	Sedan	P7 I	E28	4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代四驱与后驱共用外廓。	READY
140402_standard	140402	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-SUV-STANDARD-01	HIGH	240 hp标准高度分支。	READY
140402_trailhawk	140402	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-SUV-TRAILHAWK-01	HIGH	Trailhawk加高外廓分支。	READY
140403_standard	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-SUV-STANDARD-01	HIGH	240 hp标准高度分支。	READY
140403_trailhawk	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-SUV-TRAILHAWK-01	HIGH	Trailhawk加高外廓分支。	READY
140404	140404	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	五门掀背车外廓。	READY
140405	140405	Hatchback	Captur II		5	EU-RENAULT-CAPTUR-II-HATCHBACK-01	HIGH	输入车身类型为Schrägheck。	READY
140406_compact	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	Compact短车身外廓。	READY
140406_long	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	Long车身外廓。	READY
140406_extralong	140406	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	Extra Long长轴车身外廓。	READY
140408_compact	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	4MATIC Compact短车身外廓。	READY
140408_long	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	4MATIC Long车身外廓。	READY
140408_extralong	140408	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	4MATIC Extra Long长轴车身外廓。	READY
140412_compact	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	Mixto Compact短车身外廓。	READY
140412_long	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	Mixto Long车身外廓。	READY
140412_extralong	140412	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	Mixto Extra Long长轴车身外廓。	READY
140413_compact	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	HIGH	4MATIC Mixto Compact短车身外廓。	READY
140413_long	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	HIGH	4MATIC Mixto Long车身外廓。	READY
140413_extralong	140413	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	HIGH	4MATIC Mixto Extra Long长轴车身外廓。	READY
140414	140414	Hatchback	SX4 S-Cross I Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	HIGH	四驱与前驱共用车身外廓。	READY
140416	140416	Hatchback	SX4 S-Cross I Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	HIGH	前驱与四驱共用车身外廓。	READY
140419	140419	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-01	HIGH		READY
140420	140420	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-01	HIGH		READY
140426	140426	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
140427	140427	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
140428	140428	Hatchback	M.Go IV		3	EU-MICROCAR-MGO-IV-HATCHBACK-01	HIGH	M.Go 6三门轻型四轮车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_401-500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450	SEAT Leon Sportstourer official technical specifications	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2020/The-new-SEAT-Leon-Technical-specifications.html
EU-VW-GOLF-VIII-CD1-HATCHBACK-01	4284	1789	1456	Volkswagen Newsroom - The new Golf: Design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609/design-and-dimensions-5618
EU-SKODA-OCTAVIA-IV-NX3-HATCHBACK-01	4689	1829	1470	ŠKODA OCTAVIA official technical specifications, 16 March 2020	https://cdn.skoda-storyboard.com/2020/03/TD-OCTAVIA-petrol-diesel-en.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-LOWDECK-01	4850	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-STD-LWB-HIGHDECK-01	4850	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-DOUBLE-LWB-LOWDECK-01	4810	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-HYUNDAI-H100-II-HR-PICKUP-STD-XLWB-LOWDECK-01	5175	1740	1970	Hyundai H-100 official global brochure; Hyundai H-100 official owner's manual	https://www.hyundai.com/content/dam/hyundai/ww/en/images/footer/downloads/commercial/e-brochure/h100-ebrochure-2020.pdf;https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/manual/h-100/2017h-100-full-version.pdf
EU-NISSAN-CEDRIC-430-SEDAN-01	4815	1715	1430	Automobile-Catalog - 1980 Datsun 280C Sedan	https://www.automobile-catalog.com/car/1980/2148455/datsun_280c_sedan.html
EU-BESTUNE-T77-I-SUV-01	4525	1845	1615	Bestune T77 official brochure	https://www.bestune.bh/brochure/bestune-t77.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700	Kia Sorento 2020 official catalogue	https://www.kia.com/content/dam/kwcms/bn/en/pdf/New-Sorento-e-Catalogue.pdf
EU-ASTON-MARTIN-VANTAGE-2018-CONVERTIBLE-01	4465	1942	1273	UltimateSpecs - Aston Martin Vantage Roadster 2020 V8	https://www.ultimatespecs.com/car-specs/Aston-Martin/127774/Aston-Martin-Vantage-Roadster-2020-V8.html
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Cars Support - S90 dimensions	https://www.volvocars.com/uk/support/car/s90/article/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Cars Support - V90 dimensions	https://www.volvocars.com/uk/support/car/v90/article/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo Cars Support - V90 Cross Country Dimensions	https://www.volvocars.com/jp/support/car/v90-cross-country/18w17/article/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-PORSCHE-911-9921-TURBO-S-COUPE-01	4535	1900	1303	Porsche 911 Turbo S official brochure, effective March 2020	https://files.porsche.com/filestore/download/international/en/model-series-911-turbo-downloads-catalogue-opf/default/9e5f7775-7e4f-11ea-80c9-005056bbdc38/911-Turbo-S-brochure.pdf
EU-PORSCHE-911-9921-TURBO-S-CONVERTIBLE-01	4535	1900	1301	Porsche 911 Turbo S official brochure, effective March 2020	https://files.porsche.com/filestore/download/international/en/model-series-911-turbo-downloads-catalogue-opf/default/9e5f7775-7e4f-11ea-80c9-005056bbdc38/911-Turbo-S-brochure.pdf
EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	4096	1765	1653	Ford EcoSport official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-ECOSPORT.pdf
EU-BENTLEY-CONTINENTAL-GT-III-CONVERTIBLE-01	4850	1954	1399	Automobile-Catalog - 2019 Bentley Continental GT Convertible	https://www.automobile-catalog.com/car/2019/2974940/bentley_continental_gt_convertible.html
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	4850	1954	1405	Automobile-Catalog - 2019 Bentley Continental GT Coupe	https://www.automobile-catalog.com/car/2019/2606630/bentley_continental_gt.html
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	Hyundai i10 official technical specifications	https://www.hyundai.news/eu/models/i10/press-kit/all-new-hyundai-i10-technical-specifications.html
EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	4676	1826	1415	Hyundai Motor America 2021 Elantra Specifications	https://www.hyundainews.com/assets/documents/original/50451-446532021ElantraSpecifications20220713.pdf
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars Support - XC60 Dimensions	https://www.volvocars.com/jp/support/car/xc60/20w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-CITROEN-BERLINGO-II-B9-ELECTRIC-MPV-01	4380	1810	1822	Citroën E-Berlingo Multispace official brochure, April 2017	https://www.citroen.es/content/dam/citroen/spain/pdf/catalogos/E_BERLINGO_ELECTRIC.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	5267	2020	2360	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	5932	2020	2360	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	5932	2020	2633	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	6967	2020	2633	Mercedes-Benz The New Sprinter model information and price list, June 2018; Mercedes-Benz Sprinter UK model information and price list, March 2020	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-LAND-ROVER-DEFENDER-L663-VAN-90-01	4583	1996	1974	Land Rover 2020 Model Year Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-VAN-110-01	5018	1996	1967	Land Rover 2020 Model Year Defender 110 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
EU-CITROEN-BERLINGO-II-B9-MULTISPACE-MPV-01	4380	1810	1801	Automobile-Catalog - 2018 Citroën Berlingo Multispace PureTech 110	https://www.automobile-catalog.com/car/2018/2560235/citroen_berlingo_multispace_puretech_110.html
EU-BMW-3-G20-SEDAN-01	4709	1827	1442	BMW 3 Series Sedan official technical data	https://www.press.bmwgroup.com/global/article/attachment/T0284887EN/415307
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall Insignia Model Year 2020 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/Insignia_Spec_ePG_24_July_2019_Library-1566912107.pdf
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514	Vauxhall Insignia Model Year 2020 official price and specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/Insignia_Spec_ePG_24_July_2019_Library-1566912107.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	3700	1660	1605	Suzuki Ignis official UK brochure	https://www.acorn-group.co.uk/uploads/brochures/suzuki_ignis_brochure.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDE-01	3700	1690	1605	Suzuki Ignis official UK brochure	https://www.acorn-group.co.uk/uploads/brochures/suzuki_ignis_brochure.pdf
EU-MCLAREN-765LT-COUPE-01	4600	1930	1157	Automobile-Catalog - 2020 McLaren 765LT Coupe	https://www.automobile-catalog.com/car/2020/2975465/mclaren_765lt_coupe.html
EU-MCLAREN-SPEEDTAIL-COUPE-01	5137	2000	1120	Auto-Data - McLaren Speedtail	https://www.auto-data.net/en/mclaren-speedtail-generation-7489
EU-FERRARI-ROMA-I-COUPE-01	4656	1974	1301	Ferrari official - Ferrari Roma technical specifications	https://www.ferrari.com/en-EN/auto/ferrari-roma
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1650	Toyota Media Site - The New Toyota RAV4	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456	SEAT Leon official technical specifications	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2020/The-new-SEAT-Leon-Technical-specifications.html
EU-PORSCHE-CAYENNE-III-SUV-EHYBRID-01	4918	1983	1696	Porsche Cayenne E-Hybrid official technical data MY N 04/2021	https://newsroom.porsche.com/dam/jcr%3Ac8bd6fb1-ba9e-4d7b-baef-a1cfbe33b565/PAG_Cayenne_E-Hybrid_TD_EN.pdf
EU-MORGAN-PLUS-FOUR-CX-CONVERTIBLE-01	3830	1650	1250	Morgan Plus Four official technical specification	https://morgan-motor.com/models/plus/plus-four/
EU-MORGAN-PLUS-SIX-CX-CONVERTIBLE-01	3890	1756	1220	Morgan Plus Six official technical specification	https://morgan-motor.com/models/past-models/plus-six/
EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	5575	2070	2499	Renault Master passenger vehicle official price and specification list, January 2020	https://www.uniqehorn.eu/carmanager/res/files/PL_Master_VP_NEU_01_20.pdf
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1650	Hyundai Tucson official technical data, December 2019	https://www.hyundai.news/newsroom/dam/eu/uk/20200115_presskits_update/hyundai_tucson_technical_data_dec19.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-ESPRINTER-L2H2-VAN-01	5932	2020	2638	SwissCarInfo - Mercedes-Benz eSprinter 85 kW EU type approval e1*2007/46*1760*06	https://swisscarinfo.ch/en/vehicle/eu-359414-mercedes-benz-esprinter
EU-PIAGGIO-PORTER-I-FACELIFT-WINDOW-VAN-01	3400	1395	1870	Piaggio Porter ElectricPower official brochure - Window Van technical specifications	https://piaggiocommercialuk.com/wp-content/uploads/2018/02/Brochure-Porter_Electric-Power.pdf
EU-LEXUS-ES-VII-SEDAN-01	4975	1865	1445	Toyota Global Newsroom - The All-New Lexus ES Goes on Sale in Japan	https://global.toyota/en/newsroom/lexus/24945579.html
EU-LEXUS-LC-I-COUPE-01	4770	1920	1345	Lexus Europe - The LC Series Press Kit	https://newsroom.lexus.eu/the-lc-series-press-kit/
EU-LEXUS-RX-III-SUV-01	4770	1885	1690	Toyota GAZOO official vehicle catalogue - Lexus RX 450h	https://gazoo.com/catalog/maker/LEXUS/RX/200901/10053388/
EU-LEXUS-LS-V-AWD-SEDAN-01	5235	1900	1460	Toyota GAZOO official vehicle catalogue - Lexus LS 500h AWD	https://gazoo.com/catalog/maker/LEXUS/LS/201710/10112382/
EU-LEXUS-UX-I-300E-SUV-01	4495	1840	1545	Lexus Media Site - Lexus's First EV, the UX 300e	https://media.lexus.co.uk/lexuss-first-ev-the-ux-300e/
EU-EGO-LIFE-I-HATCHBACK-01	3345	1728	1588	e.GO Life official product information; Engine in Detail - e.GO Life 60 21.5 kWh 2020	https://autocatalogarchive.com/wp-content/uploads/2019/09/e.GO-Life-2019-INT.pdf;https://www.engineindetail.com/pae/e-go-life-60-21-5-kwh-2020
EU-TOYOTA-PROACE-II-VERSO-4X4-MEDIUM-01	4959	1920	1940	Toyota Austria Proace Verso official price and specification list, September 2021; Toyota Austria Proace Verso official dimensions	https://www.denzel.at/sites/denzel.at/files/downloads/Toyota%20Proace%20Verso%20Preisliste%20Stand%2009-2021.pdf;https://localform.toyota.at/pdf/pricelist/2023/WEB_PL_Proace_Verso_2308.pdf
EU-TOYOTA-PROACE-II-VERSO-4X4-LONG-01	5309	1920	1940	Toyota Austria Proace Verso official price and specification list, September 2021; Toyota Austria Proace Verso official dimensions	https://www.denzel.at/sites/denzel.at/files/downloads/Toyota%20Proace%20Verso%20Preisliste%20Stand%2009-2021.pdf;https://localform.toyota.at/pdf/pricelist/2023/WEB_PL_Proace_Verso_2308.pdf
EU-ALPINA-B3-G20-SEDAN-01	4719	1827	1440	CarExpert - 2020 BMW Alpina B3 specifications	https://www.carexpert.com.au/bmw-alpina/b3/2020-3l-sedan-4x4-petrol-automatic-joooafwm20210701
EU-DACIA-SANDERO-II-HATCHBACK-01	4069	1733	1519	Dacia Sandero official brochure, May 2020	https://cdn.group.renault.com/dac/fr/brochures/mai-2020/Brochure_Sandero_052020.pdf
EU-DACIA-DUSTER-II-SUV-2WD-01	4341	1804	1693	Dacia Duster official brochure, May 2020	https://cdn.group.renault.com/dac/fr/brochures/mai-2020/Brochure_Duster_052020.pdf
EU-DACIA-LOGAN-II-SEDAN-01	4358	1733	1517	Dacia Logan official brochure	https://cdn.group.renault.com/dac/es/modelos/logan/catalogo/catalogo_logan.pdf
EU-DACIA-LOGAN-II-MCV-WAGON-01	4501	1733	1552	Dacia Logan MCV official brochure	https://cdn.group.renault.com/dac/ie/transversal-assets/brochures/model-brochures/logan-mcv-brochure-oct.pdf
EU-AUDI-A6-C8-WAGON-01	4939	1886	1467	Audi official A6 Avant dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-avant-1400
EU-AUDI-A6-C8-SEDAN-01	4939	1886	1457	Audi official A6 Sedan dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-sedan-1399
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L1-01	5321	2020	2302	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-CAB-L2-01	5986	2020	2292	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-DROPSIDE-L2-01	6146	2099	2266	Mercedes-Benz Sprinter UK model information and price list, March 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Sprinter-UK.pdf
EU-XPENG-P7-I-SEDAN-01	4880	1896	1450	Auto-Data - XPENG P7 I	https://www.auto-data.net/en/xpeng-p7-generation-8996
EU-JEEP-RENEGADE-I-FACELIFT-SUV-STANDARD-01	4236	1805	1692	Jeep Renegade 4xe PHEV Series 0 product guide	https://www.nearyslusk.ie/images/new-brands/jeep/renegade-phev.brochure.pdf
EU-JEEP-RENEGADE-I-FACELIFT-SUV-TRAILHAWK-01	4236	1805	1718	Auto Express - Jeep Renegade 4xe 240 Trailhawk specifications	https://www.autoexpress.co.uk/jeep/renegade/prices-specs/94034/1.3-turbo-4xe-phev-240-trailhawk-5dr-auto
EU-JEEP-COMPASS-II-SUV-STANDARD-01	4394	1819	1649	Jeep Netherlands Compass 4xe official price and specification list, August 2020	https://www.jeep.nl/content/dam/jeep/nl/brochure/compass/pricelist/Jeep-Compass-4xe-1-augustus-2020.pdf
EU-JEEP-COMPASS-II-SUV-TRAILHAWK-01	4394	1819	1664	Jeep Netherlands Compass 4xe official price and specification list, August 2020	https://www.jeep.nl/content/dam/jeep/nl/brochure/compass/pricelist/Jeep-Compass-4xe-1-augustus-2020.pdf
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault Clio official price and specification guide, August 2019	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/clio/clio-prijslijst-08-2019.pdf
EU-RENAULT-CAPTUR-II-HATCHBACK-01	4227	1797	1576	Renault Captur official price and specification guide, July 2020	https://cdn.group.renault.com/ren/nl/brochures-en-prijslijsten/prijzenarchief/captur/captur-prijslijst-07-2020.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	5140	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Tourer official brochure, prices effective December 2020	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-HATCHBACK-01	4300	1785	1585	Suzuki S-Cross 48V SHVS Mild Hybrid official brochure	https://suzukiauto.mk/brochures/S-CROSSBROCHURE.pdf
EU-SUZUKI-VITARA-IV-LY-SUV-01	4175	1755	1610	Global Suzuki - All-new VITARA official specifications	https://www.globalsuzuki.com/globalnews/2014/1003.html
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	2890	1500	1466	Ligier official JS50 technical specifications	https://small-cars.ligier.fr/product/js50/
EU-MICROCAR-MGO-IV-HATCHBACK-01	2999	1500	1560	Ligier Group Deutschland Microcar DUÉ-M.GO official price and equipment list, May 2022	https://www.ligier.de/wp-content/uploads/sites/6/2022/05/PreiseAusstattung_Microcar_DUE_MGO_2022_05.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_401-500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（436 行）
- 累计尺寸组：dimension_groups_final.tsv（234 行）

