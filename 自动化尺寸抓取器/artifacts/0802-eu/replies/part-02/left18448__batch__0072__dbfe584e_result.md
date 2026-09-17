# 任务：left18448 第 7101-7200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0072__dbfe584e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 7101-7200 行

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
left18448 第 7101-7200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Infiniti	Ex	25	SUV	Allrad	Benzin	Apr 2010	Dec 2013	56851
Infiniti	Ex	35	SUV	Allrad	Benzin	Oct 2008	-	14883
Infiniti	Ex	37	SUV	Allrad	Benzin	Sep 2010	-	34787
Infiniti	Fx	35 Allrad	SUV	Allrad	Benzin	Jan 2003	Dec 2008	18811
Infiniti	Fx	45 Allrad	SUV	Allrad	Benzin	Jan 2003	Dec 2008	18812
Infiniti	Fx	50 AWD	SUV	Allrad	Benzin	Jun 2013	Jul 2013	59011
Infiniti	G	35	Stufenheck	Heckantrieb	Benzin	Oct 2002	-	14885
Infiniti	G	37	Coupe	Heckantrieb	Benzin	Sep 2010	-	34794
Infiniti	G	37	Cabriolet	Heckantrieb	Benzin	Sep 2010	-	34797
Infiniti	G20	2	Stufenheck	Frontantrieb	Benzin	Jan 1990	Dec 1997	14039
Infiniti	I30	3	Stufenheck	Frontantrieb	Benzin	Jan 1997	-	14040
Infiniti	J30	3	Stufenheck	Heckantrieb	Benzin	Jan 1992	Dec 1997	14059
Infiniti	M	37	Stufenheck	Heckantrieb	Benzin	Mar 2010	-	34803
Infiniti	M	30D	Stufenheck	Heckantrieb	Diesel	Mar 2010	-	34804
Infiniti	M30	3	Coupe	Heckantrieb	Benzin	Jan 1989	Dec 1993	14060
Infiniti	M30 convertible	3	Cabriolet	Heckantrieb	Benzin	Jan 1990	Dec 1993	14061
Infiniti	Q30	1.6	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	117841
Infiniti	Q30	1.6	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	117842
Infiniti	Q30	1.5 D	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	117844
Infiniti	Q30	2.0 T	Schrägheck	Frontantrieb	Benzin	Nov 2015	-	118526
Infiniti	Q30	2.0 T AWD	Schrägheck	Allrad	Benzin	Nov 2015	-	117843
Infiniti	Q30	2.2 D	Schrägheck	Frontantrieb	Diesel	Nov 2015	-	117846
Infiniti	Q30	2.2 D AWD	Schrägheck	Allrad	Diesel	Nov 2015	-	117847
Infiniti	Q45 i	4.1	Stufenheck	Heckantrieb	Benzin	Jan 1993	Dec 1996	14062
Infiniti	Q45 i	4.5	Stufenheck	Heckantrieb	Benzin	Jan 1989	Dec 1993	14063
Infiniti	Q45 ii	4.1	Stufenheck	Heckantrieb	Benzin	Jan 1997	Jan 2001	34771
Infiniti	Q50	2.0 T	Stufenheck	Heckantrieb	Benzin	Apr 2014	-	105688
Infiniti	Q50	50 RED	Stufenheck	Heckantrieb	Benzin	Sep 2015	-	119719
Infiniti	Q60	3.7	Coupe	Heckantrieb	Benzin	Oct 2013	-	100191
Infiniti	Q60	3.7	Cabriolet	Heckantrieb	Benzin	Oct 2013	-	100192
Infiniti	Q60	2.0 T	Coupe	Heckantrieb	Benzin	Sep 2016	-	121986
Infiniti	Q60	3.0 T AWD	Coupe	Allrad	Benzin	Sep 2016	-	121989
Infiniti	Q70	3	Stufenheck	Heckantrieb	Diesel	Mar 2013	-	100926
Infiniti	Q70	3.7	Stufenheck	Heckantrieb	Benzin	Mar 2013	-	100925
Infiniti	Q70	2.2 D	Stufenheck	Heckantrieb	Diesel	Oct 2014	-	110819
Infiniti	Q70	3.5 Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	Mar 2013	-	107309
Infiniti	Qx4	3.3	Geländewagen geschlossen	Allrad	Benzin	Jan 1997	-	14088
Infiniti	Qx50 i	30D AWD	SUV	Allrad	Diesel	Aug 2013	-	100723
Infiniti	Qx50 i	37 AWD	SUV	Allrad	Benzin	Aug 2013	-	100724
Infiniti	Qx70	3.7 AWD	SUV	Allrad	Benzin	Aug 2013	-	112948
Infiniti	Qx70	30D AWD	SUV	Allrad	Diesel	Aug 2013	-	100721
Infiniti	Qx70	37 AWD	SUV	Allrad	Benzin	Feb 2014	-	117608
Infiniti	Qx70	50 AWD	SUV	Allrad	Benzin	Aug 2013	-	100722
Innocenti	Mini	1	Schrägheck	Frontantrieb	Benzin	May 1974	Feb 1982	5079
Innocenti	Mini	1	Schrägheck	Frontantrieb	Benzin	May 1974	Feb 1982	5084
Innocenti	Mini	1.3	Schrägheck	Frontantrieb	Benzin	Aug 1976	Feb 1982	5080
Innocenti	Mini	1.3 DE Tomaso	Schrägheck	Frontantrieb	Benzin	Aug 1976	Feb 1982	5082
Irmscher	Coupe	1.6 16V	Coupe	Frontantrieb	Benzin	Jan 1997	-	12679
Irmscher	Gt	3.6	Coupe	Heckantrieb	Benzin	Jan 1988	Dec 1990	12680
Irmscher	Omega caravan	4.0 I	Kombi	Heckantrieb	Benzin	Jan 1990	Dec 1996	12682
Irmscher	Senator	4.0 24V	Stufenheck	Heckantrieb	Benzin	Jan 1990	Dec 1996	12681
Isdera	Commendatore	6.0 112i	Coupe	Heckantrieb	Benzin	Jan 1993	Jun 1995	12726
Isdera	Imperator	5.0 108i	Coupe	Heckantrieb	Benzin	May 1991	Jun 1995	12727
Isorivolta	Fidia	5.7 Ir-10	Stufenheck	Heckantrieb	Benzin	Jan 1972	Dec 1972	147386
Isorivolta	Grifo	5.7 Ir-8	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1972	147385
Isorivolta	Lele	5.7 Ir-6	Coupe	Heckantrieb	Benzin	Jan 1972	Dec 1972	147384
Isuzu	Campo	2.2 D	Pick-up	Heckantrieb	Diesel	Apr 1986	Dec 1990	14245
Isuzu	Campo	2.2 D 4WD	Pick-up	Allrad	Diesel	Jan 1983	Dec 1990	14246
Isuzu	D-Max i	3.0 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jan 2007	Jun 2012	34517
Isuzu	D-Max i	3.0 Ditd	Pick-up	Heckantrieb	Diesel	Jan 2007	Jun 2012	34518
Isuzu	D-Max ii	1.9 DDI	Pick-up	Heckantrieb	Diesel	Mar 2017	Dec 2022	126051
Isuzu	D-Max ii	1.9 DDI 4X4	Pick-up	Allrad	Diesel	Mar 2017	Dec 2022	126055
Isuzu	D-Max ii	2.5 Crdi	Pick-up	Heckantrieb	Diesel	Apr 2012	Dec 2018	55099
Isuzu	D-Max ii	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jun 2012	-	113463
Isuzu	D-Max ii	2.5 Crdi 4WD	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2012	-	113464
Isuzu	D-Max ii	2.5 Crdi 4X4	Pick-up	Allrad	Diesel	Apr 2012	Dec 2018	55091
Isuzu	D-Max iii	1.9 DDI	Pick-up	Heckantrieb	Diesel	Nov 2019	-	146714
Isuzu	D-Max iii	1.9 DDI 4X4	Pick-up	Allrad	Diesel	Nov 2019	-	146715
Isuzu	D-Max iii	1.9 DDI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jun 2023	-	157597
Isuzu	D-Max iii	BEV 4X4	Pick-up	Allrad	Elektro	May 2025	-	801987
Isuzu	D-Max iii	BEV 4X4	Pick-up	Allrad	Elektro	Feb 2026	-	802844
Isuzu	D-Max iii	DDI	Pick-up	Heckantrieb	Diesel	Nov 2024	-	801355
Isuzu	D-Max iii	DDI 4X4	Pick-up	Allrad	Diesel	Nov 2024	-	802421
Isuzu	Elf	3.1 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jan 1998	Dec 2001	115533
Isuzu	Gemini	1.5	Schrägheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18647
Isuzu	Gemini	1.5	Schrägheck	Frontantrieb	Benzin	Jan 1985	Dec 1987	125793
Isuzu	Gemini	1.6	Schrägheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18648
Isuzu	Gemini	1.6	Schrägheck	Allrad	Benzin	Jan 1990	Dec 1993	18649
Isuzu	Gemini	1.8	Schrägheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18650
Isuzu	Gemini	1.8	Stufenheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18656
Isuzu	Gemini	1.5 I	Stufenheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18653
Isuzu	Gemini	1.6 GTI 16V	Schrägheck	Frontantrieb	Benzin	Mar 1988	Jun 1990	125799
Isuzu	Gemini	1.6 I	Stufenheck	Frontantrieb	Benzin	Jan 1990	Dec 1993	18654
Isuzu	Gemini	1.6 I Turbo	Stufenheck	Allrad	Benzin	Jan 1990	Dec 1993	18655
Isuzu	Gemini	1.7 TD	Schrägheck	Frontantrieb	Diesel	Jan 1990	Dec 1993	18651
Isuzu	Gemini	1.7 TD	Stufenheck	Frontantrieb	Diesel	Jan 1990	Dec 1993	18652
Isuzu	Impulse	1.6	Coupe	Frontantrieb	Benzin	Jan 1990	Dec 1993	18657
Isuzu	Impulse	1.6	Coupe	Frontantrieb	Benzin	Jan 1990	Dec 1993	18658
Isuzu	Midi	2	Kasten	Heckantrieb	Benzin	Jun 1988	Aug 1992	7836
Isuzu	Midi	2.0 4WD	Kasten	Allrad	Benzin	Jun 1988	Aug 1992	10786
Isuzu	Midi	2.2 D	Kasten	Heckantrieb	Diesel	Jun 1988	Aug 1992	8819
Isuzu	Midi	2.2 D 4WD	Kasten	Allrad	Diesel	Jun 1988	Aug 1992	10788
Isuzu	Midi	2.4 TD	Kasten	Heckantrieb	Diesel	Sep 1992	Jul 1996	10787
Isuzu	Piazza	2	Coupe	Heckantrieb	Benzin	Jun 1981	Aug 1985	125804
Isuzu	Trooper i	2.2 D 4WD	Geländewagen geschlossen	Allrad	Diesel	May 1984	Dec 1989	17437
Isuzu	Trooper i	2.2 D 4X4	Geländewagen offen	Allrad	Diesel	May 1984	Jul 1989	17457
Isuzu	Trooper ii	3.2	Geländewagen geschlossen	Allrad	Benzin	Aug 1991	Jul 1998	17446
Isuzu	Trooper ii	3.2	Geländewagen offen	Allrad	Benzin	Aug 1991	Jul 1998	17447
Isuzu	Trooper iii	3.0 DTI	Geländewagen offen	Allrad	Diesel	Apr 2000	Aug 2004	17455
Isuzu	Trooper iii	3.0 TDI	Geländewagen geschlossen	Allrad	Diesel	Oct 2000	Jun 2002	121922


--- Round 1 / 首次发送 ---
## 更新点

* 首批闭合 Infiniti 历史轿车尺寸组：G20 P10、I30 A32、J30 Y32；三维均采用明确标注不含后视镜宽度的规格。([汽车目录][1])
* 闭合 M30 Coupe、Q45 G50，并确认 Q45 II FY33 在 1999 年改款时车长发生变化，因此 Ktype `34771` 拆分为改款前、改款后两个物理分支。([汽车目录][2])
* M30 Convertible 存在高度冲突；QX4 存在标准车顶与行李架高度口径冲突；Ktype `14062` 的生产期与 4.1L 所属代际不一致，暂不绑定尺寸组。([Edmunds][3])

## 当前批次进度

