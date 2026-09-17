# 任务：all 第 1901-2000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0020__674e431d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460
EU-FIAT-SCUDO-II-CHASSIS-CAB-01	5053	1895	1942
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276
EU-FIAT-SCUDO-I-MPV-LWB-01	4840	1810	1930
EU-FIAT-SCUDO-I-MPV-SWB-01	4440	1810	1940
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	5899	1990	2456
EU-NISSAN-INTERSTAR-X70-MPV-MWB-MIDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	4935	1864	1760
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02	3916	1650	1459
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jaguar	Xj	5.0 Scv8	Stufenheck	Heckantrieb	Benzin	405	550	Jun 2013	Dec 2019	2025-02-03	24106
VW	Beetle	1.4 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Oct 2011	Jul 2016	2024-03-01	24176
VW	Beetle	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Oct 2011	Jul 2016	2024-03-01	24177
Think	City	Electric	Schrägheck	Frontantrieb	Elektro	30	41	Jan 2008	-	2024-03-01	24178
VW	Beetle	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Apr 2011	Jul 2016	2024-03-01	24179
Ferrari	348 spider	3.4	Cabriolet	Heckantrieb	Benzin	235	320	Mar 1993	Dec 1995	2024-03-01	24183
Subaru	Leone	1800 4WD	Schrägheck	Allrad	Benzin	66	90	Jan 1985	Dec 1989	2024-03-01	24185
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Sep 1988	Dec 1992	2024-03-01	24190
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Jan 1993	Aug 1995	2024-03-01	24191
Nissan	Interstar	DCI 100	Bus	Frontantrieb	Diesel	74	101	Apr 2006	Mar 2011	2024-03-01	24194
Nissan	Interstar	DCI 100	Kasten	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	24195
Nissan	Interstar	DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	73	99	Feb 2004	-	2024-03-01	24196
Nissan	Interstar	DCI 115	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	115	Aug 2003	-	2024-03-01	24197
Nissan	Interstar	DCI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2006	-	2024-03-01	24198
Nissan	Interstar	DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Aug 2006	-	2024-03-01	24199
Nissan	Interstar	DCI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Nov 2003	-	2024-03-01	24200
Renault	Laguna ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	79	107	Mar 2001	Sep 2007	2024-03-01	24201
Renault	Laguna ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	79	107	Mar 2001	Dec 2007	2024-03-01	24202
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24240
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24241
Seat	Altea	2.0 Tfsi 4X4	Großraumlimousine	Allrad	Benzin	147	200	Jun 2007	May 2009	2024-03-01	24242
Seat	Altea	2.0 TDI 4X4	Großraumlimousine	Allrad	Diesel	125	170	Jun 2007	Jun 2013	2024-03-01	24243
VW	Sharan	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Sep 1995	Feb 2000	2024-03-01	24248
VW	Polo	1.6	Stufenheck	Frontantrieb	Benzin	74	101	Sep 2002	-	2024-03-01	24253
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	90	122	Aug 2005	Jul 2006	2024-03-01	24257
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Aug 2005	May 2009	2024-03-01	24259
Buick	Century	3.8 T-type	Coupe	Frontantrieb	Benzin	94	128	Oct 1986	Sep 1989	2024-03-01	24267
Buick	Century	3.8 Custom	Coupe	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1988	2024-03-01	24268
Buick	Century	3.8 Special	Kombi	Heckantrieb	Benzin	78	106	Oct 1977	Dec 1981	2024-03-01	24269
Ferrari	F50	4.7	Targa	Heckantrieb	Benzin	383	521	May 1995	Oct 1997	2024-03-01	24276
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	120	163	Jul 2013	Mar 2017	2024-03-01	24303
Seat	Leon	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Jul 2005	Aug 2013	2024-03-01	24304
Ford	Mondeo v	2.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	176	240	May 2015	Mar 2022	2026-04-01	24305
Suzuki	Jimny	1.3	Geländewagen geschlossen	Heckantrieb	Benzin	63	86	Aug 2004	-	2024-03-01	24313
Ssangyong	Musso	2.3 D	Geländewagen geschlossen	Allrad	Diesel	58	79	Mar 1993	Apr 1997	2024-03-01	24314
KIA	Bongo	2.4 Tdci	Pritsche/Fahrgestell	Heckantrieb	Diesel	69	94	Oct 2003	Dec 2012	2026-05-01	24327
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24343
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24344
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24345
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24346
Plymouth	Sundance	2.5 Duster	Coupe	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24347
Plymouth	Sundance	2.5 Turbo	Coupe	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24348
Plymouth	Sundance	3.0 Duster	Coupe	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24349
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24350
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24351
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24352
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24353
Plymouth	Sundance	2.5 Duster	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24354
Plymouth	Sundance	2.5 Turbo	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24355
Plymouth	Sundance	3.0 Duster	Stufenheck	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24356
Plymouth	Voyager / grand	3.3 LE	Großraumlimousine	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1990	2024-03-01	24357
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	63	85	Apr 2003	Nov 2009	2024-03-01	24367
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24375
BMW	I3	Electric	Schrägheck	Heckantrieb	Elektro	75	102	Aug 2013	-	2026-06-01	24378
Infiniti	Q50	50 D	Stufenheck	Heckantrieb	Diesel	125	170	Apr 2013	-	2024-03-01	24379
Fiat	Scudo	2.0 D Multijet 4X4	Bus	Allrad	Diesel	94	128	Apr 2011	Mar 2016	2024-03-01	24380
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24388
Toyota	Wish	1.8 HI	Großraumlimousine	Frontantrieb	Benzin	97	132	Apr 2003	Mar 2009	2024-03-01	24398
Aixam	500	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Dec 1997	Mar 2004	2024-03-01	24427
Aixam	A.721	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24428
Aixam	A.741	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24429
Aixam	A.751	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Jan 2005	Mar 2010	2024-03-01	24430
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jan 2006	Jul 2014	2024-03-01	24431
Opel	Vivaro a	2.0 Ecotec	Pritsche/Fahrgestell	Frontantrieb	Benzin	86	117	Aug 2006	Jul 2014	2024-03-01	24432
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Jul 2014	2024-03-01	24433
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Mar 2010	2024-03-01	24434
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	Jul 2014	2024-03-01	24435
Volvo	V70 iii	2	Kombi	Frontantrieb	Benzin	107	145	Oct 2007	Dec 2011	2024-03-01	24436
Volvo	V70 iii	3.2	Kombi	Frontantrieb	Benzin	175	238	Aug 2007	Dec 2010	2024-03-01	24437
Volvo	V70 iii	2.0 D	Kombi	Frontantrieb	Diesel	100	136	Oct 2007	Dec 2015	2024-03-01	24438
Volvo	V70 iii	D5 AWD	Kombi	Allrad	Diesel	136	185	Apr 2007	Dec 2009	2024-03-01	24439
BMW	1	120 I	Cabriolet	Heckantrieb	Benzin	125	170	Dec 2007	Oct 2013	2024-03-01	24440
BMW	1	125 I	Cabriolet	Heckantrieb	Benzin	160	218	Dec 2007	Oct 2013	2024-03-01	24441
Ford	Mondeo iv	2.3	Schrägheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24450
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24451
Ford	Mondeo iv	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24452
Ford	Mondeo iv	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24453
Ford	Mondeo iv turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24454
Ford	Mondeo iv	2.3	Stufenheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24455
Ford	Mondeo iv turnier	2.3	Kombi	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24456
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24457
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24458
Ford	S-Max	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24459
Ford	S-Max	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Jul 2007	Dec 2014	2024-03-01	24460
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Dec 2014	2024-03-01	24461
Ford	Galaxy ii	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Sep 2007	Jun 2015	2024-03-01	24462
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Jun 2015	2024-03-01	24463
Ford	Galaxy ii	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24464
VW	Caddy iii	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2005	Aug 2010	2024-03-01	24465
VW	Caddy iii	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24466
VW	Caddy iii	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24467
Chevrolet	Nubira	2.0 D	Kombi	Frontantrieb	Diesel	89	121	Jan 2007	Dec 2011	2024-03-01	24468
Chevrolet	Lacetti	2.0 D	Schrägheck	Frontantrieb	Diesel	89	121	Jan 2007	-	2024-03-01	24469
Chevrolet	Epica	2.0 D	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2007	Dec 2011	2024-03-01	24470
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	110	150	Sep 2007	-	2024-03-01	24471
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24472
Audi	Tt	2.0 TTS Quattro	Cabriolet	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24473
Jaguar	Xf i	3	Stufenheck	Heckantrieb	Benzin	175	238	Mar 2008	Apr 2015	2024-03-01	24474
Jaguar	Xf i	4.2	Stufenheck	Heckantrieb	Benzin	219	298	Mar 2008	Apr 2015	2024-03-01	24475
Jaguar	Xf i	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	306	416	Mar 2008	Apr 2015	2026-05-01	24476


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 4 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445
EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	4515	1725	1445
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460
EU-FIAT-SCUDO-II-CHASSIS-CAB-01	5053	1895	1942
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276
EU-FIAT-SCUDO-I-MPV-LWB-01	4840	1810	1930
EU-FIAT-SCUDO-I-MPV-SWB-01	4440	1810	1940
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	4810	1820	1445
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	4810	1820	1430
EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	4783	1824	1443
EU-JAGUAR-XF-I-SEDAN-X250-01	4961	1877	1460
EU-JAGUAR-XJSC-CONVERTIBLE-2D-01	4820	1793	1279
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	5899	1990	2456
EU-NISSAN-INTERSTAR-X70-MPV-MWB-MIDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	4935	1864	1760
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	4140	1640	1410
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02	3916	1650	1459
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jaguar	Xj	5.0 Scv8	Stufenheck	Heckantrieb	Benzin	405	550	Jun 2013	Dec 2019	2025-02-03	24106
VW	Beetle	1.4 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Oct 2011	Jul 2016	2024-03-01	24176
VW	Beetle	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Oct 2011	Jul 2016	2024-03-01	24177
Think	City	Electric	Schrägheck	Frontantrieb	Elektro	30	41	Jan 2008	-	2024-03-01	24178
VW	Beetle	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Apr 2011	Jul 2016	2024-03-01	24179
Ferrari	348 spider	3.4	Cabriolet	Heckantrieb	Benzin	235	320	Mar 1993	Dec 1995	2024-03-01	24183
Subaru	Leone	1800 4WD	Schrägheck	Allrad	Benzin	66	90	Jan 1985	Dec 1989	2024-03-01	24185
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Sep 1988	Dec 1992	2024-03-01	24190
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Jan 1993	Aug 1995	2024-03-01	24191
Nissan	Interstar	DCI 100	Bus	Frontantrieb	Diesel	74	101	Apr 2006	Mar 2011	2024-03-01	24194
Nissan	Interstar	DCI 100	Kasten	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	24195
Nissan	Interstar	DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	73	99	Feb 2004	-	2024-03-01	24196
Nissan	Interstar	DCI 115	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	115	Aug 2003	-	2024-03-01	24197
Nissan	Interstar	DCI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2006	-	2024-03-01	24198
Nissan	Interstar	DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Aug 2006	-	2024-03-01	24199
Nissan	Interstar	DCI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Nov 2003	-	2024-03-01	24200
Renault	Laguna ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	79	107	Mar 2001	Sep 2007	2024-03-01	24201
Renault	Laguna ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	79	107	Mar 2001	Dec 2007	2024-03-01	24202
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24240
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24241
Seat	Altea	2.0 Tfsi 4X4	Großraumlimousine	Allrad	Benzin	147	200	Jun 2007	May 2009	2024-03-01	24242
Seat	Altea	2.0 TDI 4X4	Großraumlimousine	Allrad	Diesel	125	170	Jun 2007	Jun 2013	2024-03-01	24243
VW	Sharan	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Sep 1995	Feb 2000	2024-03-01	24248
VW	Polo	1.6	Stufenheck	Frontantrieb	Benzin	74	101	Sep 2002	-	2024-03-01	24253
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	90	122	Aug 2005	Jul 2006	2024-03-01	24257
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Aug 2005	May 2009	2024-03-01	24259
Buick	Century	3.8 T-type	Coupe	Frontantrieb	Benzin	94	128	Oct 1986	Sep 1989	2024-03-01	24267
Buick	Century	3.8 Custom	Coupe	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1988	2024-03-01	24268
Buick	Century	3.8 Special	Kombi	Heckantrieb	Benzin	78	106	Oct 1977	Dec 1981	2024-03-01	24269
Ferrari	F50	4.7	Targa	Heckantrieb	Benzin	383	521	May 1995	Oct 1997	2024-03-01	24276
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	120	163	Jul 2013	Mar 2017	2024-03-01	24303
Seat	Leon	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Jul 2005	Aug 2013	2024-03-01	24304
Ford	Mondeo v	2.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	176	240	May 2015	Mar 2022	2026-04-01	24305
Suzuki	Jimny	1.3	Geländewagen geschlossen	Heckantrieb	Benzin	63	86	Aug 2004	-	2024-03-01	24313
Ssangyong	Musso	2.3 D	Geländewagen geschlossen	Allrad	Diesel	58	79	Mar 1993	Apr 1997	2024-03-01	24314
KIA	Bongo	2.4 Tdci	Pritsche/Fahrgestell	Heckantrieb	Diesel	69	94	Oct 2003	Dec 2012	2026-05-01	24327
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24343
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24344
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24345
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24346
Plymouth	Sundance	2.5 Duster	Coupe	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24347
Plymouth	Sundance	2.5 Turbo	Coupe	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24348
Plymouth	Sundance	3.0 Duster	Coupe	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24349
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24350
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24351
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24352
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24353
Plymouth	Sundance	2.5 Duster	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24354
Plymouth	Sundance	2.5 Turbo	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24355
Plymouth	Sundance	3.0 Duster	Stufenheck	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24356
Plymouth	Voyager / grand	3.3 LE	Großraumlimousine	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1990	2024-03-01	24357
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	63	85	Apr 2003	Nov 2009	2024-03-01	24367
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24375
BMW	I3	Electric	Schrägheck	Heckantrieb	Elektro	75	102	Aug 2013	-	2026-06-01	24378
Infiniti	Q50	50 D	Stufenheck	Heckantrieb	Diesel	125	170	Apr 2013	-	2024-03-01	24379
Fiat	Scudo	2.0 D Multijet 4X4	Bus	Allrad	Diesel	94	128	Apr 2011	Mar 2016	2024-03-01	24380
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24388
Toyota	Wish	1.8 HI	Großraumlimousine	Frontantrieb	Benzin	97	132	Apr 2003	Mar 2009	2024-03-01	24398
Aixam	500	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Dec 1997	Mar 2004	2024-03-01	24427
Aixam	A.721	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24428
Aixam	A.741	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24429
Aixam	A.751	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Jan 2005	Mar 2010	2024-03-01	24430
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jan 2006	Jul 2014	2024-03-01	24431
Opel	Vivaro a	2.0 Ecotec	Pritsche/Fahrgestell	Frontantrieb	Benzin	86	117	Aug 2006	Jul 2014	2024-03-01	24432
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Jul 2014	2024-03-01	24433
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Mar 2010	2024-03-01	24434
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	Jul 2014	2024-03-01	24435
Volvo	V70 iii	2	Kombi	Frontantrieb	Benzin	107	145	Oct 2007	Dec 2011	2024-03-01	24436
Volvo	V70 iii	3.2	Kombi	Frontantrieb	Benzin	175	238	Aug 2007	Dec 2010	2024-03-01	24437
Volvo	V70 iii	2.0 D	Kombi	Frontantrieb	Diesel	100	136	Oct 2007	Dec 2015	2024-03-01	24438
Volvo	V70 iii	D5 AWD	Kombi	Allrad	Diesel	136	185	Apr 2007	Dec 2009	2024-03-01	24439
BMW	1	120 I	Cabriolet	Heckantrieb	Benzin	125	170	Dec 2007	Oct 2013	2024-03-01	24440
BMW	1	125 I	Cabriolet	Heckantrieb	Benzin	160	218	Dec 2007	Oct 2013	2024-03-01	24441
Ford	Mondeo iv	2.3	Schrägheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24450
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24451
Ford	Mondeo iv	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24452
Ford	Mondeo iv	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24453
Ford	Mondeo iv turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24454
Ford	Mondeo iv	2.3	Stufenheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24455
Ford	Mondeo iv turnier	2.3	Kombi	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24456
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24457
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24458
Ford	S-Max	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24459
Ford	S-Max	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Jul 2007	Dec 2014	2024-03-01	24460
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Dec 2014	2024-03-01	24461
Ford	Galaxy ii	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Sep 2007	Jun 2015	2024-03-01	24462
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Jun 2015	2024-03-01	24463
Ford	Galaxy ii	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24464
VW	Caddy iii	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2005	Aug 2010	2024-03-01	24465
VW	Caddy iii	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24466
VW	Caddy iii	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24467
Chevrolet	Nubira	2.0 D	Kombi	Frontantrieb	Diesel	89	121	Jan 2007	Dec 2011	2024-03-01	24468
Chevrolet	Lacetti	2.0 D	Schrägheck	Frontantrieb	Diesel	89	121	Jan 2007	-	2024-03-01	24469
Chevrolet	Epica	2.0 D	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2007	Dec 2011	2024-03-01	24470
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	110	150	Sep 2007	-	2024-03-01	24471
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24472
Audi	Tt	2.0 TTS Quattro	Cabriolet	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24473
Jaguar	Xf i	3	Stufenheck	Heckantrieb	Benzin	175	238	Mar 2008	Apr 2015	2024-03-01	24474
Jaguar	Xf i	4.2	Stufenheck	Heckantrieb	Benzin	219	298	Mar 2008	Apr 2015	2024-03-01	24475
Jaguar	Xf i	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	306	416	Mar 2008	Apr 2015	2026-05-01	24476


