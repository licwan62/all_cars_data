# 任务：all 第 2001-2100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0021__13e0fd87


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2001-2100 行

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
all 第 2001-2100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	18	1.6	Kombi	Frontantrieb	Benzin	58	79	May 1979	Sep 1982	2024-03-01	2040
Renault	18	2	Kombi	Frontantrieb	Benzin	77	105	Oct 1981	Jul 1986	2024-03-01	2041
Renault	18	2.1 Diesel	Kombi	Frontantrieb	Diesel	49	67	Nov 1980	Jul 1986	2024-03-01	2042
Renault	19 i	1.4 CAT	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1989	Apr 1992	2024-03-01	2043
Renault	19 i	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Sep 1988	Apr 1992	2024-03-01	2044
Renault	19 i	1.7	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1988	Apr 1992	2024-03-01	2045
Renault	19 i	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Sep 1988	Apr 1992	2024-03-01	2046
Renault	19 i chamade	1.9 D	Stufenheck	Frontantrieb	Diesel	47	64	Oct 1989	Apr 1992	2024-03-01	2047
Renault	19 ii chamade	1.9 D	Stufenheck	Frontantrieb	Diesel	47	64	Apr 1992	Dec 1997	2025-02-03	2048
Renault	19 ii	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Apr 1992	Dec 1995	2024-03-01	2049
Renault	19 ii chamade	1.4	Stufenheck	Frontantrieb	Benzin	43	58	Apr 1992	Dec 1995	2024-03-01	2050
Renault	19 ii	1.4	Schrägheck	Frontantrieb	Benzin	43	58	Apr 1992	Dec 1995	2024-03-01	2051
Renault	19 i chamade	1.4	Stufenheck	Frontantrieb	Benzin	43	58	Jul 1988	Apr 1992	2024-03-01	2052
Renault	19 ii	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Apr 1992	Dec 1995	2024-03-01	2053
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	54	73	Oct 1989	Apr 1992	2024-03-01	2054
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	54	73	Apr 1992	Dec 1995	2024-03-01	2055
Renault	19 ii	1.7	Cabriolet	Frontantrieb	Benzin	66	90	Apr 1992	Sep 1993	2024-03-01	2056
Renault	19 i chamade	1.7	Stufenheck	Frontantrieb	Benzin	66	90	Jul 1988	Apr 1992	2024-03-01	2057
Renault	19 ii	1.8 16V	Schrägheck	Frontantrieb	Benzin	99	135	Apr 1992	Dec 1995	2024-03-01	2058
Renault	19 i chamade	1.8 16V	Stufenheck	Frontantrieb	Benzin	99	135	Oct 1989	Apr 1992	2024-03-01	2059
Renault	19 i	1.8 16V	Schrägheck	Frontantrieb	Benzin	99	135	Jun 1989	Apr 1992	2024-03-01	2060
Renault	19 ii	1.8 16V	Cabriolet	Frontantrieb	Benzin	99	135	Apr 1992	Jun 1996	2024-03-01	2061
Renault	19 ii chamade	1.8	Stufenheck	Frontantrieb	Benzin	65	88	Apr 1992	Dec 1995	2024-03-01	2062
Renault	19 ii	1.8	Schrägheck	Frontantrieb	Benzin	65	88	Apr 1992	Dec 1995	2024-03-01	2063
Renault	19 ii	1.8	Cabriolet	Frontantrieb	Benzin	65	88	Apr 1992	Jun 1996	2024-03-01	2064
Renault	19 ii	1.8	Schrägheck	Frontantrieb	Benzin	81	110	Apr 1992	May 1994	2024-03-01	2065
Renault	20	2	Schrägheck	Frontantrieb	Benzin	76	103	Oct 1980	Dec 1983	2024-03-01	2066
Renault	20	2	Schrägheck	Frontantrieb	Benzin	80	109	Oct 1977	Oct 1980	2024-03-01	2067
Renault	20	2.2	Schrägheck	Frontantrieb	Benzin	85	116	Oct 1980	Dec 1983	2024-03-01	2068
Renault	20	2.1 Diesel	Schrägheck	Frontantrieb	Diesel	47	64	Oct 1980	Dec 1983	2024-03-01	2069
Renault	30	2.6 TX	Schrägheck	Frontantrieb	Benzin	105	143	Oct 1978	Dec 1983	2024-03-01	2070
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	55	75	Mar 1986	Dec 1987	2024-03-01	2071
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	69	94	Mar 1986	Feb 1994	2024-03-01	2072
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	65	88	Mar 1986	Mar 1993	2024-03-01	2073
Renault	21	2	Stufenheck	Frontantrieb	Benzin	85	116	Mar 1986	Dec 1988	2024-03-01	2074
Renault	21	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	129	175	Apr 1987	Mar 1990	2024-03-01	2075
Renault	21	2.1 D	Stufenheck	Frontantrieb	Diesel	48	65	Mar 1986	Dec 1989	2024-03-01	2076
Renault	21	2.1 Turbo-d	Schrägheck	Frontantrieb	Diesel	65	88	Sep 1989	Jun 1994	2024-03-01	2077
Renault	21	2.1 Turbo-d	Stufenheck	Frontantrieb	Diesel	65	88	Mar 1986	Jun 1994	2024-03-01	2078
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	54	73	Jul 1986	Feb 1994	2024-03-01	2079
Renault	21	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Sep 1989	Oct 1992	2024-03-01	2080
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1989	Feb 1994	2024-03-01	2081
Renault	21	1.7	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1989	Jun 1994	2024-03-01	2082
Renault	21	2	Schrägheck	Frontantrieb	Benzin	99	135	Feb 1990	Oct 1992	2024-03-01	2083
Renault	21	2.2	Schrägheck	Frontantrieb	Benzin	79	107	Sep 1989	Jun 1994	2024-03-01	2084
Renault	21	2.2	Stufenheck	Frontantrieb	Benzin	79	107	Jul 1986	Feb 1994	2024-03-01	2085
Renault	21	1.7 CAT	Kombi	Frontantrieb	Benzin	54	73	May 1988	Jun 1993	2024-03-01	2086
Renault	21	1.7	Kombi	Frontantrieb	Benzin	65	88	Oct 1986	Dec 1988	2024-03-01	2087
Renault	21	1.7	Kombi	Frontantrieb	Benzin	69	94	Jun 1986	Dec 1989	2024-03-01	2088
Renault	21	2.2	Kombi	Frontantrieb	Benzin	79	108	Jun 1986	Nov 1993	2024-03-01	2089
Renault	21	2.1 D	Kombi	Frontantrieb	Diesel	48	65	Oct 1986	Sep 1990	2024-03-01	2090
Renault	21	2.1 D	Kombi	Frontantrieb	Diesel	53	72	Aug 1989	Dec 1992	2024-03-01	2091
Renault	21	2.1 Turbo-d	Kombi	Frontantrieb	Diesel	65	88	Oct 1986	Nov 1993	2024-03-01	2092
Renault	21	1.7	Kombi	Frontantrieb	Benzin	66	90	Oct 1989	Dec 1993	2024-03-01	2093
Renault	25	2	Schrägheck	Frontantrieb	Benzin	74	101	Apr 1984	Dec 1992	2024-03-01	2094
Renault	25	2.2	Schrägheck	Frontantrieb	Benzin	89	121	Apr 1984	Dec 1989	2024-03-01	2095
Renault	25	2.4 V6 Turbo	Schrägheck	Frontantrieb	Benzin	133	181	Oct 1984	May 1990	2024-03-01	2096
Renault	25	2.7 V6 Injection	Schrägheck	Frontantrieb	Benzin	104	141	Apr 1984	Aug 1989	2024-03-01	2097
Renault	25	2.1 Diesel	Schrägheck	Frontantrieb	Diesel	46	63	Apr 1984	May 1989	2024-03-01	2098
Renault	25	2.1 Turbo-d FWD	Schrägheck	Frontantrieb	Diesel	63	86	Apr 1984	Dec 1992	2024-03-01	2099
Renault	25	2.0 12V	Schrägheck	Frontantrieb	Benzin	99	135	Jun 1989	Dec 1992	2024-03-01	2100
Renault	25	2.2	Schrägheck	Frontantrieb	Benzin	79	108	Sep 1986	Dec 1992	2024-03-01	2101
Renault	25	2.8 V6 Injection	Schrägheck	Frontantrieb	Benzin	110	150	Jun 1987	Dec 1992	2024-03-01	2102
Renault	Fuego	1.6 Turbo	Coupe	Frontantrieb	Benzin	97	132	Aug 1983	Oct 1985	2024-03-01	2103
Renault	Fuego	1.6 Ts/gts	Coupe	Frontantrieb	Benzin	71	97	Oct 1980	Oct 1985	2024-03-01	2104
Renault	Fuego	2.0 Tx/gtx	Coupe	Frontantrieb	Benzin	81	110	Oct 1980	Oct 1985	2024-03-01	2105
Renault	Espace i	2	Großraumlimousine	Frontantrieb	Benzin	80	109	Jul 1984	Dec 1990	2024-03-01	2106
Renault	Espace i	2.2	Großraumlimousine	Frontantrieb	Benzin	79	108	Jul 1986	Dec 1990	2024-03-01	2107
Renault	Espace i	2.2 Quadra	Großraumlimousine	Allrad	Benzin	79	108	Jan 1988	Dec 1990	2024-03-01	2108
Renault	Espace i	2.1 TD	Großraumlimousine	Frontantrieb	Diesel	65	88	Oct 1984	Dec 1990	2024-03-01	2109
Renault	Rapid	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	33	45	Jun 1987	Sep 1991	2024-03-01	2110
Renault	Rapid	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	33	45	Jul 1985	Apr 1995	2024-03-01	2111
Renault	Rapid	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Mar 1986	Aug 1991	2024-03-01	2112
Renault	Rapid	1.6 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	40	55	Mar 1986	Aug 1998	2024-03-01	2113
Renault	Rapid	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	47	64	Sep 1991	Mar 1998	2024-03-01	2114
Renault	Rapid	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	40	55	Sep 1991	Mar 1998	2024-03-01	2115
Renault	Rapid	1.4 CAT	Kasten/Großraumlimousine	Frontantrieb	Benzin	43	58	Aug 1988	Mar 1998	2024-03-01	2116
Renault	Rapid	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Sep 1991	Mar 1998	2024-03-01	2117
Renault	Trafic	1.7	Bus	Frontantrieb	Benzin	50	68	Aug 1992	Aug 1994	2024-03-01	2118
Renault	Trafic	2.1 D	Bus	Frontantrieb	Diesel	43	58	Mar 1980	Apr 1989	2024-03-01	2119
Renault	Trafic	2.1 D	Kasten	Frontantrieb	Diesel	43	58	Sep 1980	Apr 1989	2024-03-01	2120
Renault	Trafic	2.1 D	Bus	Frontantrieb	Diesel	43	58	May 1989	Jun 1994	2024-03-01	2121
Renault	Trafic	2.5 D	Bus	Frontantrieb	Diesel	55	75	May 1989	Mar 2001	2024-03-01	2122
Renault	Trafic	2.2	Bus	Frontantrieb	Benzin	70	95	May 1989	Jun 1994	2024-03-01	2123
Renault	Espace ii	2.1 TD	Großraumlimousine	Frontantrieb	Diesel	65	88	Jan 1991	Oct 1996	2024-03-01	2124
Renault	Espace ii	2.2	Großraumlimousine	Frontantrieb	Benzin	79	108	Jan 1991	Oct 1996	2024-03-01	2125
Renault	Espace ii	2.8 V6	Großraumlimousine	Frontantrieb	Benzin	110	150	Jan 1991	Oct 1996	2024-03-01	2126
Renault	Clio i	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Jan 1991	Sep 1998	2026-05-01	2127
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	43	58	May 1990	Sep 1998	2026-05-01	2128
Renault	Clio i	1.4	Schrägheck	Frontantrieb	Benzin	58	79	Jan 1991	Sep 1998	2026-05-01	2129
Renault	Clio i	1.8 16V	Schrägheck	Frontantrieb	Benzin	99	135	Jan 1991	Mar 1996	2026-05-01	2130
Renault	Clio i	1.8	Schrägheck	Frontantrieb	Benzin	65	88	Jan 1991	Sep 1998	2026-05-01	2131
Renault	Twingo	1.2	Schrägheck	Frontantrieb	Benzin	40	55	Mar 1993	Oct 1996	2026-05-01	2132
Renault	Safrane i	3.0 Biturbo 4X4	Schrägheck	Allrad	Benzin	193	262	Feb 1993	Jul 1996	2024-03-01	2133
Citroën	2	4	Stufenheck	Frontantrieb	Benzin	12	16	Mar 1963	Feb 1970	2024-03-01	2134
Citroën	2	4	Stufenheck	Frontantrieb	Benzin	17	23	Jan 1970	Dec 1975	2024-03-01	2135
Citroën	2	6	Stufenheck	Frontantrieb	Benzin	18	24	Sep 1975	Jun 1981	2024-03-01	2136
Citroën	2	6	Stufenheck	Frontantrieb	Benzin	20	27	Aug 1979	Jul 1990	2024-03-01	2137
Citroën	2	6	Stufenheck	Frontantrieb	Benzin	21	29	Feb 1970	Oct 1985	2024-03-01	2138
Citroën	Dyane	4	Schrägheck	Frontantrieb	Benzin	17	23	Apr 1968	Jul 1975	2024-03-01	2139


