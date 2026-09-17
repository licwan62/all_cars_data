# 任务：left18448 第 9801-9900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0099__77f0d4b4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9801-9900 行

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
left18448 第 9801-9900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel/Elektro	Feb 2022	Oct 2023	146698
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel/Elektro	Feb 2022	Oct 2023	147212
Mercedes-benz	E-Klasse	E 220 D	Stufenheck	Heckantrieb	Diesel/Elektro	Jul 2023	-	155289
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel/Elektro	Jul 2023	-	156005
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel	Jan 2017	Oct 2023	125164
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel	Jan 2017	Oct 2023	125165
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel	Oct 2016	Oct 2023	126008
Mercedes-benz	E-Klasse	E 220 D 4-matic	Coupe	Allrad	Diesel	Mar 2017	-	126757
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Feb 2022	Oct 2023	146699
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Feb 2022	Oct 2023	147213
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Feb 2022	Oct 2023	147214
Mercedes-benz	E-Klasse	E 220 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Jul 2023	-	155290
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	156368
Mercedes-benz	E-Klasse	E 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	156369
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	Jun 1998	Jul 1999	10145
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	Mar 2003	Jul 2009	11234
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	Jul 1999	Mar 2003	12642
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	Mar 2003	Jul 2009	17165
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	May 1999	Mar 2003	54935
Mercedes-benz	E-Klasse	E 240	Stufenheck	Heckantrieb	Benzin	Aug 2000	Mar 2002	15062
Mercedes-benz	E-Klasse	E 240	Stufenheck	Heckantrieb	Benzin	Mar 2002	Dec 2008	16593
Mercedes-benz	E-Klasse	E 240	Stufenheck	Heckantrieb	Benzin	May 2005	Dec 2006	802748
Mercedes-benz	E-Klasse	E 240 4-matic	Stufenheck	Allrad	Benzin	Mar 2003	Dec 2008	16958
Mercedes-benz	E-Klasse	E 240 T	Kombi	Heckantrieb	Benzin	Aug 2000	Mar 2003	15064
Mercedes-benz	E-Klasse	E 240 T	Kombi	Heckantrieb	Benzin	Mar 2003	Jul 2009	16956
Mercedes-benz	E-Klasse	E 240 T	Kombi	Heckantrieb	Benzin	Jun 2003	Nov 2004	802749
Mercedes-benz	E-Klasse	E 240 T 4-matic	Kombi	Allrad	Benzin	Jul 2003	Jul 2009	17487
Mercedes-benz	E-Klasse	E 250	Cabriolet	Heckantrieb	Benzin	Jun 2013	Dec 2016	59038
Mercedes-benz	E-Klasse	E 250	Coupe	Heckantrieb	Benzin	Jun 2013	Dec 2016	59046
Mercedes-benz	E-Klasse	E 250	Kombi	Heckantrieb	Benzin	Nov 2012	Dec 2016	59464
Mercedes-benz	E-Klasse	E 250	Kombi	Heckantrieb	Benzin	Jul 2016	Nov 2018	120724
Mercedes-benz	E-Klasse	E 250	Stufenheck	Heckantrieb	Benzin	Jul 2016	Oct 2023	120727
Mercedes-benz	E-Klasse	E 250	Stufenheck	Heckantrieb	Benzin	May 2009	Dec 2011	143996
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec 4-matic	Kombi	Allrad	Diesel	Jul 2010	Dec 2016	12332
Mercedes-benz	E-Klasse	E 250 Turbo D	Kombi	Heckantrieb	Diesel	Jun 1993	Jun 1996	17666
Mercedes-benz	E-Klasse	E 270 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	6028
Mercedes-benz	E-Klasse	E 270 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	12585
Mercedes-benz	E-Klasse	E 270 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2002	Dec 2008	16595
Mercedes-benz	E-Klasse	E 270 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2002	Dec 2008	54937
Mercedes-benz	E-Klasse	E 270 T CDI	Kombi	Heckantrieb	Diesel	Feb 2000	Mar 2003	6027
Mercedes-benz	E-Klasse	E 270 T CDI	Kombi	Heckantrieb	Diesel	Jul 1999	Mar 2003	12590
Mercedes-benz	E-Klasse	E 270 T CDI	Kombi	Heckantrieb	Diesel	Mar 2003	Jul 2009	17166
Mercedes-benz	E-Klasse	E 270 T CDI	Kombi	Heckantrieb	Diesel	Mar 2003	Jul 2009	54949
Mercedes-benz	E-Klasse	E 280	Stufenheck	Heckantrieb	Benzin	Dec 1996	Mar 2002	7832
Mercedes-benz	E-Klasse	E 280	Stufenheck	Heckantrieb	Benzin	Mar 2005	Dec 2008	18630
Mercedes-benz	E-Klasse	E 280 4-matic	Stufenheck	Allrad	Benzin	Dec 1996	Mar 2002	7833
Mercedes-benz	E-Klasse	E 280 CDI	Stufenheck	Heckantrieb	Diesel	May 2004	Dec 2008	18058
Mercedes-benz	E-Klasse	E 280 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2005	Dec 2008	18632
Mercedes-benz	E-Klasse	E 280 CDI 4-matic	Stufenheck	Allrad	Diesel	Mar 2005	Dec 2008	18701
Mercedes-benz	E-Klasse	E 280 T	Kombi	Heckantrieb	Benzin	Mar 2005	Jul 2009	18636
Mercedes-benz	E-Klasse	E 280 T 4-matic	Kombi	Allrad	Benzin	Dec 1996	Mar 2003	7837
Mercedes-benz	E-Klasse	E 280 T 4-matic	Kombi	Allrad	Benzin	Mar 2005	Jul 2009	18885
Mercedes-benz	E-Klasse	E 280 T CDI	Kombi	Heckantrieb	Diesel	May 2004	Jul 2009	18059
Mercedes-benz	E-Klasse	E 280 T CDI	Kombi	Heckantrieb	Diesel	Mar 2005	Jul 2009	18635
Mercedes-benz	E-Klasse	E 280 T CDI 4-matic	Kombi	Allrad	Diesel	Mar 2005	Jul 2009	18702
Mercedes-benz	E-Klasse	E 300	Coupe	Heckantrieb	Benzin	Apr 2011	Jun 2016	10341
Mercedes-benz	E-Klasse	E 300	Cabriolet	Heckantrieb	Benzin	Apr 2011	Dec 2016	10346
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	Jan 2009	Dec 2013	10358
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	Jul 2011	Dec 2015	12333
Mercedes-benz	E-Klasse	E 300	Kombi	Heckantrieb	Benzin	Jul 2011	Dec 2016	12336
Mercedes-benz	E-Klasse	E 300	Kombi	Heckantrieb	Benzin	Nov 2009	Dec 2011	59468
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	Jul 2016	Jun 2020	120730
Mercedes-benz	E-Klasse	E 300	Coupe	Heckantrieb	Benzin	Dec 2016	-	124821
Mercedes-benz	E-Klasse	E 300	Cabriolet	Heckantrieb	Benzin	Jun 2017	-	127636
Mercedes-benz	E-Klasse	E 300 4-matic	Stufenheck	Allrad	Benzin	Jul 2011	Dec 2015	12334
Mercedes-benz	E-Klasse	E 300 4-matic	Kombi	Allrad	Benzin	Jul 2011	Dec 2016	12335
Mercedes-benz	E-Klasse	E 300 CDI	Stufenheck	Heckantrieb	Diesel	Dec 2009	Dec 2010	54914
Mercedes-benz	E-Klasse	E 300 CDI	Kombi	Heckantrieb	Diesel	Dec 2009	Dec 2010	54915
Mercedes-benz	E-Klasse	E 300 CDI / Bluetec	Kombi	Heckantrieb	Diesel	Nov 2009	Dec 2016	56076
Mercedes-benz	E-Klasse	E 300 D 4-matic	Kombi	Allrad	Diesel/Elektro	Jan 2021	Oct 2023	143491
Mercedes-benz	E-Klasse	E 300 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Jan 2021	Oct 2023	143498
Mercedes-benz	E-Klasse	E 300 D 4-matic	Cabriolet	Allrad	Diesel/Elektro	Apr 2021	-	143728
Mercedes-benz	E-Klasse	E 300 D 4-matic	Coupe	Allrad	Diesel/Elektro	Jan 2021	-	143729
Mercedes-benz	E-Klasse	E 300 DE	Kombi	Heckantrieb	Diesel/Elektro	Oct 2023	-	156355
Mercedes-benz	E-Klasse	E 300 DE	Stufenheck	Heckantrieb	Diesel/Elektro	Oct 2023	-	156358
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	156356
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Stufenheck	Allrad	Diesel/Elektro	Oct 2023	-	156357
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	156359
Mercedes-benz	E-Klasse	E 300 E	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2023	-	155291
Mercedes-benz	E-Klasse	E 300 E	Kombi	Heckantrieb	Benzin/Elektro	Jul 2023	-	156036
Mercedes-benz	E-Klasse	E 300 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Jul 2023	-	155292
Mercedes-benz	E-Klasse	E 300 Hybrid / Bluetec Hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Dec 2011	Dec 2016	55905
Mercedes-benz	E-Klasse	E 300 Hybrid / Bluetec Hybrid	Kombi	Heckantrieb	Diesel/Elektro	Dec 2011	Dec 2016	58962
Mercedes-benz	E-Klasse	E 300 T Turbo-d	Kombi	Heckantrieb	Diesel	Dec 1996	Jul 1999	7839
Mercedes-benz	E-Klasse	E 300 Turbo-d	Stufenheck	Heckantrieb	Diesel	Dec 1996	Jul 1999	7835
Mercedes-benz	E-Klasse	E 320	Stufenheck	Heckantrieb	Benzin	Jun 1997	Mar 2002	7834
Mercedes-benz	E-Klasse	E 320	Stufenheck	Heckantrieb	Benzin	Mar 2002	Dec 2008	16564
Mercedes-benz	E-Klasse	E 320	Cabriolet	Heckantrieb	Benzin	Jul 2014	Dec 2016	107499
Mercedes-benz	E-Klasse	E 320	Coupe	Heckantrieb	Benzin	Jul 2014	Dec 2016	107538
Mercedes-benz	E-Klasse	E 320 4-matic	Stufenheck	Allrad	Benzin	Jun 1997	Mar 2002	7841
Mercedes-benz	E-Klasse	E 320 4-matic	Stufenheck	Allrad	Benzin	Mar 2003	Dec 2008	16959
Mercedes-benz	E-Klasse	E 320 CDI	Stufenheck	Heckantrieb	Diesel	Jul 1999	Mar 2002	12587
Mercedes-benz	E-Klasse	E 320 CDI	Stufenheck	Heckantrieb	Diesel	Nov 2002	Dec 2008	17129
Mercedes-benz	E-Klasse	E 320 CDI	Stufenheck	Heckantrieb	Diesel	Mar 2005	Dec 2008	18633
Mercedes-benz	E-Klasse	E 320 T	Kombi	Heckantrieb	Benzin	Dec 1996	Mar 2003	7838
Mercedes-benz	E-Klasse	E 320 T	Kombi	Heckantrieb	Benzin	Mar 2003	Jul 2009	16957
Mercedes-benz	E-Klasse	E 320 T 4-matic	Kombi	Allrad	Benzin	Dec 1996	Mar 2003	7840
Mercedes-benz	E-Klasse	E 320 T 4-matic	Kombi	Allrad	Benzin	Jul 2003	Jul 2009	17488
Mercedes-benz	E-Klasse	E 320 T CDI	Kombi	Heckantrieb	Diesel	Jul 1999	Mar 2003	12588
Mercedes-benz	E-Klasse	E 320 T CDI	Kombi	Heckantrieb	Diesel	Mar 2003	Jul 2009	17167


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 S124、W210、S210 共 **20 个输入 Ktype** 的映射闭合；8 个跨 1999 年改款边界的 Ktype 已拆成 `prefl`、`facelift` 派生行。
* 复用既有 W210 标准轿车和 S210 改款前旅行车尺寸组；新增 S124、W210 4MATIC、W210 改款后汽油/柴油/4MATIC、S210 改款后旅行车尺寸组。
* 官方档案确认 W210 4MATIC 改款前后长度由 4795 mm 变为 4818 mm，高度保持 1451 mm；S210 旅行车改款后长度为 4839 mm。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：20
* READY 映射行：28
* PENDING 输入 Ktype：80
* 本轮映射引用尺寸组：8
* 其中复用既有尺寸组：2
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10145	10145	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	S210改款前旅行车外廓。	READY
12642	12642	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
54935_prefl	54935	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前外廓。	READY
54935_facelift	54935	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后外廓。	READY
15062	15062	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	W210改款后汽油轿车外廓。	READY
17666	17666	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-KLASSE-S124-WAGON-01	HIGH	S124旅行车外廓。	READY
6028	6028	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
12585	12585	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
6027	6027	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
12590	12590	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
7832_prefl	7832	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	1999年7月改款前标准轿车外廓。	READY
7832_facelift	7832	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	1999年7月改款后汽油轿车外廓。	READY
7833_prefl	7833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	HIGH	1999年7月改款前4MATIC外廓。	READY
7833_facelift	7833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH	1999年7月改款后4MATIC外廓。	READY
7837_prefl	7837	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7837_facelift	7837	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
7839	7839	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	S210改款前旅行车外廓。	READY
7835	7835	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	W210改款前柴油轿车外廓。	READY
7834_prefl	7834	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	1999年7月改款前标准轿车外廓。	READY
7834_facelift	7834	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	1999年7月改款后汽油轿车外廓。	READY
7841_prefl	7841	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	HIGH	1999年7月改款前4MATIC外廓。	READY
7841_facelift	7841	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH	1999年7月改款后4MATIC外廓。	READY
12587	12587	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
7838_prefl	7838	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7838_facelift	7838	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
7840_prefl	7840	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7840_facelift	7840	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
12588	12588	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-S124-WAGON-01	4765	1740	1490	Mercedes-Benz Public Archive E 250 Turbodiesel station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-Turbodiesel-station-wagon.xhtml?oid=5453
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	4795	1799	1451	Mercedes-Benz Public Archive E 280 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-4MATIC.xhtml?oid=5311
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	4839	1799	1505	Mercedes-Benz Public Archive E 220 CDI station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-station-wagon.xhtml?oid=5406
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	4818	1799	1440	Mercedes-Benz Public Archive E 240 2.6-litre engine	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240-26-liter-engine.xhtml?oid=5365
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	4818	1799	1441	Mercedes-Benz Public Archive E 270 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-270-CDI.xhtml?oid=5346
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	4818	1799	1451	Mercedes-Benz Public Archive E 320 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-320-4MATIC.xhtml?oid=5366
```

## 下一步优先处理

1. 闭合 W211/S211，并拆分 2006 年改款前后外廓。
2. 批量处理 W212/S212、C207/A207 的 2013 年改款边界。
3. 最后处理 W213/S213、C238/A238、W214/S214，并重点区分标准旅行车与 All-Terrain。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-4MATIC.xhtml?oid=5311&utm_source=chatgpt.com "E 280 4MATIC - Mercedes Benz Archive"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 W211/S211 的 28 个输入 Ktype，新增 36 条 READY 映射。
* 8 个覆盖 2006 年 6 月改款前后且物理外廓变化的 Ktype 已拆分为 `prefl`、`facelift` 派生行。
* 已一次性建立 W211/S211 的 12 个尺寸组；后续相同车身直接复用。奔驰官方档案显示，211 系列改款前后轿车长度由 4818 mm 变为 4856 mm，旅行车由 4850 mm 变为 4888 mm；不同驱动和悬架配置存在高度差异，因此分别建组。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：48
* READY 映射行：64
* PENDING 输入 Ktype：52
* 当前引用尺寸组：20
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11234	11234	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
17165	17165	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
16593	16593	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	HIGH	W211改款前轿车外廓。	READY
802748	802748	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	HIGH	W211改款前轿车外廓。	READY
16958	16958	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	W211改款前4MATIC轿车外廓。	READY
16956	16956	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
802749	802749	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
17487	17487	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	S211改款前4MATIC旅行车外廓。	READY
16595	16595	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
54937	54937	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
17166	17166	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
54949	54949	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
18630_prefl	18630	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18630_facelift	18630	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
18058	18058	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
18632_prefl	18632	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18632_facelift	18632	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	2006年6月改款后外廓。	READY
18701_prefl	18701	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18701_facelift	18701	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
18636_prefl	18636	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	2006年6月改款前外廓。	READY
18636_facelift	18636	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
18885_prefl	18885	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18885_facelift	18885	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
18059	18059	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
18635_prefl	18635	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	2006年6月改款前外廓。	READY
18635_facelift	18635	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
18702_prefl	18702	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18702_facelift	18702	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
16564	16564	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	W211改款前轿车外廓。	READY
16959	16959	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	W211改款前4MATIC轿车外廓。	READY
17129	17129	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
18633_prefl	18633	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18633_facelift	18633	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	2006年6月改款后外廓。	READY
16957	16957	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
17488	17488	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	S211改款前4MATIC旅行车外廓。	READY
17167	17167	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	4850	1822	1496	Mercedes-Benz Public Archive 211 series E-Class Estates 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml?oid=453306
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	4818	1822	1450	Mercedes-Benz Public Archive E 240	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240.xhtml?oid=5372
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	4818	1822	1463	Mercedes-Benz Public Archive E 280 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC.xhtml?oid=2461819
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	4850	1822	1495	Mercedes-Benz Public Archive E 280 CDI station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-station-wagon.xhtml?oid=2461822
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	4850	1822	1499	Automobile-Catalog Mercedes-Benz E 240 4MATIC T-Modell	https://www.automobile-catalog.com/car/2003/1541615/mercedes-benz_e_240_4matic_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	4818	1822	1452	Mercedes-Benz Public Archive 211 series E-Class Estates 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml?oid=453306
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	4818	1822	1449	Mercedes-Benz Public Archive E 280 CDI W 211 2005-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI--W-211-DE-30-LA-LR-2005---2006.xhtml?oid=2461817
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-01	4856	1822	1483	Mercedes-Benz Public Archive E 280	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280.xhtml?oid=2461839
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	4856	1822	1484	Mercedes-Benz Public Archive E 280 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI.xhtml?oid=2461818
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-4MATIC-01	4856	1822	1463	Mercedes-Benz Public Archive E 280 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC.xhtml?oid=2461820
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 280 station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-station-wagon.xhtml?oid=2461885
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	4888	1822	1509	Mercedes-Benz Public Archive E 280 CDI 4MATIC station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC-station-wagon.xhtml?oid=2461878
```

