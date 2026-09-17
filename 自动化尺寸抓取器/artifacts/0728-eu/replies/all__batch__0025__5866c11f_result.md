# 任务：all 第 2401-2500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0025__5866c11f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2401-2500 行

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
all 第 2401-2500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	106 i	1.4 LE Mans	Schrägheck	Frontantrieb	Benzin	69	94	Sep 1991	Nov 1994	2024-03-01	2468
Peugeot	106 i	1.6	Schrägheck	Frontantrieb	Benzin	65	88	Jun 1993	Apr 1996	2024-03-01	2469
Peugeot	J5	2.5 D	Bus	Frontantrieb	Diesel	54	73	Sep 1981	Sep 1990	2024-03-01	2470
Peugeot	J5	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	54	73	Sep 1981	Sep 1990	2024-03-01	2471
Peugeot	J5	2.5 TD	Bus	Frontantrieb	Diesel	70	95	Oct 1990	Feb 1994	2024-03-01	2472
Peugeot	J5	2	Bus	Frontantrieb	Benzin	55	75	Sep 1981	Sep 1990	2024-03-01	2473
Peugeot	J5	1.9 D	Bus	Frontantrieb	Diesel	51	70	Oct 1990	Feb 1994	2024-03-01	2474
Peugeot	306	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	May 1993	May 2001	2024-03-01	2475
Peugeot	306	1.9 DT	Schrägheck	Frontantrieb	Diesel	66	90	May 1993	May 2001	2024-03-01	2476
VW	Touran	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	77	105	May 2010	May 2015	2024-03-01	2477
Peugeot	306	1.1	Schrägheck	Frontantrieb	Benzin	44	60	May 1993	May 2001	2024-03-01	2478
Porsche	Cayenne	4.8 Turbo	SUV	Allrad	Benzin	368	500	Jun 2010	May 2014	2025-06-01	2479
Peugeot	306	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Apr 1993	Jul 2001	2024-03-01	2480
Porsche	Cayenne	3.0 Diesel	SUV	Allrad	Diesel	176	239	Jun 2010	May 2018	2025-06-01	2481
Peugeot	306	1.6	Schrägheck	Frontantrieb	Benzin	65	89	May 1993	Oct 2000	2024-03-01	2482
Land Rover	Range rover iii	4.4 D 4X4	Geländewagen geschlossen	Allrad	Diesel	230	313	Jul 2010	Aug 2012	2024-03-01	2483
Peugeot	306	1.8	Schrägheck	Frontantrieb	Benzin	74	101	May 1993	May 2001	2024-03-01	2484
Peugeot	306	2.0 XSI	Schrägheck	Frontantrieb	Benzin	89	121	May 1993	May 2001	2024-03-01	2485
Peugeot	306	2.0 S16	Schrägheck	Frontantrieb	Benzin	112	152	May 1993	May 2001	2024-03-01	2486
Talbot	Samba	0.9	Schrägheck	Frontantrieb	Benzin	31	42	Jan 1981	Dec 1985	2024-03-01	2487
Talbot	Samba	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Jan 1981	Jun 1986	2024-03-01	2488
Talbot	Samba	1.4	Schrägheck	Frontantrieb	Benzin	53	72	Jan 1981	Jun 1986	2024-03-01	2489
Talbot	Samba	1.4	Cabriolet	Frontantrieb	Benzin	58	79	Jan 1981	Jun 1986	2024-03-01	2490
Talbot	Horizon	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1979	Sep 1984	2024-03-01	2491
Talbot	Horizon	1.3	Schrägheck	Frontantrieb	Benzin	40	54	Sep 1981	Jun 1986	2024-03-01	2492
Talbot	Horizon	1.3	Schrägheck	Frontantrieb	Benzin	43	58	Sep 1978	Sep 1984	2024-03-01	2493
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	120	163	Dec 2010	Jun 2019	2024-03-01	2494
Talbot	Horizon	1.4	Schrägheck	Frontantrieb	Benzin	51	69	Jul 1979	Jun 1986	2024-03-01	2495
Talbot	Horizon	1.4	Schrägheck	Frontantrieb	Benzin	61	83	Jul 1979	Jun 1986	2024-03-01	2496
Talbot	Horizon	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1982	Jun 1986	2024-03-01	2497
Talbot	Horizon	1.9 Diesel	Schrägheck	Frontantrieb	Diesel	47	64	Jul 1984	Jun 1986	2024-03-01	2498
Talbot	Horizon	1.9 Diesel	Schrägheck	Frontantrieb	Diesel	48	65	Jul 1982	Jun 1986	2024-03-01	2499
Talbot	1307-1510	Simca 1307 1.3	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1978	Aug 1981	2024-03-01	2500
Talbot	1307-1510	Simca 1308 1.4	Schrägheck	Frontantrieb	Benzin	55	75	Nov 1978	Aug 1980	2024-03-01	2501
Talbot	1307-1510	Simca 1308 1.4	Schrägheck	Frontantrieb	Benzin	63	86	Nov 1978	Aug 1981	2024-03-01	2502
Talbot	1307-1510	1510 1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1981	Jun 1982	2024-03-01	2503
Talbot	Solara	1.3	Stufenheck	Frontantrieb	Benzin	40	54	Feb 1980	Jul 1986	2024-03-01	2504
Talbot	Solara	1.6	Stufenheck	Frontantrieb	Benzin	51	69	Jul 1982	Apr 1984	2024-03-01	2505
Talbot	Solara	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Sep 1981	Oct 1984	2024-03-01	2506
Talbot	Solara	1.6	Stufenheck	Frontantrieb	Benzin	65	88	Feb 1980	Jun 1981	2024-03-01	2507
Talbot	Solara	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1981	Jul 1986	2024-03-01	2508
Talbot	Tagora	2.1	Stufenheck	Heckantrieb	Benzin	85	116	Jun 1980	Dec 1983	2024-03-01	2509
Talbot	Murena	2.1	Coupe	Heckantrieb	Benzin	85	116	Sep 1980	Jul 1984	2024-03-01	2510
Talbot	Rancho	1.4	Großraumlimousine	Frontantrieb	Benzin	59	80	Aug 1976	Jul 1983	2024-03-01	2511
Alfa Romeo	Alfasud	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1980	Sep 1984	2024-03-01	2512
Alfa Romeo	Alfasud	1.2	Schrägheck	Frontantrieb	Benzin	46	63	Jun 1972	Sep 1984	2024-03-01	2513
Alfa Romeo	Alfasud	1.2 TI	Schrägheck	Frontantrieb	Benzin	50	68	Nov 1973	Sep 1984	2024-03-01	2515
Alfa Romeo	Alfasud	1.3	Schrägheck	Frontantrieb	Benzin	50	68	May 1978	Apr 1980	2024-03-01	2516
Alfa Romeo	Alfasud	1.3 TI	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1977	Sep 1984	2024-03-01	2517
Alfa Romeo	Alfasud	1.3 Super	Schrägheck	Frontantrieb	Benzin	51	69	Jan 1979	Sep 1984	2024-03-01	2518
Alfa Romeo	Alfasud	1.3 Sc/ti Super	Schrägheck	Frontantrieb	Benzin	55	76	Sep 1977	Sep 1984	2024-03-01	2519
Alfa Romeo	Alfasud	1.3 TI	Schrägheck	Frontantrieb	Benzin	63	86	Jul 1979	Jun 1984	2024-03-01	2520
Alfa Romeo	Alfasud	1.5 TI	Schrägheck	Frontantrieb	Benzin	61	83	Jan 1979	Sep 1984	2024-03-01	2521
Alfa Romeo	Alfasud	1.5 TI	Schrägheck	Frontantrieb	Benzin	70	95	May 1980	Jun 1984	2024-03-01	2522
Alfa Romeo	Alfasud	1.5 TI Sprint	Schrägheck	Frontantrieb	Benzin	77	105	Jan 1983	Dec 1984	2024-03-01	2523
Alfa Romeo	Alfasud	1.2	Kombi	Frontantrieb	Benzin	46	63	Jan 1978	Dec 1981	2024-03-01	2524
Alfa Romeo	Alfasud	1.3	Kombi	Frontantrieb	Benzin	51	69	Mar 1980	Dec 1981	2024-03-01	2525
Alfa Romeo	33	1.5	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1983	Dec 1986	2024-03-01	2526
Alfa Romeo	33	1.5 4X4	Schrägheck	Allrad	Benzin	75	102	Jul 1986	Dec 1989	2024-03-01	2527
Alfa Romeo	33	1.5	Kombi	Frontantrieb	Benzin	66	90	Sep 1984	Dec 1986	2024-03-01	2528
Alfa Romeo	33	1.5	Kombi	Frontantrieb	Benzin	75	102	Dec 1986	Dec 1989	2024-03-01	2529
Alfa Romeo	33	1.5	Kombi	Frontantrieb	Benzin	77	105	Dec 1986	Dec 1989	2024-03-01	2530
Alfa Romeo	33	1.7 I.e.	Kombi	Frontantrieb	Benzin	77	105	Sep 1988	Dec 1989	2024-03-01	2531
Alfa Romeo	6	2.5 I.e.	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1983	Dec 1986	2024-03-01	2532
Alfa Romeo	6	2.5 I.e.	Stufenheck	Heckantrieb	Benzin	116	158	Aug 1979	Jun 1984	2024-03-01	2533
Land Rover	Range rover iii	5.0 4X4	Geländewagen geschlossen	Allrad	Benzin	276	375	Sep 2009	Aug 2012	2024-03-01	2534
Alfa Romeo	33	1.7 16V 4X4	Schrägheck	Allrad	Benzin	95	129	Jan 1990	Sep 1994	2024-03-01	2535
Alfa Romeo	33	1.7 16V 4X4	Schrägheck	Allrad	Benzin	97	132	Jan 1990	Sep 1994	2024-03-01	2536
Alfa Romeo	33	1.7 I.e. 4X4	Kombi	Allrad	Benzin	79	107	Jan 1990	Mar 1992	2024-03-01	2537
Audi	A7 sportback	3.0 TDI	Schrägheck	Frontantrieb	Diesel	150	204	Nov 2010	Mar 2015	2024-03-01	2538
Alfa Romeo	33	1.7 16V 4X4	Kombi	Allrad	Benzin	95	129	Jan 1990	Sep 1994	2024-03-01	2539
Fiat	500	0.5	Stufenheck	Heckantrieb	Benzin	11	15	Jun 1957	May 1961	2024-03-01	2540
Fiat	500	0.5	Stufenheck	Heckantrieb	Benzin	13	18	Jan 1965	Dec 1975	2024-03-01	2541
Fiat	500	0.5	Kombi	Heckantrieb	Benzin	11	15	Jan 1960	Dec 1966	2024-03-01	2542
Fiat	127	0.9	Schrägheck	Frontantrieb	Benzin	29	40	Jun 1971	May 1983	2024-03-01	2543
Fiat	127	0.9	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1971	Dec 1984	2024-03-01	2544
Fiat	127	1	Schrägheck	Frontantrieb	Benzin	37	50	Apr 1977	Dec 1986	2024-03-01	2545
Fiat	127	1.0 Sport	Schrägheck	Frontantrieb	Benzin	51	70	Jul 1978	Feb 1982	2024-03-01	2546
Fiat	127	1.3 Sport	Schrägheck	Frontantrieb	Benzin	55	75	Dec 1981	May 1983	2024-03-01	2547
Fiat	127	1.3 Diesel	Schrägheck	Frontantrieb	Diesel	33	45	Apr 1981	Dec 1986	2024-03-01	2548
Fiat	127	1.3 D	Kombi	Frontantrieb	Diesel	33	45	Jun 1981	Dec 1986	2024-03-01	2549
Fiat	Panda	750	Schrägheck	Frontantrieb	Benzin	25	34	Jan 1986	Oct 2003	2024-03-01	2550
Fiat	Panda	800	Schrägheck	Frontantrieb	Benzin	25	34	Feb 1981	Dec 1985	2024-03-01	2551
Fiat	Panda	900	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1980	Jun 1994	2024-03-01	2552
Fiat	Panda	950 4X4	Schrägheck	Allrad	Benzin	35	48	Sep 1983	Dec 1986	2024-03-01	2553
Fiat	Panda	1000 4X4	Schrägheck	Allrad	Benzin	32	44	Jan 1986	Jul 1989	2024-03-01	2554
Fiat	Panda	1000 4X4	Schrägheck	Allrad	Benzin	37	50	Jan 1986	Dec 1992	2024-03-01	2555
Fiat	Panda	1000	Schrägheck	Frontantrieb	Benzin	32	44	Jan 1986	Apr 1992	2024-03-01	2556
Hyundai	Ix20	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Nov 2010	Jul 2019	2024-03-01	2557
Fiat	Panda	900	Schrägheck	Frontantrieb	Benzin	29	40	Apr 1992	Dec 1996	2024-03-01	2558
Fiat	Panda	1000 4X4	Schrägheck	Allrad	Benzin	33	45	May 1986	Dec 1994	2024-03-01	2559
Fiat	Panda	1000 I.e. CAT	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1987	Aug 1998	2024-03-01	2560
Fiat	Panda	1100 Trekking 4X4	Schrägheck	Allrad	Benzin	37	50	Oct 1991	Jul 2004	2024-03-01	2561
Fiat	Panda	1100	Schrägheck	Frontantrieb	Benzin	37	50	May 1991	Dec 1999	2024-03-01	2562
Fiat	Panda	750	Kasten/Schrägheck	Frontantrieb	Benzin	25	34	Jan 1986	Jul 1992	2024-03-01	2563
Fiat	Panda	1000	Kasten/Schrägheck	Frontantrieb	Benzin	32	44	Jan 1986	Feb 1992	2024-03-01	2564
Fiat	126	600	Schrägheck	Heckantrieb	Benzin	17	23	Sep 1972	Jun 1977	2024-03-01	2565
Fiat	126	650	Schrägheck	Heckantrieb	Benzin	17	23	Jul 1977	Sep 1987	2024-03-01	2566
Fiat	126	700	Schrägheck	Heckantrieb	Benzin	19	26	Sep 1987	Jun 1996	2024-03-01	2567
Fiat	124	1500 Sport	Cabriolet	Heckantrieb	Benzin	66	90	Jan 1966	Dec 1972	2024-03-01	2568


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **19 个 DIMENSION_GROUP**，新增 **28 条 READY 映射**。Peugeot 106 Le Mans、Porsche Cayenne Turbo/Diesel 等来源明确给出不含后视镜宽度。([汽车目录][1])
* Audi A7 使用官方技术数据，Touran、ix20 使用官方规格手册；Grand C-MAX 使用与输入动力版本对应的直接规格页。
* Samba、1307/1308、1510、Solara、Murena、Rancho 已按不同物理车身分别建组，未因三维偶然相同而合并不同 BodyStyle。([汽车目录][2])
* 已记录 Peugeot J5、306、Talbot Horizon、Tagora 的具体阻塞原因，没有创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射：**28/100**
* PENDING／未闭合：**72/100**

  * 本轮已写明具体 blocker：23
  * 尚待下一轮建立映射：49
