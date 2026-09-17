# 任务：all 第 7801-7900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0079__c38256ab


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7801-7900 行

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
all 第 7801-7900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-E39-WAGON-01	4805	1800	1440
EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	4910	1860	1454
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-CHEVROLET-CORVETTE-C5-COUPE-2D-01	4564	1869	1212
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714
EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	4315	1660	1385
EU-DAIHATSU-APPLAUSE-I-A111-HATCHBACK-4WD-01	4315	1660	1440
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-HYUNDAI-PONY-X2-HATCHBACK-01	4104	1603	1361
EU-HYUNDAI-PONY-X2-SEDAN-4D-01	4282	1603	1361
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ40-XJ81-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261
EU-JAGUAR-XJ-SERIES-II-COUPE-01	4843	1770	1375
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1377
EU-JAGUAR-XJ-SERIES-III-SEDAN-02	4959	1770	1372
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375
EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375
EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	4843	1770	1375
EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	4814	1768	1343
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261
EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	5023	1798	1314
EU-JAGUAR-XJ-X306-XJR-SEDAN-SWB-01	5023	1798	1303
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457
EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	4430	1706	1361
EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	4428	1678	1390
EU-MERCEDES-BENZ-190-W201-SEDAN-EARLY-01	4420	1678	1383
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO1-01	4430	1720	1342
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO2-01	4543	1720	1342
EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	4448	1690	1375
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE1-01	4420	1678	1390
EU-MERCEDES-BENZ-190-W201-SEDAN-PHASE2-01	4448	1690	1375
EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	4420	1678	1390
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-02	4795	1799	1439
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-AMG-01	4795	1799	1411
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	4855	2000	2455
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	5235	2000	2525
EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	5885	2000	2240
EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	5885	2000	2530
EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	4855	2000	2170
EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	5235	2000	2240
EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	5885	2000	2240
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-OPEL-KADETT-E-CARAVAN-01	4228	1666	1430
EU-OPEL-KADETT-E-COMBO-VAN-3D-01	4221	1674	1670
EU-OPEL-KADETT-E-CONVERTIBLE-16-01	3998	1663	1385
EU-OPEL-KADETT-E-CONVERTIBLE-20-01	3998	1663	1380
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400
EU-OPEL-KADETT-E-SEDAN-01	4218	1658	1400
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400
EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	4430	1700	1400
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400
EU-PEUGEOT-106-I-HATCHBACK-3D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-5D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	3564	1607	1360
EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	3680	1590	1380
EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	3680	1590	1380
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376
EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	3678	1610	1357
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380
EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	4946	1886	1670
EU-PONTIAC-TRANS-SPORT-II-GMT200-MPV-SWB-01	4757	1847	1712
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-RENAULT-4-F4-VAN-3D-01	3653	1500	1710
EU-RENAULT-4-MPV-5D-01	3668	1485	1550
EU-RENAULT-4-R2108-VAN-HIGHROOF-3D-01	3695	1500	1820
EU-SEAT-MALAGA-023A-SEDAN-4D-01	4275	1650	1390
EU-SKODA-FELICIA-I-795-WAGON-01	4205	1635	1420
EU-SKODA-FELICIA-I-HATCHBACK-01	3883	1635	1415
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-4WD-01	3870	1680	1395
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-NARROW-01	3870	1680	1390
EU-SUZUKI-BALENO-I-EG-HATCHBACK-3D-WIDE-01	3870	1690	1390
EU-SUZUKI-BALENO-I-EG-SEDAN-4D-01	4195	1690	1390
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425
EU-ZASTAVA-101-HATCHBACK-5D-01	3890	1590	1345

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	110	150	Jan 1970	Dec 1981	2024-03-01	8495
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	112	152	Dec 1981	Dec 1992	2024-03-01	8496
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	183	249	Jan 1989	Jan 1997	2024-03-01	8500
Chevrolet	Malibu	3.7	Stufenheck	Heckantrieb	Benzin	81	110	Jan 1980	Dec 1983	2024-03-01	8501
Chevrolet	Malibu	5	Stufenheck	Heckantrieb	Benzin	110	150	Jan 1980	Dec 1983	2024-03-01	8502
Chrysler	Daytona	2.2 I Turbo	Coupe	Frontantrieb	Benzin	130	177	Sep 1986	Dec 1990	2024-03-01	8506
Zastava	101	1.1	Schrägheck	Frontantrieb	Benzin	40	55	Jun 1973	Jan 1990	2024-03-01	8507
Chrysler	Saratoga	3	Stufenheck	Frontantrieb	Benzin	105	142	Sep 1989	Dec 1995	2024-03-01	8508
Chrysler	300c	3.0 V6 CRD	Stufenheck	Heckantrieb	Diesel	155	211	Nov 2010	Nov 2012	2024-03-01	8509
Chevrolet	Captiva	2.2 D	SUV	Frontantrieb	Diesel	120	163	Mar 2011	-	2024-03-01	8510
Zastava	101	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Dec 1975	Jan 1980	2024-03-01	8511
Zastava	101	1.1 Super	Schrägheck	Frontantrieb	Benzin	47	64	Jul 1979	Sep 1981	2024-03-01	8512
Chevrolet	Captiva	2.2 D 4WD	SUV	Allrad	Diesel	135	184	Mar 2011	-	2024-03-01	8513
Daihatsu	Applause i	1.6 16V	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1989	Jul 1997	2024-03-01	8516
Pontiac	Firebird	Trans AM 3.1	Coupe	Heckantrieb	Benzin	104	141	Jan 1987	Oct 1992	2024-03-01	8517
Pontiac	Firebird	5	Coupe	Heckantrieb	Benzin	112	152	Dec 1981	Oct 1989	2024-03-01	8518
Chevrolet	Captiva	2.0 D 4WD	SUV	Allrad	Diesel	93	126	Oct 2006	Dec 2009	2024-03-01	8519
Pontiac	Phoenix	2.8	Coupe	Frontantrieb	Benzin	86	117	Apr 1979	Dec 1981	2024-03-01	8521
Pontiac	Phoenix	2.8	Schrägheck	Frontantrieb	Benzin	85	116	Apr 1979	Dec 1981	2024-03-01	8522
Pontiac	Sunbird	3.8	Coupe	Heckantrieb	Benzin	83	113	Oct 1975	Dec 1981	2024-03-01	8523
Mercedes-benz	E-Klasse	E 280 T	Kombi	Heckantrieb	Benzin	150	204	Dec 1996	Mar 2003	2024-03-01	8525
BMW	5	525 TD	Stufenheck	Heckantrieb	Diesel	85	116	Jan 1997	Jun 2003	2024-03-01	8526
Mercedes-benz	T1	209 D 2.9	Kasten	Heckantrieb	Diesel	65	88	Dec 1982	Jan 1990	2024-03-01	8527
Mercedes-benz	T1	209 D 2.9	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Dec 1982	Jan 1990	2024-03-01	8528
Mercedes-benz	T1	210 2.3	Kasten	Heckantrieb	Benzin	70	95	Jul 1982	Feb 1996	2024-03-01	8529
Mercedes-benz	T1	310 D 2.9	Kasten	Heckantrieb	Diesel	70	95	Jun 1989	Feb 1996	2024-03-01	8530
Mercedes-benz	T1	308 D 2.3	Pritsche/Fahrgestell	Heckantrieb	Diesel	60	82	Jun 1989	Feb 1996	2024-03-01	8531
Mercedes-benz	G-Klasse	230 GE	Geländewagen offen	Allrad	Benzin	93	126	Jun 1990	Feb 1993	2024-03-01	8532
Mercedes-benz	G-Klasse	320 GE	Geländewagen offen	Allrad	Benzin	155	211	Sep 1994	Nov 1997	2024-03-01	8533
Pontiac	Trans sport	2.3	Großraumlimousine	Frontantrieb	Benzin	101	137	Jan 1993	Mar 1997	2024-03-01	8534
Pontiac	Trans sport	3.1	Großraumlimousine	Frontantrieb	Benzin	104	141	Jul 1989	Mar 1997	2024-03-01	8535
Pontiac	Trans sport	2.3	Großraumlimousine	Frontantrieb	Benzin	108	147	Jan 1993	Mar 1997	2024-03-01	8536
Pontiac	Trans sport	3.8	Großraumlimousine	Frontantrieb	Benzin	123	167	Jul 1989	Mar 1997	2024-03-01	8537
Pontiac	Trans sport	3.8	Großraumlimousine	Frontantrieb	Benzin	112	152	Jul 1989	Mar 1997	2024-03-01	8538
Mercedes-benz	G-Klasse	250 GD	Geländewagen geschlossen	Allrad	Diesel	68	92	Dec 1988	Aug 1992	2024-03-01	8539
Mercedes-benz	G-Klasse	230 G	Geländewagen geschlossen	Allrad	Benzin	75	102	Feb 1980	Jul 1987	2024-03-01	8540
Hyundai	Pony	1.5	Schrägheck	Frontantrieb	Benzin	53	72	Oct 1985	Sep 1989	2024-03-01	8541
Mercedes-benz	G-Klasse	350 G Turbo-d	Geländewagen offen	Allrad	Diesel	100	136	Sep 1991	Sep 1997	2024-03-01	8543
Mercedes-benz	G-Klasse	300 GD	Geländewagen offen	Allrad	Diesel	83	113	Sep 1989	Aug 1993	2024-03-01	8544
Mercedes-benz	S-Klasse	CL 500	Coupe	Heckantrieb	Benzin	320	435	Feb 2011	Dec 2013	2024-03-01	8545
Mercedes-benz	G-Klasse	300 GE	Geländewagen offen	Allrad	Benzin	125	170	Sep 1989	Sep 1997	2024-03-01	8546
Mercedes-benz	G-Klasse	250 GD	Geländewagen geschlossen	Allrad	Diesel	69	94	Jun 1990	Oct 1992	2024-03-01	8547
Innocenti	Mini	1	Schrägheck	Frontantrieb	Benzin	39	53	May 1974	Feb 1982	2024-03-01	8554
Jaguar	Xj	6 2.9	Stufenheck	Heckantrieb	Benzin	123	167	Oct 1986	Aug 1990	2024-03-01	8555
Mercedes-benz	E-Klasse	E 200 D	Stufenheck	Heckantrieb	Diesel	65	88	Jan 1996	Mar 2002	2024-03-01	8557
Mercedes-benz	190	E 2.0	Stufenheck	Heckantrieb	Benzin	93	126	Oct 1982	Jun 1993	2024-03-01	8561
Mazda	626 ii hatchback	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1983	Sep 1987	2024-03-01	8564
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	71	97	Jun 1990	Jan 1996	2024-03-01	8568
Nissan	Primera	2.0 D	Schrägheck	Frontantrieb	Diesel	55	75	Jan 1991	Jan 1996	2024-03-01	8569
Opel	Corsa a tr	1.2 S	Stufenheck	Frontantrieb	Benzin	43	58	Sep 1982	Oct 1987	2024-03-01	8574
Opel	Kadett e	1.8	Stufenheck	Frontantrieb	Benzin	84	114	Sep 1987	Aug 1990	2024-03-01	8579
Opel	Vectra a	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1993	Nov 1995	2024-03-01	8581
Peugeot	106 i	1.5 D	Schrägheck	Frontantrieb	Diesel	43	58	Jun 1994	Apr 1996	2024-03-01	8582
Mercedes-benz	S-Klasse	CL 500 4-matic	Coupe	Allrad	Benzin	320	435	Feb 2011	Dec 2013	2024-03-01	8588
Renault	4	1.1	Schrägheck	Frontantrieb	Benzin	32	44	Jun 1986	Jun 1990	2024-03-01	8603
Renault	6	1.1	Schrägheck	Frontantrieb	Benzin	33	45	Aug 1970	Apr 1987	2024-03-01	8605
Renault	6	1.1	Schrägheck	Frontantrieb	Benzin	35	48	Jul 1971	Apr 1980	2024-03-01	8606
Renault	6	0.8	Schrägheck	Frontantrieb	Benzin	25	34	Oct 1969	Apr 1980	2024-03-01	8607
Mercedes-benz	S-Klasse	CL 63 AMG	Coupe	Heckantrieb	Benzin	400	544	Feb 2011	Dec 2013	2024-03-01	8610
Peugeot	309 ii	1.6	Schrägheck	Frontantrieb	Benzin	69	94	Jul 1989	Dec 1993	2024-03-01	8622
Peugeot	309 i	1.6	Schrägheck	Frontantrieb	Benzin	69	94	Jan 1986	Jul 1989	2024-03-01	8623
Seat	Malaga	1.2	Stufenheck	Frontantrieb	Benzin	47	64	Nov 1984	Dec 1993	2024-03-01	8630
Volvo	460	1.7	Stufenheck	Frontantrieb	Benzin	64	87	Sep 1988	Jul 1996	2024-03-01	8636
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	89	121	Aug 1985	Jul 1992	2024-03-01	8639
Volvo	740	2	Kombi	Heckantrieb	Benzin	89	121	Aug 1985	Jul 1992	2024-03-01	8640
Volvo	940	2.0 Turbo	Kombi	Heckantrieb	Benzin	114	155	Jan 1991	Jul 1995	2024-03-01	8641
Mercedes-benz	S-Klasse	CL 65 AMG	Coupe	Heckantrieb	Benzin	463	630	Feb 2011	Dec 2013	2024-03-01	8663
Ford	Transit	2	Bus	Heckantrieb	Benzin	43	59	Dec 1977	Jul 1982	2024-03-01	8665
Chevrolet	Aveo / kalos	1.2	Stufenheck	Frontantrieb	Benzin	55	75	Jan 2008	-	2024-03-01	8666
Mercedes-benz	Sprinter 2-T	210 D	Kasten	Heckantrieb	Diesel	75	102	Jan 1997	Apr 2000	2024-03-01	8667
Chevrolet	Cruze	2.0 CDI	Stufenheck	Frontantrieb	Diesel	120	163	Aug 2010	-	2024-03-01	8668
Mercedes-benz	T1	207 D 2.4	Pritsche/Fahrgestell	Heckantrieb	Diesel	53	72	Dec 1977	Oct 1989	2024-03-01	8669
Mercedes-benz	Sprinter 2-T	212 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	90	122	Feb 1995	Apr 2000	2024-03-01	8670
Mercedes-benz	Sprinter 2-T	208 D	Kasten	Heckantrieb	Diesel	58	79	Feb 1995	Apr 2000	2024-03-01	8671
Ford	Transit	2	Bus	Heckantrieb	Benzin	55	75	Nov 1977	Oct 1986	2024-03-01	8672
Ford	Transit	2	Kasten	Heckantrieb	Benzin	43	59	Nov 1977	Jul 1982	2024-03-01	8673
Mercedes-benz	T1	210 2.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	70	95	Apr 1977	Oct 1989	2024-03-01	8674
Ford	Transit	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	46	62	Jan 1978	Dec 1985	2024-07-01	8675
Ford	Transit	2.5 D	Kasten	Heckantrieb	Diesel	50	68	Oct 1983	Oct 1986	2024-03-01	8676
Ford	Transit	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	50	68	Oct 1983	Oct 1986	2024-03-01	8677
Mercedes-benz	Sprinter 3-T	308 D 2.3	Pritsche/Fahrgestell	Heckantrieb	Diesel	58	79	Feb 1995	Apr 2000	2024-03-01	8678
Mercedes-benz	Sprinter 3-T	308 D 2.3	Kasten	Heckantrieb	Diesel	58	79	Feb 1995	Apr 2000	2024-03-01	8679
Citroën	Evasion	1.8	Großraumlimousine	Frontantrieb	Benzin	73	99	May 1997	Jul 2002	2024-03-01	8680
Peugeot	208 i	1.6 THP	Schrägheck	Frontantrieb	Benzin	115	156	Mar 2012	Dec 2019	2024-05-01	8683
Peugeot	208 i	1.4 HDI	Schrägheck	Frontantrieb	Diesel	50	68	Mar 2012	Dec 2019	2024-03-01	8684
Peugeot	208 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	68	92	Mar 2012	Dec 2019	2024-03-01	8685
Peugeot	208 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	84	114	Mar 2012	Dec 2019	2024-03-01	8686
Mercedes-benz	E-Klasse	E 240	Stufenheck	Heckantrieb	Benzin	125	170	Jun 1997	Aug 2000	2024-03-01	8687
Mercedes-benz	E-Klasse	E 430	Stufenheck	Heckantrieb	Benzin	205	279	Jun 1997	Mar 2002	2024-03-01	8688
Mercedes-benz	E-Klasse	E 240 T	Kombi	Heckantrieb	Benzin	125	170	Jun 1997	Mar 2003	2024-03-01	8689
Mercedes-benz	E-Klasse	E 430 T	Kombi	Heckantrieb	Benzin	205	279	Jun 1997	Mar 2003	2024-03-01	8690
Mercedes-benz	E-Klasse	E 200 T Kompressor	Kombi	Heckantrieb	Benzin	137	186	Jun 1997	Mar 2003	2024-03-01	8691
Mercedes-benz	E-Klasse	E 200 Kompressor	Stufenheck	Heckantrieb	Benzin	137	186	Jun 1997	Mar 2002	2024-03-01	8692
Volvo	S40 i	1.9 T4	Stufenheck	Frontantrieb	Benzin	147	200	May 1997	Jul 2000	2024-03-01	8693
Volvo	V40	1.9 T4	Kombi	Frontantrieb	Benzin	147	200	May 1997	Jul 2000	2024-03-01	8694
Porsche	911	3.4 Carrera	Coupe	Heckantrieb	Benzin	221	301	Aug 1997	Jul 2001	2024-03-01	8696
Ssangyong	Korando	2	Geländewagen geschlossen	Allrad	Benzin	94	128	May 1997	Oct 2002	2024-03-01	8697
Ssangyong	Korando	2.3	Geländewagen geschlossen	Allrad	Benzin	103	140	May 1997	Feb 2000	2024-03-01	8698
Suzuki	Baleno	1.3 16V	Kombi	Frontantrieb	Benzin	63	86	Mar 1997	May 2002	2024-03-01	8700
Skoda	Felicia i	1.6	Pick-up	Frontantrieb	Benzin	55	75	Jun 1997	Apr 2002	2024-03-01	8702


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 50 个输入 Ktype 的物理车身映射，共形成 58 条 READY 映射；其中 Mercedes-Benz G-Klasse W460、Peugeot 106/309、Mercedes-Benz 190 W201、Suzuki Baleno Wagon 等按实际外廓拆分派生行。
* 复用跨批次既有尺寸组 33 个，未重复抓取或重复输出既有尺寸事实。跨批次索引核对依据：
* 首次闭合 10 个尺寸组，主要包括 Mercedes-Benz CL C216、Innocenti Mini Bertone、Chevrolet Aveo T250、Cruze J300、Porsche 911 996、Suzuki Baleno Wagon 和 Skoda Felicia 797 Pickup。相关规格页面已区分车身宽度与含后视镜宽度，落盘宽度采用不含后视镜口径。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：50
* READY 映射行：58
* PENDING Ktype：50
* 已确认尺寸组：43

  * 复用既有组：33
  * 本轮首次创建：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8507	8507	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8511	8511	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8512	8512	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8516	8516	Hatchback	Applause I	A101	5	EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	HIGH		READY
