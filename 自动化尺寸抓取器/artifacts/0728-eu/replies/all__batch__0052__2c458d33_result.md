# 任务：all 第 5101-5200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0052__2c458d33


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
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	4740	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	4390	1832	2100
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	4406	1832	1899
EU-FIAT-DOBLO-II-263-MPV-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-FACELIFT-01	4406	1832	2125
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-II-CARGO-MAXI-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-II-CARGO-MAXI-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-II-CARGO-SWB-FACELIFT-01	4406	1832	1845
EU-FIAT-DOBLO-II-CARGO-SWB-PREFL-01	4390	1832	1845
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424
EU-FORD-MONDEO-IV-BA7-SEDAN-01	4844	1886	1500
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
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380
EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	4675	1780	1390
EU-HONDA-ACCORD-V-CE-WAGON-5D-01	4770	1780	1425
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410
EU-PEUGEOT-ION-HATCHBACK-01	3475	1475	1608
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424
EU-SKODA-FELICIA-I-HATCHBACK-01	3883	1635	1415
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420
EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	4350	1690	1435
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
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-VW-CADDY-III-2K-VAN-01	4405	1794	1833
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Megane i	1.6 E	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1996	Mar 1999	2024-03-01	5252
Renault	Megane i	2.0 I	Schrägheck	Frontantrieb	Benzin	84	114	Jan 1996	Aug 2003	2024-03-01	5253
Renault	Megane i	1.9 D ECO	Schrägheck	Frontantrieb	Diesel	47	64	Jan 1996	Aug 2003	2024-03-01	5254
Seat	Toledo	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Aug 1995	Mar 1999	2024-03-01	5255
Skoda	Felicia i	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1995	Mar 1998	2024-03-01	5256
Skoda	Felicia i	1.3	Kombi	Frontantrieb	Benzin	40	54	Aug 1995	Mar 1998	2024-03-01	5257
Skoda	Felicia i	1.3	Kombi	Frontantrieb	Benzin	50	68	Aug 1995	Mar 1998	2024-03-01	5258
Skoda	Felicia i	1.6	Kombi	Frontantrieb	Benzin	55	75	Aug 1995	Mar 1998	2024-03-01	5259
Fiat	Doblo	1.3 JTD 16V Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	62	84	Aug 2006	-	2024-03-01	5260
Suzuki	X-90	1.6 I 16V 4X4	Geländewagen offen	Allrad	Benzin	71	97	Sep 1995	Dec 1997	2024-03-01	5261
Toyota	Corolla	1.3 XLI	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1995	Apr 1997	2024-03-01	5262
Fiat	Doblo	1.9 JTD Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	Dec 2006	-	2024-03-01	5263
Toyota	Corolla	1.3 XLI	Kombi	Frontantrieb	Benzin	55	75	Sep 1995	Apr 1997	2024-03-01	5264
Renault	Modus / grand	1.5 DCI 75	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2010	Dec 2013	2025-12-01	5265
Toyota	Corolla	1.6 SI	Kombi	Frontantrieb	Benzin	84	114	Jul 1992	Apr 1997	2024-03-01	5266
Renault	Modus / grand	1.5 DCI 90	Schrägheck	Frontantrieb	Diesel	65	88	Oct 2010	Dec 2013	2025-12-01	5267
Toyota	Corolla	1.8 16V 4WD	Kombi	Allrad	Benzin	81	110	Sep 1995	Apr 1997	2024-03-01	5268
Toyota	Corolla	1.3 XLI	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1995	Apr 1997	2024-03-01	5269
Toyota	Corolla	1.6 SI	Stufenheck	Frontantrieb	Benzin	84	114	Sep 1995	Apr 1997	2024-03-01	5270
Toyota	Corolla	2.0 D	Stufenheck	Frontantrieb	Diesel	53	72	Jul 1992	Apr 1997	2024-03-01	5271
VW	Golf iii	2.0 Syncro	Schrägheck	Allrad	Benzin	85	115	Aug 1995	Aug 1997	2024-03-01	5272
VW	Golf iii	1.9 TDI Syncro	Schrägheck	Allrad	Diesel	66	90	Aug 1995	Dec 1997	2025-02-03	5273
VW	Golf iii variant	2.0 Syncro	Kombi	Allrad	Benzin	85	115	Aug 1995	Apr 1999	2024-03-01	5274
VW	Passat b3/b4	1.9 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Mar 1996	Aug 1996	2024-03-01	5275
VW	Passat b3/b4 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	81	110	Mar 1996	May 1997	2024-03-01	5276
VW	Polo	55 1.4	Schrägheck	Frontantrieb	Benzin	40	55	Aug 1995	Oct 1999	2024-03-01	5277
VW	Polo	60 1.4	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1995	Oct 1999	2024-03-01	5278
VW	Polo	100 1.4 16V	Schrägheck	Frontantrieb	Benzin	74	100	Apr 1996	Oct 1999	2024-03-01	5279
VW	Polo	75 1.6	Stufenheck	Frontantrieb	Benzin	55	75	Nov 1995	Sep 2001	2024-03-01	5280
VW	Transporter / multivan t4	2.5 TDI	Bus	Frontantrieb	Diesel	75	102	Sep 1995	Apr 2003	2025-11-01	5281
Dodge	Journey	2.7	Großraumlimousine	Frontantrieb	Benzin	136	185	Jan 2009	-	2024-03-01	5282
Renault	Twingo	1.5 DCI 75	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2010	Aug 2014	2026-05-01	5283
Renault	Twingo	1.5 DCI 90	Schrägheck	Frontantrieb	Diesel	63	86	Oct 2010	Sep 2014	2026-05-01	5284
Ford	Transit	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Jan 1995	Mar 2000	2024-03-01	5285
Ford	Transit	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Jul 1994	Mar 2000	2024-03-01	5286
Ford	Transit	2	Bus	Heckantrieb	Benzin	84	114	Aug 1994	Mar 2000	2024-03-01	5287
Renault	Megane iii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Oct 2010	Aug 2015	2024-03-01	5288
Renault	Megane iii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	110	150	Oct 2010	Aug 2015	2024-03-01	5289
Renault	Megane cc	2.0 TCE	Cabriolet	Frontantrieb	Benzin	132	180	Jun 2010	Aug 2015	2024-03-01	5290
Peugeot	5008	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	82	112	Aug 2010	Mar 2017	2024-03-01	5291
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	56	76	Jun 1994	Mar 2000	2024-03-01	5292
Ford	Transit	2.5 TD	Kasten	Heckantrieb	Diesel	63	85	Jun 1994	Mar 2000	2024-03-01	5293
Ford	Transit	2.5 TDI	Kasten	Heckantrieb	Diesel	74	101	Jun 1994	Mar 2000	2024-03-01	5294
Ford	Escort vi	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1995	Oct 1998	2024-03-01	5296
Peugeot	807	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	120	163	Jun 2009	-	2024-03-01	5298
VW	Polo	60 1.4	Stufenheck	Frontantrieb	Benzin	44	60	Dec 1995	Sep 2001	2024-03-01	5299
VW	Polo	64 1.9 SDI	Stufenheck	Frontantrieb	Diesel	47	64	Dec 1995	Aug 1999	2024-03-01	5300
VW	Polo	100 1.6	Stufenheck	Frontantrieb	Benzin	74	100	Dec 1995	Sep 2001	2024-03-01	5301
VW	Caddy ii	60 1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Nov 1995	Jan 2004	2024-03-01	5302
VW	Caddy ii	1.9 SDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	47	64	Nov 1995	Jan 2004	2024-03-01	5303
VW	Caddy ii	75 1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Nov 1995	Sep 2000	2024-03-01	5304
Audi	A4 b5 avant	1.6	Kombi	Frontantrieb	Benzin	74	100	Nov 1994	Sep 2001	2024-03-01	5305
Audi	A4 b5 avant	1.8	Kombi	Frontantrieb	Benzin	92	125	Feb 1996	Sep 2001	2024-03-01	5306
Audi	A4 b5 avant	1.8 T	Kombi	Frontantrieb	Benzin	110	150	Mar 1996	Sep 2001	2024-03-01	5307
Audi	A4 b5 avant	2.6	Kombi	Frontantrieb	Benzin	110	150	Feb 1996	Sep 2001	2024-03-01	5308
Audi	A4 b5 avant	2.8	Kombi	Frontantrieb	Benzin	128	174	Mar 1996	Sep 1996	2024-05-01	5309
Audi	A4 b5 avant	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Feb 1996	Sep 2001	2024-03-01	5310
Audi	A4 b5 avant	1.9 TDI	Kombi	Frontantrieb	Diesel	81	110	Feb 1996	Sep 2001	2024-03-01	5311
Peugeot	Ion	Electric	Schrägheck	Heckantrieb	Elektro	35	48	Nov 2010	-	2024-03-01	5312
Audi	A4 b5 avant	1.8 Quattro	Kombi	Allrad	Benzin	92	125	Jan 1996	Sep 2001	2024-03-01	5313
Audi	A4 b5 avant	1.8 T Quattro	Kombi	Allrad	Benzin	110	150	Jan 1996	Sep 2001	2024-03-01	5314
Audi	A4 b5 avant	2.6 Quattro	Kombi	Allrad	Benzin	110	150	Jan 1996	Sep 2001	2024-03-01	5315
Audi	A4 b5 avant	2.8 Quattro	Kombi	Allrad	Benzin	128	174	Jan 1996	Sep 1996	2024-05-01	5316
Ford	Mondeo i turnier	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Nov 1995	Aug 1996	2024-03-01	5317
Audi	A6 c4	1.8	Stufenheck	Frontantrieb	Benzin	92	125	Dec 1995	Oct 1997	2024-03-01	5318
Audi	A6 c4 avant	1.8	Kombi	Frontantrieb	Benzin	92	125	Dec 1995	Dec 1997	2024-03-01	5319
Audi	A6 c4	1.8 Quattro	Stufenheck	Allrad	Benzin	92	125	Dec 1995	Oct 1997	2024-03-01	5320
Audi	A6 c4 avant	1.8 Quattro	Kombi	Allrad	Benzin	92	125	Dec 1995	Dec 1997	2024-03-01	5321
Audi	A6 c4	2.8	Stufenheck	Frontantrieb	Benzin	142	193	Dec 1995	Oct 1997	2024-03-01	5322
Audi	A6 c4 avant	2.8	Kombi	Frontantrieb	Benzin	142	193	Dec 1995	Dec 1997	2024-03-01	5323
Audi	A6 c4	2.8 Quattro	Stufenheck	Allrad	Benzin	142	193	Dec 1995	Oct 1997	2024-03-01	5324
Audi	A6 c4 avant	2.8 Quattro	Kombi	Allrad	Benzin	142	193	Dec 1995	Dec 1997	2024-03-01	5325
Ford	Escort vi	1.8 TD	Cabriolet	Frontantrieb	Diesel	66	90	Sep 1995	Aug 1998	2024-03-01	5326
Peugeot	406	1.9 TD	Stufenheck	Frontantrieb	Diesel	66	90	Jan 1996	May 2004	2024-03-01	5327
Rover	200 ii	214 I	Schrägheck	Frontantrieb	Benzin	55	75	Nov 1995	Mar 2000	2024-03-01	5328
Rover	200 ii	214 SI	Schrägheck	Frontantrieb	Benzin	76	103	Nov 1995	Mar 2000	2024-03-01	5329
Rover	200 ii	216 SI	Schrägheck	Frontantrieb	Benzin	82	112	Nov 1995	Jun 1999	2024-03-01	5330
Rover	200 ii	218 K VI	Schrägheck	Frontantrieb	Benzin	107	146	Nov 1995	Mar 2000	2024-03-01	5331
Rover	200 ii	220 D/sd	Schrägheck	Frontantrieb	Diesel	63	86	Nov 1995	Mar 2000	2024-03-01	5332
Rover	200 ii	220 SDI	Schrägheck	Frontantrieb	Diesel	77	105	Nov 1995	Mar 2000	2024-03-01	5333
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	120	163	Jul 2011	Jun 2019	2024-03-01	5334
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	85	116	Mar 2012	Feb 2015	2024-03-01	5335
Land Rover	Defender station wagon	2.5 TDI 4X4	Geländewagen geschlossen	Allrad	Diesel	83	113	Aug 1990	Dec 1998	2024-03-01	5337
Land Rover	Defender cabrio	2.5 TDI 4X4	Geländewagen offen	Allrad	Diesel	83	113	Aug 1990	Nov 1998	2024-03-01	5338
Mercedes-benz	Vito	108 D 2.3	Bus	Frontantrieb	Diesel	58	79	Feb 1996	Jul 2003	2024-03-01	5339
Mercedes-benz	Vito	110 TD 2.3	Bus	Frontantrieb	Diesel	72	98	Feb 1996	Jul 2003	2024-03-01	5340
Mercedes-benz	Vito	113 2.0	Bus	Frontantrieb	Benzin	95	129	Feb 1996	Jul 2003	2024-03-01	5341
Ford	Escort vi	1.8 16V Xr3i	Cabriolet	Frontantrieb	Benzin	85	115	Oct 1995	Aug 1998	2024-03-01	5342
Ford	Mondeo i	1.8 TD	Schrägheck	Frontantrieb	Diesel	66	90	Oct 1995	Aug 1996	2024-03-01	5343
Ford	Mondeo i	1.8 TD	Stufenheck	Frontantrieb	Diesel	66	90	Oct 1995	Aug 1996	2024-03-01	5344
Renault	Megane i	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1996	Mar 1999	2024-03-01	5345
Renault	Megane i	1.9 DT	Schrägheck	Frontantrieb	Diesel	66	90	Jan 1996	Aug 2003	2024-03-01	5346
Renault	Megane i coach	1.6 E	Coupe	Frontantrieb	Benzin	66	90	Mar 1996	Mar 1999	2024-03-01	5347
Renault	Megane i coach	2.0 I	Coupe	Frontantrieb	Benzin	84	114	Mar 1996	Aug 2003	2024-03-01	5348
Renault	Megane i coach	2.0 16V	Coupe	Frontantrieb	Benzin	108	147	Mar 1996	Nov 1999	2024-03-01	5349
Ferrari	California	4.3	Cabriolet	Heckantrieb	Benzin	360	490	Sep 2008	-	2024-03-01	5350
Subaru	Impreza	2.0 AWD	Coupe	Allrad	Benzin	85	115	Dec 1995	Dec 2000	2024-03-01	5352
Subaru	Impreza	2.0 I AWD	Stufenheck	Allrad	Benzin	85	115	Oct 1995	Dec 2000	2024-03-01	5353
Peugeot	406	2.1 TD 12V	Stufenheck	Frontantrieb	Diesel	80	109	Jan 1996	May 2004	2024-03-01	5354
Honda	Accord v	1.8 I	Stufenheck	Frontantrieb	Benzin	85	116	Feb 1996	Oct 1998	2025-06-01	5355


