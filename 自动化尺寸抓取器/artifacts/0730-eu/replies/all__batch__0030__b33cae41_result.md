# 任务：all 第 2901-3000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0030__b33cae41


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-8-G15-840D-COUPE-01	4843	1902	1341
EU-BMW-8-G15-M850I-COUPE-01	4851	1902	1346
EU-BMW-X2-F39-SUV-01	4360	1824	1526
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595
EU-FIAT-FIORINO-III-CARGO-VAN-01	3957	1716	1721
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490
EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	3835	1660	1480
EU-FIAT-STILO-I-192-MULTIWAGON-01	4516	1756	1570
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-FACELIFT-01	4091	1735	1487
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-FACELIFT-01	4091	1735	1487
EU-FORD-FOCUS-I-DNW-VAN-01	4465	1702	1532
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-JEEP-COMMANDER-XK-SUV-FACELIFT-01	4787	1900	1826
EU-JEEP-PATRIOT-MK-FACELIFT-SUV-FWD-01	4415	1758	1664
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684
EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	4236	1805	1667
EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	4236	1805	1667
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	4695	1810	1680
EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-PREFL-01	4655	1800	1680
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-OPEL-INSIGNIA-B-COUNTRY-TOURER-WAGON-01	5004	1871	1525
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PIAGGIO-APE-50-PICKUP-CROSS-01	2530	1260	1620
EU-PIAGGIO-APE-50-PICKUP-LONG-DECK-01	2660	1260	1550
EU-PIAGGIO-APE-50-PICKUP-SHORT-DECK-01	2490	1260	1550
EU-PIAGGIO-APE-50-VAN-01	2500	1260	1590
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	4000	1642	1498
EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	3992	1642	1498
EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	4247	1642	1498
EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	4239	1642	1498
EU-SKODA-FABIA-III-NJ-HATCHBACK-R5-01	3992	1732	1452
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	4214	1684	1607
EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	4205	1684	1607
EU-VOLVO-V50-MW-WAGON-01	4514	1770	1452
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC60-I-FACELIFT-SUV-01	4644	1891	1713
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	93	126	Sep 2003	Aug 2005	2024-03-01	133168
Dacia	Sandero	1.5 Blue DCI 95	Schrägheck	Frontantrieb	Diesel	70	95	Aug 2018	-	2024-03-01	133169
Alpina	Xd4	Biturbo Allrad	SUV	Allrad	Diesel	285	388	Jul 2018	Jun 2024	2026-06-01	133170
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	103	140	Sep 2003	Aug 2005	2024-03-01	133171
Mitsubishi	Outlander iii	2.4 Hybrid 4WD	SUV	Allrad	Benzin/Elektro	153	208	Sep 2018	Dec 2022	2025-06-01	133172
Fiat	Panda	1.2 Bipower	Kasten/Schrägheck	Frontantrieb	Benzin/Ethanol	44	60	Sep 2004	Dec 2011	2024-03-01	133173
Mitsubishi	Colt vi	1.3 Flexfuel	Schrägheck	Frontantrieb	Benzin/Ethanol	70	95	Oct 2008	Jun 2012	2024-03-01	133175
Fiat	Punto	1.2 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	38	52	Apr 2004	Apr 2006	2024-03-01	133176
Seat	Ateca	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2018	-	2024-03-01	133177
Mitsubishi	Lancer cargo	1.6	Kasten/Kombi	Frontantrieb	Benzin	72	98	Sep 2003	Jun 2008	2024-03-01	133179
Mitsubishi	Lancer cargo	2	Kasten/Kombi	Frontantrieb	Benzin	99	135	Sep 2003	Jun 2008	2024-03-01	133180
Lotus	3	3.5	Cabriolet	Heckantrieb	Benzin	321	436	Aug 2018	-	2024-03-01	133182
Fiat	Stilo	1.4	Kasten/Kombi	Frontantrieb	Benzin	70	95	Jan 2004	Aug 2008	2024-03-01	133183
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	100	136	Feb 2004	Aug 2008	2024-03-01	133184
Peugeot	Partner	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	80	109	Sep 2000	May 2008	2024-03-01	133191
Hyundai	Santa fe iv	2.0 Crdi AWD	SUV	Allrad	Diesel	110	150	Jul 2018	Jul 2020	2024-03-01	133195
Citroën	Berlingo	Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jun 2018	-	2024-03-01	133200
Opel	Astra k	1.6 Biturbo	Schrägheck	Frontantrieb	Diesel	110	150	Jul 2018	Feb 2019	2025-12-01	133203
Opel	Astra k sports tourer	1.6 Biturbo	Kombi	Frontantrieb	Diesel	110	150	Jul 2018	Feb 2019	2025-12-01	133204
Ford	Focus i	1.8 16V Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	85	115	Sep 2002	Jul 2004	2024-03-01	133206
Opel	Insignia b country tourer	1.6 Turbo	Kombi	Frontantrieb	Benzin	147	200	Jun 2018	-	2024-03-01	133207
Aixam	Minauto	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Mar 2018	-	2024-03-01	133210
Jeep	Renegade	1.4	SUV	Frontantrieb	Benzin	100	136	Jan 2016	-	2024-03-01	133212
Ford	Fiesta	1.6 TI	Stufenheck	Frontantrieb	Benzin	77	105	Mar 2015	Apr 2017	2024-07-01	133216
Skoda	Fabia ii	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	44	60	Mar 2009	Nov 2011	2024-03-01	133226
Skoda	Fabia ii combi	1.2 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	44	60	Mar 2009	Nov 2011	2024-03-01	133228
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	88	120	Feb 2007	-	2024-03-01	133230
Jeep	Patriot	2.0 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	88	120	Feb 2007	Dec 2017	2024-03-01	133233
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	88	120	Sep 2005	Aug 2008	2024-03-01	133237
Fiat	Stilo	1.6	Kasten/Kombi	Frontantrieb	Benzin	77	105	Apr 2005	Aug 2008	2024-03-01	133239
Fiat	Stilo	1.9 JTD	Kasten/Kombi	Frontantrieb	Diesel	110	150	Sep 2005	Aug 2008	2024-03-01	133241
Jeep	Commander	3.0 CRD 4X4	SUV	Allrad	Diesel	155	211	Sep 2005	Dec 2010	2024-03-01	133243
Fiat	Grande punto van	1.3 JTD Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Feb 2006	Aug 2010	2024-03-01	133244
Skoda	Roomster	1.2 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	51	69	Mar 2009	May 2015	2024-03-01	133245
Fiat	Grande punto van	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	57	77	Feb 2006	Jun 2013	2024-03-01	133246
Fiat	Croma	1.9 Mjtd	Kasten/Kombi	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2011	2024-03-01	133247
BMW	3	330 I	Stufenheck	Heckantrieb	Benzin	190	258	Nov 2018	-	2024-03-01	133248
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	140	190	Nov 2018	-	2024-03-01	133249
BMW	3	320 D Xdrive	Stufenheck	Allrad	Diesel	140	190	Nov 2018	Feb 2020	2024-03-01	133250
BMW	Z4 roadster	Sdrive 20 I	Cabriolet	Heckantrieb	Benzin	145	197	Nov 2018	-	2024-03-01	133251
BMW	Z4 roadster	Sdrive 30 I	Cabriolet	Heckantrieb	Benzin	190	258	Nov 2018	-	2024-03-01	133252
BMW	Z4 roadster	M40 I	Cabriolet	Heckantrieb	Benzin	250	340	Nov 2018	-	2024-03-01	133253
Citroën	Berlingo	1.5 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Jun 2018	-	2024-03-01	133254
Citroën	Berlingo	1.5 Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Jun 2018	-	2024-03-01	133255
BMW	X2	Sdrive 20 D	SUV	Frontantrieb	Diesel	140	190	Nov 2018	Oct 2023	2024-03-01	133256
Citroën	Berlingo	1.6 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jun 2018	Apr 2020	2025-02-03	133257
Citroën	Berlingo	1.6 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	73	99	Jun 2018	Apr 2021	2025-02-03	133259
BMW	X5	Xdrive 45 E Plug-in Hybrid	SUV	Allrad	Benzin/Elektro	290	394	Jun 2019	Mar 2023	2025-06-01	133260
BMW	X2	M35 I	SUV	Allrad	Benzin	225	306	Nov 2018	Oct 2023	2024-03-01	133261
Fiat	Bravo van	1.6 JTD Multijet	Kasten/Schrägheck	Frontantrieb	Diesel	77	105	Mar 2008	Dec 2014	2024-03-01	133262
Fiat	Grande punto van	1.4 LPG	Kasten/Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	57	77	Mar 2009	Dec 2012	2024-03-01	133263
Fiat	Grande punto van	1.4 Natural Power	Kasten/Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	57	77	Mar 2009	Dec 2012	2024-03-01	133265
Fiat	Fiorino	Ecargo	Kasten/Großraumlimousine	Frontantrieb	Elektro	24	33	Jan 2010	Dec 2012	2024-03-01	133268
Fiat	500	Electric	Schrägheck	Frontantrieb	Elektro	24	33	Jan 2010	-	2024-03-01	133270
Renault	Megane iv	1.3 TCE 115	Stufenheck	Frontantrieb	Benzin	85	116	Jan 2018	-	2024-03-01	133276
Renault	Megane iv	1.3 TCE 140	Stufenheck	Frontantrieb	Benzin	103	140	Jan 2018	-	2024-03-01	133278
Audi	A7 sportback	45 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	155	211	Apr 2018	-	2024-03-01	133286
Cupra	Ateca	2.0 TSI 4drive	SUV	Allrad	Benzin	221	300	Sep 2018	-	2024-03-01	133290
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	130	Sep 2018	Aug 2020	2024-03-01	133291
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2018	Aug 2020	2024-03-01	133292
Seat	Leon	2.0 TSI	Schrägheck	Frontantrieb	Benzin	140	190	Sep 2018	Aug 2020	2024-03-01	133293
Citroën	C4 cactus	1.5 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	88	120	Sep 2018	-	2024-03-01	133295
BMW	8	M 850 I Xdrive	Cabriolet	Allrad	Benzin	390	530	Nov 2018	-	2024-03-01	133296
BMW	8	840 D Xdrive	Cabriolet	Allrad	Diesel	235	320	Nov 2018	Oct 2020	2024-03-01	133298
Peugeot	508 sw ii	1.5 Bluehdi 130	Kombi	Frontantrieb	Diesel	96	131	Sep 2018	-	2024-03-01	133299
Peugeot	508 sw ii	2.0 Bluehdi 160	Kombi	Frontantrieb	Diesel	120	163	Sep 2018	-	2024-03-01	133300
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	96	130	Sep 2018	Aug 2020	2024-03-01	133301
Skoda	Octavia	1.6 TDI 4X4	Schrägheck	Allrad	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	133302
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Sep 2018	Aug 2020	2024-03-01	133303
Skoda	Octavia	1.6 TDI 4X4	Kombi	Allrad	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	133304
Peugeot	508 sw ii	2.0 Bluehdi 180	Kombi	Frontantrieb	Diesel	130	177	Sep 2018	-	2024-03-01	133305
Seat	Leon	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Jul 2018	Aug 2020	2024-03-01	133306
Peugeot	508 sw ii	1.6 Puretech 180	Kombi	Frontantrieb	Benzin	133	181	Sep 2018	-	2024-03-01	133307
Peugeot	508 sw ii	1.6 Puretech 225	Kombi	Frontantrieb	Benzin	165	224	Sep 2018	-	2024-03-01	133308
Opel	Crossland x /	1.5 Turbo D	SUV	Frontantrieb	Diesel	88	120	Aug 2018	-	2024-03-01	133309
Volvo	V50	2.0 D4	Kombi	Frontantrieb	Diesel	96	131	Jul 2005	Dec 2006	2024-03-01	133310
Volvo	V50	1.8 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	93	126	Jan 2009	Sep 2010	2024-03-01	133311
Opel	Combo	1.5 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	56	76	Aug 2018	-	2024-03-01	133312
Opel	Combo	1.5 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Aug 2018	-	2024-03-01	133313
Opel	Combo	1.5 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Aug 2018	-	2024-03-01	133314
Jeep	Cherokee	2.2 CRD 4X4	SUV	Allrad	Diesel	143	195	Sep 2018	-	2024-03-01	133316
Jeep	Cherokee	2.2 CRD	SUV	Frontantrieb	Diesel	143	195	Sep 2018	-	2024-03-01	133321
DS	Ds	Puretech 130	SUV	Frontantrieb	Benzin	96	130	Oct 2018	Sep 2022	2024-03-01	133326
Toyota	Corolla	2.0 D4D	Kasten/Kombi	Frontantrieb	Diesel	66	90	Sep 2000	Oct 2001	2024-03-01	133333
Piaggio	Ape	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	11	15	Jun 1998	Dec 2015	2024-03-01	133338
Land Rover	Range rover iv	3.0 Sdv6 4X4	SUV	Allrad	Diesel	202	275	Oct 2018	Sep 2021	2025-02-03	133348
Toyota	Allion i	1.8	Stufenheck	Frontantrieb	Benzin	92	125	Jun 2001	Sep 2004	2024-03-01	133349
Volvo	V90 ii	Polestar AWD	Kombi	Allrad	Diesel	147	200	Oct 2016	Dec 2021	2024-05-01	133357
Volvo	V90 ii	D5 Polestar AWD	Kombi	Allrad	Diesel	176	239	Oct 2016	Dec 2021	2024-05-01	133359
Volvo	V90 ii cross country	T6 Polestar AWD	Kombi	Allrad	Benzin	246	334	Oct 2016	Dec 2017	2024-03-01	133360
Volvo	S60 ii cross country	T5 AWD	Stufenheck	Allrad	Benzin	183	249	Mar 2015	Dec 2018	2024-03-01	133362
Volvo	V60 i	2.0 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	157	213	Mar 2014	Dec 2015	2024-03-01	133363
Volvo	Xc60 i	T5 AWD	SUV	Allrad	Benzin	183	249	Apr 2014	Feb 2017	2024-03-01	133368
Aixam	D-Truck	0.5	Kasten	Frontantrieb	Diesel	6	8	Feb 2018	-	2024-03-01	133369
Aixam	D-Truck	0.5	Pritsche/Fahrgestell	Frontantrieb	Diesel	6	8	Feb 2018	-	2024-03-01	133370
Volvo	V40	2.0 D3	Kasten/Schrägheck	Frontantrieb	Diesel	110	150	Sep 2013	Dec 2015	2024-03-01	133371
Volvo	V40	2.0 D4	Kasten/Schrägheck	Frontantrieb	Diesel	130	177	Sep 2013	Dec 2014	2024-03-01	133372
Volvo	V40	1.6 D2/ Drive	Kasten/Schrägheck	Frontantrieb	Diesel	84	114	Sep 2013	Dec 2015	2024-03-01	133373
Toyota	Avensis	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	85	116	Sep 2002	Feb 2003	2024-03-01	133380
VW	Golf van iv variant	1.9 SDI	Kasten/Kombi	Frontantrieb	Diesel	50	68	May 1999	May 2006	2024-03-01	133383


