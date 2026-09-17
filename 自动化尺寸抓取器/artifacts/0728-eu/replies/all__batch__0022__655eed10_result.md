# 任务：all 第 2101-2200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0022__655eed10


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2101-2200 行

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
all 第 2101-2200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Citroën	Dyane	6	Schrägheck	Frontantrieb	Benzin	24	33	May 1972	Dec 1980	2024-03-01	2140
Fiat	Balilla 508 saloon	1	Stufenheck	Heckantrieb	Benzin	18	24	Mar 1934	Dec 1937	2024-03-01	2141
Fiat	Fiorino	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jul 2009	-	2024-03-01	2142
Citroën	Lna	0.6	Schrägheck	Frontantrieb	Benzin	24	33	Nov 1976	Jul 1979	2024-03-01	2143
Citroën	Lna	0.6	Schrägheck	Frontantrieb	Benzin	25	34	Jul 1982	Apr 1985	2024-03-01	2144
Citroën	Lna	0.6	Schrägheck	Frontantrieb	Benzin	26	35	Nov 1978	Jul 1986	2024-03-01	2145
Citroën	Lna	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Jul 1982	Apr 1985	2024-03-01	2146
Citroën	Ax	10 E	Schrägheck	Frontantrieb	Benzin	30	41	Dec 1986	Dec 1988	2024-03-01	2147
Citroën	Ax	10	Schrägheck	Frontantrieb	Benzin	33	45	Jul 1986	Dec 1998	2024-03-01	2148
Citroën	Ax	11	Schrägheck	Frontantrieb	Benzin	40	54	Dec 1986	Apr 1994	2024-03-01	2149
Fiat	Ducato	140 Natural Power	Kasten	Frontantrieb	CNG	100	136	Apr 2009	-	2024-03-01	2150
Citroën	Ax	1.3 Sport	Schrägheck	Frontantrieb	Benzin	70	95	Apr 1987	Dec 1988	2024-03-01	2151
Citroën	Ax	14	Schrägheck	Frontantrieb	Benzin	44	60	Dec 1986	Dec 1988	2024-03-01	2152
Citroën	Ax	14	Schrägheck	Frontantrieb	Benzin	62	85	Jan 1988	Dec 1992	2024-03-01	2153
Citroën	Ax	14	Schrägheck	Frontantrieb	Benzin	49	67	Jun 1988	Dec 1989	2024-03-01	2154
Citroën	Ax	14 D	Schrägheck	Frontantrieb	Diesel	38	52	Sep 1988	Jun 1992	2024-03-01	2155
Citroën	Ax	14 D	Schrägheck	Frontantrieb	Diesel	37	50	Aug 1991	Dec 1997	2024-03-01	2156
Citroën	Ax	11	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1986	Dec 1997	2024-03-01	2157
Citroën	Ax	14	Schrägheck	Frontantrieb	Benzin	55	75	Apr 1987	Apr 1997	2024-03-01	2158
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	103	140	Apr 2010	Dec 2020	2024-03-01	2159
Citroën	Gs	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Sep 1977	Jun 1980	2024-03-01	2160
Citroën	Gs	1.1	Schrägheck	Frontantrieb	Benzin	42	57	Sep 1977	Jul 1981	2024-03-01	2161
Citroën	Gs	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Apr 1973	Jun 1979	2024-03-01	2162
Citroën	Gs	A 1.3	Schrägheck	Frontantrieb	Benzin	48	65	Jul 1978	Jul 1986	2024-03-01	2163
Citroën	Gs	A 1.2	Kombi	Frontantrieb	Benzin	43	58	Apr 1973	Jun 1979	2024-03-01	2165
Citroën	Gs	A 1.3	Kombi	Frontantrieb	Benzin	48	65	Sep 1979	Jul 1986	2024-03-01	2166
Citroën	Visa	0.6	Schrägheck	Frontantrieb	Benzin	24	33	Jul 1982	Mar 1991	2024-03-01	2167
Citroën	Visa	0.6	Schrägheck	Frontantrieb	Benzin	25	34	Sep 1978	Jun 1988	2024-03-01	2168
Lancia	Ypsilon	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Aug 2010	Dec 2011	2024-03-01	2169
Citroën	Visa	11 E	Schrägheck	Frontantrieb	Benzin	35	48	Sep 1978	Jun 1988	2024-03-01	2170
Citroën	Visa	11 E	Schrägheck	Frontantrieb	Benzin	37	50	Jul 1982	Mar 1991	2024-03-01	2171
Citroën	Visa	11 E	Schrägheck	Frontantrieb	Benzin	42	57	Sep 1978	Mar 1991	2024-03-01	2172
Citroën	Visa	14	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1984	Mar 1991	2024-03-01	2173
Citroën	Visa	14 GT	Schrägheck	Frontantrieb	Benzin	58	79	Mar 1982	Mar 1991	2024-03-01	2174
Citroën	Visa	16 GTI	Schrägheck	Frontantrieb	Benzin	76	103	Jan 1985	Jun 1986	2024-03-01	2175
Citroën	Visa	16 GTI	Schrägheck	Frontantrieb	Benzin	83	113	Jun 1986	Mar 1991	2024-03-01	2176
Citroën	Visa	17 D	Schrägheck	Frontantrieb	Diesel	44	60	Apr 1984	Mar 1991	2024-03-01	2177
Citroën	Bx	14 E	Schrägheck	Frontantrieb	Benzin	45	61	Oct 1982	Jun 1988	2024-03-01	2178
Citroën	Bx	14 E	Schrägheck	Frontantrieb	Benzin	49	67	Sep 1985	Feb 1993	2024-03-01	2179
Citroën	Bx	14 E	Schrägheck	Frontantrieb	Benzin	52	71	Apr 1983	Jul 1989	2024-03-01	2180
Citroën	Bx	14 E	Schrägheck	Frontantrieb	Benzin	53	72	Apr 1983	Feb 1993	2024-03-01	2181
Citroën	Bx	16	Schrägheck	Frontantrieb	Benzin	53	72	Jan 1987	Feb 1993	2024-03-01	2182
Citroën	Bx	16	Schrägheck	Frontantrieb	Benzin	64	87	Jul 1985	Feb 1993	2024-03-01	2183
Citroën	Bx	16	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1982	Jun 1988	2024-03-01	2184
Citroën	Bx	16	Schrägheck	Frontantrieb	Benzin	68	92	Oct 1982	Dec 1992	2024-03-01	2185
Citroën	Bx	16	Schrägheck	Frontantrieb	Benzin	76	103	Mar 1986	Feb 1993	2024-03-01	2186
Citroën	Bx	19	Schrägheck	Frontantrieb	Benzin	70	95	Sep 1986	Nov 1989	2024-03-01	2187
Citroën	Bx	19	Schrägheck	Frontantrieb	Benzin	75	102	Jul 1986	May 1989	2024-03-01	2188
Citroën	Bx	19 E	Schrägheck	Frontantrieb	Benzin	80	109	Jun 1988	Feb 1993	2024-03-01	2189
Citroën	Bx	19 GTI	Schrägheck	Frontantrieb	Benzin	88	120	Jun 1988	Feb 1993	2024-03-01	2190
Citroën	Bx	19 GTI	Schrägheck	Frontantrieb	Benzin	90	122	Jul 1986	Feb 1993	2024-03-01	2191
Citroën	Bx	19 GTI 16V	Schrägheck	Frontantrieb	Benzin	108	147	Mar 1988	Feb 1993	2024-03-01	2192
Citroën	Bx	TRD Turbo	Schrägheck	Frontantrieb	Diesel	66	90	Mar 1988	Feb 1993	2024-03-01	2193
Citroën	Bx	19 D	Schrägheck	Frontantrieb	Diesel	47	64	Sep 1983	Sep 1993	2024-03-01	2194
Citroën	Bx	19 D	Schrägheck	Frontantrieb	Diesel	51	69	Mar 1987	Feb 1993	2024-03-01	2195
Citroën	Bx	14	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1989	Feb 1993	2024-03-01	2196
Citroën	Bx	16 E	Schrägheck	Frontantrieb	Benzin	65	88	May 1989	Feb 1993	2024-03-01	2197
Citroën	Bx	19 E 4X4	Schrägheck	Allrad	Benzin	80	109	Apr 1989	Feb 1993	2024-03-01	2198
Citroën	Bx	19 GTI 4X4	Schrägheck	Allrad	Benzin	88	120	Jun 1988	Feb 1993	2024-03-01	2199
Citroën	Bx	16	Kombi	Frontantrieb	Benzin	53	72	Sep 1988	Dec 1994	2024-03-01	2200
Citroën	Bx	16	Kombi	Frontantrieb	Benzin	64	87	Jul 1985	Dec 1994	2024-03-01	2201
Citroën	Bx	16	Kombi	Frontantrieb	Benzin	76	103	Mar 1986	Dec 1994	2024-03-01	2202
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	75	102	Jul 1986	Dec 1994	2024-03-01	2203
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	88	120	Jun 1988	Dec 1994	2024-03-01	2204
Citroën	Bx	TRD Turbo	Kombi	Frontantrieb	Diesel	66	90	Mar 1988	Dec 1994	2024-03-01	2205
Citroën	Bx	19 D	Kombi	Frontantrieb	Diesel	47	64	Sep 1983	Nov 1994	2024-03-01	2206
Citroën	Bx	19 D	Kombi	Frontantrieb	Diesel	51	69	Mar 1987	Dec 1994	2024-03-01	2207
Citroën	Bx	16	Kombi	Frontantrieb	Benzin	65	88	May 1989	Dec 1994	2024-03-01	2208
Citroën	Bx	19	Kombi	Frontantrieb	Benzin	80	109	Jun 1988	Dec 1994	2024-03-01	2209
Citroën	Cx i	2000	Stufenheck	Frontantrieb	Benzin	78	106	Jun 1979	Aug 1985	2024-03-01	2210
Citroën	Cx ii	22 TRS	Stufenheck	Frontantrieb	Benzin	83	113	Jul 1985	Dec 1992	2024-03-01	2211
Citroën	Cx i	2400	Stufenheck	Frontantrieb	Benzin	85	116	Aug 1976	Jun 1980	2024-03-01	2213
Citroën	Cx i	2400 GTI	Stufenheck	Frontantrieb	Benzin	96	131	Jun 1977	Jun 1982	2024-03-01	2214
Citroën	Cx i	2400 GTI	Stufenheck	Frontantrieb	Benzin	94	128	Jun 1977	Jun 1982	2024-03-01	2215
Citroën	Cx ii	25 GTI	Stufenheck	Frontantrieb	Benzin	89	121	May 1986	Dec 1992	2024-03-01	2216
Citroën	Cx ii	25 TRI	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1985	Dec 1992	2024-03-01	2217
Citroën	Cx ii	25 GTI Turbo 2	Stufenheck	Frontantrieb	Benzin	115	156	Sep 1986	Dec 1992	2024-03-01	2218
Citroën	Cx ii	25 GTI Turbo 2	Stufenheck	Frontantrieb	Benzin	122	166	Aug 1985	Dec 1992	2024-03-01	2219
Citroën	Cx i	2200 D	Stufenheck	Frontantrieb	Diesel	49	67	Oct 1975	Feb 1979	2024-03-01	2220
Citroën	Cx ii	25 D	Stufenheck	Frontantrieb	Diesel	54	73	Aug 1985	Dec 1992	2024-03-01	2221
Citroën	Cx i	2500 D	Stufenheck	Frontantrieb	Diesel	55	75	Feb 1978	Jun 1982	2024-03-01	2222
Citroën	Cx ii	25 D Turbo	Stufenheck	Frontantrieb	Diesel	70	95	Aug 1985	Dec 1986	2024-03-01	2223
Citroën	Cx ii	25 D Turbo	Stufenheck	Frontantrieb	Diesel	88	120	Jan 1987	Dec 1992	2024-03-01	2224
Citroën	Cx i break	2000	Kombi	Frontantrieb	Benzin	78	106	Jun 1979	Aug 1985	2024-03-01	2225
Citroën	Cx i break	2400	Kombi	Frontantrieb	Benzin	85	116	Aug 1976	Jun 1980	2024-03-01	2226
Citroën	Cx i break	2400 GTI	Kombi	Frontantrieb	Benzin	94	128	Jul 1982	Jun 1983	2024-03-01	2227
Citroën	Cx ii break	25 TRI	Kombi	Frontantrieb	Benzin	100	136	Aug 1985	Dec 1992	2024-03-01	2228
Citroën	Cx i break	2500 D	Kombi	Frontantrieb	Diesel	55	75	Feb 1978	Aug 1985	2024-03-01	2229
Citroën	Cx i break	2500 D Turbo	Kombi	Frontantrieb	Diesel	70	95	Apr 1983	Aug 1985	2024-03-01	2230
Citroën	Cx ii break	25 D	Kombi	Frontantrieb	Diesel	54	73	May 1986	Dec 1992	2024-03-01	2231
Citroën	Cx ii break	25 D Turbo 2	Kombi	Frontantrieb	Diesel	88	120	Jan 1987	Dec 1992	2024-03-01	2232
Citroën	Cx ii break	25 I	Kombi	Frontantrieb	Benzin	89	121	May 1986	Dec 1992	2024-03-01	2233
Citroën	C25	1.8 E	Bus	Frontantrieb	Benzin	51	69	Jul 1987	Feb 1994	2024-03-01	2234
Citroën	C25	2.0 E	Bus	Frontantrieb	Benzin	58	79	Sep 1981	Feb 1994	2024-03-01	2235
Citroën	C25	1.9 D	Bus	Frontantrieb	Diesel	51	69	Jul 1987	Feb 1994	2024-03-01	2236
Citroën	C25	2.5 D	Bus	Frontantrieb	Diesel	54	73	Oct 1985	Feb 1994	2024-03-01	2237
Citroën	C25	2.5 D Turbo 4X4	Bus	Allrad	Diesel	70	95	Aug 1987	Feb 1994	2024-03-01	2238
Citroën	C25	2	Bus	Frontantrieb	Benzin	62	84	Feb 1991	Feb 1994	2024-03-01	2239
Citroën	C25	2.5 D Turbo	Bus	Frontantrieb	Diesel	70	95	Aug 1987	Feb 1994	2024-03-01	2241
Citroën	C15	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	35	48	Oct 1984	Dec 1996	2024-03-01	2243


