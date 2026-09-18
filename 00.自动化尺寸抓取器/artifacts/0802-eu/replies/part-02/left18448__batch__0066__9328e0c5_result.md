# 任务：left18448 第 6501-6600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0066__9328e0c5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6501-6600 行

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
left18448 第 6501-6600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Honda	Accord viii tourer	2.2 I-dtec	Kombi	Frontantrieb	Diesel	Jul 2008	Jun 2015	34929
Honda	City	1.5 I-vtec	Stufenheck	Frontantrieb	Benzin	Feb 2009	Aug 2014	34515
Honda	Civic iii	1.2	Stufenheck	Frontantrieb	Benzin	Jan 1985	Oct 1987	14663
Honda	Civic iii	1.3	Stufenheck	Frontantrieb	Benzin	Oct 1983	Oct 1987	14664
Honda	Civic iii	1.5	Stufenheck	Frontantrieb	Benzin	Oct 1983	Oct 1987	14665
Honda	Civic iii	1.5 GT	Stufenheck	Frontantrieb	Benzin	Jan 1985	Oct 1987	14667
Honda	Civic iii	1.5 GTI	Stufenheck	Frontantrieb	Benzin	Mar 1986	Oct 1987	14666
Honda	Civic iv	1.3	Stufenheck	Frontantrieb	Benzin	Oct 1987	Dec 1989	17634
Honda	Civic iv	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	Oct 1987	Sep 1991	18019
Honda	Civic iv	1.6 16V 4X4	Stufenheck	Allrad	Benzin	Nov 1987	Sep 1991	55637
Honda	Civic iv hatchback	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1988	Sep 1991	18018
Honda	Civic iv shuttle	1.4 I 16V	Kombi	Frontantrieb	Benzin	Jan 1988	Dec 1992	18864
Honda	Civic ix	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2011	Dec 2016	121249
Honda	Civic ix	1.8	Stufenheck	Frontantrieb	Benzin	Feb 2012	Dec 2016	57475
Honda	Civic ix	1.8	Stufenheck	Frontantrieb	Benzin	Sep 2011	Dec 2016	107634
Honda	Civic ix	1.4 I-vtec	Schrägheck	Frontantrieb	Benzin	Feb 2012	Dec 2016	13918
Honda	Civic ix	1.6 I-dtec	Schrägheck	Frontantrieb	Diesel	Feb 2013	Dec 2016	58791
Honda	Civic ix	1.8 I-vtec	Schrägheck	Frontantrieb	Benzin	Feb 2012	Dec 2016	13926
Honda	Civic ix	2.0 I-vtec Type R	Schrägheck	Frontantrieb	Benzin	Aug 2015	Dec 2016	116064
Honda	Civic ix	2.2 I-dtec	Schrägheck	Frontantrieb	Diesel	Feb 2012	Dec 2016	13927
Honda	Civic ix tourer	1.6 I-dtec	Kombi	Frontantrieb	Diesel	Jan 2014	Dec 2016	100487
Honda	Civic ix tourer	1.8 I-vtec	Kombi	Frontantrieb	Benzin	Jan 2014	Dec 2016	100489
Honda	Civic v	1.5	Stufenheck	Frontantrieb	Benzin	Oct 1993	Dec 1995	55932
Honda	Civic v hatchback	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	Oct 1991	Nov 1995	18020
Honda	Civic vi	1.6 I	Coupe	Frontantrieb	Benzin	Mar 1996	Mar 2000	17525
Honda	Civic vi	1.6 I Vtec	Stufenheck	Frontantrieb	Benzin	Nov 1995	Feb 2001	14901
Honda	Civic vi	1.6 I Vtec	Coupe	Frontantrieb	Benzin	Mar 1996	Mar 2000	17524
Honda	Civic vi	1.6 I Vtec	Coupe	Frontantrieb	Benzin	Apr 1999	Dec 2000	18832
Honda	Civic vi aerodeck	1.6 16V	Kombi	Frontantrieb	Benzin	Apr 1998	Feb 2001	54963
Honda	Civic vi fastback	1.5 16V	Schrägheck	Frontantrieb	Benzin	Jan 1997	Feb 2001	7816
Honda	Civic vi fastback	1.6 16V	Schrägheck	Frontantrieb	Benzin	Jan 1997	Feb 2001	7817
Honda	Civic vi fastback	1.6 VTI	Schrägheck	Frontantrieb	Benzin	Jan 1997	Feb 2001	11506
Honda	Civic vi fastback	1.8 16V	Schrägheck	Frontantrieb	Benzin	Jan 1997	Feb 2001	7818
Honda	Civic vi fastback	2.0 I TD	Schrägheck	Frontantrieb	Diesel	Jan 1997	Feb 2001	7819
Honda	Civic vi fastback	2.0 Tdic	Schrägheck	Frontantrieb	Diesel	Nov 1998	Oct 2000	54964
Honda	Civic vii	1.4	Stufenheck	Frontantrieb	Benzin	Dec 2000	Sep 2005	18468
Honda	Civic vii	1.5	Stufenheck	Frontantrieb	Benzin	Feb 2003	Sep 2005	59695
Honda	Civic vii	1.6	Stufenheck	Frontantrieb	Benzin	Feb 2001	Sep 2005	18469
Honda	Civic vii	1.7	Stufenheck	Frontantrieb	Benzin	Feb 2001	Sep 2005	16103
Honda	Civic vii	1.3 IMA	Stufenheck	Frontantrieb	Benzin/Elektro	Oct 2003	Sep 2005	17802
Honda	Civic vii	1.6 I	Coupe	Frontantrieb	Benzin	Feb 2001	Dec 2005	15527
Honda	Civic vii hatchback	1.4 I	Schrägheck	Frontantrieb	Benzin	Feb 2001	Sep 2005	15934
Honda	Civic vii hatchback	1.4 IS	Schrägheck	Frontantrieb	Benzin	Nov 2000	Sep 2005	15525
Honda	Civic vii hatchback	1.6 I	Schrägheck	Frontantrieb	Benzin	Feb 2001	Sep 2005	15526
Honda	Civic vii hatchback	1.7 Ctdi	Schrägheck	Frontantrieb	Diesel	Jan 2002	Sep 2005	16522
Honda	Civic vii hatchback	2.0 I Sport	Schrägheck	Frontantrieb	Benzin	Sep 2001	Sep 2005	18063
Honda	Civic viii	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2005	Dec 2012	55936
Honda	Civic viii	1.3 IMA	Stufenheck	Frontantrieb	Benzin/Elektro	Jan 2010	Feb 2012	17513
Honda	Civic x	1.0 Vtec	Schrägheck	Frontantrieb	Benzin	Feb 2017	Dec 2022	126524
Honda	Civic x	1.5 Vtec	Schrägheck	Frontantrieb	Benzin	Feb 2017	Dec 2022	126522
Honda	Civic x	1.5 Vtec	Stufenheck	Frontantrieb	Benzin	Aug 2016	Dec 2022	126886
Honda	Civic x	2.0 Type-r	Schrägheck	Frontantrieb	Benzin	Jun 2017	Dec 2022	127817
Honda	Civic xi	1.5 Turbo ECO LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2021	-	152669
Honda	Civic xi	2.0 E:hev	Schrägheck	Frontantrieb	Benzin/Elektro	Jul 2022	-	149700
Honda	Civic xi	Type-r	Schrägheck	Frontantrieb	Benzin	Jun 2022	-	149691
Honda	Concerto	1.4	Stufenheck	Frontantrieb	Benzin	Aug 1989	Oct 1991	14144
Honda	Concerto	1.4	Schrägheck	Frontantrieb	Benzin	Oct 1989	Oct 1992	18833
Honda	Concerto	1.4	Stufenheck	Frontantrieb	Benzin	Oct 1989	Oct 1992	18834
Honda	Crossroad	2	SUV	Frontantrieb	Benzin	Feb 2007	Aug 2010	124130
Honda	Crosstour i	3.5 4WD	Schrägheck	Allrad	Benzin	Sep 2012	-	58323
Honda	Cr-V i	2.0 16V 4WD	SUV	Allrad	Benzin	Jan 1999	Feb 2002	13180
Honda	Cr-V ii	2	SUV	Allrad	Benzin	Sep 2001	Mar 2007	16573
Honda	Cr-V ii	2.2 Ctdi	SUV	Allrad	Diesel	Feb 2005	Sep 2006	18473
Honda	Cr-V iii	2.0 I-vtec	SUV	Frontantrieb	Benzin	Jan 2007	Jun 2012	57748
Honda	Cr-V iii	2.2 I-dtec 4WD	SUV	Allrad	Diesel	Jan 2007	Jun 2012	34931
Honda	Cr-V iii	2.4 I-vtec 4WD	SUV	Allrad	Benzin	Apr 2007	Dec 2012	57197
Honda	Cr-V iv	1.6 I-dtec	SUV	Frontantrieb	Diesel	Oct 2013	Aug 2018	35422
Honda	Cr-V iv	1.6 I-dtec 4WD	SUV	Allrad	Diesel	Feb 2015	Aug 2018	112038
Honda	Cr-V iv	2.0 AWD	SUV	Allrad	Benzin	Oct 2012	Dec 2018	56765
Honda	Cr-V iv	2.0 Ivtec	SUV	Frontantrieb	Benzin	Oct 2012	Dec 2018	56243
Honda	Cr-V iv	2.2 I-dtec 4WD	SUV	Allrad	Diesel	Nov 2012	May 2015	153051
Honda	Cr-V v	1.5 AWD	SUV	Allrad	Benzin	Dec 2016	-	125265
Honda	Cr-V v	2.0 E-cvt Hybrid AWD	SUV	Allrad	Benzin/Elektro	Feb 2019	Aug 2023	143743
Honda	Cr-V vi	E:hev	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	155906
Honda	Cr-V vi	E:hev	SUV	Frontantrieb	Benzin/Elektro	May 2025	-	802282
Honda	Cr-V vi	E:hev AWD	SUV	Allrad	Benzin/Elektro	Apr 2023	-	155907
Honda	Cr-V vi	E:hev AWD	SUV	Allrad	Benzin/Elektro	May 2025	-	802283
Honda	Cr-V vi	E:phev	SUV	Frontantrieb	Benzin/Elektro	Apr 2023	-	155908
Honda	Crx i	1.3	Coupe	Frontantrieb	Benzin	Oct 1983	Oct 1987	14662
Honda	Crx ii	1.6 I 16V	Coupe	Frontantrieb	Benzin	Oct 1987	Dec 1991	17067
Honda	Cr-Z	1.5 IMA	Coupe	Frontantrieb	Benzin/Elektro	Nov 2012	-	58815
Honda	Cr-Z	1.5 IMA	Coupe	Frontantrieb	Benzin/Elektro	Sep 2010	Dec 2013	107258
Honda	E:ny1	Electric	SUV	Frontantrieb	Elektro	Mar 2023	-	154952
Honda	Fr-V	1.7	Großraumlimousine	Frontantrieb	Benzin	Aug 2004	Sep 2006	18472
Honda	Fr-V	2	Großraumlimousine	Frontantrieb	Benzin	Feb 2005	Dec 2006	18471
Honda	Fr-V	2.2 I Ctdi	Großraumlimousine	Frontantrieb	Diesel	Jul 2005	Dec 2009	18231
Honda	Hr-V	1.5	SUV	Frontantrieb	Benzin	Aug 2015	-	116068
Honda	Hr-V	1.5 Ehev	SUV	Frontantrieb	Benzin/Elektro	Sep 2021	-	146819
Honda	Hr-V	1.6 16V	SUV	Frontantrieb	Benzin	Mar 1999	-	14595
Honda	Hr-V	1.6 16V 4WD	SUV	Allrad	Benzin	Mar 1999	-	11121
Honda	Hr-V	1.6 16V 4WD	SUV	Allrad	Benzin	Oct 1999	Sep 2005	14594
Honda	Hr-V	1.6 I-dtec	SUV	Frontantrieb	Diesel	Aug 2015	-	116067
Honda	Insight	1.0 IMA	Coupe	Frontantrieb	Benzin/Elektro	Apr 2000	Dec 2006	14410
Honda	Insight	1.3 IMA	Schrägheck	Frontantrieb	Benzin/Elektro	Apr 2009	Dec 2013	56184
Honda	Integra	1.5	Schrägheck	Frontantrieb	Benzin	Oct 1985	Aug 1989	17832
Honda	Integra	1.6	Schrägheck	Frontantrieb	Benzin	Mar 1986	Aug 1989	17833
Honda	Integra	1.8	Stufenheck	Frontantrieb	Benzin	Sep 1993	Aug 2001	124452
Honda	Integra	2	Coupe	Frontantrieb	Benzin	Feb 2002	Nov 2008	18564
Honda	Integra	1.8 Type-r	Coupe	Frontantrieb	Benzin	Nov 1997	Oct 2001	11059
Honda	Integra	1.8 Type-r	Coupe	Frontantrieb	Benzin	Sep 1993	Aug 2001	57345