--- Round 1 / 首次发送 ---
## 更新点

* 按候选物理车身聚类完成首轮缓存关联：48 个输入 Ktype 已闭合，共形成 51 条 READY 映射。
* `133226`、`133228`、`133245` 的生产期跨越已确认改款尺寸变化，分别拆为 `prefl` 与 `facelift` 两条物理分支。
* 本轮复用跨批次既有尺寸组 30 个，不重复输出既有组三维及来源。
* 首次创建并闭合 3 个尺寸组：Dacia Sandero II、Audi A7 C8 Sportback、Peugeot 508 II SW。Dacia 官方资料明确给出 4069×1733×1519 mm，且 1733 mm 为不含后视镜宽度；Audi 官方给出 4969×1908×1422 mm；Peugeot 官方 508 SW 规格给出 4778×1859×1420 mm，并将车身宽度与后视镜展开宽度分列。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：48
* READY 映射：51
* PENDING 输入 Ktype：52
* 已关联尺寸组：33

  * 复用既有尺寸组：30
  * 本轮新建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133168	133168	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133169	133169	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH		READY
133171	133171	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133172	133172	SUV	Outlander III	GF0W	5	EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	HIGH		READY
133183	133183	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133184	133184	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133191	133191	Pickup	Partner I		2	EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	MEDIUM		READY
133195	133195	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133203	133203	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
133204	133204	Wagon	Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
133207	133207	Wagon	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-COUNTRY-TOURER-WAGON-01	HIGH		READY
133212	133212	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	HIGH		READY
133226_prefl	133226	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133226_facelift	133226	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	生产期跨改款，改款外廓。	READY
133228_prefl	133228	Wagon	Fabia II	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133228_facelift	133228	Wagon	Fabia II	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	生产期跨改款，改款外廓。	READY
133237	133237	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133239	133239	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133241	133241	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133245_prefl	133245	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133245_facelift	133245	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH	生产期跨改款，改款外廓。	READY
133256	133256	SUV	X2 F39	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133260	133260	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
133261	133261	SUV	X2 F39	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133268	133268	Van	Fiorino III	225		EU-FIAT-FIORINO-III-CARGO-VAN-01	HIGH		READY
133276	133276	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
133278	133278	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
133286	133286	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH		READY
133291	133291	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133292	133292	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133293	133293	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133295	133295	Hatchback	C4 Cactus I		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH		READY
133299	133299	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133300	133300	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133301	133301	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133302	133302	Hatchback	Octavia III	5E3	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH		READY
133303	133303	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133304	133304	Wagon	Octavia III	5E5	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
133305	133305	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133306	133306	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133307	133307	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133308	133308	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133309	133309	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
133310	133310	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-01	HIGH		READY
133311	133311	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-01	HIGH		READY
133326	133326	SUV	DS 7 Crossback I	J4	5	EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	HIGH	输入 Model=Ds，对应 DS 7 Crossback。	READY
133348	133348	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH		READY
133357	133357	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
133359	133359	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
133360	133360	Wagon	V90 II Cross Country	236	5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH		READY
133368	133368	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-FACELIFT-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	4069	1733	1519	Dacia Sandero official brochure	https://cdn.group.renault.com/dac/tr/dacia-brochures/sandero/Dacia-Sandero-Brosur-26122019.pdf
EU-AUDI-A7-C8-4KA-SPORTBACK-01	4969	1908	1422	Audi MediaCenter A7 Sportback facts and figures	https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 Specification Guide June 2023	https://www.media.stellantis.com/uploads/uk/attachment/4885/specificationguide_peugeot508_june2023-64945a246dcb8.pdf
```

## 下一步优先处理

1. 核对 BMW 3 G20、BMW Z4 G29、SEAT Ateca 与 CUPRA Ateca 是否跨越外廓发生变化的改款节点，必要时建立 `prefl/facelift` 派生映射。
2. 按车身长度和用途分支集中处理 Berlingo K9、Combo E，以及 Grande Punto、Bravo、Panda、Lancer Cargo、Volvo V40 等乘用车衍生货运车型。
3. 闭合剩余独立车身：Alpina XD4、Jeep Compass/Patriot/Commander/Cherokee、Aixam、Toyota、Lotus 及 BMW 8 Convertible。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 9 个 READY 映射，其中 8 个 BMW Ktype 完成首次建组，`133176` 直接复用已有 Fiat Punto II 尺寸组。
* BMW 3 Series G20 的后驱车型为 `4709×1827×1435 mm`，320d xDrive 高度为 `1445 mm`，因此拆为两个尺寸组。([BMW Group PressClub][1])
* BMW Z4 G29 三个动力版本共用 `4324×1864×1304 mm` 外廓；BMW 8 Series G14 Convertible 的 M850i 与 840d 长度和高度不同，分别独立建组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：57
* READY 映射：60
* PENDING 输入 Ktype：43
* 已关联尺寸组：39

  * 本轮新建尺寸组：5
  * 本轮新增复用尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133176	133176	Hatchback	Punto II	188	5	EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	HIGH		READY
133248	133248	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
133249	133249	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
133250	133250	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	xDrive高度外廓不同。	READY
133251	133251	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133252	133252	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133253	133253	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133296	133296	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-M850I-CONVERTIBLE-01	HIGH	M850i与840d外廓尺寸不同。	READY
133298	133298	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	HIGH	840d与M850i外廓尺寸不同。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan specifications valid from 03/2019	https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan specifications valid from 03/2019	https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354
EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	4324	1864	1304	BMW Z4 specifications valid from 09/2018	https://www.press.bmwgroup.com/global/article/attachment/T0289704EN/442417
EU-BMW-8-G14-M850I-CONVERTIBLE-01	4851	1902	1345	BMW 8 Series Convertible specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286150EN/445834
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339	BMW 8 Series Convertible specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286150EN/445834
```

