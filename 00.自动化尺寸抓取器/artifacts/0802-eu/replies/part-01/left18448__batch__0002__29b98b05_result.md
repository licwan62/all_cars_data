# 任务：left18448 第 101-200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0002__29b98b05


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 101-200 行

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
left18448 第 101-200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_101-200_ktype_dimension_mapping_final.tsv
- left18448_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	4435	1743	1390
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390
EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	4430	1745	1415
EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	4430	1745	1420
EU-ALFA-ROMEO-156-932-Q4-WAGON-01	4441	1743	1458

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Alfa Romeo	156	2.4 JTD	Kombi	Frontantrieb	Diesel	Oct 2003	May 2006	17623
Alfa Romeo	156	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2002	8811
Alfa Romeo	156	2.5 V6 24V	Kombi	Frontantrieb	Benzin	Feb 1997	Aug 2003	14787
Alfa Romeo	156	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Sep 2005	15686
Alfa Romeo	156	2.5 V6 24V	Kombi	Frontantrieb	Benzin	Feb 1997	May 2006	15691
Alfa Romeo	156	3.2 GTA	Stufenheck	Frontantrieb	Benzin	Mar 2002	Sep 2005	16610
Alfa Romeo	156	3.2 GTA	Kombi	Frontantrieb	Benzin	Mar 2002	May 2006	16611
Alfa Romeo	159	1.9 Jtdm 16V	Stufenheck	Frontantrieb	Diesel	Sep 2005	Nov 2011	18930
Alfa Romeo	159	1.9 Jtdm 8V	Stufenheck	Frontantrieb	Diesel	Sep 2005	Nov 2011	18929
Alfa Romeo	159	1.9 JTS	Stufenheck	Frontantrieb	Benzin	Sep 2005	Nov 2011	18926
Alfa Romeo	159	2.2 JTS	Stufenheck	Frontantrieb	Benzin	Sep 2005	Nov 2011	18927
Alfa Romeo	159	2.4 Jtdm	Stufenheck	Frontantrieb	Diesel	Sep 2005	Nov 2011	18931
Alfa Romeo	159	3.2 JTS Q4	Stufenheck	Allrad	Benzin	Dec 2005	Nov 2011	18928
Alfa Romeo	166	2.0 T.spark	Stufenheck	Frontantrieb	Benzin	Sep 1998	Oct 2000	10006
Alfa Romeo	166	2.0 T.spark	Stufenheck	Frontantrieb	Benzin	Oct 2000	Jun 2007	15620
Alfa Romeo	166	2.0 V6	Stufenheck	Frontantrieb	Benzin	Sep 1998	Oct 2000	11366
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Sep 1998	Oct 2000	10009
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2000	Jun 2007	15695
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Apr 2002	Jun 2007	16808
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2003	Jun 2007	17704
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	Oct 2003	Jun 2007	58712
Alfa Romeo	166	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Sep 1998	Dec 2006	10007
Alfa Romeo	166	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Jun 2007	15694
Alfa Romeo	166	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Sep 1998	Jun 2007	10008
Alfa Romeo	166	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Jun 2007	15621
Alfa Romeo	166	3.2 V6 24V	Stufenheck	Frontantrieb	Benzin	Oct 2003	Jun 2007	17694
Alfa Romeo	4c	1.8	Coupe	Heckantrieb	Benzin	Mar 2013	Dec 2020	59048
Alfa Romeo	4c	1.8	Cabriolet	Heckantrieb	Benzin	Oct 2014	Dec 2020	108275
Alfa Romeo	Alfasud	1.3	Coupe	Frontantrieb	Benzin	May 1978	Dec 1979	127188
Alfa Romeo	Alfasud	1.5	Coupe	Frontantrieb	Benzin	Jan 1980	Dec 1989	14142
Alfa Romeo	Arna	1.2	Schrägheck	Frontantrieb	Benzin	Mar 1983	Dec 1986	14705
Alfa Romeo	Berlina	2000	Stufenheck	Heckantrieb	Benzin	Oct 1971	Mar 1977	35058
Alfa Romeo	Giulia	1.6	Cabriolet	Heckantrieb	Benzin	Mar 1962	Feb 1969	50865
Alfa Romeo	Giulia	1.6	Cabriolet	Heckantrieb	Benzin	Mar 1962	Dec 1966	50867
Alfa Romeo	Giulia	2	Stufenheck	Heckantrieb	Benzin	Aug 2016	-	121146
Alfa Romeo	Giulia	2	Stufenheck	Heckantrieb	Benzin	Aug 2016	Oct 2022	121698
Alfa Romeo	Giulia	1300	Stufenheck	Heckantrieb	Benzin	Jan 1964	Aug 1969	50862
Alfa Romeo	Giulia	1.6 T.I	Stufenheck	Heckantrieb	Benzin	Jan 1962	Dec 1978	50864
Alfa Romeo	Giulia	1.6 T.i. Super	Stufenheck	Heckantrieb	Benzin	Jan 1963	Dec 1978	50863
Alfa Romeo	Giulia	1.8 D	Stufenheck	Heckantrieb	Diesel	Jun 1976	Dec 1978	14742
Alfa Romeo	Giulia	1600 Sprint	Coupe	Heckantrieb	Benzin	Jan 1962	Dec 1964	50860
Alfa Romeo	Giulia	1600 Sprint	Coupe	Heckantrieb	Benzin	Jan 1963	Dec 1965	50861
Alfa Romeo	Giulia	2.0 Q4	Stufenheck	Allrad	Benzin	Aug 2016	-	123388
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	Oct 2015	-	119958
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	Oct 2015	-	119959
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	Oct 2015	-	120213
Alfa Romeo	Giulia	2.2 D Q4	Stufenheck	Allrad	Diesel	Nov 2016	-	123923
Alfa Romeo	Giulia	2.2 D Q4	Stufenheck	Allrad	Diesel	Apr 2017	-	126711
Alfa Romeo	Giulia	2.9 Quadrifoglio	Stufenheck	Heckantrieb	Benzin	Oct 2015	-	119608
Alfa Romeo	Giulietta	1.8	Stufenheck	Heckantrieb	Benzin	Jun 1983	Jul 1985	59788
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	Apr 2011	Feb 2017	12017
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	Sep 2014	Oct 2018	108276
Alfa Romeo	Giulietta	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	Feb 2015	Dec 2020	112138
Alfa Romeo	Giulietta	1.6 Jtdm	Schrägheck	Frontantrieb	Diesel	Sep 2015	Oct 2018	117422
Alfa Romeo	Giulietta	1.8 TBI	Schrägheck	Frontantrieb	Benzin	Apr 2010	Sep 2013	110004
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	Apr 2010	Feb 2016	11001
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	Nov 2013	Oct 2018	100763
Alfa Romeo	Gt	1.8 TS	Coupe	Frontantrieb	Benzin	Nov 2003	Sep 2010	17789
Alfa Romeo	Gt	1.9 JTD	Coupe	Frontantrieb	Diesel	Nov 2003	Sep 2010	17792
Alfa Romeo	Gt	2.0 JTS	Coupe	Frontantrieb	Benzin	Dec 2006	Sep 2010	10997
Alfa Romeo	Gt	2.0 JTS	Coupe	Frontantrieb	Benzin	Nov 2003	Sep 2010	17790
Alfa Romeo	Gt	3.2 GTA	Coupe	Frontantrieb	Benzin	Nov 2003	Sep 2010	17791
Alfa Romeo	Gta	1.3 Junior	Coupe	Heckantrieb	Benzin	May 1968	Dec 1976	14739
Alfa Romeo	Gta	1.3 Junior	Coupe	Heckantrieb	Benzin	May 1968	Dec 1976	14740
Alfa Romeo	Gtv	2.0 JTS	Coupe	Frontantrieb	Benzin	Apr 2003	Oct 2005	17286
Alfa Romeo	Gtv	2.0 Turbodelta	Coupe	Heckantrieb	Benzin	Jan 1978	Dec 1980	14743
Alfa Romeo	Gtv	3.0 V6 24V	Coupe	Frontantrieb	Benzin	Oct 2000	Oct 2005	15622
Alfa Romeo	Gtv	3.2 V6 24V	Coupe	Frontantrieb	Benzin	Apr 2003	Oct 2005	17287
Alfa Romeo	Junior	Electric	SUV	Frontantrieb	Elektro	Apr 2024	-	158420
Alfa Romeo	Junior	Electric 240	SUV	Frontantrieb	Elektro	Apr 2024	-	158421
Alfa Romeo	Junior	Electric 280	SUV	Frontantrieb	Elektro	Oct 2024	-	800229
Alfa Romeo	Junior	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Apr 2024	-	158418
Alfa Romeo	Junior	Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	Oct 2025	-	802739
Alfa Romeo	Junior	Mild Hybrid Q4	SUV	Allrad	Benzin/Elektro	Jan 2025	-	801364
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	May 2011	Oct 2018	10972
Alfa Romeo	Mito	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2011	Oct 2018	50239
Alfa Romeo	Mito	0.9 Twinair	Schrägheck	Frontantrieb	Benzin	Jul 2011	Dec 2013	13956
Alfa Romeo	Mito	0.9 Twinair	Schrägheck	Frontantrieb	Benzin	Apr 2013	Aug 2018	58986
Alfa Romeo	Mito	0.9 Twinair	Schrägheck	Frontantrieb	Benzin	Dec 2013	Aug 2018	100784
Alfa Romeo	Mito	1.3 Multijet	Schrägheck	Frontantrieb	Diesel	Dec 2013	Dec 2015	100783
Alfa Romeo	Mito	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2009	Aug 2016	13957
Alfa Romeo	Mito	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	Apr 2016	Oct 2018	120228
Alfa Romeo	Mito	1.4 Multiair	Schrägheck	Frontantrieb	Benzin	Sep 2009	Aug 2013	3317
Alfa Romeo	Mito	1.4 TB	Schrägheck	Frontantrieb	Benzin	Dec 2013	Oct 2018	100764
Alfa Romeo	Spider	2	Cabriolet	Heckantrieb	Benzin	Sep 1989	Dec 1990	127108
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	Jan 1980	Dec 1989	127184
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	Jan 1958	Dec 1961	12432
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	Jan 1971	Dec 1977	121297
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	Jan 1975	Dec 1986	127185
Alfa Romeo	Spider	2.0 JTS	Cabriolet	Frontantrieb	Benzin	Apr 2003	Apr 2005	17288
Alfa Romeo	Spider	3.0 V6	Cabriolet	Frontantrieb	Benzin	Apr 1995	Apr 1998	12902
Alfa Romeo	Spider	3.0 V6	Cabriolet	Frontantrieb	Benzin	Sep 1994	Apr 2005	15623
Alfa Romeo	Spider	3.0 V6 24V	Cabriolet	Frontantrieb	Benzin	Jan 1999	Oct 2003	14771
Alfa Romeo	Spider	3.2 V6 24V	Cabriolet	Frontantrieb	Benzin	Apr 2003	Apr 2005	17289
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	Dec 2016	-	125157
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	Dec 2016	-	126959
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	Dec 2019	-	143549
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	Dec 2016	-	126958
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	Dec 2016	-	127368
Alfa Romeo	Stelvio	2.2 D Q4	SUV	Allrad	Diesel	Dec 2016	-	126013