--- 新建对话（分支降级） / Round 4 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6a2e20-71cc-83ea-a1e4-fe75df640a13
新对话：https://chatgpt.com/c/6a6ce913-8574-83ea-b704-975053e51275

--- 发送 / 新建对话重发 / Round 4 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352
EU-AUDI-TT-8J-RS-CONVERTIBLE-2D-01	4198	1842	1348
EU-AUDI-TT-8J-RS-COUPE-3D-01	4198	1842	1342
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445
EU-CHEVROLET-NUBIRA-J200-SEDAN-4D-01	4515	1725	1445
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460
EU-FIAT-SCUDO-II-CHASSIS-CAB-01	5053	1895	1942
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276
EU-FIAT-SCUDO-I-MPV-LWB-01	4840	1810	1930
EU-FIAT-SCUDO-I-MPV-SWB-01	4440	1810	1940
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	4810	1820	1445
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	4810	1820	1430
EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	4783	1824	1443
EU-JAGUAR-XF-I-SEDAN-X250-01	4961	1877	1460
EU-JAGUAR-XJSC-CONVERTIBLE-2D-01	4820	1793	1279
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	5899	1990	2456
EU-NISSAN-INTERSTAR-X70-MPV-MWB-MIDROOF-01	5399	1990	2486
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	4935	1864	1760
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	4140	1640	1410
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02	3916	1650	1459
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jaguar	Xj	5.0 Scv8	Stufenheck	Heckantrieb	Benzin	405	550	Jun 2013	Dec 2019	2025-02-03	24106
VW	Beetle	1.4 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Oct 2011	Jul 2016	2024-03-01	24176
VW	Beetle	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Oct 2011	Jul 2016	2024-03-01	24177
Think	City	Electric	Schrägheck	Frontantrieb	Elektro	30	41	Jan 2008	-	2024-03-01	24178
VW	Beetle	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Apr 2011	Jul 2016	2024-03-01	24179
Ferrari	348 spider	3.4	Cabriolet	Heckantrieb	Benzin	235	320	Mar 1993	Dec 1995	2024-03-01	24183
Subaru	Leone	1800 4WD	Schrägheck	Allrad	Benzin	66	90	Jan 1985	Dec 1989	2024-03-01	24185
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Sep 1988	Dec 1992	2024-03-01	24190
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	68	92	Jan 1993	Aug 1995	2024-03-01	24191
Nissan	Interstar	DCI 100	Bus	Frontantrieb	Diesel	74	101	Apr 2006	Mar 2011	2024-03-01	24194
Nissan	Interstar	DCI 100	Kasten	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	24195
Nissan	Interstar	DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	73	99	Feb 2004	-	2024-03-01	24196
Nissan	Interstar	DCI 115	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	115	Aug 2003	-	2024-03-01	24197
Nissan	Interstar	DCI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2006	-	2024-03-01	24198
Nissan	Interstar	DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Aug 2006	-	2024-03-01	24199
Nissan	Interstar	DCI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Nov 2003	-	2024-03-01	24200
Renault	Laguna ii	1.9 DCI	Schrägheck	Frontantrieb	Diesel	79	107	Mar 2001	Sep 2007	2024-03-01	24201
Renault	Laguna ii grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	79	107	Mar 2001	Dec 2007	2024-03-01	24202
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24240
Seat	Altea	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	Jul 2015	2024-05-01	24241
Seat	Altea	2.0 Tfsi 4X4	Großraumlimousine	Allrad	Benzin	147	200	Jun 2007	May 2009	2024-03-01	24242
Seat	Altea	2.0 TDI 4X4	Großraumlimousine	Allrad	Diesel	125	170	Jun 2007	Jun 2013	2024-03-01	24243
VW	Sharan	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Sep 1995	Feb 2000	2024-03-01	24248
VW	Polo	1.6	Stufenheck	Frontantrieb	Benzin	74	101	Sep 2002	-	2024-03-01	24253
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	90	122	Aug 2005	Jul 2006	2024-03-01	24257
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Aug 2005	May 2009	2024-03-01	24259
Buick	Century	3.8 T-type	Coupe	Frontantrieb	Benzin	94	128	Oct 1986	Sep 1989	2024-03-01	24267
Buick	Century	3.8 Custom	Coupe	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1988	2024-03-01	24268
Buick	Century	3.8 Special	Kombi	Heckantrieb	Benzin	78	106	Oct 1977	Dec 1981	2024-03-01	24269
Ferrari	F50	4.7	Targa	Heckantrieb	Benzin	383	521	May 1995	Oct 1997	2024-03-01	24276
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	120	163	Jul 2013	Mar 2017	2024-03-01	24303
Seat	Leon	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Jul 2005	Aug 2013	2024-03-01	24304
Ford	Mondeo v	2.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	176	240	May 2015	Mar 2022	2026-04-01	24305
Suzuki	Jimny	1.3	Geländewagen geschlossen	Heckantrieb	Benzin	63	86	Aug 2004	-	2024-03-01	24313
Ssangyong	Musso	2.3 D	Geländewagen geschlossen	Allrad	Diesel	58	79	Mar 1993	Apr 1997	2024-03-01	24314
KIA	Bongo	2.4 Tdci	Pritsche/Fahrgestell	Heckantrieb	Diesel	69	94	Oct 2003	Dec 2012	2026-05-01	24327
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24343
Plymouth	Sundance	2.2	Coupe	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24344
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24345
Plymouth	Sundance	2.2 Turbo	Coupe	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24346
Plymouth	Sundance	2.5 Duster	Coupe	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24347
Plymouth	Sundance	2.5 Turbo	Coupe	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24348
Plymouth	Sundance	3.0 Duster	Coupe	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24349
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	67	91	Oct 1989	Sep 1994	2024-03-01	24350
Plymouth	Sundance	2.2	Stufenheck	Frontantrieb	Benzin	72	98	Mar 1986	Sep 1989	2024-03-01	24351
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	109	148	Mar 1986	Sep 1989	2024-03-01	24352
Plymouth	Sundance	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	129	175	Oct 1989	Sep 1991	2024-03-01	24353
Plymouth	Sundance	2.5 Duster	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1989	Sep 1994	2024-03-01	24354
Plymouth	Sundance	2.5 Turbo	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1994	2024-03-01	24355
Plymouth	Sundance	3.0 Duster	Stufenheck	Frontantrieb	Benzin	104	141	Oct 1991	Sep 1994	2024-03-01	24356
Plymouth	Voyager / grand	3.3 LE	Großraumlimousine	Frontantrieb	Benzin	112	152	Oct 1989	Sep 1990	2024-03-01	24357
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	63	85	Apr 2003	Nov 2009	2024-03-01	24367
VW	Transporter t5	2.0 TDI	Kasten	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24375
BMW	I3	Electric	Schrägheck	Heckantrieb	Elektro	75	102	Aug 2013	-	2026-06-01	24378
Infiniti	Q50	50 D	Stufenheck	Heckantrieb	Diesel	125	170	Apr 2013	-	2024-03-01	24379
Fiat	Scudo	2.0 D Multijet 4X4	Bus	Allrad	Diesel	94	128	Apr 2011	Mar 2016	2024-03-01	24380
VW	Transporter t5	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	24388
Toyota	Wish	1.8 HI	Großraumlimousine	Frontantrieb	Benzin	97	132	Apr 2003	Mar 2009	2024-03-01	24398
Aixam	500	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Dec 1997	Mar 2004	2024-03-01	24427
Aixam	A.721	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24428
Aixam	A.741	0.4 D	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2005	-	2024-03-01	24429
Aixam	A.751	0.5 D	Schrägheck	Frontantrieb	Diesel	10	14	Jan 2005	Mar 2010	2024-03-01	24430
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jan 2006	Jul 2014	2024-03-01	24431
Opel	Vivaro a	2.0 Ecotec	Pritsche/Fahrgestell	Frontantrieb	Benzin	86	117	Aug 2006	Jul 2014	2024-03-01	24432
Opel	Vivaro a	2.0 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Jul 2014	2024-03-01	24433
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	Mar 2010	2024-03-01	24434
Opel	Vivaro a	2.5 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	Jul 2014	2024-03-01	24435
Volvo	V70 iii	2	Kombi	Frontantrieb	Benzin	107	145	Oct 2007	Dec 2011	2024-03-01	24436
Volvo	V70 iii	3.2	Kombi	Frontantrieb	Benzin	175	238	Aug 2007	Dec 2010	2024-03-01	24437
Volvo	V70 iii	2.0 D	Kombi	Frontantrieb	Diesel	100	136	Oct 2007	Dec 2015	2024-03-01	24438
Volvo	V70 iii	D5 AWD	Kombi	Allrad	Diesel	136	185	Apr 2007	Dec 2009	2024-03-01	24439
BMW	1	120 I	Cabriolet	Heckantrieb	Benzin	125	170	Dec 2007	Oct 2013	2024-03-01	24440
BMW	1	125 I	Cabriolet	Heckantrieb	Benzin	160	218	Dec 2007	Oct 2013	2024-03-01	24441
Ford	Mondeo iv	2.3	Schrägheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24450
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24451
Ford	Mondeo iv	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24452
Ford	Mondeo iv	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24453
Ford	Mondeo iv turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	129	175	Mar 2008	Oct 2010	2024-03-01	24454
Ford	Mondeo iv	2.3	Stufenheck	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24455
Ford	Mondeo iv turnier	2.3	Kombi	Frontantrieb	Benzin	118	160	Jul 2007	Jan 2015	2024-03-01	24456
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24457
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	85	115	Nov 2007	Jan 2015	2024-03-01	24458
Ford	S-Max	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24459
Ford	S-Max	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Jul 2007	Dec 2014	2024-03-01	24460
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Dec 2014	2024-03-01	24461
Ford	Galaxy ii	2.3	Großraumlimousine	Frontantrieb	Benzin	118	160	Sep 2007	Jun 2015	2024-03-01	24462
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Nov 2007	Jun 2015	2024-03-01	24463
Ford	Galaxy ii	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	129	175	Mar 2008	Dec 2012	2024-03-01	24464
VW	Caddy iii	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2005	Aug 2010	2024-03-01	24465
VW	Caddy iii	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24466
VW	Caddy iii	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2007	Aug 2010	2024-03-01	24467
Chevrolet	Nubira	2.0 D	Kombi	Frontantrieb	Diesel	89	121	Jan 2007	Dec 2011	2024-03-01	24468
Chevrolet	Lacetti	2.0 D	Schrägheck	Frontantrieb	Diesel	89	121	Jan 2007	-	2024-03-01	24469
Chevrolet	Epica	2.0 D	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2007	Dec 2011	2024-03-01	24470
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	110	150	Sep 2007	-	2024-03-01	24471
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24472
Audi	Tt	2.0 TTS Quattro	Cabriolet	Allrad	Benzin	200	272	May 2008	Jun 2014	2024-03-01	24473
Jaguar	Xf i	3	Stufenheck	Heckantrieb	Benzin	175	238	Mar 2008	Apr 2015	2024-03-01	24474
Jaguar	Xf i	4.2	Stufenheck	Heckantrieb	Benzin	219	298	Mar 2008	Apr 2015	2024-03-01	24475
Jaguar	Xf i	4.2 Supercharged	Stufenheck	Heckantrieb	Benzin	306	416	Mar 2008	Apr 2015	2026-05-01	24476


