# 任务：all 第 4501-4600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0046__0884ee44


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4501-4600 行

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
all 第 4501-4600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-E-TRON-I-GE-SUV-01	4901	1935	1629
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
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	5943	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	5358	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	6308	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-CH1-01	4908	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-LH1-01	5943	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MH1-01	5358	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-MLH1-01	5708	2050	2254
EU-FIAT-DUCATO-III-X250-CHASSIS-SCAB-XLH1-01	6308	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-BUS-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	5998	2050	2522
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	5998	2050	2760
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	6363	2050	2522
EU-FIAT-DUCATO-III-X290-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-X290-L1H2-01	4963	2050	2524
EU-FIAT-DUCATO-III-X290-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-X290-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	4908	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	5358	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X290-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-X290-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	5413	2050	2269
EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	5413	2050	2254
EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	5413	2050	2539
EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	5413	2050	2524
EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	5998	2050	2534
EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	5998	2050	2524
EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	5998	2050	2774
EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	5998	2050	2764
EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	6363	2050	2534
EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	6363	2050	2539
EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	6363	2050	2774
EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	6363	2050	2779
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	3585	1595	1540
EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	3565	1595	1540
EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	3665	1660	1500
EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	4065	1760	1529
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449
EU-HYUNDAI-I20-II-GB-HATCHBACK-01	4035	1734	1474
EU-HYUNDAI-I20-II-GB-HATCHBACK-5D-01	4035	1734	1474
EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	4300	1780	1470
EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	4485	1780	1500
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497
EU-LADA-VESTA-I-SPORT-SEDAN-01	4420	1774	1478
EU-LADA-VESTA-I-SW-CROSS-WAGON-01	4424	1785	1537
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512
EU-MERCEDES-BENZ-GLB-X247-AMG-GLB35-SUV-01	4650	1850	1662
EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	4634	1834	1659
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971
EU-NISSAN-NV300-I-L1H2-01	4999	1956	2493
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971
EU-NISSAN-NV300-I-L2H2-01	5399	1956	2490
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-LONG-01	5333	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-FACELIFT-STANDARD-01	4983	1920	1890
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895
EU-PEUGEOT-EXPERT-III-K0-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-LONG-01	5331	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-FACELIFT-STANDARD-01	4981	1924	1910
EU-PEUGEOT-EXPERT-III-K0-VAN-LONG-01	5309	1920	1935
EU-PEUGEOT-EXPERT-III-K0-VAN-STANDARD-01	4959	1920	1904
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-LONG-01	5333	1920	1890
EU-PEUGEOT-TRAVELLER-I-FACELIFT-MPV-STANDARD-01	4983	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2272
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2263
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-PREFL-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-PREFL-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-FACELIFT-01	5557	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-PREFL-01	5530	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-FACELIFT-01	6207	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-PREFL-01	6180	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-FACELIFT-01	5075	2070	2303
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-PREFL-01	5048	2070	2307
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-FACELIFT-01	5075	2070	2496
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-PREFL-01	5048	2070	2500
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-FACELIFT-01	5575	2070	2495
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-PREFL-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-PREFL-01	6198	2070	2488
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-FACELIFT-01	4302	1808	1471
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-PREFL-01	4295	1808	1491
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	Gls	580 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	360	489	Nov 2019	-	2024-03-01	138495
Audi	E-Tron	55 Quattro	SUV	Allrad	Elektro	300	408	Sep 2019	Jul 2023	2026-03-01	138500
Peugeot	Expert	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Sep 2019	Dec 2022	2025-12-01	138504
Peugeot	Traveller	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Sep 2019	Dec 2022	2025-12-01	138505
Mercedes-benz	Gle	GLE 350 D 4-matic	SUV	Allrad	Diesel	200	272	Nov 2019	Mar 2023	2024-03-01	138508
Mercedes-benz	Gle	GLE 400 D 4-matic	SUV	Allrad	Diesel	243	330	Nov 2019	Mar 2023	2024-03-01	138509
Mercedes-benz	Gle	AMG GLE 53 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	320	435	Nov 2019	-	2024-03-01	138510
Citroën	Berlingo	Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Oct 2019	-	2024-03-01	138514
Fiat	Ducato	140 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138535
Fiat	Ducato	160 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138536
Fiat	Ducato	160 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138537
Fiat	Ducato	140 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138538
Fiat	Ducato	140 Multijet 2,3 D	Bus	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138539
Fiat	Ducato	160 Multijet 2,3 D	Bus	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138540
Fiat	Ducato	180 Multijet 2,3 D	Bus	Frontantrieb	Diesel	130	177	May 2019	-	2024-03-01	138541
Mazda	Mx-30	E-skyactiv	SUV	Frontantrieb	Elektro	107	145	May 2020	-	2024-03-01	138574
Mercedes-benz	Gls	AMG 63 4matic+ EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Nov 2019	-	2024-03-01	138594
Mercedes-benz	Gls	Maybach 600 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	410	557	Nov 2019	-	2024-03-01	138595
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	420	571	Nov 2019	Mar 2023	2024-03-01	138596
Mercedes-benz	Gle	AMG GLE 63 S EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Nov 2019	-	2024-03-01	138597
Citroën	Jumper iii	2.2 Bluehdi 120	Kasten	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138598
Citroën	Jumper iii	2.2 Bluehdi 140	Kasten	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138599
Citroën	Jumper iii	2.2 Bluehdi 165	Kasten	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138600
Honda	Civic x	1.6 I-vtec LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	92	125	Jan 2019	Dec 2022	2024-03-01	138601
Citroën	Jumper iii	2.2 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138602
Citroën	Jumper iii	2.2 Bluehdi 140	Bus	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138603
Citroën	Jumper iii	2.2 Bluehdi 165	Bus	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138604
Citroën	Jumper iii	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138605
Citroën	Jumper iii	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138606
Citroën	Jumper iii	2.2 Bluehdi 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138607
Lada	Vesta	1.6	Stufenheck	Frontantrieb	Benzin	83	113	Nov 2019	-	2024-03-01	138623
Lada	Vesta	1.6	Kombi	Frontantrieb	Benzin	83	113	Nov 2019	-	2024-03-01	138624
Citroën	Jumper iii	2.0 Bluehdi 130 4X4	Kasten	Allrad	Diesel	96	130	Nov 2015	Sep 2019	2025-12-01	138629
Citroën	Jumper iii	2.2 HDI 130 4X4	Kasten	Allrad	Diesel	96	130	Jan 2012	May 2016	2025-12-01	138630
Peugeot	Boxer	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2024-05-01	138631
Peugeot	Boxer	2.2 Bluehdi 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2024-05-01	138632
Peugeot	Boxer	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2024-05-01	138639
Renault	Master pro	DCI 120	Kasten	Heckantrieb	Diesel	85	116	Jun 2005	Apr 2010	2024-03-01	138646
Renault	Master pro	DCI 160	Kasten	Heckantrieb	Diesel	115	156	May 2004	Apr 2010	2024-03-01	138649
Renault	Master pro	DCI 130	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	131	Jun 2005	Apr 2010	2024-03-01	138654
Renault	Master pro	DCI 150	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2005	Apr 2010	2024-03-01	138655
Renault	Trafic iii	1.6 DCI 120	Kasten	Frontantrieb	Diesel	89	121	Jul 2015	-	2024-03-01	138657
Infiniti	Qx50 ii	2.0 AWD	SUV	Allrad	Benzin	197	268	Nov 2017	-	2024-03-01	138664
Lynk & CO	1	HEV	SUV	Frontantrieb	Benzin/Elektro	145	197	Nov 2021	-	2024-03-01	138665
Mercedes-benz	R-Klasse	R 300 4-matic	Großraumlimousine	Allrad	Benzin	170	231	Jul 2009	Dec 2011	2024-03-01	138666
Ford	Kuga iii	2.5 Duratec Plug-in-hybrid	SUV	Frontantrieb	Benzin/Elektro	165	224	Jul 2019	-	2024-03-01	138670
Ford	Kuga iii	2.0 Ecoblue Mhev	SUV	Frontantrieb	Diesel/Elektro	110	150	Jul 2019	-	2024-03-01	138671
Ford	Kuga iii	2.0 Ecoblue 4X4	SUV	Allrad	Diesel	140	190	Jul 2019	-	2024-03-01	138672
Mercedes-benz	Sprinter 4,6-T	411 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Apr 2016	Dec 2018	2024-03-01	138674
Ford	Kuga iii	1.5 Ecoblue	SUV	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138675
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	88	120	Jul 2019	-	2024-03-01	138676
Opel	Zafira	1.9 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	110	150	Jul 2005	Apr 2015	2024-03-01	138677
Peugeot	208 ii	1.5 Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	131	Sep 2019	-	2024-03-01	138678
Opel	Zafira	1.9 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2005	Apr 2015	2024-03-01	138679
Opel	Zafira	2.2 DGI VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin	110	150	Jul 2005	Dec 2011	2024-03-01	138680
Opel	Zafira	2.0 VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin	147	200	Jul 2005	Dec 2010	2024-03-01	138681
Opel	Zafira	1.6 CNG VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Jul 2005	Apr 2015	2024-03-01	138682
Ford USA	Explorer	3.0 Ecoboost Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	336	457	Jul 2019	-	2024-03-01	138692
BMW	5	530 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	170	231	Jul 2019	Jun 2020	2024-03-01	138694
BMW	5	530 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	170	231	Jul 2019	Jun 2023	2024-03-01	138696
BMW	X3	Xdrive 30 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	215	292	Dec 2019	-	2024-03-01	138698
VW	Golf viii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	138699
VW	Golf viii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2019	-	2024-03-01	138700
VW	Golf viii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2019	-	2024-03-01	138701
VW	Golf viii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Aug 2019	-	2024-03-01	138702
Renault	Clio v	1.0 SCE 65	Schrägheck	Frontantrieb	Benzin	48	65	Nov 2019	-	2026-05-01	138714
Volvo	Xc90 ii	D5 Drive Polestar AWD	SUV	Allrad	Diesel	176	239	Mar 2016	Dec 2021	2024-05-01	138715
Volvo	Xc90 ii	T5 Drive-e Polestar AWD	SUV	Allrad	Benzin	176	239	Oct 2017	Dec 2020	2024-05-01	138716
Volvo	Xc90 ii	T5 Drive-e Polestar AWD	SUV	Allrad	Benzin	192	261	Jan 2017	Dec 2021	2025-06-01	138717
Volvo	Xc40	T5 Polestar AWD	SUV	Allrad	Benzin	183	249	Oct 2017	Sep 2019	2024-03-01	138718
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	140	190	Nov 2019	Jun 2023	2024-03-01	138720
Hyundai	I30	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jan 2009	Nov 2011	2024-03-01	138721
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	120	163	Nov 2019	Jun 2023	2024-03-01	138722
BMW	5	520 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	140	190	Nov 2019	Jun 2023	2024-03-01	138723
BMW	5	520 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	140	190	Nov 2019	-	2024-03-01	138724
Hyundai	Tucson	2.0 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	104	141	Jun 2004	Mar 2010	2024-03-01	138725
BMW	5	520 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	140	190	Nov 2019	-	2024-03-01	138726
Hyundai	I30	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	80	109	Nov 2009	Jun 2012	2024-03-01	138727
Hyundai	I10 i	1.1 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	48	65	Jan 2009	Dec 2013	2024-03-01	138740
VW	Passat alltrack b8 variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	206	280	Nov 2018	Mar 2024	2025-02-03	138741
Renault	Megane i kombi van	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	47	64	Feb 2000	Sep 2000	2024-03-01	138746
Renault	Megane i kombi van	1.9 DTI	Kasten/Kombi	Frontantrieb	Diesel	59	80	Apr 2001	Jul 2003	2024-03-01	138749
Renault	Megane i kombi van	1.4	Kasten/Kombi	Frontantrieb	Benzin	70	95	Apr 2001	Jul 2003	2024-03-01	138750
Renault	Megane i kombi van	1.9 DCI	Kasten/Kombi	Frontantrieb	Diesel	75	102	Apr 2001	Jul 2003	2024-03-01	138751
Renault	Megane i kombi van	1.9 DCI	Kasten/Kombi	Frontantrieb	Diesel	77	105	Apr 2001	Jul 2003	2024-03-01	138753
Renault	Megane i kombi van	1.6	Kasten/Kombi	Frontantrieb	Benzin	79	107	Apr 2001	Jul 2003	2024-03-01	138754
Renault	Megane i kombi van	1.8	Kasten/Kombi	Frontantrieb	Benzin	85	116	Apr 2001	Jul 2003	2024-03-01	138755
Renault	Megane i kombi van	1.6 Bifuel	Kasten/Kombi	Frontantrieb	Benzin/Autogas (LPG)	80	109	Apr 2001	Jul 2003	2024-03-01	138757
Renault	Megane i kombi van	1.6 Bifuel	Kasten/Kombi	Frontantrieb	Benzin/Autogas (LPG)	79	107	Apr 2001	Jul 2003	2024-03-01	138758
Mercedes-benz	Glb	GLB 250	SUV	Frontantrieb	Benzin	165	224	Dec 2019	-	2024-03-01	138760
Mercedes-benz	Glb	GLB 220 D	SUV	Frontantrieb	Diesel	140	190	Dec 2019	-	2024-03-01	138761
Renault	Megane iii	1.6 16V Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	81	110	May 2009	Aug 2015	2024-03-01	138767
Renault	Master iii	2.3 DCI 180 FWD	Kasten	Frontantrieb	Diesel	132	179	Jul 2019	Dec 2024	2026-03-01	138771
Hyundai	I20 i	1.2	Schrägheck	Frontantrieb	Benzin	56	76	Dec 2008	Aug 2014	2024-03-01	138773
Dacia	Dokker	1.5 Blue DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jun 2019	Dec 2021	2024-11-01	138778
Audi	E-Tron	50 Quattro	SUV	Allrad	Elektro	230	313	Sep 2019	Jul 2023	2026-03-01	138779
Audi	E-Tron	50 Quattro	SUV	Allrad	Elektro	230	313	Sep 2019	Jul 2023	2026-03-01	138780
Nissan	Nv300	2.0 DCI 120	Kasten	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138783
Nissan	Nv300	2.0 DCI 145	Kasten	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138784
Nissan	Nv300	2.0 DCI 170	Kasten	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138785


