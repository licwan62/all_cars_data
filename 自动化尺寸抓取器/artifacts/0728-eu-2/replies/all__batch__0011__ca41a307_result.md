# 任务：all 第 1001-1100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0011__ca41a307


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1001-1100 行

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
all 第 1001-1100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Ducato	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	80	109	Jun 1994	Aug 1998	2024-03-01	20694
Fiat	Ducato	2.5 TD 4X4	Pritsche/Fahrgestell	Allrad	Diesel	80	109	Nov 1994	Apr 1998	2024-03-01	20695
Fiat	Ducato	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	85	116	Jun 1994	Apr 1998	2024-03-01	20696
Fiat	Ducato	2.8 Idtd 4X4	Pritsche/Fahrgestell	Allrad	Diesel	90	122	May 1998	Sep 2001	2024-03-01	20698
Citroën	Xsara	1.6 Chrono	Großraumlimousine	Frontantrieb	Benzin	74	101	Apr 2001	Oct 2004	2024-03-01	20706
Toyota	Hilux vii	2.5 D-4d	Pick-up	Heckantrieb	Diesel	106	144	Jan 2010	May 2015	2024-03-01	20709
Jeep	Wrangler i	4.2 2WD	Geländewagen offen	Heckantrieb	Benzin	82	111	Oct 1986	Sep 1990	2024-03-01	20716
Jeep	Cherokee	2.4 Laredo	Geländewagen geschlossen	Heckantrieb	Benzin	108	147	Oct 2001	Sep 2004	2024-03-01	20717
Jeep	Cherokee	3.7 Laredo	Geländewagen geschlossen	Heckantrieb	Benzin	150	204	Oct 2001	Sep 2004	2024-03-01	20718
Jeep	Grand cherokee i	4.0 Laredo	Geländewagen geschlossen	Heckantrieb	Benzin	131	178	Oct 1996	Sep 1998	2024-03-01	20719
Jeep	Grand cherokee i	5.2 Limited 4X4	Geländewagen geschlossen	Allrad	Benzin	136	185	Oct 1996	Sep 1998	2024-03-01	20721
Jeep	Grand cherokee i	2.5 TD Laredo	Geländewagen geschlossen	Heckantrieb	Diesel	85	115	Oct 1996	Sep 1998	2024-03-01	20722
Suzuki	Sx4 s-Cross	1.6 Ddis	Schrägheck	Frontantrieb	Diesel	88	120	Aug 2013	Jun 2022	2025-06-01	20735
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	103	140	Jun 2013	Mar 2017	2024-03-01	20737
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	103	140	Jun 2013	Mar 2017	2024-03-01	20739
Opel	Mokka	1.4	SUV	Frontantrieb	Benzin	103	140	Apr 2013	Dec 2019	2025-06-01	20740
BMW	X5	Xdrive 50 I	SUV	Allrad	Benzin	330	449	Aug 2013	Jul 2018	2024-03-01	20743
Ford	Ranger	2.5 Tdci	Pick-up	Heckantrieb	Diesel	105	143	May 2006	Jul 2012	2024-03-01	20754
Ford	Ranger	3.0 Tdci	Pick-up	Heckantrieb	Diesel	115	156	May 2006	Jul 2012	2024-03-01	20756
Cadillac	Seville	4.6	Stufenheck	Frontantrieb	Benzin	220	299	Oct 2000	Sep 2004	2024-03-01	20761
Fiat	Siena	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Sep 2001	Dec 2012	2024-03-01	20763
Chrysler	Pt cruiser	2	Kombi	Frontantrieb	Benzin	100	136	Oct 2004	Dec 2010	2024-03-01	20769
AC	Cobra iv	6.2	Cabriolet	Heckantrieb	Benzin	325	442	Apr 2009	Jun 2015	2024-03-01	20772
AC	Cobra iv	6.2	Cabriolet	Heckantrieb	Benzin	410	558	Apr 2009	Jun 2013	2024-03-01	20773
Hyundai	Trajet	2.0 Crdi	Großraumlimousine	Frontantrieb	Diesel	92	125	Aug 2005	Jul 2008	2024-03-01	20776
Daewoo	Rezzo	1.6 SX	Großraumlimousine	Frontantrieb	Benzin	66	90	Aug 2001	Dec 2004	2024-03-01	20778
Tata	Indica	1.4	Schrägheck	Frontantrieb	Benzin	62	84	Jul 2003	-	2024-03-01	20785
Tata	Indica	D 1.4	Schrägheck	Frontantrieb	Diesel	37	50	Jul 2003	Feb 2008	2024-03-01	20786
Tata	Indica	1.4 TD	Schrägheck	Frontantrieb	Diesel	52	71	Jul 2003	-	2024-03-01	20787
Tata	Safari	2.0 TDI	SUV	Heckantrieb	Diesel	64	87	Nov 2003	-	2024-03-01	20788
Land Rover	Range rover i	2.5 TDI 4X4	Geländewagen geschlossen	Allrad	Diesel	83	113	Nov 1992	Apr 1996	2024-03-01	20795
Land Rover	Range rover i	2.5 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	89	121	Oct 1989	Nov 1992	2024-03-01	20796
Land Rover	110/127	2.5 D 4X4	Geländewagen geschlossen	Allrad	Diesel	51	69	Sep 1983	Jul 1990	2024-03-01	20799
Renault	Scénic i	1.6	Großraumlimousine	Frontantrieb	Benzin	75	102	Mar 2001	Aug 2003	2024-03-01	20800
Ford	Mondeo iii	2.0 DI	Stufenheck	Frontantrieb	Diesel	92	125	Oct 2000	Mar 2007	2024-03-01	20812
Renault	Laguna ii	2.2 DCI	Schrägheck	Frontantrieb	Diesel	85	116	Apr 2004	Oct 2005	2024-03-01	20813
Renault	Laguna ii grandtour	2.2 DCI	Kombi	Frontantrieb	Diesel	85	116	Apr 2004	Oct 2005	2024-03-01	20814
KIA	Rio i	1.3	Stufenheck	Frontantrieb	Benzin	60	82	Aug 2002	Feb 2005	2024-03-01	20821
Nissan	X-Trail i	2.5 4X4	SUV	Allrad	Benzin	132	179	Nov 2002	Jan 2013	2024-03-01	20824
Hyundai	Matrix	1.5 Crdi VGT	Großraumlimousine	Frontantrieb	Diesel	81	110	Aug 2005	Aug 2010	2024-03-01	20825
Aston Martin	Vanquish	6.0 S	Coupe	Heckantrieb	Benzin	388	528	Nov 2004	Aug 2007	2025-11-01	20827
VW	Polo	1.8 GTI CUP Edition	Schrägheck	Frontantrieb	Benzin	132	180	May 2006	Nov 2009	2024-03-01	20832
Hyundai	Sonata iv	2.0 16V	Stufenheck	Frontantrieb	Benzin	106	144	Oct 2001	Nov 2004	2024-03-01	20839
Toyota	Corolla	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	85	116	Jun 2004	Jul 2007	2024-03-01	20843
Dodge	Caravan	3.8 AWD	Großraumlimousine	Allrad	Benzin	153	208	Apr 2001	Dec 2007	2024-03-01	20845
Seat	Ibiza iii	2	Schrägheck	Frontantrieb	Benzin	85	116	Apr 2002	Nov 2009	2024-03-01	20846
Peugeot	307	1.4	Kombi	Frontantrieb	Benzin	55	75	Apr 2002	Sep 2003	2024-03-01	20847
Fiat	Ducato	2.8 TD	Bus	Frontantrieb	Diesel	90	122	Nov 2003	Jul 2006	2024-03-01	20848
Fiat	Ducato	2.8 TD 4X4	Bus	Allrad	Diesel	90	122	Nov 2003	Jul 2006	2024-03-01	20849
Fiat	Ducato	2.8 TD	Kasten	Frontantrieb	Diesel	90	122	Dec 2001	Jul 2006	2024-03-01	20850
Hyundai	Getz	1.5 Crdi GLS	Schrägheck	Frontantrieb	Diesel	75	102	Jul 2004	Aug 2005	2024-03-01	20852
Hyundai	Getz	1.5 Crdi GLS	Schrägheck	Frontantrieb	Diesel	81	110	Aug 2005	Jun 2009	2024-03-01	20853
Fiat	Ducato	2.8 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	90	122	Nov 2003	Jul 2006	2024-03-01	20854
Lotus	Exige	1.8 CUP 240	Coupe	Heckantrieb	Benzin	181	246	Apr 2006	Jun 2012	2024-03-01	20856
Saab	9-3	2.0 Turbo Performance	Stufenheck	Frontantrieb	Benzin	185	252	Apr 2004	Feb 2015	2024-03-01	20857
Bentley	Continental	6.7 Turbo R	Coupe	Heckantrieb	Benzin	235	320	Oct 1991	Dec 2002	2024-03-01	20861
Ford	Transit connect	1.8 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Aug 2006	Dec 2013	2024-03-01	20862
Subaru	Forester	2.5 RX Nato AWD	SUV	Allrad	Benzin	115	156	Nov 2002	Dec 2008	2024-03-01	20863
Audi	A3	1.8 Tfsi	Schrägheck	Frontantrieb	Benzin	118	160	Nov 2006	Aug 2012	2024-03-01	20864
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	118	160	May 2011	-	2024-03-01	20872
Ssangyong	Rexton	2.3 Rx230 4X4	SUV	Allrad	Benzin	110	150	May 2002	Aug 2006	2024-03-01	20873
VW	Transporter t5	2.5 TDI	Bus	Frontantrieb	Diesel	120	163	Nov 2003	Nov 2009	2024-03-01	20881
Subaru	Legacy iv station wagon	2.0 AWD	Kombi	Allrad	Benzin	121	165	Jun 2005	Apr 2009	2024-03-01	20884
Renault	Megane ii	2.0 DCI	Stufenheck	Frontantrieb	Diesel	110	150	Sep 2005	-	2024-03-01	20890
Volvo	S40 ii	D5	Stufenheck	Frontantrieb	Diesel	132	179	Mar 2006	Dec 2010	2024-03-01	20891
Bentley	Continental	4.0 Flex AWD	Cabriolet	Allrad	Benzin/Ethanol	373	507	Feb 2012	Jul 2018	2024-03-01	20892
Volvo	V50	D5	Kombi	Frontantrieb	Diesel	132	179	Mar 2006	Dec 2010	2024-03-01	20893
Peugeot	307	1.4	Kombi	Frontantrieb	Benzin	55	75	Apr 2002	Sep 2003	2024-03-01	20894
Porsche	911	3.8 Carrera S	Coupe	Heckantrieb	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20896
Porsche	911	3.8 Carrera 4S	Coupe	Allrad	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20897
Audi	A3	1.8 Tfsi	Schrägheck	Frontantrieb	Benzin	118	160	Nov 2006	Mar 2013	2024-03-01	20898
Audi	A4 b7	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	125	170	Oct 2006	Jun 2008	2024-03-01	20910
Audi	A4 b7 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	125	170	Oct 2006	Jun 2008	2024-03-01	20911
VW	Golf plus v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	96	131	May 2005	May 2007	2024-03-01	20912
Citroën	C5	3.0 Carlsson HP	Schrägheck	Frontantrieb	Benzin	173	235	Sep 2004	Jan 2008	2024-07-01	20913
Hyundai	Sonata v	2.0 Vvti GLS	Stufenheck	Frontantrieb	Benzin	106	144	May 2005	Dec 2010	2024-03-01	20915
Toyota	Dyna	2.5 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Jul 2001	-	2024-03-01	20919
Toyota	Dyna	2.5 D4D	Pritsche/Fahrgestell	Heckantrieb	Diesel	75	102	Aug 2001	-	2024-03-01	20920
KIA	Carnival / grand iii	2.9 Crdi LX	Großraumlimousine	Frontantrieb	Diesel	141	192	Sep 2006	Jun 2015	2024-05-01	20928
BMW	X5	M 50 D	SUV	Allrad	Diesel	280	381	Dec 2013	Jul 2018	2024-03-01	20930
Ssangyong	Chairman	3.2	Stufenheck	Heckantrieb	Benzin	162	220	Jul 1997	-	2024-03-01	20983
Peugeot	106 i	Electric	Schrägheck	Frontantrieb	Elektro	20	27	Aug 1991	Mar 1996	2024-03-01	21079
Citroën	Saxo	1.1 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	44	60	Jul 2000	Jun 2003	2024-03-01	21089
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	120	163	Jul 2004	Nov 2007	2024-03-01	21092
Toyota	Corolla	1.6	Stufenheck	Frontantrieb	Benzin	85	116	May 1987	Apr 1994	2024-03-01	21097
Mazda	3	1.5	Schrägheck	Frontantrieb	Benzin	74	100	Sep 2013	May 2019	2024-03-01	21137
Mercedes-benz	Glk-Klasse	250 4-matic	SUV	Allrad	Benzin	155	211	Aug 2013	Jun 2015	2024-03-01	21140
Mazda	3	2	Schrägheck	Frontantrieb	Benzin	88	120	Sep 2013	May 2019	2024-03-01	21146
Mazda	3	2.2 D	Schrägheck	Frontantrieb	Diesel	110	150	Sep 2013	May 2019	2024-03-01	21148
Mazda	3	2	Schrägheck	Frontantrieb	Benzin	121	165	Jul 2013	May 2019	2024-03-01	21150
Mazda	3	2	Stufenheck	Frontantrieb	Benzin	88	120	Sep 2013	May 2019	2024-03-01	21156
Mazda	3	2.2 D	Stufenheck	Frontantrieb	Diesel	110	150	Sep 2013	May 2019	2024-03-01	21157
Bentley	Continental	4	Coupe	Allrad	Benzin	373	507	Sep 2011	Jul 2018	2024-03-01	21253
Mitsubishi	Pajero iii canvas top	2.5 TDI	Geländewagen offen	Allrad	Diesel	73	99	Apr 2000	Dec 2006	2024-03-01	21314
Mitsubishi	Pajero iii canvas top	2.5 TDI	Geländewagen offen	Allrad	Diesel	85	115	Sep 2001	Dec 2006	2024-03-01	21315
Audi	A6 c6	3.0 Quattro	Stufenheck	Allrad	Benzin	160	218	May 2004	May 2006	2024-03-01	21318
Audi	A6 c6 avant	3.0 Quattro	Kombi	Allrad	Benzin	160	218	Mar 2005	May 2006	2024-03-01	21319
Audi	A6 allroad c6	3.0 TDI Quattro	Kombi	Allrad	Diesel	155	211	May 2006	Aug 2011	2024-03-01	21320
Audi	A6 allroad c6	2.7 TDI Quattro	Kombi	Allrad	Diesel	120	163	May 2006	Aug 2011	2024-03-01	21321
Audi	A4 b7	3.0 TDI Quattro	Cabriolet	Allrad	Diesel	150	204	Jan 2006	Mar 2009	2024-03-01	21322


--- Round 1 / 首次发送 ---
## 更新点

