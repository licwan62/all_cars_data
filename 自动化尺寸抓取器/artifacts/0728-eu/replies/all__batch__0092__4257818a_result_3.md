# 任务：all 第 9101-9200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0092__4257818a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 9101-9200 行

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
all 第 9101-9200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_9101-9200_ktype_dimension_mapping_final.tsv
- all_9101-9200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-E39-WAGON-01	4805	1800	1440
EU-BMW-700-LS-SEDAN-LWB-01	3860	1480	1360
EU-BMW-700-SEDAN-SWB-01	3540	1480	1320
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-BMW-X3-F25-SUV-PREFL-01	4648	1881	1661
EU-CADILLAC-CTS-II-SEDAN-01	4867	1842	1473
EU-CADILLAC-ESCALADE-I-GMT400-SUV-5D-01	5110	1956	1887
EU-CHEVROLET-AVEO-II-T300-HATCHBACK-5D-01	4039	1735	1517
EU-CHEVROLET-AVEO-II-T300-SEDAN-4D-01	4399	1735	1517
EU-NISSAN-PICK-UP-D21-KING-CAB-83PS-01	4825	1735	1725
EU-NISSAN-PICK-UP-D22-DOUBLE-CAB-4X4-01	5080	1825	1705
EU-NISSAN-PICK-UP-D22-KING-CAB-2WD-01	4975	1690	1610
EU-NISSAN-PICK-UP-D22-KING-CAB-4X4-01	4975	1820	1700
EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	4466	1840	1482
EU-OPEL-VECTRA-B-I500-SEDAN-FACELIFT-01	4477	1707	1395
EU-OPEL-VECTRA-B-I500-SEDAN-PREFL-01	4477	1707	1395
EU-OPEL-VECTRA-B-I500-WAGON-FACELIFT-01	4490	1707	1460
EU-OPEL-VECTRA-B-I500-WAGON-PREFL-01	4490	1707	1460
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490
EU-ROVER-75-RJ-SEDAN-FACELIFT-01	4749	1778	1424
EU-ROVER-75-RJ-SEDAN-PREFL-01	4747	1778	1424
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-01	4785	1700	1795
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-FACELIFT-STEP-01	4915	1700	1795
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-DOUBLE-PREFL-01	4725	1690	1800
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-01	4785	1700	1765
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-FACELIFT-STEP-01	4915	1700	1765
EU-TOYOTA-HILUX-VI-RZN168-PICKUP-SINGLE-PREFL-01	4725	1690	1760
EU-VW-GOLF-VI-GTI-HATCHBACK-3D-01	4213	1779	1469
EU-VW-GOLF-VI-GTI-HATCHBACK-5D-01	4213	1786	1469

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Movano a	2.8 DTI	Bus	Frontantrieb	Diesel	84	114	Jul 1998	Oct 2001	2024-03-01	10460
Rover	75	2.0 V6	Stufenheck	Frontantrieb	Benzin	110	150	Feb 1999	May 2005	2024-03-01	10461
Rover	75	2.5 V6	Stufenheck	Frontantrieb	Benzin	129	175	Feb 1999	Oct 2001	2024-03-01	10462
Rover	75	2.0 CDT	Stufenheck	Frontantrieb	Diesel	85	115	Feb 1999	May 2005	2024-03-01	10463
Audi	A3	1.8 T Quattro	Schrägheck	Allrad	Benzin	132	180	Oct 1998	May 2003	2024-03-01	10465
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	50	68	Apr 1999	Sep 2005	2024-03-01	10466
Audi	A8 d2	4.2 Quattro	Stufenheck	Allrad	Benzin	228	310	Nov 1998	Sep 2002	2024-03-01	10467
Audi	A8 d2	3.7 Quattro	Stufenheck	Allrad	Benzin	191	260	Nov 1998	Sep 2002	2024-03-01	10468
Honda	S2000	2	Cabriolet	Heckantrieb	Benzin	177	240	Jun 1999	Jun 2009	2025-12-01	10469
Toyota	Hilux v	1.8	Pick-up	Heckantrieb	Benzin	61	83	Sep 1988	Jun 1998	2024-03-01	10473
Opel	Astra j gtc	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Oct 2011	Jun 2013	2024-05-01	10474
Opel	Astra j gtc	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	121	165	Jan 2012	Jun 2015	2024-05-01	10475
Toyota	Camry	2.4 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	140	190	Jan 2006	Sep 2011	2024-03-01	10477
Toyota	Hilux v	2.4 D	Pick-up	Heckantrieb	Diesel	58	79	Mar 1995	Aug 1997	2024-03-01	10479
VW	Taro	2.4 D	Pick-up	Heckantrieb	Diesel	58	79	Jul 1994	Mar 1997	2024-03-01	10480
VW	Taro	2.4 D	Pick-up	Heckantrieb	Diesel	61	83	Jun 1989	Mar 1997	2024-03-01	10481
BMW	5	535 I Xdrive	Stufenheck	Allrad	Benzin	225	306	Mar 2011	Oct 2016	2024-03-01	10483
Cadillac	Cts	3.0 AWD	Kombi	Allrad	Benzin	203	276	Jan 2008	-	2024-03-01	10485
Cadillac	Cts	3	Coupe	Heckantrieb	Benzin	201	273	Jan 2010	Dec 2013	2024-03-01	10489
Cadillac	Cts	3.0 AWD	Coupe	Allrad	Benzin	201	273	Jan 2010	Dec 2013	2024-03-01	10490
Mitsubishi	Pajero iv	3.2 Di-d 4WD	SUV	Allrad	Diesel	140	190	Feb 2007	-	2024-03-01	10491
Mitsubishi	Pajero iv	3.0 4WD	SUV	Allrad	Benzin	131	178	Feb 2007	-	2024-03-01	10492
Cadillac	Escalade	6.0 Hybrid	SUV	Heckantrieb	Benzin/Elektro	283	385	Nov 2010	Dec 2013	2024-03-01	10493
Cadillac	Srx	2.8 AWD	SUV	Allrad	Benzin	224	305	Jan 2009	Dec 2016	2024-03-01	10497
Fiat	Multipla	1.6 100 16V	Großraumlimousine	Frontantrieb	Benzin	76	103	Apr 1999	Aug 2000	2026-02-01	10499
Fiat	Multipla	1.9 JTD 105	Großraumlimousine	Frontantrieb	Diesel	77	105	Apr 1999	Aug 2000	2026-02-01	10500
BMW	3	323 CI	Coupe	Heckantrieb	Benzin	125	170	Apr 1999	Sep 2000	2024-03-01	10502
BMW	3	328 CI	Coupe	Heckantrieb	Benzin	142	193	Dec 1998	May 2000	2024-03-01	10503
Mercedes-benz	M-Klasse	ML 430	SUV	Allrad	Benzin	200	272	Feb 1998	Jun 2005	2024-03-01	10504
Cadillac	Escalade	6.2 Flexfuel	SUV	Heckantrieb	Benzin/Ethanol	301	409	Oct 2006	Dec 2014	2024-03-01	10505
Cadillac	Escalade	6.2 Flexfuel AWD	SUV	Allrad	Benzin/Ethanol	301	409	Oct 2006	Dec 2014	2024-03-01	10506
Cadillac	Sts	4.4 Kompressor AWD	Stufenheck	Allrad	Benzin	350	476	Sep 2005	Dec 2007	2024-03-01	10507
Toyota	Camry	1.8 Turbo-d	Stufenheck	Frontantrieb	Diesel	54	73	Oct 1982	Oct 1986	2024-03-01	10519
Toyota	Carina ii	1.8	Stufenheck	Heckantrieb	Benzin	63	86	Jan 1982	Sep 1983	2024-03-01	10521
Audi	A3	RS3 Quattro	Schrägheck	Allrad	Benzin	250	340	Jan 2011	Dec 2012	2024-03-01	10523
VW	Golf vi	2.0 GTI	Schrägheck	Frontantrieb	Benzin	173	235	May 2011	Nov 2012	2024-03-01	10524
Renault	Scénic iii	1.6 DCI	Großraumlimousine	Frontantrieb	Diesel	96	130	Apr 2011	Sep 2016	2024-05-01	10527
Renault	Grand scénic iii	1.6 DCI	Großraumlimousine	Frontantrieb	Diesel	96	130	Apr 2011	Sep 2016	2024-05-01	10528
Toyota	Prius	1.8 Hybrid	Großraumlimousine	Frontantrieb	Benzin/Elektro	100	136	May 2011	-	2024-03-01	10538
Land Rover	Freelander i soft top	1.8 I 16V 4X4	Geländewagen offen	Allrad	Benzin	88	120	Feb 1998	Oct 2006	2024-03-01	10539
Land Rover	Freelander i soft top	2.0 DI 4X4	Geländewagen offen	Allrad	Diesel	72	98	Feb 1998	Oct 2006	2024-03-01	10541
Fiat	Doblo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Feb 2011	Dec 2023	2025-02-03	10543
Citroën	Jumpy i	2.0 HDI 110	Bus	Frontantrieb	Diesel	80	109	Mar 2000	Oct 2006	2024-03-01	10544
Citroën	Jumpy i	2.0 HDI 110	Kasten	Frontantrieb	Diesel	80	109	Jan 2002	Oct 2006	2024-03-01	10545
Citroën	Jumpy i	2.0 HDI 110 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	80	109	Dec 2003	Oct 2006	2024-03-01	10546
Hyundai	H100	2.5 D	Kasten	Heckantrieb	Diesel	57	78	Dec 1994	Mar 2000	2024-03-01	10559
Hyundai	H100	2.5 D	Kasten	Heckantrieb	Diesel	55	75	Jul 1993	Dec 1994	2024-03-01	10560
Mazda	323 s iv	1.8 16V GT	Stufenheck	Frontantrieb	Benzin	94	128	Jun 1989	Jul 1994	2024-03-01	10561
Chrysler	Sebring	2.4	Stufenheck	Frontantrieb	Benzin	105	143	Apr 2001	Jun 2007	2024-03-01	10565
Opel	Vectra b	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	85	116	Oct 1995	Sep 2000	2024-03-01	10570
Piaggio	Porter	1.3 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	52	71	Jan 2011	-	2024-03-01	10571
Chevrolet	Aveo	1.2	Stufenheck	Frontantrieb	Benzin	51	69	Mar 2011	-	2024-03-01	10572
Skoda	Superb ii	2.0 TDI 16V 4X4	Kombi	Allrad	Diesel	103	140	Nov 2010	May 2015	2024-03-01	10573
Skoda	Superb ii	2.0 TDI 16V 4X4	Schrägheck	Allrad	Diesel	103	140	Nov 2010	May 2015	2024-03-01	10574
BMW	X3	Xdrive 20 D	SUV	Allrad	Diesel	120	163	Sep 2008	Aug 2010	2024-03-01	10575
BMW	X3	Xdrive 30 D	SUV	Allrad	Diesel	190	258	Apr 2011	Aug 2017	2024-03-01	10576
VW	Passat b7	1.4 TSI Multifuel	Stufenheck	Frontantrieb	Benzin/Ethanol	118	160	Nov 2010	Dec 2014	2024-03-01	10577
BMW	X3	Xdrive 30 D	SUV	Allrad	Diesel	155	211	Sep 2008	Aug 2010	2024-03-01	10578
BMW	5	525 TDS	Kombi	Heckantrieb	Diesel	105	143	Mar 1997	May 2004	2024-03-01	10579
Honda	Prelude	2.0 I EX 16V	Coupe	Frontantrieb	Benzin	110	150	Oct 1987	Dec 1990	2026-01-01	10581
Fiat	Bravo i	1.9 JTD 105	Schrägheck	Frontantrieb	Diesel	77	105	Dec 1998	Oct 2001	2024-03-01	10582
Fiat	Brava	1.9 JTD 105	Schrägheck	Frontantrieb	Diesel	77	105	Dec 1998	Oct 2001	2024-03-01	10583
BMW	600	0.6	Schrägheck	Heckantrieb	Benzin	15	20	Dec 1957	May 1961	2024-03-01	10584
Opel	Kadett e combo	1.4 S	Kasten/Kombi	Frontantrieb	Benzin	55	75	Jul 1989	Aug 1991	2024-03-01	10585
VW	Passat b7 variant	1.4 TSI Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	118	160	Nov 2010	Dec 2014	2024-03-01	10586
Opel	Kadett e combo	1.6 I	Kasten/Kombi	Frontantrieb	Benzin	55	75	Aug 1991	Jul 1994	2024-03-01	10588
Opel	Kadett e combo	1.4 I	Kasten/Kombi	Frontantrieb	Benzin	44	60	Aug 1991	Jul 1994	2024-03-01	10589
VW	Transporter t2	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	37	50	Aug 1968	Jul 1979	2024-03-01	10590
VW	Lt 28-35 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	55	75	Dec 1978	Feb 1991	2024-03-01	10591
VW	Caddy ii	1.6	Pick-up	Frontantrieb	Benzin	55	75	Jun 1996	Dec 2000	2024-03-01	10592
VW	Caddy ii	1.9 D	Pick-up	Frontantrieb	Diesel	47	64	Jun 1996	Dec 2000	2024-03-01	10593
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	152	207	Oct 1996	Dec 2001	2024-03-01	10594
Mitsubishi	L 300 / delica ii	1.6	Pritsche/Fahrgestell	Heckantrieb	Benzin	51	70	Apr 1983	Apr 1994	2024-03-01	10595
Mitsubishi	L 300 / delica ii	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	51	69	Nov 1986	Apr 1994	2024-03-01	10597
Mitsubishi	L 300 iii	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	85	116	Jul 1994	Apr 2000	2024-03-01	10598
Mitsubishi	L 300 iii	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	64	87	Nov 1994	Apr 2000	2024-03-01	10599
BMW	7	730 D	Stufenheck	Heckantrieb	Diesel	155	211	Sep 2003	Aug 2008	2024-03-01	10600
BMW	5	530 D	Schrägheck	Heckantrieb	Diesel	155	211	Sep 2010	Feb 2017	2024-03-01	10601
Hyundai	Ix20	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	85	116	Jun 2011	Jul 2019	2024-03-01	10602
Hyundai	Ix20	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	57	78	Jun 2011	Jul 2019	2024-03-01	10604
Hyundai	I30	1.4	Kombi	Frontantrieb	Benzin	77	105	Oct 2007	Jun 2012	2024-03-01	10609
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	85	115	May 2011	Dec 2022	2024-03-01	10615
Hyundai	I40 i cw	1.6 GDI	Kombi	Frontantrieb	Benzin	99	135	Jul 2011	May 2019	2024-03-01	10618
Hyundai	I40 i cw	2.0 GDI	Kombi	Frontantrieb	Benzin	130	177	Jul 2011	May 2019	2024-03-01	10620
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	103	140	May 2011	Apr 2015	2024-03-01	10621
Hyundai	I40 i cw	1.7 Crdi	Kombi	Frontantrieb	Diesel	85	116	Jul 2011	May 2019	2024-03-01	10622
Hyundai	I40 i cw	1.7 Crdi	Kombi	Frontantrieb	Diesel	100	136	Jul 2011	May 2019	2024-03-01	10623
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	100	136	Jun 2010	May 2011	2024-03-01	10625
Dodge	Ramcharger	5.2 4WD	SUV	Allrad	Benzin	164	223	Jan 1999	Dec 2001	2024-03-01	10630
Dodge	Ramcharger	5.9 4WD	SUV	Allrad	Benzin	183	249	Jan 1999	Dec 2001	2024-03-01	10631
Dodge	Ram 1500	3.9	Pick-up	Heckantrieb	Benzin	130	177	Jan 1993	Aug 2002	2024-03-01	10632
Seat	Ibiza iv sc	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	81	May 2011	May 2015	2025-06-01	10637
Mercedes-benz	Sls amg roadster	6.2	Cabriolet	Heckantrieb	Benzin	420	571	Jun 2011	-	2024-03-01	10638
Nissan	Sunny	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	40	54	Nov 1990	Mar 2000	2024-03-01	10639
Nissan	Pick up	1.8	Pick-up	Heckantrieb	Benzin	59	80	Jan 1983	Mar 1986	2024-03-01	10640
Nissan	Pick up	2.2 4WD	Pick-up	Allrad	Benzin	71	97	Apr 1983	Mar 1986	2024-03-01	10641
Nissan	Pick up	2.3 D	Pick-up	Heckantrieb	Diesel	51	69	Apr 1983	Mar 1986	2024-03-01	10642
Seat	Ibiza iv	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	81	May 2011	May 2015	2024-03-01	10643
Nissan	Pick up	2.5 D 4WD	Pick-up	Allrad	Diesel	53	72	Apr 1983	Mar 1986	2024-03-01	10644
Nissan	Sunny	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	105	143	Oct 1990	May 1995	2024-03-01	10645


