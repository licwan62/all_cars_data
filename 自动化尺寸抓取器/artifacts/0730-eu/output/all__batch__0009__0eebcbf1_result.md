# 任务：all 第 801-900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0009__0eebcbf1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 801-900 行

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
all 第 801-900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618
EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	4140	1800	1593
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-OPEL-VIVARO-B-VAN-L1H1-01	4998	1956	1971
EU-OPEL-VIVARO-B-VAN-L1H2-01	4998	1956	2465
EU-OPEL-VIVARO-B-VAN-L2H1-01	5398	1956	1971
EU-OPEL-VIVARO-B-VAN-L2H2-01	5398	1956	2465
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	5048	2070	2307
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	5048	2070	2500
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	5548	2070	2749
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	6198	2070	2488
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	6198	2070	2744
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	4295	1690	1385
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	140	190	Sep 2016	Jun 2023	2024-03-01	123345
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	140	190	Sep 2016	Jun 2023	2024-03-01	123346
BMW	5	530 D	Stufenheck	Heckantrieb	Diesel	195	265	Sep 2016	Jun 2020	2024-03-01	123348
BMW	5	530 D Xdrive	Stufenheck	Allrad	Diesel	195	265	Sep 2016	Jun 2020	2024-03-01	123349
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	100	136	Oct 2016	-	2024-03-01	123350
Mini	Mini	Cooper All4	Kombi	Allrad	Benzin	100	136	Oct 2016	-	2024-03-01	123356
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	141	192	Oct 2016	-	2024-03-01	123357
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	141	192	Oct 2016	-	2024-03-01	123358
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Nov 2016	Dec 2021	2026-03-01	123359
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	131	Nov 2016	Dec 2021	2026-03-01	123360
Opel	Movano b	2.3 Cdti RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	131	Nov 2016	Dec 2021	2026-03-01	123361
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	110	150	Oct 2016	-	2024-03-01	123362
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	125	170	Nov 2016	Dec 2021	2026-03-01	123363
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	110	150	Oct 2016	-	2024-03-01	123364
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	96	131	Nov 2016	Dec 2021	2026-03-01	123365
Opel	Movano b	2.3 Cdti RWD	Kasten	Heckantrieb	Diesel	96	131	Nov 2016	Dec 2021	2026-03-01	123366
Opel	Zafira	1.6 Cdti	Großraumlimousine	Frontantrieb	Diesel	99	134	Jul 2013	Mar 2019	2025-12-01	123367
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	140	190	Oct 2016	-	2024-03-01	123369
Mini	Mini	Cooper SD All4	Kombi	Allrad	Diesel	140	190	Oct 2016	-	2024-03-01	123370
Audi	Q5	2.0 TDI Quattro	SUV	Allrad	Diesel	120	163	Jun 2016	Aug 2018	2024-03-01	123385
Audi	Q5	2.0 TDI Quattro	SUV	Allrad	Diesel	140	190	Jun 2016	Aug 2018	2024-03-01	123387
Alfa Romeo	Giulia	2.0 Q4	Stufenheck	Allrad	Benzin	206	280	Aug 2016	-	2024-03-01	123388
Fiat	Tipo	1.6 D	Stufenheck	Frontantrieb	Diesel	84	114	Sep 2016	Oct 2020	2024-03-01	123395
Fiat	Tipo	1.6 D	Schrägheck	Frontantrieb	Diesel	84	114	Sep 2016	Oct 2020	2024-03-01	123396
Audi	Q5	2.0 Tfsi Quattro	SUV	Allrad	Benzin	183	249	Jan 2017	Nov 2020	2024-03-01	123397
Fiat	Tipo	1.6 D	Kombi	Frontantrieb	Diesel	84	114	Sep 2016	Oct 2020	2024-03-01	123398
Audi	Q5	2.0 Tfsi Quattro	SUV	Allrad	Benzin	185	252	Jun 2016	Nov 2020	2024-03-01	123400
Skoda	Kodiaq i	1.4 TSI	SUV	Frontantrieb	Benzin	92	125	Oct 2016	-	2024-05-01	123422
Skoda	Kodiaq i	1.4 TSI 4X4	SUV	Allrad	Benzin	110	150	Oct 2016	-	2024-05-01	123424
Skoda	Kodiaq i	2.0 TSI 4X4	SUV	Allrad	Benzin	132	180	Oct 2016	-	2024-05-01	123425
Skoda	Kodiaq i	2.0 TDI 4X4	SUV	Allrad	Diesel	110	150	Oct 2016	-	2024-05-01	123426
Skoda	Kodiaq i	2.0 TDI 4X4	SUV	Allrad	Diesel	140	190	Oct 2016	-	2024-05-01	123427
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	92	125	Nov 2016	Dec 2019	2024-03-01	123431
Opel	Vivaro b	1.6 Cdti	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Nov 2016	Dec 2019	2024-03-01	123432
Mini	Mini	John Cooper Works	Kombi	Allrad	Benzin	170	231	Nov 2016	Jun 2019	2024-03-01	123438
Renault	Master iii	2.3 DCI 135 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Jul 2014	Dec 2024	2026-03-01	123447
Mercedes-benz	S-Klasse	S 350 CDI 4-matic	Stufenheck	Allrad	Diesel	155	211	Jan 2009	Dec 2010	2024-03-01	123503
Toyota	Premio	1.8	Stufenheck	Frontantrieb	Benzin	100	136	Jul 2007	-	2024-03-01	123530
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	75	102	Sep 2016	Jun 2024	2025-06-01	123531
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	103	140	Sep 2016	-	2025-04-01	123535
VW	Crafter	2.0 TDI FWD	Kasten	Frontantrieb	Diesel	130	177	Sep 2016	-	2025-04-01	123537
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	75	102	Nov 2016	Jun 2024	2025-04-01	123538
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Nov 2016	-	2025-04-01	123539
VW	Crafter	2.0 TDI FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	130	177	Nov 2016	-	2025-04-01	123540
VW	Transporter t5	2.0 Bifuel	Kasten	Frontantrieb	Benzin/Erdgas (CNG)	85	115	Jun 2007	Aug 2015	2024-03-01	123561
ZD	D2s	Electric	Schrägheck	Frontantrieb	Elektro	30	41	Aug 2021	-	2024-03-01	123577
Skoda	Rapid	1.6	Schrägheck	Frontantrieb	Benzin	81	110	May 2015	Mar 2022	2024-03-01	123729
Mercedes-benz	Amg gt	GT R	Coupe	Heckantrieb	Benzin	430	585	Nov 2016	Dec 2021	2024-03-01	123743
Mercedes-benz	Amg gt roadster	GT	Cabriolet	Heckantrieb	Benzin	350	476	Nov 2016	May 2020	2024-03-01	123745
Mercedes-benz	Amg gt roadster	GT C	Cabriolet	Heckantrieb	Benzin	410	557	Nov 2016	Dec 2021	2024-03-01	123747
Suzuki	Swift ii	1	Stufenheck	Frontantrieb	Benzin	39	53	Jan 1994	May 2001	2024-03-01	123758
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	81	110	May 1995	Feb 2000	2024-03-01	123760
Lada	Nova	1300	Stufenheck	Heckantrieb	Benzin	49	66	Sep 1983	Dec 1997	2024-03-01	123770
Ferrari	F355 gts	3.5	Targa	Heckantrieb	Benzin	280	380	Jul 1994	Mar 1999	2024-03-01	123772
Nissan	Nv300 kombi	1.6 DCI 95	Bus	Frontantrieb	Diesel	70	95	Sep 2016	-	2024-03-01	123799
KIA	Sorento iii	2.2 Crdi 4WD	SUV	Allrad	Diesel	145	197	Nov 2016	Dec 2020	2024-05-01	123810
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	120	163	Oct 2016	-	2024-03-01	123815
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	100	136	Oct 2016	-	2024-03-01	123816
Mini	Mini	Cooper SD	Kombi	Frontantrieb	Diesel	120	163	Oct 2016	-	2024-03-01	123817
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	120	163	Oct 2016	-	2024-03-01	123819
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	100	136	Oct 2016	-	2024-03-01	123820
Mini	Mini	Cooper SD All4	Kombi	Allrad	Diesel	120	163	Oct 2016	-	2024-03-01	123821
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	120	163	Sep 2016	Jun 2023	2024-03-01	123822
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	120	163	Sep 2016	Jun 2023	2024-03-01	123823
BMW	5	540 I	Stufenheck	Heckantrieb	Benzin	265	360	Sep 2016	Jun 2020	2024-03-01	123824
BMW	5	540 I Xdrive	Stufenheck	Allrad	Benzin	265	360	Sep 2016	Jun 2020	2024-03-01	123825
Nissan	Micra v	0.9 Ig-t	Schrägheck	Frontantrieb	Benzin	66	90	Dec 2016	-	2024-03-01	123826
KIA	Sportage iv	1.7 Crdi	SUV	Frontantrieb	Diesel	104	141	Nov 2016	Sep 2022	2024-03-01	123827
KIA	Soul ii	1.6 Tgdi	Schrägheck	Frontantrieb	Benzin	150	204	Nov 2016	Dec 2018	2024-03-01	123828
Citroën	Bx	19	Schrägheck	Frontantrieb	Benzin	78	107	Sep 1984	Jan 1992	2024-03-01	123830
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	78	107	Jan 1987	Jan 1992	2024-03-01	123831
Nissan	Micra v	1	Schrägheck	Frontantrieb	Benzin	54	73	Dec 2016	-	2024-03-01	123835
Nissan	Micra v	1.5 DCI	Schrägheck	Frontantrieb	Diesel	66	90	Dec 2016	-	2024-03-01	123836
Aston Martin	Dbs vantage	5.3	Coupe	Heckantrieb	Benzin	235	320	Oct 1968	Aug 1972	2024-03-01	123876
Tesla	Model s	60D AWD	Schrägheck	Allrad	Elektro	245	334	Jun 2016	Apr 2026	2026-06-01	123896
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	235	320	Nov 2016	Apr 2026	2026-06-01	123897
Tesla	Model s	75	Schrägheck	Heckantrieb	Elektro	235	320	Nov 2016	Apr 2026	2026-06-01	123898
Chevrolet	Express standard cargo van	6.0 Flexfuel	Kasten	Heckantrieb	Benzin/Ethanol	241	328	Sep 2015	-	2024-03-01	123910
Alfa Romeo	Giulia	2.2 D Q4	Stufenheck	Allrad	Diesel	154	209	Nov 2016	-	2024-03-01	123923
Maserati	Quattroporte vi	3.0 S	Stufenheck	Heckantrieb	Benzin	301	409	Nov 2016	-	2024-03-01	123925
Skoda	Kodiaq i	1.4 TSI	SUV	Frontantrieb	Benzin	110	150	Oct 2016	-	2024-05-01	123933
Skoda	Kodiaq i	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Oct 2016	-	2024-05-01	123934
Hyundai	Elantra vi	1.6 SR Turbo	Stufenheck	Frontantrieb	Benzin	150	204	Feb 2016	Dec 2020	2024-05-01	123947
Nissan	Micra iii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	59	80	Oct 2002	Jun 2010	2024-03-01	123958
Audi	A5	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	185	252	Nov 2016	-	2024-03-01	123991
Audi	A5	S5 Tfsi Quattro	Cabriolet	Allrad	Benzin	260	354	Mar 2017	-	2025-11-01	123992
Audi	A5	2.0 TDI	Cabriolet	Frontantrieb	Diesel	140	190	Nov 2016	Dec 2019	2024-03-01	123993
Audi	A5	3.0 TDI Quattro	Cabriolet	Allrad	Diesel	160	218	Dec 2016	Aug 2018	2024-03-01	123994
Volvo	V90 ii	D3	Kombi	Frontantrieb	Diesel	110	150	Mar 2016	Dec 2021	2024-05-01	123999
Volvo	V90 ii	D3 AWD	Kombi	Allrad	Diesel	110	150	Mar 2016	Dec 2021	2024-05-01	124000
Volvo	V90 ii	D4 AWD	Kombi	Allrad	Diesel	140	190	Mar 2016	Dec 2021	2024-05-01	124001
Volvo	V90 ii cross country	T5 AWD	Kombi	Allrad	Benzin	187	254	Oct 2016	Dec 2018	2025-06-01	124002
Volvo	S90 ii	D4 AWD	Stufenheck	Allrad	Diesel	140	190	Mar 2016	Dec 2021	2024-05-01	124006
Volvo	S90 ii	D3	Stufenheck	Frontantrieb	Diesel	110	150	Mar 2016	Dec 2021	2024-05-01	124007
Hyundai	I30	1.6 MPI	Coupe	Frontantrieb	Benzin	88	120	May 2013	-	2024-03-01	124009
Toyota	Hilux vi	2.4 D	Pick-up	Heckantrieb	Diesel	58	79	Aug 1997	Jul 2005	2024-03-01	124036
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2020	2024-03-01	124050
Seat	Leon	1.6 TDI	Kombi	Frontantrieb	Diesel	85	115	Nov 2016	Aug 2020	2024-03-01	124051
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	81	110	Aug 2016	Jul 2020	2024-03-01	124068
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	130	177	Aug 2016	Jul 2020	2024-03-01	124077


