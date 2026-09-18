# 任务：left18448 第 3001-3100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0031__92d1d615


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 3001-3100 行

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
left18448 第 3001-3100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CADILLAC-ESCALADE-II-SUV-01	5052	2004	1943
EU-CADILLAC-ESCALADE-I-SUV-01	5110	1956	1887

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Cadillac	Escalade	6.0 Hybrid	SUV	Heckantrieb	Benzin/Elektro	Nov 2010	Dec 2013	10493
Cadillac	Escalade	6.0 Hybrid	SUV	Heckantrieb	Benzin/Ethanol/Elektro	Sep 2010	Dec 2013	113785
Cadillac	Escalade	6.0 Hybrid AWD	SUV	Allrad	Benzin/Ethanol/Elektro	Sep 2010	Dec 2013	113787
Cadillac	Escalade	6.2 AWD	SUV	Allrad	Benzin	Sep 2014	Dec 2020	107648
Cadillac	Escalade	6.2 Flexfuel	SUV	Heckantrieb	Benzin/Ethanol	Oct 2006	Dec 2014	10505
Cadillac	Escalade	6.2 Flexfuel AWD	SUV	Allrad	Benzin/Ethanol	Oct 2006	Dec 2014	10506
Cadillac	Escalade	EV AWD	SUV	Allrad	Elektro	Jun 2024	-	159313
Cadillac	Fleetwood	4.1	Stufenheck	Heckantrieb	Benzin	Sep 1982	Dec 1985	36340
Cadillac	Fleetwood	7	Stufenheck	Heckantrieb	Benzin	Sep 1976	Dec 1979	36324
Cadillac	Fleetwood	8.2	Stufenheck	Heckantrieb	Benzin	Sep 1974	Dec 1976	36308
Cadillac	Fleetwood	5.7 D	Coupe	Heckantrieb	Diesel	Sep 1979	Dec 1985	36314
Cadillac	Lyriq	EV AWD	SUV	Allrad	Elektro	Nov 2023	-	157094
Cadillac	Optiq	EV AWD	SUV	Allrad	Elektro	Mar 2025	-	160828
Cadillac	Optiq	V AWD	SUV	Allrad	Elektro	Mar 2025	-	162428
Cadillac	Seville	4.1	Stufenheck	Frontantrieb	Benzin	Sep 1981	Dec 1985	52162
Cadillac	Seville	4.9	Stufenheck	Frontantrieb	Benzin	Jun 1992	Dec 1993	36399
Cadillac	Seville	4.6 SLS V8	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2004	14478
Cadillac	Seville	4.6 STS V8	Stufenheck	Frontantrieb	Benzin	Sep 1997	Sep 2004	14480
Cadillac	Srx	3.6	SUV	Frontantrieb	Benzin	Jan 2012	Apr 2016	55225
Cadillac	Srx	4.6	SUV	Heckantrieb	Benzin	Sep 2003	Dec 2009	36404
Cadillac	Srx	2.8 AWD	SUV	Allrad	Benzin	Jan 2009	Dec 2016	10497
Cadillac	Srx	3.0 AWD	SUV	Allrad	Benzin	Jan 2009	Dec 2016	12025
Cadillac	Srx	3.6 AWD	SUV	Allrad	Benzin	Jul 2004	Dec 2008	18240
Cadillac	Srx	3.6 AWD	SUV	Allrad	Benzin	Oct 2012	Apr 2016	57400
Cadillac	Srx	4.6 AWD	SUV	Allrad	Benzin	Sep 2003	Dec 2009	18241
Cadillac	Sts	4.6	Stufenheck	Heckantrieb	Benzin	Sep 2007	Dec 2010	51071
Cadillac	Sts	4.4 Kompressor AWD	Stufenheck	Allrad	Benzin	Sep 2005	Dec 2007	10507
Cadillac	Sts	4.6 AWD	Stufenheck	Allrad	Benzin	Sep 2007	Dec 2010	51070
Cadillac	Vistiq	EV AWD	SUV	Allrad	Elektro	Jul 2025	-	162490
Cadillac	Xlr	4.6	Cabriolet	Heckantrieb	Benzin	Mar 2004	Sep 2009	17981
Cadillac	Xt4	2.0 AWD	SUV	Allrad	Benzin	Mar 2021	-	145425
Cadillac	Xt4	2.0 D	SUV	Frontantrieb	Diesel	Mar 2021	-	145426
Cadillac	Xt4	2.0 D AWD	SUV	Allrad	Diesel	Mar 2021	-	145427
Cadillac	Xt5	3.6	SUV	Frontantrieb	Benzin	May 2016	-	119844
Cadillac	Xt5	3.6 AWD	SUV	Allrad	Benzin	May 2016	-	119845
Callaway	C12	5.7	Coupe	Heckantrieb	Benzin	Mar 1998	Sep 2003	12602
Callaway	C12	5.7	Cabriolet	Heckantrieb	Benzin	Mar 1998	Sep 2003	12603
Caterham	Seven	0.7	Cabriolet	Heckantrieb	Benzin	Dec 2013	-	108935
Caterham	Seven	0.7	Cabriolet	Heckantrieb	Benzin	Jun 2021	-	145808
Caterham	Seven	1.6	Cabriolet	Heckantrieb	Benzin	Jul 2015	-	118682
Caterham	Seven	1.6	Cabriolet	Heckantrieb	Benzin	Jun 1986	Dec 1991	127267
Caterham	Seven	2	Cabriolet	Heckantrieb	Benzin	May 2015	-	124358
Caterham	Seven	1.8 16 V	Cabriolet	Heckantrieb	Benzin	Oct 1999	-	14648
Cenntro	Logistar 100	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	Sep 2022	-	154940
Cenntro	Logistar 200	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Dec 2021	-	146602
Cenntro	Logistar 200	Electric	Kasten	Heckantrieb	Elektro	Dec 2021	-	146603
Cenntro	Logistar 260	Electric	Kasten	Heckantrieb	Elektro	Jan 2023	-	154772
Cenntro	Logistar 400	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2019	-	146608
Cenntro	Logistar 400	Electric	Kasten	Heckantrieb	Elektro	Jul 2019	-	146609
Cenntro	Metro	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2019	-	146548
Cenntro	Metro	Electric	Kasten	Heckantrieb	Elektro	Jul 2019	-	146549
Cenntro	Neibor 200	Electric	Kasten/Großraumlimousine	Heckantrieb	Elektro	Jul 2021	-	146596
Cenntro	Orv	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jul 2019	-	146586
Changan	X5	1.5	SUV	Frontantrieb	Benzin	Aug 2025	-	802199
Chatenet	Ch40	0.5 D	Schrägheck	Frontantrieb	Diesel	Apr 2018	-	157776
Chatenet	Ch46	0.5 D	Schrägheck	Frontantrieb	Diesel	Mar 2019	-	157777
Chery	Omoda 5	1.6	SUV	Frontantrieb	Benzin	Jul 2022	-	157156
Chery	Omoda 5	1.6	SUV	Frontantrieb	Benzin	Jul 2022	-	800440
Chery	Omoda 5	PRO	SUV	Frontantrieb	Benzin	Jul 2024	-	800478
Chery	Tiggo 4	1.5 Hybrid CSH	SUV	Frontantrieb	Benzin/Elektro	Oct 2025	-	802880
Chery	Tiggo 7	1.6	SUV	Frontantrieb	Benzin	Oct 2025	-	163380
Chery	Tiggo 7	1.6	SUV	Allrad	Benzin	Oct 2025	-	163382
Chery	Tiggo 7	Phev	SUV	Frontantrieb	Benzin/Elektro	Oct 2025	-	162604
Chery	Tiggo 8	1.6	SUV	Frontantrieb	Benzin	Nov 2025	-	163386
Chery	Tiggo 8 plus	1.5 Super Hybrid	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	162590
Chery	Tiggo 9	Phev AWD	SUV	Allrad	Benzin/Elektro	Oct 2025	-	802540
Chevrolet	Alero	2.2	Stufenheck	Frontantrieb	Benzin	Dec 2001	Sep 2004	16671
Chevrolet	Alero	2.4 16V	Stufenheck	Frontantrieb	Benzin	Mar 1999	Sep 2004	11401
Chevrolet	Alero	3.4 V6	Stufenheck	Frontantrieb	Benzin	Mar 1999	Sep 2004	11402
Chevrolet	Astro extended cargo van	4.3	Kasten	Heckantrieb	Benzin	Sep 1994	Dec 2005	36435
Chevrolet	Astro standard cargo van	4.3	Kasten	Heckantrieb	Benzin	Sep 1994	Dec 2005	111219
Chevrolet	Avalanche	5.3	Pick-up	Heckantrieb	Benzin	Sep 2006	Dec 2008	36459
Chevrolet	Avalanche	5.3	Pick-up	Heckantrieb	Benzin	Sep 2001	Dec 2003	36463
Chevrolet	Avalanche	5.3	Pick-up	Heckantrieb	Benzin	Jan 2007	Dec 2013	58082
Chevrolet	Avalanche	5.3 4WD	Pick-up	Allrad	Benzin	Sep 2006	Dec 2008	36460
Chevrolet	Avalanche	5.3 Flexfuel 4WD	Pick-up	Allrad	Benzin/Ethanol	Sep 2006	Dec 2011	50914
Chevrolet	Avalanche	5.3 Flexfuel AWD	Pick-up	Allrad	Benzin/Ethanol	Sep 2006	Dec 2007	121496
Chevrolet	Avalanche	5.3 Flex-fuel AWD	Pick-up	Allrad	Benzin/Ethanol	Jun 2005	Dec 2013	58083
Chevrolet	Aveo	1.2	Schrägheck	Frontantrieb	Benzin	Mar 2011	-	9997
Chevrolet	Aveo	1.2	Schrägheck	Frontantrieb	Benzin	Mar 2011	-	9998
Chevrolet	Aveo	1.2	Stufenheck	Frontantrieb	Benzin	Mar 2011	-	10029
Chevrolet	Aveo	1.2	Stufenheck	Frontantrieb	Benzin	Mar 2011	-	10572
Chevrolet	Aveo	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2011	-	10019
Chevrolet	Aveo	1.4	Stufenheck	Frontantrieb	Benzin	Jul 2011	-	10444
Chevrolet	Aveo	1.6	Schrägheck	Frontantrieb	Benzin	Mar 2011	-	10035
Chevrolet	Aveo	1.6	Stufenheck	Frontantrieb	Benzin	Mar 2011	-	10443
Chevrolet	Aveo	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2012	Dec 2015	57387
Chevrolet	Aveo	1.2 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Nov 2012	Dec 2015	57388
Chevrolet	Aveo	1.3 D	Stufenheck	Frontantrieb	Diesel	Jul 2011	Dec 2015	12030
Chevrolet	Aveo	1.3 D	Schrägheck	Frontantrieb	Diesel	Jul 2011	Dec 2015	12031
Chevrolet	Aveo	1.3 D	Schrägheck	Frontantrieb	Diesel	Jul 2011	Dec 2015	12032
Chevrolet	Aveo	1.3 D	Stufenheck	Frontantrieb	Diesel	Jul 2011	Dec 2015	13977
Chevrolet	Aveo / kalos	1.2	Schrägheck	Frontantrieb	Benzin	Jun 2006	-	55609
Chevrolet	Aveo / kalos	1.2	Schrägheck	Frontantrieb	Benzin	Jan 2004	May 2008	113242
Chevrolet	Aveo / kalos	1.4	Schrägheck	Frontantrieb	Benzin	Mar 2005	May 2008	18531
Chevrolet	Aveo / kalos	1.4	Stufenheck	Frontantrieb	Benzin	May 2003	May 2008	57132
Chevrolet	Aveo / kalos	1.5	Stufenheck	Frontantrieb	Benzin	Oct 2004	May 2006	128219
Chevrolet	Aveo / kalos	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Apr 2008	Dec 2011	55439
Chevrolet	Aveo / kalos	1.2 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2009	-	57389
Chevrolet	Aveo / kalos	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jun 2008	Nov 2012	118685


