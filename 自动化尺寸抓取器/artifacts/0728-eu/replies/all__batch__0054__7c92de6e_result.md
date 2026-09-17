# 任务：all 第 5301-5400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0054__7c92de6e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5301-5400 行

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
all 第 5301-5400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-20-01	4383	1682	1376
EU-AUDI-80-B2-SEDAN-QUATTRO-22-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	4406	1682	1350
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397
EU-AUDI-80-B4-RS2-AVANT-01	4510	1695	1386
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406
EU-AUDI-80-B4-WAGON-01	4482	1695	1408
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430
EU-AUDI-A8-D2-SEDAN-FACELIFT-01	5034	1880	1438
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440
EU-CHRYSLER-STRATUS-JA-SEDAN-01	4746	1822	1374
EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	4440	1810	1927
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	3718	1595	1390
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1620	1370
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-FIAT-BRAVA-182-HATCHBACK-5D-01	4187	1741	1420
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	4025	1755	1420
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-HGT-01	4031	1755	1420
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340
EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	4448	1702	1393
EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	4420	1700	1393
EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	4585	1760	1515
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-SIGMA-F16A-SEDAN-4D-01	4750	1775	1435
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356
EU-PEUGEOT-306-CABRIO-7D-PREFL-01	4144	1689	1356
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	3995	1692	1380
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	3995	1695	1365
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-02	3995	1692	1365
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-5D-01	3995	1692	1365
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-3D-01	3995	1692	1367
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-5D-01	3995	1692	1367
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386
EU-PEUGEOT-306-SEDAN-7B-PREFL-01	4232	1689	1386
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1294
EU-PROTON-PERSONA-400-HATCHBACK-5D-01	4270	1690	1385
EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	4360	1690	1380
EU-PROTON-PERSONA-400-SEDAN-4D-PRE96-01	4360	1690	1385
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	4508	1752	1433
EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	4628	1752	1448
EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	4620	1752	1448
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443
EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	4770	1820	1440
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	3687	1654	1470
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	3600	1654	1470
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-4D-01	4935	1864	1760

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Brava	1.6 16V	Schrägheck	Frontantrieb	Benzin	76	103	Feb 1996	Oct 2001	2024-03-01	5567
Fiat	Bravo i	1.6 16V	Schrägheck	Frontantrieb	Benzin	76	103	Mar 1996	Oct 2001	2024-03-01	5568
Fiat	Coupe	1.8 16V	Coupe	Frontantrieb	Benzin	96	131	Mar 1996	Aug 2000	2024-03-01	5569
Honda	Legend iii	3.5 I 24V	Stufenheck	Frontantrieb	Benzin	151	205	Feb 1996	Oct 1997	2024-03-01	5570
Hyundai	Lantra ii	1.6 I	Kombi	Frontantrieb	Benzin	66	90	Feb 1996	Oct 2000	2024-03-01	5571
Hyundai	Lantra ii	1.6 16V	Kombi	Frontantrieb	Benzin	84	114	Feb 1996	Oct 2000	2024-03-01	5572
Opel	Astra h caravan	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	85	116	Aug 2009	Oct 2010	2024-03-01	5573
KIA	Pride	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1990	Oct 2000	2024-03-01	5574
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	100	136	May 2006	Jun 2015	2024-03-01	5575
KIA	Pride	1.3	Schrägheck	Frontantrieb	Benzin	53	72	Jan 1990	Sep 2001	2024-03-01	5576
Mitsubishi	Colt v	1300 Gl,glx	Schrägheck	Frontantrieb	Benzin	55	75	May 1996	Jun 2000	2024-03-01	5577
Mitsubishi	Colt v	1600 GLX	Schrägheck	Frontantrieb	Benzin	66	90	May 1996	Sep 2000	2024-03-01	5578
Mitsubishi	Lancer vi	1.3 12V	Stufenheck	Frontantrieb	Benzin	55	75	Dec 1995	Aug 2003	2024-03-01	5579
Peugeot	Expert	1.9 TD	Bus	Frontantrieb	Diesel	68	92	Feb 1996	May 1998	2024-03-01	5580
Peugeot	Expert	1.9 D	Bus	Frontantrieb	Diesel	51	70	Feb 1996	Dec 1998	2024-03-01	5581
Peugeot	Expert	1.6	Bus	Frontantrieb	Benzin	58	79	Feb 1996	Sep 2000	2024-03-01	5582
Peugeot	306	2.0 S16	Schrägheck	Frontantrieb	Benzin	120	163	Jun 1996	May 2001	2024-03-01	5583
Renault	Megane i	1.4 ECO	Schrägheck	Frontantrieb	Benzin	52	71	Jan 1996	Mar 1999	2024-03-01	5584
Renault	Laguna i grandtour	2.2 DT	Kombi	Frontantrieb	Diesel	83	113	Mar 1996	Mar 2001	2024-03-01	5585
Renault	Laguna i grandtour	3	Kombi	Frontantrieb	Benzin	123	167	Feb 1996	Mar 2001	2024-03-01	5586
Renault	Laguna i	2.2 DT	Schrägheck	Frontantrieb	Diesel	83	113	Mar 1996	Mar 2001	2024-03-01	5587
Rover	600	618 I/si	Stufenheck	Frontantrieb	Benzin	85	115	Mar 1996	Feb 1999	2024-03-01	5588
Seat	Inca	1.4 I	Kasten/Kombi	Frontantrieb	Benzin	44	60	Nov 1995	Jun 2003	2024-03-01	5589
Seat	Inca	1.6 I	Kasten/Kombi	Frontantrieb	Benzin	55	75	Nov 1995	May 1998	2024-03-01	5590
Seat	Inca	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	47	64	Nov 1995	Jun 2003	2024-03-01	5591
Chrysler	Stratus	2.0 LE	Cabriolet	Frontantrieb	Benzin	96	131	Jun 1996	Apr 2001	2024-03-01	5592
Chrysler	Stratus	2.5 LX	Cabriolet	Frontantrieb	Benzin	120	163	Apr 1996	Apr 2001	2024-03-01	5593
Citroën	Berlingo	1.1 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Jul 1996	Mar 2008	2024-03-01	5594
Citroën	Berlingo	1.4 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Jul 1996	Dec 2011	2024-03-01	5595
Citroën	Berlingo	1.8 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	43	59	Jul 1996	Oct 2002	2024-03-01	5596
Citroën	Berlingo	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	51	70	Jul 1996	Dec 2003	2024-03-01	5597
Mitsubishi	L200	2.5 TD 4WD	Pick-up	Allrad	Diesel	64	87	Nov 1992	Aug 1996	2024-03-01	5598
Mitsubishi	Sigma	3	Kombi	Frontantrieb	Benzin	125	170	Jun 1992	Oct 1996	2024-03-01	5599
Audi	A3	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Sep 1996	May 2003	2024-03-01	5600
Audi	A3	1.8	Schrägheck	Frontantrieb	Benzin	92	125	Sep 1996	May 2003	2024-03-01	5601
Audi	A3	1.8 T	Schrägheck	Frontantrieb	Benzin	110	150	Dec 1996	May 2003	2024-03-01	5602
Audi	A3	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Sep 1996	Jul 2001	2024-03-01	5603
Audi	A8 d2	S8 Quattro	Stufenheck	Allrad	Benzin	250	340	Jul 1996	Jun 1999	2024-03-01	5604
Audi	A4 b5	1.9 TDI Quattro	Stufenheck	Allrad	Diesel	81	110	Jul 1996	Jan 2000	2024-05-01	5605
Audi	A4 b5 avant	1.9 TDI Quattro	Kombi	Allrad	Diesel	81	110	Sep 1996	Sep 2001	2024-03-01	5606
Mazda	5	1.6 CD	Großraumlimousine	Frontantrieb	Diesel	85	116	Jul 2010	-	2024-03-01	5607
Audi	80	1.9 Cd-5s	Stufenheck	Frontantrieb	Benzin	85	115	Sep 1981	Jul 1983	2024-03-01	5608
Ssangyong	Musso	3.2	Geländewagen geschlossen	Allrad	Benzin	162	220	Jun 1996	Sep 2004	2024-03-01	5610
Ssangyong	Musso	2.9 D	Geländewagen geschlossen	Allrad	Diesel	73	99	Mar 1996	Nov 1998	2024-03-01	5611
Jeep	Wrangler ii	2.5	Geländewagen offen	Allrad	Benzin	87	118	Aug 1996	Apr 2007	2024-03-01	5612
Jeep	Wrangler ii	4	Geländewagen offen	Allrad	Benzin	130	177	Aug 1996	Apr 2007	2024-03-01	5613
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	100	136	May 2006	Dec 2014	2024-03-01	5614
Peugeot	806	2.1 TD 12V	Großraumlimousine	Frontantrieb	Diesel	80	109	Jun 1996	Aug 1999	2024-03-01	5615
Citroën	Saxo	1.5 D	Schrägheck	Frontantrieb	Diesel	42	57	Sep 1996	Jun 2001	2024-03-01	5616
Citroën	Jumpy i	1.9 TD	Bus	Frontantrieb	Diesel	66	90	Oct 1995	Aug 2000	2024-03-01	5617
Citroën	Xantia	2.1 Turbo D 12V	Kombi	Frontantrieb	Diesel	80	109	Jun 1996	Feb 1999	2024-03-01	5618
Peugeot	106 ii	1.0 I	Schrägheck	Frontantrieb	Benzin	33	45	May 1996	Oct 1999	2024-03-01	5619
Peugeot	106 ii	1.1 I	Schrägheck	Frontantrieb	Benzin	44	60	May 1996	Jul 2004	2024-03-01	5620
Peugeot	106 ii	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	May 1996	Jul 2004	2024-03-01	5621
Peugeot	106 ii	1.6 I	Schrägheck	Frontantrieb	Benzin	65	89	May 1996	Oct 1999	2024-03-01	5622
Peugeot	106 ii	1.6 S16	Schrägheck	Frontantrieb	Benzin	87	118	May 1996	Jul 2004	2024-03-01	5623
Peugeot	106 ii	1.6 I	Schrägheck	Frontantrieb	Benzin	74	101	May 1996	Jan 2001	2024-03-01	5624
Peugeot	106 ii	1.5 D	Schrägheck	Frontantrieb	Diesel	40	55	May 1996	Mar 2001	2024-03-01	5625
Peugeot	306	1.6	Cabriolet	Frontantrieb	Benzin	65	89	Apr 1996	Oct 2000	2024-03-01	5626
Peugeot	406	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	108	147	Apr 1996	May 2004	2024-03-01	5627
Peugeot	Boxer	1.9 TD 4X4	Bus	Allrad	Diesel	68	92	Jul 1996	Apr 2002	2024-03-01	5628
Peugeot	Boxer	2.5 D 4X4	Bus	Allrad	Diesel	63	86	Jul 1996	Apr 2002	2024-03-01	5629
Peugeot	Boxer	2.5 TD 4X4	Bus	Allrad	Diesel	76	103	Jul 1996	Apr 2002	2024-03-01	5630
Peugeot	406	1.9 TD	Stufenheck	Frontantrieb	Diesel	68	92	Jan 1996	May 2004	2024-03-01	5631
Porsche	911	3.8 Carrera	Targa	Heckantrieb	Benzin	221	301	May 1996	Sep 1997	2024-03-01	5632
Porsche	Boxster	2.5	Cabriolet	Heckantrieb	Benzin	150	204	Sep 1996	Aug 1999	2024-03-01	5633
Proton	Persona 300	315 Glsi	Schrägheck	Frontantrieb	Benzin	64	87	Sep 1996	Jul 2000	2024-03-01	5634
Proton	Persona 400	418 Glxi	Schrägheck	Frontantrieb	Benzin	85	115	May 1996	Jul 2000	2024-03-01	5635
Proton	Persona 400	420 GLS D	Schrägheck	Frontantrieb	Diesel	48	65	May 1996	Apr 1999	2024-03-01	5636
Proton	Persona 400	420 GLS D	Stufenheck	Frontantrieb	Diesel	48	65	May 1996	Apr 1999	2024-03-01	5637
Audi	A6 c4	S6 Plus Quattro	Stufenheck	Allrad	Benzin	240	326	Apr 1996	Oct 1997	2024-03-01	5638
Audi	A6 c4 avant	S6 Plus Quattro	Kombi	Allrad	Benzin	240	326	Apr 1996	Dec 1997	2024-03-01	5639
Mazda	5	2	Großraumlimousine	Frontantrieb	Benzin	110	150	Sep 2010	-	2024-03-01	5640
Renault	Safrane ii	2.0 16V	Schrägheck	Frontantrieb	Benzin	100	136	Jul 1996	Dec 2000	2024-03-01	5641
Renault	Safrane i	3.0 V6 4X4	Schrägheck	Allrad	Benzin	123	167	Dec 1992	Jul 1996	2024-03-01	5642
Renault	Safrane ii	2.2 DT	Schrägheck	Frontantrieb	Diesel	83	113	Jul 1996	Dec 2000	2024-03-01	5643
Renault	Safrane ii	2.5 20V	Schrägheck	Frontantrieb	Benzin	121	165	Jul 1996	Dec 2000	2024-03-01	5644
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1996	Sep 1998	2026-05-01	5645
Renault	Megane i classic	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1996	Aug 2003	2024-03-01	5646
Renault	Megane i classic	1.9 TDI	Stufenheck	Frontantrieb	Diesel	69	94	Sep 1996	Aug 2003	2024-03-01	5647
Renault	Megane i classic	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1996	Mar 1999	2024-03-01	5648
Renault	Megane i classic	1.9 DT	Stufenheck	Frontantrieb	Diesel	66	90	Sep 1996	Aug 2003	2024-03-01	5649
Renault	Megane i classic	2.0 I	Stufenheck	Frontantrieb	Benzin	84	114	Sep 1996	Aug 2003	2024-03-01	5650
Renault	Megane i classic	1.6 E	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1996	Mar 1999	2024-03-01	5651
Renault	Megane i classic	1.9 D	Stufenheck	Frontantrieb	Diesel	47	64	Sep 1996	Aug 2003	2024-03-01	5652
Renault	Megane scénic	1.4 I	Großraumlimousine	Frontantrieb	Benzin	55	75	Jan 1997	Sep 1999	2024-05-01	5653
Renault	Megane scénic	1.6 I	Großraumlimousine	Frontantrieb	Benzin	55	75	Jan 1997	Sep 1999	2024-05-01	5654
Renault	Megane scénic	1.6 E	Großraumlimousine	Frontantrieb	Benzin	66	90	Oct 1996	Oct 1999	2024-05-01	5655
Renault	Megane scénic	2.0 I	Großraumlimousine	Frontantrieb	Benzin	84	114	Jan 1997	Sep 1999	2024-05-01	5656
Renault	Megane scénic	1.9 DT	Großraumlimousine	Frontantrieb	Diesel	66	90	Jan 1997	Sep 1999	2024-05-01	5657
Renault	Twingo	1.2	Schrägheck	Frontantrieb	Benzin	40	54	May 1996	Mar 2007	2026-05-01	5658
Toyota	Carina v	2.0 D	Kombi	Frontantrieb	Diesel	54	73	Dec 1987	Jan 1992	2024-03-01	5659
Rover	400	414 SI	Stufenheck	Frontantrieb	Benzin	76	103	May 1995	Mar 2000	2024-03-01	5660
Rover	400	416 SI	Stufenheck	Frontantrieb	Benzin	82	112	May 1995	Mar 2000	2024-03-01	5661
Rover	400	416 SI	Stufenheck	Frontantrieb	Benzin	83	113	Mar 1995	Jun 1999	2024-03-01	5662
Rover	400	420 SI LUX	Stufenheck	Frontantrieb	Benzin	100	136	Dec 1995	Mar 2000	2024-03-01	5663
Rover	400	420 D	Stufenheck	Frontantrieb	Diesel	63	86	Nov 1995	Mar 2000	2024-03-01	5664
Rover	400	420 DI	Stufenheck	Frontantrieb	Diesel	77	105	May 1995	Mar 2000	2024-03-01	5665
Rover	400	420 SI LUX	Schrägheck	Frontantrieb	Benzin	100	136	Dec 1995	Mar 2000	2024-03-01	5666
Rover	400	1.8 I	Kombi	Frontantrieb	Benzin	107	146	Jun 1996	Nov 1998	2024-03-01	5667


