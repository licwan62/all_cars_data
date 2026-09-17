# 任务：all 第 3901-4000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0040__080784a7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3901-4000 行

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
all 第 3901-4000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-8-F91-M8-CONVERTIBLE-01	4867	1907	1353
EU-BMW-8-F92-M8-COUPE-01	4867	1907	1362
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339
EU-BMW-8-G14-M850I-CONVERTIBLE-01	4851	1902	1345
EU-BMW-8-G15-840D-COUPE-01	4843	1902	1341
EU-BMW-8-G15-M850I-COUPE-01	4851	1902	1346
EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	4447	1821	1582
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	4419	1748	1466
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466
EU-PEUGEOT-301-I-SEDAN-PREFL-01	4442	1748	1466
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 allroad c8	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	170	231	Nov 2018	-	2024-03-01	136392
Audi	A6 c8	S6 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	257	349	Mar 2019	-	2024-03-01	136393
Audi	A6 c8 avant	S6 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	257	349	Mar 2019	-	2024-03-01	136394
Audi	A6 allroad c8	55 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	257	349	Mar 2019	-	2024-03-01	136395
Aston Martin	Dbs volante	Superleggera	Cabriolet	Heckantrieb	Benzin	533	725	Apr 2019	-	2024-03-01	136396
Mazda	3	1.5 Skyactiv-g	Stufenheck	Frontantrieb	Benzin	88	120	Nov 2018	-	2024-03-01	136421
Mazda	3	1.5 Skyactiv-g	Schrägheck	Frontantrieb	Benzin	88	120	Jun 2019	-	2025-06-01	136428
Audi	A5	40 TDI Quattro	Cabriolet	Allrad	Diesel	140	190	Mar 2017	-	2024-07-01	136432
Mercedes-benz	E-Klasse	E 200 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	145	197	Jun 2019	Oct 2023	2024-03-01	136441
Mercedes-benz	E-Klasse	E 200 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	145	197	Jun 2019	Oct 2023	2024-03-01	136444
Mercedes-benz	E-Klasse	E 300 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	190	258	Jun 2019	Oct 2023	2024-03-01	136445
Mercedes-benz	E-Klasse	E 200 EQ Boost	Kombi	Heckantrieb	Benzin/Elektro	145	197	Jun 2019	Oct 2023	2024-03-01	136446
Mercedes-benz	E-Klasse	E 200 EQ Boost 4-matic	Kombi	Allrad	Benzin/Elektro	145	197	Jun 2019	Oct 2023	2024-03-01	136447
Mercedes-benz	E-Klasse	E 300 EQ Boost	Kombi	Heckantrieb	Benzin/Elektro	190	258	Jun 2019	Oct 2023	2024-03-01	136448
Mercedes-benz	E-Klasse	E 200 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	145	197	Jun 2019	-	2024-03-01	136449
Mercedes-benz	E-Klasse	E 200 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	145	197	Jun 2019	-	2024-03-01	136450
Mercedes-benz	E-Klasse	E 300 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	190	258	Jun 2019	-	2024-03-01	136451
Mercedes-benz	E-Klasse	E 200 EQ Boost	Cabriolet	Heckantrieb	Benzin/Elektro	145	197	Jun 2019	-	2024-03-01	136452
Mercedes-benz	E-Klasse	E 200 EQ Boost 4-matic	Cabriolet	Allrad	Benzin/Elektro	145	197	Jun 2019	-	2024-03-01	136453
Mercedes-benz	E-Klasse	E 300 EQ Boost	Cabriolet	Heckantrieb	Benzin/Elektro	190	258	Jun 2019	-	2024-03-01	136454
Audi	A7 sportback	S7 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	257	349	Mar 2019	-	2024-03-01	136458
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	140	190	Jul 2018	Oct 2020	2024-03-01	136459
Audi	A3	40 TDI Quattro	Schrägheck	Allrad	Diesel	135	184	Jul 2018	Oct 2020	2024-03-01	136460
Audi	A3	40 TDI Quattro	Stufenheck	Allrad	Diesel	135	184	Jul 2018	Jul 2019	2024-03-01	136461
Audi	A3	40 Tfsi Quattro	Stufenheck	Allrad	Benzin	140	190	Jul 2018	Oct 2020	2024-03-01	136462
Audi	A3	40 Tfsi Quattro	Cabriolet	Allrad	Benzin	140	190	Nov 2018	Oct 2020	2024-03-01	136463
Audi	A4 b9	30 TDI	Stufenheck	Frontantrieb	Diesel	90	122	May 2016	Nov 2019	2024-03-01	136464
Audi	A4 b9 avant	30 TDI	Kombi	Frontantrieb	Diesel	90	122	Oct 2018	Oct 2020	2026-04-01	136465
Audi	A4 b9 avant	40 Tfsi G-tron	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	125	170	Nov 2016	-	2024-03-01	136466
Audi	A5	50 TDI Quattro	Coupe	Allrad	Diesel	210	286	Jan 2017	Nov 2020	2026-07-01	136467
Audi	A5	35 TDI	Coupe	Frontantrieb	Diesel	110	150	May 2017	Feb 2020	2024-03-01	136468
Audi	A5	50 TDI Quattro	Schrägheck	Allrad	Diesel	210	286	Jan 2017	-	2026-07-01	136469
Audi	A5	40 Tfsi G-tron	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	125	170	Feb 2017	-	2024-03-01	136470
Audi	A5	50 TDI Quattro	Cabriolet	Allrad	Diesel	210	286	Nov 2016	-	2026-07-01	136471
Audi	A5	S5 TDI Mild Hybrid Quattro	Coupe	Allrad	Diesel/Elektro	255	347	Dec 2018	Nov 2020	2026-07-01	136473
Audi	A5	S5 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	255	347	Dec 2018	-	2026-07-01	136474
Opel	Grandland	1.6 Turbo Hybrid4	SUV	Allrad	Benzin/Elektro	221	300	Jun 2019	-	2025-02-03	136486
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	175	238	Apr 2019	-	2024-03-01	136487
BMW	3	320 I	Kombi	Heckantrieb	Benzin	135	184	Nov 2019	-	2024-03-01	136488
BMW	3	330 I	Kombi	Heckantrieb	Benzin	190	258	Jul 2019	-	2024-03-01	136489
BMW	3	330 I Xdrive	Kombi	Allrad	Benzin	190	258	Jul 2019	-	2024-03-01	136490
BMW	3	M 340 I Xdrive	Kombi	Allrad	Benzin	275	374	Nov 2019	-	2024-03-01	136491
BMW	3	318 D	Kombi	Heckantrieb	Diesel	100	136	Nov 2019	Jul 2020	2024-03-01	136492
BMW	3	318 D	Kombi	Heckantrieb	Diesel	110	150	Nov 2019	Jul 2020	2024-03-01	136493
BMW	3	320 D	Kombi	Heckantrieb	Diesel	120	163	Jul 2019	Feb 2020	2024-03-01	136494
BMW	3	320 D	Kombi	Heckantrieb	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	136495
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	120	163	Jul 2019	Feb 2020	2024-03-01	136496
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	136497
BMW	3	330 D Xdrive	Kombi	Allrad	Diesel	195	265	Jul 2019	-	2024-03-01	136498
BMW	3	330 E Plug-in-hybrid	Kombi	Heckantrieb	Benzin/Elektro	215	292	Jul 2020	-	2024-03-01	136500
Suzuki	Wagon r+	1	Schrägheck	Frontantrieb	Benzin	39	53	Jul 2001	Dec 2006	2024-03-01	136501
Volvo	S60 iii	T6 AWD	Stufenheck	Allrad	Benzin	228	310	May 2019	Dec 2021	2024-05-01	136516
BMW	8	840 I	Coupe	Heckantrieb	Benzin	250	340	Jul 2019	Oct 2020	2024-03-01	136517
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	250	340	Jul 2019	-	2024-03-01	136518
BMW	8	M 850 I Xdrive	Coupe	Allrad	Benzin	390	530	Jul 2019	-	2024-03-01	136519
BMW	8	840 D Xdrive	Coupe	Allrad	Diesel	235	320	Jul 2019	Oct 2020	2024-03-01	136520
Mercedes-benz	Cla	CLA 180 D	Kombi	Frontantrieb	Diesel	85	116	Jun 2019	-	2024-03-01	136521
Mercedes-benz	Cla	CLA 200 D	Kombi	Frontantrieb	Diesel	110	150	Jun 2019	-	2024-03-01	136522
Mercedes-benz	Cla	CLA 220 D	Kombi	Frontantrieb	Diesel	140	190	Jun 2019	-	2024-03-01	136523
Mercedes-benz	Cla	CLA 180	Kombi	Frontantrieb	Benzin	100	136	Jun 2019	-	2024-03-01	136524
Mercedes-benz	Cla	CLA 200	Kombi	Frontantrieb	Benzin	120	163	Jun 2019	-	2024-03-01	136525
Mercedes-benz	Cla	CLA 220	Kombi	Frontantrieb	Benzin	140	190	Jun 2019	-	2024-03-01	136526
Mercedes-benz	Cla	CLA 250	Kombi	Frontantrieb	Benzin	165	224	Jun 2019	-	2024-03-01	136527
Mercedes-benz	Cla	CLA 250 4-matic	Kombi	Allrad	Benzin	165	224	Jun 2019	-	2024-03-01	136528
Mercedes-benz	Cla	AMG CLA 35 4-matic	Kombi	Allrad	Benzin	225	306	Jun 2019	-	2024-03-01	136529
Peugeot	208 ii	1.2 Puretech 100	Schrägheck	Frontantrieb	Benzin	74	101	Jun 2019	-	2024-03-01	136530
Peugeot	208 ii	1.2 Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Jun 2019	-	2024-03-01	136531
Peugeot	208 ii	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	75	102	Jun 2019	-	2024-03-01	136532
Peugeot	208 ii	E-208	Schrägheck	Frontantrieb	Elektro	100	136	Jun 2019	-	2024-03-01	136533
Volvo	S60 iii	T8 Hybrid Polestar AWD	Stufenheck	Allrad	Benzin/Elektro	310	422	May 2019	Dec 2022	2024-05-01	136535
Ford	Fiesta vii van	1.1 Ti-vct	Kasten/Schrägheck	Frontantrieb	Benzin	52	71	Apr 2019	-	2024-03-01	136545
Ford	Fiesta vii van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	Apr 2019	-	2024-03-01	136546
Ford	Fiesta vii van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	103	140	Apr 2019	-	2024-03-01	136547
Ford	Kuga ii van	1.5 Ecoboost	Kasten/SUV	Frontantrieb	Benzin	88	120	Jun 2019	Dec 2019	2024-05-01	136548
Ford	Kuga ii van	1.5 Ecoboost 4X4	Kasten/SUV	Allrad	Benzin	129	176	Jun 2019	Dec 2019	2024-05-01	136549
Ford	Kuga ii van	2.0 Tdci	Kasten/SUV	Frontantrieb	Diesel	88	120	Sep 2014	Dec 2019	2026-05-01	136550
Volvo	S60 iii	T5 AWD	Stufenheck	Allrad	Benzin	187	254	May 2019	Dec 2021	2024-05-01	136552
Volvo	S60 iii	T5 AWD	Stufenheck	Allrad	Benzin	183	249	May 2019	Dec 2021	2024-05-01	136553
BMW	2	218 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	103	140	Mar 2018	Oct 2021	2024-03-01	136564
BMW	2	220 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	140	190	Nov 2014	Oct 2021	2024-03-01	136567
BMW	2	218 I	Kasten/Großraumlimousine	Frontantrieb	Benzin	103	140	Apr 2017	-	2025-02-03	136568
BMW	2	220 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	140	190	Jul 2014	-	2024-03-01	136570
Mercedes-benz	C-Klasse	C 300 4-matic	Kombi	Allrad	Benzin	190	258	May 2018	Feb 2021	2024-03-01	136578
BMW	3	330 D Xdrive	Kasten/Kombi	Allrad	Diesel	190	258	Mar 2013	Jun 2019	2024-03-01	136579
BMW	5	520 D Xdrive	Kasten/Kombi	Allrad	Diesel	140	190	Jul 2017	Nov 2019	2025-02-03	136586
BMW	5	530 D Xdrive	Kasten/Kombi	Allrad	Diesel	195	265	Mar 2017	-	2024-03-01	136588
BMW	X1	Sdrive 20 D	Kasten/SUV	Frontantrieb	Diesel	140	190	Nov 2015	May 2022	2024-03-01	136593
Citroën	C3 iii van	Puretech 82	Kasten/Schrägheck	Frontantrieb	Benzin	61	83	Mar 2019	-	2024-03-01	136596
Citroën	C3 iii van	Puretech 110	Kasten/Schrägheck	Frontantrieb	Benzin	81	110	Mar 2019	-	2024-03-01	136597
Citroën	C3 iii van	Bluehdi 75	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Mar 2019	-	2024-03-01	136598
Citroën	C3 iii van	Bluehdi 100	Kasten/Schrägheck	Frontantrieb	Diesel	75	102	Mar 2019	-	2024-03-01	136599
Citroën	C3 iii van	Bluehdi 100	Kasten/Schrägheck	Frontantrieb	Diesel	73	99	Mar 2019	-	2024-03-01	136600
Citroën	C3 aircross ii van	Puretech 82	Kasten/SUV	Frontantrieb	Benzin	60	82	May 2019	-	2024-03-01	136601
Peugeot	301	1.2 Puretech 82	Stufenheck	Frontantrieb	Benzin	61	83	Feb 2018	-	2024-03-01	136611
BMW	X3	Xdrive M40 I	Kasten/SUV	Allrad	Benzin	265	360	Aug 2017	Aug 2019	2024-03-01	136613
BMW	X3	Sdrive 18 D	Kasten/SUV	Heckantrieb	Diesel	110	150	Apr 2018	-	2024-03-01	136614
Citroën	C-Elysee	1.2 Puretech 82	Stufenheck	Frontantrieb	Benzin	61	83	Feb 2018	-	2024-03-01	136616
Citroën	C3 aircross ii van	Puretech 82	Kasten/SUV	Frontantrieb	Benzin	81	110	May 2019	-	2024-03-01	136619
Citroën	C3 aircross ii van	1.6 Bluehdi 100	Kasten/SUV	Frontantrieb	Diesel	73	99	May 2019	-	2024-03-01	136620
Citroën	C3 aircross ii van	1.5 Bluehdi 100	Kasten/SUV	Frontantrieb	Diesel	73	99	May 2019	-	2024-03-01	136624