--- Round 1 / 首次发送 ---
## 更新点

* 复用任务给定的锁定尺寸组，闭合 Rover 75、Opel Astra J GTC、VW Golf VI GTI、Chevrolet Aveo T300 Sedan、BMW 5 E39 Touring 共 7 个既有尺寸组；未重复输出尺寸事实。
* 首次建立 Audi A3 8L 1.8 T quattro 的三门/五门、改款前/改款后 4 个尺寸组。Audi 官方技术规格明确给出 3/5 门以及 `4152 × 1735 × 1427 mm`，其中宽度明确为不含后视镜；Auto-Data 用于区分 1998–2000 与 2000–2003 两个阶段。([Audi Press][1])
* 首次建立 Toyota Yaris I XP10 的三门/五门、改款前/改款后 4 个尺寸组。改款前为 `3615 × 1660 × 1500 mm`，改款后普通版为 `3640 × 1660 × 1500 mm`；Toyota 官方资料确认门数与改款外观变化，Automobile-Catalog 明确宽度为不含后视镜。([丰田媒体][2])
* 本轮未重新核对已经锁定的跨批次尺寸组三维和来源。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：10
* READY 映射行：19
* PENDING Ktype：90
* 本轮首次创建尺寸组：8
* 本轮复用锁定尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10461_prefl	10461	Sedan	Rover 75	RJ	4	EU-ROVER-75-RJ-SEDAN-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前四门轿车外廓。	READY
10461_facelift	10461	Sedan	Rover 75	RJ	4	EU-ROVER-75-RJ-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后四门轿车外廓。	READY
10462	10462	Sedan	Rover 75	RJ	4	EU-ROVER-75-RJ-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
10463_prefl	10463	Sedan	Rover 75	RJ	4	EU-ROVER-75-RJ-SEDAN-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前四门轿车外廓。	READY
10463_facelift	10463	Sedan	Rover 75	RJ	4	EU-ROVER-75-RJ-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后四门轿车外廓。	READY
10465_3dr_prefl	10465	Hatchback	Audi A3 I (8L)	8L	3	EU-AUDI-A3-I-8L-HATCHBACK-3D-PREFL-01	HIGH	Ktype未区分门数且跨2000年改款，拆分三门改款前分支。	READY
10465_3dr_facelift	10465	Hatchback	Audi A3 I (8L)	8L	3	EU-AUDI-A3-I-8L-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype未区分门数且跨2000年改款，拆分三门改款后分支。	READY
10465_5dr_prefl	10465	Hatchback	Audi A3 I (8L)	8L	5	EU-AUDI-A3-I-8L-HATCHBACK-5D-PREFL-01	HIGH	Ktype未区分门数且跨2000年改款，拆分五门改款前分支。	READY
10465_5dr_facelift	10465	Hatchback	Audi A3 I (8L)	8L	5	EU-AUDI-A3-I-8L-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype未区分门数且跨2000年改款，拆分五门改款后分支。	READY
10466_3dr_prefl	10466	Hatchback	Yaris I (XP10)	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	MEDIUM	Ktype未区分门数且跨2003年改款，拆分三门改款前分支。	READY
10466_3dr_facelift	10466	Hatchback	Yaris I (XP10)	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	MEDIUM	Ktype未区分门数且跨2003年改款，拆分三门改款后分支。	READY
10466_5dr_prefl	10466	Hatchback	Yaris I (XP10)	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype未区分门数且跨2003年改款，拆分五门改款前分支。	READY
10466_5dr_facelift	10466	Hatchback	Yaris I (XP10)	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype未区分门数且跨2003年改款，拆分五门改款后分支。	READY
10474	10474	Hatchback	Astra J GTC		3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	HIGH	GTC三门物理外廓。	READY
10475	10475	Hatchback	Astra J GTC		3	EU-OPEL-ASTRA-J-GTC-HATCHBACK-3D-01	HIGH	GTC三门物理外廓。	READY
10524_3dr	10524	Hatchback	Golf VI GTI	5K1	3	EU-VW-GOLF-VI-GTI-HATCHBACK-3D-01	HIGH	Ktype未区分门数，拆分三门GTI外廓。	READY
10524_5dr	10524	Hatchback	Golf VI GTI	5K1	5	EU-VW-GOLF-VI-GTI-HATCHBACK-5D-01	HIGH	Ktype未区分门数，拆分五门GTI外廓。	READY
10572	10572	Sedan	Aveo II (T300)	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-4D-01	HIGH	T300四门轿车外廓。	READY
10579	10579	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH	E39 Touring五门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A3-I-8L-HATCHBACK-3D-PREFL-01	4152	1735	1427	Auto-Data; Audi UK technical specification	https://www.auto-data.net/en/audi-a3-8l-1.8-t-180hp-quattro-4241; https://press.audi.co.uk/assets/documents/original/10061-AudiUK00001930A318TquattroSportTechnical.pdf
EU-AUDI-A3-I-8L-HATCHBACK-3D-FACELIFT-01	4152	1735	1427	Audi UK technical specification; Auto-Data	https://press.audi.co.uk/assets/documents/original/10061-AudiUK00001930A318TquattroSportTechnical.pdf; https://www.auto-data.net/en/audi-a3-8l-facelift-2000-1.8-t-180hp-quattro-27023
EU-AUDI-A3-I-8L-HATCHBACK-5D-PREFL-01	4152	1735	1427	Auto-Data; Audi UK technical specification	https://www.auto-data.net/en/audi-a3-8l-1.8-t-180hp-quattro-4241; https://press.audi.co.uk/assets/documents/original/10061-AudiUK00001930A318TquattroSportTechnical.pdf
EU-AUDI-A3-I-8L-HATCHBACK-5D-FACELIFT-01	4152	1735	1427	Audi UK technical specification; Auto-Data	https://press.audi.co.uk/assets/documents/original/10061-AudiUK00001930A318TquattroSportTechnical.pdf; https://www.auto-data.net/en/audi-a3-8l-facelift-2000-1.8-t-180hp-quattro-27023
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-PREFL-01	3615	1660	1500	Toyota Media Site; Automobile-Catalog	https://media.toyota.co.uk/toyota-yaris-family-grows-with-new-1-3-litre-models/; https://www.automobile-catalog.com/car/1999/3655865/toyota_yaris_1_0.html
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3640	1660	1500	Toyota Media Site; Automobile-Catalog	https://media.toyota.co.uk/toyota-yaris-more-safety-style-comfort-and-performance/; https://www.automobile-catalog.com/car/2004/3656000/toyota_yaris_1_0.html
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-PREFL-01	3615	1660	1500	Toyota Media Site; Automobile-Catalog	https://media.toyota.co.uk/toyota-yaris-family-grows-with-new-1-3-litre-models/; https://www.automobile-catalog.com/car/1999/3655865/toyota_yaris_1_0.html
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3640	1660	1500	Toyota Media Site; Automobile-Catalog	https://media.toyota.co.uk/toyota-yaris-more-safety-style-comfort-and-performance/; https://www.automobile-catalog.com/car/2004/3656000/toyota_yaris_1_0.html
```

## 下一步优先处理

1. 聚类 Opel Movano A、Citroën Jumpy I、Hyundai H100 等 Bus/Van/Chassis 车型，优先确定轴距、车顶和客车/厢式/底盘边界。
2. 集中核对 Toyota Hilux V/VW Taro、Nissan Pick-up、Mitsubishi L300 等早期商用车的驾驶室、货斗及 2WD/4WD 外廓差异。
3. 处理 Audi A8 D2 facelift、Honda S2000、Toyota Camry、BMW F10/F07/F25、Cadillac CTS/SRX/Escalade 等乘用车簇；Honda S2000 暂不建组，优先解决不同资料中的高度口径冲突。

推进信号：CONTINUE

[1]: https://press.audi.co.uk/assets/documents/original/10061-AudiUK00001930A318TquattroSportTechnical.pdf "A3 1.8 TSport quattro 6spd Tech Spec.doc"
[2]: https://media.toyota.co.uk/toyota-yaris-family-grows-with-new-1-3-litre-models/ "Toyota Yaris Family Grows With New 1.3-Litre Models - Toyota Media Site"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_9101-9200_ktype_dimension_mapping_final.tsv
- all_9101-9200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Honda S2000 两门敞篷外廓，建立 `4135 × 1750 × 1285 mm` 尺寸组。([本田新闻][1])
* BMW 535i xDrive F10 的生产区间跨越改款，按官方规格拆分为改款前 `4899 × 1860 × 1464 mm` 与改款后 `4907 × 1860 × 1464 mm` 两个尺寸组。([BMW Group PressClub][2])
* 闭合第三代 Toyota Prius 五门掀背外廓，建立 `4460 × 1745 × 1490 mm` 尺寸组。([丰田媒体][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：13
* READY 映射行：23
* PENDING Ktype：87
* 已确认且被当前映射引用的尺寸组：19
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10469	10469	Convertible	S2000		2	EU-HONDA-S2000-CONVERTIBLE-01	HIGH	两门敞篷外廓。	READY
10483_prefl	10483	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前四门轿车外廓。	READY
10483_facelift	10483	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后四门轿车外廓。	READY
10538	10538	Hatchback	Prius III		5	EU-TOYOTA-PRIUS-III-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-S2000-CONVERTIBLE-01	4135	1750	1285	Honda News Europe	https://hondanews.eu/eu/fi/cars/media/pressreleases/34329/honda-s2000-99
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	BMW Group PressClub	https://www.press.bmwgroup.com/greece/article/attachment/T0123463EL/180707
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	BMW Group PressClub	https://www.press.bmwgroup.com/global/article/attachment/T0143206EN/224275
EU-TOYOTA-PRIUS-III-HATCHBACK-5D-01	4460	1745	1490	Toyota Media Site	https://media.toyota.co.uk/european-debut-for-new-toyota-prius/
```

