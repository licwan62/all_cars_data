# 任务：all 第 4301-4400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0044__c94b717a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4301-4400 行

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
all 第 4301-4400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-DAIHATSU-CUORE-III-L201-HATCHBACK-3D-01	3295	1395	1410
EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	3200	1400	1410
EU-MAZDA-E-SERIES-III-SR1-MPV-01	4965	1690	1955
EU-MAZDA-E-SERIES-III-SR2-VAN-01	4690	1690	1960
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650
EU-NISSAN-PRAIRIE-M11-MPV-5D-01	4350	1690	1625
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630
EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	4230	1665	1685
EU-NISSAN-SUNNY-B11-COUPE-3D-01	4135	1620	1355
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385
EU-NISSAN-SUNNY-B11-WAGON-5D-01	4255	1620	1360
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370
EU-NISSAN-SUNNY-B310-WAGON-5D-01	4050	1590	1390
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-02	4215	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4215	1640	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420
EU-SUBARU-SVX-CX-COUPE-2D-01	4625	1777	1300
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	3585	1530	1350
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	3770	1545	1350
EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Subaru	Impreza station wagon	1.8 I AWD	Kombi	Allrad	Benzin	76	103	Aug 1992	Dec 2000	2024-03-01	4438
Suzuki	Swift i	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Oct 1984	Mar 1989	2024-03-01	4439
Suzuki	Swift i	1.3	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1984	Mar 1989	2024-03-01	4440
Subaru	Impreza	2.0 Turbo GT AWD	Stufenheck	Allrad	Benzin	155	211	Mar 1994	Dec 2000	2024-03-01	4441
Subaru	Impreza station wagon	2.0 I Turbo AWD	Kombi	Allrad	Benzin	155	211	Mar 1994	Dec 2000	2024-03-01	4442
Subaru	Legacy ii	2.0 I	Stufenheck	Frontantrieb	Benzin	85	116	Sep 1994	Mar 1999	2024-03-01	4443
Subaru	Legacy ii	2.0 I 4WD	Stufenheck	Allrad	Benzin	85	116	Sep 1994	Mar 1999	2024-03-01	4444
Subaru	Legacy ii	2.2 I 4WD	Stufenheck	Allrad	Benzin	94	128	Sep 1994	Mar 1999	2024-03-01	4445
Subaru	Legacy ii station wagon	2.0 I	Kombi	Frontantrieb	Benzin	85	116	Sep 1994	Nov 1998	2024-03-01	4446
Subaru	Legacy ii station wagon	2.0 I 4WD	Kombi	Allrad	Benzin	85	116	Sep 1994	Nov 1998	2024-03-01	4447
Subaru	Legacy ii station wagon	2.2 I 4WD	Kombi	Allrad	Benzin	94	128	Feb 1994	Dec 1998	2024-03-01	4448
Subaru	Svx	3.3 I 24V 4WD	Coupe	Allrad	Benzin	162	220	Sep 1994	Dec 1997	2024-03-01	4449
Suzuki	Swift ii	1	Schrägheck	Frontantrieb	Benzin	37	50	Mar 1989	May 2001	2024-03-01	4450
Suzuki	Swift ii	1.0 I	Schrägheck	Frontantrieb	Benzin	39	53	Jan 1995	Dec 2005	2024-03-01	4451
Suzuki	Swift ii	1.0 I	Schrägheck	Frontantrieb	Benzin	40	54	Mar 1989	Dec 1991	2024-03-01	4452
Suzuki	Swift ii	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Mar 1989	May 2001	2024-03-01	4453
Suzuki	Swift ii	1.3	Stufenheck	Frontantrieb	Benzin	50	68	Jan 1991	Dec 1995	2024-03-01	4454
Suzuki	Swift ii	1.3 4WD	Schrägheck	Allrad	Benzin	50	68	Mar 1989	May 2001	2024-03-01	4455
Suzuki	Swift	1.3 I	Cabriolet	Frontantrieb	Benzin	50	68	Sep 1991	Oct 1996	2024-03-01	4456
Suzuki	Swift ii	1.3 4WD	Schrägheck	Allrad	Benzin	52	71	Oct 1989	Dec 1991	2024-03-01	4459
Suzuki	Swift ii	1.3 GTI	Schrägheck	Frontantrieb	Benzin	74	101	Mar 1989	May 2001	2024-03-01	4460
Isuzu	Gemini	1.5 D	Stufenheck	Frontantrieb	Diesel	37	50	Feb 1988	Dec 1989	2024-03-01	4461
Suzuki	Swift ii	1.6 I	Stufenheck	Frontantrieb	Benzin	68	92	Jan 1990	May 2001	2024-03-01	4462
Isuzu	Gemini	1.5 TD	Stufenheck	Frontantrieb	Diesel	49	67	Feb 1988	Dec 1989	2024-03-01	4463
Isuzu	Gemini	1.5 D	Schrägheck	Frontantrieb	Diesel	37	50	Feb 1988	Dec 1990	2024-03-01	4464
Suzuki	Swift ii	1.6 I 4WD	Stufenheck	Allrad	Benzin	68	92	Jan 1990	May 2001	2024-03-01	4465
Suzuki	Swift ii	1.6	Stufenheck	Frontantrieb	Benzin	70	95	Nov 1989	Dec 1991	2024-03-01	4466
Suzuki	Swift ii	1.6 4WD	Stufenheck	Allrad	Benzin	70	95	Nov 1989	Dec 1991	2024-03-01	4467
Isuzu	Gemini	1.5 TD	Schrägheck	Frontantrieb	Diesel	49	67	Feb 1988	Dec 1990	2024-03-01	4468
Isuzu	Gemini	1.6 GTI 16V	Schrägheck	Frontantrieb	Benzin	84	114	Aug 1988	Dec 1990	2024-03-01	4469
Suzuki	Lj80	0.8	Geländewagen offen	Allrad	Benzin	29	39	Jan 1980	Jan 1984	2024-03-01	4470
Nissan	X-Trail ii	2.0 DCI	SUV	Frontantrieb	Diesel	110	150	Jun 2007	Nov 2013	2024-03-01	4471
Isuzu	Trooper i	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	71	97	Oct 1987	Dec 1991	2024-03-01	4472
Isuzu	Trooper i	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	78	106	Oct 1988	Dec 1991	2024-03-01	4473
Isuzu	Trooper i	2.3	Geländewagen offen	Allrad	Benzin	66	90	Nov 1985	Dec 1991	2024-03-01	4474
Isuzu	Trooper i	2.6 I	Geländewagen offen	Allrad	Benzin	85	116	Oct 1987	Dec 1991	2024-03-01	4475
Isuzu	Trooper i	2.2 TD	Geländewagen offen	Allrad	Diesel	53	72	Mar 1984	Dec 1991	2024-03-01	4476
Suzuki	Sj410	1	Geländewagen offen	Allrad	Benzin	33	45	Sep 1981	Jul 1991	2024-03-01	4477
Suzuki	Sj410	1	Geländewagen geschlossen	Allrad	Benzin	33	45	Sep 1981	Dec 1988	2024-03-01	4478
Suzuki	Samurai	1.0 Allrad	Geländewagen geschlossen	Allrad	Benzin	33	45	Nov 1988	Dec 2004	2024-03-01	4479
Suzuki	Samurai	1.3 Allrad	Geländewagen geschlossen	Allrad	Benzin	51	70	Nov 1988	Dec 2004	2024-03-01	4480
BMW	6	M6	Coupe	Heckantrieb	Benzin	412	560	Jul 2012	Oct 2017	2024-03-01	4481
Suzuki	Samurai	1.3 Allrad	Geländewagen geschlossen	Allrad	Benzin	44	60	Nov 1988	Dec 2004	2024-03-01	4482
Suzuki	Samurai	1.3 Allrad	Geländewagen geschlossen	Allrad	Benzin	47	64	Nov 1988	Dec 2004	2024-03-01	4483
Alfa Romeo	8c	4.7	Coupe	Heckantrieb	Benzin	331	450	Jan 2007	Oct 2009	2024-03-01	4484
Suzuki	Sj413	1.3	Geländewagen geschlossen	Allrad	Benzin	44	60	Aug 1986	Aug 1990	2024-03-01	4485
Suzuki	Sj413	1.3	Geländewagen geschlossen	Allrad	Benzin	47	64	Sep 1984	Aug 1990	2024-03-01	4486
Isuzu	Midi	2	Bus	Heckantrieb	Benzin	61	83	Jun 1988	Aug 1992	2024-03-01	4487
Isuzu	Midi	2.0 4WD	Bus	Allrad	Benzin	61	83	Jun 1988	Aug 1992	2024-03-01	4488
Isuzu	Midi	2.0 TD	Bus	Heckantrieb	Diesel	51	69	Jan 1989	Aug 1992	2024-03-01	4489
Isuzu	Midi	2.2 D	Bus	Heckantrieb	Diesel	45	61	Jun 1988	Aug 1992	2024-03-01	4490
Isuzu	Midi	2.2 D 4WD	Bus	Allrad	Diesel	45	61	Jun 1988	Aug 1992	2024-03-01	4491
Isuzu	Midi	2.4 D	Bus	Heckantrieb	Diesel	56	76	Jan 1994	Jul 1996	2024-03-01	4492
Suzuki	Vitara	1.6	Geländewagen offen	Allrad	Benzin	59	80	Jul 1988	Jan 1995	2024-03-01	4493
Isuzu	Midi	2	Kasten	Heckantrieb	Benzin	61	83	Jun 1988	Aug 1992	2024-03-01	4494
Isuzu	Midi	2.0 4WD	Kasten	Allrad	Benzin	61	83	Jun 1988	Aug 1992	2024-03-01	4495
Suzuki	Vitara	1.6 Allrad	Geländewagen geschlossen	Allrad	Benzin	59	80	Jul 1988	Mar 1998	2024-03-01	4496
Isuzu	Midi	2.0 TD	Kasten	Heckantrieb	Diesel	51	69	Jan 1989	Aug 1992	2024-03-01	4497
Isuzu	Midi	2.2 D	Kasten	Heckantrieb	Diesel	45	61	Jun 1988	Aug 1992	2024-03-01	4498
Mazda	E	E2000	Pritsche/Fahrgestell	Heckantrieb	Benzin	60	82	Oct 1989	May 1995	2024-03-01	4499
Isuzu	Midi	2.2 D 4WD	Kasten	Allrad	Diesel	45	61	Jun 1988	Aug 1992	2024-03-01	4500
Isuzu	Midi	2.4 TD	Kasten	Heckantrieb	Diesel	56	76	Jan 1994	Jul 1996	2024-03-01	4501
VW	Golf plus v	1.6 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	75	102	May 2009	Dec 2013	2024-03-01	4502
Alfa Romeo	8c	4.7	Cabriolet	Heckantrieb	Benzin	331	450	Jan 2008	Oct 2010	2024-03-01	4503
Mazda	E	E2000	Pritsche/Fahrgestell	Heckantrieb	Benzin	63	86	Nov 1988	Sep 1989	2024-03-01	4504
Suzuki	Vitara	1.6 Allrad	Geländewagen geschlossen	Allrad	Benzin	60	82	Jul 1988	Dec 1995	2024-03-01	4505
Suzuki	Vitara	1.6 I 16V Allrad	Geländewagen geschlossen	Allrad	Benzin	71	97	Jul 1990	Mar 1998	2024-03-01	4506
Suzuki	Carry	0.8	Kasten	Heckantrieb	Benzin	27	37	Nov 1980	Oct 1985	2024-03-01	4507
Suzuki	Super carry	1	Bus	Heckantrieb	Benzin	31	42	Oct 1992	Mar 1999	2024-03-01	4508
Suzuki	Super carry	1	Bus	Heckantrieb	Benzin	33	45	Oct 1985	Mar 1999	2024-03-01	4509
Suzuki	Vitara	1.6 I 16V	Geländewagen offen	Allrad	Benzin	71	97	Jul 1990	Mar 1999	2024-03-01	4510
Mazda	E	E2000	Pritsche/Fahrgestell	Heckantrieb	Benzin	65	88	Jan 1983	Jul 1991	2024-03-01	4511
Suzuki	Super carry	1	Bus	Heckantrieb	Benzin	30	41	Sep 1994	Mar 1999	2024-03-01	4512
Suzuki	Alto iv	1	Schrägheck	Frontantrieb	Benzin	39	53	Sep 1994	Jun 2002	2024-03-01	4513
BMW	6	640 D Xdrive	Coupe	Allrad	Diesel	230	313	Mar 2012	Oct 2017	2024-03-01	4514
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	155	211	Sep 2011	Oct 2016	2024-03-01	4515
Nissan	Prairie	2.0 I 4X4	Großraumlimousine	Allrad	Benzin	72	98	Oct 1988	Dec 1992	2024-03-01	4516
Nissan	Sunny	2.0 Gti-r 4X4	Schrägheck	Allrad	Benzin	162	220	Oct 1990	May 1995	2024-03-01	4517
Daihatsu	Cuore ii	0.8 4WD	Schrägheck	Allrad	Benzin	32	44	Sep 1986	Oct 1988	2024-03-01	4518
Chrysler	Le baron	2.2 I	Stufenheck	Frontantrieb	Benzin	69	94	Sep 1989	Dec 1994	2024-03-01	4519
Chrysler	Le baron	2.2 I Turbo	Stufenheck	Frontantrieb	Benzin	130	177	Sep 1989	Jan 1991	2024-03-01	4520
Chrysler	Le baron	2.5 I	Stufenheck	Frontantrieb	Benzin	75	101	Jan 1989	Dec 1994	2024-03-01	4521
Chrysler	Le baron	3.0 I V6	Stufenheck	Frontantrieb	Benzin	105	143	Jan 1990	Dec 1994	2024-03-01	4523
Chrysler	Le baron	2.2 I Turbo	Cabriolet	Frontantrieb	Benzin	109	148	Sep 1986	Dec 1990	2024-03-01	4524
Chrysler	Le baron	2.2 I Turbo	Cabriolet	Frontantrieb	Benzin	130	177	Sep 1986	Dec 1990	2024-03-01	4525
Chrysler	Le baron	2.5 I	Cabriolet	Frontantrieb	Benzin	75	101	Sep 1986	Dec 1993	2024-03-01	4526
Chrysler	Le baron	2.5 I Turbo	Cabriolet	Frontantrieb	Benzin	112	152	Jan 1989	Dec 1993	2024-03-01	4527
Chrysler	Le baron	3.0 I V6	Cabriolet	Frontantrieb	Benzin	105	143	Jan 1990	Dec 1996	2024-03-01	4528
Jeep	Wrangler i	2.5	Geländewagen offen	Allrad	Benzin	76	103	Jan 1988	Dec 1991	2024-03-01	4529
Jeep	Wrangler i	2.5	Geländewagen offen	Allrad	Benzin	89	121	Dec 1991	Aug 1996	2024-03-01	4530
Jeep	Wrangler i	4	Geländewagen offen	Allrad	Benzin	131	178	Dec 1991	Aug 1996	2024-03-01	4531
Mazda	E	E2000	Pritsche/Fahrgestell	Heckantrieb	Benzin	71	97	Jan 1991	Aug 1998	2024-03-01	4532
Ford	Maverick	2.4 I	SUV	Allrad	Benzin	91	124	Feb 1993	Aug 1996	2024-03-01	4533
Ford	Maverick	2.7 TD	SUV	Allrad	Diesel	74	100	Feb 1993	Aug 1996	2024-03-01	4534
VW	Golf vi	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Oct 2008	Nov 2012	2024-03-01	4535
VW	Golf plus v	1.6 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2009	Dec 2013	2024-03-01	4536
Hyundai	Accent i	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1994	Jan 2000	2024-03-01	4537
Hyundai	Accent i	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1994	Jan 2000	2024-03-01	4538
Hyundai	Accent i	1.3 I 12V	Schrägheck	Frontantrieb	Benzin	62	84	Oct 1994	Jan 2000	2024-03-01	4539
Hyundai	Accent i	1.5 I 12V	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1994	Jan 2000	2024-03-01	4540


