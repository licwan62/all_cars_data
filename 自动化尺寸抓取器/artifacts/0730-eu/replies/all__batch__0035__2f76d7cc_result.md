# 任务：all 第 3401-3500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0035__2f76d7cc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3401-3500 行

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
all 第 3401-3500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-7-F01-SEDAN-FACELIFT-01	5079	1902	1471
EU-BMW-7-F01-SEDAN-PREFL-01	5072	1902	1479
EU-BMW-7-G11-SEDAN-01	5098	1902	1478
EU-BMW-7-G12-SEDAN-LWB-01	5238	1902	1485
EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	4468	1839	1501
EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	4472	1840	1501
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470
EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	4775	1815	1470
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645
EU-LEXUS-NX-I-PREFL-SUV-01	4630	1845	1645
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	4275	1765	1535
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-NISSAN-LEAF-ZE1-HATCHBACK-01	4490	1788	1530
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880
EU-PEUGEOT-407-I-SEDAN-01	4676	1811	1455
EU-RENAULT-CAPTUR-I-SUV-01	4122	1778	1566
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457
EU-RENAULT-TALISMAN-I-SEDAN-01	4849	1868	1456
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465
EU-SUBARU-FORESTER-III-SH-SUV-PREFL-01	4560	1780	1675
EU-SUBARU-FORESTER-IV-SJ-SUV-01	4595	1795	1735
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Subaru	Forester	2.0 E-boxer Hybrid AWD	SUV	Allrad	Benzin/Elektro	110	150	Apr 2018	-	2024-03-01	134484
Ford	Focus ii	1.6 Ti-vct	Kasten/Kombi	Frontantrieb	Benzin	85	116	Sep 2005	Jul 2011	2024-03-01	134485
Ford	Focus ii	1.6	Kasten/Kombi	Frontantrieb	Benzin	74	101	Sep 2005	Jul 2011	2024-03-01	134486
Ford	Focus ii	1.6 Tdci	Kasten/Kombi	Frontantrieb	Diesel	66	90	Sep 2005	Jul 2011	2024-03-01	134487
Ford	Focus ii	1.4	Kasten/Kombi	Frontantrieb	Benzin	59	80	Sep 2005	Jul 2011	2024-03-01	134488
Ford	Fiesta vi van	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	71	97	Oct 2008	Dec 2012	2024-03-01	134492
Ford	Fiesta vi van	1.25	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Aug 2008	Dec 2012	2024-03-01	134493
Ford	Focus iii	1.6 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	70	95	Jan 2011	Dec 2017	2024-03-01	134495
Mercedes-benz	Gle	GLE 350 D 4-matic	SUV	Allrad	Diesel	200	272	Dec 2018	May 2021	2024-03-01	134500
Mercedes-benz	Gle	GLE 400 D 4-matic	SUV	Allrad	Diesel	243	330	Dec 2018	Mar 2023	2024-03-01	134501
Ford	Mondeo iv van	2	Kasten/Kombi	Frontantrieb	Benzin	107	145	Mar 2007	Sep 2014	2024-03-01	134502
Ford	Mondeo iv van	2.0 Tdci	Kasten/Kombi	Frontantrieb	Diesel	120	163	Mar 2010	Sep 2014	2024-03-01	134505
Ford	Mondeo iv van	1.6 Ecoboost	Kasten/Kombi	Frontantrieb	Benzin	118	160	Nov 2010	Sep 2014	2024-03-01	134506
Ford	Mondeo iv van	1.6 Tdci	Kasten/Kombi	Frontantrieb	Diesel	85	116	Mar 2013	Sep 2014	2024-03-01	134507
VW	Multivan t6	2.0 TDI 4motion	Bus	Allrad	Diesel	146	199	Aug 2018	Aug 2024	2025-06-01	134534
Nissan	Micra v	1.0 Ig-t 100	Schrägheck	Frontantrieb	Benzin	74	101	Dec 2018	-	2024-03-01	134538
Renault	19 ii	1.8	Cabriolet	Frontantrieb	Benzin	69	94	Apr 1992	Jan 1996	2024-03-01	134554
VW	Transporter t6 / caravelle	2.0 TDI 4motion	Bus	Allrad	Diesel	146	199	Aug 2018	Aug 2024	2025-02-03	134555
Lexus	Nx	300h AWD	SUV	Allrad	Benzin/Elektro	147	200	Nov 2018	-	2024-03-01	134558
Lexus	Ls	500h	Stufenheck	Heckantrieb	Benzin/Elektro	264	359	Nov 2017	-	2024-03-01	134559
Peugeot	407	2.0 Flex	Kombi	Frontantrieb	Benzin/Ethanol	103	140	Oct 2005	Feb 2011	2024-03-01	134562
Hyundai	I40 i cw	2.0 Cvvt	Kombi	Frontantrieb	Benzin	121	165	Jun 2012	May 2019	2024-05-01	134583
Renault	Megane i hatchback van	1.9 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	59	80	Oct 2000	Jul 2003	2024-03-01	134596
KIA	Proceed	1.0 T-gdi	Kombi	Frontantrieb	Benzin	88	120	Oct 2018	-	2024-03-01	134605
KIA	Proceed	1.4 T-gdi	Kombi	Frontantrieb	Benzin	103	140	Oct 2018	Dec 2020	2024-08-01	134606
KIA	Proceed	1.6 Crdi 136	Kombi	Frontantrieb	Diesel	100	136	Oct 2018	-	2024-03-01	134607
KIA	Proceed	1.6 T-gdi GT	Kombi	Frontantrieb	Benzin	150	204	Oct 2018	-	2024-03-01	134608
KIA	Ceed	1.6 T-gdi GT	Schrägheck	Frontantrieb	Benzin	150	204	Oct 2018	-	2024-03-01	134610
KIA	Ceed	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	71	97	Dec 2018	Dec 2020	2024-08-01	134611
KIA	Ceed	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	71	97	Dec 2018	Dec 2020	2024-08-01	134612
Opel	Combo	1.6 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jun 2018	Apr 2021	2025-02-03	134619
Opel	Combo	1.6 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	73	99	Jun 2018	Apr 2020	2025-02-03	134620
Vauxhall	Grandland	1.5 Turbo D	SUV	Frontantrieb	Diesel	96	131	Apr 2018	-	2025-02-03	134621
Lada	Vesta	1.6	Stufenheck	Frontantrieb	Benzin	75	102	Nov 2018	-	2024-03-01	134622
Lada	Vesta	1.6	Kombi	Frontantrieb	Benzin	75	102	Nov 2018	-	2024-03-01	134624
Lada	Vesta	Cross 1.6	Kombi	Frontantrieb	Benzin	75	102	Nov 2018	-	2024-03-01	134625
Renault	Captur i	1.3 TCE 130	Schrägheck	Frontantrieb	Benzin	96	131	Mar 2018	Dec 2019	2025-12-01	134658
Chevrolet	Lacetti	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	69	94	Jan 2005	Dec 2012	2024-03-01	134690
Renault	Clio iii grandtour	1.2 16V Hi-flex	Kombi	Frontantrieb	Benzin/Ethanol	58	79	Nov 2007	Dec 2012	2026-05-01	134697
Renault	Clio iv	1.2 16V	Kasten/Schrägheck	Frontantrieb	Benzin	54	73	Jan 2014	Aug 2021	2026-05-01	134706
Renault	Megane iii hatchback van	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	81	110	Feb 2009	Aug 2015	2024-03-01	134712
Hyundai	I30	2.0 N	Schrägheck	Frontantrieb	Benzin	184	250	Nov 2017	-	2025-06-01	134726
Toyota	Rav 4 v	2.5 Hybrid	SUV	Frontantrieb	Benzin/Elektro	160	218	Dec 2018	-	2024-03-01	134729
Hyundai	I30	2.0 N	Schrägheck	Frontantrieb	Benzin	202	275	Nov 2017	Sep 2020	2025-06-01	134730
Renault	Megane ii hatchback van	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	78	106	May 2005	Feb 2008	2024-03-01	134731
Renault	Megane ii hatchback van	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	74	101	Aug 2003	Feb 2008	2024-03-01	134732
Toyota	Rav 4 v	2	SUV	Frontantrieb	Benzin	129	175	Dec 2018	-	2024-03-01	134735
Toyota	Rav 4 v	2.0 AWD	SUV	Allrad	Benzin	129	175	Dec 2018	-	2024-03-01	134736
VW	Caddy alltrack iv	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2018	Sep 2020	2025-06-01	134739
VW	Tiguan	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Nov 2018	Apr 2024	2025-06-01	134740
VW	Jetta vii	1.4 TSI	Stufenheck	Frontantrieb	Benzin	110	150	Dec 2017	-	2024-03-01	134743
VW	Caddy alltrack iv	1.0 TSI	Großraumlimousine	Frontantrieb	Benzin	62	84	Nov 2018	Jul 2019	2025-06-01	134745
Mazda	3	2.0 Skyactiv-g M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	90	122	Nov 2018	-	2024-03-01	134747
Mazda	3	1.8 Skyactiv-d	Schrägheck	Frontantrieb	Diesel	85	116	Jan 2019	-	2024-03-01	134748
Mazda	3	2.0 Skyactiv-g M Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	90	122	Nov 2018	-	2024-03-01	134749
Mazda	3	1.8 Skyactiv-d	Stufenheck	Frontantrieb	Diesel	85	116	Jan 2019	-	2024-03-01	134750
Volvo	Xc60 ii	D4	SUV	Frontantrieb	Diesel	120	163	Dec 2018	Dec 2021	2024-05-01	134755
Volvo	V90 ii cross country	D4 AWD	Kombi	Allrad	Diesel	120	163	Sep 2018	-	2024-03-01	134756
Volvo	V90 ii	D4	Kombi	Frontantrieb	Diesel	120	163	Sep 2018	Dec 2021	2024-05-01	134757
Volvo	S90 ii	D4	Stufenheck	Frontantrieb	Diesel	120	163	Sep 2018	Dec 2021	2024-05-01	134773
Hyundai	I40 i cw	1.6 Crdi	Kombi	Frontantrieb	Diesel	85	116	Jul 2018	May 2019	2024-03-01	134825
Hyundai	I40 i	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	85	116	Jul 2018	May 2019	2024-03-01	134826
Hyundai	I40 i	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	100	136	Jul 2018	May 2019	2024-03-01	134827
Levc	Tx	Ecity	Schrägheck	Heckantrieb	Benzin/Elektro	110	150	Dec 2017	-	2024-03-01	134832
Audi	Q2	40 Tfsi Quattro	SUV	Allrad	Benzin	140	190	Sep 2018	-	2026-07-01	134844
Audi	Tt	40 Tfsi	Coupe	Frontantrieb	Benzin	145	197	Jul 2018	-	2024-03-01	134873
Audi	Tt	45 Tfsi	Coupe	Frontantrieb	Benzin	180	245	Jul 2018	-	2024-03-01	134878
Audi	Tt	45 Tfsi Quattro	Coupe	Allrad	Benzin	180	245	Jul 2018	-	2024-03-01	134886
Audi	Tt	2.0 TTS TSI Quattro	Coupe	Allrad	Benzin	225	306	Aug 2018	-	2025-06-01	134888
Audi	Tt	40 Tfsi	Cabriolet	Frontantrieb	Benzin	145	197	Jul 2018	-	2024-03-01	134890
Audi	Tt	45 Tfsi	Cabriolet	Frontantrieb	Benzin	180	245	Jul 2018	-	2024-03-01	134891
Audi	Tt	45 Tfsi Quattro	Cabriolet	Allrad	Benzin	180	245	Jul 2018	-	2024-03-01	134892
Audi	Tt	2.0 TTS Tfsi Quattro	Cabriolet	Allrad	Benzin	225	306	Aug 2018	-	2025-06-01	134893
VW	Amarok	3.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	190	258	May 2018	May 2022	2024-03-01	134896
Audi	A7 sportback	45 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	-	2024-03-01	134986
Audi	A7 sportback	45 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	180	245	Jul 2018	-	2024-03-01	134988
Volvo	S90 ii	T8 Hybrid Polestar AWD	Stufenheck	Allrad	Benzin/Elektro	233	317	Jan 2019	-	2024-03-01	134990
Volvo	Xc60 ii	T8 Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	298	405	Jan 2019	Dec 2022	2024-05-01	134992
Volvo	Xc40	D4 Polestar AWD	SUV	Allrad	Diesel	147	200	Jan 2019	Sep 2021	2024-03-01	134993
Volvo	Xc60 ii	D4 Polestar AWD	SUV	Allrad	Diesel	147	200	Jan 2019	Dec 2021	2024-05-01	134994
BMW	7	730 I, LI	Stufenheck	Heckantrieb	Benzin	195	265	Mar 2019	Jun 2022	2024-03-01	135018
Toyota	Corolla	1.2	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2019	-	2024-03-01	135019
BMW	7	740 I, LI	Stufenheck	Heckantrieb	Benzin	250	340	Mar 2019	Jun 2022	2024-03-01	135021
Subaru	Forester	2.0 AWD	SUV	Allrad	Benzin	115	156	Apr 2018	-	2024-03-01	135022
VW	Caddy iv	1.0 TSI	Großraumlimousine	Frontantrieb	Benzin	62	84	Nov 2018	Jul 2019	2024-03-01	135023
Nissan	Leaf	Electric	Schrägheck	Frontantrieb	Elektro	160	218	Jan 2019	-	2024-03-01	135024
BMW	7	745 E, LE Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	290	394	Mar 2019	Jun 2022	2024-03-01	135026
BMW	7	745 LE Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	290	394	Mar 2019	Jun 2022	2024-03-01	135028
BMW	7	740 LI Xdrive	Stufenheck	Allrad	Benzin	250	340	Mar 2019	Jun 2022	2024-03-01	135029
BMW	7	750 I, LI Xdrive	Stufenheck	Allrad	Benzin	390	530	Mar 2019	Jun 2022	2024-03-01	135033
BMW	7	M 760 LI Xdrive	Stufenheck	Allrad	Benzin	430	585	Mar 2019	Jun 2022	2024-03-01	135035
Mazda	Cx-3	2.0 Skyactiv-g	SUV	Frontantrieb	Benzin	110	150	May 2018	-	2024-03-01	135052
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	135	184	Mar 2019	-	2024-03-01	135053
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	110	150	Mar 2019	Mar 2020	2024-03-01	135058
Renault	Megane iv	1.8 RS 300	Schrägheck	Frontantrieb	Benzin	221	301	Sep 2018	-	2026-01-01	135059
Renault	Talisman	1.3 TCE 160	Stufenheck	Frontantrieb	Benzin	117	160	Jan 2019	Mar 2022	2024-03-01	135065
Renault	Talisman	1.3 TCE 160	Kombi	Frontantrieb	Benzin	117	160	Jan 2019	Mar 2022	2024-03-01	135066
Renault	Talisman	2.0 Blue DCI 160	Stufenheck	Frontantrieb	Diesel	118	160	Jan 2019	Mar 2022	2024-03-01	135068
Renault	Talisman	2.0 Blue DCI 160	Kombi	Frontantrieb	Diesel	118	160	Jan 2019	Mar 2022	2024-03-01	135069
Renault	Talisman	2.0 Blue DCI 200	Stufenheck	Frontantrieb	Diesel	147	200	Jan 2019	Mar 2022	2024-03-01	135072


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类完成首轮映射，闭合 Fiesta VI Van、Micra K14、ProCeed CD、Ceed GT、Grandland X 等新尺寸组。([汽车数据][1])
* 已闭合 RAV4 XA50、Jetta A7、Mazda 3 BP 两种车身及 Corolla E210 Hatchback 尺寸组。([汽车数据][2])
* 已闭合 Audi A7 C8 Sportback、BMW 7 Series G11/G12 LCI 两种轴距尺寸组；其余已确认车型直接复用跨批次缓存，不重复输出来源。([汽车数据][3])
* Focus II 跨改款 Ktype、Clio IV Van 跨 Phase Ktype，以及同时覆盖 BMW 7 Series 标准轴距和长轴距的 Ktype 已按物理外廓拆分。

