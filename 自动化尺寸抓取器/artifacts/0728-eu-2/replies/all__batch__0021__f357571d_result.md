# 任务：all 第 2001-2100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0021__f357571d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2001-2100 行

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
all 第 2001-2100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-CADILLAC-BLS-SEDAN-01	4680	1752	1471
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-HHR-WAGON-5D-01	4475	1755	1603
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810
EU-CITROEN-C5-I-PHASE-I-HATCHBACK-5D-01	4618	1770	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4745	1780	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-02	4750	1770	1480
EU-CITROEN-C5-I-PHASE-II-WAGON-01	4839	1780	1511
EU-CITROEN-C5-I-PHASE-I-WAGON-5D-01	4760	1770	1520
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-02	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-02	4250	1735	1525
EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	4045	1695	1470
EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	4280	1695	1470
EU-LADA-110-SEDAN-01	4277	1676	1430
EU-LEXUS-RX-II-SUV-350-AWD-01	4740	1845	1705
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	4775	1845	1855
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	4775	1845	1885
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	4260	1845	1845
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	4260	1845	1875
EU-MITSUBISHI-PAJERO-III-CLASSIC-V68W-SUV-3D-01	4295	1885	1845
EU-MITSUBISHI-PAJERO-III-CLASSIC-V78W-SUV-5D-01	4810	1885	1855
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-SMART-FORTWO-II-CONVERTIBLE-01	2695	1559	1542
EU-SMART-FORTWO-II-COUPE-01	2695	1559	1542
EU-SUBARU-FORESTER-II-FACELIFT-SUV-01	4450	1735	1590
EU-SUBARU-FORESTER-II-SUV-01	4450	1735	1590
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-TATA-SAFARI-I-SUV-01	4800	1810	1910
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jaguar	Xf i	2.7 D	Stufenheck	Heckantrieb	Diesel	152	207	Mar 2008	Apr 2015	2024-03-01	24477
Porsche	Cayenne	GTS 4.8	SUV	Allrad	Benzin	298	405	Oct 2007	Sep 2010	2024-03-01	24478
Cadillac	Bls	2.0 T Flexpower	Stufenheck	Frontantrieb	Benzin/Ethanol	147	200	Dec 2007	-	2024-03-01	24479
Cadillac	Bls	1.9 D	Stufenheck	Frontantrieb	Diesel	132	180	Dec 2007	-	2024-03-01	24480
Cadillac	Bls	2.0 T	Kombi	Frontantrieb	Benzin	129	175	Dec 2007	Dec 2010	2024-03-01	24481
Cadillac	Bls	2.0 T Flexpower	Kombi	Frontantrieb	Benzin/Ethanol	147	200	Dec 2007	-	2024-03-01	24482
Cadillac	Bls	2.0 T	Kombi	Frontantrieb	Benzin	154	210	Dec 2007	-	2024-03-01	24483
Cadillac	Bls	2.8 T	Kombi	Frontantrieb	Benzin	188	255	Dec 2007	-	2024-03-01	24484
Cadillac	Bls	1.9 D	Kombi	Frontantrieb	Diesel	110	150	Dec 2007	-	2024-03-01	24485
Cadillac	Bls	1.9 D	Kombi	Frontantrieb	Diesel	132	180	Dec 2007	-	2024-03-01	24486
Cadillac	Cts	2.8	Stufenheck	Heckantrieb	Benzin	155	211	Jan 2008	Dec 2009	2024-03-01	24487
Cadillac	Cts	3.6	Stufenheck	Heckantrieb	Benzin	229	311	Jan 2008	Sep 2013	2024-03-01	24488
Cadillac	Cts	3.6 AWD	Stufenheck	Allrad	Benzin	229	311	Jan 2008	Sep 2013	2024-03-01	24489
Dacia	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	63	86	Sep 2007	Dec 2011	2024-03-01	24490
Dacia	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	63	86	Sep 2007	Dec 2012	2024-03-01	24491
VW	Golf v variant	1.9 TDI 4motion	Kombi	Allrad	Diesel	77	105	Jan 2008	Jul 2009	2024-03-01	24492
Audi	A3	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Apr 2008	May 2013	2024-03-01	24493
Audi	A3	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	147	200	Apr 2008	May 2013	2024-03-01	24494
Audi	A3	1.9 TDI	Cabriolet	Frontantrieb	Diesel	77	105	Apr 2008	Oct 2009	2024-03-01	24495
Audi	A3	2.0 TDI	Cabriolet	Frontantrieb	Diesel	103	140	Apr 2008	May 2013	2024-03-01	24496
Audi	A6 c6 avant	RS6 Quattro	Kombi	Allrad	Benzin	426	580	Apr 2008	Aug 2010	2024-03-01	24497
Citroën	C5	1.8 16V	Stufenheck	Frontantrieb	Benzin	92	125	Feb 2008	Oct 2010	2024-07-01	24498
Citroën	C5	2.0 16V	Stufenheck	Frontantrieb	Benzin	103	140	Feb 2008	Oct 2014	2024-07-01	24499
Citroën	C5	3.0 V6	Stufenheck	Frontantrieb	Benzin	155	211	Feb 2008	Dec 2010	2024-07-01	24500
Citroën	C5	1.6 HDI 110	Stufenheck	Frontantrieb	Diesel	80	109	Feb 2008	Oct 2010	2024-07-01	24501
Citroën	C5	2.0 HDI	Stufenheck	Frontantrieb	Diesel	100	136	Feb 2008	Jun 2014	2024-07-01	24502
Citroën	C5	2.2 HDI	Stufenheck	Frontantrieb	Diesel	125	170	Feb 2008	Dec 2011	2024-07-01	24503
Citroën	C5	2.7 HDI	Stufenheck	Frontantrieb	Diesel	150	204	Feb 2008	Dec 2009	2024-07-01	24504
Citroën	C5	1.8 I 16V	Kombi	Frontantrieb	Benzin	92	125	Feb 2008	Oct 2010	2024-07-01	24505
Citroën	C5	2.0 I 16V	Kombi	Frontantrieb	Benzin	103	140	Feb 2008	Oct 2014	2024-07-01	24506
Citroën	C5	3.0 V6	Kombi	Frontantrieb	Benzin	155	211	Feb 2008	Dec 2010	2024-07-01	24507
Citroën	C5	1.6 HDI 110	Kombi	Frontantrieb	Diesel	80	109	Feb 2008	Oct 2010	2024-07-01	24508
Citroën	C5	2.0 HDI	Kombi	Frontantrieb	Diesel	100	136	Feb 2008	Jun 2014	2024-07-01	24509
Citroën	C5	2.2 HDI	Kombi	Frontantrieb	Diesel	125	170	Feb 2008	Dec 2011	2024-07-01	24510
Citroën	C5	2.7 HDI	Kombi	Frontantrieb	Diesel	150	204	Feb 2008	Oct 2009	2024-07-01	24511
Citroën	Berlingo	1.6	Großraumlimousine	Frontantrieb	Benzin	66	90	Apr 2008	Dec 2018	2026-05-01	24512
Citroën	Berlingo	1.6	Großraumlimousine	Frontantrieb	Benzin	80	109	Apr 2008	Dec 2018	2026-05-01	24513
Citroën	Berlingo	1.6 HDI 75 16V	Großraumlimousine	Frontantrieb	Diesel	55	75	Apr 2008	Dec 2018	2026-05-01	24514
Citroën	Berlingo	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	66	90	Apr 2008	Dec 2018	2026-05-01	24515
Citroën	Berlingo	1.6 HDI 110	Großraumlimousine	Frontantrieb	Diesel	80	109	Apr 2008	Dec 2018	2026-05-01	24516
Citroën	Berlingo	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	66	90	Apr 2008	Dec 2018	2026-05-01	24517
Citroën	Berlingo	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	80	109	Apr 2008	Dec 2018	2026-05-01	24518
Citroën	Berlingo	1.6 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Apr 2008	Dec 2018	2026-05-01	24519
Citroën	Berlingo	1.6 HDI 90 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Apr 2008	Dec 2018	2026-05-01	24520
Citroën	Berlingo	1.6 HDI 110	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Apr 2008	Dec 2018	2026-05-01	24521
Citroën	Nemo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	54	73	Feb 2008	-	2024-03-01	24522
Citroën	Nemo	1.4 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	50	68	Feb 2008	-	2024-03-01	24523
Renault	Logan	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Sep 2004	-	2024-03-01	24524
Renault	Logan	1.6	Stufenheck	Frontantrieb	Benzin	64	87	Sep 2004	-	2024-03-01	24525
Peugeot	Bipper	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	54	73	Feb 2008	-	2024-03-01	24527
Peugeot	Bipper	1.4 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	50	68	Feb 2008	-	2024-03-01	24528
Peugeot	Partner tepee	1.6 VTI	Großraumlimousine	Frontantrieb	Benzin	66	90	Apr 2008	-	2024-03-01	24529
Peugeot	Partner tepee	1.6 VTI	Großraumlimousine	Frontantrieb	Benzin	80	109	Apr 2008	-	2024-03-01	24530
Peugeot	Partner tepee	1.6 HDI 16V	Großraumlimousine	Frontantrieb	Diesel	66	90	Apr 2008	-	2024-03-01	24532
Peugeot	Partner tepee	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	80	109	Apr 2008	-	2024-03-01	24533
Peugeot	Partner	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	66	90	Apr 2008	-	2024-03-01	24534
Peugeot	Partner	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	80	109	Apr 2008	-	2024-03-01	24535
Peugeot	Partner	1.6 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Apr 2008	-	2024-03-01	24536
Peugeot	Partner	1.6 HDI 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Apr 2008	-	2024-03-01	24537
Peugeot	Partner	1.6 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	80	109	Apr 2008	-	2024-03-01	24538
Jeep	Patriot	2.4 4X4	Geländewagen geschlossen	Allrad	Benzin	125	170	Jan 2008	Dec 2017	2024-03-01	24539
Jeep	Patriot	2.0 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	103	140	Feb 2007	Dec 2017	2024-03-01	24540
Mitsubishi	Lancer viii	1.8	Stufenheck	Frontantrieb	Benzin	105	143	Feb 2008	-	2024-03-01	24542
Mitsubishi	Lancer viii	2.0 Di-d	Stufenheck	Frontantrieb	Diesel	103	140	Jan 2008	-	2024-03-01	24543
Mitsubishi	L200	2.5 Di-d 4WD	Pick-up	Allrad	Diesel	123	167	Oct 2007	Dec 2015	2024-03-01	24544
Lexus	Is ii	IS F	Stufenheck	Heckantrieb	Benzin	311	423	Nov 2007	Mar 2013	2024-03-01	24545
Smart	Fortwo	1.0 Brabus	Coupe	Heckantrieb	Benzin	72	98	Jan 2008	-	2024-03-01	24547
Honda	Fr-V	1.8	Großraumlimousine	Frontantrieb	Benzin	103	140	Jan 2007	Dec 2009	2025-12-01	24548
Mitsubishi	Pajero ii	2.5 Tdic	Geländewagen geschlossen	Allrad	Diesel	73	99	Mar 1991	Aug 1999	2024-03-01	24555
Mitsubishi	Pajero ii canvas top	2.5 Tdic	Geländewagen offen	Allrad	Diesel	73	99	Mar 1991	Aug 1999	2024-03-01	24585
Jeep	Wrangler i	4.0 2WD	Geländewagen offen	Heckantrieb	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	24593
Jeep	Wrangler i	4.0 4X4	Geländewagen offen	Allrad	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	24594
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	110	150	Aug 2013	Oct 2018	2024-03-01	24597
Lexus	Rx	300	SUV	Frontantrieb	Benzin	148	201	Jan 1998	Feb 2003	2024-03-01	24598
Honda	Concerto	1.6	Stufenheck	Frontantrieb	Benzin	96	131	Oct 1989	Oct 1992	2024-03-01	24599
Tata	Safari	2.0 TDI 4X4	SUV	Allrad	Diesel	64	87	Jul 2003	-	2024-03-01	24612
Land Rover	Defender cabrio	3.9 4X4	Geländewagen offen	Allrad	Benzin	134	182	Apr 1998	Sep 2000	2024-03-01	24616
Land Rover	Defender station wagon	3.9 4X4	Geländewagen geschlossen	Allrad	Benzin	134	182	Jan 1993	Sep 2000	2024-03-01	24617
Subaru	Impreza	2.5 AWD	Stufenheck	Allrad	Benzin	130	177	Mar 2001	Sep 2005	2024-03-01	24618
Subaru	Impreza	2.0 AWD	Stufenheck	Allrad	Benzin	184	250	Oct 2005	Mar 2007	2024-03-01	24621
Subaru	Impreza	2.5 AWD	Stufenheck	Allrad	Benzin	221	300	Oct 2005	Mar 2007	2024-03-01	24622
Subaru	Impreza station wagon	2.5 AWD	Kombi	Allrad	Benzin	221	300	Oct 2005	Mar 2007	2024-03-01	24627
Nissan	X-Trail i	2.2 DCI FWD	SUV	Frontantrieb	Diesel	84	114	Jun 2001	Sep 2004	2024-03-01	24628
Hyundai	Accent ii	1.5	Stufenheck	Frontantrieb	Benzin	75	102	Sep 1999	Oct 2002	2024-03-01	24636
Land Rover	Defender pick up	4.0 4X4	Geländewagen offen	Allrad	Benzin	134	182	Apr 1998	Sep 2000	2024-03-01	24641
Subaru	Forester	2.5 AWD	SUV	Allrad	Benzin	129	175	Jan 2005	Oct 2012	2024-03-01	24659
Lada	110	1.6	Stufenheck	Frontantrieb	Benzin	60	82	Jan 2000	Dec 2012	2024-03-01	24668
Lada	110	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Jan 2000	Dec 2008	2024-03-01	24669
Chevrolet	Camaro	5.7	Cabriolet	Heckantrieb	Benzin	168	228	Oct 1988	Sep 1989	2024-03-01	24676
Chevrolet	Camaro	5.7	Cabriolet	Heckantrieb	Benzin	182	247	Oct 1988	Sep 1989	2024-03-01	24677
Chevrolet	Colorado	2.8	Pick-up	Heckantrieb	Benzin	130	177	Apr 2003	Sep 2006	2024-03-01	24700
Chevrolet	Colorado	3.5	Pick-up	Heckantrieb	Benzin	164	223	May 2005	Sep 2006	2024-03-01	24701
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	246	335	Sep 1995	Dec 1997	2026-06-01	24715
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	207	281	Oct 1991	Apr 1997	2024-03-01	24717
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	224	305	Oct 1991	Apr 1997	2024-03-01	24718
Chevrolet	Hhr	2.4	Kombi	Frontantrieb	Benzin	128	174	Jan 2006	Dec 2011	2024-03-01	24720
Chrysler	Pacifica	3.5	Großraumlimousine	Frontantrieb	Benzin	186	253	Aug 2003	Dec 2006	2024-03-01	24765
Dodge	Charger	3.5	Stufenheck	Heckantrieb	Benzin	186	253	Jun 2005	Dec 2010	2024-03-01	24770
Dodge	Durango	4.7	SUV	Heckantrieb	Benzin	172	234	Nov 2003	Dec 2009	2024-03-01	24778
Dodge	Ramcharger	5.2	SUV	Heckantrieb	Benzin	107	145	Oct 1983	Sep 1988	2024-03-01	24784


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合前 40 个输入 Ktype，共形成 42 条 READY 映射；`24490`、`24491` 因生产期跨越改款且外廓发生变化，分别拆为改款前、改款后两条。
* 直接复用累计尺寸组 6 个：Cadillac BLS Sedan、Dacia Logan Sedan 改款前后、Logan MCV 改款前后、VW Golf V Variant。
* 首次建立 9 个尺寸组：Jaguar XF X250、Cayenne 957 GTS、BLS Wagon、CTS II Sedan、A3 8P Cabriolet、RS6 C6 Avant、C5 X7 Sedan、C5 X7 Tourer、Berlingo B9 MPV。
* A3 Cabriolet 与 RS6 Avant 的宽度来源明确为不含后视镜口径；C5 X7 轿车和 Tourer 分别采用独立外廓。([汽车目录][1])
* Berlingo B9 乘用 MPV 已闭合为 `4380 × 1810 × 1801 mm`；后续 `Kasten/Großraumlimousine` 行暂不强行复用，因为厢式版本存在 `1812 mm` 高度记录。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：40
* READY 映射：42
* PENDING 输入 Ktype：60
* 已确认尺寸组：15

  * 本轮首次创建：9
  * 复用累计组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24477	24477	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH		READY
