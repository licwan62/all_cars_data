# 任务：all 第 301-400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0004__1abf47d9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 301-400 行

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
all 第 301-400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Doblo	1.4	Pritsche/Fahrgestell	Frontantrieb	Benzin	88	120	Oct 2011	Dec 2023	2025-02-03	120297
Fiat	Doblo	1.4 Natural Power	Pritsche/Fahrgestell	Frontantrieb	Benzin/Erdgas (CNG)	88	120	Jun 2010	Dec 2023	2025-02-03	120298
Subaru	Legacy v station wagon	2.0 I AWD	Kombi	Allrad	Benzin	110	150	Jun 2012	Dec 2014	2024-03-01	120299
Nissan	Qashqai ii	2.0 ALL Mode 4x4-i	SUV	Allrad	Benzin	106	144	Dec 2013	Apr 2021	2026-06-01	120309
Toyota	Proace	1.6 D4D	Bus	Frontantrieb	Diesel	70	95	Feb 2016	Apr 2020	2025-02-03	120326
Toyota	Proace	1.6 D4D	Bus	Frontantrieb	Diesel	85	116	Feb 2016	Apr 2020	2025-02-03	120328
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	110	150	Feb 2016	Dec 2022	2026-01-01	120331
Opel	Mokka	1.4 4X4	SUV	Allrad	Benzin	112	152	Jun 2016	Dec 2019	2025-06-01	120340
Opel	Corsa e	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	64	87	Nov 2015	-	2024-03-01	120359
Tesla	Model x	75D AWD	Schrägheck	Allrad	Elektro	386	525	Jun 2016	Apr 2026	2026-06-01	120372
Mclaren	570gt	3.8	Coupe	Heckantrieb	Benzin	419	570	Jun 2016	-	2024-03-01	120389
Mclaren	675lt spider	3.8	Cabriolet	Heckantrieb	Benzin	496	675	Aug 2016	-	2024-03-01	120391
Chevrolet	Camaro	6.2	Coupe	Heckantrieb	Benzin	333	453	Jun 2016	-	2024-03-01	120496
Chevrolet	Camaro	6.2	Cabriolet	Heckantrieb	Benzin	333	453	Jun 2016	-	2024-03-01	120497
BMW	X5	Xdrive 40 I	SUV	Allrad	Benzin	225	306	Jan 2012	Jun 2013	2024-03-01	120501
Ford	Ka+ iii	1.2	Schrägheck	Frontantrieb	Benzin	51	70	Jun 2016	Dec 2020	2026-04-01	120503
Ford	Ka+ iii	1.2 Ti-vct	Schrägheck	Frontantrieb	Benzin	63	85	Jun 2016	Dec 2020	2026-04-01	120504
Hummer	Hummer h2 sut	6.2 Flexfuel AWD	Pick-up	Allrad	Benzin/Ethanol	293	398	Sep 2008	Dec 2009	2024-03-01	120505
Volvo	S90 ii	T5	Stufenheck	Frontantrieb	Benzin	187	254	Mar 2016	Dec 2021	2024-05-01	120506
Volvo	S80 ii	T5	Stufenheck	Frontantrieb	Benzin	162	220	Jan 2014	Dec 2016	2024-03-01	120516
BMW	3	320 I	Schrägheck	Heckantrieb	Benzin	135	184	Jul 2016	-	2024-03-01	120517
BMW	3	320 I Xdrive	Schrägheck	Allrad	Benzin	135	184	Jul 2016	-	2024-03-01	120518
Hyundai	Ioniq	1.6 GDI Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	104	141	Mar 2016	Jul 2022	2024-05-01	120519
Hyundai	Ioniq	Electric	Schrägheck	Frontantrieb	Elektro	88	120	Mar 2016	Aug 2019	2024-05-01	120520
Volvo	Xc90 ii	T5 AWD	SUV	Allrad	Benzin	183	249	Feb 2016	Dec 2018	2024-03-01	120522
Volvo	V60 i	2.0 Polestar AWD	Kombi	Allrad	Benzin	270	367	Jun 2015	May 2018	2024-03-01	120524
Volvo	S60 ii	2.0 Polestar AWD	Stufenheck	Allrad	Benzin	270	367	Jun 2015	May 2018	2024-03-01	120525
Tesla	Model s	75	Schrägheck	Heckantrieb	Elektro	285	388	Nov 2016	Apr 2026	2026-06-01	120531
Tesla	Model s	75D AWD	Schrägheck	Allrad	Elektro	386	525	Jun 2016	Apr 2026	2026-06-01	120532
BMW	4	425 D	Coupe	Heckantrieb	Diesel	155	211	Mar 2016	Feb 2018	2024-03-01	120539
BMW	3	325 D	Schrägheck	Heckantrieb	Diesel	165	224	Jul 2016	Feb 2018	2024-03-01	120542
Borgward	Bx7	28tgdi	SUV	Frontantrieb	Benzin	165	224	Apr 2016	Dec 2021	2024-03-01	120545
Borgward	Bx7	28tgdi AWD	SUV	Allrad	Benzin	165	224	Apr 2016	Dec 2021	2024-03-01	120549
Audi	A4 b9 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	185	252	May 2016	Oct 2019	2024-03-01	120565
Maserati	Levante	3.0 D Q4	SUV	Allrad	Diesel	184	250	Jun 2016	-	2024-03-01	120566
Audi	A4 b9 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	183	249	May 2016	Oct 2019	2024-03-01	120567
Ssangyong	Xlv	E-xgi 160	SUV	Frontantrieb	Benzin	94	128	Apr 2016	-	2024-03-01	120574
Ssangyong	Xlv	E-xgi 160 Allrad	SUV	Allrad	Benzin	94	128	Apr 2016	-	2024-03-01	120575
Ssangyong	Xlv	E-xdi 160	SUV	Frontantrieb	Diesel	85	116	Apr 2016	-	2024-03-01	120576
Ssangyong	Xlv	E-xdi 160 Allrad	SUV	Allrad	Diesel	85	116	Apr 2016	-	2024-03-01	120577
Audi	Q7	SQ7 TDI Quattro	SUV	Allrad	Diesel	320	435	Apr 2016	-	2025-06-01	120590
Piaggio	Porter	1.3 CNG	Bus	Heckantrieb	Benzin/Erdgas (CNG)	54	73	Jul 2016	-	2024-03-01	120591
Piaggio	Porter	1.3 CNG	Kasten	Heckantrieb	Benzin/Erdgas (CNG)	54	73	Jul 2016	-	2024-03-01	120592
Piaggio	Porter	1.3 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	54	73	Jul 2016	-	2024-03-01	120594
Audi	Q3	1.4 Tfsi	SUV	Frontantrieb	Benzin	92	125	Jul 2016	Oct 2018	2024-03-01	120595
Renault	Twingo	1.0 SCE 70	Schrägheck	Heckantrieb	Benzin	51	69	Sep 2015	Apr 2019	2026-05-01	120596
Citroën	Jumper iii	2.0 Bluehdi 110	Kasten	Frontantrieb	Diesel	81	110	Nov 2015	Sep 2019	2025-12-01	120597
Citroën	Jumper iii	2.0 Bluehdi 130	Kasten	Frontantrieb	Diesel	96	130	Nov 2015	Sep 2019	2025-12-01	120598
Citroën	Jumper iii	2.0 Bluehdi 160	Kasten	Frontantrieb	Diesel	120	163	Nov 2015	Sep 2019	2025-12-01	120599
Citroën	Jumper iii	2.0 Bluehdi 110	Pritsche/Fahrgestell	Frontantrieb	Diesel	81	110	Nov 2015	Sep 2019	2025-12-01	120601
Citroën	Jumper iii	2.0 Bluehdi 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	130	Nov 2015	Sep 2019	2025-12-01	120602
Citroën	Jumper iii	2.0 Bluehdi 160	Pritsche/Fahrgestell	Frontantrieb	Diesel	120	163	Nov 2015	Sep 2019	2025-12-01	120603
Audi	A3	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	85	115	Jul 2016	Dec 2017	2024-03-01	120604
Audi	A3	1.0 Tfsi	Schrägheck	Frontantrieb	Benzin	85	115	Jul 2016	Oct 2020	2024-03-01	120605
Audi	A3	1.0 Tfsi	Stufenheck	Frontantrieb	Benzin	85	115	Jul 2016	Oct 2020	2024-03-01	120606
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	228	310	Jun 2016	Dec 2017	2024-03-01	120607
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	228	310	Jun 2016	Oct 2020	2024-03-01	120608
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	228	310	Jun 2016	Oct 2020	2024-03-01	120609
Audi	A3	S3 Quattro	Cabriolet	Allrad	Benzin	228	310	Jul 2016	Oct 2020	2024-03-01	120613
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	140	190	May 2016	Dec 2017	2024-03-01	120616
Audi	A3	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120617
Audi	A3	2.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120618
Audi	A3	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120620
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	140	190	May 2016	Dec 2017	2024-03-01	120627
Audi	A3	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120629
Audi	A3	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120632
Audi	A3	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	140	190	May 2016	Oct 2020	2024-03-01	120633
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	70	95	Jun 2016	-	2024-03-01	120653
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	85	115	Jun 2016	-	2024-03-01	120654
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	92	125	Jun 2016	-	2024-03-01	120655
Fiat	Talento	1.6 D	Bus	Frontantrieb	Diesel	107	145	Jun 2016	-	2024-03-01	120656
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	70	95	Jun 2016	-	2024-03-01	120661
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	89	121	Jun 2016	-	2024-03-01	120662
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	92	125	Jun 2016	-	2024-03-01	120663
Fiat	Talento	1.6 D	Kasten	Frontantrieb	Diesel	107	145	Jun 2016	-	2024-03-01	120664
Fiat	Talento	1.6 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	92	125	Jun 2016	-	2024-03-01	120665
Fiat	Talento	1.6 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jun 2016	-	2024-03-01	120666
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	90	122	Jun 2013	Dec 2018	2024-03-01	120670
Hyundai	I10 i	1.1	Schrägheck	Frontantrieb	Benzin	50	68	Nov 2008	Dec 2013	2024-03-01	120679
Baic	Senova x35	1.5	SUV	Frontantrieb	Benzin	85	116	May 2016	-	2024-03-01	120689
KIA	Soul ii	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	95	129	Jul 2016	Dec 2018	2024-03-01	120699
KIA	Cerato iii	1.6 Cvvt	Stufenheck	Frontantrieb	Benzin	95	129	Jul 2016	Jun 2018	2024-05-01	120708
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	397	540	May 2016	Nov 2021	2024-03-01	120716
VW	Up!	1.0 TSI	Schrägheck	Frontantrieb	Benzin	66	90	May 2016	Aug 2019	2025-02-03	120717
Peugeot	Boxer	2.0 Bluehdi 110	Kasten	Frontantrieb	Diesel	81	110	Mar 2016	Sep 2019	2025-02-03	120718
Peugeot	Boxer	2.0 Bluehdi 130	Kasten	Frontantrieb	Diesel	96	130	Mar 2016	Sep 2019	2025-02-03	120719
Peugeot	Boxer	2.0 Bluehdi 160	Kasten	Frontantrieb	Diesel	120	163	Mar 2016	Dec 2023	2025-02-03	120720
Fiat	Tipo	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	88	120	May 2016	Oct 2020	2024-03-01	120721
Mercedes-benz	E-Klasse	E 200	Kombi	Heckantrieb	Benzin	135	184	Jul 2016	Jun 2020	2024-03-01	120722
Fiat	Tipo	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	88	120	May 2016	Oct 2020	2024-03-01	120723
Mercedes-benz	E-Klasse	E 250	Kombi	Heckantrieb	Benzin	155	211	Jul 2016	Nov 2018	2024-03-01	120724
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel	143	194	Jul 2016	Oct 2023	2024-03-01	120725
Mercedes-benz	E-Klasse	E 200 4-matic	Stufenheck	Allrad	Benzin	135	184	Jul 2016	Jun 2019	2024-03-01	120726
Mercedes-benz	E-Klasse	E 250	Stufenheck	Heckantrieb	Benzin	155	211	Jul 2016	Oct 2023	2024-03-01	120727
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	180	245	Jul 2016	Jun 2020	2024-03-01	120730
Mercedes-benz	E-Klasse	E 350 E	Stufenheck	Heckantrieb	Benzin/Elektro	210	286	Jul 2016	Jun 2019	2024-03-01	120738
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	245	333	Jul 2016	May 2018	2024-03-01	120740
Mercedes-benz	E-Klasse	AMG E 43 4-matic	Stufenheck	Allrad	Benzin	295	401	Jul 2016	May 2018	2024-03-01	120741
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel	110	150	Jul 2016	Jun 2020	2024-03-01	120746
Fiat	Punto	1.3 JTD Multijet	Schrägheck	Frontantrieb	Diesel	66	90	May 2018	-	2024-03-01	120770