--- Round 1 / 首次发送 ---
## 更新点

* 首轮按物理车身聚类，闭合 Renault 19 I/II 的 Sedan、Hatchback、Convertible 四个尺寸组；R19 II Hatchback 按来源明确的 3 门、5 门分别建立映射，但因三维一致而复用同一尺寸组。([汽车数据网][1])
* 闭合 Renault 25、Espace I Phase I/II、Clio I、Twingo I。跨 1988 年 Espace I 改款的 Ktype 已拆成 `prefl`、`facelift` 映射；Clio I 按来源覆盖的 3 门、5 门分别建立映射。([汽车数据网][2])
* 闭合 Fuego Turbo、Safrane Biturbo 和 Citroën 2CV；宽度均采用来源明确标注的 without mirrors 数值。([汽车目录][3])
* Renault 21 暂未批量落盘：同一 Phase II Hatchback 按发动机存在 1385、1390、1400 mm 等不同高度，Turbo Sedan 也有独立外廓，需先完成发动机与外廓分组，不能直接套用单一代际尺寸。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100 个
* READY 映射：58 行，覆盖 44 个输入 Ktype
* PENDING：56 个输入 Ktype
* 已确认尺寸组：12 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2047	2047	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2048	2048	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2049_3dr	2049	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2049_5dr	2049	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2050	2050	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2051_3dr	2051	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2051_5dr	2051	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2052	2052	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2053_3dr	2053	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2053_5dr	2053	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2054	2054	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2055	2055	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2056	2056	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2057	2057	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2058_3dr	2058	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2058_5dr	2058	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2059	2059	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2061	2061	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2062	2062	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2063_3dr	2063	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2063_5dr	2063	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2064	2064	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2065_3dr	2065	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2065_5dr	2065	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2094	2094	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2095	2095	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2096	2096	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2097	2097	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2098	2098	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2099	2099	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2100	2100	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2101	2101	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2102	2102	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2103	2103	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-TURBO-01	HIGH	欧洲规格Turbo外部套件外廓。	READY
2106_prefl	2106	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2106_facelift	2106	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2107_prefl	2107	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2107_facelift	2107	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2108	2108	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Quadra生产期对应Phase II外廓。	READY
2109_prefl	2109	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2109_facelift	2109	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2127_3dr	2127	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2127_5dr	2127	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2128_3dr	2128	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2128_5dr	2128	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2129_3dr	2129	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2129_5dr	2129	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2130_3dr	2130	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2130_5dr	2130	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2131_3dr	2131	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2131_5dr	2131	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2132	2132	Hatchback	Renault Twingo I		3	EU-RENAULT-TWINGO-I-HATCHBACK-01	HIGH	Twingo I三门掀背外廓。	READY
2133	2133	Hatchback	Renault Safrane I	B545	5	EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	HIGH	Biturbo宽体及外部套件独立外廓。	READY
2134	2134	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV标准四门快背式轿车外廓。	READY
2135	2135	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV标准四门快背式轿车外廓。	READY
2136	2136	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
2137	2137	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
2138	2138	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-19-I-SEDAN-L53-01	4262	1694	1412	Auto-Data Renault 19 I Chamade (L53)	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417	Auto-Data Renault 19 Chamade (L53) facelift 1992	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-generation-2188
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417	Auto-Data Renault 19 (B/C53) facelift 1992	https://www.auto-data.net/en/renault-19-b-c53-facelift-1992-generation-2186
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410	Auto-Data Renault 19 Cabriolet (D53) facelift 1992	https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-generation-2187
EU-RENAULT-25-B29-HATCHBACK-01	4715	1805	1415	Auto-Data Renault 25 (B29)	https://www.auto-data.net/en/renault-25-b29-generation-2140
EU-RENAULT-FUEGO-136-COUPE-TURBO-01	4385	1692	1336	Automobile-Catalog 1984 Renault Fuego Turbo Europe	https://www.automobile-catalog.com/car/1984/49445/renault_fuego_turbo.html
EU-RENAULT-ESPACE-I-MPV-PHASE1-01	4250	1777	1660	Auto-Data Renault Espace I (J11/13)	https://www.auto-data.net/en/renault-espace-i-j11-13-generation-2144
EU-RENAULT-ESPACE-I-MPV-PHASE2-01	4365	1777	1670	Auto-Data Renault Espace I Phase II 1988	https://www.auto-data.net/en/renault-espace-i-j11-13-phase-ii-1988-generation-5538
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Auto-Data Renault Clio I Phase I	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423	Auto-Data Renault Twingo I	https://www.auto-data.net/en/renault-twingo-i-generation-2176
EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	4770	1820	1440	Automobile-Catalog 1993 Renault Safrane Biturbo	https://www.automobile-catalog.com/car/1993/2945285/renault_safrane_biturbo.html
EU-CITROEN-2CV-SEDAN-01	3830	1480	1600	Automobile-Catalog 1970 Citroën 2CV AZL; Automobile-Catalog 1970 Citroën 2CV4; Automobile-Catalog 1980 Citroën 2CV6	https://www.automobile-catalog.com/car/1970/126680/citroen_2_cv_azl.html;https://www.automobile-catalog.com/car/1970/30005/citroen_2_cv_4.html;https://www.automobile-catalog.com/car/1980/126530/citroen_2_cv_6.html
```

## 下一步优先处理

1. 优先一次性闭合 Renault 21 的 Sedan、Hatchback、Wagon、Turbo 四类外廓及 Phase I/II 边界，预计覆盖 2071–2093。
2. 聚类 Renault Rapid 与 Trafic I 的客车/厢式车、轴距及车顶分支，避免按发动机重复查询。
3. 补齐 Renault 18 Variable、Renault 19 I Hatchback、Renault 20/30，以及 Fuego 非 Turbo 的改款前后尺寸。
4. 最后处理 Espace II 三个发动机版本的高度冲突，以及跨多个改款阶段的 Citroën Dyane Ktype 2139。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191 "Renault 19 I Chamade (L53) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-25-b29-generation-2140 "Renault 25 (B29) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1984/49445/renault_fuego_turbo.html?utm_source=chatgpt.com "1984 Renault Fuego Turbo Specs Review (97 kW / 132 PS / 130 hp) (for Europe )"
[4]: https://www.automobile-catalog.com/car/1990/2940455/renault_21_gtx_hatchback.html?utm_source=chatgpt.com "1990 Renault 21 GTX Hatchback Specs Review (88.5 kW / 120 PS / 119 hp) (for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新增闭合 Renault 19 I Hatchback、Renault 20、Renault 30、Renault 21 Sedan/Hatchback/Wagon，以及标准版 Renault Fuego，共 12 个尺寸组。
* Renault 21 按 1989 年改款边界拆分；Turbo Sedan 使用独立外廓，Hatchback 与 Wagon 分别按 L48、K48 建组。([汽车目录][1])
* Renault 20、Renault 30 跨 1980 年中期外廓变化的 Ktype 已拆成 `prefl` 与 `facelift` 分支；Fuego 非 Turbo 版本复用同一标准 Coupe 尺寸组。([汽车目录][2])
* Renault 19 I Hatchback 按 C53 三门与 B53 五门建立派生映射，两类门数复用同一尺寸组。([汽车数据网][3])

## 2. 当前批次进度

* READY 映射：107 行
* 已覆盖输入 Ktype：79/100
* PENDING 输入 Ktype：21/100
* 已确认尺寸组：24
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2043_3dr	2043	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2043_5dr	2043	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2044_3dr	2044	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2044_5dr	2044	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2045_3dr	2045	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2045_5dr	2045	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2046_3dr	2046	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2046_5dr	2046	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2060_3dr	2060	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2060_5dr	2060	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2066	2066	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2067_prefl	2067	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-PREFL-01	MEDIUM	Ktype跨1980年中期外廓变化；前期分支。	READY
2067_facelift	2067	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨1980年中期外廓变化；后期分支。	READY
2068	2068	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2069	2069	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2070_prefl	2070	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	MEDIUM	Ktype跨1980年中期外廓变化；前期分支。	READY
2070_facelift	2070	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨1980年中期外廓变化；后期分支。	READY
2071	2071	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	B48改款前四门外廓。	READY
2072_prefl	2072	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2072_facelift	2072	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2073_prefl	2073	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2073_facelift	2073	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2074	2074	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	B48改款前四门外廓。	READY
2075_prefl	2075	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Turbo Phase I分支。	READY
2075_facelift	2075	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Turbo Phase II分支。	READY
2076_prefl	2076	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2076_facelift	2076	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2077	2077	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2078_prefl	2078	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2078_facelift	2078	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2079_prefl	2079	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2079_facelift	2079	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2080	2080	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2081	2081	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	B48改款后四门外廓。	READY
2082	2082	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2083	2083	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2084	2084	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2085_prefl	2085	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2085_facelift	2085	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2086	2086	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2087	2087	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2088	2088	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2089	2089	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2090	2090	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2091	2091	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2092	2092	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2093	2093	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2104	2104	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	HIGH	136三门标准Coupe外廓。	READY
2105	2105	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	HIGH	136三门标准Coupe外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-19-I-HATCHBACK-BC53-01	4156	1694	1412	CarSpecsGuru Renault 19 I Hatchback 5-door	https://www.carspecsguru.com/renault/19/2574/3935/modification-26768
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435	Automobile-Catalog 1980 Renault 20 TS	https://www.automobile-catalog.com/car/1980/55385/renault_20_ts.html
EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	4520	1732	1435	Automobile-Catalog 1980 Renault 20 TX	https://www.automobile-catalog.com/car/1980/43550/renault_20_tx.html
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431	Automobile-Catalog 1978 Renault 30 TX	https://www.automobile-catalog.com/car/1978/2930000/renault_30_tx.html
EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	4500	1732	1431	Automobile-Catalog 1981 Renault 30 TX	https://www.automobile-catalog.com/car/1981/36530/renault_30_tx.html
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414	Automobile-Catalog 1987 Renault 21 Turbo DX	https://www.automobile-catalog.com/car/1987/2939810/renault_21_turbo_dx.html
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415	Auto-Data Renault 21 B48	https://www.auto-data.net/en/renault-21-b48-generation-2126
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	4498	1714	1400	Automobile-Catalog 1988 Renault 21 Turbo	https://www.automobile-catalog.com/car/1988/56855/renault_21_turbo.html
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	4510	1722	1385	Automobile-Catalog 1991 Renault 21 Turbo	https://www.automobile-catalog.com/car/1991/2940860/renault_21_turbo.html
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415	Auto-Data Renault 21 Hatchback L48	https://www.auto-data.net/en/renault-21-hatchback-l48-generation-2128
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450	Auto-Data Renault 21 Combi K48	https://www.auto-data.net/en/renault-21-combi-k48-generation-2127
EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	4358	1692	1315	Automobile-Catalog 1982 Renault Fuego GTX	https://www.automobile-catalog.com/car/1982/2931965/renault_fuego_gtx.html
```