--- Round 1 / 首次发送 ---
## 更新点

* 新建 BMW 5 Series G30 改款前、改款后两个尺寸组；跨越 2020 年改款期的 520d Ktype 已按 `prefl/facelift` 拆分。官方资料显示改款前为 `4936 × 1868 × 1479 mm`，改款后长度变为 `4963 mm`。
* 新建 MINI Clubman F54 Wagon 尺寸组，统一关联本批 Cooper、Cooper S、Cooper D、Cooper SD、ALL4 及 JCW Ktype。([press.bmwgroup.com][1])
* 新建 Škoda Kodiaq I NS7 改款前尺寸组；官方资料确认 `4697 × 1882 × 1676 mm`，高度含原厂车顶行李架。([Škoda Storyboard][2])
* 复用跨批次索引中的 Giulia、Tipo、Master III chassis、Corolla E110、Soul II、Model S、V90、S90 和 Tiguan II 尺寸组，未重复输出已有尺寸事实。

## 当前批次进度

* READY 映射行：55
* 已覆盖输入 Ktype：48 / 100
* PENDING 输入 Ktype：52
* 当前已引用尺寸组：19
* 本轮首次创建尺寸组：4
* 复用既有尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123345_prefl	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123345_facelift	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123346_prefl	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123346_facelift	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123348	123348	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123349	123349	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123350	123350	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123356	123356	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123357	123357	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123358	123358	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123362	123362	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123364	123364	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123369	123369	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123370	123370	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123388	123388	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
123395	123395	Sedan	Tipo 356	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH		READY
123396	123396	Hatchback	Tipo 357	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH		READY
123398	123398	Wagon	Tipo 358	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH		READY
123422	123422	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123424	123424	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123425	123425	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123426	123426	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123427	123427	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123438	123438	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123447_scab_l2	123447	Chassis Cab	Master III X62 Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_scab_l3	123447	Chassis Cab	Master III X62 Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_dcab_l2	123447	Chassis Cab	Master III X62 Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_dcab_l3	123447	Chassis Cab	Master III X62 Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123760	123760	Sedan	Corolla VIII E110	E110	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	HIGH		READY
123815	123815	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123816	123816	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123817	123817	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123819	123819	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123820	123820	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123821	123821	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123822_prefl	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123822_facelift	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123823_prefl	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123823_facelift	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123824	123824	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123825	123825	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123828	123828	Hatchback	Soul II Facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH		READY
123896	123896	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123897	123897	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123898	123898	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123923	123923	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
123933	123933	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123934	123934	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123999	123999	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124000	124000	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124001	124001	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124006	124006	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
124007	124007	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
124068	124068	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH		READY
124077	124077	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW 5 Series Sedan official specifications, valid from 09/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286565EN/419613
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW 5 Series Sedan official specifications, valid from 05/2020	https://www.press.bmwgroup.com/global/article/attachment/T0314291EN/457886
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441	MINI The new MINI Clubman official press information	https://www.press.bmwgroup.com/global/article/detail/T0222325EN/the-new-mini-clubman
EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	4697	1882	1676	ŠKODA The new KODIAQ official press kit	https://www.skoda-storyboard.com/en/press-kits/new-skoda-kodiaq-press-kit/
```

## 下一步优先处理

1. 集中处理 Opel Movano B、VW Crafter、VW Transporter T5、Opel Vivaro B 与 Nissan NV300 的轴距、车顶和驾驶室派生分支。
2. 处理 Audi Q5 8R/FY、Audi A5 F5 Cabriolet、Mercedes-AMG GT Coupe/Roadster 等代际或性能外廓差异。
3. 补齐 Zafira C、Micra K14/K12、Sportage QL、Sorento UM、SEAT Leon 5F 等乘用车尺寸组。
4. 最后处理历史稀有车型及多驾驶室皮卡：Swift Sedan、Lada Nova、F355 GTS、DBS Vantage、Hilux VI。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0222325EN/the-new-mini-clubman?language=en&utm_source=chatgpt.com "The new MINI Clubman."
[2]: https://www.skoda-storyboard.com/en/press-kits/new-skoda-kodiaq-press-kit/?utm_source=chatgpt.com "The new ŠKODA KODIAQ – Press kit - Škoda Storyboard"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 闭合 Audi Q5 8R 与 FY 两代外廓，四个 Ktype 分别关联对应代际尺寸组。Q5 8R 为 `4629 × 1898 × 1655 mm`，Q5 FY 为 `4663 × 1893 × 1659 mm`。([adac.de][1])
* 批量闭合 Nissan Micra K14、Kia Sportage QL、Citroën BX 两种车身、Maserati Quattroporte M156、Hyundai Elantra AD 等乘用车组。Kia 官方资料明确 Sportage 的宽度为不含后视镜口径。([Kia Press][2])
* Mercedes-AMG GT R Coupe 与 GT C Roadster 按宽体外廓分别建组；Audi A5/S5 F5 Cabriolet 按普通版和 S5 不同长度、高度拆组。([auto-motor-und-sport.de][3])
* 上一轮已闭合的尺寸组均直接复用，本轮未重新抓取或重复输出。

## 2. 当前批次进度

* READY 映射行：75
* 已覆盖输入 Ktype：68 / 100
* PENDING 输入 Ktype：32
* 已确认并被引用的尺寸组：33
* 本轮首次创建尺寸组：14
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123367	123367	MPV	Zafira C	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
123385	123385	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SUV-01	HIGH		READY
123387	123387	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SUV-01	HIGH		READY
123397	123397	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
123400	123400	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
123743	123743	Coupe	AMG GT I	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	HIGH	GT R宽体外廓。	READY
123747	123747	Convertible	AMG GT I	R190	2	EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	HIGH	GT C宽体Roadster外廓。	READY
123826	123826	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123827	123827	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-QL-SUV-01	HIGH		READY
123830	123830	Hatchback	BX		5	EU-CITROEN-BX-HATCHBACK-19-01	MEDIUM	对应BX 19 Hatchback外廓。	READY
123831	123831	Wagon	BX		5	EU-CITROEN-BX-WAGON-19-01	MEDIUM	对应BX 19 Break/Wagon外廓。	READY
123835	123835	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123836	123836	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123925	123925	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH		READY
123947	123947	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	HIGH	澳洲市场SR Turbo外廓。	READY
123991	123991	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
123992	123992	Convertible	A5 II	F5	2	EU-AUDI-S5-II-F5-CABRIOLET-01	HIGH	S5前后保险杠外廓与普通A5不同。	READY
123993	123993	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
123994	123994	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
124051	124051	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685	Opel Zafira Tourer 2017 Owner's Manual – Vehicle dimensions	https://www.carmanualsonline.info/opel-zafira-tourer-2017-owners-manual/?srch=dimensions
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655	ADAC Audi Q5 2.0 TDI quattro 8R – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q5/8r-facelift/241199/
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659	CarExpert 2017 Audi Q5 Design exterior dimensions	https://www.carexpert.com.au/audi/q5/2017/design/exterior-and-dimensions
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	4551	2007	1284	Auto Motor und Sport Mercedes-AMG GT R technical data	https://www.auto-motor-und-sport.de/test/mercedes-amg-gt-r/technische-daten/
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	4551	2007	1260	Auto Express Mercedes-AMG GT C Roadster specifications	https://www.autoexpress.co.uk/mercedes/amg-gt/roadster/prices-specs/77773/gt-c-2dr-auto
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	ADAC Nissan Micra K14 – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k14/317816/
EU-KIA-SPORTAGE-IV-QL-SUV-01	4480	1855	1635	Kia Europe Sportage 2016 official specifications	https://prod2-press.kia.com/eu/en/home/models/sportage/sportage-2016.html
EU-CITROEN-BX-HATCHBACK-19-01	4230	1660	1360	CarsGuide Citroën BX 1991 dimensions	https://www.carsguide.com.au/citroen/bx/car-dimensions/1991
EU-CITROEN-BX-WAGON-19-01	4399	1660	1430	CarsGuide Citroën BX 1990 Wagon dimensions	https://www.carsguide.com.au/citroen/bx/car-dimensions/1990
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481	Maserati official Quattroporte technical specifications	https://www.media.stellantis.com/uk-en/maserati/press/all-new-maserati-quattroporte-unveiled-at-naias-2013
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	4570	1800	1440	Carsales Hyundai Elantra AD SR Turbo specifications	https://www.carsales.com.au/research/hyundai/elantra/2016/sr-turbo/
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	AustralianCar.Reviews Audi F5 A5 Cabriolet body and dimensions	https://australiancar.reviews/review-audi-f5-a5-cabriolet-2017-on/
EU-AUDI-S5-II-F5-CABRIOLET-01	4692	1846	1382	ADAC Audi S5 F5 Cabriolet – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a5/f5-facelift/315604/
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454	ADAC SEAT Leon ST 1.6 TDI 5F Facelift – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/seat/leon/5f-facelift/263322/
```