--- Round 1 / 首次发送 ---
## 更新点

* Toyota Proace II 的 1.6 D-4D 95 与 115/116 hp 乘用/Combi 配置均锁定为 Medium 车身；2.0 D-4D 150 hp 覆盖 Compact、Medium、Long 三种物理长度，因此仅将 `120331` 拆成三条派生映射。
* 复用已有 BMW F34 Gran Turismo、Volvo S90 II（234）和 Toyota Proace II 尺寸组；F34 与 Volvo `234` 车身代码边界已闭合。([BMW Group PressClub][1])
* 首次创建 Audi A3/S3 8V facelift 的三门、Sportback、Sedan、Cabriolet 共 8 个尺寸组。普通 A3 与 S3 因保险杠、悬架高度及最终三维不同，分别建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 已 READY 原始 Ktype：22
* 已 READY 映射行：24
* 待处理原始 Ktype：78
* 本轮新增尺寸组：8
* 本轮复用已有尺寸组：5
* 当前映射共引用尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120326	120326	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	1.6 D-4D 95中车身乘用版。	READY
120328	120328	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	1.6 D-4D 115/116中车身Combi版。	READY
120331_compact	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	2.0 D-4D 150紧凑车身分支。	READY
120331_medium	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	2.0 D-4D 150中车身分支。	READY
120331_long	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	2.0 D-4D 150长车身分支。	READY
120506	120506	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车。	READY
120517	120517	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120518	120518	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120542	120542	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120604	120604	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120605	120605	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120606	120606	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120607	120607	Hatchback	S3 8V facelift	8V	3	EU-AUDI-S3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	S3三门车身分支。	READY
120608	120608	Hatchback	S3 8V facelift	8V	5	EU-AUDI-S3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	S3 Sportback五门车身分支。	READY
120609	120609	Sedan	S3 8V facelift	8V	4	EU-AUDI-S3-8V-FACELIFT-SEDAN-01	HIGH	S3四门轿车外廓。	READY
120613	120613	Convertible	S3 8V facelift	8V	2	EU-AUDI-S3-8V-FACELIFT-CONVERTIBLE-01	HIGH	S3双门敞篷外廓。	READY
120616	120616	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120617	120617	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120618	120618	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120620	120620	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH	双门敞篷外廓。	READY
120627	120627	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120629	120629	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120632	120632	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120633	120633	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH	双门敞篷外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424	Auto-Data Audi A3 8V facelift 1.0 TFSI 3-door	https://www.auto-data.net/en/audi-a3-8v-facelift-2016-1.0-tfsi-115hp-23679
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426	Auto-Data Audi A3 Sportback 8V facelift 1.0 TFSI	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-1.0-tfsi-115hp-23727
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift 1.0 TFSI	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-1.0-tfsi-115hp-23716
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift 2.0 TFSI	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-2.0-tfsi-190hp-s-tronic-23804
EU-AUDI-S3-8V-FACELIFT-HATCHBACK-3D-01	4252	1777	1401	Auto-Data Audi S3 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8v-facelift-2016-2.0-tfsi-310hp-quattro-23820
EU-AUDI-S3-8V-FACELIFT-SPORTBACK-5D-01	4322	1785	1404	Auto-Data Audi S3 Sportback 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-sportback-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23821
EU-AUDI-S3-8V-FACELIFT-SEDAN-01	4466	1796	1392	Auto-Data Audi S3 Sedan 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-sedan-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23712
EU-AUDI-S3-8V-FACELIFT-CONVERTIBLE-01	4431	1793	1388	Auto-Data Audi S3 Cabriolet 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-cabriolet-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23713
```

## 下一步优先处理

1. 按共平台聚类闭合 Citroën Jumper III 与 Peugeot Boxer 的不同长度、车顶及 Kasten/底盘分支。
2. 批量处理 Fiat Talento 的 Bus、Kasten、底盘和长短轴组合。
3. 处理 Piaggio Porter、Fiat Doblo 等存在 Bus、Van、Pickup/底盘差异的商用车型。
4. 随后闭合普通乘用车共享组，优先 Hyundai Ioniq、Mercedes-Benz E-Class W213/S213、Tesla Model S/X。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0260340EN/the-new-bmw-3-series-gran-turismo?utm_source=chatgpt.com "The new BMW 3 Series Gran Turismo."
[2]: https://www.auto-data.net/en/audi-a3-8v-facelift-2016-1.0-tfsi-115hp-23679 "Audi A3 (8V, facelift 2016) 1.0 TFSI (115 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz E-Class `W213` 四门轿车与 `S213` 五门旅行车两个尺寸组，共关联 10 个 Ktype。([汽车数据网][1])
* 闭合 Hyundai Ioniq Hybrid/Electric、Tesla Model S facelift 与 Model X，共关联 5 个 Ktype。([汽车数据网][2])
* 闭合 Audi A4 B9 Avant、SsangYong XLV、Borgward BX7，以及 Volvo S60/V60 Polestar，共关联 10 个 Ktype。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：47
* READY 映射行：49
* PENDING 原始 Ktype：53
* 已确认并引用尺寸组：23
* 本轮新增尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120372	120372	Hatchback	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	Model X五门车身。	READY
120519	120519	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-HATCHBACK-01	HIGH	AE五门掀背外廓。	READY
120520	120520	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-HATCHBACK-01	HIGH	AE五门掀背外廓。	READY
120524	120524	Wagon	V60 I facelift	155	5	EU-VOLVO-V60-I-FACELIFT-POLESTAR-WAGON-01	HIGH	Polestar旅行车外廓。	READY
120525	120525	Sedan	S60 II facelift	134	4	EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	HIGH	Polestar四门轿车外廓。	READY
120531	120531	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH	2016 facelift五门掀背外廓。	READY
120532	120532	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH	2016 facelift五门掀背外廓。	READY
120545	120545	SUV	BX7 I		5	EU-BORGWARD-BX7-I-SUV-01	HIGH	BX7五门SUV外廓。	READY
120549	120549	SUV	BX7 I		5	EU-BORGWARD-BX7-I-SUV-01	HIGH	BX7五门SUV外廓。	READY
120565	120565	Wagon	A4 B9	8W	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	8W Avant五门旅行车。	READY
120567	120567	Wagon	A4 B9	8W	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	8W Avant五门旅行车。	READY
120574	120574	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120575	120575	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120576	120576	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120577	120577	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120722	120722	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120724	120724	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120725	120725	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120726	120726	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120727	120727	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120730	120730	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120738	120738	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120740	120740	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120741	120741	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120746	120746	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684	Auto-Data Tesla Model X 75D	https://www.auto-data.net/en/tesla-model-x-75d-75-kwh-333hp-dual-motor-awd-33034
EU-HYUNDAI-IONIQ-I-HATCHBACK-01	4470	1820	1450	Auto-Data Hyundai IONIQ 2016 generation	https://www.auto-data.net/en/hyundai-ioniq-model-2230
EU-VOLVO-V60-I-FACELIFT-POLESTAR-WAGON-01	4668	1866	1484	Auto-Data Volvo V60 I facelift Polestar	https://www.auto-data.net/en/volvo-v60-i-facelift-2013-polestar-2.0-t6-367hp-awd-geartronic-23138
EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	4635	1865	1484	Auto-Data Volvo S60 II facelift Polestar	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-polestar-2.0-t6-367hp-awd-geartronic-23267
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445	Auto-Data Tesla Model S facelift 75D	https://www.auto-data.net/en/tesla-model-s-facelift-2016-75d-75-kwh-328hp-dual-motor-awd-32864
EU-BORGWARD-BX7-I-SUV-01	4715	1911	1690	Auto-Data Borgward BX7 generation	https://www.auto-data.net/en/borgward-bx7-generation-5860
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Auto-Data Audi A4 Avant B9 2.0 TFSI ultra	https://www.auto-data.net/en/audi-a4-avant-b9-8w-2.0-tfsi-ultra-190hp-s-tronic-22405
EU-SSANGYONG-XLV-I-SUV-01	4440	1798	1605	Auto-Data SsangYong XLV 1.6 AWD	https://www.auto-data.net/en/ssangyong-xlv-1.6-115hp-awd-automatic-29815
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class S213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200-184hp-9g-tronic-25816
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-9g-tronic-22620
```