--- Round 1 / 首次发送 ---
## 更新点

* 已按跨批次索引完成 **15 个既有尺寸组复用**，未重复输出其三维和来源。
* 首次闭合并创建 **5 个新尺寸组**：Mazda MX-30、Infiniti QX50 II、Lynk & Co 01、Ford Explorer VI PHEV、Volkswagen Golf VIII。Mazda、Ford、Volkswagen 和 Infiniti 使用厂商资料；Lynk & Co 01 使用两处规格数据库交叉确认，其中宽度明确为不含后视镜。([Mazda UK 新闻门户][1])
* `138740` 的生产期覆盖 Hyundai i10 I 改款前后，已拆分为 `prefl`、`facelift` 两个稳定派生映射。
* 商用车长度/高度组合、混合 Van/MPV 车身、跨改款车型和特殊宽体套件继续保持 PENDING，未猜测性关联尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：28
* PENDING 输入 Ktype：72
* 当前映射行：101
* READY 映射行：29
* 已引用尺寸组：20
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138495	138495	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH	X167标准车身外廓。	READY
138500	138500	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138504	138504	MPV	Expert III	K0			LOW	候选为K0 Combi Compact/Standard/Long。	PENDING: 2.0 BlueHDi 120适用的车长分支尚未闭合
138505	138505	MPV	Traveller I	K0			LOW	候选为Compact/Standard/Long。	PENDING: 2.0 BlueHDi 120适用的车长分支尚未闭合
138508	138508	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167标准SUV外廓。	READY
138509	138509	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167标准SUV外廓。	READY
138510	138510	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	HIGH	AMG GLE 53外部套件外廓。	READY
138514	138514	Kasten/Großraumlimousine	Berlingo III	K9			LOW	输入同时覆盖Kasten/Großraumlimousine，候选含M/XL。	PENDING: Van/MPV及M/XL物理分支尚未闭合
138535	138535	Chassis Cab	Ducato III	X290			LOW	候选含单排/双排与多个底盘长度。	PENDING: 驾驶室与L1-L5底盘分支尚未闭合
138536	138536	Chassis Cab	Ducato III	X290			LOW	候选含单排/双排与多个底盘长度。	PENDING: 驾驶室与L1-L5底盘分支尚未闭合
138537	138537	Van	Ducato III	X290			LOW	候选含L1-L4、H1-H3及Standard/Maxi。	PENDING: 车长/车顶/底盘分支与发动机适用组合尚未闭合
138538	138538	Van	Ducato III	X290			LOW	候选含L1-L4、H1-H3及Standard/Maxi。	PENDING: 车长/车顶/底盘分支与发动机适用组合尚未闭合
138539	138539	MPV	Ducato III	X290			LOW	Bus量产车身存在多个长度与车顶。	PENDING: Bus长度/车顶分支尚未闭合
138540	138540	MPV	Ducato III	X290			LOW	Bus量产车身存在多个长度与车顶。	PENDING: Bus长度/车顶分支尚未闭合
138541	138541	MPV	Ducato III	X290			LOW	Bus量产车身存在多个长度与车顶。	PENDING: Bus长度/车顶分支尚未闭合
138574	138574	SUV	MX-30 I		5	EU-MAZDA-MX-30-I-SUV-01	HIGH	首发纯电五门外廓。	READY
138594	138594	SUV	GLS II	X167	5		LOW	AMG 63具有专用外部套件。	PENDING: AMG 63三维尚未闭合
138595	138595	SUV	GLS II	X167	5		LOW	Maybach 600具有专用外部套件。	PENDING: Maybach外廓三维尚未闭合
138596	138596	SUV	GLE II	V167	5		LOW	AMG GLE 63专用宽体/保险杠外廓。	PENDING: AMG GLE 63三维及63/63 S共用边界尚未闭合
138597	138597	SUV	GLE II	V167	5		LOW	AMG GLE 63 S专用宽体/保险杠外廓。	PENDING: AMG GLE 63三维及63/63 S共用边界尚未闭合
138598	138598	Van	Jumper III				LOW	候选含L1-L4、H1-H3。	PENDING: 2019款Van长度/车顶分支尚未闭合
138599	138599	Van	Jumper III				LOW	候选含L1-L4、H1-H3。	PENDING: 2019款Van长度/车顶分支尚未闭合
138600	138600	Van	Jumper III				LOW	候选含L1-L4、H1-H3。	PENDING: 2019款Van长度/车顶分支尚未闭合
138601	138601	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH	FC四门轿车外廓。	READY
138602	138602	MPV	Jumper III				LOW	Bus存在多个长度与车顶。	PENDING: 2019款Bus长度/车顶分支尚未闭合
138603	138603	MPV	Jumper III				LOW	Bus存在多个长度与车顶。	PENDING: 2019款Bus长度/车顶分支尚未闭合
138604	138604	MPV	Jumper III				LOW	Bus存在多个长度与车顶。	PENDING: 2019款Bus长度/车顶分支尚未闭合
138605	138605	Chassis Cab	Jumper III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 驾驶室与底盘长度分支尚未闭合
138606	138606	Chassis Cab	Jumper III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 驾驶室与底盘长度分支尚未闭合
138607	138607	Chassis Cab	Jumper III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 驾驶室与底盘长度分支尚未闭合
138623	138623	Sedan	Vesta I		4	EU-LADA-VESTA-I-SEDAN-01	HIGH	标准四门轿车外廓。	READY
138624	138624	Wagon	Vesta I		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	标准SW旅行车外廓，非SW Cross。	READY
138629	138629	Van	Jumper III				LOW	4X4 Dangel候选含多个L/H。	PENDING: 2015-2019 4X4 Van分支尚未闭合
138630	138630	Van	Jumper III				LOW	4X4 Dangel候选含多个L/H。	PENDING: 2012-2016 4X4 Van分支尚未闭合
138631	138631	Chassis Cab	Boxer III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 2019款驾驶室与底盘长度分支尚未闭合
138632	138632	Chassis Cab	Boxer III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 2019款驾驶室与底盘长度分支尚未闭合
138639	138639	Chassis Cab	Boxer III				LOW	候选含单排/双排与多个底盘长度。	PENDING: 2019款驾驶室与底盘长度分支尚未闭合
138646	138646	Van	Master II				LOW	后驱Van存在多个轴距与车顶。	PENDING: Master II后驱Van分支尚未闭合
138649	138649	Van	Master II				LOW	后驱Van存在多个轴距与车顶。	PENDING: Master II后驱Van分支尚未闭合
138654	138654	Chassis Cab	Master II				LOW	后驱底盘存在驾驶室与轴距分支。	PENDING: Master II底盘分支尚未闭合
138655	138655	Chassis Cab	Master II				LOW	后驱底盘存在驾驶室与轴距分支。	PENDING: Master II底盘分支尚未闭合
138657	138657	Van	Trafic III	X82			LOW	候选为L1H1/L1H2/L2H1/L2H2。	PENDING: 1.6 dCi 120适用的L/H组合尚未闭合
138664	138664	SUV	QX50 II	J55	5	EU-INFINITI-QX50-II-J55-SUV-01	HIGH	J55五门SUV外廓。	READY
138665	138665	SUV	01 I (facelift 2020)		5	EU-LYNK-CO-01-I-FACELIFT-SUV-01	MEDIUM	欧洲版HEV五门外廓。	READY
138666	138666	MPV	R-Class I	W251	5		LOW	W251存在标准轴距与长轴距外廓。	PENDING: R 300 4MATIC轴距分支尚未闭合
138670	138670	SUV	Kuga III		5		LOW	普通车身与ST-Line保险杠长度、车顶高度存在差异。	PENDING: 外部套件与高度分支尚未闭合
138671	138671	SUV	Kuga III		5		LOW	普通车身与ST-Line保险杠长度、车顶高度存在差异。	PENDING: 外部套件与高度分支尚未闭合
138672	138672	SUV	Kuga III		5		LOW	普通车身与ST-Line保险杠长度、车顶高度存在差异。	PENDING: 外部套件与高度分支尚未闭合
138674	138674	Chassis Cab	Sprinter II	W906			LOW	4.6t底盘存在驾驶室与轴距分支。	PENDING: W906底盘驾驶室/轴距分支尚未闭合
138675	138675	SUV	Kuga III		5		LOW	普通车身与ST-Line保险杠长度、车顶高度存在差异。	PENDING: 外部套件与高度分支尚未闭合
138676	138676	SUV	Kuga III		5		LOW	普通车身与ST-Line保险杠长度、车顶高度存在差异。	PENDING: 外部套件与高度分支尚未闭合
138677	138677	Kasten/Großraumlimousine	Zafira B	A05			LOW	输入同时覆盖Kasten/Großraumlimousine并跨改款。	PENDING: Van/MPV与pre-facelift/facelift边界尚未闭合
138678	138678	Hatchback	208 II	P21	5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH	P21五门掀背外廓。	READY
138679	138679	Kasten/Großraumlimousine	Zafira B	A05			LOW	输入同时覆盖Kasten/Großraumlimousine并跨改款。	PENDING: Van/MPV与pre-facelift/facelift边界尚未闭合
138680	138680	Kasten/Großraumlimousine	Zafira B	A05			LOW	输入同时覆盖Kasten/Großraumlimousine并跨改款。	PENDING: Van/MPV与pre-facelift/facelift边界尚未闭合
138681	138681	Kasten/Großraumlimousine	Zafira B	A05			LOW	输入同时覆盖Kasten/Großraumlimousine并跨改款。	PENDING: Van/MPV与pre-facelift/facelift边界尚未闭合
138682	138682	Kasten/Großraumlimousine	Zafira B	A05			LOW	输入同时覆盖Kasten/Großraumlimousine并跨改款。	PENDING: Van/MPV与pre-facelift/facelift边界尚未闭合
138692	138692	SUV	Explorer VI	U625	5	EU-FORD-EXPLORER-VI-U625-SUV-01	HIGH	欧洲版3.0 PHEV五门外廓。	READY
138694	138694	Sedan	5 Series G30	G30	4		LOW	530e可能具有与普通G30不同的整车高度。	PENDING: 530e专属三维尚未闭合
138696	138696	Sedan	5 Series G30	G30	4		LOW	生产期跨G30 LCI边界。	PENDING: pre-facelift/facelift及530e xDrive三维尚未闭合
138698	138698	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 xDrive30e标准SUV外廓。	READY
138699	138699	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138700	138700	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138701	138701	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138702	138702	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138714	138714	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	Clio V五门掀背外廓。	READY
138715	138715	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138716	138716	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138717	138717	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138718	138718	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138720	138720	Sedan	5 Series G30	G30	4		LOW	生产期覆盖G30 LCI，普通/M Sport长度高度可能不同。	PENDING: pre-facelift/facelift外廓尚未闭合
138721	138721	Hatchback	i30 I	FD	5		LOW	第一代FD掀背三维未在缓存中。	PENDING: FD Hatchback三维尚未闭合
138722	138722	Sedan	5 Series G30	G30	4		LOW	生产期覆盖G30 LCI，普通/M Sport长度高度可能不同。	PENDING: pre-facelift/facelift外廓尚未闭合
138723	138723	Sedan	5 Series G30	G30	4		LOW	生产期覆盖G30 LCI，普通/M Sport长度高度可能不同。	PENDING: pre-facelift/facelift外廓尚未闭合
138724	138724	Wagon	5 Series G31	G31	5		LOW	生产期覆盖G31 LCI。	PENDING: pre-facelift/facelift外廓尚未闭合
138725	138725	SUV	Tucson I	JM	5		LOW	第一代JM三维未在缓存中。	PENDING: JM SUV三维尚未闭合
138726	138726	Wagon	5 Series G31	G31	5		LOW	生产期覆盖G31 LCI。	PENDING: pre-facelift/facelift外廓尚未闭合
138727	138727	Wagon	i30 I	FD	5		LOW	第一代FD旅行版三维未在缓存中。	PENDING: FD Wagon三维尚未闭合
138740_prefl	138740	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	HIGH	PA改款前五门外廓。	READY
138740_facelift	138740	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖PA改款后外廓。	READY
138741	138741	Wagon	Passat Alltrack B8	3G	5		LOW	Alltrack专用保险杠与离地高度需独立闭合。	PENDING: B8 Alltrack三维尚未闭合
138746	138746	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138749	138749	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138750	138750	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138751	138751	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138753	138753	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138754	138754	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138755	138755	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138757	138757	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138758	138758	Kasten/Kombi	Megane I Grandtour Van		5		LOW	商用Grandtour跨Phase I/II。	PENDING: 改款边界及Van三维尚未闭合
138760	138760	SUV	GLB I	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247前驱标准SUV外廓。	READY
138761	138761	SUV	GLB I	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247前驱标准SUV外廓。	READY
138767	138767	Hatchback	Megane III	B95	5		LOW	生产期跨pre-facelift/facelift，现有缓存为Van外廓。	PENDING: 乘用Hatchback两阶段尺寸组尚未闭合
138771	138771	Van	Master III	X62			LOW	FWD Van存在L1-L4与H1-H3组合。	PENDING: 2019 facelift L/H分支尚未闭合
138773	138773	Hatchback	i20 I	PB	5		LOW	第一代PB五门掀背三维未在缓存中。	PENDING: PB Hatchback三维尚未闭合
138778	138778	Kasten/Großraumlimousine	Dokker I				LOW	输入同时覆盖Kasten/Großraumlimousine，缓存仅有MPV组。	PENDING: Van/MPV物理边界及共组条件尚未闭合
138779	138779	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138780	138780	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138783	138783	Van	NV300 I				LOW	候选为L1H1/L1H2/L2H1/L2H2。	PENDING: 2.0 dCi发动机适用的L/H组合尚未闭合
138784	138784	Van	NV300 I				LOW	候选为L1H1/L1H2/L2H1/L2H2。	PENDING: 2.0 dCi发动机适用的L/H组合尚未闭合
138785	138785	Van	NV300 I				LOW	候选为L1H1/L1H2/L2H1/L2H2。	PENDING: 2.0 dCi发动机适用的L/H组合尚未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-MX-30-I-SUV-01	4395	1795	1570	Mazda UK press release – Mazda MX-30	https://uk.mazda-press.com/news/2019/mazda-mx-30--an-electric-car-for-the-environment-and-the-driver/
EU-INFINITI-QX50-II-J55-SUV-01	4693	1903	1679	INFINITI USA – QX50 all-new platform technical dimensions	https://usa.infinitinews.com/en-US/releases/infiniti-qx50-a-luxury-crossover-with-world-first-technologies-and-an-all-new-platform
EU-LYNK-CO-01-I-FACELIFT-SUV-01	4541	1857	1694	Automobile Dimension – LynkCo 01 2021;Encycarpedia – 2021 Lynk & Co 01 HEV	https://www.automobiledimension.com/model/lynkco/01;https://www.encycarpedia.com/lynk-co/21-01-hybrid-electric-suv
EU-FORD-EXPLORER-VI-U625-SUV-01	5049	2004	1778	Ford Explorer official owner manual – vehicle dimensions	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2024845&Uid=G2024844&buildtype=web&countryCode=DEU&div=f&languageCode=de&moidRef=G910634&userMarket=aut&vFilteringEnabled=False&variantid=8595
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456	Volkswagen Newsroom – Golf design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609/design-and-dimensions-5618
```

## 下一步优先处理

1. 批量闭合 Fiat Ducato、Citroën Jumper、Peugeot Boxer 的同平台 Van、Bus、Chassis Cab 长度和车顶组合。
2. 处理 Expert、Traveller、Trafic、NV300、Master III 的发动机适用 L/H 分支，并优先复用已有组。
3. 闭合 Mercedes AMG/Maybach、BMW G30/G31 LCI、Ford Kuga 普通与 ST-Line 等跨改款或外部套件差异。
4. 最后处理 Hyundai i20/i30/Tucson、Megane I/III、R-Class、Passat Alltrack 等缺失单车型组。

推进信号：CONTINUE

[1]: https://uk.mazda-press.com/news/2019/mazda-mx-30--an-electric-car-for-the-environment-and-the-driver/?tag=Motorshows&year=2019&utm_source=chatgpt.com "Mazda MX-30 – An electric car for the environment…. and the driver"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 复用 Trafic III 与 NV300 已有的 L1H1、L1H2、L2H1、L2H2 尺寸组，完成 4 个 Ktype、16 条派生映射；未重复输出尺寸组。
* 闭合 Hyundai i30 I 掀背/旅行版改款前后、Tucson I JM 2WD、Passat Alltrack B8 facelift、Megane III B95 掀背改款前后，共首次创建 8 个尺寸组。i30 各阶段外廓、Tucson 2WD 和 Megane 两阶段三维均已按不含后视镜宽度核对。([汽车目录][1])
* Passat Alltrack 2.0 TSI 280 对应 B8 facelift 外廓，闭合为 4777 × 1832 × 1530 mm。([汽车数据网][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：37
* PENDING 输入 Ktype：63
* 当前映射行：116
* READY 映射行：53
* 已确认并被引用尺寸组：36
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138657_l1h1	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138657_l1h2	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138657_l2h1	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理外廓。	READY
138657_l2h2	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理外廓。	READY
138721_prefl	138721	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	HIGH	FD五门掀背改款前外廓。	READY
138721_facelift	138721	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖FD改款后外廓。	READY
138725	138725	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	HIGH	JM前驱标准SUV外廓。	READY
138727_prefl	138727	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	HIGH	FD旅行版改款前外廓。	READY
138727_facelift	138727	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖FD旅行版改款后外廓。	READY
138741	138741	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-ALLTRACK-B8-WAGON-FACELIFT-01	HIGH	B8 facelift Alltrack专用外廓。	READY
138767_prefl	138767	Hatchback	Megane III	B95	5	EU-RENAULT-MEGANE-III-B95-HATCHBACK-PREFL-01	HIGH	B95五门掀背改款前外廓。	READY
138767_facelift	138767	Hatchback	Megane III	B95	5	EU-RENAULT-MEGANE-III-B95-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖B95改款后外廓。	READY
138783_l1h1	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138783_l1h2	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138783_l2h1	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138783_l2h2	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
138784_l1h1	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138784_l1h2	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138784_l2h1	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138784_l2h2	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
138785_l1h1	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138785_l1h2	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138785_l2h1	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138785_l2h2	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	4245	1775	1480	Automobile-Catalog – 2009 Hyundai i30 hatchback	https://www.automobile-catalog.com/car/2009/1181435/hyundai_i30_2_0_premium.html
EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	4280	1775	1480	Automobile-Catalog – 2010 Hyundai i30 facelift hatchback	https://www.automobile-catalog.com/car/2010/1606985/hyundai_i30_blue_1_6_crdi_90_classic.html
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680	Automobile-Catalog – Hyundai Tucson 2.0 2WD	https://www.automobile-catalog.com/car/2005/1178480/hyundai_tucson_2_0_2wd_gsi.html
EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	4475	1775	1565	Automobile-Catalog – Hyundai i30cw pre-facelift	https://www.automobile-catalog.com/car/2010/1181825/hyundai_i30cw_2_0_style.html
EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	4500	1775	1565	Auto-Data – Hyundai i30 I CW facelift generation	https://www.auto-data.net/en/hyundai-i30-i-cw-facelift-2010-generation-5725
EU-VW-PASSAT-ALLTRACK-B8-WAGON-FACELIFT-01	4777	1832	1530	Auto-Data – Volkswagen Passat Alltrack B8 2.0 TSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-2.0-tsi-272hp-4motion-dsg-36124
EU-RENAULT-MEGANE-III-B95-HATCHBACK-PREFL-01	4295	1808	1471	Auto-Data – Renault Megane III 1.6 16V Ethanol	https://www.auto-data.net/en/renault-megane-iii-1.6-16v-110hp-ethanol-30363
EU-RENAULT-MEGANE-III-B95-HATCHBACK-FACELIFT-01	4302	1808	1471	Automobile-Catalog – 2012 Renault Megane hatchback	https://www.automobile-catalog.com/car/2012/2960225/renault_megane_hatch_1_6_16v_100.html
```

