# 任务：all 第 2801-2900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0029__06d95cf9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2801-2900 行

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
all 第 2801-2900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Seat	Marbella	0.9	Schrägheck	Frontantrieb	Benzin	29	40	Jan 1987	Dec 1993	2024-03-01	2887
Seat	Marbella	0.9 CAT	Schrägheck	Frontantrieb	Benzin	29	40	Jan 1990	Nov 1996	2024-03-01	2888
Seat	Marbella	0.8	Kasten/Schrägheck	Frontantrieb	Benzin	25	34	Jan 1987	Dec 1993	2024-03-01	2889
Seat	Marbella	0.9	Kasten/Schrägheck	Frontantrieb	Benzin	29	40	Jan 1987	Dec 1993	2024-03-01	2890
Seat	Marbella	0.9 CAT	Kasten/Schrägheck	Frontantrieb	Benzin	29	40	Jan 1987	Dec 1993	2024-03-01	2891
Seat	600	0.8	Stufenheck	Heckantrieb	Benzin	17	23	Sep 1963	Apr 1970	2024-03-01	2892
Seat	133	0.8	Schrägheck	Heckantrieb	Benzin	25	34	May 1974	Nov 1979	2024-03-01	2893
Lexus	Is ii	200d	Stufenheck	Heckantrieb	Diesel	110	150	Jul 2010	Jul 2012	2024-03-01	2894
Seat	Terra	1.3 D	Kasten/Kombi	Frontantrieb	Diesel	33	45	Mar 1990	Feb 1992	2024-03-01	2896
Seat	Terra	1.4 D	Kasten/Kombi	Frontantrieb	Diesel	35	48	Oct 1990	Feb 1992	2024-03-01	2897
Citroën	C5	1.6 VTI 120	Stufenheck	Frontantrieb	Benzin	88	120	Jul 2010	Jun 2015	2024-07-01	2898
Citroën	C5	2.2 HDI 200	Stufenheck	Frontantrieb	Diesel	150	204	Jul 2010	Jun 2015	2024-07-01	2899
Seat	Terra	1.3 D	Kombi	Frontantrieb	Diesel	33	45	Mar 1990	Dec 1994	2024-03-01	2900
Seat	Terra	1.4 D	Kombi	Frontantrieb	Diesel	35	48	Oct 1990	Dec 1995	2024-03-01	2901
Seat	Toledo	1.6 I	Schrägheck	Frontantrieb	Benzin	54	73	May 1991	Mar 1999	2024-03-01	2902
Seat	Toledo	1.8 16V	Schrägheck	Frontantrieb	Benzin	98	133	May 1991	Mar 1999	2024-03-01	2903
Seat	Toledo	1.9 D	Schrägheck	Frontantrieb	Diesel	50	68	May 1991	Mar 1999	2024-03-01	2904
Seat	Toledo	1.9 TD	Schrägheck	Frontantrieb	Diesel	55	75	May 1991	Mar 1999	2024-03-01	2905
Seat	Toledo	1.6 I	Schrägheck	Frontantrieb	Benzin	52	71	May 1991	Dec 1993	2024-03-01	2906
Seat	Toledo	1.8 I	Schrägheck	Frontantrieb	Benzin	65	88	May 1991	Dec 1996	2024-03-01	2907
Seat	Toledo	1.8 16V	Schrägheck	Frontantrieb	Benzin	92	125	May 1991	Mar 1999	2024-03-01	2908
Seat	Toledo	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	May 1991	Mar 1999	2024-03-01	2909
Seat	Ibiza ii	1.9 SDI	Schrägheck	Frontantrieb	Diesel	47	64	Aug 1996	Aug 1999	2024-03-01	2910
Seat	Ibiza ii	1.9 TD	Schrägheck	Frontantrieb	Diesel	55	75	Mar 1993	Aug 1996	2024-03-01	2911
Seat	Ibiza ii	1	Schrägheck	Frontantrieb	Benzin	33	45	Mar 1993	Sep 1996	2024-03-01	2912
Seat	Ibiza ii	1.3 I	Schrägheck	Frontantrieb	Benzin	40	54	Mar 1993	Aug 1999	2024-03-01	2913
Seat	Ibiza ii	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1993	Feb 2002	2024-03-01	2914
Seat	Ibiza ii	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1993	Aug 1999	2024-03-01	2915
Seat	Ibiza ii	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	Mar 1993	Aug 1999	2024-03-01	2916
Saab	90	2	Stufenheck	Frontantrieb	Benzin	74	100	Aug 1984	Aug 1987	2024-03-01	2917
Citroën	C5	1.6 VTI 120	Kombi	Frontantrieb	Benzin	88	120	Jul 2010	Jun 2015	2024-07-01	2918
Saab	99	2.0 GL	Stufenheck	Frontantrieb	Benzin	74	100	Sep 1974	Dec 1984	2024-03-01	2919
Saab	900 i combi coupe	2.0 C	Schrägheck	Frontantrieb	Benzin	74	101	Sep 1979	Dec 1988	2024-03-01	2920
Saab	900 i combi coupe	2.0 C	Schrägheck	Frontantrieb	Benzin	79	107	Sep 1978	Aug 1984	2024-03-01	2921
Saab	900 i combi coupe	2.0 I	Schrägheck	Frontantrieb	Benzin	81	110	Sep 1980	Aug 1990	2026-01-01	2922
Saab	900 i combi coupe	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	Nov 1980	Dec 1988	2024-03-01	2923
Saab	900 i combi coupe	2.0 Turbo-16	Schrägheck	Frontantrieb	Benzin	118	160	Nov 1985	Jun 1994	2024-03-01	2924
Saab	900 i combi coupe	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	107	146	Sep 1978	Jul 1985	2024-03-01	2925
Saab	900 i combi coupe	2.0 Turbo-16 S	Schrägheck	Frontantrieb	Benzin	129	175	Feb 1984	Dec 1988	2024-03-01	2926
Saab	900 i combi coupe	2.0 -16	Schrägheck	Frontantrieb	Benzin	93	126	Jan 1989	Aug 1992	2024-03-01	2927
Saab	900 i combi coupe	2.0 S Turbo-16	Schrägheck	Frontantrieb	Benzin	104	141	Sep 1991	Jul 1993	2024-03-01	2928
Saab	900 i combi coupe	2.0 Turbo-16	Schrägheck	Frontantrieb	Benzin	132	180	Jan 1993	Jun 1994	2024-03-01	2929
Saab	9000	2.0 -16	Schrägheck	Frontantrieb	Benzin	92	125	Dec 1985	Dec 1988	2024-03-01	2930
Saab	9000	2.0 -16	Schrägheck	Frontantrieb	Benzin	94	128	Dec 1985	Aug 1988	2024-03-01	2931
Saab	9000	2.0 -16 Turbo	Schrägheck	Frontantrieb	Benzin	118	160	Sep 1984	Aug 1993	2024-03-01	2932
Saab	9000	2.0 -16 Turbo	Schrägheck	Frontantrieb	Benzin	129	175	Sep 1984	Dec 1991	2024-03-01	2933
Saab	9000	2.0 -16 CS	Schrägheck	Frontantrieb	Benzin	94	128	Jan 1989	Dec 1998	2024-03-01	2934
Citroën	C5	2.2 HDI 200	Kombi	Frontantrieb	Diesel	150	204	Jul 2010	Jun 2015	2024-07-01	2935
Porsche	911	2.2 T	Coupe	Heckantrieb	Benzin	92	125	Jan 1970	Dec 1972	2024-03-01	2936
Saab	9000	2.0 -16 ND Turbo	Schrägheck	Frontantrieb	Benzin	110	150	Sep 1993	Dec 1998	2024-03-01	2937
Porsche	911	2.2 T	Targa	Heckantrieb	Benzin	92	125	Jan 1970	Dec 1972	2024-03-01	2938
Saab	9000	2.0 -16 Turbo	Schrägheck	Frontantrieb	Benzin	120	163	May 1988	Aug 1993	2024-03-01	2939
Land Rover	Discovery iv	5.0 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	276	375	Sep 2009	Dec 2018	2024-03-01	2940
Porsche	911	2.3 T	Coupe	Heckantrieb	Benzin	96	130	Jan 1972	Dec 1973	2024-03-01	2941
Porsche	911	2.3 T	Targa	Heckantrieb	Benzin	96	130	Jan 1972	Dec 1973	2024-03-01	2942
Porsche	911	2.7	Coupe	Heckantrieb	Benzin	110	150	Sep 1973	Aug 1975	2024-03-01	2943
Porsche	911	2.7	Targa	Heckantrieb	Benzin	110	150	Sep 1973	Aug 1975	2024-03-01	2944
Porsche	911	2.7	Targa	Heckantrieb	Benzin	121	165	Sep 1975	Jun 1977	2024-03-01	2945
Saab	9000	2.0 -16 Turbo CS	Schrägheck	Frontantrieb	Benzin	136	185	Sep 1988	Dec 1998	2024-03-01	2946
Saab	9000	2.3 -16 CS	Schrägheck	Frontantrieb	Benzin	107	146	Sep 1989	Dec 1998	2024-03-01	2947
Porsche	911	2.7	Coupe	Heckantrieb	Benzin	121	165	Sep 1975	Jun 1977	2024-03-01	2948
Porsche	911	3.0 SC Carrera	Targa	Heckantrieb	Benzin	132	180	Jul 1977	Jun 1980	2024-03-01	2949
Porsche	911	3.0 SC Carrera	Coupe	Heckantrieb	Benzin	132	180	Jul 1977	Jun 1980	2024-03-01	2950
Porsche	911	3.0 SC Carrera	Coupe	Heckantrieb	Benzin	138	188	Sep 1979	Jun 1980	2024-03-01	2951
Porsche	911	3.0 SC Carrera	Targa	Heckantrieb	Benzin	138	188	Sep 1979	Jun 1980	2024-03-01	2952
Porsche	911	3.0 SC Carrera	Coupe	Heckantrieb	Benzin	147	200	Sep 1975	Jun 1977	2024-03-01	2953
Porsche	911	3.0 SC Carrera	Targa	Heckantrieb	Benzin	147	200	Sep 1975	Jun 1977	2024-03-01	2954
Porsche	911	3.0 SC	Coupe	Heckantrieb	Benzin	150	204	Aug 1980	Jul 1983	2024-03-01	2955
Porsche	911	3.0 SC	Cabriolet	Heckantrieb	Benzin	150	204	Aug 1982	Jul 1983	2024-03-01	2956
Porsche	911	3.2 SC Carrera	Cabriolet	Heckantrieb	Benzin	152	207	Oct 1984	Aug 1989	2024-03-01	2957
Porsche	911	3.2	Coupe	Heckantrieb	Benzin	160	218	Aug 1986	Aug 1989	2024-03-01	2958
Porsche	911	3.2 Carrera Speedster	Cabriolet	Heckantrieb	Benzin	160	218	Aug 1986	Aug 1989	2024-03-01	2959
Porsche	911	3.2 SC Carrera	Coupe	Heckantrieb	Benzin	170	231	Aug 1983	Aug 1989	2024-03-01	2960
Porsche	911	3.2 SC Carrera	Cabriolet	Heckantrieb	Benzin	170	231	Aug 1983	Aug 1984	2024-03-01	2961
Land Rover	Range rover sport i	3.0 D 4X4	SUV	Allrad	Diesel	155	211	May 2010	Mar 2013	2024-03-01	2962
Porsche	911	3.3 SC Turbo	Coupe	Heckantrieb	Benzin	221	301	Sep 1977	Jun 1987	2024-03-01	2964
Porsche	911	3.3 Turbo	Coupe	Heckantrieb	Benzin	221	300	Jun 1986	Aug 1989	2024-03-01	2965
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	184	250	May 1989	May 1994	2024-03-01	2966
Saab	9000	2.3 -16 CSE	Schrägheck	Frontantrieb	Benzin	108	147	Sep 1993	Dec 1998	2024-03-01	2967
Saab	9000	2.3 -16 CSE ECO Power	Schrägheck	Frontantrieb	Benzin	125	170	Sep 1993	Dec 1998	2024-03-01	2968
Saab	9000	2.3 -16 Turbo	Schrägheck	Frontantrieb	Benzin	143	195	Sep 1990	Dec 1998	2024-03-01	2969
Saab	9000	2.3 -16 Turbo CSE	Schrägheck	Frontantrieb	Benzin	147	200	Sep 1993	Dec 1998	2024-03-01	2970
Saab	9000	2.3 -16 Aero CS	Schrägheck	Frontantrieb	Benzin	162	220	Feb 1993	Dec 1998	2024-03-01	2971
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	184	250	Jul 1989	Sep 1993	2024-03-01	2972
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	184	250	Jul 1989	May 1994	2024-03-01	2973
Porsche	924	2	Coupe	Heckantrieb	Benzin	92	125	Nov 1975	Aug 1989	2024-03-01	2974
Porsche	924	2.0 Turbo	Coupe	Heckantrieb	Benzin	125	170	Nov 1978	Jun 1980	2024-03-01	2975
Saab	9000	2.3 -16 Aero CS	Schrägheck	Frontantrieb	Benzin	165	224	Feb 1993	Dec 1998	2024-03-01	2976
Porsche	924	2.5 S	Coupe	Heckantrieb	Benzin	110	150	Sep 1985	Jul 1987	2024-03-01	2977
Saab	900 i	2.0 C	Stufenheck	Frontantrieb	Benzin	79	107	Nov 1980	Aug 1984	2024-03-01	2978
Porsche	924	2.5 S	Coupe	Heckantrieb	Benzin	118	160	Aug 1987	Jul 1988	2024-03-01	2979
Porsche	944	2.5	Coupe	Heckantrieb	Benzin	110	150	Jan 1985	Jul 1987	2024-03-01	2981
Porsche	944	2.5	Coupe	Heckantrieb	Benzin	118	160	Aug 1987	Dec 1990	2024-03-01	2982
Porsche	944	2.5	Coupe	Heckantrieb	Benzin	120	163	Jun 1981	Jul 1987	2024-03-01	2983
Porsche	944	2.5 S	Coupe	Heckantrieb	Benzin	140	190	Aug 1986	Jul 1988	2024-03-01	2984
Porsche	944	2.5 Turbo	Coupe	Heckantrieb	Benzin	162	220	Aug 1985	Jul 1988	2024-03-01	2985
Porsche	944	2.5 Turbo	Coupe	Heckantrieb	Benzin	184	250	Sep 1987	Jul 1991	2024-03-01	2986
Porsche	944	2.7	Coupe	Heckantrieb	Benzin	121	165	Nov 1988	Aug 1989	2024-03-01	2987
Porsche	944	3.0 S2	Coupe	Heckantrieb	Benzin	155	211	Dec 1988	Jul 1991	2024-03-01	2988
Porsche	944	3.0 S2	Cabriolet	Heckantrieb	Benzin	155	211	Dec 1988	Jul 1991	2024-03-01	2989


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 **13 个尺寸组**，完成 Marbella、600 D、133、Terra、Toledo I、Saab 90、Saab 99、Discovery IV 和 Range Rover Sport I 的映射。
* Terra 的封闭货厢 Van 与侧窗 Kombi 虽三维一致，但属于不同物理车身，分别建组；Ktype 2896、2897 拆分为两个派生映射。
* Saab 99 的 Ktype 2919 已确认覆盖两门/四门及早期/后期保险杠外廓，拆分为四条映射。
* Toledo I 改款前后外廓尺寸不变，2902–2909 复用同一尺寸组；资料明确其为五门 Hatchback/Liftback。([汽车数据][1])
* Ibiza II 已发现原型、1996 修订和 1999 改款尺寸差异，且资料同时覆盖三门和五门；当前先保留基础 PENDING 行，避免创建无法与生产月份对齐的猜测性分支。([汽车数据][2])
* Lexus IS 200d 与 Citroën C5 暂未闭合，分别受多高度配置、悬架高度以及宽度来源冲突阻塞。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 已展开处理 Ktype：35
* READY Ktype：20
* READY 映射行：25
* PENDING Ktype／映射行：15
* 尚未展开 Ktype：65
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2887	2887	Hatchback	Marbella (28)		3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH	三门掀背物理外廓。	READY
2888	2888	Hatchback	Marbella (28)		3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH	三门掀背物理外廓。	READY
2889	2889	Hatchback	Marbella (28)		3		LOW	Kasten/Schrägheck标注尚不能确认是否为Marbella商用改装或Terra车身。	PENDING: 商用车身边界未确认
2890	2890	Hatchback	Marbella (28)		3		LOW	Kasten/Schrägheck标注尚不能确认是否为Marbella商用改装或Terra车身。	PENDING: 商用车身边界未确认
2891	2891	Hatchback	Marbella (28)		3		LOW	Kasten/Schrägheck标注尚不能确认是否为Marbella商用改装或Terra车身。	PENDING: 商用车身边界未确认
2892	2892	Sedan	600 D		2	EU-SEAT-600-D-SEDAN-2D-01	HIGH	两门Berlina物理外廓。	READY
2893	2893	Sedan	133		2	EU-SEAT-133-SEDAN-2D-01	HIGH	可靠资料将该两门车身归类为Berlina/Sedan。	READY
2894	2894	Sedan	IS II facelift 2010	XE20	4		MEDIUM	资料给出多高度配置，尚未确认200d对应分支。	PENDING: 200d高度配置分支未确认
2896_van	2896	Van	Terra		3	EU-SEAT-TERRA-VAN-3D-01	HIGH	Kasten/Kombi输入拆分为封闭货厢分支。	READY
2896_kombi	2896	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	Kasten/Kombi输入拆分为侧窗Kombi分支。	READY
2897_van	2897	Van	Terra		3	EU-SEAT-TERRA-VAN-3D-01	HIGH	Kasten/Kombi输入拆分为封闭货厢分支。	READY
2897_kombi	2897	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	Kasten/Kombi输入拆分为侧窗Kombi分支。	READY
2898	2898	Sedan	C5 II	X7	4		MEDIUM	金属弹簧与Hydractive车身高度分支尚未闭合。	PENDING: 悬架高度分支未确认
2899	2899	Sedan	C5 II	X7	4		LOW	车身宽度来源冲突且悬架高度分支尚未闭合。	PENDING: 宽度冲突与高度分支未解决
2900	2900	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	侧窗Kombi物理外廓。	READY
2901	2901	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	侧窗Kombi物理外廓。	READY
2902	2902	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2903	2903	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2904	2904	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2905	2905	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2906	2906	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2907	2907	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2908	2908	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2909	2909	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2910	2910	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2911	2911	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2912	2912	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2913	2913	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2914	2914	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2915	2915	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2916	2916	Hatchback	Ibiza II	6K			LOW	候选为原型、1996修订及1999改款外廓，生产月与门数边界尚未对齐。	PENDING: 改款月边界与门数分支未闭合
2917	2917	Sedan	90		2	EU-SAAB-90-SEDAN-2D-01	HIGH	两门Sedan物理外廓。	READY
2918	2918	Wagon	C5 II	X7	5		MEDIUM	金属弹簧与Hydractive车身高度分支尚未闭合。	PENDING: 悬架高度分支未确认
2919_2dr_early	2919	Sedan	99		2	EU-SAAB-99-SEDAN-2D-EARLY-01	MEDIUM	两门早期保险杠外廓。	READY
2919_4dr_early	2919	Sedan	99		4	EU-SAAB-99-SEDAN-4D-EARLY-01	MEDIUM	四门早期保险杠外廓。	READY
2919_2dr_late	2919	Sedan	99		2	EU-SAAB-99-SEDAN-2D-LATE-01	MEDIUM	两门后期保险杠外廓。	READY
2919_4dr_late	2919	Sedan	99		4	EU-SAAB-99-SEDAN-4D-LATE-01	MEDIUM	四门后期保险杠外廓。	READY
2935	2935	Wagon	C5 II	X7	5		LOW	车身宽度来源冲突且悬架高度分支尚未闭合。	PENDING: 宽度冲突与高度分支未解决
2940	2940	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	HIGH	五门标准轴距SUV外廓。	READY
2962	2962	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	HIGH	五门SUV物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	3475	1500	1445	Auto-Data	https://www.auto-data.net/en/seat-marbella-28-0.8-34hp-13527
EU-SEAT-600-D-SEDAN-2D-01	3295	1380	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/3060335/seat_600_d.html
EU-SEAT-133-SEDAN-2D-01	3451	1421	1328	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/40040/seat_133_n.html
EU-SEAT-TERRA-VAN-3D-01	3869	1490	1895	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3065495/seat_terra_van_1_3_diesel.html
EU-SEAT-TERRA-MPV-3D-01	3869	1490	1895	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3065420/seat_terra_kombi_1_3_diesel.html
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424	Auto-Data;Automobile-Catalog	https://www.auto-data.net/en/seat-toledo-i-1l-generation-2913;https://www.automobile-catalog.com/car/1998/3065705/seat_toledo_1_6i.html
EU-SAAB-90-SEDAN-2D-01	4579	1690	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/3027260/saab_90_4-speed.html
EU-SAAB-99-SEDAN-2D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/3019100/saab_99_gl_2-door.html
EU-SAAB-99-SEDAN-4D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/3019790/saab_99_gl_4-door.html
EU-SAAB-99-SEDAN-2D-LATE-01	4477	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/3019985/saab_99_gl_2-door_5-speed.html
EU-SAAB-99-SEDAN-4D-LATE-01	4477	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/3020000/saab_99_gl_4-door.html
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	4829	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1616330/land_rover_discovery_4_3_0_tdv6_commercial.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1405160/range_rover_sport_3_0_tdv6_se.html
```

Marbella 页面明确记录三门车身及 3475×1500×1445 mm；Toledo 的改款前后资料均支持 4321×1662×1424 mm，且宽度为不含后视镜口径。([汽车数据][4])

600、133、Terra Van/Kombi 的尺寸及物理分支由对应车型页和 SEAT 历史资料交叉确认。([汽车目录][5])

Saab 99 的早期、后期长度差异以及两门、四门车身分别保留为独立尺寸组；Discovery IV 与 Range Rover Sport I 使用不含后视镜宽度的直接车型页。([汽车目录][6])

## 下一步优先处理

1. 闭合 Ibiza II 三门／五门及 1993、1996、1999 三个外廓阶段与各 Ktype 生产月份的对应关系。
2. 处理 Saab 900 Combi Coupé、Saab 900 Sedan 和 Saab 9000 CC／CS／CSE 的车身分支。
3. 按 911 长车头早期车、G 系列、930 Turbo、964，以及 Coupe／Targa／Cabriolet／Speedster 聚类处理 Porsche 911。
4. 闭合 Porsche 924、944 Coupe／Cabriolet，并解决 Lexus IS 200d、Citroën C5 的高度及宽度冲突。
5. 最后回查 Marbella 商用标注是否实际指向 Terra 或独立改装车身。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-toledo-i-1l-generation-2913 "Seat Toledo I (1L) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/seat-ibiza-ii-1.9-sdi-64hp-13508 "Seat Ibiza II 1.9 SDI (64 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/lexus-is-ii-xe20-facelift-2010-200d-150hp-50837 "https://www.auto-data.net/en/lexus-is-ii-xe20-facelift-2010-200d-150hp-50837"
[4]: https://www.auto-data.net/en/seat-marbella-28-0.8-34hp-13527 "Seat Marbella (28) 0.8 (34 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.automobile-catalog.com/car/1968/3060335/seat_600_d.html "https://www.automobile-catalog.com/car/1968/3060335/seat_600_d.html"
[6]: https://www.automobile-catalog.com/car/1978/3019100/saab_99_gl_2-door.html "https://www.automobile-catalog.com/car/1978/3019100/saab_99_gl_2-door.html"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Lexus IS II 200d 已按欧洲规格闭合为 ALE20 四门轿车外廓，原 PENDING 映射转为 READY。([汽车目录][1])
* Saab 9000 已建立 CC、CS/CSE 和 CS Aero 三个尺寸组；Aero 因外部套件和降低车高单独建组。仅 Ktype 2969 因生产期横跨 CC/CS 且名称未限定车身继续 PENDING。([汽车目录][2])
* Porsche 911 已闭合 G Series 窄体、Carrera/SC 宽体、930 Turbo，以及欧洲规格 964 Coupe/Cabriolet。早期 F Series 的年度长度变化和 Speedster 低风挡外廓继续 PENDING。([汽车目录][3])
* Porsche 924 已闭合普通/931 Turbo 与 924 S 两种高度外廓；Porsche 944 已闭合标准车头、Turbo/S2 空力车头和 S2 Cabriolet 三组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 已展开处理 Ktype：89
* READY Ktype：68
* READY 映射行：73
* PENDING Ktype／映射行：21
* 尚未展开 Ktype：11
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2894	2894	Sedan	IS II facelift 2010	ALE20	4	EU-LEXUS-IS-II-ALE20-FACELIFT-SEDAN-4D-01	HIGH	200d后驱四门轿车外廓。	READY
2930	2930	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	HIGH	原始CC五门外廓。	READY
2931	2931	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	HIGH	原始CC五门外廓。	READY
2932	2932	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	MEDIUM	未标注CS，按原始CC五门外廓落组。	READY
2933	2933	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	HIGH	原始CC五门外廓。	READY
2934	2934	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	VariantName明确CS；输入起始月存在上游早录。	READY
2936	2936	Coupe	911 F Series	911	2		MEDIUM	生产期覆盖多个前后保险杠长度阶段，尚未闭合派生边界。	PENDING: 早期Coupe长度阶段分界未闭合
2937	2937	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	1993年后五门CS外廓。	READY
2938	2938	Targa	911 F Series	911	2		MEDIUM	生产期覆盖多个早期Targa长度阶段，尚未闭合派生边界。	PENDING: 早期Targa长度阶段分界未闭合
2939	2939	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	MEDIUM	未标注CS，按原始CC五门外廓落组。	READY
2941	2941	Coupe	911 F Series	911	2		MEDIUM	1972至1973生产期覆盖不同保险杠长度阶段。	PENDING: 2.3 T Coupe阶段边界未闭合
2942	2942	Targa	911 F Series	911	2		MEDIUM	1972至1973生产期覆盖不同保险杠长度阶段。	PENDING: 2.3 T Targa阶段边界未闭合
2943	2943	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	HIGH	G Series窄体Coupe外廓。	READY
2944	2944	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	HIGH	G Series窄体Targa外廓。	READY
2945	2945	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	HIGH	G Series窄体Targa外廓。	READY
2946	2946	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	VariantName明确CS五门外廓。	READY
2947	2947	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	VariantName明确CS五门外廓。	READY
2948	2948	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	HIGH	G Series窄体Coupe外廓。	READY
2949	2949	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2950	2950	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2951	2951	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2952	2952	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2953	2953	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2954	2954	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2955	2955	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	911 SC宽体Coupe外廓。	READY
2956	2956	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	911 SC Cabriolet外廓。	READY
2957	2957	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	Carrera 3.2 Cabriolet外廓。	READY
2958	2958	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.2 Coupe外廓。	READY
2959	2959	Convertible	911 G Series	911	2		MEDIUM	Speedster低风挡和后部罩盖形成独立外廓。	PENDING: Speedster三维尚未闭合
2960	2960	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.2 Coupe外廓。	READY
2961	2961	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	Carrera 3.2 Cabriolet外廓。	READY
2964	2964	Coupe	911 Turbo 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体Coupe外廓。	READY
2965	2965	Coupe	911 Turbo 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体Coupe外廓。	READY
2966	2966	Convertible	911 964	964	2	EU-PORSCHE-911-964-CONVERTIBLE-01	HIGH	欧洲规格964 Carrera 4 Cabriolet外廓。	READY
2967	2967	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE属于CS五门外廓。	READY
2968	2968	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE Eco Power属于CS五门外廓。	READY
2969	2969	Hatchback	9000			MEDIUM	生产期横跨CC与CS，名称未限定具体五门车身。	PENDING: CC与CS物理分支未闭合
2970	2970	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE属于CS五门外廓。	READY
2971	2971	Hatchback	9000 CS Aero	CS	5	EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	HIGH	Aero外部套件与降低车高形成独立外廓。	READY
2972	2972	Coupe	911 964	964	2	EU-PORSCHE-911-964-COUPE-01	HIGH	欧洲规格964 Carrera 2 Coupe外廓。	READY
2973	2973	Convertible	911 964	964	2	EU-PORSCHE-911-964-CONVERTIBLE-01	HIGH	欧洲规格964 Carrera 2 Cabriolet外廓。	READY
2974	2974	Coupe	924	924	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	标准924三门Coupe外廓。	READY
2975	2975	Coupe	924 Turbo	931	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	931 Turbo与标准924共用外部尺寸边界。	READY
2976	2976	Hatchback	9000 CS Aero	CS	5	EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	HIGH	Aero外部套件与降低车高形成独立外廓。	READY
2977	2977	Coupe	924 S	924S	3	EU-PORSCHE-924-S-COUPE-3D-01	HIGH	924 S三门Coupe外廓。	READY
2979	2979	Coupe	924 S	924S	3	EU-PORSCHE-924-S-COUPE-3D-01	HIGH	924 S三门Coupe外廓。	READY
2981	2981	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	HIGH	标准车头944三门Coupe外廓。	READY
2982	2982	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	MEDIUM	发动机更新未改变标准944物理外廓。	READY
2983	2983	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	HIGH	标准车头944三门Coupe外廓。	READY
2984	2984	Coupe	944 S	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	MEDIUM	944 S沿用标准944外部车身。	READY
2985	2985	Coupe	944 Turbo	951	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	951 Turbo空力车头三门Coupe外廓。	READY
2986	2986	Coupe	944 Turbo	951	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	951 Turbo空力车头三门Coupe外廓。	READY
2987	2987	Coupe	944	944	3		MEDIUM	2.7车型资料存在标准车头长度阶段差异。	PENDING: 2.7 Coupe长度边界未闭合
2988	2988	Coupe	944 S2	944	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	S2 Coupe采用Turbo式空力外廓。	READY
2989	2989	Convertible	944 S2	944	2	EU-PORSCHE-944-S2-CONVERTIBLE-2D-01	HIGH	S2 Cabriolet独立开放车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LEXUS-IS-II-ALE20-FACELIFT-SEDAN-4D-01	4585	1800	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1604795/lexus_is_200d.html
EU-SAAB-9000-CC-HATCHBACK-5D-01	4620	1764	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/54200/saab_9000_ie_16.html
EU-SAAB-9000-CS-HATCHBACK-5D-01	4761	1778	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/3029690/saab_9000_cs_cse_2_3_turbo.html
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2649485/porsche_911_coupe_4-speed.html
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2649605/porsche_911_targa_4-speed.html
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2650535/porsche_911_carrera_3_0_targa_5-speed.html
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2650295/porsche_911_carrera_3_0_coupe_4-speed.html
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/41330/porsche_911_sc_cabriolet.html
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2681630/porsche_911_turbo.html
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2865080/porsche_911_carrera_4_cabriolet.html
EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	4761	1806	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3029735/saab_9000_aero.html
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2865005/porsche_911_carrera_2_coupe.html
EU-PORSCHE-924-COUPE-3D-EARLY-01	4212	1685	1270	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/2683265/porsche_924.html
EU-PORSCHE-924-S-COUPE-3D-01	4212	1685	1275	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/31610/porsche_924_s.html
EU-PORSCHE-944-BASE-COUPE-3D-01	4200	1735	1275	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/2683910/porsche_944.html
EU-PORSCHE-944-AERO-COUPE-3D-01	4290	1735	1275	Automobile-Catalog Porsche 944 Turbo;Automobile-Catalog Porsche 944 S2	https://www.automobile-catalog.com/car/1989/2684285/porsche_944_turbo.html;https://www.automobile-catalog.com/car/1990/2684330/porsche_944_s2.html
EU-PORSCHE-944-S2-CONVERTIBLE-2D-01	4290	1735	1275	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/2684360/porsche_944_s2_cabrio.html
```

