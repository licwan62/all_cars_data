# 任务：all 第 2301-2400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0024__4af44d8b


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2301-2400 行

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
all 第 2301-2400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	305 i break	1.5	Kombi	Frontantrieb	Benzin	54	73	Aug 1980	Sep 1982	2024-03-01	2350
Peugeot	305 i break	1.5 Diesel	Kombi	Frontantrieb	Diesel	36	49	Aug 1980	Sep 1982	2024-03-01	2351
Peugeot	305 ii break	1.9 Diesel	Kombi	Frontantrieb	Diesel	47	64	Oct 1982	Dec 1988	2024-03-01	2352
Peugeot	305 ii break	1.9 Diesel	Kombi	Frontantrieb	Diesel	48	65	Oct 1982	Dec 1988	2024-03-01	2353
Peugeot	309 i	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Oct 1985	Jul 1989	2024-03-01	2354
Peugeot	309 i	1.3	Schrägheck	Frontantrieb	Benzin	47	64	Oct 1985	Jul 1989	2024-03-01	2355
Peugeot	309 i	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Mar 1989	Jul 1989	2024-03-01	2356
Peugeot	309 i	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1989	Jul 1989	2024-03-01	2357
Peugeot	309 i	1.4	Schrägheck	Frontantrieb	Benzin	62	84	Aug 1988	Aug 1989	2024-03-01	2358
Peugeot	309 i	1.6	Schrägheck	Frontantrieb	Benzin	53	72	Aug 1987	Jul 1989	2024-03-01	2359
Peugeot	309 i	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1985	Jul 1989	2024-03-01	2361
Peugeot	309 i	1.6	Schrägheck	Frontantrieb	Benzin	76	103	Nov 1985	Sep 1988	2024-03-01	2362
Peugeot	309 i	1.9	Schrägheck	Frontantrieb	Benzin	72	98	Mar 1986	Jul 1989	2024-03-01	2363
Peugeot	309 i	1.9	Schrägheck	Frontantrieb	Benzin	75	102	Oct 1985	Jul 1989	2024-03-01	2364
Peugeot	309 i	1.9	Schrägheck	Frontantrieb	Benzin	80	109	Jul 1988	Jul 1989	2024-03-01	2365
Peugeot	309 i	1.9 GTI	Schrägheck	Frontantrieb	Benzin	88	120	Jul 1988	Jul 1989	2024-03-01	2366
Peugeot	309 i	1.9 GTI	Schrägheck	Frontantrieb	Benzin	94	128	Oct 1986	Jul 1989	2024-03-01	2367
Peugeot	309 i	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Jun 1986	Jul 1989	2024-03-01	2368
Peugeot	309 ii	1.9 Diesel	Schrägheck	Frontantrieb	Diesel	47	64	Jul 1989	Dec 1993	2024-03-01	2369
Peugeot	309 ii	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1990	Dec 1993	2024-03-01	2372
Peugeot	309 ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jul 1989	Dec 1993	2024-03-01	2373
Peugeot	309 ii	1.6	Schrägheck	Frontantrieb	Benzin	65	88	Jul 1989	Dec 1993	2024-03-01	2374
Peugeot	309 ii	1.9	Schrägheck	Frontantrieb	Benzin	72	98	Aug 1989	Dec 1993	2024-03-01	2375
Peugeot	309 ii	1.9	Schrägheck	Frontantrieb	Benzin	80	109	Oct 1990	Dec 1993	2024-03-01	2377
Peugeot	309 ii	1.9 GTI	Schrägheck	Frontantrieb	Benzin	88	120	Jul 1989	Dec 1993	2024-03-01	2378
Peugeot	405 i	1.6	Stufenheck	Frontantrieb	Benzin	53	72	Jul 1987	Dec 1992	2024-03-01	2379
Peugeot	405 i	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1989	Dec 1992	2024-03-01	2380
Peugeot	405 i	1.9	Stufenheck	Frontantrieb	Benzin	70	95	Jul 1987	Dec 1992	2024-03-01	2381
Peugeot	405 i	1.9 Sport Mi-16	Stufenheck	Frontantrieb	Benzin	116	158	Jul 1987	Nov 1992	2024-03-01	2382
Peugeot	405 i	1.8 Turbo Diesel	Stufenheck	Frontantrieb	Diesel	66	90	Mar 1988	Dec 1992	2024-03-01	2384
Peugeot	405 i	1.9 Diesel	Stufenheck	Frontantrieb	Diesel	47	64	Jul 1988	Sep 1992	2024-03-01	2385
Peugeot	405 i	1.9 Diesel	Stufenheck	Frontantrieb	Diesel	51	69	Mar 1988	Dec 1992	2024-03-01	2386
Peugeot	405 ii	1.9 D	Stufenheck	Frontantrieb	Diesel	47	64	Aug 1992	Oct 1995	2024-03-01	2388
Peugeot	405 ii	1.9 TD	Stufenheck	Frontantrieb	Diesel	66	90	Aug 1992	Oct 1995	2024-03-01	2390
Peugeot	405 ii	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1992	Oct 1995	2024-03-01	2391
Peugeot	405 i	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Jul 1987	Jun 1988	2024-03-01	2392
Peugeot	405 i	1.6	Stufenheck	Frontantrieb	Benzin	65	88	Jul 1987	Dec 1992	2024-03-01	2393
Peugeot	405 ii	1.6	Stufenheck	Frontantrieb	Benzin	65	88	Aug 1992	Oct 1995	2024-03-01	2394
Peugeot	405 ii	1.8	Stufenheck	Frontantrieb	Benzin	74	101	Aug 1992	Oct 1995	2024-03-01	2395
Peugeot	405 i	1.9 Injection	Stufenheck	Frontantrieb	Benzin	77	105	Jul 1987	Dec 1992	2024-03-01	2396
Peugeot	405 i	1.9	Stufenheck	Frontantrieb	Benzin	80	109	Jun 1987	Jul 1992	2024-03-01	2397
Peugeot	405 i	1.9 4X4	Stufenheck	Allrad	Benzin	80	109	Jul 1988	Dec 1992	2024-03-01	2398
Peugeot	405 i	1.9	Stufenheck	Frontantrieb	Benzin	88	120	Jun 1987	Jul 1992	2024-03-01	2399
Peugeot	405 i	1.9 Sport Mi-16	Stufenheck	Frontantrieb	Benzin	108	147	Jun 1987	Jul 1992	2024-03-01	2400
Peugeot	405 i	1.9 Sport Mi-16 4X4	Stufenheck	Allrad	Benzin	108	147	Jun 1987	Jul 1992	2024-03-01	2401
Mazda	Cx-7	2.5 MZR	SUV	Frontantrieb	Benzin	120	163	Jul 2009	Mar 2013	2024-03-01	2403
Peugeot	405 ii	2	Stufenheck	Frontantrieb	Benzin	89	121	Aug 1992	Oct 1995	2024-03-01	2407
Peugeot	405 ii	2.0 X4	Stufenheck	Allrad	Benzin	89	121	Aug 1992	Oct 1995	2024-03-01	2408
Peugeot	405 ii	2.0 Mi-16	Stufenheck	Frontantrieb	Benzin	112	152	Aug 1992	Oct 1995	2024-03-01	2409
Peugeot	405 ii	2.0 T 16 X4	Stufenheck	Allrad	Benzin	144	196	Aug 1992	Oct 1995	2024-03-01	2410
Peugeot	405 i break	1.6	Kombi	Frontantrieb	Benzin	53	72	Oct 1988	Aug 1992	2024-03-01	2411
Peugeot	405 i break	1.6	Kombi	Frontantrieb	Benzin	66	90	Oct 1988	Aug 1992	2024-03-01	2412
Peugeot	405 i break	1.9	Kombi	Frontantrieb	Benzin	70	95	Oct 1988	Aug 1992	2024-03-01	2413
Peugeot	405 i break	1.9	Kombi	Frontantrieb	Benzin	88	120	Oct 1988	Aug 1992	2024-03-01	2414
Peugeot	405 i break	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Oct 1988	Aug 1992	2024-03-01	2416
Peugeot	405 i break	1.9 D	Kombi	Frontantrieb	Diesel	47	64	Oct 1988	Aug 1992	2024-03-01	2417
Peugeot	405 i break	1.9 D	Kombi	Frontantrieb	Diesel	51	69	Oct 1988	Aug 1992	2024-03-01	2418
Peugeot	405 ii break	1.9 D	Kombi	Frontantrieb	Diesel	47	64	Aug 1992	Oct 1996	2024-03-01	2420
Peugeot	405 ii break	1.9 TD	Kombi	Frontantrieb	Diesel	66	90	Aug 1992	Oct 1996	2024-03-01	2422
Peugeot	405 ii break	1.4	Kombi	Frontantrieb	Benzin	55	75	Aug 1992	Oct 1996	2024-03-01	2423
Peugeot	405 i break	1.6	Kombi	Frontantrieb	Benzin	65	88	Oct 1988	Aug 1992	2024-03-01	2424
Peugeot	405 i break	1.6	Kombi	Frontantrieb	Benzin	55	75	Oct 1988	Aug 1992	2024-03-01	2425
Peugeot	405 ii break	1.6	Kombi	Frontantrieb	Benzin	65	88	Aug 1992	Oct 1996	2024-03-01	2426
Peugeot	405 ii break	1.8	Kombi	Frontantrieb	Benzin	74	101	Aug 1992	Oct 1996	2024-03-01	2427
Peugeot	405 i break	1.9	Kombi	Frontantrieb	Benzin	77	105	Oct 1988	Aug 1992	2024-03-01	2428
Peugeot	405 i break	1.9	Kombi	Frontantrieb	Benzin	80	109	Oct 1988	Aug 1992	2024-03-01	2429
Peugeot	405 ii break	2	Kombi	Frontantrieb	Benzin	89	121	Aug 1992	Oct 1996	2024-03-01	2433
Peugeot	405 ii break	2.0 4X4	Kombi	Allrad	Benzin	89	121	Aug 1992	Oct 1996	2024-03-01	2434
Peugeot	504	1.8	Stufenheck	Heckantrieb	Benzin	58	79	Jan 1971	Jun 1983	2024-03-01	2435
Peugeot	504	2	Stufenheck	Heckantrieb	Benzin	71	97	Mar 1971	Jun 1986	2024-03-01	2436
Peugeot	504	2.0 TI	Stufenheck	Heckantrieb	Benzin	78	106	Jan 1971	Jun 1983	2024-03-01	2437
Peugeot	604	2.7 TI, STI	Stufenheck	Heckantrieb	Benzin	106	144	Aug 1977	May 1983	2024-03-01	2438
Peugeot	505	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Jun 1981	Oct 1985	2024-03-01	2439
Peugeot	505	1.8	Stufenheck	Heckantrieb	Benzin	60	82	Jan 1982	Oct 1985	2024-03-01	2440
Peugeot	505	2	Stufenheck	Heckantrieb	Benzin	71	97	Nov 1980	Dec 1985	2024-03-01	2441
Peugeot	505	2	Stufenheck	Heckantrieb	Benzin	72	98	Sep 1985	Sep 1995	2024-03-01	2442
Peugeot	505	2.0 TI, STI	Stufenheck	Heckantrieb	Benzin	81	110	Aug 1979	Oct 1986	2024-03-01	2443
Peugeot	505	2.2 Turbo Injection	Stufenheck	Heckantrieb	Benzin	114	155	Mar 1984	Oct 1988	2024-03-01	2444
Peugeot	505	2.2	Stufenheck	Heckantrieb	Benzin	84	114	Mar 1986	Dec 1993	2024-03-01	2445
Peugeot	505	2.2	Stufenheck	Heckantrieb	Benzin	85	116	May 1981	Oct 1984	2024-03-01	2446
Peugeot	505	2.2 GTI	Stufenheck	Heckantrieb	Benzin	90	122	Aug 1983	Dec 1993	2024-03-01	2447
Peugeot	505	2.8 GTI V6	Stufenheck	Heckantrieb	Benzin	105	143	Jun 1986	Dec 1993	2024-03-01	2448
Peugeot	505	2.3 Turbo Diesel	Stufenheck	Heckantrieb	Diesel	59	80	Sep 1980	Jun 1986	2024-03-01	2449
Peugeot	505	2.5 Diesel	Stufenheck	Heckantrieb	Diesel	55	75	Jun 1981	Dec 1993	2024-03-01	2450
Peugeot	505	2.5 Turbo Diesel	Stufenheck	Heckantrieb	Diesel	66	90	Oct 1983	Dec 1993	2024-03-01	2451
Peugeot	505	2.5 Turbo Diesel	Stufenheck	Heckantrieb	Diesel	77	105	Oct 1986	Dec 1993	2024-03-01	2452
Peugeot	505	2	Kombi	Heckantrieb	Benzin	69	94	Aug 1983	Dec 1985	2024-03-01	2453
Peugeot	505	2.2	Kombi	Heckantrieb	Benzin	84	114	Jan 1986	Dec 1993	2024-03-01	2454
Peugeot	505	2.5 Diesel	Kombi	Heckantrieb	Diesel	51	70	Jan 1986	Dec 1993	2024-03-01	2455
Peugeot	505	2.5 Diesel	Kombi	Heckantrieb	Diesel	55	75	Aug 1983	Dec 1993	2024-03-01	2456
Peugeot	605	2.1 Turbo Diesel	Stufenheck	Frontantrieb	Diesel	80	109	Jun 1989	Sep 1999	2024-03-01	2457
Peugeot	605	2	Stufenheck	Frontantrieb	Benzin	89	121	Jun 1989	Sep 1999	2024-03-01	2458
Peugeot	605	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	104	141	Jul 1992	Sep 1999	2024-03-01	2459
Peugeot	605	3	Stufenheck	Frontantrieb	Benzin	123	167	Oct 1989	Sep 1999	2024-03-01	2460
Peugeot	605	3.0 SV 24	Stufenheck	Frontantrieb	Benzin	147	200	Aug 1989	Sep 1999	2024-03-01	2461
Peugeot	106 i	1.4 D	Schrägheck	Frontantrieb	Diesel	37	50	Sep 1992	Apr 1996	2024-03-01	2463
Peugeot	106 i	1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1991	Apr 1996	2024-03-01	2464
Peugeot	106 i	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1991	Apr 1996	2024-03-01	2465
Peugeot	106 i	1.3	Schrägheck	Frontantrieb	Benzin	72	98	Oct 1993	Apr 1996	2024-03-01	2466
Peugeot	106 i	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1991	Apr 1996	2024-03-01	2467


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Peugeot 305 I/II Break、Peugeot 405 I/II Sedan、405 I/II Break、Mazda CX-7 ER** 共 9 个尺寸组。
* Peugeot 305 两代 Break 已按 `581D`、`581E` 分组，尺寸分别采用对应代际的不含后视镜宽度。([汽车目录][1])
* Peugeot 405 II 已区分普通车身、Mi-16 宽体和 T16 低车身；普通四驱 2.0 X4仍复用标准尺寸组。([汽车目录][2])
* 405 I/II Break 已按改款前后不同宽度建立独立组；Mazda CX-7 2.5 MZR 已命中 ER 车身。([汽车目录][3])

