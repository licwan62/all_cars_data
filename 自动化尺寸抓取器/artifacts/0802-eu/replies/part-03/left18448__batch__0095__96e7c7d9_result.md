# 任务：left18448 第 9401-9500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0095__96e7c7d9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9401-9500 行

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
left18448 第 9401-9500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9401-9500_ktype_dimension_mapping_final.tsv
- left18448_9401-9500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	C-Klasse	C 180 Kompressor	Kombi	Heckantrieb	Benzin	May 2002	Aug 2007	16716
Mercedes-benz	C-Klasse	C 180 Kompressor	Coupe	Heckantrieb	Benzin	May 2002	May 2008	16718
Mercedes-benz	C-Klasse	C 180 T	Kombi	Heckantrieb	Benzin	Sep 2000	Mar 2001	15037
Mercedes-benz	C-Klasse	C 200	Stufenheck	Heckantrieb	Benzin	Dec 2013	Aug 2018	100551
Mercedes-benz	C-Klasse	C 200	Kombi	Heckantrieb	Benzin	Sep 2014	May 2018	106454
Mercedes-benz	C-Klasse	C 200	Coupe	Heckantrieb	Benzin	Oct 2015	May 2018	116939
Mercedes-benz	C-Klasse	C 200	Cabriolet	Heckantrieb	Benzin	Jun 2016	May 2018	120122
Mercedes-benz	C-Klasse	C 200	Stufenheck	Heckantrieb	Benzin/Elektro	Mar 2021	-	143578
Mercedes-benz	C-Klasse	C 200	Kombi	Heckantrieb	Benzin/Elektro	Mar 2021	-	143633
Mercedes-benz	C-Klasse	C 200 4-matic	Stufenheck	Allrad	Benzin	Apr 2015	Aug 2018	112354
Mercedes-benz	C-Klasse	C 200 4-matic	Kombi	Allrad	Benzin	Apr 2015	May 2018	112362
Mercedes-benz	C-Klasse	C 200 4-matic	Cabriolet	Allrad	Benzin	Jun 2016	May 2018	120123
Mercedes-benz	C-Klasse	C 200 4-matic	Stufenheck	Allrad	Benzin/Elektro	Mar 2021	-	143579
Mercedes-benz	C-Klasse	C 200 4-matic	Kombi	Allrad	Benzin/Elektro	Oct 2021	-	145529
Mercedes-benz	C-Klasse	C 200 4-matic	Kombi	Allrad	Benzin/Elektro	Dec 2021	-	146614
Mercedes-benz	C-Klasse	C 200 Bluetec / D	Stufenheck	Heckantrieb	Diesel	May 2014	May 2018	106290
Mercedes-benz	C-Klasse	C 200 Bluetec / D	Kombi	Heckantrieb	Diesel	Sep 2014	May 2018	107474
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	Mar 1998	May 2000	10229
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	Sep 2000	Jun 2003	14818
Mercedes-benz	C-Klasse	C 200 CDI	Kombi	Heckantrieb	Diesel	Mar 2001	Aug 2007	15721
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	Feb 2001	Jun 2003	16089
Mercedes-benz	C-Klasse	C 200 CDI	Kombi	Heckantrieb	Diesel	Mar 2001	Aug 2007	16090
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	Apr 2003	Feb 2007	17375
Mercedes-benz	C-Klasse	C 200 CDI	Kombi	Heckantrieb	Diesel	Apr 2003	Aug 2007	17378
Mercedes-benz	C-Klasse	C 200 CDI	Coupe	Heckantrieb	Diesel	Mar 2003	May 2008	17379
Mercedes-benz	C-Klasse	C 200 CGI	Kombi	Heckantrieb	Benzin	Aug 2007	Aug 2014	57283
Mercedes-benz	C-Klasse	C 200 CGI	Coupe	Heckantrieb	Benzin	Jun 2011	-	57291
Mercedes-benz	C-Klasse	C 200 CGI Kompressor	Coupe	Heckantrieb	Benzin	Mar 2003	May 2008	17131
Mercedes-benz	C-Klasse	C 200 CGI Kompressor	Stufenheck	Heckantrieb	Benzin	Jul 2003	Feb 2007	17376
Mercedes-benz	C-Klasse	C 200 CGI Kompressor	Kombi	Heckantrieb	Benzin	Jul 2003	Aug 2007	17377
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel	Oct 2015	May 2018	116948
Mercedes-benz	C-Klasse	C 200 D	Kombi	Heckantrieb	Diesel	Oct 2015	May 2018	116949
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel/Elektro	Jul 2021	-	145132
Mercedes-benz	C-Klasse	C 200 D	Kombi	Heckantrieb	Diesel/Elektro	Jul 2021	-	145150
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	Oct 1995	May 2000	5116
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	May 2000	Jun 2002	14815
Mercedes-benz	C-Klasse	C 200 Kompressor	Coupe	Heckantrieb	Benzin	Mar 2001	May 2002	15263
Mercedes-benz	C-Klasse	C 200 Kompressor	Kombi	Heckantrieb	Benzin	Mar 2001	May 2002	15719
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	May 2002	Feb 2007	16715
Mercedes-benz	C-Klasse	C 200 Kompressor	Kombi	Heckantrieb	Benzin	May 2002	Aug 2007	16717
Mercedes-benz	C-Klasse	C 200 Kompressor	Coupe	Heckantrieb	Benzin	May 2002	May 2008	16719
Mercedes-benz	C-Klasse	C 200 T CDI	Kombi	Heckantrieb	Diesel	Mar 1998	Mar 2001	10966
Mercedes-benz	C-Klasse	C 200 T D	Kombi	Heckantrieb	Diesel	Oct 1996	Mar 2001	5977
Mercedes-benz	C-Klasse	C 200 T Kompressor	Kombi	Heckantrieb	Benzin	Sep 2000	Mar 2001	15038
Mercedes-benz	C-Klasse	C 220 Bluetec / D	Stufenheck	Heckantrieb	Diesel	Feb 2014	May 2018	100560
Mercedes-benz	C-Klasse	C 220 Bluetec / D	Stufenheck	Heckantrieb	Diesel	Mar 2014	May 2016	100751
Mercedes-benz	C-Klasse	C 220 Bluetec / D	Kombi	Heckantrieb	Diesel	Sep 2014	May 2018	106451
Mercedes-benz	C-Klasse	C 220 Bluetec / D	Kombi	Heckantrieb	Diesel	Sep 2014	May 2018	108610
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	Aug 2006	Aug 2007	5758
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	Sep 1997	May 2000	8888
Mercedes-benz	C-Klasse	C 220 CDI	Coupe	Heckantrieb	Diesel	Jun 2011	-	10330
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	May 2000	Feb 2007	14820
Mercedes-benz	C-Klasse	C 220 CDI	Coupe	Heckantrieb	Diesel	Mar 2001	Jan 2004	15264
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	Mar 2001	Aug 2007	15722
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	Feb 2004	Aug 2007	17863
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	Apr 2003	Feb 2007	17864
Mercedes-benz	C-Klasse	C 220 CDI	Coupe	Heckantrieb	Diesel	Feb 2004	May 2008	17865
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	May 2000	Feb 2007	54930
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	Jan 2007	Nov 2008	54942
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	Aug 2007	Nov 2008	54951
Mercedes-benz	C-Klasse	C 220 CDI	Coupe	Heckantrieb	Diesel	Mar 2001	Jan 2004	54959
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	Oct 2008	Jan 2014	59470
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	Dec 2008	Aug 2014	59471
Mercedes-benz	C-Klasse	C 220 CDI	Coupe	Heckantrieb	Diesel	Jun 2011	-	100914
Mercedes-benz	C-Klasse	C 220 CDI 4-matic	Stufenheck	Allrad	Diesel	Feb 2013	Jan 2014	59441
Mercedes-benz	C-Klasse	C 220 CDI 4-matic	Kombi	Allrad	Diesel	Feb 2013	Aug 2014	59442
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel	Jul 1996	May 2000	11079
Mercedes-benz	C-Klasse	C 220 D	Coupe	Heckantrieb	Diesel	Oct 2015	May 2018	116936
Mercedes-benz	C-Klasse	C 220 D	Coupe	Heckantrieb	Diesel	Oct 2015	May 2018	118792
Mercedes-benz	C-Klasse	C 220 D	Cabriolet	Heckantrieb	Diesel	Jun 2016	May 2018	120130
Mercedes-benz	C-Klasse	C 220 D	Cabriolet	Heckantrieb	Diesel	Jun 2016	May 2018	124381
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel/Elektro	Mar 2021	-	143580
Mercedes-benz	C-Klasse	C 220 D	Kombi	Heckantrieb	Diesel/Elektro	Mar 2021	-	143635
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel/Elektro	Jun 2023	-	155222
Mercedes-benz	C-Klasse	C 220 D	Kombi	Heckantrieb	Diesel/Elektro	Jun 2023	-	155225
Mercedes-benz	C-Klasse	C 220 D 4-matic	Stufenheck	Allrad	Diesel	Apr 2015	May 2018	112348
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel	Apr 2015	May 2018	112365
Mercedes-benz	C-Klasse	C 220 D 4-matic	Cabriolet	Allrad	Diesel	Jun 2016	May 2018	120131
Mercedes-benz	C-Klasse	C 220 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Jul 2021	-	145133
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Mar 2021	-	145149
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Dec 2021	-	146615
Mercedes-benz	C-Klasse	C 220 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Jun 2023	-	155223
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Jun 2023	-	155226
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	Jun 2023	-	155231
Mercedes-benz	C-Klasse	C 220 T CDI	Kombi	Heckantrieb	Diesel	Sep 1997	Mar 2001	8889
Mercedes-benz	C-Klasse	C 220 T D	Kombi	Heckantrieb	Diesel	Jun 1996	Mar 2001	11080
Mercedes-benz	C-Klasse	C 230	Coupe	Heckantrieb	Benzin	Jan 2005	May 2008	18699
Mercedes-benz	C-Klasse	C 230	Stufenheck	Heckantrieb	Benzin	Jan 2005	Feb 2007	18883
Mercedes-benz	C-Klasse	C 230	Kombi	Heckantrieb	Benzin	Jan 2005	Aug 2007	18884
Mercedes-benz	C-Klasse	C 230 Kompressor	Stufenheck	Heckantrieb	Benzin	Oct 1995	May 2000	5115
Mercedes-benz	C-Klasse	C 230 Kompressor	Coupe	Heckantrieb	Benzin	Mar 2001	May 2002	15265
Mercedes-benz	C-Klasse	C 230 Kompressor	Coupe	Heckantrieb	Benzin	May 2002	May 2008	16720
Mercedes-benz	C-Klasse	C 230 Kompressor	Stufenheck	Heckantrieb	Benzin	Feb 2004	Feb 2007	17861
Mercedes-benz	C-Klasse	C 230 Kompressor	Kombi	Heckantrieb	Benzin	Feb 2004	Aug 2007	17862
Mercedes-benz	C-Klasse	C 230 T	Kombi	Heckantrieb	Benzin	Jun 1996	Jun 1998	5956
Mercedes-benz	C-Klasse	C 240	Stufenheck	Heckantrieb	Benzin	May 2000	Feb 2007	14816
Mercedes-benz	C-Klasse	C 240	Kombi	Heckantrieb	Benzin	Mar 2001	Aug 2007	15833
Mercedes-benz	C-Klasse	C 240 4-matic	Stufenheck	Allrad	Benzin	Jul 2002	Feb 2007	16927
Mercedes-benz	C-Klasse	C 240 4-matic	Kombi	Allrad	Benzin	Jul 2002	Aug 2007	16929
Mercedes-benz	C-Klasse	C 240 T	Kombi	Heckantrieb	Benzin	Sep 2000	Mar 2001	15039