## 下一步优先处理

1. 闭合 Saab 900 Combi Coupé 的三门／五门、前期／改款外廓，以及 Ktype 2978 的两门／四门 Sedan 边界。
2. 批量解决 Ibiza II 的三门／五门和 1993、1996、1999 外廓阶段。
3. 处理 Citroën C5 金属弹簧／Hydractive 高度分支及宽度冲突。
4. 闭合 Marbella Kasten、早期 Porsche 911、911 Speedster、Saab 9000 Ktype 2969 和 Porsche 944 Ktype 2987。
5. PENDING 清零后仅执行一次机械闭合检查并生成两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2011/1604795/lexus_is_200d.html?utm_source=chatgpt.com "2011 Lexus IS 200d Specs Review (110 kW / 150 PS / 148 ..."
[2]: https://www.automobile-catalog.com/car/1986/54200/saab_9000_ie_16.html "https://www.automobile-catalog.com/car/1986/54200/saab_9000_ie_16.html"
[3]: https://www.automobile-catalog.com/car/1974/2649485/porsche_911_coupe_4-speed.html?utm_source=chatgpt.com "1974 Porsche 911 Coupe 4-speed Specs Review (110 kW / 150 PS / 148 hp) (up to August 1974 for Europe )"
[4]: https://www.automobile-catalog.com/car/1980/2683265/porsche_924.html "https://www.automobile-catalog.com/car/1980/2683265/porsche_924.html"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Citroën C5 II 的 Sedan 与 Tourer 两种外廓，2898、2899、2918、2935 转为 READY；两种发动机在相同车身形式下尺寸一致，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Ibiza II 的 6K、6K1、6K2 三个外廓阶段及三门／五门分支；GTi 2.0 的 6K1 车身因降低高度单独建组。([汽车目录][2])
* 闭合早期 Porsche 911 F Series：2.2 T 使用 4163 mm 外廓；2341 cc T 在 1972 年8月前后分别使用 4147 mm 与 4127 mm 外廓。([汽车目录][3])
* 修正此前误用北美规格的两个 Porsche 944 尺寸组：Turbo/S2 Coupe 与 S2 Cabriolet 的欧洲规格长度由 4290 mm 修正为 4230 mm；同时闭合 Ktype 2987。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射行：103
* 未闭合 Ktype：16
* 已确认尺寸组：46
* 本轮首次创建尺寸组：16
* 本轮修正既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2898	2898	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	四门Sedan物理外廓。	READY
2899	2899	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	四门Sedan物理外廓。	READY
2910_3dr	2910	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	6K1三门改款外廓。	READY
2910_5dr	2910	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	6K1五门改款外廓。	READY
2911_3dr	2911	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2911_5dr	2911	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2912	2912	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	1.05i三门原型外廓。	READY
2913_3dr	2913	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2913_5dr	2913	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2914_3dr_6k	2914	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2914_3dr_6k1	2914	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	6K1三门改款外廓。	READY
2914_3dr_6k2	2914	Hatchback	Ibiza II 1999 facelift	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	HIGH	6K2三门改款外廓。	READY
2914_5dr_6k	2914	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2914_5dr_6k1	2914	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	6K1五门改款外廓。	READY
2914_5dr_6k2	2914	Hatchback	Ibiza II 1999 facelift	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	HIGH	6K2五门改款外廓。	READY
2915_3dr_6k	2915	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2915_3dr_6k1	2915	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	6K1三门改款外廓。	READY
2915_5dr_6k	2915	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2915_5dr_6k1	2915	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	6K1五门改款外廓。	READY
2916_6k	2916	Hatchback	Ibiza II GTi	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门GTi原型外廓。	READY
2916_6k1	2916	Hatchback	Ibiza II GTi/Cupra	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	HIGH	6K1三门GTi/Cupra降低车身外廓。	READY
2918	2918	Wagon	C5 II	X7	5	EU-CITROEN-C5-II-X7-WAGON-5D-01	HIGH	五门Tourer物理外廓。	READY
2935	2935	Wagon	C5 II	X7	5	EU-CITROEN-C5-II-X7-WAGON-5D-01	HIGH	五门Tourer物理外廓。	READY
2936	2936	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	MEDIUM	2.2 T长轴距F Series Coupe外廓。	READY
2938	2938	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	2.2 T长轴距F Series Targa外廓。	READY
2941_pre_aug72	2941	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	HIGH	1972年8月前Coupe外廓。	READY
2941_post_aug72	2941	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	HIGH	1972年8月后Coupe外廓。	READY
2942_pre_aug72	2942	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	HIGH	1972年8月前Targa外廓。	READY
2942_post_aug72	2942	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	HIGH	1972年8月后Targa外廓。	READY
2987	2987	Coupe	944	944	3	EU-PORSCHE-944-2-7-COUPE-3D-01	HIGH	欧洲规格2.7三门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1853	1456	Automobile-Catalog Citroën C5 VTi 120;Automobile-Catalog Citroën C5 HDi 200	https://www.automobile-catalog.com/car/2011/1452470/citroen_c5_vti_120_attraction_egs6.html;https://www.automobile-catalog.com/car/2011/1452860/citroen_c5_hdi_200_fap_exclusive_automatic.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Automobile-Catalog Seat Ibiza 1.9 SDi	https://www.automobile-catalog.com/car/1996/3066200/seat_ibiza_1_9_sdi.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Automobile-Catalog Seat Ibiza 1.9 SDi	https://www.automobile-catalog.com/car/1996/3066200/seat_ibiza_1_9_sdi.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390	Automobile-Catalog Seat Ibiza 1.05i	https://www.automobile-catalog.com/car/1996/3069860/seat_ibiza_1_05i.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390	Automobile-Catalog Seat Ibiza 1.9 TD	https://www.automobile-catalog.com/car/1996/3069965/seat_ibiza_1_9_td.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422	Automobile-Catalog Seat Ibiza 1.6 75	https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422	Automobile-Catalog Seat Ibiza 1.6 75	https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409	Automobile-Catalog Seat Ibiza GTi Cupra 2.0	https://www.automobile-catalog.com/car/1996/3070100/seat_ibiza_gti_2_0.html
EU-CITROEN-C5-II-X7-WAGON-5D-01	4829	1853	1491	Automobile-Catalog Citroën C5 Tourer VTi 120;Automobile-Catalog Citroën C5 Tourer HDi 200	https://www.automobile-catalog.com/car/2011/1452485/citroen_c5_tourer_vti_120_attraction_egs6.html;https://www.automobile-catalog.com/car/2011/1452875/citroen_c5_tourer_hdi_200_fap_exclusive_automatic.html
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320	Automobile-Catalog Porsche 911 T 2.2 Coupe	https://www.automobile-catalog.com/car/1971/2589860/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320	Automobile-Catalog Porsche 911 T 2.2 Targa	https://www.automobile-catalog.com/car/1971/2589950/porsche_911_t_targa.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 T Coupe	https://www.automobile-catalog.com/car/1972/2590220/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 T Targa	https://www.automobile-catalog.com/car/1972/2590475/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 T Coupe	https://www.automobile-catalog.com/car/1972/2590745/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 T Targa	https://www.automobile-catalog.com/car/1973/2590880/porsche_911_t_coupe.html
EU-PORSCHE-944-2-7-COUPE-3D-01	4230	1735	1275	Automobile-Catalog Porsche 944 2.7 Europe	https://www.automobile-catalog.com/car/1989/2684180/porsche_944_2_7.html
EU-PORSCHE-944-AERO-COUPE-3D-01	4230	1735	1275	Automobile-Catalog Porsche 944 Turbo Europe;Automobile-Catalog Porsche 944 S2 Europe	https://www.automobile-catalog.com/car/1989/2684315/porsche_944_turbo.html;https://www.automobile-catalog.com/car/1989/2684210/porsche_944_s2.html
EU-PORSCHE-944-S2-CONVERTIBLE-2D-01	4230	1735	1275	Automobile-Catalog Porsche 944 S2 Cabrio Europe	https://www.automobile-catalog.com/car/1989/2684345/porsche_944_s2_cabrio.html
```

## 下一步优先处理

1. 批量闭合 Ktype 2920–2929 的 Saab 900 Combi Coupé 三门／五门、前期／后期及降低车身分支。
2. 闭合 Ktype 2978 的 Saab 900 两门／四门 Sedan 外廓。
3. 核对 Marbella Kasten 的独立商用车身边界。
4. 处理 Porsche 911 Speedster Ktype 2959 与 Saab 9000 Ktype 2969。
5. PENDING 清零后立即执行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2011/1452470/citroen_c5_vti_120_attraction_egs6.html "https://www.automobile-catalog.com/car/2011/1452470/citroen_c5_vti_120_attraction_egs6.html"
[2]: https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html "https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html"
[3]: https://www.automobile-catalog.com/car/1971/2589950/porsche_911_t_targa.html "https://www.automobile-catalog.com/car/1971/2589950/porsche_911_t_targa.html"
[4]: https://www.automobile-catalog.com/car/1989/2684180/porsche_944_2_7.html?utm_source=chatgpt.com "1989 Porsche 944 2.7 Specs Review (121 kW / 165 PS / 162 hp) (up to August 1989 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合最后的阻塞项：Marbella 商用车型确认为 `028A` 封闭货厢车身；Saab 900 按门数、改款阶段和 Turbo 外部套件拆分；Saab 9000 按早期 CC、后期 CC 与 CS 拆分。([历史汽车座椅][1])
* Porsche 911 Speedster 已拆分为窄体与 Turbo-Look 两种物理外廓。([汽车目录][2])
* 已完成机械收尾检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 均唯一，全部映射引用闭合，尺寸及来源字段完整。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：146
* READY 映射：146
* PENDING 映射：0
* 最终尺寸组：61
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2887	2887	Hatchback	Marbella (28)	28	3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH	三门掀背物理外廓。	READY
2888	2888	Hatchback	Marbella (28)	28	3	EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	HIGH	三门掀背物理外廓。	READY
2889	2889	Van	Marbella Box	028A	3	EU-SEAT-MARBELLA-028A-VAN-3D-01	HIGH	028A三门商用封闭货厢外廓。	READY
2890	2890	Van	Marbella Box	028A	3	EU-SEAT-MARBELLA-028A-VAN-3D-01	HIGH	028A三门商用封闭货厢外廓。	READY
2891	2891	Van	Marbella Box	028A	3	EU-SEAT-MARBELLA-028A-VAN-3D-01	HIGH	028A三门商用封闭货厢外廓。	READY
2892	2892	Sedan	600 D		2	EU-SEAT-600-D-SEDAN-2D-01	HIGH	两门Berlina物理外廓。	READY
2893	2893	Sedan	133		2	EU-SEAT-133-SEDAN-2D-01	HIGH	可靠资料将该两门车身归类为Berlina/Sedan。	READY
2894	2894	Sedan	IS II facelift 2010	ALE20	4	EU-LEXUS-IS-II-ALE20-FACELIFT-SEDAN-4D-01	HIGH	200d后驱四门轿车外廓。	READY
2896_van	2896	Van	Terra		3	EU-SEAT-TERRA-VAN-3D-01	HIGH	Kasten/Kombi输入拆分为封闭货厢分支。	READY
2896_kombi	2896	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	Kasten/Kombi输入拆分为侧窗Kombi分支。	READY
2897_van	2897	Van	Terra		3	EU-SEAT-TERRA-VAN-3D-01	HIGH	Kasten/Kombi输入拆分为封闭货厢分支。	READY
2897_kombi	2897	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	Kasten/Kombi输入拆分为侧窗Kombi分支。	READY
2898	2898	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	四门Sedan物理外廓。	READY
2899	2899	Sedan	C5 II	X7	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	四门Sedan物理外廓。	READY
2900	2900	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	侧窗Kombi物理外廓。	READY
2901	2901	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH	侧窗Kombi物理外廓。	READY
2902	2902	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2903	2903	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2904	2904	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2905	2905	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2906	2906	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2907	2907	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2908	2908	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2909	2909	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH	五门掀背式Liftback外廓。	READY
2910_3dr	2910	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	6K1三门改款外廓。	READY
2910_5dr	2910	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	6K1五门改款外廓。	READY
2911_3dr	2911	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2911_5dr	2911	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2912	2912	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	1.05i三门原型外廓。	READY
2913_3dr	2913	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门原型外廓。	READY
2913_5dr	2913	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门原型外廓。	READY
2914_3dr_6k	2914	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门外廓。	READY
2914_3dr_6k1	2914	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	HIGH	6K1三门外廓。	READY
2914_3dr_6k2	2914	Hatchback	Ibiza II 1999 facelift	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	HIGH	6K2三门外廓。	READY
2914_5dr_6k	2914	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门外廓。	READY
2914_5dr_6k1	2914	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	HIGH	6K1五门外廓。	READY
2914_5dr_6k2	2914	Hatchback	Ibiza II 1999 facelift	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	HIGH	6K2五门外廓。	READY
2915_3dr_6k	2915	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门外廓。	READY
2915_3dr_6k1	2915	Hatchback	Ibiza II 1996 facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	6K1三门外廓。	READY
2915_5dr_6k	2915	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	HIGH	6K五门外廓。	READY
2915_5dr_6k1	2915	Hatchback	Ibiza II 1996 facelift	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	6K1五门外廓。	READY
2916_6k	2916	Hatchback	Ibiza II GTi	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	HIGH	6K三门GTi原型外廓。	READY
2916_6k1	2916	Hatchback	Ibiza II GTi/Cupra	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	HIGH	6K1三门GTi/Cupra降低车身外廓。	READY
2917	2917	Sedan	90		2	EU-SAAB-90-SEDAN-2D-01	HIGH	两门Sedan物理外廓。	READY
2918	2918	Wagon	C5 II	X7	5	EU-CITROEN-C5-II-X7-WAGON-5D-01	HIGH	五门Tourer物理外廓。	READY
2919_2dr_early	2919	Sedan	99		2	EU-SAAB-99-SEDAN-2D-EARLY-01	MEDIUM	2门早期保险杠外廓。	READY
2919_4dr_early	2919	Sedan	99		4	EU-SAAB-99-SEDAN-4D-EARLY-01	MEDIUM	4门早期保险杠外廓。	READY
2919_2dr_late	2919	Sedan	99		2	EU-SAAB-99-SEDAN-2D-LATE-01	MEDIUM	2门后期保险杠外廓。	READY
2919_4dr_late	2919	Sedan	99		4	EU-SAAB-99-SEDAN-4D-LATE-01	MEDIUM	4门后期保险杠外廓。	READY
2920_3dr_prefl	2920	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	三门前期Combi Coupé外廓。	READY
2920_5dr_prefl	2920	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	五门前期Combi Coupé外廓。	READY
2920_3dr_facelift	2920	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款Combi Coupé外廓。	READY
2920_5dr_facelift	2920	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款Combi Coupé外廓。	READY
2921_3dr	2921	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	HIGH	三门前期Combi Coupé外廓。	READY
2921_5dr	2921	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	HIGH	五门前期Combi Coupé外廓。	READY
2922_3dr_prefl	2922	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	三门前期Combi Coupé外廓。	READY
2922_5dr_prefl	2922	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	五门前期Combi Coupé外廓。	READY
2922_3dr_facelift	2922	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款Combi Coupé外廓。	READY
2922_5dr_facelift	2922	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款Combi Coupé外廓。	READY
2923_3dr_prefl	2923	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	三门前期Combi Coupé外廓。	READY
2923_5dr_prefl	2923	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	五门前期Combi Coupé外廓。	READY
2923_3dr_facelift	2923	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款Combi Coupé外廓。	READY
2923_5dr_facelift	2923	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款Combi Coupé外廓。	READY
2924_3dr_prefl	2924	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-3D-01	MEDIUM	三门前期Turbo-16外廓。	READY
2924_5dr_prefl	2924	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-5D-01	MEDIUM	五门前期Turbo-16外廓。	READY
2924_3dr_facelift	2924	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款Turbo-16标准外廓。	READY
2924_5dr_facelift	2924	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款Turbo-16标准外廓。	READY
2925_3dr	2925	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	HIGH	三门前期Turbo外廓。	READY
2925_5dr	2925	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	HIGH	五门前期Turbo外廓。	READY
2926_prefl	2926	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-TURBO16S-HATCHBACK-3D-01	HIGH	前期三门Turbo-16 S外廓。	READY
2926_facelift	2926	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	HIGH	改款三门Turbo-16 S宽体低车身外廓。	READY
2927_3dr_early	2927	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门改款早期2.0-16外廓。	READY
2927_5dr_early	2927	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门改款早期2.0-16外廓。	READY
2927_3dr_late	2927	Hatchback	900 I facelift late		3	EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-3D-01	MEDIUM	三门后期2.0-16外廓。	READY
2927_5dr_late	2927	Hatchback	900 I facelift late		5	EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-5D-01	MEDIUM	五门后期2.0-16外廓。	READY
2928_3dr	2928	Hatchback	900 I facelift late		3	EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-3D-01	HIGH	三门900 S低压增压外廓。	READY
2928_5dr	2928	Hatchback	900 I facelift late		5	EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-5D-01	HIGH	五门900 S低压增压外廓。	READY
2929	2929	Hatchback	900 I facelift late		3	EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	HIGH	三门Turbo S宽体低车身外廓。	READY
2930	2930	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	HIGH	原始CC五门外廓。	READY
2931	2931	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	HIGH	原始CC五门外廓。	READY
2932_cc_early	2932	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	MEDIUM	原始CC五门外廓阶段。	READY
2932_cc_facelift	2932	Hatchback	9000 CC facelift	CC	5	EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	MEDIUM	后期CC五门外廓阶段。	READY
2932_cs	2932	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	CS五门外廓阶段。	READY
2933_cc_early	2933	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	MEDIUM	原始CC五门外廓阶段。	READY
2933_cc_facelift	2933	Hatchback	9000 CC facelift	CC	5	EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	MEDIUM	后期CC五门外廓阶段。	READY
2933_cs	2933	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	CS五门外廓阶段。	READY
2934	2934	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	VariantName明确CS；输入起始月存在上游早录。	READY
2935	2935	Wagon	C5 II	X7	5	EU-CITROEN-C5-II-X7-WAGON-5D-01	HIGH	五门Tourer物理外廓。	READY
2936	2936	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	MEDIUM	2.2 T长轴距F Series Coupe外廓。	READY
2937	2937	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	1993年后五门CS外廓。	READY
2938	2938	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	2.2 T长轴距F Series Targa外廓。	READY
2939_cc_early	2939	Hatchback	9000 CC	CC	5	EU-SAAB-9000-CC-HATCHBACK-5D-01	MEDIUM	原始CC五门外廓阶段。	READY
2939_cc_facelift	2939	Hatchback	9000 CC facelift	CC	5	EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	MEDIUM	后期CC五门外廓阶段。	READY
2939_cs	2939	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	MEDIUM	CS五门外廓阶段。	READY
2940	2940	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	HIGH	五门标准轴距SUV外廓。	READY
2941_pre_aug72	2941	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	HIGH	1972年8月前外廓。	READY
2941_post_aug72	2941	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	HIGH	1972年8月后外廓。	READY
2942_pre_aug72	2942	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	HIGH	1972年8月前外廓。	READY
2942_post_aug72	2942	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	HIGH	1972年8月后外廓。	READY
2943	2943	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	HIGH	G Series窄体Coupe外廓。	READY
2944	2944	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	HIGH	G Series窄体Targa外廓。	READY
2945	2945	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	HIGH	G Series窄体Targa外廓。	READY
2946	2946	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	VariantName明确CS五门外廓。	READY
2947	2947	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	VariantName明确CS五门外廓。	READY
2948	2948	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	HIGH	G Series窄体Coupe外廓。	READY
2949	2949	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2950	2950	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2951	2951	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2952	2952	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2953	2953	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.0宽体Coupe外廓。	READY
2954	2954	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	HIGH	Carrera 3.0宽体Targa外廓。	READY
2955	2955	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	911 SC宽体Coupe外廓。	READY
2956	2956	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	911 SC Cabriolet外廓。	READY
2957	2957	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	Carrera 3.2 Cabriolet外廓。	READY
2958	2958	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.2 Coupe外廓。	READY
2959_narrow	2959	Convertible	911 G Series Speedster	911	2	EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	HIGH	Speedster窄体低风挡外廓。	READY
2959_turbolook	2959	Convertible	911 G Series Speedster	911	2	EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	HIGH	Speedster Turbo-Look宽体低风挡外廓。	READY
2960	2960	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	Carrera 3.2 Coupe外廓。	READY
2961	2961	Convertible	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	HIGH	Carrera 3.2 Cabriolet外廓。	READY
2962	2962	SUV	Range Rover Sport I	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	HIGH	五门SUV物理外廓。	READY
2964	2964	Coupe	911 Turbo 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体Coupe外廓。	READY
2965	2965	Coupe	911 Turbo 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体Coupe外廓。	READY
2966	2966	Convertible	911 964	964	2	EU-PORSCHE-911-964-CONVERTIBLE-01	HIGH	欧洲规格964 Carrera 4 Cabriolet外廓。	READY
2967	2967	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE属于CS五门外廓。	READY
2968	2968	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE Eco Power属于CS五门外廓。	READY
2969_cc	2969	Hatchback	9000 CC facelift	CC	5	EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	HIGH	1990至1991年晚期CC五门外廓。	READY
2969_cs	2969	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	1991年后CS五门外廓。	READY
2970	2970	Hatchback	9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH	CSE属于CS五门外廓。	READY
2971	2971	Hatchback	9000 CS Aero	CS	5	EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	HIGH	Aero外部套件与降低车高形成独立外廓。	READY
2972	2972	Coupe	911 964	964	2	EU-PORSCHE-911-964-COUPE-01	HIGH	欧洲规格964 Carrera 2 Coupe外廓。	READY
2973	2973	Convertible	911 964	964	2	EU-PORSCHE-911-964-CONVERTIBLE-01	HIGH	欧洲规格964 Carrera 2 Cabriolet外廓。	READY
2974	2974	Coupe	924	924	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	标准924三门Coupe外廓。	READY
2975	2975	Coupe	924 Turbo	931	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	931 Turbo与标准924共用外部尺寸边界。	READY
2976	2976	Hatchback	9000 CS Aero	CS	5	EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	HIGH	Aero外部套件与降低车高形成独立外廓。	READY
2977	2977	Coupe	924 S	924S	3	EU-PORSCHE-924-S-COUPE-3D-01	HIGH	924 S三门Coupe外廓。	READY
2978	2978	Sedan	900 I pre-facelift		4	EU-SAAB-900-I-PREFL-SEDAN-4D-01	HIGH	GLS四门Sedan物理外廓。	READY
2979	2979	Coupe	924 S	924S	3	EU-PORSCHE-924-S-COUPE-3D-01	HIGH	924 S三门Coupe外廓。	READY
2981	2981	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	HIGH	标准车头944三门Coupe外廓。	READY
2982	2982	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	MEDIUM	发动机更新未改变标准944物理外廓。	READY
2983	2983	Coupe	944	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	HIGH	标准车头944三门Coupe外廓。	READY
2984	2984	Coupe	944 S	944	3	EU-PORSCHE-944-BASE-COUPE-3D-01	MEDIUM	944 S沿用标准944外部车身。	READY
2985	2985	Coupe	944 Turbo	951	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	951 Turbo空力车头三门Coupe外廓。	READY
2986	2986	Coupe	944 Turbo	951	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	951 Turbo空力车头三门Coupe外廓。	READY
2987	2987	Coupe	944	944	3	EU-PORSCHE-944-2-7-COUPE-3D-01	HIGH	欧洲规格2.7三门Coupe外廓。	READY
2988	2988	Coupe	944 S2	944	3	EU-PORSCHE-944-AERO-COUPE-3D-01	HIGH	S2 Coupe采用Turbo式空力外廓。	READY
2989	2989	Convertible	944 S2	944	2	EU-PORSCHE-944-S2-CONVERTIBLE-2D-01	HIGH	S2 Cabriolet独立开放车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2801-2900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-MARBELLA-28-HATCHBACK-3D-01	3475	1500	1445	SEAT Historic Cars Marbella	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1980/marbellabast.php
EU-SEAT-MARBELLA-028A-VAN-3D-01	3475	1500	1445	SEAT Historic Cars Marbella;SEAT Marbella Box 028A vehicle identification	https://www.seatcocheshistoricos.es/SEATHistoricos/en/1980/marbellabast.php;https://club.autodoc.co.uk/manuals/seat/marbella/marbella-box-028a
EU-SEAT-600-D-SEDAN-2D-01	3295	1380	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/3060335/seat_600_d.html
EU-SEAT-133-SEDAN-2D-01	3451	1421	1328	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/40040/seat_133_n.html
EU-LEXUS-IS-II-ALE20-FACELIFT-SEDAN-4D-01	4585	1800	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1604795/lexus_is_200d.html
EU-SEAT-TERRA-VAN-3D-01	3869	1490	1895	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3065495/seat_terra_van_1_3_diesel.html
EU-SEAT-TERRA-MPV-3D-01	3869	1490	1895	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3065420/seat_terra_kombi_1_3_diesel.html
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1853	1456	Automobile-Catalog Citroën C5 VTi 120;Automobile-Catalog Citroën C5 HDi 200	https://www.automobile-catalog.com/car/2011/1452470/citroen_c5_vti_120_attraction_egs6.html;https://www.automobile-catalog.com/car/2011/1452860/citroen_c5_hdi_200_fap_exclusive_automatic.html
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424	Auto-Data;Automobile-Catalog	https://www.auto-data.net/en/seat-toledo-i-1l-generation-2913;https://www.automobile-catalog.com/car/1998/3065705/seat_toledo_1_6i.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Automobile-Catalog Seat Ibiza 1.9 SDi	https://www.automobile-catalog.com/car/1996/3066200/seat_ibiza_1_9_sdi.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Automobile-Catalog Seat Ibiza 1.9 SDi	https://www.automobile-catalog.com/car/1996/3066200/seat_ibiza_1_9_sdi.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390	Automobile-Catalog Seat Ibiza 1.05i	https://www.automobile-catalog.com/car/1996/3069860/seat_ibiza_1_05i.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390	Automobile-Catalog Seat Ibiza 1.9 TD	https://www.automobile-catalog.com/car/1996/3069965/seat_ibiza_1_9_td.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422	Automobile-Catalog Seat Ibiza 1.6 75	https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422	Automobile-Catalog Seat Ibiza 1.6 75	https://www.automobile-catalog.com/car/1999/3070490/seat_ibiza_1_6_75.html
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409	Automobile-Catalog Seat Ibiza GTi Cupra 2.0	https://www.automobile-catalog.com/car/1996/3070100/seat_ibiza_gti_2_0.html
EU-SAAB-90-SEDAN-2D-01	4579	1690	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/3027260/saab_90_4-speed.html
EU-CITROEN-C5-II-X7-WAGON-5D-01	4829	1853	1491	Automobile-Catalog Citroën C5 Tourer VTi 120;Automobile-Catalog Citroën C5 Tourer HDi 200	https://www.automobile-catalog.com/car/2011/1452485/citroen_c5_tourer_vti_120_attraction_egs6.html;https://www.automobile-catalog.com/car/2011/1452875/citroen_c5_tourer_hdi_200_fap_exclusive_automatic.html
EU-SAAB-99-SEDAN-2D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/3019100/saab_99_gl_2-door.html
EU-SAAB-99-SEDAN-4D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/3019790/saab_99_gl_4-door.html
EU-SAAB-99-SEDAN-2D-LATE-01	4477	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/3019985/saab_99_gl_2-door_5-speed.html
EU-SAAB-99-SEDAN-4D-LATE-01	4477	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1982/3020000/saab_99_gl_4-door.html
EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	4740	1690	1420	Automobile-Catalog Saab 900 GL 3-door	https://www.automobile-catalog.com/car/1979/45860/saab_900_gl_3-door.html
EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	4740	1690	1425	Automobile-Catalog Saab 900 GLS 5-door	https://www.automobile-catalog.com/car/1984/3022175/saab_900_gls_5-door.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	4687	1690	1420	Automobile-Catalog Saab 900 i 3-door	https://www.automobile-catalog.com/car/1988/3024860/saab_900_i_3-door.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	4687	1690	1420	Automobile-Catalog Saab 900 i 5-door	https://www.automobile-catalog.com/car/1988/3024995/saab_900_i_automatic_5-door.html
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-3D-01	4740	1690	1425	Automobile-Catalog Saab 900 Turbo 16 3-door	https://www.automobile-catalog.com/car/1985/3023660/saab_900_turbo_16_3-door.html
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-5D-01	4740	1690	1425	Automobile-Catalog Saab 900 Turbo 16 5-door	https://www.automobile-catalog.com/car/1985/3022925/saab_900_turbo_16_5-door.html
EU-SAAB-900-I-PREFL-TURBO16S-HATCHBACK-3D-01	4740	1690	1425	Automobile-Catalog Saab 900 Turbo 16 S	https://www.automobile-catalog.com/car/1984/3022895/saab_900_turbo_16_s.html
EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	4687	1695	1405	Automobile-Catalog Saab 900 Turbo 16 S catalyst	https://www.automobile-catalog.com/car/1987/3024335/saab_900_turbo_16_s_catalyst.html
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-3D-01	4687	1693	1420	Automobile-Catalog Saab 900 i 2.0-16 3-door	https://www.automobile-catalog.com/car/1992/3026870/saab_900_i_2_0-16_3-door_catalyst.html
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-5D-01	4687	1693	1420	Automobile-Catalog Saab 900 S 5-door	https://www.automobile-catalog.com/car/1993/3027050/saab_900_s_5-door.html
EU-SAAB-9000-CC-HATCHBACK-5D-01	4620	1764	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/54200/saab_9000_ie_16.html
EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	4667	1764	1420	Automobile-Catalog Saab 9000 2.3 Turbo	https://www.automobile-catalog.com/car/1991/3028520/saab_9000_2_3_turbo_catalyst.html
EU-SAAB-9000-CS-HATCHBACK-5D-01	4761	1778	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/3029690/saab_9000_cs_cse_2_3_turbo.html
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320	Automobile-Catalog Porsche 911 T 2.2 Coupe	https://www.automobile-catalog.com/car/1971/2589860/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320	Automobile-Catalog Porsche 911 T 2.2 Targa	https://www.automobile-catalog.com/car/1971/2589950/porsche_911_t_targa.html
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	4829	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1616330/land_rover_discovery_4_3_0_tdv6_commercial.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 T Coupe	https://www.automobile-catalog.com/car/1972/2590220/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 T Coupe	https://www.automobile-catalog.com/car/1972/2590745/porsche_911_t_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 T Targa	https://www.automobile-catalog.com/car/1972/2590475/porsche_911_t_targa.html
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 T Targa	https://www.automobile-catalog.com/car/1973/2590880/porsche_911_t_targa.html
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2649485/porsche_911_coupe_4-speed.html
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2649605/porsche_911_targa_4-speed.html
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2650535/porsche_911_carrera_3_0_targa_5-speed.html
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2650295/porsche_911_carrera_3_0_coupe_4-speed.html
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/41330/porsche_911_sc_cabriolet.html
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200	Automobile-Catalog Porsche 911 Speedster	https://www.automobile-catalog.com/car/1989/2682785/porsche_911_speedster.html
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200	Automobile-Catalog Porsche 911 Speedster Turbo-Look	https://www.automobile-catalog.com/car/1989/2682830/porsche_911_speedster_turbo-look.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-5D-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1405160/range_rover_sport_3_0_tdv6_se.html
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2681630/porsche_911_turbo.html
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2865080/porsche_911_carrera_4_cabriolet.html
EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	4761	1806	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/3029735/saab_9000_aero.html
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/2865005/porsche_911_carrera_2_coupe.html
EU-PORSCHE-924-COUPE-3D-EARLY-01	4212	1685	1270	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/2683265/porsche_924.html
EU-PORSCHE-924-S-COUPE-3D-01	4212	1685	1275	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/31610/porsche_924_s.html
EU-SAAB-900-I-PREFL-SEDAN-4D-01	4740	1690	1420	Automobile-Catalog Saab 900 GLS 4-door	https://www.automobile-catalog.com/car/1982/3021455/saab_900_gls_4-door.html
EU-PORSCHE-944-BASE-COUPE-3D-01	4200	1735	1275	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/2683910/porsche_944.html
EU-PORSCHE-944-AERO-COUPE-3D-01	4230	1735	1275	Automobile-Catalog Porsche 944 Turbo Europe;Automobile-Catalog Porsche 944 S2 Europe	https://www.automobile-catalog.com/car/1989/2684315/porsche_944_turbo.html;https://www.automobile-catalog.com/car/1989/2684210/porsche_944_s2.html
EU-PORSCHE-944-2-7-COUPE-3D-01	4230	1735	1275	Automobile-Catalog Porsche 944 2.7 Europe	https://www.automobile-catalog.com/car/1989/2684180/porsche_944_2_7.html
EU-PORSCHE-944-S2-CONVERTIBLE-2D-01	4230	1735	1275	Automobile-Catalog Porsche 944 S2 Cabrio Europe	https://www.automobile-catalog.com/car/1989/2684345/porsche_944_s2_cabrio.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2801-2900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.seatcocheshistoricos.es/SEATHistoricos/1980/marbellabast.php?utm_source=chatgpt.com "Marbella"
[2]: https://www.automobile-catalog.com/car/1989/2682785/porsche_911_speedster.html "https://www.automobile-catalog.com/car/1989/2682785/porsche_911_speedster.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2801-2900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2801-2900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3483 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（919 行）