* 已确认尺寸组：**19**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2468	2468	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	HIGH	Le Mans为三门专属外廓。	READY
2469	2469	Hatchback	106 I				LOW	同期1.6 88 PS存在3门XS与5门XT，尚未确认该Ktype的门数覆盖。	PENDING: 门数分支未确认
2470	2470	Van	J5 I				LOW	Bus存在多轴距与多车顶外廓，输入未给出物理分支。	PENDING: 轴距和车顶分支未确认
2471	2471	Pickup	J5 I				LOW	Pritsche/Fahrgestell存在多轴距及驾驶室/底盘外廓。	PENDING: 底盘分支未确认
2472	2472	Van	J5 I facelift				LOW	改款Bus存在多轴距与多车顶外廓。	PENDING: 轴距和车顶分支未确认
2473	2473	Van	J5 I				LOW	Bus存在多轴距与多车顶外廓，输入未给出物理分支。	PENDING: 轴距和车顶分支未确认
2474	2474	Van	J5 I facelift				LOW	改款Bus存在多轴距与多车顶外廓。	PENDING: 轴距和车顶分支未确认
2475	2475	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2476	2476	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2477	2477	MPV	Touran I (GP2)	1T3	5	EU-VW-TOURAN-I-GP2-MPV-01	HIGH		READY
2478	2478	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2479	2479	SUV	Cayenne II	92A	5	EU-PORSCHE-CAYENNE-II-SUV-TURBO-01	HIGH		READY
2480	2480	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2481	2481	SUV	Cayenne II	92A	5	EU-PORSCHE-CAYENNE-II-SUV-DIESEL-01	HIGH		READY
2482	2482	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2483	2483	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	HIGH		READY
2484	2484	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2485	2485	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2486	2486	Hatchback	306 I				LOW	生产区间覆盖3门/5门及改款前后，Ktype物理分支未确认。	PENDING: 门数和改款分支未确认
2487	2487	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2488	2488	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2489	2489	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2490	2490	Convertible	Samba	51E	2	EU-TALBOT-SAMBA-CONVERTIBLE-01	HIGH		READY
2491	2491	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2492	2492	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2493	2493	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2494	2494	MPV	Grand C-MAX II		5	EU-FORD-GRAND-C-MAX-II-MPV-01	HIGH		READY
2495	2495	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2496	2496	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2497	2497	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，需按功率与trim核定。	PENDING: trim外廓未确认
2498	2498	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2499	2499	Hatchback	Horizon		5		LOW	基础车身与SX外廓存在长度差异，输入未给出trim边界。	PENDING: trim外廓未确认
2500	2500	Hatchback	Simca 1307		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1307。	READY
2501	2501	Hatchback	Simca 1308		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1308。	READY
2502	2502	Hatchback	Simca 1308		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1308。	READY
2503	2503	Hatchback	Talbot 1510		5	EU-TALBOT-1510-HATCHBACK-01	HIGH	VariantName明确为1510。	READY
2504	2504	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2505	2505	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2506	2506	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2507	2507	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2508	2508	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2509	2509	Sedan	Tagora		4		LOW	2.2/116 PS来源的长度与高度存在冲突，尚未闭合同一配置三维。	PENDING: 尺寸来源冲突未解决
2510	2510	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	MEDIUM	输入2.1/116 PS按同期2.2-litre量产分支映射。	READY
2511	2511	MPV	Rancho		3	EU-TALBOT-RANCHO-MPV-01	HIGH		READY
2534	2534	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	HIGH		READY
2538	2538	Hatchback	A7 Sportback I (C7)	4G8	5	EU-AUDI-A7-C7-SPORTBACK-01	HIGH		READY
2540	2540	Sedan	Nuova 500 N	110	2	EU-FIAT-500-110-SEDAN-01	HIGH		READY
2542	2542	Wagon	500 Giardiniera	120	3	EU-FIAT-500-120-GIARDINIERA-WAGON-01	HIGH		READY
2550	2550	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH	1986年起改款外廓。	READY
2551	2551	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	HIGH	1986年前外廓。	READY
2557	2557	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-01	HIGH	输入BodyStyle为Schrägheck，车型资料归为小型MPV。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	3564	1607	1360	Automobile-Catalog Peugeot 106 Le Mans	https://www.automobile-catalog.com/car/1994/2608535/peugeot_106_le_mans.html
EU-VW-TOURAN-I-GP2-MPV-01	4397	1794	1634	Volkswagen The New Touran official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2010-UK.pdf
EU-PORSCHE-CAYENNE-II-SUV-TURBO-01	4846	1939	1702	Automobile-Catalog Porsche Cayenne Turbo	https://www.automobile-catalog.com/car/2010/2869655/porsche_cayenne_turbo.html
EU-PORSCHE-CAYENNE-II-SUV-DIESEL-01	4846	1939	1705	Automobile-Catalog Porsche Cayenne Diesel	https://www.automobile-catalog.com/car/2011/2869625/porsche_cayenne_diesel.html
EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	4972	1956	1865	Automobile-Catalog Range Rover 4.4 TDV8 Vogue;Automobile-Catalog Range Rover 5.0 V8 Vogue	https://www.automobile-catalog.com/car/2011/1404485/range_rover_4_4_tdv8_vouge.html;https://www.automobile-catalog.com/car/2010/1404500/range_rover_5_0_v8_vouge.html
EU-TALBOT-SAMBA-HATCHBACK-01	3506	1528	1362	Automobile-Catalog Talbot Samba 1.4 GLS	https://www.automobile-catalog.com/car/1983/55535/talbot_samba_1_4_gls.html
EU-TALBOT-SAMBA-CONVERTIBLE-01	3506	1528	1362	Automobile-Catalog Talbot Samba Cabriolet 1.4	https://www.automobile-catalog.com/car/1983/3118040/talbot_samba_1_4.html
EU-FORD-GRAND-C-MAX-II-MPV-01	4520	1828	1684	Auto-Data Ford Grand C-MAX II 2.0 TDCi 163	https://www.auto-data.net/en/ford-grand-c-max-ii-2.0-duratorq-tdci-163hp-dpf-powershift-19881
EU-TALBOT-1307-1308-HATCHBACK-01	4245	1680	1400	Automobile-Catalog Simca 1307 S	https://www.automobile-catalog.com/car/1978/28220/simca_1307_s.html
EU-TALBOT-1510-HATCHBACK-01	4318	1680	1390	Automobile-Catalog Talbot 1510 1.6 GLS	https://www.automobile-catalog.com/car/1980/3112475/talbot_1510_1_6_gls.html
EU-TALBOT-SOLARA-SEDAN-01	4393	1680	1390	Automobile-Catalog Talbot Solara 1.6 GLS	https://www.automobile-catalog.com/car/1982/3113480/talbot_solara_1_6_gls.html
EU-TALBOT-MURENA-COUPE-01	4070	1752	1220	Automobile-Catalog Talbot-Matra Murena 2.2-litre	https://www.automobile-catalog.com/car/1981/1458620/talbot_matra_murena_2_2-litre.html
EU-TALBOT-RANCHO-MPV-01	4315	1665	1735	Automobile-Catalog Talbot-Matra Rancho	https://www.automobile-catalog.com/car/1983/1458710/talbot_matra_rancho.html
EU-AUDI-A7-C7-SPORTBACK-01	4969	1911	1420	Audi A7 Sportback official technical data	https://www.ausmotive.com/downloads/Audi/A7-Sportback-tech-data-Mar2011.pdf
EU-FIAT-500-110-SEDAN-01	2970	1320	1325	Automobile-Catalog Fiat 500 Economica	https://www.automobile-catalog.com/car/1958/708695/fiat_500_economica_standard.html
EU-FIAT-500-120-GIARDINIERA-WAGON-01	3185	1323	1354	Automobile-Catalog Fiat 500 Giardiniera	https://www.automobile-catalog.com/car/1960/708800/fiat_500_giardiniera.html
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420	Automobile-Catalog Fiat Panda 750 L	https://www.automobile-catalog.com/car/1986/715055/fiat_panda_750_l_5-speed.html
EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	3380	1460	1445	Automobile-Catalog Fiat Panda 45 Super	https://www.automobile-catalog.com/car/1986/28925/fiat_panda_45_super_5-speed.html
EU-HYUNDAI-IX20-JC-MPV-01	4100	1765	1600	Hyundai ix20 official brochure (archived)	https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-ix20-2012-UK.pdf
```

## 下一步优先处理

1. 聚类解决 Peugeot 306 的 **3门/5门及改款前后**分支，并一次性关联 2475、2476、2478、2480、2482、2484、2485、2486。
2. 核定 Peugeot J5 Bus 与 Pritsche/Fahrgestell 的 **轴距、车顶和底盘分支**。
3. 按功率和年份消除 Talbot Horizon 的基础车身／SX 长度差异，并解决 Tagora 2.2 三维来源冲突。
4. 批量处理 Alfa Romeo Alfasud／33，以及 Fiat 127、Panda、126 的代际和改款外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1994/2608535/peugeot_106_le_mans.html?utm_source=chatgpt.com "1994 Peugeot 106 Le Mans Specs Review (69 kW / 94 PS / ..."
[2]: https://www.automobile-catalog.com/car/1983/55535/talbot_samba_1_4_gls.html?utm_source=chatgpt.com "1983 Talbot Samba 1.4 GLS 80hp Specs Review (59 kW ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 批量闭合 Alfa Romeo 33 Tipo 905/907 的前驱、四驱、两厢与旅行车外廓，并将 Alfa 6 的改款前后长度差异拆成两个尺寸组。([汽车目录][1])
* Fiat Panda 复用既有改款前/后前驱组，首次新增改款后普通四驱与 Trekking 加高四驱组；跨 1986 年改款的 Ktype 2552 已拆成两个稳定派生行。([汽车数据][2])
* 新增 Fiat 126 BIS 与 Fiat 124 Sport Spider 首代尺寸组。([汽车目录][3])

## 当前批次进度

* READY Ktype：**53/100**
* READY 映射行：**55**
* PENDING Ktype：**47/100**
* 已确认尺寸组：**30**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2526	2526	Hatchback	Alfa Romeo 33 I	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	HIGH		READY
2527	2527	Hatchback	Alfa Romeo 33 I	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	HIGH	四驱车身高度独立。	READY
2528	2528	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2529	2529	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2530	2530	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2531	2531	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2532	2532	Sedan	Alfa 6 I facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	HIGH		READY
2533_prefl	2533	Sedan	Alfa 6 I pre-facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-PREFL-01	HIGH	生产区间覆盖第一系列外廓。	READY
2533_facelift	2533	Sedan	Alfa 6 I facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	HIGH	生产区间覆盖1983年改款后外廓。	READY
2535	2535	Hatchback	Alfa Romeo 33 II	907A	5	EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	HIGH		READY
2536	2536	Hatchback	Alfa Romeo 33 II	907A	5	EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	HIGH		READY
2537	2537	Wagon	Alfa Romeo 33 II	907B	5	EU-ALFA-ROMEO-33-907-WAGON-4X4-01	HIGH		READY
2539	2539	Wagon	Alfa Romeo 33 II	907B	5	EU-ALFA-ROMEO-33-907-WAGON-4X4-01	HIGH		READY
2552_prefl	2552	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	HIGH	生产区间覆盖1986年改款前外廓。	READY
2552_facelift	2552	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH	生产区间覆盖1986年改款后外廓。	READY
2554	2554	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2555	2555	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2556	2556	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2558	2558	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2559	2559	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2560	2560	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2561	2561	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	HIGH	Trekking加高外廓。	READY
2562	2562	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2563	2563	Van	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	MEDIUM	封闭货运版复用同代三门外部车身。	READY
2564	2564	Van	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	MEDIUM	封闭货运版复用同代三门外部车身。	READY
2567	2567	Hatchback	Fiat 126 BIS		3	EU-FIAT-126-BIS-HATCHBACK-01	HIGH	704发动机对应带后尾门的BIS车身。	READY
2568	2568	Convertible	124 Sport Spider I		2	EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	MEDIUM	按90 PS首代124 Sport Spider外廓映射。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	4015	1612	1303	Automobile-Catalog Alfa Romeo 33 1.5	https://www.automobile-catalog.com/car/1983/48725/alfa_romeo_33_1_5.html
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	4015	1612	1345	Automobile-Catalog Alfa Romeo 33 1.5 4x4	https://www.automobile-catalog.com/car/1987/215045/alfa_romeo_33_1_5_4x4.html
EU-ALFA-ROMEO-33-905-WAGON-FWD-01	4142	1612	1345	Automobile-Catalog Alfa Romeo 33 1.5 Giardinetta	https://www.automobile-catalog.com/car/1986/215075/alfa_romeo_33_1_5_giardinietta.html
EU-ALFA-ROMEO-ALFA-6-119-SEDAN-PREFL-01	4760	1685	1395	Automobile-Catalog Alfa Romeo Alfa 6	https://www.automobile-catalog.com/car/1982/24500/alfa_romeo_alfa_6.html
EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	4679	1685	1395	Automobile-Catalog Alfa Romeo Alfa 6 2.5 Iniezione Quadrifoglio Oro	https://www.automobile-catalog.com/car/1985/49775/alfa_romeo_alfa_6_2_5_iniezione_quadrifoglio_oro.html
EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	4075	1614	1375	Automobile-Catalog Alfa Romeo 33 16V Permanent 4 Quadrifoglio Verde	https://www.automobile-catalog.com/car/1991/216875/alfa_romeo_33_1_7_ie_16v_permanent_4_quadrifoglio_verde_s.html
EU-ALFA-ROMEO-33-907-WAGON-4X4-01	4200	1614	1375	Automobile-Catalog Alfa Romeo 33 1.7 ie Sport Wagon 4x4	https://www.automobile-catalog.com/car/1992/217055/alfa_romeo_33_1_7_ie_sport_wagon_4x4.html
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468	Automobile-Catalog Fiat Panda 1000 4x4	https://www.automobile-catalog.com/car/1991/31340/fiat_panda_1000_4x4.html
EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	3408	1500	1485	Auto Bild Klassik Fiat Panda 4x4 Trekking	https://www.autobild.de/klassik/artikel/fiat-panda-4x4-trekking-1300570.html
EU-FIAT-126-BIS-HATCHBACK-01	3107	1377	1343	Automobile-Catalog Fiat 126 BIS	https://www.automobile-catalog.com/car/1987/717935/fiat_126_bis.html
EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	3971	1613	1250	Automobile-Catalog Fiat 124 Sport Spider 1400	https://www.automobile-catalog.com/car/1968/709790/fiat_124_sport_spider_1400.html
```