--- Round 1 / 首次发送 ---
更新点

* 已按缓存优先模式完成首轮聚类，23 个 Ktype 直接关联 16 个历史尺寸组，无需重复抓取尺寸。
* 已优先闭合 A6 allroad、Mazda 3 BP、A3 8V facelift、Grandland X、Model 3、Volvo S60 III、BMW G15、奔驰 S205、BMW G31、X3 G01、Peugeot 301 与 C-Elysée。
* Audi S7 暂未建组：现有资料对 C8 S7/A7 的长度和高度存在不同口径，需先确认 2019 年 257 kW TDI 的具体外廓，避免错误覆盖或复用。([汽车数据][1])

当前批次进度

* 输入 Ktype：100
* READY 映射：23
* PENDING 映射：77
* 本轮复用既有尺寸组：16
* 本轮首次创建尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136392	136392	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
136395	136395	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
136421	136421	Sedan	Mazda 3 IV (BP)	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH		READY
136428	136428	Hatchback	Mazda 3 IV (BP)	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136459	136459	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
136460	136460	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
136461	136461	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136462	136462	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136463	136463	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
136486	136486	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH		READY
136487	136487	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
136516	136516	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136519	136519	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-M850I-COUPE-01	HIGH		READY
136520	136520	Coupe	8 Series G15	G15	2	EU-BMW-8-G15-840D-COUPE-01	HIGH		READY
136535	136535	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136552	136552	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136553	136553	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136578	136578	Wagon	C-Class W205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136586	136586	Wagon	5 Series G30/G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	商用分类未改变G31旅行车外廓。	READY
136588	136588	Wagon	5 Series G30/G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	商用分类未改变G31旅行车外廓。	READY
136611	136611	Sedan	Peugeot 301 I facelift		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH		READY
136614	136614	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	商用分类未改变G01 SUV外廓。	READY
136616	136616	Sedan	C-Elysée I facelift		4	EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 集中闭合 Audi S6 Sedan、S6 Avant、S7 Sportback 和 Aston Martin DBS Volante 四个新尺寸组。
2. 处理跨 facelift 的 A4 B9、A5 F5 与 Mercedes-Benz W213/S213/C238/A238 Ktype，确认是否必须派生 `prefl`、`facelift` 行。
3. 按车身族批量处理 BMW G21、CLA X118、Peugeot 208 II、Fiesta/Kuga Van、Citroën C3/C3 Aircross Van。
4. 最后处理 BMW F45/F46、F31、X1 F48 等需要区分车身长度或改款边界的商用分类行。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s7-sportback-c8-generation-7071 "Audi S7 Sportback (C8) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 首次闭合 Audi S6 C8 Sedan、S6 C8 Avant、S7 C8 Sportback 与 Aston Martin DBS Superleggera Volante 四个尺寸组。对应三维分别为 4954×1886×1446、4954×1886×1481、4979×1908×1417 和 4715×1970×1295 mm。([汽车数据网][1])
* Audi A4 B9 的 136464、136465、136466 跨越已确认的 pre-facelift、2018 中期改款和 2019 facelift 外廓，已拆分映射；因 2019 三维与同名历史组冲突，保留历史组并新建下一序号尺寸组。([汽车数据网][2])
* Audi A5 F5 的 136432、136467、136469、136471 按改款前后拆分；136468 与 136470 仅关联改款前现有尺寸组。既有尺寸组未重复抓取或输出。
* 本轮新增完成 13 个输入 Ktype，共新增或修改 22 条映射记录。

