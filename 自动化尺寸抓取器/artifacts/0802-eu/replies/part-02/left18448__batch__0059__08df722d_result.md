# 任务：left18448 第 5801-5900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0059__08df722d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5801-5900 行

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
left18448 第 5801-5900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Mondeo iii turnier	2.0 16V DI / Tddi / Tdci	Kombi	Frontantrieb	Diesel	Oct 2000	Mar 2007	15491
Ford	Mondeo iii turnier	2.0 16V Tddi / Tdci	Kombi	Frontantrieb	Diesel	Oct 2000	Mar 2007	15493
Ford	Mondeo iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	Oct 2001	Mar 2007	16454
Ford	Mondeo iii turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	Sep 2004	Mar 2007	10338
Ford	Mondeo iii turnier	2.2 Tdci	Kombi	Frontantrieb	Diesel	Sep 2004	Mar 2007	18271
Ford	Mondeo iii turnier	2.5 V6 24V	Kombi	Frontantrieb	Benzin	Oct 2000	Mar 2007	15489
Ford	Mondeo iii turnier	3.0 V6 24V	Kombi	Frontantrieb	Benzin	Sep 2004	Mar 2007	18274
Ford	Mondeo iii turnier	St220	Kombi	Frontantrieb	Benzin	Apr 2002	Mar 2007	16634
Ford	Mondeo iv	1.6 Ecoboost	Stufenheck	Frontantrieb	Benzin	Nov 2010	Jan 2015	120851
Ford	Mondeo iv	1.6 Tdci	Stufenheck	Frontantrieb	Diesel	Dec 2010	Jan 2015	100896
Ford	Mondeo iv	1.6 TI	Stufenheck	Frontantrieb	Benzin	Mar 2007	Jan 2015	10343
Ford	Mondeo iv	1.6 TI	Stufenheck	Frontantrieb	Benzin	Mar 2010	Jan 2015	128496
Ford	Mondeo iv	2.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jul 2009	Jan 2015	5136
Ford	Mondeo iv	2.0 Scti	Stufenheck	Frontantrieb	Benzin	Mar 2010	Jan 2015	128494
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	Mar 2007	Dec 2014	5137
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	Mar 2010	Jan 2015	54925
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	Aug 2008	Dec 2014	126877
Ford	Mondeo iv	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	Oct 2010	Jan 2015	126874
Ford	Mondeo iv turnier	2.0 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Jul 2009	Jan 2015	5086
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	Mar 2007	Dec 2014	5060
Ford	Mondeo v	2.5	Stufenheck	Frontantrieb	Benzin	May 2015	Mar 2022	114355
Ford	Mondeo v	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Feb 2015	Mar 2022	111088
Ford	Mondeo v	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	Feb 2015	Mar 2022	124773
Ford	Mondeo v	1.5 Ecoboost	Schrägheck	Frontantrieb	Benzin	Sep 2014	Mar 2022	107749
Ford	Mondeo v	1.5 Ecoboost	Stufenheck	Frontantrieb	Benzin	Sep 2014	Mar 2022	124779
Ford	Mondeo v	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	Mar 2015	Mar 2022	111093
Ford	Mondeo v	1.5 Tdci	Stufenheck	Frontantrieb	Diesel	Mar 2015	Mar 2022	124783
Ford	Mondeo v	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	Sep 2014	Mar 2022	107752
Ford	Mondeo v	2.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Sep 2014	Mar 2022	107750
Ford	Mondeo v	2.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Sep 2014	Mar 2022	107751
Ford	Mondeo v	2.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	May 2015	Mar 2022	110544
Ford	Mondeo v	2.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	May 2015	Mar 2022	114340
Ford	Mondeo v	2.0 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2014	Mar 2022	107748
Ford	Mondeo v	2.0 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2014	Mar 2022	108597
Ford	Mondeo v	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	Sep 2014	Mar 2022	107753
Ford	Mondeo v	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	Sep 2014	Mar 2022	107754
Ford	Mondeo v	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	May 2015	Mar 2022	110549
Ford	Mondeo v	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	Sep 2014	Mar 2022	124784
Ford	Mondeo v	2.0 Tdci 4X4	Schrägheck	Allrad	Diesel	Feb 2015	Mar 2022	111097
Ford	Mondeo v	2.0 Tdci 4X4	Schrägheck	Allrad	Diesel	Feb 2015	Mar 2022	111098
Ford	Mondeo v	2.0 Tdci 4X4	Stufenheck	Allrad	Diesel	May 2015	Mar 2022	115100
Ford	Mondeo v	2.0 Tdci 4X4	Stufenheck	Allrad	Diesel	Sep 2014	Mar 2022	124786
Ford	Mondeo v	2.0 Tdci Bi-turbo	Schrägheck	Frontantrieb	Diesel	Mar 2015	Mar 2022	111096
Ford	Mondeo v	2.0 Tdci Bi-turbo	Stufenheck	Frontantrieb	Diesel	May 2015	Mar 2022	115101
Ford	Mondeo v turnier	1.0 Ecoboost	Kombi	Frontantrieb	Benzin	Feb 2015	Mar 2022	111103
Ford	Mondeo v turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	Sep 2014	Mar 2022	107755
Ford	Mondeo v turnier	1.5 Tdci	Kombi	Frontantrieb	Diesel	Mar 2015	Mar 2022	111105
Ford	Mondeo v turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	Sep 2014	Mar 2022	107760
Ford	Mondeo v turnier	2.0 Ecoboost	Kombi	Frontantrieb	Benzin	Sep 2014	Mar 2022	107756
Ford	Mondeo v turnier	2.0 Ecoboost	Kombi	Frontantrieb	Benzin	Sep 2014	Mar 2022	107758
Ford	Mondeo v turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	Sep 2014	Mar 2022	107761
Ford	Mondeo v turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	Sep 2014	Mar 2022	107762
Ford	Mondeo v turnier	2.0 Tdci 4X4	Kombi	Allrad	Diesel	Feb 2015	Mar 2022	111110
Ford	Mondeo v turnier	2.0 Tdci 4X4	Kombi	Allrad	Diesel	Feb 2015	Mar 2022	111111
Ford	Mondeo v turnier	2.0 Tdci Bi-turbo	Kombi	Frontantrieb	Diesel	Mar 2015	Mar 2022	111107
Ford	Orion ii	1.6 I	Stufenheck	Frontantrieb	Benzin	Feb 1986	Jul 1990	11166
Ford	Orion iii	1.4	Stufenheck	Frontantrieb	Benzin	Jul 1990	Dec 1993	15289
Ford	Orion iii	1.6	Stufenheck	Frontantrieb	Benzin	Jul 1990	Dec 1992	15290
Ford	Puma	1.0 Ecoboost Mhev	SUV	Frontantrieb	Benzin/Elektro	Mar 2023	-	154593
Ford	Puma	1.0 Flexifuel	SUV	Frontantrieb	Benzin/Ethanol	Dec 2021	-	146629
Ford	Puma	1.0 ST Ecoboost Mhev	SUV	Frontantrieb	Benzin/Elektro	Mar 2023	-	154601
Ford	Puma	1.6 16V	Coupe	Frontantrieb	Benzin	Aug 2000	Jun 2002	16032
Ford	Puma	1.7 16V	Coupe	Frontantrieb	Benzin	Mar 1997	Jun 2002	7813
Ford	Puma	Gen-e	SUV	Frontantrieb	Elektro	Jan 2025	-	801248
Ford	Puma	Racing ST 160	Coupe	Frontantrieb	Benzin	Jun 1999	Jun 2002	11764
Ford	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	Dec 2022	-	155043
Ford	Ranger	2.2 Tdci	Pick-up	Heckantrieb	Diesel	Apr 2011	-	12573
Ford	Ranger	2.2 Tdci	Pick-up	Heckantrieb	Diesel	Apr 2011	-	55033
Ford	Ranger	2.2 Tdci	Pick-up	Heckantrieb	Diesel	Nov 2011	-	57328
Ford	Ranger	2.2 Tdci	Pick-up	Heckantrieb	Diesel	May 2015	-	116217
Ford	Ranger	2.2 Tdci	Pick-up	Heckantrieb	Diesel	May 2015	-	116220
Ford	Ranger	2.2 Tdci 4X4	Pick-up	Allrad	Diesel	Apr 2011	-	12574
Ford	Ranger	2.2 Tdci 4X4	Pick-up	Allrad	Diesel	Apr 2011	-	12605
Ford	Ranger	2.2 Tdci 4X4	Pick-up	Allrad	Diesel	May 2015	-	116219
Ford	Ranger	2.2 Tdci 4X4	Pick-up	Allrad	Diesel	May 2015	-	116221
Ford	Ranger	2.5 D	Pick-up	Heckantrieb	Diesel	Oct 1999	Apr 2002	14164
Ford	Ranger	2.5 D 4X4	Pick-up	Allrad	Diesel	Oct 1999	Apr 2002	14601
Ford	Ranger	2.5 TD	Pick-up	Heckantrieb	Diesel	Apr 2002	Jun 2006	16871
Ford	Ranger	2.5 TD 4X4	Pick-up	Allrad	Diesel	Oct 1999	Jun 2006	14163
Ford	Ranger	2.5 TD 4X4	Pick-up	Allrad	Diesel	Apr 2002	Jun 2006	16872
Ford	Ranger	3.2 Tdci 4X4	Pick-up	Allrad	Diesel	Apr 2011	-	12606
Ford	Scorpio i	2.5 D	Stufenheck	Heckantrieb	Diesel	Dec 1989	Dec 1994	16737
Ford	Scorpio ii	2.3 I 16V	Stufenheck	Heckantrieb	Benzin	Jun 1996	Aug 1998	5744
Ford	Scorpio ii	2.5 TD	Stufenheck	Heckantrieb	Diesel	Sep 1996	Aug 1998	7810
Ford	Scorpio ii turnier	2.3 I 16V	Kombi	Heckantrieb	Benzin	Jun 1996	Aug 1998	5747
Ford	Scorpio ii turnier	2.5 TD	Kombi	Heckantrieb	Diesel	Sep 1996	Aug 1998	7811
Ford	Sierra	1.3	Schrägheck	Heckantrieb	Benzin	Aug 1982	Dec 1986	11562
Ford	Sierra	1.6	Schrägheck	Heckantrieb	Benzin	Jan 1987	Feb 1993	121807
Ford	Sierra	2.0 16V Cosworth 4X4	Schrägheck	Allrad	Benzin	Jan 1990	Feb 1993	8736
Ford	Sierra	2.0 4X4	Stufenheck	Allrad	Benzin	Jan 1990	Feb 1993	15021
Ford	Sierra	2.0 4X4	Kombi	Allrad	Benzin	May 1989	Feb 1993	15028
Ford	Sierra	2.0 I	Stufenheck	Heckantrieb	Benzin	Jan 1987	Dec 1989	8733
Ford	Sierra	2.0 I	Schrägheck	Heckantrieb	Benzin	Jan 1987	Feb 1993	8734
Ford	Sierra	2.0 I	Kombi	Heckantrieb	Benzin	Jan 1987	Feb 1993	8735
Ford	Sierra	2.0 I	Stufenheck	Heckantrieb	Benzin	Jan 1990	Feb 1993	15025
Ford	Sierra	2.0 I	Kombi	Heckantrieb	Benzin	May 1989	Feb 1993	15027
Ford	Sierra	2.8 I 4X4	Kombi	Allrad	Benzin	Aug 1982	Dec 1986	16900
Ford	Sierra	2.8 I 4X4	Kombi	Allrad	Benzin	Aug 1982	Dec 1986	16901
Ford	Sierra	2.8 I XR 4X4	Schrägheck	Allrad	Benzin	Sep 1983	Dec 1986	16897
Ford	Sierra	2.8 Xr4i	Schrägheck	Heckantrieb	Benzin	Aug 1982	Dec 1986	15589


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Mondeo III、Mondeo IV、Mondeo V 和 Puma 系列的首轮聚类映射。
* Mondeo III 跨越 2003 年改款的 Ktype 已拆分为 `prefl` 与 `facelift`；两阶段虽然三维相同，但物理外观阶段不同，因此分别建组。2001 年规格与 Ford 2005 官方表均确认旅行车为 `4804 × 1812 × 1441 mm`，宽度为不含后视镜口径。([汽车目录][1])
* Mondeo IV 的 6 个既有改款前后尺寸组直接复用，没有重复输出尺寸组。
* Mondeo V 跨越 2019 改款的 Ktype 全部拆成改款前、改款后派生行。Ford 官方资料确认五门/四门为 `4871 × 1852 × 1482 mm`，旅行车为 `4867 × 1852 × 1501 mm`；改款后继续单独建组，不因三维相同而合并物理外观阶段。
* Puma II 已按普通外观、ST-Line、ST 分组；官方规格表显示三者长度和高度不同。Puma Gen-E 已按独立纯电外廓建组。
* 第一代 Puma 普通 Coupe 与 Racing Puma 宽体分别建组；Racing Puma 的宽体尺寸未与普通车身混用。([汽车数据][2])
* Ktype `146629` 的 Flexifuel 版本仍缺少适用普通外观或 ST-Line 外观的可靠边界，暂不猜测关联尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 READY 输入 Ktype：61
* READY 映射行：111
* 尚未闭合输入 Ktype：39

  * 已明确输出 PENDING 行：1
  * 尚待处理 Orion、Ranger、Scorpio、Sierra：38
