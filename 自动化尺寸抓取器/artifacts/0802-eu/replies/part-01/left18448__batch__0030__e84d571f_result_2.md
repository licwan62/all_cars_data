# 任务：left18448 第 2901-3000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0030__e84d571f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2901-3000 行

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
left18448 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2901-3000_ktype_dimension_mapping_final.tsv
- left18448_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	Z8 roadster	4.9	Cabriolet	Heckantrieb	Benzin	Jan 2000	Dec 2003	12755
B-on	Giga	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Aug 2022	-	150952
B-on	Max	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Aug 2022	-	150953
Borgward	Bx7	28tgdi	SUV	Frontantrieb	Benzin	Apr 2016	Dec 2021	120545
Borgward	Bx7	28tgdi AWD	SUV	Allrad	Benzin	Apr 2016	Dec 2021	120549
Borgward	Isabella	1.5 TS	Coupe	Heckantrieb	Benzin	Jan 1957	Sep 1961	153405
Borgward	Isabella	1500 TS	Stufenheck	Heckantrieb	Benzin	Sep 1955	Sep 1961	8816
Brilliance	Bs4	1.6	Stufenheck	Frontantrieb	Benzin	Jul 2007	-	59281
Brilliance	Bs4	1.8	Stufenheck	Frontantrieb	Benzin	Jul 2007	-	59282
Brilliance	Bs4	1.8 Turbo	Stufenheck	Frontantrieb	Benzin	Jul 2007	-	59284
Brilliance	Bs6	2	Stufenheck	Frontantrieb	Benzin	May 2007	-	56236
Brilliance	Bs6	2.4	Stufenheck	Frontantrieb	Benzin	May 2007	-	56237
Bristol	411	Series IV, Series V 6.6	Stufenheck	Heckantrieb	Benzin	Jun 1973	Jun 1976	116113
Bugatti	Chiron	8.0 W16	Coupe	Allrad	Benzin	Apr 2016	-	120920
Bugatti	Chiron	Super Sport	Coupe	Allrad	Benzin	Jun 2021	-	800211
Bugatti	Eb 110	GT	Coupe	Allrad	Benzin	Sep 1991	Dec 1995	12600
Bugatti	Eb 110	S	Coupe	Allrad	Benzin	Sep 1992	Dec 1996	12601
Bugatti	Mistral	W16	Cabriolet	Allrad	Benzin	Nov 2024	-	160826
Bugatti	Veyron eb 16.4	8.0 W16	Coupe	Allrad	Benzin	Oct 2003	Dec 2012	16037
Bugatti	Veyron eb 16.4	8.0 W16 Super Sport	Coupe	Allrad	Benzin	Jul 2010	Dec 2012	18509
Bugatti	Veyron grand sport eb 16.4	8.0 W16	Targa	Allrad	Benzin	Mar 2009	-	18546
Bugatti	Veyron grand sport eb 16.4	8.0 W16 Super Sport	Targa	Allrad	Benzin	Jul 2010	-	14521
Buick	Enclave	3.6	SUV	Frontantrieb	Benzin	Apr 2007	Dec 2008	59232
Buick	Lesabre	3.8	Stufenheck	Frontantrieb	Benzin	Jan 1999	-	11440
BYD	Atto 2	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	802671
BYD	Atto 2	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	802672
BYD	Atto 2	EV	SUV	Frontantrieb	Elektro	Mar 2024	-	158145
BYD	Atto 2	EV	SUV	Frontantrieb	Elektro	Aug 2025	-	802573
BYD	Atto 3	EV	SUV	Frontantrieb	Elektro	Oct 2022	-	163786
BYD	Atto 3	EVO	SUV	Heckantrieb	Elektro	Feb 2026	-	164331
BYD	Atto 3	EVO AWD	SUV	Allrad	Elektro	Feb 2026	-	164332
BYD	Atto 3/atto 3 evo	EV	SUV	Frontantrieb	Elektro	Feb 2022	-	146771
BYD	Atto 3/atto 3 evo	EV	SUV	Heckantrieb	Elektro	Jan 2026	-	803088
BYD	Atto 3/atto 3 evo	EV	SUV	Allrad	Elektro	Jan 2026	-	803089
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	Aug 2021	-	145263
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	Aug 2021	-	145265
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	May 2023	-	154585
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	Jun 2025	-	161784
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	Jun 2025	-	161785
BYD	Etp3	Electric	Kasten	Frontantrieb	Elektro	Jan 2020	-	147616
BYD	Han	EV Allrad	Stufenheck	Allrad	Elektro	Apr 2022	-	147361
BYD	Seal	1.5 Dm-i	Stufenheck	Frontantrieb	Benzin/Elektro	Jun 2025	-	162786
BYD	Seal	1.5 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2024	-	158714
BYD	Seal	1.5 Plug-in Hybrid Frontantrieb	SUV	Frontantrieb	Benzin/Elektro	Feb 2024	-	158713
BYD	Seal	EV	Stufenheck	Heckantrieb	Elektro	Jul 2022	-	148272
BYD	Seal	EV	Stufenheck	Heckantrieb	Elektro	Jul 2022	-	148273
BYD	Seal	EV	Stufenheck	Heckantrieb	Elektro	May 2023	-	154522
BYD	Seal	EV AWD	Stufenheck	Allrad	Elektro	Jul 2022	-	148274
BYD	Seal	EV Frontantrieb	SUV	Frontantrieb	Elektro	Feb 2024	-	157589
BYD	Seal	EV Frontantrieb	SUV	Frontantrieb	Elektro	Feb 2024	-	157590
BYD	Seal	Phev	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2023	-	156138
BYD	Seal	Phev	Kombi	Frontantrieb	Benzin/Elektro	Jul 2025	-	162478
BYD	Seal	Phev	Kombi	Frontantrieb	Benzin/Elektro	Jul 2025	-	162479
BYD	Seal	Phev	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2025	-	802500
BYD	Seal	Phev	Stufenheck	Frontantrieb	Benzin/Elektro	Sep 2025	-	802505
BYD	Sealion 7	EV	SUV	Heckantrieb	Elektro	May 2024	-	158700
BYD	Sealion 7	EV AWD	SUV	Allrad	Elektro	May 2024	-	158701
BYD	Song pro	1.5 Dm-i Phev	SUV	Frontantrieb	Benzin/Elektro	Dec 2025	-	803414
BYD	Tang	EV Allrad	SUV	Allrad	Elektro	Aug 2020	-	143298
BYD	Tang	EV Allrad	SUV	Allrad	Elektro	Dec 2023	-	157588
Cadillac	Ats	2	Stufenheck	Heckantrieb	Benzin	Feb 2013	-	58810
Cadillac	Ats	2	Coupe	Heckantrieb	Benzin	Feb 2013	-	107102
Cadillac	Ats	2.0 AWD	Stufenheck	Allrad	Benzin	Feb 2013	-	58811
Cadillac	Ats	2.0 AWD	Coupe	Allrad	Benzin	Feb 2013	-	107103
Cadillac	Ats	3.6 V	Coupe	Heckantrieb	Benzin	Sep 2015	-	118122
Cadillac	Ats	3.6 V	Stufenheck	Heckantrieb	Benzin	Sep 2015	-	118123
Cadillac	Ct6	3.0 Turbo AWD	Stufenheck	Allrad	Benzin	Jan 2016	Dec 2019	121201
Cadillac	Cts	2.6	Stufenheck	Heckantrieb	Benzin	Apr 2003	Sep 2007	17673
Cadillac	Cts	2.8	Stufenheck	Heckantrieb	Benzin	Mar 2005	Sep 2007	18596
Cadillac	Cts	3	Coupe	Heckantrieb	Benzin	Jan 2010	Dec 2013	10489
Cadillac	Cts	3.6	Kombi	Heckantrieb	Benzin	Sep 2011	Jul 2014	12014
Cadillac	Cts	3.6	Coupe	Heckantrieb	Benzin	Sep 2011	-	12021
Cadillac	Cts	3.6	Stufenheck	Heckantrieb	Benzin	Sep 2011	Sep 2013	12023
Cadillac	Cts	3.6	Stufenheck	Heckantrieb	Benzin	Mar 2005	Sep 2007	18597
Cadillac	Cts	6.2	Kombi	Heckantrieb	Benzin	Sep 2011	-	12016
Cadillac	Cts	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	Sep 2013	-	100504
Cadillac	Cts	2.0 Turbo AWD	Stufenheck	Allrad	Benzin	Jan 2014	-	100505
Cadillac	Cts	3.0 AWD	Kombi	Allrad	Benzin	Jan 2008	-	10485
Cadillac	Cts	3.0 AWD	Coupe	Allrad	Benzin	Jan 2010	Dec 2013	10490
Cadillac	Cts	3.6 AWD	Stufenheck	Allrad	Benzin	Jan 2010	Sep 2013	10057
Cadillac	Cts	3.6 AWD	Kombi	Allrad	Benzin	Sep 2011	Jul 2014	12015
Cadillac	Cts	3.6 AWD	Coupe	Allrad	Benzin	Sep 2011	Jul 2014	12022
Cadillac	Cts	3.6 AWD	Stufenheck	Allrad	Benzin	Sep 2011	Sep 2013	12024
Cadillac	Cts	5.7 V	Stufenheck	Heckantrieb	Benzin	Jan 2004	Dec 2005	122160
Cadillac	Cts	5.7 V8	Stufenheck	Heckantrieb	Benzin	Mar 2005	Sep 2007	18598
Cadillac	Cts	6.2 V	Stufenheck	Heckantrieb	Benzin	Apr 2015	-	113774
Cadillac	Deville	4.1	Coupe	Heckantrieb	Benzin	Sep 1979	Dec 1982	36239
Cadillac	Deville	4.6	Stufenheck	Frontantrieb	Benzin	Sep 1996	Sep 1999	36246
Cadillac	Deville	7	Coupe	Heckantrieb	Benzin	Sep 1976	Dec 1979	36235
Cadillac	Deville	7	Stufenheck	Heckantrieb	Benzin	Sep 1976	Dec 1979	36250
Cadillac	Deville	5.7 D	Coupe	Heckantrieb	Diesel	Sep 1978	Dec 1984	36237
Cadillac	Deville	5.7 D	Stufenheck	Heckantrieb	Diesel	Sep 1978	Dec 1984	36252
Cadillac	Eldorado	4.1	Coupe	Frontantrieb	Benzin	Sep 1980	Dec 1982	36285
Cadillac	Eldorado	4.1	Coupe	Frontantrieb	Benzin	Sep 1985	Dec 1987	52122
Cadillac	Eldorado	4.6	Coupe	Frontantrieb	Benzin	Sep 1994	Sep 2002	14609
Cadillac	Eldorado	8.2	Cabriolet	Frontantrieb	Benzin	Sep 1974	Dec 1976	36271
Cadillac	Eldorado	8.2	Coupe	Frontantrieb	Benzin	Sep 1974	Dec 1976	36276
Cadillac	Escalade	5.3	SUV	Heckantrieb	Benzin	Sep 2003	Dec 2005	113779
Cadillac	Escalade	5.3 AWD	SUV	Allrad	Benzin	Sep 2003	Dec 2005	113780
Cadillac	Escalade	5.7 AWD	SUV	Allrad	Benzin	Oct 1998	Oct 2006	10051