--- Round 1 / 首次发送 ---
## 更新点

* 完成 Subaru Impreza I、Legacy II、SVX 聚类：Impreza 普通旅行版、Turbo 旅行版分别关联不同高度尺寸组；Legacy II 按 BD 三厢与 BG 旅行版分组。([汽车数据][1])
* 完成 Suzuki Swift I 既有三门/五门尺寸组复用。
* 完成 Swift II 三门、五门、窄体三门、敞篷、普通三厢及低车高四驱三厢分组。Swift II 三门与五门外廓不同，不能共用一个尺寸组；GTI 与早期 68 HP 四驱三门的记录宽度为 1585 mm，单独建组。([汽车数据][2])
* 本轮未强行处理 Isuzu Gemini：欧洲柴油/GTI 掀背车型与部分数据库中的后期 JT 三厢数据存在代际及外廓混杂，留待下一轮集中闭合。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：25
* READY 映射行：31
* 尚待处理 Ktype：75
* 本轮引用尺寸组：14
* 本轮首次创建尺寸组：9
* 复用跨批次已有尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4438	4438	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	HIGH		READY
4439_3dr	4439	Hatchback	Swift I	SA	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4439_5dr	4439	Hatchback	Swift I	SA	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4440_3dr	4440	Hatchback	Swift I	SA	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4440_5dr	4440	Hatchback	Swift I	SA	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4441	4441	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH		READY
4442	4442	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	HIGH	Turbo旅行版高度不同于普通GF旅行版。	READY
4443	4443	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4444	4444	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4445	4445	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4446	4446	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4447	4447	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4448	4448	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4449	4449	Coupe	SVX	CX	2	EU-SUBARU-SVX-CX-COUPE-2D-01	HIGH		READY
4450_3dr	4450	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4450_5dr	4450	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4451_3dr	4451	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4451_5dr	4451	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4452_3dr	4452	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4452_5dr	4452	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4453_3dr	4453	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	HIGH	输入未区分门数，派生为三门物理分支。	READY
4453_5dr	4453	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	HIGH	输入未区分门数，派生为五门物理分支。	READY
4454	4454	Sedan	Swift II	SF413	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4455	4455	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	HIGH	该68 HP四驱版本仅确认三门分支。	READY
4456	4456	Convertible	Swift II	SF413	2	EU-SUZUKI-SWIFT-II-CONVERTIBLE-2D-01	HIGH		READY
4459	4459	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	HIGH	该71 HP四驱版本仅确认三门分支。	READY
4460	4460	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	HIGH	GTI仅确认三门物理分支。	READY
4462	4462	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4465	4465	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-4WD-LOW-01	HIGH	92 HP四驱三厢高度低于普通三厢。	READY
4466	4466	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4467	4467	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH	95 HP四驱版本与普通三厢外廓一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	4350	1690	1435	Auto-Data Subaru Impreza I Station Wagon GF GT 2.0 Turbo	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-gt-2.0-turbo-218hp-4wd-16117
EU-SUBARU-LEGACY-II-BD-SEDAN-01	4595	1695	1405	Auto-Data Subaru Legacy II BD/BG Sedan	https://www.auto-data.net/en/subaru-legacy-ii-bd-bg-generation-3615
EU-SUBARU-LEGACY-II-BG-WAGON-01	4670	1695	1490	Auto-Data Subaru Legacy II BD/BG Station Wagon	https://www.auto-data.net/en/subaru-legacy-ii-station-wagon-bd-bg-generation-3616
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	3745	1590	1350	Auto-Data Suzuki Cultus II Hatchback 1.3 i 3dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-i-3-dr-68hp-16542
EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	3845	1590	1380	Auto-Data Suzuki Cultus II Hatchback 1.3 i 5dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-i-5-dr-68hp-16544
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	3745	1585	1350	Auto-Data Suzuki Cultus II Hatchback 1.3 GTi 3dr;Auto-Data Suzuki Cultus II Hatchback 1.3 4WD 3dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-gti-3-dr-101hp-16541;https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-3-dr-68hp-4wd-16540
EU-SUZUKI-SWIFT-II-CONVERTIBLE-2D-01	3745	1590	1350	Auto-Data Suzuki Cultus Cabrio 1.3 SF413	https://www.auto-data.net/en/suzuki-cultus-cabrio-1.3-sf413-ak35-68hp-16536
EU-SUZUKI-SWIFT-II-SEDAN-4D-01	4075	1600	1380	Auto-Data Suzuki Cultus II Sedan	https://www.auto-data.net/en/suzuki-cultus-ii-generation-3722
EU-SUZUKI-SWIFT-II-SEDAN-4D-4WD-LOW-01	4075	1600	1340	Auto-Data Suzuki Cultus II 1.6 i SF416 4WD	https://www.auto-data.net/en/suzuki-cultus-ii-1.6-i-sf416-aj14-92hp-4wd-16552
```

## 下一步优先处理

1. 区分 Isuzu Gemini 1988–1990 欧洲三厢、三门掀背及 GTI 外廓，排除与后期 JT 三厢数据混用。
2. 集中闭合 Suzuki LJ80、SJ410、SJ413、Samurai、Vitara 的软顶/硬顶及短轴边界。
3. 处理 Isuzu Trooper I 的三门/五门、软顶/封闭车身以及 Midi Bus/Van 分组。
4. 批量处理 BMW 6 F12/F13、Alfa Romeo 8C、Nissan X-Trail T31 等资料较完整车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-gt-2.0-turbo-218hp-4wd-16117 "Subaru Impreza I Station Wagon (GF) GT 2.0 Turbo (218 Hp) 4WD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-i-5-dr-68hp-16544 "Suzuki Cultus II Hatchback 1.3 i (5 dr) (68 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 继续采用缓存优先模式，本轮仅做已确认尺寸组的关联复用，不重复抓取既有尺寸组来源。
* 新增完成 4 个 Ktype：BMW 5 F10 facelift 三厢、Nissan Prairie M11 4X4、Nissan Sunny N14 GTi-R、Daihatsu Cuore II L80 4WD。
* 本轮未创建或修正新的 DIMENSION_GROUP。

当前批次进度

* READY 映射：35
* PENDING 映射：71
* 已完成 Ktype：29 / 100
* 已确认并被引用的尺寸组：18
* 本轮未新建尺寸组
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4515	4515	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	HIGH		READY
4516	4516	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-02	MEDIUM		READY
4517	4517	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH		READY
4518	4518	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM		READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 集中处理 Isuzu Gemini、Trooper I、Midi 的车身分支与尺寸组闭合。
2. 处理 Suzuki LJ80、SJ410、SJ413、Samurai、Vitara 的 open/closed 分支。
3. 处理 BMW 6 F13、Alfa Romeo 8C、Nissan X-Trail II、VW Golf Plus V、VW Golf VI、Hyundai Accent I 等资料较完整车型。
4. 最后集中处理 Chrysler Le Baron、Jeep Wrangler YJ、Ford Maverick 等剩余车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 BMW M6 F13M 与 640d xDrive F13：前后期欧洲车型三维一致，分别建立稳定尺寸组，不按普通改款重复拆组。
* 完成 Alfa Romeo 8C Coupé、8C Spider，以及 Nissan X-Trail T31 改款前后分支；X-Trail 改款后长宽高均发生变化，拆为 `prefl`、`facelift`。([汽车数据][1])
* 完成 VW Golf Plus V 两个 Ktype 共用尺寸组；完成 Hyundai Accent I X3 四个 Ktype 的三门/五门派生。([汽车数据][2])

## 当前批次进度

* READY 映射：51
* PENDING 映射：60
* 已完成 Ktype：40 / 100
* 已确认并被引用的尺寸组：27
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4471_prefl	4471	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	HIGH	改款前物理外廓。	READY
4471_facelift	4471	SUV	X-Trail II Facelift	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	HIGH	改款后物理外廓。	READY
4481	4481	Coupe	M6 F13M	F13M	2	EU-BMW-M6-F13M-COUPE-01	HIGH		READY
4484	4484	Coupe	8C Competizione		2	EU-ALFA-ROMEO-8C-COMPETIZIONE-COUPE-01	HIGH		READY
4502	4502	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
4503	4503	Convertible	8C Spider		2	EU-ALFA-ROMEO-8C-SPIDER-CONVERTIBLE-01	HIGH		READY
4514	4514	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
4536	4536	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
4537_3dr	4537	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4537_5dr	4537	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4538_3dr	4538	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4538_5dr	4538	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4539_3dr	4539	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4539_5dr	4539	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4540_3dr	4540	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4540_5dr	4540	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685	Auto-Data Nissan X-Trail II T31 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-ii-t31-2.0-dci-150hp-4x4-automatic-907
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700	Auto-Data Nissan X-Trail II T31 facelift 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-ii-t31-facelift-2010-2.0-dci-150hp-4x4-automatic-17040
EU-BMW-M6-F13M-COUPE-01	4898	1899	1374	BMW M6 Coupé official technical data 2012;BMW M6 facelift official press kit 2014	https://www.press.bmwgroup.com/switzerland/article/attachment/T0128540DE/193201;https://www.press.bmwgroup.com/global/article/attachment/T0197553EN/287655
EU-ALFA-ROMEO-8C-COMPETIZIONE-COUPE-01	4381	1894	1341	Auto-Data Alfa Romeo 8C Competizione	https://www.auto-data.net/en/alfa-romeo-8c-competizione-4.7i-v8-32v-450hp-1261
EU-VW-GOLF-PLUS-V-MPV-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus	https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-tsi-122hp-dsg-17903
EU-ALFA-ROMEO-8C-SPIDER-CONVERTIBLE-01	4381	1892	1366	Auto-Data Alfa Romeo 8C Spider	https://www.auto-data.net/en/alfa-romeo-8c-spider-4.7-v8-450hp-41199
EU-BMW-6-F13-COUPE-01	4894	1894	1369	Auto-Data BMW 640d xDrive F13;Auto-Data BMW 640d xDrive F13 LCI	https://www.auto-data.net/en/bmw-6-series-coupe-f13-640d-313hp-xdrive-steptronic-18617;https://www.auto-data.net/en/bmw-6-series-coupe-f13-lci-facelift-2015-640d-313hp-xdrive-steptronic-26571
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I	https://www.auto-data.net/en/hyundai-accent-hatchback-i-1.3-i-60hp-13705
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I	https://www.auto-data.net/en/hyundai-accent-hatchback-i-1.3-i-60hp-13705
```