## 5. 下一步优先处理

1. 集中处理 Opel Movano B、VW Crafter II、Vivaro B、Transporter T5 和 Nissan NV300 的轴距、车顶及驾驶室派生。
2. 闭合 Mercedes-AMG GT 基础 Roadster、Volvo V90 Cross Country、SEAT Leon Hatchback、Kia Sorento III 和 Hyundai i30 Coupe。
3. 最后处理 S-Class W221、Toyota Premio、Swift Sedan、Lada Nova、F355 GTS、DBS Vantage、Hilux VI、ZD D2S 等需特殊分支或历史资料的车型。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q5/8r-facelift/241199/?utm_source=chatgpt.com "Audi Q5 2.0 TDI quattro S tronic (05/14 - 10/16): Technische Daten, Bilder, Preise | ADAC"
[2]: https://prod2-press.kia.com/eu/en/home/models/sportage/sportage-2016.html?utm_source=chatgpt.com "Sportage"
[3]: https://www.auto-motor-und-sport.de/test/mercedes-amg-gt-r/technische-daten/?utm_source=chatgpt.com "Mercedes-AMG GT R im Test (Technische Daten)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Toyota Premio II、Škoda Rapid Spaceback、Mercedes-AMG GT Roadster、Lada Nova、Ferrari F355 GTS、Volvo V90 Cross Country、Hyundai i30 Coupe 等低分支车型。([丰田官网][1])
* Kia Sorento III Ktype 跨越改款，按 `prefl/facelift` 拆分；改款使车长由 4780 mm 增至 4800 mm。两组宽度均为官方明确的不含后视镜口径。([起亚新闻发布网站][2])
* Nissan Micra K12 同一 Ktype 覆盖三门、五门及改款前后外廓，拆为四个稳定分支；改款前长度 3715 mm，改款后为 3719 mm。([ADAC][3])
* SEAT Leon Hatchback 按三门 SC 与五门 Hatchback 拆分，分别对应不同车长、车宽和高度。([汽车手册在线][4])

