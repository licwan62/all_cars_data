# 任务：all 第 1601-1700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0017__d389c120


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1601-1700 行

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
all 第 1601-1700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	79	107	May 1975	Jul 1979	2024-03-01	1636
VW	Jetta i	1.1	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1979	Feb 1984	2024-03-01	1637
VW	Jetta i	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1979	Feb 1984	2024-03-01	1638
VW	Jetta i	1.5	Stufenheck	Frontantrieb	Benzin	51	70	Aug 1978	Feb 1984	2024-03-01	1639
VW	Jetta i	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Aug 1978	Feb 1984	2024-03-01	1640
VW	Jetta i	1.6 GLI	Stufenheck	Frontantrieb	Benzin	81	110	Aug 1978	Jul 1982	2024-03-01	1641
VW	Jetta i	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Aug 1980	Feb 1984	2024-03-01	1642
VW	Jetta i	1.6 TD	Stufenheck	Frontantrieb	Diesel	51	70	Mar 1982	Feb 1984	2024-03-01	1643
VW	Golf ii	1.3	Schrägheck	Frontantrieb	Benzin	40	55	Aug 1983	Jun 1987	2024-03-01	1644
VW	Golf ii	1.6	Schrägheck	Frontantrieb	Benzin	51	70	Oct 1986	Dec 1992	2024-03-01	1645
VW	Golf ii	1.6	Schrägheck	Frontantrieb	Benzin	53	72	Feb 1986	Oct 1991	2024-03-01	1646
VW	Golf ii	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1983	Jul 1992	2024-03-01	1647
VW	Golf ii	1.8 GTI G60 Syncro	Schrägheck	Allrad	Benzin	118	160	Aug 1988	Dec 1991	2024-03-01	1648
VW	Golf ii	1.8	Schrägheck	Frontantrieb	Benzin	62	84	Aug 1986	Jan 1990	2024-03-01	1649
VW	Golf ii	1.8 Syncro	Schrägheck	Allrad	Benzin	66	90	Feb 1986	Jul 1991	2024-03-01	1650
VW	Golf ii	1.8 I CAT	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1987	Oct 1991	2024-03-01	1651
VW	Golf ii	1.8 Syncro	Schrägheck	Allrad	Benzin	72	98	Aug 1988	Jul 1991	2024-03-01	1652
VW	Golf ii	1.8 GTI CAT	Schrägheck	Frontantrieb	Benzin	79	107	Jan 1987	Oct 1991	2024-03-01	1653
VW	Golf ii	1.8 GTI	Schrägheck	Frontantrieb	Benzin	82	112	Aug 1983	Oct 1991	2024-03-01	1654
VW	Golf ii	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	95	129	Feb 1986	Oct 1991	2024-03-01	1655
VW	Golf ii	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	102	139	Feb 1986	Jun 1990	2024-03-01	1656
VW	Golf ii	1.8 GTI G60	Schrägheck	Frontantrieb	Benzin	118	160	Apr 1990	Jul 1991	2024-03-01	1657
VW	Golf ii	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Aug 1983	Oct 1991	2024-03-01	1658
VW	Golf ii	1.6 TD	Schrägheck	Frontantrieb	Diesel	51	70	Aug 1983	Oct 1991	2024-03-01	1659
VW	Golf ii	1.6 TD	Schrägheck	Frontantrieb	Diesel	59	80	Apr 1989	Oct 1991	2024-03-01	1660
VW	Transporter t5	2.0 TDI	Bus	Frontantrieb	Diesel	100	136	May 2010	Aug 2015	2024-03-01	1661
VW	Golf ii	1.6 TD	Schrägheck	Frontantrieb	Diesel	44	60	Aug 1989	Oct 1991	2024-03-01	1662
VW	Jetta ii	1.3	Stufenheck	Frontantrieb	Benzin	40	55	Jan 1984	Jun 1987	2024-03-01	1663
VW	Jetta ii	1.6	Stufenheck	Frontantrieb	Benzin	51	70	Oct 1986	Oct 1991	2024-03-01	1664
VW	Jetta ii	1.6	Stufenheck	Frontantrieb	Benzin	53	72	Mar 1986	Oct 1991	2024-03-01	1665
VW	Jetta ii	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Jan 1984	Jul 1992	2024-03-01	1666
VW	Jetta ii	1.8	Stufenheck	Frontantrieb	Benzin	62	84	Aug 1986	Jan 1990	2024-03-01	1667
VW	Jetta ii	1.8 CAT	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1987	Oct 1991	2024-03-01	1668
VW	Jetta ii	1.8 CAT	Stufenheck	Frontantrieb	Benzin	79	107	Jan 1987	Oct 1991	2024-03-01	1669
VW	Jetta ii	1.8	Stufenheck	Frontantrieb	Benzin	82	112	Jan 1984	Oct 1991	2024-03-01	1670
VW	Jetta ii	1.8 16V	Stufenheck	Frontantrieb	Benzin	95	129	Aug 1986	Oct 1991	2024-03-01	1671
VW	Jetta ii	1.8 16V	Stufenheck	Frontantrieb	Benzin	102	140	Jun 1987	Dec 1989	2024-03-01	1672
VW	Jetta ii	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Jan 1984	Oct 1991	2024-03-01	1673
VW	Jetta ii	1.6 TD	Stufenheck	Frontantrieb	Diesel	51	70	Jan 1984	Oct 1991	2024-03-01	1674
VW	Jetta ii	1.6 TD	Stufenheck	Frontantrieb	Diesel	59	80	Apr 1989	Oct 1991	2024-03-01	1675
VW	Jetta ii	1.6 TD	Stufenheck	Frontantrieb	Diesel	44	60	Jan 1990	Oct 1991	2024-03-01	1676
VW	15,001,600	1.5	Stufenheck	Heckantrieb	Benzin	33	45	Apr 1961	Jul 1973	2024-03-01	1677
VW	15,001,600	1.5 S	Stufenheck	Heckantrieb	Benzin	40	54	Aug 1963	Jul 1965	2024-03-01	1678
VW	15,001,600	1.6 TL	Stufenheck	Heckantrieb	Benzin	40	54	Aug 1965	Jul 1973	2024-03-01	1679
VW	15,001,600	1.6 TL	Schrägheck	Heckantrieb	Benzin	40	54	Aug 1965	Jul 1973	2024-03-01	1680
VW	15,001,600	1.6	Stufenheck	Heckantrieb	Benzin	40	54	Aug 1965	Jul 1973	2024-03-01	1681
VW	15,001,600	1.5	Kombi	Heckantrieb	Benzin	33	45	Apr 1961	Jul 1973	2024-03-01	1682
VW	15,001,600	1.6 L	Kombi	Heckantrieb	Benzin	40	54	Aug 1965	Jul 1973	2024-03-01	1683
VW	412	1.7	Kombi	Heckantrieb	Benzin	59	80	Jan 1972	Dec 1973	2024-03-01	1684
VW	K 70	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1970	Jul 1971	2024-03-01	1685
VW	K 70	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1970	Oct 1974	2024-03-01	1686
VW	K 70	1.8	Stufenheck	Frontantrieb	Benzin	74	100	Aug 1973	Oct 1974	2024-03-01	1687
VW	Passat b1	1.3	Schrägheck	Frontantrieb	Benzin	40	55	May 1973	Jul 1980	2024-03-01	1688
VW	Passat b1	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Jul 1973	Dec 1975	2024-03-01	1689
VW	Passat b1	1.6	Schrägheck	Frontantrieb	Benzin	63	85	Aug 1975	Jul 1980	2024-03-01	1690
VW	Passat b1	1.5 D	Schrägheck	Frontantrieb	Diesel	37	50	Aug 1977	Jul 1980	2024-03-01	1691
VW	Passat b2	1.3	Schrägheck	Frontantrieb	Benzin	40	55	Aug 1980	Jul 1983	2024-03-01	1692
VW	Passat b2	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1980	Jul 1986	2024-03-01	1693
VW	Passat b2	1.6	Schrägheck	Frontantrieb	Benzin	51	70	Aug 1986	Mar 1988	2024-03-01	1694
VW	Passat b2	1.6	Schrägheck	Frontantrieb	Benzin	53	72	Feb 1986	Mar 1988	2024-03-01	1695
VW	Passat b2	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1979	Mar 1988	2024-03-01	1696
VW	Passat b2	1.6	Schrägheck	Frontantrieb	Benzin	63	85	Jan 1981	Feb 1983	2024-03-01	1697
VW	Passat b2	1.8	Schrägheck	Frontantrieb	Benzin	64	87	May 1986	Mar 1988	2024-03-01	1698
VW	Passat b2	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Jan 1983	Mar 1988	2024-03-01	1699
VW	Passat b2	1.8	Schrägheck	Frontantrieb	Benzin	82	112	Dec 1983	Mar 1988	2024-03-01	1700
VW	Passat b2	1.9	Schrägheck	Frontantrieb	Benzin	85	115	Jan 1981	Jul 1983	2024-03-01	1701
VW	Passat b2	2	Schrägheck	Frontantrieb	Benzin	85	115	Aug 1983	Mar 1988	2024-03-01	1702
VW	Transporter t5	2.0 TDI 4motion	Bus	Allrad	Diesel	100	136	May 2010	Aug 2015	2024-03-01	1703
VW	Passat b2	2.2	Schrägheck	Frontantrieb	Benzin	85	115	Aug 1985	Mar 1988	2024-03-01	1704
VW	Passat b2	2.2	Schrägheck	Frontantrieb	Benzin	100	136	Jan 1985	Mar 1988	2024-03-01	1705
VW	Passat b2	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Aug 1980	Mar 1988	2024-03-01	1706
VW	Passat b2	1.6 TD	Schrägheck	Frontantrieb	Diesel	51	70	Apr 1982	Mar 1988	2024-03-01	1707
VW	Passat b3/b4	1.6	Stufenheck	Frontantrieb	Benzin	53	72	Apr 1988	Jul 1989	2024-03-01	1708
VW	Passat b3/b4	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Apr 1988	Jul 1992	2024-03-01	1709
VW	Passat b3/b4	1.8	Stufenheck	Frontantrieb	Benzin	79	107	Apr 1988	Jul 1993	2024-03-01	1710
VW	Passat b3/b4	1.8	Stufenheck	Frontantrieb	Benzin	82	112	Apr 1988	Jul 1992	2024-03-01	1711
VW	Passat b3/b4	2	Stufenheck	Frontantrieb	Benzin	85	115	Feb 1990	Aug 1996	2024-03-01	1712
VW	Passat b3/b4	1.6 TD	Stufenheck	Frontantrieb	Diesel	59	80	Aug 1988	Sep 1993	2024-03-01	1713
VW	Passat b3/b4	1.9 D	Stufenheck	Frontantrieb	Diesel	50	68	May 1989	Oct 1993	2024-03-01	1714
VW	Passat b3/b4	1.9 TD	Stufenheck	Frontantrieb	Diesel	55	75	Mar 1991	Aug 1996	2024-03-01	1715
VW	Passat b3/b4	1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Oct 1993	Aug 1996	2024-03-01	1716
VW	Passat b3/b4	1.8	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1990	Aug 1996	2024-03-01	1717
VW	Passat b3/b4	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1988	Aug 1996	2024-03-01	1718
VW	Passat b3/b4	1.8 G60 Syncro	Stufenheck	Allrad	Benzin	118	160	Aug 1988	Aug 1996	2024-03-01	1719
VW	Passat b3/b4	2.0 16V	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1988	Sep 1993	2024-03-01	1720
VW	Passat b3/b4	2.8 VR6	Stufenheck	Frontantrieb	Benzin	128	174	Jun 1991	Aug 1996	2024-03-01	1721
VW	Santana	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1981	Jul 1983	2024-03-01	1722
VW	Santana	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1981	Dec 1984	2024-03-01	1723
VW	Santana	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Aug 1981	Dec 1982	2024-03-01	1724
VW	Santana	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1983	Dec 1984	2024-03-01	1725
VW	Santana	1.9	Stufenheck	Frontantrieb	Benzin	85	115	Aug 1981	Jul 1983	2024-03-01	1726
VW	Santana	2	Stufenheck	Frontantrieb	Benzin	85	115	Aug 1983	Dec 1984	2024-03-01	1727
VW	Santana	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Aug 1981	Dec 1984	2024-03-01	1728
VW	Santana	1.6 TD	Stufenheck	Frontantrieb	Diesel	51	70	Dec 1981	Dec 1984	2024-03-01	1729
VW	Karmann ghia	1200	Cabriolet	Heckantrieb	Benzin	25	34	Aug 1960	Dec 1964	2024-03-01	1730
VW	Karmann ghia	1500	Coupe	Heckantrieb	Benzin	32	44	Jan 1966	Dec 1969	2024-03-01	1731
VW	Karmann ghia	1600	Coupe	Heckantrieb	Benzin	37	50	Jan 1970	Dec 1973	2024-03-01	1732
Porsche	914	1.7	Targa	Heckantrieb	Benzin	59	80	Jan 1969	Dec 1973	2024-03-01	1733
Porsche	914	2	Targa	Heckantrieb	Benzin	74	100	Jan 1972	Dec 1975	2024-03-01	1734
VW	Scirocco	1.1	Coupe	Frontantrieb	Benzin	37	50	Apr 1974	Jul 1979	2024-03-01	1735