## 当前批次进度

* READY 输入 Ktype：**47/100**
* PENDING 输入 Ktype：**53/100**
* READY 映射行：**47**
* 已确认尺寸组：**9**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2350	2350	Wagon	305 I	581D	5	EU-PEUGEOT-305-I-BREAK-01	MEDIUM	305 I Break五门旅行车。	READY
2351	2351	Wagon	305 I	581D	5	EU-PEUGEOT-305-I-BREAK-01	MEDIUM	305 I Break五门旅行车。	READY
2352	2352	Wagon	305 II	581E	5	EU-PEUGEOT-305-II-BREAK-01	MEDIUM	305 II Break五门旅行车。	READY
2353	2353	Wagon	305 II	581E	5	EU-PEUGEOT-305-II-BREAK-01	MEDIUM	305 II Break五门旅行车。	READY
2379	2379	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2380	2380	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2381	2381	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2382	2382	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2384	2384	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2385	2385	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2386	2386	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2388	2388	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2390	2390	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2391	2391	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2392	2392	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2393	2393	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2394	2394	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2395	2395	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2396	2396	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2397	2397	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2398	2398	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2399	2399	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2400	2400	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2401	2401	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2403	2403	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-01	HIGH		READY
2407	2407	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2408	2408	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2409	2409	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-MI16-01	HIGH	Mi-16宽体外廓。	READY
2410	2410	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-T16-01	HIGH	T16低车身外廓。	READY
2411	2411	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2412	2412	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2413	2413	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2414	2414	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2416	2416	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2417	2417	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2418	2418	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2420	2420	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2422	2422	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2423	2423	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2424	2424	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2425	2425	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2426	2426	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2427	2427	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2428	2428	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2429	2429	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2433	2433	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2434	2434	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-305-I-BREAK-01	4259	1640	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/2568110/peugeot_305_break_gl.html
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/2568290/peugeot_305_break_gl.html
EU-PEUGEOT-405-I-SEDAN-01	4408	1716	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/2584700/peugeot_405_ge_1_6.html
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585285/peugeot_405_sri_2_0_x4.html
EU-PEUGEOT-405-II-SEDAN-MI16-01	4408	1716	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585360/peugeot_405_mi_16.html
EU-PEUGEOT-405-II-SEDAN-T16-01	4408	1716	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585705/peugeot_405_t_16.html
EU-MAZDA-CX-7-ER-SUV-01	4682	1872	1645	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1691735/mazda_cx-7_i_sport.html
EU-PEUGEOT-405-I-BREAK-01	4398	1716	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/2584820/peugeot_405_break_sri_1_9.html
EU-PEUGEOT-405-II-BREAK-01	4398	1704	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2587430/peugeot_405_break_hunter_1_9_dt.html
```

## 下一步优先处理

1. 核对 Peugeot 309 I/II 的 `10A/10C`、`3A/3C` 三门和五门分支，避免把不同门数物理车身合并。
2. 闭合 Peugeot 505 改款前后 Sedan，以及 Break 的独立尺寸组。
3. 补齐 Peugeot 504、604、605 和 106 I；其中 605 需判断跨 1995 年改款的 Ktype 是否派生 `prefl/facelift`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/2568110/peugeot_305_break_gl.html?utm_source=chatgpt.com "1981 Peugeot 305 Break GL Specs Review (44 kW ..."
[2]: https://www.automobile-catalog.com/car/1993/2585285/peugeot_405_sri_2_0_x4.html?utm_source=chatgpt.com "1993 Peugeot 405 SRI 2.0 X4 Specs Review (89 kW / 121 ..."
[3]: https://www.automobile-catalog.com/car/1989/2584820/peugeot_405_break_sri_1_9.html?utm_source=chatgpt.com "1989 Peugeot 405 Break SRI 1.9 Specs Review (90 kW ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Peugeot 309 I、309 II 已按三门和五门物理车身拆分；BodyCode 固定为 Phase I 的 `10C/10A`、Phase II 的 `3C/3A`。309 的发动机记录覆盖三门和五门版本，不能继续保留无门数基础行。([汽车信息][1])
* 本轮闭合 4 个尺寸组。相同代际三门和五门虽三维接近或相同，但因车门和侧围外廓不同，分别建立稳定尺寸组。Phase I 使用 `4051×1628×1380 mm`；Phase II 三门使用 `4051×1630×1380 mm`，五门使用 `4050×1630×1380 mm`。([汽车数据][2])

## 当前批次进度

* READY 输入 Ktype：**68/100**
* PENDING 输入 Ktype：**32/100**
* READY 映射行：**89**
* 已确认尺寸组：**13**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2354_3dr	2354	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2354_5dr	2354	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2355_3dr	2355	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2355_5dr	2355	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2356_3dr	2356	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2356_5dr	2356	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2357_3dr	2357	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2357_5dr	2357	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2358_3dr	2358	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2358_5dr	2358	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2359_3dr	2359	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2359_5dr	2359	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2361_3dr	2361	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2361_5dr	2361	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2362_3dr	2362	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2362_5dr	2362	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2363_3dr	2363	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2363_5dr	2363	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2364_3dr	2364	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2364_5dr	2364	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2365_3dr	2365	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2365_5dr	2365	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2366_3dr	2366	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	GTI的10C三门分支。	READY
2366_5dr	2366	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	GTI的10A五门分支。	READY
2367_3dr	2367	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	GTI的10C三门分支。	READY
2367_5dr	2367	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	GTI后期提供10A五门分支。	READY
2368_3dr	2368	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2368_5dr	2368	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2369_3dr	2369	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2369_5dr	2369	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2372_3dr	2372	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2372_5dr	2372	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2373_3dr	2373	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2373_5dr	2373	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2374_3dr	2374	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2374_5dr	2374	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2375_3dr	2375	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2375_5dr	2375	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2377_3dr	2377	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2377_5dr	2377	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2378_3dr	2378	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	GTI的3C三门分支。	READY
2378_5dr	2378	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	GTI的3A五门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-10c-10a-3-door-1.3-64hp-46236
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-10c-10a-generation-1247
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-3c-3a-facelift-1989-3-door-generation-8986
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-3c-3a-facelift-1989-generation-1246
```