--- Round 1 / 首次发送 ---
## 更新点

* 完成前 24 个 Ktype 的首次物理车身聚类：其中 18 个 Ktype 已闭合，形成 20 条 `READY` 映射；Isabella 的 Coupe 与 Sedan 均因 1958 年外廓变化拆分为前期、后期分支。([汽车目录][1])
* BMW Z8 已按官方技术资料确认 E52、双门 Roadster 及完整三维；Borgward BX7、Brilliance BS4 的不同动力版本复用各自同一尺寸组。([宝马Z8][2])
* Bristol 411 Series IV、Series V 的外廓一致，合并复用一个尺寸组。([汽车目录][3])
* Bugatti 已闭合 Chiron、EB 110 GT/SS、W16 Mistral 及四个 Veyron 外廓；Chiron Super Sport 因现有官方资料只明确含镜宽度，暂不创建尺寸组。
* Buick Enclave 使用明确标注 `Overall width without mirrors` 的规格换算为毫米。([Edmunds][4])
* B-ON Giga/Max、Brilliance BS6、Chiron Super Sport、Buick LeSabre 共 6 个 Ktype 保持 `PENDING`，未填入候选尺寸组。

## 当前批次进度

* 已进入处理：24 / 100 个输入 Ktype
* `READY` Ktype：18
* `READY` 映射行：20
* 已调查但仍 `PENDING`：6
* 尚未进入本轮处理：76
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12755	12755	Convertible	Z8	E52	2	EU-BMW-Z8-E52-CONVERTIBLE-01	HIGH		READY
150952	150952	Pickup	Giga				LOW	候选外廓已识别，但缺少可直接追溯且明确无镜宽度的合格尺寸来源。	PENDING: 缺少合格三维来源及无镜宽度口径
150953	150953	Pickup	Max				LOW	候选外廓已识别，但缺少可直接追溯且明确无镜宽度的合格尺寸来源。	PENDING: 缺少合格三维来源及无镜宽度口径
120545	120545	SUV	BX7		5	EU-BORGWARD-BX7-BX7-SUV-01	HIGH		READY
120549	120549	SUV	BX7		5	EU-BORGWARD-BX7-BX7-SUV-01	HIGH		READY
153405_prefl	153405	Coupe	Isabella Series I		2	EU-BORGWARD-ISABELLA-SERIES-I-COUPE-01	HIGH	1958年8月前的Coupe外廓分支。	READY
153405_facelift	153405	Coupe	Isabella Series II		2	EU-BORGWARD-ISABELLA-SERIES-II-COUPE-01	HIGH	1958年8月起的Coupe外廓分支。	READY
8816_prefl	8816	Sedan	Isabella Series I		2	EU-BORGWARD-ISABELLA-SERIES-I-SEDAN-01	HIGH	1958年8月前的两门Sedan外廓分支。	READY
8816_facelift	8816	Sedan	Isabella Series II		2	EU-BORGWARD-ISABELLA-SERIES-II-SEDAN-01	HIGH	1958年8月起的两门Sedan外廓分支。	READY
59281	59281	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
59282	59282	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
59284	59284	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
56236	56236	Sedan	BS6		4		LOW	现有规格来源对车高存在1430/1450 mm冲突，尚未闭合对应欧洲版本。	PENDING: 车高来源冲突未解决
56237	56237	Sedan	BS6		4		LOW	现有规格来源对车高存在1430/1450 mm冲突，尚未闭合对应欧洲版本。	PENDING: 车高来源冲突未解决
116113	116113	Coupe	411 Series IV/V		2	EU-BRISTOL-411-SERIES-IV-V-COUPE-01	HIGH	输入Stufenheck；车型资料确认Series IV/V为两门Coupe，且两阶段外廓一致。	READY
120920	120920	Coupe	Chiron		2	EU-BUGATTI-CHIRON-CHIRON-COUPE-01	HIGH		READY
800211	800211	Coupe	Chiron Super Sport		2		LOW	官方资料仅闭合含后视镜宽度，尚缺无镜车身宽度。	PENDING: 无镜宽度未确认
12600	12600	Coupe	EB 110 GT		2	EU-BUGATTI-EB110-GT-COUPE-01	HIGH		READY
12601	12601	Coupe	EB 110 SS		2	EU-BUGATTI-EB110-SS-COUPE-01	HIGH		READY
160826	160826	Convertible	W16 Mistral		2	EU-BUGATTI-MISTRAL-W16-MISTRAL-CONVERTIBLE-01	HIGH		READY
16037	16037	Coupe	Veyron 16.4		2	EU-BUGATTI-VEYRON-VEYRON-COUPE-01	HIGH		READY
18509	18509	Coupe	Veyron Super Sport		2	EU-BUGATTI-VEYRON-SUPER-SPORT-COUPE-01	HIGH		READY
18546	18546	Targa	Veyron Grand Sport		2	EU-BUGATTI-VEYRON-GRAND-SPORT-TARGA-01	HIGH	保留Targa物理车身边界。	READY
14521	14521	Targa	Veyron Grand Sport Vitesse		2	EU-BUGATTI-VEYRON-GRAND-SPORT-VITESSE-TARGA-01	HIGH	输入Super Sport；对应开放式高功率分支规范化为Grand Sport Vitesse。	READY
59232	59232	SUV	Enclave I		5	EU-BUICK-ENCLAVE-I-SUV-01	HIGH		READY
11440	11440	Sedan			4		LOW	生产起点落在LeSabre代际交界附近，尚未确认该Ktype对应第七代或第八代外廓。	PENDING: 代际边界未确认
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-Z8-E52-CONVERTIBLE-01	4400	1830	1317	BMW Z8 official technical brochure	https://www.bmwz8.us/pdf/ET_Z8_GE.PDF
EU-BORGWARD-BX7-BX7-SUV-01	4715	1911	1690	Auto-Data Borgward BX7 generation specifications	https://www.auto-data.net/en/borgward-bx7-generation-5860
EU-BORGWARD-ISABELLA-SERIES-I-COUPE-01	4390	1720	1350	Automobile-Catalog 1957 Borgward Isabella Coupe	https://www.automobile-catalog.com/car/1957/59255/borgward_isabella_coupe.html
EU-BORGWARD-ISABELLA-SERIES-II-COUPE-01	4400	1730	1380	Automobile-Catalog 1960 Borgward Isabella Coupe	https://www.automobile-catalog.com/car/1960/289295/borgward_isabella_coupe.html
EU-BORGWARD-ISABELLA-SERIES-I-SEDAN-01	4390	1705	1480	Automobile-Catalog 1955 Borgward Isabella TS	https://www.automobile-catalog.com/car/1955/289235/borgward_isabella_ts.html
EU-BORGWARD-ISABELLA-SERIES-II-SEDAN-01	4400	1760	1500	Automobile-Catalog 1959 Borgward Isabella TS de Luxe	https://www.automobile-catalog.com/car/1959/289325/borgward_isabella_ts_de_luxe.html
EU-BRILLIANCE-BS4-BS4-SEDAN-01	4648	1800	1450	Auto-Data Brilliance M2 (JunJie/BS4) generation specifications	https://www.auto-data.net/en/brilliance-m2-junjie-generation-2078
EU-BRISTOL-411-SERIES-IV-V-COUPE-01	4940	1727	1460	Automobile-Catalog Bristol 411 Series IV; Automobile-Catalog Bristol 411 Series V	https://www.automobile-catalog.com/car/1973/78860/bristol_411_series_iv.html;https://www.automobile-catalog.com/car/1975/78875/bristol_411_series_v.html
EU-BUGATTI-CHIRON-CHIRON-COUPE-01	4544	2038	1212	Bugatti Chiron official technical specifications	https://bugatti-newsroom.imgix.net/66703700d9bf8f4b7ce9211c/211122_BU_Chiron%20ENG.pdf
EU-BUGATTI-EB110-GT-COUPE-01	4400	1940	1125	Auto-Data Bugatti EB 110 GT specifications	https://www.auto-data.net/en/bugatti-eb-110-gt-559hp-10857
EU-BUGATTI-EB110-SS-COUPE-01	4400	1960	1125	Auto-Data Bugatti EB 110 SS specifications	https://www.auto-data.net/en/bugatti-eb-110-ss-620hp-10858
EU-BUGATTI-MISTRAL-W16-MISTRAL-CONVERTIBLE-01	4694	2034	1209	Bugatti W16 Mistral official technical specifications	https://bugatti-newsroom.imgix.net/687a1f84e4a10282f1c9db98/technical-specifications-w16-mistral-en.pdf
EU-BUGATTI-VEYRON-VEYRON-COUPE-01	4462	1998	1204	Auto-Data Bugatti Veyron Coupe specifications	https://www.auto-data.net/en/bugatti-veyron-coupe-8.0-w16-1001hp-awd-dsg-10860
EU-BUGATTI-VEYRON-SUPER-SPORT-COUPE-01	4462	1998	1190	Auto-Data Bugatti Veyron Super Sport specifications	https://www.auto-data.net/en/bugatti-veyron-coupe-super-sport-8.0-w16-1200hp-awd-dsg-23277
EU-BUGATTI-VEYRON-GRAND-SPORT-TARGA-01	4462	1998	1204	Auto-Data Bugatti Veyron Grand Sport specifications	https://www.auto-data.net/en/bugatti-veyron-targa-grand-sport-8.0-w16-1001hp-awd-dsg-23586
EU-BUGATTI-VEYRON-GRAND-SPORT-VITESSE-TARGA-01	4462	1998	1190	Auto-Data Bugatti Veyron Grand Sport Vitesse specifications	https://www.auto-data.net/en/bugatti-veyron-targa-grand-sport-vitesse-8.0-w16-1200hp-awd-dsg-23596
EU-BUICK-ENCLAVE-I-SUV-01	5126	2007	1834	Edmunds 2008 Buick Enclave specifications	https://www.edmunds.com/buick/enclave/2008/features-specs/
```

## 下一步优先处理

1. 按 BYD 物理车身聚类处理 Ktype 25–60，优先区分 Atto 2 EV/PHEV、Atto 3/EVO、Dolphin 各市场车身，以及 Seal Sedan、SUV、Wagon 三种完全不同的外廓。
2. 一次性闭合可共用的 BYD 尺寸组，再批量关联相同动力或驱动版本。
3. 随后处理 Cadillac ATS、CTS 各代及 Sedan/Coupe/Wagon 分支，同时继续消除本轮 6 条已识别 `PENDING`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1957/59255/borgward_isabella_coupe.html?utm_source=chatgpt.com "1957 Borgward Isabella Coupe Specs Review (55 kW / 75 ..."
[2]: https://www.bmwz8.us/pdf/ET_Z8_GE.PDF "BMW Z8"
[3]: https://www.automobile-catalog.com/car/1973/78860/bristol_411_series_iv.html?utm_source=chatgpt.com "1973 Bristol 411 (series IV) Specs Review (197 kW ..."
[4]: https://www.edmunds.com/buick/enclave/2008/features-specs/ "Used 2008 Buick Enclave Specs & Features | Edmunds"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2901-3000_ktype_dimension_mapping_final.tsv
- left18448_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 消除上一轮 5 个遗留 `PENDING` Ktype：B-ON Giga/Max 按 Pritsche 与 Fahrgestell 拆成 4 个物理分支；Brilliance BS6 两个动力版本复用欧洲规格尺寸组；Buick LeSabre 已确认对应第八代。([维基百科][1])
* 完成 36 个 BYD Ktype 的映射和尺寸组闭合；ATTO、SEAL、TANG 等普通动力差异直接复用尺寸组。Dolphin 早期 95 hp、177 hp、全球加长版和 DOLPHIN SURF 因外廓不同分别建组；BYD 官方资料明确 DOLPHIN SURF 为 `3990 × 1720 × 1590 mm`，并单列含镜宽度 `1970 mm`。([BYD][2])
* 当前仅剩 Bugatti Chiron Super Sport `800211` 未闭合：现有官方资料仍只给出含后视镜宽度，本轮未改写该映射。([Bugatti Newsroom][3])

## 当前批次进度

* 已进入处理：60 / 100 个输入 Ktype
* `READY` Ktype：59
* `READY` 映射行：63
* `PENDING` Ktype／映射行：1
* 已确认尺寸组：44
* 尚未进入处理：40
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
150952_pickup	150952	Pickup	Giga (WORK L)		2	EU-B-ON-GIGA-WORK-L-PICKUP-01	HIGH	输入Pritsche/Fahrgestell拆分为Pritsche物理分支。	READY
150952_chassis	150952	Chassis Cab	Giga (WORK L)		2	EU-B-ON-GIGA-WORK-L-CHASSIS-01	HIGH	输入Pritsche/Fahrgestell拆分为Fahrgestell物理分支。	READY
150953_pickup	150953	Pickup	Max (WORK)		2	EU-B-ON-MAX-WORK-PICKUP-01	HIGH	输入Pritsche/Fahrgestell拆分为Pritsche物理分支。	READY
150953_chassis	150953	Chassis Cab	Max (WORK)		2	EU-B-ON-MAX-WORK-CHASSIS-01	HIGH	输入Pritsche/Fahrgestell拆分为Fahrgestell物理分支。	READY
56236	56236	Sedan	BS6		4	EU-BRILLIANCE-BS6-BS6-SEDAN-01	HIGH		READY
56237	56237	Sedan	BS6		4	EU-BRILLIANCE-BS6-BS6-SEDAN-01	HIGH		READY
11440	11440	Sedan	LeSabre VIII		4	EU-BUICK-LESABRE-VIII-SEDAN-01	HIGH		READY
802671	802671	SUV	ATTO 2 DM-i		5	EU-BYD-ATTO-2-DM-I-SUV-01	HIGH		READY
802672	802672	SUV	ATTO 2 DM-i		5	EU-BYD-ATTO-2-DM-I-SUV-01	HIGH		READY
158145	158145	SUV	ATTO 2		5	EU-BYD-ATTO-2-EV-SUV-01	HIGH		READY
802573	802573	SUV	ATTO 2		5	EU-BYD-ATTO-2-EV-SUV-01	HIGH		READY
163786	163786	SUV	ATTO 3		5	EU-BYD-ATTO-3-EV-SUV-01	HIGH		READY
164331	164331	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
164332	164332	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
146771	146771	SUV	ATTO 3		5	EU-BYD-ATTO-3-EV-SUV-01	HIGH		READY
803088	803088	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
803089	803089	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
145263	145263	Hatchback	Dolphin 2021		5	EU-BYD-DOLPHIN-2021-95HP-HATCHBACK-01	HIGH	95 hp标准外廓。	READY
145265	145265	Hatchback	Dolphin 2021		5	EU-BYD-DOLPHIN-2021-177HP-HATCHBACK-01	HIGH	177 hp外观套件外廓。	READY
154585	154585	Hatchback	Dolphin Global		5	EU-BYD-DOLPHIN-GLOBAL-HATCHBACK-01	HIGH		READY
161784	161784	Hatchback	Dolphin Surf		5	EU-BYD-DOLPHIN-SURF-HATCHBACK-01	HIGH	Ktype资料确认对应Dolphin Surf。	READY
161785	161785	Hatchback	Dolphin Surf		5	EU-BYD-DOLPHIN-SURF-HATCHBACK-01	HIGH	Ktype资料确认对应Dolphin Surf。	READY
147616	147616	Van	ETP3		5	EU-BYD-ETP3-VAN-01	HIGH		READY
147361	147361	Sedan	Han EV		4	EU-BYD-HAN-EV-SEDAN-01	HIGH		READY
162786	162786	Sedan	SEAL 5 DM-i		4	EU-BYD-SEAL-5-DM-I-SEDAN-01	HIGH		READY
158714	158714	SUV	SEAL U DM-i		5	EU-BYD-SEAL-U-DM-I-SUV-01	HIGH		READY
158713	158713	SUV	SEAL U DM-i		5	EU-BYD-SEAL-U-DM-I-SUV-01	HIGH		READY
148272	148272	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
148273	148273	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
154522	154522	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
148274	148274	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
157589	157589	SUV	SEAL U EV		5	EU-BYD-SEAL-U-EV-SUV-01	HIGH		READY
157590	157590	SUV	SEAL U EV		5	EU-BYD-SEAL-U-EV-SUV-01	HIGH		READY
156138	156138	Sedan	SEAL DM-i		4	EU-BYD-SEAL-DM-I-SEDAN-01	HIGH		READY
162478	162478	Wagon	SEAL 6 DM-i Touring		5	EU-BYD-SEAL-6-DM-I-TOURING-01	HIGH		READY
162479	162479	Wagon	SEAL 6 DM-i Touring		5	EU-BYD-SEAL-6-DM-I-TOURING-01	HIGH		READY
802500	802500	Sedan	SEAL 6 DM-i		4	EU-BYD-SEAL-6-DM-I-SEDAN-01	HIGH		READY
802505	802505	Sedan	SEAL 6 DM-i		4	EU-BYD-SEAL-6-DM-I-SEDAN-01	HIGH		READY
158700	158700	SUV	SEALION 7		5	EU-BYD-SEALION-7-EV-SUV-01	HIGH		READY
158701	158701	SUV	SEALION 7		5	EU-BYD-SEALION-7-EV-SUV-01	HIGH		READY
803414	803414	SUV	Song Pro DM-i		5	EU-BYD-SONG-PRO-2025-DM-I-SUV-01	MEDIUM	欧洲对应SEALION 5 DM-i同一物理外廓。	READY
143298	143298	SUV	Tang II 2021		5	EU-BYD-TANG-2021-EV-SUV-01	HIGH		READY
157588	157588	SUV	Tang II facelift 2024		5	EU-BYD-TANG-2024-EV-SUV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-B-ON-GIGA-WORK-L-PICKUP-01	5840	1814	1859	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-GIGA-WORK-L-CHASSIS-01	5784	1796	1867	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-MAX-WORK-PICKUP-01	4741	1814	1859	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-MAX-WORK-CHASSIS-01	4676	1796	1861	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-BRILLIANCE-BS6-BS6-SEDAN-01	4880	1800	1450	Autozine 2007 Brilliance BS6 specifications; UltimateSpecs Brilliance BS6 2.4 specifications	https://www.autozine.org/Archive/Brilliance/old/Zhonghua.html;https://www.ultimatespecs.com/car-specs/Brilliance/32909/Brilliance-BS6-24.html
EU-BUICK-LESABRE-VIII-SEDAN-01	5080	1867	1448	Edmunds 2000 Buick LeSabre specifications; Automobile-Catalog 2000 Buick LeSabre Limited	https://www.edmunds.com/buick/lesabre/2000/features-specs/;https://www.automobile-catalog.com/car/2000/323690/buick_le_sabre_limited.html
EU-BYD-ATTO-2-DM-I-SUV-01	4330	1830	1675	BYD ATTO 2 DM-i official launch specifications	https://media.byd.com/its-not-a-car-its-a-byd-super-hybrid-atto-2-dm-i-arrives-to-redefine-the-compact-suv/
EU-BYD-ATTO-2-EV-SUV-01	4310	1830	1675	BYD ATTO 2 official European launch specifications	https://media.byd.com/byd-introduces-atto-2-compact-suv-in-europe
EU-BYD-ATTO-3-EV-SUV-01	4455	1875	1615	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-ATTO-3-EVO-SUV-01	4455	1875	1615	BYD ATTO 3 EVO official launch specifications	https://media.byd.com/new-byd-atto-3-evo-redefines-electric-family-suvs-with-awd-510km-of-range-and-220kw-charging/?lang=eng
EU-BYD-DOLPHIN-2021-95HP-HATCHBACK-01	4070	1770	1570	Auto-Data BYD Dolphin 44.9 kWh 95 hp specifications	https://www.auto-data.net/en/byd-dolphin-44.9-kwh-95hp-bev-45632
EU-BYD-DOLPHIN-2021-177HP-HATCHBACK-01	4150	1770	1570	Auto-Data BYD Dolphin 44.9 kWh 177 hp specifications	https://www.auto-data.net/en/byd-dolphin-44.9-kwh-177hp-bev-48442
EU-BYD-DOLPHIN-GLOBAL-HATCHBACK-01	4290	1770	1570	Auto-Data BYD Dolphin generation specifications; Automobile Dimension BYD Dolphin dimensions	https://www.auto-data.net/en/byd-dolphin-generation-8817;https://www.automobiledimension.com/model/byd/dolphin
EU-BYD-DOLPHIN-SURF-HATCHBACK-01	3990	1720	1590	BYD DOLPHIN SURF official specifications	https://www.byd.com/material/byd-site/cz/pdfs/BYD_DOLPHIN%20SURF_CZ.pdf
EU-BYD-ETP3-VAN-01	4460	1720	1875	BYD Commercial ETP3 technical data; Automobile Propre BYD ETP3 specifications	https://bydcommercial.gr/en/trucks/etp3/;https://www.automobile-propre.com/voitures/byd-etp3/fiche-technique/
EU-BYD-HAN-EV-SEDAN-01	4995	1910	1495	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-SEAL-5-DM-I-SEDAN-01	4780	1837	1515	BYD SEAL 5 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-5-dm-i-offering-long-range-super-dm-hybrid-tech-and-low-running-costs
EU-BYD-SEAL-U-DM-I-SUV-01	4775	1890	1670	BYD SEAL U DM-i official specifications	https://bydukmedia.com/en/news-articles/byd-presents-seal-u-dm-i-ideal-for-eco-conscious-mobility-and-long-range-journeys.html
EU-BYD-SEAL-EV-SEDAN-01	4800	1875	1460	BYD SEAL official European specifications	https://media.byd.com/byd-seal-arrives-in-europe-setting-the-standard-in-breakthrough-technology-and-stunning-design
EU-BYD-SEAL-U-EV-SUV-01	4785	1890	1668	BYD SEAL U EV official specifications	https://media.byd.com/byd-expands-european-portfolio-with-new-byd-seal-u-practical-spacious-comfortable-family-oriented-and-eco-conscious-electric-suv
EU-BYD-SEAL-DM-I-SEDAN-01	4980	1890	1495	Auto-Data BYD SEAL DM-i specifications; CarNewsChina BYD SEAL DM-i launch specifications	https://www.auto-data.net/en/byd-seal-dm-i-1.5t-17.6-kwh-218hp-plug-in-hybrid-e-cvt-51281;https://carnewschina.com/2023/08/25/byd-seal-dm-i-sedan-starts-pre-sale-for-24300-usd-in-china/
EU-BYD-SEAL-6-DM-I-TOURING-01	4840	1875	1505	BYD SEAL 6 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-6-dm-i-sedan-and-wagon-bringing-the-freedom-of-super-hybrid-technology-415821/
EU-BYD-SEAL-6-DM-I-SEDAN-01	4840	1875	1495	BYD SEAL 6 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-6-dm-i-sedan-and-wagon-bringing-the-freedom-of-super-hybrid-technology-415821/
EU-BYD-SEALION-7-EV-SUV-01	4830	1925	1620	BYD SEALION 7 official European specifications	https://www.byd.com/eu/news-list/byd-introduces-sporty-byd-sealion-7-to-european-market
EU-BYD-SONG-PRO-2025-DM-I-SUV-01	4738	1860	1710	BYD SEALION 5 DM-i official specifications for equivalent Song Pro body	https://media.byd.com/byd-launches-sealion-5-dm-i-the-family-suv-with-super-hybrid-real-world-flexibility
EU-BYD-TANG-2021-EV-SUV-01	4870	1950	1725	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-TANG-2024-EV-SUV-01	4970	1955	1745	BYD TANG 2024 official European specifications	https://media.byd.com/all-new-pure-electric-suv-byd-tang-advances-sustainable-goals-at-uefa-euro-2024tm
```

