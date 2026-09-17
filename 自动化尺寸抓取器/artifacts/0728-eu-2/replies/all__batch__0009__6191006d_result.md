# 任务：all 第 801-900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0009__6191006d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 801-900 行

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
all 第 801-900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Astra h caravan	1.8	Kombi	Frontantrieb	Benzin	103	140	Nov 2005	Oct 2010	2026-05-01	20010
Opel	Vectra c	2.8 V6 Turbo	Stufenheck	Frontantrieb	Benzin	184	250	Aug 2005	Aug 2008	2024-03-01	20011
Opel	Vectra c cc	2.8 V6 Turbo	Schrägheck	Frontantrieb	Benzin	184	250	Aug 2005	Aug 2008	2024-03-01	20012
Opel	Vectra c cc	2.8 V6 Turbo	Schrägheck	Frontantrieb	Benzin	206	280	Aug 2006	Aug 2008	2024-03-01	20013
Mercedes-benz	Slr	5.4 722 Edition	Coupe	Heckantrieb	Benzin	478	650	Oct 2006	-	2024-03-01	20014
Mercedes-benz	S-Klasse	S 63 AMG	Stufenheck	Heckantrieb	Benzin	386	525	Oct 2006	Dec 2013	2024-03-01	20015
Mercedes-benz	S-Klasse	CL 63 AMG	Coupe	Heckantrieb	Benzin	386	525	Oct 2006	Dec 2013	2024-03-01	20016
Mercedes-benz	S-Klasse	CL 65 AMG	Coupe	Heckantrieb	Benzin	450	612	Oct 2006	Dec 2010	2024-03-01	20017
GAZ	Gazelle	2.3	Bus	Heckantrieb	Benzin	96	131	Oct 1993	Aug 2001	2024-03-01	20018
GAZ	Gazelle	2.5 D	Bus	Heckantrieb	Diesel	67	91	Oct 1993	Aug 2001	2024-03-01	20019
GAZ	Gazelle	2.4	Kasten	Heckantrieb	Benzin	66	90	Oct 1993	Aug 2001	2024-03-01	20020
GAZ	Gazelle	2.5 D	Kasten	Heckantrieb	Diesel	67	91	Oct 1993	Aug 2001	2024-03-01	20021
GAZ	Gazelle	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	67	91	Oct 1993	Aug 2001	2024-03-01	20022
GAZ	Gazelle	2.4	Pritsche/Fahrgestell	Heckantrieb	Benzin	66	90	Oct 1993	Aug 2001	2024-03-01	20023
Citroën	Berlingo	1.6 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jul 2005	Dec 2011	2024-03-01	20025
Fiat	Scudo	2.0 JTD	Bus	Frontantrieb	Diesel	69	94	Jan 2004	Dec 2006	2024-03-01	20026
Peugeot	207 cc	1.6 16V	Cabriolet	Frontantrieb	Benzin	88	120	Feb 2007	Oct 2013	2024-03-01	20027
Peugeot	207 cc	1.6 16V Turbo	Cabriolet	Frontantrieb	Benzin	110	150	Feb 2007	Dec 2012	2024-03-01	20028
Lexus	Lfa	4.8	Coupe	Heckantrieb	Benzin	420	571	Nov 2011	Nov 2012	2024-03-01	20029
Peugeot	207 cc	1.6 HDI	Cabriolet	Frontantrieb	Diesel	80	109	Feb 2007	Jan 2015	2024-03-01	20030
VW	Jetta iii	2.0 TDI	Stufenheck	Frontantrieb	Diesel	125	170	Oct 2006	Oct 2010	2024-03-01	20031
Lancia	Ypsilon	1.4	Schrägheck	Frontantrieb	Benzin	57	78	Feb 2006	Dec 2011	2024-03-01	20032
Lancia	Ypsilon	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	55	75	Sep 2006	Dec 2011	2024-03-01	20033
Lancia	Ypsilon	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	66	90	Sep 2006	Dec 2011	2024-03-01	20034
Citroën	Jumpy ii	2.0 I	Bus	Frontantrieb	Benzin	103	140	Jan 2007	Mar 2016	2024-03-01	20035
Citroën	Jumpy ii	1.6 HDI 90 16V	Bus	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20036
Citroën	Jumpy ii	2.0 HDI 120	Bus	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20037
Citroën	Jumpy ii	2.0 HDI 140	Bus	Frontantrieb	Diesel	100	136	Jan 2007	Mar 2016	2024-03-01	20038
Citroën	Jumpy ii	2.0 I	Kasten	Frontantrieb	Benzin	103	140	Jan 2007	Mar 2016	2024-03-01	20039
Citroën	Jumpy ii	1.6 HDI 90 16V	Kasten	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20040
Citroën	Jumpy ii	2.0 HDI 120	Kasten	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20041
Citroën	Jumpy ii	2.0 HDI 140	Kasten	Frontantrieb	Diesel	100	136	Jan 2007	Mar 2016	2024-03-01	20042
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Nov 2005	Mar 2010	2024-03-01	20043
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	147	200	May 2005	Mar 2009	2024-03-01	20048
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	177	240	Nov 2006	May 2011	2024-03-01	20049
Peugeot	Expert	1.6 HDI 90 16V	Bus	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20050
Peugeot	Expert	2.0 HDI 120	Bus	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20051
Peugeot	Expert	2.0 HDI 140	Bus	Frontantrieb	Diesel	100	136	Jan 2007	-	2024-03-01	20052
Seat	Ibiza iii	1.2 12V	Schrägheck	Frontantrieb	Benzin	51	70	May 2006	Nov 2009	2024-03-01	20053
Seat	Cordoba	1.2 12V	Stufenheck	Frontantrieb	Benzin	51	70	May 2006	Nov 2009	2024-03-01	20054
Seat	Cordoba	1.4 16V	Stufenheck	Frontantrieb	Benzin	63	86	May 2006	Nov 2009	2024-03-01	20055
Seat	Cordoba	1.6 16V	Stufenheck	Frontantrieb	Benzin	77	105	Nov 2006	Nov 2009	2024-03-01	20056
Seat	Ibiza iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	77	105	Nov 2006	Nov 2009	2024-03-01	20057
Peugeot	Expert	1.6 HDI 90 16V	Kasten	Frontantrieb	Diesel	66	90	Jan 2007	-	2024-03-01	20058
Peugeot	Expert	2.0 HDI 120	Kasten	Frontantrieb	Diesel	88	120	Jan 2007	-	2024-03-01	20059
Peugeot	Expert	2.0 HDI 140	Kasten	Frontantrieb	Diesel	100	136	Jan 2007	-	2024-03-01	20060
Peugeot	Expert	1.6 HDI 90 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jan 2007	-	2024-03-01	20061
Peugeot	Expert	2.0 HDI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Jan 2007	-	2024-03-01	20062
Peugeot	Expert	2.0 HDI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Jan 2007	-	2024-03-01	20063
VW	Golf v	2.0 GTI	Schrägheck	Frontantrieb	Benzin	169	230	Sep 2006	Dec 2008	2024-03-01	20064
Renault	Kangoo	1.5 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	50	68	Jun 2005	-	2024-03-01	20068
Honda	Legend iv	3.5 V6 4WD	Stufenheck	Allrad	Benzin	217	295	May 2006	Dec 2012	2024-03-01	20069
Mercedes-benz	E-Klasse	E 63 AMG	Stufenheck	Heckantrieb	Benzin	378	514	Mar 2006	Dec 2008	2024-03-01	20070
Mercedes-benz	E-Klasse	E 63 AMG	Kombi	Heckantrieb	Benzin	378	514	Mar 2006	Jul 2009	2024-03-01	20071
Mercedes-benz	G-Klasse	G 320 CDI	Geländewagen geschlossen	Allrad	Diesel	165	224	Sep 2006	Dec 2012	2024-03-01	20072
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	132	180	Jul 2006	Jun 2007	2024-03-01	20073
Mercedes-benz	Vito	109 CDI	Bus	Heckantrieb	Diesel	70	95	Sep 2006	-	2024-03-01	20074
Alfa Romeo	166	2.4 JTD	Stufenheck	Frontantrieb	Diesel	136	185	Jul 2005	Jun 2007	2024-03-01	20075
Fiat	Scudo	1.6 D Multijet	Bus	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20076
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20077
Renault	Clio iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	76	103	Jun 2005	Dec 2012	2026-05-01	20078
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	100	136	Jan 2007	Mar 2016	2024-03-01	20079
Nissan	Micra iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	50	68	Jun 2005	Jun 2010	2024-03-01	20080
Fiat	Scudo	1.6 D Multijet	Kasten	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20081
Nissan	Micra iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	63	86	Jun 2005	Jun 2010	2024-03-01	20082
Fiat	Scudo	2.0 D Multijet	Kasten	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20083
Fiat	Scudo	2.0 D Multijet	Kasten	Frontantrieb	Diesel	100	136	Jan 2007	Mar 2016	2024-03-01	20084
Fiat	Scudo	1.6 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jan 2007	Mar 2016	2024-03-01	20085
Fiat	Scudo	2.0 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Jan 2007	Mar 2016	2024-03-01	20086
Fiat	Scudo	2.0 D Multijet	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Jan 2007	Mar 2016	2024-03-01	20087
Fiat	Idea	1.4	Großraumlimousine	Frontantrieb	Benzin	57	77	Oct 2005	-	2024-03-01	20088
Fiat	Idea	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	66	90	Oct 2005	-	2024-03-01	20089
Volvo	S40 ii	2	Stufenheck	Frontantrieb	Benzin	107	146	Oct 2006	Dec 2012	2024-03-01	20090
Renault	Twizy	45	Schrägheck	Heckantrieb	Elektro	4	5	Apr 2012	-	2024-03-01	20091
Volvo	V50	2	Kombi	Frontantrieb	Benzin	107	146	Oct 2006	Dec 2012	2024-03-01	20092
Toyota	Hilux iv	2.4 D 4WD	Pick-up	Allrad	Diesel	55	75	Aug 1983	Jul 1988	2024-03-01	20093
Nissan	Interstar	DCI 120	Bus	Frontantrieb	Diesel	88	120	Sep 2006	Mar 2011	2024-03-01	20094
Nissan	Interstar	DCI 120	Kasten	Frontantrieb	Diesel	88	120	Sep 2006	-	2024-03-01	20095
Nissan	Interstar	DCI 150	Bus	Frontantrieb	Diesel	107	145	Sep 2006	Mar 2011	2024-03-01	20096
Nissan	Interstar	DCI 150	Kasten	Frontantrieb	Diesel	107	145	Sep 2006	-	2024-03-01	20097
Nissan	Primastar	DCI 150	Bus	Frontantrieb	Diesel	107	145	Sep 2006	-	2024-03-01	20098
Nissan	Primastar	2.5 DCI 150	Kasten	Frontantrieb	Diesel	107	145	Sep 2006	-	2024-03-01	20099
Nissan	Primastar	DCI 120	Bus	Frontantrieb	Diesel	84	114	Sep 2006	-	2024-03-01	20100
Nissan	Primastar	2.0 DCI 115	Kasten	Frontantrieb	Diesel	84	114	Sep 2006	-	2024-03-01	20101
Nissan	Primastar	DCI 90	Bus	Frontantrieb	Diesel	66	90	Sep 2006	-	2024-03-01	20102
Nissan	Primastar	2.0 DCI 90	Kasten	Frontantrieb	Diesel	66	90	Sep 2006	-	2024-03-01	20103
Hyundai	Santa fé ii	2.2 Crdi	SUV	Frontantrieb	Diesel	114	155	Mar 2006	Dec 2009	2024-03-01	20104
Hyundai	Santa fé ii	2.2 Crdi 4X4	SUV	Allrad	Diesel	114	155	Mar 2006	Dec 2009	2024-03-01	20105
Audi	100	2.0 E 16V	Kombi	Frontantrieb	Benzin	103	140	Jul 1992	Jul 1994	2024-03-01	20106
Opel	Signum cc	2.8 V6 Turbo	Schrägheck	Frontantrieb	Benzin	184	250	Jan 2006	Dec 2008	2024-03-01	20108
Audi	A6 c6	2.8 FSI	Stufenheck	Frontantrieb	Benzin	154	210	Nov 2006	Oct 2008	2024-03-01	20109
Audi	A6 c6 avant	2.8 FSI	Kombi	Frontantrieb	Benzin	154	210	Nov 2006	Oct 2008	2024-03-01	20110
Opel	Zafira	1.6 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Jul 2005	Apr 2015	2024-03-01	20111
Porsche	Cayenne	3.6	SUV	Allrad	Benzin	213	290	Feb 2007	Sep 2010	2024-03-01	20112
Porsche	Cayenne	S 4.8	SUV	Allrad	Benzin	283	385	Feb 2007	Sep 2010	2024-03-01	20113
Porsche	Cayenne	Turbo S 4.8	SUV	Allrad	Benzin	368	500	Feb 2007	Sep 2010	2024-03-01	20114
Audi	A4 b8 avant	1.8 Tfsi Quattro	Kombi	Allrad	Benzin	125	170	Nov 2011	Dec 2015	2024-03-01	20115
Audi	A4 b8 avant	3.0 Tfsi Quattro	Kombi	Allrad	Benzin	200	272	Feb 2012	Dec 2015	2024-03-01	20116
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	130	177	Nov 2011	Dec 2015	2024-03-01	20117
Audi	A4 b8 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	130	177	Nov 2011	Dec 2015	2024-03-01	20118


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理车身聚类，完成 **29 个输入 Ktype、34 条 READY 映射、20 个尺寸组**。
* `20027`、`20028`、`20030` 覆盖 Peugeot 207 CC 2009 年改款前后；长度由 4037 mm 变为 4044 mm，高度由 1397 mm 变为 1393 mm，因此拆成 `prefl` 和 `facelift`。([汽车数据网][1])
* `20049` 跨越 Seat Leon II 改款，改款前 Cupra 长 4315 mm，改款后长 4323 mm，因此拆分；`20048` 在 2009 年 3 月结束，只关联改款前组。([Spiegler][2])
* `20078` 同时覆盖 Clio III 三门 `CR0` 和五门 `BR0`，即使三维相同，也因门体和侧面外廓不同拆为两个尺寸组。
* `20016` 与 `20017` 分别确认车身代码 `216.377`、`216.379`；两款 AMG 外廓均为 5090×1871×1418 mm，复用同一尺寸组。([Meyer Motoren][3])
* `20029` Lexus LFA 暂未写入：现有来源对高度存在 1220 mm 与 1265 mm 冲突，未达到尺寸组闭合条件。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：29
* READY 映射：34
* PENDING 输入 Ktype：71
* 已确认尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20010	20010	Wagon	Astra H	L35	5	EU-OPEL-ASTRA-H-WAGON-L35-01	HIGH		READY
20011	20011	Sedan	Vectra C facelift	F69	4	EU-OPEL-VECTRA-C-FACELIFT-SEDAN-F69-01	HIGH		READY
20012	20012	Hatchback	Vectra C facelift	F68	5	EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	HIGH		READY
20013	20013	Hatchback	Vectra C facelift	F68	5	EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	HIGH		READY
20016	20016	Coupe	CL C216	216.377	2	EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	HIGH		READY
20017	20017	Coupe	CL C216	216.379	2	EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	HIGH		READY
20027_prefl	20027	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20027_facelift	20027	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20028_prefl	20028	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20028_facelift	20028	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20030_prefl	20030	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20030_facelift	20030	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20031	20031	Sedan	Jetta V	1K2	4	EU-VOLKSWAGEN-JETTA-V-SEDAN-1K2-01	HIGH		READY
20032	20032	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20033	20033	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20034	20034	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20043	20043	MPV	Alhambra I facelift		5	EU-SEAT-ALHAMBRA-I-FACELIFT-MPV-01	HIGH		READY
20048	20048	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH		READY
20049_prefl	20049	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype跨2009改款，按外廓长度变化拆分。	READY
20049_facelift	20049	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓长度变化拆分。	READY
20054	20054	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20055	20055	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20056	20056	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20069	20069	Sedan	Legend IV	KB1	4	EU-HONDA-LEGEND-IV-SEDAN-KB1-01	HIGH		READY
20073	20073	Sedan	166 facelift	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
20075	20075	Sedan	166 facelift	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
20078_3dr	20078	Hatchback	Clio III Phase I	CR0	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按车身代码拆分。	READY
20078_5dr	20078	Hatchback	Clio III Phase I	BR0	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按车身代码拆分。	READY
20088	20088	MPV	Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
20089	20089	MPV	Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
20090	20090	Sedan	S40 II	MS	4	EU-VOLVO-S40-II-SEDAN-MS-01	HIGH		READY
20104	20104	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	HIGH		READY
20105	20105	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	HIGH		READY
20106	20106	Wagon	100 C4	4A5	5	EU-AUDI-100-C4-AVANT-WAGON-4A5-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-H-WAGON-L35-01	4515	1753	1500	Auto-Data Opel Astra H Caravan	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.8-ecotec-140hp-47496
EU-OPEL-VECTRA-C-FACELIFT-SEDAN-F69-01	4611	1798	1460	Auto-Data Opel Vectra C facelift sedan	https://www.auto-data.net/en/opel-vectra-c-facelift-2005-2.8i-v6-24v-turbo-250hp-2228
EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	4611	1798	1460	Auto-Data Opel Vectra C CC facelift	https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-2.8i-v6-24v-turbo-250hp-2256
EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	5090	1871	1418	Auto-Data Mercedes-Benz CL 63 AMG; Auto-Data Mercedes-Benz CL 65 AMG	https://www.auto-data.net/en/mercedes-benz-cl-c216-amg-cl-63-v8-525hp-7g-tronic-speedshift-12711;https://www.auto-data.net/en/mercedes-benz-cl-c216-amg-cl-65-v12-612hp-5g-tronic-speedshift-12712
EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	4037	1748	1397	Auto-Data Peugeot 207 CC	https://www.auto-data.net/en/peugeot-207-cc-1.6-vti-120hp-5359
EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	4044	1748	1393	Auto-Data Peugeot 207 CC facelift	https://www.auto-data.net/en/peugeot-207-cc-facelift-2009-1.6-vti-120hp-17613
EU-VOLKSWAGEN-JETTA-V-SEDAN-1K2-01	4554	1781	1459	Auto-Data Volkswagen Jetta V	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-cr-170hp-44501
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Auto-Data Lancia Ypsilon 843 facelift	https://www.auto-data.net/en/lancia-ypsilon-843-facelift-2006-1.4-8v-77hp-47146
EU-SEAT-ALHAMBRA-I-FACELIFT-MPV-01	4634	1810	1762	Auto-Data Seat Alhambra I facelift	https://www.auto-data.net/en/seat-alhambra-i-7m-facelift-2000-2.0-tdi-140hp-dpf-29397
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data Seat Leon II Cupra	https://www.auto-data.net/en/seat-leon-ii-1p-cupra-2.0-tfsi-240hp-13611
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data Seat Leon II facelift Cupra	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-cupra-2.0-tfsi-240hp-46476
EU-SEAT-CORDOBA-II-SEDAN-6L2-01	4280	1698	1441	Auto-Data Seat Cordoba II	https://www.auto-data.net/en/seat-cordoba-ii-1.2-12v-64hp-13409
EU-HONDA-LEGEND-IV-SEDAN-KB1-01	4957	1845	1450	Auto-Data Honda Legend IV KB1	https://www.auto-data.net/en/honda-legend-iv-kb1-3.5-v6-vtec-295hp-sh-awd-12170
EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	4720	1800	1416	Auto-Data Alfa Romeo 166 facelift	https://www.auto-data.net/en/alfa-romeo-166-936-facelift-2003-2.4-jtd-20v-175hp-1286
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495	Auto-Data Renault Clio III Phase I 3-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.5-dci-103hp-fap-56130
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495	Auto-Data Renault Clio III Phase I 5-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-1.5-dci-103hp-fap-56133
EU-FIAT-IDEA-MPV-350-01	3930	1698	1660	Auto-Data Fiat Idea	https://www.auto-data.net/en/fiat-idea-1.4-i-8v-77hp-7040
EU-VOLVO-S40-II-SEDAN-MS-01	4476	1770	1454	Auto-Data Volvo S40 II 2.0i; Auto-Data Volvo S40 II facelift 2.0i	https://www.auto-data.net/en/volvo-s40-ii-2.0-i-16v-145hp-9551;https://www.auto-data.net/en/volvo-s40-ii-facelift-2007-2.0i-145hp-17553
EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	4675	1890	1795	Auto-Data Hyundai Santa Fe II CM	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-2.2-crdi-155hp-47873
EU-AUDI-100-C4-AVANT-WAGON-4A5-01	4790	1777	1440	Auto-Data Audi 100 Avant C4	https://www.auto-data.net/en/audi-100-avant-4a-c4-2.0-16v-137hp-26430
```

## 下一步优先处理

1. 批量闭合 Jumpy II、Expert II、Scudo II 的 Bus、Van、底盘车及 L1/L2、普通顶/高顶分支。
2. 处理 Gazelle、Interstar、Primastar、Vito 的轴距和车顶高度组合。
3. 拆分 `20015` S 63 AMG 的 W221 标准轴距与 V221 长轴距。
4. 解决 Lexus LFA 高度来源冲突，并处理 SLR 722、E 63 AMG、G 320 CDI 等单一乘用车。
5. 最后处理 Hilux 的驾驶室/货斗分支以及 Berlingo、Kangoo 的 Van/MPV 双重边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-207-model-572?utm_source=chatgpt.com "Peugeot 207 | Technical Specs, Fuel consumption, ..."
[2]: https://spiegler.de/en/product/seat-leon-1p1-2-0-tfsi-177-kw-240-ps-2006-2013/?utm_source=chatgpt.com "Stahlflex-Bremsleitung für Seat Leon 1P1 | 2.0 TFSI | 2006-2013 - Spiegler.de"
[3]: https://www.meyermotoren.de/en/fahrzeuge/20016/mercedes-benz/s-klasse_coupe_c216_/cl_63_amg_216_377_20016?utm_source=chatgpt.com "CL 63 AMG (216.377) | S-Klasse Coupe (C216) | Mercedes-Benz | Manufacturers | Meyer Motoren"
[4]: https://www.auto-data.net/en/lexus-lfa-generation-4996?utm_source=chatgpt.com "Lexus LFA | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增完成 **18 个输入 Ktype、23 条 READY 映射、19 个尺寸组**。
* `20015` 同时覆盖 W221 标准轴距、V221 长轴距及 2009 年改款前后，四种外廓尺寸均有差异，因此拆成四条派生映射。([AUTODOC][1])
* `20092` Volvo V50 和 `20111` Opel Zafira B 均跨越改款，改款前后外廓高度或长度不同，分别拆成两条映射。([汽车数据网][2])
* `20029` Lexus LFA 采用 Toyota 官方车型历史数据闭合为 4505×1895×1220 mm，上一轮的高度冲突已解决。([丰田官网][3])
* `20112` 与 `20113` 复用 Cayenne 957 普通车身尺寸组；`20114` Turbo S 因外廓尺寸不同独立建组。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：47
* READY 映射：57
* PENDING 输入 Ktype：53
* 已确认尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20014	20014	Coupe	SLR McLaren 722 Edition	199.376	2	EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	HIGH		READY
20015_swb_prefl	20015	Sedan	S-Class W221	221.077	4	EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-PREFL-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_swb_facelift	20015	Sedan	S-Class W221 facelift	221.077	4	EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-FACELIFT-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_lwb_prefl	20015	Sedan	S-Class V221	221.177	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-PREFL-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_lwb_facelift	20015	Sedan	S-Class V221 facelift	221.177	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-FACELIFT-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20029	20029	Coupe	LFA	LFA10	2	EU-LEXUS-LFA-LFA10-COUPE-01	HIGH		READY
20070	20070	Sedan	E-Class W211 facelift	211.077	4	EU-MERCEDES-BENZ-E-CLASS-W211-AMG-SEDAN-01	HIGH		READY
20071	20071	Wagon	E-Class S211 facelift	211.277	5	EU-MERCEDES-BENZ-E-CLASS-S211-AMG-WAGON-01	HIGH		READY
20091	20091	Hatchback	Twizy	MAM	2	EU-RENAULT-TWIZY-MAM-HATCHBACK-01	MEDIUM	轻型四轮车按输入Schrägheck归一为Hatchback。	READY
20092_prefl	20092	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-PREFL-01	HIGH	Ktype跨2007改款，按外廓变化拆分。	READY
20092_facelift	20092	Wagon	V50 facelift	MW	5	EU-VOLVO-V50-MW-WAGON-FACELIFT-01	HIGH	Ktype跨2007改款，按外廓变化拆分。	READY
20108	20108	Hatchback	Signum facelift	Z03	5	EU-OPEL-SIGNUM-Z03-FACELIFT-HATCHBACK-01	HIGH		READY
20109	20109	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4F2-01	HIGH		READY
20110	20110	Wagon	A6 C6 Avant	4F5	5	EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	HIGH		READY
20111_prefl	20111	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-PREFL-01	HIGH	Ktype跨2008改款，按高度变化拆分。	READY
20111_facelift	20111	MPV	Zafira B facelift	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH	Ktype跨2008改款，按高度变化拆分。	READY
20112	20112	SUV	Cayenne 957	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH		READY
20113	20113	SUV	Cayenne 957 S	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH		READY
20114	20114	SUV	Cayenne 957 Turbo S	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	HIGH		READY
20115	20115	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20116	20116	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20117	20117	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20118	20118	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261	Auto-Data Mercedes-Benz SLR McLaren 722 Edition	https://www.auto-data.net/en/mercedes-benz-slr-mclaren-c199-coupe-722-edition-5.5-v8-kompressor-650hp-amg-speedshift-r-12728
EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-PREFL-01	5079	1872	1473	Auto-Data Mercedes-Benz S-Class W221 S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-w221-amg-s-63-v8-525hp-7g-tronic-36902
EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-Class W221 facelift S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-amg-s-63-v8-525hp-amg-speedshift-7g-tronic-36919
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-PREFL-01	5209	1872	1473	Auto-Data Mercedes-Benz S-Class Long V221 S 63 AMG	https://www.auto-data.net/de/mercedes-benz-s-class-long-v221-amg-s-63-525hp-7g-tronic-13054
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data Mercedes-Benz S-Class Long V221 facelift S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-amg-s-63-v8-525hp-amg-speedshift-7g-tronic-36893
EU-LEXUS-LFA-LFA10-COUPE-01	4505	1895	1220	Toyota Motor Corporation vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60017188/index.html
EU-MERCEDES-BENZ-E-CLASS-W211-AMG-SEDAN-01	4881	1822	1465	Auto-Data Mercedes-Benz E-Class W211 E 63 AMG	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-amg-e-63-v8-514hp-7g-tronic-12906
EU-MERCEDES-BENZ-E-CLASS-S211-AMG-WAGON-01	4888	1822	1415	Auto-Data Mercedes-Benz E-Class S211 E 63 AMG	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-amg-e-63-v8-514hp-7g-tronic-12939
EU-RENAULT-TWIZY-MAM-HATCHBACK-01	2338	1237	1454	Auto-Data Renault Twizy ZE	https://www.auto-data.net/en/renault-twizy-ze-6.1-kwh-17hp-43848
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452	Auto-Data Volvo V50	https://www.auto-data.net/en/volvo-v50-2.0-d-136hp-9578
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457	Auto-Data Volvo V50 facelift	https://www.auto-data.net/en/volvo-v50-facelift-2007-1.6-100hp-17166
EU-OPEL-SIGNUM-Z03-FACELIFT-HATCHBACK-01	4651	1798	1466	Auto-Data Opel Signum facelift	https://www.auto-data.net/en/opel-signum-facelift-2005-2.8i-v6-24v-turbo-250hp-2586
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459	Auto-Data Audi A6 C6	https://www.auto-data.net/en/audi-a6-4f-c6-2.8-fsi-v6-210hp-4650
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463	Auto-Data Audi A6 C6 Avant	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.8-fsi-v6-210hp-26771
EU-OPEL-ZAFIRA-B-MPV-PREFL-01	4467	1801	1645	Auto-Data Opel Zafira B	https://www.auto-data.net/en/opel-zafira-b-1.6i-16v-94hp-cng-26156
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635	Auto-Data Opel Zafira B facelift	https://www.auto-data.net/en/opel-zafira-b-facelift-2008-1.6i-16v-94hp-cng-26498
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699	Auto-Data Porsche Cayenne 957 3.6; Auto-Data Porsche Cayenne 957 S 4.8	https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-3.6-v6-290hp-awd-6714;https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-s-4.8-v8-385hp-awd-6718
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696	Auto-Data Porsche Cayenne 957 Turbo 4.8	https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-turbo-4.8-v8-500hp-awd-tiptronic-s-6720
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 B8 Avant facelift 1.8 TFSI; Auto-Data Audi A4 B8 Avant facelift 3.0 TFSI; Auto-Data Audi A4 B8 Avant facelift 2.0 TDI	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-1.8-tfsi-170hp-quattro-18924;https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-3.0-tfsi-v6-272hp-quattro-s-tronic-18933;https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-2.0-tdi-177hp-quattro-s-tronic-18907
```