## 5. 下一步优先处理

1. 闭合 Renault 18 Variable 的 1979–1982、1982–1984、1984–1986 外廓变化，并拆分跨阶段 Ktype 2040–2042。
2. 处理 Espace II、Rapid 与 Trafic I，优先确认 Rapid 改款边界以及 Trafic 的轴距、车顶和 Bus/Kasten 分支。
3. 补齐 Espace II、Dyane，以及尚未处理的 Renault 19 I/II 映射边界修正。
4. 检查剩余 21 个 Ktype，达到 `PENDING=0` 后直接组装两张最终完整 TSV 和指定下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/renault/21/21/1986.html?utm_source=chatgpt.com "1986 Renault 21 phase-I Sedan full range specs"
[2]: https://www.automobile-catalog.com/car/1980/2929955/renault_20_td.html?utm_source=chatgpt.com "1980 Renault 20 TD Specs Review (47 kW / 64 PS / 63 hp) (up to July 1980 for Europe )"
[3]: https://www.auto-data.net/en/renault-19-i-b-c53-1.7-b-c53c-90hp-10784 "Renault 19 I (B/C53) 1.7 (B/C53C) (90 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Renault Espace II 的三个前驱版本；2.1 TD、2.2 与 2.8 V6 均链接同一 J63 前驱尺寸组，高度采用对应前驱版本的 1693 mm，不使用 Quadra 的 1703 mm。([汽车数据网][1])
* Ktype `2139` 覆盖 Citroën Dyane I 三个外廓阶段，拆分为 Phase I、Phase II、Phase III 三行及三个尺寸组。([汽车数据网][2])

