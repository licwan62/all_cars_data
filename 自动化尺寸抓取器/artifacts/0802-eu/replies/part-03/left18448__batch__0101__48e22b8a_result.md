# 任务：left18448 第 10001-10100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0101__48e22b8a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 10001-10100 行

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
left18448 第 10001-10100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	Eqe	EQE 300	Stufenheck	Heckantrieb	Elektro	Jul 2022	Apr 2025	148191
Mercedes-benz	Eqe	EQE 300	SUV	Heckantrieb	Elektro	Mar 2023	Apr 2025	152952
Mercedes-benz	Eqe	EQE 300	Stufenheck	Heckantrieb	Elektro	Apr 2025	-	801748
Mercedes-benz	Eqe	EQE 300	SUV	Heckantrieb	Elektro	Apr 2025	-	803230
Mercedes-benz	Eqe	EQE 350	Stufenheck	Heckantrieb	Elektro	Jul 2022	-	150131
Mercedes-benz	Eqe	EQE 350 4-matic	Stufenheck	Allrad	Elektro	Jul 2022	Apr 2025	148192
Mercedes-benz	Eqe	EQE 350 4-matic	SUV	Allrad	Elektro	Dec 2022	-	151586
Mercedes-benz	Eqe	EQE 350 4-matic	Stufenheck	Allrad	Elektro	Apr 2025	-	801747
Mercedes-benz	Eqe	EQE 350 4-matic	SUV	Allrad	Elektro	Apr 2025	-	801867
Mercedes-benz	Eqe	EQE 350+	Stufenheck	Heckantrieb	Elektro	Feb 2022	Apr 2025	145523
Mercedes-benz	Eqe	EQE 350+	SUV	Heckantrieb	Elektro	Dec 2022	-	151585
Mercedes-benz	Eqe	EQE 350+	Stufenheck	Heckantrieb	Elektro	Apr 2025	-	801746
Mercedes-benz	Eqe	EQE 350+	SUV	Heckantrieb	Elektro	Apr 2025	-	801868
Mercedes-benz	Eqe	EQE 43 AMG 4-matic	Stufenheck	Allrad	Elektro	Feb 2022	-	147037
Mercedes-benz	Eqe	EQE 43 AMG 4-matic	SUV	Allrad	Elektro	Dec 2022	-	151588
Mercedes-benz	Eqe	EQE 500 4-matic	Stufenheck	Allrad	Elektro	Jul 2022	Apr 2025	148193
Mercedes-benz	Eqe	EQE 500 4-matic	SUV	Allrad	Elektro	Dec 2022	-	151587
Mercedes-benz	Eqe	EQE 500 4-matic	Stufenheck	Allrad	Elektro	Jul 2022	-	801761
Mercedes-benz	Eqe	EQE 500 4-matic	SUV	Allrad	Elektro	Apr 2025	-	801869
Mercedes-benz	Eqe	EQE 53 AMG 4-matic+	Stufenheck	Allrad	Elektro	Jul 2022	-	148194
Mercedes-benz	Eqe	EQE 53 AMG 4-matic+	Stufenheck	Allrad	Elektro	Jul 2022	-	153322
Mercedes-benz	Eqe	EQE 53 AMG 4-matic+	SUV	Allrad	Elektro	Aug 2023	-	156146
Mercedes-benz	Eqs	450 4-matic	SUV	Allrad	Elektro	Oct 2022	-	148216
Mercedes-benz	Eqs	450+	SUV	Heckantrieb	Elektro	Oct 2022	-	148215
Mercedes-benz	Eqs	500 4-matic	SUV	Allrad	Elektro	Dec 2022	-	153320
Mercedes-benz	Eqs	580 4-matic	SUV	Allrad	Elektro	Oct 2022	-	148217
Mercedes-benz	Eqs	680 Maybach 4-matic	SUV	Allrad	Elektro	Sep 2023	-	156023
Mercedes-benz	Eqs	EQS 350	Schrägheck	Heckantrieb	Elektro	Dec 2021	-	146622
Mercedes-benz	Eqs	EQS 450 4-matic	Schrägheck	Allrad	Elektro	May 2022	-	147683
Mercedes-benz	Eqs	EQS 450+	Schrägheck	Heckantrieb	Elektro	Aug 2021	-	145121
Mercedes-benz	Eqs	EQS 450+	Schrägheck	Heckantrieb	Elektro	May 2023	-	154568
Mercedes-benz	Eqs	EQS 500 4-matic	Schrägheck	Allrad	Elektro	May 2022	-	147680
Mercedes-benz	Eqs	EQS 53 AMG 4-matic+	Schrägheck	Allrad	Elektro	Dec 2021	-	146623
Mercedes-benz	Eqs	EQS 53 AMG Dynamic Plus 4-matic+	Schrägheck	Allrad	Elektro	Dec 2021	-	146624
Mercedes-benz	Eqs	EQS 580 4-matic	Schrägheck	Allrad	Elektro	Aug 2021	-	145122
Mercedes-benz	Eqs	EQS 580 4-matic	Schrägheck	Allrad	Elektro	May 2023	-	154569
Mercedes-benz	Eqt	EQT 200	Großraumlimousine	Frontantrieb	Elektro	Jan 2023	-	151621
Mercedes-benz	Eqv	EQV 250	Bus	Frontantrieb	Elektro	Nov 2021	-	146683
Mercedes-benz	G-Class	AMG G 63 Mild Hybrid 4-matic	Geländewagen geschlossen	Allrad	Benzin/Elektro	Apr 2024	-	158341
Mercedes-benz	G-Class	G 350 D 4-matic	Geländewagen geschlossen	Allrad	Diesel	Jun 2022	-	155345
Mercedes-benz	G-Class	G 350 D 4-matic	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2022	-	155346
Mercedes-benz	G-Class	G 450 D Mild Hybrid 4-matic	Geländewagen geschlossen	Allrad	Diesel/Elektro	Apr 2024	-	158343
Mercedes-benz	G-Class	G 500 Mild Hybrid 4-matic	Geländewagen geschlossen	Allrad	Benzin/Elektro	Apr 2024	-	158340
Mercedes-benz	G-Class	G 580 EV	Geländewagen geschlossen	Allrad	Elektro	Apr 2024	-	158622
Mercedes-benz	G-Klasse	200 G	Geländewagen geschlossen	Allrad	Benzin	Jul 1982	Aug 1989	125923
Mercedes-benz	G-Klasse	200 GE	Geländewagen geschlossen	Allrad	Benzin	Jan 1990	Jul 1993	55580
Mercedes-benz	G-Klasse	250 GD	Geländewagen geschlossen	Allrad	Diesel	Feb 1990	May 1993	12084
Mercedes-benz	G-Klasse	290 GD 4-matic	Pritsche/Fahrgestell	Allrad	Diesel	Nov 1991	Jul 2001	150551
Mercedes-benz	G-Klasse	500 GE	Geländewagen geschlossen	Allrad	Benzin	Sep 1993	Dec 1994	12106
Mercedes-benz	G-Klasse	AMG G 63	Geländewagen geschlossen	Allrad	Benzin	Jun 2015	Mar 2018	114589
Mercedes-benz	G-Klasse	AMG G 63 4x4²	Geländewagen geschlossen	Allrad	Benzin	Oct 2022	-	150766
Mercedes-benz	G-Klasse	AMG G 65	Geländewagen geschlossen	Allrad	Benzin	Jun 2015	Apr 2018	114590
Mercedes-benz	G-Klasse	G 270 CDI	Geländewagen geschlossen	Allrad	Diesel	Jan 2003	Dec 2006	59485
Mercedes-benz	G-Klasse	G 280 CDI 4-matic	Pritsche/Fahrgestell	Allrad	Diesel	May 2007	Dec 2012	150550
Mercedes-benz	G-Klasse	G 290 TD	Geländewagen geschlossen	Allrad	Diesel	Jul 1997	Jul 2001	8830
Mercedes-benz	G-Klasse	G 300 CDI 4-matic	Pritsche/Fahrgestell	Allrad	Diesel	Apr 2010	Jul 2023	156393
Mercedes-benz	G-Klasse	G 300 Diesel	Geländewagen geschlossen	Allrad	Diesel	Sep 1993	Aug 1994	143391
Mercedes-benz	G-Klasse	G 300 Diesel	Geländewagen offen	Allrad	Diesel	Sep 1993	Aug 1994	143392
Mercedes-benz	G-Klasse	G 300 TD	Geländewagen offen	Allrad	Diesel	Sep 1996	Jul 2000	5951
Mercedes-benz	G-Klasse	G 300 TD	Geländewagen geschlossen	Allrad	Diesel	Aug 1996	Jul 2000	5955
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen offen	Allrad	Diesel	Jul 2011	Dec 2015	12330
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen geschlossen	Allrad	Diesel	Jul 2011	Aug 2015	12331
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen offen	Allrad	Diesel	Jun 2009	Dec 2011	125925
Mercedes-benz	G-Klasse	G 350 CDI	Geländewagen geschlossen	Allrad	Diesel	Jun 2009	Dec 2011	125926
Mercedes-benz	G-Klasse	G 350 D	Geländewagen geschlossen	Allrad	Diesel	Jun 2015	Apr 2018	114585
Mercedes-benz	G-Klasse	G 36 AMG	Geländewagen geschlossen	Allrad	Benzin	Jan 1995	Jul 1998	13443
Mercedes-benz	G-Klasse	G 400 CDI	Geländewagen geschlossen	Allrad	Diesel	Dec 2000	Jul 2006	15363
Mercedes-benz	G-Klasse	G 400 CDI	Geländewagen offen	Allrad	Diesel	Dec 2000	Jul 2006	15364
Mercedes-benz	G-Klasse	G 500	Geländewagen geschlossen	Allrad	Benzin	Apr 1998	Dec 2015	10142
Mercedes-benz	G-Klasse	G 500	Geländewagen offen	Allrad	Benzin	Apr 1998	Dec 2015	10143
Mercedes-benz	G-Klasse	G 500	Geländewagen geschlossen	Allrad	Benzin	Sep 2004	Dec 2005	45896
Mercedes-benz	G-Klasse	G 500	Geländewagen geschlossen	Allrad	Benzin	May 2008	Aug 2015	59473
Mercedes-benz	G-Klasse	G 500	Geländewagen geschlossen	Allrad	Benzin	Jun 2015	Apr 2018	114588
Mercedes-benz	G-Klasse	G 55 AMG	Geländewagen geschlossen	Allrad	Benzin	Apr 1999	Jul 2008	12143
Mercedes-benz	G-Klasse	G 55 AMG	Geländewagen geschlossen	Allrad	Benzin	Jun 2004	Jul 2006	18100
Mercedes-benz	G-Klasse	G 63 AMG	Geländewagen geschlossen	Allrad	Benzin	May 2012	Mar 2018	55394
Mercedes-benz	G-Klasse	G 63 AMG 6X6	Geländewagen geschlossen	Allrad	Benzin	Dec 2014	Mar 2018	109310
Mercedes-benz	G-Klasse	G 65 AMG	Geländewagen geschlossen	Allrad	Benzin	May 2012	Apr 2018	59474
Mercedes-benz	Gla	AMG GLA 35 Mild Hybrid 4-matic	SUV	Allrad	Benzin/Elektro	Mar 2023	-	154466
Mercedes-benz	Gla	GLA 180 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2023	-	154458
Mercedes-benz	Gla	GLA 200 4-matic	SUV	Allrad	Benzin	Oct 2020	-	142497
Mercedes-benz	Gla	GLA 200 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2023	-	154461
Mercedes-benz	Gla	GLA 220 Mild-hybrid 4-matic	SUV	Allrad	Benzin/Elektro	Mar 2023	-	154464
Mercedes-benz	Gla	GLA 250 E	SUV	Frontantrieb	Benzin/Elektro	Mar 2023	-	154463
Mercedes-benz	Gla	GLA 250 Mild-hybrid 4-matic	SUV	Allrad	Benzin/Elektro	Mar 2023	-	154465
Mercedes-benz	Gla-Klasse	AMG GLA 45 4-matic	SUV	Allrad	Benzin	Jul 2015	Jun 2019	115054
Mercedes-benz	Gla-Klasse	GLA 180	SUV	Frontantrieb	Benzin	Feb 2015	Dec 2019	110035
Mercedes-benz	Gla-Klasse	GLA 180 CDI / D	SUV	Frontantrieb	Diesel	Jul 2014	May 2018	107540
Mercedes-benz	Gla-Klasse	GLA 200	SUV	Frontantrieb	Benzin	Dec 2013	Dec 2019	100449
Mercedes-benz	Gla-Klasse	GLA 200 CDI / D	SUV	Frontantrieb	Diesel	Dec 2013	Dec 2019	100453
Mercedes-benz	Gla-Klasse	GLA 200 CDI 4-matic	SUV	Allrad	Diesel	Dec 2013	May 2019	100466
Mercedes-benz	Gla-Klasse	GLA 220 4-matic	SUV	Allrad	Benzin	Jan 2017	Dec 2019	117987
Mercedes-benz	Gla-Klasse	GLA 220 CDI	SUV	Frontantrieb	Diesel	Dec 2013	May 2019	100467
Mercedes-benz	Gla-Klasse	GLA 220 CDI / D	SUV	Frontantrieb	Diesel	Dec 2013	May 2019	100472
Mercedes-benz	Gla-Klasse	GLA 220 CDI / D 4-matic	SUV	Allrad	Diesel	Dec 2013	Dec 2019	100476
Mercedes-benz	Gla-Klasse	GLA 220 CDI 4-matic	SUV	Allrad	Diesel	Dec 2013	Dec 2019	100474
Mercedes-benz	Gla-Klasse	GLA 220 D	SUV	Frontantrieb	Diesel	Jul 2015	May 2019	115062
Mercedes-benz	Gla-Klasse	GLA 220 D 4-matic	SUV	Allrad	Diesel	Jul 2015	Dec 2019	115065
Mercedes-benz	Gla-Klasse	GLA 250	SUV	Frontantrieb	Benzin	Dec 2013	Dec 2019	100477
Mercedes-benz	Gla-Klasse	GLA 250 4-matic	SUV	Allrad	Benzin	Dec 2013	Dec 2019	100478


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 EQE、EQS、EQT、2024 款 G-Class W465/E465，以及 GLA H247/X156 的物理车身聚类和首次尺寸组建档。
* EQE 普通版与 AMG 版、EQE SUV 普通版与 AMG 版分别建组；EQS 普通掀背、AMG 掀背、普通 SUV 和 Maybach 宽体 SUV 分别建组。([Mercedes-Benz][1])
* 2024 款 G 450 d/G 500、AMG G 63 和 G 580 EV 已按 W465、AMG W465、E465 三种外廓建组。([Mercedes-Benz][2])
* GLA H247 已区分改款前、2023 改款后和 AMG 外廓；X156 已区分普通版和 AMG GLA 45。([Mercedes-Benz][3])
* 旧款 G-Klasse 暂不猜测合并：短轴/长轴、3门/5门、敞篷、底盘车、AMG 宽体、4x4² 与 6x6 等分支继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：63
* PENDING 映射：37
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
148191	148191	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
152952	152952	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801748	801748	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
803230	803230	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
150131	150131	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
148192	148192	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151586	151586	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801747	801747	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801867	801867	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
145523	145523	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151585	151585	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801746	801746	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801868	801868	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
147037	147037	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
151588	151588	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	HIGH		READY
148193	148193	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151587	151587	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801761	801761	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801869	801869	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
148194	148194	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
153322	153322	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
156146	156146	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	HIGH		READY
148216	148216	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
148215	148215	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
153320	153320	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
148217	148217	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
156023	156023	SUV	EQS SUV	Z296	5	EU-MERCEDES-BENZ-EQS-Z296-MAYBACH-SUV-01	HIGH	Maybach Z296宽体外廓。	READY
146622	146622	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
147683	147683	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
145121	145121	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
154568	154568	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
147680	147680	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
146623	146623	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	HIGH		READY
146624	146624	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	HIGH		READY
145122	145122	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
154569	154569	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
151621	151621	MPV	EQT	E420	5	EU-MERCEDES-BENZ-EQT-E420-MPV-01	MEDIUM		READY
146683	146683	MPV	EQV W447	E447	5		LOW	Ktype可能覆盖长轴与超长轴，需确认是否拆分。	PENDING: 物理外廓分支或三维来源尚未闭合
158341	158341	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-AMG-SUV-01	HIGH		READY
155345	155345	SUV	G-Class W463A	W463A	5		LOW	W463A柴油标准车身三维尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
155346	155346	Pickup	G-Class W463A	W463A	2		LOW	Pritsche/Fahrgestell的轴距与后部车身配置未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
158343	158343	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	HIGH		READY
158340	158340	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	HIGH		READY
158622	158622	SUV	G-Class E465	E465	5	EU-MERCEDES-BENZ-G-CLASS-E465-EV-SUV-01	HIGH	电动E465标准外廓。	READY
125923	125923	SUV	G-Class W460	W460			LOW	封闭车身可能含短轴3门与长轴5门，需拆分确认。	PENDING: 物理外廓分支或三维来源尚未闭合
55580	55580	SUV	G-Class W463	W463			LOW	封闭车身可能含短轴3门与长轴5门，需拆分确认。	PENDING: 物理外廓分支或三维来源尚未闭合
12084	12084	SUV	G-Class W461	W461			LOW	W461封闭车身轴距与门数分支尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
150551	150551	Pickup	G-Class W461	W461	2		LOW	底盘车轴距与车身长度配置未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
12106	12106	SUV	G-Class W463	W463	5		LOW	500 GE长轴车身三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
114589	114589	SUV	G-Class W463	W463	5		LOW	AMG外部套件对应宽度与高度口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
150766	150766	SUV	G-Class W463A	W463A	5		LOW	4x4²门式桥、宽体与高车身外廓尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
114590	114590	SUV	G-Class W463	W463	5		LOW	AMG G65外部套件三维口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
59485	59485	SUV	G-Class W463	W463			LOW	封闭车身短轴/长轴与门数分支尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
150550	150550	Pickup	G-Class W461	W461	2		LOW	底盘车轴距与后部配置未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
8830	8830	SUV	G-Class W463	W463	5		LOW	长轴封闭车身三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
156393	156393	Pickup	G-Class W461	W461	2		LOW	底盘车存在多轴距及车身长度，需拆分确认。	PENDING: 物理外廓分支或三维来源尚未闭合
143391	143391	SUV	G-Class W463	W463			LOW	封闭车身短轴3门与长轴5门分支尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
143392	143392	Convertible	G-Class W463	W463	3		LOW	敞篷短轴外廓三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
5951	5951	Convertible	G-Class W463	W463	3		LOW	敞篷短轴外廓三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
5955	5955	SUV	G-Class W463	W463			LOW	封闭车身短轴/长轴分支尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
12330	12330	Convertible	G-Class W463	W463	3		LOW	敞篷AMG Line时期外廓三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
12331	12331	SUV	G-Class W463	W463	5		LOW	长轴封闭车身改款期三维尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
125925	125925	Convertible	G-Class W463	W463	3		LOW	敞篷短轴外廓三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
125926	125926	SUV	G-Class W463	W463	5		LOW	长轴封闭车身三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
114585	114585	SUV	G-Class W463	W463	5		LOW	2015-2018改款外廓三维口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
13443	13443	SUV	G-Class W463	W463			LOW	G36 AMG短轴/长轴适用边界与三维尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
15363	15363	SUV	G-Class W463	W463	5		LOW	长轴封闭车身三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
15364	15364	Convertible	G-Class W463	W463	3		LOW	敞篷短轴外廓三维来源尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
10142	10142	SUV	G-Class W463	W463			LOW	生产期跨多次改款且可能含短轴/长轴，需拆分确认。	PENDING: 物理外廓分支或三维来源尚未闭合
10143	10143	Convertible	G-Class W463	W463	3		LOW	生产期跨多次改款，敞篷外廓需按阶段闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
45896	45896	SUV	G-Class W463	W463			LOW	封闭车身门数与轴距分支尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
59473	59473	SUV	G-Class W463	W463	5		LOW	生产期跨改款，保险杠与高度口径需闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
114588	114588	SUV	G-Class W463	W463	5		LOW	2015-2018改款外廓三维口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
12143	12143	SUV	G-Class W463	W463			LOW	早期G55 AMG门数/轴距边界与三维尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
18100	18100	SUV	G-Class W463	W463			LOW	G55 AMG门数/轴距边界与三维尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
55394	55394	SUV	G-Class W463	W463	5		LOW	AMG保险杠、轮眉宽度及高度口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
109310	109310	SUV	G-Class W463 6x6	W463	4		LOW	6x6三轴特殊车身需独立尺寸组。	PENDING: 物理外廓分支或三维来源尚未闭合
59474	59474	SUV	G-Class W463	W463	5		LOW	AMG G65外部套件三维口径尚未闭合。	PENDING: 物理外廓分支或三维来源尚未闭合
154466	154466	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	HIGH		READY
154458	154458	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
142497	142497	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	改款前H247外廓。	READY
154461	154461	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154464	154464	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154463	154463	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154465	154465	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
115054	115054	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-AMG-SUV-01	HIGH		READY
110035	110035	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
107540	107540	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100449	100449	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100453	100453	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100466	100466	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
117987	117987	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100467	100467	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100472	100472	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100476	100476	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100474	100474	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
115062	115062	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
115065	115065	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100477	100477	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100478	100478	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	4946	1961	1510	Mercedes-Benz EQE Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-eqe-saloon-2024-september-v295-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	4964	1906	1495	Mercedes-AMG EQE Owner's Manual Supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-bh/pdf/mercedes-amg-eqe-owners-manual-supplement-september-2024-1.pdf
EU-MERCEDES-BENZ-EQE-X294-SUV-01	4863	1940	1686	Mercedes-Benz EQE SUV official press release	https://media.mercedes-benz.ca/releases/release-c0cb899bf0911f20b01ae662da01cdfd-the-new-eqe-suv-high-tech-and-luxury-meet-versatility
EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	4879	1931	1672	Mercedes-Benz EQE SUV Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.in/passengercars/services/manuals.html/eqe-suv-2026-07-x294-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	5216	1926	1512	Mercedes-Benz EQS Owner's Manual	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-saloon-2023-09-v297-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	5223	1926	1513	Mercedes-Benz EQS Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.uk/passengercars/services/manuals.html/eqs-saloon-2023-09-v297-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-EQS-X296-SUV-01	5125	1959	1718	Mercedes-Benz EQS SUV Owner's Manual	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-suv-2022-06-x296-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQS-Z296-MAYBACH-SUV-01	5125	2034	1721	Mercedes-Benz EQS SUV Owner's Manual (Mercedes-Maybach)	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-suv-2025-03-z296-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQT-E420-MPV-01	4498	1859	1819	EV Database Mercedes-Benz EQT 200 Standard	https://ev-database.org/car/1908/Mercedes-Benz-EQT-200-Standard
EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	4825	1931	1973	Mercedes-Benz G-Class W465 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-g-class-suv-2024-april-w465-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W465-AMG-SUV-01	4873	1984	1971	Mercedes-Benz G-Class W465 Owner's Manual (Mercedes-AMG G 63)	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-g-class-suv-2024-april-w465-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-E465-EV-SUV-01	4680	1985	1990	Mercedes-Benz Japan G 580 with EQ Technology official page	https://www.mercedes-benz.co.jp/passengercars/models/suv/g-class-electric/overview.html
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	Mercedes-Benz GLA H247 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-kw/pdf/mercedes-gla-suv-2020-september-h247-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	4412	1834	1616	Mercedes-Benz GLA H247 Owner's Manual	https://www.mercedes-benz.com.do/en/services/manuals/gla-suv-2023-07-h247-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1590	Mercedes-Benz GLA H247 Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.uk/vans/services/manuals.html/gla-suv-2026-07-h247-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494	Mercedes-Benz GLA X156 official brochure	https://www.mercedes-benzcaribbean.com/assets/themes/mb-caribbean/media/vehicles/class-gla/suv/GLA_X156_ePaper_UP_1218_02_ENG_Final.pdf
EU-MERCEDES-BENZ-GLA-X156-AMG-SUV-01	4445	1804	1479	Mercedes-AMG GLA 45 4MATIC brochure	https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-GLA-45-AMG-2014-CN.pdf
```

## 下一步优先处理

1. 闭合 EQV E447 的长轴与超长轴边界，确认 Ktype `146683` 是否需要派生两行。
2. 优先处理 W463A/W461 的标准封闭车身和 Pritsche/Fahrgestell 多轴距分支。
3. 将旧款 W460/W463 按短轴3门、长轴5门、敞篷、AMG、4x4²、6x6 聚类，尺寸组首次闭合后批量回填相关 Ktype。

推进信号：CONTINUE

[1]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-eqe-saloon-2024-september-v295-mbux-owners-manual-1.pdf?utm_source=chatgpt.com "EQE
Owner's Manual +
F295 0087 02"
[2]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-g-class-suv-2024-april-w465-mbux-owners-manual-1.pdf?utm_source=chatgpt.com "g-class suv 2024 april mbux Owner's Manual PDF Download"
[3]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-kw/pdf/mercedes-gla-suv-2020-september-h247-mbux-owners-manual-1.pdf?utm_source=chatgpt.com "gla suv 2020 september mbux Owner's Manual PDF Download | Mercedes-Benz"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 EQV E447 的 Long 与 Extra-long 两种物理车身，Ktype `146683` 拆分为两个派生映射。官方手册明确给出两种长度、1928 mm 不含后视镜宽度及统一高度。
* 闭合 500 GE V8 长轴五门外廓，确认车身代码 `463.228`。([marsClassic][1])
* 闭合 G 300 Diesel、G 300 Turbodiesel 与 G 350 CDI 的短轴三门、长轴五门及短轴敞篷分支。([marsClassic][2])

## 当前批次进度

* READY 映射：75
* PENDING 映射：29
* 已确认尺寸组：29
* 本轮闭合输入 Ktype：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146683_long	146683	MPV	EQV E447	E447	5	EU-MERCEDES-BENZ-EQV-E447-MPV-LONG-01	HIGH	长轴车身。	READY
146683_extralong	146683	MPV	EQV E447	E447	5	EU-MERCEDES-BENZ-EQV-E447-MPV-EXTRALONG-01	HIGH	超长轴车身。	READY
12106	12106	SUV	G-Class W463	463.228	5	EU-MERCEDES-BENZ-G-CLASS-W463-500GE-LWB-01	HIGH		READY
143391_swb	143391	SUV	G-Class W463	463.327	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	HIGH	短轴三门车身。	READY
143391_lwb	143391	SUV	G-Class W463	463.328	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门车身。	READY
143392	143392	Convertible	G-Class W463	463.307	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1990-01	HIGH		READY
5951	5951	Convertible	G-Class W463	463.308	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	HIGH		READY
5955_swb	5955	SUV	G-Class W463	463.330	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	短轴三门车身。	READY
5955_lwb	5955	SUV	G-Class W463	463.331	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	长轴五门车身。	READY
125925	125925	Convertible	G-Class W463	463.303	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH		READY
125926_swb	125926	SUV	G-Class W463	463.340	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	短轴三门车身。	READY
125926_lwb	125926	SUV	G-Class W463	463.341	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	长轴五门车身。	READY
```