## 下一步优先处理

1. 闭合 Peugeot 505 Sedan 与 Break；优先判断 Sedan 是否需要按前期、后期保险杠外廓或高度拆组。
2. 闭合 Peugeot 504 Sedan、604 Sedan 和 605；605 需处理跨 1995 年改款的 Ktype 分支。
3. 最后处理 Peugeot 106 I 的 `1C` 三门、`1A` 五门及仅三门的 1.3 Rallye 分支。

推进信号：CONTINUE

[1]: https://www.car.info/en-dk/peugeot/309/309-3-door-1st-generation-244984?utm_source=chatgpt.com "Peugeot 309 3-door 10C 1986 - 1989"
[2]: https://www.auto-data.net/en/peugeot-309-10c-10a-3-door-1.3-64hp-46236 "Peugeot 309 (10C,10A) 3-door 1.3 (64 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 首次闭合 Peugeot 504 Sedan、604 Sedan、505 II 标准 Sedan、505 II V6 Sedan、505 II Break 共 5 个尺寸组。
* Peugeot 505 II 标准 Sedan 的普通汽油与 2.5 GTD Turbo 记录均命中 `4579×1737×1432 mm`；V6 因高度为 `1430 mm` 独立建组。([汽车目录][1])
* 505 II Break 的汽油与柴油车身均命中 `4901×1730×1540 mm`，因此复用同一尺寸组。([汽车目录][2])
* 跨越多个早期外廓状态的其他 505 Ktype 暂未修改，避免在宽度或改款边界未闭合前创建错误派生行。

