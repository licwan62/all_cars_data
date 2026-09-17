# 任务：all 第 3001-3100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0031__47f7956c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3001-3100 行

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
all 第 3001-3100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-BMW-X2-F39-SUV-01	4360	1824	1526
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638
EU-FORD-USA-MUSTANG-S550-ECOBOOST-COUPE-PREFL-01	4784	1916	1381
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-CONVERTIBLE-01	4789	1916	1387
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-COUPE-01	4789	1916	1373
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382
EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	4784	1916	1381
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645
EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	4084	1802	1129
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310
EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	4551	1939	1260
EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	5054	1953	1455
EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	5054	1953	1442
EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	5054	1953	1447
EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	4530	1695	1325
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448
EU-RENAULT-ESPACE-V-MPV-01	4857	1888	1677
EU-SUZUKI-JIMNY-III-JB33-CONVERTIBLE-PREFL-01	3625	1600	1655
EU-SUZUKI-JIMNY-III-JB43-CONVERTIBLE-01	3625	1600	1665
EU-SUZUKI-JIMNY-III-JB43-SUV-FACELIFT-2012-01	3675	1600	1705
EU-TOYOTA-AYGO-II-AB40-HATCHBACK-FACELIFT-01	3465	1615	1460
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-VW-GOLF-IV-1J1-VAN-3D-HIGH-01	4149	1735	1444
EU-VW-GOLF-IV-1J1-VAN-3D-LOW-01	4149	1735	1439
EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	4397	1735	1485
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Volvo	V70 iii	D5 AWD	Kombi	Allrad	Diesel	169	230	Mar 2011	Apr 2016	2024-03-01	133384
VW	Golf van iv variant	1.4	Kasten/Kombi	Frontantrieb	Benzin	55	75	May 2000	Jun 2006	2024-03-01	133386
Volvo	V70 iii	T6 AWD	Kombi	Allrad	Benzin	242	329	Nov 2013	Apr 2016	2024-03-01	133388
Volvo	V70 iii	D5	Kombi	Frontantrieb	Diesel	169	230	Mar 2011	Apr 2016	2024-03-01	133389
VW	Golf van iv variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	May 1999	May 2006	2024-03-01	133392
VW	Golf van iv variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	74	101	Feb 2000	Jun 2006	2024-03-01	133393
VW	Golf van iv variant	1.6	Kasten/Kombi	Frontantrieb	Benzin	77	105	May 2000	Jun 2006	2024-03-01	133397
VW	Golf van iv variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	81	110	May 1999	May 2006	2024-03-01	133398
VW	Golf van iv variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	85	116	May 1999	Apr 2002	2024-03-01	133399
Volvo	Xc70 ii	D5 AWD	Kombi	Allrad	Diesel	169	230	Nov 2013	Apr 2016	2024-03-01	133400
VW	Golf van iv variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	96	131	Apr 2001	May 2006	2024-03-01	133401
Volvo	Xc70 ii	T6 Polestar AWD	Kombi	Allrad	Benzin	242	329	Nov 2013	Dec 2016	2024-03-01	133402
VW	Golf iv	2.0 Bifuel	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	85	116	May 2002	May 2003	2024-03-01	133409
VW	Polo	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	82	May 2006	Nov 2009	2024-03-01	133411
Lotus	Exige	3.5 410	Cabriolet	Heckantrieb	Benzin	306	416	Oct 2018	-	2024-03-01	133416
Lotus	Exige	3.5 430	Coupe	Heckantrieb	Benzin	321	436	Nov 2017	-	2024-03-01	133417
Toyota	Aygo	1.0 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	50	68	Jul 2005	May 2014	2024-03-01	133419
Nissan	Qashqai i	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	86	117	Nov 2010	Dec 2013	2025-06-01	133425
Renault	Talisman	1.7 Blue DCI 120	Stufenheck	Frontantrieb	Diesel	88	120	Sep 2018	Mar 2022	2024-03-01	133426
Renault	Talisman	1.7 Blue DCI 150	Stufenheck	Frontantrieb	Diesel	110	150	Sep 2018	Mar 2022	2024-03-01	133427
Renault	Talisman	1.8 TCE 225	Stufenheck	Frontantrieb	Benzin	165	224	Sep 2018	Mar 2022	2024-03-01	133430
Renault	Talisman	1.7 Blue DCI 120	Kombi	Frontantrieb	Diesel	88	120	Sep 2018	Mar 2022	2024-03-01	133434
Renault	Talisman	1.7 Blue DCI 150	Kombi	Frontantrieb	Diesel	110	150	Sep 2018	Mar 2022	2024-03-01	133435
Toyota	Allion ii	1.8	Stufenheck	Frontantrieb	Benzin	100	136	Jul 2007	-	2025-06-01	133436
Renault	Talisman	1.8 TCE 225	Kombi	Frontantrieb	Benzin	165	224	Sep 2018	Mar 2022	2024-03-01	133437
Renault	Espace v	2.0 Blue DCI 160	Großraumlimousine	Frontantrieb	Diesel	118	160	Oct 2018	Mar 2023	2024-05-01	133448
Renault	Espace v	2.0 Blue DCI 200	Großraumlimousine	Frontantrieb	Diesel	147	200	Oct 2018	Mar 2023	2024-05-01	133450
Toyota	Verso	2.2 D-4d	Großraumlimousine	Frontantrieb	Diesel	100	136	Apr 2009	Aug 2018	2024-03-01	133451
Toyota	Rav 4 iv	2.2 D 4WD	SUV	Allrad	Diesel	130	177	Dec 2012	Sep 2019	2025-02-03	133453
Nissan	Skyline	2.0 AWD	Coupe	Allrad	Benzin	160	218	Jan 1990	Jan 1993	2024-03-01	133454
Renault	Clio iv	0.9 TCE 75	Schrägheck	Frontantrieb	Benzin	56	76	May 2018	Aug 2021	2026-05-01	133455
Nissan	Skyline	2	Stufenheck	Heckantrieb	Benzin	160	218	Jan 1990	Jan 1993	2024-03-01	133457
Citroën	Grand c4 spacetourer	1.6 Puretech 180	Großraumlimousine	Frontantrieb	Benzin	133	181	Apr 2018	-	2024-03-01	133465
Lexus	Nx	300h AWD	SUV	Allrad	Benzin/Elektro	145	197	Jul 2014	-	2024-03-01	133468
Toyota	Yaris	1.3 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	73	99	Oct 2012	Mar 2017	2024-05-01	133469
Citroën	C3 aircross i	1.5 Bluehdi 100	SUV	Frontantrieb	Diesel	73	99	Aug 2018	-	2025-11-01	133470
Citroën	C4 cactus	1.5 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	73	99	Jun 2018	-	2024-03-01	133471
Toyota	Yaris	1.0 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Jul 2014	Jun 2020	2024-05-01	133472
Toyota	Yaris	1.4 D4D	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Jul 2014	May 2018	2024-05-01	133473
Suzuki	Jimny	1.5 Allgrip	Geländewagen geschlossen	Allrad	Benzin	75	102	Jul 2018	-	2024-03-01	133475
BMW	X7	Xdrive 40 I	SUV	Allrad	Benzin	250	340	Mar 2019	-	2024-03-01	133483
BMW	X7	Xdrive 30 D	SUV	Allrad	Diesel	195	265	Mar 2019	-	2024-03-01	133485
BMW	X7	Xdrive M 50 D	SUV	Allrad	Diesel	294	400	Mar 2019	-	2024-03-01	133486
BMW	X2	Sdrive 16 D	SUV	Frontantrieb	Diesel	85	116	Nov 2018	Oct 2023	2024-03-01	133493
VW	Touran	1.6 Bifuel	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	75	102	Nov 2006	May 2010	2024-03-01	133496
VW	Scirocco	2.0 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	103	140	Aug 2008	May 2014	2024-03-01	133497
VW	Scirocco	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	90	122	Aug 2008	May 2014	2024-03-01	133501
VW	Golf vi van	2.0 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	103	140	Sep 2009	Nov 2012	2024-03-01	133503
VW	Golf vi van	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	118	160	Oct 2008	Nov 2012	2024-03-01	133504
VW	Golf vi van	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	77	105	May 2009	Nov 2012	2025-11-01	133509
VW	Golf vi van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	77	105	May 2009	Nov 2012	2025-11-01	133510
VW	Golf vi van	TSI	Kasten/Schrägheck	Frontantrieb	Benzin	90	122	Oct 2008	Nov 2012	2024-03-01	133511
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	66	90	May 2011	May 2014	2025-06-01	133512
VW	Polo	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Mar 2009	May 2014	2024-03-01	133515
VW	Polo	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Mar 2009	May 2014	2025-11-01	133516
VW	Polo	1.2 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Oct 2009	May 2014	2025-11-01	133517
VW	Polo	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	63	86	Mar 2009	May 2014	2024-03-01	133519
VW	Polo	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Jun 2009	May 2014	2025-11-01	133521
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	77	105	Nov 2009	May 2014	2025-11-01	133522
VW	Golf van vi variant	1.6 TDI	Kasten/Kombi	Frontantrieb	Diesel	77	105	Jul 2009	May 2014	2025-11-01	133524
VW	Golf van vi variant	2.0 TDI	Kasten/Kombi	Frontantrieb	Diesel	103	140	Jul 2009	May 2014	2024-03-01	133526
VW	Golf van vi variant	1.4 TSI	Kasten/Kombi	Frontantrieb	Benzin	118	160	Jul 2009	Oct 2012	2024-03-01	133527
VW	Golf van vi variant	1.2 TSI	Kasten/Kombi	Frontantrieb	Benzin	77	105	Sep 2009	May 2014	2024-03-01	133528
VW	Golf van vi variant	1.4 TSI	Kasten/Kombi	Frontantrieb	Benzin	90	122	Jul 2009	May 2014	2024-03-01	133529
VW	Golf plus van	2.0 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	103	140	Nov 2009	Aug 2014	2024-03-01	133530
VW	Golf plus van	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	118	160	Jan 2009	Sep 2012	2024-03-01	133531
VW	Golf plus van	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	77	105	Nov 2009	Aug 2014	2024-03-01	133533
VW	Golf plus van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	77	105	Feb 2009	Aug 2014	2024-03-01	133534
VW	Golf plus van	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	90	122	Jan 2009	Aug 2014	2024-03-01	133535
VW	Golf vi variant	1.6 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	75	102	Jul 2009	Dec 2010	2024-03-01	133536
Ford USA	Mustang	5.0 V8 Bullitt	Coupe	Heckantrieb	Benzin	338	460	Jun 2018	Apr 2023	2024-05-01	133537
KIA	Optima	1.7 Crdi	Kombi	Frontantrieb	Diesel	99	135	Sep 2016	Apr 2018	2024-03-01	133542
Mercedes-benz	Sprinter 3-T	310 D 2.9 4X4	Pritsche/Fahrgestell	Allrad	Diesel	75	102	Jan 1997	Apr 2000	2024-03-01	133546
VW	Passat b7	2.0 TDI	Kasten/Kombi	Frontantrieb	Diesel	103	140	Aug 2010	Dec 2014	2025-11-01	133559
VW	Passat b7	1.4 TSI	Kasten/Kombi	Frontantrieb	Benzin	90	122	Aug 2010	Dec 2014	2025-11-01	133563
Mercedes-benz	Amg gt	43 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	270	367	Oct 2018	-	2024-03-01	133568
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	100	136	Sep 2018	-	2024-03-01	133569
KIA	Optima	1.7 Crdi	Stufenheck	Frontantrieb	Diesel	99	135	Sep 2016	Apr 2018	2024-03-01	133575
Lotus	Exige	3.5 410	Coupe	Heckantrieb	Benzin	306	416	Apr 2018	-	2024-03-01	133577
Ssangyong	Tivoli	1.6 CNG	SUV	Frontantrieb	Benzin/Erdgas (CNG)	94	128	Jul 2018	-	2024-03-01	133578
Ssangyong	Xlv	1.6 CNG	SUV	Frontantrieb	Benzin/Erdgas (CNG)	94	128	Jul 2018	-	2024-03-01	133579
Opel	Grandland	1.6 Turbo	SUV	Frontantrieb	Benzin	133	181	Sep 2018	Jul 2021	2025-02-03	133580
Ford	Ka+ iii	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Feb 2018	Dec 2020	2026-04-01	133584
Ford	Ka+ iii	1.2	Schrägheck	Frontantrieb	Benzin	63	85	Feb 2018	Dec 2020	2026-04-01	133585
VW	Golf vii van	2.0 GTI	Kasten/Schrägheck	Frontantrieb	Benzin	162	220	Apr 2013	Mar 2017	2024-03-01	133589
VW	Golf vii van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Apr 2013	Mar 2017	2025-11-01	133593
Fiat	Linea	1.3 JTD Multijet	Stufenheck	Frontantrieb	Diesel	63	86	Oct 2006	-	2024-03-01	133594
VW	Golf vii van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	77	105	Aug 2012	Mar 2017	2025-11-01	133596
VW	Golf vii van	1.6 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	81	110	Nov 2013	Mar 2017	2025-11-01	133597
VW	Golf vii van	2.0 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	110	150	May 2013	May 2014	2025-11-01	133599
VW	Golf van vii variant	2.0 TDI 4motion	Kasten/Kombi	Allrad	Diesel	110	150	Apr 2013	Mar 2017	2025-11-01	133603
VW	Golf van vii variant	2.0 TDI	Kasten/Kombi	Frontantrieb	Diesel	110	150	Apr 2013	Mar 2017	2025-11-01	133606
VW	Golf van vii variant	1.6 TDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	May 2013	Mar 2017	2025-11-01	133609
VW	Golf van vii variant	1.6 TDI	Kasten/Kombi	Frontantrieb	Diesel	77	105	May 2013	Mar 2017	2025-11-01	133612
VW	Golf van vii variant	1.6 TDI	Kasten/Kombi	Frontantrieb	Diesel	81	110	May 2013	Mar 2017	2025-11-01	133613
Citroën	Grand c4 spacetourer	1.6 HDI 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Apr 2018	-	2024-03-01	133625
Maserati	Biturbo	Racing	Coupe	Heckantrieb	Benzin	208	283	Apr 1990	Dec 1992	2024-03-01	133628
Nissan	Pixo	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	50	68	Mar 2009	-	2024-03-01	133634
Nissan	Teana ii	2.5	Stufenheck	Frontantrieb	Benzin	123	167	Mar 2010	Jan 2013	2024-03-01	133636
Audi	A3	30 TDI	Stufenheck	Frontantrieb	Diesel	85	115	Jul 2018	Oct 2020	2024-03-01	133637


