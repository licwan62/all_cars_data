# 任务：all 第 7701-7800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0078__2d2f1144


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7701-7800 行

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
all 第 7701-7800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7701-7800_ktype_dimension_mapping_final.tsv
- all_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CADILLAC-BLS-SEDAN-4D-01	4680	1752	1471
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296
EU-MERCEDES-BENZ-SL-W113-CONVERTIBLE-01	4285	1760	1320
EU-MERCEDES-BENZ-SL-W121-CONVERTIBLE-01	4290	1740	1320
EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	3680	1590	1380
EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	3680	1590	1380
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376
EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	3678	1610	1357
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
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2455-01	5505	1998	2455
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-H2470-01	5505	1998	2470
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2145-01	5005	1998	2145
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-H2465-01	5005	1998	2465
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-H2450-01	4655	1998	2450
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2130-01	5005	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-H2150-01	5005	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5005	1998	2475
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-1.9TD-01	4665	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2150-01	4655	1998	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395
EU-RENAULT-CLIO-III-X85-VAN-3D-01	3986	1719	1495
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420
EU-RENAULT-MEGANE-SCENIC-I-MPV-01	4134	1719	1675
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424
EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	4142	1640	1424
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390
EU-SEAT-INCA-9K-VAN-01	4207	1696	1836
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mazda	626 v hatchback	2	Schrägheck	Frontantrieb	Benzin	85	115	May 1997	Oct 2002	2024-03-01	8373
Mercedes-benz	Clk	CLK 200	Coupe	Heckantrieb	Benzin	100	136	Jun 1997	Jun 2002	2024-03-01	8375
Mercedes-benz	Clk	CLK 230 Kompressor	Coupe	Heckantrieb	Benzin	142	193	Jun 1997	Jun 2000	2024-03-01	8376
Seat	Inca	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	42	57	Sep 1996	Jun 2003	2024-03-01	8377
Seat	Inca	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Sep 1996	Jun 2003	2024-03-01	8378
Mercedes-benz	Clk	CLK 320	Coupe	Heckantrieb	Benzin	160	218	Jun 1997	Jun 2002	2024-03-01	8379
Mercedes-benz	C-Klasse	C 230 T Kompressor	Kombi	Heckantrieb	Benzin	142	193	Jun 1997	Sep 2000	2024-03-01	8380
Mercedes-benz	C-Klasse	C 240 T	Kombi	Heckantrieb	Benzin	125	170	Jun 1997	Sep 2000	2024-03-01	8381
Mercedes-benz	C-Klasse	C 280 T	Kombi	Heckantrieb	Benzin	145	197	Jun 1997	Mar 2001	2024-03-01	8382
Mercedes-benz	Sl	60 AMG	Cabriolet	Heckantrieb	Benzin	280	381	May 1997	Oct 2001	2024-03-01	8383
Mercedes-benz	C-Klasse	C 240	Stufenheck	Heckantrieb	Benzin	125	170	Jun 1997	May 2000	2024-03-01	8384
Mercedes-benz	C-Klasse	C 280	Stufenheck	Heckantrieb	Benzin	145	197	Jun 1997	May 2000	2024-03-01	8385
Mercedes-benz	A-Klasse	A 140	Schrägheck	Frontantrieb	Benzin	60	82	Jul 1997	Aug 2004	2024-03-01	8386
Mercedes-benz	A-Klasse	A 160	Schrägheck	Frontantrieb	Benzin	75	102	Jul 1997	Aug 2004	2024-03-01	8387
Mercedes-benz	E-Klasse	E 250 Turbo-d	Stufenheck	Heckantrieb	Diesel	110	150	Jun 1997	Jul 1999	2024-03-01	8388
Mercedes-benz	E-Klasse	E 250 T Turbo-d	Kombi	Heckantrieb	Diesel	110	150	Jun 1997	Jul 1999	2024-03-01	8389
Peugeot	Boxer	2.5 TDI	Bus	Frontantrieb	Diesel	79	107	Jan 1997	Apr 2002	2024-03-01	8390
Peugeot	Boxer	2.5 TDI 4X4	Bus	Allrad	Diesel	79	107	Jan 1997	Apr 2002	2024-03-01	8391
Peugeot	Boxer	1.9 D	Bus	Frontantrieb	Diesel	51	69	Mar 1994	Apr 2002	2024-03-01	8392
Peugeot	406	2.0 16V	Coupe	Frontantrieb	Benzin	97	132	Mar 1997	Dec 2004	2024-03-01	8393
Peugeot	306	1.4	Kombi	Frontantrieb	Benzin	55	75	Mar 1997	Apr 2002	2024-03-01	8394
Peugeot	106 ii	1.1 I	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1997	Mar 2001	2024-03-01	8395
Peugeot	106 ii	1.0 I	Schrägheck	Frontantrieb	Benzin	37	50	Apr 1996	Mar 2001	2024-03-01	8396
Peugeot	306	1.9 TD	Kombi	Frontantrieb	Diesel	66	90	Feb 1997	Apr 2002	2024-03-01	8397
Peugeot	306	1.9 D	Kombi	Frontantrieb	Diesel	50	68	Mar 1997	Apr 2002	2024-03-01	8398
Peugeot	306	1.8 16V	Schrägheck	Frontantrieb	Benzin	81	110	Mar 1997	May 2001	2024-03-01	8399
Peugeot	306	1.8 16V	Stufenheck	Frontantrieb	Benzin	81	110	Mar 1997	May 2001	2024-03-01	8400
Peugeot	306	1.8 16V	Cabriolet	Frontantrieb	Benzin	81	110	May 1997	Apr 2002	2024-03-01	8401
Buick	Skylark	2.8	Stufenheck	Frontantrieb	Benzin	86	117	Apr 1979	Dec 1982	2024-03-01	8402
Peugeot	306	1.8 16V	Kombi	Frontantrieb	Benzin	81	110	Mar 1997	Apr 2002	2024-03-01	8403
Peugeot	306	1.8	Kombi	Frontantrieb	Benzin	74	101	Mar 1997	Apr 2002	2024-03-01	8404
Peugeot	306	1.6	Kombi	Frontantrieb	Benzin	65	89	Mar 1997	Oct 2000	2024-03-01	8405
Buick	Century	5.7 D	Stufenheck	Heckantrieb	Diesel	77	105	Apr 1978	Dec 1979	2024-03-01	8406
Peugeot	406	3.0 V6 24V	Coupe	Frontantrieb	Benzin	140	190	Mar 1997	Dec 2004	2024-03-01	8407
Peugeot	306	2.0 16V	Schrägheck	Frontantrieb	Benzin	97	132	Mar 1997	May 2001	2024-03-01	8409
Peugeot	306	2	Stufenheck	Frontantrieb	Benzin	97	132	Mar 1997	May 2001	2024-03-01	8410
Peugeot	306	2	Kombi	Frontantrieb	Benzin	97	132	Mar 1997	Apr 2002	2024-03-01	8411
Peugeot	306	2.0 16V	Cabriolet	Frontantrieb	Benzin	97	132	Mar 1997	Apr 2002	2024-03-01	8412
Renault	Megane i	2	Cabriolet	Frontantrieb	Benzin	84	114	Apr 1997	Aug 2003	2024-03-01	8413
Cadillac	Seville	5.7 D	Stufenheck	Frontantrieb	Diesel	77	105	Aug 1979	Dec 1985	2024-03-01	8414
Renault	Megane scénic	1.9 DTI	Großraumlimousine	Frontantrieb	Diesel	72	98	Apr 1997	Sep 1999	2024-05-01	8415
Renault	Clio i	1.9 D	Schrägheck	Frontantrieb	Diesel	40	54	Jan 1997	Sep 1998	2026-05-01	8416
Renault	Laguna i grandtour	3.0 24V	Kombi	Frontantrieb	Benzin	140	190	Mar 1997	Mar 2001	2024-03-01	8417
Renault	Megane i	1.9 DTI	Schrägheck	Frontantrieb	Diesel	72	98	Mar 1997	Feb 2001	2024-03-01	8418
Renault	Megane i classic	1.9 DTI	Stufenheck	Frontantrieb	Diesel	72	98	Mar 1997	Feb 2001	2024-03-01	8419
Renault	Megane i coach	1.9 DTI	Coupe	Frontantrieb	Diesel	72	98	Mar 1997	Feb 2001	2024-03-01	8420
Hyundai	H-1 / starex	2.4	Bus	Heckantrieb	Benzin	82	112	Jun 1997	Apr 2004	2024-03-01	8421
Hyundai	H-1 / starex	2.5 TD	Bus	Heckantrieb	Diesel	59	80	Jun 1997	Apr 2004	2024-03-01	8422
Mercedes-benz	Clk	CLK 200 Kompressor	Coupe	Heckantrieb	Benzin	141	192	Jun 1997	Jun 2000	2024-03-01	8423
Volvo	C70 i	2.0 T	Coupe	Frontantrieb	Benzin	166	226	Mar 1997	Sep 2002	2024-03-01	8424
Volvo	C70 i	2	Coupe	Frontantrieb	Benzin	132	180	Mar 1997	Sep 2002	2024-03-01	8425
Volvo	C70 i	T-5	Coupe	Frontantrieb	Benzin	176	240	Mar 1997	Sep 2002	2024-03-01	8426
Volvo	C70 i	2.4 T	Coupe	Frontantrieb	Benzin	142	193	Mar 1997	Sep 2002	2024-03-01	8427
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	150	204	Jan 2010	Mar 2018	2024-03-01	8428
Seat	Cordoba	1.4 I	Kombi	Frontantrieb	Benzin	44	60	Sep 1996	Dec 2002	2024-03-01	8429
Seat	Cordoba	1.9 SDI	Kombi	Frontantrieb	Diesel	47	64	Sep 1996	Jun 1999	2024-03-01	8430
VW	Polo	60 1.7 SDI	Schrägheck	Frontantrieb	Diesel	44	60	Aug 1997	Oct 1999	2024-03-01	8431
VW	Polo	90 1.8	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1997	Sep 2001	2024-03-01	8432
Seat	Cordoba	1.9 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Mar 1997	Oct 2002	2024-03-01	8433
Seat	Cordoba	1.6 I	Kombi	Frontantrieb	Benzin	74	101	Sep 1996	Dec 2002	2024-03-01	8434
Seat	Cordoba	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Aug 1996	Dec 2002	2024-03-01	8435
Seat	Cordoba	1.6 I	Kombi	Frontantrieb	Benzin	55	75	Sep 1996	Dec 2002	2024-03-01	8436
VW	Polo	1.8	Kombi	Frontantrieb	Benzin	66	90	May 1997	Sep 2001	2024-03-01	8437
Seat	Ibiza ii	1.0 I	Schrägheck	Frontantrieb	Benzin	37	50	Sep 1996	Feb 2002	2024-03-01	8438
VW	Passat b5 variant	2.8 V6 Syncro/4motion	Kombi	Allrad	Benzin	142	193	Jun 1997	Nov 2000	2024-03-01	8439
VW	Passat b5	1.8 Syncro/4motion	Stufenheck	Allrad	Benzin	92	125	Dec 1996	Aug 2000	2024-03-01	8440
Seat	Cordoba	1.0 I	Stufenheck	Frontantrieb	Benzin	37	50	Sep 1996	Oct 2002	2024-03-01	8441
VW	Passat b5 variant	1.8 Syncro/4motion	Kombi	Allrad	Benzin	92	125	Jun 1997	Nov 2000	2024-03-01	8442
VW	Passat b5	1.9 TDI Syncro/4motion	Stufenheck	Allrad	Diesel	81	110	Jun 1997	Aug 2000	2024-03-01	8443
VW	Passat b5 variant	1.9 TDI Syncro/4motion	Kombi	Allrad	Diesel	81	110	Jun 1997	Aug 2000	2024-03-01	8444
Infiniti	M	35H	Stufenheck	Heckantrieb	Benzin/Elektro	268	364	Apr 2011	-	2024-03-01	8445
KIA	Pro cee'd	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	92	125	Oct 2010	Feb 2013	2024-03-01	8446
KIA	Pro cee'd	1.6 Crdi 128	Schrägheck	Frontantrieb	Diesel	94	128	Oct 2010	Sep 2012	2024-03-01	8447
KIA	Cee'd	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	92	125	Oct 2010	Dec 2012	2024-03-01	8448
KIA	Cee'd	1.6 Crdi 128	Schrägheck	Frontantrieb	Diesel	94	128	Oct 2010	Dec 2012	2024-03-01	8449
KIA	Cee'd	1.6 Crdi 128	Kombi	Frontantrieb	Diesel	94	128	Oct 2010	Dec 2012	2024-03-01	8450
KIA	Carens iii	1.6 Cvvt	Großraumlimousine	Frontantrieb	Benzin	93	126	Jun 2009	Mar 2013	2024-05-01	8451
KIA	Sportage iii	1.6 GDI	SUV	Frontantrieb	Benzin	99	135	Jun 2010	Dec 2015	2024-05-01	8452
VW	Golf iii	1.9 SDI	Schrägheck	Frontantrieb	Diesel	47	64	Jul 1995	Aug 1997	2024-03-01	8453
KIA	Sportage iii	1.7 Crdi	SUV	Frontantrieb	Diesel	85	116	Dec 2010	Dec 2015	2024-05-01	8454
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Oct 1997	May 2004	2024-03-01	8456
VW	Golf iv	1.6	Schrägheck	Frontantrieb	Benzin	74	100	Aug 1997	May 2004	2024-03-01	8460
VW	Golf iv	1.9 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Aug 1997	May 2004	2024-03-01	8461
KIA	Carens iii	1.6 Crdi 128	Großraumlimousine	Frontantrieb	Diesel	94	128	Oct 2010	Mar 2013	2024-05-01	8469
KIA	Carens iii	2.0 Crdi 115	Großraumlimousine	Frontantrieb	Diesel	85	115	May 2007	Mar 2013	2024-05-01	8470
Opel	Agila b	1.2	Schrägheck	Frontantrieb	Benzin	69	94	Apr 2010	Oct 2014	2025-06-01	8471
VW	Golf iii variant	1.9 SDI	Kombi	Frontantrieb	Diesel	47	64	Jul 1995	Apr 1999	2024-03-01	8475
Renault	Kangoo	Z.e.	Kasten/Großraumlimousine	Frontantrieb	Elektro	44	60	Oct 2011	-	2024-03-01	8476
Renault	Laguna iii	3.5 V6	Schrägheck	Frontantrieb	Benzin	175	238	Apr 2008	Dec 2015	2024-03-01	8477
Renault	Laguna iii grandtour	3.5 V6	Kombi	Frontantrieb	Benzin	175	238	Apr 2008	Dec 2015	2024-03-01	8478
Peugeot	Partner	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	72	98	Nov 2010	-	2024-03-01	8484
Cadillac	Escalade	6.0 Hybrid AWD	SUV	Allrad	Benzin/Elektro	283	385	Nov 2010	Dec 2013	2024-03-01	8486
VW	Vento	1.9 SDI	Stufenheck	Frontantrieb	Diesel	47	64	Apr 1997	Sep 1998	2024-03-01	8487
Cadillac	Bls	2.8 T	Kombi	Frontantrieb	Benzin	206	280	Aug 2010	-	2024-03-01	8488
Cadillac	Bls	2.8 T AWD	Kombi	Allrad	Benzin	206	280	Oct 2008	-	2024-03-01	8489
Cadillac	Sts	3.6	Stufenheck	Heckantrieb	Benzin	229	311	Oct 2009	Dec 2012	2024-03-01	8490
Cadillac	Bls	2.8 T AWD	Stufenheck	Allrad	Benzin	206	280	Oct 2008	-	2024-03-01	8491
Chevrolet	Beretta	2.2	Coupe	Frontantrieb	Benzin	71	97	Jan 1991	Dec 1996	2024-03-01	8492
Chevrolet	Corsica	2.2	Stufenheck	Frontantrieb	Benzin	71	97	Jan 1990	Dec 1991	2024-03-01	8493
Chevrolet	Corsica	2.2	Stufenheck	Frontantrieb	Benzin	82	112	Sep 1991	Dec 1996	2025-02-03	8494


