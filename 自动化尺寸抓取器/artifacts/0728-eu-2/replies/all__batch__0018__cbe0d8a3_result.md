# 任务：all 第 1701-1800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0018__cbe0d8a3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1701-1800 行

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
all 第 1701-1800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Laguna iii	2.0 16V	Schrägheck	Frontantrieb	Benzin	103	140	Oct 2007	Dec 2012	2024-03-01	23369
Renault	Laguna iii	2.0 16V Turbo	Schrägheck	Frontantrieb	Benzin	125	170	Oct 2007	Dec 2015	2024-03-01	23370
Renault	Laguna iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	81	110	Oct 2007	Dec 2015	2024-03-01	23371
Renault	Laguna iii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	96	131	Oct 2007	Dec 2015	2024-03-01	23372
Renault	Laguna iii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Oct 2007	Dec 2015	2024-03-01	23373
Renault	Laguna iii grandtour	2.0 16V	Kombi	Frontantrieb	Benzin	103	140	Oct 2007	Dec 2015	2024-03-01	23374
Renault	Laguna iii grandtour	2.0 16V Turbo	Kombi	Frontantrieb	Benzin	125	170	Oct 2007	Dec 2015	2024-03-01	23375
Renault	Laguna iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	81	110	Oct 2007	Dec 2015	2024-03-01	23376
Renault	Laguna iii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	96	131	Oct 2007	Dec 2015	2024-03-01	23377
Renault	Laguna iii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	110	150	Oct 2007	Dec 2015	2024-03-01	23378
Peugeot	308 i	1.4 16V	Schrägheck	Frontantrieb	Benzin	70	95	Sep 2007	Oct 2014	2024-03-01	23379
Peugeot	308 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	88	120	Sep 2007	Oct 2014	2024-03-01	23380
Peugeot	308 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2007	Oct 2014	2024-03-01	23381
Peugeot	308 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	66	90	Sep 2007	Oct 2014	2024-03-01	23382
Peugeot	308 i	1.6 HDI	Schrägheck	Frontantrieb	Diesel	80	109	Sep 2007	Oct 2014	2024-03-01	23383
Peugeot	308 i	2.0 HDI	Schrägheck	Frontantrieb	Diesel	100	136	Sep 2007	Oct 2014	2024-03-01	23384
Peugeot	207 sw	1.4	Kombi	Frontantrieb	Benzin	54	73	Jun 2007	Dec 2012	2024-03-01	23385
Peugeot	207 sw	1.4 16V	Kombi	Frontantrieb	Benzin	70	95	Jun 2007	Oct 2013	2024-03-01	23386
Peugeot	207 sw	1.6 16V	Kombi	Frontantrieb	Benzin	88	120	Jun 2007	Oct 2013	2024-03-01	23387
Peugeot	207 sw	1.6 HDI	Kombi	Frontantrieb	Diesel	66	90	Jun 2007	Dec 2012	2024-03-01	23388
Peugeot	207 sw	1.6 HDI	Kombi	Frontantrieb	Diesel	80	109	Jun 2007	Dec 2012	2024-03-01	23389
Mazda	Cx-7	2.3 MZR Disi Turbo AWD	SUV	Allrad	Benzin	190	258	Oct 2007	Aug 2009	2024-03-01	23395
Mazda	2	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Oct 2007	Jun 2015	2024-03-01	23396
Mazda	2	1.5	Schrägheck	Frontantrieb	Benzin	76	103	Jul 2007	Jun 2015	2024-03-01	23397
Mazda	2	1.3	Schrägheck	Frontantrieb	Benzin	63	86	Oct 2007	Jun 2015	2024-03-01	23398
Mercedes-benz	C-Klasse	C 180 Kompressor	Kombi	Heckantrieb	Benzin	115	156	Aug 2007	Aug 2014	2024-03-01	23399
Mercedes-benz	C-Klasse	C 200 Kompressor	Kombi	Heckantrieb	Benzin	135	184	Aug 2007	Aug 2014	2024-03-01	23400
Mercedes-benz	C-Klasse	C 230	Kombi	Heckantrieb	Benzin	150	204	Aug 2007	Aug 2014	2024-03-01	23401
Mercedes-benz	C-Klasse	C 280	Kombi	Heckantrieb	Benzin	170	231	Aug 2007	Aug 2014	2024-03-01	23402
Mercedes-benz	C-Klasse	C 350	Kombi	Heckantrieb	Benzin	200	272	Aug 2007	Aug 2014	2024-03-01	23403
Mercedes-benz	C-Klasse	C 200 CDI	Kombi	Heckantrieb	Diesel	100	136	Aug 2007	Dec 2009	2024-03-01	23404
VW	Golf ii	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	100	136	Aug 1986	Jul 1988	2024-03-01	23406
Mercedes-benz	C-Klasse	C 220 CDI	Kombi	Heckantrieb	Diesel	125	170	Aug 2007	Nov 2008	2024-03-01	23408
Land Rover	Range rover i	2.4 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	78	106	Oct 1985	Sep 1989	2024-03-01	23411
Opel	Agila b	1	Schrägheck	Frontantrieb	Benzin	48	65	Apr 2008	Jun 2011	2025-06-01	23425
Opel	Agila b	1.2	Schrägheck	Frontantrieb	Benzin	63	86	Apr 2008	Oct 2012	2025-06-01	23426
Opel	Agila b	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	55	75	Apr 2008	Apr 2010	2025-06-01	23427
Jaguar	X-Type i	2.1 V6	Kombi	Frontantrieb	Benzin	115	156	Nov 2003	Mar 2009	2024-03-01	23428
BMW	1	135 I	Coupe	Heckantrieb	Benzin	225	306	Oct 2007	Oct 2013	2024-03-01	23429
BMW	1	120 D	Coupe	Heckantrieb	Diesel	130	177	Sep 2007	Oct 2013	2024-03-01	23430
BMW	1	123 D	Coupe	Heckantrieb	Diesel	150	204	Oct 2007	Sep 2013	2024-03-01	23431
BMW	1	123 D	Schrägheck	Heckantrieb	Diesel	150	204	Mar 2007	Dec 2011	2024-03-01	23432
Hyundai	I30	1.4	Schrägheck	Frontantrieb	Benzin	80	109	Oct 2007	Nov 2011	2024-03-01	23433
Hyundai	I30	1.6	Schrägheck	Frontantrieb	Benzin	90	122	Oct 2007	Nov 2011	2024-03-01	23434
Hyundai	I30	2	Schrägheck	Frontantrieb	Benzin	105	143	Oct 2007	Nov 2011	2024-03-01	23435
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	85	116	Oct 2007	Nov 2011	2024-03-01	23436
Hyundai	I30	2.0 Crdi	Schrägheck	Frontantrieb	Diesel	103	140	Oct 2007	Nov 2011	2024-03-01	23437
Opel	Omega b	2.2 DTI 16V	Stufenheck	Heckantrieb	Diesel	81	110	Sep 2000	Jul 2003	2024-03-01	23438
Opel	Omega b caravan	2.2 DTI 16V	Kombi	Heckantrieb	Diesel	81	110	Sep 2000	Jul 2003	2024-03-01	23439
Citroën	C5	2.0 HDI	Schrägheck	Frontantrieb	Diesel	79	107	Mar 2001	Aug 2004	2024-07-01	23440
Citroën	C5	2.0 HDI	Kombi	Frontantrieb	Diesel	80	109	Jun 2001	Aug 2004	2024-07-01	23441
Chrysler	Grand voyager v	3.3	Großraumlimousine	Frontantrieb	Benzin	125	170	Jan 2008	-	2024-03-01	23442
Suzuki	Swift iii	1.6	Schrägheck	Frontantrieb	Benzin	92	125	May 2006	Dec 2015	2026-05-01	23443
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	120	163	Oct 2007	Jun 2014	2024-03-01	23444
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	128	174	Aug 2007	Jul 2010	2024-03-01	23445
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	88	120	Oct 2007	Dec 2013	2024-03-01	23446
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	80	109	Oct 2007	Feb 2010	2024-03-01	23447
Lincoln	Ls	3.9 V8 32V	Stufenheck	Heckantrieb	Benzin	180	245	May 1998	-	2024-03-01	23448
Dacia	Solenza	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Feb 2003	Oct 2005	2024-03-01	23449
Dacia	Solenza	1.9 D	Schrägheck	Frontantrieb	Diesel	46	63	Feb 2003	-	2024-03-01	23450
Renault	Clio iii grandtour	1.2 16V	Kombi	Frontantrieb	Benzin	55	75	Feb 2008	Dec 2014	2026-05-01	23451
Renault	Clio iii grandtour	1.2 16V	Kombi	Frontantrieb	Benzin	58	78	Nov 2007	Dec 2014	2026-05-01	23452
Renault	Clio iii grandtour	1.2 16V	Kombi	Frontantrieb	Benzin	74	101	Nov 2007	Dec 2012	2026-05-01	23453
Renault	Clio iii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	82	112	Nov 2007	Dec 2012	2026-05-01	23454
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	50	68	Nov 2007	Dec 2012	2026-05-01	23455
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	63	86	Nov 2007	Dec 2012	2026-05-01	23456
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	76	103	Nov 2007	Dec 2012	2026-05-01	23457
Renault	Clio iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	78	106	Feb 2008	Dec 2012	2026-05-01	23458
Mercedes-benz	C-Klasse	C 320 CDI	Kombi	Heckantrieb	Diesel	165	224	Aug 2007	Aug 2014	2024-03-01	23459
Renault	Kangoo	1.6	Großraumlimousine	Frontantrieb	Benzin	64	87	Feb 2008	-	2024-03-01	23460
Mercedes-benz	C-Klasse	C 320 CDI 4-matic	Kombi	Allrad	Diesel	165	224	Aug 2007	Dec 2011	2024-03-01	23461
Renault	Kangoo	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	78	106	Feb 2008	-	2024-03-01	23462
Ferrari	F430	430 Scuderia	Coupe	Heckantrieb	Benzin	375	510	Sep 2007	Dec 2009	2024-03-01	23463
Renault	Kangoo	1.5 DCI 70	Großraumlimousine	Frontantrieb	Diesel	50	68	Feb 2008	-	2024-03-01	23464
Renault	Kangoo	1.5 DCI 85	Großraumlimousine	Frontantrieb	Diesel	63	86	Feb 2008	-	2024-03-01	23465
Renault	Kangoo	1.5 DCI 105	Großraumlimousine	Frontantrieb	Diesel	76	103	Feb 2008	-	2024-03-01	23466
Nissan	Tiida	1.6	Schrägheck	Frontantrieb	Benzin	81	110	Sep 2007	Dec 2011	2024-03-01	23467
Nissan	Tiida	1.8	Schrägheck	Frontantrieb	Benzin	93	126	Sep 2004	Dec 2011	2024-03-01	23468
Nissan	Tiida	1.5 DCI	Schrägheck	Frontantrieb	Diesel	78	106	Sep 2007	Dec 2011	2024-03-01	23469
KIA	Pro cee'd	1.4	Schrägheck	Frontantrieb	Benzin	80	109	Feb 2008	Sep 2012	2024-03-01	23470
KIA	Pro cee'd	1.6	Schrägheck	Frontantrieb	Benzin	90	122	Feb 2008	Sep 2012	2024-03-01	23471
KIA	Pro cee'd	2	Schrägheck	Frontantrieb	Benzin	105	143	Feb 2008	Sep 2012	2024-03-01	23472
Mercedes-benz	E-Klasse	E 350 CGI	Stufenheck	Heckantrieb	Benzin	215	292	Sep 2007	Dec 2008	2024-03-01	23473
KIA	Pro cee'd	1.6 Crdi 90	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2008	Sep 2012	2024-03-01	23474
KIA	Pro cee'd	1.6 Crdi 115	Schrägheck	Frontantrieb	Diesel	85	115	Feb 2008	Sep 2012	2024-03-01	23475
KIA	Pro cee'd	2.0 Crdi 140	Schrägheck	Frontantrieb	Diesel	103	140	Feb 2008	Sep 2012	2024-03-01	23476
Mercedes-benz	E-Klasse	E 300 Bluetec	Stufenheck	Heckantrieb	Diesel	155	211	Sep 2007	Dec 2008	2024-03-01	23477
Santana	Ps10/anibal	2.8 D 4X4	Geländewagen geschlossen	Allrad	Diesel	78	106	Mar 2003	-	2024-03-01	23478
Santana	Ps10/anibal	2.8 TD	Geländewagen geschlossen	Heckantrieb	Diesel	92	125	Dec 2002	-	2024-03-01	23479
Santana	Ps10/anibal	2.8 D 4X4	Geländewagen geschlossen	Allrad	Diesel	92	125	Mar 2003	-	2024-03-01	23480
VW	Touareg	5.0 R50 TDI	SUV	Allrad	Diesel	257	350	Aug 2007	May 2010	2024-03-01	23481
Jaguar	Xk ii	3.6	Coupe	Heckantrieb	Benzin	190	258	Jul 2007	Jul 2014	2024-03-01	23482
Chevrolet	Hhr	2.4	Kombi	Frontantrieb	Benzin	125	170	Oct 2007	Dec 2011	2024-03-01	23483
Abarth	Grande punto	1.4	Schrägheck	Frontantrieb	Benzin	114	155	Jul 2007	Jun 2010	2024-03-01	23484
Renault	Twingo	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Mar 2007	Sep 2014	2026-05-01	23485
Renault	Twingo	1.2 16V	Schrägheck	Frontantrieb	Benzin	56	76	Mar 2007	Oct 2010	2026-05-01	23486
Renault	Twingo	1.5 DCI	Schrägheck	Frontantrieb	Diesel	47	64	Mar 2007	Sep 2014	2026-05-01	23487
Nissan	Tiida	1.6	Stufenheck	Frontantrieb	Benzin	81	110	Sep 2007	Dec 2012	2024-03-01	23488
Nissan	Tiida	1.8	Stufenheck	Frontantrieb	Benzin	93	126	Sep 2007	Dec 2012	2024-03-01	23489
Nissan	Tiida	1.5 DCI	Stufenheck	Frontantrieb	Diesel	78	106	Sep 2007	Dec 2012	2024-03-01	23490