## 下一步优先处理

1. 批量闭合 Nissan Qashqai II、Opel Mokka/Corsa E、Audi Q7/Q3、Volvo XC90 II 等 SUV 与紧凑型乘用车。
2. 处理 Ford Ka+、Renault Twingo、VW Up、Hyundai i10、Kia Soul/Cerato、Toyota Corolla。
3. 随后处理 Fiat Talento、Citroën Jumper、Peugeot Boxer、Piaggio Porter 等多轴距、多车顶商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-9g-tronic-22620 "Mercedes-Benz E-class (W213) E 200 (184 Hp) 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/hyundai-ioniq-1.6-gdi-141hp-hybrid-dct-30706 "Hyundai IONIQ 1.6 GDI (141 Hp) Hybrid DCT | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/audi-a4-avant-b9-8w-2.0-tfsi-ultra-190hp-s-tronic-22405 "Audi A4 Avant (B9 8W) 2.0 TFSI ultra (190 Hp) S tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Opel Mokka X 与 Corsa E。Corsa E LPG 同时覆盖三门、五门两种不同外廓，因此将 `120359` 拆为两个派生映射。([汽车数据网][1])
* Ford Ka+ 两个 Ktype 的生产区间跨越 2018 年改款，分别拆分为改款前与改款后外廓；同时闭合 Renault Twingo III、Volkswagen Up! facelift、Audi Q3 8U facelift 与 SQ7 4M。([汽车数据网][2])
* 闭合 BMW X5 E70 LCI、Volvo XC90 II 与 Maserati Levante M161；BMW 输入版本名称与 306 hp 汽油目录命名存在差异，但物理车身边界可确定为 E70 LCI。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：58
* READY 映射行：63
* PENDING 原始 Ktype：42
* 已确认并引用尺寸组：35
* 本轮新增尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120340	120340	SUV	Mokka X		5	EU-OPEL-MOKKA-X-SUV-01	HIGH	Mokka X五门SUV外廓。	READY
120359_3dr	120359	Hatchback	Corsa E		3	EU-OPEL-CORSA-E-HATCHBACK-3D-01	HIGH	三门LPG车身分支。	READY
120359_5dr	120359	Hatchback	Corsa E		5	EU-OPEL-CORSA-E-HATCHBACK-5D-01	HIGH	五门LPG车身分支。	READY
120501	120501	SUV	X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	MEDIUM	输入版本名称存在差异；物理边界为E70 LCI五门SUV。	READY
120503_prefl	120503	Hatchback	Ka+ III pre-facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	2016至2018改款前外廓。	READY
120503_facelift	120503	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	2018至2020改款后外廓。	READY
120504_prefl	120504	Hatchback	Ka+ III pre-facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	2016至2018改款前外廓。	READY
120504_facelift	120504	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	2018至2020改款后外廓。	READY
120522	120522	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90 II五门SUV外廓。	READY
120566	120566	SUV	Levante I	M161	5	EU-MASERATI-LEVANTE-I-SUV-01	HIGH	M161五门SUV外廓。	READY
120590	120590	SUV	SQ7 4M	4M	5	EU-AUDI-SQ7-4M-SUV-01	HIGH	SQ7 4M改款前外廓。	READY
120595	120595	SUV	Q3 I facelift	8U	5	EU-AUDI-Q3-8U-FACELIFT-SUV-01	HIGH	8U改款后五门SUV。	READY
120596	120596	Hatchback	Twingo III		5	EU-RENAULT-TWINGO-III-HATCHBACK-01	HIGH	Twingo III五门车身。	READY
120717	120717	Hatchback	Up! I facelift		5	EU-VW-UP-I-FACELIFT-HATCHBACK-01	HIGH	2016 facelift五门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOKKA-X-SUV-01	4275	1781	1658	Auto-Data Opel Mokka X generation	https://www.auto-data.net/en/opel-mokka-x-generation-4949
EU-OPEL-CORSA-E-HATCHBACK-3D-01	4021	1736	1479	Auto-Data Opel Corsa E 3-door 1.4 ECOTEC LPG	https://www.auto-data.net/en/opel-corsa-e-3-door-1.4-ecotec-90hp-lpg-22254
EU-OPEL-CORSA-E-HATCHBACK-5D-01	4021	1746	1481	Auto-Data Opel Corsa E 5-door 1.4 ECOTEC LPG	https://www.auto-data.net/en/opel-corsa-e-5-door-1.4-ecotec-90hp-lpg-22247
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776	Auto-Data BMW X5 E70 LCI 35i xDrive	https://www.auto-data.net/en/bmw-x5-e70-lci-facelift-2010-35i-306hp-xdrive-steptronic-17307
EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	3929	1695	1524	Auto-Data Ford KA+ 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-1.2-ti-vct-85hp-25181
EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	3941	1704	1524	Auto-Data Ford KA+ facelift 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-facelift-2018-1.2-ti-vct-85hp-32686
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Auto-Data Volvo XC90 II generation	https://www.auto-data.net/en/volvo-xc90-ii-generation-4274
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679	Auto-Data Maserati Levante 3.0 V6 diesel AWD	https://www.auto-data.net/en/maserati-levante-3.0-v6-275hp-awd-automatic-22815
EU-AUDI-SQ7-4M-SUV-01	5069	1968	1741	Auto-Data Audi SQ7 4M 4.0 TDI	https://www.auto-data.net/en/audi-sq7-typ-4m-4.0-tdi-v8-435hp-quattro-tiptronic-23120
EU-AUDI-Q3-8U-FACELIFT-SUV-01	4388	1831	1608	Auto-Data Audi Q3 8U facelift 1.4 TFSI	https://www.auto-data.net/en/audi-q3-i-8u-facelift-2014-1.4-tfsi-125hp-27043
EU-RENAULT-TWINGO-III-HATCHBACK-01	3595	1647	1557	Auto-Data Renault Twingo III 1.0 SCe	https://www.auto-data.net/en/renault-twingo-iii-1.0-sce-70hp-start-stop-20298
EU-VW-UP-I-FACELIFT-HATCHBACK-01	3600	1641	1504	Auto-Data Volkswagen Up facelift 1.0 TSI	https://www.auto-data.net/en/volkswagen-up-facelift-2016-1.0-tsi-90hp-24558
```

## 下一步优先处理

1. 闭合 Toyota Corolla、Hyundai i10、Kia Soul/Cerato、Fiat Tipo Hatchback/Wagon 等单一乘用车外廓。
2. 处理 Chevrolet Camaro、McLaren 570GT/675LT Spider、Audi R8 Spyder 等跑车和敞篷车。
3. 随后集中拆分 Fiat Talento、Citroën Jumper、Peugeot Boxer、Piaggio Porter 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-mokka-x-generation-4949?utm_source=chatgpt.com "Opel Mokka X | Technical Specs, Fuel consumption, ..."
[2]: https://www.auto-data.net/en/ford-ka-1.2-ti-vct-85hp-25181?utm_source=chatgpt.com "Specs of Ford KA+ 1.2 Ti-VCT (85 Hp) /2016, 2017, 2018"
[3]: https://www.auto-data.net/en/bmw-x5-e70-lci-facelift-2010-35i-306hp-xdrive-steptronic-17307?utm_source=chatgpt.com "BMW X5 (E70 LCI, facelift 2010) 35i (306 Hp) xDrive Steptronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 BMW 4 Series F32 Coupe 与 Audi R8 II 4S Spyder 两个尺寸组。([汽车数据网][1])
* 闭合 Toyota Corolla XI E170、Kia Soul II facelift、Kia Cerato III facelift；Corolla 改款前后尺寸相同，继续共用一个尺寸组。([汽车数据网][2])
* Hyundai i10 I 的生产期跨越 2011 facelift，且车长由 3565 mm 变为 3585 mm，因此将 `120679` 拆为改款前、改款后两个物理分支。([汽车数据网][3])
* 闭合 Fiat Tipo 357 Hatchback、358 Wagon 与 Fiat Punto 199；Punto 尺寸采用 Fiat 官方技术资料。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：67
* READY 映射行：73
* PENDING 原始 Ktype：33
* 已确认并引用尺寸组：45
* 本轮新增尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120539	120539	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH	F32双门Coupe外廓。	READY
120670	120670	Sedan	Corolla XI E170	E170	4	EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	HIGH	E170改款前后共用同一三维。	READY
120679_prefl	120679	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-PREFL-01	HIGH	2008至2010改款前外廓。	READY
120679_facelift	120679	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-FACELIFT-01	HIGH	2011至2013改款后外廓。	READY
120699	120699	Hatchback	Soul II facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH	PS改款后五门车身。	READY
120708	120708	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH	YD改款后四门轿车。	READY
120716	120716	Convertible	R8 II Spyder	4S	2	EU-AUDI-R8-II-4S-SPYDER-01	HIGH	4S双门Spyder外廓。	READY
120721	120721	Hatchback	Tipo 357	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	357五门掀背外廓。	READY
120723	120723	Wagon	Tipo 358	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH	358五门旅行车外廓。	READY
120770	120770	Hatchback	Punto 199 facelift	199	5	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	199五门改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-F32-COUPE-01	4638	1825	1377	Auto-Data BMW 4 Series Coupe F32 425d	https://www.auto-data.net/en/bmw-4-series-coupe-f32-425d-224hp-22684
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465	Auto-Data Toyota Corolla XI E170; Auto-Data Toyota Corolla XI E170 facelift	https://www.auto-data.net/en/toyota-corolla-xi-e170-1.6-valvematic-132hp-18480;https://www.auto-data.net/en/toyota-corolla-xi-e170-facelift-2016-generation-5005
EU-HYUNDAI-I10-I-HATCHBACK-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.1	https://www.auto-data.net/en/hyundai-i10-i-1.1-67hp-13878
EU-HYUNDAI-I10-I-HATCHBACK-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I facelift 1.1	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-1.1-69hp-31036
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618	Auto-Data Kia Soul II facelift 1.6 GDI	https://www.auto-data.net/en/kia-soul-ii-facelift-2016-1.6-gdi-132hp-32196
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435	Auto-Data Kia Cerato III Sedan facelift	https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046
EU-AUDI-R8-II-4S-SPYDER-01	4426	1940	1244	Auto-Data Audi R8 II Spyder 4S 5.2 FSI	https://www.auto-data.net/en/audi-r8-ii-spyder-4s-5.2-fsi-v10-540hp-quattro-s-tronic-23069
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Auto-Data Fiat Tipo 357 Hatchback LPG	https://www.auto-data.net/en/fiat-tipo-357-hatchback-1.4-120hp-lpg-23537
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514	Auto-Data Fiat Tipo 358 Wagon LPG	https://www.auto-data.net/en/fiat-tipo-358-wagon-1.4-120hp-lpg-23578
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490	Fiat Punto official technical specification 2017	https://www.media.stellantis.com/uploads/fr/FR/2018/FIAT/INFORMATIONS_TECHNIQUES/Fiche_technique_Fiat_Punto_-_11_janvier_2018.pdf
```