--- Round 1 / 首次发送 ---
## 更新点

* 首批完成 4 个新尺寸组：Cadillac LYRIQ、普通版 OPTIQ、VISTIQ、XT5；共闭合 5 个 Ktype，其中 XT5 前驱和四驱复用同一物理尺寸组。官方资料均提供完整三维，宽度采用不含后视镜口径。([凯迪拉克新闻中心][1])
* 暂不创建 Escalade IV、Escalade IQ 和 OPTIQ-V 尺寸组：Escalade IV 同代官方资料存在两套三维；Escalade IQ 官方仅提供含镜及后视镜折叠宽度；OPTIQ-V 尚缺不含后视镜宽度直接值。([凯迪拉克新闻中心][2])
* 未改写任务锁定的两个既有 Escalade 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：5
* 已明确 PENDING：3
* 尚待聚类核对：92
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
107648	107648	SUV	Escalade IV		5		MEDIUM		PENDING: 同代际官方资料给出两套三维，市场或年份口径冲突未闭合。
159313	159313	SUV	Escalade IQ I		5		MEDIUM		PENDING: 官方仅提供含镜及后视镜折叠宽度，缺少不含后视镜车身宽度。
157094	157094	SUV	LYRIQ I		5	EU-CADILLAC-LYRIQ-I-SUV-01	HIGH		READY
160828	160828	SUV	OPTIQ I		5	EU-CADILLAC-OPTIQ-I-SUV-01	HIGH		READY
162428	162428	SUV	OPTIQ-V I		5		MEDIUM	V-Series外部套件需独立确认。	PENDING: 尚缺该版本不含后视镜宽度直接值，不能直接复用普通OPTIQ组。
162490	162490	SUV	VISTIQ I		5	EU-CADILLAC-VISTIQ-I-SUV-01	HIGH		READY
119844	119844	SUV	XT5 I		5	EU-CADILLAC-XT5-I-SUV-01	HIGH		READY
119845	119845	SUV	XT5 I		5	EU-CADILLAC-XT5-I-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-LYRIQ-I-SUV-01	4996	1977	1623	Cadillac Newsroom 2023 LYRIQ preliminary specifications	https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2021/apr/0421-lyriq.html
EU-CADILLAC-OPTIQ-I-SUV-01	4821	1913	1643	Cadillac 2026 OPTIQ official configurator specifications	https://www.cadillac.com/shopping/configurator/electric/2026/optiq/optiq/compare
EU-CADILLAC-VISTIQ-I-SUV-01	5222	2026	1804	Cadillac Newsroom 2026 VISTIQ specifications	https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2024/nov/1112-vistiq.html
EU-CADILLAC-XT5-I-SUV-01	4815	1903	1675	Cadillac XT5 Specifications Europe	https://media.gmc.com/content/dam/Media/documents/INTL/cadillac/2019/crossover-suv/xt5/Tech-Data-Cadillac-XT5-EN.pdf
```

## 下一步优先处理

1. 闭合 Escalade III Hybrid 与 6.2 Flexfuel 的尺寸差异和来源取整口径。
2. 聚类处理 Fleetwood、Seville、SRX、STS、XLR 等历史 Cadillac 车型。
3. 继续处理 XT4、Callaway、Caterham 和 Cenntro 车型组。

推进信号：CONTINUE

[1]: https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2021/apr/0421-lyriq.html "2023 Cadillac LYRIQ Debuts, Heralding an All-Electric Future"
[2]: https://media.cadillac.com/content/dam/Media/documents/INTL/cadillac/2019/crossover-suv/escalade/Tech-Data-Cadillac-Escalade-FR.pdf "Microsoft Word - Cadillac Escalade TechData FR 102018.docx"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 Escalade III、XT4 I、SRX I/II、STS I、STS-V 和 XLR I 共 7 个尺寸组，新增 19 条 READY 映射；相同驱动或动力版本直接复用尺寸组，STS-V 因外廓尺寸不同独立建组。([Edmunds][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：24
* PENDING 映射：76（已落盘具体 PENDING 3，尚待聚类核对 73）
* 已确认尺寸组：11
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10493	10493	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
113785	113785	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
113787	113787	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
10505	10505	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
10506	10506	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
55225	55225	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
36404	36404	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
10497	10497	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
12025	12025	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
18240	18240	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
57400	57400	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
18241	18241	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
51071	51071	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-01	HIGH		READY
10507	10507	Sedan	STS I		4	EU-CADILLAC-STS-V-I-SEDAN-01	HIGH	V-Series外廓独立。	READY
51070	51070	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-01	HIGH		READY
17981	17981	Convertible	XLR I		2	EU-CADILLAC-XLR-I-CONVERTIBLE-01	HIGH		READY
145425	145425	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
145426	145426	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
145427	145427	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-ESCALADE-III-SUV-01	5144	2007	1928	Edmunds 2011 Cadillac Escalade and Escalade Hybrid specifications	https://www.edmunds.com/cadillac/escalade/2011/suv/st-101352619/features-specs/;https://www.edmunds.com/cadillac/escalade-hybrid/2011/suv/features-specs/
EU-CADILLAC-SRX-I-SUV-01	4950	1844	1722	Edmunds 2008 Cadillac SRX specifications	https://www.edmunds.com/cadillac/srx/2008/suv/features-specs/
EU-CADILLAC-SRX-II-SUV-01	4834	1910	1669	Edmunds 2013 Cadillac SRX specifications	https://www.edmunds.com/cadillac/srx/2013/features-specs/
EU-CADILLAC-STS-I-SEDAN-01	4996	1844	1463	Edmunds 2008 Cadillac STS specifications	https://www.edmunds.com/cadillac/sts/2008/features-specs/
EU-CADILLAC-STS-V-I-SEDAN-01	5019	1844	1478	Edmunds 2007 Cadillac STS-V specifications	https://www.edmunds.com/cadillac/sts-v/2007/sedan/features-specs/
EU-CADILLAC-XLR-I-CONVERTIBLE-01	4514	1836	1280	Edmunds 2008 Cadillac XLR specifications	https://www.edmunds.com/cadillac/xlr/2008/features-specs/
EU-CADILLAC-XT4-I-SUV-01	4593	1881	1612	Cadillac XT4 Diesel official technical data	https://media.cadillac.com/content/dam/Media/documents/INTL/cadillac/2021/crossovers-suvs/xt4/Cadillac%20XT4%20TechData%20EN_Diesel.pdf
```