当前批次进度

* 输入 Ktype：100
* READY Ktype：36
* PENDING Ktype：64
* READY 映射行：45
* 当前已引用尺寸组：32
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136393	136393	Sedan	S6 C8	4A2	4	EU-AUDI-S6-C8-4A2-SEDAN-01	HIGH		READY
136394	136394	Wagon	S6 C8	4A5	5	EU-AUDI-S6-C8-4A5-AVANT-01	HIGH		READY
136396	136396	Convertible	DBS Superleggera Volante		2	EU-ASTON-MARTIN-DBS-SUPERLEGGERA-VOLANTE-CONVERTIBLE-01	HIGH		READY
136432_prefl	136432	Convertible	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136432_facelift	136432	Convertible	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136458	136458	Hatchback	S7 Sportback C8	4KA	5	EU-AUDI-S7-C8-4KA-SPORTBACK-01	HIGH		READY
136464_prefl	136464	Sedan	A4 B9 pre-facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136464_facelift2018	136464	Sedan	A4 B9 facelift 2018	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136464_facelift2019	136464	Sedan	A4 B9 facelift 2019	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136465_facelift2018	136465	Wagon	A4 B9 facelift 2018	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	HIGH	Ktype跨越两次不同外廓改款，按阶段拆分。	READY
136465_facelift2019	136465	Wagon	A4 B9 facelift 2019	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	Ktype跨越两次不同外廓改款，按阶段拆分。	READY
136466_prefl	136466	Wagon	A4 B9 pre-facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136466_facelift2018	136466	Wagon	A4 B9 facelift 2018	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136466_facelift2019	136466	Wagon	A4 B9 facelift 2019	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136467_prefl	136467	Coupe	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136467_facelift	136467	Coupe	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136468	136468	Coupe	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
136469_prefl	136469	Hatchback	A5 F5 pre-facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136469_facelift	136469	Hatchback	A5 F5 facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136470	136470	Hatchback	A5 F5 pre-facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
136471_prefl	136471	Convertible	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136471_facelift	136471	Convertible	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-S6-C8-4A2-SEDAN-01	4954	1886	1446	Auto-Data.net	https://www.auto-data.net/en/audi-s6-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36864
EU-AUDI-S6-C8-4A5-AVANT-01	4954	1886	1481	Auto-Data.net	https://www.auto-data.net/en/audi-s6-avant-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36863
EU-ASTON-MARTIN-DBS-SUPERLEGGERA-VOLANTE-CONVERTIBLE-01	4715	1970	1295	Aston Martin official DBS Superleggera Volante technical specification	https://www.astonmartin.com/en/our-world/news/2019/4/24/dbs-superleggera-volante-aston-martin-opens-the-top-on-the-ultimate-open-top-gt-experience
EU-AUDI-S7-C8-4KA-SPORTBACK-01	4979	1908	1417	Auto-Data.net	https://www.auto-data.net/en/audi-s7-sportback-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36865
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b9-8w-facelift-2018-30-tdi-122hp-s-tronic-35173
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b9-8w-facelift-2019-30-tdi-122hp-38311
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	4738	1842	1435	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b9-8w-facelift-2018-30-tdi-122hp-s-tronic-35174
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b9-8w-facelift-2019-30-tdi-122hp-38313
```

下一步优先处理

1. 闭合 Mercedes-Benz W213/S213、C238/A238 的普通版与特殊外廓边界，并批量关联 136441–136454。
2. 处理 BMW G21 Touring、CLA X118 Shooting Brake、Peugeot 208 II 三个集中车型簇。
3. 处理 Fiesta Van、Kuga Van、C3 Van、C3 Aircross Van 等商用转换车型，优先确认是否完全复用乘用版外廓。
4. 最后处理 BMW F45/F46、F31、X1 F48、X3 M40i 和 Audi S5 TDI 等仍需独立外廓确认的记录。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s6-avant-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36863 "Audi S6 Avant (C8) 3.0 TDI V6 (349 Hp) Mild Hybrid quattro tiptronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/audi-a4-avant-b9-8w-facelift-2018-30-tdi-122hp-s-tronic-35174 "Audi A4 Avant (B9 8W, facelift 2018) 30 TDI (122 Hp) S tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* Mercedes-Benz E-Class 的 12 个 Ktype 已按 2020 年改款前后拆分，改款前复用现有 W213、S213、C238、A238 尺寸组，改款后首次创建四个尺寸组。([汽车数据网][1])
* Mercedes-Benz CLA X118 Shooting Brake 已闭合普通车身和 AMG CLA 35 两种外廓；Peugeot 208 II 的燃油与纯电版本共用同一车身尺寸组。([汽车数据网][2])
* 本轮新增完成 25 个输入 Ktype，共新增 37 条映射行和 7 个尺寸组。

当前批次进度

* 输入 Ktype：100
* READY Ktype：61
* PENDING Ktype：39
* READY 映射行：82
* 当前已引用尺寸组：39
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136441_prefl	136441	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136441_facelift	136441	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136444_prefl	136444	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136444_facelift	136444	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136445_prefl	136445	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136445_facelift	136445	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136446_prefl	136446	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136446_facelift	136446	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136447_prefl	136447	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136447_facelift	136447	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136448_prefl	136448	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136448_facelift	136448	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136449_prefl	136449	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136449_facelift	136449	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136450_prefl	136450	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136450_facelift	136450	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136451_prefl	136451	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136451_facelift	136451	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136452_prefl	136452	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136452_facelift	136452	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136453_prefl	136453	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136453_facelift	136453	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136454_prefl	136454	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136454_facelift	136454	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136521	136521	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136522	136522	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136523	136523	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136524	136524	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136525	136525	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136526	136526	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136527	136527	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136528	136528	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136529	136529	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	HIGH	AMG CLA 35外部套件形成独立外廓。	READY
136530	136530	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136531	136531	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136532	136532	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136533	136533	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-40980
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-200-197hp-eq-boost-9g-tronic-40985
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-41065
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-41073
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-cla-shooting-brake-x118-cla-200-163hp-37965
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405	Mercedes-Benz CLA Coupé and Shooting Brake official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2019/07/cla-coupe-shooting-brake.pdf
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430	Peugeot official New E-208 press release	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-e-208-irresistible-and-fun-to-drive
```