映射中的门数、车身代码及短轴/长轴边界均来自对应 Mercedes-Benz 官方资料。([marsClassic][1])

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQV-E447-MPV-LONG-01	5140	1928	1910	Mercedes-Benz EQV E447 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-is/pdf/mercedes-eqv-fjolnota-b%C3%ADll-2021-ma%C3%AD-e447-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-EQV-E447-MPV-EXTRALONG-01	5370	1928	1910	Mercedes-Benz EQV E447 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-is/pdf/mercedes-eqv-fjolnota-b%C3%ADll-2021-ma%C3%AD-e447-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W463-500GE-LWB-01	4670	1810	1963	Mercedes-Benz Public Archive — 500 GE V8	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-GE-V8-1993---1994.xhtml?oid=191039032
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	4185	1690	1908	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	4635	1690	1936	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-long-wheelbase-1990---1994.xhtml?oid=191039017
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1990-01	4225	1690	1940	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	4275	1760	1941	Mercedes-Benz Public Archive — G 300 Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-short-wheelbase-1996---2000.xhtml?oid=191039018
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	4230	1760	1931	Mercedes-Benz Public Archive — G 300 Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-short-wheelbase-1996---2000.xhtml?oid=191039018
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	4680	1760	1936	Mercedes-Benz Public Archive — G 300 Turbodiesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-long-wheelbase-1996---2000.xhtml?oid=191039019
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	4257	1760	1941	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	4212	1760	1931	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	4662	1760	1931	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039060
```

本轮尺寸值由 EQV 官方手册及 Mercedes-Benz Public Archive 的对应车身规格页直接支持。

## 下一步优先处理

1. 闭合 2000–2018 年 W463 长轴标准车身的改款阶段，批量处理 `12331`、`125926` 之后的 G 350/G 500 系列。
2. 闭合 W463 AMG G 55、G 63、G 65 的普通 AMG 宽体外廓，并独立处理 4x4² 与 6x6。
3. 处理 W460/W461 封闭车身及 Pritsche/Fahrgestell 的短轴、长轴和底盘车分支。

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-GE-V8-1993---1994.xhtml?oid=191039032 "500 GE V8, 1993 - 1994"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016 "300 GD (from 09.1993: G 300 Diesel) (short wheelbase), 1990 - 1994"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 G 400 CDI 的短轴三门、长轴五门和短轴敞篷三种外廓；原封闭车身 Ktype `15363` 拆分为短轴与长轴两行，敞篷 Ktype `15364` 单独关联敞篷尺寸组。官方档案分别确认车身代码、门数及三维。([marsClassic][1])
* 闭合 Ktype `18100` 对应的 G 55 AMG Compressor 长轴五门外廓；该版本自 2004 年起仅提供长轴 Station Wagon，车身代码为 `463.270`。([marsClassic][2])

## 当前批次进度

* READY 映射：79
* PENDING 映射：26
* 已确认尺寸组：33
* 本轮闭合输入 Ktype：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15363_swb	15363	SUV	G-Class W463	463.332	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
15363_lwb	15363	SUV	G-Class W463	463.333	5	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
15364	15364	Convertible	G-Class W463	463.309	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-CABRIO-01	HIGH	短轴三门敞篷车身。	READY
18100	18100	SUV	G-Class W463	463.270	5	EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	HIGH	长轴五门AMG Compressor外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	4230	1760	1931	Mercedes-Benz Public Archive — G 400 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-short-wheelbase-2001---2006.xhtml?oid=191039047
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	4680	1760	1936	Mercedes-Benz Public Archive — G 400 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-long-wheelbase-2001---2006.xhtml?oid=191039048
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-CABRIO-01	4275	1760	1941	Mercedes-Benz Public Archive — G 400 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-short-wheelbase-2001---2006.xhtml?oid=191039047
EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	4662	1864	1931	Mercedes-Benz Public Archive — G 55 AMG Compressor long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-55-AMG-Compressor-long-wheelbase-2004---2008.xhtml?oid=191039057
```