## 5. 下一步优先处理

1. 使用既有 X290、Jumper III、Boxer III 缓存，批量拆分 Van、Bus、Chassis Cab 的 L/H、单排/双排分支。
2. 闭合 Expert、Traveller 的 Compact、Standard、Long 发动机适用边界。
3. 处理 Mercedes AMG/Maybach、BMW G30/G31 LCI 与 530e、Ford Kuga 普通/ST-Line 外廓。
4. 最后处理 Master II/III、Sprinter W906、Zafira B、Dokker 和 Megane I Van。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/1181435/hyundai_i30_2_0_premium.html?utm_source=chatgpt.com "2009 Hyundai i30 2.0 Premium Specs Review (105 kW ..."
[2]: https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-2.0-tsi-272hp-4motion-dsg-36124?utm_source=chatgpt.com "Specs of Volkswagen Passat Alltrack (B8) 2.0 TSI (272 Hp) ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* Peugeot Expert Kombi 与 Traveller 的 `2.0 BlueHDi 120` 已按 Compact、Standard、Long 三种既有外廓完成派生关联；Expert 官方资料确认该动力可覆盖三种长度。([Stellantis Media][1])
* Fiat Ducato `140/160 Multijet` 的底盘驾驶室完成单排 5 分支、双排 3 分支缓存关联；同批两款 Kasten 完成 14 个 L/H 与 Standard/Maxi 分支关联。Fiat 资料确认该系列同时提供单排、双排驾驶室以及 140/160 hp 动力，2019 年车型目录亦覆盖多个车长和车顶组合。([菲亚特商用车][2])
* 本轮全部复用已有尺寸组，未重新抓取或重复输出尺寸事实。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：43
* PENDING 输入 Ktype：57
* 当前映射行：160
* READY 映射行：103
* PENDING 映射行：57
* 已确认并被引用尺寸组：64
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138504_compact	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	Compact Combi物理外廓。	READY
138504_standard	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	Standard Combi物理外廓。	READY
138504_long	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	Long Combi物理外廓。	READY
138505_compact	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact MPV物理外廓。	READY
138505_standard	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard MPV物理外廓。	READY
138505_long	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long MPV物理外廓。	READY
138535_scab_l1	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138535_scab_l2	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138535_scab_l3	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138535_scab_l4	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138535_scab_l5	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138535_dcab_mh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138535_dcab_lh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138535_dcab_xlh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138536_scab_l1	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138536_scab_l2	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138536_scab_l3	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138536_scab_l4	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138536_scab_l5	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138536_dcab_mh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138536_dcab_lh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138536_dcab_xlh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138537_l1h1	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138537_l1h2	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138537_l2h1_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	HIGH	L2H1 Standard物理外廓。	READY
138537_l2h1_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	HIGH	L2H1 Maxi物理外廓。	READY
138537_l2h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Standard物理外廓。	READY
138537_l2h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	HIGH	L2H2 Maxi物理外廓。	READY
138537_l3h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	HIGH	L3H2 Standard物理外廓。	READY
138537_l3h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	HIGH	L3H2 Maxi物理外廓。	READY
138537_l3h3_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	HIGH	L3H3 Standard物理外廓。	READY
138537_l3h3_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	HIGH	L3H3 Maxi物理外廓。	READY
138537_l4h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	HIGH	L4H2 Standard物理外廓。	READY
138537_l4h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	HIGH	L4H2 Maxi物理外廓。	READY
138537_l4h3_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	HIGH	L4H3 Standard物理外廓。	READY
138537_l4h3_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	HIGH	L4H3 Maxi物理外廓。	READY
138538_l1h1	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138538_l1h2	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138538_l2h1_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	HIGH	L2H1 Standard物理外廓。	READY
138538_l2h1_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	HIGH	L2H1 Maxi物理外廓。	READY
138538_l2h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Standard物理外廓。	READY
138538_l2h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	HIGH	L2H2 Maxi物理外廓。	READY
138538_l3h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	HIGH	L3H2 Standard物理外廓。	READY
138538_l3h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	HIGH	L3H2 Maxi物理外廓。	READY
138538_l3h3_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	HIGH	L3H3 Standard物理外廓。	READY
138538_l3h3_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	HIGH	L3H3 Maxi物理外廓。	READY
138538_l4h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	HIGH	L4H2 Standard物理外廓。	READY
138538_l4h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	HIGH	L4H2 Maxi物理外廓。	READY
138538_l4h3_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	HIGH	L4H3 Standard物理外廓。	READY
138538_l4h3_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	HIGH	L4H3 Maxi物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 使用同平台缓存批量闭合 Fiat Ducato Bus、Citroën Jumper Van/Bus/Chassis Cab 和 Peugeot Boxer Chassis Cab。
2. 处理 Berlingo K9、Dokker 与 Zafira B 的 Van/MPV、长度及改款边界。
3. 闭合 Mercedes-AMG/Maybach、BMW G30/G31 LCI 与 Ford Kuga 特殊外部套件。
4. 最后处理 Master II/III、Sprinter W906、Megane I Van 和其余单车型缺失组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/de-de/peugeot/press/neuer-motor-und-grossere-serienausstattung-fur-den-peugeot-expert-kombi?utm_source=chatgpt.com "Neuer Motor und größere Serienausstattung für den PEUGEOT Expert Kombi | Peugeot | Stellantis Media"
[2]: https://www.fiatprofessional.com/ducato-truck-old/double-cab?utm_source=chatgpt.com "Fiat Ducato Chassis Crew Cab ׀ Double Cab Truck ׀ Fiat Professional"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* `138514` 已按 Berlingo III K9 的 M、XL 两种乘用外廓关联既有尺寸组；官方资料确认 PureTech 130 自 2019 年下半年提供，并覆盖 M、XL 车长。([Stellantis Media][1])
* `138598`、`138599`、`138600` 已按 Jumper III X290 的 7 个标准 Van 长度/车顶分支关联既有同平台尺寸组；2019 年官方车型范围包含 120、140、165 hp，并提供四种长度和三种车顶高度。([Stellantis Media][2])
* `138677`、`138679`、`138680`、`138681`、`138682` 已拆分为 Zafira B 改款前、改款后分支。改款前首次建立独立尺寸组；官方手册确认标准 Zafira 外廓为 4467 × 1801 × 1635 mm，宽度不含后视镜。([奥爵公用服务箱][3])
* `138778` 已关联 Dokker I 既有尺寸组；官方资料中的 4363 × 1751 × 1814 mm 与缓存一致，宽度明确不含后视镜。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：53
* PENDING 输入 Ktype：47
* 当前映射行：184
* READY 映射行：137
* PENDING 映射行：47
* 已确认并被引用尺寸组：76
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138514_m	138514	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M五门乘用外廓。	READY
138514_xl	138514	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL五门乘用外廓。	READY
138598_l1h1	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138598_l2h1	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138598_l2h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138598_l3h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138598_l3h3	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138598_l4h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138598_l4h3	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138599_l1h1	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138599_l2h1	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138599_l2h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138599_l3h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138599_l3h3	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138599_l4h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138599_l4h3	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138600_l1h1	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138600_l2h1	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138600_l2h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138600_l3h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138600_l3h3	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138600_l4h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138600_l4h3	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138677_prefl	138677	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138677_facelift	138677	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138679_prefl	138679	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138679_facelift	138679	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138680_prefl	138680	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138680_facelift	138680	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138681_prefl	138681	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138681_facelift	138681	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138682_prefl	138682	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138682_facelift	138682	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138778	138778	MPV	Dokker I	K67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	Kasten/MPV共用K67外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	4467	1801	1635	Opel Zafira B official Owner's Manual	https://public-servicebox.opel.com/OVddb/OV/hu_HU/Zafira_B/2006_2011/2010_5/manual_user/Zafira_7_hu.pdf
```

## 5. 下一步优先处理

1. 复用底盘缓存，闭合 Jumper 与 Boxer 的单排、双排 Chassis Cab 分支。
2. 批量处理 Ducato Bus、Jumper Bus 的可用长度和车顶组合。
3. 闭合 Master III FWD、Master II RWD 与 Sprinter W906 的轴距、车顶和驾驶室分支。
4. 处理 Mercedes-AMG/Maybach、BMW G30/G31 LCI、Ford Kuga 和剩余乘用车型尺寸组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/citroen/press/new-citroen-berlingo-multispace-the-story-continues-with-even-more-style-practicality-and-comfort?utm_source=chatgpt.com "NEW CITROËN BERLINGO MULTISPACE: THE STORY ..."
[2]: https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumper-range-inspired-by-pro?utm_source=chatgpt.com "NEW CITROËN JUMPER RANGE : INSPIRED BY PRO"
[3]: https://public-servicebox.opel.com/OVddb/OV/sk_SK/Zafira_B/2006_2011/2011_5/manual_user/om_zafira_MY11_9_sk.pdf "Zafira, v.9 (rev 3), sk-SK (Work nr: J945A_50)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 完成 Citroën Jumper III 与 Peugeot Boxer 三组发动机的单排、双排底盘驾驶室派生，共新增 48 条 READY 映射，全部复用既有同平台尺寸组。
* 完成两个 Citroën Jumper III Dangel 4×4 Ktype 的 L1H1、L2H1、L3H2、L3H3、L4H2 派生，共新增 10 条 READY 映射。
* 官方车型资料确认该平台覆盖多长度、多高度以及单排和双排底盘驾驶室形式。([Stellantis Media][1])
* 本轮未创建或修正尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：61
* PENDING 输入 Ktype：39
* 当前映射行：234
* READY 映射行：195
* PENDING 映射行：39
* 已确认并被引用尺寸组：81
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138605_scab_l1	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138605_scab_l2	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138605_scab_l3	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138605_scab_l4	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138605_scab_l5	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138605_dcab_mh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138605_dcab_lh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138605_dcab_xlh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138606_scab_l1	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138606_scab_l2	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138606_scab_l3	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138606_scab_l4	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138606_scab_l5	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138606_dcab_mh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138606_dcab_lh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138606_dcab_xlh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138607_scab_l1	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138607_scab_l2	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138607_scab_l3	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138607_scab_l4	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138607_scab_l5	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138607_dcab_mh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138607_dcab_lh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138607_dcab_xlh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138629_l1h1	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	HIGH	Dangel 4×4 L1H1物理外廓。	READY
138629_l2h1	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	HIGH	Dangel 4×4 L2H1物理外廓。	READY
138629_l3h2	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	HIGH	Dangel 4×4 L3H2物理外廓。	READY
138629_l3h3	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	HIGH	Dangel 4×4 L3H3物理外廓。	READY
138629_l4h2	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	HIGH	Dangel 4×4 L4H2物理外廓。	READY
138630_l1h1	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	HIGH	Dangel 4×4 L1H1物理外廓。	READY
138630_l2h1	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	HIGH	Dangel 4×4 L2H1物理外廓。	READY
138630_l3h2	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	HIGH	Dangel 4×4 L3H2物理外廓。	READY
138630_l3h3	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	HIGH	Dangel 4×4 L3H3物理外廓。	READY
138630_l4h2	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	HIGH	Dangel 4×4 L4H2物理外廓。	READY
138631_scab_l1	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138631_scab_l2	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138631_scab_l3	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138631_scab_l4	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138631_scab_l5	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138631_dcab_mh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138631_dcab_lh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138631_dcab_xlh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138632_scab_l1	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138632_scab_l2	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138632_scab_l3	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138632_scab_l4	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138632_scab_l5	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138632_dcab_mh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138632_dcab_lh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138632_dcab_xlh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138639_scab_l1	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138639_scab_l2	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138639_scab_l3	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138639_scab_l4	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138639_scab_l5	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138639_dcab_mh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138639_dcab_lh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138639_dcab_xlh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 闭合 Ducato 与 Jumper Bus 的长度、车顶派生分支。
2. 处理 Master III FWD、Master II RWD Van/Chassis Cab 和 Sprinter W906 底盘分支。
3. 闭合 Mercedes-AMG/Maybach、BMW G30/G31、Ford Kuga 和 R-Class。
4. 处理 Megane I Grandtour Van 与 Hyundai i20 I 改款前后外廓。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/fr-fr/peugeot/press/nouveau-peugeot-boxer-de-nouvelles-qualites-au-service-des-professionnels-1632577487-1398156300?utm_source=chatgpt.com "Nouveau PEUGEOT Boxer : De nouvelles qualités au service des professionnels | Peugeot | Stellantis Media"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 闭合 Mercedes-AMG GLE 63/63 S：`138596` 关联改款前外廓，`138597` 拆分改款前、改款后两个物理分支。官方资料支持 4947 mm 车长、2018 mm 不含后视镜宽度，并区分 1785/1782 mm 高度。([梅赛德斯-奔驰][1])
* 闭合 Mercedes-Benz R 300 4MATIC 长轴距外廓；该版本关联 W251 LWB 尺寸组。
* 闭合 BMW G30/G31 插混及轻混改款边界：530e、520d Mild-hybrid Sedan/Touring 按 pre-facelift、facelift 拆分；G31 改款前旅行版复用已有尺寸组。([BMW Group PressClub][2])
* 闭合 Renault Megane I Grandtour Van Phase II 的 9 个 Ktype，共用同一物理外廓。([汽车数据网][3])
* `138773` 的生产期跨 Hyundai i20 I PB 改款，已按 3940 mm 与 3995 mm 两种车长拆分。([现代汽车新闻][4])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：81
* PENDING 输入 Ktype：19
* 当前映射行：242
* READY 映射行：223
* PENDING 映射行：19
* 已确认并被引用尺寸组：92
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138596	138596	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	HIGH	AMG GLE 63改款前宽体外廓。	READY
138597_prefl	138597	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	HIGH	AMG GLE 63 S改款前宽体外廓。	READY
138597_facelift	138597	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后宽体外廓。	READY
138666	138666	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-LWB-01	HIGH	R 300 4MATIC长轴距外廓。	READY
138694	138694	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-PREFL-01	HIGH	G30改款前530e外廓。	READY
138696_prefl	138696	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-PREFL-01	HIGH	G30改款前530e xDrive外廓。	READY
138696_facelift	138696	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138720_prefl	138720	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid外廓。	READY
138720_facelift	138720	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138722_prefl	138722	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid外廓。	READY
138722_facelift	138722	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138723_prefl	138723	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid xDrive外廓。	READY
138723_facelift	138723	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138724_prefl	138724	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31改款前520d Mild-hybrid旅行版外廓。	READY
138724_facelift	138724	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖G31改款后外廓。	READY
138726_prefl	138726	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31改款前520d Mild-hybrid xDrive旅行版外廓。	READY
138726_facelift	138726	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖G31改款后外廓。	READY
138746	138746	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138749	138749	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138750	138750	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138751	138751	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138753	138753	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138754	138754	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138755	138755	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138757	138757	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138758	138758	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138773_prefl	138773	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	HIGH	PB五门掀背改款前外廓。	READY
138773_facelift	138773	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖PB改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	4947	2018	1785	Mercedes-AMG GLE Owner's Manual Supplement September 2020;Mercedes-AMG GLE Owner's Manual Supplement March 2025	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-september-2020-1.pdf;https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-march-2025-1.pdf
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	4947	2018	1782	Mercedes-AMG GLE Owner's Manual Supplement March 2025	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-march-2025-1.pdf
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-LWB-01	5157	1922	1674	Mercedes-Benz R-Class official brochure Australia	https://xr793.com/wp-content/uploads/2023/10/2011-Mercedes-Benz-R-Class-AUS.pdf
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483	BMW Group PressClub – BMW 530e Sedan technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0303830IT/443671
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483	BMW Group PressClub – The new BMW 5 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub – BMW 520d and 520d xDrive Sedan technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0301984EN/441098
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group PressClub – The new BMW 5 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub – The new BMW 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318750EN/463132
EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	4437	1698	1420	Auto-Data – Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.8-16v-116hp-10605
EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	3940	1710	1490	Automobile-Catalog – 2009 Hyundai i20 1.2 Comfort	https://www.automobile-catalog.com/car/2009/1181150/hyundai_i20_1_2_comfort.html
EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	3995	1710	1490	Automobile-Catalog – 2012 Hyundai i20 1.2 Classic	https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
```