## 下一步优先处理

1. 集中闭合 Suzuki LJ80、SJ410、SJ413、Samurai、Vitara 的开放式、封闭式及短轴分支。
2. 集中处理 Isuzu Trooper I、Gemini 与 Midi，优先消除门数、车顶和车身长度边界。
3. 处理 Chrysler Le Baron 三厢/敞篷、Jeep Wrangler YJ、Ford Maverick。
4. 最后处理 Suzuki Carry/Super Carry、Mazda E-Series 底盘车及剩余 VW Golf VI。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-8c-competizione-4.7i-v8-32v-450hp-1261 "Alfa Romeo 8C Competizione 4.7i V8 32V (450 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-tsi-122hp-dsg-17903 "Volkswagen Golf VI Plus 1.4 TSI (122 Hp) DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 完成 Suzuki LJ80、SJ410、SJ413 与第一代 Vitara 共 10 个 Ktype。
* `4485`、`4486` 的生产区间跨越 SJ 系列窄体至 Samurai 宽体转换，分别拆为 `prewide` 和 `wide` 两个物理分支；窄体硬顶为 1460 mm 宽，后期宽体硬顶为 1530 mm 宽。([汽车目录][1])
* SJ410 开放式和封闭式车身分别建组；封闭式 SJ410 与改宽前 SJ413 复用相同窄体硬顶尺寸组。([汽车目录][2])
* 第一代 Vitara 开放式和金属硬顶三维相同，但因车顶及车身形式不同，分别建立两个尺寸组。([汽车目录][3])
* Samurai `4479`、`4480`、`4482`、`4483` 暂未处理：其时间范围包含后期保险杠长度、Metal Top、Resin Top 和 High Roof 等外廓变化，下一轮集中拆分，避免错误合并。

## 2. 当前批次进度