--- 新建对话（分支降级） / Round 4 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6ce913-8574-83ea-b704-975053e51275
新对话：https://chatgpt.com/c/6a6cee41-1cc0-83ea-81d9-2faec5e04929

--- Round 4 / checkpoint 续跑 ---
## 更新点

* 本轮优先复用跨批次已有尺寸组，闭合 Renault 19、Laguna II、Altea、Passat B6、Insignia A、Leon II、Transporter T5、Q50、V70 III、Mondeo IV、S-Max、Galaxy II、Chevrolet J200/V250/C100、Jaguar XF 等映射。
* 首次创建 6 个尺寸组：VW Beetle A5、Ferrari 348 Spider、Ferrari F50、Ford Mondeo V Sedan、BMW i3 I01 前期、Toyota Wish I 2WD。
* Beetle 三维来自 Volkswagen 官方资料；BMW i3 官方规格同时确认 `75 kW / 102 hp` 是持续输出，并对应 `3999 × 1775 × 1578 mm`；Toyota 官方历史规格确认前驱 1.8 Wish 为 `4550 × 1695 × 1590 mm`。([volkswagen-newsroom.com][1])
* Ferrari 348 Spider、F50 的资料明确标注不含后视镜宽度；Mondeo V 2.0 EcoBoost 240 四门轿车三维为 `4871 × 1852 × 1482 mm`。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：51
* 尚未闭合 Ktype：49
* READY 映射：74
* 当前引用尺寸组：45
* 复用既有尺寸组：39
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24176	24176	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24177	24177	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24179	24179	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24183	24183	Convertible	348 Spider	F119	2	EU-FERRARI-348-SPIDER-CONVERTIBLE-2D-01	HIGH	F119 Spider 双门敞篷。	READY
24190	24190	Sedan	Renault 19 I Chamade	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH	L53 四门 Chamade。	READY
24191	24191	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH	第二阶段 Chamade 四门。	READY
24201_prefl	24201	Hatchback	Laguna II Phase I	B74	5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24201_facelift	24201	Hatchback	Laguna II Facelift	B74	5	EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24202_prefl	24202	Wagon	Laguna II Grandtour Phase I	K74	5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24202_facelift	24202	Wagon	Laguna II Grandtour Facelift	K74	5	EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24240_prefl	24240	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24240_facelift	24240	MPV	Altea I Facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24241_prefl	24241	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24241_facelift	24241	MPV	Altea I Facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24242	24242	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	Freetrack 四驱外廓。	READY
24243	24243	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	Freetrack 四驱外廓。	READY
24257	24257	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2 四门轿车。	READY
24259	24259	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2 四门轿车。	READY
24276	24276	Targa	F50	F130	2	EU-FERRARI-F50-TARGA-2D-01	HIGH	可拆卸硬顶双门外廓。	READY
24303	24303	Hatchback	Insignia A Facelift		5	EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	HIGH	五门掀背改款外廓。	READY
24304_prefl	24304	Hatchback	Leon II Pre-Facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24304_facelift	24304	Hatchback	Leon II Facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24305	24305	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-SEDAN-4D-01	MEDIUM	CD391 四门轿车；输入终止月晚于该动力资料覆盖。	READY
24367	24367	MPV	Multivan T5		5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	短轴乘用车外廓。	READY
24375_swb_lowroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式车。	READY
24375_swb_medroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	短轴中顶厢式车。	READY
24375_lwb_lowroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶厢式车。	READY
24375_lwb_medroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	长轴中顶厢式车。	READY
24375_lwb_highroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车。	READY
24378	24378	Hatchback	i3 I01 Pre-Facelift	I01	5	EU-BMW-I3-I01-HATCHBACK-5D-PREFL-01	HIGH	75 kW 为官方持续功率，匹配前期 I01。	READY
24379_prefl	24379	Sedan	Q50 I V37 Pre-Facelift	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	MEDIUM	后驱柴油版前期外廓。	READY
24379_facelift	24379	Sedan	Q50 I V37 Facelift	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	MEDIUM	生产终期未知，保留改款后后驱分支。	READY
24398	24398	MPV	Wish I	ZNE10G	5	EU-TOYOTA-WISH-I-MPV-5D-2WD-01	HIGH	1.8 前驱 ZNE10G 外廓。	READY
24436	24436	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期五门旅行车。	READY
24437	24437	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期五门旅行车。	READY
24438_prefl	24438	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24438_facelift	24438	Wagon	V70 III Facelift	135	5	EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24439	24439	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期 AWD 五门旅行车。	READY
24440	24440	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88 双门敞篷。	READY
24441	24441	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88 双门敞篷。	READY
24450_prefl	24450	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24450_facelift	24450	Hatchback	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24451_prefl	24451	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24451_facelift	24451	Hatchback	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24452	24452	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	生产期止于改款前。	READY
24453	24453	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产期止于改款前。	READY
24454	24454	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	生产期止于改款前。	READY
24455_prefl	24455	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24455_facelift	24455	Sedan	Mondeo IV Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24456_prefl	24456	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24456_facelift	24456	Wagon	Mondeo IV Turnier Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24457_prefl	24457	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24457_facelift	24457	Sedan	Mondeo IV Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24458_prefl	24458	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24458_facelift	24458	Wagon	Mondeo IV Turnier Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24459_prefl	24459	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24459_facelift	24459	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24460_prefl	24460	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24460_facelift	24460	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24461_prefl	24461	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24461_facelift	24461	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24462_prefl	24462	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24462_facelift	24462	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24463_prefl	24463	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24463_facelift	24463	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24464_prefl	24464	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24464_facelift	24464	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24468	24468	Wagon	Nubira J200	J200	5	EU-CHEVROLET-NUBIRA-J200-WAGON-01	HIGH	J200 五门旅行车。	READY
24469	24469	Hatchback	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200 五门掀背。	READY
24470	24470	Sedan	Epica V250	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250 柴油四门轿车。	READY
24471	24471	SUV	Captiva I C100	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100 五门 SUV。	READY
24474	24474	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
24475	24475	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
24476	24476	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-BEETLE-A5-HATCHBACK-3D-01	4278	1808	1486	Volkswagen Newsroom — The Beetle International Driving Presentation	https://www.volkswagen-newsroom.com/en/the-beetle-international-driving-presentation-3009
EU-FERRARI-348-SPIDER-CONVERTIBLE-2D-01	4230	1894	1170	Automobile-Catalog — 1993 Ferrari 348 Spider Europe specifications	https://www.automobile-catalog.com/car/1993/706865/ferrari_348_spider.html
EU-FERRARI-F50-TARGA-2D-01	4480	1986	1120	Automobile-Catalog — 1995 Ferrari F50 Europe specifications	https://www.automobile-catalog.com/car/1995/706985/ferrari_f50.html
EU-FORD-MONDEO-V-SEDAN-4D-01	4871	1852	1482	Auto-Data — Ford Mondeo Sedan 2.0 EcoBoost 240 Hp Automatic	https://www.auto-data.net/en/ford-mondeo-iv-sedan-2.0-ecoboost-240hp-automatic-20472
EU-BMW-I3-I01-HATCHBACK-5D-PREFL-01	3999	1775	1578	BMW Group PressClub — Technical Specifications BMW i3 valid from 03/2014	https://www.press.bmwgroup.com/global/article/attachment/T0243308EN/339148
EU-TOYOTA-WISH-I-MPV-5D-2WD-01	4550	1695	1590	Toyota Motor Corporation — 75 Years of Toyota, First-generation Wish 1.8 2WD	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60007858/index.html
```

## 下一步优先处理

1. 闭合 Nissan Interstar、Opel Vivaro、VW Transporter 底盘及 Kia Bongo 的单排/双排、轴距和车顶分支。
2. 核对 Jaguar XJ X351/XJR 的标准轴距与长轴边界，以及 Audi TTS Coupe/Roadster 是否需要独立于普通 TT 建组。
3. 集中处理 Plymouth Sundance、Voyager/Grand Voyager、Buick Century、Subaru Leone、Aixam 等旧车或资料稀缺车型。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/the-beetle-international-driving-presentation-3009 "The Beetle - International Driving Presentation | Volkswagen Newsroom"
[2]: https://www.automobile-catalog.com/car/1993/706865/ferrari_348_spider.html?utm_source=chatgpt.com "1993 Ferrari 348 Spider Specs Review (235 kW / 320 PS / 315 hp) (since mid-year 1993 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
## 更新点

* 新闭合 9 个 Ktype，新增 11 条映射；Suzuki Jimny 与 VW Caddy III 直接复用跨批次尺寸组，未重复输出既有尺寸事实。
* 首次创建 Think City、VW Sharan I 前期、VW Polo IV Sedan 三个尺寸组。Think City 型式资料记录三门车身及 `3143 × 1658 × 1596 mm`；Volkswagen 官方历史资料记录 Sharan 7M8 为 `4620 × 1810 × 1730 mm`；Polo 9N2 Sedan 规格为 `4179 × 1650 × 1484 mm`。([Motoro][1])
* Audi TTS Coupe 与 Roadster 的车高不同，分别创建独立尺寸组，不复用普通 TT 8J 组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：60
* 尚待闭合输入 Ktype：40
* READY 映射：85
* 已确认并引用尺寸组：50
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24178	24178	Hatchback	Think City	A306	3	EU-THINK-CITY-A306-HATCHBACK-3D-01	MEDIUM	三门城市电动车外廓；输入功率与型式批准峰值口径不同。	READY
24248	24248	MPV	Sharan I Pre-Facelift	7M8	5	EU-VW-SHARAN-I-7M8-PREFL-MPV-01	HIGH	7M8 前期五门 MPV。	READY
24253	24253	Sedan	Polo IV Sedan	9N2	4	EU-VW-POLO-IV-9N2-SEDAN-4D-01	MEDIUM	9N2 四门轿车；输入起始月早于欧洲公开车型资料。	READY
24313	24313	SUV	Jimny III Facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	MEDIUM	三门封闭式 SUV。	READY
24465_van	24465	Van	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖货运封闭车身分支。	READY
24465_mpv	24465	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖乘用车身分支。	READY
24466	24466	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
24467_van	24467	Van	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖货运封闭车身分支。	READY
24467_mpv	24467	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖乘用车身分支。	READY
24472	24472	Coupe	TT 8J TTS	8J3	3	EU-AUDI-TT-8J-TTS-COUPE-3D-01	HIGH	TTS 三门 Coupe 外廓。	READY
24473	24473	Convertible	TT 8J TTS	8J9	2	EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	HIGH	TTS 双门 Roadster 外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-THINK-CITY-A306-HATCHBACK-3D-01	3143	1658	1596	Motoro — THINK CITY Swiss type-approval specifications	https://motoro.ch/en/fiche-technique/think/city
EU-VW-SHARAN-I-7M8-PREFL-MPV-01	4620	1810	1730	Volkswagen — Sharan 1 previous-model specifications	https://www.volkswagen.de/de/besitzer-und-service/ueber-ihr-auto/vorgaengermodelle/mpv/sharan-1.html
EU-VW-POLO-IV-9N2-SEDAN-4D-01	4179	1650	1484	Auto-Data — Volkswagen Polo IV (9N) Sedan 1.6	https://www.auto-data.net/en/volkswagen-polo-iv-9n-sedan-1.6-101hp-56858
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345	Audi AG — Audi TTS brochure (2009)	https://xr793.com/wp-content/uploads/2023/04/2009-Audi-TTS-AUS.pdf
EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	4198	1842	1350	Audi AG — Audi TTS brochure (2009)	https://xr793.com/wp-content/uploads/2023/04/2009-Audi-TTS-AUS.pdf
```