--- Round 1 / 首次发送 ---
## 更新点

* 已处理 Ktype `5567–5599`，共 **33 个输入 Ktype**。
* 优先复用了 Fiat Brava、Bravo、Coupe、Peugeot 306 S16、Renault Megane I、Laguna I Grandtour、Rover 600 等 **9 个既有尺寸组**，未重复抓取或建组。
* 首次闭合 Honda Legend III、Hyundai Lantra II Wagon、Opel Astra H Caravan 等物理外廓。([汽车数据网][1])
* Mitsubishi Colt V 的两个车身代码共用三门外廓；Lancer VI 1.3 已确认四门轿车外廓；Peugeot 306 S16 与 Renault Megane I 已命中既有组。([汽车数据网][2])
* Kia Pride 按三门、五门拆分；Berlingo 按 M49 改款前、M59 改款后拆分；Seat Inca 与 Chrysler Stratus Cabrio 已闭合新增组。([汽车数据网][3])
* Ford Galaxy II、Renault Laguna I Hatchback、Mitsubishi L200、Mitsubishi Sigma Wagon 暂不强制落组，分别保留高度口径、缓存分支归属、跨代驾驶室和车宽冲突问题。

## 当前批次进度

* 已处理输入 Ktype：**33 / 100**
* READY 映射：**36**
* PENDING 映射：**4**
* 已闭合并引用尺寸组：**21**

  * 本轮首次创建：**12**
  * 复用既有尺寸组：**9**