* READY 映射：7 行，覆盖 6 个输入 Ktype。
* 已明确 PENDING：3 行。
* 尚未闭合输入 Ktype：94 个，其中 3 个已定位具体冲突，91 个尚待按物理车身聚类处理。
* 已确认尺寸组：7 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14039	14039	Sedan	G20 P10	P10	4	EU-INFINITI-G20-P10-SEDAN-01	HIGH	P10四门轿车。	READY
14040	14040	Sedan	I30 A32	A32	4	EU-INFINITI-I30-A32-SEDAN-01	HIGH	A32四门轿车。	READY
14059	14059	Sedan	J30 Y32	Y32	4	EU-INFINITI-J30-Y32-SEDAN-01	HIGH	Y32四门轿车。	READY
14060	14060	Coupe	M30	F31	2	EU-INFINITI-M30-F31-COUPE-01	HIGH	F31双门轿跑。	READY
14061	14061	Convertible	M30	F31	2		LOW	敞篷车高度来源冲突，待统一标准车顶闭合状态口径。	PENDING: 敞篷车高度来源冲突
14062	14062	Sedan	Q45		4		LOW	输入生产期对应G50，但4.1L对应后续FY33，代际边界冲突。	PENDING: 生产期与4.1L代际冲突
14063	14063	Sedan	Q45 G50	G50	4	EU-INFINITI-Q45-G50-SEDAN-01	HIGH	G50四门轿车。	READY
34771_prefl	34771	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	HIGH	1997-1998改款前外廓。	READY
34771_facelift	34771	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-FACELIFT-01	HIGH	1999-2001改款后外廓。	READY
14088	14088	SUV	QX4	JR50	5		MEDIUM	标准车顶与车顶行李架高度口径未闭合。	PENDING: 高度口径冲突
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-G20-P10-SEDAN-01	4445	1694	1394	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1991/2165630/infiniti_g20_5-speed.html;https://www.edmunds.com/infiniti/g20/1991/features-specs/
EU-INFINITI-I30-A32-SEDAN-01	4816	1770	1415	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1997/2166395/infiniti_i30.html;https://www.edmunds.com/infiniti/i30/1997/features-specs/
EU-INFINITI-J30-Y32-SEDAN-01	4860	1770	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2132225/infiniti_j30.html
EU-INFINITI-M30-F31-COUPE-01	4795	1690	1380	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1990/2132135/infiniti_m30_luxury_sports_coupe.html;https://www.edmunds.com/infiniti/m30/1990/coupe/features-specs/
EU-INFINITI-Q45-G50-SEDAN-01	5090	1825	1435	Nissan Heritage Collection;Automobile-Catalog	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/229_infiniti_q45.html;https://www.automobile-catalog.com/car/1990/2165765/infiniti_q45.html
EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	5060	1821	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2166005/infiniti_q45.html
EU-INFINITI-Q45-FY33-SEDAN-FACELIFT-01	5070	1821	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/2166065/infiniti_q45.html
```

## 下一步优先处理

1. 批量处理 Infiniti EX、FX、QX50、QX70，确认 EX/QX50 与 FX/QX70 的更名复用关系及改款边界。
2. 闭合 Infiniti G、M、Q30、Q50、Q60、Q70 的 Sedan、Coupe、Convertible 独立外廓。
3. 继续解决 M30 Convertible、QX4 和 Q45 Ktype `14062` 的三个已知冲突。
4. 随后处理 Innocenti、Irmscher、Isdera、Isorivolta及 Isuzu 乘用车；D-Max、Campo、Elf 按驾驶室、轴距和货斗分支单独处理。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1991/2165630/infiniti_g20_5-speed.html?utm_source=chatgpt.com "1991 Infiniti G20 5-speed Specs Review (104.5 kW ..."
[2]: https://www.automobile-catalog.com/car/1990/2132135/infiniti_m30_luxury_sports_coupe.html?utm_source=chatgpt.com "1990 Infiniti M30 Luxury Sports Coupe (aut. 4)"
[3]: https://www.edmunds.com/infiniti/m30/1991/convertible/features-specs/?utm_source=chatgpt.com "Used 1991 INFINITI M30 Convertible Specs & Features"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Infiniti EX37/QX50 37 的 J50 汽油版外廓，以及 QX50 30D 的独立柴油版外廓；柴油版因车长增加 10 mm，不能与汽油版合并。([汽车目录][1])
* 闭合第一代 FX35/FX45 的 S50 共用尺寸组。
* 闭合第二代 FX50 与更名后的 QX70 S51 共用尺寸组；当前 3.0D、3.7 和 5.0 Ktype 均复用该组。([Edmunds][2])
* EX25、EX35 暂未落盘：不同销售市场的前牌照、车顶行李架及高度口径存在差异，下一轮集中解决，不用欧洲 EX37 数据直接覆盖。

## 当前批次进度

* READY 映射：17 行，覆盖 16 个输入 Ktype。
* PENDING 映射：3 行。
* 尚未处理：81 个输入 Ktype。
* 已确认尺寸组：11 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34787	34787	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-01	HIGH	J50五门汽油版外廓。	READY
18811	18811	SUV	FX I	S50	5	EU-INFINITI-FX-S50-SUV-01	HIGH	S50五门SUV外廓。	READY
18812	18812	SUV	FX I	S50	5	EU-INFINITI-FX-S50-SUV-01	HIGH	S50五门SUV外廓。	READY
59011	59011	SUV	FX II	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
100723	100723	SUV	QX50 I	J50	5	EU-INFINITI-EX-QX50-J50-SUV-02	HIGH	J50五门3.0D外廓。	READY
100724	100724	SUV	QX50 I	J50	5	EU-INFINITI-EX-QX50-J50-SUV-01	HIGH	J50五门汽油版外廓。	READY
112948	112948	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
100721	100721	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
117608	117608	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
100722	100722	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-EX-QX50-J50-SUV-01	4635	1800	1575	Automobile-Catalog Infiniti EX37 Europe;encyCARpedia Infiniti QX50 3.7 J50	https://www.automobile-catalog.com/car/2012/2169620/infiniti_ex37.html;https://www.encycarpedia.com/infiniti/13-qx50-3-7-suv
EU-INFINITI-FX-S50-SUV-01	4803	1925	1651	Automobile-Catalog Infiniti FX35 4x4;Edmunds Infiniti FX35	https://www.automobile-catalog.com/car/2003/2168270/infiniti_fx35_4x4.html;https://www.edmunds.com/infiniti/fx35/2003/st-100213725/features-specs/
EU-INFINITI-FX-QX70-S51-SUV-01	4865	1925	1680	Automobile-Catalog Infiniti FX50 S AWD Europe;CarsGuide Infiniti QX70	https://www.automobile-catalog.com/car/2013/2170175/infiniti_fx50_s_awd.html;https://www.carsguide.com.au/infiniti/qx70/car-dimensions/2014
EU-INFINITI-EX-QX50-J50-SUV-02	4645	1800	1575	encyCARpedia Infiniti QX50 3.0d J50;AutoScout24 Infiniti QX50 Diesel	https://www.encycarpedia.com/infiniti/13-qx50-3-0d-suv;https://www.autoscout24.be/nl/auto/technische-gegevens/infiniti/qx50/
```

## 下一步优先处理

1. 解决 EX25、EX35 的市场规格与无行李架高度口径。
2. 批量闭合 Infiniti G Sedan、G37/Q60 Coupe 和 Convertible 的更名前后复用关系。
3. 处理 Infiniti M/Q70 Y51，并拆分改款前后车长变化。
4. 处理 Q30 普通悬架与 Sport 降低悬架的 1495/1475 mm 高度分支。
5. 继续消除 M30 Convertible、Q45 Ktype `14062`、QX4 三个既有 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/2169620/infiniti_ex37.html?utm_source=chatgpt.com "2012 Infiniti EX37 Specs Review (235 kW / 320 PS / 315 hp) (for Europe )"
[2]: https://www.edmunds.com/infiniti/fx35/2003/st-100213725/features-specs/?utm_source=chatgpt.com "Used 2003 INFINITI FX35 Base Specs & Features"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 G35 V35 Sedan。
* 闭合 G37／第一代 Q60 的 CV36 Coupe 与 HV36 Convertible，更名前后复用同一尺寸组。
* 闭合 M37、M30D 与改名前 Q70 的 Y51 标准外廓。
* Q70 2.2D 对应改款后车身，车长和高度发生变化，独立建立尺寸组。车身代码边界由 Infiniti 应用指南交叉确认，尺寸采用明确标注不含后视镜宽度的欧洲规格。([汽车目录][1])

## 当前批次进度

* READY 映射：28 行，覆盖 27 个输入 Ktype。
* PENDING 映射：3 行。
* 尚未处理：70 个输入 Ktype。
* 已确认尺寸组：16 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14885	14885	Sedan	G35 V35	V35	4	EU-INFINITI-G35-V35-SEDAN-01	HIGH	V35四门轿车。	READY
34794	34794	Coupe	G37	CV36	2	EU-INFINITI-G-Q60-CV36-COUPE-01	HIGH	CV36双门轿跑。	READY
34797	34797	Convertible	G37	HV36	2	EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	HIGH	HV36双门敞篷车。	READY
34803	34803	Sedan	M Y51	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
34804	34804	Sedan	M Y51	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
100191	100191	Coupe	Q60 I	CV36	2	EU-INFINITI-G-Q60-CV36-COUPE-01	HIGH	CV36双门轿跑。	READY
100192	100192	Convertible	Q60 I	HV36	2	EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	HIGH	HV36双门敞篷车。	READY
100926	100926	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
100925	100925	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
110819	110819	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-FACELIFT-01	HIGH	Y51改款后四门轿车。	READY
107309	107309	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-G35-V35-SEDAN-01	4737	1753	1466	Automobile-Catalog Infiniti G35 V35	https://www.automobile-catalog.com/car/2003/2166815/infiniti_g35.html
EU-INFINITI-G-Q60-CV36-COUPE-01	4655	1820	1387	Automobile-Catalog Infiniti G37 Coupe Europe;Automobile-Catalog Infiniti Q60 Coupe Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2167715/infiniti_g37_s_coupe_6-speed.html;https://www.automobile-catalog.com/car/2014/2168675/infiniti_q60_coupe_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	4660	1852	1391	Automobile-Catalog Infiniti G37 Cabrio Europe;Automobile-Catalog Infiniti Q60 Cabrio Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2167760/infiniti_g37_gt_cabrio_automatic.html;https://www.automobile-catalog.com/car/2014/2168660/infiniti_q60_cabrio_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	4945	1845	1500	Automobile-Catalog Infiniti M37 Europe;Automobile-Catalog Infiniti Q70 3.0d Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2169065/infiniti_m37.html;https://www.automobile-catalog.com/car/2014/2169140/infiniti_q70_3_0d_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-M-Q70-Y51-SEDAN-FACELIFT-01	4980	1845	1493	Automobile-Catalog Infiniti Q70 2.2d Europe	https://www.automobile-catalog.com/car/2015/2169215/infiniti_q70_2_2d.html
```

## 下一步优先处理

1. 闭合 Q50 V37 与第二代 Q60 CV37，确认后驱和四驱是否存在外廓高度差异。
2. 处理 Q30 H15，并解决普通悬架与 Sport 低悬架的高度分支。
3. 集中消除 M30 Convertible、Q45 Ktype `14062`、QX4 三个既有 PENDING。
4. 完成剩余 Infiniti 后，按 Innocenti／Irmscher／Isdera／Isorivolta 聚类推进。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2003/2166815/infiniti_g35.html?utm_source=chatgpt.com "2003 Infiniti G35 Specs Review (194 kW / 264 PS / 260 hp) (since early-year 2002 for North America )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Q50 V37：普通外观、Sport 外观和 Red Sport 外观因车长或车高不同，分别建立尺寸组。
* 闭合第二代 Q60 CV37；2.0T 后驱和 3.0T 四驱共用 `4690 × 1850 × 1390 mm` 外廓。
* 闭合 Q30 H15 标准悬架与 Sport 降低悬架两个尺寸组；仅对实际覆盖两种外廓的 Ktype 派生 `standard`、`sport` 行。
* 原 PENDING 的 M30 Convertible 与 QX4 已完成闭合。M30 Convertible 使用敞篷车独立三维；QX4 使用不含车顶行李架的标准车身高度。([Edmunds][1])

## 当前批次进度

* READY 映射：45 行，覆盖 40 个输入 Ktype。
* PENDING 映射：1 行。
* 尚未处理：59 个输入 Ktype。
* 已确认尺寸组：24 个。
* 当前唯一既有 PENDING：Ktype `14062`，输入生产期与 4.1L 所属 Q45 代际冲突。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14061	14061	Convertible	M30	F31	2	EU-INFINITI-M30-F31-CONVERTIBLE-01	HIGH	F31双门敞篷外廓。	READY
105688_standard	105688	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-STANDARD-01	HIGH	普通前后保险杠外廓。	READY
105688_sport	105688	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-SPORT-01	HIGH	Sport保险杠造成车长差异。	READY
119719	119719	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-REDSPORT-01	HIGH	Red Sport低车身外廓。	READY
121986	121986	Coupe	Q60 II	CV37	2	EU-INFINITI-Q60-CV37-COUPE-01	HIGH	CV37双门轿跑外廓。	READY
121989	121989	Coupe	Q60 II	CV37	2	EU-INFINITI-Q60-CV37-COUPE-01	HIGH	CV37双门轿跑外廓。	READY
117841	117841	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	90kW 1.6T标准悬架外廓。	READY
117842_standard	117842	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	115kW 1.6T标准悬架外廓。	READY
117842_sport	117842	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	115kW 1.6T Sport降低悬架外廓。	READY
117844	117844	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	1.5D标准悬架外廓。	READY
118526	118526	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.0T前驱Sport外廓。	READY
117843	117843	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.0T四驱Sport外廓。	READY
117846_standard	117846	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	2.2D标准悬架外廓。	READY
117846_sport	117846	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.2D Sport降低悬架外廓。	READY
117847_standard	117847	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	2.2D四驱标准悬架外廓。	READY
117847_sport	117847	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.2D四驱Sport降低悬架外廓。	READY
14088	14088	SUV	QX4	JR50	5	EU-INFINITI-QX4-JR50-SUV-01	HIGH	JR50标准车顶五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-M30-F31-CONVERTIBLE-01	4798	1689	1410	Edmunds 1991 Infiniti M30 Convertible specifications	https://www.edmunds.com/infiniti/m30/1991/convertible/features-specs/
EU-INFINITI-Q50-V37-SEDAN-STANDARD-01	4790	1820	1445	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q50-V37-SEDAN-SPORT-01	4800	1820	1445	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q50-V37-SEDAN-REDSPORT-01	4800	1820	1430	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q60-CV37-COUPE-01	4690	1850	1390	INFINITI Q60 UK official brochure;2017 INFINITI Q60 official press kit	https://www.infiniti-cdn.net/content/dam/Infiniti/Brochures/UK/final/Q60_UK.pdf;https://usa.infinitinews.com/en-US/releases/us-2017-infiniti-q60-press-kit
EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	4425	1805	1495	INFINITI Q30 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q30-Catalogue-EN.pdf
EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	4425	1805	1475	INFINITI Q30 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q30-Catalogue-EN.pdf
EU-INFINITI-QX4-JR50-SUV-01	4671	1839	1730	Automobile-Catalog 1997 Infiniti QX4 specifications	https://www.automobile-catalog.com/car/1997/2166410/infiniti_qx4.html
```

## 下一步优先处理

1. 消除最后一个既有 PENDING：Ktype `14062`，确定应按输入代际还是 4.1L 发动机对应的 FY33 代际落盘。
2. 闭合 EX25、EX35，并完成全部 Infiniti 输入。
3. 批量处理 Innocenti Mini、Irmscher、Isdera 与 Isorivolta。
4. 随后处理 Isuzu Gemini、Impulse、Piazza、Midi、Trooper等高复用组。
5. D-Max、Campo、Elf 最后按驾驶室、底盘、轴距及货斗边界集中拆分。

推进信号：CONTINUE

