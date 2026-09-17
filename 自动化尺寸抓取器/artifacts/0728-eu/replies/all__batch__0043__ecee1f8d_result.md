# 任务：all 第 4201-4300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0043__ecee1f8d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4201-4300 行

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
all 第 4201-4300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951
EU-NISSAN-200SX-S13-COUPE-2D-01	4535	1690	1290
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Nissan	200sx	2.0 I 16V Turbo	Coupe	Heckantrieb	Benzin	147	200	Oct 1993	Dec 1999	2024-03-01	4338
Nissan	Primera	2.0 I	Stufenheck	Frontantrieb	Benzin	92	125	Jan 1995	Jun 1996	2024-03-01	4339
Nissan	Primera	2.0 I	Schrägheck	Frontantrieb	Benzin	92	125	Jan 1995	Jun 1996	2024-03-01	4340
Daihatsu	Cuore i	0.5	Schrägheck	Frontantrieb	Benzin	20	27	Oct 1980	Sep 1985	2024-03-01	4341
Daihatsu	Cuore i	0.6	Schrägheck	Frontantrieb	Benzin	22	30	Aug 1982	Sep 1985	2024-03-01	4342
Daihatsu	Cuore ii	0.8	Schrägheck	Frontantrieb	Benzin	29	39	Nov 1989	Dec 1990	2024-03-01	4343
Daihatsu	Cuore iii	0.8	Schrägheck	Frontantrieb	Benzin	30	41	Oct 1990	Dec 1994	2024-03-01	4344
Daihatsu	Cuore ii	0.8	Schrägheck	Frontantrieb	Benzin	32	44	Sep 1985	Jun 1990	2024-03-01	4345
Daihatsu	Charade ii	1.0 D	Schrägheck	Frontantrieb	Diesel	27	37	Oct 1983	Mar 1987	2024-03-01	4346
Daihatsu	Charade ii	1.0 TD	Schrägheck	Frontantrieb	Diesel	34	46	Feb 1985	Mar 1987	2024-03-01	4347
Daihatsu	Charade i	1	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1977	Feb 1981	2024-03-01	4348
Mercedes-benz	G-Klasse	G 55 AMG	Geländewagen geschlossen	Allrad	Benzin	373	507	Aug 2008	Jun 2012	2024-03-01	4349
Daihatsu	Charade i	1	Schrägheck	Frontantrieb	Benzin	38	52	Feb 1981	Feb 1983	2024-03-01	4350
Dacia	Logan	1.4 MPI LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	55	75	Feb 2006	Dec 2012	2024-03-01	4351
Daihatsu	Charade ii	1	Schrägheck	Frontantrieb	Benzin	38	52	Oct 1983	Mar 1987	2024-03-01	4352
Daihatsu	Charade ii	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	50	68	Oct 1983	Mar 1987	2024-03-01	4353
Daihatsu	Charmant	1.3	Stufenheck	Heckantrieb	Benzin	48	65	Nov 1981	Jul 1987	2024-03-01	4354
Daihatsu	Charmant	1.6	Stufenheck	Heckantrieb	Benzin	57	78	Sep 1985	Jul 1987	2024-03-01	4355
Daihatsu	Charmant	1.6	Stufenheck	Heckantrieb	Benzin	60	82	May 1986	Jul 1987	2024-03-01	4356
Daihatsu	Charmant	1.6	Stufenheck	Heckantrieb	Benzin	61	83	Aug 1983	Jul 1987	2024-03-01	4357
Daihatsu	Charmant	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Dec 1981	Sep 1984	2024-03-01	4358
Daihatsu	Wildcat/rocky	2.8 D	Geländewagen offen	Allrad	Diesel	54	73	Feb 1985	Mar 1987	2024-03-01	4359
Daihatsu	Wildcat/rocky	2.8 D	Geländewagen geschlossen	Allrad	Diesel	54	73	Feb 1985	Mar 1987	2024-03-01	4360
Daihatsu	Wildcat/rocky	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	65	88	Sep 1985	Apr 1987	2024-03-01	4361
Daihatsu	Wildcat/rocky	2.8 TD	Geländewagen offen	Allrad	Diesel	65	88	Sep 1985	Apr 1987	2024-03-01	4362
Subaru	Leone ii	1800 4WD	Stufenheck	Allrad	Benzin	59	80	Sep 1980	Oct 1984	2024-03-01	4363
Subaru	Leone ii	1800 4WD	Stufenheck	Allrad	Benzin	60	82	Sep 1980	Oct 1984	2024-03-01	4364
Daihatsu	Rocky soft top	2	Geländewagen offen	Allrad	Benzin	65	88	Feb 1985	Apr 1993	2024-03-01	4365
Daihatsu	Rocky hard top	2.0 4X4	Geländewagen geschlossen	Allrad	Benzin	65	88	Feb 1985	Apr 1993	2024-07-01	4366
Subaru	Leone ii hatchback	1800 4WD	Schrägheck	Allrad	Benzin	59	80	Sep 1980	Oct 1984	2024-03-01	4367
Subaru	Leone ii hatchback	1800 Turismo 4WD	Schrägheck	Allrad	Benzin	60	82	Sep 1980	Oct 1984	2024-03-01	4368
Daihatsu	Rocky soft top	2.8 TD	Geländewagen offen	Allrad	Diesel	67	91	Dec 1987	Apr 1993	2024-03-01	4369
Subaru	Leone ii station wagon	1800 4WD	Kombi	Allrad	Benzin	59	80	Sep 1980	Oct 1984	2024-03-01	4370
Subaru	Leone ii station wagon	1800 Super 4WD	Kombi	Allrad	Benzin	60	82	Sep 1980	Oct 1984	2024-03-01	4371
Daihatsu	Rocky hard top	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	67	91	Dec 1987	Apr 1993	2024-07-01	4372
Nissan	Kubistar	1.5 DCI	Kasten	Frontantrieb	Diesel	45	61	Aug 2005	Oct 2009	2024-03-01	4373
Daihatsu	Rocky soft top	2.8 D	Geländewagen offen	Allrad	Diesel	54	73	Feb 1985	Dec 1998	2024-03-01	4374
Daihatsu	Rocky hard top	2.8 D	Geländewagen geschlossen	Allrad	Diesel	54	73	Feb 1985	Dec 1998	2024-07-01	4375
Daihatsu	Rocky soft top	2.8 TD	Geländewagen offen	Allrad	Diesel	75	102	Sep 1991	Dec 1998	2024-03-01	4376
Daihatsu	Rocky hard top	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	75	102	Sep 1991	Dec 1998	2024-07-01	4377
Daihatsu	Feroza soft top	1.6 16V	Geländewagen offen	Allrad	Benzin	63	86	Oct 1988	Dec 1999	2024-03-01	4378
Daihatsu	Feroza hard top	1.6 16V 4X4	Geländewagen geschlossen	Allrad	Benzin	63	86	Oct 1988	Dec 1999	2024-03-01	4379
Daihatsu	Feroza soft top	1.6 I 16V	Geländewagen offen	Allrad	Benzin	70	95	Oct 1988	Dec 1999	2024-03-01	4380
Subaru	Leone iii	1800 4WD	Stufenheck	Allrad	Benzin	66	90	Nov 1984	Dec 1990	2024-03-01	4381
Daihatsu	Feroza hard top	1.6 I 16V 4X4	Geländewagen geschlossen	Allrad	Benzin	70	95	Oct 1988	Dec 1999	2024-03-01	4382
Subaru	Leone iii	1800 4WD	Stufenheck	Allrad	Benzin	72	98	Jan 1988	Dec 1990	2024-03-01	4383
Subaru	Leone iii	1800 Turbo 4WD	Stufenheck	Allrad	Benzin	96	131	Mar 1989	Dec 1990	2024-03-01	4384
Subaru	Leone iii station wagon	1800 4WD	Kombi	Allrad	Benzin	66	90	Nov 1984	Dec 1990	2024-03-01	4385
Daihatsu	Charade iii	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	50	68	Mar 1987	Oct 1990	2024-03-01	4386
Subaru	Leone iii	1800 Turbo 4WD	Stufenheck	Allrad	Benzin	100	136	Nov 1984	Dec 1990	2024-03-01	4387
Subaru	Leone iii station wagon	1800 4WD	Kombi	Allrad	Benzin	72	98	Dec 1986	Jul 1991	2024-03-01	4388
Daihatsu	Charade iii	1.0 D	Schrägheck	Frontantrieb	Diesel	27	37	Mar 1987	Dec 1992	2024-03-01	4389
Subaru	Leone iii station wagon	1800 Super 4WD	Kombi	Allrad	Benzin	96	131	Mar 1989	Dec 1990	2024-03-01	4390
Subaru	Leone iii station wagon	1800 Super Turbo 4WD	Kombi	Allrad	Benzin	100	136	Nov 1984	Dec 1990	2024-03-01	4391
Daihatsu	Charade iii	1.0 TD	Schrägheck	Frontantrieb	Diesel	35	48	Mar 1987	Dec 1992	2024-03-01	4392
Daihatsu	Charade iii	1	Schrägheck	Frontantrieb	Benzin	38	52	Mar 1987	Dec 1992	2024-03-01	4393
Daihatsu	Charade iii	1	Schrägheck	Frontantrieb	Benzin	40	54	Nov 1990	Dec 1992	2024-03-01	4394
Subaru	Xt	1.8 Turbo 4WD	Coupe	Allrad	Benzin	88	120	Jan 1988	Dec 1990	2024-03-01	4395
Daihatsu	Charade iii	1	Schrägheck	Frontantrieb	Benzin	41	56	Apr 1989	Dec 1992	2024-03-01	4396
Subaru	Xt	1.8 Turbo 4WD	Coupe	Allrad	Benzin	96	131	Jan 1987	Dec 1990	2024-03-01	4397
Daihatsu	Charade iii	1.0 GTI	Schrägheck	Frontantrieb	Benzin	74	101	Mar 1987	Dec 1992	2024-03-01	4398
Subaru	Xt	1.8 Turbo 4WD	Coupe	Allrad	Benzin	100	136	Nov 1984	Dec 1990	2024-03-01	4399
Daihatsu	Charade iii	1.3 I	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1988	Dec 1992	2024-03-01	4400
Daihatsu	Charade iii	1.3 I 4WD	Schrägheck	Allrad	Benzin	66	90	Jun 1988	Jan 1993	2024-03-01	4401
Daihatsu	Applause i	1.6 16V	Schrägheck	Frontantrieb	Benzin	77	105	Jun 1989	Jul 1997	2024-03-01	4402
Subaru	Justy i	1000	Schrägheck	Frontantrieb	Benzin	40	54	Nov 1984	Jun 1989	2024-03-01	4403
Daihatsu	Applause i	1.6 16V 4WD	Schrägheck	Allrad	Benzin	77	105	Jun 1989	Jul 1997	2024-03-01	4404
Daihatsu	Charade iv	1.3 I 16V	Schrägheck	Frontantrieb	Benzin	62	84	Jan 1993	Sep 2000	2024-03-01	4405
Daihatsu	Charade iv	1.6 GTI	Schrägheck	Frontantrieb	Benzin	77	105	Mar 1993	Nov 1999	2024-03-01	4406
Subaru	Justy i	1000 4WD	Schrägheck	Allrad	Benzin	40	54	Nov 1984	Dec 1990	2024-03-01	4407
Daihatsu	Charade iv	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	66	90	Jun 1994	Nov 1999	2024-03-01	4408
Subaru	Justy i	1000	Schrägheck	Frontantrieb	Benzin	37	50	May 1987	Oct 1995	2024-03-01	4409
Subaru	Justy i	1000 4WD	Schrägheck	Allrad	Benzin	37	50	May 1987	Nov 1994	2024-03-01	4410
Subaru	Justy i	1200	Schrägheck	Frontantrieb	Benzin	49	67	May 1987	Oct 1995	2024-03-01	4411
Subaru	Justy i	1200 4WD	Schrägheck	Allrad	Benzin	49	67	May 1987	May 1991	2024-03-01	4412
Subaru	Justy i	1200 4WD	Schrägheck	Allrad	Benzin	55	75	Oct 1990	Apr 1996	2024-03-01	4413
Subaru	Justy i	1200 4WD	Schrägheck	Allrad	Benzin	50	68	Oct 1986	Dec 1990	2024-03-01	4414
Subaru	Libero	1.0 4WD	Bus	Allrad	Benzin	37	50	Jan 1983	Dec 1987	2024-03-01	4415
Subaru	Libero	1.2 4WD	Bus	Allrad	Benzin	38	52	Aug 1986	Feb 2000	2024-03-01	4416
Suzuki	Alto i	0.8	Schrägheck	Frontantrieb	Benzin	29	39	Jun 1982	Aug 1984	2024-03-01	4417
BMW	5	525 D Xdrive	Stufenheck	Allrad	Diesel	155	211	Sep 2011	Oct 2016	2024-03-01	4418
Subaru	Libero	1.2 I 4WD	Bus	Allrad	Benzin	40	54	Aug 1991	Feb 2000	2024-03-01	4419
Subaru	Legacy i	1800 4WD	Stufenheck	Allrad	Benzin	76	103	Jan 1989	Sep 1991	2024-03-01	4420
Subaru	Legacy i	2000 4WD	Stufenheck	Allrad	Benzin	85	116	Aug 1991	Jul 1994	2024-03-01	4421
Subaru	Legacy i	2200 4WD	Stufenheck	Allrad	Benzin	100	136	Jan 1989	Jul 1994	2024-03-01	4422
Subaru	Legacy i	2000 Turbo 4WD	Stufenheck	Allrad	Benzin	147	200	May 1992	Jul 1994	2024-03-01	4423
Suzuki	Alto ii	0.8	Schrägheck	Frontantrieb	Benzin	29	39	Jan 1986	Dec 1988	2024-03-01	4424
Subaru	Legacy i station wagon	1800 4WD	Kombi	Allrad	Benzin	76	103	Jan 1989	Jul 1994	2024-03-01	4425
KIA	Sorento i	2.5 Crdi	SUV	Allrad	Diesel	120	163	May 2006	Dec 2011	2024-03-01	4426
Subaru	Legacy i station wagon	2000 4WD	Kombi	Allrad	Benzin	85	116	Sep 1991	Jul 1994	2024-03-01	4427
Subaru	Legacy i station wagon	2000 Turbo Super 4WD	Kombi	Allrad	Benzin	147	200	May 1992	Jul 1994	2024-03-01	4428
Subaru	Legacy i station wagon	2200 Super 4WD	Kombi	Allrad	Benzin	100	136	Jan 1989	Jul 1994	2024-03-01	4429
Subaru	Svx	3.3 I 24V 4WD	Coupe	Allrad	Benzin	169	230	Sep 1992	Sep 1994	2024-03-01	4430
Suzuki	Swift i	1	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1983	Mar 1989	2024-03-01	4431
Subaru	Impreza	1.6 I AWD	Stufenheck	Allrad	Benzin	66	90	Aug 1992	Dec 2000	2024-03-01	4432
Suzuki	Swift i	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	52	71	Feb 1985	Dec 1989	2024-03-01	4433
Subaru	Impreza	1.8 I AWD	Stufenheck	Allrad	Benzin	76	103	Aug 1992	Dec 2000	2024-03-01	4434
Subaru	Impreza station wagon	1.6 I AWD	Kombi	Allrad	Benzin	66	90	Aug 1992	Dec 2000	2024-03-01	4435
Suzuki	Swift i	1.3 Gti/gxi	Schrägheck	Frontantrieb	Benzin	74	101	Aug 1985	Mar 1989	2024-03-01	4436
Suzuki	Swift i	1.3	Schrägheck	Frontantrieb	Benzin	47	64	Aug 1986	Mar 1989	2024-03-01	4437