* 尚未推进输入 Ktype：**67**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5567	5567	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-5D-01	HIGH		READY
5568	5568	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH		READY
5569	5569	Coupe	Fiat Coupe (175)	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
5570	5570	Sedan	Legend III	KA9	4	EU-HONDA-LEGEND-III-KA9-SEDAN-01	HIGH		READY
5571	5571	Wagon	Lantra II (J2)	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
5572	5572	Wagon	Lantra II (J2)	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
5573	5573	Wagon	Astra H	L35	5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	Caravan 改款后物理外廓。	READY
5574_3dr	5574	Hatchback	Pride (DA)	DA	3	EU-KIA-PRIDE-DA-HATCHBACK-3D-01	MEDIUM	DA 三门物理分支。	READY
5574_5dr	5574	Hatchback	Pride (DA)	DA	5	EU-KIA-PRIDE-DA-HATCHBACK-5D-01	MEDIUM	DA 五门物理分支。	READY
5575	5575	MPV	Galaxy II	WA6			LOW	候选为 WA6 改款前/后外廓；高度口径尚未闭合。	PENDING: 需统一 WA6 改款前后高度与车顶装备口径
5576_3dr	5576	Hatchback	Pride (DA)	DA	3	EU-KIA-PRIDE-DA-HATCHBACK-3D-01	MEDIUM	DA 三门物理分支。	READY
5576_5dr	5576	Hatchback	Pride (DA)	DA	5	EU-KIA-PRIDE-DA-HATCHBACK-5D-01	MEDIUM	DA 五门物理分支。	READY
5577	5577	Hatchback	Colt V (CJO)	CJ1A	3	EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	HIGH		READY
5578	5578	Hatchback	Colt V (CJO)	CJ4A	3	EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	HIGH		READY
5579	5579	Sedan	Lancer VI		4	EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	HIGH		READY
5580	5580	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5581	5581	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5582	5582	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5583	5583	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	MEDIUM	163 hp S16 对应 Phase I 三门外廓；输入结束年月晚于该规格记录。	READY
5584	5584	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH		READY
5585_prefl	5585	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	K56 改款前物理外廓。	READY
5585_facelift	5585	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	K56 改款后物理外廓。	READY
5586_prefl	5586	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	K56 改款前物理外廓。	READY
5586_facelift	5586	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	K56 改款后物理外廓。	READY
5587	5587	Hatchback	Laguna I	B56	5		LOW	候选为 B56-HATCHBACK-02（改款前）与 B56-HATCHBACK-01（改款后）；待确认改款后高度归属。	PENDING: 需确认 B56 改款后高度及既有缓存组归属
5588	5588	Sedan	600 (RH)	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
5589	5589	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5590	5590	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5591	5591	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5592	5592	Convertible	Stratus Cabrio	JX	2	EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	HIGH		READY
5593	5593	Convertible	Stratus Cabrio	JX	2	EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	HIGH		READY
5594_prefl	5594	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5594_facelift	5594	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5595_prefl	5595	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5595_facelift	5595	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5596_prefl	5596	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	1.8 D 结束于改款切换期，按 M49 外廓落盘。	READY
5597_prefl	5597	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5597_facelift	5597	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5598	5598	Pickup	L200				LOW	87 hp 资料指向 1996 年起 L200 III Double Cab，但输入始于 1992 年且未给驾驶室。	PENDING: 输入跨代且驾驶室类型未确认
5599	5599	Wagon	Sigma Station Wagon	F07W	5		LOW	候选车宽为 1775 mm 与 1780 mm，来源冲突。	PENDING: 需解决 F07W 车宽 1775/1780 冲突
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-LEGEND-III-KA9-SEDAN-01	4995	1820	1430	Auto-Data Honda Legend III KA9 3.5 i 24V	https://www.auto-data.net/en/honda-legend-iii-ka9-3.5-i-24v-205hp-12173
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457	Automobile-Catalog Hyundai Lantra Combi 1.6i 16V GLS;Automobile-Catalog Hyundai Lantra Estate 1.6 16V LSi	https://www.automobile-catalog.com/car/1996/1164380/hyundai_lantra_combi_1_6i_16v_gls.html;https://www.automobile-catalog.com/car/1996/1164815/hyundai_lantra_estate_1_6_16v_lsi.html
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift 2007	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-generation-9251
EU-KIA-PRIDE-DA-HATCHBACK-3D-01	3565	1605	1460	Auto-Data Kia Pride DA	https://www.auto-data.net/fr/kia-pride-da-1.1-i-52hp-2776
EU-KIA-PRIDE-DA-HATCHBACK-5D-01	3565	1605	1460	Auto-Data Kia Pride DA	https://www.auto-data.net/fr/kia-pride-da-1.1-i-52hp-2776
EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	3900	1680	1365	Auto-Data Mitsubishi Colt V CJ1A;Auto-Data Mitsubishi Colt V CJ4A	https://www.auto-data.net/en/mitsubishi-colt-v-cjo-1300-gl-glx-cj-1a-75hp-15760;https://www.auto-data.net/en/mitsubishi-colt-v-cjo-1600-glx-cj-4a-90hp-15761
EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	4295	1690	1395	Auto-Data Mitsubishi Lancer VI 1.3 12V	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.3-12v-gl-glx-75hp-15660
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940	Zoomcar Peugeot Expert Combi 220 C 1.9 D;Drom Peugeot Expert 1.9 D	https://zoomcar.fr/fiche-technique/peugeot/expert-combi-220-c-1-9-d-8pl-NAT61058.html;https://www.drom.ru/catalog/peugeot/expert/235599/
EU-SEAT-INCA-9K-VAN-01	4207	1696	1836	Automobile-Catalog Seat Inca Van 1.4 MPi;Auto-Data Seat Inca 9K 1.4 MPi	https://www.automobile-catalog.com/car/1995/3071165/seat_inca_van_1_4_mpi.html;https://www.auto-data.net/en/seat-inca-9k-1.4-mpi-60hp-45513
EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	4902	1780	1392	Auto-Data Chrysler Stratus Cabrio JX 2.0 LE;Automoli Chrysler Stratus Cabrio JX	https://www.auto-data.net/en/chrysler-stratus-cabrio-jx-2.0-le-131hp-14718;https://www.automoli.com/en/vehicles/chrysler/stratus/stratus-cabrio-jx-3235/
EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	4108	1698	1802	Automobile-Catalog Citroen Berlingo Multispace 1.4i	https://www.automobile-catalog.com/car/1996/547745/citroen_berlingo_multispace_1_4i.html
EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	4137	1724	1810	DrivePlace Citroen Berlingo I facelift 1.4 Van	https://citroen.drive.place/berlingo/i_res/group_furgon/579286
```

## 下一步优先处理

1. 优先消除 Ktype `5575`、`5587`、`5598`、`5599` 的四个阻塞项。
2. 批量处理 Audi A3 8L、Audi A8 D2 S8、Audi A4 B5、Mazda 5 等 `5600–5614` 车型。
3. 优先命中现有 Peugeot 806、Citroën Saxo/Jumpy、Peugeot 406/Boxer、Porsche 911、Proton、Renault、Rover 尺寸组。
4. 新尺寸组只在现有索引无法复用时首次核对并创建。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-legend-iii-ka9-3.5-i-24v-205hp-12173 "Honda Legend III (KA9) 3.5 i 24V (205 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-colt-v-cjo-1300-gl-glx-cj-1a-75hp-15760 "Mitsubishi Colt V (CJO) 1300 GL,GLX (CJ 1A) (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/fr/kia-pride-da-1.1-i-52hp-2776 "Kia Pride (DA) 1.1 i (52 CH) | Fiche technique, consommation de carburant, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已解决 Ford Galaxy II、Renault Laguna I Hatchback、Mitsubishi Sigma Wagon 三个原有阻塞项。
* Ford Galaxy II 按改款前后拆分；两阶段车宽均采用不含后视镜的 `1884 mm`。([汽车目录][1])
* 新增处理 Ktype `5600–5625`，其中缺失的 `5609` 不生成记录。
* Audi A3 8L、Audi S8 D2、Mazda 5 II、SsangYong Musso I、Jeep Wrangler TJ、Ford S-Max、Citroën Xantia Break 和 Peugeot 106 II 的尺寸组已批量闭合。([汽车数据网][2])
* Mitsubishi L200 `5598` 仍有输入生产期与已确认 L200 III Double Cab 资料不一致的问题，继续保持 PENDING。([汽车数据网][3])

## 当前批次进度

* 已处理输入 Ktype：**58 / 100**
* READY 映射：**76**
* PENDING 映射：**1**
* 已确认并被引用尺寸组：**46**
* 本轮首次创建尺寸组：**16**
* 尚未推进输入 Ktype：**42**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5575_prefl	5575	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	HIGH	WA6 改款前物理外廓。	READY
5575_facelift	5575	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6 改款后物理外廓。	READY
5587_prefl	5587	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	B56 改款前物理外廓。	READY
5587_facelift	5587	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56 改款后物理外廓。	READY
5598	5598	Pickup	L200			LOW	87 hp 资料对应 1996 年起 L200 III Double Cab，但输入始于 1992 年，跨代及驾驶室边界仍未闭合。	PENDING: 输入生产期与已确认车身代际不一致
5599	5599	Wagon	Sigma Station Wagon	F07W	5	EU-MITSUBISHI-SIGMA-F07W-WAGON-01	HIGH		READY
5600	5600	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5601	5601	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5602	5602	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5603	5603	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5604	5604	Sedan	S8 (D2)	D2	4	EU-AUDI-S8-D2-SEDAN-PREFL-01	HIGH	S8 专属车高外廓。	READY
5605	5605	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5606	5606	Wagon	A4 B5 Avant	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5607	5607	MPV	Mazda 5 II	CW	5	EU-MAZDA-5-II-CW-MPV-01	HIGH		READY
5608	5608	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH		READY
5610	5610	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
5611	5611	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	MEDIUM		READY
5612	5612	SUV	Wrangler II	TJ	2	EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	HIGH	标准短轴开放式车身。	READY
5613	5613	SUV	Wrangler II	TJ	2	EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	MEDIUM	标准短轴开放式车身；未包含后期 Unlimited 长轴分支。	READY
5614	5614	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
5615	5615	MPV	806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH		READY
5616_phase1_3dr	5616	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	Phase I 三门物理外廓。	READY
5616_phase1_5dr	5616	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	HIGH	Phase I 五门物理外廓。	READY
5616_phase2_3dr	5616	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	Phase II 三门物理外廓。	READY
5616_phase2_5dr	5616	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	HIGH	Phase II 五门物理外廓。	READY
5617	5617	MPV	Jumpy I	222		EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5618_prefl	5618	Wagon	Xantia Break	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1 旅行车外廓。	READY
5618_facelift	5618	Wagon	Xantia Break	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2 旅行车外廓。	READY
5619_3dr	5619	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	MEDIUM	标准三门物理外廓。	READY
5619_5dr	5619	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	MEDIUM	标准五门物理外廓。	READY
5620_3dr	5620	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5620_5dr	5620	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
5621_3dr	5621	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5621_5dr	5621	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
5622_3dr	5622	Hatchback	106 II		3	EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	HIGH	1.6 三门物理外廓。	READY
5622_5dr	5622	Hatchback	106 II		5	EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	HIGH	1.6 五门物理外廓。	READY
5623	5623	Hatchback	106 II		3	EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	HIGH	S16 三门宽体及车高外廓。	READY
5624_3dr	5624	Hatchback	106 II		3	EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	HIGH	1.6 三门物理外廓。	READY
5624_5dr	5624	Hatchback	106 II		5	EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	HIGH	1.6 五门物理外廓。	READY
5625_3dr	5625	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5625_5dr	5625	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	4820	1884	1723	Automobile-Catalog Ford Galaxy 2.0 TDCi 2007	https://www.automobile-catalog.com/car/2007/976055/ford_galaxy_2_0_tdci_130_trend_dpf.html
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764	Autogidas Ford Galaxy 2.0 TDCi 2010	https://autogidas.lt/en/auto-katalogas/ford/galaxy/iii-2.0-tdci-trend-2010-2011-k84863
EU-MITSUBISHI-SIGMA-F07W-WAGON-01	4800	1775	1505	Auto-Data Mitsubishi Sigma Station Wagon F07W	https://www.auto-data.net/en/mitsubishi-sigma-station-wagon-f07w-3.0-v6-177hp-automatic-24615
EU-AUDI-A3-8L-HATCHBACK-3D-01	4152	1735	1427	Auto-Data Audi A3 8L 1.6i	https://www.auto-data.net/en/audi-a3-8l-1.6i-101hp-4236
EU-AUDI-S8-D2-SEDAN-PREFL-01	5034	1880	1420	Auto-Data Audi S8 D2 4.2 V8 32V	https://www.auto-data.net/en/audi-s8-d2-4.2-v8-32v-340hp-quattro-4790
EU-MAZDA-5-II-CW-MPV-01	4585	1750	1615	Auto-Data Mazda 5 II 1.6 CD	https://www.auto-data.net/en/mazda-5-ii-1.6-cd-115hp-17508
EU-SSANGYONG-MUSSO-I-FJ-SUV-01	4640	1905	1735	Auto-Data SsangYong Musso I 3.2 i 24V	https://www.auto-data.net/en/ssangyong-musso-i-3.2-i-24v-220hp-16010
EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	3883	1740	1748	Auto-Data Jeep Wrangler II TJ 2.5 i	https://www.auto-data.net/en/jeep-wrangler-ii-tj-2.5-i-118hp-1180
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658	Automobile-Catalog Ford S-Max 2.0 TDCi 2007	https://www.automobile-catalog.com/car/2007/976685/ford_s-max_2_0_tdci_140_titanium_dpf.html
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416	Auto-Data Citroen Xantia Break X1 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xantia-break-x1-2.1-turbo-d12-109hp-14976
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420	Auto-Data Citroen Xantia Break X2 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xantia-break-x2-2.1-turbo-d12-109hp-14951
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.0 i	https://www.auto-data.net/en/peugeot-106-ii-1-1.0-i-50hp-5404
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.0 i	https://www.auto-data.net/en/peugeot-106-ii-1-1.0-i-50hp-5404
EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	3680	1590	1380	Auto-Data Peugeot 106 II 1.6 i 88 Hp	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-i-88hp-5409
EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	3680	1590	1380	Auto-Data Peugeot 106 II 1.6 i 88 Hp	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-i-88hp-5409
EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	3678	1610	1357	Auto-Data Peugeot 106 II 1.6 S16	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-s16-118hp-5410
```