## 下一步优先处理

1. 闭合 Fleetwood 和 Seville 各代轿车、Fleetwood Coupe 的物理分支。
2. 处理 Callaway C12 Coupe/Convertible 与 Caterham Seven 外廓。
3. 批量处理 Cenntro 商用车的厢式、底盘及货箱分支。

推进信号：CONTINUE

[1]: https://www.edmunds.com/cadillac/escalade/2011/suv/st-101352619/features-specs/?utm_source=chatgpt.com "Used 2011 Cadillac Escalade SUV Base Specs & Features | Edmunds"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Fleetwood Brougham V、Seville II、Seville IV 欧洲版、Seville V 欧洲版四个历史 Cadillac 尺寸组，共完成 5 个 Ktype。([汽车目录][1])
* 闭合 Cenntro Logistar 100、Logistar 260 与 ORV 三个尺寸组，共完成 3 个 Ktype；ORV 后续以 TeeMak 名称延续，但当前映射保留输入车型名称。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：32
* PENDING 映射：68
* 已确认尺寸组：18
* 本轮新增 READY：8
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
36340	36340	Sedan	Fleetwood Brougham V		4	EU-CADILLAC-FLEETWOOD-BROUGHAM-V-SEDAN-01	HIGH		READY
52162	52162	Sedan	Seville II		4	EU-CADILLAC-SEVILLE-II-SEDAN-01	HIGH		READY
36399	36399	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-01	HIGH	欧洲出口4.9车型外廓。	READY
14478	14478	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH	SLS欧洲出口外廓。	READY
14480	14480	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH	STS欧洲出口外廓。	READY
154940	154940	Van	Logistar 100 I			EU-CENNTRO-LOGISTAR-100-I-VAN-01	HIGH		READY
154772	154772	Van	Logistar 260 I			EU-CENNTRO-LOGISTAR-260-I-VAN-01	HIGH		READY
146586	146586	Pickup	ORV I		2	EU-CENNTRO-ORV-I-PICKUP-01	MEDIUM	该车型后续以TeeMak名称延续。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-FLEETWOOD-BROUGHAM-V-SEDAN-01	5613	1913	1440	Automobile-Catalog 1983 Cadillac Fleetwood Brougham Sedan 4.1	https://www.automobile-catalog.com/car/1983/331250/cadillac_fleetwood_brougham_sedan_4_1l_v-8_ht-4100.html
EU-CADILLAC-SEVILLE-II-SEDAN-01	5202	1801	1379	Automobile-Catalog 1983 Cadillac Seville 4.1	https://www.automobile-catalog.com/car/1983/330545/cadillac_seville_4_1l_v-8_ht-4100.html
EU-CADILLAC-SEVILLE-IV-SEDAN-01	5189	1887	1369	Automobile-Catalog 1992 Cadillac Seville STS 4.9 Europe	https://www.automobile-catalog.com/car/1992/333515/cadillac_seville_sts.html
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1897	1428	Automobile-Catalog 1998 Cadillac Seville SLS Europe;Automobile-Catalog 1998 Cadillac Seville STS Europe	https://www.automobile-catalog.com/car/1998/334070/cadillac_seville_sls.html;https://www.automobile-catalog.com/car/1998/334085/cadillac_seville_sts.html
EU-CENNTRO-LOGISTAR-100-I-VAN-01	3664	1610	1689	Cenntro Logistar 100 technical specifications	https://cenntro.nl/media/pages/modellen/logistar-100/25e076d43a-1699967916/2022-09-15_en_flyer_cenntrologistar100.pdf
EU-CENNTRO-LOGISTAR-260-I-VAN-01	5457	1850	2046	Cenntro Logistar 260 official specifications	https://cenntroauto.com/vehicles/logistar-260/
EU-CENNTRO-ORV-I-PICKUP-01	4010	1600	2150	Cenntro TeeMak ORV official specifications	https://cenntroauto.com/vehicles/orv/
```

## 下一步优先处理

1. 拆分并闭合其余 Fleetwood 7.0、8.2 和柴油 Coupe 的跨年份外廓。
2. 处理 Callaway C12 Coupe/Convertible 与 Caterham Seven 各车身宽度分支。
3. 批量闭合 Chery Omoda 5、Tiggo 系列和 Chevrolet Aveo 同代复用关系。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/331250/cadillac_fleetwood_brougham_sedan_4_1l_v-8_ht-4100.html?utm_source=chatgpt.com "1983 Cadillac Fleetwood Brougham Sedan 4.1L V-8 HT-4100 Specs Review (100.5 kW / 137 PS / 135 hp) (since September 1982 for North America )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Chery Omoda 5、Tiggo 4 CSH 和欧洲版 Tiggo 7 三个尺寸组，完成 7 个 Ktype；同代动力及驱动版本直接复用对应外廓。([奇瑞国际][1])
* 闭合 Chevrolet Aveo II（T300）五门 Hatchback 与四门 Sedan 两个尺寸组，完成 14 个 Ktype。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：53
* PENDING 映射：47
* 已确认尺寸组：23
* 本轮新增 READY：21
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
157156	157156	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
800440	800440	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
800478	800478	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
802880	802880	SUV	Tiggo 4 I		5	EU-CHERY-TIGGO-4-I-SUV-01	HIGH		READY
163380	163380	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
163382	163382	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
162604	162604	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
9997	9997	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
9998	9998	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10029	10029	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10572	10572	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10019	10019	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10444	10444	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10035	10035	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10443	10443	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
57387	57387	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
57388	57388	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
12030	12030	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
12031	12031	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
12032	12032	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
13977	13977	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHERY-OMODA-5-I-SUV-01	4400	1830	1588	Chery International OMODA official specifications	https://www.cheryinternational.com/omoda/
EU-CHERY-TIGGO-4-I-SUV-01	4320	1831	1652	Chery International TIGGO 4 CSH official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo4_csh/index.shtml
EU-CHERY-TIGGO-7-II-SUV-01	4553	1862	1696	Chery International TIGGO 7 CSH official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo7_csh/index.shtml
EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	4039	1735	1517	Automobile-Catalog 2011 Chevrolet Aveo 1.4 LT Hatchback	https://www.automobile-catalog.com/car/2011/1568495/chevrolet_aveo_1_4_lt_hatchback.html
EU-CHEVROLET-AVEO-II-T300-SEDAN-01	4399	1735	1517	Automobile-Catalog 2012 Chevrolet Aveo 1.4 LT Sedan	https://www.automobile-catalog.com/car/2012/1568630/chevrolet_aveo_1_4_lt_sedan.html
```

## 下一步优先处理