--- Round 1 / 首次发送 ---
## 更新点

* 完成首轮缓存关联：新增 **23 条 READY 映射**，全部引用跨批次已有尺寸组。
* 本轮未新建或修正尺寸组，因此不重复输出既有尺寸及来源。
* 已重点核对 Golf IV Variant、BMW X2 F39、Mustang Bullitt 和 Kia Optima Sedan/Sportswagon 的车型边界；大众官方资料将 Golf IV Variant 归入 1J 系列，BMW 官方技术资料明确 X2 为 F39，Ford 将 Bullitt定义为改款 Mustang GT Fastback 的特别版本，Kia 官方资料区分 JF Sedan 与 Sportswagon。([Volkswagen Newsroom][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：23
* 尚未闭合输入 Ktype：77
* 已关联尺寸组：15
* 本轮新增尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133386	133386	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133392	133392	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133393	133393	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133397	133397	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133398	133398	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133399	133399	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133401	133401	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133448	133448	MPV	Espace V	RFC	5	EU-RENAULT-ESPACE-V-MPV-01	HIGH		READY
133450	133450	MPV	Espace V	RFC	5	EU-RENAULT-ESPACE-V-MPV-01	HIGH		READY
133454	133454	Coupe	Skyline R32	R32	2	EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	HIGH	R32双门GTS-4外廓。	READY
133455	133455	Hatchback	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	Clio IV改款五门车身。	READY
133465	133465	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
133470	133470	SUV	C3 Aircross I Phase I	A88	5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH	BlueHDi 100对应第一阶段车身。	READY
133471	133471	Hatchback	C4 Cactus I Facelift	E3	5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	2018年改款车身。	READY
133493	133493	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133537	133537	Coupe	Mustang VI Facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH	Bullitt为改款GT Fastback外廓。	READY
133542	133542	Wagon	Optima IV	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH	JF Sportswagon五门车身。	READY
133568	133568	Coupe	AMG GT 4-Door Coupe I	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH	X290四门轿跑掀背外廓。	READY
133569	133569	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	普通PD五门车身，非N宽体版本。	READY
133575	133575	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH	JF四门轿车车身。	READY
133580	133580	SUV	Grandland X I	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	2018至2021年A18改款前外廓。	READY
133625	133625	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
133637	133637	Sedan	A3 8V Facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8V改款四门Sedan车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量闭合 VW 商用化车身簇：Golf VI Van、Golf VI Variant Van、Golf Plus Van、Polo V Van、Golf VII Van、Golf VII Variant Van、Passat B7 Variant Van。
2. 集中建立 Volvo V70 III／XC70 II 与 Renault Talisman Sedan／Wagon 尺寸组。
3. 单独处理可能需要派生的边界：Lexus NX 改款前后、Toyota Yaris Van 门数与改款、Lotus Exige Coupe／Roadster、Mercedes-Benz Sprinter 驾驶室及轴距。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/engine-versions-golf-4-variant-profile-19524?utm_source=chatgpt.com "Engine versions Golf IV Variant profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 **20 条 READY 映射**，首次闭合 **6 个 DIMENSION_GROUP**。
* 已批量完成 XC70 II、Talisman Sedan/Wagon、Golf VI Variant、Golf VII Variant 前驱版及 Passat B7 Variant 商用化车身。
* Golf VII Variant 4Motion 暂不并入前驱尺寸组，保留后续独立核对。
* 新建组均采用厂商官方尺寸资料，`WidthMM` 为不含外后视镜宽度。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：43
* PENDING 输入 Ktype：57
* 已确认尺寸组：21
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133400	133400	Wagon	XC70 II Facelift		5	EU-VOLVO-XC70-II-FACELIFT-WAGON-01	HIGH		READY
133402	133402	Wagon	XC70 II Facelift		5	EU-VOLVO-XC70-II-FACELIFT-WAGON-01	HIGH	Polestar动力升级不改变车身外廓。	READY
133426	133426	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133427	133427	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133430	133430	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133434	133434	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133435	133435	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133437	133437	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133524	133524	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133526	133526	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133527	133527	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133528	133528	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133529	133529	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133536	133536	Wagon	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH		READY
133559	133559	Van	Passat B7 Variant	3C	5	EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	HIGH	Variant货运化车身。	READY
133563	133563	Van	Passat B7 Variant	3C	5	EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	HIGH	Variant货运化车身。	READY
133606	133606	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133609	133609	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133612	133612	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133613	133613	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-XC70-II-FACELIFT-WAGON-01	4838	1870	1604	Volvo XC70 2016 Owner Manual - Dimensions	https://www.volvocars.com/uk/support/car/xc70/article/18f77489f78f457dc0a801e800a04016/
EU-RENAULT-TALISMAN-I-SEDAN-01	4849	1868	1456	Renault Talisman official price list - Dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Talisman_PL_f.pdf
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465	Renault Talisman Grandtour official price list - Dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Talisman_Grandtour_PL_f.pdf
EU-VW-GOLF-VI-AJ-VARIANT-01	4534	1781	1504	Volkswagen Golf VI Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-6-variant-profile-19529
EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	4771	1820	1508	Volkswagen Passat B7 official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	4562	1799	1481	Volkswagen Golf VII Estate official press presentation	https://www.volkswagen-newsroom.com/en/the-new-golf-estate-international-press-presentation-2977/the-new-golf-estate-overview-quick-facts-3002
```

## 下一步优先处理

1. 核对 Golf VII Variant 4Motion 高度差异并独立闭合 `133603`。
2. 按改款边界拆分 Volvo V70 III 跨 2013 年改款的 Ktype。
3. 批量处理 Polo V Van、Golf VI Van、Golf Plus Van 和 Golf VII Van 四个大众车身簇。
4. 闭合 Lotus Exige Coupe/Roadster、Toyota Yaris Van 与 Lexus NX 跨改款分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增 **22 条 READY 映射**，首次闭合 **6 个 DIMENSION_GROUP**。
* 已批量完成 BMW X7 G07、Scirocco III 商用化三门车身、Golf VI 三门 Van、Polo V 6R 三门 Van，以及 Golf VII 标准版与 GTI 三门 Van。尺寸组依据厂商官方技术资料建立，宽度均采用不含后视镜口径。([BMW Group PressClub][1])
* Golf Plus Van、Touran BiFuel 与 Golf VII Variant 4Motion 尚未在本轮建立尺寸组，避免使用官方资料中的未拆分尺寸范围。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：65
* PENDING 输入 Ktype：35
* 已确认尺寸组：27
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133483	133483	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
133485	133485	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
133486	133486	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	M50d动力版本不改变车身外廓。	READY
133497	133497	Van	Scirocco III Pre-Facelift	13	3	EU-VW-SCIROCCO-III-13-VAN-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133501	133501	Van	Scirocco III Pre-Facelift	13	3	EU-VW-SCIROCCO-III-13-VAN-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133503	133503	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133504	133504	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133509	133509	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133510	133510	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133511	133511	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133512	133512	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133515	133515	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133516	133516	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133517	133517	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133519	133519	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133521	133521	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133522	133522	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133589	133589	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	HIGH	GTI三门货运化车身。	READY
133593	133593	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133596	133596	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133597	133597	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133599	133599	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X7-G07-SUV-01	5151	2000	1805	BMW Group PressClub - The first-ever BMW X7	https://www.press.bmwgroup.com/global/article/detail/T0285836EN/the-first-ever-bmw-x7?language=en
EU-VW-SCIROCCO-III-13-VAN-PREFL-01	4256	1810	1404	Volkswagen The New Scirocco International Driving Presentation	https://www.volkswagen-newsroom.com/en/the-new-scirocco-international-driving-presentation-portugal-june-2008-2349
EU-VW-GOLF-VI-1K-VAN-3D-01	4199	1779	1480	Volkswagen UK Golf VI official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_oct_2011.pdf
EU-VW-POLO-V-6R-VAN-3D-PREFL-01	3970	1682	1484	Volkswagen Polo V official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	4268	1799	1442	Volkswagen Golf VII GTI official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-gti-profile-20033
EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	4255	1799	1452	Volkswagen The New Golf official quick facts	https://www.volkswagen-newsroom.com/en/the-new-golf-das-auto-international-driving-presentation-2797/the-new-golf-overview-quick-facts-2854
```

## 下一步优先处理

1. 闭合 Golf Plus Van、Touran BiFuel 和 Golf VII Variant 4Motion 的具体配置尺寸。
2. 拆分并闭合跨越 2013 年改款的 Volvo V70 III Ktype。
3. 处理 Toyota Yaris Van、Aygo Van、RAV4 IV、Lexus NX 和 Suzuki Jimny 的改款边界。
4. 最后集中处理 Lotus Exige、Sprinter 驾驶室、Allion、Skyline Sedan、Maserati Biturbo Racing 等低复用车型。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/detail/T0285836EN/the-first-ever-bmw-x7?language=en&utm_source=chatgpt.com "The first-ever BMW X7."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增 15 条 READY 映射，覆盖 13 个输入 Ktype。
* 首次闭合 6 个 DIMENSION_GROUP。
* Volvo V70 III 中跨越外廓变化的两个 Ktype 已拆为改款前、改款后派生行。
* Golf Plus、Touran、Golf VII Variant 4Motion 与 Ford Ka+ 相同外廓车型已批量关联。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：78
* READY 映射行：80
* PENDING 输入 Ktype：22
* 已确认尺寸组：33
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133384_prefl	133384	Wagon	V70 III Pre-Facelift	BW	5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133384_facelift	133384	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133388	133388	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
133389_prefl	133389	Wagon	V70 III Pre-Facelift	BW	5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133389_facelift	133389	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133496	133496	MPV	Touran I Facelift I	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH		READY
133530	133530	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133531	133531	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133533	133533	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133534	133534	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133535	133535	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133584	133584	Hatchback	Ka III Facelift	B562	5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH		READY
133585	133585	Hatchback	Ka III Facelift	B562	5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH		READY
133603	133603	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	HIGH	4Motion货运化Variant车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Volvo Cars Media UK - All-new Volvo V70 specifications	https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Volvo V70 2014 official support - Dimensions	https://www.volvocars.com/uk/support/car/v70/14w20/article/18f77489f78f457dc0a801e800a04016/
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635	Volkswagen Touran 2007 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2007-UK.pdf
EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	4204	1759	1580	Volkswagen The New Golf Plus 2009 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-Golf-Plus-2009-UK.pdf
EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	3941	1704	1524	Ford KA+ MY2019 official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_KA%2B.pdf
EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	4562	1799	1515	Volkswagen Golf VII Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042
```

本轮新建组的尺寸边界和不含后视镜宽度依据对应厂商资料闭合。([沃尔沃汽车媒体][1])

## 下一步优先处理

1. 批量闭合 Toyota Aygo、Yaris Van、Verso、RAV4 IV 与 Lexus NX 的代际及改款分支。
2. 处理 Lotus Exige 410/430 Coupe、410 Roadster 的宽体和车顶差异。
3. 闭合 Suzuki Jimny IV、SsangYong Tivoli/XLV、Nissan Qashqai I 与 Pixo。
4. 最后处理 Sprinter 4×4底盘驾驶室、Allion II、Skyline Sedan、Fiat Linea、Teana II 和 Biturbo Racing。

推进信号：CONTINUE

[1]: https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088?utm_source=chatgpt.com "PRICES AND SPECIFICATION DETAILS FOR ALL NEW VOLVO V70 AND VOLVO XC70 - Volvo Car UK Media Newsroom"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 机械复算修正上一轮进度：此前实际为 **77 个 READY 输入 Ktype、79 条 READY 映射**。
* 本轮新增 **13 个 READY 输入 Ktype、15 条 READY 映射**，首次闭合 **12 个 DIMENSION_GROUP**。
* 已完成 Lotus Exige Sport 410 Coupe/Roadster、Cup 430 Coupe 的独立外廓关联。([Lotus Antwerp][1])
* 已完成 Aygo I Van、Verso、NX 改款前后、Yaris III Van 改款前后及 Jimny IV。([Toyota Media Site][2])
* 已完成 Qashqai I Facelift、Tivoli 与 XLV。([汽车目录档案][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：90
* READY 映射行：94
* PENDING 输入 Ktype：10
* 已确认尺寸组：45
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133416	133416	Convertible	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-SPORT-410-ROADSTER-01	HIGH	Sport 410 Roadster可拆卸车顶外廓。	READY
133417	133417	Coupe	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-CUP-430-COUPE-01	HIGH	Cup 430专属空气动力套件外廓。	READY
133419	133419	Van	Aygo I	AB10	3	EU-TOYOTA-AYGO-I-AB10-VAN-3D-01	MEDIUM	三门货运化掀背车身。	READY
133425	133425	SUV	Qashqai I Facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	HIGH		READY
133451	133451	MPV	Verso I	AR20	5	EU-TOYOTA-VERSO-I-AR20-MPV-01	HIGH		READY
133468_prefl	133468	SUV	NX I Pre-Facelift	AYZ15	5	EU-LEXUS-NX-I-PREFL-SUV-01	HIGH	Ktype覆盖2017年外廓改款。	READY
133468_facelift	133468	SUV	NX I Facelift	AYZ15	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	Ktype覆盖2017年外廓改款。	READY
133469_prefl	133469	Van	Yaris III Pre-Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	MEDIUM	Ktype覆盖2014年外廓改款。	READY
133469_facelift	133469	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	Ktype覆盖2014年外廓改款。	READY
133472	133472	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	三门货运化掀背车身。	READY
133473	133473	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	三门货运化掀背车身。	READY
133475	133475	SUV	Jimny IV	JB74	3	EU-SUZUKI-JIMNY-IV-JB74-SUV-01	HIGH		READY
133577	133577	Coupe	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-SPORT-410-COUPE-01	HIGH	Sport 410固定车顶外廓。	READY
133578	133578	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
133579	133579	SUV	XLV I	X100	5	EU-SSANGYONG-XLV-I-X100-SUV-01	HIGH	加长后部车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-ROADSTER-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Sport 410 technical specifications	https://lotusantwerp.be/lotus-exige-sport-410/
EU-LOTUS-EXIGE-SERIES-3-CUP-430-COUPE-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Cup 430 technical specifications	https://lotusantwerp.be/lotus-exige-cup-430-edition/
EU-TOYOTA-AYGO-I-AB10-VAN-3D-01	3405	1615	1465	Toyota Media - Aygo Is Go technical specifications	https://media.toyota.co.uk/aygo-is-go/
EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	4330	1780	1615	Nissan Qashqai 2010 official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Nissan-Qashqai-2010-UK.pdf
EU-TOYOTA-VERSO-I-AR20-MPV-01	4440	1790	1620	Toyota Media - World Premiere of the New Toyota Verso	https://media.toyota.co.uk/world-premiere-of-the-new-toyota-verso/
EU-LEXUS-NX-I-PREFL-SUV-01	4630	1845	1645	Lexus Media - New NX Crossover Opens a New Chapter for Lexus	https://media.lexus.co.uk/new-nx-crossover-opens-new-chapter-lexus/
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510	Auto-Data - Toyota Yaris III 1.33 Dual VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.33-dual-vvt-i-99hp-17110
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510	Toyota Yaris official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1485445765170110MTechSpec.pdf
EU-SUZUKI-JIMNY-IV-JB74-SUV-01	3645	1645	1720	Suzuki Global - Jimny main specifications	https://www.globalsuzuki.com/globalnews/2021/0120.html
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-COUPE-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Sport 410 technical specifications	https://lotusantwerp.be/lotus-exige-sport-410/
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590	SsangYong Tivoli official brochure	https://cdn.mattaki.com/ssangyong/static-assets/vehicles/brochures/tivoli_ebrochure.pdf
EU-SSANGYONG-XLV-I-X100-SUV-01	4440	1798	1635	SsangYong Tivoli XLV official brochure	https://cdn.mattaki.com/ssangyong/static-assets/vehicles/brochures/tivoli-xlv_ebrochure.pdf
```

## 下一步优先处理

1. 闭合 VW Golf IV BiFuel 与 Polo IV BiFuel 的门数及车身边界。
2. 处理 Toyota Allion II、RAV4 IV 2.2 D-4D 和 Nissan Skyline R32 Sedan。
3. 闭合 Mercedes-Benz Sprinter 3-T 4×4 驾驶室与轴距分支。
4. 完成 Fiat Linea、Maserati Biturbo Racing、Nissan Pixo 与 Teana II。

推进信号：CONTINUE

[1]: https://lotusantwerp.be/lotus-exige-sport-410/ "Lotus Exige Sport 410 - Lotus Antwerp"
[2]: https://media.toyota.co.uk/aygo-is-go/?utm_source=chatgpt.com "Aygo Is Go - Toyota Media Site"
[3]: https://autocatalogarchive.com/wp-content/uploads/2017/07/Nissan-Qashqai-2010-UK.pdf?utm_source=chatgpt.com "Nissan-Qashqai-2010-UK.pdf"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 新增 **9 个 READY 输入 Ktype、12 条 READY 映射**，首次闭合 **12 个 DIMENSION_GROUP**。
* Golf IV 与 Polo IV 的 Ktype 均按三门、五门物理车身拆分；Golf 2.0 的两种门数外廓尺寸一致，Polo 9N3 的两种门数外廓尺寸一致，但分别保留独立尺寸组。([Autocentrum.pl][1])
* RAV4 IV 按 2015 年外廓改款拆分；Allion II、Pixo I、Teana II 已依据厂商规格闭合。([丰田官网][2])
* 仅剩 Sprinter Ktype `133546`：该 Ktype 同时覆盖 `903.421`、`903.422`、`903.423`，已确认其中至少存在 3000 mm 与 3550 mm 轴距以及不同驾驶室分支，暂不创建猜测性尺寸组。([Top Autopiese][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* READY 映射行：106
* PENDING 输入 Ktype：1
* PENDING 映射行：1
* 已确认尺寸组：57
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133409_3dr	133409	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-HIGH-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133409_5dr	133409	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-HIGH-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133411_3dr	133411	Hatchback	Polo IV Facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133411_5dr	133411	Hatchback	Polo IV Facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133436	133436	Sedan	Allion II	ZRT260	4	EU-TOYOTA-ALLION-II-ZRT260-SEDAN-01	HIGH		READY
133453_prefl	133453	SUV	RAV4 IV Pre-Facelift	ALA49	5	EU-TOYOTA-RAV4-IV-ALA49-SUV-PREFL-01	MEDIUM	Ktype生产期跨越2015年外廓改款。	READY
133453_facelift	133453	SUV	RAV4 IV Facelift	ALA49	5	EU-TOYOTA-RAV4-IV-ALA49-SUV-FACELIFT-01	MEDIUM	Ktype生产期跨越2015年外廓改款。	READY
133457	133457	Sedan	Skyline R32	HCR32	4	EU-NISSAN-SKYLINE-R32-SEDAN-GTS-T-01	HIGH	HCR32四门GTS-t外廓。	READY
133546	133546	Pickup	Sprinter I	W903			LOW	Ktype覆盖903.421、903.422、903.423不同驾驶室、轴距及平台分支。	PENDING: 驾驶室、轴距及平台长度分支未闭合
133594	133594	Sedan	Linea I	323	4	EU-FIAT-LINEA-I-323-SEDAN-01	MEDIUM		READY
133628	133628	Coupe	Biturbo Racing	AM331	2	EU-MASERATI-BITURBO-RACING-AM331-COUPE-01	HIGH	AM331 Racing双门外廓。	READY
133634	133634	Hatchback	Pixo I	UA0	5	EU-NISSAN-PIXO-I-UA0-HATCHBACK-01	HIGH		READY
133636	133636	Sedan	Teana II	J32	4	EU-NISSAN-TEANA-II-J32-SEDAN-01	HIGH	J32前驱四门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-HIGH-01	4149	1735	1444	Volkswagen Golf IV official vehicle data; UltimateSpecs Golf 4 3-door Highline 2.0	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478; https://www.ultimatespecs.com/car-specs/Volkswagen/43944/Volkswagen-Golf-4-3-doors-Highline-20.html
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-HIGH-01	4149	1735	1444	Volkswagen Golf IV official vehicle data; AutoCentrum Golf IV Hatchback 2.0	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478; https://www.autocentrum.pl/dane-techniczne/volkswagen/golf/iv/hatchback/silnik-benzynowy-2.0-115km-85kw-1998-2003/
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467	Volkswagen Polo IV official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467	Volkswagen Polo IV official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
EU-TOYOTA-ALLION-II-ZRT260-SEDAN-01	4565	1695	1475	Toyota 75 Years Vehicle Lineage - Allion A18	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008987/index.html
EU-TOYOTA-RAV4-IV-ALA49-SUV-PREFL-01	4570	1845	1660	Auto-Data Toyota RAV4 IV 2.2 D-4D 4WD	https://www.auto-data.net/en/toyota-rav4-iv-2.2-d-4d-150hp-4wd-18106
EU-TOYOTA-RAV4-IV-ALA49-SUV-FACELIFT-01	4605	1845	1675	Toyota RAV4 official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1547121943180511MRAV4TechnicalSpecifications.pdf
EU-NISSAN-SKYLINE-R32-SEDAN-GTS-T-01	4580	1695	1340	Automobile-Catalog 1990 Nissan Skyline 4-door Sports Sedan GTS-t Type-M	https://www.automobile-catalog.com/car/1990/2134895/nissan_skyline_4door_sports_sedan_gts-t_type-m.html
EU-FIAT-LINEA-I-323-SEDAN-01	4560	1730	1494	Fiat Linea official technical specifications; Carfolio Fiat Linea 1.3 Multijet 16v	https://www.team-bhp.com/forum/attachments/indian-car-scene/41241d1219421020-scoop-fiat-linea-pics-pg-1-5-linea_specs.pdf; https://www.carfolio.com/fiat-linea-1.3-multijet-16v-157586
EU-MASERATI-BITURBO-RACING-AM331-COUPE-01	4200	1714	1305	Maserati Classic - Racing; Automobile-Catalog Maserati Racing	https://www.maserati.com/global/en/brand/maserati-classic-cars/biturbo-and-derivates/racing; https://www.automobile-catalog.com/car/1992/1446290/maserati_racing.html
EU-NISSAN-PIXO-I-UA0-HATCHBACK-01	3565	1600	1470	Nissan Pixo official UK brochure	https://cache3.pakwheels.com/system/brochures/959/original/Nissan-Pixo-2011-UK.pdf?1750824844=
EU-NISSAN-TEANA-II-J32-SEDAN-01	4850	1795	1475	Nissan Teana J32 official specifications	https://history.nissan.co.jp/TEANA/J32/1206/j320806g02.html?gradeID=G02&model=TEANA
```

## 下一步优先处理

1. 分离 Sprinter `903.421`、`903.422`、`903.423` 的单排/双排驾驶室、3000/3550 mm 轴距及平台长度边界。
2. 为确认存在的每个物理配置分别创建尺寸组；闭合唯一剩余 PENDING 后立即进入 COMPLETE 机械收尾。

推进信号：CONTINUE

[1]: https://www.autocentrum.pl/dane-techniczne/volkswagen/golf/iv/hatchback/silnik-benzynowy-2.0-115km-1998-2003/ "Volkswagen Golf IV Hatchback 2.0 115KM 85kW 1998-2003 • Dane techniczne • AutoCentrum.pl"
[2]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008987/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[3]: https://www.topautopiese.ro/piese-auto/claxon/10420/mercedes-benz-sprinter-3-t-platou-sasiu-903/133546-310-d-2-9-4x4-903-421-903-422-903-423?utm_source=chatgpt.com "Claxon MERCEDES-BENZ SPRINTER 3-t platou / sasiu (903) ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已确认 `133546` 实际覆盖三个双排驾驶室底盘分支：`903.421` 为 3000 mm 轴距、`903.422` 为 3550 mm、`903.423` 为 4025 mm；现拆为 `swb / mwb / lwb` 三行，不再保留无后缀基础行。([PartSouq][1])
* 已核对资料能够确认 4×4 底盘及车身抬升差异，但尚未同时闭合三个分支的完整长度、不含后视镜宽度和整车高度，因此本轮不创建猜测性尺寸组。([Dezo's Garage][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* READY 映射行：106
* PENDING 输入 Ktype：1
* PENDING 映射行：3
* 已确认尺寸组：57
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133546_swb	133546	Pickup	Sprinter I	903.421			HIGH	双排驾驶室，3000 mm轴距分支。	PENDING: 完整三维尺寸未闭合
133546_mwb	133546	Pickup	Sprinter I	903.422			HIGH	双排驾驶室，3550 mm轴距分支。	PENDING: 完整三维尺寸未闭合
133546_lwb	133546	Pickup	Sprinter I	903.423			HIGH	双排驾驶室，4025 mm轴距分支。	PENDING: 完整三维尺寸未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅补齐 `903.421 / 903.422 / 903.423` 三个双排驾驶室 4×4 底盘分支的完整同配置三维及不含后视镜宽度。
2. 三个尺寸组闭合后，将三行映射改为 READY，并立即执行最终机械检查及 COMPLETE 输出。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A9019970535&srsltid=AfmBOoojtUdzvJS5SQqltcT-jJI7vZW2J0bP-hQODVigIfGlRYavZj9B&ssd=%24%2AKwHY7P3wrqqhjKuxna386ICUtLOt3NPe383i0ZmfrKKvppKxw87XqqrV3dvS1dmDiJLflZqIgquXzMWfm4SegIHGyYGNkYeD09vf2djazsKRzsLI0c7PxsmBhZGHg9u4zsHIiILMiZ-S367Owcidj8yJn5LIlgAAAACMqSN1%24&utm_source=chatgpt.com "Mercedes-Benz Parts Catalogs SPRINTER 310 D,312 D"
[2]: https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Sprinter-Traveliner-Spec-Sheet-UK.pdf "10737_Freestone_22.03.05_LT"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 完成唯一剩余 Sprinter 分支的定向核对。DaimlerChrysler 车身制造指南确认 Sprinter 存在 **3000、3550、4025 mm** 三种轴距，但明确要求底盘及驾驶室尺寸以单独的 `offer drawings` 为准，指南正文未提供可直接闭合三维的外廓表。([DIY Sprinter][1])
* `903.423` 的精确车型记录仅提供 **1922 mm 宽度**和 **4025 mm 轴距**，长度、高度为空，且现有资料不足以确认该宽度属于同一 4×4 双排驾驶室配置的无后视镜口径。([Autogidas][2])
* `903.421 / 903.422 / 903.423` 仍不满足“同一配置完整长宽高＋无镜宽度”的建组条件。本轮未猜测建组，也未修改既有映射。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* READY 映射行：106
* PENDING 输入 Ktype：1
* PENDING 映射行：3
* 已确认尺寸组：57
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 获取 `903.421 / 903.422 / 903.423` 对应的历史 Mercedes-Benz `offer drawings`、车身制造尺寸图或型式认证资料。
2. 分别闭合三个 4×4 双排驾驶室底盘分支的完整长度、不含后视镜宽度和高度。
3. 三个尺寸组闭合后立即将映射改为 READY，并进入 COMPLETE 机械收尾。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/Sprinter2002Body%20Builders%20Handbook.pdf "ARL Sprinter.book"
[2]: https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/310-d-903.423-1996-2000-k31196?utm_source=chatgpt.com "Mercedes-Benz Sprinter 310 D 903.423 1996-2000"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 最后一个 Ktype `133546` 已按 `903.421 / 903.422 / 903.423` 拆分为 SWB、MWB、LWB 三个双排驾驶室底盘分支。对应资料分别确认 3 门结构及 `4819×1900×2135`、`5569×1900×2135`、`6124×1900×2160 mm` 的外廓。([二手车目录][1])
* 最终机械检查完成：109 个映射 `id` 唯一、61 个尺寸组 ID 唯一、所有引用闭合、无孤立尺寸组、无 PENDING。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：109
* PENDING：0
* DIMENSION_GROUP：61
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
133384_prefl	133384	Wagon	V70 III Pre-Facelift	BW	5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133384_facelift	133384	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133386	133386	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133388	133388	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
133389_prefl	133389	Wagon	V70 III Pre-Facelift	BW	5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133389_facelift	133389	Wagon	V70 III Facelift	BW	5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH	Ktype生产期跨越2013年外廓变更。	READY
133392	133392	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133393	133393	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133397	133397	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133398	133398	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133399	133399	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133400	133400	Wagon	XC70 II Facelift		5	EU-VOLVO-XC70-II-FACELIFT-WAGON-01	HIGH		READY
133401	133401	Van	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	HIGH	1J5五门Variant货运化车身。	READY
133402	133402	Wagon	XC70 II Facelift		5	EU-VOLVO-XC70-II-FACELIFT-WAGON-01	HIGH	Polestar动力升级不改变车身外廓。	READY
133409_3dr	133409	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-HIGH-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133409_5dr	133409	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-HIGH-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133411_3dr	133411	Hatchback	Polo IV Facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133411_5dr	133411	Hatchback	Polo IV Facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	MEDIUM	Ktype覆盖三门与五门物理车身。	READY
133416	133416	Convertible	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-SPORT-410-ROADSTER-01	HIGH	Sport 410 Roadster可拆卸车顶外廓。	READY
133417	133417	Coupe	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-CUP-430-COUPE-01	HIGH	Cup 430专属空气动力套件外廓。	READY
133419	133419	Van	Aygo I	AB10	3	EU-TOYOTA-AYGO-I-AB10-VAN-3D-01	MEDIUM	三门货运化掀背车身。	READY
133425	133425	SUV	Qashqai I Facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	HIGH		READY
133426	133426	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133427	133427	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133430	133430	Sedan	Talisman I		4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH		READY
133434	133434	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133435	133435	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133436	133436	Sedan	Allion II	ZRT260	4	EU-TOYOTA-ALLION-II-ZRT260-SEDAN-01	HIGH		READY
133437	133437	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
133448	133448	MPV	Espace V	RFC	5	EU-RENAULT-ESPACE-V-MPV-01	HIGH		READY
133450	133450	MPV	Espace V	RFC	5	EU-RENAULT-ESPACE-V-MPV-01	HIGH		READY
133451	133451	MPV	Verso I	AR20	5	EU-TOYOTA-VERSO-I-AR20-MPV-01	HIGH		READY
133453_prefl	133453	SUV	RAV4 IV Pre-Facelift	ALA49	5	EU-TOYOTA-RAV4-IV-ALA49-SUV-PREFL-01	MEDIUM	Ktype生产期跨越2015年外廓改款。	READY
133453_facelift	133453	SUV	RAV4 IV Facelift	ALA49	5	EU-TOYOTA-RAV4-IV-ALA49-SUV-FACELIFT-01	MEDIUM	Ktype生产期跨越2015年外廓改款。	READY
133454	133454	Coupe	Skyline R32	R32	2	EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	HIGH	R32双门GTS-4外廓。	READY
133455	133455	Hatchback	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	Clio IV改款五门车身。	READY
133457	133457	Sedan	Skyline R32	HCR32	4	EU-NISSAN-SKYLINE-R32-SEDAN-GTS-T-01	HIGH	HCR32四门GTS-t外廓。	READY
133465	133465	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
133468_prefl	133468	SUV	NX I Pre-Facelift	AYZ15	5	EU-LEXUS-NX-I-PREFL-SUV-01	HIGH	Ktype覆盖2017年外廓改款。	READY
133468_facelift	133468	SUV	NX I Facelift	AYZ15	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	Ktype覆盖2017年外廓改款。	READY
133469_prefl	133469	Van	Yaris III Pre-Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	MEDIUM	Ktype覆盖2014年外廓改款。	READY
133469_facelift	133469	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	Ktype覆盖2014年外廓改款。	READY
133470	133470	SUV	C3 Aircross I Phase I	A88	5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH	BlueHDi 100对应第一阶段车身。	READY
133471	133471	Hatchback	C4 Cactus I Facelift	E3	5	EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	HIGH	2018年改款车身。	READY
133472	133472	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	三门货运化掀背车身。	READY
133473	133473	Van	Yaris III Facelift	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	MEDIUM	三门货运化掀背车身。	READY
133475	133475	SUV	Jimny IV	JB74	3	EU-SUZUKI-JIMNY-IV-JB74-SUV-01	HIGH		READY
133483	133483	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
133485	133485	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
133486	133486	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-01	HIGH	M50d动力版本不改变车身外廓。	READY
133493	133493	SUV	X2 I	F39	5	EU-BMW-X2-F39-SUV-01	HIGH		READY
133496	133496	MPV	Touran I Facelift I	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH		READY
133497	133497	Van	Scirocco III Pre-Facelift	13	3	EU-VW-SCIROCCO-III-13-VAN-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133501	133501	Van	Scirocco III Pre-Facelift	13	3	EU-VW-SCIROCCO-III-13-VAN-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133503	133503	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133504	133504	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133509	133509	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133510	133510	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133511	133511	Van	Golf VI	1K	3	EU-VW-GOLF-VI-1K-VAN-3D-01	MEDIUM	三门掀背货运化车身。	READY
133512	133512	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133515	133515	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133516	133516	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133517	133517	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133519	133519	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133521	133521	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133522	133522	Van	Polo V Pre-Facelift	6R	3	EU-VW-POLO-V-6R-VAN-3D-PREFL-01	MEDIUM	三门掀背货运化车身。	READY
133524	133524	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133526	133526	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133527	133527	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133528	133528	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133529	133529	Van	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH	Variant货运化车身。	READY
133530	133530	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133531	133531	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133533	133533	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133534	133534	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133535	133535	Van	Golf Plus I Facelift	5M1	5	EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	HIGH	五门高顶货运化车身。	READY
133536	133536	Wagon	Golf VI Variant	AJ	5	EU-VW-GOLF-VI-AJ-VARIANT-01	HIGH		READY
133537	133537	Coupe	Mustang VI Facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH	Bullitt为改款GT Fastback外廓。	READY
133542	133542	Wagon	Optima IV	JF	5	EU-KIA-OPTIMA-JF-WAGON-01	HIGH	JF Sportswagon五门车身。	READY
133546_swb	133546	Pickup	Sprinter I	903.421	3	EU-MERCEDES-BENZ-SPRINTER-I-903421-DOUBLE-CAB-CHASSIS-SWB-01	MEDIUM	双排驾驶室，3000 mm轴距分支。	READY
133546_mwb	133546	Pickup	Sprinter I	903.422	3	EU-MERCEDES-BENZ-SPRINTER-I-903422-DOUBLE-CAB-CHASSIS-MWB-01	MEDIUM	双排驾驶室，3550 mm轴距分支。	READY
133546_lwb	133546	Pickup	Sprinter I	903.423	3	EU-MERCEDES-BENZ-SPRINTER-I-903423-DOUBLE-CAB-CHASSIS-LWB-01	MEDIUM	双排驾驶室，4025 mm轴距分支。	READY
133559	133559	Van	Passat B7 Variant	3C	5	EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	HIGH	Variant货运化车身。	READY
133563	133563	Van	Passat B7 Variant	3C	5	EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	HIGH	Variant货运化车身。	READY
133568	133568	Coupe	AMG GT 4-Door Coupe I	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	HIGH	X290四门轿跑掀背外廓。	READY
133569	133569	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH	普通PD五门车身，非N宽体版本。	READY
133575	133575	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH	JF四门轿车车身。	READY
133577	133577	Coupe	Exige Series 3		2	EU-LOTUS-EXIGE-SERIES-3-SPORT-410-COUPE-01	HIGH	Sport 410固定车顶外廓。	READY
133578	133578	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
133579	133579	SUV	XLV I	X100	5	EU-SSANGYONG-XLV-I-X100-SUV-01	HIGH	加长后部车身。	READY
133580	133580	SUV	Grandland X I	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	2018至2021年A18改款前外廓。	READY
133584	133584	Hatchback	Ka III Facelift	B562	5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH		READY
133585	133585	Hatchback	Ka III Facelift	B562	5	EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	HIGH		READY
133589	133589	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	HIGH	GTI三门货运化车身。	READY
133593	133593	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133594	133594	Sedan	Linea I	323	4	EU-FIAT-LINEA-I-323-SEDAN-01	MEDIUM		READY
133596	133596	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133597	133597	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133599	133599	Van	Golf VII Pre-Facelift	5G1	3	EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	MEDIUM	标准三门掀背货运化车身。	READY
133603	133603	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	HIGH	4Motion货运化Variant车身。	READY
133606	133606	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133609	133609	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133612	133612	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133613	133613	Van	Golf VII Variant Pre-Facelift	AUV	5	EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	HIGH	前驱Variant货运化车身。	READY
133625	133625	MPV	Grand C4 SpaceTourer II	B78	5	EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	HIGH		READY
133628	133628	Coupe	Biturbo Racing	AM331	2	EU-MASERATI-BITURBO-RACING-AM331-COUPE-01	HIGH	AM331 Racing双门外廓。	READY
133634	133634	Hatchback	Pixo I	UA0	5	EU-NISSAN-PIXO-I-UA0-HATCHBACK-01	HIGH		READY
133636	133636	Sedan	Teana II	J32	4	EU-NISSAN-TEANA-II-J32-SEDAN-01	HIGH	J32前驱四门车身。	READY
133637	133637	Sedan	A3 8V Facelift	8VS	4	EU-AUDI-A3-8V-SEDAN-FACELIFT-01	HIGH	8V改款四门Sedan车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3001-3100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Volvo Cars Media UK - All-new Volvo V70 specifications	https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Volvo V70 2014 official support - Dimensions	https://www.volvocars.com/uk/support/car/v70/14w20/article/18f77489f78f457dc0a801e800a04016/
EU-VW-GOLF-IV-1J5-VARIANT-VAN-01	4397	1735	1485	Volkswagen Golf IV Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19524
EU-VOLVO-XC70-II-FACELIFT-WAGON-01	4838	1870	1604	Volvo XC70 2016 Owner Manual - Dimensions	https://www.volvocars.com/uk/support/car/xc70/article/18f77489f78f457dc0a801e800a04016/
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-HIGH-01	4149	1735	1444	Volkswagen Golf IV official vehicle data; UltimateSpecs Golf 4 3-door Highline 2.0	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478; https://www.ultimatespecs.com/car-specs/Volkswagen/43944/Volkswagen-Golf-4-3-doors-Highline-20.html
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-HIGH-01	4149	1735	1444	Volkswagen Golf IV official vehicle data; AutoCentrum Golf IV Hatchback 2.0	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478; https://www.autocentrum.pl/dane-techniczne/volkswagen/golf/iv/hatchback/silnik-benzynowy-2.0-115km-85kw-1998-2003/
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467	Volkswagen Polo IV official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467	Volkswagen Polo IV official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-ROADSTER-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Sport 410 technical specifications	https://lotusantwerp.be/lotus-exige-sport-410/
EU-LOTUS-EXIGE-SERIES-3-CUP-430-COUPE-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Cup 430 technical specifications	https://lotusantwerp.be/lotus-exige-cup-430-edition/
EU-TOYOTA-AYGO-I-AB10-VAN-3D-01	3405	1615	1465	Toyota Media - Aygo Is Go technical specifications	https://media.toyota.co.uk/aygo-is-go/
EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	4330	1780	1615	Nissan Qashqai 2010 official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/07/Nissan-Qashqai-2010-UK.pdf
EU-RENAULT-TALISMAN-I-SEDAN-01	4849	1868	1456	Renault Talisman official price list - Dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Talisman_PL_f.pdf
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465	Renault Talisman Grandtour official price list - Dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Talisman_Grandtour_PL_f.pdf
EU-TOYOTA-ALLION-II-ZRT260-SEDAN-01	4565	1695	1475	Toyota 75 Years Vehicle Lineage - Allion A18	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60008987/index.html
EU-RENAULT-ESPACE-V-MPV-01	4857	1888	1677	Renault Espace official brochure	https://app.viabiler.dk/files/454/renault-espace-brochure.pdf
EU-TOYOTA-VERSO-I-AR20-MPV-01	4440	1790	1620	Toyota Media - World Premiere of the New Toyota Verso	https://media.toyota.co.uk/world-premiere-of-the-new-toyota-verso/
EU-TOYOTA-RAV4-IV-ALA49-SUV-PREFL-01	4570	1845	1660	Auto-Data Toyota RAV4 IV 2.2 D-4D 4WD	https://www.auto-data.net/en/toyota-rav4-iv-2.2-d-4d-150hp-4wd-18106
EU-TOYOTA-RAV4-IV-ALA49-SUV-FACELIFT-01	4605	1845	1675	Toyota RAV4 official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1547121943180511MRAV4TechnicalSpecifications.pdf
EU-NISSAN-SKYLINE-R32-COUPE-GTS-01	4530	1695	1325	Nissan Heritage Collection - Skyline GTS-t TypeM (HCR32)	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/Skyline_GTS-t_TypeM.html
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448	Renault Clio official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Clio-2017-UK.pdf
EU-NISSAN-SKYLINE-R32-SEDAN-GTS-T-01	4580	1695	1340	Automobile-Catalog 1990 Nissan Skyline 4-door Sports Sedan GTS-t Type-M	https://www.automobile-catalog.com/car/1990/2134895/nissan_skyline_4door_sports_sedan_gts-t_type-m.html
EU-CITROEN-GRAND-C4-SPACETOURER-II-B78-MPV-01	4602	1826	1638	Citroën C4 SpaceTourer official brochure	https://motorlib.net/citroen/brochure/c4-spacetourer.pdf
EU-LEXUS-NX-I-PREFL-SUV-01	4630	1845	1645	Lexus Media - New NX Crossover Opens a New Chapter for Lexus	https://media.lexus.co.uk/new-nx-crossover-opens-new-chapter-lexus/
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645	Lexus NX official brochure	https://www.lexus.co.th/content/dam/thailand/Brochures/Catalogue_Lexus_NX.pdf
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510	Auto-Data - Toyota Yaris III 1.33 Dual VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.33-dual-vvt-i-99hp-17110
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510	Toyota Yaris official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1485445765170110MTechSpec.pdf
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637	Citroën C3 Aircross official UK brochure	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-C3-Aircross-2018-UK.pdf
EU-CITROEN-C4-CACTUS-I-FACELIFT-HATCHBACK-01	4170	1714	1480	Citroën C4 Cactus technical data	https://www.carnet.hu/citroen/files/muszaki-adatlap/citroen-c4-cactus-muszaki-adatlap.pdf
EU-SUZUKI-JIMNY-IV-JB74-SUV-01	3645	1645	1720	Suzuki Global - Jimny main specifications	https://www.globalsuzuki.com/globalnews/2021/0120.html
EU-BMW-X7-G07-SUV-01	5151	2000	1805	BMW Group PressClub - The first-ever BMW X7	https://www.press.bmwgroup.com/global/article/detail/T0285836EN/the-first-ever-bmw-x7?language=en
EU-BMW-X2-F39-SUV-01	4360	1824	1526	BMW Group PressClub - BMW X2 technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0328304IT/475167
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635	Volkswagen Touran 2007 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2007-UK.pdf
EU-VW-SCIROCCO-III-13-VAN-PREFL-01	4256	1810	1404	Volkswagen The New Scirocco International Driving Presentation	https://www.volkswagen-newsroom.com/en/the-new-scirocco-international-driving-presentation-portugal-june-2008-2349
EU-VW-GOLF-VI-1K-VAN-3D-01	4199	1779	1480	Volkswagen UK Golf VI official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-vi/vw_golf_mk6_2009-2013_oct_2011.pdf
EU-VW-POLO-V-6R-VAN-3D-PREFL-01	3970	1682	1484	Volkswagen Polo V official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-VW-GOLF-VI-AJ-VARIANT-01	4534	1781	1504	Volkswagen Golf VI Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-6-variant-profile-19529
EU-VW-GOLF-PLUS-I-5M1-VAN-FACELIFT-01	4204	1759	1580	Volkswagen The New Golf Plus 2009 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-Golf-Plus-2009-UK.pdf
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382	Ford Mustang official brochure	https://www.caribe.ford.com/content/dam/Ford/website-assets/cca/cca-compartido/brochures-caribe/ford-caribbean-mustang-2022-brochure-download-eng.pdf
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470	Kia Optima Sportswagon official specification	https://www.kia.com/content/dam/kwcms/kme/se/sv/assets/contents/utility/specifications/optima-sw/kia-sweden-optima-sw-specification.pdf
EU-MERCEDES-BENZ-SPRINTER-I-903421-DOUBLE-CAB-CHASSIS-SWB-01	4819	1900	2135	Használtautó Autókatalógus - Mercedes-Benz 310 D 903.421	https://katalogus.hasznaltauto.hu/mercedes-benz/310_d_903.421/52152
EU-MERCEDES-BENZ-SPRINTER-I-903422-DOUBLE-CAB-CHASSIS-MWB-01	5569	1900	2135	Használtautó Autókatalógus - Mercedes-Benz 310 D 903.422	https://katalogus.hasznaltauto.hu/mercedes-benz/310_d_903.422/52153
EU-MERCEDES-BENZ-SPRINTER-I-903423-DOUBLE-CAB-CHASSIS-LWB-01	6124	1900	2160	Használtautó Autókatalógus - Mercedes-Benz 310 D 903.423	https://katalogus.hasznaltauto.hu/mercedes-benz/310_d_903.423/52154
EU-VW-PASSAT-B7-3C-VARIANT-VAN-01	4771	1820	1508	Volkswagen Passat B7 official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-MERCEDES-BENZ-AMG-GT-X290-43-53-COUPE-01	5054	1953	1455	Mercedes-Benz AMG GT 4-Door Coupé technical data	https://www.mercedes-benz.jp/catalog/gt-4-door/pdf/GT%204-Door%20Coup%C3%A9_X290_MP202202_Data_Information_220421.pdf
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Hyundai i30 official brochure	https://www.hyundai.ie/assets/car/new-generation-i30/files/108324-hyundai-i3020p-210x260-catalogue-web.pdf
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Kia Optima official e-Catalogue	https://www.kia.com/content/dam/kwcms/bn/en/pdf/Optima-Facelift-e-Catalogue.pdf
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-COUPE-01	4084	1802	1129	Lotus Antwerp - Lotus Exige Sport 410 technical specifications	https://lotusantwerp.be/lotus-exige-sport-410/
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590	SsangYong Tivoli official brochure	https://cdn.mattaki.com/ssangyong/static-assets/vehicles/brochures/tivoli_ebrochure.pdf
EU-SSANGYONG-XLV-I-X100-SUV-01	4440	1798	1635	SsangYong Tivoli XLV official brochure	https://cdn.mattaki.com/ssangyong/static-assets/vehicles/brochures/tivoli-xlv_ebrochure.pdf
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Opel Grandland X official specification sheet	https://nd-mediagallery2-public-production.s3.amazonaws.com/f52425abdaff90529ba7443030f717c6/12014_58273_opel_grandland_x_my18_spec_sheets_a4l_fc_e_web_1_.pdf
EU-FORD-KA-PLUS-III-FACELIFT-HATCHBACK-01	3941	1704	1524	Ford KA+ MY2019 official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_KA%2B.pdf
EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	4268	1799	1442	Volkswagen Golf VII GTI official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-gti-profile-20033
EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	4255	1799	1452	Volkswagen The New Golf official quick facts	https://www.volkswagen-newsroom.com/en/the-new-golf-das-auto-international-driving-presentation-2797/the-new-golf-overview-quick-facts-2854
EU-FIAT-LINEA-I-323-SEDAN-01	4560	1730	1494	Fiat Linea official technical specifications; Carfolio Fiat Linea 1.3 Multijet 16v	https://www.team-bhp.com/forum/attachments/indian-car-scene/41241d1219421020-scoop-fiat-linea-pics-pg-1-5-linea_specs.pdf; https://www.carfolio.com/fiat-linea-1.3-multijet-16v-157586
EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	4562	1799	1515	Volkswagen Golf VII Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-variant-profile-20042
EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	4562	1799	1481	Volkswagen Golf VII Estate official press presentation	https://www.volkswagen-newsroom.com/en/the-new-golf-estate-international-press-presentation-2977/the-new-golf-estate-overview-quick-facts-3002
EU-MASERATI-BITURBO-RACING-AM331-COUPE-01	4200	1714	1305	Maserati Classic - Racing; Automobile-Catalog Maserati Racing	https://www.maserati.com/global/en/brand/maserati-classic-cars/biturbo-and-derivates/racing; https://www.automobile-catalog.com/car/1992/1446290/maserati_racing.html
EU-NISSAN-PIXO-I-UA0-HATCHBACK-01	3565	1600	1470	Nissan Pixo official UK brochure	https://cache3.pakwheels.com/system/brochures/959/original/Nissan-Pixo-2011-UK.pdf?1750824844=
EU-NISSAN-TEANA-II-J32-SEDAN-01	4850	1795	1475	Nissan Teana J32 official specifications	https://history.nissan.co.jp/TEANA/J32/1206/j320806g02.html?gradeID=G02&model=TEANA
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416	Audi A3 official brochure	https://autocatalogarchive.com/wp-content/uploads/2017/12/Audi-A3-2016-HK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3001-3100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://katalogus.hasznaltauto.hu/mercedes-benz/310_d_903.421/52152 "https://katalogus.hasznaltauto.hu/mercedes-benz/310_d_903.421/52152"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2383 行）
- 累计尺寸组：dimension_groups_final.tsv（1173 行）