--- Round 1 / 首次发送 ---
## 更新点

* 已复用累计缓存中的 Nissan Primera I P10 轿车、掀背车尺寸组，以及 Mercedes-Benz G-Klasse W463 五门尺寸组；未重复输出既有尺寸事实。
* Ktype `4351` 的生产区间跨越 Logan I 2008 年改款，已拆分为前期与改款两条映射。前期车身为 `4250×1735×1525 mm`，改款后为 `4290×1740×1525 mm`；改款资料同时列出含后视镜宽度 `1989 mm`，因此落盘的 `1740 mm` 可确认是不含后视镜宽度。([汽车数据][1])
* Charade IV G200 已闭合三个尺寸组：普通 1.3 掀背车同时覆盖三门和五门、共用同一外廓；GTi 三门因长度不同单独建组；四门轿车单独建组。([汽车数据][2])
* Ktype `4338` 已确认属于两门 S14 系列，但现有欧洲规格候选资料在长度和高度上仍有冲突，因此按前期与改款分支保留 PENDING，不创建临时尺寸组。([Ultimate Specs][3])

## 当前批次进度

* READY 映射：9 行
* 已完全闭合输入 Ktype：7 / 100
* PENDING 或尚未处理输入 Ktype：93
* 当前已引用确认尺寸组：8 个

  * 复用既有尺寸组：3 个
  * 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4338_prefl	4338	Coupe	200SX S14	S14	2		LOW	S14前期两门外廓分支。	PENDING: S14前期欧洲规格三维冲突未闭合
4338_facelift	4338	Coupe	200SX S14 facelift	S14	2		LOW	S14改款两门外廓分支。	PENDING: S14改款欧洲规格三维冲突未闭合
4339	4339	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓，复用既有组。	READY
4340	4340	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓，复用既有组。	READY
4349	4349	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	HIGH	W463五门封闭式车身，复用既有组。	READY
4351_prefl	4351	Sedan	Logan I	L90	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	L90四门轿车，按2008改款前外廓拆分。	READY
4351_facelift	4351	Sedan	Logan I facelift	L90	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	L90四门轿车，按2008改款后外廓拆分。	READY
4405_3dr	4405	Hatchback	Charade IV	G200	3	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	MEDIUM	G200掀背车按三门边界拆分。	READY
4405_5dr	4405	Hatchback	Charade IV	G200	5	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	MEDIUM	G200掀背车按五门边界拆分。	READY
4406	4406	Hatchback	Charade IV	G200	3	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-GTI-01	HIGH	G200三门GTi外廓。	READY
4408	4408	Sedan	Charade IV	G200	4	EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	HIGH	G200四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525	Auto-Data Dacia Logan I 1.4 i (75 Hp)	https://www.auto-data.net/en/dacia-logan-i-1.4-i-75hp-15891
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525	Auto-Data Dacia Logan I facelift 2008 1.4 MPI (75 Hp)	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.4-mpi-75hp-43236
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	3780	1620	1390	Auto-Data Daihatsu Charade IV Com G200 1.3 i TS (84 Hp)	https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.3-i-ts-84hp-127
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-GTI-01	3750	1620	1390	Auto-Data Daihatsu Charade IV Com G200 1.6 GTi (105 Hp)	https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.6-gti-105hp-130
EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	4085	1620	1390	Auto-Data Daihatsu Charade IV G200 1.5 i 16V SX (90 Hp)	https://www.auto-data.net/de/daihatsu-charade-iv-g200-1.5-i-16v-sx-90hp-123
```

## 下一步优先处理

1. 优先消除 Ktype `4338` 的 S14 前期与 S14a 改款欧洲规格冲突。
2. 按代际聚类处理 Daihatsu Cuore I–III、Charade I–III 和 Charmant。
3. 批量闭合 Rocky/Feroza 的软顶、硬顶及长短车身边界，再处理 Subaru Leone II/III 各车身。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.4-mpi-75hp-43236 "Dacia Logan I (facelift 2008) 1.4 MPI (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.3-i-ts-84hp-127 "Daihatsu Charade IV Com (G200) 1.3 i TS (84 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.ultimatespecs.com/car-specs/Nissan/6647/Nissan-200-SX-S14-20-Turbo.html "Nissan 200 SX S14 2.0 Turbo Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Daihatsu Cuore III L201、Subaru XT、Daihatsu Applause I 与 Subaru SVX 车型簇；同外廓发动机版本直接共用尺寸组。([汽车数据][1])
* Ktype `4418` 的生产区间覆盖 BMW F10 改款前后，车长由 `4899 mm` 变为 `4907 mm`，已拆分为 `prefl` 与 `facelift` 两个物理分支。([汽车数据][2])

## 当前批次进度

* READY 映射：18 行
* 已完全闭合输入 Ktype：15 / 100
* 待处理或 PENDING 输入 Ktype：85
* 已确认并被引用尺寸组：15 个
* 本轮新增 READY 映射：9 行
* 本轮首次创建尺寸组：7 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4344	4344	Hatchback	Cuore III	L201	3	EU-DAIHATSU-CUORE-III-L201-HATCHBACK-3D-01	HIGH	L201三门掀背外廓。	READY
4395	4395	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	HIGH	XT两门轿跑外廓。	READY
4397	4397	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	MEDIUM	同代两门轿跑外廓。	READY
4399	4399	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	HIGH	XT两门轿跑外廓。	READY
4402	4402	Hatchback	Applause I	A101	5	EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	HIGH	A101前驱五门掀背外廓。	READY
4404	4404	Hatchback	Applause I	A111	5	EU-DAIHATSU-APPLAUSE-I-A111-HATCHBACK-4WD-01	HIGH	A111四驱五门外廓。	READY
4418_prefl	4418	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	MEDIUM	F10改款前四门轿车外廓。	READY
4418_facelift	4418	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	MEDIUM	F10 LCI改款后四门轿车外廓。	READY
4430	4430	Coupe	SVX	CXW	2	EU-SUBARU-SVX-CX-COUPE-2D-01	HIGH	CXW两门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CUORE-III-L201-HATCHBACK-3D-01	3295	1395	1410	Auto-Data Daihatsu Cuore L201 0.8 (41 Hp)	https://www.auto-data.net/en/daihatsu-cuore-l201-0.8-41hp-54
EU-SUBARU-XT-COUPE-2D-01	4450	1690	1335	Auto-Data Subaru XT Coupe 1.8 Turbo (120 Hp) 4WD; Auto-Data Subaru XT Coupe 1.8 Turbo (136 Hp) 4WD	https://www.auto-data.net/en/subaru-xt-coupe-1.8-turbo-120hp-4wd-16204;https://www.auto-data.net/en/subaru-xt-coupe-1.8-turbo-136hp-4wd-16205
EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	4315	1660	1385	Auto-Data Daihatsu Applause I A101 1.6 16V (105 Hp)	https://www.auto-data.net/en/daihatsu-applause-i-a101-a111-1.6-16v-a101-105hp-automatic-24500
EU-DAIHATSU-APPLAUSE-I-A111-HATCHBACK-4WD-01	4315	1660	1440	Auto-Data Daihatsu Applause I A111 1.6 16V 4WD (105 Hp)	https://www.auto-data.net/en/daihatsu-applause-i-a101-a111-1.6-16v-4wd-a111-105hp-35
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	Auto-Data BMW 5 Series Sedan F10 525d xDrive	https://www.auto-data.net/en/bmw-5-series-sedan-f10-525d-218hp-xdrive-steptronic-17271
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464	Auto-Data BMW 5 Series Sedan F10 LCI 525d xDrive	https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-525d-218hp-xdrive-steptronic-19964
EU-SUBARU-SVX-CX-COUPE-2D-01	4625	1777	1300	Auto-Data Subaru SVX CX 3.3 i 24V 4WD CXW (230 Hp)	https://www.auto-data.net/en/subaru-svx-cx-3.3-i-24v-4wd-cxw-230hp-16203
```

## 下一步优先处理

