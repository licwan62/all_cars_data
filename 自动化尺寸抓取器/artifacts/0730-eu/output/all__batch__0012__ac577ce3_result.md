# 任务：all 第 1101-1200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0012__ac577ce3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1101-1200 行

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
all 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484
EU-FORD-TAUNUS-TC1-SEDAN-2D-01	4267	1701	1370
EU-FORD-TAUNUS-TC1-SEDAN-4D-01	4267	1701	1370
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311
EU-MAZDA-626-I-CB2-COUPE-01	4420	1690	1370
EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	4638	1939	1262
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-TOYOTA-C-HR-I-SUV-01	4360	1795	1565
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Jaguar	F-Type	3.0 Scv6 400 Sport AWD	Coupe	Allrad	Benzin	294	400	Nov 2016	-	2024-03-01	125817
Jaguar	F-Type	Scv6 400 Sport	Cabriolet	Heckantrieb	Benzin	294	400	Nov 2016	-	2024-03-01	125818
Jaguar	F-Type	Scv6 400 Sport AWD	Cabriolet	Allrad	Benzin	294	400	Nov 2016	-	2024-03-01	125819
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	43	58	Jan 1976	Jul 1979	2024-03-01	125827
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	41	56	Jan 1976	Jul 1979	2024-03-01	125828
Ford	Taunus	1.3	Kombi	Heckantrieb	Benzin	41	56	Jan 1976	Jul 1979	2024-03-01	125829
Ford	Taunus	1.3	Coupe	Heckantrieb	Benzin	40	54	Apr 1972	Feb 1976	2024-03-01	125830
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	46	63	Jul 1979	Jul 1982	2024-03-01	125838
KIA	Rio iv	1.25	Schrägheck	Frontantrieb	Benzin	62	84	Jan 2017	-	2024-03-01	125839
KIA	Rio iv	1.4	Schrägheck	Frontantrieb	Benzin	73	99	Jan 2017	-	2024-03-01	125840
KIA	Rio iv	1.0 T-gdi 100	Schrägheck	Frontantrieb	Benzin	74	101	Jan 2017	-	2024-03-01	125841
KIA	Rio iv	1.0 T-gdi 120	Schrägheck	Frontantrieb	Benzin	88	120	Jan 2017	-	2024-03-01	125842
KIA	Rio iv	1.4 Crdi 77	Schrägheck	Frontantrieb	Diesel	57	78	Jan 2017	-	2024-03-01	125843
KIA	Rio iv	1.4 Crdi 90	Schrägheck	Frontantrieb	Diesel	66	90	Jan 2017	-	2024-03-01	125844
Nissan	Bluebird	1.6	Stufenheck	Frontantrieb	Benzin	86	117	May 2013	-	2024-03-01	125847
Ford	Focus iii	2.0 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	103	140	Jan 2011	Jun 2014	2024-03-01	125852
Ford	Focus iii	1.6 TI	Kasten/Schrägheck	Frontantrieb	Benzin	77	105	Jan 2011	Feb 2020	2024-03-01	125853
Ford	Focus iii	1.6 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	110	150	Nov 2011	Jun 2014	2024-03-01	125855
Aston Martin	Lagonda i shooting brake	5.3	Kombi	Heckantrieb	Benzin	262	356	Nov 1985	Dec 1987	2024-03-01	125881
Aston Martin	Vantage	4.7 GT8	Coupe	Heckantrieb	Benzin	328	446	Jul 2013	-	2024-03-01	125883
Mazda	626 i	1.6	Coupe	Heckantrieb	Benzin	55	75	Sep 1978	Jul 1980	2024-03-01	125897
Mazda	818	1.3	Coupe	Heckantrieb	Benzin	44	60	Oct 1972	Dec 1978	2024-03-01	125898
Lexus	Rx	450h	SUV	Frontantrieb	Benzin/Elektro	230	313	Oct 2015	-	2024-03-01	125909
Mercedes-benz	G-Klasse	200 G	Geländewagen geschlossen	Allrad	Benzin	80	109	Jul 1982	Aug 1989	2024-03-01	125923
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen offen	Allrad	Diesel	165	224	Jun 2009	Dec 2011	2024-03-01	125925
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen geschlossen	Allrad	Diesel	165	224	Jun 2009	Dec 2011	2024-03-01	125926
Alfa Romeo	33	1.7 16V 4X4	Kombi	Allrad	Benzin	101	137	Jul 1990	Sep 1994	2024-03-01	125927
Porsche	911	3.0 Carrera GTS	Coupe	Heckantrieb	Benzin	331	450	Mar 2017	Dec 2019	2024-03-01	125932
Porsche	911	3.0 Carrera 4 GTS	Coupe	Allrad	Benzin	331	450	Mar 2017	Dec 2019	2024-03-01	125933
Porsche	911	3.0 Carrera GTS	Cabriolet	Heckantrieb	Benzin	331	450	Mar 2017	Dec 2019	2024-03-01	125934
Porsche	911	3.0 Carrera 4 GTS	Cabriolet	Allrad	Benzin	331	450	Mar 2017	Dec 2019	2024-03-01	125935
Porsche	911	3.0 Carrera 4 GTS	Targa	Allrad	Benzin	331	450	Mar 2017	Dec 2019	2024-03-01	125936
Mercedes-benz	S-Klasse	420 SEC	Coupe	Heckantrieb	Benzin	170	231	Sep 1986	Jun 1991	2024-03-01	125937
Mercedes-benz	Sl	350 SL	Cabriolet	Heckantrieb	Benzin	147	200	May 1971	Dec 1976	2024-03-01	125938
Mercedes-benz	Gl-Klasse	GL 63 AMG 4-matic	SUV	Allrad	Benzin	400	544	Jul 2012	Oct 2015	2024-03-01	125940
Renault	Zoe	ZOE	Schrägheck	Frontantrieb	Elektro	68	92	Sep 2016	-	2024-03-01	125941
Mercedes-benz	T1	407 D 2.4	Kasten	Heckantrieb	Diesel	53	72	Apr 1981	Jul 1982	2024-03-01	125942
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	228	310	Dec 2016	Aug 2020	2024-03-01	125943
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	228	310	Dec 2016	Aug 2020	2024-03-01	125944
Opel	Astra j caravan	1.4	Kombi	Frontantrieb	Benzin	64	87	Oct 2010	Oct 2015	2024-03-01	125949
Opel	Diplomat b	2.8	Stufenheck	Heckantrieb	Benzin	118	160	Sep 1971	Aug 1978	2024-03-01	125956
Nissan	Bluebird	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1987	Apr 1990	2024-03-01	125980
Renault	Kadjar	1.6 TCE 165	SUV	Frontantrieb	Benzin	120	163	Nov 2016	-	2024-03-01	125992
VW	Golf vii	2.0 R 4motion	Schrägheck	Allrad	Benzin	213	290	Dec 2016	Aug 2020	2024-03-01	125995
VW	Golf vii variant	2.0 R 4motion	Kombi	Allrad	Benzin	213	290	Dec 2016	Aug 2020	2024-03-01	125996
VW	Golf vii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	63	86	Jan 2017	Jul 2019	2024-03-01	125997
VW	Golf vii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	63	86	Jan 2017	Jul 2019	2024-03-01	125998
Skoda	Octavia	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	126000
Skoda	Octavia	1.6 TDI	Kombi	Frontantrieb	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	126001
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	180	245	Feb 2017	Oct 2020	2024-03-01	126002
Skoda	Octavia	2.0 TSI RS	Kombi	Frontantrieb	Benzin	180	245	Feb 2017	Oct 2020	2024-03-01	126003
Iveco	Daily vi	35s18, 55s18, 55c18, 70s18, 70c18 4X4	Pritsche/Fahrgestell	Allrad	Diesel	132	180	Apr 2016	-	2024-03-01	126004
Mercedes-benz	E-Klasse	E 180	Stufenheck	Heckantrieb	Benzin	115	156	Jan 2016	Jun 2019	2025-06-01	126006
VW	Golf vii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	180	245	Mar 2017	Aug 2020	2024-03-01	126007
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel	120	163	Oct 2016	Oct 2023	2024-03-01	126008
BMW	3	318 CI	Cabriolet	Heckantrieb	Benzin	100	136	Dec 2000	Aug 2006	2024-03-01	126010
Lancia	Gamma	2000	Coupe	Frontantrieb	Benzin	88	120	May 1981	Sep 1984	2024-03-01	126011
Alfa Romeo	Stelvio	2.2 D Q4	SUV	Allrad	Diesel	154	209	Dec 2016	-	2024-03-01	126013
Land Rover	Defender station wagon	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	100	136	Sep 1990	Jul 1994	2024-03-01	126014
Land Rover	110/127	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	100	136	Jan 1985	Jul 1990	2024-03-01	126015
Jaguar	F-Pace	2.0 TD4	SUV	Heckantrieb	Diesel	120	163	Feb 2017	-	2024-03-01	126020
Jaguar	F-Pace	2.0 SD4 AWD	SUV	Allrad	Diesel	177	241	Feb 2017	-	2024-03-01	126021
Jaguar	F-Pace	2.0 TI4 AWD	SUV	Allrad	Benzin	184	250	Feb 2017	-	2024-03-01	126022
German E Cars	Stromos	Elektro	Schrägheck	Frontantrieb	Elektro	56	76	Sep 2010	-	2024-03-01	126023
German E Cars	Cetos	Elektro	Schrägheck	Frontantrieb	Elektro	60	82	Sep 2011	-	2024-03-01	126024
German E Cars	Plantos	Elektro	Kasten	Frontantrieb	Elektro	85	116	Sep 2011	-	2024-03-01	126025
German E Cars	Plantos	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	85	116	Sep 2011	-	2024-03-01	126026
Isuzu	D-Max ii	1.9 DDI	Pick-up	Heckantrieb	Diesel	120	163	Mar 2017	Dec 2022	2024-03-01	126051
Isuzu	D-Max ii	1.9 DDI 4X4	Pick-up	Allrad	Diesel	120	163	Mar 2017	Dec 2022	2024-03-01	126055
Peugeot	Partner tepee	1.6 Bluehdi 100 4X4	Großraumlimousine	Allrad	Diesel	73	100	Apr 2015	-	2024-03-01	126060
BMW	5	525 I	Kombi	Heckantrieb	Benzin	155	211	Mar 2005	May 2010	2024-03-01	126064
Peugeot	604	2.8	Stufenheck	Heckantrieb	Benzin	114	155	Jan 1977	Dec 1981	2024-03-01	126065
BMW	Z4 roadster	2.5 SI	Cabriolet	Heckantrieb	Benzin	155	211	Sep 2005	Feb 2009	2024-03-01	126072
BMW	3	320 I	Kombi	Heckantrieb	Benzin	120	163	Sep 2000	Feb 2005	2024-03-01	126075
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	120	163	Sep 2000	Feb 2005	2024-03-01	126076
BMW	5	520 I	Kombi	Heckantrieb	Benzin	120	163	Sep 2000	Dec 2003	2024-03-01	126077
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	120	163	Sep 2000	Jun 2003	2024-03-01	126078
Audi	A3	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	126079
BMW	5	523 I	Kombi	Heckantrieb	Benzin	120	163	Sep 1998	Aug 2000	2024-03-01	126080
Audi	A3	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	115	Feb 2017	Oct 2020	2024-03-01	126081
Audi	A3	1.6 TDI	Stufenheck	Frontantrieb	Diesel	85	115	Mar 2017	Oct 2020	2024-03-01	126082
Subaru	Libero	1	Bus	Heckantrieb	Benzin	40	54	Jan 1984	Jul 1988	2024-03-01	126106
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	85	116	Dec 1999	Aug 2001	2024-03-01	126107
Subaru	Leone / loyale	1.8 Turbo 4WD	Coupe	Allrad	Benzin	100	136	Jun 1985	Oct 1989	2024-03-01	126109
BMW	3	323 CI	Coupe	Heckantrieb	Benzin	120	163	Apr 1999	Sep 2000	2024-03-01	126118
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	120	163	Mar 1998	Sep 2000	2024-03-01	126122
Subaru	Libero	1.0 4WD	Kasten	Allrad	Benzin	40	54	Jan 1984	May 1986	2024-03-01	126128
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	162	220	Jul 1987	Apr 1989	2024-03-01	126132
BMW	507	Touring Sport	Cabriolet	Heckantrieb	Benzin	103	140	Oct 1956	Jul 1959	2024-03-01	126135
BMW	507	Touring Sport	Cabriolet	Heckantrieb	Benzin	110	150	Oct 1956	Jul 1959	2024-03-01	126137
BMW	502	2.6	Stufenheck	Heckantrieb	Benzin	74	100	Sep 1954	Dec 1963	2024-03-01	126142
BMW	502	3.2	Stufenheck	Heckantrieb	Benzin	88	120	Sep 1954	Dec 1963	2024-03-01	126143
BMW	502	3.2 Super	Stufenheck	Heckantrieb	Benzin	103	140	Sep 1954	Dec 1963	2024-03-01	126144
BMW	340	340	Stufenheck	Heckantrieb	Benzin	40	55	Oct 1949	Jun 1952	2024-03-01	126152
Audi	A5	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	185	252	Mar 2017	Dec 2019	2024-03-01	126159
Audi	A5	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	140	190	Mar 2017	Dec 2019	2024-03-01	126160
Audi	A5	3.0 TDI	Cabriolet	Frontantrieb	Diesel	160	218	Mar 2017	Aug 2018	2024-03-01	126161
Audi	A5	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	140	190	Mar 2017	Apr 2020	2026-07-01	126162
Audi	A5	3.0 TDI	Schrägheck	Frontantrieb	Diesel	160	218	Mar 2017	Aug 2018	2024-03-01	126163
Toyota	C-Hr	1.8 Hybrid	SUV	Frontantrieb	Benzin/Elektro	90	122	Oct 2016	-	2024-03-01	126164


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先模式完成首批聚类：复用 14 个既有尺寸组，新建并闭合 12 个尺寸组。
* 已明确 Jaguar F-Type X152、Kia Rio IV YB、Audi A3 8V 三种车身分支；Porsche 911 GTS 根据官方技术表中不同车身及驱动版本的高度差分别建组。([meyermotoren.de][1])
* Kia Rio、Lexus RX 和 Porsche 911 的新尺寸组已核对不含后视镜宽度口径；来源已落入 DIMENSION_GROUP 表。([起亚新闻官网][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：40
* PENDING 映射：60
* 当前已引用尺寸组：26

  * 复用既有尺寸组：14
  * 本轮新建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125817	125817	Coupe	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH		READY
125818	125818	Convertible	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
125819	125819	Convertible	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
125839	125839	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125840	125840	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125841	125841	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125842	125842	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125843	125843	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125844	125844	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125897	125897	Coupe	626 I	CB2	2	EU-MAZDA-626-I-CB2-COUPE-01	HIGH		READY
125909	125909	SUV	RX IV	GYL20	5	EU-LEXUS-RX-IV-AL20-SUV-PREFL-01	MEDIUM	GYL20前驱混动车身边界。	READY
125932	125932	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	HIGH		READY
125933	125933	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	HIGH		READY
125934	125934	Convertible	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	HIGH		READY
125935	125935	Convertible	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	HIGH		READY
125936	125936	Targa	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-TARGA-4-GTS-01	HIGH	独立Targa车顶外廓。	READY
125937	125937	Coupe	S-Class W126 facelift	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	HIGH		READY
125940	125940	SUV	GL-Class II	X166	5	EU-MERCEDES-BENZ-GL-X166-SUV-AMG-PREFL-01	HIGH		READY
125941	125941	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH		READY
125944	125944	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
125992	125992	SUV	Kadjar I		5	EU-RENAULT-KADJAR-I-SUV-PREFL-01	HIGH		READY
125996	125996	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
125998	125998	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
126000	126000	Hatchback	Octavia III facelift	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	五门liftback外廓。	READY
126001	126001	Wagon	Octavia III facelift	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
126002	126002	Hatchback	Octavia III facelift	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	五门liftback外廓。	READY
126003	126003	Wagon	Octavia III facelift	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
126013	126013	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126064	126064	Wagon	5 Series E60/E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
126079	126079	Hatchback	A3 8V facelift	8V1	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门外廓。	READY
126081	126081	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	五门Sportback外廓。	READY
126082	126082	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
126107	126107	Coupe	3 Series E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH		READY
126118	126118	Coupe	3 Series E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH		READY
126159	126159	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126160	126160	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126161	126161	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126162	126162	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126163	126163	Hatchback	A5 II (F5)	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
126164	126164	SUV	C-HR I	ZYX10	5	EU-TOYOTA-C-HR-I-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	4482	1923	1308	CarExpert 2018 Jaguar F-Type 400 Sport Convertible; Automobile-Catalog 2017 Jaguar F-Type 400 Sport Convertible AWD	https://www.carexpert.com.au/jaguar/f-type/2018-400-sport-3l-convertible-rwd-petrol-automatic-josfwkgw20170721;https://www.automobile-catalog.com/car/2017/2559365/jaguar_f-type_400_sport_convertible_awd.html
EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	4065	1725	1450	Kia Rio 2017 Technical Specification	https://press.kia.com/content/dam/kiapress/EU/download-files/New-Rio/Kia-Rio-Technical-Specification-3-Feb-2017.doc
EU-LEXUS-RX-IV-AL20-SUV-PREFL-01	4890	1895	1685	Lexus RX Technical Specifications	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/220112M-RX-Tech-Spec.pdf
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	4935	1828	1407	Automobile-Catalog 1990 Mercedes-Benz 420 SEC	https://www.automobile-catalog.com/car/1990/1476020/mercedes-benz_420_sec_cat.html
EU-MERCEDES-BENZ-GL-X166-SUV-AMG-PREFL-01	5120	1934	1850	EncyCARpedia Mercedes GL 63 AMG	https://www.encycarpedia.com/mercedes/12-gl-63-amg-suv
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	4084	1730	1562	Automobile-Catalog 2017 Renault Zoe R90	https://www.automobile-catalog.com/car/2017/2984375/renault_zoe_r90.html
EU-RENAULT-KADJAR-I-SUV-PREFL-01	4449	1836	1613	Renault Kadjar 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Kadjar-2017-UK.pdf
```

## 下一步优先处理

1. 先拆解 Ford Taunus 的二门/四门、Coupe、Turnier 和 TC2/TC3 外廓边界。
2. 集中闭合 Mercedes-Benz G-Class、Land Rover Defender/110 的敞篷、封闭式及不同轴距分支。
3. 批量处理 Mercedes-Benz T1、Iveco Daily、Isuzu D-Max、German E Cars 和 Subaru Libero 等多轴距、多车顶或多用途车身。
4. 最后处理历史稀有车型及跨改款记录，包括 Lagonda Shooting Brake、BMW E46 Cabriolet、Ford Focus III Van 和 Golf VII 三门/五门边界。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/125817/jaguar/f-type_coupe_x152_/3_0_sc_v6_400_sport_awd_125817?utm_source=chatgpt.com "3.0 SC V6 400 SPORT AWD | F-Type Coupe (X152) | Jaguar | Manufacturers | Meyer Motoren"
[2]: https://press.kia.com/content/dam/kiapress/EU/download-files/New-Rio/Kia-Rio-Technical-Specification-3-Feb-2017.doc?utm_source=chatgpt.com "Download Kia Rio 2017 - technical specifications (Europe)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Ford Focus III 厢式五门的改款前尺寸组；Ktype `125853` 的生产区间跨越改款，已拆分为 `prefl` 与 `facelift` 两个物理分支，改款后分支复用既有尺寸组。([汽车目录][1])
* 闭合 Jaguar F-Pace X761 三个 Ktype，共用官方资料确认的改款前 SUV 外廓。([Jaguar][2])
* 闭合 BMW E39 轿车改款、旅行车改款前/后，以及 Z4 E85、6 Series E24、Lancia Gamma Coupe 等尺寸组。([汽车目录][3])
* 闭合 BMW 502 三个发动机 Ktype 的共用轿车外廓及 BMW 340 轿车尺寸组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：101
* READY 映射：57
* PENDING 映射：44
* 已处理 Ktype：56
* 已确认尺寸组：36
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125852	125852	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	五门厢式车外廓。	READY
125853_prefl	125853	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	Ktype生产区间跨越改款；改款前分支。	READY
125853_facelift	125853	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	HIGH	Ktype生产区间跨越改款；改款后分支。	READY
125855	125855	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	五门厢式车外廓。	READY
126020	126020	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126021	126021	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126022	126022	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126072	126072	Convertible	Z4 I facelift	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH	E85改款后Roadster外廓。	READY
126077	126077	Wagon	5 Series E39 facelift	E39	5	EU-BMW-5-E39-WAGON-FACELIFT-01	HIGH		READY
126078	126078	Sedan	5 Series E39 facelift	E39	4	EU-BMW-5-E39-SEDAN-FACELIFT-01	HIGH		READY
126080	126080	Wagon	5 Series E39 pre-facelift	E39	5	EU-BMW-5-E39-WAGON-PREFL-01	HIGH		READY
126011	126011	Coupe	Gamma Coupe Series 2	830	2	EU-LANCIA-GAMMA-830-COUPE-SERIES-2-01	HIGH	第二系列双门Coupe外廓。	READY
126132	126132	Coupe	6 Series E24 facelift	E24	2	EU-BMW-6-E24-COUPE-FACELIFT-01	HIGH	1987年后期E24外廓。	READY
126142	126142	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126143	126143	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126144	126144	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126152	126152	Sedan	340	340	4	EU-BMW-340-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-PREFL-VAN-5D-01	4358	1823	1484	Ford Focus UK brochure; Automobile-Catalog 2011 Ford Focus 1.6 Ti-VCT	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Focus-2010-UK.pdf;https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html
EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	4731	1936	1652	Jaguar All-New F-Pace official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-FPAC17-PRT0520_F_PACE_17MY_MB_GEE%20UPDATE_V3.pdf
EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	4091	1781	1299	Automobile-Catalog 2006 BMW Z4 Roadster 2.5si	https://www.automobile-catalog.com/car/2006/281015/bmw_z4_roadster_2_5si.html
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445	Automobile-Catalog 2001 BMW 520i Touring	https://www.automobile-catalog.com/car/2001/273785/bmw_520i_touring.html
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435	Automobile-Catalog 2001 BMW 520i	https://www.automobile-catalog.com/car/2001/273530/bmw_520i.html
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445	Automobile-Catalog 1999 BMW 523i Touring	https://www.automobile-catalog.com/car/1999/273275/bmw_523i_touring.html
EU-LANCIA-GAMMA-830-COUPE-SERIES-2-01	4485	1730	1330	Automobile-Catalog 1981 Lancia Gamma Coupe 2000 Series 2	https://www.automobile-catalog.com/car/1981/1378490/lancia_gamma_coupe_2000_2a_serie.html
EU-BMW-6-E24-COUPE-FACELIFT-01	4815	1725	1365	Automobile-Catalog 1988 BMW 635 CSi	https://www.automobile-catalog.com/car/1988/264185/bmw_635_csi.html
EU-BMW-502-SEDAN-01	4730	1780	1530	Automobile-Catalog 1958 BMW 502 2.6L; Automobile-Catalog 1958 BMW 502 3.2L Super	https://www.automobile-catalog.com/car/1958/262055/bmw_502_2_6l.html;https://www.automobile-catalog.com/car/1958/262115/bmw_502_3_2l_super.html
EU-BMW-340-SEDAN-01	4600	1765	1630	Automobile-Catalog 1950 BMW 340	https://www.automobile-catalog.com/car/1950/2065490/bmw_340.html
```

## 下一步优先处理

1. 集中闭合 Mercedes-Benz G-Class、Land Rover Defender Station Wagon 与 110/127 的轴距、封闭式和敞篷分支。
2. 处理 Mercedes-Benz T1、Iveco Daily VI、Isuzu D-Max II、German E Cars Plantos 等多轴距、多车顶或多驾驶室车型。
3. 随后处理 Ford Taunus、Nissan Bluebird、Subaru Libero及剩余历史稀有车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html?utm_source=chatgpt.com "2011 Ford Focus 1.6 Ti-VCT (105) Titanium (man. 5)"
[2]: https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-FPAC17-PRT0520_F_PACE_17MY_MB_GEE%20UPDATE_V3.pdf?utm_source=chatgpt.com "ALL-NEW JAGUAR F-PACE"
[3]: https://www.automobile-catalog.com/car/2001/273530/bmw_520i.html?utm_source=chatgpt.com "Detailed specs review of 2001 BMW 520i model for Europe"
[4]: https://www.automobile-catalog.com/car/1958/262100/bmw_502_3_2l.html?utm_source=chatgpt.com "1958 BMW 502 3.2L Specs Review (88 kW / 120 PS / 118 hp) (up to mid-year 1958 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 16 个剩余 Ktype，新增 19 条 READY 映射。
* Golf VII facelift 四个 Ktype 直接复用既有五门 Hatchback 尺寸组；BMW E46 跨改款记录按 Cabriolet、Touring、Sedan 的实际改款边界拆分。([维基百科][1])
* 首次闭合 Vantage GT8 宽体、Alfa 33 Sportwagon 4x4、Astra J Sports Tourer、Diplomat B、350 SL R107、Peugeot 604、BMW 507 及四个 E46 尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：72
* PENDING Ktype：28
* READY 映射：76
* PENDING 映射：28
* 当前映射总行数：104
* 已确认并被当前批次引用的尺寸组：50
* 本轮首次创建尺寸组：11
* 本轮新增复用既有尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125883	125883	Coupe	V8 Vantage I facelift	VH2	2	EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	HIGH	GT8宽体空气动力学外廓。	READY
125927	125927	Wagon	33 Tipo 907 Series 2	907B1H	5	EU-ALFA-ROMEO-33-907-SPORTWAGON-4X4-01	HIGH	907B1H五门四驱Sportwagon外廓。	READY
125938	125938	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	HIGH		READY
125943	125943	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
125949	125949	Wagon	Astra J		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-01	HIGH		READY
125956	125956	Sedan	Diplomat B		4	EU-OPEL-DIPLOMAT-B-SEDAN-01	HIGH		READY
125995	125995	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
125997	125997	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
126007	126007	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
126010_prefl	126010	Convertible	3 Series E46 pre-facelift	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间跨越Cabriolet改款；改款前分支。	READY
126010_facelift	126010	Convertible	3 Series E46 facelift	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间跨越Cabriolet改款；改款后分支。	READY
126065	126065	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH		READY
126075_prefl	126075	Wagon	3 Series E46 pre-facelift	E46/3	5	EU-BMW-3-E46-WAGON-PREFL-01	HIGH	Ktype生产区间跨越Touring改款；改款前分支。	READY
126075_facelift	126075	Wagon	3 Series E46 facelift	E46/3	5	EU-BMW-3-E46-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨越Touring改款；改款后分支。	READY
126076_prefl	126076	Sedan	3 Series E46 pre-facelift	E46/4	4	EU-BMW-3-E46-SEDAN-PREFL-01	HIGH	Ktype生产区间跨越Sedan改款；改款前分支。	READY
126076_facelift	126076	Sedan	3 Series E46 facelift	E46/4	4	EU-BMW-3-E46-SEDAN-FACELIFT-01	HIGH	Ktype生产区间跨越Sedan改款；改款后分支。	READY
126122	126122	Sedan	3 Series E46 pre-facelift	E46/4	4	EU-BMW-3-E46-SEDAN-PREFL-01	HIGH		READY
126135	126135	Convertible	507	507	2	EU-BMW-507-CONVERTIBLE-01	HIGH		READY
126137	126137	Convertible	507	507	2	EU-BMW-507-CONVERTIBLE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	4540	1915	1250	Automobile-Catalog 2016 Aston Martin Vantage GT8	https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html
EU-ALFA-ROMEO-33-907-SPORTWAGON-4X4-01	4200	1614	1375	Motor Sport Alfa Romeo 33 Sport Wagon 16V 4x4; Automobile-Catalog 1991 Alfa Romeo 33 Sport Wagon 4x4	https://www.motorsportmagazine.com/archive/article/may-1991/34/new-cars-alfa-romeo-33-s-16v-cloverleaf-and-sport-wagon-16v/;https://www.automobile-catalog.com/car/1991/217055/alfa_romeo_33_1_7_ie_sport_wagon_4x4.html
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300	Automobile-Catalog 1971 Mercedes-Benz 350 SL	https://www.automobile-catalog.com/car/1971/1469240/mercedes-benz_350_sl.html
EU-OPEL-ASTRA-J-SPORTS-TOURER-01	4698	1814	1535	Vauxhall Astra Sports Tourer official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/cars/astra/Astra_ST_Spec_PG_18_October_2013.pdf
EU-OPEL-DIPLOMAT-B-SEDAN-01	4920	1852	1450	Automobile-Catalog 1976 Opel Diplomat 2.8 160 PS	https://www.automobile-catalog.com/car/1976/2417555/opel_diplomat_e.html
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430	Automobile-Catalog 1977 Peugeot 604 SL V6	https://www.automobile-catalog.com/car/1977/2567315/peugeot_604_sl_v6.html
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372	Automobile-Catalog 2004 BMW 318Ci Cabrio	https://www.automobile-catalog.com/car/2004/276500/bmw_318ci_cabrio.html
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409	Automobile-Catalog 1999 BMW 320i Touring	https://www.automobile-catalog.com/car/1999/274760/bmw_320i_touring.html
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409	Automobile-Catalog 2004 BMW 318i Touring	https://www.automobile-catalog.com/car/2004/275450/bmw_318i_touring.html
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415	Automobile-Catalog 1999 BMW 320i	https://www.automobile-catalog.com/car/1999/274415/bmw_320i.html
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275	Automobile-Catalog 1956 BMW 507	https://www.automobile-catalog.com/car/1956/262385/bmw_507_3_70_axle_standard.html
```

## 下一步优先处理

1. 闭合 Ford Taunus TC2/TC3 的二门、四门、Coupe 与 Turnier 分支。
2. 处理 Mercedes-Benz G-Class 与 Land Rover Defender/110 的轴距、敞篷及封闭式外廓。
3. 集中处理 T1、Daily VI、D-Max II、Plantos 等多轴距、多驾驶室或多车顶车型。
4. 最后处理 Nissan Bluebird、Mazda 818、Subaru Libero、German E Cars 及 Lagonda Shooting Brake 等剩余记录。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/BMW_3_Series_%28E46%29?utm_source=chatgpt.com "BMW 3 Series (E46)"
[2]: https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html?utm_source=chatgpt.com "2016 Aston Martin Vantage GT8 Sportshift Specs Review (328.2 kW / 446.4 PS / 440 hp) (since Q4 2016 for Europe special edition)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Ford Taunus TC1、TC2、TC3 的 Coupe、Turnier 以及二门/四门轿车分支，两个轿车 Ktype 按实际门数拆分。([汽车目录][1])
* Nissan Bluebird 1987–1990 记录按 T12 与改款后 T72 的长度变化拆分；Mazda 818 Coupe 按改款前后外廓拆分。([汽车目录][2])
* 闭合 Nissan Sylphy B17、Mercedes-Benz W213 改款前后、Partner Tepee Dangel 4×4、Subaru Libero E10 和 Leone III Coupe 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：86
* PENDING Ktype：14
* READY 映射：96
* PENDING 映射：14
* 当前映射总行数：110
* 已确认并被当前批次引用的尺寸组：67
* 本轮首次创建尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125827_2d	125827	Sedan	Taunus TC2	GBTS	2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125827_4d	125827	Sedan	Taunus TC2	GBTS	4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125828_2d	125828	Sedan	Taunus TC2	GBTS	2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125828_4d	125828	Sedan	Taunus TC2	GBTS	4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125829	125829	Wagon	Taunus TC2	GBNS	5	EU-FORD-TAUNUS-TC2-WAGON-5D-01	HIGH	Turnier五门外廓。	READY
125830	125830	Coupe	Taunus TC1	GBCK	2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
125838_2d	125838	Sedan	Taunus TC3	GBFS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125838_4d	125838	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125847	125847	Sedan	Sylphy B17	B17	4	EU-NISSAN-SYLPHY-B17-SEDAN-01	MEDIUM	Bluebird名称对应B17 Sylphy四门车身。	READY
125898_prefl	125898	Coupe	818 I pre-facelift		2	EU-MAZDA-818-I-COUPE-PREFL-01	MEDIUM	Ktype生产区间跨越车身改款；改款前分支。	READY
125898_facelift	125898	Coupe	818 I facelift		2	EU-MAZDA-818-I-COUPE-FACELIFT-01	HIGH	Ktype生产区间跨越车身改款；改款后分支。	READY
125980_prefl	125980	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越1988年改款；改款前分支。	READY
125980_facelift	125980	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越1988年改款；改款后分支。	READY
126006	126006	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-RWD-01	HIGH		READY
126008_prefl	126008	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-4MATIC-01	HIGH	Ktype生产区间跨越W213改款；改款前分支。	READY
126008_facelift	126008	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-4MATIC-01	HIGH	Ktype生产区间跨越W213改款；改款后分支。	READY
126060	126060	MPV	Partner II facelift	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-01	MEDIUM	Dangel四驱Tepee外廓。	READY
126106	126106	MPV	Libero E10		4	EU-SUBARU-LIBERO-E10-MICROVAN-01	MEDIUM	E10客运车身。	READY
126109	126109	Coupe	Leone III		3	EU-SUBARU-LEONE-III-COUPE-4WD-01	HIGH	三门Coupe外廓。	READY
126128	126128	Van	Libero E10		4	EU-SUBARU-LIBERO-E10-MICROVAN-01	MEDIUM	E10货运车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TAUNUS-TC2-SEDAN-2D-01	4340	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 L	https://www.automobile-catalog.com/car/1976/920945/ford_taunus_1_3_l.html
EU-FORD-TAUNUS-TC2-SEDAN-4D-01	4340	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 L	https://www.automobile-catalog.com/car/1976/920945/ford_taunus_1_3_l.html
EU-FORD-TAUNUS-TC2-WAGON-5D-01	4440	1700	1366	Automobile-Catalog 1976 Ford Taunus Turnier 1.3 L	https://www.automobile-catalog.com/car/1976/921230/ford_taunus_turnier_1_3_l_low_compr_.html
EU-FORD-TAUNUS-TC1-COUPE-01	4267	1708	1341	Automobile-Catalog 1972 Ford Taunus 1300 L Coupe	https://www.automobile-catalog.com/car/1972/911990/ford_taunus_1300_l_coupe.html
EU-FORD-TAUNUS-TC3-SEDAN-2D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.3	https://www.automobile-catalog.com/car/1980/921815/ford_taunus_1_3.html
EU-FORD-TAUNUS-TC3-SEDAN-4D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.3	https://www.automobile-catalog.com/car/1980/921815/ford_taunus_1_3.html
EU-NISSAN-SYLPHY-B17-SEDAN-01	4625	1760	1495	Nissan Sylphy Specifications	https://i.i-sgcm.com/new_cars/cars/11294/brochures/brochure_20160927100751.pdf
EU-MAZDA-818-I-COUPE-PREFL-01	3970	1595	1350	Automobile-Catalog 1973 Mazda Grand Familia 1300 GF Coupe	https://www.automobile-catalog.com/car/1973/1583375/mazda_grand_familia_gf_coupe.html
EU-MAZDA-818-I-COUPE-FACELIFT-01	4075	1595	1350	Automobile-Catalog 1975 Mazda 818 Coupe 1300	https://www.automobile-catalog.com/car/1975/1584395/mazda_818_coupe_1300.html
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-PREFL-01	4365	1690	1395	Automobile-Catalog 1987 Nissan Bluebird 1.8 GS 5-door	https://www.automobile-catalog.com/car/1987/2236235/nissan_bluebird_1_8_gs_5-d_automatic.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-FACELIFT-01	4420	1690	1395	Automobile-Catalog 1990 Nissan Bluebird 1.6 LS 5-door	https://www.automobile-catalog.com/car/1990/2236610/nissan_bluebird_1_6_ls_5-d.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-RWD-01	4923	1852	1468	Automobile-Catalog 2018 Mercedes-Benz E 220 d	https://www.automobile-catalog.com/car/2018/2297795/mercedes-benz_e_220_d.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-4MATIC-01	4923	1852	1468	Automobile-Catalog 2018 Mercedes-Benz E 220 d 4Matic	https://www.automobile-catalog.com/car/2018/2504390/mercedes-benz_e_220_d_4matic.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-4MATIC-01	4935	1852	1467	Automobile-Catalog 2021 Mercedes-Benz E 220 d 4Matic	https://www.automobile-catalog.com/car/2021/2968295/mercedes-benz_e_220_d_4matic.html
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-01	4380	1810	1801	UltimateSpecs Peugeot Partner II Tepee Dangel 4x4	https://www.ultimatespecs.com/car-specs/Peugeot/65340/Peugeot-Partner-2-Tepee-4x4-Dangel-Extreme-HDi-92.html
EU-SUBARU-LIBERO-E10-MICROVAN-01	3410	1430	1870	Automobile-Catalog 1984 Subaru E10 Wagon 2WD; Automobile-Catalog 1984 Subaru E10 Van 2WD; Automobile-Catalog 1985 Subaru E10 Wagon 4WD	https://www.automobile-catalog.com/car/1984/3224420/subaru_e10_wagon_2wd.html;https://www.automobile-catalog.com/car/1984/3224435/subaru_e10_van_2wd.html;https://www.automobile-catalog.com/car/1985/48365/subaru_e-10.html
EU-SUBARU-LEONE-III-COUPE-4WD-01	4370	1660	1405	Automobile-Catalog 1986 Subaru Leone 4WD 3-door Coupe RX II Turbo	https://www.automobile-catalog.com/car/1986/3213125/subaru_leone_4wd_3door_coupe_1_8_rxii_turbo.html
```

## 下一步优先处理

1. 闭合 Mercedes-Benz G-Class 的 W460、W463 封闭式及 Cabriolet 轴距分支。
2. 闭合 Land Rover Defender 110 Station Wagon 与早期 110/127 轴距分支。
3. 处理 Mercedes-Benz T1、Iveco Daily VI、German E Cars Plantos 的多轴距、驾驶室和车顶分支。
4. 最后处理 Lagonda Shooting Brake、Stromos、Cetos 与 Isuzu D-Max II 驾驶室分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/911990/ford_taunus_1300_l_coupe.html?utm_source=chatgpt.com "1972 Ford Taunus 1300 L Coupe Specs Review (43.5 kW / 59 PS / 58 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/2236235/nissan_bluebird_1_8_gs_5-d_automatic.html?utm_source=chatgpt.com "1987 Nissan Bluebird 1.8 GS 5-d automatic Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1987 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz G-Class 三个 Ktype：W460 按短轴/长轴及 1987 年 10 月前后尺寸变化拆分；W463 G 350 CDI 按短轴 Cabriolet、短轴封闭式和长轴封闭式拆分。输入 `125923` 的 `200 G` 与 80 kW/109 hp 不一致，映射按官方档案对应的 230 G 处理并保留说明。([marsClassic][1])
* 闭合 Isuzu D-Max II 两个 Ktype：4×2 对应 Single Cab；4×4 按 Single Cab、Extended Cab、Double Cab及不同原厂车高配置拆分。([摩托资产][2])
* 闭合 German E Cars Stromos 和 Cetos；Stromos 使用原厂资料尺寸，Cetos 按五门 Opel Corsa D 基础车身建立尺寸组。([casacota.net][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：93
* PENDING Ktype：7
* READY 映射：111
* PENDING 映射：7
* 当前映射总行数：118
* 已确认并被当前批次引用的尺寸组：82
* 本轮新增 READY 映射：15
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125923_swb_pre87	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-W460-SUV-SWB-PRE87-01	MEDIUM	输入版本名与功率不一致；按官方230 G短轴封闭式、1987年10月前外廓。	READY
125923_swb_post87	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-W460-SUV-SWB-POST87-01	MEDIUM	输入版本名与功率不一致；按官方230 G短轴封闭式、1987年10月后外廓。	READY
125923_lwb_pre87	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-W460-SUV-LWB-PRE87-01	MEDIUM	输入版本名与功率不一致；按官方230 G长轴封闭式、1987年10月前外廓。	READY
125923_lwb_post87	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-W460-SUV-LWB-POST87-01	MEDIUM	输入版本名与功率不一致；按官方230 G长轴封闭式、1987年10月后外廓。	READY
125925	125925	Convertible	G-Class W463	463.303	3	EU-MERCEDES-BENZ-G-W463-CONVERTIBLE-SWB-01	HIGH	短轴Cabriolet外廓。	READY
125926_swb	125926	SUV	G-Class W463	463.340	3	EU-MERCEDES-BENZ-G-W463-SUV-SWB-01	HIGH	短轴封闭式外廓。	READY
125926_lwb	125926	SUV	G-Class W463	463.341	5	EU-MERCEDES-BENZ-G-W463-SUV-LWB-01	HIGH	长轴封闭式外廓。	READY
126023	126023	Hatchback	Stromos		5	EU-GERMAN-E-CARS-STROMOS-HATCHBACK-5D-01	HIGH	五门Stromos电动车身。	READY
126024	126024	Hatchback	Cetos		5	EU-GERMAN-E-CARS-CETOS-HATCHBACK-5D-01	MEDIUM	基于五门Opel Corsa D车身。	READY
126051	126051	Pickup	D-Max II facelift		2	EU-ISUZU-D-MAX-II-PICKUP-4X2-SINGLECAB-01	HIGH	4×2 Single Cab外廓。	READY
126055_singlecab	126055	Pickup	D-Max II facelift		2	EU-ISUZU-D-MAX-II-PICKUP-4X4-SINGLECAB-01	HIGH	4×4 Single Cab外廓。	READY
126055_extendedcab_utility	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-UTILITY-01	HIGH	4×4 Extended Cab Utility车高分支。	READY
126055_extendedcab_hightrim	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-HIGHTRIM-01	HIGH	4×4 Extended Cab高配置车高分支。	READY
126055_doublecab_utility	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-UTILITY-01	HIGH	4×4 Double Cab Utility/Eiger车高分支。	READY
126055_doublecab_hightrim	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-HIGHTRIM-01	HIGH	4×4 Double Cab Yukon/Utah/Blade车高分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-W460-SUV-SWB-PRE87-01	3945	1700	1960	Mercedes-Benz Public Archive 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-W460-SUV-SWB-POST87-01	3955	1700	1925	Mercedes-Benz Public Archive 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-W460-SUV-LWB-PRE87-01	4395	1700	1950	Mercedes-Benz Public Archive 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-W460-SUV-LWB-POST87-01	4405	1700	1920	Mercedes-Benz Public Archive 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-W463-CONVERTIBLE-SWB-01	4257	1760	1941	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-W463-SUV-SWB-01	4212	1760	1931	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-W463-SUV-LWB-01	4662	1760	1931	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039060
EU-GERMAN-E-CARS-STROMOS-HATCHBACK-5D-01	3715	1680	1590	German E Cars Stromos brochure	https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf
EU-GERMAN-E-CARS-CETOS-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure;eMobilität Online German E-Cars Cetos	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf;https://emobilitaet.online/e-katalog/1241-das-elektromobil-des-monats-august-der-cetos-von-german-e-cars
EU-ISUZU-D-MAX-II-PICKUP-4X2-SINGLECAB-01	5315	1775	1685	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-SINGLECAB-01	5315	1860	1780	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-UTILITY-01	5295	1860	1780	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-HIGHTRIM-01	5295	1860	1790	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-UTILITY-01	5295	1860	1785	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-HIGHTRIM-01	5295	1860	1795	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
```

## 下一步优先处理

1. 闭合 Land Rover Defender Station Wagon 与早期 110/127 的 90、110、127 轴距和封闭式车身边界。
2. 处理 Mercedes-Benz T1 407 D、Iveco Daily VI 4×4 的轴距、车顶和底盘驾驶室分支。
3. 处理 German E Cars Plantos Van/Pritsche 的 Sprinter基础车身分支。
4. 最后核对 Aston Martin Lagonda Shooting Brake 的改装车身三维；完成剩余 7 个 Ktype 后直接输出最终完整 TSV 和下载链接。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640 "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640"
[2]: https://asset.moto.it/pricelist/auto/9221a6a601f4727825b9f7fc8c05304f/brochure-2017.pdf "https://asset.moto.it/pricelist/auto/9221a6a601f4727825b9f7fc8c05304f/brochure-2017.pdf"
[3]: https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf "https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Aston Martin Lagonda Series 3 的 Roos Engineering 单一 Shooting Brake 改装车身；尺寸沿用该车基础外廓，并以改装车型资料确认 Wagon 物理边界。([汽车目录][1])
* `126014` 明确覆盖 Defender 90 与 Defender 110 Station Wagon，按短轴三门和长轴五门拆分为两个尺寸组。([Ak24 Parts][2])
* `126015` 的 `110/127 (LDH)` 明确包含两个物理外廓，拆分为 One Ten Station Wagon 与 One Two Seven Double Cab Pickup。([Autodoc][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：96
* PENDING Ktype：4
* READY 映射：116
* PENDING 映射：4
* 当前映射总行数：120
* 已确认并被当前批次引用的尺寸组：87
* 本轮新增 READY 映射：5
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125881	125881	Wagon	Lagonda Series 3 Shooting Brake		5	EU-ASTON-MARTIN-LAGONDA-SERIES-3-SHOOTING-BRAKE-01	MEDIUM	Roos Engineering单一Shooting Brake改装车身。	READY
126014_90	126014	SUV	Defender I	L316	3	EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-90-01	HIGH	Ktype覆盖90与110 Station Wagon；90短轴分支。	READY
126014_110	126014	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-110-01	HIGH	Ktype覆盖90与110 Station Wagon；110长轴分支。	READY
126015_110	126015	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-STATION-WAGON-110-01	HIGH	LDH覆盖110与127；110 Station Wagon分支。	READY
126015_127	126015	Pickup	Land Rover One Two Seven	LDH	4	EU-LAND-ROVER-ONE-TWO-SEVEN-DOUBLE-CAB-127-01	MEDIUM	LDH覆盖110与127；127 Double Cab Pickup分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-LAGONDA-SERIES-3-SHOOTING-BRAKE-01	5283	1816	1302	Aston Martin Lagonda official specifications; Automobile-Catalog 1987 Aston Martin Lagonda; Aston Martins Lagonda V8 Shooting Brake by Roos	https://www.astonmartin.com/en/models/past-models/lagonda;https://www.automobile-catalog.com/car/1987/227540/aston_martin_lagonda_automatic.html;https://astonmartins.com/car/lagonda-v8-shooting-brake-by-roos/
EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-90-01	3883	1790	1963	Automobile-Catalog 1991 Land-Rover Defender 90 Station Wagon V8	https://www.automobile-catalog.com/car/1991/1395005/land-rover_defender_90_station_wagon_v8.html
EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-110-01	4599	1790	2035	Automobile-Catalog 1991 Land-Rover Defender 110 Station Wagon V8	https://www.automobile-catalog.com/car/1991/1395245/land-rover_defender_110_station_wagon_v8.html
EU-LAND-ROVER-ONE-TEN-STATION-WAGON-110-01	4580	1790	1996	Automobile-Catalog 1986 Land-Rover 110 County V8	https://www.automobile-catalog.com/car/1986/1394405/land-rover_110_county_v8.html
EU-LAND-ROVER-ONE-TWO-SEVEN-DOUBLE-CAB-127-01	5132	1790	2035	Automobile-Catalog 1990 Land-Rover Defender 130 Double Cab V8	https://www.automobile-catalog.com/car/1990/1395050/land-rover_defender_130_double_cab_v8.html
```

## 下一步优先处理

1. 闭合 `125942` Mercedes-Benz T1 407 D，按 `611.367/611.368` 面包车底盘核定轴距和车顶分支。
2. 闭合 `126004` Iveco Daily VI 4×4 的 `35S/55S/55C/70S/70C` 底盘驾驶室及轴距分支。
3. 闭合 `126025`、`126026` German E Cars Plantos 的 Sprinter 厢式车和底盘平台分支。
4. 剩余四个 Ktype 全部闭合后，下一轮直接输出两张最终完整 TSV、指定 sandbox 下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/227540/aston_martin_lagonda_automatic.html?utm_source=chatgpt.com "1987 Aston Martin Lagonda Specs Review (227.5 kW ..."
[2]: https://www.ak24parts.com/en/land-rover-spareparts/126014/defender-station-wagon-l316-l315-3-5-4x4?srsltid=AfmBOoopwe4zZ05LctRJr1hiazFvPcKFVjFg_yffaAlUet0F-Te7XR08&utm_source=chatgpt.com "LAND ROVER DEFENDER Station Wagon (L316, L315)"
[3]: https://www.autodoc24.fr/spares/land-rover/90-110/90-110-dhmc/126015-3-5-4x4?utm_source=chatgpt.com "Parts LAND ROVER 110/127 (LDH) 3.5 4x4 136 hp Petrol 1985 ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后 4 个 Ktype 已闭合：Mercedes-Benz T1 按 3350/3700 mm 轴距拆分；Iveco Daily VI 4×4 按短、中、长轴底盘拆分；Plantos 分为长轴超高顶厢式车和长轴底盘驾驶室。T1 尺寸表明确列出 3350 与 3700 mm 轴距对应的整车三维；Iveco 官方规格表给出了三种轴距的长度、不含后视镜宽度和高度。([poomkudy.com][1])
* Plantos 已按 5 吨 Mercedes-Benz Sprinter 基础车型闭合；资料明确对应长轴、超高顶 Sprinter 513，Sprinter 技术图确认长轴超高顶外廓。([journals.open.tudelft.nl][2])
* 已完成固定表头、唯一键、映射引用、正整数三维、来源非空及孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：123
* 最终尺寸组：95
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 未闭合映射引用：0
* 孤立尺寸组：0
* 机械校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125817	125817	Coupe	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH		READY
125818	125818	Convertible	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
125819	125819	Convertible	F-Type I facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
125827_2d	125827	Sedan	Taunus TC2	GBTS	2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125827_4d	125827	Sedan	Taunus TC2	GBTS	4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125828_2d	125828	Sedan	Taunus TC2	GBTS	2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125828_4d	125828	Sedan	Taunus TC2	GBTS	4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125829	125829	Wagon	Taunus TC2	GBNS	5	EU-FORD-TAUNUS-TC2-WAGON-5D-01	HIGH	Turnier五门外廓。	READY
125830	125830	Coupe	Taunus TC1	GBCK	2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
125838_2d	125838	Sedan	Taunus TC3	GBFS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	同一Ktype覆盖二门和四门轿车；二门分支。	READY
125838_4d	125838	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	同一Ktype覆盖二门和四门轿车；四门分支。	READY
125839	125839	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125840	125840	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125841	125841	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125842	125842	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125843	125843	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125844	125844	Hatchback	Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	HIGH		READY
125847	125847	Sedan	Sylphy B17	B17	4	EU-NISSAN-SYLPHY-B17-SEDAN-01	MEDIUM	Bluebird名称对应B17 Sylphy四门车身。	READY
125852	125852	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	五门厢式车外廓。	READY
125853_prefl	125853	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	Ktype生产区间跨越改款；改款前分支。	READY
125853_facelift	125853	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	HIGH	Ktype生产区间跨越改款；改款后分支。	READY
125855	125855	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-PREFL-VAN-5D-01	HIGH	五门厢式车外廓。	READY
125881	125881	Wagon	Lagonda Series 3 Shooting Brake		5	EU-ASTON-MARTIN-LAGONDA-SERIES-3-SHOOTING-BRAKE-01	MEDIUM	Roos Engineering单一Shooting Brake改装车身。	READY
125883	125883	Coupe	V8 Vantage I facelift	VH2	2	EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	HIGH	GT8宽体空气动力学外廓。	READY
125897	125897	Coupe	626 I	CB2	2	EU-MAZDA-626-I-CB2-COUPE-01	HIGH		READY
125898_prefl	125898	Coupe	818 I pre-facelift		2	EU-MAZDA-818-I-COUPE-PREFL-01	MEDIUM	Ktype生产区间跨越车身改款；改款前分支。	READY
125898_facelift	125898	Coupe	818 I facelift		2	EU-MAZDA-818-I-COUPE-FACELIFT-01	HIGH	Ktype生产区间跨越车身改款；改款后分支。	READY
125909	125909	SUV	RX IV	GYL20	5	EU-LEXUS-RX-IV-AL20-SUV-PREFL-01	MEDIUM	GYL20前驱混动车身边界。	READY
125923_swb_pre87	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-W460-SUV-SWB-PRE87-01	MEDIUM	输入版本名与功率不一致；按官方230 G短轴封闭式、1987年10月前外廓。	READY
125923_swb_post87	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-W460-SUV-SWB-POST87-01	MEDIUM	输入版本名与功率不一致；按官方230 G短轴封闭式、1987年10月后外廓。	READY
125923_lwb_pre87	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-W460-SUV-LWB-PRE87-01	MEDIUM	输入版本名与功率不一致；按官方230 G长轴封闭式、1987年10月前外廓。	READY
125923_lwb_post87	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-W460-SUV-LWB-POST87-01	MEDIUM	输入版本名与功率不一致；按官方230 G长轴封闭式、1987年10月后外廓。	READY
125925	125925	Convertible	G-Class W463	463.303	3	EU-MERCEDES-BENZ-G-W463-CONVERTIBLE-SWB-01	HIGH	短轴Cabriolet外廓。	READY
125926_swb	125926	SUV	G-Class W463	463.340	3	EU-MERCEDES-BENZ-G-W463-SUV-SWB-01	HIGH	短轴封闭式外廓。	READY
125926_lwb	125926	SUV	G-Class W463	463.341	5	EU-MERCEDES-BENZ-G-W463-SUV-LWB-01	HIGH	长轴封闭式外廓。	READY
125927	125927	Wagon	33 Tipo 907 Series 2	907B1H	5	EU-ALFA-ROMEO-33-907-SPORTWAGON-4X4-01	HIGH	907B1H五门四驱Sportwagon外廓。	READY
125932	125932	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	HIGH		READY
125933	125933	Coupe	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	HIGH		READY
125934	125934	Convertible	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	HIGH		READY
125935	125935	Convertible	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	HIGH		READY
125936	125936	Targa	911 (991.2)	991.2	2	EU-PORSCHE-911-991-2-TARGA-4-GTS-01	HIGH	独立Targa车顶外廓。	READY
125937	125937	Coupe	S-Class W126 facelift	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	HIGH		READY
125938	125938	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	HIGH		READY
125940	125940	SUV	GL-Class II	X166	5	EU-MERCEDES-BENZ-GL-X166-SUV-AMG-PREFL-01	HIGH		READY
125941	125941	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH		READY
125942_mwb	125942	Van	T1/TN	W611.367		EU-MERCEDES-BENZ-T1-W611-VAN-MWB-HIGHROOF-01	MEDIUM	Ktype覆盖3350和3700 mm轴距；3350 mm高顶厢式分支。	READY
125942_lwb	125942	Van	T1/TN	W611.368		EU-MERCEDES-BENZ-T1-W611-VAN-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖3350和3700 mm轴距；3700 mm高顶厢式分支。	READY
125943	125943	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
125944	125944	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
125949	125949	Wagon	Astra J		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-01	HIGH		READY
125956	125956	Sedan	Diplomat B		4	EU-OPEL-DIPLOMAT-B-SEDAN-01	HIGH		READY
125980_prefl	125980	Hatchback	Bluebird T12	T12	5	EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越1988年改款；改款前分支。	READY
125980_facelift	125980	Hatchback	Bluebird T72	T72	5	EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越1988年改款；改款后分支。	READY
125992	125992	SUV	Kadjar I		5	EU-RENAULT-KADJAR-I-SUV-PREFL-01	HIGH		READY
125995	125995	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
125996	125996	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
125997	125997	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
125998	125998	Wagon	Golf VII facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
126000	126000	Hatchback	Octavia III facelift	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	五门liftback外廓。	READY
126001	126001	Wagon	Octavia III facelift	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
126002	126002	Hatchback	Octavia III facelift	5E3	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	五门liftback外廓。	READY
126003	126003	Wagon	Octavia III facelift	5E5	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH		READY
126004_swb	126004	Pickup	Daily VI 4x4		2	EU-IVECO-DAILY-VI-4X4-CHASSIS-SWB-01	MEDIUM	同一Ktype覆盖多轴距底盘驾驶室；短轴分支。	READY
126004_mwb	126004	Pickup	Daily VI 4x4		2	EU-IVECO-DAILY-VI-4X4-CHASSIS-MWB-01	MEDIUM	同一Ktype覆盖多轴距底盘驾驶室；中轴分支。	READY
126004_lwb	126004	Pickup	Daily VI 4x4		2	EU-IVECO-DAILY-VI-4X4-CHASSIS-LWB-01	MEDIUM	同一Ktype覆盖多轴距底盘驾驶室；长轴分支。	READY
126006	126006	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-RWD-01	HIGH		READY
126007	126007	Hatchback	Golf VII facelift		5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
126008_prefl	126008	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-4MATIC-01	HIGH	Ktype生产区间跨越W213改款；改款前分支。	READY
126008_facelift	126008	Sedan	E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-4MATIC-01	HIGH	Ktype生产区间跨越W213改款；改款后分支。	READY
126010_prefl	126010	Convertible	3 Series E46 pre-facelift	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间跨越Cabriolet改款；改款前分支。	READY
126010_facelift	126010	Convertible	3 Series E46 facelift	E46/2C	2	EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间跨越Cabriolet改款；改款后分支。	READY
126011	126011	Coupe	Gamma Coupe Series 2	830	2	EU-LANCIA-GAMMA-830-COUPE-SERIES-2-01	HIGH	第二系列双门Coupe外廓。	READY
126013	126013	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126014_90	126014	SUV	Defender I	L316	3	EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-90-01	HIGH	Ktype覆盖90与110 Station Wagon；90短轴分支。	READY
126014_110	126014	SUV	Defender I	L316	5	EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-110-01	HIGH	Ktype覆盖90与110 Station Wagon；110长轴分支。	READY
126015_110	126015	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-ONE-TEN-STATION-WAGON-110-01	HIGH	LDH覆盖110与127；110 Station Wagon分支。	READY
126015_127	126015	Pickup	Land Rover One Two Seven	LDH	4	EU-LAND-ROVER-ONE-TWO-SEVEN-DOUBLE-CAB-127-01	MEDIUM	LDH覆盖110与127；127 Double Cab Pickup分支。	READY
126020	126020	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126021	126021	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126022	126022	SUV	F-Pace I pre-facelift	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
126023	126023	Hatchback	Stromos		5	EU-GERMAN-E-CARS-STROMOS-HATCHBACK-5D-01	HIGH	五门Stromos电动车身。	READY
126024	126024	Hatchback	Cetos		5	EU-GERMAN-E-CARS-CETOS-HATCHBACK-5D-01	MEDIUM	基于五门Opel Corsa D车身。	READY
126025	126025	Van	Plantos (Sprinter W906)	W906		EU-GERMAN-E-CARS-PLANTOS-W906-VAN-LWB-SUPERHIGH-01	MEDIUM	5.0 t长轴超高顶厢式配置。	READY
126026	126026	Pickup	Plantos (Sprinter W906)	W906	2	EU-GERMAN-E-CARS-PLANTOS-W906-CHASSIS-LWB-01	MEDIUM	5.0 t长轴底盘驾驶室/平台分支。	READY
126051	126051	Pickup	D-Max II facelift		2	EU-ISUZU-D-MAX-II-PICKUP-4X2-SINGLECAB-01	HIGH	4×2 Single Cab外廓。	READY
126055_singlecab	126055	Pickup	D-Max II facelift		2	EU-ISUZU-D-MAX-II-PICKUP-4X4-SINGLECAB-01	HIGH	4×4 Single Cab外廓。	READY
126055_extendedcab_utility	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-UTILITY-01	HIGH	4×4 Extended Cab Utility车高分支。	READY
126055_extendedcab_hightrim	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-HIGHTRIM-01	HIGH	4×4 Extended Cab高配置车高分支。	READY
126055_doublecab_utility	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-UTILITY-01	HIGH	4×4 Double Cab Utility/Eiger车高分支。	READY
126055_doublecab_hightrim	126055	Pickup	D-Max II facelift		4	EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-HIGHTRIM-01	HIGH	4×4 Double Cab Yukon/Utah/Blade车高分支。	READY
126060	126060	MPV	Partner II facelift	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-01	MEDIUM	Dangel四驱Tepee外廓。	READY
126064	126064	Wagon	5 Series E60/E61	E61	5	EU-BMW-5-E61-WAGON-01	HIGH		READY
126065	126065	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH		READY
126072	126072	Convertible	Z4 I facelift	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH	E85改款后Roadster外廓。	READY
126075_prefl	126075	Wagon	3 Series E46 pre-facelift	E46/3	5	EU-BMW-3-E46-WAGON-PREFL-01	HIGH	Ktype生产区间跨越Touring改款；改款前分支。	READY
126075_facelift	126075	Wagon	3 Series E46 facelift	E46/3	5	EU-BMW-3-E46-WAGON-FACELIFT-01	HIGH	Ktype生产区间跨越Touring改款；改款后分支。	READY
126076_prefl	126076	Sedan	3 Series E46 pre-facelift	E46/4	4	EU-BMW-3-E46-SEDAN-PREFL-01	HIGH	Ktype生产区间跨越Sedan改款；改款前分支。	READY
126076_facelift	126076	Sedan	3 Series E46 facelift	E46/4	4	EU-BMW-3-E46-SEDAN-FACELIFT-01	HIGH	Ktype生产区间跨越Sedan改款；改款后分支。	READY
126077	126077	Wagon	5 Series E39 facelift	E39	5	EU-BMW-5-E39-WAGON-FACELIFT-01	HIGH		READY
126078	126078	Sedan	5 Series E39 facelift	E39	4	EU-BMW-5-E39-SEDAN-FACELIFT-01	HIGH		READY
126079	126079	Hatchback	A3 8V facelift	8V1	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门外廓。	READY
126080	126080	Wagon	5 Series E39 pre-facelift	E39	5	EU-BMW-5-E39-WAGON-PREFL-01	HIGH		READY
126081	126081	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	五门Sportback外廓。	READY
126082	126082	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
126106	126106	MPV	Libero E10		4	EU-SUBARU-LIBERO-E10-MICROVAN-01	MEDIUM	E10客运车身。	READY
126107	126107	Coupe	3 Series E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH		READY
126109	126109	Coupe	Leone III		3	EU-SUBARU-LEONE-III-COUPE-4WD-01	HIGH	三门Coupe外廓。	READY
126118	126118	Coupe	3 Series E46	E46	2	EU-BMW-3-E46-COUPE-PREFL-01	HIGH		READY
126122	126122	Sedan	3 Series E46 pre-facelift	E46/4	4	EU-BMW-3-E46-SEDAN-PREFL-01	HIGH		READY
126128	126128	Van	Libero E10		4	EU-SUBARU-LIBERO-E10-MICROVAN-01	MEDIUM	E10货运车身。	READY
126132	126132	Coupe	6 Series E24 facelift	E24	2	EU-BMW-6-E24-COUPE-FACELIFT-01	HIGH	1987年后期E24外廓。	READY
126135	126135	Convertible	507	507	2	EU-BMW-507-CONVERTIBLE-01	HIGH		READY
126137	126137	Convertible	507	507	2	EU-BMW-507-CONVERTIBLE-01	HIGH		READY
126142	126142	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126143	126143	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126144	126144	Sedan	502	502	4	EU-BMW-502-SEDAN-01	HIGH		READY
126152	126152	Sedan	340	340	4	EU-BMW-340-SEDAN-01	HIGH		READY
126159	126159	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126160	126160	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126161	126161	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126162	126162	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH		READY
126163	126163	Hatchback	A5 II (F5)	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	五门Sportback外廓。	READY
126164	126164	SUV	C-HR I	ZYX10	5	EU-TOYOTA-C-HR-I-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1101-1200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311	Meyer Motoren Jaguar F-Type Coupe X152 vehicle data	https://www.meyermotoren.de/en/fahrzeuge/125817/jaguar/f-type_coupe_x152_/3_0_sc_v6_400_sport_awd_125817
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	4482	1923	1308	CarExpert 2018 Jaguar F-Type 400 Sport Convertible; Automobile-Catalog 2017 Jaguar F-Type 400 Sport Convertible AWD	https://www.carexpert.com.au/jaguar/f-type/2018-400-sport-3l-convertible-rwd-petrol-automatic-josfwkgw20170721;https://www.automobile-catalog.com/car/2017/2559365/jaguar_f-type_400_sport_convertible_awd.html
EU-FORD-TAUNUS-TC2-SEDAN-2D-01	4340	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 L	https://www.automobile-catalog.com/car/1976/920945/ford_taunus_1_3_l.html
EU-FORD-TAUNUS-TC2-SEDAN-4D-01	4340	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 L	https://www.automobile-catalog.com/car/1976/920945/ford_taunus_1_3_l.html
EU-FORD-TAUNUS-TC2-WAGON-5D-01	4440	1700	1366	Automobile-Catalog 1976 Ford Taunus Turnier 1.3 L	https://www.automobile-catalog.com/car/1976/921230/ford_taunus_turnier_1_3_l_low_compr_.html
EU-FORD-TAUNUS-TC1-COUPE-01	4267	1708	1341	Automobile-Catalog 1972 Ford Taunus 1300 L Coupe	https://www.automobile-catalog.com/car/1972/911990/ford_taunus_1300_l_coupe.html
EU-FORD-TAUNUS-TC3-SEDAN-2D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.3	https://www.automobile-catalog.com/car/1980/921815/ford_taunus_1_3.html
EU-FORD-TAUNUS-TC3-SEDAN-4D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.3	https://www.automobile-catalog.com/car/1980/921815/ford_taunus_1_3.html
EU-KIA-RIO-IV-YB-HATCHBACK-5D-PREFL-01	4065	1725	1450	Kia Rio 2017 Technical Specification	https://press.kia.com/content/dam/kiapress/EU/download-files/New-Rio/Kia-Rio-Technical-Specification-3-Feb-2017.doc
EU-NISSAN-SYLPHY-B17-SEDAN-01	4625	1760	1495	Nissan Sylphy Specifications	https://i.i-sgcm.com/new_cars/cars/11294/brochures/brochure_20160927100751.pdf
EU-FORD-FOCUS-III-PREFL-VAN-5D-01	4358	1823	1484	Ford Focus UK brochure; Automobile-Catalog 2011 Ford Focus 1.6 Ti-VCT	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-Focus-2010-UK.pdf;https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484	Ford Focus official specification archive	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/Focus_TechnicalSpecifications_EU.pdf
EU-ASTON-MARTIN-LAGONDA-SERIES-3-SHOOTING-BRAKE-01	5283	1816	1302	Aston Martin Lagonda official specifications; Automobile-Catalog 1987 Aston Martin Lagonda; Aston Martins Lagonda V8 Shooting Brake by Roos	https://www.astonmartin.com/en/models/past-models/lagonda;https://www.automobile-catalog.com/car/1987/227540/aston_martin_lagonda_automatic.html;https://astonmartins.com/car/lagonda-v8-shooting-brake-by-roos/
EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	4540	1915	1250	Automobile-Catalog 2016 Aston Martin Vantage GT8	https://www.automobile-catalog.com/car/2016/2515100/aston_martin_v8_vantage_gt8.html
EU-MAZDA-626-I-CB2-COUPE-01	4420	1690	1370	Automobile-Catalog Mazda 626 Coupe 1600	https://www.automobile-catalog.com/car/1979/1585115/mazda_626_coupe_1600.html
EU-MAZDA-818-I-COUPE-PREFL-01	3970	1595	1350	Automobile-Catalog 1973 Mazda Grand Familia 1300 GF Coupe	https://www.automobile-catalog.com/car/1973/1583375/mazda_grand_familia_gf_coupe.html
EU-MAZDA-818-I-COUPE-FACELIFT-01	4075	1595	1350	Automobile-Catalog 1975 Mazda 818 Coupe 1300	https://www.automobile-catalog.com/car/1975/1584395/mazda_818_coupe_1300.html
EU-LEXUS-RX-IV-AL20-SUV-PREFL-01	4890	1895	1685	Lexus RX Technical Specifications	https://media.lexus.co.uk/wp-content/uploads/sites/3/pdf/220112M-RX-Tech-Spec.pdf
EU-MERCEDES-BENZ-G-W460-SUV-SWB-PRE87-01	3945	1700	1960	Mercedes-Benz Public Archive 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-W460-SUV-SWB-POST87-01	3955	1700	1925	Mercedes-Benz Public Archive 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-W460-SUV-LWB-PRE87-01	4395	1700	1950	Mercedes-Benz Public Archive 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-W460-SUV-LWB-POST87-01	4405	1700	1920	Mercedes-Benz Public Archive 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-W463-CONVERTIBLE-SWB-01	4257	1760	1941	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-W463-SUV-SWB-01	4212	1760	1931	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-W463-SUV-LWB-01	4662	1760	1931	Mercedes-Benz Public Archive G 320 CDI/G 350 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039060
EU-ALFA-ROMEO-33-907-SPORTWAGON-4X4-01	4200	1614	1375	Motor Sport Alfa Romeo 33 Sport Wagon 16V 4x4; Automobile-Catalog 1991 Alfa Romeo 33 Sport Wagon 4x4	https://www.motorsportmagazine.com/archive/article/may-1991/34/new-cars-alfa-romeo-33-s-16v-cloverleaf-and-sport-wagon-16v/;https://www.automobile-catalog.com/car/1991/217055/alfa_romeo_33_1_7_ie_sport_wagon_4x4.html
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291	Porsche 2017 Models Technical Data	https://newsroom.porsche.com/dam/jcr%3A48c46ea8-77ba-42f0-9891-ddff55e82cb4/PCNA18_1000_us.pdf
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	4935	1828	1407	Automobile-Catalog 1990 Mercedes-Benz 420 SEC	https://www.automobile-catalog.com/car/1990/1476020/mercedes-benz_420_sec_cat.html
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300	Automobile-Catalog 1971 Mercedes-Benz 350 SL	https://www.automobile-catalog.com/car/1971/1469240/mercedes-benz_350_sl.html
EU-MERCEDES-BENZ-GL-X166-SUV-AMG-PREFL-01	5120	1934	1850	EncyCARpedia Mercedes GL 63 AMG	https://www.encycarpedia.com/mercedes/12-gl-63-amg-suv
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	4084	1730	1562	Automobile-Catalog 2017 Renault Zoe R90	https://www.automobile-catalog.com/car/2017/2984375/renault_zoe_r90.html
EU-MERCEDES-BENZ-T1-W611-VAN-MWB-HIGHROOF-01	5615	1900	2550	Mercedes-Benz T1 body-code catalogue; Force Traveller T1-derived delivery-van technical data	https://www.partssouq.com/en/catalog/genuine/vehicle?c=Mercedes-Benz&ssd=%24%2AKwHj1eTQgo6CgoP5n4fUu7uvo6WZ6OHi4cP97P7j6u3q8vD0-vr7-Pv34ebi6Obn-Pf85-Xg4evi4f_-4uHk5eTl4uPjAAAAAM6pEF0%24;https://poomkudy.com/userdata/motorsforce/20210218_013400_542622.pdf
EU-MERCEDES-BENZ-T1-W611-VAN-LWB-HIGHROOF-01	6265	1900	2550	Mercedes-Benz T1 body-code catalogue; Force Traveller T1-derived delivery-van technical data	https://www.partssouq.com/en/catalog/genuine/vehicle?c=Mercedes-Benz&ssd=%24%2AKwHj1eTQgo6CgoP5n4fUu7uvo6WZ6OHi4cP97P7j6u3q8vD0-vr7-Pv34ebi6Obn-Pf85-Xg4evi4f_-4uHk5eTl4uPjAAAAAM6pEF0%24;https://poomkudy.com/userdata/motorsforce/20210218_013400_542622.pdf
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Volkswagen Golf 2017 technical specifications	https://www.volkswagen-newsroom.com/en/the-new-golf-2016-2543/download
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515	Volkswagen Golf Variant 2017 technical specifications	https://www.volkswagen-newsroom.com/en/the-new-golf-variant-2016-2544/download
EU-OPEL-ASTRA-J-SPORTS-TOURER-01	4698	1814	1535	Vauxhall Astra Sports Tourer official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/brochure-library/cars/astra/Astra_ST_Spec_PG_18_October_2013.pdf
EU-OPEL-DIPLOMAT-B-SEDAN-01	4920	1852	1450	Automobile-Catalog 1976 Opel Diplomat 2.8 160 PS	https://www.automobile-catalog.com/car/1976/2417555/opel_diplomat_e.html
EU-NISSAN-BLUEBIRD-T12-HATCHBACK-5D-PREFL-01	4365	1690	1395	Automobile-Catalog 1987 Nissan Bluebird 1.8 GS 5-door	https://www.automobile-catalog.com/car/1987/2236235/nissan_bluebird_1_8_gs_5-d_automatic.html
EU-NISSAN-BLUEBIRD-T72-HATCHBACK-5D-FACELIFT-01	4420	1690	1395	Automobile-Catalog 1990 Nissan Bluebird 1.6 LS 5-door	https://www.automobile-catalog.com/car/1990/2236610/nissan_bluebird_1_6_ls_5-d.html
EU-RENAULT-KADJAR-I-SUV-PREFL-01	4449	1836	1613	Renault Kadjar 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Kadjar-2017-UK.pdf
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Škoda Octavia facelift technical specifications	https://cdn.skoda-storyboard.com/2017/01/TD-OCTAVIA-en.pdf
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Škoda Octavia Combi facelift technical specifications	https://cdn.skoda-storyboard.com/2017/01/TD-OCTAVIA-COMBI-en.pdf
EU-IVECO-DAILY-VI-4X4-CHASSIS-SWB-01	5348	2056	2508	IVECO Daily 4x4 official specification sheet	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/Daily-4x4-Spec-Sheet---Web-Version.pdf?rev=5b2abb4c8789416ebb241827eb8b9332
EU-IVECO-DAILY-VI-4X4-CHASSIS-MWB-01	5853	2056	2506	IVECO Daily 4x4 official specification sheet	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/Daily-4x4-Spec-Sheet---Web-Version.pdf?rev=5b2abb4c8789416ebb241827eb8b9332
EU-IVECO-DAILY-VI-4X4-CHASSIS-LWB-01	6818	2056	2501	IVECO Daily 4x4 official specification sheet	https://www.iveco.com/nz/-/media/IVECOdotcom/NewZealand/Products/Daily/Files/Daily-4x4-Spec-Sheet---Web-Version.pdf?rev=5b2abb4c8789416ebb241827eb8b9332
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-RWD-01	4923	1852	1468	Automobile-Catalog 2018 Mercedes-Benz E 220 d	https://www.automobile-catalog.com/car/2018/2297795/mercedes-benz_e_220_d.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-4MATIC-01	4923	1852	1468	Automobile-Catalog 2018 Mercedes-Benz E 220 d 4Matic	https://www.automobile-catalog.com/car/2018/2504390/mercedes-benz_e_220_d_4matic.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-4MATIC-01	4935	1852	1467	Automobile-Catalog 2021 Mercedes-Benz E 220 d 4Matic	https://www.automobile-catalog.com/car/2021/2968295/mercedes-benz_e_220_d_4matic.html
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372	Automobile-Catalog BMW 318Ci Cabrio pre-facelift	https://www.automobile-catalog.com/car/2001/276455/bmw_318ci_cabrio.html
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372	Automobile-Catalog 2004 BMW 318Ci Cabrio	https://www.automobile-catalog.com/car/2004/276500/bmw_318ci_cabrio.html
EU-LANCIA-GAMMA-830-COUPE-SERIES-2-01	4485	1730	1330	Automobile-Catalog 1981 Lancia Gamma Coupe 2000 Series 2	https://www.automobile-catalog.com/car/1981/1378490/lancia_gamma_coupe_2000_2a_serie.html
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Alfa Romeo Stelvio technical specifications	https://www.media.stellantis.com/uploads/em/attachment/technical_data_alfa_romeo_stelvio-5d2368aa0eec6.pdf
EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-90-01	3883	1790	1963	Automobile-Catalog 1991 Land-Rover Defender 90 Station Wagon V8	https://www.automobile-catalog.com/car/1991/1395005/land-rover_defender_90_station_wagon_v8.html
EU-LAND-ROVER-DEFENDER-I-STATION-WAGON-110-01	4599	1790	2035	Automobile-Catalog 1991 Land-Rover Defender 110 Station Wagon V8	https://www.automobile-catalog.com/car/1991/1395245/land-rover_defender_110_station_wagon_v8.html
EU-LAND-ROVER-ONE-TEN-STATION-WAGON-110-01	4580	1790	1996	Automobile-Catalog 1986 Land-Rover 110 County V8	https://www.automobile-catalog.com/car/1986/1394405/land-rover_110_county_v8.html
EU-LAND-ROVER-ONE-TWO-SEVEN-DOUBLE-CAB-127-01	5132	1790	2035	Automobile-Catalog 1990 Land-Rover Defender 130 Double Cab V8	https://www.automobile-catalog.com/car/1990/1395050/land-rover_defender_130_double_cab_v8.html
EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	4731	1936	1652	Jaguar All-New F-Pace official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-FPAC17-PRT0520_F_PACE_17MY_MB_GEE%20UPDATE_V3.pdf
EU-GERMAN-E-CARS-STROMOS-HATCHBACK-5D-01	3715	1680	1590	German E Cars Stromos brochure	https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf
EU-GERMAN-E-CARS-CETOS-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure; eMobilität Online German E-Cars Cetos	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf;https://emobilitaet.online/e-katalog/1241-das-elektromobil-des-monats-august-der-cetos-von-german-e-cars
EU-GERMAN-E-CARS-PLANTOS-W906-VAN-LWB-SUPERHIGH-01	6945	1993	3045	German E-Cars Plantos vehicle-basis study; Mercedes-Benz Sprinter 2011 technical data	https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/;https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf
EU-GERMAN-E-CARS-PLANTOS-W906-CHASSIS-LWB-01	6845	1990	2385	German E-Cars Plantos vehicle-basis study; CarExpert 2011 Mercedes-Benz Sprinter chassis cab	https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/;https://www.carexpert.co.nz/mercedes-benz/sprinter/2011-3l-chassis-cab-rwd-diesel-automatic-jogkwfwo20110401
EU-ISUZU-D-MAX-II-PICKUP-4X2-SINGLECAB-01	5315	1775	1685	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-SINGLECAB-01	5315	1860	1780	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-UTILITY-01	5295	1860	1780	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-EXTENDEDCAB-HIGHTRIM-01	5295	1860	1790	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-UTILITY-01	5295	1860	1785	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-ISUZU-D-MAX-II-PICKUP-4X4-DOUBLECAB-HIGHTRIM-01	5295	1860	1795	Isuzu D-Max 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/04/Isuzu-D-Max-2017-UK.pdf
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-01	4380	1810	1801	UltimateSpecs Peugeot Partner II Tepee Dangel 4x4	https://www.ultimatespecs.com/car-specs/Peugeot/65340/Peugeot-Partner-2-Tepee-4x4-Dangel-Extreme-HDi-92.html
EU-BMW-5-E61-WAGON-01	4843	1846	1491	Automobile-Catalog BMW 525i Touring E61	https://www.automobile-catalog.com/car/2005/273890/bmw_525i_touring.html
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430	Automobile-Catalog 1977 Peugeot 604 SL V6	https://www.automobile-catalog.com/car/1977/2567315/peugeot_604_sl_v6.html
EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	4091	1781	1299	Automobile-Catalog 2006 BMW Z4 Roadster 2.5si	https://www.automobile-catalog.com/car/2006/281015/bmw_z4_roadster_2_5si.html
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409	Automobile-Catalog 1999 BMW 320i Touring	https://www.automobile-catalog.com/car/1999/274760/bmw_320i_touring.html
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409	Automobile-Catalog 2004 BMW 318i Touring	https://www.automobile-catalog.com/car/2004/275450/bmw_318i_touring.html
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415	Automobile-Catalog 1999 BMW 320i	https://www.automobile-catalog.com/car/1999/274415/bmw_320i.html
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415	Automobile-Catalog BMW 3 Series E46 Sedan facelift	https://www.automobile-catalog.com/car/2002/274505/bmw_320i.html
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445	Automobile-Catalog 2001 BMW 520i Touring	https://www.automobile-catalog.com/car/2001/273785/bmw_520i_touring.html
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435	Automobile-Catalog 2001 BMW 520i	https://www.automobile-catalog.com/car/2001/273530/bmw_520i.html
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424	Audi A3 8V facelift technical data	https://www.audi-mediacenter.com/en/audi-a3-18
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445	Automobile-Catalog 1999 BMW 523i Touring	https://www.automobile-catalog.com/car/1999/273275/bmw_523i_touring.html
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426	Audi A3 Sportback 8V facelift technical data	https://www.audi-mediacenter.com/en/audi-a3-sportback-19
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416	Audi A3 Sedan 8V facelift technical data	https://www.audi-mediacenter.com/en/audi-a3-sedan-20
EU-SUBARU-LIBERO-E10-MICROVAN-01	3410	1430	1870	Automobile-Catalog 1984 Subaru E10 Wagon 2WD; Automobile-Catalog 1984 Subaru E10 Van 2WD; Automobile-Catalog 1985 Subaru E10 Wagon 4WD	https://www.automobile-catalog.com/car/1984/3224420/subaru_e10_wagon_2wd.html;https://www.automobile-catalog.com/car/1984/3224435/subaru_e10_van_2wd.html;https://www.automobile-catalog.com/car/1985/48365/subaru_e-10.html
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370	Automobile-Catalog BMW 318Ci Coupe E46 pre-facelift	https://www.automobile-catalog.com/car/2000/276050/bmw_318ci.html
EU-SUBARU-LEONE-III-COUPE-4WD-01	4370	1660	1405	Automobile-Catalog 1986 Subaru Leone 4WD 3-door Coupe RX II Turbo	https://www.automobile-catalog.com/car/1986/3213125/subaru_leone_4wd_3door_coupe_1_8_rxii_turbo.html
EU-BMW-6-E24-COUPE-FACELIFT-01	4815	1725	1365	Automobile-Catalog 1988 BMW 635 CSi	https://www.automobile-catalog.com/car/1988/264185/bmw_635_csi.html
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275	Automobile-Catalog 1956 BMW 507	https://www.automobile-catalog.com/car/1956/262385/bmw_507_3_70_axle_standard.html
EU-BMW-502-SEDAN-01	4730	1780	1530	Automobile-Catalog 1958 BMW 502 2.6L; Automobile-Catalog 1958 BMW 502 3.2L Super	https://www.automobile-catalog.com/car/1958/262055/bmw_502_2_6l.html;https://www.automobile-catalog.com/car/1958/262115/bmw_502_3_2l_super.html
EU-BMW-340-SEDAN-01	4600	1765	1630	Automobile-Catalog 1950 BMW 340	https://www.automobile-catalog.com/car/1950/2065490/bmw_340.html
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	Audi A5 Cabriolet F5 technical data	https://www.audi-mediacenter.com/en/audi-a5-cabriolet-52
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi A5 Sportback F5 technical data	https://www.audi-mediacenter.com/en/audi-a5-sportback-50
EU-TOYOTA-C-HR-I-SUV-01	4360	1795	1565	Toyota C-HR technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/161214M-C-HR-Tech-Spec.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1101-1200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://poomkudy.com/userdata/motorsforce/20210218_013400_542622.pdf "https://poomkudy.com/userdata/motorsforce/20210218_013400_542622.pdf"
[2]: https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/ "https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1101-1200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1101-1200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1172 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（616 行）