[1]: https://www.edmunds.com/infiniti/m30/1991/convertible/features-specs/ "Used 1991 INFINITI M30 Convertible Specs & Features | Edmunds"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已消除 Infiniti Ktype `14062` 的代际冲突：4.1L `VH41DE` 只对应第二代 FY33，因此按发动机与车型身份优先于错误生产期，复用已建的 FY33 改款前尺寸组。Infiniti 官方资料确认 1997 Q45 使用 4.1L V8。([infiniti.com][1])
* 闭合 EX25 中国市场外廓与 EX35 北美市场外廓。两者与此前欧洲 EX37/QX50 数据存在市场规格差异，独立建组，不覆盖现有 J50 组。EX35 工厂维修资料明确区分无行李架高度，并给出 `4630 × 1800 × 1570 mm`；EX25 市场规格为 `4638 × 1803 × 1598 mm`。([www.slideshare.net][2])
* 闭合 Isdera Commendatore 112i 与 1991 年改款后的 Imperator 108i Series II。([汽车目录][3])
* 闭合 Iso Rivolta Fidia IR10、Grifo IR8 和 Lele IR6；三个车型分别保持独立外廓。([汽车目录][4])

## 当前批次进度

* READY 映射：53 行，覆盖 48 个输入 Ktype。
* PENDING／尚未闭合输入：52 个 Ktype。
* 已确认尺寸组：31 个。
* 前几轮明确输出的 PENDING 行已全部解决；剩余阻塞来自尚未处理的 Innocenti、Irmscher及 Isuzu 车型。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56851	56851	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-04	MEDIUM	中国市场EX25外廓。	READY
14883	14883	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-03	HIGH	北美EX35无车顶行李架外廓。	READY
14062	14062	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	MEDIUM	4.1L发动机确认FY33；输入生产期为上游冲突。	READY
12726	12726	Coupe	Commendatore 112i		2	EU-ISDERA-COMMENDATORE-112I-COUPE-01	HIGH	112i双门鸥翼轿跑外廓。	READY
12727	12727	Coupe	Imperator 108i Series II		2	EU-ISDERA-IMPERATOR-108I-SERIES-II-COUPE-01	HIGH	1991年改款后Series II外廓。	READY
147386	147386	Sedan	Fidia IR10	IR10	4	EU-ISORIVOLTA-FIDIA-IR10-SEDAN-01	HIGH	IR10四门轿车外廓。	READY
147385	147385	Coupe	Grifo IR8	IR8	2	EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	HIGH	IR8双门轿跑外廓。	READY
147384	147384	Coupe	Lele IR6	IR6	2	EU-ISORIVOLTA-LELE-IR6-COUPE-01	HIGH	IR6双门2+2轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-EX-QX50-J50-SUV-04	4638	1803	1598	AutoHome 2013 Infiniti EX25 specifications;2008 Infiniti EX35 official press information	https://www.autohome.com.cn/news/201207/363316.html;https://usa.infinitinews.com/en-US/releases/release-4a3f9f0bb1264896872dc2e3c322a08a-2008-infiniti-ex35-press-kit
EU-INFINITI-EX-QX50-J50-SUV-03	4630	1800	1570	2008 Infiniti EX35 factory service manual	https://www.slideshare.net/slideshow/2008-infiniti-ex35-service-repair-manual/82619083
EU-ISDERA-COMMENDATORE-112I-COUPE-01	4665	1885	1040	Automobile-Catalog Isdera Commendatore 112i;UltimateSpecs Isdera Commendatore 112i	https://www.automobile-catalog.com/car/2000/1271690/isdera_commendatore_112i_6l.html;https://www.ultimatespecs.com/car-specs/Isdera/3644/Isdera-Commendatore-112i.html
EU-ISDERA-IMPERATOR-108I-SERIES-II-COUPE-01	4220	1835	1135	Automobile-Catalog 1991 Isdera Imperator 108i;Auto Bild Klassik Isdera Imperator 108i	https://www.automobile-catalog.com/car/1991/1271615/isdera_imperator_108i_5l-32v.html;https://www.autobild.de/klassik/artikel/isdera-imperator-108i-3674835.html
EU-ISORIVOLTA-FIDIA-IR10-SEDAN-01	4970	1780	1320	Automobile-Catalog 1973 Iso Rivolta Fidia IR10	https://www.automobile-catalog.com/car/1973/1251440/iso_rivolta_fidia_ir_10.html
EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	4600	1770	1200	Automobile-Catalog 1972 Iso Grifo IR8	https://www.automobile-catalog.com/car/1972/1251500/iso_grifo_ir_8.html
EU-ISORIVOLTA-LELE-IR6-COUPE-01	4650	1750	1350	Automobile-Catalog 1972 Iso Rivolta Lele	https://www.automobile-catalog.com/car/1972/1251230/iso_rivolta_lele_350_automatic.html
```

## 下一步优先处理

1. 处理 Innocenti Mini 90/120、Mille 改款与 De Tomaso 宽体差异，避免把 1974—1982 全生产期错误合并。
2. 闭合 Irmscher Coupe、GT、Omega Caravan 和 Senator，优先复用对应 Opel 基础车身尺寸组。
3. 批量完成 Isuzu Gemini、Impulse、Piazza和 Midi。
4. 处理 Trooper 封闭式、开放式以及不同代际外廓。
5. 最后集中拆分 Campo、D-Max、Elf 的驾驶室、轴距、货斗和底盘分支。

推进信号：CONTINUE

[1]: https://www.infiniti.com/vehicles/legacy/q45.html?utm_source=chatgpt.com "INFINITI Q45 Luxury Sedan | INFINITI Global"
[2]: https://www.slideshare.net/slideshow/2008-infiniti-ex35-service-repair-manual/82619083?utm_source=chatgpt.com "2008 INFINITI EX35 Service Repair Manual | PDF"
[3]: https://www.automobile-catalog.com/car/2000/1271690/isdera_commendatore_112i_6l.html?utm_source=chatgpt.com "2000 Isdera Commendatore 112i 5L Specs Review (290 ..."
[4]: https://www.automobile-catalog.com/car/1973/1251440/iso_rivolta_fidia_ir_10.html?utm_source=chatgpt.com "1973 Iso Rivolta Fidia IR 10 (man. 5) (model for Europe North ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Innocenti Mini 90/120 标准车身与 De Tomaso 加宽车身；三个普通动力 Ktype 复用标准组，De Tomaso 独立建组。([汽车目录][1])
* 闭合 Irmscher Coupe、GT 和 Senator。
* Irmscher Omega Caravan Ktype `12682` 覆盖 1990 年改款前后两种外廓，已拆分 `prefl` 与 `facelift`，不再用单一尺寸覆盖整个生产期。([汽车目录][2])
* 闭合 Isuzu Impulse 第二代 JT22 与 Piazza 第一代 JR130。([carqu.es][3])

## 当前批次进度

* READY 映射：65 行，覆盖 59 个输入 Ktype。
* 尚未闭合：41 个输入 Ktype。
* 已确认尺寸组：40 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5079	5079	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5084	5084	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5080	5080	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5082	5082	Hatchback	Mini De Tomaso		3	EU-INNOCENTI-MINI-DE-TOMASO-HATCHBACK-01	HIGH	De Tomaso加宽三门车身。	READY
12679	12679	Coupe	Tigra A	S93	2	EU-IRMSCHER-TIGRA-A-COUPE-01	HIGH	Tigra A双门轿跑车身。	READY
12680	12680	Coupe	GT		2	EU-IRMSCHER-GT-COUPE-01	HIGH	Irmscher GT独立双门车身。	READY
12682_prefl	12682	Wagon	Omega A		5	EU-IRMSCHER-OMEGA-A-WAGON-PREFL-01	HIGH	1990年改款前Caravan外廓。	READY
12682_facelift	12682	Wagon	Omega A		5	EU-IRMSCHER-OMEGA-A-WAGON-FACELIFT-01	HIGH	1990年改款后Caravan外廓。	READY
12681	12681	Sedan	Senator B		4	EU-IRMSCHER-SENATOR-B-SEDAN-01	HIGH	Senator B四门轿车。	READY
18657	18657	Coupe	Impulse II	JT22	3	EU-ISUZU-IMPULSE-JT22-COUPE-01	HIGH	JT22三门轿跑车身。	READY
18658	18658	Coupe	Impulse II	JT22	3	EU-ISUZU-IMPULSE-JT22-COUPE-01	HIGH	JT22三门轿跑车身。	READY
125804	125804	Coupe	Piazza I	JR130	3	EU-ISUZU-PIAZZA-JR130-COUPE-01	HIGH	JR130三门轿跑车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INNOCENTI-MINI-90-120-HATCHBACK-01	3120	1500	1380	Automobile-Catalog Innocenti Mini 90	https://www.automobile-catalog.com/car/1979/39995/innocenti_mini_90.html
EU-INNOCENTI-MINI-DE-TOMASO-HATCHBACK-01	3130	1524	1380	Automobile-Catalog Innocenti Mini De Tomaso	https://www.automobile-catalog.com/car/1976/44660/innocenti_mini_de_tomaso.html
EU-IRMSCHER-TIGRA-A-COUPE-01	3922	1604	1340	Automobile-Catalog Irmscher Opel Tigra	https://www.automobile-catalog.com/car/1997/1272110/irmscher_opel_tigra.html
EU-IRMSCHER-GT-COUPE-01	4590	1780	1340	Automobile-Catalog Irmscher GT	https://www.automobile-catalog.com/car/1988/1271765/irmscher_gt.html
EU-IRMSCHER-OMEGA-A-WAGON-PREFL-01	4730	1772	1450	Automobile-Catalog Irmscher Opel Omega Caravan phase I	https://www.automobile-catalog.com/car/1989/1271885/irmscher_opel_omega_caravan_3_6i.html
EU-IRMSCHER-OMEGA-A-WAGON-FACELIFT-01	4768	1760	1530	Automobile-Catalog Irmscher Omega A Caravan phase II	https://www.automobile-catalog.com/car/1992/2470670/irmscher_c30e.html
EU-IRMSCHER-SENATOR-B-SEDAN-01	4845	1763	1430	Automobile-Catalog Irmscher Opel Senator 4.0i	https://www.automobile-catalog.com/car/1990/1271945/irmscher_opel_senator_4_0i.html
EU-ISUZU-IMPULSE-JT22-COUPE-01	4150	1695	1300	Auto-Data Isuzu Impulse Coupe 1.6i	https://www.auto-data.net/en/isuzu-impulse-coupe-1.6-i-130hp-15957
EU-ISUZU-PIAZZA-JR130-COUPE-01	4310	1655	1300	Automobile-Catalog 1981 Isuzu Piazza XE	https://www.automobile-catalog.com/car/1981/1256330/isuzu_piazza_xe.html
```

## 下一步优先处理

1. 按第二代、第三代及 Hatchback/Sedan 分支批量闭合 Isuzu Gemini。
2. 处理 Midi 改款前后 Van 外廓。
3. 闭合 Trooper I、II、III 的封闭式与开放式车身。
4. 最后集中拆分 Campo、D-Max、Elf 的驾驶室、轴距、货斗及底盘车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/39995/innocenti_mini_90.html?utm_source=chatgpt.com "1979 Innocenti Mini 90 (man. 4) (model for Europe ) car ..."
[2]: https://www.automobile-catalog.com/car/1989/1271885/irmscher_opel_omega_caravan_3_6i.html?utm_source=chatgpt.com "1989 Irmscher Opel Omega Caravan 3.6i Specs Review (145 kW / 197 PS / 194 hp) (since mid-year 1989 for Europe )"
[3]: https://www.carqu.es/coches/isuzu-impulse-coupe-1-6-i-130-hp-1990-1995-1211ca3a?utm_source=chatgpt.com "Ficha técnica Isuzu Impulse Coupe: 1.6 i (130 Hp), 1990 - 1995"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合第二代 Gemini 1.5 Hatchback：Ktype `125793` 跨越 1987 年改款，改款前后车长、车宽不同，拆分为 `prefl` 与 `facelift` 两个物理分支。([汽车目录][1])
* 闭合第二代 Gemini GTI 16V 的 JT190 三门车身，独立于普通 1.5 Hatchback 尺寸组。([汽车目录][2])
* 闭合第三代 Gemini 汽油 Hatchback 与 Sedan；同一车身内的发动机和驱动差异复用尺寸组。第三代底盘代码边界按 JT151F、JT191F、JT191S、JT641F 区分。([汽车目录][3])
* Ktype `18651` 暂不绑定：输入标记为 1.7 TD Hatchback，但现有 JT641F 资料均指向四门 Sedan，尚未确认实际存在对应柴油 Hatchback 外廓。([SBI Motor][4])

## 当前批次进度

