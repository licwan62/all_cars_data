# 任务：all 第 601-700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0007__a7be9a3c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 601-700 行

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
all 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-HONDA-ACCORD-V-CE9-SEDAN-FACELIFT-01	4685	1720	1380
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618
EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	4140	1800	1593
EU-LANCIA-BETA-828-BERLINA-SEDAN-01	4295	1706	1400
EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	4656	1890	1639
EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	4638	1939	1262
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	4300	1765	1580
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684
EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	4635	1865	1484

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Hyundai	Elantra vi	1.6 D	Stufenheck	Frontantrieb	Diesel	100	136	Feb 2016	Dec 2020	2024-05-01	122182
KIA	Cerato i	1.5 Crdi	Stufenheck	Frontantrieb	Diesel	66	90	Jul 2005	Dec 2009	2024-03-01	122185
KIA	Cee'd	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	91	124	Jan 2008	Sep 2012	2024-03-01	122211
KIA	Cee'd	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	95	130	Jan 2013	Jul 2018	2024-03-01	122213
KIA	Cee'd	1.6 Cvvt	Kombi	Frontantrieb	Benzin	95	130	Nov 2014	Jul 2018	2024-03-01	122217
KIA	Rio iii	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Sep 2011	Dec 2017	2024-03-01	122220
KIA	Sportage iv	2	SUV	Frontantrieb	Benzin	114	155	Dec 2015	Sep 2022	2024-03-01	122239
GAZ	Gazelle	2.4	Kasten	Heckantrieb	Benzin	66	90	Jan 2003	Mar 2013	2024-03-01	122241
KIA	Venga	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Feb 2010	Mar 2019	2024-05-01	122247
Lancia	Beta	1300	Coupe	Frontantrieb	Benzin	61	83	Jul 1977	Jan 1981	2024-03-01	122248
Hyundai	I20 active	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	74	101	Sep 2015	Jun 2018	2024-05-01	122249
KIA	Soul i	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	92	125	Feb 2009	Dec 2011	2024-03-01	122255
Honda	Civic iv	1.6 I 16V 4X4	Stufenheck	Allrad	Benzin	81	110	Jan 1989	Dec 1991	2024-03-01	122270
Honda	Accord	1.6	Schrägheck	Frontantrieb	Benzin	59	80	Jan 1978	Dec 1981	2024-03-01	122284
Honda	Element	2.4	SUV	Frontantrieb	Benzin	119	162	Jul 2002	Dec 2005	2024-03-01	122287
Honda	Element	2.4 4X4	SUV	Allrad	Benzin	119	162	Jul 2002	Dec 2005	2024-03-01	122288
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	99	135	May 1991	Mar 1995	2024-03-01	122381
Mazda	E	E2000	Bus	Heckantrieb	Benzin	60	82	Oct 1989	May 1994	2024-03-01	122392
Fiat	Scudo	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	69	Apr 1998	Dec 2006	2024-03-01	122394
Mazda	323 s v	1.5 16V	Stufenheck	Frontantrieb	Benzin	66	90	May 1994	Dec 1998	2024-03-01	122396
Mazda	Bt-50	2.5 Mrz-cd	Pick-up	Heckantrieb	Diesel	105	143	Aug 2006	Jun 2013	2024-03-01	122397
Mazda	626 ii	1.6	Coupe	Frontantrieb	Benzin	60	82	Nov 1982	Jul 1987	2024-03-01	122405
Peugeot	Partner	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	69	Jan 1999	Jul 2008	2024-03-01	122425
Peugeot	Partner	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Nov 2002	Jul 2008	2024-03-01	122426
Peugeot	3008 i	1.6 HDI 115 / Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Feb 2013	Aug 2016	2024-11-01	122430
Nissan	Nv400	DCI 130 RWD	Kasten	Heckantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122433
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	65	88	Aug 2005	Oct 2006	2024-03-01	122436
Fiat	Scudo	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	69	94	Oct 1999	Dec 2006	2024-03-01	122438
Nissan	Nv400	DCI 130	Kasten	Frontantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122439
Nissan	Nv400	DCI 170	Kasten	Frontantrieb	Diesel	125	170	Sep 2016	Dec 2022	2026-03-01	122441
Nissan	Nv400	DCI 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122443
Nissan	Nv400	DCI 130 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122445
Nissan	Nv400	DCI 170	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jun 2016	Dec 2022	2026-03-01	122450
Nissan	Nv300	1.6 DCI 95	Kasten	Frontantrieb	Diesel	70	95	Sep 2016	-	2024-03-01	122456
Nissan	Nv300	1.6 DCI 120	Kasten	Frontantrieb	Diesel	89	121	Sep 2016	-	2024-03-01	122458
Nissan	Nv300	1.6 DCI 125	Kasten	Frontantrieb	Diesel	92	125	Sep 2016	-	2024-03-01	122459
Nissan	Nv300	1.6 DCI 145	Kasten	Frontantrieb	Diesel	107	146	Sep 2016	-	2024-03-01	122462
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	81	110	Jul 2002	-	2024-03-01	122469
Nissan	Nv300 kombi	1.6 DCI 125	Bus	Frontantrieb	Diesel	92	125	Sep 2016	-	2024-03-01	122481
Nissan	Nv300 kombi	1.6 DCI 145	Bus	Frontantrieb	Diesel	107	145	Sep 2016	-	2024-03-01	122486
Dacia	Lodgy	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	81	110	Mar 2012	-	2024-03-01	122487
Renault	Thalia i	1.4	Stufenheck	Frontantrieb	Benzin	72	98	May 2000	Feb 2009	2024-03-01	122490
Renault	Dauphine	0.8	Stufenheck	Heckantrieb	Benzin	25	34	Mar 1960	Mar 1962	2024-03-01	122492
Dodge	Grand caravan	3.8	Großraumlimousine	Frontantrieb	Benzin	142	193	Jun 2007	Dec 2010	2024-03-01	122505
Fiat	Ritmo	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1980	Aug 1988	2024-03-01	122529
Mercedes-benz	Vario	815 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Sep 1996	Dec 2013	2024-03-01	122548
Wartburg	353	1	Kombi	Frontantrieb	Gemisch	37	50	Feb 1975	Jan 1989	2024-03-01	122555
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	120	163	Jan 2011	-	2024-03-01	122575
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	153	208	Jan 1998	Dec 2003	2024-03-01	122589
Renault	Laguna ii	2.9 V6 24V	Schrägheck	Frontantrieb	Benzin	155	211	Mar 2001	Aug 2007	2024-03-01	122595
Mercedes-benz	Sl	560 SL	Cabriolet	Heckantrieb	Benzin	178	242	Jan 1986	Dec 1989	2024-03-01	122596
Citroën	Jumpy iii	1.6 Bluehdi 95	Bus	Frontantrieb	Diesel	70	95	Apr 2016	-	2024-03-01	122613
Citroën	Jumpy iii	1.6 Bluehdi 115	Bus	Frontantrieb	Diesel	85	116	Apr 2016	Jun 2022	2025-12-01	122614
Mitsubishi	L200	3.5 4WD	Pick-up	Allrad	Benzin	137	186	Aug 2011	Dec 2015	2024-03-01	122618
Mitsubishi	Pajero iv	3.5 V6 4WD	SUV	Allrad	Benzin	139	189	Sep 2009	-	2024-03-01	122620
Chevrolet	Monte carlo	5	Coupe	Heckantrieb	Benzin	116	158	Sep 1978	Dec 1980	2024-03-01	122622
Citroën	Spacetourer	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Dec 2019	Dec 2022	2025-12-01	122623
Citroën	Jumpy iii	2.0 Bluehdi 150	Bus	Frontantrieb	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	122624
Mitsubishi	Delica / space gear	2	Bus	Heckantrieb	Benzin	83	113	Sep 1995	Oct 2002	2024-03-01	122627
KIA	Cerato iii	2.0 MPI	Stufenheck	Frontantrieb	Benzin	112	152	Mar 2016	Jun 2018	2024-05-01	122648
Seat	Toledo	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	May 2009	2024-03-01	122653
Opel	Astra h family	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2009	May 2014	2026-04-01	122662
Opel	Astra h family	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	66	90	Jan 2009	May 2014	2026-04-01	122663
Hyundai	H100	2.4	Kasten	Heckantrieb	Benzin	84	114	Aug 1997	Oct 2003	2024-03-01	122666
Aixam	Mega	0.4 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	4	5	Jan 2007	-	2024-03-01	122693
Aixam	Mega	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	4	5	Jan 2007	Dec 2011	2026-01-01	122694
Suzuki	Grand vitara ii	1.9 Ddis	Geländewagen geschlossen	Heckantrieb	Diesel	95	129	Mar 2006	Aug 2008	2024-03-01	122714
Citroën	C3 picasso	1.6 VTI 115	Großraumlimousine	Frontantrieb	Benzin	84	114	Jul 2009	Dec 2015	2024-08-01	122715
Suzuki	Sx4	1.6 AWD	Stufenheck	Allrad	Benzin	79	107	Oct 2007	Dec 2011	2025-02-03	122718
Land Rover	Range rover sport ii	2.0 SD4 4X4	SUV	Allrad	Diesel	177	241	Aug 2016	Mar 2022	2025-02-03	122731
Ford	Kuga ii	1.5 Tdci	SUV	Frontantrieb	Diesel	88	120	Jul 2016	Jun 2019	2024-03-01	122732
Honda	Cr-V iv	2.4 AWD	SUV	Allrad	Benzin	138	188	Sep 2015	Dec 2018	2025-12-01	122740
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel	143	194	Oct 2016	Oct 2023	2024-03-01	122801
Chevrolet	Caprice	5	Coupe	Heckantrieb	Benzin	110	150	Sep 1980	Dec 1984	2024-03-01	122805
Mercedes-benz	E-Klasse	E 400 4-matic	Kombi	Allrad	Benzin	245	333	Oct 2016	May 2018	2024-03-01	122807
Mercedes-benz	E-Klasse	AMG E 43 4-matic	Kombi	Allrad	Benzin	295	401	Oct 2016	May 2018	2024-03-01	122808
Mercedes-benz	E-Klasse	E 200 D	Kombi	Heckantrieb	Diesel	110	150	Oct 2016	Jun 2019	2024-03-01	122809
Mercedes-benz	E-Klasse	E 350 D	Kombi	Heckantrieb	Diesel	190	258	Oct 2016	May 2018	2024-03-01	122810
Mercedes-benz	Glc	350 D 4-matic	SUV	Allrad	Diesel	190	258	Oct 2016	Apr 2019	2024-03-01	122813
Porsche	Macan	3.6 Turbo	SUV	Allrad	Benzin	324	441	Sep 2016	-	2025-12-01	122815
Mercedes-benz	Glc	350 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Jan 2016	Apr 2019	2024-03-01	122819
Porsche	Panamera	2.9 4S	Schrägheck	Allrad	Benzin	324	440	May 2016	Dec 2023	2024-08-01	122820
Porsche	Panamera	4.0 Turbo	Schrägheck	Allrad	Benzin	404	550	May 2016	Dec 2023	2024-08-01	122821
Mercedes-benz	Glc	350 D 4-matic	SUV	Allrad	Diesel	190	258	Oct 2016	Apr 2019	2024-03-01	122822
Mercedes-benz	Glc	300 4-matic	SUV	Allrad	Benzin	180	245	Oct 2016	Apr 2019	2024-03-01	122823
Porsche	Panamera	4.0 S 4 Diesel	Schrägheck	Allrad	Diesel	310	422	May 2016	Dec 2023	2024-08-01	122824
Chevrolet	Captiva	2.2 D	SUV	Frontantrieb	Diesel	135	184	Feb 2011	Sep 2018	2025-11-01	122830
Mercedes-benz	Glc	350 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Oct 2016	Apr 2019	2024-03-01	122832
Mercedes-benz	Glc	AMG 43 4-matic	SUV	Allrad	Benzin	270	367	Oct 2016	Aug 2019	2024-03-01	122833
Porsche	Panamera	2.9 4 E-hybrid	Schrägheck	Allrad	Benzin/Elektro	340	462	May 2016	Dec 2023	2024-08-01	122834
Mercedes-benz	Glc	220 D 4-matic	SUV	Allrad	Diesel	120	163	Jun 2016	Apr 2019	2024-03-01	122836
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	150	204	Jun 2016	Aug 2020	2024-03-01	122843
Tesla	Model s	P100d AWD	Schrägheck	Allrad	Elektro	568	772	Oct 2016	Apr 2026	2026-06-01	122853
Tesla	Model x	P100d AWD	Schrägheck	Allrad	Elektro	568	772	Oct 2016	Apr 2026	2026-06-01	122855
Suzuki	Ignis iii	1.2	Schrägheck	Frontantrieb	Benzin	66	90	Oct 2016	-	2024-03-01	122890
Suzuki	Ignis iii	1.2 Allgrip	Schrägheck	Allrad	Benzin	66	90	Oct 2016	-	2024-03-01	122891
Suzuki	Ignis iii	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	66	90	Feb 2016	-	2025-06-01	122892
Suzuki	Ignis iii	1.2 Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	66	90	Feb 2016	-	2025-06-01	122893
Chevrolet	Impala	5.7	Coupe	Heckantrieb	Benzin	119	162	Sep 1973	Dec 1974	2024-03-01	122896
Volvo	S60 i	2.4 CDI	Stufenheck	Frontantrieb	Diesel	85	116	Oct 2003	Dec 2005	2024-03-01	122901


--- Round 1 / 首次发送 ---
## 更新点

* 首轮按物理车身聚类闭合 4 个新尺寸组：KIA Cee'd II 五门掀背、Cee'd II 旅行车、KIA Sportage IV、Suzuki Ignis III。
* KIA 官方资料明确 Cee'd 五门版为 `4310 × 1780 × 1470 mm`、旅行车为 `4505 × 1780 × 1485 mm`，宽度明确不含后视镜。([press.kia.com][1])
* KIA Sportage IV 官方资料确认 `4480 × 1855 × 1635 mm`。
* Suzuki 官方资料确认 Ignis 的 2WD、4WD 共用 `3700 × 1660 × 1595 mm` 五门外廓。([suzuki.co.jp][2])
* 直接复用跨批次已有尺寸组：Cerato III facelift、GLC X253 改款前标准车身、Tesla Model S 2016 facelift、Tesla Model X I。
* AMG GLC 43 未并入普通 X253 组，保留后续独立核对其 AMG 外部套件三维。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：16
* READY 映射：16
* PENDING Ktype：84
* 当前批次引用的已确认尺寸组：8

  * 本轮首次创建：4
  * 跨批次复用：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122213	122213	Hatchback	Cee'd II	JD	5	EU-KIA-CEED-II-JD-HATCHBACK-01	HIGH	JD五门掀背物理外廓。	READY
122217	122217	Wagon	Cee'd II	JD	5	EU-KIA-CEED-II-JD-WAGON-01	HIGH	JD五门旅行车物理外廓。	READY
122239	122239	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-QL-SUV-01	HIGH	QL五门标准SUV外廓。	READY
122648	122648	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH	YD四门改款三厢外廓；复用既有尺寸组。	READY
122813	122813	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；复用既有尺寸组。	READY
122819	122819	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；插电混动不改变物理外廓。	READY
122822	122822	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；复用既有尺寸组。	READY
122823	122823	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；复用既有尺寸组。	READY
122832	122832	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；插电混动不改变物理外廓。	READY
122836	122836	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前标准SUV外廓；复用既有尺寸组。	READY
122853	122853	Hatchback	Model S I facelift		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH	2016改款后五门掀背外廓；复用既有尺寸组。	READY
122855	122855	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	输入车身形式修正为五门SUV；复用既有尺寸组。	READY
122890	122890	Hatchback	Ignis III		5	EU-SUZUKI-IGNIS-III-HATCHBACK-01	HIGH	五门物理外廓；前驱汽油版本。	READY
122891	122891	Hatchback	Ignis III		5	EU-SUZUKI-IGNIS-III-HATCHBACK-01	HIGH	五门物理外廓；AllGrip不改变三维。	READY
122892	122892	Hatchback	Ignis III		5	EU-SUZUKI-IGNIS-III-HATCHBACK-01	HIGH	五门物理外廓；混动系统不改变三维。	READY
122893	122893	Hatchback	Ignis III		5	EU-SUZUKI-IGNIS-III-HATCHBACK-01	HIGH	五门物理外廓；混动及AllGrip不改变三维。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CEED-II-JD-HATCHBACK-01	4310	1780	1470	Kia Motors Europe upgraded cee'd official technical specifications	https://press.kia.com/ie/en/home/media-resouces/press-releases/2015/15_08_31_35---kia-ceed-upgrade.html
EU-KIA-CEED-II-JD-WAGON-01	4505	1780	1485	Kia Motors Europe upgraded cee'd official technical specifications	https://press.kia.com/ie/en/home/media-resouces/press-releases/2015/15_08_31_35---kia-ceed-upgrade.html
EU-KIA-SPORTAGE-IV-QL-SUV-01	4480	1855	1635	Kia Motors Europe All-new Sportage 2016 official press kit	https://press.kia.com/content/dam/kiapress/EU/download-files/16-02/Press-Kit-All-new-Sportage-2016.pdf
EU-SUZUKI-IGNIS-III-HATCHBACK-01	3700	1660	1595	Suzuki Motor Corporation 2015 Tokyo Motor Show Ignis specifications	https://www.suzuki.co.jp/car/entertainment/motorshow/2015/exhibition/ignis.html
```

## 下一步优先处理

1. 批量闭合 Nissan NV400 的驱动形式、轴距和车顶高度分支。
2. 批量闭合 Nissan NV300 Kasten、NV300 Kombi 的短轴/长轴与车顶分支。
3. 处理 Citroën Jumpy III、SpaceTourer 共平台的 XS/M/XL 长度组。
4. 随后处理 Mazda BT-50、Toyota Hilux、Mitsubishi L200 等驾驶室外廓分支。

推进信号：CONTINUE

[1]: https://press.kia.com/ie/en/home/media-resouces/press-releases/2015/15_08_31_35---kia-ceed-upgrade.html "Distinctive looks, new engines and more dynamic performance for upgraded Kia cee’d"
[2]: https://www.suzuki.co.jp/car/entertainment/motorshow/2015/exhibition/ignis.html?utm_source=chatgpt.com "イグニス | 第44回東京モーターショー2015 | スズキ"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Nissan NV300 商用车簇，共处理 6 个 Ktype、16 条派生映射。
* `95/120 PS` 厢式车确认覆盖 `L1H1、L2H1`；`125/145 PS` 厢式车覆盖 `L1H1、L1H2、L2H1、L2H2`；`125/145 PS` Kombi 覆盖 `L1H1、L2H1`。
* Nissan 官方资料明确四种外廓的车宽均为不含后视镜的 `1956 mm`，并分别给出长度、高度和发动机配置矩阵。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：22
* READY 映射：32
* PENDING Ktype：78
* 当前批次引用的已确认尺寸组：12
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122456_l1h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶厢式车。	READY
122456_l2h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶厢式车。	READY
122458_l1h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶厢式车。	READY
122458_l2h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶厢式车。	READY
122459_l1h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶厢式车。	READY
122459_l1h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H2-01	HIGH	L1H2短轴高顶厢式车。	READY
122459_l2h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶厢式车。	READY
122459_l2h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H2-01	HIGH	L2H2长轴高顶厢式车。	READY
122462_l1h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶厢式车。	READY
122462_l1h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L1H2-01	HIGH	L1H2短轴高顶厢式车。	READY
122462_l2h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶厢式车。	READY
122462_l2h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-VAN-L2H2-01	HIGH	L2H2长轴高顶厢式车。	READY
122481_l1h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶Kombi外廓。	READY
122481_l2h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶Kombi外廓。	READY
122486_l1h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1H1短轴低顶Kombi外廓。	READY
122486_l2h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2H1长轴低顶Kombi外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV300-I-VAN-L1H1-01	4999	1956	1971	Nissan NV300 UK official brochure and price list	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-VAN-L1H2-01	4999	1956	2493	Nissan NV300 UK official brochure and price list	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-VAN-L2H1-01	5399	1956	1971	Nissan NV300 UK official brochure and price list	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-VAN-L2H2-01	5399	1956	2490	Nissan NV300 UK official brochure and price list	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
```

## 下一步优先处理

1. 闭合 Nissan NV400 前驱厢式车的 `L1H1、L2H2、L2H3、L3H2、L3H3` 分支。
2. 单独核对 NV400 后驱厢式车及底盘车的轴距、单排/双排和单后轮/双后轮边界。
3. 随后批量处理 Citroën Jumpy III 与 SpaceTourer 的 `XS、M、XL` 共平台尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Nissan NV400 前驱厢式车簇：`DCI 130` 覆盖 `L1H1、L2H2、L2H3、L3H2、L3H3`，`DCI 170` 覆盖除 `L1H1` 外的四个分支。
* Nissan 官方规格图确认五种外廓的车身宽度均为不含后视镜的 `2070 mm`；含后视镜宽度为 `2470 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：24
* READY 映射：41
* PENDING Ktype：76
* 当前批次引用的已确认尺寸组：17
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122439_l1h1	122439	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	HIGH	前驱L1H1短轴低顶厢式车。	READY
122439_l2h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L2H2-01	HIGH	前驱L2H2中轴中顶厢式车。	READY
122439_l2h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L2H3-01	HIGH	前驱L2H3中轴高顶厢式车。	READY
122439_l3h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L3H2-01	HIGH	前驱L3H2长轴中顶厢式车。	READY
122439_l3h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L3H3-01	HIGH	前驱L3H3长轴高顶厢式车。	READY
122441_l2h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L2H2-01	HIGH	前驱L2H2中轴中顶厢式车。	READY
122441_l2h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L2H3-01	HIGH	前驱L2H3中轴高顶厢式车。	READY
122441_l3h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L3H2-01	HIGH	前驱L3H2长轴中顶厢式车。	READY
122441_l3h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-VAN-FWD-L3H3-01	HIGH	前驱L3H3长轴高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV400-I-VAN-FWD-L1H1-01	5048	2070	2303	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-VAN-FWD-L2H2-01	5548	2070	2499	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-VAN-FWD-L2H3-01	5548	2070	2749	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-VAN-FWD-L3H2-01	6198	2070	2488	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-VAN-FWD-L3H3-01	6198	2070	2744	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
```