下一步优先处理

1. 闭合 BMW G21 Touring 的后驱、四驱、插混和 M340i 外廓，并处理跨 facelift 的派生映射。
2. 处理 Audi S5 TDI、BMW 8 Series G15 840i 与 Suzuki Wagon R+。
3. 批量处理 Fiesta Van、Kuga Van、C3 Van 和 C3 Aircross Van。
4. 最后闭合 BMW F45/F46、F31、X1 F48 与 X3 G01 M40i 等剩余商用分类记录。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-197hp-eq-boost-4matic-9g-tronic-52838?utm_source=chatgpt.com "Mercedes-Benz E-class (W213) E 200 (197 Hp) EQ Boost 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-cla-shooting-brake-x118-cla-200-163hp-37965?utm_source=chatgpt.com "Specs of Mercedes-Benz CLA Shooting Brake (X118) ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 闭合 Audi S5 F5 TDI Coupe、Sportback 的改款前后四套外廓；两个 Ktype 均跨越 2019 年外观改款，已分别派生 `prefl` 和 `facelift`。改款前后 Coupe 长度为 4692/4705 mm，Sportback 为 4752/4757 mm。([汽车数据网][1])
* 闭合 BMW 3 Series G21 Touring 的普通后驱、普通 xDrive、M340i xDrive 与 330e 后驱四套外廓，一次性完成 13 个 Ktype。普通后驱高度 1440 mm、普通 xDrive 高度 1445 mm、M340i 长度 4713 mm、330e 高度 1442 mm。([汽车数据网][2])
* 本轮新增完成 15 个输入 Ktype、17 条映射行和 8 个尺寸组。

当前批次进度

