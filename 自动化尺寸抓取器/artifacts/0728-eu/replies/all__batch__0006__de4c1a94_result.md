# 任务：all 第 501-600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0006__de4c1a94


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 501-600 行

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
all 第 501-600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	S-Klasse	300 SEL	Stufenheck	Heckantrieb	Benzin	125	170	Jan 1968	Aug 1972	2026-05-01	526
Mercedes-benz	S-Klasse	280 SE, SEL	Stufenheck	Heckantrieb	Benzin	118	160	Jan 1968	Aug 1972	2024-03-01	527
Mercedes-benz	S-Klasse	300 SEL 3.5	Stufenheck	Heckantrieb	Benzin	147	200	Jan 1970	Jul 1972	2024-03-01	528
Mercedes-benz	S-Klasse	280 SE, SEL 3.5	Stufenheck	Heckantrieb	Benzin	147	200	Mar 1971	Aug 1972	2024-03-01	529
Mercedes-benz	S-Klasse	300 SEL 6.3	Stufenheck	Heckantrieb	Benzin	184	250	Mar 1968	Aug 1972	2024-03-01	530
Opel	Corsa a tr	1	Stufenheck	Frontantrieb	Benzin	33	45	Sep 1982	Sep 1992	2024-03-01	531
Opel	Corsa a cc	1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1982	Mar 1993	2024-03-01	532
Opel	Corsa a tr	1.2 S	Stufenheck	Frontantrieb	Benzin	40	55	Sep 1982	Mar 1993	2024-03-01	533
Opel	Corsa a tr	1.2 N	Stufenheck	Frontantrieb	Benzin	33	45	Jan 1985	Oct 1987	2024-03-01	534
Opel	Corsa a cc	1.2 S	Schrägheck	Frontantrieb	Benzin	40	55	Sep 1982	Feb 1990	2024-03-01	535
Opel	Corsa a tr	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1985	Oct 1987	2024-03-01	536
Opel	Corsa a tr	1.3 S	Stufenheck	Frontantrieb	Benzin	51	70	Sep 1982	Oct 1987	2024-03-01	537
Opel	Corsa a cc	1.3 S	Schrägheck	Frontantrieb	Benzin	51	70	Sep 1982	Oct 1989	2024-03-01	538
Opel	Corsa a cc	1.4 S	Schrägheck	Frontantrieb	Benzin	53	72	Jan 1990	Mar 1993	2024-03-01	539
Opel	Corsa a cc	1.5 D	Schrägheck	Frontantrieb	Diesel	37	50	Sep 1987	Mar 1993	2024-03-01	540
Opel	Corsa a cc	1.5 TD	Schrägheck	Frontantrieb	Diesel	49	67	Mar 1988	Mar 1993	2024-03-01	541
Opel	Corsa a cc	1.2	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1982	Aug 1990	2024-03-01	542
Opel	Corsa a cc	1.3 I	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1986	Sep 1990	2024-03-01	543
Opel	Corsa a cc	1.4 I	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1990	Mar 1993	2024-03-01	544
Opel	Corsa a cc	1.4 SI	Schrägheck	Frontantrieb	Benzin	60	82	Sep 1991	Mar 1993	2024-03-01	545
Opel	Corsa a cc	1.6 GSI	Schrägheck	Frontantrieb	Benzin	72	98	Sep 1989	Mar 1993	2024-03-01	546
Opel	Corsa a cc	1.6 GSI	Schrägheck	Frontantrieb	Benzin	74	100	May 1988	Mar 1992	2024-03-01	547
Opel	Kadett b	1.1	Stufenheck	Heckantrieb	Benzin	33	45	Sep 1965	Jul 1971	2024-03-01	548
Opel	Kadett b	1.1	Coupe	Heckantrieb	Benzin	33	45	Sep 1965	Jul 1971	2024-03-01	549
Opel	Kadett b	1.1	Coupe	Heckantrieb	Benzin	37	50	Aug 1971	Aug 1973	2024-03-01	550
Opel	Kadett b	1.1	Stufenheck	Heckantrieb	Benzin	37	50	Aug 1971	Aug 1973	2024-03-01	551
Opel	Kadett b	1.1 S	Stufenheck	Heckantrieb	Benzin	40	55	Sep 1965	Jul 1971	2024-03-01	552
Opel	Kadett b	1.1	Coupe	Heckantrieb	Benzin	40	55	Sep 1965	Jul 1971	2024-03-01	553
Opel	Kadett b	1.1 SR	Stufenheck	Heckantrieb	Benzin	44	60	Nov 1966	Jul 1971	2024-03-01	554
Opel	Kadett b	1.1	Coupe	Heckantrieb	Benzin	44	60	Nov 1966	Jul 1971	2024-03-01	555
Opel	Kadett b	1.2 S	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1971	Aug 1973	2024-03-01	556
Opel	Kadett b	1.2	Coupe	Heckantrieb	Benzin	44	60	Aug 1971	Aug 1973	2024-03-01	557
Opel	Kadett b	1.9	Coupe	Heckantrieb	Benzin	66	90	Aug 1967	Aug 1973	2024-03-01	558
Opel	Kadett b caravan	1.1	Kombi	Heckantrieb	Benzin	33	45	Sep 1965	Jul 1971	2024-03-01	559
Opel	Kadett b caravan	1.1	Kombi	Heckantrieb	Benzin	37	50	Aug 1971	Aug 1973	2024-03-01	560
Opel	Kadett b caravan	1.1	Kombi	Heckantrieb	Benzin	40	55	Sep 1965	Jul 1971	2024-03-01	561
Opel	Kadett b caravan	1.2	Kombi	Heckantrieb	Benzin	44	60	Aug 1971	Aug 1973	2024-03-01	562
Opel	Kadett c cc	1	Schrägheck	Heckantrieb	Benzin	29	40	May 1975	Jul 1979	2024-03-01	563
Opel	Kadett c	1	Stufenheck	Heckantrieb	Benzin	29	40	Jan 1974	Jul 1979	2024-03-01	564
Opel	Kadett c	1	Coupe	Heckantrieb	Benzin	29	40	Jan 1974	Jul 1979	2024-03-01	565
Opel	Kadett c	1.2	Coupe	Heckantrieb	Benzin	38	52	Aug 1973	Apr 1977	2024-03-01	566
Opel	Kadett c	1.2	Stufenheck	Heckantrieb	Benzin	38	52	Aug 1973	Apr 1977	2024-03-01	567
Opel	Kadett c cc	1.2	Schrägheck	Heckantrieb	Benzin	38	52	May 1975	Apr 1977	2024-03-01	568
Opel	Kadett c	1.2	Stufenheck	Heckantrieb	Benzin	40	55	Aug 1973	Jul 1979	2024-03-01	569
Opel	Kadett c cc	1.2	Schrägheck	Heckantrieb	Benzin	40	54	Jul 1976	Jul 1979	2024-03-01	570
Opel	Kadett c	1.2	Coupe	Heckantrieb	Benzin	40	54	Aug 1973	Jul 1979	2024-03-01	571
Opel	Kadett c	1.2 S	Coupe	Heckantrieb	Benzin	44	60	Aug 1973	Jul 1979	2024-03-01	572
Opel	Kadett c cc	1.2 S	Schrägheck	Heckantrieb	Benzin	44	60	Aug 1973	Jul 1979	2024-03-01	573
Opel	Kadett c	1.2 S	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1973	Jul 1979	2024-03-01	574
Opel	Kadett c cc	1.6 S	Schrägheck	Heckantrieb	Benzin	55	75	May 1977	Jul 1979	2024-03-01	575
Opel	Kadett c	1.6 S	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1976	Jul 1979	2024-03-01	576
Opel	Kadett c	1.6 S	Coupe	Heckantrieb	Benzin	55	75	May 1977	Jul 1979	2024-03-01	577
Opel	Kadett c	1.9 Gt/e	Coupe	Heckantrieb	Benzin	77	105	Sep 1975	Jul 1977	2024-03-01	578
Opel	Kadett c	2.0 E Rallye	Coupe	Heckantrieb	Benzin	81	110	Aug 1977	Jul 1979	2024-03-01	579
Opel	Kadett c caravan	1	Kombi	Heckantrieb	Benzin	29	40	Jan 1974	Jul 1979	2024-03-01	580
Opel	Kadett c caravan	1.2	Kombi	Heckantrieb	Benzin	38	52	Aug 1973	Apr 1977	2024-03-01	581
Opel	Kadett c caravan	1.2	Kombi	Heckantrieb	Benzin	40	54	Aug 1973	Jul 1979	2024-03-01	582
Opel	Kadett c caravan	1.2 S	Kombi	Heckantrieb	Benzin	44	60	Aug 1973	Jul 1979	2024-03-01	583
Opel	Kadett c caravan	1.6 S	Kombi	Heckantrieb	Benzin	55	75	May 1977	Jul 1979	2024-03-01	584
Opel	Kadett d	1.2	Schrägheck	Frontantrieb	Benzin	40	55	Aug 1982	Aug 1984	2024-03-01	585
Opel	Kadett d	1.2	Schrägheck	Frontantrieb	Benzin	39	53	Aug 1979	Jul 1982	2024-03-01	586
Opel	Kadett d	1.2 S	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1979	Aug 1984	2024-03-01	587
Opel	Kadett d	1.3 N	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1979	Aug 1984	2024-03-01	588
Opel	Kadett d	1.3 S	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1979	Aug 1984	2024-03-01	589
Opel	Kadett d	1.6 S	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1981	Aug 1984	2024-03-01	590
Opel	Kadett d	1.8 Gt/e	Schrägheck	Frontantrieb	Benzin	85	115	Feb 1983	Aug 1984	2024-03-01	591
Opel	Kadett d	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Mar 1982	Aug 1984	2024-03-01	592
Opel	Kadett c	2.0 Gt/e	Coupe	Heckantrieb	Benzin	85	115	Aug 1977	Jul 1979	2024-03-01	593
Opel	Kadett d caravan	1.2	Kombi	Frontantrieb	Benzin	39	53	Aug 1979	Jul 1982	2024-03-01	594
Opel	Kadett d caravan	1.2 S	Kombi	Frontantrieb	Benzin	44	60	Aug 1979	Aug 1984	2024-03-01	595
Opel	Kadett d caravan	1.3 N	Kombi	Frontantrieb	Benzin	44	60	Aug 1979	Aug 1984	2024-03-01	596
Opel	Kadett d caravan	1.3 S	Kombi	Frontantrieb	Benzin	55	75	Aug 1979	Aug 1984	2024-03-01	597
Opel	Kadett d caravan	1.6 S	Kombi	Frontantrieb	Benzin	66	90	Sep 1981	Aug 1984	2024-03-01	598
Opel	Kadett d caravan	1.6 D	Kombi	Frontantrieb	Diesel	40	54	Mar 1982	Aug 1984	2024-03-01	599
Opel	Kadett e cc	1.2	Schrägheck	Frontantrieb	Benzin	40	55	Sep 1984	Jul 1986	2024-03-01	600
Opel	Kadett e cc	1.3 N	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1984	Aug 1991	2024-03-01	601
Opel	Kadett e cc	1.3 S	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1984	Aug 1987	2024-03-01	602
Opel	Kadett e cc	1.4 S	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1990	Aug 1991	2024-03-01	603
Opel	Kadett e cc	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	604
Opel	Kadett e cc	1.6 S	Schrägheck	Frontantrieb	Benzin	60	82	Sep 1986	Aug 1991	2024-03-01	605
Opel	Kadett e cc	1.6 S	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1984	Aug 1986	2024-03-01	606
Opel	Kadett e cc	1.8 S	Schrägheck	Frontantrieb	Benzin	62	84	Sep 1987	Aug 1991	2024-03-01	607
Opel	Kadett e cc	1.8 E	Schrägheck	Frontantrieb	Benzin	74	100	Oct 1985	Aug 1986	2024-03-01	608
Opel	Kadett e cc	1.8 GSI	Schrägheck	Frontantrieb	Benzin	85	115	Sep 1984	Aug 1986	2024-03-01	609
Opel	Kadett e cc	2.0 GSI	Schrägheck	Frontantrieb	Benzin	85	115	Sep 1986	Aug 1991	2024-03-01	610
Opel	Kadett e cc	2.0 GSI	Schrägheck	Frontantrieb	Benzin	95	129	Sep 1986	Aug 1991	2024-03-01	611
Opel	Kadett e cc	2.0 GSI 16V	Schrägheck	Frontantrieb	Benzin	110	150	Mar 1988	Aug 1991	2024-03-01	612
Opel	Kadett e cc	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Sep 1984	Jan 1989	2024-03-01	613
Opel	Kadett e cc	1.7 D	Schrägheck	Frontantrieb	Diesel	42	57	Feb 1989	Aug 1991	2024-03-01	614
Opel	Kadett e cc	1.4 I	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1990	Aug 1991	2024-03-01	615
Opel	Kadett e cc	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1985	Aug 1991	2024-03-01	616
Opel	Kadett e	1.2	Stufenheck	Frontantrieb	Benzin	40	55	Sep 1984	Jul 1986	2024-03-01	617
Opel	Kadett e	1.3 N	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1984	Aug 1989	2024-03-01	618
Opel	Kadett e	1.3 S	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1984	Aug 1987	2024-03-01	619
Opel	Kadett e	1.4 S	Stufenheck	Frontantrieb	Benzin	55	75	Jan 1990	Aug 1991	2024-03-01	620
Opel	Kadett e	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	621
Opel	Kadett e	1.6 S	Stufenheck	Frontantrieb	Benzin	60	82	Sep 1986	Aug 1991	2024-03-01	622
Opel	Kadett e	1.6 S	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1984	Aug 1986	2024-03-01	623
Opel	Kadett e	1.8 S	Stufenheck	Frontantrieb	Benzin	62	84	Sep 1987	Aug 1991	2024-03-01	624
Opel	Kadett e	1.8 I	Stufenheck	Frontantrieb	Benzin	74	100	Oct 1985	Aug 1986	2024-03-01	625


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Mercedes-Benz S-Klasse W108/W109 的 5 个 Ktype。
* `527` 与 `529` 的 VariantName 同时覆盖 SE、SEL，已按短轴与长轴拆分。
* W108 短轴尺寸组复用上一批已确认缓存 `EU-MERCEDES-BENZ-W108-SEDAN-01`，本轮不重复输出。
* 新建 W108 长轴、W109 普通空气悬架车身和 W109 6.3 三个尺寸组。
* Mercedes-Benz 官方档案确认：W108 短轴为 4900×1810×1440 mm，W108 长轴为 5000×1810×1440 mm；W109 300 SEL 2.8/3.5 为 5000×1810×1410 mm；300 SEL 6.3 高度为 1420 mm。([marsClassic][1])