## 下一步优先处理

1. 闭合 NV400 后驱厢式车的 `L3H2 SRW、L4H2 DRW、L4H3 DRW` 分支。
2. 核对 NV400 前驱及后驱底盘车的单排、双排与轴距边界。
3. 批量处理 Citroën Jumpy III、SpaceTourer 的 `XS、M、XL` 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 NV400 前驱底盘车簇：130 PS 覆盖单排 `L2H1`、单排 `L3H1`、双排 `L3H1`；170 PS 覆盖单排和双排 `L3H1`。官方资料明确车身宽度为不含后视镜的 `2070 mm`。
* 闭合 Jumpy III／SpaceTourer 共平台乘用车簇的 `XS、M、XL` 外廓；采用已完成认证后的 `4609/4959/5309 × 1920 × 1905/1890/1890 mm`，宽度明确不含后视镜。([汽车目录档案][1])
* NV400 后驱 130 PS 厢式车及底盘车暂未修改：当前官方 UK 配置矩阵仅列出 145/165 PS 后驱版本，需优先核对其他欧洲市场配置边界。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：30
* READY 映射：57
* PENDING Ktype：70
* 当前批次引用的已确认尺寸组：23
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122443_sc_l2h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-PICKUP-FWD-SINGLE-L2H1-01	HIGH	前驱单排L2H1底盘车。	READY
122443_sc_l3h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-PICKUP-FWD-SINGLE-L3H1-01	HIGH	前驱单排L3H1底盘车。	READY
122443_dc_l3h1	122443	Pickup	NV400 I		4	EU-NISSAN-NV400-I-PICKUP-FWD-DOUBLE-L3H1-01	HIGH	前驱双排L3H1底盘车。	READY
122450_sc_l3h1	122450	Pickup	NV400 I		2	EU-NISSAN-NV400-I-PICKUP-FWD-SINGLE-L3H1-01	HIGH	前驱单排L3H1底盘车。	READY
122450_dc_l3h1	122450	Pickup	NV400 I		4	EU-NISSAN-NV400-I-PICKUP-FWD-DOUBLE-L3H1-01	HIGH	前驱双排L3H1底盘车。	READY
122613_xs	122613	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	XS短车身乘用版外廓。	READY
122613_m	122613	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M中车身乘用版外廓。	READY
122613_xl	122613	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长车身乘用版外廓。	READY
122614_xs	122614	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	XS短车身乘用版外廓。	READY
122614_m	122614	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M中车身乘用版外廓。	READY
122614_xl	122614	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长车身乘用版外廓。	READY
122623_m	122623	MPV	SpaceTourer I	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M中车身乘用版外廓。	READY
122623_xl	122623	MPV	SpaceTourer I	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长车身乘用版外廓。	READY
122624_xs	122624	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	XS短车身乘用版外廓。	READY
122624_m	122624	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M中车身乘用版外廓。	READY
122624_xl	122624	MPV	Jumpy III	K0	5	EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长车身乘用版外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV400-I-PICKUP-FWD-SINGLE-L2H1-01	5643	2070	2265	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-PICKUP-FWD-SINGLE-L3H1-01	6293	2070	2258	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-NISSAN-NV400-I-PICKUP-FWD-DOUBLE-L3H1-01	6293	2070	2263	Nissan NV400 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV400_UK.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XS-01	4609	1920	1905	Citroën SpaceTourer 2018 official brochure archived copy	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-SpaceTourer-2018-UK.pdf
EU-CITROEN-JUMPY-III-K0-MPV-M-01	4959	1920	1890	Citroën SpaceTourer 2018 official brochure archived copy	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-SpaceTourer-2018-UK.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XL-01	5309	1920	1890	Citroën SpaceTourer 2018 official brochure archived copy	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-SpaceTourer-2018-UK.pdf
```

## 下一步优先处理

1. 解决 NV400 后驱 130 PS 厢式车和底盘车的欧洲市场配置冲突。
2. 批量闭合 Fiat Scudo／Peugeot Partner 的底盘车分支。
3. 处理 Mazda BT-50、Toyota Hilux VII、Mitsubishi L200 的驾驶室和货斗外廓。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-SpaceTourer-2018-UK.pdf?utm_source=chatgpt.com "CITROËN SPACETOURER"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz E-Class V 车型簇：W213 四门三厢建立独立尺寸组；4 个 S213 旅行车 Ktype 共用同一外廓尺寸组。两组宽度资料均同时列出含镜宽度，因此落盘的 `1852 mm` 为不含后视镜口径。([汽车数据][1])
* Porsche Panamera II 标准轴距车型拆分为普通车身高度 `1423 mm` 和 Turbo 车身高度 `1427 mm`；4S、4S Diesel 和 4 E-Hybrid 共用普通车身组。Porsche 官方资料明确宽度 `1937 mm`、含镜宽度 `2165 mm`。([Porsche Newsroom][2])
* Mercedes-AMG GLC 43 的三维与已有 X253 改款前尺寸组完全一致，本轮仅新增映射，不重复输出尺寸组。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：40
* READY 映射：67
* PENDING Ktype：60
* 当前批次引用的已确认尺寸组：27
* 本轮新增映射：10
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122801	122801	Sedan	E-Class V	W213	4	EU-MERCEDES-BENZ-E-CLASS-V-W213-SEDAN-PREFL-01	HIGH	W213四门三厢外廓。	READY
122807	122807	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-V-S213-WAGON-PREFL-01	HIGH	S213五门旅行车外廓。	READY
122808	122808	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-V-S213-WAGON-PREFL-01	HIGH	S213五门旅行车外廓。	READY
122809	122809	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-V-S213-WAGON-PREFL-01	HIGH	S213五门旅行车外廓。	READY
122810	122810	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-V-S213-WAGON-PREFL-01	HIGH	S213五门旅行车外廓。	READY
122820	122820	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-HATCHBACK-01	HIGH	971标准轴距五门掀背外廓。	READY
122821	122821	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-HATCHBACK-TURBO-01	HIGH	971标准轴距Turbo外廓。	READY
122824	122824	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-HATCHBACK-01	HIGH	971标准轴距五门掀背外廓。	READY
122833	122833	SUV	GLC I	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253改款前五门SUV外廓。	READY
122834	122834	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-HATCHBACK-01	HIGH	971标准轴距五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-V-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-class W213 E 220d 4MATIC technical specifications	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-220d-194hp-4matic-9g-tronic-29551
EU-MERCEDES-BENZ-E-CLASS-V-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell S213 E 200d technical specifications;Auto-Data Mercedes-Benz E-class T-modell S213 AMG E 43 technical specifications	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-200d-150hp-9g-tronic-26741;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-43-401hp-4matic-9g-tronic-26467
EU-PORSCHE-PANAMERA-II-971-HATCHBACK-01	5049	1937	1423	Porsche 2017 Panamera official press information;Porsche Panamera 4 E-Hybrid official technical data;Automobile-Catalog Porsche Panamera 4S Diesel specifications	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf;https://download.newsroom.porsche.com/dam/jcr%3Ac8a6f10f-4f87-4404-bea7-42bf8aeb5520/Porsche_Panamera_4_E-Hybrid_Facts_and_Figures.pdf;https://www.automobile-catalog.com/car/2016/2872625/porsche_panamera_4s_diesel.html
EU-PORSCHE-PANAMERA-II-971-HATCHBACK-TURBO-01	5049	1937	1427	Porsche 2017 Panamera official press information	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf
```

## 下一步优先处理