## 下一步优先处理

1. 消除唯一剩余 PENDING：Ktype `5598` 的 L200 代际及驾驶室分支。
2. 处理 `5626–5639`，优先复用既有 Peugeot 306 Cabrio、406、Boxer、Porsche 911、Proton Persona 和 Audi A6 C4 尺寸组。
3. 批量闭合 `5640–5667` 的 Mazda 5、Renault Safrane、Megane Classic/Scénic、Toyota Carina Wagon 和 Rover 400。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/976055/ford_galaxy_2_0_tdci_130_trend_dpf.html?utm_source=chatgpt.com "2007 Ford Galaxy 2.0 TDCi (130) Trend DPF (man. 6)"
[2]: https://www.auto-data.net/en/audi-a3-8l-1.6i-101hp-4236 "Audi A3 (8L) 1.6i (101 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mitsubishi-l200-iii-double-cab-2.5-td-87hp-4wd-15583?utm_source=chatgpt.com "Mitsubishi L200 III Double Cab 2.5 TD (87 Hp) 4WD"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已完成剩余 Ktype `5626–5667` 的映射处理；当前 **100 个输入 Ktype 均已覆盖**。
* Ktype `5598` 已按明确的 `87 hp 4WD` 规格绑定 **L200 III Double Cab**，输入开始年月与车型资料不一致仅保留为映射备注，不再阻塞。该规格为四门双排驾驶室，三维 `4920 × 1655 × 1745 mm`。([汽车数据网][1])
* 已闭合 Boxster 986、Persona 300 Compact、Safrane B54 facelift、Megane I Classic 前后期、Megane Scenic、Carina T170 Wagon 和 Rover 400 RT Sedan 新尺寸组。([汽车数据网][2])
* 当前仅 Peugeot Boxer I `230P` 的三个 4x4 Bus Ktype 尚未明确 SWB/MWB 和车顶高度分支，未猜测绑定既有尺寸组。

## 当前批次进度