* READY 映射：77 行，覆盖 70 个输入 Ktype。
* 明确 PENDING：1 行。
* 尚未闭合输入：30 个 Ktype，其中 29 个尚待处理。
* 已确认尺寸组：45 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125793_prefl	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	HIGH	1985至1987年改款前普通三门车身。	READY
125793_facelift	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	HIGH	1987年改款后普通三门车身。	READY
125799	125799	Hatchback	Gemini II	JT190	3	EU-ISUZU-GEMINI-II-GTI-HATCHBACK-01	HIGH	JT190 GTI 16V三门低车身外廓。	READY
18647	18647	Hatchback	Gemini III	JT151F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
18648	18648	Hatchback	Gemini III	JT151F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
18649	18649	Hatchback	Gemini III	JT191S	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	HIGH	JT191S四驱三门Hatchback外廓。	READY
18650	18650	Hatchback	Gemini III	JT191F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
18656	18656	Sedan	Gemini III	JT191F	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT191F四门Sedan外廓。	READY
18653	18653	Sedan	Gemini III	JT151F	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT151F四门Sedan外廓。	READY
18654	18654	Sedan	Gemini III	JT151F	4	EU-ISUZU-GEMINI-III-SEDAN-01	MEDIUM	第三代四门Sedan外廓。	READY
18655	18655	Sedan	Gemini III	JT191S	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT191S四驱涡轮四门Sedan外廓。	READY
18651	18651	Hatchback	Gemini III		3		LOW	1.7 TD已确认JT641F Sedan，但输入Hatchback物理边界尚未闭合。	PENDING: 1.7 TD Hatchback车身证据冲突
18652	18652	Sedan	Gemini III	JT641F	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT641F柴油四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	3960	1600	1380	Automobile-Catalog 1986 Isuzu FF Gemini C/C Hatchback	https://www.automobile-catalog.com/car/1986/1258055/isuzu_ff_gemini_cc_3door_hatchback.html
EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	3995	1615	1380	Automobile-Catalog 1987 Isuzu Gemini 1.5 LS Hatchback	https://www.automobile-catalog.com/car/1987/56345/isuzu_gemini_1_5_ls_hatchback_cat.html
EU-ISUZU-GEMINI-II-GTI-HATCHBACK-01	4010	1615	1365	Automobile-Catalog 1989 Isuzu Gemini GTI 16V Hatchback	https://www.automobile-catalog.com/car/1989/1259060/isuzu_gemini_gti_16v_hatchback.html
EU-ISUZU-GEMINI-III-HATCHBACK-01	4185	1695	1325	Automobile-Catalog 1991 Isuzu Gemini Irmscher R Hatchback;Car From Japan Isuzu Gemini OZ specifications	https://www.automobile-catalog.com/car/1991/1262345/isuzu_gemini_irmscher_r_hatchback.html;https://carfromjapan.com/specifications/isuzu/gemini/5819751b2afaa2c4b2878639
EU-ISUZU-GEMINI-III-SEDAN-01	4195	1680	1390	Automobile-Catalog 1990 Isuzu Gemini C/C 1.5;TCV Isuzu Gemini JT641F 1.7 Diesel	https://www.automobile-catalog.com/car/1990/1261145/isuzu_gemini_cc_1_5.html;https://www.tc-v.com/specifications/isuzu/gemini/c%2Fc-l_mt_1.7diesel/20676/
```

## 下一步优先处理

1. 解决 Ktype `18651` 的 Hatchback 与 JT641F Sedan 冲突。
2. 按 SWB、LWB及 2WD、4WD 高度差异处理 Isuzu Midi。
3. 拆分 Trooper 各代封闭式、开放式以及三门、五门外廓。
4. 集中处理 Campo、D-Max 与 Elf 的驾驶室、轴距、货斗和底盘车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/1258055/isuzu_ff_gemini_cc_3door_hatchback.html?utm_source=chatgpt.com "1986 Isuzu FF Gemini C/C 3door Hatchback Specs Review (63 kW / 86 PS / 84 hp) (up to mid-year 1986 for Japan )"
[2]: https://www.automobile-catalog.com/car/1989/1259060/isuzu_gemini_gti_16v_hatchback.html?utm_source=chatgpt.com "1989 Isuzu Gemini GTi 16V Hatchback (man. 5)"
[3]: https://www.automobile-catalog.com/car/1991/1262345/isuzu_gemini_irmscher_r_hatchback.html?utm_source=chatgpt.com "1991 Isuzu Gemini Irmscher R Hatchback Specs Review ..."
[4]: https://sbimotor.com/cars/ISUZU/GEMINI/856784609?utm_source=chatgpt.com "SBI Motor Japan : Japanese Used Cars for Sale."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Ktype `18651` 的 `Hatchback` 标注判定为上游车身形式错误：1.7 TD 对应 `JT641F` 四门 Sedan。同步修正 Ktype `18652`，将两个柴油 Ktype 从汽油 Sedan 尺寸组移至独立柴油 Sedan 组。该柴油车身高度为 1370 mm，不与此前 1390 mm 的汽油 Sedan 合并。([SBI Motor][1])
* 闭合 Isuzu Midi I：`94000` 四驱版本对应短轴车身，`98000/98000N` 后驱版本对应长轴车身；发动机差异不再重复建组。短轴尺寸为 `4350 × 1690 × 1950 mm`，长轴尺寸为 `4690 × 1690 × 1950 mm`。([五十铃车主社区][2])

## 当前批次进度

* READY 映射：83 行，覆盖 76 个输入 Ktype。
* 尚未闭合输入：24 个 Ktype。
* 当前批次 PENDING 口径：24。
* 已确认尺寸组：48 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18651	18651	Sedan	Gemini III	JT641F	4	EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	MEDIUM	1.7 TD对应JT641F四门车身；输入Hatchback标注纠正。	READY
18652	18652	Sedan	Gemini III	JT641F	4	EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	HIGH	JT641F柴油四门Sedan外廓。	READY
7836	7836	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000后驱长轴厢式车身。	READY
10786	10786	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-VAN-SWB-01	MEDIUM	94000四驱短轴厢式车身。	READY
8819	8819	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000后驱长轴厢式车身。	READY
10788	10788	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-VAN-SWB-01	MEDIUM	94000四驱短轴厢式车身。	READY
10787	10787	Van	Midi I	98000N	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000N后驱长轴厢式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	4195	1680	1370	Auto-Data Isuzu Gemini JT 1.7 TD;SBI Motor Isuzu Gemini JT641F	https://www.auto-data.net/en/isuzu-gemini-jt-1.7-td-88hp-automatic-24443;https://sbimotor.com/cars/ISUZU/GEMINI/856784609
EU-ISUZU-MIDI-I-VAN-LWB-01	4690	1690	1950	Auta5P Isuzu Midi Van 2.2 D;Quality Tested Isuzu Midi application catalogue	https://auta5p.eu/lang/en/katalog/auto.php?idf=Isuzu-Midi-Van-2.2-D-17636;https://qualitytested.it/en/app/src-cod/?src=PA902JM
EU-ISUZU-MIDI-I-VAN-SWB-01	4350	1690	1950	Drive.Place Isuzu Midi I 2.0 Van;Quality Tested Isuzu Midi application catalogue	https://isuzu.drive.place/midi/i/group_furgon/777242;https://qualitytested.it/en/app/src-cod/?src=PA902JM
```

## 下一步优先处理

1. 拆分 Trooper I 的封闭式长轴车身与两门 Canvas-Top 开放式车身。
2. 拆分 Trooper II 的三门短轴、五门长轴及开放式车身。
3. 处理 Trooper III 的三门开放式与五门封闭式外廓。
4. 最后集中处理 Campo、D-Max I、D-Max II、D-Max III 和 Elf 的驾驶室、轴距、货斗及底盘车分支。

推进信号：CONTINUE

[1]: https://sbimotor.com/cars/ISUZU/GEMINI/856784609?utm_source=chatgpt.com "SBI Motor Japan : Japanese Used Cars for Sale."
[2]: https://isuzu.drive.place/midi/i/group_furgon/777242?utm_source=chatgpt.com "Isuzu Midi I 2.0 MT 83 hp Van — specifications"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Trooper II 3.2 的两种物理车身：Ktype `17446` 对应五门长轴封闭式车身；Ktype `17447` 的 TecDoc“开放式越野车”节点实际对应三门短轴车身，并非软顶敞篷。([汽车数据网][1])
* 闭合 Trooper III 3.0 DTI 的三门短轴和五门长轴车身。Ktype `17455` 对应三门短轴，Ktype `121922` 对应五门长轴；两个外廓不能共用尺寸组。([lakiauto.ee][2])

## 当前批次进度

* READY 映射：87 行，覆盖 80 个输入 Ktype。
* PENDING／尚未闭合：20 个输入 Ktype。
* 已确认尺寸组：52 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17446	17446	SUV	Trooper II	UB	5	EU-ISUZU-TROOPER-II-SUV-LWB-01	HIGH	五门长轴封闭式车身。	READY
17447	17447	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-SUV-SWB-01	HIGH	TecDoc开放式越野车节点对应三门短轴固定车顶车身。	READY
17455	17455	SUV	Trooper III		3	EU-ISUZU-TROOPER-III-SUV-SWB-01	HIGH	三门短轴固定车顶车身。	READY
121922	121922	SUV	Trooper III		5	EU-ISUZU-TROOPER-III-SUV-LWB-01	HIGH	五门长轴封闭式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-TROOPER-II-SUV-LWB-01	4660	1745	1850	Auto-Data Isuzu Trooper LS 3.2 V6	https://www.auto-data.net/en/isuzu-trooper-ls-3.2-i-v6-24v-190hp-15943
EU-ISUZU-TROOPER-II-SUV-SWB-01	4234	1745	1849	Drive.Place Isuzu Trooper II 3.2 three-door	https://isuzu.drive.place/trooper/ii/group_offroad_3d/396379
EU-ISUZU-TROOPER-III-SUV-SWB-01	4365	1835	1835	Auto-Data Isuzu Trooper 3.0 DTI three-door	https://www.auto-data.net/en/isuzu-trooper-3.0-dti-159hp-15938
EU-ISUZU-TROOPER-III-SUV-LWB-01	4795	1835	1840	Auto-Data Isuzu Trooper 3.0 DTI Wagon five-door	https://www.auto-data.net/en/isuzu-trooper-3.0-dti-wagon-159hp-15939
```

## 下一步优先处理

1. 拆分 Trooper I Ktype `17437` 的三门短轴、三门长轴、五门长轴以及改款前后外廓。
2. 闭合 Trooper I Soft Top Ktype `17457` 的改款前后长度和高度变化。
3. 集中处理 Campo 与 D-Max I、II、III 的 Single Cab、Space Cab、Double Cab、底盘车、轴距及货斗分支。
4. 最后处理 Elf 底盘车，并完成全批次引用闭合检查。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/isuzu-trooper-ls-3.2-i-v6-24v-190hp-15943 "Isuzu Trooper (LS) 3.2 i V6 24V (190 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.lakiauto.ee/admin/upload/Dokumendid/pump_compressed.pdf?utm_source=chatgpt.com "TecDoc ktype 3822 | Manufacturer ALFA ROMEO | Mode"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Trooper I Ktype `17437`。该 TecDoc 节点覆盖三种已确认的封闭式物理外廓：三门短轴、三门长轴、五门长轴，因此拆成三个派生 `id`。1986 官方资料确认三门长轴版为 `4450 × 1651 × 1801 mm`；短轴三门和长轴五门分别采用对应车身规格。
* 未处理 Ktype `17457`：Soft Top 的生产期跨越外廓调整，目前不使用封闭式三门尺寸替代。

## 当前批次进度

* READY 映射：90 行，覆盖 81 个输入 Ktype。
* PENDING／尚未闭合：19 个输入 Ktype。
* 已确认尺寸组：55 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17437_3dr_swb	17437	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SUV-3D-SWB-01	MEDIUM	三门短轴封闭式车身。	READY
17437_3dr_lwb	17437	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SUV-3D-LWB-01	MEDIUM	三门长轴封闭式车身。	READY
17437_5dr_lwb	17437	SUV	Trooper I	UBS52	5	EU-ISUZU-TROOPER-I-SUV-5D-LWB-01	MEDIUM	五门长轴封闭式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-TROOPER-I-SUV-3D-SWB-01	4122	1651	1844	Drive.Place Isuzu Trooper I three-door specifications	https://isuzu.drive.place/trooper/i/group_offroad_3d/396703
EU-ISUZU-TROOPER-I-SUV-3D-LWB-01	4450	1651	1801	1986 Isuzu official brief line-up brochure	https://www.xr793.com/wp-content/uploads/2020/01/1986-Isuzu-Brief-Line-Up.pdf
EU-ISUZU-TROOPER-I-SUV-5D-LWB-01	4470	1651	1821	Drive.Place Isuzu Trooper I five-door specifications	https://isuzu.drive.place/trooper/i/group_offroad_5d/396539
```

## 下一步优先处理

1. 闭合 Trooper I Soft Top Ktype `17457`，确认改款前后是否必须拆分。
2. 处理 Campo 两个 Ktype 的 Regular Cab、Space Cab及轴距分支。
3. 按代际批量闭合 D-Max I、II、III 的 Single Cab、Space／Extended Cab、Double Cab和底盘车。
4. 最后处理 Elf Ktype `115533`，完成引用闭合检查。

推进信号：CONTINUE


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Trooper I Soft Top Ktype `17457`：确认对应 `UBS52` 三门短轴软顶车身，生产期内未发现需要拆分的外廓变化。尺寸为 `4122 × 1651 × 1844 mm`，与固定顶车身尺寸值相同，但因车身结构不同独立建组。([汽车数据网][1])
* 闭合 Campo 2.2 D 后驱 Ktype `14245`：确认对应 `KBD27` 两门单排座 Pickup，尺寸为 `4700 × 1655 × 1600 mm`。([汽车数据网][2])
* Campo 4WD Ktype `14246` 同时覆盖 `KBD42`、`KBD47`，车身分支尚未完成三维闭合，本轮不创建猜测性派生行。([Autodoc][3])

## 当前批次进度

* READY 映射：92 行，覆盖 83 个输入 Ktype。
* PENDING／尚未闭合：17 个输入 Ktype。
* 已确认尺寸组：57 个。
* 剩余范围：Campo 4WD、D-Max I/II/III、Elf。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17457	17457	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SOFTTOP-SWB-01	HIGH	三门短轴软顶车身。	READY
14245	14245	Pickup	Campo KB	KBD27	2	EU-ISUZU-CAMPO-KB-PICKUP-2WD-01	MEDIUM	KBD27后驱两门单排座Pickup。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-TROOPER-I-SOFTTOP-SWB-01	4122	1651	1844	Auto-Data Isuzu Trooper Soft Top 2.2 TD;Drive.Place Isuzu Trooper I open-top specifications	https://www.auto-data.net/en/isuzu-trooper-soft-top-2.2-td-ubs52-72hp-15947;https://isuzu.drive.place/trooper/i/group_vezdehod/396610
EU-ISUZU-CAMPO-KB-PICKUP-2WD-01	4700	1655	1600	Auto-Data Isuzu Campo 2.2 D;Tunel Isuzu Campo 2.2 D specifications	https://www.auto-data.net/en/isuzu-campo-2.2-d-53hp-15953;https://tunel.az/en/catalog/isuzu/campo/isuzu-campo/2cf8175b-0287-4a3f-9a96-59fcd7e85c72
```

## 下一步优先处理

1. 拆分 Campo 4WD Ktype `14246` 的 `KBD42` 与 `KBD47` 车身边界。
2. 按 Single Cab、Extended Cab、Double Cab及底盘车闭合 D-Max I。
3. 批量处理 D-Max II 的 Pickup 与 Pritsche/Fahrgestell 分支。
4. 处理 D-Max III 柴油、BEV及底盘车分支。
5. 最后闭合 Elf Ktype `115533` 并执行完整引用检查。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/isuzu-trooper-soft-top-2.2-td-ubs52-72hp-15947 "Isuzu Trooper Soft Top 2.2 TD (UBS52) (72 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/isuzu-campo-2.2-d-53hp-15953 "Isuzu Campo 2.2 D (53 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.autodoc.parts/spares/isuzu/campo/campo-kb/14246-2-2-d-4wd-kbd42-kbd47?utm_source=chatgpt.com "Parts ISUZU Campo / Faster (KB) 2.2 D 4WD 53 hp Diesel 1983 - 1990 C223 | CAMPO KB parts catalogue AUTODOC"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 D-Max II 的 4 个 Ktype。后驱版本对应 Single Cab；四驱版本拆分为 Single Cab、Extended Cab、Double Cab。
* 2.5 CRDi 与 1.9 DDI 的四驱 Single Cab、Extended Cab 三维一致，复用同一尺寸组；后驱 Single Cab 与 Double Cab 因宽度或高度变化分别建组。三维均来自 Isuzu 官方技术资料，宽度明确不含后视镜。

## 当前批次进度

* READY 映射：100 行，覆盖 87 个输入 Ktype。
* PENDING／尚未闭合：13 个输入 Ktype。
* 已确认尺寸组：63 个。
* 剩余范围：D-Max I、D-Max II 底盘车、D-Max III 柴油/BEV/底盘车、Elf。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126051	126051	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-FACELIFT-01	HIGH	后驱Single Cab车身。	READY
126055_singlecab	126055	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	HIGH	四驱Single Cab车身。	READY
126055_extendedcab	126055	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	HIGH	四驱Extended Cab车身。	READY
126055_doublecab	126055	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-FACELIFT-01	HIGH	四驱Double Cab车身。	READY
55099	55099	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-PREFL-01	HIGH	后驱Single Cab车身。	READY
55091_singlecab	55091	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	HIGH	四驱Single Cab车身。	READY
55091_extendedcab	55091	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	HIGH	四驱Extended Cab车身。	READY
55091_doublecab	55091	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-PREFL-01	HIGH	四驱Double Cab车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-FACELIFT-01	5315	1775	1685	Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	5315	1860	1780	Isuzu D-Max official technical specifications;Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf;https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	5295	1860	1780	Isuzu D-Max official technical specifications;Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf;https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-FACELIFT-01	5295	1860	1785	Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-PREFL-01	5315	1860	1685	Isuzu D-Max 2.5 official technical specifications	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf
EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-PREFL-01	5295	1865	1780	Isuzu D-Max 2.5 official technical specifications	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf
```