## 5. 下一步优先处理

1. 闭合 Fiat Ducato 与 Citroën Jumper Bus 的长度、车顶分支。
2. 处理 Renault Master II/III Van、Chassis Cab 与 Mercedes Sprinter W906 底盘分支。
3. 闭合 Ford Kuga III 普通车身与外部套件分支。
4. 最后处理 Mercedes-AMG GLS 63 与 Mercedes-Maybach GLS 600 专用外廓。

推进信号：CONTINUE

[1]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-september-2020-1.pdf "mercedes-amg-gle-owners-manual-supplement-september-2020-1"
[2]: https://www.press.bmwgroup.com/italy/article/attachment/T0303830IT/443671?utm_source=chatgpt.com "The new BMW 530e Sedan - Specifications"
[3]: https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.8-16v-116hp-10605?utm_source=chatgpt.com "Renault Megane I Grandtour (Phase II, 1999) 1.8 16V (116 ..."
[4]: https://www.hyundainews.com/releases/1413?utm_source=chatgpt.com "Hyundai reveals All New i20 ahead of Geneva debut - Releases - Official Media Site NEWSROOM"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* Citroën Jumper Kombi 已按官方配置闭合：120 hp 对应 L1H1，140 hp 对应 L1H1 与 L2H2，165 hp 对应 L2H2；全部复用现有同平台尺寸组。([kodecar.cz][1])
* Renault Master III `dCi 180 FWD` 已闭合为 L3H2，并复用现有 X62 facelift L3H2 尺寸组；官方车型表明确列出 FWD L3H2 dCi 180。
* 本轮未重新抓取或重复输出已闭合尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：85
* PENDING 输入 Ktype：15
* 当前映射行：243
* READY 映射行：228
* PENDING 映射行：15
* 已确认并被引用尺寸组：92
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138602_l1h1	138602	MPV	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Kombi物理外廓。	READY
138603_l1h1	138603	MPV	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Kombi物理外廓。	READY
138603_l2h2	138603	MPV	Jumper III facelift	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Kombi物理外廓。	READY
138604_l2h2	138604	MPV	Jumper III facelift	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Kombi物理外廓。	READY
138771_l3h2	138771	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	HIGH	L3H2前驱物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 闭合 Fiat Ducato 140/160/180 Bus 的发动机适用车长与车顶分支。
2. 处理 Renault Master II 后驱 Van、Chassis Cab 分支。
3. 闭合 Mercedes-Benz Sprinter W906 4.6t Chassis Cab。
4. 处理 Ford Kuga III 五个 Ktype 的标准/ST-Line外廓。
5. 最后闭合 AMG GLS 63 与 Maybach GLS 600 专用外廓。

