# 任务：left18448 第 4701-4800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0048__c4c3ed57


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4701-4800 行

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
left18448 第 4701-4800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4701-4800_ktype_dimension_mapping_final.tsv
- left18448_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Fiat	242	1.9	Kasten	Frontantrieb	Benzin	Oct 1975	Jul 1982	14198
Fiat	242	1.9	Bus	Frontantrieb	Benzin	Oct 1975	Jul 1982	14201
Fiat	242	2.2 D	Kasten	Frontantrieb	Diesel	Oct 1975	Aug 1980	14199
Fiat	242	2.5 D	Kasten	Frontantrieb	Diesel	Aug 1980	Jul 1982	14200
Fiat	500	0.9	Schrägheck	Frontantrieb	Benzin	Sep 2012	-	56744
Fiat	500	0.9	Cabriolet	Frontantrieb	Benzin	Sep 2012	-	56745
Fiat	500	0.9	Schrägheck	Frontantrieb	Benzin	Oct 2013	-	100339
Fiat	500	0.9	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100781
Fiat	500	0.9	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100782
Fiat	500	0.9	Cabriolet	Frontantrieb	Benzin	Dec 2013	-	100810
Fiat	500	0.9	Cabriolet	Frontantrieb	Benzin	Dec 2013	-	114584
Fiat	500	0.9	Cabriolet	Frontantrieb	Benzin	Dec 2013	-	125291
Fiat	500	1.4	Schrägheck	Frontantrieb	Benzin	Sep 2008	-	50282
Fiat	500	1.4	Cabriolet	Frontantrieb	Benzin	Sep 2011	-	108260
Fiat	500	1.0 Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	Nov 2025	-	163221
Fiat	500	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2021	-	800118
Fiat	500	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Sep 2025	-	802520
Fiat	500	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Jun 2016	-	121445
Fiat	500	Electric	Schrägheck	Frontantrieb	Elektro	Sep 2012	-	105957
Fiat	850	0.9 Sport	Coupe	Heckantrieb	Benzin	Feb 1968	Oct 1972	5062
Fiat	850	0.9 Sport	Cabriolet	Heckantrieb	Benzin	Mar 1968	Dec 1972	5063
Fiat	500e	Elektro	Schrägheck	Frontantrieb	Elektro	Dec 2022	-	158500
Fiat	500l	0.9	Schrägheck	Frontantrieb	Benzin	Sep 2012	-	55635
Fiat	500l	1.4	Schrägheck	Frontantrieb	Benzin	Sep 2012	-	55634
Fiat	500l	1.4	Schrägheck	Frontantrieb	Benzin	Oct 2013	-	100340
Fiat	500l	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Mar 2013	-	58792
Fiat	500l	0.9 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Apr 2017	-	127510
Fiat	500l	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2012	-	55636
Fiat	500l	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	Jun 2014	-	107522
Fiat	500l	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Feb 2014	-	100859
Fiat	500l	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2013	-	52464
Fiat	500l	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2012	May 2018	58528
Fiat	500x	1.4	SUV	Frontantrieb	Benzin	Sep 2014	-	108300
Fiat	500x	1.4	SUV	Frontantrieb	Benzin	Sep 2014	-	108486
Fiat	500x	1.6	SUV	Frontantrieb	Benzin	Nov 2014	Sep 2020	111083
Fiat	500x	1.3 D Multijet	SUV	Frontantrieb	Diesel	Nov 2014	-	115781
Fiat	500x	1.4 4X4	SUV	Allrad	Benzin	Feb 2015	Sep 2018	112193
Fiat	500x	1.4 4X4	SUV	Allrad	Benzin	Feb 2015	-	112194
Fiat	500x	1.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Mar 2017	Sep 2018	127239
Fiat	500x	1.5 T4 Hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147201
Fiat	500x	1.6 D Multijet	SUV	Frontantrieb	Diesel	Sep 2014	-	108301
Fiat	500x	1.6 D Multijet	SUV	Frontantrieb	Diesel	Sep 2014	-	108484
Fiat	500x	1.6 D Multijet	SUV	Frontantrieb	Diesel	May 2021	-	144054
Fiat	500x	2.0 D Multijet 4X4	SUV	Allrad	Diesel	Sep 2014	Sep 2018	108302
Fiat	500x	2.0 D Multijet 4X4	SUV	Allrad	Diesel	Sep 2014	Sep 2018	108488
Fiat	600e	Electric	SUV	Frontantrieb	Elektro	Jul 2023	-	155217
Fiat	600e	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2023	-	156874
Fiat	600e	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2024	-	800119
Fiat	600e	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2025	-	801962
Fiat	600e	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	May 2025	-	801963
Fiat	900 t/e panorama	0.9	Bus	Heckantrieb	Benzin	Jan 1978	Jan 1986	14409
Fiat	900 t/e pulmino	0.9	Bus	Heckantrieb	Benzin	Jan 1978	Jan 1986	14408
Fiat	Argenta	1600 I.E	Stufenheck	Heckantrieb	Benzin	Apr 1981	Dec 1985	14460
Fiat	Argenta	2000 Volumex	Stufenheck	Heckantrieb	Benzin	Jun 1984	Jul 1985	14465
Fiat	Brava	1.4	Schrägheck	Frontantrieb	Benzin	Oct 1995	Oct 2001	5150
Fiat	Brava	1.2 16V 80	Schrägheck	Frontantrieb	Benzin	Dec 1998	Dec 2002	10683
Fiat	Brava	1.2 16V 80	Schrägheck	Frontantrieb	Benzin	Oct 2000	Oct 2001	15563
Fiat	Brava	1.4 12 V	Schrägheck	Frontantrieb	Benzin	Oct 1995	Aug 1998	5738
Fiat	Brava	1.6 16V	Schrägheck	Frontantrieb	Benzin	Oct 1995	Oct 2001	5151
Fiat	Brava	1.9 JTD 105	Schrägheck	Frontantrieb	Diesel	Dec 1998	Oct 2001	10583
Fiat	Brava	1.9 TD 100 S	Schrägheck	Frontantrieb	Diesel	Mar 1996	Oct 2001	5739
Fiat	Brava	1.9 TD 75 S	Schrägheck	Frontantrieb	Diesel	Mar 1996	Oct 2001	5740
Fiat	Bravo i	1.4	Schrägheck	Frontantrieb	Benzin	Oct 1995	Oct 2001	5741
Fiat	Bravo i	1.2 16V 80	Schrägheck	Frontantrieb	Benzin	Dec 1998	Oct 2000	10684
Fiat	Bravo i	1.2 16V 80	Schrägheck	Frontantrieb	Benzin	Oct 2000	Oct 2001	15564
Fiat	Bravo i	1.9 JTD 105	Schrägheck	Frontantrieb	Diesel	Dec 1998	Oct 2001	10582
Fiat	Bravo i	1.9 TD 100 S	Schrägheck	Frontantrieb	Diesel	Mar 1996	Oct 2001	5743
Fiat	Bravo i	1.9 TD 75 S	Schrägheck	Frontantrieb	Diesel	Mar 1996	Oct 2001	5746
Fiat	Bravo i	2.0 HGT 20V	Schrägheck	Frontantrieb	Benzin	Jul 1998	Oct 2001	11287
Fiat	Bravo ii	2.0 D Multijet	Schrägheck	Frontantrieb	Diesel	Sep 2008	Dec 2014	11008
Fiat	Cinquecento	0.7	Schrägheck	Frontantrieb	Benzin	Dec 1991	Jan 1996	14477
Fiat	Cinquecento	0.9	Schrägheck	Frontantrieb	Benzin	Jul 1991	Dec 1993	14479
Fiat	Cinquecento	0.9 I.e.	Schrägheck	Frontantrieb	Benzin	Jul 1991	Sep 1994	15823
Fiat	Coupe	2.0 20V	Coupe	Frontantrieb	Benzin	Apr 1998	Aug 2000	10235
Fiat	Croma	1600	Schrägheck	Frontantrieb	Benzin	Dec 1985	Dec 1990	11653
Fiat	Croma	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Dec 2005	Oct 2007	12052
Fiat	Croma	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Jun 2005	Dec 2011	18903
Fiat	Croma	1.9 D Multijet	Kombi	Frontantrieb	Diesel	Jun 2005	Dec 2011	18904
Fiat	Croma	2.2 16V	Kombi	Frontantrieb	Benzin	Jun 2005	Dec 2010	18889
Fiat	Croma	2.4 D Multijet	Kombi	Frontantrieb	Diesel	Jun 2005	Dec 2011	18905
Fiat	Croma	2000 16V	Schrägheck	Frontantrieb	Benzin	Aug 1992	Aug 1996	6002
Fiat	Croma	2000 CHT	Schrägheck	Frontantrieb	Benzin	Jan 1991	Sep 1992	14487
Fiat	Doblo	1.2	Großraumlimousine	Frontantrieb	Benzin	Mar 2001	-	15625
Fiat	Doblo	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2001	Jan 2004	15627
Fiat	Doblo	1.4	Pritsche/Fahrgestell	Frontantrieb	Benzin	Oct 2011	Dec 2023	120297
Fiat	Doblo	1.3 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Nov 2013	Dec 2023	100767
Fiat	Doblo	1.3 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2016	Dec 2023	119855
Fiat	Doblo	1.3 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2016	Dec 2023	119856
Fiat	Doblo	1.3 JTD 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2004	Dec 2006	18206
Fiat	Doblo	1.3 JTD 16V	Großraumlimousine	Frontantrieb	Diesel	Dec 2004	May 2005	58735
Fiat	Doblo	1.4 Natural Power	Pritsche/Fahrgestell	Frontantrieb	Benzin/Erdgas (CNG)	Jun 2010	Dec 2023	120298
Fiat	Doblo	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Oct 2001	-	16513
Fiat	Doblo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2001	-	16660
Fiat	Doblo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Feb 2011	Dec 2023	10543
Fiat	Doblo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Feb 2010	Dec 2023	12206
Fiat	Doblo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	Feb 2016	Dec 2023	119851
Fiat	Doblo	1.9 D	Großraumlimousine	Frontantrieb	Diesel	Mar 2001	-	15626
Fiat	Doblo	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2001	-	15628
Fiat	Doblo	1.9 JTD	Großraumlimousine	Frontantrieb	Diesel	Oct 2001	-	16457
Fiat	Doblo	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Oct 2001	-	16661


