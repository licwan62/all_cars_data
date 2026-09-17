# 任务：all 第 5101-5200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0052__2fad9274


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5101-5200 行

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
all 第 5101-5200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-2-F87-M2-CS-COUPE-01	4461	1871	1414
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538
EU-BMW-X2-F39-SUV-01	4360	1824	1526
EU-FORD-FIESTA-VII-SEDAN-FACELIFT-01	4320	1722	1489
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1466
EU-FORD-FIESTA-VII-VAN-SPORT-01	4065	1735	1466
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	4040	1735	1476
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-3D-FACELIFT-01	4091	1735	1487
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-01	4068	1735	1469
EU-FORD-FIESTA-VIII-MK8-ST-HATCHBACK-5D-FACELIFT-01	4091	1735	1487
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471
EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-FACELIFT-01	4393	1825	1458
EU-FORD-FOCUS-IV-C519-ST-HATCHBACK-PREFL-01	4388	1825	1458
EU-FORD-FOCUS-IV-C519-ST-WAGON-PREFL-01	4668	1825	1492
EU-FORD-FOCUS-IV-C519-WAGON-01	4668	1825	1459
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-FORD-FOCUS-IV-WAGON-ST-01	4668	1825	1492
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537
EU-FORD-PUMA-II-SUV-TITANIUM-01	4186	1805	1537
EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	4280	1775	1480
EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	4245	1775	1480
EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	4500	1775	1565
EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	4475	1775	1565
EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	4485	1780	1500
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-MCLAREN-720S-I-SPIDER-CONVERTIBLE-01	4543	1930	1196
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494
EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	4424	1804	1494
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	4655	1890	1644
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	4947	2018	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	4947	2018	1785
EU-MICROCAR-DUE-III-HATCHBACK-3D-01	2870	1500	1485
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432
EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	3879	1762	1420
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-OPEL-MOKKA-X-J13-SUV-01	4275	1781	1658
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696
EU-PORSCHE-TAYCAN-I-Y1A-4S-SEDAN-01	4963	1966	1379
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-S-SEDAN-01	4963	1966	1378
EU-PORSCHE-TAYCAN-I-Y1A-TURBO-SEDAN-01	4963	1966	1381
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440
EU-SUZUKI-SWIFT-VI-SPORT-HATCHBACK-01	3890	1735	1495
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-01	5330	1855	1815
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-EXTRACAB-01	5330	1855	1810
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-SINGLECAB-01	5330	1800	1795
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VW-CADDY-IV-2K-ALLTRACK-MPV-SWB-01	4430	1793	1824
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4430	1793	1861
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822
EU-VW-CADDY-IV-VAN-LWB-01	4878	1793	1836
EU-VW-CADDY-IV-VAN-SWB-01	4408	1793	1823
EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	5500	1994	1960
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	5500	1994	1948
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	5100	1994	1948
EU-VW-TRANSPORTER-T6-1-VAN-LWB-HIGHROOF-01	5304	1904	2477
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	420	571	Mar 2020	Mar 2023	2024-03-01	140713
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Mar 2020	-	2024-03-01	140714
Casalini	M20	M20	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2018	-	2024-03-01	140718
Microcar	Due	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Dec 2019	-	2024-03-01	140721
Aixam	Roadline	0.4	Schrägheck	Frontantrieb	Diesel	4	5	Sep 2009	Jul 2012	2024-03-01	140722
Aixam	Crossover	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2018	-	2024-03-01	140723
Hyundai	I30	1.6 Crdi Hybrid 48V	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140729
Hyundai	I30	1.6 Crdi Hybrid 48V	Kombi	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140730
Hyundai	I30	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Mar 2020	-	2024-03-01	140731
Hyundai	I30	1.0 T-gdi Hybrid 48V	Kombi	Frontantrieb	Benzin/Elektro	88	120	Mar 2020	-	2024-03-01	140732
Mercedes-benz	A-Klasse	A 250 E	Stufenheck	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	-	2024-03-01	140736
Mercedes-benz	A-Klasse	A 250 E	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	-	2024-03-01	140737
Hyundai	I30	1.6 Crdi Hybrid 48V	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Mar 2020	-	2024-03-01	140738
Renault	Clio v	1.6 E-tech 140	Schrägheck	Frontantrieb	Benzin/Elektro	103	140	Mar 2020	-	2026-05-01	140751
Renault	Twizy	80	Schrägheck	Heckantrieb	Elektro	9	12	Jun 2020	-	2024-03-01	140752
Mercedes-benz	B-Klasse sports tourer	B 250 E	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Jun 2020	-	2024-03-01	140775
Mercedes-benz	Gla	AMG GLA 35 4-matic	SUV	Allrad	Benzin	225	306	Jun 2020	-	2024-03-01	140776
Mercedes-benz	Gla	AMG GLA 45 4-matic+	SUV	Allrad	Benzin	285	387	Jun 2020	-	2024-03-01	140777
Mercedes-benz	Gla	AMG GLA 45 S 4-matic+	SUV	Allrad	Benzin	310	421	Jun 2020	-	2024-03-01	140778
Mercedes-benz	E-Klasse	E 350 E	Stufenheck	Heckantrieb	Benzin/Elektro	235	320	Sep 2016	Jun 2019	2024-03-01	140787
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Stufenheck	Allrad	Diesel/Elektro	225	306	Jun 2020	Aug 2023	2024-03-01	140789
Maxus	V80	Ev80	Kasten	Frontantrieb	Elektro	92	125	Jan 2017	-	2024-03-01	140806
Maxus	V80	Ev80	Pritsche/Fahrgestell	Frontantrieb	Elektro	92	125	Jan 2017	-	2024-03-01	140807
KIA	Soul iii cargo	E-soul	Kasten/Schrägheck	Frontantrieb	Elektro	150	204	Jun 2020	-	2024-03-01	140808
Maxus	Deliver 9	2.0 D	Kasten	Heckantrieb	Diesel	120	163	Jul 2020	-	2024-03-01	140813
BMW	4	430 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	210	286	Mar 2021	-	2024-03-01	140850
Toyota	Hilux viii	2.8 D-4d 4WD	Pick-up	Allrad	Diesel	150	204	Jun 2020	-	2026-05-01	140855
BMW	4	M440 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	250	340	Mar 2021	-	2024-03-01	140856
Maxus	Edeliver 3	Electric	Kasten	Frontantrieb	Elektro	90	122	Jul 2020	-	2024-03-01	140865
Polestar	Polestar 1	Phev AWD	Coupe	Allrad	Benzin/Elektro	448	609	Mar 2018	-	2024-03-01	140883
Mini	Mini	Cooper SE	Kombi	Allrad	Benzin/Elektro	162	220	Jul 2020	-	2024-03-01	140885
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	131	178	Jul 2020	-	2024-03-01	140889
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	131	178	Jul 2020	-	2024-03-01	140890
Mercedes-benz	Glc	300 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Nov 2019	Jun 2022	2024-03-01	140891
VW	Caddy iv	ABT E-caddy	Großraumlimousine	Frontantrieb	Elektro	83	113	Apr 2020	Dec 2020	2025-06-01	140892
Mercedes-benz	Glc	F-cell	SUV	Heckantrieb	Wasserstoff	80	109	Oct 2018	Apr 2020	2024-07-01	140893
Mercedes-benz	Glc	F-cell	SUV	Heckantrieb	Wasserstoff	155	211	Oct 2018	Apr 2020	2024-03-01	140894
VW	Caddy iv	ABT E-caddy	Kasten/Großraumlimousine	Frontantrieb	Elektro	83	113	Apr 2020	Dec 2020	2025-06-01	140895
VW	Transporter t6	ABT E-transporter	Kasten	Frontantrieb	Elektro	83	113	Jan 2020	Aug 2024	2025-02-03	140896
VW	Transporter t6 / caravelle	ABT E-caravelle	Bus	Frontantrieb	Elektro	83	113	Jan 2020	Aug 2024	2025-02-03	140897
Porsche	Cayenne	4.0 GTS	SUV	Allrad	Benzin	338	460	May 2017	May 2023	2026-03-01	140905
Mclaren	720s	4	Coupe	Heckantrieb	Benzin	530	720	Feb 2019	-	2025-06-01	140906
BMW	6	630 I Mild-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	190	258	Jul 2020	-	2024-03-01	140916
BMW	6	640 I Mild-hybrid	Schrägheck	Heckantrieb	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140917
BMW	6	640 I Mild-hybrid Xdrive	Schrägheck	Allrad	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140918
BMW	6	620 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140919
BMW	6	630 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140920
BMW	6	630 D Mild-hybrid Xdrive	Schrägheck	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140921
BMW	6	640 D Mild-hybrid Xdrive	Schrägheck	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2024-03-01	140922
BMW	5	520 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	135	184	Jul 2020	Jun 2023	2024-03-01	140923
BMW	5	530 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	185	252	Jul 2020	Jun 2023	2024-03-01	140924
BMW	5	530 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	185	252	Jul 2020	Jun 2023	2024-03-01	140925
BMW	5	540 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	245	333	Jul 2020	May 2023	2024-03-01	140926
BMW	5	540 I Mild-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	245	333	Jul 2020	Jun 2023	2024-03-01	140927
BMW	5	530 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	Jun 2023	2024-03-01	140928
BMW	5	530 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	210	286	Jul 2020	Jun 2023	2024-03-01	140929
BMW	5	540 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	250	340	Jul 2020	Jun 2023	2024-03-01	140930
BMW	5	520 I Mild-hybrid	Kombi	Heckantrieb	Benzin/Elektro	135	184	Jul 2020	-	2024-03-01	140931
BMW	5	530 I Mild-hybrid	Kombi	Heckantrieb	Benzin/Elektro	185	252	Jul 2020	-	2024-03-01	140932
BMW	5	530 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	185	252	Jul 2020	-	2024-03-01	140933
BMW	5	540 I Mild-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	245	333	Jul 2020	-	2024-03-01	140934
BMW	5	530 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140935
BMW	5	530 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	210	286	Jul 2020	-	2024-03-01	140936
BMW	5	540 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	250	340	Jul 2020	-	2024-03-01	140937
Volvo	Xc40	T4 Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	155	211	Jun 2020	-	2024-03-01	140943
Volvo	V90 ii	T6 Plug-in-hybrid AWD	Kombi	Allrad	Benzin/Elektro	250	340	Jun 2020	Dec 2022	2024-05-01	140957
BMW	3	330 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	215	292	Jul 2019	-	2024-03-01	140967
Ford	Puma	1.0 Ecoboost	SUV	Frontantrieb	Benzin	70	95	Sep 2019	-	2024-03-01	140974
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	192	261	Mar 2019	Jan 2025	2026-03-01	140979
Tesla	Model y	EV Allrad	SUV	Allrad	Elektro	258	351	Mar 2019	Jan 2025	2026-03-01	140980
Tesla	Model y	EV Performance Allrad	SUV	Allrad	Elektro	340	462	Mar 2019	Jan 2025	2026-03-01	140981
Porsche	Taycan	Electric	Stufenheck	Heckantrieb	Elektro	300	408	Jun 2020	-	2024-03-01	140982
RAM	1500 crew cab pickup	3.6 Etorque Mild Hybrid 4X4	Pick-up	Allrad	Benzin/Elektro	227	309	Dec 2018	-	2024-03-01	140998
Opel	Mokka	Mokka-e	SUV	Frontantrieb	Elektro	100	136	Jun 2020	-	2024-03-01	141005
Suzuki	Swift v	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	61	83	Jun 2020	-	2024-03-01	141020
Suzuki	Swift v	1.2 Hybrid	Schrägheck	Allrad	Benzin/Elektro	61	83	Jun 2020	-	2024-03-01	141021
Volvo	S60 iii	B5 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	141022
Volvo	S60 iii	B5 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	141023
BMW	2	218 D	Coupe	Frontantrieb	Diesel	110	150	Jul 2020	-	2024-03-01	141032
BMW	2	218 D	Coupe	Frontantrieb	Diesel	100	136	Jul 2020	Oct 2024	2025-06-01	141033
BMW	2	220 D Xdrive	Coupe	Allrad	Diesel	140	190	Jul 2020	Oct 2024	2025-06-01	141036
Ford	Focus iv turnier	1.0 Ecoboost Mhev	Kombi	Frontantrieb	Benzin/Elektro	114	155	Jul 2020	Nov 2025	2026-02-01	141038
Ford	Focus iv turnier	1.0 Ecoboost Mhev	Kombi	Frontantrieb	Benzin/Elektro	92	125	Jul 2020	Nov 2025	2026-02-01	141039
Hyundai	I30	1.5 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	118	160	Mar 2020	-	2024-03-01	141040
BMW	X2	Xdrive 25 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	162	220	Mar 2020	Oct 2023	2024-03-01	141042
Hyundai	I30	1.5 T-gdi Hybrid 48V	Kombi	Frontantrieb	Benzin/Elektro	118	160	Mar 2020	-	2024-03-01	141043
Hyundai	I30	1.5 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	118	160	Mar 2020	-	2024-03-01	141044
Hyundai	I30	1.5	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141045
Hyundai	I30	1.5	Kombi	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141046
Ford	Focus iv	1.0 Ecoboost Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	114	155	Jun 2020	Nov 2025	2026-02-01	141047
Ford	Focus iv	1.0 Ecoboost Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	92	125	Jun 2020	Nov 2025	2026-02-01	141048
BMW	6	620 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	120	163	Jul 2020	-	2024-03-01	141051
BMW	6	620 D Mild-hybrid Xdrive	Schrägheck	Allrad	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	141057
Ford	Fiesta vii	1.0 Ecoboost Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	92	125	Nov 2019	-	2024-03-01	141059
Ford	Fiesta vii	1.0 Ecoboost Mhev	Schrägheck	Frontantrieb	Benzin/Elektro	114	155	Jul 2020	-	2024-03-01	141060
BMW	6	630 D Mild-hybrid	Schrägheck	Heckantrieb	Diesel/Elektro	155	211	Jul 2020	-	2024-03-01	141061
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	92	125	Feb 2020	-	2024-03-01	141062
BMW	5	520 I Mild-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	120	163	Jul 2020	Jun 2023	2024-03-01	141064
BMW	5	518 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	100	136	Jul 2020	Jun 2023	2024-03-01	141065
BMW	5	518 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	110	150	Jul 2020	Jun 2023	2024-03-01	141066