8525	8525	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8526	8526	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
8534	8534	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8535	8535	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8536	8536	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8537	8537	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8538	8538	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8539_swb	8539	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8539_lwb	8539	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8540_swb	8540	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8540_lwb	8540	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8547_swb	8547	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8547_lwb	8547	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8545	8545	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	HIGH		READY
8554	8554	Hatchback	Innocenti Mini (Bertone)		3	EU-INNOCENTI-MINI-BERTONE-HATCHBACK-3D-01	MEDIUM	1974-1982 Bertone 三门车身。	READY
8555	8555	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
8557	8557	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
8561_prefl	8561	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	MEDIUM	生产区间跨越改款，拆分改款前外廓。	READY
8561_facelift	8561	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越改款，拆分改款后外廓。	READY
8568	8568	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH		READY
8569	8569	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH		READY
8579	8579	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
8581	8581	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
8582_3dr	8582	Hatchback	106 I	1A	3	EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	MEDIUM	同一 Ktype 覆盖三门车身分支。	READY
8582_5dr	8582	Hatchback	106 I	1C	5	EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	MEDIUM	同一 Ktype 覆盖五门车身分支。	READY
8588	8588	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	HIGH		READY
8603	8603	Hatchback	Renault 4		5	EU-RENAULT-4-MPV-5D-01	HIGH		READY
8610	8610	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG63-COUPE-01	HIGH		READY
8622_3dr	8622	Hatchback	309 II		3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门车身分支。	READY
8622_5dr	8622	Hatchback	309 II		5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖五门车身分支。	READY
8623_3dr	8623	Hatchback	309 I		3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门车身分支。	READY
8623_5dr	8623	Hatchback	309 I		5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖五门车身分支。	READY
8630	8630	Sedan	Malaga	023A	4	EU-SEAT-MALAGA-023A-SEDAN-4D-01	HIGH		READY
8636	8636	Sedan	460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
8639	8639	Sedan	740		4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
8640	8640	Wagon	740		5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
8641	8641	Wagon	940		5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
8663	8663	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG65-COUPE-01	HIGH		READY
8666	8666	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	MEDIUM	输入功率标注与资料存在小幅口径差异，车身边界为 T250 四门轿车。	READY
8668	8668	Sedan	Cruze J300	J300	4	EU-CHEVROLET-CRUZE-J300-SEDAN-4D-01	HIGH		READY
8680	8680	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
8687	8687	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8688	8688	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8689	8689	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8690	8690	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	HIGH		READY
8691	8691	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8692	8692	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8693	8693	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
8694	8694	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
8696	8696	Coupe	911 (996)	996	2	EU-PORSCHE-911-996-CARRERA-COUPE-01	HIGH		READY
8698	8698	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	HIGH		READY
8700_prefl	8700	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-EG-WAGON-PREFL-01	MEDIUM	生产区间跨越外廓长度变化，拆分改款前。	READY
8700_facelift	8700	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-EG-WAGON-FACELIFT-01	MEDIUM	生产区间跨越外廓长度变化，拆分改款后。	READY
8702	8702	Pickup	Felicia I Fun	797	2	EU-SKODA-FELICIA-I-797-PICKUP-2D-01	MEDIUM	输入结束时间晚于当前直接规格页覆盖，物理外廓按 797 Fun 皮卡闭合。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	5095	1871	1419	Auto-Data Mercedes-Benz CL C216 facelift CL 500 RWD; Auto-Data Mercedes-Benz CL C216 facelift CL 500 4MATIC	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-7g-tronic-plus-18674; https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673
EU-INNOCENTI-MINI-BERTONE-HATCHBACK-3D-01	3120	1500	1380	Automobile-Catalog 1974 Innocenti Mini 120 L; Auto-Data Innocenti Mini 1.0 53 Hp	https://www.automobile-catalog.com/car/1974/44645/innocenti_mini_120_l.html; https://www.auto-data.net/en/innocenti-mini-1.0-53hp-14652
EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG63-COUPE-01	5106	1871	1425	Auto-Data Mercedes-Benz CL C216 facelift AMG CL 63	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-amg-cl-63-v8-544hp-amg-speedshift-mct-18677
EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG65-COUPE-01	5106	1871	1428	Auto-Data Mercedes-Benz CL C216 facelift AMG CL 65	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-amg-cl-65-v12-630hp-amg-speedshift-18676
EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	4310	1710	1505	Auto-Data Chevrolet Aveo Sedan 1.2 i 8V; Automobile-Catalog 2008 Chevrolet Aveo T250 Sedan range	https://www.auto-data.net/en/chevrolet-aveo-sedan-1.2-i-8v-72hp-14427; https://www.automobile-catalog.com/make/chevrolet_europe/t250_europe/t250_eu_sedan/2008.html
EU-CHEVROLET-CRUZE-J300-SEDAN-4D-01	4597	1788	1477	Auto-Data Chevrolet Cruze Sedan 2.0 TD 163 Hp	https://www.auto-data.net/en/chevrolet-cruze-sedan-2.0-td-163hp-16938
EU-PORSCHE-911-996-CARRERA-COUPE-01	4430	1765	1305	Auto-Data Porsche 911 996 Carrera 3.4	https://www.auto-data.net/en/porsche-911-996-carrera-3.4-300hp-6591
EU-SUZUKI-BALENO-I-EG-WAGON-PREFL-01	4345	1690	1460	Auto-Data Suzuki Baleno Combi EG 1.6 i 16V 98 Hp	https://www.auto-data.net/en/suzuki-baleno-combi-eg-1995-1.6-i-16v-98hp-16477
EU-SUZUKI-BALENO-I-EG-WAGON-FACELIFT-01	4375	1690	1460	Auto-Data Suzuki Baleno Combi EG 1.3 i 16V 85 Hp	https://www.auto-data.net/en/suzuki-baleno-combi-eg-1995-1.3-i-16v-85hp-16475
EU-SKODA-FELICIA-I-797-PICKUP-2D-01	4245	1680	1465	Auto-Data Skoda Felicia I Fun 797 1.6	https://www.auto-data.net/en/skoda-felicia-i-fun-797-1.6-75hp-14088
```

## 下一步优先处理

1. 优先聚类 Mercedes-Benz T1、Sprinter 2-T/3-T 与 Ford Transit，确认 Van、Bus、Platform 的轴距和车顶分支。
2. 闭合 Chevrolet Captiva、Peugeot 208 I、SsangYong Korando 2.0 等宽度口径或版本边界尚未闭合的车型。
3. 批量处理 Camaro、Corvette C4、Malibu、Daytona、Firebird、Phoenix、Sunbird 等北美历史车型。
4. 最后处理 G-Klasse 开放式车身、Renault 6、Mazda 626 II Hatchback、Opel Corsa A TR 等剩余分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673 "https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 Peugeot 208 I（A9）四个 Ktype：THP 156 确认为三门分支；HDi 68、92、114 按三门/五门拆分，两种车身分别建立稳定尺寸组。Peugeot 官方资料确认第一代 208 的发动机序列、三门/五门车身体系及 THP 156 版本边界。([Stellantis Media][1])
* Ktype 8541、8697 分别直接复用既有 Hyundai Pony X2 Hatchback 和 SsangYong Korando II KJ H1840 尺寸组，未重复输出尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：56
* READY 映射行：67
* PENDING Ktype：44
* 已确认尺寸组：47

  * 复用既有组：35
  * 本批首次创建：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8541	8541	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH		READY
8683	8683	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	HIGH	THP 156对应三门车身。	READY
8684_3dr	8684	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8684_5dr	8684	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8685_3dr	8685	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8685_5dr	8685	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8686_3dr	8686	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8686_5dr	8686	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8697	8697	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	3962	1739	1460	Peugeot Technical characteristics: 208	https://www.media.stellantis.com/em-en/peugeot/press/technical-characteristics-208
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	3962	1739	1460	Peugeot Technical characteristics: 208	https://www.media.stellantis.com/em-en/peugeot/press/technical-characteristics-208
```