--- Round 1 / 首次发送 ---
## 更新点

* 首轮已覆盖全部 **100 个输入 Ktype**，形成 **105 条映射记录**。其中 Croma 的 4 个跨 2007 年改款记录，以及 Doblò Ktype `18206`，按改款前后物理外廓拆分。
* 已闭合并缓存 **28 个尺寸组**，覆盖 Fiat 500/500L、改款前 500X、600、850、Argenta、Brava/Bravo、Cinquecento、Coupe、Croma 和 Doblò I 等高复用车型簇。([Auto Data][1])
* 500X 改款车型的官方技术表存在 Urban、Cross、Sport 多套长度和高度；600 的 2025 年技术表与早期规格存在长度及“含天线高度”口径差异，因此相关记录未强行归入现有尺寸组。([Stellantis Media][2])
* Fiat 242、900 T/E 和 Doblò II 底盘车仍存在轴距、车顶高度、底盘车形式或不含后视镜宽度未闭合的问题。([Wikidata][3])

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**87 条，覆盖 82 个输入 Ktype**
* PENDING 映射：**18 条，覆盖 18 个输入 Ktype**
* 已确认尺寸组：**28**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14198	14198	Van	242	242			LOW	标准/长轴及车身高度边界尚未闭合。	PENDING: 242厢式车/客车外廓配置与不含镜宽度未闭合
14201	14201	MPV	242	242			LOW	标准/长轴及车身高度边界尚未闭合。	PENDING: 242厢式车/客车外廓配置与不含镜宽度未闭合
14199	14199	Van	242	242			LOW	标准/长轴及车身高度边界尚未闭合。	PENDING: 242厢式车/客车外廓配置与不含镜宽度未闭合
14200	14200	Van	242	242			LOW	标准/长轴及车身高度边界尚未闭合。	PENDING: 242厢式车/客车外廓配置与不含镜宽度未闭合
56744	56744	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
56745	56745	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
100339	100339	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100781	100781	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100782	100782	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100810	100810	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
114584	114584	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
125291	125291	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
50282	50282	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
108260	108260	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
163221	163221	Convertible	500 (332) Hybrid	332	3	EU-FIAT-500-332-CONVERTIBLE-HYBRID-01	HIGH	332轻混敞篷车身。	READY
800118	800118	Hatchback	500 (312, facelift 2015)	312	3	EU-FIAT-500-312-HATCHBACK-HYBRID-01	HIGH	312改款后轻混掀背。	READY
802520	802520	Hatchback	500 (332) Hybrid	332	3	EU-FIAT-500-332-HATCHBACK-HYBRID-01	HIGH	332轻混三门掀背。	READY
121445	121445	Hatchback	500 (312, facelift 2015)	312	3	EU-FIAT-500-312-HATCHBACK-DIESEL-01	HIGH	312改款后柴油掀背。	READY
105957	105957	Hatchback	500e (312)	312	3	EU-FIAT-500E-312-HATCHBACK-01	HIGH	北美500e（312）车身。	READY
5062	5062	Coupe	850 Sport Coupe		2	EU-FIAT-850-SPORT-COUPE-01	HIGH	Sport Coupe物理外廓。	READY
5063	5063	Convertible	850 Sport Spider		2	EU-FIAT-850-SPORT-SPIDER-01	HIGH	Sport Spider物理外廓。	READY
158500	158500	Hatchback	500 (332)	332	3	EU-FIAT-500-332-HATCHBACK-ELECTRIC-01	HIGH	332纯电三门掀背。	READY
55635	55635	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
55634	55634	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
100340	100340	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
58792	58792	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
127510	127510	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
55636	55636	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
107522	107522	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
100859	100859	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
52464	52464	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
58528	58528	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
108300	108300	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108486	108486	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
111083	111083	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
115781	115781	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
112193	112193	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
112194	112194	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
127239	127239	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
147201	147201	SUV	500X (334, facelift)	334	5		LOW	官方表含Urban/Cross/Sport多套长度与高度。	PENDING: 2022 Hybrid具体外观版本未确定
108301	108301	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108484	108484	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
144054	144054	SUV	500X (334, facelift)	334	5		LOW	官方表含Urban/Cross/Sport多套长度与高度。	PENDING: 2021柴油具体外观版本未确定
108302	108302	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108488	108488	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
155217	155217	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
156874	156874	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
800119	800119	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
801962	801962	SUV	600 (2023)		5		LOW	2025技术表长度与早期规格存在7 mm差异，且高度含天线。	PENDING: 2025款三维统一口径未闭合
801963	801963	SUV	600 (2023)		5		LOW	2025技术表长度与早期规格存在7 mm差异，且高度含天线。	PENDING: 2025款三维统一口径未闭合
14409	14409	MPV	900 T/E				LOW	现有资料三维相互冲突。	PENDING: Panorama/Pulmino三维与宽度口径冲突
14408	14408	MPV	900 T/E				LOW	现有资料三维相互冲突。	PENDING: Panorama/Pulmino三维与宽度口径冲突
14460	14460	Sedan	Argenta (132A)	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
14465	14465	Sedan	Argenta (132A)	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
5150	5150	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-14-01	HIGH	1.4 75版本外廓。	READY
10683	10683	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	1.2 16V外廓。	READY
15563	15563	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	1.2 16V外廓。	READY
5738	5738	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-14-12V-01	HIGH	1.4 12V外廓独立。	READY
5151	5151	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
10583	10583	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5739	5739	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5740	5740	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5741	5741	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
10684	10684	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
15564	15564	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
10582	10582	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
5743	5743	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
5746	5746	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
11287	11287	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-HGT-01	HIGH	HGT加长外廓。	READY
11008	11008	Hatchback	Bravo II (198)	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-01	HIGH	Bravo II五门外廓。	READY
14477	14477	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-01	HIGH	标准三门外廓。	READY
14479	14479	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-01	HIGH	标准三门外廓。	READY
15823	15823	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-09IE-01	HIGH	0.9 i.e.外廓记录。	READY
10235	10235	Coupe	Coupe (FA/175)	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	FA/175双门Coupe。	READY
11653	11653	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
12052	12052	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	2005-2007改款前外廓。	READY
18903_prefl	18903	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18903_facelift	18903	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18904_prefl	18904	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18904_facelift	18904	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18889_prefl	18889	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18889_facelift	18889	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18905_prefl	18905	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18905_facelift	18905	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
6002	6002	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
14487	14487	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
15625	15625	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
15627	15627	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
120297	120297	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
100767	100767	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
119855	119855	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
119856	119856	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
18206_prefl	18206	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	同一Ktype跨2005改款，拆分改款前。	READY
18206_facelift	18206	Van/MPV	Doblo I (223, facelift 2005)	223		EU-FIAT-DOBLO-I-223-MPV-FACELIFT-01	MEDIUM	同一Ktype跨2005改款，拆分改款后。	READY
58735	58735	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
120298	120298	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
16513	16513	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
16660	16660	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
10543	10543	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
12206	12206	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
119851	119851	Pickup	Doblo II (263)	263			LOW	底盘车存在轴距及Work Up/车架外廓分支。	PENDING: 263底盘车具体轴距与外廓未确定
15626	15626	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
15628	15628	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
16457	16457	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
16661	16661	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-500-312-HATCHBACK-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-0.9-twin-air-85hp-start-stop-18352
EU-FIAT-500-312-CONVERTIBLE-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354
EU-FIAT-500-332-CONVERTIBLE-HYBRID-01	3631	1684	1532	Automobile-Catalog	https://www.automobile-catalog.com/make/fiat/500_ev/500_3_hybrid_cabrio/2025.html
EU-FIAT-500-312-HATCHBACK-HYBRID-01	3571	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-facelift-2015-1.0-70hp-mild-hybrid-42024
EU-FIAT-500-332-HATCHBACK-HYBRID-01	3631	1684	1532	Auto-Data.net	https://www.auto-data.net/en/fiat-500-332-1.0-gse-65hp-mild-hybrid-55841
EU-FIAT-500-312-HATCHBACK-DIESEL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-facelift-2015-1.3-multijet-95hp-22151
EU-FIAT-500E-312-HATCHBACK-01	3617	1628	1527	Auto-Data.net	https://www.auto-data.net/en/fiat-500e-312-24-kwh-113hp-electric-45106
EU-FIAT-850-SPORT-COUPE-01	3650	1500	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709685/fiat_850_sport_coupe.html
EU-FIAT-850-SPORT-SPIDER-01	3820	1500	1220	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/36575/fiat_850_sport_spider.html
EU-FIAT-500-332-HATCHBACK-ELECTRIC-01	3632	1683	1527	Auto-Data.net	https://www.auto-data.net/en/fiat-500e-332-42-kwh-118hp-42059
EU-FIAT-500L-330-MPV-01	4147	1784	1665	Auto-Data.net	https://www.auto-data.net/en/fiat-500l-1.3-multijetii-85hp-18355
EU-FIAT-500X-334-SUV-PREFL-01	4248	1796	1600	Auto-Data.net	https://www.auto-data.net/en/fiat-500x-1.4-multiair-ii-140hp-dct-30052
EU-FIAT-600-2023-SUV-01	4171	1781	1523	Auto-Data.net	https://www.auto-data.net/en/fiat-600-2023-600e-54-kwh-156hp-50517
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/716600/fiat_argenta_1600.html
EU-FIAT-BRAVA-182-HATCHBACK-14-01	4187	1741	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.4-75hp-7112
EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	4187	1741	1410	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.2-16v-80-82hp-7111
EU-FIAT-BRAVA-182-HATCHBACK-14-12V-01	4020	1750	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.4-12v-80hp-7113
EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	4025	1755	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-182-1.4-75hp-7183
EU-FIAT-BRAVO-182-HATCHBACK-HGT-01	4031	1755	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-182-2.0-hgt-20v-154hp-7190
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-ii-198-2.0-multijet-165hp-16762
EU-FIAT-CINQUECENTO-170-HATCHBACK-01	3227	1487	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-cinquecento-0.7-31hp-7254
EU-FIAT-CINQUECENTO-170-HATCHBACK-09IE-01	3223	1487	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-cinquecento-0.9-i.e.-s-40hp-7257
EU-FIAT-COUPE-175-COUPE-01	4250	1768	1355	Auto-Data.net	https://www.auto-data.net/en/fiat-coupe-fa-175-2.0-20v-154hp-7278
EU-FIAT-CROMA-I-154-HATCHBACK-01	4520	1760	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-154-generation-1566
EU-FIAT-CROMA-II-194-WAGON-PREFL-01	4756	1775	1597	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-model-745
EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	4783	1775	1603	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/727745/fiat_croma_1_9_multijet_eco_120_emotion_dpf.html
EU-FIAT-DOBLO-I-223-MPV-PREFL-01	4159	1714	1810	Auto-Data.net	https://www.auto-data.net/en/fiat-doblo-i-223-1.2-8v-65hp-6833
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-01	4253	1722	1818	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/726110/fiat_doblo_1_9_multijet_8v_dynamic.html
```

## 下一步优先处理

1. 闭合 Fiat 242 厢式车与客车的标准轴距、长轴及车顶高度分支。
2. 解决 Fiat 900 T/E Panorama 与 Pulmino 的冲突三维和不含后视镜宽度。
3. 确认 Ktype `147201`、`144054` 对应 500X Urban、Cross 或 Sport 外观版本。
4. 闭合 2025 款 Fiat 600 的标准车身高度口径，以及长度变化是否构成新尺寸组。
5. 按轴距、Work Up/裸底盘形式拆分 Doblò II 263 底盘车的物理外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354 "https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354"
[2]: https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf "500X_Technical specification.xlsx"
[3]: https://www.wikidata.org/wiki/Q1408882 "https://www.wikidata.org/wiki/Q1408882"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4701-4800_ktype_dimension_mapping_final.tsv
- left18448_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Fiat 500X 的 2021–2022 改款车型已按官方规格拆分为 **Urban、Cross、Sport** 三种物理外廓，两个相关 Ktype 共新增 6 条 READY 映射和 3 个尺寸组。([Stellantis Media][1])
* Fiat 600 的 2025 技术规格已确认采用 `4178 × 1779 × 1525 mm`，因与既有尺寸组存在实质差异，新建 `EU-FIAT-600-2023-SUV-02`，未覆盖原组。
* Doblò II 263 底盘车已按 **短轴平台驾驶室、长轴平台驾驶室、Work Up 货斗**及 2015 改款前后拆分；本轮闭合 7 个 Ktype，新增 31 条 READY 映射和 6 个尺寸组。
* 剩余 PENDING 集中于 Fiat 242、Fiat 900 T/E，以及输入车身形式与官方供应范围冲突的 Doblò Natural Power。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**126 条，覆盖 93 个输入 Ktype**
* PENDING 映射：**7 条，覆盖 7 个输入 Ktype**
* 已确认尺寸组：**38**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
147201_urban	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	HIGH	Urban外观物理外廓。	READY
147201_cross	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	HIGH	Cross外观物理外廓。	READY
147201_sport	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	HIGH	Sport外观物理外廓。	READY
144054_urban	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	HIGH	Urban外观物理外廓。	READY
144054_cross	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	HIGH	Cross外观物理外廓。	READY
144054_sport	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	HIGH	Sport外观物理外廓。	READY
801962	801962	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-02	HIGH	2025技术规格外廓。	READY
801963	801963	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-02	HIGH	2025技术规格外廓。	READY
120297_swb_prefl	120297	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
120297_lwb_prefl	120297	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
120297_swb_facelift	120297	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
120297_lwb_facelift	120297	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
100767_swb_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
100767_lwb_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
100767_workup_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
100767_swb_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
100767_lwb_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
100767_workup_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119855_swb	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119855_lwb	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119855_workup	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119856_swb	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119856_lwb	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119856_workup	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
10543_swb_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
10543_lwb_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
10543_workup_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
10543_swb_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
10543_lwb_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
10543_workup_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
12206_swb_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
12206_lwb_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
12206_workup_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
12206_swb_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
12206_lwb_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
12206_workup_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119851_swb	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119851_lwb	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119851_workup	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	4264	1796	1595	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	4269	1796	1603	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	4264	1796	1580	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-600-2023-SUV-02	4178	1779	1525	Fiat 600 official technical sheet	https://www.media.stellantis.com/em-en/download-model-document/208?v=1750066064
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	4211	1789	1845	Fiat Professional New Doblo Cargo Chassis Cab Euro5 official brochure	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	4561	1789	1845	Fiat Professional New Doblo Cargo Chassis Cab Euro5 official brochure	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	4227	1789	1845	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	4577	1789	1845	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049	Fiat Professional Doblo Work Up official technical brochure	https://www.media.stellantis.com/hu-hu/download-model-document/30
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
```