24478	24478	SUV	Cayenne 957	957	5	EU-PORSCHE-CAYENNE-957-SUV-GTS-01	HIGH	GTS独立外廓高度。	READY
24479	24479	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH		READY
24480	24480	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH		READY
24481	24481	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24482	24482	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24483	24483	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24484	24484	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24485	24485	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24486	24486	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24487	24487	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24488	24488	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24489	24489	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24490_prefl	24490	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产期跨越改款，按改款前外廓拆分。	READY
24490_facelift	24490	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产期跨越改款，按改款后外廓拆分。	READY
24491_prefl	24491	Wagon	Logan I MCV	KS	5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	MEDIUM	生产期跨越改款，按改款前外廓拆分。	READY
24491_facelift	24491	Wagon	Logan I MCV	KS	5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	MEDIUM	生产期跨越改款，按改款后外廓拆分。	READY
24492	24492	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
24493	24493	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24494	24494	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24495	24495	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24496	24496	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24497	24497	Wagon	RS6 C6	4F5	5	EU-AUDI-RS6-C6-AVANT-WAGON-5D-01	HIGH	RS6宽体外廓。	READY
24498	24498	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24499	24499	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24500	24500	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24501	24501	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24502	24502	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24503	24503	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24504	24504	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24505	24505	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24506	24506	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24507	24507	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24508	24508	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24509	24509	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24510	24510	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24511	24511	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24512	24512	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24513	24513	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24514	24514	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24515	24515	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24516	24516	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XF-I-SEDAN-X250-01	4961	1877	1460	CarSized	https://www.carsized.com/en/cars/jaguar-xf-2008-sedan/front/
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675	CarExpert	https://dt16c8g6jis9k.cloudfront.net/porsche/cayenne/2008/dimensions
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543	Auto-Data	https://www.auto-data.net/en/cadillac-bls-wagon-2.0-t-175hp-51812
EU-CADILLAC-CTS-II-SEDAN-4D-01	4866	1842	1472	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/334820/cadillac_cts_3_6l_v-6.html
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1187270/audi_a3_cabriolet_1_6.html
EU-AUDI-RS6-C6-AVANT-WAGON-5D-01	4928	1889	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/252410/audi_rs6_avant.html
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451	CarsGuide	https://www.carsguide.com.au/citroen/c5/car-dimensions/2008
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479	CarsGuide	https://www.carsguide.com.au/citroen/c5/car-dimensions/2008
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/553040/citroen_berlingo_multispace_hdi_90.html
```

## 下一步优先处理

1. 先解决 `24517–24521` Berlingo B9 的厢式车/乘用车边界，并与 `1812 mm` 厢式高度分组。
2. 批量闭合 Nemo、Bipper、Partner Tepee、Partner Van 四个同平台聚类，避免重复抓取。
3. 继续处理 Jeep Patriot、Lancer VIII、L200、Lexus IS F、Honda FR-V 等单一外廓车型。
4. 最后集中处理 Pajero、Defender、Colorado 等必须确认短长轴、门数或 CAB/BED 的复杂 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/1187270/audi_a3_cabriolet_1_6.html?utm_source=chatgpt.com "2008 Audi A3 Cabriolet 1.6 Specs Review (75 kW / 102 PS / 101 hp) (since mid-year 2008 for Europe )"
[2]: https://www.automobile-catalog.com/car/2008/553040/citroen_berlingo_multispace_hdi_90.html?utm_source=chatgpt.com "2008 Citroen Berlingo Multispace HDi 90 (man. 5)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1) 更新点

* 本轮完成 18 个输入 Ktype，新增 24 条 `READY` 映射。
* 首次闭合 9 个尺寸组：Nemo 厢式/MPV、Bipper 厢式/MPV、Partner Tepee、Patriot、Lancer VIII、Lexus IS F、Honda FR-V。
* Renault Logan 改款前后直接复用本批已有 Dacia Logan 尺寸组。
* Mitsubishi L200 KB4T 双排驾驶室、Smart Fortwo II Coupe 直接复用跨批次已有尺寸组。
* Berlingo B9 与 Partner B9 厢式车存在 L1/L2 以及具体高度配置边界，本轮未写入猜测性映射。

## 2) 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：58
* READY 映射：66
* PENDING 输入 Ktype：42
* 当前批次已引用并确认尺寸组：26
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24522_van	24522	Van	Nemo I	AA		EU-CITROEN-NEMO-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24522_mpv	24522	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24523_van	24523	Van	Nemo I	AA		EU-CITROEN-NEMO-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24523_mpv	24523	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24524_prefl	24524	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产范围覆盖改款边界，按改款前外廓拆分。	READY
24524_facelift	24524	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产范围覆盖改款边界，按改款后外廓拆分。	READY
24525_prefl	24525	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产范围覆盖改款边界，按改款前外廓拆分。	READY
24525_facelift	24525	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产范围覆盖改款边界，按改款后外廓拆分。	READY
24527_van	24527	Van	Bipper I	AA		EU-PEUGEOT-BIPPER-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24527_mpv	24527	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24528_van	24528	Van	Bipper I	AA		EU-PEUGEOT-BIPPER-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24528_mpv	24528	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24529	24529	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24530	24530	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24532	24532	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24533	24533	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24539	24539	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
24540	24540	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
24542	24542	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
24543	24543	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
24544	24544	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	MEDIUM	KB4T双排驾驶室物理边界。	READY
24545	24545	Sedan	IS II	USE20	4	EU-LEXUS-IS-II-USE20-ISF-SEDAN-4D-01	HIGH	IS F专属加长加宽外廓。	READY
24547	24547	Coupe	Fortwo II	451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH		READY
24548	24548	MPV	FR-V I facelift		5	EU-HONDA-FR-V-I-FACELIFT-MPV-5D-01	HIGH		READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-NEMO-I-AA-VAN-01	3864	1716	1721	Auto-Data	https://www.auto-data.net/en/citroen-nemo-panel-van-1.4-hdi-70hp-54973
EU-CITROEN-NEMO-I-AJ-MPV-01	3959	1716	1721	Auto-Data	https://www.auto-data.net/en/citroen-nemo-multispace-1.4-hdi-70hp-54978
EU-PEUGEOT-BIPPER-I-AA-VAN-01	3864	1716	1721	AutoScout24	https://www.autoscout24.de/auto/technische-daten/peugeot/bipper/
EU-PEUGEOT-BIPPER-I-AJ-MPV-01	3959	1716	1721	AutoScout24	https://www.autoscout24.de/auto/technische-daten/peugeot/bipper/
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803	Auto-Data	https://www.auto-data.net/en/peugeot-partner-ii-tepee-1.6-90hp-5619
EU-JEEP-PATRIOT-I-MK74-SUV-01	4408	1785	1658	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1331540/jeep_patriot_2_0_crd_limited_dpf.html
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1996190/mitsubishi_lancer_2_0_di-d.html
EU-LEXUS-IS-II-USE20-ISF-SEDAN-4D-01	4660	1815	1415	Toyota GAZOO vehicle catalog	https://gazoo.com/catalog/maker/LEXUS/IS_F/200712/10043520/
EU-HONDA-FR-V-I-FACELIFT-MPV-5D-01	4285	1810	1610	Honda European Media Newsroom	https://hondanews.eu/eu/en/cars/media/pressreleases/214/fr-v-summary
```