--- Round 1 / checkpoint 续跑 ---
## 更新点

* 首轮按物理车身聚类，已闭合 **11 个 DIMENSION_GROUP**，批量关联 **50 个 Ktype**，未对同组发动机版本重复抓取。
* 已处理 Laguna III 两种车身、308 I、CX-7 ER、C-Class S204、Agila B、i30 FD、Clio III Grandtour、F430 Scuderia、Pro cee'd ED、Abarth Grande Punto 199。尺寸均采用明确的不含后视镜宽度口径。([汽车目录][1])
* Peugeot 207 SW 暂不建组：当前来源分别给出 **1510 mm** 和 **1527 mm** 高度，存在车顶纵杆或测量口径差异，不能直接选取其中一个。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：50
* READY 映射：50
* PENDING 输入 Ktype：50
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23369	23369	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23370	23370	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23371	23371	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23372	23372	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23373	23373	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23374	23374	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23375	23375	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23376	23376	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23377	23377	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23378	23378	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23379	23379	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23380	23380	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23381	23381	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23382	23382	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23383	23383	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23384	23384	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23395	23395	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-5D-01	HIGH	欧洲版前期ER车身。	READY
23399	23399	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23400	23400	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23401	23401	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23402	23402	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23403	23403	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23404	23404	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23408	23408	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23425	23425	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23426	23426	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23427	23427	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23433	23433	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23434	23434	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23435	23435	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23436	23436	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23437	23437	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23451	23451	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23452	23452	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23453	23453	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23454	23454	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23455	23455	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23456	23456	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23457	23457	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23458	23458	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23459	23459	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23461	23461	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23463	23463	Coupe	F430	F131	2	EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	HIGH	Scuderia固定外廓。	READY
23470	23470	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23471	23471	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23472	23472	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23474	23474	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23475	23475	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23476	23476	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23484	23484	Hatchback	Grande Punto	199	3	EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	Abarth专用前后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2957810/renault_laguna_2_0_16v.html
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/2958500/renault_laguna_wagon_grandtour_gt_2_0_dci_180.html
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2621750/peugeot_308_1_4_vti_95.html
EU-MAZDA-CX-7-ER-SUV-5D-01	4680	1870	1645	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1691615/mazda_cx-7.html
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	4596	1770	1459	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1550255/mercedes-benz_c_180_kompressor_t-modell_automatic.html
EU-OPEL-AGILA-B-HATCHBACK-5D-01	3740	1680	1590	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2529530/opel_agila_1_3_cdti_ecoflex.html
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1181255/hyundai_i30_1_4_comfort.html
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2952125/renault_clio_wagon_grandtour_1_2_16v_75.html
EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	4512	1923	1199	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/707420/ferrari_430_scuderia.html
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	4250	1790	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1359965/kia_pro_cee_d_1_6_cvvt_ex_automatic.html
EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	4041	1721	1490	Auto-Data	https://www.auto-data.net/en/abarth-grande-punto-199-1.4-t-jet-155hp-46793
```

## 下一步优先处理

1. 优先闭合可批量复用的 Mazda2 DE、BMW E82/E81、Nissan Tiida C11 两种车身、Renault Kangoo II。
2. 处理 Jaguar X-Type Estate、Opel Omega B、Citroën C5 I、Mini Clubman R55 的改款或配置边界。
3. 单独解决 Peugeot 207 SW 高度口径冲突，以及 Range Rover I、Santana PS10 等门数或车身长度分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/2957810/renault_laguna_2_0_16v.html?utm_source=chatgpt.com "2008 Renault Laguna 2.0 16V Specs Review (103 kW ..."
[2]: https://www.automobile-catalog.com/car/2008/2620520/peugeot_207_sw_1_4_vti_95.html?utm_source=chatgpt.com "2008 Peugeot 207 SW 1.4 VTi 95 Specs Review (70 kW ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / checkpoint 续跑 ---
## 更新点

* 新闭合 BMW 1 Series E82 Coupe、E81 三门 Hatchback、Renault Kangoo II、Nissan Tiida C11 两种车身及 Renault Twingo II，共关联 19 个 Ktype。([汽车数据][1])
* MINI Clubman R55 未强行合并：Cooper S、Cooper 和 Cooper D 的保险杠外廓长度分别为 3958、3937、3945 mm，建立三个独立尺寸组。([汽车目录][2])
* Mazda 2 DE 已确认改款前后长度分别为 3900 和 3920 mm，但三个 Ktype 的具体改款分支覆盖仍需闭合，本轮不创建猜测性映射。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：72
* READY 映射：72
* PENDING 输入 Ktype：28
* 已确认尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23429	23429	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23430	23430	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23431	23431	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23432	23432	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	三门车身。	READY
23444	23444	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	HIGH	Cooper S外廓分支。	READY
23445	23445	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	HIGH	Cooper S外廓分支。	READY
23446	23446	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-01	HIGH	Cooper标准外廓分支。	READY
23447	23447	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-D-01	HIGH	Cooper D外廓分支。	READY
23460	23460	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23462	23462	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23464	23464	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23465	23465	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23466	23466	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23467	23467	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23468	23468	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23469	23469	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23485	23485	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23486	23486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23487	23487	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23488	23488	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
23489	23489	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
23490	23490	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423	Auto-Data	https://www.auto-data.net/en/bmw-1-series-coupe-e82-120d-177hp-9835
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data	https://www.auto-data.net/en/bmw-1-series-hatchback-3dr-e81-123d-204hp-9820
EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	3958	1683	1432	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753235/mini_cooper_s_clubman.html
EU-MINI-CLUBMAN-R55-WAGON-COOPER-01	3937	1683	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753175/mini_cooper_clubman.html
EU-MINI-CLUBMAN-R55-WAGON-COOPER-D-01	3945	1683	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753205/mini_cooper_d_clubman.html
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data	https://www.auto-data.net/en/renault-kangoo-ii-1.6-16v-106hp-33902
EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	4302	1695	1533	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2291510/nissan_tiida_hatchback_1_6.html
EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	3600	1654	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2955980/renault_twingo_1_2_60.html
EU-NISSAN-TIIDA-C11-SEDAN-4D-01	4478	1695	1543	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2291450/nissan_tiida_sedan_1_6.html
```