--- Round 1 / 首次发送 ---
## 更新点

* 完成 W202/S202 的前期与后期外廓边界处理。跨越 1997 年更新节点的 Ktype 已拆成 `prefl`、`facelift` 两条派生映射。
* 新建 W202 前期轿车组 `4487×1720×1427`，以及 S202 前期旅行车组 `4487×1720×1460`；三维均为官方标准悬架数据，宽度不含后视镜。([marsClassic][1])
* W202/S202 后期组以及 W205/S205 组直接复用历史锁定缓存，不重复输出尺寸组。
* 发动机、燃料及 4MATIC 差异未用于重复建组。

## 当前批次进度

* 输入 Ktype：100
* 本轮已闭合输入 Ktype：27
* READY 映射：33
* 待闭合输入 Ktype：73
* 已确认尺寸组：6

  * 本轮新建：2
  * 历史缓存复用：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15037	15037	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期标准外廓。	READY
100551	100551	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
106454	106454	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
112354	112354	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
112362	112362	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
106290	106290	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
107474	107474	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
10229	10229	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	W202后期标准外廓。	READY
116948	116948	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
116949	116949	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
5116_prefl	5116	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5116_facelift	5116	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
10966	10966	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期标准外廓。	READY
5977_prefl	5977	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5977_facelift	5977	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
15038	15038	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期标准外廓。	READY
100560	100560	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
100751	100751	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
106451	106451	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
108610	108610	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
8888	8888	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	W202后期标准外廓。	READY
11079_prefl	11079	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
11079_facelift	11079	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
112348	112348	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205标准外廓。	READY
112365	112365	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205标准外廓。	READY
8889	8889	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期标准外廓。	READY
11080_prefl	11080	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
11080_facelift	11080	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
5115_prefl	5115	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5115_facelift	5115	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
5956_prefl	5956	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5956_facelift	5956	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
15039	15039	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1427	Mercedes-Benz Public Archive — C 230 Compressor (W 202 E 23 ML)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-230-Compressor.xhtml?oid=5524
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460	Mercedes-Benz Public Archive — C 230 station wagon (S 202 E 23)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-230-station-wagon.xhtml?oid=5551
```

## 下一步优先处理

1. 闭合 W203/S203，并处理标准悬架资料中存在的 1 mm 高度差异，避免将不同配置三维混入同一组。
2. 闭合 CL203 前期与 2004 年更新后分支，确认更新是否实际改变标准车高。
3. 批量处理 W204/S204/C204，再处理 C205/A205 与 W206/S206。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-230-Compressor.xhtml?oid=5524 "C 230 Compressor"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9401-9500_ktype_dimension_mapping_final.tsv
- left18448_9401-9500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 W203 轿车、S203 旅行车与 CL203 三门 Sports Coupé 共 38 个 Ktype 的批量闭合。
* 发动机、燃料及 4MATIC 差异未触发重复尺寸组；2004 年车型更新未改变本批标准外廓三维，因此未拆分改款前后尺寸组。
* 首次建立三个尺寸组：

  * W203 Sedan：`4526×1728×1426 mm`
  * S203 Wagon：`4541×1728×1465 mm`
  * CL203 Coupe：`4343×1728×1406 mm`
* 上述三组均采用 Mercedes-Benz Public Archive 官方数据，宽度为不含后视镜的车身宽度。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：65
* READY 映射：71 行
* PENDING Ktype：35
* 已确认尺寸组：9
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16716	16716	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16718	16718	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
14818	14818	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15721	15721	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16089	16089	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16090	16090	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17375	17375	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17378	17378	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17379	17379	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
17131	17131	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
17376	17376	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17377	17377	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
14815	14815	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15263	15263	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
15719	15719	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16715	16715	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16717	16717	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16719	16719	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
5758	5758	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
14820	14820	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15264	15264	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
15722	15722	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17863	17863	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17864	17864	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17865	17865	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
54930	54930	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
54959	54959	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
18699	18699	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
18883	18883	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
18884	18884	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
15265	15265	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
16720	16720	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
17861	17861	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17862	17862	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
14816	14816	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15833	15833	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16927	16927	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16929	16929	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	4526	1728	1426	Mercedes-Benz Public Archive — C 200 CDI W203	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI.xhtml?oid=5537
EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	4541	1728	1465	Mercedes-Benz Public Archive — C 200 CDI station wagon S203	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-station-wagon.xhtml?oid=5576
EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	4343	1728	1406	Mercedes-Benz Public Archive — 203 series C-Class Sports Coupés	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/203-series-C-Class-Sports-Coups-2001---2004.xhtml?oid=453364
```