* 已完成 Ktype：50 / 100
* READY 映射：63
* PENDING 映射：50
* 已确认并被引用的尺寸组：33
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4470	4470	SUV	LJ80	LJ80	2	EU-SUZUKI-LJ80-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
4477	4477	SUV	SJ Series	SJ410	2	EU-SUZUKI-SJ-SUV-OPEN-NARROW-01	HIGH	开放式窄体车身。	READY
4478	4478	SUV	SJ Series	SJ410	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	HIGH	封闭式窄体车身。	READY
4485_prewide	4485	SUV	SJ Series	SJ413	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	MEDIUM	Ktype生产区间覆盖改宽前窄体硬顶分支。	READY
4485_wide	4485	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	Ktype生产区间覆盖后期宽体硬顶分支。	READY
4486_prewide	4486	SUV	SJ Series	SJ413	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	HIGH	Ktype生产区间覆盖改宽前窄体硬顶分支。	READY
4486_wide	4486	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	HIGH	Ktype生产区间覆盖后期宽体硬顶分支。	READY
4493	4493	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
4496	4496	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4505	4505	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4506	4506	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4510	4510	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-LJ80-SUV-OPEN-01	3195	1395	1670	Automobile-Catalog 1980 Suzuki LJ 80 Q	https://www.automobile-catalog.com/car/1980/36740/suzuki_lj_80.html
EU-SUZUKI-SJ-SUV-OPEN-NARROW-01	3430	1460	1680	Automobile-Catalog 1987 Suzuki SJ 410 JA Cabriolet	https://www.automobile-catalog.com/car/1987/3337970/suzuki_sj_410_ja_cabriolet.html
EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	3440	1460	1690	Automobile-Catalog 1988 Suzuki SJ 413 JX Wagon	https://www.automobile-catalog.com/car/1988/60230/suzuki_sj-413.html
EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	3440	1530	1675	Automobile-Catalog 1988 Suzuki Samurai 1.3 Van catalyst	https://www.automobile-catalog.com/car/1988/3338450/suzuki_samurai_1_3_van_catalyst.html
EU-SUZUKI-VITARA-I-SUV-OPEN-01	3620	1630	1665	Automobile-Catalog 1991 Suzuki Vitara 1.6 Cabrio	https://www.automobile-catalog.com/car/1991/3349115/suzuki_vitara_1_6_cabrio.html
EU-SUZUKI-VITARA-I-SUV-CLOSED-01	3620	1630	1665	Automobile-Catalog 1991 Suzuki Vitara 1.6 Metal Top	https://www.automobile-catalog.com/car/1991/3349145/suzuki_vitara_1_6_metal_top.html
```

## 5. 下一步优先处理

1. 集中拆分 Samurai `4479`、`4480`、`4482`、`4483` 的标准硬顶、后期 Metal Top、Resin Top、高顶及长度变化。
2. 闭合 Isuzu Gemini 三厢/掀背和 Isuzu Trooper I 开放式/封闭式分支。
3. 批量处理 Isuzu Midi Bus/Van、Suzuki Carry/Super Carry 与 Mazda E-Series 底盘车。
4. 处理 Chrysler Le Baron、Jeep Wrangler YJ、Ford Maverick 和剩余乘用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/60230/suzuki_sj-413.html?utm_source=chatgpt.com "1988 Suzuki SJ 413 JX Wagon Specs Review (47 kW / 64 PS / 63 hp) (up to mid-year 1988 for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/3337970/suzuki_sj_410_ja_cabriolet.html?utm_source=chatgpt.com "1987 Suzuki SJ 410 JA Cabriolet Specs Review (33.5 kW ..."
[3]: https://www.automobile-catalog.com/car/1991/3349115/suzuki_vitara_1_6_cabrio.html?utm_source=chatgpt.com "1991 Suzuki Vitara 1.6 Cabrio Specs Review (55 kW / 75 PS / 74 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 完成 Isuzu Gemini II 柴油三厢、柴油三门掀背及 GTI 三门掀背共 5 个 Ktype；柴油普通版与涡轮版仅因动力不同，不重复建组。([汽车目录][1])
* 完成 Suzuki Samurai 1.3 封闭式车型共 3 个 Ktype，按标准金属顶与 High Roof 两种明确外廓派生。
* 根据原始荷兰市场 Samurai brochure，将本批此前建立的宽体封闭式组由 `3440×1530×1675` 修正为 `3440×1540×1680`；另建立 `3440×1540×1830` 高顶组。([汽车目录档案][2])
* Samurai 1.0 的高顶适用范围仍未闭合，本轮未强行关联。

## 2. 当前批次进度

* 已完成 Ktype：58 / 100
* READY 映射：74
* PENDING Ktype：42
* 已确认并被引用的尺寸组：37
* 本轮首次创建尺寸组：4
* 本轮修正尺寸组：1
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4461	4461	Sedan	Gemini II	JT	4	EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	MEDIUM		READY
4463	4463	Sedan	Gemini II	JT	4	EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	HIGH		READY
4464	4464	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	HIGH		READY
4468	4468	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	MEDIUM		READY
4469	4469	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-GTI-01	HIGH		READY
4480_lowroof	4480	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4480_highroof	4480	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
4482_lowroof	4482	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4482_highroof	4482	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
4483_lowroof	4483	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4483_highroof	4483	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	3440	1540	1680	Suzuki Samurai 1988 Netherlands original brochure	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Samurai-1988-NL.pdf
EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	3440	1540	1830	Suzuki Samurai 1988 Netherlands original brochure	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Samurai-1988-NL.pdf
EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	4040	1615	1380	Automobile-Catalog 1989 Isuzu Gemini GLTD Sedan	https://www.automobile-catalog.com/car/1989/1259090/isuzu_gemini_gltd_sedan.html
EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	3995	1615	1380	Automobile-Catalog 1989 Isuzu Gemini CLD Hatchback	https://www.automobile-catalog.com/car/1989/1259075/isuzu_gemini_cld_hatchback.html
EU-ISUZU-GEMINI-II-JT-HATCHBACK-GTI-01	4010	1615	1365	Automobile-Catalog 1988 Isuzu Gemini GTi 16V Hatchback	https://www.automobile-catalog.com/car/1988/1259030/isuzu_gemini_gti_16v_hatchback.html
```

## 5. 下一步优先处理

1. 闭合 Isuzu Trooper I 的短轴开放式、短轴封闭式及长轴封闭式分支。
2. 批量处理 Isuzu Midi Bus/Van，优先确认普通车身与后期 2.4 柴油车身是否改变长度或高度。
3. 处理 Suzuki Carry、Super Carry 与 Mazda E-Series 底盘车。
4. 处理 Chrysler Le Baron、Jeep Wrangler YJ、Ford Maverick及剩余 VW Golf VI。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/1259090/isuzu_gemini_gltd_sedan.html?utm_source=chatgpt.com "1989 Isuzu Gemini GLTD Sedan Specs Review (49 kW / 67 PS / 66 hp) (up to mid-year 1989 for Europe Germany)"
[2]: https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Samurai-1988-NL.pdf?utm_source=chatgpt.com ":::::"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 Isuzu Trooper I 共 5 个 Ktype；2.8 TD 与 2.8 TD Intercooler 均确认同时存在短轴三门和长轴五门，因此分别派生 `swb`、`lwb` 两个物理分支。短轴封闭式为 `4145×1650×1830 mm`，长轴封闭式为 `4495×1650×1815 mm`。([德国汽车俱乐部][1])
* 2.3、2.6 i 与 2.2 TD 开放式均关联同一 Trooper I 短轴软顶外廓；软顶车身单独建组，不与三门封闭式合并。([汽车数据][2])
* 本轮首次创建 3 个 DIMENSION_GROUP，未修改既有尺寸组。

## 当前批次进度

* 已完成 Ktype：63 / 100
* READY 映射：81
* PENDING Ktype：37
* 已确认并被引用的尺寸组：40
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4472_swb	4472	SUV	Trooper I	UBS55	3	EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	HIGH	短轴三门封闭式分支。	READY
4472_lwb	4472	SUV	Trooper I	UBS55	5	EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	HIGH	长轴五门封闭式分支。	READY
4473_swb	4473	SUV	Trooper I	UBS55	3	EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	HIGH	短轴三门封闭式分支。	READY
4473_lwb	4473	SUV	Trooper I	UBS55	5	EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	HIGH	长轴五门封闭式分支。	READY
4474	4474	SUV	Trooper I	UBS16	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
4475	4475	SUV	Trooper I	UBS17	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
4476	4476	SUV	Trooper I	UBS52	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	4145	1650	1830	ADAC Isuzu Trooper 2.8 TD kurz;ADAC Isuzu Trooper 2.8 TD Intercooler DLX kurz	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350981/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350970/
EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	4495	1650	1815	ADAC Isuzu Trooper 2.8 TD lang;ADAC Isuzu Trooper 2.8 TD Intercooler LS lang	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350982/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350969/
EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	4145	1650	1830	Automobile-Catalog Isuzu Trooper Canvas-Top 2.2 TD;Auto-Data Isuzu Trooper Soft Top generation	https://www.automobile-catalog.com/car/1988/1269860/isuzu_trooper_canvas-top_2_2_td.html;https://www.auto-data.net/en/isuzu-trooper-soft-top-generation-3549
```

## 下一步优先处理

1. 集中闭合 Isuzu Midi Bus 与 Van，确认早期 2.0/2.2 和后期 2.4 柴油是否存在外廓变化。
2. 处理 Suzuki Carry、Super Carry 与 Mazda E-Series 底盘车。
3. 处理 Chrysler Le Baron 三厢与敞篷、Jeep Wrangler YJ、Ford Maverick。
4. 最后处理 Samurai 1.0、VW Golf VI、Suzuki Alto IV 及其余零散车型。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350982/ "Isuzu Trooper 2.8 TD lang (5-Türer) (01/87 - 11/88): Technische Daten, Bilder, Preise | ADAC"
[2]: https://www.auto-data.net/en/isuzu-trooper-soft-top-2.6-i-ubs17-116hp-15948 "Isuzu Trooper Soft Top 2.6 i (UBS17) (116 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 完成 Chrysler LeBaron 共 9 个 Ktype。
* 四门三厢统一关联 AA 车身尺寸组。
* 敞篷车依据原厂 1990 与 1992 brochure 中外廓变化拆分为 `prefl`、`facelift`；跨越两个外廓阶段的 Ktype 输出两条派生映射。

## 2. 当前批次进度

* 已完成 Ktype：72 / 100
* READY 映射：93
* PENDING Ktype：28
* 已确认并被引用的尺寸组：43
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4519	4519	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4520	4520	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4521	4521	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4523	4523	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4524	4524	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	改款前敞篷外廓。	READY
4525	4525	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	改款前敞篷外廓。	READY
4526_prefl	4526	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4526_facelift	4526	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
4527_prefl	4527	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4527_facelift	4527	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
4528_prefl	4528	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4528_facelift	4528	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	4641	1730	1364	Chrysler 1992 LeBaron official brochure	https://xr793.com/wp-content/uploads/2017/01/1992-Chrysler-Lebaron.pdf
EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	4696	1740	1328	Chrysler 1990 LeBaron Coupe and Convertible official brochure	https://xr793.com/wp-content/uploads/2025/11/1990-Chrysler-LeBaron-Coupe-Convertible.pdf
EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	4694	1758	1331	Chrysler 1992 LeBaron official brochure	https://xr793.com/wp-content/uploads/2017/01/1992-Chrysler-Lebaron.pdf
```