--- Round 1 / 首次发送 ---
## 1. 更新点

* 本轮按物理外廓聚类，已闭合 Dyane、508B Balilla、LNA、GS/GSA、Visa、BX 掀背、CX/CX Break 等尺寸组，并批量关联相同外廓的发动机 Ktype。
* LNA、Visa、BX、CX 中跨越明确改款边界的 Ktype 已拆成稳定派生行；BX 掀背按 Phase I、Phase II 和四驱高度差异独立建组。([汽车目录][1])
* BX Break 暂未混入掀背尺寸组；现有资料显示旅行版不同动力或配置存在高度差异，需要继续确定分组边界。
* Fiorino、Ducato、C25、C15 等商用车仍需确定具体轴距、车顶和客货车身分支。

## 2. 当前批次进度

* 输入 Ktype：100
* 已 READY Ktype：69 / 100
* 已生成 READY 映射行：88
* PENDING Ktype：31 / 100
* 已确认尺寸组：28
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2140	2140	Hatchback	Dyane		5	EU-CITROEN-DYANE-HATCHBACK-5D-01	HIGH		READY
2141_2dr	2141	Sedan	508B Balilla	508B	2	EU-FIAT-508B-BALILLA-SEDAN-01	MEDIUM	508B两门轿车分支。	READY
2141_4dr	2141	Sedan	508B Balilla	508B	4	EU-FIAT-508B-BALILLA-SEDAN-01	MEDIUM	508B四门轿车分支。	READY
2144	2144	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2145_prefl	2145	Hatchback	LNA		3	EU-CITROEN-LNA-HATCHBACK-3D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2145_facelift	2145	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2146	2146	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2151	2151	Hatchback	AX		3	EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	HIGH		READY
2153	2153	Hatchback	AX		3	EU-CITROEN-AX-GT-HATCHBACK-3D-01	MEDIUM	GT宽体三门外廓。	READY
2159	2159	Hatchback	Giulietta Type 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
2160	2160	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2161	2161	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2162	2162	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2163	2163	Hatchback	GSA		5	EU-CITROEN-GSA-HATCHBACK-5D-01	HIGH		READY
2165	2165	Wagon	GS Break		5	EU-CITROEN-GS-BREAK-WAGON-5D-01	HIGH		READY
2166	2166	Wagon	GSA Break		5	EU-CITROEN-GSA-BREAK-WAGON-5D-01	HIGH		READY
2167_prefl	2167	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2167_facelift	2167	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2168_prefl	2168	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2168_facelift	2168	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2169	2169	Hatchback	Ypsilon (843 facelift)	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2170_prefl	2170	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2170_facelift	2170	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2171_prefl	2171	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2171_facelift	2171	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2172_prefl	2172	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2172_facelift	2172	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2173	2173	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	HIGH		READY
2175	2175	Hatchback	Visa GTI		5	EU-CITROEN-VISA-GTI-105-HATCHBACK-5D-01	HIGH		READY
2176	2176	Hatchback	Visa GTI		5	EU-CITROEN-VISA-GTI-115-HATCHBACK-5D-01	HIGH		READY
2177	2177	Hatchback	Visa		5	EU-CITROEN-VISA-DIESEL-HATCHBACK-5D-01	HIGH		READY
2178_prefl	2178	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2178_facelift	2178	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2179_prefl	2179	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2179_facelift	2179	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2180_prefl	2180	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2180_facelift	2180	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2181_prefl	2181	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2181_facelift	2181	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2182	2182	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2183_prefl	2183	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2183_facelift	2183	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2184_prefl	2184	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2184_facelift	2184	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2185_prefl	2185	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2185_facelift	2185	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2186_prefl	2186	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2186_facelift	2186	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2187	2187	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2188	2188	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2189	2189	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2190	2190	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2191	2191	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2192	2192	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2193	2193	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2194_prefl	2194	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2194_facelift	2194	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2195	2195	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2196	2196	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2197	2197	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2198	2198	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	HIGH		READY
2199	2199	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	HIGH		READY
2210_pre82	2210	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	MEDIUM	Ktype跨越1982年外廓宽度变化，拆分为改款前分支。	READY
2210_post82	2210	Sedan	CX I		4	EU-CITROEN-CX-I-1982-FACELIFT-SEDAN-4D-01	MEDIUM	Ktype跨越1982年外廓宽度变化，拆分为改款后分支。	READY
2211	2211	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2213	2213	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2214	2214	Sedan	CX I		4	EU-CITROEN-CX-I-GTI-SEDAN-4D-01	HIGH		READY
2215	2215	Sedan	CX I		4	EU-CITROEN-CX-I-GTI-SEDAN-4D-01	HIGH		READY
2216	2216	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2217	2217	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2218	2218	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2219	2219	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2220	2220	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2221	2221	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2222	2222	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2223	2223	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2224	2224	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2225_pre82	2225	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2225_post82	2225	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2226	2226	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	HIGH		READY
2227	2227	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	HIGH		READY
2228	2228	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2229_pre82	2229	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2229_post82	2229	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2230	2230	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	HIGH		READY
2231	2231	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2232	2232	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2233	2233	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-DYANE-HATCHBACK-5D-01	3905	1500	1540	Auto-Data	https://www.auto-data.net/en/citroen-dyane-i-phase-i-dyane-6-28hp-15199
EU-FIAT-508B-BALILLA-SEDAN-01	3145	1400	1530	Auta5P	https://auta5p.eu/muzea/museo_mille_miglia_2024/m1000m_07.php
EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	3427	1540	1373	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/533270/citroen_lna.html
EU-CITROEN-LNA-HATCHBACK-3D-01	3400	1520	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/55160/citroen_lna.html
EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	3495	1596	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1451270/citroen_ax_sport.html
EU-CITROEN-AX-GT-HATCHBACK-3D-01	3495	1596	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/62720/citroen_ax_gt.html
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-2.0-jtdm-140hp-17467
EU-CITROEN-GS-HATCHBACK-4D-01	4120	1608	1349	Auto-Data	https://www.auto-data.net/en/citroen-gs-1.2-59hp-14936
EU-CITROEN-GSA-HATCHBACK-5D-01	4181	1626	1349	Auto-Data	https://www.auto-data.net/en/citroen-gsa-a-1.3-65hp-14937
EU-CITROEN-GS-BREAK-WAGON-5D-01	4120	1608	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/2030315/citroen_gs_1220_break_club.html
EU-CITROEN-GSA-BREAK-WAGON-5D-01	4143	1626	1349	Auto-Data	https://www.auto-data.net/en/citroen-gsa-break-a-1.3-65hp-14931
EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	3690	1530	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/534140/citroen_visa.html
EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/534275/citroen_visa_11_e.html
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Auto-Data	https://www.auto-data.net/en/lancia-ypsilon-843-facelift-2006-1.2-8v-69hp-47149
EU-CITROEN-VISA-GTI-105-HATCHBACK-5D-01	3725	1540	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/52970/citroen_visa_gti.html
EU-CITROEN-VISA-GTI-115-HATCHBACK-5D-01	3725	1600	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1449830/citroen_visa_gti_115ch.html
EU-CITROEN-VISA-DIESEL-HATCHBACK-5D-01	3725	1550	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/63830/citroen_visa_17_rd_5-speed.html
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	4230	1650	1358	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/28325/citroen_bx.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/539165/citroen_bx_16_trs_cat.html
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/50765/citroen_bx_19_gt.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	4237	1682	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/62330/citroen_bx_4x4.html
EU-CITROEN-CX-I-SEDAN-4D-01	4659	1734	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/532730/citroen_cx_2000_reflex.html
EU-CITROEN-CX-I-1982-FACELIFT-SEDAN-4D-01	4659	1770	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/533090/citroen_cx_25_d.html
EU-CITROEN-CX-II-SEDAN-4D-01	4650	1770	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/540065/citroen_cx_25_gti.html
EU-CITROEN-CX-I-GTI-SEDAN-4D-01	4659	1755	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/532910/citroen_cx_2400_gti.html
EU-CITROEN-CX-I-BREAK-WAGON-5D-01	4922	1734	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/38840/citroen_cx_break_2000_confort.html
EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	4930	1770	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/540170/citroen_cx_break_25_rd_5-speed.html
EU-CITROEN-CX-II-BREAK-WAGON-5D-01	4930	1770	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/540080/citroen_cx_break_25_tri.html
```

## 5. 下一步优先处理

1. 优先闭合 AX 的普通窄体、GT/宽体、三门/五门及改款分支：`2147–2149、2152、2154–2158`。
2. 核对 Fiorino、Ducato、C25、C15 的轴距、车顶高度和客货车身边界：`2142、2150、2234–2243`。
3. 确定 BX Break 汽油、柴油及不同高度配置的尺寸组边界：`2200–2209`。
4. 最后处理日期边界异常的 LNA `2143` 和 Visa 14 GT `2174`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/55160/citroen_lna.html "https://www.automobile-catalog.com/car/1979/55160/citroen_lna.html"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 闭合 Citroën LN 早期三门车身，修正 `2143` 的实际代际边界。
* 闭合 AX 普通车身 Phase I、Phase II 两个尺寸组；对应资料明确覆盖三门和五门，Phase I/II 长度分别为 3495/3525 mm，宽度均为不含后视镜的 1555 mm。([汽车目录][1])
* `2148、2149、2155、2157、2158` 跨越 AX 改款边界，按 Phase I/II 和三门/五门拆分；`2147、2152、2154、2156` 按门数拆分。
* 闭合 Visa 14 GT 的 Phase I、早期 Phase II 和 1984 后期外廓三个分支。([汽车数据][2])
* BX Break 及商用车多轴距/多车顶分支本轮未创建猜测性尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：80 / 100
* READY 映射行：120
* PENDING Ktype：20 / 100
* 已确认尺寸组：34
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2143	2143	Hatchback	LN		3	EU-CITROEN-LN-HATCHBACK-3D-01	HIGH	输入名称为LNA，但生产期和功率对应LN。	READY
2147_3dr	2147	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2147_5dr	2147	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2148_3dr_prefl	2148	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2148_5dr_prefl	2148	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2148_3dr_facelift	2148	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2148_5dr_facelift	2148	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2149_3dr_prefl	2149	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2149_5dr_prefl	2149	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2149_3dr_facelift	2149	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2149_5dr_facelift	2149	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2152_3dr	2152	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2152_5dr	2152	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2154_3dr	2154	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2154_5dr	2154	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2155_3dr_prefl	2155	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2155_5dr_prefl	2155	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2155_3dr_facelift	2155	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2155_5dr_facelift	2155	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2156_3dr	2156	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	AX Phase II三门分支。	READY
2156_5dr	2156	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	AX Phase II五门分支。	READY
2157_3dr_prefl	2157	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2157_5dr_prefl	2157	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2157_3dr_facelift	2157	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2157_5dr_facelift	2157	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2158_3dr_prefl	2158	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门普通车身。	READY
2158_5dr_prefl	2158	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门普通车身。	READY
2158_3dr_facelift	2158	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门普通车身。	READY
2158_5dr_facelift	2158	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门普通车身。	READY
2174_phase1	2174	Hatchback	Visa Phase I GT		5	EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	MEDIUM	Visa GT初期Phase I外廓。	READY
2174_phase2	2174	Hatchback	Visa Phase II GT		5	EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	MEDIUM	Visa GT早期Phase II外廓。	READY
2174_facelift	2174	Hatchback	Visa Phase II GT		5	EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Visa GT后期外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-LN-HATCHBACK-3D-01	3380	1520	1370	Auto-Data	https://www.auto-data.net/en/citroen-ln-0.6-32hp-15107
EU-CITROEN-AX-PHASE-I-HATCHBACK-01	3495	1555	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/540620/citroen_ax_11_tre.html
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1451225/citroen_ax_11_tge.html
EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	3690	1535	1408	Auto-Data	https://www.auto-data.net/en/citroen-visa-phase-i-14-gt-79hp-14915
EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	3690	1530	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/55190/citroen_visa_gt.html
EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/534350/citroen_visa_gt.html
```