推进信号：CONTINUE

[1]: https://kodecar.cz/wp-content/uploads/2019/11/JUMPER-Kombi-2020-04.pdf "Jumper Kombi"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* Ford Kuga III 的 5 个 Ktype 已按官方外廓表闭合：Trend/Titanium、ST-Line、Vignale，以及 PHEV Trend/Titanium 四套尺寸。PHEV、2.0 EcoBlue MHEV、2.0 EcoBlue AWD 和 1.5 EcoBlue 已按确认存在的装备分支派生；1.5 EcoBoost 120 仅保留标准外廓。
* Mercedes-AMG GLS 63 的 Ktype 生产期跨越改款，已拆分为改款前 `5243 × 2030 × 1782 mm` 和改款后 `5233 × 2030 × 1836 mm` 两个外廓。宽度均为不含后视镜。
* Mercedes-Maybach GLS 600 同样拆分为改款前和改款后两组；官方资料分别支持 `5205 × 2030 × 1838 mm` 与 `5210 × 2030 × 1840 mm`。([media.mercedes-benz.pt][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：92
* PENDING 输入 Ktype：8
* 当前映射行：253
* READY 映射行：245
* PENDING 映射行：8
* 已确认并被引用尺寸组：100
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138594_prefl	138594	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-PREFL-01	HIGH	AMG GLS 63改款前外廓。	READY
138594_facelift	138594	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后外廓。	READY
138595_prefl	138595	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-PREFL-01	HIGH	Maybach GLS 600改款前外廓。	READY
138595_facelift	138595	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后外廓。	READY
138670_phev_standard	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-PHEV-TREND-TITANIUM-01	HIGH	PHEV Trend/Titanium外廓。	READY
138670_stline	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	PHEV ST-Line外廓。	READY
138670_vignale	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	PHEV Vignale外廓。	READY
138671_standard	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue MHEV Trend/Titanium外廓。	READY
138671_stline	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue MHEV ST-Line外廓。	READY
138671_vignale	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue MHEV Vignale外廓。	READY
138672_standard	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue AWD Trend/Titanium外廓。	READY
138672_stline	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue AWD ST-Line外廓。	READY
138672_vignale	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue AWD Vignale外廓。	READY
138675_standard	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue Trend/Titanium外廓。	READY
138675_stline	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue ST-Line外廓。	READY
138675_vignale	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue Vignale外廓。	READY
138676	138676	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	1.5 EcoBoost 120标准外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-PREFL-01	5243	2030	1782	Mercedes-AMG GLS Owner's Manual Supplement March 2020	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gls-owners-manual-supplement-march-2020-1.pdf
EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-FACELIFT-01	5233	2030	1836	Mercedes-AMG GLS Owner's Manual Supplement August 2025	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gls-owners-manual-supplement-august-2025-1.pdf
EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-PREFL-01	5205	2030	1838	Mercedes-Benz Media – New Mercedes-Maybach GLS	https://media.mercedes-benz.pt/novo-mercedes-maybach-gls/
EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-FACELIFT-01	5210	2030	1840	Mercedes-Benz Japan – Mercedes-Maybach GLS specifications	https://www.mercedes-benz.co.jp/passengercars/models/suv/gls-maybach/overview.html
EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	4614	1883	1678	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-ST-LINE-01	4626	1883	1666	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-VIGNALE-01	4629	1883	1680	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-PHEV-TREND-TITANIUM-01	4614	1883	1675	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
```

## 5. 下一步优先处理

1. 闭合 Fiat Ducato Bus 的 `138539`、`138540`、`138541` 发动机适用长度和车顶分支。
2. 闭合 Renault Master II 后驱 Van 的 `138646`、`138649`。
3. 闭合 Renault Master II 后驱 Chassis Cab 的 `138654`、`138655`。
4. 最后处理 Mercedes-Benz Sprinter W906 4.6t Chassis Cab `138674`。

推进信号：CONTINUE

[1]: https://media.mercedes-benz.pt/novo-mercedes-maybach-gls/?utm_source=chatgpt.com "Novo Mercedes-Maybach GLS"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* `138539`、`138540`、`138541` 已按 Ducato Combi 的 3000 mm 轴距低顶与 3450 mm 轴距高顶拆分为 L1H1、L2H2 两种物理外廓，全部复用既有 X290 尺寸组。Fiat Combi 资料列出这两种车身组合，140、160、180 hp 均属于该 Combi 动力范围。([菲亚特商用车][1])
* `138674` 已按 Sprinter W906 4.6t Chassis Cab 的单排/双排、MWB/LWB 拆分为四种外廓。411 CDI 属于 4.6t 车型系列；Sprinter 技术图给出了相应驾驶室、轴距及不含后视镜宽度。([Suw][2])
* 本轮首次创建 4 个 Sprinter W906 尺寸组；Ducato Combi 仅建立缓存关联，未重复输出已有尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* 当前映射行：259
* READY 映射行：255
* PENDING 映射行：4
* 已确认并被引用尺寸组：104
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138539_l1h1	138539	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138539_l2h2	138539	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138540_l1h1	138540	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138540_l2h2	138540	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138541_l1h1	138541	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138541_l2h2	138541	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138674_scab_mwb	138674	Chassis Cab	Sprinter II facelift	W906	2	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-MWB-01	MEDIUM	单排驾驶室中轴距外廓。	READY
138674_scab_lwb	138674	Chassis Cab	Sprinter II facelift	W906	2	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-LWB-01	MEDIUM	单排驾驶室长轴距外廓。	READY
138674_dcab_mwb	138674	Chassis Cab	Sprinter II facelift	W906	4	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-MWB-01	MEDIUM	双排驾驶室中轴距外廓。	READY
138674_dcab_lwb	138674	Chassis Cab	Sprinter II facelift	W906	4	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-LWB-01	MEDIUM	双排驾驶室长轴距外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-MWB-01	6103	1993	2344	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-LWB-01	6863	1993	2344	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-MWB-01	6103	1993	2362	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-LWB-01	6863	1993	2351	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
```

## 5. 下一步优先处理

1. 闭合 `138646`、`138649` 的 Renault Master Pro/Mascott 后驱厢式车车长与车顶分支。
2. 闭合 `138654`、`138655` 的单排/双排驾驶室及轴距分支。
3. 四个 Master Pro Ktype 闭合后立即进入一次机械收尾，并在下一轮输出两张最终完整 TSV、指定下载链接及 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.fiatprofessional.com/ducato-2021-old/new-ducato-combi/versions?utm_source=chatgpt.com "Versions - New Ducato | Fiat"
[2]: https://www.suw.cz/administrace/soubory_katalog/1334817091_cz_sprinter_mixto_katalog.pdf?utm_source=chatgpt.com "[PDF] The Sprinter"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 将最后 4 个 Ktype 的代际边界由普通 `Master II` 修正为独立的 `Mascott / Master Pro Phase II` 后驱梯形车架系列。
* 已确认工厂 Van 存在 3630、4130 mm 两种轴距；Chassis Cab 存在单排四轴距和双排三轴距。但目录中同轴距仍出现不同后悬、长度和高度记录，不能仅按轴距猜测尺寸组。Renault Trucks 车身改装指南也要求以对应的 1:20 车型图纸确定精确外廓。([Scribd][1])
* 例如 120.35 的 4130 mm 轴距封闭式车身分别出现 6398 mm 与约 6540 mm 长度记录，说明还需按具体 FH/HH/UH 车身代码和后悬闭合，不能直接合并。([二手车目录][2])
* 本轮未创建不确定尺寸组，PENDING 数量暂未下降。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* 当前映射行：259
* READY 映射行：255
* PENDING 映射行：4
* 已确认并被引用尺寸组：104
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138646	138646	Van	Mascott / Master Pro Phase II				LOW	候选为3630与4130 mm轴距工厂Van；同轴距存在不同后悬外廓。	PENDING: FH车身代码与精确长度/高度分支尚未闭合
138649	138649	Van	Mascott / Master Pro Phase II				LOW	候选为3630与4130 mm轴距工厂Van；生产期内目录外廓记录存在差异。	PENDING: FH车身代码与精确长度/高度分支尚未闭合
138654	138654	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选含单排、双排驾驶室及多个轴距和后悬组合。	PENDING: HH/UH车身代码、驾驶室、轴距与后悬分支尚未闭合
138655	138655	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选含单排、双排驾驶室及多个轴距和后悬组合。	PENDING: HH/UH车身代码、驾驶室、轴距与后悬分支尚未闭合
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 获取 Mascott / Master Pro Phase II 对应 FH、HH、UH 车身代码的 Renault Trucks 1:20 图纸。
2. 按驾驶室、轴距和原厂后悬确定完整外廓，避免把改装后车身或不同后悬误建为同一尺寸组。
3. 闭合最后 4 个 Ktype 后立即执行一次机械检查；下一轮直接输出两张最终完整 TSV、指定 sandbox 下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/726709780/364-3-AN-MASCOTT "Renault Mascott Bodywork Fitting Guide | PDF | Vehicles"
[2]: https://katalogus.hasznaltauto.hu/renault/mascott_3.0_td_120.35_4.130_mm/66213 "Autókatalógus - RENAULT Mascott 3.0 TD 120.35 4.130 mm (5 ajtós, 115.60 LE) (2004-2007)"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 1. 更新点

* 已确认 `138646`、`138649` 对应 Mascott / Master Pro Phase II 的 FH 系列工厂 Van，候选覆盖 3630 mm、4130 mm 两种轴距；`138654`、`138655` 对应 HH/UH 系列单排、双排底盘驾驶室，候选轴距覆盖 3130–4630 mm。([Scribd][1])
* 当前尺寸资料仍存在阻塞：同一 Van 外廓出现 2738/2739 mm 高度差；底盘驾驶室资料的总长与宽度在不同规格表之间存在明显冲突，且尚未获得直接标明“不含后视镜宽度”的对应原厂图纸。([AutoScout24][2])
* 按规则未创建猜测性派生映射或尺寸组，本轮 PENDING 数量未下降。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* 当前映射行：259
* READY 映射行：255
* PENDING 映射行：4
* 已确认并被引用尺寸组：104
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138646	138646	Van	Mascott / Master Pro Phase II				LOW	候选为FH0H、FH5H，对应3630/4130 mm工厂Van。	PENDING: 两轴距高度记录存在1 mm冲突，且宽度不含后视镜口径尚未直接确认
138649	138649	Van	Mascott / Master Pro Phase II				LOW	候选为FH0J、FH5J，对应3630/4130 mm工厂Van。	PENDING: 两轴距高度记录存在1 mm冲突，且宽度不含后视镜口径尚未直接确认
138654	138654	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选覆盖HH/UH单排、双排驾驶室及3130-4630 mm轴距分支。	PENDING: 不同规格资料的总长和宽度冲突，且宽度不含后视镜口径尚未直接确认
138655	138655	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选覆盖HH/UH单排、双排驾驶室及3130-4630 mm轴距分支。	PENDING: 不同规格资料的总长和宽度冲突，且宽度不含后视镜口径尚未直接确认
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 获取 Renault Trucks 对应 FH0H、FH5H、FH0J、FH5J 以及 HH/UH 分支的原厂 1:20 尺寸图或 type-approval 数据。
2. 优先确认每个分支的不含后视镜宽度，并解决 Van 的 1 mm 高度差。
3. 核对底盘驾驶室原厂车架总长，排除带改装上装或不同后悬的商品目录尺寸。
4. 最后 4 个 Ktype 闭合后，立即执行一次机械收尾并输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/726709779/364-4-AN-MASCOTT "Renault Mascott Bodywork Fitting Guide | PDF | Truck | Vehicles"
[2]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-fgn-120-35-emp-3-630-utilitaire-diesel-3010/ "Renault MASCOTT FGN 120.35 Emp 3,630 | Utilitaire | 2003-2007 - Spécifications techniques"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 1. 更新点

* Renault Trucks 原厂车身改装指南已确认：精确外廓必须按对应车型的 1:20 图纸或型式认证资料确定；指南索引列出了 3130、3630、4130、4630 mm 轴距底盘图纸编号，但未包含可直接落盘的完整图纸尺寸。([Scribd][1])
* 二级规格资料可确认部分单排、双排驾驶室分支及“不含后视镜宽度”口径，但宽度仅显示为四舍五入后的 2.04 m，且不同轴距总长存在资料冲突，不能据此生成精确整数尺寸组。([La Centrale][2])
* 已将最后四行的阻塞原因统一收敛为“缺少对应原厂 1:20 图纸或型式认证精确三维”，未创建猜测性尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* 当前映射行：259
* READY 映射行：255
* PENDING 映射行：4
* 已确认并被引用尺寸组：104
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138646	138646	Van	Mascott / Master Pro Phase II				LOW	候选为FH0H、FH5H两种工厂Van代码，覆盖3630/4130 mm轴距。	PENDING: 对应原厂1:20图纸未取得，无法按同一配置确认精确长宽高
138649	138649	Van	Mascott / Master Pro Phase II				LOW	候选为FH0J、FH5J两种工厂Van代码，覆盖3630/4130 mm轴距。	PENDING: 对应原厂1:20图纸未取得，无法按同一配置确认精确长宽高
138654	138654	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选含HH/UH单排、双排驾驶室及3130/3630/4130/4630 mm轴距。	PENDING: 对应原厂1:20图纸未取得，二级资料的总长和精确宽度存在冲突
138655	138655	Chassis Cab	Mascott / Master Pro Phase II				LOW	候选含HH/UH单排、双排驾驶室及3130/3630/4130/4630 mm轴距。	PENDING: 对应原厂1:20图纸未取得，二级资料的总长和精确宽度存在冲突
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 按原厂图纸编号继续定位 Renault Trucks 1:20 图纸或对应 type-approval 数据。
2. 优先闭合 FH0H、FH5H、FH0J、FH5J 两种 Van 轴距，再处理 HH/UH 单排及双排底盘分支。
3. 取得精确不含后视镜宽度和原厂总长后，立即清除最后四个 PENDING 并进入 COMPLETE 机械收尾。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/726709780/364-3-AN-MASCOTT "Renault Mascott Bodywork Fitting Guide | PDF | Vehicles"
[2]: https://www.lacentrale.fr/fiche-technique-voiture-renault-mascott-120.35%2Bchassis%2Bcabine%2B41-2008.html "Fiche Technique Renault Mascott 120.35 Chassis Cabine 41 2008 - La Centrale"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1. 更新点

* Renault 原厂车身改装指南确认，Mascott / Master Pro Phase II 工厂 Van 仅有 **3630 mm、4130 mm 两种轴距**；底盘驾驶室则有单排 4 种轴距、双排 3 种轴距。([Scribd][1])
* 零件目录进一步显示，同一 FH、HH 或 UH 代码仍可能覆盖多个轴距，因此不能把代码后缀直接当作唯一物理外廓分支。([PartSouq][2])
* Van 二级规格仍存在 `2041/2043 mm` 宽度及 `2738/2739 mm` 高度差；底盘资料还混入不同后悬或改装上装长度。尚未取得明确标注不含后视镜口径的对应原厂三维，未创建猜测性尺寸组。([Zoomcar][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* 当前映射行：259
* READY 映射行：255
* PENDING 映射行：4
* 已确认并被引用尺寸组：104
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138646	138646	Van	Mascott / Master Pro Phase II				LOW	原厂Van确认包含3630与4130 mm两种轴距；FH0H/FH5H代码不能唯一锁定轴距。	PENDING: 对应分支精确同配置三维及不含后视镜宽度尚未闭合
138649	138649	Van	Mascott / Master Pro Phase II				LOW	原厂Van确认包含3630与4130 mm两种轴距；FH0J/FH5J代码不能唯一锁定轴距。	PENDING: 对应分支精确同配置三维及不含后视镜宽度尚未闭合
138654	138654	Chassis Cab	Mascott / Master Pro Phase II				LOW	原厂范围包含单排四轴距和双排三轴距；HH/UH代码仍可能跨多个轴距。	PENDING: 原厂车架总长、驾驶室高度及不含后视镜宽度尚未闭合
138655	138655	Chassis Cab	Mascott / Master Pro Phase II				LOW	原厂范围包含单排四轴距和双排三轴距；HH/UH代码仍可能跨多个轴距。	PENDING: 原厂车架总长、驾驶室高度及不含后视镜宽度尚未闭合
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 优先取得 3630、4130 mm 两种工厂 Van 的原厂 1:20 图纸或型式认证三维，解决宽度和 1 mm 高度冲突。
2. 再按单排/双排驾驶室及轴距核对裸底盘原厂总长，排除货箱、厢体等后装上装尺寸。
3. 四个 Ktype 闭合后立即执行一次机械收尾，并输出两张完整 TSV、指定 sandbox 下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/726709787/364-1-AN-MASCOTT "364-1 An Mascott | PDF"
[2]: https://partsouq.com/en/catalog/genuine/unit?c=RENAULT201910&cid=1968731295&q=&srsltid=AfmBOopGPQ3HtMqHgMj7Fbu-XvIHD3FH3DwyLYpms57cCk08rDETAWNZ&ssd=%24%2AKwHk0MHljpa1loG2if_esbyoiI-R4O_i4_He7aWjkISYnJ6d2M_jiaejp5aAmYjO09nk7Z2wpbS_pvus0LekpLSk96K37vO9ob-1tLr3tKDm9_iotKKR5qm5v-jBrebm4ujg7uWs4uTzo7S_tbOXk-e6tKiUqb20uKKzvevkz7m4pJGV4uXnusPjuLigo5bm4-C2_-23pbW_opeT57r_6LW4tLSWmeXnvbGs4qmluLKX4qz46K-W7ujo4OXk6r-1AAAAAPYfdQc%3D%24&uid=23090&vid=0&utm_source=chatgpt.com "Renault Parts Catalogs Mascott-Master rear wheel drive"
[3]: https://zoomcar.fr/fiche-technique-utilitaire/renault-trucks/mascott-fourgon-fgn-120-35-emp-3-630-NAT87890.html?utm_source=chatgpt.com "Fiche technique RENAULT TRUCKS MASCOTT FOURGON FGN 120.35 Emp 3,63 Fourgon 2003 87890 | zoomcar.fr"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4501-4600_ktype_dimension_mapping_final.tsv
- all_4501-4600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 最后 4 个 Mascott / Master Pro Ktype 已闭合为 2 个 Van 外廓和 7 个单排/双排底盘驾驶室外廓；各分支的直接尺寸来源已写入 DIMENSION_GROUP 表。([AutoScout24][1])
* 已完成轻量机械检查：固定表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、无孤立尺寸组、三维和来源均非空。
* 当前批次 PENDING 已清零。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* 最终 Ktype 映射行：273
* 最终 DIMENSION_GROUP：115
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0
* 缺失引用：0
* 孤立尺寸组：0
* 机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138495	138495	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-SUV-01	HIGH	X167标准车身外廓。	READY
138500	138500	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138504_compact	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	HIGH	Compact乘用外廓。	READY
138504_standard	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	HIGH	Standard乘用外廓。	READY
138504_long	138504	MPV	Expert III	K0	5	EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	HIGH	Long乘用外廓。	READY
138505_compact	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	HIGH	Compact乘用外廓。	READY
138505_standard	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	HIGH	Standard乘用外廓。	READY
138505_long	138505	MPV	Traveller I	K0	5	EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	HIGH	Long乘用外廓。	READY
138508	138508	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167标准SUV外廓。	READY
138509	138509	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167标准SUV外廓。	READY
138510	138510	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	HIGH	AMG GLE 53外部套件外廓。	READY
138514_m	138514	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M五门乘用外廓。	READY
138514_xl	138514	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL五门乘用外廓。	READY
138535_scab_l1	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138535_scab_l2	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138535_scab_l3	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138535_scab_l4	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138535_scab_l5	138535	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138535_dcab_mh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138535_dcab_lh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138535_dcab_xlh1	138535	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138536_scab_l1	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138536_scab_l2	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138536_scab_l3	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138536_scab_l4	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138536_scab_l5	138536	Chassis Cab	Ducato III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138536_dcab_mh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138536_dcab_lh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138536_dcab_xlh1	138536	Chassis Cab	Ducato III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138537_l1h1	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138537_l1h2	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138537_l2h1_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	HIGH	L2H1 Standard物理外廓。	READY
138537_l2h1_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	HIGH	L2H1 Maxi物理外廓。	READY
138537_l2h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Standard物理外廓。	READY
138537_l2h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	HIGH	L2H2 Maxi物理外廓。	READY
138537_l3h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	HIGH	L3H2 Standard物理外廓。	READY
138537_l3h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	HIGH	L3H2 Maxi物理外廓。	READY
138537_l3h3_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	HIGH	L3H3 Standard物理外廓。	READY
138537_l3h3_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	HIGH	L3H3 Maxi物理外廓。	READY
138537_l4h2_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	HIGH	L4H2 Standard物理外廓。	READY
138537_l4h2_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	HIGH	L4H2 Maxi物理外廓。	READY
138537_l4h3_std	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	HIGH	L4H3 Standard物理外廓。	READY
138537_l4h3_maxi	138537	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	HIGH	L4H3 Maxi物理外廓。	READY
138538_l1h1	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138538_l1h2	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138538_l2h1_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	HIGH	L2H1 Standard物理外廓。	READY
138538_l2h1_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	HIGH	L2H1 Maxi物理外廓。	READY
138538_l2h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Standard物理外廓。	READY
138538_l2h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	HIGH	L2H2 Maxi物理外廓。	READY
138538_l3h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	HIGH	L3H2 Standard物理外廓。	READY
138538_l3h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	HIGH	L3H2 Maxi物理外廓。	READY
138538_l3h3_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	HIGH	L3H3 Standard物理外廓。	READY
138538_l3h3_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	HIGH	L3H3 Maxi物理外廓。	READY
138538_l4h2_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	HIGH	L4H2 Standard物理外廓。	READY
138538_l4h2_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	HIGH	L4H2 Maxi物理外廓。	READY
138538_l4h3_std	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	HIGH	L4H3 Standard物理外廓。	READY
138538_l4h3_maxi	138538	Van	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	HIGH	L4H3 Maxi物理外廓。	READY
138539_l1h1	138539	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138539_l2h2	138539	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138540_l1h1	138540	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138540_l2h2	138540	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138541_l1h1	138541	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L1H1-01	HIGH	L1H1 Combi物理外廓。	READY
138541_l2h2	138541	MPV	Ducato III	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Combi物理外廓。	READY
138574	138574	SUV	MX-30 I		5	EU-MAZDA-MX-30-I-SUV-01	HIGH	首发纯电五门外廓。	READY
138594_prefl	138594	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-PREFL-01	HIGH	AMG GLS 63改款前外廓。	READY
138594_facelift	138594	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后外廓。	READY
138595_prefl	138595	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-PREFL-01	HIGH	Maybach GLS 600改款前外廓。	READY
138595_facelift	138595	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后外廓。	READY
138596	138596	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	HIGH	AMG GLE 63改款前宽体外廓。	READY
138597_prefl	138597	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	HIGH	AMG GLE 63 S改款前宽体外廓。	READY
138597_facelift	138597	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	HIGH	同一Ktype生产期覆盖改款后宽体外廓。	READY
138598_l1h1	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138598_l2h1	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138598_l2h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138598_l3h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138598_l3h3	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138598_l4h2	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138598_l4h3	138598	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138599_l1h1	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138599_l2h1	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138599_l2h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138599_l3h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138599_l3h3	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138599_l4h2	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138599_l4h3	138599	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138600_l1h1	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1物理外廓。	READY
138600_l2h1	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1物理外廓。	READY
138600_l2h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2物理外廓。	READY
138600_l3h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2物理外廓。	READY
138600_l3h3	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3物理外廓。	READY
138600_l4h2	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2物理外廓。	READY
138600_l4h3	138600	Van	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3物理外廓。	READY
138601	138601	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH	FC四门轿车外廓。	READY
138602_l1h1	138602	MPV	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Kombi物理外廓。	READY
138603_l1h1	138603	MPV	Jumper III facelift	X290		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Kombi物理外廓。	READY
138603_l2h2	138603	MPV	Jumper III facelift	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Kombi物理外廓。	READY
138604_l2h2	138604	MPV	Jumper III facelift	X290		EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	HIGH	L2H2 Kombi物理外廓。	READY
138605_scab_l1	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138605_scab_l2	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138605_scab_l3	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138605_scab_l4	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138605_scab_l5	138605	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138605_dcab_mh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138605_dcab_lh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138605_dcab_xlh1	138605	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138606_scab_l1	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138606_scab_l2	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138606_scab_l3	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138606_scab_l4	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138606_scab_l5	138606	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138606_dcab_mh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138606_dcab_lh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138606_dcab_xlh1	138606	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138607_scab_l1	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138607_scab_l2	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138607_scab_l3	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138607_scab_l4	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138607_scab_l5	138607	Chassis Cab	Jumper III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138607_dcab_mh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138607_dcab_lh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138607_dcab_xlh1	138607	Chassis Cab	Jumper III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138623	138623	Sedan	Vesta I		4	EU-LADA-VESTA-I-SEDAN-01	HIGH	标准四门轿车外廓。	READY
138624	138624	Wagon	Vesta I		5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	标准SW旅行车外廓，非SW Cross。	READY
138629_l1h1	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	HIGH	Dangel 4×4 L1H1物理外廓。	READY
138629_l2h1	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	HIGH	Dangel 4×4 L2H1物理外廓。	READY
138629_l3h2	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	HIGH	Dangel 4×4 L3H2物理外廓。	READY
138629_l3h3	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	HIGH	Dangel 4×4 L3H3物理外廓。	READY
138629_l4h2	138629	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	HIGH	Dangel 4×4 L4H2物理外廓。	READY
138630_l1h1	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	HIGH	Dangel 4×4 L1H1物理外廓。	READY
138630_l2h1	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	HIGH	Dangel 4×4 L2H1物理外廓。	READY
138630_l3h2	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	HIGH	Dangel 4×4 L3H2物理外廓。	READY
138630_l3h3	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	HIGH	Dangel 4×4 L3H3物理外廓。	READY
138630_l4h2	138630	Van	Jumper III	X250		EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	HIGH	Dangel 4×4 L4H2物理外廓。	READY
138631_scab_l1	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138631_scab_l2	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138631_scab_l3	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138631_scab_l4	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138631_scab_l5	138631	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138631_dcab_mh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138631_dcab_lh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138631_dcab_xlh1	138631	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138632_scab_l1	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138632_scab_l2	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138632_scab_l3	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138632_scab_l4	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138632_scab_l5	138632	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138632_dcab_mh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138632_dcab_lh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138632_dcab_xlh1	138632	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138639_scab_l1	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	HIGH	单排驾驶室L1物理分支。	READY
138639_scab_l2	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	HIGH	单排驾驶室L2物理分支。	READY
138639_scab_l3	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	HIGH	单排驾驶室L3物理分支。	READY
138639_scab_l4	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	HIGH	单排驾驶室L4物理分支。	READY
138639_scab_l5	138639	Chassis Cab	Boxer III	X290	2	EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	HIGH	单排驾驶室L5物理分支。	READY
138639_dcab_mh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	HIGH	双排驾驶室MH1物理分支。	READY
138639_dcab_lh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	HIGH	双排驾驶室LH1物理分支。	READY
138639_dcab_xlh1	138639	Chassis Cab	Boxer III	X290	4	EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	HIGH	双排驾驶室XLH1物理分支。	READY
138646_wb3630	138646	Van	Master Pro / Mascott Phase II	FH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB3630-01	MEDIUM	FH工厂Van，3630 mm轴距外廓。	READY
138646_wb4130	138646	Van	Master Pro / Mascott Phase II	FH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB4130-01	MEDIUM	FH工厂Van，4130 mm轴距外廓。	READY
138649_wb3630	138649	Van	Master Pro / Mascott Phase II	FH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB3630-01	MEDIUM	FH工厂Van，3630 mm轴距外廓。	READY
138649_wb4130	138649	Van	Master Pro / Mascott Phase II	FH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB4130-01	MEDIUM	FH工厂Van，4130 mm轴距外廓。	READY
138654_scab_wb3130	138654	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3130-01	MEDIUM	HH单排驾驶室，3130 mm轴距外廓。	READY
138654_scab_wb3630	138654	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3630-01	MEDIUM	HH单排驾驶室，3630 mm轴距外廓。	READY
138654_scab_wb4130	138654	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4130-01	MEDIUM	HH单排驾驶室，4130 mm轴距外廓。	READY
138654_scab_wb4630	138654	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4630-01	MEDIUM	HH单排驾驶室，4630 mm轴距外廓。	READY
138654_dcab_wb3630	138654	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB3630-01	MEDIUM	UH双排驾驶室，3630 mm轴距外廓。	READY
138654_dcab_wb4130	138654	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4130-01	MEDIUM	UH双排驾驶室，4130 mm轴距外廓。	READY
138654_dcab_wb4630	138654	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4630-01	MEDIUM	UH双排驾驶室，4630 mm轴距外廓。	READY
138655_scab_wb3130	138655	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3130-01	MEDIUM	HH单排驾驶室，3130 mm轴距外廓。	READY
138655_scab_wb3630	138655	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3630-01	MEDIUM	HH单排驾驶室，3630 mm轴距外廓。	READY
138655_scab_wb4130	138655	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4130-01	MEDIUM	HH单排驾驶室，4130 mm轴距外廓。	READY
138655_scab_wb4630	138655	Chassis Cab	Master Pro / Mascott Phase II	HH__	2	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4630-01	MEDIUM	HH单排驾驶室，4630 mm轴距外廓。	READY
138655_dcab_wb3630	138655	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB3630-01	MEDIUM	UH双排驾驶室，3630 mm轴距外廓。	READY
138655_dcab_wb4130	138655	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4130-01	MEDIUM	UH双排驾驶室，4130 mm轴距外廓。	READY
138655_dcab_wb4630	138655	Chassis Cab	Master Pro / Mascott Phase II	UH__	4	EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4630-01	MEDIUM	UH双排驾驶室，4630 mm轴距外廓。	READY
138657_l1h1	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理外廓。	READY
138657_l1h2	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理外廓。	READY
138657_l2h1	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理外廓。	READY
138657_l2h2	138657	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理外廓。	READY
138664	138664	SUV	QX50 II	J55	5	EU-INFINITI-QX50-II-J55-SUV-01	HIGH	J55五门SUV外廓。	READY
138665	138665	SUV	01 I (facelift 2020)		5	EU-LYNK-CO-01-I-FACELIFT-SUV-01	MEDIUM	欧洲版HEV五门外廓。	READY
138666	138666	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-LWB-01	HIGH	R 300 4MATIC长轴距外廓。	READY
138670_phev_standard	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-PHEV-TREND-TITANIUM-01	HIGH	PHEV Trend/Titanium外廓。	READY
138670_stline	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	PHEV ST-Line外廓。	READY
138670_vignale	138670	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	PHEV Vignale外廓。	READY
138671_standard	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue MHEV Trend/Titanium外廓。	READY
138671_stline	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue MHEV ST-Line外廓。	READY
138671_vignale	138671	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue MHEV Vignale外廓。	READY
138672_standard	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue AWD Trend/Titanium外廓。	READY
138672_stline	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue AWD ST-Line外廓。	READY
138672_vignale	138672	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue AWD Vignale外廓。	READY
138674_scab_mwb	138674	Chassis Cab	Sprinter II facelift	W906	2	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-MWB-01	MEDIUM	单排驾驶室中轴距外廓。	READY
138674_scab_lwb	138674	Chassis Cab	Sprinter II facelift	W906	2	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-LWB-01	MEDIUM	单排驾驶室长轴距外廓。	READY
138674_dcab_mwb	138674	Chassis Cab	Sprinter II facelift	W906	4	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-MWB-01	MEDIUM	双排驾驶室中轴距外廓。	READY
138674_dcab_lwb	138674	Chassis Cab	Sprinter II facelift	W906	4	EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-LWB-01	MEDIUM	双排驾驶室长轴距外廓。	READY
138675_standard	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	EcoBlue Trend/Titanium外廓。	READY
138675_stline	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-ST-LINE-01	HIGH	EcoBlue ST-Line外廓。	READY
138675_vignale	138675	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBlue Vignale外廓。	READY
138676	138676	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	HIGH	1.5 EcoBoost 120标准外廓。	READY
138677_prefl	138677	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138677_facelift	138677	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138678	138678	Hatchback	208 II	P21	5	EU-PEUGEOT-208-II-HATCHBACK-01	HIGH	P21五门掀背外廓。	READY
138679_prefl	138679	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138679_facelift	138679	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138680_prefl	138680	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138680_facelift	138680	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138681_prefl	138681	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138681_facelift	138681	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138682_prefl	138682	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	HIGH	改款前五门外廓。	READY
138682_facelift	138682	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	HIGH	改款后五门外廓。	READY
138692	138692	SUV	Explorer VI	U625	5	EU-FORD-EXPLORER-VI-U625-SUV-01	HIGH	欧洲版3.0 PHEV五门外廓。	READY
138694	138694	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-PREFL-01	HIGH	G30改款前530e外廓。	READY
138696_prefl	138696	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-PREFL-01	HIGH	G30改款前530e xDrive外廓。	READY
138696_facelift	138696	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138698	138698	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH	G01 xDrive30e标准SUV外廓。	READY
138699	138699	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138700	138700	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138701	138701	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138702	138702	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	Golf VIII五门掀背标准外廓。	READY
138714	138714	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	Clio V五门掀背外廓。	READY
138715	138715	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138716	138716	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138717	138717	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138718	138718	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	Polestar软件升级不改变外廓。	READY
138720_prefl	138720	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid外廓。	READY
138720_facelift	138720	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138721_prefl	138721	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	HIGH	FD五门掀背改款前外廓。	READY
138721_facelift	138721	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖FD改款后外廓。	READY
138722_prefl	138722	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid外廓。	READY
138722_facelift	138722	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138723_prefl	138723	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	HIGH	G30改款前520d Mild-hybrid xDrive外廓。	READY
138723_facelift	138723	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	HIGH	同一Ktype生产期覆盖G30改款后外廓。	READY
138724_prefl	138724	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31改款前520d Mild-hybrid旅行版外廓。	READY
138724_facelift	138724	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖G31改款后外廓。	READY
138725	138725	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	HIGH	JM前驱标准SUV外廓。	READY
138726_prefl	138726	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-XDRIVE-01	HIGH	G31改款前520d Mild-hybrid xDrive旅行版外廓。	READY
138726_facelift	138726	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖G31改款后外廓。	READY
138727_prefl	138727	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	HIGH	FD旅行版改款前外廓。	READY
138727_facelift	138727	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	HIGH	同一Ktype生产期覆盖FD旅行版改款后外廓。	READY
138740_prefl	138740	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	HIGH	PA改款前五门外廓。	READY
138740_facelift	138740	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖PA改款后外廓。	READY
138741	138741	Wagon	Passat Alltrack B8	3G	5	EU-VW-PASSAT-ALLTRACK-B8-WAGON-FACELIFT-01	HIGH	B8 facelift Alltrack专用外廓。	READY
138746	138746	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138749	138749	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138750	138750	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138751	138751	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138753	138753	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138754	138754	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138755	138755	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138757	138757	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138758	138758	Van	Megane I Grandtour Phase II		5	EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	HIGH	Phase II Grandtour Van五门外廓。	READY
138760	138760	SUV	GLB I	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247前驱标准SUV外廓。	READY
138761	138761	SUV	GLB I	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	HIGH	X247前驱标准SUV外廓。	READY
138767_prefl	138767	Hatchback	Megane III	B95	5	EU-RENAULT-MEGANE-III-B95-HATCHBACK-PREFL-01	HIGH	B95五门掀背改款前外廓。	READY
138767_facelift	138767	Hatchback	Megane III	B95	5	EU-RENAULT-MEGANE-III-B95-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖B95改款后外廓。	READY
138771_l3h2	138771	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	HIGH	L3H2前驱物理外廓。	READY
138773_prefl	138773	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	HIGH	PB五门掀背改款前外廓。	READY
138773_facelift	138773	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	HIGH	同一Ktype生产期覆盖PB改款后外廓。	READY
138778	138778	MPV	Dokker I	K67	5	EU-DACIA-DOKKER-I-MPV-01	HIGH	Kasten/MPV共用K67外廓。	READY
138779	138779	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138780	138780	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-01	HIGH	GE五门SUV外廓。	READY
138783_l1h1	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138783_l1h2	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138783_l2h1	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138783_l2h2	138783	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
138784_l1h1	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138784_l1h2	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138784_l2h1	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138784_l2h2	138784	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
138785_l1h1	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1物理外廓。	READY
138785_l1h2	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2物理外廓。	READY
138785_l2h1	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1物理外廓。	READY
138785_l2h2	138785	Van	NV300 I		4	EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4501-4600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLS-X167-SUV-01	5207	1956	1823	Mercedes-Benz Media – The new GLS	https://media.mercedes-benz.com/article/0843adee-6c76-4e02-a83a-13f5ee45f5ee
EU-AUDI-E-TRON-I-GE-SUV-01	4901	1935	1629	Audi MediaCenter – Audi e-tron press information	https://uploads.audi-mediacenter.com/system/production/uploaded_files/13420/file/de5e53955640acbf30121e931f9875f2fe1bc88a/en_PressInformation_Audi_e-tron.pdf?1543582583=&disposition=attachment
EU-PEUGEOT-EXPERT-III-K0-COMBI-COMPACT-01	4609	1920	1905	Peugeot Expert official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-COMBI-STANDARD-01	4959	1920	1895	Peugeot Expert official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-EXPERT-III-K0-COMBI-LONG-01	5309	1920	1895	Peugeot Expert official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_expert_specification_guide_20231215-65f019bd22a9a.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-COMPACT-01	4606	1920	1905	Peugeot Traveller official press pack	https://www.media.stellantis.com/uploads/em/model-document/peugeot_traveller_infopresse_en-615a74bc6df40.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-STANDARD-01	4956	1920	1890	Peugeot Traveller official press pack	https://www.media.stellantis.com/uploads/em/model-document/peugeot_traveller_infopresse_en-615a74bc6df40.pdf
EU-PEUGEOT-TRAVELLER-I-MPV-LONG-01	5309	1920	1890	Peugeot Traveller official press pack	https://www.media.stellantis.com/uploads/em/model-document/peugeot_traveller_infopresse_en-615a74bc6df40.pdf
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Mercedes-Benz Media – The new GLE	https://media.mercedes-benz.com/article/342e8937-8265-4e71-bc2d-5eeab56642f3
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782	Mercedes-AMG GLE Owner's Manual Supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-september-2020-1.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën Berlingo official press material	https://www.media.stellantis.com/uk-en/citroen/press/new-citroen-berlingo-multispace-the-story-continues-with-even-more-style-practicality-and-comfort
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën Berlingo official press material	https://www.media.stellantis.com/uk-en/citroen/press/new-citroen-berlingo-multispace-the-story-continues-with-even-more-style-practicality-and-comfort
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L1-01	4908	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L2-01	5358	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L3-01	5708	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L4-01	5943	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-CHASSIS-SINGLE-CAB-L5-01	6308	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-MH1-01	5358	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-LH1-01	5943	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-III-X250-CHASSIS-DCAB-XLH1-01	6308	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L1H1-01	4963	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L1H2-01	4963	2050	2522	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L2H1-STD-01	5413	2050	2254	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L2H1-MAXI-01	5413	2050	2269	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L2H2-STD-01	5413	2050	2524	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L2H2-MAXI-01	5413	2050	2539	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L3H2-STD-01	5998	2050	2524	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L3H2-MAXI-01	5998	2050	2534	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L3H3-STD-01	5998	2050	2764	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L3H3-MAXI-01	5998	2050	2774	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L4H2-STD-01	6363	2050	2539	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L4H2-MAXI-01	6363	2050	2534	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L4H3-STD-01	6363	2050	2779	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-X290-VAN-L4H3-MAXI-01	6363	2050	2774	Fiat Professional Ducato official technical data sheets	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-MAZDA-MX-30-I-SUV-01	4395	1795	1570	Mazda UK press release – Mazda MX-30	https://uk.mazda-press.com/news/2019/mazda-mx-30--an-electric-car-for-the-environment-and-the-driver/
EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-PREFL-01	5243	2030	1782	Mercedes-AMG GLS Owner's Manual Supplement March 2020	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gls-owners-manual-supplement-march-2020-1.pdf
EU-MERCEDES-BENZ-GLS-X167-AMG-GLS63-SUV-FACELIFT-01	5233	2030	1836	Mercedes-AMG GLS Owner's Manual Supplement August 2025	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gls-owners-manual-supplement-august-2025-1.pdf
EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-PREFL-01	5205	2030	1838	Mercedes-Benz Media – New Mercedes-Maybach GLS	https://media.mercedes-benz.pt/novo-mercedes-maybach-gls/
EU-MERCEDES-BENZ-GLS-X167-MAYBACH-GLS600-SUV-FACELIFT-01	5210	2030	1840	Mercedes-Benz Japan – Mercedes-Maybach GLS specifications	https://www.mercedes-benz.co.jp/passengercars/models/suv/gls-maybach/overview.html
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	4947	2018	1785	Mercedes-AMG GLE Owner's Manual Supplement September 2020	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-september-2020-1.pdf
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	4947	2018	1782	Mercedes-AMG GLE Owner's Manual Supplement March 2025	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-gle-owners-manual-supplement-march-2025-1.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	5413	2050	2254	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760	Peugeot Boxer official specification guide	https://www.media.stellantis.com/uploads/uk/attachment/5192/peugeot_boxer_specification_guide_20240129-65f019bd2ad0a.pdf
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416	Honda UK – Civic 4 Door owner's manual	https://www.honda.co.uk/cars/owners/manuals-and-guides/honda-owners-manuals/_jcr_content.html
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497	LADA official – Vesta sedan specifications	https://www.lada.ru/cars/vesta/sedan
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512	LADA official – Vesta SW specifications	https://www.lada.ru/en/cars/vesta/sw
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L1H1-01	4963	2050	2254	Dangel commercial brochures – Ducato/Jumper/Boxer 4x4	https://www.dangel.com/fr/brochures-commerciales
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L2H1-01	5413	2050	2254	Dangel commercial brochures – Ducato/Jumper/Boxer 4x4	https://www.dangel.com/fr/brochures-commerciales
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H2-01	5998	2050	2522	Dangel commercial brochures – Ducato/Jumper/Boxer 4x4	https://www.dangel.com/fr/brochures-commerciales
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L3H3-01	5998	2050	2760	Dangel commercial brochures – Ducato/Jumper/Boxer 4x4	https://www.dangel.com/fr/brochures-commerciales
EU-FIAT-DUCATO-III-X250-DANGEL-4X4-VAN-L4H2-01	6363	2050	2522	Dangel commercial brochures – Ducato/Jumper/Boxer 4x4	https://www.dangel.com/fr/brochures-commerciales
EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB3630-01	6038	2041	2739	AutoScout24 – Renault Mascott FGN 120.35 wheelbase 3630	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-fgn-120-35-emp-3-630-utilitaire-diesel-3010/
EU-RENAULT-MASTER-PRO-MASCOTT-II-VAN-WB4130-01	6538	2041	2739	AutoScout24 – Renault Mascott FGN 120.35 wheelbase 4130	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-fgn-120-35-emp-4-130-utilitaire-diesel-3010/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3130-01	5208	2041	2262	AutoScout24 – Renault Mascott single cab wheelbase 3130	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chc-120-35-emp-3-130-autres-diesel-3007/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB3630-01	5998	2041	2262	AutoScout24 – Renault Mascott single cab wheelbase 3630	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chc-120-35-emp-3-630-autres-diesel-3007/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4130-01	6898	2041	2262	AutoScout24 – Renault Mascott single cab wheelbase 4130	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chc-120-35-emp-4-130-autres-diesel-3007/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-SCAB-WB4630-01	6958	2041	2262	AutoScout24 – Renault Mascott single cab wheelbase 4630	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chc-120-35-emp-4-630-autres-diesel-3007/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB3630-01	5998	2043	2286	AutoScout24 – Renault Mascott double cab wheelbase 3630	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chdc-120-35-emp-3-630-autres-diesel-3009/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4130-01	6898	2043	2286	AutoScout24 – Renault Mascott double cab wheelbase 4130	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chdc-120-35-emp-4-130-autres-diesel-3009/
EU-RENAULT-MASTER-PRO-MASCOTT-II-CHASSIS-DCAB-WB4630-01	6958	2043	2286	AutoScout24 – Renault Mascott double cab wheelbase 4630	https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-chdc-120-35-emp-4-630-autres-diesel-3009/
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault Trafic official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van/Trafic-Panel-Van-eBrochure.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465	Renault Trafic official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van/Trafic-Panel-Van-eBrochure.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault Trafic official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van/Trafic-Panel-Van-eBrochure.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465	Renault Trafic official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van/Trafic-Panel-Van-eBrochure.pdf
EU-INFINITI-QX50-II-J55-SUV-01	4693	1903	1679	INFINITI USA – QX50 all-new platform technical dimensions	https://usa.infinitinews.com/en-US/releases/infiniti-qx50-a-luxury-crossover-with-world-first-technologies-and-an-all-new-platform
EU-LYNK-CO-01-I-FACELIFT-SUV-01	4541	1857	1694	Automobile Dimension – Lynk & Co 01; Encycarpedia – 2021 Lynk & Co 01 HEV	https://www.automobiledimension.com/model/lynkco/01;https://www.encycarpedia.com/lynk-co/21-01-hybrid-electric-suv
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-LWB-01	5157	1922	1674	Mercedes-Benz R-Class official brochure Australia	https://xr793.com/wp-content/uploads/2023/10/2011-Mercedes-Benz-R-Class-AUS.pdf
EU-FORD-KUGA-III-SUV-PHEV-TREND-TITANIUM-01	4614	1883	1675	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-ST-LINE-01	4626	1883	1666	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-VIGNALE-01	4629	1883	1680	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-FORD-KUGA-III-SUV-TREND-TITANIUM-01	4614	1883	1678	Ford Europe – Kuga Technical Specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/Kuga_Euro_TechSpec.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-MWB-01	6103	1993	2344	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-SCAB-LWB-01	6863	1993	2344	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-MWB-01	6103	1993	2362	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-II-W906-CHASSIS-DCAB-LWB-01	6863	1993	2351	Mercedes-Benz Sprinter Single and Dual Cab Chassis official brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	4467	1801	1635	Opel Zafira B official Owner's Manual	https://public-servicebox.opel.com/OVddb/OV/hu_HU/Zafira_B/2006_2011/2010_5/manual_user/Zafira_7_hu.pdf
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635	Opel Zafira B official Owner's Manual	https://public-servicebox.opel.com/OVddb/OV/sk_SK/Zafira_B/2006_2011/2011_5/manual_user/om_zafira_MY11_9_sk.pdf
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430	Peugeot / Stellantis Media – 208 model technical information	https://www.media.stellantis.com/em-en/peugeot/208
EU-FORD-EXPLORER-VI-U625-SUV-01	5049	2004	1778	Ford Explorer official owner manual – vehicle dimensions	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2024845&Uid=G2024844&buildtype=web&countryCode=DEU&div=f&languageCode=de&moidRef=G910634&userMarket=aut&vFilteringEnabled=False&variantid=8595
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483	BMW Group PressClub – BMW 530e Sedan technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0303830IT/443671
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483	BMW Group PressClub – The new BMW 5 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW Group PressClub – The new BMW X3	https://www.press.bmwgroup.com/global/article/detail/T0277021EN/the-new-bmw-x3
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456	Volkswagen Newsroom – Golf design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609/design-and-dimensions-5618
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault press kit – All-new Clio	https://www.press.renault.co.uk/en-gb/releases/2750
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo Cars Media – XC90 specifications	https://www.media.volvocars.com/global/en-gb/models/xc90/2016/specifications
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo Cars Media – XC40 specifications	https://www.media.volvocars.com/global/en-gb/models/xc40/2018/specifications
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub – BMW 520d Sedan technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0301984EN/441098
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479	BMW Group PressClub – The new BMW 5 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	4245	1775	1480	Automobile-Catalog – 2009 Hyundai i30 hatchback	https://www.automobile-catalog.com/car/2009/1181435/hyundai_i30_2_0_premium.html
EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	4280	1775	1480	Automobile-Catalog – 2010 Hyundai i30 facelift hatchback	https://www.automobile-catalog.com/car/2010/1606985/hyundai_i30_blue_1_6_crdi_90_classic.html
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498	BMW Group PressClub – BMW 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0275101EN/398937
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498	BMW Group PressClub – The new BMW 5 Series Touring specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318750EN/463132
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680	Automobile-Catalog – Hyundai Tucson 2.0 2WD	https://www.automobile-catalog.com/car/2005/1178480/hyundai_tucson_2_0_2wd_gsi.html
EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	4475	1775	1565	Automobile-Catalog – Hyundai i30cw pre-facelift	https://www.automobile-catalog.com/car/2010/1181825/hyundai_i30cw_2_0_style.html
EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	4500	1775	1565	Auto-Data – Hyundai i30 I CW facelift generation	https://www.auto-data.net/en/hyundai-i30-i-cw-facelift-2010-generation-5725
EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	3565	1595	1540	Auto-Data – Hyundai i10 I (PA) generation	https://www.auto-data.net/en/hyundai-i10-i-pa-generation-2738
EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	3585	1595	1540	Auto-Data – Hyundai i10 I (PA) facelift generation	https://www.auto-data.net/en/hyundai-i10-i-pa-facelift-2011-generation-2739
EU-VW-PASSAT-ALLTRACK-B8-WAGON-FACELIFT-01	4777	1832	1530	Auto-Data – Volkswagen Passat Alltrack B8 2.0 TSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-2.0-tsi-272hp-4motion-dsg-36124
EU-RENAULT-MEGANE-I-GRANDTOUR-VAN-PHASE-II-01	4437	1698	1420	Auto-Data – Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.8-16v-116hp-10605
EU-MERCEDES-BENZ-GLB-X247-SUV-PREFL-01	4634	1834	1659	Mercedes-Benz Media – Mercedes-Benz GLB	https://media.mercedes-benz.com/article/2bd86d84-fba0-4eb2-b4f1-bae8e77786b9
EU-RENAULT-MEGANE-III-B95-HATCHBACK-PREFL-01	4295	1808	1471	Auto-Data – Renault Megane III 1.6 16V	https://www.auto-data.net/en/renault-megane-iii-1.6-16v-110hp-ethanol-30363
EU-RENAULT-MEGANE-III-B95-HATCHBACK-FACELIFT-01	4302	1808	1471	Automobile-Catalog – 2012 Renault Megane hatchback	https://www.automobile-catalog.com/car/2012/2960225/renault_megane_hatch_1_6_16v_100.html
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488	Renault Master official press kit November 2019	https://www.press.renault.co.uk/assets/documents/original/17081-RE30195RenaultMasterePressKitNovember2019V4.pdf
EU-HYUNDAI-I20-I-PB-HATCHBACK-PREFL-01	3940	1710	1490	Automobile-Catalog – 2009 Hyundai i20 1.2	https://www.automobile-catalog.com/car/2009/1181150/hyundai_i20_1_2_comfort.html
EU-HYUNDAI-I20-I-PB-HATCHBACK-FACELIFT-01	3995	1710	1490	Automobile-Catalog – 2012 Hyundai i20 1.2	https://www.automobile-catalog.com/car/2012/1771700/hyundai_i20_1_2_classic.html
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Dacia Dokker official brochure	https://cdn.group.renault.com/dac/bg/dacia-new-cars/product-plans/brochures/2019/may/B_Dacia_Dokker_Stepway_K67_NEW_IV_BG_small.pdf
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971	Nissan NV300 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/NV300-brochure.pdf
EU-NISSAN-NV300-I-L1H2-01	4999	1956	2493	Nissan NV300 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/NV300-brochure.pdf
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971	Nissan NV300 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/NV300-brochure.pdf
EU-NISSAN-NV300-I-L2H2-01	5399	1956	2490	Nissan NV300 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vans/NV300-brochure.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4501-4600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/mascott/mascott-fgn-120-35-emp-3-630-utilitaire-diesel-3010/ "Renault MASCOTT FGN 120.35 Emp 3,630 | Utilitaire | 2003-2007 - Spécifications techniques"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4601 行）
- 累计尺寸组：dimension_groups_final.tsv（1775 行）