## 下一步优先处理

1. 批量闭合 Citroën Jumpy II、Peugeot Expert II、Fiat Scudo II 的 Bus、Van、底盘车及轴距、车顶分支。
2. 处理 GAZ Gazelle、Nissan Interstar、Primastar、Mercedes-Benz Vito 的多轴距和多车顶组合。
3. 处理 Berlingo、Kangoo 的 Van/MPV 边界，以及 Hilux 的驾驶室和货斗分支。
4. 补齐 Ibiza III、Golf V 等可能覆盖不同门数的剩余乘用车。

推进信号：CONTINUE

[1]: https://www.auto-doc.fr/pieces-detachees/avertisseur-sonore-trompette-10420/mercedes-benz/s-klasse/classe-s-w221/20015-s-63-amg-221-077-221-177?utm_source=chatgpt.com "Klaxon Mercedes w221 S 63 AMG 6.2 525 CV Essence M 156.984"
[2]: https://www.auto-data.net/en/volvo-v50-facelift-2007-1.6-100hp-17166 "Volvo V50 (facelift 2007) 1.6 (100 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60017188/index.html?utm_source=chatgpt.com "Lexus LFA - Toyota Motor Corporation Official Global Website"
[4]: https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-3.6-v6-290hp-awd-6714 "Porsche Cayenne (955, facelift 2007) 3.6 V6 (290 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮完成 Citroën Jumpy II、Peugeot Expert II、Fiat Scudo II 共平台商用车聚类，新增覆盖 **26 个输入 Ktype、51 条 READY 映射、17 个尺寸组**。
* Jumpy II 和 Expert II 按短轴、长轴及高顶拆分；2.0 HDi 140 厢式车仅覆盖 L1H1、L2H1，1.6 HDi 90 与 2.0 HDi 120 还覆盖 L2H2。车身宽度统一采用不含后视镜的 1895 mm。([标致财富][1])
* Scudo II 官方车型矩阵确认 90/120 Multijet 厢式车覆盖 L1H1、L2H1、L2H2，140 Multijet 不覆盖 L2H2；平台驾驶室独立建组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：73
* READY 映射：108
* PENDING 输入 Ktype：27
* 已确认尺寸组：56
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20035_swb	20035	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20035_lwb	20035	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20036	20036	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH		READY
20037_swb	20037	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20037_lwb	20037	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20038_swb	20038	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20038_lwb	20038	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20039_l1h1	20039	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20039_l2h1	20039	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20040_l1h1	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20040_l2h1	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20040_l2h2	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l1h1	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l2h1	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l2h2	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20042_l1h1	20042	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20042_l2h1	20042	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20050_swb	20050	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20050_lwb	20050	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20051_swb	20051	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20051_lwb	20051	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20052_swb	20052	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20052_lwb	20052	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20058_l1h1	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20058_l2h1	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20058_l2h2	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l1h1	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l2h1	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l2h2	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20060_l1h1	20060	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20060_l2h1	20060	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20061	20061	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20062	20062	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20063	20063	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20076_swb	20076	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20076_lwb	20076	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20077_swb	20077	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20077_lwb	20077	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20079_swb	20079	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20079_lwb	20079	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20081_l1h1	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20081_l2h1	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20081_l2h2	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20083_l1h1	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20083_l2h1	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20083_l2h2	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20084_l1h1	20084	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20084_l2h1	20084	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20085	20085	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20086	20086	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20087	20087	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-II-MPV-SWB-01	4805	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-MPV-LWB-01	5135	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L1H1-01	4805	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L2H1-01	5135	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L2H2-01	5135	1895	2276	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-PEUGEOT-EXPERT-II-MPV-SWB-01	4805	1895	1942	Peugeot Expert Tepee 2007 official brochure; Peugeot Expert official owner handbook	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf;https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-MPV-LWB-01	5135	1895	1942	Peugeot Expert Tepee 2007 official brochure; Peugeot Expert official owner handbook	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf;https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	5016	1895	1942	Peugeot Expert official owner handbook; Peugeot Expert 2007 official brochure	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf;https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-CHASSIS-CAB-01	5053	1895	1942	Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
```

## 下一步优先处理

1. 批量处理 Nissan Interstar 与 Primastar 的短轴、长轴及车顶高度分支。
2. 处理 GAZ Gazelle 的 Bus、Van、底盘车及轴距、车顶组合。
3. 处理 Mercedes-Benz Vito 的车长和车顶分支。
4. 补齐 Berlingo、Kangoo、Hilux、Ibiza III、Golf V、Micra III 和 G-Class 等剩余 Ktype。

推进信号：CONTINUE

[1]: https://citroenpavilly.com/vn/JumpyCombiCt.pdf "CT_JUMPY_0610_Quadri.qxp:CT_CMJN"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮完成 Nissan Interstar X70 与 Primastar X83 的客运、厢式车轴距和车顶组合，新增覆盖 **8 个输入 Ktype、17 条 READY 映射、13 个尺寸组**。
* Interstar 依据官方车型矩阵拆分中轴中顶、长轴中顶和长轴高顶；`20097` 的 dCi 150 仅关联已确认的长轴高顶厢式车组。
* Primastar 客运版按短轴、长轴及发动机对应高度拆分；厢式车进一步区分短轴低顶的 1.0 吨与 1.2 吨悬架高度、短轴高顶、长轴低顶和长轴高顶。([YUMPU][1])
* `20096` Interstar dCi 150 Bus 与 `20102` Primastar dCi 90 Bus 暂未强行关联，因为现有官方客运车型矩阵未确认对应外廓。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：81
* READY 映射：125
* PENDING 输入 Ktype：19
* 已确认尺寸组：69
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20094	20094	MPV	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	HIGH		READY
20095_mwb_midroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20095_lwb_midroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20095_lwb_highroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20097	20097	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	HIGH		READY
20098_swb	20098	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI150-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20098_lwb	20098	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI150-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20099_lwb_lowroof	20099	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	HIGH	同一Ktype覆盖长轴低顶与长轴高顶车身。	READY
20099_lwb_highroof	20099	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖长轴低顶与长轴高顶车身。	READY
20100_swb	20100	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI115-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20100_lwb	20100	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI115-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20101_swb_lowroof_1t	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_swb_lowroof_1p2t	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1P2T-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_swb_highroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-HIGHROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_lwb_lowroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_lwb_highroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20103	20103	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	5899	1990	2456	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI150-01	4782	1904	1958	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI150-01	5182	1904	1954	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	5182	1904	1962	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	5182	1904	2464	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI115-01	4782	1904	1942	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI115-01	5182	1904	1952	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	4782	1904	1955	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1P2T-01	4782	1904	1963	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-HIGHROOF-01	4782	1904	2465	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
```