## 当前批次进度

* READY Ktype：5/100
* READY 映射：7 条
* PENDING Ktype：95/100
* 本轮新建尺寸组：3 个
* 复用历史尺寸组：1 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
526	526	Sedan	W109	109.016	4	EU-MERCEDES-BENZ-W109-SEDAN-01	MEDIUM	170 hp对应300 SEL 2.8；输入结束年月晚于官方109.016生产期。	READY
527_swb	527	Sedan	W108	108.018	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH	280 SE短轴车身。	READY
527_lwb	527	Sedan	W108	108.019	4	EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	HIGH	280 SE long、后更名280 SEL的长轴车身。	READY
528	528	Sedan	W109	109.056	4	EU-MERCEDES-BENZ-W109-SEDAN-01	HIGH	300 SEL 3.5空气悬架长轴车身。	READY
529_swb	529	Sedan	W108	108.057	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH	280 SE 3.5短轴车身。	READY
529_lwb	529	Sedan	W108	108.058	4	EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	HIGH	280 SEL 3.5长轴车身。	READY
530	530	Sedan	W109	109.018	4	EU-MERCEDES-BENZ-W109-SEDAN-63-01	HIGH	300 SEL 6.3独立高度配置。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	5000	1810	1440	Mercedes-Benz Public Archive – 280 SE long wheelbase / 280 SEL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SE-long-wheelbase-from-091969-280-SEL.xhtml?oid=4921
EU-MERCEDES-BENZ-W109-SEDAN-01	5000	1810	1410	Mercedes-Benz Public Archive – 300 SEL W109 E 28	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL.xhtml?oid=4906
EU-MERCEDES-BENZ-W109-SEDAN-63-01	5000	1810	1420	Mercedes-Benz Public Archive – 300 SEL 6.3	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL-63.xhtml?oid=4903
```

## 下一步优先处理

1. 按车身聚类闭合 Opel Corsa A：TR Sedan、CC 3-door、CC 5-door。
2. 批量关联 Ktype `531–547`，避免按发动机重复抓取尺寸。
3. 随后处理 Kadett B Sedan、Coupe、Caravan 三个车身分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL.xhtml?oid=4906&utm_source=chatgpt.com "300 SEL"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Opel Corsa A 的 Sedan 2-door、Sedan 4-door、Hatchback 3-door、Hatchback 5-door，以及 1990 facelift 前后尺寸边界。
* 已批量完成 Ktype `531–547`；普通 Hatchback 按 3/5 门拆分，跨 1990 facelift 的 Ktype 同时拆分 `prefl` 与 `facelift`。
* `546`、`547` 的 GSI 按已确认的 3-door 车身处理，不创建无依据的 5-door 分支。
* Corsa A Sedan 尺寸保持 3955×1540×1360 mm；Hatchback 从 3622×1532×1365 mm 更新为 1990 facelift 的 3652×1542×1365 mm。门数边界由 S83 车身资料确认。([汽车数据网][1])

## 当前批次进度

* READY Ktype：22/100
* READY 映射：53 条
* PENDING Ktype：78/100
* 已确认尺寸组：10 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
531_2dr	531	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
531_4dr	531	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
532_3dr_prefl	532	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
532_3dr_facelift	532	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
532_5dr_prefl	532	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
532_5dr_facelift	532	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
533_2dr	533	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
533_4dr	533	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
534_2dr	534	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
534_4dr	534	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
535_3dr	535	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
535_5dr	535	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
536_2dr	536	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
536_4dr	536	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
537_2dr	537	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
537_4dr	537	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
538_3dr	538	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
538_5dr	538	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
539_3dr_prefl	539	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
539_3dr_facelift	539	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
539_5dr_prefl	539	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
539_5dr_facelift	539	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
540_3dr_prefl	540	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
540_3dr_facelift	540	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
540_5dr_prefl	540	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
540_5dr_facelift	540	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
541_3dr_prefl	541	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
541_3dr_facelift	541	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
541_5dr_prefl	541	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
541_5dr_facelift	541	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
542_3dr	542	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
542_5dr	542	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
543_3dr_prefl	543	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
543_3dr_facelift	543	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	生产结束月覆盖1990 facelift转换月。	READY
543_5dr_prefl	543	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
543_5dr_facelift	543	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	生产结束月覆盖1990 facelift转换月。	READY
544_3dr_prefl	544	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
544_3dr_facelift	544	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
544_5dr_prefl	544	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
544_5dr_facelift	544	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
545_3dr	545	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door facelift Hatchback物理分支。	READY
545_5dr	545	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door facelift Hatchback物理分支。	READY
546_prefl	546	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	GSI 3-door，1990 facelift前。	READY
546_facelift	546	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	HIGH	GSI 3-door，1990 facelift后。	READY
547_prefl	547	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	GSI 3-door，1990 facelift前。	READY
547_facelift	547	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	HIGH	GSI 3-door，1990 facelift后。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CORSA-A-SEDAN-2D-01	3955	1540	1360	Auto-Data – Opel Corsa A Sedan; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-sedan-generation-5145;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-SEDAN-4D-01	3955	1540	1360	Auto-Data – Opel Corsa A Sedan; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-sedan-generation-5145;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	3622	1532	1365	Auto-Data – Opel Corsa A model overview; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-model-248;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	3622	1532	1365	Auto-Data – Opel Corsa A model overview; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-model-248;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	3652	1542	1365	Auto-Data – Opel Corsa A facelift 1990; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-facelift-1990-1.4i-82hp-2130;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	3652	1542	1365	Auto-Data – Opel Corsa A facelift 1990; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-facelift-1990-1.4i-82hp-2130;https://www.opel-infos.de/fgst/fgst_mj82-97.html
```