--- Round 1 / 首次发送 ---
## 更新点

* 完成 49 个 Ktype 的物理分支闭合，共形成 59 条 `READY` 映射。
* 直接复用 26 个已有尺寸组；本轮首次创建 6 个尺寸组。
* 新建组包括 Felicia I Combi、Suzuki X-90、Modus、Grand Modus、Passat B4 Sedan 和 Passat B4 Variant。Felicia Combi 为 4205×1635×1420 mm，欧洲版 X-90 为 3710×1695×1555 mm；Modus/Grand Modus 按短轴和长轴分别建组；Passat B4 三厢与旅行版分别使用 4605×1720×1430 mm 和 4595×1720×1445 mm。([汽车目录][1])
* Renault Megane I 与 Peugeot 406 的跨改款 Ktype 已拆分为 `prefl`、`facelift` 派生行。
* Renault Modus / Grand Modus 的 75 PS、90 PS 版本均确认同时存在短轴 Modus 与长轴 Grand Modus，因此分别输出两个物理分支。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：49
* READY 映射：59
* 尚未闭合 Ktype：51
* 当前已引用尺寸组：32
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5252	5252	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
5253_prefl	5253	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5253_facelift	5253	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5254_prefl	5254	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5254_facelift	5254	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5255	5255	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	Toledo I五门掀背外廓。	READY
5256	5256	Hatchback	Felicia I	791	5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH	Felicia I五门掀背外廓。	READY
5257	5257	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5258	5258	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5259	5259	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5261	5261	SUV	X-90	EL	2	EU-SUZUKI-X-90-EL-SUV-2D-01	HIGH	两门T形顶SUV外廓。	READY
5264	5264	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	E100五门旅行车外廓。	READY
5265_modus	5265	MPV	Modus I	J77	5	EU-RENAULT-MODUS-I-J77-MPV-01	HIGH	车型字段同时覆盖短轴Modus。	READY
5265_grand	5265	MPV	Grand Modus I	R77	5	EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	HIGH	车型字段同时覆盖长轴Grand Modus。	READY
5266	5266	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	E100五门旅行车外廓。	READY
5267_modus	5267	MPV	Modus I	J77	5	EU-RENAULT-MODUS-I-J77-MPV-01	HIGH	车型字段同时覆盖短轴Modus。	READY
5267_grand	5267	MPV	Grand Modus I	R77	5	EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	HIGH	车型字段同时覆盖长轴Grand Modus。	READY
5268	5268	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	MEDIUM	E100四驱五门旅行车采用相同外廓组。	READY
5269	5269	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5270	5270	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5271	5271	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5272_3dr	5272	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5272_5dr	5272	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5273_3dr	5273	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5273_5dr	5273	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5274	5274	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH	Golf III Variant五门旅行车外廓。	READY
5275	5275	Sedan	Passat B4	3A2	4	EU-VW-PASSAT-B4-3A2-SEDAN-01	HIGH	生产日期对应B4四门三厢。	READY
5276	5276	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-3A5-WAGON-01	HIGH	生产日期对应B4五门旅行版。	READY
5277	5277	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5278	5278	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5279	5279	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5288	5288	Hatchback	Megane III	BZ0	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH	Megane III五门掀背外廓。	READY
5289	5289	Wagon	Megane III Grandtour	KZ0	5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Grandtour五门旅行车外廓。	READY
5290	5290	Convertible	Megane III CC	EZ0	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
5296_3dr	5296	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5296_5dr	5296	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5312	5312	Hatchback	iOn		5	EU-PEUGEOT-ION-HATCHBACK-01	HIGH	iOn五门电动掀背外廓。	READY
5317	5317	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH	Mondeo I五门旅行车外廓。	READY
5318	5318	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	A6 C4普通车身四门三厢。	READY
5319	5319	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	A6 C4普通车身五门Avant。	READY
5320	5320	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	Quattro未改变普通车身外廓。	READY
5321	5321	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	Quattro未改变普通Avant外廓。	READY
5322	5322	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	A6 C4普通车身四门三厢。	READY
5323	5323	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	A6 C4普通车身五门Avant。	READY
5324	5324	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	Quattro未改变普通车身外廓。	READY
5325	5325	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	Quattro未改变普通Avant外廓。	READY
5326	5326	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Escort VI改款双门敞篷外廓。	READY
5327_prefl	5327	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-PREFL-01	HIGH	Ktype生产期覆盖改款前三厢外廓。	READY
5327_facelift	5327	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	Ktype生产期覆盖改款后三厢外廓。	READY
5342	5342	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Escort VI改款双门敞篷外廓。	READY
5343	5343	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH	Mondeo I五门掀背外廓。	READY
5344	5344	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH	Mondeo I四门三厢外廓。	READY
5345	5345	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
5346_prefl	5346	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5346_facelift	5346	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5353	5353	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门三厢外廓。	READY
5354_prefl	5354	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-PREFL-01	HIGH	Ktype生产期覆盖改款前三厢外廓。	READY
5354_facelift	5354	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	Ktype生产期覆盖改款后三厢外廓。	READY
5355	5355	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门三厢外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FELICIA-I-795-WAGON-01	4205	1635	1420	Automobile-Catalog 1995 Skoda Felicia Estate 1.3 (54)	https://www.automobile-catalog.com/car/1995/3133670/skoda_felicia_estate_1_3_54.html
EU-SUZUKI-X-90-EL-SUV-2D-01	3710	1695	1555	Automobile-Catalog 1996 Suzuki X-90 4WD	https://www.automobile-catalog.com/car/1996/3351515/suzuki_x-90_4wd_automatic.html
EU-RENAULT-MODUS-I-J77-MPV-01	3874	1709	1589	Renault Modus and Grand Modus official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Renault-Modus-2008-UK.pdf
EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	4034	1709	1589	Renault Modus and Grand Modus official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Renault-Modus-2008-UK.pdf
EU-VW-PASSAT-B4-3A2-SEDAN-01	4605	1720	1430	Auto-Data Volkswagen Passat B4 generation	https://www.auto-data.net/en/volkswagen-passat-b4-generation-8293
EU-VW-PASSAT-B4-3A5-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B4 1.9 TDI 110	https://www.auto-data.net/en/volkswagen-passat-variant-b4-1.9-tdi-110hp-8985
```

## 下一步优先处理

1. 处理 Fiat Doblo 5260、5263，区分第一代改款 Cargo、Passenger/MPV 以及标准轴距、Maxi 分支。
2. 处理 Ford Transit 5285–5287、5292–5294，按 Bus/Kasten、SWB/LWB、低顶/中顶/高顶关联现有 VE6 尺寸组。
3. 处理 VW Transporter T4 5281，确认 Multivan/Transporter Bus 的 SWB、LWB 与车顶分支。
4. 闭合 Audi A4 B5 Avant 5305–5316 的改款前后外廓。
5. 继续处理 Polo Classic、Caddy II、Twingo II、Peugeot 5008/807、Rover 200 R3、BMW F20/F21、Defender、Vito W638 等剩余分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/3133670/skoda_felicia_estate_1_3_54.html?utm_source=chatgpt.com "1995 Skoda Felicia Estate 1.3 (54) Specs Review (40 kW / 54 PS / 54 hp) (since mid-year 1995 for Europe )"
[2]: https://www.automobile-catalog.com/car/2010/2951825/renault_grand_modus_1_5_dci_90_eco_2.html?utm_source=chatgpt.com "2010 Renault Grand Modus 1.5 dCi 90 eco 2 Specs Review (65 kW / 88 PS / 87 hp) (since November 2010 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Polo Classic 6KV、Dodge Journey、Twingo II 改款前后及 Peugeot 807，共新增 5 个尺寸组。Twingo II 普通版改款前后长度分别为 3600 mm 和 3687 mm，车身宽度均按 1654 mm 处理。([汽车数据网][1])
* 闭合 Audi A4 B5 Avant 全部 12 个 Ktype、Mercedes-Benz Vito W638 Bus、Renault Megane I Coach 改款前后、BMW F21 三门及 Ferrari California。([汽车目录][2])
* BMW 5334 按固定的 120 kW/163 hp 五门 F20 改款前版本复用既有尺寸组；5335 按 F20 五门和 F21 三门拆分。
* 商用车多轴距/车顶、Doblo 混合车身、Caddy II、Rover 200 RF、Defender 以及 Impreza Coupe 继续保留处理。

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：78
* READY 映射：92
* PENDING Ktype：22
* 已确认并引用尺寸组：43
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5280	5280	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5282	5282	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-01	HIGH	JC五门跨界MPV外廓。	READY
5283_prefl	5283	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5283_facelift	5283	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5284_prefl	5284	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5284_facelift	5284	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5298	5298	MPV	807 I	E	5	EU-PEUGEOT-807-I-E-MPV-01	HIGH	807五门大型MPV外廓。	READY
5299	5299	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5300	5300	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5301	5301	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5305	5305	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5306	5306	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5307	5307	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5308	5308	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5309	5309	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5310	5310	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5311	5311	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5313	5313	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5314	5314	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5315	5315	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5316	5316	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5334	5334	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	MEDIUM	120 kW/163 hp五门F20改款前外廓。	READY
5335_3dr	5335	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
5335_5dr	5335	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
5339	5339	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5340	5340	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5341	5341	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5347	5347	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	DA双门改款前Coupe外廓。	READY
5348	5348	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	2.0 I版本对应改款前DA外廓。	READY
5349_prefl	5349	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5349_facelift	5349	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5350	5350	Convertible	California I	F149	2	EU-FERRARI-CALIFORNIA-I-F149-CONVERTIBLE-01	HIGH	F149双门硬顶敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414	Auto-Data Volkswagen Polo III Classic 1.4 60	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-1.4-60hp-8453
EU-DODGE-JOURNEY-I-JC-MPV-01	4888	1835	1691	Car and Driver 2009 Dodge Journey specifications	https://www.caranddriver.com/dodge/journey/specs/2009/dodge_journey_dodge-journey_2009
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	3600	1654	1470	Automobile-Catalog 2011 Renault Twingo II phase I range	https://www.automobile-catalog.com/make/renault/twingo_2gen/twingo_2_1/2011.html
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	3687	1654	1470	Automobile-Catalog 2012 Renault Twingo II facelift	https://www.automobile-catalog.com/car/2012/2956325/renault_twingo_1_2_lev_16v_75.html
EU-PEUGEOT-807-I-E-MPV-01	4727	1854	1752	Automobile-Catalog 2010 Peugeot 807 2.0 HDi	https://www.automobile-catalog.com/car/2010/2618780/peugeot_807_2_0_hdi_136.html
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417	Automobile-Catalog 1996 Audi A4 Avant B5	https://www.automobile-catalog.com/car/1996/241670/audi_a4_avant_1_9_tdi.html
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	BMW Group PressClub new three-door BMW 1 Series	https://www.press.bmwgroup.com/asia/article/detail/T0137200EN/the-new-three-door-bmw-1-series?language=en
EU-MERCEDES-BENZ-VITO-W638-BUS-01	4660	1880	1875	UltimateSpecs Mercedes-Benz Vito W638 Kombi	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/M15370/Vito-W638-Kombi
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366	Auto-Data Renault Megane I Coach DA generation	https://www.auto-data.net/en/renault-megane-i-coach-da-generation-2154
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366	Auto-Data Renault Megane I Coach Phase II 2.0i 16V	https://www.auto-data.net/en/renault-megane-i-coach-phase-ii-1999-2.0i-16v-147hp-30542
EU-FERRARI-CALIFORNIA-I-F149-CONVERTIBLE-01	4563	1902	1308	Ferrari official California specifications	https://www.ferrari.com/en-EN/auto/ferrari-california
```