## 当前批次进度

* 输入 Ktype 覆盖：100 / 100
* 当前映射行：111
* READY 映射：83
* PENDING 映射：28
* 已确认并引用尺寸组：46
* 本轮首次创建尺寸组：13
* 复用已有尺寸组：33
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134484	134484	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK 五门 SUV 外廓。	READY
134485_prefl	134485	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134485_facelift	134485	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134486_prefl	134486	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134486_facelift	134486	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134487_prefl	134487	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134487_facelift	134487	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134488_prefl	134488	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134488_facelift	134488	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134492	134492	Van	Fiesta VI	JA8	3	EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	HIGH	三门厢式掀背外廓。	READY
134493	134493	Van	Fiesta VI	JA8	3	EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	HIGH	三门厢式掀背外廓。	READY
134495_prefl	134495	Van	Focus III	DYB	5		MEDIUM	改款前厢式掀背尺寸组尚未闭合。	PENDING: 改款前厢式掀背尺寸组尚未闭合。
134495_facelift	134495	Van	Focus III	DYB	5	EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	改款后厢式版复用五门掀背外廓。	READY
134500	134500	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 五门 SUV 外廓。	READY
134501	134501	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 五门 SUV 外廓。	READY
134502	134502	Van	Mondeo IV	BA7	5		LOW	生产区间跨改款，厢式旅行车分支和尺寸组尚未闭合。	PENDING: 生产区间跨改款，厢式旅行车分支和尺寸组尚未闭合。
134505	134505	Van	Mondeo IV	BA7	5		LOW	厢式旅行车改款边界及尺寸组尚未闭合。	PENDING: 厢式旅行车改款边界及尺寸组尚未闭合。
134506	134506	Van	Mondeo IV	BA7	5		LOW	厢式旅行车改款边界及尺寸组尚未闭合。	PENDING: 厢式旅行车改款边界及尺寸组尚未闭合。
134507	134507	Van	Mondeo IV	BA7	5		LOW	厢式旅行车改款边界及尺寸组尚未闭合。	PENDING: 厢式旅行车改款边界及尺寸组尚未闭合。
134534	134534	MPV	Multivan T6	7H	5		LOW	T6/T6.1 与轴距分支尚未闭合。	PENDING: T6/T6.1 与轴距分支尚未闭合。
134538	134538	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH	K14 五门掀背外廓。	READY
134554	134554	Convertible	Renault 19 II	D53	2		LOW	敞篷车尺寸组与直接来源尚未闭合。	PENDING: 敞篷车尺寸组与直接来源尚未闭合。
134555	134555	MPV	Transporter T6 / Caravelle	7H	5		LOW	T6/T6.1、轴距及车顶分支尚未闭合。	PENDING: T6/T6.1、轴距及车顶分支尚未闭合。
134558	134558	SUV	NX I facelift	AZ10	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	改款后 NX I 五门 SUV 外廓。	READY
134559	134559	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50 四门轿车外廓。	READY
134562	134562	Wagon	407 I	6E	5		LOW	旅行车尺寸组尚未闭合。	PENDING: 旅行车尺寸组尚未闭合。
134583_prefl	134583	Wagon	i40 I	VF	5		MEDIUM	改款前旅行车尺寸组尚未闭合。	PENDING: 改款前旅行车尺寸组尚未闭合。
134583_facelift	134583	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
134596	134596	Van	Megane I facelift	BA0	5		LOW	厢式掀背尺寸组与直接来源尚未闭合。	PENDING: 厢式掀背尺寸组与直接来源尚未闭合。
134605	134605	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134606	134606	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134607	134607	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134608	134608	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134610	134610	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-GT-01	HIGH	GT 专用保险杠与降低车高外廓。	READY
134611	134611	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	标准五门掀背外廓。	READY
134612	134612	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	标准五门旅行车外廓。	READY
134619	134619	MPV	Combo E	K9	5		LOW	M/XL 轴距及厢式/乘用外廓边界尚未闭合。	PENDING: M/XL 轴距及厢式/乘用外廓边界尚未闭合。
134620	134620	MPV	Combo E	K9	5		LOW	M/XL 轴距及厢式/乘用外廓边界尚未闭合。	PENDING: M/XL 轴距及厢式/乘用外廓边界尚未闭合。
134621	134621	SUV	Grandland X	P1	5	EU-VAUXHALL-GRANDLAND-X-SUV-01	HIGH	Grandland X 五门 SUV 外廓。	READY
134622	134622	Sedan	Vesta I	2180	4	EU-LADA-VESTA-I-SEDAN-01	HIGH	Vesta I 四门轿车外廓。	READY
134624	134624	Wagon	Vesta I SW	2181	5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW 五门旅行车外廓。	READY
134625	134625	Wagon	Vesta I SW Cross	2181	5		LOW	Cross 车高与外部套件尺寸组尚未闭合。	PENDING: Cross 车高与外部套件尺寸组尚未闭合。
134658	134658	SUV	Captur I	J87	5	EU-RENAULT-CAPTUR-I-SUV-01	HIGH	Captur I 五门 SUV 外廓。	READY
134690	134690	Hatchback	Lacetti	J200	5		LOW	五门掀背尺寸组尚未闭合。	PENDING: 五门掀背尺寸组尚未闭合。
134697	134697	Wagon	Clio III Grandtour	KR	5		LOW	Grandtour 旅行车尺寸组尚未闭合。	PENDING: Grandtour 旅行车尺寸组尚未闭合。
134706_phase1	134706	Van	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	MEDIUM	Phase I 厢式版复用五门掀背外廓。	READY
134706_phase2	134706	Van	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	MEDIUM	Phase II 厢式版复用五门掀背外廓。	READY
134712	134712	Van	Megane III	B95	5		LOW	生产区间跨多次改款，厢式掀背分支尚未闭合。	PENDING: 生产区间跨多次改款，厢式掀背分支尚未闭合。
134726	134726	Hatchback	i30 III N	PD	5	EU-HYUNDAI-I30-PD-HATCHBACK-N-01	HIGH	N 250 五门掀背外廓。	READY
134729	134729	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134730	134730	Hatchback	i30 III N	PD	5	EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	HIGH	N Performance 五门掀背外廓。	READY
134731	134731	Van	Megane II	B84	5		LOW	改款阶段及厢式掀背尺寸组尚未闭合。	PENDING: 改款阶段及厢式掀背尺寸组尚未闭合。
134732	134732	Van	Megane II	B84	5		LOW	改款阶段及厢式掀背尺寸组尚未闭合。	PENDING: 改款阶段及厢式掀背尺寸组尚未闭合。
134735	134735	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134736	134736	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134739	134739	MPV	Caddy IV Alltrack	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴 Alltrack 外廓。	READY
134740	134740	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-FWD-01	HIGH	前驱标准车高外廓。	READY
134743	134743	Sedan	Jetta VII	A7	4	EU-VW-JETTA-VII-A7-SEDAN-01	HIGH	A7 四门轿车外廓。	READY
134745	134745	MPV	Caddy IV Alltrack	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴 Alltrack 外廓。	READY
134747	134747	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH	BP 五门掀背外廓。	READY
134748	134748	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH	BP 五门掀背外廓。	READY
134749	134749	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	BP 四门轿车外廓。	READY
134750	134750	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	BP 四门轿车外廓。	READY
134755	134755	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60 II 五门 SUV 外廓。	READY
134756	134756	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
134757	134757	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II 五门旅行车外廓。	READY
134773	134773	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
134825	134825	Wagon	i40 I facelift	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
134826	134826	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	四门轿车外廓。	READY
134827	134827	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	四门轿车外廓。	READY
134832	134832	Hatchback	TX		5		LOW	LEVC TX 车身分类与尺寸组尚未闭合。	PENDING: LEVC TX 车身分类与尺寸组尚未闭合。
134844	134844	SUV	Q2	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH	GA 五门 SUV 外廓。	READY
134873	134873	Coupe	TT III facelift	8S	3		LOW	改款后 Coupe 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Coupe 标准外廓尺寸组尚未闭合。
134878	134878	Coupe	TT III facelift	8S	3		LOW	改款后 Coupe 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Coupe 标准外廓尺寸组尚未闭合。
134886	134886	Coupe	TT III facelift	8S	3		LOW	改款后 Coupe 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Coupe 标准外廓尺寸组尚未闭合。
134888	134888	Coupe	TTS III facelift	8S	3		LOW	TTS 专用保险杠外廓尺寸组尚未闭合。	PENDING: TTS 专用保险杠外廓尺寸组尚未闭合。
134890	134890	Convertible	TT Roadster III facelift	8S	2		LOW	改款后 Roadster 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Roadster 标准外廓尺寸组尚未闭合。
134891	134891	Convertible	TT Roadster III facelift	8S	2		LOW	改款后 Roadster 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Roadster 标准外廓尺寸组尚未闭合。
134892	134892	Convertible	TT Roadster III facelift	8S	2		LOW	改款后 Roadster 标准外廓尺寸组尚未闭合。	PENDING: 改款后 Roadster 标准外廓尺寸组尚未闭合。
134893	134893	Convertible	TTS Roadster III facelift	8S	2		LOW	TTS Roadster 专用外廓尺寸组尚未闭合。	PENDING: TTS Roadster 专用外廓尺寸组尚未闭合。
134896	134896	Pickup	Amarok I facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	改款后双排驾驶室皮卡外廓。	READY
134986	134986	Hatchback	A7 Sportback II	C8	5	EU-AUDI-A7-C8-SPORTBACK-01	HIGH	C8 五门 Sportback 外廓。	READY
134988	134988	Hatchback	A7 Sportback II	C8	5	EU-AUDI-A7-C8-SPORTBACK-01	HIGH	C8 五门 Sportback 外廓。	READY
134990	134990	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	Polestar 动力标定不改变车身外廓。	READY
134992	134992	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	Polestar 动力标定不改变车身外廓。	READY
134993	134993	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	Polestar 动力标定不改变车身外廓。	READY
134994	134994	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	Polestar 动力标定不改变车身外廓。	READY
135018_swb	135018	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135018_lwb	135018	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135019	135019	Hatchback	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	HIGH	E210 五门掀背外廓。	READY
135021_swb	135021	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135021_lwb	135021	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135022	135022	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK 五门 SUV 外廓。	READY
135023	135023	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴乘用外廓。	READY
135024	135024	Hatchback	Leaf II	ZE1	5	EU-NISSAN-LEAF-ZE1-HATCHBACK-01	HIGH	ZE1 五门掀背外廓。	READY
135026_swb	135026	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135026_lwb	135026	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135028	135028	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135029	135029	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135033_swb	135033	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135033_lwb	135033	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135035	135035	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135052	135052	SUV	CX-3 I facelift	DK	5	EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	HIGH	DK 改款后五门 SUV 外廓。	READY
135053	135053	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	后驱改款前四门轿车外廓。	READY
135058	135058	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	后驱改款前四门轿车外廓。	READY
135059	135059	Hatchback	Megane IV RS	BFB	5	EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	HIGH	RS 宽体五门掀背外廓。	READY
135065	135065	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
135066	135066	Wagon	Talisman I	KFD	5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH	五门旅行车外廓。	READY
135068	135068	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
135069	135069	Wagon	Talisman I	KFD	5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH	五门旅行车外廓。	READY
135072	135072	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	3950	1722	1481	Auto-Data.net Ford Fiesta VII (Mk7) 3 door 1.4 TDCi	https://www.auto-data.net/en/ford-fiesta-vii-mk7-3-door-1.4-tdci-70hp-46833
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	Auto-Data.net Nissan Micra K14 1.0 IG-T	https://www.auto-data.net/en/nissan-micra-k14-1.0-ig-t-92hp-54732
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Auto-Data.net Kia ProCeed III 1.0 T-GDI	https://www.auto-data.net/en/kia-proceed-iii-1.0-t-gdi-120hp-34462
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442	Auto-Data.net Kia Ceed III GT 1.6 T-GDI	https://www.auto-data.net/en/kia-ceed-iii-gt-1.6-t-gdi-204hp-dct-44392
EU-VAUXHALL-GRANDLAND-X-SUV-01	4477	1856	1609	Auto-Data.net Vauxhall Grandland X 1.5 Turbo D	https://www.auto-data.net/en/vauxhall-grandland-x-1.5-turbo-d-130hp-38263
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Auto-Data.net Toyota RAV4 V 2.5 Hybrid e-CVT	https://www.auto-data.net/en/toyota-rav4-v-2.5-218hp-hybrid-e-cvt-34622
EU-VW-JETTA-VII-A7-SEDAN-01	4702	1799	1458	Volkswagen Newsroom; Auto-Data.net Volkswagen Jetta VII 1.4 TSI	https://www.volkswagen-newsroom.com/en/press-releases/the-new-jetta-world-premiere-north-american-international-auto-show-410;https://www.auto-data.net/en/volkswagen-jetta-vii-1.4-tsi-147hp-34640
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Auto-Data.net Mazda 3 IV Hatchback 2.0 SkyActiv-G M Hybrid	https://www.auto-data.net/en/mazda-3-iv-hatchback-2.0-skyactiv-g-m-hybrid-122hp-35962
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440	Auto-Data.net Mazda 3 IV Sedan 1.8 SkyActiv-D	https://www.auto-data.net/en/mazda-3-iv-sedan-1.8-skyactiv-d-116hp-35960
EU-AUDI-A7-C8-SPORTBACK-01	4969	1908	1422	Auto-Data.net Audi A7 Sportback C8 45 TFSI	https://www.auto-data.net/en/audi-a7-sportback-c8-45-tfsi-245hp-s-tronic-35834
EU-BMW-7-G11-LCI-SEDAN-01	5120	1902	1467	Auto-Data.net BMW 7 Series G11 LCI 730i	https://www.auto-data.net/en/bmw-7-series-g11-lci-facelift-2019-730i-249hp-steptronic-52254
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435	Auto-Data.net Toyota Corolla Hatchback XII E210	https://www.auto-data.net/en/toyota-corolla-hatchback-xii-e210-1.8-122hp-hybrid-e-cvt-34628
EU-BMW-7-G12-LCI-SEDAN-LWB-01	5260	1902	1479	Auto-Data.net BMW 7 Series Long G12 LCI 745Le	https://www.auto-data.net/en/bmw-7-series-long-g12-lci-facelift-2019-745le-394hp-plug-in-hybrid-xdrive-steptronic-35565
```

## 下一步优先处理

1. 集中闭合 Ford Focus III 改款前 Van 与 Mondeo IV Van 改款分支。
2. 闭合 Renault Megane I/II/III Van、Clio III Grandtour 和 Renault 19 Cabriolet 聚类。
3. 核对 VW T6/T6.1 Multivan、Transporter/Caravelle 的轴距、车顶和改款边界。
4. 一次性闭合 Audi TT/TTS 8S facelift 的 Coupe、Roadster及 TTS 专用外廓。
5. 处理 Combo E、Peugeot 407 Wagon、Lacetti Hatchback、Vesta SW Cross、LEVC TX 等剩余单组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-fiesta-vii-mk7-3-door-1.4-tdci-70hp-46833?utm_source=chatgpt.com "Ford Fiesta VII (Mk7) 3 door 1.4 TDCi (70 Hp)"
[2]: https://www.auto-data.net/en/toyota-rav4-v-2.5-218hp-hybrid-e-cvt-34622?utm_source=chatgpt.com "Toyota RAV4 V 2.5 (218 Hp) Hybrid e-CVT /SUV 2018"
[3]: https://www.auto-data.net/en/audi-a7-sportback-c8-45-tfsi-245hp-s-tronic-35834?utm_source=chatgpt.com "Audi A7 Sportback (C8) 45 TFSI (245 Hp) S tronic"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Ford Focus III 改款前厢式掀背，以及 Mondeo IV/BA7 厢式旅行车改款前、改款后两个物理分支；跨改款 Ktype 已拆分。([汽车目录][1])
* 闭合 Renault 19 II Cabriolet、Mégane I/II 厢式掀背和 Clio III Grandtour。([汽车数据][2])
* 闭合 Peugeot 407 SW、Hyundai i40 改款前旅行车、Chevrolet Lacetti Hatchback 和 Lada Vesta SW Cross。([汽车数据][3])
* 本轮新建 11 个尺寸组，未重复输出既有缓存尺寸组。

## 当前批次进度

* 输入 Ktype 覆盖：100 / 100
* 当前映射行：113
* READY 映射：99
* PENDING 映射：14
* 已确认并引用尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134495_prefl	134495	Van	Focus III	DYB	5	EU-FORD-FOCUS-III-PREFL-HATCHBACK-5D-01	HIGH	改款前五门厢式掀背外廓。	READY
134502_prefl	134502	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	生产区间覆盖改款前厢式旅行车外廓。	READY
134502_facelift	134502	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后厢式旅行车外廓。	READY
134505_prefl	134505	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	生产区间起始阶段覆盖改款前外廓。	READY
134505_facelift	134505	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
134506	134506	Van	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	改款后厢式旅行车外廓。	READY
134507	134507	Van	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	改款后厢式旅行车外廓。	READY
134554	134554	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-D53-CONVERTIBLE-01	HIGH	D53 改款后双门敞篷外廓。	READY
134562	134562	Wagon	407 I	6E	5	EU-PEUGEOT-407-I-SW-WAGON-01	HIGH	407 SW 五门旅行车外廓。	READY
134583_prefl	134583	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	HIGH	改款前五门旅行车外廓。	READY
134596	134596	Van	Megane I Phase II	BA0	5	EU-RENAULT-MEGANE-I-BA0-VAN-HATCHBACK-PHASE-II-01	HIGH	Phase II 五门厢式掀背外廓。	READY
134625	134625	Wagon	Vesta I SW Cross	2181	5	EU-LADA-VESTA-I-SW-CROSS-WAGON-01	HIGH	SW Cross 加高车身及外部套件外廓。	READY
134690	134690	Hatchback	Lacetti	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200 五门掀背外廓。	READY
134697	134697	Wagon	Clio III Grandtour Phase I	KR	5	EU-RENAULT-CLIO-III-KR-GRANDTOUR-WAGON-01	HIGH	Phase I Grandtour 五门旅行车外廓。	READY
134731	134731	Van	Megane II	B84	5	EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	HIGH	五门厢式掀背外廓；改款未改变三维。	READY
134732	134732	Van	Megane II	B84	5	EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	HIGH	五门厢式掀背外廓；改款未改变三维。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-PREFL-HATCHBACK-5D-01	4358	1823	1484	Automobile-Catalog Ford Focus 1.6 Ti-VCT 2011	https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html
EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	4830	1886	1512	Auto-Data.net Ford Mondeo III Wagon 2.0 i 16V	https://www.auto-data.net/en/ford-mondeo-iii-wagon-2.0-i-16v-145hp-7669
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Auto-Data.net Ford Mondeo III Wagon facelift 2010 2.0 EcoBoost	https://www.auto-data.net/en/ford-mondeo-iii-wagon-facelift-2010-2.0-ecoboost-203hp-powershift-20137
EU-RENAULT-19-II-D53-CONVERTIBLE-01	4162	1696	1410	Auto-Data.net Renault 19 Cabriolet D53 facelift 1992	https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-1.8-i-16v-135hp-10769
EU-PEUGEOT-407-I-SW-WAGON-01	4763	1811	1486	Auto-Data.net Peugeot 407 SW Phase I 2.0 16V	https://www.auto-data.net/en/peugeot-407-sw-phase-i-2004-2.0-16v-136hp-automatic-28800
EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	4770	1815	1470	Auto-Data.net Hyundai i40 Combi 2.0 MPI	https://www.auto-data.net/en/hyundai-i40-combi-2.0-mpi-166hp-automatic-31445
EU-RENAULT-MEGANE-I-BA0-VAN-HATCHBACK-PHASE-II-01	4164	1698	1420	Auto-Data.net Renault Megane I Phase II 1.9 dTi	https://www.auto-data.net/en/renault-megane-i-phase-ii-1999-1.9-dti-80hp-10578
EU-LADA-VESTA-I-SW-CROSS-WAGON-01	4424	1785	1537	LADA Vesta SW Cross official vehicle specifications	https://ladarymco.com/cars/vesta/sw-cross/print_tth.pdf
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data.net Chevrolet Lacetti Hatchback 1.4 i 16V	https://www.auto-data.net/en/chevrolet-lacetti-hatchback-1.4-i-16v-95hp-14436
EU-RENAULT-CLIO-III-KR-GRANDTOUR-WAGON-01	4203	1719	1513	Auto-Data.net Renault Clio III Grandtour Phase I	https://www.auto-data.net/en/renault-clio-iii-grandtour-phase-i-1.5-dci-86hp-fap-56120
EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	4228	1777	1458	Auto-Data.net Renault Megane II generation	https://www.auto-data.net/en/renault-megane-ii-generation-2147
```