--- Round 1 / 首次发送 ---
## 1. 更新点

* 首次闭合 **10 个尺寸组**，覆盖 **31 个输入 Ktype、35 条 READY 映射**。
* Jetta I 官方档案确认 `Type 16` 车身及 `4190×1610×1410 mm` 外廓。Golf II 官方档案确认标准 `19E` 外廓为 `3985×1665×1415 mm`，118 kW G60 Syncro 对应 Rallye 宽体 `4035×1700×1405 mm`。([Volkswagen Newsroom][1])
* Type 3 官方档案明确区分早期/后期 Notchback、TL Fastback 和 Variant 外廓；K 70 官方档案明确区分 1971 年前后的两套尺寸。([Volkswagen Newsroom][2])
* `1677`、`1679`、`1682` 暂未输出：输入生产区间或 BodyStyle 与官方 Type 3 分支存在冲突，需先确定具体物理分支。
* Jetta II、Passat、Transporter T5 等尚未进入本轮映射表。

## 2. 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：31/100
* READY 映射行：35
* PENDING 输入 Ktype：69/100
* 已确认尺寸组：10
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1637	1637	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1638	1638	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1639	1639	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1640	1640	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1641	1641	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1642	1642	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1643	1643	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1644	1644	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1645	1645	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1646	1646	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1647	1647	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1648	1648	Hatchback	Golf II	19E	3	EU-VW-GOLF-II-HATCHBACK-RALLYE-01	HIGH	118 kW G60 Syncro maps to Rallye widebody.	READY
1649	1649	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1650	1650	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1651	1651	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1652	1652	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1653	1653	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1654	1654	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1655	1655	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1656	1656	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1657	1657	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Front-drive G60 retains standard Golf II exterior.	READY
1658	1658	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1659	1659	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1660	1660	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1678	1678	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	1500 S early notchback exterior.	READY
1680	1680	Hatchback	Type 3 1500/1600	31	2	EU-VW-TYPE-3-FASTBACK-01	HIGH	1600 TL fastback exterior.	READY
1681_pre69	1681	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	Pre-1969 notchback exterior.	READY
1681_post69	1681	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-POST69-01	HIGH	1969-on notchback exterior.	READY
1683_pre69	1683	Wagon	Type 3 1500/1600	31	2	EU-VW-TYPE-3-WAGON-PRE69-01	HIGH	Pre-1969 Variant exterior.	READY
1683_post69	1683	Wagon	Type 3 1500/1600	31	2	EU-VW-TYPE-3-WAGON-POST69-01	HIGH	1969-on Variant exterior.	READY
1685_pre71	1685	Sedan	K 70	48	4	EU-VW-K70-SEDAN-PRE71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1685_post71	1685	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1686_pre71	1686	Sedan	K 70	48	4	EU-VW-K70-SEDAN-PRE71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1686_post71	1686	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1687	1687	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	HIGH	Post-1971 K 70 exterior.	READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-JETTA-I-SEDAN-01	4190	1610	1410	Volkswagen Classic Vehicle data Jetta I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-VW-GOLF-II-HATCHBACK-STD-01	3985	1665	1415	Volkswagen Classic Vehicle data Golf II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-2-profile-19471
EU-VW-GOLF-II-HATCHBACK-RALLYE-01	4035	1700	1405	Volkswagen Classic Vehicle data Golf II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-2-profile-19471
EU-VW-TYPE-3-SEDAN-PRE69-01	4225	1605	1475	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-FASTBACK-01	4225	1640	1475	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-SEDAN-POST69-01	4340	1640	1470	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-WAGON-PRE69-01	4225	1605	1465	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-WAGON-POST69-01	4340	1640	1470	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-K70-SEDAN-PRE71-01	4420	1685	1450	Volkswagen Classic Vehicle data K 70 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-k-70-profile-19702
EU-VW-K70-SEDAN-POST71-01	4455	1665	1435	Volkswagen Classic Vehicle data K 70 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-k-70-profile-19702
```

## 5. 下一步优先处理

1. 闭合 Jetta II 的 1989/1990 外廓变化及 GT 降低车高分支。
2. 聚类 Passat B1、B2、B3/B4 和 Santana，优先解决跨改款 Ktype。
3. 拆分 Transporter T5 的 SWB/LWB 与车顶高度。
4. 处理 Type 3 的 `1677`、`1679`、`1682` 输入字段冲突，以及 Ford Taunus、VW 412、Karmann Ghia、Porsche 914、Scirocco I。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641 "Vehicle data Jetta I profile | Volkswagen Newsroom"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664 "Vehicle data Type 3 1500/1600 profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新增 **48 个 Ktype、55 条 READY 映射**。
* `1662` 直接复用既有 Golf II 标准尺寸组，不重复创建或输出尺寸组。
* 首次闭合 Passat B1 前后期、Passat B2 Hatchback、Passat B3/B4 Sedan、Santana、Karmann Ghia Type 14、Porsche 914 和 Scirocco I，共新增 **10 个尺寸组**。
* Passat B3 与 B4 官方档案确认外廓分别为 `4570×1705×1450 mm` 和 `4605×1720×1430 mm`；仅跨两个代际且发动机确实延续的 Ktype 才拆分。([Volkswagen Newsroom][1])
* Passat B1、B2 与 Santana 分别按官方 Type 32、Type 32B、Type 321 车身边界完成关联。([Volkswagen Newsroom][2])
* Porsche 914、Karmann Ghia 与 Scirocco I 使用官方历史车型档案首次建组。([Volkswagen Newsroom][3])

## 2. 当前批次进度

* READY 输入 Ktype：79/100
* READY 映射行：90
* PENDING 输入 Ktype：21/100
* 已确认尺寸组：20
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1662	1662	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	标准19E外廓。	READY
1688_pre75	1688	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	HIGH	1975年外廓更新前分支。	READY
1688_post75	1688	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓更新后分支。	READY
1689_pre75	1689	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	HIGH	1975年外廓更新前分支。	READY
1689_post75	1689	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	生产区间延续至1975年更新后。	READY
1690	1690	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓。	READY
1691	1691	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓。	READY
1692	1692	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1693	1693	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1694	1694	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1695	1695	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1696	1696	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1697	1697	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1698	1698	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1699	1699	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1700	1700	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1701	1701	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1702	1702	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1704	1704	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1705	1705	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1706	1706	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1707	1707	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1708	1708	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	该发动机仅对应B3分支。	READY
1709	1709	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	该发动机仅对应B3分支。	READY
1710	1710	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	79kW版本仅对应B3分支。	READY
1711	1711	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	82kW版本仅对应B3分支。	READY
1712_b3	1712	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段2.0 85kW分支。	READY
1712_b4	1712	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段2.0 85kW分支。	READY
1713	1713	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	1.6 TD仅对应B3分支。	READY
1714	1714	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	自然吸气1.9 D仅对应B3分支。	READY
1715_b3	1715	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.9 TD分支。	READY
1715_b4	1715	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.9 TD分支。	READY
1716	1716	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	1.9 TDI对应B4分支。	READY
1717_b3	1717	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.8 55kW分支。	READY
1717_b4	1717	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.8 55kW分支。	READY
1718_b3	1718	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.8 66kW分支。	READY
1718_b4	1718	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.8 66kW分支。	READY
1719	1719	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	G60 Syncro仅对应B3分支。	READY
1720	1720	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	100kW 2.0 16V仅对应B3分支。	READY
1721_b3	1721	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段2.8 VR6分支。	READY
1721_b4	1721	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段2.8 VR6分支。	READY
1722	1722	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1723	1723	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1724	1724	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1725	1725	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1726	1726	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1727	1727	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1728	1728	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1729	1729	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1730	1730	Convertible	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	HIGH	Type 14 Cabriolet外廓。	READY
1731	1731	Coupe	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14 Coupé外廓。	READY
1732	1732	Coupe	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14 Coupé外廓。	READY
1733	1733	Convertible	914	47	2	EU-PORSCHE-914-TARGA-01	HIGH	Type 47 Targa外廓。	READY
1734	1734	Convertible	914	47	2	EU-PORSCHE-914-TARGA-01	HIGH	Type 47 Targa外廓。	READY
1735	1735	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	非GTI标准Type 53外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	4190	1600	1360	Volkswagen Classic Vehicle data Passat B1 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-HATCHBACK-POST75-01	4290	1615	1360	Volkswagen Classic Vehicle data Passat B1 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B2-HATCHBACK-01	4335	1685	1385	Volkswagen Classic Vehicle data Passat B2 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B3-SEDAN-01	4570	1705	1450	Volkswagen Classic Vehicle data Passat B3 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Volkswagen Classic Vehicle data Passat B4 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
EU-VW-SANTANA-B2-SEDAN-01	4545	1695	1400	Volkswagen Classic Vehicle data Santana profile	https://www.volkswagen-newsroom.com/en/vehicle-data-santana-profile-19711
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	4140	1634	1330	Volkswagen Classic Vehicle data Karmann Ghia Type 14 Cabriolet profile	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-typ-14-cabriolet-profile-19634
EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	4140	1634	1330	Volkswagen Classic Vehicle data Karmann Ghia Type 14 Coupé profile	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-type-14-coupe-profile-19631
EU-PORSCHE-914-TARGA-01	3985	1650	1230	Volkswagen Classic Vehicle data VW Porsche 914 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-vw-porsche-914-profile-19673
EU-VW-SCIROCCO-I-COUPE-STD-01	3855	1625	1310	Volkswagen Classic Vehicle data Scirocco I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-scirocco-1-profile-19648
```