1. 解决 Ktype `4338` 的 Nissan 200SX S14 前期与改款尺寸冲突。
2. 批量闭合 Daihatsu Cuore I–II、Charade I–III 和 Charmant。
3. 按软顶、硬顶及车身长度边界处理 Daihatsu Wildcat/Rocky/Feroza。
4. 随后集中处理 Subaru Leone II、Leone III、Legacy I 的 Sedan、Hatchback 与 Wagon 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/daihatsu-cuore-l201-0.8-41hp-54 "Daihatsu Cuore (L201) 0.8 (41 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-5-series-sedan-f10-525d-218hp-xdrive-steptronic-17271 "BMW 5 Series Sedan (F10) 525d (218 Hp) xDrive Steptronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Subaru Legacy I 的 BC 轿车与 BJF 旅行车簇；跨 1991 年改款的 Ktype 按改款前后外廓拆分。
* Legacy I 改款轿车存在不同量产高度：1800/2200 AWD 为 `1400 mm`，2000 AWD 为 `1380 mm`，Turbo 为 `1385 mm`，分别建立尺寸组。([汽车数据][1])
* Legacy I 旅行车改款前为 `4600×1690×1490 mm`；改款后自然吸气车型为 `4620×1690×1480 mm`，Turbo 为 `4620×1690×1465 mm`。([汽车数据][2])
* 闭合 Subaru Impreza I GC 轿车和 GF 旅行车 1.6 AWD 车型簇。([汽车数据][3])

## 当前批次进度

* READY 映射：33 行
* 已完全闭合输入 Ktype：26 / 100
* PENDING 或尚未处理输入 Ktype：74
* 已确认并被引用尺寸组：24 个
* 本轮新增 READY 映射：15 行
* 本轮首次创建尺寸组：9 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4420_prefl	4420	Sedan	Legacy I	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	HIGH	跨1991改款，改款前外廓。	READY
4420_facelift	4420	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	HIGH	跨1991改款，改款后1800 AWD外廓。	READY
4421	4421	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-2000-01	HIGH	改款后2000 AWD外廓。	READY
4422_prefl	4422	Sedan	Legacy I	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	HIGH	跨1991改款，改款前外廓。	READY
4422_facelift	4422	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	HIGH	跨1991改款，改款后2200 AWD外廓。	READY
4423	4423	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-TURBO-01	MEDIUM	改款后Turbo轿车外廓。	READY
4425_prefl	4425	Wagon	Legacy I	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	HIGH	跨1991改款，改款前旅行车外廓。	READY
4425_facelift	4425	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	跨1991改款，改款后旅行车外廓。	READY
4427	4427	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
4428	4428	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-TURBO-01	HIGH	改款后Turbo旅行车外廓。	READY
4429_prefl	4429	Wagon	Legacy I	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	HIGH	跨1991改款，改款前旅行车外廓。	READY
4429_facelift	4429	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	跨1991改款，改款后旅行车外廓。	READY
4432	4432	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门轿车外廓。	READY
4434	4434	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门轿车外廓。	READY
4435	4435	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	HIGH	GF五门1.6 AWD旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	4510	1690	1385	Auto-Data Subaru Legacy I BC generation	https://www.auto-data.net/en/subaru-legacy-i-bc-generation-3617
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	4545	1690	1400	Auto-Data Subaru Legacy I BC facelift 1800 AWD; Auto-Data Subaru Legacy I BC facelift 2200 AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-1800-103hp-awd-34241;https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2200-136hp-awd-16191
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-2000-01	4545	1690	1380	Auto-Data Subaru Legacy I BC facelift 2000 AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2000-116hp-awd-16188
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-TURBO-01	4545	1690	1385	Auto-Data Subaru Legacy I BC facelift 2000 Turbo AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2000-turbo-220hp-awd-16190
EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	4600	1690	1490	Auto-Data Subaru Legacy I Station Wagon BJF generation	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-generation-3618
EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	4620	1690	1480	Auto-Data Subaru Legacy I BJF facelift 1800 AWD; Auto-Data Subaru Legacy I BJF facelift 2000 AWD; Auto-Data Subaru Legacy I BJF facelift 2200 AWD	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-1800-103hp-awd-34172;https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2000-116hp-awd-automatic-24057;https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2200-136hp-awd-34173
EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-TURBO-01	4620	1690	1465	Auto-Data Subaru Legacy I BJF facelift 2000 Turbo AWD	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2000-turbo-200hp-awd-16195
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415	Auto-Data Subaru Impreza I GC 1.6i AWD	https://www.auto-data.net/en/subaru-impreza-i-gc-1.6i-90hp-4wd-16095
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420	Auto-Data Subaru Impreza I GF 1.6i AWD	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-1.6i-90hp-4wd-16111
```

## 下一步优先处理

1. 闭合 Subaru Leone II、Leone III 的 Sedan、Hatchback 与 Wagon 分支。
2. 处理 Daihatsu Rocky、Wildcat 与 Feroza 的软顶、硬顶及不同车宽分支。
3. 集中处理 Charade I–III、Cuore I–II 和 Charmant。
4. 最后消除 Nissan 200SX S14 前期与改款尺寸冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-1800-103hp-awd-34241?utm_source=chatgpt.com "Subaru Legacy I (BC, facelift 1991) 1800 (103 Hp) AWD"
[2]: https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-generation-3618?utm_source=chatgpt.com "Subaru Legacy I Station Wagon (BJF) /1989, 1990, 1991"
[3]: https://www.auto-data.net/en/subaru-impreza-i-gc-1.6i-90hp-4wd-16095?utm_source=chatgpt.com "Subaru Impreza I (GC) 1.6i (90 Hp) 4WD /Sedan 1992"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Subaru Leone II 的 Sedan、Hatchback、标准顶 Wagon 与 Super Station 高顶 Wagon 车型簇。
* 已闭合 Subaru Leone III 的四驱 Sedan、Turbo Sedan、标准顶 Wagon 与 Super Station 高顶 Wagon 车型簇。
* 同一外廓的发动机功率版本直接关联同一尺寸组，未重复建组。([汽车目录][1])

## 当前批次进度

* READY 映射：47 行
* PENDING 映射：2 行
* 已完全闭合输入 Ktype：40 / 100
* PENDING 或尚未处理输入 Ktype：60
* 已确认并被引用尺寸组：32 个
* 本轮新增 READY 映射：14 行
* 本轮首次创建尺寸组：8 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4363	4363	Sedan	Leone II	AB	4	EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	HIGH	AB四门四驱轿车。	READY
4364	4364	Sedan	Leone II	AB	4	EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	HIGH	AB四门四驱轿车。	READY
4367	4367	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	HIGH	三门四驱掀背车。	READY
4368	4368	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	HIGH	三门Turismo四驱掀背车。	READY
4370	4370	Wagon	Leone II	AM	5	EU-SUBARU-LEONE-II-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4371	4371	Wagon	Leone II		5	EU-SUBARU-LEONE-II-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Station。	READY
4381	4381	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH	四门四驱轿车。	READY
4383	4383	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH	四门四驱轿车。	READY
4384	4384	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	HIGH	四门Turbo四驱轿车。	READY
4387	4387	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	HIGH	四门Turbo四驱轿车。	READY
4385	4385	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4388	4388	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4390	4390	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Station。	READY
4391	4391	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Turbo Station。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	4250	1620	1410	Automobile-Catalog 1980 Subaru 1800 4WD Sedan	https://www.automobile-catalog.com/car/1980/3206660/subaru_1800_4wd_sedan.html
EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	3980	1620	1415	Automobile-Catalog 1980 Subaru 1800 4WD Hatchback SRX	https://www.automobile-catalog.com/car/1980/3206645/subaru_1800_4wd_hatchback_srx.html
EU-SUBARU-LEONE-II-WAGON-5D-4WD-01	4285	1620	1445	Automobile-Catalog 1981 Subaru 1800 4WD Station Wagon Dual Range	https://www.automobile-catalog.com/car/1981/3208100/subaru_1800_4wd_station_wagon_dual_range.html
EU-SUBARU-LEONE-II-WAGON-5D-SUPER-4WD-01	4285	1620	1485	Automobile-Catalog 1984 Subaru 1800 GLF 4WD Super Station	https://www.automobile-catalog.com/car/1984/3209195/subaru_1800_glf_4wd_station_wagon_super_station_dual_range.html
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425	Automobile-Catalog 1988 Subaru Full Time 4WD 1800 Sedan catalyst	https://www.automobile-catalog.com/car/1988/3216335/subaru_full_time_4wd_1800_sedan_catalyst.html
EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	4370	1660	1400	Automobile-Catalog 1989 Subaru Full Time 4WD 1.8 Turbo Sedan	https://www.automobile-catalog.com/car/1989/3216290/subaru_full_time_4wd_1_8_turbo_4-door_sedan_dual_range.html
EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	4410	1660	1450	Automobile-Catalog 1990 Subaru 4WD 1800 Station Dual Range catalyst	https://www.automobile-catalog.com/car/1990/3216545/subaru_4wd_1800_station_dual_range_catalyst.html
EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	4410	1660	1490	Automobile-Catalog 1984 Subaru 4WD 1.8 GL Super Station	https://www.automobile-catalog.com/car/1984/3214265/subaru_4wd_1_8_gl_station_wagon_dual_range.html
```

## 下一步优先处理

1. 批量闭合 Daihatsu Rocky、Wildcat 与 Feroza 的软顶、硬顶及车身长度分支。
2. 处理 Daihatsu Cuore I–II、Charade I–III 与 Charmant。
3. 处理 Subaru Justy I、Libero，Suzuki Alto I–II 与 Swift I。
4. 消除 Nissan 200SX S14 前期和改款分支的剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/3206660/subaru_1800_4wd_sedan.html?utm_source=chatgpt.com "1980 Subaru 1800 4WD Sedan Specs Review (59 kW / 80 PS / 79 hp) (since October 1980 for Europe South America Asia export)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已消除 Nissan 200SX S14 两条 PENDING：改款前外廓闭合为 `4520×1730×1295 mm`，S14a 改款后因保险杠变化闭合为 `4560×1730×1295 mm`。([汽车目录][1])
* 已闭合 Nissan Kubistar X76 厢式货车、Kia Sorento I facelift 2.5 CRDi 和 Suzuki Alto II SB308。([Anchor Vans][2])
* 本轮未重复核验或输出上一轮已经闭合的尺寸组。

## 当前批次进度

