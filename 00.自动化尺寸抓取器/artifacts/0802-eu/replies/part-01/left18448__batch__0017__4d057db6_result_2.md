# 任务：left18448 第 1601-1700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0017__4d057db6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1601-1700 行

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
left18448 第 1601-1700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-FACELIFT-01	5290	1916	1475
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-PREFL-01	5307	1916	1479
EU-BENTLEY-CONTINENTAL-GTC-I-CONVERTIBLE-01	4804	1916	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GTC-II-SPEED-CONVERTIBLE-01	4806	1943	1393
EU-BENTLEY-CONTINENTAL-GTC-I-SPEED-CONVERTIBLE-01	4804	1916	1388
EU-BENTLEY-CONTINENTAL-GTC-I-SUPERSPORTS-ISR-01	4804	1916	1388
EU-BENTLEY-CONTINENTAL-GT-I-COUPE-01	4804	1916	1390
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1944	1404

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Bentley	Continental	6.0 Speed	Stufenheck	Allrad	Benzin	Sep 2008	Dec 2010	106066
Bentley	Continental	6.0 Supersports	Coupe	Allrad	Benzin	Oct 2009	Dec 2011	34873
Bentley	Continental	6.0 W12 AWD	Coupe	Allrad	Benzin	Sep 2017	-	128569
Bentley	Continental	6.0 W12 AWD	Coupe	Allrad	Benzin	Jun 2021	-	144433
Bentley	Continental	6.75 V8 R	Coupe	Heckantrieb	Benzin	Oct 1991	Aug 1999	16853
Bentley	Continental	6.75 V8 R	Coupe	Heckantrieb	Benzin	Aug 1999	Oct 2002	16856
Bentley	Continental	6.75 V8 S	Coupe	Heckantrieb	Benzin	May 1994	Dec 1995	16854
Bentley	Continental	6.75 V8 T Mulliner	Coupe	Heckantrieb	Benzin	Aug 1999	Oct 2002	16855
Bentley	Continental	GT Phev	Cabriolet	Allrad	Benzin/Elektro	Jul 2024	-	160823
Bentley	Continental	Phev	Coupe	Allrad	Benzin/Elektro	Nov 2024	-	160310
Bentley	Continental	Phev	Coupe	Allrad	Benzin/Elektro	Jul 2024	-	800960
Bentley	Continental	Phev	Cabriolet	Allrad	Benzin/Elektro	Jul 2024	-	800961
Bentley	Flying spur	2.9 Tfsi Phev	Stufenheck	Allrad	Benzin/Elektro	Nov 2021	-	146534
Bentley	Flying spur	4.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	Mar 2013	-	105576
Bentley	Flying spur	V8 Phev	Stufenheck	Allrad	Benzin/Elektro	Oct 2024	-	800959
Bentley	Flying spur	V8 Phev	Stufenheck	Allrad	Benzin/Elektro	Sep 2025	-	802249
Bentley	Mulsanne	6.8	Stufenheck	Heckantrieb	Benzin	Sep 2009	Jul 2020	34838
Bentley	Mulsanne	6.75 Turbo	Stufenheck	Heckantrieb	Benzin	Sep 1981	Dec 1985	108189
Bentley	T1 series	6.8	Stufenheck	Heckantrieb	Benzin	Sep 1974	Dec 1976	35592
Bentley	Turbo r	6.7	Stufenheck	Heckantrieb	Benzin	Jun 1995	Feb 1998	12627
Bentley	Turbo r	6.7 S	Stufenheck	Heckantrieb	Benzin	Jan 1994	Dec 1995	100707
Bertone	Freeclimber	1.6	Geländewagen geschlossen	Allrad	Benzin	Mar 1992	Dec 1999	12589
Bertone	Freeclimber	2	Geländewagen geschlossen	Allrad	Benzin	Dec 1990	Dec 1993	12581
Bertone	Freeclimber	2.7	Geländewagen geschlossen	Allrad	Benzin	Jun 1989	Dec 1993	12584
Bertone	Freeclimber	2.0 CAT	Geländewagen geschlossen	Allrad	Benzin	Dec 1990	Dec 1993	12582
Bertone	Freeclimber	2.4 TD	Geländewagen geschlossen	Allrad	Diesel	Jun 1989	Dec 1993	12586
Bestune	B70	1.5	Schrägheck	Frontantrieb	Benzin	Jan 2025	-	802622
Bestune	B70	2	Schrägheck	Frontantrieb	Benzin	Jan 2025	-	802623
Bestune	Joyee 07	1.5 Phev	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	162924
Bestune	T77	1.5	SUV	Frontantrieb	Benzin	Jan 2025	-	802626
Bestune	T90	1.5	SUV	Frontantrieb	Benzin	Jan 2025	-	802624
Bestune	T90	2	SUV	Frontantrieb	Benzin	Jan 2025	-	802625
Bitter	Type 3	3.0 I	Cabriolet	Heckantrieb	Benzin	Jan 1991	Jun 1992	12597
Bitter	Type 3	3.0 I	Cabriolet	Heckantrieb	Benzin	Mar 1987	Dec 1990	127261
Bitter	Type 3	4.0 I	Cabriolet	Heckantrieb	Benzin	Jan 1991	Jun 1992	12598
BMC	Megastar	CRI	Bus	Heckantrieb	Diesel	Jan 2004	Dec 2010	156011
BMC	Megastar	CRI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2004	Dec 2010	156012
BMC	Megastar	CRI	Kasten	Heckantrieb	Diesel	Jan 2004	Dec 2010	156013
BMC	Megastar	CRI	Kasten	Heckantrieb	Diesel	Jan 2004	Dec 2010	156014
BMC	Megastar	CRI	Bus	Heckantrieb	Diesel	Jan 2004	Dec 2010	156015
BMC	Megastar	CRI	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 2004	Dec 2010	156016
BMW	1	116	Schrägheck	Frontantrieb	Benzin	Nov 2024	-	800017
BMW	1	114 D	Schrägheck	Heckantrieb	Diesel	Nov 2012	Jun 2015	57464
BMW	1	114 D	Schrägheck	Heckantrieb	Diesel	Jul 2012	May 2019	58360
BMW	1	114 D	Schrägheck	Heckantrieb	Diesel	Jun 2015	May 2019	115277
BMW	1	114 D	Schrägheck	Heckantrieb	Diesel	Jul 2015	Jun 2019	115279
BMW	1	114 I	Schrägheck	Heckantrieb	Benzin	Jul 2012	Feb 2015	55488
BMW	1	114 I	Schrägheck	Heckantrieb	Benzin	Jul 2012	Jan 2015	58336
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Jul 2011	Feb 2015	10313
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Mar 2009	Jun 2011	58252
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Dec 2011	Feb 2015	58364
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Jul 2012	Feb 2015	58365
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Jan 2011	Dec 2011	58963
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Jan 2011	Dec 2011	58964
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	May 2019	110048
BMW	1	116 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110072
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Jul 2011	Feb 2015	10311
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Sep 2007	Dec 2011	17928
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Jun 2004	Jun 2011	58168
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Sep 2007	Jun 2011	58169
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Jan 2009	Jun 2011	58184
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Dec 2011	Feb 2015	58344
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2019	110042
BMW	1	116 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2019	110060
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Jul 2011	Jun 2019	5671
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Jul 2011	Feb 2015	10314
BMW	1	118 D	Coupe	Heckantrieb	Diesel	Sep 2009	Oct 2013	12272
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Jun 2004	Feb 2007	58253
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Jun 2011	58254
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Jun 2011	58256
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Dec 2011	Jun 2019	58368
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Dec 2011	Feb 2015	58369
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110049
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	Mar 2015	Jun 2019	110073
BMW	1	118 D	Schrägheck	Frontantrieb	Diesel	Jul 2024	-	800019
BMW	1	118 D Xdrive	Schrägheck	Allrad	Diesel	May 2013	Feb 2015	52331
BMW	1	118 D Xdrive	Schrägheck	Allrad	Diesel	Jul 2013	Feb 2015	100886
BMW	1	118 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	May 2019	110050
BMW	1	118 D Xdrive	Schrägheck	Allrad	Diesel	Mar 2015	Jun 2019	110074
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Jul 2011	Feb 2015	10312
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Sep 2006	Dec 2011	55945
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Jul 2004	Feb 2007	58185
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Oct 2006	Jun 2011	58186
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Sep 2006	Jun 2011	58187
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Jul 2012	Jun 2019	58355
BMW	1	118 I	Cabriolet	Heckantrieb	Benzin	Sep 2008	Dec 2013	59274
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2019	110043
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2015	110061
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Jul 2015	Jun 2019	115121
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Mar 2015	Jun 2019	115122
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	Sep 2006	Feb 2008	126495
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jul 2011	Feb 2015	10316
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Dec 2011	17931
BMW	1	120 D	Cabriolet	Heckantrieb	Diesel	Mar 2008	Dec 2013	55647
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jun 2004	Jun 2011	58283
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Mar 2007	Jun 2011	58303
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jul 2012	Jun 2019	58371
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jul 2012	Feb 2015	58373
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jul 2011	Feb 2015	100891
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	Jan 2012	Feb 2015	100893


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理外廓完成 21 个 Ktype 映射，优先闭合了 Bentley 新旧 Continental/Flying Spur、Bertone Freeclimber II、Bestune、Bitter Type 3 前期型及 BMW 1 Series F70。
* Bentley 第四代 Continental、第三代及改款 Flying Spur 已按车身宽度（不含后视镜）分别建组；未将发动机或混动系统差异作为额外拆组依据。([汽车目录][1])
* Bestune B70、T77、T90 和 Joyee/Yueyi 07 已完成同外廓发动机版本合并。([Bestune Qatar][2])
* Bitter Type 3 暂仅闭合有完整原厂资料支持的 1987–1990 前期型；1991 年改款车型继续保留核验。([Car Back Catalogue][3])
* BMW 116 F70 已依据 BMW 官方技术规格闭合五门外廓。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：21
* PENDING 映射：79
* 当前已引用且闭合的尺寸组：15
* 本轮首次创建尺寸组：14
* 复用跨批次已有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106066	106066	Sedan	Continental Flying Spur I Facelift	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-FACELIFT-01	HIGH	Speed版本属于第一代Flying Spur改款四门外廓。	READY
34873	34873	Coupe	Continental GT I	3W	2	EU-BENTLEY-CONTINENTAL-GT-I-SUPERSPORTS-COUPE-01	HIGH	Supersports宽体双门外廓。	READY
128569	128569	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代GT双门外廓。	READY
144433	144433	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代GT双门外廓。	READY
160823	160823	Convertible	Continental GTC IV		2	EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	HIGH	第四代混动敞篷外廓。	READY
160310	160310	Coupe	Continental GT IV		2	EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	HIGH	第四代混动双门外廓。	READY
800960	800960	Coupe	Continental GT IV		2	EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	HIGH	第四代混动双门外廓。	READY
800961	800961	Convertible	Continental GTC IV		2	EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	HIGH	第四代混动敞篷外廓。	READY
146534	146534	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代Flying Spur四门外廓。	READY
105576	105576	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	MEDIUM	4.0 Flex按第二代Flying Spur四门外廓归组。	READY
800959	800959	Sedan	Flying Spur III Facelift		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	HIGH	2024改款混动四门外廓。	READY
802249	802249	Sedan	Flying Spur III Facelift		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	HIGH	2024改款混动四门外廓。	READY
12589	12589	SUV	Freeclimber II		3	EU-BERTONE-FREECLIMBER-II-SUV-3D-01	HIGH	Freeclimber II三门外廓。	READY
802622	802622	Hatchback	B70 III Facelift		5	EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	HIGH	第三代改款五门掀背外廓。	READY
802623	802623	Hatchback	B70 III Facelift		5	EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	HIGH	第三代改款五门掀背外廓。	READY
162924	162924	SUV	Joyee 07 I		5	EU-BESTUNE-YUEYI-07-I-SUV-01	MEDIUM	Joyee 07按Yueyi 07出口车型边界归组。	READY
802626	802626	SUV	T77 I Facelift		5	EU-BESTUNE-T77-I-SUV-FACELIFT-01	HIGH	第一代改款五门SUV外廓。	READY
802624	802624	SUV	T90 I		5	EU-BESTUNE-T90-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
802625	802625	SUV	T90 I		5	EU-BESTUNE-T90-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
127261	127261	Convertible	Type 3 Pre-Facelift		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	MEDIUM	1987至1990年前改款双门敞篷外廓。	READY
800017	800017	Hatchback	1 Series F70	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门前驱外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-GT-I-SUPERSPORTS-COUPE-01	4804	1945	1380	Bentley Heritage Collection; carsales	https://www.bentleymedia.com/en/heritage-collection/2011-continental-supersports-dk12fzm;https://www.carsales.com.au/research/bentley/continental/2009/supersports/
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	4850	1954	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2606630/bentley_continental_gt.html
EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	4895	1966	1392	Bentley Motors; Edmunds	https://www.bentleymotors.com/en/models/continental-gtc/continental-gtc.html;https://www.edmunds.com/bentley/continental/2025/st-402064474/features-specs/
EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	4895	1966	1397	Bentley Motors; Automobile-Catalog	https://www.bentleymotors.com/en/models/continental-gt/continental-gt.html;https://www.automobile-catalog.com/car/2025/3342005/bentley_continental_gt_speed.html
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1978	1483	Bentley Flying Spur official brochure	https://cdn.bentleymotors.com/downloads/en/brochure/global/flying-spur/BEN-FS-21-017_FlyingSpurMullinerCustomerBookUpdate_EN_v17_AW%28Digital%29_clean.pdf
EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	5295	1976	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/1830305/bentley_flying_spur.html
EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	5316	1988	1474	Bentley Media technical specifications	https://www.bentleymedia.com/attachment/7b743a18-74d8-4a2b-89c6-5eee8377392f
EU-BERTONE-FREECLIMBER-II-SUV-3D-01	3785	1740	1720	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Bertone/18094/Bertone-Freeclimber-16-Si.html
EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	4810	1840	1455	BESTUNE Russia official specification	https://bestune.ru/B70_Price_01_11_2025_6557653825203732106.pdf
EU-BESTUNE-YUEYI-07-I-SUV-01	4745	1880	1710	Auto-Data	https://www.auto-data.net/en/bestune-yueyi-07-generation-10854
EU-BESTUNE-T77-I-SUV-FACELIFT-01	4525	1845	1615	Bestune Qatar official specification	https://www.bestune-qatar.com/en/car/t77
EU-BESTUNE-T90-I-SUV-01	4718	1880	1710	BESTUNE Russia official specification	https://bestune.ru/models/new-bestune-t90/t90-tth/
EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	4450	1765	1395	1988 Bitter Type 3 US brochure	https://www.carbackcatalogue.com/cars/bitter/models/type-3/1980-1989/1988/1988-bitter-type-3-us-brochure-specs-info.html
EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	4361	1800	1459	BMW Group technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0446043EN/624101
```

## 下一步优先处理

1. 按 E81/E87、F20/F21、改款前后和三门/五门边界批量闭合 BMW 1 系列 Ktype。
2. 核验 BMC Megastar 的 Bus、Van、底盘车轴距及车顶高度分支，避免把六个 Ktype 错并为一个尺寸组。
3. 补齐 Bentley Mulsanne、Mulsanne Turbo、T1、Turbo R、Continental R/T Mulliner 等经典车型。
4. 解决 Freeclimber I 不同资料间的 5 mm 长度和高度差异，以及 Bitter Type 3 1991 年改款后的三维。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2025/3342005/bentley_continental_gt_speed.html?utm_source=chatgpt.com "2025 Bentley Continental GT Speed Specs Review (575 kW / 782 PS / 771 hp) (for Europe worldwide)"
[2]: https://www.bestune-qatar.com/en/car/t77?utm_source=chatgpt.com "T77 | Bestune | en"
[3]: https://www.carbackcatalogue.com/cars/bitter/models/type-3/1980-1989/1988/1988-bitter-type-3-us-brochure-specs-info.html "1988 Bitter Type 3 | US Brochure Specs & Info"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 BMW 1 Series F20/F21 改款前及改款后四个物理车身组，新增 15 个 READY 映射。
* Ktype 已按 F20 五门、F21 三门及 2015 年改款边界批量关联；同一车身不因发动机或排量差异重复建组。相关 Ktype 目录分别明确标注 F20/F21。([AUTODOC][1])
* BMW 官方规格确认：改款前普通 F20/F21 外廓为 `4324 × 1765 × 1421 mm`；改款后普通 F20/F21 外廓为 `4329 × 1765 × 1421 mm`，宽度不含后视镜。([宝马集团新闻][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：36
* PENDING 映射：64
* 已确认尺寸组：19
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57464	57464	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58360	58360	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
115277	115277	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
115279	115279	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
55488	55488	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58336	58336	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
10313	10313	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58364	58364	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
58365	58365	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110048	110048	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110072	110072	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
10311	10311	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58344	58344	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110042	110042	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110060	110060	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	BMW Group official technical specifications – BMW 1 Series F20 5 Door	https://www.press.bmwgroup.com/global/article/attachment/T0132458EN/199449
EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	BMW Group official technical specifications – BMW 1 Series F21 3 Door	https://www.press.bmwgroup.com/global/article/attachment/T0132455EN/199443
EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421	BMW Group official technical specifications – BMW 1 Series F20 LCI 5 Door	https://www.press.bmwgroup.com/global/article/attachment/T0286379EN/419630
EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421	BMW Group official technical specifications – BMW 1 Series F21 LCI 3 Door	https://www.press.bmwgroup.com/global/article/attachment/T0286379EN/419629
```