## 下一步优先处理

1. 闭合 VW Multivan T6 与 Transporter T6/Caravelle 的 T6、T6.1、轴距和车顶物理分支。
2. 闭合 Opel Combo E 的 M/XL 及乘用、厢式车身边界。
3. 集中闭合 Audi TT/TTS 8S facelift 的 Coupe、Roadster 和 TTS 专用外廓。
4. 处理 Megane III Van、LEVC TX 两个剩余独立车型族。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html?utm_source=chatgpt.com "2011 Ford Focus 1.6 Ti-VCT (105) Titanium (man. 5)"
[2]: https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-1.8-i-16v-135hp-10769?utm_source=chatgpt.com "Renault 19 Cabriolet (D53) (facelift 1992) 1.8 i 16V (135 Hp)"
[3]: https://www.auto-data.net/en/peugeot-407-sw-phase-i-2004-2.0-16v-136hp-automatic-28800?utm_source=chatgpt.com "Peugeot 407 SW (Phase I, 2004) 2.0 16V (136 Hp) Automatic"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Audi TT/TTS 8S facelift 的标准 Coupe、TTS Coupe、标准 Roadster 和 TTS Roadster 四个尺寸组，相关 8 条 Ktype 映射全部转为 READY。([汽车数据][1])
* Renault Mégane III 厢式掀背按改款前、改款后两种外廓拆分并闭合。([汽车目录][2])
* LEVC TX 使用官方规格闭合，宽度采用不含后视镜的 1874 mm。
* VW T6 客车的轴距、普通/降低车身边界，以及 Combo E 的 M/XL 与厢式/乘用边界仍未闭合，本轮未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype 覆盖：100 / 100
* 当前映射行：114
* READY 映射：110
* PENDING 映射：4
* 已确认并引用尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134712_prefl	134712	Van	Megane III Phase I	B95	5	EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-PREFL-01	HIGH	改款前五门厢式掀背外廓。	READY
134712_facelift	134712	Van	Megane III facelift	B95	5	EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-FACELIFT-01	HIGH	改款后五门厢式掀背外廓。	READY
134832	134832	Hatchback	TX		5	EU-LEVC-TX-HATCHBACK-01	HIGH	TX 五门出租车外廓。	READY
134873	134873	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134878	134878	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134886	134886	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134888	134888	Coupe	TTS III facelift	8S	3	EU-AUDI-TTS-III-8S-FACELIFT-COUPE-01	HIGH	TTS 专用保险杠及降低车身外廓。	READY
134890	134890	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134891	134891	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134892	134892	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134893	134893	Convertible	TTS Roadster III facelift	8S	2	EU-AUDI-TTS-III-8S-FACELIFT-ROADSTER-01	HIGH	TTS Roadster 专用保险杠及降低车身外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-PREFL-01	4295	1808	1491	Automobile-Catalog 2009 Renault Megane Hatch	https://www.automobile-catalog.com/car/2009/2959430/renault_megane_hatch_1_6_16v_110.html
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-FACELIFT-01	4302	1808	1471	Automobile-Catalog 2014 Renault Megane Hatch 1.5 Energy dCi 110	https://www.automobile-catalog.com/car/2014/2961005/renault_megane_hatch_1_5_energy_dci_110.html
EU-LEVC-TX-HATCHBACK-01	4857	1874	1888	LEVC TX Price and Specification	https://www.levc.ae/images/tx.pdf
EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	4191	1832	1353	Auto-Data.net Audi TT Coupe 8S facelift 40 TFSI	https://www.auto-data.net/en/audi-tt-coupe-8s-facelift-2018-40-tfsi-197hp-s-tronic-34988
EU-AUDI-TTS-III-8S-FACELIFT-COUPE-01	4199	1832	1343	Audi TTS official dimensions; Auto-Data.net Audi TTS Coupe 8S facelift	https://media.audi.com/is/content/audi/country/za/assets/models-and-pricelists/april-2024/tt/Audi_TTS_April_2024.pdf;https://www.auto-data.net/en/audi-tts-coupe-8s-facelift-2018-2.0-tfsi-306hp-quattro-s-tronic-35845
EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	4191	1832	1355	Auto-Data.net Audi TT Roadster 8S facelift 40 TFSI	https://www.auto-data.net/en/audi-tt-roadster-8s-facelift-2018-40-tfsi-197hp-s-tronic-34993
EU-AUDI-TTS-III-8S-FACELIFT-ROADSTER-01	4199	1832	1345	Auto-Data.net Audi TTS Roadster 8S facelift	https://www.auto-data.net/en/audi-tts-roadster-8s-facelift-2018-2.0-tfsi-306hp-quattro-s-tronic-35846
```

## 下一步优先处理

1. 确认 134534、134555 在 T6/T6.1 下实际覆盖的 SWB、LWB及普通/降低车身分支。
2. 确认 134619、134620 是否同时覆盖 Combo E M/XL，以及厢式车与 Combo Life 缓存组的外廓一致性。
3. 四条 PENDING 消除后立即进行一次机械收尾并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-tt-coupe-8s-facelift-2018-40-tfsi-197hp-s-tronic-34988 "Audi TT Coupe (8S, facelift 2018) 40 TFSI (197 Hp) S tronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2009/2959430/renault_megane_hatch_1_6_16v_110.html?utm_source=chatgpt.com "2009 Renault Megane Hatch 1.6 16V 110 Specs Review ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Multivan T6/T6.1 短轴、长轴两个物理分支，分别为 4904×1904×1970 mm 和 5304×1904×1990 mm。([大众商用车][1])
* 闭合 Combo E 的 M/XL 厢式车分支；乘用分支直接复用既有 Combo E Life M/XL 尺寸组，不重复输出缓存来源。官方资料确认厢式车 M、XL 的不含后视镜宽度均为 1848 mm。([Stellantis Media][2])
* 134555 仍保留 PENDING：其输入范围同时覆盖 SGB、SGJ、SHB、SHJ，而官方 Caravelle 资料存在 4904/5304 mm 轴距分支及 1950、1970、1990 mm 高度分支，尚需将具体分支与该 Ktype 的车身代码边界闭合，未创建猜测性尺寸组。([Diederichs商店][3])

## 当前批次进度

* 输入 Ktype 覆盖：100 / 100
* 当前映射行：121
* READY 映射：120
* PENDING 映射：1
* 已确认并引用尺寸组：70
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134534_swb	134534	MPV	Multivan T6 / T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	短轴乘用车外廓。	READY
134534_lwb	134534	MPV	Multivan T6 / T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	长轴乘用车外廓。	READY
134619_van_m	134619	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M 短轴厢式车分支。	READY
134619_van_xl	134619	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL 长轴厢式车分支。	READY
134619_mpv_m	134619	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M 短轴乘用车分支。	READY
134619_mpv_xl	134619	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL 长轴乘用车分支。	READY
134620_van_m	134620	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M 短轴厢式车分支。	READY
134620_van_xl	134620	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL 长轴厢式车分支。	READY
134620_mpv_m	134620	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M 短轴乘用车分支。	READY
134620_mpv_xl	134620	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL 长轴乘用车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	4904	1904	1970	Volkswagen Commercial Vehicles Multivan 6.1 official brochure	https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf
EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	5304	1904	1990	Volkswagen Commercial Vehicles Multivan 6.1 official brochure	https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796	Vauxhall all-new Combo Van official press release	https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812	Vauxhall all-new Combo Van official press release	https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van
```

