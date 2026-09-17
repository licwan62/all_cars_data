# 任务：all 第 5001-5100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0051__7cab253e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5001-5100 行

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
all 第 5001-5100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5001-5100_ktype_dimension_mapping_final.tsv
- all_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425
EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330
EU-ALFA-ROMEO-GTV-116-COUPE-FACELIFT-01	4260	1664	1330
EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	4250	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	4120	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	4245	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	4258	1630	1290
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390
EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	3750	1460	1730
EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	3390	1395	1730
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	3370	1395	1870
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
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
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Mondeo iv	2.0 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	107	145	Jul 2009	Jan 2015	2024-03-01	5152
Fiat	Brava	1.8 GT 16V	Schrägheck	Frontantrieb	Benzin	83	113	Oct 1995	Aug 2001	2024-03-01	5153
Fiat	Bravo i	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1995	Oct 2001	2024-03-01	5154
Fiat	Bravo i	1.6 16V	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1995	Oct 2001	2024-03-01	5155
Fiat	Bravo i	1.8 GT	Schrägheck	Frontantrieb	Benzin	83	113	Oct 1995	Oct 2001	2024-03-01	5156
Fiat	Bravo i	2.0 HGT 20V	Schrägheck	Frontantrieb	Benzin	108	147	Oct 1995	Jul 1998	2024-03-01	5157
Fiat	Ducato	1.9 D Combinato	Bus	Frontantrieb	Diesel	51	69	Jun 1995	Apr 2002	2024-03-01	5158
Alfa Romeo	145	2.0 16V T.s.	Schrägheck	Frontantrieb	Benzin	110	150	Oct 1995	Jan 2001	2024-03-01	5159
Alfa Romeo	146	2.0 16V T.s.	Schrägheck	Frontantrieb	Benzin	110	150	Oct 1995	Jan 2001	2024-03-01	5160
Alfa Romeo	Gtv	2.0 V6 Turbo	Coupe	Frontantrieb	Benzin	148	202	Jun 1995	Sep 1998	2024-03-01	5161
Alfa Romeo	Gtv	2.0 T.spark 16V	Coupe	Frontantrieb	Benzin	110	150	Jun 1995	Oct 2005	2024-03-01	5162
Alfa Romeo	Spider	3.0 V6	Cabriolet	Frontantrieb	Benzin	141	192	Jun 1995	Apr 2005	2024-03-01	5163
Alfa Romeo	Spider	2.0 T.spark 16V	Cabriolet	Frontantrieb	Benzin	110	150	Jun 1995	Apr 2005	2024-03-01	5164
Opel	Vectra b	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1995	Apr 2002	2024-03-01	5165
Opel	Vectra b	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	74	100	Oct 1995	Apr 2002	2024-03-01	5166
Opel	Vectra b	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	85	115	Oct 1995	Sep 2000	2024-03-01	5167
Opel	Vectra b	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	100	136	Sep 1995	Jun 2000	2024-03-01	5168
Opel	Vectra b	2.5 I V6	Stufenheck	Frontantrieb	Benzin	125	170	Oct 1995	Sep 2000	2024-03-01	5169
Opel	Vectra b	1.7 TD	Stufenheck	Frontantrieb	Diesel	60	82	Oct 1995	Dec 1998	2024-03-01	5170
Lancia	Zeta	2.0 Turbo	Großraumlimousine	Frontantrieb	Benzin	108	147	May 1995	Sep 2002	2024-03-01	5171
Ford	Escort vi	1.8 16V	Schrägheck	Frontantrieb	Benzin	85	115	Jan 1995	Oct 1998	2024-03-01	5172
Ford	Escort vi	1.8 Turbo D	Schrägheck	Frontantrieb	Diesel	51	70	Dec 1995	Oct 1998	2024-03-01	5173
Ford	Escort vi	1.8 16V	Stufenheck	Frontantrieb	Benzin	85	115	Jan 1995	Feb 1999	2024-03-01	5174
Ford	Escort vi	1.8 Turbo D	Stufenheck	Frontantrieb	Diesel	51	70	Dec 1995	Feb 1999	2024-03-01	5175
Ford	Escort vi turnier	1.8 16V	Kombi	Frontantrieb	Benzin	85	115	Jan 1995	Feb 1999	2024-03-01	5176
Ford	Escort vi turnier	1.8 Turbo D	Kombi	Frontantrieb	Diesel	51	70	Dec 1995	Feb 1999	2024-03-01	5177
Ford	Escort vi	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1995	Oct 1998	2024-03-01	5178
Piaggio	Porter	1.3 LPG	Kasten	Heckantrieb	Benzin/Autogas (LPG)	48	64	Jun 1998	Dec 2011	2024-03-01	5179
Piaggio	Porter	1.3 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	48	64	Jun 1998	Dec 2011	2024-03-01	5180
Ford	Escort vi	1.6 16V	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1995	Oct 1998	2024-03-01	5181
Ford	Escort vi	RS Cosworth 4X4	Schrägheck	Allrad	Benzin	162	220	Feb 1995	Oct 1998	2024-03-01	5182
Ford	Escort vi	1.8 TD	Schrägheck	Frontantrieb	Diesel	66	90	Jan 1995	Oct 1998	2024-03-01	5183
Ford	Escort vi	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Jan 1995	Feb 1999	2024-03-01	5184
Ford	Escort vi turnier	1.4	Kombi	Frontantrieb	Benzin	55	75	Jan 1995	Feb 1999	2024-03-01	5185
Ford	Escort vi turnier	1.6 16V	Kombi	Frontantrieb	Benzin	66	90	Jan 1995	Feb 1999	2024-03-01	5186
Ford	Escort vi turnier	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Jan 1995	Feb 1999	2024-03-01	5187
Ford	Escort vi	1.4	Cabriolet	Frontantrieb	Benzin	55	75	Feb 1995	Aug 1998	2024-03-01	5188
Ford	Escort vi	1.6 16V Xr3i	Cabriolet	Frontantrieb	Benzin	65	88	Feb 1995	Dec 1996	2024-03-01	5189
Ford	Escort vi	1.6 16V Xr3i	Cabriolet	Frontantrieb	Benzin	66	90	Feb 1995	Sep 1999	2024-03-01	5190
Ford	Fiesta iv	1.3 I	Schrägheck	Frontantrieb	Benzin	37	50	Aug 1995	Jan 2002	2024-03-01	5191
Ford	Fiesta iv	1.3 I	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1995	Jan 2002	2024-03-01	5192
Ford	Fiesta iv	1.25 I 16V	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1995	Jan 2002	2024-03-01	5193
Ford	Fiesta iv	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Aug 1995	Apr 2000	2024-03-01	5194
Ford USA	Windstar	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	109	148	Mar 1995	Feb 1999	2024-03-01	5195
Honda	Civic vi hatchback	1.4 I	Schrägheck	Frontantrieb	Benzin	55	75	Nov 1995	Feb 2001	2024-03-01	5196
Honda	Civic vi hatchback	1.4 I S	Schrägheck	Frontantrieb	Benzin	66	90	Nov 1995	Feb 2001	2024-03-01	5197
Honda	Civic vi hatchback	1.6 I	Schrägheck	Frontantrieb	Benzin	84	114	Nov 1995	Feb 2001	2024-03-01	5198
Honda	Civic vi hatchback	1.5 I	Schrägheck	Frontantrieb	Benzin	84	114	Nov 1995	Feb 2001	2024-03-01	5199
Honda	Civic vi hatchback	1.6 VTI	Schrägheck	Frontantrieb	Benzin	118	160	Nov 1995	Feb 2001	2024-03-01	5200
Honda	Civic vi	1.4 I	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1995	Feb 2001	2024-03-01	5201
Honda	Civic vi	1.5 I	Stufenheck	Frontantrieb	Benzin	84	114	Nov 1995	Feb 2001	2024-03-01	5202
Honda	Civic vi	1.6 VTI	Stufenheck	Frontantrieb	Benzin	118	160	Nov 1995	Feb 2001	2024-03-01	5203
Hyundai	Lantra ii	1.6 I	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1995	Sep 2000	2024-03-01	5204
Hyundai	Lantra ii	1.6 16V	Stufenheck	Frontantrieb	Benzin	84	114	Nov 1995	Sep 2000	2024-03-01	5205
Hyundai	Lantra ii	1.8 16V	Stufenheck	Frontantrieb	Benzin	94	128	Nov 1995	Sep 2000	2024-03-01	5206
Lada	Priora	1.6	Kombi	Frontantrieb	Benzin	72	98	Oct 2009	Dec 2015	2024-03-01	5207
Proton	Persona 400	413 Glsi	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1994	Jan 2000	2024-03-01	5208
Proton	Persona 400	415 Gli/glsi	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1994	Jul 2000	2024-03-01	5209
Proton	Persona 400	416 Glxi	Schrägheck	Frontantrieb	Benzin	83	113	Jan 1994	Jul 2000	2024-03-01	5210
Proton	Persona 400	413	Stufenheck	Frontantrieb	Benzin	55	75	Jan 1994	Jun 2003	2024-03-01	5211
Proton	Persona 400	415 Gli/glsi	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1994	Jul 2000	2024-03-01	5212
Proton	Persona 400	416 Glxi	Stufenheck	Frontantrieb	Benzin	83	113	Jan 1994	Jul 2000	2024-03-01	5213
Subaru	Justy ii	1.3 GX 4X4	Schrägheck	Allrad	Benzin	50	68	Oct 1995	Nov 2003	2024-03-01	5214
Mitsubishi	Eclipse ii	2000 GS 16V	Coupe	Frontantrieb	Benzin	107	146	Dec 1995	Apr 1999	2024-03-01	5215
Mitsubishi	Carisma	1.8 MSX - 16V	Schrägheck	Frontantrieb	Benzin	103	140	Jul 1995	Jul 1997	2024-03-01	5216
Mitsubishi	Carisma	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1995	Jun 2006	2024-03-01	5217
Mitsubishi	Carisma	1.8	Schrägheck	Frontantrieb	Benzin	85	116	Jul 1995	Jul 1997	2024-03-01	5218
Nissan	Almera i hatchback	1.4 S, GX, LX	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1995	Mar 2000	2024-03-01	5219
Nissan	Almera i hatchback	1.4	Schrägheck	Frontantrieb	Benzin	64	87	Sep 1995	Mar 2000	2024-03-01	5220
Nissan	Almera i hatchback	1.6 SR, SLX	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1995	Mar 2000	2024-03-01	5221
Nissan	Almera i hatchback	1.6	Schrägheck	Frontantrieb	Benzin	73	99	Sep 1995	Mar 2000	2024-03-01	5222
Nissan	Almera i hatchback	2.0 D	Schrägheck	Frontantrieb	Diesel	55	75	Nov 1995	Mar 2000	2024-03-01	5223
Nissan	Almera i	1.4 Gx,lx	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1995	Jul 2000	2024-03-01	5224
Nissan	Almera i	1.4	Stufenheck	Frontantrieb	Benzin	64	87	Sep 1995	Jul 2000	2024-03-01	5225
Nissan	Almera i	1.6 SLX	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1995	Jul 2000	2024-03-01	5226
Nissan	Almera i	1.6	Stufenheck	Frontantrieb	Benzin	73	99	Sep 1995	Jul 2000	2024-03-01	5227
Nissan	Almera i	2.0 D	Stufenheck	Frontantrieb	Diesel	55	75	Nov 1995	Jul 2000	2024-03-01	5228
Peugeot	406	1.6	Stufenheck	Frontantrieb	Benzin	65	88	Nov 1995	May 2004	2024-03-01	5229
Peugeot	406	1.8 16V	Stufenheck	Frontantrieb	Benzin	81	110	Nov 1995	Oct 2000	2024-03-01	5230
Peugeot	406	2.0 16V	Stufenheck	Frontantrieb	Benzin	97	132	Nov 1995	May 2004	2024-03-01	5231
Porsche	911	3.8 Carrera	Cabriolet	Heckantrieb	Benzin	221	301	Aug 1995	Sep 1997	2024-03-01	5232
Porsche	911	3.8 Carrera 4	Cabriolet	Allrad	Benzin	221	301	Aug 1995	Sep 1997	2024-03-01	5233
Porsche	911	3.8 Carrera 4	Coupe	Allrad	Benzin	221	300	Aug 1995	Sep 1997	2024-03-01	5234
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	210	286	Aug 1995	Sep 1997	2024-03-01	5235
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	210	286	Aug 1995	Sep 1997	2024-03-01	5236
Porsche	911	3.6 Carrera	Targa	Heckantrieb	Benzin	210	286	Aug 1995	Sep 1997	2024-03-01	5237
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	210	286	Aug 1995	Sep 1997	2024-03-01	5238
Porsche	911	3.6 Turbo GT2 4	Coupe	Allrad	Benzin	316	430	Aug 1995	Sep 1997	2024-03-01	5239
Renault	Laguna i	2.0 16V	Schrägheck	Frontantrieb	Benzin	102	139	Jun 1995	Mar 2001	2024-03-01	5240
Citroën	C-Zero	C-zero	Schrägheck	Heckantrieb	Elektro	35	48	Oct 2010	-	2024-03-01	5241
Renault	Laguna i	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1995	Mar 2001	2024-03-01	5242
Renault	Laguna i	1.8	Schrägheck	Frontantrieb	Benzin	69	94	Aug 1995	Mar 2001	2024-03-01	5243
Citroën	C8	2.0 HDI 165	Großraumlimousine	Frontantrieb	Diesel	120	163	Mar 2006	-	2024-03-01	5244
Renault	Laguna i grandtour	2.0 16V	Kombi	Frontantrieb	Benzin	102	139	Sep 1995	Mar 2001	2024-03-01	5245
Renault	Laguna i grandtour	1.8	Kombi	Frontantrieb	Benzin	66	90	Sep 1995	Mar 2001	2024-03-01	5246
Renault	Laguna i grandtour	1.8	Kombi	Frontantrieb	Benzin	69	94	Sep 1995	Mar 2001	2024-03-01	5247
Renault	Laguna i grandtour	2	Kombi	Frontantrieb	Benzin	83	113	Sep 1995	Mar 2001	2024-03-01	5248
Piaggio	Quargo	0.7 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	13	18	Jan 2004	-	2024-03-01	5249
Renault	Laguna i grandtour	2.2 D	Kombi	Frontantrieb	Diesel	61	83	Sep 1995	Mar 2001	2024-03-01	5250
Renault	Megane i	1.4 E	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1996	Aug 2003	2024-03-01	5251


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类处理 Ktype `5152–5171`。Mondeo IV 三厢、Fiat Brava/Bravo I、Alfa Romeo 916 Spider、Vectra B 改款前后等尺寸组已闭合；Fiat Bravo HGT 因保险杠造型产生长度差异，独立建组。([汽车目录][1])
* 已直接复用累计表中的 Alfa Romeo 145 三门和 146 五门尺寸组，没有重复输出已有尺寸事实。
* Opel Vectra B 三厢确认存在改款前后长度差异：改款前 `4477 mm`，1999 改款后 `4495 mm`，相关跨改款 Ktype 已拆分。([汽车目录][2])
* Alfa Romeo Spider 916 的 Phase 3 改款改变了车长和车宽，2.0 Twin Spark 跨改款记录已拆分；GTV 2.0 Twin Spark 的早期高度资料仍有冲突，暂不猜测派生。([汽车目录][3])
* Fiat Ducato 230P Combinato 尚未确认轴距和车顶分支；Lancia Zeta 2.0 Turbo 的直接来源存在 `4454/4470 mm` 长度冲突，均保持 PENDING。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：20
* 已闭合 Ktype：17
* READY 映射行：23
* PENDING 映射行：3
* 本轮首次创建尺寸组：9
* 本轮复用已有尺寸组：2
* 尚未开始处理 Ktype：80
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5152	5152	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-BA7-SEDAN-01	HIGH	BA7四门三厢外廓。	READY
5153	5153	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-5D-01	HIGH	182五门Brava外廓。	READY
5154	5154	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5155	5155	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5156	5156	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5157	5157	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-HGT-01	HIGH	HGT保险杠外廓与标准版不同。	READY
5158	5158	MPV	Ducato II	230P			LOW	候选为230P Combinato标准车身，需确认轴距和车顶。	PENDING: Combinato未明确轴距及车顶，无法唯一命中现有230P Bus尺寸组
5159	5159	Hatchback	145 (930)	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门145外廓。	READY
5160	5160	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH	930五门146外廓。	READY
5161	5161	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-V6TB-01	HIGH	2.0 V6 Turbo的Phase 1/2外廓。	READY
5162	5162	Coupe	GTV (916)	916	2		LOW	跨Phase 1/2与Phase 3，早期高度资料尚未闭合。	PENDING: 2.0 Twin Spark跨改款且早期高度来源存在冲突
5163	5163	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	MEDIUM	141kW 3.0 V6对应改款前外廓。	READY
5164_prefl	5164	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	MEDIUM	Phase 1/2改款前外廓。	READY
5164_facelift	5164	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	MEDIUM	Phase 3前脸及保险杠外廓。	READY
5165_prefl	5165	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999改款前三厢外廓。	READY
5165_facelift	5165	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999改款后三厢外廓。	READY
5166_prefl	5166	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999改款前三厢外廓。	READY
5166_facelift	5166	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999改款后三厢外廓。	READY
5167_prefl	5167	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999改款前三厢外廓。	READY
5167_facelift	5167	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999改款后三厢外廓。	READY
5168_prefl	5168	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999改款前三厢外廓。	READY
5168_facelift	5168	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999改款后三厢外廓。	READY
5169_prefl	5169	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999改款前三厢外廓。	READY
5169_facelift	5169	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999改款后三厢外廓。	READY
5170	5170	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	生产期止于1999改款前。	READY
5171	5171	MPV	Zeta	220	5		LOW	需解决早期2.0 Turbo外廓长度口径冲突。	PENDING: 精确车型的可靠来源给出不同车长，暂不创建尺寸组
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-IV-BA7-SEDAN-01	4844	1886	1500	Automobile-Catalog 2007 Ford Mondeo 4-dr 2.0 Titanium	https://www.automobile-catalog.com/car/2007/977510/ford_mondeo_4-dr_2_0_titanium.html
EU-FIAT-BRAVA-182-HATCHBACK-5D-01	4187	1741	1420	Automobile-Catalog 1996 Fiat Brava 1.8 16V EL	https://www.automobile-catalog.com/car/1996/721100/fiat_brava_1_8_16v_el.html
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	4025	1755	1420	Automobile-Catalog 1996 Fiat Bravo 1.8 16V GT	https://www.automobile-catalog.com/car/1996/720950/fiat_bravo_1_8_16v_gt.html
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-HGT-01	4031	1755	1420	Automobile-Catalog 1997 Fiat Bravo 2.0 20V HGT	https://www.automobile-catalog.com/car/1997/720995/fiat_bravo_2_0_20v_hgt.html
EU-ALFA-ROMEO-GTV-916-COUPE-V6TB-01	4285	1780	1318	Automobile-Catalog 1995 Alfa Romeo GTV 2.0 V6 TB	https://www.automobile-catalog.com/car/1995/218390/alfa_romeo_gtv_2_0_v6_tb.html
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	4285	1780	1315	Automobile-Catalog 1995 Alfa Romeo Spider 2.0 Twin Spark 16V	https://www.automobile-catalog.com/car/1995/218420/alfa_romeo_spider_2_0_twin_spark_16v.html
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	4299	1776	1315	Automobile-Catalog 2004 Alfa Romeo Spider 2.0 Twin Spark 16V	https://www.automobile-catalog.com/car/2004/218690/alfa_romeo_spider_2_0_twin_spark_16v.html
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425	Automobile-Catalog 1996 Opel Vectra 4d 1.6	https://www.automobile-catalog.com/car/1996/2476805/opel_vectra_4d_1_6.html
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425	Automobile-Catalog 1999 Opel Vectra 4d 1.6 16V	https://www.automobile-catalog.com/car/1999/2478665/opel_vectra_4d_1_6_16v.html
```

## 下一步优先处理

1. 先闭合 Ktype `5158` 的 Ducato 230P Combinato 轴距和车顶分支。
2. 解决 Ktype `5162` 的 GTV 2.0 Twin Spark Phase 1/2 高度差异，再决定是否拆为 Phase 1、Phase 2、Phase 3 三行。
3. 解决 Ktype `5171` 的 Lancia Zeta 2.0 Turbo 长度来源冲突。
4. 随后按 Escort VI、Fiesta IV、Civic VI、Lantra II 等车身簇批量处理 Ktype `5172–5206`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/977510/ford_mondeo_4-dr_2_0_titanium.html?utm_source=chatgpt.com "2007 Ford Mondeo (4-dr) 2.0 Titanium (man. 5)"
[2]: https://www.automobile-catalog.com/car/1996/2476805/opel_vectra_4d_1_6.html?utm_source=chatgpt.com "1996 Opel Vectra (4d) 1.6 Specs Review (55 kW / 75 ..."
[3]: https://www.automobile-catalog.com/car/1995/218420/alfa_romeo_spider_2_0_twin_spark_16v.html?utm_source=chatgpt.com "1995 Alfa Romeo Spider 2.0 Twin Spark 16V (man. 5)"
[4]: https://www.automobile-catalog.com/car/1995/1383800/lancia_zeta_turbo.html?utm_source=chatgpt.com "1995 Lancia Zeta Turbo Specs Review (108 kW / 147 PS ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5001-5100_ktype_dimension_mapping_final.tsv
- all_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已消除上一轮 3 个阻塞项：Ducato 230P Combinato 复用既有短轴 Bus 组；GTV 916 按 2003 年外观改款拆分并把发动机化的临时组 ID 修正为物理车身组；Lancia Zeta 采用可确认不含后视镜宽度的 `4470 × 1834 × 1714 mm`。([dieversicherer.de][1])
* 已批量完成 Escort VI、Piaggio Porter、Fiesta IV、欧洲版 Windstar I、Civic VI Fastback/Sedan。Fiesta 按 1999 年 Phase II 外廓变化拆分；Windstar 按 1998 年外观修订拆分；Civic VI Sedan 按中期改款拆分。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已处理并 READY：52
* 尚未处理：48
* READY 映射行：82
* 当前已引用并闭合尺寸组：32
* 本轮首次创建或修正尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5158	5158	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	230P Combinato短轴标准顶外廓。	READY
5161	5161	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	916改款前双门Coupe外廓。	READY
5162_prefl	5162	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	MEDIUM	2003年外观改款前分支。	READY
5162_facelift	5162	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	MEDIUM	2003年Pininfarina前脸改款分支。	READY
5171	5171	MPV	Zeta I	220	5	EU-LANCIA-ZETA-220-MPV-01	HIGH	220系列五门MPV外廓。	READY
5172_3dr	5172	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback物理分支。	READY
5172_5dr	5172	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback物理分支。	READY
5173_3dr	5173	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback物理分支。	READY
5173_5dr	5173	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback物理分支。	READY
5174	5174	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5175	5175	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5176	5176	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5177	5177	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5178_3dr	5178	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback物理分支。	READY
5178_5dr	5178	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback物理分支。	READY
5179	5179	Van	Porter I		5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	封闭式Van外廓。	READY
5180_pickup	5180	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货台Pickup分支。	READY
5180_chassis_long	5180	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长轴底盘车分支。	READY
5181_3dr	5181	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback物理分支。	READY
5181_5dr	5181	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback物理分支。	READY
5182	5182	Hatchback	Escort RS Cosworth		3	EU-FORD-ESCORT-RS-COSWORTH-HATCHBACK-3D-01	HIGH	RS Cosworth宽体及空气动力套件外廓。	READY
5183_3dr	5183	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback物理分支。	READY
5183_5dr	5183	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback物理分支。	READY
5184	5184	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5185	5185	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5186	5186	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5187	5187	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5188	5188	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5189	5189	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5190	5190	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5191_3dr_prefl	5191	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门且1999年改款前分支。	READY
5191_3dr_facelift	5191	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门且1999年改款后分支。	READY
5191_5dr_prefl	5191	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门且1999年改款前分支。	READY
5191_5dr_facelift	5191	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门且1999年改款后分支。	READY
5192_3dr_prefl	5192	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门且1999年改款前分支。	READY
5192_3dr_facelift	5192	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门且1999年改款后分支。	READY
5192_5dr_prefl	5192	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门且1999年改款前分支。	READY
5192_5dr_facelift	5192	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门且1999年改款后分支。	READY
5193_3dr_prefl	5193	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门且1999年改款前分支。	READY
5193_3dr_facelift	5193	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门且1999年改款后分支。	READY
5193_5dr_prefl	5193	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门且1999年改款前分支。	READY
5193_5dr_facelift	5193	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门且1999年改款后分支。	READY
5194_3dr_prefl	5194	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门且1999年改款前分支。	READY
5194_3dr_facelift	5194	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门且1999年改款后分支。	READY
5194_5dr_prefl	5194	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门且1999年改款前分支。	READY
5194_5dr_facelift	5194	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门且1999年改款后分支。	READY
5195_prefl	5195	MPV	Windstar I		4	EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	MEDIUM	欧洲出口版1998年外观修订前分支。	READY
5195_facelift	5195	MPV	Windstar I		4	EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	MEDIUM	欧洲出口版1998年外观修订分支。	READY
5196	5196	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5197	5197	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5198	5198	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5199	5199	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5200	5200	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5201_prefl	5201	Sedan	Civic VI	EJ9	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan中期改款前分支。	READY
5201_facelift	5201	Sedan	Civic VI	EJ9	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan中期改款后分支。	READY
5202_prefl	5202	Sedan	Civic VI	EK3	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan中期改款前分支。	READY
5202_facelift	5202	Sedan	Civic VI	EK3	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan中期改款后分支。	READY
5203_prefl	5203	Sedan	Civic VI	EK4	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan中期改款前分支。	READY
5203_facelift	5203	Sedan	Civic VI	EK4	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan中期改款后分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318	Automobile-Catalog 2001 Alfa Romeo GTV 2.0 Twin Spark 16V; Automobile-Catalog 1995 Alfa Romeo GTV 2.0 V6 TB	https://www.automobile-catalog.com/car/2001/218450/alfa_romeo_gtv_2_0_twin_spark_16v.html;https://www.automobile-catalog.com/car/1995/218390/alfa_romeo_gtv_2_0_v6_tb.html
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318	Automobile-Catalog 2003 Alfa Romeo GTV 2.0 JTS 16V	https://www.automobile-catalog.com/car/2003/218660/alfa_romeo_gtv_2_0_jts_16v.html
EU-LANCIA-ZETA-220-MPV-01	4470	1834	1714	Automobile-Catalog 1999 Lancia Zeta 2.0 ie LX Turbo	https://www.automobile-catalog.com/car/1999/1383860/lancia_zeta_2_0_ie_lx_turbo.html
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398	Automobile-Catalog 1995 Ford Escort Mk VI Hatchback range	https://www.automobile-catalog.com/make/ford_europe/escort_europe_7gen/escort_europe_7gen_hatchback/1995.html
EU-FORD-ESCORT-RS-COSWORTH-HATCHBACK-3D-01	4211	1738	1425	Automobile-Catalog 1995 Ford Escort RS Cosworth	https://www.automobile-catalog.com/car/1995/947120/ford_escort_rs_cosworth.html
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	3828	1634	1334	Automobile-Catalog 1995 Ford Fiesta 1.3i 50 Flair	https://www.automobile-catalog.com/car/1995/953645/ford_fiesta_1_3i_50_flair.html
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	3828	1634	1334	Automobile-Catalog 1995 Ford Fiesta 1.8 D LX	https://www.automobile-catalog.com/car/1995/953915/ford_fiesta_1_8_d_lx.html
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	3833	1634	1377	Automobile-Catalog 1999 Ford Fiesta 1.3i 50 Phase II	https://www.automobile-catalog.com/car/1999/955085/ford_fiesta_1_3i_50.html
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	3833	1634	1377	Automobile-Catalog 2000 Ford Fiesta 1.8 Di Finesse	https://www.automobile-catalog.com/car/2000/955445/ford_fiesta_1_8_di_finesse.html
EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	5126	1915	1789	Automobile-Catalog 1996 Ford Windstar Europe export	https://www.automobile-catalog.com/car/1996/886490/ford_windstar.html
EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	5126	1915	1789	Automobile-Catalog 1998 Ford Windstar Europe export	https://www.automobile-catalog.com/car/1998/886505/ford_windstar.html
EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	4460	1695	1390	Automobile-Catalog 1998 Honda Civic 1.4i S Sedan pre-facelift	https://www.automobile-catalog.com/car/1998/1117775/honda_civic_1_4i_s_sedan.html
EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	4460	1695	1390	Automobile-Catalog 1998 Honda Civic 1.4i S Sedan facelift	https://www.automobile-catalog.com/car/1998/1117940/honda_civic_1_4i_s_sedan.html
```