* 本轮优先闭合低歧义乘用车，共完成 **12 个 Ktype 映射、10 个尺寸组**。
* BMW X5 F15 与 Mercedes-Benz GLK X204 facelift 的车身边界及三维已闭合。
* Audi A4 B7、Audi A6 C6、Volvo S40/V50 和 Porsche 911 997 的独立车身组已建立；Carrera S 与 Carrera 4S 因车宽不同分别建组。([Ultimate Specs][1])
* 商用车、皮卡、门数不明确以及跨改款 Ktype 暂未强行映射。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：12
* PENDING Ktype：88
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20743	20743	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
20891	20891	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-01	HIGH		READY
20893	20893	Wagon	V50 I		5	EU-VOLVO-V50-I-WAGON-01	HIGH		READY
20896	20896	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	Carrera S后驱标准车身。	READY
20897	20897	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	HIGH	Carrera 4S四驱宽体。	READY
20911	20911	Wagon	A4 B7		5	EU-AUDI-A4-B7-WAGON-01	HIGH	Avant车身。	READY
20930	20930	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
21140	21140	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-FACELIFT-01	HIGH	2012 facelift车身。	READY
21318	21318	Sedan	A6 C6		4	EU-AUDI-A6-C6-SEDAN-01	HIGH		READY
21320	21320	Wagon	A6 allroad C6		5	EU-AUDI-A6-C6-ALLROAD-WAGON-01	HIGH	Allroad车身。	READY
21321	21321	Wagon	A6 allroad C6		5	EU-AUDI-A6-C6-ALLROAD-WAGON-01	HIGH	Allroad车身。	READY
21322	21322	Convertible	A4 B7		2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	Cabriolet车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X5-F15-SUV-01	4886	1938	1762	BMW X5 (F15) official specification sheet	https://bps.bmw.com.tw/uploads/bps/1605240477_OZDbT4.pdf
EU-VOLVO-S40-II-SEDAN-01	4468	1770	1452	UltimateSpecs Volvo S40 II D5	https://www.ultimatespecs.com/car-specs/Volvo/1106/Volvo-S40-II-D5-Aut.html
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450	UltimateSpecs Volvo V50 D5	https://www.ultimatespecs.com/car-specs/Volvo/4649/Volvo-V50-D5-Aut.html
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300	UltimateSpecs Porsche 911 (997) Carrera S	https://www.ultimatespecs.com/car-specs/Porsche/1790/Porsche-911-%28997%29-Carrera-S.html
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300	UltimateSpecs Porsche 911 (997) Carrera 4S	https://www.ultimatespecs.com/car-specs/Porsche/1800/Porsche-911-%28997%29-Carrera-4S.html
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427	UltimateSpecs Audi A4 (B7) Avant 2.0 TFSI	https://www.ultimatespecs.com/car-specs/Audi/55826/Audi-A4-%28B7%29-Avant-20-TFSI-6speed-200HP.html
EU-MERCEDES-BENZ-GLK-X204-SUV-FACELIFT-01	4536	1840	1669	UltimateSpecs Mercedes-Benz GLK (X204 2012) 250 4MATIC	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/65885/Mercedes-Benz-GLK-%28X204-2012%29-250-4MATIC-BlueEFFICIENCY.html
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459	UltimateSpecs Audi A6 (C6) 3.0 TDI Quattro	https://www.ultimatespecs.com/car-specs/Audi/125868/Audi-A6-%28C6%29-30-TDI-V6-225HP-Quattro.html
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520	UltimateSpecs Audi A6 (C6) Allroad 3.0 TDI	https://www.ultimatespecs.com/car-specs/Audi/3950/Audi-A6-%28C6%29-Allroad-Quattro-30-TDI.html
EU-AUDI-A4-B7-CONVERTIBLE-01	4570	1780	1390	UltimateSpecs Audi A4 (B7) Cabriolet 2.0 TFSI	https://www.ultimatespecs.com/car-specs/Audi/3880/Audi-A4-%28B7%29-Cabriolet-20-TFSI.html
```

## 下一步优先处理

1. 批量闭合 Mazda 3 BM/BN Hatchback 与 Sedan，并判断 facelift 前后三维能否共组。
2. 处理 Audi A3 8P、VW Polo、Seat Ibiza、Hyundai Getz 等可能存在三门/五门分支的 Ktype。
3. 最后集中处理 Ducato、Hilux、Ranger、Dyna、Transporter T5 等轴距、车顶、CAB/BED 分支较多的商用车和皮卡。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Audi/55826/Audi-A4-%28B7%29-Avant-20-TFSI-6speed-200HP.html "Audi A4 (B7) Avant 2.0 TFSI 6speed 200HP Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **15 条 READY 映射**，集中闭合 Mazda3 III 两种车身、Audi A4/A6、Bentley Continental II、Abarth 500C、MINI R52、Lotus Exige S2、Aston Martin Vanquish I 和 Subaru Legacy IV Wagon。
* Mazda3 III 的四个掀背 Ktype 共用一个尺寸组，两个三厢 Ktype 共用另一个尺寸组；BM/BN 改款未造成三维变化。([Ultimate Specs][1])
* Audi A4 B7 Sedan、A6 C6 Avant，以及 Bentley GT/GTC II 分别按独立物理车身建组。([Ultimate Specs][2])
* Abarth、MINI、Lotus、Aston Martin 和 Subaru 的车身边界及三维已闭合。([Ultimate Specs][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：27
* PENDING Ktype：73
* 已确认尺寸组：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20827	20827	Coupe	Vanquish I		2	EU-ASTON-MARTIN-VANQUISH-I-COUPE-01	HIGH	Vanquish S车身。	READY
20856	20856	Coupe	Exige S2		2	EU-LOTUS-EXIGE-S2-COUPE-01	HIGH	Cup 240使用Exige S2固定车身外廓。	READY
20872	20872	Convertible	500C/595C/695C	312	2	EU-ABARTH-500C-312-CONVERTIBLE-01	HIGH	500C、595C和695C共用312系敞篷外廓。	READY
20884	20884	Wagon	Legacy IV	BP5	5	EU-SUBARU-LEGACY-IV-WAGON-01	HIGH	BP5旅行车。	READY
20892	20892	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH		READY
20910	20910	Sedan	A4 B7		4	EU-AUDI-A4-B7-SEDAN-01	HIGH		READY
21092	21092	Convertible	MINI Cabrio R52	R52	2	EU-MINI-MINI-R52-CONVERTIBLE-01	HIGH		READY
21137	21137	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21146	21146	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21148	21148	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21150	21150	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21156	21156	Sedan	Mazda3 III		4	EU-MAZDA-MAZDA3-III-SEDAN-01	HIGH	BM/BN使用同一三厢外廓。	READY
21157	21157	Sedan	Mazda3 III		4	EU-MAZDA-MAZDA3-III-SEDAN-01	HIGH	BM/BN使用同一三厢外廓。	READY
21253	21253	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH		READY
21319	21319	Wagon	A6 C6		5	EU-AUDI-A6-C6-WAGON-01	HIGH	Avant车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ASTON-MARTIN-VANQUISH-I-COUPE-01	4665	1923	1318	UltimateSpecs Aston Martin Vanquish S	https://www.ultimatespecs.com/car-specs/Aston-Martin/685/Aston-Martin-Vanquish-S.html
EU-LOTUS-EXIGE-S2-COUPE-01	3785	1719	1170	UltimateSpecs Lotus Exige S2 S	https://www.ultimatespecs.com/car-specs/Lotus/12811/Lotus-Exige-S2-S.html
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485	UltimateSpecs Abarth 500C 1.4 T-JET	https://www.ultimatespecs.com/car-specs/Abarth/63008/Abarth-500C-14-16v-T-JET-135HP-.html
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470	Subaru Legacy 2009 official brochure	https://www.subaru.fr/docs/brochures/Documentation_2009_Subaru_Legacy.pdf
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403	UltimateSpecs Bentley Continental GTC II V8	https://www.ultimatespecs.com/car-specs/Bentley/63718/Bentley-Continental-GTC-II-V8.html
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427	UltimateSpecs Audi A4 B7 2.0 TFSI Quattro	https://www.ultimatespecs.com/car-specs/Audi/3870/Audi-A4-%28B7%29-20-TFSI-Quattro.html
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420	UltimateSpecs MINI Cabrio R52 Cooper S	https://www.ultimatespecs.com/car-specs/Mini/6893/Mini-Mini-Cabrio-R52-Cooper-S.html
EU-MAZDA-MAZDA3-III-HATCHBACK-01	4465	1795	1450	UltimateSpecs Mazda3 III Hatchback	https://www.ultimatespecs.com/car-specs/Mazda/67106/Mazda-3-III-SKYACTIV-G-20-120HP.html
EU-MAZDA-MAZDA3-III-SEDAN-01	4585	1795	1450	UltimateSpecs Mazda3 III SportSedan	https://www.ultimatespecs.com/car-specs/Mazda/67112/Mazda-3-III-SportSedan-SKYACTIV-G-20-120HP.html
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404	UltimateSpecs Bentley Continental GT II V8	https://www.ultimatespecs.com/car-specs/Bentley/63701/Bentley-Continental-GT-2-V8.html
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463	UltimateSpecs Audi A6 C6 Avant	https://www.ultimatespecs.com/car-specs/Audi/25424/Audi-A6-%28C6%29-Avant-30-TDI-240HP-Quattro-DPF.html
```

## 下一步优先处理