## 5. 下一步优先处理

1. 优先闭合 `2200–2209` BX Break：区分 Phase I、Phase II 早期及后期高度分支。
2. 随后处理 `2142` Fiorino 的货运版/乘用版与改款边界。
3. 最后集中处理 `2150、2234–2239、2241、2243` 的轴距、车顶和 Bus/Van 车身分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/540635/citroen_ax_14_trs.html?utm_source=chatgpt.com "1988 Citroen AX 14 TRS Specs Review (48 kW / 65 PS / 64 hp) (up to mid-year 1988 for Europe )"
[2]: https://www.auto-data.net/en/citroen-visa-phase-i-14-gt-79hp-14915 "Citroen Visa (Phase I) 14 GT (79 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 `2200–2209` 的 BX Break 外廓边界。
* 首次创建 BX Break Phase I、Phase II 早期和 Phase II 后期三个尺寸组；长度均为 4399 mm，改款后车宽由 1660 mm 增至 1682 mm，后期高度由 1431 mm 调整为 1410 mm。宽度来源均明确为不含后视镜口径。([汽车目录][1])
* 跨越外廓变化节点的 Ktype 已拆分为 `prefl`、`facelift`、`late` 分支。
* 本轮未重复输出或重新核对既有尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：90 / 100
* READY 映射行：143
* PENDING Ktype：10 / 100
* 已确认尺寸组：37
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2200_facelift	2200	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2200_late	2200	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2201_prefl	2201	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	Phase I旅行车外廓。	READY
2201_facelift	2201	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2201_late	2201	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2202_prefl	2202	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	Phase I旅行车外廓。	READY
2202_facelift	2202	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2202_late	2202	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2203_facelift	2203	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2203_late	2203	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2204_facelift	2204	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2204_late	2204	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2205_facelift	2205	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2205_late	2205	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2206_prefl	2206	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	输入起始期早于Break量产；保留已确认Phase I外廓。	READY
2206_facelift	2206	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2206_late	2206	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2207_facelift	2207	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2207_late	2207	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2208_facelift	2208	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2208_late	2208	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2209_facelift	2209	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2209_late	2209	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	4399	1660	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/54530/citroen_bx_break_19_rd.html
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/539960/citroen_bx_break_19_rd.html
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/539630/citroen_bx_break_19_tzs.html
```

## 5. 下一步优先处理

1. 闭合 `2142` Fiorino 的 Cargo、Combi 与 2016 改款分支。
2. 闭合 `2150` Ducato Natural Power 的实际可用轴距和车顶组合。
3. 集中处理 `2234–2239、2241` C25 Bus 与 `2243` C15 的车身分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/54530/citroen_bx_break_19_rd.html?utm_source=chatgpt.com "1985 Citroen BX Break 19 RD Specs Review (48 kW ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合 Fiorino 改款前 Cargo、改款前 Combi 以及改款后 Cargo/Combi 三套外廓；改款后两种用途共享同一尺寸组。([Stellantis Media][1])
* 闭合 Ducato Natural Power 对应的 X250 L2H2 中轴高顶车身。
* 闭合 C15 厢式和乘用衍生外廓；两种用途复用同一尺寸组。([Citroën Origins][2])
* C25 的 7 个 Ktype 暂未闭合：现有资料能够确认基础 L1H1、L1H2、L2H2 尺寸，但尚不能确定各 Bus 发动机及四驱版本实际覆盖的车身分支，因此未创建猜测性映射。([Дром][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：93 / 100
* READY 映射行：150
* PENDING Ktype：7 / 100
* 已确认尺寸组：42
* 剩余 PENDING：`2234、2235、2236、2237、2238、2239、2241`
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2142_cargo_prefl	2142	Van	Fiorino III			EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	HIGH	改款前Cargo短后悬外廓。	READY
2142_combi_prefl	2142	MPV	Fiorino III			EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	HIGH	改款前Combi长后悬外廓。	READY
2142_cargo_facelift	2142	Van	Fiorino III facelift			EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	HIGH	改款后Cargo外廓。	READY
2142_combi_facelift	2142	MPV	Fiorino III facelift			EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	HIGH	改款后Combi与Cargo共享外廓。	READY
2150	2150	Van	Ducato III	250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	HIGH	L2H2中轴高顶原厂配置。	READY
2243_van	2243	Van	C15			EU-CITROEN-C15-VAN-MPV-01	HIGH	厢式车分支。	READY
2243_mpv	2243	MPV	C15			EU-CITROEN-C15-VAN-MPV-01	MEDIUM	乘用衍生与厢式车共享外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	3864	1716	1721	Fiat Professional official press pack	https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	3959	1716	1721	Fiat Professional official press pack	https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	3957	1716	1721	Fiat Professional Fiorino official brochure	https://glencom.co.uk/wp-content/uploads/2019/03/fiat-professional-fiorino-brochure.pdf
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524	Fiat Professional Ducato Natural Power technical presentation;AutoScout24	https://cng.auto.pl/pliki/DUCATONATURAL.pdf;https://www.autoscout24.de/auto/technische-daten/fiat/ducato/ducato-maxi-35-natural-power-16000/
EU-CITROEN-C15-VAN-MPV-01	3995	1636	1801	Citroën Origins;Drom	https://www.citroenorigins.co.uk/en/cars/c15;https://www.drom.ru/catalog/citroen/c15/specs/dimensions/
```