## 下一步优先处理

1. 闭合 Nissan Interstar 的 Bus、Van 和底盘车型，按轴距、车顶及驾驶室分支复用现有组或仅补缺失组。
2. 处理 Opel Vivaro、VW Transporter、KIA Bongo 的 `Pritsche/Fahrgestell`，确认裸底盘、单排/双排及成品货台边界。
3. 集中核对 Plymouth Sundance、Voyager、Buick Century、Subaru Leone及 Aixam 等尚无可靠缓存的旧车尺寸组。

推进信号：CONTINUE

[1]: https://motoro.ch/en/fiche-technique/think/city?utm_source=chatgpt.com "THINK CITY 46.2 HP — Specifications"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 续跑 ---
## 更新点

* 闭合 Jaguar XJ X351 XJR、Nissan Interstar Bus/Van、VW Transporter T5 底盘及 Opel Vivaro A Dropside，共新增 9 个 READY Ktype、12 条映射。
* Interstar 和 Transporter 仅关联跨批次既有尺寸组，未重复输出尺寸事实。
* 首次创建 XJ X351 XJR 标准轴距组与 Vivaro A 单排长轴 Dropside 组。Jaguar 2014 官方规格表确认 405 kW／550 PS XJR 仅提供标准轴距，三维为 `5127 × 1899 × 1456 mm`；Vauxhall 官方 Dropside 资料确认三维为 `5350 × 1980 × 2000 mm`，其中宽度明确不含后视镜。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：69
* 尚待闭合输入 Ktype：31
* READY 映射：97
* 当前已引用尺寸组：58
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24106	24106	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-XJR-SEDAN-SWB-01	HIGH	XJR 550PS仅对应标准轴距外廓。	READY
24194	24194	MPV	Interstar I X70	X70		EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	HIGH	中轴中顶Bus外廓。	READY
24195_mwb_midroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	MEDIUM	中轴中顶厢式车分支。	READY
24195_lwb_midroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	MEDIUM	长轴中顶厢式车分支。	READY
24195_lwb_highroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车分支。	READY
24388_singlecab_lwb	24388	Pickup	Transporter T5 Facelift		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	MEDIUM	长轴单排底盘驾驶室分支。	READY
24388_doublecab_lwb	24388	Pickup	Transporter T5 Facelift		4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排底盘驾驶室分支。	READY
24431	24431	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24432	24432	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	MEDIUM	汽油动力不改变单排长轴Dropside外廓。	READY
24433	24433	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24434	24434	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24435	24435	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-X351-XJR-SEDAN-SWB-01	5127	1899	1456	Jaguar XJ 2014 official Specification and Price Guide	https://xr793.com/wp-content/uploads/2022/10/2014-Jaguar-XJ-Specs-Price-Guide-UK.pdf
EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	5350	1980	2000	Vauxhall Vivaro Dropside 2011 Models Edition 2 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Dropside_Conv_April_2011.pdf
```

## 下一步优先处理

1. 集中闭合 Nissan Interstar 的五个底盘 Ktype，确认中轴、长轴及单排/双排物理分支。
2. 核对 Fiat Scudo 4×4 的 Dangel 加高是否改变车高，禁止直接复用普通 MPV 组。
3. 批量处理 Plymouth Sundance、Voyager、Buick Century、Subaru Leone、SsangYong Musso 与 Aixam 剩余旧车组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 续跑 ---
## 更新点

* 闭合 Subaru Leone III 三门掀背、SsangYong Musso I 五门 SUV，以及 Aixam A.721、A.741、A.751，共新增 5 个 READY 映射。
* Aixam 官方手册确认 A.721 为 `2674 × 1474 × 1460 mm`，A.741 为 `2897 × 1474 × 1460 mm`；A.751 的 0.5 D 版本与 A.741 共用长车身外廓，因此复用同一尺寸组。([Aixam Mega Sav][1])
* Leone III 1.8 4WD 三门车身为 `4370 × 1660 × 1385 mm`；Musso I SUV 为 `4640 × 1905 × 1735 mm`，宽度资料明确为不含后视镜口径。([斯巴鲁驾驶地][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：74
* PENDING 输入 Ktype：26
* READY 映射：102
* 当前已引用尺寸组：62
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24185	24185	Hatchback	Leone III		3	EU-SUBARU-LEONE-III-HATCHBACK-3D-01	MEDIUM	第三代三门掀背式车身。	READY
24314	24314	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-SUV-5D-01	HIGH	FJ系列五门封闭式SUV。	READY
24428	24428	Hatchback	Aixam A7xx	K34VBA	2	EU-AIXAM-A7XX-HATCHBACK-SWB-01	HIGH	A.721短轴双门车身。	READY
24429	24429	Hatchback	Aixam A7xx	K44VBA	2	EU-AIXAM-A7XX-HATCHBACK-LWB-01	HIGH	A.741长轴双门车身。	READY
24430	24430	Hatchback	Aixam A7xx		2	EU-AIXAM-A7XX-HATCHBACK-LWB-01	MEDIUM	A.751与A.741共用长轴车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-LEONE-III-HATCHBACK-3D-01	4370	1660	1385	Drive.Place — Subaru Leone III 1.8 90 hp Coupe specifications	https://subaru.drive.place/leone/iii/group_coupe/557630
EU-SSANGYONG-MUSSO-I-SUV-5D-01	4640	1905	1735	Auto-Data — SsangYong Musso I model specifications; Automobile-Catalog — SsangYong Musso FJ-series dimensions	https://www.auto-data.net/en/ssangyong-musso-model-1816;https://www.automobile-catalog.com/car/1996/3159500/ssangyong_musso_e32.html
EU-AIXAM-A7XX-HATCHBACK-SWB-01	2674	1474	1460	Aixam-Mega official A721-A741 user manual	https://www.aixam-mega-sav.com/data/gamme/doc/user%20manual%20a721-a741.pdf
EU-AIXAM-A7XX-HATCHBACK-LWB-01	2897	1474	1460	Aixam-Mega official A721-A741 user manual; AutoCentrum — Aixam A.751 specifications	https://www.aixam-mega-sav.com/data/gamme/doc/user%20manual%20a721-a741.pdf;https://www.autocentrum.pl/dane-techniczne/aixam/a-751/
```