* 已处理输入 Ktype：**100 / 100**
* READY 映射：**119**
* PENDING 映射：**3**
* 未处理输入 Ktype：**0**
* 本轮首次创建尺寸组：**9**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5598	5598	Pickup	L200 III Double Cab		4	EU-MITSUBISHI-L200-III-DOUBLE-CAB-PICKUP-01	MEDIUM	87 hp 4WD 对应 1996 年起双排驾驶室；输入开始年月早于该外廓资料。	READY
5626_prefl	5626	Convertible	306 Cabrio	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	HIGH	7D 改款前外廓。	READY
5626_facelift	5626	Convertible	306 Cabrio	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH	7D 改款后外廓。	READY
5627	5627	Sedan	406 Phase I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	2.0 Turbo 147 hp 对应改款前外廓；输入结束年月晚于该发动机版本。	READY
5628	5628	MPV	Boxer I	230P			LOW	候选为 230P Bus 的 SWB/MWB 与不同车顶外廓；4x4 版本未明确长度和车顶。	PENDING: 需确认 1.9 TD 4x4 Bus 的轴距与车顶分支
5629	5629	MPV	Boxer I	230P			LOW	候选为 230P Bus 的 SWB/MWB 与不同车顶外廓；4x4 版本未明确长度和车顶。	PENDING: 需确认 2.5 D 4x4 Bus 的轴距与车顶分支
5630	5630	MPV	Boxer I	230P			LOW	候选为 230P Bus 的 SWB/MWB 与不同车顶外廓；4x4 版本未明确长度和车顶。	PENDING: 需确认 2.5 TD 4x4 Bus 的轴距与车顶分支
5631	5631	Sedan	406 Phase I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	1.9 TD 92 hp 对应改款前外廓；输入结束年月晚于该发动机版本。	READY
5632	5632	Targa	911 (993)	993	2	EU-PORSCHE-911-993-TARGA-CARRERA-01	HIGH		READY
5633	5633	Convertible	Boxster (986)	986	2	EU-PORSCHE-BOXSTER-986-CONVERTIBLE-01	HIGH		READY
5634	5634	Hatchback	Persona 300 Compact		3	EU-PROTON-PERSONA-300-COMPACT-HATCHBACK-3D-01	HIGH		READY
5635	5635	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH		READY
5636	5636	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH		READY
5637	5637	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	HIGH	1996 年后轿车外廓。	READY
5638	5638	Sedan	A6 C4 S6 Plus	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
5639	5639	Wagon	A6 C4 S6 Plus Avant	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
5640	5640	MPV	Mazda 5 II	CW	5	EU-MAZDA-5-II-CW-MPV-01	HIGH		READY
5641	5641	Hatchback	Safrane I facelift	B54L	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5642	5642	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	MEDIUM	改款前 3.0 V6 4x4 标准外廓。	READY
5643	5643	Hatchback	Safrane I facelift	B54G	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5644	5644	Hatchback	Safrane I facelift	B54F	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5645	5645	Hatchback	Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
5646_prefl	5646	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH	LA 改款前外廓。	READY
5646_facelift	5646	Sedan	Megane I Classic Phase II	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	MEDIUM	输入生产期覆盖 Phase II 外廓。	READY
5647_prefl	5647	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	柴油版本名称与功率存在市场写法差异。	READY
5647_facelift	5647	Sedan	Megane I Classic Phase II	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	MEDIUM	输入生产期覆盖 Phase II 外廓。	READY
5648	5648	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH		READY
5649	5649	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	1.9 dT 90 hp 对应改款前外廓；输入结束年月偏晚。	READY
5650	5650	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	2.0i 114 hp 对应改款前外廓。	READY
5651	5651	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH		READY
5652	5652	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	1.9 D 64 hp 对应改款前外廓；输入结束年月偏晚。	READY
5653	5653	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5654	5654	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5655	5655	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5656	5656	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5657	5657	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	MEDIUM	1.9 DT 90 hp 市场写法与资料名称存在差异。	READY
5658	5658	Hatchback	Twingo I		3	EU-RENAULT-TWINGO-I-HATCHBACK-01	HIGH		READY
5659	5659	Wagon	Carina V Wagon	CT170G	5	EU-TOYOTA-CARINA-V-T170-WAGON-01	MEDIUM	欧洲 Carina II Wagon 与 CT170G 同代五门旅行车外廓。	READY
5660	5660	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5661	5661	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5662	5662	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5663	5663	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5664	5664	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5665	5665	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5666	5666	Hatchback	Rover 400 II	HH-R	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5667	5667	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-III-DOUBLE-CAB-PICKUP-01	4920	1655	1745	Auto-Data Mitsubishi L200 III Double Cab 2.5 TD 87 Hp 4WD	https://www.auto-data.net/en/mitsubishi-l200-iii-double-cab-2.5-td-87hp-4wd-15583
EU-PORSCHE-BOXSTER-986-CONVERTIBLE-01	4315	1780	1290	Auto-Data Porsche Boxster 986 2.5 204 Hp	https://www.auto-data.net/en/porsche-boxster-986-2.5-204hp-6708
EU-PROTON-PERSONA-300-COMPACT-HATCHBACK-3D-01	3990	1698	1365	Auto-Data Proton Persona I Compact 1.5 GLi 315GLi	https://www.auto-data.net/en/proton-persona-i-compact-1.5-gli-315gli-87hp-8234
EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	4768	1816	1435	Auto-Data Renault Safrane I B54 facelift 1996 2.0 16V	https://www.auto-data.net/en/renault-safrane-i-b54-facelift-1996-2.0-16v-b54l-136hp-10738
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420	Auto-Data Renault Megane I Classic LA 1.4 e	https://www.auto-data.net/en/renault-megane-i-classic-la-1.4-e-75hp-10582
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420	Auto-Data Renault Megane I Classic Phase II 1.4 e	https://www.auto-data.net/en/renault-megane-i-classic-phase-ii-1999-1.4-e-75hp-30232
EU-RENAULT-MEGANE-SCENIC-I-MPV-01	4134	1719	1675	Auto-Data Renault Megane Scenic generation	https://www.auto-data.net/en/renault-megane-scenic-generation-6217
EU-TOYOTA-CARINA-V-T170-WAGON-01	4470	1690	1380	JapaneseCarTrade Toyota Carina Surf Q-CT170G SV	https://cars.japanesecartrade.com/detail/toyota/carina-surf/sv/133151
EU-ROVER-400-II-RT-SEDAN-4D-01	4491	1695	1385	Auto-Data Rover 400 RT 416 Si	https://www.auto-data.net/en/rover-400-rt-416-si-113hp-11618
```

## 下一步优先处理

1. 仅处理 Ktype `5628–5630`。
2. 确认 Peugeot Boxer I `230P` 4x4 Bus 是否分别覆盖 SWB、MWB、标准顶和高顶。
3. 优先复用现有 Boxer 尺寸组；只有 4x4 悬架造成不同外部高度时才创建新组。
4. 三个 Ktype 闭合后立即进入机械收尾并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-l200-iii-double-cab-2.5-td-87hp-4wd-15583 "Mitsubishi L200 III Double Cab 2.5 TD (87 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/porsche-boxster-986-2.5-204hp-6708 "Porsche Boxster (986) 2.5 (204 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5301-5400_ktype_dimension_mapping_final.tsv
- all_5301-5400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Peugeot Boxer I `230P` 的三个 4×4 Bus Ktype：

  * `5628`：短轴高顶。
  * `5629`：短轴/中轴、标准顶/高顶。
  * `5630`：短轴/中轴、标准顶/高顶。
* 已按缓存优先、长宽高只保存在尺寸组表的解耦原则完成最终机械检查。
* 两张最终表的字段顺序、主键唯一性、映射引用和尺寸来源均已校验通过。

## 当前批次进度

* 输入 Ktype：**100 / 100**
* 最终映射行：**128**
* READY：**128**
* PENDING：**0**
* DIMENSION_GROUP：**73**
* 重复 `id`：**0**
* 重复 `DIMENSION_GROUP_ID`：**0**
* 未闭合映射引用：**0**
* 孤立尺寸组：**0**
* 尺寸或来源空值：**0**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5567	5567	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-5D-01	HIGH		READY
5568	5568	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH		READY
5569	5569	Coupe	Fiat Coupe (175)	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH		READY
5570	5570	Sedan	Legend III	KA9	4	EU-HONDA-LEGEND-III-KA9-SEDAN-01	HIGH		READY
5571	5571	Wagon	Lantra II (J2)	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
5572	5572	Wagon	Lantra II (J2)	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
5573	5573	Wagon	Astra H	L35	5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	Caravan 改款后物理外廓。	READY
5574_3dr	5574	Hatchback	Pride (DA)	DA	3	EU-KIA-PRIDE-DA-HATCHBACK-3D-01	MEDIUM	DA 三门物理分支。	READY
5574_5dr	5574	Hatchback	Pride (DA)	DA	5	EU-KIA-PRIDE-DA-HATCHBACK-5D-01	MEDIUM	DA 五门物理分支。	READY
5575_prefl	5575	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	HIGH	WA6 改款前物理外廓。	READY
5575_facelift	5575	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	HIGH	WA6 改款后物理外廓。	READY
5576_3dr	5576	Hatchback	Pride (DA)	DA	3	EU-KIA-PRIDE-DA-HATCHBACK-3D-01	MEDIUM	DA 三门物理分支。	READY
5576_5dr	5576	Hatchback	Pride (DA)	DA	5	EU-KIA-PRIDE-DA-HATCHBACK-5D-01	MEDIUM	DA 五门物理分支。	READY
5577	5577	Hatchback	Colt V (CJO)	CJ1A	3	EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	HIGH		READY
5578	5578	Hatchback	Colt V (CJO)	CJ4A	3	EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	HIGH		READY
5579	5579	Sedan	Lancer VI		4	EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	HIGH		READY
5580	5580	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5581	5581	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5582	5582	MPV	Expert I	222		EU-PEUGEOT-EXPERT-I-222-BUS-01	MEDIUM	乘用 Bus 外廓。	READY
5583	5583	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	MEDIUM	163 hp S16 对应 Phase I 三门外廓；输入结束年月晚于该规格记录。	READY
5584	5584	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH		READY
5585_prefl	5585	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	K56 改款前物理外廓。	READY
5585_facelift	5585	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	K56 改款后物理外廓。	READY
5586_prefl	5586	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	K56 改款前物理外廓。	READY
5586_facelift	5586	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	K56 改款后物理外廓。	READY
5587_prefl	5587	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	B56 改款前物理外廓。	READY
5587_facelift	5587	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	B56 改款后物理外廓。	READY
5588	5588	Sedan	600 (RH)	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
5589	5589	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5590	5590	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5591	5591	Van	Inca	9K	3	EU-SEAT-INCA-9K-VAN-01	HIGH		READY
5592	5592	Convertible	Stratus Cabrio	JX	2	EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	HIGH		READY
5593	5593	Convertible	Stratus Cabrio	JX	2	EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	HIGH		READY
5594_prefl	5594	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5594_facelift	5594	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5595_prefl	5595	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5595_facelift	5595	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5596_prefl	5596	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	1.8 D 结束于改款切换期，按 M49 外廓落盘。	READY
5597_prefl	5597	MPV	Berlingo I (M49)	M49		EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	MEDIUM	M49 共用 Kasten/Multispace 外壳。	READY
5597_facelift	5597	MPV	Berlingo I (M59)	M59		EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	MEDIUM	M59 共用 Kasten/Multispace 外壳。	READY
5598	5598	Pickup	L200 III Double Cab		4	EU-MITSUBISHI-L200-III-DOUBLE-CAB-PICKUP-01	MEDIUM	87 hp 4WD 对应 1996 年起双排驾驶室；输入开始年月早于该外廓资料。	READY
5599	5599	Wagon	Sigma Station Wagon	F07W	5	EU-MITSUBISHI-SIGMA-F07W-WAGON-01	HIGH		READY
5600	5600	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5601	5601	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5602	5602	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5603	5603	Hatchback	A3 (8L)	8L1	3	EU-AUDI-A3-8L-HATCHBACK-3D-01	HIGH		READY
5604	5604	Sedan	S8 (D2)	D2	4	EU-AUDI-S8-D2-SEDAN-PREFL-01	HIGH	S8 专属车高外廓。	READY
5605	5605	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
5606	5606	Wagon	A4 B5 Avant	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
5607	5607	MPV	Mazda 5 II	CW	5	EU-MAZDA-5-II-CW-MPV-01	HIGH		READY
5608	5608	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH		READY
5610	5610	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	HIGH		READY
5611	5611	SUV	Musso I	FJ	5	EU-SSANGYONG-MUSSO-I-FJ-SUV-01	MEDIUM		READY
5612	5612	SUV	Wrangler II	TJ	2	EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	HIGH	标准短轴开放式车身。	READY
5613	5613	SUV	Wrangler II	TJ	2	EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	MEDIUM	标准短轴开放式车身；未包含后期 Unlimited 长轴分支。	READY
5614	5614	MPV	S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
5615	5615	MPV	806	221	5	EU-PEUGEOT-806-221-MPV-01	HIGH		READY
5616_phase1_3dr	5616	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	HIGH	Phase I 三门物理外廓。	READY
5616_phase1_5dr	5616	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	HIGH	Phase I 五门物理外廓。	READY
5616_phase2_3dr	5616	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	HIGH	Phase II 三门物理外廓。	READY
5616_phase2_5dr	5616	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	HIGH	Phase II 五门物理外廓。	READY
5617	5617	MPV	Jumpy I	222		EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	HIGH		READY
5618_prefl	5618	Wagon	Xantia Break	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1 旅行车外廓。	READY
5618_facelift	5618	Wagon	Xantia Break	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2 旅行车外廓。	READY
5619_3dr	5619	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	MEDIUM	标准三门物理外廓。	READY
5619_5dr	5619	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	MEDIUM	标准五门物理外廓。	READY
5620_3dr	5620	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5620_5dr	5620	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
5621_3dr	5621	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5621_5dr	5621	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
5622_3dr	5622	Hatchback	106 II		3	EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	HIGH	1.6 三门物理外廓。	READY
5622_5dr	5622	Hatchback	106 II		5	EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	HIGH	1.6 五门物理外廓。	READY
5623	5623	Hatchback	106 II		3	EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	HIGH	S16 三门宽体及车高外廓。	READY
5624_3dr	5624	Hatchback	106 II		3	EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	HIGH	1.6 三门物理外廓。	READY
5624_5dr	5624	Hatchback	106 II		5	EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	HIGH	1.6 五门物理外廓。	READY
5625_3dr	5625	Hatchback	106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	标准三门物理外廓。	READY
5625_5dr	5625	Hatchback	106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	标准五门物理外廓。	READY
5626_prefl	5626	Convertible	306 Cabrio	7D	2	EU-PEUGEOT-306-CABRIO-7D-PREFL-01	HIGH	7D 改款前外廓。	READY
5626_facelift	5626	Convertible	306 Cabrio	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH	7D 改款后外廓。	READY
5627	5627	Sedan	406 Phase I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	2.0 Turbo 147 hp 对应改款前外廓；输入结束年月晚于该发动机版本。	READY
5628_swbhigh	5628	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	HIGH	1.9 TD 4×4 的 310 CS 高顶短轴外廓。	READY
5629_swblow	5629	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	HIGH	2.5 D 4×4 的 310 C 标准顶短轴外廓。	READY
5629_swbhigh	5629	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	HIGH	2.5 D 4×4 的 310 CS 高顶短轴外廓。	READY
5629_mwblow	5629	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	2.5 D 4×4 的中轴标准顶外廓。	READY
5629_mwbhigh	5629	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	HIGH	2.5 D 4×4 的中轴高顶外廓。	READY
5630_swblow	5630	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	HIGH	2.5 TD 4×4 的 310 C 标准顶短轴外廓。	READY
5630_swbhigh	5630	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	HIGH	2.5 TD 4×4 的 310 CS 高顶短轴外廓。	READY
5630_mwblow	5630	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	MEDIUM	2.5 TD 4×4 的中轴标准顶外廓。	READY
5630_mwbhigh	5630	MPV	Boxer I	230P	5	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	HIGH	2.5 TD 4×4 的中轴高顶外廓。	READY
5631	5631	Sedan	406 Phase I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	1.9 TD 92 hp 对应改款前外廓；输入结束年月晚于该发动机版本。	READY
5632	5632	Targa	911 (993)	993	2	EU-PORSCHE-911-993-TARGA-CARRERA-01	HIGH		READY
5633	5633	Convertible	Boxster (986)	986	2	EU-PORSCHE-BOXSTER-986-CONVERTIBLE-01	HIGH		READY
5634	5634	Hatchback	Persona 300 Compact		3	EU-PROTON-PERSONA-300-COMPACT-HATCHBACK-3D-01	HIGH		READY
5635	5635	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH		READY
5636	5636	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH		READY
5637	5637	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	HIGH	1996 年后轿车外廓。	READY
5638	5638	Sedan	A6 C4 S6 Plus	4A	4	EU-AUDI-A6-C4-S6-SEDAN-01	HIGH		READY
5639	5639	Wagon	A6 C4 S6 Plus Avant	4A	5	EU-AUDI-A6-C4-S6-AVANT-WAGON-01	HIGH		READY
5640	5640	MPV	Mazda 5 II	CW	5	EU-MAZDA-5-II-CW-MPV-01	HIGH		READY
5641	5641	Hatchback	Safrane I facelift	B54L	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5642	5642	Hatchback	Safrane I	B54	5	EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	MEDIUM	改款前 3.0 V6 4x4 标准外廓。	READY
5643	5643	Hatchback	Safrane I facelift	B54G	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5644	5644	Hatchback	Safrane I facelift	B54F	5	EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	HIGH		READY
5645	5645	Hatchback	Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	HIGH		READY
5646_prefl	5646	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH	LA 改款前外廓。	READY
5646_facelift	5646	Sedan	Megane I Classic Phase II	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	MEDIUM	输入生产期覆盖 Phase II 外廓。	READY
5647_prefl	5647	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	柴油版本名称与功率存在市场写法差异。	READY
5647_facelift	5647	Sedan	Megane I Classic Phase II	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	MEDIUM	输入生产期覆盖 Phase II 外廓。	READY
5648	5648	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH		READY
5649	5649	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	1.9 dT 90 hp 对应改款前外廓；输入结束年月偏晚。	READY
5650	5650	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	2.0i 114 hp 对应改款前外廓。	READY
5651	5651	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH		READY
5652	5652	Sedan	Megane I Classic	LA	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	MEDIUM	1.9 D 64 hp 对应改款前外廓；输入结束年月偏晚。	READY
5653	5653	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5654	5654	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5655	5655	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5656	5656	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
5657	5657	MPV	Megane Scenic		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	MEDIUM	1.9 DT 90 hp 市场写法与资料名称存在差异。	READY
5658	5658	Hatchback	Twingo I		3	EU-RENAULT-TWINGO-I-HATCHBACK-01	HIGH		READY
5659	5659	Wagon	Carina V Wagon	CT170G	5	EU-TOYOTA-CARINA-V-T170-WAGON-01	MEDIUM	欧洲 Carina II Wagon 与 CT170G 同代五门旅行车外廓。	READY
5660	5660	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5661	5661	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5662	5662	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5663	5663	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5664	5664	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5665	5665	Sedan	Rover 400 II	RT	4	EU-ROVER-400-II-RT-SEDAN-4D-01	HIGH		READY
5666	5666	Hatchback	Rover 400 II	HH-R	5	EU-ROVER-400-II-HHR-HATCHBACK-01	HIGH		READY
5667	5667	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5301-5400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-BRAVA-182-HATCHBACK-5D-01	4187	1741	1420	Automobile-Catalog Fiat Brava 1.4 12V SX	https://www.automobile-catalog.com/car/1995/721265/fiat_brava_1_4_12v_sx_55kw.html
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	4025	1755	1420	Automobile-Catalog Fiat Bravo TD 75 S	https://www.automobile-catalog.com/car/1998/721295/fiat_bravo_td_75_s.html
EU-FIAT-COUPE-175-COUPE-01	4250	1766	1340	AutoZine Fiat Coupe archive	https://www.autozine.org/Archive/Fiat/classic/Coupe.html
EU-HONDA-LEGEND-III-KA9-SEDAN-01	4995	1820	1430	Auto-Data Honda Legend III KA9 3.5 i 24V	https://www.auto-data.net/en/honda-legend-iii-ka9-3.5-i-24v-205hp-12173
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457	Automobile-Catalog Hyundai Lantra Combi 1.6i 16V GLS;Automobile-Catalog Hyundai Lantra Estate 1.6 16V LSi	https://www.automobile-catalog.com/car/1996/1164380/hyundai_lantra_combi_1_6i_16v_gls.html;https://www.automobile-catalog.com/car/1996/1164815/hyundai_lantra_estate_1_6_16v_lsi.html
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift 2007	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-generation-9251
EU-KIA-PRIDE-DA-HATCHBACK-3D-01	3565	1605	1460	Auto-Data Kia Pride DA	https://www.auto-data.net/fr/kia-pride-da-1.1-i-52hp-2776
EU-KIA-PRIDE-DA-HATCHBACK-5D-01	3565	1605	1460	Auto-Data Kia Pride DA	https://www.auto-data.net/fr/kia-pride-da-1.1-i-52hp-2776
EU-FORD-GALAXY-II-WA6-MPV-PREFL-01	4820	1884	1723	Automobile-Catalog Ford Galaxy 2.0 TDCi 2007	https://www.automobile-catalog.com/car/2007/976055/ford_galaxy_2_0_tdci_130_trend_dpf.html
EU-FORD-GALAXY-II-WA6-MPV-FACELIFT-01	4820	1884	1764	Autogidas Ford Galaxy 2.0 TDCi 2010	https://autogidas.lt/en/auto-katalogas/ford/galaxy/iii-2.0-tdci-trend-2010-2011-k84863
EU-MITSUBISHI-COLT-V-CJO-HATCHBACK-3D-01	3900	1680	1365	Auto-Data Mitsubishi Colt V CJ1A;Auto-Data Mitsubishi Colt V CJ4A	https://www.auto-data.net/en/mitsubishi-colt-v-cjo-1300-gl-glx-cj-1a-75hp-15760;https://www.auto-data.net/en/mitsubishi-colt-v-cjo-1600-glx-cj-4a-90hp-15761
EU-MITSUBISHI-LANCER-VI-SEDAN-4D-01	4295	1690	1395	Auto-Data Mitsubishi Lancer VI 1.3 12V	https://www.auto-data.net/en/mitsubishi-lancer-vi-1.3-12v-gl-glx-75hp-15660
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940	Zoomcar Peugeot Expert Combi 220 C 1.9 D;Drom Peugeot Expert 1.9 D	https://zoomcar.fr/fiche-technique/peugeot/expert-combi-220-c-1-9-d-8pl-NAT61058.html;https://www.drom.ru/catalog/peugeot/expert/235599/
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	3995	1695	1365	Auto-Data Peugeot 306 Hatchback 2.0 S16	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-2.0-s16-163hp-5721
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420	Auto-Data Renault Megane I BA 1.4 ECO	https://www.auto-data.net/en/renault-megane-i-ba-1.4-eco-69hp-10569
EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	4620	1752	1448	Auto-Data Renault Laguna Grandtour 2.2 DT	https://www.auto-data.net/en/renault-laguna-grandtour-2.2-dt-113hp-10354
EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	4628	1752	1448	Automobile-Catalog Renault Laguna Wagon 1.8 GPL	https://www.automobile-catalog.com/car/1999/2946065/renault_laguna_wagon_1_8_gpl.html
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	4508	1752	1433	Automobile-Catalog Renault Laguna 1.8i	https://www.automobile-catalog.com/car/1998/2945570/renault_laguna_1_8i.html
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432	Auto Motor und Sport Renault Laguna I technical data	https://www.auto-motor-und-sport.de/marken-modelle/renault/laguna/i-typ-b56-k56/technische-daten/
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380	Auto-Data Rover 600 RH 618 i/Si	https://www.auto-data.net/en/rover-600-rh-618-i-si-115hp-11589
EU-SEAT-INCA-9K-VAN-01	4207	1696	1836	Automobile-Catalog Seat Inca Van 1.4 MPi;Auto-Data Seat Inca 9K 1.4 MPi	https://www.automobile-catalog.com/car/1995/3071165/seat_inca_van_1_4_mpi.html;https://www.auto-data.net/en/seat-inca-9k-1.4-mpi-60hp-45513
EU-CHRYSLER-STRATUS-JX-CONVERTIBLE-01	4902	1780	1392	Auto-Data Chrysler Stratus Cabrio JX 2.0 LE;Automoli Chrysler Stratus Cabrio JX	https://www.auto-data.net/en/chrysler-stratus-cabrio-jx-2.0-le-131hp-14718;https://www.automoli.com/en/vehicles/chrysler/stratus/stratus-cabrio-jx-3235/
EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	4108	1698	1802	Automobile-Catalog Citroen Berlingo Multispace 1.4i	https://www.automobile-catalog.com/car/1996/547745/citroen_berlingo_multispace_1_4i.html
EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	4137	1724	1810	DrivePlace Citroen Berlingo I facelift 1.4 Van	https://citroen.drive.place/berlingo/i_res/group_furgon/579286
EU-MITSUBISHI-L200-III-DOUBLE-CAB-PICKUP-01	4920	1655	1745	Auto-Data Mitsubishi L200 III Double Cab 2.5 TD 87 Hp 4WD	https://www.auto-data.net/en/mitsubishi-l200-iii-double-cab-2.5-td-87hp-4wd-15583
EU-MITSUBISHI-SIGMA-F07W-WAGON-01	4800	1775	1505	Auto-Data Mitsubishi Sigma Station Wagon F07W	https://www.auto-data.net/en/mitsubishi-sigma-station-wagon-f07w-3.0-v6-177hp-automatic-24615
EU-AUDI-A3-8L-HATCHBACK-3D-01	4152	1735	1427	Auto-Data Audi A3 8L 1.6i	https://www.auto-data.net/en/audi-a3-8l-1.6i-101hp-4236
EU-AUDI-S8-D2-SEDAN-PREFL-01	5034	1880	1420	Auto-Data Audi S8 D2 4.2 V8 32V	https://www.auto-data.net/en/audi-s8-d2-4.2-v8-32v-340hp-quattro-4790
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415	Auto-Data Audi A4 B5 1.9 TDI quattro	https://www.auto-data.net/en/audi-a4-b5-typ-8d-1.9-tdi-110hp-quattro-4420
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417	Auto-Data Audi A4 Avant B5 1.9 TDI quattro	https://www.auto-data.net/en/audi-a4-avant-b5-typ-8d-1.9-tdi-110hp-quattro-4444
EU-MAZDA-5-II-CW-MPV-01	4585	1750	1615	Auto-Data Mazda 5 II 1.6 CD	https://www.auto-data.net/en/mazda-5-ii-1.6-cd-115hp-17508
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365	Auto-Data Audi 80 B2 1.9 CD-5S	https://www.auto-data.net/en/audi-80-b2-typ-81-85-1.9-cd-5s-115hp-4615
EU-SSANGYONG-MUSSO-I-FJ-SUV-01	4640	1905	1735	Auto-Data SsangYong Musso I 3.2 i 24V	https://www.auto-data.net/en/ssangyong-musso-i-3.2-i-24v-220hp-16010
EU-JEEP-WRANGLER-II-TJ-SUV-SWB-01	3883	1740	1748	Auto-Data Jeep Wrangler II TJ 2.5 i	https://www.auto-data.net/en/jeep-wrangler-ii-tj-2.5-i-118hp-1180
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658	Automobile-Catalog Ford S-Max 2.0 TDCi 2007	https://www.automobile-catalog.com/car/2007/976685/ford_s-max_2_0_tdci_140_titanium_dpf.html
EU-PEUGEOT-806-221-MPV-01	4454	1834	1714	Drom Peugeot 806 dimensions	https://www.drom.ru/catalog/peugeot/806/specs/dimensions/
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-01	3718	1595	1390	Drom Citroen Saxo dimensions	https://www.drom.ru/catalog/citroen/saxo/specs/dimensions/
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Drom Citroen Saxo dimensions	https://www.drom.ru/catalog/citroen/saxo/specs/dimensions/
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1620	1370	Drom Citroen Saxo dimensions	https://www.drom.ru/catalog/citroen/saxo/specs/dimensions/
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Drom Citroen Saxo dimensions	https://www.drom.ru/catalog/citroen/saxo/specs/dimensions/
EU-CITROEN-JUMPY-I-DISPATCH-MPV-01	4440	1810	1927	Drom Citroen Jumpy dimensions	https://www.drom.ru/catalog/citroen/jumpy/specs/dimensions/
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416	Auto-Data Citroen Xantia Break X1 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xantia-break-x1-2.1-turbo-d12-109hp-14976
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420	Auto-Data Citroen Xantia Break X2 2.1 Turbo D12	https://www.auto-data.net/en/citroen-xantia-break-x2-2.1-turbo-d12-109hp-14951
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.0 i	https://www.auto-data.net/en/peugeot-106-ii-1-1.0-i-50hp-5404
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376	Auto-Data Peugeot 106 II 1.0 i	https://www.auto-data.net/en/peugeot-106-ii-1-1.0-i-50hp-5404
EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	3680	1590	1380	Auto-Data Peugeot 106 II 1.6 i 88 Hp	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-i-88hp-5409
EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	3680	1590	1380	Auto-Data Peugeot 106 II 1.6 i 88 Hp	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-i-88hp-5409
EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	3678	1610	1357	Auto-Data Peugeot 106 II 1.6 S16	https://www.auto-data.net/en/peugeot-106-ii-1-1.6-s16-118hp-5410
EU-PEUGEOT-306-CABRIO-7D-PREFL-01	4144	1689	1356	Drom Peugeot 306 dimensions	https://www.drom.ru/catalog/peugeot/306/specs/dimensions/
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356	Auto-Data Peugeot 306 Cabrio facelift generation	https://www.auto-data.net/en/peugeot-306-cabrio-facelift-1997-generation-6620
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410	Drom Peugeot 406 dimensions	https://www.drom.ru/catalog/peugeot/406/specs/dimensions/
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465	Zoomcar Peugeot Boxer 310 CS 1.9 TD 9m3 4x4;Zoomcar Peugeot Boxer 310 CS 2.5 D 9m3 4x4	https://zoomcar.fr/fiche-technique-utilitaire/peugeot/boxer-b-94-02-boxer-fgn-tole-310-cs-1-9-td-9m3-4x4-NAT58913.html;https://zoomcar.fr/fiche-technique-utilitaire/peugeot/boxer-b-94-02-boxer-fgn-tole-310-cs-2-5-d-9m3-4x4-NAT58912.html
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150	Zoomcar Peugeot Boxer 310 C 2.5 D 7.5m3 4x4	https://zoomcar.fr/fiche-technique-utilitaire/peugeot/boxer-b-94-02-boxer-fgn-tole-310-c-2-5-d-7-5m3-4x4-NAT58428.html
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150	Dauto Peugeot Boxer 2.5 DT 4x4 type approval;Drom Peugeot Boxer dimensions	https://www.dauto.ch/typenscheine/peugeot-boxer-2-5dt-4x4-1pa246-vf323v94-e3-70-156-96-27-0026;https://www.drom.ru/catalog/peugeot/boxer/specs/dimensions/
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470	Zoomcar Peugeot Boxer 350 LH 2.5 D 12m3 4x4;Zoomcar Peugeot Boxer 350 LH 2.5 TD 12m3 4x4	https://zoomcar.fr/fiche-technique-utilitaire/peugeot/boxer-b-94-02-boxer-fgn-tole-350-lh-2-5-d-12m3-4x4-NAT58434.html;https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/boxer-b-94-02-boxer-fgn-tole-350-lh-2-5-td-12m3-4x4-NAT58435.html
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300	Drom Porsche 911 dimensions	https://www.drom.ru/catalog/porsche/911/specs/dimensions/
EU-PORSCHE-BOXSTER-986-CONVERTIBLE-01	4315	1780	1290	Auto-Data Porsche Boxster 986 2.5 204 Hp	https://www.auto-data.net/en/porsche-boxster-986-2.5-204hp-6708
EU-PROTON-PERSONA-300-COMPACT-HATCHBACK-3D-01	3990	1698	1365	Auto-Data Proton Persona I Compact 1.5 GLi 315GLi	https://www.auto-data.net/en/proton-persona-i-compact-1.5-gli-315gli-87hp-8234
EU-PROTON-PERSONA-400-HATCHBACK-5D-01	4270	1690	1385	Drom Proton Persona dimensions	https://www.drom.ru/catalog/proton/persona/specs/dimensions/
EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	4360	1690	1380	Drom Proton Persona dimensions	https://www.drom.ru/catalog/proton/persona/specs/dimensions/
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430	Drom Audi A6 dimensions	https://www.drom.ru/catalog/audi/a6/specs/dimensions/
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440	Drom Audi A6 dimensions	https://www.drom.ru/catalog/audi/a6/specs/dimensions/
EU-RENAULT-SAFRANE-I-B54-FACELIFT-HATCHBACK-01	4768	1816	1435	Auto-Data Renault Safrane I B54 facelift 1996 2.0 16V	https://www.auto-data.net/en/renault-safrane-i-b54-facelift-1996-2.0-16v-b54l-136hp-10738
EU-RENAULT-SAFRANE-I-B54-HATCHBACK-STANDARD-01	4734	1818	1443	Automobile-Catalog Renault Safrane 2.2i	https://www.automobile-catalog.com/car/1993/2945135/renault_safrane_2_2i.html
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Drom Renault Clio dimensions	https://www.drom.ru/catalog/renault/clio/specs/dimensions/
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420	Auto-Data Renault Megane I Classic LA 1.4 e	https://www.auto-data.net/en/renault-megane-i-classic-la-1.4-e-75hp-10582
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420	Auto-Data Renault Megane I Classic Phase II 1.4 e	https://www.auto-data.net/en/renault-megane-i-classic-phase-ii-1999-1.4-e-75hp-30232
EU-RENAULT-MEGANE-SCENIC-I-MPV-01	4134	1719	1675	Auto-Data Renault Megane Scenic generation	https://www.auto-data.net/en/renault-megane-scenic-generation-6217
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423	Drom Renault Twingo dimensions	https://www.drom.ru/catalog/renault/twingo/specs/dimensions/
EU-TOYOTA-CARINA-V-T170-WAGON-01	4470	1690	1380	JapaneseCarTrade Toyota Carina Surf Q-CT170G SV	https://cars.japanesecartrade.com/detail/toyota/carina-surf/sv/133151
EU-ROVER-400-II-RT-SEDAN-4D-01	4491	1695	1385	Auto-Data Rover 400 RT 416 Si	https://www.auto-data.net/en/rover-400-rt-416-si-113hp-11618
EU-ROVER-400-II-HHR-HATCHBACK-01	4490	1695	1390	Drom Rover 400 dimensions	https://www.drom.ru/catalog/rover/400/specs/dimensions/
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390	Drom Rover 400 dimensions	https://www.drom.ru/catalog/rover/400/specs/dimensions/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5301-5400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5301-5400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5301-5400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6983 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2159 行）

