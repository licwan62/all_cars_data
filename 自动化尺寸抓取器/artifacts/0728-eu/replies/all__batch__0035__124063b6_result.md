# 任务：all 第 3401-3500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0035__124063b6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3401-3500 行

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
all 第 3401-3500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mitsubishi	Lancer viii sportback	1.6 Mivec	Schrägheck	Frontantrieb	Benzin	86	117	May 2010	-	2024-03-01	3520
Toyota	Carina iv	1.6	Schrägheck	Frontantrieb	Benzin	63	86	Oct 1986	Nov 1987	2024-03-01	3521
Toyota	Carina iv	1.8 GLI	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1983	Nov 1987	2024-03-01	3522
Toyota	Carina iv	1.8 GLI	Schrägheck	Frontantrieb	Benzin	74	101	Oct 1983	Nov 1987	2024-03-01	3523
Toyota	Carina iv	2.0 D	Schrägheck	Frontantrieb	Diesel	51	69	Dec 1985	Nov 1987	2024-03-01	3524
Toyota	Carina v	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Dec 1987	Aug 1990	2024-03-01	3525
Toyota	Carina v	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Dec 1987	Nov 1989	2024-03-01	3526
Toyota	Carina v	1.6	Stufenheck	Frontantrieb	Benzin	75	102	Dec 1987	Mar 1992	2024-03-01	3527
Toyota	Carina v	1.6	Schrägheck	Frontantrieb	Benzin	75	102	Dec 1987	Mar 1992	2024-03-01	3528
Toyota	Carina v	2.0 GLI	Stufenheck	Frontantrieb	Benzin	89	121	Dec 1987	Mar 1992	2024-03-01	3529
Toyota	Carina v	2.0 GLI	Schrägheck	Frontantrieb	Benzin	89	121	Dec 1987	Mar 1992	2024-03-01	3530
Toyota	Carina v	1.6	Stufenheck	Frontantrieb	Benzin	72	98	Dec 1987	Mar 1992	2024-03-01	3531
Toyota	Carina v	1.6	Schrägheck	Frontantrieb	Benzin	72	98	Dec 1987	Mar 1992	2024-03-01	3532
Toyota	Carina v	1.6	Kombi	Frontantrieb	Benzin	66	90	Dec 1987	Dec 1989	2024-03-01	3533
Toyota	Carina v	1.6	Kombi	Frontantrieb	Benzin	75	102	Dec 1987	Mar 1992	2024-03-01	3534
Toyota	Carina v	1.6	Kombi	Frontantrieb	Benzin	72	98	Dec 1987	Mar 1992	2024-03-01	3535
BMW	3	325 I	Kombi	Heckantrieb	Benzin	155	211	Sep 2007	Jun 2012	2024-03-01	3536
Toyota	Tercel	1.3	Schrägheck	Frontantrieb	Benzin	48	65	Mar 1979	Jan 1988	2024-03-01	3537
Toyota	Camry	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1983	Oct 1986	2024-03-01	3538
Toyota	Camry	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1983	Oct 1986	2024-03-01	3539
Toyota	Camry	2	Stufenheck	Frontantrieb	Benzin	79	107	Feb 1983	Oct 1986	2024-03-01	3540
Mitsubishi	Lancer viii sportback	1.8 Mivec	Schrägheck	Frontantrieb	Benzin	103	140	Mar 2009	-	2024-03-01	3541
Toyota	Camry	2	Stufenheck	Frontantrieb	Benzin	94	128	Nov 1986	May 1991	2024-03-01	3542
Toyota	Camry	2	Stufenheck	Frontantrieb	Benzin	89	121	Nov 1986	Feb 1993	2024-03-01	3543
Toyota	Camry	2.5	Stufenheck	Frontantrieb	Benzin	118	160	Oct 1986	Jun 1991	2024-03-01	3544
Toyota	Camry	2.0 Turbo-d	Stufenheck	Frontantrieb	Diesel	62	84	Nov 1986	May 1991	2024-03-01	3545
Toyota	Camry	2.0 Turbo-d	Stufenheck	Frontantrieb	Diesel	63	86	Oct 1986	May 1991	2024-03-01	3546
Toyota	Camry	2.2	Stufenheck	Frontantrieb	Benzin	100	136	Jun 1991	Jul 1996	2024-03-01	3547
Toyota	Camry	3	Stufenheck	Frontantrieb	Benzin	138	188	Jun 1991	Aug 1996	2024-03-01	3548
Toyota	Camry	2	Kombi	Frontantrieb	Benzin	94	128	Nov 1986	May 1991	2024-03-01	3549
Toyota	Camry	2	Kombi	Frontantrieb	Benzin	89	121	Nov 1986	Feb 1993	2024-03-01	3550
Toyota	Camry	2.0 Turbo-d	Kombi	Frontantrieb	Diesel	62	84	Nov 1986	May 1991	2024-03-01	3551
Toyota	Camry	2.0 Turbo-d	Kombi	Frontantrieb	Diesel	63	86	Nov 1988	May 1991	2024-03-01	3552
Toyota	Camry	2.2	Kombi	Frontantrieb	Benzin	100	136	Sep 1991	Jul 1996	2024-03-01	3553
Toyota	Camry	2.5	Kombi	Frontantrieb	Benzin	118	160	Nov 1986	May 1991	2024-03-01	3554
Toyota	Camry	3	Kombi	Frontantrieb	Benzin	138	188	Sep 1991	Jul 1996	2024-03-01	3555
Toyota	Crown	2.8 SI	Stufenheck	Heckantrieb	Benzin	107	146	Apr 1980	Jul 1983	2024-03-01	3556
Mazda	323 ii	1.5	Stufenheck	Frontantrieb	Benzin	65	88	Mar 1982	Sep 1986	2024-03-01	3557
Mazda	323 ii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	63	86	Nov 1980	Dec 1983	2024-03-01	3558
Mazda	323 ii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	65	88	Mar 1982	Dec 1985	2024-03-01	3559
Mitsubishi	Lancer viii sportback	1.8 Di-d	Schrägheck	Frontantrieb	Diesel	85	116	May 2010	-	2024-03-01	3560
Mazda	323 iii hatchback	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Sep 1985	Oct 1989	2024-03-01	3561
Mazda	323 iii hatchback	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1985	Dec 1987	2024-03-01	3562
Mazda	323 iii	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1985	May 1989	2024-03-01	3563
Mazda	323 iii hatchback	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1985	May 1989	2024-03-01	3564
Mazda	323 iii	1.5	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1985	May 1989	2024-03-01	3565
Toyota	Celica	1.6 LT	Coupe	Heckantrieb	Benzin	55	75	Feb 1979	Jul 1981	2024-03-01	3566
Toyota	Celica	1.6 ST	Coupe	Heckantrieb	Benzin	63	86	Aug 1977	Jul 1981	2024-03-01	3567
Toyota	Celica	1.6 ST	Schrägheck	Heckantrieb	Benzin	63	86	Aug 1977	Jul 1981	2024-03-01	3568
Alpina	B3	GT3	Coupe	Heckantrieb	Benzin	300	408	Mar 2012	Dec 2013	2024-03-01	3569
Alpina	B5	Biturbo	Kombi	Heckantrieb	Benzin	397	540	Jan 2012	Dec 2014	2024-03-01	3570
Toyota	Celica	1.6 ST	Schrägheck	Heckantrieb	Benzin	66	90	Feb 1979	Jul 1981	2024-03-01	3571
Toyota	Celica	1.6 ST	Coupe	Heckantrieb	Benzin	66	90	Feb 1979	Jul 1981	2024-03-01	3572
Toyota	Celica	2.0 XT	Schrägheck	Heckantrieb	Benzin	65	88	Jan 1980	Jul 1981	2024-03-01	3573
Toyota	Celica	2.0 XT	Schrägheck	Heckantrieb	Benzin	66	90	Aug 1977	Jul 1981	2024-03-01	3574
Toyota	Celica	2.0 GT	Schrägheck	Heckantrieb	Benzin	90	122	Aug 1977	Jul 1981	2024-03-01	3575
Toyota	Celica	2.0 XT	Schrägheck	Heckantrieb	Benzin	77	105	Feb 1982	Aug 1985	2024-03-01	3576
Toyota	Celica	1.6 GT 16V	Schrägheck	Frontantrieb	Benzin	91	124	Sep 1985	Aug 1989	2024-03-01	3577
Toyota	Celica	2.0 GT	Schrägheck	Frontantrieb	Benzin	110	150	Aug 1985	Aug 1989	2024-03-01	3578
Toyota	Celica	1.6 GT	Schrägheck	Frontantrieb	Benzin	85	116	Aug 1987	Aug 1989	2024-03-01	3579
Toyota	Celica	2.0 GT	Schrägheck	Frontantrieb	Benzin	103	140	Sep 1985	Aug 1989	2024-03-01	3580
Toyota	Celica	2.0 Turbo 4WD	Coupe	Allrad	Benzin	136	185	Mar 1988	Aug 1989	2024-03-01	3581
Toyota	Celica	2	Coupe	Frontantrieb	Benzin	110	150	Jan 1987	Aug 1989	2024-03-01	3582
Toyota	Celica	2.0 GT	Cabriolet	Frontantrieb	Benzin	103	140	Aug 1985	Aug 1989	2024-03-01	3583
Toyota	Celica	2.0 GT	Cabriolet	Frontantrieb	Benzin	110	150	Oct 1986	Aug 1989	2024-03-01	3584
Toyota	Supra	3.0 24V	Coupe	Heckantrieb	Benzin	150	204	Jan 1986	Aug 1988	2024-03-01	3585
Toyota	Supra	3.0 Turbo	Coupe	Heckantrieb	Benzin	173	235	Sep 1987	Apr 1993	2024-03-01	3586
Toyota	Supra	3.0 Turbo	Coupe	Heckantrieb	Benzin	175	238	Aug 1988	May 1993	2024-03-01	3587
Toyota	Mr2 i	1.6 16V	Coupe	Heckantrieb	Benzin	85	116	Nov 1984	Jun 1990	2024-03-01	3588
Toyota	Mr2 i	1.6 16V	Coupe	Heckantrieb	Benzin	91	124	Nov 1984	Jun 1990	2024-03-01	3589
Toyota	Mr2 ii	2.0 16V	Coupe	Heckantrieb	Benzin	115	156	Dec 1989	Sep 1999	2024-03-01	3590
Toyota	Celica	2.8 Supra	Coupe	Heckantrieb	Benzin	125	170	Aug 1981	Dec 1985	2024-03-01	3591
Toyota	Hiace ii	1.6	Bus	Heckantrieb	Benzin	49	67	Feb 1977	Nov 1982	2024-03-01	3592
Toyota	Hiace iii	2	Bus	Heckantrieb	Benzin	65	88	Jan 1985	Aug 1989	2024-03-01	3593
Toyota	Hiace iii	2.4 D	Bus	Heckantrieb	Diesel	55	75	Apr 1984	Aug 1989	2024-03-01	3594
Toyota	Liteace	1.3	Kasten	Heckantrieb	Benzin	42	57	Oct 1979	Oct 1986	2024-03-01	3595
Toyota	Liteace	1.5	Bus	Heckantrieb	Benzin	51	69	Oct 1985	Aug 1989	2024-03-01	3596
Toyota	Land cruiser 80	4.2 TD	Geländewagen geschlossen	Allrad	Diesel	123	167	Jan 1990	Dec 1997	2024-03-01	3597
Toyota	Land cruiser	2.4	Geländewagen geschlossen	Allrad	Benzin	77	105	Nov 1984	May 1993	2024-03-01	3598
Toyota	Land cruiser	2.4	Geländewagen geschlossen	Allrad	Benzin	81	110	Nov 1984	May 1993	2024-03-01	3599
Toyota	Land cruiser	2.4 D	Geländewagen geschlossen	Allrad	Diesel	53	72	Nov 1984	Oct 1985	2024-03-01	3600
Toyota	Land cruiser	2.4 TD	Geländewagen geschlossen	Allrad	Diesel	63	86	Oct 1985	May 1990	2024-03-01	3601
Toyota	Land cruiser	2.4 TD	Geländewagen geschlossen	Allrad	Diesel	66	90	Jan 1990	May 1993	2024-03-01	3602
Toyota	Land cruiser hardtop	2.4 TD	Geländewagen offen	Allrad	Diesel	66	90	Jul 1990	May 1996	2024-03-01	3603
Toyota	Land cruiser	3.0 TD	Geländewagen geschlossen	Allrad	Diesel	92	125	May 1993	May 1996	2024-03-01	3604
Toyota	Land cruiser hardtop	3.0 TD	Geländewagen offen	Allrad	Diesel	92	125	May 1993	May 1996	2024-03-01	3605
Toyota	Land cruiser	4.0 Diesel	Geländewagen geschlossen	Allrad	Diesel	74	101	Jan 1982	Dec 1985	2024-03-01	3606
Toyota	Land cruiser	4.0 Diesel	Geländewagen geschlossen	Allrad	Diesel	76	103	Oct 1982	Dec 1989	2024-03-01	3607
Toyota	Land cruiser	4.0 Turbo-d	Geländewagen geschlossen	Allrad	Diesel	100	136	Oct 1985	Dec 1989	2024-03-01	3608
Toyota	Model f	1.8 DE Luxe	Bus	Heckantrieb	Benzin	58	79	Nov 1982	Aug 1984	2024-03-01	3609
Toyota	Model f	2.0 Super	Bus	Heckantrieb	Benzin	65	88	Aug 1984	Aug 1988	2024-03-01	3610
Toyota	Model f	2	Bus	Heckantrieb	Benzin	66	90	Aug 1988	Jan 1990	2024-03-01	3611
Toyota	Hilux v	2.4 D	Pick-up	Heckantrieb	Diesel	59	80	Oct 1991	Jul 1997	2024-03-01	3612
Toyota	Tercel	1.5 4WD	Schrägheck	Allrad	Benzin	52	71	Oct 1982	Jan 1988	2024-03-01	3613
Toyota	Tercel	1.5 4WD	Schrägheck	Allrad	Benzin	50	68	Sep 1982	Jan 1988	2024-03-01	3614
Toyota	Celica	1.6	Coupe	Frontantrieb	Benzin	77	105	Sep 1989	Dec 1993	2024-03-01	3615
Toyota	Celica	2	Coupe	Frontantrieb	Benzin	115	156	Oct 1989	Jan 1994	2024-03-01	3616
Toyota	Celica	2.0 GTI	Cabriolet	Frontantrieb	Benzin	115	156	Oct 1989	Nov 1993	2024-03-01	3617
Toyota	Celica	2.0 4WD	Coupe	Allrad	Benzin	150	204	Oct 1989	Nov 1993	2024-03-01	3618
Toyota	Celica	2.0 4WD	Coupe	Allrad	Benzin	153	208	Oct 1989	Jan 1994	2024-03-01	3619


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 **Camry I/II/III 的 Sedan、Hatchback、Wagon 共 6 个尺寸组**，并批量关联 17 个 Ktype。各车身形式、门数和三维已按对应代际独立处理。([汽车数据][1])
* 首次闭合 **Alpina B3 GT3 E92、B5 Biturbo F11、Supra A70、MR2 AW11、MR2 SW20、Celica T16 4WD、Celica T18** 共 7 个尺寸组。([汽车数据][2])
* Celica T16 未按代际整体合并：本轮仅确认与输入 `Coupe / 4WD` 边界一致的 Ktype 3581；其余 T16 普通前驱、Schrägheck 和 Cabriolet 分支继续独立核对。
* 未对 Carina、Hiace、Liteace、Hilux、Land Cruiser 等可能存在门数、轴距、车顶或长短车身差异的记录进行猜测性建组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：30
* PENDING 输入 Ktype：70
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3538	3538	Hatchback	Camry I (V10)	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH		READY
3539	3539	Sedan	Camry I (V10)	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH		READY
3540	3540	Sedan	Camry I (V10)	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH		READY
3542	3542	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3543	3543	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	MEDIUM	输入目录结束日期晚于主要车型资料年份，物理车身仍对应V20四门轿车。	READY
3544	3544	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3545	3545	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3546	3546	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3547	3547	Sedan	Camry III (XV10)	XV10	4	EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	HIGH		READY
3548	3548	Sedan	Camry III (XV10)	XV10	4	EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	HIGH		READY
3549	3549	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3550	3550	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	MEDIUM	输入目录结束日期晚于主要车型资料年份，物理车身仍对应V20五门旅行车。	READY
3551	3551	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3552	3552	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3553	3553	Wagon	Camry III Wagon (XV10)	XV10	5	EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	HIGH		READY
3554	3554	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3555	3555	Wagon	Camry III Wagon (XV10)	XV10	5	EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	HIGH		READY
3569	3569	Coupe	B3 Coupe (E92)	E92	2	EU-ALPINA-B3-E92-COUPE-2D-GT3-01	HIGH	GT3专属外廓。	READY
3570	3570	Wagon	B5 Touring (F11)	F11	5	EU-ALPINA-B5-F11-WAGON-5D-BITURBO-01	HIGH		READY
3581	3581	Coupe	Celica IV (T16)	T16	2	EU-TOYOTA-CELICA-IV-T16-COUPE-2D-4WD-01	HIGH	四驱涡轮版长度不同于已核对的普通前驱T16，独立建组。	READY
3585	3585	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	MEDIUM	功率标定存在市场差异，物理外廓为A70三门车身。	READY
3586	3586	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	HIGH		READY
3587	3587	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	MEDIUM	功率标定存在市场差异，物理外廓为A70三门车身。	READY
3588	3588	Coupe	MR2 I (AW11)	AW11	2	EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	HIGH		READY
3589	3589	Coupe	MR2 I (AW11)	AW11	2	EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	HIGH		READY
3590	3590	Targa	MR2 II (SW20)	SW20	2	EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	HIGH	可靠资料将该SW20车身标为Targa。	READY
3615	3615	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH		READY
3616	3616	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH		READY
3618	3618	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH	四驱版本与本代已核对三维一致。	READY
3619	3619	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH	四驱版本与本代已核对三维一致。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370	Auto-Data Toyota Camry I Hatchback (V10) generation specifications	https://www.auto-data.net/en/toyota-camry-i-hatchback-v10-generation-1020
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395	Auto-Data Toyota Camry I (V10) generation specifications	https://www.auto-data.net/en/toyota-camry-i-v10-generation-1019
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400	Auto-Data Toyota Camry II (V20) 1.8 technical specifications	https://www.auto-data.net/en/toyota-camry-ii-v20-1.8-90hp-3939
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415	Auto-Data Toyota Camry III (XV10) 2.2 technical specifications	https://www.auto-data.net/en/toyota-camry-iii-xv10-2.2-136hp-3932
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440	Auto-Data Toyota Camry II Wagon (V20) 2.0 GLi technical specifications	https://www.auto-data.net/en/toyota-camry-ii-wagon-v20-2.0-gli-128hp-3934
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420	Auto-Data Toyota Camry III Wagon (XV10) 2.2 technical specifications	https://www.auto-data.net/en/toyota-camry-iii-wagon-xv10-2.2-136hp-3930
EU-ALPINA-B3-E92-COUPE-2D-GT3-01	4668	1782	1405	Auto-Data Alpina B3 Coupe (E92) GT3 technical specifications	https://www.auto-data.net/en/alpina-b3-coupe-e92-gt3-3.0-408hp-switch-tronic-18321
EU-ALPINA-B5-F11-WAGON-5D-BITURBO-01	4913	1860	1453	Auto-Data Alpina B5 Touring (F11) Biturbo technical specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-4.4-v8-540hp-biturbo-18325
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-4WD-01	4380	1710	1290	Auto-Data Toyota Celica T16 2.0 Turbo 4WD technical specifications	https://www.auto-data.net/en/toyota-celica-t16-2.0-turbo-185hp-4x4-3143
EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	4620	1745	1310	Auto-Data Toyota Supra III A70 3.0 24V; Auto-Data Toyota Supra III A70 3.0 Turbo	https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-24v-190hp-automatic-46697;https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-turbo-235hp-automatic-3458
EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	3925	1665	1250	Auto-Data Toyota MR2 W1 generation specifications	https://www.auto-data.net/en/toyota-mr-2-w1-generation-1001
EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	4140	1695	1240	Auto-Data Toyota MR2 W2 SW20 2.0 16V technical specifications	https://www.auto-data.net/en/toyota-mr-2-w2-2.0-16v-sw20-156hp-automatic-28460
EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	4420	1690	1300	Auto-Data Toyota Celica T18 generation specifications; Auto-Data Toyota Celica T18 2.0 Turbo 4WD technical specifications	https://www.auto-data.net/en/toyota-celica-t18-generation-770;https://www.auto-data.net/en/toyota-celica-t18-2.0-i-16v-turbo-208hp-4wd-3137
```

## 下一步优先处理

1. 闭合 Carina IV/V 的 Sedan、Hatchback、Wagon 物理外廓及 T15/T17 车身代码。
2. 处理 Mazda 323 BD/BF 的 Sedan 与 Hatchback，重点确认门数和不同车身长度。
3. 继续拆分 Celica TA40/TA60、T16 普通前驱与 Cabriolet 分支。
4. 最后处理 Hiace、Liteace、Hilux 和 Land Cruiser 的轴距、门数、软顶/硬顶及长短车身差异。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-camry-i-hatchback-v10-generation-1020 "Toyota Camry I Hatchback (V10) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alpina-b3-coupe-e92-gt3-3.0-408hp-switch-tronic-18321 "Alpina B3 Coupe (E92) GT3 3.0 (408 Hp) Switch-Tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 首次闭合 Mitsubishi Lancer VIII Sportback 五门掀背尺寸组，关联 Ktype `3520`、`3541`、`3560`。汽油与柴油版本外廓一致。([汽车目录][1])
* 首次闭合 Toyota Carina II 第二代 T170 的 Sedan、Hatchback、Wagon 三个尺寸组，批量关联 Ktype `3525–3535`。Sedan 与 Hatchback 虽三维相同，但因车身形式不同分别建组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：44
* PENDING 输入 Ktype：56
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3520	3520	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
3525	3525	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3526	3526	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3527	3527	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3528	3528	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3529	3529	Sedan	Carina II II (T170)	ST171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3530	3530	Hatchback	Carina II II (T170)	ST171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3531	3531	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3532	3532	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3533	3533	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3534	3534	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3535	3535	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3541	3541	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
3560	3560	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	4585	1760	1515	Automobile-Catalog Mitsubishi Lancer Sportback 1.8; Automobile-Catalog Mitsubishi Lancer Sportback 1.8 DI-D ClearTec	https://www.automobile-catalog.com/car/2009/1996220/mitsubishi_lancer_sportback_1_8.html;https://www.automobile-catalog.com/car/2010/1996385/mitsubishi_lancer_sportback_1_8_di-d_cleartec_inform.html
EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	4440	1690	1370	Automobile-Catalog Toyota Carina II Sedan 1.6 XLi	https://www.automobile-catalog.com/car/1990/3547850/toyota_carina_ii_sedan_1_6_xli_automatic.html
EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	4440	1690	1370	Automobile-Catalog Toyota Carina II Liftback 1.6 XLi	https://www.automobile-catalog.com/car/1990/3547895/toyota_carina_ii_liftback_1_6_xli.html
EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	4435	1690	1400	Automobile-Catalog Toyota Carina II Wagon 1.6 XL	https://www.automobile-catalog.com/car/1990/3547700/toyota_carina_ii_wagon_1_6_xl.html
```