## 下一步优先处理

1. 批量解决 Alfa Romeo Alfasud 的早期四门、TI 双门/三门、后期掀背及 Giardinetta 分支。
2. 闭合 Fiat 127 三个系列、Panorama 旅行车，以及 Fiat 126 600/650 的保险杠外廓差异。
3. 继续处理 Peugeot 306、J5 和 Talbot Horizon 的多物理分支 blocker。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/48725/alfa_romeo_33_1_5.html?utm_source=chatgpt.com "1983 Alfa Romeo 33 1.5 Specs Review (62.5 kW / 85 PS / 84 hp) (since mid-year 1983 for Europe Australia )"
[2]: https://www.auto-data.net/en/fiat-panda-zaf-141-generation-1583?utm_source=chatgpt.com "Fiat Panda (ZAF 141) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1987/717935/fiat_126_bis.html?utm_source=chatgpt.com "1987 Fiat 126 Bis (man. 4) (model since mid-year 1987 for ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **16 条 READY 映射**：闭合 Fiat 127 的第二系列、第三系列、Unificata、Sport、Diesel 与 Panorama 物理分支；相同三门外廓直接复用同一尺寸组。([汽车目录][1])
* 闭合 Fiat Panda 改款前四驱、Fiat 126 早期标准车身及 650 Economic、Personal、后期改款分支；Fiat 500 Ktype 2541 直接复用已确认尺寸组。([汽车目录][2])
* 本轮首次创建 **12 个 DIMENSION_GROUP**；既有尺寸组未重复输出。