* READY 映射：52 行
* PENDING 映射：0 行
* 已完全闭合输入 Ktype：44 / 100
* 尚未处理输入 Ktype：56
* 已确认并被引用尺寸组：37 个
* 本轮新增或转为 READY 映射：5 行
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4338_prefl	4338	Coupe	200SX S14	S14	2	EU-NISSAN-200SX-S14-COUPE-PREFL-01	HIGH	S14改款前欧洲两门轿跑外廓。	READY
4338_facelift	4338	Coupe	200SX S14 facelift	S14	2	EU-NISSAN-200SX-S14-COUPE-FACELIFT-01	HIGH	S14a改款后欧洲两门轿跑外廓。	READY
4373	4373	Van	Kubistar	X76		EU-NISSAN-KUBISTAR-X76-VAN-01	MEDIUM	X76厢式货车外廓。	READY
4424	4424	Hatchback	Alto II	SB308	3	EU-SUZUKI-ALTO-II-SB308-HATCHBACK-3D-01	HIGH	SB308欧洲三门掀背外廓。	READY
4426	4426	SUV	Sorento I facelift	BL	5	EU-KIA-SORENTO-I-BL-SUV-FACELIFT-01	HIGH	BL改款五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-200SX-S14-COUPE-PREFL-01	4520	1730	1295	Nissan 200 SX 1994 international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Nissan-200-SX-1994-INT.pdf
EU-NISSAN-200SX-S14-COUPE-FACELIFT-01	4560	1730	1295	Automobile-Catalog 1999 Nissan 200SX; Auto-Data Nissan 200 SX S14 2.0 i 16V Turbo	https://www.automobile-catalog.com/make/nissan/200sx_s14/200sx_s14/1999.html;https://www.auto-data.net/en/nissan-200-sx-s14-2.0-i-16v-turbo-200hp-380
EU-NISSAN-KUBISTAR-X76-VAN-01	4035	1672	1825	Anchor Vans Nissan Kubistar specifications	https://www.anchorvans.co.uk/specifications/kubistar
EU-SUZUKI-ALTO-II-SB308-HATCHBACK-3D-01	3300	1420	1340	UltimateSpecs Suzuki Alto 2 specifications	https://www.ultimatespecs.com/car-specs/Suzuki/M972/Alto-2
EU-KIA-SORENTO-I-BL-SUV-FACELIFT-01	4590	1865	1730	Auto-Data Kia Sorento I facelift 2006 2.5 CRDi 170 Hp	https://www.auto-data.net/en/kia-sorento-i-facelift-2006-2.5-crdi-170hp-2661
```

## 下一步优先处理

1. 批量闭合 Daihatsu Rocky、Wildcat 与 Feroza 的软顶、硬顶及改款分支。
2. 处理 Daihatsu Cuore I–II、Charade I–III 与 Charmant。
3. 处理 Subaru Justy I 的改款前后长度、车高及三门/五门分支。
4. 处理 Subaru Libero E10/E12 与 1993 年后 SDX 新车身。
5. 随后闭合剩余 Suzuki Swift I、Daihatsu Charade IV 四驱及其他未处理记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/2180390/nissan_200_sx.html?utm_source=chatgpt.com "1995 Nissan 200SX Specs Review (147 kW / 200 PS / ..."
[2]: https://www.anchorvans.co.uk/specifications/kubistar?utm_source=chatgpt.com "Kubistar, Specifications"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Daihatsu Rocky/Wildcat 的早期窄体软顶、硬顶分支。2.8 D 与 2.8 TD 仅发动机不同，共用对应软顶或硬顶尺寸组：软顶 `3775×1580×1830 mm`，硬顶 `3775×1580×1840 mm`。([汽车目录][1])
* 闭合 1991–1998 年 75 kW Rocky 2.8 TD 的后期宽体软顶与硬顶分支：软顶 `4165×1780×1925 mm`，硬顶 `3840×1690×1850 mm`。([汽车数据][2])
* Feroza Ktype 的时间范围跨越 1993 年外观阶段变化，已按 `prefl` 与 `facelift` 拆分；前期软顶和硬顶均为 `3685×1580×1720 mm`，后期软顶为 `3700×1580×1720 mm`、硬顶为 `3775×1580×1720 mm`。([汽车目录][3])

## 当前批次进度

* READY 映射：68 行
* 已完全闭合输入 Ktype：56 / 100
* PENDING／尚未闭合输入 Ktype：44
* 已确认并被引用尺寸组：45 个
* 本轮新增 READY 映射：16 行
* 本轮首次创建尺寸组：8 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4359	4359	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70早期窄体软顶外廓。	READY
4360	4360	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70早期窄体硬顶外廓。	READY
4361	4361	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70早期窄体硬顶外廓。	READY
4362	4362	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70早期窄体软顶外廓。	READY
4369	4369	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70窄体软顶外廓。	READY
4372	4372	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70窄体硬顶外廓。	READY
4376	4376	SUV	Rocky I	F75	3	EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-WIDE-01	HIGH	F75后期宽体软顶外廓。	READY
4377	4377	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-WIDE-01	HIGH	F70后期宽体硬顶外廓。	READY
4378_prefl	4378	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	MEDIUM	F300前期软顶外廓。	READY
4378_facelift	4378	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	MEDIUM	F300改款后软顶外廓。	READY
4379_prefl	4379	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	MEDIUM	F300前期硬顶外廓。	READY
4379_facelift	4379	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	MEDIUM	F300改款后硬顶外廓。	READY
4380_prefl	4380	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	HIGH	F300前期软顶外廓。	READY
4380_facelift	4380	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	HIGH	F300改款后软顶外廓。	READY
4382_prefl	4382	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	HIGH	F300前期硬顶外廓。	READY
4382_facelift	4382	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	HIGH	F300改款后硬顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	3775	1580	1830	Automobile-Catalog Daihatsu Rocky Fourtrak F70 Soft-top	https://www.automobile-catalog.com/car/1987/562730/daihatsu_rocky_2_8_turbo_diesel_soft-top.html
EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	3775	1580	1840	Automobile-Catalog Daihatsu Rocky Fourtrak F70 Hard-top	https://www.automobile-catalog.com/car/1987/562850/daihatsu_rocky_2_8_turbo_diesel_hard-top.html
EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-WIDE-01	4165	1780	1925	Auto-Data Daihatsu Rocky Soft Top F7 F8 2.8 TD 102 Hp	https://www.auto-data.net/en/daihatsu-rocky-soft-top-f7-f8-2.8-td-102hp-68
EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-WIDE-01	3840	1690	1850	Auto-Data Daihatsu Rocky Hard Top F7 F8 2.8 TD 102 Hp	https://www.auto-data.net/en/daihatsu-rocky-hard-top-f7-f8-2.8-td-102hp-63
EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	3685	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase I Soft-top	https://www.automobile-catalog.com/car/1989/563795/daihatsu_feroza_1_6i_16v_dx_soft-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	3685	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase I Hard-top	https://www.automobile-catalog.com/car/1993/563825/daihatsu_feroza_1_6i_16v_dx_hard-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	3700	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase II Soft-top	https://www.automobile-catalog.com/car/1998/566825/daihatsu_feroza_1_6i_16v_dx_soft-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	3775	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase II Hard-top	https://www.automobile-catalog.com/car/1998/566840/daihatsu_feroza_1_6i_16v_se_hard-top.html
```

## 下一步优先处理

1. 闭合 Daihatsu Cuore I–II、Charade I–III 与 Charmant。
2. 处理 Subaru Justy I 的前期、改款及三门/五门分支。
3. 处理 Subaru Libero E10、E12 和后期高顶车身。
4. 闭合 Suzuki Alto I、Swift I，以及 Charade IV 4WD。
5. 最后处理尚未闭合的 Rocky 2.0、Rocky 2.8 D 跨阶段记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/60200/daihatsu_rocky_2_8_diesel_soft-top.html?utm_source=chatgpt.com "1985 Daihatsu Rocky (Fourtrak) 2.8 Diesel Soft-top (man. 5)"
[2]: https://www.auto-data.net/en/daihatsu-rocky-soft-top-f7-f8-2.8-td-102hp-68?utm_source=chatgpt.com "Daihatsu Rocky Soft Top (F7,F8) 2.8 TD (102 Hp)"
[3]: https://www.automobile-catalog.com/car/1993/563825/daihatsu_feroza_1_6i_16v_dx_hard-top.html?utm_source=chatgpt.com "1993 Daihatsu Feroza (Sportrak) 1.6i 16V DX Hard-top Specs Review (70 kW / 95 PS / 94 hp) (up to mid-year 1993 for Europe export)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 修正上一轮进度口径：尚未处理的 Ktype 必须计入待处理量，不能在仅有显式 PENDING 行为零时写作 `PENDING=0`。
* 闭合 Daihatsu Cuore I 的 L55 0.5 与 L60 0.6 三门、五门分支；四个映射共用同一外廓尺寸组。该代确认同时存在三门和五门车身，外廓为 `3195×1395×1370 mm`。([汽车目录][1])
* 闭合 Daihatsu Cuore II L80 0.8 的三门、五门分支，两个功率版本共用 `3200×1400×1410 mm` 尺寸组。([汽车数据][2])
* 闭合 Charmant II 的部分 1.6 车型；跨 1984 年出口改款的 Ktype `4357` 拆为前期和改款后分支。前期为 `4150×1630×1380 mm`，改款后为 `4200×1620×1380 mm`。([汽车目录][3])

## 当前批次进度

* READY 映射：81 行
* 已完全闭合输入 Ktype：64 / 100
* PENDING／尚未处理输入 Ktype：36
* 已确认并被引用尺寸组：49 个
* 本轮新增 READY 映射：13 行
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4341_3dr	4341	Hatchback	Cuore I	L55	3	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L55三门掀背外廓。	READY
4341_5dr	4341	Hatchback	Cuore I	L55	5	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L55五门掀背外廓。	READY
4342_3dr	4342	Hatchback	Cuore I	L60	3	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L60三门掀背外廓。	READY
4342_5dr	4342	Hatchback	Cuore I	L60	5	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L60五门掀背外廓。	READY
4343_3dr	4343	Hatchback	Cuore II	L80	3	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80三门掀背外廓。	READY
4343_5dr	4343	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80五门掀背外廓。	READY
4345_3dr	4345	Hatchback	Cuore II	L80	3	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80三门掀背外廓。	READY
4345_5dr	4345	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80五门掀背外廓。	READY
4355	4355	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	HIGH	A60改款后四门轿车外廓。	READY
4356	4356	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	HIGH	A60改款后四门轿车外廓。	READY
4357_prefl	4357	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	MEDIUM	A60改款前四门轿车外廓。	READY
4357_facelift	4357	Sedan	Charmant II facelift	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	MEDIUM	A60改款后四门轿车外廓。	READY
4358	4358	Sedan	Charmant II	A45	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	HIGH	A45改款前四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	3195	1395	1370	Automobile-Catalog 1980 Daihatsu Cuore L55/L60	https://www.automobile-catalog.com/make/daihatsu/cuore_1gen/cuore_1gen_hatchback/1980.html
EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	3200	1400	1410	UltimateSpecs Daihatsu Cuore II L70 850	https://www.ultimatespecs.com/car-specs/Daihatsu/4829/Daihatsu-Cuore-II-%28L70%29-850.html
EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	4150	1630	1380	Automobile-Catalog 1983 Daihatsu Charmant 1600 LE	https://www.automobile-catalog.com/car/1983/41480/daihatsu_charmant_1600_le.html
EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	4200	1620	1380	Automobile-Catalog 1986 Daihatsu Charmant 1600 LGX	https://www.automobile-catalog.com/car/1986/561725/daihatsu_charmant_1600_lgx.html
```

## 下一步优先处理

1. 闭合 Charade I 的三门、五门及 1980 年改款外廓。
2. 批量处理 Charade II、Charade III 的改款前后和三门、五门分支。
3. 补齐 Charmant 1.3 跨改款记录。
4. 处理 Subaru Justy I、Libero，以及 Suzuki Alto I、Swift I。
5. 闭合 Rocky 2.0、跨阶段 Rocky 2.8 D 和 Charade IV 4WD。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/daihatsu/cuore_1gen/cuore_1gen_hatchback/1980.html?utm_source=chatgpt.com "1980 Daihatsu Cuore 1gen (L55) full range specs"
[2]: https://www.auto-data.net/en/daihatsu-cuore-l80-l81-0.8-l80-44hp-56?utm_source=chatgpt.com "Daihatsu Cuore (L80,L81) 0.8 (L80) (44 Hp) /Hatchback 1985"
[3]: https://www.automobile-catalog.com/car/1983/41480/daihatsu_charmant_1600_le.html?utm_source=chatgpt.com "1983 Daihatsu Charmant 1600 LE Specs Review (55 kW ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 闭合 Daihatsu Charade III 的标准五门、三门 Turbo、三门 GTi 和五门 4WD 外廓。
* 标准五门汽油、柴油及 1.3 i 版本共用 `3610×1600×1385 mm` 外廓；发动机和燃料差异未重复建组。([汽车目录][1])
* 三门 Turbo 为 `3610×1600×1385 mm`，三门 GTi 因宽体外廓独立为 `3610×1615×1385 mm`。([汽车目录][2])
* 五门 1.3 i 4WD 因车宽和车高变化独立为 `3610×1615×1400 mm`。([汽车目录][3])
* Charmant 1.3 直接关联上一轮已经创建的改款前尺寸组，未重复输出尺寸来源。([汽车目录][4])

## 2. 当前批次进度

* READY 映射：91 行
* 已完全闭合输入 Ktype：74 / 100
* PENDING／尚未处理输入 Ktype：26
* 已确认并被引用尺寸组：53 个
* 本轮新增 READY 映射：10 行
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4354	4354	Sedan	Charmant II	A45	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	HIGH	A45改款前四门轿车外廓。	READY
4386	4386	Hatchback	Charade III	G100	3	EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-TURBO-01	HIGH	G100三门Turbo外廓。	READY
4389	4389	Hatchback	Charade III	G101	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G101五门柴油掀背外廓。	READY
4392	4392	Hatchback	Charade III	G101	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G101五门涡轮柴油掀背外廓。	READY
4393	4393	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4394	4394	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4396	4396	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4398	4398	Hatchback	Charade III	G100	3	EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-GTI-01	HIGH	G100三门GTi宽体外廓。	READY
4400	4400	Hatchback	Charade III	G102	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G102前驱五门掀背外廓。	READY
4401	4401	Hatchback	Charade III	G102	5	EU-DAIHATSU-CHARADE-III-G102-HATCHBACK-5D-4WD-01	HIGH	G102五门四驱增高外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-TURBO-01	3610	1600	1385	Automobile-Catalog 1988 Daihatsu Charade Turbo Europe export	https://www.automobile-catalog.com/car/1988/57815/daihatsu_charade_turbo.html
EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	3610	1600	1385	Automobile-Catalog 1987 Daihatsu Charade TS Europe export; Automobile-Catalog 1990 Daihatsu Charade Turbo Diesel Europe export; Automobile-Catalog 1989 Daihatsu Charade 1.3i TX	https://www.automobile-catalog.com/car/1987/56165/daihatsu_charade_ts.html;https://www.automobile-catalog.com/car/1990/57800/daihatsu_charade_tx_turbo_diesel.html;https://www.automobile-catalog.com/car/1989/563240/daihatsu_charade_1_3i_tx.html
EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-GTI-01	3610	1615	1385	Automobile-Catalog 1990 Daihatsu Charade GTti Europe export	https://www.automobile-catalog.com/car/1990/56180/daihatsu_charade_gtti.html
EU-DAIHATSU-CHARADE-III-G102-HATCHBACK-5D-4WD-01	3610	1615	1400	Automobile-Catalog 1989 Daihatsu Charade 1.3i TXF 4WD	https://www.automobile-catalog.com/car/1989/563270/daihatsu_charade_1_3i_txf_4wd.html
```