## 2. 当前批次进度

* READY 映射：113 行
* 已覆盖输入 Ktype：83/100
* PENDING 输入 Ktype：17/100
* 已确认尺寸组：28
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2124	2124	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2125	2125	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2126	2126	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2139_phase1	2139	Hatchback	Citroën Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE1-01	MEDIUM	Ktype跨三个外廓阶段；1968-1970分支。	READY
2139_phase2	2139	Hatchback	Citroën Dyane I Phase II		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE2-01	MEDIUM	Ktype跨三个外廓阶段；1970-1974分支。	READY
2139_phase3	2139	Hatchback	Citroën Dyane I Phase III		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE3-01	MEDIUM	Ktype跨三个外廓阶段；1975分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693	Auto-Data Renault Espace II 2.1 TD;Auto-Data Renault Espace II 2.2i;Auto-Data Renault Espace II 2.8 V6	https://www.auto-data.net/en/renault-espace-ii-j63-2.1-td-88hp-10508;https://www.auto-data.net/en/renault-espace-ii-j63-2.2i-107hp-10510;https://www.auto-data.net/en/renault-espace-ii-j63-2.8-v6-150hp-10512
EU-CITROEN-DYANE-I-HATCHBACK-PHASE1-01	3905	1500	1540	Auto-Data Citroen Dyane I Phase I	https://www.auto-data.net/en/citroen-dyane-i-phase-i-generation-3338
EU-CITROEN-DYANE-I-HATCHBACK-PHASE2-01	3870	1500	1540	Auto-Data Citroen Dyane I Phase II	https://www.auto-data.net/en/citroen-dyane-i-phase-ii-generation-7607
EU-CITROEN-DYANE-I-HATCHBACK-PHASE3-01	3874	1500	1525	Auto-Data Citroen Dyane I Phase III	https://www.auto-data.net/en/citroen-dyane-i-phase-iii-generation-7610
```

## 5. 下一步优先处理

1. 优先闭合 Renault Rapid 的 Phase I、II、III 外廓边界，覆盖 Ktype `2110–2117`。
2. 随后处理 Renault 18 Wagon 的外廓冲突，以及 Renault Trafic I 改款前后 Bus/Kasten、轴距和车顶分支。
3. 剩余 17 个 Ktype 清零后，下一轮直接输出两张最终完整 TSV 和指定 sandbox 下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-espace-ii-j63-2.8-v6-150hp-automatic-10509?utm_source=chatgpt.com "Renault Espace II (J63) 2.8 V6 (150 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/citroen-dyane-i-phase-iii-generation-7610 "Citroen Dyane I (Phase III) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 闭合 Renault 18 Wagon 的三套外廓：早期 `4451×1682×1402`、1982 更新型 `4487×1689×1402`、Phase II `4487×1696×1402`；跨阶段 Ktype 已拆分映射。([汽车目录][1])
* 闭合 Renault Rapid 的三套外廓：Phase I 早期 `3982×1588×1790`、1989 更新型 `3982×1588×1803`、Phase II–III `4056×1566×1776`。Phase II 与 Phase III 三维一致，复用同一尺寸组。([汽车目录][2])
* 本轮覆盖 Ktype `2040–2042`、`2110–2117`。
* 剩余仅 Renault Trafic I 的 6 个 Ktype。

## 2. 当前批次进度

* READY 映射：136 行
* 已覆盖输入 Ktype：94/100
* PENDING 输入 Ktype：6/100
* 已确认尺寸组：34
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2040_pre82	2040	Wagon	Renault 18 Break Early	135	5	EU-RENAULT-18-135-WAGON-EARLY-01	MEDIUM	Ktype跨早期与1982更新外廓；早期分支。	READY
2040_1982	2040	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨早期与1982更新外廓；1982分支。	READY
2041_prefl	2041	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨Phase II改款；改款前分支。	READY
2041_facelift	2041	Wagon	Renault 18 Break Phase II	135	5	EU-RENAULT-18-135-WAGON-PHASE2-01	MEDIUM	Ktype跨Phase II改款；改款后分支。	READY
2042_early	2042	Wagon	Renault 18 Break Early	135	5	EU-RENAULT-18-135-WAGON-EARLY-01	MEDIUM	Ktype跨三套外廓阶段；早期分支。	READY
2042_1982	2042	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨三套外廓阶段；1982更新分支。	READY
2042_facelift	2042	Wagon	Renault 18 Break Phase II	135	5	EU-RENAULT-18-135-WAGON-PHASE2-01	MEDIUM	Ktype跨三套外廓阶段；Phase II分支。	READY
2110_pre89	2110	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨1989车高更新；早期外廓。	READY
2110_1989update	2110	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨1989车高更新；后期外廓。	READY
2111_pre89	2111	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2111_1989update	2111	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2111_facelift	2111	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2112_pre89	2112	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨1989车高更新；早期外廓。	READY
2112_1989update	2112	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨1989车高更新；后期外廓。	READY
2113_pre89	2113	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2113_1989update	2113	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2113_facelift	2113	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2114	2114	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
2115	2115	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
2116_pre89	2116	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2116_1989update	2116	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2116_facelift	2116	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2117	2117	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-18-135-WAGON-EARLY-01	4451	1682	1402	Automobile-Catalog 1980 Renault 18 Break TL BV4	https://www.automobile-catalog.com/car/1980/2930660/renault_18_break_tl.html
EU-RENAULT-18-135-WAGON-1982-01	4487	1689	1402	Automobile-Catalog 1982 Renault 18 Break TX Automatic	https://www.automobile-catalog.com/car/1982/2931695/renault_18_break_tx_automatic.html
EU-RENAULT-18-135-WAGON-PHASE2-01	4487	1696	1402	Automobile-Catalog 1986 Renault 18 Break	https://www.automobile-catalog.com/car/1986/2932535/renault_18_break.html
EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	3982	1588	1790	Automobile-Catalog 1987 Renault Express Break Rapid Combi 1.1	https://www.automobile-catalog.com/car/1987/52490/renault_express_1_1.html
EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	3982	1588	1803	Automobile-Catalog 1991 Renault Rapid Combi 1.4 catalyst	https://www.automobile-catalog.com/car/1991/2943980/renault_rapid_combi_1_4_catalyst.html
EU-RENAULT-RAPID-PHASE23-VAN-01	4056	1566	1776	Automobilisto Renault Express Restyling 1;Automobilisto Renault Express Restyling 2	https://automobilisto.de/ro/catalog/renault/express/12400/18377;https://automobilisto.de/ro/catalog/renault/express/12402/18381
```