## 下一步优先处理

1. 闭合 Subaru Legacy V Wagon、Volvo S80 II、BAIC Senova X35、Nissan Qashqai II 等剩余单一乘用车或 SUV 外廓。
2. 处理 Chevrolet Camaro Coupe/Convertible、McLaren 570GT、675LT Spider 与 Hummer H2 SUT。
3. 最后集中拆分 Fiat Doblo、Piaggio Porter、Fiat Talento、Citroën Jumper 和 Peugeot Boxer 的轴距、车顶及车身形式分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-4-series-coupe-f32-425d-224hp-22684 "BMW 4 Series Coupe (F32) 425d (224 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/toyota-corolla-model-407?utm_source=chatgpt.com "Toyota Corolla | Technical Specs, Fuel consumption ..."
[3]: https://www.auto-data.net/en/hyundai-i10-i-1.1-67hp-13878 "Hyundai i10 I 1.1 (67 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/fiat-tipo-357-hatchback-1.4-120hp-lpg-23537 "Fiat Tipo (357) Hatchback 1.4 (120 Hp) LPG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Subaru Legacy V facelift 旅行车；Nissan Qashqai II 的生产区间覆盖 2017 年改款，车长发生变化，因此将 `120309` 拆为改款前、改款后两个物理分支。([汽车数据网][1])
* 闭合 McLaren 570GT、675LT Spider，以及第六代 Chevrolet Camaro Coupe、Convertible 四个跑车尺寸组。McLaren 宽度采用明确不含后视镜的规格。([汽车目录][2])
* 闭合 Hummer H2 SUT、Volvo S80 II facelift 和第一代 BAIC Senova X35。Volvo S80 使用官方车身宽度 `1861 mm`，未采用包含折叠后视镜的 `1907 mm`。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：76
* READY 映射行：83
* PENDING 原始 Ktype：24
* 已确认并引用尺寸组：55
* 本轮新增尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120299	120299	Wagon	Legacy V facelift	BR	5	EU-SUBARU-LEGACY-V-FACELIFT-WAGON-01	HIGH	BR五门旅行车外廓。	READY
120309_prefl	120309	SUV	Qashqai II J11 pre-facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-PREFL-01	HIGH	生产区间覆盖2017年改款前外廓。	READY
120309_facelift	120309	SUV	Qashqai II J11 facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	生产区间覆盖2017年改款后外廓。	READY
120389	120389	Coupe	570GT		2	EU-MCLAREN-570GT-COUPE-01	HIGH	双门GT车身外廓。	READY
120391	120391	Convertible	675LT Spider		2	EU-MCLAREN-675LT-SPIDER-CONVERTIBLE-01	HIGH	双门Spider外廓。	READY
120496	120496	Coupe	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	第六代双门Coupe外廓。	READY
120497	120497	Convertible	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	第六代双门敞篷外廓。	READY
120505	120505	Pickup	H2 SUT	GMT913	4	EU-HUMMER-H2-SUT-PICKUP-01	HIGH	GMT913四门SUT外廓。	READY
120516	120516	Sedan	S80 II facelift	124	4	EU-VOLVO-S80-II-FACELIFT-SEDAN-01	HIGH	124四门轿车外廓。	READY
120689	120689	SUV	Senova X35 I		5	EU-BAIC-SENOVA-X35-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-LEGACY-V-FACELIFT-WAGON-01	4790	1780	1535	Auto-Data Subaru Legacy V Station Wagon facelift 2012	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-2.0i-150hp-awd-lineartronic-22373
EU-NISSAN-QASHQAI-II-J11-SUV-PREFL-01	4377	1806	1590	Auto-Data Nissan Qashqai II J11	https://www.auto-data.net/en/nissan-qashqai-ii-j11-1.2-dig-t-115hp-cvt-19826
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Auto-Data Nissan Qashqai II J11 facelift	https://www.auto-data.net/en/nissan-qashqai-ii-j11-facelift-2017-1.6-dig-t-163hp-30836
EU-MCLAREN-570GT-COUPE-01	4530	1914	1201	Automobile-Catalog McLaren 570GT	https://www.automobile-catalog.com/car/2016/2327570/mclaren_570gt.html
EU-MCLAREN-675LT-SPIDER-CONVERTIBLE-01	4546	1908	1192	Automobile-Catalog McLaren 675LT Spider	https://www.automobile-catalog.com/car/2017/2261105/mclaren_675lt_spider.html
EU-CHEVROLET-CAMARO-VI-COUPE-01	4784	1880	1340	Auto-Data Chevrolet Camaro VI 6.2 V8	https://www.auto-data.net/en/chevrolet-camaro-vi-6.2-v8-453hp-automatic-24759
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4784	1897	1344	Auto-Data Chevrolet Camaro VI Convertible 6.2 V8	https://www.auto-data.net/en/chevrolet-camaro-vi-convertible-6.2-v8-453hp-automatic-25212
EU-HUMMER-H2-SUT-PICKUP-01	5170	2063	2012	Auto-Data Hummer H2 SUT 6.2 V8	https://www.auto-data.net/en/hummer-h2-sut-6.2i-v8-398hp-4x4-automatic-16668
EU-VOLVO-S80-II-FACELIFT-SEDAN-01	4854	1861	1493	Volvo S80 official dimensions	https://www.volvocars.com/mt/support/car/s80/2014/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/a40dd0d5c4ed9343c0a801e8008db8aa/
EU-BAIC-SENOVA-X35-I-SUV-01	4300	1815	1640	CarNewsChina Senova X35 launch dimensions; AutoScout24 BAIC Senova X35 technical data	https://carnewschina.com/2016/04/22/this-is-the-new-beijing-auto-senova-x35-for-china/;https://www.autoscout24.de/auto/technische-daten/baic/senova-x35/
```

## 下一步优先处理

1. 集中拆分 Fiat Talento 的 Bus、Van、底盘及 SWB/LWB 物理分支。
2. 按共平台批量闭合 Citroën Jumper III 与 Peugeot Boxer 的长度、车顶和 Kasten/底盘分支。
3. 最后处理 Fiat Doblo 底盘与 Piaggio Porter Bus、Van、Pickup/底盘分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-2.0i-150hp-awd-lineartronic-22373 "Subaru Legacy V Station Wagon (facelift 2012) 2.0i (150 Hp) AWD Lineartronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2016/2327570/mclaren_570gt.html?utm_source=chatgpt.com "2016 McLaren 570GT Specs Review (419 kW / 570 PS / 562 hp) (since late-year 2016 for Europe North America Asia worldwide)"
[3]: https://www.auto-data.net/en/hummer-h2-sut-6.2i-v8-398hp-4x4-automatic-16668 "Hummer H2 SUT 6.2i V8 (398 Hp) 4x4 Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Fiat Doblò II `263` Work Up 货斗外廓，关联 `120297`、`120298`。Ktype 目录均指向 `263` Platform/Chassis，其中 `120297` 另有 Work-Up 车型限定；尺寸采用 Fiat 官方 Work Up 数据。([Autodoc][1])
* 闭合 Piaggio Porter S85 的玻璃客车/封闭厢式车共用车身，并将 `120594` 拆分为标准货斗和裸底盘两个物理分支。([汽车目录档案][2])
* 闭合 Fiat Talento `296` 的 Combi、Van 和 Platform Cab 分支；95 hp Combi 仅映射 SWB，125/145 hp Combi覆盖 SWB/LWB，125/145 hp Van 进一步拆分低顶与高顶。([Stellantis Media][3])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：91
* READY 映射行：110
* PENDING 原始 Ktype：9
* 已确认并引用尺寸组：66
* 本轮新增尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120297	120297	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	MEDIUM	263 Work Up平台货斗外廓。	READY
120298	120298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	MEDIUM	263 Work Up平台货斗外廓。	READY
120591	120591	MPV	Porter S85 Euro 6	S85	5	EU-PIAGGIO-PORTER-S85-VAN-BODY-01	HIGH	玻璃客运车身外廓。	READY
120592	120592	Van	Porter S85 Euro 6	S85	5	EU-PIAGGIO-PORTER-S85-VAN-BODY-01	HIGH	封闭式厢式车身外廓。	READY
120594_pickup	120594	Pickup	Porter S85 Euro 6	S85	2	EU-PIAGGIO-PORTER-S85-PICKUP-01	HIGH	标准货斗分支。	READY
120594_chassis	120594	Pickup	Porter S85 Euro 6	S85	2	EU-PIAGGIO-PORTER-S85-CHASSIS-01	HIGH	裸底盘分支。	READY
120653	120653	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi外廓。	READY
120654_swb	120654	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	L1H1短轴低顶分支。	READY
120654_lwb	120654	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	L2H1长轴低顶分支。	READY
120655_swb	120655	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi分支。	READY
120655_lwb	120655	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-LWB-01	HIGH	L2H1长轴Combi分支。	READY
120656_swb	120656	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi分支。	READY
120656_lwb	120656	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-LWB-01	HIGH	L2H1长轴Combi分支。	READY
120661_swb	120661	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120661_lwb	120661	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120662_swb	120662	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120662_lwb	120662	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120663_swb_lowroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120663_swb_highroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶分支。	READY
120663_lwb_lowroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120663_lwb_highroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	HIGH	L2H2长轴高顶分支。	READY
120664_swb_lowroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120664_swb_highroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶分支。	READY
120664_lwb_lowroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120664_lwb_highroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	HIGH	L2H2长轴高顶分支。	READY
120665	120665	Pickup	Talento 296	296	2	EU-FIAT-TALENTO-296-CHASSIS-LWB-01	HIGH	L2H1长轴Platform Cab外廓。	READY
120666	120666	Pickup	Talento 296	296	2	EU-FIAT-TALENTO-296-CHASSIS-LWB-01	HIGH	L2H1长轴Platform Cab外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	4981	1872	2049	Fiat Professional Range price list; Fiat Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-PIAGGIO-PORTER-S85-VAN-BODY-01	3400	1395	1870	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-PIAGGIO-PORTER-S85-PICKUP-01	3420	1395	1705	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-PIAGGIO-PORTER-S85-CHASSIS-01	3555	1395	1705	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-FIAT-TALENTO-296-MPV-SWB-01	4999	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-MPV-LWB-01	5399	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-CHASSIS-LWB-01	5248	1956	1953	Fiat Talento official technical sheet; Fiat Professional Range price list	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf;https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
```

