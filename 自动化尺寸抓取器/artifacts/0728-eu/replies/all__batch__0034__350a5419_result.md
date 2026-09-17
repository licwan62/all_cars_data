# 任务：all 第 3301-3400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0034__350a5419


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3301-3400 行

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
all 第 3301-3400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mitsubishi	Sigma	3.0 V6	Stufenheck	Frontantrieb	Benzin	151	205	Dec 1990	Jul 1996	2024-03-01	3418
Mitsubishi	Colt iv	1.3 GLI 12V	Schrägheck	Frontantrieb	Benzin	55	75	Apr 1992	Apr 1996	2024-03-01	3419
Mitsubishi	Colt iv	1.6 Glxi 16V	Schrägheck	Frontantrieb	Benzin	83	113	Apr 1992	Apr 1996	2024-03-01	3420
Mitsubishi	Colt iv	1.8 GTI 16V	Schrägheck	Frontantrieb	Benzin	103	140	Apr 1992	Apr 1996	2024-03-01	3421
Mitsubishi	Space wagon	1.8 TD	Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 1991	Oct 1998	2024-03-01	3422
Mitsubishi	Space wagon	2.0 TD	Großraumlimousine	Frontantrieb	Diesel	60	82	Oct 1992	Oct 1998	2024-03-01	3423
Mitsubishi	Space wagon	1.8	Großraumlimousine	Frontantrieb	Benzin	90	122	Oct 1991	Oct 1998	2024-03-01	3424
Mitsubishi	Space runner	1.8	Großraumlimousine	Frontantrieb	Benzin	90	122	Oct 1991	Aug 1999	2024-03-01	3425
Mitsubishi	Space runner	1.8 4WD	Großraumlimousine	Allrad	Benzin	90	122	Oct 1991	Aug 1999	2024-03-01	3426
Mitsubishi	Space wagon	1.8 4WD	Großraumlimousine	Allrad	Benzin	90	122	Oct 1991	Oct 1998	2024-03-01	3427
Mitsubishi	Space wagon	2	Großraumlimousine	Frontantrieb	Benzin	98	133	Oct 1992	Oct 1998	2024-03-01	3428
Mitsubishi	Space wagon	2.0 4WD	Großraumlimousine	Allrad	Benzin	98	133	Oct 1992	Oct 1998	2024-03-01	3429
Mitsubishi	Galant vii	2.0 Glstd	Stufenheck	Frontantrieb	Diesel	66	90	Nov 1992	Aug 1996	2024-03-01	3430
Mitsubishi	Galant vii	1.8 Glsi	Stufenheck	Frontantrieb	Benzin	93	126	Nov 1992	Aug 1996	2024-03-01	3431
Mitsubishi	Galant vii	2.0 Glsi	Stufenheck	Frontantrieb	Benzin	101	137	Nov 1992	Aug 1996	2024-03-01	3432
Mitsubishi	Galant vii	2.0 Glsi 4WD	Stufenheck	Allrad	Benzin	101	137	Nov 1992	Aug 1996	2024-03-01	3433
Mitsubishi	Galant vii	2.0 V6-24	Stufenheck	Frontantrieb	Benzin	110	150	Nov 1992	Aug 1996	2024-03-01	3434
Mitsubishi	Galant vii	2.5 V6-24 4WD	Stufenheck	Allrad	Benzin	125	170	Nov 1992	Aug 1996	2024-03-01	3435
Mitsubishi	Galant vii	2.0 Glstd	Schrägheck	Frontantrieb	Diesel	66	90	Nov 1992	Aug 1996	2024-03-01	3436
Mitsubishi	Galant vii	1.8 Glsi	Schrägheck	Frontantrieb	Benzin	93	126	Nov 1992	Aug 1996	2024-03-01	3437
Mitsubishi	Galant vii	2.0 Glsi	Schrägheck	Frontantrieb	Benzin	101	137	Nov 1992	Aug 1996	2024-03-01	3438
Mitsubishi	Galant vii	2.0 Glsi 4WD	Schrägheck	Allrad	Benzin	101	137	Nov 1992	Aug 1996	2024-03-01	3439
Mitsubishi	Galant vii	2.0 V6-24	Schrägheck	Frontantrieb	Benzin	110	150	Nov 1992	Aug 1996	2024-03-01	3440
Mitsubishi	Galant vii	2.5 V6-24 4WD	Schrägheck	Allrad	Benzin	125	170	Nov 1992	Aug 1996	2024-03-01	3441
Mitsubishi	Lancer v	2.0 Diesel	Stufenheck	Frontantrieb	Diesel	50	68	Jun 1992	Dec 1996	2024-03-01	3442
Mitsubishi	Lancer v	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Jun 1992	Dec 1996	2024-03-01	3443
Mitsubishi	Lancer v	1.6 16V	Stufenheck	Frontantrieb	Benzin	83	113	Jun 1992	Dec 1996	2024-03-01	3444
Mitsubishi	3000 gt	3.0 Turbo 4WD	Coupe	Allrad	Benzin	210	286	Jan 1990	Aug 1999	2024-03-01	3445
Toyota	Starlet	1	Schrägheck	Heckantrieb	Benzin	33	45	Feb 1978	Sep 1984	2024-03-01	3446
Toyota	Starlet	1.2 S	Schrägheck	Heckantrieb	Benzin	39	53	Oct 1978	Aug 1982	2024-03-01	3447
Toyota	Starlet	1.3 S	Schrägheck	Heckantrieb	Benzin	48	65	Aug 1982	Sep 1984	2024-03-01	3448
Toyota	Starlet	1	Kombi	Heckantrieb	Benzin	33	45	Feb 1978	Sep 1984	2024-03-01	3449
Toyota	Starlet	1	Schrägheck	Frontantrieb	Benzin	40	54	Oct 1984	Dec 1989	2024-03-01	3450
Toyota	Starlet	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1984	Dec 1989	2024-03-01	3451
Toyota	Starlet	1.5 D	Schrägheck	Frontantrieb	Diesel	40	54	Dec 1986	Dec 1989	2024-03-01	3452
Toyota	Starlet	1.3 12V CAT	Schrägheck	Frontantrieb	Benzin	55	75	Dec 1989	Mar 1996	2024-03-01	3453
Toyota	Corolla	1.2	Stufenheck	Heckantrieb	Benzin	40	54	Aug 1974	Dec 1980	2024-03-01	3454
Toyota	Corolla	1.3	Schrägheck	Heckantrieb	Benzin	44	60	Sep 1979	Jan 1982	2024-03-01	3455
Toyota	Corolla	1.3	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1979	Jun 1983	2024-03-01	3456
Toyota	Corolla	1.3	Stufenheck	Heckantrieb	Benzin	48	65	Feb 1982	Jun 1983	2024-03-01	3457
Toyota	Corolla	1.3	Schrägheck	Heckantrieb	Benzin	48	65	Feb 1982	May 1983	2024-03-01	3458
Toyota	Corolla	1.6	Schrägheck	Heckantrieb	Benzin	54	73	Sep 1979	May 1983	2024-03-01	3459
Toyota	Corolla	1.6	Schrägheck	Heckantrieb	Benzin	55	75	Sep 1979	May 1983	2024-03-01	3460
Toyota	Corolla	1.6	Schrägheck	Heckantrieb	Benzin	63	86	Sep 1979	May 1983	2024-03-01	3461
Toyota	Corolla	1.3	Kombi	Heckantrieb	Benzin	44	60	Dec 1979	Jan 1982	2024-03-01	3462
Toyota	Corolla	1.3	Kombi	Heckantrieb	Benzin	48	65	Feb 1982	Aug 1987	2024-03-01	3463
Toyota	Corolla	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Jun 1983	Sep 1984	2024-03-01	3464
Toyota	Corolla	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1985	Aug 1987	2024-03-01	3465
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	54	73	Aug 1985	Aug 1987	2024-03-01	3467
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	62	84	Jun 1983	Aug 1987	2024-03-01	3468
Toyota	Corolla	1.6 GT 16V	Schrägheck	Frontantrieb	Benzin	89	121	Aug 1985	Aug 1987	2024-03-01	3469
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	47	64	Jun 1983	Aug 1987	2024-03-01	3470
Renault	Trafic ii	2.5 DCI 115	Bus	Frontantrieb	Diesel	84	114	Feb 2008	-	2024-03-01	3471
Toyota	Corolla	1.3	Stufenheck	Frontantrieb	Benzin	51	69	Jun 1983	Oct 1984	2024-03-01	3472
Toyota	Corolla	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1984	Aug 1987	2024-03-01	3473
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	62	84	Jun 1983	Aug 1987	2024-03-01	3474
Toyota	Corolla	1.6 GT 16V	Coupe	Heckantrieb	Benzin	91	124	Aug 1983	Jul 1987	2024-03-01	3475
Mazda	121 i	1.1	Schrägheck	Frontantrieb	Benzin	42	57	Oct 1987	Oct 1990	2024-03-01	3476
Mazda	121 i	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1987	Jun 1991	2024-03-01	3477
Mazda	121 i	1.3	Schrägheck	Frontantrieb	Benzin	40	55	Apr 1989	Oct 1990	2024-03-01	3478
Mazda	323 i	1	Schrägheck	Heckantrieb	Benzin	33	45	Jun 1977	May 1980	2024-03-01	3479
Mazda	323 i	1.3	Schrägheck	Heckantrieb	Benzin	44	60	Jan 1977	May 1980	2024-03-01	3480
Mazda	323 i	1.4	Schrägheck	Heckantrieb	Benzin	51	69	May 1978	May 1980	2024-03-01	3481
Mazda	323 i station wagon	1.4	Kombi	Heckantrieb	Benzin	51	69	May 1978	Aug 1982	2024-03-01	3482
Mazda	323 i station wagon	1.5	Kombi	Heckantrieb	Benzin	52	70	Apr 1982	May 1986	2024-03-01	3483
Mitsubishi	Lancer viii	1.8 Di-d	Stufenheck	Frontantrieb	Diesel	85	116	May 2010	-	2024-03-01	3484
Mazda	323 ii hatchback	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Nov 1980	Oct 1985	2024-03-01	3485
Renault	Kangoo	1.6 16V Bivalent	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	60	82	Jun 2005	-	2024-03-01	3487
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	66	90	May 1987	Nov 1992	2024-03-01	3488
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1987	Apr 1992	2024-03-01	3489
Toyota	Corolla	1.6 GTI	Schrägheck	Frontantrieb	Benzin	85	116	Aug 1987	Oct 1994	2024-03-01	3490
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1987	Apr 1992	2024-03-01	3491
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	47	64	Aug 1987	Apr 1992	2024-03-01	3492
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	47	64	Aug 1987	Apr 1992	2024-03-01	3493
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	49	67	Aug 1989	Apr 1992	2024-03-01	3494
Toyota	Corolla	1.8 D	Schrägheck	Frontantrieb	Diesel	49	67	Aug 1989	Apr 1992	2024-03-01	3495
Toyota	Corolla	1.3 I	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1987	Apr 1992	2024-03-01	3496
Toyota	Corolla	1.3 I	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1989	Apr 1992	2024-03-01	3497
Toyota	Corolla	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1987	Apr 1992	2024-03-01	3498
Toyota	Corolla	1.6 4WD	Kombi	Allrad	Benzin	77	105	Apr 1988	Oct 1995	2024-03-01	3499
Toyota	Corolla	1.6 I	Schrägheck	Frontantrieb	Benzin	77	105	Aug 1989	Apr 1992	2024-03-01	3500
Toyota	Corolla	1.3	Kombi	Frontantrieb	Benzin	55	75	Jun 1989	Jun 1992	2024-03-01	3501
Toyota	Corolla	1.8 D	Kombi	Frontantrieb	Diesel	47	64	Dec 1987	Jun 1992	2024-03-01	3502
Toyota	Corolla	1.8 D	Kombi	Frontantrieb	Diesel	49	67	Aug 1989	Jun 1992	2024-03-01	3503
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Aug 1989	Apr 1992	2024-03-01	3504
Toyota	Corona	1.8	Schrägheck	Heckantrieb	Benzin	63	86	Jun 1979	Jul 1981	2024-03-01	3505
Toyota	Cressida	2	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1977	Jul 1981	2024-03-01	3506
Mazda	323 ii hatchback	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Nov 1980	Oct 1985	2024-03-01	3507
Mazda	323 ii	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1981	Oct 1985	2024-03-01	3508
Toyota	Cressida	2	Stufenheck	Heckantrieb	Benzin	77	105	Sep 1980	Apr 1985	2024-03-01	3509
Toyota	Cressida	2.0 GLI	Stufenheck	Heckantrieb	Benzin	80	109	Aug 1982	Jun 1985	2024-03-01	3510
Mazda	323 ii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	55	75	May 1981	Jul 1985	2024-03-01	3511
Toyota	Carina ii	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Jan 1978	Sep 1983	2024-03-01	3512
BMW	1	125 D	Schrägheck	Heckantrieb	Diesel	155	211	Mar 2012	Jun 2019	2024-03-01	3513
Toyota	Carina iii	1.6	Kombi	Heckantrieb	Benzin	54	73	Mar 1981	Jan 1982	2024-03-01	3514
Alpina	B5	Biturbo	Stufenheck	Heckantrieb	Benzin	397	540	Jan 2012	Dec 2014	2024-03-01	3515
Toyota	Carina iv	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1983	Nov 1987	2024-03-01	3516
Toyota	Carina iv	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1983	Nov 1987	2024-03-01	3517
Toyota	Carina iv	1.6	Stufenheck	Frontantrieb	Benzin	62	84	Oct 1983	Nov 1987	2024-03-01	3518
Toyota	Carina iv	1.6	Schrägheck	Frontantrieb	Benzin	62	84	Oct 1983	Nov 1987	2024-03-01	3519


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批前 **28 个输入 Ktype** 的车身边界整理。
* 已闭合 Mitsubishi Sigma、Colt IV、Space Wagon II、Space Runner I、Galant VII、Lancer V 共 **8 个尺寸组**。相同发动机无关配置已批量复用尺寸组，没有逐 Ktype 重复建组。([汽车数据][1])
* `3445` 的欧洲版 3000 GT 286 PS 覆盖改款前后两个物理外廓，已拆为 `prefl` 和 `facelift` 两行；现有资料对欧洲车型长度口径存在冲突，暂不创建尺寸组。([汽车数据][2])