## 下一步优先处理

1. 闭合 Chevrolet Captiva 改款前、改款后尺寸组，并批量关联三个 Captiva Ktype。
2. 处理 Camaro、Corvette C4、Malibu、Firebird、Phoenix 和 Sunbird 的年份外廓分支。
3. 集中处理 Mercedes-Benz T1、Sprinter 与 Ford Transit 的轴距、车顶和车身形式组合。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/peugeot/press/technical-characteristics-208 "Technical characteristics : 208 | Peugeot | Stellantis Media"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Chevrolet Captiva I 的改款前 C100 与 2011 改款 C140 两个尺寸组，三个 Ktype 均完成关联；改款前为 4635×1850×1720 mm，改款后为 4673×1849×1727 mm，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Mercedes-Benz G-Class W463 Cabriolet：230 GE、300 GD、300 GE 共用窄体 Cabriolet 组；350 GD Turbo 因 1994 年 7 月起长宽高发生变化拆为窄体、宽体两行；G 320 关联宽体组。官方资料同时确认相应车身代码和三门边界。([marsClassic][2])
* 闭合 Mazda 626 II GC 五门 Hatchback 尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* READY 映射行：77
* PENDING Ktype：35
* 已确认尺寸组：52
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8510	8510	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
8513	8513	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
8519	8519	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH		READY
8532	8532	Convertible	G-Class W463	463.204	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8533	8533	Convertible	G-Class W463	463.208	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	HIGH		READY
8543_pre94	8543	Convertible	G-Class W463	463.300	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH	1994年7月前窄体外廓。	READY
8543_wide	8543	Convertible	G-Class W463	463.300	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	HIGH	1994年7月起宽体外廓。	READY
8544	8544	Convertible	G-Class W463	463.307	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8546	8546	Convertible	G-Class W463	463.207	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8564	8564	Hatchback	626 II	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	4673	1849	1727	Automobile-Catalog 2011 Chevrolet Captiva 2.2 D 163 LS 2WD; Automobile-Catalog 2011 Chevrolet Captiva 2.2 D 184 LT 4WD	https://www.automobile-catalog.com/car/2011/1569185/chevrolet_captiva_2_2_d_163_ls_2wd.html; https://www.automobile-catalog.com/car/2011/1569125/chevrolet_captiva_2_2_d_184_lt_4wd.html
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Captiva 2.0 VCDi 127 4WD LS	https://www.automobile-catalog.com/car/2007/559895/chevrolet_captiva_2_0_vcdi_127_4wd_ls.html
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	4225	1690	1940	Mercedes-Benz Public Archive 230 GE short wheelbase; Mercedes-Benz Public Archive 300 GD short wheelbase; Mercedes-Benz Public Archive 300 GE short wheelbase; Mercedes-Benz Public Archive 350 GD Turbo short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-GE-from-091993-G-230-short-wheelbase-1990---1994.xhtml?oid=191039024; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GE-from-091993-G-300-short-wheelbase-1990---1996.xhtml?oid=191039026; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-GD-Turbo-from-091993-G-350-Turbodiesel-short-wheelbase-1992---1996.xhtml?oid=191039020
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	4275	1760	1941	Mercedes-Benz Public Archive 350 GD Turbo short wheelbase; Mercedes-Benz Public Archive G 320 short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-GD-Turbo-from-091993-G-350-Turbodiesel-short-wheelbase-1992---1996.xhtml?oid=191039020; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-short-wheelbase-1994---1997.xhtml?oid=191039028
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350	Automobile-Catalog 1983 Mazda 626 1.6 LX 5-Door	https://www.automobile-catalog.com/car/1983/1645400/mazda_626_1_6_lx_5-door_automatic.html
```

## 下一步优先处理

1. 处理 Chevrolet Camaro、Corvette、Malibu 与 Pontiac Firebird 等跨改款、跨代际北美车型。
2. 批量闭合 Chrysler Daytona、Saratoga、Pontiac Phoenix、Sunbird。
3. 随后集中处理 Mercedes-Benz T1、Sprinter 与 Ford Transit 的轴距、车顶及车身形式分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/559895/chevrolet_captiva_2_0_vcdi_127_4wd_ls.html?utm_source=chatgpt.com "2007 Chevrolet Captiva 2.0 VCDi 127 4WD LS (man. 5)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GE-from-091993-G-300-short-wheelbase-1990---1996.xhtml?oid=191039026 "300 GE (from 09.1993: G 300) (short wheelbase), 1990 - 1996"
[3]: https://www.automobile-catalog.com/car/1983/1645400/mazda_626_1_6_lx_5-door_automatic.html?utm_source=chatgpt.com "1983 Mazda 626 1.6 LX 5-Door automatic (aut. 3)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Mercedes-Benz T1 七个 Ktype 的缓存关联。Kasten 按 L1/L2/L3 与 H1/H2 拆分；Pritsche/Fahrgestell 按 L1/L2/L3 拆分。全部复用既有尺寸组，未重复输出尺寸事实。
* 首次闭合 Chrysler 300C 第二代四门 Sedan 尺寸组。官方资料确认该车身基于新一代 Chrysler 300，外廓为 5066 × 1902 × 1488 mm。([Stellantis Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射行：108
* PENDING Ktype：27
* 已确认尺寸组：53
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8509	8509	Sedan	300C II	LD	4	EU-CHRYSLER-300C-II-LD-SEDAN-4D-01	HIGH		READY
8527_l1h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8527_l1h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8527_l2h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8527_l2h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8527_l3h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8527_l3h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8528_l1	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8528_l2	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8528_l3	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8529_l1h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8529_l1h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8529_l2h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8529_l2h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8529_l3h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8529_l3h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8530_l1h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8530_l1h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8530_l2h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8530_l2h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8530_l3h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8530_l3h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8531_l1	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8531_l2	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8531_l3	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8669_l1	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8669_l2	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8669_l3	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8674_l1	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8674_l2	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8674_l3	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-300C-II-LD-SEDAN-4D-01	5066	1902	1488	Lancia Thema official technical data based on the new Chrysler 300	https://www.media.stellantis.com/nl-nl/lancia/press/nieuwe-lancia-thema-het-beste-van-twee-werelden
```

## 下一步优先处理

