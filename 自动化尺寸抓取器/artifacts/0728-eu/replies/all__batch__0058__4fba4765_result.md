# 任务：all 第 5701-5800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0058__4fba4765


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5701-5800 行

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
all 第 5701-5800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-100-C1-COUPE-01	4398	1750	1340
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421
EU-AUDI-100-C2-AVANT-01	4587	1768	1390
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390
EU-AUDI-100-C2-WAGON-FACELIFT-01	4590	1768	1390
EU-AUDI-100-C2-WAGON-PREFL-01	4587	1768	1390
EU-AUDI-100-C3-AVANT-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-02	4793	1814	1421
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422
EU-AUDI-100-C3-WAGON-QUATTRO-01	4793	1814	1422
EU-AUDI-100-C4-S4-AVANT-WAGON-01	4790	1805	1422
EU-AUDI-100-C4-S4-SEDAN-01	4790	1805	1420
EU-AUDI-100-C4-SEDAN-FWD-01	4790	1777	1431
EU-AUDI-100-C4-SEDAN-QUATTRO-01	4790	1777	1437
EU-AUDI-100-C4-WAGON-FWD-01	4790	1777	1440
EU-AUDI-100-C4-WAGON-QUATTRO-01	4790	1777	1448
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
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-BMW-ISETTA-250-COUPE-EARLY-01	2285	1380	1340
EU-BMW-ISETTA-250-COUPE-LATE-01	2355	1380	1340
EU-CHRYSLER-VOYAGER-II-ES-MPV-01	4525	1830	1707
EU-CITROEN-CX-I-1982-FACELIFT-SEDAN-4D-01	4659	1770	1360
EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	4930	1770	1460
EU-CITROEN-CX-I-BREAK-WAGON-5D-01	4922	1734	1465
EU-CITROEN-CX-I-GTI-SEDAN-4D-01	4659	1755	1360
EU-CITROEN-CX-II-BREAK-WAGON-5D-01	4930	1770	1460
EU-CITROEN-CX-II-SEDAN-4D-01	4650	1770	1360
EU-CITROEN-CX-I-SEDAN-4D-01	4659	1734	1360
EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	4036	1692	1395
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	4104	1696	1397
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	4104	1696	1397
EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	4104	1696	1397
EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	4036	1692	1395
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	4108	1696	1379
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	4040	1692	1389
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	4108	1696	1370
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-PREFL-01	4036	1692	1389
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	4211	1738	1425
EU-FORD-ESCORT-V-WAGON-PREFL-01	4268	1690	1414
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490
EU-FORD-SCORPIO-I-HATCHBACK-01	4669	1760	1440
EU-FORD-SCORPIO-I-HATCHBACK-5D-01	4669	1760	1490
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1402
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442
EU-FORD-SCORPIO-I-SEDAN-01	4744	1766	1450
EU-FORD-SCORPIO-I-SEDAN-4D-01	4744	1766	1450
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407
EU-FORD-SIERRA-MK1-HATCHBACK-3D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-GHIA-01	4425	1725	1408
EU-FORD-SIERRA-MK1-WAGON-01	4491	1712	1438
EU-FORD-SIERRA-MK1-WAGON-GHIA-01	4522	1729	1438
EU-FORD-SIERRA-MK1-XR4I-HATCHBACK-3D-01	4459	1728	1392
EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	4459	1725	1378
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	4105	1690	1515
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385
EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	4590	1752	1433
EU-LANCIA-THEMA-I-SEDAN-SERIES-2-01	4590	1758	1435
EU-LANCIA-THEMA-I-SEDAN-SERIES-3-01	4605	1752	1435
EU-LANCIA-THEMA-I-WAGON-SERIES-2-01	4590	1755	1440
EU-LANCIA-THEMA-I-WAGON-SERIES-3-01	4605	1752	1435
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430
EU-MAZDA-626-III-GV-WAGON-5D-02	4660	1755	1440
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	4395	1655	1400
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-PREFL-01	4350	1655	1400
EU-NISSAN-BLUEBIRD-910-WAGON-5D-FACELIFT-01	4445	1655	1405
EU-NISSAN-BLUEBIRD-910-WAGON-5D-PREFL-01	4400	1655	1400
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-01	4365	1690	1395
EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	4405	1690	1395
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-01	4420	1690	1395
EU-NISSAN-BLUEBIRD-T72-SEDAN-4D-01	4460	1690	1395
EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	4360	1690	1400
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-FACELIFT-01	4445	1690	1475
EU-NISSAN-BLUEBIRD-U11-WAGON-5D-PREFL-01	4405	1690	1455
EU-NISSAN-CHERRY-N10-COUPE-PHASE-I-01	3890	1620	1320
EU-NISSAN-CHERRY-N10-COUPE-PHASE-II-01	3960	1620	1320
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	3890	1600	1360
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	3960	1620	1360
EU-NISSAN-CHERRY-N12-HATCHBACK-01	3960	1620	1385
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-I-01	3930	1600	1385
EU-NISSAN-CHERRY-VN10-WAGON-PHASE-II-01	3990	1620	1385
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1303-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-TYPE113-1600-01	4060	1550	1500
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	4140	1634	1330
EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	4140	1634	1330

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Transporter t1	1.6	Kasten	Heckantrieb	Benzin	35	48	Aug 1964	Dec 1968	2024-03-01	6062
Morris	Marina	1800	Kombi	Heckantrieb	Benzin	57	78	Apr 1971	Oct 1975	2024-03-01	6063
Autobianchi	A 111	1.4	Stufenheck	Frontantrieb	Benzin	51	70	Aug 1969	Nov 1972	2024-03-01	6064
Autobianchi	A 112	0.9	Schrägheck	Frontantrieb	Benzin	32	44	Oct 1969	Dec 1972	2024-03-01	6065
Volvo	V60 i	D5	Kombi	Frontantrieb	Diesel	151	205	Jul 2010	Dec 2011	2024-03-01	6066
Volvo	V60 i	D5 AWD	Kombi	Allrad	Diesel	151	205	Jul 2010	Dec 2011	2024-03-01	6067
Autobianchi	A 112	1.0 Abarth	Schrägheck	Frontantrieb	Benzin	43	58	Sep 1971	Dec 1975	2024-03-01	6068
Autobianchi	A 112	0.9 E	Schrägheck	Frontantrieb	Benzin	34	47	Jan 1973	Dec 1977	2024-03-01	6069
Autobianchi	A 112	1.0 Abarth	Schrägheck	Frontantrieb	Benzin	51	70	Jan 1974	Dec 1984	2024-03-01	6070
Autobianchi	A 112	0.9 Junior	Schrägheck	Frontantrieb	Benzin	31	42	Jul 1975	Dec 1985	2024-03-01	6071
Autobianchi	A 112	1.0 E,elite,lx	Schrägheck	Frontantrieb	Benzin	35	48	Nov 1977	Dec 1985	2024-03-01	6072
Autobianchi	A 112	0.9	Schrägheck	Frontantrieb	Benzin	33	45	Jan 1976	Dec 1978	2024-03-01	6073
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	120	163	Aug 2010	Oct 2016	2024-03-01	6074
BMW	1502-2002	1600	Kombi	Heckantrieb	Benzin	63	85	May 1971	Apr 1973	2024-03-01	6075
BMW	1502-2002	1802	Kombi	Heckantrieb	Benzin	66	90	May 1971	Jul 1975	2024-03-01	6076
BMW	1502-2002	2002	Kombi	Heckantrieb	Benzin	74	100	May 1971	Jul 1975	2024-03-01	6077
BMW	1502-2002	2002 TII	Kombi	Heckantrieb	Benzin	96	130	Jan 1971	Jul 1975	2024-03-01	6078
Chrysler	Voyager ii	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	87	118	Jan 1992	Sep 1995	2024-03-01	6079
Citroën	Cx i	2000	Stufenheck	Frontantrieb	Benzin	75	102	Sep 1974	May 1979	2024-03-01	6080
Citroën	Cx i	2200	Stufenheck	Frontantrieb	Benzin	82	112	Sep 1974	Jul 1976	2024-03-01	6081
Citroën	Cx i break	2000	Kombi	Frontantrieb	Benzin	75	102	Sep 1975	May 1979	2024-03-01	6082
Ford	Escort v	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1990	Aug 1992	2024-03-01	6085
Ford	Escort v turnier	1.6	Kombi	Frontantrieb	Benzin	66	90	Jul 1990	Aug 1992	2024-03-01	6086
Volvo	V60 i	T3	Kombi	Frontantrieb	Benzin	110	150	Sep 2010	Dec 2015	2024-03-01	6087
Ford	Escort iv express	1.1	Kasten/Kombi	Frontantrieb	Benzin	37	50	May 1986	Jul 1990	2024-03-01	6088
Ford	Escort v express	1.3	Kasten/Kombi	Frontantrieb	Benzin	46	63	Jul 1990	Dec 1994	2024-03-01	6090
Ford	Escort v express	1.4	Kasten/Kombi	Frontantrieb	Benzin	52	71	Jul 1990	Dec 1994	2024-03-01	6091
Ford	Escort v express	1.8 D	Kasten/Kombi	Frontantrieb	Diesel	44	60	Jul 1990	Dec 1994	2024-03-01	6092
Ford	Escort vi express	1.4	Kasten/Kombi	Frontantrieb	Benzin	54	73	Jan 1995	Aug 2000	2024-03-01	6093
Ford	Escort vi express	1.8 D	Kasten/Kombi	Frontantrieb	Diesel	44	60	Jan 1995	Aug 2000	2024-03-01	6094
Ford	Escort iii express	1.1	Kasten/Kombi	Frontantrieb	Benzin	37	50	Mar 1981	Feb 1986	2024-03-01	6095
Ford	Escort iii express	1.3	Kasten/Kombi	Frontantrieb	Benzin	51	69	Mar 1981	Feb 1986	2024-03-01	6096
Ford	Escort iii express	1.6 D	Kasten/Kombi	Frontantrieb	Diesel	40	54	Feb 1984	Feb 1986	2024-03-01	6097
Ford	Scorpio i	2.9 I	Stufenheck	Heckantrieb	Benzin	107	145	Sep 1986	Dec 1994	2024-03-01	6101
Ford	Sierra	2.9 I XR 4X4	Schrägheck	Allrad	Benzin	110	150	Aug 1988	Feb 1993	2024-03-01	6102
Ford	Sierra	2.9 I XR 4X4	Schrägheck	Allrad	Benzin	107	145	Aug 1988	Feb 1993	2024-03-01	6103
Ford	Sierra	2.9 I	Schrägheck	Heckantrieb	Benzin	107	145	Aug 1988	Feb 1993	2024-03-01	6104
Ford	Sierra	2.9 I	Stufenheck	Heckantrieb	Benzin	107	145	Aug 1988	Feb 1993	2024-03-01	6105
Honda	Civic iv	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	96	130	Sep 1987	Sep 1991	2024-03-01	6107
Honda	Civic iv shuttle	1.5 I 16V	Kombi	Frontantrieb	Benzin	69	94	Jan 1988	Nov 1991	2025-02-03	6108
Lancia	Prisma	1.6 I.e.	Stufenheck	Frontantrieb	Benzin	80	109	May 1986	Dec 1989	2024-03-01	6110
Lancia	Thema	2000 I.e.	Stufenheck	Frontantrieb	Benzin	88	120	Nov 1984	Sep 1988	2024-03-01	6111
Mazda	626 iii	1.8	Coupe	Frontantrieb	Benzin	65	88	Sep 1987	Aug 1991	2024-03-01	6112
Mazda	626 iii station wagon	2.0 16V	Kombi	Frontantrieb	Benzin	103	140	Jan 1988	Mar 1992	2024-03-01	6114
Nissan	Bluebird	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1983	Jun 1988	2024-03-01	6119
Nissan	Bluebird	2.0 I	Stufenheck	Heckantrieb	Benzin	80	109	Jan 1982	Dec 1983	2024-03-01	6122
Nissan	Bluebird	1.9 I	Stufenheck	Heckantrieb	Benzin	80	109	Jan 1982	May 1984	2024-03-01	6123
Volvo	V60 i	T4	Kombi	Frontantrieb	Benzin	132	180	Sep 2010	Dec 2015	2024-03-01	6124
Nissan	Cherry	1	Schrägheck	Frontantrieb	Benzin	32	44	Aug 1978	Jul 1981	2024-03-01	6129
Audi	80	1.3	Stufenheck	Frontantrieb	Benzin	44	60	May 1972	Jul 1978	2024-03-01	6133
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Sep 1975	Jul 1978	2024-03-01	6135
Audi	80	1.6 GT	Stufenheck	Frontantrieb	Benzin	74	100	Sep 1973	Jul 1976	2024-03-01	6136
Audi	80	1.6 GTE	Stufenheck	Frontantrieb	Benzin	81	110	Jan 1976	Jul 1978	2024-03-01	6138
Audi	80	2.0 E 16V Quattro	Kombi	Allrad	Benzin	103	140	Dec 1992	Jul 1995	2024-03-01	6139
Audi	100	1.9	Coupe	Frontantrieb	Benzin	85	115	Jul 1970	Jul 1971	2024-03-01	6140
Audi	b3	2.2 Quattro	Coupe	Allrad	Benzin	100	136	Nov 1988	Jul 1991	2024-03-01	6141
BMW	1502-2002	1600/2	Stufenheck	Heckantrieb	Benzin	63	85	Dec 1967	Dec 1971	2024-03-01	6142
BMW	1502-2002	2002 TI	Stufenheck	Heckantrieb	Benzin	88	120	Jun 1968	Apr 1972	2024-03-01	6143
BMW	Isetta	300	Coupe	Heckantrieb	Benzin	10	14	May 1958	Nov 1963	2024-03-01	6144
BMW	3	316	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1983	Jun 1988	2024-03-01	6145
BMW	3	315	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1982	Dec 1991	2024-03-01	6146
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	75	102	Aug 1987	Aug 1988	2024-03-01	6147
BMW	3	M3 EVO II 2.5	Stufenheck	Heckantrieb	Benzin	175	238	Jan 1990	Jan 1992	2024-03-01	6148
Alpine	A110 i	1100	Coupe	Heckantrieb	Benzin	70	95	Jan 1968	Dec 1970	2024-03-01	6149
Alpine	A110 i	1300	Coupe	Heckantrieb	Benzin	81	110	Jan 1968	Dec 1970	2024-03-01	6150
Volvo	V60 i	T5	Kombi	Frontantrieb	Benzin	177	241	Sep 2010	Dec 2014	2024-03-01	6151
Alpine	A110 i	1500	Coupe	Heckantrieb	Benzin	51	70	Jan 1966	Dec 1970	2024-03-01	6152
Alpine	A110 i	1500	Coupe	Heckantrieb	Benzin	66	90	Jan 1966	Dec 1970	2024-03-01	6153
Volvo	V60 i	T6 AWD	Kombi	Allrad	Benzin	224	305	Jul 2010	Dec 2015	2024-03-01	6154
VW	Kaefer	1.1	Stufenheck	Heckantrieb	Benzin	18	24	Dec 1947	Dec 1953	2024-03-01	6155
Alpine	1300	1.3 85	Coupe	Heckantrieb	Benzin	60	81	Jan 1970	Dec 1973	2024-03-01	6156
Alpine	1300	1.3 G	Coupe	Heckantrieb	Benzin	76	103	Jan 1970	Dec 1972	2024-03-01	6157
Volvo	V70 iii	T4	Kombi	Frontantrieb	Benzin	132	180	Oct 2010	Dec 2015	2024-03-01	6158
Alpine	1300	1.3 S	Coupe	Heckantrieb	Benzin	97	132	Jan 1970	Dec 1972	2024-03-01	6159
Alpine	1300	1.3	Coupe	Heckantrieb	Benzin	54	73	Jan 1974	Dec 1975	2024-03-01	6160
Alpine	1600	1.6	Coupe	Heckantrieb	Benzin	75	102	Jan 1970	Dec 1971	2024-03-01	6161
Alpine	1600	1.6 S	Coupe	Heckantrieb	Benzin	101	138	Jan 1969	Dec 1973	2024-03-01	6162
Alpine	1600	1.6 Sc-si	Coupe	Heckantrieb	Benzin	93	127	Jan 1973	Dec 1975	2024-03-01	6163
Alpine	1600	1.6 Sc-si	Coupe	Heckantrieb	Benzin	103	140	Jan 1973	Dec 1975	2024-03-01	6164
Alpine	A310	1.7	Coupe	Heckantrieb	Benzin	70	95	Jan 1971	Dec 1977	2024-03-01	6165
Alpine	A310	1.6	Coupe	Heckantrieb	Benzin	93	127	Jan 1971	Dec 1977	2024-03-01	6166
VW	Kaefer	Karmann 1.3	Cabriolet	Heckantrieb	Benzin	29	40	Jul 1964	Jul 1970	2024-03-01	6167
Volvo	Xc60 i	T5	SUV	Frontantrieb	Benzin	177	241	Sep 2010	Feb 2017	2024-03-01	6168
Alpine	A310	1.6 Injection	Coupe	Heckantrieb	Benzin	94	127	Jan 1976	Dec 1977	2024-03-01	6169
Alpine	A310	2.7 V6	Coupe	Heckantrieb	Benzin	110	150	Jan 1976	Dec 1984	2024-03-01	6170
Alpine	Berlinette	1300	Coupe	Heckantrieb	Benzin	50	68	Jan 1976	Dec 1977	2024-03-01	6171
Alpine	Berlinette	1600 SX	Coupe	Heckantrieb	Benzin	70	95	Jan 1976	Dec 1977	2024-03-01	6172
Alpine	V6	GT	Coupe	Heckantrieb	Benzin	116	158	Jan 1985	Dec 1990	2024-03-01	6173
Alpine	V6	Turbo	Coupe	Heckantrieb	Benzin	136	185	Jan 1985	Dec 1990	2024-03-01	6174
Alpine	V6	Turbo	Coupe	Heckantrieb	Benzin	147	200	Jan 1988	Dec 1990	2024-03-01	6175
Alpine	A610	3.0 Turbo	Coupe	Heckantrieb	Benzin	184	250	Jan 1991	Apr 1995	2024-03-01	6179
VW	Kaefer	1302 1.3	Cabriolet	Heckantrieb	Benzin	29	39	Aug 1970	Jul 1974	2024-03-01	6180
VW	Kaefer	1303 1.3	Cabriolet	Heckantrieb	Benzin	32	44	Jul 1970	Mar 1981	2024-03-01	6181
VW	Kaefer	1500 1.6	Cabriolet	Heckantrieb	Benzin	35	48	Jul 1969	Jul 1970	2024-03-01	6182
VW	Kaefer	1302 1.6	Cabriolet	Heckantrieb	Benzin	34	46	Aug 1970	Jul 1974	2024-03-01	6183
VW	Kaefer	1303 1.6	Cabriolet	Heckantrieb	Benzin	35	48	Aug 1970	Jul 1974	2024-03-01	6184
VW	Kaefer	1303 1.2	Cabriolet	Heckantrieb	Benzin	25	34	Apr 1975	Dec 1979	2024-03-01	6185
VW	Karmann ghia	1300	Coupe	Heckantrieb	Benzin	32	44	Jul 1970	Jul 1974	2024-03-01	6187
VW	Karmann ghia	1500	Coupe	Heckantrieb	Benzin	40	54	Aug 1961	Jul 1970	2024-03-01	6188
VW	Karmann ghia	1600	Coupe	Heckantrieb	Benzin	35	48	Jul 1971	Jul 1974	2024-03-01	6189


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类处理 39 个 Ktype，共形成 50 条 READY 映射，其中 22 个尺寸组直接复用跨批次缓存，新增闭合 8 个尺寸组。
* Volvo V60 I、V70 III、XC60 I 的输入生产区间跨越改款，改款前后长度发生变化，已拆成稳定派生映射；宽度均采用不含后视镜口径。([手册架][1])
* MINI Cooper S ALL4 已确认属于 Countryman R60 五门 SUV 外廓，官方产品资料尺寸为 4110 × 1789 × 1561 mm。([BMW Group PressClub][2])
* Autobianchi A112 早期 0.9 已闭合为 Series 1 三门车身，尺寸为 3231 × 1480 × 1340 mm。([汽车目录][3])
* Audi 80 B1、Nissan Cherry N10、VW Käfer Type 15 等跨改款记录已按现有缓存拆分，不重复抓取尺寸来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：39
* READY 映射行：50
* PENDING Ktype：61
* 当前已引用尺寸组：30
* 本轮新建尺寸组：8
* 本轮复用既有尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6065	6065	Hatchback	A112 Series 1		3	EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	HIGH	首代三门外廓。	READY
6066	6066	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6067	6067	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6074	6074	SUV	Countryman R60	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH	输入Kombi；R60 Countryman按SUV外廓归类。	READY
6079	6079	MPV	Voyager II	ES	5	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH	ES代五门MPV。	READY
6080	6080	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH	早期CX I四门轿车外廓。	READY
6081	6081	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH	早期CX I四门轿车外廓。	READY
6082	6082	Wagon	CX I		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	HIGH	CX I Break五门外廓。	READY
6086	6086	Wagon	Escort V		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Escort V改款前旅行版。	READY
6087_prefl	6087	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6087_facelift	6087	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6101	6101	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	HIGH	Scorpio I四门轿车外廓。	READY
6107	6107	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	第四代四门轿车。	READY
6110	6110	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门外廓。	READY
6111	6111	Sedan	Thema I		4	EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	HIGH	第一系列四门外廓。	READY
6112	6112	Coupe	626 III	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe。	READY
6114	6114	Wagon	626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行版。	READY
6124_prefl	6124	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6124_facelift	6124	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6129_phase_i	6129	Hatchback	Cherry N10	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	HIGH	N10第一阶段外廓。	READY
6129_phase_ii	6129	Hatchback	Cherry N10	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	N10第二阶段外廓。	READY
6133_prefl	6133	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6133_facelift	6133	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6135_prefl	6135	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6135_facelift	6135	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6136	6136	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6138_prefl	6138	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6138_facelift	6138	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6139	6139	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4五门旅行版外廓。	READY
6140	6140	Coupe	100 C1		2	EU-AUDI-100-C1-COUPE-01	HIGH	C1双门Coupe。	READY
6144	6144	Coupe	Isetta 2. Serie		1	EU-BMW-ISETTA-250-COUPE-LATE-01	HIGH	300二期与已缓存250后期共用外廓。	READY
6151_prefl	6151	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6151_facelift	6151	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6154_prefl	6154	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6154_facelift	6154	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6158_prefl	6158	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6158_facelift	6158	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6167_pre67	6167	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-STD-01	HIGH	1967改款前Type 15外廓。	READY
6167_post67	6167	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967改款后Type 15外廓。	READY
6168_prefl	6168	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	HIGH	2013改款前外廓。	READY
6168_facelift	6168	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	2013改款后外廓。	READY
6180	6180	Convertible	Käfer 1302	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	1302敞篷外廓。	READY
6181	6181	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	MEDIUM	VariantName明确1303；输入起始年月早于车型发布。	READY
6182	6182	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967改款后Type 15敞篷外廓。	READY
6183	6183	Convertible	Käfer 1302	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	1302敞篷外廓。	READY
6184	6184	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	1303敞篷外廓。	READY
6185	6185	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	1303敞篷外廓。	READY
6187	6187	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
6188	6188	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
6189	6189	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	3231	1480	1340	Automobile-Catalog 1969 Autobianchi A-112 specifications	https://www.automobile-catalog.com/car/1969/75770/autobianchi_a-112.html
EU-VOLVO-V60-I-WAGON-PREFL-01	4628	1865	1484	Volvo V60 2011 Owner's Manual	https://www.manualshelf.com/manual/volvo/v60-2011/operation-manual-english.html
EU-MINI-COUNTRYMAN-R60-SUV-5D-01	4110	1789	1561	MINI Canada Product Guide 2011	https://www.press.bmwgroup.com/canada/article/attachment/T0091734EN/151238
EU-VOLVO-V60-I-WAGON-FACELIFT-01	4635	1865	1484	Volvo Cars V60 dimensions	https://www.volvocars.com/us/support/car/v60/14w46/article/84c655c2aaaa015ac0a801e801c02b97/5c828b35aab0984dc0a801e801603734/0328ea86b98d614cc0a801e800b575bb/
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Volvo V70 and XC70 Owner's Manual	https://www.manualslib.com/manual/533843/Volvo-V70.html
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Volvo Cars V70 dimensions	https://www.volvocars.com/sg/support/car/v70/article/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-XC60-I-SUV-PREFL-01	4628	1891	1713	Volvo XC60 2011 Owner's Manual	https://www.manualshelf.com/manual/volvo/xc60-2011/operation-manual-english.html
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Volvo Cars XC60 dimensions	https://www.volvocars.com/sg/support/car/xc60/16w17/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
```

## 下一步优先处理

1. 闭合 Autobianchi A111，以及 A112 Series 2–7 的改款边界，批量处理 6064、6068–6073。
2. 处理 Ford Escort Express III–VI、Sierra、Scorpio 的 Van/Hatchback/Sedan 外廓和改款分支。
3. 解决 Nissan Bluebird 910、U11、T12/T72 的驱动方式与代际交叉，避免错误复用现有组。
4. 集中核对 Alpine A110、A310、V6、A610，以及 BMW 02 Touring 等尚无缓存的历史 Coupe/Wagon 尺寸组。
5. 单独解决 VW Transporter T1 Kasten 的宽度口径冲突，以及 Morris Marina Estate 的输入起始年月与车型发布时间差异。

推进信号：CONTINUE

[1]: https://www.manualshelf.com/manual/volvo/v60-2011/operation-manual-english.html?utm_source=chatgpt.com "Volvo V60 - 2011 : Operation Manual"
[2]: https://www.press.bmwgroup.com/canada/article/attachment/T0091734EN/151238?utm_source=chatgpt.com "MINI Canada Product Guide 2011"
[3]: https://www.automobile-catalog.com/car/1969/75770/autobianchi_a-112.html?utm_source=chatgpt.com "1969 Autobianchi A-112 Specs Review (32.3 kW / 44 PS / 43 hp) (since mid-year 1969 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Autobianchi A111 与 A112 的 7 个 Ktype。A112 已按改款阶段及基础版/高配版保险杠造成的长度差异拆分；各阶段均为三门 Hatchback。([德国汽车俱乐部][1])
* 闭合 BMW 02 Series Touring 的 4 个 Ktype，统一关联 E6 三门 Touring 外廓 4110 × 1590 × 1380 mm。([汽车目录][2])
* 本轮新增 22 条 READY 映射、7 个尺寸组；既有 `EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01` 仅复用，不重复输出。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：50
* READY 映射行：72
* PENDING Ktype：50
* 当前已确认尺寸组：37
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6064	6064	Sedan	A111		4	EU-AUTOBIANCHI-A111-SEDAN-4D-01	HIGH	A111四门轿车外廓。	READY
6068_series1	6068	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	HIGH	1971至1972初期外廓。	READY
6068_fl1	6068	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1973至1975第一改款外廓。	READY
6069	6069	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1973至1977两阶段三维一致。	READY
6070_early	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1974至1977早期Abarth外廓。	READY
6070_fl3	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	HIGH	第三次改款Abarth外廓。	READY
6070_fl4	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款外廓。	READY
6070_fl5	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五次改款外廓。	READY
6071_early	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	MEDIUM	1975至1977早期外廓。	READY
6071_fl3	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	MEDIUM	第三次改款基础版外廓。	READY
6071_fl4	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款Junior外廓。	READY
6071_fl5_6	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五至第六次改款Junior外廓。	READY
6072_fl2	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	MEDIUM	改款前期E版本外廓。	READY
6072_fl3	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	HIGH	第三次改款Elegant外廓。	READY
6072_fl4	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款Elite外廓。	READY
6072_fl5_6	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五至第六次改款LX外廓。	READY
6073_early	6073	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1976至1977早期外廓。	READY
6073_fl3	6073	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	HIGH	第三次改款基础版外廓。	READY
6075	6075	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6076	6076	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6077	6077	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6078	6078	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-A111-SEDAN-4D-01	4020	1610	1345	ADAC Autobianchi A111 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a111/1generation/350119/
EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	3230	1480	1340	ADAC Autobianchi A112 1973-1975; ADAC Autobianchi A112 1975-1977	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift/350130/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-2/350133/
EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	3203	1480	1360	ADAC Autobianchi A112 1977-1979	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350134/
EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	3231	1480	1360	ADAC Autobianchi A112 Abarth 1977-1979; ADAC Autobianchi A112 Elegant 1977-1979	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350136/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350135/
EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	3228	1480	1360	ADAC Autobianchi A112 Abarth 1979-1982	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-4/350138/
EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	3268	1480	1360	ADAC Autobianchi A112 Junior 1982-1984; A112.de technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-5/350139/;https://a112.de/Daten.html
EU-BMW-02-E6-TOURING-3D-01	4110	1590	1380	BMW Group Classic 02 Series Touring; Automobile-Catalog BMW Touring 1600	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-811-1.bmw-1602-touring.html;https://www.automobile-catalog.com/car/1971/76955/bmw_touring_1600.html
```

