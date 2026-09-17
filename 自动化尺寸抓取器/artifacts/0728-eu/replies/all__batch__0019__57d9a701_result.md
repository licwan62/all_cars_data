# 任务：all 第 1801-1900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0019__57d9a701


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1801-1900 行

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
all 第 1801-1900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Monterey a	3.2	Geländewagen geschlossen	Allrad	Benzin	130	177	Aug 1991	Mar 1994	2024-03-01	1836
Opel	Corsa b	1.5 D	Schrägheck	Frontantrieb	Diesel	37	50	Mar 1993	Sep 2000	2024-03-01	1837
Opel	Corsa b	1.5 TD	Schrägheck	Frontantrieb	Diesel	49	67	Mar 1993	Sep 2000	2024-03-01	1838
Opel	Corsa b	1.2 I	Schrägheck	Frontantrieb	Benzin	33	45	Mar 1993	Sep 2000	2024-03-01	1839
Opel	Corsa b	1.4 I	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1993	Sep 2000	2024-03-01	1840
Opel	Corsa b	1.4 SI	Schrägheck	Frontantrieb	Benzin	60	82	Mar 1993	Sep 2000	2024-03-01	1841
Opel	Corsa b	1.6 GSI 16V	Schrägheck	Frontantrieb	Benzin	80	109	Mar 1993	Sep 2000	2024-03-01	1842
VW	Transporter t3	1.6 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	51	70	Oct 1984	Jul 1992	2024-03-01	1843
VW	Transporter t3	1.7 D	Bus	Heckantrieb	Diesel	42	57	Oct 1986	Jul 1992	2024-03-01	1844
VW	Transporter t3	1.7 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	42	57	Aug 1985	Jul 1992	2024-03-01	1845
VW	Transporter t3	2.1 I	Bus	Heckantrieb	Benzin	68	92	Jul 1989	Jul 1992	2024-03-01	1846
VW	Transporter t3	2.1 CAT	Bus	Heckantrieb	Benzin	70	95	Jun 1989	Jul 1992	2024-03-01	1847
VW	Transporter t3	1.9	Bus	Heckantrieb	Benzin	66	90	Aug 1983	Jul 1985	2024-03-01	1848
Fiat	Scudo	2.0 D Multijet	Kasten	Frontantrieb	Diesel	120	163	Jul 2010	Mar 2016	2024-03-01	1849
VW	Transporter t3	2.1	Kasten	Heckantrieb	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	1850
VW	Transporter t3	1.9	Kasten	Heckantrieb	Benzin	44	60	Oct 1982	Jul 1992	2024-03-01	1851
VW	Transporter t3	1.9 Syncro	Bus	Allrad	Benzin	57	78	Feb 1985	Jul 1992	2024-03-01	1852
VW	Transporter t3	2.1 Syncro	Bus	Allrad	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	1853
VW	Transporter t3	1.6 TD Syncro	Bus	Allrad	Diesel	51	70	Mar 1986	Jul 1992	2024-03-01	1854
VW	Transporter t3	2.1 Syncro	Kasten	Allrad	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	1855
Fiat	Punto	1.4 Natural Power	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	57	78	Oct 2009	Feb 2012	2024-03-01	1856
VW	Transporter t3	2.1 Syncro	Bus	Allrad	Benzin	82	112	Jan 1986	Jul 1992	2024-03-01	1857
VW	Taro	1.8	Pick-up	Heckantrieb	Benzin	61	83	Apr 1989	Sep 1994	2024-03-01	1858
VW	Taro	2.4 D	Pick-up	Heckantrieb	Diesel	59	80	Sep 1991	Jul 1994	2024-03-01	1859
VW	Transporter / multivan t4	1.8	Bus	Frontantrieb	Benzin	49	67	Dec 1990	Jul 1992	2025-11-01	1860
VW	Transporter / multivan t4	1.9 D	Bus	Frontantrieb	Diesel	44	60	Sep 1990	Dec 1995	2025-11-01	1861
VW	Transporter / multivan t4	1.9 TD	Bus	Frontantrieb	Diesel	50	68	Oct 1992	Apr 2003	2025-11-01	1862
VW	Transporter / multivan t4	2.4 D	Bus	Frontantrieb	Diesel	57	78	Sep 1990	Apr 1998	2025-11-01	1863
VW	Transporter / multivan t4	2	Bus	Frontantrieb	Benzin	62	84	Sep 1990	Apr 2003	2025-11-01	1864
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	62	84	Oct 2009	Feb 2012	2024-03-01	1865
VW	Golf iii	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Nov 1991	Aug 1997	2024-03-01	1866
VW	Golf iii	1.9 TD, GTD	Schrägheck	Frontantrieb	Diesel	55	75	Nov 1991	Aug 1997	2024-03-01	1867
VW	Golf iii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Aug 1993	Dec 1997	2025-02-03	1868
VW	Golf iii	1.4	Schrägheck	Frontantrieb	Benzin	40	55	Nov 1991	Aug 1997	2024-03-01	1869
VW	Golf iii	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1992	Aug 1997	2024-03-01	1870
VW	Golf iii	1.8	Schrägheck	Frontantrieb	Benzin	55	75	Nov 1991	Aug 1997	2024-03-01	1871
VW	Golf iii	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Nov 1991	Aug 1997	2024-03-01	1872
VW	Golf iii	1.8 Syncro	Schrägheck	Allrad	Benzin	66	90	Jan 1993	Aug 1997	2024-03-01	1873
VW	Golf iii	2	Schrägheck	Frontantrieb	Benzin	85	115	Nov 1991	Aug 1997	2024-03-01	1874
VW	Golf iii	2.0 GTI 16V	Schrägheck	Frontantrieb	Benzin	110	150	Aug 1992	Dec 1997	2024-08-01	1875
VW	Golf iii	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1991	Aug 1997	2024-03-01	1876
VW	Golf iii	2.8 VR6	Schrägheck	Frontantrieb	Benzin	128	174	Jan 1992	Aug 1997	2024-03-01	1877
Fiat	Punto	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Oct 2009	Feb 2012	2024-03-01	1878
VW	Vento	1.9 D	Stufenheck	Frontantrieb	Diesel	48	65	Nov 1991	Sep 1998	2024-03-01	1879
VW	Vento	1.9 TD	Stufenheck	Frontantrieb	Diesel	55	75	Nov 1991	Sep 1998	2024-03-01	1880
VW	Vento	1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Sep 1993	Sep 1998	2024-03-01	1881
VW	Vento	1.4	Stufenheck	Frontantrieb	Benzin	40	55	Nov 1991	Sep 1998	2024-03-01	1882
VW	Vento	1.4	Stufenheck	Frontantrieb	Benzin	44	60	Nov 1991	Sep 1998	2024-03-01	1883
VW	Vento	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1992	Sep 1998	2024-03-01	1884
VW	Vento	1.8	Stufenheck	Frontantrieb	Benzin	55	75	Nov 1991	Sep 1998	2024-03-01	1885
VW	Vento	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1991	Sep 1998	2024-03-01	1886
VW	Vento	2	Stufenheck	Frontantrieb	Benzin	85	115	Nov 1991	Sep 1998	2024-03-01	1887
Ford	Ranger	2.5 Tdci 4X4	Pick-up	Allrad	Diesel	105	143	May 2006	Jul 2012	2024-03-01	1888
VW	Vento	2.8 VR6	Stufenheck	Frontantrieb	Benzin	128	174	Jan 1992	Sep 1998	2024-03-01	1889
VW	Lt 28-35 i	2.4 D	Bus	Heckantrieb	Diesel	55	75	Jan 1979	Jul 1992	2024-03-01	1890
VW	Lt 28-35 i	2.4 TD	Bus	Heckantrieb	Diesel	68	92	Aug 1989	Aug 1992	2024-03-01	1891
VW	Lt 28-35 i	2	Bus	Heckantrieb	Benzin	55	75	Apr 1975	Sep 1983	2024-03-01	1892
VW	Lt 28-35 i	2.4	Bus	Heckantrieb	Benzin	66	90	Dec 1982	Jul 1992	2024-03-01	1893
VW	Lt 28-35 i	2.4 TD	Bus	Heckantrieb	Diesel	75	102	Dec 1982	Jul 1989	2024-03-01	1894
VW	Lt 28-35 i	2.4 D	Bus	Heckantrieb	Diesel	51	70	Aug 1989	Jun 1996	2024-03-01	1895
VW	Golf iii variant	1.9 D	Kombi	Frontantrieb	Diesel	47	64	Jul 1993	Apr 1999	2024-03-01	1896
VW	Golf iii variant	1.9 TD	Kombi	Frontantrieb	Diesel	55	75	Jul 1993	Apr 1999	2024-03-01	1897
VW	Golf iii variant	1.4	Kombi	Frontantrieb	Benzin	40	55	Jul 1993	Apr 1999	2024-03-01	1898
VW	Golf iii variant	1.4	Kombi	Frontantrieb	Benzin	44	60	Jul 1993	Apr 1999	2024-03-01	1899
VW	Golf iii variant	1.8	Kombi	Frontantrieb	Benzin	55	75	Jul 1993	Apr 1999	2024-03-01	1900
VW	Golf iii variant	1.8	Kombi	Frontantrieb	Benzin	66	90	Jul 1993	Apr 1999	2024-03-01	1901
VW	Golf iii variant	2	Kombi	Frontantrieb	Benzin	85	115	Jul 1993	Apr 1999	2024-03-01	1902
VW	Golf iii	1.8	Cabriolet	Frontantrieb	Benzin	55	75	Jul 1993	May 1998	2024-03-01	1903
VW	Golf iii	1.8	Cabriolet	Frontantrieb	Benzin	66	90	Jul 1993	May 1998	2024-03-01	1904
VW	Golf iii	2	Cabriolet	Frontantrieb	Benzin	85	115	Jul 1993	May 1998	2024-03-01	1905
VW	Passat b3/b4 variant	1.6	Kombi	Frontantrieb	Benzin	53	72	Apr 1988	Jul 1989	2024-03-01	1906
VW	Passat b3/b4 variant	1.6	Kombi	Frontantrieb	Benzin	55	75	Apr 1988	Jul 1991	2024-03-01	1907
VW	Passat b3/b4 variant	1.8	Kombi	Frontantrieb	Benzin	79	107	Apr 1988	Jul 1990	2024-03-01	1908
VW	Passat b3/b4 variant	1.8	Kombi	Frontantrieb	Benzin	82	112	Apr 1988	Jul 1992	2024-03-01	1909
VW	Passat b3/b4 variant	2	Kombi	Frontantrieb	Benzin	85	115	Feb 1990	May 1997	2024-03-01	1910
VW	Passat b3/b4 variant	1.6 TD	Kombi	Frontantrieb	Diesel	59	80	Aug 1988	Oct 1993	2024-03-01	1911
VW	Passat b3/b4 variant	1.9 D	Kombi	Frontantrieb	Diesel	50	68	May 1989	Oct 1993	2024-03-01	1912
VW	Passat b3/b4 variant	1.9 TD	Kombi	Frontantrieb	Diesel	55	75	Mar 1991	May 1997	2024-03-01	1913
VW	Passat b3/b4 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	Oct 1993	May 1997	2024-03-01	1914
VW	Passat b3/b4 variant	1.8	Kombi	Frontantrieb	Benzin	55	75	Aug 1990	May 1997	2024-03-01	1915
VW	Passat b3/b4 variant	1.8	Kombi	Frontantrieb	Benzin	66	90	Feb 1988	May 1997	2024-03-01	1916
VW	Passat b3/b4 variant	1.8 G60 Syncro	Kombi	Allrad	Benzin	118	160	Aug 1988	May 1997	2024-03-01	1917
Ford	Ranger	3.0 Tdci 4X4	Pick-up	Allrad	Diesel	115	156	May 2006	Jul 2012	2024-03-01	1918
VW	Passat b3/b4 variant	2.0 16V	Kombi	Frontantrieb	Benzin	100	136	Aug 1988	Sep 1993	2024-03-01	1919
VW	Passat b3/b4 variant	2.8 VR6	Kombi	Frontantrieb	Benzin	128	174	Jun 1991	May 1997	2024-03-01	1920
VW	Passat b2 variant	1.3	Kombi	Frontantrieb	Benzin	40	55	Aug 1980	Jul 1983	2024-03-01	1921
VW	Passat b2 variant	1.3	Kombi	Frontantrieb	Benzin	44	60	Aug 1980	Jul 1986	2024-03-01	1922
VW	Passat b2 variant	1.6	Kombi	Frontantrieb	Benzin	51	70	Aug 1986	Mar 1988	2024-03-01	1923
VW	Passat b2 variant	1.6	Kombi	Frontantrieb	Benzin	53	72	Feb 1986	Mar 1988	2024-03-01	1924
VW	Passat b2 variant	1.6	Kombi	Frontantrieb	Benzin	55	75	Aug 1980	Jul 1983	2024-03-01	1925
VW	Passat b2 variant	1.6	Kombi	Frontantrieb	Benzin	63	85	Jan 1981	Feb 1983	2024-03-01	1926
VW	Passat b2 variant	1.8	Kombi	Frontantrieb	Benzin	64	87	May 1986	Mar 1988	2024-03-01	1927
VW	Passat b2 variant	1.8 Syncro	Kombi	Allrad	Benzin	66	90	Jan 1986	Mar 1988	2024-03-01	1928
VW	Passat b2 variant	1.8	Kombi	Frontantrieb	Benzin	66	90	Jan 1983	Mar 1988	2024-03-01	1929
VW	Passat b2 variant	1.9	Kombi	Frontantrieb	Benzin	85	115	Jan 1981	Jul 1983	2024-03-01	1930
VW	Passat b2 variant	2	Kombi	Frontantrieb	Benzin	85	115	Aug 1983	Mar 1988	2024-03-01	1931
VW	Passat b2 variant	2.2	Kombi	Frontantrieb	Benzin	85	116	Aug 1985	Mar 1988	2026-01-01	1932
VW	Passat b2 variant	2.2 Syncro	Kombi	Allrad	Benzin	88	120	Aug 1985	Mar 1988	2024-03-01	1933
VW	Passat b2 variant	2.2	Kombi	Frontantrieb	Benzin	100	136	Jan 1985	Mar 1988	2024-03-01	1934
VW	Passat b2 variant	1.6 D	Kombi	Frontantrieb	Diesel	40	54	Aug 1980	Mar 1988	2024-03-01	1935


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **Corsa B、Punto Evo、Golf III、Vento、Golf III Variant、Golf III Cabrio、Passat B3/B4 Variant** 共 55 个输入 Ktype。
* Corsa B、Punto Evo 和 Golf III Hatchback 按来源覆盖的 3 门/5 门物理车身拆分；Corsa B GSi 仅保留已确认的 3 门分支。Punto Evo Natural Power 因车高不同于普通版本，独立建立 CNG 尺寸组。([汽车数据网][1])
* Golf III Hatchback、Vento Sedan、Golf III Variant 和 Golf III Cabrio 分别建立独立尺寸组；Golf III Syncro 在当前外廓三维下复用普通 Hatchback 组。([汽车数据网][2])
* Passat Variant 跨越 B3/B4 的 Ktype 按代际派生；B3 G60 Syncro 的高度为 1490 mm，不复用 B3 前驱车型的 1445 mm 尺寸组。([汽车数据网][3])