## 5. 下一步优先处理

1. 闭合 Charade I 的改款前后及三门、五门分支。
2. 闭合 Charade II 的前期、改款后、Turbo 与柴油外廓。
3. 处理 Subaru Justy I 的三门、五门及改款分支。
4. 处理 Subaru Libero E10、E12 与后期车身。
5. 补齐 Rocky 2.0、跨阶段 Rocky 2.8 D、Suzuki Alto I 和 Swift I。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/563015/daihatsu_charade_tg.html?utm_source=chatgpt.com "1987 Daihatsu Charade TG Specs Review (38 kW / 52 PS / 51 hp) (since mid-year 1987 for Europe export)"
[2]: https://www.automobile-catalog.com/car/1988/57815/daihatsu_charade_turbo.html?utm_source=chatgpt.com "1988 Daihatsu Charade Turbo Specs Review (50 kW / 68 PS / 67 hp) (for Europe export)"
[3]: https://www.automobile-catalog.com/car/1989/563270/daihatsu_charade_1_3i_txf_4wd.html?utm_source=chatgpt.com "1989 Daihatsu Charade 1.3i TXF 4WD Specs Review (66 ..."
[4]: https://www.automobile-catalog.com/car/1982/561680/daihatsu_charmant_1300_lc.html?utm_source=chatgpt.com "1982 Daihatsu Charmant 1300 LC Specs Review (48 kW / 65 PS / 64 hp) (since mid-year 1982 for Europe export)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 闭合 Daihatsu Charade I 的 G10 前期与改款后外廓，并按三门 Runabout、五门 Hatchback 拆分。
* Ktype `4348` 跨越 1980 年末改款，拆为前期三门、前期五门、改款后三门、改款后五门四个物理分支。
* 前期三门为 `3525×1515×1355 mm`，前期五门为 `3485×1515×1360 mm`；改款后三门为 `3510×1520×1345 mm`，改款后五门为 `3490×1510×1345 mm`。([汽车目录][1])
* Ktype `4350` 仅覆盖改款后阶段，直接关联已在本轮创建的三门、五门尺寸组。

## 2. 当前批次进度

* READY 映射：97 行
* 已完全闭合输入 Ktype：76 / 100
* PENDING／尚未处理输入 Ktype：24
* 已确认并被引用尺寸组：57 个
* 本轮新增 READY 映射：6 行
* 本轮首次创建尺寸组：4 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4348_3dr_prefl	4348	Hatchback	Charade I	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-PREFL-01	HIGH	G10前期三门Runabout外廓。	READY
4348_5dr_prefl	4348	Hatchback	Charade I	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-PREFL-01	HIGH	G10前期五门掀背外廓。	READY
4348_3dr_facelift	4348	Hatchback	Charade I facelift	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	HIGH	G10改款后三门Runabout外廓。	READY
4348_5dr_facelift	4348	Hatchback	Charade I facelift	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	HIGH	G10改款后五门掀背外廓。	READY
4350_3dr	4350	Hatchback	Charade I facelift	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	HIGH	G10改款后三门Runabout外廓。	READY
4350_5dr	4350	Hatchback	Charade I facelift	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	HIGH	G10改款后五门掀背外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-PREFL-01	3525	1515	1355	Automobile-Catalog 1978 Daihatsu Charade Runabout XG Europe export	https://www.automobile-catalog.com/car/1978/1867070/daihatsu_charade_runabout.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-PREFL-01	3485	1515	1360	Automobile-Catalog 1977 Daihatsu Charade XG-5 Europe export	https://www.automobile-catalog.com/car/1977/31760/daihatsu_charade_xg-5.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	3510	1520	1345	Automobile-Catalog 1981 Daihatsu Charade Runabout XG Europe export	https://www.automobile-catalog.com/car/1981/1867055/daihatsu_charade_runabout_xg.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	3490	1510	1345	Automobile-Catalog 1981 Daihatsu Charade XG-5 Europe export	https://www.automobile-catalog.com/car/1981/561200/daihatsu_charade_xg-5.html
```

## 5. 下一步优先处理

1. 闭合 Charade II G11 的前期、改款后、三门、五门和 Turbo 外廓。
2. 处理 Subaru Justy I 的改款前后及三门、五门分支。
3. 处理 Subaru Libero E10、E12 与后期车身。
4. 补齐 Rocky 2.0、跨阶段 Rocky 2.8 D、Suzuki Alto I 与 Swift I。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/1867070/daihatsu_charade_runabout.html?utm_source=chatgpt.com "1978 Daihatsu Charade Runabout XG Specs Review (37 kW / 50 PS / 50 hp) (since September 1978 for Europe export)"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 闭合 Daihatsu Charade II G11/G30 的改款前后外廓：改款前为 `3550×1550×1395 mm`，改款后为 `3595×1550×1395 mm`；同阶段柴油、涡轮柴油、汽油和 Turbo 共用车身组。([汽车目录档案][1])
* 闭合 Subaru Libero 的 E10、E12 低顶/高顶及 1993 年后第二代车身。E10 为 `3410×1430×1870/1900 mm`，E12 为 `3425×1430×1870/1900 mm`，第二代为 `3525×1415×1925 mm`。([汽车目录][2])
* 闭合 Suzuki Alto I 0.8 五门外廓，以及 Swift I 的三门短车身和五门长车身分支。([汽车数据][3])

## 2. 当前批次进度

* READY 映射：118 行
* 显式 PENDING 映射：0 行
* 已完全闭合输入 Ktype：88 / 100
* 尚未处理输入 Ktype：12
* 当前有效待处理量：12
* 已确认并被引用尺寸组：67 个
* 本轮新增 READY 映射：21 行
* 本轮首次创建尺寸组：10 个
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4346_prefl	4346	Hatchback	Charade II	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G30改款前外廓分支。	READY
4346_facelift	4346	Hatchback	Charade II facelift	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G30改款后外廓分支。	READY
4347	4347	Hatchback	Charade II facelift	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	HIGH	G30改款后涡轮柴油外廓。	READY
4352_prefl	4352	Hatchback	Charade II	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G11改款前外廓分支。	READY
4352_facelift	4352	Hatchback	Charade II facelift	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G11改款后外廓分支。	READY
4353_prefl	4353	Hatchback	Charade II	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G11改款前Turbo外廓。	READY
4353_facelift	4353	Hatchback	Charade II facelift	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G11改款后Turbo外廓。	READY
4415_lowroof	4415	MPV	Libero I	E10	5	EU-SUBARU-LIBERO-I-E10-MPV-LOWROOF-01	MEDIUM	E10五门低顶车身。	READY
4415_highroof	4415	MPV	Libero I	E10	5	EU-SUBARU-LIBERO-I-E10-MPV-HIGHROOF-01	MEDIUM	E10五门高顶车身。	READY
4416_e12_lowroof	4416	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-LOWROOF-01	MEDIUM	E12五门低顶车身。	READY
4416_e12_highroof	4416	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	MEDIUM	E12五门高顶车身。	READY
4416_gen2	4416	MPV	Libero II		5	EU-SUBARU-LIBERO-II-MPV-01	MEDIUM	1993年后第二代五门车身。	READY
4417	4417	Hatchback	Alto I		5	EU-SUZUKI-ALTO-I-HATCHBACK-5D-01	HIGH	欧洲0.8五门掀背外廓。	READY
4419_e12_highroof	4419	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	MEDIUM	E12喷射型高顶车身。	READY
4419_gen2	4419	MPV	Libero II		5	EU-SUBARU-LIBERO-II-MPV-01	MEDIUM	1993年后第二代五门车身。	READY
4431	4431	Hatchback	Swift I	SA310	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA310三门1.0外廓。	READY
4433	4433	Hatchback	Swift I	SA310	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA310三门Turbo外廓。	READY
4436_3dr	4436	Hatchback	Swift I	SA413	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA413三门GTi外廓。	READY
4436_5dr	4436	Hatchback	Swift I	SA413	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	SA413五门GXi外廓。	READY
4437_3dr	4437	Hatchback	Swift I	SA413	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	SA413三门1.3外廓。	READY
4437_5dr	4437	Hatchback	Swift I	SA413	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	SA413五门1.3外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	3550	1550	1395	Daihatsu Charade 1984 official-market brochure	https://autocatalogarchive.com/wp-content/uploads/2022/04/Daihatsu-Charade-1984-NZ.pdf
EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	3595	1550	1395	Automobile-Catalog 1987 Daihatsu Charade Turbo	https://www.automobile-catalog.com/car/1987/561935/daihatsu_charade_turbo.html
EU-SUBARU-LIBERO-I-E10-MPV-LOWROOF-01	3410	1430	1870	Automobile-Catalog 1984 Subaru Domingo 4WD GS	https://www.automobile-catalog.com/car/1984/3223895/subaru_domingo_4wd_gs.html
EU-SUBARU-LIBERO-I-E10-MPV-HIGHROOF-01	3410	1430	1900	Automobile-Catalog 1984 Subaru Libero E10 Wagon 4WD	https://www.automobile-catalog.com/car/1984/48365/subaru_e-10.html
EU-SUBARU-LIBERO-I-E12-MPV-LOWROOF-01	3425	1430	1870	Automobile-Catalog 1991 Subaru Domingo Full Time 4WD GS	https://www.automobile-catalog.com/car/1991/3224030/subaru_domingo_full_time_4wd_gs.html
EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	3425	1430	1900	Automobile-Catalog 1991 Subaru Domingo Full Time 4WD GX	https://www.automobile-catalog.com/car/1991/3224180/subaru_domingo_full_time_4wd_gx.html
EU-SUBARU-LIBERO-II-MPV-01	3525	1415	1925	Automobile-Catalog 1997 Subaru Libero 1.2 Wagon 4WD SDX SR Special	https://www.automobile-catalog.com/car/1997/3224735/subaru_libero_1_2_wagon_4wd_sdx_sr_special.html
EU-SUZUKI-ALTO-I-HATCHBACK-5D-01	3195	1395	1335	Automobile-Catalog 1979 Suzuki Alto MX	https://www.automobile-catalog.com/car/1979/3324710/suzuki_alto_mx.html
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	3585	1530	1350	Automobile-Catalog 1984 Suzuki Swift 1.0 GA	https://www.automobile-catalog.com/car/1984/48485/suzuki_swift_1_0.html
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	3770	1545	1350	Automobile-Catalog 1987 Suzuki Swift 1.3 GLX 5-door	https://www.automobile-catalog.com/car/1987/3327875/suzuki_swift_1_3_glx_5-door.html
```