## 下一步优先处理

1. 闭合 Nissan Interstar 五个底盘 Ktype，重点区分中轴/长轴以及单排/双排驾驶室。
2. 处理 Fiat Scudo 4×4 和 Kia Bongo，确认改装加高与驾驶室、货台分支。
3. 集中闭合 Plymouth Sundance、Voyager、Buick Century及 Aixam 500，解决剩余历史资料冲突。

推进信号：CONTINUE

[1]: https://www.aixam-mega-sav.com/data/gamme/doc/user%20manual%20a721-a741.pdf "User manual A721-A741"
[2]: https://subaru.drive.place/leone/iii/group_coupe/557630?utm_source=chatgpt.com "Subaru Leone III 1.8 MT 90 hp Coupe — specifications"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 20 个 Ktype，主要完成 Buick Century、Plymouth Sundance、Grand Voyager、Fiat Scudo 4×4 与 Aixam 500。
* Buick Century Ktype `24269` 按 1978、1979、1980–1981 三套外廓拆分：`4978×1781×1415`、`4978×1834×1415`、`4996×1808×1415 mm`，各来源宽度均为不含后视镜口径。([汽车目录][1])
* Plymouth Sundance 的输入 `Coupe/Stufenheck` 统一落为三门/五门 Hatchback，并按 1987–1989、1990–1991、1992–1994 三个已确认尺寸阶段建组。([汽车目录][2])
* 3.3 LE 对应长轴 Grand Voyager；Scudo Dangel 4×4 五座短轴分支为 `4805×1895×1880 mm`；Aixam 500-4 为三门 Hatchback，尺寸 `2885×1440×1365 mm`。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：94
* PENDING 输入 Ktype：6
* READY 映射：126
* 当前已引用尺寸组：75
* 本轮首次创建尺寸组：13
* 剩余未闭合 Ktype：`24196`、`24197`、`24198`、`24199`、`24200`、`24327`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24267	24267	Coupe	Century IV	A	2	EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	MEDIUM	T-Type年款标签与公开资料不完全一致，按A-body双门外廓。	READY
24268	24268	Coupe	Century IV	A	2	EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	HIGH	A-body双门Custom外廓。	READY
24269_my1978	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1978-01	HIGH	1978年款五门旅行车外廓。	READY
24269_my1979	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1979-01	HIGH	1979年款五门旅行车外廓。	READY
24269_my1980_81	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1980-1981-01	HIGH	1980至1981年款五门旅行车外廓。	READY
24343_my1990_91	24343	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	MEDIUM	输入Coupe对应三门掀背；拆分1990至1991年款外廓。	READY
24343_my1992_94	24343	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	MEDIUM	输入Coupe对应三门掀背；拆分1992至1994年款外廓。	READY
24344	24344	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	HIGH	输入Coupe对应前期三门掀背外廓。	READY
24345	24345	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	HIGH	前期Turbo三门掀背外廓。	READY
24346	24346	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	HIGH	1990至1991年款Turbo三门掀背外廓。	READY
24347	24347	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	MEDIUM	Duster三门外廓；输入起始月早于Duster公开年款。	READY
24348	24348	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	MEDIUM	2.5 Turbo三门外廓；输入终止月晚于该动力公开覆盖。	READY
24349	24349	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	HIGH	Duster 3.0三门掀背外廓。	READY
24350_my1990_91	24350	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	MEDIUM	输入Stufenheck对应五门掀背；拆分1990至1991年款外廓。	READY
24350_my1992_94	24350	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	MEDIUM	输入Stufenheck对应五门掀背；拆分1992至1994年款外廓。	READY
24351	24351	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	HIGH	输入Stufenheck对应前期五门掀背外廓。	READY
24352	24352	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	HIGH	前期Turbo五门掀背外廓。	READY
24353	24353	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	HIGH	1990至1991年款Turbo五门掀背外廓。	READY
24354	24354	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	MEDIUM	Duster五门外廓；输入起始月早于Duster公开年款。	READY
24355	24355	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	MEDIUM	2.5 Turbo五门外廓；输入终止月晚于该动力公开覆盖。	READY
24356	24356	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	HIGH	Duster 3.0五门掀背外廓。	READY
24357	24357	MPV	Grand Voyager I	S	4	EU-PLYMOUTH-GRAND-VOYAGER-I-S-MPV-LWB-01	HIGH	3.3 LE对应长轴Grand Voyager外廓。	READY
24380	24380	MPV	Scudo II	270		EU-FIAT-SCUDO-II-DANGEL-MPV-SWB-4X4-01	MEDIUM	Dangel短轴五座四驱外廓。	READY
24427	24427	Hatchback	500-4 / Evolution		3	EU-AIXAM-500-4-HATCHBACK-3D-01	MEDIUM	500-4三门微型车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	4803	1763	1364	Automobile-Catalog — 1986 Buick Century Custom Coupe 3.8L V6	https://www.automobile-catalog.com/car/1986/315200/buick_century_custom_coupe_3_8l_v-6.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1978-01	4978	1781	1415	Automobile-Catalog — 1978 Buick Century Custom Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1978/178970/buick_century_custom_station_wagon_3_8l_v-6_automatic.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1979-01	4978	1834	1415	Automobile-Catalog — 1979 Buick Century Special Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1979/180305/buick_century_special_station_wagon_3_8l_v-6_automatic.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1980-1981-01	4996	1808	1415	Automobile-Catalog — 1981 Buick Century Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1981/181940/buick_century_station_wagon_3_8l_v-6_automatic.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	4361	1709	1336	Plymouth 1990 official Sundance brochure	https://xr793.com/wp-content/uploads/2025/04/1990-Plymouth-Sundance.pdf
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	4361	1709	1346	Automobile-Catalog — 1992 Plymouth Sundance Duster 3.0-liter V6	https://www.automobile-catalog.com/car/1992/2728760/plymouth_sundance_duster_3_0-liter_v6.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	4361	1709	1339	Automobile-Catalog — 1987 Plymouth Sundance 2.2-liter	https://www.automobile-catalog.com/car/1987/2727935/plymouth_sundance_2_2-liter.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	4361	1709	1336	Plymouth 1990 official Sundance brochure	https://xr793.com/wp-content/uploads/2025/04/1990-Plymouth-Sundance.pdf
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	4361	1709	1346	Automobile-Catalog — 1992 Plymouth Sundance Duster 3.0-liter V6	https://www.automobile-catalog.com/car/1992/2728760/plymouth_sundance_duster_3_0-liter_v6.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	4361	1709	1339	Automobile-Catalog — 1987 Plymouth Sundance 2.2-liter	https://www.automobile-catalog.com/car/1987/2727935/plymouth_sundance_2_2-liter.html
EU-PLYMOUTH-GRAND-VOYAGER-I-S-MPV-LWB-01	4839	1834	1643	Plymouth 1990 official Voyager brochure	https://xr793.com/wp-content/uploads/2020/01/1990-Plymouth-Voyager.pdf
EU-FIAT-SCUDO-II-DANGEL-MPV-SWB-4X4-01	4805	1895	1880	Motoro — FIAT-DANGEL Scudo 2.0 MJ Swiss type approval	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj
EU-AIXAM-500-4-HATCHBACK-3D-01	2885	1440	1365	Auta5P — Aixam 500-4 2003 specifications	https://auta5p.eu/lang/en/katalog/auto.php?idf=Aixam-500-4-263
```

## 下一步优先处理

1. 一次性闭合 Nissan Interstar 五个底盘 Ktype，确认单排/双排驾驶室、中轴/长轴以及成品底盘长度边界。
2. 闭合 KIA Bongo `24327`，按标准驾驶室、加长驾驶室或双排驾驶室确认实际覆盖分支。
3. 上述 6 个 Ktype 闭合后立即进行一次机械检查，并在下一条回复直接输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/178970/buick_century_custom_station_wagon_3_8l_v-6_automatic.html?utm_source=chatgpt.com "1978 Buick Century Custom Station Wagon 3.8L V-6 automatic Specs Review (78 kW / 106 PS / 105 hp) (since October 1977 for North America U.S.)"
[2]: https://www.automobile-catalog.com/car/1987/2727935/plymouth_sundance_2_2-liter.html?utm_source=chatgpt.com "1987 Plymouth Sundance 2.2-liter (man. 5)"
[3]: https://www.automobile-catalog.com/car/1990/2731850/plymouth_grand_voyager_3_3-liter_v6_ultradrive_automatic.html?utm_source=chatgpt.com "1990 Plymouth Grand Voyager 3.3-liter V6 Ultradrive automatic Specs Review (112 kW / 152 PS / 150 hp) (since mid-year 1989 for North America U.S.)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
## 更新点

* 剩余 5 个 Nissan Interstar 底盘 Ktype 已拆分为中轴单排、长轴单排和长轴双排分支。该映射结合 Nissan Interstar 官方规格与同平台 Movano 官方底盘规格完成。
* KIA Bongo III 已拆分为 Standard Cab、King Cab 和 Double Cab 三种物理外廓，并完成尺寸组建档。([Kia Australia][1])
* 已完成唯一性、引用闭合、尺寸与来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：144
* PENDING 映射：0
* DIMENSION_GROUP：83
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24106	24106	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-XJR-SEDAN-SWB-01	HIGH	XJR 550PS仅对应标准轴距外廓。	READY
24176	24176	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24177	24177	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24178	24178	Hatchback	Think City	A306	3	EU-THINK-CITY-A306-HATCHBACK-3D-01	MEDIUM	三门城市电动车外廓；输入功率与型式批准峰值口径不同。	READY
24179	24179	Hatchback	Beetle A5	5C1	3	EU-VW-BEETLE-A5-HATCHBACK-3D-01	HIGH	5C1 三门掀背外廓。	READY
24183	24183	Convertible	348 Spider	F119	2	EU-FERRARI-348-SPIDER-CONVERTIBLE-2D-01	HIGH	F119 Spider 双门敞篷。	READY
24185	24185	Hatchback	Leone III		3	EU-SUBARU-LEONE-III-HATCHBACK-3D-01	MEDIUM	第三代三门掀背式车身。	READY
24190	24190	Sedan	Renault 19 I Chamade	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH	L53 四门 Chamade。	READY
24191	24191	Sedan	Renault 19 II Chamade	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH	第二阶段 Chamade 四门。	READY
24194	24194	MPV	Interstar I X70	X70		EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	HIGH	中轴中顶Bus外廓。	READY
24195_mwb_midroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	MEDIUM	中轴中顶厢式车分支。	READY
24195_lwb_midroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	MEDIUM	长轴中顶厢式车分支。	READY
24195_lwb_highroof	24195	Van	Interstar I X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车分支。	READY
24196_mwb_singlecab	24196	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	MEDIUM	Ktype未细分轴距，展开中轴单排底盘驾驶室。	READY
24196_lwb_singlecab	24196	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	MEDIUM	Ktype未细分轴距，展开长轴单排底盘驾驶室。	READY
24196_lwb_crewcab	24196	Pickup	Interstar I X70	X70	4	EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	MEDIUM	Ktype未细分驾驶室，展开长轴双排底盘驾驶室。	READY
24197_mwb_singlecab	24197	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	MEDIUM	Ktype未细分轴距，展开中轴单排底盘驾驶室。	READY
24197_lwb_singlecab	24197	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	MEDIUM	Ktype未细分轴距，展开长轴单排底盘驾驶室。	READY
24197_lwb_crewcab	24197	Pickup	Interstar I X70	X70	4	EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	MEDIUM	Ktype未细分驾驶室，展开长轴双排底盘驾驶室。	READY
24198_mwb_singlecab	24198	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	MEDIUM	Ktype未细分轴距，展开中轴单排底盘驾驶室。	READY
24198_lwb_singlecab	24198	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	MEDIUM	Ktype未细分轴距，展开长轴单排底盘驾驶室。	READY
24198_lwb_crewcab	24198	Pickup	Interstar I X70	X70	4	EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	MEDIUM	Ktype未细分驾驶室，展开长轴双排底盘驾驶室。	READY
24199_mwb_singlecab	24199	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	MEDIUM	Ktype未细分轴距，展开中轴单排底盘驾驶室。	READY
24199_lwb_singlecab	24199	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	MEDIUM	Ktype未细分轴距，展开长轴单排底盘驾驶室。	READY
24199_lwb_crewcab	24199	Pickup	Interstar I X70	X70	4	EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	MEDIUM	Ktype未细分驾驶室，展开长轴双排底盘驾驶室。	READY
24200_mwb_singlecab	24200	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	MEDIUM	Ktype未细分轴距，展开中轴单排底盘驾驶室。	READY
24200_lwb_singlecab	24200	Pickup	Interstar I X70	X70	2	EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	MEDIUM	Ktype未细分轴距，展开长轴单排底盘驾驶室。	READY
24200_lwb_crewcab	24200	Pickup	Interstar I X70	X70	4	EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	MEDIUM	Ktype未细分驾驶室，展开长轴双排底盘驾驶室。	READY
24201_prefl	24201	Hatchback	Laguna II Phase I	B74	5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24201_facelift	24201	Hatchback	Laguna II Facelift	B74	5	EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24202_prefl	24202	Wagon	Laguna II Grandtour Phase I	K74	5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24202_facelift	24202	Wagon	Laguna II Grandtour Facelift	K74	5	EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24240_prefl	24240	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24240_facelift	24240	MPV	Altea I Facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24241_prefl	24241	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24241_facelift	24241	MPV	Altea I Facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24242	24242	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	Freetrack 四驱外廓。	READY
24243	24243	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	Freetrack 四驱外廓。	READY
24248	24248	MPV	Sharan I Pre-Facelift	7M8	5	EU-VW-SHARAN-I-7M8-PREFL-MPV-01	HIGH	7M8 前期五门 MPV。	READY
24253	24253	Sedan	Polo IV Sedan	9N2	4	EU-VW-POLO-IV-9N2-SEDAN-4D-01	MEDIUM	9N2 四门轿车；输入起始月早于欧洲公开车型资料。	READY
24257	24257	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2 四门轿车。	READY
24259	24259	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2 四门轿车。	READY
24267	24267	Coupe	Century IV	A	2	EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	MEDIUM	T-Type年款标签与公开资料不完全一致，按A-body双门外廓。	READY
24268	24268	Coupe	Century IV	A	2	EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	HIGH	A-body双门Custom外廓。	READY
24269_my1978	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1978-01	HIGH	1978年款五门旅行车外廓。	READY
24269_my1979	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1979-01	HIGH	1979年款五门旅行车外廓。	READY
24269_my1980_81	24269	Wagon	Century 1978-1981	A	5	EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1980-1981-01	HIGH	1980至1981年款五门旅行车外廓。	READY
24276	24276	Targa	F50	F130	2	EU-FERRARI-F50-TARGA-2D-01	HIGH	可拆卸硬顶双门外廓。	READY
24303	24303	Hatchback	Insignia A Facelift		5	EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	HIGH	五门掀背改款外廓。	READY
24304_prefl	24304	Hatchback	Leon II Pre-Facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24304_facelift	24304	Hatchback	Leon II Facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24305	24305	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-SEDAN-4D-01	MEDIUM	CD391 四门轿车；输入终止月晚于该动力资料覆盖。	READY
24313	24313	SUV	Jimny III Facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	MEDIUM	三门封闭式 SUV。	READY
24314	24314	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-SUV-5D-01	HIGH	FJ系列五门封闭式SUV。	READY
24327_standardcab	24327	Pickup	Bongo III	PU	2	EU-KIA-BONGO-III-PU-PICKUP-STANDARD-CAB-01	MEDIUM	PU平台标准单排驾驶室分支。	READY
24327_kingcab	24327	Pickup	Bongo III	PU	2	EU-KIA-BONGO-III-PU-PICKUP-KING-CAB-01	MEDIUM	PU平台加长单排驾驶室分支。	READY
24327_doublecab	24327	Pickup	Bongo III	PU	4	EU-KIA-BONGO-III-PU-PICKUP-DOUBLE-CAB-01	MEDIUM	PU平台双排驾驶室分支。	READY
24343_my1990_91	24343	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	MEDIUM	输入Coupe对应三门掀背；拆分1990至1991年款外廓。	READY
24343_my1992_94	24343	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	MEDIUM	输入Coupe对应三门掀背；拆分1992至1994年款外廓。	READY
24344	24344	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	HIGH	输入Coupe对应前期三门掀背外廓。	READY
24345	24345	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	HIGH	前期Turbo三门掀背外廓。	READY
24346	24346	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	HIGH	1990至1991年款Turbo三门掀背外廓。	READY
24347	24347	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	MEDIUM	Duster三门外廓；输入起始月早于Duster公开年款。	READY
24348	24348	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	MEDIUM	2.5 Turbo三门外廓；输入终止月晚于该动力公开覆盖。	READY
24349	24349	Hatchback	Sundance P-body	P	3	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	HIGH	Duster 3.0三门掀背外廓。	READY
24350_my1990_91	24350	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	MEDIUM	输入Stufenheck对应五门掀背；拆分1990至1991年款外廓。	READY
24350_my1992_94	24350	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	MEDIUM	输入Stufenheck对应五门掀背；拆分1992至1994年款外廓。	READY
24351	24351	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	HIGH	输入Stufenheck对应前期五门掀背外廓。	READY
24352	24352	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	HIGH	前期Turbo五门掀背外廓。	READY
24353	24353	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	HIGH	1990至1991年款Turbo五门掀背外廓。	READY
24354	24354	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	MEDIUM	Duster五门外廓；输入起始月早于Duster公开年款。	READY
24355	24355	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	MEDIUM	2.5 Turbo五门外廓；输入终止月晚于该动力公开覆盖。	READY
24356	24356	Hatchback	Sundance P-body	P	5	EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	HIGH	Duster 3.0五门掀背外廓。	READY
24357	24357	MPV	Grand Voyager I	S	4	EU-PLYMOUTH-GRAND-VOYAGER-I-S-MPV-LWB-01	HIGH	3.3 LE对应长轴Grand Voyager外廓。	READY
24367	24367	MPV	Multivan T5		5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	短轴乘用车外廓。	READY
24375_swb_lowroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	短轴低顶厢式车。	READY
24375_swb_medroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	短轴中顶厢式车。	READY
24375_lwb_lowroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	长轴低顶厢式车。	READY
24375_lwb_medroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	长轴中顶厢式车。	READY
24375_lwb_highroof	24375	Van	Transporter T5	7H		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式车。	READY
24378	24378	Hatchback	i3 I01 Pre-Facelift	I01	5	EU-BMW-I3-I01-HATCHBACK-5D-PREFL-01	HIGH	75 kW 为官方持续功率，匹配前期 I01。	READY
24379_prefl	24379	Sedan	Q50 I V37 Pre-Facelift	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	MEDIUM	后驱柴油版前期外廓。	READY
24379_facelift	24379	Sedan	Q50 I V37 Facelift	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	MEDIUM	生产终期未知，保留改款后后驱分支。	READY
24380	24380	MPV	Scudo II	270		EU-FIAT-SCUDO-II-DANGEL-MPV-SWB-4X4-01	MEDIUM	Dangel短轴五座四驱外廓。	READY
24388_singlecab_lwb	24388	Pickup	Transporter T5 Facelift		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	MEDIUM	长轴单排底盘驾驶室分支。	READY
24388_doublecab_lwb	24388	Pickup	Transporter T5 Facelift		4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排底盘驾驶室分支。	READY
24398	24398	MPV	Wish I	ZNE10G	5	EU-TOYOTA-WISH-I-MPV-5D-2WD-01	HIGH	1.8 前驱 ZNE10G 外廓。	READY
24427	24427	Hatchback	500-4 / Evolution		3	EU-AIXAM-500-4-HATCHBACK-3D-01	MEDIUM	500-4三门微型车外廓。	READY
24428	24428	Hatchback	Aixam A7xx	K34VBA	2	EU-AIXAM-A7XX-HATCHBACK-SWB-01	HIGH	A.721短轴双门车身。	READY
24429	24429	Hatchback	Aixam A7xx	K44VBA	2	EU-AIXAM-A7XX-HATCHBACK-LWB-01	HIGH	A.741长轴双门车身。	READY
24430	24430	Hatchback	Aixam A7xx		2	EU-AIXAM-A7XX-HATCHBACK-LWB-01	MEDIUM	A.751与A.741共用长轴车身外廓。	READY
24431	24431	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24432	24432	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	MEDIUM	汽油动力不改变单排长轴Dropside外廓。	READY
24433	24433	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24434	24434	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24435	24435	Pickup	Vivaro A		2	EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	HIGH	单排长轴Dropside外廓。	READY
24436	24436	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期五门旅行车。	READY
24437	24437	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期五门旅行车。	READY
24438_prefl	24438	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24438_facelift	24438	Wagon	V70 III Facelift	135	5	EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24439	24439	Wagon	V70 III Pre-Facelift	135	5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH	前期 AWD 五门旅行车。	READY
24440	24440	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88 双门敞篷。	READY
24441	24441	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH	E88 双门敞篷。	READY
24450_prefl	24450	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24450_facelift	24450	Hatchback	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24451_prefl	24451	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24451_facelift	24451	Hatchback	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24452	24452	Hatchback	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	生产期止于改款前。	READY
24453	24453	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	生产期止于改款前。	READY
24454	24454	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	生产期止于改款前。	READY
24455_prefl	24455	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24455_facelift	24455	Sedan	Mondeo IV Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24456_prefl	24456	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24456_facelift	24456	Wagon	Mondeo IV Turnier Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24457_prefl	24457	Sedan	Mondeo IV Pre-Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24457_facelift	24457	Sedan	Mondeo IV Facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24458_prefl	24458	Wagon	Mondeo IV Turnier Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24458_facelift	24458	Wagon	Mondeo IV Turnier Facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24459_prefl	24459	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24459_facelift	24459	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24460_prefl	24460	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24460_facelift	24460	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24461_prefl	24461	MPV	S-Max I Pre-Facelift	WA6	5	EU-FORD-S-MAX-I-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24461_facelift	24461	MPV	S-Max I Facelift	WA6	5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24462_prefl	24462	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24462_facelift	24462	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24463_prefl	24463	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24463_facelift	24463	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24464_prefl	24464	MPV	Galaxy II Pre-Facelift	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	MEDIUM	Ktype 跨改款，拆分前期外廓。	READY
24464_facelift	24464	MPV	Galaxy II Facelift	WA6	5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	MEDIUM	Ktype 跨改款，拆分改款外廓。	READY
24465_van	24465	Van	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖货运封闭车身分支。	READY
24465_mpv	24465	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖乘用车身分支。	READY
24466	24466	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	短轴乘用车身。	READY
24467_van	24467	Van	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖货运封闭车身分支。	READY
24467_mpv	24467	MPV	Caddy III Pre-Facelift			EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	输入同时覆盖乘用车身分支。	READY
24468	24468	Wagon	Nubira J200	J200	5	EU-CHEVROLET-NUBIRA-J200-WAGON-01	HIGH	J200 五门旅行车。	READY
24469	24469	Hatchback	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200 五门掀背。	READY
24470	24470	Sedan	Epica V250	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250 柴油四门轿车。	READY
24471	24471	SUV	Captiva I C100	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100 五门 SUV。	READY
24472	24472	Coupe	TT 8J TTS	8J3	3	EU-AUDI-TT-8J-TTS-COUPE-3D-01	HIGH	TTS 三门 Coupe 外廓。	READY
24473	24473	Convertible	TT 8J TTS	8J9	2	EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	HIGH	TTS 双门 Roadster 外廓。	READY
24474	24474	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
24475	24475	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
24476	24476	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH	X250 四门轿车。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1901-2000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-X351-XJR-SEDAN-SWB-01	5127	1899	1456	Jaguar XJ 2014 official Specification and Price Guide	https://xr793.com/wp-content/uploads/2022/10/2014-Jaguar-XJ-Specs-Price-Guide-UK.pdf
EU-VW-BEETLE-A5-HATCHBACK-3D-01	4278	1808	1486	Volkswagen Newsroom — The Beetle International Driving Presentation	https://www.volkswagen-newsroom.com/en/the-beetle-international-driving-presentation-3009
EU-THINK-CITY-A306-HATCHBACK-3D-01	3143	1658	1596	Motoro — THINK CITY Swiss type-approval specifications	https://motoro.ch/en/fiche-technique/think/city
EU-FERRARI-348-SPIDER-CONVERTIBLE-2D-01	4230	1894	1170	Automobile-Catalog — 1993 Ferrari 348 Spider Europe specifications	https://www.automobile-catalog.com/car/1993/706865/ferrari_348_spider.html
EU-SUBARU-LEONE-III-HATCHBACK-3D-01	4370	1660	1385	Drive.Place — Subaru Leone III 1.8 90 hp Coupe specifications	https://subaru.drive.place/leone/iii/group_coupe/557630
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412	Automobile-Catalog — 1992 Renault 19 Chamade 1.7 TXI	https://www.automobile-catalog.com/car/1992/2942480/renault_19_chamade_1_7_txi.html
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412	Cars-Directory — Renault 19 II Chamade facelift specifications	https://www.cars-directory.net/car-specs/renault/19/19-chamade-l53-facelift-1992-3740/
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-MWB-01	5369	1990	2198	Vauxhall Movano Dec 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-NISSAN-INTERSTAR-X70-CHASSIS-CAB-LWB-01	5869	1990	2194	Vauxhall Movano Dec 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-NISSAN-INTERSTAR-X70-CHASSIS-CREW-CAB-LWB-01	5869	1990	2202	Vauxhall Movano Dec 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429	Auto-Data — Renault Laguna II specifications	https://www.auto-data.net/en/renault-laguna-ii-generation-2120
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429	Auto-Data — Renault Laguna II specifications	https://www.auto-data.net/en/renault-laguna-ii-generation-2120
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443	Auto-Data — Renault Laguna II Grandtour specifications	https://www.auto-data.net/en/renault-laguna-ii-grandtour-generation-2119
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443	Auto-Data — Renault Laguna II Grandtour specifications	https://www.auto-data.net/en/renault-laguna-ii-grandtour-generation-2119
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	Auto-Data — Seat Altea 1.4 TSI specifications	https://www.auto-data.net/en/seat-altea-5p-1.4-tsi-125hp-13578
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data — Seat Altea facelift specifications	https://www.auto-data.net/en/seat-altea-facelift-2009-1.8-tsi-160hp-52668
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622	Auto-Data — Seat Altea Freetrack specifications	https://www.auto-data.net/en/seat-altea-freetrack-generation-2914
EU-VW-SHARAN-I-7M8-PREFL-MPV-01	4620	1810	1730	Volkswagen — Sharan 1 previous-model specifications	https://www.volkswagen.de/de/besitzer-und-service/ueber-ihr-auto/vorgaengermodelle/mpv/sharan-1.html
EU-VW-POLO-IV-9N2-SEDAN-4D-01	4179	1650	1484	Auto-Data — Volkswagen Polo IV (9N) Sedan 1.6	https://www.auto-data.net/en/volkswagen-polo-iv-9n-sedan-1.6-101hp-56858
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Volkswagen Newsroom — Passat B6 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b6-profile-19550
EU-BUICK-CENTURY-IV-COUPE-FACELIFT-01	4803	1763	1364	Automobile-Catalog — 1986 Buick Century Custom Coupe 3.8L V6	https://www.automobile-catalog.com/car/1986/315200/buick_century_custom_coupe_3_8l_v-6.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1978-01	4978	1781	1415	Automobile-Catalog — 1978 Buick Century Custom Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1978/178970/buick_century_custom_station_wagon_3_8l_v-6_automatic.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1979-01	4978	1834	1415	Automobile-Catalog — 1979 Buick Century Special Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1979/180305/buick_century_special_station_wagon_3_8l_v-6_automatic.html
EU-BUICK-CENTURY-1978-1981-A-WAGON-MY1980-1981-01	4996	1808	1415	Automobile-Catalog — 1981 Buick Century Station Wagon 3.8L V6	https://www.automobile-catalog.com/car/1981/181940/buick_century_station_wagon_3_8l_v-6_automatic.html
EU-FERRARI-F50-TARGA-2D-01	4480	1986	1120	Automobile-Catalog — 1995 Ferrari F50 Europe specifications	https://www.automobile-catalog.com/car/1995/706985/ferrari_f50.html
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498	Auto-Data — Opel Insignia Hatchback A facelift specifications	https://www.auto-data.net/en/opel-insignia-hatchback-a-facelift-2013-opc-2.8-v6-325hp-awd-turbo-ecotec-19617
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data — Seat Leon II 1P specifications	https://www.auto-data.net/en/seat-leon-ii-1p-1.8-tsi-160hp-46446
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data — Seat Leon II facelift FR specifications	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-fr-2.0-tdi-cr-170hp-dpf-dsg-46488
EU-FORD-MONDEO-V-SEDAN-4D-01	4871	1852	1482	Auto-Data — Ford Mondeo Sedan 2.0 EcoBoost 240 Hp Automatic	https://www.auto-data.net/en/ford-mondeo-iv-sedan-2.0-ecoboost-240hp-automatic-20472
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705	Auto-Data — Suzuki Jimny III facelift specifications	https://www.auto-data.net/en/suzuki-jimny-model-217
EU-SSANGYONG-MUSSO-I-SUV-5D-01	4640	1905	1735	Auto-Data — SsangYong Musso I; Automobile-Catalog — Musso FJ-series	https://www.auto-data.net/en/ssangyong-musso-model-1816;https://www.automobile-catalog.com/car/1996/3159500/ssangyong_musso_e32.html
EU-KIA-BONGO-III-PU-PICKUP-STANDARD-CAB-01	5125	1740	1995	Kia Bongo III official brochure	https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/en_brochure/en_catalog_bongo3.pdf
EU-KIA-BONGO-III-PU-PICKUP-KING-CAB-01	5115	1740	1995	Kia Bongo III official brochure	https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/en_brochure/en_catalog_bongo3.pdf
EU-KIA-BONGO-III-PU-PICKUP-DOUBLE-CAB-01	5125	1740	1995	Kia Bongo III official brochure	https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/en_brochure/en_catalog_bongo3.pdf
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1990-91-01	4361	1709	1336	Plymouth 1990 official Sundance brochure	https://xr793.com/wp-content/uploads/2025/04/1990-Plymouth-Sundance.pdf
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1992-94-01	4361	1709	1346	Automobile-Catalog — 1992 Plymouth Sundance Duster 3.0-liter V6	https://www.automobile-catalog.com/car/1992/2728760/plymouth_sundance_duster_3_0-liter_v6.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-3D-MY1987-89-01	4361	1709	1339	Automobile-Catalog — 1987 Plymouth Sundance 2.2-liter	https://www.automobile-catalog.com/car/1987/2727935/plymouth_sundance_2_2-liter.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1990-91-01	4361	1709	1336	Plymouth 1990 official Sundance brochure	https://xr793.com/wp-content/uploads/2025/04/1990-Plymouth-Sundance.pdf
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1992-94-01	4361	1709	1346	Automobile-Catalog — 1992 Plymouth Sundance Duster 3.0-liter V6	https://www.automobile-catalog.com/car/1992/2728760/plymouth_sundance_duster_3_0-liter_v6.html
EU-PLYMOUTH-SUNDANCE-P-HATCHBACK-5D-MY1987-89-01	4361	1709	1339	Automobile-Catalog — 1987 Plymouth Sundance 2.2-liter	https://www.automobile-catalog.com/car/1987/2727935/plymouth_sundance_2_2-liter.html
EU-PLYMOUTH-GRAND-VOYAGER-I-S-MPV-LWB-01	4839	1834	1643	Plymouth 1990 official Voyager brochure	https://xr793.com/wp-content/uploads/2020/01/1990-Plymouth-Voyager.pdf
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Volkswagen Multivan T5 official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/03/VW-Multivan-2008-INT.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-BMW-I3-I01-HATCHBACK-5D-PREFL-01	3999	1775	1578	BMW Group PressClub — Technical Specifications BMW i3 valid from 03/2014	https://www.press.bmwgroup.com/global/article/attachment/T0243308EN/339148
EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	4783	1824	1443	Auto-Data — Infiniti Q50 pre-facelift specifications	https://www.auto-data.net/en/infiniti-q50-s-3.5-v6-364hp-hybrid-automatic-18982
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	4810	1820	1430	Auto-Data — Infiniti Q50 facelift RWD specifications	https://www.auto-data.net/en/infiniti-q50-facelift-2017-s-3.0t-405hp-automatic-31419
EU-FIAT-SCUDO-II-DANGEL-MPV-SWB-4X4-01	4805	1895	1880	Motoro — FIAT-DANGEL Scudo 2.0 MJ Swiss type approval	https://motoro.ch/en/fiche-technique/fiat-dangel/scudo-2-0-mj
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949	Volkswagen Transporter T5 official technical specification	https://www.vwpress.co.uk/assets/documents/original/519-Transporter_Price_List__Tech_Spec_1.pdf
EU-TOYOTA-WISH-I-MPV-5D-2WD-01	4550	1695	1590	Toyota Motor Corporation — 75 Years of Toyota, First-generation Wish 1.8 2WD	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60007858/index.html
EU-AIXAM-500-4-HATCHBACK-3D-01	2885	1440	1365	Auta5P — Aixam 500-4 2003 specifications	https://auta5p.eu/lang/en/katalog/auto.php?idf=Aixam-500-4-263
EU-AIXAM-A7XX-HATCHBACK-SWB-01	2674	1474	1460	Aixam-Mega official A721-A741 user manual	https://www.aixam-mega-sav.com/data/gamme/doc/user%20manual%20a721-a741.pdf
EU-AIXAM-A7XX-HATCHBACK-LWB-01	2897	1474	1460	Aixam-Mega official A721-A741 user manual; AutoCentrum — Aixam A.751 specifications	https://www.aixam-mega-sav.com/data/gamme/doc/user%20manual%20a721-a741.pdf;https://www.autocentrum.pl/dane-techniczne/aixam/a-751/
EU-OPEL-VIVARO-A-DROPSIDE-LWB-01	5350	1980	2000	Vauxhall Vivaro Dropside 2011 Models Edition 2 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Dropside_Conv_April_2011.pdf
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547	Auto-Data — Volvo V70 III specifications	https://www.auto-data.net/en/volvo-v70-iii-generation-1931
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547	Auto-Data — Volvo V70 model specifications	https://www.auto-data.net/en/volvo-v70-model-918
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411	Auto-Data — BMW 1 Series Convertible E88 120i	https://www.auto-data.net/en/bmw-1-series-convertible-e88-120i-170hp-9829
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Ford Mondeo 2007 official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Ford-Mondeo-2007-UK.pdf
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Ford Mondeo 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500	Ford Mondeo 2007 official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Ford-Mondeo-2007-UK.pdf
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Ford Mondeo 2007 official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Ford-Mondeo-2007-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500	Ford Mondeo 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Ford Mondeo 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Mondeo-UK.pdf
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658	Ford S-Max 2008 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-S-MAX-UK.pdf
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Ford S-Max 2011 official brochure	https://www.onlymanuals.com/ford/s_max/ford_s_max_brochure_2011_2011_2
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723	Ford Galaxy 2008 official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Ford-Galaxy-2008-UK.pdf
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758	Ford Galaxy 2011 official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Galaxy-UK.pdf
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833	CarsGuide — Volkswagen Caddy 2008 dimensions	https://www.carsguide.com.au/volkswagen/caddy/car-dimensions/2008
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460	Auto-Data — Chevrolet Nubira model specifications	https://www.auto-data.net/en/chevrolet-nubira-model-1576
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data — Chevrolet Lacetti model specifications	https://www.auto-data.net/en/chevrolet-lacetti-model-1590
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450	Auto-Data — Chevrolet Epica specifications	https://www.auto-data.net/en/chevrolet-epica-generation-3201
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Auto-Data — Chevrolet Captiva model specifications	https://www.auto-data.net/en/chevrolet-captiva-model-1623
EU-AUDI-TT-8J-TTS-COUPE-3D-01	4198	1842	1345	Audi AG — Audi TTS brochure (2009)	https://xr793.com/wp-content/uploads/2023/04/2009-Audi-TTS-AUS.pdf
EU-AUDI-TT-8J-TTS-CONVERTIBLE-2D-01	4198	1842	1350	Audi AG — Audi TTS brochure (2009)	https://xr793.com/wp-content/uploads/2023/04/2009-Audi-TTS-AUS.pdf
EU-JAGUAR-XF-I-SEDAN-X250-01	4961	1877	1460	Auto-Data — Jaguar XF X250 specifications	https://www.auto-data.net/en/jaguar-xf-x250-generation-71
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1901-2000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/en_brochure/en_catalog_bongo3.pdf "https://www.kia.com/content/dam/kwp/kr/ko/vehicles/pdf/en_brochure/en_catalog_bongo3.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5563 行）
- 累计尺寸组：dimension_groups_final.tsv（2379 行）

