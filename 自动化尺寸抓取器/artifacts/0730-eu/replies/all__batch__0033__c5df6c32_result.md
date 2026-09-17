# 任务：all 第 3201-3300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0033__c5df6c32


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3201-3300 行

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
all 第 3201-3300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-HONDA-CR-V-V-RW-SUV-AWD-01	4600	1855	1689
EU-HONDA-CR-V-V-RW-SUV-FWD-01	4600	1855	1679
EU-KIA-CERATO-IV-BD-SEDAN-01	4640	1800	1450
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470
EU-KIA-RIO-III-HATCHBACK-01	4045	1720	1455
EU-KIA-SORENTO-II-XM-FACELIFT-SUV-01	4685	1885	1700
EU-KIA-SORENTO-III-SUV-FACELIFT-01	4800	1890	1690
EU-KIA-SORENTO-III-SUV-PREFL-01	4780	1890	1690
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645
EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	4075	1765	1600
EU-KIA-VENGA-YN-HATCHBACK-PREFL-01	4068	1765	1600
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305
EU-MAN-TGE-I-VAN-L1H1-RWD-01	5986	2040	2355
EU-MAN-TGE-I-VAN-L1H2-RWD-01	5986	2040	2590
EU-MAN-TGE-I-VAN-L2H2-RWD-01	6836	2040	2590
EU-MAN-TGE-I-VAN-L2H3-RWD-01	6836	2040	2798
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355
EU-MAN-TGE-I-VAN-L3H2-RWD-01	7391	2040	2590
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590
EU-MAN-TGE-I-VAN-L3H3-RWD-01	7391	2040	2798
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590
EU-MAN-TGE-I-VAN-L4H4-01	6836	2040	2798
EU-MAN-TGE-I-VAN-L5H3-01	7391	2040	2590
EU-MAN-TGE-I-VAN-L5H4-01	7391	2040	2798
EU-MAZDA-6-III-FACELIFT-SEDAN-01	4870	1840	1450
EU-MAZDA-6-III-FACELIFT-WAGON-01	4805	1840	1475
EU-MAZDA-626-II-GC-COUPE-01	4430	1690	1350
EU-MAZDA-626-III-GD-SEDAN-FACELIFT-01	4535	1690	1410
EU-MAZDA-CX-5-II-KF-SUV-01	4550	1840	1675
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-PAGANI-ZONDA-CINQUE-COUPE-01	4435	2055	1141
EU-PAGANI-ZONDA-CINQUE-ROADSTER-CONVERTIBLE-01	4435	2055	1141
EU-PAGANI-ZONDA-F-ROADSTER-CONVERTIBLE-01	4435	2055	1141
EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	4395	2055	1151
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457
EU-SEAT-ATECA-I-KH7-SUV-FACELIFT-FWD-01	4381	1841	1601
EU-SEAT-ATECA-I-KH7-SUV-PREFL-FWD-01	4363	1841	1601
EU-SUBARU-FORESTER-IV-SJ-SUV-01	4595	1795	1735
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	Gle	GLE 300 D 4-matic	SUV	Allrad	Diesel	180	245	Oct 2018	Mar 2023	2024-03-01	133936
KIA	Optima	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	121	165	Mar 2013	Dec 2015	2024-03-01	133937
KIA	Rio ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jan 2010	Dec 2011	2024-03-01	133939
KIA	Sorento ii	2.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	126	171	Apr 2010	Dec 2015	2024-03-01	133945
KIA	Sportage ii	2.0 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	101	137	Jun 2009	May 2010	2024-03-01	133954
Mercedes-benz	E-Klasse	E 180	Stufenheck	Heckantrieb	Benzin	115	156	Aug 2013	Dec 2015	2024-03-01	133955
Daewoo	Rezzo	1.6	Großraumlimousine	Frontantrieb	Benzin	78	106	Feb 2002	Dec 2004	2024-03-01	133956
Renault	Clio iv	0.9 TCE 90 LPG	Kasten/Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Aug 2015	Aug 2021	2026-05-01	133957
Land Rover	Range rover sport i	4.2 4X4	SUV	Allrad	Benzin	291	396	Jan 2006	Feb 2010	2024-03-01	133959
Subaru	Legacy v station wagon	2.5 CNG AWD	Kombi	Allrad	Benzin/Erdgas (CNG)	127	173	Apr 2013	Dec 2014	2024-03-01	133961
Subaru	Outback	2.5 CNG AWD	Kombi	Allrad	Benzin/Erdgas (CNG)	127	173	Jun 2014	Dec 2014	2024-03-01	133962
Land Rover	Range rover iv	3.0 Sdv6 4X4	SUV	Allrad	Diesel	215	292	Oct 2012	Sep 2021	2025-02-03	133963
Subaru	Outback	2.5 Bifuel AWD	Kombi	Allrad	Benzin/Autogas (LPG)	127	173	Jan 2013	Dec 2014	2024-03-01	133964
KIA	Sportage iii	2.0 Cvvt AWD	SUV	Allrad	Benzin	113	154	Nov 2014	Dec 2015	2024-03-01	133966
KIA	Sportage iii	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	99	135	Jan 2014	Dec 2015	2024-03-01	133969
Subaru	Outback	2.5 Bifuel AWD	Kombi	Allrad	Benzin/Autogas (LPG)	123	167	Jan 2010	Dec 2014	2024-03-01	133970
KIA	Sportage iv	2.0 Crdi	SUV	Frontantrieb	Diesel	136	185	Sep 2015	Sep 2022	2024-03-01	133975
DS	Ds	1.2 Puretech 100	Schrägheck	Frontantrieb	Benzin	74	101	Oct 2018	-	2024-03-01	133978
DS	Ds	1.2 Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Oct 2018	-	2024-03-01	133979
DS	Ds	1.2 Puretech 155	Schrägheck	Frontantrieb	Benzin	115	156	Oct 2018	Dec 2022	2024-03-01	133980
DS	Ds	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	75	102	Oct 2018	Dec 2022	2024-03-01	133981
DS	Ds	1.5 Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	130	Oct 2018	-	2025-06-01	133982
Mazda	6	2.5	Stufenheck	Frontantrieb	Benzin	170	231	Mar 2018	-	2024-03-01	133985
KIA	Pro cee'd hatchback van	1.4 Cvvt	Kasten/Schrägheck	Frontantrieb	Benzin	73	99	May 2012	Jul 2018	2024-03-01	133987
BMW	Z4 roadster	Sdrive 20 I	Cabriolet	Heckantrieb	Benzin	120	163	Nov 2018	-	2024-03-01	133990
Mazda	6	2.5	Stufenheck	Frontantrieb	Benzin	140	190	Mar 2018	-	2024-03-01	133991
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	120	163	Nov 2018	Feb 2020	2024-03-01	133993
BMW	3	320 D Xdrive	Stufenheck	Allrad	Diesel	120	163	Nov 2018	Feb 2020	2024-03-01	133994
KIA	Rio iii hatchback van	1.4 Cvvt	Kasten/Schrägheck	Frontantrieb	Benzin	80	109	Apr 2015	-	2024-03-01	133999
BMW	3	M 340 I Xdrive	Stufenheck	Allrad	Benzin	275	374	Jul 2019	-	2024-03-01	134016
KIA	Venga	Cvvt	Kasten/Schrägheck	Frontantrieb	Benzin	66	90	Apr 2015	-	2024-03-01	134018
KIA	Venga	Cvvt	Kasten/Schrägheck	Frontantrieb	Benzin	92	125	Feb 2015	-	2024-03-01	134021
Volvo	Xc60 ii	T4	SUV	Frontantrieb	Benzin	140	190	Sep 2018	Dec 2021	2024-05-01	134022
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	110	150	Mar 2018	-	2024-03-01	134042
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	110	150	Mar 2018	-	2024-03-01	134043
Renault	Megane iii combi van	1.5 DCI	Kasten/Kombi	Frontantrieb	Diesel	81	110	Jan 2009	Aug 2015	2024-03-01	134046
Mercedes-benz	A-Klasse	A 200 D	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2018	-	2024-03-01	134048
Mercedes-benz	A-Klasse	A 220 D	Schrägheck	Frontantrieb	Diesel	140	190	Nov 2018	-	2024-03-01	134049
Renault	Megane iv grandtour	1.3 TCE 100	Kombi	Frontantrieb	Benzin	75	102	Aug 2018	-	2025-06-01	134066
Renault	Megane iv	1.3 TCE 100	Schrägheck	Frontantrieb	Benzin	75	102	Aug 2018	-	2024-03-01	134067
Ford	Focus iv	1.5 Ecoblue	Stufenheck	Frontantrieb	Diesel	88	120	Nov 2018	Nov 2025	2026-02-01	134068
Ford	Focus iv	1.5 Ti-vct	Stufenheck	Frontantrieb	Benzin	90	122	Nov 2018	Nov 2025	2026-02-01	134069
Ford	Focus iv	1.5 Ti-vct	Schrägheck	Frontantrieb	Benzin	90	123	Nov 2018	Nov 2025	2026-02-01	134070
Bentley	Bentayga	4.0 TDI	SUV	Allrad	Diesel	310	421	Nov 2016	-	2024-03-01	134071
Subaru	Forester	2.0 Bifuel AWD	SUV	Allrad	Benzin/Autogas (LPG)	110	150	Jan 2009	Dec 2011	2024-03-01	134072
Subaru	Outback	2.5 Bifuel AWD	Kombi	Allrad	Benzin/Autogas (LPG)	127	173	Sep 2008	Jun 2009	2024-03-01	134074
MIA Electric	Mia	Electric	Schrägheck	Heckantrieb	Elektro	18	24	Jan 2011	Apr 2014	2024-03-01	134076
Subaru	Justy iv	1.0 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	69	Sep 2007	Mar 2012	2024-03-01	134077
KIA	Cerato iv	2.0 MPI	Stufenheck	Frontantrieb	Benzin	110	150	Feb 2018	-	2024-03-01	134079
Citroën	Jumpy i	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	69	Nov 2000	Oct 2006	2024-03-01	134080
Subaru	Impreza station wagon	1.6	Kombi	Frontantrieb	Benzin	70	95	Oct 2000	Sep 2006	2024-03-01	134081
MAN	Tge	Etge	Kasten	Frontantrieb	Elektro	100	136	Jul 2018	-	2024-03-01	134086
MAN	Tge	2.0 TDI	Bus	Frontantrieb	Diesel	75	102	Feb 2017	Jun 2024	2024-05-01	134090
MAN	Tge	2.0 TDI	Bus	Frontantrieb	Diesel	103	140	Feb 2017	-	2024-03-01	134091
MAN	Tge	2.0 TDI AWD	Bus	Allrad	Diesel	103	140	Feb 2017	-	2024-03-01	134092
MAN	Tge	2.0 TDI	Bus	Frontantrieb	Diesel	130	177	Feb 2017	-	2024-03-01	134093
MAN	Tge	2.0 TDI AWD	Bus	Allrad	Diesel	130	177	Feb 2017	-	2024-03-01	134094
Peugeot	5008	1.6 THP 110	Großraumlimousine	Frontantrieb	Benzin	110	150	Jul 2018	-	2024-08-01	134098
Dacia	Dokker	1.6 LPG	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	80	109	Aug 2018	Dec 2021	2024-11-01	134099
Polaris	Slingshot	2.4 VVT	Cabriolet	Heckantrieb	Benzin	127	173	Oct 2014	-	2024-03-01	134105
Renault	Mascott	110	Kasten	Heckantrieb	Diesel	78	106	Jan 1999	Jun 2004	2024-03-01	134106
Renault	Mascott	150	Kasten	Heckantrieb	Diesel	107	145	Jan 1999	Jun 2004	2024-03-01	134107
Renault	Mascott	110	Pritsche/Fahrgestell	Heckantrieb	Diesel	78	106	Jan 1999	Jun 2005	2024-03-01	134108
Ferrari	Monza sp1	6.5	Cabriolet	Heckantrieb	Benzin	596	810	Sep 2018	-	2024-03-01	134110
Ferrari	Monza sp2	6.5	Cabriolet	Heckantrieb	Benzin	596	810	Sep 2018	-	2024-03-01	134111
Mercedes-benz	Sprinter 3-T	308 E	Kasten	Heckantrieb	Elektro	40	54	Jan 1996	May 2006	2024-03-01	134112
Mercedes-benz	Sprinter 3-T	308 E	Pritsche/Fahrgestell	Heckantrieb	Elektro	40	54	Jan 1996	May 2006	2024-03-01	134113
Mazda	Cx-5	2.5	SUV	Frontantrieb	Benzin	143	194	Mar 2019	Nov 2022	2025-06-01	134114
Peugeot	3008 ii	1.6 THP 150	SUV	Frontantrieb	Benzin	110	150	Nov 2017	-	2024-11-01	134117
KIA	Optima	2.0 GDI Hybrid	Kombi	Frontantrieb	Benzin/Elektro	151	205	Apr 2017	Dec 2019	2024-03-01	134129
Peugeot	508 ii	1.6 THP 165	Schrägheck	Frontantrieb	Benzin	121	165	Sep 2018	-	2024-03-01	134175
Peugeot	508 sw ii	1.6 THP 165	Kombi	Frontantrieb	Benzin	121	165	Sep 2018	-	2024-03-01	134176
Volvo	Xc40	T5 AWD	SUV	Allrad	Benzin	183	249	Oct 2017	Dec 2022	2024-05-01	134183
Ford	Fiesta v van	1.3	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	May 2002	Aug 2008	2024-03-01	134187
Ford	Mondeo iv van	2.0 Tdci	Kasten/Kombi	Frontantrieb	Diesel	103	140	Mar 2007	Sep 2014	2024-03-01	134188
Saab	9-3	2.0 T16	Kombi	Frontantrieb	Benzin	143	194	Apr 2006	Feb 2015	2024-03-01	134195
Saab	9-3	2.0 T16	Stufenheck	Frontantrieb	Benzin	143	194	Jun 2006	Feb 2015	2024-03-01	134196
UAZ	Patriot	2.7	SUV	Allrad	Benzin	110	150	Oct 2018	-	2024-03-01	134199
UAZ	Pickup	2.7 4X4	Pick-up	Allrad	Benzin	110	150	Oct 2018	-	2024-03-01	134200
UAZ	Hunter	2.7	Geländewagen geschlossen	Allrad	Benzin	99	135	Feb 2018	-	2024-03-01	134201
Honda	Civic x	1.0 Ivtec	Stufenheck	Frontantrieb	Benzin	93	126	Jul 2018	Dec 2022	2024-03-01	134214
Volvo	V60 ii	D4 Polestar	Kombi	Frontantrieb	Diesel	147	200	Feb 2018	Dec 2021	2024-05-01	134215
VW	Arteon	2.0 TSI 4motion	Schrägheck	Allrad	Benzin	200	272	Apr 2018	-	2025-12-01	134219
Lifan	Myway	1.8	SUV	Heckantrieb	Benzin	92	125	Sep 2018	-	2024-03-01	134222
Lifan	X70	2.0 VVT	SUV	Frontantrieb	Benzin	100	136	Apr 2018	-	2024-03-01	134223
Aston Martin	Db11 vantage	5.2 AMR	Coupe	Heckantrieb	Benzin	470	639	Oct 2018	-	2024-03-01	134226
Honda	Cr-V v	2.0 E-cvt Hybrid	SUV	Frontantrieb	Benzin/Elektro	158	215	Dec 2018	-	2024-03-01	134227
Mazda	Cx-5	2.0 Skyactiv-g	SUV	Frontantrieb	Benzin	120	163	Mar 2018	-	2024-03-01	134229
Mazda	Cx-5	2.0 Skyactiv-g AWD	SUV	Allrad	Benzin	120	163	Mar 2018	-	2024-03-01	134230
Seat	Ateca	1.5 TSI 4drive	SUV	Allrad	Benzin	110	150	Jul 2018	-	2024-03-01	134232
Pagani	Zonda	6	Coupe	Heckantrieb	Benzin	294	400	Jun 1999	May 2002	2024-03-01	134233
Pagani	Zonda	6	Coupe	Heckantrieb	Benzin	551	749	Jun 2009	-	2024-03-01	134234
Pagani	Zonda	6	Coupe	Heckantrieb	Benzin	588	799	Jun 2013	Dec 2013	2024-03-01	134235
Pagani	Zonda	6	Coupe	Heckantrieb	Benzin	331	450	Jun 1999	May 2002	2024-03-01	134236
Mercedes-benz	B-Klasse sports tourer	B 200 D	Schrägheck	Frontantrieb	Diesel	110	150	Dec 2018	-	2024-03-01	134237
Mercedes-benz	B-Klasse sports tourer	B 220 D	Schrägheck	Frontantrieb	Diesel	140	190	Dec 2018	-	2024-03-01	134238
Mercedes-benz	B-Klasse sports tourer	B 180	Schrägheck	Frontantrieb	Benzin	100	136	Dec 2018	-	2024-03-01	134242
Mercedes-benz	B-Klasse sports tourer	B 200	Schrägheck	Frontantrieb	Benzin	120	163	Dec 2018	-	2024-03-01	134243
VW	Touareg	3.0 TDI 4motion	SUV	Allrad	Diesel	183	249	Jan 2018	Nov 2023	2024-03-01	134244
Mercedes-benz	S-Klasse	S 63 AMG	Coupe	Heckantrieb	Benzin	450	612	Dec 2018	Jul 2020	2024-03-01	134245