## 下一步优先处理

1. 批量闭合 W204、S204 与 C204；优先复用已锁定的 S204 改款前、改款后尺寸组。
2. 闭合 C205 Coupe 与 A205 Cabriolet。
3. 最后处理 W206、S206 的后驱和 4MATIC 高度边界。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI.xhtml?oid=5537 "C 200 CDI"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9401-9500_ktype_dimension_mapping_final.tsv
- left18448_9401-9500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 W204 轿车、S204 旅行车及 C204 双门 Coupé 共 10 个 Ktype 的映射闭合。
* 跨越 2011 年外廓更新的 `57283`、`59470`、`59471` 已拆分为 `prefl` 与 `facelift` 分支。
* W204 更新后后驱与 4MATIC 的本批标准外廓一致，复用同一尺寸组；未因驱动形式重复建组。
* 首次创建 5 个尺寸组。官方档案确认 W204 由 `4581 mm` 更新为 `4591 mm`、S204 由 `4596 mm` 更新为 `4606 mm`；车宽均为不含后视镜的 `1770 mm`。C204 标准外廓为 `4590×1770×1403 mm`。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：75
* READY 映射：84 行
* PENDING Ktype：25
* 已确认尺寸组：14
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57283_prefl	57283	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
57283_facelift	57283	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
57291	57291	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
10330	10330	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
54942	54942	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	W204更新前四门轿车外廓。	READY
54951	54951	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	S204更新前五门旅行车外廓。	READY
59470_prefl	59470	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
59470_facelift	59470	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
59471_prefl	59471	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
59471_facelift	59471	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
100914	100914	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
59441	59441	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	W204更新后四门轿车外廓。	READY
59442	59442	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	S204更新后五门旅行车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Mercedes-Benz Public Archive — C 220 CDI Estate 2007–2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-2007---2009.xhtml?oid=189508161
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Estate 2011–2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-2011---2014-from-2013-C-220-CDI.xhtml?oid=189508213
EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	4590	1770	1403	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Coupé 2011–2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-Coup-2011---2015-from-2013-C-220-CDI-Coup.xhtml?oid=189638968
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1444	Mercedes-Benz Public Archive — C 220 CDI Saloon 2007–2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-2007---2008-only-for-export-until-2009.xhtml?oid=189266725
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1444	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Saloon 2011–2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-2011---2014-from-2013-C-220-CDI.xhtml?oid=189266522
```

## 下一步优先处理

1. 闭合 C205 Coupe 与 A205 Cabriolet 的 8 个剩余 Ktype。
2. 批量闭合 W206 Sedan 与 S206 Wagon 的 17 个剩余 Ktype，并仅在实际高度不同的情况下区分后驱与 4MATIC。
3. PENDING 清零后立即执行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-2007---2008-only-for-export-until-2009.xhtml?oid=189266725&utm_source=chatgpt.com "C 220 CDI, 2007 - 2008 (only for export until 2009)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9401-9500_ktype_dimension_mapping_final.tsv
- left18448_9401-9500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合剩余 C205、A205、W206、S206 映射；C205 与 A205 分别建立独立双门 Coupé、Cabriolet 尺寸组。
* W206 Sedan 与 S206 Wagon 已按官方资料建立尺寸组，后驱、4MATIC、汽油轻混和柴油轻混在本批未形成不同物理外廓。
* 已完成一次机械检查：固定表头正确、109 个 `id` 唯一、18 个尺寸组唯一、全部引用闭合、尺寸和来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：109
* READY 映射：109
* PENDING：0
* 最终尺寸组：18
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16716	16716	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16718	16718	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
15037	15037	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期五门旅行车标准外廓。	READY
100551	100551	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
106454	106454	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
116939	116939	Coupe	C-Class C205	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-01	HIGH	C205双门Coupé标准外廓。	READY
120122	120122	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	HIGH	A205双门Cabriolet标准外廓。	READY
143578	143578	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
143633	143633	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
112354	112354	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
112362	112362	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
120123	120123	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	HIGH	A205双门Cabriolet标准外廓。	READY
143579	143579	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
145529	145529	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
146614	146614	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
106290	106290	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
107474	107474	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
10229	10229	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	W202后期四门轿车标准外廓。	READY
14818	14818	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15721	15721	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16089	16089	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16090	16090	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17375	17375	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17378	17378	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17379	17379	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
57283_prefl	57283	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
57283_facelift	57283	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
57291	57291	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
17131	17131	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
17376	17376	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17377	17377	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
116948	116948	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
116949	116949	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
145132	145132	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
145150	145150	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
5116_prefl	5116	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5116_facelift	5116	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
14815	14815	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15263	15263	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
15719	15719	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16715	16715	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16717	16717	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16719	16719	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
10966	10966	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期五门旅行车标准外廓。	READY
5977_prefl	5977	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5977_facelift	5977	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
15038	15038	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期五门旅行车标准外廓。	READY
100560	100560	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
100751	100751	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
106451	106451	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
108610	108610	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
5758	5758	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
8888	8888	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	W202后期四门轿车标准外廓。	READY
10330	10330	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
14820	14820	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15264	15264	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
15722	15722	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17863	17863	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
17864	17864	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17865	17865	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
54930	54930	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
54942	54942	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	W204更新前四门轿车外廓。	READY
54951	54951	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	S204更新前五门旅行车外廓。	READY
54959	54959	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
59470_prefl	59470	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
59470_facelift	59470	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
59471_prefl	59471	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	HIGH	Ktype跨越2011年外廓更新，拆分前期分支。	READY
59471_facelift	59471	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	Ktype跨越2011年外廓更新，拆分后期分支。	READY
100914	100914	Coupe	C-Class C204	C204	2	EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	HIGH	C204双门Coupé标准外廓。	READY
59441	59441	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	W204更新后四门轿车外廓。	READY
59442	59442	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH	S204更新后五门旅行车外廓。	READY
11079_prefl	11079	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
11079_facelift	11079	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
116936	116936	Coupe	C-Class C205	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-01	HIGH	C205双门Coupé标准外廓。	READY
118792	118792	Coupe	C-Class C205	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-01	HIGH	C205双门Coupé标准外廓。	READY
120130	120130	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	HIGH	A205双门Cabriolet标准外廓。	READY
124381	124381	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	HIGH	A205双门Cabriolet标准外廓。	READY
143580	143580	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
143635	143635	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
155222	155222	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
155225	155225	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
112348	112348	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	W205四门轿车标准外廓。	READY
112365	112365	Wagon	C-Class S205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205五门旅行车标准外廓。	READY
120131	120131	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	HIGH	A205双门Cabriolet标准外廓。	READY
145133	145133	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
145149	145149	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
146615	146615	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
155223	155223	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	HIGH	W206四门轿车标准外廓。	READY
155226	155226	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
155231	155231	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	HIGH	S206五门旅行车标准外廓。	READY
8889	8889	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期五门旅行车标准外廓。	READY
11080_prefl	11080	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
11080_facelift	11080	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
18699	18699	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
18883	18883	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
18884	18884	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
5115_prefl	5115	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5115_facelift	5115	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
15265	15265	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
16720	16720	Coupe	C-Class CL203	CL203	3	EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	HIGH	CL203三门Sports Coupé标准外廓。	READY
17861	17861	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
17862	17862	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
5956_prefl	5956	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	HIGH	Ktype跨越1997年外廓更新，拆分前期分支。	READY
5956_facelift	5956	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	Ktype跨越1997年外廓更新，拆分后期分支。	READY
14816	14816	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
15833	15833	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
16927	16927	Sedan	C-Class W203	W203	4	EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	HIGH	W203四门轿车标准外廓。	READY
16929	16929	Wagon	C-Class S203	S203	5	EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	HIGH	S203五门旅行车标准外廓。	READY
15039	15039	Wagon	C-Class S202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	HIGH	S202后期五门旅行车标准外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_9401-9500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-S203-WAGON-01	4541	1728	1465	Mercedes-Benz Public Archive — C 200 CDI station wagon (S203)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-station-wagon.xhtml?oid=5576
EU-MERCEDES-BENZ-C-KLASSE-CL203-COUPE-01	4343	1728	1406	Mercedes-Benz Public Archive — 203 series C-Class Sports Coupés 2001–2004	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/203-series-C-Class-Sports-Coups-2001---2004.xhtml?oid=453364
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460	Mercedes-Benz Public Archive — C 200 CDI station wagon (S202)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI-station-wagon.xhtml?oid=5559
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Mercedes-Benz C-Class Saloon official brochure	https://www.mercedes-benzcaribbean.com/assets/themes/mb-caribbean/media/vehicles/class-c/sedans/C_Klasse_FL_W205_ePaper_0718_02_ENG_Final.pdf
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Daimler AG Mercedes-Benz C-Class brochure — Estate dimensions	https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-Clase-C-2015-AU.pdf
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-01	4696	1810	1405	Mercedes-Benz UK C-Class Coupé and Cabriolet official brochure	https://mercedes-benz-media.co.uk/assets/documents/original/894-cclasscoupecabrioletbrochure.pdf
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-01	4686	1810	1409	Mercedes-Benz UK C-Class Coupé and Cabriolet official brochure	https://mercedes-benz-media.co.uk/assets/documents/original/894-cclasscoupecabrioletbrochure.pdf
EU-MERCEDES-BENZ-C-KLASSE-W206-SEDAN-01	4751	1820	1437	Mercedes-Benz C-Class Saloon official brochure	https://www.mercedes-benz-mena.com/static/pdfs/c-klasse-w206-epaper-24-2-02-eng.pdf
EU-MERCEDES-BENZ-C-KLASSE-S206-WAGON-01	4751	1820	1455	Mercedes-Benz UK C-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/c-class/overview.html
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427	Mercedes-Benz Public Archive — C 200 CDI (W202)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI.xhtml?oid=5494
EU-MERCEDES-BENZ-C-KLASSE-W203-SEDAN-01	4526	1728	1426	Mercedes-Benz Public Archive — C 200 CDI (W203)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200-CDI.xhtml?oid=5537
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459	Mercedes-Benz Public Archive — C 220 CDI Estate 2007–2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-2007---2009.xhtml?oid=189508161
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Estate 2011–2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-2011---2014-from-2013-C-220-CDI.xhtml?oid=189508213
EU-MERCEDES-BENZ-C-KLASSE-C204-COUPE-01	4590	1770	1403	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Coupé 2011–2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-Coup-2011---2015-from-2013-C-220-CDI-Coup.xhtml?oid=189638968
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1427	Mercedes-Benz Public Archive — C 230 Compressor (W202)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-230-Compressor.xhtml?oid=5524
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460	Mercedes-Benz Public Archive — C 230 station wagon (S202)	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-230-station-wagon.xhtml?oid=5551
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1444	Mercedes-Benz Public Archive — C 220 CDI Saloon 2007–2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-2007---2008-only-for-export-until-2009.xhtml?oid=189266725
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1444	Mercedes-Benz Public Archive — C 220 CDI BlueEFFICIENCY Saloon 2011–2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-220-CDI-BlueEFFICIENCY-2011---2014-from-2013-C-220-CDI.xhtml?oid=189266522
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_9401-9500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（109 行）
- 累计尺寸组：dimension_groups_final.tsv（18 行）