## 当前批次进度

* 已处理输入 Ktype：**28 / 100**
* READY 映射：**27 行，覆盖 27 个 Ktype**
* PENDING 映射：**2 行，覆盖 1 个 Ktype**
* 已确认尺寸组：**8**
* 尚未处理输入 Ktype：**72**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3418	3418	Sedan	Sigma (F16A)	F16A	4	EU-MITSUBISHI-SIGMA-F16A-SEDAN-4D-01	HIGH	F16A四门轿车车身。	READY
3419	3419	Hatchback	Colt IV (CAO)	CA1A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA1A三门掀背车身。	READY
3420	3420	Hatchback	Colt IV (CAO)	CA4A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA4A三门掀背车身。	READY
3421	3421	Hatchback	Colt IV (CAO)	CA5A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA5A三门掀背车身。	READY
3422	3422	MPV	Space Wagon II	N35W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N35W车身。	READY
3423	3423	MPV	Space Wagon II	N38W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N38W车身。	READY
3424	3424	MPV	Space Wagon II	N31W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N31W车身。	READY
3425	3425	MPV	Space Runner I (N1_W,N2_W)	N11W	4	EU-MITSUBISHI-SPACE-RUNNER-I-N11W-MPV-01	HIGH	N11W两驱四门车身。	READY
3426	3426	MPV	Space Runner I (N1_W,N2_W)	N21W	4	EU-MITSUBISHI-SPACE-RUNNER-I-N21W-MPV-01	HIGH	N21W四驱四门车身。	READY
3427	3427	MPV	Space Wagon II	N41W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N41W车身。	READY
3428	3428	MPV	Space Wagon II	N33W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N33W车身。	READY
3429	3429	MPV	Space Wagon II	N43W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N43W车身。	READY
3430	3430	Sedan	Galant VII	E57A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E57A四门轿车车身。	READY
3431	3431	Sedan	Galant VII	E52A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E52A四门轿车车身。	READY
3432	3432	Sedan	Galant VII	E55A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E55A四门轿车车身。	READY
3433	3433	Sedan	Galant VII	E75A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E75A四门四驱轿车车身。	READY
3434	3434	Sedan	Galant VII	E54A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E54A四门轿车车身。	READY
3435	3435	Sedan	Galant VII	E88A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E88A四门四驱轿车车身。	READY
3436	3436	Hatchback	Galant VII	E57A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E57A五门掀背车身。	READY
3437	3437	Hatchback	Galant VII	E52A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E52A五门掀背车身。	READY
3438	3438	Hatchback	Galant VII	E55A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E55A五门掀背车身。	READY
3439	3439	Hatchback	Galant VII	E75A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E75A五门四驱掀背车身。	READY
3440	3440	Hatchback	Galant VII	E54A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E54A五门掀背车身。	READY
3441	3441	Hatchback	Galant VII	E88A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E88A五门四驱掀背车身。	READY
3442	3442	Sedan	Lancer V	CB8A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB8A四门轿车车身。	READY
3443	3443	Sedan	Lancer V	CB1A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB1A四门轿车车身。	READY
3444	3444	Sedan	Lancer V	CB4A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB4A四门轿车车身。	READY
3445_prefl	3445	Coupe	3000 GT Series 1	Z16A	3		MEDIUM	欧洲286 PS改款前车身边界；尺寸口径待闭合。	PENDING: 欧洲286 PS改款前尺寸口径冲突
3445_facelift	3445	Coupe	3000 GT Series 2	Z16A	3		MEDIUM	欧洲286 PS改款后车身边界；尺寸口径待闭合。	PENDING: 欧洲286 PS改款后尺寸口径冲突
```

其中 Lancer V 的 `CB1A`、`CB4A`、`CB8A` 分支均属于相同四门轿车外廓；发动机差异未重复创建尺寸组。([汽车数据][3])

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SIGMA-F16A-SEDAN-4D-01	4750	1775	1435	Auto-Data Mitsubishi Sigma (F16A) 3.0 V6 205 Hp	https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-205hp-automatic-24613
EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	3955	1690	1365	Auto-Data Mitsubishi Colt IV (CAO) 1.3 GLi 12V	https://www.auto-data.net/en/mitsubishi-colt-iv-cao-1.3-gli-12v-ca1a-75hp-15762
EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	4515	1695	1630	Auto-Data Mitsubishi Space Wagon II	https://www.auto-data.net/en/mitsubishi-space-wagon-ii-generation-3427
EU-MITSUBISHI-SPACE-RUNNER-I-N11W-MPV-01	4290	1695	1640	Auto-Data Mitsubishi Space Runner 1.8 N11W	https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-1.8-n11w-122hp-15538
EU-MITSUBISHI-SPACE-RUNNER-I-N21W-MPV-01	4270	1695	1680	Auto-Data Mitsubishi Space Runner 1.8 4x4 N21W	https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-1.8-4x4-n21w-122hp-15539
EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII Sedan	https://www.auto-data.net/en/mitsubishi-galant-vii-2.0-glstd-e57a-90hp-15376
EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII Hatchback	https://www.auto-data.net/en/mitsubishi-galant-vii-hatchback-2.0-v6-24-e54a-150hp-automatic-24622
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data Mitsubishi Lancer V 1.6 16V CB4A	https://www.auto-data.net/en/mitsubishi-lancer-v-1.6-16v-cb4a-113hp-15667
```