1. 批量闭合 Chevrolet Aveo/Kalos 第一代 Hatchback 与 Sedan 分支。
2. 处理 Chevrolet Avalanche 两代及 Astro 标准轴距、加长轴距货车。
3. 继续闭合 Chery Tiggo 8、Tiggo 8 Plus、Tiggo 9，以及剩余 Cadillac PENDING 项。

推进信号：CONTINUE

[1]: https://www.cheryinternational.com/omoda/?utm_source=chatgpt.com "OMODA is an automotive brand | Official site"
[2]: https://www.automobile-catalog.com/car/2011/1568495/chevrolet_aveo_1_4_lt_hatchback.html?utm_source=chatgpt.com "2011 Chevrolet Aveo 1.4 LT Hatchback (man. 5)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Chevrolet Alero 欧洲版尺寸组，3 个动力 Ktype 复用同一四门 Sedan 外廓。([汽车目录][1])
* 闭合 Chevrolet Avalanche 第一代早期、第一代后期及第二代 3 个尺寸组；跨越两代的 Ktype `58083` 拆分为两个派生映射。([Edmunds][2])
* 闭合 Aveo/Kalos T200、T250 的 Sedan、三门 Hatchback 和五门 Hatchback 共 6 个尺寸组，8 个 Ktype 完整拆分门数分支。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* READY 映射行：77
* PENDING/尚待处理 Ktype：29
* 已确认尺寸组：33
* 本轮新增 READY Ktype：18
* 本轮新增 READY 映射行：24
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16671	16671	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
11401	11401	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
11402	11402	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
36459	36459	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
36463	36463	Pickup	Avalanche I		4	EU-CHEVROLET-AVALANCHE-I-PICKUP-PREFL-01	HIGH	第一代早期外廓。	READY
58082	58082	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
36460	36460	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
50914	50914	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
121496	121496	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
58083_gen1	58083	Pickup	Avalanche I		4	EU-CHEVROLET-AVALANCHE-I-PICKUP-FACELIFT-01	HIGH	跨代Ktype的第一代后期外廓。	READY
58083_gen2	58083	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH	跨代Ktype的第二代外廓。	READY
55609_3dr	55609	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
55609_5dr	55609	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
113242_3dr	113242	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
113242_5dr	113242	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
18531_3dr	18531	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
18531_5dr	18531	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
57132	57132	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH		READY
128219	128219	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH		READY
55439_3dr	55439	Hatchback	Aveo T250	T250	3	EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
55439_5dr	55439	Hatchback	Aveo T250	T250	5	EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
57389	57389	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-01	HIGH		READY
118685_3dr	118685	Hatchback	Aveo T250	T250	3	EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
118685_5dr	118685	Hatchback	Aveo T250	T250	5	EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-ALERO-I-SEDAN-01	4742	1780	1399	Automobile-Catalog 1999 Chevrolet Alero 2.4 16V Europe	https://www.automobile-catalog.com/car/1999/2406875/chevrolet_alero_2_4_16v.html
EU-CHEVROLET-AVALANCHE-I-PICKUP-PREFL-01	5631	2027	1862	Edmunds 2003 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2003/features-specs/
EU-CHEVROLET-AVALANCHE-I-PICKUP-FACELIFT-01	5629	2027	1869	Edmunds 2006 Chevrolet Avalanche 1500 specifications	https://www.edmunds.com/chevrolet/avalanche/2006/st-100580431/features-specs/
EU-CHEVROLET-AVALANCHE-II-PICKUP-01	5621	2009	1946	Edmunds 2011 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2011/features-specs/
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	3880	1670	1495	Automobile-Catalog 2006 Chevrolet Kalos 1.2 SE Hatchback Europe	https://www.automobile-catalog.com/car/2006/559025/chevrolet_kalos_1_2_se_hatchback.html
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	3880	1670	1495	Automobile-Catalog 2006 Chevrolet Kalos 1.2 SE Hatchback Europe	https://www.automobile-catalog.com/car/2006/559025/chevrolet_kalos_1_2_se_hatchback.html
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495	Automobile-Catalog 2005 Chevrolet Kalos 1.4 16V SX Sedan Europe	https://www.automobile-catalog.com/car/2005/559085/chevrolet_kalos_1_4_16v_sx_sedan_automatic.html
EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	3920	1680	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.2 Hatchback Europe	https://www.automobile-catalog.com/car/2009/1209830/chevrolet_aveo_1_2_hatchback.html
EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	3920	1680	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.2 Hatchback Europe	https://www.automobile-catalog.com/car/2009/1209830/chevrolet_aveo_1_2_hatchback.html
EU-CHEVROLET-AVEO-T250-SEDAN-01	4310	1710	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.4 LT Sedan Europe	https://www.automobile-catalog.com/car/2009/559175/chevrolet_aveo_1_4_lt_sedan.html
```

## 下一步优先处理

1. 拆分 Astro 1995—2005 年间发生变化的宽度和高度外廓，避免把不同年份尺寸强行合并。([Edmunds][4])
2. 闭合 Callaway C12 Coupe/Convertible 与 Caterham Seven 各代宽体分支。
3. 批量处理 Cenntro Logistar 200/400、Metro、Neibor 200。
4. 处理剩余 Changan、Chatenet、Chery 车型及 3 条 Cadillac PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/2406875/chevrolet_alero_2_4_16v.html?utm_source=chatgpt.com "2000 Chevrolet Alero 2.4 16V Specs Review (104 kW ..."
[2]: https://www.edmunds.com/chevrolet/avalanche/2003/features-specs/?utm_source=chatgpt.com "Used 2003 Chevrolet Avalanche Specs & Features | Edmunds"
[3]: https://www.automobile-catalog.com/car/2004/558935/daewoo_kalos_1_2_se_hatchback.html?utm_source=chatgpt.com "2004 Daewoo Kalos 1.2 SE Hatchback (man. 5)"
[4]: https://www.edmunds.com/chevrolet/astro-cargo/1995/features-specs/?utm_source=chatgpt.com "Used 1995 Chevrolet Astro Cargo Specs & Features | Edmunds"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Callaway C12 Coupe 与 Cabriolet 两个车身分支；虽然三维相同，但 BodyStyle 不同，分别建立独立尺寸组。([汽车数据网][1])
* 闭合 Caterham Seven 0.7 的两个时期分支：2013 年末车型对应 Seven 160 窄体外廓，2021 年车型对应 Seven 170 外廓。([ケータハム JAPAN 公式サイト][2])
* 闭合 Cenntro Logistar 200 Pickup、Logistar 200 Van、Logistar 400 Van 和 Metro Van 四个商用车尺寸组。([Cenntro Europe][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射行：85
* PENDING/尚待处理 Ktype：21
* 已确认尺寸组：41
* 本轮新增 READY Ktype：8
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12602	12602	Coupe	C12 I		2	EU-CALLAWAY-C12-I-COUPE-01	HIGH		READY
12603	12603	Convertible	C12 I		2	EU-CALLAWAY-C12-I-CONVERTIBLE-01	HIGH		READY
108935	108935	Convertible	Seven 160		2	EU-CATERHAM-SEVEN-160-CONVERTIBLE-01	HIGH	2013年末Seven 130后更名为Seven 160；同一窄体外廓。	READY
145808	145808	Convertible	Seven 170		2	EU-CATERHAM-SEVEN-170-CONVERTIBLE-01	HIGH		READY
146602	146602	Pickup	Logistar 200 I		2	EU-CENNTRO-LOGISTAR-200-I-PICKUP-01	HIGH		READY
146603	146603	Van	Logistar 200 I			EU-CENNTRO-LOGISTAR-200-I-VAN-01	HIGH		READY
146609	146609	Van	Logistar 400 I			EU-CENNTRO-LOGISTAR-400-I-VAN-01	HIGH		READY
146549	146549	Van	Metro I			EU-CENNTRO-METRO-I-VAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CALLAWAY-C12-I-COUPE-01	4850	2000	1200	Auto-Data Callaway C12 Coupe;Callaway Cars C12 official project page	https://www.auto-data.net/en/callaway-c12-coupe-generation-2554;https://www.callawaycars.com/homepage/the-company/callaway-c-projects/c12/
EU-CALLAWAY-C12-I-CONVERTIBLE-01	4850	2000	1200	Auto-Data Callaway C12 Cabrio;Callaway Cars C12 official project page	https://www.auto-data.net/en/callaway-c12-cabrio-generation-2553;https://www.callawaycars.com/homepage/the-company/callaway-c-projects/c12/
EU-CATERHAM-SEVEN-160-CONVERTIBLE-01	3100	1470	1090	Caterham Cars Japan Seven 160 official specifications	https://www.caterham-cars.jp/news/2014/
EU-CATERHAM-SEVEN-170-CONVERTIBLE-01	3180	1470	1090	Caterham Cars Seven 170 official specifications	https://caterhamcars.com/tw/models/the-range/seven-170
EU-CENNTRO-LOGISTAR-200-I-PICKUP-01	4770	1640	1991	Cenntro Europe Logistar 200 official technical data	https://cenntro-europe.com/wp-content/uploads/2023/05/DE_CENN_200_ALL-1.pdf
EU-CENNTRO-LOGISTAR-200-I-VAN-01	4421	1677	1902	Cenntro Logistar 200 official technical specifications	https://www.cenntro.nl/media/pages/modellen/logistar-200-van/274cf7a578-1698766079/logistar-specs.pdf
EU-CENNTRO-LOGISTAR-400-I-VAN-01	5994	2057	2718	Cenntro Logistar 400 official specifications	https://cenntroauto.com/vehicles/logistar-400/
EU-CENNTRO-METRO-I-VAN-01	3910	1400	1905	Cenntro Metro official specifications	https://cenntroauto.com/vehicles/metro/
```