## 下一步优先处理

1. 继续批量挂接已闭合 F20/F21 四个尺寸组对应的 118d、118i、120d 与 xDrive Ktype。
2. 首次闭合 E81 三门、E87 五门、E82 Coupe 和 E88 Convertible 尺寸组。
3. 随后处理剩余 Bentley 经典车型及 BMC Megastar 多车身分支。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/spares/bmw/1er-reihe/1-f20/57464-114-d?utm_source=chatgpt.com "Parts BMW F20 114 d 95 hp Diesel 2012 - 2015 N47 D16 A | 1 Series F20 parts catalogue AUTODOC"
[2]: https://www.press.bmwgroup.com/global/article/attachment/T0132458EN/199449?utm_source=chatgpt.com "BMW Group PressClub"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增完成 22 个输入 Ktype，并修正此前 `58360` 的单行映射；该 Ktype 横跨 2015 年改款边界，现拆为改款前、改款后两个物理外廓派生行。
* 已确认 `58360`、`58369`、`58371` 属于 F21 三门，`10316` 属于 F20 五门，`800019` 属于 F70；其余 Ktype 按前轮已确认车身代码批量挂接现有缓存组。([DENSO][1])
* 本轮仅复用现有 F20、F21、F70 尺寸组，没有重新抓取三维或重复输出来源。

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：58
* READY 映射行：63
* PENDING 输入 Ktype：42
* 已确认尺寸组：19
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58360_prefl	58360	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58360_facelift	58360	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
5671_prefl	5671	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F20改款前五门外廓。	READY
5671_facelift	5671	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F20改款后五门外廓。	READY
10314	10314	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58368_prefl	58368	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58368_facelift	58368	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
58369	58369	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110049	110049	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110073	110073	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
800019	800019	Hatchback	1 Series F70	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
52331	52331	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
100886	100886	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
110050	110050	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110074	110074	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
10312	10312	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58355_prefl	58355	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58355_facelift	58355	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
110043	110043	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110061	110061	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
115121	115121	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
115122	115122	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
10316	10316	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58371_prefl	58371	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58371_facelift	58371	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
58373	58373	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
100891	100891	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
100893	100893	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 首次闭合 BMW E81 三门、E87 五门、E82 Coupe 和 E88 Convertible 四类尺寸组，并批量挂接剩余 E8x Ktype。
2. 闭合 Bentley Mulsanne、T1、Turbo R、Continental R/T 等剩余经典车型。
3. 单独处理 BMC Megastar 的 Bus、Van、底盘车及轴距、车顶分支。