* 输入 Ktype：100
* READY Ktype：76
* PENDING Ktype：24
* READY 映射行：99
* 当前已引用尺寸组：47
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136473_prefl	136473	Coupe	S5 F5 pre-facelift	F5	2	EU-AUDI-S5-F5-COUPE-PREFL-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136473_facelift	136473	Coupe	S5 F5 facelift	F5	2	EU-AUDI-S5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136474_prefl	136474	Hatchback	S5 F5 Sportback pre-facelift	F5	5	EU-AUDI-S5-F5-SPORTBACK-PREFL-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136474_facelift	136474	Hatchback	S5 F5 Sportback facelift	F5	5	EU-AUDI-S5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136488	136488	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136489	136489	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136490	136490	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136491	136491	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340i外部长度与普通G21 Touring不同。	READY
136492	136492	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136493	136493	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136494	136494	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136495	136495	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136496	136496	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136497	136497	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136498	136498	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136500	136500	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	插混悬架高度形成独立外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-S5-F5-COUPE-PREFL-01	4692	1846	1368	Auto-Data.net	https://www.auto-data.net/en/audi-s5-coupe-f5-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-36833
EU-AUDI-S5-F5-COUPE-FACELIFT-01	4705	1846	1368	Auto-Data.net	https://www.auto-data.net/en/audi-s5-coupe-f5-facelift-2019-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-41380
EU-AUDI-S5-F5-SPORTBACK-PREFL-01	4752	1843	1395	Auto-Data.net	https://www.auto-data.net/en/audi-s5-sportback-f5-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-36834
EU-AUDI-S5-F5-SPORTBACK-FACELIFT-01	4757	1843	1395	Auto-Data.net	https://www.auto-data.net/en/audi-s5-sportback-f5-facelift-2019-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-41381
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-320i-184hp-steptronic-37970
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-330i-258hp-xdrive-steptronic-37261
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-m340i-374hp-xdrive-steptronic-37907
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-330e-292hp-plug-in-hybrid-steptronic-42235
```

下一步优先处理

1. 批量闭合 Ford Fiesta VII Van、Kuga II Van、Citroën C3 III Van 与 C3 Aircross Van，共 15 个 Ktype。
2. 处理 BMW 2 Series F45/F46 四个 Ktype，确认 Active Tourer 与 Gran Tourer 边界及跨改款派生。
3. 闭合 BMW F31、X1 F48、X3 G01 M40i、BMW 8 G15 840i 和 Suzuki Wagon R+。
4. PENDING 清零后立即进行一次机械闭合检查并输出两张完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s5-coupe-f5-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-36833 "Audi S5 Coupe (F5) 3.0 TDI V6 (347 Hp) Mild Hybrid quattro tiptronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-3-series-touring-g21-318d-150hp-steptronic-37972?utm_source=chatgpt.com "BMW 3 Series Touring (G21) 318d (150 Hp) Steptronic"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 完成 Ford Fiesta VII Van 三个 Ktype：普通 Van 与 Sport Van 因车身套件造成长度差异，分别关联 4040 mm 和既有 4065 mm 尺寸组；140 PS 版本复用历史 Sport Van 组。([福特服务内容][1])
* 完成 Ford Kuga II Van 三个 Ktype；136550 跨越改款前后不同外廓，拆为 `prefl`、`facelift` 两行。改款前为 4524×1838×1702 mm，改款后为 4531×1838×1689 mm。([汽车目录][2])
* 完成 Citroën C3 III Van 五个 Ktype和 C3 Aircross II Van 四个 Ktype；商用隔舱未改变车身外廓，分别批量关联同一尺寸组。
* 机械纠正上一轮进度计数：上一轮实际新增 14 个 Ktype、16 条映射行，而非 15 个 Ktype；不涉及既有映射内容变更。

当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* PENDING Ktype：10
* READY 映射行：114
* 当前已引用尺寸组：52
* 本轮新增 READY Ktype：15
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136545	136545	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-01	HIGH	普通Van外廓；Sport车身套件另组。	READY
136546	136546	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-01	HIGH	普通Van外廓；Sport车身套件另组。	READY
136547	136547	Van	Fiesta VII Sport Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	HIGH	Sport车身套件外廓。	READY
136548	136548	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH		READY
136549	136549	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH		READY
136550_prefl	136550	Van	Kuga II pre-facelift		5	EU-FORD-KUGA-II-VAN-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136550_facelift	136550	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136596	136596	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136597	136597	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136598	136598	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136599	136599	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136600	136600	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136601	136601	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136619	136619	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136620	136620	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136624	136624	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1466	Ford Fiesta official owner's manual; Auto-Data.net Fiesta VIII 3-door 1.1 70 HP	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2008253&Uid=G2008252&buildtype=web&countryCode=USA&div=f&languageCode=en&userMarket=GBR&vCode=WF0JXXGAHJKD23722&vFilteringEnabled=True&variantid=6894;https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.1-70hp-30368
EU-FORD-KUGA-II-VAN-PREFL-01	4524	1838	1702	Ford Kuga official brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Kuga-2014-UK-.pdf;https://www.automobile-catalog.com/car/2014/1775855/ford_kuga_1_6_ecoboost_150_trend_4x2.html
EU-FORD-KUGA-II-VAN-FACELIFT-01	4531	1838	1689	Ford Kuga official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Kuga.pdf
EU-CITROEN-C3-III-VAN-01	3996	1749	1474	Citroën C3 official range brochure	https://xr793.com/wp-content/uploads/2020/12/2019-Citroen-C3-Range.pdf
EU-CITROEN-C3-AIRCROSS-II-VAN-01	4154	1756	1597	Citroën C3 Aircross official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/20815/c3aircross.pdf
```

下一步优先处理