## 下一步优先处理

1. 按共用车身聚类处理 Ktype `5204–5228`：Lantra II、Priora Wagon、Proton Persona 400、Justy II、Eclipse II、Carisma、Almera I。
2. 优先拆解 Lantra II、Carisma 和 Almera I 跨中期改款的物理分支。
3. 随后闭合 Peugeot 406、Porsche 993、Laguna I、C-Zero、C8、Quargo 与 Megane I。

推进信号：CONTINUE

[1]: https://www.dieversicherer.de/typklassen/versicherer/Fiat_Ducato "Typklassen für Fiat Ducato"
[2]: https://www.automobile-catalog.com/make/ford_europe/escort_europe_7gen/escort_europe_7gen_hatchback/1995.html?utm_source=chatgpt.com "1995 Ford (Europe) Escort Mk VI Hatchback full range specs"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5001-5100_ktype_dimension_mapping_final.tsv
- all_5001-5100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已完成剩余 Ktype `5204–5251`，当前批次全部输入均已闭合。
* Fiat Ducato 230P 短轴 Combinato 的 `4655 × 1998 × 2150 mm` 已通过车型规格和瑞士型式批准记录闭合。([gazoo.pl][1])
* 当前欧洲版 Porsche 911（993）Carrera Coupe 的三维为 `4245 × 1735 × 1300 mm`，与累计索引中现有 `EU-PORSCHE-911-993-COUPE-CARRERA-01` 的三维不同，因此未覆盖旧组，按规则创建 `EU-PORSCHE-911-993-COUPE-CARRERA-02`。([汽车目录][2])
* 已完成固定表头、`id` 唯一性、尺寸组唯一性、映射引用闭合、正整数三维、来源非空和下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：166
* READY 映射：166
* PENDING 映射：0
* 最终 DIMENSION_GROUP：63
* 未引用尺寸组：0
* 缺失映射引用：0
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5152	5152	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-BA7-SEDAN-01	HIGH	BA7四门三厢外廓。	READY
5153	5153	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-5D-01	HIGH	182五门Brava外廓。	READY
5154	5154	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5155	5155	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5156	5156	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	HIGH	182三门标准外廓。	READY
5157	5157	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-I-182-HATCHBACK-3D-HGT-01	HIGH	HGT保险杠外廓。	READY
5158	5158	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-SWB-01	MEDIUM	230P Combinato短轴标准顶外廓。	READY
5159	5159	Hatchback	145 (930)	930	3	EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	HIGH	930三门145外廓。	READY
5160	5160	Hatchback	146 (930)	930	5	EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	HIGH	930五门146外廓。	READY
5161	5161	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	HIGH	2003年外观改款前外廓。	READY
5162_prefl	5162	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	MEDIUM	2003年外观改款前分支。	READY
5162_facelift	5162	Coupe	GTV (916)	916	2	EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	MEDIUM	2003年外观改款后分支。	READY
5163	5163	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	MEDIUM	Phase 1/2改款前外廓。	READY
5164_prefl	5164	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	MEDIUM	Phase 1/2改款前分支。	READY
5164_facelift	5164	Convertible	Spider (916)	916	2	EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	MEDIUM	Phase 3改款后分支。	READY
5165_prefl	5165	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999年改款前三厢外廓。	READY
5165_facelift	5165	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999年改款后三厢外廓。	READY
5166_prefl	5166	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999年改款前三厢外廓。	READY
5166_facelift	5166	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999年改款后三厢外廓。	READY
5167_prefl	5167	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999年改款前三厢外廓。	READY
5167_facelift	5167	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999年改款后三厢外廓。	READY
5168_prefl	5168	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999年改款前三厢外廓。	READY
5168_facelift	5168	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999年改款后三厢外廓。	READY
5169_prefl	5169	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	1999年改款前三厢外廓。	READY
5169_facelift	5169	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	1999年改款后三厢外廓。	READY
5170	5170	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	生产期止于1999年改款前。	READY
5171	5171	MPV	Zeta I	220	5	EU-LANCIA-ZETA-220-MPV-01	HIGH	220系列五门MPV外廓。	READY
5172_3dr	5172	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback分支。	READY
5172_5dr	5172	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback分支。	READY
5173_3dr	5173	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback分支。	READY
5173_5dr	5173	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback分支。	READY
5174	5174	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5175	5175	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5176	5176	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5177	5177	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5178_3dr	5178	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback分支。	READY
5178_5dr	5178	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback分支。	READY
5179	5179	Van	Porter I		5	EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	HIGH	封闭式Van外廓。	READY
5180_pickup	5180	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	MEDIUM	标准货台Pickup分支。	READY
5180_chassis_long	5180	Pickup	Porter I		2	EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	MEDIUM	长轴底盘车分支。	READY
5181_3dr	5181	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback分支。	READY
5181_5dr	5181	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback分支。	READY
5182	5182	Hatchback	Escort RS Cosworth		3	EU-FORD-ESCORT-RS-COSWORTH-HATCHBACK-3D-01	HIGH	RS Cosworth宽体外廓。	READY
5183_3dr	5183	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门Hatchback分支。	READY
5183_5dr	5183	Hatchback	Escort VI		5	EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门Hatchback分支。	READY
5184	5184	Sedan	Escort VI	GAL	4	EU-FORD-ESCORT-VI-GAL-SEDAN-01	HIGH	GAL四门三厢外廓。	READY
5185	5185	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5186	5186	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5187	5187	Wagon	Escort VI		5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	五门Turnier外廓。	READY
5188	5188	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5189	5189	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5190	5190	Convertible	Escort VI	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	ALL双门敞篷外廓。	READY
5191_3dr_prefl	5191	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5191_3dr_facelift	5191	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5191_5dr_prefl	5191	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5191_5dr_facelift	5191	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5192_3dr_prefl	5192	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5192_3dr_facelift	5192	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5192_5dr_prefl	5192	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5192_5dr_facelift	5192	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5193_3dr_prefl	5193	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5193_3dr_facelift	5193	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5193_5dr_prefl	5193	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5193_5dr_facelift	5193	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5194_3dr_prefl	5194	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5194_3dr_facelift	5194	Hatchback	Fiesta IV	JA	3	EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5194_5dr_prefl	5194	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5194_5dr_facelift	5194	Hatchback	Fiesta IV	JB	5	EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5195_prefl	5195	MPV	Windstar I		4	EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	MEDIUM	1998年外观修订前分支。	READY
5195_facelift	5195	MPV	Windstar I		4	EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	MEDIUM	1998年外观修订后分支。	READY
5196	5196	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5197	5197	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5198	5198	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5199	5199	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5200	5200	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	欧洲五门Fastback外廓。	READY
5201_prefl	5201	Sedan	Civic VI	EJ9	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5201_facelift	5201	Sedan	Civic VI	EJ9	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5202_prefl	5202	Sedan	Civic VI	EK3	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5202_facelift	5202	Sedan	Civic VI	EK3	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5203_prefl	5203	Sedan	Civic VI	EK4	4	EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5203_facelift	5203	Sedan	Civic VI	EK4	4	EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5204_prefl	5204	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	MEDIUM	1998年改款前三厢分支。	READY
5204_facelift	5204	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	MEDIUM	1998年改款后三厢分支。	READY
5205_prefl	5205	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	MEDIUM	1998年改款前三厢分支。	READY
5205_facelift	5205	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	MEDIUM	1998年改款后三厢分支。	READY
5206_prefl	5206	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	MEDIUM	1998年改款前三厢分支。	READY
5206_facelift	5206	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	MEDIUM	1998年改款后三厢分支。	READY
5207	5207	Wagon	Priora I	2171	5	EU-LADA-PRIORA-2171-WAGON-01	HIGH	2171五门旅行车外廓。	READY
5208	5208	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
5209	5209	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
5210	5210	Hatchback	Persona 400		5	EU-PROTON-PERSONA-400-HATCHBACK-5D-01	HIGH	五门Hatchback外廓。	READY
5211_pre96	5211	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-PRE96-01	MEDIUM	1996年车身修订前分支。	READY
5211_post96	5211	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	MEDIUM	1996年车身修订后分支。	READY
5212_pre96	5212	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-PRE96-01	MEDIUM	1996年车身修订前分支。	READY
5212_post96	5212	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	MEDIUM	1996年车身修订后分支。	READY
5213_pre96	5213	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-PRE96-01	MEDIUM	1996年车身修订前分支。	READY
5213_post96	5213	Sedan	Persona 400		4	EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	MEDIUM	1996年车身修订后分支。	READY
5214_3dr	5214	Hatchback	Justy II		3	EU-SUBARU-JUSTY-II-HATCHBACK-3D-01	MEDIUM	三门Hatchback分支。	READY
5214_5dr	5214	Hatchback	Justy II		5	EU-SUBARU-JUSTY-II-HATCHBACK-5D-01	MEDIUM	五门Hatchback分支。	READY
5215	5215	Coupe	Eclipse II	D30	3	EU-MITSUBISHI-ECLIPSE-II-D30-COUPE-01	HIGH	D30三门Coupe外廓。	READY
5216	5216	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	HIGH	改款前五门Liftback外廓。	READY
5217_prefl	5217	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	MEDIUM	1999年改款前分支。	READY
5217_facelift	5217	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	MEDIUM	1999年改款后分支。	READY
5218	5218	Hatchback	Carisma	DA	5	EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	HIGH	改款前五门Liftback外廓。	READY
5219_3dr_prefl	5219	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5219_3dr_facelift	5219	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5219_5dr_prefl	5219	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5219_5dr_facelift	5219	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5220_3dr_prefl	5220	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5220_3dr_facelift	5220	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5220_5dr_prefl	5220	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5220_5dr_facelift	5220	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5221_3dr_prefl	5221	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5221_3dr_facelift	5221	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5221_5dr_prefl	5221	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5221_5dr_facelift	5221	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5222_3dr_prefl	5222	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5222_3dr_facelift	5222	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5222_5dr_prefl	5222	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5222_5dr_facelift	5222	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5223_3dr_prefl	5223	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
5223_3dr_facelift	5223	Hatchback	Almera I	N15	3	EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
5223_5dr_prefl	5223	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
5223_5dr_facelift	5223	Hatchback	Almera I	N15	5	EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
5224_prefl	5224	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5224_facelift	5224	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5225_prefl	5225	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5225_facelift	5225	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5226_prefl	5226	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5226_facelift	5226	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5227_prefl	5227	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5227_facelift	5227	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5228_prefl	5228	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	MEDIUM	四门Sedan改款前分支。	READY
5228_facelift	5228	Sedan	Almera I	N15	4	EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	MEDIUM	四门Sedan改款后分支。	READY
5229_prefl	5229	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	1999年改款前三厢分支。	READY
5229_facelift	5229	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	MEDIUM	1999年改款后三厢分支。	READY
5230_prefl	5230	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	1999年改款前三厢分支。	READY
5230_facelift	5230	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	MEDIUM	1999年改款后三厢分支。	READY
5231_prefl	5231	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-PREFL-01	MEDIUM	1999年改款前三厢分支。	READY
5231_facelift	5231	Sedan	406 I		4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	MEDIUM	1999年改款后三厢分支。	READY
5232	5232	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH	993 Carrera Cabriolet欧洲版外廓。	READY
5233	5233	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH	993 Carrera Cabriolet欧洲版外廓。	READY
5234	5234	Coupe	911 (993)	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-02	HIGH	993 Carrera Coupe欧洲版外廓。	READY
5235	5235	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH	993 Carrera Cabriolet欧洲版外廓。	READY
5236	5236	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH	993 Carrera Cabriolet欧洲版外廓。	READY
5237	5237	Targa	911 (993)	993	2	EU-PORSCHE-911-993-TARGA-CARRERA-01	HIGH	993 Carrera Targa欧洲版外廓。	READY
5238	5238	Coupe	911 (993)	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-02	HIGH	993 Carrera Coupe欧洲版外廓。	READY
5239	5239	Coupe	911 (993)	993	2	EU-PORSCHE-911-993-COUPE-GT2-01	HIGH	993 GT2宽体外廓。	READY
5240	5240	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	B56五门Hatchback欧洲版外廓。	READY
5241	5241	Hatchback	C-Zero		5	EU-CITROEN-C-ZERO-HATCHBACK-5D-01	HIGH	五门电动Hatchback外廓。	READY
5242	5242	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	B56五门Hatchback欧洲版外廓。	READY
5243	5243	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	B56五门Hatchback欧洲版外廓。	READY
5244	5244	MPV	C8		5	EU-CITROEN-C8-MPV-FACELIFT-01	HIGH	后期五门MPV外廓。	READY
5245_prefl	5245	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	MEDIUM	1998年改款前旅行车分支。	READY
5245_facelift	5245	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	MEDIUM	1998年改款后旅行车分支。	READY
5246_prefl	5246	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	MEDIUM	1998年改款前旅行车分支。	READY
5246_facelift	5246	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	MEDIUM	1998年改款后旅行车分支。	READY
5247_prefl	5247	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	MEDIUM	1998年改款前旅行车分支。	READY
5247_facelift	5247	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	MEDIUM	1998年改款后旅行车分支。	READY
5248_prefl	5248	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	MEDIUM	1998年改款前旅行车分支。	READY
5248_facelift	5248	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	MEDIUM	1998年改款后旅行车分支。	READY
5249	5249	Pickup	Quargo		2	EU-PIAGGIO-QUARGO-PICKUP-01	MEDIUM	标准单排平板外廓。	READY
5250_prefl	5250	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	MEDIUM	1998年改款前旅行车分支。	READY
5250_facelift	5250	Wagon	Laguna I Grandtour	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	MEDIUM	1998年改款后旅行车分支。	READY
5251_prefl	5251	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	MEDIUM	1999年改款前五门分支。	READY
5251_facelift	5251	Hatchback	Megane I	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	MEDIUM	1999年改款后五门分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5001-5100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-IV-BA7-SEDAN-01	4844	1886	1500	Automobile-Catalog 2007 Ford Mondeo 4-dr 2.0 Titanium	https://www.automobile-catalog.com/car/2007/977510/ford_mondeo_4-dr_2_0_titanium.html
EU-FIAT-BRAVA-182-HATCHBACK-5D-01	4187	1741	1420	Automobile-Catalog 1996 Fiat Brava 1.8 16V EL	https://www.automobile-catalog.com/car/1996/721100/fiat_brava_1_8_16v_el.html
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-01	4025	1755	1420	Automobile-Catalog 1996 Fiat Bravo 1.8 16V GT	https://www.automobile-catalog.com/car/1996/720950/fiat_bravo_1_8_16v_gt.html
EU-FIAT-BRAVO-I-182-HATCHBACK-3D-HGT-01	4031	1755	1420	Automobile-Catalog 1997 Fiat Bravo 2.0 20V HGT	https://www.automobile-catalog.com/car/1997/720995/fiat_bravo_2_0_20v_hgt.html
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150	Swiss type approval DAuto Fiat Ducato 230/10	https://www.dauto.ch/typenscheine/fiat-ducato-230-10-1f3275-x-x
EU-ALFA-ROMEO-145-930-HATCHBACK-3D-01	4093	1712	1427	Automobile-Catalog 1999 Alfa Romeo 145 Quadrifoglio	https://www.automobile-catalog.com/car/1999/218015/alfa_romeo_145_quadrifoglio.html
EU-ALFA-ROMEO-146-930-HATCHBACK-5D-01	4257	1712	1425	Automobile-Catalog 1997 Alfa Romeo 146 Ti	https://www.automobile-catalog.com/car/1997/218090/alfa_romeo_146_ti.html
EU-ALFA-ROMEO-GTV-916-COUPE-PREFL-01	4285	1780	1318	Automobile-Catalog 2001 Alfa Romeo GTV 2.0 Twin Spark 16V; Automobile-Catalog 1995 Alfa Romeo GTV 2.0 V6 TB	https://www.automobile-catalog.com/car/2001/218450/alfa_romeo_gtv_2_0_twin_spark_16v.html;https://www.automobile-catalog.com/car/1995/218390/alfa_romeo_gtv_2_0_v6_tb.html
EU-ALFA-ROMEO-GTV-916-COUPE-FACELIFT-01	4299	1776	1318	Automobile-Catalog 2003 Alfa Romeo GTV 2.0 JTS 16V	https://www.automobile-catalog.com/car/2003/218660/alfa_romeo_gtv_2_0_jts_16v.html
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	4285	1780	1315	Automobile-Catalog 1995 Alfa Romeo Spider 2.0 Twin Spark 16V	https://www.automobile-catalog.com/car/1995/218420/alfa_romeo_spider_2_0_twin_spark_16v.html
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	4299	1776	1315	Automobile-Catalog 2004 Alfa Romeo Spider 2.0 Twin Spark 16V	https://www.automobile-catalog.com/car/2004/218690/alfa_romeo_spider_2_0_twin_spark_16v.html
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425	Automobile-Catalog 1996 Opel Vectra 4d 1.6	https://www.automobile-catalog.com/car/1996/2476805/opel_vectra_4d_1_6.html
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425	Automobile-Catalog 1999 Opel Vectra 4d 1.6 16V	https://www.automobile-catalog.com/car/1999/2478665/opel_vectra_4d_1_6_16v.html
EU-LANCIA-ZETA-220-MPV-01	4470	1834	1714	Automobile-Catalog 1999 Lancia Zeta 2.0 ie LX Turbo	https://www.automobile-catalog.com/car/1999/1383860/lancia_zeta_2_0_ie_lx_turbo.html
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398	Automobile-Catalog 1995 Ford Escort Mk VI Hatchback range	https://www.automobile-catalog.com/make/ford_europe/escort_europe_7gen/escort_europe_7gen_hatchback/1995.html
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398	Automobile-Catalog 1995 Ford Escort 1.8i 16V LX	https://www.automobile-catalog.com/car/1995/952160/ford_escort_1_8i_16v_lx.html
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397	Arabalar 1995 Ford Escort Sedan 1.8 CLX 16V	https://www.arabalar.com.tr/ford/escort/1995/sedan-1-8-clx-16v
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410	Automobile-Catalog 1995 Ford Escort Turnier 1.6i 16V Ghia	https://www.automobile-catalog.com/car/1995/947000/ford_escort_turnier_1_6i_16v_ghia.html
EU-PIAGGIO-PORTER-I-FACELIFT-VAN-01	3370	1395	1870	Anchor Vans Piaggio Porter specifications	https://www.anchorvans.co.uk/specifications/porter-piaggio
EU-PIAGGIO-PORTER-I-FACELIFT-PICKUP-01	3390	1395	1730	Anchor Vans Piaggio Porter specifications	https://www.anchorvans.co.uk/specifications/porter-piaggio
EU-PIAGGIO-PORTER-I-FACELIFT-CHASSIS-LONG-01	3750	1460	1730	Web4x4 Piaggio Porter dimensions table	https://web4x4.free.fr/page/piaggio2.htm
EU-FORD-ESCORT-RS-COSWORTH-HATCHBACK-3D-01	4211	1738	1425	Automobile-Catalog 1995 Ford Escort RS Cosworth	https://www.automobile-catalog.com/car/1995/947120/ford_escort_rs_cosworth.html
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379	Wagenegaw Ford Escort VI Cabriolet ALL specifications	https://wagenegaw.com/specificaties/ford/escort/cabriolet-1993/
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	3828	1634	1334	Automobile-Catalog 1995 Ford Fiesta 1.3i 50 Flair	https://www.automobile-catalog.com/car/1995/953645/ford_fiesta_1_3i_50_flair.html
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	3833	1634	1377	Automobile-Catalog 1999 Ford Fiesta 1.3i 50 Phase II	https://www.automobile-catalog.com/car/1999/955085/ford_fiesta_1_3i_50.html
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	3828	1634	1334	Automobile-Catalog 1995 Ford Fiesta 1.8 D LX	https://www.automobile-catalog.com/car/1995/953915/ford_fiesta_1_8_d_lx.html
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	3833	1634	1377	Automobile-Catalog 2000 Ford Fiesta 1.8 Di Finesse	https://www.automobile-catalog.com/car/2000/955445/ford_fiesta_1_8_di_finesse.html
EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	5126	1915	1789	Automobile-Catalog 1996 Ford Windstar Europe export	https://www.automobile-catalog.com/car/1996/886490/ford_windstar.html
EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	5126	1915	1789	Automobile-Catalog 1998 Ford Windstar Europe export	https://www.automobile-catalog.com/car/1998/886505/ford_windstar.html
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Automobile-Catalog 1999 Honda Civic 1.5i VTEC 5-Door	https://www.automobile-catalog.com/car/1999/1118075/honda_civic_1_5i_vtec_5-door.html
EU-HONDA-CIVIC-VI-SEDAN-4D-PREFL-01	4460	1695	1390	Automobile-Catalog 1998 Honda Civic 1.4i S Sedan pre-facelift	https://www.automobile-catalog.com/car/1998/1117775/honda_civic_1_4i_s_sedan.html
EU-HONDA-CIVIC-VI-SEDAN-4D-FACELIFT-01	4460	1695	1390	Automobile-Catalog 1998 Honda Civic 1.4i S Sedan facelift	https://www.automobile-catalog.com/car/1998/1117940/honda_civic_1_4i_s_sedan.html
EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	4420	1700	1393	Automobile-Catalog 1995 Hyundai Lantra 1.6i 16V GLS automatic	https://www.automobile-catalog.com/car/1995/1164305/hyundai_lantra_1_6i_16v_gls_automatic.html
EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	4448	1702	1393	Automobile-Catalog 2000 Hyundai Lantra 1.6i 16V GLS automatic	https://www.automobile-catalog.com/car/2000/1164650/hyundai_lantra_1_6i_16v_gls_automatic.html
EU-LADA-PRIORA-2171-WAGON-01	4340	1680	1508	Auto-Data Lada Priora model specifications	https://www.auto-data.net/en/lada-priora-model-1421
EU-PROTON-PERSONA-400-HATCHBACK-5D-01	4270	1690	1385	Automobile-Catalog 1995 Proton Persona 5 Door 1.5	https://www.automobile-catalog.com/car/1995/2878835/proton_persona_5_door_1_5.html
EU-PROTON-PERSONA-400-SEDAN-4D-PRE96-01	4360	1690	1385	Automobile-Catalog 1995 Proton Persona 4 Door 1.5	https://www.automobile-catalog.com/car/1995/2878775/proton_persona_4_door_1_5.html
EU-PROTON-PERSONA-400-SEDAN-4D-POST96-01	4360	1690	1380	Automobile-Catalog 1997 Proton Persona 4 Door 1.6 XLi	https://www.automobile-catalog.com/car/1997/2879015/proton_persona_4_door_1_6_xli.html
EU-SUBARU-JUSTY-II-HATCHBACK-3D-01	3745	1590	1350	Automobile-Catalog 1996 Subaru Justy 1.3 GX 3 Door AWD	https://www.automobile-catalog.com/car/1996/3243335/subaru_justy_1_3_gx_3_door_awd.html
EU-SUBARU-JUSTY-II-HATCHBACK-5D-01	3845	1590	1380	Automobile-Catalog 1995 Subaru Justy 1.3 GX 5 Door AWD	https://www.automobile-catalog.com/car/1995/3243575/subaru_justy_1_3_gx_5_door_awd.html
EU-MITSUBISHI-ECLIPSE-II-D30-COUPE-01	4385	1745	1293	Automobile-Catalog 1996 Mitsubishi Eclipse GS 16V	https://www.automobile-catalog.com/car/1996/2006750/mitsubishi_eclipse_gs_16v.html
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-PREFL-01	4435	1695	1405	Automobile-Catalog 1996 Mitsubishi Carisma 5d 1.8 GLX	https://www.automobile-catalog.com/car/1996/1999190/mitsubishi_carisma_5d_1_8_glx.html
EU-MITSUBISHI-CARISMA-DA-HATCHBACK-5D-FACELIFT-01	4475	1710	1405	Automobile-Catalog 2000 Mitsubishi Carisma 5d 1.6i	https://www.automobile-catalog.com/car/2000/1999910/mitsubishi_carisma_5d_1_6i.html
EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-PREFL-01	4120	1690	1395	Automobile-Catalog 1996 Nissan Almera N15 Hatchback range	https://www.automobile-catalog.com/make/nissan/almera_1gen_n15/almera_1gen_1_hatchback/1996.html
EU-NISSAN-ALMERA-I-N15-HATCHBACK-3D-FACELIFT-01	4140	1700	1395	Automobile-Catalog 1998 Nissan Almera N15 Hatchback facelift range	https://www.automobile-catalog.com/make/nissan/almera_1gen_n15/almera_1gen_2_hatchback/1998.html
EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-PREFL-01	4120	1690	1395	Automobile-Catalog 1996 Nissan Almera N15 Hatchback range	https://www.automobile-catalog.com/make/nissan/almera_1gen_n15/almera_1gen_1_hatchback/1996.html
EU-NISSAN-ALMERA-I-N15-HATCHBACK-5D-FACELIFT-01	4140	1700	1395	Automobile-Catalog 1998 Nissan Almera N15 Hatchback facelift range	https://www.automobile-catalog.com/make/nissan/almera_1gen_n15/almera_1gen_2_hatchback/1998.html
EU-NISSAN-ALMERA-I-N15-SEDAN-4D-PREFL-01	4320	1690	1395	Automobile-Catalog 1996 Nissan Almera N15 Sedan range	https://www.automobile-catalog.com/make/nissan/almera_1gen_n15/almera_1gen_1_sedan/1996.html
EU-NISSAN-ALMERA-I-N15-SEDAN-4D-FACELIFT-01	4340	1700	1395	Automobile-Catalog 1999 Nissan Almera 4d 1.4 Classic	https://www.automobile-catalog.com/car/1999/2253515/nissan_almera_4d_1_4_classic.html
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410	Automobile-Catalog 1996 Peugeot 406 1.8i 16V	https://www.automobile-catalog.com/car/1996/2613800/peugeot_406_1_8i_16v.html
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412	Automobile-Catalog 2000 Peugeot 406 1.8i 16V	https://www.automobile-catalog.com/car/2000/2614190/peugeot_406_1_8i_16v.html
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300	Automobile-Catalog 1997 Porsche 911 Carrera Cabriolet	https://www.automobile-catalog.com/car/1997/2865830/porsche_911_carrera_cabriolet.html
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300	Automobile-Catalog 1997 Porsche 911 Carrera Coupe Europe	https://www.automobile-catalog.com/car/1997/2865785/porsche_911_carrera_coupe.html
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300	Automobile-Catalog 1997 Porsche 911 Targa Europe	https://www.automobile-catalog.com/car/1997/2866130/porsche_911_targa.html
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270	Automobile-Catalog 1997 Porsche 911 GT2	https://www.automobile-catalog.com/car/1997/2866085/porsche_911_gt2.html
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	4508	1752	1433	Automobile-Catalog 1996 Renault Laguna 2.0S 16V	https://www.automobile-catalog.com/car/1996/2945690/renault_laguna_2_0s_16v.html
EU-CITROEN-C-ZERO-HATCHBACK-5D-01	3475	1475	1608	Automobile-Catalog 2011 Citroen C-Zero	https://www.automobile-catalog.com/car/2011/2018870/citroen_c-zero.html
EU-CITROEN-C8-MPV-FACELIFT-01	4727	1854	1752	Automobile-Catalog 2010 Citroen C8 HDi 165 Exclusive	https://www.automobile-catalog.com/car/2010/1452950/citroen_c8_hdi_165_exclusive.html
EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	4620	1752	1448	Automobile-Catalog 1996 Renault Laguna Wagon 2.0S 16V	https://www.automobile-catalog.com/car/1996/2945810/renault_laguna_wagon_2_0s_16v.html
EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	4628	1752	1448	Automobile-Catalog 2000 Renault Laguna Wagon 2.0 16V	https://www.automobile-catalog.com/car/2000/2946245/renault_laguna_wagon_2_0_16v.html
EU-PIAGGIO-QUARGO-PICKUP-01	3495	1460	1705	Piaggio Quargo Disco 2008 workshop manual	https://www.manualslib.de/manual/1208700/Piaggio-Quargo-Disco-2008.html
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420	Automobile-Catalog 1996 Renault Megane 1.4e	https://www.automobile-catalog.com/car/1996/2946350/renault_megane_1_4e.html
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420	Automobile-Catalog 2000 Renault Megane 1.4e	https://www.automobile-catalog.com/car/2000/2946770/renault_megane_1_4e.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5001-5100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/ "https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/"
[2]: https://www.automobile-catalog.com/car/1997/2865785/porsche_911_carrera_coupe.html "https://www.automobile-catalog.com/car/1997/2865785/porsche_911_carrera_coupe.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5001-5100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5001-5100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（6575 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2047 行）