## 下一步优先处理

1. 拆分 Carina II T150 改款前后不同长度的 Sedan 与 Hatchback 外廓。
2. 确认 Mazda 323 BD/BF 掀背车型的三门、五门覆盖范围及欧洲市场尺寸冲突。
3. 闭合 Celica TA40、A60 与 T16 普通前驱、Cabriolet 分支。
4. 后续处理 Hiace、Liteace、Hilux 与 Land Cruiser 的轴距、车顶和开闭式车身分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/1996220/mitsubishi_lancer_sportback_1_8.html?utm_source=chatgpt.com "2009 Mitsubishi Lancer Sportback 1.8 Specs Review (105 ..."
[2]: https://www.automobile-catalog.com/car/1990/3547850/toyota_carina_ii_sedan_1_6_xli_automatic.html?utm_source=chatgpt.com "1990 Toyota Carina II Sedan 1.6 XLi automatic (aut. 4)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 首次闭合 Toyota Carina II T15 的普通五门 Liftback、GLi 五门 Liftback、GLi 四门 Sedan 三个物理外廓组，关联 Ktype `3521–3524`。普通版与 GLi 版长度不同，未强制合并。([汽车目录][1])
* 首次闭合 Mazda 323 II BD 的四门 Sedan、三门 Hatchback、五门 Hatchback，以及 Mazda 323 III BF 的四门 Sedan、三门 Hatchback、五门 Hatchback。来源明确标注宽度为不含后视镜。([汽车目录][2])
* Ktype `3558`、`3559`、`3562`、`3564` 覆盖三门和五门实体车身，已按门数拆成派生映射；Ktype `3561` 的 1.1 版本仅建立三门分支。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：56
* READY 映射行：60
* PENDING 输入 Ktype：44
* 已确认尺寸组：26
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3521	3521	Hatchback	Carina II I (T15)	AT151	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	HIGH	普通外廓分支。	READY
3522	3522	Sedan	Carina II I (T15)	ST150	4	EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	HIGH	GLi外廓分支。	READY
3523	3523	Hatchback	Carina II I (T15)	ST150	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	HIGH	GLi外廓分支。	READY
3524	3524	Hatchback	Carina II I (T15)	CT150	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	HIGH	普通外廓分支。	READY
3557	3557	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-01	HIGH		READY
3558_3dr	3558	Hatchback	323 II (BD)	BD105	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3558_5dr	3558	Hatchback	323 II (BD)	BD105	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3559_3dr	3559	Hatchback	323 II (BD)	BD105	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3559_5dr	3559	Hatchback	323 II (BD)	BD105	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3561	3561	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	HIGH		READY
3562_3dr	3562	Hatchback	323 III (BF)	BF103	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3562_5dr	3562	Hatchback	323 III (BF)	BF103	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3563	3563	Sedan	323 III (BF)	BF103	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH		READY
3564_3dr	3564	Hatchback	323 III (BF)	BF5S	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3564_5dr	3564	Hatchback	323 III (BF)	BF5S	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3565	3565	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	4360	1670	1365	Automobile-Catalog Toyota Carina II Liftback 1.6 DX	https://www.automobile-catalog.com/car/1986/3516365/toyota_carina_ii_liftback_1_6_dx.html
EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	4390	1670	1365	Automobile-Catalog Toyota Carina II Sedan 1.8 GLi	https://www.automobile-catalog.com/car/1986/3516440/toyota_carina_ii_sedan_1_8_gli.html
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	4390	1670	1365	Automobile-Catalog Toyota Carina II Liftback 1.8 GLi	https://www.automobile-catalog.com/car/1987/3516200/toyota_carina_ii_liftback_1_8_gli_automatic.html
EU-MAZDA-323-II-BD-SEDAN-4D-01	4155	1630	1375	Automobile-Catalog Mazda 323 1.5 CD Sedan	https://www.automobile-catalog.com/car/1982/1623965/mazda_323_1_5_cd_sedan.html
EU-MAZDA-323-II-BD-HATCHBACK-3D-01	3955	1630	1375	Automobile-Catalog Mazda 323 1.5 GLS 3/5-door	https://www.automobile-catalog.com/car/1982/25730/mazda_323_1500_s.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-01	3955	1630	1375	Automobile-Catalog Mazda 323 1.5 GLS 3/5-door	https://www.automobile-catalog.com/car/1982/25730/mazda_323_1500_s.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390	Automobile-Catalog Mazda 323 1.1 LX three-door	https://www.automobile-catalog.com/car/1986/52025/mazda_323_1_1_lx.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390	Automobile-Catalog Mazda 323 1.5 GLX five-door	https://www.automobile-catalog.com/car/1986/1630010/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390	Automobile-Catalog Mazda 323 1.5 GLX Sedan	https://www.automobile-catalog.com/car/1985/1630220/mazda_323_1_5_glx_sedan.html
```

## 5. 下一步优先处理

1. 闭合 Celica A40、A60、T16 普通前驱及 Cabriolet 分支。
2. 处理 Toyota Tercel、Crown 与 Celica Supra A60。
3. 处理 Hiace、Liteace、Model F 的轴距和车顶分支。
4. 最后集中处理 Hilux 与 Land Cruiser 的长短轴、开闭式车身和车顶差异。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/3516200/toyota_carina_ii_liftback_1_8_gli_automatic.html?utm_source=chatgpt.com "1987 Toyota Carina II Liftback 1.8 GLi automatic Specs Review (74 kW / 101 PS / 99 hp) (up to December 1987 for Europe )"
[2]: https://www.automobile-catalog.com/car/1982/1623965/mazda_323_1_5_cd_sedan.html?utm_source=chatgpt.com "1982 Mazda 323 1.5 CD Sedan Specs Review (55 kW / 75 PS / 74 hp) (up to December 1982 for Europe )"
[3]: https://www.automobile-catalog.com/car/1982/25730/mazda_323_1500_s.html?utm_source=chatgpt.com "1982 Mazda 323 1.5 GLS Specs Review (55 kW / 75 PS / 74 hp) (up to December 1982 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* Ktype `3536` 的生产区间跨越 BMW E91 旅行车改款，已拆分为改款前和改款后两个物理外廓；同时闭合 Toyota Crown S110 与 Celica A60 Liftback 尺寸组。([汽车数据][1])
* 闭合 Celica T16 的前驱三门掀背、前驱二门 Coupe、Cabriolet 三种外廓；Ktype `3581` 修正为 ST165 四驱三门掀背，不再按二门 Coupe 映射。([汽车数据][2])
* Ktype `3591` 按 Celica Supra A60 早期窄体和后期宽体拆分；同时闭合 Tercel AL25 四驱旅行车及 Celica T18 Cabriolet。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：70
* READY 映射行：76
* PENDING 输入 Ktype：30
* 已确认尺寸组：37
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3536_prefl	3536	Wagon	3 Series Touring (E91)	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	MEDIUM	输入生产区间跨越2008年外观改款；改款前物理外廓。	READY
3536_facelift	3536	Wagon	3 Series Touring (E91 LCI)	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	MEDIUM	输入生产区间跨越2008年外观改款；改款后物理外廓。	READY
3556	3556	Sedan	Crown VI (S110)	MS112	4	EU-TOYOTA-CROWN-VI-S110-SEDAN-4D-01	HIGH		READY
3576	3576	Hatchback	Celica III (A60)	RA61	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH		READY
3577	3577	Hatchback	Celica IV (T16)	AT160	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3578	3578	Hatchback	Celica IV (T16)	ST162	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3579	3579	Hatchback	Celica IV (T16)	AT160	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3580	3580	Hatchback	Celica IV (T16)	ST162	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3581	3581	Hatchback	Celica IV (T16)	ST165	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	HIGH	四驱涡轮三门掀背外廓；修正原二门Coupe映射。	READY
3582	3582	Coupe	Celica IV (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	HIGH	二门折背Coupe物理外廓。	READY
3583	3583	Convertible	Celica Cabrio (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	HIGH		READY
3584	3584	Convertible	Celica Cabrio (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	HIGH		READY
3591_narrow	3591	Hatchback	Celica Supra II (A60)	MA61	3	EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	MEDIUM	早期窄体物理分支。	READY
3591_wide	3591	Hatchback	Celica Supra II (A60)	MA61	3	EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	MEDIUM	后期宽体物理分支。	READY
3613	3613	Wagon	Tercel II 4WD (L20)	AL25	5	EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	HIGH	五门四驱旅行车物理外廓。	READY
3614	3614	Wagon	Tercel II 4WD (L20)	AL25	5	EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	MEDIUM	五门四驱旅行车物理外廓。	READY
3617	3617	Convertible	Celica Cabrio (T18)	ST182	2	EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	MEDIUM		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data BMW 3 Series Touring E91 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-325i-218hp-9945
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-325i-218hp-17216
EU-TOYOTA-CROWN-VI-S110-SEDAN-4D-01	4860	1715	1430	Automobile-Catalog Toyota Crown 2.8 Super Saloon	https://www.automobile-catalog.com/car/1980/45650/toyota_crown_i.html
EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	4450	1665	1320	Automobile-Catalog Toyota Celica 2000 XT Liftback	https://www.automobile-catalog.com/car/1982/50210/toyota_celica_xt_liftback.html
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	4365	1710	1290	Auto-Data Toyota Celica T16 2.0 GTi	https://www.auto-data.net/en/toyota-celica-t16-2.0-gti-140hp-3142
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	4380	1710	1290	Auto-Data Toyota Celica T16 2.0 Turbo 4x4	https://www.auto-data.net/en/toyota-celica-t16-2.0-turbo-185hp-4x4-3143
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	4410	1710	1290	Automobile-Catalog Toyota Celica fourth-generation export Coupe	https://www.automobile-catalog.com/make/toyota/celica_4gen/celica_4_export_coupe/1986.html
EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	4410	1690	1320	Automobile-Catalog Toyota Celica 2.0 GT Cabrio	https://www.automobile-catalog.com/car/1988/3520040/toyota_celica_2_0_gt_cabrio.html
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	4620	1685	1315	Automobile-Catalog Toyota Celica Supra 2.8i narrow body	https://www.automobile-catalog.com/car/1982/3504725/toyota_celica_supra_2_8i.html
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	4620	1720	1315	Automobile-Catalog Toyota Celica Supra 2.8i wide body	https://www.automobile-catalog.com/car/1983/3504770/toyota_celica_supra_2_8i_wide.html
EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	4175	1615	1510	Automobile-Catalog Toyota Tercel 4WD	https://www.automobile-catalog.com/car/1983/25535/toyota_tercel_4wd.html
EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	4430	1705	1320	ADAC Toyota Celica Cabrio 2.0 GTi	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/toyota/celica/t18/348676/
```