## 下一步优先处理

1. 批量闭合 W212/S212 的轿车和旅行车映射，并处理 2013 年改款边界。
2. 同轮处理 C207 Coupe、A207 Cabriolet，避免将双门车错误复用 W212 尺寸组。
3. 随后处理 W213/S213、C238/A238 及 W214/S214。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml?oid=453306&utm_source=chatgpt.com "211 series E-Class Estates, 2003 - 2006"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 补齐上一轮遗漏的 Ktype `15064`，直接关联已闭合的 S210 改款后旅行车尺寸组。
* 完成 C207 Coupe 与 A207 Cabriolet 聚类；Ktype `10341`、`10346` 按 2013 年改款边界拆分，其余对应改款后外廓。
* 本轮首次创建 4 个尺寸组。官方档案确认 C207/A207 改款前车长为 4698 mm；C207 改款后车长为 4703 mm，宽度保持 1786 mm。A207 改款后尺寸由改款系列档案和规格页交叉闭合。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：55
* READY 映射行：73
* PENDING 输入 Ktype：45
* 当前引用尺寸组：24
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15064	15064	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
59038	59038	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207改款后敞篷车外廓。	READY
59046	59046	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	C207改款后双门轿跑外廓。	READY
10341_prefl	10341	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	2013年4月改款前外廓。	READY
10341_facelift	10341	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	2013年4月改款后外廓。	READY
10346_prefl	10346	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	2013年4月改款前外廓。	READY
10346_facelift	10346	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	2013年4月改款后外廓。	READY
107499	107499	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207改款后敞篷车外廓。	READY
107538	107538	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	C207改款后双门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Mercedes-Benz Public Archive 207 series E-Class Convertibles 2013-2016;Carfolio Mercedes-Benz E 350 BlueTEC Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Convertibles-2013---2016.xhtml?oid=6009649;https://www.carfolio.com/mercedes-benz-e-350-bluetec-cabriolet-336270
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	4703	1786	1397	Mercedes-Benz Public Archive E 350 BlueTEC Coupé 2014-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-BlueTEC-2014---2016-from-092015-Mercedes-Benz-E-350-d.xhtml?oid=189019541
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	4698	1786	1397	Mercedes-Benz Public Archive E 250 CGI BlueEFFICIENCY Coupé 2009-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CGI-BlueEFFICIENCY-2009---2013-from-042011-E-250-BlueEFFICIENCY.xhtml?oid=188954807
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	4698	1786	1398	Mercedes-Benz Public Archive E 250 CGI BlueEFFICIENCY Cabriolet 2010-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CGI-BlueEFFICIENCY-2010---2013-from-042011-E-250-BlueEFFICIENCY.xhtml?oid=188954780
```

## 下一步优先处理

1. 闭合 W212/S212 普通、4MATIC 与混合动力外廓，并处理 2013 年改款前后派生。
2. 批量关联 W213/S213 与 C238/A238 的既有尺寸组，仅补充尚未建档的配置。
3. 最后处理 W214/S214，并消除两个重复旅行车 Ktype 是否属于 X214 All-Terrain 的边界问题。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CGI-BlueEFFICIENCY-2009---2013-from-042011-E-250-BlueEFFICIENCY.xhtml?oid=188954807 "E 250 CGI BlueEFFICIENCY, 2009 - 2013 (from 04.2011: E 250 BlueEFFICIENCY)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 6 个 W212/S212 输入 Ktype，新增 9 条 READY 映射。
* `12332`、`55905`、`58962` 覆盖 2013 年 4 月改款边界，已分别拆成 `prefl` 与 `facelift`。
* S212 改款前的 E 250 CDI 4MATIC 与 E 300 BlueTEC Hybrid 均为 4895 × 1854 × 1515 mm，复用同一尺寸组；对应改款后版本均为 4905 × 1854 × 1507 mm，也复用同一尺寸组。([marsClassic][1])
* W212 E 300 BlueTEC Hybrid 改款前后分别为 4868 × 1854 × 1472 mm 和 4879 × 1854 × 1475 mm，独立建组。([marsClassic][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：61
* READY 映射行：82
* PENDING 输入 Ktype：39
* 当前引用尺寸组：31
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143996	143996	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	HIGH	W212改款前轿车外廓。	READY
12332_prefl	12332	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	2013年4月改款前4MATIC旅行车外廓。	READY
12332_facelift	12332	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	2013年4月改款后4MATIC旅行车外廓。	READY
54914	54914	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E300-CDI-01	HIGH	W212改款前柴油轿车外廓。	READY
54915	54915	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	S212改款前柴油旅行车外廓。	READY
55905_prefl	55905	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	HIGH	2013年4月改款前混合动力轿车外廓。	READY
55905_facelift	55905	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-HYBRID-01	HIGH	2013年4月改款后混合动力轿车外廓。	READY
58962_prefl	58962	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	2013年4月改款前混合动力旅行车外廓。	READY
58962_facelift	58962	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	2013年4月改款后混合动力旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	4868	1854	1470	Auto-Data Mercedes-Benz E-class W212 E 250 CGI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	4895	1854	1515	Mercedes-Benz Public Archive E 250 CDI 4MATIC BlueEFFICIENCY;Auto-Data S212 E 300 BlueTEC Hybrid	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CDI-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188823491;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-300-bluetec-hybrid-204hp-7g-tronic-plus-52822
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	4905	1854	1507	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID Estate;Auto-Data S212 facelift E 250 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2013---2015.xhtml?oid=188823537;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-facelift-2013-e-250-cdi-204hp-4matic-7g-tronic-plus-18747
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E300-CDI-01	4868	1854	1464	Auto-Data Mercedes-Benz E-class W212 E 300 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-300-cdi-blueefficiency-v6-204hp-7g-tronic-52835
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	4895	1854	1512	Auto-Data Mercedes-Benz E-class S212 E 300 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-300-cdi-blueefficiency-v6-204hp-7g-tronic-52818
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	4868	1854	1472	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID 2012-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2012---2013.xhtml?oid=188539262
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-HYBRID-01	4879	1854	1475	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2013---2015.xhtml?oid=188541021
```