## 下一步优先处理

1. 集中闭合 Fiat Grande Punto Van、Bravo Van、Croma、Panda 等共享乘用车外廓的货运衍生 Ktype。
2. 处理 SEAT Ateca、CUPRA Ateca、Jeep Compass、Patriot、Commander 和 Cherokee SUV 簇。
3. 再处理 Citroën Berlingo K9、Opel Combo E 的 M/XL 与客货车型物理边界。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354 "Microsoft Word - The_all_new_BMW_3_Series_Sedan_Specifications.doc"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Fiat Grande Punto Van 的 4 个 Ktype，并按改款前后拆成 8 条映射；改款后直接复用既有 `EU-FIAT-PUNTO-199-HATCHBACK-01`。Fiat 官方技术表确认改款前外廓为 `4030×1687×1490 mm`。
* 闭合 Volvo V40 货运衍生车型 3 个 Ktype，共用 V40 五门车身外廓 `4369×1802×1420 mm`，其中官方资料将不含后视镜宽度与含后视镜宽度分别列出。([沃尔沃汽车][1])
* 闭合 Volvo V60 I BiFuel 与 S60 II Cross Country；官方尺寸分别为 `4635×1865×1484 mm` 和 `4637×1866×1539 mm`。([沃尔沃汽车][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：66
* READY 映射：73
* PENDING 输入 Ktype：34
* 已确认尺寸组：44
* 本轮首次创建尺寸组：4
* 本轮新增复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133244_prefl	133244	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133244_facelift	133244	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	生产期跨改款，改款后外廓。	READY
133246_prefl	133246	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133246_facelift	133246	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	生产期跨改款，改款后外廓。	READY
133263_prefl	133263	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	MEDIUM	生产期跨改款，改款前外廓。	READY
133263_facelift	133263	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	MEDIUM	生产期跨改款，改款后外廓。	READY
133265_prefl	133265	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	MEDIUM	生产期跨改款，改款前外廓。	READY
133265_facelift	133265	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	MEDIUM	生产期跨改款，改款后外廓。	READY
133362	133362	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH		READY
133363	133363	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH		READY
133371	133371	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
133372	133372	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
133373	133373	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	4030	1687	1490	Fiat Professional Grande Punto Van technical data	https://www.media.stellantis.com/hu-hu/download-model-document/10?v=1576184405
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539	Volvo Support S60 Cross Country dimensions	https://www.volvocars.com/jp/support/car/s60-cross-country/article/d24bb7d1e21ec6e4c0a801e801cf6114_1fb4a1e231ff3432c0a801e8011f8ab3_18f77489f78f457dc0a801e800a04016/
EU-VOLVO-V60-I-WAGON-FACELIFT-01	4635	1865	1484	Volvo Support V60 2015 dimensions	https://www.volvocars.com/en-kw/support/car/v60/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-V40-II-HATCHBACK-01	4369	1802	1420	Volvo Support V40 dimensions	https://www.volvocars.com/in/support/car/v40/16w17/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
```

## 下一步优先处理

1. 集中处理 Citroën Berlingo K9 与 Opel Combo E 的 M/XL、乘用版和厢式版物理分支。
2. 闭合 SEAT Ateca、CUPRA Ateca，以及 Jeep Compass、Patriot、Commander、Cherokee SUV 簇。
3. 随后处理剩余 Fiat Panda、Bravo、Croma，以及 Toyota、Aixam、Alpina 和 Lotus 独立车身。

推进信号：CONTINUE

[1]: https://www.volvocars.com/in/support/car/v40/16w17/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/ "V40 Dimensions | Volvo Support IN"
[2]: https://www.volvocars.com/en-kw/support/car/v60/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/ "V60 Dimensions | Volvo Support EN-KW"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 6 个输入 Ktype，新增 7 条 READY 映射。
* `133247` 的生产期横跨 Fiat Croma II 外观改款，拆分为 `prefl` 与 `facelift` 两个物理外廓。
* Fiat Panda Natural Power、Mitsubishi Colt Flexfuel、Mitsubishi Lancer Cargo 和 Fiat Bravo Van 均按对应乘用车/旅行车外壳建立稳定尺寸组。Panda Natural Power 为 `3538×1589×1576 mm`；Colt 五门改款车型为 `3940×1695×1550 mm`；Lancer Wagon 为 `4485×1695×1450 mm`；Bravo 为 `4336×1792×1498 mm`。([汽车目录][1])
* Croma 改款前为 `4756×1775×1597 mm`，改款后为 `4783×1775×1603 mm`，宽度均采用不含后视镜口径。([Stellantis Media][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：72
* READY 映射：80
* PENDING 输入 Ktype：28
* 已确认尺寸组：50
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133173	133173	Van	Panda II	169	5	EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	HIGH	Natural Power使用加高外廓。	READY
133175	133175	Hatchback	Colt VI	Z35A	5	EU-MITSUBISHI-COLT-VI-Z35A-HATCHBACK-FACELIFT-01	HIGH		READY
133179	133179	Van	Lancer VII	CS0W	5	EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	HIGH		READY
133180	133180	Van	Lancer VII	CS0W	5	EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	HIGH		READY
133247_prefl	133247	Van	Croma II	194	5	EU-FIAT-CROMA-II-194-VAN-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133247_facelift	133247	Van	Croma II	194	5	EU-FIAT-CROMA-II-194-VAN-FACELIFT-01	HIGH	生产期跨改款，改款后外廓。	READY
133262	133262	Van	Bravo II	198	5	EU-FIAT-BRAVO-II-198-VAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	3538	1589	1576	Automobile-Catalog Fiat Panda 1.2 Natural Power CNG 2006	https://www.automobile-catalog.com/car/2006/726785/fiat_panda_1_2_natural_power_cng.html
EU-MITSUBISHI-COLT-VI-Z35A-HATCHBACK-FACELIFT-01	3940	1695	1550	Automobile-Catalog Mitsubishi Colt 5dr 1.3 ClearTec 2009	https://www.automobile-catalog.com/car/2009/1993610/mitsubishi_colt_5dr_1_3_cleartec.html
EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	4485	1695	1450	Automobile-Catalog Mitsubishi Lancer Wagon 1.6 2004	https://www.automobile-catalog.com/car/2004/1995020/mitsubishi_lancer_wagon_1_6.html
EU-FIAT-CROMA-II-194-VAN-PREFL-01	4756	1775	1597	Fiat New Croma official press information	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-croma-in-uk
EU-FIAT-CROMA-II-194-VAN-FACELIFT-01	4783	1775	1603	Automobile-Catalog Fiat Croma 1.9 Multijet 16V 150 2008	https://www.automobile-catalog.com/car/2008/727790/fiat_croma_1_9_multijet_16v_150_emotion_dpf.html
EU-FIAT-BRAVO-II-198-VAN-01	4336	1792	1498	Fiat New Bravo official press information	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-bravo-in-uk
```

## 下一步优先处理

1. 闭合 Citroën Berlingo K9 与 Opel Combo E 的 M、XL及客货车分支。
2. 处理 SEAT Ateca、CUPRA Ateca及 Jeep Compass、Patriot、Commander、Cherokee SUV 簇。
3. 处理剩余 Aixam、Toyota、Lotus、Alpina、Ford Fiesta Sedan、Ford Focus I、Fiat 500 Electric、Piaggio Ape Electric 与 VW Golf IV Variant Van。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/726785/fiat_panda_1_2_natural_power_cng.html?utm_source=chatgpt.com "2006 Fiat Panda 1.2 Natural Power (CNG) Specs Review (38 kW / 52 PS / 51 hp) (since mid-year 2006 for Europe )"
[2]: https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-croma-in-uk?utm_source=chatgpt.com "NEW FIAT CROMA IN UK"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 SEAT Ateca 与 CUPRA Ateca，并按改款前后外廓变化分别拆分。SEAT Ateca 长度由 4363 mm 变为 4381 mm；CUPRA Ateca 由 `4376×1841×1611 mm` 变为 `4386×1841×1599 mm`。([SEAT][1])
* Citroën Berlingo III 的 5 个 Ktype 和 Opel Combo E 的 3 个 Ktype，均按 M/XL 两种已确认物理车长拆分，并直接复用跨批次既有尺寸组。
* 本轮闭合 10 个输入 Ktype，新增 20 条 READY 映射；首次创建 4 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：82
* READY 映射：100
* PENDING 输入 Ktype：18
* 当前已引用尺寸组：58
* 本轮首次创建尺寸组：4
* 本轮新增复用既有尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133177_prefl	133177	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-PREFL-FWD-01	HIGH	生产期覆盖改款前外廓。	READY
133177_facelift	133177	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-FACELIFT-FWD-01	HIGH	生产期覆盖改款后外廓。	READY
133200_m	133200	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133200_xl	133200	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133254_m	133254	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133254_xl	133254	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133255_m	133255	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133255_xl	133255	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133257_m	133257	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133257_xl	133257	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133259_m	133259	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133259_xl	133259	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133290_prefl	133290	SUV	CUPRA Ateca I	KH7	5	EU-CUPRA-ATECA-I-KH7-SUV-PREFL-AWD-01	HIGH	生产期覆盖改款前外廓。	READY
133290_facelift	133290	SUV	CUPRA Ateca I	KH7	5	EU-CUPRA-ATECA-I-KH7-SUV-FACELIFT-AWD-01	HIGH	生产期覆盖改款后外廓。	READY
133312_m	133312	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133312_xl	133312	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133313_m	133313	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133313_xl	133313	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133314_m	133314	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133314_xl	133314	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-ATECA-I-KH7-SUV-PREFL-FWD-01	4363	1841	1601	SEAT Ateca official specifications December 2018	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/ateca/cars-specs-brochure-KH7-NA-december-2018.pdf
EU-SEAT-ATECA-I-KH7-SUV-FACELIFT-FWD-01	4381	1841	1601	New SEAT Ateca official brochure August 2020	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-ateca/cars-models-brochure-newateca-ago-2020.pdf
EU-CUPRA-ATECA-I-KH7-SUV-PREFL-AWD-01	4376	1841	1611	New CUPRA Ateca official technical specifications 2018	https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/Img/2018/10/2018-10-29/Technical-Specifications-New-CUPRA-Ateca.pdf
EU-CUPRA-ATECA-I-KH7-SUV-FACELIFT-AWD-01	4386	1841	1599	CUPRA Ateca official brochure 2021	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-ateca-2021.pdf
```

## 下一步优先处理

1. 集中闭合 Jeep Compass、Patriot、Commander 与 Cherokee 的驱动形式及改款分支。
2. 处理 Toyota Corolla Wagon、Allion、Avensis，以及 VW Golf IV Variant Van。
3. 最后处理 Alpina XD4、Lotus 3-Eleven、Fiat 500 Electric、Aixam Minauto/D-Truck、Piaggio Ape Electric 和 Ford 两个剩余车型。

推进信号：CONTINUE

[1]: https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/ateca/cars-specs-brochure-KH7-NA-december-2018.pdf "SEAT Ateca Brochure Download Specs"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 Jeep Compass、Patriot、Commander、Cherokee，Toyota Allion 与 VW Golf IV Variant Van，共 7 个输入 Ktype。
* `133243` 按 Commander XK 改款前后拆分；改款后直接复用已有尺寸组，改款前新建独立组。
* `133316` 的 2.2 CRD 4X4 按 Active Drive I 与 Active Drive II 拆分；官方规格显示二者长宽相同，但 Active Drive II 的车高为 1707 mm，标准 Active Drive I 为 1683 mm。
* Compass 2.0 CRD 与 Patriot 2.0 CRD 分别闭合为 `4405×1810×1630 mm` 和 `4408×1785×1658 mm`。([汽车目录][1])
* Allion I 官方规格为 `4550×1695×1470 mm`；Golf IV Variant 官方车型档案确认厂内代码 1J，规格为 `4397×1735×1485 mm`。([丰田官方网站][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：89
* READY 映射：109
* PENDING 输入 Ktype：11
* 当前已引用尺寸组：66
* 本轮首次创建尺寸组：7
* 本轮新增复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133230	133230	SUV	Compass I	MK49	5	EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	HIGH	2.0 CRD对应改款前四驱外廓。	READY
133233	133233	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-PREFL-AWD-01	MEDIUM	2.0 CRD对应改款前欧洲四驱外廓。	READY
133243_prefl	133243	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
133243_facelift	133243	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
133316_adi	133316	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	HIGH	Active Drive I标准车高外廓。	READY
133316_adii	133316	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	HIGH	Active Drive II车高外廓不同。	READY
133321	133321	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	MEDIUM	前驱版本使用标准车高外廓。	READY
133349	133349	Sedan	Allion I	T240	4	EU-TOYOTA-ALLION-I-T240-SEDAN-01	MEDIUM	输入功率与驱动组合存在版本差异，但车身外廓一致。	READY
133383	133383	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	厢式用途沿用Golf IV Variant五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	4405	1810	1630	Automobile-Catalog Jeep Compass 2.0 CRD Sport 2007	https://www.automobile-catalog.com/car/2007/1330580/jeep_compass_2_0_crd_sport.html
EU-JEEP-PATRIOT-I-MK74-SUV-PREFL-AWD-01	4408	1785	1658	Automobile-Catalog Jeep Patriot 2.0 CRD Limited 2007	https://www.automobile-catalog.com/car/2007/1331435/jeep_patriot_2_0_crd_limited.html
EU-JEEP-COMMANDER-XK-SUV-PREFL-01	4787	1900	1826	Automobile-Catalog Jeep Commander 3.0 CRD Limited 2007	https://www.automobile-catalog.com/car/2007/1328720/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683	Jeep Cherokee official specifications May 2019	https://www.media.stellantis.com/uploads/de/DE/2019/JEEP/Preislisten/190520_J_Cherokee_PL.pdf
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	4623	1859	1707	Jeep Cherokee official specifications May 2019	https://www.media.stellantis.com/uploads/de/DE/2019/JEEP/Preislisten/190520_J_Cherokee_PL.pdf
EU-TOYOTA-ALLION-I-T240-SEDAN-01	4550	1695	1470	Toyota 75 Years Vehicle Lineage First-generation Allion	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000074/index.html
EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	4397	1735	1485	Volkswagen Newsroom Golf IV Variant vehicle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
```

## 下一步优先处理

1. 闭合 Toyota Corolla Wagon 与 Avensis T22 Sedan。
2. 集中处理 Aixam Minauto、D-Truck Van 和 D-Truck Platform Cab。
3. 最后处理 Alpina XD4、Lotus 3-Eleven、Ford Focus I、Ford Fiesta Sedan、Fiat 500 Electric 与 Piaggio Ape Electric。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/1330580/jeep_compass_2_0_crd_sport.html?utm_source=chatgpt.com "2007 Jeep Compass 2.0 CRD Sport Specs Review (103 kW / 140 PS / 138 hp) (since early-year 2007 for Europe )"
[2]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000074/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 本轮闭合 6 个输入 Ktype，新增 6 条 READY 映射并首次创建 6 个尺寸组。
* `133170` 对应 Alpina XD4 G02；官方资料支持 `4751×1927×1615 mm`。`133182` 的 321 kW/436 PS 对应 Lotus 3-Eleven 430、Type 123，外廓为 `4120×1858×1201 mm`。([阿尔皮纳][1])
* `133216` 与 2015—2017 Fiesta VII facelift Sedan 1.6 105 HP 精确匹配；Toyota Corolla E110 Wagon 与 Avensis T22 D-4D 也已按对应动力、年份和车身闭合。([汽车数据网][2])
* 尚余 5 个输入 Ktype：Ford Focus I、Aixam Minauto、Aixam D-Truck Van、Aixam D-Truck Platform Cab、Piaggio Ape Electric。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：95
* READY 映射：115
* PENDING 输入 Ktype：5
* 当前已引用尺寸组：72
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133170	133170	SUV	XD4 G02	G02	5	EU-ALPINA-XD4-G02-SUV-01	HIGH	改款前后公开三维一致，合并同组。	READY
133182	133182	Convertible	3-Eleven 430	Type 123	0	EU-LOTUS-3-ELEVEN-430-TYPE123-CONVERTIBLE-01	HIGH	321 kW/436 PS对应3-Eleven 430。	READY
133216	133216	Sedan	Fiesta VII facelift		4	EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	HIGH		READY
133270	133270	Hatchback	500 I	312	3	EU-FIAT-500-I-312-HATCHBACK-PREFL-01	MEDIUM	2010年24 kW电动版沿用500三门车身外廓。	READY
133333	133333	Van	Corolla VIII E110	E110	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	HIGH	货运用途沿用五门旅行车外廓。	READY
133380	133380	Sedan	Avensis I facelift	T22	4	EU-TOYOTA-AVENSIS-I-T22-SEDAN-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-XD4-G02-SUV-01	4751	1927	1615	BMW ALPINA XD4 official press release September 2021	https://files.alpina.co.jp/press/2021/xd4lhd_press_pdf.html
EU-LOTUS-3-ELEVEN-430-TYPE123-CONVERTIBLE-01	4120	1858	1201	Lotus 3-Eleven 430 official media information;Encyclopaedia Lotus 3-Eleven 430 specifications	https://www.motorshow.me/uploadImages/GalleryDocs/Doc7338.pdf;https://www.encycarpedia.com/lotus/18-3-eleven-430-roadster
EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	4320	1722	1489	Auto-Data Ford Fiesta VII Sedan 1.6 105 HP 2015	https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-facelift-2013-1.6-105hp-powershift-29541
EU-FIAT-500-I-312-HATCHBACK-PREFL-01	3546	1627	1488	Fiat 500 Electric exact model listing;CarsGuide Fiat 500 2010 dimensions	https://autogidas.lt/en/auto-katalogas/fiat/500/electric-ev-2010-k109237;https://www.carsguide.com.au/fiat/500/car-dimensions/2010
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610	Auto-Data Toyota Corolla Wagon VIII E110 2.0 D-4D 90 HP	https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-2.0-d-4d-90hp-16667
EU-TOYOTA-AVENSIS-I-T22-SEDAN-FACELIFT-01	4520	1710	1425	Auto-Data Toyota Avensis T22 2.0 D-4D 110 HP	https://www.auto-data.net/en/toyota-avensis-t22-2.0-d-4d-110hp-3608
```

## 下一步优先处理

1. 确认 `133206` Ford Focus I BiFuel 覆盖三门、五门还是单一车身分支。
2. 闭合 `133210` Minauto Access/Cross，以及 `133369`、`133370` 2018 facelift D-Truck 的完整车高。
3. 确认 `133338` Ape Electric 对应的短货台、长货台或 Cross 平台分支。

推进信号：CONTINUE

[1]: https://files.alpina.co.jp/press/2021/xd4lhd_press_pdf.html?utm_source=chatgpt.com "PRESS RELEASE September 2021"
[2]: https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-facelift-2013-1.6-105hp-powershift-29541 "Ford Fiesta VII Sedan (Mk7, facelift 2013) 1.6 (105 Hp) PowerShift | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* `133206` 已确认同时覆盖 Focus I 改款型 DAW 三门与 DBW 五门车身，拆分为两条映射。Ford 2002—2003 官方资料给出的两种掀背外廓均为 `4174×1702×1430 mm`，宽度为不含后视镜口径。([汽车目录档案][1])
* `133210` 按 Minauto Access 短车身与 Minauto Cross 长高车身拆分；两者长度分别为 2759 mm、2998 mm，Cross 使用 2000 mm 轴距的高车身边界。([Autodata][2])
* `133369`、`133370` 已按 D-Truck Fourgon 与 Plateau Ridelles 分别闭合。技术表明确列出不含后视镜宽度 1500 mm，整车高度分别为 1830 mm、1750 mm。([Scribd][3])
* 当前仅剩 `133338` Piaggio Ape TM Electric 的短平台/长平台适用边界尚未唯一确认。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：99
* READY 映射：121
* PENDING 输入 Ktype：1
* 已确认尺寸组：78
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133206_3dr	133206	Hatchback	Focus I facelift	DAW	3	EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype覆盖DAW三门物理分支。	READY
133206_5dr	133206	Hatchback	Focus I facelift	DBW	5	EU-FORD-FOCUS-I-DBW-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype覆盖DBW五门物理分支。	READY
133210_access	133210	Hatchback	Minauto I Access		3	EU-AIXAM-MINAUTO-I-ACCESS-HATCHBACK-01	MEDIUM	输入未区分Access与Cross，短车身分支。	READY
133210_cross	133210	Hatchback	Minauto I Cross		3	EU-AIXAM-MINAUTO-I-CROSS-HATCHBACK-01	MEDIUM	输入未区分Access与Cross，长高车身分支。	READY
133369	133369	Van	D-Truck 2018		2	EU-AIXAM-D-TRUCK-2018-VAN-01	HIGH		READY
133370	133370	Pickup	D-Truck 2018		2	EU-AIXAM-D-TRUCK-2018-PLATFORM-CAB-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	4174	1702	1430	Ford Focus 2002 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/10/Ford-Focus-2002-UK.pdf
EU-FORD-FOCUS-I-DBW-HATCHBACK-5D-FACELIFT-01	4174	1702	1430	Ford Focus 2003 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/10/Ford-Focus-2003-UK.pdf
EU-AIXAM-MINAUTO-I-ACCESS-HATCHBACK-01	2759	1500	1470	Auto-Data Aixam Minauto I Access;Aixam model dimension comparison	https://www.auto-data.net/en/aixam-minauto-i-access-0.5d-8hp-automatic-35917;https://aixam-center-sued.de/aixam-city/city-gto
EU-AIXAM-MINAUTO-I-CROSS-HATCHBACK-01	2998	1500	1540	Auto-Data Aixam Minauto I Cross;Aixam model dimension comparison	https://www.auto-data.net/en/aixam-minauto-i-cross-0.5d-8hp-automatic-35918;https://aixam-center-sued.de/aixam-crossline/crossline-gt
EU-AIXAM-D-TRUCK-2018-VAN-01	3000	1500	1830	Aixam Pro D-Truck official technical sheet	https://fr.scribd.com/document/732494660/Aixampro-Ficheteche-Dtruck3vols2022-Compressed1
EU-AIXAM-D-TRUCK-2018-PLATFORM-CAB-01	3000	1500	1750	Aixam Pro D-Truck official technical sheet	https://fr.scribd.com/document/732494660/Aixampro-Ficheteche-Dtruck3vols2022-Compressed1
```

## 下一步优先处理

1. 唯一确认 `133338` 的 `LIT` 电动底盘对应 Ape TM 标准短平台还是长平台；闭合后立即执行机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2025/10/Ford-Focus-2002-UK.pdf?utm_source=chatgpt.com "Ford-Focus-2002-UK.pdf"
[2]: https://www.autodata1.com/fr/car/aixam/minauto/minauto-access-05d-8-hp-automatic?utm_source=chatgpt.com "Aixam MINAUTO ACCESS 0.5d (8 Hp) Automatic"
[3]: https://fr.scribd.com/document/732494660/Aixampro-Ficheteche-Dtruck3vols2022-Compressed1 "Fiche Technique Aixam D-Truck Électrique/Diesel | PDF | Frein | Véhicule électrique"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* `133338` 已闭合。目录记录将其识别为 **Piaggio Ape TM Platform/Chassis Electric 11 kW、BodyCode=LIT**；官方 Ape TM 技术资料同时列出标准货台 `3175×1480×1630 mm` 与长货台 `3390×1500×1630 mm`，因此拆分为 `std`、`long` 两条物理分支。([DENSO][1])
* 已完成轻量机械收尾：Ktype 全部覆盖、`id` 唯一、所有映射均为 READY、尺寸组唯一、映射引用全部闭合、三维与来源字段非空。
* 已生成两个指定文件名的 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：123
* PENDING：0
* DIMENSION_GROUP：80
* 映射引用闭合：80/80
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133168	133168	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133169	133169	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH		READY
133170	133170	SUV	XD4 G02	G02	5	EU-ALPINA-XD4-G02-SUV-01	HIGH	改款前后公开三维一致，合并同组。	READY
133171	133171	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133172	133172	SUV	Outlander III	GF0W	5	EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	HIGH		READY
133173	133173	Van	Panda II	169	5	EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	HIGH	Natural Power使用加高外廓。	READY
133175	133175	Hatchback	Colt VI	Z35A	5	EU-MITSUBISHI-COLT-VI-Z35A-HATCHBACK-FACELIFT-01	HIGH		READY
133176	133176	Hatchback	Punto II	188	5	EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	HIGH		READY
133177_prefl	133177	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-PREFL-FWD-01	HIGH	生产期覆盖改款前外廓。	READY
133177_facelift	133177	SUV	Ateca I	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-FACELIFT-FWD-01	HIGH	生产期覆盖改款后外廓。	READY
133179	133179	Van	Lancer VII	CS0W	5	EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	HIGH		READY
133180	133180	Van	Lancer VII	CS0W	5	EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	HIGH		READY
133182	133182	Convertible	3-Eleven 430	Type 123	0	EU-LOTUS-3-ELEVEN-430-TYPE123-CONVERTIBLE-01	HIGH	321 kW/436 PS对应3-Eleven 430。	READY
133183	133183	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133184	133184	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133191	133191	Pickup	Partner I		2	EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	MEDIUM		READY
133195	133195	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
133200_m	133200	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133200_xl	133200	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133203	133203	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
133204	133204	Wagon	Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
133206_3dr	133206	Hatchback	Focus I facelift	DAW	3	EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype覆盖DAW三门物理分支。	READY
133206_5dr	133206	Hatchback	Focus I facelift	DBW	5	EU-FORD-FOCUS-I-DBW-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype覆盖DBW五门物理分支。	READY
133207	133207	Wagon	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-COUNTRY-TOURER-WAGON-01	HIGH		READY
133210_access	133210	Hatchback	Minauto I Access		3	EU-AIXAM-MINAUTO-I-ACCESS-HATCHBACK-01	MEDIUM	输入未区分Access与Cross，短车身分支。	READY
133210_cross	133210	Hatchback	Minauto I Cross		3	EU-AIXAM-MINAUTO-I-CROSS-HATCHBACK-01	MEDIUM	输入未区分Access与Cross，长高车身分支。	READY
133212	133212	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	HIGH		READY
133216	133216	Sedan	Fiesta VII facelift		4	EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	HIGH		READY
133226_prefl	133226	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133226_facelift	133226	Hatchback	Fabia II	5J2	5	EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	HIGH	生产期跨改款，改款外廓。	READY
133228_prefl	133228	Wagon	Fabia II	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133228_facelift	133228	Wagon	Fabia II	5J5	5	EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	HIGH	生产期跨改款，改款外廓。	READY
133230	133230	SUV	Compass I	MK49	5	EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	HIGH	2.0 CRD对应改款前四驱外廓。	READY
133233	133233	SUV	Patriot I	MK74	5	EU-JEEP-PATRIOT-I-MK74-SUV-PREFL-AWD-01	MEDIUM	2.0 CRD对应改款前欧洲四驱外廓。	READY
133237	133237	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133239	133239	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133241	133241	Van	Stilo I	192	5	EU-FIAT-STILO-I-192-MULTIWAGON-01	HIGH		READY
133243_prefl	133243	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
133243_facelift	133243	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
133244_prefl	133244	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133244_facelift	133244	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	生产期跨改款，改款后外廓。	READY
133245_prefl	133245	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	HIGH	生产期跨改款，前期外廓。	READY
133245_facelift	133245	MPV	Roomster I	5J7	5	EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	HIGH	生产期跨改款，改款外廓。	READY
133246_prefl	133246	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133246_facelift	133246	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	生产期跨改款，改款后外廓。	READY
133247_prefl	133247	Van	Croma II	194	5	EU-FIAT-CROMA-II-194-VAN-PREFL-01	HIGH	生产期跨改款，改款前外廓。	READY
133247_facelift	133247	Van	Croma II	194	5	EU-FIAT-CROMA-II-194-VAN-FACELIFT-01	HIGH	生产期跨改款，改款后外廓。	READY
133248	133248	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
133249	133249	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
133250	133250	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	xDrive高度外廓不同。	READY
133251	133251	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133252	133252	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133253	133253	Convertible	Z4 G29	G29	2	EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	HIGH		READY
133254_m	133254	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133254_xl	133254	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133255_m	133255	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133255_xl	133255	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133256	133256	SUV	X2 F39	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133257_m	133257	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133257_xl	133257	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133259_m	133259	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133259_xl	133259	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133260	133260	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
133261	133261	SUV	X2 F39	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133262	133262	Van	Bravo II	198	5	EU-FIAT-BRAVO-II-198-VAN-01	HIGH		READY
133263_prefl	133263	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	MEDIUM	生产期跨改款，改款前外廓。	READY
133263_facelift	133263	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	MEDIUM	生产期跨改款，改款后外廓。	READY
133265_prefl	133265	Van	Punto III pre-facelift	199		EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	MEDIUM	生产期跨改款，改款前外廓。	READY
133265_facelift	133265	Van	Punto III facelift	199		EU-FIAT-PUNTO-199-HATCHBACK-01	MEDIUM	生产期跨改款，改款后外廓。	READY
133268	133268	Van	Fiorino III	225		EU-FIAT-FIORINO-III-CARGO-VAN-01	HIGH		READY
133270	133270	Hatchback	500 I	312	3	EU-FIAT-500-I-312-HATCHBACK-PREFL-01	MEDIUM	2010年24 kW电动版沿用500三门车身外廓。	READY
133276	133276	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
133278	133278	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
133286	133286	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-C8-4KA-SPORTBACK-01	HIGH		READY
133290_prefl	133290	SUV	CUPRA Ateca I	KH7	5	EU-CUPRA-ATECA-I-KH7-SUV-PREFL-AWD-01	HIGH	生产期覆盖改款前外廓。	READY
133290_facelift	133290	SUV	CUPRA Ateca I	KH7	5	EU-CUPRA-ATECA-I-KH7-SUV-FACELIFT-AWD-01	HIGH	生产期覆盖改款后外廓。	READY
133291	133291	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133292	133292	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133293	133293	Hatchback	Leon III	5F1	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
133295	133295	Hatchback	C4 Cactus I		5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH		READY
133296	133296	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-M850I-CONVERTIBLE-01	HIGH	M850i与840d外廓尺寸不同。	READY
133298	133298	Convertible	8 Series G14	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	HIGH	840d与M850i外廓尺寸不同。	READY
133299	133299	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133300	133300	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133301	133301	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133302	133302	Hatchback	Octavia III	5E3	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH		READY
133303	133303	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133304	133304	Wagon	Octavia III	5E5	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
133305	133305	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133306	133306	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
133307	133307	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133308	133308	Wagon	508 II		5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
133309	133309	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
133310	133310	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-01	HIGH		READY
133311	133311	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-01	HIGH		READY
133312_m	133312	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133312_xl	133312	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133313_m	133313	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133313_xl	133313	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133314_m	133314	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133314_xl	133314	MPV	Combo E		5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	输入未区分M与XL，按已确认双车长派生。	READY
133316_adi	133316	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	HIGH	Active Drive I标准车高外廓。	READY
133316_adii	133316	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	HIGH	Active Drive II车高外廓不同。	READY
133321	133321	SUV	Cherokee KL facelift	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	MEDIUM	前驱版本使用标准车高外廓。	READY
133326	133326	SUV	DS 7 Crossback I	J4	5	EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	HIGH	输入 Model=Ds，对应 DS 7 Crossback。	READY
133333	133333	Van	Corolla VIII E110	E110	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	HIGH	货运用途沿用五门旅行车外廓。	READY
133338_std	133338	Pickup	Ape TM	LIT	2	EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-STANDARD-01	MEDIUM	输入未区分标准与长货台，按官方双平台外廓派生。	READY
133338_long	133338	Pickup	Ape TM	LIT	2	EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-LONG-01	MEDIUM	输入未区分标准与长货台，按官方双平台外廓派生。	READY
133348	133348	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH		READY
133349	133349	Sedan	Allion I	T240	4	EU-TOYOTA-ALLION-I-T240-SEDAN-01	MEDIUM	输入功率与驱动组合存在版本差异，但车身外廓一致。	READY
133357	133357	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
133359	133359	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
133360	133360	Wagon	V90 II Cross Country	236	5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH		READY
133362	133362	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH		READY
133363	133363	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH		READY
133368	133368	SUV	XC60 I	156	5	EU-VOLVO-XC60-I-FACELIFT-SUV-01	HIGH		READY
133369	133369	Van	D-Truck 2018		2	EU-AIXAM-D-TRUCK-2018-VAN-01	HIGH		READY
133370	133370	Pickup	D-Truck 2018		2	EU-AIXAM-D-TRUCK-2018-PLATFORM-CAB-01	HIGH		READY
133371	133371	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
133372	133372	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
133373	133373	Van	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH		READY
133380	133380	Sedan	Avensis I facelift	T22	4	EU-TOYOTA-AVENSIS-I-T22-SEDAN-FACELIFT-01	HIGH		READY
133383	133383	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	厢式用途沿用Golf IV Variant五门外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2901-3000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-STILO-I-192-MULTIWAGON-01	4516	1756	1570	Fiat Stilo official owner handbook	https://aftersales.fiat.com/eLumData/EN/00/192_STILO/00_192_STILO_603.46.714_EN_01_09.05_SA_VA/00_192_STILO_603.46.714_EN_01_09.05_SA_VA.pdf
EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	4069	1733	1519	Dacia Sandero official brochure	https://cdn.group.renault.com/dac/tr/dacia-brochures/sandero/Dacia-Sandero-Brosur-26122019.pdf
EU-ALPINA-XD4-G02-SUV-01	4751	1927	1615	BMW ALPINA XD4 official press release September 2021	https://files.alpina.co.jp/press/2021/xd4lhd_press_pdf.html
EU-MITSUBISHI-OUTLANDER-III-GF0W-SUV-FACELIFT-01	4695	1810	1680	Mitsubishi Outlander official brochure	https://www.mitsubishi-motors.com.bh/content/dam/mitsubishi-motors/images/site-images/brochures/brochure_files/20_OL_EU_Brochure_Eng_190710_2_cs_master.pdf
EU-FIAT-PANDA-II-169-NATURAL-POWER-VAN-01	3538	1589	1576	Automobile-Catalog Fiat Panda 1.2 Natural Power CNG 2006	https://www.automobile-catalog.com/car/2006/726785/fiat_panda_1_2_natural_power_cng.html
EU-MITSUBISHI-COLT-VI-Z35A-HATCHBACK-FACELIFT-01	3940	1695	1550	Automobile-Catalog Mitsubishi Colt 5dr 1.3 ClearTec 2009	https://www.automobile-catalog.com/car/2009/1993610/mitsubishi_colt_5dr_1_3_cleartec.html
EU-FIAT-PUNTO-II-188-HATCHBACK-5D-PREFL-01	3835	1660	1480	Automobile-Catalog Fiat Punto 5-porte specifications	https://www.automobile-catalog.com/car/2003/1369070/fiat_punto_5-porte_1_2_16v_emotion.html
EU-SEAT-ATECA-I-KH7-SUV-PREFL-FWD-01	4363	1841	1601	SEAT Ateca official specifications December 2018	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/ateca/cars-specs-brochure-KH7-NA-december-2018.pdf
EU-SEAT-ATECA-I-KH7-SUV-FACELIFT-FWD-01	4381	1841	1601	New SEAT Ateca official brochure August 2020	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-ateca/cars-models-brochure-newateca-ago-2020.pdf
EU-MITSUBISHI-LANCER-VII-CS0W-CARGO-VAN-01	4485	1695	1450	Automobile-Catalog Mitsubishi Lancer Wagon 1.6 2004	https://www.automobile-catalog.com/car/2004/1995020/mitsubishi_lancer_wagon_1_6.html
EU-LOTUS-3-ELEVEN-430-TYPE123-CONVERTIBLE-01	4120	1858	1201	Lotus 3-Eleven 430 official media information;Encyclopaedia Lotus 3-Eleven 430 specifications	https://www.motorshow.me/uploadImages/GalleryDocs/Doc7338.pdf;https://www.encycarpedia.com/lotus/18-3-eleven-430-roadster
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819	VehicleScore Peugeot Partner dimensions	https://vehiclescore.co.uk/car-dimensions-check/peugeot/partner
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Hyundai Santa Fe official brochure	https://hyundai.simemotors.my/download/eBrochure/Hyundai-Santa-Fe.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën Berlingo official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-Berlingo-Van-2018-UK.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën Berlingo official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-Berlingo-Van-2018-UK.pdf
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485	Opel Astra official specification sheet	https://nd-mediagallery2-public-production.s3.amazonaws.com/ba78cc2a509bcdcb849506ae8b698eda/10855_56586_opel_astra_enjoy_my18_spec_sheets_a4l_fc_e_web.pdf
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510	Automobile-Catalog Opel Astra Sports Tourer specifications	https://www.automobile-catalog.com/car/2018/2532800/opel_astra_sports_tourer_1_6_cdti_ecoflex_110.html
EU-FORD-FOCUS-I-DAW-HATCHBACK-3D-FACELIFT-01	4174	1702	1430	Ford Focus 2002 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/10/Ford-Focus-2002-UK.pdf
EU-FORD-FOCUS-I-DBW-HATCHBACK-5D-FACELIFT-01	4174	1702	1430	Ford Focus 2003 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/10/Ford-Focus-2003-UK.pdf
EU-OPEL-INSIGNIA-B-COUNTRY-TOURER-WAGON-01	5004	1871	1525	Automobile-Catalog Opel Insignia Country Tourer specifications	https://www.automobile-catalog.com/car/2018/2606240/opel_insignia_country_tourer_2_0_diesel_170_automatic.html
EU-AIXAM-MINAUTO-I-ACCESS-HATCHBACK-01	2759	1500	1470	Auto-Data Aixam Minauto I Access;Aixam model dimension comparison	https://www.auto-data.net/en/aixam-minauto-i-access-0.5d-8hp-automatic-35917;https://aixam-center-sued.de/aixam-city/city-gto
EU-AIXAM-MINAUTO-I-CROSS-HATCHBACK-01	2998	1500	1540	Auto-Data Aixam Minauto I Cross;Aixam model dimension comparison	https://www.auto-data.net/en/aixam-minauto-i-cross-0.5d-8hp-automatic-35918;https://aixam-center-sued.de/aixam-crossline/crossline-gt
EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	4236	1805	1667	VehicleScore Jeep Renegade dimensions	https://vehiclescore.co.uk/car-dimensions-check/jeep/renegade
EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	4320	1722	1489	Auto-Data Ford Fiesta VII Sedan 1.6 105 HP 2015	https://www.auto-data.net/en/ford-fiesta-vii-sedan-mk7-facelift-2013-1.6-105hp-powershift-29541
EU-SKODA-FABIA-II-5J2-HATCHBACK-PREFL-01	3992	1642	1498	Auto-Data Škoda Fabia II specifications	https://www.auto-data.net/en/skoda-fabia-model-1559
EU-SKODA-FABIA-II-5J2-HATCHBACK-FACELIFT-01	4000	1642	1498	Škoda Fabia official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Skoda-Fabia-2012-INT.pdf
EU-SKODA-FABIA-II-5J5-WAGON-PREFL-01	4239	1642	1498	Auto-Data Škoda Fabia II specifications	https://www.auto-data.net/en/skoda-fabia-model-1559
EU-SKODA-FABIA-II-5J5-WAGON-FACELIFT-01	4247	1642	1498	Škoda Fabia official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Skoda-Fabia-2012-INT.pdf
EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	4405	1810	1630	Automobile-Catalog Jeep Compass 2.0 CRD Sport 2007	https://www.automobile-catalog.com/car/2007/1330580/jeep_compass_2_0_crd_sport.html
EU-JEEP-PATRIOT-I-MK74-SUV-PREFL-AWD-01	4408	1785	1658	Automobile-Catalog Jeep Patriot 2.0 CRD Limited 2007	https://www.automobile-catalog.com/car/2007/1331435/jeep_patriot_2_0_crd_limited.html
EU-JEEP-COMMANDER-XK-SUV-PREFL-01	4787	1900	1826	Automobile-Catalog Jeep Commander 3.0 CRD Limited 2007	https://www.automobile-catalog.com/car/2007/1328720/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-JEEP-COMMANDER-XK-SUV-FACELIFT-01	4787	1900	1826	CarsGuide Jeep Commander dimensions	https://www.carsguide.com.au/jeep/commander/car-dimensions/2008
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-PREFL-01	4030	1687	1490	Fiat Professional Grande Punto Van technical data	https://www.media.stellantis.com/hu-hu/download-model-document/10?v=1576184405
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490	Fiat Punto official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Fiat-Punto-2010-UK.pdf
EU-SKODA-ROOMSTER-I-5J7-MPV-PREFL-01	4205	1684	1607	Auto-Data Škoda Roomster specifications	https://www.auto-data.net/en/skoda-roomster-model-1561
EU-SKODA-ROOMSTER-I-5J7-FACELIFT-MPV-01	4214	1684	1607	Škoda Roomster official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Skoda-Roomster-2012-INT.pdf
EU-FIAT-CROMA-II-194-VAN-PREFL-01	4756	1775	1597	Fiat New Croma official press information	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-croma-in-uk
EU-FIAT-CROMA-II-194-VAN-FACELIFT-01	4783	1775	1603	Automobile-Catalog Fiat Croma 1.9 Multijet 16V 150 2008	https://www.automobile-catalog.com/car/2008/727790/fiat_croma_1_9_multijet_16v_150_emotion_dpf.html
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan specifications valid from 03/2019	https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan specifications valid from 03/2019	https://www.press.bmwgroup.com/global/article/attachment/T0299451EN/437354
EU-BMW-Z4-G29-CONVERTIBLE-PREFL-01	4324	1864	1304	BMW Z4 specifications valid from 09/2018	https://www.press.bmwgroup.com/global/article/attachment/T0289704EN/442417
EU-BMW-X2-F39-SUV-01	4360	1824	1526	BMW X2 official technical specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286609CS/417929
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0281834IT/409651
EU-FIAT-BRAVO-II-198-VAN-01	4336	1792	1498	Fiat New Bravo official press information	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-bravo-in-uk
EU-FIAT-FIORINO-III-CARGO-VAN-01	3957	1716	1721	Fiat Professional Fiorino official brochure	https://glencom.co.uk/wp-content/uploads/2019/03/fiat-professional-fiorino-brochure.pdf
EU-FIAT-500-I-312-HATCHBACK-PREFL-01	3546	1627	1488	Fiat 500 Electric exact model listing;CarsGuide Fiat 500 2010 dimensions	https://autogidas.lt/en/auto-katalogas/fiat/500/electric-ev-2010-k109237;https://www.carsguide.com.au/fiat/500/car-dimensions/2010
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443	Automoli Renault Megane IV Sedan specifications	https://www.automoli.com/en/vehicles/renault/megane/megane-iv-sedan-5017/
EU-AUDI-A7-C8-4KA-SPORTBACK-01	4969	1908	1422	Audi MediaCenter A7 Sportback facts and figures	https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835
EU-CUPRA-ATECA-I-KH7-SUV-PREFL-AWD-01	4376	1841	1611	New CUPRA Ateca official technical specifications 2018	https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/Img/2018/10/2018-10-29/Technical-Specifications-New-CUPRA-Ateca.pdf
EU-CUPRA-ATECA-I-KH7-SUV-FACELIFT-AWD-01	4386	1841	1599	CUPRA Ateca official brochure 2021	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-ateca-2021.pdf
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	SEAT Leon official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Seat-Leon-2017-UK.pdf
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480	Citroën C4 Cactus official brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Citroen-C4-Cactus-2018-UK.pdf
EU-BMW-8-G14-M850I-CONVERTIBLE-01	4851	1902	1345	BMW 8 Series Convertible specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286150EN/445834
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339	BMW 8 Series Convertible specifications 11/2018	https://www.press.bmwgroup.com/global/article/attachment/T0286150EN/445834
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 Specification Guide June 2023	https://www.media.stellantis.com/uploads/uk/attachment/4885/specificationguide_peugeot508_june2023-64945a246dcb8.pdf
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454	SEAT Leon ST official technical specifications	https://www.seat-cupra-mediacenter.es/content/dam/seat-media-center/Documents/2016/Technical-Specifications-New-SEAT-Leon-ST2016EN.pdf
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461	Škoda Octavia official press kit	https://cdn.skoda-storyboard.com/2017/02/170207-%C5%A0KODA-OCTAVIA-Press-Kit.pdf
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465	Škoda Octavia official press kit	https://cdn.skoda-storyboard.com/2017/02/170207-%C5%A0KODA-OCTAVIA-Press-Kit.pdf
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Opel Crossland X official specification sheet	https://nd-mediagallery2-public-production.s3.amazonaws.com/7a59942555d21186be99fc0e36fb50d9/9424_55031_opel_crossland_x_cosmo_1.2t_my18_spec_sheets_a4l_fc_e_web.pdf
EU-VOLVO-V50-MW-WAGON-01	4514	1770	1452	Volvo V50 official owner manual	https://ldgsvccassets.blob.core.windows.net/pdfs/18939bdb9d7f579ebf9812040b32cd622be31e4c/V50_owners_manual_MY10_EN_tp10852.pdf
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841	Opel Combo official specification sheet	https://nd-mediagallery2-public-production.s3.amazonaws.com/24809f2e6c3805db18caf65ea7c65ec3/combo_cargo_my22_spec_sheet_01_04_2022.pdf
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880	Opel Combo Life official brochure	https://i.i-sgcm.com/new_cars/cars/21843/brochures/brochure_20240305102451.pdf
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683	Jeep Cherokee official specifications May 2019	https://www.media.stellantis.com/uploads/de/DE/2019/JEEP/Preislisten/190520_J_Cherokee_PL.pdf
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	4623	1859	1707	Jeep Cherokee official specifications May 2019	https://www.media.stellantis.com/uploads/de/DE/2019/JEEP/Preislisten/190520_J_Cherokee_PL.pdf
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620	DS 7 Crossback official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds7crossbackpricesandspecs-6172c7be26ee3.pdf
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610	Auto-Data Toyota Corolla Wagon VIII E110 2.0 D-4D 90 HP	https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-2.0-d-4d-90hp-16667
EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-STANDARD-01	3175	1480	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-PIAGGIO-APE-TM-ELECTRIC-PICKUP-LONG-01	3390	1500	1630	Piaggio Ape TM official owner manual	https://www.mondoape.com/manuali/Uso-e-manutenzione-APE-TM-Diesel-EN.pdf
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869	Land Rover Range Rover official specification guide	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/old-range-rover-%28l405%29/Specification-And-Price-Guide-1L4051810000SGBEN01P_tcm295-427210.pdf
EU-TOYOTA-ALLION-I-T240-SEDAN-01	4550	1695	1470	Toyota 75 Years Vehicle Lineage First-generation Allion	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60000074/index.html
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data Volvo V90 specifications	https://www.auto-data.net/en/volvo-v90-model-923
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo V90 Cross Country technical specifications	https://www.volvoclub.org.uk/pdf/v90/v90cc_2017_techspecs.pdf
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539	Volvo Support S60 Cross Country dimensions	https://www.volvocars.com/jp/support/car/s60-cross-country/article/d24bb7d1e21ec6e4c0a801e801cf6114_1fb4a1e231ff3432c0a801e8011f8ab3_18f77489f78f457dc0a801e800a04016/
EU-VOLVO-V60-I-WAGON-FACELIFT-01	4635	1865	1484	Volvo Support V60 2015 dimensions	https://www.volvocars.com/en-kw/support/car/v60/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-XC60-I-FACELIFT-SUV-01	4644	1891	1713	Volvo XC60 official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/Volvo-XC60-2014-INT.pdf
EU-AIXAM-D-TRUCK-2018-VAN-01	3000	1500	1830	Aixam Pro D-Truck official technical sheet	https://fr.scribd.com/document/732494660/Aixampro-Ficheteche-Dtruck3vols2022-Compressed1
EU-AIXAM-D-TRUCK-2018-PLATFORM-CAB-01	3000	1500	1750	Aixam Pro D-Truck official technical sheet	https://fr.scribd.com/document/732494660/Aixampro-Ficheteche-Dtruck3vols2022-Compressed1
EU-VOLVO-V40-II-HATCHBACK-01	4369	1802	1420	Volvo Support V40 dimensions	https://www.volvocars.com/in/support/car/v40/16w17/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
EU-TOYOTA-AVENSIS-I-T22-SEDAN-FACELIFT-01	4520	1710	1425	Auto-Data Toyota Avensis T22 2.0 D-4D 110 HP	https://www.auto-data.net/en/toyota-avensis-t22-2.0-d-4d-110hp-3608
EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	4397	1735	1485	Volkswagen Newsroom Golf IV Variant vehicle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2901-3000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.denso-am.eu/catalog/pv/133338 "https://www.denso-am.eu/catalog/pv/133338"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2274 行）
- 累计尺寸组：dimension_groups_final.tsv（1129 行）