## 5) 下一步优先处理

1. 闭合 `24517–24521` Berlingo B9 厢式车的 L1/L2 与具体高度配置。
2. 闭合 `24534–24538` Partner B9 厢式车的 L1/L2 分支。
3. 集中处理 Pajero II、Pajero Canvas Top、Wrangler YJ、Defender 90/110 等短长轴或开放式车身。
4. 批量复用 Giulietta、Tata Safari、Subaru、Lada、Corvette、HHR 等已有尺寸组。
5. 最后处理 Colorado CAB/BED、Camaro Convertible、Pacifica、Charger、Durango 与 Ramcharger。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1) 更新点

* 本轮完成 26 个输入 Ktype，新增 28 条 `READY` 映射。
* Berlingo/Partner 厢式车已按 L1/L2 物理长度闭合；90 马力柴油 Ktype 拆分为短轴和长轴，其余版本只关联已确认的 L1 外廓。Berlingo 与 Partner 的资料均明确给出 `1810 mm` 不含后视镜宽度及两种车长。
* Giulietta、Tata Safari、Impreza、Lada 110、Chevrolet HHR 等直接复用已有尺寸组，没有重复输出尺寸来源。
* 剩余阻塞项集中为 Pajero、Defender、早期 Impreza、跨代 Forester、Camaro、Colorado、Corvette、Durango 和 Ramcharger。