## 5. 下一步优先处理

1. 闭合 Jetta II 的官方 `1395–1415 mm` 高度范围，确认是否需要按悬架或版本拆组。
2. 拆分 Transporter T5 的 SWB/LWB 和车顶高度分支。
3. 解决 Type 3 的 `1677`、`1679`、`1682` BodyStyle 与生产区间冲突。
4. 确定 VW 412 `1684` 的普通版与 L/LE 长度边界。
5. 补齐 Ford Taunus `1636` 的具体 TC 代际与外廓。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/engine-versions-passat-b3-profile-19542 "Engine versions Passat B3 profile | Volkswagen Newsroom"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538 "Vehicle data Passat B2 profile | Volkswagen Newsroom"
[3]: https://www.volkswagen-newsroom.com/en/vehicle-data-vw-porsche-914-profile-19673?utm_source=chatgpt.com "Vehicle data VW Porsche 914 profile"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Ford Taunus `1636`，按二门与四门 Sedan 派生两条映射；两者复用相同外廓尺寸组。1975 年 Ford 原始目录给出的 Sedan 三维为 `4267×1700×1370 mm`。
* 闭合 Type 3 的 `1677`、`1679`、`1682`：`1.5` 发动机限定为早期 Notchback/Variant；`1.6 TL` 按官方定义纠正为 Hatchback/Fastback。全部复用既有尺寸组。([Volkswagen Newsroom][1])
* 闭合 VW 412 `1684`，因输入未区分普通 `E` 与加长 `LE` 外廓，拆为 `std`、`l` 两个分支，并首次创建两个尺寸组。官方资料给出普通版 `4555×1675×1475 mm`、L/LE 版 `4583×1675×1475 mm`。([Volkswagen Newsroom][2])
* 剩余 PENDING 集中为 Jetta II 14 个 Ktype，以及 Transporter T5 2 个 Ktype。