## 下一步优先处理

1. 处理 Opel/Vauxhall Vivaro 共平台资料，确认 `20102` Primastar dCi 90 Bus 是否存在可闭合的客运外廓。
2. 处理 GAZ Gazelle 的 Bus、Van、底盘车及轴距、车顶分支。
3. 处理 Mercedes-Benz Vito W639 的紧凑型、长轴、超长轴及车顶组合。
4. 补齐 Berlingo、Scudo I、Kangoo、Hilux、Ibiza III、Golf V、Micra III、G-Class。
5. 单独确认 `20096` Interstar dCi 150 Bus 的客运车身边界。

推进信号：CONTINUE

[1]: https://www.yumpu.com/en/document/view/23244658/nissan-primastar "NISSAN PrImAStAr"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 Seat Ibiza III 改款版的三门、五门分支。两种发动机对应相同车身尺寸 3977×1698×1441 mm，但门体外廓不同，分别建组。([汽车数据网][1])
* 完成 `20072`。该 Ktype 明确对应 `463.343` 长轴五门 G 320 CDI，官方尺寸为 4662×1760×1931 mm。([Meyer Motoren][2])
* 完成 Micra III K12 的 68 hp、86 hp 三门与五门分支，统一尺寸为 3734×1660×1540 mm。([汽车目录档案][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：86
* READY 映射：134
* PENDING 输入 Ktype：14
* 已确认尺寸组：74
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20053_3dr	20053	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20053_5dr	20053	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20057_3dr	20057	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20057_5dr	20057	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20072	20072	SUV	G-Class W463	463.343	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH		READY
20080_3dr	20080	Hatchback	Micra III K12 facelift	K12	3	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20080_5dr	20080	Hatchback	Micra III K12 facelift	K12	5	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20082_3dr	20082	Hatchback	Micra III K12 facelift	K12	3	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20082_5dr	20082	Hatchback	Micra III K12 facelift	K12	5	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.2	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.2-70hp-34942
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.2	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.2-70hp-34942
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4662	1760	1931	Mercedes-Benz Public Archive G 320 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2006---2008.xhtml?oid=191039046
EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	3734	1660	1540	Nissan Micra 2008 UK brochure; encyCARpedia Nissan Micra 1.5 dCi 86	https://autocatalogarchive.com/wp-content/uploads/2025/10/Nissan-Micra-2008-UK.pdf;https://www.encycarpedia.com/nissan/06-micra-1-5-dci-86-hatch
EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	3734	1660	1540	Nissan Micra 2008 UK brochure; encyCARpedia Nissan Micra 1.5 dCi 86	https://autocatalogarchive.com/wp-content/uploads/2025/10/Nissan-Micra-2008-UK.pdf;https://www.encycarpedia.com/nissan/06-micra-1-5-dci-86-hatch
```

## 下一步优先处理

1. 处理 Golf V GTI 230 的三门、五门高度来源冲突。
2. 闭合 Berlingo I 与 Kangoo I 的乘用版、厢式版分支。
3. 处理 Vito W639、Scudo I 的轴距和车长组合。
4. 处理 Interstar dCi 150 Bus、Primastar dCi 90 Bus。
5. 最后集中处理 Gazelle 六个 Ktype 与 Hilux 驾驶室、货斗分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.2-70hp-34942 "Seat Ibiza III (facelift 2006) 1.2 (70 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.meyermotoren.de/fahrzeuge/20072/mercedes-benz/g-klasse_w463_/g_320_cdi_463_343_20072 "G 320 CDI (463.343) | G-Klasse (W463) | Mercedes-Benz | Herstellerübersicht | Meyer Motoren"
[3]: https://autocatalogarchive.com/wp-content/uploads/2025/10/Nissan-Micra-2008-UK.pdf?utm_source=chatgpt.com "Nissan-Micra-2008-UK.pdf"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 `20025` Berlingo I M59 的 Van 与 MPV 分支。两者长宽相同，但 Van 高 1819 mm、MPV 高 1810 mm，因此分别建组。([Anchor Vans][1])
* 完成 `20064` Golf V GTI 230 PS 的三门、五门分支。官方资料确认其为 Type 1K，外廓为 4216×1759×1469 mm，并同时存在两门侧门和四门侧门版本。([Volkswagen Newsroom][2])
* 完成 `20068` Kangoo I facelift 的 Van 与 MPV 分支。Van 与 MPV 高度分别为 1835 mm、1825 mm，因此不合并尺寸组。([汽车数据网][3])
* 完成 `20102` Primastar X83 dCi 90 Bus 的短轴、长轴分支；官方资料确认客运版存在两种轴距，精确车型资料分别闭合为 4782×1904×1940 mm 和 5182×1904×1947 mm。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：90
* READY 映射：142
* PENDING 输入 Ktype：10
* 已确认尺寸组：82
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20025_van	20025	Van	Berlingo I M59 facelift	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	输入车身类型覆盖Van与MPV，按高度差异拆分。	READY
20025_mpv	20025	MPV	Berlingo I M59 facelift	M59		EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	输入车身类型覆盖Van与MPV，按高度差异拆分。	READY
20064_3dr	20064	Hatchback	Golf V GTI Edition 30/Pirelli	1K	3	EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20064_5dr	20064	Hatchback	Golf V GTI Edition 30/Pirelli	1K	5	EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20068_van	20068	Van	Kangoo I facelift	FC		EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	HIGH	输入车身类型覆盖Van与MPV，按车身代码和高度拆分。	READY
20068_mpv	20068	MPV	Kangoo I facelift	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	HIGH	输入车身类型覆盖Van与MPV，按车身代码和高度拆分。	READY
20102_swb	20102	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI90-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20102_lwb	20102	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI90-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819	Anchor Vans Citroën Berlingo 1.6 HDi 75 specifications	https://www.anchorvans.co.uk/specifications/berlingo
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810	Automobile-Catalog Citroën Berlingo Multispace 1.6 HDi 75	https://www.automobile-catalog.com/car/2005/550220/citroen_berlingo_multispace_1_6_hdi_75_fap.html
EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-3D-01	4216	1759	1469	Volkswagen Newsroom Golf V GTI history; Volkswagen Newsroom Golf V GTI vehicle data	https://www.volkswagen-newsroom.com/en/golf-5-gti-20042008-19511;https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-gti-profile-19512
EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-5D-01	4216	1759	1469	Volkswagen Newsroom Golf V GTI history; Volkswagen Newsroom Golf V GTI vehicle data	https://www.volkswagen-newsroom.com/en/golf-5-gti-20042008-19511;https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-gti-profile-19512
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835	Auto-Data Renault Kangoo I Express FC facelift	https://www.auto-data.net/en/renault-kangoo-i-express-fc-facelift-2003-1.5-dci-65hp-33873
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825	Automobile-Catalog Renault Kangoo 1.5 dCi 70	https://www.automobile-catalog.com/car/2005/2948930/renault_kangoo_1_5_dci_70.html
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI90-01	4782	1904	1940	Nissan Primastar official brochure; EngineInDetail Nissan Primastar short dCi 90	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf;https://www.engineindetail.com/pa/nissan-primastar-estate-wagon-short-2-0-dci-90-comfort-9-seater-2006
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI90-01	5182	1904	1947	Nissan Primastar official brochure; EngineInDetail Nissan Primastar long dCi 90	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf;https://www.engineindetail.com/pa/nissan-primastar-estate-wagon-long-2-0-dci-90-pro-9-seater-2006
```

## 下一步优先处理

1. 闭合 Fiat Scudo I Bus 的短轴、长轴车身。
2. 拆分 Mercedes-Benz Vito W639 Bus 的紧凑、长轴和超长轴外廓。
3. 确认 Interstar dCi 150 Bus 属于原厂客运车身还是基于高顶厢式车的改装车型。
4. 集中处理 GAZ Gazelle 的 Bus、Van、底盘车分支。
5. 最后处理 Toyota Hilux IV 的单排、双排及货斗长度边界。

推进信号：CONTINUE

[1]: https://www.anchorvans.co.uk/specifications/berlingo?utm_source=chatgpt.com "Berlingo, Specifications"
[2]: https://www.volkswagen-newsroom.com/en/golf-5-gti-20042008-19511?utm_source=chatgpt.com "Golf V GTI (2004–2008) | Volkswagen Newsroom"
[3]: https://www.auto-data.net/en/renault-kangoo-i-express-fc-facelift-2003-1.5-dci-65hp-33873?utm_source=chatgpt.com "Renault Kangoo I Express (FC, facelift 2003) 1.5 dCi (65 Hp)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_801-900_ktype_dimension_mapping_final.tsv
- all_801-900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 剩余 10 个 Ktype 已全部闭合：GAZ Gazelle 6 个、Fiat Scudo I、Mercedes-Benz Vito W639、Toyota Hilux IV、Nissan Interstar dCi 150 Bus。
* 已完成最终机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、全部映射引用闭合、尺寸及来源字段完整、无孤立尺寸组。
* 当前批次已满足 COMPLETE 条件。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：156
* PENDING：0
* DIMENSION_GROUP：92
* 映射覆盖率：100%

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20010	20010	Wagon	Astra H	L35	5	EU-OPEL-ASTRA-H-WAGON-L35-01	HIGH		READY
20011	20011	Sedan	Vectra C facelift	F69	4	EU-OPEL-VECTRA-C-FACELIFT-SEDAN-F69-01	HIGH		READY
20012	20012	Hatchback	Vectra C facelift	F68	5	EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	HIGH		READY
20013	20013	Hatchback	Vectra C facelift	F68	5	EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	HIGH		READY
20014	20014	Coupe	SLR McLaren 722 Edition	199.376	2	EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	HIGH		READY
20015_swb_prefl	20015	Sedan	S-Class W221	221.077	4	EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-PREFL-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_swb_facelift	20015	Sedan	S-Class W221 facelift	221.077	4	EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-FACELIFT-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_lwb_prefl	20015	Sedan	S-Class V221	221.177	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-PREFL-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20015_lwb_facelift	20015	Sedan	S-Class V221 facelift	221.177	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-FACELIFT-01	HIGH	同一Ktype覆盖标准轴距、长轴距及2009改款前后，按物理外廓拆分。	READY
20016	20016	Coupe	CL C216	216.377	2	EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	HIGH		READY
20017	20017	Coupe	CL C216	216.379	2	EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	HIGH		READY
20018	20018	MPV	GAZelle I	3221		EU-GAZ-GAZELLE-I-MPV-3221-01	MEDIUM		READY
20019	20019	MPV	GAZelle I	3221		EU-GAZ-GAZELLE-I-MPV-3221-01	MEDIUM		READY
20020	20020	Van	GAZelle I	2705		EU-GAZ-GAZELLE-I-VAN-2705-01	MEDIUM		READY
20021	20021	Van	GAZelle I	2705		EU-GAZ-GAZELLE-I-VAN-2705-01	MEDIUM		READY
20022	20022	Pickup	GAZelle I	3302	2	EU-GAZ-GAZELLE-I-PICKUP-3302-01	MEDIUM		READY
20023	20023	Pickup	GAZelle I	3302	2	EU-GAZ-GAZELLE-I-PICKUP-3302-01	MEDIUM		READY
20025_van	20025	Van	Berlingo I M59 facelift	M59		EU-CITROEN-BERLINGO-I-M59-VAN-01	HIGH	输入车身类型覆盖Van与MPV，按高度差异拆分。	READY
20025_mpv	20025	MPV	Berlingo I M59 facelift	M59		EU-CITROEN-BERLINGO-I-M59-MPV-01	HIGH	输入车身类型覆盖Van与MPV，按高度差异拆分。	READY
20026_swb	20026	MPV	Scudo I facelift	220		EU-FIAT-SCUDO-I-MPV-SWB-01	HIGH	同一Ktype覆盖标准轴距与长轴客运车身。	READY
20026_lwb	20026	MPV	Scudo I facelift	220		EU-FIAT-SCUDO-I-MPV-LWB-01	HIGH	同一Ktype覆盖标准轴距与长轴客运车身。	READY
20027_prefl	20027	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20027_facelift	20027	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20028_prefl	20028	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20028_facelift	20028	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20029	20029	Coupe	LFA	LFA10	2	EU-LEXUS-LFA-LFA10-COUPE-01	HIGH		READY
20030_prefl	20030	Convertible	207 CC		2	EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20030_facelift	20030	Convertible	207 CC facelift		2	EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓变化拆分。	READY
20031	20031	Sedan	Jetta V	1K2	4	EU-VOLKSWAGEN-JETTA-V-SEDAN-1K2-01	HIGH		READY
20032	20032	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20033	20033	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20034	20034	Hatchback	Ypsilon 843 facelift	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
20035_swb	20035	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20035_lwb	20035	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20036	20036	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH		READY
20037_swb	20037	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20037_lwb	20037	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20038_swb	20038	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20038_lwb	20038	MPV	Jumpy II			EU-CITROEN-JUMPY-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20039_l1h1	20039	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20039_l2h1	20039	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20040_l1h1	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20040_l2h1	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20040_l2h2	20040	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l1h1	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l2h1	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20041_l2h2	20041	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20042_l1h1	20042	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20042_l2h1	20042	Van	Jumpy II			EU-CITROEN-JUMPY-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20043	20043	MPV	Alhambra I facelift		5	EU-SEAT-ALHAMBRA-I-FACELIFT-MPV-01	HIGH		READY
20048	20048	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH		READY
20049_prefl	20049	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype跨2009改款，按外廓长度变化拆分。	READY
20049_facelift	20049	Hatchback	Leon II facelift	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨2009改款，按外廓长度变化拆分。	READY
20050_swb	20050	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20050_lwb	20050	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20051_swb	20051	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20051_lwb	20051	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20052_swb	20052	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20052_lwb	20052	MPV	Expert II			EU-PEUGEOT-EXPERT-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20053_3dr	20053	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20053_5dr	20053	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20054	20054	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20055	20055	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20056	20056	Sedan	Cordoba II	6L2	4	EU-SEAT-CORDOBA-II-SEDAN-6L2-01	HIGH		READY
20057_3dr	20057	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20057_5dr	20057	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20058_l1h1	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20058_l2h1	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20058_l2h2	20058	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l1h1	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l2h1	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20059_l2h2	20059	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20060_l1h1	20060	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20060_l2h1	20060	Van	Expert II			EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20061	20061	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20062	20062	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20063	20063	Pickup	Expert II			EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20064_3dr	20064	Hatchback	Golf V GTI Edition 30/Pirelli	1K	3	EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20064_5dr	20064	Hatchback	Golf V GTI Edition 30/Pirelli	1K	5	EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20068_van	20068	Van	Kangoo I facelift	FC		EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	HIGH	输入车身类型覆盖Van与MPV，按车身代码和高度拆分。	READY
20068_mpv	20068	MPV	Kangoo I facelift	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	HIGH	输入车身类型覆盖Van与MPV，按车身代码和高度拆分。	READY
20069	20069	Sedan	Legend IV	KB1	4	EU-HONDA-LEGEND-IV-SEDAN-KB1-01	HIGH		READY
20070	20070	Sedan	E-Class W211 facelift	211.077	4	EU-MERCEDES-BENZ-E-CLASS-W211-AMG-SEDAN-01	HIGH		READY
20071	20071	Wagon	E-Class S211 facelift	211.277	5	EU-MERCEDES-BENZ-E-CLASS-S211-AMG-WAGON-01	HIGH		READY
20072	20072	SUV	G-Class W463	463.343	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH		READY
20073	20073	Sedan	166 facelift	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
20074_compact	20074	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	同一Ktype覆盖紧凑、长轴与超长轴客运车身。	READY
20074_long	20074	MPV	Vito W639	639.703		EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	同一Ktype覆盖紧凑、长轴与超长轴客运车身。	READY
20074_extralong	20074	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	同一Ktype覆盖紧凑、长轴与超长轴客运车身。	READY
20075	20075	Sedan	166 facelift	936	4	EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	HIGH		READY
20076_swb	20076	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20076_lwb	20076	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20077_swb	20077	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20077_lwb	20077	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20078_3dr	20078	Hatchback	Clio III Phase I	CR0	3	EU-RENAULT-CLIO-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按车身代码拆分。	READY
20078_5dr	20078	Hatchback	Clio III Phase I	BR0	5	EU-RENAULT-CLIO-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按车身代码拆分。	READY
20079_swb	20079	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-SWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20079_lwb	20079	MPV	Scudo II			EU-FIAT-SCUDO-II-MPV-LWB-01	HIGH	同一Ktype覆盖短轴与长轴车身。	READY
20080_3dr	20080	Hatchback	Micra III K12 facelift	K12	3	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20080_5dr	20080	Hatchback	Micra III K12 facelift	K12	5	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20081_l1h1	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20081_l2h1	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20081_l2h2	20081	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20082_3dr	20082	Hatchback	Micra III K12 facelift	K12	3	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20082_5dr	20082	Hatchback	Micra III K12 facelift	K12	5	EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门车身。	READY
20083_l1h1	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20083_l2h1	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20083_l2h2	20083	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H2-01	HIGH	同一Ktype覆盖L1H1、L2H1与L2H2车身。	READY
20084_l1h1	20084	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L1H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20084_l2h1	20084	Van	Scudo II			EU-FIAT-SCUDO-II-VAN-L2H1-01	HIGH	同一Ktype覆盖L1H1与L2H1车身。	READY
20085	20085	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20086	20086	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20087	20087	Pickup	Scudo II			EU-FIAT-SCUDO-II-CHASSIS-CAB-01	HIGH	平台驾驶室物理外廓。	READY
20088	20088	MPV	Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
20089	20089	MPV	Idea	350	5	EU-FIAT-IDEA-MPV-350-01	HIGH		READY
20090	20090	Sedan	S40 II	MS	4	EU-VOLVO-S40-II-SEDAN-MS-01	HIGH		READY
20091	20091	Hatchback	Twizy	MAM	2	EU-RENAULT-TWIZY-MAM-HATCHBACK-01	MEDIUM	轻型四轮车按输入Schrägheck归一为Hatchback。	READY
20092_prefl	20092	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-PREFL-01	HIGH	Ktype跨2007改款，按外廓变化拆分。	READY
20092_facelift	20092	Wagon	V50 facelift	MW	5	EU-VOLVO-V50-MW-WAGON-FACELIFT-01	HIGH	Ktype跨2007改款，按外廓变化拆分。	READY
20093	20093	Pickup	Hilux IV	LN65	2	EU-TOYOTA-HILUX-IV-PICKUP-LN65-01	MEDIUM	LN65低货台标准货斗单排车身。	READY
20094	20094	MPV	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	HIGH		READY
20095_mwb_midroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20095_lwb_midroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20095_lwb_highroof	20095	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖中轴中顶、长轴中顶与长轴高顶车身。	READY
20096_mwb_midroof	20096	MPV	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-MPV-MWB-MIDROOF-01	MEDIUM	同一Ktype覆盖中轴中顶与长轴中顶客运车身。	READY
20096_lwb_midroof	20096	MPV	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	MEDIUM	同一Ktype覆盖中轴中顶与长轴中顶客运车身。	READY
20097	20097	Van	Interstar X70	X70		EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	HIGH		READY
20098_swb	20098	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI150-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20098_lwb	20098	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI150-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20099_lwb_lowroof	20099	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	HIGH	同一Ktype覆盖长轴低顶与长轴高顶车身。	READY
20099_lwb_highroof	20099	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖长轴低顶与长轴高顶车身。	READY
20100_swb	20100	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI115-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20100_lwb	20100	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI115-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20101_swb_lowroof_1t	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_swb_lowroof_1p2t	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1P2T-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_swb_highroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-HIGHROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_lwb_lowroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20101_lwb_highroof	20101	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	HIGH	同一Ktype覆盖1.0吨与1.2吨悬架高度及不同轴距、车顶车身。	READY
20102_swb	20102	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI90-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20102_lwb	20102	MPV	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI90-01	HIGH	同一Ktype覆盖短轴与长轴客运车身。	READY
20103	20103	Van	Primastar X83 facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	HIGH		READY
20104	20104	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	HIGH		READY
20105	20105	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	HIGH		READY
20106	20106	Wagon	100 C4	4A5	5	EU-AUDI-100-C4-AVANT-WAGON-4A5-01	HIGH		READY
20108	20108	Hatchback	Signum facelift	Z03	5	EU-OPEL-SIGNUM-Z03-FACELIFT-HATCHBACK-01	HIGH		READY
20109	20109	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4F2-01	HIGH		READY
20110	20110	Wagon	A6 C6 Avant	4F5	5	EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	HIGH		READY
20111_prefl	20111	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-PREFL-01	HIGH	Ktype跨2008改款，按高度变化拆分。	READY
20111_facelift	20111	MPV	Zafira B facelift	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH	Ktype跨2008改款，按高度变化拆分。	READY
20112	20112	SUV	Cayenne 957	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH		READY
20113	20113	SUV	Cayenne 957 S	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH		READY
20114	20114	SUV	Cayenne 957 Turbo S	9PA	5	EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	HIGH		READY
20115	20115	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20116	20116	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20117	20117	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
20118	20118	Wagon	A4 B8 Avant facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_801-900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-H-WAGON-L35-01	4515	1753	1500	Auto-Data Opel Astra H Caravan	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.8-ecotec-140hp-47496
EU-OPEL-VECTRA-C-FACELIFT-SEDAN-F69-01	4611	1798	1460	Auto-Data Opel Vectra C facelift sedan	https://www.auto-data.net/en/opel-vectra-c-facelift-2005-2.8i-v6-24v-turbo-250hp-2228
EU-OPEL-VECTRA-C-FACELIFT-HATCHBACK-F68-01	4611	1798	1460	Auto-Data Opel Vectra C CC facelift	https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-2.8i-v6-24v-turbo-250hp-2256
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261	Auto-Data Mercedes-Benz SLR McLaren 722 Edition	https://www.auto-data.net/en/mercedes-benz-slr-mclaren-c199-coupe-722-edition-5.5-v8-kompressor-650hp-amg-speedshift-r-12728
EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-PREFL-01	5079	1872	1473	Auto-Data Mercedes-Benz S-Class W221 S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-w221-amg-s-63-v8-525hp-7g-tronic-36902
EU-MERCEDES-BENZ-S-CLASS-W221-AMG-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data Mercedes-Benz S-Class W221 facelift S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-amg-s-63-v8-525hp-amg-speedshift-7g-tronic-36919
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-PREFL-01	5209	1872	1473	Auto-Data Mercedes-Benz S-Class Long V221 S 63 AMG	https://www.auto-data.net/de/mercedes-benz-s-class-long-v221-amg-s-63-525hp-7g-tronic-13054
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data Mercedes-Benz S-Class Long V221 facelift S 63 AMG	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-amg-s-63-v8-525hp-amg-speedshift-7g-tronic-36893
EU-MERCEDES-BENZ-CL-C216-AMG-COUPE-01	5090	1871	1418	Auto-Data Mercedes-Benz CL 63 AMG; Auto-Data Mercedes-Benz CL 65 AMG	https://www.auto-data.net/en/mercedes-benz-cl-c216-amg-cl-63-v8-525hp-7g-tronic-speedshift-12711;https://www.auto-data.net/en/mercedes-benz-cl-c216-amg-cl-65-v12-612hp-5g-tronic-speedshift-12712
EU-GAZ-GAZELLE-I-MPV-3221-01	5475	2075	2200	GAZ-3221 vehicle specifications	https://www.26auto.ru/gaz/lmg/gmd04/gaz3221/
EU-GAZ-GAZELLE-I-VAN-2705-01	5475	2075	2200	GAZ-2705 vehicle specifications	https://www.26auto.ru/gaz/lmg/gmd04/gaz2705/
EU-GAZ-GAZELLE-I-PICKUP-3302-01	5480	2066	2120	GAZelle operating specifications	https://gazavtomir.ru/info/teh/exploitation/gazel_umz/4/
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819	Anchor Vans Citroën Berlingo 1.6 HDi 75 specifications	https://www.anchorvans.co.uk/specifications/berlingo
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810	Automobile-Catalog Citroën Berlingo Multispace 1.6 HDi 75	https://www.automobile-catalog.com/car/2005/550220/citroen_berlingo_multispace_1_6_hdi_75_fap.html
EU-FIAT-SCUDO-I-MPV-SWB-01	4440	1810	1940	Fiat Scudo 1995-2006 owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
EU-FIAT-SCUDO-I-MPV-LWB-01	4840	1810	1930	Fiat Scudo 1995-2006 owner manual dimensions	https://www.mycarusermanual.com/fiat/scudo/van/1995-2006/dimensions
EU-PEUGEOT-207-CC-CONVERTIBLE-PREFL-01	4037	1748	1397	Auto-Data Peugeot 207 CC	https://www.auto-data.net/en/peugeot-207-cc-1.6-vti-120hp-5359
EU-PEUGEOT-207-CC-CONVERTIBLE-FACELIFT-01	4044	1748	1393	Auto-Data Peugeot 207 CC facelift	https://www.auto-data.net/en/peugeot-207-cc-facelift-2009-1.6-vti-120hp-17613
EU-LEXUS-LFA-LFA10-COUPE-01	4505	1895	1220	Toyota Motor Corporation vehicle lineage	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60017188/index.html
EU-VOLKSWAGEN-JETTA-V-SEDAN-1K2-01	4554	1781	1459	Auto-Data Volkswagen Jetta V	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-cr-170hp-44501
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Auto-Data Lancia Ypsilon 843 facelift	https://www.auto-data.net/en/lancia-ypsilon-843-facelift-2006-1.4-8v-77hp-47146
EU-CITROEN-JUMPY-II-MPV-SWB-01	4805	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-MPV-LWB-01	5135	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L1H1-01	4805	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L2H1-01	5135	1895	1942	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-CITROEN-JUMPY-II-VAN-L2H2-01	5135	1895	2276	Citroën Jumpy technical specifications June 2010	https://citroenpavilly.com/vn/JumpyCombiCt.pdf
EU-SEAT-ALHAMBRA-I-FACELIFT-MPV-01	4634	1810	1762	Auto-Data Seat Alhambra I facelift	https://www.auto-data.net/en/seat-alhambra-i-7m-facelift-2000-2.0-tdi-140hp-dpf-29397
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data Seat Leon II Cupra	https://www.auto-data.net/en/seat-leon-ii-1p-cupra-2.0-tfsi-240hp-13611
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data Seat Leon II facelift Cupra	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-cupra-2.0-tfsi-240hp-46476
EU-PEUGEOT-EXPERT-II-MPV-SWB-01	4805	1895	1942	Peugeot Expert Tepee 2007 official brochure; Peugeot Expert official owner handbook	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf;https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-MPV-LWB-01	5135	1895	1942	Peugeot Expert Tepee 2007 official brochure; Peugeot Expert official owner handbook	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf;https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.2	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.2-70hp-34942
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.2	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.2-70hp-34942
EU-SEAT-CORDOBA-II-SEDAN-6L2-01	4280	1698	1441	Auto-Data Seat Cordoba II	https://www.auto-data.net/en/seat-cordoba-ii-1.2-12v-64hp-13409
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276	Peugeot Expert official owner handbook	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf
EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	5016	1895	1942	Peugeot Expert official owner handbook; Peugeot Expert 2007 official brochure	https://manuals.plus/m/9be6f7e56bf89f757deea34af28f3bc0cdc8ecd3a64ebd87ac690c81c1fd1321_optim.pdf;https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-Expert-Tepee-UK.pdf
EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-3D-01	4216	1759	1469	Volkswagen Newsroom Golf V GTI history; Volkswagen Newsroom Golf V GTI vehicle data	https://www.volkswagen-newsroom.com/en/golf-5-gti-20042008-19511;https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-gti-profile-19512
EU-VOLKSWAGEN-GOLF-V-GTI-HATCHBACK-5D-01	4216	1759	1469	Volkswagen Newsroom Golf V GTI history; Volkswagen Newsroom Golf V GTI vehicle data	https://www.volkswagen-newsroom.com/en/golf-5-gti-20042008-19511;https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-gti-profile-19512
EU-RENAULT-KANGOO-I-FACELIFT-VAN-FC-01	4035	1672	1835	Auto-Data Renault Kangoo I Express FC facelift	https://www.auto-data.net/en/renault-kangoo-i-express-fc-facelift-2003-1.5-dci-65hp-33873
EU-RENAULT-KANGOO-I-FACELIFT-MPV-KC-01	4035	1672	1825	Automobile-Catalog Renault Kangoo 1.5 dCi 70	https://www.automobile-catalog.com/car/2005/2948930/renault_kangoo_1_5_dci_70.html
EU-HONDA-LEGEND-IV-SEDAN-KB1-01	4957	1845	1450	Auto-Data Honda Legend IV KB1	https://www.auto-data.net/en/honda-legend-iv-kb1-3.5-v6-vtec-295hp-sh-awd-12170
EU-MERCEDES-BENZ-E-CLASS-W211-AMG-SEDAN-01	4881	1822	1465	Auto-Data Mercedes-Benz E-Class W211 E 63 AMG	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-amg-e-63-v8-514hp-7g-tronic-12906
EU-MERCEDES-BENZ-E-CLASS-S211-AMG-WAGON-01	4888	1822	1415	Auto-Data Mercedes-Benz E-Class S211 E 63 AMG	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-amg-e-63-v8-514hp-7g-tronic-12939
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4662	1760	1931	Mercedes-Benz Public Archive G 320 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-CDI-long-wheelbase-2006---2008.xhtml?oid=191039046
EU-ALFA-ROMEO-166-936-FACELIFT-SEDAN-01	4720	1800	1416	Auto-Data Alfa Romeo 166 facelift	https://www.auto-data.net/en/alfa-romeo-166-936-facelift-2003-2.4-jtd-20v-175hp-1286
EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	4748	1901	1902	Mercedes-Benz Vito 2005 official specification sheet	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	4993	1901	1902	Mercedes-Benz Vito 2005 official specification sheet	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	5223	1901	1900	Mercedes-Benz Vito 2005 official specification sheet	https://xr793.com/wp-content/uploads/2022/12/2005-Mercedes-Benz-Vito-Panel-Van-Spec-Sheet-UK.pdf
EU-FIAT-SCUDO-II-MPV-SWB-01	4805	1895	1980	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-MPV-LWB-01	5135	1895	1980	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495	Auto-Data Renault Clio III Phase I 3-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.5-dci-103hp-fap-56130
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495	Auto-Data Renault Clio III Phase I 5-door	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-1.5-dci-103hp-fap-56133
EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-3D-01	3734	1660	1540	Nissan Micra 2008 UK brochure; encyCARpedia Nissan Micra 1.5 dCi 86	https://autocatalogarchive.com/wp-content/uploads/2025/10/Nissan-Micra-2008-UK.pdf;https://www.encycarpedia.com/nissan/06-micra-1-5-dci-86-hatch
EU-NISSAN-MICRA-III-K12-FACELIFT-HATCHBACK-5D-01	3734	1660	1540	Nissan Micra 2008 UK brochure; encyCARpedia Nissan Micra 1.5 dCi 86	https://autocatalogarchive.com/wp-content/uploads/2025/10/Nissan-Micra-2008-UK.pdf;https://www.encycarpedia.com/nissan/06-micra-1-5-dci-86-hatch
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276	Fiat Scudo official technical data; Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010114007_scudo_techndaten.pdf;https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-CHASSIS-CAB-01	5053	1895	1942	Fiat Scudo official technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-IDEA-MPV-350-01	3930	1698	1660	Auto-Data Fiat Idea	https://www.auto-data.net/en/fiat-idea-1.4-i-8v-77hp-7040
EU-VOLVO-S40-II-SEDAN-MS-01	4476	1770	1454	Auto-Data Volvo S40 II 2.0i; Auto-Data Volvo S40 II facelift 2.0i	https://www.auto-data.net/en/volvo-s40-ii-2.0-i-16v-145hp-9551;https://www.auto-data.net/en/volvo-s40-ii-facelift-2007-2.0i-145hp-17553
EU-RENAULT-TWIZY-MAM-HATCHBACK-01	2338	1237	1454	Auto-Data Renault Twizy ZE	https://www.auto-data.net/en/renault-twizy-ze-6.1-kwh-17hp-43848
EU-VOLVO-V50-MW-WAGON-PREFL-01	4514	1770	1452	Auto-Data Volvo V50	https://www.auto-data.net/en/volvo-v50-2.0-d-136hp-9578
EU-VOLVO-V50-MW-WAGON-FACELIFT-01	4522	1770	1457	Auto-Data Volvo V50 facelift	https://www.auto-data.net/en/volvo-v50-facelift-2007-1.6-100hp-17166
EU-TOYOTA-HILUX-IV-PICKUP-LN65-01	4690	1690	1765	Toyota Motor Corporation Hilux Surf 1st vehicle lineage; Toyota Hilux LN65 parts catalogue	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60011317/index.html;https://jp-carparts.com/toyota/figlist.php?cartype=32&maker=toyota&type=671140
EU-NISSAN-INTERSTAR-X70-MPV-LWB-MIDROOF-16SEAT-01	5899	1990	2456	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-MWB-MIDROOF-01	5399	1990	2486	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-MIDROOF-01	5899	1990	2484	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-VAN-LWB-HIGHROOF-01	5899	1990	2716	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-INTERSTAR-X70-MPV-MWB-MIDROOF-01	5399	1990	2486	Nissan Interstar official e-brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI150-01	4782	1904	1958	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI150-01	5182	1904	1954	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-LWB-LOWROOF-01	5182	1904	1962	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-LWB-HIGHROOF-01	5182	1904	2464	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI115-01	4782	1904	1942	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI115-01	5182	1904	1952	Nissan Primastar 2009 official e-brochure; Nissan Primastar 2011 official brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar;https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1T-01	4782	1904	1955	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-LOWROOF-1P2T-01	4782	1904	1963	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-VAN-SWB-HIGHROOF-01	4782	1904	2465	Nissan Primastar 2009 official e-brochure	https://www.yumpu.com/en/document/view/23244658/nissan-primastar
EU-NISSAN-PRIMASTAR-X83-MPV-SWB-DCI90-01	4782	1904	1940	Nissan Primastar official brochure; EngineInDetail Nissan Primastar short dCi 90	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf;https://www.engineindetail.com/pa/nissan-primastar-estate-wagon-short-2-0-dci-90-comfort-9-seater-2006
EU-NISSAN-PRIMASTAR-X83-MPV-LWB-DCI90-01	5182	1904	1947	Nissan Primastar official brochure; EngineInDetail Nissan Primastar long dCi 90	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf;https://www.engineindetail.com/pa/nissan-primastar-estate-wagon-long-2-0-dci-90-pro-9-seater-2006
EU-HYUNDAI-SANTA-FE-II-SUV-CM-01	4675	1890	1795	Auto-Data Hyundai Santa Fe II CM	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-2.2-crdi-155hp-47873
EU-AUDI-100-C4-AVANT-WAGON-4A5-01	4790	1777	1440	Auto-Data Audi 100 Avant C4	https://www.auto-data.net/en/audi-100-avant-4a-c4-2.0-16v-137hp-26430
EU-OPEL-SIGNUM-Z03-FACELIFT-HATCHBACK-01	4651	1798	1466	Auto-Data Opel Signum facelift	https://www.auto-data.net/en/opel-signum-facelift-2005-2.8i-v6-24v-turbo-250hp-2586
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459	Auto-Data Audi A6 C6	https://www.auto-data.net/en/audi-a6-4f-c6-2.8-fsi-v6-210hp-4650
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463	Auto-Data Audi A6 C6 Avant	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.8-fsi-v6-210hp-26771
EU-OPEL-ZAFIRA-B-MPV-PREFL-01	4467	1801	1645	Auto-Data Opel Zafira B	https://www.auto-data.net/en/opel-zafira-b-1.6i-16v-94hp-cng-26156
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635	Auto-Data Opel Zafira B facelift	https://www.auto-data.net/en/opel-zafira-b-facelift-2008-1.6i-16v-94hp-cng-26498
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699	Auto-Data Porsche Cayenne 957 3.6; Auto-Data Porsche Cayenne 957 S 4.8	https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-3.6-v6-290hp-awd-6714;https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-s-4.8-v8-385hp-awd-6718
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696	Auto-Data Porsche Cayenne 957 Turbo 4.8	https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-turbo-4.8-v8-500hp-awd-tiptronic-s-6720
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 B8 Avant facelift 1.8 TFSI; Auto-Data Audi A4 B8 Avant facelift 3.0 TFSI; Auto-Data Audi A4 B8 Avant facelift 2.0 TDI	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-1.8-tfsi-170hp-quattro-18924;https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-3.0-tfsi-v6-272hp-quattro-s-tronic-18933;https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-2.0-tdi-177hp-quattro-s-tronic-18907
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_801-900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_801-900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_801-900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1078 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（535 行）