## 5. 下一步优先处理

1. 仅处理 C25 Bus 剩余 7 个 Ktype，先确定普通前驱版本覆盖的 L1H1、L1H2、L2H2 分支。
2. 单独确认 `2238` 四驱 Bus 是否改变高度或限制车身长度。
3. 闭合后立即进行一次机械收尾，并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack?utm_source=chatgpt.com "AWARD-WINNING NEW FIAT FIORINO IN UK (PRESS PACK) | FIAT Professional | Stellantis Media"
[2]: https://www.citroenorigins.co.uk/en/cars/c15?utm_source=chatgpt.com "Citroën C15 - Photos, détails et équipements"
[3]: https://www.drom.ru/catalog/lcv/citroen/c25/g_1981_11397/ "Citroen C25 1981, 1982, 1983, 1984, 1985, цельнометаллический фургон, 1 поколение технические характеристики и комплектации"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2101-2200_ktype_dimension_mapping_final.tsv
- all_2101-2200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 C25 剩余 7 个 Ktype：普通 Minibus 复用短轴低顶尺寸组；四驱版本单独保留物理分支；`2241` 另拆出涡轮柴油高顶 16 座 Minibus 分支。C25 资料明确列出短/长轴、普通/加高车顶组合；维修资料给出 1965 mm 车身宽度，历史商用车资料确认涡轮柴油高顶 16 座版本，四驱资料则指向短轴车身。据此完成映射层归并。([France Galerie][1])
* 已完成唯一一次机械收尾：固定表头、主键唯一、Ktype 全覆盖、映射外键闭合、尺寸组无孤立记录、三维为正整数、来源及 URL 非空。
* 最终产物包含 158 条 READY 映射和 45 个尺寸组。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY Ktype：100 / 100
* READY 映射行：158
* PENDING：0
* DIMENSION_GROUP：45
* 机械检查：全部通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2140	2140	Hatchback	Dyane		5	EU-CITROEN-DYANE-HATCHBACK-5D-01	HIGH		READY
2141_2dr	2141	Sedan	508B Balilla	508B	2	EU-FIAT-508B-BALILLA-SEDAN-01	MEDIUM	508B两门轿车分支。	READY
2141_4dr	2141	Sedan	508B Balilla	508B	4	EU-FIAT-508B-BALILLA-SEDAN-01	MEDIUM	508B四门轿车分支。	READY
2142_cargo_prefl	2142	Van	Fiorino III			EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	HIGH	改款前Cargo短后悬外廓。	READY
2142_combi_prefl	2142	MPV	Fiorino III			EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	HIGH	改款前Combi长后悬外廓。	READY
2142_cargo_facelift	2142	Van	Fiorino III facelift			EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	HIGH	改款后Cargo外廓。	READY
2142_combi_facelift	2142	MPV	Fiorino III facelift			EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	HIGH	改款后Combi与Cargo共享外廓。	READY
2143	2143	Hatchback	LN		3	EU-CITROEN-LN-HATCHBACK-3D-01	HIGH	输入名称为LNA，但生产期和功率对应LN。	READY
2144	2144	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2145_prefl	2145	Hatchback	LNA		3	EU-CITROEN-LNA-HATCHBACK-3D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2145_facelift	2145	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2146	2146	Hatchback	LNA (1982 facelift)		3	EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2147_3dr	2147	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2147_5dr	2147	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2148_3dr_prefl	2148	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2148_5dr_prefl	2148	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2148_3dr_facelift	2148	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2148_5dr_facelift	2148	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2149_3dr_prefl	2149	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2149_5dr_prefl	2149	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2149_3dr_facelift	2149	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2149_5dr_facelift	2149	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2150	2150	Van	Ducato III	250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	HIGH	L2H2中轴高顶原厂配置。	READY
2151	2151	Hatchback	AX		3	EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	HIGH		READY
2152_3dr	2152	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2152_5dr	2152	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2153	2153	Hatchback	AX		3	EU-CITROEN-AX-GT-HATCHBACK-3D-01	MEDIUM	GT宽体三门外廓。	READY
2154_3dr	2154	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I三门分支。	READY
2154_5dr	2154	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	AX Phase I五门分支。	READY
2155_3dr_prefl	2155	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2155_5dr_prefl	2155	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2155_3dr_facelift	2155	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2155_5dr_facelift	2155	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2156_3dr	2156	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	AX Phase II三门分支。	READY
2156_5dr	2156	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	AX Phase II五门分支。	READY
2157_3dr_prefl	2157	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门外廓。	READY
2157_5dr_prefl	2157	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门外廓。	READY
2157_3dr_facelift	2157	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门外廓。	READY
2157_5dr_facelift	2157	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门外廓。	READY
2158_3dr_prefl	2158	Hatchback	AX Phase I		3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I三门普通车身。	READY
2158_5dr_prefl	2158	Hatchback	AX Phase I		5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	覆盖AX Phase I五门普通车身。	READY
2158_3dr_facelift	2158	Hatchback	AX Phase II		3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II三门普通车身。	READY
2158_5dr_facelift	2158	Hatchback	AX Phase II		5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	覆盖AX Phase II五门普通车身。	READY
2159	2159	Hatchback	Giulietta Type 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
2160	2160	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2161	2161	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2162	2162	Hatchback	GS		4	EU-CITROEN-GS-HATCHBACK-4D-01	HIGH		READY
2163	2163	Hatchback	GSA		5	EU-CITROEN-GSA-HATCHBACK-5D-01	HIGH		READY
2165	2165	Wagon	GS Break		5	EU-CITROEN-GS-BREAK-WAGON-5D-01	HIGH		READY
2166	2166	Wagon	GSA Break		5	EU-CITROEN-GSA-BREAK-WAGON-5D-01	HIGH		READY
2167_prefl	2167	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2167_facelift	2167	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2168_prefl	2168	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2168_facelift	2168	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2169	2169	Hatchback	Ypsilon (843 facelift)	843	3	EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	HIGH		READY
2170_prefl	2170	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2170_facelift	2170	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2171_prefl	2171	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2171_facelift	2171	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2172_prefl	2172	Hatchback	Visa		5	EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款前分支。	READY
2172_facelift	2172	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Ktype跨越1984年外廓变化，拆分为改款后分支。	READY
2173	2173	Hatchback	Visa		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	HIGH		READY
2174_phase1	2174	Hatchback	Visa Phase I GT		5	EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	MEDIUM	Visa GT初期Phase I外廓。	READY
2174_phase2	2174	Hatchback	Visa Phase II GT		5	EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	MEDIUM	Visa GT早期Phase II外廓。	READY
2174_facelift	2174	Hatchback	Visa Phase II GT		5	EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	Visa GT后期外廓。	READY
2175	2175	Hatchback	Visa GTI		5	EU-CITROEN-VISA-GTI-105-HATCHBACK-5D-01	HIGH		READY
2176	2176	Hatchback	Visa GTI		5	EU-CITROEN-VISA-GTI-115-HATCHBACK-5D-01	HIGH		READY
2177	2177	Hatchback	Visa		5	EU-CITROEN-VISA-DIESEL-HATCHBACK-5D-01	HIGH		READY
2178_prefl	2178	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2178_facelift	2178	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2179_prefl	2179	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2179_facelift	2179	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2180_prefl	2180	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2180_facelift	2180	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2181_prefl	2181	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2181_facelift	2181	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2182	2182	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2183_prefl	2183	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2183_facelift	2183	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2184_prefl	2184	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2184_facelift	2184	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2185_prefl	2185	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2185_facelift	2185	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2186_prefl	2186	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2186_facelift	2186	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2187	2187	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2188	2188	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2189	2189	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2190	2190	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2191	2191	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2192	2192	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2193	2193	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2194_prefl	2194	Hatchback	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase I分支。	READY
2194_facelift	2194	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH	Ktype跨越1986年7月外廓变化，拆分为Phase II分支。	READY
2195	2195	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2196	2196	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2197	2197	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
2198	2198	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	HIGH		READY
2199	2199	Hatchback	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	HIGH		READY
2200_facelift	2200	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2200_late	2200	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2201_prefl	2201	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	Phase I旅行车外廓。	READY
2201_facelift	2201	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2201_late	2201	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2202_prefl	2202	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	Phase I旅行车外廓。	READY
2202_facelift	2202	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2202_late	2202	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2203_facelift	2203	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2203_late	2203	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2204_facelift	2204	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2204_late	2204	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2205_facelift	2205	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2205_late	2205	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2206_prefl	2206	Wagon	BX I Phase I		5	EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	MEDIUM	输入起始期早于Break量产；保留已确认Phase I外廓。	READY
2206_facelift	2206	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2206_late	2206	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2207_facelift	2207	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2207_late	2207	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2208_facelift	2208	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2208_late	2208	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2209_facelift	2209	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	MEDIUM	Phase II早期旅行车外廓。	READY
2209_late	2209	Wagon	BX I Phase II		5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	MEDIUM	Phase II后期高度分支。	READY
2210_pre82	2210	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	MEDIUM	Ktype跨越1982年外廓宽度变化，拆分为改款前分支。	READY
2210_post82	2210	Sedan	CX I		4	EU-CITROEN-CX-I-1982-FACELIFT-SEDAN-4D-01	MEDIUM	Ktype跨越1982年外廓宽度变化，拆分为改款后分支。	READY
2211	2211	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2213	2213	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2214	2214	Sedan	CX I		4	EU-CITROEN-CX-I-GTI-SEDAN-4D-01	HIGH		READY
2215	2215	Sedan	CX I		4	EU-CITROEN-CX-I-GTI-SEDAN-4D-01	HIGH		READY
2216	2216	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2217	2217	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2218	2218	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2219	2219	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2220	2220	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2221	2221	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2222	2222	Sedan	CX I		4	EU-CITROEN-CX-I-SEDAN-4D-01	HIGH		READY
2223	2223	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2224	2224	Sedan	CX II		4	EU-CITROEN-CX-II-SEDAN-4D-01	HIGH		READY
2225_pre82	2225	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2225_post82	2225	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2226	2226	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	HIGH		READY
2227	2227	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	HIGH		READY
2228	2228	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2229_pre82	2229	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款前分支。	READY
2229_post82	2229	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	MEDIUM	Ktype跨越1982年外廓变化，拆分为改款后分支。	READY
2230	2230	Wagon	CX I Break		5	EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	HIGH		READY
2231	2231	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2232	2232	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2233	2233	Wagon	CX II Break		5	EU-CITROEN-CX-II-BREAK-WAGON-5D-01	HIGH		READY
2234	2234	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus外廓。	READY
2235	2235	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus外廓。	READY
2236	2236	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus外廓。	READY
2237	2237	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus外廓。	READY
2238	2238	MPV	C25 4x4			EU-CITROEN-C25-MINIBUS-4X4-SWB-LOWROOF-01	MEDIUM	四驱短轴低顶Minibus分支。	READY
2239	2239	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus外廓。	READY
2241_standard	2241	MPV	C25			EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	MEDIUM	标准短轴低顶Minibus分支。	READY
2241_highroof	2241	MPV	C25			EU-CITROEN-C25-MINIBUS-LWB-HIGHROOF-01	MEDIUM	涡轮柴油高顶16座Minibus分支。	READY
2243_van	2243	Van	C15			EU-CITROEN-C15-VAN-MPV-01	HIGH	厢式车分支。	READY
2243_mpv	2243	MPV	C15			EU-CITROEN-C15-VAN-MPV-01	MEDIUM	乘用衍生与厢式车共享外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2101-2200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-DYANE-HATCHBACK-5D-01	3905	1500	1540	Auto-Data	https://www.auto-data.net/en/citroen-dyane-i-phase-i-dyane-6-28hp-15199
EU-FIAT-508B-BALILLA-SEDAN-01	3145	1400	1530	Auta5P	https://auta5p.eu/muzea/museo_mille_miglia_2024/m1000m_07.php
EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	3864	1716	1721	Fiat Professional official press pack	https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	3959	1716	1721	Fiat Professional official press pack	https://www.media.stellantis.com/uk-en/fiat-professional/press/award-winning-new-fiat-fiorino-in-uk-press-pack
EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	3957	1716	1721	Fiat Professional Fiorino official brochure	https://glencom.co.uk/wp-content/uploads/2019/03/fiat-professional-fiorino-brochure.pdf
EU-CITROEN-LN-HATCHBACK-3D-01	3380	1520	1370	Auto-Data	https://www.auto-data.net/en/citroen-ln-0.6-32hp-15107
EU-CITROEN-LNA-1982-FACELIFT-HATCHBACK-3D-01	3427	1540	1373	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/533270/citroen_lna.html
EU-CITROEN-LNA-HATCHBACK-3D-01	3400	1520	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/55160/citroen_lna.html
EU-CITROEN-AX-PHASE-I-HATCHBACK-01	3495	1555	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/540620/citroen_ax_11_tre.html
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/1451225/citroen_ax_11_tge.html
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524	Fiat Professional Ducato Natural Power technical presentation;AutoScout24	https://cng.auto.pl/pliki/DUCATONATURAL.pdf;https://www.autoscout24.de/auto/technische-daten/fiat/ducato/ducato-maxi-35-natural-power-16000/
EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	3495	1596	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1451270/citroen_ax_sport.html
EU-CITROEN-AX-GT-HATCHBACK-3D-01	3495	1596	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/62720/citroen_ax_gt.html
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-2.0-jtdm-140hp-17467
EU-CITROEN-GS-HATCHBACK-4D-01	4120	1608	1349	Auto-Data	https://www.auto-data.net/en/citroen-gs-1.2-59hp-14936
EU-CITROEN-GSA-HATCHBACK-5D-01	4181	1626	1349	Auto-Data	https://www.auto-data.net/en/citroen-gsa-a-1.3-65hp-14937
EU-CITROEN-GS-BREAK-WAGON-5D-01	4120	1608	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1973/2030315/citroen_gs_1220_break_club.html
EU-CITROEN-GSA-BREAK-WAGON-5D-01	4143	1626	1349	Auto-Data	https://www.auto-data.net/en/citroen-gsa-break-a-1.3-65hp-14931
EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	3690	1530	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/534140/citroen_visa.html
EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/534275/citroen_visa_11_e.html
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530	Auto-Data	https://www.auto-data.net/en/lancia-ypsilon-843-facelift-2006-1.2-8v-69hp-47149
EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	3690	1535	1408	Auto-Data	https://www.auto-data.net/en/citroen-visa-phase-i-14-gt-79hp-14915
EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	3690	1530	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/55190/citroen_visa_gt.html
EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/534350/citroen_visa_gt.html
EU-CITROEN-VISA-GTI-105-HATCHBACK-5D-01	3725	1540	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/52970/citroen_visa_gti.html
EU-CITROEN-VISA-GTI-115-HATCHBACK-5D-01	3725	1600	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1449830/citroen_visa_gti_115ch.html
EU-CITROEN-VISA-DIESEL-HATCHBACK-5D-01	3725	1550	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/63830/citroen_visa_17_rd_5-speed.html
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	4230	1650	1358	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/28325/citroen_bx.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/539165/citroen_bx_16_trs_cat.html
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/50765/citroen_bx_19_gt.html
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	4237	1682	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/62330/citroen_bx_4x4.html
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/539960/citroen_bx_break_19_rd.html
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/539630/citroen_bx_break_19_tzs.html
EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	4399	1660	1431	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/54530/citroen_bx_break_19_rd.html
EU-CITROEN-CX-I-SEDAN-4D-01	4659	1734	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/532730/citroen_cx_2000_reflex.html
EU-CITROEN-CX-I-1982-FACELIFT-SEDAN-4D-01	4659	1770	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/533090/citroen_cx_25_d.html
EU-CITROEN-CX-II-SEDAN-4D-01	4650	1770	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/540065/citroen_cx_25_gti.html
EU-CITROEN-CX-I-GTI-SEDAN-4D-01	4659	1755	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/532910/citroen_cx_2400_gti.html
EU-CITROEN-CX-I-BREAK-WAGON-5D-01	4922	1734	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/38840/citroen_cx_break_2000_confort.html
EU-CITROEN-CX-I-BREAK-1982-FACELIFT-WAGON-5D-01	4930	1770	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/540170/citroen_cx_break_25_rd_5-speed.html
EU-CITROEN-CX-II-BREAK-WAGON-5D-01	4930	1770	1460	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/540080/citroen_cx_break_25_tri.html
EU-CITROEN-C25-MINIBUS-SWB-LOWROOF-01	4759	1965	2096	France Galerie;Citroën C25 workshop manual	https://www.france-galerie.com/content/32-dimensions-citroen;https://www.scribd.com/document/806058588/Citroen-C25-Fiat-Ducato-Talbot-Express
EU-CITROEN-C25-MINIBUS-4X4-SWB-LOWROOF-01	4759	1965	2096	La Centrale;France Galerie;Citroën C25 workshop manual	https://www.lacentrale.fr/fiche-technique-voiture-citroen-c25-d%2B1400%2Bcourt%2B4x4-1992.html;https://www.france-galerie.com/content/32-dimensions-citroen;https://www.scribd.com/document/806058588/Citroen-C25-Fiat-Ducato-Talbot-Express
EU-CITROEN-C25-MINIBUS-LWB-HIGHROOF-01	5489	1965	2420	Commercial Motor Archive;France Galerie;Citroën C25 workshop manual	https://archive.commercialmotor.com/article/17th-december-1987/14/citroen-gets-heavy-on-c25;https://www.france-galerie.com/content/32-dimensions-citroen;https://www.scribd.com/document/806058588/Citroen-C25-Fiat-Ducato-Talbot-Express
EU-CITROEN-C15-VAN-MPV-01	3995	1636	1801	Citroën Origins;Drom	https://www.citroenorigins.co.uk/en/cars/c15;https://www.drom.ru/catalog/citroen/c15/specs/dimensions/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2101-2200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.france-galerie.com/content/32-dimensions-citroen "Dimensions utilitaires Citroën : Berlingo, Jumpy, Jumper"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2101-2200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2101-2200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2748 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（689 行）