* 已确认并引用尺寸组：20

  * 本轮首次创建或纠正：12
  * 直接复用既有缓存：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15491_prefl	15491	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15491_facelift	15491	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
15493_prefl	15493	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15493_facelift	15493	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
16454_prefl	16454	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
16454_facelift	16454	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
10338	10338	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
18271	18271	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
15489_prefl	15489	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15489_facelift	15489	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
18274	18274	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
16634_prefl	16634	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
16634_facelift	16634	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
120851	120851	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
100896	100896	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
10343_prefl	10343	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
10343_facelift	10343	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
128496_prefl	128496	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
128496_facelift	128496	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5136_prefl	5136	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
5136_facelift	5136	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
128494_prefl	128494	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
128494_facelift	128494	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5137_prefl	5137	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
5137_facelift	5137	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
54925_prefl	54925	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
54925_facelift	54925	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
126877_prefl	126877	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
126877_facelift	126877	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
126874	126874	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5086_prefl	5086	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
5086_facelift	5086	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
5060_prefl	5060	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
5060_facelift	5060	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
114355_prefl	114355	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
114355_facelift	114355	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111088_prefl	111088	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111088_facelift	111088	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124773_prefl	124773	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124773_facelift	124773	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107749_prefl	107749	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107749_facelift	107749	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124779_prefl	124779	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124779_facelift	124779	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111093_prefl	111093	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111093_facelift	111093	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124783_prefl	124783	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124783_facelift	124783	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107752_prefl	107752	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107752_facelift	107752	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107750_prefl	107750	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107750_facelift	107750	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107751_prefl	107751	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107751_facelift	107751	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
110544_prefl	110544	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
110544_facelift	110544	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
114340_prefl	114340	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
114340_facelift	114340	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107748_prefl	107748	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
107748_facelift	107748	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
108597_prefl	108597	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
108597_facelift	108597	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107753_prefl	107753	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107753_facelift	107753	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107754_prefl	107754	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107754_facelift	107754	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
110549_prefl	110549	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
110549_facelift	110549	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
124784_prefl	124784	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124784_facelift	124784	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111097_prefl	111097	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111097_facelift	111097	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
111098_prefl	111098	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111098_facelift	111098	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
115100_prefl	115100	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
115100_facelift	115100	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
124786_prefl	124786	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124786_facelift	124786	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111096_prefl	111096	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111096_facelift	111096	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
115101_prefl	115101	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
115101_facelift	115101	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111103_prefl	111103	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111103_facelift	111103	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107755_prefl	107755	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107755_facelift	107755	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111105_prefl	111105	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111105_facelift	111105	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107760_prefl	107760	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107760_facelift	107760	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107756_prefl	107756	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107756_facelift	107756	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107758_prefl	107758	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107758_facelift	107758	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107761_prefl	107761	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107761_facelift	107761	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107762_prefl	107762	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107762_facelift	107762	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111110_prefl	111110	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111110_facelift	111110	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111111_prefl	111111	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111111_facelift	111111	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111107_prefl	111107	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111107_facelift	111107	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
154593_base	154593	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH	普通外观分支。	READY
154593_stline	154593	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	HIGH	ST-Line外观分支。	READY
146629	146629	SUV	Puma II		5		LOW	候选为普通或ST-Line外观，需确认Flexifuel适用系列。	PENDING: Flexifuel适用外观系列未确认
154601	154601	SUV	Puma II ST		5	EU-FORD-PUMA-II-SUV-ST-01	HIGH	ST专属外观分支。	READY
16032	16032	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-COUPE-01	HIGH	标准三门Coupe外廓。	READY
7813	7813	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-COUPE-01	HIGH	标准三门Coupe外廓。	READY
801248	801248	SUV	Puma Gen-E		5	EU-FORD-PUMA-GEN-E-SUV-01	HIGH	纯电五门SUV外廓。	READY
11764	11764	Coupe	Puma I Racing	ECT	3	EU-FORD-PUMA-I-RACING-COUPE-WIDEBODY-01	HIGH	Racing Puma原厂宽体外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-III-WAGON-PREFL-01	4804	1812	1441	Automobile-Catalog 2001 Ford Mondeo Estate	https://www.automobile-catalog.com/car/2001/975005/ford_mondeo_estate_2_0_di_zetec.html
EU-FORD-MONDEO-III-WAGON-FACELIFT-01	4804	1812	1441	Ford Mondeo 2005 official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf
EU-FORD-MONDEO-V-PREFL-SEDAN-01	4871	1852	1482	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	4871	1852	1482	Ford UK Mondeo official brochure; Ford UK Mondeo Vignale official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo_Vignale.pdf
EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	4871	1852	1482	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-PREFL-WAGON-01	4867	1852	1501	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-FACELIFT-WAGON-01	4867	1852	1501	Ford UK Mondeo official brochure; Ford UK Mondeo Vignale official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo_Vignale.pdf
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537	Ford UK Puma official specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Puma_new.pdf
EU-FORD-PUMA-II-SUV-ST-01	4226	1805	1533	Ford UK Puma official specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Puma_new.pdf
EU-FORD-PUMA-I-COUPE-01	3984	1674	1345	Auto-Data Ford Puma Coupe (ECT)	https://www.auto-data.net/en/ford-puma-coupe-ect-generation-1760
EU-FORD-PUMA-GEN-E-SUV-01	4214	1805	1555	Ford Europe Puma Gen-E official factsheet	https://www.fordpers.be/content/documents/news/2024/ford_2024_puma_gen_e_factsheet_eu.pdf
EU-FORD-PUMA-I-RACING-COUPE-WIDEBODY-01	3984	1770	1315	Carfolio Ford Racing Puma	https://www.carfolio.com/ford-racing-puma-87571
```

## 下一步优先处理

1. 按驾驶室和轴距聚类处理 Ranger，先确认 1999–2006 与 2011–现款各代的 Single、Super、Double Cab 分支，禁止把多个 CAB/轴距压入一个尺寸组。
2. 批量闭合 Orion II、Orion III、Scorpio I/II Sedan 与 Wagon。
3. 按前期、改款期、Sedan、Hatchback、Wagon 和 XR4i/Cosworth 特殊外廓拆分 Sierra。
4. 单独确认 Puma Flexifuel Ktype `146629` 覆盖的普通或 ST-Line 外观系列。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/975005/ford_mondeo_estate_2_0_di_zetec.html?utm_source=chatgpt.com "2001 Ford Mondeo Estate 2.0 Di Zetec (man. 5)"
[2]: https://www.auto-data.net/en/ford-puma-coupe-ect-1.4-16v-90hp-8008?utm_source=chatgpt.com "Specs of Ford Puma Coupe (ECT) 1.4 16V (90 Hp) /1997, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Ktype `146629` 已由单行 PENDING 拆为普通外观和 ST-Line 外观两条 READY 映射，直接复用既有 Puma II 尺寸组，不重复输出尺寸。Ford 官方车型资料确认 Flexifuel 动力覆盖 Titanium 与 ST-Line 系列。([福特法国][1])
* Scorpio II 的 Sedan 与 Wagon 物理边界和不含后视镜三维已闭合，共解决 4 个 Ktype。Ford 官方资料明确列出 Sedan 为 `4825 × 1760 × 1388 mm`、Wagon 为 `4826 × 1760 × 1442 mm`。([汽车档案馆][2])
* Scorpio I、Orion、Ranger、Sierra 尚未闭合，本轮未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 READY 输入 Ktype：66
* READY 映射行：116
* 未闭合输入 Ktype：34
* 已确认并引用尺寸组：22
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146629_base	146629	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH	普通外观分支。	READY
146629_stline	146629	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	HIGH	ST-Line外观分支。	READY
5744	5744	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH	四门轿车外廓。	READY
7810	7810	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH	四门轿车外廓。	READY
5747	5747	Wagon	Scorpio II		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH	五门旅行车外廓。	READY
7811	7811	Wagon	Scorpio II		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH	五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1388	Ford Scorpio 1997 official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Scorpio-1997-UK.pdf
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442	Ford Scorpio 1997 official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Scorpio-1997-UK.pdf
```