## 下一步优先处理

1. 闭合 G 270 CDI 的短轴和长轴封闭车身，处理 Ktype `59485`。
2. 闭合 2008–2015 年 G 350 CDI/BlueTEC 的短轴、长轴和敞篷阶段，批量处理 `12330`、`12331`。
3. 闭合 2012–2018 年标准长轴、AMG G 63、AMG G 65、4x4² 与 6x6 特殊外廓。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-short-wheelbase-2001---2006.xhtml?oid=191039047&utm_source=chatgpt.com "G 400 CDI (short wheelbase), 2001 - 2006"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-55-AMG-Compressor-long-wheelbase-2004---2008.xhtml?oid=191039057 "G 55 AMG Compressor (long wheelbase), 2004 - 2008"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 G 270 CDI 的短轴三门与长轴五门分支，复用同阶段已确认的 W463 尺寸组。
* 闭合 G 350 CDI/BlueTEC 的短轴敞篷、短轴三门和长轴五门分支，复用既有 2008–2012 尺寸组。官方档案确认相应车身代码、门数和三维边界。([marsClassic][1])
* 首次创建 2015–2018 W463 改款标准车身及 AMG 车身尺寸组；官方手册分别给出不含后视镜宽度及完整三维。([Mercedes-Benz][2])

## 当前批次进度