--- Round 1 / checkpoint 续跑 ---
## 更新点

* 本轮按物理车身聚类完成 156、159、166、4C、Giulietta 940、GT、Junior 前驱版、MiTo 与 Stelvio 的映射。
* 共首次闭合 16 个尺寸组，并复用跨批次已有的 4 个 156 改款前/后 Sedan、Wagon 尺寸组。
* 156 与 166 中生产区间跨越外观改款、且外廓发生变化的 Ktype 已拆分为 `prefl`、`facelift` 派生行。
* GT 根据厂方公布的版本车高拆为标准汽油、JTD、GTA 三个物理尺寸组；Junior 根据标准电动、Veloce 低悬架、Ibrida 三种高度拆组。主要尺寸采用 Alfa Romeo／Stellantis 官方规格；156 GTA 与 166 改款前使用明确标注不含后视镜宽度的直接规格页面补齐。([Stellantis Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：61
* READY 映射行：70
* PENDING 输入 Ktype：39
* 本轮首次创建尺寸组：16
* 本轮复用已有尺寸组：4
* 当前映射已引用且闭合的尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17623	17623	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	2003年外观改款后 Sportwagon。	READY
8811	8811	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH		READY
14787	14787	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH		READY
15686_prefl	15686	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15686_facelift	15686	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15691_prefl	15691	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15691_facelift	15691	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
16610	16610	Sedan	156 GTA (932)	932	4	EU-ALFA-ROMEO-156-GTA-932-SEDAN-01	HIGH	GTA宽体及低悬架外廓。	READY
16611	16611	Wagon	156 GTA (932)	932	5	EU-ALFA-ROMEO-156-GTA-932-WAGON-01	HIGH	GTA宽体及低悬架外廓。	READY
18930	18930	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18929	18929	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18926	18926	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18927	18927	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18931	18931	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18928	18928	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
10006	10006	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
15620_prefl	15620	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15620_facelift	15620	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
11366	11366	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
10009	10009	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
15695_prefl	15695	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15695_facelift	15695	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
16808_prefl	16808	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
16808_facelift	16808	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
17704	17704	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
58712	58712	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
10007_prefl	10007	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
10007_facelift	10007	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15694_prefl	15694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15694_facelift	15694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
10008_prefl	10008	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
10008_facelift	10008	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15621_prefl	15621	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15621_facelift	15621	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
17694	17694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
59048	59048	Coupe	4C (960)	960	2	EU-ALFA-ROMEO-4C-960-COUPE-01	HIGH		READY
108275	108275	Convertible	4C (960)	960	2	EU-ALFA-ROMEO-4C-960-CONVERTIBLE-01	HIGH		READY
12017	12017	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
108276	108276	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
112138	112138	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
117422	117422	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
110004	110004	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
11001	11001	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
100763	100763	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
17789	17789	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17792	17792	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-JTD-01	HIGH	厂方JTD车高分支。	READY
10997	10997	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17790	17790	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17791	17791	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-GTA-01	HIGH	3.2 GTA低车高分支。	READY
158420	158420	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-ELETTRICA-01	HIGH		READY
158421	158421	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	HIGH	Veloce低悬架外廓。	READY
800229	800229	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	HIGH	Veloce低悬架外廓。	READY
158418	158418	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	HIGH	前驱Ibrida标准悬架外廓。	READY
802739	802739	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	HIGH	前驱Ibrida标准悬架外廓。	READY
10972	10972	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
50239	50239	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
13956	13956	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
58986	58986	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100784	100784	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100783	100783	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
13957	13957	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
120228	120228	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
3317	3317	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100764	100764	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
125157	125157	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126959	126959	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
143549	143549	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126958	126958	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127368	127368	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126013	126013	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

跨批次已有的 4 个 156 普通车身尺寸组仅复用，未在本节重复输出。

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-156-GTA-932-SEDAN-01	4430	1765	1402	Automobile-Catalog Alfa Romeo 156 GTA	https://www.automobile-catalog.com/car/2002/219980/alfa_romeo_156_gta.html
EU-ALFA-ROMEO-156-GTA-932-WAGON-01	4430	1765	1411	Automobile-Catalog Alfa Romeo 156 Sportwagon GTA	https://www.automobile-catalog.com/car/2002/219965/alfa_romeo_156_sportwagon_gta.html
EU-ALFA-ROMEO-159-939-SEDAN-01	4660	1828	1417	Stellantis Media Alfa 159	https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-159-4
EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	4720	1815	1416	Automobile-Catalog Alfa Romeo 166 2.4 JTD	https://www.automobile-catalog.com/car/1999/220730/alfa_romeo_166_2_4_jtd.html
EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	4720	1800	1416	Stellantis Media Revised Alfa 166	https://www.media.stellantis.com/uk-en/alfa-romeo/press/revised-alfa-166-in-the-uk
EU-ALFA-ROMEO-4C-960-COUPE-01	3989	1864	1183	Stellantis Media Alfa Romeo 4C technical specification	https://www.media.stellantis.com/uploads/uk/UK/2013/ALFA_ROMEO/PRESS/71157alf%20-TECH_SPEC.doc
EU-ALFA-ROMEO-4C-960-CONVERTIBLE-01	3989	1864	1183	Auto-Data Alfa Romeo 4C Spider	https://www.auto-data.net/en/alfa-romeo-4c-spider-1.7-240hp-tct-22095
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	4351	1798	1465	Stellantis Media Alfa Romeo Giulietta technical specification	https://www.media.stellantis.com/uploads/pl/PL/2011/ALFA_ROMEO/SPECIFICATIONS/100413_AR_Giulietta_wyposazenie_TS.pdf
EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	4489	1763	1362	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-GT-937-COUPE-JTD-01	4489	1763	1366	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-GT-937-COUPE-GTA-01	4489	1763	1355	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	4173	1781	1539	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-JUNIOR-I-SUV-ELETTRICA-01	4173	1781	1532	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	4173	1781	1505	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	4063	1720	1446	Stellantis Media New Alfa MiTo MultiAir in UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-mito-multiair-in-uk
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Stellantis Media Alfa Romeo Stelvio First Edition	https://www.media.stellantis.com/nl-nl/alfa-romeo/press/de-alfa-romeo-stelvio-first-edition-is-nu-bestelbaar
```

## 下一步优先处理

1. 优先闭合现代 Giulia 952 的标准车身、Q4 与 Quadrifoglio 外廓边界。
2. 聚类核对经典 Giulia Sedan、Sprint Coupe、Convertible，避免把同名但不同车系的物理车身混组。
3. 处理 Spider／GTV 的经典 105/115、116 与 916 系列及可能的改款分支。
4. 随后处理 Alfasud、Arna、Berlina、旧 Giulietta、GTA Junior，以及尚未闭合的 Junior Q4。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-159-4?utm_source=chatgpt.com "Alfa 159 | Alfa Romeo"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_101-200_ktype_dimension_mapping_final.tsv
- left18448_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 已闭合现代 Giulia 952 的标准后驱、Q4 和 Quadrifoglio 三种外廓。官方规格明确给出普通后驱车高 1436 mm、Q4 车高 1450 mm，普通车身宽度为不含后视镜的 1860 mm；欧洲 Quadrifoglio 使用独立的 4639 × 1873 × 1426 mm 外廓。
* 已闭合 GTV／Spider 916 的 2003 Phase 3 前后外廓：GTV 从 4285 × 1780 × 1318 mm 变为 4299 × 1776 × 1318 mm；Spider 从 4285 × 1780 × 1315 mm 变为 4299 × 1776 × 1315 mm。([汽车目录][1])
* Junior Ibrida Q4 暂不建组：德国官方页面给出车高 1538 mm，法国及卢森堡官方页面给出 1544 mm，冲突尚未闭合。([alfaromeo.de][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：78
* PENDING 输入 Ktype：22
* READY 映射行：87
* 当前已闭合尺寸组：27
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121146	121146	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
121698	121698	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
123388	123388	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
119958	119958	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
119959	119959	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
120213	120213	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
123923	123923	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
126711	126711	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
119608	119608	Sedan	Giulia Quadrifoglio (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-QUADRIFOGLIO-SEDAN-01	HIGH	Quadrifoglio宽体、保险杠及低车高外廓。	READY
17286	17286	Coupe	GTV (916 Phase 3)	916	2	EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	HIGH	2003 Phase 3前部外廓。	READY
15622	15622	Coupe	GTV (916 Phase 2)	916	2	EU-ALFA-ROMEO-GTV-916-PREFL-COUPE-01	MEDIUM	3.0 V6 24V对应Phase 3之前外廓，未创建2003改款分支。	READY
17287	17287	Coupe	GTV (916 Phase 3)	916	2	EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	HIGH	2003 Phase 3前部外廓。	READY
801364	801364	SUV	Junior I		5		LOW	Junior Ibrida Q4官方欧洲页面车高存在1538与1544 mm冲突。	PENDING: 官方车高冲突未闭合
17288	17288	Convertible	Spider (916 Phase 3)	916	2	EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	HIGH	2003 Phase 3前部外廓。	READY
12902	12902	Convertible	Spider (916 Phase 1)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	HIGH		READY
15623	15623	Convertible	Spider (916 Phase 1/2)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	MEDIUM	3.0 V6对应Phase 3之前外廓，未创建2003改款分支。	READY
14771	14771	Convertible	Spider (916 Phase 2)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	HIGH	3.0 V6 24V对应Phase 3之前外廓。	READY
17289	17289	Convertible	Spider (916 Phase 3)	916	2	EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	HIGH	2003 Phase 3前部外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436	Alfa Romeo Canada 2019 Giulia official specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2019-alfaromeo-giulia-specifications-en.pdf
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450	Alfa Romeo Canada 2019 Giulia official specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2019-alfaromeo-giulia-specifications-en.pdf
EU-ALFA-ROMEO-GIULIA-952-QUADRIFOGLIO-SEDAN-01	4639	1873	1426	Automobile-Catalog 2018 Alfa Romeo Giulia Quadrifoglio	https://www.automobile-catalog.com/car/2018/2455370/alfa_romeo_giulia_quadrifoglio.html
EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	4299	1776	1318	Automobile-Catalog 2003 Alfa Romeo GTV 2.0 JTS	https://www.automobile-catalog.com/car/2003/218660/alfa_romeo_gtv_2_0_jts_16v.html
EU-ALFA-ROMEO-GTV-916-PREFL-COUPE-01	4285	1780	1318	Automobile-Catalog 1997 Alfa Romeo GTV 3.0 V6 24V	https://www.automobile-catalog.com/car/1997/218405/alfa_romeo_gtv_3_0_v6_24v.html
EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	4299	1776	1315	Auto-Data Alfa Romeo Spider 916 facelift 3.2 V6	https://www.auto-data.net/de/alfa-romeo-spider-916-facelift-2003-3.2-v6-240hp-1450
EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	4285	1780	1315	Automobile-Catalog 1997 Alfa Romeo Spider 3.0 V6	https://www.automobile-catalog.com/car/1997/218435/alfa_romeo_spider_3_0_v6.html
```

## 下一步优先处理

1. 集中闭合经典 Giulia Sedan、Sprint Coupe 与 Giulia Spider，严格区分 101、105 系列和不同车身。
2. 处理经典 Spider 102、105/115 的各代改款外廓。
3. 聚类处理 Alfasud Sprint、Arna、Berlina、旧 Giulietta、GTA Junior 和 Alfetta GTV。
4. 最后处理 Junior Q4 官方车高冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/218405/alfa_romeo_gtv_3_0_v6_24v.html?utm_source=chatgpt.com "1997 Alfa Romeo GTV 3.0 V6 24V Specs Review (162 kW ..."
[2]: https://www.alfaromeo.de/modelle/junior-ibrida-q4?utm_source=chatgpt.com "Alfa Romeo Junior Ibrida Q4 | Sportlicher kompakter Hybrid"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_101-200_ktype_dimension_mapping_final.tsv
- left18448_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* Alfasud Sprint 的 Ktype `14142` 已按 1983 年外廓变化拆为改款前后两支：改款前为 `4019 × 1610 × 1305 mm`，改款后为 `4024 × 1620 × 1305 mm`；`127188` 仅命中改款前组。([汽车目录][1])
* 已闭合 2000 Berlina、Giulietta 116 和 GTA 1300 Junior；GTA 尺寸同时得到 Alfa Romeo 历史博物馆资料支持。([汽车目录][2])
* Junior Ibrida Q4 的冲突已按 Alfa Romeo France 官方 2025 年 4 月规格闭合为 `4173 × 1781 × 1544 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：85
* PENDING 输入 Ktype：15
* READY 映射行：95
* 已确认尺寸组：33
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127188	127188	Coupe	Alfasud Sprint (902 Series 1)	902	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	HIGH		READY
14142_prefl	14142	Coupe	Alfasud Sprint (902 Series 1)	902	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	HIGH	生产区间跨1983年外廓改款，拆分改款前分支。	READY
14142_facelift	14142	Coupe	Sprint (902 facelift)	902	3	EU-ALFA-ROMEO-SPRINT-902-FACELIFT-COUPE-01	HIGH	生产区间跨1983年外廓改款，拆分改款后分支。	READY
35058	35058	Sedan	2000 Berlina (105)	105	4	EU-ALFA-ROMEO-2000-BERLINA-105-SEDAN-01	HIGH		READY
59788	59788	Sedan	Giulietta (116)	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH		READY
14739	14739	Coupe	GTA 1300 Junior (105)	105	2	EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	HIGH		READY
14740	14740	Coupe	GTA 1300 Junior (105)	105	2	EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	HIGH		READY
801364	801364	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-Q4-01	HIGH	Q4增高外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	4019	1610	1305	Automobile-Catalog 1980 Alfa Romeo Alfasud Sprint 1.5	https://www.automobile-catalog.com/car/1980/35930/alfa_romeo_alfasud_sprint_1_5.html
EU-ALFA-ROMEO-SPRINT-902-FACELIFT-COUPE-01	4024	1620	1305	Automobile-Catalog 1983 Alfa Romeo Sprint 1.5	https://www.automobile-catalog.com/car/1983/214550/alfa_romeo_sprint_1_5.html
EU-ALFA-ROMEO-2000-BERLINA-105-SEDAN-01	4390	1565	1430	Automobile-Catalog 1972 Alfa Romeo 2000 Berlina	https://www.automobile-catalog.com/car/1972/71840/alfa_romeo_2000_berlina.html
EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	4210	1650	1400	Automobile-Catalog 1983 Alfa Romeo Giulietta 1.8 L	https://www.automobile-catalog.com/car/1983/144515/alfa_romeo_giulietta_1_8_l.html
EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	4080	1580	1315	Alfa Romeo Museum GTA 1300 Junior	https://www.museoalfaromeo.com/en-us/collezione/Pages/GTA-1300-Junior-.aspx
EU-ALFA-ROMEO-JUNIOR-I-SUV-Q4-01	4173	1781	1544	Alfa Romeo France Junior official tariff April 2025	https://www.media.stellantis.com/uploads/fr/attachment//tarifpublicalfaromeogammemy2520250401-67ff6ae22a234.pdf
```

## 下一步优先处理

1. 闭合经典 Giulia Sedan 的早期车身与 Nuova 改款分支。
2. 区分 Giulia 1600 Sprint、Giulia Spider 101 与后续 Spider 105/115。
3. 处理经典 Spider 各代尾部改款、Alfetta GTV Turbodelta。
4. 最后解决 Arna 1.2 的三门/五门边界及规格来源冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html?utm_source=chatgpt.com "1978 Alfa Romeo Alfasud Sprint 1.3 Specs Review (58 kW / 79 PS / 78 hp) (since mid-year 1978 for Europe )"
[2]: https://www.automobile-catalog.com/car/1972/71840/alfa_romeo_2000_berlina.html?utm_source=chatgpt.com "1972 Alfa Romeo 2000 Berlina Specs Review (96.5 kW / 131 PS / 129 hp) (for Europe Australia )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_101-200_ktype_dimension_mapping_final.tsv
- left18448_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
## 更新点

* 剩余 15 个 Ktype 已全部闭合，新增 12 个尺寸组。
* 已完成 Arna 1.2 L 三门车身、经典 Giulia 三阶段 Sedan、Giulia Spider/Sprint、Alfetta GTV Turbodelta，以及 Spider 102 和 115 Series 2/3/4 的物理分支拆分。([汽车目录][1])
* Spider 跨代 Ktype 已依据欧洲规格拆分为 Series 2 的 4120 mm、Series 3 的 4245 mm 和 Series 4 的 4258 mm 外廓。([汽车目录][2])
* 已完成机械检查：固定表头正确、117 个映射 id 唯一、45 个尺寸组 ID 唯一、全部引用闭合、尺寸及来源字段非空。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：117
* PENDING：0
* DIMENSION_GROUP：45
* 孤立尺寸组：0
* 未闭合引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17623	17623	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	2003年外观改款后 Sportwagon。	READY
8811	8811	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH		READY
14787	14787	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH		READY
15686_prefl	15686	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15686_facelift	15686	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15691_prefl	15691	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15691_facelift	15691	Wagon	156 (932)	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
16610	16610	Sedan	156 GTA (932)	932	4	EU-ALFA-ROMEO-156-GTA-932-SEDAN-01	HIGH	GTA宽体及低悬架外廓。	READY
16611	16611	Wagon	156 GTA (932)	932	5	EU-ALFA-ROMEO-156-GTA-932-WAGON-01	HIGH	GTA宽体及低悬架外廓。	READY
18930	18930	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18929	18929	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18926	18926	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18927	18927	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18931	18931	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
18928	18928	Sedan	159 (939)	939	4	EU-ALFA-ROMEO-159-939-SEDAN-01	HIGH		READY
10006	10006	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
15620_prefl	15620	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15620_facelift	15620	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
11366	11366	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
10009	10009	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH		READY
15695_prefl	15695	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15695_facelift	15695	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
16808_prefl	16808	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
16808_facelift	16808	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
17704	17704	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
58712	58712	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
10007_prefl	10007	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
10007_facelift	10007	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15694_prefl	15694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15694_facelift	15694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
10008_prefl	10008	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
10008_facelift	10008	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
15621_prefl	15621	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款前分支。	READY
15621_facelift	15621	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH	Ktype生产范围跨2003年外观改款，拆分改款后分支。	READY
17694	17694	Sedan	166 (936)	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
59048	59048	Coupe	4C (960)	960	2	EU-ALFA-ROMEO-4C-960-COUPE-01	HIGH		READY
108275	108275	Convertible	4C (960)	960	2	EU-ALFA-ROMEO-4C-960-CONVERTIBLE-01	HIGH		READY
127188	127188	Coupe	Alfasud Sprint (902 Series 1)	902	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	HIGH		READY
14142_prefl	14142	Coupe	Alfasud Sprint (902 Series 1)	902	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	HIGH	生产区间跨1983年外廓改款，拆分改款前分支。	READY
14142_facelift	14142	Coupe	Sprint (902 facelift)	902	3	EU-ALFA-ROMEO-SPRINT-902-FACELIFT-COUPE-01	HIGH	生产区间跨1983年外廓改款，拆分改款后分支。	READY
14705	14705	Hatchback	Arna (920)	920	3	EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	HIGH	1.2 L三门车身。	READY
35058	35058	Sedan	2000 Berlina (105)	105	4	EU-ALFA-ROMEO-2000-BERLINA-105-SEDAN-01	HIGH		READY
50865	50865	Convertible	Giulia Spider (101)	101.23	2	EU-ALFA-ROMEO-GIULIA-SPIDER-101-CONVERTIBLE-01	HIGH		READY
50867	50867	Convertible	Giulia Spider (101)	101.23	2	EU-ALFA-ROMEO-GIULIA-SPIDER-101-CONVERTIBLE-01	HIGH		READY
121146	121146	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
121698	121698	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
50862	50862	Sedan	Giulia 1300 (105)	105	4	EU-ALFA-ROMEO-GIULIA-105-1300-SEDAN-01	HIGH	1300基础版短前后外廓。	READY
50864_early	50864	Sedan	Giulia 1600 TI (105 early)	105	4	EU-ALFA-ROMEO-GIULIA-105-EARLY-SEDAN-01	HIGH	Ktype覆盖早期4140 mm车身分支。	READY
50864_mid	50864	Sedan	Giulia 1600 TI (105 Series 1)	105	4	EU-ALFA-ROMEO-GIULIA-105-MID-SEDAN-01	HIGH	Ktype覆盖中期4160 mm车身分支。	READY
50864_nuova	50864	Sedan	Giulia Nuova (105)	105	4	EU-ALFA-ROMEO-GIULIA-105-NUOVA-SEDAN-01	HIGH	Ktype覆盖1974年后Nuova外廓分支。	READY
50863_early	50863	Sedan	Giulia TI Super (105 early)	105	4	EU-ALFA-ROMEO-GIULIA-105-EARLY-SEDAN-01	HIGH	Ktype覆盖早期4140 mm车身分支。	READY
50863_mid	50863	Sedan	Giulia TI Super (105 Series 1)	105	4	EU-ALFA-ROMEO-GIULIA-105-MID-SEDAN-01	HIGH	Ktype覆盖中期4160 mm车身分支。	READY
50863_nuova	50863	Sedan	Giulia Nuova Super (105)	105	4	EU-ALFA-ROMEO-GIULIA-105-NUOVA-SEDAN-01	HIGH	Ktype覆盖1974年后Nuova外廓分支。	READY
14742	14742	Sedan	Giulia Nuova Diesel (105)	105	4	EU-ALFA-ROMEO-GIULIA-105-NUOVA-SEDAN-01	HIGH	Nuova车身。	READY
50860	50860	Coupe	Giulia 1600 Sprint (101)	101.12	2	EU-ALFA-ROMEO-GIULIA-SPRINT-101-COUPE-01	HIGH		READY
50861	50861	Coupe	Giulia 1600 Sprint (101)	101.12	2	EU-ALFA-ROMEO-GIULIA-SPRINT-101-COUPE-01	HIGH		READY
123388	123388	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
119958	119958	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
119959	119959	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
120213	120213	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	HIGH		READY
123923	123923	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
126711	126711	Sedan	Giulia (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	HIGH	Q4增高外廓。	READY
119608	119608	Sedan	Giulia Quadrifoglio (952)	952	4	EU-ALFA-ROMEO-GIULIA-952-QUADRIFOGLIO-SEDAN-01	HIGH	Quadrifoglio宽体、保险杠及低车高外廓。	READY
59788	59788	Sedan	Giulietta (116)	116	4	EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	HIGH		READY
12017	12017	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
108276	108276	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
112138	112138	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
117422	117422	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
110004	110004	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
11001	11001	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
100763	100763	Hatchback	Giulietta (940)	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	HIGH		READY
17789	17789	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17792	17792	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-JTD-01	HIGH	厂方JTD车高分支。	READY
10997	10997	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17790	17790	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	HIGH	厂方标准汽油版本车高分支。	READY
17791	17791	Coupe	GT (937)	937	2	EU-ALFA-ROMEO-GT-937-COUPE-GTA-01	HIGH	3.2 GTA低车高分支。	READY
14739	14739	Coupe	GTA 1300 Junior (105)	105	2	EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	HIGH		READY
14740	14740	Coupe	GTA 1300 Junior (105)	105	2	EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	HIGH		READY
17286	17286	Coupe	GTV (916 Phase 3)	916	2	EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	HIGH	2003 Phase 3前部外廓。	READY
14743	14743	Coupe	Alfetta GTV Turbodelta (116)	116	3	EU-ALFA-ROMEO-ALFETTA-GTV-116-TURBODELTA-COUPE-01	HIGH	Turbodelta外廓。	READY
15622	15622	Coupe	GTV (916 Phase 2)	916	2	EU-ALFA-ROMEO-GTV-916-PREFL-COUPE-01	MEDIUM	3.0 V6 24V对应Phase 3之前外廓，未创建2003改款分支。	READY
17287	17287	Coupe	GTV (916 Phase 3)	916	2	EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	HIGH	2003 Phase 3前部外廓。	READY
158420	158420	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-ELETTRICA-01	HIGH		READY
158421	158421	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	HIGH	Veloce低悬架外廓。	READY
800229	800229	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	HIGH	Veloce低悬架外廓。	READY
158418	158418	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	HIGH	前驱Ibrida标准悬架外廓。	READY
802739	802739	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	HIGH	前驱Ibrida标准悬架外廓。	READY
801364	801364	SUV	Junior I		5	EU-ALFA-ROMEO-JUNIOR-I-SUV-Q4-01	HIGH	Q4增高外廓。	READY
10972	10972	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
50239	50239	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
13956	13956	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
58986	58986	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100784	100784	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100783	100783	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
13957	13957	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
120228	120228	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
3317	3317	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
100764	100764	Hatchback	MiTo (955)	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	HIGH		READY
127108_series3	127108	Convertible	Spider (115 Series 3)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-3-CONVERTIBLE-01	HIGH	Ktype覆盖Series 3空气动力套件外廓。	READY
127108_series4	127108	Convertible	Spider (115 Series 4)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-4-CONVERTIBLE-01	HIGH	Ktype覆盖1990年Series 4外廓。	READY
127184_series2	127184	Convertible	Spider (115 Series 2)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-2-CONVERTIBLE-01	HIGH	Ktype覆盖Series 2方尾外廓。	READY
127184_series3	127184	Convertible	Spider (115 Series 3)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-3-CONVERTIBLE-01	HIGH	Ktype覆盖1983年后Series 3外廓。	READY
12432	12432	Convertible	2000 Spider (102)	102	2	EU-ALFA-ROMEO-2000-SPIDER-102-CONVERTIBLE-01	HIGH		READY
121297	121297	Convertible	Spider (115 Series 2)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-2-CONVERTIBLE-01	HIGH	欧洲规格方尾外廓。	READY
127185_series2	127185	Convertible	Spider (115 Series 2)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-2-CONVERTIBLE-01	HIGH	Ktype覆盖Series 2方尾外廓。	READY
127185_series3	127185	Convertible	Spider (115 Series 3)	115	2	EU-ALFA-ROMEO-SPIDER-105-115-SERIES-3-CONVERTIBLE-01	HIGH	Ktype覆盖1983年后Series 3外廓。	READY
17288	17288	Convertible	Spider (916 Phase 3)	916	2	EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	HIGH	2003 Phase 3前部外廓。	READY
12902	12902	Convertible	Spider (916 Phase 1)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	HIGH		READY
15623	15623	Convertible	Spider (916 Phase 1/2)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	MEDIUM	3.0 V6对应Phase 3之前外廓，未创建2003改款分支。	READY
14771	14771	Convertible	Spider (916 Phase 2)	916	2	EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	HIGH	3.0 V6 24V对应Phase 3之前外廓。	READY
17289	17289	Convertible	Spider (916 Phase 3)	916	2	EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	HIGH	2003 Phase 3前部外廓。	READY
125157	125157	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126959	126959	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
143549	143549	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126958	126958	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
127368	127368	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126013	126013	SUV	Stelvio (949)	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_101-200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-156-932-FACELIFT-SEDAN-01	4435	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 2.5 V6 24V	https://www.automobile-catalog.com/car/2004/220055/alfa_romeo_156_2_5_v6_24v_distinctive_exclusive__lusso.html
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390	Automobile-Catalog 2004 Alfa Romeo 156 Sportwagon 2.4 JTD 20V	https://www.automobile-catalog.com/car/2004/220265/alfa_romeo_156_sportwagon_2_4_jtd_20v_distinctive_exclusive__lusso.html
EU-ALFA-ROMEO-156-932-PREFL-SEDAN-01	4430	1745	1415	Automobile-Catalog 1998 Alfa Romeo 156 2.5 V6 24V	https://www.automobile-catalog.com/car/1998/218780/alfa_romeo_156_2_5_v6_24v.html
EU-ALFA-ROMEO-156-932-PREFL-WAGON-01	4430	1745	1420	Automobile-Catalog 2001 Alfa Romeo 156 Sportwagon 2.5 V6 24V	https://www.automobile-catalog.com/car/2001/219410/alfa_romeo_156_sportwagon_2_5_v6_24v.html
EU-ALFA-ROMEO-156-GTA-932-SEDAN-01	4430	1765	1402	Automobile-Catalog Alfa Romeo 156 GTA	https://www.automobile-catalog.com/car/2002/219980/alfa_romeo_156_gta.html
EU-ALFA-ROMEO-156-GTA-932-WAGON-01	4430	1765	1411	Automobile-Catalog Alfa Romeo 156 Sportwagon GTA	https://www.automobile-catalog.com/car/2002/219965/alfa_romeo_156_sportwagon_gta.html
EU-ALFA-ROMEO-159-939-SEDAN-01	4660	1828	1417	Stellantis Media Alfa 159	https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-159-4
EU-ALFA-ROMEO-166-936-PREFL-SEDAN-01	4720	1815	1416	Automobile-Catalog Alfa Romeo 166 2.4 JTD	https://www.automobile-catalog.com/car/1999/220730/alfa_romeo_166_2_4_jtd.html
EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	4720	1800	1416	Stellantis Media Revised Alfa 166	https://www.media.stellantis.com/uk-en/alfa-romeo/press/revised-alfa-166-in-the-uk
EU-ALFA-ROMEO-4C-960-COUPE-01	3989	1864	1183	Stellantis Media Alfa Romeo 4C technical specification	https://www.media.stellantis.com/uploads/uk/UK/2013/ALFA_ROMEO/PRESS/71157alf%20-TECH_SPEC.doc
EU-ALFA-ROMEO-4C-960-CONVERTIBLE-01	3989	1864	1183	Auto-Data Alfa Romeo 4C Spider	https://www.auto-data.net/en/alfa-romeo-4c-spider-1.7-240hp-tct-22095
EU-ALFA-ROMEO-ALFASUD-SPRINT-902-SERIES-1-COUPE-01	4019	1610	1305	Automobile-Catalog 1980 Alfa Romeo Alfasud Sprint 1.5	https://www.automobile-catalog.com/car/1980/35930/alfa_romeo_alfasud_sprint_1_5.html
EU-ALFA-ROMEO-SPRINT-902-FACELIFT-COUPE-01	4024	1620	1305	Automobile-Catalog 1983 Alfa Romeo Sprint 1.5	https://www.automobile-catalog.com/car/1983/214550/alfa_romeo_sprint_1_5.html
EU-ALFA-ROMEO-ARNA-920-HATCHBACK-3D-01	4000	1651	1367	Automobile-Catalog 1983 Alfa Romeo Arna 1.2 L	https://www.automobile-catalog.com/car/1983/214655/alfa_romeo_arna_1_2_l.html
EU-ALFA-ROMEO-2000-BERLINA-105-SEDAN-01	4390	1565	1430	Automobile-Catalog 1972 Alfa Romeo 2000 Berlina	https://www.automobile-catalog.com/car/1972/71840/alfa_romeo_2000_berlina.html
EU-ALFA-ROMEO-GIULIA-SPIDER-101-CONVERTIBLE-01	3900	1540	1290	Automobile-Catalog 1963 Alfa Romeo Giulia 1600 Spider Tipo 101.23	https://www.automobile-catalog.com/car/1963/214055/alfa_romeo_giulia_1600_spider_tipo_101_23.html
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436	Alfa Romeo Canada 2019 Giulia official specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2019-alfaromeo-giulia-specifications-en.pdf
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450	Alfa Romeo Canada 2019 Giulia official specifications	https://www.alfaromeo.ca/documents/alfaromeo/specifications/2019-alfaromeo-giulia-specifications-en.pdf
EU-ALFA-ROMEO-GIULIA-952-QUADRIFOGLIO-SEDAN-01	4639	1873	1426	Automobile-Catalog 2018 Alfa Romeo Giulia Quadrifoglio	https://www.automobile-catalog.com/car/2018/2455370/alfa_romeo_giulia_quadrifoglio.html
EU-ALFA-ROMEO-GIULIA-105-1300-SEDAN-01	4115	1560	1430	Automobile-Catalog 1965 Alfa Romeo Giulia 1300	https://www.automobile-catalog.com/car/1965/64835/alfa_romeo_giulia_1300.html
EU-ALFA-ROMEO-GIULIA-105-EARLY-SEDAN-01	4140	1560	1430	Automobile-Catalog 1962 Alfa Romeo Giulia 1600 TI	https://www.automobile-catalog.com/car/1962/55550/alfa_romeo_giulia_1600_ti.html
EU-ALFA-ROMEO-GIULIA-105-MID-SEDAN-01	4160	1560	1430	Automobile-Catalog 1967 Alfa Romeo Giulia 1600 TI	https://www.automobile-catalog.com/car/1967/1375115/alfa_romeo_giulia_1600_ti.html
EU-ALFA-ROMEO-GIULIA-105-NUOVA-SEDAN-01	4185	1560	1430	Automobile-Catalog 1976 Alfa Romeo Giulia Diesel	https://www.automobile-catalog.com/car/1976/143525/alfa_romeo_giulia_diesel.html
EU-ALFA-ROMEO-GIULIA-SPRINT-101-COUPE-01	3980	1540	1348	Automobile-Catalog 1962 Alfa Romeo Giulia 1600 Sprint	https://www.automobile-catalog.com/car/1962/214040/alfa_romeo_giulia_1600_sprint.html
EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	4210	1650	1400	Automobile-Catalog 1983 Alfa Romeo Giulietta 1.8 L	https://www.automobile-catalog.com/car/1983/144515/alfa_romeo_giulietta_1_8_l.html
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-01	4351	1798	1465	Stellantis Media Alfa Romeo Giulietta technical specification	https://www.media.stellantis.com/uploads/pl/PL/2011/ALFA_ROMEO/SPECIFICATIONS/100413_AR_Giulietta_wyposazenie_TS.pdf
EU-ALFA-ROMEO-GT-937-COUPE-STANDARD-01	4489	1763	1362	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-GT-937-COUPE-JTD-01	4489	1763	1366	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-GT-937-COUPE-GTA-01	4489	1763	1355	Stellantis Media New Alfa GT in the UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-gt-in-the-uk
EU-ALFA-ROMEO-GTA-1300-JUNIOR-105-COUPE-01	4080	1580	1315	Alfa Romeo Museum GTA 1300 Junior	https://www.museoalfaromeo.com/en-us/collezione/Pages/GTA-1300-Junior-.aspx
EU-ALFA-ROMEO-GTV-916-PREFL-COUPE-01	4285	1780	1318	Automobile-Catalog 1997 Alfa Romeo GTV 3.0 V6 24V	https://www.automobile-catalog.com/car/1997/218405/alfa_romeo_gtv_3_0_v6_24v.html
EU-ALFA-ROMEO-GTV-916-FACELIFT-COUPE-01	4299	1776	1318	Automobile-Catalog 2003 Alfa Romeo GTV 2.0 JTS	https://www.automobile-catalog.com/car/2003/218660/alfa_romeo_gtv_2_0_jts_16v.html
EU-ALFA-ROMEO-ALFETTA-GTV-116-TURBODELTA-COUPE-01	4205	1660	1330	Automobile-Catalog 1980 Alfa Romeo Alfetta GTV 2000 Turbodelta	https://www.automobile-catalog.com/car/1980/144065/alfa_romeo_alfetta_gtv_2000_turbodelta.html
EU-ALFA-ROMEO-JUNIOR-I-SUV-ELETTRICA-01	4173	1781	1532	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-JUNIOR-I-SUV-VELOCE-01	4173	1781	1505	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-JUNIOR-I-SUV-IBRIDA-01	4173	1781	1539	Stellantis Media Alfa Romeo Junior technical specification	https://www.media.stellantis.com/uploads/uk/model-pricelist/junior-6a27e1a856441.pdf
EU-ALFA-ROMEO-JUNIOR-I-SUV-Q4-01	4173	1781	1544	Alfa Romeo France Junior official tariff April 2025	https://www.media.stellantis.com/uploads/fr/attachment//tarifpublicalfaromeogammemy2520250401-67ff6ae22a234.pdf
EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	4063	1720	1446	Stellantis Media New Alfa MiTo MultiAir in UK	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-mito-multiair-in-uk
EU-ALFA-ROMEO-2000-SPIDER-102-CONVERTIBLE-01	4500	1660	1330	Automobile-Catalog 1958 Alfa Romeo 2000 Spider	https://www.automobile-catalog.com/car/1958/213845/alfa_romeo_2000_spider.html
EU-ALFA-ROMEO-SPIDER-105-115-SERIES-2-CONVERTIBLE-01	4120	1630	1290	Automobile-Catalog 1975 Alfa Romeo Spider Veloce 2000 Europe	https://www.automobile-catalog.com/car/1975/27245/alfa_romeo_spider_veloce_2000.html
EU-ALFA-ROMEO-SPIDER-105-115-SERIES-3-CONVERTIBLE-01	4245	1630	1290	Automobile-Catalog 1984 Alfa Romeo Spider 2.0 Europe Germany	https://www.automobile-catalog.com/car/1984/214310/alfa_romeo_spider_2_0.html
EU-ALFA-ROMEO-SPIDER-105-115-SERIES-4-CONVERTIBLE-01	4258	1630	1290	Automobile-Catalog 1990 Alfa Romeo Spider 2.0 Europe	https://www.automobile-catalog.com/car/1990/217295/alfa_romeo_spider_2_0.html
EU-ALFA-ROMEO-SPIDER-916-PREFL-CONVERTIBLE-01	4285	1780	1315	Automobile-Catalog 1997 Alfa Romeo Spider 3.0 V6	https://www.automobile-catalog.com/car/1997/218435/alfa_romeo_spider_3_0_v6.html
EU-ALFA-ROMEO-SPIDER-916-FACELIFT-CONVERTIBLE-01	4299	1776	1315	Auto-Data Alfa Romeo Spider 916 facelift 3.2 V6	https://www.auto-data.net/de/alfa-romeo-spider-916-facelift-2003-3.2-v6-240hp-1450
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Stellantis Media Alfa Romeo Stelvio First Edition	https://www.media.stellantis.com/nl-nl/alfa-romeo/press/de-alfa-romeo-stelvio-first-edition-is-nu-bestelbaar
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_101-200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1983/214655/alfa_romeo_arna_1_2_l.html?utm_source=chatgpt.com "1983 Alfa Romeo Arna 1.2 L Specs Review (46.3 kW ..."
[2]: https://www.automobile-catalog.com/car/1971/65285/alfa_romeo_2000_spider_veloce.html?utm_source=chatgpt.com "1971 Alfa Romeo 2000 Spider Veloce (man. 5)"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（258 行）
- 累计尺寸组：dimension_groups_final.tsv（94 行）