## 下一步优先处理

1. 闭合其余 W212/S212 普通汽油、4MATIC 与 BlueTEC 旅行车，并处理改款边界。
2. 批量关联已缓存的 W213/S213 标准轿车、旅行车及改款尺寸组。
3. 最后处理 C238/A238、W214/S214 和 X213/X214 All-Terrain 分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CDI-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188823491&utm_source=chatgpt.com "E 250 CDI 4MATIC BlueEFFICIENCY, 2011 - 2013"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2012---2013.xhtml?oid=188539262&utm_source=chatgpt.com "E 300 BlueTEC HYBRID, 2012 - 2013"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成剩余 8 个 W212/S212 输入 Ktype，新增 14 条 READY 映射。
* `10358`、`12333`、`12334`、`12335`、`12336`、`56076` 按 2013 年改款前后拆分；`59464` 对应 S212 改款后车身，`59468` 对应改款前车身。
* 新建 W212 改款前 4MATIC 轿车与改款后 1474 mm 高轿车两个尺寸组；S212 旅行车均复用已经闭合的 1515 mm、1507 mm 高度尺寸组。官方资料确认 W212 E 300 4MATIC 改款前为 4868 × 1854 × 1474 mm；改款后 E 300 轿车为 4879 × 1854 × 1474 mm。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：69
* READY 映射行：96
* PENDING 输入 Ktype：31
* 当前引用尺寸组：33
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59464	59464	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	S212改款后旅行车外廓。	READY
10358_prefl	10358	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	HIGH	212.054改款前轿车外廓。	READY
10358_facelift	10358	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	212.054改款后轿车外廓。	READY
12333_prefl	12333	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	HIGH	212.055改款前轿车外廓。	READY
12333_facelift	12333	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	212.055改款后轿车外廓。	READY
12336_prefl	12336	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.255改款前旅行车外廓。	READY
12336_facelift	12336	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.255改款后旅行车外廓。	READY
59468	59468	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	S212改款前旅行车外廓。	READY
12334_prefl	12334	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	HIGH	W212改款前4MATIC轿车外廓。	READY
12334_facelift	12334	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	W212改款后4MATIC轿车外廓。	READY
12335_prefl	12335	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.280改款前4MATIC旅行车外廓。	READY
12335_facelift	12335	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.280改款后4MATIC旅行车外廓。	READY
56076_prefl	56076	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.221改款前柴油旅行车外廓。	READY
56076_facelift	56076	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.227改款后柴油旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	4868	1854	1474	Mercedes-Benz Public Archive E 300 4MATIC BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539295
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	4879	1854	1474	Auto-Data Mercedes-Benz E-class W212 facelift E 300 V6	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-300-v6-252hp-7g-tronic-plus-18731
```

## 下一步优先处理

1. 批量闭合 W213/S213 的 2016–2023 年轿车和旅行车，并按 2020 年改款边界拆分。
2. 处理 C238 Coupe、A238 Cabriolet，复用对应既有前后期尺寸组。
3. 最后闭合 W214/S214，并区分标准旅行车和可能的 X214 All-Terrain 重复 Ktype。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539295&utm_source=chatgpt.com "E 300 4MATIC BlueEFFICIENCY, 2011 - 2013"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9801-9900_ktype_dimension_mapping_final.tsv
- left18448_9801-9900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已完成剩余 W213/S213、X213、C238/A238、W214/S214 与 X214 映射，标准旅行车与 All-Terrain 已分离。
* 补齐此前复用但未完整打印的 S210 改款前和 W210 改款前尺寸组；奔驰档案对应尺寸分别为 4816 × 1799 × 1505 mm、4795 × 1799 × 1437 mm。([marsClassic][1])
* 已完成机械检查：两张表列数正确、主键唯一、映射引用全部闭合、尺寸和来源字段均非空、指定下载文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：132
* PENDING：0
* DIMENSION_GROUP：51
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146698	146698	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1460-01	HIGH	S213改款后后驱旅行车外廓。	READY
147212	147212	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1460-01	HIGH	W213改款后后驱轿车外廓。	READY
155289	155289	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-RWD-01	HIGH	W214后驱轿车外廓。	READY
156005	156005	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH	S214标准旅行车外廓。	READY
125164_prefl	125164	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH	2020年改款前标准4MATIC旅行车外廓。	READY
125164_facelift	125164	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1466-01	HIGH	2020年改款后标准4MATIC旅行车外廓。	READY
125165	125165	Wagon	E-Class X213	X213	5	EU-MERCEDES-BENZ-E-KLASSE-X213-ALL-TERRAIN-01	HIGH	X213 All-Terrain旅行车外廓。	READY
126008_prefl	126008	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH	2020年改款前4MATIC轿车外廓。	READY
126008_facelift	126008	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1466-01	HIGH	2020年改款后4MATIC轿车外廓。	READY
126757_prefl	126757	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	HIGH	2020年改款前双门轿跑外廓。	READY
126757_facelift	126757	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	2020年改款后双门轿跑外廓。	READY
146699	146699	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1466-01	HIGH	S213改款后标准4MATIC旅行车外廓。	READY
147213	147213	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1466-01	HIGH	W213改款后4MATIC轿车外廓。	READY
147214	147214	Wagon	E-Class X213	X213	5	EU-MERCEDES-BENZ-E-KLASSE-X213-ALL-TERRAIN-01	HIGH	X213 All-Terrain改款后旅行车外廓。	READY
155290	155290	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	HIGH	W214 4MATIC轿车外廓。	READY
156368	156368	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH	S214标准4MATIC旅行车外廓。	READY
156369	156369	Wagon	E-Class X214	X214	5	EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-DIESEL-01	HIGH	X214 All-Terrain柴油旅行车外廓。	READY
10145	10145	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	S210改款前旅行车外廓。	READY
11234	11234	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
12642	12642	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
17165	17165	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
54935_prefl	54935	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前外廓。	READY
54935_facelift	54935	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后外廓。	READY
15062	15062	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	W210改款后汽油轿车外廓。	READY
16593	16593	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	HIGH	W211改款前轿车外廓。	READY
802748	802748	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	HIGH	W211改款前轿车外廓。	READY
16958	16958	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	W211改款前4MATIC轿车外廓。	READY
15064	15064	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
16956	16956	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
802749	802749	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
17487	17487	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	S211改款前4MATIC旅行车外廓。	READY
59038	59038	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207改款后敞篷车外廓。	READY
59046	59046	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	C207改款后双门轿跑外廓。	READY
59464	59464	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	S212改款后旅行车外廓。	READY
120724	120724	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH	S213改款前标准旅行车外廓。	READY
120727	120727	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH	W213改款前轿车外廓。	READY
143996	143996	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	HIGH	W212改款前轿车外廓。	READY
12332_prefl	12332	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	2013年4月改款前4MATIC旅行车外廓。	READY
12332_facelift	12332	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	2013年4月改款后4MATIC旅行车外廓。	READY
17666	17666	Wagon	E-Class S124	S124	5	EU-MERCEDES-BENZ-E-KLASSE-S124-WAGON-01	HIGH	S124旅行车外廓。	READY
6028	6028	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
12585	12585	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
16595	16595	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
54937	54937	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
6027	6027	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
12590	12590	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
17166	17166	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
54949	54949	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	S211改款前旅行车外廓。	READY
7832_prefl	7832	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	1999年7月改款前标准轿车外廓。	READY
7832_facelift	7832	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	1999年7月改款后汽油轿车外廓。	READY
18630_prefl	18630	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18630_facelift	18630	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
7833_prefl	7833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	HIGH	1999年7月改款前4MATIC外廓。	READY
7833_facelift	7833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH	1999年7月改款后4MATIC外廓。	READY
18058	18058	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
18632_prefl	18632	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18632_facelift	18632	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	2006年6月改款后外廓。	READY
18701_prefl	18701	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18701_facelift	18701	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
18636_prefl	18636	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	2006年6月改款前外廓。	READY
18636_facelift	18636	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
7837_prefl	7837	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7837_facelift	7837	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
18885_prefl	18885	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18885_facelift	18885	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
18059	18059	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
18635_prefl	18635	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	2006年6月改款前外廓。	READY
18635_facelift	18635	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	2006年6月改款后外廓。	READY
18702_prefl	18702	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	2006年6月改款前4MATIC外廓。	READY
18702_facelift	18702	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	HIGH	2006年6月改款后4MATIC外廓。	READY
10341_prefl	10341	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	2013年4月改款前外廓。	READY
10341_facelift	10341	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	2013年4月改款后外廓。	READY
10346_prefl	10346	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	2013年4月改款前外廓。	READY
10346_facelift	10346	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	2013年4月改款后外廓。	READY
10358_prefl	10358	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	HIGH	212.054改款前轿车外廓。	READY
10358_facelift	10358	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	212.054改款后轿车外廓。	READY
12333_prefl	12333	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	HIGH	212.055改款前轿车外廓。	READY
12333_facelift	12333	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	212.055改款后轿车外廓。	READY
12336_prefl	12336	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.255改款前旅行车外廓。	READY
12336_facelift	12336	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.255改款后旅行车外廓。	READY
59468	59468	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	S212改款前旅行车外廓。	READY
120730	120730	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH	W213改款前轿车外廓。	READY
124821_prefl	124821	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	HIGH	2020年改款前双门轿跑外廓。	READY
124821_facelift	124821	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	2020年改款后双门轿跑外廓。	READY
127636_prefl	127636	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	HIGH	2020年改款前敞篷车外廓。	READY
127636_facelift	127636	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	2020年改款后敞篷车外廓。	READY
12334_prefl	12334	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	HIGH	W212改款前4MATIC轿车外廓。	READY
12334_facelift	12334	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	W212改款后4MATIC轿车外廓。	READY
12335_prefl	12335	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.280改款前4MATIC旅行车外廓。	READY
12335_facelift	12335	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.280改款后4MATIC旅行车外廓。	READY
54914	54914	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E300-CDI-01	HIGH	W212改款前柴油轿车外廓。	READY
54915	54915	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	S212改款前柴油旅行车外廓。	READY
56076_prefl	56076	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	212.221改款前柴油旅行车外廓。	READY
56076_facelift	56076	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	212.227改款后柴油旅行车外廓。	READY
143491	143491	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1460-01	HIGH	S213改款后4MATIC柴油旅行车外廓。	READY
143498	143498	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1460-01	HIGH	W213改款后4MATIC柴油轿车外廓。	READY
143728	143728	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款后敞篷车外廓。	READY
143729	143729	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	HIGH	C238改款后双门轿跑外廓。	READY
156355	156355	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH	S214后驱插电混动旅行车外廓。	READY
156358	156358	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH	W214后驱插电混动轿车外廓。	READY
156356	156356	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH	S214标准4MATIC插电混动旅行车外廓。	READY
156357	156357	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH	W214 4MATIC插电混动轿车外廓。	READY
156359	156359	Wagon	E-Class X214	X214	5	EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-PHEV-01	HIGH	X214 All-Terrain插电混动旅行车外廓。	READY
155291	155291	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH	W214后驱插电混动轿车外廓。	READY
156036	156036	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH	S214后驱插电混动旅行车外廓。	READY
155292	155292	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH	W214 4MATIC插电混动轿车外廓。	READY
55905_prefl	55905	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	HIGH	2013年4月改款前混合动力轿车外廓。	READY
55905_facelift	55905	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-HYBRID-01	HIGH	2013年4月改款后混合动力轿车外廓。	READY
58962_prefl	58962	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	2013年4月改款前混合动力旅行车外廓。	READY
58962_facelift	58962	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	2013年4月改款后混合动力旅行车外廓。	READY
7839	7839	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	S210改款前旅行车外廓。	READY
7835	7835	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	W210改款前柴油轿车外廓。	READY
7834_prefl	7834	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	HIGH	1999年7月改款前标准轿车外廓。	READY
7834_facelift	7834	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	HIGH	1999年7月改款后汽油轿车外廓。	READY
16564	16564	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	W211改款前轿车外廓。	READY
107499	107499	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	A207改款后敞篷车外廓。	READY
107538	107538	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	C207改款后双门轿跑外廓。	READY
7841_prefl	7841	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	HIGH	1999年7月改款前4MATIC外廓。	READY
7841_facelift	7841	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH	1999年7月改款后4MATIC外廓。	READY
16959	16959	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	HIGH	W211改款前4MATIC轿车外廓。	READY
12587	12587	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	HIGH	W210改款后柴油轿车外廓。	READY
17129	17129	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	HIGH	W211改款前轿车外廓。	READY
18633_prefl	18633	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	2006年6月改款前外廓。	READY
18633_facelift	18633	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	2006年6月改款后外廓。	READY
7838_prefl	7838	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7838_facelift	7838	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
16957	16957	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
7840_prefl	7840	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	HIGH	1999年7月改款前旅行车外廓。	READY
7840_facelift	7840	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	1999年7月改款后旅行车外廓。	READY
17488	17488	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	HIGH	S211改款前4MATIC旅行车外廓。	READY
12588	12588	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH	S210改款后旅行车外廓。	READY
17167	17167	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	S211改款前旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_9801-9900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1460-01	4945	1852	1460	Auto-Data Mercedes-Benz E-class T-modell S213 facelift E 220d EQ Boost	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-200hp-eq-boost-9g-tronic-53993
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1460-01	4935	1852	1460	Auto-Data Mercedes-Benz E-class W213 facelift E 220d EQ Boost	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-220d-200hp-eq-boost-9g-tronic-53996
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-RWD-01	4949	1880	1468	Auto-Data Mercedes-Benz E-class W214 E 220d	https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-220d-197hp-mild-hybrid-9g-tronic-48453
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	4949	1880	1469	Auto-Data Mercedes-Benz E-class T-modell S214 E 220d;Auto-Data Mercedes-Benz E-class T-modell S214 E 300de 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-220d-197hp-mild-hybrid-9g-tronic-48917;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-300de-313hp-plug-in-hybrid-4matic-9g-tronic-50070
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E-class T-modell S213 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-220d-194hp-4matic-9g-tronic-30787
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1466-01	4945	1852	1466	Auto-Data Mercedes-Benz E-class T-modell S213 facelift E 220d EQ Boost 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-220d-200hp-eq-boost-4matic-9g-tronic-53994
EU-MERCEDES-BENZ-E-KLASSE-X213-ALL-TERRAIN-01	4947	1861	1497	Auto-Data Mercedes-Benz E-class All-Terrain S213 E 220d 4MATIC;Auto-Data Mercedes-Benz E-class All-Terrain S213 facelift E 220d EQ Boost 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-all-terrain-s213-e-220d-194hp-4matic-9g-tronic-27186;https://www.auto-data.net/en/mercedes-benz-e-class-all-terrain-s213-facelift-2020-e-220d-200hp-eq-boost-4matic-9g-tronic-53995
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-class W213 E 250	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-250-211hp-9g-tronic-29565
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1466-01	4935	1852	1466	Auto-Data Mercedes-Benz E-class W213 facelift E 220d EQ Boost 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-220d-200hp-eq-boost-4matic-9g-tronic-53997
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	4826	1860	1430	Auto-Data Mercedes-Benz E-class Coupe C238 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E-class Coupe C238 facelift E 300d EQ Boost 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43738
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	4949	1880	1469	Auto-Data Mercedes-Benz E-class W214 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-220d-197hp-mild-hybrid-4matic-9g-tronic-48454
EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-DIESEL-01	4950	1889	1497	Auto-Data Mercedes-Benz E-class All-Terrain S214 E 220d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-all-terrain-s214-e-220d-197hp-mild-hybrid-4matic-9g-tronic-50056
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505	Mercedes-Benz Public Archive E 220 CDI station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-station-wagon.xhtml?oid=5421
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	4850	1822	1496	Mercedes-Benz Public Archive 211 series E-Class Estates 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml?oid=453306
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	4839	1799	1505	Mercedes-Benz Public Archive E 220 CDI station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-220-CDI-station-wagon.xhtml?oid=5406
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	4818	1799	1440	Mercedes-Benz Public Archive E 240 2.6-litre engine	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240-26-liter-engine.xhtml?oid=5365
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	4818	1822	1450	Mercedes-Benz Public Archive E 240	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-240.xhtml?oid=5372
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	4818	1822	1463	Mercedes-Benz Public Archive E 280 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC.xhtml?oid=2461819
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	4850	1822	1495	Mercedes-Benz Public Archive E 280 CDI station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-station-wagon.xhtml?oid=2461822
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	4850	1822	1499	Automobile-Catalog Mercedes-Benz E 240 4MATIC T-Modell	https://www.automobile-catalog.com/car/2003/1541615/mercedes-benz_e_240_4matic_t-modell.html
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Mercedes-Benz Public Archive 207 series E-Class Convertibles 2013-2016;Carfolio Mercedes-Benz E 350 BlueTEC Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Convertibles-2013---2016.xhtml?oid=6009649;https://www.carfolio.com/mercedes-benz-e-350-bluetec-cabriolet-336270
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	4703	1786	1397	Mercedes-Benz Public Archive E 350 BlueTEC Coupé 2014-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-BlueTEC-2014---2016-from-092015-Mercedes-Benz-E-350-d.xhtml?oid=189019541
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	4905	1854	1507	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID Estate;Auto-Data S212 facelift E 250 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2013---2015.xhtml?oid=188823537;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-facelift-2013-e-250-cdi-204hp-4matic-9g-tronic-plus-18747
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	4868	1854	1470	Auto-Data Mercedes-Benz E-class W212 E 250 CGI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	4895	1854	1515	Mercedes-Benz Public Archive E 250 CDI 4MATIC BlueEFFICIENCY;Auto-Data S212 E 300 BlueTEC Hybrid	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CDI-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188823491;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-300-bluetec-hybrid-204hp-7g-tronic-plus-52822
EU-MERCEDES-BENZ-E-KLASSE-S124-WAGON-01	4765	1740	1490	Mercedes-Benz Public Archive E 250 Turbodiesel station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-Turbodiesel-station-wagon.xhtml?oid=5453
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	4818	1799	1441	Mercedes-Benz Public Archive E 270 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-270-CDI.xhtml?oid=5346
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	4818	1822	1452	Mercedes-Benz Public Archive 211 series E-Class Estates 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml?oid=453306
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1437	Mercedes-Benz Public Archive E 300 Turbodiesel	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-Turbodiesel.xhtml?oid=5323
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	4818	1822	1449	Mercedes-Benz Public Archive E 280 CDI W 211 2005-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI--W-211-DE-30-LA-LR-2005---2006.xhtml?oid=2461817
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-01	4856	1822	1483	Mercedes-Benz Public Archive E 280	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280.xhtml?oid=2461839
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	4795	1799	1451	Mercedes-Benz Public Archive E 280 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-4MATIC.xhtml?oid=5311
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	4818	1799	1451	Mercedes-Benz Public Archive E 320 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-320-4MATIC.xhtml?oid=5366
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	4856	1822	1484	Mercedes-Benz Public Archive E 280 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI.xhtml?oid=2461818
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-4MATIC-01	4856	1822	1463	Mercedes-Benz Public Archive E 280 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC.xhtml?oid=2461820
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive E 280 station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-station-wagon.xhtml?oid=2461885
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	4888	1822	1509	Mercedes-Benz Public Archive E 280 CDI 4MATIC station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-280-CDI-4MATIC-station-wagon.xhtml?oid=2461878
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	4698	1786	1397	Mercedes-Benz Public Archive E 250 CGI BlueEFFICIENCY Coupé 2009-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CGI-BlueEFFICIENCY-2009---2013-from-042011-E-250-BlueEFFICIENCY.xhtml?oid=188954807
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	4698	1786	1398	Mercedes-Benz Public Archive E 250 CGI BlueEFFICIENCY Cabriolet 2010-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CGI-BlueEFFICIENCY-2010---2013-from-042011-E-250-BlueEFFICIENCY.xhtml?oid=188954780
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	4879	1854	1474	Auto-Data Mercedes-Benz E-class W212 facelift E 300 V6	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-300-v6-252hp-7g-tronic-plus-18731
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	4868	1854	1472	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID 2012-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2012---2013.xhtml?oid=188539262
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	4826	1860	1428	Auto-Data Mercedes-Benz E-class Cabrio A238 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300-245hp-9g-tronic-29749
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data Mercedes-Benz E-class Cabrio A238 facelift E 300d EQ Boost 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43739
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	4868	1854	1474	Mercedes-Benz Public Archive E 300 4MATIC BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539295
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E300-CDI-01	4868	1854	1464	Auto-Data Mercedes-Benz E-class W212 E 300 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-300-cdi-blueefficiency-v6-204hp-7g-tronic-52835
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	4895	1854	1512	Auto-Data Mercedes-Benz E-class S212 E 300 CDI BlueEFFICIENCY	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s212-e-300-cdi-blueefficiency-v6-204hp-7g-tronic-52818
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	4949	1880	1470	Auto-Data Mercedes-Benz E-class T-modell S214 E 300e;Auto-Data Mercedes-Benz E-class T-modell S214 E 300de	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-300e-313hp-plug-in-hybrid-9g-tronic-48919;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s214-e-300de-313hp-plug-in-hybrid-9g-tronic-50071
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	4949	1880	1480	Auto-Data Mercedes-Benz E-class W214 E 300e;Auto-Data Mercedes-Benz E-class W214 E 300de 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-300e-313hp-plug-in-hybrid-9g-tronic-48462;https://www.auto-data.net/en/mercedes-benz-e-class-w214-e-300de-313hp-plug-in-hybrid-4matic-9g-tronic-50066
EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-PHEV-01	4950	1889	1489	Auto-Data Mercedes-Benz E-class All-Terrain S214 E 300de 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-all-terrain-s214-e-300de-313hp-plug-in-hybrid-4matic-9g-tronic-50057
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-HYBRID-01	4879	1854	1475	Mercedes-Benz Public Archive E 300 BlueTEC HYBRID 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-BlueTEC-HYBRID-2013---2015.xhtml?oid=188541021
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_9801-9900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-Turbodiesel.xhtml?oid=5323 "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-300-Turbodiesel.xhtml?oid=5323"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（625 行）
- 累计尺寸组：dimension_groups_final.tsv（172 行）

