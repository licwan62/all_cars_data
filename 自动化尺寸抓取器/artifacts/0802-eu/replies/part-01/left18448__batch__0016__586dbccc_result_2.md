# 任务：left18448 第 1501-1600 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0016__586dbccc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1501-1600 行

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
left18448 第 1501-1600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1501-1600_ktype_dimension_mapping_final.tsv
- left18448_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-TT-I-8N-COUPE-FWD-01	4041	1764	1346
EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	4041	1764	1345
EU-AUDI-TT-I-8N-ROADSTER-FWD-01	4041	1764	1349
EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	4041	1764	1348
EU-AUDI-TT-III-8S-COUPE-01	4177	1832	1353
EU-AUDI-TT-III-8S-ROADSTER-01	4177	1832	1355

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Audi	Tt	2.0 TDI Quattro	Coupe	Allrad	Diesel	Jan 2017	-	125351
Audi	Tt	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	Jan 2017	-	125352
Audi	Tt	2.0 Tfsi	Coupe	Frontantrieb	Benzin	Jul 2014	-	106596
Audi	Tt	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	Nov 2014	-	108396
Audi	Tt	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	Jul 2014	-	106597
Audi	Tt	2.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	Nov 2014	-	108397
Audi	Tt	2.0 TTS Quattro	Coupe	Allrad	Benzin	Nov 2014	-	108402
Audi	Tt	2.0 TTS Tfsi Quattro	Cabriolet	Allrad	Benzin	Nov 2014	-	108403
Audi	Tt	2.0 TTS Tfsi Quattro	Coupe	Allrad	Benzin	Jul 2015	-	115134
Audi	Tt	2.0 TTS Tfsi Quattro	Coupe	Allrad	Benzin	Feb 2015	-	115137
Audi	Tt	2.0 TTS Tfsi Quattro	Cabriolet	Allrad	Benzin	Feb 2015	-	115138
Audi	Tt	2.5 RS Quattro	Coupe	Allrad	Benzin	May 2011	Jun 2014	11144
Audi	Tt	2.5 RS Quattro	Cabriolet	Allrad	Benzin	Mar 2012	Jun 2014	14759
Audi	Tt	2.5 RS Tfsi Quattro	Coupe	Allrad	Benzin	May 2016	-	121956
Audi	Tt	2.5 RS Tfsi Quattro	Cabriolet	Allrad	Benzin	May 2016	-	121959
Audi	Tt	3.2 VR6 Quattro	Coupe	Allrad	Benzin	Jul 2003	Jun 2006	17144
Audi	Tt	3.2 VR6 Quattro	Cabriolet	Allrad	Benzin	Jul 2003	Jun 2006	17472
Audi	Tt	TTS Tfsi Quattro	Cabriolet	Allrad	Benzin	Nov 2020	-	143490
Audi	Tt	TTS Tfsi Quattro	Coupe	Allrad	Benzin	Jan 2021	-	144132
Austin	Allegro i	1	Stufenheck	Frontantrieb	Benzin	Jan 1980	Oct 1983	13839
Austin	Allegro i	1.1	Schrägheck	Frontantrieb	Benzin	Jan 1975	Oct 1979	13818
Austin	Allegro i	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1975	Dec 1982	13819
Austin	Allegro i	1.3	Schrägheck	Frontantrieb	Benzin	Jan 1979	Oct 1983	13840
Austin	Allegro i	1.3	Stufenheck	Frontantrieb	Benzin	Feb 1973	Dec 1975	127242
Austin	Allegro i	1.3	Kombi	Frontantrieb	Benzin	Jan 1981	Dec 1983	127244
Austin	Allegro i	1.5	Stufenheck	Frontantrieb	Benzin	Feb 1973	Dec 1979	127243
Austin	Allegro i	1750	Schrägheck	Frontantrieb	Benzin	Jan 1975	Oct 1979	13820
Austin	Ambassador i fastback	2	Schrägheck	Frontantrieb	Benzin	Mar 1982	Oct 1984	13841
Austin	Apache	1300	Stufenheck	Heckantrieb	Benzin	Nov 1971	Oct 1974	13961
Austin	Apache	1300 TC	Stufenheck	Heckantrieb	Benzin	Nov 1971	Oct 1974	13962
Austin	Maxi ii fastback	1750	Schrägheck	Frontantrieb	Benzin	Oct 1980	Dec 1982	14112
Austin	Maxi ii fastback	1750 HLS	Schrägheck	Frontantrieb	Benzin	Oct 1980	Dec 1982	14113
Austin	Metro	1.3	Schrägheck	Frontantrieb	Benzin	Oct 1980	Dec 1983	16792
Austin	Mini	850	Schrägheck	Frontantrieb	Benzin	Sep 1969	Oct 1985	143342
Austin	Montego	1.3	Stufenheck	Frontantrieb	Benzin	Oct 1984	Aug 1988	13987
Austin	Montego	2	Kombi	Frontantrieb	Benzin	Oct 1984	Aug 1991	13989
Austin	Montego	2	Stufenheck	Frontantrieb	Benzin	Jan 1988	Dec 1993	127241
Austin	Princess	1700	Stufenheck	Frontantrieb	Benzin	Oct 1978	Oct 1982	13842
Austin	Princess	2000	Stufenheck	Frontantrieb	Benzin	Oct 1978	Oct 1982	13843
Austin	Princess	2200	Stufenheck	Frontantrieb	Benzin	Oct 1978	Oct 1982	13844
Austin-healey	100	2.6	Cabriolet	Heckantrieb	Benzin	Jan 1957	Dec 1959	127250
Austin-healey	3000 mk.i	2.9	Cabriolet	Heckantrieb	Benzin	Jan 1959	Dec 1961	127249
Austin-healey	3000 mk.iii	3.0 Sport	Cabriolet	Heckantrieb	Benzin	Mar 1964	Oct 1968	13846
Austin-healey	Sprite mk.iii	1.1	Cabriolet	Heckantrieb	Benzin	Mar 1964	Sep 1966	13845
Austin-healey	Sprite mk.iv	1.3	Cabriolet	Heckantrieb	Benzin	Mar 1966	Oct 1971	13847
Austin-healey	Sprite mk.iv	1.3	Cabriolet	Heckantrieb	Benzin	Mar 1966	Oct 1971	127251
Autobianchi	Primula	1.2	Coupe	Frontantrieb	Benzin	Jun 1968	Oct 1970	127252
Autobianchi	Y10	1.1	Schrägheck	Frontantrieb	Benzin	Feb 1990	Sep 1992	127254
Autobianchi	Y10	1.1 4WD	Schrägheck	Allrad	Benzin	Feb 1990	Apr 1991	127253
BAC	Mono	2.5	Cabriolet	Heckantrieb	Benzin	Apr 2019	-	158108
BAC	Mono	2.5 R	Cabriolet	Heckantrieb	Benzin	Apr 2019	-	158109
Baic	Beijing x55	1.5	SUV	Frontantrieb	Benzin	Sep 2024	-	160574
Baic	Beijing x55	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Sep 2024	-	160575
Baic	Bj30	1.5 E 4X4	SUV	Allrad	Benzin/Elektro	Jul 2024	-	160537
Baic	Bj60	Mhev	SUV	Allrad	Benzin/Elektro	Apr 2024	-	801295
Baic	Senova x25	1.5	SUV	Frontantrieb	Benzin	Nov 2015	-	117679
Baic	Senova x35	1.5	SUV	Frontantrieb	Benzin	May 2016	-	120689
Baic	Senova x55	1.5	SUV	Frontantrieb	Benzin	Dec 2023	-	157723
Baic	Senova x55	1.5 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Dec 2023	-	157724
Baic	Senova x65	2.0 T	SUV	Frontantrieb	Benzin	Mar 2015	-	112224
Baic	X35	1.5	SUV	Frontantrieb	Benzin	Sep 2025	-	802369
Baic	X75	GDI	SUV	Frontantrieb	Benzin	Apr 2024	-	801360
Baic	X75	LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	Apr 2024	-	801361
Barkas	B 1000	1	Kasten	Frontantrieb	Benzin	Jan 1976	Dec 1991	6005
Barkas	B 1000	1	Bus	Frontantrieb	Benzin	Apr 1967	Dec 1991	6006
Barkas	B 1000	1	Bus	Frontantrieb	Benzin	Jan 1976	Dec 1991	6007
BAW	Bj 212	2.0 4X4	Geländewagen geschlossen	Allrad	Benzin	Jul 2022	-	148181
BAW	Pony	EV	Schrägheck	Heckantrieb	Elektro	Jun 2022	-	148079
Beijing	X7	GDI	SUV	Frontantrieb	Benzin	Dec 2023	-	157725
Bentley	Arnage	6.7 V8	Stufenheck	Heckantrieb	Benzin	Sep 1999	Aug 2003	13876
Bentley	Arnage	6.8 V8 T	Stufenheck	Heckantrieb	Benzin	Feb 2002	Oct 2009	16607
Bentley	Azure	6.8	Cabriolet	Heckantrieb	Benzin	Jun 2006	-	34869
Bentley	Azure	6.75 V8	Cabriolet	Heckantrieb	Benzin	Sep 1995	Aug 1999	16850
Bentley	Azure	6.75 V8	Cabriolet	Heckantrieb	Benzin	Aug 1999	Jun 2006	16852
Bentley	Azure	6.75 V8 Mulliner	Cabriolet	Heckantrieb	Benzin	Aug 1999	Jun 2006	16851
Bentley	Bentayga	6	SUV	Allrad	Benzin	Oct 2015	-	117494
Bentley	Bentayga	3.0 Hybrid	SUV	Allrad	Benzin/Elektro	Jan 2023	-	151616
Bentley	Bentayga	4.0 D	SUV	Allrad	Diesel	Jan 2017	-	124751
Bentley	Bentayga	4.0 Speed	SUV	Allrad	Benzin	Sep 2025	-	802250
Bentley	Brooklands	6.8	Coupe	Heckantrieb	Benzin	Mar 2008	-	34870
Bentley	Brooklands	6.7 R	Stufenheck	Heckantrieb	Benzin	Oct 1992	Sep 1997	100706
Bentley	Continental	4	Coupe	Allrad	Benzin	Jan 2014	Jul 2018	122119
Bentley	Continental	6	Stufenheck	Allrad	Benzin	Mar 2005	Dec 2010	18595
Bentley	Continental	6	Coupe	Allrad	Benzin	Sep 2012	Jul 2018	57514
Bentley	Continental	4.0 AWD	Cabriolet	Allrad	Benzin	Jan 2013	Jul 2018	122120
Bentley	Continental	4.0 Flex	Coupe	Allrad	Benzin/Ethanol	Oct 2014	Jul 2018	108356
Bentley	Continental	4.0 Flex	Coupe	Allrad	Benzin/Ethanol	Apr 2012	Jul 2018	119109
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	Nov 2011	Jul 2018	11928
Bentley	Continental	6.0 CS ISR	Cabriolet	Allrad	Benzin/Ethanol	Mar 2011	Jun 2014	11945
Bentley	Continental	6.0 Flex	Coupe	Allrad	Benzin/Ethanol	Feb 2008	May 2010	54822
Bentley	Continental	6.0 Flex	Coupe	Allrad	Benzin/Ethanol	May 2015	Jul 2018	115816
Bentley	Continental	6.0 Flex	Stufenheck	Allrad	Benzin/Ethanol	Jun 2010	Dec 2013	119715
Bentley	Continental	6.0 Flex	Coupe	Allrad	Benzin/Ethanol	Jan 2010	Jul 2010	802167
Bentley	Continental	6.0 Flex AWD	Cabriolet	Allrad	Benzin/Ethanol	Mar 2010	Dec 2013	34872
Bentley	Continental	6.0 Flex AWD	Cabriolet	Allrad	Benzin/Ethanol	Sep 2011	Dec 2015	58428
Bentley	Continental	6.0 Flex AWD	Cabriolet	Allrad	Benzin/Ethanol	May 2015	Jul 2018	115817
Bentley	Continental	6.0 GT	Coupe	Allrad	Benzin	Jun 2003	Dec 2011	17827
Bentley	Continental	6.0 GTC Speed AWD	Cabriolet	Allrad	Benzin	Sep 2012	Jul 2018	58832
Bentley	Continental	6.0 GTC Speed AWD	Cabriolet	Allrad	Benzin	May 2014	Jul 2018	106277
Bentley	Continental	6.0 GTC Speed Flex AWD	Cabriolet	Allrad	Benzin/Ethanol	Aug 2007	Apr 2011	800223