## 5. 下一步优先处理

1. Jeep Wrangler YJ 与 Ford Maverick/Terrano II。
2. Isuzu Midi Bus/Van 的轴距、车顶分支。
3. Suzuki Carry、Super Carry 与 Mazda E-Series 底盘车。
4. VW Golf VI、Suzuki Alto IV、Samurai 1.0 等剩余零散车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 完成 Suzuki Alto IV 1.0 三门掀背车型。
* 完成 Jeep Wrangler YJ 后期 2.5 与 4.0 开放式车型；两种发动机不改变物理外廓，共用同一尺寸组。欧洲规格记录为 `3890×1745×1780 mm`，宽度不含后视镜。([汽车目录][1])
* 完成 Ford Maverick I 2.4 与 2.7 TD；两个 Ktype 均覆盖三门短轴和五门长轴，分别派生 `swb`、`lwb`。ADAC 数据确认短轴为 `4105×1755×1805 mm`，长轴为 `4585×1755×1810 mm`。([德国汽车俱乐部][2])
* 完成 VW Golf VI 1.6 MultiFuel 五门掀背车型；五门车身宽度为 1786 mm，不与三门 1779 mm 车身合并。([大众汽车英国][3])

## 2. 当前批次进度

* 已完成 Ktype：78 / 100
* READY 映射：101
* PENDING Ktype：22
* 已确认并被引用的尺寸组：48
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4513	4513	Hatchback	Alto IV		3	EU-SUZUKI-ALTO-IV-HATCHBACK-3D-01	HIGH		READY
4530	4530	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	HIGH	后期开放式车身。	READY
4531	4531	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	HIGH	后期开放式车身。	READY
4533_swb	4533	SUV	Maverick I	UDS	3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
4533_lwb	4533	SUV	Maverick I	UDS	5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
4534_swb	4534	SUV	Maverick I	UDS	3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
4534_lwb	4534	SUV	Maverick I	UDS	5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
4535	4535	Hatchback	Golf VI	5K	5	EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	HIGH	MultiFuel五门车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-ALTO-IV-HATCHBACK-3D-01	3495	1495	1405	Automobile-Catalog 1994 Suzuki Alto 1.0 Europe export	https://www.automobile-catalog.com/car/1994/3358250/suzuki_alto.html
EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	3890	1745	1780	Automobile-Catalog 1992 Jeep Wrangler 2.5 Europe;Automobile-Catalog 1994 Jeep Wrangler 4.0 Europe	https://www.automobile-catalog.com/car/1992/1315625/jeep_wrangler_2_5.html;https://www.automobile-catalog.com/car/1994/1315805/jeep_wrangler_4_0.html
EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	4105	1755	1805	ADAC Ford Maverick 2.4 3-Türer;ADAC Ford Maverick 2.7 TD 3-Türer	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348771/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348773/
EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	4585	1755	1810	ADAC Ford Maverick 2.4 5-Türer;ADAC Ford Maverick 2.7 TD 5-Türer	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348775/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348776/
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480	Volkswagen Golf VI official UK brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_oct_2011.pdf
```

## 5. 下一步优先处理

1. 闭合 Jeep Wrangler YJ 早期 103 HP 开放式车型的标准版与 Sahara 保险杠长度边界。
2. 集中处理 Isuzu Midi Bus/Van 的普通轴距、长轴及后期 2.4 柴油分支。
3. 批量处理 Mazda E-Series Pritsche/Fahrgestell、Suzuki Carry 与 Super Carry。
4. 最后处理 Samurai 1.0 及剩余零散 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1992/1315625/jeep_wrangler_2_5.html?utm_source=chatgpt.com "Detailed specs review of 1992 Jeep Wrangler 2.5 model for Europe"
[2]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348775/?utm_source=chatgpt.com "Ford Maverick 2.4 (5-Türer) (03/93 - 08/96)"
[3]: https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_oct_2011.pdf?utm_source=chatgpt.com "Volkswagen Information Service. Telephone 0800 333 666"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 完成 Isuzu Midi Bus/Van 共 12 个 Ktype。各发动机与驱动版本均确认覆盖 `L1H1`、`L2H1`、`L2H2` 三种物理外廓，因此按短轴低顶、长轴低顶、长轴高顶派生；发动机及驱动形式不额外创建尺寸组。([Дром][1])
* 三个基础外廓分别为 `4350×1690×1950`、`4690×1690×1950`、`4690×1690×2185 mm`，Bus 与 Van 在外部包络完全相同时复用同一尺寸组。([汽车网][2])
* 2.4 TD Bus 另确认存在 `4960×1690×1950 mm` 的加长乘用车身，Ktype `4492` 增加 `lwb_extended` 分支，不与普通 4690 mm 长轴车身合并。([引擎细节][3])

## 2. 当前批次进度

* 已完成 Ktype：90 / 100
* READY 映射：138
* PENDING Ktype：10
* 已确认并被引用的尺寸组：52
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4487_swb_lowroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4487_lwb_lowroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4487_lwb_highroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4488_swb_lowroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱乘用车身。	READY
4488_lwb_lowroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱乘用车身。	READY
4488_lwb_highroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱乘用车身。	READY
4489_swb_lowroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4489_lwb_lowroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4489_lwb_highroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4490_swb_lowroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4490_lwb_lowroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4490_lwb_highroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4491_swb_lowroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱乘用车身。	READY
4491_lwb_lowroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱乘用车身。	READY
4491_lwb_highroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱乘用车身。	READY
4492_swb_lowroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4492_lwb_lowroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4492_lwb_extended	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-BUS-LWB-EXTENDED-01	MEDIUM	加长后悬长轴乘用车身。	READY
4492_lwb_highroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4494_swb_lowroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4494_lwb_lowroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4494_lwb_highroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4495_swb_lowroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱厢式车身。	READY
4495_lwb_lowroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱厢式车身。	READY
4495_lwb_highroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱厢式车身。	READY
4497_swb_lowroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4497_lwb_lowroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4497_lwb_highroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4498_swb_lowroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4498_lwb_lowroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4498_lwb_highroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4500_swb_lowroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱厢式车身。	READY
4500_lwb_lowroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱厢式车身。	READY
4500_lwb_highroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱厢式车身。	READY
4501_swb_lowroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4501_lwb_lowroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4501_lwb_highroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-MIDI-I-SWB-LOWROOF-01	4350	1690	1950	Drom Isuzu Midi L1H1 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284238/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-LWB-LOWROOF-01	4690	1690	1950	Drom Isuzu Midi L2H1 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284271/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	4690	1690	2185	Drom Isuzu Midi L2H2 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284256/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-BUS-LWB-EXTENDED-01	4960	1690	1950	EngineInDetail Isuzu Midi Estate long 2.4 TD;Gazoo Isuzu Midi Bus specifications	https://www.engineindetail.com/pa/isuzu-midi-estate-wagon-long-2.4-td-1989;https://gazoo.pl/samochody/isuzu/isuzu-midi-bus/
```

## 5. 下一步优先处理

1. Mazda E2000 `4499`、`4504`、`4511`、`4532`：按 SR1/SR2、短轴/长轴及 Pritsche/Fahrgestell 外廓闭合。
2. Suzuki Carry `4507` 与 Super Carry `4508`、`4509`、`4512`。
3. Suzuki Samurai 1.0 `4479` 的标准顶与高顶边界。
4. Jeep Wrangler YJ 早期 `4529` 的标准保险杠与外廓边界。

推进信号：CONTINUE

[1]: https://www.drom.ru/catalog/isuzu/midi/g_1986_11078/ "Isuzu Midi 1986, 1987, 1988, 1989, 1990, минивэн, 1 поколение технические характеристики и комплектации"
[2]: https://www.motor-car.net/bedford/item/10086-midi-1985-94 "Bedford Midi (1985-1994)"
[3]: https://www.engineindetail.com/pa/isuzu-midi-estate-wagon-long-2-4-td-1989?utm_source=chatgpt.com "Isuzu Midi Estate (Wagon) long 2.4 TD 1989 - Specs, Review & Tests"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 完成 Samurai 1.0 `4479`：确认其为 SJ410 窄体三门封闭式车身，直接复用既有窄体尺寸组，不与 1540 mm 宽的 Samurai 1.3 宽体组合并。([Bendix Brakes][1])
* 完成 Carry 0.8 `4507`：输入未区分普通顶和高顶，拆为 `lowroof`、`highroof`；两者长宽相同，高度分别为 1660 mm 和1855 mm。([汽车目录][2])
* 完成 Super Carry Bus `4508`、`4509`、`4512`：三种功率均属于 SK410 相同乘用车身，统一关联 `3295×1395×1780 mm` 尺寸组。([Brembo 配件][3])
* 完成早期 Jeep Wrangler YJ `4529`：开放式软顶车身单独建组，不与后期 `3890×1745×1780 mm` 组复用。([汽车目录][4])

## 2. 当前批次进度