## 下一步优先处理

1. 按车身聚类创建 Kadett B Sedan、Coupe、Caravan 尺寸组。
2. 批量关联 Ktype `548–562`。
3. 随后处理 Kadett C Sedan、Coupe、Hatchback 与 Caravan。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-corsa-model-248 "Opel Corsa | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Opel Kadett D 标准 Hatchback、GTE 宽体 Hatchback 与 Caravan 的尺寸组。
* 标准 Hatchback 和 Caravan 均按 3-door、5-door 物理分支拆分；共享三维但不合并门数外廓。
* Ktype `591` 的 1.8 GT/E 使用独立宽体组：车身宽度为 1656 mm，区别于普通 Kadett D 的 1636 mm。([汽车目录][1])
* 已批量完成 Ktype `585–592`、`594–599`；Kadett B 的标准/L/LS 与两类 Coupé 边界暂不生成猜测映射。

## 当前批次进度

* READY Ktype：37/100
* READY 映射：80 条
* PENDING Ktype：63/100
* 已确认尺寸组：15 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
585_3dr	585	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
585_5dr	585	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
586_3dr	586	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
586_5dr	586	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
587_3dr	587	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
587_5dr	587	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
588_3dr	588	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
588_5dr	588	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
589_3dr	589	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
589_5dr	589	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
590_3dr	590	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
590_5dr	590	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
591	591	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-GTE-HATCHBACK-3D-01	HIGH	GT/E宽体3-door外廓。	READY
592_3dr	592	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
592_5dr	592	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
594_3dr	594	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
594_5dr	594	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
595_3dr	595	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
595_5dr	595	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
596_3dr	596	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
596_5dr	596	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
597_3dr	597	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
597_5dr	597	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
598_3dr	598	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
598_5dr	598	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
599_3dr	599	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
599_5dr	599	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-KADETT-D-HATCHBACK-3D-01	3998	1636	1380	Automobile-Catalog – 1983 Opel Kadett 1.6 D Hatch; Auto-Data – Opel Kadett D	https://www.automobile-catalog.com/car/1983/2439245/opel_kadett_1_6_d_hatch.html;https://www.auto-data.net/en/opel-kadett-d-generation-507
EU-OPEL-KADETT-D-HATCHBACK-5D-01	3998	1636	1380	Automobile-Catalog – 1983 Opel Kadett 1.6 D Hatch; Auto-Data – Opel Kadett D	https://www.automobile-catalog.com/car/1983/2439245/opel_kadett_1_6_d_hatch.html;https://www.auto-data.net/en/opel-kadett-d-generation-507
EU-OPEL-KADETT-D-GTE-HATCHBACK-3D-01	3998	1656	1380	Automobile-Catalog – 1983 Opel Kadett D GTE; Carfolio – Opel Kadett 1.8 GTE	https://www.automobile-catalog.com/make/opel/kadett_d/kadett_d_gte/1983.html;https://www.carfolio.com/opel-kadett-1.8-gte-39039
EU-OPEL-KADETT-D-WAGON-3D-01	4207	1636	1400	Auto-Data – Opel Kadett D Caravan; Opel Team Niedersachsen – Kadett D technical data	https://www.auto-data.net/en/opel-kadett-d-caravan-generation-508;https://www.opel-team-niedersachsen.de/kadett-d.html
EU-OPEL-KADETT-D-WAGON-5D-01	4207	1636	1400	Auto-Data – Opel Kadett D Caravan; Opel Team Niedersachsen – Kadett D technical data	https://www.auto-data.net/en/opel-kadett-d-caravan-generation-508;https://www.opel-team-niedersachsen.de/kadett-d.html
```

## 下一步优先处理

1. 闭合 Kadett E CC 的 3-door、5-door、GSI 外廓及 1989 facelift 尺寸边界。
2. 闭合 Kadett E Sedan 的 2-door、4-door 与 facelift 前后尺寸组。
3. 批量关联 Ktype `600–625`，随后回补 Kadett B、Kadett C 的复杂分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/2439245/opel_kadett_1_6_d_hatch.html?utm_source=chatgpt.com "1983 Opel Kadett 1.6 D Hatch Specs Review (40 kW ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Kadett E CC 普通 3-door、5-door Hatchback，三维均为 `3998×1663×1400 mm`。
* 已闭合 Kadett E GSI 3-door、5-door 分支，普通 GSI 外廓为 `3998×1666×1395 mm`；未将 Champion 等特殊外观版本的宽度用于当前输入。
* 已闭合 Kadett E 4-door Sedan，三维为 `4218×1658×1400 mm`。
* 1989 年的小改款未造成当前普通 Hatchback 或 Sedan 尺寸组必须拆分的三维变化，因此不创建重复 facelift 组。资料同时确认 Kadett E Hatchback 和 GSI 存在 3/5-door 分支，Sedan 为 4-door 分支。([汽车目录][1])
* 已批量关联 Ktype `600–625`。

## 当前批次进度

* READY Ktype：63/100
* READY 映射：123 条
* PENDING Ktype：37/100
* 已确认尺寸组：20 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
600_3dr	600	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
600_5dr	600	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
601_3dr	601	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
601_5dr	601	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
602_3dr	602	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
602_5dr	602	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
603_3dr	603	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
603_5dr	603	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
604_3dr	604	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
604_5dr	604	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
605_3dr	605	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
605_5dr	605	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
606_3dr	606	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
606_5dr	606	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
607_3dr	607	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
607_5dr	607	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
608_3dr	608	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
608_5dr	608	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
609_3dr	609	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
609_5dr	609	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSI 5-door外观分支。	READY
610_3dr	610	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
610_5dr	610	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	HIGH	GSI 5-door外观分支。	READY
611_3dr	611	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
611_5dr	611	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	HIGH	GSI 5-door外观分支。	READY
612_3dr	612	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 16V 3-door外观分支。	READY
612_5dr	612	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSI 16V 5-door物理分支。	READY
613_3dr	613	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
613_5dr	613	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
614_3dr	614	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
614_5dr	614	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
615_3dr	615	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
615_5dr	615	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
616_3dr	616	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
616_5dr	616	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
617	617	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
618	618	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
619	619	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
620	620	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
621	621	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
622	622	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
623	623	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
624	624	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
625	625	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400	Automobile-Catalog – 1986 Opel Kadett 1.2 S; Opel Kadett E body overview	https://www.automobile-catalog.com/car/1986/2458235/opel_kadett_1_2_s_5-speed.html;https://en.wikipedia.org/wiki/Opel_Kadett_E
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400	Automobile-Catalog – 1986 Opel Kadett 1.2 S; Opel Kadett E body overview	https://www.automobile-catalog.com/car/1986/2458235/opel_kadett_1_2_s_5-speed.html;https://en.wikipedia.org/wiki/Opel_Kadett_E
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395	Automobile-Catalog – 1988 Opel Kadett GSi; Auto-Data – Opel Kadett E CC 2.0 GSI	https://www.automobile-catalog.com/car/1988/2460140/opel_kadett_gsi.html;https://www.auto-data.net/en/opel-kadett-e-cc-2.0-gsi-115hp-1917
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395	Automobile-Catalog – 1988 Opel Kadett GSi; Auto-Data – Opel Kadett E CC 2.0 GSI	https://www.automobile-catalog.com/car/1988/2460140/opel_kadett_gsi.html;https://www.auto-data.net/en/opel-kadett-e-cc-2.0-gsi-115hp-1917
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400	Automobile-Catalog – 1987 Opel Kadett 4-door 1.6 S; Auto-Data – Opel Kadett model overview	https://www.automobile-catalog.com/car/1987/2459495/opel_kadett_4d_1_6_s.html;https://www.auto-data.net/en/opel-kadett-model-244
```