## 当前批次进度

* READY Ktype：**62/100**
* PENDING Ktype：**38/100**
* READY 映射行：**71**
* 已确认尺寸组：**42**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2541	2541	Sedan	Nuova 500 F/L/R	110	2	EU-FIAT-500-110-SEDAN-01	HIGH		READY
2545_series2_3dr	2545	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	MEDIUM	第二系列三门物理外廓。	READY
2545_series3_3dr	2545	Hatchback	127 Series III		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	MEDIUM	第三系列三门物理外廓。	READY
2545_series3_5dr	2545	Hatchback	127 Series III		5	EU-FIAT-127-SERIES-III-HATCHBACK-5D-01	MEDIUM	第三系列五门物理外廓。	READY
2545_unificata_3dr	2545	Hatchback	127 Unificata		3	EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	MEDIUM	后期Unificata三门物理外廓。	READY
2546	2546	Hatchback	127 Series II Sport		3	EU-FIAT-127-SERIES-II-SPORT-HATCHBACK-3D-01	HIGH		READY
2547	2547	Hatchback	127 Series III Sport		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	HIGH		READY
2548_early	2548	Hatchback	127 Diesel early		3	EU-FIAT-127-DIESEL-EARLY-HATCHBACK-3D-01	MEDIUM	早期柴油三门外廓。	READY
2548_facelift	2548	Hatchback	127 Unificata Diesel		3	EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	MEDIUM	后期柴油三门外廓。	READY
2549	2549	Wagon	127 Panorama		3	EU-FIAT-127-PANORAMA-WAGON-01	HIGH		READY
2553	2553	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-PREFL-4X4-01	HIGH		READY
2565	2565	Hatchback	Fiat 126 I		2	EU-FIAT-126-EARLY-STANDARD-01	HIGH		READY
2566_standard	2566	Hatchback	Fiat 126 650 standard		2	EU-FIAT-126-EARLY-STANDARD-01	MEDIUM	标准车身外廓。	READY
2566_economic	2566	Hatchback	Fiat 126 650 Economic		2	EU-FIAT-126-650-ECONOMIC-01	MEDIUM	Economic车身外廓。	READY
2566_personal	2566	Hatchback	Fiat 126 650 Personal		2	EU-FIAT-126-650-PERSONAL-01	MEDIUM	Personal车身外廓。	READY
2566_facelift	2566	Hatchback	Fiat 126 650 facelift		2	EU-FIAT-126-650-FACELIFT-01	MEDIUM	后期改款车身外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-I-PREFL-4X4-01	3390	1485	1470	Automobile-Catalog Fiat Panda 4x4	https://www.automobile-catalog.com/car/1984/49220/fiat_panda_4x4.html
EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	3645	1527	1380	Automobile-Catalog Fiat 127 900 CL 3P	https://www.automobile-catalog.com/car/1979/2067110/fiat_127_900_cl_3p_low_compr.html
EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	3711	1552	1370	Automobile-Catalog Fiat 127 1050 Super 3-door	https://www.automobile-catalog.com/car/1982/711530/fiat_127_super.html
EU-FIAT-127-SERIES-III-HATCHBACK-5D-01	3711	1552	1370	Automobile-Catalog Fiat 127 1050 Super 5 Porte	https://www.automobile-catalog.com/car/1982/711560/fiat_127_super_5_porte.html
EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	3745	1545	1405	Automobile-Catalog Fiat 127 1050	https://www.automobile-catalog.com/car/1984/711590/fiat_127_1050.html
EU-FIAT-127-SERIES-II-SPORT-HATCHBACK-3D-01	3645	1536	1380	Automobile-Catalog Fiat 127 Sport	https://www.automobile-catalog.com/car/1980/711425/fiat_127_sport.html
EU-FIAT-127-DIESEL-EARLY-HATCHBACK-3D-01	3745	1545	1410	Automobile-Catalog Fiat 127 D	https://www.automobile-catalog.com/car/1981/711500/fiat_127_d.html
EU-FIAT-127-PANORAMA-WAGON-01	3920	1545	1425	Automobile-Catalog Fiat 127 Panorama D	https://www.automobile-catalog.com/car/1981/711485/fiat_127_panorama_d.html
EU-FIAT-126-EARLY-STANDARD-01	3054	1377	1335	Automobile-Catalog Fiat 126	https://www.automobile-catalog.com/car/1972/711065/fiat_126.html
EU-FIAT-126-650-ECONOMIC-01	3070	1377	1335	Automobile-Catalog Fiat 126 Economic	https://www.automobile-catalog.com/car/1981/711095/fiat_126.html
EU-FIAT-126-650-PERSONAL-01	3129	1382	1335	Automobile-Catalog Fiat 126 Personal	https://www.automobile-catalog.com/car/1977/711080/fiat_126_personal.html
EU-FIAT-126-650-FACELIFT-01	3109	1377	1335	Automobile-Catalog Fiat 126 facelift	https://www.automobile-catalog.com/car/1985/2066855/fiat_126.html
```

## 下一步优先处理

1. 闭合 Fiat 127 Ktype 2543、2544 的早期三门、五门及跨系列边界。
2. 批量处理 Alfa Romeo Alfasud 的四门、三门 TI、五门改款和 Giardinetta 分支。
3. 继续消除 Peugeot 306、J5、Talbot Horizon 与 Tagora 的剩余阻塞。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/711455/fiat_127_c_5_porte.html?utm_source=chatgpt.com "1980 Fiat 127 900 CL 5 Porte Specs Review (33 kW / 45 PS / 44 hp) (since mid-year 1980 for Europe )"
[2]: https://www.automobile-catalog.com/car/1984/49220/fiat_panda_4x4.html?utm_source=chatgpt.com "1984 Fiat Panda 4x4 Specs Review (35.5 kW / 48 PS / 48 hp) (for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* 闭合 Alfa Romeo Alfasud 的 **8 个 Ktype、10 条映射**。Series III TI 按早期双门快背与后期三门掀背拆分；Ktype 2522 直接复用与 2520 相同的两个物理外廓组，不因发动机差异重复建组。([汽车目录][1])
* Alfasud Giardinetta 按 `904A` 与 `904B2` 两种已确认外廓分别建组；Sprint 105 PS 作为独立三门 Coupe 外廓建组。([汽车目录][2])

## 2) 当前批次进度

* READY Ktype：**70/100**
* PENDING Ktype：**30/100**
* READY 映射行：**81**
* 已确认尺寸组：**50**
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2516	2516	Sedan	Alfasud II	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH		READY
2517	2517	Sedan	Alfasud I TI	901	2	EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	HIGH		READY
2520_2dr	2520	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	改款初期双门快背车身。	READY
2520_3dr	2520	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	后期三门掀背车身。	READY
2521	2521	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	HIGH		READY
2522_2dr	2522	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	改款初期双门快背车身。	READY
2522_3dr	2522	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	后期三门掀背车身。	READY
2523	2523	Coupe	Sprint II	902A	3	EU-ALFA-ROMEO-SPRINT-902A-COUPE-QV-01	HIGH	输入TI Sprint对应105 PS Quadrifoglio Verde外廓。	READY
2524	2524	Wagon	Alfasud Giardinetta	904A	3	EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	HIGH		READY
2525	2525	Wagon	Alfasud Giardinetta	904B2	3	EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	HIGH		READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	3935	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Super 1.3	https://www.automobile-catalog.com/car/1977/35855/alfa_romeo_alfasud_super_1_3.html
EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	3926	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3	https://www.automobile-catalog.com/car/1977/143090/alfa_romeo_alfasud_ti_1_3.html
EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	3995	1616	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3	https://www.automobile-catalog.com/car/1980/143180/alfa_romeo_alfasud_ti_1_3.html
EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	3995	1616	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3 3-Porte	https://www.automobile-catalog.com/car/1981/143240/alfa_romeo_alfasud_ti_1_3_3-porte.html
EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	3935	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.5	https://www.automobile-catalog.com/car/1978/35900/alfa_romeo_alfasud_ti_1_5.html
EU-ALFA-ROMEO-SPRINT-902A-COUPE-QV-01	4024	1620	1295	Automobile-Catalog Alfa Romeo Sprint 1.5 Quadrifoglio Verde	https://www.automobile-catalog.com/car/1983/41660/alfa_romeo_sprint_1_5_quadrifoglio_verde.html
EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	3935	1590	1370	Auto-Data Alfa Romeo Alfasud Giardinetta 1.2	https://www.auto-data.net/en/alfa-romeo-alfasud-giardinetta-904-1.2-63hp-1343
EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	3975	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Giardinetta 1.3	https://www.automobile-catalog.com/car/1979/143135/alfa_romeo_alfasud_giardinietta_1_3.html
```

## 5) 下一步优先处理

1. 处理剩余 Alfasud Ktype 2512、2513、2515、2518、2519 的早期四门、TI 双门及跨系列边界。
2. 闭合 Fiat 127 Ktype 2543、2544 的第一系列、第二系列及三门/五门分支。
3. 继续解决 Peugeot 306、J5、Talbot Horizon 与 Tagora 的剩余物理外廓阻塞。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/143090/alfa_romeo_alfasud_ti_1_3.html?utm_source=chatgpt.com "1977 Alfa Romeo Alfasud Ti 1.3 Specs Review (55 kW / 75 PS / 74 hp) (up to late-year 1977 for Europe )"
[2]: https://www.automobile-catalog.com/car/1983/41660/alfa_romeo_sprint_1_5_quadrifoglio_verde.html?utm_source=chatgpt.com "1983 Alfa Romeo Sprint 1.5 Quadrifoglio Verde Specs Review (77 kW / 105 PS / 103 hp) (since mid-year 1983 for Europe Australia )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1) 更新点

* 闭合 Ktype `2513`：按 Alfasud 第一系列四门、第二系列四门、第三系列四门及第三系列三门掀背拆分，其中第二系列直接复用既有尺寸组。([汽车目录][1])
* 闭合 Ktype `2543`：40 PS 低压缩版确认覆盖 Fiat 127 第一系列三门和第二系列三门，第二系列直接复用已有组。([汽车目录][2])
* 闭合 Ktype `2544`：拆分第一系列标准三门、第一系列 Special 三门、第二系列三门、第二系列五门和第三系列三门；既有组不重复输出。([汽车目录][3])

## 2) 当前批次进度