* READY 映射：89
* PENDING 映射：18
* 已确认尺寸组：35
* 本轮闭合输入 Ktype：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59485_swb	59485	SUV	G-Class W463	463.322	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
59485_lwb	59485	SUV	G-Class W463	463.323	5	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
12330	12330	Convertible	G-Class W463	463.306	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH	短轴三门敞篷车身。	READY
12331_swb	12331	SUV	G-Class W463	463.336	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	短轴三门封闭车身。	READY
12331_lwb	12331	SUV	G-Class W463	463.346	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	长轴五门封闭车身。	READY
114585	114585	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	HIGH	2015改款标准外廓。	READY
114588	114588	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	HIGH	2015改款标准外廓。	READY
114589	114589	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015改款AMG外廓。	READY
114590	114590	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015改款AMG外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	4764	1867	1954	Mercedes-Benz G-Class Owner's Manual, Edition 2015-1a	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-g-class-suv-2015-july-463-comand-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	4769	1855	1938	Mercedes-Benz G-Class Owner's Manual, Edition 2015-1a	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-g-class-suv-2015-july-463-comand-owners-manual-1.pdf
```

## 下一步优先处理

1. 闭合 2012–2015 改款前 AMG G 63、G 65 外廓，并拆分跨越 2015 改款的 Ktype。
2. 独立闭合 AMG G 63 4x4² 与 G 63 AMG 6x6 特殊宽体、高车身外廓。
3. 处理剩余 W460/W461 封闭车身及 Pritsche/Fahrgestell 的轴距和底盘分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-270-CDI-short-wheelbase-2001---2006.xhtml?oid=191039043 "G 270 CDI (short wheelbase), 2001 - 2006"
[2]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-g-class-suv-2015-july-463-comand-owners-manual-1.pdf?utm_source=chatgpt.com "g-class suv 2015 july comand Owner's Manual PDF ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 G 290 Turbodiesel W461 的短轴三门和长轴五门外廓，首次创建两个尺寸组。官方档案分别确认 `461.335`、`461.336` 以及对应三维。([marsClassic][1])
* 闭合 G 36 AMG 长轴五门外廓，复用既有 W463 长轴尺寸组；官方档案确认车身代码 `463.231` 和 4680/1760/1936 mm 外廓。([marsClassic][2])
* 闭合跨阶段 G 500 的短轴、长轴及敞篷分支；1998–2008、2008–2012 外廓直接复用既有缓存，2012 年后长轴车身复用既有改款组。官方档案确认各阶段车身边界。([marsClassic][3])
* 闭合早期 G 55 AMG 的短轴、长轴与后期 Compressor 长轴外廓，均复用已有尺寸组。([marsClassic][4])

## 当前批次进度

* READY 映射：107
* PENDING 映射：11
* 已确认尺寸组：37
* 本轮闭合输入 Ktype：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8830_swb	8830	SUV	G-Class W461	461.335	3	EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
8830_lwb	8830	SUV	G-Class W461	461.336	5	EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
13443	13443	SUV	G-Class W463	463.231	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	长轴五门外廓。	READY
10142_swb_pre2008	10142	SUV	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	1998-2008短轴三门封闭车身。	READY
10142_lwb_pre2008	10142	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	1998-2008长轴五门封闭车身。	READY
10142_swb_2008	10142	SUV	G-Class W463	463.222	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	2008改款短轴三门封闭车身。	READY
10142_lwb_2008	10142	SUV	G-Class W463	463.236	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	2008改款长轴五门封闭车身。	READY
10142_lwb_2012	10142	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	MEDIUM	2012-2015改款长轴五门外廓。	READY
10143_pre2008	10143	Convertible	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	HIGH	1998-2008短轴三门敞篷车身。	READY
10143_2008	10143	Convertible	G-Class W463	463.202	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH	2008改款短轴三门敞篷车身。	READY
45896_swb	45896	SUV	G-Class W463	463.247	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	短轴三门封闭车身。	READY
45896_lwb	45896	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	长轴五门封闭车身。	READY
59473_swb	59473	SUV	G-Class W463	463.222	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	2008改款短轴三门封闭车身。	READY
59473_lwb_pre2012	59473	SUV	G-Class W463	463.236	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	2008-2012长轴五门封闭车身。	READY
59473_lwb_2012	59473	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	MEDIUM	2012-2015改款长轴五门外廓。	READY
12143_swb_1999	12143	SUV	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	早期自然吸气AMG短轴三门外廓。	READY
12143_lwb_1999	12143	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	早期自然吸气AMG长轴五门外廓。	READY
12143_lwb_comp	12143	SUV	G-Class W463	463.270	5	EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	HIGH	AMG Compressor长轴五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-SWB-STATION-01	4015	1700	1940	Mercedes-Benz Public Archive — 290 GD Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-Turbodiesel-short-wheelbase-1997---2001-from-2001-G-290-Turbodiesel.xhtml?oid=191011040
EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-LWB-STATION-01	4465	1700	1945	Mercedes-Benz Public Archive — 290 GD Turbodiesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-Turbodiesel-long-wheelbase-1997---2001-from-2001-G-290-Turbodiesel.xhtml?oid=191011041
```