1. 一次性闭合 BMW 2 Series F45 Active Tourer 与 F46 Gran Tourer 的四个 Ktype，并处理可能跨 facelift 的分支。
2. 处理 BMW 3 Series F31 Van、X1 F48 Van 与 X3 G01 M40i。
3. 闭合 BMW 8 Series G15 840i 后驱及 xDrive 两个外廓。
4. 最后处理 Suzuki Wagon R+；PENDING 清零后下一轮直接输出两张完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2008253&Uid=G2008252&buildtype=web%2F1000&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=True&variantid=7566 "www.fordservicecontent.com"
[2]: https://www.automobile-catalog.com/car/2014/1775855/ford_kuga_1_6_ecoboost_150_trend_4x2.html?utm_source=chatgpt.com "2014 Ford Kuga 1.6 EcoBoost (150) Trend (Titanium) 4x2 ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3901-4000_ktype_dimension_mapping_final.tsv
- all_3901-4000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后 10 个 Ktype 已全部闭合，完成 BMW F45/F46、F31、X1 F48、X3 G01 M40i、Suzuki Wagon R+ 等剩余映射。
* 机械纠正 Ktype `136517`–`136520`：四行实际对应 BMW 8 Series **G16 四门 Gran Coupe**，统一关联新建尺寸组 `EU-BMW-8-G16-GRAN-COUPE-01`，不再错误使用 G15 双门 Coupe 尺寸组。([宝马集团新闻][1])
* 已完成最终机械检查并生成两个指定文件。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：129
* 最终尺寸组：66
* `id` 与 `DIMENSION_GROUP_ID` 均唯一。
* 所有映射引用均闭合，尺寸组无孤立记录。
* 所有长宽高均为正整数，来源与 URL 均非空。
* Ktype 映射表严格为 10 列，DIMENSION_GROUP 表严格为 6 列。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136392	136392	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
136393	136393	Sedan	S6 C8	4A2	4	EU-AUDI-S6-C8-4A2-SEDAN-01	HIGH		READY
136394	136394	Wagon	S6 C8	4A5	5	EU-AUDI-S6-C8-4A5-AVANT-01	HIGH		READY
136395	136395	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
136396	136396	Convertible	DBS Superleggera Volante		2	EU-ASTON-MARTIN-DBS-SUPERLEGGERA-VOLANTE-CONVERTIBLE-01	HIGH		READY
136421	136421	Sedan	Mazda 3 IV (BP)	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH		READY
136428	136428	Hatchback	Mazda 3 IV (BP)	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
136432_prefl	136432	Convertible	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136432_facelift	136432	Convertible	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136441_prefl	136441	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136441_facelift	136441	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136444_prefl	136444	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136444_facelift	136444	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136445_prefl	136445	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136445_facelift	136445	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136446_prefl	136446	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136446_facelift	136446	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136447_prefl	136447	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136447_facelift	136447	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136448_prefl	136448	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136448_facelift	136448	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136449_prefl	136449	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136449_facelift	136449	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136450_prefl	136450	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136450_facelift	136450	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136451_prefl	136451	Coupe	E-Class C238 pre-facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136451_facelift	136451	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136452_prefl	136452	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136452_facelift	136452	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136453_prefl	136453	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136453_facelift	136453	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136454_prefl	136454	Convertible	E-Class A238 pre-facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136454_facelift	136454	Convertible	E-Class A238 facelift	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越2020年改款，按物理外廓拆分。	READY
136458	136458	Hatchback	S7 Sportback C8	4KA	5	EU-AUDI-S7-C8-4KA-SPORTBACK-01	HIGH		READY
136459	136459	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
136460	136460	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
136461	136461	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136462	136462	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH		READY
136463	136463	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	HIGH		READY
136464_prefl	136464	Sedan	A4 B9 pre-facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136464_facelift2018	136464	Sedan	A4 B9 facelift 2018	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136464_facelift2019	136464	Sedan	A4 B9 facelift 2019	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136465_facelift2018	136465	Wagon	A4 B9 facelift 2018	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	HIGH	Ktype跨越两次不同外廓改款，按阶段拆分。	READY
136465_facelift2019	136465	Wagon	A4 B9 facelift 2019	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	Ktype跨越两次不同外廓改款，按阶段拆分。	READY
136466_prefl	136466	Wagon	A4 B9 pre-facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136466_facelift2018	136466	Wagon	A4 B9 facelift 2018	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136466_facelift2019	136466	Wagon	A4 B9 facelift 2019	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	Ktype跨越多次外廓改款，按阶段拆分。	READY
136467_prefl	136467	Coupe	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136467_facelift	136467	Coupe	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136468	136468	Coupe	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
136469_prefl	136469	Hatchback	A5 F5 pre-facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136469_facelift	136469	Hatchback	A5 F5 facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136470	136470	Hatchback	A5 F5 pre-facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
136471_prefl	136471	Convertible	A5 F5 pre-facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136471_facelift	136471	Convertible	A5 F5 facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136473_prefl	136473	Coupe	S5 F5 pre-facelift	F5	2	EU-AUDI-S5-F5-COUPE-PREFL-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136473_facelift	136473	Coupe	S5 F5 facelift	F5	2	EU-AUDI-S5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136474_prefl	136474	Hatchback	S5 F5 Sportback pre-facelift	F5	5	EU-AUDI-S5-F5-SPORTBACK-PREFL-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136474_facelift	136474	Hatchback	S5 F5 Sportback facelift	F5	5	EU-AUDI-S5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136486	136486	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH		READY
136487	136487	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
136488	136488	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136489	136489	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136490	136490	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136491	136491	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	HIGH	M340i外部长度与普通G21 Touring不同。	READY
136492	136492	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136493	136493	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136494	136494	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136495	136495	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-RWD-01	HIGH		READY
136496	136496	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136497	136497	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136498	136498	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-WAGON-XDRIVE-01	HIGH		READY
136500	136500	Wagon	3 Series G21	G21	5	EU-BMW-3-G21-330E-WAGON-RWD-01	HIGH	插混悬架高度形成独立外廓。	READY
136501	136501	Hatchback	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	HIGH		READY
136516	136516	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136517	136517	Coupe	8 Series Gran Coupe G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	Ktype对应G16四门Gran Coupe。	READY
136518	136518	Coupe	8 Series Gran Coupe G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	Ktype对应G16四门Gran Coupe。	READY
136519	136519	Coupe	8 Series Gran Coupe G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	Ktype对应G16四门Gran Coupe。	READY
136520	136520	Coupe	8 Series Gran Coupe G16	G16	4	EU-BMW-8-G16-GRAN-COUPE-01	HIGH	Ktype对应G16四门Gran Coupe。	READY
136521	136521	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136522	136522	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136523	136523	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136524	136524	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136525	136525	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136526	136526	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136527	136527	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136528	136528	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
136529	136529	Wagon	CLA X118 Shooting Brake	X118	5	EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	HIGH	AMG CLA 35外部套件形成独立外廓。	READY
136530	136530	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136531	136531	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136532	136532	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136533	136533	Hatchback	208 II		5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH		READY
136535	136535	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136545	136545	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-01	HIGH	普通Van外廓；Sport车身套件另组。	READY
136546	136546	Van	Fiesta VII Van		3	EU-FORD-FIESTA-VII-VAN-01	HIGH	普通Van外廓；Sport车身套件另组。	READY
136547	136547	Van	Fiesta VII Sport Van		3	EU-FORD-FIESTA-VII-VAN-SPORT-01	HIGH	Sport车身套件外廓。	READY
136548	136548	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH		READY
136549	136549	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH		READY
136550_prefl	136550	Van	Kuga II pre-facelift		5	EU-FORD-KUGA-II-VAN-PREFL-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136550_facelift	136550	Van	Kuga II facelift		5	EU-FORD-KUGA-II-VAN-FACELIFT-01	HIGH	Ktype跨越改款，按物理外廓拆分。	READY
136552	136552	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136553	136553	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136564	136564	Van	2 Series F45 Active Tourer facelift	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH		READY
136567_prefl	136567	Van	2 Series F45 Active Tourer pre-facelift	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136567_facelift	136567	Van	2 Series F45 Active Tourer facelift	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136568_prefl	136568	Van	2 Series F46 Gran Tourer pre-facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136568_facelift	136568	Van	2 Series F46 Gran Tourer facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136570_prefl	136570	Van	2 Series F46 Gran Tourer pre-facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136570_facelift	136570	Van	2 Series F46 Gran Tourer facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	HIGH	Ktype跨越2018年改款，按物理外廓拆分。	READY
136578	136578	Wagon	C-Class W205 facelift	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136579_prefl	136579	Wagon	3 Series F31 pre-facelift	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	HIGH	Ktype跨越2015年改款，按物理外廓拆分。	READY
136579_facelift	136579	Wagon	3 Series F31 facelift	F31	5	EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	HIGH	Ktype跨越2015年改款，按物理外廓拆分。	READY
136586	136586	Wagon	5 Series G30/G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	商用分类未改变G31旅行车外廓。	READY
136588	136588	Wagon	5 Series G30/G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	商用分类未改变G31旅行车外廓。	READY
136593_prefl	136593	SUV	X1 F48 pre-facelift	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-PREFL-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136593_facelift	136593	SUV	X1 F48 facelift	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	HIGH	Ktype跨越2019年改款，按物理外廓拆分。	READY
136596	136596	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136597	136597	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136598	136598	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136599	136599	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136600	136600	Van	C3 III Van		5	EU-CITROEN-C3-III-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136601	136601	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136611	136611	Sedan	Peugeot 301 I facelift		4	EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	HIGH		READY
136613	136613	SUV	X3 G01 M40i	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	M40i外部套件形成独立外廓。	READY
136614	136614	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	商用分类未改变G01 SUV外廓。	READY
136616	136616	Sedan	C-Elysée I facelift		4	EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	HIGH		READY
136619	136619	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136620	136620	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
136624	136624	Van	C3 Aircross II Van		5	EU-CITROEN-C3-AIRCROSS-II-VAN-01	HIGH	商用隔舱未改变车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3901-4000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497	Auto-Data.net	https://www.auto-data.net/en/audi-a6-allroad-c8-45-tdi-v6-245hp-mild-hybrid-quattro-ultra-s-tronic-47538
EU-AUDI-S6-C8-4A2-SEDAN-01	4954	1886	1446	Auto-Data.net	https://www.auto-data.net/en/audi-s6-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36864
EU-AUDI-S6-C8-4A5-AVANT-01	4954	1886	1481	Auto-Data.net	https://www.auto-data.net/en/audi-s6-avant-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36863
EU-ASTON-MARTIN-DBS-SUPERLEGGERA-VOLANTE-CONVERTIBLE-01	4715	1970	1295	Aston Martin official DBS Superleggera Volante technical specification	https://www.astonmartin.com/en/our-world/news/2019/4/24/dbs-superleggera-volante-aston-martin-opens-the-top-on-the-ultimate-open-top-gt-experience
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440	Mazda official 2019 Mazda3 specification sheet	https://www.autointernational.com.my/WebNews/News/Year%202019/Mazda%203%20launch%20-%2017%20Jul%2019/2019%20ALL-NEW%20MAZDA3%20-%20SPECIFICATION%20SHEET.pdf
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Mazda official 2019 Mazda3 specification sheet	https://www.autointernational.com.my/WebNews/News/Year%202019/Mazda%203%20launch%20-%2017%20Jul%2019/2019%20ALL-NEW%20MAZDA3%20-%20SPECIFICATION%20SHEET.pdf
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371	Auto-Data.net	https://www.auto-data.net/en/audi-a5-cabriolet-f5-40-tdi-190hp-quattro-s-tronic-35140
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Auto-Data.net	https://www.auto-data.net/en/audi-a5-cabriolet-f5-facelift-2019-40-tdi-190hp-quattro-s-tronic-41379
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-197hp-eq-boost-9g-tronic-37946
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-40980
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200-197hp-eq-boost-9g-tronic-37949
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-200-197hp-eq-boost-9g-tronic-40985
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-300d-245hp-9g-tronic-34043
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-41065
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300d-245hp-9g-tronic-34045
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-200-197hp-eq-boost-4matic-9g-tronic-41073
EU-AUDI-S7-C8-4KA-SPORTBACK-01	4979	1908	1417	Auto-Data.net	https://www.auto-data.net/en/audi-s7-sportback-c8-3.0-tdi-v6-349hp-mild-hybrid-quattro-tiptronic-36865
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Auto-Data.net	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-40-tfsi-190hp-s-tronic-52331
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Auto-Data.net	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-40-tdi-184hp-quattro-s-tronic-35259
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409	Auto-Data.net	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-40-tfsi-190hp-quattro-s-tronic-35265
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b9-8w-30-tdi-122hp-s-tronic-35171
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b9-8w-facelift-2018-30-tdi-122hp-s-tronic-35173
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b9-8w-facelift-2019-30-tdi-122hp-38311
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	4738	1842	1435	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b9-8w-facelift-2018-30-tdi-122hp-s-tronic-35174
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b9-8w-facelift-2019-30-tdi-122hp-38313
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b9-8w-40-tfsi-g-tron-170hp-s-tronic-35032
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Auto-Data.net	https://www.auto-data.net/en/audi-a5-coupe-f5-35-tdi-150hp-s-tronic-35136
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Auto-Data.net	https://www.auto-data.net/en/audi-a5-coupe-f5-facelift-2019-50-tdi-v6-286hp-mild-hybrid-quattro-tiptronic-41377
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Auto-Data.net	https://www.auto-data.net/en/audi-a5-sportback-f5-40-tfsi-g-tron-170hp-s-tronic-35037
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Auto-Data.net	https://www.auto-data.net/en/audi-a5-sportback-f5-facelift-2019-50-tdi-v6-286hp-mild-hybrid-quattro-tiptronic-41378
EU-AUDI-S5-F5-COUPE-PREFL-01	4692	1846	1368	Auto-Data.net	https://www.auto-data.net/en/audi-s5-coupe-f5-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-36833
EU-AUDI-S5-F5-COUPE-FACELIFT-01	4705	1846	1368	Auto-Data.net	https://www.auto-data.net/en/audi-s5-coupe-f5-facelift-2019-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-41380
EU-AUDI-S5-F5-SPORTBACK-PREFL-01	4752	1843	1395	Auto-Data.net	https://www.auto-data.net/en/audi-s5-sportback-f5-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-36834
EU-AUDI-S5-F5-SPORTBACK-FACELIFT-01	4757	1843	1395	Auto-Data.net	https://www.auto-data.net/en/audi-s5-sportback-f5-facelift-2019-3.0-tdi-v6-347hp-mild-hybrid-quattro-tiptronic-41381
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Auto-Data.net	https://www.auto-data.net/en/opel-grandland-x-1.6-turbo-300hp-plug-in-hybrid4-automatic-37663
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443	Tesla Model 3 official owner manual	https://www.tesla.com/ownersmanual/model3/en_eu/GUID-E414862C-CFA1-4A0B-9548-BE21C32CAA58.html
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-320i-184hp-steptronic-37970
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-330i-258hp-xdrive-steptronic-37261
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-m340i-374hp-xdrive-steptronic-37907
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-g21-330e-292hp-plug-in-hybrid-steptronic-42235
EU-SUZUKI-WAGON-R-PLUS-II-HATCHBACK-01	3500	1620	1705	Auto-Data.net	https://www.auto-data.net/en/suzuki-wagon-r-ii-1.0-i-12v-53hp-16492
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Auto-Data.net	https://www.auto-data.net/en/volvo-s60-iii-t6-310hp-awd-geartronic-35187
EU-BMW-8-G16-GRAN-COUPE-01	5082	1932	1407	BMW 8 Series Gran Coupe official technical data	https://www.press.bmwgroup.com/netherlands/article/attachment/T0297256NL/432852
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-cla-shooting-brake-x118-cla-200-163hp-37965
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405	Mercedes-Benz CLA Coupé and Shooting Brake official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2019/07/cla-coupe-shooting-brake.pdf
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430	Peugeot official New E-208 press release	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-e-208-irresistible-and-fun-to-drive
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1466	Ford Fiesta official owner manual; Auto-Data.net Fiesta VIII 3-door 1.1 70 HP	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2008253&Uid=G2008252&buildtype=web&countryCode=USA&div=f&languageCode=en&userMarket=GBR&vCode=WF0JXXGAHJKD23722&vFilteringEnabled=True&variantid=6894;https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.1-70hp-30368
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466	Ford Fiesta official owner manual	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2008253&Uid=G2008252&buildtype=web&countryCode=USA&div=f&languageCode=en&userMarket=USA&vFilteringEnabled=True&variantid=7566
EU-FORD-KUGA-II-VAN-FACELIFT-01	4531	1838	1689	Ford Kuga official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Kuga.pdf
EU-FORD-KUGA-II-VAN-PREFL-01	4524	1838	1702	Ford Kuga official brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Kuga-2014-UK-.pdf;https://www.automobile-catalog.com/car/2014/1775855/ford_kuga_1_6_ecoboost_150_trend_4x2.html
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555	BMW official 2 Series Active Tourer technical data	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0277755EN_GB/the-new-bmw-2-series-active-tourer-the-new-bmw-2-series-gran-tourer?language=en_GB
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555	BMW official 2 Series Active Tourer technical data	https://www.press.bmwgroup.com/global/article/detail/T0186826EN/the-new-bmw-2-series-active-tourer?language=en
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641	BMW official 2 Series Gran Tourer technical data	https://www.press.bmwgroup.com/asia/article/detail/T0274133EN/the-new-bmw-216i-gran-tourer-now-available-in-singapore?language=en
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641	BMW official 2 Series Gran Tourer technical data	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0277755EN_GB/the-new-bmw-2-series-active-tourer-the-new-bmw-2-series-gran-tourer?language=en_GB
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-300-258hp-4matic-9g-tronic-34038
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434	BMW official 3 Series Touring 330d xDrive specification	https://www.press.bmwgroup.com/global/article/attachment/T0137145EN/208689/Specifications_BMW_3_Series_Touring_330d_xDrive_03_2013.pdf
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-f31-lci-facelift-2015-330d-258hp-xdrive-steptronic-22939
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/g30-g31-f90/301104/
EU-BMW-X1-F48-SDRIVE20D-SUV-PREFL-01	4439	1821	1598	BMW official X1 sDrive20d specification	https://www.press.bmwgroup.com/global/article/detail/T0260622EN/specifications-bmw-x1-sdrive-20d-valid-from-07/2016?language=en
EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	4447	1821	1598	BMW official X1 LCI specification	https://www.press.bmwgroup.com/new-zealand/article/detail/T0300660EN/bmw-x1-lci-pricing-and-specification?language=en
EU-CITROEN-C3-III-VAN-01	3996	1749	1474	Citroën C3 official range brochure	https://xr793.com/wp-content/uploads/2020/12/2019-Citroen-C3-Range.pdf
EU-CITROEN-C3-AIRCROSS-II-VAN-01	4154	1756	1597	Citroën C3 Aircross official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/20815/c3aircross.pdf
EU-PEUGEOT-301-I-FACELIFT-SEDAN-01	4445	1748	1466	Auto-Data.net	https://www.auto-data.net/en/peugeot-301-facelift-2017-1.2-puretech-82hp-29120
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676	BMW official X3 M40i technical data	https://www.press.bmwgroup.com/asia/article/attachment/T0272141EN/389222
EU-BMW-X3-G01-SUV-01	4708	1891	1676	Auto-Data.net	https://www.auto-data.net/en/bmw-x3-g01-18d-150hp-sdrive-30643
EU-CITROEN-C-ELYSEE-I-FACELIFT-SEDAN-01	4419	1748	1466	Auto-Data.net	https://www.auto-data.net/en/citroen-c-elysee-facelift-2016-1.2-puretech-82hp-29124
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3901-4000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.bmwgroup.com/netherlands/article/attachment/T0297256NL/432852?utm_source=chatgpt.com "Specifications. The new BMW 8 Series Gran Coupe. 840i."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3556 行）
- 累计尺寸组：dimension_groups_final.tsv（1553 行）