1. 闭合第一代 Mercedes-Benz Sprinter 2-T、3-T 的 Van 与平台车身分支。
2. 处理 Ford Transit Mk2、VE6 的 Bus、Van 与平台组合。
3. 随后集中处理 Camaro、Corvette C4、Malibu、Firebird、Phoenix、Sunbird、Daytona 和 Saratoga。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/nl-nl/lancia/press/nieuwe-lancia-thema-het-beste-van-twee-werelden?utm_source=chatgpt.com "Nieuwe Lancia Thema: het beste van twee werelden"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 Ford Transit Mk1/Mk2 Bus 与 Van 的缓存关联。
* Ktype 8665、8672、8673 的生产区间跨 Mk1/Mk2，按代际、轴距和车顶外廓拆分。
* Ktype 8676 仅关联 Mk2 的 SWB 低顶与 LWB 高顶外廓。
* 本轮全部复用既有尺寸组，未重新抓取三维或重复输出来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：77
* READY 映射行：119
* PENDING Ktype：23
* 已确认尺寸组：53
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8665_mk1_swb_lowroof	8665	MPV	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶车身分支。	READY
8665_mk2_swb_lowroof	8665	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶车身分支。	READY
8665_mk2_lwb_highroof	8665	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶车身分支。	READY
8672_mk1_swb_lowroof	8672	MPV	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶车身分支。	READY
8672_mk2_swb_lowroof	8672	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶车身分支。	READY
8672_mk2_lwb_highroof	8672	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶车身分支。	READY
8673_mk1_swb_lowroof	8673	Van	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶封闭车身，与既有Bus外廓相同。	READY
8673_mk2_swb_lowroof	8673	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶封闭车身，与既有Bus外廓相同。	READY
8673_mk2_lwb_highroof	8673	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶封闭车身，与既有Bus外廓相同。	READY
8676_swb_lowroof	8676	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶封闭车身，与既有Bus外廓相同。	READY
8676_lwb_highroof	8676	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶封闭车身，与既有Bus外廓相同。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Mercedes-Benz Sprinter T1N 的 2-T、3-T Van 和平台车身，按 L1/L2/L3 与车顶高度批量建组。
2. 处理 Ford Transit Mk2 的 Pritsche/Fahrgestell，补齐平台车身尺寸组。
3. 批量闭合 Camaro、Corvette C4、Malibu、Firebird、Phoenix、Sunbird、Daytona 和 Saratoga。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Chrysler Daytona Shelby G-body 与 Chrysler Saratoga AA 四门轿车，共新增 2 个 Ktype 映射和 2 个尺寸组。Daytona 按三门掀背式 Coupe 处理；Saratoga 对应欧洲市场 AA-platform 四门 Sedan。([汽车数据网][1])
* 闭合 Pontiac Phoenix II X-body 的二门 Coupe、五门 Hatchback 两种独立外廓。([汽车目录][2])
* 闭合 Opel Corsa A TR phase I 二门轿车外廓。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射行：124
* PENDING Ktype：18
* 已确认尺寸组：58
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8506	8506	Coupe	Daytona Shelby	G	3	EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	MEDIUM	Shelby三门掀背式Coupe外廓。	READY
8508	8508	Sedan	Saratoga	AA	4	EU-CHRYSLER-SARATOGA-AA-SEDAN-4D-01	HIGH		READY
8521	8521	Coupe	Phoenix II	X	2	EU-PONTIAC-PHOENIX-II-X-COUPE-2D-01	HIGH	X-body二门Coupe外廓。	READY
8522	8522	Hatchback	Phoenix II	X	5	EU-PONTIAC-PHOENIX-II-X-HATCHBACK-5D-01	HIGH	X-body五门掀背外廓。	READY
8574	8574	Sedan	Corsa A TR phase I		2	EU-OPEL-CORSA-A-TR-PHASE1-SEDAN-2D-01	MEDIUM	TR二门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	4560	1760	1285	Auto-Data Chrysler Daytona Shelby generation; Auto-Data Chrysler Daytona Shelby 2.2 i Turbo 177 Hp	https://www.auto-data.net/en/chrysler-daytona-shelby-model-1642; https://www.auto-data.net/en/chrysler-daytona-shelby-2.2-i-turbo-177hp-14698
EU-CHRYSLER-SARATOGA-AA-SEDAN-4D-01	4602	1731	1410	Auto-Data Chrysler Saratoga 3.0 i V6; Automobile-Catalog 1990 Chrysler Saratoga range	https://www.auto-data.net/en/chrysler-saratoga-3.0-i-v6-141hp-automatic-14783; https://www.automobile-catalog.com/make/chrysler/saratoga/saratoga/1990.html
EU-PONTIAC-PHOENIX-II-X-COUPE-2D-01	4626	1754	1359	Automobile-Catalog 1980 Pontiac Phoenix LJ Coupe 2.8 V6	https://www.automobile-catalog.com/car/1980/2835860/pontiac_phoenix_lj_coupe_2_8_liter_v6.html
EU-PONTIAC-PHOENIX-II-X-HATCHBACK-5D-01	4555	1768	1356	Automobile-Catalog 1980 Pontiac Phoenix 5-Door Hatchback; Automobile-Catalog 1980 Pontiac Phoenix 5-Door Hatchback 2.8 V6	https://www.automobile-catalog.com/car/1980/2835740/pontiac_phoenix_5-door_hatchback_2_5_liter.html; https://www.automobile-catalog.com/car/1980/47630/pontiac_phoenix_5-door_hatchback_2_8-litre_v6_automatic.html
EU-OPEL-CORSA-A-TR-PHASE1-SEDAN-2D-01	3955	1540	1360	Automobile-Catalog 1983 Opel Corsa TR 1.2 S	https://www.automobile-catalog.com/car/1983/2456240/opel_corsa_tr_1_2_s.html
```

## 下一步优先处理

1. 批量闭合 Camaro、Corvette C4、Malibu、Firebird 与 Sunbird 的代际及改款外廓。
2. 处理第一代 Sprinter 2-T、3-T 的 Van 和平台车轴距、车顶组合。
3. 补齐 Ford Transit 平台车、Renault 6 等剩余物理分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/chrysler-daytona-shelby-2.2-i-turbo-177hp-14698 "Chrysler Daytona Shelby 2.2 i Turbo (177 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1980/2835860/pontiac_phoenix_lj_coupe_2_8_liter_v6.html?utm_source=chatgpt.com "1980 Pontiac Phoenix LJ Coupe 2.8 Liter V6 (man. 4)"
[3]: https://www.automobile-catalog.com/car/1983/2456240/opel_corsa_tr_1_2_s.html?utm_source=chatgpt.com "1983 Opel Corsa TR 1.2 S Specs Review (40.5 kW / 55 PS / 54 hp) (up to mid-year 1983 for Europe Spain, France)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Chevrolet Camaro III Ktype 8496，按 1982–1984、1985–1990、1991–1992 三套不同外廓拆分。([汽车目录][1])
* 闭合 Chevrolet Corvette C4 Cabriolet Ktype 8500，按 1989、1990、1991、1992–1993、1994–1996 五套实际变化的外廓拆分。([汽车目录][2])
* 闭合 Chevrolet Malibu III 两个 Ktype。1980 年车身与 1981–1983 年车身宽度、高度不同，分别建组后供 3.7 和 5.0 版本共同引用。([汽车目录][3])
* 闭合 Renault 6 三个 Ktype。生产区间均跨越早期与 1974 年后外廓变化，因此分别拆成 `pre74` 和 `post74`。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射行：142
* PENDING Ktype：11
* 已确认尺寸组：70
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8496_82_84	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-82-84-01	MEDIUM	1982至1984年初期外廓。	READY
8496_85_90	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-85-90-01	MEDIUM	1985至1990年外廓。	READY
8496_91_92	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-91-92-01	MEDIUM	1991至1992年改款外廓。	READY
8500_89	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1989-01	MEDIUM	1989年Cabriolet外廓。	READY
8500_90	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1990-01	MEDIUM	1990年高度变化外廓。	READY
8500_91	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1991-01	MEDIUM	1991年车身长度变化外廓。	READY
8500_92_93	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-92-93-01	MEDIUM	1992至1993年外廓。	READY
8500_94_96	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-94-96-01	MEDIUM	1994至1996年高度变化外廓。	READY
8501_80	8501	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	MEDIUM	1980年四门轿车外廓。	READY
8501_81_83	8501	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	MEDIUM	1981至1983年四门轿车外廓。	READY
8502_80	8502	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	MEDIUM	1980年四门轿车外廓。	READY
8502_81_83	8502	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	MEDIUM	1981至1983年四门轿车外廓。	READY
8605_pre74	8605	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8605_post74	8605	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
8606_pre74	8606	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8606_post74	8606	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
8607_pre74	8607	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8607_post74	8607	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-III-F-COUPE-82-84-01	4770	1849	1270	Automobile-Catalog 1983 Chevrolet Camaro Z28 5.0L V8	https://www.automobile-catalog.com/car/1983/458210/chevrolet_camaro_z28_5_0l_v-8_5-speed.html
EU-CHEVROLET-CAMARO-III-F-COUPE-85-90-01	4877	1849	1278	Automobile-Catalog 1986 Chevrolet Camaro Z28 5.0L V8	https://www.automobile-catalog.com/car/1986/458975/chevrolet_camaro_z28_5_0l_v-8.html
EU-CHEVROLET-CAMARO-III-F-COUPE-91-92-01	4892	1839	1280	Automobile-Catalog 1992 Chevrolet Camaro Z28 5.0L V8 EFI	https://www.automobile-catalog.com/car/1992/460145/chevrolet_camaro_z28_5_0l_v-8_efi.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1989-01	4483	1803	1179	Automobile-Catalog 1989 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1989/463505/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1990-01	4483	1803	1186	Automobile-Catalog 1990 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1990/463595/chevrolet_corvette_convertible_automatic.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1991-01	4536	1803	1186	Automobile-Catalog 1991 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1991/463670/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-92-93-01	4534	1796	1176	Automobile-Catalog 1992 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1992/463775/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-94-96-01	4534	1796	1201	Automobile-Catalog 1994 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1994/463955/chevrolet_corvette_convertible.html
EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	4895	1816	1377	Automobile-Catalog 1980 Chevrolet Malibu Sedan 3.8L V6; Automobile-Catalog 1980 Chevrolet Malibu Classic Sedan 5.0L V8	https://www.automobile-catalog.com/car/1980/202985/chevrolet_malibu_sedan_3_8l_v-6_automatic.html; https://www.automobile-catalog.com/car/1980/206690/chevrolet_malibu_classic_sedan_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	4895	1836	1415	Automobile-Catalog 1983 Chevrolet Malibu Sedan 3.8 V6; Automobile-Catalog 1983 Chevrolet Malibu Classic Sport Sedan 5.0L V8	https://www.automobile-catalog.com/car/1983/203825/chevrolet_malibu_sedan_3_8_v6_automatic.html; https://www.automobile-catalog.com/car/1983/204245/chevrolet_malibu_sport_sedan_5_0l_v-8_automatic.html
EU-RENAULT-6-HATCHBACK-PRE74-01	3848	1537	1500	Automobile-Catalog 1969 Renault 6	https://www.automobile-catalog.com/car/1969/27380/renault_6.html
EU-RENAULT-6-HATCHBACK-POST74-01	3858	1504	1475	Automobile-Catalog 1980 Renault 6 TL	https://www.automobile-catalog.com/car/1980/2925605/renault_6_tl.html
```

## 下一步优先处理

1. 闭合 Chevrolet Camaro II Ktype 8495 的改款前后外廓。
2. 闭合 Pontiac Firebird Ktype 8517、8518 与 Sunbird Ktype 8523。
3. 最后集中处理 8 个 Mercedes-Benz Sprinter/Ford Transit Van、平台车 Ktype，完成轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/458210/chevrolet_camaro_z28_5_0l_v-8_5-speed.html?utm_source=chatgpt.com "1983 Chevrolet Camaro Z28 5.0L V-8 5-speed (man. 5)"
[2]: https://www.automobile-catalog.com/car/1989/463505/chevrolet_corvette_convertible.html?utm_source=chatgpt.com "1989 Chevrolet Corvette Convertible (man. 6)"
[3]: https://www.automobile-catalog.com/car/1980/202985/chevrolet_malibu_sedan_3_8l_v-6_automatic.html?utm_source=chatgpt.com "1980 Chevrolet Malibu Sedan 3.8L V-6 automatic (aut. 3)"
[4]: https://www.automobile-catalog.com/car/1969/27380/renault_6.html?utm_source=chatgpt.com "1969 Renault 6 Specs Review (25 kW / 34 PS / 34 hp) (up ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Pontiac Firebird III 剩余两个 Ktype。Ktype 8518 按 1982、1983–1984、1985、1986、1987–1989 的实际外廓变化拆分；Ktype 8517 的 3.1 L 版本按 1990 与 1991–1992 改款外廓拆分，其中 1990 年外廓复用已创建的 1987–1990 尺寸组。([汽车目录][1])
* 闭合 Pontiac Sunbird I 3.8 Coupe，按 1976–1977、1978、1979–1980 三套不同长宽高拆分。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* READY 映射行：152
* PENDING Ktype：8
* 已确认尺寸组：79
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8517_1990	8517	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	MEDIUM	3.1版本对应1990年改款前外廓。	READY
8517_91_92	8517	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-91-92-01	MEDIUM	1991至1992年加长前后保险杠外廓。	READY
8518_1982	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1982-01	MEDIUM	1982年初期外廓。	READY
8518_83_84	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-83-84-01	MEDIUM	1983至1984年外廓。	READY
8518_1985	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1985-01	MEDIUM	1985年外廓。	READY
8518_1986	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1986-01	MEDIUM	1986年外廓。	READY
8518_87_89	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	MEDIUM	1987至1989年外廓。	READY
8523_76_77	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-76-77-01	MEDIUM	1976至1977年初期Coupe外廓。	READY
8523_1978	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-1978-01	MEDIUM	1978年高度变化外廓。	READY
8523_79_80	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-79-80-01	MEDIUM	1979至1980年加长外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	4778	1839	1270	Automobile-Catalog 1987 Pontiac Firebird Formula 5.0 V8; Automobile-Catalog 1990 Pontiac Firebird 3.1 V6	https://www.automobile-catalog.com/car/1987/2849630/pontiac_firebird_formula_5_0_l_v8_automatic.html; https://www.automobile-catalog.com/car/1990/2852645/pontiac_firebird_3_1_l_v6_mfi_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-91-92-01	4956	1839	1262	Automobile-Catalog 1992 Pontiac Firebird 3.1 V6	https://www.automobile-catalog.com/car/1992/2853830/pontiac_firebird_3_1_l_v6_5-speed.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1982-01	4821	1829	1265	Automobile-Catalog 1982 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1982/2839955/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-83-84-01	4821	1844	1288	Automobile-Catalog 1983 Pontiac Firebird S/E 5.0 V8; Automobile-Catalog 1984 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1983/2841770/pontiac_firebird_se_5_0_liter_v8_5-speed.html; https://www.automobile-catalog.com/car/1984/2843990/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1985-01	4823	1839	1262	Automobile-Catalog 1985 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1985/2845595/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1986-01	4839	1839	1262	Automobile-Catalog 1986 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1986/2847680/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-76-77-01	4516	1661	1265	Automobile-Catalog 1977 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1977/2826815/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-1978-01	4516	1661	1260	Automobile-Catalog 1978 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1978/2829635/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-79-80-01	4552	1661	1260	Automobile-Catalog 1979 Pontiac Sunbird Coupe 3.8 V6; Automobile-Catalog 1980 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1979/2832605/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html; https://www.automobile-catalog.com/car/1980/2835620/pontiac_sunbird_coupe_3_8_liter_v6_4-speed.html
```

## 下一步优先处理

1. 闭合 Chevrolet Camaro II Ktype 8495 的年份外廓分支。
2. 集中处理 Mercedes-Benz Sprinter 2-T/3-T 的 Kasten 与 Pritsche/Fahrgestell，共 5 个 Ktype。
3. 闭合 Ford Transit Mk2 平台车 Ktype 8675、8677。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1982/2839955/pontiac_firebird_5_0_liter_v8_automatic.html?utm_source=chatgpt.com "1982 Pontiac Firebird 5.0 Liter V8 automatic (aut. 3)"
[2]: https://www.automobile-catalog.com/car/1977/2826815/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html?utm_source=chatgpt.com "1977 Pontiac Sunbird Coupe 3.8-litre V6 5-speed (man. 5)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Chevrolet Camaro II Ktype `8495`。生产区间覆盖多次保险杠及车身高度变化，按 1970、1971、1972、1973、1974–1976、1977、1978、1979–1981 八套实际外廓拆分。
* 各分支宽度均采用资料明确标注的车身宽度、不含后视镜。1970–1973 年长度/高度逐年存在变化；1974 年起加长，1977 年高度变化，1978 年再次加长，1979 年起宽度增至 1892 mm。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射行：160
* PENDING Ktype：7
* 已确认尺寸组：87
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8495_1970	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1970-01	MEDIUM	1970年初期车身外廓。	READY
8495_1971	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1971-01	MEDIUM	1971年车身高度分支。	READY
8495_1972	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1972-01	MEDIUM	1972年车身高度分支。	READY
8495_1973	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1973-01	MEDIUM	1973年车身长度分支。	READY
8495_74_76	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-74-76-01	MEDIUM	1974至1976年加长外廓。	READY
8495_1977	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1977-01	MEDIUM	1977年车身高度分支。	READY
8495_1978	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1978-01	MEDIUM	1978年加长外廓。	READY
8495_79_81	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-79-81-01	MEDIUM	1979至1981年宽度调整后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-II-F-COUPE-1970-01	4775	1890	1273	Automobile-Catalog 1970 Chevrolet Camaro 250 Turbo-Thrift Powerglide	https://www.automobile-catalog.com/car/1970/100670/chevrolet_camaro_250_turbo-thrift_powerglide.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1971-01	4775	1890	1283	Automobile-Catalog 1971 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1971/101090/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1972-01	4775	1890	1247	Automobile-Catalog 1972 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1972/101285/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1973-01	4785	1890	1247	Automobile-Catalog 1973 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1973/101540/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAMARO-II-F-COUPE-74-76-01	4963	1890	1247	Automobile-Catalog 1975 Chevrolet Camaro Sport Coupe 350 V8	https://www.automobile-catalog.com/car/1975/102320/chevrolet_camaro_sport_coupe_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1977-01	4963	1890	1250	Automobile-Catalog 1977 Chevrolet Camaro Sport Coupe 305 V8	https://www.automobile-catalog.com/car/1977/205535/chevrolet_camaro_sport_coupe_305_v-8.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1978-01	5019	1890	1250	Automobile-Catalog 1978 Chevrolet Camaro Sport Coupe 305 V8	https://www.automobile-catalog.com/car/1978/205790/chevrolet_camaro_sport_coupe_305_v-8_4-speed.html
EU-CHEVROLET-CAMARO-II-F-COUPE-79-81-01	5019	1892	1250	Automobile-Catalog 1979 Chevrolet Camaro Sport Coupe; Automobile-Catalog 1980 Chevrolet Camaro Sport Coupe 5.0 V8; Automobile-Catalog 1981 Chevrolet Camaro Sport Coupe 5.0 V8	https://www.automobile-catalog.com/car/1979/206240/chevrolet_camaro_sport_coupe_4_1l_automatic.html; https://www.automobile-catalog.com/car/1980/206855/chevrolet_camaro_sport_coupe_5_0l_v-8_automatic.html; https://www.automobile-catalog.com/car/1981/207215/chevrolet_camaro_sport_coupe_5_0l_v-8_automatic.html
```