## 2. 当前批次进度

* READY 映射行：90
* 已覆盖输入 Ktype：78 / 100
* PENDING 输入 Ktype：22
* 已确认并被引用的尺寸组：48
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123530	123530	Sedan	Premio II	ZRT260	4	EU-TOYOTA-PREMIO-II-ZRT260-SEDAN-01	HIGH	1.8升前驱对应ZRT260车身。	READY
123729	123729	Hatchback	Rapid I Spaceback		5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	输入Schrägheck对应Rapid Spaceback。	READY
123745	123745	Convertible	AMG GT I	R190	2	EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	HIGH	基础GT Roadster窄体外廓。	READY
123770	123770	Sedan	Nova 2105	VAZ-2105	4	EU-LADA-NOVA-2105-SEDAN-01	HIGH	Nova 1300对应VAZ-2105轿车。	READY
123772	123772	Targa	F355	F129	2	EU-FERRARI-F355-F129-TARGA-01	HIGH	F355 GTS可拆卸硬顶车身。	READY
123810_prefl	123810	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-PREFL-01	HIGH	同一Ktype跨越UM改款，按车长变化拆分。	READY
123810_facelift	123810	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	HIGH	同一Ktype跨越UM改款，按车长变化拆分。	READY
123958_3dr_prefl	123958	Hatchback	Micra III	K12	3	EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-PREFL-01	MEDIUM	输入未区分门数且跨越改款，保留三门改款前分支。	READY
123958_5dr_prefl	123958	Hatchback	Micra III	K12	5	EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-PREFL-01	MEDIUM	输入未区分门数且跨越改款，保留五门改款前分支。	READY
123958_3dr_facelift	123958	Hatchback	Micra III	K12	3	EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入未区分门数且跨越改款，保留三门改款后分支。	READY
123958_5dr_facelift	123958	Hatchback	Micra III	K12	5	EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-FACELIFT-01	MEDIUM	输入未区分门数且跨越改款，保留五门改款后分支。	READY
124002	124002	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country升高车身，不复用普通V90尺寸组。	READY
124009	124009	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH	GD三门Coupe物理外廓。	READY
124050_3dr	124050	Hatchback	Leon III Facelift	5F	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入未区分SC三门与五门车身。	READY
124050_5dr	124050	Hatchback	Leon III Facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	MEDIUM	输入未区分SC三门与五门车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PREMIO-II-ZRT260-SEDAN-01	4600	1695	1475	Toyota 75 Years Vehicle Lineage – Second-generation Premio specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008578/index.html
EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	4304	1706	1459	ADAC Škoda Rapid Spaceback manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/skoda/rapid/1generation/238509/
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	4544	1939	1259	Mercedes-Benz Media AMG GT Roadster technical data	https://media.mercedes-benz.fr/mercedes-amg-gt-roadster-et-mercedes-amg-gt-c-roadster/
EU-LADA-NOVA-2105-SEDAN-01	4130	1620	1446	Auto-Data Lada 2105 1.3 specifications	https://www.auto-data.net/en/lada-2105-1.3-64hp-13306
EU-FERRARI-F355-F129-TARGA-01	4250	1900	1170	Ferrari F355 GTS official technical specifications	https://www.ferrari.com/en-EN/auto/f355-gts
EU-KIA-SORENTO-III-UM-SUV-PREFL-01	4780	1890	1685	Kia Europe Sorento 2014 official specifications	https://press.kia.com/content/kiapress/eu/en/home/models/sorento/sorento-2014.html
EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	4800	1890	1685	Kia France facelift Sorento official specifications	https://press.kia.com/fr/fr/home/press-releases/2017/Sorento-nouveau-design.html
EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-PREFL-01	3715	1660	1540	ADAC Nissan Micra K12 three-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12/995458/
EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-PREFL-01	3715	1660	1540	Automobile-Catalog Nissan Micra K12 3/5-door specifications	https://www.automobile-catalog.com/car/2003/2198975/nissan_micra_1_2_65.html
EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-FACELIFT-01	3719	1660	1540	ADAC Nissan Micra K12 facelift three-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12-facelift/203479/
EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-FACELIFT-01	3719	1660	1540	ADAC Nissan Micra K12 facelift five-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12-facelift/203492/
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo Support V90 Cross Country 2017 dimensions	https://www.volvocars.com/uk/support/car/v90-cross-country/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/871e942e897ca77dc0a801511788660a/
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470	ADAC Hyundai i30 Coupe manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/hyundai/i30/2generation/235199/
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446	SEAT Leon SC 2017 Owner's Manual – technical dimensions	https://www.carmanualsonline.info/seat-leon-sc-2017-owner-s-manual/?srch=dimensions
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	ADAC SEAT Leon 5F facelift manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/seat/leon/5f-facelift/263274/
```

## 5. 下一步优先处理

1. 集中闭合 Opel Movano B、VW Crafter II、Opel Vivaro B、Renault Trafic/Nissan NV300 系商用车的轴距、车顶和驾驶室分支。
2. 处理 Mercedes S-Class W221 跨改款、Chevrolet Express 2500/3500 标准轴距及 Toyota Hilux VI 多驾驶室分支。
3. 最后解决 ZD D2S 的 L7e/M1 宽度口径、Suzuki Swift Sedan 发动机与车身组合冲突、Aston Martin DBS 5.3 版本命名边界。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008578/index.html?utm_source=chatgpt.com "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://press.kia.com/es/es/home/models/sorento/sorento.html?utm_source=chatgpt.com "Sorento"
[3]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12/995458/?utm_source=chatgpt.com "Nissan Micra 1.2 Visia (3-Türer) (01/03 - 06/05): Technische Daten, Bilder, Preise | ADAC"
[4]: https://www.carmanualsonline.info/seat-leon-sc-2017-owner-s-manual/?srch=dimensions&utm_source=chatgpt.com "dimensions Seat Leon SC 2017 Owner's manual (332 Pages)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* Opel Movano B 前驱底盘与厢式车已按驾驶室、长度和车顶完整派生，并直接复用现有 Renault Master III X62 Phase II 尺寸组，不重复输出尺寸来源。Movano B 与对应 Master X62 的三维一致。([manualzz.com][1])
* 闭合 VW Crafter II 前驱厢式车和底盘驾驶室组合：厢式车覆盖 L3/L4/L5 与 H2/H3/H4，底盘覆盖单排 L3/L4/L5 和双排 L3/L4。([Scribd][2])
* 闭合 Vivaro B Platform Cab、NV300 Combi L1/L2、Transporter T5 五种长度/车顶外廓，以及 S-Class W221、ZD D2S、DBS V8 和 Chevrolet Express 标准轴距 Cargo。([汽车手册在线][3])
* 剩余 4 个 PENDING Ktype 均为需要继续拆分物理分支的记录：Movano B 后驱底盘、Movano B 后驱厢式车、Swift II Sedan 车身/发动机冲突、Hilux VI 驾驶室边界。

## 2. 当前批次进度

* READY 映射行：157
* 已覆盖输入 Ktype：96 / 100
* PENDING 输入 Ktype：4
* 已确认并被引用的尺寸组：78
* 本轮新增 READY 映射行：67
* 本轮首次创建尺寸组：24
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123359_scab_l2	123359	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123359_scab_l3	123359	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123359_dcab_l2	123359	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123359_dcab_l3	123359	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123360_scab_l2	123360	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123360_scab_l3	123360	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123360_dcab_l2	123360	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123360_dcab_l3	123360	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123363_l1h1	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l1h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l2h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l2h3	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l3h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l3h3	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l1h1	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l1h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l2h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l2h3	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l3h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l3h3	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123431	123431	Chassis Cab	Vivaro B	X82	2	EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	HIGH	L2 Platform Cab单一外廓。	READY
123432	123432	Chassis Cab	Vivaro B	X82	2	EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	HIGH	L2 Platform Cab单一外廓。	READY
123503	123503	Sedan	S-Class W221 Facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	HIGH	211 PS标注存在上游功率偏差，但生产期与车型边界对应W221改款版。	READY
123531_l3h2	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l3h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l4h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l4h4	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l5h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l5h4	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l3h2	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l3h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l4h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l4h4	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l5h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l5h4	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l3h2	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l3h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l4h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l4h4	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l5h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l5h4	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123538_scab_l3	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_scab_l4	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_scab_l5	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_dcab_l3	123538	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_dcab_l4	123538	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l3	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l4	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l5	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_dcab_l3	123539	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_dcab_l4	123539	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l3	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l4	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l5	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_dcab_l3	123540	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_dcab_l4	123540	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123561_l1h1	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H1-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l1h2	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H2-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h1	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H1-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h2	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H2-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h3	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H3-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123577	123577	Hatchback	D2S		3	EU-ZD-D2S-HATCHBACK-01	MEDIUM	欧洲L7e双座三门城市电动车。	READY
123799_l1h1	123799	MPV	NV300	X82		EU-NISSAN-NV300-X82-COMBI-L1H1-01	HIGH	输入未区分L1与L2车长。	READY
123799_l2h1	123799	MPV	NV300	X82		EU-NISSAN-NV300-X82-COMBI-L2H1-01	HIGH	输入未区分L1与L2车长。	READY
123876	123876	Coupe	DBS V8		2	EU-ASTON-MARTIN-DBS-V8-COUPE-01	MEDIUM	5.3升V8对应DBS V8；输入车型名含Vantage但发动机和功率不对应直六DBS Vantage。	READY
123910_2500	123910	Van	Express GMT610	GMT610		EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-2500-01	MEDIUM	标准轴距Cargo输入未区分2500与3500载重级别。	READY
123910_3500	123910	Van	Express GMT610	GMT610		EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-3500-01	MEDIUM	标准轴距Cargo输入未区分2500与3500载重级别。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	5248	1955	1971	Opel Vivaro B 2017.5 Owner's Manual – Vehicle dimensions	https://www.carmanualsonline.info/opel-vivaro-b-2017-5-owner-s-manual-2/?srch=dimensions
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	5096	1871	1479	Mercedes-Benz Public Archive – S 350 CDI 4MATIC BlueEFFICIENCY 2009–2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-CDI-4MATIC-BlueEFFICIENCY-2009---2010.xhtml?oid=191730299
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H1-01	4892	1904	1990	Volkswagen Transporter T5 panel van dimensions; Auto-Data T5 facelift panel van specifications	https://vandimensions.com/database/volkswagen/transporter-t5;https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-generation-7811
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H2-01	4892	1904	2176	Auto-Data Volkswagen Transporter T5 facelift Panel Van L1H2 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-102hp-l1h2-50137
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H1-01	5292	1904	1990	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H1 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-bmt-140hp-l2h1-50100
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H2-01	5292	1904	2176	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H2 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-140hp-l2h2-50166
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H3-01	5292	1904	2476	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H3 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-140hp-dsg-l2h3-50199
EU-ZD-D2S-HATCHBACK-01	2810	1500	1560	Quattroruote ZD D2S technical dimensions	https://www.quattroruote.it/listino/zd/d2s
EU-NISSAN-NV300-X82-COMBI-L1H1-01	4999	1956	1971	Nissan NV300 Combi official dimensions	https://www.nissan.re/vehicules/neufs/NV300-new-combi/performance.html
EU-NISSAN-NV300-X82-COMBI-L2H1-01	5399	1956	1971	Nissan NV300 Combi official dimensions	https://www.nissan.re/vehicules/neufs/NV300-new-combi/performance.html
EU-ASTON-MARTIN-DBS-V8-COUPE-01	4585	1829	1327	Automobile-Catalog Aston Martin DBS V8 5.3 specifications	https://www.automobile-catalog.com/car/1970/74225/aston_martin_dbs_v8.html
EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-2500-01	5692	2012	2149	Edmunds 2016 Chevrolet Express Cargo standard-wheelbase specifications	https://www.edmunds.com/chevrolet/express-cargo/2016/van/features-specs/
EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-3500-01	5692	2012	2159	Cars.com 2016 Chevrolet Express 3500 Cargo specifications	https://www.cars.com/research/chevrolet-express_3500-2016/specs/
```