--- Round 1 / 首次发送 ---
## 更新点

* 复用 4 个历史尺寸组：Accord VIII Tourer 改款前/后、Civic VI Fastback、Civic VIII 常规 Sedan。
* 首次创建 5 个尺寸组：Civic IX Sedan、Civic IX Hatchback 改款前/后、Civic Type R FK2、Civic VIII Sedan IMA。
* Civic IX 普通五门改款前后外廓由 `4300×1770×1440` 变为 `4370×1770×1470`；FK2 Type R 为独立宽体外廓 `4390×1878×1466`。([汽车数据网][1])
* Ktype `13927` 的 2.2 i-DTEC 只关联改款前组：改款前资料明确包含 2.2 i-DTEC，而改款后普通 Hatchback 资料未包含该动力，不因输入结束年月机械创建改款后分支。([汽车数据网][1])
* Civic VIII IMA 的 `4488×1753×1430` 与常规 1.6 Sedan 的 `4545×1750×1435` 不同，独立建组，未错误复用常规 Sedan。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：17
* READY 映射行：21
* 待闭合 Ktype：83
* READY 映射已引用尺寸组：9
* 本轮首次创建尺寸组：5
* 本轮复用历史尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34929_prefl	34929	Wagon	Accord VIII Tourer		5	EU-HONDA-ACCORD-VIII-TOURER-WAGON-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门Tourer外廓。	READY
34929_facelift	34929	Wagon	Accord VIII Tourer facelift		5	EU-HONDA-ACCORD-VIII-TOURER-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门Tourer外廓。	READY
121249	121249	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
57475	57475	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
107634	107634	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
13918_prefl	13918	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
13918_facelift	13918	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
58791_prefl	58791	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
58791_facelift	58791	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
13926_prefl	13926	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
13926_facelift	13926	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
116064	116064	Hatchback	Civic IX Type R	FK2	5	EU-HONDA-CIVIC-TYPE-R-FK2-HATCHBACK-5D-01	HIGH	FK2宽体五门外廓。	READY
13927	13927	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	2.2 i-DTEC对应改款前五门外廓。	READY
7816	7816	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7817	7817	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
11506	11506	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7818	7818	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7819	7819	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
54964	54964	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
55936	55936	Sedan	Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-4D-01	HIGH	常规四门Sedan外廓。	READY
17513	17513	Sedan	Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-IMA-4D-01	HIGH	IMA四门外廓与常规Sedan尺寸不同，独立建组。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-IX-SEDAN-4D-01	4545	1755	1435	Auto-Data Honda Civic IX Sedan	https://www.auto-data.net/en/honda-civic-ix-sedan-generation-3926
EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	4300	1770	1440	Auto-Data Honda Civic IX Hatchback	https://www.auto-data.net/en/honda-civic-ix-hatchback-generation-3837
EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	4370	1770	1470	Auto-Data Honda Civic IX Hatchback facelift 2014	https://www.auto-data.net/en/honda-civic-ix-hatchback-facelift-2014-generation-4482
EU-HONDA-CIVIC-TYPE-R-FK2-HATCHBACK-5D-01	4390	1878	1466	Auto-Data Honda Civic Type R FK2	https://www.auto-data.net/en/honda-civic-type-r-fk2-2.0-310hp-30245
EU-HONDA-CIVIC-VIII-SEDAN-IMA-4D-01	4488	1753	1430	Auto-Data Honda Civic VIII Sedan 1.3 i-DSi IMA	https://www.auto-data.net/en/honda-civic-viii-sedan-1.3-i-dsi-ima-110hp-hybrid-e-cvt-12214
```

上述新建组的车身形式、门数和三维分别由对应 Auto-Data 直接车型页或代际页闭合。([汽车数据网][3])

## 下一步优先处理

1. 闭合 Civic IX Tourer 改款后高度；当前来源已确认长度、车宽及不含后视镜口径，但页面未提供高度，暂不创建残缺尺寸组。([汽车数据网][4])
2. 处理 Civic III、IV、V、VI Sedan/Coupe/Aerodeck 和 Civic VII 各车身，优先按代际与门数批量建组。
3. 纠正 CRX II 的长度分支：资料同时出现 `3755 mm` 与 `3815 mm`，必须先确定 Ktype `17067` 覆盖的具体年份/外廓，不能直接复用单一组。([汽车数据网][5])
4. 随后处理 CR-V 各代；CR-V III 改款前后长度不同，必须按改款及市场版本分组，不能继续复用单一 `4530 mm` 组。([汽车数据网][6])

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-civic-ix-hatchback-generation-3837?utm_source=chatgpt.com "Honda Civic IX Hatchback /2012, 2013, 2014/ specs, Fuel ..."
[2]: https://www.auto-data.net/en/honda-civic-viii-sedan-1.6-i-vtec-125hp-17146?utm_source=chatgpt.com "Honda Civic VIII Sedan 1.6 i-VTEC (125 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/honda-civic-ix-sedan-generation-3926?utm_source=chatgpt.com "Honda Civic IX Sedan | Technical Specs, Fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/honda-civic-ix-tourer-facelift-2014-1.6-i-dtec-120hp-21993 "Honda Civic IX Tourer (facelift 2014) 1.6 i-DTEC (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/honda-crx-model-1327?utm_source=chatgpt.com "Honda CRX | Technical Specs, Fuel consumption, Dimensions"
[6]: https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-automatic-12336?utm_source=chatgpt.com "Honda CR-V III 2.0 i-VTEC (150 Hp) AWD Automatic"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Civic IX Tourer 改款前后两套外廓，并将两个跨改款 Ktype 各拆成 `prefl`、`facelift` 两行。
* 新建 Civic VI Sedan、Civic VI Coupe、Civic VII Sedan、Civic V Sedan 和 Civic V Hatchback 尺寸组；同车身不同发动机直接复用。Civic VI Coupe 的三个 Ktype 分别确认到 EJ6、EM1 车身代码，但三维一致，因此不重复建组。([本田新闻][1])
* Civic VII 的 ES4、ES5 四门 Sedan 共用相同外廓；Civic V 的 Sedan 与三门 Hatchback 分别独立建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：27
* PENDING Ktype：73
* READY 映射行：33
* 已确认尺寸组：16
* 本轮新增 READY Ktype：10
* 本轮新增映射行：12
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100487_prefl	100487	Wagon	Civic IX Tourer		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门旅行车外廓。	READY
100487_facelift	100487	Wagon	Civic IX Tourer facelift		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门旅行车外廓。	READY
100489_prefl	100489	Wagon	Civic IX Tourer		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门旅行车外廓。	READY
100489_facelift	100489	Wagon	Civic IX Tourer facelift		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门旅行车外廓。	READY
14901	14901	Sedan	Civic VI Sedan	EK1	4	EU-HONDA-CIVIC-VI-SEDAN-4D-01	HIGH	EK1四门Sedan外廓。	READY
17525	17525	Coupe	Civic VI Coupe	EJ6	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EJ6双门Coupe外廓。	READY
17524	17524	Coupe	Civic VI Coupe	EM1	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EM1双门Coupe外廓。	READY
18832	18832	Coupe	Civic VI Coupe	EM1	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EM1高功率双门Coupe外廓。	READY
18468	18468	Sedan	Civic VII Sedan	ES4	4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	HIGH	ES4四门Sedan外廓。	READY
18469	18469	Sedan	Civic VII Sedan	ES5	4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	HIGH	ES5四门Sedan外廓。	READY
55932	55932	Sedan	Civic V Sedan		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
18020	18020	Hatchback	Civic V Hatchback	EG4	3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	EG4三门Hatchback外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	4535	1770	1480	Honda Europe 2014 Civic Tourer press release	https://hondanews.eu/eu/lt/cars/media/pressreleases/35274/2014-honda-civic-tourer
EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	4590	1770	1480	Auto-Data Honda Civic IX Tourer facelift 2014; Automobile Dimension Honda Civic Tourer 2015	https://www.auto-data.net/en/honda-civic-ix-tourer-facelift-2014-generation-4553;https://www.automobiledimension.com/model/honda/civic-tourer
EU-HONDA-CIVIC-VI-SEDAN-4D-01	4460	1695	1390	Auto-Data Honda Civic VI 1.6 i Vtec; Automoli Honda Civic VI	https://www.auto-data.net/en/honda-civic-vi-1.6-i-vtec-125hp-12262;https://www.automoli.com/gb/vehicles/honda/civic/civic-vi-2632/
EU-HONDA-CIVIC-VI-COUPE-2D-01	4460	1695	1375	Auto-Data Honda Civic VI Coupe	https://www.auto-data.net/en/honda-civic-vi-coupe-generation-2629
EU-HONDA-CIVIC-VII-SEDAN-4D-01	4458	1715	1440	Auto-Data Honda Civic VII Sedan	https://www.auto-data.net/en/honda-civic-vii-sedan-generation-2626
EU-HONDA-CIVIC-V-SEDAN-4D-01	4405	1695	1375	Auto-Data Honda Civic V 1.5i 16V Sedan	https://www.auto-data.net/en/honda-civic-v-1.5i-16v-90hp-12272
EU-HONDA-CIVIC-V-HATCHBACK-3D-01	4080	1695	1345	Auto-Data Honda Civic V Hatchback 1.5i 16V	https://www.auto-data.net/en/honda-civic-v-hatchback-1.5i-16v-90hp-12267
```

## 下一步优先处理