--- Round 1 / 首次发送 ---
## 更新点

* 已优先完成跨批次缓存匹配，复用 36 个既有尺寸组，不重复输出其三维和来源。
* 首次闭合 Mazda 626 V GF 五门掀背与 Mercedes-Benz CLK C208 Coupé 两个尺寸组。Mazda 626 的欧洲 2.0 五门车型资料给出 4575×1710×1430 mm，宽度明确为不含后视镜；Mercedes-Benz 官方档案确认 CLK 200、CLK 230 Kompressor 与 CLK 320 的 C208 外廓均为 4567×1722×1371 mm。([汽车目录][1])
* Mercedes-Benz SL 60 AMG 官方档案给出的外廓与已有 R129 4470×1812×1296 mm 稳定组相同，本轮直接复用，不另建重复组。([marsClassic][2])
* Peugeot 106/306、Renault Mégane I、Mercedes-Benz W202/S202/W210/S210、VW Passat B5、Golf III、Touareg II 等已按门数、车身代码或改款边界完成关联。Renault Mégane I 的 BA0、LA0、DA0 与 Scénic JA0 边界已交叉确认。([AS-PL][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：43
* READY 映射行：57
* 待处理输入 Ktype：57
* 当前已引用尺寸组：38
* 本轮首次创建尺寸组：2
* 本轮复用既有尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8373	8373	Hatchback	Mazda 626 V	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-5D-01	HIGH		READY
8375	8375	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8376	8376	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8377	8377	Van	SEAT Inca I	9K		EU-SEAT-INCA-9K-VAN-01	HIGH	Kasten/Kombi共用同一外廓。	READY
8378	8378	Van	SEAT Inca I	9K		EU-SEAT-INCA-9K-VAN-01	HIGH	Kasten/Kombi共用同一外廓。	READY
8379	8379	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8380	8380	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8381	8381	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8382	8382	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8383	8383	Convertible	Mercedes-Benz SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	MEDIUM	SL 60 AMG外廓与既有R129低车身组一致；复用稳定组。	READY
8384	8384	Sedan	Mercedes-Benz C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH		READY
8385	8385	Sedan	Mercedes-Benz C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH		READY
8388	8388	Sedan	Mercedes-Benz E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
8389	8389	Wagon	Mercedes-Benz E-Class W210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8395_3dr	8395	Hatchback	Peugeot 106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8395_5dr	8395	Hatchback	Peugeot 106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8396_3dr	8396	Hatchback	Peugeot 106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8396_5dr	8396	Hatchback	Peugeot 106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8399_3dr	8399	Hatchback	Peugeot 306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8399_5dr	8399	Hatchback	Peugeot 306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8400	8400	Sedan	Peugeot 306 Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
8401	8401	Convertible	Peugeot 306 Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH		READY
8409_3dr	8409	Hatchback	Peugeot 306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8409_5dr	8409	Hatchback	Peugeot 306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8410	8410	Sedan	Peugeot 306 Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
8412	8412	Convertible	Peugeot 306 Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH		READY
8415	8415	MPV	Renault Mégane Scénic I	JA0	5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
8416_3dr	8416	Hatchback	Renault Clio I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	三门物理分支。	READY
8416_5dr	8416	Hatchback	Renault Clio I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	五门物理分支；与三门共用已确认三维。	READY
8418_prefl	8418	Hatchback	Renault Mégane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前物理分支。	READY
8418_facelift	8418	Hatchback	Renault Mégane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理分支。	READY
8419_prefl	8419	Sedan	Renault Mégane I	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH	改款前物理分支。	READY
8419_facelift	8419	Sedan	Renault Mégane I	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	HIGH	改款后物理分支。	READY
8420_prefl	8420	Coupe	Renault Mégane I	DA0	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	改款前物理分支。	READY
8420_facelift	8420	Coupe	Renault Mégane I	DA0	2	EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	HIGH	改款后物理分支。	READY
8423	8423	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8428_prefl	8428	SUV	Volkswagen Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	改款前物理分支。	READY
8428_facelift	8428	SUV	Volkswagen Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
8431_3dr	8431	Hatchback	Volkswagen Polo III	6N1	3	EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	三门物理分支。	READY
8431_5dr	8431	Hatchback	Volkswagen Polo III	6N1	5	EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	五门物理分支；与三门共用已确认三维。	READY
8432	8432	Sedan	Volkswagen Polo III	6KV2	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH		READY
8433	8433	Sedan	SEAT Córdoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH		READY
8438_3dr_prefl	8438	Hatchback	SEAT Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	三门改款前物理分支。	READY
8438_5dr_prefl	8438	Hatchback	SEAT Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	五门改款前物理分支。	READY
8438_3dr_facelift	8438	Hatchback	SEAT Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	HIGH	三门改款后物理分支。	READY
8438_5dr_facelift	8438	Hatchback	SEAT Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	HIGH	五门改款后物理分支。	READY
8439	8439	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8440	8440	Sedan	Volkswagen Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
8441	8441	Sedan	SEAT Córdoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH		READY
8442	8442	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8443	8443	Sedan	Volkswagen Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
8444	8444	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8453_3dr	8453	Hatchback	Volkswagen Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8453_5dr	8453	Hatchback	Volkswagen Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8475	8475	Wagon	Volkswagen Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
8487	8487	Sedan	Volkswagen Vento I	1H2	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
8491	8491	Sedan	Cadillac BLS		4	EU-CADILLAC-BLS-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-626-V-GF-HATCHBACK-5D-01	4575	1710	1430	Automobile-Catalog 1997 Mazda 626 2.0 5-Door Europe	https://www.automobile-catalog.com/car/1997/1665305/mazda_626_2_0_5-door.html
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371	Mercedes-Benz Public Archive CLK 200 C208	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-200.xhtml?oid=4562
```

## 下一步优先处理

1. 闭合 Peugeot 306 Wagon、406 Coupé 与 Boxer 230P Bus 的物理分支。
2. 批量处理 Mercedes-Benz A-Class W168/V168 的早期高度、改款与长轴版本边界。
3. 创建 Renault Laguna、Mégane Cabriolet、Hyundai H-1、Volvo C70、SEAT Córdoba Vario 和 VW Polo Variant 尺寸组。
4. 随后集中处理 Kia、Infiniti、Cadillac、Buick 与 Chevrolet 车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/1665305/mazda_626_2_0_5-door.html?utm_source=chatgpt.com "1997 Mazda 626 2.0 5-Door Specs Review (85 kW / 116 PS / 114 hp) (since August 1997 for Europe )"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-60-AMG.xhtml?oid=4720&utm_source=chatgpt.com "SL 60 AMG"
[3]: https://as-pl.com/en/tpu/A3090/1?utm_source=chatgpt.com "Application A3090 | AS-PL Rotating Electrics - Starter motors, Alternators, Parts for starter motors and alternators | AS-PL Sp. z o.o."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7701-7800_ktype_dimension_mapping_final.tsv
- all_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 Mercedes-Benz A-Class W168、Peugeot 306 Break、Peugeot 406 Coupé、Renault Mégane I Cabriolet、Renault Laguna I/III 和 Volvo C70 I 等车型簇。跨改款生产区间的 Mégane Cabriolet 已按改款前后不同长度拆分。([汽车目录][1])
* 完成 SEAT Córdoba Vario 改款前后、Kia Pro cee'd/Cee'd/Carens/Sportage、Volkswagen Golf IV 三门与五门以及 Opel Agila B 的尺寸组闭合。Golf IV 三门和五门虽然三维相同，仍按门数物理分支分别建组。([汽车目录][2])
* 本轮未重复输出任何既有缓存尺寸组，也未输出缓存来源或匹配理由。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：81
* READY 映射行：103
* PENDING 输入 Ktype：19
* 当前已引用尺寸组：57
* 本轮新增尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8386	8386	Hatchback	Mercedes-Benz A-Class W168	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH		READY
8387	8387	Hatchback	Mercedes-Benz A-Class W168	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH		READY
8393	8393	Coupe	Peugeot 406 Coupé	8C	2	EU-PEUGEOT-406-COUPE-2D-01	HIGH		READY
8394	8394	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8397	8397	Wagon	Peugeot306-PHASE-II-WAGON-5D-01	HIGH		 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8398	8398	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8403	8403	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8404	8404	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8405	8405	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8407	8407	Coupe	Peugeot 406 Coupé	8C	2	EU-PEUGEOT-406-COUPE-2D-01	HIGH		READY
8411	8411	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8413_prefl	8413	Convertible	Renault Mégane I	EA0	2	EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	HIGH	改款前物理分支。	READY
8413_facelift	8413	Convertible	Renault Mégane I	EA0	2	EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理分支。	READY
8417	8417	Wagon	Renault Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-01	HIGH		READY
8424	8424	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8425	8425	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8426	8426	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8427	8427	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8429_prefl	8429	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8429_facelift	8429	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8430	8430	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH		READY
8434_prefl	8434	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8434_facelift	8434	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8435_prefl	8435	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8435_facelift	8435	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8436_prefl	8436	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8436_facelift	8436	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8446	8446	Hatchback	Kia Cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	HIGH		READY
8447	8447	Hatchback	Kia Cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	HIGH		READY
8448	8448	Hatchback	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	HIGH		READY
8449	8449	Hatchback	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	HIGH		READY
8450	8450	Wagon	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-5D-FACELIFT-01	HIGH		READY
8451	8451	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8452	8452	SUV	Kia Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-5D-01	HIGH		READY
8454	8454	SUV	Kia Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-5D-01	HIGH		READY
8456_3dr	8456	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8456_5dr	8456	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8460_3dr	8460	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8460_5dr	8460	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8461_3dr	8461	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8461_5dr	8461	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8469	8469	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8470	8470	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8471	8471	Hatchback	Opel Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH		READY
8477	8477	Hatchback	Renault Laguna III	B91	5	EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	HIGH		READY
8478	8478	Wagon	Renault Laguna III	K91	5	EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	3575	1719	1575	Automobile-Catalog 1998 Mercedes-Benz A 160	https://www.automobile-catalog.com/car/1998/1532465/mercedes-benz_a_160.html
EU-PEUGEOT-406-COUPE-2D-01	4615	1780	1352	Autozine Peugeot 406 Coupe technical specifications	https://www.autozine.org/Archive/Peugeot/old/406.html
EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	4338	1689	1415	Automobile-Catalog 1997 Peugeot 306 Break 1.4i XR	https://www.automobile-catalog.com/car/1997/2612015/peugeot_306_break_1_4i_xr.html
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	4028	1698	1368	Automobile-Catalog 1997 Renault Mégane Cabriolet 2.0 16V	https://www.automobile-catalog.com/car/1997/2946725/renault_megane_cabriolet_2_0_16v.html
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	4082	1698	1368	Carfolio 2001 Renault Mégane Cabriolet 2.0 16V	https://www.carfolio.com/renault-megane-cabriolet-2.0-16v-254122
EU-RENAULT-LAGUNA-I-K56-WAGON-01	4620	1752	1448	Automobile-Catalog 1997 Renault Laguna Wagon 3.0i V6 24V	https://www.automobile-catalog.com/car/1997/2945840/renault_laguna_wagon_3_0i_v6_24v.html
EU-VOLVO-C70-I-P80-COUPE-2D-01	4720	1820	1410	Auto-Data Volvo C70 Coupe 2.3 T5	https://www.auto-data.net/en/volvo-c70-coupe-2.3-20v-t5-240hp-9509
EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	4142	1640	1426	Automobile-Catalog 1998 SEAT Córdoba Vario 1.4	https://www.automobile-catalog.com/car/1998/3066530/seat_cordoba_vario_1_4.html
EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	4163	1640	1433	Automobile-Catalog 2001 SEAT Córdoba Vario 1.4 16V	https://www.automobile-catalog.com/car/2001/3070850/seat_cordoba_vario_1_4_16v_75.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	4250	1790	1450	Automobile-Catalog 2010 Kia Pro_Cee'd 1.6 CVVT	https://www.automobile-catalog.com/car/2010/1359935/kia_pro_cee_d_1_6_cvvt_ex.html
EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	4260	1790	1480	Automobile-Catalog 2010 Kia Cee'd 1.6 CVVT	https://www.automobile-catalog.com/car/2010/1362125/kia_cee_d_1_1_6_cvvt_automatic.html
EU-KIA-CEED-I-ED-WAGON-5D-FACELIFT-01	4490	1790	1525	Automobile-Catalog 2010 Kia Cee'd SW 1.6 CRDi 128	https://www.automobile-catalog.com/car/2010/1361540/kia_cee_d_sw_1_6_crdi_128_spirit_dpf.html
EU-KIA-CARENS-II-UN-MPV-5D-01	4545	1820	1650	Automobile-Catalog 2009 Kia Carens 2.0 VGT 7-Seat	https://www.automobile-catalog.com/car/2009/1368215/kia_carens_2_0_vgt_7-seat.html
EU-KIA-SPORTAGE-III-SL-SUV-5D-01	4440	1855	1635	Automobile-Catalog 2010 Kia Sportage 2.0 CRDi AWD	https://www.automobile-catalog.com/car/2010/1364000/kia_sportage_2_0_crdi_vision_awd.html
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-8673
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-8673
EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	3740	1680	1590	Automobile-Catalog 2010 Opel Agila 1.2	https://www.automobile-catalog.com/car/2010/2529500/opel_agila_1_2.html
EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	4695	1811	1445	Automobile-Catalog 2008 Renault Laguna 2.0 dCi 150	https://www.automobile-catalog.com/car/2008/2957885/renault_laguna_2_0_dci_150_fap.html
EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	4803	1811	1445	Automobile-Catalog 2009 Renault Laguna Grandtour 3.5 V6	https://www.automobile-catalog.com/car/2009/2958230/renault_laguna_wagon_grandtour_3_5_v6.html
```

## 下一步优先处理

1. 闭合 Peugeot Boxer 230P Bus、Hyundai H-1/Starex 与 Volkswagen Polo Variant 的车长、车顶和改款边界。
2. 处理 Renault Kangoo Z.E. 与 Peugeot Partner II 的 Van/MPV 多外廓分支。
3. 集中完成 Buick、Cadillac、Chevrolet 与 Infiniti 剩余车型优先处理可批量复用的平台车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1998/1532465/mercedes-benz_a_160.html?utm_source=chatgpt.com "1998 Mercedes-Benz A 160 Specs Review (75 kW / 102 ..."
[2]: https://www.automobile-catalog.com/car/1998/3066530/seat_cordoba_vario_1_4.html?utm_source=chatgpt.com "1998 Seat Cordoba Vario 1.4 Specs Review (44 kW / 60 ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7701-7800_ktype_dimension_mapping_final.tsv
- all_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增闭合 14 个输入 Ktype，覆盖 Buick Skylark/Century、Cadillac Seville/BLS Wagon/STS/Escalade、Hyundai H-1、Infiniti M35h、VW Polo Variant、Chevrolet Beretta/Corsica 等车型簇。([汽车目录][1])
* Buick Skylark 按 1980–1981 与 1982 外廓拆分；Chevrolet Beretta 按 1991–1993 与 1994–1996 外廓拆分。Corsica 两个 Ktype 核对后三维一致，复用同一尺寸组。([汽车目录][1])
* Peugeot Boxer、Renault Kangoo Z.E. 和 Peugeot Partner II 暂不猜测派生分支，继续保持 PENDING；这些输入仍存在轴距、车顶高度或 Van/MPV 外廓边界未闭合的问题。([engineindetail.com][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：95
* READY 映射行：119
* PENDING 输入 Ktype：5
* 当前已引用尺寸组：70
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8390	8390	MPV	Peugeot Boxer I	230P			LOW	SWB/MWB及车顶物理分支尚未闭合。	PENDING: 2.5 TDI Bus配置边界未确认
8391	8391	MPV	Peugeot Boxer I	230P			LOW	4X4的SWB/MWB及车顶物理分支尚未闭合。	PENDING: 2.5 TDI 4X4 Bus配置边界未确认
8392	8392	MPV	Peugeot Boxer I	230P			LOW	1.9 D适用的轴距及车顶分支尚未闭合。	PENDING: 1.9 D Bus配置边界未确认
8402_pre82	8402	Sedan	Buick Skylark V	X	4	EU-BUICK-SKYLARK-V-SEDAN-4D-PRE82-01	HIGH	1980-1981外廓分支。	READY
8402_1982	8402	Sedan	Buick Skylark V	X	4	EU-BUICK-SKYLARK-V-SEDAN-4D-1982-01	HIGH	1982外廓分支。	READY
8406	8406	Sedan	Buick Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-4D-01	MEDIUM		READY
8414	8414	Sedan	Cadillac Seville II	K	4	EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	HIGH		READY
8421	8421	MPV	Hyundai H-1/Starex I	A1		EU-HYUNDAI-H1-STAREX-I-MPV-01	HIGH		READY
8422	8422	MPV	Hyundai H-1/Starex I	A1		EU-HYUNDAI-H1-STAREX-I-MPV-01	HIGH		READY
8437	8437	Wagon	Volkswagen Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH		READY
8445	8445	Sedan	Infiniti M Y51	Y51	4	EU-INFINITI-M-Y51-SEDAN-4D-01	HIGH		READY
8476	8476	Van	Renault Kangoo II	X61			LOW	SWB/LWB、改款前后及乘用分支仍需闭合。	PENDING: Z.E.物理分支及高度配置未完全确认
8484	8484	Van	Peugeot Partner II	B9			LOW	Kasten与Großraumlimousine候选外廓尚未闭合。	PENDING: Van/MPV及高度配置未完全确认
8486	8486	SUV	Cadillac Escalade III	GMT900	5	EU-CADILLAC-ESCALADE-III-HYBRID-SUV-5D-01	HIGH		READY
8488	8488	Wagon	Cadillac BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
8489	8489	Wagon	Cadillac BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
8490	8490	Sedan	Cadillac STS I	GMX295	4	EU-CADILLAC-STS-I-SEDAN-4D-01	HIGH		READY
8492_pre94	8492	Coupe	Chevrolet Beretta I	L	2	EU-CHEVROLET-BERETTA-I-COUPE-2D-PRE94-01	HIGH	1991-1993外廓分支。	READY
8492_94on	8492	Coupe	Chevrolet Beretta I	L	2	EU-CHEVROLET-BERETTA-I-COUPE-2D-94ON-01	HIGH	1994-1996外廓分支。	READY
8493	8493	Sedan	Chevrolet Corsica I	L	4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH		READY
8494	8494	Sedan	Chevrolet Corsica I	L	4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BUICK-SKYLARK-V-SEDAN-4D-PRE82-01	4620	1720	1359	Automobile-Catalog 1980 Buick Skylark Sedan 2.8L V6	https://www.automobile-catalog.com/car/1980/304310/buick_skylark_sedan_2_8l_v-6.html
EU-BUICK-SKYLARK-V-SEDAN-4D-1982-01	4600	1750	1364	Automobile-Catalog 1982 Buick Skylark Sedan 2.8L V6 automatic	https://www.automobile-catalog.com/car/1982/305345/buick_skylark_sedan_2_8l_v-6_automatic.html
EU-BUICK-CENTURY-IV-SEDAN-4D-01	4978	1834	1397	Automobile-Catalog 1979 Buick Century Limited Sedan	https://www.automobile-catalog.com/car/1979/179855/buick_century_limited_sedan_4_9l_v-8_automatic.html
EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	5202	1801	1379	Automobile-Catalog 1980 Cadillac Seville Elegante 5.7L Diesel	https://www.automobile-catalog.com/car/1980/47300/cadillac_seville_elegante_5_7l_v-8_diesel.html
EU-HYUNDAI-H1-STAREX-I-MPV-01	4695	1820	1885	Automobile-Catalog 1998 Hyundai H-1 Starex 2.4i; Automobile-Catalog 1998 Hyundai H-1 Starex 2.5 TD	https://www.automobile-catalog.com/car/1998/1167755/hyundai_h-1_starex_2_4i_automatic.html;https://www.automobile-catalog.com/car/1998/1167785/hyundai_h-1_starex_2_5_td.html
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433	Auto-Data Volkswagen Polo III Variant	https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n-generation-1858
EU-INFINITI-M-Y51-SEDAN-4D-01	4945	1845	1500	Automobile-Catalog 2011 Infiniti M35h GT Hybrid	https://www.automobile-catalog.com/car/2011/2169110/infiniti_m35h_gt_hybrid.html
EU-CADILLAC-ESCALADE-III-HYBRID-SUV-5D-01	5143	2007	1887	Automobile-Catalog 2012 Cadillac Escalade Hybrid 4WD	https://www.automobile-catalog.com/car/2012/1614005/cadillac_escalade_hybrid_4wd.html
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543	Automobile-Catalog 2008 Cadillac BLS Wagon 2.8 T V6 AWD	https://www.automobile-catalog.com/car/2008/1200440/cadillac_bls_wagon_2_8_t_v6_awd_sport_luxury.html
EU-CADILLAC-STS-I-SEDAN-4D-01	4986	1844	1463	Automobile-Catalog 2010 Cadillac STS 3.6 V6	https://www.automobile-catalog.com/car/2010/336755/cadillac_sts_3_6_v6.html
EU-CHEVROLET-BERETTA-I-COUPE-2D-PRE94-01	4755	1727	1344	Automobile-Catalog 1991 Chevrolet Beretta 2.2L	https://www.automobile-catalog.com/make/chevrolet_usa/beretta/beretta/1991.html
EU-CHEVROLET-BERETTA-I-COUPE-2D-94ON-01	4757	1727	1351	Automobile-Catalog 1994 Chevrolet Beretta 2.2 Europe export	https://www.automobile-catalog.com/car/1994/470720/chevrolet_beretta_2_2.html
EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	4658	1732	1367	Automobile-Catalog 1991 Chevrolet Corsica Sedan 2.2L; Automobile-Catalog 1994 Chevrolet Corsica Sedan 2.2L	https://www.automobile-catalog.com/car/1991/470180/chevrolet_corsica_sedan_2_2l.html;https://www.automobile-catalog.com/car/1994/470675/chevrolet_corsica_sedan_2_2l_automatic.html
```

## 下一步优先处理

1. 使用已有 Boxer 230P 缓存，确认 8390–8392 各自覆盖的 SWB/MWB、普通顶和高顶分支。
2. 闭合 Kangoo Z.E. 的 SWB/LWB、Van/MPV及改款高度分支。
3. 闭合 Partner II B9 的标准 Van 与 Partner Tepee 乘用外廓，完成剩余 5 个 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/304310/buick_skylark_sedan_2_8l_v-6.html?utm_source=chatgpt.com "1980 Buick Skylark Sedan 2.8L V-6 Specs Review (86 kW / 117 PS / 115 hp) (since September 1979 for North America U.S.)"
[2]: https://www.engineindetail.com/cars/peugeot/boxer/boxer-ii-estate-wagon-1998-2002 "https://www.engineindetail.com/cars/peugeot/boxer/boxer-ii-estate-wagon-1998-2002"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7701-7800_ktype_dimension_mapping_final.tsv
- all_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Ktype `8390` 已闭合：79 kW Boxer 230P Bus 的 270 C 与 310 C 配置均为 SWB、`4655×1998×2130 mm`，复用已有 `EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01`，不重复输出尺寸组。([Engine In Detail][1])
* Ktype `8476` 已按官方资料拆分 Kangoo Z.E. 的改款前/后、SWB/LWB、两座/五座及明确高度分支。官方资料确认改款前长度为 4213/4597 mm，后期长度为 4282/4666 mm，车身宽度均为不含后视镜的 1829 mm。([雷诺新闻][2])
* 本轮未重新抓取或重复输出任何已闭合缓存尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：97
* READY 映射行：132
* PENDING 输入 Ktype：3
* 当前已引用尺寸组：83
* 本轮首次创建尺寸组：12
* 剩余 PENDING：`8391`、`8392`、`8484`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8390	8390	MPV	Peugeot Boxer I	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	HIGH	270 C与310 C共享同一SWB外廓。	READY
8476_swb_prefl_h1805	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	MEDIUM	改款前SWB低高度分支。	READY
8476_swb_prefl_h1844	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	MEDIUM	改款前SWB高高度分支。	READY
8476_lwb_2s_prefl_h1810	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	MEDIUM	改款前LWB两座低高度分支。	READY
8476_lwb_2s_prefl_h1836	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	MEDIUM	改款前LWB两座高高度分支。	READY
8476_lwb_5s_prefl_h1802	8476	MPV	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	MEDIUM	改款前LWB五座低高度分支。	READY
8476_lwb_5s_prefl_h1826	8476	MPV	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	MEDIUM	改款前LWB五座高高度分支。	READY
8476_swb_facelift_h1805	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	MEDIUM	改款后SWB低高度分支。	READY
8476_swb_facelift_h1844	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	MEDIUM	改款后SWB高高度分支。	READY
8476_lwb_2s_facelift_h1810	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	MEDIUM	改款后LWB两座低高度分支。	READY
8476_lwb_2s_facelift_h1836	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	MEDIUM	改款后LWB两座高高度分支。	READY
8476_lwb_5s_facelift_h1802	8476	MPV	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	MEDIUM	改款后LWB五座低高度分支。	READY
8476_lwb_5s_facelift_h1826	8476	MPV	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	MEDIUM	改款后LWB五座高高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
```

## 下一步优先处理

1. 闭合 `8391` Boxer 2.5 TDI 4X4 的 SWB/MWB 与标准顶、高顶边界。
2. 闭合 `8392` Boxer 1.9 D Bus 的适用轴距和高度分支。
3. 闭合 `8484` Partner B9 1.6 的 Van/Tepee、改款前后外廓；达到 `PENDING=0` 后直接输出最终完整两表及指定下载链接。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/peugeot-boxer-estate-wagon-270-c-2-5-d-luxus-1998?utm_source=chatgpt.com "Peugeot Boxer Estate (Wagon) 270 C 2.5 D Luxus 1998 - Specs, Review & Tests"
[2]: https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf?utm_source=chatgpt.com "Kangoo ZE : dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7701-7800_ktype_dimension_mapping_final.tsv
- all_7701-7800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合最后 3 个 PENDING Ktype。
* `8391` 拆分为 Boxer 230P Bus 的 SWB/MWB 高顶 4X4 两个既有缓存分支；`8392` 关联 SWB 标准顶缓存组。([Brembo Parts][1])
* `8484` 确认为 Peugeot Partner II B9 L1H1 Van，新建尺寸组 `4380 × 1810 × 1801 mm`。([catalogonuevo.icerbrakes.com][2])
* 已完成固定表头、唯一性、引用闭合、正整数尺寸、来源完整性及文件名检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：136
* PENDING：0
* DIMENSION_GROUP：86
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合且无孤立尺寸组：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8373	8373	Hatchback	Mazda 626 V	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-5D-01	HIGH		READY
8375	8375	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8376	8376	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8377	8377	Van	SEAT Inca I	9K		EU-SEAT-INCA-9K-VAN-01	HIGH	Kasten/Kombi共用同一外廓。	READY
8378	8378	Van	SEAT Inca I	9K		EU-SEAT-INCA-9K-VAN-01	HIGH	Kasten/Kombi共用同一外廓。	READY
8379	8379	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8380	8380	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8381	8381	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8382	8382	Wagon	Mercedes-Benz C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH		READY
8383	8383	Convertible	Mercedes-Benz SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	MEDIUM	SL 60 AMG外廓与既有R129低车身组一致；复用稳定组。	READY
8384	8384	Sedan	Mercedes-Benz C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH		READY
8385	8385	Sedan	Mercedes-Benz C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH		READY
8386	8386	Hatchback	Mercedes-Benz A-Class W168	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH		READY
8387	8387	Hatchback	Mercedes-Benz A-Class W168	W168	5	EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	HIGH		READY
8388	8388	Sedan	Mercedes-Benz E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
8389	8389	Wagon	Mercedes-Benz E-Class W210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8390	8390	MPV	Peugeot Boxer I	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	HIGH	270 C与310 C共享同一SWB外廓。	READY
8391_swb_highroof	8391	MPV	Peugeot Boxer I	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	MEDIUM	SWB高顶4X4物理分支。	READY
8391_mwb_highroof	8391	MPV	Peugeot Boxer I	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	MEDIUM	MWB高顶4X4物理分支。	READY
8392	8392	MPV	Peugeot Boxer I	230P	4	EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	HIGH	1.9 D 270 C短轴标准顶外廓。	READY
8393	8393	Coupe	Peugeot 406 Coupé	8C	2	EU-PEUGEOT-406-COUPE-2D-01	HIGH		READY
8394	8394	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8395_3dr	8395	Hatchback	Peugeot 106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8395_5dr	8395	Hatchback	Peugeot 106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8396_3dr	8396	Hatchback	Peugeot 106 II		3	EU-PEUGEOT-106-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8396_5dr	8396	Hatchback	Peugeot 106 II		5	EU-PEUGEOT-106-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8397	8397	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8398	8398	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8399_3dr	8399	Hatchback	Peugeot 306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8399_5dr	8399	Hatchback	Peugeot 306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8400	8400	Sedan	Peugeot 306 Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
8401	8401	Convertible	Peugeot 306 Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH		READY
8402_pre82	8402	Sedan	Buick Skylark V	X	4	EU-BUICK-SKYLARK-V-SEDAN-4D-PRE82-01	HIGH	1980-1981外廓分支。	READY
8402_1982	8402	Sedan	Buick Skylark V	X	4	EU-BUICK-SKYLARK-V-SEDAN-4D-1982-01	HIGH	1982外廓分支。	READY
8403	8403	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8404	8404	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8405	8405	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8406	8406	Sedan	Buick Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-4D-01	MEDIUM		READY
8407	8407	Coupe	Peugeot 406 Coupé	8C	2	EU-PEUGEOT-406-COUPE-2D-01	HIGH		READY
8409_3dr	8409	Hatchback	Peugeot 306 Phase II		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8409_5dr	8409	Hatchback	Peugeot 306 Phase II		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8410	8410	Sedan	Peugeot 306 Phase II	7B	4	EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	HIGH		READY
8411	8411	Wagon	Peugeot 306 Phase II	7E	5	EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	HIGH		READY
8412	8412	Convertible	Peugeot 306 Phase II	7D	2	EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	HIGH		READY
8413_prefl	8413	Convertible	Renault Mégane I	EA0	2	EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	HIGH	改款前物理分支。	READY
8413_facelift	8413	Convertible	Renault Mégane I	EA0	2	EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理分支。	READY
8414	8414	Sedan	Cadillac Seville II	K	4	EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	HIGH		READY
8415	8415	MPV	Renault Mégane Scénic I	JA0	5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
8416_3dr	8416	Hatchback	Renault Clio I	C57	3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	三门物理分支。	READY
8416_5dr	8416	Hatchback	Renault Clio I	B57	5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	五门物理分支；与三门共用已确认三维。	READY
8417	8417	Wagon	Renault Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-01	HIGH		READY
8418_prefl	8418	Hatchback	Renault Mégane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	HIGH	改款前物理分支。	READY
8418_facelift	8418	Hatchback	Renault Mégane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理分支。	READY
8419_prefl	8419	Sedan	Renault Mégane I	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	HIGH	改款前物理分支。	READY
8419_facelift	8419	Sedan	Renault Mégane I	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	HIGH	改款后物理分支。	READY
8420_prefl	8420	Coupe	Renault Mégane I	DA0	2	EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	HIGH	改款前物理分支。	READY
8420_facelift	8420	Coupe	Renault Mégane I	DA0	2	EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	HIGH	改款后物理分支。	READY
8421	8421	MPV	Hyundai H-1/Starex I	A1		EU-HYUNDAI-H1-STAREX-I-MPV-01	HIGH		READY
8422	8422	MPV	Hyundai H-1/Starex I	A1		EU-HYUNDAI-H1-STAREX-I-MPV-01	HIGH		READY
8423	8423	Coupe	Mercedes-Benz CLK C208	C208	2	EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	HIGH		READY
8424	8424	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8425	8425	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8426	8426	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8427	8427	Coupe	Volvo C70 I	P80	2	EU-VOLVO-C70-I-P80-COUPE-2D-01	HIGH		READY
8428_prefl	8428	SUV	Volkswagen Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	改款前物理分支。	READY
8428_facelift	8428	SUV	Volkswagen Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	改款后物理分支。	READY
8429_prefl	8429	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8429_facelift	8429	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8430	8430	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH		READY
8431_3dr	8431	Hatchback	Volkswagen Polo III	6N1	3	EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	三门物理分支。	READY
8431_5dr	8431	Hatchback	Volkswagen Polo III	6N1	5	EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	五门物理分支；与三门共用已确认三维。	READY
8432	8432	Sedan	Volkswagen Polo III	6KV2	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH		READY
8433	8433	Sedan	SEAT Córdoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH		READY
8434_prefl	8434	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8434_facelift	8434	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8435_prefl	8435	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8435_facelift	8435	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8436_prefl	8436	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	HIGH	改款前物理分支。	READY
8436_facelift	8436	Wagon	SEAT Córdoba I	6K5	5	EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	HIGH	改款后物理分支。	READY
8437	8437	Wagon	Volkswagen Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH		READY
8438_3dr_prefl	8438	Hatchback	SEAT Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	三门改款前物理分支。	READY
8438_5dr_prefl	8438	Hatchback	SEAT Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	五门改款前物理分支。	READY
8438_3dr_facelift	8438	Hatchback	SEAT Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	HIGH	三门改款后物理分支。	READY
8438_5dr_facelift	8438	Hatchback	SEAT Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	HIGH	五门改款后物理分支。	READY
8439	8439	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8440	8440	Sedan	Volkswagen Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
8441	8441	Sedan	SEAT Córdoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH		READY
8442	8442	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8443	8443	Sedan	Volkswagen Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH		READY
8444	8444	Wagon	Volkswagen Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH		READY
8445	8445	Sedan	Infiniti M Y51	Y51	4	EU-INFINITI-M-Y51-SEDAN-4D-01	HIGH		READY
8446	8446	Hatchback	Kia Cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	HIGH		READY
8447	8447	Hatchback	Kia Cee'd I facelift	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	HIGH		READY
8448	8448	Hatchback	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	HIGH		READY
8449	8449	Hatchback	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	HIGH		READY
8450	8450	Wagon	Kia Cee'd I facelift	ED	5	EU-KIA-CEED-I-ED-WAGON-5D-FACELIFT-01	HIGH		READY
8451	8451	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8452	8452	SUV	Kia Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-5D-01	HIGH		READY
8453_3dr	8453	Hatchback	Volkswagen Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8453_5dr	8453	Hatchback	Volkswagen Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8454	8454	SUV	Kia Sportage III	SL	5	EU-KIA-SPORTAGE-III-SL-SUV-5D-01	HIGH		READY
8456_3dr	8456	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8456_5dr	8456	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8460_3dr	8460	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8460_5dr	8460	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8461_3dr	8461	Hatchback	Volkswagen Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8461_5dr	8461	Hatchback	Volkswagen Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8469	8469	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8470	8470	MPV	Kia Carens II	UN	5	EU-KIA-CARENS-II-UN-MPV-5D-01	HIGH		READY
8471	8471	Hatchback	Opel Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH		READY
8475	8475	Wagon	Volkswagen Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
8476_swb_prefl_h1805	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	MEDIUM	改款前SWB低高度分支。	READY
8476_swb_prefl_h1844	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	MEDIUM	改款前SWB高高度分支。	READY
8476_lwb_2s_prefl_h1810	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	MEDIUM	改款前LWB两座低高度分支。	READY
8476_lwb_2s_prefl_h1836	8476	Van	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	MEDIUM	改款前LWB两座高高度分支。	READY
8476_lwb_5s_prefl_h1802	8476	MPV	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	MEDIUM	改款前LWB五座低高度分支。	READY
8476_lwb_5s_prefl_h1826	8476	MPV	Renault Kangoo II	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	MEDIUM	改款前LWB五座高高度分支。	READY
8476_swb_facelift_h1805	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	MEDIUM	改款后SWB低高度分支。	READY
8476_swb_facelift_h1844	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	MEDIUM	改款后SWB高高度分支。	READY
8476_lwb_2s_facelift_h1810	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	MEDIUM	改款后LWB两座低高度分支。	READY
8476_lwb_2s_facelift_h1836	8476	Van	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	MEDIUM	改款后LWB两座高高度分支。	READY
8476_lwb_5s_facelift_h1802	8476	MPV	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	MEDIUM	改款后LWB五座低高度分支。	READY
8476_lwb_5s_facelift_h1826	8476	MPV	Renault Kangoo II facelift	X61		EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	MEDIUM	改款后LWB五座高高度分支。	READY
8477	8477	Hatchback	Renault Laguna III	B91	5	EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	HIGH		READY
8478	8478	Wagon	Renault Laguna III	K91	5	EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	HIGH		READY
8484	8484	Van	Peugeot Partner II	B9	4	EU-PEUGEOT-PARTNER-II-B9-VAN-L1H1-01	HIGH	L1H1箱式车物理外廓。	READY
8486	8486	SUV	Cadillac Escalade III	GMT900	5	EU-CADILLAC-ESCALADE-III-HYBRID-SUV-5D-01	HIGH		READY
8487	8487	Sedan	Volkswagen Vento I	1H2	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
8488	8488	Wagon	Cadillac BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
8489	8489	Wagon	Cadillac BLS		5	EU-CADILLAC-BLS-WAGON-5D-01	HIGH		READY
8490	8490	Sedan	Cadillac STS I	GMX295	4	EU-CADILLAC-STS-I-SEDAN-4D-01	HIGH		READY
8491	8491	Sedan	Cadillac BLS		4	EU-CADILLAC-BLS-SEDAN-4D-01	HIGH		READY
8492_pre94	8492	Coupe	Chevrolet Beretta I	L	2	EU-CHEVROLET-BERETTA-I-COUPE-2D-PRE94-01	HIGH	1991-1993外廓分支。	READY
8492_94on	8492	Coupe	Chevrolet Beretta I	L	2	EU-CHEVROLET-BERETTA-I-COUPE-2D-94ON-01	HIGH	1994-1996外廓分支。	READY
8493	8493	Sedan	Chevrolet Corsica I	L	4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH		READY
8494	8494	Sedan	Chevrolet Corsica I	L	4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7701-7800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-626-V-GF-HATCHBACK-5D-01	4575	1710	1430	Automobile-Catalog 1997 Mazda 626 2.0 5-Door Europe	https://www.automobile-catalog.com/car/1997/1665305/mazda_626_2_0_5-door.html
EU-MERCEDES-BENZ-CLK-C208-COUPE-2D-01	4567	1722	1371	Mercedes-Benz Public Archive CLK 200 C208	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-200.xhtml?oid=4562
EU-SEAT-INCA-9K-VAN-01	4207	1696	1836	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-A-KLASSE-W168-HATCHBACK-5D-01	3575	1719	1575	Automobile-Catalog 1998 Mercedes-Benz A 160	https://www.automobile-catalog.com/car/1998/1532465/mercedes-benz_a_160.html
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-H2130-01	4655	1998	2130	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-HIGHROOF-4X4-01	4655	1998	2465	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-4X4-01	5005	1998	2470	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-406-COUPE-2D-01	4615	1780	1352	Autozine Peugeot 406 Coupe technical specifications	https://www.autozine.org/Archive/Peugeot/old/406.html
EU-PEUGEOT-306-PHASE-II-WAGON-5D-01	4338	1689	1415	Automobile-Catalog 1997 Peugeot 306 Break 1.4i XR	https://www.automobile-catalog.com/car/1997/2612015/peugeot_306_break_1_4i_xr.html
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-306-SEDAN-7B-FACELIFT-01	4267	1689	1386	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-PEUGEOT-306-CABRIO-7D-FACELIFT-01	4179	1689	1356	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-BUICK-SKYLARK-V-SEDAN-4D-PRE82-01	4620	1720	1359	Automobile-Catalog 1980 Buick Skylark Sedan 2.8L V6	https://www.automobile-catalog.com/car/1980/304310/buick_skylark_sedan_2_8l_v-6.html
EU-BUICK-SKYLARK-V-SEDAN-4D-1982-01	4600	1750	1364	Automobile-Catalog 1982 Buick Skylark Sedan 2.8L V6 automatic	https://www.automobile-catalog.com/car/1982/305345/buick_skylark_sedan_2_8l_v-6_automatic.html
EU-BUICK-CENTURY-IV-SEDAN-4D-01	4978	1834	1397	Automobile-Catalog 1979 Buick Century Limited Sedan	https://www.automobile-catalog.com/car/1979/179855/buick_century_limited_sedan_4_9l_v-8_automatic.html
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	4028	1698	1368	Automobile-Catalog 1997 Renault Mégane Cabriolet 2.0 16V	https://www.automobile-catalog.com/car/1997/2946725/renault_megane_cabriolet_2_0_16v.html
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	4082	1698	1368	Carfolio 2001 Renault Mégane Cabriolet 2.0 16V	https://www.carfolio.com/renault-megane-cabriolet-2.0-16v-254122
EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	5202	1801	1379	Automobile-Catalog 1980 Cadillac Seville Elegante 5.7L Diesel	https://www.automobile-catalog.com/car/1980/47300/cadillac_seville_elegante_5_7l_v-8_diesel.html
EU-RENAULT-MEGANE-SCENIC-I-MPV-01	4134	1719	1675	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-LAGUNA-I-K56-WAGON-01	4620	1752	1448	Automobile-Catalog 1997 Renault Laguna Wagon 3.0i V6 24V	https://www.automobile-catalog.com/car/1997/2945840/renault_laguna_wagon_3_0i_v6_24v.html
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-HYUNDAI-H1-STAREX-I-MPV-01	4695	1820	1885	Automobile-Catalog 1998 Hyundai H-1 Starex 2.4i; Automobile-Catalog 1998 Hyundai H-1 Starex 2.5 TD	https://www.automobile-catalog.com/car/1998/1167755/hyundai_h-1_starex_2_4i_automatic.html;https://www.automobile-catalog.com/car/1998/1167785/hyundai_h-1_starex_2_5_td.html
EU-VOLVO-C70-I-P80-COUPE-2D-01	4720	1820	1410	Auto-Data Volvo C70 Coupe 2.3 T5	https://www.auto-data.net/en/volvo-c70-coupe-2.3-20v-t5-240hp-9509
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-SEAT-CORDOBA-I-6K5-WAGON-PREFL-01	4142	1640	1426	Automobile-Catalog 1998 SEAT Córdoba Vario 1.4	https://www.automobile-catalog.com/car/1998/3066530/seat_cordoba_vario_1_4.html
EU-SEAT-CORDOBA-I-6K5-WAGON-FACELIFT-01	4163	1640	1433	Automobile-Catalog 2001 SEAT Córdoba Vario 1.4 16V	https://www.automobile-catalog.com/car/2001/3070850/seat_cordoba_vario_1_4_16v_75.html
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433	Auto-Data Volkswagen Polo III Variant	https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n-generation-1858
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-INFINITI-M-Y51-SEDAN-4D-01	4945	1845	1500	Automobile-Catalog 2011 Infiniti M35h GT Hybrid	https://www.automobile-catalog.com/car/2011/2169110/infiniti_m35h_gt_hybrid.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-FACELIFT-01	4250	1790	1450	Automobile-Catalog 2010 Kia Pro_Cee'd 1.6 CVVT	https://www.automobile-catalog.com/car/2010/1359935/kia_pro_cee_d_1_6_cvvt_ex.html
EU-KIA-CEED-I-ED-HATCHBACK-5D-FACELIFT-01	4260	1790	1480	Automobile-Catalog 2010 Kia Cee'd 1.6 CVVT	https://www.automobile-catalog.com/car/2010/1362125/kia_cee_d_1_1_6_cvvt_automatic.html
EU-KIA-CEED-I-ED-WAGON-5D-FACELIFT-01	4490	1790	1525	Automobile-Catalog 2010 Kia Cee'd SW 1.6 CRDi 128	https://www.automobile-catalog.com/car/2010/1361540/kia_cee_d_sw_1_6_crdi_128_spirit_dpf.html
EU-KIA-CARENS-II-UN-MPV-5D-01	4545	1820	1650	Automobile-Catalog 2009 Kia Carens 2.0 VGT 7-Seat	https://www.automobile-catalog.com/car/2009/1368215/kia_carens_2_0_vgt_7-seat.html
EU-KIA-SPORTAGE-III-SL-SUV-5D-01	4440	1855	1635	Automobile-Catalog 2010 Kia Sportage 2.0 CRDi AWD	https://www.automobile-catalog.com/car/2010/1364000/kia_sportage_2_0_crdi_vision_awd.html
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-8673
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439	Auto-Data Volkswagen Golf IV 1.9 TDI	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-8673
EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	3740	1680	1590	Automobile-Catalog 2010 Opel Agila 1.2	https://www.automobile-catalog.com/car/2010/2529500/opel_agila_1_2.html
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826	Renault Kangoo Z.E. official dimensions	https://www.press.renault.co.uk/assets/documents/original/10710-KangooVanZEdimensions.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826	Renault Kangoo Express & Z.E. official brochure	https://www.renault.sc/CountriesData/Seychelles/images/cars/kangooExpress/brochure/Brochure_Kangoo.pdf
EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	4695	1811	1445	Automobile-Catalog 2008 Renault Laguna 2.0 dCi 150	https://www.automobile-catalog.com/car/2008/2957885/renault_laguna_2_0_dci_150_fap.html
EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	4803	1811	1445	Automobile-Catalog 2009 Renault Laguna Grandtour 3.5 V6	https://www.automobile-catalog.com/car/2009/2958230/renault_laguna_wagon_grandtour_3_5_v6.html
EU-PEUGEOT-PARTNER-II-B9-VAN-L1H1-01	4380	1810	1801	Peugeot Partner 2008 official brochure; PEUGEOT Partner L1 homologation record	https://autocatalogarchive.com/wp-content/uploads/2023/08/Peugeot-Partner-2008-AU.pdf;https://jomologia.hr/Detalji?id=35220&redniBroj=0
EU-CADILLAC-ESCALADE-III-HYBRID-SUV-5D-01	5143	2007	1887	Automobile-Catalog 2012 Cadillac Escalade Hybrid 4WD	https://www.automobile-catalog.com/car/2012/1614005/cadillac_escalade_hybrid_4wd.html
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-CADILLAC-BLS-WAGON-5D-01	4716	1752	1543	Automobile-Catalog 2008 Cadillac BLS Wagon 2.8 T V6 AWD	https://www.automobile-catalog.com/car/2008/1200440/cadillac_bls_wagon_2_8_t_v6_awd_sport_luxury.html
EU-CADILLAC-STS-I-SEDAN-4D-01	4986	1844	1463	Automobile-Catalog 2010 Cadillac STS 3.6 V6	https://www.automobile-catalog.com/car/2010/336755/cadillac_sts_3_6_v6.html
EU-CADILLAC-BLS-SEDAN-4D-01	4680	1752	1471	Task-provided cross-batch confirmed DIMENSION_GROUP index	sandbox:/mnt/data/all_7701-7800_cross_batch_dimension_index_source.txt
EU-CHEVROLET-BERETTA-I-COUPE-2D-PRE94-01	4755	1727	1344	Automobile-Catalog 1991 Chevrolet Beretta 2.2L	https://www.automobile-catalog.com/make/chevrolet_usa/beretta/beretta/1991.html
EU-CHEVROLET-BERETTA-I-COUPE-2D-94ON-01	4757	1727	1351	Automobile-Catalog 1994 Chevrolet Beretta 2.2 Europe export	https://www.automobile-catalog.com/car/1994/470720/chevrolet_beretta_2_2.html
EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	4658	1732	1367	Automobile-Catalog 1991 Chevrolet Corsica Sedan 2.2L; Automobile-Catalog 1994 Chevrolet Corsica Sedan 2.2L	https://www.automobile-catalog.com/car/1991/470180/chevrolet_corsica_sedan_2_2l.html;https://www.automobile-catalog.com/car/1994/470675/chevrolet_corsica_sedan_2_2l_automatic.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7701-7800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.bremboparts.com/asiapacific/en/catalogue/peugeot-boxer-bus-230p-2-5-tdi-4x4/000008391-1?utm_source=chatgpt.com "Pads and Discs for PEUGEOT BOXER Bus (230P) 2.5 TDI 4x4"
[2]: https://catalogonuevo.icerbrakes.com/Vehiculo/Details?idTipoVehiculo=2&idVehiculo=8484&utm_source=chatgpt.com "PARTNER II / GRAND RAID / RANCH - 1.6 details"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7701-7800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7701-7800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9735 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2984 行）