## 5. 下一步优先处理

1. 闭合 `123361` Movano B RWD Chassis：区分单排/双排、L2/L3/L4、SRW/DRW，以及相应长度和高度。
2. 闭合 `123366` Movano B RWD Van：区分 L3/L4、H2/H3 和 SRW/DRW 高度差异。
3. 解决 `123758` Suzuki Swift II 的 Sedan 与 1.0 39 kW 发动机组合冲突，确认是否为上游 BodyStyle 错配。
4. 确认 `124036` Hilux VI 2.4 D 后驱在对应欧洲市场仅覆盖 Single Cab，还是还包含 Extra/Double Cab。

推进信号：CONTINUE

[1]: https://manualzz.com/doc/41561768/vauxhall-movano-van-owner-s-manual?utm_source=chatgpt.com "Vauxhall Movano Owner's Manual | Manualzz"
[2]: https://www.scribd.com/document/977961179/Volkswagen-CV-Crafter?utm_source=chatgpt.com "2017 Volkswagen Crafter Overview | PDF | Manual Transmission | Automatic Transmission"
[3]: https://www.carmanualsonline.info/opel-vivaro-b-2017-5-owner-s-manual-2/?srch=dimensions&utm_source=chatgpt.com "dimensions OPEL VIVARO B 2017.5 Owner's Manual (233 Pages)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 剩余 4 个 PENDING Ktype 已闭合：Movano B 后驱底盘及厢式车按长度、驾驶室、SRW/DRW 和车顶高度拆分；其资料明确给出 `2070 mm` 不含后视镜宽度及各分支三维。([汽车手册在线][1])
* Suzuki Swift II 已按实际三门/五门 Hatchback 与改款前后外廓拆分。
* Toyota Hilux VI 已按 Regular Cab、Xtracab、Double Cab 拆分。
* 已完成固定表头、唯一性、引用闭合、正整数三维、来源完整性及下载文件检查。

## 当前批次进度

