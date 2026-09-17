# 任务：left18448 第 3701-3800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0038__c3d069d2


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3701-3800 行

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
left18448.tsv

【当前独立任务】
left18448 第 3701-3800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3701-3800_ktype_dimension_mapping_final.tsv
- left18448_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-C5-AIRCROSS-II-SUV-5D-ELECTRIC-01	4652	1902	1691
EU-CITROEN-C5-AIRCROSS-II-SUV-5D-HYBRID-01	4652	1902	1688
EU-CITROEN-C5-AIRCROSS-II-SUV-5D-PHEV-01	4652	1902	1690
EU-CITROEN-C5-AIRCROSS-I-SUV-5D-PHASE-II-01	4500	1840	1689
EU-CITROEN-C5-I-DC-HATCHBACK-5D-PHASE-I-01	4618	1770	1476
EU-CITROEN-C5-I-DE-WAGON-5D-PHASE-I-01	4756	1770	1516
EU-CITROEN-C5-II-X7-RD-SEDAN-4D-01	4779	1860	1458
EU-CITROEN-C5-II-X7-TD-WAGON-5D-01	4829	1860	1495
EU-CITROEN-C5-I-RC-HATCHBACK-5D-PHASE-II-01	4745	1780	1475
EU-CITROEN-C5-I-RE-WAGON-5D-PHASE-II-01	4839	1780	1555
EU-CITROEN-C5-X-I-ND-WAGON-5D-01	4805	1865	1485

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Citroën	C5	Puretech 180	Kombi	Frontantrieb	Benzin	Sep 2021	-	145503
Citroën	C6	2.2 HDI	Stufenheck	Frontantrieb	Diesel	Jun 2006	Dec 2010	58669
Citroën	C6	2.7 HDI	Stufenheck	Frontantrieb	Diesel	Sep 2005	Dec 2011	18772
Citroën	C6	3.0 V6	Stufenheck	Frontantrieb	Benzin	Sep 2005	Dec 2012	18771
Citroën	C8	2	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	-	16726
Citroën	C8	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2003	Nov 2004	142684
Citroën	C8	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 2004	Dec 2011	142685
Citroën	C8	2.2	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	-	16727
Citroën	C8	2.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2003	Aug 2007	142686
Citroën	C8	3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2003	Oct 2007	142687
Citroën	C8	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	-	19011
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	-	16729
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	-	101093
Citroën	C8	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	Jul 2002	-	16730
Citroën	C8	2.2 HDI	Großraumlimousine	Frontantrieb	Diesel	Jun 2007	-	58668
Citroën	C8	3.0 V6	Großraumlimousine	Frontantrieb	Benzin	Jul 2002	-	16728
Citroën	C8	HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2003	Jul 2006	142691
Citroën	C8	HDI 110	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2003	Dec 2009	142690
Citroën	C-Crosser	2.2 HDI	Kasten/SUV	Allrad	Diesel	Jun 2007	Dec 2012	142692
Citroën	C-Crosser	2.4 16V	Kasten/SUV	Allrad	Benzin	Jan 2009	-	11207
Citroën	C-Elysee	1.2 VTI 72	Stufenheck	Frontantrieb	Benzin	Nov 2012	Jan 2017	57402
Citroën	C-Elysee	1.2 VTI 82	Stufenheck	Frontantrieb	Benzin	Dec 2014	-	117342
Citroën	C-Elysee	1.6 Bluehdi 100	Stufenheck	Frontantrieb	Diesel	Nov 2014	Dec 2016	117340
Citroën	C-Elysee	1.6 HDI 92	Stufenheck	Frontantrieb	Diesel	Nov 2012	-	57403
Citroën	C-Elysee	1.6 VTI 115	Stufenheck	Frontantrieb	Benzin	Nov 2012	-	57404
Citroën	Cx i	2200	Stufenheck	Frontantrieb	Benzin	Jun 1981	Aug 1985	17461
Citroën	Cx i	2400	Stufenheck	Frontantrieb	Benzin	May 1980	May 1982	6577
Citroën	Cx i	25 D Turbo	Stufenheck	Frontantrieb	Diesel	Apr 1983	Aug 1985	17430
Citroën	Cx i	25 GTI Turbo 2	Stufenheck	Frontantrieb	Benzin	Jun 1984	Aug 1985	17432
Citroën	Cx i	25 TRI	Stufenheck	Frontantrieb	Benzin	Jul 1983	Aug 1985	17431
Citroën	Cx i break	2200	Kombi	Frontantrieb	Benzin	Jun 1981	Aug 1985	17462
Citroën	Cx i break	2400	Kombi	Frontantrieb	Benzin	May 1980	May 1982	6585
Citroën	Cx i break	2200 D	Kombi	Frontantrieb	Diesel	Aug 1976	Feb 1979	6584
Citroën	Cx i break	25 TRI	Kombi	Frontantrieb	Benzin	Jul 1983	Aug 1985	17433
Citroën	Cx ii	22 TRS	Stufenheck	Frontantrieb	Benzin	Jul 1985	Jul 1989	17464
Citroën	Cx ii break	22 TRS	Kombi	Frontantrieb	Benzin	Jul 1985	Dec 1992	15073
Citroën	Cx ii break	22trs	Kombi	Frontantrieb	Benzin	Jul 1985	Jul 1989	17465
Citroën	Cx ii break	2500 D Turbo	Kombi	Frontantrieb	Diesel	Aug 1985	Dec 1986	17429
Citroën	C-Zero	C-zero	Schrägheck	Heckantrieb	Elektro	Jan 2011	-	112395
Citroën	Ds	19	Cabriolet	Frontantrieb	Benzin	Aug 1956	Dec 1965	15076
Citroën	Ds	20	Kombi	Frontantrieb	Benzin	Sep 1972	Jul 1975	15133
Citroën	Ds	21	Cabriolet	Frontantrieb	Benzin	Apr 1968	Mar 1969	15074
Citroën	Ds	21	Cabriolet	Frontantrieb	Benzin	Apr 1969	Dec 1971	15075
Citroën	Ds	21	Kombi	Frontantrieb	Benzin	Sep 1972	Jul 1975	15134
Citroën	Ds3	1.2 THP 110	Cabriolet	Frontantrieb	Benzin	Oct 2014	Jul 2015	108598
Citroën	Ds3	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	Oct 2014	Mar 2015	108600
Citroën	Ds3	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	Jan 2013	Mar 2015	58578
Citroën	Ds3	1.2 VTI 82	Cabriolet	Frontantrieb	Benzin	Jan 2013	Jul 2015	58583
Citroën	Ds3	1.4 HDI 70	Schrägheck	Frontantrieb	Diesel	Apr 2010	Jul 2015	12291
Citroën	Ds3	1.4 VTI 95 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Aug 2012	Jul 2015	58579
Citroën	Ds3	1.4 VTI 98	Schrägheck	Frontantrieb	Benzin	Nov 2009	Jul 2015	58570
Citroën	Ds3	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	107159
Citroën	Ds3	1.6 Bluehdi 100	Cabriolet	Frontantrieb	Diesel	Jul 2014	Jul 2015	108159
Citroën	Ds3	1.6 Bluehdi 115	Cabriolet	Frontantrieb	Diesel	Oct 2013	Jul 2015	117894
Citroën	Ds3	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Oct 2013	Jul 2015	100643
Citroën	Ds3	1.6 Bluehdi 120	Cabriolet	Frontantrieb	Diesel	Jul 2014	Jul 2015	107569
Citroën	Ds3	1.6 Bluehdi 75	Schrägheck	Frontantrieb	Diesel	Mar 2015	Jul 2015	117893
Citroën	Ds3	1.6 HDI 115	Schrägheck	Frontantrieb	Diesel	Aug 2012	Jul 2015	58582
Citroën	Ds3	1.6 HDI 115	Schrägheck	Frontantrieb	Diesel	Oct 2013	Jul 2015	100642
Citroën	Ds3	1.6 HDI 90	Cabriolet	Frontantrieb	Diesel	Jan 2013	Jul 2015	58586
Citroën	Ds3	1.6 Racing	Schrägheck	Frontantrieb	Benzin	Feb 2011	Jul 2015	5091
Citroën	Ds3	1.6 Racing	Cabriolet	Frontantrieb	Benzin	Mar 2014	Jul 2015	108686
Citroën	Ds3	1.6 THP 150	Schrägheck	Frontantrieb	Benzin	Jan 2010	Jul 2015	12290
Citroën	Ds3	1.6 THP 150	Cabriolet	Frontantrieb	Benzin	Jan 2013	Jul 2015	59305
Citroën	Ds3	1.6 THP 155	Cabriolet	Frontantrieb	Benzin	Jan 2013	Jul 2015	58585
Citroën	Ds3	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Oct 2014	Jun 2015	109261
Citroën	Ds3	1.6 THP 165	Cabriolet	Frontantrieb	Benzin	Oct 2014	Jul 2015	109321
Citroën	Ds3	1.6 VTI 120	Cabriolet	Frontantrieb	Benzin	Jan 2013	Jul 2015	58584
Citroën	Ds4	1.2 THP 130	Schrägheck	Frontantrieb	Benzin	Jul 2014	Jul 2015	109325
Citroën	Ds4	1.6 Bluehdi 115	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	117920
Citroën	Ds4	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	108856
Citroën	Ds4	1.6 HDI 115	Schrägheck	Frontantrieb	Diesel	Aug 2012	Jul 2015	58671
Citroën	Ds4	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	May 2011	Jul 2015	59311
Citroën	Ds4	1.6 THP 160	Schrägheck	Frontantrieb	Benzin	Apr 2012	Jul 2015	55402
Citroën	Ds4	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Jan 2012	Jul 2015	49684
Citroën	Ds4	2.0 Bluehdi 150	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	109324
Citroën	Ds4	2.0 Bluehdi 180	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	109323
Citroën	Ds4	2.0 HDI / Bluehdi 135	Schrägheck	Frontantrieb	Diesel	Sep 2011	Jul 2015	59310
Citroën	Ds5	1.6 Bluehdi 120	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	108149
Citroën	Ds5	1.6 HDI	Schrägheck	Frontantrieb	Diesel	Nov 2013	Jul 2015	100512
Citroën	Ds5	1.6 HDI 110	Schrägheck	Frontantrieb	Diesel	Nov 2011	Jul 2015	10885
Citroën	Ds5	1.6 HDI 115	Schrägheck	Frontantrieb	Diesel	Jun 2012	Jul 2015	59306
Citroën	Ds5	1.6 THP 150	Schrägheck	Frontantrieb	Benzin	Nov 2011	Jul 2015	59891
Citroën	Ds5	1.6 THP 155	Schrägheck	Frontantrieb	Benzin	Nov 2011	Jul 2015	10877
Citroën	Ds5	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	Jan 2012	Jul 2015	51869
Citroën	Ds5	1.6 THP 165 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2012	Jul 2015	108053
Citroën	Ds5	1.6 THP 200	Schrägheck	Frontantrieb	Benzin	Nov 2011	Jul 2015	10878
Citroën	Ds5	2.0 Bluehdi 150	Schrägheck	Frontantrieb	Diesel	Jul 2014	Jul 2015	108854
Citroën	Ds5	2.0 Bluehdi 180	Schrägheck	Frontantrieb	Diesel	Aug 2013	Jul 2015	50144
Citroën	Ds5	2.0 HDI 135	Schrägheck	Frontantrieb	Diesel	Nov 2011	Jul 2015	59308
Citroën	Ds5	2.0 HDI 165	Schrägheck	Frontantrieb	Diesel	Nov 2011	Jul 2015	10886
Citroën	Ds5	2.0 HDI 200 Hybrid4 Allrad	Schrägheck	Allrad	Diesel/Elektro	Dec 2011	Jul 2015	53387
Citroën	Dyane	4	Schrägheck	Frontantrieb	Benzin	Aug 1967	Mar 1968	6026
Citroën	Dyane	6	Schrägheck	Frontantrieb	Benzin	Dec 1968	Oct 1984	6025
Citroën	E-Mehari	Electric	Cabriolet	Frontantrieb	Elektro	Jun 2016	-	121049
Citroën	E-Mehari	Electric	Cabriolet	Frontantrieb	Elektro	Jun 2016	-	155895
Citroën	Evasion	1.9 TD	Großraumlimousine	Frontantrieb	Diesel	Oct 1995	Dec 1998	17428
Citroën	Evasion	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 1998	Apr 2000	11370
Citroën	Evasion	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 2000	Jul 2002	15085
Citroën	Evasion	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	Aug 1999	Jul 2002	13862