--- Round 1 / 首次发送 ---
## 更新点

* Audi TT 的 19 个 Ktype 已完成映射：标准 TT 复用 4 个既有尺寸组；TTS、第二代 TT RS、第三代 TT RS 因外廓长度或高度不同，新建 6 个尺寸组。Audi 官方资料明确给出了 TT RS 的不含后视镜宽度。([汽车目录][1])
* 已闭合部分 Austin、Austin-Healey、Autobianchi 和 BAC 聚类；相同发动机差异未重复建组。Austin Apache 已确认属于四门 ADO16 衍生轿车，标准版与 TC 共用外廓。([汽车目录][2])
* Austin-Healey Sprite Mk III、Mk IV 和 Autobianchi Y10 前驱/四驱已按实际外廓差异分别建组。([汽车目录][3])
* Allegro Series 3、Montego 改款边界及 Bentley 多代际记录暂未强制落盘，避免在物理分支尚未完全闭合时错误复用。

## 当前批次进度

* READY Ktype：42 / 100
* READY 映射行：42
* PENDING Ktype：58
* 本轮首次创建尺寸组：24
* 复用跨批次既有尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125351	125351	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	8S标准Coupe外廓。	READY
125352	125352	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	8S标准Roadster外廓。	READY
106596	106596	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	8S标准Coupe外廓。	READY
108396	108396	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	8S标准Roadster外廓。	READY
106597	106597	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	quattro未改变标准Coupe外廓。	READY
108397	108397	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	quattro未改变标准Roadster外廓。	READY
108402	108402	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
108403	108403	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	TTS专属Roadster外廓。	READY
115134	115134	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
115137	115137	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
115138	115138	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	TTS专属Roadster外廓。	READY
11144	11144	Coupe	TT II	8J	3	EU-AUDI-TT-II-8J-RS-COUPE-01	HIGH	8J TT RS专属外廓。	READY
14759	14759	Convertible	TT II	8J	2	EU-AUDI-TT-II-8J-RS-ROADSTER-01	HIGH	8J TT RS Roadster外廓。	READY
121956	121956	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-RS-COUPE-01	HIGH	8S TT RS专属外廓。	READY
121959	121959	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-RS-ROADSTER-01	HIGH	8S TT RS Roadster外廓。	READY
17144	17144	Coupe	TT I	8N	3	EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	HIGH	8N quattro Coupe外廓。	READY
17472	17472	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	HIGH	8N quattro Roadster外廓。	READY
143490	143490	Convertible	TT III facelift	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	facelift TTS Roadster沿用既定外廓。	READY
144132	144132	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	facelift TTS Coupe沿用既定外廓。	READY
127242	127242	Sedan	Allegro I	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	早期四门Allegro外廓。	READY
127244	127244	Wagon	Allegro I Series 3	ADO67	3	EU-AUSTIN-ALLEGRO-I-ADO67-WAGON-SERIES-3-01	HIGH	Series 3三门Estate外廓。	READY
13841	13841	Hatchback	Ambassador I		5	EU-AUSTIN-AMBASSADOR-I-HATCHBACK-01	HIGH	五门fastback外廓。	READY
13961	13961	Sedan	Apache I	ADO16	4	EU-AUSTIN-APACHE-I-SEDAN-01	HIGH	四门Apache标准外廓。	READY
13962	13962	Sedan	Apache I	ADO16	4	EU-AUSTIN-APACHE-I-SEDAN-01	HIGH	TC配置未改变车身外廓。	READY
14112	14112	Hatchback	Maxi II	ADO14	5	EU-AUSTIN-MAXI-II-HATCHBACK-01	HIGH	五门Maxi II fastback外廓。	READY
14113	14113	Hatchback	Maxi II	ADO14	5	EU-AUSTIN-MAXI-II-HATCHBACK-01	HIGH	HLS配置未改变车身外廓。	READY
16792	16792	Hatchback	Metro I	LC8	3	EU-AUSTIN-METRO-I-HATCHBACK-3D-01	HIGH	1980-1983三门Metro外廓。	READY
143342	143342	Hatchback	Mini (ADO20)	ADO20	2	EU-AUSTIN-MINI-ADO20-SEDAN-2D-01	MEDIUM	输入为Schrägheck；物理车身按经典Mini两门saloon归组。	READY
13842	13842	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	四门Princess外廓。	READY
13843	13843	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	发动机版本未改变外廓。	READY
13844	13844	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	发动机版本未改变外廓。	READY
127250	127250	Convertible	100-Six		2	EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	HIGH	100-Six量产外廓。	READY
127249	127249	Convertible	3000 Mk I		2	EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	HIGH	3000 Mk I外廓。	READY
13846	13846	Convertible	3000 Mk III	BJ8	2	EU-AUSTIN-HEALEY-3000-MK-III-CONVERTIBLE-01	HIGH	BJ8外廓。	READY
13845	13845	Convertible	Sprite Mk III	HAN8	2	EU-AUSTIN-HEALEY-SPRITE-MK-III-CONVERTIBLE-01	HIGH	HAN8外廓。	READY
13847	13847	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH	HAN9外廓。	READY
127251	127251	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH	与同代HAN9共用外廓。	READY
127252	127252	Coupe	Primula I		2	EU-AUTOBIANCHI-PRIMULA-I-COUPE-01	HIGH	Primula Coupe两门外廓。	READY
127254	127254	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-FWD-01	HIGH	Series II前驱三门外廓。	READY
127253	127253	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-4WD-01	HIGH	4WD悬架高度与车宽不同，独立归组。	READY
158108	158108	Convertible	Mono I		0	EU-BAC-MONO-I-ROADSTER-01	HIGH	无传统车门的单座开放式车身。	READY
158109	158109	Convertible	Mono R		0	EU-BAC-MONO-R-I-ROADSTER-01	HIGH	Mono R专属外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-TT-III-8S-TTS-COUPE-01	4191	1832	1343	Auto-Data Audi TT model specifications	https://www.auto-data.net/en/audi-tt-model-519
EU-AUDI-TT-III-8S-TTS-ROADSTER-01	4191	1832	1345	Auto-Data Audi TT model specifications	https://www.auto-data.net/en/audi-tt-model-519
EU-AUDI-TT-II-8J-RS-COUPE-01	4198	1842	1342	Automobile-Catalog 2014 Audi TT RS Coupe	https://www.automobile-catalog.com/car/2014/1438205/audi_tt_rs_coupe.html
EU-AUDI-TT-II-8J-RS-ROADSTER-01	4189	1842	1348	Automobile-Catalog 2014 Audi TT RS Roadster	https://www.automobile-catalog.com/car/2014/1438220/audi_tt_rs_roadster.html
EU-AUDI-TT-III-8S-RS-COUPE-01	4191	1832	1344	Audi UK TT RS official pricelist	https://press.audi.co.uk/assets/documents/original/23309-AudiUK00019252AudiTTRSCoup%C3%A9andRoadster.pdf
EU-AUDI-TT-III-8S-RS-ROADSTER-01	4191	1832	1346	Audi UK TT RS Roadster technical data	https://press.audi.co.uk/assets/documents/original/23564-AudiUK00001393AudiTTRSRoadsterStronic.pdf
EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	3855	1613	1397	Carfolio Austin Allegro 1300	https://www.carfolio.com/austin-allegro-1300-53097
EU-AUSTIN-ALLEGRO-I-ADO67-WAGON-SERIES-3-01	3995	1630	1440	Automobile-Catalog 1980 Austin Allegro Estate 1.5 HL	https://www.automobile-catalog.com/car/1980/256745/austin_allegro_estate_1_5_hl.html
EU-AUSTIN-AMBASSADOR-I-HATCHBACK-01	4555	1730	1400	Automobile-Catalog 1982 Austin Ambassador 2.0 HLS	https://www.automobile-catalog.com/car/1982/257450/austin_ambassador_2_0_hls_automatic.html
EU-AUSTIN-APACHE-I-SEDAN-01	4060	1530	1340	Carfolio 1977 Leyland Austin Apache TC	https://www.carfolio.com/leyland-austin-apache-tc-114378
EU-AUSTIN-MAXI-II-HATCHBACK-01	4022	1629	1404	Automobile-Catalog 1981 Austin Maxi 2 1750 HLS	https://www.automobile-catalog.com/car/1981/256550/austin_maxi_2_1750_hls.html
EU-AUSTIN-METRO-I-HATCHBACK-3D-01	3405	1549	1369	Automobile-Catalog 1981 Austin Metro 1.3 S	https://www.automobile-catalog.com/car/1981/257015/austin_metro_1_3_s.html
EU-AUSTIN-MINI-ADO20-SEDAN-2D-01	3054	1410	1346	Automobile-Catalog 1969 Austin Mini 850 Mk II	https://www.automobile-catalog.com/car/1969/256370/austin_mini_850_mk_ii.html
EU-AUSTIN-PRINCESS-I-SEDAN-01	4455	1730	1409	Automobile-Catalog 1980 Princess 2200 HLS	https://www.automobile-catalog.com/car/1980/168575/princess_2200_hls_automatic.html
EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	4001	1537	1244	Automobile-Catalog 1957 Austin-Healey 100 Six	https://www.automobile-catalog.com/car/1957/258620/austin-healey_100_six.html
EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	4001	1524	1250	Automobile-Catalog 1959 Austin-Healey 3000 2+2	https://www.automobile-catalog.com/car/1959/258740/austin-healey_3000_22.html
EU-AUSTIN-HEALEY-3000-MK-III-CONVERTIBLE-01	4001	1540	1240	Automobile-Catalog 1965 Austin-Healey 3000 Mk III	https://www.automobile-catalog.com/car/1965/258860/austin-healey_3000_mk_iii.html
EU-AUSTIN-HEALEY-SPRITE-MK-III-CONVERTIBLE-01	3496	1346	1264	Automobile-Catalog 1965 Austin-Healey Sprite Mk III	https://www.automobile-catalog.com/car/1965/75695/austin-healey_sprite_mk_iii.html
EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	3496	1394	1200	Automobile-Catalog 1969 Austin-Healey Sprite Mk IV	https://www.automobile-catalog.com/car/1969/1698665/austin-healey_sprite_mk_iv.html
EU-AUTOBIANCHI-PRIMULA-I-COUPE-01	3785	1580	1350	Automobile-Catalog 1968 Autobianchi Primula Coupe	https://www.automobile-catalog.com/car/1968/259160/autobianchi_primula_coupe.html
EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-FWD-01	3392	1507	1440	Automobile-Catalog 1990 Lancia Y10 Fire 1.1 i.e. LX	https://www.automobile-catalog.com/car/1990/1381220/lancia_y10_fire_1_1_i_e__lx_cat.html
EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-4WD-01	3392	1537	1460	Automobile-Catalog 1990 Lancia Y10 4WD i.e.	https://www.automobile-catalog.com/car/1990/1381160/lancia_y10_4wd_i_e_.html
EU-BAC-MONO-I-ROADSTER-01	3952	1836	1110	Encycarpedia BAC Mono 2.5	https://www.encycarpedia.com/bac/16-mono-2-5-roadster
EU-BAC-MONO-R-I-ROADSTER-01	3977	1836	1090	Carfolio BAC Mono R	https://www.carfolio.com/bac-mono-r-618563
```

## 下一步优先处理

1. 闭合 Allegro Series 1/2/3 的门数与改款分支，以及 Montego 轿车、旅行版改款边界。
2. 批量完成 BAIC、Beijing、BAW 与 Barkas 的官方尺寸组。
3. 按 Azure、Arnage、Bentayga、Continental GT/GTC/Flying Spur 的代际与性能外观套件拆分 Bentley 剩余记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2014/1438205/audi_tt_rs_coupe.html?utm_source=chatgpt.com "2014 Audi TT RS Coupe Specs Review (250 kW / 340 PS / 335 hp) (up to mid-year 2014 for Europe )"
[2]: https://www.automobile-catalog.com/make/austin_south_africa/apache/apache/1974.html?utm_source=chatgpt.com "1974 Austin (South Africa) Apache full range specs"
[3]: https://www.automobile-catalog.com/car/1966/75695/austin-healey_sprite_mk_iii.html?utm_source=chatgpt.com "1966 Austin-Healey Sprite Mk III Specs Review (44 kW / 60 PS / 59 hp) (up to September 1966 for Europe Australia )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1501-1600_ktype_dimension_mapping_final.tsv
- left18448_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Austin Allegro Series 3 及 Montego 改款前后外廓；跨改款生产区间的 Ktype 已拆分为 `prefl`、`facelift` 派生映射。([汽车目录][1])
* 闭合 BAIC/Beijing 的 X25、X35、X55、X65、X75、X7、BJ30、BJ60 聚类；LPG、混动或发动机版本未重复建组。([PakWheels][2])
* 闭合 BAW BJ212 Classic、BAW Pony，以及 Barkas B 1000 厢式车和客车外廓。([CarNewsChina.com][3])

## 当前批次进度

* READY Ktype：69 / 100
* READY 映射行：73
* PENDING Ktype：31
* 本轮首次创建尺寸组：19
* 累计已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13839	13839	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	HIGH	Series 3 saloon外廓；门数未在Ktype中区分。	READY
13818	13818	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	输入Schrägheck，实际归入无掀背尾门的Allegro saloon外廓。	READY
13819_prefl	13819	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	MEDIUM	Ktype跨越Series 3改款，改款前物理分支。	READY
13819_facelift	13819	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	MEDIUM	Ktype跨越Series 3改款，改款后物理分支。	READY
13840	13840	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	HIGH	输入Schrägheck，实际归入Series 3 saloon外廓。	READY
127243_prefl	127243	Sedan	Allegro I Series 1/2	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	MEDIUM	Ktype跨越Series 3改款，改款前四门分支。	READY
127243_facelift	127243	Sedan	Allegro I Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	MEDIUM	Ktype跨越Series 3改款，改款后四门分支。	READY
13820	13820	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	输入Schrägheck，实际归入改款前Allegro saloon外廓。	READY
13987	13987	Sedan	Montego I	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-LOW-01	HIGH	1.3版本对应较低车高的四门外廓。	READY
13989_prefl	13989	Wagon	Montego I	LM11	5	EU-AUSTIN-MONTEGO-I-LM11-WAGON-PREFL-01	HIGH	Ktype跨越1989车型改款，改款前Estate分支。	READY
13989_facelift	13989	Wagon	Montego I facelift	LM11	5	EU-AUSTIN-MONTEGO-I-LM11-WAGON-FACELIFT-01	HIGH	Ktype跨越1989车型改款，改款后Estate分支。	READY
127241_prefl	127241	Sedan	Montego I	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-PREFL-01	HIGH	Ktype跨越1989车型改款，改款前四门分支。	READY
127241_facelift	127241	Sedan	Montego I facelift	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-FACELIFT-01	HIGH	Ktype跨越1989车型改款，改款后四门分支。	READY
160574	160574	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	第二代X55标准SUV外廓。	READY
160575	160575	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	LPG动力未改变第二代X55外廓。	READY
160537	160537	SUV	BJ30 II		5	EU-BAIC-BJ30-II-SUV-01	HIGH	第二代BJ30五门SUV外廓。	READY
801295	801295	SUV	BJ60 I		5	EU-BAIC-BJ60-I-SUV-01	HIGH	MHEV动力未改变BJ60标准外廓。	READY
117679	117679	SUV	Senova X25 I		5	EU-BAIC-SENOVA-X25-I-SUV-01	HIGH	第一代Senova X25五门外廓。	READY
120689	120689	SUV	Senova X35 I		5	EU-BAIC-SENOVA-X35-I-SUV-01	HIGH	2016款第一代Senova X35外廓。	READY
157723	157723	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	输入沿用Senova命名，对应第二代X55外廓。	READY
157724	157724	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	LPG动力未改变第二代X55外廓。	READY
112224	112224	SUV	Senova X65 I		5	EU-BAIC-SENOVA-X65-I-SUV-01	HIGH	第一代Senova X65五门外廓。	READY
802369	802369	SUV	X35 II		5	EU-BAIC-X35-II-SUV-01	HIGH	新款X35外廓，不与2016款Senova X35混用。	READY
801360	801360	SUV	X75 I		5	EU-BAIC-X75-I-SUV-01	HIGH	X75标准五门SUV外廓。	READY
801361	801361	SUV	X75 I		5	EU-BAIC-X75-I-SUV-01	HIGH	LPG动力未改变X75外廓。	READY
6005	6005	Van	B 1000		4	EU-BARKAS-B1000-VAN-01	HIGH	B 1000封闭式厢式车外廓。	READY
6006	6006	MPV	B 1000		4	EU-BARKAS-B1000-MINIBUS-01	HIGH	B 1000 Kleinbus客车外廓。	READY
6007	6007	MPV	B 1000		4	EU-BARKAS-B1000-MINIBUS-01	HIGH	生产时期差异未改变Kleinbus外廓。	READY
148181	148181	SUV	BJ212 Classic		4	EU-BAW-BJ212-CLASSIC-SUV-01	HIGH	经典BJ212封闭式四门外廓。	READY
148079	148079	Hatchback	Pony I		3	EU-BAW-PONY-I-HATCHBACK-01	HIGH	三门微型纯电车外廓。	READY
157725	157725	SUV	X7 I		5	EU-BEIJING-X7-I-SUV-01	HIGH	第一代Beijing X7五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	3908	1613	1393	Automobile-Catalog 1980 Austin Allegro 1.3 L	https://www.automobile-catalog.com/car/1980/256595/austin_allegro_1_3_l.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-LOW-01	4468	1710	1418	Automobile-Catalog 1984 Austin Montego 1.3	https://www.automobile-catalog.com/car/1984/62645/austin_montego_1_3.html
EU-AUSTIN-MONTEGO-I-LM11-WAGON-PREFL-01	4468	1710	1447	Automobile-Catalog 1984 Austin Montego Estate 1.6	https://www.automobile-catalog.com/car/1984/30680/austin_montego_estate_1_6_5-speed.html
EU-AUSTIN-MONTEGO-I-LM11-WAGON-FACELIFT-01	4465	1710	1447	Automobile-Catalog 1989 Montego Estate 2.0 GSi	https://www.automobile-catalog.com/car/1989/1701080/montego_estate_2_0_gsi.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-PREFL-01	4468	1710	1420	Automobile-Catalog 1984 Austin Montego 2.0 HLS	https://www.automobile-catalog.com/car/1984/258125/austin_montego_2_0_hls.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-FACELIFT-01	4465	1710	1420	Automobile-Catalog 1989 Montego 2.0 SL	https://www.automobile-catalog.com/car/1989/1700765/montego_2_0_sl.html
EU-BAIC-X55-II-SUV-01	4620	1886	1680	BAIC Switzerland X55 II specifications	https://www.baic-schweiz.ch/x55
EU-BAIC-BJ30-II-SUV-01	4730	1910	1790	BAIC Qatar BJ30 specifications	https://www.baic.qa/models/BJ30
EU-BAIC-BJ60-I-SUV-01	5040	1955	1925	BAIC Group B60 official specifications	https://www.baicglobal.com/models/31
EU-BAIC-SENOVA-X25-I-SUV-01	4110	1750	1545	BAIC X25 official brochure	https://cache1.pakwheels.com/system/brochures/605/original/X25_Brochure.pdf
EU-BAIC-SENOVA-X35-I-SUV-01	4300	1815	1640	17VIN 2016 BAIC Senova X35 specification	https://en.17vin.com/model/jg6ol.html
EU-BAIC-SENOVA-X65-I-SUV-01	4654	1816	1680	Zigwheels BAIC X65 2.0T specification	https://www.zigwheels.vn/en/new-cars/baic/x65/2-0t-at-premium
EU-BAIC-X35-II-SUV-01	4325	1830	1640	BAIC Group X35 official specification PDF	https://www.baicglobal.com/file/upload/2022/08/12/X35%20Specifications_20220812131259A118.pdf
EU-BAIC-X75-I-SUV-01	4745	1892	1715	BAIC Switzerland X75 specifications	https://www.baic-schweiz.ch/x75
EU-BARKAS-B1000-VAN-01	4520	1860	1850	Barkas B 1000 technical overview	https://de.wikipedia.org/wiki/Barkas_B_1000
EU-BARKAS-B1000-MINIBUS-01	4520	1860	1910	WheelsAge Barkas B1000 KB Kleinbus specifications	https://en.wheelsage.org/barkas/b1000/kb_kleinbus/specifications
EU-BAW-BJ212-CLASSIC-SUV-01	4080	1840	1870	CarNewsChina BAW BJ212 2.0 specification	https://carnewschina.com/2017/05/10/good-old-beijing-auto-works-bj212-alive-kicking/
EU-BAW-PONY-I-HATCHBACK-01	3162	1498	1585	BAW International Pony official specifications	https://bawauto.com/pony/
EU-BEIJING-X7-I-SUV-01	4710	1892	1715	China Daily Beijing X7 launch specifications	https://epaper.chinadaily.com.cn/a/202006/29/WS5ef92c0ea3107831ec75310f.html
```