## 下一步优先处理

1. 闭合 D-Max I Ktype `34517`、`34518` 的 Single Cab、Extended Cab、Double Cab及底盘车分支。
2. 处理 D-Max II 底盘车 Ktype `113463`、`113464`。
3. 一次性闭合 D-Max III 柴油、BEV和底盘车尺寸组。
4. 最后处理 Elf Ktype `115533`，随后执行完整引用与唯一性检查。

推进信号：CONTINUE


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 D-Max III 柴油 Pickup。2019—2023 车身按 Single Cab、Extended Cab、Double Cab 分组；2024 外观改款后，Single Cab 车长由 5305 mm 增至 5320 mm，Extended/Double Cab 由 5265 mm 增至 5280 mm，因此改款前后不能共用尺寸组。后驱版本仅关联 Single Cab，四驱版本覆盖三种驾驶室。
* Ktype `801355`、`802421` 属于后续动力更新，但未改变已经确认的改款后外廓，因此直接复用改款后尺寸组，不因发动机变化重复建组。
* 闭合 D-Max EV Double Cab。Ktype `801987` 与 `802844` 对应同一量产车身，采用 Isuzu 官方公布的含原厂车顶行李架高度：`5280 × 1870 × 1810 mm`。([isuzu.co.jp][1])
* D-Max III 底盘车 Ktype `157597` 暂未闭合：官方资料确认其可能覆盖 Single Cab、Space Cab 和 Crew Cab，但底盘车高度标注会受后装车身影响，暂不能将带货斗完成车高度直接写入尺寸组。

## 当前批次进度

* READY 映射：110 行，覆盖 93 个输入 Ktype。
* PENDING／尚未闭合：7 个输入 Ktype。
* 已确认尺寸组：70 个。
* 剩余 Ktype：`14246`、`34517`、`34518`、`113463`、`113464`、`157597`、`115533`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
146714	146714	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	HIGH	改款前后驱Single Cab车身。	READY
146715_singlecab	146715	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	HIGH	改款前四驱Single Cab车身。	READY
146715_extendedcab	146715	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-PREFL-01	HIGH	改款前四驱Extended Cab车身。	READY
146715_doublecab	146715	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	改款前四驱Double Cab车身。	READY
801355	801355	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	HIGH	改款后后驱Single Cab车身。	READY
802421_singlecab	802421	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	HIGH	改款后四驱Single Cab车身。	READY
802421_extendedcab	802421	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-FACELIFT-01	HIGH	改款后四驱Extended Cab车身。	READY
802421_doublecab	802421	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-FACELIFT-01	HIGH	改款后四驱Double Cab车身。	READY
801987	801987	Pickup	D-Max III EV		4	EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	HIGH	全时四驱Double Cab量产车身。	READY
802844	802844	Pickup	D-Max III EV		4	EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	HIGH	全时四驱Double Cab量产车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	5305	1810	1770	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-PREFL-01	5265	1870	1790	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-PREFL-01	5265	1870	1790	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	5320	1810	1770	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-FACELIFT-01	5280	1870	1790	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-FACELIFT-01	5280	1870	1790	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	5280	1870	1810	Isuzu Motors D-Max EV official production announcement	https://www.isuzu.co.jp/world/newsroom/details/20250429_1.html
```

## 下一步优先处理

1. 闭合 D-Max I Pickup 与底盘车 Ktype `34517`、`34518`。
2. 闭合 D-Max II 底盘车 Ktype `113463`、`113464`。
3. 确认 D-Max III Ktype `157597` 的具体驾驶室分支及不受后装货斗影响的标准三维。
4. 解决 Campo 4WD Ktype `14246` 的 `KBD42/KBD47` 外廓边界。
5. 最后闭合 Elf Ktype `115533`，随后进行完整引用检查。

推进信号：CONTINUE

[1]: https://www.isuzu.co.jp/world/newsroom/details/20250429_1.html?utm_source=chatgpt.com "Isuzu begins production of D-MAX EV pickup truck ..."


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 闭合 D-Max II 底盘车 Ktype `113463`、`113464`。按 Single Cab 低车身、Single Cab 高车身、Space Cab、Crew Cab 拆分；后驱与四驱外廓相同的高车身 Single Cab、Crew Cab 复用同一尺寸组，不因驱动形式重复建组。
* 闭合 D-Max III 底盘车 Ktype `157597`。官方 23MY 规格覆盖 Single Cab、Space Cab、Crew Cab 三种物理驾驶室，因此输出三个派生映射；Space Cab 与 Crew Cab 三维相同，但驾驶室外形不同，分别建组。

## 当前批次进度

* READY 映射：119 行，覆盖 96 个输入 Ktype。
* PENDING／尚未闭合：4 个输入 Ktype。
* 已确认尺寸组：77 个。
* 剩余 Ktype：`14246`、`34517`、`34518`、`115533`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
113463_singlecab_lowride	113463	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-LOWRIDE-01	MEDIUM	后驱低车身Single Cab底盘车。	READY
113463_singlecab_highride	113463	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	MEDIUM	后驱高车身Single Cab底盘车。	READY
113463_crewcab	113463	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	MEDIUM	后驱Crew Cab底盘车。	READY
113464_singlecab	113464	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	MEDIUM	四驱Single Cab底盘车。	READY
113464_spacecab	113464	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-SPACECAB-HIGHRIDE-01	MEDIUM	四驱Space Cab底盘车。	READY
113464_crewcab	113464	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	MEDIUM	四驱Crew Cab底盘车。	READY
157597_singlecab	157597	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-CHASSISCAB-SINGLECAB-PREFL-01	MEDIUM	23MY四驱Single Cab底盘车。	READY
157597_spacecab	157597	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-CHASSISCAB-SPACECAB-PREFL-01	MEDIUM	23MY四驱Space Cab底盘车。	READY
157597_crewcab	157597	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-CHASSISCAB-CREWCAB-PREFL-01	MEDIUM	23MY四驱Crew Cab底盘车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-LOWRIDE-01	5040	1775	1685	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	5040	1860	1780	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-SPACECAB-HIGHRIDE-01	5020	1860	1780	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	5020	1860	1785	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-SINGLECAB-PREFL-01	5330	1870	1790	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-SPACECAB-PREFL-01	5290	1870	1800	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-CREWCAB-PREFL-01	5290	1870	1800	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
```

## 下一步优先处理

1. 闭合 Campo 4WD Ktype `14246` 的 `KBD42`、`KBD47` 车身分支。
2. 闭合 D-Max I Ktype `34517`、`34518` 的驾驶室、Pickup及底盘车分支。
3. 闭合 Elf Ktype `115533` 的驾驶室与轴距边界。
4. PENDING 清零后仅执行一次表头、唯一性、引用闭合和下载文件检查，随后直接输出 COMPLETE。

推进信号：CONTINUE


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* Ktype `34518` 已确认对应 `TFR85` 后驱车系，覆盖两门 Single Cab 和四门 Double Cab，不能继续保留单一无后缀映射。([Total Engines][1])
* Single Cab 分支已闭合。采用欧洲同代官方 4×2 Single Cab 外廓，宽度明确为不含后视镜；发动机差异不改变物理车身。
* Double Cab 后驱同时存在窄体和宽体两种外廓。现有资料确认两者尺寸不同，但窄体资料未明确宽度是否不含后视镜，宽体欧洲与澳洲市场车长亦存在差异，因此两个分支继续保持 PENDING，不创建不可靠尺寸组。([CarsGuide][2])

## 当前批次进度

* READY 映射：120 行。
* PENDING 映射：2 行。
* 已完全闭合输入 Ktype：96 个。
* 已有至少一条 READY 映射的输入 Ktype：97 个。
* 尚未完全闭合：4 个 Ktype。
* 已确认尺寸组：78 个。
* 剩余 Ktype：`14246`、`34517`、`34518`、`115533`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34518_singlecab	34518	Pickup	D-Max I	TFR85	2	EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-2WD-01	MEDIUM	TFR85后驱两门Single Cab物理分支。	READY
34518_doublecab_narrow	34518	Pickup	D-Max I	TFR85	4		MEDIUM	TFR85后驱窄体Double Cab物理分支。	PENDING: 窄体Double Cab不含后视镜宽度来源未闭合
34518_doublecab_wide	34518	Pickup	D-Max I	TFR85	4		MEDIUM	TFR85后驱宽体Double Cab物理分支。	PENDING: 宽体Double Cab欧洲市场车长边界未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-2WD-01	5155	1720	1635	Isuzu Rodeo 2011 official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/74-9340414004fe1bc33e6006doc.doc
```

## 下一步优先处理

1. 用明确标注不含后视镜宽度的资料闭合 `34518` 两个 Double Cab 分支。
2. 拆分 Campo Ktype `14246` 的 `KBD42`、`KBD47` 外廓。
3. 闭合 D-Max I 底盘车 Ktype `34517` 的驾驶室分支。
4. 闭合 Elf Ktype `115533` 的 NKR/NKS/NHR/NPR 驾驶室和轴距边界。

推进信号：CONTINUE

[1]: https://www.totalengines.com.au/Part/Isuzu/D-MAX/TFR/Head-set/nason/1407310/Head-Set.aspx "Nason Head Set Fits Isuzu D-MAX TFR TFR85 Ute/Single Cab [06/2012 to 10/2012] (3.0L 4JJ1-TCX 4 Cyl DOHC I/C Turbo CRD)"
[2]: https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010 "Isuzu D-Max Dimensions 2010 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 已闭合 D-Max I 底盘车 Ktype `34517`。该 Ktype 对应 2007—2012 年 `TFR/TFS` 3.0 D 4×4 平台/底盘车；按官方规格拆分为 Single Cab、Space Cab、Crew Cab 三种物理驾驶室。三组宽度均为明确不含后视镜口径。([AUTODOC][1])
* 三种底盘车外廓分别为：Single Cab `5025 × 1800 × 1730 mm`、Space Cab `4905 × 1800 × 1735 mm`、Crew Cab `4925 × 1800 × 1750 mm`。([Scribd][2])

## 当前批次进度

* READY 映射：123 行。
* 明确 PENDING 映射：2 行。
* 已完全闭合输入 Ktype：97 个。
* 尚未完全闭合：3 个 Ktype。
* 已确认尺寸组：81 个。
* 剩余 Ktype：`14246`、`34518`、`115533`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34517_singlecab	34517	Pickup	D-Max I	TFS85	2	EU-ISUZU-D-MAX-I-CHASSISCAB-SINGLECAB-4WD-01	MEDIUM	四驱Single Cab底盘车。	READY
34517_spacecab	34517	Pickup	D-Max I	TFS85	4	EU-ISUZU-D-MAX-I-CHASSISCAB-SPACECAB-4WD-01	MEDIUM	四驱Space Cab底盘车。	READY
34517_crewcab	34517	Pickup	D-Max I	TFS85	4	EU-ISUZU-D-MAX-I-CHASSISCAB-CREWCAB-4WD-01	MEDIUM	四驱Crew Cab底盘车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-I-CHASSISCAB-SINGLECAB-4WD-01	5025	1800	1730	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
EU-ISUZU-D-MAX-I-CHASSISCAB-SPACECAB-4WD-01	4905	1800	1735	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
EU-ISUZU-D-MAX-I-CHASSISCAB-CREWCAB-4WD-01	4925	1800	1750	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
```

## 下一步优先处理

1. 闭合 Ktype `34518` 的后驱 Double Cab 低车身与高车身分支，替换现有两条 PENDING 映射。
2. 确认 Campo Ktype `14246` 中 `KBD42`、`KBD47` 的完整不含后视镜三维。
3. 闭合 Elf Ktype `115533` 的驾驶室、底盘代码及轴距外廓分支。
4. 三个 Ktype 全部闭合后，仅执行一次表头、唯一性、引用关系和下载文件机械检查，随后直接输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.autodoc.de/autoteile/radschrauben-und-radmuttern-10313/isuzu/d-max/d-max-pritsche-fahrgestell-8dh/34517-3-0-d-4x4?utm_source=chatgpt.com "Radschrauben und Radmuttern ISUZU D-Max I Pritsche / Fahrgestell (TFR, TFS) 3.0 D 4x4 163 PS Diesel 120 kW 2007 - 2012 4JJ1-TC"
[2]: https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs "Isuzu D-MAX Technical Specifications | PDF | Manual Transmission | Four Wheel Drive"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 已闭合 Ktype `34518` 的两个后驱 Double Cab 分支：低车身窄体为 `4925 × 1720 × 1660 mm`，高车身宽体为 `5030 × 1800 × 1735 mm`。两者外廓不同，替换上一轮两条 PENDING 映射，不能合并为一个尺寸组。([CarsGuide][1])
* Campo Ktype `14246` 继续保持 PENDING：`KBD42` 与 `KBD47` 均被该 Ktype 覆盖，但现有整车资料与同期车型手册的车长口径不一致，暂不创建猜测性尺寸组。([Brembo Parts][2])
* Elf Ktype `115533` 继续保持 PENDING：3.1L `4JG2` 可对应多种 NHR69/NKR69 底盘和驾驶室，而现有车辆页面尺寸受货厢或后装设备影响，不能作为裸底盘统一三维。([Clutch Direct][3])