* READY Ktype：**73/100**
* PENDING Ktype：**27/100**
* READY 映射行：**92**
* 已确认尺寸组：**56**
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2513_series1_4dr	2513	Sedan	Alfasud I	901	4	EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	HIGH	第一系列四门快背车身。	READY
2513_series2_4dr	2513	Sedan	Alfasud II	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH	第二系列四门快背车身。	READY
2513_series3_4dr	2513	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	HIGH	第三系列四门快背车身。	READY
2513_series3_3dr	2513	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	HIGH	第三系列三门掀背车身。	READY
2543_series1_3dr	2543	Hatchback	127 Series I		3	EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	HIGH	第一系列低压缩三门外廓。	READY
2543_series2_3dr	2543	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	HIGH	第二系列低压缩三门外廓。	READY
2544_series1_3dr	2544	Hatchback	127 Series I		3	EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	HIGH	第一系列标准三门外廓。	READY
2544_series1_special_3dr	2544	Hatchback	127 Series I Special		3	EU-FIAT-127-SERIES-I-SPECIAL-HATCHBACK-3D-01	HIGH	Special保险杠造成长度差异。	READY
2544_series2_3dr	2544	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	HIGH	第二系列三门外廓。	READY
2544_series2_5dr	2544	Hatchback	127 Series II		5	EU-FIAT-127-SERIES-II-HATCHBACK-5D-01	HIGH	第二系列五门外廓。	READY
2544_series3_3dr	2544	Hatchback	127 Series III		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	HIGH	第三系列三门外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	3890	1590	1370	Automobile-Catalog Alfa Romeo Alfasud	https://www.automobile-catalog.com/car/1972/27740/alfa_romeo_alfasud.html
EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.2 4M	https://www.automobile-catalog.com/car/1980/44450/alfa_romeo_alfasud_1_2.html
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.2 3-Porte	https://www.automobile-catalog.com/car/1981/143195/alfa_romeo_alfasud_1_2_3-porte.html
EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	3595	1527	1380	Automobile-Catalog Fiat 127 Tre Porte	https://www.automobile-catalog.com/car/1972/711125/fiat_127_tre_porte.html
EU-FIAT-127-SERIES-I-SPECIAL-HATCHBACK-3D-01	3635	1527	1380	Automobile-Catalog Fiat 127 Special 3 Porte 45PS	https://www.automobile-catalog.com/car/1974/711320/fiat_127_special_3_porte.html
EU-FIAT-127-SERIES-II-HATCHBACK-5D-01	3645	1527	1380	Automobile-Catalog Fiat 127 900 CL 5 Porte	https://www.automobile-catalog.com/car/1981/711455/fiat_127_c_5_porte.html
```

## 5) 下一步优先处理

1. 闭合剩余 Alfasud Ktype `2512`、`2515`、`2518`、`2519`，优先复用本轮及既有 Alfasud 尺寸组。
2. 解决 Peugeot 306 的三门、五门及改款前后分支。
3. 处理 Talbot Horizon 基础车身／SX 外廓和 Tagora 尺寸冲突。
4. 最后集中处理 Peugeot J5 的轴距、车顶及底盘分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/27740/alfa_romeo_alfasud.html?utm_source=chatgpt.com "1972 Alfa Romeo Alfasud Specs Review (46.5 kW / 63 PS / 62 hp) (since mid-year 1972 for Europe )"
[2]: https://www.automobile-catalog.com/car/1976/711275/fiat_127_tre_porte_low_compr_.html?utm_source=chatgpt.com "1976 Fiat 127 Tre Porte (low compr.) Specs Review (29.5 kW / 40 PS / 40 hp) (for Europe Germany)"
[3]: https://www.automobile-catalog.com/car/1972/711125/fiat_127_tre_porte.html?utm_source=chatgpt.com "1972 Fiat 127 Tre Porte Specs Review (34.57 kW / 47 PS / 46 hp) (since March 1972 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1) 更新点

* 闭合剩余 4 个 Alfa Romeo Alfasud Ktype。Series III 普通车身拆分为四门快背、三门掀背和五门掀背；TI 分支继续区分双门快背与三门掀背。([汽车目录][1])
* 本轮仅首次创建 **Alfasud Series III 五门掀背**尺寸组；其余映射全部复用已闭合尺寸组。五门组尺寸为 `3995 × 1590 × 1370 mm`，宽度为不含后视镜口径。([汽车目录][2])

## 2) 当前批次进度

* READY Ktype：**77/100**
* PENDING Ktype：**23/100**
* READY 映射行：**109**
* 已确认尺寸组：**57**
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2512_series3_4dr	2512	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2512_series3_3dr	2512	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2512_series3_5dr	2512	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2515_series1_2dr	2515	Sedan	Alfasud I TI	901	2	EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	HIGH	第一系列TI双门快背外廓。	READY
2515_series2_2dr	2515	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	HIGH	第二系列TI双门快背外廓。	READY
2515_series3_2dr	2515	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	第三系列初期TI双门快背外廓。	READY
2515_series3_3dr	2515	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	第三系列后期TI三门掀背外廓。	READY
2518_series2_4dr	2518	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH	第二系列Super四门快背外廓。	READY
2518_series3_4dr	2518	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2518_series3_3dr	2518	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2518_series3_5dr	2518	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2519_series2_super_4dr	2519	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	MEDIUM	Super四门快背外廓。	READY
2519_series2_ti_2dr	2519	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	MEDIUM	TI双门快背外廓。	READY
2519_series3_sc_3dr	2519	Hatchback	Alfasud III SC	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	SC三门掀背外廓。	READY
2519_series3_sc_5dr	2519	Hatchback	Alfasud III SC	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	SC五门掀背外廓。	READY
2519_series3_ti_2dr	2519	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	MEDIUM	改款初期TI双门快背外廓。	READY
2519_series3_ti_3dr	2519	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	MEDIUM	后期TI三门掀背外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.3 SC 5-Porte	https://www.automobile-catalog.com/car/1982/143330/alfa_romeo_alfasud_1_3_sc_5-porte.html
```

## 5) 下一步优先处理

1. 批量闭合 Peugeot 306 的三门、五门及改款前后外廓。
2. 解决 Talbot Horizon 标准版与 SX 外廓，并闭合 Tagora。
3. 最后集中处理 Peugeot J5 Bus、Pritsche/Fahrgestell 的轴距、车顶和底盘分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/44450/alfa_romeo_alfasud_1_2.html?utm_source=chatgpt.com "1980 Alfa Romeo Alfasud 1.2 4M Specs Review (46.5 kW ..."
[2]: https://www.automobile-catalog.com/car/1982/143330/alfa_romeo_alfasud_1_3_sc_5-porte.html?utm_source=chatgpt.com "1982 Alfa Romeo Alfasud 1.3 SC 5-Porte Specs Review (58 kW / 79 PS / 78 hp) (since mid-year 1982 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1) 更新点

- 闭合剩余 4 个 Alfa Romeo Alfasud Ktype。Series III 普通车身拆分为四门快背、三门掀背和五门掀背；TI 分支继续区分双门快背与三门掀背。汽车目录+4汽车目录+4汽车目录+4
- 本轮仅首次创建 Alfasud Series III 五门掀背尺寸组；其余映射全部复用已闭合尺寸组。五门组尺寸为 `3995 × 1590 × 1370 mm`，宽度为不含后视镜口径。汽车目录

## 2) 当前批次进度