## 2. 当前批次进度

* READY 输入 Ktype：84/100
* READY 映射行：97
* PENDING 输入 Ktype：16/100
* 已确认尺寸组：23
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1636_2dr	1636	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-01	MEDIUM	二门Sedan物理分支；与四门版共用外廓三维。	READY
1636_4dr	1636	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-01	MEDIUM	四门Sedan物理分支；与二门版共用外廓三维。	READY
1677	1677	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	1.5发动机限定为早期Notchback分支；上游结束年月宽于官方1500生产期。	READY
1679	1679	Hatchback	Type 3 1500/1600	31	2	EU-VW-TYPE-3-FASTBACK-01	HIGH	1600 TL为官方Fastback分支，纠正输入Stufenheck分类。	READY
1682	1682	Wagon	Type 3 1500/1600	31	2	EU-VW-TYPE-3-WAGON-PRE69-01	HIGH	1.5发动机限定为早期Variant外廓。	READY
1684_std	1684	Wagon	412	412	2	EU-VW-412-WAGON-STD-01	HIGH	412 E 1700 Variant普通外廓分支。	READY
1684_l	1684	Wagon	412	412	2	EU-VW-412-WAGON-L-01	HIGH	412 LE 1700 Variant加长外廓分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TAUNUS-TC2-SEDAN-01	4267	1700	1370	Ford Taunus original brochure August 1975	https://www.motomobil.com/fileadmin/_2020/prospekte/Prospekte_Taunus_MK1_MK2_MK3/Ford_Taunus_MK1_Originalprospekt_1975.pdf
EU-VW-412-WAGON-STD-01	4555	1675	1475	Volkswagen Classic Vehicle data Volkswagen 412 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-412-WAGON-L-01	4583	1675	1475	Volkswagen Classic Vehicle data Volkswagen 412 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
```

## 5. 下一步优先处理

1. 将 Jetta II 按普通/GT 外廓及 1990 年前后保险杠改款聚类，闭合 14 个 Ktype。
2. 最后拆分 Transporter T5 Bus 的 SWB/LWB 与适用车顶分支，处理前驱和 4Motion 两个 Ktype。
3. PENDING 清零后立即输出两张最终完整 TSV 与指定 sandbox 下载链接。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664?utm_source=chatgpt.com "Vehicle data Type 3 1500/1600 profile"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661 "Vehicle data Volkswagen 412 profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合剩余 Jetta II Ktype：按官方 `4315×1665×1395–1415 mm` 高度边界拆为普通悬架与 GT/GTD/GTX 运动悬架尺寸组；`1668` 和 `1674` 同时覆盖普通版与运动版，因此派生两行。([Volkswagen Newsroom][1])
* 闭合 Transporter T5 Bus：前驱与 4MOTION 均按短轴、长轴标准顶拆分。2013 年乘用版目录确认短轴 `4892×1904×1990 mm`、长轴 `5292×1904×1990 mm`，其中 `1904 mm` 为不含后视镜车宽。
* 机械修正 Type 3 Variant 与 VW 412 Variant 的 `Doors` 为 `3`。
* 已完成唯一主键、固定表头、外键闭合、正整数三维、来源与 URL 非空检查。

## 2. 当前批次进度

* 输入 Ktype：100/100
* READY 输入 Ktype：100/100
* READY 映射行：117
* PENDING：0
* DIMENSION_GROUP：27
* 映射引用闭合：27/27
* 当前批次已完成。

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1636_2dr	1636	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-01	MEDIUM	二门Sedan物理分支；与四门版共用外廓三维。	READY
1636_4dr	1636	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-01	MEDIUM	四门Sedan物理分支；与二门版共用外廓三维。	READY
1637	1637	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1638	1638	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1639	1639	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1640	1640	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1641	1641	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1642	1642	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1643	1643	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	Type 16 notchback exterior.	READY
1644	1644	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1645	1645	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1646	1646	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1647	1647	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1648	1648	Hatchback	Golf II	19E	3	EU-VW-GOLF-II-HATCHBACK-RALLYE-01	HIGH	118 kW G60 Syncro maps to Rallye widebody.	READY
1649	1649	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1650	1650	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1651	1651	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1652	1652	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1653	1653	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1654	1654	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1655	1655	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1656	1656	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1657	1657	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Front-drive G60 retains standard Golf II exterior.	READY
1658	1658	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1659	1659	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1660	1660	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	Standard 19E exterior; common 3/5-door envelope.	READY
1661_swb	1661	MPV	Transporter T5 facelift			EU-VW-TRANSPORTER-T5-FACELIFT-MPV-SWB-01	MEDIUM	短轴标准顶Bus分支。	READY
1661_lwb	1661	MPV	Transporter T5 facelift			EU-VW-TRANSPORTER-T5-FACELIFT-MPV-LWB-01	MEDIUM	长轴标准顶Bus分支。	READY
1662	1662	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH	标准19E外廓。	READY
1663	1663	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通悬架Sedan外廓。	READY
1664	1664	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通悬架Sedan外廓。	READY
1665	1665	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通悬架Sedan外廓。	READY
1666	1666	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通悬架Sedan外廓。	READY
1667	1667	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通悬架Sedan外廓。	READY
1668_std	1668	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	1.8 66 kW普通版外廓。	READY
1668_gt	1668	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	同功率Jetta GT低车身分支。	READY
1669	1669	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	GT/GTX运动版低车身外廓。	READY
1670	1670	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	GT/GTX运动版低车身外廓。	READY
1671	1671	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	GT/GTX运动版低车身外廓。	READY
1672	1672	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	GT/GTX运动版低车身外廓。	READY
1673	1673	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	普通柴油Sedan外廓。	READY
1674_std	1674	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	1.6 TD普通版外廓。	READY
1674_gtd	1674	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	同功率GTD低车身分支。	READY
1675	1675	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-SPORT-01	MEDIUM	高功率GTD低车身外廓。	READY
1676	1676	Sedan	Jetta II			EU-VW-JETTA-II-SEDAN-STD-01	MEDIUM	低功率1.6 TD普通外廓。	READY
1677	1677	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	1.5发动机限定为早期Notchback分支；上游结束年月宽于官方1500生产期。	READY
1678	1678	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	1500 S early notchback exterior.	READY
1679	1679	Hatchback	Type 3 1500/1600	31	2	EU-VW-TYPE-3-FASTBACK-01	HIGH	1600 TL为官方Fastback分支，纠正输入Stufenheck分类。	READY
1680	1680	Hatchback	Type 3 1500/1600	31	2	EU-VW-TYPE-3-FASTBACK-01	HIGH	1600 TL fastback exterior.	READY
1681_pre69	1681	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-PRE69-01	HIGH	Pre-1969 notchback exterior.	READY
1681_post69	1681	Sedan	Type 3 1500/1600	31	2	EU-VW-TYPE-3-SEDAN-POST69-01	HIGH	1969-on notchback exterior.	READY
1682	1682	Wagon	Type 3 1500/1600	31	3	EU-VW-TYPE-3-WAGON-PRE69-01	HIGH	1.5发动机限定为早期Variant外廓。	READY
1683_pre69	1683	Wagon	Type 3 1500/1600	31	3	EU-VW-TYPE-3-WAGON-PRE69-01	HIGH	Pre-1969 Variant exterior.	READY
1683_post69	1683	Wagon	Type 3 1500/1600	31	3	EU-VW-TYPE-3-WAGON-POST69-01	HIGH	1969-on Variant exterior.	READY
1684_std	1684	Wagon	412	412	3	EU-VW-412-WAGON-STD-01	HIGH	412 E 1700 Variant普通外廓分支。	READY
1684_l	1684	Wagon	412	412	3	EU-VW-412-WAGON-L-01	HIGH	412 LE 1700 Variant加长外廓分支。	READY
1685_pre71	1685	Sedan	K 70	48	4	EU-VW-K70-SEDAN-PRE71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1685_post71	1685	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1686_pre71	1686	Sedan	K 70	48	4	EU-VW-K70-SEDAN-PRE71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1686_post71	1686	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	MEDIUM	Ktype production span crosses the 1971 exterior revision.	READY
1687	1687	Sedan	K 70	48	4	EU-VW-K70-SEDAN-POST71-01	HIGH	Post-1971 K 70 exterior.	READY
1688_pre75	1688	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	HIGH	1975年外廓更新前分支。	READY
1688_post75	1688	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓更新后分支。	READY
1689_pre75	1689	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	HIGH	1975年外廓更新前分支。	READY
1689_post75	1689	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	生产区间延续至1975年更新后。	READY
1690	1690	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓。	READY
1691	1691	Hatchback	Passat B1	32		EU-VW-PASSAT-B1-HATCHBACK-POST75-01	HIGH	1975年起外廓。	READY
1692	1692	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1693	1693	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1694	1694	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1695	1695	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1696	1696	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1697	1697	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1698	1698	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1699	1699	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1700	1700	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1701	1701	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1702	1702	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1703_swb	1703	MPV	Transporter T5 facelift			EU-VW-TRANSPORTER-T5-FACELIFT-MPV-SWB-01	MEDIUM	4MOTION短轴标准顶Bus分支。	READY
1703_lwb	1703	MPV	Transporter T5 facelift			EU-VW-TRANSPORTER-T5-FACELIFT-MPV-LWB-01	MEDIUM	4MOTION长轴标准顶Bus分支。	READY
1704	1704	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1705	1705	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1706	1706	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1707	1707	Hatchback	Passat B2	32B		EU-VW-PASSAT-B2-HATCHBACK-01	HIGH	Type 32B Hatchback外廓。	READY
1708	1708	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	该发动机仅对应B3分支。	READY
1709	1709	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	该发动机仅对应B3分支。	READY
1710	1710	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	79kW版本仅对应B3分支。	READY
1711	1711	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	82kW版本仅对应B3分支。	READY
1712_b3	1712	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段2.0 85kW分支。	READY
1712_b4	1712	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段2.0 85kW分支。	READY
1713	1713	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	1.6 TD仅对应B3分支。	READY
1714	1714	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	自然吸气1.9 D仅对应B3分支。	READY
1715_b3	1715	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.9 TD分支。	READY
1715_b4	1715	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.9 TD分支。	READY
1716	1716	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	1.9 TDI对应B4分支。	READY
1717_b3	1717	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.8 55kW分支。	READY
1717_b4	1717	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.8 55kW分支。	READY
1718_b3	1718	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段1.8 66kW分支。	READY
1718_b4	1718	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段1.8 66kW分支。	READY
1719	1719	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	G60 Syncro仅对应B3分支。	READY
1720	1720	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	100kW 2.0 16V仅对应B3分支。	READY
1721_b3	1721	Sedan	Passat B3	35i	4	EU-VW-PASSAT-B3-SEDAN-01	HIGH	B3阶段2.8 VR6分支。	READY
1721_b4	1721	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH	B4阶段2.8 VR6分支。	READY
1722	1722	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1723	1723	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1724	1724	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1725	1725	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1726	1726	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1727	1727	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1728	1728	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1729	1729	Sedan	Santana B2	321	4	EU-VW-SANTANA-B2-SEDAN-01	HIGH	Type 321外廓。	READY
1730	1730	Convertible	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	HIGH	Type 14 Cabriolet外廓。	READY
1731	1731	Coupe	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14 Coupé外廓。	READY
1732	1732	Coupe	Karmann Ghia Type 14	14	2	EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	HIGH	Type 14 Coupé外廓。	READY
1733	1733	Convertible	914	47	2	EU-PORSCHE-914-TARGA-01	HIGH	Type 47 Targa外廓。	READY
1734	1734	Convertible	914	47	2	EU-PORSCHE-914-TARGA-01	HIGH	Type 47 Targa外廓。	READY
1735	1735	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	非GTI标准Type 53外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1601-1700_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TAUNUS-TC2-SEDAN-01	4267	1700	1370	Ford Taunus original brochure August 1975	https://www.motomobil.com/fileadmin/_2020/prospekte/Prospekte_Taunus_MK1_MK2_MK3/Ford_Taunus_MK1_Originalprospekt_1975.pdf
EU-VW-JETTA-I-SEDAN-01	4190	1610	1410	Volkswagen Classic Vehicle data Jetta I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-VW-GOLF-II-HATCHBACK-STD-01	3985	1665	1415	Volkswagen Classic Vehicle data Golf II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-2-profile-19471
EU-VW-GOLF-II-HATCHBACK-RALLYE-01	4035	1700	1405	Volkswagen Classic Vehicle data Golf II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-2-profile-19471
EU-VW-TRANSPORTER-T5-FACELIFT-MPV-SWB-01	4892	1904	1990	Volkswagen Commercial Vehicles Transporter Passenger Carriers brochure January 2013	https://xr793.com/wp-content/uploads/2022/12/2013-VW-T5-Transporter-Passenger-Carriers-UK.pdf
EU-VW-TRANSPORTER-T5-FACELIFT-MPV-LWB-01	5292	1904	1990	Volkswagen Commercial Vehicles Transporter Passenger Carriers brochure January 2013	https://xr793.com/wp-content/uploads/2022/12/2013-VW-T5-Transporter-Passenger-Carriers-UK.pdf
EU-VW-JETTA-II-SEDAN-STD-01	4315	1665	1415	Volkswagen Classic Vehicle data Jetta II profile; Volkswagen Classic Jetta II history and engine versions	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-2-profile-19644;https://www.volkswagen-newsroom.com/en/engine-versions-jetta-2-profile-19645
EU-VW-JETTA-II-SEDAN-SPORT-01	4315	1665	1395	Volkswagen Classic Vehicle data Jetta II profile; Volkswagen Classic Jetta II history and engine versions	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-2-profile-19644;https://www.volkswagen-newsroom.com/en/engine-versions-jetta-2-profile-19645
EU-VW-TYPE-3-SEDAN-PRE69-01	4225	1605	1475	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-FASTBACK-01	4225	1640	1475	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-SEDAN-POST69-01	4340	1640	1470	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-WAGON-PRE69-01	4225	1605	1465	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE-3-WAGON-POST69-01	4340	1640	1470	Volkswagen Classic Vehicle data Type 3 1500/1600 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-412-WAGON-STD-01	4555	1675	1475	Volkswagen Classic Vehicle data Volkswagen 412 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-412-WAGON-L-01	4583	1675	1475	Volkswagen Classic Vehicle data Volkswagen 412 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-K70-SEDAN-PRE71-01	4420	1685	1450	Volkswagen Classic Vehicle data K 70 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-k-70-profile-19702
EU-VW-K70-SEDAN-POST71-01	4455	1665	1435	Volkswagen Classic Vehicle data K 70 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-k-70-profile-19702
EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	4190	1600	1360	Volkswagen Classic Vehicle data Passat B1 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-HATCHBACK-POST75-01	4290	1615	1360	Volkswagen Classic Vehicle data Passat B1 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B2-HATCHBACK-01	4335	1685	1385	Volkswagen Classic Vehicle data Passat B2 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B3-SEDAN-01	4570	1705	1450	Volkswagen Classic Vehicle data Passat B3 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Volkswagen Classic Vehicle data Passat B4 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
EU-VW-SANTANA-B2-SEDAN-01	4545	1695	1400	Volkswagen Classic Vehicle data Santana profile	https://www.volkswagen-newsroom.com/en/vehicle-data-santana-profile-19711
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	4140	1634	1330	Volkswagen Classic Vehicle data Karmann Ghia Type 14 Cabriolet profile	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-typ-14-cabriolet-profile-19634
EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	4140	1634	1330	Volkswagen Classic Vehicle data Karmann Ghia Type 14 Coupé profile	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-type-14-coupe-profile-19631
EU-PORSCHE-914-TARGA-01	3985	1650	1230	Volkswagen Classic Vehicle data VW Porsche 914 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-vw-porsche-914-profile-19673
EU-VW-SCIROCCO-I-COUPE-STD-01	3855	1625	1310	Volkswagen Classic Vehicle data Scirocco I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-scirocco-1-profile-19648
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1601-1700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-2-profile-19644 "Vehicle data Jetta II profile | Volkswagen Newsroom"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1601-1700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1601-1700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2150 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（532 行）