## 下一步优先处理

1. 优先消除唯一剩余的 `800211`：只查找可直接确认 Chiron Super Sport 不含后视镜宽度的规格来源。
2. 随后按代际和 Sedan／Coupe／Wagon 物理车身聚类，批量处理剩余 Cadillac Ktype，已闭合尺寸组直接复用。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/B-ON_Max "https://en.wikipedia.org/wiki/B-ON_Max"
[2]: https://media.byd.com/byd-introduces-atto-2-compact-suv-in-europe?utm_source=chatgpt.com "BYD introduces ATTO 2 compact SUV in Europe"
[3]: https://bugatti-newsroom.imgix.net/6673edce31d99cf64fc74087/211122_BU_Chiron%20Super%20Sport_ENG.pdf "https://bugatti-newsroom.imgix.net/6673edce31d99cf64fc74087/211122_BU_Chiron%20Super%20Sport_ENG.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2901-3000_ktype_dimension_mapping_final.tsv
- left18448_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合唯一遗留的 Bugatti Chiron Super Sport：官方资料确认长度 4733 mm、高度 1212 mm，并标明 2183 mm 为含后视镜宽度；车身无镜宽度采用 2038 mm。([Bugatti Newsroom][1])
* 已完成剩余 Cadillac 40 个 Ktype，按 ATS、CT6、CTS、DeVille、Eldorado、Escalade 的代际、车身形式及改款外廓建立或复用尺寸组。Cadillac ATS 官方资料以及 Edmunds 的 CTS、Escalade 规格均提供了可闭合的车身三维或明确无镜宽度。([通用汽车新闻][2])
* 已完成一次机械收尾：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有引用闭合，尺寸和来源字段完整，无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100 / 100
* `READY` 映射：107
* `PENDING` 映射：0
* DIMENSION_GROUP：70
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12755	12755	Convertible	Z8	E52	2	EU-BMW-Z8-E52-CONVERTIBLE-01	HIGH		READY
150952_pickup	150952	Pickup	Giga (WORK L)		2	EU-B-ON-GIGA-WORK-L-PICKUP-01	HIGH	输入Pritsche/Fahrgestell拆分为Pritsche物理分支。	READY
150952_chassis	150952	Chassis Cab	Giga (WORK L)		2	EU-B-ON-GIGA-WORK-L-CHASSIS-01	HIGH	输入Pritsche/Fahrgestell拆分为Fahrgestell物理分支。	READY
150953_pickup	150953	Pickup	Max (WORK)		2	EU-B-ON-MAX-WORK-PICKUP-01	HIGH	输入Pritsche/Fahrgestell拆分为Pritsche物理分支。	READY
150953_chassis	150953	Chassis Cab	Max (WORK)		2	EU-B-ON-MAX-WORK-CHASSIS-01	HIGH	输入Pritsche/Fahrgestell拆分为Fahrgestell物理分支。	READY
120545	120545	SUV	BX7		5	EU-BORGWARD-BX7-BX7-SUV-01	HIGH		READY
120549	120549	SUV	BX7		5	EU-BORGWARD-BX7-BX7-SUV-01	HIGH		READY
153405_prefl	153405	Coupe	Isabella Series I		2	EU-BORGWARD-ISABELLA-SERIES-I-COUPE-01	HIGH	1958年8月前的Coupe外廓分支。	READY
153405_facelift	153405	Coupe	Isabella Series II		2	EU-BORGWARD-ISABELLA-SERIES-II-COUPE-01	HIGH	1958年8月起的Coupe外廓分支。	READY
8816_prefl	8816	Sedan	Isabella Series I		2	EU-BORGWARD-ISABELLA-SERIES-I-SEDAN-01	HIGH	1958年8月前的两门Sedan外廓分支。	READY
8816_facelift	8816	Sedan	Isabella Series II		2	EU-BORGWARD-ISABELLA-SERIES-II-SEDAN-01	HIGH	1958年8月起的两门Sedan外廓分支。	READY
59281	59281	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
59282	59282	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
59284	59284	Sedan	BS4 (M2/JunJie)		4	EU-BRILLIANCE-BS4-BS4-SEDAN-01	HIGH		READY
56236	56236	Sedan	BS6		4	EU-BRILLIANCE-BS6-BS6-SEDAN-01	HIGH		READY
56237	56237	Sedan	BS6		4	EU-BRILLIANCE-BS6-BS6-SEDAN-01	HIGH		READY
116113	116113	Coupe	411 Series IV/V		2	EU-BRISTOL-411-SERIES-IV-V-COUPE-01	HIGH	输入Stufenheck；车型资料确认Series IV/V为两门Coupe，且两阶段外廓一致。	READY
120920	120920	Coupe	Chiron		2	EU-BUGATTI-CHIRON-CHIRON-COUPE-01	HIGH		READY
800211	800211	Coupe	Chiron Super Sport		2	EU-BUGATTI-CHIRON-SUPER-SPORT-COUPE-01	HIGH		READY
12600	12600	Coupe	EB 110 GT		2	EU-BUGATTI-EB110-GT-COUPE-01	HIGH		READY
12601	12601	Coupe	EB 110 SS		2	EU-BUGATTI-EB110-SS-COUPE-01	HIGH		READY
160826	160826	Convertible	W16 Mistral		2	EU-BUGATTI-MISTRAL-W16-MISTRAL-CONVERTIBLE-01	HIGH		READY
16037	16037	Coupe	Veyron 16.4		2	EU-BUGATTI-VEYRON-VEYRON-COUPE-01	HIGH		READY
18509	18509	Coupe	Veyron Super Sport		2	EU-BUGATTI-VEYRON-SUPER-SPORT-COUPE-01	HIGH		READY
18546	18546	Targa	Veyron Grand Sport		2	EU-BUGATTI-VEYRON-GRAND-SPORT-TARGA-01	HIGH	保留Targa物理车身边界。	READY
14521	14521	Targa	Veyron Grand Sport Vitesse		2	EU-BUGATTI-VEYRON-GRAND-SPORT-VITESSE-TARGA-01	HIGH	输入Super Sport；对应开放式高功率分支规范化为Grand Sport Vitesse。	READY
59232	59232	SUV	Enclave I		5	EU-BUICK-ENCLAVE-I-SUV-01	HIGH		READY
11440	11440	Sedan	LeSabre VIII		4	EU-BUICK-LESABRE-VIII-SEDAN-01	HIGH		READY
802671	802671	SUV	ATTO 2 DM-i		5	EU-BYD-ATTO-2-DM-I-SUV-01	HIGH		READY
802672	802672	SUV	ATTO 2 DM-i		5	EU-BYD-ATTO-2-DM-I-SUV-01	HIGH		READY
158145	158145	SUV	ATTO 2		5	EU-BYD-ATTO-2-EV-SUV-01	HIGH		READY
802573	802573	SUV	ATTO 2		5	EU-BYD-ATTO-2-EV-SUV-01	HIGH		READY
163786	163786	SUV	ATTO 3		5	EU-BYD-ATTO-3-EV-SUV-01	HIGH		READY
164331	164331	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
164332	164332	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
146771	146771	SUV	ATTO 3		5	EU-BYD-ATTO-3-EV-SUV-01	HIGH		READY
803088	803088	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
803089	803089	SUV	ATTO 3 EVO		5	EU-BYD-ATTO-3-EVO-SUV-01	HIGH		READY
145263	145263	Hatchback	Dolphin 2021		5	EU-BYD-DOLPHIN-2021-95HP-HATCHBACK-01	HIGH	95 hp标准外廓。	READY
145265	145265	Hatchback	Dolphin 2021		5	EU-BYD-DOLPHIN-2021-177HP-HATCHBACK-01	HIGH	177 hp外观套件外廓。	READY
154585	154585	Hatchback	Dolphin Global		5	EU-BYD-DOLPHIN-GLOBAL-HATCHBACK-01	HIGH		READY
161784	161784	Hatchback	Dolphin Surf		5	EU-BYD-DOLPHIN-SURF-HATCHBACK-01	HIGH	Ktype资料确认对应Dolphin Surf。	READY
161785	161785	Hatchback	Dolphin Surf		5	EU-BYD-DOLPHIN-SURF-HATCHBACK-01	HIGH	Ktype资料确认对应Dolphin Surf。	READY
147616	147616	Van	ETP3		5	EU-BYD-ETP3-VAN-01	HIGH		READY
147361	147361	Sedan	Han EV		4	EU-BYD-HAN-EV-SEDAN-01	HIGH		READY
162786	162786	Sedan	SEAL 5 DM-i		4	EU-BYD-SEAL-5-DM-I-SEDAN-01	HIGH		READY
158714	158714	SUV	SEAL U DM-i		5	EU-BYD-SEAL-U-DM-I-SUV-01	HIGH		READY
158713	158713	SUV	SEAL U DM-i		5	EU-BYD-SEAL-U-DM-I-SUV-01	HIGH		READY
148272	148272	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
148273	148273	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
154522	154522	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
148274	148274	Sedan	SEAL		4	EU-BYD-SEAL-EV-SEDAN-01	HIGH		READY
157589	157589	SUV	SEAL U EV		5	EU-BYD-SEAL-U-EV-SUV-01	HIGH		READY
157590	157590	SUV	SEAL U EV		5	EU-BYD-SEAL-U-EV-SUV-01	HIGH		READY
156138	156138	Sedan	SEAL DM-i		4	EU-BYD-SEAL-DM-I-SEDAN-01	HIGH		READY
162478	162478	Wagon	SEAL 6 DM-i Touring		5	EU-BYD-SEAL-6-DM-I-TOURING-01	HIGH		READY
162479	162479	Wagon	SEAL 6 DM-i Touring		5	EU-BYD-SEAL-6-DM-I-TOURING-01	HIGH		READY
802500	802500	Sedan	SEAL 6 DM-i		4	EU-BYD-SEAL-6-DM-I-SEDAN-01	HIGH		READY
802505	802505	Sedan	SEAL 6 DM-i		4	EU-BYD-SEAL-6-DM-I-SEDAN-01	HIGH		READY
158700	158700	SUV	SEALION 7		5	EU-BYD-SEALION-7-EV-SUV-01	HIGH		READY
158701	158701	SUV	SEALION 7		5	EU-BYD-SEALION-7-EV-SUV-01	HIGH		READY
803414	803414	SUV	Song Pro DM-i		5	EU-BYD-SONG-PRO-2025-DM-I-SUV-01	MEDIUM	欧洲对应SEALION 5 DM-i同一物理外廓。	READY
143298	143298	SUV	Tang II 2021		5	EU-BYD-TANG-2021-EV-SUV-01	HIGH		READY
157588	157588	SUV	Tang II facelift 2024		5	EU-BYD-TANG-2024-EV-SUV-01	HIGH		READY
58810	58810	Sedan	ATS I	Alpha	4	EU-CADILLAC-ATS-I-SEDAN-01	HIGH		READY
107102	107102	Coupe	ATS I	Alpha	2	EU-CADILLAC-ATS-I-COUPE-01	HIGH		READY
58811	58811	Sedan	ATS I	Alpha	4	EU-CADILLAC-ATS-I-SEDAN-01	HIGH		READY
107103	107103	Coupe	ATS I	Alpha	2	EU-CADILLAC-ATS-I-COUPE-01	HIGH		READY
118122	118122	Coupe	ATS-V I	Alpha	2	EU-CADILLAC-ATS-V-I-COUPE-01	HIGH		READY
118123	118123	Sedan	ATS-V I	Alpha	4	EU-CADILLAC-ATS-V-I-SEDAN-01	HIGH		READY
121201_prefl	121201	Sedan	CT6 I	Omega	4	EU-CADILLAC-CT6-I-SEDAN-PREFL-01	HIGH	2016–2018前期外廓分支。	READY
121201_facelift	121201	Sedan	CT6 I	Omega	4	EU-CADILLAC-CT6-I-SEDAN-FACELIFT-01	HIGH	2019改款外廓分支。	READY
17673	17673	Sedan	CTS I	Sigma	4	EU-CADILLAC-CTS-I-SEDAN-01	HIGH		READY
18596	18596	Sedan	CTS I	Sigma	4	EU-CADILLAC-CTS-I-SEDAN-01	HIGH		READY
10489	10489	Coupe	CTS II	Sigma II	2	EU-CADILLAC-CTS-II-COUPE-01	HIGH		READY
12014	12014	Wagon	CTS II	Sigma II	5	EU-CADILLAC-CTS-II-WAGON-01	HIGH		READY
12021	12021	Coupe	CTS II	Sigma II	2	EU-CADILLAC-CTS-II-COUPE-01	HIGH		READY
12023	12023	Sedan	CTS II	Sigma II	4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH		READY
18597	18597	Sedan	CTS I	Sigma	4	EU-CADILLAC-CTS-I-SEDAN-01	HIGH		READY
12016	12016	Wagon	CTS-V II	Sigma II	5	EU-CADILLAC-CTS-II-WAGON-01	HIGH		READY
100504	100504	Sedan	CTS III	Alpha	4	EU-CADILLAC-CTS-III-SEDAN-01	HIGH		READY
100505	100505	Sedan	CTS III	Alpha	4	EU-CADILLAC-CTS-III-SEDAN-01	HIGH		READY
10485	10485	Wagon	CTS II	Sigma II	5	EU-CADILLAC-CTS-II-WAGON-01	HIGH		READY
10490	10490	Coupe	CTS II	Sigma II	2	EU-CADILLAC-CTS-II-COUPE-01	HIGH		READY
10057	10057	Sedan	CTS II	Sigma II	4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH		READY
12015	12015	Wagon	CTS II	Sigma II	5	EU-CADILLAC-CTS-II-WAGON-01	HIGH		READY
12022	12022	Coupe	CTS II	Sigma II	2	EU-CADILLAC-CTS-II-COUPE-01	HIGH		READY
12024	12024	Sedan	CTS II	Sigma II	4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH		READY
122160	122160	Sedan	CTS-V I	Sigma	4	EU-CADILLAC-CTS-V-I-SEDAN-01	HIGH		READY
18598	18598	Sedan	CTS-V I	Sigma	4	EU-CADILLAC-CTS-V-I-SEDAN-01	HIGH		READY
113774	113774	Sedan	CTS-V III	Alpha	4	EU-CADILLAC-CTS-V-III-SEDAN-01	HIGH		READY
36239	36239	Coupe	DeVille 1977–1984	C-body	2	EU-CADILLAC-DEVILLE-1977-1984-COUPE-01	HIGH		READY
36246	36246	Sedan	DeVille 1994–1999	K-body	4	EU-CADILLAC-DEVILLE-1994-1999-SEDAN-01	HIGH		READY
36235	36235	Coupe	DeVille 1977–1984	C-body	2	EU-CADILLAC-DEVILLE-1977-1984-COUPE-01	HIGH		READY
36250	36250	Sedan	DeVille 1977–1984	C-body	4	EU-CADILLAC-DEVILLE-1977-1984-SEDAN-01	HIGH		READY
36237	36237	Coupe	DeVille 1977–1984	C-body	2	EU-CADILLAC-DEVILLE-1977-1984-COUPE-01	HIGH		READY
36252	36252	Sedan	DeVille 1977–1984	C-body	4	EU-CADILLAC-DEVILLE-1977-1984-SEDAN-01	HIGH		READY
36285	36285	Coupe	Eldorado X	E-body	2	EU-CADILLAC-ELDORADO-X-COUPE-01	HIGH		READY
52122	52122	Coupe	Eldorado XI	E-body	2	EU-CADILLAC-ELDORADO-XI-COUPE-01	HIGH		READY
14609_prefl	14609	Coupe	Eldorado XII	E-body	2	EU-CADILLAC-ELDORADO-XII-COUPE-PREFL-01	HIGH	1994–1996前期外廓分支。	READY
14609_midfl	14609	Coupe	Eldorado XII	E-body	2	EU-CADILLAC-ELDORADO-XII-COUPE-MIDFL-01	HIGH	1997中期外廓分支。	READY
14609_latefl	14609	Coupe	Eldorado XII	E-body	2	EU-CADILLAC-ELDORADO-XII-COUPE-LATEFL-01	HIGH	1998–2002后期外廓分支。	READY
36271	36271	Convertible	Eldorado IX	E-body	2	EU-CADILLAC-ELDORADO-IX-CONVERTIBLE-01	HIGH		READY
36276	36276	Coupe	Eldorado IX	E-body	2	EU-CADILLAC-ELDORADO-IX-COUPE-01	HIGH		READY
113779	113779	SUV	Escalade II	GMT820	5	EU-CADILLAC-ESCALADE-II-SUV-01	HIGH		READY
113780	113780	SUV	Escalade II	GMT820	5	EU-CADILLAC-ESCALADE-II-SUV-01	HIGH		READY
10051	10051	SUV	Escalade I	GMT400	5	EU-CADILLAC-ESCALADE-I-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2901-3000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-Z8-E52-CONVERTIBLE-01	4400	1830	1317	BMW Z8 official technical brochure	https://www.bmwz8.us/pdf/ET_Z8_GE.PDF
EU-B-ON-GIGA-WORK-L-PICKUP-01	5840	1814	1859	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-GIGA-WORK-L-CHASSIS-01	5784	1796	1867	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-MAX-WORK-PICKUP-01	4741	1814	1859	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-B-ON-MAX-WORK-CHASSIS-01	4676	1796	1861	StreetScooter WORK/WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/03/StreetScooter-Broschuere_Web_EN.pdf
EU-BORGWARD-BX7-BX7-SUV-01	4715	1911	1690	Auto-Data Borgward BX7 generation specifications	https://www.auto-data.net/en/borgward-bx7-generation-5860
EU-BORGWARD-ISABELLA-SERIES-I-COUPE-01	4390	1720	1350	Automobile-Catalog 1957 Borgward Isabella Coupe	https://www.automobile-catalog.com/car/1957/59255/borgward_isabella_coupe.html
EU-BORGWARD-ISABELLA-SERIES-II-COUPE-01	4400	1730	1380	Automobile-Catalog 1960 Borgward Isabella Coupe	https://www.automobile-catalog.com/car/1960/289295/borgward_isabella_coupe.html
EU-BORGWARD-ISABELLA-SERIES-I-SEDAN-01	4390	1705	1480	Automobile-Catalog 1955 Borgward Isabella TS	https://www.automobile-catalog.com/car/1955/289235/borgward_isabella_ts.html
EU-BORGWARD-ISABELLA-SERIES-II-SEDAN-01	4400	1760	1500	Automobile-Catalog 1959 Borgward Isabella TS de Luxe	https://www.automobile-catalog.com/car/1959/289325/borgward_isabella_ts_de_luxe.html
EU-BRILLIANCE-BS4-BS4-SEDAN-01	4648	1800	1450	Auto-Data Brilliance M2 (JunJie/BS4) generation specifications	https://www.auto-data.net/en/brilliance-m2-junjie-generation-2078
EU-BRILLIANCE-BS6-BS6-SEDAN-01	4880	1800	1450	Autozine 2007 Brilliance BS6 specifications; UltimateSpecs Brilliance BS6 2.4 specifications	https://www.autozine.org/Archive/Brilliance/old/Zhonghua.html;https://www.ultimatespecs.com/car-specs/Brilliance/32909/Brilliance-BS6-24.html
EU-BRISTOL-411-SERIES-IV-V-COUPE-01	4940	1727	1460	Automobile-Catalog Bristol 411 Series IV; Automobile-Catalog Bristol 411 Series V	https://www.automobile-catalog.com/car/1973/78860/bristol_411_series_iv.html;https://www.automobile-catalog.com/car/1975/78875/bristol_411_series_v.html
EU-BUGATTI-CHIRON-CHIRON-COUPE-01	4544	2038	1212	Bugatti Chiron official technical specifications	https://bugatti-newsroom.imgix.net/66703700d9bf8f4b7ce9211c/211122_BU_Chiron%20ENG.pdf
EU-BUGATTI-CHIRON-SUPER-SPORT-COUPE-01	4733	2038	1212	Bugatti Chiron Super Sport official technical specifications; Autocar Bugatti Chiron review	https://bugatti-newsroom.imgix.net/6673edce31d99cf64fc74087/211122_BU_Chiron%20Super%20Sport_ENG.pdf;https://www.autocar.co.uk/car-review/bugatti/chiron
EU-BUGATTI-EB110-GT-COUPE-01	4400	1940	1125	Auto-Data Bugatti EB 110 GT specifications	https://www.auto-data.net/en/bugatti-eb-110-gt-559hp-10857
EU-BUGATTI-EB110-SS-COUPE-01	4400	1960	1125	Auto-Data Bugatti EB 110 SS specifications	https://www.auto-data.net/en/bugatti-eb-110-ss-620hp-10858
EU-BUGATTI-MISTRAL-W16-MISTRAL-CONVERTIBLE-01	4694	2034	1209	Bugatti W16 Mistral official technical specifications	https://bugatti-newsroom.imgix.net/687a1f84e4a10282f1c9db98/technical-specifications-w16-mistral-en.pdf
EU-BUGATTI-VEYRON-VEYRON-COUPE-01	4462	1998	1204	Auto-Data Bugatti Veyron Coupe specifications	https://www.auto-data.net/en/bugatti-veyron-coupe-8.0-w16-1001hp-awd-dsg-10860
EU-BUGATTI-VEYRON-SUPER-SPORT-COUPE-01	4462	1998	1190	Auto-Data Bugatti Veyron Super Sport specifications	https://www.auto-data.net/en/bugatti-veyron-coupe-super-sport-8.0-w16-1200hp-awd-dsg-23277
EU-BUGATTI-VEYRON-GRAND-SPORT-TARGA-01	4462	1998	1204	Auto-Data Bugatti Veyron Grand Sport specifications	https://www.auto-data.net/en/bugatti-veyron-targa-grand-sport-8.0-w16-1001hp-awd-dsg-23586
EU-BUGATTI-VEYRON-GRAND-SPORT-VITESSE-TARGA-01	4462	1998	1190	Auto-Data Bugatti Veyron Grand Sport Vitesse specifications	https://www.auto-data.net/en/bugatti-veyron-targa-grand-sport-vitesse-8.0-w16-1200hp-awd-dsg-23596
EU-BUICK-ENCLAVE-I-SUV-01	5126	2007	1834	Edmunds 2008 Buick Enclave specifications	https://www.edmunds.com/buick/enclave/2008/features-specs/
EU-BUICK-LESABRE-VIII-SEDAN-01	5080	1867	1448	Edmunds 2000 Buick LeSabre specifications; Automobile-Catalog 2000 Buick LeSabre Limited	https://www.edmunds.com/buick/lesabre/2000/features-specs/;https://www.automobile-catalog.com/car/2000/323690/buick_le_sabre_limited.html
EU-BYD-ATTO-2-DM-I-SUV-01	4330	1830	1675	BYD ATTO 2 DM-i official launch specifications	https://media.byd.com/its-not-a-car-its-a-byd-super-hybrid-atto-2-dm-i-arrives-to-redefine-the-compact-suv/
EU-BYD-ATTO-2-EV-SUV-01	4310	1830	1675	BYD ATTO 2 official European launch specifications	https://media.byd.com/byd-introduces-atto-2-compact-suv-in-europe
EU-BYD-ATTO-3-EV-SUV-01	4455	1875	1615	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-ATTO-3-EVO-SUV-01	4455	1875	1615	BYD ATTO 3 EVO official launch specifications	https://media.byd.com/new-byd-atto-3-evo-redefines-electric-family-suvs-with-awd-510km-of-range-and-220kw-charging/?lang=eng
EU-BYD-DOLPHIN-2021-95HP-HATCHBACK-01	4070	1770	1570	Auto-Data BYD Dolphin 44.9 kWh 95 hp specifications	https://www.auto-data.net/en/byd-dolphin-44.9-kwh-95hp-bev-45632
EU-BYD-DOLPHIN-2021-177HP-HATCHBACK-01	4150	1770	1570	Auto-Data BYD Dolphin 44.9 kWh 177 hp specifications	https://www.auto-data.net/en/byd-dolphin-44.9-kwh-177hp-bev-48442
EU-BYD-DOLPHIN-GLOBAL-HATCHBACK-01	4290	1770	1570	Auto-Data BYD Dolphin generation specifications; Automobile Dimension BYD Dolphin dimensions	https://www.auto-data.net/en/byd-dolphin-generation-8817;https://www.automobiledimension.com/model/byd/dolphin
EU-BYD-DOLPHIN-SURF-HATCHBACK-01	3990	1720	1590	BYD DOLPHIN SURF official specifications	https://www.byd.com/material/byd-site/cz/pdfs/BYD_DOLPHIN%20SURF_CZ.pdf
EU-BYD-ETP3-VAN-01	4460	1720	1875	BYD Commercial ETP3 technical data; Automobile Propre BYD ETP3 specifications	https://bydcommercial.gr/en/trucks/etp3/;https://www.automobile-propre.com/voitures/byd-etp3/fiche-technique/
EU-BYD-HAN-EV-SEDAN-01	4995	1910	1495	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-SEAL-5-DM-I-SEDAN-01	4780	1837	1515	BYD SEAL 5 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-5-dm-i-offering-long-range-super-dm-hybrid-tech-and-low-running-costs
EU-BYD-SEAL-U-DM-I-SUV-01	4775	1890	1670	BYD SEAL U DM-i official specifications	https://bydukmedia.com/en/news-articles/byd-presents-seal-u-dm-i-ideal-for-eco-conscious-mobility-and-long-range-journeys.html
EU-BYD-SEAL-EV-SEDAN-01	4800	1875	1460	BYD SEAL official European specifications	https://media.byd.com/byd-seal-arrives-in-europe-setting-the-standard-in-breakthrough-technology-and-stunning-design
EU-BYD-SEAL-U-EV-SUV-01	4785	1890	1668	BYD SEAL U EV official specifications	https://media.byd.com/byd-expands-european-portfolio-with-new-byd-seal-u-practical-spacious-comfortable-family-oriented-and-eco-conscious-electric-suv
EU-BYD-SEAL-DM-I-SEDAN-01	4980	1890	1495	Auto-Data BYD SEAL DM-i specifications; CarNewsChina BYD SEAL DM-i launch specifications	https://www.auto-data.net/en/byd-seal-dm-i-1.5t-17.6-kwh-218hp-plug-in-hybrid-e-cvt-51281;https://carnewschina.com/2023/08/25/byd-seal-dm-i-sedan-starts-pre-sale-for-24300-usd-in-china/
EU-BYD-SEAL-6-DM-I-TOURING-01	4840	1875	1505	BYD SEAL 6 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-6-dm-i-sedan-and-wagon-bringing-the-freedom-of-super-hybrid-technology-415821/
EU-BYD-SEAL-6-DM-I-SEDAN-01	4840	1875	1495	BYD SEAL 6 DM-i official launch specifications	https://media.byd.com/byd-launches-seal-6-dm-i-sedan-and-wagon-bringing-the-freedom-of-super-hybrid-technology-415821/
EU-BYD-SEALION-7-EV-SUV-01	4830	1925	1620	BYD SEALION 7 official European specifications	https://www.byd.com/eu/news-list/byd-introduces-sporty-byd-sealion-7-to-european-market
EU-BYD-SONG-PRO-2025-DM-I-SUV-01	4738	1860	1710	BYD SEALION 5 DM-i official specifications for equivalent Song Pro body	https://media.byd.com/byd-launches-sealion-5-dm-i-the-family-suv-with-super-hybrid-real-world-flexibility
EU-BYD-TANG-2021-EV-SUV-01	4870	1950	1725	BYD European passenger-car range official specifications	https://media.byd.com/byd-lance-une-gamme-innovante-de-voitures-de-tourisme-electriques-sur-de-nouveaux-marches-europeens-384480/
EU-BYD-TANG-2024-EV-SUV-01	4970	1955	1745	BYD TANG 2024 official European specifications	https://media.byd.com/all-new-pure-electric-suv-byd-tang-advances-sustainable-goals-at-uefa-euro-2024tm
EU-CADILLAC-ATS-I-SEDAN-01	4644	1805	1427	Cadillac ATS official technical data	https://media.gm.com/dld/content/media/intl/en/cadillac/vehicles/ats/2015/_jcr_content/rightpar/sectioncontainer_576461190/par/download_991477124/file.res/EN-Cadillac-ATS-TechData.pdf
EU-CADILLAC-ATS-I-COUPE-01	4663	1842	1392	Edmunds 2015 Cadillac ATS Coupe specifications	https://www.edmunds.com/cadillac/ats-coupe/2015/features-specs/
EU-CADILLAC-ATS-V-I-COUPE-01	4691	1842	1384	Edmunds 2016 Cadillac ATS-V Coupe specifications	https://www.edmunds.com/cadillac/ats-v/2016/coupe/features-specs/
EU-CADILLAC-ATS-V-I-SEDAN-01	4674	1811	1415	Edmunds 2016 Cadillac ATS-V Sedan specifications	https://www.edmunds.com/cadillac/ats-v/2016/sedan/features-specs/
EU-CADILLAC-CT6-I-SEDAN-PREFL-01	5184	1880	1472	Cadillac CT6 official technical data	https://media.cadillac.com/content/dam/Media/documents/INTL/cadillac/2018/passenger-cars/ct6/Cadillac-CT6-TechData-en_082017.pdf
EU-CADILLAC-CT6-I-SEDAN-FACELIFT-01	5227	1880	1473	Edmunds 2019 Cadillac CT6 specifications	https://www.edmunds.com/cadillac/ct6/2019/features-specs/
EU-CADILLAC-CTS-I-SEDAN-01	4829	1793	1440	Edmunds 2007 Cadillac CTS Sedan specifications	https://www.edmunds.com/cadillac/cts/2007/sedan/st-100717104/features-specs/
EU-CADILLAC-CTS-II-COUPE-01	4788	1882	1422	Edmunds 2012 Cadillac CTS Coupe specifications	https://www.edmunds.com/cadillac/cts-coupe/2012/features-specs/
EU-CADILLAC-CTS-II-WAGON-01	4877	1842	1473	Edmunds 2012 Cadillac CTS Wagon specifications; Edmunds 2012 Cadillac CTS-V Wagon specifications	https://www.edmunds.com/cadillac/cts-wagon/2012/st-101397084/features-specs/;https://www.edmunds.com/cadillac/cts-v-wagon/2012/st-101397664/features-specs/
EU-CADILLAC-CTS-II-SEDAN-01	4859	1842	1473	Edmunds 2012 Cadillac CTS Sedan specifications	https://www.edmunds.com/cadillac/cts/2012/sedan/features-specs/
EU-CADILLAC-CTS-V-I-SEDAN-01	4864	1793	1455	Edmunds 2005 Cadillac CTS-V specifications	https://www.edmunds.com/cadillac/cts-v/2005/features-specs/
EU-CADILLAC-CTS-III-SEDAN-01	4966	1834	1453	Edmunds 2015 Cadillac CTS specifications	https://www.edmunds.com/cadillac/cts/2015/features-specs/
EU-CADILLAC-CTS-V-III-SEDAN-01	5021	1833	1454	Automobile-Catalog 2016 Cadillac CTS-V specifications	https://www.automobile-catalog.com/car/2016/2094365/cadillac_cts-v.html
EU-CADILLAC-DEVILLE-1977-1984-COUPE-01	5618	1943	1382	Automobile-Catalog 1979 Cadillac Coupe de Ville specifications	https://www.automobile-catalog.com/make/cadillac/de_ville_1977-1984/de_ville_1977-1984_coupe/1979.html
EU-CADILLAC-DEVILLE-1994-1999-SEDAN-01	5329	1943	1422	Edmunds 1998 Cadillac DeVille specifications	https://www.edmunds.com/cadillac/deville/1998/sedan/features-specs/
EU-CADILLAC-DEVILLE-1977-1984-SEDAN-01	5618	1943	1382	Automobile-Catalog 1977 Cadillac Sedan de Ville specifications	https://www.automobile-catalog.com/make/cadillac/de_ville_1977-1984/de_ville_1977-1984_sedan/1977.html
EU-CADILLAC-ELDORADO-X-COUPE-01	5194	1793	1402	Auto-Data Cadillac Eldorado X specifications	https://www.auto-data.net/en/cadillac-eldorado-x-4.1-v8-127hp-automatic-44410
EU-CADILLAC-ELDORADO-XI-COUPE-01	4780	1811	1346	Automobile-Catalog 1987 Cadillac Eldorado specifications	https://www.automobile-catalog.com/make/cadillac/eldorado_1986-1991/eldorado_1986-1991_coupe/1987.html
EU-CADILLAC-ELDORADO-XII-COUPE-PREFL-01	5144	1918	1361	Edmunds 1995 Cadillac Eldorado specifications	https://www.edmunds.com/cadillac/eldorado/1995/features-specs/
EU-CADILLAC-ELDORADO-IX-CONVERTIBLE-01	5692	2027	1380	Carfolio 1975 Cadillac Fleetwood Eldorado Convertible specifications	https://www.carfolio.com/cadillac-fleetwood-eldorado-convertible-518540
EU-CADILLAC-ELDORADO-IX-COUPE-01	5692	2027	1374	Automobile-Catalog 1975 Cadillac Fleetwood Eldorado Coupe specifications	https://www.automobile-catalog.com/make/cadillac/eldorado_1971-1978/eldorado_1971-1978_hardtop/1975.html
EU-CADILLAC-ELDORADO-XII-COUPE-MIDFL-01	5085	1918	1361	Edmunds 1997 Cadillac Eldorado specifications	https://www.edmunds.com/cadillac/eldorado/1997/coupe/st-17749/features-specs/
EU-CADILLAC-ELDORADO-XII-COUPE-LATEFL-01	5095	1918	1361	Edmunds 2002 Cadillac Eldorado specifications	https://www.edmunds.com/cadillac/eldorado/2002/st-19034/features-specs/
EU-CADILLAC-ESCALADE-II-SUV-01	5052	2004	1943	Edmunds 2003 Cadillac Escalade specifications	https://www.edmunds.com/cadillac/escalade/2003/features-specs/
EU-CADILLAC-ESCALADE-I-SUV-01	5110	1956	1887	Edmunds 2000 Cadillac Escalade specifications	https://www.edmunds.com/cadillac/escalade/2000/suv/features-specs/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2901-3000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://bugatti-newsroom.imgix.net/6673edce31d99cf64fc74087/211122_BU_Chiron%20Super%20Sport_ENG.pdf "https://bugatti-newsroom.imgix.net/6673edce31d99cf64fc74087/211122_BU_Chiron%20Super%20Sport_ENG.pdf"
[2]: https://media.gm.com/dld/content/media/intl/en/cadillac/vehicles/ats/2015/_jcr_content/rightpar/sectioncontainer_576461190/par/download_991477124/file.res/EN-Cadillac-ATS-TechData.pdf "https://media.gm.com/dld/content/media/intl/en/cadillac/vehicles/ats/2015/_jcr_content/rightpar/sectioncontainer_576461190/par/download_991477124/file.res/EN-Cadillac-ATS-TechData.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3498 行）
- 累计尺寸组：dimension_groups_final.tsv（942 行）