## 下一步优先处理

1. Ford Escort Express III、IV、V、VI 的 Van 外廓与改款边界。
2. Ford Sierra 与 Scorpio 的 Hatchback、Sedan 和四驱外廓关联。
3. Nissan Bluebird 910、U11、T12/T72 的代际及驱动方式边界。
4. Alpine A110、A310、V6、A610 的历史 Coupe 尺寸组。
5. VW Transporter T1、Morris Marina Estate 与剩余 BMW 02 Sedan。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a111/1generation/350119/?utm_source=chatgpt.com "Autobianchi A111 (06/69 - 06/72): Technische Daten, Bilder, Preise | ADAC"
[2]: https://www.automobile-catalog.com/car/1971/76955/bmw_touring_1600.html?utm_source=chatgpt.com "1971 BMW Touring 1600 Specs Review (62.5 kW / 85 PS / 84 hp) (since April 1971 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Ford Escort V 1.6 的三门、五门分支；两种外廓三维相同，但车门结构不同，因此建立独立尺寸组。([汽车目录][1])
* 完成 Ford Sierra 2.9、Honda Civic IV Shuttle、Nissan Bluebird 910/U11/T12 的缓存关联。
* 新建 Audi Coupé B3 quattro、BMW 02 Series Sedan、BMW M3 E30 Sport Evolution 尺寸组。Audi quattro 版本高度按 1365 mm 落盘，不使用普通前驱 Coupé 的 1370/1375 mm 高度。([汽车目录][2])
* 本轮新增 21 条 READY 映射、5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：66
* READY 映射行：93
* PENDING Ktype：34
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6085_3dr	6085	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-PREFL-HATCHBACK-3D-01	HIGH	改款前三门外廓。	READY
6085_5dr	6085	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-PREFL-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
6102	6102	Hatchback	Sierra II		5	EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	HIGH	XR4x4五门外廓。	READY
6103	6103	Hatchback	Sierra II		5	EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	HIGH	XR4x4五门外廓。	READY
6104	6104	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
6105	6105	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH	四门Sedan外廓。	READY
6108	6108	Wagon	Civic IV Shuttle	EE2	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE2五门Shuttle外廓。	READY
6119_u11	6119	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门外廓。	READY
6119_t12	6119	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12四门外廓。	READY
6122	6122	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910改款后四门外廓。	READY
6123	6123	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910改款后四门外廓。	READY
6141	6141	Coupe	Coupé B3	8B	3	EU-AUDI-COUPE-B3-QUATTRO-COUPE-3D-01	HIGH	B3 quattro三门Coupé外廓。	READY
6142	6142	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-2D-01	HIGH	1600-2双门Sedan外廓。	READY
6143	6143	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-2D-01	HIGH	2002 TI双门Sedan外廓。	READY
6145_2dr	6145	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6145_4dr	6145	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6146_2dr	6146	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6146_4dr	6146	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6147_2dr	6147	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6147_4dr	6147	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6148	6148	Sedan	M3 E30 Sport Evolution	E30/2S	2	EU-BMW-M3-E30-SPORT-EVOLUTION-SEDAN-2D-01	HIGH	2.5升Sport Evolution双门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-V-PREFL-HATCHBACK-3D-01	4036	1692	1395	Automobile-Catalog 1990 Ford Escort S 1.6	https://www.automobile-catalog.com/car/1990/944810/ford_escort_s_1_6.html
EU-FORD-ESCORT-V-PREFL-HATCHBACK-5D-01	4036	1692	1395	Automobile-Catalog 1990 Ford Escort 1.6 Ghia	https://www.automobile-catalog.com/car/1990/944675/ford_escort_1_6_ghia.html
EU-AUDI-COUPE-B3-QUATTRO-COUPE-3D-01	4366	1716	1365	Automobile-Catalog 1988 Audi Coupe Quattro catalyst	https://www.automobile-catalog.com/car/1988/62615/audi_coupe_quattro_cat.html
EU-BMW-02-E10-SEDAN-2D-01	4230	1590	1410	Automobile-Catalog BMW 1600-2; AUTO BILD Klassik BMW 2002 ti	https://www.automobile-catalog.com/car/1971/76550/bmw_1600-2.html;https://www.autobild.de/klassik/artikel/bmw-2002-ti-60303.html
EU-BMW-M3-E30-SPORT-EVOLUTION-SEDAN-2D-01	4345	1680	1370	Automobile-Catalog 1990 BMW M3 Sport Evolution	https://www.automobile-catalog.com/car/1990/266600/bmw_m3_sport_evolution.html
```

## 下一步优先处理

1. Ford Escort Express III–VI 的 Van 高度及改款边界。
2. Alpine A110、1300、1600 与 Berlinette 的同源车身聚类。
3. Alpine A310 四缸、V6，以及 Alpine V6 GT/Turbo 和 A610。
4. VW Transporter T1 Kasten、Morris Marina Estate。
5. 剩余 Volvo、VW Käfer早期车身及未闭合历史车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/944675/ford_escort_1_6_ghia.html?utm_source=chatgpt.com "1990 Ford Escort 1.6 Ghia Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1990 for Europe )"
[2]: https://www.automobile-catalog.com/car/1988/62615/audi_coupe_quattro_cat.html?utm_source=chatgpt.com "1988 Audi Coupe Quattro catalyst Specs Review (100 kW / 136 PS / 134 hp) (since mid-year 1988 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成剩余 Alpine A110、A310、GTA V6、A610 共 22 个 Ktype，并复用早期 VW Käfer 既有尺寸组。
* A110 按早期 Series 1 与后期 Series 2 外廓分组；Series 1 为 3850 × 1460 × 1120 mm，Series 2 为 3850 × 1520 × 1130 mm。([汽车目录][1])
* A310 V6 在 1980 年改款后由 4180 × 1640 × 1150 mm 变为 4250 × 1650 × 1150 mm，Ktype 6170 已拆分。([汽车目录][2])
* GTA V6 GT/Turbo 共用 4330 × 1754 × 1197 mm 外廓；A610 使用 4415 × 1762 × 1188 mm。([Alpine][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射行：117
* PENDING Ktype：11
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6149	6149	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	HIGH	早期Berlinette外廓。	READY
6150	6150	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	HIGH	早期Berlinette外廓。	READY
6152	6152	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	MEDIUM	早期1500 Berlinette外廓。	READY
6153	6153	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	MEDIUM	早期1500 Berlinette外廓。	READY
6155	6155	Sedan	Käfer Type 11	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH	早期Type 11标准车身。	READY
6156	6156	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6157	6157	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6159	6159	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6160	6160	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6161	6161	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6162	6162	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 S Series 2外廓。	READY
6163	6163	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SC/SI Series 2外廓。	READY
6164	6164	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SC/SI Series 2外廓。	READY
6165	6165	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸A310外廓。	READY
6166	6166	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸A310外廓。	READY
6169	6169	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸Injection外廓。	READY
6170_prefl	6170	Coupe	A310 V6		2	EU-ALPINE-A310-V6-COUPE-PREFL-01	HIGH	1980改款前V6外廓。	READY
6170_facelift	6170	Coupe	A310 V6		2	EU-ALPINE-A310-V6-COUPE-FACELIFT-01	HIGH	1980改款后V6外廓。	READY
6171	6171	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	后期1300 Berlinette外廓。	READY
6172	6172	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SX Berlinette外廓。	READY
6173	6173	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 GT外廓。	READY
6174	6174	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 Turbo外廓。	READY
6175	6175	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 Turbo外廓。	READY
6179	6179	Coupe	A610		3	EU-ALPINE-A610-COUPE-3D-01	HIGH	A610三门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINE-A110-SERIES-1-COUPE-2D-01	3850	1460	1120	Automobile-Catalog Alpine A110 1100 Berlinette Series 1	https://www.automobile-catalog.com/car/1968/223865/alpine_a-110_1100_100_berlinette.html
EU-ALPINE-A110-SERIES-2-COUPE-2D-01	3850	1520	1130	Automobile-Catalog Alpine Renault A110 Berlinette Series 2	https://www.automobile-catalog.com/car/1970/65420/alpine_renault_a-110_1300_85.html
EU-ALPINE-A310-4CYL-COUPE-2D-01	4180	1640	1150	Automobile-Catalog 1976 Alpine Renault A310 Injection	https://www.automobile-catalog.com/car/1976/65510/alpine_renault_a-310_injection.html
EU-ALPINE-A310-V6-COUPE-PREFL-01	4180	1640	1150	Automobile-Catalog 1979 Alpine Renault A310 V6	https://www.automobile-catalog.com/car/1979/144890/alpine_renault_a-310_v6.html
EU-ALPINE-A310-V6-COUPE-FACELIFT-01	4250	1650	1150	Automobile-Catalog 1981 Alpine Renault A310 V6	https://www.automobile-catalog.com/car/1981/144905/alpine_renault_a-310_v6.html
EU-ALPINE-GTA-V6-COUPE-3D-01	4330	1754	1197	Alpine Deutschland V6 GT and V6 Turbo history; Automobile-Catalog Alpine Renault V6 GT	https://presse.alpinecars.de/alpine-v6-gt-und-v6-turbo-mehr-komfort-mehr-leistung/?lang=deu;https://www.automobile-catalog.com/car/1987/62375/alpine_renault_v6_gt.html
EU-ALPINE-A610-COUPE-3D-01	4415	1762	1188	Automobile-Catalog Alpine Renault A610; Engine in Detail Alpine A610	https://www.automobile-catalog.com/make/alpine_renault/alpine_a610/alpine_a610/1991.html;https://www.engineindetail.com/cars/alpine/a610
```