## 下一步优先处理

1. 闭合 Kadett C Sedan、Coupe、City Hatchback 与 Caravan 尺寸组并关联 `563–584`、`593`。
2. 回补 Kadett B Sedan、Coupe 与 Caravan 的标准/L/LS 物理边界并关联 `548–562`。
3. 消除剩余 37 个 PENDING 后，立即进入一次轻量机械收尾并输出完整最终文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/2458235/opel_kadett_1_2_s_5-speed.html?utm_source=chatgpt.com "1986 Opel Kadett 1.2 S 5-speed Specs Review (40.5 kW ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Kadett C 的 Sedan 2-door、Sedan 4-door、Coupe 2-door、City Hatchback 3-door 和 Caravan 3-door 五个物理分支。
* Sedan 采用 `4124×1580×1375 mm`；Coupe 采用 `4127×1580×1340 mm`；City 采用 `3893×1580×1380 mm`；Caravan 采用 `4138×1580×1385 mm`，所用 Automobile-Catalog 页面明确将宽度标为不含后视镜。([汽车目录][1])
* `578`、`579`、`593` 的 GT/E、Rallye 发动机版本未发现需要另建尺寸组的不同整体外廓，继续关联 Kadett C Coupe 组。
* 已批量完成 Ktype `563–584` 和 `593`。
* 按已输出 Ktype 重新机械计数，上一轮 READY 应为 `62/100`；本轮完成后为 `85/100`。