## 下一步优先处理

1. 按共平台一次性闭合 Citroën Jumper III 与 Peugeot Boxer 的 Kasten 长度、车顶组合。
2. 闭合 Citroën Jumper III 的 Pritsche/Fahrgestell 轴距及底盘分支。
3. 完成剩余 9 个 Ktype 后立即进行一次机械收尾并输出两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/turbocharger-10972/fiat/doblo/doblo-platform-chassis-263/120297-1-4?utm_source=chatgpt.com "FIAT Doblo II Platform/Chassis (263) 1.4 Turbo - 120 hp Petrol 88 ..."
[2]: https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf?utm_source=chatgpt.com "New Porter Range"
[3]: https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf?utm_source=chatgpt.com "FIAT PROFESSIONAL RANGE"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合最后 9 个商用车 Ktype：Citroën Jumper III 的 Kasten、单排/双排底盘，以及 Peugeot Boxer II 的全部适用 L/H 厢式车分支。
* Jumper 的发动机适配矩阵、车长、车高及不含后视镜宽度均按 2016 技术资料闭合；其中 BlueHDi 160 的 L4H3 35 Heavy 与 40 Heavy 高度不同，分别建组。([Attardi Group][1])
* Jumper 单排底盘按 L1/L2/L2S/L3/L4 拆分，双排底盘按不同实际外廓拆分；Boxer 按官方车型资料中的八种厢式车外廓闭合。([Attardi Group][1])

## 当前批次进度