--- Round 1 / 首次发送 ---
## 更新点

* 已复用现有 `EU-CITROEN-C5-X-I-ND-WAGON-5D-01`，未重复创建 C5 X 尺寸组。
* 已闭合 C6、C8、C-Crosser、C-Elysée 的标准物理外廓；其中 C8 使用不含车顶行李架的标准高度，C-Elysée 使用官方规格中的不含后视镜宽度。([汽车目录][1])
* DS3 已区分 Hatchback、Cabriolet、Racing Hatchback 和 Racing Cabriolet；DS5 已区分标准车身与增高的 Hybrid4 外廓。([汽车档案馆][2])
* Dyane Ktype `6025` 的生产期跨越三种已确认外廓，已拆分为 `phase1`、`phase2`、`phase3` 三条派生映射。C-Zero、E-Méhari、Evasion 也已闭合。([汽车档案馆][3])
* CX 仍存在 Series I/II、改款阶段及车身形式之间的长度和宽度数据冲突，且部分来源未明确宽度口径，因此暂不创建尺寸组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：102
* READY 映射：89 行，覆盖 87 个 Ktype
* PENDING 映射：13 行，覆盖 13 个 Ktype
* 已确认尺寸组：20 个，其中复用既有组 1 个、本轮新建 19 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145503	145503	Wagon	C5 X I	ND	5	EU-CITROEN-C5-X-I-ND-WAGON-5D-01	HIGH	输入C5 Kombi对应2021年起C5 X ND五门外廓。	READY
58669	58669	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH	C6 TD四门外廓。	READY
18772	18772	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH	C6 TD四门外廓。	READY
18771	18771	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH	C6 TD四门外廓。	READY
16726	16726	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
142684	142684	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
142685	142685	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
16727	16727	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
142686	142686	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
142687	142687	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
19011	19011	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
16729	16729	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
101093	101093	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
16730	16730	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
58668	58668	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
16728	16728	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8五门MPV外廓。	READY
142691	142691	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
142690	142690	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	C8商用登记车身与乘用MPV共用外部壳体。	READY
142692	142692	SUV	C-Crosser I	EP	5	EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	HIGH	EP五门SUV外廓；Kasten/SUV为登记用途差异。	READY
11207	11207	SUV	C-Crosser I	EP	5	EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	HIGH	EP五门SUV外廓；Kasten/SUV为登记用途差异。	READY
57402	57402	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH	DD四门Phase I外廓。	READY
117342	117342	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH	DD四门Phase I外廓。	READY
117340	117340	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH	DD四门Phase I外廓。	READY
57403	57403	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH	DD四门Phase I外廓。	READY
57404	57404	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH	DD四门Phase I外廓。	READY
17461	17461	Sedan	CX I		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
6577	6577	Sedan	CX I		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17430	17430	Sedan	CX I		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17432	17432	Sedan	CX I		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17431	17431	Sedan	CX I		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17462	17462	Wagon	CX I		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
6585	6585	Wagon	CX I		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
6584	6584	Wagon	CX I		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17433	17433	Wagon	CX I		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17464	17464	Sedan	CX II		4		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
15073	15073	Wagon	CX II		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17465	17465	Wagon	CX II		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
17429	17429	Wagon	CX II		5		LOW	候选尺寸在Series/Phase资料间存在长度与宽度口径冲突，待按具体车身阶段闭合。	PENDING: CX具体阶段三维与宽度口径尚未闭合
112395	112395	Hatchback	C-Zero I		5	EU-CITROEN-C-ZERO-I-HATCHBACK-5D-01	HIGH	五门电动微型车外廓。	READY
15076	15076	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	MEDIUM	输入起始年月早于量产Cabriolet记录；按DS Cabriolet物理外廓归组。	READY
15133	15133	Wagon	DS I		5	EU-CITROEN-DS-I-WAGON-5D-01	HIGH	DS Break五门长车身外廓。	READY
15074	15074	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	HIGH	DS 21 Cabriolet双门外廓。	READY
15075	15075	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	HIGH	DS 21 Cabriolet双门外廓。	READY
15134	15134	Wagon	DS I		5	EU-CITROEN-DS-I-WAGON-5D-01	HIGH	DS Break五门长车身外廓。	READY
108598	108598	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
108600	108600	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58578	58578	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58583	58583	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
12291	12291	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58579	58579	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58570	58570	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
107159	107159	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
108159	108159	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
117894	117894	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
100643	100643	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
107569	107569	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
117893	117893	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58582	58582	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
100642	100642	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
58586	58586	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
5091	5091	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-RACING-01	HIGH	SA三门Racing宽体低车身外廓。	READY
108686	108686	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-RACING-01	HIGH	SB Cabriolet Racing宽体低车身外廓。	READY
12290	12290	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
59305	59305	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
58585	58585	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
109261	109261	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH	SA三门Hatchback外廓。	READY
109321	109321	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
58584	58584	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH	SB Cabriolet双门固定侧围软顶外廓。	READY
109325	109325	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
117920	117920	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
108856	108856	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
58671	58671	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
59311	59311	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
55402	55402	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
49684	49684	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
109324	109324	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
109323	109323	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
59310	59310	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH	NX五门外廓。	READY
108149	108149	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
100512	100512	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
10885	10885	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
59306	59306	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
59891	59891	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
10877	10877	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
51869	51869	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
108053	108053	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	MEDIUM	输入标注汽油混合动力但未指向Hybrid4四驱；按KF标准外廓归组。	READY
10878	10878	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
108854	108854	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
50144	50144	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
59308	59308	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
10886	10886	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH	KF五门标准外廓。	READY
53387	53387	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-HYBRID4-01	HIGH	KF Hybrid4四驱增高外廓。	READY
6026	6026	Hatchback	Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	早期Dyane 4归入Phase I外廓。	READY
6025_phase1	6025	Hatchback	Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	Ktype跨越Phase I，拆分早期外廓。	READY
6025_phase2	6025	Hatchback	Dyane I Phase II		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	Ktype跨越Phase II，拆分中期外廓。	READY
6025_phase3	6025	Hatchback	Dyane I Phase III		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-III-01	MEDIUM	Ktype跨越Phase III，拆分后期外廓。	READY
121049	121049	Convertible	E-Méhari I		2	EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	HIGH	双门开放式电动车外廓。	READY
155895	155895	Convertible	E-Méhari I		2	EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	HIGH	双门开放式电动车外廓。	READY
17428	17428	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH	22代号五门MPV外廓。	READY
11370	11370	MPV	Evasion I		5	EU-CITROEN-EVASION-I-MPV-5D-01	MEDIUM	生产期跨22/U6U编码过渡，外部三维保持同组。	READY
15085	15085	MPV	Evasion I	U6U	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH	U6U五门MPV外廓。	READY
13862	13862	MPV	Evasion I	U6U	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH	U6U五门MPV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C6-I-TD-SEDAN-4D-01	4908	1860	1464	Automobile-Catalog Citroën C6 technical data	https://www.automobile-catalog.com/car/2012/1453025/citroen_c6_v6_hdi_240_exclusive_automatic.html
EU-CITROEN-C8-I-MPV-5D-01	4726	1854	1752	Citroën C8 technical information	https://www.citroenet.org.uk/passenger-cars/psa/c8/c8-14.html
EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	4646	1806	1670	Automobile-Catalog Citroën C-Crosser technical data	https://www.automobile-catalog.com/car/2007/552620/citroen_c-crosser_hdi_155_fap_exclusive.html
EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	4427	1748	1466	Citroën C-Elysée official technical specifications	https://files.citroen.ua/th/C-ELYSEE.PDF
EU-CITROEN-C-ZERO-I-HATCHBACK-5D-01	3475	1475	1600	Citroën C-Zero UK brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Citroen-C-Zero-2017-UK.pdf
EU-CITROEN-DS-I-CONVERTIBLE-2D-01	4840	1790	1420	Carfolio Citroën DS 21 Cabriolet technical data	https://www.carfolio.com/citroen-ds-21-cabriolet-749859
EU-CITROEN-DS-I-WAGON-5D-01	5026	1803	1530	Automobile-Catalog Citroën DS 23 Break technical data	https://www.automobile-catalog.com/car/1972/127775/citroen_ds_23_break.html
EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	3948	1715	1483	Citroën DS3 Cabrio UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS3-Cabrio-2012-UK.pdf
EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	3948	1715	1458	Automobile-Catalog Citroën DS3 technical data	https://www.automobile-catalog.com/car/2011/1214165/citroen_ds3_thp_150_sportchic.html
EU-CITROEN-DS3-I-SA-HATCHBACK-3D-RACING-01	3962	1717	1443	Automobile-Catalog Citroën DS3 Racing technical data	https://www.automobile-catalog.com/car/2011/1451810/citroen_ds3_racing.html
EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-RACING-01	3962	1717	1443	Automobile-Catalog Citroën DS3 Cabrio Racing technical data	https://www.automobile-catalog.com/car/2014/2086055/citroen_ds3_cabrio_racing.html
EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	4275	1810	1523	Citroën DS4 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS4-2011-UK.pdf
EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	4530	1871	1504	Automobile-Catalog Citroën DS5 technical data	https://www.automobile-catalog.com/car/2012/1694900/citroen_ds5_thp_155_sochic_automatic.html
EU-CITROEN-DS5-I-KF-HATCHBACK-5D-HYBRID4-01	4530	1871	1513	Automobile-Catalog Citroën DS5 Hybrid4 technical data	https://www.automobile-catalog.com/car/2012/1695095/citroen_ds5_hybrid4_airdream_sportchic.html
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	3905	1500	1540	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-II-01	3870	1500	1540	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-III-01	3874	1500	1525	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	3809	1728	1653	Automobile Dimensions Citroën E-Méhari	https://www.automobiledimension.com/model/citroen/e-mehari
EU-CITROEN-EVASION-I-MPV-5D-01	4454	1812	1710	Automobile-Catalog Citroën Evasion 1.9 Turbo D; Automobile-Catalog Citroën Evasion 2.0i 16V	https://www.automobile-catalog.com/car/1995/545450/citroen_evasion_1_9_turbo_d_sx.html;https://www.automobile-catalog.com/car/1998/545540/citroen_evasion_2_0i_16v_x.html
```

## 下一步优先处理

1. 按 CX 的 `Sedan/Wagon × Series I/II × Phase` 聚类，先确定各阶段实际车身边界。
2. 优先闭合 1980–1985 CX I Sedan 与 Break，再处理 1985 年后的 CX II Sedan 与 Break。
3. 仅在不含后视镜宽度和同配置三维全部确认后创建 CX 尺寸组，并批量消除剩余 13 条 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/1453025/citroen_c6_v6_hdi_240_exclusive_automatic.html?utm_source=chatgpt.com "2012 Citroen C6 V6 HDi 240 Exclusive automatic (aut. 6)"
[2]: https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS3-Cabrio-2012-UK.pdf "https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS3-Cabrio-2012-UK.pdf"
[3]: https://autocatalogarchive.com/wp-content/uploads/2018/02/Citroen-C-Zero-2017-UK.pdf "https://autocatalogarchive.com/wp-content/uploads/2018/02/Citroen-C-Zero-2017-UK.pdf"
[4]: https://www.automobile-catalog.com/make/citroen/cx/cx_series_1_salon/1981.html?utm_source=chatgpt.com "1981 Citroen CX phase-I Salon full range specs"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3701-3800_ktype_dimension_mapping_final.tsv
- left18448_3701-3800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 剩余 13 条 CX PENDING 已全部闭合。CX I 按 1982 年阶段变化拆分 Sedan 和 Wagon；早期 Break、CX II Sedan、CX II Wagon 分别建立独立尺寸组。CX I Sedan 前期与 1982 阶段宽度分别为 1734 mm、1770 mm；对应 Wagon 同样区分 1734 mm 与 1770 mm。([Auto Data][1])
* Ktype `17461`、`17462` 均跨越物理外廓变化阶段，已分别拆分为 `pre82` 与 `phase82` 派生映射。
* CX 早期 Break 使用 4922 × 1734 × 1465 mm；CX II Sedan 使用 4650 × 1770 × 1360 mm；CX II Wagon 使用 4930 × 1770 × 1460 mm，宽度均按不含后视镜口径落盘。([汽车目录][2])
* 已完成固定表头、唯一主键、映射引用闭合、尺寸和来源非空、文件链接存在等机械检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：104 行，覆盖全部 100 个 Ktype
* PENDING 映射：0
* DIMENSION_GROUP：27 个
* 唯一 `id`：104 个
* 所有尺寸组均被映射引用，无孤立组
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145503	145503	Wagon	C5 X I	ND	5	EU-CITROEN-C5-X-I-ND-WAGON-5D-01	HIGH	输入C5 Kombi对应C5 X ND五门外廓。	READY
58669	58669	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH		READY
18772	18772	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH		READY
18771	18771	Sedan	C6 I	TD	4	EU-CITROEN-C6-I-TD-SEDAN-4D-01	HIGH		READY
16726	16726	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
142684	142684	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
142685	142685	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
16727	16727	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
142686	142686	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
142687	142687	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
19011	19011	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
16729	16729	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
101093	101093	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
16730	16730	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
58668	58668	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
16728	16728	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH		READY
142691	142691	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
142690	142690	Van	C8 I		5	EU-CITROEN-C8-I-MPV-5D-01	HIGH	商用登记车身与乘用MPV共用外部壳体。	READY
142692	142692	SUV	C-Crosser I	EP	5	EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	HIGH	Kasten/SUV为登记用途差异。	READY
11207	11207	SUV	C-Crosser I	EP	5	EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	HIGH		READY
57402	57402	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH		READY
117342	117342	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH		READY
117340	117340	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH		READY
57403	57403	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH		READY
57404	57404	Sedan	C-Elysée II Phase I	DD	4	EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	HIGH		READY
17461_pre82	17461	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-PRE82-01	MEDIUM	Ktype跨越1982阶段边界，拆分前期窄体。	READY
17461_phase82	17461	Sedan	CX I Phase 1982		4	EU-CITROEN-CX-I-SEDAN-4D-PHASE-1982-01	MEDIUM	Ktype跨越1982阶段边界，拆分后期宽体。	READY
6577	6577	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-PRE82-01	HIGH		READY
17430	17430	Sedan	CX I Phase 1982		4	EU-CITROEN-CX-I-SEDAN-4D-PHASE-1982-01	HIGH		READY
17432	17432	Sedan	CX I Phase 1982		4	EU-CITROEN-CX-I-SEDAN-4D-PHASE-1982-01	HIGH		READY
17431	17431	Sedan	CX I Phase 1982		4	EU-CITROEN-CX-I-SEDAN-4D-PHASE-1982-01	HIGH		READY
17462_pre82	17462	Wagon	CX I		5	EU-CITROEN-CX-I-WAGON-5D-PRE82-01	MEDIUM	Ktype跨越1982阶段边界，拆分前期窄体。	READY
17462_phase82	17462	Wagon	CX I Break Phase 1982		5	EU-CITROEN-CX-I-WAGON-5D-PHASE-1982-01	MEDIUM	Ktype跨越1982阶段边界，拆分后期宽体。	READY
6585	6585	Wagon	CX I		5	EU-CITROEN-CX-I-WAGON-5D-PRE82-01	HIGH		READY
6584	6584	Wagon	CX I		5	EU-CITROEN-CX-I-WAGON-5D-EARLY-01	HIGH	早期Break采用较短车身外廓。	READY
17433	17433	Wagon	CX I Break Phase 1982		5	EU-CITROEN-CX-I-WAGON-5D-PHASE-1982-01	HIGH		READY
17464	17464	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
15073	15073	Wagon	CX II		5	EU-CITROEN-CX-II-WAGON-5D-01	HIGH		READY
17465	17465	Wagon	CX II		5	EU-CITROEN-CX-II-WAGON-5D-01	HIGH		READY
17429	17429	Wagon	CX II		5	EU-CITROEN-CX-II-WAGON-5D-01	HIGH		READY
112395	112395	Hatchback	C-Zero I		5	EU-CITROEN-C-ZERO-I-HATCHBACK-5D-01	HIGH		READY
15076	15076	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	MEDIUM	输入起始年月早于量产Cabriolet记录；按已确认Cabriolet外廓归组。	READY
15133	15133	Wagon	DS I		5	EU-CITROEN-DS-I-WAGON-5D-01	HIGH		READY
15074	15074	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	HIGH		READY
15075	15075	Convertible	DS I		2	EU-CITROEN-DS-I-CONVERTIBLE-2D-01	HIGH		READY
15134	15134	Wagon	DS I		5	EU-CITROEN-DS-I-WAGON-5D-01	HIGH		READY
108598	108598	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
108600	108600	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58578	58578	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58583	58583	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
12291	12291	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58579	58579	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58570	58570	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
107159	107159	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
108159	108159	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
117894	117894	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
100643	100643	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
107569	107569	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
117893	117893	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58582	58582	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
100642	100642	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
58586	58586	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
5091	5091	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-RACING-01	HIGH	Racing特殊外廓。	READY
108686	108686	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-RACING-01	HIGH	Racing特殊外廓。	READY
12290	12290	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
59305	59305	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
58585	58585	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
109261	109261	Hatchback	DS3 I	SA	3	EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	HIGH		READY
109321	109321	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
58584	58584	Convertible	DS3 I	SB	2	EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	HIGH		READY
109325	109325	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
117920	117920	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
108856	108856	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
58671	58671	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
59311	59311	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
55402	55402	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
49684	49684	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
109324	109324	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
109323	109323	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
59310	59310	Hatchback	DS4 I	NX	5	EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	HIGH		READY
108149	108149	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
100512	100512	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
10885	10885	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
59306	59306	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
59891	59891	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
10877	10877	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
51869	51869	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
108053	108053	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	MEDIUM	输入标注汽油混合动力但未指向Hybrid4四驱；按标准KF外廓归组。	READY
10878	10878	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
108854	108854	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
50144	50144	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
59308	59308	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
10886	10886	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	HIGH		READY
53387	53387	Hatchback	DS5 I	KF	5	EU-CITROEN-DS5-I-KF-HATCHBACK-5D-HYBRID4-01	HIGH	Hybrid4四驱增高外廓。	READY
6026	6026	Hatchback	Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	早期Dyane 4归入Phase I外廓。	READY
6025_phase1	6025	Hatchback	Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	Ktype跨越三个阶段，拆分Phase I外廓。	READY
6025_phase2	6025	Hatchback	Dyane I Phase II		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	Ktype跨越三个阶段，拆分Phase II外廓。	READY
6025_phase3	6025	Hatchback	Dyane I Phase III		5	EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-III-01	MEDIUM	Ktype跨越三个阶段，拆分Phase III外廓。	READY
121049	121049	Convertible	E-Méhari I		2	EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	HIGH		READY
155895	155895	Convertible	E-Méhari I		2	EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	HIGH		READY
17428	17428	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH		READY
11370	11370	MPV	Evasion I		5	EU-CITROEN-EVASION-I-MPV-5D-01	MEDIUM	生产期跨车身代码过渡，外部外廓保持同组。	READY
15085	15085	MPV	Evasion I	U6U	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH		READY
13862	13862	MPV	Evasion I	U6U	5	EU-CITROEN-EVASION-I-MPV-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_3701-3800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C5-X-I-ND-WAGON-5D-01	4805	1865	1485	Citroën C5 X official price and specification guide	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/tools/brochure/pdf/brochures/new-brochures/cars/c5x/C5-X-price-and-specification-guide.pdf
EU-CITROEN-C6-I-TD-SEDAN-4D-01	4908	1860	1464	Automobile-Catalog Citroën C6 technical data	https://www.automobile-catalog.com/car/2012/1453025/citroen_c6_v6_hdi_240_exclusive_automatic.html
EU-CITROEN-C8-I-MPV-5D-01	4726	1854	1752	Citroën C8 technical information	https://www.citroenet.org.uk/passenger-cars/psa/c8/c8-14.html
EU-CITROEN-C-CROSSER-I-EP-SUV-5D-01	4646	1806	1670	Automobile-Catalog Citroën C-Crosser technical data	https://www.automobile-catalog.com/car/2007/552620/citroen_c-crosser_hdi_155_fap_exclusive.html
EU-CITROEN-C-ELYSEE-II-DD-SEDAN-4D-PHASE-I-01	4427	1748	1466	Citroën C-Elysée official technical specifications	https://files.citroen.ua/th/C-ELYSEE.PDF
EU-CITROEN-CX-I-SEDAN-4D-PRE82-01	4659	1734	1360	Auto-Data Citroën CX I 2400 technical data	https://www.auto-data.net/en/citroen-cx-i-2400-120hp-15017
EU-CITROEN-CX-I-SEDAN-4D-PHASE-1982-01	4659	1770	1360	Auto-Data Citroën CX I Phase 1982 25 D Turbo technical data	https://www.auto-data.net/en/citroen-cx-i-phase-i-1982-25-d-turbo-95hp-28143
EU-CITROEN-CX-I-WAGON-5D-PRE82-01	4952	1734	1465	Automobile-Catalog Citroën CX Break 2400 Super technical data	https://www.automobile-catalog.com/car/1981/532850/citroen_cx_break_2400_super.html
EU-CITROEN-CX-I-WAGON-5D-PHASE-1982-01	4952	1770	1465	Auto-Data Citroën CX I Break Phase 1982 generation specifications	https://www.auto-data.net/en/citroen-cx-i-break-phase-i-1982-generation-5370
EU-CITROEN-CX-I-WAGON-5D-EARLY-01	4922	1734	1465	Automobile-Catalog Citroën CX Break 2200 Diesel Confort technical data	https://www.automobile-catalog.com/car/1977/532250/citroen_cx_break_2200_diesel_confort.html
EU-CITROEN-CX-II-SEDAN-4D-01	4650	1770	1360	Auto-Data Citroën CX II 22 TRS technical data	https://www.auto-data.net/en/citroen-cx-ii-22-trs-115hp-14993
EU-CITROEN-CX-II-WAGON-5D-01	4930	1770	1460	Automobile-Catalog Citroën CX Break 22 RS technical data; Automobile-Catalog Citroën CX Break 25 TRD Turbo technical data	https://www.automobile-catalog.com/car/1988/540485/citroen_cx_break_22_rs.html;https://www.automobile-catalog.com/car/1986/540185/citroen_cx_break_25_trd_turbo.html
EU-CITROEN-C-ZERO-I-HATCHBACK-5D-01	3475	1475	1600	Citroën C-Zero UK brochure	https://autocatalogarchive.com/wp-content/uploads/2018/02/Citroen-C-Zero-2017-UK.pdf
EU-CITROEN-DS-I-CONVERTIBLE-2D-01	4840	1790	1420	Carfolio Citroën DS 21 Cabriolet technical data	https://www.carfolio.com/citroen-ds-21-cabriolet-749859
EU-CITROEN-DS-I-WAGON-5D-01	5026	1803	1530	Automobile-Catalog Citroën DS 23 Break technical data	https://www.automobile-catalog.com/car/1972/127775/citroen_ds_23_break.html
EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-01	3948	1715	1483	Citroën DS3 Cabrio UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS3-Cabrio-2012-UK.pdf
EU-CITROEN-DS3-I-SA-HATCHBACK-3D-01	3948	1715	1458	Automobile-Catalog Citroën DS3 technical data	https://www.automobile-catalog.com/car/2011/1214165/citroen_ds3_thp_150_sportchic.html
EU-CITROEN-DS3-I-SA-HATCHBACK-3D-RACING-01	3962	1717	1443	Automobile-Catalog Citroën DS3 Racing technical data	https://www.automobile-catalog.com/car/2011/1451810/citroen_ds3_racing.html
EU-CITROEN-DS3-I-SB-CONVERTIBLE-2D-RACING-01	3962	1717	1443	Automobile-Catalog Citroën DS3 Cabrio Racing technical data	https://www.automobile-catalog.com/car/2014/2086055/citroen_ds3_cabrio_racing.html
EU-CITROEN-DS4-I-NX-HATCHBACK-5D-01	4275	1810	1523	Citroën DS4 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Citroen-DS4-2011-UK.pdf
EU-CITROEN-DS5-I-KF-HATCHBACK-5D-01	4530	1871	1504	Automobile-Catalog Citroën DS5 technical data	https://www.automobile-catalog.com/car/2012/1694900/citroen_ds5_thp_155_sochic_automatic.html
EU-CITROEN-DS5-I-KF-HATCHBACK-5D-HYBRID4-01	4530	1871	1513	Automobile-Catalog Citroën DS5 Hybrid4 technical data	https://www.automobile-catalog.com/car/2012/1695095/citroen_ds5_hybrid4_airdream_sportchic.html
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-I-01	3905	1500	1540	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-II-01	3870	1500	1540	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-DYANE-I-HATCHBACK-5D-PHASE-III-01	3874	1500	1525	Auto-Data Citroën Dyane generation specifications	https://www.auto-data.net/en/citroen-dyane-model-1696
EU-CITROEN-E-MEHARI-I-CONVERTIBLE-2D-01	3809	1728	1653	Automobile Dimensions Citroën E-Méhari	https://www.automobiledimension.com/model/citroen/e-mehari
EU-CITROEN-EVASION-I-MPV-5D-01	4454	1812	1710	Automobile-Catalog Citroën Evasion 1.9 Turbo D; Automobile-Catalog Citroën Evasion 2.0i 16V	https://www.automobile-catalog.com/car/1995/545450/citroen_evasion_1_9_turbo_d_sx.html;https://www.automobile-catalog.com/car/1998/545540/citroen_evasion_2_0i_16v_x.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_3701-3800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/citroen-cx-i-2400-120hp-15017 "https://www.auto-data.net/en/citroen-cx-i-2400-120hp-15017"
[2]: https://www.automobile-catalog.com/car/1977/532250/citroen_cx_break_2200_diesel_confort.html "https://www.automobile-catalog.com/car/1977/532250/citroen_cx_break_2200_diesel_confort.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4410 行）
- 累计尺寸组：dimension_groups_final.tsv（1272 行）