## 下一步优先处理

1. 闭合 G 63 AMG、G 65 AMG 的 2012–2015 外廓，并复用 2015–2018 AMG 缓存组。
2. 独立闭合 G 500 4x4² 和 G 63 AMG 6x6。
3. 处理剩余 W460/W461 封闭车身及 Pritsche/Fahrgestell 多轴距分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-Turbodiesel-short-wheelbase-1997---2001-from-2001-G-290-Turbodiesel.xhtml?oid=191011040&utm_source=chatgpt.com "290 GD Turbodiesel (short wheelbase), 1997 - 2001 (from 2001: G 290 Turbodiesel)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-36-AMG-long-wheelbase-1996---1997.xhtml?oid=193619749&utm_source=chatgpt.com "G 36 AMG (long wheelbase), 1996 - 1997"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-500-short-wheelbase-1998---2000.xhtml?oid=191039033&utm_source=chatgpt.com "G 500 (short wheelbase), 1998 - 2000"
[4]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-55-AMG-short-wheelbase-1999---2000.xhtml?oid=191039040&utm_source=chatgpt.com "G 55 AMG (short wheelbase), 1999 - 2000"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Ktype `55580`：200 GE 仅对应 W463 长轴五门 Station Wagon，复用既有 1990 年代 W463 长轴尺寸组。([marsClassic][1])
* 闭合 Ktype `12084`：250 GD 的封闭车身拆分为 W463 短轴三门与长轴五门，均复用既有尺寸组，不重复抓取三维。([marsClassic][2])

## 当前批次进度

* READY 映射：110
* PENDING 映射：9
* 已确认尺寸组：37
* 本轮闭合输入 Ktype：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
55580	55580	SUV	G-Class W463	463.221	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门封闭车身。	READY
12084_swb	12084	SUV	G-Class W463	463.324	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	HIGH	短轴三门封闭车身。	READY
12084_lwb	12084	SUV	G-Class W463	463.325	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门封闭车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Ktype `125923` 的 W460 短轴、长轴及跨 1987 年外廓变化。
2. 解决 2012–2015 G 63/G 65 AMG 的宽体宽度来源冲突，再批量闭合 `55394`、`59474`。
3. 独立闭合 `150766` AMG G 63 4x4²、`109310` G 63 AMG 6x6。
4. 最后处理 `155345`、`155346`、`150551`、`156393` 的 W463A/W461 标准车身及底盘车轴距分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-GE-from-091993-G-200-long-wheelbase-1989---1993-only-as-export-model-for-Italy.xhtml?oid=191039023 "200 GE (from 09.1993: G 200) (long wheelbase), 1989 - 1993 (only as export model for Italy)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-GD-short-wheelbase-1990---1992.xhtml?oid=191039014 "250 GD (short wheelbase), 1990 - 1992"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 `150551` 的 W461 超长轴双门底盘车。官方档案确认车身代码 `461.329`，外廓为 4688/1760/1984 mm。([marsClassic][1])
* `55394` 与 `59474` 按 2015 年改款边界拆分：2012–2015 年 AMG 外廓首次建组，2015–2018 年直接复用既有 AMG 改款尺寸组。改款前 G 63/G 65 的不含后视镜外廓为 4672/1855/1938 mm。([汽车目录][2])
* 闭合 `150766` 的 G 63 4x4² 独立宽体高车身，按 194.5×82.5×88.8 in 换算并取整为 4940/2096/2256 mm。([MotorTrend][3])
* 闭合 `109310` 的 G 63 AMG 6x6 四门双排皮卡外廓，采用量产规格 5875/2110/2210 mm。([汽车杂志][4])