## 下一步优先处理

1. 按代际闭合 Bentley Arnage 与 Azure。
2. 分离 Bentley Continental GT、GTC、Flying Spur 及改款前后外廓。
3. 闭合 Bentayga 标准版、Hybrid、Diesel 与 Speed 的车高或外部套件边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/256595/austin_allegro_1_3_l.html?utm_source=chatgpt.com "1980 Austin Allegro 1.3 L Specs Review (40.5 kW / 55 PS / 54 hp) (for Europe )"
[2]: https://cache1.pakwheels.com/system/brochures/605/original/X25_Brochure.pdf?1750228336=&utm_source=chatgpt.com "BAIC"
[3]: https://carnewschina.com/2017/05/10/good-old-beijing-auto-works-bj212-alive-kicking/?utm_source=chatgpt.com "The Good Old Beijing Auto Works BJ212 Is Alive And Kicking Again"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1501-1600_ktype_dimension_mapping_final.tsv
- left18448_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 31 个 Bentley Ktype 已闭合，新增 Arnage、Azure、Bentayga、Brooklands、Continental GT/GTC 与 Flying Spur 共 18 个尺寸组；跨改款或换代的 `18595`、`34872` 已拆成稳定派生映射。Bentayga Hybrid、MY26 Speed 以及两代 Continental GTC 的尺寸边界分别核对，不按发动机或燃料重复建组。
* 补齐当前映射引用的 4 个历史 Audi TT 缓存组来源；宽度均明确为不含后视镜口径。([汽车目录][1])
* 已完成机械检查：映射表严格 10 列，尺寸组表严格 6 列；`id` 与 `DIMENSION_GROUP_ID` 均唯一；所有引用闭合；不存在孤立尺寸组、空尺寸、空来源或 `PENDING`。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY Ktype：100
* READY 映射行：106
* PENDING：0
* DIMENSION_GROUP：65
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125351	125351	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	8S标准Coupe外廓。	READY
125352	125352	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	8S标准Roadster外廓。	READY
106596	106596	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	8S标准Coupe外廓。	READY
108396	108396	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	8S标准Roadster外廓。	READY
106597	106597	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-COUPE-01	HIGH	quattro未改变标准Coupe外廓。	READY
108397	108397	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH	quattro未改变标准Roadster外廓。	READY
108402	108402	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
108403	108403	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	TTS专属Roadster外廓。	READY
115134	115134	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
115137	115137	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	TTS专属外廓。	READY
115138	115138	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	TTS专属Roadster外廓。	READY
11144	11144	Coupe	TT II	8J	3	EU-AUDI-TT-II-8J-RS-COUPE-01	HIGH	8J TT RS专属外廓。	READY
14759	14759	Convertible	TT II	8J	2	EU-AUDI-TT-II-8J-RS-ROADSTER-01	HIGH	8J TT RS Roadster外廓。	READY
121956	121956	Coupe	TT III	8S	3	EU-AUDI-TT-III-8S-RS-COUPE-01	HIGH	8S TT RS专属外廓。	READY
121959	121959	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-RS-ROADSTER-01	HIGH	8S TT RS Roadster外廓。	READY
17144	17144	Coupe	TT I	8N	3	EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	HIGH	8N quattro Coupe外廓。	READY
17472	17472	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	HIGH	8N quattro Roadster外廓。	READY
143490	143490	Convertible	TT III facelift	8S	2	EU-AUDI-TT-III-8S-TTS-ROADSTER-01	HIGH	facelift TTS Roadster沿用既定外廓。	READY
144132	144132	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-TTS-COUPE-01	HIGH	facelift TTS Coupe沿用既定外廓。	READY
13839	13839	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	HIGH	Series 3 saloon外廓；门数未在Ktype中区分。	READY
13818	13818	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	输入Schrägheck，实际归入无掀背尾门的Allegro saloon外廓。	READY
13819_prefl	13819	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	MEDIUM	Ktype跨越Series 3改款，改款前物理分支。	READY
13819_facelift	13819	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	MEDIUM	Ktype跨越Series 3改款，改款后物理分支。	READY
13840	13840	Sedan	Allegro I Series 3	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	HIGH	输入Schrägheck，实际归入Series 3 saloon外廓。	READY
127242	127242	Sedan	Allegro I	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	早期四门Allegro外廓。	READY
127244	127244	Wagon	Allegro I Series 3	ADO67	3	EU-AUSTIN-ALLEGRO-I-ADO67-WAGON-SERIES-3-01	HIGH	Series 3三门Estate外廓。	READY
127243_prefl	127243	Sedan	Allegro I Series 1/2	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	MEDIUM	Ktype跨越Series 3改款，改款前四门分支。	READY
127243_facelift	127243	Sedan	Allegro I Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	MEDIUM	Ktype跨越Series 3改款，改款后四门分支。	READY
13820	13820	Sedan	Allegro I Series 2	ADO67		EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	输入Schrägheck，实际归入改款前Allegro saloon外廓。	READY
13841	13841	Hatchback	Ambassador I		5	EU-AUSTIN-AMBASSADOR-I-HATCHBACK-01	HIGH	五门fastback外廓。	READY
13961	13961	Sedan	Apache I	ADO16	4	EU-AUSTIN-APACHE-I-SEDAN-01	HIGH	四门Apache标准外廓。	READY
13962	13962	Sedan	Apache I	ADO16	4	EU-AUSTIN-APACHE-I-SEDAN-01	HIGH	TC配置未改变车身外廓。	READY
14112	14112	Hatchback	Maxi II	ADO14	5	EU-AUSTIN-MAXI-II-HATCHBACK-01	HIGH	五门Maxi II fastback外廓。	READY
14113	14113	Hatchback	Maxi II	ADO14	5	EU-AUSTIN-MAXI-II-HATCHBACK-01	HIGH	HLS配置未改变车身外廓。	READY
16792	16792	Hatchback	Metro I	LC8	3	EU-AUSTIN-METRO-I-HATCHBACK-3D-01	HIGH	1980-1983三门Metro外廓。	READY
143342	143342	Hatchback	Mini (ADO20)	ADO20	2	EU-AUSTIN-MINI-ADO20-SEDAN-2D-01	MEDIUM	输入为Schrägheck；物理车身按经典Mini两门saloon归组。	READY
13987	13987	Sedan	Montego I	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-LOW-01	HIGH	1.3版本对应较低车高的四门外廓。	READY
13989_prefl	13989	Wagon	Montego I	LM11	5	EU-AUSTIN-MONTEGO-I-LM11-WAGON-PREFL-01	HIGH	Ktype跨越1989车型改款，改款前Estate分支。	READY
13989_facelift	13989	Wagon	Montego I facelift	LM11	5	EU-AUSTIN-MONTEGO-I-LM11-WAGON-FACELIFT-01	HIGH	Ktype跨越1989车型改款，改款后Estate分支。	READY
127241_prefl	127241	Sedan	Montego I	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-PREFL-01	HIGH	Ktype跨越1989车型改款，改款前四门分支。	READY
127241_facelift	127241	Sedan	Montego I facelift	LM11	4	EU-AUSTIN-MONTEGO-I-LM11-SEDAN-FACELIFT-01	HIGH	Ktype跨越1989车型改款，改款后四门分支。	READY
13842	13842	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	四门Princess外廓。	READY
13843	13843	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	发动机版本未改变外廓。	READY
13844	13844	Sedan	Princess I	ADO71	4	EU-AUSTIN-PRINCESS-I-SEDAN-01	HIGH	发动机版本未改变外廓。	READY
127250	127250	Convertible	100-Six		2	EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	HIGH	100-Six量产外廓。	READY
127249	127249	Convertible	3000 Mk I		2	EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	HIGH	3000 Mk I外廓。	READY
13846	13846	Convertible	3000 Mk III	BJ8	2	EU-AUSTIN-HEALEY-3000-MK-III-CONVERTIBLE-01	HIGH	BJ8外廓。	READY
13845	13845	Convertible	Sprite Mk III	HAN8	2	EU-AUSTIN-HEALEY-SPRITE-MK-III-CONVERTIBLE-01	HIGH	HAN8外廓。	READY
13847	13847	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH	HAN9外廓。	READY
127251	127251	Convertible	Sprite Mk IV	HAN9	2	EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	HIGH	与同代HAN9共用外廓。	READY
127252	127252	Coupe	Primula I		2	EU-AUTOBIANCHI-PRIMULA-I-COUPE-01	HIGH	Primula Coupe两门外廓。	READY
127254	127254	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-FWD-01	HIGH	Series II前驱三门外廓。	READY
127253	127253	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-4WD-01	HIGH	4WD悬架高度与车宽不同，独立归组。	READY
158108	158108	Convertible	Mono I		0	EU-BAC-MONO-I-ROADSTER-01	HIGH	无传统车门的单座开放式车身。	READY
158109	158109	Convertible	Mono R		0	EU-BAC-MONO-R-I-ROADSTER-01	HIGH	Mono R专属外廓。	READY
160574	160574	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	第二代X55标准SUV外廓。	READY
160575	160575	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	LPG动力未改变第二代X55外廓。	READY
160537	160537	SUV	BJ30 II		5	EU-BAIC-BJ30-II-SUV-01	HIGH	第二代BJ30五门SUV外廓。	READY
801295	801295	SUV	BJ60 I		5	EU-BAIC-BJ60-I-SUV-01	HIGH	MHEV动力未改变BJ60标准外廓。	READY
117679	117679	SUV	Senova X25 I		5	EU-BAIC-SENOVA-X25-I-SUV-01	HIGH	第一代Senova X25五门外廓。	READY
120689	120689	SUV	Senova X35 I		5	EU-BAIC-SENOVA-X35-I-SUV-01	HIGH	2016款第一代Senova X35外廓。	READY
157723	157723	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	输入沿用Senova命名，对应第二代X55外廓。	READY
157724	157724	SUV	Beijing X55 II		5	EU-BAIC-X55-II-SUV-01	HIGH	LPG动力未改变第二代X55外廓。	READY
112224	112224	SUV	Senova X65 I		5	EU-BAIC-SENOVA-X65-I-SUV-01	HIGH	第一代Senova X65五门外廓。	READY
802369	802369	SUV	X35 II		5	EU-BAIC-X35-II-SUV-01	HIGH	新款X35外廓，不与2016款Senova X35混用。	READY
801360	801360	SUV	X75 I		5	EU-BAIC-X75-I-SUV-01	HIGH	X75标准五门SUV外廓。	READY
801361	801361	SUV	X75 I		5	EU-BAIC-X75-I-SUV-01	HIGH	LPG动力未改变X75外廓。	READY
6005	6005	Van	B 1000		4	EU-BARKAS-B1000-VAN-01	HIGH	B 1000封闭式厢式车外廓。	READY
6006	6006	MPV	B 1000		4	EU-BARKAS-B1000-MINIBUS-01	HIGH	B 1000 Kleinbus客车外廓。	READY
6007	6007	MPV	B 1000		4	EU-BARKAS-B1000-MINIBUS-01	HIGH	生产时期差异未改变Kleinbus外廓。	READY
148181	148181	SUV	BJ212 Classic		4	EU-BAW-BJ212-CLASSIC-SUV-01	HIGH	经典BJ212封闭式四门外廓。	READY
148079	148079	Hatchback	Pony I		3	EU-BAW-PONY-I-HATCHBACK-01	HIGH	三门微型纯电车外廓。	READY
157725	157725	SUV	X7 I		5	EU-BEIJING-X7-I-SUV-01	HIGH	第一代Beijing X7五门SUV外廓。	READY
13876	13876	Sedan	Arnage I		4	EU-BENTLEY-ARNAGE-I-SEDAN-01	HIGH	早期Arnage四门外廓。	READY
16607	16607	Sedan	Arnage I T		4	EU-BENTLEY-ARNAGE-I-T-SEDAN-01	HIGH	Arnage T专属四门外廓。	READY
34869	34869	Convertible	Azure II		2	EU-BENTLEY-AZURE-II-CONVERTIBLE-01	HIGH	第二代Azure两门敞篷外廓。	READY
16850	16850	Convertible	Azure I		2	EU-BENTLEY-AZURE-I-CONVERTIBLE-01	HIGH	第一代Azure两门敞篷外廓。	READY
16852	16852	Convertible	Azure I		2	EU-BENTLEY-AZURE-I-CONVERTIBLE-01	HIGH	后期第一代Azure沿用同一外廓。	READY
16851	16851	Convertible	Azure I Mulliner		2	EU-BENTLEY-AZURE-I-CONVERTIBLE-01	HIGH	Mulliner配置未改变第一代Azure外廓。	READY
117494	117494	SUV	Bentayga I pre-facelift		5	EU-BENTLEY-BENTAYGA-I-SUV-PREFL-01	HIGH	首发W12标准轴距外廓。	READY
151616	151616	SUV	Bentayga I facelift		5	EU-BENTLEY-BENTAYGA-I-SUV-FACELIFT-HYBRID-01	HIGH	改款后Hybrid标准轴距外廓。	READY
124751	124751	SUV	Bentayga I pre-facelift		5	EU-BENTLEY-BENTAYGA-I-SUV-PREFL-01	HIGH	Diesel动力未改变改款前标准外廓。	READY
802250	802250	SUV	Bentayga I facelift		5	EU-BENTLEY-BENTAYGA-I-SUV-SPEED-MY26-01	HIGH	MY26 Speed外部套件形成独立外廓。	READY
34870	34870	Coupe	Brooklands II		2	EU-BENTLEY-BROOKLANDS-II-COUPE-01	HIGH	第二代Brooklands双门Coupe外廓。	READY
100706	100706	Sedan	Brooklands I R		4	EU-BENTLEY-BROOKLANDS-I-R-SEDAN-01	HIGH	Brooklands R四门轿车外廓。	READY
122119	122119	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH	第二代Continental GT Coupe标准外廓。	READY
18595_prefl	18595	Sedan	Continental Flying Spur I		4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-PREFL-01	MEDIUM	Ktype跨越外观改款，改款前四门分支。	READY
18595_facelift	18595	Sedan	Continental Flying Spur I facelift		4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越外观改款，改款后四门分支。	READY
57514	57514	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH	第二代Continental GT W12标准外廓。	READY
122120	122120	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH	第二代Continental GTC标准外廓。	READY
108356	108356	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH	Flex燃料未改变第二代Coupe外廓。	READY
119109	119109	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH	Flex燃料未改变第二代Coupe外廓。	READY
11928	11928	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH	第二代Continental GTC W12标准外廓。	READY
11945	11945	Convertible	Continental Supersports ISR		2	EU-BENTLEY-CONTINENTAL-GTC-I-SUPERSPORTS-ISR-01	HIGH	Supersports Convertible ISR专属低车身外廓。	READY
54822	54822	Coupe	Continental GT I		2	EU-BENTLEY-CONTINENTAL-GT-I-COUPE-01	HIGH	第一代Continental GT标准Coupe外廓。	READY
115816	115816	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH	Flex燃料未改变第二代Coupe外廓。	READY
119715	119715	Sedan	Continental Flying Spur I facelift		4	EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-FACELIFT-01	HIGH	改款后Flying Spur标准四门外廓。	READY
802167	802167	Coupe	Continental GT I		2	EU-BENTLEY-CONTINENTAL-GT-I-COUPE-01	HIGH	第一代Continental GT标准Coupe外廓。	READY
34872_gen1	34872	Convertible	Continental GTC I		2	EU-BENTLEY-CONTINENTAL-GTC-I-CONVERTIBLE-01	MEDIUM	Ktype跨越换代，第一代GTC物理分支。	READY
34872_gen2	34872	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	MEDIUM	Ktype跨越换代，第二代GTC物理分支。	READY
58428	58428	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH	第二代GTC标准外廓。	READY
115817	115817	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH	Flex燃料未改变第二代GTC外廓。	READY
17827	17827	Coupe	Continental GT I		2	EU-BENTLEY-CONTINENTAL-GT-I-COUPE-01	HIGH	第一代Continental GT标准Coupe外廓。	READY
58832	58832	Convertible	Continental GTC II Speed		2	EU-BENTLEY-CONTINENTAL-GTC-II-SPEED-CONVERTIBLE-01	HIGH	第二代GTC Speed专属低车身外廓。	READY
106277	106277	Convertible	Continental GTC II Speed		2	EU-BENTLEY-CONTINENTAL-GTC-II-SPEED-CONVERTIBLE-01	HIGH	第二代GTC Speed专属低车身外廓。	READY
800223	800223	Convertible	Continental GTC I Speed		2	EU-BENTLEY-CONTINENTAL-GTC-I-SPEED-CONVERTIBLE-01	HIGH	第一代GTC Speed专属低车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1501-1600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-TT-III-8S-COUPE-01	4177	1832	1353	Automobile-Catalog 2015 Audi TT Coupe 2.0 TFSI	https://www.automobile-catalog.com/car/2015/2084600/audi_tt_coupe_2_0_tfsi_230_s-tronic.html
EU-AUDI-TT-III-8S-ROADSTER-01	4177	1832	1355	Automobile-Catalog 2015 Audi TT Roadster 1.8 TFSI	https://www.automobile-catalog.com/car/2015/2162690/audi_tt_roadster_1_8_tfsi_180_s-tronic.html
EU-AUDI-TT-III-8S-TTS-COUPE-01	4191	1832	1343	Auto-Data Audi TT model specifications	https://www.auto-data.net/en/audi-tt-model-519
EU-AUDI-TT-III-8S-TTS-ROADSTER-01	4191	1832	1345	Auto-Data Audi TT model specifications	https://www.auto-data.net/en/audi-tt-model-519
EU-AUDI-TT-II-8J-RS-COUPE-01	4198	1842	1342	Automobile-Catalog 2014 Audi TT RS Coupe	https://www.automobile-catalog.com/car/2014/1438205/audi_tt_rs_coupe.html
EU-AUDI-TT-II-8J-RS-ROADSTER-01	4189	1842	1348	Automobile-Catalog 2014 Audi TT RS Roadster	https://www.automobile-catalog.com/car/2014/1438220/audi_tt_rs_roadster.html
EU-AUDI-TT-III-8S-RS-COUPE-01	4191	1832	1344	Audi UK TT RS official pricelist	https://press.audi.co.uk/assets/documents/original/23309-AudiUK00019252AudiTTRSCoup%C3%A9andRoadster.pdf
EU-AUDI-TT-III-8S-RS-ROADSTER-01	4191	1832	1346	Audi UK TT RS Roadster technical data	https://press.audi.co.uk/assets/documents/original/23564-AudiUK00001393AudiTTRSRoadsterStronic.pdf
EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	4041	1764	1345	Automobile-Catalog 2004 Audi TT Coupe 3.2 Quattro	https://www.automobile-catalog.com/car/2004/253325/audi_tt_coupe_3_2_quattro_dsg.html
EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	4041	1764	1348	Automobile-Catalog 2004 Audi TT Roadster 3.2 Quattro	https://www.automobile-catalog.com/car/2004/253850/audi_tt_roadster_3_2_quattro_dsg.html
EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-SERIES-3-01	3908	1613	1393	Automobile-Catalog 1980 Austin Allegro 1.3 L	https://www.automobile-catalog.com/car/1980/256595/austin_allegro_1_3_l.html
EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	3855	1613	1397	Carfolio Austin Allegro 1300	https://www.carfolio.com/austin-allegro-1300-53097
EU-AUSTIN-ALLEGRO-I-ADO67-WAGON-SERIES-3-01	3995	1630	1440	Automobile-Catalog 1980 Austin Allegro Estate 1.5 HL	https://www.automobile-catalog.com/car/1980/256745/austin_allegro_estate_1_5_hl.html
EU-AUSTIN-AMBASSADOR-I-HATCHBACK-01	4555	1730	1400	Automobile-Catalog 1982 Austin Ambassador 2.0 HLS	https://www.automobile-catalog.com/car/1982/257450/austin_ambassador_2_0_hls_automatic.html
EU-AUSTIN-APACHE-I-SEDAN-01	4060	1530	1340	Carfolio 1977 Leyland Austin Apache TC	https://www.carfolio.com/leyland-austin-apache-tc-114378
EU-AUSTIN-MAXI-II-HATCHBACK-01	4022	1629	1404	Automobile-Catalog 1981 Austin Maxi 2 1750 HLS	https://www.automobile-catalog.com/car/1981/256550/austin_maxi_2_1750_hls.html
EU-AUSTIN-METRO-I-HATCHBACK-3D-01	3405	1549	1369	Automobile-Catalog 1981 Austin Metro 1.3 S	https://www.automobile-catalog.com/car/1981/257015/austin_metro_1_3_s.html
EU-AUSTIN-MINI-ADO20-SEDAN-2D-01	3054	1410	1346	Automobile-Catalog 1969 Austin Mini 850 Mk II	https://www.automobile-catalog.com/car/1969/256370/austin_mini_850_mk_ii.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-LOW-01	4468	1710	1418	Automobile-Catalog 1984 Austin Montego 1.3	https://www.automobile-catalog.com/car/1984/62645/austin_montego_1_3.html
EU-AUSTIN-MONTEGO-I-LM11-WAGON-PREFL-01	4468	1710	1447	Automobile-Catalog 1984 Austin Montego Estate 1.6	https://www.automobile-catalog.com/car/1984/30680/austin_montego_estate_1_6_5-speed.html
EU-AUSTIN-MONTEGO-I-LM11-WAGON-FACELIFT-01	4465	1710	1447	Automobile-Catalog 1989 Montego Estate 2.0 GSi	https://www.automobile-catalog.com/car/1989/1701080/montego_estate_2_0_gsi.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-PREFL-01	4468	1710	1420	Automobile-Catalog 1984 Austin Montego 2.0 HLS	https://www.automobile-catalog.com/car/1984/258125/austin_montego_2_0_hls.html
EU-AUSTIN-MONTEGO-I-LM11-SEDAN-FACELIFT-01	4465	1710	1420	Automobile-Catalog 1989 Montego 2.0 SL	https://www.automobile-catalog.com/car/1989/1700765/montego_2_0_sl.html
EU-AUSTIN-PRINCESS-I-SEDAN-01	4455	1730	1409	Automobile-Catalog 1980 Princess 2200 HLS	https://www.automobile-catalog.com/car/1980/168575/princess_2200_hls_automatic.html
EU-AUSTIN-HEALEY-100-SIX-CONVERTIBLE-01	4001	1537	1244	Automobile-Catalog 1957 Austin-Healey 100 Six	https://www.automobile-catalog.com/car/1957/258620/austin-healey_100_six.html
EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	4001	1524	1250	Automobile-Catalog 1959 Austin-Healey 3000 2+2	https://www.automobile-catalog.com/car/1959/258740/austin-healey_3000_22.html
EU-AUSTIN-HEALEY-3000-MK-III-CONVERTIBLE-01	4001	1540	1240	Automobile-Catalog 1965 Austin-Healey 3000 Mk III	https://www.automobile-catalog.com/car/1965/258860/austin-healey_3000_mk_iii.html
EU-AUSTIN-HEALEY-SPRITE-MK-III-CONVERTIBLE-01	3496	1346	1264	Automobile-Catalog 1965 Austin-Healey Sprite Mk III	https://www.automobile-catalog.com/car/1965/75695/austin-healey_sprite_mk_iii.html
EU-AUSTIN-HEALEY-SPRITE-MK-IV-CONVERTIBLE-01	3496	1394	1200	Automobile-Catalog 1969 Austin-Healey Sprite Mk IV	https://www.automobile-catalog.com/car/1969/1698665/austin-healey_sprite_mk_iv.html
EU-AUTOBIANCHI-PRIMULA-I-COUPE-01	3785	1580	1350	Automobile-Catalog 1968 Autobianchi Primula Coupe	https://www.automobile-catalog.com/car/1968/259160/autobianchi_primula_coupe.html
EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-FWD-01	3392	1507	1440	Automobile-Catalog 1990 Lancia Y10 Fire 1.1 i.e. LX	https://www.automobile-catalog.com/car/1990/1381220/lancia_y10_fire_1_1_i_e__lx_cat.html
EU-AUTOBIANCHI-Y10-II-156-HATCHBACK-4WD-01	3392	1537	1460	Automobile-Catalog 1990 Lancia Y10 4WD i.e.	https://www.automobile-catalog.com/car/1990/1381160/lancia_y10_4wd_i_e_.html
EU-BAC-MONO-I-ROADSTER-01	3952	1836	1110	Encycarpedia BAC Mono 2.5	https://www.encycarpedia.com/bac/16-mono-2-5-roadster
EU-BAC-MONO-R-I-ROADSTER-01	3977	1836	1090	Carfolio BAC Mono R	https://www.carfolio.com/bac-mono-r-618563
EU-BAIC-X55-II-SUV-01	4620	1886	1680	BAIC Switzerland X55 II specifications	https://www.baic-schweiz.ch/x55
EU-BAIC-BJ30-II-SUV-01	4730	1910	1790	BAIC Qatar BJ30 specifications	https://www.baic.qa/models/BJ30
EU-BAIC-BJ60-I-SUV-01	5040	1955	1925	BAIC Group B60 official specifications	https://www.baicglobal.com/models/31
EU-BAIC-SENOVA-X25-I-SUV-01	4110	1750	1545	BAIC X25 official brochure	https://cache1.pakwheels.com/system/brochures/605/original/X25_Brochure.pdf
EU-BAIC-SENOVA-X35-I-SUV-01	4300	1815	1640	17VIN 2016 BAIC Senova X35 specification	https://en.17vin.com/model/jg6ol.html
EU-BAIC-SENOVA-X65-I-SUV-01	4654	1816	1680	Zigwheels BAIC X65 2.0T specification	https://www.zigwheels.vn/en/new-cars/baic/x65/2-0t-at-premium
EU-BAIC-X35-II-SUV-01	4325	1830	1640	BAIC Group X35 official specification PDF	https://www.baicglobal.com/file/upload/2022/08/12/X35%20Specifications_20220812131259A118.pdf
EU-BAIC-X75-I-SUV-01	4745	1892	1715	BAIC Switzerland X75 specifications	https://www.baic-schweiz.ch/x75
EU-BARKAS-B1000-VAN-01	4520	1860	1850	Barkas B 1000 technical overview	https://de.wikipedia.org/wiki/Barkas_B_1000
EU-BARKAS-B1000-MINIBUS-01	4520	1860	1910	WheelsAge Barkas B1000 KB Kleinbus specifications	https://en.wheelsage.org/barkas/b1000/kb_kleinbus/specifications
EU-BAW-BJ212-CLASSIC-SUV-01	4080	1840	1870	CarNewsChina BAW BJ212 2.0 specification	https://carnewschina.com/2017/05/10/good-old-beijing-auto-works-bj212-alive-kicking/
EU-BAW-PONY-I-HATCHBACK-01	3162	1498	1585	BAW International Pony official specifications	https://bawauto.com/pony/
EU-BEIJING-X7-I-SUV-01	4710	1892	1715	China Daily Beijing X7 launch specifications	https://epaper.chinadaily.com.cn/a/202006/29/WS5ef92c0ea3107831ec75310f.html
EU-BENTLEY-ARNAGE-I-SEDAN-01	5390	1932	1515	Automobile-Catalog 2000 Bentley Arnage Green Label	https://www.automobile-catalog.com/car/2000/261035/bentley_arnage_green_label.html
EU-BENTLEY-ARNAGE-I-T-SEDAN-01	5400	1932	1515	Automobile-Catalog 2003 Bentley Arnage T	https://www.automobile-catalog.com/car/2003/261095/bentley_arnage_t.html
EU-BENTLEY-AZURE-II-CONVERTIBLE-01	5410	1900	1492	Automobile-Catalog 2006 Bentley Azure	https://www.automobile-catalog.com/car/2006/261245/bentley_azure.html
EU-BENTLEY-AZURE-I-CONVERTIBLE-01	5342	1878	1475	Automobile-Catalog 1999 Bentley Azure	https://www.automobile-catalog.com/car/1999/260960/bentley_azure.html
EU-BENTLEY-BENTAYGA-I-SUV-PREFL-01	5140	1998	1742	Automobile-Catalog 2016 Bentley Bentayga	https://www.automobile-catalog.com/car/2016/2210120/bentley_bentayga.html
EU-BENTLEY-BENTAYGA-I-SUV-FACELIFT-HYBRID-01	5125	2010	1710	Edmunds 2023 Bentley Bentayga Hybrid specifications	https://www.edmunds.com/bentley/bentayga/2023/st-401934848/features-specs/
EU-BENTLEY-BENTAYGA-I-SUV-SPEED-MY26-01	5144	2010	1728	CarExpert 2026 Bentley Bentayga Speed specifications	https://www.carexpert.com.au/bentley/bentayga/2026-speed-4l-suv-4x4-petrol-automatic-jsgwsgwg20250909
EU-BENTLEY-BROOKLANDS-II-COUPE-01	5411	1900	1473	Automobile-Catalog 2010 Bentley Brooklands	https://www.automobile-catalog.com/car/2010/1373480/bentley_brooklands.html
EU-BENTLEY-BROOKLANDS-I-R-SEDAN-01	5295	1914	1486	Automobile-Catalog 1997 Bentley Brooklands R	https://www.automobile-catalog.com/car/1997/260795/bentley_brooklands_r.html
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1944	1404	Automobile-Catalog 2012 Bentley Continental GT W12	https://www.automobile-catalog.com/car/2012/1767680/bentley_continental_gt_w12.html
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-PREFL-01	5307	1916	1479	Automobile-Catalog 2005 Bentley Continental Flying Spur	https://www.automobile-catalog.com/car/2005/261320/bentley_continental_flying_spur.html
EU-BENTLEY-CONTINENTAL-FLYING-SPUR-I-SEDAN-FACELIFT-01	5290	1916	1475	Automobile-Catalog 2010 Bentley Continental Flying Spur	https://www.automobile-catalog.com/car/2010/1193525/bentley_continental_flying_spur.html
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1944	1403	Automobile-Catalog 2012 Bentley Continental GTC W12	https://www.automobile-catalog.com/car/2012/1614950/bentley_continental_gtc_6_0_litre_w12.html
EU-BENTLEY-CONTINENTAL-GTC-I-SUPERSPORTS-ISR-01	4804	1916	1388	Automobile-Catalog 2011 Bentley Continental Supersports Convertible	https://www.automobile-catalog.com/car/2011/1373075/bentley_continental_supersports_convertible.html
EU-BENTLEY-CONTINENTAL-GT-I-COUPE-01	4804	1916	1390	Automobile-Catalog 2008 Bentley Continental GT	https://www.automobile-catalog.com/car/2008/1193420/bentley_continental_gt.html
EU-BENTLEY-CONTINENTAL-GTC-I-CONVERTIBLE-01	4804	1916	1398	Automobile-Catalog 2008 Bentley Continental GTC	https://www.automobile-catalog.com/car/2008/1193435/bentley_continental_gtc.html
EU-BENTLEY-CONTINENTAL-GTC-II-SPEED-CONVERTIBLE-01	4806	1943	1393	Carsales 2013 Bentley Continental GTC Speed specifications	https://www.carsales.com.au/research/bentley/continental/2013/gtc-speed/
EU-BENTLEY-CONTINENTAL-GTC-I-SPEED-CONVERTIBLE-01	4804	1916	1388	Automobile-Catalog 2010 Bentley Continental GTC Speed	https://www.automobile-catalog.com/car/2010/1193450/bentley_continental_gtc_speed.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1501-1600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2015/2084600/audi_tt_coupe_2_0_tfsi_230_s-tronic.html?utm_source=chatgpt.com "2015 Audi TT Coupe 2.0 TFSI (230) S-Tronic (d-cl. 6)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1857 行）
- 累计尺寸组：dimension_groups_final.tsv（589 行）