* 已完成 Ktype：96 / 100
* READY 映射：145
* PENDING Ktype：4
* 已确认并被引用的尺寸组：56
* 本轮首次创建尺寸组：4
* 剩余 Ktype：`4499`、`4504`、`4511`、`4532`
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4479	4479	SUV	Samurai SJ	SJ410	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	MEDIUM	SJ410窄体封闭式车身。	READY
4507_lowroof	4507	Van	Carry VII	ST90V	4	EU-SUZUKI-CARRY-ST90V-VAN-LOWROOF-01	HIGH	普通顶厢式车身。	READY
4507_highroof	4507	Van	Carry VII	ST90V	4	EU-SUZUKI-CARRY-ST90V-VAN-HIGHROOF-01	HIGH	高顶厢式车身。	READY
4508	4508	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4509	4509	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4512	4512	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4529	4529	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-EARLY-01	HIGH	早期软顶开放式外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-CARRY-ST90V-VAN-LOWROOF-01	3195	1395	1660	Automobile-Catalog 1985 Suzuki Carry Van ST90V Europe	https://www.automobile-catalog.com/car/1985/3325745/suzuki_carry_van_st90v.html
EU-SUZUKI-CARRY-ST90V-VAN-HIGHROOF-01	3195	1395	1855	Automobile-Catalog 1983 Suzuki Carry Van ST90V High Roof Europe	https://www.automobile-catalog.com/car/1983/3325715/suzuki_carry_van_st90v_high_roof.html
EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	3295	1395	1780	Suzuki Carry historical SK410 specifications	https://en.wikipedia.org/wiki/Suzuki_Carry
EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-EARLY-01	3900	1740	1829	Automobile-Catalog 1990 Jeep Wrangler Sahara Soft-Top 2.5L	https://www.automobile-catalog.com/car/1990/1315400/jeep_wrangler_sahara_soft-top_2_5l.html
```

## 5. 下一步优先处理

1. 集中闭合 Mazda E2000 `4499`、`4504`、`4511`、`4532`。
2. 确认四个 Ktype 是否全部为第三代 E-Series 单排长轴底盘车，或是否跨越早期/后期驾驶室外廓。
3. 尺寸闭合后立即进行唯一一次机械检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.bendix.co.id/en-id/catalogue/suzuki/samurai/samurai-closed-off-road-vehicle-sj/10-all-wheel-drive-sj410?id=4479&tab=Passenger&utm_source=chatgpt.com "SUZUKI SAMURAI Closed Off-Road Vehicle (SJ_) 1.0 All ..."
[2]: https://www.automobile-catalog.com/car/1983/3325715/suzuki_carry_van_st90v_high_roof.html?utm_source=chatgpt.com "1983 Suzuki Carry Van ST90V High Roof Specs Review (27 kW / 37 PS / 36 hp) (up to October 1983 for Europe export)"
[3]: https://www.bremboparts.com/america/en/catalogue/suzuki-super-carry-bus-ed-1-0-sk410/000004509-1?utm_source=chatgpt.com "Pads and Discs for SUZUKI SUPER CARRY Bus (ED) 1.0 (SK410)"
[4]: https://www.automobile-catalog.com/car/1990/1315400/jeep_wrangler_sahara_soft-top_2_5l.html?utm_source=chatgpt.com "1990 Jeep Wrangler Sahara Soft-Top 2.5L (man. 5)"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4301-4400_ktype_dimension_mapping_final.tsv
- all_4301-4400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 完成最后 4 个 Mazda E2000 Ktype。`4499`、`4504`、`4532`关联后期 `4690×1690×1960 mm` 长车身底盘组；跨越早期与后期外廓的 `4511` 拆为 `early`、`late` 两个分支。早期 E2000 Ute 记录为 `4390×1690×1960 mm`，后期 Cab Chassis 记录为 `4690×1690×1960 mm`。([Carsales][1])
* 已完成唯一一次机械收尾：固定表头、150 个 `id` 唯一、58 个 `DIMENSION_GROUP_ID` 唯一、映射引用完全闭合、尺寸及来源字段完整、无孤立尺寸组。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：150
* PENDING 映射：0
* DIMENSION_GROUP：58
* 映射引用闭合：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4438	4438	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	HIGH		READY
4439_3dr	4439	Hatchback	Swift I	SA	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4439_5dr	4439	Hatchback	Swift I	SA	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4440_3dr	4440	Hatchback	Swift I	SA	3	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4440_5dr	4440	Hatchback	Swift I	SA	5	EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4441	4441	Sedan	Impreza I	GC	4	EU-SUBARU-IMPREZA-I-GC-SEDAN-01	HIGH		READY
4442	4442	Wagon	Impreza I	GF	5	EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	HIGH	Turbo旅行版高度不同于普通GF旅行版。	READY
4443	4443	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4444	4444	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4445	4445	Sedan	Legacy II	BD	4	EU-SUBARU-LEGACY-II-BD-SEDAN-01	HIGH		READY
4446	4446	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4447	4447	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4448	4448	Wagon	Legacy II	BG	5	EU-SUBARU-LEGACY-II-BG-WAGON-01	HIGH		READY
4449	4449	Coupe	SVX	CX	2	EU-SUBARU-SVX-CX-COUPE-2D-01	HIGH		READY
4450_3dr	4450	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4450_5dr	4450	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4451_3dr	4451	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4451_5dr	4451	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4452_3dr	4452	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门物理分支。	READY
4452_5dr	4452	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门物理分支。	READY
4453_3dr	4453	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	HIGH	输入未区分门数，派生为三门物理分支。	READY
4453_5dr	4453	Hatchback	Swift II		5	EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	HIGH	输入未区分门数，派生为五门物理分支。	READY
4454	4454	Sedan	Swift II	SF413	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4455	4455	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	HIGH	该68 HP四驱版本仅确认三门分支。	READY
4456	4456	Convertible	Swift II	SF413	2	EU-SUZUKI-SWIFT-II-CONVERTIBLE-2D-01	HIGH		READY
4459	4459	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	HIGH	该71 HP四驱版本仅确认三门分支。	READY
4460	4460	Hatchback	Swift II		3	EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	HIGH	GTI仅确认三门物理分支。	READY
4461	4461	Sedan	Gemini II	JT	4	EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	MEDIUM		READY
4462	4462	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4463	4463	Sedan	Gemini II	JT	4	EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	HIGH		READY
4464	4464	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	HIGH		READY
4465	4465	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-4WD-LOW-01	HIGH	92 HP四驱三厢高度低于普通三厢。	READY
4466	4466	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH		READY
4467	4467	Sedan	Swift II	SF416	4	EU-SUZUKI-SWIFT-II-SEDAN-4D-01	HIGH	95 HP四驱版本与普通三厢外廓一致。	READY
4468	4468	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	MEDIUM		READY
4469	4469	Hatchback	Gemini II	JT	3	EU-ISUZU-GEMINI-II-JT-HATCHBACK-GTI-01	HIGH		READY
4470	4470	SUV	LJ80	LJ80	2	EU-SUZUKI-LJ80-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
4471_prefl	4471	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	HIGH	改款前物理外廓。	READY
4471_facelift	4471	SUV	X-Trail II Facelift	T31	5	EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	HIGH	改款后物理外廓。	READY
4472_swb	4472	SUV	Trooper I	UBS55	3	EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	HIGH	短轴三门封闭式分支。	READY
4472_lwb	4472	SUV	Trooper I	UBS55	5	EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	HIGH	长轴五门封闭式分支。	READY
4473_swb	4473	SUV	Trooper I	UBS55	3	EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	HIGH	短轴三门封闭式分支。	READY
4473_lwb	4473	SUV	Trooper I	UBS55	5	EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	HIGH	长轴五门封闭式分支。	READY
4474	4474	SUV	Trooper I	UBS16	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
4475	4475	SUV	Trooper I	UBS17	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
4476	4476	SUV	Trooper I	UBS52	2	EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	HIGH	短轴软顶开放式车身。	READY
4477	4477	SUV	SJ Series	SJ410	2	EU-SUZUKI-SJ-SUV-OPEN-NARROW-01	HIGH	开放式窄体车身。	READY
4478	4478	SUV	SJ Series	SJ410	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	HIGH	封闭式窄体车身。	READY
4479	4479	SUV	Samurai SJ	SJ410	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	MEDIUM	SJ410窄体封闭式车身。	READY
4480_lowroof	4480	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4480_highroof	4480	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
4481	4481	Coupe	M6 F13M	F13M	2	EU-BMW-M6-F13M-COUPE-01	HIGH		READY
4482_lowroof	4482	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4482_highroof	4482	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
4483_lowroof	4483	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	标准金属顶封闭式分支。	READY
4483_highroof	4483	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	MEDIUM	高顶封闭式分支。	READY
4484	4484	Coupe	8C Competizione		2	EU-ALFA-ROMEO-8C-COMPETIZIONE-COUPE-01	HIGH		READY
4485_prewide	4485	SUV	SJ Series	SJ413	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	MEDIUM	Ktype生产区间覆盖改宽前窄体硬顶分支。	READY
4485_wide	4485	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	MEDIUM	Ktype生产区间覆盖后期宽体硬顶分支。	READY
4486_prewide	4486	SUV	SJ Series	SJ413	3	EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	HIGH	Ktype生产区间覆盖改宽前窄体硬顶分支。	READY
4486_wide	4486	SUV	Samurai SJ	SJ413	3	EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	HIGH	Ktype生产区间覆盖后期宽体硬顶分支。	READY
4487_swb_lowroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4487_lwb_lowroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4487_lwb_highroof	4487	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4488_swb_lowroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱乘用车身。	READY
4488_lwb_lowroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱乘用车身。	READY
4488_lwb_highroof	4488	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱乘用车身。	READY
4489_swb_lowroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4489_lwb_lowroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4489_lwb_highroof	4489	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4490_swb_lowroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4490_lwb_lowroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4490_lwb_highroof	4490	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4491_swb_lowroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱乘用车身。	READY
4491_lwb_lowroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱乘用车身。	READY
4491_lwb_highroof	4491	MPV	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱乘用车身。	READY
4492_swb_lowroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶乘用车身。	READY
4492_lwb_lowroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶乘用车身。	READY
4492_lwb_extended	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-BUS-LWB-EXTENDED-01	MEDIUM	加长后悬长轴乘用车身。	READY
4492_lwb_highroof	4492	MPV	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶乘用车身。	READY
4493	4493	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
4494_swb_lowroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4494_lwb_lowroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4494_lwb_highroof	4494	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4495_swb_lowroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱厢式车身。	READY
4495_lwb_lowroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱厢式车身。	READY
4495_lwb_highroof	4495	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱厢式车身。	READY
4496	4496	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4497_swb_lowroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4497_lwb_lowroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4497_lwb_highroof	4497	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4498_swb_lowroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4498_lwb_lowroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4498_lwb_highroof	4498	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4499	4499	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH	后期长车身底盘车外廓。	READY
4500_swb_lowroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶四驱厢式车身。	READY
4500_lwb_lowroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶四驱厢式车身。	READY
4500_lwb_highroof	4500	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶四驱厢式车身。	READY
4501_swb_lowroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-SWB-LOWROOF-01	HIGH	短轴低顶厢式车身。	READY
4501_lwb_lowroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-LOWROOF-01	HIGH	长轴低顶厢式车身。	READY
4501_lwb_highroof	4501	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车身。	READY
4502	4502	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
4503	4503	Convertible	8C Spider		2	EU-ALFA-ROMEO-8C-SPIDER-CONVERTIBLE-01	HIGH		READY
4504	4504	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	MEDIUM	后期长车身底盘车外廓。	READY
4505	4505	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4506	4506	SUV	Vitara I		3	EU-SUZUKI-VITARA-I-SUV-CLOSED-01	HIGH	三门金属硬顶车身。	READY
4507_lowroof	4507	Van	Carry VII	ST90V	4	EU-SUZUKI-CARRY-ST90V-VAN-LOWROOF-01	HIGH	普通顶厢式车身。	READY
4507_highroof	4507	Van	Carry VII	ST90V	4	EU-SUZUKI-CARRY-ST90V-VAN-HIGHROOF-01	HIGH	高顶厢式车身。	READY
4508	4508	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4509	4509	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4510	4510	SUV	Vitara I		2	EU-SUZUKI-VITARA-I-SUV-OPEN-01	HIGH	开放式短轴车身。	READY
4511_early	4511	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	MEDIUM	生产区间覆盖早期底盘车外廓。	READY
4511_late	4511	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	MEDIUM	生产区间覆盖后期底盘车外廓。	READY
4512	4512	MPV	Super Carry ED	SK410	5	EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	HIGH		READY
4513	4513	Hatchback	Alto IV		3	EU-SUZUKI-ALTO-IV-HATCHBACK-3D-01	HIGH		READY
4514	4514	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
4515	4515	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	HIGH		READY
4516	4516	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-02	MEDIUM		READY
4517	4517	Hatchback	Sunny N14	N14	3	EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	HIGH		READY
4518	4518	Hatchback	Cuore II	L80	5	EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	MEDIUM		READY
4519	4519	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4520	4520	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4521	4521	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4523	4523	Sedan	LeBaron Sedan AA	AA	4	EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	HIGH		READY
4524	4524	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	改款前敞篷外廓。	READY
4525	4525	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	改款前敞篷外廓。	READY
4526_prefl	4526	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4526_facelift	4526	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
4527_prefl	4527	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4527_facelift	4527	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
4528_prefl	4528	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
4528_facelift	4528	Convertible	LeBaron Convertible J	J	2	EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
4529	4529	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-EARLY-01	HIGH	早期软顶开放式外廓。	READY
4530	4530	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	HIGH	后期开放式车身。	READY
4531	4531	SUV	Wrangler I	YJ	2	EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	HIGH	后期开放式车身。	READY
4532	4532	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH	后期长车身底盘车外廓。	READY
4533_swb	4533	SUV	Maverick I	UDS	3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
4533_lwb	4533	SUV	Maverick I	UDS	5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
4534_swb	4534	SUV	Maverick I	UDS	3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	HIGH	短轴三门物理分支。	READY
4534_lwb	4534	SUV	Maverick I	UDS	5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	HIGH	长轴五门物理分支。	READY
4535	4535	Hatchback	Golf VI	5K	5	EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	HIGH	MultiFuel五门车身。	READY
4536	4536	MPV	Golf Plus V		5	EU-VW-GOLF-PLUS-V-MPV-01	HIGH		READY
4537_3dr	4537	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4537_5dr	4537	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4538_3dr	4538	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4538_5dr	4538	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4539_3dr	4539	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4539_5dr	4539	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
4540_3dr	4540	Hatchback	Accent I	X3	3	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	MEDIUM	输入未区分门数，派生为三门分支。	READY
4540_5dr	4540	Hatchback	Accent I	X3	5	EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	MEDIUM	输入未区分门数，派生为五门分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4301-4400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-IMPREZA-I-GF-WAGON-16-AWD-01	4350	1690	1420	Auto-Data Subaru Impreza I Station Wagon GF specifications	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-generation-3593
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-3D-01	3585	1530	1350	Suzuki Swift I SA 3-door historical specifications	https://www.carsguide.com.au/suzuki/swift/car-dimensions/1984
EU-SUZUKI-SWIFT-I-SA-HATCHBACK-5D-01	3770	1545	1350	Automobile-Catalog 1988 Suzuki Swift 1.3 GLX 5-door	https://www.automobile-catalog.com/car/1988/3327875/suzuki_swift_1_3_glx_5-door.html
EU-SUBARU-IMPREZA-I-GC-SEDAN-01	4350	1690	1415	Auto-Data Subaru Impreza I GC specifications	https://www.auto-data.net/en/subaru-impreza-i-gc-generation-3592
EU-SUBARU-IMPREZA-I-GF-WAGON-TURBO-01	4350	1690	1435	Auto-Data Subaru Impreza I Station Wagon GF GT 2.0 Turbo	https://www.auto-data.net/en/subaru-impreza-i-station-wagon-gf-gt-2.0-turbo-218hp-4wd-16117
EU-SUBARU-LEGACY-II-BD-SEDAN-01	4595	1695	1405	Auto-Data Subaru Legacy II BD/BG Sedan	https://www.auto-data.net/en/subaru-legacy-ii-bd-bg-generation-3615
EU-SUBARU-LEGACY-II-BG-WAGON-01	4670	1695	1490	Auto-Data Subaru Legacy II BD/BG Station Wagon	https://www.auto-data.net/en/subaru-legacy-ii-station-wagon-bd-bg-generation-3616
EU-SUBARU-SVX-CX-COUPE-2D-01	4625	1777	1300	Auto-Data Subaru SVX CX specifications	https://www.auto-data.net/en/subaru-svx-cx-3.3-i-24v-4wd-cxw-230hp-16203
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-01	3745	1590	1350	Auto-Data Suzuki Cultus II Hatchback 1.3 i 3dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-i-3-dr-68hp-16542
EU-SUZUKI-SWIFT-II-HATCHBACK-5D-01	3845	1590	1380	Auto-Data Suzuki Cultus II Hatchback 1.3 i 5dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-i-5-dr-68hp-16544
EU-SUZUKI-SWIFT-II-SEDAN-4D-01	4075	1600	1380	Auto-Data Suzuki Cultus II Sedan	https://www.auto-data.net/en/suzuki-cultus-ii-generation-3722
EU-SUZUKI-SWIFT-II-HATCHBACK-3D-NARROW-01	3745	1585	1350	Auto-Data Suzuki Cultus II Hatchback 1.3 GTi 3dr;Auto-Data Suzuki Cultus II Hatchback 1.3 4WD 3dr	https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-gti-3-dr-101hp-16541;https://www.auto-data.net/en/suzuki-cultus-ii-hatchback-1.3-3-dr-68hp-4wd-16540
EU-SUZUKI-SWIFT-II-CONVERTIBLE-2D-01	3745	1590	1350	Auto-Data Suzuki Cultus Cabrio 1.3 SF413	https://www.auto-data.net/en/suzuki-cultus-cabrio-1.3-sf413-ak35-68hp-16536
EU-ISUZU-GEMINI-II-JT-SEDAN-DIESEL-01	4040	1615	1380	Automobile-Catalog 1989 Isuzu Gemini GLTD Sedan	https://www.automobile-catalog.com/car/1989/1259090/isuzu_gemini_gltd_sedan.html
EU-ISUZU-GEMINI-II-JT-HATCHBACK-DIESEL-01	3995	1615	1380	Automobile-Catalog 1989 Isuzu Gemini CLD Hatchback	https://www.automobile-catalog.com/car/1989/1259075/isuzu_gemini_cld_hatchback.html
EU-SUZUKI-SWIFT-II-SEDAN-4D-4WD-LOW-01	4075	1600	1340	Auto-Data Suzuki Cultus II 1.6 i SF416 4WD	https://www.auto-data.net/en/suzuki-cultus-ii-1.6-i-sf416-aj14-92hp-4wd-16552
EU-ISUZU-GEMINI-II-JT-HATCHBACK-GTI-01	4010	1615	1365	Automobile-Catalog 1988 Isuzu Gemini GTi 16V Hatchback	https://www.automobile-catalog.com/car/1988/1259030/isuzu_gemini_gti_16v_hatchback.html
EU-SUZUKI-LJ80-SUV-OPEN-01	3195	1395	1670	Automobile-Catalog 1980 Suzuki LJ 80 Q	https://www.automobile-catalog.com/car/1980/36740/suzuki_lj_80.html
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685	Auto-Data Nissan X-Trail II T31 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-ii-t31-2.0-dci-150hp-4x4-automatic-907
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700	Auto-Data Nissan X-Trail II T31 facelift 2.0 dCi	https://www.auto-data.net/en/nissan-x-trail-ii-t31-facelift-2010-2.0-dci-150hp-4x4-automatic-17040
EU-ISUZU-TROOPER-I-SUV-CLOSED-SWB-01	4145	1650	1830	ADAC Isuzu Trooper 2.8 TD kurz;ADAC Isuzu Trooper 2.8 TD Intercooler DLX kurz	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350981/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350970/
EU-ISUZU-TROOPER-I-SUV-CLOSED-LWB-01	4495	1650	1815	ADAC Isuzu Trooper 2.8 TD lang;ADAC Isuzu Trooper 2.8 TD Intercooler LS lang	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350982/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/isuzu/trooper/1generation-facelift/350969/
EU-ISUZU-TROOPER-I-SUV-OPEN-SWB-01	4145	1650	1830	Automobile-Catalog Isuzu Trooper Canvas-Top 2.2 TD;Auto-Data Isuzu Trooper Soft Top generation	https://www.automobile-catalog.com/car/1988/1269860/isuzu_trooper_canvas-top_2_2_td.html;https://www.auto-data.net/en/isuzu-trooper-soft-top-generation-3549
EU-SUZUKI-SJ-SUV-OPEN-NARROW-01	3430	1460	1680	Automobile-Catalog 1987 Suzuki SJ 410 JA Cabriolet	https://www.automobile-catalog.com/car/1987/3337970/suzuki_sj_410_ja_cabriolet.html
EU-SUZUKI-SJ-SUV-CLOSED-NARROW-01	3440	1460	1690	Automobile-Catalog 1988 Suzuki SJ 413 JX Wagon	https://www.automobile-catalog.com/car/1988/60230/suzuki_sj-413.html
EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-01	3440	1540	1680	Suzuki Samurai 1988 Netherlands original brochure	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Samurai-1988-NL.pdf
EU-SUZUKI-SJ-SAMURAI-SUV-CLOSED-WIDE-HIGHROOF-01	3440	1540	1830	Suzuki Samurai 1988 Netherlands original brochure	https://autocatalogarchive.com/wp-content/uploads/2017/06/Suzuki-Samurai-1988-NL.pdf
EU-BMW-M6-F13M-COUPE-01	4898	1899	1374	BMW M6 Coupé official technical data 2012;BMW M6 facelift official press kit 2014	https://www.press.bmwgroup.com/switzerland/article/attachment/T0128540DE/193201;https://www.press.bmwgroup.com/global/article/attachment/T0197553EN/287655
EU-ALFA-ROMEO-8C-COMPETIZIONE-COUPE-01	4381	1894	1341	Auto-Data Alfa Romeo 8C Competizione	https://www.auto-data.net/en/alfa-romeo-8c-competizione-4.7i-v8-32v-450hp-1261
EU-ISUZU-MIDI-I-SWB-LOWROOF-01	4350	1690	1950	Drom Isuzu Midi L1H1 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284238/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-LWB-LOWROOF-01	4690	1690	1950	Drom Isuzu Midi L2H1 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284271/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-LWB-HIGHROOF-01	4690	1690	2185	Drom Isuzu Midi L2H2 specifications;Bedford/Isuzu Midi technical specifications	https://www.drom.ru/catalog/isuzu/midi/284256/;https://www.motor-car.net/bedford/item/10086-midi-1985-94
EU-ISUZU-MIDI-I-BUS-LWB-EXTENDED-01	4960	1690	1950	EngineInDetail Isuzu Midi Estate long 2.4 TD;Gazoo Isuzu Midi Bus specifications	https://www.engineindetail.com/pa/isuzu-midi-estate-wagon-long-2-4-td-1989;https://gazoo.pl/samochody/isuzu/isuzu-midi-bus/
EU-SUZUKI-VITARA-I-SUV-OPEN-01	3620	1630	1665	Automobile-Catalog 1991 Suzuki Vitara 1.6 Cabrio	https://www.automobile-catalog.com/car/1991/3349115/suzuki_vitara_1_6_cabrio.html
EU-SUZUKI-VITARA-I-SUV-CLOSED-01	3620	1630	1665	Automobile-Catalog 1991 Suzuki Vitara 1.6 Metal Top	https://www.automobile-catalog.com/car/1991/3349145/suzuki_vitara_1_6_metal_top.html
EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	4690	1690	1960	Carsales Mazda E2000 1997 Cab Chassis specifications	https://www.carsales.com.au/research/mazda/e2000/1997/no-badge/06a160c0-efe4-4461-83ed-a7290e0f5f55/
EU-VW-GOLF-PLUS-V-MPV-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus	https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-tsi-122hp-dsg-17903
EU-ALFA-ROMEO-8C-SPIDER-CONVERTIBLE-01	4381	1892	1366	Auto-Data Alfa Romeo 8C Spider	https://www.auto-data.net/en/alfa-romeo-8c-spider-4.7-v8-450hp-41199
EU-SUZUKI-CARRY-ST90V-VAN-LOWROOF-01	3195	1395	1660	Automobile-Catalog 1985 Suzuki Carry Van ST90V Europe	https://www.automobile-catalog.com/car/1985/3325745/suzuki_carry_van_st90v.html
EU-SUZUKI-CARRY-ST90V-VAN-HIGHROOF-01	3195	1395	1855	Automobile-Catalog 1983 Suzuki Carry Van ST90V High Roof Europe	https://www.automobile-catalog.com/car/1983/3325715/suzuki_carry_van_st90v_high_roof.html
EU-SUZUKI-SUPER-CARRY-SK410-MPV-01	3295	1395	1780	Suzuki Carry historical SK410 specifications	https://en.wikipedia.org/wiki/Suzuki_Carry
EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	4390	1690	1960	Carsales Mazda E2000 1984 Ute specifications	https://www.carsales.com.au/research/mazda/e2000/1984/no-badge/93de3e5c-0072-421e-ae20-d515ce8b5a1e/
EU-SUZUKI-ALTO-IV-HATCHBACK-3D-01	3495	1495	1405	Automobile-Catalog 1994 Suzuki Alto 1.0 Europe export	https://www.automobile-catalog.com/car/1994/3358250/suzuki_alto.html
EU-BMW-6-F13-COUPE-01	4894	1894	1369	Auto-Data BMW 640d xDrive F13;Auto-Data BMW 640d xDrive F13 LCI	https://www.auto-data.net/en/bmw-6-series-coupe-f13-640d-313hp-xdrive-steptronic-18617;https://www.auto-data.net/en/bmw-6-series-coupe-f13-lci-facelift-2015-640d-313hp-xdrive-steptronic-26571
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464	Auto-Data BMW 5 Series F10 LCI 525d	https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-525d-218hp-19953
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630	Auto-Data Nissan Prairie M11 2.0 i 4X4	https://www.auto-data.net/en/nissan-prairie-m11-2.0-i-98hp-4x4-408
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395	Automobile-Catalog Nissan Sunny N14 3-door	https://www.automobile-catalog.com/car/1994/2248085/nissan_sunny_2_0_gti_3d.html
EU-DAIHATSU-CUORE-II-L80-HATCHBACK-01	3200	1400	1410	Auto-Data Daihatsu Cuore II L80 specifications	https://www.auto-data.net/en/daihatsu-cuore-model-15
EU-CHRYSLER-LEBARON-AA-SEDAN-4D-01	4641	1730	1364	Chrysler 1992 LeBaron official brochure	https://xr793.com/wp-content/uploads/2017/01/1992-Chrysler-Lebaron.pdf
EU-CHRYSLER-LEBARON-J-CONVERTIBLE-PREFL-01	4696	1740	1328	Chrysler 1990 LeBaron Coupe and Convertible official brochure	https://xr793.com/wp-content/uploads/2025/11/1990-Chrysler-LeBaron-Coupe-Convertible.pdf
EU-CHRYSLER-LEBARON-J-CONVERTIBLE-FACELIFT-01	4694	1758	1331	Chrysler 1992 LeBaron official brochure	https://xr793.com/wp-content/uploads/2017/01/1992-Chrysler-Lebaron.pdf
EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-EARLY-01	3900	1740	1829	Automobile-Catalog 1990 Jeep Wrangler Sahara Soft-Top 2.5L	https://www.automobile-catalog.com/car/1990/1315400/jeep_wrangler_sahara_soft-top_2_5l.html
EU-JEEP-WRANGLER-I-YJ-SUV-OPEN-LATE-01	3890	1745	1780	Automobile-Catalog 1992 Jeep Wrangler 2.5 Europe;Automobile-Catalog 1994 Jeep Wrangler 4.0 Europe	https://www.automobile-catalog.com/car/1992/1315625/jeep_wrangler_2_5.html;https://www.automobile-catalog.com/car/1994/1315805/jeep_wrangler_4_0.html
EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	4105	1755	1805	ADAC Ford Maverick 2.4 3-Türer;ADAC Ford Maverick 2.7 TD 3-Türer	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348771/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348773/
EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	4585	1755	1810	ADAC Ford Maverick 2.4 5-Türer;ADAC Ford Maverick 2.7 TD 5-Türer	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348775/;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/maverick/i/348776/
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480	Volkswagen Golf VI official UK brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_oct_2011.pdf
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I	https://www.auto-data.net/en/hyundai-accent-hatchback-i-1.3-i-60hp-13705
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	4103	1620	1394	Auto-Data Hyundai Accent Hatchback I	https://www.auto-data.net/en/hyundai-accent-hatchback-i-1.3-i-60hp-13705
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4301-4400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carsales.com.au/research/mazda/e2000/1984/no-badge/93de3e5c-0072-421e-ae20-d515ce8b5a1e/ "https://www.carsales.com.au/research/mazda/e2000/1984/no-badge/93de3e5c-0072-421e-ae20-d515ce8b5a1e/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4301-4400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4301-4400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5827 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1784 行）