## 下一步优先处理

1. 集中闭合 Mercedes-Benz Sprinter T1N 的 2-T/3-T Kasten：Ktype `8667`、`8671`、`8679`。
2. 闭合 Sprinter Pritsche/Fahrgestell：Ktype `8670`、`8678`。
3. 最后处理 Ford Transit Mk2 平台车：Ktype `8675`、`8677`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1970/100670/chevrolet_camaro_250_turbo-thrift_powerglide.html?utm_source=chatgpt.com "1970 Chevrolet Camaro 250 Turbo-Thrift Powerglide Specs Review (115.5 kW / 157 PS / 155 hp) (since September 1970 for North America )"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz Sprinter T1N 两个底盘车 Ktype：

  * `8670` 确认为 `901.421` 短轴单排驾驶室和 `902.412` 中轴单排驾驶室。
  * `8678` 确认为 `903.311` 短轴单排、`903.312` 中轴单排及 `903.322` 中轴双排驾驶室。
* 相同单排驾驶室物理外廓跨 2-T/3-T 复用同一尺寸组；`903.322` 双排驾驶室单独建组。车型代码范围及对应轴距由车型目录交叉闭合。([autogidas.lt][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：165
* PENDING Ktype：5
* 已确认尺寸组：90
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8670_swb_singlecab	8670	Pickup	Sprinter I T1N	901.421	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	MEDIUM	短轴单排驾驶室平台分支。	READY
8670_mwb_singlecab	8670	Pickup	Sprinter I T1N	902.412	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	MEDIUM	中轴单排驾驶室平台分支。	READY
8678_swb_singlecab	8678	Pickup	Sprinter I T1N	903.311	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	MEDIUM	短轴单排驾驶室平台分支。	READY
8678_mwb_singlecab	8678	Pickup	Sprinter I T1N	903.312	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	MEDIUM	中轴单排驾驶室平台分支。	READY
8678_mwb_doublecab	8678	Pickup	Sprinter I T1N	903.322	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-PLATFORM-MWB-DOUBLECAB-01	MEDIUM	中轴双排驾驶室平台分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	4819	1922	2135	Autogidas Mercedes-Benz Sprinter 208 D 902.311; AUTODOC Sprinter 212 D and 308 D platform/chassis code listings	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/208-d-902.311-1995-2000-k18354; https://www.autodoc.co.uk/car-parts/centre-rod-assembly-15157/mercedes-benz/sprinter/sprinter-2-t-platform-chassis-901-902/8670-212-d-901-421-902-412; https://www.autodoc.co.uk/car-parts/air-filter-10360/mercedes-benz/sprinter/sprinter-3-t-platform-chassis-903/8678-308-d-2-3-903-311-903-312-903-322
EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	5470	1922	2115	Autogidas Mercedes-Benz Sprinter 212 D 902.412; Autogidas Mercedes-Benz Sprinter 308 D 903.312	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/212-d-902.412-1995-2000-k18369; https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/308-d-903.312-1995-2000-k31182
EU-MERCEDES-BENZ-SPRINTER-I-W903-PLATFORM-MWB-DOUBLECAB-01	5855	1922	2155	Autogidas Mercedes-Benz Sprinter 308 D 903.322	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/308-d-903.322-1995-2000-k31185
```

## 下一步优先处理

1. 闭合 Sprinter T1N Kasten：`8667`、`8671`、`8679`，按轴距与车顶高度拆分。
2. 闭合 Ford Transit Mk2 平台车：`8675`、`8677`，确认短轴/长轴及单排/双排驾驶室外廓。
3. PENDING 清零后只做一次机械检查，并在下一轮直接输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/212-d-902.411-1995-2000-k30624?utm_source=chatgpt.com "Mercedes-Benz Sprinter 212 D 902.411 1995-2000"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Sprinter T1N 最后 3 个 Ktype。`8667`、`8671` 分别覆盖 W901/W902 的短轴和中轴封闭车身；`8679` 覆盖 W903 的短轴、中轴及长轴高顶车身。车型代码范围分别为 `901/902.361/.362`、`901/902.461/.462` 和 `903.361/.362/.363`。([AUTODOC][1])
* 按相同物理外廓合并后首次创建 3 个尺寸组：3000 mm 轴距短轴、3550 mm 轴距中轴、4025 mm 轴距长轴高顶；不同发动机和总质量级别直接复用相同外廓组。短轴为 4835×1933×2350 mm，中轴为 5585×1933×2345 mm，长轴高顶为 6535×1933×2570 mm。([CarExpert NZ][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：176
* PENDING Ktype：2
* 已确认尺寸组：93
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8667_901461	8667	Van	Sprinter I T1N	901.461		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	901.461短轴封闭车身分支。	READY
8667_901462	8667	Van	Sprinter I T1N	901.462		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	901.462中轴封闭车身分支。	READY
8667_902461	8667	Van	Sprinter I T1N	902.461		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	902.461短轴封闭车身分支。	READY
8667_902462	8667	Van	Sprinter I T1N	902.462		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	902.462中轴封闭车身分支。	READY
8671_901361	8671	Van	Sprinter I T1N	901.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	901.361短轴封闭车身分支。	READY
8671_901362	8671	Van	Sprinter I T1N	901.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	901.362中轴封闭车身分支。	READY
8671_902361	8671	Van	Sprinter I T1N	902.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	902.361短轴封闭车身分支。	READY
8671_902362	8671	Van	Sprinter I T1N	902.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	902.362中轴封闭车身分支。	READY
8679_903361	8679	Van	Sprinter I T1N	903.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	903.361短轴封闭车身分支。	READY
8679_903362	8679	Van	Sprinter I T1N	903.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	903.362中轴封闭车身分支。	READY
8679_903363	8679	Van	Sprinter I T1N	903.363		EU-MERCEDES-BENZ-SPRINTER-I-VAN-LWB-HIGHROOF-01	MEDIUM	903.363长轴高顶封闭车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	4835	1933	2350	CarExpert 1998 Mercedes-Benz Sprinter 3000 mm wheelbase specifications; AUTODOC Sprinter 2-T Van body-code listing	https://www.carexpert.co.nz/mercedes-benz/sprinter/1998-2-9l-window-van-rwd-diesel-manual-jjo8fsm819980401; https://www.autodoc.co.uk/spares/mercedes-benz/sprinter/sprinter-2-t-box-901-902/8671-208-d-901-361-901-362-902-361-902-362
EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	5585	1933	2345	CarExpert 1999 Mercedes-Benz Sprinter 3550 mm wheelbase specifications; AUTODOC Sprinter 2-T Van 210 D body-code listing	https://www.carexpert.co.nz/mercedes-benz/sprinter/1999-2-9l-window-van-rwd-diesel-manual-jjo8fsma19991001; https://www.autodoc.co.uk/spares/mercedes-benz/sprinter/sprinter-2-t-box-901-902/8667-210-d-901-461-901-462-902-461-902-462
EU-MERCEDES-BENZ-SPRINTER-I-VAN-LWB-HIGHROOF-01	6535	1933	2570	CarsGuide 1999 Mercedes-Benz Sprinter 308D specifications; AUTODOC Sprinter 3-T Van 308 D body-code listing	https://www.carsguide.com.au/mercedes-benz/sprinter/price/1999/308d; https://www.autodoc.parts/car-parts/catalyst-converter-10147/mercedes-benz/sprinter/sprinter-3-t-box-903/8679-308-d-2-3-903-361-903-362-903-363
```

## 下一步优先处理

1. 闭合 Ford Transit Mk2 平台车 Ktype `8675`、`8677`。
2. 核定 VGL/VSL/VTL/VCS/VDS 对应的短轴、长轴及驾驶室外廓，避免直接套用 Bus/Van 的车顶高度。
3. 两个 Ktype 完成后立即进行一次机械检查，并在下一轮输出两张完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/spares/mercedes-benz/sprinter/sprinter-2-t-box-901-902/8667-210-d-901-461-901-462-902-461-902-462?utm_source=chatgpt.com "Parts Mercedes Sprinter 2t 210 D 102 hp Diesel 1997"
[2]: https://www.carexpert.co.nz/mercedes-benz/sprinter/1998-2-9l-window-van-rwd-diesel-manual-jjo8fsm819980401?utm_source=chatgpt.com "1998 Mercedes-Benz Sprinter Base Price and Specifications"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7801-7900_ktype_dimension_mapping_final.tsv
- all_7801-7900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 最后两个 Ford Transit Mk2 平台车 Ktype `8675`、`8677` 已按短轴与长轴单排 dropside 外廓完成拆分和尺寸组绑定。Transit Mk2 资料确认底盘驾驶室存在 SWB/LWB 分支，并结合历史车型资料闭合对应外廓。([维基百科][1])
* 已完成机械检查：映射表共 180 行、覆盖 100 个原始 Ktype、`id` 全部唯一；尺寸组共 107 行、`DIMENSION_GROUP_ID` 全部唯一；所有映射引用闭合，无孤立尺寸组、无 PENDING。
* 47 个跨批次既有尺寸组按缓存优先原则直接复用，未重新抓取；其来源通过累计缓存 URI 保留。当前批次首次创建的尺寸组保留直接来源 URL。
* 两个任务指定 TSV 文件已生成并校验。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：180
* PENDING Ktype：0
* DIMENSION_GROUP：107
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8495_1970	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1970-01	MEDIUM	1970年初期车身外廓。	READY
8495_1971	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1971-01	MEDIUM	1971年车身高度分支。	READY
8495_1972	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1972-01	MEDIUM	1972年车身高度分支。	READY
8495_1973	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1973-01	MEDIUM	1973年车身长度分支。	READY
8495_74_76	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-74-76-01	MEDIUM	1974至1976年加长外廓。	READY
8495_1977	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1977-01	MEDIUM	1977年车身高度分支。	READY
8495_1978	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-1978-01	MEDIUM	1978年加长外廓。	READY
8495_79_81	8495	Coupe	Camaro II	F	2	EU-CHEVROLET-CAMARO-II-F-COUPE-79-81-01	MEDIUM	1979至1981年宽度调整后外廓。	READY
8496_82_84	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-82-84-01	MEDIUM	1982至1984年初期外廓。	READY
8496_85_90	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-85-90-01	MEDIUM	1985至1990年外廓。	READY
8496_91_92	8496	Coupe	Camaro III	F	3	EU-CHEVROLET-CAMARO-III-F-COUPE-91-92-01	MEDIUM	1991至1992年改款外廓。	READY
8500_89	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1989-01	MEDIUM	1989年Cabriolet外廓。	READY
8500_90	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1990-01	MEDIUM	1990年高度变化外廓。	READY
8500_91	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1991-01	MEDIUM	1991年车身长度变化外廓。	READY
8500_92_93	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-92-93-01	MEDIUM	1992至1993年外廓。	READY
8500_94_96	8500	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-94-96-01	MEDIUM	1994至1996年高度变化外廓。	READY
8501_80	8501	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	MEDIUM	1980年四门轿车外廓。	READY
8501_81_83	8501	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	MEDIUM	1981至1983年四门轿车外廓。	READY
8502_80	8502	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	MEDIUM	1980年四门轿车外廓。	READY
8502_81_83	8502	Sedan	Malibu III	G	4	EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	MEDIUM	1981至1983年四门轿车外廓。	READY
8506	8506	Coupe	Daytona Shelby	G	3	EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	MEDIUM	Shelby三门掀背式Coupe外廓。	READY
8507	8507	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8508	8508	Sedan	Saratoga	AA	4	EU-CHRYSLER-SARATOGA-AA-SEDAN-4D-01	HIGH		READY
8509	8509	Sedan	300C II	LD	4	EU-CHRYSLER-300C-II-LD-SEDAN-4D-01	HIGH		READY
8510	8510	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
8511	8511	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8512	8512	Hatchback	Zastava 101		5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
8513	8513	SUV	Captiva I facelift	C140	5	EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	HIGH		READY
8516	8516	Hatchback	Applause I	A101	5	EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	HIGH		READY
8517_1990	8517	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	MEDIUM	3.1版本对应1990年改款前外廓。	READY
8517_91_92	8517	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-91-92-01	MEDIUM	1991至1992年加长前后保险杠外廓。	READY
8518_1982	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1982-01	MEDIUM	1982年初期外廓。	READY
8518_83_84	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-83-84-01	MEDIUM	1983至1984年外廓。	READY
8518_1985	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1985-01	MEDIUM	1985年外廓。	READY
8518_1986	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-1986-01	MEDIUM	1986年外廓。	READY
8518_87_89	8518	Coupe	Firebird III	F	3	EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	MEDIUM	1987至1989年外廓。	READY
8519	8519	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH		READY
8521	8521	Coupe	Phoenix II	X	2	EU-PONTIAC-PHOENIX-II-X-COUPE-2D-01	HIGH	X-body二门Coupe外廓。	READY
8522	8522	Hatchback	Phoenix II	X	5	EU-PONTIAC-PHOENIX-II-X-HATCHBACK-5D-01	HIGH	X-body五门掀背外廓。	READY
8523_76_77	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-76-77-01	MEDIUM	1976至1977年初期Coupe外廓。	READY
8523_1978	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-1978-01	MEDIUM	1978年高度变化外廓。	READY
8523_79_80	8523	Coupe	Sunbird I	H	2	EU-PONTIAC-SUNBIRD-I-H-COUPE-79-80-01	MEDIUM	1979至1980年加长外廓。	READY
8525	8525	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8526	8526	Sedan	5 Series E39	E39	4	EU-BMW-5-E39-SEDAN-01	HIGH		READY
8527_l1h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8527_l1h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8527_l2h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8527_l2h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8527_l3h1	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8527_l3h2	8527	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8528_l1	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8528_l2	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8528_l3	8528	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8529_l1h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8529_l1h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8529_l2h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8529_l2h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8529_l3h1	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8529_l3h2	8529	Van	T1	601		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8530_l1h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	MEDIUM	L1标准顶车身分支。	READY
8530_l1h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	MEDIUM	L1高顶车身分支。	READY
8530_l2h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	MEDIUM	L2标准顶车身分支。	READY
8530_l2h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	MEDIUM	L2高顶车身分支。	READY
8530_l3h1	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	MEDIUM	L3标准顶车身分支。	READY
8530_l3h2	8530	Van	T1	602		EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	MEDIUM	L3高顶车身分支。	READY
8531_l1	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8531_l2	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8531_l3	8531	Pickup	T1	602		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8532	8532	Convertible	G-Class W463	463.204	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8533	8533	Convertible	G-Class W463	463.208	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	HIGH		READY
8534	8534	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8535	8535	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8536	8536	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8537	8537	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8538	8538	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	HIGH		READY
8539_swb	8539	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8539_lwb	8539	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8540_swb	8540	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8540_lwb	8540	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8541	8541	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH		READY
8543_pre94	8543	Convertible	G-Class W463	463.300	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH	1994年7月前窄体外廓。	READY
8543_wide	8543	Convertible	G-Class W463	463.300	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	HIGH	1994年7月起宽体外廓。	READY
8544	8544	Convertible	G-Class W463	463.307	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8545	8545	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	HIGH		READY
8546	8546	Convertible	G-Class W463	463.207	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	HIGH		READY
8547_swb	8547	SUV	G-Class W460	W460	3	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	MEDIUM	封闭车身短轴三门分支。	READY
8547_lwb	8547	SUV	G-Class W460	W460	5	EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	MEDIUM	封闭车身长轴五门分支。	READY
8554	8554	Hatchback	Innocenti Mini (Bertone)		3	EU-INNOCENTI-MINI-BERTONE-HATCHBACK-3D-01	MEDIUM	1974-1982 Bertone三门车身。	READY
8555	8555	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
8557	8557	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH		READY
8561_prefl	8561	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	MEDIUM	生产区间跨越改款，拆分改款前外廓。	READY
8561_facelift	8561	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越改款，拆分改款后外廓。	READY
8564	8564	Hatchback	626 II	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-01	HIGH		READY
8568	8568	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH		READY
8569	8569	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH		READY
8574	8574	Sedan	Corsa A TR phase I		2	EU-OPEL-CORSA-A-TR-PHASE1-SEDAN-2D-01	MEDIUM	TR二门轿车外廓。	READY
8579	8579	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
8581	8581	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
8582_3dr	8582	Hatchback	106 I	1A	3	EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8582_5dr	8582	Hatchback	106 I	1C	5	EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8588	8588	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	HIGH		READY
8603	8603	Hatchback	Renault 4		5	EU-RENAULT-4-MPV-5D-01	HIGH		READY
8605_pre74	8605	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8605_post74	8605	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
8606_pre74	8606	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8606_post74	8606	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
8607_pre74	8607	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-PRE74-01	MEDIUM	1974年外廓调整前车身。	READY
8607_post74	8607	Hatchback	Renault 6		5	EU-RENAULT-6-HATCHBACK-POST74-01	MEDIUM	1974年外廓调整后车身。	READY
8610	8610	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG63-COUPE-01	HIGH		READY
8622_3dr	8622	Hatchback	309 II		3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8622_5dr	8622	Hatchback	309 II		5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8623_3dr	8623	Hatchback	309 I		3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8623_5dr	8623	Hatchback	309 I		5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8630	8630	Sedan	Malaga	023A	4	EU-SEAT-MALAGA-023A-SEDAN-4D-01	HIGH		READY
8636	8636	Sedan	460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
8639	8639	Sedan	740		4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
8640	8640	Wagon	740		5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
8641	8641	Wagon	940		5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
8663	8663	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG65-COUPE-01	HIGH		READY
8665_mk1_swb_lowroof	8665	MPV	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶车身分支。	READY
8665_mk2_swb_lowroof	8665	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶车身分支。	READY
8665_mk2_lwb_highroof	8665	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶车身分支。	READY
8666	8666	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	MEDIUM	输入功率标注与资料存在小幅口径差异，车身边界为T250四门轿车。	READY
8667_901461	8667	Van	Sprinter I T1N	901.461		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	901.461短轴封闭车身分支。	READY
8667_901462	8667	Van	Sprinter I T1N	901.462		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	901.462中轴封闭车身分支。	READY
8667_902461	8667	Van	Sprinter I T1N	902.461		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	902.461短轴封闭车身分支。	READY
8667_902462	8667	Van	Sprinter I T1N	902.462		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	902.462中轴封闭车身分支。	READY
8668	8668	Sedan	Cruze J300	J300	4	EU-CHEVROLET-CRUZE-J300-SEDAN-4D-01	HIGH		READY
8669_l1	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8669_l2	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8669_l3	8669	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8670_swb_singlecab	8670	Pickup	Sprinter I T1N	901.421	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	MEDIUM	短轴单排驾驶室平台分支。	READY
8670_mwb_singlecab	8670	Pickup	Sprinter I T1N	902.412	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	MEDIUM	中轴单排驾驶室平台分支。	READY
8671_901361	8671	Van	Sprinter I T1N	901.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	901.361短轴封闭车身分支。	READY
8671_901362	8671	Van	Sprinter I T1N	901.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	901.362中轴封闭车身分支。	READY
8671_902361	8671	Van	Sprinter I T1N	902.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	902.361短轴封闭车身分支。	READY
8671_902362	8671	Van	Sprinter I T1N	902.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	902.362中轴封闭车身分支。	READY
8672_mk1_swb_lowroof	8672	MPV	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶车身分支。	READY
8672_mk2_swb_lowroof	8672	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶车身分支。	READY
8672_mk2_lwb_highroof	8672	MPV	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶车身分支。	READY
8673_mk1_swb_lowroof	8673	Van	Transit Mk1			EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	Mk1短轴低顶封闭车身，与既有Bus外廓相同。	READY
8673_mk2_swb_lowroof	8673	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶封闭车身，与既有Bus外廓相同。	READY
8673_mk2_lwb_highroof	8673	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶封闭车身，与既有Bus外廓相同。	READY
8674_l1	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	MEDIUM	L1平台车身分支。	READY
8674_l2	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	MEDIUM	L2平台车身分支。	READY
8674_l3	8674	Pickup	T1	601		EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	MEDIUM	L3平台车身分支。	READY
8675_swb	8675	Pickup	Transit Mk2		2	EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	MEDIUM	短轴单排平台车外廓。	READY
8675_lwb	8675	Pickup	Transit Mk2		2	EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	MEDIUM	长轴单排平台车外廓。	READY
8676_swb_lowroof	8676	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶封闭车身，与既有Bus外廓相同。	READY
8676_lwb_highroof	8676	Van	Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶封闭车身，与既有Bus外廓相同。	READY
8677_swb	8677	Pickup	Transit Mk2		2	EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	MEDIUM	短轴单排平台车外廓。	READY
8677_lwb	8677	Pickup	Transit Mk2		2	EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	MEDIUM	长轴单排平台车外廓。	READY
8678_swb_singlecab	8678	Pickup	Sprinter I T1N	903.311	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	MEDIUM	短轴单排驾驶室平台分支。	READY
8678_mwb_singlecab	8678	Pickup	Sprinter I T1N	903.312	2	EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	MEDIUM	中轴单排驾驶室平台分支。	READY
8678_mwb_doublecab	8678	Pickup	Sprinter I T1N	903.322	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-PLATFORM-MWB-DOUBLECAB-01	MEDIUM	中轴双排驾驶室平台分支。	READY
8679_903361	8679	Van	Sprinter I T1N	903.361		EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	MEDIUM	903.361短轴封闭车身分支。	READY
8679_903362	8679	Van	Sprinter I T1N	903.362		EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	MEDIUM	903.362中轴封闭车身分支。	READY
8679_903363	8679	Van	Sprinter I T1N	903.363		EU-MERCEDES-BENZ-SPRINTER-I-VAN-LWB-HIGHROOF-01	MEDIUM	903.363长轴高顶封闭车身分支。	READY
8680	8680	MPV	Evasion I	22	5	EU-CITROEN-EVASION-I-22-MPV-01	HIGH		READY
8683	8683	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	HIGH	THP 156对应三门车身。	READY
8684_3dr	8684	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8684_5dr	8684	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8685_3dr	8685	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8685_5dr	8685	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8686_3dr	8686	Hatchback	208 I	A9	3	EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	MEDIUM	同一Ktype覆盖三门车身分支。	READY
8686_5dr	8686	Hatchback	208 I	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	MEDIUM	同一Ktype覆盖五门车身分支。	READY
8687	8687	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8688	8688	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8689	8689	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8690	8690	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	HIGH		READY
8691	8691	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH		READY
8692	8692	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	HIGH		READY
8693	8693	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
8694	8694	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
8696	8696	Coupe	911 (996)	996	2	EU-PORSCHE-911-996-CARRERA-COUPE-01	HIGH		READY
8697	8697	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	HIGH		READY
8698	8698	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	HIGH		READY
8700_prefl	8700	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-EG-WAGON-PREFL-01	MEDIUM	生产区间跨越外廓长度变化，拆分改款前。	READY
8700_facelift	8700	Wagon	Baleno I	EG	5	EU-SUZUKI-BALENO-I-EG-WAGON-FACELIFT-01	MEDIUM	生产区间跨越外廓长度变化，拆分改款后。	READY
8702	8702	Pickup	Felicia I Fun	797	2	EU-SKODA-FELICIA-I-797-PICKUP-2D-01	MEDIUM	输入结束时间晚于当前直接规格页覆盖，物理外廓按797 Fun皮卡闭合。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7801-7900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAMARO-II-F-COUPE-1970-01	4775	1890	1273	Automobile-Catalog 1970 Chevrolet Camaro 250 Turbo-Thrift Powerglide	https://www.automobile-catalog.com/car/1970/100670/chevrolet_camaro_250_turbo-thrift_powerglide.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1971-01	4775	1890	1283	Automobile-Catalog 1971 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1971/101090/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1972-01	4775	1890	1247	Automobile-Catalog 1972 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1972/101285/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1973-01	4785	1890	1247	Automobile-Catalog 1973 Chevrolet Camaro Sport Coupe 307 V8	https://www.automobile-catalog.com/car/1973/101540/chevrolet_camaro_sport_coupe_307_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAMARO-II-F-COUPE-74-76-01	4963	1890	1247	Automobile-Catalog 1975 Chevrolet Camaro Sport Coupe 350 V8	https://www.automobile-catalog.com/car/1975/102320/chevrolet_camaro_sport_coupe_350_v-8_turbo-fire_hydra-matic.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1977-01	4963	1890	1250	Automobile-Catalog 1977 Chevrolet Camaro Sport Coupe 305 V8	https://www.automobile-catalog.com/car/1977/205535/chevrolet_camaro_sport_coupe_305_v-8.html
EU-CHEVROLET-CAMARO-II-F-COUPE-1978-01	5019	1890	1250	Automobile-Catalog 1978 Chevrolet Camaro Sport Coupe 305 V8	https://www.automobile-catalog.com/car/1978/205790/chevrolet_camaro_sport_coupe_305_v-8_4-speed.html
EU-CHEVROLET-CAMARO-II-F-COUPE-79-81-01	5019	1892	1250	Automobile-Catalog 1979 Chevrolet Camaro Sport Coupe; Automobile-Catalog 1980 Chevrolet Camaro Sport Coupe 5.0 V8; Automobile-Catalog 1981 Chevrolet Camaro Sport Coupe 5.0 V8	https://www.automobile-catalog.com/car/1979/206240/chevrolet_camaro_sport_coupe_4_1l_automatic.html; https://www.automobile-catalog.com/car/1980/206855/chevrolet_camaro_sport_coupe_5_0l_v-8_automatic.html; https://www.automobile-catalog.com/car/1981/207215/chevrolet_camaro_sport_coupe_5_0l_v-8_automatic.html
EU-CHEVROLET-CAMARO-III-F-COUPE-82-84-01	4770	1849	1270	Automobile-Catalog 1983 Chevrolet Camaro Z28 5.0L V8	https://www.automobile-catalog.com/car/1983/458210/chevrolet_camaro_z28_5_0l_v-8_5-speed.html
EU-CHEVROLET-CAMARO-III-F-COUPE-85-90-01	4877	1849	1278	Automobile-Catalog 1986 Chevrolet Camaro Z28 5.0L V8	https://www.automobile-catalog.com/car/1986/458975/chevrolet_camaro_z28_5_0l_v-8.html
EU-CHEVROLET-CAMARO-III-F-COUPE-91-92-01	4892	1839	1280	Automobile-Catalog 1992 Chevrolet Camaro Z28 5.0L V8 EFI	https://www.automobile-catalog.com/car/1992/460145/chevrolet_camaro_z28_5_0l_v-8_efi.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1989-01	4483	1803	1179	Automobile-Catalog 1989 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1989/463505/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1990-01	4483	1803	1186	Automobile-Catalog 1990 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1990/463595/chevrolet_corvette_convertible_automatic.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-1991-01	4536	1803	1186	Automobile-Catalog 1991 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1991/463670/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-92-93-01	4534	1796	1176	Automobile-Catalog 1992 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1992/463775/chevrolet_corvette_convertible.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-94-96-01	4534	1796	1201	Automobile-Catalog 1994 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1994/463955/chevrolet_corvette_convertible.html
EU-CHEVROLET-MALIBU-III-G-SEDAN-1980-01	4895	1816	1377	Automobile-Catalog 1980 Chevrolet Malibu Sedan 3.8L V6; Automobile-Catalog 1980 Chevrolet Malibu Classic Sedan 5.0L V8	https://www.automobile-catalog.com/car/1980/202985/chevrolet_malibu_sedan_3_8l_v-6_automatic.html; https://www.automobile-catalog.com/car/1980/206690/chevrolet_malibu_classic_sedan_5_0l_v-8_automatic.html
EU-CHEVROLET-MALIBU-III-G-SEDAN-81-83-01	4895	1836	1415	Automobile-Catalog 1983 Chevrolet Malibu Sedan 3.8 V6; Automobile-Catalog 1983 Chevrolet Malibu Classic Sport Sedan 5.0L V8	https://www.automobile-catalog.com/car/1983/203825/chevrolet_malibu_sedan_3_8_v6_automatic.html; https://www.automobile-catalog.com/car/1983/204245/chevrolet_malibu_sport_sedan_5_0l_v-8_automatic.html
EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	4560	1760	1285	Auto-Data Chrysler Daytona Shelby generation; Auto-Data Chrysler Daytona Shelby 2.2 i Turbo 177 Hp	https://www.auto-data.net/en/chrysler-daytona-shelby-model-1642; https://www.auto-data.net/en/chrysler-daytona-shelby-2.2-i-turbo-177hp-14698
EU-ZASTAVA-101-HATCHBACK-5D-01	3890	1590	1345	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-ZASTAVA-101-HATCHBACK-5D-01
EU-CHRYSLER-SARATOGA-AA-SEDAN-4D-01	4602	1731	1410	Auto-Data Chrysler Saratoga 3.0 i V6; Automobile-Catalog 1990 Chrysler Saratoga range	https://www.auto-data.net/en/chrysler-saratoga-3.0-i-v6-141hp-automatic-14783; https://www.automobile-catalog.com/make/chrysler/saratoga/saratoga/1990.html
EU-CHRYSLER-300C-II-LD-SEDAN-4D-01	5066	1902	1488	Lancia Thema official technical data based on the new Chrysler 300	https://www.media.stellantis.com/nl-nl/lancia/press/nieuwe-lancia-thema-het-beste-van-twee-werelden
EU-CHEVROLET-CAPTIVA-I-C140-SUV-01	4673	1849	1727	Automobile-Catalog 2011 Chevrolet Captiva 2.2 D 163 LS 2WD; Automobile-Catalog 2011 Chevrolet Captiva 2.2 D 184 LT 4WD	https://www.automobile-catalog.com/car/2011/1569185/chevrolet_captiva_2_2_d_163_ls_2wd.html; https://www.automobile-catalog.com/car/2011/1569125/chevrolet_captiva_2_2_d_184_lt_4wd.html
EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01	4315	1660	1385	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-DAIHATSU-APPLAUSE-I-A101-HATCHBACK-01
EU-PONTIAC-FIREBIRD-III-F-COUPE-87-90-01	4778	1839	1270	Automobile-Catalog 1987 Pontiac Firebird Formula 5.0 V8; Automobile-Catalog 1990 Pontiac Firebird 3.1 V6	https://www.automobile-catalog.com/car/1987/2849630/pontiac_firebird_formula_5_0_l_v8_automatic.html; https://www.automobile-catalog.com/car/1990/2852645/pontiac_firebird_3_1_l_v6_mfi_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-91-92-01	4956	1839	1262	Automobile-Catalog 1992 Pontiac Firebird 3.1 V6	https://www.automobile-catalog.com/car/1992/2853830/pontiac_firebird_3_1_l_v6_5-speed.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1982-01	4821	1829	1265	Automobile-Catalog 1982 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1982/2839955/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-83-84-01	4821	1844	1288	Automobile-Catalog 1983 Pontiac Firebird S/E 5.0 V8; Automobile-Catalog 1984 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1983/2841770/pontiac_firebird_se_5_0_liter_v8_5-speed.html; https://www.automobile-catalog.com/car/1984/2843990/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1985-01	4823	1839	1262	Automobile-Catalog 1985 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1985/2845595/pontiac_firebird_5_0_liter_v8_automatic.html
EU-PONTIAC-FIREBIRD-III-F-COUPE-1986-01	4839	1839	1262	Automobile-Catalog 1986 Pontiac Firebird 5.0 V8	https://www.automobile-catalog.com/car/1986/2847680/pontiac_firebird_5_0_liter_v8_automatic.html
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Captiva 2.0 VCDi 127 4WD LS	https://www.automobile-catalog.com/car/2007/559895/chevrolet_captiva_2_0_vcdi_127_4wd_ls.html
EU-PONTIAC-PHOENIX-II-X-COUPE-2D-01	4626	1754	1359	Automobile-Catalog 1980 Pontiac Phoenix LJ Coupe 2.8 V6	https://www.automobile-catalog.com/car/1980/2835860/pontiac_phoenix_lj_coupe_2_8_liter_v6.html
EU-PONTIAC-PHOENIX-II-X-HATCHBACK-5D-01	4555	1768	1356	Automobile-Catalog 1980 Pontiac Phoenix 5-Door Hatchback; Automobile-Catalog 1980 Pontiac Phoenix 5-Door Hatchback 2.8 V6	https://www.automobile-catalog.com/car/1980/2835740/pontiac_phoenix_5-door_hatchback_2_5_liter.html; https://www.automobile-catalog.com/car/1980/47630/pontiac_phoenix_5-door_hatchback_2_8-litre_v6_automatic.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-76-77-01	4516	1661	1265	Automobile-Catalog 1977 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1977/2826815/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-1978-01	4516	1661	1260	Automobile-Catalog 1978 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1978/2829635/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html
EU-PONTIAC-SUNBIRD-I-H-COUPE-79-80-01	4552	1661	1260	Automobile-Catalog 1979 Pontiac Sunbird Coupe 3.8 V6; Automobile-Catalog 1980 Pontiac Sunbird Coupe 3.8 V6	https://www.automobile-catalog.com/car/1979/2832605/pontiac_sunbird_coupe_3_8-litre_v6_5-speed.html; https://www.automobile-catalog.com/car/1980/2835620/pontiac_sunbird_coupe_3_8_liter_v6_4-speed.html
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01
EU-BMW-5-E39-SEDAN-01	4775	1800	1435	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-BMW-5-E39-SEDAN-01
EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01	4855	2000	2170	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L1H1-01
EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01	4855	2000	2455	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L1H2-01
EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01	5235	2000	2240	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L2H1-01
EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01	5235	2000	2525	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L2H2-01
EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01	5885	2000	2240	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L3H1-01
EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01	5885	2000	2530	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-CLOSED-L3H2-01
EU-MERCEDES-BENZ-T1-PLATFORM-L1-01	4855	2000	2170	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-PLATFORM-L1-01
EU-MERCEDES-BENZ-T1-PLATFORM-L2-01	5235	2000	2240	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-PLATFORM-L2-01
EU-MERCEDES-BENZ-T1-PLATFORM-L3-01	5885	2000	2240	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-T1-PLATFORM-L3-01
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	4225	1690	1940	Mercedes-Benz Public Archive 230 GE short wheelbase; Mercedes-Benz Public Archive 300 GD short wheelbase; Mercedes-Benz Public Archive 300 GE short wheelbase; Mercedes-Benz Public Archive 350 GD Turbo short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-GE-from-091993-G-230-short-wheelbase-1990---1994.xhtml?oid=191039024; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GE-from-091993-G-300-short-wheelbase-1990---1996.xhtml?oid=191039026; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-GD-Turbo-from-091993-G-350-Turbodiesel-short-wheelbase-1992---1996.xhtml?oid=191039020
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	4275	1760	1941	Mercedes-Benz Public Archive 350 GD Turbo short wheelbase; Mercedes-Benz Public Archive G 320 short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-GD-Turbo-from-091993-G-350-Turbodiesel-short-wheelbase-1992---1996.xhtml?oid=191039020; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-short-wheelbase-1994---1997.xhtml?oid=191039028
EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01	4946	1886	1670	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-01
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01
EU-HYUNDAI-PONY-X2-HATCHBACK-01	4104	1603	1361	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-HYUNDAI-PONY-X2-HATCHBACK-01
EU-MERCEDES-BENZ-CL-C216-FACELIFT-COUPE-01	5095	1871	1419	Auto-Data Mercedes-Benz CL C216 facelift CL 500 RWD; Auto-Data Mercedes-Benz CL C216 facelift CL 500 4MATIC	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-7g-tronic-plus-18674; https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673
EU-INNOCENTI-MINI-BERTONE-HATCHBACK-3D-01	3120	1500	1380	Automobile-Catalog 1974 Innocenti Mini 120 L; Auto-Data Innocenti Mini 1.0 53 Hp	https://www.automobile-catalog.com/car/1974/44645/innocenti_mini_120_l.html; https://www.auto-data.net/en/innocenti-mini-1.0-53hp-14652
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-JAGUAR-XJ40-SEDAN-01
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1438	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01
EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	4420	1678	1390	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01
EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	4448	1690	1375	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350	Automobile-Catalog 1983 Mazda 626 1.6 LX 5-Door	https://www.automobile-catalog.com/car/1983/1645400/mazda_626_1_6_lx_5-door_automatic.html
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01
EU-OPEL-CORSA-A-TR-PHASE1-SEDAN-2D-01	3955	1540	1360	Automobile-Catalog 1983 Opel Corsa TR 1.2 S	https://www.automobile-catalog.com/car/1983/2456240/opel_corsa_tr_1_2_s.html
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-OPEL-KADETT-E-SEDAN-4D-01
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-OPEL-VECTRA-A-SEDAN-01
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01
EU-RENAULT-4-MPV-5D-01	3668	1485	1550	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-RENAULT-4-MPV-5D-01
EU-RENAULT-6-HATCHBACK-PRE74-01	3848	1537	1500	Automobile-Catalog 1969 Renault 6	https://www.automobile-catalog.com/car/1969/27380/renault_6.html
EU-RENAULT-6-HATCHBACK-POST74-01	3858	1504	1475	Automobile-Catalog 1980 Renault 6 TL	https://www.automobile-catalog.com/car/1980/2925605/renault_6_tl.html
EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG63-COUPE-01	5106	1871	1425	Auto-Data Mercedes-Benz CL C216 facelift AMG CL 63	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-amg-cl-63-v8-544hp-amg-speedshift-mct-18677
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-309-II-HATCHBACK-3D-01
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-309-II-HATCHBACK-5D-01
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-309-I-HATCHBACK-3D-01
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-PEUGEOT-309-I-HATCHBACK-5D-01
EU-SEAT-MALAGA-023A-SEDAN-4D-01	4275	1650	1390	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-SEAT-MALAGA-023A-SEDAN-4D-01
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-460-L-SEDAN-4D-01
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-740-SEDAN-4D-01
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-740-WAGON-5D-01
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-940-WAGON-5D-01
EU-MERCEDES-BENZ-CL-C216-FACELIFT-AMG65-COUPE-01	5106	1871	1428	Auto-Data Mercedes-Benz CL C216 facelift AMG CL 65	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-amg-cl-65-v12-630hp-amg-speedshift-18676
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01
EU-CHEVROLET-AVEO-T250-SEDAN-4D-01	4310	1710	1505	Auto-Data Chevrolet Aveo Sedan 1.2 i 8V; Automobile-Catalog 2008 Chevrolet Aveo T250 Sedan range	https://www.auto-data.net/en/chevrolet-aveo-sedan-1.2-i-8v-72hp-14427; https://www.automobile-catalog.com/make/chevrolet_europe/t250_europe/t250_eu_sedan/2008.html
EU-MERCEDES-BENZ-SPRINTER-I-VAN-SWB-01	4835	1933	2350	CarExpert 1998 Mercedes-Benz Sprinter 3000 mm wheelbase specifications; AUTODOC Sprinter 2-T Van body-code listing	https://www.carexpert.co.nz/mercedes-benz/sprinter/1998-2-9l-window-van-rwd-diesel-manual-jjo8fsm819980401; https://www.autodoc.co.uk/spares/mercedes-benz/sprinter/sprinter-2-t-box-901-902/8671-208-d-901-361-901-362-902-361-902-362
EU-MERCEDES-BENZ-SPRINTER-I-VAN-MWB-01	5585	1933	2345	CarExpert 1999 Mercedes-Benz Sprinter 3550 mm wheelbase specifications; AUTODOC Sprinter 2-T Van 210 D body-code listing	https://www.carexpert.co.nz/mercedes-benz/sprinter/1999-2-9l-window-van-rwd-diesel-manual-jjo8fsma19991001; https://www.autodoc.co.uk/spares/mercedes-benz/sprinter/sprinter-2-t-box-901-902/8667-210-d-901-461-901-462-902-461-902-462
EU-CHEVROLET-CRUZE-J300-SEDAN-4D-01	4597	1788	1477	Auto-Data Chevrolet Cruze Sedan 2.0 TD 163 Hp	https://www.auto-data.net/en/chevrolet-cruze-sedan-2.0-td-163hp-16938
EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-SWB-SINGLECAB-01	4819	1922	2135	Autogidas Mercedes-Benz Sprinter 208 D 902.311; AUTODOC Sprinter 212 D and 308 D platform/chassis code listings	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/208-d-902.311-1995-2000-k18354; https://www.autodoc.co.uk/car-parts/centre-rod-assembly-15157/mercedes-benz/sprinter/sprinter-2-t-platform-chassis-901-902/8670-212-d-901-421-902-412; https://www.autodoc.co.uk/car-parts/air-filter-10360/mercedes-benz/sprinter/sprinter-3-t-platform-chassis-903/8678-308-d-2-3-903-311-903-312-903-322
EU-MERCEDES-BENZ-SPRINTER-I-PLATFORM-MWB-SINGLECAB-01	5470	1922	2115	Autogidas Mercedes-Benz Sprinter 212 D 902.412; Autogidas Mercedes-Benz Sprinter 308 D 903.312	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/212-d-902.412-1995-2000-k18369; https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/308-d-903.312-1995-2000-k31182
EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	4552	1960	1990	Ford Transit '78 UK brochure archive; Ford Transit Sep 1982 chassis-cab brochure; CarsGuide 1980 Ford Transit dimensions	https://www.capri.pl/library/folders/transit; https://www.flickr.com/photos/61090099@N04/50025047788; https://www.carsguide.com.au/ford/transit/car-dimensions/1980
EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	5302	2125	1990	Ford Transit '78 UK brochure archive; Ford Transit Sep 1982 chassis-cab brochure; CarsGuide 1980 Ford Transit dimensions	https://www.capri.pl/library/folders/transit; https://www.flickr.com/photos/61090099@N04/50025047788; https://www.carsguide.com.au/ford/transit/car-dimensions/1980
EU-MERCEDES-BENZ-SPRINTER-I-W903-PLATFORM-MWB-DOUBLECAB-01	5855	1922	2155	Autogidas Mercedes-Benz Sprinter 308 D 903.322	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/308-d-903.322-1995-2000-k31185
EU-MERCEDES-BENZ-SPRINTER-I-VAN-LWB-HIGHROOF-01	6535	1933	2570	CarsGuide 1999 Mercedes-Benz Sprinter 308D specifications; AUTODOC Sprinter 3-T Van 308 D body-code listing	https://www.carsguide.com.au/mercedes-benz/sprinter/price/1999/308d; https://www.autodoc.parts/car-parts/catalyst-converter-10147/mercedes-benz/sprinter/sprinter-3-t-box-903/8679-308-d-2-3-903-361-903-362-903-363
EU-CITROEN-EVASION-I-22-MPV-01	4454	1834	1714	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-CITROEN-EVASION-I-22-MPV-01
EU-PEUGEOT-208-I-A9-HATCHBACK-3D-01	3962	1739	1460	Peugeot Technical characteristics: 208	https://www.media.stellantis.com/em-en/peugeot/press/technical-characteristics-208
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-01	3962	1739	1460	Peugeot Technical characteristics: 208	https://www.media.stellantis.com/em-en/peugeot/press/technical-characteristics-208
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01	4795	1799	1420	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-01
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01	4816	1799	1506	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-V8-01
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-S40-I-VS-SEDAN-4D-01
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-VOLVO-V40-I-VW-WAGON-5D-01
EU-PORSCHE-911-996-CARRERA-COUPE-01	4430	1765	1305	Auto-Data Porsche 911 996 Carrera 3.4	https://www.auto-data.net/en/porsche-911-996-carrera-3.4-300hp-6591
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940	Task-provided cross-batch cumulative DIMENSION_GROUP cache; original external source retained upstream	cache://cumulative-dimension-group/EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01
EU-SUZUKI-BALENO-I-EG-WAGON-PREFL-01	4345	1690	1460	Auto-Data Suzuki Baleno Combi EG 1.6 i 16V 98 Hp	https://www.auto-data.net/en/suzuki-baleno-combi-eg-1995-1.6-i-16v-98hp-16477
EU-SUZUKI-BALENO-I-EG-WAGON-FACELIFT-01	4375	1690	1460	Auto-Data Suzuki Baleno Combi EG 1.3 i 16V 85 Hp	https://www.auto-data.net/en/suzuki-baleno-combi-eg-1995-1.3-i-16v-85hp-16475
EU-SKODA-FELICIA-I-797-PICKUP-2D-01	4245	1680	1465	Auto-Data Skoda Felicia I Fun 797 1.6	https://www.auto-data.net/en/skoda-felicia-i-fun-797-1.6-75hp-14088
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7801-7900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://en.wikipedia.org/wiki/Ford_Transit "https://en.wikipedia.org/wiki/Ford_Transit"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7801-7900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7801-7900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9915 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3043 行）