- READY Ktype：77/100
- PENDING Ktype：23/100
- READY 映射行：109
- 已确认尺寸组：57
- 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2512_series3_4dr	2512	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2512_series3_3dr	2512	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2512_series3_5dr	2512	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2515_series1_2dr	2515	Sedan	Alfasud I TI	901	2	EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	HIGH	第一系列TI双门快背外廓。	READY
2515_series2_2dr	2515	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	HIGH	第二系列TI双门快背外廓。	READY
2515_series3_2dr	2515	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	第三系列初期TI双门快背外廓。	READY
2515_series3_3dr	2515	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	第三系列后期TI三门掀背外廓。	READY
2518_series2_4dr	2518	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH	第二系列Super四门快背外廓。	READY
2518_series3_4dr	2518	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2518_series3_3dr	2518	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2518_series3_5dr	2518	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2519_series2_super_4dr	2519	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	MEDIUM	Super四门快背外廓。	READY
2519_series2_ti_2dr	2519	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	MEDIUM	TI双门快背外廓。	READY
2519_series3_sc_3dr	2519	Hatchback	Alfasud III SC	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	SC三门掀背外廓。	READY
2519_series3_sc_5dr	2519	Hatchback	Alfasud III SC	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	SC五门掀背外廓。	READY
2519_series3_ti_2dr	2519	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	MEDIUM	改款初期TI双门快背外廓。	READY
2519_series3_ti_3dr	2519	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	MEDIUM	后期TI三门掀背外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.3 SC 5-Porte	https://www.automobile-catalog.com/car/1982/143330/alfa_romeo_alfasud_1_3_sc_5-porte.html
```

## 5) 下一步优先处理

- 批量闭合 Peugeot 306 的三门、五门及改款前后外廓。
- 解决 Talbot Horizon 标准版与 SX 外廓，并闭合 Tagora。
- 最后集中处理 Peugeot J5 Bus、Pritsche/Fahrgestell 的轴距、车顶和底盘分支。

推进信号：CONTINUE


--- 发送 / checkpoint 续跑到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
## 更新点

* Peugeot J5 最后 5 个 Ktype 已闭合：Bus 关联标准 Minibus 外廓；`Pritsche/Fahrgestell` 拆分短轴与长轴底盘驾驶室。
* J5 标准 Minibus 使用 `4765 × 1965 × 2100 mm`；底盘驾驶室短轴、长轴分别使用 `4712 × 1965 × 1900 mm` 和 `5489 × 1965 × 1900 mm`。280P/290P Bus 与 280L/290L Chassis 的车身代码边界已核对。([Truck1][1])
* 已完成轻量机械检查：表头正确、映射 `id` 唯一、尺寸组 ID 唯一、映射引用全部闭合，无孤立尺寸组，无空尺寸或空来源。

## 当前批次进度

* 输入 Ktype：**100**
* READY 映射行：**144**
* READY Ktype：**100/100**
* PENDING：**0**
* DIMENSION_GROUP：**71**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2468	2468	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	HIGH	Le Mans为三门专属外廓。	READY
2469_3dr	2469	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	HIGH	1.6 XS三门外廓。	READY
2469_5dr	2469	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	HIGH	1.6 XT五门外廓。	READY
2470	2470	MPV	J5 I	280P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	HIGH	标准轴距Minibus外廓。	READY
2471_swb	2471	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴双门底盘驾驶室外廓。	READY
2471_lwb	2471	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴双门底盘驾驶室外廓。	READY
2472	2472	MPV	J5 I facelift	290P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	HIGH	标准轴距Minibus外廓。	READY
2473	2473	MPV	J5 I	280P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	HIGH	标准轴距Minibus外廓。	READY
2474	2474	MPV	J5 I facelift	290P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	HIGH	标准轴距Minibus外廓。	READY
2475_3dr	2475	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	64 PS柴油版对应改款前三门外廓。	READY
2475_5dr	2475	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	64 PS柴油版对应改款前五门外廓。	READY
2476_3dr	2476	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	90 PS DT改款前三门外廓。	READY
2476_5dr	2476	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	90 PS DT改款前五门外廓。	READY
2477	2477	MPV	Touran I (GP2)	1T3	5	EU-VW-TOURAN-I-GP2-MPV-01	HIGH		READY
2478_3dr	2478	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	1.1改款前三门外廓。	READY
2478_5dr	2478	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	1.1改款前五门外廓。	READY
2479	2479	SUV	Cayenne II	92A	5	EU-PORSCHE-CAYENNE-II-SUV-TURBO-01	HIGH		READY
2480_prefl_3dr	2480	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	改款前三门外廓。	READY
2480_prefl_5dr	2480	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	改款前五门外廓。	READY
2480_facelift_3dr	2480	Hatchback	306 facelift		3	EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	HIGH	1997年后改款三门外廓。	READY
2480_facelift_5dr	2480	Hatchback	306 facelift		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	HIGH	1997年后改款五门外廓。	READY
2481	2481	SUV	Cayenne II	92A	5	EU-PORSCHE-CAYENNE-II-SUV-DIESEL-01	HIGH		READY
2482_prefl_3dr	2482	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	89 PS改款前三门外廓。	READY
2482_prefl_5dr	2482	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	89 PS改款前五门外廓。	READY
2482_facelift_5dr	2482	Hatchback	306 facelift		5	EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	MEDIUM	改款后88/89 PS五门外廓。	READY
2483	2483	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	HIGH		READY
2484_3dr	2484	Hatchback	306 Phase I		3	EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	HIGH	101 PS版本对应改款前三门外廓。	READY
2484_5dr	2484	Hatchback	306 Phase I		5	EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	HIGH	101 PS版本对应改款前五门外廓。	READY
2485_3dr	2485	Hatchback	306 Phase I XSi		3	EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-3D-01	HIGH	XSi三门运动外廓。	READY
2485_5dr	2485	Hatchback	306 Phase I XSi		5	EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-5D-01	HIGH	XSi五门运动外廓。	READY
2486	2486	Hatchback	306 Phase I S16		3	EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	HIGH	S16仅三门运动外廓。	READY
2487	2487	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2488	2488	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2489	2489	Hatchback	Samba	51A	3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
2490	2490	Convertible	Samba	51E	2	EU-TALBOT-SAMBA-CONVERTIBLE-01	HIGH		READY
2491	2491	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2492	2492	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2493	2493	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2494	2494	MPV	Grand C-MAX II		5	EU-FORD-GRAND-C-MAX-II-MPV-01	HIGH		READY
2495	2495	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2496	2496	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2497	2497	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2498	2498	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2499	2499	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
2500	2500	Hatchback	Simca 1307		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1307。	READY
2501	2501	Hatchback	Simca 1308		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1308。	READY
2502	2502	Hatchback	Simca 1308		5	EU-TALBOT-1307-1308-HATCHBACK-01	HIGH	VariantName明确为Simca 1308。	READY
2503	2503	Hatchback	Talbot 1510		5	EU-TALBOT-1510-HATCHBACK-01	HIGH	VariantName明确为1510。	READY
2504	2504	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2505	2505	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2506	2506	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2507	2507	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2508	2508	Sedan	Solara		4	EU-TALBOT-SOLARA-SEDAN-01	HIGH		READY
2509	2509	Sedan	Tagora		4	EU-TALBOT-TAGORA-SEDAN-01	MEDIUM	输入2.1对应2156cc的2.2 GL/GLS外廓。	READY
2510	2510	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	MEDIUM	输入2.1/116 PS按同期2.2-litre量产分支映射。	READY
2511	2511	MPV	Rancho		3	EU-TALBOT-RANCHO-MPV-01	HIGH		READY
2512_series3_4dr	2512	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2512_series3_3dr	2512	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2512_series3_5dr	2512	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2513_series1_4dr	2513	Sedan	Alfasud I	901	4	EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	HIGH	第一系列四门快背车身。	READY
2513_series2_4dr	2513	Sedan	Alfasud II	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH	第二系列四门快背车身。	READY
2513_series3_4dr	2513	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	HIGH	第三系列四门快背车身。	READY
2513_series3_3dr	2513	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	HIGH	第三系列三门掀背车身。	READY
2515_series1_2dr	2515	Sedan	Alfasud I TI	901	2	EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	HIGH	第一系列TI双门快背外廓。	READY
2515_series2_2dr	2515	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	HIGH	第二系列TI双门快背外廓。	READY
2515_series3_2dr	2515	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	第三系列初期TI双门快背外廓。	READY
2515_series3_3dr	2515	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	第三系列后期TI三门掀背外廓。	READY
2516	2516	Sedan	Alfasud II	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH		READY
2517	2517	Sedan	Alfasud I TI	901	2	EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	HIGH		READY
2518_series2_4dr	2518	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	HIGH	第二系列Super四门快背外廓。	READY
2518_series3_4dr	2518	Sedan	Alfasud III	901	4	EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	MEDIUM	第三系列四门快背外廓。	READY
2518_series3_3dr	2518	Hatchback	Alfasud III	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	第三系列三门掀背外廓。	READY
2518_series3_5dr	2518	Hatchback	Alfasud III	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	第三系列五门掀背外廓。	READY
2519_series2_super_4dr	2519	Sedan	Alfasud II Super	901	4	EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	MEDIUM	Super四门快背外廓。	READY
2519_series2_ti_2dr	2519	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	MEDIUM	TI双门快背外廓。	READY
2519_series3_sc_3dr	2519	Hatchback	Alfasud III SC	901	3	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	MEDIUM	SC三门掀背外廓。	READY
2519_series3_sc_5dr	2519	Hatchback	Alfasud III SC	901	5	EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	MEDIUM	SC五门掀背外廓。	READY
2519_series3_ti_2dr	2519	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	MEDIUM	改款初期TI双门快背外廓。	READY
2519_series3_ti_3dr	2519	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	MEDIUM	后期TI三门掀背外廓。	READY
2520_2dr	2520	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	改款初期双门快背车身。	READY
2520_3dr	2520	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	后期三门掀背车身。	READY
2521	2521	Sedan	Alfasud II TI	901	2	EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	HIGH		READY
2522_2dr	2522	Sedan	Alfasud III TI	901	2	EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	HIGH	改款初期双门快背车身。	READY
2522_3dr	2522	Hatchback	Alfasud III TI	901	3	EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	HIGH	后期三门掀背车身。	READY
2523	2523	Coupe	Sprint II	902A	3	EU-ALFA-ROMEO-SPRINT-902A-COUPE-QV-01	HIGH	输入TI Sprint对应105 PS Quadrifoglio Verde外廓。	READY
2524	2524	Wagon	Alfasud Giardinetta	904A	3	EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	HIGH		READY
2525	2525	Wagon	Alfasud Giardinetta	904B2	3	EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	HIGH		READY
2526	2526	Hatchback	Alfa Romeo 33 I	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	HIGH		READY
2527	2527	Hatchback	Alfa Romeo 33 I	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	HIGH	四驱车身高度独立。	READY
2528	2528	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2529	2529	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2530	2530	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2531	2531	Wagon	Alfa Romeo 33 I	905A	5	EU-ALFA-ROMEO-33-905-WAGON-FWD-01	HIGH		READY
2532	2532	Sedan	Alfa 6 I facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	HIGH		READY
2533_prefl	2533	Sedan	Alfa 6 I pre-facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-PREFL-01	HIGH	生产区间覆盖第一系列外廓。	READY
2533_facelift	2533	Sedan	Alfa 6 I facelift	119	4	EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	HIGH	生产区间覆盖1983年改款后外廓。	READY
2534	2534	SUV	Range Rover III	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	HIGH		READY
2535	2535	Hatchback	Alfa Romeo 33 II	907A	5	EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	HIGH		READY
2536	2536	Hatchback	Alfa Romeo 33 II	907A	5	EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	HIGH		READY
2537	2537	Wagon	Alfa Romeo 33 II	907B	5	EU-ALFA-ROMEO-33-907-WAGON-4X4-01	HIGH		READY
2538	2538	Hatchback	A7 Sportback I (C7)	4G8	5	EU-AUDI-A7-C7-SPORTBACK-01	HIGH		READY
2539	2539	Wagon	Alfa Romeo 33 II	907B	5	EU-ALFA-ROMEO-33-907-WAGON-4X4-01	HIGH		READY
2540	2540	Sedan	Nuova 500 N	110	2	EU-FIAT-500-110-SEDAN-01	HIGH		READY
2541	2541	Sedan	Nuova 500 F/L/R	110	2	EU-FIAT-500-110-SEDAN-01	HIGH		READY
2542	2542	Wagon	500 Giardiniera	120	3	EU-FIAT-500-120-GIARDINIERA-WAGON-01	HIGH		READY
2543_series1_3dr	2543	Hatchback	127 Series I		3	EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	HIGH	第一系列低压缩三门外廓。	READY
2543_series2_3dr	2543	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	HIGH	第二系列低压缩三门外廓。	READY
2544_series1_3dr	2544	Hatchback	127 Series I		3	EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	HIGH	第一系列标准三门外廓。	READY
2544_series1_special_3dr	2544	Hatchback	127 Series I Special		3	EU-FIAT-127-SERIES-I-SPECIAL-HATCHBACK-3D-01	HIGH	Special保险杠造成长度差异。	READY
2544_series2_3dr	2544	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	HIGH	第二系列三门外廓。	READY
2544_series2_5dr	2544	Hatchback	127 Series II		5	EU-FIAT-127-SERIES-II-HATCHBACK-5D-01	HIGH	第二系列五门外廓。	READY
2544_series3_3dr	2544	Hatchback	127 Series III		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	HIGH	第三系列三门外廓。	READY
2545_series2_3dr	2545	Hatchback	127 Series II		3	EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	MEDIUM	第二系列三门物理外廓。	READY
2545_series3_3dr	2545	Hatchback	127 Series III		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	MEDIUM	第三系列三门物理外廓。	READY
2545_series3_5dr	2545	Hatchback	127 Series III		5	EU-FIAT-127-SERIES-III-HATCHBACK-5D-01	MEDIUM	第三系列五门物理外廓。	READY
2545_unificata_3dr	2545	Hatchback	127 Unificata		3	EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	MEDIUM	后期Unificata三门物理外廓。	READY
2546	2546	Hatchback	127 Series II Sport		3	EU-FIAT-127-SERIES-II-SPORT-HATCHBACK-3D-01	HIGH		READY
2547	2547	Hatchback	127 Series III Sport		3	EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	HIGH		READY
2548_early	2548	Hatchback	127 Diesel early		3	EU-FIAT-127-DIESEL-EARLY-HATCHBACK-3D-01	MEDIUM	早期柴油三门外廓。	READY
2548_facelift	2548	Hatchback	127 Unificata Diesel		3	EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	MEDIUM	后期柴油三门外廓。	READY
2549	2549	Wagon	127 Panorama		3	EU-FIAT-127-PANORAMA-WAGON-01	HIGH		READY
2550	2550	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH	1986年起改款外廓。	READY
2551	2551	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	HIGH	1986年前外廓。	READY
2552_prefl	2552	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	HIGH	生产区间覆盖1986年改款前外廓。	READY
2552_facelift	2552	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH	生产区间覆盖1986年改款后外廓。	READY
2553	2553	Hatchback	Panda I pre-facelift	141	3	EU-FIAT-PANDA-I-PREFL-4X4-01	HIGH		READY
2554	2554	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2555	2555	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2556	2556	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2557	2557	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-01	HIGH	输入BodyStyle为Schrägheck，车型资料归为小型MPV。	READY
2558	2558	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2559	2559	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-01	HIGH		READY
2560	2560	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2561	2561	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	HIGH	Trekking加高外廓。	READY
2562	2562	Hatchback	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	HIGH		READY
2563	2563	Van	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	MEDIUM	封闭货运版复用同代三门外部车身。	READY
2564	2564	Van	Panda I facelift	141	3	EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	MEDIUM	封闭货运版复用同代三门外部车身。	READY
2565	2565	Hatchback	Fiat 126 I		2	EU-FIAT-126-EARLY-STANDARD-01	HIGH		READY
2566_standard	2566	Hatchback	Fiat 126 650 standard		2	EU-FIAT-126-EARLY-STANDARD-01	MEDIUM	标准车身外廓。	READY
2566_economic	2566	Hatchback	Fiat 126 650 Economic		2	EU-FIAT-126-650-ECONOMIC-01	MEDIUM	Economic车身外廓。	READY
2566_personal	2566	Hatchback	Fiat 126 650 Personal		2	EU-FIAT-126-650-PERSONAL-01	MEDIUM	Personal车身外廓。	READY
2566_facelift	2566	Hatchback	Fiat 126 650 facelift		2	EU-FIAT-126-650-FACELIFT-01	MEDIUM	后期改款车身外廓。	READY
2567	2567	Hatchback	Fiat 126 BIS		3	EU-FIAT-126-BIS-HATCHBACK-01	HIGH	704发动机对应带后尾门的BIS车身。	READY
2568	2568	Convertible	124 Sport Spider I		2	EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	MEDIUM	按90 PS首代124 Sport Spider外廓映射。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2401-2500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	3564	1607	1360	Automobile-Catalog Peugeot 106 Le Mans	https://www.automobile-catalog.com/car/1994/2608535/peugeot_106_le_mans.html
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367	Automobile-Catalog Peugeot 106 1.6i XS	https://www.automobile-catalog.com/car/1994/2608595/peugeot_106_1_6i_xs.html
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367	Automobile-Catalog Peugeot 106 1.6i XT	https://www.automobile-catalog.com/car/1994/2608610/peugeot_106_1_6i_xt.html
EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	4765	1965	2100	Truck1 Peugeot J5 Minibus 2.5 D;Truck1 Peugeot J5 Minibus 2.0	https://www.truck1.eu/blog/peugeot-j5-minibus-2-5-d-73-hp-tech-specs-t30521;https://www.truck1.eu/blog/peugeot-j5-minibus-2-0-75-hp-tech-specs-t30506
EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	4712	1965	1900	Zoomcar Peugeot J5 Chassis Cab 1400 D Short	https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/j5-chassis-cabine-j5-chassis-cab-1400-d-court-NAT56839.html
EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	5489	1965	1900	Zoomcar Peugeot J5 Chassis Cab 1400 D Long	https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/j5-chassis-cabine-j5-chassis-cab-1400-d-long-NAT56838.html
EU-PEUGEOT-306-PHASE-I-HATCHBACK-3D-01	3995	1692	1380	Auto-Data Peugeot 306 Hatchback 1.9 DT 90	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-1.9-dt-90hp-5716
EU-PEUGEOT-306-PHASE-I-HATCHBACK-5D-01	3995	1692	1380	Auto-Data Peugeot 306 Hatchback 1.9 DT 90	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-1.9-dt-90hp-5716
EU-VW-TOURAN-I-GP2-MPV-01	4397	1794	1634	Volkswagen The New Touran official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2010-UK.pdf
EU-PORSCHE-CAYENNE-II-SUV-TURBO-01	4846	1939	1702	Automobile-Catalog Porsche Cayenne Turbo	https://www.automobile-catalog.com/car/2010/2869655/porsche_cayenne_turbo.html
EU-PEUGEOT-306-FACELIFT-HATCHBACK-3D-01	4030	1690	1380	Auto-Data Peugeot 306 Hatchback facelift generation	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PEUGEOT-306-FACELIFT-HATCHBACK-5D-01	4030	1690	1380	Auto-Data Peugeot 306 Hatchback facelift generation	https://www.auto-data.net/en/peugeot-306-hatchback-facelift-1997-generation-6618
EU-PORSCHE-CAYENNE-II-SUV-DIESEL-01	4846	1939	1705	Automobile-Catalog Porsche Cayenne Diesel	https://www.automobile-catalog.com/car/2011/2869625/porsche_cayenne_diesel.html
EU-LAND-ROVER-RANGE-ROVER-III-SUV-2010-01	4972	1956	1865	Automobile-Catalog Range Rover 4.4 TDV8 Vogue;Automobile-Catalog Range Rover 5.0 V8 Vogue	https://www.automobile-catalog.com/car/2011/1404485/range_rover_4_4_tdv8_vouge.html;https://www.automobile-catalog.com/car/2010/1404500/range_rover_5_0_v8_vouge.html
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-3D-01	3995	1692	1367	Auto-Data Peugeot 306 Hatchback 2.0 XSi 121	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-2.0-xsi-121hp-5722
EU-PEUGEOT-306-PHASE-I-XSI-HATCHBACK-5D-01	3995	1692	1367	Auto-Data Peugeot 306 Hatchback 2.0 XSi 121	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-2.0-xsi-121hp-5722
EU-PEUGEOT-306-PHASE-I-S16-HATCHBACK-3D-01	3995	1695	1365	Auto-Data Peugeot 306 S16 152;Auto-Data Peugeot 306 S16 163	https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-2.0-s16-152hp-5720;https://www.auto-data.net/en/peugeot-306-hatchback-7a-c-2.0-s16-163hp-5721
EU-TALBOT-SAMBA-HATCHBACK-01	3506	1528	1362	Automobile-Catalog Talbot Samba 1.4 GLS	https://www.automobile-catalog.com/car/1983/55535/talbot_samba_1_4_gls.html
EU-TALBOT-SAMBA-CONVERTIBLE-01	3506	1528	1362	Automobile-Catalog Talbot Samba Cabriolet 1.4	https://www.automobile-catalog.com/car/1983/3118040/talbot_samba_1_4.html
EU-TALBOT-HORIZON-HATCHBACK-01	3960	1680	1410	Automobile-Catalog Talbot Horizon 1.1 LS	https://www.automobile-catalog.com/car/1980/3116495/talbot_horizon_1_1_ls_59.html
EU-FORD-GRAND-C-MAX-II-MPV-01	4520	1828	1684	Auto-Data Ford Grand C-MAX II 2.0 TDCi 163	https://www.auto-data.net/en/ford-grand-c-max-ii-2.0-duratorq-tdci-163hp-dpf-powershift-19881
EU-TALBOT-1307-1308-HATCHBACK-01	4245	1680	1400	Automobile-Catalog Simca 1307 S	https://www.automobile-catalog.com/car/1978/28220/simca_1307_s.html
EU-TALBOT-1510-HATCHBACK-01	4318	1680	1390	Automobile-Catalog Talbot 1510 1.6 GLS	https://www.automobile-catalog.com/car/1980/3112475/talbot_1510_1_6_gls.html
EU-TALBOT-SOLARA-SEDAN-01	4393	1680	1390	Automobile-Catalog Talbot Solara 1.6 GLS	https://www.automobile-catalog.com/car/1982/3113480/talbot_solara_1_6_gls.html
EU-TALBOT-TAGORA-SEDAN-01	4628	1810	1444	Automobile-Catalog Talbot Tagora GLS;Engine in Detail Talbot Tagora	https://www.automobile-catalog.com/car/1980/3118355/talbot_tagora_gls.html;https://www.engineindetail.com/cars/talbot/tagora
EU-TALBOT-MURENA-COUPE-01	4070	1752	1220	Automobile-Catalog Talbot-Matra Murena 2.2-litre	https://www.automobile-catalog.com/car/1981/1458620/talbot_matra_murena_2_2-litre.html
EU-TALBOT-RANCHO-MPV-01	4315	1665	1735	Automobile-Catalog Talbot-Matra Rancho	https://www.automobile-catalog.com/car/1983/1458710/talbot_matra_rancho.html
EU-ALFA-ROMEO-ALFASUD-III-SEDAN-4D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.2 4M	https://www.automobile-catalog.com/car/1980/44450/alfa_romeo_alfasud_1_2.html
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-3D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.2 3-Porte	https://www.automobile-catalog.com/car/1981/143195/alfa_romeo_alfasud_1_2_3-porte.html
EU-ALFA-ROMEO-ALFASUD-III-HATCHBACK-5D-01	3995	1590	1370	Automobile-Catalog Alfa Romeo Alfasud 1.3 SC 5-Porte	https://www.automobile-catalog.com/car/1982/143330/alfa_romeo_alfasud_1_3_sc_5-porte.html
EU-ALFA-ROMEO-ALFASUD-I-SEDAN-4D-01	3890	1590	1370	Automobile-Catalog Alfa Romeo Alfasud	https://www.automobile-catalog.com/car/1972/27740/alfa_romeo_alfasud.html
EU-ALFA-ROMEO-ALFASUD-II-SEDAN-4D-01	3935	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Super 1.3	https://www.automobile-catalog.com/car/1977/35855/alfa_romeo_alfasud_super_1_3.html
EU-ALFA-ROMEO-ALFASUD-I-TI-SEDAN-2D-01	3926	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3	https://www.automobile-catalog.com/car/1977/143090/alfa_romeo_alfasud_ti_1_3.html
EU-ALFA-ROMEO-ALFASUD-II-TI-SEDAN-2D-01	3935	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.5	https://www.automobile-catalog.com/car/1978/35900/alfa_romeo_alfasud_ti_1_5.html
EU-ALFA-ROMEO-ALFASUD-III-TI-SEDAN-2D-01	3995	1616	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3	https://www.automobile-catalog.com/car/1980/143180/alfa_romeo_alfasud_ti_1_3.html
EU-ALFA-ROMEO-ALFASUD-III-TI-HATCHBACK-3D-01	3995	1616	1370	Automobile-Catalog Alfa Romeo Alfasud Ti 1.3 3-Porte	https://www.automobile-catalog.com/car/1981/143240/alfa_romeo_alfasud_ti_1_3_3-porte.html
EU-ALFA-ROMEO-SPRINT-902A-COUPE-QV-01	4024	1620	1295	Automobile-Catalog Alfa Romeo Sprint 1.5 Quadrifoglio Verde	https://www.automobile-catalog.com/car/1983/41660/alfa_romeo_sprint_1_5_quadrifoglio_verde.html
EU-ALFA-ROMEO-ALFASUD-904A-WAGON-01	3935	1590	1370	Auto-Data Alfa Romeo Alfasud Giardinetta 1.2	https://www.auto-data.net/en/alfa-romeo-alfasud-giardinetta-904-1.2-63hp-1343
EU-ALFA-ROMEO-ALFASUD-904B2-WAGON-01	3975	1590	1370	Automobile-Catalog Alfa Romeo Alfasud Giardinetta 1.3	https://www.automobile-catalog.com/car/1979/143135/alfa_romeo_alfasud_giardinietta_1_3.html
EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	4015	1612	1303	Automobile-Catalog Alfa Romeo 33 1.5	https://www.automobile-catalog.com/car/1983/48725/alfa_romeo_33_1_5.html
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	4015	1612	1345	Automobile-Catalog Alfa Romeo 33 1.5 4x4	https://www.automobile-catalog.com/car/1987/215045/alfa_romeo_33_1_5_4x4.html
EU-ALFA-ROMEO-33-905-WAGON-FWD-01	4142	1612	1345	Automobile-Catalog Alfa Romeo 33 1.5 Giardinetta	https://www.automobile-catalog.com/car/1986/215075/alfa_romeo_33_1_5_giardinietta.html
EU-ALFA-ROMEO-ALFA-6-119-SEDAN-FACELIFT-01	4679	1685	1395	Automobile-Catalog Alfa Romeo Alfa 6 2.5 Iniezione Quadrifoglio Oro	https://www.automobile-catalog.com/car/1985/49775/alfa_romeo_alfa_6_2_5_iniezione_quadrifoglio_oro.html
EU-ALFA-ROMEO-ALFA-6-119-SEDAN-PREFL-01	4760	1685	1395	Automobile-Catalog Alfa Romeo Alfa 6	https://www.automobile-catalog.com/car/1982/24500/alfa_romeo_alfa_6.html
EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	4075	1614	1375	Automobile-Catalog Alfa Romeo 33 16V Permanent 4 Quadrifoglio Verde	https://www.automobile-catalog.com/car/1991/216875/alfa_romeo_33_1_7_ie_16v_permanent_4_quadrifoglio_verde_s.html
EU-ALFA-ROMEO-33-907-WAGON-4X4-01	4200	1614	1375	Automobile-Catalog Alfa Romeo 33 1.7 ie Sport Wagon 4x4	https://www.automobile-catalog.com/car/1992/217055/alfa_romeo_33_1_7_ie_sport_wagon_4x4.html
EU-AUDI-A7-C7-SPORTBACK-01	4969	1911	1420	Audi A7 Sportback official technical data	https://www.ausmotive.com/downloads/Audi/A7-Sportback-tech-data-Mar2011.pdf
EU-FIAT-500-110-SEDAN-01	2970	1320	1325	Automobile-Catalog Fiat 500 Economica	https://www.automobile-catalog.com/car/1958/708695/fiat_500_economica_standard.html
EU-FIAT-500-120-GIARDINIERA-WAGON-01	3185	1323	1354	Automobile-Catalog Fiat 500 Giardiniera	https://www.automobile-catalog.com/car/1960/708800/fiat_500_giardiniera.html
EU-FIAT-127-SERIES-I-HATCHBACK-3D-01	3595	1527	1380	Automobile-Catalog Fiat 127 Tre Porte	https://www.automobile-catalog.com/car/1972/711125/fiat_127_tre_porte.html
EU-FIAT-127-SERIES-II-HATCHBACK-3D-01	3645	1527	1380	Automobile-Catalog Fiat 127 900 CL 3P	https://www.automobile-catalog.com/car/1979/2067110/fiat_127_900_cl_3p_low_compr.html
EU-FIAT-127-SERIES-I-SPECIAL-HATCHBACK-3D-01	3635	1527	1380	Automobile-Catalog Fiat 127 Special 3 Porte 45PS	https://www.automobile-catalog.com/car/1974/711320/fiat_127_special_3_porte.html
EU-FIAT-127-SERIES-II-HATCHBACK-5D-01	3645	1527	1380	Automobile-Catalog Fiat 127 900 CL 5 Porte	https://www.automobile-catalog.com/car/1981/711455/fiat_127_c_5_porte.html
EU-FIAT-127-SERIES-III-HATCHBACK-3D-01	3711	1552	1370	Automobile-Catalog Fiat 127 1050 Super 3-door	https://www.automobile-catalog.com/car/1982/711530/fiat_127_super.html
EU-FIAT-127-SERIES-III-HATCHBACK-5D-01	3711	1552	1370	Automobile-Catalog Fiat 127 1050 Super 5 Porte	https://www.automobile-catalog.com/car/1982/711560/fiat_127_super_5_porte.html
EU-FIAT-127-UNIFICATA-HATCHBACK-3D-01	3745	1545	1405	Automobile-Catalog Fiat 127 1050	https://www.automobile-catalog.com/car/1984/711590/fiat_127_1050.html
EU-FIAT-127-SERIES-II-SPORT-HATCHBACK-3D-01	3645	1536	1380	Automobile-Catalog Fiat 127 Sport	https://www.automobile-catalog.com/car/1980/711425/fiat_127_sport.html
EU-FIAT-127-DIESEL-EARLY-HATCHBACK-3D-01	3745	1545	1410	Automobile-Catalog Fiat 127 D	https://www.automobile-catalog.com/car/1981/711500/fiat_127_d.html
EU-FIAT-127-PANORAMA-WAGON-01	3920	1545	1425	Automobile-Catalog Fiat 127 Panorama D	https://www.automobile-catalog.com/car/1981/711485/fiat_127_panorama_d.html
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420	Automobile-Catalog Fiat Panda 750 L	https://www.automobile-catalog.com/car/1986/715055/fiat_panda_750_l_5-speed.html
EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	3380	1460	1445	Automobile-Catalog Fiat Panda 45 Super	https://www.automobile-catalog.com/car/1986/28925/fiat_panda_45_super_5-speed.html
EU-FIAT-PANDA-I-PREFL-4X4-01	3390	1485	1470	Automobile-Catalog Fiat Panda 4x4	https://www.automobile-catalog.com/car/1984/49220/fiat_panda_4x4.html
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468	Automobile-Catalog Fiat Panda 1000 4x4	https://www.automobile-catalog.com/car/1991/31340/fiat_panda_1000_4x4.html
EU-HYUNDAI-IX20-JC-MPV-01	4100	1765	1600	Hyundai ix20 official brochure (archived)	https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-ix20-2012-UK.pdf
EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	3408	1500	1485	Auto Bild Klassik Fiat Panda 4x4 Trekking	https://www.autobild.de/klassik/artikel/fiat-panda-4x4-trekking-1300570.html
EU-FIAT-126-EARLY-STANDARD-01	3054	1377	1335	Automobile-Catalog Fiat 126	https://www.automobile-catalog.com/car/1972/711065/fiat_126.html
EU-FIAT-126-650-ECONOMIC-01	3070	1377	1335	Automobile-Catalog Fiat 126 Economic	https://www.automobile-catalog.com/car/1981/711095/fiat_126.html
EU-FIAT-126-650-PERSONAL-01	3129	1382	1335	Automobile-Catalog Fiat 126 Personal	https://www.automobile-catalog.com/car/1977/711080/fiat_126_personal.html
EU-FIAT-126-650-FACELIFT-01	3109	1377	1335	Automobile-Catalog Fiat 126 facelift	https://www.automobile-catalog.com/car/1985/2066855/fiat_126.html
EU-FIAT-126-BIS-HATCHBACK-01	3107	1377	1343	Automobile-Catalog Fiat 126 BIS	https://www.automobile-catalog.com/car/1987/717935/fiat_126_bis.html
EU-FIAT-124-SPORT-SPIDER-I-CONVERTIBLE-01	3971	1613	1250	Automobile-Catalog Fiat 124 Sport Spider 1400	https://www.automobile-catalog.com/car/1968/709790/fiat_124_sport_spider_1400.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2401-2500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.truck1.eu/blog/peugeot-j5-minibus-2-5-d-73-hp-tech-specs-t30521?srsltid=AfmBOoq3NlqgCP_deivdo0Sda_kHUhbZVzi4Ur1MtSj5Nf3Wp7eOoD8q&utm_source=chatgpt.com "Peugeot J5 Minibus 2.5 D (73 Hp) - Tech specs"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2401-2500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2401-2500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4408 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1266 行）