## 当前批次进度

* READY 映射：117
* PENDING 映射：4
* 已确认尺寸组：41
* 本轮闭合输入 Ktype：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
150551	150551	Pickup	G-Class W461	461.329	2	EU-MERCEDES-BENZ-G-CLASS-W461-290GD-CHASSIS-XLWB-01	HIGH	超长轴双门底盘车。	READY
55394_prefl	55394	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	HIGH	2012-2015改款前AMG外廓。	READY
55394_facelift	55394	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015-2018改款AMG外廓。	READY
59474_prefl	59474	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	HIGH	2012-2015改款前AMG外廓。	READY
59474_facelift	59474	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015-2018改款AMG外廓。	READY
150766	150766	SUV	G-Class W463A 4x4²	W463A	5	EU-MERCEDES-BENZ-G-CLASS-W463A-AMG-G63-4X4SQUARED-01	HIGH	门式桥宽体高车身外廓。	READY
109310	109310	Pickup	G-Class W463 6x6	W463	4	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-G63-6X6-PICKUP-01	HIGH	三轴双排四门皮卡外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W461-290GD-CHASSIS-XLWB-01	4688	1760	1984	Mercedes-Benz Public Archive — 290 GD chassis with extra long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-chassis-with-extra-long-wheelbase-1991---2000.xhtml?oid=194038773
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	4672	1855	1938	Automobile-Catalog — 2013 Mercedes-Benz G 63 AMG	https://www.automobile-catalog.com/car/2013/1782050/mercedes-benz_g_63_amg.html
EU-MERCEDES-BENZ-G-CLASS-W463A-AMG-G63-4X4SQUARED-01	4940	2096	2256	MotorTrend — 2022 Mercedes-AMG G 63 4x4 Squared First Drive	https://www.motortrend.com/reviews/2022-mercedes-amg-g63-4x4-squared-first-drive-review
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-G63-6X6-PICKUP-01	5875	2110	2210	Autocar — Mercedes-AMG G 63 6x6 review	https://www.autocar.co.uk/car-review/mercedes-amg/g-63-6x6-2013-2015
```

## 下一步优先处理

1. 闭合 `125923` 的 W460 短轴三门与长轴五门封闭车身分支。
2. 闭合 `155345` 的 W464 G 350 d Professional 标准封闭车身。
3. 分别闭合 `155346` 的 W464 底盘车及 `156393` 的 W461 `461.343` 长驾驶室底盘/钢制货台外廓。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-chassis-with-extra-long-wheelbase-1991---2000.xhtml?oid=194038773 "290 GD (chassis with extra long wheelbase), 1991 - 2000"
[2]: https://www.automobile-catalog.com/car/2013/1782050/mercedes-benz_g_63_amg.html?utm_source=chatgpt.com "2013 Mercedes-Benz G 63 AMG Specs Review (400 kW ..."
[3]: https://www.motortrend.com/reviews/2022-mercedes-amg-g63-4x4-squared-first-drive-review?utm_source=chatgpt.com "2022 Mercedes-AMG 4x4² First Drive"
[4]: https://www.autocar.co.uk/car-review/mercedes-amg/g-63-6x6-2013-2015?utm_source=chatgpt.com "Used Mercedes-AMG G 63 6x6 2013-2015 review"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10001-10100_ktype_dimension_mapping_final.tsv
- left18448_10001-10100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合最后 4 个 PENDING：W460 `200 G` 按短轴/长轴及 1987 年 10 月前后外廓拆分；W464 `BA06` 五门封闭车身、`BA09` 双门底盘驾驶室和 W461 `461.343` 底盘驾驶室均已建立完整尺寸组。([marsClassic][1])
* 已完成轻量机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，三维与来源字段非空。
* 已生成两个任务指定的最终 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：124
* PENDING 映射：0
* DIMENSION_GROUP：49
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
148191	148191	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
152952	152952	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801748	801748	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
803230	803230	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
150131	150131	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
148192	148192	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151586	151586	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801747	801747	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801867	801867	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
145523	145523	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151585	151585	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801746	801746	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801868	801868	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
147037	147037	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
151588	151588	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	HIGH		READY
148193	148193	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
151587	151587	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
801761	801761	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	HIGH		READY
801869	801869	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-SUV-01	HIGH		READY
148194	148194	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
153322	153322	Sedan	EQE V295	V295	4	EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	HIGH		READY
156146	156146	SUV	EQE SUV X294	X294	5	EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	HIGH		READY
148216	148216	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
148215	148215	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
153320	153320	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
148217	148217	SUV	EQS SUV X296	X296	5	EU-MERCEDES-BENZ-EQS-X296-SUV-01	HIGH		READY
156023	156023	SUV	EQS SUV	Z296	5	EU-MERCEDES-BENZ-EQS-Z296-MAYBACH-SUV-01	HIGH	Maybach Z296宽体外廓。	READY
146622	146622	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
147683	147683	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
145121	145121	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
154568	154568	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
147680	147680	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
146623	146623	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	HIGH		READY
146624	146624	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	HIGH		READY
145122	145122	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
154569	154569	Hatchback	EQS V297	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
151621	151621	MPV	EQT	E420	5	EU-MERCEDES-BENZ-EQT-E420-MPV-01	MEDIUM		READY
146683_long	146683	MPV	EQV E447	E447	5	EU-MERCEDES-BENZ-EQV-E447-MPV-LONG-01	HIGH	长轴车身。	READY
146683_extralong	146683	MPV	EQV E447	E447	5	EU-MERCEDES-BENZ-EQV-E447-MPV-EXTRALONG-01	HIGH	超长轴车身。	READY
158341	158341	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-AMG-SUV-01	HIGH		READY
155345	155345	SUV	G-Class W464	W464	5	EU-MERCEDES-BENZ-G-CLASS-W464-BA06-STATION-01	HIGH	BA06五门封闭车身。	READY
155346	155346	Pickup	G-Class W464	W464	2	EU-MERCEDES-BENZ-G-CLASS-W464-BA09-CHASSIS-CAB-01	HIGH	BA09双门底盘驾驶室。	READY
158343	158343	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	HIGH		READY
158340	158340	SUV	G-Class W465	W465	5	EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	HIGH		READY
158622	158622	SUV	G-Class E465	E465	5	EU-MERCEDES-BENZ-G-CLASS-E465-EV-SUV-01	HIGH	电动E465标准外廓。	READY
125923_swb_pre87	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-CLASS-W460-SWB-STATION-PRE1987-01	MEDIUM	短轴三门，1987年10月前外廓。	READY
125923_lwb_pre87	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-CLASS-W460-LWB-STATION-PRE1987-01	MEDIUM	长轴五门，1987年10月前外廓。	READY
125923_swb_1987	125923	SUV	G-Class W460	460.230	3	EU-MERCEDES-BENZ-G-CLASS-W460-SWB-STATION-1987-01	MEDIUM	短轴三门，1987年10月后外廓。	READY
125923_lwb_1987	125923	SUV	G-Class W460	460.231	5	EU-MERCEDES-BENZ-G-CLASS-W460-LWB-STATION-1987-01	MEDIUM	长轴五门，1987年10月后外廓。	READY
55580	55580	SUV	G-Class W463	463.221	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门封闭车身。	READY
12084_swb	12084	SUV	G-Class W463	463.324	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	HIGH	短轴三门封闭车身。	READY
12084_lwb	12084	SUV	G-Class W463	463.325	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门封闭车身。	READY
150551	150551	Pickup	G-Class W461	461.329	2	EU-MERCEDES-BENZ-G-CLASS-W461-290GD-CHASSIS-XLWB-01	HIGH	超长轴双门底盘车。	READY
12106	12106	SUV	G-Class W463	463.228	5	EU-MERCEDES-BENZ-G-CLASS-W463-500GE-LWB-01	HIGH		READY
114589	114589	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH		READY
150766	150766	SUV	G-Class W463A 4x4²	W463A	5	EU-MERCEDES-BENZ-G-CLASS-W463A-AMG-G63-4X4SQUARED-01	HIGH	门式桥宽体高车身外廓。	READY
114590	114590	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH		READY
59485_swb	59485	SUV	G-Class W463	463.322	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
59485_lwb	59485	SUV	G-Class W463	463.323	5	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
150550	150550	Pickup	G-Class W461	W461	2	EU-MERCEDES-BENZ-G-CLASS-W461-CHASSIS-XLWB-2007-01	MEDIUM	超长轴双门底盘车。	READY
8830_swb	8830	SUV	G-Class W461	461.335	3	EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
8830_lwb	8830	SUV	G-Class W461	461.336	5	EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
156393	156393	Pickup	G-Class W461	461.343	2	EU-MERCEDES-BENZ-G-CLASS-W461-G300CDI-CHASSIS-CAB-01	HIGH	长轴双门底盘驾驶室。	READY
143391_swb	143391	SUV	G-Class W463	463.327	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	HIGH	短轴三门车身。	READY
143391_lwb	143391	SUV	G-Class W463	463.328	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	HIGH	长轴五门车身。	READY
143392	143392	Convertible	G-Class W463	463.307	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1990-01	HIGH		READY
5951	5951	Convertible	G-Class W463	463.308	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	HIGH		READY
5955_swb	5955	SUV	G-Class W463	463.330	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	短轴三门车身。	READY
5955_lwb	5955	SUV	G-Class W463	463.331	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	长轴五门车身。	READY
12330	12330	Convertible	G-Class W463	463.306	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH	短轴三门敞篷车身。	READY
12331_swb	12331	SUV	G-Class W463	463.336	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	短轴三门封闭车身。	READY
12331_lwb	12331	SUV	G-Class W463	463.346	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	长轴五门封闭车身。	READY
125925	125925	Convertible	G-Class W463	463.303	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH		READY
125926_swb	125926	SUV	G-Class W463	463.340	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	短轴三门车身。	READY
125926_lwb	125926	SUV	G-Class W463	463.341	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	长轴五门车身。	READY
114585	114585	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	HIGH		READY
13443	13443	SUV	G-Class W463	463.231	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH		READY
15363_swb	15363	SUV	G-Class W463	463.332	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	HIGH	短轴三门封闭车身。	READY
15363_lwb	15363	SUV	G-Class W463	463.333	5	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	HIGH	长轴五门封闭车身。	READY
15364	15364	Convertible	G-Class W463	463.309	3	EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-CABRIO-01	HIGH		READY
10142_swb_pre2008	10142	SUV	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	1998-2008短轴三门封闭车身。	READY
10142_lwb_pre2008	10142	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	1998-2008长轴五门封闭车身。	READY
10142_swb_2008	10142	SUV	G-Class W463	463.222	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	2008改款短轴三门封闭车身。	READY
10142_lwb_2008	10142	SUV	G-Class W463	463.236	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	2008改款长轴五门封闭车身。	READY
10142_lwb_2012	10142	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	MEDIUM	2012-2015改款长轴五门外廓。	READY
10143_pre2008	10143	Convertible	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	HIGH	1998-2008短轴三门敞篷车身。	READY
10143_2008	10143	Convertible	G-Class W463	463.202	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	HIGH	2008改款短轴三门敞篷车身。	READY
45896_swb	45896	SUV	G-Class W463	463.247	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	短轴三门封闭车身。	READY
45896_lwb	45896	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	长轴五门封闭车身。	READY
59473_swb	59473	SUV	G-Class W463	463.222	3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	HIGH	2008改款短轴三门封闭车身。	READY
59473_lwb_pre2012	59473	SUV	G-Class W463	463.236	5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	HIGH	2008-2012长轴五门封闭车身。	READY
59473_lwb_2012	59473	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	MEDIUM	2012-2015改款长轴五门外廓。	READY
114588	114588	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	HIGH		READY
12143_swb_1999	12143	SUV	G-Class W463		3	EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	HIGH	早期自然吸气AMG短轴三门外廓。	READY
12143_lwb_1999	12143	SUV	G-Class W463		5	EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	HIGH	早期自然吸气AMG长轴五门外廓。	READY
12143_lwb_comp	12143	SUV	G-Class W463	463.270	5	EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	HIGH	AMG Compressor长轴五门外廓。	READY
18100	18100	SUV	G-Class W463	463.270	5	EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	HIGH		READY
55394_prefl	55394	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	HIGH	2012-2015改款前AMG外廓。	READY
55394_facelift	55394	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015-2018改款AMG外廓。	READY
109310	109310	Pickup	G-Class W463 6x6	W463	4	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-G63-6X6-PICKUP-01	HIGH	三轴双排四门皮卡外廓。	READY
59474_prefl	59474	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	HIGH	2012-2015改款前AMG外廓。	READY
59474_facelift	59474	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	HIGH	2015-2018改款AMG外廓。	READY
154466	154466	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	HIGH		READY
154458	154458	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
142497	142497	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	HIGH	改款前H247外廓。	READY
154461	154461	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154464	154464	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154463	154463	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
154465	154465	SUV	GLA H247	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	HIGH	2023改款H247外廓。	READY
115054	115054	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-AMG-SUV-01	HIGH		READY
110035	110035	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
107540	107540	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100449	100449	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100453	100453	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100466	100466	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
117987	117987	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100467	100467	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100472	100472	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100476	100476	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100474	100474	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
115062	115062	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
115065	115065	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100477	100477	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
100478	100478	SUV	GLA X156	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_10001-10100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQE-V295-SEDAN-01	4946	1961	1510	Mercedes-Benz EQE Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-eqe-saloon-2024-september-v295-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-EQE-X294-SUV-01	4863	1940	1686	Mercedes-Benz EQE SUV official press release	https://media.mercedes-benz.ca/releases/release-c0cb899bf0911f20b01ae662da01cdfd-the-new-eqe-suv-high-tech-and-luxury-meet-versatility
EU-MERCEDES-BENZ-EQE-V295-AMG-SEDAN-01	4964	1906	1495	Mercedes-AMG EQE Owner's Manual Supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-bh/pdf/mercedes-amg-eqe-owners-manual-supplement-september-2024-1.pdf
EU-MERCEDES-BENZ-EQE-X294-AMG-SUV-01	4879	1931	1672	Mercedes-Benz EQE SUV Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.in/passengercars/services/manuals.html/eqe-suv-2026-07-x294-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-EQS-X296-SUV-01	5125	1959	1718	Mercedes-Benz EQS SUV Owner's Manual	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-suv-2022-06-x296-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQS-Z296-MAYBACH-SUV-01	5125	2034	1721	Mercedes-Benz EQS SUV Owner's Manual (Mercedes-Maybach)	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-suv-2025-03-z296-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	5216	1926	1512	Mercedes-Benz EQS Owner's Manual	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/eqs-saloon-2023-09-v297-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-EQS-V297-AMG-HATCHBACK-01	5223	1926	1513	Mercedes-Benz EQS Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.uk/passengercars/services/manuals.html/eqs-saloon-2023-09-v297-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-EQT-E420-MPV-01	4498	1859	1819	EV Database Mercedes-Benz EQT 200 Standard	https://ev-database.org/car/1908/Mercedes-Benz-EQT-200-Standard
EU-MERCEDES-BENZ-EQV-E447-MPV-LONG-01	5140	1928	1910	Mercedes-Benz EQV E447 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-is/pdf/mercedes-eqv-fjolnota-b%C3%ADll-2021-ma%C3%AD-e447-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-EQV-E447-MPV-EXTRALONG-01	5370	1928	1910	Mercedes-Benz EQV E447 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-is/pdf/mercedes-eqv-fjolnota-b%C3%ADll-2021-ma%C3%AD-e447-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W465-AMG-SUV-01	4873	1984	1971	Mercedes-Benz G-Class W465 Owner's Manual (Mercedes-AMG G 63)	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-g-class-suv-2024-april-w465-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W464-BA06-STATION-01	4780	1911	2098	Mercedes-Benz G-Class Governmental Business; EDR Magazine — BR464 BA06	https://ggb.mercedes-benz.com/en/vehicles/base-vehicles-model-series-464/mercedes-benz-g-350-d-station-wagon;https://www.edrmagazine.eu/mercedes-benz-a-new-g-class-after-42-years-of-history
EU-MERCEDES-BENZ-G-CLASS-W464-BA09-CHASSIS-CAB-01	5397	1900	2108	Mercedes-Benz G-Class Governmental Business; EDR Magazine — BR464 BA09	https://ggb.mercedes-benz.com/en/vehicles/base-vehicles-model-series-464/mercedes-benz-g-350-d-chassis-cab;https://www.edrmagazine.eu/mercedes-benz-a-new-g-class-after-42-years-of-history
EU-MERCEDES-BENZ-G-CLASS-W465-SUV-01	4825	1931	1973	Mercedes-Benz G-Class W465 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-g-class-suv-2024-april-w465-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-E465-EV-SUV-01	4680	1985	1990	Mercedes-Benz Japan G 580 with EQ Technology official page	https://www.mercedes-benz.co.jp/passengercars/models/suv/g-class-electric/overview.html
EU-MERCEDES-BENZ-G-CLASS-W460-SWB-STATION-PRE1987-01	3945	1700	1960	Mercedes-Benz Public Archive — 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-CLASS-W460-LWB-STATION-PRE1987-01	4395	1700	1950	Mercedes-Benz Public Archive — 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-CLASS-W460-SWB-STATION-1987-01	3955	1700	1925	Mercedes-Benz Public Archive — 230 G short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640
EU-MERCEDES-BENZ-G-CLASS-W460-LWB-STATION-1987-01	4405	1700	1920	Mercedes-Benz Public Archive — 230 G long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-long-wheelbase-1979---1989.xhtml?oid=190007641
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1990-01	4635	1690	1936	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-long-wheelbase-1990---1994.xhtml?oid=191039017
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1990-01	4185	1690	1908	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016
EU-MERCEDES-BENZ-G-CLASS-W461-290GD-CHASSIS-XLWB-01	4688	1760	1984	Mercedes-Benz Public Archive — 290 GD chassis with extra long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-chassis-with-extra-long-wheelbase-1991---2000.xhtml?oid=194038773
EU-MERCEDES-BENZ-G-CLASS-W463-500GE-LWB-01	4670	1810	1963	Mercedes-Benz Public Archive — 500 GE V8	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-GE-V8-1993---1994.xhtml?oid=191039032
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-FACELIFT-2015-01	4769	1855	1938	Mercedes-Benz G-Class Owner's Manual, Edition 2015-1a	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-g-class-suv-2015-july-463-comand-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W463A-AMG-G63-4X4SQUARED-01	4940	2096	2256	MotorTrend — 2022 Mercedes-AMG G 63 4x4 Squared First Drive	https://www.motortrend.com/reviews/2022-mercedes-amg-g63-4x4-squared-first-drive-review
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-STATION-01	4230	1760	1931	Mercedes-Benz Public Archive — G 400 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-short-wheelbase-2001---2006.xhtml?oid=191039047
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-LWB-STATION-01	4680	1760	1936	Mercedes-Benz Public Archive — G 400 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-long-wheelbase-2001---2006.xhtml?oid=191039048
EU-MERCEDES-BENZ-G-CLASS-W461-CHASSIS-XLWB-2007-01	4688	1760	1984	Mercedes-Benz Public Archive — G-Class extra-long-wheelbase chassis	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-chassis-with-extra-long-wheelbase-1991---2000.xhtml?oid=194038773
EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-SWB-STATION-01	4015	1700	1940	Mercedes-Benz Public Archive — 290 GD Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-Turbodiesel-short-wheelbase-1997---2001-from-2001-G-290-Turbodiesel.xhtml?oid=191011040
EU-MERCEDES-BENZ-G-CLASS-W461-G290TD-LWB-STATION-01	4465	1700	1945	Mercedes-Benz Public Archive — 290 GD Turbodiesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-Turbodiesel-long-wheelbase-1997---2001-from-2001-G-290-Turbodiesel.xhtml?oid=191011041
EU-MERCEDES-BENZ-G-CLASS-W461-G300CDI-CHASSIS-CAB-01	5192	1850	2090	GoAuto — Mercedes-Benz G300 CDI Professional Cab Chassis	https://www.goauto.com.au/car-reviews/mercedes-benz/g-wagon/g300-cdi-professional/2017-01-13/44909.html
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1990-01	4225	1690	1940	Mercedes-Benz Public Archive — 300 GD/G 300 Diesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-GD-from-091993-G-300-Diesel-short-wheelbase-1990---1994.xhtml?oid=191039016
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-1996-01	4275	1760	1941	Mercedes-Benz Public Archive — G 300 Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-short-wheelbase-1996---2000.xhtml?oid=191039018
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-1996-01	4230	1760	1931	Mercedes-Benz Public Archive — G 300 Turbodiesel short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-short-wheelbase-1996---2000.xhtml?oid=191039018
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-1996-01	4680	1760	1936	Mercedes-Benz Public Archive — G 300 Turbodiesel long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-300-Turbodiesel-long-wheelbase-1996---2000.xhtml?oid=191039019
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-CABRIO-2008-01	4257	1760	1941	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-CLASS-W463-SWB-STATION-2008-01	4212	1760	1931	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-short-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039059
EU-MERCEDES-BENZ-G-CLASS-W463-LWB-STATION-2008-01	4662	1760	1931	Mercedes-Benz Public Archive — G 320 CDI/G 350 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2008---2010-from-062009-G-350-CDI-only-for-export-until-2012.xhtml?oid=191039060
EU-MERCEDES-BENZ-G-CLASS-W463-STANDARD-FACELIFT-2015-01	4764	1867	1954	Mercedes-Benz G-Class Owner's Manual, Edition 2015-1a	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-do/pdf/mercedes-g-class-suv-2015-july-463-comand-owners-manual-1.pdf
EU-MERCEDES-BENZ-G-CLASS-W463-G400CDI-SWB-CABRIO-01	4275	1760	1941	Mercedes-Benz Public Archive — G 400 CDI short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-400-CDI-short-wheelbase-2001---2006.xhtml?oid=191039047
EU-MERCEDES-BENZ-G-CLASS-W463-G55-AMG-COMPRESSOR-LWB-01	4662	1864	1931	Mercedes-Benz Public Archive — G 55 AMG Compressor long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-55-AMG-Compressor-long-wheelbase-2004---2008.xhtml?oid=191039057
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-PREFL-2012-01	4672	1855	1938	Automobile-Catalog — 2013 Mercedes-Benz G 63 AMG	https://www.automobile-catalog.com/car/2013/1782050/mercedes-benz_g_63_amg.html
EU-MERCEDES-BENZ-G-CLASS-W463-AMG-G63-6X6-PICKUP-01	5875	2110	2210	Autocar — Mercedes-AMG G 63 6x6 review	https://www.autocar.co.uk/car-review/mercedes-amg/g-63-6x6-2013-2015
EU-MERCEDES-BENZ-GLA-H247-AMG-SUV-FACELIFT-01	4436	1849	1590	Mercedes-Benz GLA H247 Owner's Manual (Mercedes-AMG vehicles)	https://www.mercedes-benz.co.uk/vans/services/manuals.html/gla-suv-2026-07-h247-mbux/vehicle-data/vehicle-dimensions-mercedes-amg-vehicles
EU-MERCEDES-BENZ-GLA-H247-SUV-FACELIFT-01	4412	1834	1616	Mercedes-Benz GLA H247 Owner's Manual	https://www.mercedes-benz.com.do/en/services/manuals/gla-suv-2023-07-h247-mbux/vehicle-data/vehicle-dimensions/
EU-MERCEDES-BENZ-GLA-H247-SUV-PREFL-01	4410	1834	1611	Mercedes-Benz GLA H247 Owner's Manual	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-kw/pdf/mercedes-gla-suv-2020-september-h247-mbux-owners-manual-1.pdf
EU-MERCEDES-BENZ-GLA-X156-AMG-SUV-01	4445	1804	1479	Mercedes-AMG GLA 45 4MATIC brochure	https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-GLA-45-AMG-2014-CN.pdf
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494	Mercedes-Benz GLA X156 official brochure	https://www.mercedes-benzcaribbean.com/assets/themes/mb-caribbean/media/vehicles/class-gla/suv/GLA_X156_ePaper_UP_1218_02_ENG_Final.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_10001-10100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-G-short-wheelbase-1979---1989.xhtml?oid=190007640 "230 G (short wheelbase), 1979 - 1989"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（885 行）
- 累计尺寸组：dimension_groups_final.tsv（246 行）