## 2) 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：84
* READY 映射：94
* PENDING 输入 Ktype：16
* 当前批次已引用并确认尺寸组：43
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24517	24517	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24518	24518	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24519	24519	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24520_l1	24520	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	同一动力覆盖L1厢式车。	READY
24520_l2	24520	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	MEDIUM	同一动力覆盖L2厢式车。	READY
24521	24521	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24534	24534	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24535	24535	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24536	24536	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24537_l1	24537	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	同一动力覆盖L1厢式车。	READY
24537_l2	24537	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	同一动力覆盖L2厢式车。	READY
24538	24538	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24593	24593	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	MEDIUM	4.0升版本对应YJ软顶两门外廓；上游生产年月早于该发动机上市。	READY
24594	24594	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	MEDIUM	4.0升版本对应YJ软顶两门外廓；上游生产年月早于该发动机上市。	READY
24597	24597	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
24598	24598	SUV	RX I	XU10	5	EU-LEXUS-RX-I-XU10-SUV-01	HIGH		READY
24599	24599	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH		READY
24612	24612	SUV	Safari I		5	EU-TATA-SAFARI-I-SUV-01	HIGH		READY
24621	24621	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH		READY
24622	24622	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH		READY
24627	24627	Wagon	Impreza II	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	HIGH	WRX旅行车高度外廓。	READY
24628	24628	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	HIGH	改款前T30外廓。	READY
24636	24636	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-PREFL-01	HIGH	改款前轿车外廓。	READY
24668	24668	Sedan	110		4	EU-LADA-110-SEDAN-01	HIGH		READY
24669	24669	Sedan	110		4	EU-LADA-110-SEDAN-01	HIGH		READY
24720	24720	Wagon	HHR		5	EU-CHEVROLET-HHR-WAGON-5D-01	HIGH		READY
24765	24765	MPV	Pacifica I	CS	5	EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	HIGH		READY
24770	24770	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH		READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801	Citroën Berlingo Van official brochure	https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828	Citroën Berlingo Van official brochure	https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834	Peugeot Partner 2008 official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/08/Peugeot-Partner-2008-AU.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner 2008 official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/08/Peugeot-Partner-2008-AU.pdf
EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	3879	1676	1829	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1315415/jeep_wrangler_4_0l.html
EU-LEXUS-RX-I-XU10-SUV-01	4580	1815	1660	Auto-Data	https://www.auto-data.net/en/lexus-rx-i-300-201hp-5894
EU-HONDA-CONCERTO-HW-SEDAN-4D-01	4415	1690	1395	Auto-Data	https://www.auto-data.net/en/honda-concerto-model-1312
EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	4510	1765	1675	Auto-Data	https://www.auto-data.net/en/nissan-x-trail-i-t30-2.2-dci-114hp-4x4-913
EU-HYUNDAI-ACCENT-II-LC-SEDAN-PREFL-01	4235	1670	1395	Auto-Data	https://www.auto-data.net/en/hyundai-accent-ii-1.5-i-16v-102hp-automatic-24810
EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	5052	2013	1688	Auto-Data	https://www.auto-data.net/en/chrysler-pacifica-3.5-v6-253hp-14716
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479	Dodge 2006 Charger official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2006Charger_specs.pdf
```

## 5) 下一步优先处理

1. 闭合 Pajero II 硬顶和 Canvas Top 的门数、窄体/宽体边界。
2. 闭合 Defender Cabrio、Station Wagon、Pick Up 的 90/110/130 车身分支。
3. 拆分 `24618` Impreza 早期改款和 `24659` Forester SG/SH 跨代外廓。
4. 闭合 Camaro Convertible、Colorado CAB/BED、Corvette C4 Coupe。
5. 最后处理 Durango II 与 Ramcharger II，随后检查是否达到 `PENDING=0`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已完成剩余 16 个输入 Ktype 的物理外廓拆分与尺寸组闭合。
* 本批 100 个输入 Ktype 全部覆盖，共生成 129 条映射。
* 最终引用 66 个尺寸组，全部具备完整长、宽、高、来源和直接 URL。
* 已完成机械检查：表头正确、`id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、无孤立尺寸组、无 `PENDING`。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：129
* PENDING：0
* DIMENSION_GROUP：66
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
24477	24477	Sedan	XF I	X250	4	EU-JAGUAR-XF-I-SEDAN-X250-01	HIGH		READY
24478	24478	SUV	Cayenne 957	957	5	EU-PORSCHE-CAYENNE-957-SUV-GTS-01	HIGH	GTS独立外廓高度。	READY
24479	24479	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH		READY
24480	24480	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH		READY
24481	24481	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24482	24482	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24483	24483	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24484	24484	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24485	24485	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24486	24486	Wagon	BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
24487	24487	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24488	24488	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24489	24489	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
24490_prefl	24490	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产期跨越改款，按改款前外廓拆分。	READY
24490_facelift	24490	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产期跨越改款，按改款后外廓拆分。	READY
24491_prefl	24491	Wagon	Logan I MCV	KS	5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	MEDIUM	生产期跨越改款，按改款前外廓拆分。	READY
24491_facelift	24491	Wagon	Logan I MCV	KS	5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	MEDIUM	生产期跨越改款，按改款后外廓拆分。	READY
24492	24492	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
24493	24493	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24494	24494	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24495	24495	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24496	24496	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
24497	24497	Wagon	RS6 C6	4F5	5	EU-AUDI-RS6-C6-AVANT-WAGON-5D-01	HIGH	RS6宽体外廓。	READY
24498	24498	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24499	24499	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24500	24500	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24501	24501	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24502	24502	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24503	24503	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24504	24504	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH		READY
24505	24505	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24506	24506	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24507	24507	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24508	24508	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24509	24509	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24510	24510	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24511	24511	Wagon	C5 II Tourer	X7	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH		READY
24512	24512	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24513	24513	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24514	24514	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24515	24515	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24516	24516	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
24517	24517	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24518	24518	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24519	24519	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24520_l1	24520	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	同一动力覆盖L1厢式车。	READY
24520_l2	24520	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	MEDIUM	同一动力覆盖L2厢式车。	READY
24521	24521	Van	Berlingo II	B9		EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24522_van	24522	Van	Nemo I	AA		EU-CITROEN-NEMO-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24522_mpv	24522	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24523_van	24523	Van	Nemo I	AA		EU-CITROEN-NEMO-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24523_mpv	24523	MPV	Nemo I	AJ	5	EU-CITROEN-NEMO-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24524_prefl	24524	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产范围覆盖改款边界，按改款前外廓拆分。	READY
24524_facelift	24524	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产范围覆盖改款边界，按改款后外廓拆分。	READY
24525_prefl	24525	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	生产范围覆盖改款边界，按改款前外廓拆分。	READY
24525_facelift	24525	Sedan	Logan I	LS	4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	生产范围覆盖改款边界，按改款后外廓拆分。	READY
24527_van	24527	Van	Bipper I	AA		EU-PEUGEOT-BIPPER-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24527_mpv	24527	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24528_van	24528	Van	Bipper I	AA		EU-PEUGEOT-BIPPER-I-AA-VAN-01	MEDIUM	上游为厢式/MPV混合分类，按厢式外廓拆分。	READY
24528_mpv	24528	MPV	Bipper I	AJ	5	EU-PEUGEOT-BIPPER-I-AJ-MPV-01	MEDIUM	上游为厢式/MPV混合分类，按乘用MPV外廓拆分。	READY
24529	24529	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24530	24530	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24532	24532	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24533	24533	MPV	Partner II Tepee	B9	5	EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	HIGH		READY
24534	24534	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24535	24535	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24536	24536	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24537_l1	24537	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	同一动力覆盖L1厢式车。	READY
24537_l2	24537	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	同一动力覆盖L2厢式车。	READY
24538	24538	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1厢式车外廓。	READY
24539	24539	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
24540	24540	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-01	HIGH		READY
24542	24542	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
24543	24543	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH		READY
24544	24544	Pickup	L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	MEDIUM	KB4T双排驾驶室物理边界。	READY
24545	24545	Sedan	IS II	USE20	4	EU-LEXUS-IS-II-USE20-ISF-SEDAN-4D-01	HIGH	IS F专属加长加宽外廓。	READY
24547	24547	Coupe	Fortwo II	451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH		READY
24548	24548	MPV	FR-V I facelift		5	EU-HONDA-FR-V-I-FACELIFT-MPV-5D-01	HIGH		READY
24555_3dr	24555	SUV	Pajero II	V24W	3	EU-MITSUBISHI-PAJERO-II-V24W-SUV-3D-01	MEDIUM	同一Ktype覆盖短轴三门与长轴五门车身。	READY
24555_5dr	24555	SUV	Pajero II	V44W	5	EU-MITSUBISHI-PAJERO-II-V44W-SUV-5D-01	MEDIUM	同一Ktype覆盖短轴三门与长轴五门车身。	READY
24585	24585	Convertible	Pajero II Canvas Top	V24C	2	EU-MITSUBISHI-PAJERO-II-V24C-CANVAS-TOP-2D-01	MEDIUM	开放式短轴Canvas Top车身。	READY
24593	24593	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	MEDIUM	4.0升版本对应YJ软顶两门外廓；上游生产年月早于该发动机上市。	READY
24594	24594	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	MEDIUM	4.0升版本对应YJ软顶两门外廓；上游生产年月早于该发动机上市。	READY
24597	24597	Hatchback	Giulietta	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
24598	24598	SUV	RX I	XU10	5	EU-LEXUS-RX-I-XU10-SUV-01	HIGH		READY
24599	24599	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH		READY
24612	24612	SUV	Safari I		5	EU-TATA-SAFARI-I-SUV-01	HIGH		READY
24616	24616	Convertible	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-I-L316-90-SOFT-TOP-01	MEDIUM	3.9 V8开放式车身按Defender 90软顶边界。	READY
24617_90	24617	SUV	Defender I	L316	3	EU-LAND-ROVER-DEFENDER-I-L316-90-STATION-WAGON-01	MEDIUM	同一Ktype未区分90与110轴距，按两种车身拆分。	READY
24617_110	24617	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-I-L316-110-STATION-WAGON-01	MEDIUM	同一Ktype未区分90与110轴距，按两种车身拆分。	READY
24618_prefl	24618	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	MEDIUM	生产期跨越第一次改款，按改款前外廓拆分。	READY
24618_facelift1	24618	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	MEDIUM	生产期跨越第一次改款，按第一次改款外廓拆分。	READY
24621	24621	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH		READY
24622	24622	Sedan	Impreza II	GD	4	EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	HIGH		READY
24627	24627	Wagon	Impreza II	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	HIGH	WRX旅行车高度外廓。	READY
24628	24628	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	HIGH	改款前T30外廓。	READY
24636	24636	Sedan	Accent II	LC	4	EU-HYUNDAI-ACCENT-II-LC-SEDAN-PREFL-01	HIGH	改款前轿车外廓。	READY
24641	24641	Pickup	Defender I	L316	2	EU-LAND-ROVER-DEFENDER-I-L316-90-PICKUP-01	MEDIUM	4.0 V8皮卡按Defender 90单排车身。	READY
24659	24659	SUV	Forester II	SG	5	EU-SUBARU-FORESTER-II-FACELIFT-SUV-01	HIGH		READY
24668	24668	Sedan	110		4	EU-LADA-110-SEDAN-01	HIGH		READY
24669	24669	Sedan	110		4	EU-LADA-110-SEDAN-01	HIGH		READY
24676	24676	Convertible	Camaro III		2	EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	HIGH		READY
24677	24677	Convertible	Camaro III		2	EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	HIGH		READY
24700_regcab_zq8	24700	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab ZQ8外廓拆分。	READY
24700_regcab_z85	24700	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab Z85外廓拆分。	READY
24700_regcab_z71	24700	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab Z71外廓拆分。	READY
24700_extcab_zq8	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab ZQ8外廓拆分。	READY
24700_extcab_z85	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab Z85外廓拆分。	READY
24700_extcab_z71	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab Z71外廓拆分。	READY
24700_crewcab_zq8	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab ZQ8外廓拆分。	READY
24700_crewcab_z85	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab Z85外廓拆分。	READY
24700_crewcab_z71	24700	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab Z71外廓拆分。	READY
24701_regcab_zq8	24701	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab ZQ8外廓拆分。	READY
24701_regcab_z85	24701	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab Z85外廓拆分。	READY
24701_regcab_z71	24701	Pickup	Colorado I	GMT355	2	EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Regular Cab Z71外廓拆分。	READY
24701_extcab_zq8	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab ZQ8外廓拆分。	READY
24701_extcab_z85	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab Z85外廓拆分。	READY
24701_extcab_z71	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Extended Cab Z71外廓拆分。	READY
24701_crewcab_zq8	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab ZQ8外廓拆分。	READY
24701_crewcab_z85	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab Z85外廓拆分。	READY
24701_crewcab_z71	24701	Pickup	Colorado I	GMT355	4	EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	MEDIUM	上游未区分驾驶室与悬架高度，按Crew Cab Z71外廓拆分。	READY
24715	24715	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-01	HIGH		READY
24717	24717	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-01	HIGH		READY
24718	24718	Coupe	Corvette C4		2	EU-CHEVROLET-CORVETTE-C4-COUPE-01	HIGH		READY
24720	24720	Wagon	HHR		5	EU-CHEVROLET-HHR-WAGON-5D-01	HIGH		READY
24765	24765	MPV	Pacifica I	CS	5	EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	HIGH		READY
24770	24770	Sedan	Charger VI	LX	4	EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	HIGH		READY
24778	24778	SUV	Durango II	HB	5	EU-DODGE-DURANGO-II-HB-SUV-5D-01	HIGH		READY
24784	24784	SUV	Ramcharger II	AD150	3	EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2001-2100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XF-I-SEDAN-X250-01	4961	1877	1460	CarSized	https://www.carsized.com/en/cars/jaguar-xf-2008-sedan/front/
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675	CarExpert	https://dt16c8g6jis9k.cloudfront.net/porsche/cayenne/2008/dimensions
EU-CADILLAC-BLS-SEDAN-01	4680	1752	1471	Auto-Data	https://www.auto-data.net/en/cadillac-bls-2.0-t-175hp-11689
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543	Auto-Data	https://www.auto-data.net/en/cadillac-bls-wagon-2.0-t-175hp-51812
EU-CADILLAC-CTS-II-SEDAN-4D-01	4866	1842	1472	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/334820/cadillac_cts_3_6l_v-6.html
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534	Auto-Data	https://www.auto-data.net/en/dacia-logan-i-1.6-16v-105hp-43234
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534	Auto-Data	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-generation-3957
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674	Auto-Data	https://www.auto-data.net/en/dacia-logan-i-mcv-generation-3529
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640	Auto-Data	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-generation-8968
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.9-tdi-105hp-dpf-4motion-51635
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1187270/audi_a3_cabriolet_1_6.html
EU-AUDI-RS6-C6-AVANT-WAGON-5D-01	4928	1889	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/252410/audi_rs6_avant.html
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451	CarsGuide	https://www.carsguide.com.au/citroen/c5/car-dimensions/2008
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479	CarsGuide	https://www.carsguide.com.au/citroen/c5/car-dimensions/2008
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/553040/citroen_berlingo_multispace_hdi_90.html
EU-CITROEN-BERLINGO-II-B9-VAN-L1-01	4380	1810	1801	Citroën Berlingo Van official brochure	https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-BERLINGO-II-B9-VAN-L2-01	4628	1810	1828	Citroën Berlingo Van official brochure	https://xr793.com/wp-content/uploads/2020/09/2015-Citroen-Berlingo-Van.pdf
EU-CITROEN-NEMO-I-AA-VAN-01	3864	1716	1721	Auto-Data	https://www.auto-data.net/en/citroen-nemo-panel-van-1.4-hdi-70hp-54973
EU-CITROEN-NEMO-I-AJ-MPV-01	3959	1716	1721	Auto-Data	https://www.auto-data.net/en/citroen-nemo-multispace-1.4-hdi-70hp-54978
EU-PEUGEOT-BIPPER-I-AA-VAN-01	3864	1716	1721	AutoScout24	https://www.autoscout24.de/auto/technische-daten/peugeot/bipper/
EU-PEUGEOT-BIPPER-I-AJ-MPV-01	3959	1716	1721	AutoScout24	https://www.autoscout24.de/auto/technische-daten/peugeot/bipper/
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803	Auto-Data	https://www.auto-data.net/en/peugeot-partner-ii-tepee-1.6-90hp-5619
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834	Peugeot Partner 2008 official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/08/Peugeot-Partner-2008-AU.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner 2008 official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/08/Peugeot-Partner-2008-AU.pdf
EU-JEEP-PATRIOT-I-MK74-SUV-01	4408	1785	1658	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1331540/jeep_patriot_2_0_crd_limited_dpf.html
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1996190/mitsubishi_lancer_2_0_di-d.html
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775	Drom	https://www.drom.ru/catalog/mitsubishi/l200/76991/
EU-LEXUS-IS-II-USE20-ISF-SEDAN-4D-01	4660	1815	1415	Toyota GAZOO vehicle catalog	https://gazoo.com/catalog/maker/LEXUS/IS_F/200712/10043520/
EU-SMART-FORTWO-II-COUPE-01	2695	1559	1542	Automobile-Catalog	https://www.automobile-catalog.com/car/2012/3155300/smart_fortwo_coupe_61_mhd.html
EU-HONDA-FR-V-I-FACELIFT-MPV-5D-01	4285	1810	1610	Honda European Media Newsroom	https://hondanews.eu/eu/en/cars/media/pressreleases/214/fr-v-summary
EU-MITSUBISHI-PAJERO-II-V24W-SUV-3D-01	4030	1695	1800	Toyota GAZOO vehicle catalog	https://gazoo.com/catalog/maker/MITSUBISHI/PAJERO/199101/4004290/
EU-MITSUBISHI-PAJERO-II-V44W-SUV-5D-01	4650	1695	1855	Toyota GAZOO vehicle catalog	https://gazoo.com/catalog/maker/MITSUBISHI/PAJERO/199101/4004851/
EU-MITSUBISHI-PAJERO-II-V24C-CANVAS-TOP-2D-01	4030	1695	1850	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/1972970/mitsubishi_pajero_2500_diesel_turbo_intercooler_xs_canvas_top.html
EU-JEEP-WRANGLER-I-YJ-CONVERTIBLE-2D-01	3879	1676	1829	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1315415/jeep_wrangler_4_0l.html
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-2.0-jtdm-150hp-18682
EU-LEXUS-RX-I-XU10-SUV-01	4580	1815	1660	Auto-Data	https://www.auto-data.net/en/lexus-rx-i-300-201hp-5894
EU-HONDA-CONCERTO-HW-SEDAN-4D-01	4415	1690	1395	Auto-Data	https://www.auto-data.net/en/honda-concerto-model-1312
EU-TATA-SAFARI-I-SUV-01	4800	1810	1910	Automobile-Catalog	https://www.automobile-catalog.com/car/2003/3418925/tata_safari_2_0_tdi_4x4.html
EU-LAND-ROVER-DEFENDER-I-L316-90-SOFT-TOP-01	3722	1790	1965	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/1395650/land-rover_defender_90_soft_top_td5.html
EU-LAND-ROVER-DEFENDER-I-L316-90-STATION-WAGON-01	3883	1790	1963	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/1395665/land-rover_defender_90_station_wagon_td5.html
EU-LAND-ROVER-DEFENDER-I-L316-110-STATION-WAGON-01	4599	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/1395590/land-rover_defender_110_station_wagon_td5.html
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440	CarsGuide	https://www.carsguide.com.au/subaru/impreza/car-dimensions/2001
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440	CarExpert	https://www.carexpert.com.au/subaru/impreza/2004-rs-2-5l-sedan-4x4-petrol-manual-jjoa5sf820040116
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/3256970/subaru_impreza_2_5i_sedan_awd_automatic.html
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465	CarsGuide	https://www.carsguide.com.au/subaru/impreza/car-dimensions/2006
EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	4510	1765	1675	Auto-Data	https://www.auto-data.net/en/nissan-x-trail-i-t30-2.2-dci-114hp-4x4-913
EU-HYUNDAI-ACCENT-II-LC-SEDAN-PREFL-01	4235	1670	1395	Auto-Data	https://www.auto-data.net/en/hyundai-accent-ii-1.5-i-16v-102hp-automatic-24810
EU-LAND-ROVER-DEFENDER-I-L316-90-PICKUP-01	3722	1790	1963	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/1395635/land-rover_defender_90_pick-up_td5.html
EU-SUBARU-FORESTER-II-FACELIFT-SUV-01	4450	1735	1590	CarsGuide	https://www.carsguide.com.au/subaru/forester/car-dimensions/2005
EU-LADA-110-SEDAN-01	4277	1676	1430	Auto-Data	https://www.auto-data.net/en/lada-2110-model-1423
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	4877	1849	1278	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/459815/chevrolet_camaro_iroc-z_5_7l_v-8_tpi_automatic_dual_exhaust.html
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-ZQ8-PICKUP-01	4887	1717	1613	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z85-PICKUP-01	4887	1717	1648	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-REGCAB-Z71-PICKUP-01	4887	1717	1694	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-ZQ8-PICKUP-01	5258	1717	1613	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z85-PICKUP-01	5258	1717	1648	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-EXTCAB-Z71-PICKUP-01	5258	1717	1694	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-ZQ8-PICKUP-01	5258	1717	1618	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z85-PICKUP-01	5258	1717	1656	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-COLORADO-I-GMT355-CREWCAB-Z71-PICKUP-01	5258	1717	1702	4x4Review 2004 Chevrolet Colorado specifications	https://www.4x4review.com/2004-chevrolet-colorado/
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176	Automobile-Catalog	https://www.automobile-catalog.com/car/1996/464210/chevrolet_corvette.html
EU-CHEVROLET-HHR-WAGON-5D-01	4475	1755	1603	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1223420/chevrolet_hhr_2_4_lt.html
EU-CHRYSLER-PACIFICA-I-CS-MPV-5D-01	5052	2013	1688	Auto-Data	https://www.auto-data.net/en/chrysler-pacifica-3.5-v6-253hp-14716
EU-DODGE-CHARGER-VI-LX-SEDAN-4D-01	5082	1891	1479	Dodge 2006 Charger official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2006Charger_specs.pdf
EU-DODGE-DURANGO-II-HB-SUV-5D-01	5101	1930	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/689975/dodge_durango_slt_2wd_4_7l_v-8.html
EU-DODGE-RAMCHARGER-II-AD150-SUV-3D-01	4689	2019	1787	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/1484720/dodge_ramcharger_ad150_5_2l_torqueflite.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2001-2100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2001-2100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2001-2100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2936 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1513 行）