1. 解决 Civic VI Aerodeck `54963` 的高度冲突：现有来源分别给出 `1410 mm` 和 `1440 mm`，未闭合前不创建尺寸组。([汽车数据网][3])
2. 处理 Civic VII 剩余 Sedan `59695`、`16103`、`17802`，分别核对 1.5、1.7 和 IMA 是否存在市场或外廓差异。
3. 按三门与五门边界批量处理 Civic VII Hatchback，再推进 Civic III、Civic IV 的 Sedan/Shuttle 外廓。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/lt/cars/media/pressreleases/35274/2014-honda-civic-tourer?utm_source=chatgpt.com "2014 HONDA Civic Tourer"
[2]: https://www.auto-data.net/en/honda-civic-vii-sedan-generation-2626 "Honda Civic VII Sedan | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/honda-civic-vi-wagon-1.6-16v-116hp-12237?utm_source=chatgpt.com "Specs of Honda Civic VI Wagon 1.6 16V (116 Hp) /1998, ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 修正 Civic VII 四门 Sedan 的市场外廓边界：Ktype `18468`、`18469` 改指 Honda 欧洲规格的 `4480×1715×1440` 新尺寸组；不覆盖已有 `4458×1715×1440` 尺寸组。
* Civic VII IMA 与 Coupe 分别闭合为独立尺寸组。
* Civic VII Hatchback 按三门、五门改款前和五门改款后三种外廓批量闭合。Honda 官方资料确认三门为 `4140×1695×1440`，五门改款前为 `4285×1695×1495`，2004 年改款后五门宽度增至 `1715 mm`。([本田新闻][1])
* Civic VI Aerodeck 的高度冲突已消除，采用直接车型页的 `4425×1695×1410`。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：37
* PENDING Ktype：63
* READY 映射行：52
* 已引用尺寸组：23
* 本轮新增 READY Ktype：10
* 本轮修改既有 READY Ktype：2
* 本轮首次创建/纠正尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
54963	54963	Wagon	Civic VI Aerodeck	MC1	5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH	MC1五门Aerodeck外廓。	READY
18468	18468	Sedan	Civic VII Sedan	ES4	4	EU-HONDA-CIVIC-VII-SEDAN-4D-02	HIGH	按Honda欧洲四门规格修正尺寸组关联。	READY
59695	59695	Sedan	Civic VII Sedan	ES8	4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	MEDIUM	ES8四门Sedan外廓。	READY
18469	18469	Sedan	Civic VII Sedan	ES5	4	EU-HONDA-CIVIC-VII-SEDAN-4D-02	HIGH	按Honda欧洲四门规格修正尺寸组关联。	READY
16103	16103	Sedan	Civic VII Sedan		4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
17802	17802	Sedan	Civic VII Sedan IMA		4	EU-HONDA-CIVIC-VII-SEDAN-IMA-4D-01	HIGH	IMA四门车身高度与常规Sedan不同。	READY
15527	15527	Coupe	Civic VII Coupe	EM2	2	EU-HONDA-CIVIC-VII-COUPE-2D-01	HIGH	EM2双门Coupe外廓。	READY
15934_3dr	15934	Hatchback	Civic VII Hatchback	EP1	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP1三门外廓。	READY
15934_5dr_prefl	15934	Hatchback	Civic VII Hatchback	EU7	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU7五门改款前外廓。	READY
15934_5dr_facelift	15934	Hatchback	Civic VII Hatchback facelift	EU7	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU7五门改款后外廓。	READY
15525_3dr	15525	Hatchback	Civic VII Hatchback	EP1	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP1三门外廓。	READY
15525_5dr_prefl	15525	Hatchback	Civic VII Hatchback		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU5/EU7五门改款前外廓。	READY
15525_5dr_facelift	15525	Hatchback	Civic VII Hatchback facelift		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU5/EU7五门改款后外廓。	READY
15526_3dr	15526	Hatchback	Civic VII Hatchback	EP2	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP2三门外廓。	READY
15526_5dr_prefl	15526	Hatchback	Civic VII Hatchback		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU6/EU8五门改款前外廓。	READY
15526_5dr_facelift	15526	Hatchback	Civic VII Hatchback facelift		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU6/EU8五门改款后外廓。	READY
16522_3dr	16522	Hatchback	Civic VII Hatchback	EP4	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP4三门柴油外廓。	READY
16522_5dr_prefl	16522	Hatchback	Civic VII Hatchback	EU9	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU9五门改款前外廓。	READY
16522_5dr_facelift	16522	Hatchback	Civic VII Hatchback facelift	EU9	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU9五门改款后外廓。	READY
18063_5dr_prefl	18063	Hatchback	Civic VII Hatchback	EV1	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EV1五门2.0 Sport改款前外廓。	READY
18063_5dr_facelift	18063	Hatchback	Civic VII Hatchback facelift	EV1	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EV1五门2.0 Sport改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	4425	1695	1410	Auto-Data Honda Civic VI Wagon 1.6 16V	https://www.auto-data.net/en/honda-civic-vi-wagon-1.6-16v-116hp-12237
EU-HONDA-CIVIC-VII-SEDAN-4D-02	4480	1715	1440	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-SEDAN-IMA-4D-01	4480	1715	1430	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-COUPE-2D-01	4438	1695	1399	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	4140	1695	1440	Honda Europe Civic 01 3 Door	https://hondanews.eu/eu/en/cars/media/pressreleases/34356/civic-01-3-door
EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	4285	1695	1495	Honda Europe Civic 01 5 Door	https://hondanews.eu/eu/en/cars/media/pressreleases/34353/civic-01-5-door
EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	4285	1715	1495	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
```

## 下一步优先处理

1. 按代际批量闭合 Civic III、Civic IV Sedan、Hatchback 和 Shuttle。
2. 处理 Civic X、Civic XI 的普通 Hatchback、Sedan 与 Type R 宽体外廓。
3. 随后集中处理 CR-V I 至 VI，优先识别改款、市场版本和五座/七座外廓差异。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/lv/cars/media/pressreleases/34356/civic-01-3-door?utm_source=chatgpt.com "Civic 01 - 3 Door"
[2]: https://www.auto-data.net/en/honda-civic-vi-wagon-1.6-16v-116hp-12237?utm_source=chatgpt.com "Specs of Honda Civic VI Wagon 1.6 16V (116 Hp) /1998, ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Civic III 四门 Sedan 单一外廓，5 个发动机 Ktype 共用同一尺寸组。
* 闭合 Civic IV 的四门 Sedan、三门 Hatchback、五门 Shuttle 三种物理外廓；四驱版本未产生额外尺寸组。具体匹配车型的 Civic IV Sedan 均为 `4230×1690×1360`，避免采用代际汇总页中不对应本批版本的尺寸。([汽车数据网][1])
* 闭合 Civic XI 土耳其市场 LPG Sedan、欧洲 e:HEV Hatchback 和 FL5 Type R 三种外廓。Honda 土耳其官方资料明确 LPG Sedan 为 `4677×1802×1407`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：50
* PENDING Ktype：50
* READY 映射行：65
* 已确认尺寸组：30
* 本轮新增 READY Ktype：13
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14663	14663	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14664	14664	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14665	14665	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14667	14667	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14666	14666	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
17634	17634	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
18019	18019	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
55637	55637	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四驱未改变四门Sedan外廓。	READY
18018	18018	Hatchback	Civic IV Hatchback		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH	三门Hatchback外廓。	READY
18864	18864	Wagon	Civic IV Shuttle		5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-5D-01	MEDIUM	五门Shuttle外廓。	READY
152669	152669	Sedan	Civic XI Sedan		4	EU-HONDA-CIVIC-XI-SEDAN-4D-01	HIGH	土耳其市场四门LPG Sedan外廓。	READY
149700	149700	Hatchback	Civic XI	FL4	5	EU-HONDA-CIVIC-XI-HATCHBACK-5D-01	HIGH	FL4五门e:HEV外廓。	READY
149691	149691	Hatchback	Civic XI Type R	FL5	5	EU-HONDA-CIVIC-TYPE-R-FL5-HATCHBACK-5D-01	HIGH	FL5宽体五门Type R外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-III-SEDAN-4D-01	4145	1630	1385	DrivePlace Honda Civic III 1.2 Sedan	https://honda.drive.place/civic/iii/group_sedan/93411
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4230	1690	1360	Auto-Data Honda Civic IV 1.5i 16V	https://www.auto-data.net/en/honda-civic-iv-1.5i-16v-90hp-12276
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330	Auto-Data Honda Civic IV Hatchback 1.5 i 16V	https://www.auto-data.net/en/honda-civic-iv-hatchback-1.5-i-16v-90hp-12286
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-5D-01	4105	1690	1515	Auto-Data Honda Civic IV Shuttle	https://www.auto-data.net/en/honda-civic-iv-shuttle-generation-2637
EU-HONDA-CIVIC-XI-SEDAN-4D-01	4677	1802	1407	Honda Turkey New Civic Sedan official brochure	https://www.honda.com.tr/assets/files/yeni-civic-sedan-SVcS3.pdf
EU-HONDA-CIVIC-XI-HATCHBACK-5D-01	4551	1802	1408	Honda Europe 2022 Civic e:HEV specifications	https://hondanews.eu/gb/en/cars/media/documenttext/412439/2022-honda-civic-ehev-72
EU-HONDA-CIVIC-TYPE-R-FL5-HATCHBACK-5D-01	4594	1890	1401	Honda Europe 2023 Civic Type R specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/429984/2023-honda-civic-type-r
```

## 下一步优先处理

