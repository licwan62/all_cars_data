# 任务：all 第 4601-4700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0047__c6a03315


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4601-4700 行

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
all 第 4601-4700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	4721	1841	1495
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-A4-B8-FACELIFT-SEDAN-01	4701	1826	1427
EU-AUDI-A4-B8-FACELIFT-WAGON-01	4699	1826	1436
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383
EU-AUDI-A5-8F7-PREFL-CONVERTIBLE-01	4625	1854	1383
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372
EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	4712	1854	1391
EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	4711	1854	1391
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E30-CONVERTIBLE-2D-01	4325	1645	1370
EU-BMW-3-SERIES-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-BMW-3-SERIES-F30-SEDAN-4D-FACELIFT-01	4633	1811	1429
EU-BMW-3-SERIES-F30-SEDAN-4D-PREFL-01	4624	1811	1429
EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	3941	1728	1524
EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	3941	1728	1538
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674
EU-DACIA-LOGAN-I-PICKUP-2D-01	4499	1735	1554
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-02	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-02	4250	1735	1525
EU-DACIA-LOGAN-I-VAN-5D-01	4450	1740	1636
EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	3546	1627	1488
EU-FIAT-500C-312-CONVERTIBLE-2D-PREFL-01	3546	1627	1488
EU-FIAT-FIORINO-147-VAN-MPV-3D-01	4159	1622	1904
EU-FIAT-FIORINO-III-VAN-MPV-01	3864	1716	1721
EU-FIAT-QUBO-I-MPV-5D-01	3959	1716	1735
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-HATCHBACK-5D-FACELIFT-01	4358	1823	1484
EU-FORD-FOCUS-III-HATCHBACK-5D-PREFL-01	4358	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-4D-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658
EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	4800	1805	1480
EU-KIA-MAGENTIS-II-MG-PREFL-SEDAN-01	4735	1805	1480
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375
EU-MAZDA-323-S-VI-BJ-FACELIFT-SEDAN-4D-01	4390	1705	1410
EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	4435	1765	1465
EU-MAZDA-3-I-BK-FACELIFT-HATCHBACK-5D-01	4415	1755	1465
EU-MAZDA-3-I-BK-FACELIFT-SEDAN-4D-01	4580	1755	1465
EU-MAZDA-3-II-BL-HATCHBACK-5D-FACELIFT-01	4460	1755	1470
EU-MAZDA-3-II-BL-HATCHBACK-5D-PREFL-01	4460	1755	1470
EU-MAZDA-3-II-BL-SEDAN-4D-FACELIFT-01	4580	1755	1470
EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	4580	1755	1470
EU-MAZDA-CX-7-ER-SUV-5D-01	4680	1870	1645
EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	4700	1870	1645
EU-MAZDA-E-SERIES-III-SR2-VAN-LWB-4X4-01	4690	1690	1960
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870
EU-PEUGEOT-407-COUPE-2D-01	4815	1868	1399
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486
EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	4970	1913	1418
EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	3600	1654	1470
EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	3699	1688	1470
EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	3602	1665	1470
EU-RENAULT-TWINGO-II-RS-HATCHBACK-3D-01	3607	1688	1460
EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	4827	1792	1475
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459
EU-SAAB-9-5-PREFL-SEDAN-4D-01	4810	1790	1450
EU-SAAB-9-5-PREFL-WAGON-5D-01	4808	1792	1497
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	4140	1640	1410
EU-VW-POLO-IV-9N2-SEDAN-4D-01	4179	1650	1484
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02	3916	1650	1459
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465
EU-VW-POLO-V-6R-HATCHBACK-3D-01	3970	1682	1453
EU-VW-POLO-V-6R-HATCHBACK-5D-01	3970	1682	1453
EU-VW-SHARAN-I-7M8-PREFL-MPV-01	4620	1810	1730
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	120	163	Mar 2010	Dec 2014	2024-03-01	33347
Ford	S-Max	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	149	203	Mar 2010	Dec 2014	2024-03-01	33348
Ford	Galaxy ii	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	149	203	Mar 2010	Jun 2015	2024-03-01	33349
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	120	163	Mar 2010	Jun 2015	2024-03-01	33350
Ford	Mondeo iv	2.0 Scti	Schrägheck	Frontantrieb	Benzin	149	203	Mar 2010	Jan 2015	2024-03-01	33351
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	120	163	Mar 2010	Jan 2015	2024-03-01	33352
Fiat	500	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	70	95	Dec 2009	-	2024-03-01	33353
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	120	163	Mar 2010	Jan 2015	2024-03-01	33354
Ford	Mondeo iv turnier	2.0 Scti	Kombi	Frontantrieb	Benzin	149	203	Mar 2010	Jan 2015	2024-03-01	33355
Dacia	Logan	1.6 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	64	87	Nov 2008	-	2024-03-01	33356
KIA	K2900	2.9 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	92	125	Jan 2008	-	2024-03-01	33357
KIA	Cerato ii	2	Stufenheck	Frontantrieb	Benzin	115	156	Jan 2009	Jun 2013	2024-05-01	33359
Seat	Altea	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 2009	Dec 2010	2024-05-01	33361
Seat	Altea	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 2009	Dec 2010	2024-03-01	33362
Audi	A3	1.2 Tfsi	Cabriolet	Frontantrieb	Benzin	77	105	Mar 2010	May 2013	2024-03-01	33363
Audi	A4 b8	2.0 Tfsi Flexible Fuel	Stufenheck	Frontantrieb	Benzin/Ethanol	132	180	Nov 2009	Dec 2015	2024-03-01	33365
Audi	A4 b8	2.0 Tfsi Flexible Fuel Quattro	Stufenheck	Allrad	Benzin/Ethanol	132	180	Nov 2009	Dec 2015	2024-03-01	33366
Audi	A4 b8 avant	2.0 Tfsi Flexible Fuel	Kombi	Frontantrieb	Benzin/Ethanol	132	180	Nov 2009	Dec 2015	2024-03-01	33367
Audi	A4 b8 avant	2.0 Tfsi Flexible Fuel Quattro	Kombi	Allrad	Benzin/Ethanol	132	180	Nov 2009	Dec 2015	2024-03-01	33368
KIA	Magentis ii	2	Stufenheck	Frontantrieb	Benzin	121	165	Sep 2009	Dec 2010	2024-03-01	33369
KIA	Magentis ii	2.7 V6	Stufenheck	Frontantrieb	Benzin	142	193	Jul 2009	Dec 2010	2024-03-01	33370
KIA	Magentis ii	2.0 Crdi	Stufenheck	Frontantrieb	Diesel	110	150	Apr 2006	Dec 2010	2024-03-01	33371
Fiat	Qubo	1.4 Natural Power	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	57	78	Oct 2009	-	2024-03-01	33372
Volvo	S80 ii	1.6 D Drive	Stufenheck	Frontantrieb	Diesel	80	109	Jan 2010	Dec 2011	2024-03-01	33373
Volvo	S60 ii	T3	Stufenheck	Frontantrieb	Benzin	110	150	Apr 2010	Dec 2015	2024-03-01	33374
Volvo	S60 ii	T4	Stufenheck	Frontantrieb	Benzin	132	180	Apr 2010	Dec 2015	2024-03-01	33375
Volvo	S60 ii	2.0 T	Stufenheck	Frontantrieb	Benzin	149	203	Apr 2010	Dec 2011	2024-03-01	33376
Volvo	S60 ii	T5	Stufenheck	Frontantrieb	Benzin	177	240	Apr 2010	Dec 2014	2024-03-01	33377
Volvo	S60 ii	T6 AWD	Stufenheck	Allrad	Benzin	224	304	Apr 2010	Dec 2015	2024-03-01	33378
Volvo	S60 ii	D3	Stufenheck	Frontantrieb	Diesel	120	163	Apr 2010	Dec 2014	2024-03-01	33379
Volvo	S60 ii	D5	Stufenheck	Frontantrieb	Diesel	151	205	Apr 2010	Dec 2011	2024-03-01	33380
Volvo	S60 ii	D5 AWD	Stufenheck	Allrad	Diesel	151	205	Apr 2010	Dec 2011	2024-03-01	33381
Volvo	Xc60 i	2.0 T	SUV	Frontantrieb	Benzin	149	203	Dec 2009	Dec 2012	2024-03-01	33382
Volvo	Xc60 i	3.2 AWD	SUV	Allrad	Benzin	179	243	Mar 2010	Dec 2015	2024-03-01	33383
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	224	304	Mar 2010	Feb 2017	2024-03-01	33384
Volvo	Xc60 i	D3 / D4	SUV	Frontantrieb	Diesel	120	163	Mar 2010	Dec 2014	2024-03-01	33385
BMW	3	316 D	Stufenheck	Heckantrieb	Diesel	85	116	Jul 2009	Dec 2011	2024-03-01	33386
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	135	184	Mar 2010	Oct 2011	2024-03-01	33387
BMW	3	320 D Xdrive	Stufenheck	Allrad	Diesel	135	184	Mar 2010	Oct 2011	2024-03-01	33388
BMW	3	320 D	Kombi	Heckantrieb	Diesel	135	184	Mar 2010	May 2012	2024-03-01	33389
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	135	184	Mar 2010	Jun 2012	2024-03-01	33390
BMW	3	320 D Xdrive	Coupe	Allrad	Diesel	135	184	Mar 2010	Jun 2013	2024-03-01	33391
BMW	3	320 D	Coupe	Heckantrieb	Diesel	135	184	Mar 2010	Jun 2013	2024-03-01	33392
BMW	3	320 D	Cabriolet	Heckantrieb	Diesel	135	184	Mar 2010	Oct 2013	2024-03-01	33393
Citroën	C3 ii	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	66	90	Nov 2009	Sep 2016	2024-07-01	33394
Citroën	C3 ii	1.4 HDI 70	Schrägheck	Frontantrieb	Diesel	50	68	Nov 2009	Sep 2016	2024-07-01	33395
BMW	3	325 D	Stufenheck	Heckantrieb	Diesel	150	204	Mar 2010	Oct 2011	2024-03-01	33396
Fiat	Doblo kombi	1.3 D Multijet	Bus	Frontantrieb	Diesel	66	90	Feb 2010	Dec 2023	2025-02-03	33397
Fiat	Doblo kombi	1.4	Bus	Frontantrieb	Benzin	70	95	Feb 2010	Dec 2023	2025-02-03	33398
Fiat	Doblo kombi	1.6 D Multijet	Bus	Frontantrieb	Diesel	77	105	Jan 2010	Dec 2023	2025-02-03	33399
Fiat	Doblo kombi	2.0 D Multijet	Bus	Frontantrieb	Diesel	99	135	Jan 2010	Dec 2023	2025-02-03	33400
Fiat	Doblo cargo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	70	95	Feb 2010	Dec 2023	2025-02-03	33401
Fiat	Doblo cargo	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Feb 2010	Dec 2023	2025-02-03	33402
Fiat	Doblo cargo	1.6 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	100	Feb 2010	Dec 2023	2025-02-03	33403
Fiat	Doblo cargo	2.0 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	99	135	Feb 2010	Dec 2023	2025-02-03	33404
Fiat	Fiorino	1.4 Natural Power	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	57	78	Jun 2008	-	2024-03-01	33405
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	188	256	Jul 2008	Mar 2013	2024-03-01	33406
Audi	A5	2.0 TDI	Coupe	Frontantrieb	Diesel	120	163	Aug 2008	Jan 2017	2024-03-01	33407
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	120	163	Sep 2009	Jan 2017	2024-03-01	33408
Audi	A5	1.8 Tfsi	Schrägheck	Frontantrieb	Benzin	118	160	Nov 2009	Sep 2011	2024-03-01	33409
Audi	A5	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	155	211	Sep 2009	Nov 2013	2024-03-01	33410
Audi	A5	S5 Quattro	Schrägheck	Allrad	Benzin	245	333	Jan 2010	Jan 2017	2024-03-01	33411
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	Sep 2009	Jan 2017	2024-03-01	33412
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	105	143	Sep 2009	Jan 2017	2024-03-01	33413
Audi	A5	2.7 TDI	Schrägheck	Frontantrieb	Diesel	120	163	Sep 2009	Mar 2012	2024-03-01	33414
Audi	A5	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	125	170	Sep 2009	Mar 2012	2024-03-01	33415
Audi	A5	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	118	160	Sep 2009	Mar 2012	2024-03-01	33416
Audi	A4 b8 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	155	211	Jun 2008	May 2010	2024-03-01	33417
Audi	A4 allroad b8	2.0 TDI Quattro	Kombi	Allrad	Diesel	100	136	Sep 2009	May 2016	2024-03-01	33418
Audi	A4 allroad b8	2.0 TDI Quattro	Kombi	Allrad	Diesel	120	163	Apr 2009	May 2016	2024-03-01	33419
Nissan	Teana i	2	Stufenheck	Frontantrieb	Benzin	103	140	Oct 2003	Jun 2008	2024-03-01	33420
Nissan	Teana i	3.5	Stufenheck	Frontantrieb	Benzin	170	231	Oct 2003	Jun 2008	2024-03-01	33422
Peugeot	407	2.0 HDI	Stufenheck	Frontantrieb	Diesel	120	163	Jun 2009	Dec 2010	2024-03-01	33426
Peugeot	407	2.0 HDI	Kombi	Frontantrieb	Diesel	120	163	Jun 2009	Dec 2010	2024-03-01	33427
Audi	A8 d4	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	213	290	Jul 2010	Apr 2014	2024-03-01	33429
Audi	A8 d4	4.2 FSI Quattro	Stufenheck	Allrad	Benzin	273	371	Nov 2009	Dec 2012	2024-03-01	33430
Audi	A8 d4	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	184	250	Jul 2010	Jan 2018	2024-03-01	33431
Audi	A8 d4	4.2 TDI Quattro	Stufenheck	Allrad	Diesel	258	351	Nov 2009	Apr 2014	2024-03-01	33432
VW	Sharan	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	110	150	May 2010	Nov 2015	2024-03-01	33434
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2010	Nov 2015	2024-03-01	33435
Mitsubishi	Asx	1.6 Mivec	SUV	Frontantrieb	Benzin	86	117	Jun 2010	-	2024-03-01	33436
Mitsubishi	Asx	1.8 Di-d	SUV	Frontantrieb	Diesel	110	150	Jun 2010	-	2024-03-01	33437
Mitsubishi	Asx	1.8 Di-d 4WD	SUV	Allrad	Diesel	110	150	Jun 2010	-	2024-03-01	33438
Mazda	3	2.3 MPS Turbo	Schrägheck	Frontantrieb	Benzin	191	260	Dec 2008	Sep 2014	2024-03-01	33440
Mazda	3	2.2 MZR CD	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2009	Sep 2014	2024-03-01	33443
Mazda	3	2.2 MZR CD	Stufenheck	Frontantrieb	Diesel	136	185	Jun 2009	May 2013	2024-03-01	33444
VW	Amarok	2.0 Bitdi	Pick-up	Heckantrieb	Diesel	120	163	Sep 2010	Aug 2012	2024-03-01	33470
VW	Amarok	2.0 Bitdi 4motion	Pick-up	Allrad	Diesel	120	163	Sep 2010	Aug 2012	2024-03-01	33472
Mazda	E	E2200 D	Bus	Heckantrieb	Diesel	47	64	Mar 1991	May 2003	2024-03-01	33475
Mazda	Cx-7	2.3 MZR Disi Turbo AWD	SUV	Allrad	Benzin	175	238	Jun 2006	Dec 2014	2024-03-01	33482
Renault	Twingo	1.2 16V	Schrägheck	Frontantrieb	Benzin	55	75	Mar 2007	Sep 2014	2026-05-01	33486
Mercedes-benz	Clk	CLK AMG DTM	Cabriolet	Heckantrieb	Benzin	428	582	Jun 2004	Oct 2005	2024-03-01	33488
Mitsubishi	Pajero iv	3.8 V6	SUV	Allrad	Benzin	182	248	Oct 2006	-	2024-03-01	33489
VW	Polo	1.4 GTI	Schrägheck	Frontantrieb	Benzin	132	180	May 2010	May 2014	2024-03-01	33491
Porsche	Panamera	3.6	Schrägheck	Heckantrieb	Benzin	220	300	May 2010	Jul 2013	2024-03-01	33492
Porsche	Panamera	3.6 4	Schrägheck	Allrad	Benzin	220	300	May 2010	Jul 2013	2024-03-01	33493
Ford	Focus ii	2.5 RS 500	Schrägheck	Frontantrieb	Benzin	257	350	May 2010	Jul 2011	2024-03-01	33494
Mitsubishi	Lancer vii	2.0 I	Stufenheck	Frontantrieb	Benzin	113	154	Oct 2007	Dec 2013	2024-03-01	33495
Saab	9-5	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	132	180	May 2010	Jan 2012	2024-03-01	33498
Saab	9-5	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	162	220	May 2010	Jan 2012	2024-03-01	33499


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 87 个输入 Ktype 的物理外廓映射，形成 117 条 `READY` 派生映射。
* 复用历史尺寸组 45 个，本轮首次创建尺寸组 15 个，当前已闭合并引用尺寸组共 60 个。
* 已拆分 A4、A5、S60、XC60、C3、ASX、CX-7、Twingo 等改款前后外廓，以及 Amarok 驾驶室、Pajero/Polo 门数分支。
* 暂保留 13 个 `PENDING`：Doblò II 8 个、Audi A8 D4 4 个、Mazda E-Series Bus 1 个。Doblò 官方资料已确认存在标准轴距、Maxi 和高顶组合；A8 官方资料已确认标准轴距与长轴距存在不同长度，但仍需锁定各 Ktype 实际覆盖范围。([Stellantis Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* PENDING Ktype：13
* READY 映射行：117
* PENDING 映射行：13
* 已确认尺寸组：60
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33347	33347	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH		READY
33348	33348	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH		READY
33349	33349	MPV	Galaxy II		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH		READY
33350	33350	MPV	Galaxy II		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH		READY
33351	33351	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH		READY
33352	33352	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH		READY
33353	33353	Hatchback	500 I	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH		READY
33354	33354	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH		READY
33355	33355	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH		READY
33356	33356	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH		READY
33357	33357	Pickup	K2900	PU3	2	EU-KIA-K2900-PU3-PICKUP-2D-01	MEDIUM		READY
33359	33359	Sedan	Cerato II	TD	4	EU-KIA-CERATO-II-TD-SEDAN-4D-01	HIGH		READY
33361	33361	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33362	33362	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33363	33363	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
33365_prefl	33365	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
33365_facelift	33365	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
33366_prefl	33366	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
33366_facelift	33366	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
33367	33367	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33368	33368	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33369	33369	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH		READY
33370	33370	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH		READY
33371_prefl	33371	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-PREFL-SEDAN-01	HIGH	改款前外廓。	READY
33371_facelift	33371	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH	改款后外廓。	READY
33372	33372	MPV	Qubo I	225	5	EU-FIAT-QUBO-I-MPV-5D-01	HIGH		READY
33373	33373	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
33374_prefl	33374	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33374_facelift	33374	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33375_prefl	33375	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33375_facelift	33375	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33376	33376	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33377_prefl	33377	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33377_facelift	33377	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33378_prefl	33378	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33378_facelift	33378	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33379_prefl	33379	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33379_facelift	33379	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33380	33380	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33381	33381	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33382	33382	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH		READY
33383_prefl	33383	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33383_facelift	33383	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33384_prefl	33384	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33384_facelift	33384	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33385_prefl	33385	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33385_facelift	33385	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33386	33386	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33387	33387	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33388	33388	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33389	33389	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH		READY
33390	33390	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH		READY
33391	33391	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
33392	33392	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
33393	33393	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH		READY
33394_phase1	33394	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	第一阶段外廓。	READY
33394_phase2	33394	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	第二阶段外廓。	READY
33395_phase1	33395	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	第一阶段外廓。	READY
33395_phase2	33395	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	第二阶段外廓。	READY
33396	33396	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33397	33397	MPV	Doblò II	263			LOW	需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身。	PENDING: 需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身
33398	33398	MPV	Doblò II	263			LOW	需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身。	PENDING: 需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身
33399	33399	MPV	Doblò II	263			LOW	需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身。	PENDING: 需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身
33400	33400	MPV	Doblò II	263			LOW	需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身。	PENDING: 需确认Ktype是否同时覆盖标准轴距与Maxi乘用车身
33401	33401	Van	Doblò II	263			LOW	需确认Ktype覆盖的SWB/LWB及低顶/高顶组合。	PENDING: 需确认Ktype覆盖的SWB/LWB及低顶/高顶组合
33402	33402	Van	Doblò II	263			LOW	需确认Ktype覆盖的SWB/LWB及低顶/高顶组合。	PENDING: 需确认Ktype覆盖的SWB/LWB及低顶/高顶组合
33403	33403	Van	Doblò II	263			LOW	需确认Ktype覆盖的SWB/LWB及低顶/高顶组合。	PENDING: 需确认Ktype覆盖的SWB/LWB及低顶/高顶组合
33404	33404	Van	Doblò II	263			LOW	需确认Ktype覆盖的SWB/LWB及低顶/高顶组合。	PENDING: 需确认Ktype覆盖的SWB/LWB及低顶/高顶组合
33405	33405	Van	Fiorino III	225		EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH		READY
33406	33406	Hatchback	A3 II	8P	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH		READY
33407_prefl	33407	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	改款前外廓。	READY
33407_facelift	33407	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
33408_prefl	33408	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33408_facelift	33408	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33409	33409	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH		READY
33410_prefl	33410	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33410_facelift	33410	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33411_prefl	33411	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33411_facelift	33411	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33412_prefl	33412	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33412_facelift	33412	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33413_prefl	33413	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33413_facelift	33413	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33414_prefl	33414	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33414_facelift	33414	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33415_prefl	33415	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33415_facelift	33415	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33416_prefl	33416	Convertible	A5 I	8F7	2	EU-AUDI-A5-8F7-PREFL-CONVERTIBLE-01	HIGH	改款前外廓。	READY
33416_facelift	33416	Convertible	A5 I	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	改款后外廓。	READY
33417	33417	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33418	33418	Wagon	A4 Allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
33419	33419	Wagon	A4 Allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
33420	33420	Sedan	Teana I	J31	4	EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	HIGH		READY
33422	33422	Sedan	Teana I	J31	4	EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	HIGH		READY
33426	33426	Sedan	407 I		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH		READY
33427	33427	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH		READY
33429	33429	Sedan	A8 D4	4H			LOW	需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖。	PENDING: 需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖
33430	33430	Sedan	A8 D4	4H			LOW	需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖。	PENDING: 需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖
33431	33431	Sedan	A8 D4	4H			LOW	需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖。	PENDING: 需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖
33432	33432	Sedan	A8 D4	4H			LOW	需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖。	PENDING: 需确认Ktype对标准轴距/长轴距及改款前后分支的覆盖
33434	33434	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33435	33435	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33436_prefl	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	MEDIUM	初期外廓。	READY
33436_facelift2016	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2016-01	MEDIUM	2016改款外廓。	READY
33436_facelift2019	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2019-01	MEDIUM	2019改款外廓。	READY
33437	33437	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	HIGH		READY
33438	33438	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	HIGH		READY
33440	33440	Hatchback	3 II	BL	5	EU-MAZDA-3-II-BL-MPS-HATCHBACK-5D-01	HIGH		READY
33443	33443	Sedan	3 II	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH		READY
33444	33444	Sedan	3 II	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH		READY
33470_singlecab	33470	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	MEDIUM	单排驾驶室外廓。	READY
33470_doublecab	33470	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	MEDIUM	双排驾驶室外廓。	READY
33472_singlecab	33472	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	MEDIUM	单排驾驶室外廓。	READY
33472_doublecab	33472	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	MEDIUM	双排驾驶室外廓。	READY
33475	33475	MPV	E-Series III	SR1			LOW	需确认SR1系列Bus的轴距与车顶分支。	PENDING: 需确认SR1系列Bus的轴距与车顶分支
33482_prefl	33482	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-5D-01	HIGH	改款前外廓。	READY
33482_facelift	33482	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	HIGH	改款后外廓。	READY
33486_prefl	33486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
33486_facelift	33486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	HIGH	改款后外廓。	READY
33488	33488	Convertible	CLK II	A209	2	EU-MERCEDES-BENZ-CLK-A209-DTM-AMG-CONVERTIBLE-2D-01	MEDIUM	DTM AMG特殊宽体外廓。	READY
33489_3dr	33489	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	HIGH	三门短车身。	READY
33489_5dr	33489	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	HIGH	五门长车身。	READY
33491_3dr	33491	Hatchback	Polo V	6R	3	EU-VW-POLO-V-6R-HATCHBACK-3D-01	HIGH	三门外廓。	READY
33491_5dr	33491	Hatchback	Polo V	6R	5	EU-VW-POLO-V-6R-HATCHBACK-5D-01	HIGH	五门外廓。	READY
33492	33492	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
33493	33493	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
33494	33494	Hatchback	Focus II		3	EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	HIGH		READY
33495	33495	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	输入代际名与CY0车身对应关系已校正。	READY
33498	33498	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33499	33499	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-K2900-PU3-PICKUP-2D-01	5120	1740	2035	Kia K2900 official specification sheet	https://www.turnbulls.com.au/kia/brochures/K2900_Spec_Sheet_0408.pdf
EU-KIA-CERATO-II-TD-SEDAN-4D-01	4530	1775	1460	Kia Cerato official specifications brochure	https://xr793.com/wp-content/uploads/2023/04/2010-KIa-Cerato-Specs-AUS.pdf
EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	4628	1865	1484	Volvo 2011 S60 Specifications;CarExpert 2011 Volvo S60 exterior dimensions	https://www.volvoclub.org.uk/pdf/s60/s60_2011_techspecs.pdf;https://www.carexpert.co.nz/volvo/s60/2011/exterior-and-dimensions
EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	4635	1865	1484	Volvo 2014 S60 Specifications;Volvo Support S60 dimensions	https://www.volvoclub.org.uk/pdf/s60/s60_2014_techspecs.pdf;https://www.volvocars.com/uk/support/car/s60/13w46/article/18f7748df78f457dc0a801e800a04011
EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	4644	1891	1713	Volvo Support XC60 dimensions	https://www.volvocars.com/hk/support/car/xc60/14w20/article/18f77489f78f457dc0a801e800a04016
EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	4770	1765	1475	Nissan Heritage Collection Teana 230JK	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/476_teana_230jk.html
EU-VW-SHARAN-II-7N-MPV-5D-01	4854	1904	1720	Volkswagen Sharan II specifications	https://www.cataloge.eu/volkswagen/sharan-2010-7n
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	4295	1770	1615	Automobile-Catalog Mitsubishi ASX 1.8 DI-D 2WD	https://www.automobile-catalog.com/car/2010/2009735/mitsubishi_asx_1_8_di-d_plus_2wd.html
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2016-01	4355	1770	1640	Carfolio Mitsubishi ASX 1.6 ClearTec	https://www.carfolio.com/mitsubishi-asx-1.6-cleartec-531597
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2019-01	4365	1810	1640	VehicleScore Mitsubishi ASX dimensions	https://vehiclescore.co.uk/car-dimensions-check/mitsubishi/asx
EU-MAZDA-3-II-BL-MPS-HATCHBACK-5D-01	4505	1770	1460	CarExpert Mazda 3 MPS exterior dimensions	https://www.carexpert.co.nz/mazda/mazda-3/2009-mps-2-3l-hatchback-fwd-petrol-manual-jog5ggg820090713
EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	5181	1944	1820	Auto-Data Volkswagen Amarok I Single Cab	https://www.auto-data.net/en/volkswagen-amarok-i-single-cab-generation-4341
EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	5254	1944	1834	CarExpert 2011 Volkswagen Amarok exterior dimensions	https://www.carexpert.co.nz/volkswagen/amarok/2011-2l-pickup-rwd-diesel-manual-joww55gs20110110
EU-MERCEDES-BENZ-CLK-A209-DTM-AMG-CONVERTIBLE-2D-01	4650	1800	1360	Automobile-Catalog Mercedes-Benz CLK DTM AMG Cabriolet	https://www.automobile-catalog.com/car/2005/1543895/mercedes-benz_clk_dtm_amg_cabriolet.html
EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	5008	1868	1466	Car and Driver 2010 Saab 9-5 specifications	https://www.caranddriver.com/saab/9-5/specs/2010/saab_9-5_saab-9-5-sedan_2010
```

K2900、Cerato、S60、XC60 和 Teana 的本轮新组三维分别由车型规格册、Volvo 技术资料及 Nissan 历史车型资料闭合。

ASX 三阶段外廓、Mazda 3 MPS 以及 Amarok 单排/双排驾驶室使用各自对应配置的三维记录，未将不同车身配置拼接。([汽车目录][2])

CLK DTM AMG Cabriolet 按特殊宽体独立建组；Saab 9-5 II 使用不含后视镜宽度记录。([汽车目录][3])

## 下一步优先处理

1. 一次性闭合 Doblò II：确认 33397–33400 是否覆盖标准轴距和 Maxi 乘用车身；确认 33401–33404 的 SWB、LWB、低顶和高顶组合。
2. 闭合 Audi A8 D4：按标准轴距/长轴距及改款边界拆分 33429–33432，避免把 5137 mm 与 5267 mm 车身合并。
3. 闭合 Mazda E-Series 33475：确认 SR1 Bus 对应的车长、轴距和车顶高度分支。
4. PENDING 清零后只执行一次表头、主键、外键和来源完整性检查，随后直接生成两张最终文件。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf?utm_source=chatgpt.com "TECHNICAL SPECIFICATIONS AND MAIN EQUIPMENT"
[2]: https://www.automobile-catalog.com/car/2010/2009735/mitsubishi_asx_1_8_di-d_plus_2wd.html?utm_source=chatgpt.com "2010 Mitsubishi ASX 1.8 DI-D Plus 2WD Specs Review ..."
[3]: https://www.automobile-catalog.com/car/2005/1543895/mercedes-benz_clk_dtm_amg_cabriolet.html?utm_source=chatgpt.com "2005 Mercedes-Benz CLK DTM AMG Cabriolet (aut. 5)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4601-4700_ktype_dimension_mapping_final.tsv
- all_4601-4700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已消除上一轮全部 13 个 `PENDING`。
* Doblò II 按 SWB/LWB、低顶/高顶和乘用/货运车身完成拆分；A8 D4 按标准轴距/长轴距和改款前后完成拆分；Mazda E-Series 锁定长轴客车外廓。([Stellantis Media][1])
* 已完成固定表头、主键唯一、外键引用闭合、尺寸与来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* Ktype 映射行：151
* DIMENSION_GROUP：70
* `id` 重复：0
* 孤立尺寸组：0
* 缺失尺寸组引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
33347	33347	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH		READY
33348	33348	MPV	S-Max I		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH		READY
33349	33349	MPV	Galaxy II		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH		READY
33350	33350	MPV	Galaxy II		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH		READY
33351	33351	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH		READY
33352	33352	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH		READY
33353	33353	Hatchback	500 I	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH		READY
33354	33354	Hatchback	Mondeo IV		5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH		READY
33355	33355	Wagon	Mondeo IV		5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH		READY
33356	33356	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH		READY
33357	33357	Pickup	K2900	PU3	2	EU-KIA-K2900-PU3-PICKUP-2D-01	MEDIUM		READY
33359	33359	Sedan	Cerato II	TD	4	EU-KIA-CERATO-II-TD-SEDAN-4D-01	HIGH		READY
33361	33361	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33362	33362	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH		READY
33363	33363	Convertible	A3 II	8P7	2	EU-AUDI-A3-II-CABRIOLET-2D-01	HIGH		READY
33365_prefl	33365	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
33365_facelift	33365	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
33366_prefl	33366	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
33366_facelift	33366	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
33367	33367	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33368	33368	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33369	33369	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH		READY
33370	33370	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH		READY
33371_prefl	33371	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-PREFL-SEDAN-01	HIGH	改款前外廓。	READY
33371_facelift	33371	Sedan	Magentis II	MG	4	EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	HIGH	改款后外廓。	READY
33372	33372	MPV	Qubo I	225	5	EU-FIAT-QUBO-I-MPV-5D-01	HIGH		READY
33373	33373	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
33374_prefl	33374	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33374_facelift	33374	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33375_prefl	33375	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33375_facelift	33375	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33376	33376	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33377_prefl	33377	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33377_facelift	33377	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33378_prefl	33378	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33378_facelift	33378	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33379_prefl	33379	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
33379_facelift	33379	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
33380	33380	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33381	33381	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	HIGH		READY
33382	33382	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH		READY
33383_prefl	33383	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33383_facelift	33383	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33384_prefl	33384	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33384_facelift	33384	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33385_prefl	33385	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	改款前外廓。	READY
33385_facelift	33385	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	HIGH	改款后外廓。	READY
33386	33386	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33387	33387	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33388	33388	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33389	33389	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH		READY
33390	33390	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH		READY
33391	33391	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
33392	33392	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
33393	33393	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH		READY
33394_phase1	33394	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	第一阶段外廓。	READY
33394_phase2	33394	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	第二阶段外廓。	READY
33395_phase1	33395	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	第一阶段外廓。	READY
33395_phase2	33395	Hatchback	C3 II		5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	第二阶段外廓。	READY
33396	33396	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH		READY
33397_swb	33397	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-SWB-01	MEDIUM	标准轴距乘用车身。	READY
33397_lwb	33397	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-LWB-01	MEDIUM	Maxi长轴乘用车身。	READY
33398_swb	33398	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-SWB-01	MEDIUM	标准轴距乘用车身。	READY
33398_lwb	33398	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-LWB-01	MEDIUM	Maxi长轴乘用车身。	READY
33399_swb	33399	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-SWB-01	MEDIUM	标准轴距乘用车身。	READY
33399_lwb	33399	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-LWB-01	MEDIUM	Maxi长轴乘用车身。	READY
33400_swb	33400	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-SWB-01	MEDIUM	标准轴距乘用车身。	READY
33400_lwb	33400	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-LWB-01	MEDIUM	Maxi长轴乘用车身。	READY
33401_swb_lowroof	33401	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距低顶货车。	READY
33401_swb_highroof	33401	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-HIGHROOF-01	MEDIUM	标准轴距高顶货车。	READY
33401_lwb_lowroof	33401	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-LWB-LOWROOF-01	MEDIUM	Maxi长轴低顶货车。	READY
33402_swb_lowroof	33402	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距低顶货车。	READY
33402_lwb_lowroof	33402	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-LWB-LOWROOF-01	MEDIUM	Maxi长轴低顶货车。	READY
33403_swb_lowroof	33403	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距低顶货车。	READY
33403_swb_highroof	33403	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-HIGHROOF-01	MEDIUM	标准轴距高顶货车。	READY
33403_lwb_lowroof	33403	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-LWB-LOWROOF-01	MEDIUM	Maxi长轴低顶货车。	READY
33404_swb_lowroof	33404	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-LOWROOF-01	MEDIUM	标准轴距低顶货车。	READY
33404_swb_highroof	33404	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-SWB-HIGHROOF-01	MEDIUM	标准轴距高顶货车。	READY
33404_lwb_lowroof	33404	Van	Doblò II	263		EU-FIAT-DOBLO-II-263-VAN-LWB-LOWROOF-01	MEDIUM	Maxi长轴低顶货车。	READY
33405	33405	Van	Fiorino III	225		EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH		READY
33406	33406	Hatchback	A3 II	8P	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH		READY
33407_prefl	33407	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	改款前外廓。	READY
33407_facelift	33407	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	改款后外廓。	READY
33408_prefl	33408	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33408_facelift	33408	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33409	33409	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH		READY
33410_prefl	33410	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33410_facelift	33410	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33411_prefl	33411	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33411_facelift	33411	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33412_prefl	33412	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33412_facelift	33412	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33413_prefl	33413	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33413_facelift	33413	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33414_prefl	33414	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33414_facelift	33414	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33415_prefl	33415	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	HIGH	改款前外廓。	READY
33415_facelift	33415	Hatchback	A5 I Sportback	8TA	5	EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	HIGH	改款后外廓。	READY
33416_prefl	33416	Convertible	A5 I	8F7	2	EU-AUDI-A5-8F7-PREFL-CONVERTIBLE-01	HIGH	改款前外廓。	READY
33416_facelift	33416	Convertible	A5 I	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	改款后外廓。	READY
33417	33417	Wagon	A4 B8 Avant	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
33418	33418	Wagon	A4 Allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
33419	33419	Wagon	A4 Allroad B8	8KH	5	EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	HIGH		READY
33420	33420	Sedan	Teana I	J31	4	EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	HIGH		READY
33422	33422	Sedan	Teana I	J31	4	EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	HIGH		READY
33426	33426	Sedan	407 I		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH		READY
33427	33427	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH		READY
33429_swb_prefl	33429	Sedan	A8 D4	4H2	4	EU-AUDI-A8-D4-4H2-SEDAN-PREFL-01	MEDIUM	标准轴距改款前外廓。	READY
33429_lwb_prefl	33429	Sedan	A8 D4	4H8	4	EU-AUDI-A8-D4-4H8-SEDAN-LWB-PREFL-01	MEDIUM	长轴改款前外廓。	READY
33429_swb_facelift	33429	Sedan	A8 D4	4HC	4	EU-AUDI-A8-D4-4HC-SEDAN-FACELIFT-01	MEDIUM	标准轴距改款后外廓。	READY
33429_lwb_facelift	33429	Sedan	A8 D4	4HL	4	EU-AUDI-A8-D4-4HL-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴改款后外廓。	READY
33430_swb_prefl	33430	Sedan	A8 D4	4H2	4	EU-AUDI-A8-D4-4H2-SEDAN-PREFL-01	MEDIUM	标准轴距改款前外廓。	READY
33430_lwb_prefl	33430	Sedan	A8 D4	4H8	4	EU-AUDI-A8-D4-4H8-SEDAN-LWB-PREFL-01	MEDIUM	长轴改款前外廓。	READY
33431_swb_prefl	33431	Sedan	A8 D4	4H2	4	EU-AUDI-A8-D4-4H2-SEDAN-PREFL-01	MEDIUM	标准轴距改款前外廓。	READY
33431_lwb_prefl	33431	Sedan	A8 D4	4H8	4	EU-AUDI-A8-D4-4H8-SEDAN-LWB-PREFL-01	MEDIUM	长轴改款前外廓。	READY
33431_swb_facelift	33431	Sedan	A8 D4	4HC	4	EU-AUDI-A8-D4-4HC-SEDAN-FACELIFT-01	MEDIUM	标准轴距改款后外廓。	READY
33431_lwb_facelift	33431	Sedan	A8 D4	4HL	4	EU-AUDI-A8-D4-4HL-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴改款后外廓。	READY
33432_swb_prefl	33432	Sedan	A8 D4	4H2	4	EU-AUDI-A8-D4-4H2-SEDAN-PREFL-01	MEDIUM	标准轴距改款前外廓。	READY
33432_lwb_prefl	33432	Sedan	A8 D4	4H8	4	EU-AUDI-A8-D4-4H8-SEDAN-LWB-PREFL-01	MEDIUM	长轴改款前外廓。	READY
33432_swb_facelift	33432	Sedan	A8 D4	4HC	4	EU-AUDI-A8-D4-4HC-SEDAN-FACELIFT-01	MEDIUM	标准轴距改款后外廓。	READY
33432_lwb_facelift	33432	Sedan	A8 D4	4HL	4	EU-AUDI-A8-D4-4HL-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴改款后外廓。	READY
33434	33434	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33435	33435	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-5D-01	HIGH		READY
33436_prefl	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	MEDIUM	初期外廓。	READY
33436_facelift2016	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2016-01	MEDIUM	2016改款外廓。	READY
33436_facelift2019	33436	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2019-01	MEDIUM	2019改款外廓。	READY
33437	33437	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	HIGH		READY
33438	33438	SUV	ASX I	GA0W	5	EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	HIGH		READY
33440	33440	Hatchback	3 II	BL	5	EU-MAZDA-3-II-BL-MPS-HATCHBACK-5D-01	HIGH		READY
33443	33443	Sedan	3 II	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH		READY
33444	33444	Sedan	3 II	BL	4	EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	HIGH		READY
33470_singlecab	33470	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	MEDIUM	单排驾驶室外廓。	READY
33470_doublecab	33470	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	MEDIUM	双排驾驶室外廓。	READY
33472_singlecab	33472	Pickup	Amarok I	2H	2	EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	MEDIUM	单排驾驶室外廓。	READY
33472_doublecab	33472	Pickup	Amarok I	2H	4	EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	MEDIUM	双排驾驶室外廓。	READY
33475	33475	MPV	E-Series III	SR1	4	EU-MAZDA-E-SERIES-III-SR1-BUS-LWB-01	MEDIUM	长轴客车外廓。	READY
33482_prefl	33482	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-5D-01	HIGH	改款前外廓。	READY
33482_facelift	33482	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	HIGH	改款后外廓。	READY
33486_prefl	33486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
33486_facelift	33486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	HIGH	改款后外廓。	READY
33488	33488	Convertible	CLK II	A209	2	EU-MERCEDES-BENZ-CLK-A209-DTM-AMG-CONVERTIBLE-2D-01	MEDIUM	DTM AMG特殊宽体外廓。	READY
33489_3dr	33489	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	HIGH	三门短车身。	READY
33489_5dr	33489	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	HIGH	五门长车身。	READY
33491_3dr	33491	Hatchback	Polo V	6R	3	EU-VW-POLO-V-6R-HATCHBACK-3D-01	HIGH	三门外廓。	READY
33491_5dr	33491	Hatchback	Polo V	6R	5	EU-VW-POLO-V-6R-HATCHBACK-5D-01	HIGH	五门外廓。	READY
33492	33492	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
33493	33493	Hatchback	Panamera I	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
33494	33494	Hatchback	Focus II		3	EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	HIGH		READY
33495	33495	Sedan	Lancer VIII	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	输入代际名与CY0车身对应关系已校正。	READY
33498	33498	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
33499	33499	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4601-4700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Automobile-Catalog 2010 Ford S-Max specifications	https://www.automobile-catalog.com/car/2010/1234850/ford_s-max_2_0_titanium.html
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758	Auto-Data Ford Galaxy II facelift	https://www.auto-data.net/en/ford-galaxy-ii-facelift-2010-2.0-ecoboost-203hp-powershift-51879
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Auto-Data Ford Mondeo IV facelift	https://www.auto-data.net/en/ford-mondeo-iv-hatchback-facelift-2010-generation-4060
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Auto-Data Ford Mondeo IV Turnier facelift	https://www.auto-data.net/en/ford-mondeo-iv-turnier-facelift-2010-generation-4062
EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	3546	1627	1488	Auto-Data Fiat 500 (312)	https://www.auto-data.net/en/fiat-500-312-1.3-multijet-16v-75hp-16750
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-generation-8968
EU-KIA-K2900-PU3-PICKUP-2D-01	5120	1740	2035	Kia K2900 official specification sheet	https://www.turnbulls.com.au/kia/brochures/K2900_Spec_Sheet_0408.pdf
EU-KIA-CERATO-II-TD-SEDAN-4D-01	4530	1775	1460	Kia Cerato official specifications brochure	https://xr793.com/wp-content/uploads/2023/04/2010-KIa-Cerato-Specs-AUS.pdf
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Auto-Data Seat Altea facelift	https://www.auto-data.net/en/seat-altea-facelift-2009-generation-4202
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424	Auto-Data Audi A3 Cabriolet 8P facelift	https://www.auto-data.net/en/audi-a3-cabriolet-8p-facelift-2008-generation-1068
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Auto-Data Audi A4 B8 sedan	https://www.auto-data.net/en/audi-a4-b8-8k-generation-1084
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Auto-Data Audi A4 B8 facelift sedan	https://www.auto-data.net/en/audi-a4-b8-8k-facelift-2011-2.0-tfsi-225hp-18837
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8	https://www.auto-data.net/en/audi-a4-avant-b8-8k-generation-1085
EU-KIA-MAGENTIS-II-MG-FACELIFT-SEDAN-01	4800	1805	1480	Auto-Data Kia Magentis II facelift	https://www.auto-data.net/en/kia-magentis-ii-facelift-2008-generation-590
EU-KIA-MAGENTIS-II-MG-PREFL-SEDAN-01	4735	1805	1480	Auto-Data Kia Magentis II	https://www.auto-data.net/en/kia-magentis-ii-2.0-crdi-140hp-2646
EU-FIAT-QUBO-I-MPV-5D-01	3959	1716	1735	Auto-Data Fiat Qubo	https://www.auto-data.net/en/fiat-qubo-generation-3984
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II facelift	https://www.auto-data.net/en/volvo-s80-ii-facelift-2009-generation-4270
EU-VOLVO-S60-II-SEDAN-4D-PREFL-01	4628	1865	1484	Volvo 2011 S60 Specifications;CarExpert 2011 Volvo S60 exterior dimensions	https://www.volvoclub.org.uk/pdf/s60/s60_2011_techspecs.pdf;https://www.carexpert.co.nz/volvo/s60/2011/exterior-and-dimensions
EU-VOLVO-S60-II-SEDAN-4D-FACELIFT-01	4635	1865	1484	Volvo 2014 S60 Specifications;Volvo Support S60 dimensions	https://www.volvoclub.org.uk/pdf/s60/s60_2014_techspecs.pdf;https://www.volvocars.com/uk/support/car/s60/13w46/article/18f7748df78f457dc0a801e800a04011
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713	Auto-Data Volvo XC60 I	https://www.auto-data.net/en/volvo-xc60-i-3.2-238hp-awd-geartronic-17159
EU-VOLVO-XC60-I-SUV-5D-FACELIFT-01	4644	1891	1713	Volvo Support XC60 dimensions	https://www.volvocars.com/hk/support/car/xc60/14w20/article/18f77489f78f457dc0a801e800a04016
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	Auto-Data BMW 3 Series Sedan E90 LCI	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-generation-5304
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-generation-4365
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data BMW 3 Series Coupe E92 LCI	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-generation-4363
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	Auto-Data BMW 3 Series Convertible E93 LCI	https://www.auto-data.net/en/bmw-3-series-convertible-e93-lci-facelift-2010-320d-184hp-17751
EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	3941	1728	1524	Auto-Data Citroen C3 II Phase I	https://www.auto-data.net/en/citroen-c3-ii-phase-i-2009-generation-3323
EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	3941	1728	1538	Auto-Data Citroen C3 II Phase II	https://www.auto-data.net/en/citroen-c3-ii-phase-ii-2013-generation-4397
EU-FIAT-DOBLO-II-263-MPV-SWB-01	4390	1832	1845	Fiat Professional Doblò Cargo official press pack	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-MPV-LWB-01	4740	1832	1880	Fiat Professional Doblò Cargo official press pack	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-VAN-SWB-LOWROOF-01	4390	1832	1845	Fiat Professional Doblò Cargo official press pack	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-VAN-SWB-HIGHROOF-01	4390	1832	2100	Fiat Professional Doblò Cargo official press pack	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-VAN-LWB-LOWROOF-01	4740	1832	1880	Fiat Professional Doblò Cargo official press pack	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-FIORINO-III-VAN-MPV-01	3864	1716	1721	Auto-Data Fiat Fiorino	https://www.auto-data.net/en/fiat-fiorino-model-760
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-generation-5194
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372	Auto-Data Audi A5 Coupe 8T3	https://www.auto-data.net/en/audi-a5-coupe-8t3-generation-1096
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372	Auto-Data Audi A5 Coupe 8T3 facelift	https://www.auto-data.net/en/audi-a5-coupe-8t3-facelift-2011-generation-4152
EU-AUDI-A5-8TA-SPORTBACK-PREFL-01	4711	1854	1391	Auto-Data Audi A5 Sportback 8TA	https://www.auto-data.net/en/audi-a5-sportback-8ta-generation-1095
EU-AUDI-A5-8TA-SPORTBACK-FACELIFT-01	4712	1854	1391	Auto-Data Audi A5 Sportback 8TA facelift	https://www.auto-data.net/en/audi-a5-sportback-8ta-facelift-2011-2.0-tfsi-225hp-19056
EU-AUDI-A5-8F7-PREFL-CONVERTIBLE-01	4625	1854	1383	Auto-Data Audi A5 Cabriolet 8F7	https://www.auto-data.net/en/audi-a5-cabriolet-8f7-generation-1097
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383	Auto-Data Audi A5 Cabriolet 8F7 facelift	https://www.auto-data.net/en/audi-a5-cabriolet-8f7-facelift-2011-generation-4154
EU-AUDI-A4-ALLROAD-B8-8KH-WAGON-5D-01	4721	1841	1495	Auto-Data Audi A4 allroad B8	https://www.auto-data.net/en/audi-a4-allroad-b8-8k-generation-1082
EU-NISSAN-TEANA-I-J31-SEDAN-4D-01	4770	1765	1475	Nissan Heritage Collection Teana 230JK	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/476_teana_230jk.html
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442	Auto-Data Peugeot 407 Phase II	https://www.auto-data.net/en/peugeot-407-phase-ii-2008-2.0-hdi-163hp-automatic-57047
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460	Auto-Data Peugeot 407 SW Phase II	https://www.auto-data.net/en/peugeot-407-model-574
EU-AUDI-A8-D4-4H2-SEDAN-PREFL-01	5137	1949	1460	Audi A8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/19785-AudiUK00000115A8PriceandSpecification.pdf
EU-AUDI-A8-D4-4H8-SEDAN-LWB-PREFL-01	5267	1949	1471	Audi A8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/19785-AudiUK00000115A8PriceandSpecification.pdf
EU-AUDI-A8-D4-4HC-SEDAN-FACELIFT-01	5135	1949	1460	Audi A8 and S8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/19787-AudiUK00000380AudiA8andS8Pricingand.pdf
EU-AUDI-A8-D4-4HL-SEDAN-LWB-FACELIFT-01	5265	1949	1471	Audi A8 and S8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/19787-AudiUK00000380AudiA8andS8Pricingand.pdf
EU-VW-SHARAN-II-7N-MPV-5D-01	4854	1904	1720	Volkswagen Sharan II specifications	https://www.cataloge.eu/volkswagen/sharan-2010-7n
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-PREFL-01	4295	1770	1615	Automobile-Catalog Mitsubishi ASX 1.8 DI-D 2WD	https://www.automobile-catalog.com/car/2010/2009735/mitsubishi_asx_1_8_di-d_plus_2wd.html
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2016-01	4355	1770	1640	Carfolio Mitsubishi ASX 1.6 ClearTec	https://www.carfolio.com/mitsubishi-asx-1.6-cleartec-531597
EU-MITSUBISHI-ASX-I-GA0W-SUV-5D-FACELIFT-2019-01	4365	1810	1640	VehicleScore Mitsubishi ASX dimensions	https://vehiclescore.co.uk/car-dimensions-check/mitsubishi/asx
EU-MAZDA-3-II-BL-MPS-HATCHBACK-5D-01	4505	1770	1460	CarExpert Mazda 3 MPS exterior dimensions	https://www.carexpert.co.nz/mazda/mazda-3/2009-mps-2-3l-hatchback-fwd-petrol-manual-jog5ggg820090713
EU-MAZDA-3-II-BL-SEDAN-4D-PREFL-01	4580	1755	1470	Auto-Data Mazda 3 II Sedan BL	https://www.auto-data.net/en/mazda-3-ii-sedan-bl-generation-3889
EU-VW-AMAROK-I-PICKUP-SINGLECAB-2D-01	5181	1944	1820	Auto-Data Volkswagen Amarok I Single Cab	https://www.auto-data.net/en/volkswagen-amarok-i-single-cab-generation-4341
EU-VW-AMAROK-I-PICKUP-DOUBLECAB-4D-01	5254	1944	1834	CarExpert 2011 Volkswagen Amarok exterior dimensions	https://www.carexpert.co.nz/volkswagen/amarok/2011-2l-pickup-rwd-diesel-manual-joww55gs20110110
EU-MAZDA-E-SERIES-III-SR1-BUS-LWB-01	4915	1690	1970	CarsGuide 1991 Mazda E2200 dimensions	https://www.carsguide.com.au/mazda/e2200/car-dimensions/1991
EU-MAZDA-CX-7-ER-SUV-5D-01	4680	1870	1645	Automobile-Catalog 2007 Mazda CX-7 specifications	https://www.automobile-catalog.com/car/2007/1691615/mazda_cx-7.html
EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	4700	1870	1645	Automobile-Catalog 2010 Mazda CX-7 specifications	https://www.automobile-catalog.com/car/2010/1691645/mazda_cx-7_2_2_mzr-cd.html
EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	3602	1665	1470	Auto-Data Renault Twingo II	https://www.auto-data.net/en/renault-twingo-ii-1.2-16v-76hp-10690
EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	3699	1688	1470	Auto-Data Renault Twingo II facelift	https://www.auto-data.net/en/renault-twingo-ii-facelift-2011-generation-3870
EU-MERCEDES-BENZ-CLK-A209-DTM-AMG-CONVERTIBLE-2D-01	4650	1800	1360	Automobile-Catalog Mercedes-Benz CLK DTM AMG Cabriolet	https://www.automobile-catalog.com/car/2005/1543895/mercedes-benz_clk_dtm_amg_cabriolet.html
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV 3-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-3-doors-15485
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870	Auto-Data Mitsubishi Pajero IV 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-5-doors-15486
EU-VW-POLO-V-6R-HATCHBACK-3D-01	3970	1682	1453	Auto-Data Volkswagen Polo V 3-door	https://www.auto-data.net/en/volkswagen-polo-v-3-door-1.2-70hp-8404
EU-VW-POLO-V-6R-HATCHBACK-5D-01	3970	1682	1453	Auto-Data Volkswagen Polo V 5-door	https://www.auto-data.net/en/volkswagen-polo-v-5-door-1.2-tsi-105hp-16812
EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	4970	1913	1418	Auto-Data Porsche Panamera G1	https://www.auto-data.net/en/porsche-panamera-g1-4s-4.8-v8-400hp-pdk-6728
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484	Auto-Data Ford Focus II Hatchback RS	https://www.auto-data.net/en/ford-focus-ii-hatchback-rs-2.5-305hp-7326
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog Mitsubishi Lancer VIII	https://www.automobile-catalog.com/car/2013/1996400/mitsubishi_lancer_1_8_di-d_plus_cleartec_invite.html
EU-SAAB-9-5-II-YS3G-SEDAN-4D-01	5008	1868	1466	Car and Driver 2010 Saab 9-5 specifications	https://www.caranddriver.com/saab/9-5/specs/2010/saab_9-5_saab-9-5-sedan_2010
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4601-4700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf "Doblo Press Pack for CD.indd"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（7566 行）
- 累计尺寸组：dimension_groups_final.tsv（2920 行）