1. 批量处理无需拆分轴距的普通乘用车：Opel Insignia A、Mokka、Suzuki S-Cross、Volvo/Hyundai/Renault 等。
2. 处理 Audi A3 8P、VW Polo、Seat Ibiza、Hyundai Getz 等门数可能导致派生行的 Ktype。
3. 最后集中解决 Ducato、Hilux、Ranger、Dyna、Transit Connect、Transporter T5 等轴距、驾驶室、车顶或货斗分支。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Mazda/67106/Mazda-3-III-SKYACTIV-G-20-120HP.html "Mazda 3 III SKYACTIV-G 2.0 120HP Specs, Performance, Comparisons"
[2]: https://www.ultimatespecs.com/car-specs/Audi/3870/Audi-A4-%28B7%29-20-TFSI-Quattro.html "Audi A4 (B7) 2.0 TFSI Quattro Specs, Performance, Comparisons"
[3]: https://www.ultimatespecs.com/car-specs/Abarth/63008/Abarth-500C-14-16v-T-JET-135HP-.html "Abarth 500C 1.4 16v T-JET 135HP Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **10 条 READY 映射、10 个尺寸组**。
* 已闭合 Suzuki SX4 S-Cross、Opel Insignia A facelift 两种车身、Opel Mokka A、Hyundai Trajet、Daewoo Rezzo、Nissan X-Trail T30、Hyundai Matrix facelift、Sonata EF facelift 和 Sonata NF。([Ultimate Specs][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：37
* PENDING Ktype：63
* 已确认尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20735	20735	Hatchback	SX4 S-Cross I		5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH		READY
20737	20737	Sedan	Insignia A facelift	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	四门三厢车身。	READY
20739	20739	Hatchback	Insignia A facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	HIGH	五门掀背车身。	READY
20740	20740	SUV	Mokka A	J13	5	EU-OPEL-MOKKA-A-SUV-01	HIGH		READY
20776	20776	MPV	Trajet	FO	5	EU-HYUNDAI-TRAJET-MPV-01	HIGH		READY
20778	20778	MPV	Rezzo	U100	5	EU-DAEWOO-REZZO-MPV-01	MEDIUM	U100车身亦以Tacuma名称销售。	READY
20824	20824	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-T30-SUV-01	HIGH		READY
20825	20825	MPV	Matrix facelift	FC	5	EU-HYUNDAI-MATRIX-FACELIFT-MPV-01	HIGH		READY
20839	20839	Sedan	Sonata IV facelift	EF	4	EU-HYUNDAI-SONATA-EF-FACELIFT-SEDAN-01	MEDIUM	2001 facelift车身。	READY
20915	20915	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-NF-SEDAN-01	HIGH		READY
```

([Ultimate Specs][1])

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575	UltimateSpecs Suzuki SX4 S-Cross 1.6 DDiS	https://www.ultimatespecs.com/car-specs/Suzuki/66919/Suzuki-SX4-S-Cross-16-DDiS-GLX-EL-2WD.html
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	UltimateSpecs Opel Insignia 4 doors Facelift 2.0 CDTI	https://www.ultimatespecs.com/car-specs/Opel/71112/Opel-Insignia-4-doors-Facelift-20-CDTI-ecoFLEX-140HP-Selective.html
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498	UltimateSpecs Opel Insignia 5 doors Facelift 2.0 CDTI	https://www.ultimatespecs.com/car-specs/Opel/66374/Opel-Insignia-5-doors-Facelift-Excellence-20-CDTI-163HP-Auto.html
EU-OPEL-MOKKA-A-SUV-01	4278	1777	1658	UltimateSpecs Opel Mokka A 1.4 Turbo	https://www.ultimatespecs.com/car-specs/Opel/67678/Opel-Mokka-A-14-Turbo-140HP-4x2-Start-Stop-Selective.html
EU-HYUNDAI-TRAJET-MPV-01	4700	1840	1760	UltimateSpecs Hyundai Trajet 2.0 CRDi	https://www.ultimatespecs.com/car-specs/Hyundai/4451/Hyundai-Trajet-20-CRDi.html
EU-DAEWOO-REZZO-MPV-01	4350	1755	1630	UltimateSpecs Chevrolet Tacuma 1.6 16v SX	https://www.ultimatespecs.com/car-specs/Chevrolet/50189/Chevrolet-Tacuma-16-16v-SX.html
EU-NISSAN-X-TRAIL-T30-SUV-01	4510	1760	1750	UltimateSpecs Nissan X-Trail T30 2.5 4WD	https://www.ultimatespecs.com/car-specs/Nissan/6832/Nissan-X-Trail-%28T30%29-25-4WD.html
EU-HYUNDAI-MATRIX-FACELIFT-MPV-01	4025	1740	1685	UltimateSpecs Hyundai Matrix 2006 1.5 CRDi VGT	https://www.ultimatespecs.com/car-specs/Hyundai/51677/Hyundai-Matrix-2006-15-CRDi-VGT.html
EU-HYUNDAI-SONATA-EF-FACELIFT-SEDAN-01	4747	1820	1422	UltimateSpecs Hyundai Sonata IV.5 2.0i	https://www.ultimatespecs.com/car-specs/Hyundai/4440/Hyundai-Sonata-IV5-20i.html
EU-HYUNDAI-SONATA-NF-SEDAN-01	4800	1830	1480	UltimateSpecs Hyundai Sonata V 2.0i	https://www.ultimatespecs.com/car-specs/Hyundai/4444/Hyundai-Sonata-V-20i.html
```

([Ultimate Specs][1])

## 下一步优先处理

1. 批量闭合 Renault Scénic I、Laguna II Hatchback/Grandtour、Ford Mondeo III、Peugeot 307 Wagon 等普通乘用车。
2. 处理 Audi A3 8P、VW Polo、Seat Ibiza、Hyundai Getz 等门数分支。
3. 最后处理 Ducato、Hilux、Ranger、Dyna、Transit Connect 和 Transporter T5 的轴距、车顶、驾驶室及货斗分支。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Opel/71112/Opel-Insignia-4-doors-Facelift-20-CDTI-ecoFLEX-140HP-Selective.html "Opel Insignia 4 doors Facelift 2.0 CDTI ecoFLEX 140HP Selective Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* 本轮新增 **12 条 READY 映射、11 个尺寸组**。
* 已闭合 Cadillac Seville V、Renault Scénic I Phase II、Ford Mondeo III Sedan、Renault Laguna II 两种车身、Kia Rio I facelift Sedan、Dodge Caravan IV LWB AWD、Peugeot 307 Break、Saab 9-3 II Sedan、Renault Mégane II Phase II Sedan 和 Citroën C5 I Phase II。([汽车数据网][1])
* Peugeot 307 的两个重复输入 Ktype 已复用同一尺寸组，未重复建组。([汽车目录][2])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：49
* PENDING Ktype：51
* 已确认尺寸组：42
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20761	20761	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH		READY
20800	20800	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	HIGH		READY
20812	20812	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-SEDAN-01	HIGH	四门三厢车身。	READY
20813	20813	Hatchback	Laguna II Phase I	BG09	5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	HIGH	五门掀背车身。	READY
20814	20814	Wagon	Laguna II Phase I	KG09	5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	HIGH	Grandtour旅行车身。	READY
20821	20821	Sedan	Rio I facelift	DC	4	EU-KIA-RIO-I-FACELIFT-SEDAN-01	HIGH		READY
20845	20845	MPV	Caravan IV LWB	RS	5	EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	3.8 AWD长轴距车身。	READY
20847	20847	Wagon	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-01	HIGH	Break旅行车身。	READY
20857	20857	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-SEDAN-01	HIGH	Sport Sedan车身。	READY
20890	20890	Sedan	Mégane II Phase II	LM	4	EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	HIGH	四门Classic车身。	READY
20894	20894	Wagon	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-01	HIGH	Break旅行车身。	READY
20913	20913	Hatchback	C5 I Phase II	DC	5	EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	HIGH	五门掀背车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414	Auto-Data Cadillac Seville V 4.6 V8	https://www.auto-data.net/en/cadillac-seville-v-4.6-i-v8-32-279hp-11734
EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	4170	1700	1680	UltimateSpecs Renault Scenic I 1.6 16v	https://www.ultimatespecs.com/car-specs/Renault/6625/Renault-Scenic-1-16-16v.html
EU-FORD-MONDEO-III-SEDAN-01	4731	1812	1429	UltimateSpecs Ford Mondeo III Sedan 2.0 TDdi	https://www.ultimatespecs.com/car-specs/Ford/47628/Ford-Mondeo-3-Sedan-20-TDdi-115HP-Ghia.html
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II 2.2 dCi	https://www.auto-data.net/en/renault-laguna-ii-2.2-dci-150hp-10331
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443	Auto-Data Renault Laguna II Grandtour 2.2 dCi	https://www.auto-data.net/en/renault-laguna-ii-grandtour-2.2-dci-150hp-10318
EU-KIA-RIO-I-FACELIFT-SEDAN-01	4240	1680	1440	Auto-Data Kia Rio I Sedan facelift 1.3i	https://www.auto-data.net/en/kia-rio-i-sedan-dc-facelift-2002-1.3i-82hp-2685
EU-DODGE-CARAVAN-IV-MPV-LWB-01	5093	1995	1750	Auto-Data Dodge Caravan IV LWB 3.8 AWD	https://www.auto-data.net/en/dodge-caravan-iv-lwb-3.8-v6-218hp-4x4-automatic-29967
EU-PEUGEOT-307-I-WAGON-01	4419	1757	1544	Automobile-Catalog Peugeot 307 Break 1.4	https://www.automobile-catalog.com/car/2002/2617325/peugeot_307_break_estate_1_4_75.html
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466	Auto-Data Saab 9-3 Sedan II	https://www.auto-data.net/en/saab-9-3-sedan-ii-generation-2537
EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	4498	1777	1460	Auto-Data Renault Megane II Classic Phase II 2.0 dCi	https://www.auto-data.net/en/renault-megane-ii-classic-phase-ii-2006-2.0-dci-150hp-fap-30269
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4750	1770	1480	UltimateSpecs Citroen C5 2.0 16v	https://www.ultimatespecs.com/car-specs/Citroen/4104/Citroen-C5-20-16v.html
```

## 5) 下一步优先处理

1. 闭合 Toyota Corolla、Peugeot 106、Citroën Saxo、Tata Indica 等普通乘用车。
2. 处理 Audi A3、VW Polo、Seat Ibiza、Hyundai Getz 的三门和五门分支。
3. 集中处理 Jeep、Range Rover、Pajero Canvas Top 等代际、车身长度或门数边界。
4. 最后处理 Ducato、Hilux、Ranger、Dyna、Transit Connect、Transporter T5 等多轴距、多车顶及多驾驶室车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/cadillac-seville-v-4.6-i-v8-32-279hp-11734 "Cadillac Seville V 4.6 i V8 32 (279 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2002/2617325/peugeot_307_break_estate_1_4_75.html?utm_source=chatgpt.com "2002 Peugeot 307 Break (Estate) 1.4 75 Specs Review ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1) 更新点

* 本轮新增 **13 条 READY 映射、9 个尺寸组**。
* Audi A3 两个 Ktype 均跨越 2008 年外廓更新，分别拆为 `prefl` 与 `facelift` 两个物理分支。
* Tata Indica 三个动力版本复用同一尺寸组；未重复建立尺寸事实。
* 已闭合 PT Cruiser、Corolla IX Sedan、Forester II、Golf V Plus、Grand Carnival II 与 Chairman H。([汽车数据网][1])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：62
* PENDING Ktype：40
* 已确认尺寸组：51
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20769	20769	Wagon	PT Cruiser		5	EU-CHRYSLER-PT-CRUISER-WAGON-01	HIGH	五门量产车身。	READY
20785	20785	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20786	20786	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20787	20787	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20843	20843	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-E120-SEDAN-01	HIGH		READY
20863	20863	SUV	Forester II	SG	5	EU-SUBARU-FORESTER-II-SUV-01	MEDIUM	SG系五门车身。	READY
20864_prefl	20864	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008年外廓更新前分支。	READY
20864_facelift	20864	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008年外廓更新后分支。	READY
20898_prefl	20898	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008年外廓更新前分支。	READY
20898_facelift	20898	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008年外廓更新后分支。	READY
20912	20912	MPV	Golf V Plus	5M1	5	EU-VW-GOLF-V-PLUS-MPV-01	HIGH		READY
20928	20928	MPV	Grand Carnival II	VQ	5	EU-KIA-GRAND-CARNIVAL-II-MPV-01	HIGH	长车身Grand Carnival。	READY
20983	20983	Sedan	Chairman H		4	EU-SSANGYONG-CHAIRMAN-H-SEDAN-01	MEDIUM	CM600S标准轴距车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-PT-CRUISER-WAGON-01	4290	1705	1600	Auto-Data Chrysler PT Cruiser	https://www.auto-data.net/en/chrysler-pt-cruiser-generation-3250
EU-TATA-INDICA-I-HATCHBACK-01	3660	1625	1485	Auto-Data Tata Indica 1.4 TD	https://www.auto-data.net/en/tata-indica-1.4-td-71hp-1216
EU-TOYOTA-COROLLA-E120-SEDAN-01	4375	1710	1470	Auto-Data Toyota Corolla IX E120/E130	https://www.auto-data.net/en/toyota-corolla-ix-e120-e130-generation-818
EU-SUBARU-FORESTER-II-SUV-01	4450	1735	1590	Auto-Data Subaru Forester II	https://www.auto-data.net/en/subaru-forester-ii-generation-3623
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005 1.8 TFSI	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-1.8-tfsi-160hp-4183
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008 1.8 TFSI	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-1.8-tfsi-160hp-27144
EU-VW-GOLF-V-PLUS-MPV-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 2.0 TDI	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-KIA-GRAND-CARNIVAL-II-MPV-01	5130	1985	1780	Auto-Data Kia Grand Carnival II 2.9 CRDi	https://www.auto-data.net/en/kia-grand-carnival-ii-2.9-crdi-192hp-automatic-34420
EU-SSANGYONG-CHAIRMAN-H-SEDAN-01	5055	1825	1465	Auto-Data SsangYong Chairman H CM600S	https://www.auto-data.net/en/ssangyong-chairman-h-cm600s-3.2-i-24v-220hp-16015
```

## 5) 下一步优先处理

1. 处理 VW Polo、Seat Ibiza、Hyundai Getz、Citroën Saxo 和 Peugeot 106 的门数分支。
2. 闭合 Jeep Cherokee、Grand Cherokee、Range Rover I、Wrangler I 和 Pajero Canvas Top。
3. 最后集中处理 Ducato、Hilux、Ranger、Dyna、Transit Connect 与 Transporter T5 的轴距、车顶、驾驶室及货斗分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-a3-8p-facelift-2005-1.8-tfsi-160hp-4183 "Audi A3 (8P, facelift 2005) 1.8 TFSI (160 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1) 更新点

* Jeep Cherokee KJ 的两个 Ktype 复用同一尺寸组；Grand Cherokee ZJ 根据标准高度与 Limited 较高外廓拆为两个尺寸组。([汽车数据网][1])
* VW Polo GTI Cup Edition 已确认同时存在三门和五门车身，拆成两个派生映射及两个独立尺寸组。([汽车数据网][2])
* SsangYong Rexton I 已闭合；Citroën Saxo Phase II 按三门和五门拆分，两种车身高度不同。([汽车数据网][3])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：72
* PENDING Ktype：32
* 已确认尺寸组：59
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20717	20717	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
20718	20718	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
20719	20719	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	MEDIUM	标准高度车身。	READY
20721	20721	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-LIMITED-01	MEDIUM	Limited较高车身配置。	READY
20722	20722	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	HIGH	标准高度车身。	READY
20832_3dr	20832	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	HIGH	GTI Cup Edition三门分支。	READY
20832_5dr	20832	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	HIGH	GTI Cup Edition五门分支。	READY
20873	20873	SUV	Rexton I		5	EU-SSANGYONG-REXTON-I-SUV-01	HIGH	RX230车身。	READY
21089_3dr	21089	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	1.1 Bifuel三门分支。	READY
21089_5dr	21089	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	1.1 Bifuel五门分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866	Auto-Data Jeep Cherokee III KJ 2.4i	https://www.auto-data.net/en/jeep-cherokee-iii-kj-2.4i-16v-147hp-awd-1126
EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	4500	1800	1690	Auto-Data Jeep Grand Cherokee I ZJ 4.0i; Auto-Data Jeep Grand Cherokee I ZJ 2.5 TD	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-4.0i-177hp-4x4-automatic-1165;https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-2.5-td-116hp-4x4-1164
EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-LIMITED-01	4500	1800	1720	Auto-Data Jeep Grand Cherokee I ZJ 5.2i V8	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.2i-v8-212hp-4x4-automatic-31370
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1459	Auto-Data Volkswagen Polo IV GTI Cup 3-door	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-cup-1.8-180hp-3-d-8430
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3916	1650	1459	Auto-Data Volkswagen Polo IV GTI Cup 5-door	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-cup-1.8-180hp-5-d-8431
EU-SSANGYONG-REXTON-I-SUV-01	4720	1870	1760	Auto-Data SsangYong Rexton I RX230	https://www.auto-data.net/en/ssangyong-rexton-i-rx-230-143hp-16025
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360	Auto-Data Citroen Saxo Phase II 3-door 1.1	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.1-60hp-44808
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data Citroen Saxo Phase II 5-door 1.1	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-5-door-1.1-60hp-44820
```

## 5) 下一步优先处理

1. 闭合 Peugeot 106 Electric、Toyota Corolla E90 Sedan、Fiat Siena、Tata Safari 和 Range Rover I。
2. 处理 Seat Ibiza III、Hyundai Getz 的三门/五门及改款边界。
3. 集中处理 Wrangler YJ、Pajero Canvas Top 和 Land Rover 110/127。
4. 最后处理 Ducato、Hilux、Ranger、Dyna、Transit Connect 与 Transporter T5 的轴距、驾驶室、货斗和车顶分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jeep-cherokee-iii-kj-2.4i-16v-147hp-awd-1126?utm_source=chatgpt.com "Jeep Cherokee III (KJ) 2.4i 16V (147 Hp) AWD /SUV 2001"
[2]: https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-cup-1.8-180hp-3-d-8430?utm_source=chatgpt.com "Specs of Volkswagen Polo IV (9N, facelift 2005) GTI Cup ..."
[3]: https://www.auto-data.net/en/ssangyong-rexton-i-rx-230-143hp-16025 "SsangYong Rexton I RX 230 (143 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 本轮新增 **5 条 READY 映射、5 个尺寸组**。
* Citroën Xsara Picasso 与 Tata Safari 2.0 TDI 4×2 已确认五门车身，尺寸来源明确标注宽度不含后视镜。([汽车目录][1])
* Jeep Wrangler YJ、Bentley Continental R 的固定外廓已闭合。([汽车数据网][2])
* Toyota Corolla AE92 四门 Twin Cam 16 GT 采用 Toyota 官方历史规格建组。([丰田汽车官网][3])
* Peugeot 106 Electric 存在高度来源冲突，Range Rover I 尚需确认三门/五门边界，本轮未强行建立映射。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：77
* PENDING Ktype：27
* 已确认尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20706	20706	MPV	Xsara Picasso I	N68	5	EU-CITROEN-XSARA-PICASSO-I-MPV-01	HIGH		READY
20716	20716	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-YJ-CONVERTIBLE-01	HIGH	YJ两门开放式车身。	READY
20788	20788	SUV	Safari I		5	EU-TATA-SAFARI-I-SUV-01	HIGH	五门4x2标准车身。	READY
20861	20861	Coupe	Continental R		2	EU-BENTLEY-CONTINENTAL-R-COUPE-01	HIGH		READY
21097	21097	Sedan	Corolla VI (E90)	AE92	4	EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	HIGH	AE92 Twin Cam 16 GT四门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-XSARA-PICASSO-I-MPV-01	4276	1751	1637	Automobile-Catalog Citroen Xsara Picasso 1.6i SX	https://www.automobile-catalog.com/car/2001/547895/citroen_xsara_picasso_1_6i_sx.html
EU-JEEP-WRANGLER-YJ-CONVERTIBLE-01	3879	1740	1765	Auto-Data Jeep Wrangler I (YJ)	https://www.auto-data.net/en/jeep-wrangler-i-yj-generation-341
EU-TATA-SAFARI-I-SUV-01	4800	1810	1910	Automobile-Catalog Tata Safari 2.0 TDi 4x2	https://www.automobile-catalog.com/car/2003/3418910/tata_safari_2_0_tdi_4x2.html
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462	Automobile-Catalog Bentley Continental R	https://www.automobile-catalog.com/car/1992/260690/bentley_continental_r.html
EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	4195	1655	1360	Toyota 75 Years Corolla 6th official specification	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003780/index.html
```

## 下一步优先处理

1. 解决 Peugeot 106 Electric 的车身高度冲突，以及 Range Rover I 的三门/五门边界。
2. 闭合 Seat Ibiza III、Hyundai Getz 的门数和改款分支。
3. 处理 Fiat Siena、AC Cobra IV、Land Rover 110/127 与 Pajero Canvas Top。
4. 最后集中处理 Ducato、Hilux、Ranger、Dyna、Transit Connect 和 Transporter T5 的轴距、驾驶室、货斗及车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/547895/citroen_xsara_picasso_1_6i_sx.html?utm_source=chatgpt.com "2001 Citroen Xsara Picasso 1.6i SX Specs Review (70 kW / 95 PS / 94 hp) (for Europe )"
[2]: https://www.auto-data.net/en/jeep-wrangler-model-161?utm_source=chatgpt.com "Jeep Wrangler | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003780/index.html?utm_source=chatgpt.com "Corolla 6th - Toyota Motor Corporation Official Global Website"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1) 更新点

* 本轮新增 **9 条 READY 映射、8 个尺寸组**。
* Range Rover I 的 `20796` 已拆分为三门、五门；`20795` 对应五门 2.5 TDi。三门与五门外廓尺寸相同，但按物理车身边界分别建组。([Ultimate Specs][1])
* Seat Ibiza III `20846` 已按三门、五门拆分；两个分支三维相同。([汽车数据网][2])
* Hyundai Getz `20852` 与 `20853` 已分别按改款前后及三门、五门拆分。Ktype、发动机代码和生产区间已对应至 TB 车身。([Tekstara][3])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：86
* PENDING Ktype：22
* 已确认尺寸组：72
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20795	20795	SUV	Range Rover I / Classic		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	2.5 TDi五门车身。	READY
20796_3dr	20796	SUV	Range Rover I / Classic		3	EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	HIGH	2.5 TD三门车身。	READY
20796_5dr	20796	SUV	Range Rover I / Classic		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	2.5 TD五门车身。	READY
20846_3dr	20846	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
20846_5dr	20846	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-HATCHBACK-5D-01	HIGH	五门车身分支。	READY
20852_3dr	20852	Hatchback	Getz I	TB	3	EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门车身。	READY
20852_5dr	20852	Hatchback	Getz I	TB	5	EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门车身。	READY
20853_3dr	20853	Hatchback	Getz I facelift	TB	3	EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门车身。	READY
20853_5dr	20853	Hatchback	Getz I facelift	TB	5	EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	4480	1820	1810	UltimateSpecs Land Rover Range Rover I 3d 2.5 TD	https://www.ultimatespecs.com/car-specs/Land-Rover/7409/Land-Rover-Range-Rover-I-3d-25-TD.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	4480	1820	1810	UltimateSpecs Land Rover Range Rover I 2.5 TD; UltimateSpecs Land Rover Range Rover I 2.5 TDi	https://www.ultimatespecs.com/car-specs/Land-Rover/7384/Land-Rover-Range-Rover-I-25-TD.html;https://www.ultimatespecs.com/car-specs/Land-Rover/7383/Land-Rover-Range-Rover-I-25-TDi.html
EU-SEAT-IBIZA-III-HATCHBACK-3D-01	3955	1700	1440	Auto-Data Seat Ibiza III Sport 2.0i	https://www.auto-data.net/en/seat-ibiza-iii-sport-2.0i-115hp-13487
EU-SEAT-IBIZA-III-HATCHBACK-5D-01	3955	1700	1440	Auto-Data Seat Ibiza III Sport 2.0i	https://www.auto-data.net/en/seat-ibiza-iii-sport-2.0i-115hp-13487
EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-PREFL-01	3810	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-82hp-13785
EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-PREFL-01	3810	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-82hp-13785
EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-FACELIFT-01	3825	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi HP	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-hp-110hp-13786
EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-FACELIFT-01	3825	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi HP	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-hp-110hp-13786
```

## 5) 下一步优先处理

1. 解决 Fiat Siena、Peugeot 106 Electric 和 AC Cobra IV 的跨年份或规格边界。
2. 处理 Land Rover 110/127 与 Mitsubishi Pajero III Canvas Top 的轴距、开放式车身边界。
3. 集中关闭 Ducato、Hilux、Ranger、Dyna、Transit Connect 和 Transporter T5 的轴距、驾驶室、车顶及货斗分支。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Land-Rover/7409/Land-Rover-Range-Rover-I-3d-25-TD.html "Land Rover Range Rover I 3d 2.5 TD Specs, Performance, Comparisons"
[2]: https://www.auto-data.net/en/seat-ibiza-iii-sport-2.0i-115hp-13487 "Seat Ibiza III Sport 2.0i (115 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://tekstara.lt/partscatalogue/droselio-korpusas-hyundai-getz-tb-1-6-2002-09-2005-09%2C8-00183-04901-16813-0002-00158-0100002%2C0100383%2C0100704.aspx?utm_source=chatgpt.com "droselio korpusas HYUNDAI GETZ (TB) 1.6 2002-09-2005-09 77 106"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1) 更新点

* 本轮新增 **4 条 READY 映射、3 个尺寸组**。
* AC Cobra 两个 Ktype 的年份、6.2 L 动力和功率边界实际对应 **Cobra Mk VI**，已纠正代际并复用同一敞篷尺寸组。([驱动站][1])
* Peugeot 106 Electric 的 Ktype 同时覆盖三门与五门 Phase I 车身，已拆成 `3dr`、`5dr` 两个派生映射；`1A` 对应三门，`1C` 对应五门。([AUTODOC][2])
* Phase I 两种门数使用相同外廓三维，但因门数车身边界不同分别建组。([汽车目录][3])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：90
* PENDING Ktype：19
* 已确认尺寸组：75
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20772	20772	Convertible	Cobra Mk VI		2	EU-AC-COBRA-MK-VI-CONVERTIBLE-01	HIGH	输入Cobra IV标签与2009年起6.2L车型边界不一致，按Mk VI映射。	READY
20773	20773	Convertible	Cobra Mk VI		2	EU-AC-COBRA-MK-VI-CONVERTIBLE-01	HIGH	输入Cobra IV标签与2009年起6.2L车型边界不一致，按Mk VI映射。	READY
21079_3dr	21079	Hatchback	106 I Phase I	1A	3	EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-3D-01	MEDIUM	Electric三门分支。	READY
21079_5dr	21079	Hatchback	106 I Phase I	1C	5	EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	Electric五门分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AC-COBRA-MK-VI-CONVERTIBLE-01	4020	1830	1130	Automobile-Catalog AC Cobra Mk VI full range; Drive.Place AC Cobra Mk VI 6.2	https://www.automobile-catalog.com/make/ac/cobra/cobra_vi/2015.html;https://ac.drive.place/cobra/mk-vi/group_roadster/347599
EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-3D-01	3564	1590	1369	Automobile-Catalog Peugeot 106 Phase I full range; AUTODOC Peugeot 106 I Electric 3/5 doors	https://www.automobile-catalog.com/make/peugeot/106/106_1/1995.html;https://www.auto-doc.fr/pieces-detachees/batterie-10142/peugeot/106/106-i-1a-1c/21079-electric
EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-5D-01	3564	1590	1369	Automobile-Catalog Peugeot 106 Phase I full range; AUTODOC Peugeot 106 I Electric 3/5 doors	https://www.automobile-catalog.com/make/peugeot/106/106_1/1995.html;https://www.auto-doc.fr/pieces-detachees/batterie-10142/peugeot/106/106-i-1a-1c/21079-electric
```

## 5) 下一步优先处理

1. 拆解 Fiat Siena `20763` 跨越的改款外廓边界，避免用单一 2002 年尺寸覆盖至 2012 年。
2. 确认 Land Rover `20799` 在封闭车身条件下实际覆盖 110、127 中的哪些分支。
3. 闭合 Pajero III Canvas Top `21314`、`21315` 的 `V64W/V74W` 车身代码与软顶外廓边界。
4. 集中处理剩余 Ducato、Hilux、Ranger、Dyna、Transit Connect 和 Transporter T5 多轴距、多车顶及驾驶室分支。

推进信号：CONTINUE

[1]: https://ac.drive.place/cobra/mk-vi/group_roadster/347599?utm_source=chatgpt.com "AC Cobra Mk VI 6.2 MT 647 hp Roadster — specifications"
[2]: https://www.auto-doc.fr/pieces-detachees/batterie-10142/peugeot/106/106-i-1a-1c/21079-electric?utm_source=chatgpt.com "Batterie Peugeot 106 3/5 Portes Électrique 27 CV ..."
[3]: https://www.automobile-catalog.com/make/peugeot/106/106_1/1995.html?utm_source=chatgpt.com "1995 Peugeot 106 phase-I Hatchback full range specs"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1) 更新点

* 本轮闭合 Mitsubishi Pajero III Canvas Top 的两个 Ktype。两个 Ktype 均覆盖 `V64W` 短轴与 `V74W` 长轴车身，并按有无车顶纵轨造成的高度差拆分物理分支；相同功率分支复用同一组尺寸事实。Mitsubishi 零件目录将 `V64W` 标记为短轴、`V74W` 标记为长轴，维修手册分别给出两种轴距及纵轨高度。([PartSouq][1])

## 2) 当前批次进度

* 输入 Ktype：100
* READY 映射：98
* PENDING Ktype：17
* 已确认尺寸组：79
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21314_swb_norails	21314	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	HIGH	V64W短轴无车顶纵轨分支。	READY
21314_swb_roofrails	21314	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	HIGH	V64W短轴带车顶纵轨分支。	READY
21314_lwb_norails	21314	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	HIGH	V74W长轴无车顶纵轨分支。	READY
21314_lwb_roofrails	21314	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	HIGH	V74W长轴带车顶纵轨分支。	READY
21315_swb_norails	21315	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	HIGH	V64W短轴无车顶纵轨分支。	READY
21315_swb_roofrails	21315	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	HIGH	V64W短轴带车顶纵轨分支。	READY
21315_lwb_norails	21315	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	HIGH	V74W长轴无车顶纵轨分支。	READY
21315_lwb_roofrails	21315	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	HIGH	V74W长轴带车顶纵轨分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	4260	1845	1845	Mitsubishi Pajero workshop manual - short wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=24
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	4260	1845	1875	Mitsubishi Pajero workshop manual - short wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=24
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	4775	1845	1855	Mitsubishi Pajero workshop manual - long wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=27
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	4775	1845	1885	Mitsubishi Pajero workshop manual - long wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=27
```

## 5) 下一步优先处理

1. 确认 Fiat Siena `20763` 的 `178/172/372` 车身边界及跨改款尺寸分支。
2. 拆分 Land Rover `20799` 的 110 与 127 封闭车身外廓。
3. 集中处理 Ducato、Hilux、Ranger、Dyna、Transit Connect 和 Transporter T5 的轴距、驾驶室、货斗与车顶分支。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MB882412&ssd=%24%2AKwGiloeB6OvQ5cTFp8G_qPruzsnXpqmkpbexvvjR7bX5s6z6vKu3vLP1taqz1Kz59JOioaHWsr20-ev9-canosCyvbT3peXh_uT6--0AAAAAZGOk7w%24 "Electrical | Mitsubishi PAJERO/MONTERO General (EXPORT) V64W | Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 1) 更新点

* 本轮闭合 **2 个 Ktype**，新增 **7 条 READY 映射、7 个尺寸组**。
* Ford Transit Connect `20862` 按短轴低顶与长轴高顶拆分；2006、2009 两次改款对应外廓未形成新的尺寸分支。([Ultimate Specs][1])
* VW Transporter T5 `20881` 按短轴/长轴及低顶/中顶/高顶拆为五个物理分支。

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：85
* READY 映射行：105
* PENDING Ktype：15
* 已确认尺寸组：86
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20862_swb_lowroof	20862	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	MEDIUM	Kasten/MPV共用短轴低顶外廓。	READY
20862_lwb_highroof	20862	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	MEDIUM	Kasten/MPV共用长轴高顶外廓。	READY
20881_swb_lowroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
20881_swb_midroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	MEDIUM	短轴中顶Bus分支。	READY
20881_lwb_lowroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
20881_lwb_midroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus分支。	READY
20881_lwb_highroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824	Ford Transit Connect official owner handbook; UltimateSpecs Ford Transit Connect Kombi 2009 L1H1 1.8 TDCi 110HP	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/ENUSA_CG3526_TRC_og_200606.pdf;https://www.ultimatespecs.com/car-specs/Ford/13453/Ford-Transit-Connect-Kombi-2009-L1H1-18-TDCi-110HP.html
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982	UltimateSpecs Ford Transit Connect Kombi 2006 L2H2 1.8 TDCi 110HP; UltimateSpecs Ford Transit Connect Kombi 2009 L2H2 1.8 TDCi 110HP	https://www.ultimatespecs.com/car-specs/Ford/51951/Ford-Transit-Connect-Kombi-2006-L2H2-FT230-TDCi-110HP.html;https://www.ultimatespecs.com/car-specs/Ford/13459/Ford-Transit-Connect-Kombi-2009-L2H2-18-TDCi-110HP.html
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959	Auto-Data Volkswagen Transporter T5 L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l1h1-49881
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160	Auto-Data Volkswagen Transporter T5 L1H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l1h2-49957
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959	Auto-Data Volkswagen Transporter T5 L2H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h1-49909
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160	Auto-Data Volkswagen Transporter T5 L2H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h2-49939
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460	Auto-Data Volkswagen Transporter T5 L2H3	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h3-49936
```

## 5) 下一步优先处理

1. 闭合 Fiat Siena `20763` 与 Land Rover 110/127 `20799`。
2. 批量拆分 Ducato `20694`、`20695`、`20696`、`20698`、`20848`、`20849`、`20850`、`20854`。
3. 最后处理 Hilux `20709`、Ranger `20754/20756` 与 Dyna `20919/20920` 的驾驶室、轴距和货斗分支。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Ford/13453/Ford-Transit-Connect-Kombi-2009-L1H1-18-TDCi-110HP.html?utm_source=chatgpt.com "Ford Transit Connect Kombi 2009 L1H1 1.8 TDCi 110HP Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 1) 更新点

* 本轮闭合 Land Rover `20799`。该 Ktype 的封闭式车身拆为 **110 Hard Top** 与 **110 Station Wagon** 两个物理分支；127 标准车型为加长驾驶室/货斗用途，不纳入当前“封闭越野车”映射。110 两种封闭车身宽度均为不含后视镜的 1790 mm，但长度不同。([汽车目录][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：86
* READY 映射行：107
* PENDING Ktype：14
* 已确认尺寸组：88
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20799_110_hardtop	20799	SUV	Land Rover One Ten		3	EU-LAND-ROVER-ONE-TEN-SUV-HARDTOP-01	MEDIUM	110三门Hard Top封闭车身。	READY
20799_110_stationwagon	20799	SUV	Land Rover One Ten		5	EU-LAND-ROVER-ONE-TEN-SUV-STATION-WAGON-01	MEDIUM	110五门Station Wagon封闭车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-ONE-TEN-SUV-HARDTOP-01	4445	1790	2035	Automobile-Catalog 1987 Land-Rover 110 Hard Top 2.5 Diesel	https://www.automobile-catalog.com/car/1987/1393910/land-rover_110_hard_top_2_5_diesel.html
EU-LAND-ROVER-ONE-TEN-SUV-STATION-WAGON-01	4580	1790	2035	Automobile-Catalog 1985 Land-Rover 110 Station Wagon 2.5 Diesel	https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html
```

## 5) 下一步优先处理

1. 批量拆分 Ducato `20694`、`20695`、`20696`、`20698`、`20848`、`20849`、`20850`、`20854`。
2. 处理 Hilux `20709`、Ranger `20754/20756` 与 Dyna `20919/20920` 的驾驶室、轴距和货斗分支。
3. 最后解决 Fiat Siena `20763` 跨多个车身代码及改款阶段的尺寸冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html?utm_source=chatgpt.com "1985 Land-Rover 110 Station Wagon 2.5 Diesel (man. 5)"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1) 更新点

* 本轮闭合 Toyota Dyna `20919`、`20920`。
* `20919` 按 Dyna 300 短轴的单排底盘与原厂栏板货厢拆为两个物理分支。
* `20920` 按 Dyna 350 中轴/长轴及底盘/栏板货厢拆为四个物理分支。
* Toyota 原厂资料分别列出各分支的完整长宽高，并明确宽度为**不含后视镜**口径。([xr793.com][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：88
* READY 映射行：113
* PENDING Ktype：12
* 已确认尺寸组：94
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20919_chassis_swb	20919	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	HIGH	Dyna 300短轴单排底盘分支。	READY
20919_dropside_swb	20919	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	HIGH	Dyna 300短轴原厂栏板货厢分支。	READY
20920_chassis_mwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	HIGH	Dyna 350中轴单排底盘分支。	READY
20920_dropside_mwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	HIGH	Dyna 350中轴原厂栏板货厢分支。	READY
20920_chassis_lwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	HIGH	Dyna 350长轴单排底盘分支。	READY
20920_dropside_lwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	HIGH	Dyna 350长轴原厂栏板货厢分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
```

## 5) 下一步优先处理

1. 批量拆分 Ducato `20694`、`20695`、`20696`、`20698`、`20848`、`20849`、`20850`、`20854` 的 X230/X244、轴距、车顶与车身形式。
2. 处理 Ranger `20754`、`20756` 的 Single Cab、Super Cab、Double Cab 分支。
3. 处理 Hilux `20709` 的 `KUN15/KUN35` 驾驶室边界。
4. 最后解决 Siena `20763` 跨 `178/172/372` 及多次改款的外廓差异。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf "Toyota_Dyna_GBNGV-025DY-VB.qxp"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 1) 更新点

* 本轮闭合 Ducato X244 的 `20848`、`20849`、`20850`，新增 **39 条 READY 映射、13 个尺寸组**。
* 三个 Ktype 共用同一套 X244 车身尺寸组；按 SWB/MWB/LWB、低顶/中顶/高顶及 11/15/MAXI 造成的实际高度差拆分。Fiat eLearn 的普通版与 4×4 技术资料给出的外廓矩阵一致，因此四驱未重复建组。([四卡数据][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：91
* READY 映射行：152
* PENDING Ktype：9
* 已确认尺寸组：107
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20848_11_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶Bus分支。	READY
20848_15_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶Bus分支。	READY
20848_maxi_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶Bus分支。	READY
20848_swb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶Bus分支。	READY
20848_maxi_swb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶Bus分支。	READY
20848_mwb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶Bus分支。	READY
20848_maxi_mwb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶Bus分支。	READY
20848_mwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶Bus分支。	READY
20848_maxi_mwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶Bus分支。	READY
20848_15_lwb_midroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶Bus分支。	READY
20848_maxi_lwb_midroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶Bus分支。	READY
20848_15_lwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶Bus分支。	READY
20848_maxi_lwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶Bus分支。	READY
20849_11_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶4x4 Bus分支。	READY
20849_15_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶4x4 Bus分支。	READY
20849_maxi_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶4x4 Bus分支。	READY
20849_swb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶4x4 Bus分支。	READY
20849_maxi_swb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶4x4 Bus分支。	READY
20849_mwb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶4x4 Bus分支。	READY
20849_maxi_mwb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶4x4 Bus分支。	READY
20849_mwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶4x4 Bus分支。	READY
20849_maxi_mwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶4x4 Bus分支。	READY
20849_15_lwb_midroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶4x4 Bus分支。	READY
20849_maxi_lwb_midroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶4x4 Bus分支。	READY
20849_15_lwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶4x4 Bus分支。	READY
20849_maxi_lwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶4x4 Bus分支。	READY
20850_11_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶Kasten分支。	READY
20850_15_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶Kasten分支。	READY
20850_maxi_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶Kasten分支。	READY
20850_swb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶Kasten分支。	READY
20850_maxi_swb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶Kasten分支。	READY
20850_mwb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶Kasten分支。	READY
20850_maxi_mwb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶Kasten分支。	READY
20850_mwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶Kasten分支。	READY
20850_maxi_mwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶Kasten分支。	READY
20850_15_lwb_midroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶Kasten分支。	READY
20850_maxi_lwb_midroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶Kasten分支。	READY
20850_15_lwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶Kasten分支。	READY
20850_maxi_lwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶Kasten分支。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
```

## 5) 下一步优先处理

1. 处理 Ducato X230 `20694`、`20695`、`20696`、`20698` 的短轴/中轴/长轴平台货厢分支。
2. 处理 Ducato X244 `20854` 的底盘驾驶室与原厂栏板货厢分支。
3. 关闭 Hilux `20709`、Ranger `20754/20756` 的驾驶室和货斗组合。
4. 最后解决 Siena `20763` 的跨改款车身边界。

推进信号：CONTINUE

[1]: https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010 "VEHICLE DIMENSIONS - Fiat - DUCATO - eLearn - 4CarData"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 1) 更新点

* 本轮闭合 Ducato X244 `20854`，新增 **5 条 READY 映射、5 个尺寸组**。
* 按 Fiat X244 Truck 尺寸矩阵拆分短轴、中轴、长轴以及标准/MAXI 高度。`11` 与 `15` 短轴外廓相同，未重复建组；中轴和长轴的 MAXI 版本因高度增加而独立建组。([四卡数据][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：92
* READY 映射行：157
* PENDING Ktype：8
* 已确认尺寸组：112
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20854_swb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	HIGH	11/15短轴Pritsche/Fahrgestell外廓。	READY
20854_mwb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	HIGH	15中轴Pritsche/Fahrgestell外廓。	READY
20854_mwb_maxi	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	HIGH	MAXI中轴Pritsche/Fahrgestell外廓。	READY
20854_lwb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	HIGH	15长轴Pritsche/Fahrgestell外廓。	READY
20854_lwb_maxi	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	HIGH	MAXI长轴Pritsche/Fahrgestell外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
```

## 5) 下一步优先处理

1. 闭合 Ducato X230 `20694`、`20695`、`20696`、`20698` 的短轴、中轴、长轴及标准/MAXI 平台分支。
2. 处理 Ranger `20754`、`20756` 的 Single Cab、Super Cab、Double Cab 外廓。
3. 处理 Hilux `20709` 的 2WD 驾驶室分支。
4. 最后解决 Siena `20763` 的跨改款车身边界。

推进信号：CONTINUE

[1]: https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010 "VEHICLE DIMENSIONS - Fiat - DUCATO - eLearn - 4CarData"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 1) 更新点

* 本轮闭合 Toyota Hilux `20709`。该 Ktype 对应第七代 Hilux 的 `KUN15` 左舵 2WD Single Cab；Toyota 2012 规格表给出的外廓为 5255 × 1760 × 1680 mm，其中宽度明确为不含后视镜口径。([丰田欧洲新闻中心][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：93
* READY 映射行：158
* PENDING Ktype：7
* 已确认尺寸组：113
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20709	20709	Pickup	Hilux VII	KUN15	2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	HIGH	KUN15两门2WD Single Cab。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK.pdf
```

## 5) 下一步优先处理

1. 闭合 Ranger `20754`、`20756`，拆分 2009 facelift 前后及 Regular Cab、Super Cab、Double Cab 外廓。
2. 批量处理 Ducato X230 `20694`、`20695`、`20696`、`20698` 的轴距和底盘分支。
3. 最后解决 Siena `20763` 的跨改款车身边界。

推进信号：CONTINUE

[1]: https://newsroom.toyota.eu/2019-hilux-2012-upgraded-2wd-25-d-4d-hilux-2012-engine-range-now-euro-v-compliant/?utm_source=chatgpt.com "Hilux 2012: Upgraded 2wd 2.5 d-4d ..."


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 1) 更新点

* 闭合 Ranger `20754`，按 **2009 改款前后、Regular/Super/Double Cab、低车身/高车身**拆成 8 个物理分支。
* Ford 官方 2008、2010 规格表直接支持 4×2 低车身尺寸；Auto-Data 补充确认后驱 Super Cab 与 Double Cab 高车身尺寸。相同动力不重复建组。
* Ranger `20756` 暂未关闭：3.0 TDCi 后驱的改款后驾驶室覆盖范围尚未完全闭合，本轮未套用 `20754` 的发动机无关假设。

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：94
* READY 映射行：166
* PENDING Ktype：6
* 已确认尺寸组：121
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20754_regularcab_prefl_lowbody	20754	Pickup	Ranger II	ET	2	EU-FORD-RANGER-II-PICKUP-REGULARCAB-PREFL-LOWBODY-01	MEDIUM	改款前Regular Cab后驱低车身。	READY
20754_supercab_prefl_lowbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-LOWBODY-01	MEDIUM	改款前Super Cab后驱低车身。	READY
20754_supercab_prefl_highbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	MEDIUM	改款前Super Cab后驱高车身。	READY
20754_doublecab_prefl_highbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	MEDIUM	改款前Double Cab后驱高车身。	READY
20754_regularcab_facelift_lowbody	20754	Pickup	Ranger II facelift	ET	2	EU-FORD-RANGER-II-PICKUP-REGULARCAB-FACELIFT-LOWBODY-01	MEDIUM	2009改款后Regular Cab后驱低车身。	READY
20754_supercab_facelift_lowbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-LOWBODY-01	MEDIUM	2009改款后Super Cab后驱低车身。	READY
20754_supercab_facelift_highbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-HIGHBODY-01	MEDIUM	2009改款后Super Cab后驱高车身。	READY
20754_doublecab_facelift_highbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-HIGHBODY-01	MEDIUM	2009改款后Double Cab后驱高车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-RANGER-II-PICKUP-REGULARCAB-PREFL-LOWBODY-01	5075	1715	1620	Ford Ranger 2008 UK official brochure archived copy	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-LOWBODY-01	5075	1715	1620	Ford Ranger 2008 UK official brochure archived copy	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	5075	1805	1745	Auto-Data Ford Ranger II Super Cab 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-super-cab-2.5-tdci-143hp-31994
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	5075	1805	1745	Auto-Data Ford Ranger II Double Cab 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-double-cab-2.5-tdci-143hp-31725
EU-FORD-RANGER-II-PICKUP-REGULARCAB-FACELIFT-LOWBODY-01	5080	1725	1622	Ford Ranger 2010 UK official brochure archived copy	https://www.xr793.com/wp-content/uploads/2022/09/2010-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-LOWBODY-01	5080	1725	1622	Ford Ranger 2010 UK official brochure archived copy	https://www.xr793.com/wp-content/uploads/2022/09/2010-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-HIGHBODY-01	5080	1788	1762	Auto-Data Ford Ranger II Super Cab facelift 2009 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-super-cab-facelift-2009-2.5-tdci-143hp-33185
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-HIGHBODY-01	5080	1788	1762	Auto-Data Ford Ranger II Double Cab facelift 2009 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-double-cab-facelift-2009-2.5-tdci-143hp-32868
```

## 5) 下一步优先处理

1. 关闭 Ranger `20756` 的 3.0 TDCi 后驱驾驶室及改款边界。
2. 批量关闭 Ducato X230 `20694`、`20695`、`20696`、`20698` 的轴距和底盘分支。
3. 最后处理 Siena `20763` 的 `178/172/372` 与改款外廓边界。

推进信号：CONTINUE


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 1) 更新点

* 闭合 Ranger `20756`。
* 3.0 TDCi 156 hp 后驱版本确认覆盖 **Super Cab** 与 **Double Cab**，均属于 2006–2010 改款前高车身外廓；直接关联上一轮已有尺寸组，不新增、不重复输出尺寸组。([汽车数据网][1])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：95
* READY 映射行：168
* PENDING Ktype：5
* 已确认尺寸组：121
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20756_supercab_prefl_highbody	20756	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	HIGH	改款前Super Cab后驱高车身。	READY
20756_doublecab_prefl_highbody	20756	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	HIGH	改款前Double Cab后驱高车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5) 下一步优先处理

1. 批量闭合 Ducato X230 `20694`、`20695`、`20696`、`20698` 的短轴、中轴、长轴及标准/MAXI 底盘分支。
2. 最后处理 Siena `20763` 跨改款车身边界。
3. PENDING 清零后立即执行一次机械收尾并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-ranger-ii-super-cab-3.0-tdci-156hp-30784?utm_source=chatgpt.com "Ford Ranger II Super Cab 3.0 TDCi (156 Hp) /Pick-up 2006"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 1) 更新点

* 本轮闭合 Fiat Siena `20763`。该 Ktype 明确覆盖 `178CXS1AAI`、`178BYA1AAT`、`178CYA1AAT` 三个地区车型代码，生产区间为 2001 年 9 月至 2012 年 12 月。([KMOTORSHOP][1])
* 三个代码均归入四门 Albea/Siena 178 系列外廓；改款前后核对尺寸均为 4186 × 1703 × 1489 mm，因此复用一个尺寸组，不建立仅因地区代码不同而重复的尺寸组。([汽车目录][2])

## 2) 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：96
* READY 映射行：169
* PENDING Ktype：4
* 已确认尺寸组：122
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20763	20763	Sedan	Albea I / Siena 178		4	EU-FIAT-SIENA-ALBEA-I-SEDAN-01	MEDIUM	178CXS1AAI、178BYA1AAT及178CYA1AAT地区代码共用四门外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SIENA-ALBEA-I-SEDAN-01	4186	1703	1489	Automobile-Catalog Fiat Albea 1.2 EL 2002; Automobile-Catalog Fiat Albea 1.2 16V Active 2005	https://www.automobile-catalog.com/car/2002/723335/fiat_albea_1_2_el.html;https://www.automobile-catalog.com/car/2005/723380/fiat_albea_1_2_16v_active.html
```

## 5) 下一步优先处理

1. 批量闭合 Ducato X230 `20694`、`20695`、`20696`、`20698`。
2. 重点确认 X230 平台/底盘的短轴、中轴、长轴完整车长以及 4×4 是否改变标准高度。
3. 四个 PENDING 清零后，下一轮直接执行机械收尾并输出两张最终完整 TSV及指定 sandbox 下载链接。

推进信号：CONTINUE

[1]: https://www.kmotorshop.com/en/device/car-list/4589 "Cars FIAT SIENA (178_, 172_, 372_) | K MOTORSHOP s.r.o."
[2]: https://www.automobile-catalog.com/car/2002/723335/fiat_albea_1_2_el.html?utm_source=chatgpt.com "2002 Fiat Albea 1.2 EL Specs Review (44 kW ..."


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* 已闭合最后 4 个 Ducato X230 Ktype：`20694`、`20695`、`20696`、`20698`。
* 新增 12 条轴距派生映射，复用 3 个稳定尺寸组：SWB、MWB、LWB。
* 已完成机械检查：表头正确、181 个 `id` 唯一、125 个 `DIMENSION_GROUP_ID` 唯一、100 个输入 Ktype 全覆盖、映射引用全部闭合、无孤立尺寸组、无 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：181
* PENDING：0
* DIMENSION_GROUP：125
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20694_swb	20694	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-SWB-01	MEDIUM	短轴Pritsche/Fahrgestell分支。	READY
20694_mwb	20694	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-MWB-01	MEDIUM	中轴Pritsche/Fahrgestell分支。	READY
20694_lwb	20694	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-LWB-01	MEDIUM	长轴Pritsche/Fahrgestell分支。	READY
20695_swb	20695	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-SWB-01	MEDIUM	短轴4x4 Pritsche/Fahrgestell分支。	READY
20695_mwb	20695	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-MWB-01	MEDIUM	中轴4x4 Pritsche/Fahrgestell分支。	READY
20695_lwb	20695	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-LWB-01	MEDIUM	长轴4x4 Pritsche/Fahrgestell分支。	READY
20696_swb	20696	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-SWB-01	MEDIUM	短轴Pritsche/Fahrgestell分支。	READY
20696_mwb	20696	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-MWB-01	MEDIUM	中轴Pritsche/Fahrgestell分支。	READY
20696_lwb	20696	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-LWB-01	MEDIUM	长轴Pritsche/Fahrgestell分支。	READY
20698_swb	20698	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-SWB-01	MEDIUM	短轴4x4 Pritsche/Fahrgestell分支。	READY
20698_mwb	20698	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-MWB-01	MEDIUM	中轴4x4 Pritsche/Fahrgestell分支。	READY
20698_lwb	20698	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-X230-TRUCK-LWB-01	MEDIUM	长轴4x4 Pritsche/Fahrgestell分支。	READY
20706	20706	MPV	Xsara Picasso I	N68	5	EU-CITROEN-XSARA-PICASSO-I-MPV-01	HIGH		READY
20709	20709	Pickup	Hilux VII	KUN15	2	EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	HIGH	KUN15两门2WD Single Cab。	READY
20716	20716	Convertible	Wrangler I	YJ	2	EU-JEEP-WRANGLER-YJ-CONVERTIBLE-01	HIGH	YJ两门开放式车身。	READY
20717	20717	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
20718	20718	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-KJ-SUV-01	HIGH		READY
20719	20719	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	MEDIUM	标准高度车身。	READY
20721	20721	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-LIMITED-01	MEDIUM	Limited较高车身配置。	READY
20722	20722	SUV	Grand Cherokee I	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	HIGH	标准高度车身。	READY
20735	20735	Hatchback	SX4 S-Cross I		5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH		READY
20737	20737	Sedan	Insignia A facelift	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH	四门三厢车身。	READY
20739	20739	Hatchback	Insignia A facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	HIGH	五门掀背车身。	READY
20740	20740	SUV	Mokka A	J13	5	EU-OPEL-MOKKA-A-SUV-01	HIGH		READY
20743	20743	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
20754_regularcab_prefl_lowbody	20754	Pickup	Ranger II	ET	2	EU-FORD-RANGER-II-PICKUP-REGULARCAB-PREFL-LOWBODY-01	MEDIUM	改款前Regular Cab后驱低车身。	READY
20754_supercab_prefl_lowbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-LOWBODY-01	MEDIUM	改款前Super Cab后驱低车身。	READY
20754_supercab_prefl_highbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	MEDIUM	改款前Super Cab后驱高车身。	READY
20754_doublecab_prefl_highbody	20754	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	MEDIUM	改款前Double Cab后驱高车身。	READY
20754_regularcab_facelift_lowbody	20754	Pickup	Ranger II facelift	ET	2	EU-FORD-RANGER-II-PICKUP-REGULARCAB-FACELIFT-LOWBODY-01	MEDIUM	2009改款后Regular Cab后驱低车身。	READY
20754_supercab_facelift_lowbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-LOWBODY-01	MEDIUM	2009改款后Super Cab后驱低车身。	READY
20754_supercab_facelift_highbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-HIGHBODY-01	MEDIUM	2009改款后Super Cab后驱高车身。	READY
20754_doublecab_facelift_highbody	20754	Pickup	Ranger II facelift	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-HIGHBODY-01	MEDIUM	2009改款后Double Cab后驱高车身。	READY
20756_supercab_prefl_highbody	20756	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	HIGH	改款前Super Cab后驱高车身。	READY
20756_doublecab_prefl_highbody	20756	Pickup	Ranger II	ET	4	EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	HIGH	改款前Double Cab后驱高车身。	READY
20761	20761	Sedan	Seville V		4	EU-CADILLAC-SEVILLE-V-SEDAN-01	HIGH		READY
20763	20763	Sedan	Albea I / Siena 178		4	EU-FIAT-SIENA-ALBEA-I-SEDAN-01	MEDIUM	178CXS1AAI、178BYA1AAT及178CYA1AAT地区代码共用四门外廓。	READY
20769	20769	Wagon	PT Cruiser		5	EU-CHRYSLER-PT-CRUISER-WAGON-01	HIGH	五门量产车身。	READY
20772	20772	Convertible	Cobra Mk VI		2	EU-AC-COBRA-MK-VI-CONVERTIBLE-01	HIGH	输入Cobra IV标签与2009年起6.2L车型边界不一致，按Mk VI映射。	READY
20773	20773	Convertible	Cobra Mk VI		2	EU-AC-COBRA-MK-VI-CONVERTIBLE-01	HIGH	输入Cobra IV标签与2009年起6.2L车型边界不一致，按Mk VI映射。	READY
20776	20776	MPV	Trajet	FO	5	EU-HYUNDAI-TRAJET-MPV-01	HIGH		READY
20778	20778	MPV	Rezzo	U100	5	EU-DAEWOO-REZZO-MPV-01	MEDIUM	U100车身亦以Tacuma名称销售。	READY
20785	20785	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20786	20786	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20787	20787	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
20788	20788	SUV	Safari I		5	EU-TATA-SAFARI-I-SUV-01	HIGH	五门4x2标准车身。	READY
20795	20795	SUV	Range Rover I / Classic		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	2.5 TDi五门车身。	READY
20796_3dr	20796	SUV	Range Rover I / Classic		3	EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	HIGH	2.5 TD三门车身。	READY
20796_5dr	20796	SUV	Range Rover I / Classic		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	2.5 TD五门车身。	READY
20799_110_hardtop	20799	SUV	Land Rover One Ten		3	EU-LAND-ROVER-ONE-TEN-SUV-HARDTOP-01	MEDIUM	110三门Hard Top封闭车身。	READY
20799_110_stationwagon	20799	SUV	Land Rover One Ten		5	EU-LAND-ROVER-ONE-TEN-SUV-STATION-WAGON-01	MEDIUM	110五门Station Wagon封闭车身。	READY
20800	20800	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	HIGH		READY
20812	20812	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-SEDAN-01	HIGH	四门三厢车身。	READY
20813	20813	Hatchback	Laguna II Phase I	BG09	5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	HIGH	五门掀背车身。	READY
20814	20814	Wagon	Laguna II Phase I	KG09	5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	HIGH	Grandtour旅行车身。	READY
20821	20821	Sedan	Rio I facelift	DC	4	EU-KIA-RIO-I-FACELIFT-SEDAN-01	HIGH		READY
20824	20824	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-T30-SUV-01	HIGH		READY
20825	20825	MPV	Matrix facelift	FC	5	EU-HYUNDAI-MATRIX-FACELIFT-MPV-01	HIGH		READY
20827	20827	Coupe	Vanquish I		2	EU-ASTON-MARTIN-VANQUISH-I-COUPE-01	HIGH	Vanquish S车身。	READY
20832_3dr	20832	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	HIGH	GTI Cup Edition三门分支。	READY
20832_5dr	20832	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	HIGH	GTI Cup Edition五门分支。	READY
20839	20839	Sedan	Sonata IV facelift	EF	4	EU-HYUNDAI-SONATA-EF-FACELIFT-SEDAN-01	MEDIUM	2001 facelift车身。	READY
20843	20843	Sedan	Corolla IX	E120	4	EU-TOYOTA-COROLLA-E120-SEDAN-01	HIGH		READY
20845	20845	MPV	Caravan IV LWB	RS	5	EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	3.8 AWD长轴距车身。	READY
20846_3dr	20846	Hatchback	Ibiza III	6L1	3	EU-SEAT-IBIZA-III-HATCHBACK-3D-01	HIGH	三门车身分支。	READY
20846_5dr	20846	Hatchback	Ibiza III	6L1	5	EU-SEAT-IBIZA-III-HATCHBACK-5D-01	HIGH	五门车身分支。	READY
20847	20847	Wagon	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-01	HIGH	Break旅行车身。	READY
20848_11_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶Bus分支。	READY
20848_15_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶Bus分支。	READY
20848_maxi_swb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶Bus分支。	READY
20848_swb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶Bus分支。	READY
20848_maxi_swb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶Bus分支。	READY
20848_mwb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶Bus分支。	READY
20848_maxi_mwb_lowroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶Bus分支。	READY
20848_mwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶Bus分支。	READY
20848_maxi_mwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶Bus分支。	READY
20848_15_lwb_midroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶Bus分支。	READY
20848_maxi_lwb_midroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶Bus分支。	READY
20848_15_lwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶Bus分支。	READY
20848_maxi_lwb_highroof	20848	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶Bus分支。	READY
20849_11_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶4x4 Bus分支。	READY
20849_15_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶4x4 Bus分支。	READY
20849_maxi_swb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶4x4 Bus分支。	READY
20849_swb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶4x4 Bus分支。	READY
20849_maxi_swb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶4x4 Bus分支。	READY
20849_mwb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶4x4 Bus分支。	READY
20849_maxi_mwb_lowroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶4x4 Bus分支。	READY
20849_mwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶4x4 Bus分支。	READY
20849_maxi_mwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶4x4 Bus分支。	READY
20849_15_lwb_midroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶4x4 Bus分支。	READY
20849_maxi_lwb_midroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶4x4 Bus分支。	READY
20849_15_lwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶4x4 Bus分支。	READY
20849_maxi_lwb_highroof	20849	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶4x4 Bus分支。	READY
20850_11_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	MEDIUM	11短轴低顶Kasten分支。	READY
20850_15_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	MEDIUM	15短轴低顶Kasten分支。	READY
20850_maxi_swb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	MEDIUM	MAXI短轴低顶Kasten分支。	READY
20850_swb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	MEDIUM	11/15短轴高顶Kasten分支。	READY
20850_maxi_swb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	MEDIUM	MAXI短轴高顶Kasten分支。	READY
20850_mwb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	MEDIUM	11/15中轴低顶Kasten分支。	READY
20850_maxi_mwb_lowroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	MEDIUM	MAXI中轴低顶Kasten分支。	READY
20850_mwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	MEDIUM	11/15中轴高顶Kasten分支。	READY
20850_maxi_mwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	MEDIUM	MAXI中轴高顶Kasten分支。	READY
20850_15_lwb_midroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	MEDIUM	15长轴中顶Kasten分支。	READY
20850_maxi_lwb_midroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	MEDIUM	MAXI长轴中顶Kasten分支。	READY
20850_15_lwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	MEDIUM	15长轴高顶Kasten分支。	READY
20850_maxi_lwb_highroof	20850	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	MEDIUM	MAXI长轴高顶Kasten分支。	READY
20852_3dr	20852	Hatchback	Getz I	TB	3	EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门车身。	READY
20852_5dr	20852	Hatchback	Getz I	TB	5	EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门车身。	READY
20853_3dr	20853	Hatchback	Getz I facelift	TB	3	EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门车身。	READY
20853_5dr	20853	Hatchback	Getz I facelift	TB	5	EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门车身。	READY
20854_swb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	HIGH	11/15短轴Pritsche/Fahrgestell外廓。	READY
20854_mwb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	HIGH	15中轴Pritsche/Fahrgestell外廓。	READY
20854_mwb_maxi	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	HIGH	MAXI中轴Pritsche/Fahrgestell外廓。	READY
20854_lwb_standard	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	HIGH	15长轴Pritsche/Fahrgestell外廓。	READY
20854_lwb_maxi	20854	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	HIGH	MAXI长轴Pritsche/Fahrgestell外廓。	READY
20856	20856	Coupe	Exige S2		2	EU-LOTUS-EXIGE-S2-COUPE-01	HIGH	Cup 240使用Exige S2固定车身外廓。	READY
20857	20857	Sedan	9-3 II	YS3F	4	EU-SAAB-9-3-II-SEDAN-01	HIGH	Sport Sedan车身。	READY
20861	20861	Coupe	Continental R		2	EU-BENTLEY-CONTINENTAL-R-COUPE-01	HIGH		READY
20862_swb_lowroof	20862	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	MEDIUM	Kasten/MPV共用短轴低顶外廓。	READY
20862_lwb_highroof	20862	Van	Transit Connect I			EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	MEDIUM	Kasten/MPV共用长轴高顶外廓。	READY
20863	20863	SUV	Forester II	SG	5	EU-SUBARU-FORESTER-II-SUV-01	MEDIUM	SG系五门车身。	READY
20864_prefl	20864	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008年外廓更新前分支。	READY
20864_facelift	20864	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008年外廓更新后分支。	READY
20872	20872	Convertible	500C/595C/695C	312	2	EU-ABARTH-500C-312-CONVERTIBLE-01	HIGH	500C、595C和695C共用312系敞篷外廓。	READY
20873	20873	SUV	Rexton I		5	EU-SSANGYONG-REXTON-I-SUV-01	HIGH	RX230车身。	READY
20881_swb_lowroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
20881_swb_midroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	MEDIUM	短轴中顶Bus分支。	READY
20881_lwb_lowroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus分支。	READY
20881_lwb_midroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	MEDIUM	长轴中顶Bus分支。	READY
20881_lwb_highroof	20881	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus分支。	READY
20884	20884	Wagon	Legacy IV	BP5	5	EU-SUBARU-LEGACY-IV-WAGON-01	HIGH	BP5旅行车。	READY
20890	20890	Sedan	Mégane II Phase II	LM	4	EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	HIGH	四门Classic车身。	READY
20891	20891	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-01	HIGH		READY
20892	20892	Convertible	Continental GTC II		2	EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	HIGH		READY
20893	20893	Wagon	V50 I		5	EU-VOLVO-V50-I-WAGON-01	HIGH		READY
20894	20894	Wagon	307 I	3E	5	EU-PEUGEOT-307-I-WAGON-01	HIGH	Break旅行车身。	READY
20896	20896	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-COUPE-RWD-01	HIGH	Carrera S后驱标准车身。	READY
20897	20897	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	HIGH	Carrera 4S四驱宽体。	READY
20898_prefl	20898	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008年外廓更新前分支。	READY
20898_facelift	20898	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008年外廓更新后分支。	READY
20910	20910	Sedan	A4 B7		4	EU-AUDI-A4-B7-SEDAN-01	HIGH		READY
20911	20911	Wagon	A4 B7		5	EU-AUDI-A4-B7-WAGON-01	HIGH	Avant车身。	READY
20912	20912	MPV	Golf V Plus	5M1	5	EU-VW-GOLF-V-PLUS-MPV-01	HIGH		READY
20913	20913	Hatchback	C5 I Phase II	DC	5	EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	HIGH	五门掀背车身。	READY
20915	20915	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-NF-SEDAN-01	HIGH		READY
20919_chassis_swb	20919	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	HIGH	Dyna 300短轴单排底盘分支。	READY
20919_dropside_swb	20919	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	HIGH	Dyna 300短轴原厂栏板货厢分支。	READY
20920_chassis_mwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	HIGH	Dyna 350中轴单排底盘分支。	READY
20920_dropside_mwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	HIGH	Dyna 350中轴原厂栏板货厢分支。	READY
20920_chassis_lwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	HIGH	Dyna 350长轴单排底盘分支。	READY
20920_dropside_lwb	20920	Pickup	Dyna VII		2	EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	HIGH	Dyna 350长轴原厂栏板货厢分支。	READY
20928	20928	MPV	Grand Carnival II	VQ	5	EU-KIA-GRAND-CARNIVAL-II-MPV-01	HIGH	长车身Grand Carnival。	READY
20930	20930	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
20983	20983	Sedan	Chairman H		4	EU-SSANGYONG-CHAIRMAN-H-SEDAN-01	MEDIUM	CM600S标准轴距车身。	READY
21079_3dr	21079	Hatchback	106 I Phase I	1A	3	EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-3D-01	MEDIUM	Electric三门分支。	READY
21079_5dr	21079	Hatchback	106 I Phase I	1C	5	EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	Electric五门分支。	READY
21089_3dr	21089	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	MEDIUM	1.1 Bifuel三门分支。	READY
21089_5dr	21089	Hatchback	Saxo Phase II		5	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	MEDIUM	1.1 Bifuel五门分支。	READY
21092	21092	Convertible	MINI Cabrio R52	R52	2	EU-MINI-MINI-R52-CONVERTIBLE-01	HIGH		READY
21097	21097	Sedan	Corolla VI (E90)	AE92	4	EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	HIGH	AE92 Twin Cam 16 GT四门车身。	READY
21137	21137	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21140	21140	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-FACELIFT-01	HIGH	2012 facelift车身。	READY
21146	21146	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21148	21148	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21150	21150	Hatchback	Mazda3 III		5	EU-MAZDA-MAZDA3-III-HATCHBACK-01	HIGH	BM/BN使用同一掀背外廓。	READY
21156	21156	Sedan	Mazda3 III		4	EU-MAZDA-MAZDA3-III-SEDAN-01	HIGH	BM/BN使用同一三厢外廓。	READY
21157	21157	Sedan	Mazda3 III		4	EU-MAZDA-MAZDA3-III-SEDAN-01	HIGH	BM/BN使用同一三厢外廓。	READY
21253	21253	Coupe	Continental GT II		2	EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	HIGH		READY
21314_swb_norails	21314	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	HIGH	V64W短轴无车顶纵轨分支。	READY
21314_swb_roofrails	21314	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	HIGH	V64W短轴带车顶纵轨分支。	READY
21314_lwb_norails	21314	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	HIGH	V74W长轴无车顶纵轨分支。	READY
21314_lwb_roofrails	21314	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	HIGH	V74W长轴带车顶纵轨分支。	READY
21315_swb_norails	21315	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	HIGH	V64W短轴无车顶纵轨分支。	READY
21315_swb_roofrails	21315	Convertible	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	HIGH	V64W短轴带车顶纵轨分支。	READY
21315_lwb_norails	21315	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	HIGH	V74W长轴无车顶纵轨分支。	READY
21315_lwb_roofrails	21315	Convertible	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	HIGH	V74W长轴带车顶纵轨分支。	READY
21318	21318	Sedan	A6 C6		4	EU-AUDI-A6-C6-SEDAN-01	HIGH		READY
21319	21319	Wagon	A6 C6		5	EU-AUDI-A6-C6-WAGON-01	HIGH	Avant车身。	READY
21320	21320	Wagon	A6 allroad C6		5	EU-AUDI-A6-C6-ALLROAD-WAGON-01	HIGH	Allroad车身。	READY
21321	21321	Wagon	A6 allroad C6		5	EU-AUDI-A6-C6-ALLROAD-WAGON-01	HIGH	Allroad车身。	READY
21322	21322	Convertible	A4 B7		2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	Cabriolet车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1001-1100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-X230-TRUCK-SWB-01	4770	2000	2100	Fiat Ducato 230 owner handbook; Swiss type approval FIAT Ducato 14 2.8TD	https://www.gebruikershandleiding.com/Fiat-Ducato-230/preview-handleiding-573899.html?page=0171;https://typenscheinschweiz.ch/pdf/auto/3FA230
EU-FIAT-DUCATO-X230-TRUCK-MWB-01	5120	2000	2100	Fiat Ducato 230 owner handbook; Swiss type approval FIAT Ducato 18 2.5TD	https://www.gebruikershandleiding.com/Fiat-Ducato-230/preview-handleiding-573899.html?page=0171;https://typenscheinschweiz.ch/pdf/auto/3FA196
EU-FIAT-DUCATO-X230-TRUCK-LWB-01	5620	2000	2100	Fiat Ducato 230 owner handbook; Swiss type approval FIAT Ducato 18 2.5TD	https://www.gebruikershandleiding.com/Fiat-Ducato-230/preview-handleiding-573899.html?page=0171;https://typenscheinschweiz.ch/pdf/auto/3FA196
EU-CITROEN-XSARA-PICASSO-I-MPV-01	4276	1751	1637	Automobile-Catalog Citroen Xsara Picasso 1.6i SX	https://www.automobile-catalog.com/car/2001/547895/citroen_xsara_picasso_1_6i_sx.html
EU-TOYOTA-HILUX-VII-PICKUP-SINGLE-CAB-2WD-01	5255	1760	1680	Toyota Hilux 2012 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Hilux-2012-UK.pdf
EU-JEEP-WRANGLER-YJ-CONVERTIBLE-01	3879	1740	1765	Auto-Data Jeep Wrangler I (YJ)	https://www.auto-data.net/en/jeep-wrangler-i-yj-generation-341
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866	Auto-Data Jeep Cherokee III KJ 2.4i	https://www.auto-data.net/en/jeep-cherokee-iii-kj-2.4i-16v-147hp-awd-1126
EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-STANDARD-01	4500	1800	1690	Auto-Data Jeep Grand Cherokee I ZJ 4.0i; Auto-Data Jeep Grand Cherokee I ZJ 2.5 TD	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-4.0i-177hp-4x4-automatic-1165;https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-2.5-td-116hp-4x4-1164
EU-JEEP-GRAND-CHEROKEE-ZJ-SUV-LIMITED-01	4500	1800	1720	Auto-Data Jeep Grand Cherokee I ZJ 5.2i V8	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.2i-v8-212hp-4x4-automatic-31370
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575	UltimateSpecs Suzuki SX4 S-Cross 1.6 DDiS	https://www.ultimatespecs.com/car-specs/Suzuki/66919/Suzuki-SX4-S-Cross-16-DDiS-GLX-EL-2WD.html
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	UltimateSpecs Opel Insignia 4 doors Facelift 2.0 CDTI	https://www.ultimatespecs.com/car-specs/Opel/71112/Opel-Insignia-4-doors-Facelift-20-CDTI-ecoFLEX-140HP-Selective.html
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498	UltimateSpecs Opel Insignia 5 doors Facelift 2.0 CDTI	https://www.ultimatespecs.com/car-specs/Opel/66374/Opel-Insignia-5-doors-Facelift-Excellence-20-CDTI-163HP-Auto.html
EU-OPEL-MOKKA-A-SUV-01	4278	1777	1658	UltimateSpecs Opel Mokka A 1.4 Turbo	https://www.ultimatespecs.com/car-specs/Opel/67678/Opel-Mokka-A-14-Turbo-140HP-4x2-Start-Stop-Selective.html
EU-BMW-X5-F15-SUV-01	4886	1938	1762	BMW X5 (F15) official specification sheet	https://bps.bmw.com.tw/uploads/bps/1605240477_OZDbT4.pdf
EU-FORD-RANGER-II-PICKUP-REGULARCAB-PREFL-LOWBODY-01	5075	1715	1620	Ford Ranger 2008 UK official brochure archived copy	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-LOWBODY-01	5075	1715	1620	Ford Ranger 2008 UK official brochure archived copy	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-PREFL-HIGHBODY-01	5075	1805	1745	Auto-Data Ford Ranger II Super Cab 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-super-cab-2.5-tdci-143hp-31994
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-PREFL-HIGHBODY-01	5075	1805	1745	Auto-Data Ford Ranger II Double Cab 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-double-cab-2.5-tdci-143hp-31725
EU-FORD-RANGER-II-PICKUP-REGULARCAB-FACELIFT-LOWBODY-01	5080	1725	1622	Ford Ranger 2010 UK official brochure archived copy	https://www.xr793.com/wp-content/uploads/2022/09/2010-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-LOWBODY-01	5080	1725	1622	Ford Ranger 2010 UK official brochure archived copy	https://www.xr793.com/wp-content/uploads/2022/09/2010-Ford-Ranger-UK.pdf
EU-FORD-RANGER-II-PICKUP-SUPERCAB-FACELIFT-HIGHBODY-01	5080	1788	1762	Auto-Data Ford Ranger II Super Cab facelift 2009 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-super-cab-facelift-2009-2.5-tdci-143hp-33185
EU-FORD-RANGER-II-PICKUP-DOUBLECAB-FACELIFT-HIGHBODY-01	5080	1788	1762	Auto-Data Ford Ranger II Double Cab facelift 2009 2.5 TDCi	https://www.auto-data.net/en/ford-ranger-ii-double-cab-facelift-2009-2.5-tdci-143hp-32868
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414	Auto-Data Cadillac Seville V 4.6 V8	https://www.auto-data.net/en/cadillac-seville-v-4.6-i-v8-32-279hp-11734
EU-FIAT-SIENA-ALBEA-I-SEDAN-01	4186	1703	1489	Automobile-Catalog Fiat Albea 1.2 EL 2002; Automobile-Catalog Fiat Albea 1.2 16V Active 2005	https://www.automobile-catalog.com/car/2002/723335/fiat_albea_1_2_el.html;https://www.automobile-catalog.com/car/2005/723380/fiat_albea_1_2_16v_active.html
EU-CHRYSLER-PT-CRUISER-WAGON-01	4290	1705	1600	Auto-Data Chrysler PT Cruiser	https://www.auto-data.net/en/chrysler-pt-cruiser-generation-3250
EU-AC-COBRA-MK-VI-CONVERTIBLE-01	4020	1830	1130	Automobile-Catalog AC Cobra Mk VI full range; Drive.Place AC Cobra Mk VI 6.2	https://www.automobile-catalog.com/make/ac/cobra/cobra_vi/2015.html;https://ac.drive.place/cobra/mk-vi/group_roadster/347599
EU-HYUNDAI-TRAJET-MPV-01	4700	1840	1760	UltimateSpecs Hyundai Trajet 2.0 CRDi	https://www.ultimatespecs.com/car-specs/Hyundai/4451/Hyundai-Trajet-20-CRDi.html
EU-DAEWOO-REZZO-MPV-01	4350	1755	1630	UltimateSpecs Chevrolet Tacuma 1.6 16v SX	https://www.ultimatespecs.com/car-specs/Chevrolet/50189/Chevrolet-Tacuma-16-16v-SX.html
EU-TATA-INDICA-I-HATCHBACK-01	3660	1625	1485	Auto-Data Tata Indica 1.4 TD	https://www.auto-data.net/en/tata-indica-1.4-td-71hp-1216
EU-TATA-SAFARI-I-SUV-01	4800	1810	1910	Automobile-Catalog Tata Safari 2.0 TDi 4x2	https://www.automobile-catalog.com/car/2003/3418910/tata_safari_2_0_tdi_4x2.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	4480	1820	1810	UltimateSpecs Land Rover Range Rover I 2.5 TD; UltimateSpecs Land Rover Range Rover I 2.5 TDi	https://www.ultimatespecs.com/car-specs/Land-Rover/7384/Land-Rover-Range-Rover-I-25-TD.html;https://www.ultimatespecs.com/car-specs/Land-Rover/7383/Land-Rover-Range-Rover-I-25-TDi.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	4480	1820	1810	UltimateSpecs Land Rover Range Rover I 3d 2.5 TD	https://www.ultimatespecs.com/car-specs/Land-Rover/7409/Land-Rover-Range-Rover-I-3d-25-TD.html
EU-LAND-ROVER-ONE-TEN-SUV-HARDTOP-01	4445	1790	2035	Automobile-Catalog 1987 Land-Rover 110 Hard Top 2.5 Diesel	https://www.automobile-catalog.com/car/1987/1393910/land-rover_110_hard_top_2_5_diesel.html
EU-LAND-ROVER-ONE-TEN-SUV-STATION-WAGON-01	4580	1790	2035	Automobile-Catalog 1985 Land-Rover 110 Station Wagon 2.5 Diesel	https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html
EU-RENAULT-SCENIC-I-PHASE-II-MPV-01	4170	1700	1680	UltimateSpecs Renault Scenic I 1.6 16v	https://www.ultimatespecs.com/car-specs/Renault/6625/Renault-Scenic-1-16-16v.html
EU-FORD-MONDEO-III-SEDAN-01	4731	1812	1429	UltimateSpecs Ford Mondeo III Sedan 2.0 TDdi	https://www.ultimatespecs.com/car-specs/Ford/47628/Ford-Mondeo-3-Sedan-20-TDdi-115HP-Ghia.html
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II 2.2 dCi	https://www.auto-data.net/en/renault-laguna-ii-2.2-dci-150hp-10331
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443	Auto-Data Renault Laguna II Grandtour 2.2 dCi	https://www.auto-data.net/en/renault-laguna-ii-grandtour-2.2-dci-150hp-10318
EU-KIA-RIO-I-FACELIFT-SEDAN-01	4240	1680	1440	Auto-Data Kia Rio I Sedan facelift 1.3i	https://www.auto-data.net/en/kia-rio-i-sedan-dc-facelift-2002-1.3i-82hp-2685
EU-NISSAN-X-TRAIL-T30-SUV-01	4510	1760	1750	UltimateSpecs Nissan X-Trail T30 2.5 4WD	https://www.ultimatespecs.com/car-specs/Nissan/6832/Nissan-X-Trail-%28T30%29-25-4WD.html
EU-HYUNDAI-MATRIX-FACELIFT-MPV-01	4025	1740	1685	UltimateSpecs Hyundai Matrix 2006 1.5 CRDi VGT	https://www.ultimatespecs.com/car-specs/Hyundai/51677/Hyundai-Matrix-2006-15-CRDi-VGT.html
EU-ASTON-MARTIN-VANQUISH-I-COUPE-01	4665	1923	1318	UltimateSpecs Aston Martin Vanquish S	https://www.ultimatespecs.com/car-specs/Aston-Martin/685/Aston-Martin-Vanquish-S.html
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1459	Auto-Data Volkswagen Polo IV GTI Cup 3-door	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-cup-1.8-180hp-3-d-8430
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3916	1650	1459	Auto-Data Volkswagen Polo IV GTI Cup 5-door	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-cup-1.8-180hp-5-d-8431
EU-HYUNDAI-SONATA-EF-FACELIFT-SEDAN-01	4747	1820	1422	UltimateSpecs Hyundai Sonata IV.5 2.0i	https://www.ultimatespecs.com/car-specs/Hyundai/4440/Hyundai-Sonata-IV5-20i.html
EU-TOYOTA-COROLLA-E120-SEDAN-01	4375	1710	1470	Auto-Data Toyota Corolla IX E120/E130	https://www.auto-data.net/en/toyota-corolla-ix-e120-e130-generation-818
EU-DODGE-CARAVAN-IV-MPV-LWB-01	5093	1995	1750	Auto-Data Dodge Caravan IV LWB 3.8 AWD	https://www.auto-data.net/en/dodge-caravan-iv-lwb-3.8-v6-218hp-4x4-automatic-29967
EU-SEAT-IBIZA-III-HATCHBACK-3D-01	3955	1700	1440	Auto-Data Seat Ibiza III Sport 2.0i	https://www.auto-data.net/en/seat-ibiza-iii-sport-2.0i-115hp-13487
EU-SEAT-IBIZA-III-HATCHBACK-5D-01	3955	1700	1440	Auto-Data Seat Ibiza III Sport 2.0i	https://www.auto-data.net/en/seat-ibiza-iii-sport-2.0i-115hp-13487
EU-PEUGEOT-307-I-WAGON-01	4419	1757	1544	Automobile-Catalog Peugeot 307 Break 1.4	https://www.automobile-catalog.com/car/2002/2617325/peugeot_307_break_estate_1_4_75.html
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860	Fiat Ducato X244 eLearn vehicle dimensions; Fiat Ducato X244 4x4 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010;https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-PREFL-01	3810	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-82hp-13785
EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-PREFL-01	3810	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-82hp-13785
EU-HYUNDAI-GETZ-TB-HATCHBACK-3D-FACELIFT-01	3825	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi HP	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-hp-110hp-13786
EU-HYUNDAI-GETZ-TB-HATCHBACK-5D-FACELIFT-01	3825	1665	1490	Auto-Data Hyundai Getz 1.5 CRDi HP	https://www.auto-data.net/en/hyundai-getz-1.5-crdi-hp-110hp-13786
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125	Fiat Ducato X244 eLearn truck vehicle dimensions	https://4cardata.info/elearn/244/2/244000002/244000000/244000000/244000010
EU-LOTUS-EXIGE-S2-COUPE-01	3785	1719	1170	UltimateSpecs Lotus Exige S2 S	https://www.ultimatespecs.com/car-specs/Lotus/12811/Lotus-Exige-S2-S.html
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466	Auto-Data Saab 9-3 Sedan II	https://www.auto-data.net/en/saab-9-3-sedan-ii-generation-2537
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462	Automobile-Catalog Bentley Continental R	https://www.automobile-catalog.com/car/1992/260690/bentley_continental_r.html
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824	Ford Transit Connect official owner handbook; UltimateSpecs Ford Transit Connect Kombi 2009 L1H1 1.8 TDCi 110HP	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/ENUSA_CG3526_TRC_og_200606.pdf;https://www.ultimatespecs.com/car-specs/Ford/13453/Ford-Transit-Connect-Kombi-2009-L1H1-18-TDCi-110HP.html
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982	UltimateSpecs Ford Transit Connect Kombi 2006 L2H2 1.8 TDCi 110HP; UltimateSpecs Ford Transit Connect Kombi 2009 L2H2 1.8 TDCi 110HP	https://www.ultimatespecs.com/car-specs/Ford/51951/Ford-Transit-Connect-Kombi-2006-L2H2-FT230-TDCi-110HP.html;https://www.ultimatespecs.com/car-specs/Ford/13459/Ford-Transit-Connect-Kombi-2009-L2H2-18-TDCi-110HP.html
EU-SUBARU-FORESTER-II-SUV-01	4450	1735	1590	Auto-Data Subaru Forester II	https://www.auto-data.net/en/subaru-forester-ii-generation-3623
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005 1.8 TFSI	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-1.8-tfsi-160hp-4183
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008 1.8 TFSI	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-1.8-tfsi-160hp-27144
EU-ABARTH-500C-312-CONVERTIBLE-01	3657	1627	1485	UltimateSpecs Abarth 500C 1.4 T-JET	https://www.ultimatespecs.com/car-specs/Abarth/63008/Abarth-500C-14-16v-T-JET-135HP-.html
EU-SSANGYONG-REXTON-I-SUV-01	4720	1870	1760	Auto-Data SsangYong Rexton I RX230	https://www.auto-data.net/en/ssangyong-rexton-i-rx-230-143hp-16025
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959	Auto-Data Volkswagen Transporter T5 L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l1h1-49881
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160	Auto-Data Volkswagen Transporter T5 L1H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l1h2-49957
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959	Auto-Data Volkswagen Transporter T5 L2H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h1-49909
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160	Auto-Data Volkswagen Transporter T5 L2H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h2-49939
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460	Auto-Data Volkswagen Transporter T5 L2H3	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-2.5-tdi-130hp-l2h3-49936
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470	Subaru Legacy 2009 official brochure	https://www.subaru.fr/docs/brochures/Documentation_2009_Subaru_Legacy.pdf
EU-RENAULT-MEGANE-II-PHASE-II-SEDAN-01	4498	1777	1460	Auto-Data Renault Megane II Classic Phase II 2.0 dCi	https://www.auto-data.net/en/renault-megane-ii-classic-phase-ii-2006-2.0-dci-150hp-fap-30269
EU-VOLVO-S40-II-SEDAN-01	4468	1770	1452	UltimateSpecs Volvo S40 II D5	https://www.ultimatespecs.com/car-specs/Volvo/1106/Volvo-S40-II-D5-Aut.html
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403	UltimateSpecs Bentley Continental GTC II V8	https://www.ultimatespecs.com/car-specs/Bentley/63718/Bentley-Continental-GTC-II-V8.html
EU-VOLVO-V50-I-WAGON-01	4510	1770	1450	UltimateSpecs Volvo V50 D5	https://www.ultimatespecs.com/car-specs/Volvo/4649/Volvo-V50-D5-Aut.html
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300	UltimateSpecs Porsche 911 (997) Carrera S	https://www.ultimatespecs.com/car-specs/Porsche/1790/Porsche-911-%28997%29-Carrera-S.html
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300	UltimateSpecs Porsche 911 (997) Carrera 4S	https://www.ultimatespecs.com/car-specs/Porsche/1800/Porsche-911-%28997%29-Carrera-4S.html
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427	UltimateSpecs Audi A4 B7 2.0 TFSI Quattro	https://www.ultimatespecs.com/car-specs/Audi/3870/Audi-A4-%28B7%29-20-TFSI-Quattro.html
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427	UltimateSpecs Audi A4 (B7) Avant 2.0 TFSI	https://www.ultimatespecs.com/car-specs/Audi/55826/Audi-A4-%28B7%29-Avant-20-TFSI-6speed-200HP.html
EU-VW-GOLF-V-PLUS-MPV-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 2.0 TDI	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4750	1770	1480	UltimateSpecs Citroen C5 2.0 16v	https://www.ultimatespecs.com/car-specs/Citroen/4104/Citroen-C5-20-16v.html
EU-HYUNDAI-SONATA-NF-SEDAN-01	4800	1830	1480	UltimateSpecs Hyundai Sonata V 2.0i	https://www.ultimatespecs.com/car-specs/Hyundai/4444/Hyundai-Sonata-V-20i.html
EU-TOYOTA-DYNA-VII-PICKUP-SWB-CHASSIS-CAB-01	4280	1695	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-SWB-DROPSIDE-01	4380	1695	2194	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-CHASSIS-CAB-01	4525	1900	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-MWB-DROPSIDE-01	4663	2000	2231	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-CHASSIS-CAB-01	5840	1900	2055	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-TOYOTA-DYNA-VII-PICKUP-LWB-DROPSIDE-01	5993	2075	2235	Toyota Dyna UK official brochure 2005 archived copy	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Dyna-UK.pdf
EU-KIA-GRAND-CARNIVAL-II-MPV-01	5130	1985	1780	Auto-Data Kia Grand Carnival II 2.9 CRDi	https://www.auto-data.net/en/kia-grand-carnival-ii-2.9-crdi-192hp-automatic-34420
EU-SSANGYONG-CHAIRMAN-H-SEDAN-01	5055	1825	1465	Auto-Data SsangYong Chairman H CM600S	https://www.auto-data.net/en/ssangyong-chairman-h-cm600s-3.2-i-24v-220hp-16015
EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-3D-01	3564	1590	1369	Automobile-Catalog Peugeot 106 Phase I full range; AUTODOC Peugeot 106 I Electric 3/5 doors	https://www.automobile-catalog.com/make/peugeot/106/106_1/1995.html;https://www.auto-doc.fr/pieces-detachees/batterie-10142/peugeot/106/106-i-1a-1c/21079-electric
EU-PEUGEOT-106-I-PHASE-I-HATCHBACK-5D-01	3564	1590	1369	Automobile-Catalog Peugeot 106 Phase I full range; AUTODOC Peugeot 106 I Electric 3/5 doors	https://www.automobile-catalog.com/make/peugeot/106/106_1/1995.html;https://www.auto-doc.fr/pieces-detachees/batterie-10142/peugeot/106/106-i-1a-1c/21079-electric
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360	Auto-Data Citroen Saxo Phase II 3-door 1.1	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.1-60hp-44808
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368	Auto-Data Citroen Saxo Phase II 5-door 1.1	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-5-door-1.1-60hp-44820
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420	UltimateSpecs MINI Cabrio R52 Cooper S	https://www.ultimatespecs.com/car-specs/Mini/6893/Mini-Mini-Cabrio-R52-Cooper-S.html
EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	4195	1655	1360	Toyota 75 Years Corolla 6th official specification	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60003780/index.html
EU-MAZDA-MAZDA3-III-HATCHBACK-01	4465	1795	1450	UltimateSpecs Mazda3 III Hatchback	https://www.ultimatespecs.com/car-specs/Mazda/67106/Mazda-3-III-SKYACTIV-G-20-120HP.html
EU-MERCEDES-BENZ-GLK-X204-SUV-FACELIFT-01	4536	1840	1669	UltimateSpecs Mercedes-Benz GLK (X204 2012) 250 4MATIC	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/65885/Mercedes-Benz-GLK-%28X204-2012%29-250-4MATIC-BlueEFFICIENCY.html
EU-MAZDA-MAZDA3-III-SEDAN-01	4585	1795	1450	UltimateSpecs Mazda3 III SportSedan	https://www.ultimatespecs.com/car-specs/Mazda/67112/Mazda-3-III-SportSedan-SKYACTIV-G-20-120HP.html
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404	UltimateSpecs Bentley Continental GT II V8	https://www.ultimatespecs.com/car-specs/Bentley/63701/Bentley-Continental-GT-2-V8.html
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-NORAILS-01	4260	1845	1845	Mitsubishi Pajero workshop manual - short wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=24
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-SWB-ROOFRAILS-01	4260	1845	1875	Mitsubishi Pajero workshop manual - short wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=24
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-NORAILS-01	4775	1845	1855	Mitsubishi Pajero workshop manual - long wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=27
EU-MITSUBISHI-PAJERO-III-CANVAS-TOP-LWB-ROOFRAILS-01	4775	1845	1885	Mitsubishi Pajero workshop manual - long wheelbase specifications	https://www.manualslib.fr/manual/332122/Mitsubishi-Pajero.html?page=27
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459	UltimateSpecs Audi A6 (C6) 3.0 TDI Quattro	https://www.ultimatespecs.com/car-specs/Audi/125868/Audi-A6-%28C6%29-30-TDI-V6-225HP-Quattro.html
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463	UltimateSpecs Audi A6 C6 Avant	https://www.ultimatespecs.com/car-specs/Audi/25424/Audi-A6-%28C6%29-Avant-30-TDI-240HP-Quattro-DPF.html
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520	UltimateSpecs Audi A6 (C6) Allroad 3.0 TDI	https://www.ultimatespecs.com/car-specs/Audi/3950/Audi-A6-%28C6%29-Allroad-Quattro-30-TDI.html
EU-AUDI-A4-B7-CONVERTIBLE-01	4570	1780	1390	UltimateSpecs Audi A4 (B7) Cabriolet 2.0 TFSI	https://www.ultimatespecs.com/car-specs/Audi/3880/Audi-A4-%28B7%29-Cabriolet-20-TFSI.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1001-1100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01 的 HeightMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1001-1100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1001-1100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2275 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1179 行）

- 尺寸冲突协调：
  - EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01 -> EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02：3916x1650x1467 与 3916x1650x1459，创建新尺寸组
  - EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01 -> EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02：3897x1650x1465 与 3916x1650x1459，创建新尺寸组
  - EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01 -> EU-CITROEN-C5-I-PHASE-II-HATCHBACK-02：4745x1780x1476 与 4750x1770x1480，创建新尺寸组
  - EU-AUDI-A4-B7-CONVERTIBLE-01 -> EU-AUDI-A4-B7-CONVERTIBLE-02：4573x1777x1391 与 4570x1780x1390，创建新尺寸组