## 下一步优先处理

1. 闭合 `3445_prefl` 与 `3445_facelift` 的欧洲市场同配置三维，重点消除不同资料中车长口径冲突。
2. 按 Toyota Starlet 代际和 Hatchback/Wagon 物理分支集中处理 `3446–3453`。
3. 按 Corolla E30、E70、E80 代际及 Sedan、Hatchback、Wagon、Coupe 聚类处理 `3454–3475`，避免因发动机版本重复抓取。
4. 随后处理 Mazda 121/323，并复用已闭合的 Renault Trafic II、Kangoo I 尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-205hp-automatic-24613?utm_source=chatgpt.com "Mitsubishi Sigma (F16A) 3.0 V6 (205 Hp) Automatic /Sedan 1990"
[2]: https://www.auto-data.net/en/mitsubishi-3000-gt-generation-3368?utm_source=chatgpt.com "Mitsubishi 3000 GT | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mitsubishi-lancer-v-1.3-75hp-15664?utm_source=chatgpt.com "Mitsubishi Lancer V 1.3 (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 `3445` 的欧洲版 Mitsubishi 3000 GT 改款前、改款后两个物理外廓，分别采用欧洲 286 PS 车型不含后视镜尺寸。([汽车目录][1])
* 已完成 `3446–3453` Toyota Starlet 的 P60、P70、P80 代际映射；Hatchback 按 3 门、5 门物理车身拆分，Wagon 单独建组。P60、P70 的门数边界及车型代码已按对应代际资料闭合。([维基百科][2])
* 本轮首次创建 **9 个尺寸组**，未重复输出上一轮已闭合尺寸组。

## 当前批次进度

* 已处理输入 Ktype：**36 / 100**
* READY 映射：**44 行，覆盖 36 个 Ktype**
* PENDING／未完成输入：**64 个 Ktype**
* 已确认尺寸组：**17**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3445_prefl	3445	Coupe	3000 GT Series 1	Z16A	3	EU-MITSUBISHI-3000-GT-SERIES-1-COUPE-3D-01	HIGH	欧洲286 PS改款前三门车身。	READY
3445_facelift	3445	Coupe	3000 GT Series 2	Z16A	3	EU-MITSUBISHI-3000-GT-SERIES-2-COUPE-3D-01	HIGH	欧洲286 PS改款后三门车身。	READY
3446_3dr	3446	Hatchback	Starlet II (P60)	KP60	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	P60三门掀背车身。	READY
3446_5dr	3446	Hatchback	Starlet II (P60)	KP60	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	P60五门掀背车身。	READY
3447_3dr	3447	Hatchback	Starlet II (P60)	KP62	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	KP62三门掀背车身。	READY
3447_5dr	3447	Hatchback	Starlet II (P60)	KP62	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	KP62五门掀背车身。	READY
3448_3dr	3448	Hatchback	Starlet II (P60)	KP61	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	KP61三门掀背车身。	READY
3448_5dr	3448	Hatchback	Starlet II (P60)	KP61	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	KP61五门掀背车身。	READY
3449	3449	Wagon	Starlet II (P60)	KP60	5	EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	HIGH	KP60五门旅行车车身。	READY
3450_3dr	3450	Hatchback	Starlet III (P70)	EP70	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	EP70三门掀背车身。	READY
3450_5dr	3450	Hatchback	Starlet III (P70)	EP70	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	EP70五门掀背车身。	READY
3451_3dr	3451	Hatchback	Starlet III (P70)	EP71	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	EP71三门掀背车身。	READY
3451_5dr	3451	Hatchback	Starlet III (P70)	EP71	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	EP71五门掀背车身。	READY
3452_3dr	3452	Hatchback	Starlet III (P70)	NP70	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	NP70三门柴油掀背车身。	READY
3452_5dr	3452	Hatchback	Starlet III (P70)	NP70	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	NP70五门柴油掀背车身。	READY
3453_3dr	3453	Hatchback	Starlet IV (P80)	EP81	3	EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	HIGH	EP81三门掀背车身。	READY
3453_5dr	3453	Hatchback	Starlet IV (P80)	EP81	5	EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	HIGH	EP81五门掀背车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-3000-GT-SERIES-1-COUPE-3D-01	4560	1840	1285	Automobile-Catalog 1992 Mitsubishi 3000 GT Europe	https://www.automobile-catalog.com/car/1992/1967780/mitsubishi_3000_gt.html
EU-MITSUBISHI-3000-GT-SERIES-2-COUPE-3D-01	4570	1840	1285	Automobile-Catalog 1996 Mitsubishi 3000 GT Europe	https://www.automobile-catalog.com/car/1996/1967810/mitsubishi_3000_gt.html
EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	3680	1525	1380	Toyota 75 Years Vehicle Lineage Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006941/index.html
EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	3680	1525	1380	Toyota 75 Years Vehicle Lineage Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006941/index.html
EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	3850	1525	1395	Toyota 75 Years Vehicle Lineage Starlet Van	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006953/index.html
EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	3700	1590	1395	Automobile-Catalog 1985 Toyota Starlet 1.0 DX Europe	https://www.automobile-catalog.com/car/1985/3521570/toyota_starlet_1_0_dx_5-speed.html
EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	3700	1590	1395	Automobile-Catalog 1985 Toyota Starlet 1.0 DX Europe	https://www.automobile-catalog.com/car/1985/3521570/toyota_starlet_1_0_dx_5-speed.html
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	3720	1600	1380	Auto-Data Toyota Starlet IV	https://www.auto-data.net/en/toyota-starlet-iv-generation-811
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	3720	1600	1380	Auto-Data Toyota Starlet IV	https://www.auto-data.net/en/toyota-starlet-iv-generation-811
```

## 下一步优先处理

1. 按 Corolla E30、E70、E80 的 Sedan、Hatchback、Wagon、Coupe 物理车身集中处理 `3454–3475`。
2. 闭合 Renault Trafic II `3471` 的轴距及车顶分支；优先查询历史缓存，确认是否已有可直接复用尺寸组。
3. 随后聚类处理 Mazda 121、323 与 Mitsubishi Lancer VIII，避免按发动机重复创建尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1996/1967810/mitsubishi_3000_gt.html?utm_source=chatgpt.com "1996 Mitsubishi 3000 GT Specs Review (210 kW / 286 PS / 282 hp) (for Europe )"
[2]: https://en.wikipedia.org/wiki/Toyota_Starlet?utm_source=chatgpt.com "Toyota Starlet"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Toyota Corolla E30、E70 与 E80 的 Sedan、Hatchback、Wagon 和 Coupe 主要物理车身，共新增 **8 个尺寸组**。E70 的 KE70、TE71 分支以及 E80 的 AE80、EE80、AE82、CE80、AE86 车身边界已按门数分别关联。([丰田官方网站][1])
* `3469` 已确认属于 Corolla FX Compact E80 三门车身，但不含后视镜宽度尚未闭合，暂时保持 `PENDING`。([汽车数据][2])
* `3471` Renault Trafic II 客运版仍需确认其 Ktype 是否覆盖多个轴距或车顶高度，未创建猜测性派生行。

## 当前批次进度

* 已处理输入 Ktype：**57 / 100**
* READY 映射：**63 行，覆盖 55 个 Ktype**
* PENDING 映射：**2 行，覆盖 2 个 Ktype**
* 尚未处理输入 Ktype：**43**
* 已确认尺寸组：**25**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3454	3454	Sedan	Corolla III (E30)	KE30	4	EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	HIGH	KE30四门轿车车身。	READY
3455	3455	Hatchback	Corolla IV (E70)	KE70	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	HIGH	KE70三门掀背车身。	READY
3456	3456	Sedan	Corolla IV (E70)	KE70	4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	KE70四门轿车车身。	READY
3457	3457	Sedan	Corolla IV (E70)	KE70	4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	KE70四门轿车车身。	READY
3458	3458	Hatchback	Corolla IV (E70)	KE70	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	HIGH	KE70三门掀背车身。	READY
3459	3459	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3460	3460	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3461	3461	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3462	3462	Wagon	Corolla IV (E70)	KE70	5	EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	HIGH	KE70五门旅行车车身。	READY
3463	3463	Wagon	Corolla IV (E70)	KE70	5	EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	HIGH	KE70五门旅行车车身。	READY
3464	3464	Hatchback	Corolla V (E80)	AE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE80五门掀背车身。	READY
3465	3465	Hatchback	Corolla V (E80)	EE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	EE80五门掀背车身。	READY
3467	3467	Hatchback	Corolla V (E80)	AE82	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE82五门掀背车身。	READY
3468	3468	Hatchback	Corolla V (E80)	AE82	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE82五门掀背车身。	READY
3469	3469	Hatchback	Corolla FX Compact V (E80)	AE82	3		MEDIUM	FX Compact三门车身边界已确认。	PENDING: 不含后视镜宽度尚未闭合
3470	3470	Hatchback	Corolla V (E80)	CE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	CE80五门柴油掀背车身。	READY
3471	3471	MPV	Trafic II facelift	X83			MEDIUM	客运版轴距和车顶物理分支尚未闭合。	PENDING: 轴距和车顶分支尚未确认
3472	3472	Sedan	Corolla V (E80)	AE80	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	AE80四门轿车车身。	READY
3473	3473	Sedan	Corolla V (E80)	EE80	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	EE80四门轿车车身。	READY
3474	3474	Sedan	Corolla V (E80)	AE82	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	AE82四门轿车车身。	READY
3475	3475	Coupe	Corolla Coupe V (E80)	AE86	2	EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	HIGH	AE86双门轿跑车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375	Toyota 75 Years Corolla 3rd	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003402/index.html
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385	Tunel Toyota Corolla Hatch IV E70 1.3	https://tunel.az/en/catalog/toyota/corolla/toyota-corolla-hatch-iv-e70/627683fb-a304-4e92-810d-b1348111a6a5
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385	Carsot Toyota Corolla IV E70 Sedan	https://carsot.com/toyota/corolla/toyota-corolla-iv-e70-1979-1983-sedan.html
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341	CarSpecsGuru Toyota Corolla IV E70 1.6	https://www.carspecsguru.com/toyota/corolla/4757/7165/modification-51217
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390	Carsot Toyota Corolla IV E70 Station Wagon	https://carsot.com/toyota/corolla/toyota-corolla-iv-e70-1979-1983-station-wagon-5-door.html
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385	Toyota 75 Years Corolla 5th	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003705A/index.html
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385	Toyota 75 Years Corolla 5th	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003705A/index.html
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335	Auto-Data Toyota Corolla Coupe V E80 1.6 GT 16V	https://www.auto-data.net/en/toyota-corolla-coupe-v-e80-1.6-gt-16v-124hp-3403
```