## 下一步优先处理

1. 批量闭合 Jaguar X-Type Estate、Opel Omega B Sedan/Caravan、Citroën C5 I Liftback/Wagon 和 Chrysler Grand Voyager V。
2. 处理 Golf II、Suzuki Swift III、Lincoln LS、Dacia Solenza、Mercedes W211、Touareg R50、Jaguar XK II 和 Chevrolet HHR。
3. 最后集中解决 Mazda 2 改款分支、Peugeot 207 SW 高度口径、Range Rover I 车身边界及 Santana PS10 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-1-series-coupe-e82-120d-177hp-9835 "BMW 1 Series Coupe (E82) 120d (177 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2007/1753235/mini_cooper_s_clubman.html?utm_source=chatgpt.com "2007 Mini Cooper S Clubman Specs Review (128.5 kW / 175 PS / 172 hp) (since August 2007 for Europe Japan )"
[3]: https://www.automobile-catalog.com/make/mazda/2_2gen/2_2_1_hatch/2007.html?utm_source=chatgpt.com "2007 Mazda 2 2gen/I Hatch (DE) full range specs"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / checkpoint 续跑 ---
## 更新点

* Peugeot 207 SW 的高度口径已闭合为 1527 mm，页面同时区分车身宽度、折叠后视镜宽度和含后视镜宽度，因此 `WidthMM=1748` 符合不含后视镜规则。([汽车数据][1])
* Mazda2 DE 的同一批 Ktype 覆盖改款前后两种外廓：改款前长度 3900 mm，2010 改款后长度 3920 mm，因此分别派生 `prefl` 与 `facelift` 映射。([汽车数据][2])
* Range Rover I 2.4 Turbo D 跨越 1986 年外廓更新，尺寸由 4460×1800×1785 mm 变为 4450×1818×1800 mm，已拆成两个物理分支。([汽车目录][3])
* Chrysler Grand Voyager V 按明确的 Grand Voyager 长轴车身落盘；未采用与该长轴车身边界冲突的 5096 mm 聚合记录。([汽车数据][4])
* 已完成固定表头、唯一性、引用闭合、正整数三维、来源完整及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：104
* PENDING 映射：0
* 已确认尺寸组：40
* 唯一 `id`：104
* 唯一 `DIMENSION_GROUP_ID`：40
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23369	23369	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23370	23370	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23371	23371	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23372	23372	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23373	23373	Hatchback	Laguna III		5	EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	HIGH		READY
23374	23374	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23375	23375	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23376	23376	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23377	23377	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23378	23378	Wagon	Laguna III		5	EU-RENAULT-LAGUNA-III-WAGON-5D-01	HIGH		READY
23379	23379	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23380	23380	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23381	23381	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23382	23382	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23383	23383	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23384	23384	Hatchback	308 I	T7	5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH		READY
23385	23385	Wagon	207 I		5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
23386	23386	Wagon	207 I		5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
23387	23387	Wagon	207 I		5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
23388	23388	Wagon	207 I		5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
23389	23389	Wagon	207 I		5	EU-PEUGEOT-207-I-SW-WAGON-5D-01	HIGH		READY
23395	23395	SUV	CX-7 I	ER	5	EU-MAZDA-CX-7-ER-SUV-5D-01	HIGH	欧洲版前期ER车身。	READY
23396_prefl	23396	Hatchback	Mazda2 II	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖2010改款前外廓。	READY
23396_facelift	23396	Hatchback	Mazda2 II facelift	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖2010改款后外廓。	READY
23397_prefl	23397	Hatchback	Mazda2 II	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖2010改款前外廓。	READY
23397_facelift	23397	Hatchback	Mazda2 II facelift	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖2010改款后外廓。	READY
23398_prefl	23398	Hatchback	Mazda2 II	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	MEDIUM	Ktype覆盖2010改款前外廓。	READY
23398_facelift	23398	Hatchback	Mazda2 II facelift	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	MEDIUM	Ktype覆盖2010改款后外廓。	READY
23399	23399	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23400	23400	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23401	23401	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23402	23402	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23403	23403	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23404	23404	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23406	23406	Hatchback	Golf II	19E	3	EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-3D-01	MEDIUM	100kW早期三门GTI 16V外廓。	READY
23408	23408	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23411_prefl	23411	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-PREFL-01	MEDIUM	Ktype覆盖1986年外廓更新前分支。	READY
23411_facelift	23411	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-FACELIFT-01	MEDIUM	Ktype覆盖1986年外廓更新后分支。	READY
23425	23425	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23426	23426	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23427	23427	Hatchback	Agila B		5	EU-OPEL-AGILA-B-HATCHBACK-5D-01	HIGH		READY
23428	23428	Wagon	X-Type I	X400	5	EU-JAGUAR-X-TYPE-X400-WAGON-5D-01	HIGH		READY
23429	23429	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23430	23430	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23431	23431	Coupe	1 Series I	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
23432	23432	Hatchback	1 Series I	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH	三门车身。	READY
23433	23433	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23434	23434	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23435	23435	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23436	23436	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23437	23437	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	HIGH		READY
23438	23438	Sedan	Omega B facelift		4	EU-OPEL-OMEGA-B-FACELIFT-SEDAN-4D-01	HIGH		READY
23439	23439	Wagon	Omega B facelift		5	EU-OPEL-OMEGA-B-FACELIFT-WAGON-5D-01	HIGH		READY
23440	23440	Hatchback	C5 I Phase I		5	EU-CITROEN-C5-I-PHASE-I-HATCHBACK-5D-01	HIGH	五门掀背式车身。	READY
23441	23441	Wagon	C5 I Phase I		5	EU-CITROEN-C5-I-PHASE-I-WAGON-5D-01	HIGH		READY
23442	23442	MPV	Grand Voyager V	RT	5	EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	MEDIUM	欧洲Grand Voyager长轴车身。	READY
23443	23443	Hatchback	Swift III	MZ	3	EU-SUZUKI-SWIFT-MZ-SPORT-HATCHBACK-3D-01	HIGH		READY
23444	23444	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	HIGH	Cooper S外廓分支。	READY
23445	23445	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	HIGH	Cooper S外廓分支。	READY
23446	23446	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-01	HIGH	Cooper标准外廓分支。	READY
23447	23447	Wagon	Clubman I	R55	3	EU-MINI-CLUBMAN-R55-WAGON-COOPER-D-01	HIGH	Cooper D外廓分支。	READY
23448	23448	Sedan	LS I		4	EU-LINCOLN-LS-I-SEDAN-4D-01	HIGH		READY
23449	23449	Sedan	Solenza		4	EU-DACIA-SOLENZA-SEDAN-4D-01	HIGH	原始BodyStyle为Schrägheck；可靠规格资料确认四门Sedan。	READY
23450	23450	Sedan	Solenza		4	EU-DACIA-SOLENZA-SEDAN-4D-01	HIGH	原始BodyStyle为Schrägheck；可靠规格资料确认四门Sedan。	READY
23451	23451	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23452	23452	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23453	23453	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23454	23454	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23455	23455	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23456	23456	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23457	23457	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23458	23458	Wagon	Clio III		5	EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	HIGH		READY
23459	23459	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23460	23460	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23461	23461	Wagon	C-Class W204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	HIGH		READY
23462	23462	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23463	23463	Coupe	F430	F131	2	EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	HIGH	Scuderia固定外廓。	READY
23464	23464	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23465	23465	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23466	23466	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-MPV-5D-01	HIGH		READY
23467	23467	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23468	23468	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23469	23469	Hatchback	Tiida I	C11	5	EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	HIGH	欧洲出口五门车身。	READY
23470	23470	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23471	23471	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23472	23472	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23473	23473	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	HIGH		READY
23474	23474	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23475	23475	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23476	23476	Hatchback	Pro cee'd I	ED	3	EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	HIGH	三门车身。	READY
23477	23477	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	HIGH		READY
23478	23478	SUV	PS-10/Anibal		5	EU-SANTANA-PS10-ANIBAL-SW-SUV-5D-01	MEDIUM	五门SW车身。	READY
23479	23479	SUV	PS-10/Anibal		5	EU-SANTANA-PS10-ANIBAL-SW-SUV-5D-01	MEDIUM	五门SW车身。	READY
23480	23480	SUV	PS-10/Anibal		5	EU-SANTANA-PS10-ANIBAL-SW-SUV-5D-01	MEDIUM	五门SW车身。	READY
23481	23481	SUV	Touareg I facelift	7L	5	EU-VOLKSWAGEN-TOUAREG-7L-R50-SUV-5D-01	HIGH	R50宽体外廓。	READY
23482	23482	Coupe	XK II	X150	2	EU-JAGUAR-XK-X150-COUPE-2D-01	MEDIUM	输入3.6版本对应欧洲X150同外廓车身。	READY
23483	23483	Wagon	HHR		5	EU-CHEVROLET-HHR-WAGON-5D-01	HIGH		READY
23484	23484	Hatchback	Grande Punto	199	3	EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	Abarth专用前后外廓。	READY
23485	23485	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23486	23486	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23487	23487	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	HIGH	标准非RS车身。	READY
23488	23488	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
23489	23489	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
23490	23490	Sedan	Tiida I	C11	4	EU-NISSAN-TIIDA-C11-SEDAN-4D-01	HIGH	欧洲出口四门车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1701-1800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2957810/renault_laguna_2_0_16v.html
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/2958500/renault_laguna_wagon_grandtour_gt_2_0_dci_180.html
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2621750/peugeot_308_1_4_vti_95.html
EU-PEUGEOT-207-I-SW-WAGON-5D-01	4156	1748	1527	Auto-Data	https://www.auto-data.net/en/peugeot-207-sw-1.4-73hp-34054
EU-MAZDA-CX-7-ER-SUV-5D-01	4680	1870	1645	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1691615/mazda_cx-7.html
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475	Auto-Data	https://www.auto-data.net/en/mazda-2-ii-de-1.3i-75hp-11446
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475	Auto-Data	https://www.auto-data.net/en/mazda-2-ii-de-facelift-2010-1.3i-75hp-17493
EU-MERCEDES-BENZ-C-CLASS-S204-WAGON-5D-01	4596	1770	1459	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1550255/mercedes-benz_c_180_kompressor_t-modell_automatic.html
EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-3D-01	3985	1665	1405	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-ii-3-door-1.8-gti-16v-139hp-8771
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-PREFL-01	4460	1800	1785	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1397615/range_rover_turbo_d.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-FACELIFT-01	4450	1818	1800	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1397675/range_rover_turbo_d.html
EU-OPEL-AGILA-B-HATCHBACK-5D-01	3740	1680	1590	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2529530/opel_agila_1_3_cdti_ecoflex.html
EU-JAGUAR-X-TYPE-X400-WAGON-5D-01	4716	1789	1483	Auto-Data	https://www.auto-data.net/en/jaguar-x-type-estate-2.1-i-v6-156hp-sport-170
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423	Auto-Data	https://www.auto-data.net/en/bmw-1-series-coupe-e82-120d-177hp-9835
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data	https://www.auto-data.net/en/bmw-1-series-hatchback-3dr-e81-123d-204hp-9820
EU-HYUNDAI-I30-FD-HATCHBACK-5D-01	4245	1775	1480	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1181255/hyundai_i30_1_4_comfort.html
EU-OPEL-OMEGA-B-FACELIFT-SEDAN-4D-01	4898	1785	1455	Auto-Data	https://www.auto-data.net/en/opel-omega-b-facelift-1999-generation-5160
EU-OPEL-OMEGA-B-FACELIFT-WAGON-5D-01	4898	1776	1545	Auto-Data	https://www.auto-data.net/en/opel-omega-model-245
EU-CITROEN-C5-I-PHASE-I-HATCHBACK-5D-01	4618	1770	1476	Auto-Data	https://www.auto-data.net/en/citroen-c5-i-phase-i-2000-generation-3346
EU-CITROEN-C5-I-PHASE-I-WAGON-5D-01	4760	1770	1520	Auto-Data	https://www.auto-data.net/en/citroen-c5-i-break-phase-i-2000-generation-3347
EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	5143	1954	1750	Automobile-Catalog	https://www.automobile-catalog.com/make/chrysler/voyager_chrysler_5gen/voyager_chrysler_5gen_grand/2008.html
EU-SUZUKI-SWIFT-MZ-SPORT-HATCHBACK-3D-01	3765	1690	1500	Auto-Data	https://www.auto-data.net/en/suzuki-swift-iv-1.6-i-16v-125hp-sport-16526
EU-MINI-CLUBMAN-R55-WAGON-COOPER-S-01	3958	1683	1432	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753235/mini_cooper_s_clubman.html
EU-MINI-CLUBMAN-R55-WAGON-COOPER-01	3937	1683	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753175/mini_cooper_clubman.html
EU-MINI-CLUBMAN-R55-WAGON-COOPER-D-01	3945	1683	1426	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/1753205/mini_cooper_d_clubman.html
EU-LINCOLN-LS-I-SEDAN-4D-01	4925	1860	1425	Auto-Data	https://www.auto-data.net/en/lincoln-ls-3.9-v8-32v-245hp-8200
EU-DACIA-SOLENZA-SEDAN-4D-01	4080	1664	1379	Auto-Data	https://www.auto-data.net/en/dacia-solenza-1.4-i-75hp-15895
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2952125/renault_clio_wagon_grandtour_1_2_16v_75.html
EU-RENAULT-KANGOO-II-MPV-5D-01	4213	1829	1839	Auto-Data	https://www.auto-data.net/en/renault-kangoo-ii-1.6-16v-106hp-33902
EU-FERRARI-F430-SCUDERIA-COUPE-2D-01	4512	1923	1199	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/707420/ferrari_430_scuderia.html
EU-NISSAN-TIIDA-C11-HATCHBACK-5D-01	4302	1695	1533	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2291510/nissan_tiida_hatchback_1_6.html
EU-KIA-PRO-CEED-ED-HATCHBACK-3D-01	4250	1790	1450	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1359965/kia_pro_cee_d_1_6_cvvt_ex_automatic.html
EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-4D-01	4856	1822	1484	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-350-cgi-292hp-7g-tronic-45851
EU-SANTANA-PS10-ANIBAL-SW-SUV-5D-01	4714	1750	2000	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/santana-ps-10-sw-generation-10884; https://www.automobile-catalog.com/car/2007/3042995/santana_ps-10_sw_anibal_civil_5p.html
EU-VOLKSWAGEN-TOUAREG-7L-R50-SUV-5D-01	4754	1977	1703	Auto-Data	https://www.auto-data.net/fr/volkswagen-touareg-i-7l-facelift-2006-r50-5.0-tdi-v10-350hp-4xmotion-tiptronic-54823
EU-JAGUAR-XK-X150-COUPE-2D-01	4791	1893	1322	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1292915/jaguar_xk_3_5_coupe.html
EU-CHEVROLET-HHR-WAGON-5D-01	4475	1755	1603	Auto-Data	https://www.auto-data.net/en/chevrolet-hhr-2.4-i-16v-175hp-14368
EU-ABARTH-GRANDE-PUNTO-199-HATCHBACK-3D-01	4041	1721	1490	Auto-Data	https://www.auto-data.net/en/abarth-grande-punto-199-1.4-t-jet-155hp-46793
EU-RENAULT-TWINGO-II-HATCHBACK-3D-01	3600	1654	1470	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2955980/renault_twingo_1_2_60.html
EU-NISSAN-TIIDA-C11-SEDAN-4D-01	4478	1695	1543	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/2291450/nissan_tiida_sedan_1_6.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1701-1800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/peugeot-207-sw-1.4-73hp-34054 "https://www.auto-data.net/en/peugeot-207-sw-1.4-73hp-34054"
[2]: https://www.auto-data.net/en/mazda-2-ii-de-1.3i-75hp-11446 "https://www.auto-data.net/en/mazda-2-ii-de-1.3i-75hp-11446"
[3]: https://www.automobile-catalog.com/car/1986/1397615/range_rover_turbo_d.html "https://www.automobile-catalog.com/car/1986/1397615/range_rover_turbo_d.html"
[4]: https://www.auto-data.net/en/chrysler-grand-voyager-v-3.3i-v6-172hp-14765 "https://www.auto-data.net/en/chrysler-grand-voyager-v-3.3i-v6-172hp-14765"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1701-1800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1701-1800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2636 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1378 行）