## 下一步优先处理

1. Ford Escort Express III、IV、V、VI 共 9 个 Ktype，集中核对 Van 外廓和代际改款边界。
2. VW Transporter T1 Kasten 的生产阶段和不含后视镜宽度。
3. Morris Marina Estate 的早期与改款外廓边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1968/223865/alpine_a-110_1100_100_berlinette.html?utm_source=chatgpt.com "1968 Alpine A-110 1100 100 Berlinette Specs Review (70 kW / 95 PS / 94 hp) (up to mid-year 1968 for Europe )"
[2]: https://www.automobile-catalog.com/car/1979/144890/alpine_renault_a-310_v6.html?utm_source=chatgpt.com "1979 Alpine Renault A-310 V6 Specs Review (110.5 kW / 150 PS / 148 hp) (since mid-year 1979 for Europe )"
[3]: https://presse.alpinecars.de/alpine-v6-gt-und-v6-turbo-mehr-komfort-mehr-leistung/?lang=deu&utm_source=chatgpt.com "Alpine V6 GT und V6 Turbo: mehr Komfort, mehr Leistung - Alpine Deutschland Presse-Service"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Morris Marina Mk 1 Estate，Ktype `6063` 关联新尺寸组 `EU-MORRIS-MARINA-MK1-ESTATE-WAGON-5D-01`，三维为 4256 × 1655 × 1436 mm。([汽车目录][1])
* 闭合 Ford Escort IV Express，Ktype `6088` 对应 `ALF` 三门 Van 外廓，三维为 4181 × 1640 × 1594 mm；1.1 L、37 kW/50 PS 的生产区间与输入记录一致。([manualzz.com][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：119
* PENDING Ktype：9
* 已确认尺寸组：51
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6063	6063	Wagon	Marina Mk 1	ADO28	5	EU-MORRIS-MARINA-MK1-ESTATE-WAGON-5D-01	HIGH	Mk 1五门Estate外廓。	READY
6088	6088	Van	Escort IV Express	ALF	3	EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-3D-01	HIGH	ALF三门Express外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORRIS-MARINA-MK1-ESTATE-WAGON-5D-01	4256	1655	1436	Automobile-Catalog 1972 Morris Marina 1.8 Estate	https://www.automobile-catalog.com/car/1972/2035205/morris_marina_1_8_estate.html
EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-3D-01	4181	1640	1594	Ford Escort Mk4 owner's manual; Ford Escort service and repair manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung;https://www.fordmanuals.org/page-1274.html
```

## 下一步优先处理

1. 闭合 Escort III Express `AVA` 的不含后视镜精确宽度，批量处理 Ktype `6095`–`6097`。
2. 闭合 Escort V Express `AVF` 和 Escort VI Express `AVL` 的完整三维，批量处理 Ktype `6090`–`6094`。
3. 将 Ktype `6062` 按 1967 年 T1/T2 代际边界拆分，分别确认标准顶 Kasten 三维。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/2035205/morris_marina_1_8_estate.html?utm_source=chatgpt.com "1972 Morris Marina 1.8 Estate Specs Review (57.5 kW / 78 PS / 77 hp) (since April 1972 for Europe )"
[2]: https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung?utm_source=chatgpt.com "Ford Escort MK4 Bedienungsanleitung | Manualzz"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 VW Transporter T1 Kasten `6062`。该 Ktype 明确对应 `21/23` 系列 1.6、35 kW、48 PS，生产期为 1964 年 8 月至 1968 年 12 月；其后期 T1 标准顶 Kasten 外廓为 4280 × 1750 × 1940 mm。([werkstatteinkauf.de][1])
* 修正 Escort IV Express `6088`：原单一高度组拆为 Type 35 与 Type 55 两种载重/悬架高度分支，分别为 1568 mm 和 1594 mm；长度、宽度均为 4181 × 1640 mm。([manualzz.com][2])
* 闭合 Escort VI Express `6093`、`6094`，按 Model 55 与 Model 75 两种外廓高度拆分；尺寸为 4290 × 1688 × 1591/1603 mm。([ikz.de][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射行：125
* PENDING Ktype：6
* 当前有效尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6062	6062	Van	Transporter T1			EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	后期T1标准顶Kasten外廓；21/23具体代码未由输入区分。	READY
6088_type35	6088	Van	Escort IV Express	ALF	3	EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-TYPE35-01	HIGH	Type 35载重高度分支。	READY
6088_type55	6088	Van	Escort IV Express	ALF	3	EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-TYPE55-01	HIGH	Type 55载重高度分支。	READY
6093_type55	6093	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	HIGH	Model 55载重高度分支。	READY
6093_type75	6093	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	HIGH	Model 75载重高度分支。	READY
6094_type55	6094	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	HIGH	Model 55载重高度分支。	READY
6094_type75	6094	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	HIGH	Model 75载重高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	4280	1750	1940	Fahrzeugseiten VW Bulli T1 Kastenwagen; JP Group T1 Kasten 1.6 application data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html;https://www.werkstatteinkauf.de/items/zundverteiler-einzelteile-22208/jp-group-8191500202-kondensator-zundanlage-bosch/45963878/
EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-TYPE35-01	4181	1640	1568	Ford Escort Mk4 official owner manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-IV-ALF-EXPRESS-VAN-TYPE55-01	4181	1640	1594	Ford Escort Mk4 official owner manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	4290	1688	1591	IKZ Haustechnik Ford Escort Express technical data	https://www.ikz.de/ikz-archiv/1997/22/9722052.php
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	4290	1688	1603	IKZ Haustechnik Ford Escort Express technical data	https://www.ikz.de/ikz-archiv/1997/22/9722052.php
```

## 下一步优先处理

1. 闭合 Escort V Express `6090`–`6092` 的 AVF 改款前保险杠长度和 Model 55/75 高度边界。
2. 闭合 Escort III Express `6095`–`6097` 的 AVA 精确不含后视镜宽度及不同载重高度分支。
3. PENDING 清零后立即执行一次机械校验并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.werkstatteinkauf.de/items/zundverteiler-einzelteile-22208/jp-group-8191500202-kondensator-zundanlage-bosch/45963878/?utm_source=chatgpt.com "JP GROUP 8191500202 Kondensator, Zündanlage BOSCH / Zündverteiler/-einzelteile: Zünd-/Glühanlage > PKW Ersatzteile"
[2]: https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung?utm_source=chatgpt.com "Ford Escort MK4 Bedienungsanleitung | Manualzz"
[3]: https://www.ikz.de/ikz-archiv/1997/22/9722052.php?utm_source=chatgpt.com "IKZ-HAUSTECHNIK"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5701-5800_ktype_dimension_mapping_final.tsv
- all_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后 6 个 PENDING 已闭合：Escort III Express `6095–6097` 关联 AVA 车身；Escort V Express `6090–6092` 按早期车身和改款后 Model 55/75 拆分。
* 修正 Ktype `6088` 的 BodyCode 为 `AVF`，保留 Type 35、Type 55 两个高度分支。
* Ktype `6101` 的 2.9i Sedan 高度确认为 1440 mm，与累计表既有 1450 mm 尺寸组冲突；未覆盖原组，已创建 `EU-FORD-SCORPIO-I-SEDAN-02`。([ford-express.de][1])
* 已完成最终机械校验并生成指定下载文件。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：137
* PENDING Ktype：0
* DIMENSION_GROUP：69
* `id` 与 `DIMENSION_GROUP_ID` 均唯一。
* 69 个尺寸组全部被引用，137 条映射引用全部闭合。
* 长宽高、来源及 SourceURL 均非空。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6062	6062	Van	Transporter T1			EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	后期T1标准顶Kasten外廓；21/23具体代码未由输入区分。	READY
6063	6063	Wagon	Marina Mk 1	ADO28	5	EU-MORRIS-MARINA-MK1-ESTATE-WAGON-5D-01	HIGH	Mk 1五门Estate外廓。	READY
6064	6064	Sedan	A111		4	EU-AUTOBIANCHI-A111-SEDAN-4D-01	HIGH	A111四门轿车外廓。	READY
6065	6065	Hatchback	A112 Series 1		3	EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	HIGH	首代三门外廓。	READY
6066	6066	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6067	6067	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6068_series1	6068	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	HIGH	1971至1972初期外廓。	READY
6068_fl1	6068	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1973至1975第一改款外廓。	READY
6069	6069	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1973至1977两阶段三维一致。	READY
6070_early	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1974至1977早期Abarth外廓。	READY
6070_fl3	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	HIGH	第三次改款Abarth外廓。	READY
6070_fl4	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款外廓。	READY
6070_fl5	6070	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五次改款外廓。	READY
6071_early	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	MEDIUM	1975至1977早期外廓。	READY
6071_fl3	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	MEDIUM	第三次改款基础版外廓。	READY
6071_fl4	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款Junior外廓。	READY
6071_fl5_6	6071	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五至第六次改款Junior外廓。	READY
6072_fl2	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	MEDIUM	改款前期E版本外廓。	READY
6072_fl3	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	HIGH	第三次改款Elegant外廓。	READY
6072_fl4	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	HIGH	第四次改款Elite外廓。	READY
6072_fl5_6	6072	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	HIGH	第五至第六次改款LX外廓。	READY
6073_early	6073	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	HIGH	1976至1977早期外廓。	READY
6073_fl3	6073	Hatchback	A112 1st Generation		3	EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	HIGH	第三次改款基础版外廓。	READY
6074	6074	SUV	Countryman R60	R60	5	EU-MINI-COUNTRYMAN-R60-SUV-5D-01	HIGH	输入Kombi；R60 Countryman按SUV外廓归类。	READY
6075	6075	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6076	6076	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6077	6077	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6078	6078	Wagon	02 Series Touring	E6	3	EU-BMW-02-E6-TOURING-3D-01	HIGH	E6三门Touring外廓。	READY
6079	6079	MPV	Voyager II	ES	5	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH	ES代五门MPV。	READY
6080	6080	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH	早期CX I四门轿车外廓。	READY
6081	6081	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH	早期CX I四门轿车外廓。	READY
6082	6082	Wagon	CX I		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	HIGH	CX I Break五门外廓。	READY
6085_3dr	6085	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-PREFL-HATCHBACK-3D-01	HIGH	改款前三门外廓。	READY
6085_5dr	6085	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-PREFL-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
6086	6086	Wagon	Escort V		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Escort V改款前旅行版。	READY
6087_prefl	6087	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6087_facelift	6087	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6088_type35	6088	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	HIGH	Type 35载重高度分支。	READY
6088_type55	6088	Van	Escort IV Express	AVF	3	EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	HIGH	Type 55载重高度分支。	READY
6090_prefl_type55	6090	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-PREFL-TYPE55-01	MEDIUM	1990至1992早期Type 55外廓。	READY
6090_facelift_type55	6090	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE55-01	HIGH	1992改款后Model 55外廓。	READY
6090_facelift_type75	6090	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE75-01	HIGH	1992改款后Model 75外廓。	READY
6091_prefl_type55	6091	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-PREFL-TYPE55-01	MEDIUM	1990至1992早期Type 55外廓。	READY
6091_facelift_type55	6091	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE55-01	HIGH	1992改款后Model 55外廓。	READY
6091_facelift_type75	6091	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE75-01	HIGH	1992改款后Model 75外廓。	READY
6092_prefl_type55	6092	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-PREFL-TYPE55-01	MEDIUM	1990至1992早期Type 55外廓。	READY
6092_facelift_type55	6092	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE55-01	HIGH	1992改款后Model 55外廓。	READY
6092_facelift_type75	6092	Van	Escort V Express	AVL	3	EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE75-01	HIGH	1992改款后Model 75外廓。	READY
6093_type55	6093	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	HIGH	Model 55载重高度分支。	READY
6093_type75	6093	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	HIGH	Model 75载重高度分支。	READY
6094_type55	6094	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	HIGH	Model 55载重高度分支。	READY
6094_type75	6094	Van	Escort VI Express	AVL	3	EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	HIGH	Model 75载重高度分支。	READY
6095	6095	Van	Escort III Express	AVA	3	EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	HIGH	AVA三门Express 55外廓。	READY
6096	6096	Van	Escort III Express	AVA	3	EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	HIGH	AVA三门Express 55外廓。	READY
6097	6097	Van	Escort III Express	AVA	3	EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	HIGH	AVA三门Express 55外廓。	READY
6101	6101	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-02	HIGH	2.9i四门Sedan外廓；与既有1450 mm高度组冲突，使用新组。	READY
6102	6102	Hatchback	Sierra II		5	EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	HIGH	XR4x4五门外廓。	READY
6103	6103	Hatchback	Sierra II		5	EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	HIGH	XR4x4五门外廓。	READY
6104	6104	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
6105	6105	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH	四门Sedan外廓。	READY
6107	6107	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	第四代四门轿车。	READY
6108	6108	Wagon	Civic IV Shuttle	EE2	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE2五门Shuttle外廓。	READY
6110	6110	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门外廓。	READY
6111	6111	Sedan	Thema I		4	EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	HIGH	第一系列四门外廓。	READY
6112	6112	Coupe	626 III	GD	2	EU-MAZDA-626-III-GD-COUPE-2D-01	HIGH	GD双门Coupe。	READY
6114	6114	Wagon	626 III	GV	5	EU-MAZDA-626-III-GV-WAGON-5D-01	HIGH	GV五门旅行版。	READY
6119_u11	6119	Sedan	Bluebird U11	U11	4	EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	HIGH	U11四门外廓。	READY
6119_t12	6119	Sedan	Bluebird T12	T12	4	EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	HIGH	T12四门外廓。	READY
6122	6122	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910改款后四门外廓。	READY
6123	6123	Sedan	Bluebird 910	910	4	EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	HIGH	910改款后四门外廓。	READY
6124_prefl	6124	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6124_facelift	6124	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6129_phase_i	6129	Hatchback	Cherry N10	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	HIGH	N10第一阶段外廓。	READY
6129_phase_ii	6129	Hatchback	Cherry N10	N10		EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	HIGH	N10第二阶段外廓。	READY
6133_prefl	6133	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6133_facelift	6133	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6135_prefl	6135	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6135_facelift	6135	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6136	6136	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6138_prefl	6138	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前外廓；输入未区分门数。	READY
6138_facelift	6138	Sedan	80 B1			EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	B1改款后外廓；输入未区分门数。	READY
6139	6139	Wagon	80 B4	8C	5	EU-AUDI-80-B4-WAGON-01	HIGH	B4五门旅行版外廓。	READY
6140	6140	Coupe	100 C1		2	EU-AUDI-100-C1-COUPE-01	HIGH	C1双门Coupe。	READY
6141	6141	Coupe	Coupé B3	8B	3	EU-AUDI-COUPE-B3-QUATTRO-COUPE-3D-01	HIGH	B3 quattro三门Coupé外廓。	READY
6142	6142	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-2D-01	HIGH	1600-2双门Sedan外廓。	READY
6143	6143	Sedan	02 Series	E10	2	EU-BMW-02-E10-SEDAN-2D-01	HIGH	2002 TI双门Sedan外廓。	READY
6144	6144	Coupe	Isetta 2. Serie		1	EU-BMW-ISETTA-250-COUPE-LATE-01	HIGH	300二期与已缓存250后期共用外廓。	READY
6145_2dr	6145	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6145_4dr	6145	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6146_2dr	6146	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6146_4dr	6146	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6147_2dr	6147	Sedan	3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	HIGH	E30双门Sedan外廓。	READY
6147_4dr	6147	Sedan	3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	HIGH	E30四门Sedan外廓。	READY
6148	6148	Sedan	M3 E30 Sport Evolution	E30/2S	2	EU-BMW-M3-E30-SPORT-EVOLUTION-SEDAN-2D-01	HIGH	2.5升Sport Evolution双门外廓。	READY
6149	6149	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	HIGH	早期Berlinette外廓。	READY
6150	6150	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	HIGH	早期Berlinette外廓。	READY
6151_prefl	6151	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6151_facelift	6151	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6152	6152	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	MEDIUM	早期1500 Berlinette外廓。	READY
6153	6153	Coupe	A110 Berlinette Series 1		2	EU-ALPINE-A110-SERIES-1-COUPE-2D-01	MEDIUM	早期1500 Berlinette外廓。	READY
6154_prefl	6154	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6154_facelift	6154	Wagon	V60 I		5	EU-VOLVO-V60-I-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6155	6155	Sedan	Käfer Type 11	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH	早期Type 11标准车身。	READY
6156	6156	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6157	6157	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6158_prefl	6158	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	2013改款前外廓。	READY
6158_facelift	6158	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	2013改款后外廓。	READY
6159	6159	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6160	6160	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6161	6161	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	Series 2 Berlinette外廓。	READY
6162	6162	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 S Series 2外廓。	READY
6163	6163	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SC/SI Series 2外廓。	READY
6164	6164	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SC/SI Series 2外廓。	READY
6165	6165	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸A310外廓。	READY
6166	6166	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸A310外廓。	READY
6167_pre67	6167	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-STD-01	HIGH	1967改款前Type 15外廓。	READY
6167_post67	6167	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967改款后Type 15外廓。	READY
6168_prefl	6168	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	HIGH	2013改款前外廓。	READY
6168_facelift	6168	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	2013改款后外廓。	READY
6169	6169	Coupe	A310 4-cylinder		2	EU-ALPINE-A310-4CYL-COUPE-2D-01	HIGH	四缸Injection外廓。	READY
6170_prefl	6170	Coupe	A310 V6		2	EU-ALPINE-A310-V6-COUPE-PREFL-01	HIGH	1980改款前V6外廓。	READY
6170_facelift	6170	Coupe	A310 V6		2	EU-ALPINE-A310-V6-COUPE-FACELIFT-01	HIGH	1980改款后V6外廓。	READY
6171	6171	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	后期1300 Berlinette外廓。	READY
6172	6172	Coupe	A110 Berlinette Series 2		2	EU-ALPINE-A110-SERIES-2-COUPE-2D-01	HIGH	1600 SX Berlinette外廓。	READY
6173	6173	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 GT外廓。	READY
6174	6174	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 Turbo外廓。	READY
6175	6175	Coupe	GTA V6		3	EU-ALPINE-GTA-V6-COUPE-3D-01	HIGH	GTA V6 Turbo外廓。	READY
6179	6179	Coupe	A610		3	EU-ALPINE-A610-COUPE-3D-01	HIGH	A610三门Coupe外廓。	READY
6180	6180	Convertible	Käfer 1302	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	1302敞篷外廓。	READY
6181	6181	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	MEDIUM	VariantName明确1303；输入起始年月早于车型发布。	READY
6182	6182	Convertible	Käfer Type 15	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967改款后Type 15敞篷外廓。	READY
6183	6183	Convertible	Käfer 1302	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	1302敞篷外廓。	READY
6184	6184	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	1303敞篷外廓。	READY
6185	6185	Convertible	Käfer 1303	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	1303敞篷外廓。	READY
6187	6187	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
6188	6188	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
6189	6189	Coupe	Karmann Ghia Type 14	Type 14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14双门Coupe外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5701-5800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	4280	1750	1940	Fahrzeugseiten VW Bulli T1 Kastenwagen; JP Group T1 Kasten 1.6 application data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html;https://www.werkstatteinkauf.de/items/zundverteiler-einzelteile-22208/jp-group-8191500202-kondensator-zundanlage-bosch/45963878/
EU-MORRIS-MARINA-MK1-ESTATE-WAGON-5D-01	4256	1655	1436	Automobile-Catalog 1972 Morris Marina 1.8 Estate	https://www.automobile-catalog.com/car/1972/2035205/morris_marina_1_8_estate.html
EU-AUTOBIANCHI-A111-SEDAN-4D-01	4020	1610	1345	ADAC Autobianchi A111 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a111/1generation/350119/
EU-AUTOBIANCHI-A112-SERIES-1-HATCHBACK-3D-01	3231	1480	1340	Automobile-Catalog 1969 Autobianchi A-112 specifications	https://www.automobile-catalog.com/car/1969/75770/autobianchi_a-112.html
EU-VOLVO-V60-I-WAGON-PREFL-01	4628	1865	1484	Volvo V60 2011 Owner's Manual	https://www.manualshelf.com/manual/volvo/v60-2011/operation-manual-english.html
EU-AUTOBIANCHI-A112-FL1-2-HATCHBACK-3D-01	3230	1480	1340	ADAC Autobianchi A112 1973-1975; ADAC Autobianchi A112 1975-1977	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift/350130/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-2/350133/
EU-AUTOBIANCHI-A112-FL3-TRIM-HATCHBACK-3D-01	3231	1480	1360	ADAC Autobianchi A112 Abarth 1977-1979; ADAC Autobianchi A112 Elegant 1977-1979	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350136/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350135/
EU-AUTOBIANCHI-A112-FL4-HATCHBACK-3D-01	3228	1480	1360	ADAC Autobianchi A112 Abarth 1979-1982	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-4/350138/
EU-AUTOBIANCHI-A112-FL5-6-HATCHBACK-3D-01	3268	1480	1360	ADAC Autobianchi A112 Junior 1982-1984; A112.de technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-5/350139/;https://a112.de/Daten.html
EU-AUTOBIANCHI-A112-FL3-BASE-HATCHBACK-3D-01	3203	1480	1360	ADAC Autobianchi A112 1977-1979	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/autobianchi/a112/1generation-facelift-3/350134/
EU-MINI-COUNTRYMAN-R60-SUV-5D-01	4110	1789	1561	MINI Canada Product Guide 2011	https://www.press.bmwgroup.com/canada/article/attachment/T0091734EN/151238
EU-BMW-02-E6-TOURING-3D-01	4110	1590	1380	BMW Group Classic 02 Series Touring; Automobile-Catalog BMW Touring 1600	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-811-1.bmw-1602-touring.html;https://www.automobile-catalog.com/car/1971/76955/bmw_touring_1600.html
EU-CHRYSLER-VOYAGER-II-ES-MPV-01	4525	1830	1707	Automobile-Catalog 1993 Chrysler Voyager 2.5 TD	https://www.automobile-catalog.com/car/1993/518180/chrysler_voyager_2_5_td.html
EU-CITROEN-CX-I-SEDAN-4D-01	4659	1734	1360	Automobile-Catalog Citroën CX I 2000	https://www.automobile-catalog.com/car/1979/532730/citroen_cx_2000_reflex.html
EU-CITROEN-CX-I-BREAK-WAGON-5D-01	4922	1734	1465	Automobile-Catalog 1978 Citroën CX Break 2000 Confort	https://www.automobile-catalog.com/car/1978/38840/citroen_cx_break_2000_confort.html
EU-FORD-ESCORT-V-PREFL-HATCHBACK-3D-01	4036	1692	1395	Automobile-Catalog 1990 Ford Escort S 1.6	https://www.automobile-catalog.com/car/1990/944810/ford_escort_s_1_6.html
EU-FORD-ESCORT-V-PREFL-HATCHBACK-5D-01	4036	1692	1395	Automobile-Catalog 1990 Ford Escort 1.6 Ghia	https://www.automobile-catalog.com/car/1990/944675/ford_escort_1_6_ghia.html
EU-FORD-ESCORT-V-WAGON-PREFL-01	4268	1690	1414	Automobile-Catalog 1990 Ford Escort Turnier 1.6i CL	https://www.automobile-catalog.com/car/1990/945335/ford_escort_turnier_1_6i_cl.html
EU-VOLVO-V60-I-WAGON-FACELIFT-01	4635	1865	1484	Volvo Cars V60 dimensions	https://www.volvocars.com/us/support/car/v60/14w46/article/84c655c2aaaa015ac0a801e801c02b97/5c828b35aab0984dc0a801e801603734/0328ea86b98d614cc0a801e800b575bb/
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE35-01	4181	1640	1568	Ford Escort Mk4 official owner manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-IV-AVF-EXPRESS-VAN-TYPE55-01	4181	1640	1594	Ford Escort Mk4 official owner manual	https://manualzz.com/doc/4656044/ford-escort-mk4-auto-bedienungsanleitung
EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-PREFL-TYPE55-01	4250	1650	1594	Swedish Transport Agency registration record via Fordonskollen; Ford Express model variants	https://www.fordonskollen.se/fordon/OWH860;https://www.ford-express.de/technische_daten/modellvarianten/
EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE55-01	4290	1688	1591	IKZ Ford Escort Express technical data; Swedish registration record	https://www.ikz.de/ikz-archiv/1997/22/9722052.php;https://www.fordonskollen.se/fordon/PWZ781
EU-FORD-ESCORT-V-AVL-EXPRESS-VAN-FACELIFT-TYPE75-01	4290	1688	1603	IKZ Ford Escort Express technical data	https://www.ikz.de/ikz-archiv/1997/22/9722052.php
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	4290	1688	1591	IKZ Ford Escort Express technical data	https://www.ikz.de/ikz-archiv/1997/22/9722052.php
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	4290	1688	1603	IKZ Ford Escort Express technical data	https://www.ikz.de/ikz-archiv/1997/22/9722052.php
EU-FORD-ESCORT-III-AVA-EXPRESS-VAN-55-01	4129	1640	1568	Ford Escort Service and Repair Manual	https://www.fordmanuals.org/page-1274.html
EU-FORD-SCORPIO-I-SEDAN-02	4744	1766	1440	Automobile-Catalog 1990 Ford Scorpio 2.9i Ghia	https://www.automobile-catalog.com/car/1990/939605/ford_scorpio_4t__2_9i_ghia_cat.html
EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	4459	1725	1378	Automobile-Catalog Ford Sierra XR 4x4	https://www.automobile-catalog.com/car/1987/932600/ford_sierra_xr_4x4.html
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407	Automobile-Catalog 1990 Ford Sierra 2.9i GL	https://www.automobile-catalog.com/car/1990/934760/ford_sierra_2_9i_gl_cat.html
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407	Auto-Data Ford Sierra model dimensions	https://www.auto-data.net/en/ford-sierra-model-802
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4295	1695	1360	Auto-Data Honda Civic IV generation	https://www.auto-data.net/en/honda-civic-iv-generation-2636
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	4105	1690	1515	Auto-Data Honda Civic IV Shuttle generation	https://www.auto-data.net/en/honda-civic-iv-shuttle-generation-2637
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385	Auto-Data Lancia Prisma 831 AB generation	https://www.auto-data.net/en/lancia-prisma-831-ab-generation-1164
EU-LANCIA-THEMA-I-SEDAN-SERIES-1-01	4590	1752	1433	Automobile-Catalog 1987 Lancia Thema i.e.	https://www.automobile-catalog.com/car/1987/1379840/lancia_thema_i_e_.html
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360	Automobile-Catalog 1990 Mazda 626 2.0i 16V GT Coupe	https://www.automobile-catalog.com/car/1990/1636970/mazda_626_2_0i_16v_gt_coupe.html
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430	Automobile-Catalog 1990 Mazda 626 2.0i 16V GT Estate	https://www.automobile-catalog.com/car/1990/1636955/mazda_626_2_0i_16v_gt_estate.html
EU-NISSAN-BLUEBIRD-U11-SEDAN-4D-01	4360	1690	1400	Auto-Data Nissan Bluebird U11 generation	https://www.auto-data.net/en/nissan-bluebird-u11-generation-262
EU-NISSAN-BLUEBIRD-T12-SEDAN-4D-01	4405	1690	1395	Nissan Bluebird T12 service specifications	https://www.nissanbook.ru/en/Teana/Bluebird-T12/main/service/obschie-harakteristiki-avtomobilya
EU-NISSAN-BLUEBIRD-910-SEDAN-4D-FACELIFT-01	4395	1655	1400	Automobile-Catalog 1983 Datsun Bluebird 2.0 GLE	https://www.automobile-catalog.com/car/1983/2119370/datsun_bluebird_2_0_gle.html
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-I-01	3890	1600	1360	Automobile-Catalog 1979 Datsun Cherry 1.0 3-door	https://www.automobile-catalog.com/car/1979/2105345/datsun_cherry_1_0_3door.html
EU-NISSAN-CHERRY-N10-HATCHBACK-PHASE-II-01	3960	1620	1360	Automobile-Catalog 1982 Datsun Cherry 1.3 GL 3-door	https://www.automobile-catalog.com/car/1982/2105570/datsun_cherry_1_3_gl_3door.html
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362	Automobile-Catalog 1975 Audi 80 GL	https://www.automobile-catalog.com/car/1975/165260/audi_80_gl.html
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360	Automobile-Catalog 1977 Audi 80	https://www.automobile-catalog.com/car/1977/165395/audi_80.html
EU-AUDI-80-B4-WAGON-01	4482	1695	1408	Automobile-Catalog 1993 Audi 80 Avant 2.0	https://www.automobile-catalog.com/car/1993/236690/audi_80_avant_2_0.html
EU-AUDI-100-C1-COUPE-01	4398	1750	1340	Automobile-Catalog 1973 Audi 100 Coupé S	https://www.automobile-catalog.com/car/1973/74765/audi_100_coupe_s_automatic.html
EU-AUDI-COUPE-B3-QUATTRO-COUPE-3D-01	4366	1716	1365	Automobile-Catalog 1988 Audi Coupé quattro	https://www.automobile-catalog.com/car/1988/62615/audi_coupe_quattro_cat.html
EU-BMW-02-E10-SEDAN-2D-01	4230	1590	1410	Automobile-Catalog BMW 1600-2; AUTO BILD Klassik BMW 2002 ti	https://www.automobile-catalog.com/car/1971/76550/bmw_1600-2.html;https://www.autobild.de/klassik/artikel/bmw-2002-ti-60303.html
EU-BMW-ISETTA-250-COUPE-LATE-01	2355	1380	1340	Automobile-Catalog BMW Isetta 300 second series	https://www.automobile-catalog.com/car/1960/1449065/bmw_isetta_300_2__serie.html
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	Automobile-Catalog 1985 BMW 316	https://www.automobile-catalog.com/car/1985/264920/bmw_316_4-speed.html
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	Automobile-Catalog 1985 BMW 316	https://www.automobile-catalog.com/car/1985/265160/bmw_316_5-speed.html
EU-BMW-M3-E30-SPORT-EVOLUTION-SEDAN-2D-01	4345	1680	1370	Automobile-Catalog 1990 BMW M3 Sport Evolution	https://www.automobile-catalog.com/car/1990/266600/bmw_m3_sport_evolution.html
EU-ALPINE-A110-SERIES-1-COUPE-2D-01	3850	1460	1120	Automobile-Catalog Alpine A110 1100 Berlinette Series 1	https://www.automobile-catalog.com/car/1968/223865/alpine_a-110_1100_100_berlinette.html
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500	Volkswagen Classic Beetle 1100 profile; CarsPlusPlus 1948 Beetle dimensions	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1100-profile-19569;https://carsplusplus.com/specs1948/volkswagen_beetle.php
EU-ALPINE-A110-SERIES-2-COUPE-2D-01	3850	1520	1130	Automobile-Catalog Alpine Renault A110 Berlinette Series 2	https://www.automobile-catalog.com/car/1970/65420/alpine_renault_a-110_1300_85.html
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Volvo V70 and XC70 Owner's Manual	https://www.manualslib.com/manual/533843/Volvo-V70.html
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Volvo Cars V70 dimensions	https://www.volvocars.com/sg/support/car/v70/article/18f77489f78f457dc0a801e800a04016/
EU-ALPINE-A310-4CYL-COUPE-2D-01	4180	1640	1150	Automobile-Catalog 1976 Alpine Renault A310 Injection	https://www.automobile-catalog.com/car/1976/65510/alpine_renault_a-310_injection.html
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500	Volkswagen Classic Beetle 1200 Cabriolet profile; Carspector 1964 Beetle Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1200-cabriolet-profile-19615;https://carspector.com/car/Volkswagen/056046/
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500	Volkswagen Classic Beetle 1500 Cabriolet profile; Carfolio 1970 Beetle 1500 dimensions	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-cabriolet-profile-19627;https://www.carfolio.com/volkswagen-%27beetle%27-1500-17666
EU-VOLVO-XC60-I-SUV-PREFL-01	4628	1891	1713	Volvo XC60 2011 Owner's Manual	https://www.manualshelf.com/manual/volvo/xc60-2011/operation-manual-english.html
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Volvo Cars XC60 dimensions	https://www.volvocars.com/sg/support/car/xc60/16w17/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-ALPINE-A310-V6-COUPE-PREFL-01	4180	1640	1150	Automobile-Catalog 1979 Alpine Renault A310 V6	https://www.automobile-catalog.com/car/1979/144890/alpine_renault_a-310_v6.html
EU-ALPINE-A310-V6-COUPE-FACELIFT-01	4250	1650	1150	Automobile-Catalog 1981 Alpine Renault A310 V6	https://www.automobile-catalog.com/car/1981/144905/alpine_renault_a-310_v6.html
EU-ALPINE-GTA-V6-COUPE-3D-01	4330	1754	1197	Alpine Deutschland V6 GT and V6 Turbo history; Automobile-Catalog Alpine Renault V6 GT	https://presse.alpinecars.de/alpine-v6-gt-und-v6-turbo-mehr-komfort-mehr-leistung/?lang=deu;https://www.automobile-catalog.com/car/1987/62375/alpine_renault_v6_gt.html
EU-ALPINE-A610-COUPE-3D-01	4415	1762	1188	Automobile-Catalog Alpine Renault A610; Engine in Detail Alpine A610	https://www.automobile-catalog.com/make/alpine_renault/alpine_a610/alpine_a610/1991.html;https://www.engineindetail.com/cars/alpine/a610
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500	Volkswagen 1302 owner manual; Volkswagen Classic 1302 Cabriolet profile	https://www.scribd.com/document/550618562/August-1971-1302-Beetle-Owners-Manual;https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-cabriolet-profile-19618
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500	Volkswagen Classic 1303 Cabriolet profile; Volkswagen 1302/1303 dimensional specification	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1303-cabriolet-profile-19624;https://www.scribd.com/document/550618562/August-1971-1302-Beetle-Owners-Manual
EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	4140	1634	1330	Volkswagen Classic Karmann Ghia Type 14 Coupé profile; technical specifications	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-type-14-coupe-profile-19631;https://www.forumsamochodowe.pl/dane-techniczne/21970-volkswagen-karmann-ghia-type-14-1-2-mt-30-km-coupe
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5701-5800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ford-express.de/technische_daten/modellvarianten/ "https://www.ford-express.de/technische_daten/modellvarianten/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5701-5800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5701-5800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7277 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2267 行）