## 下一步优先处理

1. 闭合 Scorpio I Sedan 的不含后视镜宽度，避免误用官方 brochure 中的含镜宽度。
2. 批量处理 Orion II、Orion III。
3. 按代际及驾驶室/轴距分支处理 Ranger。
4. 最后集中闭合 Sierra 的 Hatchback、Sedan、Wagon 与特殊外观分支。

推进信号：CONTINUE

[1]: https://www.ford.fr/content/dam/guxeu/fr/documents/feature-pdfs/FT-Puma.pdf?utm_source=chatgpt.com "FORD PUMA"
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Scorpio-1997-UK.pdf?utm_source=chatgpt.com "Ford-Scorpio-1997-UK.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Orion II、Orion III、Scorpio I，以及 Sierra I 的标准掀背、四驱旅行车、XR 4x4、XR4i 和 Sierra RS Cosworth 外廓。
* Sierra Ktype `8733` 已命中改款前四门 Sedan 尺寸组。
* Sierra II 其余 7 个 Ktype 暂不强制建组：同级资料对改款后三门掀背、四门 Sedan 和旅行车存在实质尺寸差异。例如，1990–1993 三门版资料为 `4420 × 1689 × 1410 mm`，而改款前 2.0i S 为 `4425 × 1694 × 1407 mm`；Sedan 资料也出现 `4470 × 1699 × 1410 mm` 与 `4467 × 1698 mm` 的差异。冲突未闭合前保持 PENDING。([autoevolution][1])
* Ranger 的 16 个 Ktype 本轮未逐发动机重复处理，继续等待按代际、CAB 和轴距成组闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：77
* PENDING 输入 Ktype：23

  * Ranger：16
  * Sierra II：7
* READY 映射行：129
* 已确认尺寸组：33
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11166	11166	Sedan	Orion II	AFF	4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
15289	15289	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-SEDAN-01	HIGH	四门轿车外廓。	READY
15290	15290	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-SEDAN-01	HIGH	四门轿车外廓。	READY
16737	16737	Sedan	Scorpio I	GGE	4	EU-FORD-SCORPIO-I-SEDAN-01	HIGH	四门轿车外廓。	READY
11562_3dr	11562	Hatchback	Sierra I		3	EU-FORD-SIERRA-I-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
11562_5dr	11562	Hatchback	Sierra I		5	EU-FORD-SIERRA-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
121807	121807	Hatchback	Sierra II					LOW	跨越改款且覆盖三门、五门外廓，改款后分支尺寸尚有冲突。	PENDING: 改款后门数分支尺寸冲突
8736	8736	Sedan	Sierra RS Cosworth		4	EU-FORD-SIERRA-RS-COSWORTH-4X4-SEDAN-01	HIGH	输入车身标签与可靠车型资料不一致，按四门Cosworth轿车外廓映射。	READY
15021	15021	Sedan	Sierra II		4		LOW	四驱四门轿车候选跨越1990年外观边界。	PENDING: 1990年四驱轿车外廓边界未闭合
15028	15028	Wagon	Sierra II	BNG	5		LOW	跨越改款前后4x4旅行车外廓，改款前高度尚未闭合。	PENDING: 改款前4x4旅行车高度未闭合
8733	8733	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
8734	8734	Hatchback	Sierra II					LOW	跨越改款且覆盖三门、五门外廓，改款后分支尺寸尚有冲突。	PENDING: 改款后门数分支尺寸冲突
8735	8735	Wagon	Sierra II	BNG	5		LOW	跨越改款前后后驱旅行车外廓，高度口径尚未统一。	PENDING: 改款前后旅行车高度冲突
15025	15025	Sedan	Sierra II		4		LOW	生产期跨越1990年外观边界，前后阶段尺寸尚未统一。	PENDING: 改款前后轿车尺寸冲突
15027	15027	Wagon	Sierra II	BNG	5		LOW	生产期跨越改款前后旅行车外廓，高度口径尚未统一。	PENDING: 改款前后旅行车高度冲突
16900	16900	Wagon	Sierra I	BNC	5	EU-FORD-SIERRA-I-WAGON-4X4-01	HIGH	五门四驱旅行车外廓。	READY
16901	16901	Wagon	Sierra I	BNC	5	EU-FORD-SIERRA-I-WAGON-4X4-01	HIGH	五门四驱旅行车外廓。	READY
16897_3dr	16897	Hatchback	Sierra I XR 4x4		3	EU-FORD-SIERRA-I-XR4X4-HATCHBACK-3D-01	HIGH	XR 4x4三门掀背外廓。	READY
16897_5dr	16897	Hatchback	Sierra I XR 4x4		5	EU-FORD-SIERRA-I-XR4X4-HATCHBACK-5D-01	HIGH	XR 4x4五门掀背外廓。	READY
15589	15589	Hatchback	Sierra I XR4i		3	EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	HIGH	XR4i三门专属外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389	Automobile-Catalog 1988 Ford Orion 1.6i Ghia	https://www.automobile-catalog.com/car/1988/943340/ford_orion_1_6i_ghia.html
EU-FORD-ORION-III-SEDAN-01	4229	1690	1395	Automobile-Catalog 1990 Ford Orion 1.4i CLX; Automobile-Catalog 1990 Ford Orion 1.6i CLX	https://www.automobile-catalog.com/car/1990/945200/ford_orion_1_4i_clx.html; https://www.automobile-catalog.com/car/1990/945470/ford_orion_1_6i_clx.html
EU-FORD-SCORPIO-I-SEDAN-01	4740	1760	1440	Autoevolution Ford Scorpio Sedan 1990	https://www.autoevolution.com/cars/ford-scorpio-sedan-1990.html
EU-FORD-SIERRA-I-HATCHBACK-3D-01	4394	1703	1408	Automobile-Catalog 1986 Ford Sierra 1.3 L	https://www.automobile-catalog.com/car/1986/929390/ford_sierra_1_3_l.html
EU-FORD-SIERRA-I-HATCHBACK-5D-01	4394	1703	1408	Automobile-Catalog 1986 Ford Sierra 1.3 L	https://www.automobile-catalog.com/car/1986/929390/ford_sierra_1_3_l.html
EU-FORD-SIERRA-RS-COSWORTH-4X4-SEDAN-01	4494	1698	1376	Automobile-Catalog 1990 Ford Sierra Cosworth 4x4	https://www.automobile-catalog.com/car/1990/936410/ford_sierra_cosworth_4x4.html
EU-FORD-SIERRA-II-SEDAN-PREFL-01	4467	1698	1407	Automobile-Catalog 1987 Ford Sierra Sapphire 2.0i Ghia automatic	https://www.automobile-catalog.com/car/1987/934565/ford_sierra_sapphire_2_0i_ghia_automatic.html
EU-FORD-SIERRA-I-WAGON-4X4-01	4522	1729	1438	Automobile-Catalog 1986 Ford Sierra Turnier 2.8i V6 Ghia 4x4	https://www.automobile-catalog.com/car/1986/932630/ford_sierra_turnier_2_8i_v6_ghia_4x4.html
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-3D-01	4459	1725	1378	Automobile-Catalog 1985 Ford Sierra XR 4x4	https://www.automobile-catalog.com/car/1985/52220/ford_sierra_xr_4x4.html
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-5D-01	4459	1725	1378	Automobile-Catalog 1985 Ford Sierra XR 4x4	https://www.automobile-catalog.com/car/1985/52220/ford_sierra_xr_4x4.html
EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	4459	1728	1392	Automobile-Catalog 1984 Ford Sierra XR4i	https://www.automobile-catalog.com/car/1984/30050/ford_sierra_xr4i.html
```

## 下一步优先处理

1. 按 Ranger 1999–2006、2011–2022、2022–现款三个代际，集中闭合 Single Cab、Super Cab、Double Cab 的轴距与外廓，随后批量关联全部16个 Ktype。
2. 在尺寸组层一次性解决 Sierra II 的三门/五门、Sedan、后驱 Wagon 与四驱 Wagon 来源冲突；不再逐 Ktype 重复抓取。

推进信号：CONTINUE

[1]: https://www.autoevolution.com/cars/ford-sierra-3-doors-1990.html "https://www.autoevolution.com/cars/ford-sierra-3-doors-1990.html"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Sierra II 四门 Sedan 的 1990 年中期外廓变化。Ktype `15021`、`15025` 分别拆为更新前后两条映射；更新前复用既有尺寸组，更新后新建 `4501 × 1698 × 1407 mm` 尺寸组，宽度明确不含后视镜。([汽车目录][1])
* 已闭合 Ranger Ktype `16871`。该 Ktype 对应 84 PS、4x2 动力，官方资料确认同时覆盖 Regular Cab 与 Super Cab，因此拆成两个物理分支；官方尺寸表明确标注宽度不含外后视镜。([JMS Fahrzeugteile][2])
* Sierra Hatchback、Sierra Wagon 及其余 Ranger 未强行套用候选尺寸，继续保持待处理。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：80
* PENDING 输入 Ktype：20

  * Ranger：15
  * Sierra II Hatchback：2
  * Sierra II Wagon：3
* READY 映射行：135
* 已确认尺寸组：36
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15021_prefl	15021	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	1990年中期外观更新前四门轿车外廓。	READY
15021_facelift	15021	Sedan	Sierra II facelift		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	HIGH	1990年中期外观更新后四门轿车外廓。	READY
16871_regcab	16871	Pickup	Ranger ER/EQ/R_		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-01	HIGH	两门Regular Cab 4x2外廓。	READY
16871_supercab	16871	Pickup	Ranger ER/EQ/R_		2	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-01	HIGH	两门Super Cab 4x2外廓。	READY
15025_prefl	15025	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	1990年中期外观更新前四门轿车外廓。	READY
15025_facelift	15025	Sedan	Sierra II facelift		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	HIGH	1990年中期外观更新后四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	4501	1698	1407	Automobile-Catalog 1991 Ford Sierra Sapphire 2.0i DOHC Ghia	https://www.automobile-catalog.com/car/1991/935510/ford_sierra_sapphire_2_0i_dohc_ghia.html
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-01	5012	1695	1615	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-01	5012	1695	1615	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
```