* 输入 Ktype：100 / 100 已覆盖
* READY 映射：179
* PENDING 映射：0
* DIMENSION_GROUP：100
* 映射 `id` 重复：0
* 尺寸组孤立或缺失引用：0
* 尺寸及来源缺失：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123345_prefl	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123345_facelift	123345	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123346_prefl	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123346_facelift	123346	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123348	123348	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123349	123349	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123350	123350	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123356	123356	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123357	123357	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123358	123358	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123359_scab_l2	123359	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123359_scab_l3	123359	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123359_dcab_l2	123359	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123359_dcab_l3	123359	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123360_scab_l2	123360	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123360_scab_l3	123360	Chassis Cab	Movano B	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分单排驾驶室与底盘长度。	READY
123360_dcab_l2	123360	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123360_dcab_l3	123360	Chassis Cab	Movano B	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分双排驾驶室与底盘长度。	READY
123361_scab_l2	123361	Chassis Cab	Movano B	X62	2	EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L2-RWD-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_scab_l3_srw	123361	Chassis Cab	Movano B	X62	2	EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L3-SRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_scab_l3_drw	123361	Chassis Cab	Movano B	X62	2	EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L3-DRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_scab_l4_drw	123361	Chassis Cab	Movano B	X62	2	EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L4-DRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_dcab_l2_srw	123361	Chassis Cab	Movano B	X62	4	EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L2-SRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_dcab_l2_drw	123361	Chassis Cab	Movano B	X62	4	EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L2-DRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_dcab_l3_srw	123361	Chassis Cab	Movano B	X62	4	EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L3-SRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_dcab_l3_drw	123361	Chassis Cab	Movano B	X62	4	EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L3-DRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123361_dcab_l4_drw	123361	Chassis Cab	Movano B	X62	4	EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L4-DRW-01	HIGH	输入未区分驾驶室、长度及后轮形式。	READY
123362	123362	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123363_l1h1	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l1h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l2h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l2h3	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l3h2	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123363_l3h3	123363	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123364	123364	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123365_l1h1	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l1h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l2h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l2h3	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l3h2	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123365_l3h3	123365	Van	Movano B	X62		EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123366_l3h2_srw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-SRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123366_l3h3_srw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H3-SRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123366_l3h2_drw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-DRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123366_l3h3_drw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H3-DRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123366_l4h2_drw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L4H2-DRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123366_l4h3_drw	123366	Van	Movano B	X62		EU-OPEL-MOVANO-B-X62-VAN-L4H3-DRW-01	HIGH	输入未区分长度、车顶高度及后轮形式。	READY
123367	123367	MPV	Zafira C	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
123369	123369	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123370	123370	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123385	123385	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SUV-01	HIGH		READY
123387	123387	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SUV-01	HIGH		READY
123388	123388	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
123395	123395	Sedan	Tipo 356	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH		READY
123396	123396	Hatchback	Tipo 357	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH		READY
123397	123397	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
123398	123398	Wagon	Tipo 358	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH		READY
123400	123400	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH		READY
123422	123422	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123424	123424	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123425	123425	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123426	123426	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123427	123427	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123431	123431	Chassis Cab	Vivaro B	X82	2	EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	HIGH	L2 Platform Cab单一外廓。	READY
123432	123432	Chassis Cab	Vivaro B	X82	2	EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	HIGH	L2 Platform Cab单一外廓。	READY
123438	123438	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123447_scab_l2	123447	Chassis Cab	Master III X62 Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_scab_l3	123447	Chassis Cab	Master III X62 Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_dcab_l2	123447	Chassis Cab	Master III X62 Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123447_dcab_l3	123447	Chassis Cab	Master III X62 Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室与车长，按SCAB/DCAB及L2/L3外廓拆分。	READY
123503	123503	Sedan	S-Class W221 Facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	HIGH	211 PS标注存在上游功率偏差，但生产期与车型边界对应W221改款版。	READY
123530	123530	Sedan	Premio II	ZRT260	4	EU-TOYOTA-PREMIO-II-ZRT260-SEDAN-01	HIGH	1.8升前驱对应ZRT260车身。	READY
123531_l3h2	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l3h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l4h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l4h4	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l5h3	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123531_l5h4	123531	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l3h2	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l3h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l4h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l4h4	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l5h3	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123535_l5h4	123535	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l3h2	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l3h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l4h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l4h4	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l5h3	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	输入未区分长度和车顶高度。	READY
123537_l5h4	123537	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	输入未区分长度和车顶高度。	READY
123538_scab_l3	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_scab_l4	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_scab_l5	123538	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_dcab_l3	123538	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123538_dcab_l4	123538	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l3	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l4	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_scab_l5	123539	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_dcab_l3	123539	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123539_dcab_l4	123539	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l3	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l4	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_scab_l5	123540	Chassis Cab	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_dcab_l3	123540	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123540_dcab_l4	123540	Chassis Cab	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	输入未区分驾驶室和底盘长度。	READY
123561_l1h1	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H1-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l1h2	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H2-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h1	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H1-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h2	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H2-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123561_l2h3	123561	Van	Transporter T5 Facelift	7H		EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H3-01	MEDIUM	输入未区分轴距和车顶高度。	READY
123577	123577	Hatchback	D2S		3	EU-ZD-D2S-HATCHBACK-01	MEDIUM	欧洲L7e双座三门城市电动车。	READY
123729	123729	Hatchback	Rapid I Spaceback		5	EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	HIGH	输入Schrägheck对应Rapid Spaceback。	READY
123743	123743	Coupe	AMG GT I	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	HIGH	GT R宽体外廓。	READY
123745	123745	Convertible	AMG GT I	R190	2	EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	HIGH	基础GT Roadster窄体外廓。	READY
123747	123747	Convertible	AMG GT I	R190	2	EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	HIGH	GT C宽体Roadster外廓。	READY
123758_3dr_prefl	123758	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-PREFL-01	MEDIUM	输入Sedan与1.0 39 kW欧洲车型不符；按三门Hatchback改款前外廓修正。	READY
123758_5dr_prefl	123758	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-PREFL-01	MEDIUM	输入Sedan与1.0 39 kW欧洲车型不符；按五门Hatchback改款前外廓修正。	READY
123758_3dr_facelift	123758	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入Sedan与1.0 39 kW欧洲车型不符；按三门Hatchback改款后外廓修正。	READY
123758_5dr_facelift	123758	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-FACELIFT-01	MEDIUM	输入Sedan与1.0 39 kW欧洲车型不符；按五门Hatchback改款后外廓修正。	READY
123760	123760	Sedan	Corolla VIII E110	E110	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	HIGH		READY
123770	123770	Sedan	Nova 2105	VAZ-2105	4	EU-LADA-NOVA-2105-SEDAN-01	HIGH	Nova 1300对应VAZ-2105轿车。	READY
123772	123772	Targa	F355	F129	2	EU-FERRARI-F355-F129-TARGA-01	HIGH	F355 GTS可拆卸硬顶车身。	READY
123799_l1h1	123799	MPV	NV300	X82		EU-NISSAN-NV300-X82-COMBI-L1H1-01	HIGH	输入未区分L1与L2车长。	READY
123799_l2h1	123799	MPV	NV300	X82		EU-NISSAN-NV300-X82-COMBI-L2H1-01	HIGH	输入未区分L1与L2车长。	READY
123810_prefl	123810	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-PREFL-01	HIGH	同一Ktype跨越UM改款，按车长变化拆分。	READY
123810_facelift	123810	SUV	Sorento III	UM	5	EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	HIGH	同一Ktype跨越UM改款，按车长变化拆分。	READY
123815	123815	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123816	123816	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123817	123817	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123819	123819	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123820	123820	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123821	123821	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH	F54 Clubman六门外廓（四侧门及双开尾门）。	READY
123822_prefl	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123822_facelift	123822	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123823_prefl	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123823_facelift	123823	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖G30改款前后外廓，按长度变化拆分。	READY
123824	123824	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123825	123825	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
123826	123826	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123827	123827	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-QL-SUV-01	HIGH		READY
123828	123828	Hatchback	Soul II Facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH		READY
123830	123830	Hatchback	BX		5	EU-CITROEN-BX-HATCHBACK-19-01	MEDIUM	对应BX 19 Hatchback外廓。	READY
123831	123831	Wagon	BX		5	EU-CITROEN-BX-WAGON-19-01	MEDIUM	对应BX 19 Break/Wagon外廓。	READY
123835	123835	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123836	123836	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
123876	123876	Coupe	DBS V8		2	EU-ASTON-MARTIN-DBS-V8-COUPE-01	MEDIUM	5.3升V8对应DBS V8；输入车型名含Vantage但发动机和功率不对应直六DBS Vantage。	READY
123896	123896	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123897	123897	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123898	123898	Hatchback	Model S Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
123910_2500	123910	Van	Express GMT610	GMT610		EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-2500-01	MEDIUM	标准轴距Cargo输入未区分2500与3500载重级别。	READY
123910_3500	123910	Van	Express GMT610	GMT610		EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-3500-01	MEDIUM	标准轴距Cargo输入未区分2500与3500载重级别。	READY
123923	123923	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
123925	123925	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH		READY
123933	123933	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123934	123934	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	HIGH		READY
123947	123947	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	HIGH	澳洲市场SR Turbo外廓。	READY
123958_3dr_prefl	123958	Hatchback	Micra III	K12	3	EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-PREFL-01	MEDIUM	输入未区分门数且跨越改款，保留三门改款前分支。	READY
123958_5dr_prefl	123958	Hatchback	Micra III	K12	5	EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-PREFL-01	MEDIUM	输入未区分门数且跨越改款，保留五门改款前分支。	READY
123958_3dr_facelift	123958	Hatchback	Micra III	K12	3	EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入未区分门数且跨越改款，保留三门改款后分支。	READY
123958_5dr_facelift	123958	Hatchback	Micra III	K12	5	EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-FACELIFT-01	MEDIUM	输入未区分门数且跨越改款，保留五门改款后分支。	READY
123991	123991	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
123992	123992	Convertible	A5 II	F5	2	EU-AUDI-S5-II-F5-CABRIOLET-01	HIGH	S5前后保险杠外廓与普通A5不同。	READY
123993	123993	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
123994	123994	Convertible	A5 II	F5	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
123999	123999	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124000	124000	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124001	124001	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
124002	124002	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country升高车身，不复用普通V90尺寸组。	READY
124006	124006	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
124007	124007	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
124009	124009	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH	GD三门Coupe物理外廓。	READY
124036_scab	124036	Pickup	Hilux VI	LN145	2	EU-TOYOTA-HILUX-VI-LN145-PICKUP-REGULAR-CAB-01	HIGH	输入未区分驾驶室；对应单排驾驶室分支。	READY
124036_xtracab	124036	Pickup	Hilux VI	LN150	2	EU-TOYOTA-HILUX-VI-LN150-PICKUP-XTRACAB-01	MEDIUM	输入未区分驾驶室；对应加长驾驶室分支。	READY
124036_dcab	124036	Pickup	Hilux VI	LN145	4	EU-TOYOTA-HILUX-VI-LN145-PICKUP-DOUBLE-CAB-01	HIGH	输入未区分驾驶室；对应双排驾驶室分支。	READY
124050_3dr	124050	Hatchback	Leon III Facelift	5F	3	EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	MEDIUM	输入未区分SC三门与五门车身。	READY
124050_5dr	124050	Hatchback	Leon III Facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	MEDIUM	输入未区分SC三门与五门车身。	READY
124051	124051	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	HIGH		READY
124068	124068	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	HIGH		READY
124077	124077	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_801-900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW 5 Series Sedan official specifications, valid from 09/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286565EN/419613
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW 5 Series Sedan official specifications, valid from 05/2020	https://www.press.bmwgroup.com/global/article/attachment/T0314291EN/457886
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441	MINI The new MINI Clubman official press information	https://www.press.bmwgroup.com/global/article/detail/T0222325EN/the-new-mini-clubman
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L2-RWD-01	5643	2070	2284	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L3-SRW-01	6293	2070	2283	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L3-DRW-01	6193	2070	2283	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-SCAB-L4-DRW-01	6843	2070	2273	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L2-SRW-01	5643	2070	2272	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L2-DRW-01	5643	2070	2301	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L3-SRW-01	6293	2070	2285	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L3-DRW-01	6193	2070	2285	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-CHASSIS-DCAB-L4-DRW-01	6843	2070	2286	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	5048	2070	2307	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	5048	2070	2500	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	5548	2070	2499	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	5548	2070	2749	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	6198	2070	2488	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	6198	2070	2744	Vauxhall Movano B / Renault Master III X62 owner's manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L3H2-SRW-01	6198	2070	2527	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L3H3-SRW-01	6198	2070	2786	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L3H2-DRW-01	6198	2070	2549	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L3H3-DRW-01	6198	2070	2815	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L4H2-DRW-01	6848	2070	2557	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-MOVANO-B-X62-VAN-L4H3-DRW-01	6848	2070	2808	Vauxhall Movano B Owner's Manual – vehicle dimensions	https://manuals.plus/m/ae64e7d174d3726f01ebb3ff979f620923db99a5032ce0098ba29aaadf07d2f4
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685	Opel Zafira Tourer 2017 Owner's Manual – Vehicle dimensions	https://www.carmanualsonline.info/opel-zafira-tourer-2017-owners-manual/?srch=dimensions
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655	ADAC Audi Q5 2.0 TDI quattro 8R – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/q5/8r-facelift/241199/
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436	Alfa Romeo Giulia official technical specifications	https://www.media.stellantis.com/uploads/me/ME/2018/Alfa-Romeo/Technical-sheet/0618_Alfa-Romeo_Giulia.pdf
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Fiat Tipo official technical specifications	https://www.media.stellantis.com/uploads/pl/model-document/new_tipo_pl-6087c76786e2c.pdf
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Fiat Tipo official technical specifications	https://www.media.stellantis.com/uploads/pl/model-document/new_tipo_pl-6087c76786e2c.pdf
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659	CarExpert 2017 Audi Q5 Design exterior dimensions	https://www.carexpert.com.au/audi/q5/2017/design/exterior-and-dimensions
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514	Fiat Tipo official technical specifications	https://www.media.stellantis.com/uploads/pl/model-document/new_tipo_pl-6087c76786e2c.pdf
EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	4697	1882	1676	ŠKODA The new KODIAQ official press kit	https://www.skoda-storyboard.com/en/press-kits/new-skoda-kodiaq-press-kit/
EU-OPEL-VIVARO-B-X82-PLATFORM-CAB-L2-01	5248	1955	1971	Opel Vivaro B 2017.5 Owner's Manual – Vehicle dimensions	https://www.carmanualsonline.info/opel-vivaro-b-2017-5-owner-s-manual-2/?srch=dimensions
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-01	5096	1871	1479	Mercedes-Benz Public Archive – S 350 CDI 4MATIC BlueEFFICIENCY 2009–2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-CDI-4MATIC-BlueEFFICIENCY-2009---2010.xhtml?oid=191730299
EU-TOYOTA-PREMIO-II-ZRT260-SEDAN-01	4600	1695	1475	Toyota 75 Years Vehicle Lineage – Second-generation Premio specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008578/index.html
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen France new Crafter technical release	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://media.volkswagen.fr/le-nouveau-crafter-une-nouvelle-dimension-plus-econome-fonctionnel-et-fiable-que-jamais-communique/?lang=fr
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321	Volkswagen Crafter 2017 Self Study Programme 566; Volkswagen Crafter Chassis official model information	https://pdfcoffee.com/crafter-2017-pdf-free.html;https://www.volkswagen-vans.co.uk/en/new-vehicles/crafter-chassis.html
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H1-01	4892	1904	1990	Volkswagen Transporter T5 panel van dimensions; Auto-Data T5 facelift panel van specifications	https://vandimensions.com/database/volkswagen/transporter-t5;https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-generation-7811
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L1H2-01	4892	1904	2176	Auto-Data Volkswagen Transporter T5 facelift Panel Van L1H2 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-102hp-l1h2-50137
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H1-01	5292	1904	1990	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H1 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-bmt-140hp-l2h1-50100
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H2-01	5292	1904	2176	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H2 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-140hp-l2h2-50166
EU-VW-TRANSPORTER-T5-FACELIFT-VAN-L2H3-01	5292	1904	2476	Auto-Data Volkswagen Transporter T5 facelift Panel Van L2H3 specifications	https://www.auto-data.net/en/volkswagen-transporter-t5-facelift-2009-panel-van-2.0-tdi-140hp-dsg-l2h3-50199
EU-ZD-D2S-HATCHBACK-01	2810	1500	1560	Quattroruote ZD D2S technical dimensions	https://www.quattroruote.it/listino/zd/d2s
EU-SKODA-RAPID-I-SPACEBACK-HATCHBACK-01	4304	1706	1459	ADAC Škoda Rapid Spaceback manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/skoda/rapid/1generation/238509/
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	4551	2007	1284	Auto Motor und Sport Mercedes-AMG GT R technical data	https://www.auto-motor-und-sport.de/test/mercedes-amg-gt-r/technische-daten/
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	4544	1939	1259	Mercedes-Benz Media AMG GT Roadster technical data	https://media.mercedes-benz.fr/mercedes-amg-gt-roadster-et-mercedes-amg-gt-c-roadster/
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	4551	2007	1260	Auto Express Mercedes-AMG GT C Roadster specifications	https://www.autoexpress.co.uk/mercedes/amg-gt/roadster/prices-specs/77773/gt-c-2dr-auto
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-PREFL-01	3745	1575	1350	Automobile-Catalog 1994 Suzuki Swift 1.0 GL 3-door specifications	https://www.automobile-catalog.com/car/1994/3334490/suzuki_swift_1_0_gl_3-door.html
EU-SUZUKI-SWIFT-II-HATCHBACK-5D-PREFL-01	3845	1575	1380	Automobile-Catalog 1994 Suzuki Swift 1.0 GL 5-door specifications	https://www.automobile-catalog.com/car/1994/3334655/suzuki_swift_1_0_gl_5-door.html
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-FACELIFT-01	3745	1590	1350	Automobile-Catalog 1998 Suzuki Swift 1.0 GLS 3-door specifications	https://www.automobile-catalog.com/car/1998/3334925/suzuki_swift_1_0_gls_3-door.html
EU-SUZUKI-SWIFT-II-HATCHBACK-5D-FACELIFT-01	3845	1590	1380	Automobile-Catalog 1998 Suzuki Swift 1.0 GL 5-door specifications	https://www.automobile-catalog.com/car/1998/3334835/suzuki_swift_1_0_gl_5-door.html
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	4295	1690	1385	Carsales Toyota Corolla E110 dimensions	https://www.carsales.com.au/research/toyota/corolla/2000/ultima-seca/
EU-LADA-NOVA-2105-SEDAN-01	4130	1620	1446	Auto-Data Lada 2105 1.3 specifications	https://www.auto-data.net/en/lada-2105-1.3-64hp-13306
EU-FERRARI-F355-F129-TARGA-01	4250	1900	1170	Ferrari F355 GTS official technical specifications	https://www.ferrari.com/en-EN/auto/f355-gts
EU-NISSAN-NV300-X82-COMBI-L1H1-01	4999	1956	1971	Nissan NV300 Combi official dimensions	https://www.nissan.re/vehicules/neufs/NV300-new-combi/performance.html
EU-NISSAN-NV300-X82-COMBI-L2H1-01	5399	1956	1971	Nissan NV300 Combi official dimensions	https://www.nissan.re/vehicules/neufs/NV300-new-combi/performance.html
EU-KIA-SORENTO-III-UM-SUV-PREFL-01	4780	1890	1685	Kia Europe Sorento 2014 official specifications	https://press.kia.com/content/kiapress/eu/en/home/models/sorento/sorento-2014.html
EU-KIA-SORENTO-III-UM-SUV-FACELIFT-01	4800	1890	1685	Kia France facelift Sorento official specifications	https://press.kia.com/fr/fr/home/press-releases/2017/Sorento-nouveau-design.html
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	ADAC Nissan Micra K14 – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k14/317816/
EU-KIA-SPORTAGE-IV-QL-SUV-01	4480	1855	1635	Kia Europe Sportage 2016 official specifications	https://prod2-press.kia.com/eu/en/home/models/sportage/sportage-2016.html
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618	Kia Europe Soul official technical specifications	https://press.kia.com/content/kiapress/eu/en/home/models/soul/soul-2014.html
EU-CITROEN-BX-HATCHBACK-19-01	4230	1660	1360	CarsGuide Citroën BX 1991 dimensions	https://www.carsguide.com.au/citroen/bx/car-dimensions/1991
EU-CITROEN-BX-WAGON-19-01	4399	1660	1430	CarsGuide Citroën BX 1990 Wagon dimensions	https://www.carsguide.com.au/citroen/bx/car-dimensions/1990
EU-ASTON-MARTIN-DBS-V8-COUPE-01	4585	1829	1327	Automobile-Catalog Aston Martin DBS V8 5.3 specifications	https://www.automobile-catalog.com/car/1970/74225/aston_martin_dbs_v8.html
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445	Auto-Data Tesla Model S facelift 2016 dimensions	https://www.auto-data.net/en/tesla-model-s-facelift-2016-generation-5637
EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-2500-01	5692	2012	2149	Edmunds 2016 Chevrolet Express Cargo standard-wheelbase specifications	https://www.edmunds.com/chevrolet/express-cargo/2016/van/features-specs/
EU-CHEVROLET-EXPRESS-GMT610-CARGO-STANDARD-3500-01	5692	2012	2159	Cars.com 2016 Chevrolet Express 3500 Cargo specifications	https://www.cars.com/research/chevrolet-express_3500-2016/specs/
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481	Maserati official Quattroporte technical specifications	https://www.media.stellantis.com/uk-en/maserati/press/all-new-maserati-quattroporte-unveiled-at-naias-2013
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	4570	1800	1440	Carsales Hyundai Elantra AD SR Turbo specifications	https://www.carsales.com.au/research/hyundai/elantra/2016/sr-turbo/
EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-PREFL-01	3715	1660	1540	ADAC Nissan Micra K12 three-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12/995458/
EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-PREFL-01	3715	1660	1540	Automobile-Catalog Nissan Micra K12 3/5-door specifications	https://www.automobile-catalog.com/car/2003/2198975/nissan_micra_1_2_65.html
EU-NISSAN-MICRA-III-K12-HATCHBACK-3D-FACELIFT-01	3719	1660	1540	ADAC Nissan Micra K12 facelift three-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12-facelift/203479/
EU-NISSAN-MICRA-III-K12-HATCHBACK-5D-FACELIFT-01	3719	1660	1540	ADAC Nissan Micra K12 facelift five-door manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k12-facelift/203492/
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	AustralianCar.Reviews Audi F5 A5 Cabriolet body and dimensions	https://australiancar.reviews/review-audi-f5-a5-cabriolet-2017-on/
EU-AUDI-S5-II-F5-CABRIOLET-01	4692	1846	1382	ADAC Audi S5 F5 Cabriolet – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a5/f5-facelift/315604/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Support V90 dimensions	https://www.volvocars.com/sg/support/car/v90/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/871e942e897ca77dc0a801511788660a/
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo Support V90 Cross Country 2017 dimensions	https://www.volvocars.com/uk/support/car/v90-cross-country/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/871e942e897ca77dc0a801511788660a/
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Support S90 dimensions	https://www.volvocars.com/sg/support/car/s90/19w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_766ee075f0e03896c0a8015109ee0749/
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470	ADAC Hyundai i30 Coupe manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/hyundai/i30/2generation/235199/
EU-TOYOTA-HILUX-VI-LN145-PICKUP-REGULAR-CAB-01	4690	1665	1650	Drom Toyota Hilux 2.4D Regular Cab specifications	https://www.drom.ru/catalog/toyota/hilux_pick_up/250233/
EU-TOYOTA-HILUX-VI-LN150-PICKUP-XTRACAB-01	5035	1665	1695	Toyota Media Site Hilux 1997–2005; Drom Toyota Hilux 2.4D Xtracab specifications	https://media.toyota.co.uk/vehicles/hilux-1997-2005/;https://www.drom.ru/catalog/toyota/hilux_pick_up/250234/
EU-TOYOTA-HILUX-VI-LN145-PICKUP-DOUBLE-CAB-01	4790	1665	1695	Drom Toyota Hilux 2.4D Double Cab specifications	https://www.drom.ru/catalog/toyota/hilux_pick_up/250235/
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446	SEAT Leon SC 2017 Owner's Manual – technical dimensions	https://www.carmanualsonline.info/seat-leon-sc-2017-owner-s-manual/?srch=dimensions
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	ADAC SEAT Leon 5F facelift manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/seat/leon/5f-facelift/263274/
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454	ADAC SEAT Leon ST 1.6 TDI 5F Facelift – manufacturer specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/seat/leon/5f-facelift/263322/
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654	Volkswagen Tiguan official dimensions	https://www.volkswagen.co.uk/assets/common/pdf/brochures/tiguan-nf-dimensions.pdf
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673	Volkswagen Tiguan official dimensions	https://www.volkswagen.co.uk/assets/common/pdf/brochures/tiguan-nf-dimensions.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_801-900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carmanualsonline.info/vauxhall-movano-b-2018-5-owner-s-manual/?srch=width "https://www.carmanualsonline.info/vauxhall-movano-b-2018-5-owner-s-manual/?srch=width"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_801-900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_801-900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（800 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（412 行）