## 下一步优先处理

1. 闭合 Logistar 400 底盘、Metro 底盘及 Neibor 200 的具体车身外廓。
2. 拆分 Caterham Seven 1.6、1.8 和 2.0 的 S3、SV及历史窄体分支。
3. 处理 Fleetwood 7.0、8.2、柴油 Coupe，以及 Changan、Chatenet、Chery 剩余车型。
4. 最后集中消除 Escalade IV、Escalade IQ、OPTIQ-V 和 Astro 的剩余阻塞项。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/callaway-c12-cabrio-generation-2553 "Callaway C12 Cabrio | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.caterham-cars.jp/news/2014/ "2014 | ケータハム JAPAN"
[3]: https://cenntro-europe.com/wp-content/uploads/2023/05/DE_CENN_200_ALL-1.pdf?utm_source=chatgpt.com "LOGISTAR 200  VAN"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Cenntro Neibor 200 整车外廓，完成 1 个 Ktype。([Cenntro][1])
* 闭合 Chatenet CH40、CH46 两个独立 Hatchback 尺寸组，完成 2 个 Ktype。
* 闭合 Chery Tiggo 9 PHEV 欧洲规格尺寸组，完成 1 个 Ktype。([奇瑞汽车][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* READY 映射行：89
* PENDING/尚待处理 Ktype：17
* 已确认尺寸组：45
* 本轮新增 READY Ktype：4
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146596	146596	Van	Neibor 200 I			EU-CENNTRO-NEIBOR-200-I-VAN-01	MEDIUM		READY
157776	157776	Hatchback	CH40 I		3	EU-CHATENET-CH40-I-HATCHBACK-01	HIGH		READY
157777	157777	Hatchback	CH46 I		3	EU-CHATENET-CH46-I-HATCHBACK-01	HIGH		READY
802540	802540	SUV	Tiggo 9 I		5	EU-CHERY-TIGGO-9-I-SUV-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CENNTRO-NEIBOR-200-I-VAN-01	3500	1480	1490	Cenntro Neibor 200 regional product specifications	https://electricvan-inc.fr/products.html
EU-CHATENET-CH40-I-HATCHBACK-01	2977	1492	1457	Automobiles Chatenet CH40-CH46 official owner notice	https://www.automobiles-chatenet.com/service-apres-vente.html?file=files%2Fpack%2Fcontenu%2FPDF-technique%2F2025%2FNOTICE+CH40-CH46+V2.pdf
EU-CHATENET-CH46-I-HATCHBACK-01	2882	1500	1453	Automobiles Chatenet CH40-CH46 official owner notice	https://www.automobiles-chatenet.com/service-apres-vente.html?file=files%2Fpack%2Fcontenu%2FPDF-technique%2F2025%2FNOTICE+CH40-CH46+V2.pdf
EU-CHERY-TIGGO-9-I-SUV-01	4810	1925	1741	Chery Lithuania TIGGO 9 PHEV official specifications	https://cherymotor.lt/en/tiggo-9-phev/
```

## 下一步优先处理

1. 闭合 Cenntro Logistar 400 底盘、Metro 底盘的完整整车外廓。
2. 处理 Caterham Seven 1.6、1.8、2.0 的标准底盘、SV 与历史窄体边界。
3. 处理 Fleetwood 7.0、8.2、柴油 Coupe 与 Chevrolet Astro 标准/加长货车。
4. 集中消除 Escalade IV、Escalade IQ、OPTIQ-V、Changan X5 和 Tiggo 8 系列的剩余阻塞项。

推进信号：CONTINUE

[1]: https://electricvan-inc.fr/products.html "Véhicules Utilitaires électriques | Utilitaire électrique | Cenntro"
[2]: https://cherymotor.lt/en/tiggo-9-phev/?utm_source=chatgpt.com "Chery Tiggo 9 PHEV – a comfortable powerful SUV | Chery Lietuva"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Fleetwood Brougham Coupe、Changan X5 Plus、Chery Tiggo 8 欧洲版、Chevrolet Astro II Cargo 与 Cenntro Metro Pickup 共 5 个尺寸组，新增 7 个 READY Ktype。([汽车目录][1])
* Tiggo 8 1.6 与 Tiggo 8 Plus Super Hybrid 共用当前欧洲版外廓；Astro 两个输入名称均关联 1995—2005 年第二代 Cargo 外廓。([Chery UK][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：96
* PENDING/尚待处理 Ktype：10
* 已确认尺寸组：50
* 本轮新增 READY Ktype：7
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
36314	36314	Coupe	Fleetwood Brougham V		2	EU-CADILLAC-FLEETWOOD-BROUGHAM-V-COUPE-01	HIGH		READY
146548	146548	Pickup	Metro I		2	EU-CENNTRO-METRO-I-PICKUP-01	MEDIUM		READY
802199	802199	SUV	X5 Plus I		5	EU-CHANGAN-X5-PLUS-I-SUV-01	MEDIUM		READY
163386	163386	SUV	Tiggo 8 I facelift		5	EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	HIGH		READY
162590	162590	SUV	Tiggo 8 I facelift		5	EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	HIGH		READY
36435	36435	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	HIGH	1995—2005第二代Cargo外廓。	READY
111219	111219	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	HIGH	1995—2005第二代Cargo外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-FLEETWOOD-BROUGHAM-V-COUPE-01	5613	1915	1387	Automobile-Catalog 1982 Cadillac Fleetwood Brougham Coupe 5.7 Diesel	https://www.automobile-catalog.com/car/1982/331040/cadillac_fleetwood_brougham_coupe_5_7l_v-8_diesel.html
EU-CENNTRO-METRO-I-PICKUP-01	3700	1400	1905	Cenntro Metro electric utility truck regional specifications	https://electricvan-inc.com/1-metro-series-electric-vehicle.html
EU-CHANGAN-X5-PLUS-I-SUV-01	4540	1860	1620	AutoCango 2025 Changan X5 Plus specifications	https://www.autocango.com/carspecs-detail/ChangAn-X5-PLUS-BXND3W
EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	4725	1860	1705	Chery International Tiggo 8 official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo8proe/index.shtml
EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	4821	1969	1905	Edmunds 2005 Chevrolet Astro Cargo specifications	https://www.edmunds.com/chevrolet/astro-cargo/2005/features-specs/
```

## 下一步优先处理

1. 闭合 Caterham Seven 剩余 4 个 Ktype，并按标准 S3、宽体 S5/SV 的真实外廓边界拆分。
2. 处理 Fleetwood 7.0、8.2 与 Logistar 400 底盘车。
3. 最后集中消除 Escalade IV、Escalade IQ、OPTIQ-V 三个 Cadillac 阻塞项。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1982/331040/cadillac_fleetwood_brougham_coupe_5_7l_v-8_diesel.html?utm_source=chatgpt.com "1982 Cadillac Fleetwood Brougham Coupe 5.7L V-8 Diesel (aut. 3)"
[2]: https://www.cherycar.co.uk/models/tiggo-8?utm_source=chatgpt.com "Explore the TIGGO 8 our 7 seater family SUV"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_3001-3100_ktype_dimension_mapping_final.tsv
- left18448_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合最后 10 个 Ktype：Escalade IV、Escalade IQ、OPTIQ-V、两代历史 Fleetwood、4 个 Caterham Seven 版本及 Logistar 400 底盘车；对应新增 10 个尺寸组。Escalade IQ 与 OPTIQ-V 已补齐不含后视镜宽度。([Edmunds][1])
* Fleetwood 历史外廓、Caterham 各时期标准车身以及 Logistar 400 标准整车外廓均已闭合。([汽车目录][2])
* 已完成最终机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，映射引用完全闭合，无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：106
* PENDING：0
* DIMENSION_GROUP：60
* 全部映射和尺寸组已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10493	10493	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
113785	113785	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
113787	113787	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
107648	107648	SUV	Escalade IV		5	EU-CADILLAC-ESCALADE-IV-SUV-01	HIGH		READY
10505	10505	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
10506	10506	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH		READY
159313	159313	SUV	Escalade IQ I		5	EU-CADILLAC-ESCALADE-IQ-I-SUV-01	HIGH		READY
36340	36340	Sedan	Fleetwood Brougham V		4	EU-CADILLAC-FLEETWOOD-BROUGHAM-V-SEDAN-01	HIGH		READY
36324	36324	Sedan	Fleetwood Brougham 1977-1979		4	EU-CADILLAC-FLEETWOOD-BROUGHAM-1977-SEDAN-01	HIGH		READY
36308	36308	Sedan	Fleetwood Sixty Special 1971-1976		4	EU-CADILLAC-FLEETWOOD-SIXTY-SPECIAL-1971-SEDAN-01	HIGH		READY
36314	36314	Coupe	Fleetwood Brougham V		2	EU-CADILLAC-FLEETWOOD-BROUGHAM-V-COUPE-01	HIGH		READY
157094	157094	SUV	LYRIQ I		5	EU-CADILLAC-LYRIQ-I-SUV-01	HIGH		READY
160828	160828	SUV	OPTIQ I		5	EU-CADILLAC-OPTIQ-I-SUV-01	HIGH		READY
162428	162428	SUV	OPTIQ-V I		5	EU-CADILLAC-OPTIQ-V-I-SUV-01	HIGH	V-Series外廓独立。	READY
52162	52162	Sedan	Seville II		4	EU-CADILLAC-SEVILLE-II-SEDAN-01	HIGH		READY
36399	36399	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-01	HIGH	欧洲出口4.9车型外廓。	READY
14478	14478	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH	SLS欧洲出口外廓。	READY
14480	14480	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH	STS欧洲出口外廓。	READY
55225	55225	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
36404	36404	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
10497	10497	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
12025	12025	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
18240	18240	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
57400	57400	SUV	SRX II		5	EU-CADILLAC-SRX-II-SUV-01	HIGH		READY
18241	18241	SUV	SRX I		5	EU-CADILLAC-SRX-I-SUV-01	HIGH		READY
51071	51071	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-01	HIGH		READY
10507	10507	Sedan	STS I		4	EU-CADILLAC-STS-V-I-SEDAN-01	HIGH	V-Series外廓独立。	READY
51070	51070	Sedan	STS I		4	EU-CADILLAC-STS-I-SEDAN-01	HIGH		READY
162490	162490	SUV	VISTIQ I		5	EU-CADILLAC-VISTIQ-I-SUV-01	HIGH		READY
17981	17981	Convertible	XLR I		2	EU-CADILLAC-XLR-I-CONVERTIBLE-01	HIGH		READY
145425	145425	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
145426	145426	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
145427	145427	SUV	XT4 I		5	EU-CADILLAC-XT4-I-SUV-01	HIGH		READY
119844	119844	SUV	XT5 I		5	EU-CADILLAC-XT5-I-SUV-01	HIGH		READY
119845	119845	SUV	XT5 I		5	EU-CADILLAC-XT5-I-SUV-01	HIGH		READY
12602	12602	Coupe	C12 I		2	EU-CALLAWAY-C12-I-COUPE-01	HIGH		READY
12603	12603	Convertible	C12 I		2	EU-CALLAWAY-C12-I-CONVERTIBLE-01	HIGH		READY
108935	108935	Convertible	Seven 160		2	EU-CATERHAM-SEVEN-160-CONVERTIBLE-01	HIGH	2013年末Seven 130后更名为Seven 160；同一窄体外廓。	READY
145808	145808	Convertible	Seven 170		2	EU-CATERHAM-SEVEN-170-CONVERTIBLE-01	HIGH		READY
118682	118682	Convertible	Seven 275		2	EU-CATERHAM-SEVEN-275-CONVERTIBLE-01	HIGH		READY
127267	127267	Convertible	Super Seven 1600		2	EU-CATERHAM-SUPER-SEVEN-1600-CONVERTIBLE-01	HIGH		READY
124358	124358	Convertible	Seven 420		2	EU-CATERHAM-SEVEN-420-CONVERTIBLE-01	HIGH		READY
14648	14648	Convertible	Seven 1.8 K-Series		2	EU-CATERHAM-SEVEN-1-8-K-SERIES-CONVERTIBLE-01	MEDIUM		READY
154940	154940	Van	Logistar 100 I			EU-CENNTRO-LOGISTAR-100-I-VAN-01	HIGH		READY
146602	146602	Pickup	Logistar 200 I		2	EU-CENNTRO-LOGISTAR-200-I-PICKUP-01	HIGH		READY
146603	146603	Van	Logistar 200 I			EU-CENNTRO-LOGISTAR-200-I-VAN-01	HIGH		READY
154772	154772	Van	Logistar 260 I			EU-CENNTRO-LOGISTAR-260-I-VAN-01	HIGH		READY
146608	146608	Pickup	Logistar 400 I		2	EU-CENNTRO-LOGISTAR-400-I-PICKUP-01	MEDIUM	底盘/上装车型按官方标准整车外廓落盘。	READY
146609	146609	Van	Logistar 400 I			EU-CENNTRO-LOGISTAR-400-I-VAN-01	HIGH		READY
146548	146548	Pickup	Metro I		2	EU-CENNTRO-METRO-I-PICKUP-01	MEDIUM		READY
146549	146549	Van	Metro I			EU-CENNTRO-METRO-I-VAN-01	HIGH		READY
146596	146596	Van	Neibor 200 I			EU-CENNTRO-NEIBOR-200-I-VAN-01	MEDIUM		READY
146586	146586	Pickup	ORV I		2	EU-CENNTRO-ORV-I-PICKUP-01	MEDIUM	该车型后续以TeeMak名称延续。	READY
802199	802199	SUV	X5 Plus I		5	EU-CHANGAN-X5-PLUS-I-SUV-01	MEDIUM		READY
157776	157776	Hatchback	CH40 I		3	EU-CHATENET-CH40-I-HATCHBACK-01	HIGH		READY
157777	157777	Hatchback	CH46 I		3	EU-CHATENET-CH46-I-HATCHBACK-01	HIGH		READY
157156	157156	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
800440	800440	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
800478	800478	SUV	Omoda 5 I		5	EU-CHERY-OMODA-5-I-SUV-01	HIGH		READY
802880	802880	SUV	Tiggo 4 I		5	EU-CHERY-TIGGO-4-I-SUV-01	HIGH		READY
163380	163380	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
163382	163382	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
162604	162604	SUV	Tiggo 7 II		5	EU-CHERY-TIGGO-7-II-SUV-01	HIGH		READY
163386	163386	SUV	Tiggo 8 I facelift		5	EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	HIGH		READY
162590	162590	SUV	Tiggo 8 I facelift		5	EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	HIGH		READY
802540	802540	SUV	Tiggo 9 I		5	EU-CHERY-TIGGO-9-I-SUV-01	HIGH		READY
16671	16671	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
11401	11401	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
11402	11402	Sedan	Alero I		4	EU-CHEVROLET-ALERO-I-SEDAN-01	HIGH		READY
36435	36435	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	HIGH	1995—2005第二代Cargo外廓。	READY
111219	111219	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	HIGH	1995—2005第二代Cargo外廓。	READY
36459	36459	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
36463	36463	Pickup	Avalanche I		4	EU-CHEVROLET-AVALANCHE-I-PICKUP-PREFL-01	HIGH	第一代早期外廓。	READY
58082	58082	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
36460	36460	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
50914	50914	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
121496	121496	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
58083_gen1	58083	Pickup	Avalanche I		4	EU-CHEVROLET-AVALANCHE-I-PICKUP-FACELIFT-01	HIGH	跨代Ktype的第一代后期外廓。	READY
58083_gen2	58083	Pickup	Avalanche II		4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH	跨代Ktype的第二代外廓。	READY
9997	9997	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
9998	9998	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10029	10029	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10572	10572	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10019	10019	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10444	10444	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
10035	10035	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
10443	10443	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
57387	57387	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
57388	57388	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
12030	12030	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
12031	12031	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
12032	12032	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	HIGH		READY
13977	13977	Sedan	Aveo II	T300	4	EU-CHEVROLET-AVEO-II-T300-SEDAN-01	HIGH		READY
55609_3dr	55609	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
55609_5dr	55609	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
113242_3dr	113242	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
113242_5dr	113242	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
18531_3dr	18531	Hatchback	Aveo/Kalos T200	T200	3	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
18531_5dr	18531	Hatchback	Aveo/Kalos T200	T200	5	EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
57132	57132	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH		READY
128219	128219	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH		READY
55439_3dr	55439	Hatchback	Aveo T250	T250	3	EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
55439_5dr	55439	Hatchback	Aveo T250	T250	5	EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
57389	57389	Sedan	Aveo T250	T250	4	EU-CHEVROLET-AVEO-T250-SEDAN-01	HIGH		READY
118685_3dr	118685	Hatchback	Aveo T250	T250	3	EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
118685_5dr	118685	Hatchback	Aveo T250	T250	5	EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_3001-3100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-ESCALADE-III-SUV-01	5144	2007	1928	Edmunds 2011 Cadillac Escalade and Escalade Hybrid specifications	https://www.edmunds.com/cadillac/escalade/2011/suv/st-101352619/features-specs/;https://www.edmunds.com/cadillac/escalade-hybrid/2011/suv/features-specs/
EU-CADILLAC-ESCALADE-IV-SUV-01	5179	2045	1890	Edmunds 2015 Cadillac Escalade specifications	https://www.edmunds.com/cadillac/escalade/2015/features-specs/
EU-CADILLAC-ESCALADE-IQ-I-SUV-01	5697	2093	1933	Cadillac 2026 Escalade IQ official specifications;Edmunds 2026 Cadillac Escalade IQ specifications	https://www.cadillac.com/electric/escalade-iq/specs;https://www.edmunds.com/cadillac/escalade-iq/2026/features-specs/
EU-CADILLAC-FLEETWOOD-BROUGHAM-V-SEDAN-01	5613	1913	1440	Automobile-Catalog 1983 Cadillac Fleetwood Brougham Sedan 4.1	https://www.automobile-catalog.com/car/1983/331250/cadillac_fleetwood_brougham_sedan_4_1l_v-8_ht-4100.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-1977-SEDAN-01	5618	1941	1453	Automobile-Catalog 1977 Cadillac Fleetwood Brougham 7.0	https://www.automobile-catalog.com/car/1977/186650/cadillac_fleetwood_brougham_7_0l_v-8.html
EU-CADILLAC-FLEETWOOD-SIXTY-SPECIAL-1971-SEDAN-01	5936	2027	1405	Automobile-Catalog 1975 Cadillac Fleetwood Sixty Special Brougham	https://www.automobile-catalog.com/car/1975/185975/cadillac_fleetwood_sixty_special_brougham.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-V-COUPE-01	5613	1915	1387	Automobile-Catalog 1982 Cadillac Fleetwood Brougham Coupe 5.7 Diesel	https://www.automobile-catalog.com/car/1982/331040/cadillac_fleetwood_brougham_coupe_5_7l_v-8_diesel.html
EU-CADILLAC-LYRIQ-I-SUV-01	4996	1977	1623	Cadillac Newsroom 2023 LYRIQ preliminary specifications	https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2021/apr/0421-lyriq.html
EU-CADILLAC-OPTIQ-I-SUV-01	4821	1913	1643	Cadillac 2026 OPTIQ official configurator specifications	https://www.cadillac.com/shopping/configurator/electric/2026/optiq/optiq/compare
EU-CADILLAC-OPTIQ-V-I-SUV-01	4820	1913	1644	Cadillac Newsroom 2026 OPTIQ-V specifications;Edmunds 2026 Cadillac OPTIQ-V specifications	https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2025/jun/0609-optiq-v.html;https://www.edmunds.com/cadillac/optiq/2026/v/features-specs/
EU-CADILLAC-SEVILLE-II-SEDAN-01	5202	1801	1379	Automobile-Catalog 1983 Cadillac Seville 4.1	https://www.automobile-catalog.com/car/1983/330545/cadillac_seville_4_1l_v-8_ht-4100.html
EU-CADILLAC-SEVILLE-IV-SEDAN-01	5189	1887	1369	Automobile-Catalog 1992 Cadillac Seville STS 4.9 Europe	https://www.automobile-catalog.com/car/1992/333515/cadillac_seville_sts.html
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1897	1428	Automobile-Catalog 1998 Cadillac Seville SLS Europe;Automobile-Catalog 1998 Cadillac Seville STS Europe	https://www.automobile-catalog.com/car/1998/334070/cadillac_seville_sls.html;https://www.automobile-catalog.com/car/1998/334085/cadillac_seville_sts.html
EU-CADILLAC-SRX-I-SUV-01	4950	1844	1722	Edmunds 2008 Cadillac SRX specifications	https://www.edmunds.com/cadillac/srx/2008/suv/features-specs/
EU-CADILLAC-SRX-II-SUV-01	4834	1910	1669	Edmunds 2013 Cadillac SRX specifications	https://www.edmunds.com/cadillac/srx/2013/features-specs/
EU-CADILLAC-STS-I-SEDAN-01	4996	1844	1463	Edmunds 2008 Cadillac STS specifications	https://www.edmunds.com/cadillac/sts/2008/features-specs/
EU-CADILLAC-STS-V-I-SEDAN-01	5019	1844	1478	Edmunds 2007 Cadillac STS-V specifications	https://www.edmunds.com/cadillac/sts-v/2007/sedan/features-specs/
EU-CADILLAC-VISTIQ-I-SUV-01	5222	2026	1804	Cadillac Newsroom 2026 VISTIQ specifications	https://news.cadillac.com/newsroom.detail.html/Pages/news/us/en/2024/nov/1112-vistiq.html
EU-CADILLAC-XLR-I-CONVERTIBLE-01	4514	1836	1280	Edmunds 2008 Cadillac XLR specifications	https://www.edmunds.com/cadillac/xlr/2008/features-specs/
EU-CADILLAC-XT4-I-SUV-01	4593	1881	1612	Cadillac XT4 Diesel official technical data	https://media.cadillac.com/content/dam/Media/documents/INTL/cadillac/2021/crossovers-suvs/xt4/Cadillac%20XT4%20TechData%20EN_Diesel.pdf
EU-CADILLAC-XT5-I-SUV-01	4815	1903	1675	Cadillac XT5 Specifications Europe	https://media.gmc.com/content/dam/Media/documents/INTL/cadillac/2019/crossover-suv/xt5/Tech-Data-Cadillac-XT5-EN.pdf
EU-CALLAWAY-C12-I-COUPE-01	4850	2000	1200	Auto-Data Callaway C12 Coupe;Callaway Cars C12 official project page	https://www.auto-data.net/en/callaway-c12-coupe-generation-2554;https://www.callawaycars.com/homepage/the-company/callaway-c-projects/c12/
EU-CALLAWAY-C12-I-CONVERTIBLE-01	4850	2000	1200	Auto-Data Callaway C12 Cabrio;Callaway Cars C12 official project page	https://www.auto-data.net/en/callaway-c12-cabrio-generation-2553;https://www.callawaycars.com/homepage/the-company/callaway-c-projects/c12/
EU-CATERHAM-SEVEN-160-CONVERTIBLE-01	3100	1470	1090	Caterham Cars Japan Seven 160 official specifications	https://www.caterham-cars.jp/news/2014/
EU-CATERHAM-SEVEN-170-CONVERTIBLE-01	3180	1470	1090	Caterham Cars Seven 170 official specifications	https://caterhamcars.com/tw/models/the-range/seven-170
EU-CATERHAM-SEVEN-275-CONVERTIBLE-01	3180	1575	1090	Automobile-Catalog Caterham Seven 275 Europe specifications	https://www.automobile-catalog.com/car/2018/2969990/caterham_seven_275.html
EU-CATERHAM-SUPER-SEVEN-1600-CONVERTIBLE-01	3378	1575	1040	Automobile-Catalog 1986 Caterham Super Seven 1600 GT specifications	https://www.automobile-catalog.com/car/1986/336815/caterham_super_seven_1600_gt.html
EU-CATERHAM-SEVEN-420-CONVERTIBLE-01	3180	1470	1090	Caterham Cars Seven 420 official specifications	https://caterhamcars.com/en/models/the-range/seven-420
EU-CATERHAM-SEVEN-1-8-K-SERIES-CONVERTIBLE-01	3100	1575	1115	Automobile-Catalog 2001 Caterham 7 Superlight R300 specifications	https://www.automobile-catalog.com/car/2001/337925/caterham_7_superlight_r300.html
EU-CENNTRO-LOGISTAR-100-I-VAN-01	3664	1610	1689	Cenntro Logistar 100 technical specifications	https://cenntro.nl/media/pages/modellen/logistar-100/25e076d43a-1699967916/2022-09-15_en_flyer_cenntrologistar100.pdf
EU-CENNTRO-LOGISTAR-200-I-PICKUP-01	4770	1640	1991	Cenntro Europe Logistar 200 official technical data	https://cenntro-europe.com/wp-content/uploads/2023/05/DE_CENN_200_ALL-1.pdf
EU-CENNTRO-LOGISTAR-200-I-VAN-01	4421	1677	1902	Cenntro Logistar 200 official technical specifications	https://www.cenntro.nl/media/pages/modellen/logistar-200-van/274cf7a578-1698766079/logistar-specs.pdf
EU-CENNTRO-LOGISTAR-260-I-VAN-01	5457	1850	2046	Cenntro Logistar 260 official specifications	https://cenntroauto.com/vehicles/logistar-260/
EU-CENNTRO-LOGISTAR-400-I-PICKUP-01	5994	2057	2718	Cenntro Logistar 400 official specifications	https://cenntroauto.com/vehicles/logistar-400/
EU-CENNTRO-LOGISTAR-400-I-VAN-01	5994	2057	2718	Cenntro Logistar 400 official specifications	https://cenntroauto.com/vehicles/logistar-400/
EU-CENNTRO-METRO-I-PICKUP-01	3700	1400	1905	Cenntro Metro electric utility truck regional specifications	https://electricvan-inc.com/1-metro-series-electric-vehicle.html
EU-CENNTRO-METRO-I-VAN-01	3910	1400	1905	Cenntro Metro official specifications	https://cenntroauto.com/vehicles/metro/
EU-CENNTRO-NEIBOR-200-I-VAN-01	3500	1480	1490	Cenntro Neibor 200 regional product specifications	https://electricvan-inc.fr/products.html
EU-CENNTRO-ORV-I-PICKUP-01	4010	1600	2150	Cenntro TeeMak ORV official specifications	https://cenntroauto.com/vehicles/orv/
EU-CHANGAN-X5-PLUS-I-SUV-01	4540	1860	1620	AutoCango 2025 Changan X5 Plus specifications	https://www.autocango.com/carspecs-detail/ChangAn-X5-PLUS-BXND3W
EU-CHATENET-CH40-I-HATCHBACK-01	2977	1492	1457	Automobiles Chatenet CH40-CH46 official owner notice	https://www.automobiles-chatenet.com/service-apres-vente.html?file=files%2Fpack%2Fcontenu%2FPDF-technique%2F2025%2FNOTICE+CH40-CH46+V2.pdf
EU-CHATENET-CH46-I-HATCHBACK-01	2882	1500	1453	Automobiles Chatenet CH40-CH46 official owner notice	https://www.automobiles-chatenet.com/service-apres-vente.html?file=files%2Fpack%2Fcontenu%2FPDF-technique%2F2025%2FNOTICE+CH40-CH46+V2.pdf
EU-CHERY-OMODA-5-I-SUV-01	4400	1830	1588	Chery International OMODA official specifications	https://www.cheryinternational.com/omoda/
EU-CHERY-TIGGO-4-I-SUV-01	4320	1831	1652	Chery International TIGGO 4 CSH official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo4_csh/index.shtml
EU-CHERY-TIGGO-7-II-SUV-01	4553	1862	1696	Chery International TIGGO 7 CSH official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo7_csh/index.shtml
EU-CHERY-TIGGO-8-I-FACELIFT-SUV-01	4725	1860	1705	Chery International Tiggo 8 official specifications	https://www.cheryinternational.com/pc/models/tiggo/tiggo8proe/index.shtml
EU-CHERY-TIGGO-9-I-SUV-01	4810	1925	1741	Chery Lithuania TIGGO 9 PHEV official specifications	https://cherymotor.lt/en/tiggo-9-phev/
EU-CHEVROLET-ALERO-I-SEDAN-01	4742	1780	1399	Automobile-Catalog 1999 Chevrolet Alero 2.4 16V Europe	https://www.automobile-catalog.com/car/1999/2406875/chevrolet_alero_2_4_16v.html
EU-CHEVROLET-ASTRO-II-CARGO-VAN-01	4821	1969	1905	Edmunds 2005 Chevrolet Astro Cargo specifications	https://www.edmunds.com/chevrolet/astro-cargo/2005/features-specs/
EU-CHEVROLET-AVALANCHE-I-PICKUP-PREFL-01	5631	2027	1862	Edmunds 2003 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2003/features-specs/
EU-CHEVROLET-AVALANCHE-I-PICKUP-FACELIFT-01	5629	2027	1869	Edmunds 2006 Chevrolet Avalanche 1500 specifications	https://www.edmunds.com/chevrolet/avalanche/2006/st-100580431/features-specs/
EU-CHEVROLET-AVALANCHE-II-PICKUP-01	5621	2009	1946	Edmunds 2011 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2011/features-specs/
EU-CHEVROLET-AVEO-II-T300-HATCHBACK-01	4039	1735	1517	Automobile-Catalog 2011 Chevrolet Aveo 1.4 LT Hatchback	https://www.automobile-catalog.com/car/2011/1568495/chevrolet_aveo_1_4_lt_hatchback.html
EU-CHEVROLET-AVEO-II-T300-SEDAN-01	4399	1735	1517	Automobile-Catalog 2012 Chevrolet Aveo 1.4 LT Sedan	https://www.automobile-catalog.com/car/2012/1568630/chevrolet_aveo_1_4_lt_sedan.html
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-3D-01	3880	1670	1495	Automobile-Catalog 2006 Chevrolet Kalos 1.2 SE Hatchback Europe	https://www.automobile-catalog.com/car/2006/559025/chevrolet_kalos_1_2_se_hatchback.html
EU-CHEVROLET-AVEO-KALOS-T200-HATCHBACK-5D-01	3880	1670	1495	Automobile-Catalog 2006 Chevrolet Kalos 1.2 SE Hatchback Europe	https://www.automobile-catalog.com/car/2006/559025/chevrolet_kalos_1_2_se_hatchback.html
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495	Automobile-Catalog 2005 Chevrolet Kalos 1.4 16V SX Sedan Europe	https://www.automobile-catalog.com/car/2005/559085/chevrolet_kalos_1_4_16v_sx_sedan_automatic.html
EU-CHEVROLET-AVEO-T250-HATCHBACK-3D-01	3920	1680	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.2 Hatchback Europe	https://www.automobile-catalog.com/car/2009/1209830/chevrolet_aveo_1_2_hatchback.html
EU-CHEVROLET-AVEO-T250-HATCHBACK-5D-01	3920	1680	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.2 Hatchback Europe	https://www.automobile-catalog.com/car/2009/1209830/chevrolet_aveo_1_2_hatchback.html
EU-CHEVROLET-AVEO-T250-SEDAN-01	4310	1710	1505	Automobile-Catalog 2009 Chevrolet Aveo 1.4 LT Sedan Europe	https://www.automobile-catalog.com/car/2009/559175/chevrolet_aveo_1_4_lt_sedan.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_3001-3100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.edmunds.com/cadillac/escalade/2015/features-specs/?utm_source=chatgpt.com "Used 2015 Cadillac Escalade Specs & Features"
[2]: https://www.automobile-catalog.com/make/cadillac/fleetwood_1977-1986/fleetwood_1977-1986_sedan/1977.html?utm_source=chatgpt.com "1977 Cadillac Fleetwood 5gen Brougham Sedan full range ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3604 行）
- 累计尺寸组：dimension_groups_final.tsv（1002 行）