## 当前批次进度

* READY Ktype：85/100
* READY 映射：151 条
* PENDING Ktype：15/100
* 已确认尺寸组：25 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
563	563	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
564_2dr	564	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
564_4dr	564	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
565	565	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
566	566	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
567_2dr	567	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
567_4dr	567	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
568	568	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
569_2dr	569	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
569_4dr	569	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
570	570	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
571	571	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
572	572	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
573	573	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
574_2dr	574	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
574_4dr	574	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
575	575	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
576_2dr	576	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
576_4dr	576	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
577	577	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
578	578	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	GT/E使用2-door Coupe外廓。	READY
579	579	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	Rallye使用2-door Coupe外廓。	READY
580	580	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
581	581	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
582	582	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
583	583	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
584	584	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
593	593	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	GT/E使用2-door Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-KADETT-C-SEDAN-2D-01	4124	1580	1375	Automobile-Catalog – 1978 Opel Kadett 1.2 N	https://www.automobile-catalog.com/car/1978/2419385/opel_kadett_1_2_n.html
EU-OPEL-KADETT-C-SEDAN-4D-01	4124	1580	1375	Automobile-Catalog – 1978 Opel Kadett 1.2 N	https://www.automobile-catalog.com/car/1978/2419385/opel_kadett_1_2_n.html
EU-OPEL-KADETT-C-COUPE-2D-01	4127	1580	1340	Auto-Data – Opel Kadett C Coupe; Automobile-Catalog – 1979 Opel Kadett Coupe Luxe 1.2 S	https://www.auto-data.net/en/opel-kadett-c-coupe-generation-512;https://www.automobile-catalog.com/car/1979/2418590/opel_kadett_coupe_luxe_1_2_s.html
EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	3893	1580	1380	Automobile-Catalog – 1978 Opel Kadett City Berlina 1.2 S	https://www.automobile-catalog.com/car/1978/2419145/opel_kadett_city_berlina_1_2_s.html
EU-OPEL-KADETT-C-WAGON-3D-01	4138	1580	1385	Automobile-Catalog – 1978 Opel Kadett Caravan 1.2 N	https://www.automobile-catalog.com/car/1978/2419505/opel_kadett_caravan_1_2_n.html
```

## 下一步优先处理

1. 闭合 Kadett B Sedan 2-door、Sedan 4-door、Coupe 与 Caravan 的物理分支。
2. 批量关联最后的 Ktype `548–562`。
3. PENDING 清零后，下一轮直接进行一次机械收尾并输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/2419385/opel_kadett_1_2_n.html?utm_source=chatgpt.com "1978 Opel Kadett 1.2 N Specs Review (40.5 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已完成剩余 Kadett B 的标准/L/LS Sedan、Gill/LS Coupé，以及标准/L Caravan 物理分支。
* Opel 官方档案确认 Kadett B 包含双门/四门 notchback、双门/四门 LS fastback、Gill Coupé、LS Coupé及三门/五门 Caravan；尺寸组已按外廓和门数分别闭合。Kadett B 的规格来源同时明确了标准、L、LS、Coupé 与 Caravan 的长宽高，其中 Automobile-Catalog 的宽度口径为不含后视镜。([Stellantis Media][1])
* 已完成固定表头、唯一主键、外键闭合、尺寸与来源非空检查。
* 已覆盖全部 100 个输入 Ktype，不存在 PENDING。

## 当前批次进度

* Ktype 覆盖：100/100
* READY 映射：199 条
* PENDING：0
* DIMENSION_GROUP：37 个
* 映射引用闭合：通过
* 孤立尺寸组：0
* `id` 与 `DIMENSION_GROUP_ID` 唯一性：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
526	526	Sedan	W109	109.016	4	EU-MERCEDES-BENZ-W109-SEDAN-01	MEDIUM	170 hp对应300 SEL 2.8；输入结束年月晚于官方109.016生产期。	READY
527_swb	527	Sedan	W108	108.018	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH	280 SE短轴车身。	READY
527_lwb	527	Sedan	W108	108.019	4	EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	HIGH	280 SE long、后更名280 SEL的长轴车身。	READY
528	528	Sedan	W109	109.056	4	EU-MERCEDES-BENZ-W109-SEDAN-01	HIGH	300 SEL 3.5空气悬架长轴车身。	READY
529_swb	529	Sedan	W108	108.057	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH	280 SE 3.5短轴车身。	READY
529_lwb	529	Sedan	W108	108.058	4	EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	HIGH	280 SEL 3.5长轴车身。	READY
530	530	Sedan	W109	109.018	4	EU-MERCEDES-BENZ-W109-SEDAN-63-01	HIGH	300 SEL 6.3独立高度配置。	READY
531_2dr	531	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
531_4dr	531	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
532_3dr_prefl	532	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
532_3dr_facelift	532	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
532_5dr_prefl	532	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
532_5dr_facelift	532	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
533_2dr	533	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
533_4dr	533	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
534_2dr	534	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
534_4dr	534	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
535_3dr	535	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
535_5dr	535	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
536_2dr	536	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
536_4dr	536	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
537_2dr	537	Sedan	Corsa A	S83	2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
537_4dr	537	Sedan	Corsa A	S83	4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
538_3dr	538	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
538_5dr	538	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
539_3dr_prefl	539	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
539_3dr_facelift	539	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
539_5dr_prefl	539	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
539_5dr_facelift	539	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
540_3dr_prefl	540	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
540_3dr_facelift	540	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
540_5dr_prefl	540	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
540_5dr_facelift	540	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
541_3dr_prefl	541	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
541_3dr_facelift	541	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
541_5dr_prefl	541	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
541_5dr_facelift	541	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
542_3dr	542	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback物理分支。	READY
542_5dr	542	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback物理分支。	READY
543_3dr_prefl	543	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
543_3dr_facelift	543	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	生产结束月覆盖1990 facelift转换月。	READY
543_5dr_prefl	543	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
543_5dr_facelift	543	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	生产结束月覆盖1990 facelift转换月。	READY
544_3dr_prefl	544	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	3-door Hatchback，1990 facelift前。	READY
544_3dr_facelift	544	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door Hatchback，1990 facelift后。	READY
544_5dr_prefl	544	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	5-door Hatchback，1990 facelift前。	READY
544_5dr_facelift	544	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door Hatchback，1990 facelift后。	READY
545_3dr	545	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	3-door facelift Hatchback物理分支。	READY
545_5dr	545	Hatchback	Corsa A	S83	5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	5-door facelift Hatchback物理分支。	READY
546_prefl	546	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	GSI 3-door，1990 facelift前。	READY
546_facelift	546	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	HIGH	GSI 3-door，1990 facelift后。	READY
547_prefl	547	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	GSI 3-door，1990 facelift前。	READY
547_facelift	547	Hatchback	Corsa A	S83	3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	HIGH	GSI 3-door，1990 facelift后。	READY
548_std_2dr	548	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-STD-2D-01	MEDIUM	标准2-door notchback分支。	READY
548_std_4dr	548	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-STD-4D-01	MEDIUM	标准4-door notchback分支。	READY
548_l_2dr	548	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-L-2D-01	MEDIUM	L 2-door加长notchback外廓。	READY
548_l_4dr	548	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-L-4D-01	MEDIUM	L 4-door加长notchback外廓。	READY
548_ls_2dr	548	Hatchback	Kadett B		2	EU-OPEL-KADETT-B-HATCHBACK-LS-2D-01	MEDIUM	LS 2-door fastback分支。	READY
548_ls_4dr	548	Hatchback	Kadett B		4	EU-OPEL-KADETT-B-HATCHBACK-LS-4D-01	MEDIUM	LS 4-door fastback分支。	READY
549_gill	549	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-GILL-2D-01	MEDIUM	Gill Coupé早期车身。	READY
549_ls	549	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	MEDIUM	LS Coupé后期车身。	READY
550	550	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	HIGH	1971年后LS Coupé车身。	READY
551_std_2dr	551	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-STD-2D-01	MEDIUM	标准2-door notchback分支。	READY
551_std_4dr	551	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-STD-4D-01	MEDIUM	标准4-door notchback分支。	READY
551_l_2dr	551	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-L-2D-01	MEDIUM	L 2-door加长notchback外廓。	READY
551_l_4dr	551	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-L-4D-01	MEDIUM	L 4-door加长notchback外廓。	READY
552_std_2dr	552	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-STD-2D-01	MEDIUM	标准2-door notchback分支。	READY
552_std_4dr	552	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-STD-4D-01	MEDIUM	标准4-door notchback分支。	READY
552_l_2dr	552	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-L-2D-01	MEDIUM	L 2-door加长notchback外廓。	READY
552_l_4dr	552	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-L-4D-01	MEDIUM	L 4-door加长notchback外廓。	READY
552_ls_2dr	552	Hatchback	Kadett B		2	EU-OPEL-KADETT-B-HATCHBACK-LS-2D-01	MEDIUM	LS 2-door fastback分支。	READY
552_ls_4dr	552	Hatchback	Kadett B		4	EU-OPEL-KADETT-B-HATCHBACK-LS-4D-01	MEDIUM	LS 4-door fastback分支。	READY
553_gill	553	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-GILL-2D-01	MEDIUM	Gill Coupé早期车身。	READY
553_ls	553	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	MEDIUM	LS Coupé后期车身。	READY
554_std_2dr	554	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-STD-2D-01	MEDIUM	标准2-door notchback分支。	READY
554_std_4dr	554	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-STD-4D-01	MEDIUM	标准4-door notchback分支。	READY
554_l_2dr	554	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-L-2D-01	MEDIUM	L 2-door加长notchback外廓。	READY
554_l_4dr	554	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-L-4D-01	MEDIUM	L 4-door加长notchback外廓。	READY
554_ls_2dr	554	Hatchback	Kadett B		2	EU-OPEL-KADETT-B-HATCHBACK-LS-2D-01	MEDIUM	LS 2-door fastback分支。	READY
554_ls_4dr	554	Hatchback	Kadett B		4	EU-OPEL-KADETT-B-HATCHBACK-LS-4D-01	MEDIUM	LS 4-door fastback分支。	READY
555_gill	555	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-GILL-2D-01	MEDIUM	Gill Coupé早期车身。	READY
555_ls	555	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	MEDIUM	LS Coupé后期车身。	READY
556_std_2dr	556	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-STD-2D-01	MEDIUM	标准2-door notchback分支。	READY
556_std_4dr	556	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-STD-4D-01	MEDIUM	标准4-door notchback分支。	READY
556_l_2dr	556	Sedan	Kadett B		2	EU-OPEL-KADETT-B-SEDAN-L-2D-01	MEDIUM	L 2-door加长notchback外廓。	READY
556_l_4dr	556	Sedan	Kadett B		4	EU-OPEL-KADETT-B-SEDAN-L-4D-01	MEDIUM	L 4-door加长notchback外廓。	READY
557	557	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	HIGH	1971年后LS Coupé车身。	READY
558_gill	558	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-GILL-2D-01	MEDIUM	Gill Coupé早期车身。	READY
558_ls	558	Coupe	Kadett B		2	EU-OPEL-KADETT-B-COUPE-LS-2D-01	MEDIUM	LS Coupé后期车身。	READY
559_std_3dr	559	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-STD-3D-01	MEDIUM	标准3-door Caravan分支。	READY
559_std_5dr	559	Wagon	Kadett B		5	EU-OPEL-KADETT-B-WAGON-STD-5D-01	MEDIUM	标准5-door Caravan分支。	READY
559_l_3dr	559	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-L-3D-01	MEDIUM	L 3-door Caravan加长外廓。	READY
559_l_5dr	559	Wagon	Kadett B		5	EU-OPEL-KADETT-B-WAGON-L-5D-01	MEDIUM	L 5-door Caravan加长外廓。	READY
560_std_3dr	560	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-STD-3D-01	MEDIUM	标准3-door Caravan分支。	READY
560_l_3dr	560	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-L-3D-01	MEDIUM	L 3-door Caravan加长外廓。	READY
561_std_3dr	561	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-STD-3D-01	MEDIUM	标准3-door Caravan分支。	READY
561_std_5dr	561	Wagon	Kadett B		5	EU-OPEL-KADETT-B-WAGON-STD-5D-01	MEDIUM	标准5-door Caravan分支。	READY
561_l_3dr	561	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-L-3D-01	MEDIUM	L 3-door Caravan加长外廓。	READY
561_l_5dr	561	Wagon	Kadett B		5	EU-OPEL-KADETT-B-WAGON-L-5D-01	MEDIUM	L 5-door Caravan加长外廓。	READY
562_std_3dr	562	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-STD-3D-01	MEDIUM	标准3-door Caravan分支。	READY
562_l_3dr	562	Wagon	Kadett B		3	EU-OPEL-KADETT-B-WAGON-L-3D-01	MEDIUM	L 3-door Caravan加长外廓。	READY
563	563	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
564_2dr	564	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
564_4dr	564	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
565	565	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
566	566	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
567_2dr	567	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
567_4dr	567	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
568	568	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
569_2dr	569	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
569_4dr	569	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
570	570	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
571	571	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
572	572	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
573	573	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
574_2dr	574	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
574_4dr	574	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
575	575	Hatchback	Kadett C		3	EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	HIGH	3-door City Hatchback物理分支。	READY
576_2dr	576	Sedan	Kadett C		2	EU-OPEL-KADETT-C-SEDAN-2D-01	MEDIUM	2-door Sedan物理分支。	READY
576_4dr	576	Sedan	Kadett C		4	EU-OPEL-KADETT-C-SEDAN-4D-01	MEDIUM	4-door Sedan物理分支。	READY
577	577	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	2-door Coupe物理分支。	READY
578	578	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	GT/E使用2-door Coupe外廓。	READY
579	579	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	Rallye使用2-door Coupe外廓。	READY
580	580	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
581	581	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
582	582	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
583	583	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
584	584	Wagon	Kadett C		3	EU-OPEL-KADETT-C-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
585_3dr	585	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
585_5dr	585	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
586_3dr	586	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
586_5dr	586	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
587_3dr	587	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
587_5dr	587	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
588_3dr	588	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
588_5dr	588	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
589_3dr	589	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
589_5dr	589	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
590_3dr	590	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
590_5dr	590	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
591	591	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-GTE-HATCHBACK-3D-01	HIGH	GT/E宽体3-door外廓。	READY
592_3dr	592	Hatchback	Kadett D		3	EU-OPEL-KADETT-D-HATCHBACK-3D-01	HIGH	3-door Hatchback物理分支。	READY
592_5dr	592	Hatchback	Kadett D		5	EU-OPEL-KADETT-D-HATCHBACK-5D-01	HIGH	5-door Hatchback物理分支。	READY
593	593	Coupe	Kadett C		2	EU-OPEL-KADETT-C-COUPE-2D-01	HIGH	GT/E使用2-door Coupe外廓。	READY
594_3dr	594	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
594_5dr	594	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
595_3dr	595	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
595_5dr	595	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
596_3dr	596	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
596_5dr	596	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
597_3dr	597	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
597_5dr	597	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
598_3dr	598	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
598_5dr	598	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
599_3dr	599	Wagon	Kadett D		3	EU-OPEL-KADETT-D-WAGON-3D-01	HIGH	3-door Caravan物理分支。	READY
599_5dr	599	Wagon	Kadett D		5	EU-OPEL-KADETT-D-WAGON-5D-01	HIGH	5-door Caravan物理分支。	READY
600_3dr	600	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
600_5dr	600	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
601_3dr	601	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
601_5dr	601	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
602_3dr	602	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
602_5dr	602	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
603_3dr	603	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
603_5dr	603	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
604_3dr	604	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
604_5dr	604	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
605_3dr	605	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
605_5dr	605	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
606_3dr	606	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
606_5dr	606	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
607_3dr	607	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
607_5dr	607	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
608_3dr	608	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
608_5dr	608	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
609_3dr	609	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
609_5dr	609	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSI 5-door外观分支。	READY
610_3dr	610	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
610_5dr	610	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	HIGH	GSI 5-door外观分支。	READY
611_3dr	611	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 3-door外观分支。	READY
611_5dr	611	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	HIGH	GSI 5-door外观分支。	READY
612_3dr	612	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	HIGH	GSI 16V 3-door外观分支。	READY
612_5dr	612	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSI 16V 5-door物理分支。	READY
613_3dr	613	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
613_5dr	613	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
614_3dr	614	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
614_5dr	614	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
615_3dr	615	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
615_5dr	615	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
616_3dr	616	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	HIGH	3-door CC物理分支。	READY
616_5dr	616	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	HIGH	5-door CC物理分支。	READY
617	617	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
618	618	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
619	619	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
620	620	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
621	621	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
622	622	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
623	623	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
624	624	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
625	625	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH	4-door Stufenheck车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_501-600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-W109-SEDAN-01	5000	1810	1410	Mercedes-Benz Public Archive – 300 SEL W109 E 28	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL.xhtml?oid=4906
EU-MERCEDES-BENZ-W108-SEDAN-01	4900	1810	1440	Mercedes-Benz Public Archive – 280 SE 3.5	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SE-35.xhtml?oid=4909
EU-MERCEDES-BENZ-W108-SEDAN-LWB-01	5000	1810	1440	Mercedes-Benz Public Archive – 280 SE long wheelbase / 280 SEL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SE-long-wheelbase-from-091969-280-SEL.xhtml?oid=4921
EU-MERCEDES-BENZ-W109-SEDAN-63-01	5000	1810	1420	Mercedes-Benz Public Archive – 300 SEL 6.3	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SEL-63.xhtml?oid=4903
EU-OPEL-CORSA-A-SEDAN-2D-01	3955	1540	1360	Auto-Data – Opel Corsa A Sedan; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-sedan-generation-5145;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-SEDAN-4D-01	3955	1540	1360	Auto-Data – Opel Corsa A Sedan; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-sedan-generation-5145;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	3622	1532	1365	Auto-Data – Opel Corsa A model overview; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-model-248;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	3652	1542	1365	Auto-Data – Opel Corsa A facelift 1990; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-facelift-1990-1.4i-82hp-2130;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	3622	1532	1365	Auto-Data – Opel Corsa A model overview; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-model-248;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	3652	1542	1365	Auto-Data – Opel Corsa A facelift 1990; Opel Corsa A chassis-number reference	https://www.auto-data.net/en/opel-corsa-a-facelift-1990-1.4i-82hp-2130;https://www.opel-infos.de/fgst/fgst_mj82-97.html
EU-OPEL-KADETT-B-SEDAN-STD-2D-01	4105	1573	1400	ADAC – Opel Kadett B standard sedan; Automobile-Catalog – Opel Kadett 1100	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345438/;https://www.automobile-catalog.com/car/1968/2414120/opel_kadett_1100.html
EU-OPEL-KADETT-B-SEDAN-STD-4D-01	4105	1573	1400	ADAC – Opel Kadett B standard sedan; Automobile-Catalog – Opel Kadett 1100	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345438/;https://www.automobile-catalog.com/car/1968/2414120/opel_kadett_1100.html
EU-OPEL-KADETT-B-SEDAN-L-2D-01	4182	1573	1405	ADAC – Opel Kadett B L sedan; Automobile-Catalog – Opel Kadett L 1100	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345437/;https://www.automobile-catalog.com/car/1968/2414150/opel_kadett_l_1100.html
EU-OPEL-KADETT-B-SEDAN-L-4D-01	4182	1573	1405	ADAC – Opel Kadett B L sedan; Automobile-Catalog – Opel Kadett L 1100	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345437/;https://www.automobile-catalog.com/car/1968/2414150/opel_kadett_l_1100.html
EU-OPEL-KADETT-B-HATCHBACK-LS-2D-01	4182	1573	1405	ADAC – Opel Kadett B LS fastback; Opel official Kadett B body archive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345447/;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-HATCHBACK-LS-4D-01	4182	1573	1405	ADAC – Opel Kadett B LS fastback; Opel official Kadett B body archive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/kadett/b/345447/;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-COUPE-GILL-2D-01	4182	1573	1405	Automobile-Catalog – Opel Kadett Coupe; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1968/2414360/opel_kadett_coupe_1700_s.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-COUPE-LS-2D-01	4182	1573	1405	Automobile-Catalog – Opel Kadett LS Coupe; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1968/2414315/opel_kadett_ls_coupe_1100_s.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-WAGON-STD-3D-01	4100	1573	1395	Automobile-Catalog – Opel Kadett Caravan 1100; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1967/2414210/opel_kadett_caravan_1100.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-WAGON-STD-5D-01	4100	1573	1395	Automobile-Catalog – Opel Kadett Caravan 1100; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1967/2414210/opel_kadett_caravan_1100.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-WAGON-L-3D-01	4177	1573	1395	Automobile-Catalog – Opel Kadett Caravan L 1100 S; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1969/2414255/opel_kadett_caravan_l_1100_s.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-B-WAGON-L-5D-01	4177	1573	1395	Automobile-Catalog – Opel Kadett Caravan L 1100 S; Opel official Kadett B body archive	https://www.automobile-catalog.com/car/1969/2414255/opel_kadett_caravan_l_1100_s.html;https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago
EU-OPEL-KADETT-C-CITY-HATCHBACK-3D-01	3893	1580	1380	Automobile-Catalog – 1978 Opel Kadett City Berlina 1.2 S	https://www.automobile-catalog.com/car/1978/2419145/opel_kadett_city_berlina_1_2_s.html
EU-OPEL-KADETT-C-SEDAN-2D-01	4124	1580	1375	Automobile-Catalog – 1978 Opel Kadett 1.2 N	https://www.automobile-catalog.com/car/1978/2419385/opel_kadett_1_2_n.html
EU-OPEL-KADETT-C-SEDAN-4D-01	4124	1580	1375	Automobile-Catalog – 1978 Opel Kadett 1.2 N	https://www.automobile-catalog.com/car/1978/2419385/opel_kadett_1_2_n.html
EU-OPEL-KADETT-C-COUPE-2D-01	4127	1580	1340	Auto-Data – Opel Kadett C Coupe; Automobile-Catalog – 1979 Opel Kadett Coupe Luxe 1.2 S	https://www.auto-data.net/en/opel-kadett-c-coupe-generation-512;https://www.automobile-catalog.com/car/1979/2418590/opel_kadett_coupe_luxe_1_2_s.html
EU-OPEL-KADETT-C-WAGON-3D-01	4138	1580	1385	Automobile-Catalog – 1978 Opel Kadett Caravan 1.2 N	https://www.automobile-catalog.com/car/1978/2419505/opel_kadett_caravan_1_2_n.html
EU-OPEL-KADETT-D-HATCHBACK-3D-01	3998	1636	1380	Automobile-Catalog – 1983 Opel Kadett 1.6 D Hatch; Auto-Data – Opel Kadett D	https://www.automobile-catalog.com/car/1983/2439245/opel_kadett_1_6_d_hatch.html;https://www.auto-data.net/en/opel-kadett-d-generation-507
EU-OPEL-KADETT-D-HATCHBACK-5D-01	3998	1636	1380	Automobile-Catalog – 1983 Opel Kadett 1.6 D Hatch; Auto-Data – Opel Kadett D	https://www.automobile-catalog.com/car/1983/2439245/opel_kadett_1_6_d_hatch.html;https://www.auto-data.net/en/opel-kadett-d-generation-507
EU-OPEL-KADETT-D-GTE-HATCHBACK-3D-01	3998	1656	1380	Automobile-Catalog – 1983 Opel Kadett D GTE; Carfolio – Opel Kadett 1.8 GTE	https://www.automobile-catalog.com/make/opel/kadett_d/kadett_d_gte/1983.html;https://www.carfolio.com/opel-kadett-1.8-gte-39039
EU-OPEL-KADETT-D-WAGON-3D-01	4207	1636	1400	Auto-Data – Opel Kadett D Caravan; Opel Team Niedersachsen – Kadett D technical data	https://www.auto-data.net/en/opel-kadett-d-caravan-generation-508;https://www.opel-team-niedersachsen.de/kadett-d.html
EU-OPEL-KADETT-D-WAGON-5D-01	4207	1636	1400	Auto-Data – Opel Kadett D Caravan; Opel Team Niedersachsen – Kadett D technical data	https://www.auto-data.net/en/opel-kadett-d-caravan-generation-508;https://www.opel-team-niedersachsen.de/kadett-d.html
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400	Automobile-Catalog – 1986 Opel Kadett 1.2 S; Opel Kadett E body overview	https://www.automobile-catalog.com/car/1986/2458235/opel_kadett_1_2_s_5-speed.html;https://en.wikipedia.org/wiki/Opel_Kadett_E
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400	Automobile-Catalog – 1986 Opel Kadett 1.2 S; Opel Kadett E body overview	https://www.automobile-catalog.com/car/1986/2458235/opel_kadett_1_2_s_5-speed.html;https://en.wikipedia.org/wiki/Opel_Kadett_E
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395	Automobile-Catalog – 1988 Opel Kadett GSi; Auto-Data – Opel Kadett E CC 2.0 GSI	https://www.automobile-catalog.com/car/1988/2460140/opel_kadett_gsi.html;https://www.auto-data.net/en/opel-kadett-e-cc-2.0-gsi-115hp-1917
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395	Automobile-Catalog – 1988 Opel Kadett GSi; Auto-Data – Opel Kadett E CC 2.0 GSI	https://www.automobile-catalog.com/car/1988/2460140/opel_kadett_gsi.html;https://www.auto-data.net/en/opel-kadett-e-cc-2.0-gsi-115hp-1917
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400	Automobile-Catalog – 1987 Opel Kadett 4-door 1.6 S; Auto-Data – Opel Kadett model overview	https://www.automobile-catalog.com/car/1987/2459495/opel_kadett_4d_1_6_s.html;https://www.auto-data.net/en/opel-kadett-model-244
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_501-600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago "https://www.media.stellantis.com/em-en/opel/press/opel-kadett-das-auto-kadett-b-celebrates-debut-60-years-ago"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_501-600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_501-600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（800 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（189 行）