## 下一步优先处理

1. Fiat Doblo 5260、5263：区分第一代改款 Cargo、Passenger、标准轴距及 Maxi。
2. VW Transporter T4 5281、Ford Transit 5285–5287/5292–5294：闭合轴距和车顶派生分支。
3. VW Caddy II 5302–5304：区分 Van 与乘用 MPV 外廓。
4. Rover 200 RF 5328–5333：确认各发动机适用的三门、五门分支。
5. Defender 5337–5338、Peugeot 5008 5291、Subaru Impreza Coupe 5352：完成剩余特殊车身边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-1.4-60hp-8453?utm_source=chatgpt.com "Volkswagen Polo III Classic (6N) 1.4 (60 Hp) /Sedan 1995"
[2]: https://www.automobile-catalog.com/car/1996/241670/audi_a4_avant_1_9_tdi.html?utm_source=chatgpt.com "1996 Audi A4 Avant 1.9 TDI Specs Review (66 kW / 90 ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Peugeot 5008、VW Caddy II、Rover 200 RF/R3、Land Rover Defender 90/110 和 Subaru Impreza I Coupe，共消除 13 个待处理 Ktype。
* Caddy II Typ 9K 与 SEAT Inca 为同一西班牙生产车身，三个 Ktype 共用一个外廓组。([汽车数据网][1])
* Rover 200 RF 的三门、五门版本共用 3973×1688×1419 mm 外廓；218 K VVC/200 Vi 仅保留三门分支。([汽车数据网][2])
* Defender Station Wagon 拆分为 90 和 110；Cabrio 对应 Defender 90 Soft Top。([汽车目录][3])
* Impreza 2.0 AWD Coupe 确认为两门 GFC 外廓 4350×1690×1410 mm。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：91
* READY 映射：111
* PENDING Ktype：9
* 已确认并引用尺寸组：50
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5291	5291	MPV	5008 I	T87	5	EU-PEUGEOT-5008-I-T87-MPV-01	HIGH	T87五门MPV外廓。	READY
5302	5302	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5303	5303	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5304	5304	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5328_3dr	5328	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5328_5dr	5328	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5329_3dr	5329	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5329_5dr	5329	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5330_3dr	5330	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5330_5dr	5330	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5331	5331	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	218 K VVC高功率版本对应三门外廓。	READY
5332_3dr	5332	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5332_5dr	5332	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5333_3dr	5333	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5333_5dr	5333	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5337_90	5337	SUV	Defender I		3	EU-LAND-ROVER-DEFENDER-I-90-STATION-WAGON-01	HIGH	Defender 90 Station Wagon外廓。	READY
5337_110	5337	SUV	Defender I		5	EU-LAND-ROVER-DEFENDER-I-110-STATION-WAGON-01	HIGH	Defender 110 Station Wagon外廓。	READY
5338	5338	Convertible	Defender I		2	EU-LAND-ROVER-DEFENDER-I-90-SOFT-TOP-01	MEDIUM	开放式车型对应Defender 90 Soft Top。	READY
5352	5352	Coupe	Impreza I	GFC	2	EU-SUBARU-IMPREZA-I-GFC-COUPE-2D-01	HIGH	GFC两门自然吸气四驱Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-5008-I-T87-MPV-01	4529	1837	1644	Automobile-Catalog 2010 Peugeot 5008 1.6 HDi 112	https://www.automobile-catalog.com/car/2010/2625995/peugeot_5008_1_6_hdi_fap_112_110.html
EU-VW-CADDY-II-9K9-VAN-01	4207	1696	1836	Volkswagen Caddy Typ 9K model history; Auto-Data SEAT Inca 9K 1.6 specification	https://en.wikipedia.org/wiki/Volkswagen_Caddy;https://www.auto-data.net/de/seat-inca-9k-1.6-i-75hp-45514
EU-ROVER-200-III-RF-HATCHBACK-01	3973	1688	1419	Auto-Data Rover 200 RF; Automobile-Catalog 1996 Rover 200 vi	https://www.auto-data.net/en/rover-200-model-1222;https://www.automobile-catalog.com/car/1996/3012155/rover_200_vi.html
EU-LAND-ROVER-DEFENDER-I-90-STATION-WAGON-01	3883	1790	1963	Automobile-Catalog 1997 Land Rover Defender 90 County 300Tdi	https://www.automobile-catalog.com/car/1997/1396640/land-rover_defender_90_county_300tdi.html
EU-LAND-ROVER-DEFENDER-I-110-STATION-WAGON-01	4599	1790	2035	Automobile-Catalog 1997 Land Rover Defender 110 Station Wagon 300Tdi	https://www.automobile-catalog.com/car/1997/1395890/land-rover_defender_110_station_wagon_300tdi.html
EU-LAND-ROVER-DEFENDER-I-90-SOFT-TOP-01	3722	1790	1965	Automobile-Catalog 1997 Land Rover Defender 90 Soft Top 300Tdi	https://www.automobile-catalog.com/car/1997/1395950/land-rover_defender_90_soft_top_300tdi.html
EU-SUBARU-IMPREZA-I-GFC-COUPE-2D-01	4350	1690	1410	Auto-Data Subaru Impreza I Coupe GFC 2.0 AWD	https://www.auto-data.net/en/subaru-impreza-i-coupe-gfc-2.0-115hp-4wd-16104
```

## 下一步优先处理

1. Fiat Doblo 5260、5263：闭合改款第一代 Cargo、Passenger，以及标准顶/高顶或长车身分支。
2. VW Transporter / Multivan T4 5281：拆分 Transporter 与 Multivan、SWB/LWB 和长短车头。
3. Ford Transit Bus 5285–5287：关联既有 VE6 改款轴距及车顶尺寸组。
4. Ford Transit Kasten 5292–5294：关联既有 VE6 改款 SWB/LWB、低顶/中顶/高顶尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/de/seat-inca-9k-1.6-i-75hp-45514?utm_source=chatgpt.com "Seat Inca (9K) 1.6 i (75 PS) | Technische Daten, Verbrauch, ..."
[2]: https://www.auto-data.net/en/rover-200-model-1222?utm_source=chatgpt.com "Rover 200 | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1997/1396640/land-rover_defender_90_county_300tdi.html?utm_source=chatgpt.com "1997 Land-Rover Defender 90 County 300tdi (man. 5)"
[4]: https://www.auto-data.net/en/subaru-impreza-i-coupe-gfc-2.0-115hp-4wd-16104?utm_source=chatgpt.com "Subaru Impreza I Coupe (GFC) 2.0 (115 Hp) 4WD"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5101-5200_ktype_dimension_mapping_final.tsv
- all_5101-5200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已消除剩余阻塞项，完成 Fiat Doblo I 改款版 Cargo/乘用、Toyota Corolla E100 Compact、VW Transporter/Multivan T4，以及 Ford Transit Bus/Kasten 的物理分支映射。
* Doblo 按短轴标准顶、短轴高顶、长轴标准顶和乘用高低顶拆分；对应手册明确列出各车身配置及三维。([mycarusermanual.com][1])
* Corolla 5262 确认覆盖三门和五门 Compact，二者均为 4095×1685×1380 mm，宽度明确不含后视镜。([汽车目录][2])
* T4 改款后短轴、长轴分别为 4789×1840×1940 mm 和 5189×1840×1940 mm，页面同时区分车身宽度与含后视镜宽度。([汽车数据网][3])
* Ford Transit 直接复用累计缓存中的 VE6 Facelift 尺寸组，未重复创建或改写尺寸事实。
* 已完成最终机械检查：表头固定、`id` 唯一、尺寸组唯一、引用全部闭合、三维和来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：143
* PENDING：0
* 最终 DIMENSION_GROUP：66
* 映射引用闭合：66/66
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5252	5252	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
5253_prefl	5253	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5253_facelift	5253	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5254_prefl	5254	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5254_facelift	5254	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5255	5255	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	Toledo I五门掀背外廓。	READY
5256	5256	Hatchback	Felicia I	791	5	EU-SKODA-FELICIA-I-HATCHBACK-01	HIGH	Felicia I五门掀背外廓。	READY
5257	5257	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5258	5258	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5259	5259	Wagon	Felicia I	795	5	EU-SKODA-FELICIA-I-795-WAGON-01	HIGH	Typ 795五门旅行车外廓。	READY
5260_cargo_swb_lowroof	5260	Van	Doblo I Facelift	223		EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	HIGH	短轴标准顶Cargo外廓。	READY
5260_cargo_swb_highroof	5260	Van	Doblo I Facelift	223		EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	HIGH	短轴高顶Cargo外廓。	READY
5260_mpv_lowroof	5260	MPV	Doblo I Facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	HIGH	标准顶乘用MPV外廓。	READY
5260_mpv_highroof	5260	MPV	Doblo I Facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	HIGH	高顶乘用MPV外廓。	READY
5261	5261	SUV	X-90	EL	2	EU-SUZUKI-X-90-EL-SUV-2D-01	HIGH	两门T形顶SUV外廓。	READY
5262_3dr	5262	Hatchback	Corolla VII	E100	3	EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	HIGH	E100三门Compact外廓。	READY
5262_5dr	5262	Hatchback	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	HIGH	E100五门Compact外廓。	READY
5263_cargo_swb_lowroof	5263	Van	Doblo I Facelift	223		EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	HIGH	短轴标准顶Cargo外廓。	READY
5263_cargo_swb_highroof	5263	Van	Doblo I Facelift	223		EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	HIGH	短轴高顶Cargo外廓。	READY
5263_cargo_lwb_lowroof	5263	Van	Doblo I Facelift	223		EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-LWB-LOWROOF-01	HIGH	长轴标准顶Cargo外廓。	READY
5263_mpv_lowroof	5263	MPV	Doblo I Facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	HIGH	标准顶乘用MPV外廓。	READY
5263_mpv_highroof	5263	MPV	Doblo I Facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	HIGH	高顶乘用MPV外廓。	READY
5264	5264	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	E100五门旅行车外廓。	READY
5265_modus	5265	MPV	Modus I	J77	5	EU-RENAULT-MODUS-I-J77-MPV-01	HIGH	车型字段同时覆盖短轴Modus。	READY
5265_grand	5265	MPV	Grand Modus I	R77	5	EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	HIGH	车型字段同时覆盖长轴Grand Modus。	READY
5266	5266	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	HIGH	E100五门旅行车外廓。	READY
5267_modus	5267	MPV	Modus I	J77	5	EU-RENAULT-MODUS-I-J77-MPV-01	HIGH	车型字段同时覆盖短轴Modus。	READY
5267_grand	5267	MPV	Grand Modus I	R77	5	EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	HIGH	车型字段同时覆盖长轴Grand Modus。	READY
5268	5268	Wagon	Corolla VII	E100	5	EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	MEDIUM	E100四驱五门旅行车采用相同外廓组。	READY
5269	5269	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5270	5270	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5271	5271	Sedan	Corolla VII	E100	4	EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	HIGH	E100四门三厢外廓。	READY
5272_3dr	5272	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5272_5dr	5272	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5273_3dr	5273	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5273_5dr	5273	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5274	5274	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH	Golf III Variant五门旅行车外廓。	READY
5275	5275	Sedan	Passat B4	3A2	4	EU-VW-PASSAT-B4-3A2-SEDAN-01	HIGH	生产日期对应B4四门三厢。	READY
5276	5276	Wagon	Passat B4 Variant	3A5	5	EU-VW-PASSAT-B4-3A5-WAGON-01	HIGH	生产日期对应B4五门旅行版。	READY
5277	5277	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5278	5278	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5279	5279	Hatchback	Polo III	6N1		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	6N1三门与五门共用已确认外廓组。	READY
5280	5280	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5281_prefl_swb	5281	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	改款前短轴Bus外廓。	READY
5281_prefl_lwb	5281	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	改款前长轴Bus外廓。	READY
5281_facelift_swb	5281	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	HIGH	改款后长鼻短轴Bus外廓。	READY
5281_facelift_lwb	5281	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	HIGH	改款后长鼻长轴Bus外廓。	READY
5282	5282	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-01	HIGH	JC五门跨界MPV外廓。	READY
5283_prefl	5283	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5283_facelift	5283	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5284_prefl	5284	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5284_facelift	5284	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5285_swb_lowroof	5285	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
5285_lwb_midroof	5285	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
5286_swb_lowroof	5286	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
5286_lwb_midroof	5286	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
5287_swb_lowroof	5287	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
5287_lwb_midroof	5287	MPV	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
5288	5288	Hatchback	Megane III	BZ0	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH	Megane III五门掀背外廓。	READY
5289	5289	Wagon	Megane III Grandtour	KZ0	5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Grandtour五门旅行车外廓。	READY
5290	5290	Convertible	Megane III CC	EZ0	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
5291	5291	MPV	5008 I	T87	5	EU-PEUGEOT-5008-I-T87-MPV-01	HIGH	T87五门MPV外廓。	READY
5292_swb_lowroof	5292	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Kasten外廓。	READY
5292_swb_midroof	5292	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶Kasten外廓。	READY
5292_lwb_midroof	5292	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Kasten外廓。	READY
5292_lwb_highroof	5292	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶Kasten外廓。	READY
5293_swb_lowroof	5293	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Kasten外廓。	READY
5293_swb_midroof	5293	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶Kasten外廓。	READY
5293_lwb_midroof	5293	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Kasten外廓。	READY
5293_lwb_highroof	5293	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶Kasten外廓。	READY
5294_swb_lowroof	5294	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶Kasten外廓。	READY
5294_swb_midroof	5294	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶Kasten外廓。	READY
5294_lwb_midroof	5294	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶Kasten外廓。	READY
5294_lwb_highroof	5294	Van	Transit VE6 Facelift	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶Kasten外廓。	READY
5296_3dr	5296	Hatchback	Escort VI	GAL	3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	Schrägheck记录覆盖三门外廓。	READY
5296_5dr	5296	Hatchback	Escort VI	GAL	5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	Schrägheck记录覆盖五门外廓。	READY
5298	5298	MPV	807 I	E	5	EU-PEUGEOT-807-I-E-MPV-01	HIGH	807五门大型MPV外廓。	READY
5299	5299	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5300	5300	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5301	5301	Sedan	Polo III Classic	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门三厢外廓。	READY
5302	5302	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5303	5303	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5304	5304	Van	Caddy II	9K9		EU-VW-CADDY-II-9K9-VAN-01	MEDIUM	输入合并Kasten与Großraumlimousine；两者共用Typ 9K外廓。	READY
5305	5305	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5306	5306	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5307	5307	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5308	5308	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5309	5309	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5310	5310	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5311	5311	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5312	5312	Hatchback	iOn		5	EU-PEUGEOT-ION-HATCHBACK-01	HIGH	iOn五门电动掀背外廓。	READY
5313	5313	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5314	5314	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5315	5315	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5316	5316	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH	8D5五门Avant外廓。	READY
5317	5317	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH	Mondeo I五门旅行车外廓。	READY
5318	5318	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	A6 C4普通车身四门三厢。	READY
5319	5319	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	A6 C4普通车身五门Avant。	READY
5320	5320	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	Quattro未改变普通车身外廓。	READY
5321	5321	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	Quattro未改变普通Avant外廓。	READY
5322	5322	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	A6 C4普通车身四门三厢。	READY
5323	5323	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	A6 C4普通车身五门Avant。	READY
5324	5324	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH	Quattro未改变普通车身外廓。	READY
5325	5325	Wagon	A6 C4 Avant	4A5	5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH	Quattro未改变普通Avant外廓。	READY
5326	5326	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Escort VI改款双门敞篷外廓。	READY
5327_prefl	5327	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-PREFL-01	HIGH	Ktype生产期覆盖改款前三厢外廓。	READY
5327_facelift	5327	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	Ktype生产期覆盖改款后三厢外廓。	READY
5328_3dr	5328	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5328_5dr	5328	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5329_3dr	5329	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5329_5dr	5329	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5330_3dr	5330	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5330_5dr	5330	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5331	5331	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	218 K VVC高功率版本对应三门外廓。	READY
5332_3dr	5332	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5332_5dr	5332	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5333_3dr	5333	Hatchback	200 III	RF	3	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF三门掀背外廓。	READY
5333_5dr	5333	Hatchback	200 III	RF	5	EU-ROVER-200-III-RF-HATCHBACK-01	HIGH	RF五门掀背外廓。	READY
5334	5334	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	MEDIUM	120 kW/163 hp五门F20改款前外廓。	READY
5335_3dr	5335	Hatchback	1 Series II	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
5335_5dr	5335	Hatchback	1 Series II	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
5337_90	5337	SUV	Defender I		3	EU-LAND-ROVER-DEFENDER-I-90-STATION-WAGON-01	HIGH	Defender 90 Station Wagon外廓。	READY
5337_110	5337	SUV	Defender I		5	EU-LAND-ROVER-DEFENDER-I-110-STATION-WAGON-01	HIGH	Defender 110 Station Wagon外廓。	READY
5338	5338	Convertible	Defender I		2	EU-LAND-ROVER-DEFENDER-I-90-SOFT-TOP-01	MEDIUM	开放式车型对应Defender 90 Soft Top。	READY
5339	5339	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5340	5340	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5341	5341	MPV	Vito W638	W638		EU-MERCEDES-BENZ-VITO-W638-BUS-01	HIGH	W638乘用Bus外廓。	READY
5342	5342	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Escort VI改款双门敞篷外廓。	READY
5343	5343	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH	Mondeo I五门掀背外廓。	READY
5344	5344	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-01	HIGH	Mondeo I四门三厢外廓。	READY
5345	5345	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背外廓。	READY
5346_prefl	5346	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5346_facelift	5346	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5347	5347	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	DA双门改款前Coupe外廓。	READY
5348	5348	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	2.0 I版本对应改款前DA外廓。	READY
5349_prefl	5349	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	Ktype生产期覆盖改款前外廓。	READY
5349_facelift	5349	Coupe	Megane I Coach	DA	2	EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	HIGH	Ktype生产期覆盖改款后外廓。	READY
5350	5350	Convertible	California I	F149	2	EU-FERRARI-CALIFORNIA-I-F149-CONVERTIBLE-01	HIGH	F149双门硬顶敞篷外廓。	READY
5352	5352	Coupe	Impreza I	GFC	2	EU-SUBARU-IMPREZA-I-GFC-COUPE-2D-01	HIGH	GFC两门自然吸气四驱Coupe外廓。	READY
5353	5353	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH	GC四门三厢外廓。	READY
5354_prefl	5354	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-PREFL-01	HIGH	Ktype生产期覆盖改款前三厢外廓。	READY
5354_facelift	5354	Sedan	406 I	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	Ktype生产期覆盖改款后三厢外廓。	READY
5355	5355	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门三厢外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5101-5200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420	Auto-Data Renault Megane I BA0 Phase I	https://www.auto-data.net/en/renault-megane-i-ba0-1-generation-2157
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420	Auto-Data Renault Megane I BA0 Phase II	https://www.auto-data.net/en/renault-megane-i-hatchback-ba0-1-phase-ii-1999-generation-5203
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424	Auto-Data SEAT Toledo I 1L	https://www.auto-data.net/en/seat-toledo-i-1l-generation-1017
EU-SKODA-FELICIA-I-HATCHBACK-01	3883	1635	1415	Auto-Data Skoda Felicia I 791	https://www.auto-data.net/en/skoda-felicia-i-791-generation-9518
EU-SKODA-FELICIA-I-795-WAGON-01	4205	1635	1420	Automobile-Catalog 1995 Skoda Felicia Estate 1.3 (54)	https://www.automobile-catalog.com/car/1995/3133670/skoda_felicia_estate_1_3_54.html
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	4253	1722	1831	Fiat Doblo 2000-2009 technical specifications	https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	4253	1722	2086	Fiat Doblo 2000-2009 technical specifications	https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	4253	1722	1818	Fiat Doblo 2000-2009 technical specifications	https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	4253	1722	2073	Fiat Doblo 2000-2009 technical specifications	https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications
EU-SUZUKI-X-90-EL-SUV-2D-01	3710	1695	1555	Automobile-Catalog 1996 Suzuki X-90 4WD	https://www.automobile-catalog.com/car/1996/3351515/suzuki_x-90_4wd_automatic.html
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380	Automobile-Catalog 1995 Toyota Corolla Compact 1.3 XLi	https://www.automobile-catalog.com/car/1995/3583565/toyota_corolla_compact_1_3_xli.html
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380	Automobile-Catalog 1995 Toyota Corolla Compact 1.3 XLi	https://www.automobile-catalog.com/car/1995/3583565/toyota_corolla_compact_1_3_xli.html
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-LWB-LOWROOF-01	4633	1722	1817	Fiat Doblo 2000-2009 technical specifications	https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460	Auto-Data Toyota Corolla Wagon VII E100	https://www.auto-data.net/en/toyota-corolla-wagon-vii-e100-generation-833
EU-RENAULT-MODUS-I-J77-MPV-01	3874	1709	1589	Renault Modus and Grand Modus official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Renault-Modus-2008-UK.pdf
EU-RENAULT-GRAND-MODUS-I-R77-MPV-01	4034	1709	1589	Renault Modus and Grand Modus official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Renault-Modus-2008-UK.pdf
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380	Auto-Data Toyota Corolla VII E100 Sedan	https://www.auto-data.net/en/toyota-corolla-vii-e100-generation-831
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1H1	https://www.auto-data.net/en/volkswagen-golf-iii-1h1-generation-1863
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1H1	https://www.auto-data.net/en/volkswagen-golf-iii-1h1-generation-1863
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant 1H5	https://www.auto-data.net/en/volkswagen-golf-iii-variant-1h5-generation-1864
EU-VW-PASSAT-B4-3A2-SEDAN-01	4605	1720	1430	Auto-Data Volkswagen Passat B4 generation	https://www.auto-data.net/en/volkswagen-passat-b4-generation-8293
EU-VW-PASSAT-B4-3A5-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B4 1.9 TDI 110	https://www.auto-data.net/en/volkswagen-passat-variant-b4-1.9-tdi-110hp-8985
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Auto-Data Volkswagen Polo III 6N	https://www.auto-data.net/en/volkswagen-polo-iii-6n-generation-1854
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414	Auto-Data Volkswagen Polo III Classic 1.4 60	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-1.4-60hp-8453
EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	4655	1840	1940	Auto-Data Volkswagen Caravelle T4 2.5 SWB	https://www.auto-data.net/en/volkswagen-caravelle-t4-2.5-110hp-49330
EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	5055	1840	1940	Auto-Data Volkswagen Caravelle T4 Long 2.5	https://www.auto-data.net/en/volkswagen-caravelle-t4-long-2.5-110hp-49339
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	4789	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift 2.5 TDI SWB	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-tdi-102hp-49361
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	5189	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Long 2.5 TDI	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.5-tdi-102hp-49374
EU-DODGE-JOURNEY-I-JC-MPV-01	4888	1835	1691	Car and Driver 2009 Dodge Journey specifications	https://www.caranddriver.com/dodge/journey/specs/2009/dodge_journey_dodge-journey_2009
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-PREFL-01	3600	1654	1470	Automobile-Catalog 2011 Renault Twingo II phase I range	https://www.automobile-catalog.com/make/renault/twingo_2gen/twingo_2_1/2011.html
EU-RENAULT-TWINGO-II-CN0-HATCHBACK-FACELIFT-01	3687	1654	1470	Automobile-Catalog 2012 Renault Twingo II facelift	https://www.automobile-catalog.com/car/2012/2956325/renault_twingo_1_2_lev_16v_75.html
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Ford Transit VE6 facelift cached technical specification	https://www.automobile-catalog.com/make/ford_europe/transit_4gen/transit_4_van/1995.html
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Ford Transit VE6 facelift cached technical specification	https://www.automobile-catalog.com/make/ford_europe/transit_4gen/transit_4_van/1995.html
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471	Auto-Data Renault Megane III hatchback	https://www.auto-data.net/en/renault-megane-iii-generation-5400
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Auto-Data Renault Megane III Grandtour	https://www.auto-data.net/en/renault-megane-iii-grandtour-generation-5402
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	Auto-Data Renault Megane III CC	https://www.auto-data.net/en/renault-megane-iii-cc-generation-5401
EU-PEUGEOT-5008-I-T87-MPV-01	4529	1837	1644	Automobile-Catalog 2010 Peugeot 5008 1.6 HDi 112	https://www.automobile-catalog.com/car/2010/2625995/peugeot_5008_1_6_hdi_fap_112_110.html
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Ford Transit VE6 facelift cached technical specification	https://www.automobile-catalog.com/make/ford_europe/transit_4gen/transit_4_van/1995.html
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Ford Transit VE6 facelift cached technical specification	https://www.automobile-catalog.com/make/ford_europe/transit_4gen/transit_4_van/1995.html
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398	Auto-Data Ford Escort VI GAL facelift	https://www.auto-data.net/en/ford-escort-vi-gal-generation-3021
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398	Auto-Data Ford Escort VI GAL facelift	https://www.auto-data.net/en/ford-escort-vi-gal-generation-3021
EU-PEUGEOT-807-I-E-MPV-01	4727	1854	1752	Automobile-Catalog 2010 Peugeot 807 2.0 HDi	https://www.automobile-catalog.com/car/2010/2618780/peugeot_807_2_0_hdi_136.html
EU-VW-CADDY-II-9K9-VAN-01	4207	1696	1836	Volkswagen Caddy Typ 9K model history; Auto-Data SEAT Inca 9K 1.6 specification	https://en.wikipedia.org/wiki/Volkswagen_Caddy;https://www.auto-data.net/de/seat-inca-9k-1.6-i-75hp-45514
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417	Automobile-Catalog 1996 Audi A4 Avant B5	https://www.automobile-catalog.com/car/1996/241670/audi_a4_avant_1_9_tdi.html
EU-PEUGEOT-ION-HATCHBACK-01	3475	1475	1608	Auto-Data Peugeot iOn	https://www.auto-data.net/en/peugeot-ion-generation-3690
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510	Auto-Data Ford Mondeo I Turnier BNP	https://www.auto-data.net/en/ford-mondeo-i-turnier-bnp-generation-1490
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Auto-Data Audi A6 C4 4A2	https://www.auto-data.net/en/audi-a6-c4-4a2-generation-179
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440	Auto-Data Audi A6 C4 Avant 4A5	https://www.auto-data.net/en/audi-a6-c4-avant-4a5-generation-180
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379	Auto-Data Ford Escort VI Cabriolet ALL	https://www.auto-data.net/en/ford-escort-vi-cabrio-all-generation-3024
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410	Auto-Data Peugeot 406 Sedan phase I	https://www.auto-data.net/en/peugeot-406-8b-generation-1248
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412	Auto-Data Peugeot 406 Sedan phase II	https://www.auto-data.net/en/peugeot-406-8b-facelift-1999-generation-4902
EU-ROVER-200-III-RF-HATCHBACK-01	3973	1688	1419	Auto-Data Rover 200 RF; Automobile-Catalog 1996 Rover 200 vi	https://www.auto-data.net/en/rover-200-model-1222;https://www.automobile-catalog.com/car/1996/3012155/rover_200_vi.html
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	BMW Group official new BMW 1 Series specifications	https://www.press.bmwgroup.com/global/article/detail/T0117564EN/the-new-bmw-1-series
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	BMW Group PressClub new three-door BMW 1 Series	https://www.press.bmwgroup.com/asia/article/detail/T0137200EN/the-new-three-door-bmw-1-series?language=en
EU-LAND-ROVER-DEFENDER-I-90-STATION-WAGON-01	3883	1790	1963	Automobile-Catalog 1997 Land Rover Defender 90 County 300Tdi	https://www.automobile-catalog.com/car/1997/1396640/land-rover_defender_90_county_300tdi.html
EU-LAND-ROVER-DEFENDER-I-110-STATION-WAGON-01	4599	1790	2035	Automobile-Catalog 1997 Land Rover Defender 110 Station Wagon 300Tdi	https://www.automobile-catalog.com/car/1997/1395890/land-rover_defender_110_station_wagon_300tdi.html
EU-LAND-ROVER-DEFENDER-I-90-SOFT-TOP-01	3722	1790	1965	Automobile-Catalog 1997 Land Rover Defender 90 Soft Top 300Tdi	https://www.automobile-catalog.com/car/1997/1395950/land-rover_defender_90_soft_top_300tdi.html
EU-MERCEDES-BENZ-VITO-W638-BUS-01	4660	1880	1875	UltimateSpecs Mercedes-Benz Vito W638 Kombi	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/M15370/Vito-W638-Kombi
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424	Auto-Data Ford Mondeo I GBP hatchback	https://www.auto-data.net/en/ford-mondeo-i-hatchback-gbp-generation-1488
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424	Auto-Data Ford Mondeo I GBP sedan	https://www.auto-data.net/en/ford-mondeo-i-sedan-gbp-generation-1489
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366	Auto-Data Renault Megane I Coach DA generation	https://www.auto-data.net/en/renault-megane-i-coach-da-generation-2154
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366	Auto-Data Renault Megane I Coach Phase II 2.0i 16V	https://www.auto-data.net/en/renault-megane-i-coach-phase-ii-1999-2.0i-16v-147hp-30542
EU-FERRARI-CALIFORNIA-I-F149-CONVERTIBLE-01	4563	1902	1308	Ferrari official California specifications	https://www.ferrari.com/en-EN/auto/ferrari-california
EU-SUBARU-IMPREZA-I-GFC-COUPE-2D-01	4350	1690	1410	Auto-Data Subaru Impreza I Coupe GFC 2.0 AWD	https://www.auto-data.net/en/subaru-impreza-i-coupe-gfc-2.0-115hp-4wd-16104
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415	Auto-Data Subaru Impreza I GC sedan	https://www.auto-data.net/en/subaru-impreza-i-gc-generation-2630
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380	Auto-Data Honda Accord V CC7 sedan	https://www.auto-data.net/en/honda-accord-v-cc7-generation-3041
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5101-5200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications "https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications"
[2]: https://www.automobile-catalog.com/car/1995/3583565/toyota_corolla_compact_1_3_xli.html "https://www.automobile-catalog.com/car/1995/3583565/toyota_corolla_compact_1_3_xli.html"
[3]: https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-tdi-102hp-49361 "https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-tdi-102hp-49361"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5101-5200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5101-5200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6718 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2077 行）