## 下一步优先处理

闭合唯一剩余的 134555：根据 SGB/SGJ/SHB/SHJ 车身代码确定 T6、T6.1 的短轴、长轴及降低车高分支。该行转为 READY 后立即进行一次机械检查并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf "https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf"
[2]: https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van "https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van"
[3]: https://shop.diederichs.com/en/t134555-c70/vw-transporter-t6-caravelle-t6-bus-sgb-sgj-shb-shj-2-0-tdi-4motion-car-body "https://shop.diederichs.com/en/t134555-c70/vw-transporter-t6-caravelle-t6-bus-sgb-sgj-shb-shj-2-0-tdi-4motion-car-body"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 134555 已按 `SGB/SGJ/SHB/SHJ` 拆分为 T6、T6.1 的短轴和长轴四个分支；对应外廓复用已闭合的 4904 mm ([大众厢型车][1])([volkswagen-vans.co.uk][1])
* 已完成机械检查：映射表严格 10 列，尺寸组表严格 6 列；`id`、`DIMENSION_GROUP_ID` 均唯一；所有引用闭合；无孤立尺寸组。
* 已生成两个指定文件。

## 当前批次进度

* 输入 Ktype：100 / 100
* 最终映射行：124
* READY：124
* PENDING：0
* 最终尺寸组：70
* 映射引用闭合：是
* 尺寸及来源完整：是

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
134484	134484	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK 五门 SUV 外廓。	READY
134485_prefl	134485	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134485_facelift	134485	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134486_prefl	134486	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134486_facelift	134486	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134487_prefl	134487	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134487_facelift	134487	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134488_prefl	134488	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	HIGH	厢式旅行车，按改款前外廓拆分。	READY
134488_facelift	134488	Van	Focus II	DA3	5	EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	HIGH	厢式旅行车，按改款后外廓拆分。	READY
134492	134492	Van	Fiesta VI	JA8	3	EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	HIGH	三门厢式掀背外廓。	READY
134493	134493	Van	Fiesta VI	JA8	3	EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	HIGH	三门厢式掀背外廓。	READY
134495_prefl	134495	Van	Focus III	DYB	5	EU-FORD-FOCUS-III-PREFL-HATCHBACK-5D-01	HIGH	改款前五门厢式掀背外廓。	READY
134495_facelift	134495	Van	Focus III	DYB	5	EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	改款后五门厢式掀背外廓。	READY
134500	134500	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 五门 SUV 外廓。	READY
134501	134501	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 五门 SUV 外廓。	READY
134502_prefl	134502	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	生产区间覆盖改款前厢式旅行车外廓。	READY
134502_facelift	134502	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后厢式旅行车外廓。	READY
134505_prefl	134505	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	HIGH	生产区间起始阶段覆盖改款前外廓。	READY
134505_facelift	134505	Van	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	生产区间覆盖改款后外廓。	READY
134506	134506	Van	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	改款后厢式旅行车外廓。	READY
134507	134507	Van	Mondeo IV facelift	BA7	5	EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	HIGH	改款后厢式旅行车外廓。	READY
134534_swb	134534	MPV	Multivan T6 / T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	短轴乘用车外廓。	READY
134534_lwb	134534	MPV	Multivan T6 / T6.1		5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	长轴乘用车外廓。	READY
134538	134538	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH	K14 五门掀背外廓。	READY
134554	134554	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-D53-CONVERTIBLE-01	HIGH	D53 改款后双门敞篷外廓。	READY
134555_t6_swb	134555	MPV	Transporter / Caravelle T6	SGB	5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	T6 短轴乘用 Bus 外廓。	READY
134555_t6_lwb	134555	MPV	Transporter / Caravelle T6	SGJ	5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	T6 长轴乘用 Bus 外廓。	READY
134555_t61_swb	134555	MPV	Transporter / Caravelle T6.1	SHB	5	EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	HIGH	T6.1 短轴乘用 Bus 外廓。	READY
134555_t61_lwb	134555	MPV	Transporter / Caravelle T6.1	SHJ	5	EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	HIGH	T6.1 长轴乘用 Bus 外廓。	READY
134558	134558	SUV	NX I facelift	AZ10	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	改款后 NX I 五门 SUV 外廓。	READY
134559	134559	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50 四门轿车外廓。	READY
134562	134562	Wagon	407 I	6E	5	EU-PEUGEOT-407-I-SW-WAGON-01	HIGH	407 SW 五门旅行车外廓。	READY
134583_prefl	134583	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	HIGH	改款前五门旅行车外廓。	READY
134583_facelift	134583	Wagon	i40 I	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
134596	134596	Van	Megane I Phase II	BA0	5	EU-RENAULT-MEGANE-I-BA0-VAN-HATCHBACK-PHASE-II-01	HIGH	Phase II 五门厢式掀背外廓。	READY
134605	134605	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134606	134606	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134607	134607	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134608	134608	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH	CD 五门 shooting-brake/旅行车外廓。	READY
134610	134610	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-GT-01	HIGH	GT 专用保险杠与降低车高外廓。	READY
134611	134611	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH	标准五门掀背外廓。	READY
134612	134612	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH	标准五门旅行车外廓。	READY
134619_van_m	134619	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M 短轴厢式车分支。	READY
134619_van_xl	134619	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL 长轴厢式车分支。	READY
134619_mpv_m	134619	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M 短轴乘用车分支。	READY
134619_mpv_xl	134619	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL 长轴乘用车分支。	READY
134620_van_m	134620	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M 短轴厢式车分支。	READY
134620_van_xl	134620	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL 长轴厢式车分支。	READY
134620_mpv_m	134620	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M 短轴乘用车分支。	READY
134620_mpv_xl	134620	MPV	Combo E Life	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL 长轴乘用车分支。	READY
134621	134621	SUV	Grandland X	P1	5	EU-VAUXHALL-GRANDLAND-X-SUV-01	HIGH	Grandland X 五门 SUV 外廓。	READY
134622	134622	Sedan	Vesta I	2180	4	EU-LADA-VESTA-I-SEDAN-01	HIGH	Vesta I 四门轿车外廓。	READY
134624	134624	Wagon	Vesta I SW	2181	5	EU-LADA-VESTA-I-SW-WAGON-01	HIGH	Vesta SW 五门旅行车外廓。	READY
134625	134625	Wagon	Vesta I SW Cross	2181	5	EU-LADA-VESTA-I-SW-CROSS-WAGON-01	HIGH	SW Cross 加高车身及外部套件外廓。	READY
134658	134658	SUV	Captur I	J87	5	EU-RENAULT-CAPTUR-I-SUV-01	HIGH	Captur I 五门 SUV 外廓。	READY
134690	134690	Hatchback	Lacetti	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200 五门掀背外廓。	READY
134697	134697	Wagon	Clio III Grandtour Phase I	KR	5	EU-RENAULT-CLIO-III-KR-GRANDTOUR-WAGON-01	HIGH	Phase I Grandtour 五门旅行车外廓。	READY
134706_phase1	134706	Van	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	MEDIUM	Phase I 五门厢式掀背外廓。	READY
134706_phase2	134706	Van	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	MEDIUM	Phase II 五门厢式掀背外廓。	READY
134712_prefl	134712	Van	Megane III Phase I	B95	5	EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-PREFL-01	HIGH	改款前五门厢式掀背外廓。	READY
134712_facelift	134712	Van	Megane III facelift	B95	5	EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-FACELIFT-01	HIGH	改款后五门厢式掀背外廓。	READY
134726	134726	Hatchback	i30 III N	PD	5	EU-HYUNDAI-I30-PD-HATCHBACK-N-01	HIGH	N 250 五门掀背外廓。	READY
134729	134729	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134730	134730	Hatchback	i30 III N	PD	5	EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	HIGH	N Performance 五门掀背外廓。	READY
134731	134731	Van	Megane II	B84	5	EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	HIGH	五门厢式掀背外廓；改款未改变三维。	READY
134732	134732	Van	Megane II	B84	5	EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	HIGH	五门厢式掀背外廓；改款未改变三维。	READY
134735	134735	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134736	134736	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	XA50 五门 SUV 外廓。	READY
134739	134739	MPV	Caddy IV Alltrack	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴 Alltrack 外廓。	READY
134740	134740	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-FWD-01	HIGH	前驱标准车高外廓。	READY
134743	134743	Sedan	Jetta VII	A7	4	EU-VW-JETTA-VII-A7-SEDAN-01	HIGH	A7 四门轿车外廓。	READY
134745	134745	MPV	Caddy IV Alltrack	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴 Alltrack 外廓。	READY
134747	134747	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH	BP 五门掀背外廓。	READY
134748	134748	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH	BP 五门掀背外廓。	READY
134749	134749	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	BP 四门轿车外廓。	READY
134750	134750	Sedan	Mazda 3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	BP 四门轿车外廓。	READY
134755	134755	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60 II 五门 SUV 外廓。	READY
134756	134756	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 五门旅行车外廓。	READY
134757	134757	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II 五门旅行车外廓。	READY
134773	134773	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
134825	134825	Wagon	i40 I facelift	VF	5	EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	HIGH	改款后旅行车外廓。	READY
134826	134826	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	四门轿车外廓。	READY
134827	134827	Sedan	i40 I	VF	4	EU-HYUNDAI-I40-I-VF-SEDAN-01	HIGH	四门轿车外廓。	READY
134832	134832	Hatchback	TX		5	EU-LEVC-TX-HATCHBACK-01	HIGH	TX 五门出租车外廓。	READY
134844	134844	SUV	Q2	GA	5	EU-AUDI-Q2-GA-SUV-01	HIGH	GA 五门 SUV 外廓。	READY
134873	134873	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134878	134878	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134886	134886	Coupe	TT III facelift	8S	3	EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	HIGH	改款后标准 Coupe 外廓。	READY
134888	134888	Coupe	TTS III facelift	8S	3	EU-AUDI-TTS-III-8S-FACELIFT-COUPE-01	HIGH	TTS 专用保险杠及降低车身外廓。	READY
134890	134890	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134891	134891	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134892	134892	Convertible	TT Roadster III facelift	8S	2	EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	HIGH	改款后标准 Roadster 外廓。	READY
134893	134893	Convertible	TTS Roadster III facelift	8S	2	EU-AUDI-TTS-III-8S-FACELIFT-ROADSTER-01	HIGH	TTS Roadster 专用保险杠及降低车身外廓。	READY
134896	134896	Pickup	Amarok I facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	改款后双排驾驶室皮卡外廓。	READY
134986	134986	Hatchback	A7 Sportback II	C8	5	EU-AUDI-A7-C8-SPORTBACK-01	HIGH	C8 五门 Sportback 外廓。	READY
134988	134988	Hatchback	A7 Sportback II	C8	5	EU-AUDI-A7-C8-SPORTBACK-01	HIGH	C8 五门 Sportback 外廓。	READY
134990	134990	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90 II 四门轿车外廓。	READY
134992	134992	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60 II 五门 SUV 外廓。	READY
134993	134993	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH	XC40 I 五门 SUV 外廓。	READY
134994	134994	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	XC60 II 五门 SUV 外廓。	READY
135018_swb	135018	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135018_lwb	135018	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135019	135019	Hatchback	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	HIGH	E210 五门掀背外廓。	READY
135021_swb	135021	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135021_lwb	135021	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135022	135022	SUV	Forester V	SK	5	EU-SUBARU-FORESTER-V-SK-SUV-01	HIGH	SK 五门 SUV 外廓。	READY
135023	135023	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	未标 Maxi，按短轴乘用外廓。	READY
135024	135024	Hatchback	Leaf II	ZE1	5	EU-NISSAN-LEAF-ZE1-HATCHBACK-01	HIGH	ZE1 五门掀背外廓。	READY
135026_swb	135026	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135026_lwb	135026	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135028	135028	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135029	135029	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135033_swb	135033	Sedan	7 Series G11 LCI	G11	4	EU-BMW-7-G11-LCI-SEDAN-01	HIGH	标准轴距 G11 LCI 分支。	READY
135033_lwb	135033	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 分支。	READY
135035	135035	Sedan	7 Series G12 LCI	G12	4	EU-BMW-7-G12-LCI-SEDAN-LWB-01	HIGH	长轴距 G12 LCI 外廓。	READY
135052	135052	SUV	CX-3 I facelift	DK	5	EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	HIGH	DK 改款后五门 SUV 外廓。	READY
135053	135053	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	后驱改款前四门轿车外廓。	READY
135058	135058	Sedan	3 Series G20 pre-facelift	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	后驱改款前四门轿车外廓。	READY
135059	135059	Hatchback	Megane IV RS	BFB	5	EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	HIGH	RS 宽体五门掀背外廓。	READY
135065	135065	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
135066	135066	Wagon	Talisman I	KFD	5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH	五门旅行车外廓。	READY
135068	135068	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
135069	135069	Wagon	Talisman I	KFD	5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH	五门旅行车外廓。	READY
135072	135072	Sedan	Talisman I	L2M	4	EU-RENAULT-TALISMAN-I-SEDAN-01	HIGH	四门轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3401-3500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-FORESTER-V-SK-SUV-01	4625	1815	1730	Auto-Data.net Subaru Forester V 2.0 e-Boxer	https://www.auto-data.net/en/subaru-forester-v-2.0-e-boxer-150hp-awd-lineartronic-36903
EU-FORD-FOCUS-II-DA3-VAN-WAGON-PREFL-01	4472	1840	1501	Auto-Data.net Ford Focus Turnier II	https://www.auto-data.net/en/ford-focus-turnier-ii-generation-1648
EU-FORD-FOCUS-II-DA3-VAN-WAGON-FACELIFT-01	4468	1839	1501	Auto-Data.net Ford Focus Turnier II	https://www.auto-data.net/en/ford-focus-turnier-ii-generation-1648
EU-FORD-FIESTA-VI-JA8-VAN-HATCHBACK-3D-01	3950	1722	1481	Auto-Data.net Ford Fiesta VII (Mk7) 3-door 1.4 TDCi	https://www.auto-data.net/en/ford-fiesta-vii-mk7-3-door-1.4-tdci-70hp-46833
EU-FORD-FOCUS-III-PREFL-HATCHBACK-5D-01	4358	1823	1484	Automobile-Catalog Ford Focus 1.6 Ti-VCT 2011	https://www.automobile-catalog.com/car/2011/1592780/ford_focus_1_6_ti-vct_105_titanium.html
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484	Auto-Data.net Ford Focus III Hatchback facelift	https://www.auto-data.net/en/ford-focus-iii-hatchback-facelift-2014-generation-4281
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	Auto-Data.net Mercedes-Benz GLE SUV V167	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-generation-6596
EU-FORD-MONDEO-IV-BA7-WAGON-PREFL-01	4830	1886	1512	Auto-Data.net Ford Mondeo III Wagon 2.0 i 16V	https://www.auto-data.net/en/ford-mondeo-iii-wagon-2.0-i-16v-145hp-7669
EU-FORD-MONDEO-IV-BA7-WAGON-FACELIFT-01	4837	1886	1512	Auto-Data.net Ford Mondeo III Wagon facelift 2.0 EcoBoost	https://www.auto-data.net/en/ford-mondeo-iii-wagon-facelift-2010-2.0-ecoboost-203hp-powershift-20137
EU-VW-MULTIVAN-T6-T61-MPV-SWB-01	4904	1904	1970	Volkswagen Commercial Vehicles Multivan 6.1 official brochure	https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf
EU-VW-MULTIVAN-T6-T61-MPV-LWB-01	5304	1904	1990	Volkswagen Commercial Vehicles Multivan 6.1 official brochure	https://www.volkswagen-utilitaires.lu/idhub/content/dam/onehub_nfz/importers/lu/listes-de-prix-%26-catalogues/catalogues/2021/multivan/Multivan_EN.pdf
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	Auto-Data.net Nissan Micra K14 1.0 IG-T	https://www.auto-data.net/en/nissan-micra-k14-1.0-ig-t-92hp-54732
EU-RENAULT-19-II-D53-CONVERTIBLE-01	4162	1696	1410	Auto-Data.net Renault 19 Cabriolet D53 facelift	https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-1.8-i-16v-135hp-10769
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645	Auto-Data.net Lexus NX I AZ10 facelift 300h	https://www.auto-data.net/en/lexus-nx-i-az10-facelift-2017-300h-197hp-hybrid-e-four-e-cvt-32700
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450	Auto-Data.net Lexus LS V 500h	https://www.auto-data.net/en/lexus-ls-v-500h-v6-354hp-hybrid-e-cvt-29161
EU-PEUGEOT-407-I-SW-WAGON-01	4763	1811	1486	Auto-Data.net Peugeot 407 SW Phase I 2.0 16V	https://www.auto-data.net/en/peugeot-407-sw-phase-i-2004-2.0-16v-136hp-automatic-28800
EU-HYUNDAI-I40-I-VF-WAGON-PREFL-01	4770	1815	1470	Auto-Data.net Hyundai i40 Combi 2.0 MPI	https://www.auto-data.net/en/hyundai-i40-combi-2.0-mpi-166hp-automatic-31445
EU-HYUNDAI-I40-I-VF-WAGON-FACELIFT-01	4775	1815	1470	Auto-Data.net Hyundai i40 Combi facelift	https://www.auto-data.net/en/hyundai-i40-combi-facelift-2015-generation-4646
EU-RENAULT-MEGANE-I-BA0-VAN-HATCHBACK-PHASE-II-01	4164	1698	1420	Auto-Data.net Renault Megane I Phase II 1.9 dTi	https://www.auto-data.net/en/renault-megane-i-phase-ii-1999-1.9-dti-80hp-10578
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Auto-Data.net Kia ProCeed III 1.0 T-GDI	https://www.auto-data.net/en/kia-proceed-iii-1.0-t-gdi-120hp-34462
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442	Auto-Data.net Kia Ceed III GT 1.6 T-GDI	https://www.auto-data.net/en/kia-ceed-iii-gt-1.6-t-gdi-204hp-dct-44392
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Auto-Data.net Kia Ceed III	https://www.auto-data.net/en/kia-ceed-model-1935
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Auto-Data.net Kia Ceed III Sportswagon	https://www.auto-data.net/en/kia-ceed-iii-sportswagon-1.4-t-gdi-140hp-dct-32823
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796	Vauxhall all-new Combo Van official press release	https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812	Vauxhall all-new Combo Van official press release	https://www.media.stellantis.com/uk-en/vauxhall/press/vauxhall-announces-pricing-for-all-new-combo-van
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841	Auto-Data.net Opel Combo Life E	https://www.auto-data.net/en/opel-combo-life-e-generation-6369
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880	Auto-Data.net Opel Combo Life XL E	https://www.auto-data.net/en/opel-combo-life-xl-e-generation-6370
EU-VAUXHALL-GRANDLAND-X-SUV-01	4477	1856	1609	Auto-Data.net Vauxhall Grandland X 1.5 Turbo D	https://www.auto-data.net/en/vauxhall-grandland-x-1.5-turbo-d-130hp-38263
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497	LADA Vesta official vehicle specifications	https://ladarymco.com/cars/vesta/sw-cross/print_tth.pdf
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512	LADA Vesta official vehicle specifications	https://ladarymco.com/cars/vesta/sw-cross/print_tth.pdf
EU-LADA-VESTA-I-SW-CROSS-WAGON-01	4424	1785	1537	LADA Vesta SW Cross official vehicle specifications	https://ladarymco.com/cars/vesta/sw-cross/print_tth.pdf
EU-RENAULT-CAPTUR-I-SUV-01	4122	1778	1566	Auto-Data.net Renault Captur facelift	https://www.auto-data.net/en/renault-captur-facelift-2017-generation-5532
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data.net Chevrolet Lacetti Hatchback 1.4 i 16V	https://www.auto-data.net/en/chevrolet-lacetti-hatchback-1.4-i-16v-95hp-14436
EU-RENAULT-CLIO-III-KR-GRANDTOUR-WAGON-01	4203	1719	1513	Auto-Data.net Renault Clio III Grandtour Phase I	https://www.auto-data.net/en/renault-clio-iii-grandtour-phase-i-1.5-dci-86hp-fap-56120
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448	Auto-Data.net Renault Clio IV Phase I	https://www.auto-data.net/en/renault-clio-iv-phase-i-generation-3871
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448	Auto-Data.net Renault Clio IV Phase II 1.2 16V	https://www.auto-data.net/en/renault-clio-iv-phase-ii-2016-1.2-16v-75hp-25148
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-PREFL-01	4295	1808	1491	Automobile-Catalog 2009 Renault Megane Hatch	https://www.automobile-catalog.com/car/2009/2959430/renault_megane_hatch_1_6_16v_110.html
EU-RENAULT-MEGANE-III-B95-VAN-HATCHBACK-FACELIFT-01	4302	1808	1471	Automobile-Catalog 2014 Renault Megane Hatch 1.5 Energy dCi 110	https://www.automobile-catalog.com/car/2014/2961005/renault_megane_hatch_1_5_energy_dci_110.html
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451	AutoData1 Hyundai i30 III N 2.0 T-GDI 250	https://www.autodata1.com/en/car/hyundai/i30/i30-iii-n-20-t-gdi-250-hp
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Auto-Data.net Toyota RAV4 V 2.5 Hybrid e-CVT	https://www.auto-data.net/en/toyota-rav4-v-2.5-218hp-hybrid-e-cvt-34622
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447	ADAC Hyundai i30 N Performance	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/hyundai/i30/3generation-facelift/298832/
EU-RENAULT-MEGANE-II-B84-HATCHBACK-01	4228	1777	1458	Auto-Data.net Renault Megane II	https://www.auto-data.net/en/renault-megane-ii-generation-2147
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Commercial Vehicles Caddy body builder guidelines	https://umbauportal.volkswagen-nutzfahrzeuge.ch/download/Technische%20Informationen/Aufbaurichtlinien/Caddy/Archiv/Aufbaurichtlinien-Caddy-DE-28-2019.pdf
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654	Auto-Data.net Volkswagen Tiguan II	https://www.auto-data.net/en/volkswagen-tiguan-ii-generation-4678
EU-VW-JETTA-VII-A7-SEDAN-01	4702	1799	1458	Volkswagen Newsroom; Auto-Data.net Volkswagen Jetta VII 1.4 TSI	https://www.volkswagen-newsroom.com/en/press-releases/the-new-jetta-world-premiere-north-american-international-auto-show-410;https://www.auto-data.net/en/volkswagen-jetta-vii-1.4-tsi-147hp-34640
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Auto-Data.net Mazda 3 IV Hatchback 2.0 SkyActiv-G M Hybrid	https://www.auto-data.net/en/mazda-3-iv-hatchback-2.0-skyactiv-g-m-hybrid-122hp-35962
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440	Auto-Data.net Mazda 3 IV Sedan 1.8 SkyActiv-D	https://www.auto-data.net/en/mazda-3-iv-sedan-1.8-skyactiv-d-116hp-35960
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data.net Volvo XC60 II	https://www.auto-data.net/en/volvo-xc60-ii-generation-5397
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Auto-Data.net Volvo V90 Cross Country	https://www.auto-data.net/en/volvo-v90-cross-country-generation-5155
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data.net Volvo V90 2.0 D4	https://www.auto-data.net/en/volvo-v90-2016-2.0-d4-190hp-automatic-36301
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Auto-Data.net Volvo S90	https://www.auto-data.net/en/volvo-s90-2016-generation-4653
EU-HYUNDAI-I40-I-VF-SEDAN-01	4770	1815	1470	Hyundai i40 owner's manual	https://www.manualslib.com/manual/623628/Hyundai-I40.html
EU-LEVC-TX-HATCHBACK-01	4857	1874	1888	LEVC TX Price and Specification	https://www.levc.ae/images/tx.pdf
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508	Auto-Data.net Audi Q2 40 TFSI quattro	https://www.auto-data.net/en/audi-q2-40-tfsi-190hp-quattro-s-tronic-35837
EU-AUDI-TT-III-8S-FACELIFT-COUPE-01	4191	1832	1353	Auto-Data.net Audi TT Coupe 8S facelift 40 TFSI	https://www.auto-data.net/en/audi-tt-coupe-8s-facelift-2018-40-tfsi-197hp-s-tronic-34988
EU-AUDI-TTS-III-8S-FACELIFT-COUPE-01	4199	1832	1343	Audi TTS official dimensions; Auto-Data.net Audi TTS Coupe 8S facelift	https://media.audi.com/is/content/audi/country/za/assets/models-and-pricelists/april-2024/tt/Audi_TTS_April_2024.pdf;https://www.auto-data.net/en/audi-tts-coupe-8s-facelift-2018-2.0-tfsi-306hp-quattro-s-tronic-35845
EU-AUDI-TT-III-8S-FACELIFT-ROADSTER-01	4191	1832	1355	Auto-Data.net Audi TT Roadster 8S facelift 40 TFSI	https://www.auto-data.net/en/audi-tt-roadster-8s-facelift-2018-40-tfsi-197hp-s-tronic-34993
EU-AUDI-TTS-III-8S-FACELIFT-ROADSTER-01	4199	1832	1345	Auto-Data.net Audi TTS Roadster 8S facelift	https://www.auto-data.net/en/audi-tts-roadster-8s-facelift-2018-2.0-tfsi-306hp-quattro-s-tronic-35846
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834	Auto-Data.net Volkswagen Amarok I Double Cab facelift	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-224hp-4motion-automatic-27100
EU-AUDI-A7-C8-SPORTBACK-01	4969	1908	1422	Auto-Data.net Audi A7 Sportback C8 45 TFSI	https://www.auto-data.net/en/audi-a7-sportback-c8-45-tfsi-245hp-s-tronic-35834
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo Support XC40 dimensions	https://www.volvocars.com/jp/support/car/xc40/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-BMW-7-G11-LCI-SEDAN-01	5120	1902	1467	Auto-Data.net BMW 7 Series G11 LCI 730i	https://www.auto-data.net/en/bmw-7-series-g11-lci-facelift-2019-730i-249hp-steptronic-52254
EU-BMW-7-G12-LCI-SEDAN-LWB-01	5260	1902	1479	Auto-Data.net BMW 7 Series Long G12 LCI 745Le	https://www.auto-data.net/en/bmw-7-series-long-g12-lci-facelift-2019-745le-394hp-plug-in-hybrid-xdrive-steptronic-35565
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435	Auto-Data.net Toyota Corolla Hatchback XII E210	https://www.auto-data.net/en/toyota-corolla-hatchback-xii-e210-1.8-122hp-hybrid-e-cvt-34628
EU-NISSAN-LEAF-ZE1-HATCHBACK-01	4490	1788	1530	Auto-Data.net Nissan Leaf II ZE1 40 kWh	https://www.auto-data.net/en/nissan-leaf-ii-ze1-40-kwh-150hp-32049
EU-MAZDA-CX-3-DK-FACELIFT-SUV-01	4275	1765	1535	Auto-Data.net Mazda CX-3 facelift 2018	https://www.auto-data.net/en/mazda-cx-3-facelift-2018-generation-6355
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	Auto-Data.net BMW 3 Series Sedan G20 320i	https://www.auto-data.net/en/bmw-3-series-sedan-g20-320i-184hp-steptronic-37228
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435	Auto-Data.net Renault Megane IV RS	https://www.auto-data.net/en/renault-megane-iv-generation-4654
EU-RENAULT-TALISMAN-I-SEDAN-01	4849	1868	1456	Renault Talisman official brochure	https://brochures.renault.com.gh/brochures/Talisman-brochure-EN.pdf
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465	Renault Talisman official brochure	https://brochures.renault.com.gh/brochures/Talisman-brochure-EN.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3401-3500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf "https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caravelle/caravelle-brochure.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2914 行）
- 累计尺寸组：dimension_groups_final.tsv（1388 行）