--- Round 1 / 首次发送 ---
## 更新点

* 按缓存优先完成 48 个输入 Ktype，共新增 49 条 READY 映射；`134070` 因覆盖 Focus IV 改款前后两套外廓，拆分为两条派生映射。
* 复用 26 个已有尺寸组；首次闭合 9 个尺寸组，包括 W212 facelift、DS 3 Crossback、BMW Z4 G29、Polaris Slingshot、Ferrari Monza SP1/SP2、DB11 AMR、B-Class W247 和 C217 S 63 Coupé。新建组的三维及不含后视镜宽度已由对应车型资料闭合。
* `134098` 根据第二代 Peugeot 5008 的实际物理车身归一为 SUV；货运版 Rio、Venga 复用对应五门车身尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：49 条，覆盖 48 个 Ktype
* PENDING Ktype：52
* 已引用并闭合尺寸组：35 个
* 本轮首次创建尺寸组：9 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133936	133936	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
133955	133955	Sedan	E-Class W212 Facelift	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH		READY
133975	133975	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
133978	133978	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133979	133979	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133980	133980	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133981	133981	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133982	133982	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133985	133985	Sedan	Mazda 6 III Facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH		READY
133990	133990	Convertible	Z4 III	G29	2	EU-BMW-Z4-III-G29-CONVERTIBLE-01	HIGH		READY
133991	133991	Sedan	Mazda 6 III Facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH		READY
133993	133993	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	改款前后驱外廓。	READY
133994	133994	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	改款前xDrive外廓。	READY
133999	133999	Van	Rio III	UB	5	EU-KIA-RIO-III-HATCHBACK-01	HIGH	货运版沿用五门车身外廓。	READY
134018	134018	Van	Venga Facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	货运版沿用五门车身外廓。	READY
134021	134021	Van	Venga Facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	货运版沿用五门车身外廓。	READY
134022	134022	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
134042	134042	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134043	134043	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134048	134048	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
134049	134049	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
134066	134066	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
134067	134067	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
134070_prefl	134070	Hatchback	Focus IV Pre-Facelift	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门外廓。	READY
134070_facelift	134070	Hatchback	Focus IV Facelift	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门外廓。	READY
134071	134071	SUV	Bentayga I	4V	5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
134079	134079	Sedan	Cerato IV	BD	4	EU-KIA-CERATO-IV-BD-SEDAN-01	HIGH		READY
134098	134098	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入车身类型按第二代5008实际SUV外廓归一。	READY
134105	134105	Convertible	Slingshot I		0	EU-POLARIS-SLINGSHOT-I-ROADSTER-01	HIGH	三轮双座开放式车身。	READY
134110	134110	Convertible	Monza SP		2	EU-FERRARI-MONZA-SP1-CONVERTIBLE-01	HIGH	SP1单座座舱外廓。	READY
134111	134111	Convertible	Monza SP		2	EU-FERRARI-MONZA-SP2-CONVERTIBLE-01	HIGH	SP2双座座舱外廓。	READY
134114	134114	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134117	134117	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
134129	134129	Wagon	Optima IV	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
134175	134175	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门Fastback外廓。	READY
134176	134176	Wagon	508 II	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
134183	134183	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
134214	134214	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH		READY
134215	134215	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
134219	134219	Liftback	Arteon I Pre-Facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	272 PS版本对应改款前外廓。	READY
134226	134226	Coupe	DB11 I		2	EU-ASTON-MARTIN-DB11-AMR-COUPE-01	HIGH	AMR外廓。	READY
134227	134227	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-FWD-01	HIGH	前驱外廓。	READY
134229	134229	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134230	134230	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134237	134237	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134238	134238	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134242	134242	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134243	134243	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134245	134245	Coupe	S-Class Coupe Facelift	C217	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	HIGH	AMG S 63改款后双门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474	Mercedes-Benz E-Class Saloon and Estate official brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/E-Class_saloon_estate_W212_S212_0413.pdf
EU-DS-DS3-CROSSBACK-I-SUV-01	4118	1791	1534	DS Automobiles DS 3 CROSSBACK official press release	https://www.media.stellantis.com/uk-en/ds/press/ds-3-crossback-icon-of-high-tech-style
EU-BMW-Z4-III-G29-CONVERTIBLE-01	4324	1864	1304	BMW Group PressClub Z4 sDrive20i technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0329593EN/476180
EU-POLARIS-SLINGSHOT-I-ROADSTER-01	3800	1960	1318	Polaris Slingshot official owner's manual specifications	https://cdn.polarisportal.com/servicemanagement-public/OwnerManuals/9928978/SLINGSHOTSLINGSHOTSLSLINGSHOTSLRSLI-71E25B1E.html
EU-FERRARI-MONZA-SP1-CONVERTIBLE-01	4657	1996	1155	Ferrari Monza SP1 and SP2 official technical sheet	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/180016_car_ferrari_monza_sp1_sp2_en1.pdf
EU-FERRARI-MONZA-SP2-CONVERTIBLE-01	4657	1996	1155	Ferrari Monza SP1 and SP2 official technical sheet	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/180016_car_ferrari_monza_sp1_sp2_en1.pdf
EU-ASTON-MARTIN-DB11-AMR-COUPE-01	4750	1950	1290	Aston Martin DB11 AMR official press release	https://media.astonmartin.com/db11-amr-new-performance-flagship-of-the-db11-range
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247 specifications	https://www.auto-data.net/en/mercedes-benz-b-class-model-1363
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424	Automobile-Catalog Mercedes-AMG S 63 4MATIC+ Coupe specifications	https://www.automobile-catalog.com/car/2017/2603030/mercedes-amg_s_63_4matic_plus_coupe.html
```

## 下一步优先处理

1. 集中闭合 Kia 旧代际组：Optima TF、Rio II、Sorento II 改款边界、Sportage II/III、Pro cee'd。
2. 批量处理 Subaru Legacy、Outback、Forester、Justy、Impreza，优先确认跨改款 Ktype 是否需要派生。
3. 随后处理 MAN TGE Bus/eTGE、Citroën Jumpy I、Renault Mascott、Mercedes Sprinter 等多轴距、多车顶商用车分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 15 个 Ktype，新增 17 条 READY 映射；`134068`、`134069` 均覆盖 Focus IV 四门轿车改款前后两套外廓，已分别派生。福克斯两阶段尺寸采用官方资料闭合。([Szilcar][1])
* 复用 BMW G20 xDrive 改款前尺寸组和 VW Touareg III CR 尺寸组；首次创建 12 个尺寸组。
* 新建尺寸组覆盖 Optima TF、Sportage III facelift、Mia、Dokker、Ateca AWD、UAZ 三种车身及 Lifan 两款 SUV。
* UAZ 与 Lifan 三维采用对应品牌资料，其中宽度均按不含后视镜口径落盘。([UAZ][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：66 条，覆盖 63 个 Ktype
* PENDING Ktype：37
* 已引用并闭合尺寸组：48 个
* 本轮首次创建尺寸组：12 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133937	133937	Sedan	Optima III	TF	4	EU-KIA-OPTIMA-III-TF-SEDAN-01	HIGH		READY
133966	133966	SUV	Sportage III Facelift	SL	5	EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	HIGH		READY
133969	133969	SUV	Sportage III Facelift	SL	5	EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	HIGH		READY
134016	134016	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
134068_prefl	134068	Sedan	Focus IV Pre-Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前四门外廓。	READY
134068_facelift	134068	Sedan	Focus IV Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后四门外廓。	READY
134069_prefl	134069	Sedan	Focus IV Pre-Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前四门外廓。	READY
134069_facelift	134069	Sedan	Focus IV Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后四门外廓。	READY
134076	134076	Hatchback	Mia		3	EU-MIA-ELECTRIC-MIA-HATCHBACK-01	HIGH		READY
134099	134099	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
134199	134199	SUV	Patriot		5	EU-UAZ-PATRIOT-SUV-01	HIGH		READY
134200	134200	Pickup	Pickup		4	EU-UAZ-PICKUP-PICKUP-01	HIGH		READY
134201	134201	SUV	Hunter		3	EU-UAZ-HUNTER-SUV-HARDTOP-01	HIGH	硬顶封闭车身。	READY
134222	134222	SUV	Myway		5	EU-LIFAN-MYWAY-SUV-01	HIGH		READY
134223	134223	SUV	X70		5	EU-LIFAN-X70-SUV-01	HIGH		READY
134232	134232	SUV	Ateca I Pre-Facelift	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-PREFL-AWD-01	HIGH		READY
134244	134244	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-OPTIMA-III-TF-SEDAN-01	4845	1830	1455	Kia Optima official brochure	https://www.kia.com/content/dam/kwcms/aw/en/pdf/Optima-brochure.pdf
EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	4440	1855	1630	Kia Europe Geneva 2014 enhanced Sportage technical specifications	https://press.kia.com/content/dam/kiapress/EU/download-files/english/Geneva-2014-Enhanced-Kia-Sportage.doc
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471	Ford Focus 2019.5MY official brochure	https://www.fordszilcar.sk/sites/default/files/2020-10/FOCUS_2019.5MY_SK.pdf
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452	Ford Focus December 2025 official technical brochure	https://cdnepws.azureedge.net/getmedia/1ef366f3-90e2-40b3-8796-6ff7dfea6a96/focus-teknikfoy-aralik-2025_1.pdf.aspx
EU-MIA-ELECTRIC-MIA-HATCHBACK-01	2870	1640	1550	Mia electric official brochure	https://www.mia-electric.nl/.cm4all/uproc.php/0/brochure_mia_electric_-_en.pdf?_=190d0c3d879&cdp=a
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Dacia Dokker 2018 official brochure	https://daciast.ams3.cdn.digitaloceanspaces.com/downloads/czechia/cz-brochure-dacia-dokker-2018-02.pdf
EU-UAZ-PATRIOT-SUV-01	4785	1900	1910	UAZ Patriot official brochure	https://www.uaz.ru/data/uploads/uaz/originals/f80bb717-9f45-483c-b178-12d4fd99a562.pdf
EU-UAZ-PICKUP-PICKUP-01	5125	1915	1915	UAZ Pickup official brochure	https://www.uaz.ru/data/uploads/uaz/originals/uaz-pickup-broshure-en-290722.pdf
EU-UAZ-HUNTER-SUV-HARDTOP-01	4050	1775	1950	UAZ Hunter official brochure	https://www.uaz.ru/data/uploads/uaz/originals/b68e7d74-c8f7-47f8-bf3b-08e43e5d4ec5.pdf
EU-LIFAN-MYWAY-SUV-01	4440	1760	1730	Lifan Myway official specifications	https://lifan-car.ru/cars/myway
EU-LIFAN-X70-SUV-01	4390	1820	1715	Lifan X70 official specifications	https://lifan-car.ru/cars/x70
EU-SEAT-ATECA-I-KH7-SUV-PREFL-AWD-01	4363	1841	1611	SEAT Ateca official brochure	https://www.seat.com/content/dam/public/seat-website/myco/2028/car-shopping-tools/brochure-download/brochures/ateca/other-shoppingtools-brochure-ateca-specs-final-october-2019.pdf
```