## 下一步优先处理

1. 在 Sierra Wagon 尺寸组层区分标准外廓与加长保险杠、车顶附件造成的 `4511 × 1720 × 1428` 和 `4544 × 1720 × 1488` 两类配置，再统一处理 3 个 Wagon Ktype。
2. 闭合 Sierra Hatchback 三门与五门、1990 年更新前后的物理边界。
3. 按 Ranger 1999–2002、2002–2006、2011–2015、2015–2022 和 2022 年后代际，批量处理剩余 Regular Cab、Super Cab、Double Cab 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/934430/ford_sierra_4-dr_2_0i_ghia_cat.html?utm_source=chatgpt.com "1990 Ford Sierra (4-dr) 2.0i Ghia catalyst Specs Review (74 kW / 101 PS / 99 hp) (up to mid-year 1990 for Europe )"
[2]: https://www.jms-fahrzeugteile.de/Bremsentechnik/EBC-Bremscheiben-Belaege/EBC-Standardbremsscheiben-fuer/Ford/Ranger/VA-vorne-front/EBC-Premium-Disc-Bremsscheibe-passend-fuer-Ford-Ranger%3A%3A1180166.html?utm_source=chatgpt.com "EBC Premium Disc Bremsscheibe passend für Ford Ranger"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Sierra II 的两个掀背 Ktype 已按三门、五门及 1990 年更新前后拆分，8 条派生映射全部闭合。更新前尺寸为 `4425 × 1694 × 1407 mm`，更新后尺寸为 `4420 × 1689 × 1410 mm`；宽度均为不含后视镜口径。([汽车目录][1])
* 已一次性闭合 Ranger 1999–2006 阶段剩余的 4 个 Ktype。1999 版按 Regular Cab、Super Cab、Double Cab 与驱动形式拆分；2002 年后进一步区分标准车身和 XLT 加宽轮眉外廓。Ford 1999、2005 官方资料均提供对应驾驶室的完整三维和不含后视镜宽度。([Dezo's Garage][2])
* Sierra Wagon 的 3 个 Ktype 尚未修改：欧洲大陆标准尺寸与英国规格存在 `4511 × 1720 × 1428`、`4544 × 1720 × 1488` 两套外廓，需在尺寸组层确认适用边界后再映射。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：86
* PENDING 输入 Ktype：14

  * Ranger 2011 年后：11
  * Sierra II Wagon：3
* READY 映射行：157
* 已确认并引用尺寸组：49
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121807_3dr_prefl	121807	Hatchback	Sierra II		3	EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	HIGH	1990年更新前三门掀背外廓。	READY
121807_5dr_prefl	121807	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	HIGH	1990年更新前五门掀背外廓。	READY
121807_3dr_facelift	121807	Hatchback	Sierra II facelift		3	EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	HIGH	1990年更新后三门掀背外廓。	READY
121807_5dr_facelift	121807	Hatchback	Sierra II facelift		5	EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	HIGH	1990年更新后五门掀背外廓。	READY
8734_3dr_prefl	8734	Hatchback	Sierra II		3	EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	HIGH	1990年更新前三门掀背外廓。	READY
8734_5dr_prefl	8734	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	HIGH	1990年更新前五门掀背外廓。	READY
8734_3dr_facelift	8734	Hatchback	Sierra II facelift		3	EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	HIGH	1990年更新后三门掀背外廓。	READY
8734_5dr_facelift	8734	Hatchback	Sierra II facelift		5	EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	HIGH	1990年更新后五门掀背外廓。	READY
14164_regcab_prefl	14164	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-PREFL-01	HIGH	改款前Regular Cab后驱外廓。	READY
14164_supercab_prefl	14164	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-PREFL-01	HIGH	改款前Super Cab后驱外廓。	READY
14601_regcab_prefl	14601	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-PREFL-01	HIGH	改款前Regular Cab四驱外廓。	READY
14163_doublecab_prefl	14163	Pickup	Ranger ER/EQ		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	改款前Double Cab四驱外廓。	READY
14163_regcab_facelift	14163	Pickup	Ranger ER/EQ facelift		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	HIGH	改款后Regular Cab四驱外廓。	READY
14163_supercab_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	HIGH	改款后标准Super Cab四驱外廓。	READY
14163_supercab_xlt_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Super Cab外廓。	READY
14163_doublecab_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	HIGH	改款后标准Double Cab四驱外廓。	READY
14163_doublecab_xlt_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Double Cab外廓。	READY
16872_regcab_facelift	16872	Pickup	Ranger ER/EQ facelift		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	HIGH	改款后Regular Cab四驱外廓。	READY
16872_supercab_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	HIGH	改款后标准Super Cab四驱外廓。	READY
16872_supercab_xlt_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Super Cab外廓。	READY
16872_doublecab_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	HIGH	改款后标准Double Cab四驱外廓。	READY
16872_doublecab_xlt_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Double Cab外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	4425	1694	1407	Automobile-Catalog 1987 Ford Sierra 2.0 CL	https://www.automobile-catalog.com/car/1987/932900/ford_sierra_2_0_cl.html
EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	4425	1694	1407	Automobile-Catalog 1987 Ford Sierra 2.0 CL	https://www.automobile-catalog.com/car/1987/932900/ford_sierra_2_0_cl.html
EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	4420	1689	1410	Autoevolution Ford Sierra 3 Doors 1990	https://www.autoevolution.com/cars/ford-sierra-3-doors-1990.html
EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	4420	1689	1410	Autoevolution Ford Sierra 5 Doors 1990	https://www.autoevolution.com/cars/ford-sierra-5-doors-1990.html
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-PREFL-01	4998	1695	1615	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-PREFL-01	4998	1695	1615	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-PREFL-01	4998	1750	1740	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-PREFL-01	4998	1750	1750	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	5022	1740	1740	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	5022	1740	1740	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	5022	1810	1750	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	5022	1740	1750	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	5022	1810	1760	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
```

## 下一步优先处理

1. 按 120、125、150、131、160 和 200 PS 的动力供应范围，将 Ranger TKE 的 11 个 Ktype 批量关联到 Regular Cab、Super Cab、Double Cab 现有或新建尺寸组。
2. 在尺寸组层确定 Sierra II Wagon 的大陆版与英国版外廓边界，随后一次性关闭剩余 3 个 Wagon Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/932900/ford_sierra_2_0_cl.html?utm_source=chatgpt.com "1987 Ford Sierra 2.0 CL Specs Review (77 kW ..."
[2]: https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf?utm_source=chatgpt.com "RANGER"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 Sierra II 剩余 3 个 Wagon Ktype，按后驱/四驱及更新前后拆为 6 条 READY 映射。后驱旅行车分别为 `4511 × 1720 × 1428 mm` 与 `4544 × 1720 × 1488 mm`；四驱旅行车分别为 `4511 × 1720 × 1410 mm` 与 `4544 × 1720 × 1476 mm`。([汽车目录][1])
* 已闭合 Ranger TKE 的 Ktype `12573`、`57328`、`12606`，分别关联 Regular Cab 4x2、Super Cab 4x2 和 Double Cab 高配 4x4 尺寸组。尺寸及驾驶室供应范围来自同一份 Ford 官方规格资料。
* 剩余 8 个 Ranger Ktype 尚未强制映射，主要阻塞项为驾驶室覆盖范围、改款阶段及不同配置高度边界。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：92
* PENDING 输入 Ktype：8
* READY 映射行：166
* 已确认并引用尺寸组：56
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15028_prefl	15028	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	MEDIUM	更新前五门四驱旅行车外廓。	READY
15028_facelift	15028	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	HIGH	更新后五门四驱旅行车外廓。	READY
8735_prefl	8735	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-PREFL-01	HIGH	更新前五门后驱旅行车外廓。	READY
8735_facelift	8735	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	HIGH	更新后五门后驱旅行车外廓。	READY
15027_prefl	15027	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-PREFL-01	HIGH	更新前五门后驱旅行车外廓。	READY
15027_facelift	15027	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	HIGH	更新后五门后驱旅行车外廓。	READY
12573	12573	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	HIGH	Regular Cab后驱外廓。	READY
57328	57328	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-PREFL-01	HIGH	Super Cab后驱外廓。	READY
12606	12606	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	HIGH	Double Cab高配四驱外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	4511	1720	1410	Automobile-Catalog 1989 Ford Sierra Turnier 2.9i Ghia 4x4 catalyst	https://www.automobile-catalog.com/car/1989/934745/ford_sierra_turnier_2_9i_ghia_4x4_cat.html
EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	4544	1720	1476	Automobile-Catalog 1991 Ford Sierra Turnier 2.0i DOHC Ghia 4x4 catalyst	https://www.automobile-catalog.com/car/1991/936005/ford_sierra_turnier_2_0i_dohc_ghia_4x4_cat.html
EU-FORD-SIERRA-II-WAGON-PREFL-01	4511	1720	1428	Automobile-Catalog 1989 Ford Sierra Turnier 2.0i Ghia catalyst	https://www.automobile-catalog.com/car/1989/933320/ford_sierra_turnier_2_0i_ghia_cat.html
EU-FORD-SIERRA-II-WAGON-FACELIFT-01	4544	1720	1488	Automobile-Catalog 1991 Ford Sierra Turnier 2.0i CLX catalyst	https://www.automobile-catalog.com/car/1991/935270/ford_sierra_turnier_2_0i_clx_cat.html
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	5274	1850	1703	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-PREFL-01	5359	1850	1706	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	5359	1850	1848	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
```

## 下一步优先处理

1. 确认 Ktype `55033` 的 120 PS 后驱版本对应驾驶室。
2. 一次性闭合 Ktype `12574`、`12605` 的 Regular、Super、Double Cab 分支及标准高度边界。
3. 处理改款后的 `116217`、`116220`、`116219`、`116221`，最后确认新一代 Ktype `155043` 的驾驶室与标准外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/933320/ford_sierra_turnier_2_0i_ghia_cat.html?utm_source=chatgpt.com "1989 Ford Sierra Turnier 2.0i Ghia catalyst Specs Review (74 kW / 101 PS / 99 hp) (for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Ktype `55033`、`12574`、`12605`：分别完成 120 PS 后驱 Regular Cab、125 PS 四驱 Regular/Double Cab，以及 150 PS 四驱 Regular/Super/Double Cab 分支。相关驾驶室边界由 Ford 同代官方车型资料确认。([汽车档案馆][1])
* 已闭合改款后 Ktype `116219`，按 Regular Cab、Super Cab 标准/高配、Double Cab 标准/高配拆为 5 条映射。Ford 官方价格表确认 160 PS 版本覆盖三种驾驶室及多个配置等级。
* Ktype `116217`、`116220`、`116221` 仍需确认各自发动机与驱动组合在欧洲市场对应的驾驶室覆盖范围。
* Ktype `155043` 已确认 P703 170 PS 覆盖 Single Cab、Rap Cab 和 Double Cab，但 Rap Cab 的欧洲市场完整三维尚未闭合，因此继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* PENDING 输入 Ktype：4
* READY 映射行：179
* PENDING 映射行：4
* 已确认并引用尺寸组：65
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
55033	55033	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	MEDIUM	两门Regular Cab后驱外廓。	READY
12574_regcab	12574	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	HIGH	两门Regular Cab四驱外廓。	READY
12574_doublecab	12574	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	四门Double Cab标准四驱外廓。	READY
12605_regcab	12605	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	HIGH	两门Regular Cab四驱外廓。	READY
12605_supercab_std	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-PREFL-01	HIGH	Super Cab标准四驱外廓。	READY
12605_supercab_highspec	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-PREFL-01	HIGH	Super Cab高配四驱外廓。	READY
12605_doublecab_std	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	Double Cab标准四驱外廓。	READY
12605_doublecab_highspec	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	HIGH	Double Cab高配四驱外廓。	READY
116219_regcab	116219	Pickup	Ranger TKE facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-FACELIFT-01	HIGH	两门Regular Cab四驱外廓。	READY
116219_supercab_std	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-FACELIFT-01	HIGH	Super Cab标准四驱外廓。	READY
116219_supercab_highspec	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-FACELIFT-01	HIGH	Super Cab高配四驱外廓。	READY
116219_doublecab_std	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-FACELIFT-01	HIGH	Double Cab标准四驱外廓。	READY
116219_doublecab_highspec	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-FACELIFT-01	HIGH	Double Cab高配四驱外廓。	READY
116217	116217	Pickup	Ranger TKE facelift	TKE				LOW	候选为Regular、Super或Double Cab后驱外廓。	PENDING: 160PS后驱驾驶室覆盖范围未确认
116220	116220	Pickup	Ranger TKE facelift	TKE				LOW	候选为Regular、Super或Double Cab后驱外廓。	PENDING: 131PS后驱驾驶室覆盖范围未确认
116221	116221	Pickup	Ranger TKE facelift	TKE				LOW	候选为Regular、Super或Double Cab四驱外廓。	PENDING: 131PS四驱驾驶室覆盖范围未确认
155043	155043	Pickup	Ranger IV	P703				LOW	覆盖Single、Rap及Double Cab候选外廓。	PENDING: Rap Cab欧洲市场完整三维未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	5274	1850	1800	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-PREFL-01	5359	1850	1804	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-PREFL-01	5359	1850	1840	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	5359	1850	1815	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-FACELIFT-01	5277	1860	1800	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-FACELIFT-01	5362	1860	1804	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-FACELIFT-01	5362	1860	1840	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-FACELIFT-01	5362	1860	1815	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-FACELIFT-01	5362	1860	1848	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
```

## 下一步优先处理

1. 一次性确认 Ktype `116217`、`116220`、`116221` 的欧洲市场驾驶室供应范围，并关联本轮已经闭合的 TKE facelift 尺寸组。
2. 闭合 P703 Rap Cab 的欧洲市场长度、不含后视镜宽度和高度，再完成 Ktype `155043` 的全部驾驶室派生映射。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2018/06/Ford-Ranger-2013-UK.pdf?utm_source=chatgpt.com "FORD RANGER"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5801-5900_ktype_dimension_mapping_final.tsv
- left18448_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 最后 4 个 Ranger Ktype 已全部闭合：

  * `116217`：Super Cab 后驱。
  * `116220`：Regular Cab 后驱。
  * `116221`：Regular Cab、Super Cab、Double Cab 四驱。
  * `155043`：P703 Single Cab、Super Cab、Double Cab 四驱。
* Ford 资料确认 TKE 160 PS 后驱的 Super Cab 分支，以及 130/131 PS 对应的驾驶室供应边界；P703 官方欧洲资料确认 170 PS 四驱覆盖三种驾驶室。P703 的长度和高度采用欧洲规格，不含后视镜宽度由 Ford 官方规格表确认是 1918 mm。([Mustang Italia][1])
* 已完成轻量机械检查：固定表头正确，188 个 `id` 唯一，70 个 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，无孤立尺寸组，无 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：188
* PENDING：0
* DIMENSION_GROUP：70
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15491_prefl	15491	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15491_facelift	15491	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
15493_prefl	15493	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15493_facelift	15493	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
16454_prefl	16454	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
16454_facelift	16454	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
10338	10338	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
18271	18271	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
15489_prefl	15489	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
15489_facelift	15489	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
18274	18274	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
16634_prefl	16634	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-WAGON-PREFL-01	HIGH	改款前BWY五门旅行车外廓。	READY
16634_facelift	16634	Wagon	Mondeo III facelift	BWY	5	EU-FORD-MONDEO-III-WAGON-FACELIFT-01	HIGH	改款后BWY五门旅行车外廓。	READY
120851	120851	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
100896	100896	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
10343_prefl	10343	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
10343_facelift	10343	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
128496_prefl	128496	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
128496_facelift	128496	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5136_prefl	5136	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
5136_facelift	5136	Hatchback	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
128494_prefl	128494	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
128494_facelift	128494	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5137_prefl	5137	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
5137_facelift	5137	Hatchback	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
54925_prefl	54925	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
54925_facelift	54925	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
126877_prefl	126877	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
126877_facelift	126877	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
126874	126874	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
5086_prefl	5086	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
5086_facelift	5086	Wagon	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
5060_prefl	5060	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
5060_facelift	5060	Wagon	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
114355_prefl	114355	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
114355_facelift	114355	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111088_prefl	111088	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111088_facelift	111088	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124773_prefl	124773	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124773_facelift	124773	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107749_prefl	107749	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107749_facelift	107749	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124779_prefl	124779	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124779_facelift	124779	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111093_prefl	111093	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111093_facelift	111093	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
124783_prefl	124783	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124783_facelift	124783	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107752_prefl	107752	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107752_facelift	107752	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107750_prefl	107750	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107750_facelift	107750	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107751_prefl	107751	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107751_facelift	107751	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
110544_prefl	110544	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
110544_facelift	110544	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
114340_prefl	114340	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
114340_facelift	114340	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107748_prefl	107748	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
107748_facelift	107748	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
108597_prefl	108597	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
108597_facelift	108597	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
107753_prefl	107753	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107753_facelift	107753	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
107754_prefl	107754	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
107754_facelift	107754	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
110549_prefl	110549	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
110549_facelift	110549	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
124784_prefl	124784	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124784_facelift	124784	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111097_prefl	111097	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111097_facelift	111097	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
111098_prefl	111098	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111098_facelift	111098	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
115100_prefl	115100	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
115100_facelift	115100	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
124786_prefl	124786	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
124786_facelift	124786	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111096_prefl	111096	Hatchback	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	HIGH	改款前物理外廓。	READY
111096_facelift	111096	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	改款后物理外廓。	READY
115101_prefl	115101	Sedan	Mondeo V		4	EU-FORD-MONDEO-V-PREFL-SEDAN-01	HIGH	改款前物理外廓。	READY
115101_facelift	115101	Sedan	Mondeo V facelift		4	EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	HIGH	改款后物理外廓。	READY
111103_prefl	111103	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111103_facelift	111103	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107755_prefl	107755	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107755_facelift	107755	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111105_prefl	111105	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111105_facelift	111105	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107760_prefl	107760	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107760_facelift	107760	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107756_prefl	107756	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107756_facelift	107756	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107758_prefl	107758	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107758_facelift	107758	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107761_prefl	107761	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107761_facelift	107761	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
107762_prefl	107762	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
107762_facelift	107762	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111110_prefl	111110	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111110_facelift	111110	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111111_prefl	111111	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111111_facelift	111111	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
111107_prefl	111107	Wagon	Mondeo V		5	EU-FORD-MONDEO-V-PREFL-WAGON-01	HIGH	改款前物理外廓。	READY
111107_facelift	111107	Wagon	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-WAGON-01	HIGH	改款后物理外廓。	READY
11166	11166	Sedan	Orion II	AFF	4	EU-FORD-ORION-II-SEDAN-01	HIGH	四门轿车外廓。	READY
15289	15289	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-SEDAN-01	HIGH	四门轿车外廓。	READY
15290	15290	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-SEDAN-01	HIGH	四门轿车外廓。	READY
154593_base	154593	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH	普通外观分支。	READY
154593_stline	154593	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	HIGH	ST-Line外观分支。	READY
146629_base	146629	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH	普通外观分支。	READY
146629_stline	146629	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-STLINE-01	HIGH	ST-Line外观分支。	READY
154601	154601	SUV	Puma II ST		5	EU-FORD-PUMA-II-SUV-ST-01	HIGH	ST专属外观分支。	READY
16032	16032	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-COUPE-01	HIGH	标准三门Coupe外廓。	READY
7813	7813	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-COUPE-01	HIGH	标准三门Coupe外廓。	READY
801248	801248	SUV	Puma Gen-E		5	EU-FORD-PUMA-GEN-E-SUV-01	HIGH	纯电五门SUV外廓。	READY
11764	11764	Coupe	Puma I Racing	ECT	3	EU-FORD-PUMA-I-RACING-COUPE-WIDEBODY-01	HIGH	Racing Puma原厂宽体外廓。	READY
155043_singlecab	155043	Pickup	Ranger IV	P703	2	EU-FORD-RANGER-P703-PICKUP-SINGLECAB-4X4-01	HIGH	Single Cab四驱外廓。	READY
155043_supercab	155043	Pickup	Ranger IV	P703	4	EU-FORD-RANGER-P703-PICKUP-SUPERCAB-4X4-01	HIGH	Super Cab四驱外廓。	READY
155043_doublecab	155043	Pickup	Ranger IV	P703	4	EU-FORD-RANGER-P703-PICKUP-DOUBLECAB-4X4-01	HIGH	Double Cab四驱外廓。	READY
12573	12573	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	HIGH	Regular Cab后驱外廓。	READY
55033	55033	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	MEDIUM	两门Regular Cab后驱外廓。	READY
57328	57328	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-PREFL-01	HIGH	Super Cab后驱外廓。	READY
116217	116217	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-FACELIFT-01	HIGH	Super Cab后驱外廓。	READY
116220	116220	Pickup	Ranger TKE facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-FACELIFT-01	HIGH	Regular Cab后驱外廓。	READY
12574_regcab	12574	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	HIGH	两门Regular Cab四驱外廓。	READY
12574_doublecab	12574	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	四门Double Cab标准四驱外廓。	READY
12605_regcab	12605	Pickup	Ranger TKE pre-facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	HIGH	两门Regular Cab四驱外廓。	READY
12605_supercab_std	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-PREFL-01	HIGH	Super Cab标准四驱外廓。	READY
12605_supercab_highspec	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-PREFL-01	HIGH	Super Cab高配四驱外廓。	READY
12605_doublecab_std	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	Double Cab标准四驱外廓。	READY
12605_doublecab_highspec	12605	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	HIGH	Double Cab高配四驱外廓。	READY
116219_regcab	116219	Pickup	Ranger TKE facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-FACELIFT-01	HIGH	两门Regular Cab四驱外廓。	READY
116219_supercab_std	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-FACELIFT-01	HIGH	Super Cab标准四驱外廓。	READY
116219_supercab_highspec	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-FACELIFT-01	HIGH	Super Cab高配四驱外廓。	READY
116219_doublecab_std	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-FACELIFT-01	HIGH	Double Cab标准四驱外廓。	READY
116219_doublecab_highspec	116219	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-FACELIFT-01	HIGH	Double Cab高配四驱外廓。	READY
116221_regcab	116221	Pickup	Ranger TKE facelift	TKE	2	EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-FACELIFT-01	HIGH	Regular Cab四驱外廓。	READY
116221_supercab	116221	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-FACELIFT-01	HIGH	Super Cab标准四驱外廓。	READY
116221_doublecab	116221	Pickup	Ranger TKE facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-FACELIFT-01	HIGH	Double Cab标准四驱外廓。	READY
14164_regcab_prefl	14164	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-PREFL-01	HIGH	改款前Regular Cab后驱外廓。	READY
14164_supercab_prefl	14164	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-PREFL-01	HIGH	改款前Super Cab后驱外廓。	READY
14601_regcab_prefl	14601	Pickup	Ranger ER/EQ		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-PREFL-01	HIGH	改款前Regular Cab四驱外廓。	READY
16871_regcab	16871	Pickup	Ranger ER/EQ/R_		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-01	HIGH	两门Regular Cab 4x2外廓。	READY
16871_supercab	16871	Pickup	Ranger ER/EQ/R_		2	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-01	HIGH	两门Super Cab 4x2外廓。	READY
14163_doublecab_prefl	14163	Pickup	Ranger ER/EQ		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-PREFL-01	HIGH	改款前Double Cab四驱外廓。	READY
14163_regcab_facelift	14163	Pickup	Ranger ER/EQ facelift		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	HIGH	改款后Regular Cab四驱外廓。	READY
14163_supercab_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	HIGH	改款后标准Super Cab四驱外廓。	READY
14163_supercab_xlt_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Super Cab外廓。	READY
14163_doublecab_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	HIGH	改款后标准Double Cab四驱外廓。	READY
14163_doublecab_xlt_facelift	14163	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Double Cab外廓。	READY
16872_regcab_facelift	16872	Pickup	Ranger ER/EQ facelift		2	EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	HIGH	改款后Regular Cab四驱外廓。	READY
16872_supercab_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	HIGH	改款后标准Super Cab四驱外廓。	READY
16872_supercab_xlt_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Super Cab外廓。	READY
16872_doublecab_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	HIGH	改款后标准Double Cab四驱外廓。	READY
16872_doublecab_xlt_facelift	16872	Pickup	Ranger ER/EQ facelift		4	EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	HIGH	改款后XLT加宽轮眉Double Cab外廓。	READY
12606	12606	Pickup	Ranger TKE pre-facelift	TKE	4	EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	HIGH	Double Cab高配四驱外廓。	READY
16737	16737	Sedan	Scorpio I	GGE	4	EU-FORD-SCORPIO-I-SEDAN-01	HIGH	四门轿车外廓。	READY
5744	5744	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH	四门轿车外廓。	READY
7810	7810	Sedan	Scorpio II		4	EU-FORD-SCORPIO-II-SEDAN-01	HIGH	四门轿车外廓。	READY
5747	5747	Wagon	Scorpio II		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH	五门旅行车外廓。	READY
7811	7811	Wagon	Scorpio II		5	EU-FORD-SCORPIO-II-WAGON-01	HIGH	五门旅行车外廓。	READY
11562_3dr	11562	Hatchback	Sierra I		3	EU-FORD-SIERRA-I-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
11562_5dr	11562	Hatchback	Sierra I		5	EU-FORD-SIERRA-I-HATCHBACK-5D-01	HIGH	五门掀背外廓。	READY
121807_3dr_prefl	121807	Hatchback	Sierra II		3	EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	HIGH	1990年更新前三门掀背外廓。	READY
121807_5dr_prefl	121807	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	HIGH	1990年更新前五门掀背外廓。	READY
121807_3dr_facelift	121807	Hatchback	Sierra II facelift		3	EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	HIGH	1990年更新后三门掀背外廓。	READY
121807_5dr_facelift	121807	Hatchback	Sierra II facelift		5	EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	HIGH	1990年更新后五门掀背外廓。	READY
8736	8736	Sedan	Sierra RS Cosworth		4	EU-FORD-SIERRA-RS-COSWORTH-4X4-SEDAN-01	HIGH	输入车身标签与可靠车型资料不一致，按四门Cosworth轿车外廓映射。	READY
15021_prefl	15021	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	1990年中期外观更新前四门轿车外廓。	READY
15021_facelift	15021	Sedan	Sierra II facelift		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	HIGH	1990年中期外观更新后四门轿车外廓。	READY
15028_prefl	15028	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	MEDIUM	更新前五门四驱旅行车外廓。	READY
15028_facelift	15028	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	HIGH	更新后五门四驱旅行车外廓。	READY
8733	8733	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
8734_3dr_prefl	8734	Hatchback	Sierra II		3	EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	HIGH	1990年更新前三门掀背外廓。	READY
8734_5dr_prefl	8734	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	HIGH	1990年更新前五门掀背外廓。	READY
8734_3dr_facelift	8734	Hatchback	Sierra II facelift		3	EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	HIGH	1990年更新后三门掀背外廓。	READY
8734_5dr_facelift	8734	Hatchback	Sierra II facelift		5	EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	HIGH	1990年更新后五门掀背外廓。	READY
8735_prefl	8735	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-PREFL-01	HIGH	更新前五门后驱旅行车外廓。	READY
8735_facelift	8735	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	HIGH	更新后五门后驱旅行车外廓。	READY
15025_prefl	15025	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	HIGH	1990年中期外观更新前四门轿车外廓。	READY
15025_facelift	15025	Sedan	Sierra II facelift		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	HIGH	1990年中期外观更新后四门轿车外廓。	READY
15027_prefl	15027	Wagon	Sierra II	BNG	5	EU-FORD-SIERRA-II-WAGON-PREFL-01	HIGH	更新前五门后驱旅行车外廓。	READY
15027_facelift	15027	Wagon	Sierra II facelift	BNG	5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	HIGH	更新后五门后驱旅行车外廓。	READY
16900	16900	Wagon	Sierra I	BNC	5	EU-FORD-SIERRA-I-WAGON-4X4-01	HIGH	五门四驱旅行车外廓。	READY
16901	16901	Wagon	Sierra I	BNC	5	EU-FORD-SIERRA-I-WAGON-4X4-01	HIGH	五门四驱旅行车外廓。	READY
16897_3dr	16897	Hatchback	Sierra I XR 4x4		3	EU-FORD-SIERRA-I-XR4X4-HATCHBACK-3D-01	HIGH	XR 4x4三门掀背外廓。	READY
16897_5dr	16897	Hatchback	Sierra I XR 4x4		5	EU-FORD-SIERRA-I-XR4X4-HATCHBACK-5D-01	HIGH	XR 4x4五门掀背外廓。	READY
15589	15589	Hatchback	Sierra I XR4i		3	EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	HIGH	XR4i三门专属外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5801-5900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-III-WAGON-PREFL-01	4804	1812	1441	Automobile-Catalog 2001 Ford Mondeo Estate	https://www.automobile-catalog.com/car/2001/975005/ford_mondeo_estate_2_0_di_zetec.html
EU-FORD-MONDEO-III-WAGON-FACELIFT-01	4804	1812	1441	Ford Mondeo 2005 official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500	Automobile-Catalog 2011 Ford Mondeo 4-door	https://www.automobile-catalog.com/car/2011/1595495/ford_mondeo_5-dr_2_0_flexifuel_trend.html
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500	Automobile-Catalog 2008 Ford Mondeo 4-door	https://www.automobile-catalog.com/car/2008/978695/ford_mondeo_4-dr_2_0_zetec.html
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Automobile-Catalog 2008 Ford Mondeo 5-door	https://www.automobile-catalog.com/car/2008/977255/ford_mondeo_5-dr_2_0_trend.html
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Automobile-Catalog 2011 Ford Mondeo 5-door	https://www.automobile-catalog.com/car/2011/1594460/ford_mondeo_5-dr_2_0_ecoboost_240_ghia.html
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Automobile-Catalog 2008 Ford Mondeo Turnier	https://www.automobile-catalog.com/car/2008/978050/ford_mondeo_turnier_2_0_ghia.html
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Automobile-Catalog 2011 Ford Mondeo Turnier	https://www.automobile-catalog.com/car/2011/1595555/ford_mondeo_5-dr_2_0_trend.html
EU-FORD-MONDEO-V-PREFL-SEDAN-01	4871	1852	1482	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-FACELIFT-SEDAN-01	4871	1852	1482	Ford UK Mondeo official brochure; Ford UK Mondeo Vignale official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo_Vignale.pdf
EU-FORD-MONDEO-V-PREFL-HATCHBACK-01	4871	1852	1482	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	4871	1852	1482	Ford UK Mondeo official brochure; Ford UK Mondeo Vignale official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo_Vignale.pdf
EU-FORD-MONDEO-V-PREFL-WAGON-01	4867	1852	1501	Ford New Zealand Mondeo official brochure	https://www.ford.co.nz/content/dam/Ford/website-assets/ap/nz/nameplate/Mondeo/brochure/Mondeo-Brochure-Updated-2018.pdf
EU-FORD-MONDEO-V-FACELIFT-WAGON-01	4867	1852	1501	Ford UK Mondeo official brochure; Ford UK Mondeo Vignale official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo.pdf; https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Mondeo_Vignale.pdf
EU-FORD-ORION-II-SEDAN-01	4213	1640	1389	Automobile-Catalog 1988 Ford Orion 1.6i Ghia	https://www.automobile-catalog.com/car/1988/943340/ford_orion_1_6i_ghia.html
EU-FORD-ORION-III-SEDAN-01	4229	1690	1395	Automobile-Catalog 1990 Ford Orion 1.4i CLX; Automobile-Catalog 1990 Ford Orion 1.6i CLX	https://www.automobile-catalog.com/car/1990/945200/ford_orion_1_4i_clx.html; https://www.automobile-catalog.com/car/1990/945470/ford_orion_1_6i_clx.html
EU-FORD-PUMA-II-SUV-01	4186	1805	1550	Ford Puma official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Puma_new.pdf
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537	Ford UK Puma official specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Puma_new.pdf
EU-FORD-PUMA-II-SUV-ST-01	4226	1805	1533	Ford UK Puma official specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Puma_new.pdf
EU-FORD-PUMA-I-COUPE-01	3984	1674	1345	Auto-Data Ford Puma Coupe (ECT)	https://www.auto-data.net/en/ford-puma-coupe-ect-generation-1760
EU-FORD-PUMA-GEN-E-SUV-01	4214	1805	1555	Ford Europe Puma Gen-E official factsheet	https://www.fordpers.be/content/documents/news/2024/ford_2024_puma_gen_e_factsheet_eu.pdf
EU-FORD-PUMA-I-RACING-COUPE-WIDEBODY-01	3984	1770	1315	Carfolio Ford Racing Puma	https://www.carfolio.com/ford-racing-puma-87571
EU-FORD-RANGER-P703-PICKUP-SINGLECAB-4X4-01	5370	1918	1880	Ford Spain Ranger official brochure; Ford South Africa Ranger official specifications	https://www.ford.es/content/dam/guxeu/es/documents/brochures/cars/ranger/BRO-ford_ranger.pdf; https://www.ford.co.za/content/dam/Ford/za/nameplate/ranger/brochure/specs-brochure/20260609-ranger-brochure.pdf
EU-FORD-RANGER-P703-PICKUP-SUPERCAB-4X4-01	5370	1918	1874	Ford Spain Ranger official brochure; Ford South Africa Ranger official specifications	https://www.ford.es/content/dam/guxeu/es/documents/brochures/cars/ranger/BRO-ford_ranger.pdf; https://www.ford.co.za/content/dam/Ford/za/nameplate/ranger/brochure/specs-brochure/20260609-ranger-brochure.pdf
EU-FORD-RANGER-P703-PICKUP-DOUBLECAB-4X4-01	5370	1918	1884	Ford Spain Ranger official brochure; Ford South Africa Ranger official specifications	https://www.ford.es/content/dam/guxeu/es/documents/brochures/cars/ranger/BRO-ford_ranger.pdf; https://www.ford.co.za/content/dam/Ford/za/nameplate/ranger/brochure/specs-brochure/20260609-ranger-brochure.pdf
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-PREFL-01	5274	1850	1703	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-PREFL-01	5359	1850	1706	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X2-FACELIFT-01	5362	1860	1804	Ford Ranger facelift official technical specifications	https://www.mustang-italia.it/pdf_pickup_2018/ranger2016_spec_tec_IT.pdf
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X2-FACELIFT-01	5277	1860	1800	Ford Ranger facelift official technical specifications	https://www.mustang-italia.it/pdf_pickup_2018/ranger2016_spec_tec_IT.pdf
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-PREFL-01	5274	1850	1800	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-PREFL-01	5359	1850	1815	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-PREFL-01	5359	1850	1804	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-PREFL-01	5359	1850	1840	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-PREFL-01	5359	1850	1848	Ford Ranger 2015 official UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Ranger-UK.pdf
EU-FORD-RANGER-TKE-PICKUP-REGCAB-4X4-FACELIFT-01	5277	1860	1800	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-4X4-FACELIFT-01	5362	1860	1804	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-SUPERCAB-HIGHSPEC-4X4-FACELIFT-01	5362	1860	1840	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-4X4-FACELIFT-01	5362	1860	1815	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-TKE-PICKUP-DOUBLECAB-HIGHSPEC-4X4-FACELIFT-01	5362	1860	1848	Ford Ranger facelift official UK brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-Ranger.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-PREFL-01	4998	1695	1615	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-PREFL-01	4998	1695	1615	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-PREFL-01	4998	1750	1740	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X2-01	5012	1695	1615	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X2-01	5012	1695	1615	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-PREFL-01	4998	1750	1750	Ford Ranger 1999 official brochure	https://xr793.com/wp-content/uploads/2023/02/1999-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-REGCAB-4X4-01	5022	1740	1740	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-4X4-01	5022	1740	1740	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-SUPERCAB-XLT-4X4-01	5022	1810	1750	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-4X4-01	5022	1740	1750	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-RANGER-ER-EQ-PICKUP-DOUBLECAB-XLT-4X4-01	5022	1810	1760	Ford Ranger 2005 official brochure	https://xr793.com/wp-content/uploads/2020/10/2005-Ford-Ranger-UK.pdf
EU-FORD-SCORPIO-I-SEDAN-01	4740	1760	1440	Autoevolution Ford Scorpio Sedan 1990	https://www.autoevolution.com/cars/ford-scorpio-sedan-1990.html
EU-FORD-SCORPIO-II-SEDAN-01	4825	1760	1388	Ford Scorpio 1997 official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Scorpio-1997-UK.pdf
EU-FORD-SCORPIO-II-WAGON-01	4826	1760	1442	Ford Scorpio 1997 official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Scorpio-1997-UK.pdf
EU-FORD-SIERRA-I-HATCHBACK-3D-01	4394	1703	1408	Automobile-Catalog 1986 Ford Sierra 1.3 L	https://www.automobile-catalog.com/car/1986/929390/ford_sierra_1_3_l.html
EU-FORD-SIERRA-I-HATCHBACK-5D-01	4394	1703	1408	Automobile-Catalog 1986 Ford Sierra 1.3 L	https://www.automobile-catalog.com/car/1986/929390/ford_sierra_1_3_l.html
EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	4425	1694	1407	Automobile-Catalog 1987 Ford Sierra 2.0 CL	https://www.automobile-catalog.com/car/1987/932900/ford_sierra_2_0_cl.html
EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	4425	1694	1407	Automobile-Catalog 1987 Ford Sierra 2.0 CL	https://www.automobile-catalog.com/car/1987/932900/ford_sierra_2_0_cl.html
EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	4420	1689	1410	Autoevolution Ford Sierra 3 Doors 1990	https://www.autoevolution.com/cars/ford-sierra-3-doors-1990.html
EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	4420	1689	1410	Autoevolution Ford Sierra 5 Doors 1990	https://www.autoevolution.com/cars/ford-sierra-5-doors-1990.html
EU-FORD-SIERRA-RS-COSWORTH-4X4-SEDAN-01	4494	1698	1376	Automobile-Catalog 1990 Ford Sierra Cosworth 4x4	https://www.automobile-catalog.com/car/1990/936410/ford_sierra_cosworth_4x4.html
EU-FORD-SIERRA-II-SEDAN-PREFL-01	4467	1698	1407	Automobile-Catalog 1987 Ford Sierra Sapphire 2.0i Ghia automatic	https://www.automobile-catalog.com/car/1987/934565/ford_sierra_sapphire_2_0i_ghia_automatic.html
EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	4501	1698	1407	Automobile-Catalog 1991 Ford Sierra Sapphire 2.0i DOHC Ghia	https://www.automobile-catalog.com/car/1991/935510/ford_sierra_sapphire_2_0i_dohc_ghia.html
EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	4511	1720	1410	Automobile-Catalog 1989 Ford Sierra Turnier 2.9i Ghia 4x4 catalyst	https://www.automobile-catalog.com/car/1989/934745/ford_sierra_turnier_2_9i_ghia_4x4_cat.html
EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	4544	1720	1476	Automobile-Catalog 1991 Ford Sierra Turnier 2.0i DOHC Ghia 4x4 catalyst	https://www.automobile-catalog.com/car/1991/936005/ford_sierra_turnier_2_0i_dohc_ghia_4x4_cat.html
EU-FORD-SIERRA-II-WAGON-PREFL-01	4511	1720	1428	Automobile-Catalog 1989 Ford Sierra Turnier 2.0i Ghia catalyst	https://www.automobile-catalog.com/car/1989/933320/ford_sierra_turnier_2_0i_ghia_cat.html
EU-FORD-SIERRA-II-WAGON-FACELIFT-01	4544	1720	1488	Automobile-Catalog 1991 Ford Sierra Turnier 2.0i CLX catalyst	https://www.automobile-catalog.com/car/1991/935270/ford_sierra_turnier_2_0i_clx_cat.html
EU-FORD-SIERRA-I-WAGON-4X4-01	4522	1729	1438	Automobile-Catalog 1986 Ford Sierra Turnier 2.8i V6 Ghia 4x4	https://www.automobile-catalog.com/car/1986/932630/ford_sierra_turnier_2_8i_v6_ghia_4x4.html
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-3D-01	4459	1725	1378	Automobile-Catalog 1985 Ford Sierra XR 4x4	https://www.automobile-catalog.com/car/1985/52220/ford_sierra_xr_4x4.html
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-5D-01	4459	1725	1378	Automobile-Catalog 1985 Ford Sierra XR 4x4	https://www.automobile-catalog.com/car/1985/52220/ford_sierra_xr_4x4.html
EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	4459	1728	1392	Automobile-Catalog 1984 Ford Sierra XR4i	https://www.automobile-catalog.com/car/1984/30050/ford_sierra_xr4i.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5801-5900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.mustang-italia.it/pdf_pickup_2018/ranger2016_spec_tec_IT.pdf "https://www.mustang-italia.it/pdf_pickup_2018/ranger2016_spec_tec_IT.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2013 行）
- 累计尺寸组：dimension_groups_final.tsv（504 行）

