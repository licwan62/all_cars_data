# 任务：all 第 401-500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0005__b17c10ac


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 401-500 行

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
all 第 401-500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	123 t-Model	230 TE	Kombi	Heckantrieb	Benzin	100	136	Apr 1980	Nov 1985	2024-03-01	423
Mercedes-benz	123 t-Model	230 T	Kombi	Heckantrieb	Benzin	80	109	Sep 1977	Mar 1980	2024-03-01	424
Mercedes-benz	123 t-Model	250 T	Kombi	Heckantrieb	Benzin	95	129	May 1978	Oct 1979	2024-03-01	425
Mercedes-benz	123 t-Model	250 T	Kombi	Heckantrieb	Benzin	103	140	May 1978	Aug 1982	2024-03-01	426
Mercedes-benz	123 t-Model	280 TE	Kombi	Heckantrieb	Benzin	136	185	Sep 1977	Nov 1985	2024-03-01	427
Mercedes-benz	123 t-Model	240 T D	Kombi	Heckantrieb	Diesel	53	72	Mar 1979	Dec 1985	2024-03-01	428
Mercedes-benz	123 t-Model	240 T D	Kombi	Heckantrieb	Diesel	48	65	Sep 1977	Feb 1979	2024-03-01	429
Chevrolet	Matiz	0.8 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	38	52	Mar 2005	Dec 2007	2024-03-01	430
Mercedes-benz	123 t-Model	300 T D	Kombi	Heckantrieb	Diesel	59	80	Sep 1977	Oct 1985	2024-03-01	431
Mercedes-benz	123 t-Model	300 T D	Kombi	Heckantrieb	Diesel	65	88	Mar 1979	Nov 1985	2024-03-01	432
Mercedes-benz	123 t-Model	300 T Turbo-d	Kombi	Heckantrieb	Diesel	92	125	Oct 1980	Nov 1985	2024-03-01	433
Citroën	C4 ii	1.6 VTI 120	Schrägheck	Frontantrieb	Benzin	88	120	Nov 2009	Dec 2016	2024-03-01	434
Mercedes-benz	124	200	Stufenheck	Heckantrieb	Benzin	75	102	Jan 1986	May 1990	2024-03-01	435
Mercedes-benz	124	200	Stufenheck	Heckantrieb	Benzin	80	109	Dec 1985	May 1990	2024-03-01	436
Mercedes-benz	124	200 E	Stufenheck	Heckantrieb	Benzin	87	118	Sep 1988	Aug 1993	2024-03-01	437
Mercedes-benz	124	200 E	Stufenheck	Heckantrieb	Benzin	90	122	Sep 1988	Dec 1989	2024-03-01	438
Mercedes-benz	124	230 E	Stufenheck	Heckantrieb	Benzin	97	132	Dec 1984	Mar 1992	2024-03-01	439
Mercedes-benz	124	230 E	Stufenheck	Heckantrieb	Benzin	100	136	Jan 1985	Jun 1993	2024-03-01	440
Mercedes-benz	124	260 E 4-matic	Stufenheck	Allrad	Benzin	118	160	Sep 1986	Aug 1992	2024-03-01	441
Mercedes-benz	124	260 E	Stufenheck	Heckantrieb	Benzin	118	160	Sep 1985	Aug 1992	2024-03-01	442
Mercedes-benz	124	260 E	Stufenheck	Heckantrieb	Benzin	122	166	Sep 1985	Dec 1989	2024-03-01	443
Mercedes-benz	124	260 E 4-matic	Stufenheck	Allrad	Benzin	122	166	Dec 1986	Dec 1989	2024-03-01	444
Mercedes-benz	124	300 E	Stufenheck	Heckantrieb	Benzin	138	188	Jan 1985	Dec 1985	2024-03-01	445
Mercedes-benz	124	300 E	Stufenheck	Heckantrieb	Benzin	132	180	Aug 1985	Aug 1992	2024-03-01	446
Mercedes-benz	124	300 E 4-matic	Stufenheck	Allrad	Benzin	132	180	Sep 1986	Jun 1993	2024-03-01	447
Mercedes-benz	124	300 E 4-matic	Stufenheck	Allrad	Benzin	138	188	Sep 1986	Feb 1992	2024-03-01	448
Mercedes-benz	124	300 E	Stufenheck	Heckantrieb	Benzin	138	188	Jun 1985	Aug 1992	2024-03-01	449
Mercedes-benz	124	200 D	Stufenheck	Heckantrieb	Diesel	53	72	Dec 1984	Aug 1989	2024-03-01	450
Mercedes-benz	124	200 D	Stufenheck	Heckantrieb	Diesel	55	75	Aug 1989	Jun 1993	2024-03-01	451
Mercedes-benz	124	250 D	Stufenheck	Heckantrieb	Diesel	66	90	Apr 1985	Jun 1993	2024-03-01	452
Mercedes-benz	124	250 D	Stufenheck	Heckantrieb	Diesel	69	94	Jan 1989	Jun 1993	2024-03-01	453
Mercedes-benz	E-Klasse	E 250 D	Stufenheck	Heckantrieb	Diesel	83	113	Jul 1993	Jun 1995	2024-03-01	454
Mercedes-benz	124	250 Turbo-d	Stufenheck	Heckantrieb	Diesel	93	126	Sep 1988	Jun 1993	2024-03-01	455
Mercedes-benz	124	300 D	Stufenheck	Heckantrieb	Diesel	80	109	Dec 1984	Aug 1989	2024-03-01	456
Mercedes-benz	124	300 D 4-matic	Stufenheck	Allrad	Diesel	80	109	Sep 1986	Aug 1992	2024-03-01	457
Mercedes-benz	124	300 D	Stufenheck	Heckantrieb	Diesel	81	110	Jun 1990	Jun 1993	2024-03-01	458
Mercedes-benz	124	300 D 4-matic	Stufenheck	Allrad	Diesel	83	113	Aug 1989	Jun 1993	2024-03-01	459
Mercedes-benz	124	300 D	Stufenheck	Heckantrieb	Diesel	83	113	Aug 1989	Jun 1993	2024-03-01	460
Mercedes-benz	E-Klasse	E 300 D	Stufenheck	Heckantrieb	Diesel	100	136	Jul 1993	Jun 1995	2024-03-01	461
Mercedes-benz	124	300 Turbo-d 4-matic	Stufenheck	Allrad	Diesel	105	143	Sep 1986	Sep 1988	2024-03-01	462
Citroën	C4 ii	1.4 VTI 95	Schrägheck	Frontantrieb	Benzin	70	95	Nov 2009	Nov 2015	2024-07-01	463
Mercedes-benz	124	300 Turbo-d 4-matic	Stufenheck	Allrad	Diesel	108	147	Jan 1988	Jun 1993	2024-03-01	464
Mercedes-benz	124	300 Turbo-d	Stufenheck	Heckantrieb	Diesel	108	147	Sep 1988	Jun 1993	2024-03-01	465
Mercedes-benz	124	200	Stufenheck	Heckantrieb	Benzin	77	105	Jan 1986	Oct 1992	2024-03-01	466
Citroën	C4 ii	1.6 THP 155	Schrägheck	Frontantrieb	Benzin	115	156	Nov 2009	Dec 2016	2024-03-01	467
Mercedes-benz	E-Klasse	E 200	Stufenheck	Heckantrieb	Benzin	100	136	Jun 1993	Jun 1995	2024-03-01	468
Mercedes-benz	E-Klasse	E 220	Stufenheck	Heckantrieb	Benzin	110	150	Jun 1993	Jun 1995	2024-03-01	469
Citroën	C4 ii	1.6 HDI 90	Schrägheck	Frontantrieb	Diesel	68	92	Nov 2009	-	2024-03-01	470
Mitsubishi	Outlander ii	2	SUV	Frontantrieb	Benzin	108	147	Nov 2006	Nov 2012	2024-03-01	471
Citroën	C4 ii	1.6 HDI 110	Schrägheck	Frontantrieb	Diesel	82	112	Nov 2009	-	2024-03-01	472
Mercedes-benz	E-Klasse	E 280	Stufenheck	Heckantrieb	Benzin	142	193	Jun 1993	Jun 1995	2024-03-01	473
Mercedes-benz	E-Klasse	E 280	Stufenheck	Heckantrieb	Benzin	145	197	Jun 1993	Jun 1995	2024-03-01	474
Citroën	C4 ii	2.0 HDI / Bluehdi 150	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2009	-	2024-03-01	475
Mitsubishi	Outlander ii	2.2 Di-d	SUV	Frontantrieb	Diesel	130	177	Nov 2006	Nov 2012	2024-03-01	476
Mercedes-benz	124	300 E-24	Stufenheck	Heckantrieb	Benzin	162	220	Sep 1988	Aug 1992	2024-03-01	477
Mercedes-benz	E-Klasse	E 320	Stufenheck	Heckantrieb	Benzin	162	220	Jun 1993	Jun 1995	2024-03-01	478
Mercedes-benz	E-Klasse	E 420	Stufenheck	Heckantrieb	Benzin	205	279	Jun 1993	Jun 1995	2024-03-01	479
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	235	320	Jun 1993	Jun 1995	2024-03-01	480
Mercedes-benz	124	500 E	Stufenheck	Heckantrieb	Benzin	240	326	Jan 1991	Jun 1993	2024-03-01	481
Mercedes-benz	124	200 T	Kombi	Heckantrieb	Benzin	77	105	Jan 1986	May 1990	2024-03-01	482
Mercedes-benz	124	200 T	Kombi	Heckantrieb	Benzin	80	109	Sep 1985	Aug 1989	2024-03-01	483
Mercedes-benz	124	200 TE	Kombi	Heckantrieb	Benzin	87	118	Sep 1988	Aug 1992	2024-03-01	484
Mercedes-benz	124	200 TE	Kombi	Heckantrieb	Benzin	90	122	Sep 1988	Dec 1989	2024-03-01	485
Mercedes-benz	124	230 TE CAT	Kombi	Heckantrieb	Benzin	97	132	Jun 1989	Aug 1992	2024-03-01	486
Mercedes-benz	124	230 TE	Kombi	Heckantrieb	Benzin	100	136	Sep 1985	Aug 1992	2024-03-01	487
Mercedes-benz	124	300 TE 4-matic	Kombi	Allrad	Benzin	132	180	Sep 1986	Jun 1993	2024-03-01	488
Mercedes-benz	124	300 TE	Kombi	Heckantrieb	Benzin	132	180	Jan 1986	Aug 1992	2024-03-01	489
Mercedes-benz	124	300 TE	Kombi	Heckantrieb	Benzin	138	188	Jan 1986	Dec 1989	2024-03-01	490
Mercedes-benz	124	300 TE 4-matic	Kombi	Allrad	Benzin	138	188	Sep 1986	Dec 1989	2024-03-01	491
Mercedes-benz	124	200 T D	Kombi	Heckantrieb	Diesel	53	72	Sep 1985	Aug 1991	2024-03-01	492
Mercedes-benz	124	200 T D	Kombi	Heckantrieb	Diesel	55	75	Sep 1988	Aug 1991	2024-03-01	493
Mercedes-benz	124	250 T D	Kombi	Heckantrieb	Diesel	66	90	Sep 1985	Jun 1993	2024-03-01	494
Mercedes-benz	124	250 T D	Kombi	Heckantrieb	Diesel	69	94	Jan 1989	Jun 1993	2024-03-01	495
Mercedes-benz	124	300 T D	Kombi	Heckantrieb	Diesel	80	109	Sep 1986	Jun 1993	2024-03-01	496
Mercedes-benz	124	300 T D	Kombi	Heckantrieb	Diesel	81	110	Jan 1989	Jun 1993	2024-03-01	497
Mercedes-benz	124	300 T D	Kombi	Heckantrieb	Diesel	83	113	Jan 1989	Jun 1993	2024-03-01	498
Mercedes-benz	E-Klasse	E 300 TD	Kombi	Heckantrieb	Diesel	100	136	Jun 1993	Jun 1996	2024-03-01	499
Mitsubishi	Outlander ii	2.2 Di-d 4WD	SUV	Allrad	Diesel	130	177	Nov 2006	Nov 2012	2024-03-01	500
Mercedes-benz	124	300 T Turbo-d 4-matic	Kombi	Allrad	Diesel	105	143	Sep 1986	Jan 1989	2024-03-01	501
Mercedes-benz	124	300 T Turbo-d 4-matic	Kombi	Allrad	Diesel	108	147	Jan 1989	Jun 1993	2024-03-01	502
Chevrolet	Matiz	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	49	67	Mar 2005	Mar 2011	2024-03-01	503
Fiat	Panda	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Mar 2010	Aug 2013	2024-03-01	504
Porsche	Boxster	3.4	Cabriolet	Heckantrieb	Benzin	235	320	Feb 2010	Dec 2011	2024-03-01	505
Mercedes-benz	E-Klasse	E 200 T	Kombi	Heckantrieb	Benzin	100	136	Jun 1993	Jun 1996	2024-03-01	507
Mercedes-benz	E-Klasse	E 220 T	Kombi	Heckantrieb	Benzin	110	150	Jun 1993	Jun 1996	2024-03-01	508
Peugeot	205 i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	85	116	Feb 1983	Jul 1987	2024-03-01	509
Mercedes-benz	E-Klasse	E 280 T	Kombi	Heckantrieb	Benzin	145	197	Jun 1993	Jun 1996	2024-03-01	510
Mercedes-benz	124	300 Te-24	Kombi	Heckantrieb	Benzin	162	220	Sep 1989	Aug 1992	2024-03-01	513
Mercedes-benz	E-Klasse	E 320 T	Kombi	Heckantrieb	Benzin	162	220	Jun 1993	Jun 1996	2024-03-01	514
Mercedes-benz	124	260 TE Fgst.	Kombi	Heckantrieb	Benzin	118	160	Sep 1989	Aug 1992	2024-03-01	515
Mercedes-benz	124	260 TE Fgst.	Kombi	Heckantrieb	Benzin	122	166	Sep 1985	Dec 1989	2024-03-01	516
Mercedes-benz	E-Klasse	E 250 TD	Kombi	Heckantrieb	Diesel	83	113	Jun 1993	Jun 1996	2024-03-01	517
Mercedes-benz	E-Klasse	E 280 T	Kombi	Heckantrieb	Benzin	142	193	Jun 1993	Jun 1996	2024-03-01	518
Seat	Alhambra	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	110	150	Jun 2010	Apr 2015	2024-03-01	519
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Jun 2010	Apr 2015	2025-06-01	520
Seat	Alhambra	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Jun 2010	Feb 2013	2024-03-01	521
Mercedes-benz	S-Klasse	250 S	Stufenheck	Heckantrieb	Benzin	96	130	Jan 1966	Dec 1969	2024-03-01	522
Seat	Ibiza iv	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Jul 2009	May 2015	2025-02-03	523
Mercedes-benz	S-Klasse	250 SE	Stufenheck	Heckantrieb	Benzin	110	150	Jan 1966	Dec 1967	2024-03-01	524
Mercedes-benz	S-Klasse	280 S	Stufenheck	Heckantrieb	Benzin	103	140	Oct 1967	Jul 1972	2024-03-01	525


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类完成首轮处理，100 个输入 Ktype 均已保留并回查。
* Ktype `430`、`503` 分拆为 Matiz M200 改款前与 M250 改款后；`475` 分拆为 C4 II Phase I/II；`504` 分拆为 Panda 169/319；`523` 分拆为三门/五门及改款前后共四个外廓。([汽车目录][1])
* W124/S124 已区分后驱与 4MATIC、轿车与旅行车、Phase I/II，以及 500 E/E 500 宽体外廓；这些分支存在实际高度或宽度差异，不能合并为单一尺寸组。([汽车目录][2])
* Ktype `515`、`516` 的 `Fgst.` 指向 124 系改装用底盘，但现有输入无法确定最终车身制造商、F124/VF124 分支及成品外廓，因此暂不创建猜测性尺寸组。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* 已完全解决 Ktype：98/100
* READY 映射行：105
* PENDING 映射行：2
* 已确认尺寸组：24
* 唯一阻塞 Ktype：`515`、`516`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
423	423	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
424	424	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
425	425	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
426	426	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
427	427	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
428	428	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
429	429	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
430_prefl	430	Hatchback	Matiz II pre-facelift	M200	5	EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	HIGH	M200改款前分支。	READY
430_facelift	430	Hatchback	Matiz II facelift	M250	5	EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	HIGH	M250改款后分支。	READY
431	431	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
432	432	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
433	433	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
434	434	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
435	435	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
436	436	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
437	437	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
438	438	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
439	439	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
440	440	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
441	441	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
442	442	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
443	443	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
444	444	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
445	445	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
446	446	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
447	447	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
448	448	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
449	449	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
450	450	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
451	451	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
452	452	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
453	453	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
454	454	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
455	455	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
456	456	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
457	457	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
458	458	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
459	459	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
460	460	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
461	461	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
462	462	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
463	463	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
464	464	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
465	465	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
466	466	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
467	467	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
468	468	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
469	469	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
470	470	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
471	471	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
472	472	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
473	473	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
474	474	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
475_prefl	475	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH	2.0 HDi 150改款前分支。	READY
475_facelift	475	Hatchback	C4 II Phase II	B7	5	EU-CITROEN-C4-II-PHASE-II-HATCHBACK-01	HIGH	2.0 BlueHDi 150改款后分支。	READY
476	476	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
477	477	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
478	478	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
479	479	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
480	480	Sedan	E-Class W124 Phase II	W124.036	4	EU-MERCEDES-BENZ-W124-E500-FACELIFT-SEDAN-01	HIGH	E 500宽体改款后外廓。	READY
481	481	Sedan	124 series 500 E	W124.036	4	EU-MERCEDES-BENZ-W124-500E-PREFL-SEDAN-01	HIGH	500 E宽体改款前外廓。	READY
482	482	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
483	483	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
484	484	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
485	485	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
486	486	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
487	487	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
488	488	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
489	489	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
490	490	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
491	491	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
492	492	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
493	493	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
494	494	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
495	495	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
496	496	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
497	497	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
498	498	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
499	499	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
500	500	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
501	501	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
502	502	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
503_prefl	503	Hatchback	Matiz II pre-facelift	M200	5	EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	HIGH	M200改款前分支。	READY
503_facelift	503	Hatchback	Matiz II facelift	M250	5	EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	HIGH	M250改款后分支。	READY
504_169	504	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-01	HIGH	169代1.2 69 PS分支。	READY
504_319	504	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-01	HIGH	319代1.2 69 PS分支。	READY
505	505	Convertible	Boxster 987.2	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
507	507	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
508	508	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
509	509	Hatchback	205 I GTI		3	EU-PEUGEOT-205-I-GTI-HATCHBACK-01	HIGH		READY
510	510	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
513	513	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
514	514	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
515	515	Wagon	124 series special-purpose chassis				LOW	Fgst.为124系改装底盘；F124/VF124及最终车身制造商未确定。	PENDING: 改装底盘最终车身外廓未确定
516	516	Wagon	124 series special-purpose chassis				LOW	Fgst.为124系改装底盘；F124/VF124及最终车身制造商未确定。	PENDING: 改装底盘最终车身外廓未确定
517	517	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
518	518	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
519	519	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
520	520	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
521	521	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
522	522	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
523_3dr_prefl	523	Hatchback	Ibiza IV	6J1	3	EU-SEAT-IBIZA-IV-3D-PREFL-HATCHBACK-01	HIGH	6J1三门SC改款前分支。	READY
523_3dr_facelift	523	Hatchback	Ibiza IV facelift 2012	6J1	3	EU-SEAT-IBIZA-IV-3D-FACELIFT-HATCHBACK-01	HIGH	6J1三门SC 2012改款分支。	READY
523_5dr_prefl	523	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-5D-PREFL-HATCHBACK-01	HIGH	6J5五门改款前分支。	READY
523_5dr_facelift	523	Hatchback	Ibiza IV facelift 2012	6J5	5	EU-SEAT-IBIZA-IV-5D-FACELIFT-HATCHBACK-01	HIGH	6J5五门2012改款分支。	READY
524	524	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
525	525	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-123-S123-WAGON-01	4725	1786	1470	Automobile-Catalog 1980 Mercedes-Benz 230 TE	https://www.automobile-catalog.com/car/1980/1473095/mercedes-benz_230_te.html
EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	3495	1495	1500	Automobile-Catalog 2005 Chevrolet Matiz 0.8 S	https://www.automobile-catalog.com/car/2005/559475/chevrolet_matiz_0_8_s.html
EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	3495	1495	1500	ADAC Chevrolet Matiz 0.8 LPG S	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/chevrolet/matiz/2generation-facelift/341319/
EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	4329	1789	1498	Automobile-Catalog 2011 Citroën C4 HDi 150	https://www.automobile-catalog.com/car/2011/1451930/citroen_c4_hdi_150_tendance.html
EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	4740	1740	1428	Automobile-Catalog 1992 Mercedes-Benz 300 E	https://www.automobile-catalog.com/car/1992/1514555/mercedes-benz_300_e.html
EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	4740	1740	1450	Automobile-Catalog 1992 Mercedes-Benz 300 E 4MATIC	https://www.automobile-catalog.com/car/1992/1516205/mercedes-benz_300_e_4matic_automatic.html
EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	4740	1740	1430	Automobile-Catalog 1994 Mercedes-Benz E 200	https://www.automobile-catalog.com/car/1994/1519400/mercedes-benz_e_200.html
EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	4665	1800	1680	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D 177 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-177hp-4wd-42194
EU-CITROEN-C4-II-PHASE-II-HATCHBACK-01	4329	1789	1498	Automobile-Catalog 2015 Citroën C4 BlueHDi 150	https://www.automobile-catalog.com/car/2015/2139845/citroen_c4_bluehdi_150.html
EU-MERCEDES-BENZ-W124-E500-FACELIFT-SEDAN-01	4750	1796	1410	Automobile-Catalog 1993 Mercedes-Benz E 500	https://www.automobile-catalog.com/car/1993/1519700/mercedes-benz_e_500.html
EU-MERCEDES-BENZ-W124-500E-PREFL-SEDAN-01	4750	1796	1410	Automobile-Catalog 1991 Mercedes-Benz 500 E	https://www.automobile-catalog.com/car/1991/1514705/mercedes-benz_500_e.html
EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	4765	1740	1489	Automobile-Catalog 1992 Mercedes-Benz 300 TE	https://www.automobile-catalog.com/car/1992/1517555/mercedes-benz_300_te.html
EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	4765	1740	1497	Automobile-Catalog 1992 Mercedes-Benz 300 TE 4MATIC	https://www.automobile-catalog.com/car/1992/1518785/mercedes-benz_300_te_4matic_automatic.html
EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	4765	1740	1490	Automobile-Catalog 1994 Mercedes-Benz E 320 T-Modell	https://www.automobile-catalog.com/car/1994/1520015/mercedes-benz_e_320_t-modell.html
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540	Automobile-Catalog 2010 Fiat Panda 1.2 Active Euro 5	https://www.automobile-catalog.com/car/2010/1456145/fiat_panda_1_2_active_euro_5.html
EU-FIAT-PANDA-III-319-HATCHBACK-01	3653	1643	1551	Automobile-Catalog 2012 Fiat Panda 1.2 EasyPower Pop	https://www.automobile-catalog.com/car/2012/1770530/fiat_panda_1_2_easypower_pop.html
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1294	Stuttcars Porsche Boxster S 2009-2012	https://www.stuttcars.com/porsche-boxster-s-2009-2012/
EU-PEUGEOT-205-I-GTI-HATCHBACK-01	3705	1589	1355	Automobile-Catalog 1987 Peugeot 205 GTI 115ch	https://www.automobile-catalog.com/car/1987/2575205/peugeot_205_gti_115ch.html
EU-SEAT-ALHAMBRA-II-7N-MPV-01	4854	1904	1720	Automobile-Catalog 2011 Seat Alhambra 2.0 TDI CR 170 DSG	https://www.automobile-catalog.com/car/2011/3100700/seat_alhambra_2_0_tdi_cr_170_dsg.html
EU-MERCEDES-BENZ-W108-SEDAN-01	4900	1810	1440	Automobile-Catalog 1967 Mercedes-Benz 250 S	https://www.automobile-catalog.com/car/1967/1465040/mercedes-benz_250_s.html
EU-SEAT-IBIZA-IV-3D-PREFL-HATCHBACK-01	4034	1693	1428	Automobile-Catalog 2010 Seat Ibiza SC 1.2 12V 60	https://www.automobile-catalog.com/car/2010/3094730/seat_ibiza_sc_1_2_12v_60.html
EU-SEAT-IBIZA-IV-3D-FACELIFT-HATCHBACK-01	4043	1693	1428	Auto-Data Seat Ibiza IV SC facelift 1.2 12V 60	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.2-12v-60hp-19319
EU-SEAT-IBIZA-IV-5D-PREFL-HATCHBACK-01	4052	1693	1445	Automobile-Catalog 2010 Seat Ibiza 1.2 12V 60	https://www.automobile-catalog.com/car/2010/3094850/seat_ibiza_1_2_12v_60.html
EU-SEAT-IBIZA-IV-5D-FACELIFT-HATCHBACK-01	4061	1693	1445	Auto-Data Seat Ibiza IV facelift 1.2 12V 60	https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-1.2-12v-60hp-16881
```

## 下一步优先处理

1. 只处理 Ktype `515`、`516`：确认 `260 TE Fgst.` 对应的 F124/VF124 底盘分支、轴距及最终车身制造商。
2. 若无法确定统一成品外廓，则按已确认的不同改装车身分别派生 `id`，不得套用普通 S124 旅行车尺寸。
3. 两条 PENDING 消除后，只进行一次表头、唯一键、外键闭合和来源非空的机械收尾，然后直接输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2005/559475/chevrolet_matiz_0_8_s.html "https://www.automobile-catalog.com/car/2005/559475/chevrolet_matiz_0_8_s.html"
[2]: https://www.automobile-catalog.com/car/1992/1514555/mercedes-benz_300_e.html "https://www.automobile-catalog.com/car/1992/1514555/mercedes-benz_300_e.html"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/260-E-long-wheelbase-chassis.xhtml?oid=5286&utm_source=chatgpt.com "260 E long-wheelbase chassis"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Ktype `515`、`516` 已确认是普通后驱 `S124` 五门旅行车目录条目，不是独立改装底盘外廓；现复用已确认的 `EU-MERCEDES-BENZ-S124-PHASE([Bendix][1])([Bendix][1])
* 已完成轻量机械收尾：固定表头、唯一主键、映射外键闭合、三维与来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100/100
* READY 映射行：107
* PENDING 映射行：0
* DIMENSION_GROUP：24
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一且引用闭合：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
423	423	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
424	424	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
425	425	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
426	426	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
427	427	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
428	428	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
429	429	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
430_prefl	430	Hatchback	Matiz II pre-facelift	M200	5	EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	HIGH	M200改款前分支。	READY
430_facelift	430	Hatchback	Matiz II facelift	M250	5	EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	HIGH	M250改款后分支。	READY
431	431	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
432	432	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
433	433	Wagon	123 series T-Model	S123	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH		READY
434	434	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
435	435	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
436	436	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
437	437	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
438	438	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
439	439	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
440	440	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
441	441	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
442	442	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
443	443	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
444	444	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
445	445	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
446	446	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
447	447	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
448	448	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
449	449	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
450	450	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
451	451	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
452	452	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
453	453	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
454	454	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
455	455	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
456	456	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
457	457	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
458	458	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
459	459	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
460	460	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
461	461	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
462	462	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
463	463	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
464	464	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	HIGH		READY
465	465	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
466	466	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
467	467	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
468	468	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
469	469	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
470	470	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
471	471	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
472	472	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH		READY
473	473	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
474	474	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
475_prefl	475	Hatchback	C4 II Phase I	B7	5	EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	HIGH	2.0 HDi 150改款前分支。	READY
475_facelift	475	Hatchback	C4 II Phase II	B7	5	EU-CITROEN-C4-II-PHASE-II-HATCHBACK-01	HIGH	2.0 BlueHDi 150改款后分支。	READY
476	476	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
477	477	Sedan	124 series Phase I	W124	4	EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	HIGH		READY
478	478	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
479	479	Sedan	E-Class W124 Phase II	W124	4	EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	HIGH		READY
480	480	Sedan	E-Class W124 Phase II	W124.036	4	EU-MERCEDES-BENZ-W124-E500-FACELIFT-SEDAN-01	HIGH	E 500宽体改款后外廓。	READY
481	481	Sedan	124 series 500 E	W124.036	4	EU-MERCEDES-BENZ-W124-500E-PREFL-SEDAN-01	HIGH	500 E宽体改款前外廓。	READY
482	482	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
483	483	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
484	484	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
485	485	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
486	486	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
487	487	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
488	488	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
489	489	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
490	490	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
491	491	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
492	492	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
493	493	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
494	494	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
495	495	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
496	496	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
497	497	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
498	498	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
499	499	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
500	500	SUV	Outlander II facelift 2009	CW	5	EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	HIGH	147/177 PS版本均对应2009年改款车身。	READY
501	501	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
502	502	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	HIGH		READY
503_prefl	503	Hatchback	Matiz II pre-facelift	M200	5	EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	HIGH	M200改款前分支。	READY
503_facelift	503	Hatchback	Matiz II facelift	M250	5	EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	HIGH	M250改款后分支。	READY
504_169	504	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-01	HIGH	169代1.2 69 PS分支。	READY
504_319	504	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-01	HIGH	319代1.2 69 PS分支。	READY
505	505	Convertible	Boxster 987.2	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	HIGH		READY
507	507	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
508	508	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
509	509	Hatchback	205 I GTI		3	EU-PEUGEOT-205-I-GTI-HATCHBACK-01	HIGH		READY
510	510	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
513	513	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH		READY
514	514	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
515	515	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH	Fgst.目录条目对应普通后驱S124旅行车。	READY
516	516	Wagon	124 series Phase I	S124	5	EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	HIGH	Fgst.目录条目对应普通后驱S124旅行车。	READY
517	517	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
518	518	Wagon	E-Class S124 Phase II	S124	5	EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	HIGH		READY
519	519	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
520	520	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
521	521	MPV	Alhambra II	7N	5	EU-SEAT-ALHAMBRA-II-7N-MPV-01	HIGH		READY
522	522	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
523_3dr_prefl	523	Hatchback	Ibiza IV	6J1	3	EU-SEAT-IBIZA-IV-3D-PREFL-HATCHBACK-01	HIGH	6J1三门SC改款前分支。	READY
523_3dr_facelift	523	Hatchback	Ibiza IV facelift 2012	6J1	3	EU-SEAT-IBIZA-IV-3D-FACELIFT-HATCHBACK-01	HIGH	6J1三门SC 2012改款分支。	READY
523_5dr_prefl	523	Hatchback	Ibiza IV	6J5	5	EU-SEAT-IBIZA-IV-5D-PREFL-HATCHBACK-01	HIGH	6J5五门改款前分支。	READY
523_5dr_facelift	523	Hatchback	Ibiza IV facelift 2012	6J5	5	EU-SEAT-IBIZA-IV-5D-FACELIFT-HATCHBACK-01	HIGH	6J5五门2012改款分支。	READY
524	524	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
525	525	Sedan	S-Class W108	W108	4	EU-MERCEDES-BENZ-W108-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_401-500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-123-S123-WAGON-01	4725	1786	1470	Automobile-Catalog 1980 Mercedes-Benz 230 TE	https://www.automobile-catalog.com/car/1980/1473095/mercedes-benz_230_te.html
EU-CHEVROLET-MATIZ-M200-HATCHBACK-01	3495	1495	1500	Automobile-Catalog 2005 Chevrolet Matiz 0.8 S	https://www.automobile-catalog.com/car/2005/559475/chevrolet_matiz_0_8_s.html
EU-CHEVROLET-MATIZ-M250-HATCHBACK-01	3495	1495	1500	ADAC Chevrolet Matiz 0.8 LPG S	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/chevrolet/matiz/2generation-facelift/341319/
EU-CITROEN-C4-II-PHASE-I-HATCHBACK-01	4329	1789	1498	Automobile-Catalog 2011 Citroën C4 HDi 150	https://www.automobile-catalog.com/car/2011/1451930/citroen_c4_hdi_150_tendance.html
EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-RWD-01	4740	1740	1428	Automobile-Catalog 1992 Mercedes-Benz 300 E	https://www.automobile-catalog.com/car/1992/1514555/mercedes-benz_300_e.html
EU-MERCEDES-BENZ-W124-PHASE-I-SEDAN-4MATIC-01	4740	1740	1450	Automobile-Catalog 1992 Mercedes-Benz 300 E 4MATIC	https://www.automobile-catalog.com/car/1992/1516205/mercedes-benz_300_e_4matic_automatic.html
EU-MERCEDES-BENZ-W124-PHASE-II-SEDAN-RWD-01	4740	1740	1430	Automobile-Catalog 1994 Mercedes-Benz E 200	https://www.automobile-catalog.com/car/1994/1519400/mercedes-benz_e_200.html
EU-MITSUBISHI-OUTLANDER-II-FACELIFT-SUV-01	4665	1800	1680	Auto-Data Mitsubishi Outlander II facelift 2.2 DI-D 177 4WD	https://www.auto-data.net/en/mitsubishi-outlander-ii-facelift-2009-2.2-di-d-177hp-4wd-42194
EU-CITROEN-C4-II-PHASE-II-HATCHBACK-01	4329	1789	1498	Automobile-Catalog 2015 Citroën C4 BlueHDi 150	https://www.automobile-catalog.com/car/2015/2139845/citroen_c4_bluehdi_150.html
EU-MERCEDES-BENZ-W124-E500-FACELIFT-SEDAN-01	4750	1796	1410	Automobile-Catalog 1993 Mercedes-Benz E 500	https://www.automobile-catalog.com/car/1993/1519700/mercedes-benz_e_500.html
EU-MERCEDES-BENZ-W124-500E-PREFL-SEDAN-01	4750	1796	1410	Automobile-Catalog 1991 Mercedes-Benz 500 E	https://www.automobile-catalog.com/car/1991/1514705/mercedes-benz_500_e.html
EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-RWD-01	4765	1740	1489	Automobile-Catalog 1992 Mercedes-Benz 300 TE	https://www.automobile-catalog.com/car/1992/1517555/mercedes-benz_300_te.html
EU-MERCEDES-BENZ-S124-PHASE-I-WAGON-4MATIC-01	4765	1740	1497	Automobile-Catalog 1992 Mercedes-Benz 300 TE 4MATIC	https://www.automobile-catalog.com/car/1992/1518785/mercedes-benz_300_te_4matic_automatic.html
EU-MERCEDES-BENZ-S124-PHASE-II-WAGON-RWD-01	4765	1740	1490	Automobile-Catalog 1994 Mercedes-Benz E 320 T-Modell	https://www.automobile-catalog.com/car/1994/1520015/mercedes-benz_e_320_t-modell.html
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540	Automobile-Catalog 2010 Fiat Panda 1.2 Active Euro 5	https://www.automobile-catalog.com/car/2010/1456145/fiat_panda_1_2_active_euro_5.html
EU-FIAT-PANDA-III-319-HATCHBACK-01	3653	1643	1551	Automobile-Catalog 2012 Fiat Panda 1.2 EasyPower Pop	https://www.automobile-catalog.com/car/2012/1770530/fiat_panda_1_2_easypower_pop.html
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-01	4342	1801	1294	Stuttcars Porsche Boxster S 2009-2012	https://www.stuttcars.com/porsche-boxster-s-2009-2012/
EU-PEUGEOT-205-I-GTI-HATCHBACK-01	3705	1589	1355	Automobile-Catalog 1987 Peugeot 205 GTI 115ch	https://www.automobile-catalog.com/car/1987/2575205/peugeot_205_gti_115ch.html
EU-SEAT-ALHAMBRA-II-7N-MPV-01	4854	1904	1720	Automobile-Catalog 2011 Seat Alhambra 2.0 TDI CR 170 DSG	https://www.automobile-catalog.com/car/2011/3100700/seat_alhambra_2_0_tdi_cr_170_dsg.html
EU-MERCEDES-BENZ-W108-SEDAN-01	4900	1810	1440	Automobile-Catalog 1967 Mercedes-Benz 250 S	https://www.automobile-catalog.com/car/1967/1465040/mercedes-benz_250_s.html
EU-SEAT-IBIZA-IV-3D-PREFL-HATCHBACK-01	4034	1693	1428	Automobile-Catalog 2010 Seat Ibiza SC 1.2 12V 60	https://www.automobile-catalog.com/car/2010/3094730/seat_ibiza_sc_1_2_12v_60.html
EU-SEAT-IBIZA-IV-3D-FACELIFT-HATCHBACK-01	4043	1693	1428	Auto-Data Seat Ibiza IV SC facelift 1.2 12V 60	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.2-12v-60hp-19319
EU-SEAT-IBIZA-IV-5D-PREFL-HATCHBACK-01	4052	1693	1445	Automobile-Catalog 2010 Seat Ibiza 1.2 12V 60	https://www.automobile-catalog.com/car/2010/3094850/seat_ibiza_1_2_12v_60.html
EU-SEAT-IBIZA-IV-5D-FACELIFT-HATCHBACK-01	4061	1693	1445	Auto-Data Seat Ibiza IV facelift 1.2 12V 60	https://www.auto-data.net/en/seat-ibiza-iv-facelift-2012-1.2-12v-60hp-16881
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_401-500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.bendix.com.au/catalogue/mercedes-benz/124/260-te-fgst-s124?utm_source=chatgpt.com "260 TE FGST. [S124] | Bendix Brakes"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_401-500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_401-500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（601 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（153 行）