* 输入 Ktype：100
* READY 原始 Ktype：100
* READY 映射行：171
* PENDING：0
* DIMENSION_GROUP：90
* `id` 与 `DIMENSION_GROUP_ID` 均唯一。
* 所有映射引用闭合，尺寸组无孤立记录。
* 长宽高、来源和 URL 均非空。
* 机械收尾检查通过。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120297	120297	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	MEDIUM	263 Work Up平台货斗外廓。	READY
120298	120298	Pickup	Doblò II	263	2	EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	MEDIUM	263 Work Up平台货斗外廓。	READY
120299	120299	Wagon	Legacy V facelift	BR	5	EU-SUBARU-LEGACY-V-FACELIFT-WAGON-01	HIGH	BR五门旅行车外廓。	READY
120309_prefl	120309	SUV	Qashqai II J11 pre-facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-PREFL-01	HIGH	生产区间覆盖2017年改款前外廓。	READY
120309_facelift	120309	SUV	Qashqai II J11 facelift	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	生产区间覆盖2017年改款后外廓。	READY
120326	120326	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	1.6 D-4D 95中车身乘用版。	READY
120328	120328	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	1.6 D-4D 115/116中车身Combi版。	READY
120331_compact	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	2.0 D-4D 150紧凑车身分支。	READY
120331_medium	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	2.0 D-4D 150中车身分支。	READY
120331_long	120331	MPV	Proace II	MPY	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	2.0 D-4D 150长车身分支。	READY
120340	120340	SUV	Mokka X		5	EU-OPEL-MOKKA-X-SUV-01	HIGH	Mokka X五门SUV外廓。	READY
120359_3dr	120359	Hatchback	Corsa E		3	EU-OPEL-CORSA-E-HATCHBACK-3D-01	HIGH	三门LPG车身分支。	READY
120359_5dr	120359	Hatchback	Corsa E		5	EU-OPEL-CORSA-E-HATCHBACK-5D-01	HIGH	五门LPG车身分支。	READY
120372	120372	Hatchback	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	Model X五门车身。	READY
120389	120389	Coupe	570GT		2	EU-MCLAREN-570GT-COUPE-01	HIGH	双门GT车身外廓。	READY
120391	120391	Convertible	675LT Spider		2	EU-MCLAREN-675LT-SPIDER-CONVERTIBLE-01	HIGH	双门Spider外廓。	READY
120496	120496	Coupe	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH	第六代双门Coupe外廓。	READY
120497	120497	Convertible	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH	第六代双门敞篷外廓。	READY
120501	120501	SUV	X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	MEDIUM	输入版本名称存在差异；物理边界为E70 LCI五门SUV。	READY
120503_prefl	120503	Hatchback	Ka+ III pre-facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	2016至2018改款前外廓。	READY
120503_facelift	120503	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	2018至2020改款后外廓。	READY
120504_prefl	120504	Hatchback	Ka+ III pre-facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	2016至2018改款前外廓。	READY
120504_facelift	120504	Hatchback	Ka+ III facelift		5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	2018至2020改款后外廓。	READY
120505	120505	Pickup	H2 SUT	GMT913	4	EU-HUMMER-H2-SUT-PICKUP-01	HIGH	GMT913四门SUT外廓。	READY
120506	120506	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II四门轿车。	READY
120516	120516	Sedan	S80 II facelift	124	4	EU-VOLVO-S80-II-FACELIFT-SEDAN-01	HIGH	124四门轿车外廓。	READY
120517	120517	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120518	120518	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120519	120519	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-HATCHBACK-01	HIGH	AE五门掀背外廓。	READY
120520	120520	Hatchback	Ioniq I	AE	5	EU-HYUNDAI-IONIQ-I-HATCHBACK-01	HIGH	AE五门掀背外廓。	READY
120522	120522	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	XC90 II五门SUV外廓。	READY
120524	120524	Wagon	V60 I facelift	155	5	EU-VOLVO-V60-I-FACELIFT-POLESTAR-WAGON-01	HIGH	Polestar旅行车外廓。	READY
120525	120525	Sedan	S60 II facelift	134	4	EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	HIGH	Polestar四门轿车外廓。	READY
120531	120531	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH	2016 facelift五门掀背外廓。	READY
120532	120532	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH	2016 facelift五门掀背外廓。	READY
120539	120539	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH	F32双门Coupe外廓。	READY
120542	120542	Hatchback	3 Series Gran Turismo F34	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 Gran Turismo五门外廓。	READY
120545	120545	SUV	BX7 I		5	EU-BORGWARD-BX7-I-SUV-01	HIGH	BX7五门SUV外廓。	READY
120549	120549	SUV	BX7 I		5	EU-BORGWARD-BX7-I-SUV-01	HIGH	BX7五门SUV外廓。	READY
120565	120565	Wagon	A4 B9	8W	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	8W Avant五门旅行车。	READY
120566	120566	SUV	Levante I	M161	5	EU-MASERATI-LEVANTE-I-SUV-01	HIGH	M161五门SUV外廓。	READY
120567	120567	Wagon	A4 B9	8W	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	8W Avant五门旅行车。	READY
120574	120574	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120575	120575	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120576	120576	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120577	120577	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	XLV五门长车身SUV。	READY
120590	120590	SUV	SQ7 4M	4M	5	EU-AUDI-SQ7-4M-SUV-01	HIGH	SQ7 4M改款前外廓。	READY
120591	120591	MPV	Porter S85 Euro 6	S85	5	EU-PIAGGIO-PORTER-S85-VAN-BODY-01	HIGH	玻璃客运车身外廓。	READY
120592	120592	Van	Porter S85 Euro 6	S85	5	EU-PIAGGIO-PORTER-S85-VAN-BODY-01	HIGH	封闭式厢式车身外廓。	READY
120594_pickup	120594	Pickup	Porter S85 Euro 6	S85	2	EU-PIAGGIO-PORTER-S85-PICKUP-01	HIGH	标准货斗分支。	READY
120594_chassis	120594	Pickup	Porter S85 Euro 6	S85	2	EU-PIAGGIO-PORTER-S85-CHASSIS-01	HIGH	裸底盘分支。	READY
120595	120595	SUV	Q3 I facelift	8U	5	EU-AUDI-Q3-8U-FACELIFT-SUV-01	HIGH	8U改款后五门SUV。	READY
120596	120596	Hatchback	Twingo III		5	EU-RENAULT-TWINGO-III-HATCHBACK-01	HIGH	Twingo III五门车身。	READY
120597_l1h1	120597	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120597_l1h2	120597	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120597_l2h1	120597	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120597_l2h2	120597	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120597_l3h2	120597	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120598_l1h1	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120598_l1h2	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120598_l2h1	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120598_l2h2	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120598_l3h2	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120598_l3h3	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H3-01	HIGH	L3H3高顶长车身。	READY
120598_l4h2	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H2-01	HIGH	L4H2中顶超长车身。	READY
120598_l4h3	120598	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H3-35-01	HIGH	L4H3 35 Heavy高顶超长车身。	READY
120599_l1h1	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120599_l1h2	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120599_l2h1	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120599_l2h2	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120599_l3h2	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120599_l3h3	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H3-01	HIGH	L3H3高顶长车身。	READY
120599_l4h2	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H2-01	HIGH	L4H2中顶超长车身。	READY
120599_l4h3	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H3-35-01	HIGH	L4H3 35 Heavy高顶超长车身。	READY
120599_l4h3_40	120599	Van	Jumper III facelift			EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H3-40-01	HIGH	L4H3 40 Heavy高顶超长车身。	READY
120601_scab_l1	120601	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L1-01	HIGH	单排驾驶室L1底盘。	READY
120601_scab_l2	120601	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2-01	HIGH	单排驾驶室L2底盘。	READY
120601_scab_l2s	120601	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2S-01	HIGH	单排驾驶室L2S底盘。	READY
120601_dcab_l3	120601	Pickup	Jumper III facelift		4	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L3-01	HIGH	双排驾驶室L3底盘。	READY
120602_scab_l1	120602	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L1-01	HIGH	单排驾驶室L1底盘。	READY
120602_scab_l2	120602	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2-01	HIGH	单排驾驶室L2底盘。	READY
120602_scab_l2s	120602	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2S-01	HIGH	单排驾驶室L2S底盘。	READY
120602_scab_l3	120602	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L3-01	HIGH	单排驾驶室L3底盘。	READY
120602_scab_l4	120602	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L4-01	HIGH	单排驾驶室L4底盘。	READY
120602_dcab_l2	120602	Pickup	Jumper III facelift		4	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L2-01	HIGH	双排驾驶室L2底盘。	READY
120602_dcab_l3	120602	Pickup	Jumper III facelift		4	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L3-01	HIGH	双排驾驶室L3/L4同外廓底盘。	READY
120603_scab_l1	120603	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L1-01	HIGH	单排驾驶室L1底盘。	READY
120603_scab_l2	120603	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2-01	HIGH	单排驾驶室L2底盘。	READY
120603_scab_l2s	120603	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2S-01	HIGH	单排驾驶室L2S底盘。	READY
120603_scab_l3	120603	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L3-01	HIGH	单排驾驶室L3底盘。	READY
120603_scab_l4	120603	Pickup	Jumper III facelift		2	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L4-01	HIGH	单排驾驶室L4底盘。	READY
120603_dcab_l2	120603	Pickup	Jumper III facelift		4	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L2-01	HIGH	双排驾驶室L2底盘。	READY
120603_dcab_l3	120603	Pickup	Jumper III facelift		4	EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L3-01	HIGH	双排驾驶室L3/L4同外廓底盘。	READY
120604	120604	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120605	120605	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120606	120606	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120607	120607	Hatchback	S3 8V facelift	8V	3	EU-AUDI-S3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	S3三门车身分支。	READY
120608	120608	Hatchback	S3 8V facelift	8V	5	EU-AUDI-S3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	S3 Sportback五门车身分支。	READY
120609	120609	Sedan	S3 8V facelift	8V	4	EU-AUDI-S3-8V-FACELIFT-SEDAN-01	HIGH	S3四门轿车外廓。	READY
120613	120613	Convertible	S3 8V facelift	8V	2	EU-AUDI-S3-8V-FACELIFT-CONVERTIBLE-01	HIGH	S3双门敞篷外廓。	READY
120616	120616	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120617	120617	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120618	120618	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120620	120620	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH	双门敞篷外廓。	READY
120627	120627	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
120629	120629	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门车身分支。	READY
120632	120632	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH	四门轿车外廓。	READY
120633	120633	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH	双门敞篷外廓。	READY
120653	120653	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi外廓。	READY
120654_swb	120654	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	MEDIUM	L1H1短轴低顶分支。	READY
120654_lwb	120654	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	MEDIUM	L2H1长轴低顶分支。	READY
120655_swb	120655	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi分支。	READY
120655_lwb	120655	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-LWB-01	HIGH	L2H1长轴Combi分支。	READY
120656_swb	120656	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-SWB-01	HIGH	L1H1短轴Combi分支。	READY
120656_lwb	120656	MPV	Talento 296	296	5	EU-FIAT-TALENTO-296-MPV-LWB-01	HIGH	L2H1长轴Combi分支。	READY
120661_swb	120661	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120661_lwb	120661	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120662_swb	120662	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120662_lwb	120662	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120663_swb_lowroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120663_swb_highroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶分支。	READY
120663_lwb_lowroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120663_lwb_highroof	120663	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	HIGH	L2H2长轴高顶分支。	READY
120664_swb_lowroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴低顶分支。	READY
120664_swb_highroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶分支。	READY
120664_lwb_lowroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	HIGH	L2H1长轴低顶分支。	READY
120664_lwb_highroof	120664	Van	Talento 296	296	5	EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	HIGH	L2H2长轴高顶分支。	READY
120665	120665	Pickup	Talento 296	296	2	EU-FIAT-TALENTO-296-CHASSIS-LWB-01	HIGH	L2H1长轴Platform Cab外廓。	READY
120666	120666	Pickup	Talento 296	296	2	EU-FIAT-TALENTO-296-CHASSIS-LWB-01	HIGH	L2H1长轴Platform Cab外廓。	READY
120670	120670	Sedan	Corolla XI E170	E170	4	EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	HIGH	E170改款前后共用同一三维。	READY
120679_prefl	120679	Hatchback	i10 I pre-facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-PREFL-01	HIGH	2008至2010改款前外廓。	READY
120679_facelift	120679	Hatchback	i10 I facelift	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-FACELIFT-01	HIGH	2011至2013改款后外廓。	READY
120689	120689	SUV	Senova X35 I		5	EU-BAIC-SENOVA-X35-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
120699	120699	Hatchback	Soul II facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH	PS改款后五门车身。	READY
120708	120708	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH	YD改款后四门轿车。	READY
120716	120716	Convertible	R8 II Spyder	4S	2	EU-AUDI-R8-II-4S-SPYDER-01	HIGH	4S双门Spyder外廓。	READY
120717	120717	Hatchback	Up! I facelift		5	EU-VW-UP-I-FACELIFT-HATCHBACK-01	HIGH	2016 facelift五门车身。	READY
120718_l1h1	120718	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120718_l1h2	120718	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120718_l2h1	120718	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120718_l2h2	120718	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120718_l3h2	120718	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120719_l1h1	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120719_l1h2	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120719_l2h1	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120719_l2h2	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120719_l3h2	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120719_l3h3	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H3-01	HIGH	L3H3高顶长车身。	READY
120719_l4h2	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H2-01	HIGH	L4H2中顶超长车身。	READY
120719_l4h3	120719	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H3-01	HIGH	L4H3高顶超长车身。	READY
120720_l1h1	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H1-01	HIGH	L1H1低顶短车身。	READY
120720_l1h2	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H2-01	HIGH	L1H2高顶短车身。	READY
120720_l2h1	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H1-01	HIGH	L2H1低顶中车身。	READY
120720_l2h2	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H2-01	HIGH	L2H2中顶中车身。	READY
120720_l3h2	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H2-01	HIGH	L3H2中顶长车身。	READY
120720_l3h3	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H3-01	HIGH	L3H3高顶长车身。	READY
120720_l4h2	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H2-01	HIGH	L4H2中顶超长车身。	READY
120720_l4h3	120720	Van	Boxer II facelift			EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H3-01	HIGH	L4H3高顶超长车身。	READY
120721	120721	Hatchback	Tipo 357	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH	357五门掀背外廓。	READY
120722	120722	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120723	120723	Wagon	Tipo 358	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH	358五门旅行车外廓。	READY
120724	120724	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120725	120725	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH	S213五门旅行车。	READY
120726	120726	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120727	120727	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120730	120730	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120738	120738	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120740	120740	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120741	120741	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120746	120746	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH	W213四门轿车。	READY
120770	120770	Hatchback	Punto 199 facelift	199	5	EU-FIAT-PUNTO-199-HATCHBACK-01	HIGH	199五门改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-II-263-WORK-UP-PICKUP-01	4981	1872	2049	Fiat Professional Range price list; Fiat Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-SUBARU-LEGACY-V-FACELIFT-WAGON-01	4790	1780	1535	Auto-Data Subaru Legacy V Station Wagon facelift 2012	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-2.0i-150hp-awd-lineartronic-22373
EU-NISSAN-QASHQAI-II-J11-SUV-PREFL-01	4377	1806	1590	Auto-Data Nissan Qashqai II J11	https://www.auto-data.net/en/nissan-qashqai-ii-j11-1.2-dig-t-115hp-cvt-19826
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Auto-Data Nissan Qashqai II J11 facelift	https://www.auto-data.net/en/nissan-qashqai-ii-j11-facelift-2017-1.6-dig-t-163hp-30836
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota Proace official brochure	https://blog.le-parnass.com/catalogue_pdf/toyota_proace_builtforbusiness_2016_e.pdf
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910	Toyota Proace official brochure	https://blog.le-parnass.com/catalogue_pdf/toyota_proace_builtforbusiness_2016_e.pdf
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910	Toyota Proace official brochure	https://blog.le-parnass.com/catalogue_pdf/toyota_proace_builtforbusiness_2016_e.pdf
EU-OPEL-MOKKA-X-SUV-01	4275	1781	1658	Auto-Data Opel Mokka X generation	https://www.auto-data.net/en/opel-mokka-x-generation-4949
EU-OPEL-CORSA-E-HATCHBACK-3D-01	4021	1736	1479	Auto-Data Opel Corsa E 3-door 1.4 ECOTEC LPG	https://www.auto-data.net/en/opel-corsa-e-3-door-1.4-ecotec-90hp-lpg-22254
EU-OPEL-CORSA-E-HATCHBACK-5D-01	4021	1746	1481	Auto-Data Opel Corsa E 5-door 1.4 ECOTEC LPG	https://www.auto-data.net/en/opel-corsa-e-5-door-1.4-ecotec-90hp-lpg-22247
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684	Auto-Data Tesla Model X 75D	https://www.auto-data.net/en/tesla-model-x-75d-75-kwh-333hp-dual-motor-awd-33034
EU-MCLAREN-570GT-COUPE-01	4530	1914	1201	Automobile-Catalog McLaren 570GT	https://www.automobile-catalog.com/car/2016/2327570/mclaren_570gt.html
EU-MCLAREN-675LT-SPIDER-CONVERTIBLE-01	4546	1908	1192	Automobile-Catalog McLaren 675LT Spider	https://www.automobile-catalog.com/car/2017/2261105/mclaren_675lt_spider.html
EU-CHEVROLET-CAMARO-VI-COUPE-01	4784	1880	1340	Auto-Data Chevrolet Camaro VI 6.2 V8	https://www.auto-data.net/en/chevrolet-camaro-vi-6.2-v8-453hp-automatic-24759
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4784	1897	1344	Auto-Data Chevrolet Camaro VI Convertible 6.2 V8	https://www.auto-data.net/en/chevrolet-camaro-vi-convertible-6.2-v8-453hp-automatic-25212
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776	Auto-Data BMW X5 E70 LCI 35i xDrive	https://www.auto-data.net/en/bmw-x5-e70-lci-facelift-2010-35i-306hp-xdrive-steptronic-17307
EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	3929	1695	1524	Auto-Data Ford KA+ 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-1.2-ti-vct-85hp-25181
EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	3941	1704	1524	Auto-Data Ford KA+ facelift 1.2 Ti-VCT	https://www.auto-data.net/en/ford-ka-facelift-2018-1.2-ti-vct-85hp-32686
EU-HUMMER-H2-SUT-PICKUP-01	5170	2063	2012	Auto-Data Hummer H2 SUT 6.2 V8	https://www.auto-data.net/en/hummer-h2-sut-6.2i-v8-398hp-4x4-automatic-16668
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Support – S90 dimensions	https://www.volvocars.com/sg/support/car/s90/18w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-S80-II-FACELIFT-SEDAN-01	4854	1861	1493	Volvo S80 official dimensions	https://www.volvocars.com/mt/support/car/s80/2014/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/a40dd0d5c4ed9343c0a801e8008db8aa/
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508	BMW Group PressClub – The new BMW 3 Series Gran Turismo	https://www.press.bmwgroup.com/global/article/detail/T0260340EN/the-new-bmw-3-series-gran-turismo
EU-HYUNDAI-IONIQ-I-HATCHBACK-01	4470	1820	1450	Auto-Data Hyundai IONIQ 2016 generation	https://www.auto-data.net/en/hyundai-ioniq-model-2230
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Auto-Data Volvo XC90 II generation	https://www.auto-data.net/en/volvo-xc90-ii-generation-4274
EU-VOLVO-V60-I-FACELIFT-POLESTAR-WAGON-01	4668	1866	1484	Auto-Data Volvo V60 I facelift Polestar	https://www.auto-data.net/en/volvo-v60-i-facelift-2013-polestar-2.0-t6-367hp-awd-geartronic-23138
EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	4635	1865	1484	Auto-Data Volvo S60 II facelift Polestar	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-polestar-2.0-t6-367hp-awd-geartronic-23267
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445	Auto-Data Tesla Model S facelift 75D	https://www.auto-data.net/en/tesla-model-s-facelift-2016-75d-75-kwh-328hp-dual-motor-awd-32864
EU-BMW-4-F32-COUPE-01	4638	1825	1377	Auto-Data BMW 4 Series Coupe F32 425d	https://www.auto-data.net/en/bmw-4-series-coupe-f32-425d-224hp-22684
EU-BORGWARD-BX7-I-SUV-01	4715	1911	1690	Auto-Data Borgward BX7 generation	https://www.auto-data.net/en/borgward-bx7-generation-5860
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Auto-Data Audi A4 Avant B9 2.0 TFSI ultra	https://www.auto-data.net/en/audi-a4-avant-b9-8w-2.0-tfsi-ultra-190hp-s-tronic-22405
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679	Auto-Data Maserati Levante 3.0 V6 diesel AWD	https://www.auto-data.net/en/maserati-levante-3.0-v6-275hp-awd-automatic-22815
EU-SSANGYONG-XLV-I-SUV-01	4440	1798	1605	Auto-Data SsangYong XLV 1.6 AWD	https://www.auto-data.net/en/ssangyong-xlv-1.6-115hp-awd-automatic-29815
EU-AUDI-SQ7-4M-SUV-01	5069	1968	1741	Auto-Data Audi SQ7 4M 4.0 TDI	https://www.auto-data.net/en/audi-sq7-typ-4m-4.0-tdi-v8-435hp-quattro-tiptronic-23120
EU-PIAGGIO-PORTER-S85-VAN-BODY-01	3400	1395	1870	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-PIAGGIO-PORTER-S85-PICKUP-01	3420	1395	1705	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-PIAGGIO-PORTER-S85-CHASSIS-01	3555	1395	1705	Piaggio New Porter Range brochure	https://autocatalogarchive.com/wp-content/uploads/2023/03/Piaggio-Porter-2019-INT.pdf
EU-AUDI-Q3-8U-FACELIFT-SUV-01	4388	1831	1608	Auto-Data Audi Q3 8U facelift 1.4 TFSI	https://www.auto-data.net/en/audi-q3-i-8u-facelift-2014-1.4-tfsi-125hp-27043
EU-RENAULT-TWINGO-III-HATCHBACK-01	3595	1647	1557	Auto-Data Renault Twingo III 1.0 SCe	https://www.auto-data.net/en/renault-twingo-iii-1.0-sce-70hp-start-stop-20298
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H1-01	4963	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L1H2-01	4963	2050	2522	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H1-01	5413	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L2H2-01	5413	2050	2522	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H2-01	5998	2050	2522	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L3H3-01	5998	2050	2764	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H2-01	6363	2050	2522	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H3-35-01	6363	2050	2760	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-VAN-L4H3-40-01	6363	2050	2764	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L1-01	4908	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2-01	5358	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L2S-01	5708	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L3-01	5943	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L3-01	5943	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-SCAB-L4-01	6308	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-CITROEN-JUMPER-III-FACELIFT-CHASSIS-DCAB-L2-01	5358	2050	2254	Citroën Jumper technical characteristics, May 2016	https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424	Auto-Data Audi A3 8V facelift 1.0 TFSI 3-door	https://www.auto-data.net/en/audi-a3-8v-facelift-2016-1.0-tfsi-115hp-23679
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426	Auto-Data Audi A3 Sportback 8V facelift 1.0 TFSI	https://www.auto-data.net/en/audi-a3-sportback-8v-facelift-2016-1.0-tfsi-115hp-23727
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416	Auto-Data Audi A3 Sedan 8V facelift 1.0 TFSI	https://www.auto-data.net/en/audi-a3-sedan-8v-facelift-2016-1.0-tfsi-115hp-23716
EU-AUDI-S3-8V-FACELIFT-HATCHBACK-3D-01	4252	1777	1401	Auto-Data Audi S3 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8v-facelift-2016-2.0-tfsi-310hp-quattro-23820
EU-AUDI-S3-8V-FACELIFT-SPORTBACK-5D-01	4322	1785	1404	Auto-Data Audi S3 Sportback 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-sportback-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23821
EU-AUDI-S3-8V-FACELIFT-SEDAN-01	4466	1796	1392	Auto-Data Audi S3 Sedan 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-sedan-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23712
EU-AUDI-S3-8V-FACELIFT-CONVERTIBLE-01	4431	1793	1388	Auto-Data Audi S3 Cabriolet 8V facelift 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-cabriolet-8v-facelift-2016-2.0-tfsi-310hp-quattro-s-tronic-23713
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift 2.0 TFSI	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-2.0-tfsi-190hp-s-tronic-23804
EU-FIAT-TALENTO-296-MPV-SWB-01	4999	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-SWB-LOWROOF-01	4999	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-LWB-LOWROOF-01	5399	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-MPV-LWB-01	5399	1956	1971	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-SWB-HIGHROOF-01	4999	1956	2493	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-VAN-LWB-HIGHROOF-01	5399	1956	2490	Fiat Talento official technical sheet	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf
EU-FIAT-TALENTO-296-CHASSIS-LWB-01	5248	1956	1953	Fiat Talento official technical sheet; Fiat Professional Range price list	https://www.media.stellantis.com/uploads/em/2018/FIAT-PROFESSIONAL/Schede-Tecniche/180319_Fiat-Professional_Talento_Scheda-tecnica_EN.pdf;https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465	Auto-Data Toyota Corolla XI E170; Auto-Data Toyota Corolla XI E170 facelift	https://www.auto-data.net/en/toyota-corolla-xi-e170-1.6-valvematic-132hp-18480;https://www.auto-data.net/en/toyota-corolla-xi-e170-facelift-2016-generation-5005
EU-HYUNDAI-I10-I-HATCHBACK-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.1	https://www.auto-data.net/en/hyundai-i10-i-1.1-67hp-13878
EU-HYUNDAI-I10-I-HATCHBACK-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I facelift 1.1	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-1.1-69hp-31036
EU-BAIC-SENOVA-X35-I-SUV-01	4300	1815	1640	CarNewsChina Senova X35 launch dimensions; AutoScout24 BAIC Senova X35 technical data	https://carnewschina.com/2016/04/22/this-is-the-new-beijing-auto-senova-x35-for-china/;https://www.autoscout24.de/auto/technische-daten/baic/senova-x35/
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618	Auto-Data Kia Soul II facelift 1.6 GDI	https://www.auto-data.net/en/kia-soul-ii-facelift-2016-1.6-gdi-132hp-32196
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435	Auto-Data Kia Cerato III Sedan facelift	https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046
EU-AUDI-R8-II-4S-SPYDER-01	4426	1940	1244	Auto-Data Audi R8 II Spyder 4S 5.2 FSI	https://www.auto-data.net/en/audi-r8-ii-spyder-4s-5.2-fsi-v10-540hp-quattro-s-tronic-23069
EU-VW-UP-I-FACELIFT-HATCHBACK-01	3600	1641	1504	Auto-Data Volkswagen Up facelift 1.0 TSI	https://www.auto-data.net/en/volkswagen-up-facelift-2016-1.0-tsi-90hp-24558
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H1-01	4963	2050	2254	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H2-01	4963	2050	2522	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H1-01	5413	2050	2254	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H2-01	5413	2050	2522	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H2-01	5998	2050	2522	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H3-01	5998	2050	2760	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H2-01	6363	2050	2522	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H3-01	6363	2050	2760	Peugeot Boxer official model brochure 2017	https://www.louwman.nl/uploads/Peugeot/wk2817-peugeot-boxer-modelbrochure-11971-f835c0.272748.pdf
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Auto-Data Fiat Tipo 357 Hatchback LPG	https://www.auto-data.net/en/fiat-tipo-357-hatchback-1.4-120hp-lpg-23537
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class S213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200-184hp-9g-tronic-25816
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514	Auto-Data Fiat Tipo 358 Wagon LPG	https://www.auto-data.net/en/fiat-tipo-358-wagon-1.4-120hp-lpg-23578
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 200	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-9g-tronic-22620
EU-FIAT-PUNTO-199-HATCHBACK-01	4065	1687	1490	Fiat Punto official technical specification 2017	https://www.media.stellantis.com/uploads/fr/FR/2018/FIAT/INFORMATIONS_TECHNIQUES/Fiche_technique_Fiat_Punto_-_11_janvier_2018.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf "https://www.attardigroup.it/sites/default/files/brochures/ct_jumper.225509.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_301-400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_301-400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（310 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（155 行）