([汽车目录档案][1])

## 5. 下一步优先处理

1. 闭合 Ktype `4365`、`4366` 的 Rocky 2.0 软顶与硬顶外廓。
2. 拆分并闭合 Ktype `4374`、`4375` 跨阶段的 Rocky 2.8 D 窄体、后期宽体分支。
3. 集中处理最后 8 个 Subaru Justy I Ktype，统一确认 J10/J12、三门/五门、低顶/高顶及 1989 年改款边界。
4. 待剩余 12 个 Ktype 全部闭合后，下一轮直接执行机械收尾并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2022/04/Daihatsu-Charade-1984-NZ.pdf?utm_source=chatgpt.com "Daihatsu Charade (1983-1987)"
[2]: https://www.automobile-catalog.com/car/1984/48365/subaru_e-10.html?utm_source=chatgpt.com "1984 Subaru (Libero) E10 Wagon 4WD Specs Review ..."
[3]: https://www.auto-data.net/en/suzuki-alto-i-0.8-39hp-16447 "Suzuki Alto I 0.8 (39 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4201-4300_ktype_dimension_mapping_final.tsv
- all_4201-4300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 最后 12 个 Ktype 已全部闭合，当前 100 个输入 Ktype 均已覆盖。
* Subaru Justy I 的 1000/1200、前驱/四驱版本按三门和五门建立映射，共用已确认的 `3695×1535×1420 mm` 物理外廓。([汽车数据][1])
* Rocky 2.0 软顶、硬顶复用现有窄体组；跨阶段的 Rocky 2.8 D 已拆分为早期窄体、后期长轴软顶和宽体硬顶分支。([汽车目录][2])
* 修正 Ktype `4349`：G 55 AMG 不再复用已有高度 `1951 mm` 的尺寸组，改为新建 `EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02`，尺寸为 `4662×1760×1931 mm`，未覆盖累计表中的既有组。([汽车数据][3])
* 已完成机械校验：映射表 10 列、尺寸组表 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；所有引用闭合；无孤立尺寸组；尺寸、来源及 URL 均非空。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：140 行
* PENDING 映射：0 行
* DIMENSION_GROUP：69 行
* 映射引用闭合：通过
* 下载文件生成：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4338_prefl	4338	Coupe	200SX S14	S14	2	EU-NISSAN-200SX-S14-COUPE-PREFL-01	HIGH	S14改款前欧洲两门轿跑外廓。	READY
4338_facelift	4338	Coupe	200SX S14 facelift	S14	2	EU-NISSAN-200SX-S14-COUPE-FACELIFT-01	HIGH	S14a改款后欧洲两门轿跑外廓。	READY
4339	4339	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4340	4340	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓。	READY
4341_3dr	4341	Hatchback	Cuore I	L55	3	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L55三门掀背外廓。	READY
4341_5dr	4341	Hatchback	Cuore I	L55	5	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L55五门掀背外廓。	READY
4342_3dr	4342	Hatchback	Cuore I	L60	3	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L60三门掀背外廓。	READY
4342_5dr	4342	Hatchback	Cuore I	L60	5	EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	HIGH	L60五门掀背外廓。	READY
4343_3dr	4343	Hatchback	Cuore II	L80	3	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80三门掀背外廓。	READY
4343_5dr	4343	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80五门掀背外廓。	READY
4344	4344	Hatchback	Cuore III	L201	3	EU-DAIHATSU-CUORE-III-L201-HATCHBACK-3D-01	HIGH	L201三门掀背外廓。	READY
4345_3dr	4345	Hatchback	Cuore II	L80	3	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80三门掀背外廓。	READY
4345_5dr	4345	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM	L80五门掀背外廓。	READY
4346_prefl	4346	Hatchback	Charade II	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G30改款前外廓分支。	READY
4346_facelift	4346	Hatchback	Charade II facelift	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G30改款后外廓分支。	READY
4347	4347	Hatchback	Charade II facelift	G30		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	HIGH	G30改款后涡轮柴油外廓。	READY
4348_3dr_prefl	4348	Hatchback	Charade I	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-PREFL-01	HIGH	G10前期三门Runabout外廓。	READY
4348_5dr_prefl	4348	Hatchback	Charade I	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-PREFL-01	HIGH	G10前期五门掀背外廓。	READY
4348_3dr_facelift	4348	Hatchback	Charade I facelift	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	HIGH	G10改款后三门Runabout外廓。	READY
4348_5dr_facelift	4348	Hatchback	Charade I facelift	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	HIGH	G10改款后五门掀背外廓。	READY
4349	4349	SUV	G-Class W463 facelift	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	HIGH	W463改款五门长轴AMG外廓。	READY
4350_3dr	4350	Hatchback	Charade I facelift	G10	3	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	HIGH	G10改款后三门Runabout外廓。	READY
4350_5dr	4350	Hatchback	Charade I facelift	G10	5	EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	HIGH	G10改款后五门掀背外廓。	READY
4351_prefl	4351	Sedan	Logan I	L90	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	L90四门轿车，按2008改款前外廓拆分。	READY
4351_facelift	4351	Sedan	Logan I facelift	L90	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	L90四门轿车，按2008改款后外廓拆分。	READY
4352_prefl	4352	Hatchback	Charade II	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G11改款前外廓分支。	READY
4352_facelift	4352	Hatchback	Charade II facelift	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G11改款后外廓分支。	READY
4353_prefl	4353	Hatchback	Charade II	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	MEDIUM	G11改款前Turbo外廓分支。	READY
4353_facelift	4353	Hatchback	Charade II facelift	G11		EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	MEDIUM	G11改款后Turbo外廓分支。	READY
4354	4354	Sedan	Charmant II	A45	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	HIGH	A45改款前四门轿车外廓。	READY
4355	4355	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	HIGH	A60改款后四门轿车外廓。	READY
4356	4356	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	HIGH	A60改款后四门轿车外廓。	READY
4357_prefl	4357	Sedan	Charmant II	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	MEDIUM	A60改款前四门轿车外廓。	READY
4357_facelift	4357	Sedan	Charmant II facelift	A60	4	EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	MEDIUM	A60改款后四门轿车外廓。	READY
4358	4358	Sedan	Charmant II	A45	4	EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	HIGH	A45改款前四门轿车外廓。	READY
4359	4359	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70早期窄体软顶外廓。	READY
4360	4360	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70早期窄体硬顶外廓。	READY
4361	4361	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70早期窄体硬顶外廓。	READY
4362	4362	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70早期窄体软顶外廓。	READY
4363	4363	Sedan	Leone II	AB	4	EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	HIGH	AB四门四驱轿车。	READY
4364	4364	Sedan	Leone II	AB	4	EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	HIGH	AB四门四驱轿车。	READY
4365	4365	SUV	Rocky I	F80	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F80两门软顶与早期窄体软顶共用外廓。	READY
4366	4366	SUV	Rocky I	F80	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F80三门硬顶与早期窄体硬顶共用外廓。	READY
4367	4367	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	HIGH	三门四驱掀背车。	READY
4368	4368	Hatchback	Leone II		3	EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	HIGH	三门Turismo四驱掀背车。	READY
4369	4369	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	HIGH	F70窄体软顶外廓。	READY
4370	4370	Wagon	Leone II	AM	5	EU-SUBARU-LEONE-II-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4371	4371	Wagon	Leone II		5	EU-SUBARU-LEONE-II-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Station。	READY
4372	4372	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	HIGH	F70窄体硬顶外廓。	READY
4373	4373	Van	Kubistar	X76		EU-NISSAN-KUBISTAR-X76-VAN-01	MEDIUM	X76厢式货车外廓。	READY
4374_narrow	4374	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	MEDIUM	1985–1986早期窄体软顶分支。	READY
4374_lwb	4374	SUV	Rocky I	F75	3	EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-LWB-01	MEDIUM	1987–1998长轴软顶分支。	READY
4375_narrow	4375	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	MEDIUM	1985–1986早期窄体硬顶分支。	READY
4375_wide	4375	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-WIDE-01	MEDIUM	1987–1998后期宽体硬顶分支。	READY
4376	4376	SUV	Rocky I	F75	3	EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-WIDE-01	HIGH	F75后期宽体软顶外廓。	READY
4377	4377	SUV	Rocky I	F70	3	EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-WIDE-01	HIGH	F70后期宽体硬顶外廓。	READY
4378_prefl	4378	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	MEDIUM	F300前期软顶外廓。	READY
4378_facelift	4378	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	MEDIUM	F300改款后软顶外廓。	READY
4379_prefl	4379	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	MEDIUM	F300前期硬顶外廓。	READY
4379_facelift	4379	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	MEDIUM	F300改款后硬顶外廓。	READY
4380_prefl	4380	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	HIGH	F300前期软顶外廓。	READY
4380_facelift	4380	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	HIGH	F300改款后软顶外廓。	READY
4381	4381	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH	四门四驱轿车。	READY
4382_prefl	4382	SUV	Feroza I	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	HIGH	F300前期硬顶外廓。	READY
4382_facelift	4382	SUV	Feroza I facelift	F300	3	EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	HIGH	F300改款后硬顶外廓。	READY
4383	4383	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	HIGH	四门四驱轿车。	READY
4384	4384	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	HIGH	四门Turbo四驱轿车。	READY
4385	4385	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4386	4386	Hatchback	Charade III	G100	3	EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-TURBO-01	HIGH	G100三门Turbo外廓。	READY
4387	4387	Sedan	Leone III		4	EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	HIGH	四门Turbo四驱轿车。	READY
4388	4388	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	HIGH	五门标准顶四驱旅行车。	READY
4389	4389	Hatchback	Charade III	G101	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G101五门柴油掀背外廓。	READY
4390	4390	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Station。	READY
4391	4391	Wagon	Leone III		5	EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	HIGH	五门高顶Super Turbo Station。	READY
4392	4392	Hatchback	Charade III	G101	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G101五门涡轮柴油掀背外廓。	READY
4393	4393	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4394	4394	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4395	4395	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	HIGH	XT两门轿跑外廓。	READY
4396	4396	Hatchback	Charade III	G100	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G100五门掀背外廓。	READY
4397	4397	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	MEDIUM	同代两门轿跑外廓。	READY
4398	4398	Hatchback	Charade III	G100	3	EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-GTI-01	HIGH	G100三门GTi宽体外廓。	READY
4399	4399	Coupe	XT		2	EU-SUBARU-XT-COUPE-2D-01	HIGH	XT两门轿跑外廓。	READY
4400	4400	Hatchback	Charade III	G102	5	EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	HIGH	G102前驱五门掀背外廓。	READY
4401	4401	Hatchback	Charade III	G102	5	EU-DAIHATSU-CHARADE-III-G102-HATCHBACK-5D-4WD-01	HIGH	G102五门四驱增高外廓。	READY
4402	4402	Hatchback	Applause I	A101	5	EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	HIGH	A101前驱五门掀背外廓。	READY
4403_3dr	4403	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000前期前驱三门外廓。	READY
4403_5dr	4403	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000前期前驱五门外廓。	READY
4404	4404	Hatchback	Applause I	A111	5	EU-DAIHATSU-APPLAUSE-I-A111-HATCHBACK-4WD-01	HIGH	A111四驱五门外廓。	READY
4405_3dr	4405	Hatchback	Charade IV	G200	3	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	MEDIUM	G200掀背车按三门边界拆分。	READY
4405_5dr	4405	Hatchback	Charade IV	G200	5	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	MEDIUM	G200掀背车按五门边界拆分。	READY
4406	4406	Hatchback	Charade IV	G200	3	EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-GTI-01	HIGH	G200三门GTi外廓。	READY
4407_3dr	4407	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000四驱三门外廓。	READY
4407_5dr	4407	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000四驱五门外廓。	READY
4408	4408	Sedan	Charade IV	G200	4	EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	HIGH	G200四门轿车外廓。	READY
4409_3dr	4409	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000后期前驱三门外廓。	READY
4409_5dr	4409	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000后期前驱五门外廓。	READY
4410_3dr	4410	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000后期四驱三门外廓。	READY
4410_5dr	4410	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1000后期四驱五门外廓。	READY
4411_3dr	4411	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200前驱三门外廓。	READY
4411_5dr	4411	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200前驱五门外廓。	READY
4412_3dr	4412	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200四驱三门外廓。	READY
4412_5dr	4412	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200四驱五门外廓。	READY
4413_3dr	4413	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200后期四驱三门外廓。	READY
4413_5dr	4413	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200后期四驱五门外廓。	READY
4414_3dr	4414	Hatchback	Justy I	KAD	3	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200四驱三门外廓。	READY
4414_5dr	4414	Hatchback	Justy I	KAD	5	EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	MEDIUM	1200四驱五门外廓。	READY
4415_lowroof	4415	MPV	Libero I	E10	5	EU-SUBARU-LIBERO-I-E10-MPV-LOWROOF-01	MEDIUM	E10五门低顶车身。	READY
4415_highroof	4415	MPV	Libero I	E10	5	EU-SUBARU-LIBERO-I-E10-MPV-HIGHROOF-01	MEDIUM	E10五门高顶车身。	READY
4416_e12_lowroof	4416	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-LOWROOF-01	MEDIUM	E12五门低顶车身。	READY
4416_e12_highroof	4416	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	MEDIUM	E12五门高顶车身。	READY
4416_gen2	4416	MPV	Libero II		5	EU-SUBARU-LIBERO-II-MPV-01	MEDIUM	1993年后第二代五门车身。	READY
4417	4417	Hatchback	Alto I		5	EU-SUZUKI-ALTO-I-HATCHBACK-5D-01	HIGH	欧洲0.8五门掀背外廓。	READY
4418_prefl	4418	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	MEDIUM	F10改款前四门轿车外廓。	READY
4418_facelift	4418	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	MEDIUM	F10 LCI改款后四门轿车外廓。	READY
4419_e12_highroof	4419	MPV	Libero I	E12	5	EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	MEDIUM	E12喷射型高顶车身。	READY
4419_gen2	4419	MPV	Libero II		5	EU-SUBARU-LIBERO-II-MPV-01	MEDIUM	1993年后第二代五门车身。	READY
4420_prefl	4420	Sedan	Legacy I	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	HIGH	跨1991改款，改款前外廓。	READY
4420_facelift	4420	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	HIGH	跨1991改款，改款后1800 AWD外廓。	READY
4421	4421	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-2000-01	HIGH	改款后2000 AWD外廓。	READY
4422_prefl	4422	Sedan	Legacy I	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	HIGH	跨1991改款，改款前外廓。	READY
4422_facelift	4422	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	HIGH	跨1991改款，改款后2200 AWD外廓。	READY
4423	4423	Sedan	Legacy I facelift	BC	4	EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-TURBO-01	MEDIUM	改款后Turbo轿车外廓。	READY
4424	4424	Hatchback	Alto II	SB308	3	EU-SUZUKI-ALTO-II-SB308-HATCHBACK-3D-01	HIGH	SB308欧洲三门掀背外廓。	READY
4425_prefl	4425	Wagon	Legacy I	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	HIGH	跨1991改款，改款前旅行车外廓。	READY
4425_facelift	4425	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	跨1991改款，改款后旅行车外廓。	READY
4426	4426	SUV	Sorento I facelift	BL	5	EU-KIA-SORENTO-I-BL-SUV-FACELIFT-01	HIGH	BL改款五门SUV外廓。	READY
4427	4427	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
4428	4428	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-TURBO-01	HIGH	改款后Turbo旅行车外廓。	READY
4429_prefl	4429	Wagon	Legacy I	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	HIGH	跨1991改款，改款前旅行车外廓。	READY
4429_facelift	4429	Wagon	Legacy I facelift	BJF	5	EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	HIGH	跨1991改款，改款后旅行车外廓。	READY
4430	4430	Coupe	SVX	CXW	2	EU-SUBARU-SVX-CX-COUPE-2D-01	HIGH	CXW两门轿跑外廓。	READY
4431	4431	Hatchback	Swift I	SA310	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA310三门1.0外廓。	READY
4432	4432	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门轿车外廓。	READY
4433	4433	Hatchback	Swift I	SA310	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA310三门Turbo外廓。	READY
4434	4434	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门轿车外廓。	READY
4435	4435	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	HIGH	GF五门1.6 AWD旅行车外廓。	READY
4436_3dr	4436	Hatchback	Swift I	SA413	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	HIGH	SA413三门GTi外廓。	READY
4436_5dr	4436	Hatchback	Swift I	SA413	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	SA413五门GXi外廓。	READY
4437_3dr	4437	Hatchback	Swift I	SA413	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	SA413三门1.3外廓。	READY
4437_5dr	4437	Hatchback	Swift I	SA413	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	SA413五门1.3外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4201-4300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-200SX-S14-COUPE-PREFL-01	4520	1730	1295	Nissan 200 SX 1994 international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Nissan-200-SX-1994-INT.pdf
EU-NISSAN-200SX-S14-COUPE-FACELIFT-01	4560	1730	1295	Automobile-Catalog 1999 Nissan 200SX; Auto-Data Nissan 200 SX S14 2.0 i 16V Turbo	https://www.automobile-catalog.com/make/nissan/200sx_s14/200sx_s14/1999.html;https://www.auto-data.net/en/nissan-200-sx-s14-2.0-i-16v-turbo-200hp-380
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390	Auto-Data Nissan Primera P10 2.0 i 125 Hp	https://www.auto-data.net/en/nissan-primera-p10-2.0-i-125hp-640
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390	Auto-Data Nissan Primera Hatch P10 2.0 i 125 Hp	https://www.auto-data.net/en/nissan-primera-hatch-p10-2.0-i-125hp-646
EU-DAIHATSU-CUORE-I-L55-L60-HATCHBACK-01	3195	1395	1370	Automobile-Catalog 1980 Daihatsu Cuore L55/L60	https://www.automobile-catalog.com/make/daihatsu/cuore_1gen/cuore_1gen_hatchback/1980.html
EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	3200	1400	1410	UltimateSpecs Daihatsu Cuore II L70 850	https://www.ultimatespecs.com/car-specs/Daihatsu/4829/Daihatsu-Cuore-II-%28L70%29-850.html
EU-DAIHATSU-CUORE-III-L201-HATCHBACK-3D-01	3295	1395	1410	Auto-Data Daihatsu Cuore L201 0.8 (41 Hp)	https://www.auto-data.net/en/daihatsu-cuore-l201-0.8-41hp-54
EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-PREFL-01	3550	1550	1395	Daihatsu Charade 1984 official-market brochure	https://autocatalogarchive.com/wp-content/uploads/2022/04/Daihatsu-Charade-1984-NZ.pdf
EU-DAIHATSU-CHARADE-II-G11-G30-HATCHBACK-FACELIFT-01	3595	1550	1395	Automobile-Catalog 1987 Daihatsu Charade Turbo	https://www.automobile-catalog.com/car/1987/561935/daihatsu_charade_turbo.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-PREFL-01	3525	1515	1355	Automobile-Catalog 1978 Daihatsu Charade Runabout XG Europe export	https://www.automobile-catalog.com/car/1978/1867070/daihatsu_charade_runabout.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-PREFL-01	3485	1515	1360	Automobile-Catalog 1977 Daihatsu Charade XG-5 Europe export	https://www.automobile-catalog.com/car/1977/31760/daihatsu_charade_xg-5.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-3D-FACELIFT-01	3510	1520	1345	Automobile-Catalog 1981 Daihatsu Charade Runabout XG Europe export	https://www.automobile-catalog.com/car/1981/1867055/daihatsu_charade_runabout_xg.html
EU-DAIHATSU-CHARADE-I-G10-HATCHBACK-5D-FACELIFT-01	3490	1510	1345	Automobile-Catalog 1981 Daihatsu Charade XG-5 Europe export	https://www.automobile-catalog.com/car/1981/561200/daihatsu_charade_xg-5.html
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931	Auto-Data Mercedes-Benz G-class Long W463 facelift 2008 AMG G 55	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2008-amg-g-55-v8-kompressor-507hp-4matic-7g-tronic-42526
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525	Auto-Data Dacia Logan I 1.4 i (75 Hp)	https://www.auto-data.net/en/dacia-logan-i-1.4-i-75hp-15891
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525	Auto-Data Dacia Logan I facelift 2008 1.4 MPI (75 Hp)	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.4-mpi-75hp-43236
EU-DAIHATSU-CHARMANT-II-SEDAN-PREFL-01	4150	1630	1380	Automobile-Catalog 1983 Daihatsu Charmant 1600 LE	https://www.automobile-catalog.com/car/1983/41480/daihatsu_charmant_1600_le.html
EU-DAIHATSU-CHARMANT-II-SEDAN-FACELIFT-01	4200	1620	1380	Automobile-Catalog 1986 Daihatsu Charmant 1600 LGX	https://www.automobile-catalog.com/car/1986/561725/daihatsu_charmant_1600_lgx.html
EU-DAIHATSU-ROCKY-I-F70-SUV-SOFTTOP-NARROW-01	3775	1580	1830	Automobile-Catalog Daihatsu Rocky Fourtrak F70 Soft-top	https://www.automobile-catalog.com/car/1987/562730/daihatsu_rocky_2_8_turbo_diesel_soft-top.html
EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-NARROW-01	3775	1580	1840	Automobile-Catalog Daihatsu Rocky Fourtrak F70 Hard-top	https://www.automobile-catalog.com/car/1987/562850/daihatsu_rocky_2_8_turbo_diesel_hard-top.html
EU-SUBARU-LEONE-II-AB-SEDAN-4WD-01	4250	1620	1410	Automobile-Catalog 1980 Subaru 1800 4WD Sedan	https://www.automobile-catalog.com/car/1980/3206660/subaru_1800_4wd_sedan.html
EU-SUBARU-LEONE-II-HATCHBACK-3D-4WD-01	3980	1620	1415	Automobile-Catalog 1980 Subaru 1800 4WD Hatchback SRX	https://www.automobile-catalog.com/car/1980/3206645/subaru_1800_4wd_hatchback_srx.html
EU-SUBARU-LEONE-II-WAGON-5D-4WD-01	4285	1620	1445	Automobile-Catalog 1981 Subaru 1800 4WD Station Wagon Dual Range	https://www.automobile-catalog.com/car/1981/3208100/subaru_1800_4wd_station_wagon_dual_range.html
EU-SUBARU-LEONE-II-WAGON-5D-SUPER-4WD-01	4285	1620	1485	Automobile-Catalog 1984 Subaru 1800 GLF 4WD Super Station	https://www.automobile-catalog.com/car/1984/3209195/subaru_1800_glf_4wd_station_wagon_super_station_dual_range.html
EU-NISSAN-KUBISTAR-X76-VAN-01	4035	1672	1825	Anchor Vans Nissan Kubistar specifications	https://www.anchorvans.co.uk/specifications/kubistar
EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-LWB-01	4165	1690	1930	Auto-Data Daihatsu Rocky Soft Top F7 F8 2.8 D 73 Hp	https://www.auto-data.net/en/daihatsu-rocky-soft-top-f7-f8-2.8-d-73hp-67
EU-DAIHATSU-ROCKY-I-F70-SUV-HARDTOP-WIDE-01	3840	1690	1850	Auto-Data Daihatsu Rocky Hard Top F7 F8 2.8 TD 102 Hp	https://www.auto-data.net/en/daihatsu-rocky-hard-top-f7-f8-2.8-td-102hp-63
EU-DAIHATSU-ROCKY-I-F75-SUV-SOFTTOP-WIDE-01	4165	1780	1925	Auto-Data Daihatsu Rocky Soft Top F7 F8 2.8 TD 102 Hp	https://www.auto-data.net/en/daihatsu-rocky-soft-top-f7-f8-2.8-td-102hp-68
EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-PREFL-01	3685	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase I Soft-top	https://www.automobile-catalog.com/car/1989/563795/daihatsu_feroza_1_6i_16v_dx_soft-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-SOFTTOP-FACELIFT-01	3700	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase II Soft-top	https://www.automobile-catalog.com/car/1998/566825/daihatsu_feroza_1_6i_16v_dx_soft-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-PREFL-01	3685	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase I Hard-top	https://www.automobile-catalog.com/car/1993/563825/daihatsu_feroza_1_6i_16v_dx_hard-top.html
EU-DAIHATSU-FEROZA-I-F300-SUV-HARDTOP-FACELIFT-01	3775	1580	1720	Automobile-Catalog Daihatsu Feroza Sportrak phase II Hard-top	https://www.automobile-catalog.com/car/1998/566840/daihatsu_feroza_1_6i_16v_se_hard-top.html
EU-SUBARU-LEONE-III-SEDAN-4D-4WD-01	4370	1660	1425	Automobile-Catalog 1988 Subaru Full Time 4WD 1800 Sedan catalyst	https://www.automobile-catalog.com/car/1988/3216335/subaru_full_time_4wd_1800_sedan_catalyst.html
EU-SUBARU-LEONE-III-SEDAN-4D-TURBO-4WD-01	4370	1660	1400	Automobile-Catalog 1989 Subaru Full Time 4WD 1.8 Turbo Sedan	https://www.automobile-catalog.com/car/1989/3216290/subaru_full_time_4wd_1_8_turbo_4-door_sedan_dual_range.html
EU-SUBARU-LEONE-III-WAGON-5D-4WD-01	4410	1660	1450	Automobile-Catalog 1990 Subaru 4WD 1800 Station Dual Range catalyst	https://www.automobile-catalog.com/car/1990/3216545/subaru_4wd_1800_station_dual_range_catalyst.html
EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-TURBO-01	3610	1600	1385	Automobile-Catalog 1988 Daihatsu Charade Turbo Europe export	https://www.automobile-catalog.com/car/1988/57815/daihatsu_charade_turbo.html
EU-DAIHATSU-CHARADE-III-HATCHBACK-5D-01	3610	1600	1385	Automobile-Catalog 1987 Daihatsu Charade TS Europe export; Automobile-Catalog 1990 Daihatsu Charade Turbo Diesel Europe export; Automobile-Catalog 1989 Daihatsu Charade 1.3i TX	https://www.automobile-catalog.com/car/1987/56165/daihatsu_charade_ts.html;https://www.automobile-catalog.com/car/1990/57800/daihatsu_charade_tx_turbo_diesel.html;https://www.automobile-catalog.com/car/1989/563240/daihatsu_charade_1_3i_tx.html
EU-SUBARU-LEONE-III-WAGON-5D-SUPER-4WD-01	4410	1660	1490	Automobile-Catalog 1984 Subaru 4WD 1.8 GL Super Station	https://www.automobile-catalog.com/car/1984/3214265/subaru_4wd_1_8_gl_station_wagon_dual_range.html
EU-SUBARU-XT-COUPE-2D-01	4450	1690	1335	Auto-Data Subaru XT Coupe 1.8 Turbo 120 Hp 4WD; Auto-Data Subaru XT Coupe 1.8 Turbo 136 Hp 4WD	https://www.auto-data.net/en/subaru-xt-coupe-1.8-turbo-120hp-4wd-16204;https://www.auto-data.net/en/subaru-xt-coupe-1.8-turbo-136hp-4wd-16205
EU-DAIHATSU-CHARADE-III-G100-HATCHBACK-3D-GTI-01	3610	1615	1385	Automobile-Catalog 1990 Daihatsu Charade GTti Europe export	https://www.automobile-catalog.com/car/1990/56180/daihatsu_charade_gtti.html
EU-DAIHATSU-CHARADE-III-G102-HATCHBACK-5D-4WD-01	3610	1615	1400	Automobile-Catalog 1989 Daihatsu Charade 1.3i TXF 4WD	https://www.automobile-catalog.com/car/1989/563270/daihatsu_charade_1_3i_txf_4wd.html
EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	4315	1660	1385	Auto-Data Daihatsu Applause I A101 1.6 16V 105 Hp	https://www.auto-data.net/en/daihatsu-applause-i-a101-a111-1.6-16v-a101-105hp-automatic-24500
EU-SUBARU-JUSTY-I-KAD-HATCHBACK-01	3695	1535	1420	Auto-Data Subaru Justy I KAD 1000 4WD 3dr/5dr; Auto-Data Subaru Justy I KAD 1200 4WD 3dr/5dr	https://www.auto-data.net/en/subaru-justy-i-kad-1000-4wd-kad-a-3-dr-55hp-16133;https://www.auto-data.net/en/subaru-justy-i-kad-1000-4wd-kad-a-5-dr-55hp-16135;https://www.auto-data.net/en/subaru-justy-i-kad-1200-4wd-3-dr-74hp-16137;https://www.auto-data.net/en/subaru-justy-i-kad-1200-4wd-5-dr-74hp-16138
EU-DAIHATSU-APPLAUSE-I-A111-HATCHBACK-4WD-01	4315	1660	1440	Auto-Data Daihatsu Applause I A111 1.6 16V 4WD 105 Hp	https://www.auto-data.net/en/daihatsu-applause-i-a101-a111-1.6-16v-4wd-a111-105hp-35
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-01	3780	1620	1390	Auto-Data Daihatsu Charade IV Com G200 1.3 i TS 84 Hp	https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.3-i-ts-84hp-127
EU-DAIHATSU-CHARADE-IV-G200-HATCHBACK-GTI-01	3750	1620	1390	Auto-Data Daihatsu Charade IV Com G200 1.6 GTi 105 Hp	https://www.auto-data.net/en/daihatsu-charade-iv-com-g200-1.6-gti-105hp-130
EU-DAIHATSU-CHARADE-IV-G200-SEDAN-01	4085	1620	1390	Auto-Data Daihatsu Charade IV G200 1.5 i 16V SX 90 Hp	https://www.auto-data.net/de/daihatsu-charade-iv-g200-1.5-i-16v-sx-90hp-123
EU-SUBARU-LIBERO-I-E10-MPV-LOWROOF-01	3410	1430	1870	Automobile-Catalog 1984 Subaru Domingo 4WD GS	https://www.automobile-catalog.com/car/1984/3223895/subaru_domingo_4wd_gs.html
EU-SUBARU-LIBERO-I-E10-MPV-HIGHROOF-01	3410	1430	1900	Automobile-Catalog 1984 Subaru Libero E10 Wagon 4WD	https://www.automobile-catalog.com/car/1984/48365/subaru_e-10.html
EU-SUBARU-LIBERO-I-E12-MPV-LOWROOF-01	3425	1430	1870	Automobile-Catalog 1991 Subaru Domingo Full Time 4WD GS	https://www.automobile-catalog.com/car/1991/3224030/subaru_domingo_full_time_4wd_gs.html
EU-SUBARU-LIBERO-I-E12-MPV-HIGHROOF-01	3425	1430	1900	Automobile-Catalog 1991 Subaru Domingo Full Time 4WD GX	https://www.automobile-catalog.com/car/1991/3224180/subaru_domingo_full_time_4wd_gx.html
EU-SUBARU-LIBERO-II-MPV-01	3525	1415	1925	Automobile-Catalog 1997 Subaru Libero 1.2 Wagon 4WD SDX SR Special	https://www.automobile-catalog.com/car/1997/3224735/subaru_libero_1_2_wagon_4wd_sdx_sr_special.html
EU-SUZUKI-ALTO-I-HATCHBACK-5D-01	3195	1395	1335	Automobile-Catalog 1979 Suzuki Alto MX	https://www.automobile-catalog.com/car/1979/3324710/suzuki_alto_mx.html
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	Auto-Data BMW 5 Series Sedan F10 525d xDrive	https://www.auto-data.net/en/bmw-5-series-sedan-f10-525d-218hp-xdrive-steptronic-17271
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464	Auto-Data BMW 5 Series Sedan F10 LCI 525d xDrive	https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-525d-218hp-xdrive-steptronic-19964
EU-SUBARU-LEGACY-I-BC-SEDAN-PREFL-01	4510	1690	1385	Auto-Data Subaru Legacy I BC generation	https://www.auto-data.net/en/subaru-legacy-i-bc-generation-3617
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-1800-2200-01	4545	1690	1400	Auto-Data Subaru Legacy I BC facelift 1800 AWD; Auto-Data Subaru Legacy I BC facelift 2200 AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-1800-103hp-awd-34241;https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2200-136hp-awd-16191
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-2000-01	4545	1690	1380	Auto-Data Subaru Legacy I BC facelift 2000 AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2000-116hp-awd-16188
EU-SUBARU-LEGACY-I-BC-SEDAN-FACELIFT-TURBO-01	4545	1690	1385	Auto-Data Subaru Legacy I BC facelift 2000 Turbo AWD	https://www.auto-data.net/en/subaru-legacy-i-bc-facelift-1991-2000-turbo-220hp-awd-16190
EU-SUZUKI-ALTO-II-SB308-HATCHBACK-3D-01	3300	1420	1340	UltimateSpecs Suzuki Alto 2 specifications	https://www.ultimatespecs.com/car-specs/Suzuki/M972/Alto-2
EU-SUBARU-LEGACY-I-BJF-WAGON-PREFL-01	4600	1690	1490	Auto-Data Subaru Legacy I Station Wagon BJF generation	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-generation-3618
EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-01	4620	1690	1480	Auto-Data Subaru Legacy I BJF facelift 1800 AWD; Auto-Data Subaru Legacy I BJF facelift 2000 AWD; Auto-Data Subaru Legacy I BJF facelift 2200 AWD	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-1800-103hp-awd-34172;https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2000-116hp-awd-automatic-24057;https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2200-136hp-awd-34173
EU-KIA-SORENTO-I-BL-SUV-FACELIFT-01	4590	1865	1730	Auto-Data Kia Sorento I facelift 2006 2.5 CRDi 170 Hp	https://www.auto-data.net/en/kia-sorento-i-facelift-2006-2.5-crdi-170hp-2661
EU-SUBARU-LEGACY-I-BJF-WAGON-FACELIFT-TURBO-01	4620	1690	1465	Auto-Data Subaru Legacy I BJF facelift 2000 Turbo AWD	https://www.auto-data.net/en/subaru-legacy-i-station-wagon-bjf-facelift-1991-2000-turbo-200hp-awd-16195
EU-SUBARU-SVX-CX-COUPE-2D-01	4625	1777	1300	Auto-Data Subaru SVX CX 3.3 i 24V 4WD CXW 230 Hp	https://www.auto-data.net/en/subaru-svx-cx-3.3-i-24v-4wd-cxw-230hp-16203
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	3585	1530	1350	Automobile-Catalog 1984 Suzuki Swift 1.0 GA	https://www.automobile-catalog.com/car/1984/48485/suzuki_swift_1_0.html
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415	Auto-Data Subaru Impreza I GC 1.6i AWD	https://www.auto-data.net/en/subaru-impreza-i-gc-1.6i-90hp-4wd-16095
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420	Auto-Data Subaru Impreza I GF 1.6i AWD	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-1.6i-90hp-4wd-16111
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	3770	1545	1350	Automobile-Catalog 1987 Suzuki Swift 1.3 GLX 5-door	https://www.automobile-catalog.com/car/1987/3327875/suzuki_swift_1_3_glx_5-door.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4201-4300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/subaru-justy-i-kad-1000-4wd-kad-a-3-dr-55hp-16133 "Subaru Justy I (KAD) 1000 4WD (KAD-A) (3 dr) (55 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1986/562670/daihatsu_rocky_2_0_soft-top.html?utm_source=chatgpt.com "1986 Daihatsu Rocky (Fourtrak) 2.0 Soft-top Specs Review ..."
[3]: https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2008-amg-g-55-v8-kompressor-507hp-4matic-7g-tronic-42526?utm_source=chatgpt.com "Mercedes-Benz G-class Long (W463, facelift 2008) AMG G ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4201-4300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4201-4300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5677 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1735 行）