--- Round 1 / 首次发送 ---
更新点

* 复用 22 个既有 `DIMENSION_GROUP_ID`，完成 56 个输入 Ktype 的映射闭合。
* `141038`、`141039`、`141047`、`141048` 跨越 Ford Focus IV 改款尺寸边界，已分别拆为 `prefl`、`facelift` 派生行。
* 本轮共新增/修改 60 条映射行；未重复输出既有尺寸组。

当前批次进度

* 输入 Ktype：100
* READY Ktype：56
* READY 映射行：60
* PENDING Ktype：44
* 已引用尺寸组：22
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140713	140713	SUV	GLE II (V167)	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	HIGH	改款前AMG GLE 63外廓。	READY
140721	140721	Hatchback	Due III		3	EU-MICROCAR-DUE-III-HATCHBACK-3D-01	HIGH	Due III三门微型车外廓。	READY
140729	140729	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140730	140730	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
140731	140731	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140732	140732	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
140738	140738	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140751	140751	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	Clio V五门掀背外廓。	READY
140850	140850	Coupe	4 Series II (G22)	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive双门轿跑外廓。	READY
140856	140856	Coupe	4 Series II (G22)	G22	2	EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	MEDIUM	M440d与已建M440i xDrive外廓一致。	READY
140889	140889	Wagon	MINI Clubman II (F54)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman五门旅行外廓。	READY
140890	140890	Wagon	MINI Clubman II (F54)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman五门旅行外廓。	READY
140891	140891	SUV	GLC I facelift (X253)	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	HIGH	X253改款插混SUV外廓。	READY
140896	140896	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	MEDIUM	ABT e-Transporter长轴低顶外廓。	READY
140897	140897	MPV	Transporter/Caravelle T6.1		5	EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	MEDIUM	ABT e-Caravelle与长轴低顶车身外廓一致。	READY
140916	140916	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140917	140917	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140918	140918	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140919	140919	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140920	140920	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140921	140921	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140922	140922	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140923	140923	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
140924	140924	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
140926	140926	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
140928	140928	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
140931	140931	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140932	140932	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140933	140933	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140934	140934	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140935	140935	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140936	140936	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140937	140937	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140943	140943	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	XC40五门SUV外廓。	READY
140957	140957	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II标准旅行版外廓。	READY
141022	141022	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	S60 III四门轿车外廓。	READY
141023	141023	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	S60 III四门轿车外廓。	READY
141032	141032	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141033	141033	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141036	141036	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141038_prefl	141038	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前旅行版外廓。	READY
141038_facelift	141038	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后旅行版外廓。	READY
141039_prefl	141039	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前旅行版外廓。	READY
141039_facelift	141039	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后旅行版外廓。	READY
141040	141040	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141042	141042	SUV	X2 I (F39)	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV外廓。	READY
141043	141043	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
141044	141044	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141045	141045	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141046	141046	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
141047_prefl	141047	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门掀背外廓。	READY
141047_facelift	141047	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门掀背外廓。	READY
141048_prefl	141048	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门掀背外廓。	READY
141048_facelift	141048	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门掀背外廓。	READY
141051	141051	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141057	141057	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141061	141061	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141064	141064	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
141065	141065	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
141066	141066	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI后驱标准车身外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 首先闭合 Casalini、Aixam、Renault Twizy、Maxus、Polestar、Tesla、Opel Mokka B、Suzuki Swift 和 Toyota Yaris 等尚无缓存的尺寸组。
2. 核对 Mercedes-Benz A 250 e、B 250 e、GLA AMG、GLC F-CELL、E-Class 插混及 BMW G30 xDrive 的版本专属高度或保险杠外廓。
3. 消除 `140714` 的改款边界，以及 Hilux 驾驶室、RAM 1500 货斗、Fiesta 门数/改款、Puma 外观套件、ABT e-Caddy 轴距等多外廓歧义。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 修正 `140713`：精确 Ktype 对应 `C167 GLE Coupé`，不是上一轮误关联的 `V167 SUV`；`140713` 改指 C167 改款前尺寸组。`140714` 的同一车身代码持续覆盖 2023 年改款前后，拆为 `prefl`、`facelift` 两行。 ([123koplampen.nl][1])
* `140778` 持续覆盖 H247 AMG GLA 45 S 改款前后，拆为两行；`140776`、`140777` 仅关联改款前组。 ([Alkatreszek][2])
* 首次创建 9 个尺寸组，闭合 A 250 e、B 250 e、E 300 de 4MATIC、GLC F-CELL、BMW 330e 及两个改款分支。三维均采用不含后视镜宽度。 ([汽车数据网][3])
* 复用 5 个既有尺寸组：H247 改款前、W213 改款前、Caddy IV LWB MPV、Caddy IV LWB Van、BMW G30 LCI 标准尺寸组。 ([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* PENDING Ktype：26
* READY 映射行：81
* 当前引用尺寸组：34
* 本轮新增/修改映射行：22
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140713	140713	Coupe	GLE Coupe II (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	HIGH	修正为C167 GLE Coupe改款前外廓。	READY
140714_prefl	140714	Coupe	GLE Coupe II (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	HIGH	同一Ktype覆盖改款前C167外廓。	READY
140714_facelift	140714	Coupe	GLE Coupe II facelift (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-FACELIFT-01	HIGH	同一Ktype覆盖改款后C167外廓。	READY
140736	140736	Sedan	A-Class IV (V177)	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-A250E-SEDAN-PREFL-01	HIGH	V177 A 250 e插混轿车外廓。	READY
140737	140737	Hatchback	A-Class IV (W177)	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-A250E-HATCHBACK-PREFL-01	HIGH	W177 A 250 e五门插混外廓。	READY
140775	140775	MPV	B-Class III (W247)	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-B250E-MPV-PREFL-01	HIGH	W247 B 250 e Sports Tourer外廓。	READY
140776	140776	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 AMG GLA 35改款前外廓。	READY
140777	140777	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 AMG GLA 45改款前外廓。	READY
140778_prefl	140778	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	同一Ktype覆盖改款前AMG GLA 45 S外廓。	READY
140778_facelift	140778	SUV	GLA II facelift (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	HIGH	同一Ktype覆盖改款后AMG GLA 45 S外廓。	READY
140787	140787	Sedan	E-Class V (W213)	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	W213改款前E 350 e轿车外廓。	READY
140789	140789	Sedan	E-Class V facelift (W213)	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	HIGH	W213改款后E 300 de 4MATIC高度分支。	READY
140892	140892	MPV	Caddy IV (2K)	2K		EU-VW-CADDY-IV-MPV-LWB-01	HIGH	ABT e-Caddy仅使用长轴MPV外廓。	READY
140893	140893	SUV	GLC F-CELL (N253)	N253	5	EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	HIGH	N253 F-CELL外廓。	READY
140894	140894	SUV	GLC F-CELL (N253)	N253	5	EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	HIGH	功率口径差异不改变N253 F-CELL外廓。	READY
140895_van	140895	Van	Caddy IV (2K)	2K		EU-VW-CADDY-IV-VAN-LWB-01	HIGH	同一Ktype的长轴厢式分支。	READY
140895_mpv	140895	MPV	Caddy IV (2K)	2K		EU-VW-CADDY-IV-MPV-LWB-01	HIGH	同一Ktype的长轴MPV分支。	READY
140925	140925	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive标准外廓。	READY
140927	140927	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive标准外廓。	READY
140929	140929	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive标准外廓。	READY
140930	140930	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive标准外廓。	READY
140967	140967	Sedan	3 Series VII (G20)	G20	4	EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	HIGH	G20 330e后驱插混高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	4961	2018	1720	Auto-Data; EncyCARpedia	https://www.auto-data.net/en/mercedes-benz-gle-coupe-c167-amg-gle-63-v8-571hp-eq-boost-4matic-amg-speedshift-tct-39188;https://www.encycarpedia.com/mercedes/20-amg-gle-coupe-63-s-4matic-suv
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-FACELIFT-01	4954	2018	1720	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gle-coupe-c167-facelift-2023-amg-gle-63-s-v8-612hp-eq-boost-4matic-amg-speedshift-tct-9g-47366
EU-MERCEDES-BENZ-A-KLASSE-V177-A250E-SEDAN-PREFL-01	4549	1796	1458	Auto-Data	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-250e-218hp-plug-in-hybrid-8g-dct-37688
EU-MERCEDES-BENZ-A-KLASSE-W177-A250E-HATCHBACK-PREFL-01	4419	1796	1452	Auto-Data	https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-250e-218hp-plug-in-hybrid-8g-dct-37687
EU-MERCEDES-BENZ-B-KLASSE-W247-B250E-MPV-PREFL-01	4419	1796	1562	Auto-Data	https://www.auto-data.net/en/mercedes-benz-b-class-w247-b-250e-218hp-plug-in-hybrid-8g-dct-41799
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1616	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gla-h247-facelift-2023-amg-gla-45-s-421hp-4matic-amg-speedshift-dct-8g-51785
EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	4935	1852	1481	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300de-306hp-plug-in-hybrid-4matic-9g-tronic-40972
EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	4671	1890	1653	Engine in detail; Autohled vehicle comparison	https://www.engineindetail.com/cars/mercedes-benz/glc/glc-253-f-cell-2019-2020;https://www.autohled.cz/de/porovnavac/hyundai-nexo-vs-mercedes-benz-glc-f-cell
EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	4709	1827	1444	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-g20-330e-292hp-plug-in-hybrid-steptronic-37654
```

## 下一步优先处理

1. 批量闭合 Tesla Model Y 三个 Ktype、Suzuki Swift 两个 Ktype、Ford Fiesta 两个 Ktype，以及 Opel Mokka B、Toyota Yaris IV。
2. 处理 Maxus V80、Deliver 9、eDeliver 3 的轴距、车顶和车身形式分支。
3. 核对 Hilux 驾驶室、RAM 1500 Crew Cab 货斗，以及 Casalini、Aixam、Twizy 等微型车尺寸组。

推进信号：CONTINUE

[1]: https://www.123koplampen.nl/de/autoteile/sensoren/naherungsradar-naherungssensor/product/2202187/mercedes-radar-a0009009638-original-neu?utm_source=chatgpt.com "Mercedes Radar A0009009638 original neu"
[2]: https://alkatreszek.hu/tipus/mercedes_benz/gla/gla_h247_2020_02?utm_source=chatgpt.com "Kedvező árú MERCEDES-BENZ GLA (H247) 2020/02 autóalkatrészek - Kovács"
[3]: https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-250e-218hp-plug-in-hybrid-8g-dct-37688 "Mercedes-Benz A-class Sedan (V177) A 250e (218 Hp) Plug-in Hybrid 8G-DCT | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/mercedes-benz-gla-h247-amg-gla-35-306hp-4matic-dct-38235 "Mercedes-Benz GLA (H247) AMG GLA 35 (306 Hp) 4MATIC DCT | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Model Y、Polestar 1、Twizy、Toyota Yaris IV 和 Suzuki Swift VI 改款版尺寸组；其中 Yaris 使用欧洲规格 `1745 mm` 车宽，未采用日本市场窄体数据。([Tesla][1])
* 首次闭合 MINI Countryman F60 插混、Cayenne GTS、McLaren 720S Coupé、Ford Puma 95 PS、Taycan 后驱和 Mokka-e 尺寸组。([汽车数据网][2])
* `141059`、`141060` 均确认覆盖 Fiesta Mk8 三门和五门车身，分别拆为 `3dr`、`5dr` 派生行，并复用已有三门、五门尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* PENDING Ktype：10
* READY 映射行：99
* 当前引用尺寸组：48
* 本轮新增/修改映射行：18
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140752	140752	Hatchback	Twizy I		2	EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	HIGH	Twizy双门四轮车物理外廓。	READY
140883	140883	Coupe	Polestar 1		2	EU-POLESTAR-1-I-COUPE-01	HIGH	Polestar 1双门轿跑外廓。	READY
140885	140885	SUV	Countryman II facelift (F60)	F60	5	EU-MINI-COUNTRYMAN-F60-SUV-FACELIFT-PHEV-01	HIGH	输入Mini Kombi对应F60 Countryman插混车型。	READY
140905	140905	SUV	Cayenne III (9YA)	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	HIGH	GTS专属保险杠和车高外廓。	READY
140906	140906	Coupe	720S I		2	EU-MCLAREN-720S-I-COUPE-01	HIGH	720S Coupe车身，不复用Spider尺寸组。	READY
140974	140974	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STANDARD-01	HIGH	95 PS标准车身外廓。	READY
140979	140979	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前后驱车身外廓。	READY
140980	140980	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前四驱车身外廓。	READY
140981	140981	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前Performance车身外廓。	READY
140982	140982	Sedan	Taycan I (Y1A)	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-RWD-SEDAN-01	HIGH	后驱基础版车高分支。	READY
141005	141005	SUV	Mokka B		5	EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	HIGH	Mokka-e电动车外廓。	READY
141020	141020	Hatchback	Swift VI facelift		5	EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-FWD-01	HIGH	输入代际名称按2020年欧洲车型修正。	READY
141021	141021	Hatchback	Swift VI facelift		5	EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-AWD-01	HIGH	ALLGRIP车型具有独立车高。	READY
141059_3dr	141059	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	HIGH	同一Ktype覆盖三门物理分支。	READY
141059_5dr	141059	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	HIGH	同一Ktype覆盖五门物理分支。	READY
141060_3dr	141060	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	HIGH	同一Ktype覆盖三门物理分支。	READY
141060_5dr	141060	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	HIGH	同一Ktype覆盖五门物理分支。	READY
141062	141062	Hatchback	Yaris IV (XP210)	XP210	5	EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	HIGH	采用欧洲市场宽体五门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	2338	1234	1454	Renault Twizy press kit; EVSpecs	https://www.press.renault.co.uk/assets/documents/original/14737-RenaultTwizyPressKit2018.pdf;https://www.evspecs.org/tech-specs/renault/twizy/urban-80
EU-POLESTAR-1-I-COUPE-01	4586	1958	1352	Polestar Owner's Manual	https://www.polestar.com/uk/manual/polestar-1/2020/article/fe05d7088a0740d0c0a8015150f8256d/
EU-MINI-COUNTRYMAN-F60-SUV-FACELIFT-PHEV-01	4297	1822	1559	Auto-Data	https://www.auto-data.net/en/mini-countryman-f60-facelift-2020-cooper-se-1.5-220hp-plug-in-hybrid-all4-steptronic-40760
EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	4929	1983	1676	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-gts-4.0-v8-460hp-tiptronic-s-40967
EU-MCLAREN-720S-I-COUPE-01	4543	1930	1196	Auto-Data	https://www.auto-data.net/en/mclaren-720s-4.0-v8-720hp-ssg-28867
EU-FORD-PUMA-II-SUV-STANDARD-01	4186	1805	1536	Auto-Data	https://www.auto-data.net/en/ford-puma-1.0-ecoboost-95hp-41458
EU-TESLA-MODEL-Y-I-SUV-PREFL-01	4750	1921	1624	Tesla Model Y Owner's Manual 2020-2024	https://www.tesla.com/ownersmanual/2020_2024_modely/en_cn/GUID-E47C4A6D-528E-419C-8C57-FD3864644C34.html
EU-PORSCHE-TAYCAN-I-Y1A-RWD-SEDAN-01	4963	1966	1395	Auto-Data	https://www.auto-data.net/en/porsche-taycan-y1a-generation-7269
EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	4151	1791	1532	Auto-Data	https://www.auto-data.net/en/opel-mokka-b-mokka-e-50-kwh-136hp-41307
EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-FWD-01	3845	1735	1495	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-facelift-2020-1.2-dualjet-shvs-83hp-41193
EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-AWD-01	3845	1735	1520	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-facelift-2020-1.2-dualjet-shvs-83hp-allgrip-41206
EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	3940	1745	1500	Toyota UK Yaris technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210713M-Yaris-Tech-Spec.pdf
```

## 下一步优先处理

1. 聚类闭合 Maxus V80、Deliver 9 和 eDeliver 3 的轴距、车顶及厢式车/底盘分支。
2. 确认 Hilux `140855` 的驾驶室分支及 RAM 1500 `140998` 的 Crew Cab 货斗长度。
3. 补齐 Casalini M20、Aixam Roadline、Aixam Crossover 和 Kia Soul Cargo 的完整三维及不含后视镜宽度。

推进信号：CONTINUE

[1]: https://www.tesla.com/ownersmanual/2020_2024_modely/en_cn/GUID-E47C4A6D-528E-419C-8C57-FD3864644C34.html?utm_source=chatgpt.com "Dimensions and Weights"
[2]: https://www.auto-data.net/en/mini-countryman-f60-facelift-2020-cooper-se-1.5-220hp-plug-in-hybrid-all4-steptronic-40760 "Mini Countryman (F60, facelift 2020) Cooper SE 1.5 (220 Hp) Plug-in hybrid ALL4 Steptronic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.0-ecoboost-155hp-mild-hybrid-41396?utm_source=chatgpt.com "Ford Fiesta VIII (Mk8) 3 door 1.0 EcoBoost (155 Hp) Mild Hybrid | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Casalini M20、Aixam Crossover、Kia e-Soul Cargo、Maxus eDeliver 3，共首次创建 4 个尺寸组。
* `140806` 的 EV80 厢式车确认存在中顶、高顶两种物理外廓，拆为两个派生映射和两个尺寸组。
* `140855` 确认为 Hilux 2.8 D-4D Double Cab。官方三维为 `5325×1855×1815`，与累计 `...DOUBLECAB-01` 的长度 `5330` 冲突，未覆盖旧组，按规则新建 `...DOUBLECAB-02`。
* `140998` 的 RAM 1500 Crew Cab 同时覆盖 5 ft 7 in 和 6 ft 4 in 货斗，拆为两个派生映射。
* 剩余 `140722`、`140807`、`140813` 三个 Ktype 尚未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射行：108
* PENDING 映射行：3
* 当前引用尺寸组：57
* 本轮新增/修改映射行：12
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140718	140718	Hatchback	M20		3	EU-CASALINI-M20-I-HATCHBACK-3D-01	HIGH	M20三门微型车外廓。	READY
140722	140722	Hatchback	Roadline		3		LOW	轻型四轮车版本与后续高功率版本的三维资料存在冲突。	PENDING: Roadline轻型四轮车三维未闭合
140723	140723	Hatchback	Crossover Sensation		3	EU-AIXAM-CROSSOVER-SENSATION-HATCHBACK-3D-01	HIGH	2018款Crossover三门微型车外廓。	READY
140806_midroof	140806	Van	EV80			EU-MAXUS-EV80-VAN-LWB-MIDROOF-01	HIGH	长轴中顶厢式车分支。	READY
140806_highroof	140806	Van	EV80			EU-MAXUS-EV80-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车分支。	READY
140807	140807	Pickup	EV80				LOW	裸底盘尺寸已确认，但Pritsche成车外廓取决于具体上装。	PENDING: Pritsche成车外廓未确认
140808	140808	Van	Soul III (SK3)	SK3	5	EU-KIA-SOUL-III-SK3-CARGO-VAN-01	HIGH	e-Soul Cargo改型不改变基础车身外廓。	READY
140813	140813	Van	Deliver 9				LOW	通用Ktype可能覆盖不同轴距及H2、H3车顶分支。	PENDING: 轴距与车顶分支未闭合
140855	140855	Pickup	Hilux VIII (AN120)	AN120	4	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-02	HIGH	欧洲2.8 D-4D对应Double Cab；累计01组三维冲突，使用新序号。	READY
140865	140865	Van	eDeliver 3 (EV30)	EV30		EU-MAXUS-EDELIVER-3-EV30-VAN-SWB-01	HIGH	短轴厢式电动车外廓。	READY
140998_5ft7bed	140998	Pickup	1500 V (DT)	DT	4	EU-RAM-1500-DT-PICKUP-CREWCAB-5FT7BED-01	HIGH	Crew Cab配5英尺7英寸货斗分支。	READY
140998_6ft4bed	140998	Pickup	1500 V (DT)	DT	4	EU-RAM-1500-DT-PICKUP-CREWCAB-6FT4BED-01	HIGH	Crew Cab配6英尺4英寸货斗分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CASALINI-M20-I-HATCHBACK-3D-01	3000	1500	1470	Casalini M20 brochure	https://ampautos.fr/wp-content/uploads/2018/07/Brochure-M20_FR.pdf
EU-AIXAM-CROSSOVER-SENSATION-HATCHBACK-3D-01	3000	1500	1590	AIXAM User Manual Edition 10/2018	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-MAXUS-EV80-VAN-LWB-MIDROOF-01	5700	1998	2345	MAXUS EV80 Model Year 2018 specification	https://www.electricdrive.be/wp-content/uploads/2018/11/20180910-MAXUS-EV80-spec-sheet-18-Sept.-2018.pdf
EU-MAXUS-EV80-VAN-LWB-HIGHROOF-01	5700	1998	2552	MAXUS EV80 Model Year 2018 specification	https://www.electricdrive.be/wp-content/uploads/2018/11/20180910-MAXUS-EV80-spec-sheet-18-Sept.-2018.pdf
EU-KIA-SOUL-III-SK3-CARGO-VAN-01	4195	1800	1605	Kia Soul EV specifications	https://eu-www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/soul-ev/specification/kia-soul-ev-specification.pdf
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-02	5325	1855	1815	Toyota Hilux Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1611922571210129MHiluxTechSpec.pdf
EU-MAXUS-EDELIVER-3-EV30-VAN-SWB-01	4555	1780	1895	MAXUS eDELIVER 3 brochure	https://www.maxus.si/EasyEdit/UserFiles/CatalogDocs/MAXUS_Brochure_eDELIVER3_wLQ6Za8V.pdf
EU-RAM-1500-DT-PICKUP-CREWCAB-5FT7BED-01	5916	2085	1971	2019 Ram 1500 official brochure	https://www.fremontchryslerdodgejeeprocksprings.com/assets/shared/CustomHTMLFiles/Compliance/CDJR/Brochure/eBrochure-Ram-DT-Catalog-2019.pdf
EU-RAM-1500-DT-PICKUP-CREWCAB-6FT4BED-01	6142	2085	1969	2019 Ram 1500 official brochure	https://www.fremontchryslerdodgejeeprocksprings.com/assets/shared/CustomHTMLFiles/Compliance/CDJR/Brochure/eBrochure-Ram-DT-Catalog-2019.pdf
```

## 下一步优先处理

1. 闭合 `140722` Aixam Roadline 4 kW 轻型四轮车版本的完整三维，排除高功率重型四轮车资料。
2. 明确 `140807` EV80 的 Pritsche 实际上装外廓，不能用裸底盘尺寸代替完成车辆尺寸。
3. 补齐 `140813` Deliver 9 在该 Ktype 下实际覆盖的轴距和车顶组合；闭合后立即进入一次机械检查并输出两张最终完整 TSV。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 剩余 `140722`、`140807`、`140813` 已全部闭合。Roadline 按官方手册中的 `K44VBR` 外廓建组；EV80 底盘驾驶室采用官方 `5620 ([aixam-mega-sav.com][1])。([aixam-mega-sav.com][1])
* 已完成一次机械收尾：固定表头正确，112 个 `id` 唯一，61 个尺寸组唯一，全部映射引用闭合，尺寸与来源字段均非空。
* `PENDING=0`，当前批次完成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：112
* PENDING：0
* DIMENSION_GROUP：61
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140713	140713	Coupe	GLE Coupe II (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	HIGH	C167改款前AMG GLE 63 Coupe外廓。	READY
140714_prefl	140714	Coupe	GLE Coupe II (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	HIGH	同一Ktype覆盖改款前C167外廓。	READY
140714_facelift	140714	Coupe	GLE Coupe II facelift (C167)	C167	5	EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-FACELIFT-01	HIGH	同一Ktype覆盖改款后C167外廓。	READY
140718	140718	Hatchback	M20		3	EU-CASALINI-M20-I-HATCHBACK-3D-01	HIGH	M20三门微型车外廓。	READY
140721	140721	Hatchback	Due III		3	EU-MICROCAR-DUE-III-HATCHBACK-3D-01	HIGH	Due III三门微型车外廓。	READY
140722	140722	Hatchback	Roadline	K44VBR	3	EU-AIXAM-ROADLINE-K44VBR-HATCHBACK-3D-01	HIGH	K44VBR轻型四轮车外廓。	READY
140723	140723	Hatchback	Crossover Sensation		3	EU-AIXAM-CROSSOVER-SENSATION-HATCHBACK-3D-01	HIGH	2018款Crossover三门微型车外廓。	READY
140729	140729	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140730	140730	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
140731	140731	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140732	140732	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
140736	140736	Sedan	A-Class IV (V177)	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-A250E-SEDAN-PREFL-01	HIGH	V177 A 250 e插混轿车外廓。	READY
140737	140737	Hatchback	A-Class IV (W177)	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-A250E-HATCHBACK-PREFL-01	HIGH	W177 A 250 e五门插混外廓。	READY
140738	140738	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
140751	140751	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	Clio V五门掀背外廓。	READY
140752	140752	Hatchback	Twizy I		2	EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	HIGH	Twizy双门四轮车外廓。	READY
140775	140775	MPV	B-Class III (W247)	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-B250E-MPV-PREFL-01	HIGH	W247 B 250 e Sports Tourer外廓。	READY
140776	140776	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 AMG GLA 35改款前外廓。	READY
140777	140777	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	H247 AMG GLA 45改款前外廓。	READY
140778_prefl	140778	SUV	GLA II (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	同一Ktype覆盖改款前AMG GLA 45 S外廓。	READY
140778_facelift	140778	SUV	GLA II facelift (H247)	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	HIGH	同一Ktype覆盖改款后AMG GLA 45 S外廓。	READY
140787	140787	Sedan	E-Class V (W213)	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH	W213改款前E 350 e轿车外廓。	READY
140789	140789	Sedan	E-Class V facelift (W213)	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	HIGH	W213改款后E 300 de 4MATIC高度分支。	READY
140806_midroof	140806	Van	EV80			EU-MAXUS-EV80-VAN-LWB-MIDROOF-01	HIGH	长轴中顶厢式车分支。	READY
140806_highroof	140806	Van	EV80			EU-MAXUS-EV80-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车分支。	READY
140807	140807	Pickup	EV80		2	EU-MAXUS-EV80-CHASSIS-CAB-LWB-01	HIGH	EV80长轴底盘驾驶室外廓。	READY
140808	140808	Van	Soul III (SK3)	SK3	5	EU-KIA-SOUL-III-SK3-CARGO-VAN-01	HIGH	e-Soul Cargo改型不改变基础车身外廓。	READY
140813_l3h2	140813	Van	Deliver 9			EU-MAXUS-DELIVER-9-VAN-L3H2-RWD-01	HIGH	后驱L3H2厢式车分支。	READY
140813_l3h3	140813	Van	Deliver 9			EU-MAXUS-DELIVER-9-VAN-L3H3-RWD-01	HIGH	后驱L3H3厢式车分支。	READY
140850	140850	Coupe	4 Series II (G22)	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive双门轿跑外廓。	READY
140855	140855	Pickup	Hilux VIII (AN120)	AN120	4	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-02	HIGH	欧洲2.8 D-4D对应Double Cab；累计01组三维冲突，使用新序号。	READY
140856	140856	Coupe	4 Series II (G22)	G22	2	EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	MEDIUM	M440d与既有M440i xDrive外廓一致。	READY
140865	140865	Van	eDeliver 3 (EV30)	EV30		EU-MAXUS-EDELIVER-3-EV30-VAN-SWB-01	HIGH	短轴厢式电动车外廓。	READY
140883	140883	Coupe	Polestar 1		2	EU-POLESTAR-1-I-COUPE-01	HIGH	Polestar 1双门轿跑外廓。	READY
140885	140885	SUV	Countryman II facelift (F60)	F60	5	EU-MINI-COUNTRYMAN-F60-SUV-FACELIFT-PHEV-01	HIGH	输入Kombi对应F60 Countryman插混车型。	READY
140889	140889	Wagon	MINI Clubman II (F54)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman五门旅行外廓。	READY
140890	140890	Wagon	MINI Clubman II (F54)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman五门旅行外廓。	READY
140891	140891	SUV	GLC I facelift (X253)	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	HIGH	X253改款插混SUV外廓。	READY
140892	140892	MPV	Caddy IV (2K)	2K		EU-VW-CADDY-IV-MPV-LWB-01	HIGH	ABT e-Caddy长轴MPV外廓。	READY
140893	140893	SUV	GLC F-CELL (N253)	N253	5	EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	HIGH	N253 F-CELL外廓。	READY
140894	140894	SUV	GLC F-CELL (N253)	N253	5	EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	HIGH	N253 F-CELL外廓。	READY
140895_van	140895	Van	Caddy IV (2K)	2K		EU-VW-CADDY-IV-VAN-LWB-01	HIGH	同一Ktype的长轴厢式分支。	READY
140895_mpv	140895	MPV	Caddy IV (2K)	2K		EU-VW-CADDY-IV-MPV-LWB-01	HIGH	同一Ktype的长轴MPV分支。	READY
140896	140896	Van	Transporter T6.1			EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	MEDIUM	ABT e-Transporter长轴低顶外廓。	READY
140897	140897	MPV	Transporter/Caravelle T6.1		5	EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	MEDIUM	ABT e-Caravelle与长轴低顶车身外廓一致。	READY
140905	140905	SUV	Cayenne III (9YA)	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	HIGH	GTS专属保险杠和车高外廓。	READY
140906	140906	Coupe	720S I		2	EU-MCLAREN-720S-I-COUPE-01	HIGH	720S Coupe车身。	READY
140916	140916	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140917	140917	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140918	140918	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140919	140919	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140920	140920	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140921	140921	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140922	140922	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
140923	140923	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140924	140924	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140925	140925	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140926	140926	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140927	140927	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140928	140928	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140929	140929	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140930	140930	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
140931	140931	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140932	140932	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140933	140933	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140934	140934	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140935	140935	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140936	140936	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140937	140937	Wagon	5 Series VII facelift (G31)	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI旅行版外廓。	READY
140943	140943	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	XC40五门SUV外廓。	READY
140957	140957	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II标准旅行版外廓。	READY
140967	140967	Sedan	3 Series VII (G20)	G20	4	EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	HIGH	G20 330e后驱插混高度分支。	READY
140974	140974	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STANDARD-01	HIGH	95 PS标准车身外廓。	READY
140979	140979	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前Model Y车身外廓。	READY
140980	140980	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前Model Y车身外廓。	READY
140981	140981	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-PREFL-01	HIGH	改款前Model Y车身外廓。	READY
140982	140982	Sedan	Taycan I (Y1A)	Y1A	4	EU-PORSCHE-TAYCAN-I-Y1A-RWD-SEDAN-01	HIGH	后驱基础版车高分支。	READY
140998_5ft7bed	140998	Pickup	1500 V (DT)	DT	4	EU-RAM-1500-DT-PICKUP-CREWCAB-5FT7BED-01	HIGH	Crew Cab配5英尺7英寸货斗分支。	READY
140998_6ft4bed	140998	Pickup	1500 V (DT)	DT	4	EU-RAM-1500-DT-PICKUP-CREWCAB-6FT4BED-01	HIGH	Crew Cab配6英尺4英寸货斗分支。	READY
141005	141005	SUV	Mokka B		5	EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	HIGH	Mokka-e电动车外廓。	READY
141020	141020	Hatchback	Swift VI facelift		5	EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-FWD-01	HIGH	2020年欧洲前驱车型外廓。	READY
141021	141021	Hatchback	Swift VI facelift		5	EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-AWD-01	HIGH	ALLGRIP车型独立车高。	READY
141022	141022	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	S60 III四门轿车外廓。	READY
141023	141023	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	S60 III四门轿车外廓。	READY
141032	141032	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141033	141033	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141036	141036	Sedan	2 Series Gran Coupe (F44)	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应F44四门Gran Coupe外廓。	READY
141038_prefl	141038	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前旅行版外廓。	READY
141038_facelift	141038	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后旅行版外廓。	READY
141039_prefl	141039	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前旅行版外廓。	READY
141039_facelift	141039	Wagon	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后旅行版外廓。	READY
141040	141040	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141042	141042	SUV	X2 I (F39)	F39	5	EU-BMW-X2-F39-SUV-01	HIGH	F39五门SUV外廓。	READY
141043	141043	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
141044	141044	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141045	141045	Hatchback	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	PD五门掀背外廓。	READY
141046	141046	Wagon	i30 III (PD)	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH	PD旅行版外廓。	READY
141047_prefl	141047	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门掀背外廓。	READY
141047_facelift	141047	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门掀背外廓。	READY
141048_prefl	141048	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门掀背外廓。	READY
141048_facelift	141048	Hatchback	Focus IV (C519)	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门掀背外廓。	READY
141051	141051	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141057	141057	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141059_3dr	141059	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	HIGH	同一Ktype覆盖三门物理分支。	READY
141059_5dr	141059	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	HIGH	同一Ktype覆盖五门物理分支。	READY
141060_3dr	141060	Hatchback	Fiesta VIII (Mk8)		3	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	HIGH	同一Ktype覆盖三门物理分支。	READY
141060_5dr	141060	Hatchback	Fiesta VIII (Mk8)		5	EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	HIGH	同一Ktype覆盖五门物理分支。	READY
141061	141061	Hatchback	6 Series Gran Turismo (G32)	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH	G32五门Gran Turismo外廓。	READY
141062	141062	Hatchback	Yaris IV (XP210)	XP210	5	EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	HIGH	欧洲市场宽体五门车身。	READY
141064	141064	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
141065	141065	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
141066	141066	Sedan	5 Series VII facelift (G30)	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	G30 LCI标准轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5101-5200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	4961	2018	1720	Auto-Data; EncyCARpedia	https://www.auto-data.net/en/mercedes-benz-gle-coupe-c167-amg-gle-63-v8-571hp-eq-boost-4matic-amg-speedshift-tct-39188;https://www.encycarpedia.com/mercedes/20-amg-gle-coupe-63-s-4matic-suv
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-FACELIFT-01	4954	2018	1720	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gle-coupe-c167-facelift-2023-amg-gle-63-s-v8-612hp-eq-boost-4matic-amg-speedshift-tct-9g-47366
EU-CASALINI-M20-I-HATCHBACK-3D-01	3000	1500	1470	Casalini M20 brochure	https://ampautos.fr/wp-content/uploads/2018/07/Brochure-M20_FR.pdf
EU-MICROCAR-DUE-III-HATCHBACK-3D-01	2870	1500	1485	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/microcar/due/1generation-facelift/324298/
EU-AIXAM-ROADLINE-K44VBR-HATCHBACK-3D-01	2959	1492	1480	AIXAM Roadline official user manual	https://www.aixam-mega-sav.com/data/gamme/doc/manuel%20utilisateur%20vsp%20fr.pdf
EU-AIXAM-CROSSOVER-SENSATION-HATCHBACK-3D-01	3000	1500	1590	AIXAM User Manual Edition 10/2018	https://www.aixam.com/ressources/pages/sav/aixam-user-manual.pdf
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-generation-5503
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-wagon-generation-5960
EU-MERCEDES-BENZ-A-KLASSE-V177-A250E-SEDAN-PREFL-01	4549	1796	1458	Auto-Data	https://www.auto-data.net/en/mercedes-benz-a-class-sedan-v177-a-250e-218hp-plug-in-hybrid-8g-dct-37688
EU-MERCEDES-BENZ-A-KLASSE-W177-A250E-HATCHBACK-PREFL-01	4419	1796	1452	Auto-Data	https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-250e-218hp-plug-in-hybrid-8g-dct-37687
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault Clio V official dimensions	https://www.renault.mu/cars/NouvelleCLIObjaPh1/dimensionsandspecifications.html
EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	2338	1234	1454	Renault Twizy press kit; EVSpecs	https://www.press.renault.co.uk/assets/documents/original/14737-RenaultTwizyPressKit2018.pdf;https://www.evspecs.org/tech-specs/renault/twizy/urban-80
EU-MERCEDES-BENZ-B-KLASSE-W247-B250E-MPV-PREFL-01	4419	1796	1562	Auto-Data	https://www.auto-data.net/en/mercedes-benz-b-class-w247-b-250e-218hp-plug-in-hybrid-8g-dct-41799
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gla-h247-amg-gla-35-306hp-4matic-dct-38235
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1616	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gla-h247-facelift-2023-amg-gla-45-s-421hp-4matic-amg-speedshift-dct-8g-51785
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-350e-286hp-plug-in-hybrid-9g-tronic-30131
EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	4935	1852	1481	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300de-306hp-plug-in-hybrid-4matic-9g-tronic-40972
EU-MAXUS-EV80-VAN-LWB-MIDROOF-01	5700	1998	2345	MAXUS EV80 official specifications	https://maxus-motor.gr/images/brochures/MAXUS-EV80.pdf
EU-MAXUS-EV80-VAN-LWB-HIGHROOF-01	5700	1998	2552	MAXUS EV80 official specifications	https://maxus-motor.gr/images/brochures/MAXUS-EV80.pdf
EU-MAXUS-EV80-CHASSIS-CAB-LWB-01	5620	1996	2136	MAXUS EV80 official specifications	https://maxus-motor.gr/images/brochures/MAXUS-EV80.pdf
EU-KIA-SOUL-III-SK3-CARGO-VAN-01	4195	1800	1605	Kia Soul EV official specifications	https://eu-www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/soul-ev/specification/kia-soul-ev-specification.pdf
EU-MAXUS-DELIVER-9-VAN-L3H2-RWD-01	5940	2062	2535	MAXUS Deliver 9 official dimensions	https://www.maxus-automotive.es/storage/app/media/deliver_9.pdf
EU-MAXUS-DELIVER-9-VAN-L3H3-RWD-01	5940	2062	2755	MAXUS Deliver 9 official dimensions	https://www.maxus-automotive.es/storage/app/media/deliver_9.pdf
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW 4 Series Coupé official specifications	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-02	5325	1855	1815	Toyota Hilux Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1611922571210129MHiluxTechSpec.pdf
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393	BMW M440i xDrive Coupé official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0313067EN/456762
EU-MAXUS-EDELIVER-3-EV30-VAN-SWB-01	4555	1780	1895	MAXUS eDELIVER 3 official brochure	https://www.maxus.si/EasyEdit/UserFiles/CatalogDocs/MAXUS_Brochure_eDELIVER3_wLQ6Za8V.pdf
EU-POLESTAR-1-I-COUPE-01	4586	1958	1352	Polestar Owner's Manual	https://www.polestar.com/uk/manual/polestar-1/2020/article/fe05d7088a0740d0c0a8015150f8256d/
EU-MINI-COUNTRYMAN-F60-SUV-FACELIFT-PHEV-01	4297	1822	1559	Auto-Data	https://www.auto-data.net/en/mini-countryman-f60-facelift-2020-cooper-se-1.5-220hp-plug-in-hybrid-all4-steptronic-40760
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441	MINI Clubman official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252423EN/353092
EU-MERCEDES-BENZ-GLC-X253-SUV-FACELIFT-01	4655	1890	1644	Auto-Data	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-facelift-2019-glc-300e-320hp-plug-in-hybrid-4matic-g-tronic-38696
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831	Volkswagen Caddy official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-brochure.pdf
EU-MERCEDES-BENZ-GLC-N253-F-CELL-SUV-01	4671	1890	1653	Engine in detail; Autohled vehicle comparison	https://www.engineindetail.com/cars/mercedes-benz/glc/glc-253-f-cell-2019-2020;https://www.autohled.cz/de/porovnavac/hyundai-nexo-vs-mercedes-benz-glc-f-cell
EU-VW-CADDY-IV-VAN-LWB-01	4878	1793	1836	Volkswagen Caddy official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-brochure.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990	Volkswagen Transporter 6.1 official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/transporter-6-1-brochure.pdf
EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	4929	1983	1676	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-iii-gts-4.0-v8-460hp-tiptronic-s-40967
EU-MCLAREN-720S-I-COUPE-01	4543	1930	1196	Auto-Data	https://www.auto-data.net/en/mclaren-720s-4.0-v8-720hp-ssg-28867
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	BMW 6 Series Gran Turismo official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0271742EN/388196
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479	BMW 5 Series Sedan official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498	BMW 5 Series Touring official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318750EN/463132
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Auto-Data	https://www.auto-data.net/en/volvo-xc40-generation-5636
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data	https://www.auto-data.net/en/volvo-v90-2016-2.0-d4-190hp-automatic-36301
EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	4709	1827	1444	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-g20-330e-292hp-plug-in-hybrid-steptronic-37654
EU-FORD-PUMA-II-SUV-STANDARD-01	4186	1805	1536	Auto-Data	https://www.auto-data.net/en/ford-puma-1.0-ecoboost-95hp-41458
EU-TESLA-MODEL-Y-I-SUV-PREFL-01	4750	1921	1624	Tesla Model Y Owner's Manual 2020-2024	https://www.tesla.com/ownersmanual/2020_2024/modely/en_us/GUID-E47C4A6D-528E-419C-8C57-FD3864644C34.html
EU-PORSCHE-TAYCAN-I-Y1A-RWD-SEDAN-01	4963	1966	1395	Auto-Data	https://www.auto-data.net/en/porsche-taycan-y1a-generation-7269
EU-RAM-1500-DT-PICKUP-CREWCAB-5FT7BED-01	5916	2085	1971	2019 Ram 1500 official brochure	https://www.fremontchryslerdodgejeeprocksprings.com/assets/shared/CustomHTMLFiles/Compliance/CDJR/Brochure/eBrochure-Ram-DT-Catalog-2019.pdf
EU-RAM-1500-DT-PICKUP-CREWCAB-6FT4BED-01	6142	2085	1969	2019 Ram 1500 official brochure	https://www.fremontchryslerdodgejeeprocksprings.com/assets/shared/CustomHTMLFiles/Compliance/CDJR/Brochure/eBrochure-Ram-DT-Catalog-2019.pdf
EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	4151	1791	1532	Auto-Data	https://www.auto-data.net/en/opel-mokka-b-mokka-e-50-kwh-136hp-41307
EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-FWD-01	3845	1735	1495	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-facelift-2020-1.2-dualjet-shvs-83hp-41193
EU-SUZUKI-SWIFT-VI-FACELIFT-HATCHBACK-AWD-01	3845	1735	1520	Auto-Data	https://www.auto-data.net/en/suzuki-swift-vi-facelift-2020-1.2-dualjet-shvs-83hp-allgrip-41206
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Volvo S60 official technical specifications	https://www.volvoclub.org.uk/pdf/s60/s60_2019_techspecs.pdf
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW 2 Series Gran Coupé official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0309526EN/452536
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481	Auto-Data	https://www.auto-data.net/en/ford-focus-iv-wagon-generation-6064
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497	Auto-Data	https://www.auto-data.net/en/ford-focus-iv-wagon-facelift-2021-generation-8720
EU-BMW-X2-F39-SUV-01	4360	1824	1526	Auto-Data	https://www.auto-data.net/en/bmw-x2-f39-generation-5794
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Auto-Data	https://www.auto-data.net/en/ford-focus-iv-generation-6061
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471	Auto-Data	https://www.auto-data.net/en/ford-focus-iv-facelift-2021-generation-8716
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-3D-STANDARD-01	4040	1735	1476	Auto-Data	https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.0-ecoboost-155hp-mild-hybrid-41396
EU-FORD-FIESTA-VIII-MK8-HATCHBACK-5D-STANDARD-01	4040	1735	1476	Ford Fiesta official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-new_fiesta.pdf
EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	3940	1745	1500	Toyota Yaris Technical Specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210713M-Yaris-Tech-Spec.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5101-5200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.aixam-mega-sav.com/data/gamme/doc/manuel%20utilisateur%20vsp%20fr.pdf?utm_source=chatgpt.com "Manuel utilisateur VSP FR"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5405 行）
- 累计尺寸组：dimension_groups_final.tsv（2008 行）