推进信号：CONTINUE

[1]: https://www.denso-am.eu/catalog/pv/58369?utm_source=chatgpt.com "Car parts for BMW 1 (F21), 118 d, 105kW(143ps), N47 D20 C | DENSO"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮完成剩余 21 个 BMW 1 Series E8x Ktype，新增 24 条 READY 映射。
* `58168`、`58186`、`58283` 横跨 E87 改款尺寸边界，分别拆成 `prefl` 与 `facelift` 派生行；其他 Ktype 按已确认的 E81、E87、E82 或 E88 车身代码挂接。([AUTODOC][1])
* 本轮首次闭合 E81 三门、E87 五门改款前后、E82 Coupe、E88 Convertible 五个尺寸组；BMW 官方规格给出的宽度均为车身宽度，不含外后视镜。([宝马集团新闻][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：79
* READY 映射行：87
* PENDING 输入 Ktype：21
* 已确认尺寸组：24
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58252	58252	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58963	58963	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58964	58964	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
17928	17928	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58168_prefl	58168	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58168_facelift	58168	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58169	58169	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58184	58184	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
12272	12272	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-01	HIGH	E82双门Coupe外廓。	READY
58253	58253	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
58254	58254	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58256	58256	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
55945	55945	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58185	58185	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
58186_prefl	58186	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58186_facelift	58186	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58187	58187	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
59274	59274	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
126495	126495	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
17931	17931	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
55647	55647	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
58283_prefl	58283	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58283_facelift	58283	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58303	58303	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421	BMW Group official technical specifications – BMW 1 Series 5 Door	https://www.press.bmwgroup.com/netherlands/article/attachment/T0024402NL/44288
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	BMW Group official technical specifications – BMW 1 Series 3 Door	https://www.press.bmwgroup.com/netherlands/article/attachment/T0024402NL/44288
EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	BMW Group official technical specifications – BMW 1 Series 5 Door Pre-Facelift	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0013432EN_GB/30291
EU-BMW-1-SERIES-E82-COUPE-01	4360	1748	1423	BMW Group official technical specifications – BMW 1 Series Coupe	https://www.press.bmwgroup.com/global/article/attachment/T0095893EN/142801
EU-BMW-1-SERIES-E88-CONVERTIBLE-01	4360	1748	1411	BMW Group official technical specifications – BMW 1 Series Convertible	https://www.press.bmwgroup.com/global/article/attachment/T0095873EN/142796
```

## 下一步优先处理

1. 闭合 Bentley Continental R、Continental S、Continental T Mulliner、Mulsanne、Mulsanne Turbo、T1 与 Turbo R。
2. 批量处理 Bertone Freeclimber I 的四个 Ktype。
3. 闭合 Bitter Type 3 1991–1992 改款外廓。
4. 最后集中处理 BMC Megastar Bus、Van 与底盘车的轴距、车顶和车身分支。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/flywheel-10157/bmw/1er-reihe/1-e87/58168-116-i?utm_source=chatgpt.com "Flywheel BMW E87 116 i 115 hp Petrol 85 kW 2004 - 2011 N45 B16 A"
[2]: https://www.press.bmwgroup.com/netherlands/article/attachment/T0024402NL/44288?utm_source=chatgpt.com "The new BMW 1 Series. Contents."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮完成剩余 15 个非 BMC Ktype，新增 15 条 READY 映射。
* Bentley Continental R 与 Continental S 复用同一物理外廓；Continental T Mulliner 独立建组。Mulsanne、Mulsanne Turbo、T1、Turbo R 后期型及 Turbo S 分别闭合。([汽车目录][1])
* Bertone Freeclimber I 的四个发动机版本批量关联同一三门 SUV 尺寸组。([Bertone][2])
* Bitter Type 3 的 1991–1992 年 3.0 与 4.0 版本尺寸未改变，直接复用既有 Type 3 Convertible 尺寸组，不重复输出尺寸事实。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：94
* READY 映射行：102
* PENDING 输入 Ktype：6
* 已确认尺寸组：32
* 本轮首次创建尺寸组：8
* 剩余 Ktype 均为 BMC Megastar。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16853	16853	Coupe	Continental R I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental R双门外廓。	READY
16856	16856	Coupe	Continental R I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental R后期动力版本沿用同一双门外廓。	READY
16854	16854	Coupe	Continental S I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental S沿用Continental R双门外廓。	READY
16855	16855	Coupe	Continental T I Mulliner		2	EU-BENTLEY-CONTINENTAL-T-I-MULLINER-COUPE-01	HIGH	短轴Continental T Mulliner双门外廓。	READY
34838	34838	Sedan	Mulsanne II		4	EU-BENTLEY-MULSANNE-II-SEDAN-01	HIGH	第二代Mulsanne标准轴距四门外廓。	READY
108189	108189	Sedan	Mulsanne Turbo I		4	EU-BENTLEY-MULSANNE-TURBO-I-SEDAN-01	MEDIUM	Mulsanne Turbo标准轴距四门外廓。	READY
35592	35592	Sedan	T1		4	EU-BENTLEY-T1-I-SEDAN-01	HIGH	T1四门外廓。	READY
12627	12627	Sedan	Turbo R I Facelift		4	EU-BENTLEY-TURBO-R-I-SEDAN-FACELIFT-01	HIGH	1995年更新后的Turbo R标准轴距四门外廓。	READY
100707	100707	Sedan	Turbo S I		4	EU-BENTLEY-TURBO-S-I-SEDAN-01	HIGH	Turbo S四门外廓。	READY
12581	12581	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12584	12584	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12582	12582	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12586	12586	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12597	12597	Convertible	Type 3		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	HIGH	Type 3双门敞篷外廓。	READY
12598	12598	Convertible	Type 3		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	HIGH	Type 3双门敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	5342	1872	1462	Automobile-Catalog Bentley Continental R; Automobile-Catalog Bentley Continental S	https://www.automobile-catalog.com/car/1996/260825/bentley_continental_r.html;https://www.automobile-catalog.com/car/1994/2993630/bentley_continental_s.html
EU-BENTLEY-CONTINENTAL-T-I-MULLINER-COUPE-01	5222	1872	1447	Automobile-Catalog Bentley Continental T Mulliner	https://www.automobile-catalog.com/car/1999/261020/bentley_continental_t_mulliner.html
EU-BENTLEY-MULSANNE-II-SEDAN-01	5575	1926	1521	Bentley Heritage Collection; Automobile-Catalog Bentley Mulsanne	https://www.bentleymedia.com/en/heritage-collection/2010-mulsanne-dk10fej;https://www.automobile-catalog.com/car/2010/1193390/bentley_mulsanne.html
EU-BENTLEY-MULSANNE-TURBO-I-SEDAN-01	5309	1887	1485	Automobile-Catalog Bentley Mulsanne Turbo	https://www.automobile-catalog.com/car/1984/260240/bentley_mulsanne_turbo.html
EU-BENTLEY-T1-I-SEDAN-01	5169	1803	1518	Bentley Heritage Collection; Automobile-Catalog Bentley T	https://www.bentleymedia.com/en/heritage-collection/1965-t-series-saloon;https://www.automobile-catalog.com/car/1976/76205/bentley_t.html
EU-BENTLEY-TURBO-R-I-SEDAN-FACELIFT-01	5295	1914	1480	Automobile-Catalog Bentley Turbo R	https://www.automobile-catalog.com/car/1995/260840/bentley_turbo_r.html
EU-BENTLEY-TURBO-S-I-SEDAN-01	5268	1887	1480	Automobile-Catalog Bentley Turbo S	https://www.automobile-catalog.com/car/1995/1767995/bentley_turbo_s.html
EU-BERTONE-FREECLIMBER-I-SUV-3D-01	3995	1650	1650	Drive.Place Bertone Freeclimber I; Auto-Data Bertone Freeclimber	https://bertone.drive.place/freeclimber/i/group_offroad_3d/357942;https://www.auto-data.net/en/bertone-freeclimber-generation-1641
```

## 下一步优先处理

1. 一次性核对 BMC Megastar 的可用轴距、车顶高度与车身长度组合。
2. 分别闭合 Bus、Van 和 Pritsche/Fahrgestell 的物理外廓分支。
3. 批量处理最后 6 个 Ktype，并在达到 `PENDING=0` 后直接生成两张最终完整 TSV 和指定下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/260930/bentley_continental_r.html?utm_source=chatgpt.com "2002 Bentley Continental R Specs Review (300 kW ..."
[2]: https://bertone.drive.place/freeclimber/i/group_offroad_3d/357942?utm_source=chatgpt.com "Bertone Freeclimber I 2.0 MT 129 hp 3 door SUV"
[3]: https://www.automobile-catalog.com/car/1991/261725/bitter_type_3_cabriolet_3_0_24v.html?utm_source=chatgpt.com "1991 Bitter Type 3 Cabriolet 3.0 24V (man. 5)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮完成 `156012`、`156013`、`156016`，并闭合 `156014` 的 `360 VH` 高顶分支。
* 首次创建 310 P 平台车、290 V 普通顶厢式车、360 VH 高顶厢式车和 360 P 平台车四个尺寸组。
* 车型资料确认 96 kW Megastar 同时存在 `360 V`、`360 VH`、`360 M`、`360 MH` 和 `360 P` 等不同外廓分支。([Sofima Aftermarket][1])
* `360 V` 普通顶在两份官方资料中存在前后期外廓差异，尚未确认切换边界，因此不覆盖或强行合并；`290 M`、`360 M`、`360 MH` 尚缺直接支持完整三维的资料。([德萨迪塞尔][2])

## 当前批次进度

* 输入 Ktype：100
* 已全部闭合输入 Ktype：97
* READY 映射行：106
* PENDING 映射行：4
* PENDING 输入 Ktype：3（`156011`、`156014`、`156015`）
* 已确认尺寸组：36
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156011	156011	MPV	Megastar I	290 M			LOW	290 M小型客车外廓尚缺直接三维资料。	PENDING: 缺少直接支持290 M完整三维的可追溯来源
156012	156012	Pickup	Megastar I	310 P		EU-BMC-MEGASTAR-I-PICKUP-310P-01	HIGH	310 P单排平台及底盘外廓。	READY
156013	156013	Van	Megastar I	290 V		EU-BMC-MEGASTAR-I-VAN-290V-LOWROOF-01	HIGH	290 V普通顶厢式车外廓。	READY
156014_lowroof	156014	Van	Megastar I	360 V			LOW	360 V普通顶前后期资料外廓边界尚未闭合。	PENDING: 360 V普通顶前后期资料外廓冲突尚未解析
156014_highroof	156014	Van	Megastar I	360 VH		EU-BMC-MEGASTAR-I-VAN-360VH-HIGHROOF-01	MEDIUM	360 VH高顶厢式车外廓。	READY
156015_lowroof	156015	MPV	Megastar I	360 M			LOW	360 M普通顶小型客车外廓尚缺直接三维资料。	PENDING: 缺少直接支持360 M完整三维的可追溯来源
156015_highroof	156015	MPV	Megastar I	360 MH			LOW	360 MH高顶小型客车外廓尚缺直接三维资料。	PENDING: 缺少直接支持360 MH完整三维的可追溯来源
156016	156016	Pickup	Megastar I	360 P		EU-BMC-MEGASTAR-I-PICKUP-360P-01	HIGH	360 P单排平台及底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMC-MEGASTAR-I-PICKUP-310P-01	5326	1958	2220	BMC Megastar 310 P/360 P official brochure	https://www.dersadiesel.com/files/310p_360p_tek_sira.pdf
EU-BMC-MEGASTAR-I-VAN-290V-LOWROOF-01	4784	1958	2220	BMC Megastar 290 V/360 V official brochure	https://www.dersadiesel.com/files/290v_360V_panel_van.pdf
EU-BMC-MEGASTAR-I-VAN-360VH-HIGHROOF-01	5502	1958	2445	BMC Megastar 360 V/360 VH official brochure	https://www.dersadiesel.com/files/360vh_panel_van.pdf
EU-BMC-MEGASTAR-I-PICKUP-360P-01	5826	1958	2220	BMC Megastar 310 P/360 P official brochure	https://www.dersadiesel.com/files/310p_360p_tek_sira.pdf
```

## 下一步优先处理

1. 定位直接列出 `290 M`、`360 M` 与 `360 MH` 完整外廓的 BMC 规格资料。
2. 解析 `360 V` 普通顶前后期资料的车型年份或改型边界，必要时拆分稳定的前后期尺寸组。
3. 四条 PENDING 映射闭合后，立即进行一次机械检查并输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://sofima-aftermarket.com/EU/wp-content/uploads/downloads/sofima/pdfs/CatalogoLV/SOFIMA_Catalogo_LV_2021.pdf?utm_source=chatgpt.com "LIGHT VEHICLES"
[2]: https://www.dersadiesel.com/files/290v_360V_panel_van.pdf?utm_source=chatgpt.com "MEGASTAR 290V-360 V Arka TR yeni.ai"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1601-1700_ktype_dimension_mapping_final.tsv
- left18448_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后 4 条 BMC Megastar PENDING 已闭合。原厂资料分别确认前期 `360 V` 为 `5484 × 1958 × 2220 mm`，后期普通顶/高顶为 `5502 × 1958 × 2255/2445 mm`；`290 M`、`360 M`、`360 MH` 客运版按对应 290/360 车身壳体复用尺寸组，映射置信度保留为 `MEDIUM`。([德萨迪塞尔][1])
* 修正 `106066`：Flying Spur Speed 的高度为 `1465 mm`，不再错误复用高度 `1475 mm` 的普通改款尺寸组，已创建独立 Speed 尺寸组。([汽车档案馆][2])
* 已完成固定表头、唯一键、引用闭合、正整数三维、来源字段及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：112
* PENDING 映射：0
* DIMENSION_GROUP：38
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 缺失尺寸组引用：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
106066	106066	Sedan	Continental Flying Spur I Facelift	3W	4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SPEED-SEDAN-FACELIFT-01	HIGH	Speed版本采用改款后四门低车身外廓。	READY
34873	34873	Coupe	Continental GT I	3W	2	EU-BENTLEY-CONTINENTAL-GT-I-SUPERSPORTS-COUPE-01	HIGH	Supersports宽体双门外廓。	READY
128569	128569	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代GT双门外廓。	READY
144433	144433	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	HIGH	第三代GT双门外廓。	READY
16853	16853	Coupe	Continental R I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental R双门外廓。	READY
16856	16856	Coupe	Continental R I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental R后期动力版本沿用同一双门外廓。	READY
16854	16854	Coupe	Continental S I		2	EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	HIGH	Continental S沿用Continental R双门外廓。	READY
16855	16855	Coupe	Continental T I Mulliner		2	EU-BENTLEY-CONTINENTAL-T-I-MULLINER-COUPE-01	HIGH	短轴Continental T Mulliner双门外廓。	READY
160823	160823	Convertible	Continental GTC IV		2	EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	HIGH	第四代混动敞篷外廓。	READY
160310	160310	Coupe	Continental GT IV		2	EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	HIGH	第四代混动双门外廓。	READY
800960	800960	Coupe	Continental GT IV		2	EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	HIGH	第四代混动双门外廓。	READY
800961	800961	Convertible	Continental GTC IV		2	EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	HIGH	第四代混动敞篷外廓。	READY
146534	146534	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代Flying Spur四门外廓。	READY
105576	105576	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	MEDIUM	4.0 Flex按第二代Flying Spur四门外廓归组。	READY
800959	800959	Sedan	Flying Spur III Facelift		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	HIGH	2024改款混动四门外廓。	READY
802249	802249	Sedan	Flying Spur III Facelift		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	HIGH	2024改款混动四门外廓。	READY
34838	34838	Sedan	Mulsanne II		4	EU-BENTLEY-MULSANNE-II-SEDAN-01	HIGH	第二代Mulsanne标准轴距四门外廓。	READY
108189	108189	Sedan	Mulsanne Turbo I		4	EU-BENTLEY-MULSANNE-TURBO-I-SEDAN-01	MEDIUM	Mulsanne Turbo标准轴距四门外廓。	READY
35592	35592	Sedan	T1		4	EU-BENTLEY-T1-I-SEDAN-01	HIGH	T1四门外廓。	READY
12627	12627	Sedan	Turbo R I Facelift		4	EU-BENTLEY-TURBO-R-I-SEDAN-FACELIFT-01	HIGH	1995年更新后的Turbo R标准轴距四门外廓。	READY
100707	100707	Sedan	Turbo S I		4	EU-BENTLEY-TURBO-S-I-SEDAN-01	HIGH	Turbo S四门外廓。	READY
12589	12589	SUV	Freeclimber II		3	EU-BERTONE-FREECLIMBER-II-SUV-3D-01	HIGH	Freeclimber II三门外廓。	READY
12581	12581	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12584	12584	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12582	12582	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
12586	12586	SUV	Freeclimber I		3	EU-BERTONE-FREECLIMBER-I-SUV-3D-01	MEDIUM	Freeclimber I三门外廓。	READY
802622	802622	Hatchback	B70 III Facelift		5	EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	HIGH	第三代改款五门掀背外廓。	READY
802623	802623	Hatchback	B70 III Facelift		5	EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	HIGH	第三代改款五门掀背外廓。	READY
162924	162924	SUV	Joyee 07 I		5	EU-BESTUNE-YUEYI-07-I-SUV-01	MEDIUM	Joyee 07按Yueyi 07出口车型边界归组。	READY
802626	802626	SUV	T77 I Facelift		5	EU-BESTUNE-T77-I-SUV-FACELIFT-01	HIGH	第一代改款五门SUV外廓。	READY
802624	802624	SUV	T90 I		5	EU-BESTUNE-T90-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
802625	802625	SUV	T90 I		5	EU-BESTUNE-T90-I-SUV-01	HIGH	第一代五门SUV外廓。	READY
12597	12597	Convertible	Type 3		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	HIGH	Type 3双门敞篷外廓。	READY
127261	127261	Convertible	Type 3 Pre-Facelift		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	MEDIUM	1987至1990年前改款双门敞篷外廓。	READY
12598	12598	Convertible	Type 3		2	EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	HIGH	Type 3双门敞篷外廓。	READY
156011	156011	MPV	Megastar I	290 M		EU-BMC-MEGASTAR-I-VAN-290V-LOWROOF-01	MEDIUM	290 M客运版沿用290普通顶车身外廓。	READY
156012	156012	Pickup	Megastar I	310 P		EU-BMC-MEGASTAR-I-PICKUP-310P-01	HIGH	310 P单排平台及底盘外廓。	READY
156013	156013	Van	Megastar I	290 V		EU-BMC-MEGASTAR-I-VAN-290V-LOWROOF-01	HIGH	290 V普通顶厢式车外廓。	READY
156014_lowroof_prefl	156014	Van	Megastar I Pre-Facelift	360 V		EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-PREFL-01	HIGH	官方资料确认的前期360 V普通顶外廓。	READY
156014_lowroof_facelift	156014	Van	Megastar I Facelift	360 V		EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-FACELIFT-01	HIGH	官方资料确认的后期360 V普通顶外廓。	READY
156014_highroof	156014	Van	Megastar I Facelift	360 VH		EU-BMC-MEGASTAR-I-VAN-360VH-HIGHROOF-01	HIGH	360 VH高顶厢式车外廓。	READY
156015_lowroof_prefl	156015	MPV	Megastar I Pre-Facelift	360 M		EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-PREFL-01	MEDIUM	360 M客运版沿用前期360普通顶车身外廓。	READY
156015_lowroof_facelift	156015	MPV	Megastar I Facelift	360 M		EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-FACELIFT-01	MEDIUM	360 M客运版沿用后期360普通顶车身外廓。	READY
156015_highroof	156015	MPV	Megastar I Facelift	360 MH		EU-BMC-MEGASTAR-I-VAN-360VH-HIGHROOF-01	MEDIUM	360 MH客运版沿用360高顶车身外廓。	READY
156016	156016	Pickup	Megastar I	360 P		EU-BMC-MEGASTAR-I-PICKUP-360P-01	HIGH	360 P单排平台及底盘外廓。	READY
800017	800017	Hatchback	1 Series F70	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门前驱外廓。	READY
57464	57464	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58360_prefl	58360	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58360_facelift	58360	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
115277	115277	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
115279	115279	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
55488	55488	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58336	58336	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
10313	10313	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
58252	58252	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58364	58364	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
58365	58365	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
58963	58963	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58964	58964	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
110048	110048	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110072	110072	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
10311	10311	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
17928	17928	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58168_prefl	58168	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58168_facelift	58168	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58169	58169	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58184	58184	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58344	58344	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110042	110042	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款外廓。	READY
110060	110060	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款外廓。	READY
5671_prefl	5671	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F20改款前五门外廓。	READY
5671_facelift	5671	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F20改款后五门外廓。	READY
10314	10314	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
12272	12272	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-01	HIGH	E82双门Coupe外廓。	READY
58253	58253	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
58254	58254	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58256	58256	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58368_prefl	58368	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58368_facelift	58368	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
58369	58369	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
110049	110049	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110073	110073	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
800019	800019	Hatchback	1 Series F70	F70	5	EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	HIGH	F70五门外廓。	READY
52331	52331	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
100886	100886	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
110050	110050	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110074	110074	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
10312	10312	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
55945	55945	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
58185	58185	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	E87五门改款前外廓。	READY
58186_prefl	58186	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58186_facelift	58186	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58187	58187	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58355_prefl	58355	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58355_facelift	58355	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
59274	59274	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
110043	110043	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
110061	110061	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
115121	115121	Hatchback	1 Series II Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门改款后外廓。	READY
115122	115122	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	F21三门改款后外廓。	READY
126495	126495	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
10316	10316	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
17931	17931	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	E81三门外廓。	READY
55647	55647	Convertible	1 Series I	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-01	HIGH	E88双门敞篷外廓。	READY
58283_prefl	58283	Hatchback	1 Series I Pre-Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越E87改款边界，拆分为改款前外廓。	READY
58283_facelift	58283	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越E87改款边界，拆分为改款后外廓。	READY
58303	58303	Hatchback	1 Series I Facelift	E87	5	EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	HIGH	E87五门改款外廓。	READY
58371_prefl	58371	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2015年改款，拆分为F21改款前三门外廓。	READY
58371_facelift	58371	Hatchback	1 Series II Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2015年改款，拆分为F21改款后三门外廓。	READY
58373	58373	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
100891	100891	Hatchback	1 Series II Pre-Facelift	F20	5	EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前外廓。	READY
100893	100893	Hatchback	1 Series II Pre-Facelift	F21	3	EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	HIGH	F21三门改款前外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1601-1700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SPEED-SEDAN-FACELIFT-01	5290	1916	1465	Bentley Continental Flying Spur 2008 official brochure; EncyCARpedia Bentley Continental Flying Spur Speed	https://autocatalogarchive.com/wp-content/uploads/2016/05/Bentley-Continental-Flying-Spur-2008.pdf;https://www.encycarpedia.com/bentley/08-continental-flying-spur-speed-saloon
EU-BENTLEY-CONTINENTAL-GT-I-SUPERSPORTS-COUPE-01	4804	1945	1380	Bentley Heritage Collection; carsales	https://www.bentleymedia.com/en/heritage-collection/2011-continental-supersports-dk12fzm;https://www.carsales.com.au/research/bentley/continental/2009/supersports/
EU-BENTLEY-CONTINENTAL-GT-III-COUPE-01	4850	1954	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/2021/2606630/bentley_continental_gt.html
EU-BENTLEY-CONTINENTAL-R-I-COUPE-01	5342	1872	1462	Automobile-Catalog Bentley Continental R; Automobile-Catalog Bentley Continental S	https://www.automobile-catalog.com/car/1996/260825/bentley_continental_r.html;https://www.automobile-catalog.com/car/1994/2993630/bentley_continental_s.html
EU-BENTLEY-CONTINENTAL-T-I-MULLINER-COUPE-01	5222	1872	1447	Automobile-Catalog Bentley Continental T Mulliner	https://www.automobile-catalog.com/car/1999/261020/bentley_continental_t_mulliner.html
EU-BENTLEY-CONTINENTAL-GTC-IV-CONVERTIBLE-01	4895	1966	1392	Bentley Motors; Edmunds	https://www.bentleymotors.com/en/models/continental-gtc/continental-gtc.html;https://www.edmunds.com/bentley/continental/2025/st-402064474/features-specs/
EU-BENTLEY-CONTINENTAL-GT-IV-COUPE-01	4895	1966	1397	Bentley Motors; Automobile-Catalog	https://www.bentleymotors.com/en/models/continental-gt/continental-gt.html;https://www.automobile-catalog.com/car/2025/3342005/bentley_continental_gt_speed.html
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1978	1483	Bentley Flying Spur official brochure	https://cdn.bentleymotors.com/downloads/en/brochure/global/flying-spur/BEN-FS-21-017_FlyingSpurMullinerCustomerBookUpdate_EN_v17_AW%28Digital%29_clean.pdf
EU-BENTLEY-FLYING-SPUR-II-SEDAN-01	5295	1976	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/1830305/bentley_flying_spur.html
EU-BENTLEY-FLYING-SPUR-III-SEDAN-FACELIFT-01	5316	1988	1474	Bentley Media technical specifications	https://www.bentleymedia.com/attachment/7b743a18-74d8-4a2b-89c6-5eee8377392f
EU-BENTLEY-MULSANNE-II-SEDAN-01	5575	1926	1521	Bentley Heritage Collection; Automobile-Catalog Bentley Mulsanne	https://www.bentleymedia.com/en/heritage-collection/2010-mulsanne-dk10fej;https://www.automobile-catalog.com/car/2010/1193390/bentley_mulsanne.html
EU-BENTLEY-MULSANNE-TURBO-I-SEDAN-01	5309	1887	1485	Automobile-Catalog Bentley Mulsanne Turbo	https://www.automobile-catalog.com/car/1984/260240/bentley_mulsanne_turbo.html
EU-BENTLEY-T1-I-SEDAN-01	5169	1803	1518	Bentley Heritage Collection; Automobile-Catalog Bentley T	https://www.bentleymedia.com/en/heritage-collection/1965-t-series-saloon;https://www.automobile-catalog.com/car/1976/76205/bentley_t.html
EU-BENTLEY-TURBO-R-I-SEDAN-FACELIFT-01	5295	1914	1480	Automobile-Catalog Bentley Turbo R	https://www.automobile-catalog.com/car/1995/260840/bentley_turbo_r.html
EU-BENTLEY-TURBO-S-I-SEDAN-01	5268	1887	1480	Automobile-Catalog Bentley Turbo S	https://www.automobile-catalog.com/car/1995/1767995/bentley_turbo_s.html
EU-BERTONE-FREECLIMBER-II-SUV-3D-01	3785	1740	1720	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Bertone/18094/Bertone-Freeclimber-16-Si.html
EU-BERTONE-FREECLIMBER-I-SUV-3D-01	3995	1650	1650	Drive.Place Bertone Freeclimber I; Auto-Data Bertone Freeclimber	https://bertone.drive.place/freeclimber/i/group_offroad_3d/357942;https://www.auto-data.net/en/bertone-freeclimber-generation-1641
EU-BESTUNE-B70-III-HATCHBACK-FACELIFT-01	4810	1840	1455	BESTUNE Russia official specification	https://bestune.ru/B70_Price_01_11_2025_6557653825203732106.pdf
EU-BESTUNE-YUEYI-07-I-SUV-01	4745	1880	1710	Auto-Data	https://www.auto-data.net/en/bestune-yueyi-07-generation-10854
EU-BESTUNE-T77-I-SUV-FACELIFT-01	4525	1845	1615	Bestune Qatar official specification	https://www.bestune-qatar.com/en/car/t77
EU-BESTUNE-T90-I-SUV-01	4718	1880	1710	BESTUNE Russia official specification	https://bestune.ru/models/new-bestune-t90/t90-tth/
EU-BITTER-TYPE-3-I-CONVERTIBLE-PREFL-01	4450	1765	1395	1988 Bitter Type 3 US brochure	https://www.carbackcatalogue.com/cars/bitter/models/type-3/1980-1989/1988/1988-bitter-type-3-us-brochure-specs-info.html
EU-BMC-MEGASTAR-I-VAN-290V-LOWROOF-01	4784	1958	2220	BMC Megastar 290 V/360 V official brochure; BMC Megastar 290 V Kombi Van official brochure	https://www.dersadiesel.com/files/290v_360V_panel_van.pdf;https://www.dersadiesel.com/files/290v_kombi_van.pdf
EU-BMC-MEGASTAR-I-PICKUP-310P-01	5326	1958	2220	BMC Megastar 310 P/360 P official brochure	https://www.dersadiesel.com/files/310p_360p_tek_sira.pdf
EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-PREFL-01	5484	1958	2220	BMC Megastar 290 V/360 V official brochure	https://www.dersadiesel.com/files/290v_360V_panel_van.pdf
EU-BMC-MEGASTAR-I-VAN-360V-LOWROOF-FACELIFT-01	5502	1958	2255	BMC Megastar 360 V/360 VH official brochure	https://www.dersadiesel.com/files/360vh_panel_van.pdf
EU-BMC-MEGASTAR-I-VAN-360VH-HIGHROOF-01	5502	1958	2445	BMC Megastar 360 V/360 VH official brochure	https://www.dersadiesel.com/files/360vh_panel_van.pdf
EU-BMC-MEGASTAR-I-PICKUP-360P-01	5826	1958	2220	BMC Megastar 310 P/360 P official brochure	https://www.dersadiesel.com/files/310p_360p_tek_sira.pdf
EU-BMW-1-SERIES-F70-HATCHBACK-5D-01	4361	1800	1459	BMW Group technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0446043EN/624101
EU-BMW-1-SERIES-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	BMW Group official technical specifications – BMW 1 Series F20 5 Door	https://www.press.bmwgroup.com/global/article/attachment/T0132458EN/199449
EU-BMW-1-SERIES-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	BMW Group official technical specifications – BMW 1 Series F21 3 Door	https://www.press.bmwgroup.com/global/article/attachment/T0132455EN/199443
EU-BMW-1-SERIES-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421	BMW Group official technical specifications – BMW 1 Series F21 LCI 3 Door	https://www.press.bmwgroup.com/global/article/attachment/T0286379EN/419629
EU-BMW-1-SERIES-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421	BMW Group official technical specifications – BMW 1 Series F20 LCI 5 Door	https://www.press.bmwgroup.com/global/article/attachment/T0286379EN/419630
EU-BMW-1-SERIES-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421	BMW Group official technical specifications – BMW 1 Series 5 Door	https://www.press.bmwgroup.com/netherlands/article/attachment/T0024402NL/44288
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	BMW Group official technical specifications – BMW 1 Series 3 Door	https://www.press.bmwgroup.com/netherlands/article/attachment/T0024402NL/44288
EU-BMW-1-SERIES-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	BMW Group official technical specifications – BMW 1 Series 5 Door Pre-Facelift	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0013432EN_GB/30291
EU-BMW-1-SERIES-E82-COUPE-01	4360	1748	1423	BMW Group official technical specifications – BMW 1 Series Coupe	https://www.press.bmwgroup.com/global/article/attachment/T0095893EN/142801
EU-BMW-1-SERIES-E88-CONVERTIBLE-01	4360	1748	1411	BMW Group official technical specifications – BMW 1 Series Convertible	https://www.press.bmwgroup.com/global/article/attachment/T0095873EN/142796
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1601-1700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.dersadiesel.com/files/290v_360V_panel_van.pdf "https://www.dersadiesel.com/files/290v_360V_panel_van.pdf"
[2]: https://autocatalogarchive.com/wp-content/uploads/2016/05/Bentley-Continental-Flying-Spur-2008.pdf "https://autocatalogarchive.com/wp-content/uploads/2016/05/Bentley-Continental-Flying-Spur-2008.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1969 行）
- 累计尺寸组：dimension_groups_final.tsv（627 行）