## 下一步优先处理

1. 批量闭合 Kia Rio II、Sorento II、Sportage II 与 Pro cee'd 货运版。
2. 集中处理 Subaru Legacy、Outback、Forester、Justy 和 Impreza 的代际及改款边界。
3. 随后处理 MAN TGE Bus/eTGE、Citroën Jumpy I、Renault Mascott 与 Mercedes-Benz Sprinter 的轴距、车顶和车身分支。

推进信号：CONTINUE

[1]: https://www.fordszilcar.sk/sites/default/files/2020-10/FOCUS_2019.5MY_SK.pdf "Focus_19.5_EDM_V2_#SF_SVK_SK_EBRO.pdf"
[2]: https://www.uaz.ru/data/uploads/uaz/originals/f80bb717-9f45-483c-b178-12d4fd99a562.pdf?utm_source=chatgpt.com "uaz patriot"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 12 个 Ktype，新增 14 条 READY 映射。
* `133945` 按 Sorento II 改款前后拆分；改款后直接复用已有尺寸组。
* `133970` 按 Outback IV 改款前后拆分；`133962`、`133964` 直接关联改款后尺寸组。
* 首次创建 11 个尺寸组。Kia、Daewoo 与 Subaru 各组的车身边界、三维及不含后视镜宽度已闭合。([Kia Australia][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：80 条，覆盖 75 个 Ktype
* PENDING Ktype：25
* 已引用并闭合尺寸组：59 个
* 本轮首次创建尺寸组：11 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133939	133939	Hatchback	Rio II Facelift	JB	5	EU-KIA-RIO-II-JB-HATCHBACK-01	HIGH		READY
133945_prefl	133945	SUV	Sorento II Pre-Facelift	XM	5	EU-KIA-SORENTO-II-XM-PREFL-SUV-01	HIGH	同一Ktype覆盖改款前外廓。	READY
133945_facelift	133945	SUV	Sorento II Facelift	XM	5	EU-KIA-SORENTO-II-XM-FACELIFT-SUV-01	HIGH	同一Ktype覆盖改款后外廓。	READY
133954	133954	SUV	Sportage II Facelift	KM	5	EU-KIA-SPORTAGE-II-KM-FACELIFT-SUV-01	HIGH		READY
133956	133956	MPV	Rezzo I	KLAU	5	EU-DAEWOO-REZZO-I-KLAU-MPV-01	HIGH		READY
133961	133961	Wagon	Legacy V Station Wagon Facelift	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	HIGH		READY
133962	133962	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH		READY
133964	133964	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH		READY
133970_prefl	133970	Wagon	Outback IV Pre-Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前外廓。	READY
133970_facelift	133970	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后外廓。	READY
133987	133987	Van	Pro cee'd II	JD	3	EU-KIA-PRO-CEED-II-JD-HATCHBACK-3D-01	HIGH	货运版沿用三门车身外廓。	READY
134072	134072	SUV	Forester III Pre-Facelift	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-PREFL-01	HIGH		READY
134074	134074	Wagon	Outback III Facelift	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
134077	134077	Hatchback	Justy IV		5	EU-SUBARU-JUSTY-IV-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-RIO-II-JB-HATCHBACK-01	3990	1695	1470	Automobile-Catalog Kia Rio II 1.4 EX Top specifications	https://www.automobile-catalog.com/car/2010/1354520/kia_rio_1_4_ex_top.html
EU-KIA-SORENTO-II-XM-PREFL-SUV-01	4685	1885	1710	Kia Sorento official brochure	https://www.kia.com/content/dam/kwcms/dm/en/pdf/Sorento-brochure.pdf
EU-KIA-SPORTAGE-II-KM-FACELIFT-SUV-01	4350	1800	1695	CarsGuide 2009 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/2009
EU-DAEWOO-REZZO-I-KLAU-MPV-01	4350	1755	1580	Automobile-Catalog Daewoo Rezzo 1.6 SX specifications	https://www.automobile-catalog.com/car/2002/2056730/daewoo_rezzo_1_6_sx.html
EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	4790	1780	1535	Automobile-Catalog Subaru Legacy Wagon 2.5i specifications	https://www.automobile-catalog.com/car/2013/3290780/subaru_legacy_wagon_2_5i_lineatronic.html
EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	4775	1820	1605	Automobile-Catalog Subaru Outback 2.5i Europe specifications	https://www.automobile-catalog.com/car/2011/3290480/subaru_outback_2_5i.html
EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	4790	1820	1605	Automobile-Catalog Subaru Outback facelift Europe specifications	https://www.automobile-catalog.com/car/2014/3290585/subaru_outback_2_0_d.html
EU-KIA-PRO-CEED-II-JD-HATCHBACK-3D-01	4310	1780	1430	Kia Europe pro_cee'd official press specifications	https://staging-press.kia.com/eu/en/home/models/pro-ceed/pro-ceed-2013.html
EU-SUBARU-FORESTER-III-SH-SUV-PREFL-01	4560	1780	1675	Automobile-Catalog Subaru Forester 2.0 X specifications	https://www.automobile-catalog.com/car/2009/3292085/subaru_forester_2_0_x_awd.html
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545	Automobile-Catalog Subaru Outback 2.5i specifications	https://www.automobile-catalog.com/car/2008/3263750/subaru_outback_2_5_i.html
EU-SUBARU-JUSTY-IV-HATCHBACK-01	3610	1665	1550	Subaru official new Justy news release	https://www.subaru.co.jp/en/news/archives/press/2007/07_09_11e.html
```

## 下一步优先处理

1. 闭合 Range Rover Sport I、Range Rover IV 改款前后以及 Renault Clio IV 货运版。
2. 处理 Renault Megane III Combi Van、Ford Fiesta/Mondeo Van、Saab 9-3 Sedan/Wagon。
3. 集中处理 MAN TGE Bus/eTGE、Citroën Jumpy I、Renault Mascott 和 Mercedes-Benz Sprinter 的轴距、车顶及车身分支。

推进信号：CONTINUE

[1]: https://www.kia.com/content/dam/kwcms/dm/en/pdf/Sorento-brochure.pdf?utm_source=chatgpt.com "Kia Motors Corporation"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 7 个 Ktype，新增 9 条 READY 映射；`133957`、`133963` 按改款前后物理外廓拆分。
* `133963` 改款后 SDV6 的尺寸为 `5000×1983×1836 mm`，与累计索引中的 facelift `-01` 高度 `1869 mm` 不一致，因此未覆盖旧组，按规则新建 `EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02`。([汽车数据][1])
* `134234`、`134235` 分别确认是 Zonda R 和 Zonda Revolución，而不是公路版 Cinque；两者虽三维相同，但空气动力学外部结构不同，分别建组。Pagani 官方资料确认二者均为 `4886×2014×1141 mm`。([Pagani][2])
* `134233` 与 `134236` 分别对应早期 Zonda C12 和 C12-S，复用同一早期 Coupé 外廓尺寸组。([Pagani][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：89 条，覆盖 82 个 Ktype
* PENDING Ktype：18
* 已引用并闭合尺寸组：67 个
* 本轮首次创建尺寸组：7 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133957_prefl	133957	Van	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	HIGH	货运版沿用改款前五门车身外廓。	READY
133957_facelift	133957	Van	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	货运版沿用改款后五门车身外廓。	READY
133959	133959	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	HIGH	4.2升版本对应改款前外廓。	READY
133963_prefl	133963	SUV	Range Rover IV Pre-Facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	HIGH	同一Ktype覆盖改款前标准轴距外廓。	READY
133963_facelift	133963	SUV	Range Rover IV Facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	同一Ktype覆盖改款后SDV6标准轴距外廓。	READY
134233	134233	Coupe	Zonda C12		2	EU-PAGANI-ZONDA-C12-C12S-COUPE-01	HIGH	早期C12 Coupé外廓。	READY
134234	134234	Coupe	Zonda R		2	EU-PAGANI-ZONDA-R-COUPE-01	HIGH	750 PS赛道版Zonda R外廓。	READY
134235	134235	Coupe	Zonda Revolucion		2	EU-PAGANI-ZONDA-REVOLUCION-COUPE-01	HIGH	800 PS Zonda Revolución赛道外廓。	READY
134236	134236	Coupe	Zonda C12-S		2	EU-PAGANI-ZONDA-C12-C12S-COUPE-01	HIGH	C12-S与早期C12共用物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448	Automobile-Catalog Renault Clio IV specifications	https://www.automobile-catalog.com/car/2015/2983490/renault_clio_energy_dci_75.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	4788	1928	1812	Automobile-Catalog Range Rover Sport V8 Supercharged HSE specifications	https://www.automobile-catalog.com/car/2007/1404935/range_rover_sport_v8_supercharged_hse.html
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836	Auto-Data Range Rover IV specifications	https://www.auto-data.net/en/land-rover-range-rover-model-562
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836	Automobile-Catalog Range Rover 3.0 SDV6 275 specifications	https://www.automobile-catalog.com/car/2018/2875685/range_rover_3_0_sdv6_275.html
EU-PAGANI-ZONDA-C12-C12S-COUPE-01	4395	2055	1151	Pagani Zonda C12 official specifications; Pagani Zonda S official specifications	https://www.pagani.com/zonda-c12/;https://www.pagani.com/zonda-s/
EU-PAGANI-ZONDA-R-COUPE-01	4886	2014	1141	Pagani Zonda R official specifications	https://www.pagani.com/zonda-r/
EU-PAGANI-ZONDA-REVOLUCION-COUPE-01	4886	2014	1141	Pagani Zonda Revolución official specifications	https://www.pagani.com/zonda-revolucion/
```

## 下一步优先处理

1. 闭合 Subaru Impreza II Wagon、Renault Megane III Combi Van 的改款分支。
2. 处理 Ford Fiesta V Van、Mondeo IV Van 与 Saab 9-3 Sedan/SportCombi 的改款前后外廓。
3. 最后集中处理 Jumpy I、MAN TGE Bus/eTGE、Mascott 与 Sprinter 的轴距、车顶和底盘分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/land-rover-range-rover-model-562?utm_source=chatgpt.com "Specs for all generations of Land Rover Range Rover"
[2]: https://www.pagani.com/zonda-r/ "Zonda R | Pagani"
[3]: https://www.pagani.com/zonda-c12/ "Zonda C12 | Pagani"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 5 个 Ktype，新增 8 条 READY 映射。
* `134046` 的 Mégane III Combi Van 复用 Grandtour 五门旅行车外廓；该外廓为 `4559×1804×1507 mm`。([汽车目录][1])
* `134086` 确认为标准长度高顶 eTGE，直接复用已有 `EU-MAN-TGE-I-VAN-L3H3-01`，不重复建立尺寸组。([MAN Global][2])
* `134188` 按 Mondeo IV 旅行车改款前后拆分，车长分别为 4830 mm 和 4837 mm，宽度及高度不变。([汽车目录][3])
* `134195`、`134196` 分别按 Saab 9-3 SportCombi 和 Sport Sedan 改款前后拆分。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：97 条，覆盖 87 个 Ktype
* PENDING Ktype：13
* 已引用并闭合尺寸组：74 个
* 本轮首次创建尺寸组：7 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134046	134046	Van	Megane III Grandtour		5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	货运版沿用Grandtour五门旅行车外廓。	READY
134086	134086	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	eTGE标准长度高顶厢式车外廓。	READY
134188_prefl	134188	Van	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	货运版沿用改款前旅行车外廓。	READY
134188_facelift	134188	Van	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	货运版沿用改款后旅行车外廓。	READY
134195_prefl	134195	Wagon	9-3 II Pre-Facelift	YS3F	5	EU-SAAB-9-3-II-YS3F-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前SportCombi外廓。	READY
134195_facelift	134195	Wagon	9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-YS3F-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后SportCombi外廓。	READY
134196_prefl	134196	Sedan	9-3 II Pre-Facelift	YS3F	4	EU-SAAB-9-3-II-YS3F-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前Sport Sedan外廓。	READY
134196_facelift	134196	Sedan	9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-YS3F-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后Sport Sedan外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Automobile-Catalog Renault Megane Estate Grandtour 1.5 dCi 110 specifications	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	4830	1886	1512	Automobile-Catalog Ford Mondeo Estate 2.0 TDCi 140 specifications	https://www.automobile-catalog.com/car/2007/979130/ford_mondeo_estate_2_0_tdci_140_zetec.html
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Automobile-Catalog Ford Mondeo Turnier 2.0 TDCi 140 specifications	https://www.automobile-catalog.com/car/2011/1595885/ford_mondeo_5-dr_2_0_tdci_140_trend_powershift.html
EU-SAAB-9-3-II-YS3F-WAGON-PREFL-01	4654	1762	1490	Automobile-Catalog Saab 9-3 2.0T SportCombi specifications	https://www.automobile-catalog.com/car/2007/3036140/saab_9-3_2_0t_sportcombi.html
EU-SAAB-9-3-II-YS3F-WAGON-FACELIFT-01	4670	1762	1498	Automobile-Catalog Saab 9-3 2.0t SportCombi specifications	https://www.automobile-catalog.com/car/2010/3037040/saab_9-3_2_0t_sportcombi.html
EU-SAAB-9-3-II-YS3F-SEDAN-PREFL-01	4635	1762	1467	Automobile-Catalog Saab 9-3 2.0t Sport Sedan specifications	https://www.automobile-catalog.com/car/2006/3035855/saab_9-3_2_0t_sport.html
EU-SAAB-9-3-II-YS3F-SEDAN-FACELIFT-01	4647	1762	1450	Automobile-Catalog Saab 9-3 2.0T Sport Sedan specifications	https://www.automobile-catalog.com/car/2010/3037970/saab_9-3_2_0t.html
```

## 下一步优先处理

1. 闭合 Subaru Impreza II Wagon 的三次前脸阶段，以及 Ford Fiesta V Van 改款边界。
2. 集中拆分五个 MAN TGE Bus Ktype 的标准、长轴和车顶组合。
3. 最后处理 Citroën Jumpy I、Renault Mascott 和 Mercedes-Benz Sprinter 的厢式车及底盘分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html?utm_source=chatgpt.com "2009 Renault Megane Estate (Grandtour) 1.5 dCi 110 FAP ..."
[2]: https://www.man.eu/ntg_media/media/en/content_medien/doc/bw_master/truck_2/industry_1/man_lkw_branchen_agrar.pdf?utm_source=chatgpt.com "POWERFUL. ROBUST."
[3]: https://www.automobile-catalog.com/car/2007/977915/ford_mondeo_estate_1_8_tdci_125_edge_6-speed.html?utm_source=chatgpt.com "2007 Ford Mondeo Estate 1.8 TDCi (125) Edge 6-speed Specs Review (92 kW / 125 PS / 123 hp) (since mid-year 2007 for Europe )"
[4]: https://www.automobile-catalog.com/car/2007/3036140/saab_9-3_2_0t_sportcombi.html?utm_source=chatgpt.com "2007 Saab 9-3 2.0T SportCombi Specs Review (154.5 kW / 210 PS / 207 hp) (up to Autumn 2007 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 2 个 Ktype，新增 5 条 READY 映射。
* `134081` 覆盖 Impreza II Wagon 三次前脸阶段，分别拆分为改款前、2002 年改款和 2005 年改款外廓；对应车长依次为 4405、4415、4465 mm，宽度均为不含后视镜的 1695 mm。([汽车目录][1])
* `134187` 为 Fiesta 三门货运车身，按改款前后拆分；两阶段尺寸分别为 `3917×1683×1467 mm` 和 `3918×1721×1468 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：102 条，覆盖 89 个 Ktype
* PENDING Ktype：11
* 已引用并闭合尺寸组：79 个
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134081_prefl	134081	Wagon	Impreza II Pre-Facelift	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-PREFL-01	MEDIUM	改款前三维外廓；输入驱动字段差异不改变车身边界。	READY
134081_facelift_2002	134081	Wagon	Impreza II Facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2002-01	MEDIUM	2002年改款五门旅行车外廓。	READY
134081_facelift_2005	134081	Wagon	Impreza II Facelift 2005	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2005-01	MEDIUM	2005年改款五门旅行车外廓。	READY
134187_prefl	134187	Van	Fiesta V Pre-Facelift	JC3	3	EU-FORD-FIESTA-V-JC3-VAN-PREFL-01	HIGH	改款前三门货运车身外廓。	READY
134187_facelift	134187	Van	Fiesta V Facelift	JC3	3	EU-FORD-FIESTA-V-JC3-VAN-FACELIFT-01	HIGH	改款后三门货运车身外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-IMPREZA-II-GG-WAGON-PREFL-01	4405	1695	1485	Automobile-Catalog Subaru Impreza Sports Wagon 1.6 TS AWD 2001 specifications	https://www.automobile-catalog.com/car/2001/3255650/subaru_impreza_sports_wagon_1_6_ts_awd.html
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2002-01	4415	1695	1465	Automobile-Catalog Subaru Impreza Sports Wagon 1.6 TS AWD 2003 specifications	https://www.automobile-catalog.com/car/2003/3255785/subaru_impreza_sports_wagon_1_6_ts_awd.html
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2005-01	4465	1695	1485	Automobile-Catalog Subaru Impreza Sports Wagon 1.5R 4WD 2006 specifications	https://www.automobile-catalog.com/car/2006/3256115/subaru_impreza_sports_wagon_1_5r_4wd.html
EU-FORD-FIESTA-V-JC3-VAN-PREFL-01	3917	1683	1467	Ford Fiesta Van official brochure archived copy	https://manuals.plus/m/7218d31c7755745164911cb2826b7a226d785b6c13d9176ee306d168ced6b2c2
EU-FORD-FIESTA-V-JC3-VAN-FACELIFT-01	3918	1721	1468	Ford commercial vehicle range official brochure archived copy	https://manuals.plus/m/968094e06d7f3c43af8268ba976de918466003510008e734a4857625a8b61f0e
```

## 下一步优先处理

1. 集中拆分 `134090–134094` 五个 MAN TGE Bus Ktype 的长度、车顶及驱动组合。
2. 闭合 `134106–134108` Renault Mascott 厢式车和底盘的轴距、车顶分支。
3. 最后处理 `134080` Jumpy I 底盘以及 `134112–134113` Sprinter 308 E 厢式车和底盘分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/3255650/subaru_impreza_sports_wagon_1_6_ts_awd.html?utm_source=chatgpt.com "2001 Subaru Impreza Sports Wagon 1.6 TS AWD (man. 5)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 `134091`、`134093` 两个 MAN TGE Bus Ktype，共新增 6 条 READY 映射。
* 两个 Ktype 均覆盖标准轴距普通顶、标准轴距高顶和长轴高顶三种乘用车身外廓；官方技术资料确认 103 kW、130 kW 前驱 Kombi 可对应这三种尺寸配置。([MAN вантажівки][1])
* 三种外廓全部复用已有尺寸组，本轮未创建或修正 DIMENSION_GROUP。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：108 条，覆盖 91 个 Ktype
* PENDING Ktype：9
* 已引用并闭合尺寸组：81 个
* 本轮首次创建尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134091_swb_lowroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶乘用车身外廓。	READY
134091_swb_highroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶乘用车身外廓。	READY
134091_lwb_highroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶乘用车身外廓。	READY
134093_swb_lowroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶乘用车身外廓。	READY
134093_swb_highroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶乘用车身外廓。	READY
134093_lwb_highroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶乘用车身外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 核对 `134090` 的 75 kW 前驱 Bus，以及 `134092`、`134094` 的四驱 Bus 是否存在原厂独立车身组合。
2. 集中拆分 `134106–134108` Renault Mascott 厢式车和底盘的轴距、车顶分支。
3. 闭合 `134080` Citroën Jumpy I 底盘，以及 `134112–134113` Sprinter 308 E 厢式车和底盘分支。

推进信号：CONTINUE

[1]: https://man-motors.com.ua/assets/media/d-pdf/man-tge-technical-data.pdf "MAN_Technische_Daten_TGE_EN_2019.indd"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 `134090`、`134092`、`134094` 三个 MAN TGE Bus Ktype，新增 9 条 READY 映射。
* `134090` 的 75 kW 前驱版本覆盖标准轴距普通顶、标准轴距高顶和长轴高顶，复用已有前驱尺寸组。
* `134092`、`134094` 的四驱车身高度高于对应前驱车型：普通顶为 2390 mm，高顶为 2625 mm。因此未复用高度分别为 2355 mm、2590 mm 的既有组，新建三个四驱尺寸组；两种发动机功率共用相同物理外廓。官方资料同时列明 103/130 kW 四驱动力配置、2040 mm 不含后视镜宽度及各车顶高度。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：117 条，覆盖 94 个 Ktype
* PENDING Ktype：6
* 已引用并闭合尺寸组：84 个
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134090_swb_lowroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶前驱乘用车身外廓。	READY
134090_swb_highroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶前驱乘用车身外廓。	READY
134090_lwb_highroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶前驱乘用车身外廓。	READY
134092_swb_lowroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-AWD-01	HIGH	标准轴距普通顶四驱乘用车身外廓。	READY
134092_swb_highroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-AWD-01	HIGH	标准轴距高顶四驱乘用车身外廓。	READY
134092_lwb_highroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-AWD-01	HIGH	长轴高顶四驱乘用车身外廓。	READY
134094_swb_lowroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-AWD-01	HIGH	标准轴距普通顶四驱乘用车身外廓。	READY
134094_swb_highroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-AWD-01	HIGH	标准轴距高顶四驱乘用车身外廓。	READY
134094_lwb_highroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-AWD-01	HIGH	长轴高顶四驱乘用车身外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAN-TGE-I-VAN-L3H2-AWD-01	5986	2040	2390	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H3-AWD-01	5986	2040	2625	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H3-AWD-01	6836	2040	2625	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
```

## 下一步优先处理

1. 集中闭合 `134106–134108` Renault Mascott：两个厢式车 Ktype 的短轴/长轴分支及底盘 Ktype 的四种轴距。
2. 处理 `134112–134113` Mercedes-Benz Sprinter 308 E 的厢式车和底盘分支。
3. 最后闭合 `134080` Citroën Jumpy I 底盘车型；归零后立即执行机械校验并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 `134080`、`134106`、`134107` 三个 Ktype，新增 5 条 READY 映射和 3 个尺寸组。
* `134080` 确认为 Jumpy I 短轴平台驾驶室；同平台 Peugeot Expert PHC 230C 的外廓为 `4430×1810×1930 mm`，轴距 2824 mm。([AutoScout24][1])
* Mascott I Phase I 厢式车确认存在两种外廓：L1 为 `6163×2062×2832 mm`，L2 为 `6663×2062×2832 mm`；110 与 150 动力版本直接共用这两组。([Дром][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：122 条，覆盖 97 个 Ktype
* PENDING Ktype：3
* 已引用并闭合尺寸组：87 个
* 本轮首次创建尺寸组：3 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134080	134080	Pickup	Jumpy I		2	EU-CITROEN-JUMPY-I-PLATFORM-CAB-01	MEDIUM	短轴平台驾驶室外廓。	READY
134106_l1	134106	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	MEDIUM	同一Ktype覆盖L1厢式外廓。	READY
134106_l2	134106	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	MEDIUM	同一Ktype覆盖L2厢式外廓。	READY
134107_l1	134107	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	MEDIUM	同一Ktype覆盖L1厢式外廓。	READY
134107_l2	134107	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	MEDIUM	同一Ktype覆盖L2厢式外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-I-PLATFORM-CAB-01	4430	1810	1930	AutoScout24 Peugeot Expert PHC 230C equivalent platform-cab specifications; TecDoc Citroën Jumpy I 1.9 TD platform/chassis boundary	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/expert/expert-phc-230c-2-0-hdi-95-utilitaire-diesel-2904/;https://uus.lakinet.ee/tecdoc/articles/en/p/21/4684/134080/100113
EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	6163	2062	2832	Drom Renault Mascott Phase I van dimensions	https://www.drom.ru/catalog/lcv/renault/mascott/specs/dimensions/
EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	6663	2062	2832	Drom Renault Mascott Phase I van dimensions	https://www.drom.ru/catalog/lcv/renault/mascott/specs/dimensions/
```

## 下一步优先处理

1. 拆分 `134108` Mascott 110 平台/底盘的单排、双排驾驶室及轴距分支。
2. 闭合 `134112` Sprinter 308 E 3550 mm 轴距厢式车的普通顶和高顶外廓。
3. 闭合 `134113` Sprinter 308 E 的 `903.312` 单排驾驶室和 `903.322` 双排驾驶室底盘分支；归零后立即生成最终两张完整 TSV 与指定下载文件。

推进信号：CONTINUE

[1]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/expert/expert-phc-230c-2-0-hdi-95-utilitaire-diesel-2904/?utm_source=chatgpt.com "Peugeot EXPERT PHC 230C 2.0 HDI 95 | Utilitaire | 2004-2007 - Spécifications techniques"
[2]: https://www.drom.ru/catalog/lcv/renault/mascott/specs/dimensions/ "Размеры Рено Маскот и вес. Какие габариты Renault Mascott?"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3201-3300_ktype_dimension_mapping_final.tsv
- all_3201-3300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 最后 3 个待处理 Ktype 已闭合：`134108` 拆分为 3 个 Mascott 底盘轴距分支；`134112` 拆分为 Sprinter 903.362 普通顶与高顶厢式车；`134113` 拆分为 903.312 单排和 903.322 双排驾驶室底盘。Mascott 三个轴距配置和 Sprinter 车身代码边界均已对应到完整尺寸组。([Zoomcar][1])
* 本轮新增 7 条 READY 映射、7 个尺寸组。
* 已完成固定表头、唯一性、引用闭合、正整数三维、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：129 条，覆盖 100 个 Ktype
* PENDING：0
* DIMENSION_GROUP：96 个
* 映射引用闭合：通过
* 唯一性检查：通过
* 最终机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133936	133936	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH		READY
133937	133937	Sedan	Optima III	TF	4	EU-KIA-OPTIMA-III-TF-SEDAN-01	HIGH		READY
133939	133939	Hatchback	Rio II Facelift	JB	5	EU-KIA-RIO-II-JB-HATCHBACK-01	HIGH		READY
133945_prefl	133945	SUV	Sorento II Pre-Facelift	XM	5	EU-KIA-SORENTO-II-XM-PREFL-SUV-01	HIGH	同一Ktype覆盖改款前外廓。	READY
133945_facelift	133945	SUV	Sorento II Facelift	XM	5	EU-KIA-SORENTO-II-XM-FACELIFT-SUV-01	HIGH	同一Ktype覆盖改款后外廓。	READY
133954	133954	SUV	Sportage II Facelift	KM	5	EU-KIA-SPORTAGE-II-KM-FACELIFT-SUV-01	HIGH		READY
133955	133955	Sedan	E-Class W212 Facelift	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	HIGH		READY
133956	133956	MPV	Rezzo I	KLAU	5	EU-DAEWOO-REZZO-I-KLAU-MPV-01	HIGH		READY
133957_prefl	133957	Van	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	HIGH	货运版沿用改款前五门车身外廓。	READY
133957_facelift	133957	Van	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	货运版沿用改款后五门车身外廓。	READY
133959	133959	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	HIGH	4.2升版本对应改款前外廓。	READY
133961	133961	Wagon	Legacy V Station Wagon Facelift	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	HIGH		READY
133962	133962	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH		READY
133963_prefl	133963	SUV	Range Rover IV Pre-Facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	HIGH	同一Ktype覆盖改款前标准轴距外廓。	READY
133963_facelift	133963	SUV	Range Rover IV Facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	同一Ktype覆盖改款后SDV6标准轴距外廓。	READY
133964	133964	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH		READY
133966	133966	SUV	Sportage III Facelift	SL	5	EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	HIGH		READY
133969	133969	SUV	Sportage III Facelift	SL	5	EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	HIGH		READY
133970_prefl	133970	Wagon	Outback IV Pre-Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前外廓。	READY
133970_facelift	133970	Wagon	Outback IV Facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后外廓。	READY
133975	133975	SUV	Sportage IV	QL	5	EU-KIA-SPORTAGE-IV-SUV-01	HIGH		READY
133978	133978	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133979	133979	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133980	133980	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133981	133981	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133982	133982	SUV	DS 3 Crossback I	U	5	EU-DS-DS3-CROSSBACK-I-SUV-01	HIGH		READY
133985	133985	Sedan	Mazda 6 III Facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH		READY
133987	133987	Van	Pro cee'd II	JD	3	EU-KIA-PRO-CEED-II-JD-HATCHBACK-3D-01	HIGH	货运版沿用三门车身外廓。	READY
133990	133990	Convertible	Z4 III	G29	2	EU-BMW-Z4-III-G29-CONVERTIBLE-01	HIGH		READY
133991	133991	Sedan	Mazda 6 III Facelift		4	EU-MAZDA-6-III-FACELIFT-SEDAN-01	HIGH		READY
133993	133993	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	改款前后驱外廓。	READY
133994	133994	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH	改款前xDrive外廓。	READY
133999	133999	Van	Rio III	UB	5	EU-KIA-RIO-III-HATCHBACK-01	HIGH	货运版沿用五门车身外廓。	READY
134016	134016	Sedan	3 Series VII	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
134018	134018	Van	Venga Facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	货运版沿用五门车身外廓。	READY
134021	134021	Van	Venga Facelift	YN	5	EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	HIGH	货运版沿用五门车身外廓。	READY
134022	134022	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
134042	134042	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134043	134043	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134046	134046	Van	Megane III Grandtour		5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	货运版沿用Grandtour五门旅行车外廓。	READY
134048	134048	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
134049	134049	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
134066	134066	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
134067	134067	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
134068_prefl	134068	Sedan	Focus IV Pre-Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前四门外廓。	READY
134068_facelift	134068	Sedan	Focus IV Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后四门外廓。	READY
134069_prefl	134069	Sedan	Focus IV Pre-Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前四门外廓。	READY
134069_facelift	134069	Sedan	Focus IV Facelift	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后四门外廓。	READY
134070_prefl	134070	Hatchback	Focus IV Pre-Facelift	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	HIGH	同一Ktype覆盖改款前五门外廓。	READY
134070_facelift	134070	Hatchback	Focus IV Facelift	C519	5	EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype覆盖改款后五门外廓。	READY
134071	134071	SUV	Bentayga I	4V	5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
134072	134072	SUV	Forester III Pre-Facelift	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-PREFL-01	HIGH		READY
134074	134074	Wagon	Outback III Facelift	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
134076	134076	Hatchback	Mia		3	EU-MIA-ELECTRIC-MIA-HATCHBACK-01	HIGH		READY
134077	134077	Hatchback	Justy IV		5	EU-SUBARU-JUSTY-IV-HATCHBACK-01	HIGH		READY
134079	134079	Sedan	Cerato IV	BD	4	EU-KIA-CERATO-IV-BD-SEDAN-01	HIGH		READY
134080	134080	Pickup	Jumpy I		2	EU-CITROEN-JUMPY-I-PLATFORM-CAB-01	MEDIUM	短轴平台驾驶室外廓。	READY
134081_prefl	134081	Wagon	Impreza II Pre-Facelift	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-PREFL-01	MEDIUM	改款前三维外廓；输入驱动字段差异不改变车身边界。	READY
134081_facelift_2002	134081	Wagon	Impreza II Facelift 2002	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2002-01	MEDIUM	2002年改款五门旅行车外廓。	READY
134081_facelift_2005	134081	Wagon	Impreza II Facelift 2005	GG	5	EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2005-01	MEDIUM	2005年改款五门旅行车外廓。	READY
134086	134086	Van	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	eTGE标准长度高顶厢式车外廓。	READY
134090_swb_lowroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶前驱乘用车身外廓。	READY
134090_swb_highroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶前驱乘用车身外廓。	READY
134090_lwb_highroof	134090	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶前驱乘用车身外廓。	READY
134091_swb_lowroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶乘用车身外廓。	READY
134091_swb_highroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶乘用车身外廓。	READY
134091_lwb_highroof	134091	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶乘用车身外廓。	READY
134092_swb_lowroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-AWD-01	HIGH	标准轴距普通顶四驱乘用车身外廓。	READY
134092_swb_highroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-AWD-01	HIGH	标准轴距高顶四驱乘用车身外廓。	READY
134092_lwb_highroof	134092	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-AWD-01	HIGH	长轴高顶四驱乘用车身外廓。	READY
134093_swb_lowroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-01	HIGH	标准轴距普通顶乘用车身外廓。	READY
134093_swb_highroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-01	HIGH	标准轴距高顶乘用车身外廓。	READY
134093_lwb_highroof	134093	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-01	HIGH	长轴高顶乘用车身外廓。	READY
134094_swb_lowroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H2-AWD-01	HIGH	标准轴距普通顶四驱乘用车身外廓。	READY
134094_swb_highroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L3H3-AWD-01	HIGH	标准轴距高顶四驱乘用车身外廓。	READY
134094_lwb_highroof	134094	MPV	TGE I			EU-MAN-TGE-I-VAN-L4H3-AWD-01	HIGH	长轴高顶四驱乘用车身外廓。	READY
134098	134098	SUV	5008 II Phase I		5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入车身类型按第二代5008实际SUV外廓归一。	READY
134099	134099	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
134105	134105	Convertible	Slingshot I		0	EU-POLARIS-SLINGSHOT-I-ROADSTER-01	HIGH	三轮双座开放式车身。	READY
134106_l1	134106	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	MEDIUM	同一Ktype覆盖L1厢式外廓。	READY
134106_l2	134106	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	MEDIUM	同一Ktype覆盖L2厢式外廓。	READY
134107_l1	134107	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	MEDIUM	同一Ktype覆盖L1厢式外廓。	READY
134107_l2	134107	Van	Mascott I Phase I	FH	4	EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	MEDIUM	同一Ktype覆盖L2厢式外廓。	READY
134108_wb3130	134108	Pickup	Mascott I Phase I		2	EU-RENAULT-MASCOTT-I-CHASSIS-WB3130-01	MEDIUM	同一Ktype覆盖3130 mm轴距单排底盘外廓。	READY
134108_wb3630	134108	Pickup	Mascott I Phase I		2	EU-RENAULT-MASCOTT-I-CHASSIS-WB3630-01	MEDIUM	同一Ktype覆盖3630 mm轴距单排底盘外廓。	READY
134108_wb4630	134108	Pickup	Mascott I Phase I		2	EU-RENAULT-MASCOTT-I-CHASSIS-WB4630-01	MEDIUM	同一Ktype覆盖4630 mm轴距单排底盘外廓。	READY
134110	134110	Convertible	Monza SP		2	EU-FERRARI-MONZA-SP1-CONVERTIBLE-01	HIGH	SP1单座座舱外廓。	READY
134111	134111	Convertible	Monza SP		2	EU-FERRARI-MONZA-SP2-CONVERTIBLE-01	HIGH	SP2双座座舱外廓。	READY
134112_lowroof	134112	Van	Sprinter I	903.362	4	EU-MERCEDES-BENZ-SPRINTER-I-903362-VAN-L2H1-01	MEDIUM	3550 mm轴距普通顶厢式外廓。	READY
134112_highroof	134112	Van	Sprinter I	903.362	4	EU-MERCEDES-BENZ-SPRINTER-I-903362-VAN-L2H2-01	MEDIUM	3550 mm轴距高顶厢式外廓。	READY
134113_scab	134113	Pickup	Sprinter I	903.312	2	EU-MERCEDES-BENZ-SPRINTER-I-903312-CHASSIS-SCAB-01	MEDIUM	3550 mm轴距单排驾驶室底盘。	READY
134113_dcab	134113	Pickup	Sprinter I	903.322	4	EU-MERCEDES-BENZ-SPRINTER-I-903322-CHASSIS-DCAB-01	MEDIUM	3550 mm轴距双排驾驶室底盘。	READY
134114	134114	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134117	134117	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
134129	134129	Wagon	Optima IV	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH		READY
134175	134175	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门Fastback外廓。	READY
134176	134176	Wagon	508 II	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH		READY
134183	134183	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
134187_prefl	134187	Van	Fiesta V Pre-Facelift	JC3	3	EU-FORD-FIESTA-V-JC3-VAN-PREFL-01	HIGH	改款前三门货运车身外廓。	READY
134187_facelift	134187	Van	Fiesta V Facelift	JC3	3	EU-FORD-FIESTA-V-JC3-VAN-FACELIFT-01	HIGH	改款后三门货运车身外廓。	READY
134188_prefl	134188	Van	Mondeo IV Pre-Facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	货运版沿用改款前旅行车外廓。	READY
134188_facelift	134188	Van	Mondeo IV Facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	货运版沿用改款后旅行车外廓。	READY
134195_prefl	134195	Wagon	9-3 II Pre-Facelift	YS3F	5	EU-SAAB-9-3-II-YS3F-WAGON-PREFL-01	HIGH	同一Ktype覆盖改款前SportCombi外廓。	READY
134195_facelift	134195	Wagon	9-3 II Facelift	YS3F	5	EU-SAAB-9-3-II-YS3F-WAGON-FACELIFT-01	HIGH	同一Ktype覆盖改款后SportCombi外廓。	READY
134196_prefl	134196	Sedan	9-3 II Pre-Facelift	YS3F	4	EU-SAAB-9-3-II-YS3F-SEDAN-PREFL-01	HIGH	同一Ktype覆盖改款前Sport Sedan外廓。	READY
134196_facelift	134196	Sedan	9-3 II Facelift	YS3F	4	EU-SAAB-9-3-II-YS3F-SEDAN-FACELIFT-01	HIGH	同一Ktype覆盖改款后Sport Sedan外廓。	READY
134199	134199	SUV	Patriot		5	EU-UAZ-PATRIOT-SUV-01	HIGH		READY
134200	134200	Pickup	Pickup		4	EU-UAZ-PICKUP-PICKUP-01	HIGH		READY
134201	134201	SUV	Hunter		3	EU-UAZ-HUNTER-SUV-HARDTOP-01	HIGH	硬顶封闭车身。	READY
134214	134214	Sedan	Civic X	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH		READY
134215	134215	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
134219	134219	Liftback	Arteon I Pre-Facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	272 PS版本对应改款前外廓。	READY
134222	134222	SUV	Myway		5	EU-LIFAN-MYWAY-SUV-01	HIGH		READY
134223	134223	SUV	X70		5	EU-LIFAN-X70-SUV-01	HIGH		READY
134226	134226	Coupe	DB11 I		2	EU-ASTON-MARTIN-DB11-AMR-COUPE-01	HIGH	AMR外廓。	READY
134227	134227	SUV	CR-V V	RW	5	EU-HONDA-CR-V-V-RW-SUV-FWD-01	HIGH	前驱外廓。	READY
134229	134229	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134230	134230	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
134232	134232	SUV	Ateca I Pre-Facelift	KH7	5	EU-SEAT-ATECA-I-KH7-SUV-PREFL-AWD-01	HIGH		READY
134233	134233	Coupe	Zonda C12		2	EU-PAGANI-ZONDA-C12-C12S-COUPE-01	HIGH	早期C12 Coupé外廓。	READY
134234	134234	Coupe	Zonda R		2	EU-PAGANI-ZONDA-R-COUPE-01	HIGH	750 PS赛道版Zonda R外廓。	READY
134235	134235	Coupe	Zonda Revolucion		2	EU-PAGANI-ZONDA-REVOLUCION-COUPE-01	HIGH	800 PS Zonda Revolución赛道外廓。	READY
134236	134236	Coupe	Zonda C12-S		2	EU-PAGANI-ZONDA-C12-C12S-COUPE-01	HIGH	C12-S与早期C12共用物理外廓。	READY
134237	134237	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134238	134238	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134242	134242	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134243	134243	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
134244	134244	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
134245	134245	Coupe	S-Class Coupe Facelift	C217	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	HIGH	AMG S 63改款后双门外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3201-3300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Mercedes-Benz GLE V167 official technical data	https://www.mercedes-benz.com/en/vehicles/passenger-cars/gle/
EU-KIA-OPTIMA-III-TF-SEDAN-01	4845	1830	1455	Kia Optima official brochure	https://www.kia.com/content/dam/kwcms/aw/en/pdf/Optima-brochure.pdf
EU-KIA-RIO-II-JB-HATCHBACK-01	3990	1695	1470	Automobile-Catalog Kia Rio II 1.4 EX Top specifications	https://www.automobile-catalog.com/car/2010/1354520/kia_rio_1_4_ex_top.html
EU-KIA-SORENTO-II-XM-PREFL-SUV-01	4685	1885	1710	Kia Sorento official brochure	https://www.kia.com/content/dam/kwcms/dm/en/pdf/Sorento-brochure.pdf
EU-KIA-SORENTO-II-XM-FACELIFT-SUV-01	4685	1885	1700	Kia Sorento official brochure	https://www.kia.com/content/dam/kwcms/dm/en/pdf/Sorento-brochure.pdf
EU-KIA-SPORTAGE-II-KM-FACELIFT-SUV-01	4350	1800	1695	CarsGuide 2009 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/2009
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474	Mercedes-Benz E-Class Saloon and Estate official brochure	https://www.car-mbenz.com/content/media_library/retailer/product/pc/all-class-brochures/E-Class_saloon_estate_W212_S212_0413.pdf
EU-DAEWOO-REZZO-I-KLAU-MPV-01	4350	1755	1580	Automobile-Catalog Daewoo Rezzo 1.6 SX specifications	https://www.automobile-catalog.com/car/2002/2056730/daewoo_rezzo_1_6_sx.html
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448	Automobile-Catalog Renault Clio IV specifications	https://www.automobile-catalog.com/car/2015/2983490/renault_clio_energy_dci_75.html
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448	Renault Clio official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/car-ebrochures/CLIO-eBrochure.pdf
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-PREFL-01	4788	1928	1812	Automobile-Catalog Range Rover Sport V8 Supercharged HSE specifications	https://www.automobile-catalog.com/car/2007/1404935/range_rover_sport_v8_supercharged_hse.html
EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	4790	1780	1535	Automobile-Catalog Subaru Legacy Wagon 2.5i specifications	https://www.automobile-catalog.com/car/2013/3290780/subaru_legacy_wagon_2_5i_lineatronic.html
EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	4790	1820	1605	Automobile-Catalog Subaru Outback facelift Europe specifications	https://www.automobile-catalog.com/car/2014/3290585/subaru_outback_2_0_d.html
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836	Auto-Data Range Rover IV specifications	https://www.auto-data.net/en/land-rover-range-rover-model-562
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836	Automobile-Catalog Range Rover 3.0 SDV6 275 specifications	https://www.automobile-catalog.com/car/2018/2875685/range_rover_3_0_sdv6_275.html
EU-KIA-SPORTAGE-III-SL-FACELIFT-SUV-01	4440	1855	1630	Kia Europe Geneva 2014 enhanced Sportage technical specifications	https://press.kia.com/content/dam/kiapress/EU/download-files/english/Geneva-2014-Enhanced-Kia-Sportage.doc
EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	4775	1820	1605	Automobile-Catalog Subaru Outback 2.5i Europe specifications	https://www.automobile-catalog.com/car/2011/3290480/subaru_outback_2_5i.html
EU-KIA-SPORTAGE-IV-SUV-01	4480	1855	1645	Kia Sportage official specifications	https://press.kia.com/eu/en/home/models/sportage/sportage-2016.html
EU-DS-DS3-CROSSBACK-I-SUV-01	4118	1791	1534	DS Automobiles DS 3 CROSSBACK official press release	https://www.media.stellantis.com/uk-en/ds/press/ds-3-crossback-icon-of-high-tech-style
EU-MAZDA-6-III-FACELIFT-SEDAN-01	4870	1840	1450	Mazda6 official specifications	https://www.mazda.co.uk/cars/mazda6-saloon/
EU-KIA-PRO-CEED-II-JD-HATCHBACK-3D-01	4310	1780	1430	Kia Europe pro_cee'd official press specifications	https://staging-press.kia.com/eu/en/home/models/pro-ceed/pro-ceed-2013.html
EU-BMW-Z4-III-G29-CONVERTIBLE-01	4324	1864	1304	BMW Group PressClub Z4 sDrive20i technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0329593EN/476180
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW 3 Series Sedan G20 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0289341EN/the-all-new-bmw-3-series-sedan
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series Sedan G20 official technical data	https://www.press.bmwgroup.com/global/article/detail/T0289341EN/the-all-new-bmw-3-series-sedan
EU-KIA-RIO-III-HATCHBACK-01	4045	1720	1455	Kia Rio official brochure	https://www.kia.com/content/dam/kwcms/au/en/files/owners-manual/kia-rio-brochure.pdf
EU-KIA-VENGA-YN-HATCHBACK-FACELIFT-01	4075	1765	1600	Kia Venga official specifications	https://press.kia.com/eu/en/home/models/venga/venga-2015.html
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo XC60 official specifications	https://www.volvocars.com/intl/cars/xc60/specifications/
EU-MAZDA-CX-5-II-KF-SUV-01	4550	1840	1675	Mazda CX-5 official specifications	https://www.mazda.co.uk/cars/mazda-cx-5/specifications/
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Automobile-Catalog Renault Megane Estate Grandtour 1.5 dCi 110 specifications	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440	Mercedes-Benz A-Class W177 official brochure	https://www.mercedes-benz.co.uk/passengercars/models/hatchback/a-class/overview.html
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457	Renault Megane Estate official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/car-ebrochures/MEGANE-Sport-Tourer-eBrochure.pdf
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Renault Megane official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/car-ebrochures/MEGANE-eBrochure.pdf
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471	Ford Focus 2019.5MY official brochure	https://www.fordszilcar.sk/sites/default/files/2020-10/FOCUS_2019.5MY_SK.pdf
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452	Ford Focus December 2025 official technical brochure	https://cdnepws.azureedge.net/getmedia/1ef366f3-90e2-40b3-8796-6ff7dfea6a96/focus-teknikfoy-aralik-2025_1.pdf.aspx
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471	Ford Focus official brochure	https://www.fordszilcar.sk/sites/default/files/2020-10/FOCUS_2019.5MY_SK.pdf
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471	Ford Focus facelift official technical brochure	https://cdnepws.azureedge.net/getmedia/1ef366f3-90e2-40b3-8796-6ff7dfea6a96/focus-teknikfoy-aralik-2025_1.pdf.aspx
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742	Bentley Bentayga official technical specifications	https://www.bentleymotors.com/en/models/bentayga/bentayga.html
EU-SUBARU-FORESTER-III-SH-SUV-PREFL-01	4560	1780	1675	Automobile-Catalog Subaru Forester 2.0 X specifications	https://www.automobile-catalog.com/car/2009/3292085/subaru_forester_2_0_x_awd.html
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545	Automobile-Catalog Subaru Outback 2.5i specifications	https://www.automobile-catalog.com/car/2008/3263750/subaru_outback_2_5_i.html
EU-MIA-ELECTRIC-MIA-HATCHBACK-01	2870	1640	1550	Mia electric official brochure	https://www.mia-electric.nl/.cm4all/uproc.php/0/brochure_mia_electric_-_en.pdf?_=190d0c3d879&cdp=a
EU-SUBARU-JUSTY-IV-HATCHBACK-01	3610	1665	1550	Subaru official new Justy news release	https://www.subaru.co.jp/en/news/archives/press/2007/07_09_11e.html
EU-KIA-CERATO-IV-BD-SEDAN-01	4640	1800	1450	Kia Cerato official specifications	https://www.kia.com/content/dam/kwcms/au/en/files/vehicles/cerato/kia-cerato-brochure.pdf
EU-CITROEN-JUMPY-I-PLATFORM-CAB-01	4430	1810	1930	AutoScout24 Peugeot Expert PHC 230C equivalent platform-cab specifications; TecDoc Citroën Jumpy I 1.9 TD platform/chassis boundary	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/expert/expert-phc-230c-2-0-hdi-95-utilitaire-diesel-2904/;https://uus.lakinet.ee/tecdoc/articles/en/p/21/4684/134080/100113
EU-SUBARU-IMPREZA-II-GG-WAGON-PREFL-01	4405	1695	1485	Automobile-Catalog Subaru Impreza Sports Wagon 1.6 TS AWD 2001 specifications	https://www.automobile-catalog.com/car/2001/3255650/subaru_impreza_sports_wagon_1_6_ts_awd.html
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2002-01	4415	1695	1465	Automobile-Catalog Subaru Impreza Sports Wagon 1.6 TS AWD 2003 specifications	https://www.automobile-catalog.com/car/2003/3255785/subaru_impreza_sports_wagon_1_6_ts_awd.html
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-2005-01	4465	1695	1485	Automobile-Catalog Subaru Impreza Sports Wagon 1.5R 4WD 2006 specifications	https://www.automobile-catalog.com/car/2006/3256115/subaru_impreza_sports_wagon_1_5r_4wd.html
EU-MAN-TGE-I-VAN-L3H3-01	5986	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H2-01	5986	2040	2355	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H3-01	6836	2040	2590	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H2-AWD-01	5986	2040	2390	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L3H3-AWD-01	5986	2040	2625	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-VAN-L4H3-AWD-01	6836	2040	2625	MAN TGE Next Level official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640	Peugeot 5008 official technical data	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-5008
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Dacia Dokker 2018 official brochure	https://daciast.ams3.cdn.digitaloceanspaces.com/downloads/czechia/cz-brochure-dacia-dokker-2018-02.pdf
EU-POLARIS-SLINGSHOT-I-ROADSTER-01	3800	1960	1318	Polaris Slingshot official owner's manual specifications	https://cdn.polarisportal.com/servicemanagement-public/OwnerManuals/9928978/SLINGSHOTSLINGSHOTSLSLINGSHOTSLRSLI-71E25B1E.html
EU-RENAULT-MASCOTT-I-FH-VAN-L1-01	6163	2062	2832	Drom Renault Mascott Phase I van dimensions	https://www.drom.ru/catalog/lcv/renault/mascott/specs/dimensions/
EU-RENAULT-MASCOTT-I-FH-VAN-L2-01	6663	2062	2832	Drom Renault Mascott Phase I van dimensions	https://www.drom.ru/catalog/lcv/renault/mascott/specs/dimensions/
EU-RENAULT-MASCOTT-I-CHASSIS-WB3130-01	5929	2093	2268	Zoomcar Renault Trucks Mascott 110.35 chassis cab EMP 3.13 specifications	https://zoomcar.fr/fiche-technique-utilitaire/renault-trucks/mascott-110-150-chassis-cabine-110-35-emp-3-13-NAT59979.html
EU-RENAULT-MASCOTT-I-CHASSIS-WB3630-01	5929	2093	2268	Zoomcar Renault Trucks Mascott 110.35 chassis cab EMP 3.63 specifications	https://zoomcar.fr/fiche-technique-utilitaire/renault-trucks/mascott-110-150-chassis-cabine-110-35-emp-3-63-NAT59980.html
EU-RENAULT-MASCOTT-I-CHASSIS-WB4630-01	5929	2093	2268	Zoomcar Renault Trucks Mascott 110.35 chassis cab EMP 4.63 specifications	https://zoomcar.fr/fiche-technique-utilitaire/renault-trucks/mascott-110-150-chassis-cabine-110-35-emp-4-63-NAT59982.html
EU-FERRARI-MONZA-SP1-CONVERTIBLE-01	4657	1996	1155	Ferrari Monza SP1 and SP2 official technical sheet	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/180016_car_ferrari_monza_sp1_sp2_en1.pdf
EU-FERRARI-MONZA-SP2-CONVERTIBLE-01	4657	1996	1155	Ferrari Monza SP1 and SP2 official technical sheet	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/180016_car_ferrari_monza_sp1_sp2_en1.pdf
EU-MERCEDES-BENZ-SPRINTER-I-903362-VAN-L2H1-01	5585	1933	2365	Mercedes Sprinter I L2H1 dimensional specification; TecDoc 308 E body-code boundary	https://www.transitcenter.de/mercedes-sprinter-1995-technische-daten-t-86.html;https://www.autodoc.co.uk/car-parts/shock-absorber-10221/mercedes-benz/sprinter/sprinter-3-t-box-903/134112-308-e-903-362
EU-MERCEDES-BENZ-SPRINTER-I-903362-VAN-L2H2-01	5585	1933	2591	Mercedes Sprinter I L2H2 dimensional specification; TecDoc 308 E body-code boundary	https://www.transitcenter.de/mercedes-sprinter-1995-technische-daten-t-86.html;https://www.autodoc.co.uk/car-parts/shock-absorber-10221/mercedes-benz/sprinter/sprinter-3-t-box-903/134112-308-e-903-362
EU-MERCEDES-BENZ-SPRINTER-I-903312-CHASSIS-SCAB-01	5369	1933	2140	JATO Mercedes-Benz Sprinter 3550-mm single-cab chassis dimensions; Mercedes EPC body-code boundary	https://www.coches.net/fichas_tecnicas/mercedes-benz/sprinter/industriales/2-puertas/310d_35t_3550_102cv_diesel/19613/30079619990301/;https://partsouq.com/shop/product/A0006370134-mercedes-rail/19610707
EU-MERCEDES-BENZ-SPRINTER-I-903322-CHASSIS-DCAB-01	5369	1933	2140	JATO Mercedes-Benz Sprinter 3550-mm chassis dimensions; Mercedes EPC double-cab body-code boundary	https://www.carexpert.co.nz/mercedes-benz/sprinter/1999-2-9l-chassis-cab-rwd-diesel-manual-jjo8fsm519991001;https://partsouq.com/shop/product/A0009108665-mercedes-frame/19690172
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Peugeot 3008 official technical data	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-3008
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470	Kia Optima Sportswagon official specifications	https://press.kia.com/eu/en/home/models/optima/optima-sportswagon.html
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404	Peugeot 508 official technical data	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-508
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 SW official technical data	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-508-sw
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo XC40 official specifications	https://www.volvocars.com/intl/cars/xc40/specifications/
EU-FORD-FIESTA-V-JC3-VAN-PREFL-01	3917	1683	1467	Ford Fiesta Van official brochure archived copy	https://manuals.plus/m/7218d31c7755745164911cb2826b7a226d785b6c13d9176ee306d168ced6b2c2
EU-FORD-FIESTA-V-JC3-VAN-FACELIFT-01	3918	1721	1468	Ford commercial vehicle range official brochure archived copy	https://manuals.plus/m/968094e06d7f3c43af8268ba976de918466003510008e734a4857625a8b61f0e
EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	4830	1886	1512	Automobile-Catalog Ford Mondeo Estate 2.0 TDCi 140 specifications	https://www.automobile-catalog.com/car/2007/979130/ford_mondeo_estate_2_0_tdci_140_zetec.html
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Automobile-Catalog Ford Mondeo Turnier 2.0 TDCi 140 specifications	https://www.automobile-catalog.com/car/2011/1595885/ford_mondeo_5-dr_2_0_tdci_140_trend_powershift.html
EU-SAAB-9-3-II-YS3F-WAGON-PREFL-01	4654	1762	1490	Automobile-Catalog Saab 9-3 2.0T SportCombi specifications	https://www.automobile-catalog.com/car/2007/3036140/saab_9-3_2_0t_sportcombi.html
EU-SAAB-9-3-II-YS3F-WAGON-FACELIFT-01	4670	1762	1498	Automobile-Catalog Saab 9-3 2.0t SportCombi specifications	https://www.automobile-catalog.com/car/2010/3037040/saab_9-3_2_0t_sportcombi.html
EU-SAAB-9-3-II-YS3F-SEDAN-PREFL-01	4635	1762	1467	Automobile-Catalog Saab 9-3 2.0t Sport Sedan specifications	https://www.automobile-catalog.com/car/2006/3035855/saab_9-3_2_0t_sport.html
EU-SAAB-9-3-II-YS3F-SEDAN-FACELIFT-01	4647	1762	1450	Automobile-Catalog Saab 9-3 2.0T Sport Sedan specifications	https://www.automobile-catalog.com/car/2010/3037970/saab_9-3_2_0t.html
EU-UAZ-PATRIOT-SUV-01	4785	1900	1910	UAZ Patriot official brochure	https://www.uaz.ru/data/uploads/uaz/originals/f80bb717-9f45-483c-b178-12d4fd99a562.pdf
EU-UAZ-PICKUP-PICKUP-01	5125	1915	1915	UAZ Pickup official brochure	https://www.uaz.ru/data/uploads/uaz/originals/uaz-pickup-broshure-en-290722.pdf
EU-UAZ-HUNTER-SUV-HARDTOP-01	4050	1775	1950	UAZ Hunter official brochure	https://www.uaz.ru/data/uploads/uaz/originals/b68e7d74-c8f7-47f8-bf3b-08e43e5d4ec5.pdf
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416	Honda Civic Sedan official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/94264/2017-honda-civic-sedan
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo V60 official specifications	https://www.volvocars.com/intl/cars/v60/specifications/
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450	Volkswagen Arteon official brochure	https://www.volkswagen-newsroom.com/en/the-arteon-2017-2019-1957
EU-LIFAN-MYWAY-SUV-01	4440	1760	1730	Lifan Myway official specifications	https://lifan-car.ru/cars/myway
EU-LIFAN-X70-SUV-01	4390	1820	1715	Lifan X70 official specifications	https://lifan-car.ru/cars/x70
EU-ASTON-MARTIN-DB11-AMR-COUPE-01	4750	1950	1290	Aston Martin DB11 AMR official press release	https://media.astonmartin.com/db11-amr-new-performance-flagship-of-the-db11-range
EU-HONDA-CR-V-V-RW-SUV-FWD-01	4600	1855	1679	Honda CR-V official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/156416/2019-honda-cr-v-hybrid
EU-SEAT-ATECA-I-KH7-SUV-PREFL-AWD-01	4363	1841	1611	SEAT Ateca official brochure	https://www.seat.com/content/dam/public/seat-website/myco/2028/car-shopping-tools/brochure-download/brochures/ateca/other-shoppingtools-brochure-ateca-specs-final-october-2019.pdf
EU-PAGANI-ZONDA-C12-C12S-COUPE-01	4395	2055	1151	Pagani Zonda C12 official specifications; Pagani Zonda S official specifications	https://www.pagani.com/zonda-c12/;https://www.pagani.com/zonda-s/
EU-PAGANI-ZONDA-R-COUPE-01	4886	2014	1141	Pagani Zonda R official specifications	https://www.pagani.com/zonda-r/
EU-PAGANI-ZONDA-REVOLUCION-COUPE-01	4886	2014	1141	Pagani Zonda Revolución official specifications	https://www.pagani.com/zonda-revolucion/
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247 specifications	https://www.auto-data.net/en/mercedes-benz-b-class-model-1363
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Touareg official technical data	https://www.volkswagen-newsroom.com/en/the-new-touareg-2018-4145
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424	Automobile-Catalog Mercedes-AMG S 63 4MATIC+ Coupe specifications	https://www.automobile-catalog.com/car/2017/2603030/mercedes-amg_s_63_4matic_plus_coupe.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3201-3300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://zoomcar.fr/fiche-technique-utilitaire/renault-trucks/mascott-110-150-chassis-cabine-110-35-emp-3-13-NAT59979.html?utm_source=chatgpt.com "Fiche technique RENAULT TRUCKS MASCOTT 110-150 CHASSIS CAB Châssis cabine 1999 59979 | zoomcar.fr"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2678 行）
- 累计尺寸组：dimension_groups_final.tsv（1310 行）