## 下一步优先处理

1. 闭合 `3469` Corolla FX Compact E80 的不含后视镜宽度。
2. 确认 `3471` Trafic II 客运版实际覆盖的轴距与车顶分支，并一次性创建对应尺寸组。
3. 随后批量处理 Mazda 121、Mazda 323、Mitsubishi Lancer VIII，并优先复用 Renault Kangoo 历史尺寸组。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003402/index.html "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://www.auto-data.net/en/toyota-corolla-hatch-v-e80-1.3-ae80-69hp-3408 "Toyota Corolla Hatch V (E80) 1.3 (AE80) (69 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 `3469` Corolla FX Compact E80 三门车身，采用官方 FX-GT 外廓，并以明确标注不含后视镜宽度的同车身资料交叉确认。([丰田官方网站][1])
* 已将 `3471` Renault Trafic II 客运版原单行 `PENDING` 拆为短轴低顶与长轴低顶两个分支。输入的 `84 kW / 114 hp` 与官方 `2.0 dCi 115` 功率对应；客运版官方提供 L1H1、L2H1 两种外廓。([Manuals+][2])
* 已完成 Mazda 121 I `3476–3478`，三个动力版本复用同一 DA 三门掀背尺寸组。([汽车目录][3])
* 已完成 Mitsubishi Lancer VIII `3484`，关联 CY0 四门轿车尺寸组。([汽车目录][4])

## 当前批次进度

* READY 映射：**70 行**
* READY 覆盖：**61 / 100 个输入 Ktype**
* PENDING／尚未完成：**39 个输入 Ktype**
* 已确认尺寸组：**30**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3469	3469	Hatchback	Corolla FX Compact V (E80)	AE82	3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	HIGH	AE82三门FX Compact车身。	READY
3471_swb	3471	MPV	Trafic II facelift	X83		EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	HIGH	客运版短轴低顶分支。	READY
3471_lwb	3471	MPV	Trafic II facelift	X83		EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	HIGH	客运版长轴低顶分支。	READY
3476	3476	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3477	3477	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3478	3478	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3484	3484	Sedan	Lancer VIII (CY0)	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	CY0四门轿车车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385	Toyota 75 Years Corolla FX; Automobile-Catalog 1987 Toyota Corolla FX	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003729/index.html;https://www.automobile-catalog.com/car/1987/3532310/toyota_corolla_fx_1500_fx-l_automatic.html
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	4782	1904	1960	Renault New Trafic Passenger 2006 press information	https://manuals.plus/m/da24f2e1280e2eff17bc58b46b7e8fcce24887fa0e941a919969bca1c466085e
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	5182	1904	1958	Renault New Trafic Passenger 2006 press information	https://manuals.plus/m/da24f2e1280e2eff17bc58b46b7e8fcce24887fa0e941a919969bca1c466085e
EU-MAZDA-121-I-DA-HATCHBACK-3D-01	3475	1605	1450	Automobile-Catalog 1989 Mazda 121 1.3 L cat	https://www.automobile-catalog.com/car/1989/1639655/mazda_121_1_3_l_cat_60.html
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog 2011 Mitsubishi Lancer 1.8 DI-D; Automaniac Mitsubishi Lancer 1.8 DI-D ClearTec	https://www.automobile-catalog.com/car/2011/1996325/mitsubishi_lancer_1_8_di-d_cleartec_inform.html;https://www.automaniac.org/mitsubishi/2007/8436/mitsubishi-lancer-1.8-di-d-cleartec
```

## 下一步优先处理

1. 集中处理 `3479–3483` Mazda 323 I Hatchback/Wagon，先划分改款前后及 Wagon 外廓。
2. 处理 `3485、3507、3508、3511` Mazda 323 II，按 Hatchback 与 Sedan 聚类。
3. 闭合 `3487` Renault Kangoo 的 Van/MPV 物理分支。
4. 批量处理 `3488–3504` Toyota Corolla E90 的 Sedan、Hatchback 与 Wagon 尺寸组。

推进信号：CONTINUE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003729/index.html?utm_source=chatgpt.com "75 Years of TOYOTA | TOYOTA MOTOR CORPORATION GLOBAL WEBSITE | Vehicle Lineage | In-depth Vehicle Information, Specification"
[2]: https://manuals.plus/m/da24f2e1280e2eff17bc58b46b7e8fcce24887fa0e941a919969bca1c466085e "TRAFIC-DP-GB"
[3]: https://www.automobile-catalog.com/car/1989/1639655/mazda_121_1_3_l_cat_60.html?utm_source=chatgpt.com "1989 Mazda 121 1.3 L cat (60) Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[4]: https://www.automobile-catalog.com/car/2011/1996325/mitsubishi_lancer_1_8_di-d_cleartec_inform.html?utm_source=chatgpt.com "2011 Mitsubishi Lancer 1.8 DI-D ClearTec Inform (man. 6)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已完成 Mazda 323 I 的 Hatchback 与 Station Wagon 车身簇。Hatchback 按 3 门、5 门拆分；Wagon 因 1979 年外廓高度变化拆分为改款前后尺寸组。([维基百科][1])
* 已完成 Mazda 323 II BD 的 Hatchback 与 Sedan 车身簇。1983 年改款后车长增加 10 mm，已按门数和改款阶段建立独立尺寸组。([汽车目录][2])
* 已闭合 `3487` Renault Kangoo I facelift 标准短轴车身。输入的 Kasten/Großraumlimousine 共用相同外部壳体，本轮只创建一个尺寸组。([汽车目录][3])

## 当前批次进度

* READY 映射：**92 行**
* READY 覆盖：**71 / 100 个输入 Ktype**
* PENDING／尚未处理：**29 个输入 Ktype**
* 已确认尺寸组：**41**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3479_3dr	3479	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3479_5dr	3479	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3480_3dr	3480	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3480_5dr	3480	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3481_3dr	3481	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3481_5dr	3481	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3482_prefl	3482	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-PREFL-01	HIGH	改款前五门旅行车车身。	READY
3482_facelift	3482	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	HIGH	改款后五门旅行车车身。	READY
3483	3483	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	HIGH	改款后五门旅行车车身。	READY
3485_prefl	3485	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前1.1三门掀背车身。	READY
3485_facelift	3485	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后1.1三门掀背车身。	READY
3487	3487	MPV	Kangoo I facelift			EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	MEDIUM	Kasten与Großraumlimousine使用相同标准短轴外壳。	READY
3507_3dr_prefl	3507	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背车身。	READY
3507_5dr_prefl	3507	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背车身。	READY
3507_3dr_facelift	3507	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背车身。	READY
3507_5dr_facelift	3507	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门掀背车身。	READY
3508_prefl	3508	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-PREFL-01	HIGH	改款前四门轿车车身。	READY
3508_facelift	3508	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-FACELIFT-01	HIGH	改款后四门轿车车身。	READY
3511_3dr_prefl	3511	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背车身。	READY
3511_5dr_prefl	3511	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背车身。	READY
3511_3dr_facelift	3511	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背车身。	READY
3511_5dr_facelift	3511	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门掀背车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	3835	1605	1375	Automobile-Catalog 1977 Mazda 323 1.3 GL	https://www.automobile-catalog.com/car/1977/1619180/mazda_323_1_3_gl_automatic.html
EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	3835	1605	1375	Automobile-Catalog 1977 Mazda 323 1.3 GL	https://www.automobile-catalog.com/car/1977/1619180/mazda_323_1_3_gl_automatic.html
EU-MAZDA-323-I-FA4-WAGON-5D-PREFL-01	4010	1605	1425	Automobile-Catalog 1979 Mazda 323 Estate 1.3	https://www.automobile-catalog.com/car/1979/1619120/mazda_323_estate_1_3_wagon.html
EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	4010	1605	1415	Automobile-Catalog 1980 Mazda 323 Estate 1.3 GL	https://www.automobile-catalog.com/car/1980/1619270/mazda_323_estate_1_3_gl_wagon.html
EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	3955	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3	https://www.automobile-catalog.com/car/1981/1623995/mazda_323_1_3.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	3955	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3	https://www.automobile-catalog.com/car/1981/1623995/mazda_323_1_3.html
EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	3965	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3	https://www.automobile-catalog.com/car/1983/1624055/mazda_323_1_3.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	3965	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3	https://www.automobile-catalog.com/car/1983/1624055/mazda_323_1_3.html
EU-MAZDA-323-II-BD-SEDAN-4D-PREFL-01	4155	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3 Sedan	https://www.automobile-catalog.com/car/1981/1624025/mazda_323_1_3_sedan.html
EU-MAZDA-323-II-BD-SEDAN-4D-FACELIFT-01	4165	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3 Sedan	https://www.automobile-catalog.com/car/1983/1624160/mazda_323_1_3_sedan.html
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825	Automobile-Catalog 2005 Renault Kangoo 1.6 16V	https://www.automobile-catalog.com/car/2005/2948810/renault_kangoo_1_6_16v.html
```

## 下一步优先处理

1. 集中闭合 `3488–3504` Toyota Corolla E90 的 Compact、Liftback、Sedan 与 Wagon 分支，并处理 1989 年改款边界。
2. 处理 `3505` Toyota Corona、`3506/3509/3510` Toyota Cressida。
3. 最后处理 Carina II–IV、BMW 1 Series 与 Alpina B5。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Mazda_Familia?utm_source=chatgpt.com "Mazda Familia"
[2]: https://www.automobile-catalog.com/car/1981/1623995/mazda_323_1_3.html?utm_source=chatgpt.com "1981 Mazda 323 1.3 Specs Review (44 kW / 60 PS / 59 hp) (for Europe Germany)"
[3]: https://www.automobile-catalog.com/car/2005/2948810/renault_kangoo_1_6_16v.html?utm_source=chatgpt.com "2005 Renault Kangoo 1.6 16V Specs Review (70 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已完成 `3488–3504` Toyota Corolla VI（E90）共 **17 个 Ktype** 的映射。
* 已按欧洲市场实际车身拆分为 Sedan、Liftback、普通三门 Compact、GTi 三门 Compact、柴油五门 Compact、前驱 Wagon、四驱 Wagon 共 **7 个尺寸组**。发动机功率差异未重复建组。([www.valeoservice.com][1])
* Sedan、Liftback、Compact 与 Wagon 的尺寸均按不含后视镜宽度闭合；AE95 四驱 Wagon 因车长及车高不同单独建组，GTi Compact 因宽度及高度不同于普通 Compact 单独建组。([汽车目录][2])

## 当前批次进度

* READY 映射：**109 行**
* READY 覆盖：**88 / 100 个输入 Ktype**
* PENDING／尚未处理：**12 个输入 Ktype**
* 已确认尺寸组：**48**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3488	3488	Sedan	Corolla VI (E90)	AE92	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	AE92四门轿车车身。	READY
3489	3489	Hatchback	Corolla VI (E90)	AE92	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	AE92五门Liftback车身。	READY
3490	3490	Hatchback	Corolla VI (E90)		3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	HIGH	GTi三门Compact车身；车型资料并列AE92与AE93代码。	READY
3491	3491	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	AE92三门Compact车身。	READY
3492	3492	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	HIGH	CE90五门柴油Compact车身。	READY
3493	3493	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	CE90五门Liftback车身。	READY
3494	3494	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	HIGH	CE90五门柴油Compact车身。	READY
3495	3495	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	CE90五门Liftback车身。	READY
3496	3496	Hatchback	Corolla VI (E90)	EE90	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	EE90三门Compact车身。	READY
3497	3497	Sedan	Corolla VI (E90)	EE90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	EE90四门轿车车身。	READY
3498	3498	Hatchback	Corolla VI (E90)	EE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	EE90五门Liftback车身。	READY
3499	3499	Wagon	Corolla VI (E90)	AE95	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	HIGH	AE95五门四驱旅行车车身。	READY
3500	3500	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	AE92三门Compact车身。	READY
3501	3501	Wagon	Corolla VI (E90)	EE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	EE90五门前驱旅行车车身。	READY
3502	3502	Wagon	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	CE90五门前驱柴油旅行车车身。	READY
3503	3503	Wagon	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	CE90五门前驱柴油旅行车车身。	READY
3504	3504	Hatchback	Corolla VI (E90)	AE92	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	AE92五门Liftback车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365	Automobile-Catalog 1989 Toyota Corolla Sedan 1.3 XL catalyst	https://www.automobile-catalog.com/car/1989/3543395/toyota_corolla_sedan_1_3_xl_catalyst.html
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365	Automobile-Catalog 1987 Toyota Corolla Liftback 1.6 GL	https://www.automobile-catalog.com/car/1987/57155/toyota_corolla_liftback_1_6_gl.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365	Automobile-Catalog 1989 Toyota Corolla FX 1500 FX-L	https://www.automobile-catalog.com/car/1989/3541220/toyota_corolla_fx_1500_fx-l_4speed.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360	Automobile-Catalog 1990 Toyota Corolla Compact GTi 16 catalyst	https://www.automobile-catalog.com/car/1990/3543695/toyota_corolla_compact_gti_16_catalyst.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365	Automobile-Catalog 1989 Toyota Corolla FX 1500 FX-L; Engine in Detail Toyota Corolla Compact 1.8 Diesel XL	https://www.automobile-catalog.com/car/1989/3541220/toyota_corolla_fx_1500_fx-l_4speed.html;https://www.engineindetail.com/pa/toyota-corolla-compact-1-8-diesel-xl-1989
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425	Automobile-Catalog 1987 Toyota Corolla Wagon 1.3 GL	https://www.automobile-catalog.com/car/1987/3543320/toyota_corolla_wagon_1_3_gl.html
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450	Automobile-Catalog 1989 Toyota Corolla Escape 4WD	https://www.automobile-catalog.com/car/1989/58835/toyota_corolla_escape_4wd.html
```

## 下一步优先处理

1. 集中闭合 `3505` Toyota Corona 与 `3506、3509、3510` Toyota Cressida 的代际和改款边界。
2. 按 Carina II、III、IV 的 Sedan、Hatchback、Wagon 车身聚类处理 `3512、3514、3516–3519`。
3. 最后闭合 `3513` BMW 125d 与 `3515` Alpina B5，完成剩余映射后立即进行一次机械收尾并输出最终完整文件。

推进信号：CONTINUE

[1]: https://www.valeoservice.com/en-com/techassist/vehicle/P-3488?country=DZ_algeria&utm_source=chatgpt.com "Parts TOYOTA COROLLA (_E9_)"
[2]: https://www.automobile-catalog.com/car/1989/3543395/toyota_corolla_sedan_1_3_xl_catalyst.html?utm_source=chatgpt.com "1989 Toyota Corolla Sedan 1.3 XL catalyst (man. 5)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3301-3400_ktype_dimension_mapping_final.tsv
- all_3301-3400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已完成剩余 12 个输入 Ktype 的映射与尺寸组闭合。
* 已完成一次轻量机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，尺寸及来源字段完整。
* 当前批次不存在 `PENDING`。

## 当前批次进度

* 输入 Ktype：**100 / 100**
* READY 映射：**128 行**
* PENDING 映射：**0 行**
* DIMENSION_GROUP：**62 个**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3418	3418	Sedan	Sigma (F16A)	F16A	4	EU-MITSUBISHI-SIGMA-F16A-SEDAN-4D-01	HIGH	F16A四门轿车车身。	READY
3419	3419	Hatchback	Colt IV (CAO)	CA1A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA1A三门掀背车身。	READY
3420	3420	Hatchback	Colt IV (CAO)	CA4A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA4A三门掀背车身。	READY
3421	3421	Hatchback	Colt IV (CAO)	CA5A	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH	CA5A三门掀背车身。	READY
3422	3422	MPV	Space Wagon II	N35W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N35W车身。	READY
3423	3423	MPV	Space Wagon II	N38W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N38W车身。	READY
3424	3424	MPV	Space Wagon II	N31W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N31W车身。	READY
3425	3425	MPV	Space Runner I (N1_W,N2_W)	N11W	4	EU-MITSUBISHI-SPACE-RUNNER-I-N11W-MPV-01	HIGH	N11W两驱四门车身。	READY
3426	3426	MPV	Space Runner I (N1_W,N2_W)	N21W	4	EU-MITSUBISHI-SPACE-RUNNER-I-N21W-MPV-01	HIGH	N21W四驱四门车身。	READY
3427	3427	MPV	Space Wagon II	N41W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N41W车身。	READY
3428	3428	MPV	Space Wagon II	N33W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N33W车身。	READY
3429	3429	MPV	Space Wagon II	N43W		EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	HIGH	N43W车身。	READY
3430	3430	Sedan	Galant VII	E57A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E57A四门轿车车身。	READY
3431	3431	Sedan	Galant VII	E52A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E52A四门轿车车身。	READY
3432	3432	Sedan	Galant VII	E55A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E55A四门轿车车身。	READY
3433	3433	Sedan	Galant VII	E75A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E75A四门四驱轿车车身。	READY
3434	3434	Sedan	Galant VII	E54A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E54A四门轿车车身。	READY
3435	3435	Sedan	Galant VII	E88A	4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH	E88A四门四驱轿车车身。	READY
3436	3436	Hatchback	Galant VII	E57A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E57A五门掀背车身。	READY
3437	3437	Hatchback	Galant VII	E52A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E52A五门掀背车身。	READY
3438	3438	Hatchback	Galant VII	E55A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E55A五门掀背车身。	READY
3439	3439	Hatchback	Galant VII	E75A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E75A五门四驱掀背车身。	READY
3440	3440	Hatchback	Galant VII	E54A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E54A五门掀背车身。	READY
3441	3441	Hatchback	Galant VII	E88A	5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH	E88A五门四驱掀背车身。	READY
3442	3442	Sedan	Lancer V	CB8A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB8A四门轿车车身。	READY
3443	3443	Sedan	Lancer V	CB1A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB1A四门轿车车身。	READY
3444	3444	Sedan	Lancer V	CB4A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH	CB4A四门轿车车身。	READY
3445_prefl	3445	Coupe	3000 GT Series 1	Z16A	3	EU-MITSUBISHI-3000-GT-SERIES-1-COUPE-3D-01	HIGH	欧洲286 PS改款前三门车身。	READY
3445_facelift	3445	Coupe	3000 GT Series 2	Z16A	3	EU-MITSUBISHI-3000-GT-SERIES-2-COUPE-3D-01	HIGH	欧洲286 PS改款后三门车身。	READY
3446_3dr	3446	Hatchback	Starlet II (P60)	KP60	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	KP60三门掀背车身。	READY
3446_5dr	3446	Hatchback	Starlet II (P60)	KP60	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	KP60五门掀背车身。	READY
3447_3dr	3447	Hatchback	Starlet II (P60)	KP62	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	KP62三门掀背车身。	READY
3447_5dr	3447	Hatchback	Starlet II (P60)	KP62	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	KP62五门掀背车身。	READY
3448_3dr	3448	Hatchback	Starlet II (P60)	KP61	3	EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	HIGH	KP61三门掀背车身。	READY
3448_5dr	3448	Hatchback	Starlet II (P60)	KP61	5	EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	HIGH	KP61五门掀背车身。	READY
3449	3449	Wagon	Starlet II (P60)	KP60	5	EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	HIGH	KP60五门旅行车车身。	READY
3450_3dr	3450	Hatchback	Starlet III (P70)	EP70	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	EP70三门掀背车身。	READY
3450_5dr	3450	Hatchback	Starlet III (P70)	EP70	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	EP70五门掀背车身。	READY
3451_3dr	3451	Hatchback	Starlet III (P70)	EP71	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	EP71三门掀背车身。	READY
3451_5dr	3451	Hatchback	Starlet III (P70)	EP71	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	EP71五门掀背车身。	READY
3452_3dr	3452	Hatchback	Starlet III (P70)	NP70	3	EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	HIGH	NP70三门柴油掀背车身。	READY
3452_5dr	3452	Hatchback	Starlet III (P70)	NP70	5	EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	HIGH	NP70五门柴油掀背车身。	READY
3453_3dr	3453	Hatchback	Starlet IV (P80)	EP81	3	EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	HIGH	EP81三门掀背车身。	READY
3453_5dr	3453	Hatchback	Starlet IV (P80)	EP81	5	EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	HIGH	EP81五门掀背车身。	READY
3454	3454	Sedan	Corolla III (E30)	KE30	4	EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	HIGH	KE30四门轿车车身。	READY
3455	3455	Hatchback	Corolla IV (E70)	KE70	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	HIGH	KE70三门掀背车身。	READY
3456	3456	Sedan	Corolla IV (E70)	KE70	4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	KE70四门轿车车身。	READY
3457	3457	Sedan	Corolla IV (E70)	KE70	4	EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	HIGH	KE70四门轿车车身。	READY
3458	3458	Hatchback	Corolla IV (E70)	KE70	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	HIGH	KE70三门掀背车身。	READY
3459	3459	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3460	3460	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3461	3461	Hatchback	Corolla IV (E70)	TE71	3	EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	HIGH	TE71三门掀背车身。	READY
3462	3462	Wagon	Corolla IV (E70)	KE70	5	EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	HIGH	KE70五门旅行车车身。	READY
3463	3463	Wagon	Corolla IV (E70)	KE70	5	EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	HIGH	KE70五门旅行车车身。	READY
3464	3464	Hatchback	Corolla V (E80)	AE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE80五门掀背车身。	READY
3465	3465	Hatchback	Corolla V (E80)	EE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	EE80五门掀背车身。	READY
3467	3467	Hatchback	Corolla V (E80)	AE82	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE82五门掀背车身。	READY
3468	3468	Hatchback	Corolla V (E80)	AE82	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	AE82五门掀背车身。	READY
3469	3469	Hatchback	Corolla FX Compact V (E80)	AE82	3	EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	HIGH	AE82三门FX Compact车身。	READY
3470	3470	Hatchback	Corolla V (E80)	CE80	5	EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	HIGH	CE80五门柴油掀背车身。	READY
3471_swb	3471	MPV	Trafic II facelift	X83		EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	HIGH	客运版短轴低顶分支。	READY
3471_lwb	3471	MPV	Trafic II facelift	X83		EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	HIGH	客运版长轴低顶分支。	READY
3472	3472	Sedan	Corolla V (E80)	AE80	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	AE80四门轿车车身。	READY
3473	3473	Sedan	Corolla V (E80)	EE80	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	EE80四门轿车车身。	READY
3474	3474	Sedan	Corolla V (E80)	AE82	4	EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	HIGH	AE82四门轿车车身。	READY
3475	3475	Coupe	Corolla Coupe V (E80)	AE86	2	EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	HIGH	AE86双门轿跑车身。	READY
3476	3476	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3477	3477	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3478	3478	Hatchback	121 I (DA)	DA	3	EU-MAZDA-121-I-DA-HATCHBACK-3D-01	HIGH	DA三门掀背车身。	READY
3479_3dr	3479	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3479_5dr	3479	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3480_3dr	3480	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3480_5dr	3480	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3481_3dr	3481	Hatchback	323 I (FA4)	FA4	3	EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	HIGH	FA4三门掀背车身。	READY
3481_5dr	3481	Hatchback	323 I (FA4)	FA4	5	EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	HIGH	FA4五门掀背车身。	READY
3482_prefl	3482	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-PREFL-01	HIGH	改款前五门旅行车车身。	READY
3482_facelift	3482	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	HIGH	改款后五门旅行车车身。	READY
3483	3483	Wagon	323 I Station Wagon (FA4)	FA4	5	EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	HIGH	改款后五门旅行车车身。	READY
3484	3484	Sedan	Lancer VIII (CY0)	CY0	4	EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	HIGH	CY0四门轿车车身。	READY
3485_prefl	3485	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前1.1三门掀背车身。	READY
3485_facelift	3485	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后1.1三门掀背车身。	READY
3487	3487	MPV	Kangoo I facelift			EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	MEDIUM	Kasten与Großraumlimousine使用相同标准短轴外壳。	READY
3488	3488	Sedan	Corolla VI (E90)	AE92	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	AE92四门轿车车身。	READY
3489	3489	Hatchback	Corolla VI (E90)	AE92	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	AE92五门Liftback车身。	READY
3490	3490	Hatchback	Corolla VI (E90)		3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	HIGH	GTi三门Compact车身；车型资料并列AE92与AE93代码。	READY
3491	3491	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	AE92三门Compact车身。	READY
3492	3492	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	HIGH	CE90五门柴油Compact车身。	READY
3493	3493	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	CE90五门Liftback车身。	READY
3494	3494	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	HIGH	CE90五门柴油Compact车身。	READY
3495	3495	Hatchback	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	CE90五门Liftback车身。	READY
3496	3496	Hatchback	Corolla VI (E90)	EE90	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	EE90三门Compact车身。	READY
3497	3497	Sedan	Corolla VI (E90)	EE90	4	EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	HIGH	EE90四门轿车车身。	READY
3498	3498	Hatchback	Corolla VI (E90)	EE90	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	EE90五门Liftback车身。	READY
3499	3499	Wagon	Corolla VI (E90)	AE95	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	HIGH	AE95五门四驱旅行车车身。	READY
3500	3500	Hatchback	Corolla VI (E90)	AE92	3	EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	HIGH	AE92三门Compact车身。	READY
3501	3501	Wagon	Corolla VI (E90)	EE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	EE90五门前驱旅行车车身。	READY
3502	3502	Wagon	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	CE90五门前驱柴油旅行车车身。	READY
3503	3503	Wagon	Corolla VI (E90)	CE90	5	EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	HIGH	CE90五门前驱柴油旅行车车身。	READY
3504	3504	Hatchback	Corolla VI (E90)	AE92	5	EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	HIGH	AE92五门Liftback车身。	READY
3505	3505	Hatchback	Corona VI (T130)		5	EU-TOYOTA-CORONA-VI-T130-LIFTBACK-5D-01	HIGH	欧洲1.8五门Liftback车身。	READY
3506	3506	Sedan	Cressida I (X30)	RX30	4	EU-TOYOTA-CRESSIDA-I-X30-SEDAN-4D-01	HIGH	RX30四门轿车车身。	READY
3507_3dr_prefl	3507	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背车身。	READY
3507_5dr_prefl	3507	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背车身。	READY
3507_3dr_facelift	3507	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背车身。	READY
3507_5dr_facelift	3507	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门掀背车身。	READY
3508_prefl	3508	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-PREFL-01	HIGH	改款前四门轿车车身。	READY
3508_facelift	3508	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-FACELIFT-01	HIGH	改款后四门轿车车身。	READY
3509_prefl	3509	Sedan	Cressida II (X60)	RX60	4	EU-TOYOTA-CRESSIDA-II-X60-SEDAN-4D-PREFL-01	HIGH	RX60改款前四门轿车车身。	READY
3509_facelift	3509	Sedan	Cressida II (X60)	RX60	4	EU-TOYOTA-CRESSIDA-II-X60-SEDAN-4D-FACELIFT-01	HIGH	RX60改款后四门轿车车身。	READY
3510	3510	Sedan	Cressida II (X60)	GX61	4	EU-TOYOTA-CRESSIDA-II-X60-SEDAN-4D-FACELIFT-01	HIGH	GX61改款后四门轿车车身。	READY
3511_3dr_prefl	3511	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背车身。	READY
3511_5dr_prefl	3511	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	HIGH	改款前五门掀背车身。	READY
3511_3dr_facelift	3511	Hatchback	323 II (BD)	BD	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背车身。	READY
3511_5dr_facelift	3511	Hatchback	323 II (BD)	BD	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门掀背车身。	READY
3512_prefl	3512	Sedan	Carina II (A40/A50)		4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	HIGH	欧洲四门轿车改款前外廓。	READY
3512_facelift	3512	Sedan	Carina II (A40/A50)		4	EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	HIGH	欧洲四门轿车改款后外廓。	READY
3513_prefl	3513	Hatchback	1 Series II (F20)	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	HIGH	F20五门改款前车身。	READY
3513_facelift	3513	Hatchback	1 Series II (F20 LCI)	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	HIGH	F20五门LCI车身。	READY
3514	3514	Wagon	Carina II (A40/A50)		5	EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	HIGH	欧洲1.6五门旅行车改款后外廓。	READY
3515	3515	Sedan	B5 II (F10) facelift	F10	4	EU-ALPINA-B5-II-F10-FACELIFT-SEDAN-4D-01	HIGH	397 kW B5 Bi-Turbo四门轿车。	READY
3516_prefl	3516	Sedan	Carina II (T150)	AT151	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	HIGH	四门轿车改款前外廓。	READY
3516_facelift	3516	Sedan	Carina II (T150)	AT151	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	HIGH	四门轿车改款后外廓。	READY
3517_prefl	3517	Hatchback	Carina II (T150)	AT151	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	HIGH	五门Liftback改款前外廓。	READY
3517_facelift	3517	Hatchback	Carina II (T150)	AT151	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	HIGH	五门Liftback改款后外廓。	READY
3518_prefl	3518	Sedan	Carina II (T150)	AT151	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	HIGH	四门轿车改款前外廓。	READY
3518_facelift	3518	Sedan	Carina II (T150)	AT151	4	EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	HIGH	四门轿车改款后外廓。	READY
3519_prefl	3519	Hatchback	Carina II (T150)	AT151	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	HIGH	五门Liftback改款前外廓。	READY
3519_facelift	3519	Hatchback	Carina II (T150)	AT151	5	EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	HIGH	五门Liftback改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3301-3400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SIGMA-F16A-SEDAN-4D-01	4750	1775	1435	Auto-Data Mitsubishi Sigma (F16A) 3.0 V6 205 Hp	https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-205hp-automatic-24613
EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	3955	1690	1365	Auto-Data Mitsubishi Colt IV (CAO) 1.3 GLi 12V	https://www.auto-data.net/en/mitsubishi-colt-iv-cao-1.3-gli-12v-ca1a-75hp-15762
EU-MITSUBISHI-SPACE-WAGON-II-MPV-01	4515	1695	1630	Auto-Data Mitsubishi Space Wagon II	https://www.auto-data.net/en/mitsubishi-space-wagon-ii-generation-3427
EU-MITSUBISHI-SPACE-RUNNER-I-N11W-MPV-01	4290	1695	1640	Auto-Data Mitsubishi Space Runner 1.8 N11W	https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-1.8-n11w-122hp-15538
EU-MITSUBISHI-SPACE-RUNNER-I-N21W-MPV-01	4270	1695	1680	Auto-Data Mitsubishi Space Runner 1.8 4x4 N21W	https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-1.8-4x4-n21w-122hp-15539
EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII Sedan	https://www.auto-data.net/en/mitsubishi-galant-vii-2.0-glstd-e57a-90hp-15376
EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII Hatchback	https://www.auto-data.net/en/mitsubishi-galant-vii-hatchback-2.0-v6-24-e54a-150hp-automatic-24622
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data Mitsubishi Lancer V 1.6 16V CB4A	https://www.auto-data.net/en/mitsubishi-lancer-v-1.6-16v-cb4a-113hp-15667
EU-MITSUBISHI-3000-GT-SERIES-1-COUPE-3D-01	4560	1840	1285	Automobile-Catalog 1992 Mitsubishi 3000 GT Europe	https://www.automobile-catalog.com/car/1992/1967780/mitsubishi_3000_gt.html
EU-MITSUBISHI-3000-GT-SERIES-2-COUPE-3D-01	4570	1840	1285	Automobile-Catalog 1996 Mitsubishi 3000 GT Europe	https://www.automobile-catalog.com/car/1996/1967810/mitsubishi_3000_gt.html
EU-TOYOTA-STARLET-II-P60-HATCHBACK-3D-01	3680	1525	1380	Toyota 75 Years Vehicle Lineage Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006941/index.html
EU-TOYOTA-STARLET-II-P60-HATCHBACK-5D-01	3680	1525	1380	Toyota 75 Years Vehicle Lineage Starlet	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006941/index.html
EU-TOYOTA-STARLET-II-P60-WAGON-5D-01	3850	1525	1395	Toyota 75 Years Vehicle Lineage Starlet Van	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60006953/index.html
EU-TOYOTA-STARLET-III-P70-HATCHBACK-3D-01	3700	1590	1395	Automobile-Catalog 1985 Toyota Starlet 1.0 DX Europe	https://www.automobile-catalog.com/car/1985/3521570/toyota_starlet_1_0_dx_5-speed.html
EU-TOYOTA-STARLET-III-P70-HATCHBACK-5D-01	3700	1590	1395	Automobile-Catalog 1985 Toyota Starlet 1.0 DX Europe	https://www.automobile-catalog.com/car/1985/3521570/toyota_starlet_1_0_dx_5-speed.html
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-3D-01	3720	1600	1380	Auto-Data Toyota Starlet IV	https://www.auto-data.net/en/toyota-starlet-iv-generation-811
EU-TOYOTA-STARLET-IV-P80-HATCHBACK-5D-01	3720	1600	1380	Auto-Data Toyota Starlet IV	https://www.auto-data.net/en/toyota-starlet-iv-generation-811
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375	Toyota 75 Years Corolla 3rd	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003402/index.html
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385	Tunel Toyota Corolla Hatch IV E70 1.3	https://tunel.az/en/catalog/toyota/corolla/toyota-corolla-hatch-iv-e70/627683fb-a304-4e92-810d-b1348111a6a5
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385	Carsot Toyota Corolla IV E70 Sedan	https://carsot.com/toyota/corolla/toyota-corolla-iv-e70-1979-1983-sedan.html
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341	CarSpecsGuru Toyota Corolla IV E70 1.6	https://www.carspecsguru.com/toyota/corolla/4757/7165/modification-51217
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390	Carsot Toyota Corolla IV E70 Station Wagon	https://carsot.com/toyota/corolla/toyota-corolla-iv-e70-1979-1983-station-wagon-5-door.html
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385	Toyota 75 Years Corolla 5th	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003705A/index.html
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385	Toyota 75 Years Corolla FX; Automobile-Catalog 1987 Toyota Corolla FX	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003729/index.html;https://www.automobile-catalog.com/car/1987/3532310/toyota_corolla_fx_1500_fx-l_automatic.html
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-SWB-LOWROOF-01	4782	1904	1960	Renault New Trafic Passenger 2006 press information	https://manuals.plus/m/da24f2e1280e2eff17bc58b46b7e8fcce24887fa0e941a919969bca1c466085e
EU-RENAULT-TRAFIC-II-FACELIFT-MPV-LWB-LOWROOF-01	5182	1904	1958	Renault New Trafic Passenger 2006 press information	https://manuals.plus/m/da24f2e1280e2eff17bc58b46b7e8fcce24887fa0e941a919969bca1c466085e
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385	Toyota 75 Years Corolla 5th	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003705A/index.html
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335	Auto-Data Toyota Corolla Coupe V E80 1.6 GT 16V	https://www.auto-data.net/en/toyota-corolla-coupe-v-e80-1.6-gt-16v-124hp-3403
EU-MAZDA-121-I-DA-HATCHBACK-3D-01	3475	1605	1450	Automobile-Catalog 1989 Mazda 121 1.3 L cat	https://www.automobile-catalog.com/car/1989/1639655/mazda_121_1_3_l_cat_60.html
EU-MAZDA-323-I-FA4-HATCHBACK-3D-01	3835	1605	1375	Automobile-Catalog 1977 Mazda 323 1.3 GL	https://www.automobile-catalog.com/car/1977/1619180/mazda_323_1_3_gl_automatic.html
EU-MAZDA-323-I-FA4-HATCHBACK-5D-01	3835	1605	1375	Automobile-Catalog 1977 Mazda 323 1.3 GL	https://www.automobile-catalog.com/car/1977/1619180/mazda_323_1_3_gl_automatic.html
EU-MAZDA-323-I-FA4-WAGON-5D-PREFL-01	4010	1605	1425	Automobile-Catalog 1979 Mazda 323 Estate 1.3	https://www.automobile-catalog.com/car/1979/1619120/mazda_323_estate_1_3_wagon.html
EU-MAZDA-323-I-FA4-WAGON-5D-FACELIFT-01	4010	1605	1415	Automobile-Catalog 1980 Mazda 323 Estate 1.3 GL	https://www.automobile-catalog.com/car/1980/1619270/mazda_323_estate_1_3_gl_wagon.html
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490	Automobile-Catalog 2011 Mitsubishi Lancer 1.8 DI-D; Automaniac Mitsubishi Lancer 1.8 DI-D ClearTec	https://www.automobile-catalog.com/car/2011/1996325/mitsubishi_lancer_1_8_di-d_cleartec_inform.html;https://www.automaniac.org/mitsubishi/2007/8436/mitsubishi-lancer-1.8-di-d-cleartec
EU-MAZDA-323-II-BD-HATCHBACK-3D-PREFL-01	3955	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3	https://www.automobile-catalog.com/car/1981/1623995/mazda_323_1_3.html
EU-MAZDA-323-II-BD-HATCHBACK-3D-FACELIFT-01	3965	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3	https://www.automobile-catalog.com/car/1983/1624055/mazda_323_1_3.html
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825	Automobile-Catalog 2005 Renault Kangoo 1.6 16V	https://www.automobile-catalog.com/car/2005/2948810/renault_kangoo_1_6_16v.html
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365	Automobile-Catalog 1989 Toyota Corolla Sedan 1.3 XL catalyst	https://www.automobile-catalog.com/car/1989/3543395/toyota_corolla_sedan_1_3_xl_catalyst.html
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365	Automobile-Catalog 1987 Toyota Corolla Liftback 1.6 GL	https://www.automobile-catalog.com/car/1987/57155/toyota_corolla_liftback_1_6_gl.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360	Automobile-Catalog 1990 Toyota Corolla Compact GTi 16 catalyst	https://www.automobile-catalog.com/car/1990/3543695/toyota_corolla_compact_gti_16_catalyst.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365	Automobile-Catalog 1989 Toyota Corolla FX 1500 FX-L	https://www.automobile-catalog.com/car/1989/3541220/toyota_corolla_fx_1500_fx-l_4speed.html
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365	Automobile-Catalog 1989 Toyota Corolla FX 1500 FX-L; Engine in Detail Toyota Corolla Compact 1.8 Diesel XL	https://www.automobile-catalog.com/car/1989/3541220/toyota_corolla_fx_1500_fx-l_4speed.html;https://www.engineindetail.com/pa/toyota-corolla-compact-1-8-diesel-xl-1989
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450	Automobile-Catalog 1989 Toyota Corolla Escape 4WD	https://www.automobile-catalog.com/car/1989/58835/toyota_corolla_escape_4wd.html
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425	Automobile-Catalog 1987 Toyota Corolla Wagon 1.3 GL	https://www.automobile-catalog.com/car/1987/3543320/toyota_corolla_wagon_1_3_gl.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-PREFL-01	3955	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3	https://www.automobile-catalog.com/car/1981/1623995/mazda_323_1_3.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-FACELIFT-01	3965	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3	https://www.automobile-catalog.com/car/1983/1624055/mazda_323_1_3.html
EU-MAZDA-323-II-BD-SEDAN-4D-PREFL-01	4155	1630	1375	Automobile-Catalog 1981 Mazda 323 1.3 Sedan	https://www.automobile-catalog.com/car/1981/1624025/mazda_323_1_3_sedan.html
EU-MAZDA-323-II-BD-SEDAN-4D-FACELIFT-01	4165	1630	1375	Automobile-Catalog 1983 Mazda 323 1.3 Sedan	https://www.automobile-catalog.com/car/1983/1624160/mazda_323_1_3_sedan.html
EU-TOYOTA-CORONA-VI-T130-LIFTBACK-5D-01	4290	1645	1385	Automobile-Catalog 1979 Toyota Corona Liftback 1.8 GL	https://www.automobile-catalog.com/car/1979/41060/toyota_corona_liftback_1_8.html
EU-TOYOTA-CRESSIDA-I-X30-SEDAN-4D-01	4530	1680	1445	Automobile-Catalog 1977 Toyota Cressida 2000 Europe	https://www.automobile-catalog.com/car/1977/36020/toyota_cressida_2000.html
EU-TOYOTA-CRESSIDA-II-X60-SEDAN-4D-PREFL-01	4640	1690	1440	Automobile-Catalog 1982 Toyota Cressida 2.0 GL Europe	https://www.automobile-catalog.com/car/1982/3477170/toyota_cressida_2_0_gl.html
EU-TOYOTA-CRESSIDA-II-X60-SEDAN-4D-FACELIFT-01	4670	1690	1445	Automobile-Catalog 1984 Toyota Cressida 2.0 GLi-6 Europe	https://www.automobile-catalog.com/car/1984/3477365/toyota_cressida_2_0_gli-6.html
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-PREFL-01	4230	1630	1390	Toyota 75 Years 2nd Carina Sedan	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60002368A/index.html
EU-TOYOTA-CARINA-II-A40-SEDAN-4D-FACELIFT-01	4360	1630	1395	Automobile-Catalog 1981 Toyota Carina 1.6 Europe	https://www.automobile-catalog.com/car/1981/3489575/toyota_carina_1_6_automatic.html
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	Auto-Data BMW 1 Series F20 125d	https://www.auto-data.net/en/bmw-1-series-hatchback-5dr-f20-125d-218hp-17717
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421	BMW Group 125d 5-door technical data	https://www.press.bmwgroup.com/global/article/attachment/T0286379EN/419630
EU-TOYOTA-CARINA-II-A40-WAGON-5D-FACELIFT-01	4370	1630	1400	Automobile-Catalog 1981 Toyota Carina 1.6 Combi Europe	https://www.automobile-catalog.com/car/1981/45605/toyota_carina_kombi_1_6.html
EU-ALPINA-B5-II-F10-FACELIFT-SEDAN-4D-01	4899	1860	1469	Encycarpedia 2012 Alpina B5 Biturbo F10 Saloon	https://www.encycarpedia.com/alpina/12-b5-biturbo-f10-saloon
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-PREFL-01	4350	1670	1365	Automobile-Catalog 1984 Toyota Carina II Sedan 1.6 GL Europe	https://www.automobile-catalog.com/car/1984/3516230/toyota_carina_ii_sedan_1_6_gl.html
EU-TOYOTA-CARINA-II-T150-SEDAN-4D-FACELIFT-01	4370	1670	1365	Automobile-Catalog 1986 Toyota Carina II Sedan 1.6 XL Europe	https://www.automobile-catalog.com/car/1986/3516410/toyota_carina_ii_sedan_1_6_xl.html
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-PREFL-01	4330	1670	1365	Automobile-Catalog 1984 Toyota Carina II Liftback 1.6 GL Europe	https://www.automobile-catalog.com/car/1984/49955/toyota_carina_ii_liftback_1_6_gl.html
EU-TOYOTA-CARINA-II-T150-LIFTBACK-5D-FACELIFT-01	4360	1670	1365	Automobile-Catalog 1986 Toyota Carina II Liftback 1.6 XL Europe	https://www.automobile-catalog.com/car/1986/3516425/toyota_carina_ii_liftback_1_6_xl.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3301-3400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3301-3400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3301-3400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3852 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1075 行）