## 5. 下一步优先处理

1. 闭合 Renault Trafic I Phase I 的 Bus 与 Kasten 标准轴距、标准车顶外廓。
2. 闭合 1989 Phase II 加长车头外廓，并处理跨 1989 改款的 Ktype `2119–2120`。
3. 判断 Ktype `2122` 是否需继续拆分 1994 Phase III；完成 `2118–2123` 后立即进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/2930660/renault_18_break_tl.html?utm_source=chatgpt.com "1980 Renault 18 Break TL BV4 Specs Review (47.1 kW / 64 PS / 63 hp) (since September 1980 for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/52490/renault_express_1_1.html?utm_source=chatgpt.com "1987 Renault Express Break (Rapid Combi) 1.1 Specs Review (33 kW / 45 PS / 44 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2001-2100_ktype_dimension_mapping_final.tsv
- all_2001-2100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合剩余 Renault Trafic I Ktype `2118–2123`。Phase I 标准轴距低顶外廓采用 `4337×1905×2037 mm`，1989 年改款后的标准外廓采用 `4542×1905×2037 mm`；Ktype `2122` 的 1995 年更新未发现标准轴距低顶三维变化，因此以 Phase II–III 稳定尺寸组落盘。([CarSpecsGuru][1])
* 已完成固定表头、唯一主键、100 个输入 Ktype 覆盖、映射外键闭合、尺寸与来源非空检查。
* 已生成两个任务指定文件。

## 2. 当前批次进度

* 输入 Ktype：100/100
* READY 映射：142 行
* PENDING：0
* DIMENSION_GROUP：38 个
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一及引用闭合：通过
* 三维、来源与 URL 非空：通过

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2040_pre82	2040	Wagon	Renault 18 Break Early	135	5	EU-RENAULT-18-135-WAGON-EARLY-01	MEDIUM	Ktype跨早期与1982更新外廓；早期分支。	READY
2040_1982	2040	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨早期与1982更新外廓；1982分支。	READY
2041_prefl	2041	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨Phase II改款；改款前分支。	READY
2041_facelift	2041	Wagon	Renault 18 Break Phase II	135	5	EU-RENAULT-18-135-WAGON-PHASE2-01	MEDIUM	Ktype跨Phase II改款；改款后分支。	READY
2042_early	2042	Wagon	Renault 18 Break Early	135	5	EU-RENAULT-18-135-WAGON-EARLY-01	MEDIUM	Ktype跨三套外廓阶段；早期分支。	READY
2042_1982	2042	Wagon	Renault 18 Break 1982 Update	135	5	EU-RENAULT-18-135-WAGON-1982-01	MEDIUM	Ktype跨三套外廓阶段；1982更新分支。	READY
2042_facelift	2042	Wagon	Renault 18 Break Phase II	135	5	EU-RENAULT-18-135-WAGON-PHASE2-01	MEDIUM	Ktype跨三套外廓阶段；Phase II分支。	READY
2043_3dr	2043	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2043_5dr	2043	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2044_3dr	2044	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2044_5dr	2044	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2045_3dr	2045	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2045_5dr	2045	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2046_3dr	2046	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2046_5dr	2046	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2047	2047	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2048	2048	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2049_3dr	2049	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2049_5dr	2049	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2050	2050	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2051_3dr	2051	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2051_5dr	2051	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2052	2052	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2053_3dr	2053	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2053_5dr	2053	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2054	2054	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2055	2055	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2056	2056	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2057	2057	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2058_3dr	2058	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2058_5dr	2058	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2059	2059	Sedan	Renault 19 I	L53	4	EU-RENAULT-19-I-SEDAN-L53-01	HIGH	L53四门Chamade外廓。	READY
2060_3dr	2060	Hatchback	Renault 19 I	C53	3	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	C53三门分支；与B53五门分支共用三维。	READY
2060_5dr	2060	Hatchback	Renault 19 I	B53	5	EU-RENAULT-19-I-HATCHBACK-BC53-01	MEDIUM	B53五门分支；与C53三门分支共用三维。	READY
2061	2061	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2062	2062	Sedan	Renault 19 II	L53	4	EU-RENAULT-19-II-SEDAN-L53-01	HIGH	L53改款四门Chamade外廓。	READY
2063_3dr	2063	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2063_5dr	2063	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2064	2064	Convertible	Renault 19 II	D53	2	EU-RENAULT-19-II-CONVERTIBLE-D53-01	HIGH	D53改款敞篷外廓。	READY
2065_3dr	2065	Hatchback	Renault 19 II		3	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2065_5dr	2065	Hatchback	Renault 19 II		5	EU-RENAULT-19-II-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2066	2066	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2067_prefl	2067	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-PREFL-01	MEDIUM	Ktype跨1980年中期外廓变化；前期分支。	READY
2067_facelift	2067	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨1980年中期外廓变化；后期分支。	READY
2068	2068	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2069	2069	Hatchback	Renault 20	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	HIGH	1980年中期以后外廓。	READY
2070_prefl	2070	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-PREFL-01	MEDIUM	Ktype跨1980年中期外廓变化；前期分支。	READY
2070_facelift	2070	Hatchback	Renault 30	127	5	EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	MEDIUM	Ktype跨1980年中期外廓变化；后期分支。	READY
2071	2071	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	B48改款前四门外廓。	READY
2072_prefl	2072	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2072_facelift	2072	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2073_prefl	2073	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2073_facelift	2073	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2074	2074	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	B48改款前四门外廓。	READY
2075_prefl	2075	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Turbo Phase I分支。	READY
2075_facelift	2075	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Turbo Phase II分支。	READY
2076_prefl	2076	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2076_facelift	2076	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2077	2077	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2078_prefl	2078	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2078_facelift	2078	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2079_prefl	2079	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2079_facelift	2079	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2080	2080	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2081	2081	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	B48改款后四门外廓。	READY
2082	2082	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2083	2083	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2084	2084	Hatchback	Renault 21 Phase II	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
2085_prefl	2085	Sedan	Renault 21 Phase I	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	Ktype跨1989改款；Phase I分支。	READY
2085_facelift	2085	Sedan	Renault 21 Phase II	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	Ktype跨1989改款；Phase II分支。	READY
2086	2086	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2087	2087	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2088	2088	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2089	2089	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2090	2090	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2091	2091	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2092	2092	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2093	2093	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
2094	2094	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2095	2095	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2096	2096	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2097	2097	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2098	2098	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2099	2099	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2100	2100	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2101	2101	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2102	2102	Hatchback	Renault 25	B29	5	EU-RENAULT-25-B29-HATCHBACK-01	HIGH	B29五门掀背外廓。	READY
2103	2103	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-TURBO-01	HIGH	欧洲规格Turbo外部套件外廓。	READY
2104	2104	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	HIGH	136三门标准Coupe外廓。	READY
2105	2105	Coupe	Renault Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	HIGH	136三门标准Coupe外廓。	READY
2106_prefl	2106	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2106_facelift	2106	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2107_prefl	2107	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2107_facelift	2107	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2108	2108	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Quadra生产期对应Phase II外廓。	READY
2109_prefl	2109	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE1-01	MEDIUM	Ktype跨1988外廓变更；Phase I分支。	READY
2109_facelift	2109	MPV	Renault Espace I		5	EU-RENAULT-ESPACE-I-MPV-PHASE2-01	MEDIUM	Ktype跨1988外廓变更；Phase II分支。	READY
2110_pre89	2110	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨1989车高更新；早期外廓。	READY
2110_1989update	2110	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨1989车高更新；后期外廓。	READY
2111_pre89	2111	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2111_1989update	2111	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2111_facelift	2111	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2112_pre89	2112	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨1989车高更新；早期外廓。	READY
2112_1989update	2112	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨1989车高更新；后期外廓。	READY
2113_pre89	2113	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2113_1989update	2113	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2113_facelift	2113	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2114	2114	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
2115	2115	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
2116_pre89	2116	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	MEDIUM	Ktype跨三套外廓；Phase I早期。	READY
2116_1989update	2116	Van	Renault Rapid Phase I			EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	MEDIUM	Ktype跨三套外廓；Phase I后期。	READY
2116_facelift	2116	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	MEDIUM	Ktype跨三套外廓；Phase II–III分支。	READY
2117	2117	Van	Renault Rapid Phase II–III			EU-RENAULT-RAPID-PHASE23-VAN-01	HIGH	Phase II与Phase III三维一致。	READY
2118	2118	MPV	Renault Trafic I Phase II		4	EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH	Phase II标准轴距低顶客车外廓。	READY
2119	2119	MPV	Renault Trafic I Phase I		4	EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	MEDIUM	Phase I标准轴距低顶客车与厢式车共用外廓三维。	READY
2120	2120	Van	Renault Trafic I Phase I		4	EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	HIGH	Phase I标准轴距低顶厢式车外廓。	READY
2121	2121	MPV	Renault Trafic I Phase II		4	EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH	Phase II标准轴距低顶客车外廓。	READY
2122	2122	MPV	Renault Trafic I Phase II–III		4	EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	MEDIUM	1995改款未改变标准轴距低顶三维，Phase II–III复用同组。	READY
2123	2123	MPV	Renault Trafic I Phase II		4	EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	HIGH	Phase II标准轴距低顶客车外廓。	READY
2124	2124	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2125	2125	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2126	2126	MPV	Renault Espace II	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	HIGH	J63前驱标准外廓。	READY
2127_3dr	2127	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2127_5dr	2127	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2128_3dr	2128	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2128_5dr	2128	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2129_3dr	2129	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2129_5dr	2129	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2130_3dr	2130	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2130_5dr	2130	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2131_3dr	2131	Hatchback	Renault Clio I		3	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖三门分支；与五门分支共用三维。	READY
2131_5dr	2131	Hatchback	Renault Clio I		5	EU-RENAULT-CLIO-I-HATCHBACK-01	MEDIUM	来源覆盖五门分支；与三门分支共用三维。	READY
2132	2132	Hatchback	Renault Twingo I		3	EU-RENAULT-TWINGO-I-HATCHBACK-01	HIGH	Twingo I三门掀背外廓。	READY
2133	2133	Hatchback	Renault Safrane I	B545	5	EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	HIGH	Biturbo宽体及外部套件独立外廓。	READY
2134	2134	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV标准四门快背式轿车外廓。	READY
2135	2135	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV标准四门快背式轿车外廓。	READY
2136	2136	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
2137	2137	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
2138	2138	Sedan	Citroën 2CV		4	EU-CITROEN-2CV-SEDAN-01	HIGH	2CV4与2CV6共用标准外廓。	READY
2139_phase1	2139	Hatchback	Citroën Dyane I Phase I		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE1-01	MEDIUM	Ktype跨三个外廓阶段；1968-1970分支。	READY
2139_phase2	2139	Hatchback	Citroën Dyane I Phase II		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE2-01	MEDIUM	Ktype跨三个外廓阶段；1970-1974分支。	READY
2139_phase3	2139	Hatchback	Citroën Dyane I Phase III		5	EU-CITROEN-DYANE-I-HATCHBACK-PHASE3-01	MEDIUM	Ktype跨三个外廓阶段；1975分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2001-2100_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-18-135-WAGON-EARLY-01	4451	1682	1402	Automobile-Catalog 1980 Renault 18 Break TL BV4	https://www.automobile-catalog.com/car/1980/2930660/renault_18_break_tl.html
EU-RENAULT-18-135-WAGON-1982-01	4487	1689	1402	Automobile-Catalog 1982 Renault 18 Break TX Automatic	https://www.automobile-catalog.com/car/1982/2931695/renault_18_break_tx_automatic.html
EU-RENAULT-18-135-WAGON-PHASE2-01	4487	1696	1402	Automobile-Catalog 1986 Renault 18 Break	https://www.automobile-catalog.com/car/1986/2932535/renault_18_break.html
EU-RENAULT-19-I-HATCHBACK-BC53-01	4156	1694	1412	CarSpecsGuru Renault 19 I Hatchback 5-door	https://www.carspecsguru.com/renault/19/2574/3935/modification-26768
EU-RENAULT-19-I-SEDAN-L53-01	4262	1694	1412	Auto-Data Renault 19 I Chamade (L53)	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-RENAULT-19-II-SEDAN-L53-01	4248	1696	1417	Auto-Data Renault 19 Chamade (L53) facelift 1992	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-generation-2188
EU-RENAULT-19-II-HATCHBACK-01	4162	1696	1417	Auto-Data Renault 19 (B/C53) facelift 1992	https://www.auto-data.net/en/renault-19-b-c53-facelift-1992-generation-2186
EU-RENAULT-19-II-CONVERTIBLE-D53-01	4162	1696	1410	Auto-Data Renault 19 Cabriolet (D53) facelift 1992	https://www.auto-data.net/en/renault-19-cabriolet-d53-facelift-1992-generation-2187
EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	4520	1732	1435	Automobile-Catalog 1980 Renault 20 TX	https://www.automobile-catalog.com/car/1980/43550/renault_20_tx.html
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435	Automobile-Catalog 1980 Renault 20 TS	https://www.automobile-catalog.com/car/1980/55385/renault_20_ts.html
EU-RENAULT-30-127-HATCHBACK-PREFL-01	4520	1732	1431	Automobile-Catalog 1978 Renault 30 TX	https://www.automobile-catalog.com/car/1978/2930000/renault_30_tx.html
EU-RENAULT-30-127-HATCHBACK-FACELIFT-01	4500	1732	1431	Automobile-Catalog 1981 Renault 30 TX	https://www.automobile-catalog.com/car/1981/36530/renault_30_tx.html
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414	Automobile-Catalog 1987 Renault 21 Turbo DX	https://www.automobile-catalog.com/car/1987/2939810/renault_21_turbo_dx.html
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415	Auto-Data Renault 21 B48	https://www.auto-data.net/en/renault-21-b48-generation-2126
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	4498	1714	1400	Automobile-Catalog 1988 Renault 21 Turbo	https://www.automobile-catalog.com/car/1988/56855/renault_21_turbo.html
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	4510	1722	1385	Automobile-Catalog 1991 Renault 21 Turbo	https://www.automobile-catalog.com/car/1991/2940860/renault_21_turbo.html
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415	Auto-Data Renault 21 Hatchback L48	https://www.auto-data.net/en/renault-21-hatchback-l48-generation-2128
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450	Auto-Data Renault 21 Combi K48	https://www.auto-data.net/en/renault-21-combi-k48-generation-2127
EU-RENAULT-25-B29-HATCHBACK-01	4715	1805	1415	Auto-Data Renault 25 (B29)	https://www.auto-data.net/en/renault-25-b29-generation-2140
EU-RENAULT-FUEGO-136-COUPE-TURBO-01	4385	1692	1336	Automobile-Catalog 1984 Renault Fuego Turbo Europe	https://www.automobile-catalog.com/car/1984/49445/renault_fuego_turbo.html
EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	4358	1692	1315	Automobile-Catalog 1982 Renault Fuego GTX	https://www.automobile-catalog.com/car/1982/2931965/renault_fuego_gtx.html
EU-RENAULT-ESPACE-I-MPV-PHASE1-01	4250	1777	1660	Auto-Data Renault Espace I (J11/13)	https://www.auto-data.net/en/renault-espace-i-j11-13-generation-2144
EU-RENAULT-ESPACE-I-MPV-PHASE2-01	4365	1777	1670	Auto-Data Renault Espace I Phase II 1988	https://www.auto-data.net/en/renault-espace-i-j11-13-phase-ii-1988-generation-5538
EU-RENAULT-RAPID-PHASE1-VAN-PRE1989-01	3982	1588	1790	Automobile-Catalog 1987 Renault Express Break Rapid Combi 1.1	https://www.automobile-catalog.com/car/1987/52490/renault_express_1_1.html
EU-RENAULT-RAPID-PHASE1-VAN-1989UPDATE-01	3982	1588	1803	Automobile-Catalog 1991 Renault Rapid Combi 1.4 catalyst	https://www.automobile-catalog.com/car/1991/2943980/renault_rapid_combi_1_4_catalyst.html
EU-RENAULT-RAPID-PHASE23-VAN-01	4056	1566	1776	Automobilisto Renault Express Restyling 1;Automobilisto Renault Express Restyling 2	https://automobilisto.de/ro/catalog/renault/express/12400/18377;https://automobilisto.de/ro/catalog/renault/express/12402/18381
EU-RENAULT-TRAFIC-I-PHASE2-BUS-SWB-LOWROOF-01	4542	1905	2037	AV.BY Renault Trafic I Restyling 2.1 D passenger minibus	https://av.by/catalog/renault_trafic_i-restajling-1989-1997_58329
EU-RENAULT-TRAFIC-I-PHASE1-BUS-SWB-LOWROOF-01	4337	1905	2037	CarSpecsGuru Renault Trafic I 2.1 MT 58 HP Van;Renault Trafic first-generation body styles	https://www.carspecsguru.com/renault/trafic/6051/9242/modification-61781;https://en.wikipedia.org/wiki/Renault_Trafic
EU-RENAULT-TRAFIC-I-PHASE1-VAN-SWB-LOWROOF-01	4337	1905	2037	Drive.Place Renault Trafic I 2.1 MT 58 hp Van	https://renault.drive.place/trafic/i/group_furgon/653123
EU-RENAULT-TRAFIC-I-PHASE23-BUS-SWB-LOWROOF-01	4542	1905	2037	AV.BY Renault Trafic I Restyling 2.1 D passenger minibus;Carwow Renault Trafic I 1994-2001 dimensions	https://av.by/catalog/renault_trafic_i-restajling-1989-1997_58329;https://carwow.by/cars/renault/trafic/specifications/dimensions-and-weight
EU-RENAULT-ESPACE-II-J63-MPV-FWD-01	4429	1795	1693	Auto-Data Renault Espace II 2.1 TD;Auto-Data Renault Espace II 2.2i;Auto-Data Renault Espace II 2.8 V6	https://www.auto-data.net/en/renault-espace-ii-j63-2.1-td-88hp-10508;https://www.auto-data.net/en/renault-espace-ii-j63-2.2i-107hp-10510;https://www.auto-data.net/en/renault-espace-ii-j63-2.8-v6-150hp-10512
EU-RENAULT-CLIO-I-HATCHBACK-01	3709	1616	1395	Auto-Data Renault Clio I Phase I	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423	Auto-Data Renault Twingo I	https://www.auto-data.net/en/renault-twingo-i-generation-2176
EU-RENAULT-SAFRANE-I-BITURBO-HATCHBACK-01	4770	1820	1440	Automobile-Catalog 1993 Renault Safrane Biturbo	https://www.automobile-catalog.com/car/1993/2945285/renault_safrane_biturbo.html
EU-CITROEN-2CV-SEDAN-01	3830	1480	1600	Automobile-Catalog 1970 Citroën 2CV AZL; Automobile-Catalog 1970 Citroën 2CV4; Automobile-Catalog 1980 Citroën 2CV6	https://www.automobile-catalog.com/car/1970/126680/citroen_2_cv_azl.html;https://www.automobile-catalog.com/car/1970/30005/citroen_2_cv_4.html;https://www.automobile-catalog.com/car/1980/126530/citroen_2_cv_6.html
EU-CITROEN-DYANE-I-HATCHBACK-PHASE1-01	3905	1500	1540	Auto-Data Citroen Dyane I Phase I	https://www.auto-data.net/en/citroen-dyane-i-phase-i-generation-3338
EU-CITROEN-DYANE-I-HATCHBACK-PHASE2-01	3870	1500	1540	Auto-Data Citroen Dyane I Phase II	https://www.auto-data.net/en/citroen-dyane-i-phase-ii-generation-7607
EU-CITROEN-DYANE-I-HATCHBACK-PHASE3-01	3874	1500	1525	Auto-Data Citroen Dyane I Phase III	https://www.auto-data.net/en/citroen-dyane-i-phase-iii-generation-7610
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2001-2100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carspecsguru.com/renault/trafic/6051/9242/modification-61781 "Renault Trafic I 2.1 MT 58 HP specifications and technical data | CarSpecsGuru.com"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2001-2100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2001-2100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2590 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（644 行）