## 5. 下一步优先处理

1. 闭合 Ktype `3537` 的 Tercel 多代际、两驱掀背物理分支。
2. 处理 Celica A40 的 Coupe 与 Liftback，以及剩余 A60/T16 边界。
3. 闭合 Hiace、Liteace、Model F 的轴距、车顶和厢式/客车分支。
4. 集中处理 Hilux V 与 Land Cruiser 40/70/80 系列的长短轴、硬顶、软顶及车门差异。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-3-series-touring-e91-325i-218hp-9945?utm_source=chatgpt.com "Specs of BMW 3 Series Touring (E91) 325i (218 Hp) /2005 ..."
[2]: https://www.auto-data.net/en/toyota-celica-t16-2.0-gti-140hp-3142?utm_source=chatgpt.com "Toyota Celica (T16) 2.0 GTi (140 Hp) /Coupe 1988"
[3]: https://www.automobile-catalog.com/car/1982/3504725/toyota_celica_supra_2_8i.html?utm_source=chatgpt.com "1982 Toyota Celica Supra 2.8i Specs Review (125 kW / 170 PS / 168 hp) (since June 1982 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 Toyota Celica II（A40/A50）早期与后期改款的 Coupe、1600 Liftback、2000 XT Liftback 和 2000 GT Liftback，共新增 8 个尺寸组。
* Ktype `3566`、`3567`、`3568`、`3571`、`3572`、`3574`、`3575` 的生产区间跨越 1980 年初的 Phase I／Phase II 外廓变化，已拆分为 `prefl` 与 `facelift`；Ktype `3573` 仅对应 Phase II。
* Phase II 相比 Phase I 主要表现为车长由 4330 mm 增至 4370 mm；Coupe、1600 Liftback、2000 XT 和 2000 GT 的宽度及高度边界分别保留，没有因同代车型而强制合并。([汽车目录][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：78
* READY 映射行：91
* PENDING 输入 Ktype：22
* 已确认尺寸组：45
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3566_prefl	3566	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3566_facelift	3566	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3567_prefl	3567	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	HIGH	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3567_facelift	3567	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3568_prefl	3568	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	HIGH	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3568_facelift	3568	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3571_prefl	3571	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3571_facelift	3571	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3572_prefl	3572	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3572_facelift	3572	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3573	3573	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	HIGH	Phase II 2000 XT外廓。	READY
3574_prefl	3574	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3574_facelift	3574	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3575_prefl	3575	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3575_facelift	3575	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	4330	1635	1320	Automobile-Catalog Toyota Celica Coupe 1600 ST Phase I Europe	https://www.automobile-catalog.com/car/1978/3493220/toyota_celica_coupe_1600_st.html
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	4370	1635	1320	Automobile-Catalog Toyota Celica Coupe 1600 LT Phase II Europe; Automobile-Catalog Toyota Celica Coupe 1600 ST Phase II Europe	https://www.automobile-catalog.com/car/1980/3493415/toyota_celica_coupe_1600_lt.html;https://www.automobile-catalog.com/car/1980/3493445/toyota_celica_coupe_1600_st.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	4330	1635	1310	Automobile-Catalog Toyota Celica Liftback 1600 ST Phase I Europe	https://www.automobile-catalog.com/car/1978/3493265/toyota_celica_liftback_1600_st_5-speed.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	4370	1635	1310	Automobile-Catalog Toyota Celica Liftback 1600 ST Phase II Europe	https://www.automobile-catalog.com/car/1980/3493475/toyota_celica_liftback_1600_st.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	4330	1640	1320	Automobile-Catalog Toyota Celica Liftback 2000 XT Phase I Europe	https://www.automobile-catalog.com/car/1978/3493310/toyota_celica_liftback_2000_xt.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	4370	1640	1320	Automobile-Catalog Toyota Celica Liftback 2000 XT Phase II Europe	https://www.automobile-catalog.com/car/1980/3493520/toyota_celica_liftback_2000_xt_automatic.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	4330	1640	1315	Automobile-Catalog Toyota Celica Liftback 2000 GT Phase I Europe	https://www.automobile-catalog.com/car/1978/28655/toyota_celica_2000_gt.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	4370	1640	1315	Automobile-Catalog Toyota Celica Liftback 2000 GT Phase II Europe	https://www.automobile-catalog.com/car/1980/3493490/toyota_celica_liftback_2000_gt.html
```

## 5. 下一步优先处理

1. 拆分 Ktype `3537` 覆盖的 Tercel L10 与后续车身分支。
2. 闭合 Hiace II、Hiace III、LiteAce 与 Model F 的车长、车顶和客货车边界。
3. 处理 Hilux V 的驾驶室与货斗分支。
4. 最后集中闭合 Land Cruiser 40、70、80 系列的短轴、长轴、硬顶及开放式车身。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/3493220/toyota_celica_coupe_1600_st.html?utm_source=chatgpt.com "1978 Toyota Celica Coupe 1600 ST Specs Review (63 kW / 86 PS / 84 hp) (for Europe export)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 闭合 Ktype `3537`：按 Tercel L10 改款前、L10 改款后，以及 L20 三门、五门拆成四个物理分支。
* 闭合 Hiace II/III：Ktype `3592–3594` 均明确覆盖短轴与长轴车身，按 RH20/RH30、YH51/YH61、LH51/LH61 分支建立关联。
* 闭合 LiteAce `3595–3596`：`3595` 对应 M20 厢式车；`3596` 的生产区间跨越 1989 年欧洲版外廓变化，拆为改款前后。
* 闭合 Model F `3609–3611`：YR20 与 YR21 发动机版本复用同一四门 MPV 尺寸组。([汽车目录][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：87
* READY 映射行：107
* PENDING 输入 Ktype：13
* 已确认尺寸组：57
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3537_l10_prefl	3537	Hatchback	Tercel I (L10)	AL11	3	EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-PREFL-01	MEDIUM	L10改款前三门掀背物理分支。	READY
3537_l10_facelift	3537	Hatchback	Tercel I (L10)	AL11	3	EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-FACELIFT-01	MEDIUM	L10改款后三门掀背物理分支。	READY
3537_l20_3dr	3537	Hatchback	Tercel II (L20)	AL20	3	EU-TOYOTA-TERCEL-II-L20-HATCHBACK-3D-01	MEDIUM	L20三门物理分支。	READY
3537_l20_5dr	3537	Hatchback	Tercel II (L20)	AL20	5	EU-TOYOTA-TERCEL-II-L20-HATCHBACK-5D-01	MEDIUM	L20五门物理分支。	READY
3592_swb	3592	MPV	Hiace II (H20/H30)	RH20	4	EU-TOYOTA-HIACE-II-H20-MPV-4D-SWB-01	MEDIUM	RH20短轴客车分支。	READY
3592_lwb	3592	MPV	Hiace II (H20/H30)	RH30	4	EU-TOYOTA-HIACE-II-H30-MPV-4D-LWB-01	MEDIUM	RH30长轴客车分支。	READY
3593_swb	3593	MPV	Hiace III (H50/H60)	YH51	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	MEDIUM	YH51短轴客车分支。	READY
3593_lwb	3593	MPV	Hiace III (H50/H60)	YH61	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	MEDIUM	YH61长轴客车分支。	READY
3594_swb	3594	MPV	Hiace III (H50/H60)	LH51	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	MEDIUM	LH51短轴客车分支。	READY
3594_lwb	3594	MPV	Hiace III (H50/H60)	LH61	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	MEDIUM	LH61长轴客车分支。	READY
3595	3595	Van	LiteAce II (M20)	KM20V	4	EU-TOYOTA-LITEACE-II-M20-VAN-4D-01	HIGH		READY
3596_prefl	3596	MPV	LiteAce III (M30)	KM30G	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	MEDIUM	1989年中期改款前外廓。	READY
3596_facelift	3596	MPV	LiteAce III (M30)	KM30G	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	MEDIUM	1989年中期改款后外廓。	READY
3609	3609	MPV	Model F (R20)	YR20	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
3610	3610	MPV	Model F (R20)	YR21	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
3611	3611	MPV	Model F (R20)	YR21	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-PREFL-01	3960	1550	1370	Automobile-Catalog Toyota Tercel Liftback Coupe Phase I Europe	https://www.automobile-catalog.com/car/1979/45515/toyota_tercel_liftback_coupe.html
EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-FACELIFT-01	3980	1550	1370	Automobile-Catalog Toyota Tercel Liftback Coupe facelift Europe	https://www.automobile-catalog.com/car/1981/3481670/toyota_tercel_liftback_coupe_5-speed.html
EU-TOYOTA-TERCEL-II-L20-HATCHBACK-3D-01	3880	1615	1390	Automobile-Catalog Toyota Tercel 1.3 DX Europe	https://www.automobile-catalog.com/car/1982/29555/toyota_tercel_1_3.html
EU-TOYOTA-TERCEL-II-L20-HATCHBACK-5D-01	3880	1615	1390	Automobile-Catalog Toyota Tercel 1.3 DX Europe	https://www.automobile-catalog.com/car/1982/29555/toyota_tercel_1_3.html
EU-TOYOTA-HIACE-II-H20-MPV-4D-SWB-01	4340	1690	1925	Toyota 75 Years Hiace second-generation specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/index.html
EU-TOYOTA-HIACE-II-H30-MPV-4D-LWB-01	4690	1690	1920	Toyota 75 Years Hiace second-generation specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/index.html
EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	4425	1690	1890	Toyota 75 Years Hiace third-generation specifications; Drom Toyota Hiace YH51 Short Base Commuter	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html;https://www.drom.ru/catalog/toyota/hiace/319660/
EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	4690	1690	1890	Toyota 75 Years Hiace third-generation specifications; Drom Toyota Hiace YH61 nine-seat body	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html;https://www.drom.ru/catalog/toyota/hiace/319428/
EU-TOYOTA-LITEACE-II-M20-VAN-4D-01	3900	1625	1765	Toyota 75 Years LiteAce second-generation van specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015748/index.html
EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	4000	1650	1910	Automobile-Catalog Toyota Lite Ace 1.5 Combi Europe	https://www.automobile-catalog.com/car/1986/3606200/toyota_lite_ace_1_5_combi.html
EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	3995	1650	1900	Automobile-Catalog Toyota Lite Ace 1.5 Combi facelift Europe	https://www.automobile-catalog.com/car/1989/3606260/toyota_lite_ace_1_5_combi.html
EU-TOYOTA-MODEL-F-R20-MPV-4D-01	4285	1670	1815	Automobile-Catalog Toyota Model F Space Cruiser 1.8; Automobile-Catalog Toyota Model F Space Cruiser 2.0	https://www.automobile-catalog.com/car/1984/31130/toyota_f_1_8.html;https://www.automobile-catalog.com/car/1985/56135/toyota_f_2_0.html
```

## 5. 下一步优先处理

1. 闭合 Ktype `3597` 的 Land Cruiser 80 标准车身。
2. 集中拆分 Ktype `3598–3605` 的 Land Cruiser 70 短轴、长轴、硬顶及开放式车身。
3. 闭合 Ktype `3606–3608` 的 Land Cruiser 60 普通柴油与涡轮柴油外廓。
4. 最后处理 Ktype `3612` Hilux V 的单排、加长驾驶室及货斗分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/45515/toyota_tercel_liftback_coupe.html?utm_source=chatgpt.com "1980 Toyota Tercel Liftback (Coupe) Specs Review (48 kW / 65 PS / 64 hp) (up to late-year 1980 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 恢复已完成回复 ---
## 更新点

* 已闭合剩余 13 个 Ktype，新增 20 行映射和 10 个尺寸组，覆盖 Land Cruiser 80、70、60 系列及 Hilux V 的不同车身分支。Toyota 官方资料确认 HDJ81V 为 `4820 × 1900 × 1900 mm`，并明确 Prado 70 存在三门短轴和五门长轴车身。([丰田官网][1])
* Land Cruiser 70 的 LJ70/KZJ70、LJ73 以及 Land Cruiser 60 柴油和涡轮柴油外廓已分别闭合；Hilux V 按 Regular Cab、Double Cab、Xtracab 拆分。([汽车数据][2])
* 已完成一次机械收尾检查：固定表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、所有引用闭合、尺寸与来源完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：127
* PENDING：0
* DIMENSION_GROUP：67
* 机械检查：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3520	3520	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
3521	3521	Hatchback	Carina II I (T15)	AT151	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	HIGH	普通外廓分支。	READY
3522	3522	Sedan	Carina II I (T15)	ST150	4	EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	HIGH	GLi外廓分支。	READY
3523	3523	Hatchback	Carina II I (T15)	ST150	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	HIGH	GLi外廓分支。	READY
3524	3524	Hatchback	Carina II I (T15)	CT150	5	EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	HIGH	普通外廓分支。	READY
3525	3525	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3526	3526	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3527	3527	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3528	3528	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3529	3529	Sedan	Carina II II (T170)	ST171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3530	3530	Hatchback	Carina II II (T170)	ST171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3531	3531	Sedan	Carina II II (T170)	AT171	4	EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	HIGH		READY
3532	3532	Hatchback	Carina II II (T170)	AT171	5	EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	HIGH		READY
3533	3533	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3534	3534	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3535	3535	Wagon	Carina II II (T170)	AT171G	5	EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	HIGH		READY
3536_prefl	3536	Wagon	3 Series Touring (E91)	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	MEDIUM	输入生产区间跨越2008年外观改款；改款前物理外廓。	READY
3536_facelift	3536	Wagon	3 Series Touring (E91 LCI)	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	MEDIUM	输入生产区间跨越2008年外观改款；改款后物理外廓。	READY
3537_l10_prefl	3537	Hatchback	Tercel I (L10)	AL11	3	EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-PREFL-01	MEDIUM	L10改款前三门掀背物理分支。	READY
3537_l10_facelift	3537	Hatchback	Tercel I (L10)	AL11	3	EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-FACELIFT-01	MEDIUM	L10改款后三门掀背物理分支。	READY
3537_l20_3dr	3537	Hatchback	Tercel II (L20)	AL20	3	EU-TOYOTA-TERCEL-II-L20-HATCHBACK-3D-01	MEDIUM	L20三门物理分支。	READY
3537_l20_5dr	3537	Hatchback	Tercel II (L20)	AL20	5	EU-TOYOTA-TERCEL-II-L20-HATCHBACK-5D-01	MEDIUM	L20五门物理分支。	READY
3538	3538	Hatchback	Camry I (V10)	V10	5	EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	HIGH		READY
3539	3539	Sedan	Camry I (V10)	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH		READY
3540	3540	Sedan	Camry I (V10)	V10	4	EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	HIGH		READY
3541	3541	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
3542	3542	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3543	3543	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	MEDIUM	输入目录结束日期晚于主要车型资料年份，物理车身仍对应V20四门轿车。	READY
3544	3544	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3545	3545	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3546	3546	Sedan	Camry II (V20)	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	HIGH		READY
3547	3547	Sedan	Camry III (XV10)	XV10	4	EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	HIGH		READY
3548	3548	Sedan	Camry III (XV10)	XV10	4	EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	HIGH		READY
3549	3549	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3550	3550	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	MEDIUM	输入目录结束日期晚于主要车型资料年份，物理车身仍对应V20五门旅行车。	READY
3551	3551	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3552	3552	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3553	3553	Wagon	Camry III Wagon (XV10)	XV10	5	EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	HIGH		READY
3554	3554	Wagon	Camry II Wagon (V20)	V20	5	EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	HIGH		READY
3555	3555	Wagon	Camry III Wagon (XV10)	XV10	5	EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	HIGH		READY
3556	3556	Sedan	Crown VI (S110)	MS112	4	EU-TOYOTA-CROWN-VI-S110-SEDAN-4D-01	HIGH		READY
3557	3557	Sedan	323 II (BD)	BD	4	EU-MAZDA-323-II-BD-SEDAN-4D-01	HIGH		READY
3558_3dr	3558	Hatchback	323 II (BD)	BD105	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3558_5dr	3558	Hatchback	323 II (BD)	BD105	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3559_3dr	3559	Hatchback	323 II (BD)	BD105	3	EU-MAZDA-323-II-BD-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3559_5dr	3559	Hatchback	323 II (BD)	BD105	5	EU-MAZDA-323-II-BD-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3560	3560	Hatchback	Lancer VIII Sportback	CX_A	5	EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	HIGH		READY
3561	3561	Hatchback	323 III (BF)	BF	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	HIGH		READY
3562_3dr	3562	Hatchback	323 III (BF)	BF103	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3562_5dr	3562	Hatchback	323 III (BF)	BF103	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3563	3563	Sedan	323 III (BF)	BF103	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH		READY
3564_3dr	3564	Hatchback	323 III (BF)	BF5S	3	EU-MAZDA-323-III-BF-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
3564_5dr	3564	Hatchback	323 III (BF)	BF5S	5	EU-MAZDA-323-III-BF-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
3565	3565	Sedan	323 III (BF)	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH		READY
3566_prefl	3566	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3566_facelift	3566	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3567_prefl	3567	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	HIGH	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3567_facelift	3567	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3568_prefl	3568	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	HIGH	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3568_facelift	3568	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	HIGH	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3569	3569	Coupe	B3 Coupe (E92)	E92	2	EU-ALPINA-B3-E92-COUPE-2D-GT3-01	HIGH	GT3专属外廓。	READY
3570	3570	Wagon	B5 Touring (F11)	F11	5	EU-ALPINA-B5-F11-WAGON-5D-BITURBO-01	HIGH		READY
3571_prefl	3571	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3571_facelift	3571	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3572_prefl	3572	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3572_facelift	3572	Coupe	Celica II (A40/A50)		2	EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3573	3573	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	HIGH	Phase II 2000 XT外廓。	READY
3574_prefl	3574	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3574_facelift	3574	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3575_prefl	3575	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	MEDIUM	生产区间跨越Phase I与Phase II；改款前外廓。	READY
3575_facelift	3575	Hatchback	Celica II (A40/A50)		3	EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	MEDIUM	生产区间跨越Phase I与Phase II；改款后外廓。	READY
3576	3576	Hatchback	Celica III (A60)	RA61	3	EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	HIGH		READY
3577	3577	Hatchback	Celica IV (T16)	AT160	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3578	3578	Hatchback	Celica IV (T16)	ST162	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3579	3579	Hatchback	Celica IV (T16)	AT160	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3580	3580	Hatchback	Celica IV (T16)	ST162	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	HIGH		READY
3581	3581	Hatchback	Celica IV (T16)	ST165	3	EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	HIGH	四驱涡轮三门掀背外廓；修正原二门Coupe映射。	READY
3582	3582	Coupe	Celica IV (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	HIGH	二门折背Coupe物理外廓。	READY
3583	3583	Convertible	Celica Cabrio (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	HIGH		READY
3584	3584	Convertible	Celica Cabrio (T16)	ST162	2	EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	HIGH		READY
3585	3585	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	MEDIUM	功率标定存在市场差异，物理外廓为A70三门车身。	READY
3586	3586	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	HIGH		READY
3587	3587	Coupe	Supra III (A70)	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	MEDIUM	功率标定存在市场差异，物理外廓为A70三门车身。	READY
3588	3588	Coupe	MR2 I (AW11)	AW11	2	EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	HIGH		READY
3589	3589	Coupe	MR2 I (AW11)	AW11	2	EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	HIGH		READY
3590	3590	Targa	MR2 II (SW20)	SW20	2	EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	HIGH	可靠资料将该SW20车身标为Targa。	READY
3591_narrow	3591	Hatchback	Celica Supra II (A60)	MA61	3	EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	MEDIUM	早期窄体物理分支。	READY
3591_wide	3591	Hatchback	Celica Supra II (A60)	MA61	3	EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	MEDIUM	后期宽体物理分支。	READY
3592_swb	3592	MPV	Hiace II (H20/H30)	RH20	4	EU-TOYOTA-HIACE-II-H20-MPV-4D-SWB-01	MEDIUM	RH20短轴客车分支。	READY
3592_lwb	3592	MPV	Hiace II (H20/H30)	RH30	4	EU-TOYOTA-HIACE-II-H30-MPV-4D-LWB-01	MEDIUM	RH30长轴客车分支。	READY
3593_swb	3593	MPV	Hiace III (H50/H60)	YH51	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	MEDIUM	YH51短轴客车分支。	READY
3593_lwb	3593	MPV	Hiace III (H50/H60)	YH61	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	MEDIUM	YH61长轴客车分支。	READY
3594_swb	3594	MPV	Hiace III (H50/H60)	LH51	4	EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	MEDIUM	LH51短轴客车分支。	READY
3594_lwb	3594	MPV	Hiace III (H50/H60)	LH61	4	EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	MEDIUM	LH61长轴客车分支。	READY
3595	3595	Van	LiteAce II (M20)	KM20V	4	EU-TOYOTA-LITEACE-II-M20-VAN-4D-01	HIGH		READY
3596_prefl	3596	MPV	LiteAce III (M30)	KM30G	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	MEDIUM	1989年中期改款前外廓。	READY
3596_facelift	3596	MPV	LiteAce III (M30)	KM30G	4	EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	MEDIUM	1989年中期改款后外廓。	READY
3597	3597	SUV	Land Cruiser 80	HDJ81	5	EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	HIGH		READY
3598_swb	3598	SUV	Land Cruiser 70	RJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	MEDIUM	短轴三门物理分支。	READY
3598_mwb	3598	SUV	Land Cruiser 70	RJ73	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	MEDIUM	中轴三门物理分支。	READY
3599_swb	3599	SUV	Land Cruiser 70	RJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	MEDIUM	短轴三门物理分支。	READY
3599_mwb	3599	SUV	Land Cruiser 70	RJ73	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	MEDIUM	中轴三门物理分支。	READY
3600	3600	SUV	Land Cruiser 70	LJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	HIGH		READY
3601_swb	3601	SUV	Land Cruiser 70	LJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	MEDIUM	短轴三门物理分支。	READY
3601_mwb	3601	SUV	Land Cruiser 70	LJ73	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	MEDIUM	中轴三门物理分支。	READY
3602	3602	SUV	Land Cruiser 70	LJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	HIGH		READY
3603	3603	Convertible	Land Cruiser 70 Hardtop	LJ70	2	EU-TOYOTA-LAND-CRUISER-70-CONVERTIBLE-2D-SWB-HARDTOP-01	MEDIUM	短轴可拆硬顶开放式车身。	READY
3604_swb	3604	SUV	Land Cruiser Prado 70	KZJ70	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	MEDIUM	短轴三门物理分支。	READY
3604_mwb	3604	SUV	Land Cruiser 70	KZJ73	3	EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	MEDIUM	中轴三门物理分支。	READY
3604_lwb	3604	SUV	Land Cruiser Prado 70	KZJ78	5	EU-TOYOTA-LAND-CRUISER-PRADO-70-SUV-5D-LWB-01	MEDIUM	长轴五门物理分支。	READY
3605	3605	Convertible	Land Cruiser 70 Hardtop	KZJ70	2	EU-TOYOTA-LAND-CRUISER-70-CONVERTIBLE-2D-SWB-HARDTOP-01	MEDIUM	短轴可拆硬顶开放式车身。	READY
3606	3606	SUV	Land Cruiser 60	HJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	HIGH		READY
3607	3607	SUV	Land Cruiser 60	HJ60	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	HIGH		READY
3608	3608	SUV	Land Cruiser 60	HJ61	5	EU-TOYOTA-LAND-CRUISER-60-SUV-5D-TURBODIESEL-01	HIGH		READY
3609	3609	MPV	Model F (R20)	YR20	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
3610	3610	MPV	Model F (R20)	YR21	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
3611	3611	MPV	Model F (R20)	YR21	4	EU-TOYOTA-MODEL-F-R20-MPV-4D-01	HIGH		READY
3612_regularcab	3612	Pickup	Hilux V	LN85	2	EU-TOYOTA-HILUX-V-PICKUP-2D-REGULARCAB-01	MEDIUM	单排短轴驾驶室物理分支。	READY
3612_doublecab	3612	Pickup	Hilux V	LN85	4	EU-TOYOTA-HILUX-V-PICKUP-4D-DOUBLECAB-01	MEDIUM	双排四门驾驶室物理分支。	READY
3612_xtracab	3612	Pickup	Hilux V	LN90	2	EU-TOYOTA-HILUX-V-PICKUP-2D-XTRACAB-01	MEDIUM	加长驾驶室物理分支。	READY
3613	3613	Wagon	Tercel II 4WD (L20)	AL25	5	EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	HIGH	五门四驱旅行车物理外廓。	READY
3614	3614	Wagon	Tercel II 4WD (L20)	AL25	5	EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	MEDIUM	五门四驱旅行车物理外廓。	READY
3615	3615	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH		READY
3616	3616	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH		READY
3617	3617	Convertible	Celica Cabrio (T18)	ST182	2	EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	MEDIUM		READY
3618	3618	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH	四驱版本与本代已核对三维一致。	READY
3619	3619	Coupe	Celica V (T18)	T18	3	EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	HIGH	四驱版本与本代已核对三维一致。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3401-3500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	4585	1760	1515	Automobile-Catalog Mitsubishi Lancer Sportback 1.8; Automobile-Catalog Mitsubishi Lancer Sportback 1.8 DI-D ClearTec	https://www.automobile-catalog.com/car/2009/1996220/mitsubishi_lancer_sportback_1_8.html;https://www.automobile-catalog.com/car/2010/1996385/mitsubishi_lancer_sportback_1_8_di-d_cleartec_inform.html
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-STD-01	4360	1670	1365	Automobile-Catalog Toyota Carina II Liftback 1.6 DX	https://www.automobile-catalog.com/car/1986/3516365/toyota_carina_ii_liftback_1_6_dx.html
EU-TOYOTA-CARINA-II-T15-SEDAN-4D-GLI-01	4390	1670	1365	Automobile-Catalog Toyota Carina II Sedan 1.8 GLi	https://www.automobile-catalog.com/car/1986/3516440/toyota_carina_ii_sedan_1_8_gli.html
EU-TOYOTA-CARINA-II-T15-HATCHBACK-5D-GLI-01	4390	1670	1365	Automobile-Catalog Toyota Carina II Liftback 1.8 GLi	https://www.automobile-catalog.com/car/1987/3516200/toyota_carina_ii_liftback_1_8_gli_automatic.html
EU-TOYOTA-CARINA-II-T170-SEDAN-4D-01	4440	1690	1370	Automobile-Catalog Toyota Carina II Sedan 1.6 XLi	https://www.automobile-catalog.com/car/1990/3547850/toyota_carina_ii_sedan_1_6_xli_automatic.html
EU-TOYOTA-CARINA-II-T170-HATCHBACK-5D-01	4440	1690	1370	Automobile-Catalog Toyota Carina II Liftback 1.6 XLi	https://www.automobile-catalog.com/car/1990/3547895/toyota_carina_ii_liftback_1_6_xli.html
EU-TOYOTA-CARINA-II-T170-WAGON-5D-01	4435	1690	1400	Automobile-Catalog Toyota Carina II Wagon 1.6 XL	https://www.automobile-catalog.com/car/1990/3547700/toyota_carina_ii_wagon_1_6_xl.html
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data BMW 3 Series Touring E91 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-325i-218hp-9945
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-325i-218hp-17216
EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-PREFL-01	3960	1550	1370	Automobile-Catalog Toyota Tercel Liftback Coupe Phase I Europe	https://www.automobile-catalog.com/car/1979/45515/toyota_tercel_liftback_coupe.html
EU-TOYOTA-TERCEL-I-L10-HATCHBACK-3D-FACELIFT-01	3980	1550	1370	Automobile-Catalog Toyota Tercel Liftback Coupe facelift Europe	https://www.automobile-catalog.com/car/1981/3481670/toyota_tercel_liftback_coupe_5-speed.html
EU-TOYOTA-TERCEL-II-L20-HATCHBACK-3D-01	3880	1615	1390	Automobile-Catalog Toyota Tercel 1.3 DX Europe	https://www.automobile-catalog.com/car/1982/29555/toyota_tercel_1_3.html
EU-TOYOTA-TERCEL-II-L20-HATCHBACK-5D-01	3880	1615	1390	Automobile-Catalog Toyota Tercel 1.3 DX Europe	https://www.automobile-catalog.com/car/1982/29555/toyota_tercel_1_3.html
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370	Auto-Data Toyota Camry I Hatchback (V10) generation specifications	https://www.auto-data.net/en/toyota-camry-i-hatchback-v10-generation-1020
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395	Auto-Data Toyota Camry I (V10) generation specifications	https://www.auto-data.net/en/toyota-camry-i-v10-generation-1019
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400	Auto-Data Toyota Camry II (V20) 1.8 technical specifications	https://www.auto-data.net/en/toyota-camry-ii-v20-1.8-90hp-3939
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415	Auto-Data Toyota Camry III (XV10) 2.2 technical specifications	https://www.auto-data.net/en/toyota-camry-iii-xv10-2.2-136hp-3932
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440	Auto-Data Toyota Camry II Wagon (V20) 2.0 GLi technical specifications	https://www.auto-data.net/en/toyota-camry-ii-wagon-v20-2.0-gli-128hp-3934
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420	Auto-Data Toyota Camry III Wagon (XV10) 2.2 technical specifications	https://www.auto-data.net/en/toyota-camry-iii-wagon-xv10-2.2-136hp-3930
EU-TOYOTA-CROWN-VI-S110-SEDAN-4D-01	4860	1715	1430	Automobile-Catalog Toyota Crown 2.8 Super Saloon	https://www.automobile-catalog.com/car/1980/45650/toyota_crown_i.html
EU-MAZDA-323-II-BD-SEDAN-4D-01	4155	1630	1375	Automobile-Catalog Mazda 323 1.5 CD Sedan	https://www.automobile-catalog.com/car/1982/1623965/mazda_323_1_5_cd_sedan.html
EU-MAZDA-323-II-BD-HATCHBACK-3D-01	3955	1630	1375	Automobile-Catalog Mazda 323 1.5 GLS 3/5-door	https://www.automobile-catalog.com/car/1982/25730/mazda_323_1500_s.html
EU-MAZDA-323-II-BD-HATCHBACK-5D-01	3955	1630	1375	Automobile-Catalog Mazda 323 1.5 GLS 3/5-door	https://www.automobile-catalog.com/car/1982/25730/mazda_323_1500_s.html
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390	Automobile-Catalog Mazda 323 1.1 LX three-door	https://www.automobile-catalog.com/car/1986/52025/mazda_323_1_1_lx.html
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390	Automobile-Catalog Mazda 323 1.5 GLX five-door	https://www.automobile-catalog.com/car/1986/1630010/mazda_323_1_5_glx.html
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390	Automobile-Catalog Mazda 323 1.5 GLX Sedan	https://www.automobile-catalog.com/car/1985/1630220/mazda_323_1_5_glx_sedan.html
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-PREFL-01	4330	1635	1320	Automobile-Catalog Toyota Celica Coupe 1600 ST Phase I Europe	https://www.automobile-catalog.com/car/1978/3493220/toyota_celica_coupe_1600_st.html
EU-TOYOTA-CELICA-II-A40A50-COUPE-2D-FACELIFT-01	4370	1635	1320	Automobile-Catalog Toyota Celica Coupe 1600 LT Phase II Europe; Automobile-Catalog Toyota Celica Coupe 1600 ST Phase II Europe	https://www.automobile-catalog.com/car/1980/3493415/toyota_celica_coupe_1600_lt.html;https://www.automobile-catalog.com/car/1980/3493445/toyota_celica_coupe_1600_st.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-PREFL-01	4330	1635	1310	Automobile-Catalog Toyota Celica Liftback 1600 ST Phase I Europe	https://www.automobile-catalog.com/car/1978/3493265/toyota_celica_liftback_1600_st_5-speed.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-1600-FACELIFT-01	4370	1635	1310	Automobile-Catalog Toyota Celica Liftback 1600 ST Phase II Europe	https://www.automobile-catalog.com/car/1980/3493475/toyota_celica_liftback_1600_st.html
EU-ALPINA-B3-E92-COUPE-2D-GT3-01	4668	1782	1405	Auto-Data Alpina B3 Coupe (E92) GT3 technical specifications	https://www.auto-data.net/en/alpina-b3-coupe-e92-gt3-3.0-408hp-switch-tronic-18321
EU-ALPINA-B5-F11-WAGON-5D-BITURBO-01	4913	1860	1453	Auto-Data Alpina B5 Touring (F11) Biturbo technical specifications	https://www.auto-data.net/en/alpina-b5-touring-f11-4.4-v8-540hp-biturbo-18325
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-PREFL-01	4330	1640	1320	Automobile-Catalog Toyota Celica Liftback 2000 XT Phase I Europe	https://www.automobile-catalog.com/car/1978/3493310/toyota_celica_liftback_2000_xt.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-XT-FACELIFT-01	4370	1640	1320	Automobile-Catalog Toyota Celica Liftback 2000 XT Phase II Europe	https://www.automobile-catalog.com/car/1980/3493520/toyota_celica_liftback_2000_xt_automatic.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-PREFL-01	4330	1640	1315	Automobile-Catalog Toyota Celica Liftback 2000 GT Phase I Europe	https://www.automobile-catalog.com/car/1978/28655/toyota_celica_2000_gt.html
EU-TOYOTA-CELICA-II-A40A50-HATCHBACK-3D-2000-GT-FACELIFT-01	4370	1640	1315	Automobile-Catalog Toyota Celica Liftback 2000 GT Phase II Europe	https://www.automobile-catalog.com/car/1980/3493490/toyota_celica_liftback_2000_gt.html
EU-TOYOTA-CELICA-III-A60-HATCHBACK-3D-01	4450	1665	1320	Automobile-Catalog Toyota Celica 2000 XT Liftback	https://www.automobile-catalog.com/car/1982/50210/toyota_celica_xt_liftback.html
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-FWD-01	4365	1710	1290	Auto-Data Toyota Celica T16 2.0 GTi	https://www.auto-data.net/en/toyota-celica-t16-2.0-gti-140hp-3142
EU-TOYOTA-CELICA-IV-T16-HATCHBACK-3D-4WD-01	4380	1710	1290	Auto-Data Toyota Celica T16 2.0 Turbo 4x4	https://www.auto-data.net/en/toyota-celica-t16-2.0-turbo-185hp-4x4-3143
EU-TOYOTA-CELICA-IV-T16-COUPE-2D-FWD-01	4410	1710	1290	Automobile-Catalog Toyota Celica fourth-generation export Coupe	https://www.automobile-catalog.com/make/toyota/celica_4gen/celica_4_export_coupe/1986.html
EU-TOYOTA-CELICA-IV-T16-CONVERTIBLE-2D-01	4410	1690	1320	Automobile-Catalog Toyota Celica 2.0 GT Cabrio	https://www.automobile-catalog.com/car/1988/3520040/toyota_celica_2_0_gt_cabrio.html
EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	4620	1745	1310	Auto-Data Toyota Supra III A70 3.0 24V; Auto-Data Toyota Supra III A70 3.0 Turbo	https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-24v-190hp-automatic-46697;https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-turbo-235hp-automatic-3458
EU-TOYOTA-MR2-I-AW11-COUPE-2D-01	3925	1665	1250	Auto-Data Toyota MR2 W1 generation specifications	https://www.auto-data.net/en/toyota-mr-2-w1-generation-1001
EU-TOYOTA-MR2-II-SW20-TARGA-2D-01	4140	1695	1240	Auto-Data Toyota MR2 W2 SW20 2.0 16V technical specifications	https://www.auto-data.net/en/toyota-mr-2-w2-2.0-16v-sw20-156hp-automatic-28460
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-NARROW-01	4620	1685	1315	Automobile-Catalog Toyota Celica Supra 2.8i narrow body	https://www.automobile-catalog.com/car/1982/3504725/toyota_celica_supra_2_8i.html
EU-TOYOTA-CELICA-SUPRA-II-A60-HATCHBACK-3D-WIDE-01	4620	1720	1315	Automobile-Catalog Toyota Celica Supra 2.8i wide body	https://www.automobile-catalog.com/car/1983/3504770/toyota_celica_supra_2_8i_wide.html
EU-TOYOTA-HIACE-II-H20-MPV-4D-SWB-01	4340	1690	1925	Toyota 75 Years Hiace second-generation specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/index.html
EU-TOYOTA-HIACE-II-H30-MPV-4D-LWB-01	4690	1690	1920	Toyota 75 Years Hiace second-generation specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60001848B/index.html
EU-TOYOTA-HIACE-III-H50-MPV-4D-SWB-01	4425	1690	1890	Toyota 75 Years Hiace third-generation specifications; Drom Toyota Hiace YH51 Short Base Commuter	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html;https://www.drom.ru/catalog/toyota/hiace/319660/
EU-TOYOTA-HIACE-III-H60-MPV-4D-LWB-01	4690	1690	1890	Toyota 75 Years Hiace third-generation specifications; Drom Toyota Hiace YH61 nine-seat body	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015287/index.html;https://www.drom.ru/catalog/toyota/hiace/319428/
EU-TOYOTA-LITEACE-II-M20-VAN-4D-01	3900	1625	1765	Toyota 75 Years LiteAce second-generation van specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60015748/index.html
EU-TOYOTA-LITEACE-III-M30-MPV-4D-PREFL-01	4000	1650	1910	Automobile-Catalog Toyota Lite Ace 1.5 Combi Europe	https://www.automobile-catalog.com/car/1986/3606200/toyota_lite_ace_1_5_combi.html
EU-TOYOTA-LITEACE-III-M30-MPV-4D-FACELIFT-01	3995	1650	1900	Automobile-Catalog Toyota Lite Ace 1.5 Combi facelift Europe	https://www.automobile-catalog.com/car/1989/3606260/toyota_lite_ace_1_5_combi.html
EU-TOYOTA-LAND-CRUISER-80-SUV-5D-TD-01	4820	1900	1900	Toyota 75 Years Land Cruiser 80 HDJ81V specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60013935/index.html
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-SWB-01	3975	1690	1870	Auto-Data Toyota Land Cruiser J70 LJ70 2.4 TD specifications;Auto-Data Toyota Land Cruiser J70 KZJ70 3.0 TD specifications	https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-2.4-td-lj70-86hp-4wd-3740;https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-3.0-td-kzj70-125hp-4wd-3735
EU-TOYOTA-LAND-CRUISER-70-SUV-3D-MWB-01	4405	1790	1950	Auto-Data Toyota Land Cruiser J73 2.4 TD specifications	https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-2.4-td-lj73-86hp-4wd-3734
EU-TOYOTA-LAND-CRUISER-70-CONVERTIBLE-2D-SWB-HARDTOP-01	4040	1690	1890	UltimateSpecs Toyota Land Cruiser V 2.4 HardTop	https://www.ultimatespecs.com/car-specs/Toyota/5341/Toyota-Land-Cruiser-V-24-HardTop.html
EU-TOYOTA-LAND-CRUISER-PRADO-70-SUV-5D-LWB-01	4585	1690	1890	Toyota 75 Years Land Cruiser Prado 70 SX5 specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012614/index.html
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-DIESEL-01	4750	1800	1845	Auto-Data Toyota Land Cruiser J60 4.0 Diesel 101 Hp specifications;Auto-Data Toyota Land Cruiser J60 4.0 Diesel 103 Hp specifications	https://www.auto-data.net/en/toyota-land-cruiser-j60-wagon-4.0-diesel-101hp-4wd-3744;https://www.auto-data.net/en/toyota-land-cruiser-j60-wagon-4.0-diesel-103hp-4wd-3745
EU-TOYOTA-LAND-CRUISER-60-SUV-5D-TURBODIESEL-01	4750	1800	1830	Auto-Data Toyota Land Cruiser J60 4.0 Turbo-D 136 Hp specifications	https://www.auto-data.net/en/toyota-land-cruiser-j60-wagon-4.0-turbo-d-136hp-4wd-3747
EU-TOYOTA-MODEL-F-R20-MPV-4D-01	4285	1670	1815	Automobile-Catalog Toyota Model F Space Cruiser 1.8; Automobile-Catalog Toyota Model F Space Cruiser 2.0	https://www.automobile-catalog.com/car/1984/31130/toyota_f_1_8.html;https://www.automobile-catalog.com/car/1985/56135/toyota_f_2_0.html
EU-TOYOTA-HILUX-V-PICKUP-2D-REGULARCAB-01	4435	1689	1750	Drom Toyota Hilux LN85 2.4D Regular Cab	https://www.drom.ru/catalog/toyota/hilux_pick_up/250221/
EU-TOYOTA-HILUX-V-PICKUP-4D-DOUBLECAB-01	4725	1689	1585	Drom Toyota Hilux LN85 2.4D Double Cab	https://www.drom.ru/catalog/toyota/hilux_pick_up/250220/
EU-TOYOTA-HILUX-V-PICKUP-2D-XTRACAB-01	4905	1689	1735	Drom Toyota Hilux LN90 2.4D Xtracab	https://www.drom.ru/catalog/toyota/hilux_pick_up/250212/
EU-TOYOTA-TERCEL-II-AL25-WAGON-5D-4WD-01	4175	1615	1510	Automobile-Catalog Toyota Tercel 4WD	https://www.automobile-catalog.com/car/1983/25535/toyota_tercel_4wd.html
EU-TOYOTA-CELICA-V-T18-COUPE-3D-01	4420	1690	1300	Auto-Data Toyota Celica T18 generation specifications; Auto-Data Toyota Celica T18 2.0 Turbo 4WD technical specifications	https://www.auto-data.net/en/toyota-celica-t18-generation-770;https://www.auto-data.net/en/toyota-celica-t18-2.0-i-16v-turbo-208hp-4wd-3137
EU-TOYOTA-CELICA-V-T18-CONVERTIBLE-2D-01	4430	1705	1320	ADAC Toyota Celica Cabrio 2.0 GTi	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/toyota/celica/t18/348676/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3401-3500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60013935/index.html "https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60013935/index.html"
[2]: https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-2.4-td-lj70-86hp-4wd-3740 "https://www.auto-data.net/en/toyota-land-cruiser-j70-j73-2.4-td-lj70-86hp-4wd-3740"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3401-3500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3401-3500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4701 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1391 行）