1. 批量闭合现代 SUV 簇：Porsche Macan、Chevrolet Captiva、Range Rover Sport II、Ford Kuga II、Honda CR-V IV。
2. 处理 Mazda BT-50、Toyota Hilux VII、Mitsubishi L200 和 VW Amarok 的驾驶室、货斗与宽体分支。
3. 随后解决 NV400 后驱 130 PS 与旧款 Scudo、Partner 底盘车边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-220d-194hp-4matic-9g-tronic-29551 "Mercedes-Benz E-class (W213) E 220d (194 Hp) 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf?utm_source=chatgpt.com "2017 Porsche Panamera"
[3]: https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-amg-glc-43-367hp-4matic-g-tronic-24365 "Mercedes-Benz GLC SUV (X253) AMG GLC 43 (367 Hp) 4MATIC G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Porsche Macan I `324 kW / 441 PS` 分支，确认对应 `Macan Turbo Performance Package` 外廓：`4699 × 1923 × 1609 mm`。([i.i-sgcm][1])
* 闭合 Chevrolet Captiva I facelift 车型簇，两个柴油 Ktype 共用 `4673 × 1849 × 1727 mm` 五门 SUV 外廓，宽度为不含后视镜口径。([汽车目录][2])
* 闭合 Ford Kuga II facelift `1.5 TDCi` 外廓：`4524 × 1838 × 1689 mm`。([Dezo's Garage][3])
* 闭合 Honda CR-V IV facelift AWD 外廓：`4605 × 1820 × 1685 mm`，其中 `1820 mm` 明确为不含后视镜宽度。([本田新闻][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：45
* READY 映射：72
* PENDING Ktype：55
* 当前批次引用的已确认尺寸组：31
* 本轮新增映射：5
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122575	122575	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	MEDIUM	C140五门改款SUV外廓。	READY
122732	122732	SUV	Kuga II facelift	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH	DM2改款后五门SUV外廓。	READY
122740	122740	SUV	CR-V IV facelift	RM4	5	EU-HONDA-CR-V-IV-FACELIFT-RM4-SUV-01	HIGH	RM4改款后AWD五门SUV外廓。	READY
122815	122815	SUV	Macan I	95B	5	EU-PORSCHE-MACAN-I-95B-SUV-TURBO-PERFORMANCE-01	HIGH	95B Turbo Performance Package外廓。	READY
122830	122830	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	HIGH	C140五门改款SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	4673	1849	1727	Chevrolet Captiva 2011 official brochure archived copy;Automobile-Catalog Chevrolet Captiva 2.2 D facelift specifications	https://autocatalogarchive.com/wp-content/uploads/2021/11/Chevrolet-Captiva-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1569185/chevrolet_captiva_2_2_d_163_ls_2wd.html
EU-FORD-KUGA-II-FACELIFT-SUV-01	4524	1838	1689	Ford Kuga 2017 official UK brochure archived copy	https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Kuga-UK.pdf
EU-HONDA-CR-V-IV-FACELIFT-RM4-SUV-01	4605	1820	1685	Honda 2015 CR-V official press kit;Honda 2015 CR-V official brochure archived copy	https://hondanews.eu/eu/en/media/pressreleases/42656/2015-honda-cr-v2;https://autocatalogarchive.com/wp-content/uploads/2016/09/Honda-CR-V-2015-CA.pdf
EU-PORSCHE-MACAN-I-95B-SUV-TURBO-PERFORMANCE-01	4699	1923	1609	Porsche Macan Turbo Performance Package official specifications;Porsche Macan Turbo with Performance Package official brochure archived copy	https://presse.porsche.de/download/prod/presse_pag/PressBasicData.nsf/Download?OpenAgent=&attachmentid=173967&previewpdf=1;https://i.i-sgcm.com/new_cars/cars/11449/brochures/brochure_20170815104545.pdf
```

## 下一步优先处理

1. 拆分并闭合 Range Rover Sport II `2.0 SD4` 的改款前、改款后外廓。
2. 批量处理 Mazda BT-50、Toyota Hilux VII、Mitsubishi L200 与 VW Amarok 的驾驶室和货斗分支。
3. 处理 Hyundai Elantra VI、KIA Rio III、Venga、Soul I 等高复用乘用车型簇。

推进信号：CONTINUE

[1]: https://i.i-sgcm.com/new_cars/cars/11449/brochures/brochure_20170815104545.pdf?utm_source=chatgpt.com "Porsche Macan Turbo with Performance Package"
[2]: https://www.automobile-catalog.com/car/2011/1569005/chevrolet_captiva_2_4_lt_4wd.html?utm_source=chatgpt.com "2011 Chevrolet Captiva 2.4 LT 4WD (man. 6)"
[3]: https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Kuga-UK.pdf?utm_source=chatgpt.com "Ford Kuga"
[4]: https://hondanews.eu/eu/en/media/pressreleases/42656/2015-honda-cr-v2?utm_source=chatgpt.com "2015 Honda CR-V"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 KIA Rio III `1.2 69 PS` 的三门、五门分支。两种车身均为 `4045 × 1720 × 1455 mm`，但门数及侧围不同，因此分别建组。([Kia Press Office][1])
* 闭合 Hyundai i20 Active I `1.4 100 PS` 五门外廓；官方技术资料确认 `4065 × 1760 × 1529 mm`，其中宽度明确不含后视镜。([HYUNDAI MOTORS][2])
* 闭合 KIA Soul I 无车顶行李架外廓：`4105 × 1785 × 1610 mm`；官方资料另列带车顶行李架高度，未与本组混用。([Kia][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：48
* READY 映射：76
* PENDING Ktype：52
* 当前批次引用的已确认尺寸组：35
* 本轮新增映射：4
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122220_3dr	122220	Hatchback	Rio III	UB	3	EU-KIA-RIO-III-UB-HATCHBACK-3D-01	HIGH	UB三门掀背物理外廓。	READY
122220_5dr	122220	Hatchback	Rio III	UB	5	EU-KIA-RIO-III-UB-HATCHBACK-5D-01	HIGH	UB五门掀背物理外廓。	READY
122249	122249	Hatchback	i20 Active I	GB	5	EU-HYUNDAI-I20-ACTIVE-I-GB-HATCHBACK-01	HIGH	GB五门跨界掀背外廓。	READY
122255	122255	Hatchback	Soul I	AM	5	EU-KIA-SOUL-I-AM-HATCHBACK-NO-ROOF-BARS-01	HIGH	AM五门无车顶行李架外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-RIO-III-UB-HATCHBACK-3D-01	4045	1720	1455	Kia Rio 3-door official technical specifications	https://www.kiapressoffice.com/releases/325
EU-KIA-RIO-III-UB-HATCHBACK-5D-01	4045	1720	1455	Kia Rio Geneva debut official technical specifications	https://www.kiapressoffice.com/releases/552
EU-HYUNDAI-I20-ACTIVE-I-GB-HATCHBACK-01	4065	1760	1529	Hyundai i20 Active IAA 2015 official press information	https://www.hyundai.com/content/hyundai/ww/data/news/data/2015/0000004836/attach/150915_New%20i20%20Active%20Press%20Information%20IAA%202015.docx
EU-KIA-SOUL-I-AM-HATCHBACK-NO-ROOF-BARS-01	4105	1785	1610	Kia Soul official product brochure	https://www.kia.com/content/dam/kwcms/dm/en/pdf/Soul-brochure.pdf
```

## 下一步优先处理

1. 解决 KIA Venga 改款前后不同市场保险杠长度口径。
2. 闭合 Hyundai Elantra VI 改款前、改款后柴油车外廓。
3. 处理 Range Rover Sport II SD4，以及 Hilux、BT-50、L200、Amarok 的驾驶室分支。

推进信号：CONTINUE

[1]: https://www.kiapressoffice.com/releases/325?utm_source=chatgpt.com "Kia Rio 3-door goes on sale | Releases"
[2]: https://www.hyundai.com/content/hyundai/ww/data/news/data/2015/0000004836/attach/150915_New%20i20%20Active%20Press%20Information%20IAA%202015.docx?utm_source=chatgpt.com "150915_New i20 Active Press Information IAA 2015.docx"
[3]: https://www.kia.com/content/dam/kwcms/dm/en/pdf/Soul-brochure.pdf?utm_source=chatgpt.com "Free Your Mind"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* KIA Venga `122247` 按改款前、改款后拆分。改款前外廓为 `4068 × 1765 × 1600 mm`；改款后因保险杠造型变化，长度增至 `4075 mm`，宽度仍为明确不含后视镜的 `1765 mm`。([汽车目录][1])
* Range Rover Sport II `122731` 按 L494 改款前、改款后拆分。改款前为 `4850 × 1983 × 1780 mm`；改款后长度增至 `4879 mm`，官方主尺寸高度为 `1803 mm`，不含后视镜车身宽度继续采用 `1983 mm`。
* Hyundai Elantra VI 本轮未修改。现有资料能确认改款前后外廓不同，但对 `1.6 CRDi 136 PS` 的准确改款覆盖边界仍未完全闭合，因此暂不创建猜测性派生行。此项为基于现有资料的判断。([Ultimate Specs][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：50
* READY 映射：80
* PENDING Ktype：50
* 当前批次引用的已确认尺寸组：39
* 本轮新增映射：4
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122247_prefl	122247	Hatchback	Venga I	YN	5	EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	HIGH	YN改款前五门外廓。	READY
122247_facelift	122247	Hatchback	Venga I	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	YN改款后五门外廓。	READY
122731_prefl	122731	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	L494改款前五门SUV外廓。	READY
122731_facelift	122731	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	L494改款后五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	4068	1765	1600	Automobile-Catalog 2010 Kia Venga specifications	https://www.automobile-catalog.com/car/2010/1359515/kia_venga_1_6_crdi_128_mind.html
EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	4075	1765	1600	Kia Venga MY15 official product brochure	https://prod2-eu.kia.com/content/dam/kwcms/kme/global/en/assets/contents/utility/brochure/product-brochure/kia-venga-my15-product-brochure.pdf
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780	Land Rover Range Rover Sport official brochure;Automobile-Catalog 2017 Range Rover Sport 2.0 SD4 specifications	https://resource.digitaldealer.com.au/pdf/17134620805418d32b5c7d0343521230.pdf;https://www.automobile-catalog.com/car/2017/2564720/range-rover_sport_2_0_sd4.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1803	Land Rover Range Rover Sport official UK brochure;Automobile-Catalog 2018 Range Rover Sport 2.0 SD4 specifications	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/misc/Range-Rover-Sport-Brochure-1L4941920000BGBEN01P_tcm295-140482.pdf;https://www.automobile-catalog.com/car/2018/2606930/range-rover_sport_2_0_sd4.html
```

## 下一步优先处理

1. 闭合 Hyundai Elantra VI `1.6 D` 的改款分界。
2. 批量处理 Toyota Hilux VII、Mazda BT-50、Mitsubishi L200 和 VW Amarok 的驾驶室及货斗分支。
3. 处理 Dacia Lodgy、Citroën C3 Picasso、Suzuki Grand Vitara II 等剩余 MPV／SUV 车型簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2010/1359515/kia_venga_1_6_crdi_128_mind.html?utm_source=chatgpt.com "2010 Kia Venga 1.6 CRDi 128 Mind Specs Review (94 kW ..."
[2]: https://www.ultimatespecs.com/car-specs/Hyundai/106177/Hyundai-Elantra-%28AD%29-16-CRDI-136HP.html?utm_source=chatgpt.com "Hyundai Elantra (AD) 1.6 CRDI 136HP Specs"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Cerato I Sedan 与 Cee’d SW I 的改款前后外廓；两者因改款造成长度或高度变化，分别拆成派生映射。([汽车数据][1])
* 闭合 Honda Element 前驱／四驱共用外廓、Dacia Lodgy、Astra H Family、C3 Picasso，以及 Grand Vitara II 三门／五门分支。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：59
* READY 映射：92
* PENDING Ktype：41
* 当前批次引用的已确认尺寸组：49
* 本轮新增映射：12
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122185_prefl	122185	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	HIGH	LD改款前四门三厢外廓。	READY
122185_facelift	122185	Sedan	Cerato I facelift	LD	4	EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	HIGH	LD改款后四门三厢外廓。	READY
122211_prefl	122211	Wagon	Cee'd SW I	ED	5	EU-KIA-CEED-SW-I-ED-WAGON-PREFL-01	HIGH	ED改款前五门旅行车外廓。	READY
122211_facelift	122211	Wagon	Cee'd SW I facelift	ED	5	EU-KIA-CEED-SW-I-ED-WAGON-FACELIFT-01	HIGH	ED改款后五门旅行车外廓。	READY
122287	122287	SUV	Element I	YH1	5	EU-HONDA-ELEMENT-I-SUV-01	HIGH	YH1前驱五门外廓。	READY
122288	122288	SUV	Element I	YH2	5	EU-HONDA-ELEMENT-I-SUV-01	HIGH	YH2四驱五门外廓。	READY
122487	122487	MPV	Lodgy I		5	EU-DACIA-LODGY-I-MPV-01	HIGH	五门标准MPV外廓。	READY
122662	122662	Hatchback	Astra H facelift	A04	5	EU-OPEL-ASTRA-H-A04-HATCHBACK-FACELIFT-01	HIGH	A04改款后五门掀背外廓。	READY
122663	122663	Hatchback	Astra H facelift	A04	5	EU-OPEL-ASTRA-H-A04-HATCHBACK-FACELIFT-01	HIGH	A04改款后五门掀背外廓。	READY
122714_3dr	122714	SUV	Grand Vitara II	JT	3	EU-SUZUKI-GRAND-VITARA-II-JT-SUV-3D-01	HIGH	JT三门短轴外廓。	READY
122714_5dr	122714	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	HIGH	JT五门长轴外廓。	READY
122715	122715	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-MPV-01	HIGH	五门MPV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	4480	1735	1470	Auto-Data Kia Cerato I Sedan 1.5 CRDi specifications	https://www.auto-data.net/en/kia-cerato-i-sedan-1.5-crdi-102hp-32546
EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	4500	1735	1470	Kia Cerato 2007 owner's manual specifications	https://www.carmanualsonline.info/kia-cerato-2007-owners-manual/?srch=dimensions
EU-KIA-CEED-SW-I-ED-WAGON-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I specifications	https://www.auto-data.net/en/kia-ceed-sw-i-generation-8041
EU-KIA-CEED-SW-I-ED-WAGON-FACELIFT-01	4490	1790	1525	Kia Cee'd 2011 owner's manual specifications	https://www.carmanualsonline.info/kia-ceed-2011-owners-manual/?srch=dimensions
EU-HONDA-ELEMENT-I-SUV-01	4300	1815	1788	Auto-Data Honda Element I 2.4 4WD specifications	https://www.auto-data.net/en/honda-element-i-2.4-160hp-4wd-12136
EU-DACIA-LODGY-I-MPV-01	4498	1751	1680	Automobile Dimension Dacia Lodgy dimensions	https://www.automobiledimension.com/model/dacia/lodgy
EU-OPEL-ASTRA-H-A04-HATCHBACK-FACELIFT-01	4249	1753	1460	Vauxhall Astra H 2009 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/astra-h/AstraH_April_2009.pdf
EU-SUZUKI-GRAND-VITARA-II-JT-SUV-3D-01	4005	1810	1695	Suzuki Grand Vitara official product brochure	https://suzukicentar.com/wp-content/uploads/2011/12/vitara-katalog.pdf
EU-SUZUKI-GRAND-VITARA-II-JT-SUV-5D-01	4470	1810	1695	Suzuki Grand Vitara official product brochure	https://suzukicentar.com/wp-content/uploads/2011/12/vitara-katalog.pdf
EU-CITROEN-C3-PICASSO-I-MPV-01	4078	1766	1631	Automobile-Catalog Citroën C3 Picasso European specifications	https://www.automobile-catalog.com/car/2013/1864895/citroen_c3_picasso_vti_120_egs6_tendance.html
```

## 下一步优先处理

1. 闭合 Hyundai Elantra VI 改款前后柴油车型的市场高度口径。
2. 处理 Hilux VII、BT-50、L200、Amarok 的驾驶室与货斗分支。
3. 继续处理 Volvo 940、Mazda 323 S V、Renault Laguna II 等标准乘用车外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-cerato-i-sedan-1.5-crdi-102hp-32546 "Kia Cerato I Sedan 1.5 CRDi (102 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/honda-element-i-2.4-160hp-4wd-12136?utm_source=chatgpt.com "Honda Element I 2.4 (160 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Volvo 940 `944` 四门三厢外廓：`4871 × 1750 × 1425 mm`。([汽车数据][1])
* 闭合 Mazda 323 S V `BA` 四门三厢外廓：`4340 × 1710 × 1420 mm`。([汽车数据][2])
* 闭合 Renault Laguna II `B74` 五门掀背外廓：`4576 × 1772 × 1429 mm`；输入中的 `2.9 V6 24V` 对应资料中的 2946 cc V6。([汽车数据][3])
* 闭合 Honda Civic IV 实时四驱四门三厢外廓。Honda 官方历史规格表明确四驱 `EF5` 为 `4310 × 1695 × 1380 mm`，未采用前驱版本的较低车身尺寸。([honda.co.jp][4])
* 闭合 Honda Accord I `SJ` 三门掀背外廓：`4125 × 1620 × 1335 mm`。([汽车数据][5])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射：97
* PENDING Ktype：36
* 当前批次引用的已确认尺寸组：54
* 本轮新增映射：5
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122270	122270	Sedan	Civic IV	EF5	4	EU-HONDA-CIVIC-IV-EF5-SEDAN-4WD-01	HIGH	EF5实时四驱四门三厢外廓。	READY
122284	122284	Hatchback	Accord I	SJ	3	EU-HONDA-ACCORD-I-SJ-HATCHBACK-01	HIGH	SJ三门掀背外廓。	READY
122381	122381	Sedan	940	944	4	EU-VOLVO-940-944-SEDAN-01	HIGH	944四门三厢外廓。	READY
122396	122396	Sedan	323 S V	BA	4	EU-MAZDA-323-S-V-BA-SEDAN-01	HIGH	BA四门三厢外廓。	READY
122595	122595	Hatchback	Laguna II	B74	5	EU-RENAULT-LAGUNA-II-B74-HATCHBACK-01	HIGH	B74五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-IV-EF5-SEDAN-4WD-01	4310	1695	1380	Honda Civic historical official specifications	https://www.honda.co.jp/factbook/auto/CIVIC/19920700/cv20-043.html
EU-HONDA-ACCORD-I-SJ-HATCHBACK-01	4125	1620	1335	Auto-Data Honda Accord I Hatchback 1.6 EX specifications	https://www.auto-data.net/en/honda-accord-i-hatchback-sj-sy-1.6-ex-sj-80hp-12111
EU-VOLVO-940-944-SEDAN-01	4871	1750	1425	Auto-Data Volvo 940 944 2.3i specifications	https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286
EU-MAZDA-323-S-V-BA-SEDAN-01	4340	1710	1420	Auto-Data Mazda 323 S V BA 1.5i 16V specifications	https://www.auto-data.net/en/mazda-323-s-v-ba-1.5i-16v-88hp-11160
EU-RENAULT-LAGUNA-II-B74-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II 3.0 V6 24V specifications	https://www.auto-data.net/en/renault-laguna-ii-3.0-v6-24v-207hp-10332
```

## 下一步优先处理

1. 闭合 Hyundai Elantra VI 改款前后柴油外廓。
2. 批量处理 Toyota Hilux VII、Mazda BT-50、Mitsubishi L200 和 VW Amarok 的驾驶室及货斗分支。
3. 处理 Suzuki SX4 Sedan、Renault Thalia I、Fiat Ritmo、Seat Toledo 与 Peugeot 3008 I 等剩余标准乘用车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286 "Volvo 940 (944) 2.3i (131 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mazda-323-s-v-ba-1.5i-16v-88hp-11160 "Mazda 323 S V (BA) 1.5i 16V (88 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/renault-laguna-ii-3.0-v6-24v-207hp-10332 "Renault Laguna II 3.0 V6 24V (207 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.honda.co.jp/factbook/auto/CIVIC/19920700/cv20-043.html?msockid=1f5038b7d7156cd43d3b2e2ed6c46d4d "CIVIC 1992.07｜プレスインフォメーション｜Honda公式サイト"
[5]: https://www.auto-data.net/en/honda-accord-i-hatchback-sj-sy-1.6-ex-sj-80hp-12111?utm_source=chatgpt.com "Honda Accord I Hatchback (SJ,SY) 1.6 EX (SJ) (80 Hp)"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* Hyundai Elantra VI 按改款前后拆分：改款前为 `4570 × 1800 × 1450 mm`，改款后因前后保险杠变化增长至 `4620 mm`；两组宽度均为不含后视镜的 `1800 mm`。([Ultimate Specs][1])
* Renault Thalia I 按 2002 年改款拆分：改款前 `4150 × 1639 × 1416 mm`，改款后 `4171 × 1639 × 1437 mm`。([汽车数据][2])
* 闭合 Peugeot 3008 I Phase II 和 SEAT Toledo III 5P2 标准外廓。Peugeot 资料同时列出折叠后视镜及含镜宽度，因此落盘的 `1837 mm` 为车身宽度。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：68
* READY 映射：103
* PENDING Ktype：32
* 当前批次引用的已确认尺寸组：60
* 本轮新增映射：6
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122182_prefl	122182	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	HIGH	AD改款前四门三厢外廓。	READY
122182_facelift	122182	Sedan	Elantra VI facelift	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	MEDIUM	AD改款后四门三厢外廓。	READY
122430	122430	SUV	3008 I facelift		5	EU-PEUGEOT-3008-I-SUV-FACELIFT-01	HIGH	第一代改款后五门外廓。	READY
122490_prefl	122490	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-PREFL-01	HIGH	第一代改款前四门三厢外廓。	READY
122490_facelift	122490	Sedan	Thalia I facelift		4	EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	HIGH	第一代2002年改款后四门外廓。	READY
122653	122653	MPV	Toledo III	5P2	5	EU-SEAT-TOLEDO-III-5P2-MPV-01	HIGH	5P2五门高顶掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	4570	1800	1450	Hyundai Asia Pacific Elantra official specifications;Ultimate Specs Hyundai Elantra AD 1.6 CRDi specifications	https://www.hyundai.com/pacific/en/find-a-car/elantra/specification;https://www.ultimatespecs.com/car-specs/Hyundai/106177/Hyundai-Elantra-%28AD%29-16-CRDI-136HP.html
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	4620	1800	1450	Hyundai Elantra official specifications sheet	https://www.hyundai.com/content/dam/hyundai/au/en/models/elantra/docs/Hyundai_Elantra_Specifications_Sheet.pdf
EU-PEUGEOT-3008-I-SUV-FACELIFT-01	4365	1837	1635	Auto-Data Peugeot 3008 I Phase II 1.6 HDi specifications	https://www.auto-data.net/en/peugeot-3008-i-phase-ii-2013-1.6-hdi-115hp-fap-bmp-19788
EU-RENAULT-THALIA-I-SEDAN-PREFL-01	4150	1639	1416	Auto-Data Renault Clio Symbol I 1.4 16V specifications	https://www.auto-data.net/en/renault-clio-symbol-i-1.4-i-16v-98hp-10429
EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 1.4 16V specifications	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-1.4-16v-98hp-10663
EU-SEAT-TOLEDO-III-5P2-MPV-01	4457	1768	1568	Automobile-Catalog 2008 SEAT Toledo III specifications	https://www.automobile-catalog.com/car/2008/3081065/seat_toledo_1_6.html
```

## 下一步优先处理

1. 处理 Toyota Hilux VII、Mazda BT-50、Mitsubishi L200 和 Volkswagen Amarok 的驾驶室、货斗及改款分支。
2. 闭合 Lancia Beta Coupe、Mazda 626 II Coupe、Mercedes-Benz SL R107 等双门车型。
3. 处理 Lincoln Town Car III、Dodge Grand Caravan、Chevrolet Monte Carlo／Caprice／Impala 等北美车型外廓。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Hyundai/106177/Hyundai-Elantra-%28AD%29-16-CRDI-136HP.html "Hyundai Elantra (AD) 1.6 CRDI 136HP Specs, Performance, Comparisons"
[2]: https://www.auto-data.net/en/renault-clio-symbol-i-1.4-i-16v-98hp-10429 "Renault Clio Symbol I 1.4 i 16V (98 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/peugeot-3008-i-phase-ii-2013-1.6-hdi-115hp-fap-bmp-19788 "Peugeot 3008 I (Phase II, 2013) 1.6 HDi (115 Hp) FAP BMP | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Lancia Beta Coupe、Mazda 626 II Coupe 与 Mercedes-Benz 560 SL。三组宽度均明确为不含后视镜口径。([汽车目录][1])
* Fiat Ritmo Ktype 跨越 1982 年改款，并同时覆盖三门、五门车身，本轮拆为四个稳定物理分支。改款前为 `3937 × 1650 × 1400 mm`，改款后为 `4014 × 1650 × 1405 mm`。([汽车目录][2])
* 闭合 Lincoln Town Car III 标准轴距外廓；不含后视镜宽度另经 Edmunds 交叉确认。([汽车数据][3])
* 闭合 Suzuki SX4 I Sedan 与 Volvo S60 I。SX4 输入中的 AWD 配置与欧洲三厢资料存在配置字段差异，但已确认的四门三厢物理外廓不受驱动形式影响。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：75
* READY 映射：113
* PENDING Ktype：25
* 当前批次引用的已确认尺寸组：70
* 本轮新增映射：10
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122248	122248	Coupe	Beta Coupe	828BC	2	EU-LANCIA-BETA-828BC-COUPE-01	HIGH	828BC双门Coupe外廓。	READY
122405	122405	Coupe	626 II	GC	2	EU-MAZDA-626-II-GC-COUPE-01	HIGH	GC双门Coupe外廓。	READY
122529_prefl_3dr	122529	Hatchback	Ritmo I	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	HIGH	改款前三门掀背外廓。	READY
122529_prefl_5dr	122529	Hatchback	Ritmo I	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	HIGH	改款前五门掀背外廓。	READY
122529_facelift_3dr	122529	Hatchback	Ritmo I facelift	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	HIGH	改款后三门掀背外廓。	READY
122529_facelift_5dr	122529	Hatchback	Ritmo I facelift	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	HIGH	改款后五门掀背外廓。	READY
122589	122589	Sedan	Town Car III	FN145	4	EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	HIGH	FN145标准轴距四门三厢外廓。	READY
122596	122596	Convertible	SL R107 facelift	R107	2	EU-MERCEDES-BENZ-SL-R107-FACELIFT-560SL-CONVERTIBLE-01	HIGH	560 SL北美规格长保险杠外廓。	READY
122718	122718	Sedan	SX4 I		4	EU-SUZUKI-SX4-I-SEDAN-01	MEDIUM	四门三厢外廓；输入AWD配置字段与欧洲版资料不一致。	READY
122901	122901	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-PREFL-01	HIGH	第一代改款前四门三厢外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-BETA-828BC-COUPE-01	3995	1650	1285	Automobile-Catalog 1977 Lancia Beta Coupe 1300 specifications	https://www.automobile-catalog.com/car/1977/44720/lancia_beta_coupe_1300_2a_serie.html
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1350	Automobile-Catalog 1985 Mazda 626 1.6 LX Coupe specifications	https://www.automobile-catalog.com/car/1985/1626140/mazda_626_1_6_lx_coupe.html
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 CL specifications	https://www.automobile-catalog.com/car/1980/1369610/fiat_ritmo_60_cl.html
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 CL specifications	https://www.automobile-catalog.com/car/1980/1369610/fiat_ritmo_60_cl.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	4014	1650	1405	Automobile-Catalog 1984 Fiat Ritmo 60 specifications	https://www.automobile-catalog.com/car/1984/714455/fiat_ritmo_60.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	4014	1650	1405	Automobile-Catalog 1984 Fiat Ritmo 60 specifications	https://www.automobile-catalog.com/car/1984/714455/fiat_ritmo_60.html
EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	5470	1985	1470	Auto-Data Lincoln Town Car III FN145 4.6 V8 specifications;Edmunds 1998 Lincoln Town Car exterior specifications	https://www.auto-data.net/en/lincoln-town-car-iii-fn145-4.6-v8-208hp-8207;https://www.edmunds.com/lincoln/town-car/1998/sedan/features-specs/
EU-MERCEDES-BENZ-SL-R107-FACELIFT-560SL-CONVERTIBLE-01	4580	1790	1307	Automobile-Catalog 1986 Mercedes-Benz 560 SL specifications	https://www.automobile-catalog.com/car/1986/1469810/mercedes-benz_560_sl.html
EU-SUZUKI-SX4-I-SEDAN-01	4490	1730	1545	Automobile-Catalog 2008 Suzuki SX4 Sedan 1.6 VVT specifications	https://www.automobile-catalog.com/car/2008/3408965/suzuki_sx4_sedan_1_6_vvt_2wd.html
EU-VOLVO-S60-I-SEDAN-PREFL-01	4576	1804	1428	Auto-Data Volvo S60 2.4 D specifications;Edmunds 2002 Volvo S60 exterior specifications	https://www.auto-data.net/en/volvo-s60-2.4-d-130hp-9219;https://www.edmunds.com/volvo/s60/2002/sedan/features-specs/
```

## 下一步优先处理

1. 批量闭合 Toyota Hilux VII、Mazda BT-50、Mitsubishi L200 与 Volkswagen Amarok 的驾驶室和货斗分支。
2. 解决 Nissan NV400 后驱厢式车及底盘车配置边界。
3. 处理 Fiat Scudo、Peugeot Partner、Mercedes-Benz Vario、GAZ Gazelle 等商用车轴距和车顶分支。
4. 随后处理 Pajero IV、Grand Caravan、Delica、Monte Carlo、Caprice 与 Impala。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/44720/lancia_beta_coupe_1300_2a_serie.html?utm_source=chatgpt.com "1977 Lancia Beta Coupe 1300 (2a serie) Specs Review (60.3 kW / 82 PS / 81 hp) (since mid-year 1977 for Europe )"
[2]: https://www.automobile-catalog.com/car/1980/1369610/fiat_ritmo_60_cl.html?utm_source=chatgpt.com "1980 Fiat Ritmo 60 CL Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[3]: https://www.auto-data.net/en/lincoln-town-car-iii-fn145-4.6-v8-208hp-8207?utm_source=chatgpt.com "Lincoln Town Car III (FN145) 4.6 V8 (208 Hp) /Sedan 1998"
[4]: https://www.automobile-catalog.com/car/2008/3408965/suzuki_sx4_sedan_1_6_vvt_2wd.html?utm_source=chatgpt.com "2008 Suzuki SX4 Sedan 1.6 VVT 2WD Specs Review (79 kW / 107 PS / 106 hp) (for Europe )"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 发送 / checkpoint 续跑到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 14 ---
【任务名称】
【全量表更新】all 第 601-700 行

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
all 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639
EU-MITSUBISHI-L200-V-CLUB-CAB-PICKUP-01	5195	1785	1775
EU-MITSUBISHI-L200-V-DOUBLE-CAB-PICKUP-01	5205	1785	1775
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Hyundai	Elantra vi	1.6 D	Stufenheck	Frontantrieb	Diesel	100	136	Feb 2016	Dec 2020	2024-05-01	122182
KIA	Cerato i	1.5 Crdi	Stufenheck	Frontantrieb	Diesel	66	90	Jul 2005	Dec 2009	2024-03-01	122185
KIA	Cee'd	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	91	124	Jan 2008	Sep 2012	2024-03-01	122211
KIA	Cee'd	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	95	130	Jan 2013	Jul 2018	2024-03-01	122213
KIA	Cee'd	1.6 Cvvt	Kombi	Frontantrieb	Benzin	95	130	Nov 2014	Jul 2018	2024-03-01	122217
KIA	Rio iii	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Sep 2011	Dec 2017	2024-03-01	122220
KIA	Sportage iv	2	SUV	Frontantrieb	Benzin	114	155	Dec 2015	Sep 2022	2024-03-01	122239
GAZ	Gazelle	2.4	Kasten	Heckantrieb	Benzin	66	90	Jan 2003	Mar 2013	2024-03-01	122241
KIA	Venga	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Feb 2010	Mar 2019	2024-05-01	122247
Lancia	Beta	1300	Coupe	Frontantrieb	Benzin	61	83	Jul 1977	Jan 1981	2024-03-01	122248
Hyundai	I20 active	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	74	101	Sep 2015	Jun 2018	2024-05-01	122249
KIA	Soul i	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	92	125	Feb 2009	Dec 2011	2024-03-01	122255
Honda	Civic iv	1.6 I 16V 4X4	Stufenheck	Allrad	Benzin	81	110	Jan 1989	Dec 1991	2024-03-01	122270
Honda	Accord	1.6	Schrägheck	Frontantrieb	Benzin	59	80	Jan 1978	Dec 1981	2024-03-01	122284
Honda	Element	2.4	SUV	Frontantrieb	Benzin	119	162	Jul 2002	Dec 2005	2024-03-01	122287
Honda	Element	2.4 4X4	SUV	Allrad	Benzin	119	162	Jul 2002	Dec 2005	2024-03-01	122288
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	99	135	May 1991	Mar 1995	2024-03-01	122381
Mazda	E	E2000	Bus	Heckantrieb	Benzin	60	82	Oct 1989	May 1994	2024-03-01	122392
Fiat	Scudo	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	69	Apr 1998	Dec 2006	2024-03-01	122394
Mazda	323 s v	1.5 16V	Stufenheck	Frontantrieb	Benzin	66	90	May 1994	Dec 1998	2024-03-01	122396
Mazda	Bt-50	2.5 Mrz-cd	Pick-up	Heckantrieb	Diesel	105	143	Aug 2006	Jun 2013	2024-03-01	122397
Mazda	626 ii	1.6	Coupe	Frontantrieb	Benzin	60	82	Nov 1982	Jul 1987	2024-03-01	122405
Peugeot	Partner	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	69	Jan 1999	Jul 2008	2024-03-01	122425
Peugeot	Partner	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Nov 2002	Jul 2008	2024-03-01	122426
Peugeot	3008 i	1.6 HDI 115 / Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Feb 2013	Aug 2016	2024-11-01	122430
Nissan	Nv400	DCI 130 RWD	Kasten	Heckantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122433
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	65	88	Aug 2005	Oct 2006	2024-03-01	122436
Fiat	Scudo	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	69	94	Oct 1999	Dec 2006	2024-03-01	122438
Nissan	Nv400	DCI 130	Kasten	Frontantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122439
Nissan	Nv400	DCI 170	Kasten	Frontantrieb	Diesel	125	170	Sep 2016	Dec 2022	2026-03-01	122441
Nissan	Nv400	DCI 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122443
Nissan	Nv400	DCI 130 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	130	Sep 2016	Dec 2022	2026-03-01	122445
Nissan	Nv400	DCI 170	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jun 2016	Dec 2022	2026-03-01	122450
Nissan	Nv300	1.6 DCI 95	Kasten	Frontantrieb	Diesel	70	95	Sep 2016	-	2024-03-01	122456
Nissan	Nv300	1.6 DCI 120	Kasten	Frontantrieb	Diesel	89	121	Sep 2016	-	2024-03-01	122458
Nissan	Nv300	1.6 DCI 125	Kasten	Frontantrieb	Diesel	92	125	Sep 2016	-	2024-03-01	122459
Nissan	Nv300	1.6 DCI 145	Kasten	Frontantrieb	Diesel	107	146	Sep 2016	-	2024-03-01	122462
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	81	110	Jul 2002	-	2024-03-01	122469
Nissan	Nv300 kombi	1.6 DCI 125	Bus	Frontantrieb	Diesel	92	125	Sep 2016	-	2024-03-01	122481
Nissan	Nv300 kombi	1.6 DCI 145	Bus	Frontantrieb	Diesel	107	145	Sep 2016	-	2024-03-01	122486
Dacia	Lodgy	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	81	110	Mar 2012	-	2024-03-01	122487
Renault	Thalia i	1.4	Stufenheck	Frontantrieb	Benzin	72	98	May 2000	Feb 2009	2024-03-01	122490
Renault	Dauphine	0.8	Stufenheck	Heckantrieb	Benzin	25	34	Mar 1960	Mar 1962	2024-03-01	122492
Dodge	Grand caravan	3.8	Großraumlimousine	Frontantrieb	Benzin	142	193	Jun 2007	Dec 2010	2024-03-01	122505
Fiat	Ritmo	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1980	Aug 1988	2024-03-01	122529
Mercedes-benz	Vario	815 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Sep 1996	Dec 2013	2024-03-01	122548
Wartburg	353	1	Kombi	Frontantrieb	Gemisch	37	50	Feb 1975	Jan 1989	2024-03-01	122555
Chevrolet	Captiva	2.0 D	SUV	Frontantrieb	Diesel	120	163	Jan 2011	-	2024-03-01	122575
Lincoln	Town car iii	4.6	Stufenheck	Heckantrieb	Benzin	153	208	Jan 1998	Dec 2003	2024-03-01	122589
Renault	Laguna ii	2.9 V6 24V	Schrägheck	Frontantrieb	Benzin	155	211	Mar 2001	Aug 2007	2024-03-01	122595
Mercedes-benz	Sl	560 SL	Cabriolet	Heckantrieb	Benzin	178	242	Jan 1986	Dec 1989	2024-03-01	122596
Citroën	Jumpy iii	1.6 Bluehdi 95	Bus	Frontantrieb	Diesel	70	95	Apr 2016	-	2024-03-01	122613
Citroën	Jumpy iii	1.6 Bluehdi 115	Bus	Frontantrieb	Diesel	85	116	Apr 2016	Jun 2022	2025-12-01	122614
Mitsubishi	L200	3.5 4WD	Pick-up	Allrad	Benzin	137	186	Aug 2011	Dec 2015	2024-03-01	122618
Mitsubishi	Pajero iv	3.5 V6 4WD	SUV	Allrad	Benzin	139	189	Sep 2009	-	2024-03-01	122620
Chevrolet	Monte carlo	5	Coupe	Heckantrieb	Benzin	116	158	Sep 1978	Dec 1980	2024-03-01	122622
Citroën	Spacetourer	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Dec 2019	Dec 2022	2025-12-01	122623
Citroën	Jumpy iii	2.0 Bluehdi 150	Bus	Frontantrieb	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	122624
Mitsubishi	Delica / space gear	2	Bus	Heckantrieb	Benzin	83	113	Sep 1995	Oct 2002	2024-03-01	122627
KIA	Cerato iii	2.0 MPI	Stufenheck	Frontantrieb	Benzin	112	152	Mar 2016	Jun 2018	2024-05-01	122648
Seat	Toledo	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	92	125	Nov 2007	May 2009	2024-03-01	122653
Opel	Astra h family	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2009	May 2014	2026-04-01	122662
Opel	Astra h family	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	66	90	Jan 2009	May 2014	2026-04-01	122663
Hyundai	H100	2.4	Kasten	Heckantrieb	Benzin	84	114	Aug 1997	Oct 2003	2024-03-01	122666
Aixam	Mega	0.4 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	4	5	Jan 2007	-	2024-03-01	122693
Aixam	Mega	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	4	5	Jan 2007	Dec 2011	2026-01-01	122694
Suzuki	Grand vitara ii	1.9 Ddis	Geländewagen geschlossen	Heckantrieb	Diesel	95	129	Mar 2006	Aug 2008	2024-03-01	122714
Citroën	C3 picasso	1.6 VTI 115	Großraumlimousine	Frontantrieb	Benzin	84	114	Jul 2009	Dec 2015	2024-08-01	122715
Suzuki	Sx4	1.6 AWD	Stufenheck	Allrad	Benzin	79	107	Oct 2007	Dec 2011	2025-02-03	122718
Land Rover	Range rover sport ii	2.0 SD4 4X4	SUV	Allrad	Diesel	177	241	Aug 2016	Mar 2022	2025-02-03	122731
Ford	Kuga ii	1.5 Tdci	SUV	Frontantrieb	Diesel	88	120	Jul 2016	Jun 2019	2024-03-01	122732
Honda	Cr-V iv	2.4 AWD	SUV	Allrad	Benzin	138	188	Sep 2015	Dec 2018	2025-12-01	122740
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel	143	194	Oct 2016	Oct 2023	2024-03-01	122801
Chevrolet	Caprice	5	Coupe	Heckantrieb	Benzin	110	150	Sep 1980	Dec 1984	2024-03-01	122805
Mercedes-benz	E-Klasse	E 400 4-matic	Kombi	Allrad	Benzin	245	333	Oct 2016	May 2018	2024-03-01	122807
Mercedes-benz	E-Klasse	AMG E 43 4-matic	Kombi	Allrad	Benzin	295	401	Oct 2016	May 2018	2024-03-01	122808
Mercedes-benz	E-Klasse	E 200 D	Kombi	Heckantrieb	Diesel	110	150	Oct 2016	Jun 2019	2024-03-01	122809
Mercedes-benz	E-Klasse	E 350 D	Kombi	Heckantrieb	Diesel	190	258	Oct 2016	May 2018	2024-03-01	122810
Mercedes-benz	Glc	350 D 4-matic	SUV	Allrad	Diesel	190	258	Oct 2016	Apr 2019	2024-03-01	122813
Porsche	Macan	3.6 Turbo	SUV	Allrad	Benzin	324	441	Sep 2016	-	2025-12-01	122815
Mercedes-benz	Glc	350 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Jan 2016	Apr 2019	2024-03-01	122819
Porsche	Panamera	2.9 4S	Schrägheck	Allrad	Benzin	324	440	May 2016	Dec 2023	2024-08-01	122820
Porsche	Panamera	4.0 Turbo	Schrägheck	Allrad	Benzin	404	550	May 2016	Dec 2023	2024-08-01	122821
Mercedes-benz	Glc	350 D 4-matic	SUV	Allrad	Diesel	190	258	Oct 2016	Apr 2019	2024-03-01	122822
Mercedes-benz	Glc	300 4-matic	SUV	Allrad	Benzin	180	245	Oct 2016	Apr 2019	2024-03-01	122823
Porsche	Panamera	4.0 S 4 Diesel	Schrägheck	Allrad	Diesel	310	422	May 2016	Dec 2023	2024-08-01	122824
Chevrolet	Captiva	2.2 D	SUV	Frontantrieb	Diesel	135	184	Feb 2011	Sep 2018	2025-11-01	122830
Mercedes-benz	Glc	350 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Oct 2016	Apr 2019	2024-03-01	122832
Mercedes-benz	Glc	AMG 43 4-matic	SUV	Allrad	Benzin	270	367	Oct 2016	Aug 2019	2024-03-01	122833
Porsche	Panamera	2.9 4 E-hybrid	Schrägheck	Allrad	Benzin/Elektro	340	462	May 2016	Dec 2023	2024-08-01	122834
Mercedes-benz	Glc	220 D 4-matic	SUV	Allrad	Diesel	120	163	Jun 2016	Apr 2019	2024-03-01	122836
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	150	204	Jun 2016	Aug 2020	2024-03-01	122843
Tesla	Model s	P100d AWD	Schrägheck	Allrad	Elektro	568	772	Oct 2016	Apr 2026	2026-06-01	122853
Tesla	Model x	P100d AWD	Schrägheck	Allrad	Elektro	568	772	Oct 2016	Apr 2026	2026-06-01	122855
Suzuki	Ignis iii	1.2	Schrägheck	Frontantrieb	Benzin	66	90	Oct 2016	-	2024-03-01	122890
Suzuki	Ignis iii	1.2 Allgrip	Schrägheck	Allrad	Benzin	66	90	Oct 2016	-	2024-03-01	122891
Suzuki	Ignis iii	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	66	90	Feb 2016	-	2025-06-01	122892
Suzuki	Ignis iii	1.2 Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	66	90	Feb 2016	-	2025-06-01	122893
Chevrolet	Impala	5.7	Coupe	Heckantrieb	Benzin	119	162	Sep 1973	Dec 1974	2024-03-01	122896
Volvo	S60 i	2.4 CDI	Stufenheck	Frontantrieb	Diesel	85	116	Oct 2003	Dec 2005	2024-03-01	122901


--- 新建对话（分支降级） / Round 14 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6c150b-a744-83ee-ac75-523d49366578
新对话：https://chatgpt.com/c/6a6d462a-22bc-83ee-b421-f034238d536e

--- Round 14 / checkpoint 续跑 ---
## 更新点

* 闭合 Mercedes-Benz E-Class S213 旅行车簇：普通车型与 AMG E 43 分开建组；两组均确认车宽为不含后视镜的 1852 mm，含镜宽另列为 2065 mm。([汽车数据网][1])
* 闭合 Mercedes-Benz GLC X253 改款前标准 SUV 簇，批量关联 6 个普通版本；尺寸为 4656×1890×1639 mm，其中 1890 mm 明确不含后视镜。([汽车数据网][2])
* AMG GLC 43 直接复用跨批次已有尺寸组 `EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01`，未重复创建或输出尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入：11
* PENDING 输入：89
* READY 映射：11
* 本轮新增尺寸组：3
* 当前已引用确认尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122807	122807	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122808	122808	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-AMG-E43-WAGON-01	HIGH	AMG E 43外部套件分支。	READY
122809	122809	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122810	122810	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122813	122813	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122819	122819	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122822	122822	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122823	122823	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122832	122832	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122833	122833	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH	AMG GLC 43外部套件分支。	READY
122836	122836	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell (S213) E 400 V6 3.5 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-400-v6-3.5-333hp-4matic-9g-tronic-26418
EU-MERCEDES-BENZ-E-CLASS-S213-AMG-E43-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell (S213) AMG E 43 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-43-401hp-4matic-9g-tronic-26467
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639	Auto-Data Mercedes-Benz GLC SUV (X253) GLC 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-glc-350d-258hp-4matic-g-tronic-27078
```

## 下一步优先处理

1. 闭合 Porsche Panamera G2 的改款前、改款后及可能的 Executive 长轴分支。
2. 使用官方或可核实不含镜口径的资料解决 Suzuki Ignis III 宽度冲突。
3. 批量处理 Cee'd、Rio、Sportage、Cerato 等 KIA 乘用车簇，再进入 NV300、NV400、Scudo、Partner 等多轴距商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-400-v6-3.5-333hp-4matic-9g-tronic-26418 "Mercedes-Benz E-class T-modell (S213) E 400 V6 3.5 (333 Hp) 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-glc-350d-258hp-4matic-g-tronic-27078 "Mercedes-Benz GLC SUV (X253) GLC 350d (258 Hp) 4MATIC G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Kia Cee'd SW I 跨改款分支：改款前后长度、宽度一致，但高度由 1490 mm 变为 1525 mm，因此 Ktype `122211` 拆分为 `prefl`、`facelift` 两条映射。([汽车数据网][1])
* 闭合 Cee'd II 两厢及旅行车；2015 年改款前后三维未变化，分别复用单一尺寸组。([汽车数据网][2])
* 闭合 Rio III Hatchback、Sportage IV 改款前 2.0 MPI、Honda Element、Dacia Lodgy 和 Dodge Grand Caravan。Element 前驱与四驱外廓一致，共用同一尺寸组。([汽车数据网][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：20
* PENDING 输入：80
* READY 映射：21
* 已确认并被引用尺寸组：13
* 本轮新增尺寸组：9
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122211_prefl	122211	Wagon	Cee'd I		5	EU-KIA-CEED-I-WAGON-PREFL-01	MEDIUM	2009改款前旅行车外廓。	READY
122211_facelift	122211	Wagon	Cee'd I facelift		5	EU-KIA-CEED-I-WAGON-FACELIFT-01	MEDIUM	2009改款后车高变化。	READY
122213	122213	Hatchback	Cee'd II		5	EU-KIA-CEED-II-HATCHBACK-01	HIGH		READY
122217	122217	Wagon	Cee'd II		5	EU-KIA-CEED-II-WAGON-01	HIGH		READY
122220	122220	Hatchback	Rio III	UB	5	EU-KIA-RIO-III-HATCHBACK-01	HIGH		READY
122239	122239	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	155 hp版本对应改款前外廓。	READY
122287	122287	SUV	Element I		5	EU-HONDA-ELEMENT-I-SUV-01	HIGH		READY
122288	122288	SUV	Element I		5	EU-HONDA-ELEMENT-I-SUV-01	HIGH		READY
122487	122487	MPV	Lodgy		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
122505	122505	MPV	Grand Caravan V		5	EU-DODGE-GRAND-CARAVAN-V-MPV-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I 1.6 CVVT (122 Hp)	https://www.auto-data.net/en/kia-ceed-sw-i-1.6-cvvt-122hp-42438
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift 2009 1.6 16V (126 Hp)	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.6-16v-126hp-17072
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470	Auto-Data Kia Cee'd II 1.6 GDi; Auto-Data Kia Cee'd II facelift 2015	https://www.auto-data.net/en/kia-ceed-ii-1.6-gdi-16v-135hp-17855;https://www.auto-data.net/en/kia-ceed-ii-facelift-2015-generation-5965
EU-KIA-CEED-II-WAGON-01	4505	1780	1485	Auto-Data Kia Cee'd SW II; Auto-Data Kia Cee'd SW II facelift 2015 1.6 GDI	https://www.auto-data.net/en/kia-ceed-sw-ii-generation-3930;https://www.auto-data.net/en/kia-ceed-sw-ii-facelift-2015-1.6-gdi-135hp-41653
EU-KIA-RIO-III-HATCHBACK-01	4045	1720	1455	Auto-Data Kia Rio III Hatchback UB 1.2 16V	https://www.auto-data.net/en/kia-rio-iii-hatchback-ub-1.2-16v-85hp-17052
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Auto-Data Kia Sportage IV 2.0 MPI (155 Hp)	https://www.auto-data.net/en/kia-sportage-iv-2.0-mpi-155hp-sportmatic-54522
EU-HONDA-ELEMENT-I-SUV-01	4300	1815	1788	Auto-Data Honda Element I 2.4; Auto-Data Honda Element I 2.4 4WD	https://www.auto-data.net/en/honda-element-i-2.4-160hp-automatic-56677;https://www.auto-data.net/en/honda-element-i-2.4-160hp-4wd-12136
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Auto-Data Dacia Lodgy 1.5 dCi (110 Hp)	https://www.auto-data.net/en/dacia-lodgy-1.5-dci-110hp-fap-18008
EU-DODGE-GRAND-CARAVAN-V-MPV-01	5177	2000	1750	Auto-Data Dodge Caravan V 3.8 V6 (193 Hp)	https://www.auto-data.net/en/dodge-caravan-v-3.8-v6-193hp-automatic-30983
```

## 5. 下一步优先处理

1. 批量闭合 Hyundai Elantra VI、Kia Cerato I/III、Venga、Soul I。
2. 处理 Porsche Panamera 971 各动力版本的车高及外部套件差异。
3. 随后处理 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-ceed-sw-i-1.6-cvvt-122hp-42438 "Kia Cee'd SW I 1.6 CVVT (122 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/kia-ceed-ii-1.6-gdi-16v-135hp-17855 "Kia Cee'd II 1.6 GDi 16V (135 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/kia-rio-iii-hatchback-ub-1.2-16v-85hp-17052 "Kia Rio III Hatchback (UB) 1.2 16V (85 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / checkpoint 续跑 ---
## 1. 更新点

* Hyundai Elantra VI `122182` 覆盖 2018 年改款前后两种外廓，拆分为 `prefl` 和 `facelift`；官方资料确认改款前为 4570×1800×1450 mm，改款后柴油版为 4620×1800×1440 mm。
* Kia Venga `122247` 覆盖 2014 年改款前后，车长由 4068 mm 增至 4075 mm，因此拆分为两个尺寸组；宽度和高度保持 1765×1600 mm。([汽车数据网][1])
* Kia Cerato III `122648` 对应 2016 改款后 YD 四门轿车，闭合为单一尺寸组。([汽车数据网][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：23
* PENDING 输入：77
* READY 映射：26
* 已确认并被引用尺寸组：18
* 本轮新增尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122182_prefl	122182	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	HIGH	2018改款前外廓。	READY
122182_facelift	122182	Sedan	Elantra VI facelift	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	HIGH	2018改款后车长及车高变化。	READY
122247_prefl	122247	Hatchback	Venga YN	YN	5	EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	HIGH	2014改款前外廓。	READY
122247_facelift	122247	Hatchback	Venga YN facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	2014改款后车长变化。	READY
122648	122648	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	4570	1800	1450	Hyundai Elantra AD official technical data	https://www.hyundai.hu/downloads/muszaki_adatlapok/Elantra_muszaki_adatlap.pdf
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	4620	1800	1440	Hyundai Avante official catalog	https://www.hyundai.com/content/dam/hyundai/kr/ko/html/pdf/en-cn-catalog/en-catalog/avante-catalog-eng.pdf
EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	4068	1765	1600	Auto-Data Kia Venga YN 1.4 16V	https://www.auto-data.net/en/kia-venga-yn-1.4-16v-90hp-17089
EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	4075	1765	1600	Auto-Data Kia Venga YN facelift 2014 1.4	https://www.auto-data.net/en/kia-venga-yn-facelift-2014-1.4-90hp-23781
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435	Auto-Data Kia Cerato III Sedan facelift 2016 2.0 MPI	https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046
```

## 5. 下一步优先处理

1. 闭合 Hyundai i20 Active、Kia Soul I、Suzuki SX4 Sedan 等单一乘用车外廓。
2. 批量处理 Porsche Panamera 971 的标准轴距、长轴距及动力相关车高分支。
3. 随后处理 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-venga-yn-1.4-16v-90hp-17089 "Kia Venga (YN) 1.4 16V (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046?utm_source=chatgpt.com "Specs of Kia Cerato III Sedan (facelift 2016) 2.0 MPI (152 ..."


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Hyundai i20 II Active、Kia Soul I、Suzuki SX4 I Sedan 三个单一乘用车外廓。i20 Active 为 4065×1760×1529 mm；Soul I 为 4105×1785×1661 mm；SX4 Sedan 为 4490×1730×1545 mm。([汽车数据网][1])
* 闭合 Suzuki Grand Vitara II 五门、Ford Kuga II facelift 和 Honda CR-V IV facelift 三个 SUV 外廓。Kuga 来源同时单列含镜宽度 2086 mm，落盘使用不含后视镜宽度 1838 mm。([汽车数据网][2])
* Honda CR-V 输入功率 188 hp 与资料市场版本 185 hp 存在标定差异，但车身代际、2.4 AWD 和物理外廓边界一致，映射置信度记为 `MEDIUM`。([汽车数据网][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：29
* PENDING 输入：71
* READY 映射：32
* 已确认并被引用尺寸组：24
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122249	122249	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	HIGH	Active跨界两厢外廓。	READY
122255	122255	Hatchback	Soul I		5	EU-KIA-SOUL-I-HATCHBACK-01	HIGH		READY
122714	122714	SUV	Grand Vitara II		5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	HIGH	五门长轴车身。	READY
122718	122718	Sedan	SX4 I Sedan		4	EU-SUZUKI-SX4-I-SEDAN-01	MEDIUM	四驱不改变轿车物理外廓。	READY
122732	122732	SUV	Kuga II facelift		5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
122740	122740	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-FACELIFT-SUV-01	MEDIUM	输入188 hp与资料185 hp为市场功率标定差异。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	4065	1760	1529	Auto-Data Hyundai i20 II Active 1.4	https://www.auto-data.net/en/hyundai-i20-ii-active-1.4-100hp-23643
EU-KIA-SOUL-I-HATCHBACK-01	4105	1785	1661	Auto-Data Kia Soul I 1.6	https://www.auto-data.net/en/kia-soul-i-1.6-126hp-2692
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695	Auto-Data Suzuki Grand Vitara II 5 Door 1.9 DDiS	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-1.9-ddis-129hp-16579
EU-SUZUKI-SX4-I-SEDAN-01	4490	1730	1545	Auto-Data Suzuki SX4 I Sedan 1.6 VVT	https://www.auto-data.net/en/suzuki-sx4-i-sedan-1.6-i-16v-vvt-2wd-107hp-16564
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Auto-Data Ford Kuga II facelift 1.5 TDCI	https://www.auto-data.net/en/ford-kuga-ii-facelift-2016-1.5-tdci-120hp-26011
EU-HONDA-CR-V-IV-FACELIFT-SUV-01	4557	1819	1654	Auto-Data Honda CR-V IV facelift 2.4 AWD	https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-2.4-i-vtec-185hp-awd-cvt-50947
```

## 5. 下一步优先处理

1. 闭合 Chevrolet Captiva facelift、Range Rover Sport II、Porsche Macan 等 SUV 簇。
2. 处理 Porsche Panamera 971 标准轴距动力版本及车高差异。
3. 随后集中处理 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/hyundai-i20-ii-active-1.4-100hp-23643 "Hyundai i20 II Active 1.4 (100 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/ford-kuga-ii-facelift-2016-1.5-tdci-120hp-26011 "Ford Kuga II (facelift 2016) 1.5 TDCI (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-2.4-i-vtec-185hp-awd-cvt-50947 "Honda CR-V IV (facelift 2014) 2.4 i-VTEC (185 Hp) AWD CVT | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Porsche Macan 95B 的 324 kW 版本。该功率与 2016 年 9 月发布的 **Macan Turbo with Performance Package** 一致，并按其独立悬架高度及外部套件建组。([Porsche Newsroom][1])
* 闭合 Porsche Panamera 971 标准轴距簇：4S、4S Diesel 与 4 E-Hybrid 共用 5049×1937×1423 mm 外廓。([Porsche Newsroom][2])
* Panamera Turbo 标准轴距车型因官方车高为 1427 mm，与其他标准轴距版本分开建组。([Porsche Newsroom][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：34
* PENDING 输入：66
* READY 映射：37
* 已确认并被引用尺寸组：27
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122815	122815	SUV	Macan I	95B	5	EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	HIGH	324 kW Turbo Performance Package外廓。	READY
122820	122820	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
122821	122821	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	HIGH	Turbo标准车高分支。	READY
122824	122824	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
122834	122834	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600	Porsche Newsroom 2017 Macan Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A5c3a8aab-ba1b-4372-8052-bf157517f993/2017_Macan_Models_Technical_Data.pdf
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423	Porsche Newsroom 2017 Panamera press kit; Porsche Newsroom 2018 Panamera Technical Information	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf;https://newsroom.porsche.com/dam/jcr%3Ac629e2c4-a8db-46ad-9a14-3e9b59a3cc90/2018_Porsche_Panamera_Technical_Information.pdf
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427	Porsche Newsroom 2017 Panamera press kit	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf
```

## 5. 下一步优先处理

1. 闭合 Chevrolet Captiva 2011–2018 改款阶段及 Range Rover Sport II。
2. 处理 Tesla Model S、Model X 中跨多次改款的物理外廓分支。
3. 随后集中拆解 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://newsroom.porsche.com/en/products/porsche-macan-turbo-performance-package-12842.html?utm_source=chatgpt.com "Macan Turbo with Performance Package"
[2]: https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf?utm_source=chatgpt.com "2017 Porsche Panamera"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Volvo 940 四门轿车、Volvo S60 I 四门轿车及 Mazda 323 S V（BA）四门轿车。输入中的功率与资料存在地区标定差异，但车身代际和物理外廓边界一致。([汽车数据网][1])
* 闭合 Opel Astra H facelift 五门两厢尺寸组；1.6 汽油和 1.3 CDTI 两个 Ktype 的三维均为 4249×1753×1460 mm，复用同一尺寸组。([汽车数据网][2])
* 闭合 Peugeot 3008 I facelift 和 Mercedes-Benz SL R107 facelift。3008 页面将 1837 mm 与含镜宽度 2113 mm 分列，落盘采用不含后视镜宽度。([汽车数据网][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：41
* PENDING 输入：59
* READY 映射：44
* 已确认并被引用尺寸组：33
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122381	122381	Sedan	Volvo 940	944	4	EU-VOLVO-940-944-SEDAN-01	MEDIUM		READY
122396	122396	Sedan	Mazda 323 S V	BA	4	EU-MAZDA-323-BA-SEDAN-01	MEDIUM		READY
122430	122430	MPV	Peugeot 3008 I facelift		5	EU-PEUGEOT-3008-I-FACELIFT-MPV-01	HIGH		READY
122596	122596	Convertible	SL R107 facelift	R107	2	EU-MERCEDES-BENZ-SL-R107-FACELIFT-CONVERTIBLE-01	MEDIUM		READY
122662	122662	Hatchback	Astra H facelift		5	EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	HIGH		READY
122663	122663	Hatchback	Astra H facelift		5	EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	HIGH		READY
122901	122901	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-01	MEDIUM		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-940-944-SEDAN-01	4871	1750	1425	Auto-Data Volvo 940 (944) 2.3i	https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420	Auto-Data Mazda 323 S V (BA) 1.5i 16V	https://www.auto-data.net/en/mazda-323-s-v-ba-1.5i-16v-88hp-11160
EU-PEUGEOT-3008-I-FACELIFT-MPV-01	4365	1837	1635	Auto-Data Peugeot 3008 I Phase II 1.6 HDi	https://www.auto-data.net/en/peugeot-3008-i-phase-ii-2013-1.6-hdi-115hp-fap-19764
EU-MERCEDES-BENZ-SL-R107-FACELIFT-CONVERTIBLE-01	4580	1790	1300	Auto-Data Mercedes-Benz SL R107 facelift 560 SL	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-560-sl-cat-v8-230hp-automatic-43219
EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	4249	1753	1460	Auto-Data Opel Astra H facelift 1.6 ECOTEC;Auto-Data Opel Astra H facelift 1.3 CDTI	https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-ecotec-115hp-47448;https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.3-cdti-ecotec-90hp-47452
EU-VOLVO-S60-I-SEDAN-01	4576	1804	1428	Auto-Data Volvo S60 2.4 D	https://www.auto-data.net/en/volvo-s60-2.4-d-130hp-9219
```

## 5. 下一步优先处理

1. 闭合 Honda Civic IV、Honda Accord I、Mazda 626 II、Lancia Beta 等历史乘用车外廓。
2. 处理 Chevrolet Captiva、Range Rover Sport II 和 Tesla 跨改款派生分支。
3. 随后集中拆解 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286 "Volvo 940 (944) 2.3i (131 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-ecotec-115hp-47448 "Opel Astra H (facelift 2007) 1.6 ECOTEC (115 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/peugeot-3008-i-phase-ii-2013-1.6-hdi-115hp-fap-19764 "Peugeot 3008 I (Phase II, 2013) 1.6 HDi (115 Hp) FAP | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Honda Civic IV 欧洲版 1.6i 16V 4WD 四门轿车，以及 Honda Accord I 1.6 EX 三门掀背车；对应三维分别为 4230×1690×1360 mm 和 4125×1620×1335 mm。([汽车目录][1])
* 闭合 1977 年起的 Lancia Beta Coupé 1300。资料确认其为 BC 系列双门 Coupe，三维为 3995×1650×1285 mm。([encyCARpedia][2])
* 闭合 Mazda 626 II GC 双门 Coupe 与 Wartburg 353 Tourist 五门旅行车；宽度均采用不含后视镜口径。([Ultimate Specs][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：46
* PENDING 输入：54
* READY 映射：49
* 已确认并被引用尺寸组：38
* 本轮新增尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122248	122248	Coupe	Beta Coupe	BC	2	EU-LANCIA-BETA-BC-COUPE-01	HIGH		READY
122270	122270	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-01	HIGH	欧洲4WD四门轿车外廓。	READY
122284	122284	Hatchback	Accord I	SJ	3	EU-HONDA-ACCORD-I-HATCHBACK-01	HIGH		READY
122405	122405	Coupe	626 II	GC	2	EU-MAZDA-626-II-GC-COUPE-01	HIGH		READY
122555	122555	Wagon	Wartburg 353	353	5	EU-WARTBURG-353-TOURIST-WAGON-01	HIGH	Tourist五门旅行车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-BETA-BC-COUPE-01	3995	1650	1285	EncyCARpedia 1977 Lancia Beta Coupe 1300	https://www.encycarpedia.com/lancia/77-beta-coupe-1300
EU-HONDA-CIVIC-IV-SEDAN-01	4230	1690	1360	Automobile-Catalog 1989 Honda Civic EX 1.6i-16 4WD;Auto-Data Honda Civic IV 1.6i 16V 4x4	https://www.automobile-catalog.com/car/1989/1101950/honda_civic_ex_1_6i-16_4wd_cat.html;https://www.auto-data.net/en/honda-civic-iv-1.6i-16v-4x4-109hp-12279
EU-HONDA-ACCORD-I-HATCHBACK-01	4125	1620	1335	Auto-Data Honda Accord I Hatchback 1.6 EX SJ	https://www.auto-data.net/en/honda-accord-i-hatchback-sj-sy-1.6-ex-sj-80hp-12111
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1350	UltimateSpecs Mazda 626 II Coupe;Automobile-Catalog 1983 Mazda 626 1.6 LX Coupe	https://www.ultimatespecs.com/car-specs/Mazda/M1241/626-II-Coupe;https://www.automobile-catalog.com/car/1983/1626125/mazda_626_1_6_lx_coupe.html
EU-WARTBURG-353-TOURIST-WAGON-01	4380	1640	1495	Automobile-Catalog 1987 Wartburg 353 W Tourist	https://www.automobile-catalog.com/car/1987/50015/wartburg_353_w_tourist.html
```

## 5. 下一步优先处理

1. 闭合 Renault Thalia I、Laguna II、Fiat Ritmo 和 Citroën C8 等普通乘用车及 MPV。
2. 拆分 Chevrolet Captiva、Range Rover Sport II、Tesla Model S/X 的跨改款外廓。
3. 集中处理 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/1101950/honda_civic_ex_1_6i-16_4wd_cat.html?utm_source=chatgpt.com "1989 Honda Civic EX 1.6i-16 4WD catalyst Specs Review (81 kW / 110 PS / 109 hp) (since mid-year 1989 for Europe Switzerland)"
[2]: https://www.encycarpedia.com/lancia/77-beta-coupe-1300 "Lancia Beta Coupé 1300 specs (1977-1982), performance, dimensions & technical specifications - encyCARpedia"
[3]: https://www.ultimatespecs.com/car-specs/Mazda/M1241/626-II-Coupe "Specs for all Mazda 626 II Coupe versions"


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Tesla Model S P100D 对应的 2016–2020 年改款外廓。官方车主手册给出的三维为 4970×1964×1445 mm，其中 1964 mm 明确为不含后视镜宽度。([Tesla][1])
* 闭合 Tesla Model X P100D 对应的初代外廓。官方车主手册给出的三维为 5052×1999×1684 mm，其中 1999 mm 为不含后视镜宽度；输入的 `Schrägheck` 按实际车型形态标准化为 `SUV`。([Tesla][2])
* Suzuki Ignis III 暂未建组：早期官方资料为 3700×1660×1595 mm，而改款资料同时存在 1660 mm 与带轮拱扩展的 1690 mm 宽度分支；改款前宽体配置边界尚未完全闭合，本轮不创建猜测性派生行。([全球铃木][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：48
* PENDING 输入：52
* READY 映射：51
* 已确认并被引用尺寸组：40
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122853	122853	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	P100D对应2016–2020量产外廓。	READY
122855	122855	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	输入车身形式标准化为SUV。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	4970	1964	1445	Tesla Model S 2012-2020 Owner's Manual	https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-TESLA-MODEL-X-I-SUV-01	5052	1999	1684	Tesla Model X 2015-2020 Owner's Manual	https://www.tesla.com/ownersmanual/2015_2020_modelx/en_il/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
```

## 5. 下一步优先处理

1. 闭合 Suzuki Ignis III 改款前窄体、宽体配置边界，批量处理 4 个相关 Ktype。
2. 处理 Renault Thalia I、Laguna II、Citroën C8 等单一乘用车及 MPV 外廓。
3. 随后集中处理 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车分支。

推进信号：CONTINUE

[1]: https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html?utm_source=chatgpt.com "Dimensions and Weights"
[2]: https://www.tesla.com/ownersmanual/2015_2020_modelx/en_il/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html?utm_source=chatgpt.com "Dimensions"
[3]: https://www.globalsuzuki.com/globalnews/2017/0419.html?utm_source=chatgpt.com "Suzuki at the Auto Shanghai 2017"


--- 发送 / 继续到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Renault Thalia I 1.4 16V：2002 年改款使车长由 4150 mm 增至 4171 mm、车高由 1416 mm 增至 1437 mm，Ktype `122490` 拆分为改款前后两个物理分支。([汽车数据网][1])
* 闭合 Renault Laguna II 五门掀背车和 Seat Toledo III 5P 外廓；Laguna II 为 4576×1772×1429 mm，Toledo III 为 4458×1768×1568 mm。([汽车数据网][2])
* 闭合 Renault Dauphine Gordini 欧洲版四门轿车；输入的 34 hp 对应约 33.5 hp 的 Gordini 版本，外廓为 3945×1520×1440 mm。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：52
* PENDING 输入：48
* READY 映射：56
* 已确认并被引用尺寸组：45
* 本轮新增尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122490_prefl	122490	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-PREFL-01	HIGH	2002改款前轿车外廓。	READY
122490_facelift	122490	Sedan	Thalia I facelift		4	EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	HIGH	2002改款后车长及车高变化。	READY
122492	122492	Sedan	Dauphine Gordini		4	EU-RENAULT-DAUPHINE-GORDINI-SEDAN-01	HIGH	34 hp输入对应Dauphine Gordini版本。	READY
122595	122595	Hatchback	Laguna II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-01	MEDIUM	输入211 hp与资料207 hp为市场功率标定差异。	READY
122653	122653	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	MEDIUM	5P五门高顶车身外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-THALIA-I-SEDAN-PREFL-01	4150	1639	1416	Auto-Data Renault Clio Symbol I 1.4 i 16V	https://www.auto-data.net/en/renault-clio-symbol-i-1.4-i-16v-98hp-10429
EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 1.4 16V	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-1.4-16v-98hp-10663
EU-RENAULT-DAUPHINE-GORDINI-SEDAN-01	3945	1520	1440	Automobile-Catalog 1960 Renault Dauphine Gordini	https://www.automobile-catalog.com/car/1960/2922830/renault_dauphine_gordini.html
EU-RENAULT-LAGUNA-II-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II 3.0 V6 24V	https://www.auto-data.net/en/renault-laguna-ii-3.0-v6-24v-207hp-10332
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data Seat Toledo III 5P	https://www.auto-data.net/en/seat-toledo-iii-5p-generation-2911
```

## 5. 下一步优先处理

1. 闭合 Chevrolet Captiva 2011–2018、Range Rover Sport II 等跨改款 SUV 分支。
2. 处理 Kia Cerato I、Mazda E2000、Hyundai H100 等尚未闭合的单一车身。
3. 集中拆解 NV300、NV400、Scudo、Partner 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-clio-symbol-i-1.4-i-16v-98hp-10429 "Renault Clio Symbol I 1.4 i 16V (98 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/se/renault-laguna-ii-3.0-v6-24v-207hp-10332 "Renault Laguna II 3.0 V6 24V (207 hk) | Tekniska data, bränsleförbrukning, Mått"
[3]: https://www.automobile-catalog.com/car/1960/2922830/renault_dauphine_gordini.html?utm_source=chatgpt.com "1960 Renault Dauphine Gordini Specs Review (24.6 kW / 33.5 PS / 33 hp) (for Europe )"


--- 发送 / 继续到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Kia Cerato I 四门轿车；输入的 90 hp 与可追溯欧洲规格 102 hp 存在市场标定差异，但 `LD` 代际及四门外廓一致。([汽车数据网][1])
* 闭合 Chevrolet Captiva I facelift 柴油簇，163 hp 与 184 hp 共用车身尺寸组。官方规格将基础车宽 1849 mm 与带侧踏板宽度 1868 mm、基础车高 1727 mm 与带车顶行李架高度 1756 mm 分列，本组采用不含侧踏板、无附加行李架的量产车身尺寸。([Dezo's Garage][2])
* 闭合 Lincoln Town Car III `153 kW / 208 hp` 标准轴距外廓；该功率对应 1998 年初期 FN145 车身，不按输入的异常结束年月扩展到后期高功率改款。([汽车数据网][3])
* 闭合 Mercedes-Benz E-Class W213 E 220 d 4MATIC 四门轿车，车宽 1852 mm 明确区别于含镜宽度 2065 mm。([汽车数据网][4])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：57
* PENDING 输入：43
* READY 映射：61
* 已确认并被引用尺寸组：49
* 本轮新增尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122185	122185	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-01	MEDIUM	输入90 hp与可追溯资料102 hp存在市场功率标定差异。	READY
122575	122575	SUV	Captiva I facelift		5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	MEDIUM	输入2.0 D名称与120 kW/163 hp官方2.2柴油规格不一致。	READY
122589	122589	Sedan	Town Car III	FN145	4	EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	MEDIUM	153 kW/208 hp锁定初期标准轴距外廓。	READY
122801	122801	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH		READY
122830	122830	SUV	Captiva I facelift		5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CERATO-I-LD-SEDAN-01	4480	1735	1470	Auto-Data Kia Cerato I Sedan 1.5 CRDi	https://www.auto-data.net/en/kia-cerato-i-sedan-1.5-crdi-102hp-32546
EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	4673	1849	1727	Chevrolet Captiva 2014 UK official brochure (archived)	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Captiva-UK.pdf
EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	5470	1985	1470	Auto-Data Lincoln Town Car III FN145 4.6 V8	https://www.auto-data.net/en/lincoln-town-car-iii-fn145-4.6-v8-208hp-8207
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-220d-194hp-4matic-9g-tronic-29551
```

## 5. 下一步优先处理

1. 闭合 Citroën C3 Picasso 改款前后宽度边界、Citroën C8 和 Fiat Ritmo。
2. 批量处理 Jumpy III、Spacetourer 与 NV300 的 XS/M/XL、低顶/高顶分支，并优先复用已有 Jumpy III 尺寸组。
3. 随后拆解 NV400、Scudo、Partner、Vario 等多轴距底盘及厢式车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-cerato-i-sedan-1.5-crdi-102hp-32546?utm_source=chatgpt.com "Specs of Kia Cerato I Sedan 1.5 CRDi (102 Hp) /2005, 2006"
[2]: https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Captiva-UK.pdf "Chevrolet Print PDF"
[3]: https://www.auto-data.net/en/lincoln-town-car-iii-fn145-4.6-v8-208hp-8207?utm_source=chatgpt.com "Lincoln Town Car III (FN145) 4.6 V8 (208 Hp) /Sedan 1998"
[4]: https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-220d-194hp-4matic-9g-tronic-29551?utm_source=chatgpt.com "Mercedes-Benz E-class (W213) E 220d (194 Hp) 4MATIC ..."


--- 发送 / 继续到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 24 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Citroën C8 2.0 HDi 五门 MPV，官方技术规格给出 4726×1854×1856 mm；1854 mm 为车身宽度，另列含后视镜宽度 2194 mm。([Dezo's Garage][1])
* 闭合 Suzuki Ignis III（MF）尺寸边界。官方车型表确认普通 `1.2 Dualjet` 同时覆盖 1660 mm 的 SZ3 窄体和带轮拱扩展的 1690 mm SZ-T 宽体，因此 `122890` 拆为两个物理分支；Allgrip 与 Hybrid 相关版本均关联 1690 mm 宽体组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：62
* PENDING 输入：38
* READY 映射：67
* 已确认并被引用尺寸组：52
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122469	122469	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH		READY
122890_narrow	122890	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	HIGH	SZ3无轮拱扩展窄体外廓。	READY
122890_widebody	122890	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	SZ-T轮拱扩展宽体外廓。	READY
122891	122891	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Allgrip宽体外廓。	READY
122892	122892	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Hybrid宽体外廓。	READY
122893	122893	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Hybrid Allgrip宽体外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C8-I-MPV-01	4726	1854	1856	Citroën C8 2002 UK official technical specification	https://xr793.org/wp-content/uploads/2022/09/2002-Citroen-C8-Tech-Specs-UK.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	3700	1660	1595	Suzuki Ignis UK official brochure	https://www.autosynergy.co.uk/assets/brochures/suzuki-ignis.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	3700	1690	1595	Suzuki Ignis UK official brochure	https://www.autosynergy.co.uk/assets/brochures/suzuki-ignis.pdf
```

## 5. 下一步优先处理

1. 闭合 Citroën Jumpy III、Spacetourer 与 Nissan NV300 的 XS/M/XL 分支，优先匹配并复用已有 Jumpy III 尺寸组。
2. 处理 Mitsubishi L200、Toyota Hilux VII、Mazda BT-50 与 VW Amarok 的驾驶室和货斗外廓。
3. 随后集中拆解 Nissan NV400、Fiat Scudo、Peugeot Partner、Mercedes-Benz Vario 等多轴距商用车。

推进信号：CONTINUE

[1]: https://xr793.org/wp-content/uploads/2022/09/2002-Citroen-C8-Tech-Specs-UK.pdf "Xsara, 012"


--- 发送 / 继续到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 25 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Chevrolet Monte Carlo 第三代 5.0 V8 双门 Coupe。1979 年 119 kW/162 PS 与 1980 年约 116 kW/157 PS 版本的外廓均为 5090×1816×1369 mm，可使用同一尺寸组。([汽车目录][1])
* 闭合 Volkswagen Amarok I 2016 facelift Double Cab 3.0 V6 TDI 204 hp 4MOTION。资料明确为四门 Double Cab，尺寸为 5254×1954×1834 mm，另列含镜宽度 2228 mm，因此落盘宽度使用 1954 mm。([汽车数据网][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：64
* PENDING 输入：36
* READY 映射：69
* 已确认并被引用尺寸组：54
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122622	122622	Coupe	Monte Carlo III		2	EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	HIGH	第三代双门Coupe外廓。	READY
122843	122843	Pickup	Amarok I facelift		4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	Double Cab外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	5090	1816	1369	Automobile-Catalog 1979 Chevrolet Monte Carlo 5.0L V8;Automobile-Catalog 1980 Chevrolet Monte Carlo 5.0L V8	https://www.automobile-catalog.com/car/1979/204920/chevrolet_monte_carlo_5_0l_v-8_automatic.html;https://www.automobile-catalog.com/car/1980/205115/chevrolet_monte_carlo_5_0l_v-8_automatic.html
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834	Auto-Data Volkswagen Amarok I Double Cab facelift 3.0 V6 TDI 204 4MOTION	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-204hp-4motion-automatic-27099
```

## 5. 下一步优先处理

1. 闭合 Range Rover Sport II 2017 款与 2018 facelift 的外廓变化分支。
2. 处理 Citroën C3 Picasso 改款前后长度和标准车高口径。
3. 批量处理 Jumpy III、Spacetourer、NV300，并优先复用已有 Jumpy III 尺寸组。
4. 最后集中拆解 NV400、Scudo、Partner、Vario 等多轴距、多车顶商用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/204920/chevrolet_monte_carlo_5_0l_v-8_automatic.html?utm_source=chatgpt.com "1979 Chevrolet Monte Carlo 5.0L V-8 automatic Specs Review (119 kW / 162 PS / 160 hp) (since September 1978 for North America U.S.)"
[2]: https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-204hp-4motion-automatic-27099 "Volkswagen Amarok I Double Cab (facelift 2016) 3.0 V6 TDI (204 Hp) 4MOTION Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 26 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 26 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Citroën C3 Picasso 1.6 VTi 115 改款前外廓；84 kW/115 hp 动力仅对应 Phase I，采用 4078×1766×1669 mm，1766 mm 为不含后视镜宽度。([汽车数据网][1])
* 闭合 Mitsubishi Delica / Space Gear 2.0 欧洲后驱短轴五门 MPV；对应 L400、83 kW/113 PS 版本为 4655×1695×1855 mm，来源明确标注宽度不含后视镜。([汽车目录][2])
* Fiat Ritmo 1.1 的输入期跨越前期与改款车型，并同时覆盖三门、五门车身；拆为四个稳定物理分支。前期为 3937×1650×1400 mm，改款后为 3993×1650×1418 mm。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：67
* PENDING 输入：33
* READY 映射：75
* 已确认并被引用尺寸组：60
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122529_prefl_3dr	122529	Hatchback	Ritmo I pre-facelift	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	MEDIUM	前期三门车身分支。	READY
122529_prefl_5dr	122529	Hatchback	Ritmo I pre-facelift	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	MEDIUM	前期五门车身分支。	READY
122529_facelift_3dr	122529	Hatchback	Ritmo I facelift	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	MEDIUM	改款后三门车身分支。	READY
122529_facelift_5dr	122529	Hatchback	Ritmo I facelift	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	MEDIUM	改款后五门车身分支。	READY
122627	122627	MPV	Delica Space Gear	L400	5	EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	HIGH	欧洲后驱五门车身。	READY
122715	122715	MPV	C3 Picasso I pre-facelift		5	EU-CITROEN-C3-PICASSO-I-PREFL-MPV-01	MEDIUM	84kW/115hp动力对应改款前车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 CL	https://www.automobile-catalog.com/car/1980/1369610/fiat_ritmo_60_cl.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	3993	1650	1418	Automobile-Catalog 1987 Fiat Ritmo 60 CL	https://www.automobile-catalog.com/car/1987/714680/fiat_ritmo_60_l_5-speed.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	3993	1650	1418	Automobile-Catalog 1987 Fiat Ritmo 60 L	https://www.automobile-catalog.com/car/1987/714665/fiat_ritmo_60_l.html
EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	4655	1695	1855	Automobile-Catalog 1999 Mitsubishi Space Gear 2000 GLX	https://www.automobile-catalog.com/car/1999/2020010/mitsubishi_space_gear_2000_glx.html
EU-CITROEN-C3-PICASSO-I-PREFL-MPV-01	4078	1766	1669	Auto-Data Citroën C3 I Picasso Phase I 1.6 VTi 115	https://www.auto-data.net/en/citroen-c3-i-picasso-phase-i-2008-1.6-vti-115hp-27454
```

## 5. 下一步优先处理

1. 闭合 Range Rover Sport II 改款前后高度口径冲突后，拆分 `122731`。
2. 批量处理 Jumpy III、Spacetourer 与 NV300，优先复用累计表中已有 Jumpy III 尺寸组。
3. 处理 L200、Hilux VII、BT-50 的驾驶室和货斗分支。
4. 最后集中拆解 NV400、Scudo、Partner、Vario 等多轴距商用车。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-c3-i-picasso-phase-i-2008-1.6-vti-115hp-27454 "Citroen C3 I Picasso (Phase I, 2008) 1.6 VTi (115 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2000/2020010/mitsubishi_space_gear_2000_glx.html?utm_source=chatgpt.com "2000 Mitsubishi Space Gear 2000 GLX Specs Review (83 kW / 113 PS / 111 hp) (up to August 2000 for Europe )"
[3]: https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html?utm_source=chatgpt.com "1980 Fiat Ritmo 60 Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"


--- 发送 / 继续到 Round 27 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 27 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Nissan NV300 I 厢式车簇。官方 brochure 确认：

  * `dCi 95`、`dCi 120`：覆盖 `L1H1`、`L2H1`。
  * `dCi 125`、`dCi 145`：覆盖 `L1H1`、`L1H2`、`L2H1`、`L2H2`。
* 闭合 NV300 Combi 125/145 分支，均覆盖 `L1H1`、`L2H1`。Combi 与同长度低顶厢式车的外部三维一致，直接复用相同尺寸组，不重复建组。
* 四个尺寸组均由 Nissan 官方资料明确区分车身宽度与含镜宽度；落盘统一采用不含后视镜的 `1956 mm`。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：73
* PENDING 输入：27
* READY 映射：91
* 已确认并被引用尺寸组：64
* 本轮新增尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122456_l1h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122456_l2h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122458_l1h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122458_l2h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122459_l1h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122459_l1h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2高顶短轴物理分支。	READY
122459_l2h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122459_l2h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2高顶长轴物理分支。	READY
122462_l1h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122462_l1h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2高顶短轴物理分支。	READY
122462_l2h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122462_l2h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2高顶长轴物理分支。	READY
122481_l1h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1短轴Combi物理分支。	READY
122481_l2h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1长轴Combi物理分支。	READY
122486_l1h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1短轴Combi物理分支。	READY
122486_l2h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1长轴Combi物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L1H2-01	4999	1956	2493	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L2H2-01	5399	1956	2490	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
```

## 5. 下一步优先处理

1. 批量关联 Jumpy III 与 SpaceTourer 的 XS/M/XL 分支，优先复用累计表已有 Jumpy III 尺寸组。
2. 拆解 Range Rover Sport II 改款前后、Mitsubishi Pajero IV 三门/五门边界。
3. 处理 L200、Hilux VII、BT-50 的驾驶室分支。
4. 最后集中处理 NV400、Scudo、Partner、Vario 等多轴距商用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 28 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 28 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Citroën SpaceTourer 2.0 BlueHDi 120 的 `M`、`XL` 两个物理分支。该动力自 2019 年投入生产，官方车型范围包含 M 与 XL；两种车长均明确区分车身宽度 1920 mm 与含后视镜宽度 2204 mm。([Stellantis Media][1])
* 现有 Jumpy III 缓存组与 SpaceTourer 当前配置的高度不同，本轮未强行复用，新增两个独立尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：74
* PENDING 输入：26
* READY 映射：93
* 已确认并被引用尺寸组：66
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122623_m	122623	MPV	SpaceTourer I		5	EU-CITROEN-SPACETOURER-I-MPV-M-01	HIGH	M车长物理分支。	READY
122623_xl	122623	MPV	SpaceTourer I		5	EU-CITROEN-SPACETOURER-I-MPV-XL-01	HIGH	XL车长物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920	Citroën UK Stellantis Media;Auto-Data Citroën SpaceTourer M 2.0 BlueHDi 120	https://www.media.stellantis.com/uk-en/citroen/press/new-engine-gearbox-option-for-citroen-spacetourer-mpv;https://www.auto-data.net/en/citroen-spacetourer-m-2.0-bluehdi-120hp-s-s-automatic-46442
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920	Citroën UK Stellantis Media;Auto-Data Citroën SpaceTourer XL 2.0 BlueHDi 120	https://www.media.stellantis.com/uk-en/citroen/press/new-engine-gearbox-option-for-citroen-spacetourer-mpv;https://www.auto-data.net/en/citroen-spacetourer-xl-2.0-bluehdi-120hp-s-s-automatic-46443
```

## 5. 下一步优先处理

1. 按缓存优先模式关联 Jumpy III 1.6 BlueHDi 95、115 和 2.0 BlueHDi 150 的 XS/M/XL 及高度分支。
2. 闭合 Range Rover Sport II 改款前后、Pajero IV 三门/五门边界。
3. 处理 L200、Hilux VII、BT-50 的驾驶室分支。
4. 最后集中拆解 NV400、Scudo、Partner、Vario 等多轴距商用车。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/citroen/press/new-engine-gearbox-option-for-citroen-spacetourer-mpv "NEW ENGINE & GEARBOX OPTION FOR CITROËN SPACETOURER MPV  | Citroën | Stellantis Media"


--- 发送 / 继续到 Round 29 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 29 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Range Rover Sport II `122731` 的改款前后外廓。240 PS SD4 于 2017 车型年引入，并延续到 2018 年改款车型；改款后车长由 4850 mm 增至 4879 mm，车身宽度与标准车高保持 1983×1780 mm，因此拆分为两个尺寸组。([路虎媒体中心][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：75
* PENDING 输入：25
* READY 映射：95
* 已确认并被引用尺寸组：68
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122731_prefl	122731	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	2017车型年改款前外廓。	READY
122731_facelift	122731	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	2018车型年改款后车长变化。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780	Land Rover Media 2017 Model Year Range Rover Sport;Automobile-Catalog 2017 Range Rover Sport 2.0 SD4	https://media.landrover.com/news/2016/08/new-engine-and-advanced-technology-range-rover-sport;https://www.automobile-catalog.com/car/2017/2564720/range-rover_sport_2_0_sd4.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Land Rover Range Rover Sport 2018 official brochure;Automobile-Catalog 2018 Range Rover Sport 2.0 SD4	https://stewartsautogroup.com/wp-content/uploads/2016/11/Range-Rover-Sport-Brochure-2018.pdf;https://www.automobile-catalog.com/car/2018/2606930/range-rover_sport_2_0_sd4.html
```

## 5. 下一步优先处理

1. 按已有尺寸组关联 Jumpy III 1.6 BlueHDi 95、115 与 2.0 BlueHDi 150 的 XS/M/XL 分支。
2. 闭合 Pajero IV 三门/五门及 L200、Hilux VII、BT-50 驾驶室分支。
3. 集中处理 NV400、Scudo、Partner、Vario 等多轴距商用车。

推进信号：CONTINUE

[1]: https://media.landrover.com/news/2016/08/new-engine-and-advanced-technology-range-rover-sport?utm_source=chatgpt.com "NEW ENGINE AND ADVANCED TECHNOLOGY FOR ..."


--- 发送 / 继续到 Round 30 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 30 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Citroën Jumpy III Kombi 的 3 个 Ktype。官方资料确认 Jumpy Kombi 提供 XS、M、XL 三种长度，并同时提供 BlueHDi 95、115、150 动力；XS/M 为约 1.90 m 车高，XL 对应既有 1940 mm 组，因此全部直接关联累计缓存中的 XS 低顶、M 低顶和 XL 尺寸组。([Stellantis Media][1])
* 本轮仅建立 Ktype 与既有尺寸组的关联，没有重新抓取三维或创建尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：78
* PENDING 输入：22
* READY 映射：104
* 已确认并被引用尺寸组：68
* 本轮新增尺寸组：0
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122613_xs	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122613_m	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122613_xl	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
122614_xs	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122614_m	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122614_xl	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
122624_xs	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122624_m	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122624_xl	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 闭合 Mitsubishi Pajero IV 三门与五门、L200 驾驶室分支。
2. 处理 Toyota Hilux VII 与 Mazda BT-50 的 Single、Extra/Freestyle、Double Cab 外廓。
3. 集中拆解 Nissan NV400 的 L1/L2/L3/L4 与 H1/H2/H3 厢式车、底盘分支。
4. 最后处理 Fiat Scudo、Peugeot Partner、Mercedes-Benz Vario 等剩余商用车。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/de-de/citroen/press/neuer-citroen-jumpy-kombi-ab-29-490-euro "Neuer Citroën Jumpy Kombi ab 29.490 Euro | Citroën | Stellantis Media"


--- 发送 / 继续到 Round 31 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 31 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Mitsubishi Pajero IV 3.5 V6 4WD 的三门和五门物理分支。官方规格确认 3.5 V6 同时用于 `V85W` 三门和 `V95W` 五门：三门为 4385×1875×1850 mm，五门为 4900×1875×1870 mm，车高均采用不含选装车顶行李架的标准值。([哈布图汽车][1])
* 闭合 Chevrolet Impala IV 1974 款 5.7 350-4 双门 Coupe。输入的 119 kW/162 hp 对应约 119.5 kW/163 PS 版本，三维为 5657×2019×1364 mm，宽度明确为不含后视镜。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：80
* PENDING 输入：20
* READY 映射：107
* 已确认并被引用尺寸组：71
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122620_3dr	122620	SUV	Pajero IV	V85W	3	EU-MITSUBISHI-PAJERO-IV-V85W-SUV-3D-01	HIGH	3.5 V6三门短轴物理分支。	READY
122620_5dr	122620	SUV	Pajero IV	V95W	5	EU-MITSUBISHI-PAJERO-IV-V95W-SUV-5D-01	HIGH	3.5 V6五门长轴物理分支。	READY
122896	122896	Coupe	Impala IV		2	EU-CHEVROLET-IMPALA-IV-COUPE-1974-01	HIGH	1974款双门硬顶Coupe外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-IV-V85W-SUV-3D-01	4385	1875	1850	Mitsubishi Pajero official specification brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-V95W-SUV-5D-01	4900	1875	1870	Mitsubishi Pajero official specification brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-CHEVROLET-IMPALA-IV-COUPE-1974-01	5657	2019	1364	Automobile-Catalog 1974 Chevrolet Impala Custom Coupe 350-4 V8	https://www.automobile-catalog.com/car/1974/116960/chevrolet_impala_custom_coupe_350-4_v-8_turbo-fire_hydra-matic.html
```

## 5. 下一步优先处理

1. 闭合 Mitsubishi L200 IV 3.5 V6、Toyota Hilux VII 2.5 D-4D 与 Mazda BT-50 I 的驾驶室分支。
2. 集中处理 Nissan NV400 的 L1/L2/L3/L4、H1/H2/H3 厢式车及底盘分支。
3. 处理 Fiat Scudo、Peugeot Partner、Mercedes-Benz Vario 等多轴距底盘车型。
4. 最后闭合 GAZelle、Mazda E2000、Hyundai H100、Aixam Mega 和 Chevrolet Caprice 等剩余记录。

推进信号：CONTINUE

[1]: https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf "18MY_RC_PAJERO_GCC_En.pdf"
[2]: https://www.automobile-catalog.com/car/1974/116960/chevrolet_impala_custom_coupe_350-4_v-8_turbo-fire_hydra-matic.html?utm_source=chatgpt.com "1974 Chevrolet Impala Custom Coupe 350-4 V-8 Turbo-Fire Hydra-Matic Specs Review (119.5 kW / 163 PS / 160 hp) (since September 1973 for North America California (U.S.))"


--- 发送 / 继续到 Round 32 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 32 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Toyota Hilux VII 2.5 D-4D 后驱车型的 Single Cab、Extra Cab、Double Cab 三个分支。三者车长均为 5255 mm、车宽均为 1760 mm；Single/Extra Cab 车高为 1680 mm，Double Cab 为 1695 mm。([丰田欧洲新闻中心][1])
* 闭合 Mazda BT-50 I 2.5 MZR-CD 后驱 Single Cab，以及 Mitsubishi L200 IV 3.5 V6 4WD Double Cab。([Scribd][2])
* Chevrolet Caprice III Coupe 的输入生产期覆盖三种外廓：1981 年低车高版、1982–1983 年增高版，以及 1984 年车长和车宽变化版，因此拆分为三个尺寸组。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：84
* PENDING 输入：16
* READY 映射：115
* 已确认并被引用尺寸组：79
* 本轮新增尺寸组：8
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122397	122397	Pickup	BT-50 I		2	EU-MAZDA-BT-50-I-SINGLE-CAB-PICKUP-01	HIGH	4x2 Single Cab外廓。	READY
122436_singlecab	122436	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-SINGLE-CAB-PICKUP-01	HIGH	4x2 Single Cab物理分支。	READY
122436_extracab	122436	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-EXTRA-CAB-PICKUP-01	HIGH	4x2 Extra Cab物理分支。	READY
122436_doublecab	122436	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-DOUBLE-CAB-PICKUP-01	HIGH	4x2 Double Cab物理分支。	READY
122618	122618	Pickup	L200 IV	KB9T	4	EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	HIGH	3.5 V6仅对应Double Cab外廓。	READY
122805_1981	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1981-01	HIGH	1981车型年低车高外廓。	READY
122805_1982_1983	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1982-1983-01	MEDIUM	1982–1983车型年车高变化分支。	READY
122805_1984	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1984-01	HIGH	1984车型年车长及车宽变化分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-BT-50-I-SINGLE-CAB-PICKUP-01	5075	1715	1620	Mazda BT-50 2007 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Mazda-BT-50-2007-UK-.pdf
EU-TOYOTA-HILUX-VII-SINGLE-CAB-PICKUP-01	5255	1760	1680	Toyota Europe 2005 Hilux press kit;Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-EXTRA-CAB-PICKUP-01	5255	1760	1680	Toyota Europe 2005 Hilux press kit;Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-DOUBLE-CAB-PICKUP-01	5255	1760	1695	Toyota Europe 2005 Hilux press kit;Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	5115	1800	1780	Mitsubishi L200 IV owner manual;Ficha Completa Mitsubishi L200 Triton HPE 3.5 V6 2014	https://www.mitsubishiman.ru/en/L200/4_d/main/manual/tehnicheskie-harakteristiki-avtomobiley-l200;https://www.fichacompleta.com.br/en/carros/mitsubishi/l200-triton-hpe-3-5-v6-at-2014
EU-CHEVROLET-CAPRICE-III-COUPE-1981-01	5387	1913	1387	Automobile-Catalog 1981 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1981/210005/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-COUPE-1982-1983-01	5387	1913	1433	Automobile-Catalog 1982 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1982/210500/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-III-COUPE-1984-01	5405	1915	1433	Automobile-Catalog 1984 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1984/1484000/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic.html
```

## 5. 下一步优先处理

1. 批量拆解 Nissan NV400 的前驱/后驱、L1–L4、H1–H3 厢式车和底盘分支。
2. 处理 Fiat Scudo 与 Peugeot Partner 的底盘驾驶室分支。
3. 闭合 GAZelle、Mazda E2000、Hyundai H100、Mercedes-Benz Vario 等剩余商用车。
4. 最后处理 Aixam Mega 柴油版和电动版。

推进信号：CONTINUE

[1]: https://newsroom.toyota.eu/2005-toyota-hilux/ "2005 Toyota Hilux"
[2]: https://www.scribd.com/document/761926950/Mazda-BT-50-2007-UK?utm_source=chatgpt.com "Mazda BT 50 2007 UK | PDF"
[3]: https://www.automobile-catalog.com/car/1981/210005/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic_overdrive.html?utm_source=chatgpt.com "1981 Chevrolet Caprice Classic Coupe 5.0L V-8 automatic overdrive Specs Review (112 kW / 152 PS / 150 hp) (since September 1980 for North America U.S.)"


--- 发送 / 继续到 Round 33 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 33 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Nissan NV400 前驱厢式车：dCi 130 与 dCi 170 均拆分为 L1H1、L1H2、L2H2、L2H3、L3H2、L3H3 六种外廓。
* 闭合 dCi 130 后驱厢式车：拆分为 L3H2/L3H3，并分别区分单后轮与双后轮；四种配置的标准高度不同。
* 闭合前驱底盘驾驶室：dCi 130 对应单排 L2H1、L3H1；dCi 170 对应单排 L3H1与双排 L3H1。
* 闭合 dCi 130 后驱单排底盘驾驶室：官方专项规格明确覆盖 L2/L3 与单后轮/双后轮四种配置。所有宽度均采用官方明确列出的不含后视镜车宽 2070 mm。([日产][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：90
* PENDING 输入：10
* READY 映射：139
* 已确认并被引用尺寸组：96
* 本轮新增尺寸组：17
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122433_l3h2_srw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	HIGH	L3H2单后轮分支。	READY
122433_l3h2_drw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	HIGH	L3H2双后轮分支。	READY
122433_l3h3_srw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	HIGH	L3H3单后轮分支。	READY
122433_l3h3_drw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	HIGH	L3H3双后轮分支。	READY
122439_l1h1	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
122439_l1h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
122439_l2h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
122439_l2h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	L2H3物理分支。	READY
122439_l3h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	L3H2物理分支。	READY
122439_l3h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	L3H3物理分支。	READY
122441_l1h1	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
122441_l1h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
122441_l2h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
122441_l2h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	L2H3物理分支。	READY
122441_l3h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	L3H2物理分支。	READY
122441_l3h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	L3H3物理分支。	READY
122443_single_l2h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	HIGH	单排L2H1底盘分支。	READY
122443_single_l3h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	单排L3H1底盘分支。	READY
122445_single_l2h1_srw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	HIGH	单排L2H1单后轮分支。	READY
122445_single_l3h1_srw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	HIGH	单排L3H1单后轮分支。	READY
122445_single_l2h1_drw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	HIGH	单排L2H1双后轮分支。	READY
122445_single_l3h1_drw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	HIGH	单排L3H1双后轮分支。	READY
122450_single_l3h1	122450	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	单排L3H1底盘分支。	READY
122450_double_l3h1	122450	Pickup	NV400 I		4	EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	HIGH	双排L3H1底盘分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	6198	2070	2527	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	6198	2070	2549	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	6198	2070	2786	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	6198	2070	2815	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	5048	2070	2500	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	5548	2070	2749	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	6198	2070	2488	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	6198	2070	2744	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	5549	2070	2265	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	6199	2070	2258	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	6199	2070	2263	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	5643	2070	2284	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	6293	2070	2276	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	5643	2070	2283	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	6193	2070	2283	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
```

## 5. 下一步优先处理

1. 闭合 Fiat Scudo I 与 Peugeot Partner I 的底盘驾驶室分支。
2. 处理 GAZelle、Mazda E2000、Hyundai H100 和 Mercedes-Benz Vario。
3. 最后闭合 Aixam Mega 柴油版及电动版；完成后立即进行一次机械收尾并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf?utm_source=chatgpt.com "NISSAN"


--- 发送 / 继续到 Round 34 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 34 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Hyundai H100 2.4 厢式车。1997 年技术资料将 Van 单独列为 `4790×1690×1965 mm`，与货车及底盘驾驶室配置区分，建立独立尺寸组。([IKZ][1])
* 闭合 Mazda E2000 82 hp `SR1` Bus。精确车型生产期为 1989 年 10 月至 1994 年 5 月，三维为 `4965×1690×1955 mm`；未复用后期 95 hp 车型的不同尺寸。([Truck1][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：92
* PENDING 输入：8
* READY 映射：141
* 已确认并被引用尺寸组：98
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122392	122392	MPV	E-Series SR1	SR1		EU-MAZDA-E-SR1-E2000-BUS-01	MEDIUM	82 hp欧洲Bus外廓。	READY
122666	122666	Van	H100 II			EU-HYUNDAI-H100-II-VAN-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-E-SR1-E2000-BUS-01	4965	1690	1955	Truck1 Mazda E2000 Bus SR1 2.0 82 Hp technical specifications	https://www.truck1.eu/blog/mazda-e2000-bus-sr1-2-0-82-hp-tech-specs-t28416
EU-HYUNDAI-H100-II-VAN-01	4790	1690	1965	IKZ-HAUSTECHNIK Hyundai H100 compact transporter profile;Korejskevozy Hyundai H100 1997 technical data	https://www.ikz.de/ikz-archiv/1997/23/9723052.php;https://korejskevozy.cz/clanek/technicke-informace-hyundai-h-100-1997/?id=b563d190-c7e3-4d6e-8a0c-eea232d697ae&skupina=ae456b0a-24f3-4cdc-bc33-0688abef814f
```

## 5. 下一步优先处理

1. 闭合 Fiat Scudo I 1.9 D、2.0 JTD 底盘驾驶室外廓。
2. 解决 Peugeot Partner I 1.9 D、2.0 HDi 平台驾驶室的完整车高。
3. 处理 GAZelle、Mercedes-Benz Vario 815 D。
4. 最后闭合 Aixam Mega 柴油版和电动版。

推进信号：CONTINUE

[1]: https://www.ikz.de/ikz-archiv/1997/23/9723052.php "IKZ-HAUSTECHNIK"
[2]: https://www.truck1.eu/blog/mazda-e2000-bus-sr1-2-0-82-hp-tech-specs-t28416?srsltid=AfmBOoqZbUxCzCIgByJvO4_R3ZFqLFcYrw4kU3xTKbbjmclsFTIjFiEq&utm_source=chatgpt.com "Mazda E2000 Bus (SR1) 2.0 (82 Hp) - Tech specs"


--- 发送 / 继续到 Round 35 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 35 / checkpoint 续跑 ---
## 1. 更新点

* 闭合 Mercedes-Benz Vario 815 D 底盘驾驶室分支。该 Ktype 覆盖 3700、4250、4800 mm 三种轴距，每种轴距均包含标准驾驶室与双排驾驶室。
* 815 D 的发动机差异不改变 Vario 8 系列底盘驾驶室外廓；按官方 Vario 底盘规格，三种轴距车长分别为 6060、6940、7485 mm，车宽均为不含后视镜的 2206 mm；标准驾驶室车高 2405 mm，双排驾驶室车高 2410 mm。([Dezo's Garage][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：93
* PENDING 输入：7
* READY 映射：147
* 已确认并被引用尺寸组：104
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122548_std_wb3700	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB3700-01	MEDIUM	标准驾驶室、3700 mm轴距分支。	READY
122548_crew_wb3700	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB3700-01	MEDIUM	双排驾驶室、3700 mm轴距分支。	READY
122548_std_wb4250	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4250-01	MEDIUM	标准驾驶室、4250 mm轴距分支。	READY
122548_crew_wb4250	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4250-01	MEDIUM	双排驾驶室、4250 mm轴距分支。	READY
122548_std_wb4800	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4800-01	MEDIUM	标准驾驶室、4800 mm轴距分支。	READY
122548_crew_wb4800	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4800-01	MEDIUM	双排驾驶室、4800 mm轴距分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB3700-01	6060	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB3700-01	6060	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4250-01	6940	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4250-01	6940	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4800-01	7485	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4800-01	7485	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
```

## 5. 下一步优先处理

1. 闭合 Fiat Scudo I 1.9 D、2.0 JTD 平台驾驶室。
2. 闭合 Peugeot Partner I 1.9 D、2.0 HDi 平台驾驶室。
3. 处理 GAZelle 2.4 厢式车及 Aixam Mega 柴油、电动平台驾驶室。
4. 剩余 7 个 Ktype 全部 READY 后，立即执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf "7938_VarioSpecBro.qxd"


--- 发送 / 继续到 Round 36 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 36 / checkpoint 续跑 ---
## 1. 更新点

* 闭合最后 7 个 Ktype：GAZelle GAZ-2705、Fiat Scudo I 平台驾驶室、Peugeot Partner I 平台驾驶室，以及 Aixam Mega 柴油/电动平台式货车。
* Scudo 与 Partner 的同平台动力版本分别复用单一尺寸组；Aixam 柴油版与电动版的量产平台外廓均为 3102×1476×1800 mm，复用同一尺寸组。([Dezo's Garage][1])
* 已完成固定表头、唯一性、引用闭合、正整数尺寸、来源非空和下载文件检查。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入：100
* PENDING 输入：0
* READY 映射：154
* 当前引用尺寸组：111
* 映射引用全部闭合，无孤立尺寸组。

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122182_prefl	122182	Sedan	Elantra VI	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	HIGH	2018改款前外廓。	READY
122182_facelift	122182	Sedan	Elantra VI facelift	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	HIGH	2018改款后车长及车高变化。	READY
122185	122185	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-01	MEDIUM	输入90 hp与可追溯资料102 hp存在市场功率标定差异。	READY
122211_prefl	122211	Wagon	Cee'd I		5	EU-KIA-CEED-I-WAGON-PREFL-01	MEDIUM	2009改款前旅行车外廓。	READY
122211_facelift	122211	Wagon	Cee'd I facelift		5	EU-KIA-CEED-I-WAGON-FACELIFT-01	MEDIUM	2009改款后车高变化。	READY
122213	122213	Hatchback	Cee'd II		5	EU-KIA-CEED-II-HATCHBACK-01	HIGH		READY
122217	122217	Wagon	Cee'd II		5	EU-KIA-CEED-II-WAGON-01	HIGH		READY
122220	122220	Hatchback	Rio III	UB	5	EU-KIA-RIO-III-HATCHBACK-01	HIGH		READY
122239	122239	SUV	Sportage IV		5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH	155 hp版本对应改款前外廓。	READY
122241	122241	Van	GAZelle I facelift	GAZ-2705		EU-GAZ-GAZELLE-GAZ-2705-VAN-01	MEDIUM	标准轴距全封闭货运厢式车。	READY
122247_prefl	122247	Hatchback	Venga YN	YN	5	EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	HIGH	2014改款前外廓。	READY
122247_facelift	122247	Hatchback	Venga YN facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	2014改款后车长变化。	READY
122248	122248	Coupe	Beta Coupe	BC	2	EU-LANCIA-BETA-BC-COUPE-01	HIGH		READY
122249	122249	Hatchback	i20 II Active		5	EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	HIGH	Active跨界两厢外廓。	READY
122255	122255	Hatchback	Soul I		5	EU-KIA-SOUL-I-HATCHBACK-01	HIGH		READY
122270	122270	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-01	HIGH	欧洲4WD四门轿车外廓。	READY
122284	122284	Hatchback	Accord I	SJ	3	EU-HONDA-ACCORD-I-HATCHBACK-01	HIGH		READY
122287	122287	SUV	Element I		5	EU-HONDA-ELEMENT-I-SUV-01	HIGH		READY
122288	122288	SUV	Element I		5	EU-HONDA-ELEMENT-I-SUV-01	HIGH		READY
122381	122381	Sedan	Volvo 940	944	4	EU-VOLVO-940-944-SEDAN-01	MEDIUM		READY
122392	122392	MPV	E-Series SR1	SR1		EU-MAZDA-E-SR1-E2000-BUS-01	MEDIUM	82 hp欧洲Bus外廓。	READY
122394	122394	Pickup	Scudo I	220	2	EU-FIAT-SCUDO-I-220-PLATFORM-CAB-01	HIGH	第一代平台驾驶室外廓。	READY
122396	122396	Sedan	Mazda 323 S V	BA	4	EU-MAZDA-323-BA-SEDAN-01	MEDIUM		READY
122397	122397	Pickup	BT-50 I		2	EU-MAZDA-BT-50-I-SINGLE-CAB-PICKUP-01	HIGH	4x2 Single Cab外廓。	READY
122405	122405	Coupe	626 II	GC	2	EU-MAZDA-626-II-GC-COUPE-01	HIGH		READY
122425	122425	Pickup	Partner I		2	EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH	第一代平台驾驶室外廓。	READY
122426	122426	Pickup	Partner I		2	EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH	第一代平台驾驶室外廓。	READY
122430	122430	MPV	Peugeot 3008 I facelift		5	EU-PEUGEOT-3008-I-FACELIFT-MPV-01	HIGH		READY
122433_l3h2_srw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	HIGH	L3H2单后轮分支。	READY
122433_l3h2_drw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	HIGH	L3H2双后轮分支。	READY
122433_l3h3_srw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	HIGH	L3H3单后轮分支。	READY
122433_l3h3_drw	122433	Van	NV400 I			EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	HIGH	L3H3双后轮分支。	READY
122436_singlecab	122436	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-SINGLE-CAB-PICKUP-01	HIGH	4x2 Single Cab物理分支。	READY
122436_extracab	122436	Pickup	Hilux VII		2	EU-TOYOTA-HILUX-VII-EXTRA-CAB-PICKUP-01	HIGH	4x2 Extra Cab物理分支。	READY
122436_doublecab	122436	Pickup	Hilux VII		4	EU-TOYOTA-HILUX-VII-DOUBLE-CAB-PICKUP-01	HIGH	4x2 Double Cab物理分支。	READY
122438	122438	Pickup	Scudo I	220	2	EU-FIAT-SCUDO-I-220-PLATFORM-CAB-01	HIGH	第一代平台驾驶室外廓。	READY
122439_l1h1	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
122439_l1h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
122439_l2h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
122439_l2h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	L2H3物理分支。	READY
122439_l3h2	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	L3H2物理分支。	READY
122439_l3h3	122439	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	L3H3物理分支。	READY
122441_l1h1	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
122441_l1h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
122441_l2h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
122441_l2h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	HIGH	L2H3物理分支。	READY
122441_l3h2	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	HIGH	L3H2物理分支。	READY
122441_l3h3	122441	Van	NV400 I			EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	HIGH	L3H3物理分支。	READY
122443_single_l2h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	HIGH	单排L2H1底盘分支。	READY
122443_single_l3h1	122443	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	单排L3H1底盘分支。	READY
122445_single_l2h1_srw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	HIGH	单排L2H1单后轮分支。	READY
122445_single_l3h1_srw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	HIGH	单排L3H1单后轮分支。	READY
122445_single_l2h1_drw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	HIGH	单排L2H1双后轮分支。	READY
122445_single_l3h1_drw	122445	Pickup	NV400 I		2	EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	HIGH	单排L3H1双后轮分支。	READY
122450_single_l3h1	122450	Pickup	NV400 I		2	EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	HIGH	单排L3H1底盘分支。	READY
122450_double_l3h1	122450	Pickup	NV400 I		4	EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	HIGH	双排L3H1底盘分支。	READY
122456_l1h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122456_l2h1	122456	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122458_l1h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122458_l2h1	122458	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122459_l1h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122459_l1h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2高顶短轴物理分支。	READY
122459_l2h1	122459	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122459_l2h2	122459	Van	NV300 I			EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2高顶长轴物理分支。	READY
122462_l1h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1低顶短轴物理分支。	READY
122462_l1h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-L1H2-01	HIGH	L1H2高顶短轴物理分支。	READY
122462_l2h1	122462	Van	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1低顶长轴物理分支。	READY
122462_l2h2	122462	Van	NV300 I			EU-NISSAN-NV300-I-L2H2-01	HIGH	L2H2高顶长轴物理分支。	READY
122469	122469	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH		READY
122481_l1h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1短轴Combi物理分支。	READY
122481_l2h1	122481	MPV	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1长轴Combi物理分支。	READY
122486_l1h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-L1H1-01	HIGH	L1H1短轴Combi物理分支。	READY
122486_l2h1	122486	MPV	NV300 I			EU-NISSAN-NV300-I-L2H1-01	HIGH	L2H1长轴Combi物理分支。	READY
122487	122487	MPV	Lodgy		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
122490_prefl	122490	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-SEDAN-PREFL-01	HIGH	2002改款前轿车外廓。	READY
122490_facelift	122490	Sedan	Thalia I facelift		4	EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	HIGH	2002改款后车长及车高变化。	READY
122492	122492	Sedan	Dauphine Gordini		4	EU-RENAULT-DAUPHINE-GORDINI-SEDAN-01	HIGH	34 hp输入对应Dauphine Gordini版本。	READY
122505	122505	MPV	Grand Caravan V		5	EU-DODGE-GRAND-CARAVAN-V-MPV-01	HIGH		READY
122529_prefl_3dr	122529	Hatchback	Ritmo I pre-facelift	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	MEDIUM	前期三门车身分支。	READY
122529_prefl_5dr	122529	Hatchback	Ritmo I pre-facelift	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	MEDIUM	前期五门车身分支。	READY
122529_facelift_3dr	122529	Hatchback	Ritmo I facelift	138A	3	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	MEDIUM	改款后三门车身分支。	READY
122529_facelift_5dr	122529	Hatchback	Ritmo I facelift	138A	5	EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	MEDIUM	改款后五门车身分支。	READY
122548_std_wb3700	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB3700-01	MEDIUM	标准驾驶室、3700 mm轴距分支。	READY
122548_crew_wb3700	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB3700-01	MEDIUM	双排驾驶室、3700 mm轴距分支。	READY
122548_std_wb4250	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4250-01	MEDIUM	标准驾驶室、4250 mm轴距分支。	READY
122548_crew_wb4250	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4250-01	MEDIUM	双排驾驶室、4250 mm轴距分支。	READY
122548_std_wb4800	122548	Pickup	Vario	W670	2	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4800-01	MEDIUM	标准驾驶室、4800 mm轴距分支。	READY
122548_crew_wb4800	122548	Pickup	Vario	W670	4	EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4800-01	MEDIUM	双排驾驶室、4800 mm轴距分支。	READY
122555	122555	Wagon	Wartburg 353	353	5	EU-WARTBURG-353-TOURIST-WAGON-01	HIGH	Tourist五门旅行车外廓。	READY
122575	122575	SUV	Captiva I facelift		5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	MEDIUM	输入2.0 D名称与120 kW/163 hp官方2.2柴油规格不一致。	READY
122589	122589	Sedan	Town Car III	FN145	4	EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	MEDIUM	153 kW/208 hp锁定初期标准轴距外廓。	READY
122595	122595	Hatchback	Laguna II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-01	MEDIUM	输入211 hp与资料207 hp为市场功率标定差异。	READY
122596	122596	Convertible	SL R107 facelift	R107	2	EU-MERCEDES-BENZ-SL-R107-FACELIFT-CONVERTIBLE-01	MEDIUM		READY
122613_xs	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122613_m	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122613_xl	122613	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
122614_xs	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122614_m	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122614_xl	122614	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
122618	122618	Pickup	L200 IV	KB9T	4	EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	HIGH	3.5 V6仅对应Double Cab外廓。	READY
122620_3dr	122620	SUV	Pajero IV	V85W	3	EU-MITSUBISHI-PAJERO-IV-V85W-SUV-3D-01	HIGH	3.5 V6三门短轴物理分支。	READY
122620_5dr	122620	SUV	Pajero IV	V95W	5	EU-MITSUBISHI-PAJERO-IV-V95W-SUV-5D-01	HIGH	3.5 V6五门长轴物理分支。	READY
122622	122622	Coupe	Monte Carlo III		2	EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	HIGH	第三代双门Coupe外廓。	READY
122623_m	122623	MPV	SpaceTourer I		5	EU-CITROEN-SPACETOURER-I-MPV-M-01	HIGH	M车长物理分支。	READY
122623_xl	122623	MPV	SpaceTourer I		5	EU-CITROEN-SPACETOURER-I-MPV-XL-01	HIGH	XL车长物理分支。	READY
122624_xs	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	HIGH	XS短车身物理分支。	READY
122624_m	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-M-LOW-01	HIGH	M中长车身物理分支。	READY
122624_xl	122624	MPV	Jumpy III		5	EU-CITROEN-JUMPY-III-VAN-XL-01	HIGH	XL长车身物理分支。	READY
122627	122627	MPV	Delica Space Gear	L400	5	EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	HIGH	欧洲后驱五门车身。	READY
122648	122648	Sedan	Cerato III facelift	YD	4	EU-KIA-CERATO-III-FACELIFT-SEDAN-01	HIGH		READY
122653	122653	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	MEDIUM	5P五门高顶车身外廓。	READY
122662	122662	Hatchback	Astra H facelift		5	EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	HIGH		READY
122663	122663	Hatchback	Astra H facelift		5	EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	HIGH		READY
122666	122666	Van	H100 II			EU-HYUNDAI-H100-II-VAN-01	HIGH		READY
122693	122693	Pickup	Mega Multitruck 400		2	EU-AIXAM-MEGA-MULTITRUCK-PLATFORM-01	HIGH	柴油平台式货车外廓。	READY
122694	122694	Pickup	Mega Multitruck NE		2	EU-AIXAM-MEGA-MULTITRUCK-PLATFORM-01	HIGH	电动平台式货车外廓。	READY
122714	122714	SUV	Grand Vitara II		5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	HIGH	五门长轴车身。	READY
122715	122715	MPV	C3 Picasso I pre-facelift		5	EU-CITROEN-C3-PICASSO-I-PREFL-MPV-01	MEDIUM	84kW/115hp动力对应改款前车身。	READY
122718	122718	Sedan	SX4 I Sedan		4	EU-SUZUKI-SX4-I-SEDAN-01	MEDIUM	四驱不改变轿车物理外廓。	READY
122731_prefl	122731	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	HIGH	2017车型年改款前外廓。	READY
122731_facelift	122731	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	2018车型年改款后车长变化。	READY
122732	122732	SUV	Kuga II facelift		5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH		READY
122740	122740	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-FACELIFT-SUV-01	MEDIUM	输入188 hp与资料185 hp为市场功率标定差异。	READY
122801	122801	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	HIGH		READY
122805_1981	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1981-01	HIGH	1981车型年低车高外廓。	READY
122805_1982_1983	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1982-1983-01	MEDIUM	1982–1983车型年车高变化分支。	READY
122805_1984	122805	Coupe	Caprice III		2	EU-CHEVROLET-CAPRICE-III-COUPE-1984-01	HIGH	1984车型年车长及车宽变化分支。	READY
122807	122807	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122808	122808	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-AMG-E43-WAGON-01	HIGH	AMG E 43外部套件分支。	READY
122809	122809	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122810	122810	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	HIGH		READY
122813	122813	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122815	122815	SUV	Macan I	95B	5	EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	HIGH	324 kW Turbo Performance Package外廓。	READY
122819	122819	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122820	122820	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
122821	122821	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	HIGH	Turbo标准车高分支。	READY
122822	122822	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122823	122823	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122824	122824	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
122830	122830	SUV	Captiva I facelift		5	EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	HIGH		READY
122832	122832	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122833	122833	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH	AMG GLC 43外部套件分支。	READY
122834	122834	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
122836	122836	SUV	GLC X253	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
122843	122843	Pickup	Amarok I facelift		4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	Double Cab外廓。	READY
122853	122853	Hatchback	Model S facelift		5	EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	HIGH	P100D对应2016–2020量产外廓。	READY
122855	122855	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH	输入车身形式标准化为SUV。	READY
122890_narrow	122890	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	HIGH	SZ3无轮拱扩展窄体外廓。	READY
122890_widebody	122890	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	SZ-T轮拱扩展宽体外廓。	READY
122891	122891	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Allgrip宽体外廓。	READY
122892	122892	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Hybrid宽体外廓。	READY
122893	122893	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	Hybrid Allgrip宽体外廓。	READY
122896	122896	Coupe	Impala IV		2	EU-CHEVROLET-IMPALA-IV-COUPE-1974-01	HIGH	1974款双门硬顶Coupe外廓。	READY
122901	122901	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-01	MEDIUM		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_601-700_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-PREFL-01	4570	1800	1450	Hyundai Elantra AD official technical data	https://www.hyundai.hu/downloads/muszaki_adatlapok/Elantra_muszaki_adatlap.pdf
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-FACELIFT-01	4620	1800	1440	Hyundai Avante official catalog	https://www.hyundai.com/content/dam/hyundai/kr/ko/html/pdf/en-cn-catalog/en-catalog/avante-catalog-eng.pdf
EU-KIA-CERATO-I-LD-SEDAN-01	4480	1735	1470	Auto-Data Kia Cerato I Sedan 1.5 CRDi	https://www.auto-data.net/en/kia-cerato-i-sedan-1.5-crdi-102hp-32546
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490	Auto-Data Kia Cee'd SW I 1.6 CVVT (122 Hp)	https://www.auto-data.net/en/kia-ceed-sw-i-1.6-cvvt-122hp-42438
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525	Auto-Data Kia Cee'd SW I facelift 2009 1.6 16V (126 Hp)	https://www.auto-data.net/en/kia-ceed-sw-i-facelift-2009-1.6-16v-126hp-17072
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470	Auto-Data Kia Cee'd II 1.6 GDi; Auto-Data Kia Cee'd II facelift 2015	https://www.auto-data.net/en/kia-ceed-ii-1.6-gdi-16v-135hp-17855;https://www.auto-data.net/en/kia-ceed-ii-facelift-2015-generation-5965
EU-KIA-CEED-II-WAGON-01	4505	1780	1485	Auto-Data Kia Cee'd SW II; Auto-Data Kia Cee'd SW II facelift 2015 1.6 GDI	https://www.auto-data.net/en/kia-ceed-sw-ii-generation-3930;https://www.auto-data.net/en/kia-ceed-sw-ii-facelift-2015-1.6-gdi-135hp-41653
EU-KIA-RIO-III-HATCHBACK-01	4045	1720	1455	Auto-Data Kia Rio III Hatchback UB 1.2 16V	https://www.auto-data.net/en/kia-rio-iii-hatchback-ub-1.2-16v-85hp-17052
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Auto-Data Kia Sportage IV 2.0 MPI (155 Hp)	https://www.auto-data.net/en/kia-sportage-iv-2.0-mpi-155hp-sportmatic-54522
EU-GAZ-GAZELLE-GAZ-2705-VAN-01	5475	2075	2200	GAZ-2705 technical specification; GAZelle operation technical data	https://www.26auto.ru/gaz/lmg/gmd04/gaz2705/;https://gazavtomir.ru/info/teh/exploitation/gazel_umz/4/
EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	4068	1765	1600	Auto-Data Kia Venga YN 1.4 16V	https://www.auto-data.net/en/kia-venga-yn-1.4-16v-90hp-17089
EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	4075	1765	1600	Auto-Data Kia Venga YN facelift 2014 1.4	https://www.auto-data.net/en/kia-venga-yn-facelift-2014-1.4-90hp-23781
EU-LANCIA-BETA-BC-COUPE-01	3995	1650	1285	EncyCARpedia 1977 Lancia Beta Coupe 1300	https://www.encycarpedia.com/lancia/77-beta-coupe-1300
EU-HYUNDAI-I20-II-ACTIVE-HATCHBACK-01	4065	1760	1529	Auto-Data Hyundai i20 II Active 1.4	https://www.auto-data.net/en/hyundai-i20-ii-active-1.4-100hp-23643
EU-KIA-SOUL-I-HATCHBACK-01	4105	1785	1661	Auto-Data Kia Soul I 1.6	https://www.auto-data.net/en/kia-soul-i-1.6-126hp-2692
EU-HONDA-CIVIC-IV-SEDAN-01	4230	1690	1360	Automobile-Catalog 1989 Honda Civic EX 1.6i-16 4WD; Auto-Data Honda Civic IV 1.6i 16V 4x4	https://www.automobile-catalog.com/car/1989/1101950/honda_civic_ex_1_6i-16_4wd_cat.html;https://www.auto-data.net/en/honda-civic-iv-1.6i-16v-4x4-109hp-12279
EU-HONDA-ACCORD-I-HATCHBACK-01	4125	1620	1335	Auto-Data Honda Accord I Hatchback 1.6 EX SJ	https://www.auto-data.net/en/honda-accord-i-hatchback-sj-sy-1.6-ex-sj-80hp-12111
EU-HONDA-ELEMENT-I-SUV-01	4300	1815	1788	Auto-Data Honda Element I 2.4; Auto-Data Honda Element I 2.4 4WD	https://www.auto-data.net/en/honda-element-i-2.4-160hp-automatic-56677;https://www.auto-data.net/en/honda-element-i-2.4-160hp-4wd-12136
EU-VOLVO-940-944-SEDAN-01	4871	1750	1425	Auto-Data Volvo 940 (944) 2.3i	https://www.auto-data.net/en/volvo-940-944-2.3i-131hp-9286
EU-MAZDA-E-SR1-E2000-BUS-01	4965	1690	1955	Truck1 Mazda E2000 Bus SR1 2.0 82 Hp technical specifications	https://www.truck1.eu/blog/mazda-e2000-bus-sr1-2-0-82-hp-tech-specs-t28416
EU-FIAT-SCUDO-I-220-PLATFORM-CAB-01	4522	1844	1940	Citroën Dispatch 2006 official van technical specifications	https://xr793.com/wp-content/uploads/2022/09/2006-Citroen-Van-Tech-Specs-UK.pdf
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420	Auto-Data Mazda 323 S V (BA) 1.5i 16V	https://www.auto-data.net/en/mazda-323-s-v-ba-1.5i-16v-88hp-11160
EU-MAZDA-BT-50-I-SINGLE-CAB-PICKUP-01	5075	1715	1620	Mazda BT-50 2007 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/02/Mazda-BT-50-2007-UK-.pdf
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1350	UltimateSpecs Mazda 626 II Coupe; Automobile-Catalog 1983 Mazda 626 1.6 LX Coupe	https://www.ultimatespecs.com/car-specs/Mazda/M1241/626-II-Coupe;https://www.automobile-catalog.com/car/1983/1626125/mazda_626_1_6_lx_coupe.html
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819	Citroën Berlingo 2006 official van technical specifications	https://xr793.com/wp-content/uploads/2022/09/2006-Citroen-Van-Tech-Specs-UK.pdf
EU-PEUGEOT-3008-I-FACELIFT-MPV-01	4365	1837	1635	Auto-Data Peugeot 3008 I Phase II 1.6 HDi	https://www.auto-data.net/en/peugeot-3008-i-phase-ii-2013-1.6-hdi-115hp-fap-19764
EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	6198	2070	2527	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	6198	2070	2549	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	6198	2070	2786	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	6198	2070	2815	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-TOYOTA-HILUX-VII-SINGLE-CAB-PICKUP-01	5255	1760	1680	Toyota Europe 2005 Hilux press kit; Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-EXTRA-CAB-PICKUP-01	5255	1760	1680	Toyota Europe 2005 Hilux press kit; Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-TOYOTA-HILUX-VII-DOUBLE-CAB-PICKUP-01	5255	1760	1695	Toyota Europe 2005 Hilux press kit; Toyota Europe 2006 Paris Motor Show specifications	https://newsroom.toyota.eu/2005-toyota-hilux/;https://newsroom.toyota.eu/2006-paris-motor-show/
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	5048	2070	2500	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	5548	2070	2749	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	6198	2070	2488	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	6198	2070	2744	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	5549	2070	2265	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	6199	2070	2258	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	5643	2070	2284	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	6293	2070	2276	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	5643	2070	2283	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	6193	2070	2283	Nissan Greece NV400 Chassis Cab official technical specifications	https://www-europe.nissan-cdn.net/content/dam/Nissan/greece/brochures/NV400_CHASSIS_CAB.pdf
EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	6199	2070	2263	Nissan NV400 Ireland 2017 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20%20Brochure%202017.pdf
EU-NISSAN-NV300-I-L1H1-01	4999	1956	1971	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L2H1-01	5399	1956	1971	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L1H2-01	4999	1956	2493	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-I-L2H2-01	5399	1956	2490	Nissan NV300 UK official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-CITROEN-C8-I-MPV-01	4726	1854	1856	Citroën C8 2002 UK official technical specification	https://xr793.org/wp-content/uploads/2022/09/2002-Citroen-C8-Tech-Specs-UK.pdf
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Auto-Data Dacia Lodgy 1.5 dCi (110 Hp)	https://www.auto-data.net/en/dacia-lodgy-1.5-dci-110hp-fap-18008
EU-RENAULT-THALIA-I-SEDAN-PREFL-01	4150	1639	1416	Auto-Data Renault Clio Symbol I 1.4 i 16V	https://www.auto-data.net/en/renault-clio-symbol-i-1.4-i-16v-98hp-10429
EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 1.4 16V	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-1.4-16v-98hp-10663
EU-RENAULT-DAUPHINE-GORDINI-SEDAN-01	3945	1520	1440	Automobile-Catalog 1960 Renault Dauphine Gordini	https://www.automobile-catalog.com/car/1960/2922830/renault_dauphine_gordini.html
EU-DODGE-GRAND-CARAVAN-V-MPV-01	5177	2000	1750	Auto-Data Dodge Caravan V 3.8 V6 (193 Hp)	https://www.auto-data.net/en/dodge-caravan-v-3.8-v6-193hp-automatic-30983
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-3D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html
EU-FIAT-RITMO-I-138A-HATCHBACK-PREFL-5D-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 CL	https://www.automobile-catalog.com/car/1980/1369610/fiat_ritmo_60_cl.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-3D-01	3993	1650	1418	Automobile-Catalog 1987 Fiat Ritmo 60 CL	https://www.automobile-catalog.com/car/1987/714680/fiat_ritmo_60_l_5-speed.html
EU-FIAT-RITMO-I-138A-HATCHBACK-FACELIFT-5D-01	3993	1650	1418	Automobile-Catalog 1987 Fiat Ritmo 60 L	https://www.automobile-catalog.com/car/1987/714665/fiat_ritmo_60_l.html
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB3700-01	6060	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB3700-01	6060	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4250-01	6940	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4250-01	6940	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-STANDARD-WB4800-01	7485	2206	2405	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VARIO-W670-CHASSIS-CREW-WB4800-01	7485	2206	2410	Mercedes-Benz Vario 2004 official chassis cab specification sheet	https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf
EU-WARTBURG-353-TOURIST-WAGON-01	4380	1640	1495	Automobile-Catalog 1987 Wartburg 353 W Tourist	https://www.automobile-catalog.com/car/1987/50015/wartburg_353_w_tourist.html
EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	4673	1849	1727	Chevrolet Captiva 2014 UK official brochure (archived)	https://xr793.com/wp-content/uploads/2022/10/2014-Chevrolet-Captiva-UK.pdf
EU-LINCOLN-TOWN-CAR-III-FN145-SEDAN-01	5470	1985	1470	Auto-Data Lincoln Town Car III FN145 4.6 V8	https://www.auto-data.net/en/lincoln-town-car-iii-fn145-4.6-v8-208hp-8207
EU-RENAULT-LAGUNA-II-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II 3.0 V6 24V	https://www.auto-data.net/en/renault-laguna-ii-3.0-v6-24v-207hp-10332
EU-MERCEDES-BENZ-SL-R107-FACELIFT-CONVERTIBLE-01	4580	1790	1300	Auto-Data Mercedes-Benz SL R107 facelift 560 SL	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-560-sl-cat-v8-230hp-automatic-43219
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910	Citroën Dispatch/Jumpy official brochure	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/van-range/Dispatch_Brochure.pdf
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899	Citroën Dispatch/Jumpy official brochure	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/van-range/Dispatch_Brochure.pdf
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940	Citroën Dispatch/Jumpy official brochure	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/van-range/Dispatch_Brochure.pdf
EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	5115	1800	1780	Mitsubishi L200 IV owner manual; Ficha Completa Mitsubishi L200 Triton HPE 3.5 V6 2014	https://www.mitsubishiman.ru/en/L200/4_d/main/manual/tehnicheskie-harakteristiki-avtomobiley-l200;https://www.fichacompleta.com.br/en/carros/mitsubishi/l200-triton-hpe-3-5-v6-at-2014
EU-MITSUBISHI-PAJERO-IV-V85W-SUV-3D-01	4385	1875	1850	Mitsubishi Pajero official specification brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-V95W-SUV-5D-01	4900	1875	1870	Mitsubishi Pajero official specification brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-CHEVROLET-MONTE-CARLO-III-COUPE-01	5090	1816	1369	Automobile-Catalog 1979 Chevrolet Monte Carlo 5.0L V8; Automobile-Catalog 1980 Chevrolet Monte Carlo 5.0L V8	https://www.automobile-catalog.com/car/1979/204920/chevrolet_monte_carlo_5_0l_v-8_automatic.html;https://www.automobile-catalog.com/car/1980/205115/chevrolet_monte_carlo_5_0l_v-8_automatic.html
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920	Citroën UK Stellantis Media; Auto-Data Citroën SpaceTourer M 2.0 BlueHDi 120	https://www.media.stellantis.com/uk-en/citroen/press/new-engine-gearbox-option-for-citroen-spacetourer-mpv;https://www.auto-data.net/en/citroen-spacetourer-m-2.0-bluehdi-120hp-s-s-automatic-46442
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920	Citroën UK Stellantis Media; Auto-Data Citroën SpaceTourer XL 2.0 BlueHDi 120	https://www.media.stellantis.com/uk-en/citroen/press/new-engine-gearbox-option-for-citroen-spacetourer-mpv;https://www.auto-data.net/en/citroen-spacetourer-xl-2.0-bluehdi-120hp-s-s-automatic-46443
EU-MITSUBISHI-DELICA-SPACE-GEAR-L400-MPV-01	4655	1695	1855	Automobile-Catalog 1999 Mitsubishi Space Gear 2000 GLX	https://www.automobile-catalog.com/car/1999/2020010/mitsubishi_space_gear_2000_glx.html
EU-KIA-CERATO-III-FACELIFT-SEDAN-01	4560	1780	1435	Auto-Data Kia Cerato III Sedan facelift 2016 2.0 MPI	https://www.auto-data.net/en/kia-cerato-iii-sedan-facelift-2016-2.0-mpi-152hp-automatic-50046
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data Seat Toledo III 5P	https://www.auto-data.net/en/seat-toledo-iii-5p-generation-2911
EU-OPEL-ASTRA-H-FACELIFT-HATCHBACK-01	4249	1753	1460	Auto-Data Opel Astra H facelift 1.6 ECOTEC; Auto-Data Opel Astra H facelift 1.3 CDTI	https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-ecotec-115hp-47448;https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.3-cdti-ecotec-90hp-47452
EU-HYUNDAI-H100-II-VAN-01	4790	1690	1965	IKZ-HAUSTECHNIK Hyundai H100 compact transporter profile; Korejskevozy Hyundai H100 1997 technical data	https://www.ikz.de/ikz-archiv/1997/23/9723052.php;https://korejskevozy.cz/clanek/technicke-informace-hyundai-h-100-1997/?id=b563d190-c7e3-4d6e-8a0c-eea232d697ae&skupina=ae456b0a-24f3-4cdc-bc33-0688abef814f
EU-AIXAM-MEGA-MULTITRUCK-PLATFORM-01	3102	1476	1800	Swiss FEDRO MEGA Multitruck 400 type data; Swiss FEDRO MEGA Multitruck NE type data	https://v2.motoro.ch/en/fiche-technique/mega/multitruck-400;https://v2.motoro.ch/en/fiche-technique/mega/multitruck-ne
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695	Auto-Data Suzuki Grand Vitara II 5 Door 1.9 DDiS	https://www.auto-data.net/en/suzuki-grand-vitara-ii-5-door-1.9-ddis-129hp-16579
EU-CITROEN-C3-PICASSO-I-PREFL-MPV-01	4078	1766	1669	Auto-Data Citroën C3 I Picasso Phase I 1.6 VTi 115	https://www.auto-data.net/en/citroen-c3-i-picasso-phase-i-2008-1.6-vti-115hp-27454
EU-SUZUKI-SX4-I-SEDAN-01	4490	1730	1545	Auto-Data Suzuki SX4 I Sedan 1.6 VVT	https://www.auto-data.net/en/suzuki-sx4-i-sedan-1.6-i-16v-vvt-2wd-107hp-16564
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780	Land Rover Media 2017 Model Year Range Rover Sport; Automobile-Catalog 2017 Range Rover Sport 2.0 SD4	https://media.landrover.com/news/2016/08/new-engine-and-advanced-technology-range-rover-sport;https://www.automobile-catalog.com/car/2017/2564720/range-rover_sport_2_0_sd4.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Land Rover Range Rover Sport 2018 official brochure; Automobile-Catalog 2018 Range Rover Sport 2.0 SD4	https://stewartsautogroup.com/wp-content/uploads/2016/11/Range-Rover-Sport-Brochure-2018.pdf;https://www.automobile-catalog.com/car/2018/2606930/range-rover_sport_2_0_sd4.html
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Auto-Data Ford Kuga II facelift 1.5 TDCI	https://www.auto-data.net/en/ford-kuga-ii-facelift-2016-1.5-tdci-120hp-26011
EU-HONDA-CR-V-IV-FACELIFT-SUV-01	4557	1819	1654	Auto-Data Honda CR-V IV facelift 2.4 AWD	https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-2.4-i-vtec-185hp-awd-cvt-50947
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-220d-194hp-4matic-9g-tronic-29551
EU-CHEVROLET-CAPRICE-III-COUPE-1981-01	5387	1913	1387	Automobile-Catalog 1981 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1981/210005/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-COUPE-1982-1983-01	5387	1913	1433	Automobile-Catalog 1982 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1982/210500/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-III-COUPE-1984-01	5405	1915	1433	Automobile-Catalog 1984 Chevrolet Caprice Classic Coupe 5.0L V8	https://www.automobile-catalog.com/car/1984/1484000/chevrolet_caprice_classic_coupe_5_0l_v-8_automatic.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell (S213) E 400 V6 3.5 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-400-v6-3.5-333hp-4matic-9g-tronic-26418
EU-MERCEDES-BENZ-E-CLASS-S213-AMG-E43-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell (S213) AMG E 43 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-amg-e-43-401hp-4matic-9g-tronic-26467
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639	Auto-Data Mercedes-Benz GLC SUV (X253) GLC 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-glc-350d-258hp-4matic-g-tronic-27078
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600	Porsche Newsroom 2017 Macan Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A5c3a8aab-ba1b-4372-8052-bf157517f993/2017_Macan_Models_Technical_Data.pdf
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423	Porsche Newsroom 2017 Panamera press kit; Porsche Newsroom 2018 Panamera Technical Information	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf;https://newsroom.porsche.com/dam/jcr%3Ac629e2c4-a8db-46ad-9a14-3e9b59a3cc90/2018_Porsche_Panamera_Technical_Information.pdf
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427	Porsche Newsroom 2017 Panamera press kit	https://newsroom.porsche.com/dam/jcr%3Abaa79d62-86a0-4cf5-9eea-5776d1e96b40/PCNA18_0114_us.pdf
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639	Auto-Data Mercedes-Benz GLC SUV X253 AMG GLC 43 4MATIC	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-amg-glc-43-367hp-4matic-g-tronic-24365
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834	Auto-Data Volkswagen Amarok I Double Cab facelift 3.0 V6 TDI 204 4MOTION	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-204hp-4motion-automatic-27099
EU-TESLA-MODEL-S-FACELIFT-HATCHBACK-01	4970	1964	1445	Tesla Model S 2012-2020 Owner's Manual	https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-TESLA-MODEL-X-I-SUV-01	5052	1999	1684	Tesla Model X 2015-2020 Owner's Manual	https://www.tesla.com/ownersmanual/2015_2020_modelx/en_il/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	3700	1660	1595	Suzuki Ignis UK official brochure	https://www.autosynergy.co.uk/assets/brochures/suzuki-ignis.pdf
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	3700	1690	1595	Suzuki Ignis UK official brochure	https://www.autosynergy.co.uk/assets/brochures/suzuki-ignis.pdf
EU-CHEVROLET-IMPALA-IV-COUPE-1974-01	5657	2019	1364	Automobile-Catalog 1974 Chevrolet Impala Custom Coupe 350-4 V8	https://www.automobile-catalog.com/car/1974/116960/chevrolet_impala_custom_coupe_350-4_v-8_turbo-fire_hydra-matic.html
EU-VOLVO-S60-I-SEDAN-01	4576	1804	1428	Auto-Data Volvo S60 2.4 D	https://www.auto-data.net/en/volvo-s60-2.4-d-130hp-9219
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_601-700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://xr793.com/wp-content/uploads/2022/09/2006-Citroen-Van-Tech-Specs-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2006-Citroen-Van-Tech-Specs-UK.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（407 行）
- 累计尺寸组：dimension_groups_final.tsv（216 行）