## 当前批次进度

* READY 映射：125 行。
* PENDING 映射：2 行。
* 已完全闭合输入 Ktype：98 个。
* 尚未完全闭合：2 个 Ktype。
* 已确认尺寸组：83 个。
* 剩余 Ktype：`14246`、`115533`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
34518_doublecab_lowride	34518	Pickup	D-Max I	TFR85	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-LOWRIDE-01	HIGH	后驱低车身窄体Double Cab。	READY
34518_doublecab_highride	34518	Pickup	D-Max I	TFR85	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-HIGHRIDE-01	HIGH	后驱高车身宽体Double Cab。	READY
14246	14246	Pickup	Campo KB		2		LOW	KBD42与KBD47物理分支尚未完成统一三维闭合。	PENDING: KBD42/KBD47外廓及尺寸口径冲突
115533	115533	Pickup	Elf V	NHR69/NKR69	2		LOW	3.1 TD底盘车覆盖多个驾驶室和轴距，现有完成车尺寸受后装车身影响。	PENDING: 底盘代码与标准裸底盘三维未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-LOWRIDE-01	4925	1720	1660	CarsGuide 2010 Isuzu D-Max dimensions;Autotrader Australia 2010 Isuzu D-Max dimensions	https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010;https://www.autotrader.com.au/isuzu/d-max/dimensions/2010
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-HIGHRIDE-01	5030	1800	1735	CarsGuide 2010 Isuzu D-Max dimensions;Carsales 2010 Isuzu D-Max LS High Ride specifications	https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010;https://www.carsales.com.au/research/isuzu/d-max/2010/ls-high-ride/
```

## 下一步优先处理

1. 用同一市场、同一车身状态的资料闭合 Campo `KBD42` 与 `KBD47`，必要时按两个车身代码派生。
2. 识别 Elf `115533` 实际覆盖的 NHR69/NKR69 驾驶室和轴距，只采用未安装后装货厢的底盘车三维。
3. 两个 Ktype 闭合后立即执行一次机械检查并输出两张完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010 "Isuzu D-Max Dimensions 2010 - Length, Width, Height, Turning Circle, Ground Clearance, Wheelbase & Size | CarsGuide"
[2]: https://www.bremboparts.com/africa/en/catalogue/isuzu-campo-kb-2-2-d-4wd-kbd42-kbd47/000014246-1?utm_source=chatgpt.com "Pads and Discs for ISUZU CAMPO (KB) 2.2 D 4WD ..."
[3]: https://clutchdirect.com.au/products/v1675n-12018?srsltid=AfmBOoo8cj-2l1SFJTyjAEAYVzCYWz8ChBQKcEP0LnoDfY-tI1MvTiR4&utm_source=chatgpt.com "Isuzu NKR Series (1993+) 3.1 Ltr, 4JG2 OEM PHC"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_7101-7200_ktype_dimension_mapping_final.tsv
- left18448_7101-7200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* Campo Ktype `14246` 已按 `KBD42`、`KBD47` 两个明确车身代码拆分，两者车身长度、宽度和高度不同，不再保留基础 PENDING 行。([BE FORWARD: Japanese Used Cars for Sale][1])
* Elf Ktype `115533` 按输入的后轮驱动边界拆分为 `NHR69`、`NKR69` 两种窄体单排驾驶室底盘车；四驱 `NHS69` 和非 3.1 TD 的宽体 NPR 分支未混入。([autodoc24.fr][2])
* 已完成机械检查：映射表 10 列、尺寸组表 6 列；`id` 与 `DIMENSION_GROUP_ID` 唯一；全部引用闭合；无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100 个
* READY 映射：129 行
* PENDING 映射：0 行
* DIMENSION_GROUP：87 个
* 数据阶段和机械收尾均已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56851	56851	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-04	MEDIUM	中国市场EX25外廓。	READY
14883	14883	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-03	HIGH	北美EX35无车顶行李架外廓。	READY
34787	34787	SUV	EX J50	J50	5	EU-INFINITI-EX-QX50-J50-SUV-01	HIGH	J50五门汽油版外廓。	READY
18811	18811	SUV	FX I	S50	5	EU-INFINITI-FX-S50-SUV-01	HIGH	S50五门SUV外廓。	READY
18812	18812	SUV	FX I	S50	5	EU-INFINITI-FX-S50-SUV-01	HIGH	S50五门SUV外廓。	READY
59011	59011	SUV	FX II	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
14885	14885	Sedan	G35 V35	V35	4	EU-INFINITI-G35-V35-SEDAN-01	HIGH	V35四门轿车。	READY
34794	34794	Coupe	G37	CV36	2	EU-INFINITI-G-Q60-CV36-COUPE-01	HIGH	CV36双门轿跑。	READY
34797	34797	Convertible	G37	HV36	2	EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	HIGH	HV36双门敞篷车。	READY
14039	14039	Sedan	G20 P10	P10	4	EU-INFINITI-G20-P10-SEDAN-01	HIGH	P10四门轿车。	READY
14040	14040	Sedan	I30 A32	A32	4	EU-INFINITI-I30-A32-SEDAN-01	HIGH	A32四门轿车。	READY
14059	14059	Sedan	J30 Y32	Y32	4	EU-INFINITI-J30-Y32-SEDAN-01	HIGH	Y32四门轿车。	READY
34803	34803	Sedan	M Y51	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
34804	34804	Sedan	M Y51	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
14060	14060	Coupe	M30	F31	2	EU-INFINITI-M30-F31-COUPE-01	HIGH	F31双门轿跑。	READY
14061	14061	Convertible	M30	F31	2	EU-INFINITI-M30-F31-CONVERTIBLE-01	HIGH	F31双门敞篷外廓。	READY
117841	117841	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	90kW 1.6T标准悬架外廓。	READY
117842_standard	117842	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	115kW 1.6T标准悬架外廓。	READY
117842_sport	117842	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	115kW 1.6T Sport降低悬架外廓。	READY
117844	117844	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	1.5D标准悬架外廓。	READY
118526	118526	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.0T前驱Sport外廓。	READY
117843	117843	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.0T四驱Sport外廓。	READY
117846_standard	117846	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	2.2D标准悬架外廓。	READY
117846_sport	117846	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.2D Sport降低悬架外廓。	READY
117847_standard	117847	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	HIGH	2.2D四驱标准悬架外廓。	READY
117847_sport	117847	Hatchback	Q30	H15	5	EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	HIGH	2.2D四驱Sport降低悬架外廓。	READY
14062	14062	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	MEDIUM	4.1L发动机确认FY33；输入生产期为上游冲突。	READY
14063	14063	Sedan	Q45 G50	G50	4	EU-INFINITI-Q45-G50-SEDAN-01	HIGH	G50四门轿车。	READY
34771_prefl	34771	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	HIGH	1997-1998改款前外廓。	READY
34771_facelift	34771	Sedan	Q45 II	FY33	4	EU-INFINITI-Q45-FY33-SEDAN-FACELIFT-01	HIGH	1999-2001改款后外廓。	READY
105688_standard	105688	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-STANDARD-01	HIGH	普通前后保险杠外廓。	READY
105688_sport	105688	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-SPORT-01	HIGH	Sport保险杠造成车长差异。	READY
119719	119719	Sedan	Q50	V37	4	EU-INFINITI-Q50-V37-SEDAN-REDSPORT-01	HIGH	Red Sport低车身外廓。	READY
100191	100191	Coupe	Q60 I	CV36	2	EU-INFINITI-G-Q60-CV36-COUPE-01	HIGH	CV36双门轿跑。	READY
100192	100192	Convertible	Q60 I	HV36	2	EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	HIGH	HV36双门敞篷车。	READY
121986	121986	Coupe	Q60 II	CV37	2	EU-INFINITI-Q60-CV37-COUPE-01	HIGH	CV37双门轿跑外廓。	READY
121989	121989	Coupe	Q60 II	CV37	2	EU-INFINITI-Q60-CV37-COUPE-01	HIGH	CV37双门轿跑外廓。	READY
100926	100926	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
100925	100925	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
110819	110819	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-FACELIFT-01	HIGH	Y51改款后四门轿车。	READY
107309	107309	Sedan	Q70	Y51	4	EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	HIGH	Y51改款前四门轿车。	READY
14088	14088	SUV	QX4	JR50	5	EU-INFINITI-QX4-JR50-SUV-01	HIGH	JR50标准车顶五门SUV外廓。	READY
100723	100723	SUV	QX50 I	J50	5	EU-INFINITI-EX-QX50-J50-SUV-02	HIGH	J50五门3.0D外廓。	READY
100724	100724	SUV	QX50 I	J50	5	EU-INFINITI-EX-QX50-J50-SUV-01	HIGH	J50五门汽油版外廓。	READY
112948	112948	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
100721	100721	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
117608	117608	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
100722	100722	SUV	QX70	S51	5	EU-INFINITI-FX-QX70-S51-SUV-01	HIGH	S51五门SUV外廓。	READY
5079	5079	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5084	5084	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5080	5080	Hatchback	Mini 90/120		3	EU-INNOCENTI-MINI-90-120-HATCHBACK-01	HIGH	标准三门车身。	READY
5082	5082	Hatchback	Mini De Tomaso		3	EU-INNOCENTI-MINI-DE-TOMASO-HATCHBACK-01	HIGH	De Tomaso加宽三门车身。	READY
12679	12679	Coupe	Tigra A	S93	2	EU-IRMSCHER-TIGRA-A-COUPE-01	HIGH	Tigra A双门轿跑车身。	READY
12680	12680	Coupe	GT		2	EU-IRMSCHER-GT-COUPE-01	HIGH	Irmscher GT独立双门车身。	READY
12682_prefl	12682	Wagon	Omega A		5	EU-IRMSCHER-OMEGA-A-WAGON-PREFL-01	HIGH	1990年改款前Caravan外廓。	READY
12682_facelift	12682	Wagon	Omega A		5	EU-IRMSCHER-OMEGA-A-WAGON-FACELIFT-01	HIGH	1990年改款后Caravan外廓。	READY
12681	12681	Sedan	Senator B		4	EU-IRMSCHER-SENATOR-B-SEDAN-01	HIGH	Senator B四门轿车。	READY
12726	12726	Coupe	Commendatore 112i		2	EU-ISDERA-COMMENDATORE-112I-COUPE-01	HIGH	112i双门鸥翼轿跑外廓。	READY
12727	12727	Coupe	Imperator 108i Series II		2	EU-ISDERA-IMPERATOR-108I-SERIES-II-COUPE-01	HIGH	1991年改款后Series II外廓。	READY
147386	147386	Sedan	Fidia IR10	IR10	4	EU-ISORIVOLTA-FIDIA-IR10-SEDAN-01	HIGH	IR10四门轿车外廓。	READY
147385	147385	Coupe	Grifo IR8	IR8	2	EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	HIGH	IR8双门轿跑外廓。	READY
147384	147384	Coupe	Lele IR6	IR6	2	EU-ISORIVOLTA-LELE-IR6-COUPE-01	HIGH	IR6双门2+2轿跑外廓。	READY
14245	14245	Pickup	Campo KB	KBD27	2	EU-ISUZU-CAMPO-KB-PICKUP-2WD-01	MEDIUM	KBD27后驱两门单排座Pickup。	READY
14246_kbd42	14246	Pickup	Campo KB	KBD42	2	EU-ISUZU-CAMPO-KB-PICKUP-4WD-KBD42-01	MEDIUM	KBD42四驱短轴两门Pickup。	READY
14246_kbd47	14246	Pickup	Campo KB	KBD47	2	EU-ISUZU-CAMPO-KB-PICKUP-4WD-KBD47-01	MEDIUM	KBD47四驱长轴两门Pickup。	READY
34517_singlecab	34517	Pickup	D-Max I	TFS85	2	EU-ISUZU-D-MAX-I-CHASSISCAB-SINGLECAB-4WD-01	MEDIUM	四驱Single Cab底盘车。	READY
34517_spacecab	34517	Pickup	D-Max I	TFS85	4	EU-ISUZU-D-MAX-I-CHASSISCAB-SPACECAB-4WD-01	MEDIUM	四驱Space Cab底盘车。	READY
34517_crewcab	34517	Pickup	D-Max I	TFS85	4	EU-ISUZU-D-MAX-I-CHASSISCAB-CREWCAB-4WD-01	MEDIUM	四驱Crew Cab底盘车。	READY
34518_singlecab	34518	Pickup	D-Max I	TFR85	2	EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-2WD-01	MEDIUM	TFR85后驱两门Single Cab物理分支。	READY
34518_doublecab_lowride	34518	Pickup	D-Max I	TFR85	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-LOWRIDE-01	HIGH	后驱低车身窄体Double Cab。	READY
34518_doublecab_highride	34518	Pickup	D-Max I	TFR85	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-HIGHRIDE-01	HIGH	后驱高车身宽体Double Cab。	READY
126051	126051	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-FACELIFT-01	HIGH	后驱Single Cab车身。	READY
126055_singlecab	126055	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	HIGH	四驱Single Cab车身。	READY
126055_extendedcab	126055	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	HIGH	四驱Extended Cab车身。	READY
126055_doublecab	126055	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-FACELIFT-01	HIGH	四驱Double Cab车身。	READY
55099	55099	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-PREFL-01	HIGH	后驱Single Cab车身。	READY
113463_singlecab_lowride	113463	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-LOWRIDE-01	MEDIUM	后驱低车身Single Cab底盘车。	READY
113463_singlecab_highride	113463	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	MEDIUM	后驱高车身Single Cab底盘车。	READY
113463_crewcab	113463	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	MEDIUM	后驱Crew Cab底盘车。	READY
113464_singlecab	113464	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	MEDIUM	四驱Single Cab底盘车。	READY
113464_spacecab	113464	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-SPACECAB-HIGHRIDE-01	MEDIUM	四驱Space Cab底盘车。	READY
113464_crewcab	113464	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	MEDIUM	四驱Crew Cab底盘车。	READY
55091_singlecab	55091	Pickup	D-Max II		2	EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	HIGH	四驱Single Cab车身。	READY
55091_extendedcab	55091	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	HIGH	四驱Extended Cab车身。	READY
55091_doublecab	55091	Pickup	D-Max II		4	EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-PREFL-01	HIGH	四驱Double Cab车身。	READY
146714	146714	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	HIGH	改款前后驱Single Cab车身。	READY
146715_singlecab	146715	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	HIGH	改款前四驱Single Cab车身。	READY
146715_extendedcab	146715	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-PREFL-01	HIGH	改款前四驱Extended Cab车身。	READY
146715_doublecab	146715	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-PREFL-01	HIGH	改款前四驱Double Cab车身。	READY
157597_singlecab	157597	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-CHASSISCAB-SINGLECAB-PREFL-01	MEDIUM	23MY四驱Single Cab底盘车。	READY
157597_spacecab	157597	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-CHASSISCAB-SPACECAB-PREFL-01	MEDIUM	23MY四驱Space Cab底盘车。	READY
157597_crewcab	157597	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-CHASSISCAB-CREWCAB-PREFL-01	MEDIUM	23MY四驱Crew Cab底盘车。	READY
801987	801987	Pickup	D-Max III EV		4	EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	HIGH	全时四驱Double Cab量产车身。	READY
802844	802844	Pickup	D-Max III EV		4	EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	HIGH	全时四驱Double Cab量产车身。	READY
801355	801355	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	HIGH	改款后后驱Single Cab车身。	READY
802421_singlecab	802421	Pickup	D-Max III		2	EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	HIGH	改款后四驱Single Cab车身。	READY
802421_extendedcab	802421	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-FACELIFT-01	HIGH	改款后四驱Extended Cab车身。	READY
802421_doublecab	802421	Pickup	D-Max III		4	EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-FACELIFT-01	HIGH	改款后四驱Double Cab车身。	READY
115533_nhr69	115533	Pickup	Elf V	NHR69	2	EU-ISUZU-ELF-V-CHASSISCAB-NHR69-01	MEDIUM	后驱窄体NHR69单排驾驶室底盘车。	READY
115533_nkr69	115533	Pickup	Elf V	NKR69	2	EU-ISUZU-ELF-V-CHASSISCAB-NKR69-01	MEDIUM	后驱窄体NKR69单排驾驶室底盘车。	READY
18647	18647	Hatchback	Gemini III	JT151F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
125793_prefl	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	HIGH	1985至1987年改款前普通三门车身。	READY
125793_facelift	125793	Hatchback	Gemini II	JT150	3	EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	HIGH	1987年改款后普通三门车身。	READY
18648	18648	Hatchback	Gemini III	JT151F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
18649	18649	Hatchback	Gemini III	JT191S	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	HIGH	JT191S四驱三门Hatchback外廓。	READY
18650	18650	Hatchback	Gemini III	JT191F	3	EU-ISUZU-GEMINI-III-HATCHBACK-01	MEDIUM	第三代三门Hatchback外廓。	READY
18656	18656	Sedan	Gemini III	JT191F	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT191F四门Sedan外廓。	READY
18653	18653	Sedan	Gemini III	JT151F	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT151F四门Sedan外廓。	READY
125799	125799	Hatchback	Gemini II	JT190	3	EU-ISUZU-GEMINI-II-GTI-HATCHBACK-01	HIGH	JT190 GTI 16V三门低车身外廓。	READY
18654	18654	Sedan	Gemini III	JT151F	4	EU-ISUZU-GEMINI-III-SEDAN-01	MEDIUM	第三代四门Sedan外廓。	READY
18655	18655	Sedan	Gemini III	JT191S	4	EU-ISUZU-GEMINI-III-SEDAN-01	HIGH	JT191S四驱涡轮四门Sedan外廓。	READY
18651	18651	Sedan	Gemini III	JT641F	4	EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	MEDIUM	1.7 TD对应JT641F四门车身；输入Hatchback标注纠正。	READY
18652	18652	Sedan	Gemini III	JT641F	4	EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	HIGH	JT641F柴油四门Sedan外廓。	READY
18657	18657	Coupe	Impulse II	JT22	3	EU-ISUZU-IMPULSE-JT22-COUPE-01	HIGH	JT22三门轿跑车身。	READY
18658	18658	Coupe	Impulse II	JT22	3	EU-ISUZU-IMPULSE-JT22-COUPE-01	HIGH	JT22三门轿跑车身。	READY
7836	7836	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000后驱长轴厢式车身。	READY
10786	10786	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-VAN-SWB-01	MEDIUM	94000四驱短轴厢式车身。	READY
8819	8819	Van	Midi I	98000	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000后驱长轴厢式车身。	READY
10788	10788	Van	Midi I	94000	4	EU-ISUZU-MIDI-I-VAN-SWB-01	MEDIUM	94000四驱短轴厢式车身。	READY
10787	10787	Van	Midi I	98000N	4	EU-ISUZU-MIDI-I-VAN-LWB-01	MEDIUM	98000N后驱长轴厢式车身。	READY
125804	125804	Coupe	Piazza I	JR130	3	EU-ISUZU-PIAZZA-JR130-COUPE-01	HIGH	JR130三门轿跑车身。	READY
17437_3dr_swb	17437	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SUV-3D-SWB-01	MEDIUM	三门短轴封闭式车身。	READY
17437_3dr_lwb	17437	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SUV-3D-LWB-01	MEDIUM	三门长轴封闭式车身。	READY
17437_5dr_lwb	17437	SUV	Trooper I	UBS52	5	EU-ISUZU-TROOPER-I-SUV-5D-LWB-01	MEDIUM	五门长轴封闭式车身。	READY
17457	17457	SUV	Trooper I	UBS52	3	EU-ISUZU-TROOPER-I-SOFTTOP-SWB-01	HIGH	三门短轴软顶车身。	READY
17446	17446	SUV	Trooper II	UB	5	EU-ISUZU-TROOPER-II-SUV-LWB-01	HIGH	五门长轴封闭式车身。	READY
17447	17447	SUV	Trooper II	UB	3	EU-ISUZU-TROOPER-II-SUV-SWB-01	HIGH	TecDoc开放式越野车节点对应三门短轴固定车顶车身。	READY
17455	17455	SUV	Trooper III		3	EU-ISUZU-TROOPER-III-SUV-SWB-01	HIGH	三门短轴固定车顶车身。	READY
121922	121922	SUV	Trooper III		5	EU-ISUZU-TROOPER-III-SUV-LWB-01	HIGH	五门长轴封闭式车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_7101-7200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-INFINITI-EX-QX50-J50-SUV-04	4638	1803	1598	AutoHome 2013 Infiniti EX25 specifications;2008 Infiniti EX35 official press information	https://www.autohome.com.cn/news/201207/363316.html;https://usa.infinitinews.com/en-US/releases/release-4a3f9f0bb1264896872dc2e3c322a08a-2008-infiniti-ex35-press-kit
EU-INFINITI-EX-QX50-J50-SUV-03	4630	1800	1570	2008 Infiniti EX35 factory service manual	https://www.slideshare.net/slideshow/2008-infiniti-ex35-service-repair-manual/82619083
EU-INFINITI-EX-QX50-J50-SUV-01	4635	1800	1575	Automobile-Catalog Infiniti EX37 Europe;encyCARpedia Infiniti QX50 3.7 J50	https://www.automobile-catalog.com/car/2012/2169620/infiniti_ex37.html;https://www.encycarpedia.com/infiniti/13-qx50-3-7-suv
EU-INFINITI-FX-S50-SUV-01	4803	1925	1651	Automobile-Catalog Infiniti FX35 4x4;Edmunds Infiniti FX35	https://www.automobile-catalog.com/car/2003/2168270/infiniti_fx35_4x4.html;https://www.edmunds.com/infiniti/fx35/2003/st-100213725/features-specs/
EU-INFINITI-FX-QX70-S51-SUV-01	4865	1925	1680	Automobile-Catalog Infiniti FX50 S AWD Europe;CarsGuide Infiniti QX70	https://www.automobile-catalog.com/car/2013/2170175/infiniti_fx50_s_awd.html;https://www.carsguide.com.au/infiniti/qx70/car-dimensions/2014
EU-INFINITI-G35-V35-SEDAN-01	4737	1753	1466	Automobile-Catalog Infiniti G35 V35	https://www.automobile-catalog.com/car/2003/2166815/infiniti_g35.html
EU-INFINITI-G-Q60-CV36-COUPE-01	4655	1820	1387	Automobile-Catalog Infiniti G37 Coupe Europe;Automobile-Catalog Infiniti Q60 Coupe Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2167715/infiniti_g37_s_coupe_6-speed.html;https://www.automobile-catalog.com/car/2014/2168675/infiniti_q60_coupe_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-G-Q60-HV36-CONVERTIBLE-01	4660	1852	1391	Automobile-Catalog Infiniti G37 Cabrio Europe;Automobile-Catalog Infiniti Q60 Cabrio Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2167760/infiniti_g37_gt_cabrio_automatic.html;https://www.automobile-catalog.com/car/2014/2168660/infiniti_q60_cabrio_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-G20-P10-SEDAN-01	4445	1694	1394	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1991/2165630/infiniti_g20_5-speed.html;https://www.edmunds.com/infiniti/g20/1991/features-specs/
EU-INFINITI-I30-A32-SEDAN-01	4816	1770	1415	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1997/2166395/infiniti_i30.html;https://www.edmunds.com/infiniti/i30/1997/features-specs/
EU-INFINITI-J30-Y32-SEDAN-01	4860	1770	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2132225/infiniti_j30.html
EU-INFINITI-M-Q70-Y51-SEDAN-PREFL-01	4945	1845	1500	Automobile-Catalog Infiniti M37 Europe;Automobile-Catalog Infiniti Q70 3.0d Europe;Infiniti Maintenance Advantage application guide	https://www.automobile-catalog.com/car/2011/2169065/infiniti_m37.html;https://www.automobile-catalog.com/car/2014/2169140/infiniti_q70_3_0d_gt.html;https://partsadvantage.infinitiusa.com/wp-content/uploads/2017/10/Infiniti-Maintenance-Advantage%E2%84%A2-RADIATOR-CONDENSER_Application-Guide_10-24-2017.pdf
EU-INFINITI-M30-F31-COUPE-01	4795	1690	1380	Automobile-Catalog;Edmunds	https://www.automobile-catalog.com/car/1990/2132135/infiniti_m30_luxury_sports_coupe.html;https://www.edmunds.com/infiniti/m30/1990/coupe/features-specs/
EU-INFINITI-M30-F31-CONVERTIBLE-01	4798	1689	1410	Edmunds 1991 Infiniti M30 Convertible specifications	https://www.edmunds.com/infiniti/m30/1991/convertible/features-specs/
EU-INFINITI-Q30-H15-HATCHBACK-STANDARD-01	4425	1805	1495	INFINITI Q30 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q30-Catalogue-EN.pdf
EU-INFINITI-Q30-H15-HATCHBACK-SPORT-01	4425	1805	1475	INFINITI Q30 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q30-Catalogue-EN.pdf
EU-INFINITI-Q45-FY33-SEDAN-PREFL-01	5060	1821	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2166005/infiniti_q45.html
EU-INFINITI-Q45-G50-SEDAN-01	5090	1825	1435	Nissan Heritage Collection;Automobile-Catalog	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/229_infiniti_q45.html;https://www.automobile-catalog.com/car/1990/2165765/infiniti_q45.html
EU-INFINITI-Q45-FY33-SEDAN-FACELIFT-01	5070	1821	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/2166065/infiniti_q45.html
EU-INFINITI-Q50-V37-SEDAN-STANDARD-01	4790	1820	1445	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q50-V37-SEDAN-SPORT-01	4800	1820	1445	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q50-V37-SEDAN-REDSPORT-01	4800	1820	1430	INFINITI Q50 official catalogue	https://www-europe.infiniti-cdn.net/content/dam/Infiniti/me/brochures/Infiniti-Q50-Catalogue-EN.pdf
EU-INFINITI-Q60-CV37-COUPE-01	4690	1850	1390	INFINITI Q60 UK official brochure;2017 INFINITI Q60 official press kit	https://www.infiniti-cdn.net/content/dam/Infiniti/Brochures/UK/final/Q60_UK.pdf;https://usa.infinitinews.com/en-US/releases/us-2017-infiniti-q60-press-kit
EU-INFINITI-M-Q70-Y51-SEDAN-FACELIFT-01	4980	1845	1493	Automobile-Catalog Infiniti Q70 2.2d Europe	https://www.automobile-catalog.com/car/2015/2169215/infiniti_q70_2_2d.html
EU-INFINITI-QX4-JR50-SUV-01	4671	1839	1730	Automobile-Catalog 1997 Infiniti QX4 specifications	https://www.automobile-catalog.com/car/1997/2166410/infiniti_qx4.html
EU-INFINITI-EX-QX50-J50-SUV-02	4645	1800	1575	encyCARpedia Infiniti QX50 3.0d J50;AutoScout24 Infiniti QX50 Diesel	https://www.encycarpedia.com/infiniti/13-qx50-3-0d-suv;https://www.autoscout24.be/nl/auto/technische-gegevens/infiniti/qx50/
EU-INNOCENTI-MINI-90-120-HATCHBACK-01	3120	1500	1380	Automobile-Catalog Innocenti Mini 90	https://www.automobile-catalog.com/car/1979/39995/innocenti_mini_90.html
EU-INNOCENTI-MINI-DE-TOMASO-HATCHBACK-01	3130	1524	1380	Automobile-Catalog Innocenti Mini De Tomaso	https://www.automobile-catalog.com/car/1976/44660/innocenti_mini_de_tomaso.html
EU-IRMSCHER-TIGRA-A-COUPE-01	3922	1604	1340	Automobile-Catalog Irmscher Opel Tigra	https://www.automobile-catalog.com/car/1997/1272110/irmscher_opel_tigra.html
EU-IRMSCHER-GT-COUPE-01	4590	1780	1340	Automobile-Catalog Irmscher GT	https://www.automobile-catalog.com/car/1988/1271765/irmscher_gt.html
EU-IRMSCHER-OMEGA-A-WAGON-PREFL-01	4730	1772	1450	Automobile-Catalog Irmscher Opel Omega Caravan phase I	https://www.automobile-catalog.com/car/1989/1271885/irmscher_opel_omega_caravan_3_6i.html
EU-IRMSCHER-OMEGA-A-WAGON-FACELIFT-01	4768	1760	1530	Automobile-Catalog Irmscher Omega A Caravan phase II	https://www.automobile-catalog.com/car/1992/2470670/irmscher_c30e.html
EU-IRMSCHER-SENATOR-B-SEDAN-01	4845	1763	1430	Automobile-Catalog Irmscher Opel Senator 4.0i	https://www.automobile-catalog.com/car/1990/1271945/irmscher_opel_senator_4_0i.html
EU-ISDERA-COMMENDATORE-112I-COUPE-01	4665	1885	1040	Automobile-Catalog Isdera Commendatore 112i;UltimateSpecs Isdera Commendatore 112i	https://www.automobile-catalog.com/car/2000/1271690/isdera_commendatore_112i_6l.html;https://www.ultimatespecs.com/car-specs/Isdera/3644/Isdera-Commendatore-112i.html
EU-ISDERA-IMPERATOR-108I-SERIES-II-COUPE-01	4220	1835	1135	Automobile-Catalog 1991 Isdera Imperator 108i;Auto Bild Klassik Isdera Imperator 108i	https://www.automobile-catalog.com/car/1991/1271615/isdera_imperator_108i_5l-32v.html;https://www.autobild.de/klassik/artikel/isdera-imperator-108i-3674835.html
EU-ISORIVOLTA-FIDIA-IR10-SEDAN-01	4970	1780	1320	Automobile-Catalog 1973 Iso Rivolta Fidia IR10	https://www.automobile-catalog.com/car/1973/1251440/iso_rivolta_fidia_ir_10.html
EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	4600	1770	1200	Automobile-Catalog 1972 Iso Grifo IR8	https://www.automobile-catalog.com/car/1972/1251500/iso_grifo_ir_8.html
EU-ISORIVOLTA-LELE-IR6-COUPE-01	4650	1750	1350	Automobile-Catalog 1972 Iso Rivolta Lele	https://www.automobile-catalog.com/car/1972/1251230/iso_rivolta_lele_350_automatic.html
EU-ISUZU-CAMPO-KB-PICKUP-2WD-01	4700	1655	1600	Auto-Data Isuzu Campo 2.2 D;Tunel Isuzu Campo 2.2 D specifications	https://www.auto-data.net/en/isuzu-campo-2.2-d-53hp-15953;https://tunel.az/en/catalog/isuzu/campo/isuzu-campo/2cf8175b-0287-4a3f-9a96-59fcd7e85c72
EU-ISUZU-CAMPO-KB-PICKUP-4WD-KBD42-01	4580	1600	1600	1986 Isuzu official brief line-up brochure;BE FORWARD archived 1985 Isuzu Faster KBD42 registration dimensions	https://www.xr793.com/wp-content/uploads/2020/01/1986-Isuzu-Brief-Line-Up.pdf;https://www.beforward.jp/isuzu/faster/bf191231/id/186566/
EU-ISUZU-CAMPO-KB-PICKUP-4WD-KBD47-01	4670	1640	1630	1986 Isuzu official brief line-up brochure;BE FORWARD archived 1985 Isuzu Faster KBD47 registration dimensions	https://www.xr793.com/wp-content/uploads/2020/01/1986-Isuzu-Brief-Line-Up.pdf;https://www.beforward.jp/isuzu/faster/bf241274/id/237517/
EU-ISUZU-D-MAX-I-CHASSISCAB-SINGLECAB-4WD-01	5025	1800	1730	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
EU-ISUZU-D-MAX-I-CHASSISCAB-SPACECAB-4WD-01	4905	1800	1735	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
EU-ISUZU-D-MAX-I-CHASSISCAB-CREWCAB-4WD-01	4925	1800	1750	Isuzu UTE Australia D-Max official technical specifications, May 2010	https://www.scribd.com/document/160394470/Isuzu-d-max-australian-specs
EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-2WD-01	5155	1720	1635	Isuzu Rodeo 2011 official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/74-9340414004fe1bc33e6006doc.doc
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-LOWRIDE-01	4925	1720	1660	CarsGuide 2010 Isuzu D-Max dimensions;Autotrader Australia 2010 Isuzu D-Max dimensions	https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010;https://www.autotrader.com.au/isuzu/d-max/dimensions/2010
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-2WD-HIGHRIDE-01	5030	1800	1735	CarsGuide 2010 Isuzu D-Max dimensions;Carsales 2010 Isuzu D-Max LS High Ride specifications	https://www.carsguide.com.au/isuzu/d-max/car-dimensions/2010;https://www.carsales.com.au/research/isuzu/d-max/2010/ls-high-ride/
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-FACELIFT-01	5315	1775	1685	Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-4WD-01	5315	1860	1780	Isuzu D-Max official technical specifications;Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf;https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-EXTENDEDCAB-4WD-01	5295	1860	1780	Isuzu D-Max official technical specifications;Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf;https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-FACELIFT-01	5295	1860	1785	Isuzu D-Max 2018 official UK range brochure	https://www.isuzumedia.co.uk/assets/documents/original/941-DMaxRangeBrochure18MY.pdf
EU-ISUZU-D-MAX-II-PICKUP-SINGLECAB-2WD-PREFL-01	5315	1860	1685	Isuzu D-Max 2.5 official technical specifications	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-LOWRIDE-01	5040	1775	1685	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-SINGLECAB-HIGHRIDE-01	5040	1860	1780	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-CREWCAB-HIGHRIDE-01	5020	1860	1785	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-CHASSISCAB-SPACECAB-HIGHRIDE-01	5020	1860	1780	Isuzu UTE Australia D-Max 15.5MY technical specifications	https://s3-ap-southeast-2.amazonaws.com/imotor-cms/files_cms/Isuzu_D-MAX_specification_sheet.pdf
EU-ISUZU-D-MAX-II-PICKUP-DOUBLECAB-4WD-PREFL-01	5295	1865	1780	Isuzu D-Max 2.5 official technical specifications	https://www.isuzumedia.co.uk/assets/documents/original/134-20430485135255540185c8fpdf.pdf
EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-PREFL-01	5305	1810	1770	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-PREFL-01	5265	1870	1790	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-PREFL-01	5265	1870	1790	Isuzu All-New D-Max official UK press pack	https://www.isuzumedia.co.uk/assets/documents/original/1908-AllNewIsuzuDMaxRangePressPack.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-SINGLECAB-PREFL-01	5330	1870	1790	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-SPACECAB-PREFL-01	5290	1870	1800	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
EU-ISUZU-D-MAX-III-CHASSISCAB-CREWCAB-PREFL-01	5290	1870	1800	Isuzu UTE Australia 23MY D-Max specifications	https://resource.digitaldealer.com.au/pdf/1967726791638d1f5210061480102832.pdf
EU-ISUZU-D-MAX-III-EV-PICKUP-DOUBLECAB-01	5280	1870	1810	Isuzu Motors D-Max EV official production announcement	https://www.isuzu.co.jp/world/newsroom/details/20250429_1.html
EU-ISUZU-D-MAX-III-PICKUP-SINGLECAB-FACELIFT-01	5320	1810	1770	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-D-MAX-III-PICKUP-EXTENDEDCAB-FACELIFT-01	5280	1870	1790	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-D-MAX-III-PICKUP-DOUBLECAB-FACELIFT-01	5280	1870	1790	Isuzu New D-Max official press information	https://www.isuzumedia.co.uk/assets/applications/original/3625-the-new-isuzu-d-max-press-information.pdf
EU-ISUZU-ELF-V-CHASSISCAB-NHR69-01	4690	1695	1950	Goo-net Isuzu Elf NHR KG-NHR69EA catalogue specifications	https://www.goo-net.com/catalog/ISUZU/ELF_NHR/602170/
EU-ISUZU-ELF-V-CHASSISCAB-NKR69-01	4685	1695	1965	Goo-net Isuzu Elf NKR KK-NKR69EA catalogue specifications	https://www.goo-net.com/catalog/ISUZU/ELF_NKR/602346/
EU-ISUZU-GEMINI-III-HATCHBACK-01	4185	1695	1325	Automobile-Catalog 1991 Isuzu Gemini Irmscher R Hatchback;Car From Japan Isuzu Gemini OZ specifications	https://www.automobile-catalog.com/car/1991/1262345/isuzu_gemini_irmscher_r_hatchback.html;https://carfromjapan.com/specifications/isuzu/gemini/5819751b2afaa2c4b2878639
EU-ISUZU-GEMINI-II-HATCHBACK-PREFL-01	3960	1600	1380	Automobile-Catalog 1986 Isuzu FF Gemini C/C Hatchback	https://www.automobile-catalog.com/car/1986/1258055/isuzu_ff_gemini_cc_3door_hatchback.html
EU-ISUZU-GEMINI-II-HATCHBACK-FACELIFT-01	3995	1615	1380	Automobile-Catalog 1987 Isuzu Gemini 1.5 LS Hatchback	https://www.automobile-catalog.com/car/1987/56345/isuzu_gemini_1_5_ls_hatchback_cat.html
EU-ISUZU-GEMINI-III-SEDAN-01	4195	1680	1390	Automobile-Catalog 1990 Isuzu Gemini C/C 1.5;TCV Isuzu Gemini JT641F 1.7 Diesel	https://www.automobile-catalog.com/car/1990/1261145/isuzu_gemini_cc_1_5.html;https://www.tc-v.com/specifications/isuzu/gemini/c%2Fc-l_mt_1.7diesel/20676/
EU-ISUZU-GEMINI-II-GTI-HATCHBACK-01	4010	1615	1365	Automobile-Catalog 1989 Isuzu Gemini GTI 16V Hatchback	https://www.automobile-catalog.com/car/1989/1259060/isuzu_gemini_gti_16v_hatchback.html
EU-ISUZU-GEMINI-III-DIESEL-SEDAN-01	4195	1680	1370	Auto-Data Isuzu Gemini JT 1.7 TD;SBI Motor Isuzu Gemini JT641F	https://www.auto-data.net/en/isuzu-gemini-jt-1.7-td-88hp-automatic-24443;https://sbimotor.com/cars/ISUZU/GEMINI/856784609
EU-ISUZU-IMPULSE-JT22-COUPE-01	4150	1695	1300	Auto-Data Isuzu Impulse Coupe 1.6i	https://www.auto-data.net/en/isuzu-impulse-coupe-1.6-i-130hp-15957
EU-ISUZU-MIDI-I-VAN-LWB-01	4690	1690	1950	Auta5P Isuzu Midi Van 2.2 D;Quality Tested Isuzu Midi application catalogue	https://auta5p.eu/lang/en/katalog/auto.php?idf=Isuzu-Midi-Van-2.2-D-17636;https://qualitytested.it/en/app/src-cod/?src=PA902JM
EU-ISUZU-MIDI-I-VAN-SWB-01	4350	1690	1950	Drive.Place Isuzu Midi I 2.0 Van;Quality Tested Isuzu Midi application catalogue	https://isuzu.drive.place/midi/i/group_furgon/777242;https://qualitytested.it/en/app/src-cod/?src=PA902JM
EU-ISUZU-PIAZZA-JR130-COUPE-01	4310	1655	1300	Automobile-Catalog 1981 Isuzu Piazza XE	https://www.automobile-catalog.com/car/1981/1256330/isuzu_piazza_xe.html
EU-ISUZU-TROOPER-I-SUV-3D-SWB-01	4122	1651	1844	Drive.Place Isuzu Trooper I three-door specifications	https://isuzu.drive.place/trooper/i/group_offroad_3d/396703
EU-ISUZU-TROOPER-I-SUV-3D-LWB-01	4450	1651	1801	1986 Isuzu official brief line-up brochure	https://www.xr793.com/wp-content/uploads/2020/01/1986-Isuzu-Brief-Line-Up.pdf
EU-ISUZU-TROOPER-I-SUV-5D-LWB-01	4470	1651	1821	Drive.Place Isuzu Trooper I five-door specifications	https://isuzu.drive.place/trooper/i/group_offroad_5d/396539
EU-ISUZU-TROOPER-I-SOFTTOP-SWB-01	4122	1651	1844	Auto-Data Isuzu Trooper Soft Top 2.2 TD;Drive.Place Isuzu Trooper I open-top specifications	https://www.auto-data.net/en/isuzu-trooper-soft-top-2.2-td-ubs52-72hp-15947;https://isuzu.drive.place/trooper/i/group_vezdehod/396610
EU-ISUZU-TROOPER-II-SUV-LWB-01	4660	1745	1850	Auto-Data Isuzu Trooper LS 3.2 V6	https://www.auto-data.net/en/isuzu-trooper-ls-3.2-i-v6-24v-190hp-15943
EU-ISUZU-TROOPER-II-SUV-SWB-01	4234	1745	1849	Drive.Place Isuzu Trooper II 3.2 three-door	https://isuzu.drive.place/trooper/ii/group_offroad_3d/396379
EU-ISUZU-TROOPER-III-SUV-SWB-01	4365	1835	1835	Auto-Data Isuzu Trooper 3.0 DTI three-door	https://www.auto-data.net/en/isuzu-trooper-3.0-dti-159hp-15938
EU-ISUZU-TROOPER-III-SUV-LWB-01	4795	1835	1840	Auto-Data Isuzu Trooper 3.0 DTI Wagon five-door	https://www.auto-data.net/en/isuzu-trooper-3.0-dti-wagon-159hp-15939
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_7101-7200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.beforward.jp/isuzu/faster/bf191231/id/186566/?utm_source=chatgpt.com "Used 1985 ISUZU FASTER/N-KBD42 for Sale BF191231"
[2]: https://www.autodoc24.fr/car-parts/wheel-hub-10678/isuzu/elf/elf-platform-chassis-nkr7-nks7-nhr6-nkr6-npr-6/115533-3-1-td?utm_source=chatgpt.com "Wheel hub ISUZU Elf Platform / Chassis (NKR7_, NKS7_, NHR6_ ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4296 行）
- 累计尺寸组：dimension_groups_final.tsv（1223 行）

