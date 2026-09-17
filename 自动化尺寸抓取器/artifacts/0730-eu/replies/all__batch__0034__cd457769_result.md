# 任务：all 第 3301-3400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0034__cd457769


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3301-3400 行

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
all 第 3301-3400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALPINA-XD3-II-G01-SUV-PREFL-01	4718	1897	1655
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-BMW-X7-G07-SUV-01	5151	2000	1805
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-KIA-SORENTO-III-SUV-FACELIFT-01	4800	1890	1690
EU-KIA-SORENTO-III-SUV-PREFL-01	4780	1890	1690
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	4803	1930	1665
EU-MCLAREN-SENNA-P15-COUPE-01	4744	1958	1229
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
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-WP11-WAGON-FACELIFT-01	4579	1715	1450
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	4697	1882	1661
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1865
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Alpina	Xd3	Biturbo Allrad	SUV	Allrad	Diesel	245	333	Nov 2018	Oct 2020	2024-03-01	134246
Mercedes-benz	S-Klasse	AMG S 63	Cabriolet	Heckantrieb	Benzin	450	612	Dec 2018	Jul 2020	2024-03-01	134247
Alpina	D5	S Allrad	Stufenheck	Allrad	Diesel	240	326	Nov 2018	Oct 2020	2024-03-01	134249
VW	Passat alltrack b8 variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	200	272	Aug 2018	Nov 2020	2025-02-03	134251
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel	118	160	Nov 2018	Aug 2023	2024-03-01	134260
Mercedes-benz	E-Klasse	E 200 D	Kombi	Heckantrieb	Diesel	118	160	Nov 2018	Aug 2023	2024-03-01	134261
Chevrolet	Epica	2.0 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	105	144	Apr 2007	Dec 2010	2024-03-01	134262
Mercedes-benz	E-Klasse	E 400 D	Stufenheck	Heckantrieb	Diesel	250	340	Dec 2018	Jun 2020	2024-03-01	134263
Seat	Arona	1.0 TGI	SUV	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2018	-	2024-03-01	134265
Skoda	Karoq	1.5 TSI 4X4	SUV	Allrad	Benzin	110	150	Jul 2017	-	2024-03-01	134266
Mercedes-benz	Gla-Klasse	GLA 200	SUV	Frontantrieb	Benzin	110	150	Jul 2018	Dec 2019	2024-03-01	134269
VW	Touareg	3.0 TSI 4motion	SUV	Allrad	Benzin	250	340	Mar 2018	-	2024-03-01	134270
Audi	Q2	35 Tfsi	SUV	Frontantrieb	Benzin	110	150	Jul 2018	-	2024-03-01	134271
Mercedes-benz	Cla	CLA 200	Coupe	Frontantrieb	Benzin	110	150	Jul 2018	Mar 2019	2024-03-01	134272
Mercedes-benz	C-Klasse	C 180	Stufenheck	Heckantrieb	Benzin	110	150	Oct 2018	Mar 2021	2024-03-01	134273
Mercedes-benz	C-Klasse	C 180	Coupe	Heckantrieb	Benzin	110	150	Nov 2018	Aug 2020	2024-03-01	134274
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	130	177	Nov 2018	Dec 2022	2024-03-01	134276
Mercedes-benz	C-Klasse	C 300	Stufenheck	Heckantrieb	Benzin	183	249	May 2018	May 2021	2024-03-01	134277
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	183	249	Jul 2018	Jul 2020	2024-03-01	134279
Mercedes-benz	E-Klasse	E 200	Stufenheck	Heckantrieb	Benzin	145	197	Oct 2018	Oct 2023	2024-03-01	134280
Porsche	Macan	2	SUV	Allrad	Benzin	180	245	May 2018	-	2024-03-01	134281
Toyota	Alphard / vellfire	3.5	Großraumlimousine	Frontantrieb	Benzin	221	300	Oct 2018	Dec 2023	2026-03-01	134282
Seat	Ibiza v	1.0 MPI	Schrägheck	Frontantrieb	Benzin	59	80	Jul 2018	-	2024-03-01	134283
Audi	Q3	40 Tfsi Quattro	SUV	Allrad	Benzin	140	190	Jul 2018	Jun 2021	2025-06-01	134284
Skoda	Kodiaq i	1.5 TSI 4X4	SUV	Allrad	Benzin	110	150	Jul 2018	-	2024-05-01	134285
Mclaren	Senna	4	Coupe	Heckantrieb	Benzin	674	916	Jul 2018	-	2024-03-01	134286
Skoda	Kodiaq i	2.0 RS Bi-tdi 4X4	SUV	Allrad	Diesel	176	239	Nov 2018	-	2024-05-01	134287
Seat	Tarraco	1.5 TSI ACT	SUV	Frontantrieb	Benzin	110	150	Sep 2018	May 2024	2025-06-01	134288
Seat	Tarraco	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Sep 2018	May 2024	2025-06-01	134289
Seat	Tarraco	2.0 TDI 4drive	SUV	Allrad	Diesel	110	150	Sep 2018	May 2024	2025-06-01	134290
Seat	Tarraco	2.0 TDI 4drive	SUV	Allrad	Diesel	140	190	Sep 2018	May 2024	2025-06-01	134291
Seat	Tarraco	2.0 TSI 4drive	SUV	Allrad	Benzin	140	190	Sep 2018	May 2024	2025-06-01	134292
Toyota	C-Hr	1.2 4WD	SUV	Allrad	Benzin	96	131	Oct 2016	-	2024-03-01	134293
VW	T-Cross	1.0 TSI	SUV	Frontantrieb	Benzin	70	95	Dec 2018	-	2024-03-01	134294
VW	T-Cross	1.0 TSI	SUV	Frontantrieb	Benzin	85	116	Dec 2018	-	2024-03-01	134295
VW	Passat b8	2.0 TSI 4motion	Stufenheck	Allrad	Benzin	200	272	Sep 2018	Nov 2020	2025-02-03	134306
VW	Passat b8 variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	200	272	Sep 2018	Nov 2020	2025-02-03	134309
Toyota	Land cruiser prado	2.8 D-4d	Geländewagen geschlossen	Allrad	Diesel	147	200	Oct 2018	-	2024-03-01	134314
Toyota	Hilux viii	2.4 D	Pick-up	Heckantrieb	Diesel	125	170	Oct 2018	-	2024-03-01	134324
Toyota	Hilux viii	2.4 D 4WD	Pick-up	Allrad	Diesel	125	170	Oct 2018	-	2024-03-01	134325
Audi	E-Tron	55 Quattro	SUV	Allrad	Elektro	300	408	Sep 2018	Jul 2023	2026-03-01	134328
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	105	143	Jun 1996	Dec 2001	2024-03-01	134336
Land Rover	Range rover evoque	2.0 D150 Mhev 4X4	SUV	Allrad	Diesel/Elektro	110	150	Dec 2018	-	2024-03-01	134341
Land Rover	Range rover evoque	2.0 D180 Mhev 4X4	SUV	Allrad	Diesel/Elektro	132	180	Dec 2018	-	2024-03-01	134343
Land Rover	Range rover evoque	2.0 D240 Mhev 4X4	SUV	Allrad	Diesel/Elektro	177	241	Dec 2018	-	2024-03-01	134344
Land Rover	Range rover evoque	2.0 P200 Mhev 4X4	SUV	Allrad	Benzin/Elektro	147	200	Dec 2018	-	2024-03-01	134345
Land Rover	Range rover evoque	2.0 P250 Mhev 4X4	SUV	Allrad	Benzin/Elektro	183	249	Dec 2018	-	2024-03-01	134346
Land Rover	Range rover evoque	2.0 P300 Mhev 4X4	SUV	Allrad	Benzin/Elektro	221	300	Dec 2018	-	2024-03-01	134347
Mercedes-benz	C-Klasse	C 350 CDI 4-matic	Kombi	Allrad	Diesel	165	224	Aug 2007	Dec 2011	2024-03-01	134351
Land Rover	Range rover evoque	2.0 D150 4X4	SUV	Allrad	Diesel	110	150	Dec 2018	-	2024-03-01	134353
Land Rover	Range rover evoque	2.0 D180 4X4	SUV	Allrad	Diesel	132	180	Dec 2018	-	2024-03-01	134355
Land Rover	Range rover evoque	2.0 P200 4X4	SUV	Allrad	Benzin	147	200	Dec 2018	-	2024-03-01	134357
Land Rover	Range rover evoque	2.0 P250 4X4	SUV	Allrad	Benzin	184	250	Dec 2018	-	2024-03-01	134358
BMW	X7	Xdrive 30 D	SUV	Allrad	Diesel	155	211	Mar 2019	Aug 2020	2024-03-01	134361
BMW	X7	Xdrive 30 D	SUV	Allrad	Diesel	183	249	Mar 2019	-	2024-03-01	134362
Mercedes-benz	S-Klasse	S 350 CDI 4-matic	Stufenheck	Allrad	Diesel	173	235	Jun 2009	Jul 2013	2024-03-01	134364
RAM	1500 crew cab pickup	5.7	Pick-up	Heckantrieb	Benzin	295	401	Dec 2018	-	2024-03-01	134367
RAM	1500 crew cab pickup	5.7 4X4	Pick-up	Allrad	Benzin	295	401	Dec 2018	-	2024-03-01	134369
Seat	Leon	1.0 TSI	Schrägheck	Frontantrieb	Benzin	63	86	Sep 2018	Aug 2020	2024-03-01	134370
Donkervoort	D8	2.5 Gto-40	Cabriolet	Heckantrieb	Benzin	284	386	Jan 2018	-	2024-03-01	134372
Hyundai	Ix20	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Nov 2010	Jul 2019	2024-03-01	134375
Microcar	Due	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Dec 2018	-	2024-03-01	134376
Hyundai	Santa fe iv	2.4 GDI AWD	SUV	Allrad	Benzin	138	188	Jul 2018	Jul 2020	2024-03-01	134377
Hyundai	Sonata vii	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	110	150	Nov 2014	Dec 2019	2024-05-01	134379
Hyundai	I40 i cw	1.6 Crdi	Kombi	Frontantrieb	Diesel	100	136	Jul 2018	May 2019	2024-03-01	134380
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	81	110	Aug 2018	-	2024-03-01	134381
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	81	110	Aug 2018	-	2024-03-01	134382
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	100	136	Aug 2018	-	2024-03-01	134383
Mercedes-benz	B-Klasse sports tourer	B 180 D	Schrägheck	Frontantrieb	Diesel	85	116	Dec 2018	-	2024-03-01	134384
KIA	Stonic	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	71	97	Nov 2018	Dec 2025	2026-03-01	134385
KIA	Picanto iii	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	48	65	Nov 2018	-	2024-03-01	134386
Great Wall	Hover h6	1.5 LPG 4WD	SUV	Allrad	Benzin/Autogas (LPG)	105	143	Dec 2018	-	2024-03-01	134389
Seat	Leon	1.5 TGI	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Oct 2018	Aug 2020	2024-03-01	134390
Seat	Leon	1.5 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Oct 2018	Aug 2020	2024-03-01	134392
Lexus	Ux	200	SUV	Frontantrieb	Benzin	126	171	Oct 2018	-	2024-03-01	134394
Seat	Leon	1.0 TSI	Kombi	Frontantrieb	Benzin	63	86	Sep 2018	Aug 2020	2024-03-01	134395
Lexus	Ux	250h E-four	SUV	Allrad	Benzin/Elektro	131	178	Oct 2018	-	2024-03-01	134396
KIA	Ceed	1.6	Schrägheck	Frontantrieb	Benzin	94	128	Mar 2018	-	2024-03-01	134398
Lexus	Ux	250h E-four	SUV	Allrad	Benzin/Elektro	135	184	Oct 2018	-	2024-03-01	134399
Lexus	Ux	250h	SUV	Frontantrieb	Benzin/Elektro	135	184	Oct 2018	-	2024-03-01	134400
KIA	Stinger	2.0 T-gdi	Schrägheck	Heckantrieb	Benzin	145	197	Jul 2018	Dec 2023	2026-04-01	134401
KIA	Stinger	2.0 T-gdi 4WD	Schrägheck	Allrad	Benzin	145	197	Jul 2018	Dec 2023	2026-04-01	134402
KIA	Sorento iii	3.5 D-cvvt	SUV	Frontantrieb	Benzin	183	249	Dec 2018	-	2024-05-01	134405
KIA	Sorento iii	3.5 D-cvvt 4WD	SUV	Allrad	Benzin	183	249	Dec 2018	Dec 2020	2024-05-01	134406
Xpeng	G3	EV	SUV	Frontantrieb	Elektro	145	197	Dec 2020	-	2025-02-03	134433
Aston Martin	Dbs	5.2 Superleggera	Coupe	Heckantrieb	Benzin	533	725	Dec 2018	-	2024-03-01	134437
Aston Martin	Rapide	6.0 AMR	Schrägheck	Heckantrieb	Benzin	444	604	Dec 2018	-	2024-03-01	134438
Lexus	Ux	250h	SUV	Frontantrieb	Benzin/Elektro	131	178	Oct 2018	-	2024-03-01	134439
Land Rover	Range rover velar	3.0 P340 Scv6 4X4	SUV	Allrad	Benzin	250	340	Apr 2018	-	2024-03-01	134441
Audi	A4 b9	35 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	110	150	Dec 2018	-	2024-03-01	134445
Audi	A4 b9 avant	35 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	110	150	Dec 2018	-	2024-03-01	134446
Seat	Ibiza iii	1.9 TDI Joya Racer	Schrägheck	Frontantrieb	Diesel	112	152	Jul 2003	Jun 2004	2024-03-01	134447
Lexus	Ux	200	SUV	Frontantrieb	Benzin	110	150	Oct 2018	-	2024-03-01	134448
Lexus	Es	200	Stufenheck	Frontantrieb	Benzin	110	150	Oct 2018	-	2024-03-01	134453
Lexus	Es	250	Stufenheck	Frontantrieb	Benzin	147	200	Oct 2018	-	2024-03-01	134461
Lexus	Es	350	Stufenheck	Frontantrieb	Benzin	183	249	Oct 2018	-	2024-03-01	134467
Lexus	Lc	500	Coupe	Heckantrieb	Benzin	341	464	Nov 2018	-	2024-03-01	134479
Ford	Fiesta v van	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	59	80	May 2002	Sep 2005	2024-03-01	134480
Ford	Focus ii	1.6 Tdci	Kasten/Kombi	Frontantrieb	Diesel	80	109	Jul 2004	Jul 2011	2024-03-01	134482
Ford	Focus ii	2.0 Tdci	Kasten/Kombi	Frontantrieb	Diesel	100	136	Sep 2005	Jul 2011	2024-03-01	134483