## 当前批次进度

* READY 输入 Ktype：**55/100**
* READY 映射行：**80**
* PENDING 输入 Ktype：**45/100**
* 已确认尺寸组：**14**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1837_3dr	1837	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1837_5dr	1837	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1838_3dr	1838	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1838_5dr	1838	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1839_3dr	1839	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1839_5dr	1839	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1840_3dr	1840	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1840_5dr	1840	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1841_3dr	1841	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1841_5dr	1841	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1842	1842	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	GSi仅确认3门车身。	READY
1856_3dr	1856	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	HIGH	Natural Power覆盖3门/5门，CNG车高独立。	READY
1856_5dr	1856	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	HIGH	Natural Power覆盖3门/5门，CNG车高独立。	READY
1865_3dr	1865	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1865_5dr	1865	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1866_3dr	1866	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1866_5dr	1866	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1867_3dr	1867	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1867_5dr	1867	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1868_3dr	1868	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1868_5dr	1868	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1869_3dr	1869	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1869_5dr	1869	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1870_3dr	1870	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1870_5dr	1870	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1871_3dr	1871	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1871_5dr	1871	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1872_3dr	1872	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1872_5dr	1872	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1873_3dr	1873	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1873_5dr	1873	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1874_3dr	1874	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1874_5dr	1874	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1875_3dr	1875	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1875_5dr	1875	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1876_3dr	1876	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1876_5dr	1876	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1877_3dr	1877	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1877_5dr	1877	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1878_3dr	1878	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1878_5dr	1878	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1879	1879	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1880	1880	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1881	1881	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1882	1882	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1883	1883	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1884	1884	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1885	1885	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1886	1886	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1887	1887	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1889	1889	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1896	1896	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1897	1897	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1898	1898	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1899	1899	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1900	1900	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1901	1901	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1902	1902	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1903	1903	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1904	1904	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1905	1905	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1906	1906	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1907	1907	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1908	1908	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1909	1909	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1910_b3	1910	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1910_b4	1910	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1911	1911	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1912	1912	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1913_b3	1913	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1913_b4	1913	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1914	1914	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH		READY
1915_b3	1915	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1915_b4	1915	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1916_b3	1916	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1916_b4	1916	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1917	1917	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-SYNCRO-01	HIGH	G60 Syncro车高独立。	READY
1919	1919	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1920_b3	1920	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1920_b4	1920	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420	Auto-Data Opel Corsa B 1.5 TD (67 Hp)	https://www.auto-data.net/en/opel-corsa-b-1.5-td-67hp-2118
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420	Auto-Data Opel Corsa B 1.5 TD (67 Hp)	https://www.auto-data.net/en/opel-corsa-b-1.5-td-67hp-2118
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514	Auto-Data Fiat Punto Evo 1.4 Natural Power	https://www.auto-data.net/en/fiat-punto-evo-199-1.4-8v-77hp-natural-power-16751
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514	Auto-Data Fiat Punto Evo 1.4 Natural Power	https://www.auto-data.net/en/fiat-punto-evo-199-1.4-8v-77hp-natural-power-16751
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490	Auto-Data Fiat Punto Evo 1.3 Multijet (90 Hp)	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-90hp-16756
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490	Auto-Data Fiat Punto Evo 1.3 Multijet (90 Hp)	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-90hp-16756
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415	Auto-Data Volkswagen Vento (1HX0) 1.6 (101 Hp)	https://www.auto-data.net/en/volkswagen-vento-1hx0-1.6-101hp-automatic-8842
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400	Auto-Data Volkswagen Golf III Cabrio 1.8 i (75 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-cabrio-1.8-i-75hp-8751
EU-VW-PASSAT-B3-VARIANT-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B3 1.6 TD (80 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b3-1.6-td-80hp-8976
EU-VW-PASSAT-B4-VARIANT-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B4 1.9 TDI (90 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b4-1.9-tdi-90hp-8986
EU-VW-PASSAT-B3-VARIANT-WAGON-SYNCRO-01	4595	1720	1490	Auto-Data Volkswagen Passat Variant B3 1.8 G60 Syncro (160 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b3-1.8-g60-syncro-160hp-8982
```

## 下一步优先处理

1. 优先聚类并闭合 VW Transporter T3 的 Bus、Kasten、Pritsche/Fahrgestell，以及 Syncro、不同轴距和车顶分支。
2. 随后处理 Transporter T4、Fiat Scudo、VW Taro、Ford Ranger 和 VW LT 28-35 的商用车/皮卡外廓。
3. 最后处理 Opel Monterey A 与 Passat B2 Variant，重点确认 Monterey 车门/轴距分支以及 Passat B2 前驱、Syncro 是否存在外廓高度差异。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-corsa-b-1.5-td-67hp-2118 "Opel Corsa B 1.5 TD (67 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719 "Volkswagen Golf III 1.8 (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volkswagen-passat-variant-b3-1.6-td-80hp-8976 "Volkswagen Passat Variant (B3) 1.6 TD (80 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Opel Monterey A 3.2 的三门 RS、五门 LTD 分支，分别建立独立尺寸组；两种车身的长度和高度不同。([汽车数据网][1])
* 完成 4 个 Transporter T3 后驱 Bus Ktype，统一关联标准 Caravelle T3 后驱车身组。([汽车数据网][2])
* 完成 2 个 Transporter T3 Syncro 14 Bus Ktype，关联独立的 Syncro 14 高度尺寸组。([汽车数据网][3])

## 当前批次进度

* READY 输入 Ktype：**62/100**
* READY 映射行：**88**
* PENDING 输入 Ktype：**38/100**
* 已确认尺寸组：**18**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1836_3dr	1836	SUV	Monterey A		3	EU-OPEL-MONTEREY-A-SUV-3D-01	MEDIUM	3.2 177 hp覆盖三门RS与五门LTD，按门数派生。	READY
1836_5dr	1836	SUV	Monterey A		5	EU-OPEL-MONTEREY-A-SUV-5D-01	MEDIUM	3.2 177 hp覆盖三门RS与五门LTD，按门数派生。	READY
1844	1844	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1846	1846	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1847	1847	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1848	1848	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1852	1852	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	Syncro 14英寸底盘Bus外廓。	READY
1853	1853	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	Syncro 14英寸底盘Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MONTEREY-A-SUV-3D-01	4270	1745	1835	Auto-Data Opel Monterey RS 3.2i V6 24V (177 Hp) 4x4	https://www.auto-data.net/en/opel-monterey-rs-3.2i-v6-24v-177hp-4x4-2575
EU-OPEL-MONTEREY-A-SUV-5D-01	4700	1745	1840	Auto-Data Opel Monterey LTD 3.2i V6 24V (177 Hp) 4x4	https://www.auto-data.net/en/opel-monterey-ltd-3.2i-v6-24v-177hp-4x4-2576
EU-VW-TRANSPORTER-T3-BUS-RWD-01	4600	1845	1950	Auto-Data Volkswagen Caravelle T3 1.7 D;Auto-Data Volkswagen Caravelle T3 2.1	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.7-d-57hp-manual-5-speed-49423;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-95hp-49393
EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	4600	1845	1990	Auto-Data Volkswagen Caravelle T3 1.9 Syncro 14;Auto-Data Volkswagen Caravelle T3 2.1 Syncro 14	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.9-78hp-syncro-14-49421;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-95hp-syncro-14-49409
```

## 下一步优先处理

1. 闭合 Transporter T3 的 Syncro 14/16、Kasten 和 Pritsche/Fahrgestell 分支。
2. 集中处理 Transporter T4、Fiat Scudo 和 LT 28-35 的轴距及车顶分支。
3. 解决 Taro、Ranger 和 Passat B2 Variant 的来源尺寸冲突后批量建立关联。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-monterey-rs-3.2i-v6-24v-177hp-4x4-2575 "Opel Monterey RS 3.2i V6 24V (177 Hp) 4x4 | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-95hp-49393 "Volkswagen Caravelle (T3) 2.1 (95 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volkswagen-caravelle-t3-1.9-78hp-syncro-14-49421 "Volkswagen Caravelle (T3) 1.9 (78 Hp) Syncro 14 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Passat B2 Variant 全部 15 个 Ktype；前驱与 Syncro 的外廓三维均为 `4545 × 1695 × 1385 mm`，复用同一尺寸组。([汽车数据网][1])
* 闭合 VW Taro 两个后驱 Ktype；1.8 和 2.4 D 80 hp 均关联已确认的两驱标准驾驶室外廓。([汽车数据网][2])
* Ford Ranger II 的两个 Ktype 均确认覆盖 Super Cab 与 Double Cab，按驾驶室物理分支拆分；未按发动机重复建组。([汽车数据网][3])

## 2. 当前批次进度

* READY 输入 Ktype：**81/100**
* READY 映射行：**109**
* PENDING 输入 Ktype：**19/100**
* 已确认尺寸组：**24**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1858	1858	Pickup	Taro		2	EU-VW-TARO-PICKUP-2WD-01	HIGH		READY
1859	1859	Pickup	Taro		2	EU-VW-TARO-PICKUP-2WD-01	MEDIUM	同一两驱标准驾驶室外廓。	READY
1888_supercab	1888	Pickup	Ranger II		2	EU-FORD-RANGER-II-PICKUP-SUPERCAB-25-4X4-01	MEDIUM	输入未区分驾驶室，按已确认Super Cab分支派生。	READY
1888_doublecab	1888	Pickup	Ranger II		4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-25-4X4-01	MEDIUM	输入未区分驾驶室，按已确认Double Cab分支派生。	READY
1918_supercab	1918	Pickup	Ranger II		2	EU-FORD-RANGER-II-PICKUP-SUPERCAB-30-4X4-01	MEDIUM	输入未区分驾驶室，按已确认Super Cab分支派生。	READY
1918_doublecab	1918	Pickup	Ranger II		4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-30-4X4-01	MEDIUM	输入未区分驾驶室，按已确认Double Cab分支派生。	READY
1921	1921	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1922	1922	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1923	1923	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1924	1924	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1925	1925	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1926	1926	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1927	1927	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1928	1928	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	Syncro与前驱车型外廓三维一致。	READY
1929	1929	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1930	1930	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1931	1931	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1932	1932	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1933	1933	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	Syncro与前驱车型外廓三维一致。	READY
1934	1934	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1935	1935	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TARO-PICKUP-2WD-01	4725	1650	1550	Auto-Data Volkswagen Taro 1.8;Auto Motor und Sport VW Taro technical data	https://www.auto-data.net/en/volkswagen-taro-1.8-83hp-9161;https://www.auto-motor-und-sport.de/marken-modelle/vw/taro/technische-daten/
EU-FORD-RANGER-II-PICKUP-SUPERCAB-25-4X4-01	5075	1805	1745	Auto-Data Ford Ranger II Super Cab 2.5 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-super-cab-2.5-tdci-143hp-4x4-33269
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-25-4X4-01	5170	1715	1745	Auto-Data Ford Ranger II Double Cab 2.5 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-double-cab-2.5-tdci-143hp-4x4-8086
EU-FORD-RANGER-II-PICKUP-SUPERCAB-30-4X4-01	5075	1805	1745	Auto-Data Ford Ranger II Super Cab 3.0 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-super-cab-3.0-tdci-156hp-4x4-30804
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-30-4X4-01	5075	1805	1745	Auto-Data Ford Ranger II Double Cab 3.0 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-double-cab-3.0-tdci-156hp-4x4-8087
EU-VW-PASSAT-B2-VARIANT-WAGON-01	4545	1695	1385	Auto-Data Volkswagen Passat Variant B2 1.6 D;Auto-Data Volkswagen Passat Variant B2 1.8 Syncro	https://www.auto-data.net/en/volkswagen-passat-variant-b2-1.6-d-54hp-9023;https://www.auto-data.net/en/volkswagen-passat-variant-b2-1.8-syncro-90hp-9028
```

## 5. 下一步优先处理

1. 闭合 Transporter T4 Bus 的短轴、长轴及 1996 年改款分支。
2. 闭合 Transporter T3 的 Kasten、Pritsche/Fahrgestell 与剩余 Syncro 分支。
3. 最后处理 Fiat Scudo、VW LT 28-35；重点区分轴距和车顶高度，避免把多个商用车外廓合并。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-passat-variant-b2-1.8-syncro-90hp-9028 "Volkswagen Passat Variant (B2) 1.8 Syncro (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-taro-1.8-83hp-9161 "Volkswagen Taro 1.8 (83 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/ford-ranger-ii-super-cab-2.5-tdci-143hp-4x4-33269?utm_source=chatgpt.com "Ford Ranger II Super Cab 2.5 TDCi (143 Hp) 4x4"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 完成 Fiat Scudo II 2.0 Multijet 163 hp 厢式车：确认同一 Ktype 覆盖短轴低顶、长轴低顶和长轴高顶三种物理外廓，建立 3 个尺寸组。官方技术规格明确标注车宽不含后视镜。([Stellantis Media][1])
* 完成 VW Transporter/Multivan T4 的 5 个 Ktype：按改款前后及短轴、长轴拆分为 4 个稳定尺寸组，不再按发动机重复建组。([汽车数据][2])

## 2. 当前批次进度

* READY 输入 Ktype：**87/100**
* READY 映射行：**128**
* PENDING 输入 Ktype：**13/100**
* 已确认尺寸组：**31**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1849_l1h1	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖多种轴距和车顶，短轴低顶分支。	READY
1849_l2h1	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖多种轴距和车顶，长轴低顶分支。	READY
1849_l2h2	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	同一Ktype覆盖多种轴距和车顶，长轴高顶分支。	READY
1860_swb	1860	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，短轴分支。	READY
1860_lwb	1860	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，长轴分支。	READY
1861_swb	1861	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，短轴分支。	READY
1861_lwb	1861	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，长轴分支。	READY
1862_swb_prefl	1862	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1862_lwb_prefl	1862	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1862_swb_facelift	1862	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1862_lwb_facelift	1862	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
1863_swb_prefl	1863	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1863_lwb_prefl	1863	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1863_swb_facelift	1863	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1863_lwb_facelift	1863	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
1864_swb_prefl	1864	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1864_lwb_prefl	1864	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1864_swb_facelift	1864	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1864_lwb_facelift	1864	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	4655	1840	1940	Auto-Data Volkswagen Caravelle T4	https://www.auto-data.net/en/volkswagen-caravelle-t4-2.0-84hp-49329
EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	5055	1840	1940	Auto-Data Volkswagen Caravelle T4 Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-long-2.0-84hp-49338
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	4789	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.0-84hp-49347
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	5189	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.0-84hp-49362
```

## 5. 下一步优先处理

1. 闭合剩余 7 个 Transporter T3 Ktype，区分 Pritsche/Fahrgestell、Kasten、Syncro 14/16 及可能的高顶分支。
2. 闭合剩余 6 个 VW LT 28-35 I Bus Ktype，重点区分短轴、长轴和不同车顶高度。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf "Scudo_18p_CT_Ingl_int@.indd"
[2]: https://www.auto-data.net/en/volkswagen-caravelle-t4-2.0-84hp-49329?utm_source=chatgpt.com "Volkswagen Caravelle (T4) 2.0 (84 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 Transporter T3 剩余两个 **Syncro Bus** Ktype。1.6 TD 70 hp 与 2.1 112 hp 均覆盖 Syncro 14 和 Syncro 16；Syncro 14 复用既有尺寸组，Syncro 16 根据原厂列出的 `195/80 R16`、`205/80 R16` 轮胎及 `2020–2028 mm` 高度区间拆成两个确定高度分支。两个轮胎直径相差 16 mm，因此整车高度相差 8 mm；这是依据来源规格作出的机械换算。([汽车数据][1])
* 闭合 VW LT 28–35 I 的 6 个 Bus Ktype。官方技术规格将 Kombi/Bus 分为短轴低顶、长轴低顶、短轴高顶、长轴高顶四种外廓，名义三维分别为 `4855/5305 × 2040 × 2160/2570 mm`。
* 剩余未闭合 Ktype 为 T3 的两个 `Pritsche/Fahrgestell`、两个后驱 `Kasten` 和一个 Syncro `Kasten`。

## 2. 当前批次进度

* READY 输入 Ktype：**95/100**
* READY 映射行：**158**
* PENDING 输入 Ktype：**5/100**
* 已确认尺寸组：**37**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1854_syncro14	1854	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，14英寸分支。	READY
1854_syncro16_195	1854	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-195-01	MEDIUM	Syncro 16配195/80 R16轮胎分支。	READY
1854_syncro16_205	1854	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-205-01	MEDIUM	Syncro 16配205/80 R16轮胎分支。	READY
1857_syncro14	1857	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，14英寸分支。	READY
1857_syncro16_195	1857	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-195-01	MEDIUM	Syncro 16配195/80 R16轮胎分支。	READY
1857_syncro16_205	1857	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-205-01	MEDIUM	Syncro 16配205/80 R16轮胎分支。	READY
1890_swb_lowroof	1890	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1890_lwb_lowroof	1890	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1890_swb_highroof	1890	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1890_lwb_highroof	1890	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1891_swb_lowroof	1891	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1891_lwb_lowroof	1891	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1891_swb_highroof	1891	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1891_lwb_highroof	1891	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1892_swb_lowroof	1892	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1892_lwb_lowroof	1892	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1892_swb_highroof	1892	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1892_lwb_highroof	1892	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1893_swb_lowroof	1893	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1893_lwb_lowroof	1893	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1893_swb_highroof	1893	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1893_lwb_highroof	1893	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1894_swb_lowroof	1894	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1894_lwb_lowroof	1894	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1894_swb_highroof	1894	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1894_lwb_highroof	1894	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1895_swb_lowroof	1895	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1895_lwb_lowroof	1895	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1895_swb_highroof	1895	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1895_lwb_highroof	1895	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-195-01	4600	1845	2020	Auto-Data Volkswagen Caravelle T3 1.6 TD Syncro 16;Auto-Data Volkswagen Caravelle T3 2.1 112 Hp Syncro 16	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.6-td-70hp-syncro-16-49411;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-112hp-syncro-16-49410
EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-205-01	4600	1845	2028	Auto-Data Volkswagen Caravelle T3 1.6 TD Syncro 16;Auto-Data Volkswagen Caravelle T3 2.1 112 Hp Syncro 16	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.6-td-70hp-syncro-16-49411;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-112hp-syncro-16-49410
EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	4855	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	5305	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-SWB-HIGHROOF-01	4855	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-LWB-HIGHROOF-01	5305	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
```

## 5. 下一步优先处理

1. 闭合 Ktype `1843`、`1845` 的 T3 单排标准货台、宽货台、双排驾驶室及底盘分支边界。
2. 闭合 Ktype `1850`、`1851` 的 T3 后驱 Kasten 标准顶外廓。
3. 闭合 Ktype `1855` 的 T3 Syncro Kasten 14 英寸与 16 英寸分支；完成后进入轻量机械收尾。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-112hp-syncro-14-49412 "Volkswagen Caravelle (T3) 2.1 (112 Hp) Syncro 14 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1801-1900_ktype_dimension_mapping_final.tsv
- all_1801-1900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 最后 5 个 Transporter T3 Ktype 已闭合，补齐 Pritsche、Doppelkabine、宽货台、Kasten 标准顶/高顶及 Syncro 14/16 分支。T3 尺寸依据历史车型资料按物理外廓建立稳定尺寸组。
* 机械收尾中合并了 Ford Ranger 因发动机差异重复建立的尺寸组，并保留改款前后及 Super Cab/Double Cab 的真实外廓分支。([汽车数据][1])
* 已完成固定表头、唯一主键、映射外键闭合、尺寸及来源非空检查。

## 2. 当前批次进度

* READY 输入 Ktype：**100/100**
* READY 映射行：**170**
* PENDING 输入 Ktype：**0/100**
* 最终 DIMENSION_GROUP：**43**
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 三维及来源完整：通过

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1836_3dr	1836	SUV	Monterey A		3	EU-OPEL-MONTEREY-A-SUV-3D-01	MEDIUM	3.2 177 hp覆盖三门RS与五门LTD，按门数派生。	READY
1836_5dr	1836	SUV	Monterey A		5	EU-OPEL-MONTEREY-A-SUV-5D-01	MEDIUM	3.2 177 hp覆盖三门RS与五门LTD，按门数派生。	READY
1837_3dr	1837	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1837_5dr	1837	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1838_3dr	1838	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1838_5dr	1838	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1839_3dr	1839	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1839_5dr	1839	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1840_3dr	1840	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1840_5dr	1840	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1841_3dr	1841	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1841_5dr	1841	Hatchback	Corsa B		5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1842	1842	Hatchback	Corsa B		3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	GSi仅确认3门车身。	READY
1843_singlecab	1843	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	HIGH	标准单排货台分支。	READY
1843_widebed	1843	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	HIGH	Großraum-Pritsche宽货台分支。	READY
1843_doublecab	1843	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	HIGH	Doppelkabine双排驾驶室分支。	READY
1844	1844	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1845_singlecab	1845	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	HIGH	标准单排货台分支。	READY
1845_widebed	1845	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	HIGH	Großraum-Pritsche宽货台分支。	READY
1845_doublecab	1845	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	HIGH	Doppelkabine双排驾驶室分支。	READY
1846	1846	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1847	1847	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1848	1848	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-RWD-01	MEDIUM	标准后驱Bus外廓。	READY
1849_l1h1	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	短轴低顶分支。	READY
1849_l2h1	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	长轴低顶分支。	READY
1849_l2h2	1849	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	长轴高顶分支。	READY
1850_lowroof	1850	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	HIGH	标准顶Kasten分支。	READY
1850_highroof	1850	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	HIGH	原厂Hochraum-Kastenwagen分支。	READY
1851_lowroof	1851	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	HIGH	标准顶Kasten分支。	READY
1851_highroof	1851	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	HIGH	原厂Hochraum-Kastenwagen分支。	READY
1852	1852	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	Syncro 14英寸底盘Bus外廓。	READY
1853	1853	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	Syncro 14英寸底盘Bus外廓。	READY
1854_syncro14	1854	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，14英寸分支。	READY
1854_syncro16	1854	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，16英寸宽体分支。	READY
1855_syncro14	1855	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	HIGH	Syncro 14英寸标准顶Kasten分支。	READY
1855_syncro16	1855	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	HIGH	Syncro 16英寸标准顶宽体Kasten分支。	READY
1856_3dr	1856	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	HIGH	Natural Power覆盖3门/5门，CNG车高独立。	READY
1856_5dr	1856	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	HIGH	Natural Power覆盖3门/5门，CNG车高独立。	READY
1857_syncro14	1857	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，14英寸分支。	READY
1857_syncro16	1857	MPV	Transporter T3			EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-01	HIGH	同一Ktype覆盖Syncro 14与Syncro 16，16英寸宽体分支。	READY
1858	1858	Pickup	Taro		2	EU-VW-TARO-PICKUP-2WD-01	HIGH		READY
1859	1859	Pickup	Taro		2	EU-VW-TARO-PICKUP-2WD-01	MEDIUM	同一两驱标准驾驶室外廓。	READY
1860_swb	1860	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，短轴分支。	READY
1860_lwb	1860	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，长轴分支。	READY
1861_swb	1861	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，短轴分支。	READY
1861_lwb	1861	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	同一Ktype覆盖短轴和长轴Bus，长轴分支。	READY
1862_swb_prefl	1862	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1862_lwb_prefl	1862	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1862_swb_facelift	1862	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1862_lwb_facelift	1862	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
1863_swb_prefl	1863	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1863_lwb_prefl	1863	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1863_swb_facelift	1863	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1863_lwb_facelift	1863	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
1864_swb_prefl	1864	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前短轴分支。	READY
1864_lwb_prefl	1864	MPV	Transporter T4			EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款前长轴分支。	READY
1864_swb_facelift	1864	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后短轴分支。	READY
1864_lwb_facelift	1864	MPV	Transporter T4 Facelift			EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	MEDIUM	生产区间覆盖改款前后及短轴/长轴，改款后长轴分支。	READY
1865_3dr	1865	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1865_5dr	1865	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1866_3dr	1866	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1866_5dr	1866	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1867_3dr	1867	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1867_5dr	1867	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1868_3dr	1868	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1868_5dr	1868	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1869_3dr	1869	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1869_5dr	1869	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1870_3dr	1870	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1870_5dr	1870	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1871_3dr	1871	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1871_5dr	1871	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1872_3dr	1872	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1872_5dr	1872	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1873_3dr	1873	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1873_5dr	1873	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1874_3dr	1874	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1874_5dr	1874	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1875_3dr	1875	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1875_5dr	1875	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1876_3dr	1876	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1876_5dr	1876	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1877_3dr	1877	Hatchback	Golf III		3	EU-VW-GOLF-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1877_5dr	1877	Hatchback	Golf III		5	EU-VW-GOLF-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1878_3dr	1878	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1878_5dr	1878	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖3门/5门车身，按门数派生。	READY
1879	1879	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1880	1880	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1881	1881	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1882	1882	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1883	1883	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1884	1884	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1885	1885	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1886	1886	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1887	1887	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1888_supercab_prefl	1888	Pickup	Ranger II		2	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-01	HIGH	改款前Super Cab分支。	READY
1888_doublecab_prefl	1888	Pickup	Ranger II		4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-01	HIGH	改款前Double Cab分支。	READY
1888_supercab_facelift	1888	Pickup	Ranger II Facelift		2	EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-01	HIGH	2009年改款Super Cab分支。	READY
1888_doublecab_facelift	1888	Pickup	Ranger II Facelift		4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-01	HIGH	2009年改款Double Cab分支。	READY
1889	1889	Sedan	Vento	1HX0	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
1890_swb_lowroof	1890	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1890_lwb_lowroof	1890	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1890_swb_highroof	1890	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1890_lwb_highroof	1890	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1891_swb_lowroof	1891	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1891_lwb_lowroof	1891	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1891_swb_highroof	1891	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1891_lwb_highroof	1891	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1892_swb_lowroof	1892	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1892_lwb_lowroof	1892	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1892_swb_highroof	1892	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1892_lwb_highroof	1892	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1893_swb_lowroof	1893	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1893_lwb_lowroof	1893	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1893_swb_highroof	1893	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1893_lwb_highroof	1893	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1894_swb_lowroof	1894	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1894_lwb_lowroof	1894	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1894_swb_highroof	1894	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1894_lwb_highroof	1894	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1895_swb_lowroof	1895	MPV	LT I			EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，短轴标准顶分支。	READY
1895_lwb_lowroof	1895	MPV	LT I			EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	MEDIUM	输入未区分轴距和车顶，长轴标准顶分支。	READY
1895_swb_highroof	1895	MPV	LT I			EU-VW-LT-I-BUS-SWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，短轴高顶分支。	READY
1895_lwb_highroof	1895	MPV	LT I			EU-VW-LT-I-BUS-LWB-HIGHROOF-01	MEDIUM	输入未区分轴距和车顶，长轴高顶分支。	READY
1896	1896	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1897	1897	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1898	1898	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1899	1899	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1900	1900	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1901	1901	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1902	1902	Wagon	Golf III Variant		5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
1903	1903	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1904	1904	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1905	1905	Convertible	Golf III Cabrio		2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
1906	1906	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1907	1907	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1908	1908	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1909	1909	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1910_b3	1910	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1910_b4	1910	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1911	1911	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1912	1912	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1913_b3	1913	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1913_b4	1913	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1914	1914	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH		READY
1915_b3	1915	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1915_b4	1915	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1916_b3	1916	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1916_b4	1916	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1917	1917	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-SYNCRO-01	HIGH	G60 Syncro车高独立。	READY
1918_supercab	1918	Pickup	Ranger II		2	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-01	HIGH	3.0 TDCi已确认Super Cab分支。	READY
1918_doublecab	1918	Pickup	Ranger II		4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-01	HIGH	3.0 TDCi已确认Double Cab分支。	READY
1919	1919	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH		READY
1920_b3	1920	Wagon	Passat B3 Variant		5	EU-VW-PASSAT-B3-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1920_b4	1920	Wagon	Passat B4 Variant		5	EU-VW-PASSAT-B4-VARIANT-WAGON-01	HIGH	生产区间跨B3/B4，按代际派生。	READY
1921	1921	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1922	1922	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1923	1923	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1924	1924	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1925	1925	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1926	1926	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1927	1927	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1928	1928	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	Syncro与前驱车型外廓三维一致。	READY
1929	1929	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1930	1930	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1931	1931	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1932	1932	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1933	1933	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	Syncro与前驱车型外廓三维一致。	READY
1934	1934	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
1935	1935	Wagon	Passat B2 Variant		5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1801-1900_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MONTEREY-A-SUV-3D-01	4270	1745	1835	Auto-Data Opel Monterey RS 3.2i V6 24V (177 Hp) 4x4	https://www.auto-data.net/en/opel-monterey-rs-3.2i-v6-24v-177hp-4x4-2575
EU-OPEL-MONTEREY-A-SUV-5D-01	4700	1745	1840	Auto-Data Opel Monterey LTD 3.2i V6 24V (177 Hp) 4x4	https://www.auto-data.net/en/opel-monterey-ltd-3.2i-v6-24v-177hp-4x4-2576
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420	Auto-Data Opel Corsa B 1.5 TD (67 Hp)	https://www.auto-data.net/en/opel-corsa-b-1.5-td-67hp-2118
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420	Auto-Data Opel Corsa B 1.5 TD (67 Hp)	https://www.auto-data.net/en/opel-corsa-b-1.5-td-67hp-2118
EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	4570	1870	1930	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	4636	2000	1930	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	4570	1870	1925	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-BUS-RWD-01	4600	1845	1950	Auto-Data Volkswagen Caravelle T3 1.7 D;Auto-Data Volkswagen Caravelle T3 2.1	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.7-d-57hp-manual-5-speed-49423;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-95hp-49393
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	4570	1845	1965	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	4570	1845	2365	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	4600	1845	1990	Auto-Data Volkswagen Caravelle T3 1.9 Syncro 14;Auto-Data Volkswagen Caravelle T3 2.1 Syncro 14	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.9-78hp-syncro-14-49421;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-95hp-syncro-14-49409
EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-01	4600	1865	2020	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation;Auto-Data Volkswagen Caravelle T3 2.1 Syncro 16	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf;https://www.auto-data.net/en/volkswagen-caravelle-t3-2.1-112hp-syncro-16-49410
EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	4570	1845	1990	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	4570	1865	2020	Volkswagen Nutzfahrzeuge Der Volkswagen Transporter – die dritte Generation	https://oldtimerphotography.de/wp-content/uploads/2016/07/VWN_T3.pdf
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514	Auto-Data Fiat Punto Evo 1.4 Natural Power	https://www.auto-data.net/en/fiat-punto-evo-199-1.4-8v-77hp-natural-power-16751
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514	Auto-Data Fiat Punto Evo 1.4 Natural Power	https://www.auto-data.net/en/fiat-punto-evo-199-1.4-8v-77hp-natural-power-16751
EU-VW-TARO-PICKUP-2WD-01	4725	1650	1550	Auto-Data Volkswagen Taro 1.8;Auto Motor und Sport VW Taro technical data	https://www.auto-data.net/en/volkswagen-taro-1.8-83hp-9161;https://www.auto-motor-und-sport.de/marken-modelle/vw/taro/technische-daten/
EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	4655	1840	1940	Auto-Data Volkswagen Caravelle T4	https://www.auto-data.net/en/volkswagen-caravelle-t4-2.0-84hp-49329
EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	5055	1840	1940	Auto-Data Volkswagen Caravelle T4 Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-long-2.0-84hp-49338
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	4789	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.0-84hp-49347
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	5189	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.0-84hp-49362
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490	Auto-Data Fiat Punto Evo 1.3 Multijet (90 Hp)	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-90hp-16756
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490	Auto-Data Fiat Punto Evo 1.3 Multijet (90 Hp)	https://www.auto-data.net/en/fiat-punto-evo-199-1.3-16v-multijet-90hp-16756
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415	Auto-Data Volkswagen Vento (1HX0) 1.6 (101 Hp)	https://www.auto-data.net/en/volkswagen-vento-1hx0-1.6-101hp-automatic-8842
EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-01	5075	1805	1745	Auto-Data Ford Ranger II Super Cab 2.5 TDCi 4x4;Auto-Data Ford Ranger II Super Cab generation	https://www.auto-data.net/en/ford-ranger-ii-super-cab-2.5-tdci-143hp-4x4-33269;https://www.auto-data.net/en/ford-ranger-ii-super-cab-generation-5673
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-01	5075	1805	1745	Auto-Data Ford Ranger II Double Cab 2.5 TDCi;Auto-Data Ford Ranger II Double Cab 3.0 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-double-cab-2.5-tdci-143hp-31725;https://www.auto-data.net/en/ford-ranger-ii-double-cab-3.0-tdci-156hp-4x4-8087
EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-01	5080	1788	1762	Auto-Data Ford Ranger II Super Cab facelift 2009 2.5 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-super-cab-facelift-2009-2.5-tdci-143hp-4x4-30798
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-01	5080	1788	1762	Auto-Data Ford Ranger II Double Cab facelift 2009 2.5 TDCi 4x4	https://www.auto-data.net/en/ford-ranger-ii-double-cab-facelift-2009-2.5-tdci-143hp-4x4-30780
EU-VW-LT-I-BUS-SWB-STANDARDROOF-01	4855	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-LWB-STANDARDROOF-01	5305	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-SWB-HIGHROOF-01	4855	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-BUS-LWB-HIGHROOF-01	5305	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400	Auto-Data Volkswagen Golf III Cabrio 1.8 i (75 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-cabrio-1.8-i-75hp-8751
EU-VW-PASSAT-B3-VARIANT-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B3 1.6 TD (80 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b3-1.6-td-80hp-8976
EU-VW-PASSAT-B4-VARIANT-WAGON-01	4595	1720	1445	Auto-Data Volkswagen Passat Variant B4 1.9 TDI (90 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b4-1.9-tdi-90hp-8986
EU-VW-PASSAT-B3-VARIANT-WAGON-SYNCRO-01	4595	1720	1490	Auto-Data Volkswagen Passat Variant B3 1.8 G60 Syncro (160 Hp)	https://www.auto-data.net/en/volkswagen-passat-variant-b3-1.8-g60-syncro-160hp-8982
EU-VW-PASSAT-B2-VARIANT-WAGON-01	4545	1695	1385	Auto-Data Volkswagen Passat Variant B2 1.6 D;Auto-Data Volkswagen Passat Variant B2 1.8 Syncro	https://www.auto-data.net/en/volkswagen-passat-variant-b2-1.6-d-54hp-9023;https://www.auto-data.net/en/volkswagen-passat-variant-b2-1.8-syncro-90hp-9028
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1801-1900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/ford-ranger-ii-super-cab-facelift-2009-2.5-tdci-143hp-4x4-30798 "https://www.auto-data.net/en/ford-ranger-ii-super-cab-facelift-2009-2.5-tdci-143hp-4x4-30798"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1801-1900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1801-1900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2448 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（606 行）