1. 闭合 Civic X 普通 Hatchback、Sedan 与 FK8 Type R，并判断跨 2019 改款的 Ktype 是否需要派生。
2. 处理 City、Concerto、Crossroad 和 Crosstour。
3. 集中处理 CR-V I 至 VI，按代际及改款外廓批量建组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-civic-iv-1.4-90hp-12275 "Honda Civic IV 1.4 (90 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Civic X 普通 Hatchback 和 Sedan 的改款前后外廓尺寸不同，相关 Ktype 拆分为 `prefl`、`facelift`；FK8 Type R 改款前后外廓尺寸不变，复用单一尺寸组。([本田新闻][1])
* 闭合 Concerto 四门 Sedan、五门 Hatchback 两套外廓。([汽车数据网][2])
* 闭合 Crossroad RT3 两驱五门 SUV，以及 Crosstour TF2 四驱改款车型。([本田汽车][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：59
* PENDING Ktype：41
* READY 映射行：77
* 已确认尺寸组：39
* 本轮新增 READY Ktype：9
* 本轮新增映射行：12
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126524_prefl	126524	Hatchback	Civic X Hatchback		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
126524_facelift	126524	Hatchback	Civic X Hatchback facelift		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
126522_prefl	126522	Hatchback	Civic X Hatchback		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
126522_facelift	126522	Hatchback	Civic X Hatchback facelift		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
126886_prefl	126886	Sedan	Civic X Sedan	FC1	4	EU-HONDA-CIVIC-X-SEDAN-4D-PREFL-01	HIGH	FC1四门改款前外廓。	READY
126886_facelift	126886	Sedan	Civic X Sedan facelift	FC1	4	EU-HONDA-CIVIC-X-SEDAN-4D-FACELIFT-01	HIGH	FC1四门改款后外廓。	READY
127817	127817	Hatchback	Civic X Type R	FK8	5	EU-HONDA-CIVIC-TYPE-R-FK8-HATCHBACK-5D-01	HIGH	FK8宽体五门外廓。	READY
14144	14144	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH	HW四门Sedan外廓。	READY
18833	18833	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门Hatchback外廓。	READY
18834	18834	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH	HW四门Sedan外廓。	READY
124130	124130	SUV	Crossroad II	RT3	5	EU-HONDA-CROSSROAD-II-RT3-SUV-5D-01	HIGH	RT3两驱五门SUV外廓。	READY
58323	58323	Hatchback	Crosstour I facelift	TF2	5	EU-HONDA-CROSSTOUR-I-FACELIFT-HATCHBACK-5D-01	HIGH	TF2四驱五门改款外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	4497	1800	1421	Honda Europe Civic 10th generation Paris Motor Show press pack	https://hondanews.eu/gb/en/cars/media/pressreleases/77994/civic-10th-generation-press-pack-paris-motor-show
EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	4518	1799	1434	Honda Europe 2021 Honda Civic specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/327918/2021-honda-civic
EU-HONDA-CIVIC-X-SEDAN-4D-PREFL-01	4648	1799	1416	Honda Europe 2017 Honda Civic Sedan specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/107785/2017-honda-civic-sedan11
EU-HONDA-CIVIC-X-SEDAN-4D-FACELIFT-01	4658	1799	1416	Honda Europe 2021 Honda Civic specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/327918/2021-honda-civic
EU-HONDA-CIVIC-TYPE-R-FK8-HATCHBACK-5D-01	4557	1877	1434	Honda Europe 2020 Honda Civic Type R specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/308995/2020-honda-civic-type-r
EU-HONDA-CONCERTO-HW-SEDAN-4D-01	4415	1690	1395	Auto-Data Honda Concerto HW	https://www.auto-data.net/en/honda-concerto-model-1312
EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	4265	1690	1395	Auto-Data Honda Concerto Hatch HW	https://www.auto-data.net/en/honda-concerto-model-1312
EU-HONDA-CROSSROAD-II-RT3-SUV-5D-01	4285	1755	1670	Honda Crossroad official archive specifications	https://www.honda.co.jp/auto-archive/crossroad/2010/grade-data/
EU-HONDA-CROSSTOUR-I-FACELIFT-HATCHBACK-5D-01	4994	1898	1561	Auto-Data Honda Crosstour facelift 3.5 V6 4WD	https://www.auto-data.net/en/honda-crosstour-facelift-2012-3.5-v6-278hp-4wd-automatic-46152
```

## 下一步优先处理

1. 解决 City `34515` 跨代际结束时间边界，避免误把 2008—2013 与 2013 年后新一代外廓合并。
2. 批量闭合 CR-V I、II、III，并按 CR-V III 改款前后长度差异拆分。
3. 继续处理 CR-V IV、V、VI，随后处理 CRX、CR-Z、Insight 与 Integra。

推进信号：CONTINUE

[1]: https://hondanews.eu/gb/en/cars/media/pressreleases/77994/civic-10th-generation-press-pack-paris-motor-show?utm_source=chatgpt.com "Civic 10th generation press pack – Paris Motor Show"
[2]: https://www.auto-data.net/en/honda-concerto-model-1312?utm_source=chatgpt.com "Honda Concerto | Technical Specs, Fuel consumption ..."
[3]: https://www.honda.co.jp/factbook/auto/CROSSROAD/200702/15.html?utm_source=chatgpt.com "CROSSROAD"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 City V（GM2）改款前后两套 Sedan 外廓：改款后保险杠使长度由 `4410 mm` 增至 `4430 mm`，宽度和高度不变。([CarExpert NZ][1])
* 闭合 CR-V I 1999 年后期外廓 `4520×1750×1675 mm`。([汽车数据网][2])
* CR-V III 按欧洲 2.0/2.2 与北美规格 2.4 分开处理；改款前后长度及部分高度不同，未错误合并。([汽车数据网][3])
* CR-V II 的 2.0 与 2.2 来源仍存在 `4555 mm`、`4535 mm` 长度差异，本轮不建立猜测性尺寸组。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* PENDING Ktype：36
* READY 映射行：85
* 已确认尺寸组：46
* 本轮新增 READY Ktype：5
* 本轮新增映射行：8
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34515_prefl	34515	Sedan	City V	GM2	4	EU-HONDA-CITY-V-SEDAN-4D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前四门外廓。	READY
34515_facelift	34515	Sedan	City V facelift	GM2	4	EU-HONDA-CITY-V-SEDAN-4D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后四门外廓。	READY
13180	13180	SUV	CR-V I	RD1	5	EU-HONDA-CR-V-I-RD1-SUV-5D-01	HIGH	RD1五门四驱SUV外廓。	READY
57748_prefl	57748	SUV	CR-V III		5	EU-HONDA-CR-V-III-EU-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分欧洲规格改款前外廓。	READY
57748_facelift	57748	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分欧洲规格改款后外廓。	READY
34931	34931	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	HIGH	2.2 i-DTEC对应改款后欧洲规格外廓。	READY
57197_prefl	57197	SUV	CR-V III		5	EU-HONDA-CR-V-III-24-SUV-5D-PREFL-01	HIGH	2.4四驱改款前市场规格外廓。	READY
57197_facelift	57197	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-24-SUV-5D-FACELIFT-01	HIGH	2.4四驱改款后市场规格外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CITY-V-SEDAN-4D-PREFL-01	4410	1695	1470	CarExpert 2009 Honda City 1.5 E specifications	https://www.carexpert.co.nz/honda/honda-city/2009-e-1-5l-sedan-fwd-petrol-automatic-joskw85f20090715
EU-HONDA-CITY-V-SEDAN-4D-FACELIFT-01	4430	1695	1470	CarExpert 2012 Honda City VTi specifications	https://www.carexpert.com.au/honda/city/2012-vti-1-5l-sedan-fwd-petrol-manual-jomgwkwf20120502
EU-HONDA-CR-V-I-RD1-SUV-5D-01	4520	1750	1675	Auto-Data Honda CR-V I RD 2.0 16V 1999	https://www.auto-data.net/en/honda-cr-v-i-rd-2.0-16v-147hp-automatic-29215
EU-HONDA-CR-V-III-EU-SUV-5D-PREFL-01	4530	1820	1675	Auto-Data Honda CR-V III 2.0 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-automatic-12336
EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	4574	1820	1675	Auto-Data Honda CR-V III facelift 2.0 i-VTEC; Auto-Data Honda CR-V III facelift 2.2 i-DTEC	https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.0-i-vtec-150hp-awd-17151;https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.2-i-dtec-150hp-awd-automatic-17154
EU-HONDA-CR-V-III-24-SUV-5D-PREFL-01	4519	1820	1679	Auto-Data Honda CR-V III 2.4 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.4-i-vtec-166hp-awd-automatic-12338
EU-HONDA-CR-V-III-24-SUV-5D-FACELIFT-01	4555	1820	1680	Auto-Data Honda CR-V III facelift 2.4 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.4-i-vtec-180hp-awd-automatic-50949
```

## 下一步优先处理

1. 用同一欧洲市场口径解决 CR-V II 2.0 与 2.2 的长度冲突。
2. 批量闭合 CR-V IV、V、VI，重点检查 CR-V IV 改款前后及 CR-V VI 不同市场高度。
3. 随后处理 CRX、CR-Z、Insight、Integra 与 HR-V。

推进信号：CONTINUE

[1]: https://www.carexpert.co.nz/honda/honda-city/2009-e-1-5l-sedan-fwd-petrol-automatic-joskw85f20090715?utm_source=chatgpt.com "2009 Honda City E Price and Specifications"
[2]: https://www.auto-data.net/en/honda-cr-v-i-rd-2.0-16v-147hp-automatic-29215?utm_source=chatgpt.com "Honda CR-V I (RD) 2.0 16V (147 Hp) Automatic /SUV 1999"
[3]: https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-automatic-12336?utm_source=chatgpt.com "Honda CR-V III 2.0 i-VTEC (150 Hp) AWD Automatic"
[4]: https://www.auto-data.net/en/honda-cr-v-ii-2.0-16v-150hp-12339?utm_source=chatgpt.com "Honda CR-V II 2.0 16V (150 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 CR-V II 改款前后两套外廓。Ktype `16573` 跨越改款，拆为两行；柴油 Ktype `18473` 仅对应改款后外廓。Honda 欧洲资料给出改款前 `4555×1780×1710 mm`、改款后 `4635×1785×1710 mm`。([本田新闻][1])
* 闭合 CR-V IV 改款前后两套外廓：改款前 `4570×1820×1685 mm`，改款后 `4605×1820×1685 mm`。跨改款 Ktype 均按物理外廓拆分；2.2 i-DTEC 仅关联改款前组。([本田新闻][2])
* CR-V V 本批两个 AWD Ktype 共用 `4600×1855×1689 mm` 外廓，不因汽油和混动动力不同重复建组。([本田新闻][3])
* CR-V VI 按驱动与底盘高度拆成 e:HEV FWD、e:HEV AWD、e:PHEV FWD 三组；2025 年新增 Ktype 直接复用对应稳定组。Honda 规格明确区分不含后视镜宽度与含镜宽度。([live.dealer-asset.co][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* PENDING Ktype：22
* READY 映射行：103
* 已确认尺寸组：54
* 本轮新增 READY Ktype：14
* 本轮新增映射行：18
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16573_prefl	16573	SUV	CR-V II		5	EU-HONDA-CR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
16573_facelift	16573	SUV	CR-V II facelift		5	EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
18473	18473	SUV	CR-V II facelift	RD9	5	EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	HIGH	RD9柴油改款后五门外廓。	READY
35422_prefl	35422	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
35422_facelift	35422	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
112038	112038	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	改款后五门AWD外廓。	READY
56765_prefl	56765	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
56765_facelift	56765	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
56243_prefl	56243	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
56243_facelift	56243	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
153051	153051	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	2.2 i-DTEC对应改款前五门外廓。	READY
125265	125265	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-AWD-5D-01	HIGH	五门AWD外廓。	READY
143743	143743	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-AWD-5D-01	HIGH	混动AWD与同代汽油AWD共用外廓。	READY
155906	155906	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	HIGH	e:HEV前驱五门外廓。	READY
802282	802282	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	HIGH	2025年e:HEV前驱版本复用同一外廓。	READY
155907	155907	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	HIGH	e:HEV四驱五门外廓。	READY
802283	802283	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	HIGH	2025年e:HEV四驱版本复用同一外廓。	READY
155908	155908	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EPHEV-FWD-SUV-5D-01	HIGH	e:PHEV前驱底盘高度不同，独立建组。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CR-V-II-SUV-5D-PREFL-01	4555	1780	1710	Honda Europe CR-V 02 official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34287/cr-v-02
EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	4635	1785	1710	Honda CR-V 2005 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/09/Honda-CR-V-2005-UK.pdf
EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	4570	1820	1685	Honda Europe CR-V 1.6 i-DTEC official specifications	https://hondanews.eu/eu/fi/media/pressreleases/34746/introducing-the-new-sub-120-gkm-cr-v-16-i-dtec
EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	4605	1820	1685	Honda Europe 2015 CR-V specifications; Auto-Data Honda CR-V IV facelift	https://hondanews.eu/eu/en/cars/media/pressreleases/42656/2015-honda-cr-v2;https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-1.6-i-dtec-160hp-awd-21489
EU-HONDA-CR-V-V-SUV-AWD-5D-01	4600	1855	1689	Honda Europe 2018 CR-V specifications; Auto-Data Honda CR-V V 1.5 VTEC Turbo AWD	https://hondanews.eu/pl/pl/cars/media/pressreleases/135747/honda-cr-v-2018;https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-193hp-awd-cvt-34298
EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	4706	1866	1674	Honda 2023 CR-V official press kit; Auto-Data Honda CR-V VI e:HEV FWD	https://hondanews.eu/gb/en/cars/media/pressreleases/453027/2023-honda-cr-v-press-kit-43;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ehev-e-cvt-50279
EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	4706	1866	1684	Honda 2024 CR-V official brochure; Auto-Data Honda CR-V VI e:HEV AWD	https://live.dealer-asset.co/ie33/product/file/Honda24YMCR-VBrochure2024.pdf;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ehev-4wd-e-cvt-50280
EU-HONDA-CR-V-VI-EPHEV-FWD-SUV-5D-01	4706	1866	1673	Honda 2024 CR-V official brochure; Auto-Data Honda CR-V VI e:PHEV	https://live.dealer-asset.co/ie33/product/file/Honda24YMCR-VBrochure2024.pdf;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ephev-e-cvt-50281
```

## 下一步优先处理

1. 批量闭合 e:Ny1、FR-V 和 HR-V，共 10 个剩余 Ktype。
2. 随后处理 CRX、CR-Z、Insight 和 Integra，共 12 个 Ktype。
3. 优先解决 CRX II 长度分支以及 Integra Type R 与普通 Coupe 的外廓边界。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/en/cars/media/pressreleases/34287/cr-v-02?utm_source=chatgpt.com "CR-V 02"
[2]: https://hondanews.eu/eu/fi/media/pressreleases/34746/introducing-the-new-sub-120-gkm-cr-v-16-i-dtec?utm_source=chatgpt.com "INTRODUCING THE NEW SUB-120 G/KM CR-V 1.6 i-DTEC"
[3]: https://hondanews.eu/pl/pl/cars/media/pressreleases/135747/honda-cr-v-2018 "Honda CR-V 2018"
[4]: https://live.dealer-asset.co/ie33/product/file/Honda24YMCR-VBrochure2024.pdf "PowerPoint Presentation"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 e:Ny1 单一五门电动 SUV 外廓。
* FR-V 的 1.7、2.0 与 2.2 i-CTDi 三个 Ktype 共用同一五门 MPV 外廓；发动机差异未重复建组。([本田新闻][1])
* 第一代 HR-V 按三门与五门拆成两套外廓；前驱和四驱本身不触发重复建组。([汽车数据网][2])
* 第二代 HR-V 的两个 Ktype 均跨越 2018 年改款，按改款前后拆分；欧洲普通版本改款后长度增加，宽度和高度保持同一口径。([汽车数据网][3])
* 闭合第三代 HR-V e:HEV 五门外廓。([本田新闻][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* PENDING Ktype：12
* READY 映射行：115
* 已确认尺寸组：61
* 本轮新增 READY Ktype：10
* 本轮新增映射行：12
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
154952	154952	SUV	e:Ny1		5	EU-HONDA-ENY1-ELECTRIC-SUV-5D-01	HIGH	五门电动SUV外廓。	READY
18472	18472	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	五门六座MPV外廓。	READY
18471	18471	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	五门六座MPV外廓。	READY
18231	18231	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	柴油动力未改变五门MPV外廓。	READY
14595	14595	SUV	HR-V I	GH1	3	EU-HONDA-HR-V-I-SUV-3D-01	HIGH	GH1前驱三门外廓。	READY
11121	11121	SUV	HR-V I	GH2	3	EU-HONDA-HR-V-I-SUV-3D-01	HIGH	GH2四驱三门外廓。	READY
14594	14594	SUV	HR-V I	GH4	5	EU-HONDA-HR-V-I-SUV-5D-01	HIGH	GH4四驱五门外廓。	READY
116068_prefl	116068	SUV	HR-V II		5	EU-HONDA-HR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
116068_facelift	116068	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
146819	146819	SUV	HR-V III		5	EU-HONDA-HR-V-III-EHEV-SUV-5D-01	HIGH	e:HEV五门SUV外廓。	READY
116067_prefl	116067	SUV	HR-V II		5	EU-HONDA-HR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
116067_facelift	116067	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-ENY1-ELECTRIC-SUV-5D-01	4387	1790	1584	Honda Europe 2023 Honda e:Ny1 press kit	https://hondanews.eu/gb/en/cars/media/pressreleases/452981/2023-honda-eny1-press-kit-43
EU-HONDA-FR-V-MPV-5D-01	4285	1810	1610	Honda Europe FR-V Summary	https://hondanews.eu/eu/en/cars/media/pressreleases/214/fr-v-summary
EU-HONDA-HR-V-I-SUV-3D-01	4010	1695	1670	Auto-Data Honda HR-V GH 1.6 i 16V 4WD 3-door; Honda Europe Geneva Motor Show 2000	https://www.auto-data.net/en/honda-hr-v-gh-1.6-i-16v-4wd-3-dr-124hp-12347;https://hondanews.eu/eu/lv/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-HR-V-I-SUV-5D-01	4110	1695	1670	Auto-Data Honda HR-V GH 1.6 i 16V 4WD 5-door; Honda Europe Geneva Motor Show 2000	https://www.auto-data.net/en/honda-hr-v-gh-1.6-i-16v-4wd-5-dr-124hp-12349;https://hondanews.eu/eu/lv/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-HR-V-II-SUV-5D-PREFL-01	4294	1772	1605	Auto-Data Honda HR-V II 1.6 i-DTEC; Honda Europe 2015 HR-V specifications	https://www.auto-data.net/en/honda-hr-v-ii-1.6-i-dtec-120hp-22480;https://hondanews.eu/eu/lt/cars/media/pressreleases/56929/2015-honda-hr-v17
EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	4335	1772	1605	Honda Europe 2019 HR-V specifications; Auto-Data Honda HR-V II facelift 1.5 i-VTEC	https://hondanews.eu/eu/lt/cars/media/pressreleases/163240/2019-honda-hr-v46;https://www.auto-data.net/en/honda-hr-v-ii-facelift-2018-1.5-i-vtec-130hp-34799
EU-HONDA-HR-V-III-EHEV-SUV-5D-01	4340	1790	1582	Honda Europe 2021 HR-V e:HEV specifications	https://hondanews.eu/eu/el/cars/media/pressreleases/346733/2021-honda-hr-v-ehev-3
```

## 下一步优先处理

1. 闭合 CRX I、CRX II 与 CR-Z，优先解决 CRX II 不同长度记录对应的具体外廓边界。
2. 处理 Insight I、Insight II。
3. 最后集中闭合 Integra 的 Hatchback、Sedan、普通 Coupe 与 Type R Coupe，消除剩余 12 个 PENDING Ktype。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/en/cars/media/pressreleases/214/fr-v-summary?utm_source=chatgpt.com "FR-V Summary"
[2]: https://www.auto-data.net/en/honda-hr-v-gh-1.6-i-16v-4wd-3-dr-124hp-12347?utm_source=chatgpt.com "Honda HR-V (Gh) 1.6 i 16V 4WD (3 dr) (124 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/honda-hr-v-ii-facelift-2018-1.5-i-vtec-130hp-34799?utm_source=chatgpt.com "Honda HR-V II (facelift 2018) 1.5 i-VTEC (130 Hp)"
[4]: https://hondanews.eu/hu/hu/cars/media/pressreleases/348056/honda-hr-v-ehev-2021-26?utm_source=chatgpt.com "Honda HR-V e:HEV 2021"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* CRX II 的长度分支冲突已消除：Ktype `17067` 对应非 VTEC 1.6 i 16V 三门车型，采用 `3755 mm` 外廓；`3815 mm` 属于其他动力分支，不拆分当前 Ktype。CRX I 同时闭合为 AF 三门外廓。([汽车数据网][1])
* CR-Z 两个 Ktype 的车身边界已明确：`107258` 对应 ZF1 改款前，`58815` 对应 ZF2 改款后，分别建立尺寸组。([AUTODOC][2])
* Insight I Ktype `14410` 闭合为 ZE1 三门双座 Coupe，采用 Honda 欧洲官方三维。([本田新闻][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* PENDING Ktype：7
* READY 映射行：120
* 已确认尺寸组：66
* 本轮新增 READY Ktype：5
* 本轮新增映射行：5
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14662	14662	Coupe	CRX I	AF	3	EU-HONDA-CRX-I-AF-COUPE-3D-01	HIGH	AF三门Coupe外廓。	READY
17067	17067	Coupe	CRX II		3	EU-HONDA-CRX-II-COUPE-3D-01	HIGH	非VTEC 1.6 i 16V三门外廓。	READY
58815	58815	Coupe	CR-Z facelift	ZF2	3	EU-HONDA-CR-Z-ZF2-COUPE-3D-01	HIGH	ZF2改款后三门Coupe外廓。	READY
107258	107258	Coupe	CR-Z	ZF1	3	EU-HONDA-CR-Z-ZF1-COUPE-3D-01	HIGH	ZF1改款前三门Coupe外廓。	READY
14410	14410	Coupe	Insight I	ZE1	3	EU-HONDA-INSIGHT-I-ZE1-COUPE-3D-01	HIGH	ZE1三门双座Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CRX-I-AF-COUPE-3D-01	3675	1625	1290	Auto-Data Honda CRX I 1.3	https://www.auto-data.net/en/honda-crx-i-af-as-1.3-71hp-12378
EU-HONDA-CRX-II-COUPE-3D-01	3755	1675	1270	Auto-Data Honda CRX II 1.6 i 16V	https://www.auto-data.net/en/honda-crx-ii-ed-ee-1.6-i-16v-124hp-12375
EU-HONDA-CR-Z-ZF2-COUPE-3D-01	4075	1740	1395	Auto-Data Honda CR-Z facelift 1.5 i-VTEC IMA	https://www.auto-data.net/en/honda-cr-z-facelift-2012-1.5-i-vtec-137hp-ima-hybrid-56426
EU-HONDA-CR-Z-ZF1-COUPE-3D-01	4080	1740	1395	Auto-Data Honda CR-Z 1.5 i-VTEC IMA	https://www.auto-data.net/en/honda-cr-z-1.5-i-vtec-124hp-ima-hybrid-17149
EU-HONDA-INSIGHT-I-ZE1-COUPE-3D-01	3945	1695	1355	Honda Europe Insight 2000 official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34323/insight-2000
```

## 下一步优先处理

1. 解决 Insight II Ktype `56184` 的改款后高度边界：官方资料中不同配置出现 `1425 mm` 与 `1435 mm`，确认是否构成实际物理分支后再建组，不创建猜测性映射。
2. 集中闭合剩余 6 个 Integra Ktype，依次处理第一代 Hatchback、四门 Sedan、DC5 Coupe 和 DC2 Type R 的车身代码及改款边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-crx-i-af-as-1.3-71hp-12378 "Honda CRX I (AF,AS) 1.3 (71 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-doc.ie/car-parts/brake-disc-back-plate-15099/honda/cr-z/cr-z-zf1/107258-1-5-ima-zf1?srsltid=AfmBOorGyxe0jUFqoLfaXW7Zm5bzNGvproCyXhBdMpfFYu5HJhrx3n8w&utm_source=chatgpt.com "Honda CRZ ZF 1.5 IMA Brake disc backing plate"
[3]: https://hondanews.eu/eu/en/cars/media/pressreleases/34323/insight-2000?utm_source=chatgpt.com "Insight 2000"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6501-6600_ktype_dimension_mapping_final.tsv
- left18448_6501-6600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 最后 7 个 Ktype 已闭合：Insight II 采用 ZE2 五门外廓；Integra 分别按 DA 五门、DB7 四门、DC5 改款前后，以及 DC2 Type R 欧洲版、96 Spec、98 Spec 建立映射。([汽车目录档案][1])
* Accord VIII Tourer 改款前后外廓尺寸一致，已合并为一个稳定尺寸组，删除无必要的重复分支。([汽车数据网][2])
* 已完成机械检查：表头列数正确、`id` 和 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、尺寸与来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* READY 映射行：128
* DIMENSION_GROUP：73
* 全部映射均为 `READY`，数据阶段与机械收尾均已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34929	34929	Wagon	Accord VIII Tourer	CW3	5	EU-HONDA-ACCORD-VIII-TOURER-WAGON-5D-01	HIGH	CW3五门Tourer外廓；改款前后外廓尺寸一致。	READY
34515_prefl	34515	Sedan	City V	GM2	4	EU-HONDA-CITY-V-SEDAN-4D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前四门外廓。	READY
34515_facelift	34515	Sedan	City V facelift	GM2	4	EU-HONDA-CITY-V-SEDAN-4D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后四门外廓。	READY
14663	14663	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14664	14664	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14665	14665	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14667	14667	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
14666	14666	Sedan	Civic III		4	EU-HONDA-CIVIC-III-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
17634	17634	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
18019	18019	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
55637	55637	Sedan	Civic IV		4	EU-HONDA-CIVIC-IV-SEDAN-4D-01	HIGH	四驱未改变四门Sedan外廓。	READY
18018	18018	Hatchback	Civic IV Hatchback		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH	三门Hatchback外廓。	READY
18864	18864	Wagon	Civic IV Shuttle		5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-5D-01	MEDIUM	五门Shuttle外廓。	READY
121249	121249	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
57475	57475	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
107634	107634	Sedan	Civic IX		4	EU-HONDA-CIVIC-IX-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
13918_prefl	13918	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
13918_facelift	13918	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
58791_prefl	58791	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
58791_facelift	58791	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
13926_prefl	13926	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	同一Ktype跨越2014改款，拆分改款前五门外廓。	READY
13926_facelift	13926	Hatchback	Civic IX Hatchback facelift		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	HIGH	同一Ktype跨越2014改款，拆分改款后五门外廓。	READY
116064	116064	Hatchback	Civic IX Type R	FK2	5	EU-HONDA-CIVIC-TYPE-R-FK2-HATCHBACK-5D-01	HIGH	FK2宽体五门外廓。	READY
13927	13927	Hatchback	Civic IX Hatchback		5	EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	HIGH	2.2 i-DTEC对应改款前五门外廓。	READY
100487_prefl	100487	Wagon	Civic IX Tourer		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门旅行车外廓。	READY
100487_facelift	100487	Wagon	Civic IX Tourer facelift		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门旅行车外廓。	READY
100489_prefl	100489	Wagon	Civic IX Tourer		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门旅行车外廓。	READY
100489_facelift	100489	Wagon	Civic IX Tourer facelift		5	EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门旅行车外廓。	READY
55932	55932	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门Sedan外廓。	READY
18020	18020	Hatchback	Civic V Hatchback	EG4	3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	EG4三门Hatchback外廓。	READY
17525	17525	Coupe	Civic VI Coupe	EJ6	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EJ6双门Coupe外廓。	READY
14901	14901	Sedan	Civic VI Sedan	EK1	4	EU-HONDA-CIVIC-VI-SEDAN-4D-01	HIGH	EK1四门Sedan外廓。	READY
17524	17524	Coupe	Civic VI Coupe	EM1	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EM1双门Coupe外廓。	READY
18832	18832	Coupe	Civic VI Coupe	EM1	2	EU-HONDA-CIVIC-VI-COUPE-2D-01	HIGH	EM1高功率双门Coupe外廓。	READY
54963	54963	Wagon	Civic VI Aerodeck	MC1	5	EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	HIGH	MC1五门Aerodeck外廓。	READY
7816	7816	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7817	7817	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
11506	11506	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7818	7818	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
7819	7819	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
54964	54964	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	HIGH	五门Fastback外廓。	READY
18468	18468	Sedan	Civic VII Sedan	ES4	4	EU-HONDA-CIVIC-VII-SEDAN-4D-02	HIGH	按Honda欧洲四门规格修正尺寸组关联。	READY
59695	59695	Sedan	Civic VII Sedan	ES8	4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	MEDIUM	ES8四门Sedan外廓。	READY
18469	18469	Sedan	Civic VII Sedan	ES5	4	EU-HONDA-CIVIC-VII-SEDAN-4D-02	HIGH	按Honda欧洲四门规格修正尺寸组关联。	READY
16103	16103	Sedan	Civic VII Sedan		4	EU-HONDA-CIVIC-VII-SEDAN-4D-01	MEDIUM	四门Sedan外廓。	READY
17802	17802	Sedan	Civic VII Sedan IMA		4	EU-HONDA-CIVIC-VII-SEDAN-IMA-4D-01	HIGH	IMA四门车身高度与常规Sedan不同。	READY
15527	15527	Coupe	Civic VII Coupe	EM2	2	EU-HONDA-CIVIC-VII-COUPE-2D-01	HIGH	EM2双门Coupe外廓。	READY
15934_3dr	15934	Hatchback	Civic VII Hatchback	EP1	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP1三门外廓。	READY
15934_5dr_prefl	15934	Hatchback	Civic VII Hatchback	EU7	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU7五门改款前外廓。	READY
15934_5dr_facelift	15934	Hatchback	Civic VII Hatchback facelift	EU7	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU7五门改款后外廓。	READY
15525_3dr	15525	Hatchback	Civic VII Hatchback	EP1	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP1三门外廓。	READY
15525_5dr_prefl	15525	Hatchback	Civic VII Hatchback		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU5/EU7五门改款前外廓。	READY
15525_5dr_facelift	15525	Hatchback	Civic VII Hatchback facelift		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU5/EU7五门改款后外廓。	READY
15526_3dr	15526	Hatchback	Civic VII Hatchback	EP2	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP2三门外廓。	READY
15526_5dr_prefl	15526	Hatchback	Civic VII Hatchback		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU6/EU8五门改款前外廓。	READY
15526_5dr_facelift	15526	Hatchback	Civic VII Hatchback facelift		5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU6/EU8五门改款后外廓。	READY
16522_3dr	16522	Hatchback	Civic VII Hatchback	EP4	3	EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	HIGH	EP4三门外廓。	READY
16522_5dr_prefl	16522	Hatchback	Civic VII Hatchback	EU9	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EU9五门改款前外廓。	READY
16522_5dr_facelift	16522	Hatchback	Civic VII Hatchback facelift	EU9	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EU9五门改款后外廓。	READY
18063_5dr_prefl	18063	Hatchback	Civic VII Hatchback	EV1	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	HIGH	EV1五门2.0 Sport改款前外廓。	READY
18063_5dr_facelift	18063	Hatchback	Civic VII Hatchback facelift	EV1	5	EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	HIGH	EV1五门2.0 Sport改款后外廓。	READY
55936	55936	Sedan	Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-4D-01	HIGH	常规四门Sedan外廓。	READY
17513	17513	Sedan	Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-IMA-4D-01	HIGH	IMA四门外廓与常规Sedan尺寸不同，独立建组。	READY
126524_prefl	126524	Hatchback	Civic X Hatchback		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
126524_facelift	126524	Hatchback	Civic X Hatchback facelift		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
126522_prefl	126522	Hatchback	Civic X Hatchback		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	HIGH	五门改款前外廓。	READY
126522_facelift	126522	Hatchback	Civic X Hatchback facelift		5	EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	HIGH	五门改款后外廓。	READY
126886_prefl	126886	Sedan	Civic X Sedan	FC1	4	EU-HONDA-CIVIC-X-SEDAN-4D-PREFL-01	HIGH	FC1四门改款前外廓。	READY
126886_facelift	126886	Sedan	Civic X Sedan facelift	FC1	4	EU-HONDA-CIVIC-X-SEDAN-4D-FACELIFT-01	HIGH	FC1四门改款后外廓。	READY
127817	127817	Hatchback	Civic X Type R	FK8	5	EU-HONDA-CIVIC-TYPE-R-FK8-HATCHBACK-5D-01	HIGH	FK8宽体五门外廓。	READY
152669	152669	Sedan	Civic XI Sedan		4	EU-HONDA-CIVIC-XI-SEDAN-4D-01	HIGH	土耳其市场四门LPG Sedan外廓。	READY
149700	149700	Hatchback	Civic XI	FL4	5	EU-HONDA-CIVIC-XI-HATCHBACK-5D-01	HIGH	FL4五门e:HEV外廓。	READY
149691	149691	Hatchback	Civic XI Type R	FL5	5	EU-HONDA-CIVIC-TYPE-R-FL5-HATCHBACK-5D-01	HIGH	FL5宽体五门Type R外廓。	READY
14144	14144	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH	HW四门Sedan外廓。	READY
18833	18833	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门Hatchback外廓。	READY
18834	18834	Sedan	Concerto	HW	4	EU-HONDA-CONCERTO-HW-SEDAN-4D-01	HIGH	HW四门Sedan外廓。	READY
124130	124130	SUV	Crossroad II	RT3	5	EU-HONDA-CROSSROAD-II-RT3-SUV-5D-01	HIGH	RT3两驱五门SUV外廓。	READY
58323	58323	Hatchback	Crosstour I facelift	TF2	5	EU-HONDA-CROSSTOUR-I-FACELIFT-HATCHBACK-5D-01	HIGH	TF2四驱五门改款外廓。	READY
13180	13180	SUV	CR-V I	RD1	5	EU-HONDA-CR-V-I-RD1-SUV-5D-01	HIGH	RD1五门四驱SUV外廓。	READY
16573_prefl	16573	SUV	CR-V II		5	EU-HONDA-CR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
16573_facelift	16573	SUV	CR-V II facelift		5	EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
18473	18473	SUV	CR-V II facelift	RD9	5	EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	HIGH	RD9柴油改款后五门外廓。	READY
57748_prefl	57748	SUV	CR-V III		5	EU-HONDA-CR-V-III-EU-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分欧洲规格改款前外廓。	READY
57748_facelift	57748	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分欧洲规格改款后外廓。	READY
34931	34931	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	HIGH	2.2 i-DTEC对应改款后欧洲规格外廓。	READY
57197_prefl	57197	SUV	CR-V III		5	EU-HONDA-CR-V-III-24-SUV-5D-PREFL-01	HIGH	2.4四驱改款前市场规格外廓。	READY
57197_facelift	57197	SUV	CR-V III facelift		5	EU-HONDA-CR-V-III-24-SUV-5D-FACELIFT-01	HIGH	2.4四驱改款后市场规格外廓。	READY
35422_prefl	35422	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
35422_facelift	35422	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
112038	112038	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	改款后五门AWD外廓。	READY
56765_prefl	56765	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
56765_facelift	56765	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
56243_prefl	56243	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
56243_facelift	56243	SUV	CR-V IV facelift		5	EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
153051	153051	SUV	CR-V IV		5	EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	HIGH	2.2 i-DTEC对应改款前五门外廓。	READY
125265	125265	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-AWD-5D-01	HIGH	五门AWD外廓。	READY
143743	143743	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-AWD-5D-01	HIGH	混动AWD与同代汽油AWD共用外廓。	READY
155906	155906	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	HIGH	e:HEV前驱五门外廓。	READY
802282	802282	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	HIGH	2025年e:HEV前驱版本复用同一外廓。	READY
155907	155907	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	HIGH	e:HEV四驱五门外廓。	READY
802283	802283	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	HIGH	2025年e:HEV四驱版本复用同一外廓。	READY
155908	155908	SUV	CR-V VI		5	EU-HONDA-CR-V-VI-EPHEV-FWD-SUV-5D-01	HIGH	e:PHEV前驱底盘高度不同，独立建组。	READY
14662	14662	Coupe	CRX I	AF	3	EU-HONDA-CRX-I-AF-COUPE-3D-01	HIGH	AF三门Coupe外廓。	READY
17067	17067	Coupe	CRX II		3	EU-HONDA-CRX-II-COUPE-3D-01	HIGH	非VTEC 1.6 i 16V三门外廓。	READY
58815	58815	Coupe	CR-Z facelift	ZF2	3	EU-HONDA-CR-Z-ZF2-COUPE-3D-01	HIGH	ZF2改款后三门Coupe外廓。	READY
107258	107258	Coupe	CR-Z	ZF1	3	EU-HONDA-CR-Z-ZF1-COUPE-3D-01	HIGH	ZF1改款前三门Coupe外廓。	READY
154952	154952	SUV	e:Ny1		5	EU-HONDA-ENY1-ELECTRIC-SUV-5D-01	HIGH	五门电动SUV外廓。	READY
18472	18472	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	五门六座MPV外廓。	READY
18471	18471	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	五门六座MPV外廓。	READY
18231	18231	MPV	FR-V		5	EU-HONDA-FR-V-MPV-5D-01	HIGH	柴油动力未改变五门MPV外廓。	READY
116068_prefl	116068	SUV	HR-V II		5	EU-HONDA-HR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
116068_facelift	116068	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
146819	146819	SUV	HR-V III		5	EU-HONDA-HR-V-III-EHEV-SUV-5D-01	HIGH	e:HEV五门SUV外廓。	READY
14595	14595	SUV	HR-V I	GH1	3	EU-HONDA-HR-V-I-SUV-3D-01	HIGH	GH1前驱三门外廓。	READY
11121	11121	SUV	HR-V I	GH2	3	EU-HONDA-HR-V-I-SUV-3D-01	HIGH	GH2四驱三门外廓。	READY
14594	14594	SUV	HR-V I	GH4	5	EU-HONDA-HR-V-I-SUV-5D-01	HIGH	GH4四驱五门外廓。	READY
116067_prefl	116067	SUV	HR-V II		5	EU-HONDA-HR-V-II-SUV-5D-PREFL-01	HIGH	同一Ktype跨越改款，拆分改款前五门外廓。	READY
116067_facelift	116067	SUV	HR-V II facelift		5	EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	HIGH	同一Ktype跨越改款，拆分改款后五门外廓。	READY
14410	14410	Coupe	Insight I	ZE1	3	EU-HONDA-INSIGHT-I-ZE1-COUPE-3D-01	HIGH	ZE1三门双座Coupe外廓。	READY
56184	56184	Hatchback	Insight II	ZE2	5	EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	HIGH	ZE2五门Hybrid Hatchback外廓。	READY
17832	17832	Hatchback	Integra I	DA4	5	EU-HONDA-INTEGRA-I-DA-HATCHBACK-5D-01	HIGH	DA4五门Liftback外廓。	READY
17833	17833	Hatchback	Integra I		5	EU-HONDA-INTEGRA-I-DA-HATCHBACK-5D-01	HIGH	DA1/DA3共用五门Liftback外廓。	READY
124452	124452	Sedan	Integra III Sedan	DB7	4	EU-HONDA-INTEGRA-III-DB7-SEDAN-4D-01	HIGH	DB7四门Hardtop Sedan外廓。	READY
18564_prefl	18564	Coupe	Integra IV	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	HIGH	DC5改款前三门Liftback外廓。	READY
18564_facelift	18564	Coupe	Integra IV facelift	DC5	3	EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	HIGH	DC5改款后三门Liftback高度变化，独立建组。	READY
11059	11059	Coupe	Integra III Type R	DC2	3	EU-HONDA-INTEGRA-III-TYPE-R-DC2-EU-COUPE-3D-01	HIGH	欧洲190 PS DC2 Type R三门外廓。	READY
57345_96spec	57345	Coupe	Integra III Type R 96 Spec	DC2	3	EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-96SPEC-COUPE-3D-01	HIGH	JDM 96 Spec三门Type R外廓。	READY
57345_98spec	57345	Coupe	Integra III Type R 98 Spec	DC2	3	EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-98SPEC-COUPE-3D-01	HIGH	JDM 98 Spec三门Type R高度变化。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6501-6600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-ACCORD-VIII-TOURER-WAGON-5D-01	4750	1840	1470	Auto-Data Honda Accord VIII Wagon 2.2 i-DTEC; Automobile-Catalog Honda Accord Tourer 2.2 i-DTEC Type-S	https://www.auto-data.net/en/honda-accord-viii-wagon-2.2-i-dtec-150hp-12035;https://www.automobile-catalog.com/car/2012/1601465/honda_accord_tourer_2_2_i-dtec_type-s.html
EU-HONDA-CITY-V-SEDAN-4D-PREFL-01	4410	1695	1470	CarExpert 2009 Honda City 1.5 E specifications	https://www.carexpert.co.nz/honda/honda-city/2009-e-1-5l-sedan-fwd-petrol-automatic-joskw85f20090715
EU-HONDA-CITY-V-SEDAN-4D-FACELIFT-01	4430	1695	1470	CarExpert 2012 Honda City VTi specifications	https://www.carexpert.com.au/honda/city/2012-vti-1-5l-sedan-fwd-petrol-manual-jomgwkwf20120502
EU-HONDA-CIVIC-III-SEDAN-4D-01	4145	1630	1385	DrivePlace Honda Civic III 1.2 Sedan	https://honda.drive.place/civic/iii/group_sedan/93411
EU-HONDA-CIVIC-IV-SEDAN-4D-01	4230	1690	1360	Auto-Data Honda Civic IV 1.5i 16V	https://www.auto-data.net/en/honda-civic-iv-1.5i-16v-90hp-12276
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330	Auto-Data Honda Civic IV Hatchback 1.5 i 16V	https://www.auto-data.net/en/honda-civic-iv-hatchback-1.5-i-16v-90hp-12286
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-5D-01	4105	1690	1515	Auto-Data Honda Civic IV Shuttle	https://www.auto-data.net/en/honda-civic-iv-shuttle-generation-2637
EU-HONDA-CIVIC-IX-SEDAN-4D-01	4545	1755	1435	Auto-Data Honda Civic IX Sedan	https://www.auto-data.net/en/honda-civic-ix-sedan-generation-3926
EU-HONDA-CIVIC-IX-HATCHBACK-5D-PREFL-01	4300	1770	1440	Auto-Data Honda Civic IX Hatchback	https://www.auto-data.net/en/honda-civic-ix-hatchback-generation-3837
EU-HONDA-CIVIC-IX-HATCHBACK-5D-FACELIFT-01	4370	1770	1470	Auto-Data Honda Civic IX Hatchback facelift 2014	https://www.auto-data.net/en/honda-civic-ix-hatchback-facelift-2014-generation-4482
EU-HONDA-CIVIC-TYPE-R-FK2-HATCHBACK-5D-01	4390	1878	1466	Auto-Data Honda Civic Type R FK2	https://www.auto-data.net/en/honda-civic-type-r-fk2-2.0-310hp-30245
EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-PREFL-01	4535	1770	1480	Honda Europe 2014 Civic Tourer press release	https://hondanews.eu/eu/lt/cars/media/pressreleases/35274/2014-honda-civic-tourer
EU-HONDA-CIVIC-IX-TOURER-WAGON-5D-FACELIFT-01	4590	1770	1480	Auto-Data Honda Civic IX Tourer facelift 2014; Automobile Dimension Honda Civic Tourer 2015	https://www.auto-data.net/en/honda-civic-ix-tourer-facelift-2014-generation-4553;https://www.automobiledimension.com/model/honda/civic-tourer
EU-HONDA-CIVIC-V-SEDAN-4D-01	4405	1695	1375	Auto-Data Honda Civic V 1.5i 16V Sedan	https://www.auto-data.net/en/honda-civic-v-1.5i-16v-90hp-12272
EU-HONDA-CIVIC-V-HATCHBACK-3D-01	4080	1695	1345	Auto-Data Honda Civic V Hatchback 1.5i 16V	https://www.auto-data.net/en/honda-civic-v-hatchback-1.5i-16v-90hp-12267
EU-HONDA-CIVIC-VI-COUPE-2D-01	4460	1695	1375	Auto-Data Honda Civic VI Coupe	https://www.auto-data.net/en/honda-civic-vi-coupe-generation-2629
EU-HONDA-CIVIC-VI-SEDAN-4D-01	4460	1695	1390	Auto-Data Honda Civic VI 1.6 i Vtec; Automoli Honda Civic VI	https://www.auto-data.net/en/honda-civic-vi-1.6-i-vtec-125hp-12262;https://www.automoli.com/gb/vehicles/honda/civic/civic-vi-2632/
EU-HONDA-CIVIC-VI-AERODECK-WAGON-5D-01	4425	1695	1410	Auto-Data Honda Civic VI Wagon 1.6 16V	https://www.auto-data.net/en/honda-civic-vi-wagon-1.6-16v-116hp-12237
EU-HONDA-CIVIC-VI-FASTBACK-HATCHBACK-5D-01	4325	1695	1390	Auto-Data Honda Civic VI Fastback	https://www.auto-data.net/en/honda-civic-vi-fastback-generation-2628
EU-HONDA-CIVIC-VII-SEDAN-4D-02	4480	1715	1440	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-SEDAN-4D-01	4458	1715	1440	Auto-Data Honda Civic VII Sedan	https://www.auto-data.net/en/honda-civic-vii-sedan-generation-2626
EU-HONDA-CIVIC-VII-SEDAN-IMA-4D-01	4480	1715	1430	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-COUPE-2D-01	4438	1695	1399	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VII-HATCHBACK-3D-01	4140	1695	1440	Honda Europe Civic 01 3 Door	https://hondanews.eu/eu/en/cars/media/pressreleases/34356/civic-01-3-door
EU-HONDA-CIVIC-VII-HATCHBACK-5D-PREFL-01	4285	1695	1495	Honda Europe Civic 01 5 Door	https://hondanews.eu/eu/en/cars/media/pressreleases/34353/civic-01-5-door
EU-HONDA-CIVIC-VII-HATCHBACK-5D-FACELIFT-01	4285	1715	1495	Honda Europe Civic 04 Specifications 2004	https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004
EU-HONDA-CIVIC-VIII-SEDAN-4D-01	4545	1750	1435	Auto-Data Honda Civic VIII Sedan 1.6 i-VTEC	https://www.auto-data.net/en/honda-civic-viii-sedan-1.6-i-vtec-125hp-17146
EU-HONDA-CIVIC-VIII-SEDAN-IMA-4D-01	4488	1753	1430	Auto-Data Honda Civic VIII Sedan 1.3 i-DSi IMA	https://www.auto-data.net/en/honda-civic-viii-sedan-1.3-i-dsi-ima-110hp-hybrid-e-cvt-12214
EU-HONDA-CIVIC-X-HATCHBACK-5D-PREFL-01	4497	1800	1421	Honda Europe Civic 10th generation Paris Motor Show press pack	https://hondanews.eu/gb/en/cars/media/pressreleases/77994/civic-10th-generation-press-pack-paris-motor-show
EU-HONDA-CIVIC-X-HATCHBACK-5D-FACELIFT-01	4518	1799	1434	Honda Europe 2021 Honda Civic specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/327918/2021-honda-civic
EU-HONDA-CIVIC-X-SEDAN-4D-PREFL-01	4648	1799	1416	Honda Europe 2017 Honda Civic Sedan specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/107785/2017-honda-civic-sedan11
EU-HONDA-CIVIC-X-SEDAN-4D-FACELIFT-01	4658	1799	1416	Honda Europe 2021 Honda Civic specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/327918/2021-honda-civic
EU-HONDA-CIVIC-TYPE-R-FK8-HATCHBACK-5D-01	4557	1877	1434	Honda Europe 2020 Honda Civic Type R specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/308995/2020-honda-civic-type-r
EU-HONDA-CIVIC-XI-SEDAN-4D-01	4677	1802	1407	Honda Turkey New Civic Sedan official brochure	https://www.honda.com.tr/assets/files/yeni-civic-sedan-SVcS3.pdf
EU-HONDA-CIVIC-XI-HATCHBACK-5D-01	4551	1802	1408	Honda Europe 2022 Civic e:HEV specifications	https://hondanews.eu/gb/en/cars/media/documenttext/412439/2022-honda-civic-ehev-72
EU-HONDA-CIVIC-TYPE-R-FL5-HATCHBACK-5D-01	4594	1890	1401	Honda Europe 2023 Civic Type R specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/429984/2023-honda-civic-type-r
EU-HONDA-CONCERTO-HW-SEDAN-4D-01	4415	1690	1395	Auto-Data Honda Concerto HW	https://www.auto-data.net/en/honda-concerto-model-1312
EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	4265	1690	1395	Auto-Data Honda Concerto Hatch HW	https://www.auto-data.net/en/honda-concerto-model-1312
EU-HONDA-CROSSROAD-II-RT3-SUV-5D-01	4285	1755	1670	Honda Crossroad official archive specifications	https://www.honda.co.jp/auto-archive/crossroad/2010/grade-data/
EU-HONDA-CROSSTOUR-I-FACELIFT-HATCHBACK-5D-01	4994	1898	1561	Auto-Data Honda Crosstour facelift 3.5 V6 4WD	https://www.auto-data.net/en/honda-crosstour-facelift-2012-3.5-v6-278hp-4wd-automatic-46152
EU-HONDA-CR-V-I-RD1-SUV-5D-01	4520	1750	1675	Auto-Data Honda CR-V I RD 2.0 16V 1999	https://www.auto-data.net/en/honda-cr-v-i-rd-2.0-16v-147hp-automatic-29215
EU-HONDA-CR-V-II-SUV-5D-PREFL-01	4555	1780	1710	Honda Europe CR-V 02 official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34287/cr-v-02
EU-HONDA-CR-V-II-SUV-5D-FACELIFT-01	4635	1785	1710	Honda CR-V 2005 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/09/Honda-CR-V-2005-UK.pdf
EU-HONDA-CR-V-III-EU-SUV-5D-PREFL-01	4530	1820	1675	Auto-Data Honda CR-V III 2.0 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-automatic-12336
EU-HONDA-CR-V-III-EU-SUV-5D-FACELIFT-01	4574	1820	1675	Auto-Data Honda CR-V III facelift 2.0 i-VTEC; Auto-Data Honda CR-V III facelift 2.2 i-DTEC	https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.0-i-vtec-150hp-awd-17151;https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.2-i-dtec-150hp-awd-automatic-17154
EU-HONDA-CR-V-III-24-SUV-5D-PREFL-01	4519	1820	1679	Auto-Data Honda CR-V III 2.4 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.4-i-vtec-166hp-awd-automatic-12338
EU-HONDA-CR-V-III-24-SUV-5D-FACELIFT-01	4555	1820	1680	Auto-Data Honda CR-V III facelift 2.4 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-facelift-2009-2.4-i-vtec-180hp-awd-automatic-50949
EU-HONDA-CR-V-IV-SUV-5D-PREFL-01	4570	1820	1685	Honda Europe CR-V 1.6 i-DTEC official specifications	https://hondanews.eu/eu/fi/media/pressreleases/34746/introducing-the-new-sub-120-gkm-cr-v-16-i-dtec
EU-HONDA-CR-V-IV-SUV-5D-FACELIFT-01	4605	1820	1685	Honda Europe 2015 CR-V specifications; Auto-Data Honda CR-V IV facelift	https://hondanews.eu/eu/en/cars/media/pressreleases/42656/2015-honda-cr-v2;https://www.auto-data.net/en/honda-cr-v-iv-facelift-2014-1.6-i-dtec-160hp-awd-21489
EU-HONDA-CR-V-V-SUV-AWD-5D-01	4600	1855	1689	Honda Europe 2018 CR-V specifications; Auto-Data Honda CR-V V 1.5 VTEC Turbo AWD	https://hondanews.eu/pl/pl/cars/media/pressreleases/135747/honda-cr-v-2018;https://www.auto-data.net/en/honda-cr-v-v-1.5-vtec-turbo-193hp-awd-cvt-34298
EU-HONDA-CR-V-VI-EHEV-FWD-SUV-5D-01	4706	1866	1674	Honda 2023 CR-V official press kit; Auto-Data Honda CR-V VI e:HEV FWD	https://hondanews.eu/gb/en/cars/media/pressreleases/453027/2023-honda-cr-v-press-kit-43;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ehev-e-cvt-50279
EU-HONDA-CR-V-VI-EHEV-AWD-SUV-5D-01	4706	1866	1684	Honda 2024 CR-V official brochure; Auto-Data Honda CR-V VI e:HEV AWD	https://live.dealer-asset.co/ie33/product/file/Honda24YMCR-VBrochure2024.pdf;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ehev-4wd-e-cvt-50280
EU-HONDA-CR-V-VI-EPHEV-FWD-SUV-5D-01	4706	1866	1673	Honda 2024 CR-V official brochure; Auto-Data Honda CR-V VI e:PHEV	https://live.dealer-asset.co/ie33/product/file/Honda24YMCR-VBrochure2024.pdf;https://www.auto-data.net/en/honda-cr-v-vi-2.0-i-mmd-184hp-ephev-e-cvt-50281
EU-HONDA-CRX-I-AF-COUPE-3D-01	3675	1625	1290	Auto-Data Honda CRX I 1.3	https://www.auto-data.net/en/honda-crx-i-af-as-1.3-71hp-12378
EU-HONDA-CRX-II-COUPE-3D-01	3755	1675	1270	Auto-Data Honda CRX II 1.6 i 16V	https://www.auto-data.net/en/honda-crx-ii-ed-ee-1.6-i-16v-124hp-12375
EU-HONDA-CR-Z-ZF2-COUPE-3D-01	4075	1740	1395	Auto-Data Honda CR-Z facelift 1.5 i-VTEC IMA	https://www.auto-data.net/en/honda-cr-z-facelift-2012-1.5-i-vtec-137hp-ima-hybrid-56426
EU-HONDA-CR-Z-ZF1-COUPE-3D-01	4080	1740	1395	Auto-Data Honda CR-Z 1.5 i-VTEC IMA	https://www.auto-data.net/en/honda-cr-z-1.5-i-vtec-124hp-ima-hybrid-17149
EU-HONDA-ENY1-ELECTRIC-SUV-5D-01	4387	1790	1584	Honda Europe 2023 Honda e:Ny1 press kit	https://hondanews.eu/gb/en/cars/media/pressreleases/452981/2023-honda-eny1-press-kit-43
EU-HONDA-FR-V-MPV-5D-01	4285	1810	1610	Honda Europe FR-V Summary	https://hondanews.eu/eu/en/cars/media/pressreleases/214/fr-v-summary
EU-HONDA-HR-V-II-SUV-5D-PREFL-01	4294	1772	1605	Auto-Data Honda HR-V II 1.6 i-DTEC; Honda Europe 2015 HR-V specifications	https://www.auto-data.net/en/honda-hr-v-ii-1.6-i-dtec-120hp-22480;https://hondanews.eu/eu/lt/cars/media/pressreleases/56929/2015-honda-hr-v17
EU-HONDA-HR-V-II-SUV-5D-FACELIFT-01	4335	1772	1605	Honda Europe 2019 HR-V specifications; Auto-Data Honda HR-V II facelift 1.5 i-VTEC	https://hondanews.eu/eu/lt/cars/media/pressreleases/163240/2019-honda-hr-v46;https://www.auto-data.net/en/honda-hr-v-ii-facelift-2018-1.5-i-vtec-130hp-34799
EU-HONDA-HR-V-III-EHEV-SUV-5D-01	4340	1790	1582	Honda Europe 2021 HR-V e:HEV specifications	https://hondanews.eu/eu/el/cars/media/pressreleases/346733/2021-honda-hr-v-ehev-3
EU-HONDA-HR-V-I-SUV-3D-01	4010	1695	1670	Auto-Data Honda HR-V GH 1.6 i 16V 4WD 3-door; Honda Europe Geneva Motor Show 2000	https://www.auto-data.net/en/honda-hr-v-gh-1.6-i-16v-4wd-3-dr-124hp-12347;https://hondanews.eu/eu/lv/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-HR-V-I-SUV-5D-01	4110	1695	1670	Auto-Data Honda HR-V GH 1.6 i 16V 4WD 5-door; Honda Europe Geneva Motor Show 2000	https://www.auto-data.net/en/honda-hr-v-gh-1.6-i-16v-4wd-5-dr-124hp-12349;https://hondanews.eu/eu/lv/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-INSIGHT-I-ZE1-COUPE-3D-01	3945	1695	1355	Honda Europe Insight 2000 official specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34323/insight-2000
EU-HONDA-INSIGHT-II-ZE2-HATCHBACK-5D-01	4396	1695	1425	Honda Insight 2009 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Honda-Insight-2009-UK.pdf
EU-HONDA-INTEGRA-I-DA-HATCHBACK-5D-01	4350	1665	1345	Auto-Data Honda Integra I DA 5-door	https://www.auto-data.net/en/honda-integra-i-da-5-door-generation-9178
EU-HONDA-INTEGRA-III-DB7-SEDAN-4D-01	4525	1695	1370	Goo-net Honda Integra historical catalog; Honda Integra DB7 specifications	https://www.goo-net.com/catalog/HONDA/INTEGRA/;https://spec.greeco-channel.com/en/integra-8_m/
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-PREFL-01	4400	1725	1400	Auto-Data Honda Integra IV DC5 2.0 160 Hp	https://www.auto-data.net/en/honda-integra-iv-dc5-2.0-160hp-automatic-12118
EU-HONDA-INTEGRA-IV-DC5-COUPE-3D-FACELIFT-01	4400	1725	1395	Auto-Data Honda Integra IV DC5 facelift 2.0 160 Hp	https://www.auto-data.net/en/honda-integra-iv-dc5-facelift-2004-2.0-160hp-47120
EU-HONDA-INTEGRA-III-TYPE-R-DC2-EU-COUPE-3D-01	4400	1695	1320	Automobile-Catalog Honda Integra Type-R 2000 Europe	https://www.automobile-catalog.com/car/2000/1112450/honda_integra_type-r.html
EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-96SPEC-COUPE-3D-01	4380	1695	1320	Honda Sports Drive Web Integra Type R history; J-PN Honda Integra Type R 96 Spec	https://www.honda.co.jp/sportscar/sportscar/integra_type_r/;https://www.j-pn.co.uk/jdm-unicorns/Honda-Integra-Type-R-DC2-DC5/12/
EU-HONDA-INTEGRA-III-TYPE-R-DC2-JDM-98SPEC-COUPE-3D-01	4380	1695	1330	Honda Sports Drive Web Integra Type R history; J-PN Honda Integra Type R 98 Spec	https://www.honda.co.jp/sportscar/sportscar/integra_type_r/;https://www.j-pn.co.uk/jdm-unicorns/Honda-Integra-Type-R-DC2-DC5/12/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6501-6600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://autocatalogarchive.com/wp-content/uploads/2025/03/Honda-Insight-2009-UK.pdf?utm_source=chatgpt.com "Insight"
[2]: https://www.auto-data.net/en/honda-accord-viii-wagon-2.2-i-dtec-150hp-12035 "https://www.auto-data.net/en/honda-accord-viii-wagon-2.2-i-dtec-150hp-12035"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3550 行）
- 累计尺寸组：dimension_groups_final.tsv（952 行）