## 下一步优先处理

1. 批量闭合 BMW X3 E83/F25、Cadillac CTS/SRX/Escalade 与 Mitsubishi Pajero IV 等 SUV 和乘用车簇。
2. 随后处理 Passat B7、Superb II、Scénic III、Alhambra 与 Hyundai i40 等同平台或同车身多动力 Ktype。
3. 最后集中拆解 Movano、Jumpy、H100、Hilux/Taro、Nissan Pick-up 与 L300 等存在轴距、车顶、驾驶室或货斗差异的商用车。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/fi/cars/media/pressreleases/34329/honda-s2000-99?utm_source=chatgpt.com "Honda S2000 99"
[2]: https://www.press.bmwgroup.com/greece/article/attachment/T0123463EL/180707 "BMW Group PressClub"
[3]: https://media.toyota.co.uk/vehicles/prius-archive-2009/?utm_source=chatgpt.com "Prius (3rd generation, 2009–2016) - Toyota Media Site"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_9101-9200_ktype_dimension_mapping_final.tsv
- all_9101-9200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 BMW X3 E83 改款后 2 个 Ktype；F25 Ktype 按改款前后拆分，改款前复用既有尺寸组，改款后首次建组。BMW 官方资料确认 E83 为 `4569 × 1853 × 1674 mm`；F25 改款仅增加车长，欧洲规格为 `4657 × 1881 × 1661 mm`。([BMW Group PressClub][1])
* 闭合 VW Passat B7 Sedan 与 Variant 两个 Ktype，分别建立四门轿车和五门旅行车尺寸组；对应规格明确区分车身宽度与含后视镜宽度。([汽车数据网][2])
* Hyundai ix20 与 i40 CW 的 Ktype 均跨越改款，按改款前后拆分；相同动力 Ktype 批量复用对应车身尺寸组。ix20 为 `4100/4115 × 1765 × 1600 mm`，i40 CW 为 `4770/4775 × 1815 × 1470 mm`。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：24
* READY 映射行：39
* PENDING Ktype：76
* 已确认且被当前映射引用的尺寸组：28
* 本轮首次创建尺寸组：8
* 本轮新增复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10575	10575	SUV	X3 I (E83)	E83	5	EU-BMW-X3-E83-SUV-FACELIFT-01	HIGH	E83改款后五门SUV外廓。	READY
10576_prefl	10576	SUV	X3 II (F25)	F25	5	EU-BMW-X3-F25-SUV-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门SUV外廓。	READY
10576_facelift	10576	SUV	X3 II (F25)	F25	5	EU-BMW-X3-F25-SUV-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门SUV外廓。	READY
10577	10577	Sedan	Passat B7	362	4	EU-VW-PASSAT-B7-SEDAN-01	HIGH	B7四门轿车外廓。	READY
10578	10578	SUV	X3 I (E83)	E83	5	EU-BMW-X3-E83-SUV-FACELIFT-01	HIGH	E83改款后五门SUV外廓。	READY
10586	10586	Wagon	Passat B7 Variant	365	5	EU-VW-PASSAT-B7-WAGON-01	HIGH	B7五门旅行车外廓。	READY
10602_prefl	10602	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门MPV外廓。	READY
10602_facelift	10602	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门MPV外廓。	READY
10604_prefl	10604	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门MPV外廓。	READY
10604_facelift	10604	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门MPV外廓。	READY
10618_prefl	10618	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门旅行车外廓。	READY
10618_facelift	10618	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门旅行车外廓。	READY
10620_prefl	10620	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门旅行车外廓。	READY
10620_facelift	10620	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门旅行车外廓。	READY
10622_prefl	10622	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门旅行车外廓。	READY
10622_facelift	10622	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门旅行车外廓。	READY
10623_prefl	10623	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	生产区间覆盖改款，拆分改款前五门旅行车外廓。	READY
10623_facelift	10623	Wagon	i40 CW	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款，拆分改款后五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X3-E83-SUV-FACELIFT-01	4569	1853	1674	BMW Group PressClub	https://www.press.bmwgroup.com/deutschland/article/detail/T0002679DE/der-neue-bmw-x3
EU-BMW-X3-F25-SUV-FACELIFT-01	4657	1881	1661	BMW Group PressClub; Automobile-Catalog	https://www.press.bmwgroup.com/global/article/detail/T0165242EN/specifications-of-the-new-bmw-x3-04/2014?language=en; https://www.automobile-catalog.com/car/2015/2026085/bmw_x3_xdrive20d.html
EU-VW-PASSAT-B7-SEDAN-01	4769	1820	1470	Auto-Data; Volkswagen Newsroom	https://www.auto-data.net/en/volkswagen-passat-b7-1.4-tsi-bmt-160hp-44143; https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-VW-PASSAT-B7-WAGON-01	4771	1820	1516	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b7-1.4-tsi-bmt-160hp-44155
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/2011/1606775/hyundai_ix20_1_6_crdi_style.html; https://www.auto-data.net/en/hyundai-ix20-1.6-crdi-116hp-blue-drive-37038
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/2016/2228465/hyundai_ix20_blue_1_6_crdi_128.html; https://www.auto-data.net/en/hyundai-ix20-facelift-2015-1.6d-128hp-23624
EU-HYUNDAI-I40-VF-WAGON-PREFL-01	4770	1815	1470	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/2011/1607840/hyundai_i40_tourer_blue_1_6_gdi_active.html; https://www.auto-data.net/en/hyundai-i40-combi-1.7-crdi-136hp-automatic-18577
EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	4775	1815	1470	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/2015/2161085/hyundai_i40_wagon_2_0_gdi_automatic.html; https://www.auto-data.net/en/hyundai-i40-combi-facelift-2015-1.7-crdi-141hp-22496
```

## 下一步优先处理

1. 闭合 Cadillac CTS Wagon/Coupe、SRX II、Escalade III 与 Mitsubishi Pajero IV 乘用车/SUV 簇。
2. 批量处理 Skoda Superb II、Renault Scénic III/Grand Scénic III、Seat Alhambra 与 Hyundai i30 Wagon。
3. 乘用车簇完成后，集中处理 Movano、Jumpy、H100、Hilux/Taro、Nissan Pick-up 和 L300 的轴距、车顶、驾驶室及货斗分支。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/deutschland/article/detail/T0002679DE/der-neue-bmw-x3 "Der neue BMW X3"
[2]: https://www.auto-data.net/en/volkswagen-passat-b7-1.4-tsi-bmt-160hp-44143 "Volkswagen Passat (B7) 1.4 TSI BMT (160 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/2011/1606775/hyundai_ix20_1_6_crdi_style.html?utm_source=chatgpt.com "2011 Hyundai ix20 1.6 CRDi Style Specs Review (85 kW / 116 PS / 114 hp) (since early-year 2011 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_9101-9200_ktype_dimension_mapping_final.tsv
- all_9101-9200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