--- Round 1 / 首次发送 ---
## 更新点

* 完成 100 个输入 Ktype 的物理外廓聚类，共形成 112 条映射。
* 对 Alphard/Vellfire、Hilux 驾驶室、Primera 改款、S204 改款、RAM 货斗、ix20 改款及 Focus II 改款进行了派生拆分。
* RAM Crew Cab 按驱动形式和 5 英尺 7 英寸／6 英尺 4 英寸货斗拆为四个尺寸组；Kodiaq RS、Audi e-tron、T-Cross、Prado 等采用官方技术资料核对。([Amazon Web Services, Inc.][1])
* Hilux 的 GUN125/GUN135 覆盖单排、加长及双排驾驶室，分别关联三个已闭合尺寸组。([汽车数据][2])
* 已完成固定表头、主键唯一、尺寸组引用闭合、正整数三维、来源非空及下载文件一致性检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：112
* PENDING 映射：0
* 已确认且被引用的尺寸组：77
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134246	134246	SUV	XD3 II	G01	5	EU-ALPINA-XD3-II-G01-SUV-PREFL-01	HIGH		READY
134247	134247	Convertible	S-Class VI facelift	A217	2	EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	HIGH		READY
134249	134249	Sedan	D5 S (G30)	G30	4	EU-ALPINA-D5-S-G30-SEDAN-01	HIGH		READY
134251	134251	Wagon	Passat Alltrack B8	3G5	5	EU-VW-PASSAT-ALLTRACK-B8-WAGON-PREFL-01	HIGH		READY
134260	134260	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
134261	134261	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
134262	134262	Sedan	Epica	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH		READY
134263	134263	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
134265	134265	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH		READY
134266	134266	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	HIGH		READY
134269	134269	SUV	GLA I facelift	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	HIGH		READY
134270	134270	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
134271	134271	SUV	Q2 I	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH		READY
134272	134272	Coupe	CLA I facelift	C117	4	EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	HIGH		READY
134273	134273	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
134274	134274	Coupe	C-Class IV facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
134276	134276	MPV	Alhambra II facelift	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-FACELIFT-01	HIGH		READY
134277	134277	Sedan	C-Class IV facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
134279	134279	Sedan	S-Class VI facelift	W222	4	EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	HIGH		READY
134280	134280	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
134281	134281	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	HIGH		READY
134282_alphard	134282	MPV	Alphard III facelift	GGH30W	5	EU-TOYOTA-ALPHARD-AH30-MPV-FACELIFT-01	MEDIUM	同一Ktype按Alphard与Vellfire不同前脸长度拆分。	READY
134282_vellfire	134282	MPV	Vellfire II facelift	GGH30W	5	EU-TOYOTA-VELLFIRE-AH30-MPV-FACELIFT-01	MEDIUM	同一Ktype按Alphard与Vellfire不同前脸长度拆分。	READY
134283	134283	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
134284	134284	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
134285	134285	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH		READY
134286	134286	Coupe	Senna	P15	2	EU-MCLAREN-SENNA-P15-COUPE-01	HIGH		READY
134287	134287	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-RS-SUV-PREFL-01	HIGH		READY
134288	134288	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH		READY
134289	134289	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH		READY
134290	134290	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH		READY
134291	134291	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH		READY
134292	134292	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH		READY
134293	134293	SUV	C-HR I	NGX50	5	EU-TOYOTA-C-HR-I-AX10-SUV-01	HIGH		READY
134294	134294	SUV	T-Cross I	C11	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
134295	134295	SUV	T-Cross I	C11	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
134306	134306	Sedan	Passat B8	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH		READY
134309	134309	Wagon	Passat B8	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	HIGH		READY
134314	134314	SUV	Land Cruiser Prado J150 facelift	GDJ150	5	EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	HIGH		READY
134324_singlecab	134324	Pickup	Hilux VIII facelift	GUN135	2	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-SINGLECAB-01	MEDIUM	GUN135覆盖单排驾驶室外廓。	READY
134324_extracab	134324	Pickup	Hilux VIII facelift	GUN135	2	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-EXTRACAB-01	MEDIUM	GUN135覆盖加长驾驶室外廓。	READY
134324_doublecab	134324	Pickup	Hilux VIII facelift	GUN135	4	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-01	MEDIUM	GUN135覆盖双排驾驶室外廓。	READY
134325_singlecab	134325	Pickup	Hilux VIII facelift	GUN125	2	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-SINGLECAB-01	MEDIUM	GUN125覆盖单排驾驶室外廓。	READY
134325_extracab	134325	Pickup	Hilux VIII facelift	GUN125	2	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-EXTRACAB-01	MEDIUM	GUN125覆盖加长驾驶室外廓。	READY
134325_doublecab	134325	Pickup	Hilux VIII facelift	GUN125	4	EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-01	MEDIUM	GUN125覆盖双排驾驶室外廓。	READY
134328	134328	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH		READY
134336_prefl	134336	Sedan	Primera P11	P11	4	EU-NISSAN-PRIMERA-P11-SEDAN-PREFL-01	HIGH	生产区间跨越P11改款，按改款前外廓拆分。	READY
134336_facelift	134336	Sedan	Primera P11-144	P11-144	4	EU-NISSAN-PRIMERA-P11-144-SEDAN-FACELIFT-01	HIGH	生产区间跨越P11改款，按改款后外廓拆分。	READY
134341	134341	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134343	134343	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134344	134344	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134345	134345	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134346	134346	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134347	134347	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134351_prefl	134351	Wagon	C-Class III	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	生产区间跨越S204改款，按改款前外廓拆分。	READY
134351_facelift	134351	Wagon	C-Class III facelift	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	生产区间跨越S204改款，按改款后外廓拆分。	READY
134353	134353	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134355	134355	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134357	134357	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134358	134358	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
134361	134361	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
134362	134362	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
134364	134364	Sedan	S-Class V facelift	W221	4	EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	HIGH		READY
134367_shortbed	134367	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-V-DT-CREWCAB-4X2-SHORTBED-01	HIGH	Crew Cab按5英尺7英寸货斗拆分。	READY
134367_longbed	134367	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-V-DT-CREWCAB-4X2-LONGBED-01	HIGH	Crew Cab按6英尺4英寸货斗拆分。	READY
134369_shortbed	134369	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-V-DT-CREWCAB-4X4-SHORTBED-01	HIGH	Crew Cab按5英尺7英寸货斗拆分。	READY
134369_longbed	134369	Pickup	Ram 1500 V	DT	4	EU-RAM-1500-V-DT-CREWCAB-4X4-LONGBED-01	HIGH	Crew Cab按6英尺4英寸货斗拆分。	READY
134370	134370	Hatchback	Leon III facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
134372	134372	Convertible	D8 GTO-40		2	EU-DONKERVOORT-D8-GTO-40-CONVERTIBLE-01	HIGH		READY
134375_prefl	134375	MPV	ix20 I	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	HIGH	生产区间跨越2015年改款，按改款前外廓拆分。	READY
134375_facelift	134375	MPV	ix20 I facelift	JC	5	EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	HIGH	生产区间跨越2015年改款，按改款后外廓拆分。	READY
134376	134376	Hatchback	Dué III		3	EU-MICROCAR-DUE-III-HATCHBACK-3D-01	HIGH		READY
134377	134377	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	HIGH		READY
134379	134379	Sedan	Sonata VII	LF	4	EU-HYUNDAI-SONATA-VII-LF-SEDAN-01	HIGH		READY
134380	134380	Wagon	i40 I facelift	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH		READY
134381	134381	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
134382	134382	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
134383	134383	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
134384	134384	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134385	134385	SUV	Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH		READY
134386	134386	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
134389	134389	SUV	Hover H6 I		5	EU-GREAT-WALL-HOVER-H6-I-SUV-01	HIGH		READY
134390	134390	Hatchback	Leon III facelift	5F	5	EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	HIGH		READY
134392	134392	Wagon	Leon III ST facelift	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
134394	134394	SUV	UX I	MZAA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134395	134395	Wagon	Leon III ST facelift	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
134396	134396	SUV	UX I	MZAH15	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134398	134398	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
134399	134399	SUV	UX I	MZAH15	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134400	134400	SUV	UX I	MZAH10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134401	134401	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
134402	134402	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
134405	134405	SUV	Sorento III facelift	UM	5	EU-KIA-SORENTO-III-SUV-FACELIFT-01	HIGH		READY
134406	134406	SUV	Sorento III facelift	UM	5	EU-KIA-SORENTO-III-SUV-FACELIFT-01	HIGH		READY
134433	134433	SUV	G3 I		5	EU-XPENG-G3-I-SUV-PREFL-01	HIGH		READY
134437	134437	Coupe	DBS Superleggera	AM7	2	EU-ASTON-MARTIN-DBS-SUPERLEGGERA-AM7-COUPE-01	HIGH		READY
134438	134438	Hatchback	Rapide AMR		4	EU-ASTON-MARTIN-RAPIDE-AMR-LIFTBACK-01	HIGH		READY
134439	134439	SUV	UX I	MZAH10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134441	134441	SUV	Range Rover Velar	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	HIGH		READY
134445	134445	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
134446	134446	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
134447	134447	Hatchback	Ibiza III	6L1		EU-SEAT-IBIZA-III-6L-HATCHBACK-01	MEDIUM	Ktype未独立限定3门或5门；两者外廓三维一致。	READY
134448	134448	SUV	UX I	MZAA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH		READY
134453	134453	Sedan	ES VII	AXZA10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH		READY
134461	134461	Sedan	ES VII	AXZA10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH		READY
134467	134467	Sedan	ES VII	GSZ10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH		READY
134479	134479	Coupe	LC I	URZ100	2	EU-LEXUS-LC-I-Z100-COUPE-01	HIGH		READY
134480	134480	Van	Fiesta V	JH1	3	EU-FORD-FIESTA-V-JH1-VAN-3D-01	HIGH		READY
134482_prefl	134482	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	生产区间跨越Focus II改款，按改款前旅行厢式外廓拆分。	READY
134482_facelift	134482	Van	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	生产区间跨越Focus II改款，按改款后旅行厢式外廓拆分。	READY
134483_prefl	134483	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	生产区间跨越Focus II改款，按改款前旅行厢式外廓拆分。	READY
134483_facelift	134483	Van	Focus II facelift	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	生产区间跨越Focus II改款，按改款后旅行厢式外廓拆分。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3301-3400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-XD3-II-G01-SUV-PREFL-01	4718	1897	1655	Auto-Data	https://www.auto-data.net/en/alpina-xd3-g01-generation-6138
EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	5052	1913	1422	Car and Driver	https://www.caranddriver.com/mercedes-amg/s63/specs/2019/mercedes-amg_s63-s65_mercedes-amg-s63-4matic-cabriolet_2019
EU-ALPINA-D5-S-G30-SEDAN-01	4956	1868	1466	Alpina D5 S official brochure	https://kurumacatalog.com/wp-content/uploads/2020/05/2017_Alpina_D5S_Biturbo_limousine_Touring_catalog.pdf
EU-VW-PASSAT-ALLTRACK-B8-WAGON-PREFL-01	4777	1832	1530	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-2.0-tsi-272hp-4motion-dsg-36124
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-200-184hp-29667
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200-184hp-4matic-9g-tronic-30770
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450	Auto-Data	https://www.auto-data.net/en/chevrolet-epica-2.0-d-150hp-52547
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/arona/cars-specs-brochure-KJ7-NA-december-2018.pdf
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603	Auto-Data	https://www.auto-data.net/en/skoda-karoq-1.5-tsi-150hp-31962
EU-MERCEDES-BENZ-GLA-X156-SUV-FACELIFT-01	4424	1804	1494	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2533895/mercedes-benz_gla_200.html
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Newsroom	https://www.volkswagen-newsroom.com/en/leading-the-way-the-new-touareg-2405/exterior-design-tailor-made-for-freedom-2416
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Auto-Data	https://www.auto-data.net/en/audi-q2-35-tfsi-150hp-35047
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-facelift-2016-generation-4746
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-c-180-1.6-156hp-9g-tronic-33290
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-180-1.6-156hp-9g-tronic-33194
EU-SEAT-ALHAMBRA-II-7N-MPV-FACELIFT-01	4854	1904	1720	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/3100985/seat_alhambra_2_0_tdi_cr_150.html
EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	5125	1905	1493	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2560565/mercedes-benz_s_350_d_4matic.html
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	4696	1923	1624	Auto-Data	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2018-2.0-245hp-pdk-34454
EU-TOYOTA-ALPHARD-AH30-MPV-FACELIFT-01	4945	1850	1935	Toyota Japan used-car catalog	https://toyota.jp/ucar/catalog/brand-TOYOTA/car-ALPHARD/201810/10118373/
EU-TOYOTA-VELLFIRE-AH30-MPV-FACELIFT-01	4935	1850	1935	Toyota Japan used-car catalog	https://toyota.jp/ucar/catalog/brand-TOYOTA/car-VELLFIRE/201801/10113474/
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	Auto-Data	https://www.auto-data.net/en/seat-ibiza-v-1.0-mpi-80hp-35882
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Auto-Data	https://www.auto-data.net/en/audi-q3-ii-f3-40-tfsi-190hp-quattro-s-tronic-34921
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655	Auto-Data	https://www.auto-data.net/en/skoda-kodiaq-generation-5336
EU-MCLAREN-SENNA-P15-COUPE-01	4744	1958	1229	McLaren Automotive	https://cars.mclaren.com/en/legacy/mclaren-senna
EU-SKODA-KODIAQ-I-RS-SUV-PREFL-01	4699	1882	1686	Skoda Kodiaq RS official technical data	https://cdn.skoda-storyboard.com/2019/02/TD-KODIAQ-RS-en.pdf
EU-SEAT-TARRACO-I-KN2-SUV-01	4735	1839	1674	Auto-Data	https://www.auto-data.net/en/seat-tarraco-generation-6553
EU-TOYOTA-C-HR-I-AX10-SUV-01	4360	1795	1565	Auto-Data	https://www.auto-data.net/en/toyota-c-hr-i-1.2-116hp-26892
EU-VW-T-CROSS-I-C1-SUV-PREFL-01	4108	1760	1584	Volkswagen T-Cross official press pack	https://www.vwpress.co.uk/assets/documents/original/22700-21868TCrosspresspackD2LR.pdf
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-b8-2.0-tsi-272hp-4motion-dsg-36140
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b8-2.0-tsi-272hp-dsg-4motion-36137
EU-TOYOTA-LAND-CRUISER-PRADO-J150-SUV-5D-FACELIFT-01	4840	1885	1845	Toyota UK Land Cruiser official technical specifications	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/new-cars/commercial-vehicles/LC150.pdf
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-SINGLECAB-01	5330	1800	1795	Auto-Data	https://www.auto-data.net/en/toyota-hilux-model-403
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-EXTRACAB-01	5330	1855	1810	Auto-Data	https://www.auto-data.net/en/toyota-hilux-model-403
EU-TOYOTA-HILUX-VIII-AN120-PICKUP-DOUBLECAB-01	5330	1855	1815	Auto-Data	https://www.auto-data.net/en/toyota-hilux-double-cab-viii-facelift-2017-2.4d-150hp-4x4-32846
EU-AUDI-E-TRON-I-GE-SUV-01	4901	1935	1629	Audi e-tron 55 quattro UK technical data	https://press.audi.co.uk/assets/documents/original/8395-5Audietron55quattroUKTechnicalDataMarch2019.pdf
EU-NISSAN-PRIMERA-P11-SEDAN-PREFL-01	4430	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-p11-2.0-16v-130hp-617
EU-NISSAN-PRIMERA-P11-144-SEDAN-FACELIFT-01	4520	1720	1410	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Nissan/M1111/Primera-P11-144
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Auto-Data	https://www.auto-data.net/en/land-rover-range-rover-evoque-ii-2.0-td4-150hp-34876
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-c-320-cdi-v6-224hp-4matic-7g-tronic-52860
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s204-facelift-2011-generation-4108
EU-BMW-X7-G07-SUV-01	5151	2000	1805	Auto-Data	https://www.auto-data.net/en/bmw-x7-g07-30d-265hp-xdrive-steptronic-34590
EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	5096	1871	1479	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-CDI-4MATIC-BlueEFFICIENCY-2009---2010.xhtml?oid=191730299
EU-RAM-1500-V-DT-CREWCAB-4X2-SHORTBED-01	5916	2084	1968	RAM 1500 official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf
EU-RAM-1500-V-DT-CREWCAB-4X2-LONGBED-01	6142	2084	1966	RAM 1500 official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf
EU-RAM-1500-V-DT-CREWCAB-4X4-SHORTBED-01	5916	2084	1971	RAM 1500 official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf
EU-RAM-1500-V-DT-CREWCAB-4X4-LONGBED-01	6142	2084	1968	RAM 1500 official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459	Auto-Data	https://www.auto-data.net/en/seat-leon-iii-facelift-2016-1.0-tsi-86hp-35883
EU-DONKERVOORT-D8-GTO-40-CONVERTIBLE-01	3836	1850	1081	Donkervoort	https://www.donkervoort.com/en/models/heritage/d8-gto-40/
EU-HYUNDAI-IX20-I-JC-MPV-PREFL-01	4100	1765	1600	Auto-Data	https://www.auto-data.net/en/hyundai-ix20-model-2117
EU-HYUNDAI-IX20-I-JC-MPV-FACELIFT-01	4115	1765	1600	Auto-Data	https://www.auto-data.net/en/hyundai-ix20-facelift-2015-generation-4833
EU-MICROCAR-DUE-III-HATCHBACK-3D-01	2870	1500	1485	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/microcar/due/1generation-facelift/324298/
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-01	4770	1890	1680	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-iv-tm-generation-6121
EU-HYUNDAI-SONATA-VII-LF-SEDAN-01	4855	1865	1475	Australian Car.Reviews	https://australiancar.reviews/review-hyundai-lf-sonata-2015-19/
EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	4775	1815	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/2018/2767760/hyundai_i40_kombi_wagon_1_6_crdi_136.html
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-generation-5503
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Auto-Data	https://www.auto-data.net/en/hyundai-i30-iii-wagon-generation-5960
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2967170/mercedes-benz_b_180_d.html
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Auto-Data	https://www.auto-data.net/en/kia-stonic-1.4i-100hp-31118
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485	Auto-Data	https://www.auto-data.net/en/kia-picanto-model-291
EU-GREAT-WALL-HOVER-H6-I-SUV-01	4640	1825	1745	Auto-Data	https://www.auto-data.net/en/great-wall-hover-h6-1.5-143hp-4x4-22092
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454	Auto-Data	https://www.auto-data.net/en/seat-leon-iii-st-facelift-2016-1.5-tsi-150hp-35798
EU-LEXUS-UX-I-ZA10-SUV-01	4495	1840	1540	Lexus global newsroom	https://global.toyota/en/newsroom/lexus/25335735.html
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Auto-Data	https://www.auto-data.net/en/kia-ceed-iii-1.4-100hp-34226
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400	Auto-Data	https://www.auto-data.net/en/kia-stinger-2.0-gdi-245hp-automatic-36022
EU-KIA-SORENTO-III-SUV-FACELIFT-01	4800	1890	1690	Auto-Data	https://www.auto-data.net/en/kia-sorento-iii-facelift-2018-3.5-v6-249hp-awd-automatic-33255
EU-XPENG-G3-I-SUV-PREFL-01	4450	1820	1610	XPeng	https://www.xiaopeng.com/content/3395.html
EU-ASTON-MARTIN-DBS-SUPERLEGGERA-AM7-COUPE-01	4712	1968	1280	Aston Martin	https://www.astonmartin.com/en/our-world/news/2018/6/26/introducing-the-new-dbs-superleggera-two-illustrious-names-one-magnificent-super-gt
EU-ASTON-MARTIN-RAPIDE-AMR-LIFTBACK-01	5019	1929	1350	Automobile Dimension	https://www.automobiledimension.com/model/aston-martin/rapide-amr
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	4803	1930	1665	Auto-Data	https://www.auto-data.net/en/land-rover-range-rover-velar-generation-5596
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	Auto-Data	https://www.auto-data.net/en/audi-a4-b9-8w-35-tfsi-150hp-mild-hybrid-s-tronic-36098
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Auto-Data	https://www.auto-data.net/en/audi-a4-avant-b9-8w-35-tfsi-150hp-mild-hybrid-s-tronic-36099
EU-SEAT-IBIZA-III-6L-HATCHBACK-01	3953	1698	1441	Auto-Data	https://www.auto-data.net/en/seat-ibiza-iii-1.9-sdi-64hp-13483
EU-LEXUS-ES-VII-XZ10-SEDAN-01	4975	1865	1445	CarExpert New Zealand	https://www.carexpert.co.nz/lexus/es/2019-base-2-5l-sedan-fwd-petrol-automatic-joagwf8o20180921
EU-LEXUS-LC-I-Z100-COUPE-01	4770	1920	1345	CarsGuide	https://www.carsguide.com.au/lexus/lc/lc500/car-dimensions/2019
EU-FORD-FIESTA-V-JH1-VAN-3D-01	3916	1683	1432	Automobile-Catalog	https://www.automobile-catalog.com/car/2002/959930/ford_fiesta_1_4_16v.html
EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	4472	1840	1501	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/966335/ford_focus_estate_1_6_16v_lx.html
EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	4468	1839	1501	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Ford/M8333/Focus-2-Wagon-Facelift
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3301-3400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf "https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2019_Ram_1500_SP160igecpp6jn85geq3o0r4cs90.pdf"
[2]: https://www.auto-data.net/en/toyota-hilux-model-403?utm_source=chatgpt.com "Toyota Hilux | Technical Specs, Fuel consumption ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2790 行）
- 累计尺寸组：dimension_groups_final.tsv（1356 行）