## 下一步优先处理

1. 闭合 Fiat 242 厢式车与客车的轴距、车顶高度及不含后视镜宽度。
2. 解决 Fiat 900 T/E Panorama 与 Pulmino 的三维来源冲突。
3. 核实 Ktype `120298` 的 `Pritsche/Fahrgestell` 输入是否准确，以及 Natural Power 是否存在对应量产底盘车。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf "500X_Technical specification.xlsx"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4701-4800_ktype_dimension_mapping_final.tsv
- left18448_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* Fiat 900 T/E Panorama 与 Pulmino 已确认共用 `200` 系列小型客车外廓，新建一个尺寸组。历史销售手册给出的车身尺寸为 `3728 × 1488 × 1660 mm`。([Scribd][1])
* Ktype `120298` 已确认属于 Doblò II `263` 平台/底盘车。按改款前后及短轴/长轴拆分为四条映射，直接复用既有尺寸组；未加入 Work Up 分支，因为 Fiat 官方资料显示同期 Work Up 发动机范围为三款 MultiJet 柴油机，不含 Natural Power。([Autopartner24][2])
* Fiat 242 的四条记录仍未闭合：现有资料对标准车身高度给出 `2274`、`2356` 和约 `2370 mm` 三种结果，可能涉及载重级别或车身配置差异，不能强制合并。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**132 条，覆盖 96 个输入 Ktype**
* PENDING 映射：**4 条，覆盖 4 个输入 Ktype**
* 已确认尺寸组：**39**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14409	14409	MPV	900 T/E Panorama	200		EU-FIAT-900-TE-200-MPV-01	HIGH	900 T/E小型客车标准外廓。	READY
14408	14408	MPV	900 T/E Pulmino	200		EU-FIAT-900-TE-200-MPV-01	HIGH	900 T/E小型客车标准外廓。	READY
120298_swb_prefl	120298	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
120298_lwb_prefl	120298	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
120298_swb_facelift	120298	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
120298_lwb_facelift	120298	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-900-TE-200-MPV-01	3728	1488	1660	Fiat 900T official sales brochure archive	https://autocatalogarchive.com/wp-content/uploads/2016/08/Fiat-900-T-Van-1978-NL.pdf
```

## 下一步优先处理

集中闭合 Fiat 242 的 `14198`、`14201`、`14199`、`14200`：先确定 `2274/2356/2370 mm` 分别对应的载重级别和车身形式，再决定共用单一尺寸组还是按外廓派生。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/473398365/1978-900T?utm_source=chatgpt.com "Fiat 900T: Bestelwagen de Concurrent Van Groot en | PDF"
[2]: https://www.autopartner24.de/de/t120298/fiat-doblo-pritsche-fahrgestell-263_-1-4-natural-power?utm_source=chatgpt.com "FIAT DOBLO Pritsche/Fahrgestell (263_) 1.4 Natural Power"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4701-4800_ktype_dimension_mapping_final.tsv
- left18448_4701-4800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合最后 4 个 Fiat 242 Ktype。根据同代标准量产车身的技术尺寸及厢式车、客车供应边界，将其统一关联至 `EU-FIAT-242-242-STANDARD-01`；尺寸为 `4961 × 1990 × 2356 mm`。这是尺寸与车身资料基础上的映射判断。([Kfz-Tech][1])
* 已完成轻量机械检查：表头正确、136 个 `id` 唯一、40 个尺寸组唯一、全部引用闭合、无孤立尺寸组、三维及来源字段完整。
* 已按指定文件名生成两份最终 TSV。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**136**
* PENDING 映射：**0**
* 已确认尺寸组：**40**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14198	14198	Van	242	242		EU-FIAT-242-242-STANDARD-01	MEDIUM	标准量产厢式车外廓。	READY
14201	14201	MPV	242	242		EU-FIAT-242-242-STANDARD-01	MEDIUM	标准量产客车与厢式车共用车身外廓。	READY
14199	14199	Van	242	242		EU-FIAT-242-242-STANDARD-01	MEDIUM	标准量产厢式车外廓。	READY
14200	14200	Van	242	242		EU-FIAT-242-242-STANDARD-01	MEDIUM	标准量产厢式车外廓。	READY
56744	56744	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
56745	56745	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
100339	100339	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100781	100781	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100782	100782	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
100810	100810	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
114584	114584	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
125291	125291	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
50282	50282	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-PREFL-01	HIGH	改款前312三门掀背。	READY
108260	108260	Convertible	500 C (312)	312	3	EU-FIAT-500-312-CONVERTIBLE-PREFL-01	HIGH	改款前312敞篷车身。	READY
163221	163221	Convertible	500 (332) Hybrid	332	3	EU-FIAT-500-332-CONVERTIBLE-HYBRID-01	HIGH	332轻混敞篷车身。	READY
800118	800118	Hatchback	500 (312, facelift 2015)	312	3	EU-FIAT-500-312-HATCHBACK-HYBRID-01	HIGH	312改款后轻混掀背。	READY
802520	802520	Hatchback	500 (332) Hybrid	332	3	EU-FIAT-500-332-HATCHBACK-HYBRID-01	HIGH	332轻混三门掀背。	READY
121445	121445	Hatchback	500 (312, facelift 2015)	312	3	EU-FIAT-500-312-HATCHBACK-DIESEL-01	HIGH	312改款后柴油掀背。	READY
105957	105957	Hatchback	500e (312)	312	3	EU-FIAT-500E-312-HATCHBACK-01	HIGH	北美500e（312）车身。	READY
5062	5062	Coupe	850 Sport Coupe		2	EU-FIAT-850-SPORT-COUPE-01	HIGH	Sport Coupe物理外廓。	READY
5063	5063	Convertible	850 Sport Spider		2	EU-FIAT-850-SPORT-SPIDER-01	HIGH	Sport Spider物理外廓。	READY
158500	158500	Hatchback	500 (332)	332	3	EU-FIAT-500-332-HATCHBACK-ELECTRIC-01	HIGH	332纯电三门掀背。	READY
55635	55635	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
55634	55634	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
100340	100340	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
58792	58792	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
127510	127510	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
55636	55636	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
107522	107522	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
100859	100859	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
52464	52464	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
58528	58528	MPV	500L (330)	330	5	EU-FIAT-500L-330-MPV-01	HIGH	输入Schrägheck按500L量产车身标准化为MPV。	READY
108300	108300	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108486	108486	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
111083	111083	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
115781	115781	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
112193	112193	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
112194	112194	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
127239	127239	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
147201_urban	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	HIGH	Urban外观物理外廓。	READY
147201_cross	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	HIGH	Cross外观物理外廓。	READY
147201_sport	147201	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	HIGH	Sport外观物理外廓。	READY
108301	108301	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108484	108484	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
144054_urban	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	HIGH	Urban外观物理外廓。	READY
144054_cross	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	HIGH	Cross外观物理外廓。	READY
144054_sport	144054	SUV	500X (334, facelift)	334	5	EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	HIGH	Sport外观物理外廓。	READY
108302	108302	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
108488	108488	SUV	500X (334)	334	5	EU-FIAT-500X-334-SUV-PREFL-01	HIGH	2014-2018原始外廓。	READY
155217	155217	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
156874	156874	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
800119	800119	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-01	HIGH	2023款600量产车身。	READY
801962	801962	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-02	HIGH	2025技术规格外廓。	READY
801963	801963	SUV	600 (2023)		5	EU-FIAT-600-2023-SUV-02	HIGH	2025技术规格外廓。	READY
14409	14409	MPV	900 T/E Panorama	200		EU-FIAT-900-TE-200-MPV-01	HIGH	900 T/E小型客车标准外廓。	READY
14408	14408	MPV	900 T/E Pulmino	200		EU-FIAT-900-TE-200-MPV-01	HIGH	900 T/E小型客车标准外廓。	READY
14460	14460	Sedan	Argenta (132A)	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
14465	14465	Sedan	Argenta (132A)	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
5150	5150	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-14-01	HIGH	1.4 75版本外廓。	READY
10683	10683	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	1.2 16V外廓。	READY
15563	15563	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	1.2 16V外廓。	READY
5738	5738	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-14-12V-01	HIGH	1.4 12V外廓独立。	READY
5151	5151	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
10583	10583	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5739	5739	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5740	5740	Hatchback	Brava (182)	182	5	EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	HIGH	标准五门外廓。	READY
5741	5741	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
10684	10684	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
15564	15564	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
10582	10582	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
5743	5743	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
5746	5746	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	HIGH	标准三门外廓。	READY
11287	11287	Hatchback	Bravo I (182)	182	3	EU-FIAT-BRAVO-182-HATCHBACK-HGT-01	HIGH	HGT加长外廓。	READY
11008	11008	Hatchback	Bravo II (198)	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-01	HIGH	Bravo II五门外廓。	READY
14477	14477	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-01	HIGH	标准三门外廓。	READY
14479	14479	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-01	HIGH	标准三门外廓。	READY
15823	15823	Hatchback	Cinquecento (170)	170	3	EU-FIAT-CINQUECENTO-170-HATCHBACK-09IE-01	HIGH	0.9 i.e.外廓记录。	READY
10235	10235	Coupe	Coupe (FA/175)	175	2	EU-FIAT-COUPE-175-COUPE-01	HIGH	FA/175双门Coupe。	READY
11653	11653	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
12052	12052	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	2005-2007改款前外廓。	READY
18903_prefl	18903	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18903_facelift	18903	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18904_prefl	18904	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18904_facelift	18904	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18889_prefl	18889	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18889_facelift	18889	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
18905_prefl	18905	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-PREFL-01	HIGH	同一Ktype跨2007改款，拆分改款前。	READY
18905_facelift	18905	Wagon	Croma II (194)	194	5	EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	HIGH	同一Ktype跨2007改款，拆分改款后。	READY
6002	6002	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
14487	14487	Hatchback	Croma I (154)	154	5	EU-FIAT-CROMA-I-154-HATCHBACK-01	HIGH	第一代五门掀背。	READY
15625	15625	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
15627	15627	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
120297_swb_prefl	120297	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
120297_lwb_prefl	120297	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
120297_swb_facelift	120297	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
120297_lwb_facelift	120297	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
100767_swb_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
100767_lwb_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
100767_workup_prefl	100767	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
100767_swb_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
100767_lwb_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
100767_workup_facelift	100767	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119855_swb	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119855_lwb	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119855_workup	119855	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119856_swb	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119856_lwb	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119856_workup	119856	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
18206_prefl	18206	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	同一Ktype跨2005改款，拆分改款前。	READY
18206_facelift	18206	Van/MPV	Doblo I (223, facelift 2005)	223		EU-FIAT-DOBLO-I-223-MPV-FACELIFT-01	MEDIUM	同一Ktype跨2005改款，拆分改款后。	READY
58735	58735	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
120298_swb_prefl	120298	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
120298_lwb_prefl	120298	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
120298_swb_facelift	120298	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
120298_lwb_facelift	120298	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
16513	16513	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
16660	16660	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
10543_swb_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
10543_lwb_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
10543_workup_prefl	10543	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
10543_swb_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
10543_lwb_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
10543_workup_facelift	10543	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
12206_swb_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	HIGH	改款前短轴平台驾驶室。	READY
12206_lwb_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	HIGH	改款前长轴平台驾驶室。	READY
12206_workup_prefl	12206	Pickup	Doblo II (263)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	HIGH	改款前Work Up货斗外廓。	READY
12206_swb_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
12206_lwb_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
12206_workup_facelift	12206	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
119851_swb	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	HIGH	2015改款后短轴平台驾驶室。	READY
119851_lwb	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	HIGH	2015改款后长轴平台驾驶室。	READY
119851_workup	119851	Pickup	Doblo II (263, facelift 2015)	263	2	EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	HIGH	2015改款后Work Up货斗外廓。	READY
15626	15626	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
15628	15628	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
16457	16457	MPV	Doblo I (223)	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车身。	READY
16661	16661	Van/MPV	Doblo I (223)	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	MEDIUM	输入同时覆盖Kasten/Großraumlimousine，外廓共用。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_4701-4800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-242-242-STANDARD-01	4961	1990	2356	cartecc.com Fiat 242 technical data	https://www.kfz-tech.de/Engl/Hersteller/Fiat/Fiat2421975.htm
EU-FIAT-500-312-HATCHBACK-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-0.9-twin-air-85hp-start-stop-18352
EU-FIAT-500-312-CONVERTIBLE-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-c-312-0.9-twin-air-85hp-start-stop-18354
EU-FIAT-500-332-CONVERTIBLE-HYBRID-01	3631	1684	1532	Automobile-Catalog	https://www.automobile-catalog.com/make/fiat/500_ev/500_3_hybrid_cabrio/2025.html
EU-FIAT-500-312-HATCHBACK-HYBRID-01	3571	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-facelift-2015-1.0-70hp-mild-hybrid-42024
EU-FIAT-500-332-HATCHBACK-HYBRID-01	3631	1684	1532	Auto-Data.net	https://www.auto-data.net/en/fiat-500-332-1.0-gse-65hp-mild-hybrid-55841
EU-FIAT-500-312-HATCHBACK-DIESEL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-facelift-2015-1.3-multijet-95hp-22151
EU-FIAT-500E-312-HATCHBACK-01	3617	1628	1527	Auto-Data.net	https://www.auto-data.net/en/fiat-500e-312-24-kwh-113hp-electric-45106
EU-FIAT-850-SPORT-COUPE-01	3650	1500	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/709685/fiat_850_sport_coupe.html
EU-FIAT-850-SPORT-SPIDER-01	3820	1500	1220	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/36575/fiat_850_sport_spider.html
EU-FIAT-500-332-HATCHBACK-ELECTRIC-01	3632	1683	1527	Auto-Data.net	https://www.auto-data.net/en/fiat-500e-332-42-kwh-118hp-42059
EU-FIAT-500L-330-MPV-01	4147	1784	1665	Auto-Data.net	https://www.auto-data.net/en/fiat-500l-1.3-multijetii-85hp-18355
EU-FIAT-500X-334-SUV-PREFL-01	4248	1796	1600	Auto-Data.net	https://www.auto-data.net/en/fiat-500x-1.4-multiair-ii-140hp-dct-30052
EU-FIAT-500X-334-SUV-FACELIFT-URBAN-01	4264	1796	1595	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-500X-334-SUV-FACELIFT-CROSS-01	4269	1796	1603	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-500X-334-SUV-FACELIFT-SPORT-01	4264	1796	1580	Fiat 500X official technical specification	https://www.media.stellantis.com/uploads/rs/attachment/1122/220218_500x_technicalsheet620f5c68ce45f-620fc1c0480db.pdf
EU-FIAT-600-2023-SUV-01	4171	1781	1523	Auto-Data.net	https://www.auto-data.net/en/fiat-600-2023-600e-54-kwh-156hp-50517
EU-FIAT-600-2023-SUV-02	4178	1779	1525	Fiat 600 official technical sheet	https://www.media.stellantis.com/em-en/download-model-document/208?v=1750066064
EU-FIAT-900-TE-200-MPV-01	3728	1488	1660	Fiat 900T official sales brochure archive	https://autocatalogarchive.com/wp-content/uploads/2016/08/Fiat-900-T-Van-1978-NL.pdf
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/716600/fiat_argenta_1600.html
EU-FIAT-BRAVA-182-HATCHBACK-14-01	4187	1741	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.4-75hp-7112
EU-FIAT-BRAVA-182-HATCHBACK-STANDARD-01	4187	1741	1410	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.2-16v-80-82hp-7111
EU-FIAT-BRAVA-182-HATCHBACK-14-12V-01	4020	1750	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-brava-182-1.4-12v-80hp-7113
EU-FIAT-BRAVO-182-HATCHBACK-STANDARD-01	4025	1755	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-182-1.4-75hp-7183
EU-FIAT-BRAVO-182-HATCHBACK-HGT-01	4031	1755	1420	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-182-2.0-hgt-20v-154hp-7190
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-ii-198-2.0-multijet-165hp-16762
EU-FIAT-CINQUECENTO-170-HATCHBACK-01	3227	1487	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-cinquecento-0.7-31hp-7254
EU-FIAT-CINQUECENTO-170-HATCHBACK-09IE-01	3223	1487	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-cinquecento-0.9-i.e.-s-40hp-7257
EU-FIAT-COUPE-175-COUPE-01	4250	1768	1355	Auto-Data.net	https://www.auto-data.net/en/fiat-coupe-fa-175-2.0-20v-154hp-7278
EU-FIAT-CROMA-I-154-HATCHBACK-01	4520	1760	1435	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-154-generation-1566
EU-FIAT-CROMA-II-194-WAGON-PREFL-01	4756	1775	1597	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-model-745
EU-FIAT-CROMA-II-194-WAGON-FACELIFT-01	4783	1775	1603	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/727745/fiat_croma_1_9_multijet_eco_120_emotion_dpf.html
EU-FIAT-DOBLO-I-223-MPV-PREFL-01	4159	1714	1810	Auto-Data.net	https://www.auto-data.net/en/fiat-doblo-i-223-1.2-8v-65hp-6833
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	4211	1789	1845	Fiat Professional New Doblo Cargo Chassis Cab Euro5 official brochure	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	4561	1789	1845	Fiat Professional New Doblo Cargo Chassis Cab Euro5 official brochure	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_CHASSIS_CAB_EURO5.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	4227	1789	1845	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	4577	1789	1845	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049	Fiat Professional Doblo Work Up official technical brochure	https://www.media.stellantis.com/hu-hu/download-model-document/30
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049	Fiat Professional New Doblo Cargo Technical Specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-01	4253	1722	1818	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/726110/fiat_doblo_1_9_multijet_8v_dynamic.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_4701-4800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.kfz-tech.de/Engl/Hersteller/Fiat/Fiat2421975.htm?utm_source=chatgpt.com "cartecc.com - 1975 Fiat 242"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（136 行）
- 累计尺寸组：dimension_groups_final.tsv（40 行）