## 2. 当前批次进度

* READY 输入 Ktype：**77/100**
* PENDING 输入 Ktype：**23/100**
* READY 映射行：**98**
* 已确认尺寸组：**18**
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2435	2435	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2436	2436	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2437	2437	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2438	2438	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH		READY
2445	2445	Sedan	505 II		4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH		READY
2448	2448	Sedan	505 II		4	EU-PEUGEOT-505-II-SEDAN-V6-01	HIGH	V6低车身外廓。	READY
2452	2452	Sedan	505 II		4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH		READY
2454	2454	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH		READY
2455	2455	Wagon	505 II		5	EU-PEUGEOT-505-II-BREAK-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-504-SEDAN-01	4496	1689	1461	Automobile-Catalog 1971 Peugeot 504 Sedan	https://www.automobile-catalog.com/car/1971/2558090/peugeot_504_sedan.html
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430	Automobile-Catalog 1977 Peugeot 604 Ti V6	https://www.automobile-catalog.com/car/1977/2567240/peugeot_604_ti_v6.html
EU-PEUGEOT-505-II-SEDAN-STANDARD-01	4579	1737	1432	Automobile-Catalog 1986 Peugeot 505 GTi catalyst;Automobile-Catalog 1986 Peugeot 505 GTD Turbo	https://www.automobile-catalog.com/car/1986/2571170/peugeot_505_gti_cat.html;https://www.automobile-catalog.com/car/1986/2570885/peugeot_505_gtd_turbo.html
EU-PEUGEOT-505-II-SEDAN-V6-01	4579	1737	1430	Automobile-Catalog 1987 Peugeot 505 V6 Automatic catalyst	https://www.automobile-catalog.com/car/1987/2571155/peugeot_505_v6_automatic_cat.html
EU-PEUGEOT-505-II-BREAK-01	4901	1730	1540	Automobile-Catalog 1986 Peugeot 505 Break GTi;Automobile-Catalog 1988 Peugeot 505 Break GLD	https://www.automobile-catalog.com/car/1986/2570990/peugeot_505_break_gti.html;https://www.automobile-catalog.com/car/1988/2570960/peugeot_505_break_gld.html
```

## 5. 下一步优先处理

1. 闭合剩余 Peugeot 505 Sedan 的 Phase I、Phase II、Turbo/GTI 低车身及跨改款派生边界。
2. 闭合 Ktype `2453`、`2456` 的 505 Break 改款前后尺寸分支。
3. 随后一次性处理 Peugeot 605 和 106 I 的改款、三门及五门分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/2571170/peugeot_505_gti_cat.html?utm_source=chatgpt.com "1986 Peugeot 505 GTi catalyst Specs Review (84.5 kW / 115 PS / 113 hp) (since mid-year 1986 for Europe export)"
[2]: https://www.automobile-catalog.com/car/1986/2570990/peugeot_505_break_gti.html?utm_source=chatgpt.com "1986 Peugeot 505 Break GTi Specs Review (89.5 kW / 122 PS / 120 hp) (since October 1986 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2301-2400_ktype_dimension_mapping_final.tsv
- all_2301-2400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 剩余 23 个 Ktype 已全部闭合。Peugeot 505 按 `551A` Sedan、`551D` Break 以及改款前后真实外廓拆分；Break 长度分别为 4898 mm 和 4901 mm。([汽车目录][1])
* Peugeot 605 的跨期 Ktype 已拆分为 1994 改款前后分支，并区分标准车身、V6 和 SV24 的高度差异。([汽车目录][2])
* Peugeot 106 I 已按 `1C` 三门和 `1A` 五门拆分；Ktype `2466` 的 1.3 高功率版本仅保留三门分支。([汽车目录][3])
* 已完成固定表头、唯一主键、外键闭合、尺寸与来源非空检查，并生成两个指定文件。

## 当前批次进度

* READY 输入 Ktype：**100/100**
* PENDING 输入 Ktype：**0/100**
* READY 映射行：**136**
* 已确认尺寸组：**29**
* `id` 唯一：**通过**
* `DIMENSION_GROUP_ID` 唯一且引用闭合：**通过**
* 孤立尺寸组：**0**
* 缺失三维或来源：**0**

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2350	2350	Wagon	305 I	581D	5	EU-PEUGEOT-305-I-BREAK-01	MEDIUM	305 I Break五门旅行车。	READY
2351	2351	Wagon	305 I	581D	5	EU-PEUGEOT-305-I-BREAK-01	MEDIUM	305 I Break五门旅行车。	READY
2352	2352	Wagon	305 II	581E	5	EU-PEUGEOT-305-II-BREAK-01	MEDIUM	305 II Break五门旅行车。	READY
2353	2353	Wagon	305 II	581E	5	EU-PEUGEOT-305-II-BREAK-01	MEDIUM	305 II Break五门旅行车。	READY
2354_3dr	2354	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2354_5dr	2354	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2355_3dr	2355	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2355_5dr	2355	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2356_3dr	2356	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2356_5dr	2356	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2357_3dr	2357	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2357_5dr	2357	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2358_3dr	2358	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2358_5dr	2358	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2359_3dr	2359	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2359_5dr	2359	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2361_3dr	2361	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2361_5dr	2361	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2362_3dr	2362	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2362_5dr	2362	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2363_3dr	2363	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2363_5dr	2363	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2364_3dr	2364	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2364_5dr	2364	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2365_3dr	2365	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2365_5dr	2365	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2366_3dr	2366	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	GTI的10C三门分支。	READY
2366_5dr	2366	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	GTI的10A五门分支。	READY
2367_3dr	2367	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	GTI的10C三门分支。	READY
2367_5dr	2367	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	GTI后期提供10A五门分支。	READY
2368_3dr	2368	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	10C三门物理分支。	READY
2368_5dr	2368	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	10A五门物理分支。	READY
2369_3dr	2369	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2369_5dr	2369	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2372_3dr	2372	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2372_5dr	2372	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2373_3dr	2373	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2373_5dr	2373	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2374_3dr	2374	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2374_5dr	2374	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2375_3dr	2375	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2375_5dr	2375	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2377_3dr	2377	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	3C三门物理分支。	READY
2377_5dr	2377	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	3A五门物理分支。	READY
2378_3dr	2378	Hatchback	309 II	3C	3	EU-PEUGEOT-309-II-HATCHBACK-3D-01	MEDIUM	GTI的3C三门分支。	READY
2378_5dr	2378	Hatchback	309 II	3A	5	EU-PEUGEOT-309-II-HATCHBACK-5D-01	MEDIUM	GTI的3A五门分支。	READY
2379	2379	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2380	2380	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2381	2381	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2382	2382	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2384	2384	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2385	2385	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2386	2386	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2388	2388	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2390	2390	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2391	2391	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2392	2392	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2393	2393	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2394	2394	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2395	2395	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2396	2396	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2397	2397	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2398	2398	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2399	2399	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2400	2400	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2401	2401	Sedan	405 I	15B	4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
2403	2403	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-01	HIGH		READY
2407	2407	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2408	2408	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-STANDARD-01	HIGH		READY
2409	2409	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-MI16-01	HIGH	Mi-16宽体外廓。	READY
2410	2410	Sedan	405 II	4B	4	EU-PEUGEOT-405-II-SEDAN-T16-01	HIGH	T16低车身外廓。	READY
2411	2411	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2412	2412	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2413	2413	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2414	2414	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2416	2416	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2417	2417	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2418	2418	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2420	2420	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2422	2422	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2423	2423	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2424	2424	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2425	2425	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2426	2426	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2427	2427	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2428	2428	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2429	2429	Wagon	405 I	15E	5	EU-PEUGEOT-405-I-BREAK-01	HIGH		READY
2433	2433	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2434	2434	Wagon	405 II	4E	5	EU-PEUGEOT-405-II-BREAK-01	HIGH		READY
2435	2435	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2436	2436	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2437	2437	Sedan	504		4	EU-PEUGEOT-504-SEDAN-01	HIGH		READY
2438	2438	Sedan	604		4	EU-PEUGEOT-604-SEDAN-01	HIGH		READY
2439	2439	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	改款前标准四门外廓。	READY
2440	2440	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	改款前标准四门外廓。	READY
2441	2441	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	改款前标准四门外廓。	READY
2442	2442	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH		READY
2443_prefl	2443	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	跨改款Ktype的改款前分支。	READY
2443_facelift	2443	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	跨改款Ktype的改款后分支。	READY
2444_prefl	2444	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-TURBO-01	MEDIUM	Turbo Injection改款前低车身分支。	READY
2444_facelift	2444	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-V6-01	MEDIUM	Turbo Injection改款后低车身分支。	READY
2445	2445	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH		READY
2446	2446	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	改款前标准四门外廓。	READY
2447_prefl	2447	Sedan	505 I	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	GTI改款前分支；三维与后期标准低车身组一致。	READY
2447_facelift	2447	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	GTI改款后分支。	READY
2448	2448	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-V6-01	HIGH	V6低车身外廓。	READY
2449	2449	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	改款前标准四门外廓。	READY
2450_prefl	2450	Sedan	505 I	551A	4	EU-PEUGEOT-505-I-SEDAN-STANDARD-01	MEDIUM	跨改款柴油Ktype的改款前分支。	READY
2450_facelift	2450	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	跨改款柴油Ktype的改款后分支。	READY
2451_prefl	2451	Sedan	505 I	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	Turbo Diesel改款前分支；三维命中标准低车身组。	READY
2451_facelift	2451	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	MEDIUM	Turbo Diesel改款后分支。	READY
2452	2452	Sedan	505 II	551A	4	EU-PEUGEOT-505-II-SEDAN-STANDARD-01	HIGH		READY
2453	2453	Wagon	505 I	551D	5	EU-PEUGEOT-505-I-BREAK-01	MEDIUM	改款前五门旅行车。	READY
2454	2454	Wagon	505 II	551D	5	EU-PEUGEOT-505-II-BREAK-01	HIGH		READY
2455	2455	Wagon	505 II	551D	5	EU-PEUGEOT-505-II-BREAK-01	HIGH		READY
2456_prefl	2456	Wagon	505 I	551D	5	EU-PEUGEOT-505-I-BREAK-01	MEDIUM	跨改款Ktype的改款前Break分支。	READY
2456_facelift	2456	Wagon	505 II	551D	5	EU-PEUGEOT-505-II-BREAK-01	MEDIUM	跨改款Ktype的改款后Break分支。	READY
2457_prefl	2457	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-STANDARD-01	HIGH	1994改款前外廓。	READY
2457_facelift	2457	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	1994改款后加长外廓。	READY
2458_prefl	2458	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-STANDARD-01	HIGH	1994改款前外廓。	READY
2458_facelift	2458	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	1994改款后加长外廓。	READY
2459_prefl	2459	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-STANDARD-01	HIGH	1994改款前外廓。	READY
2459_facelift	2459	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	HIGH	1994改款后加长外廓。	READY
2460_prefl	2460	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-V6-01	HIGH	3.0 V6改款前外廓。	READY
2460_facelift	2460	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	HIGH	3.0 V6改款后加长外廓。	READY
2461_prefl	2461	Sedan	605 I	6B	4	EU-PEUGEOT-605-I-SEDAN-SV24-01	HIGH	SV24改款前低车身外廓。	READY
2461_facelift	2461	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-SV24-01	HIGH	SV24改款后加长外廓。	READY
2463_3dr	2463	Hatchback	106 I	1C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	HIGH	1C三门物理分支。	READY
2463_5dr	2463	Hatchback	106 I	1A	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	HIGH	1A五门物理分支。	READY
2464_3dr	2464	Hatchback	106 I	1C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	HIGH	1C三门物理分支。	READY
2464_5dr	2464	Hatchback	106 I	1A	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	HIGH	1A五门物理分支。	READY
2465_3dr	2465	Hatchback	106 I	1C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	HIGH	1C三门物理分支。	READY
2465_5dr	2465	Hatchback	106 I	1A	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	HIGH	1A五门物理分支。	READY
2466	2466	Hatchback	106 I	1C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	HIGH	1.3高功率版本仅保留三门分支。	READY
2467_3dr	2467	Hatchback	106 I	1C	3	EU-PEUGEOT-106-I-HATCHBACK-3D-01	HIGH	1C三门物理分支。	READY
2467_5dr	2467	Hatchback	106 I	1A	5	EU-PEUGEOT-106-I-HATCHBACK-5D-01	HIGH	1A五门物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2301-2400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-305-I-BREAK-01	4259	1640	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/2568110/peugeot_305_break_gl.html
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/2568290/peugeot_305_break_gl.html
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-10c-10a-3-door-1.3-64hp-46236
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-10c-10a-generation-1247
EU-PEUGEOT-309-II-HATCHBACK-3D-01	4051	1630	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-3c-3a-facelift-1989-3-door-generation-8986
EU-PEUGEOT-309-II-HATCHBACK-5D-01	4050	1630	1380	Auto-Data	https://www.auto-data.net/en/peugeot-309-3c-3a-facelift-1989-generation-1246
EU-PEUGEOT-405-I-SEDAN-01	4408	1716	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/2584700/peugeot_405_ge_1_6.html
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585285/peugeot_405_sri_2_0_x4.html
EU-MAZDA-CX-7-ER-SUV-01	4682	1872	1645	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1691735/mazda_cx-7_i_sport.html
EU-PEUGEOT-405-II-SEDAN-MI16-01	4408	1716	1406	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585360/peugeot_405_mi_16.html
EU-PEUGEOT-405-II-SEDAN-T16-01	4408	1716	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2585705/peugeot_405_t_16.html
EU-PEUGEOT-405-I-BREAK-01	4398	1716	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/2584820/peugeot_405_break_sri_1_9.html
EU-PEUGEOT-405-II-BREAK-01	4398	1704	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2587430/peugeot_405_break_hunter_1_9_dt.html
EU-PEUGEOT-504-SEDAN-01	4496	1689	1461	Automobile-Catalog 1971 Peugeot 504 Sedan	https://www.automobile-catalog.com/car/1971/2558090/peugeot_504_sedan.html
EU-PEUGEOT-604-SEDAN-01	4720	1770	1430	Automobile-Catalog 1977 Peugeot 604 Ti V6	https://www.automobile-catalog.com/car/1977/2567240/peugeot_604_ti_v6.html
EU-PEUGEOT-505-I-SEDAN-STANDARD-01	4579	1720	1450	Automobile-Catalog 1981 Peugeot 505 GR	https://www.automobile-catalog.com/car/1981/27020/peugeot_505_gr.html
EU-PEUGEOT-505-II-SEDAN-STANDARD-01	4579	1737	1432	Automobile-Catalog 1986 Peugeot 505 GTi catalyst;Automobile-Catalog 1987 Peugeot 505 SRD Turbo	https://www.automobile-catalog.com/car/1986/2571170/peugeot_505_gti_cat.html;https://www.automobile-catalog.com/car/1987/2570840/peugeot_505_srd_turbo.html
EU-PEUGEOT-505-I-SEDAN-TURBO-01	4579	1737	1424	Automobile-Catalog 1985 Peugeot 505 Turbo Injection	https://www.automobile-catalog.com/car/1985/2570405/peugeot_505_turbo_injection.html
EU-PEUGEOT-505-II-SEDAN-V6-01	4579	1737	1430	Automobile-Catalog 1987 Peugeot 505 V6 Automatic catalyst;Automobile-Catalog 1987 Peugeot 505 Turbo Injection	https://www.automobile-catalog.com/car/1987/2571155/peugeot_505_v6_automatic_cat.html;https://www.automobile-catalog.com/car/1987/57440/peugeot_505_turbo_injection.html
EU-PEUGEOT-505-I-BREAK-01	4898	1730	1540	Automobile-Catalog 1983 Peugeot 505 Break GRD	https://www.automobile-catalog.com/car/1983/2569805/peugeot_505_break_grd.html
EU-PEUGEOT-505-II-BREAK-01	4901	1730	1540	Automobile-Catalog 1986 Peugeot 505 Break GTi;Automobile-Catalog 1988 Peugeot 505 Break GLD	https://www.automobile-catalog.com/car/1986/2570990/peugeot_505_break_gti.html;https://www.automobile-catalog.com/car/1988/2570960/peugeot_505_break_gld.html
EU-PEUGEOT-605-I-SEDAN-STANDARD-01	4723	1799	1417	Automobile-Catalog 1990 Peugeot 605 SRi	https://www.automobile-catalog.com/car/1990/2587475/peugeot_605_sri.html
EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	4765	1799	1417	Auto-Data Peugeot 605 2.0 121 Hp	https://www.auto-data.net/en/peugeot-605-6b-2.0-121hp-5325
EU-PEUGEOT-605-I-SEDAN-V6-01	4723	1799	1415	Automobile-Catalog 1990 Peugeot 605 SV 3.0 automatic	https://www.automobile-catalog.com/car/1990/2587550/peugeot_605_sv_3_0_automatic.html
EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	4765	1799	1415	Auto-Data Peugeot 605 3.0 167 Hp	https://www.auto-data.net/en/peugeot-605-6b-3.0-167hp-5332
EU-PEUGEOT-605-I-SEDAN-SV24-01	4723	1799	1411	Automobile-Catalog 1990 Peugeot 605 SV 24	https://www.automobile-catalog.com/car/1990/2587565/peugeot_605_sv_24.html
EU-PEUGEOT-605-I-FACELIFT-SEDAN-SV24-01	4765	1799	1411	Automobile-Catalog 1995 Peugeot 605 SV 24	https://www.automobile-catalog.com/car/1995/2587940/peugeot_605_sv_24.html
EU-PEUGEOT-106-I-HATCHBACK-3D-01	3564	1590	1369	Automobile-Catalog 1994 Peugeot 106 1.0i XR	https://www.automobile-catalog.com/car/1994/2608265/peugeot_106_1_0i_xr.html
EU-PEUGEOT-106-I-HATCHBACK-5D-01	3564	1590	1369	Automobile-Catalog 1994 Peugeot 106 1.1i XN	https://www.automobile-catalog.com/car/1994/2608280/peugeot_106_1_1i_xn.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2301-2400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1981/27020/peugeot_505_gr.html?utm_source=chatgpt.com "1981 Peugeot 505 GR Specs Review (70.6 kW / 96 PS ..."
[2]: https://www.automobile-catalog.com/car/1990/2587475/peugeot_605_sri.html?utm_source=chatgpt.com "1990 Peugeot 605 SRi (man. 5) (model for Europe ) car ..."
[3]: https://www.automobile-catalog.com/car/1994/2608265/peugeot_106_1_0i_xr.html?utm_source=chatgpt.com "1994 Peugeot 106 1.0i XR (man. 5) (model for Europe ) car ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2301-2400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2301-2400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2884 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（718 行）
