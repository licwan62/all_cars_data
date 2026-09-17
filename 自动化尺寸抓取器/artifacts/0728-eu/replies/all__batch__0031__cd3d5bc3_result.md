# 任务：all 第 3001-3100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0031__cd3d5bc3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3001-3100 行

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
all 第 3001-3100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Austin	Metro	1	Schrägheck	Frontantrieb	Benzin	30	41	Oct 1980	Apr 1990	2024-03-01	3098
Austin	Metro	1	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1980	Apr 1990	2024-03-01	3099
Austin	Metro	1.0 Surf HLE	Schrägheck	Frontantrieb	Benzin	35	48	Oct 1980	Apr 1990	2024-03-01	3100
Austin	Metro	1.3 L, Hle, S	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1980	Apr 1990	2024-03-01	3101
Austin	Metro	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Oct 1980	Apr 1990	2024-03-01	3102
Austin	Metro	1.3	Schrägheck	Frontantrieb	Benzin	52	71	Oct 1980	Dec 1985	2024-03-01	3103
Austin	Metro	1.3 Turbo	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1983	Apr 1990	2024-03-01	3104
Austin	Metro	1.3 Surf	Schrägheck	Frontantrieb	Benzin	44	60	Nov 1985	Apr 1990	2024-03-01	3105
Austin	1000-Series mk ii	1100	Stufenheck	Frontantrieb	Benzin	32	44	Jan 1970	Dec 1974	2024-03-01	3106
Austin	1000-Series mk ii	1300	Stufenheck	Frontantrieb	Benzin	39	53	Jan 1970	Dec 1974	2024-03-01	3107
Austin	1000-Series mk ii	1300 GT	Stufenheck	Frontantrieb	Benzin	50	68	Jan 1970	Dec 1974	2024-03-01	3108
Land Rover	Range rover sport i	5.0 4X4	SUV	Allrad	Benzin	276	375	Jul 2009	Mar 2013	2024-03-01	3113
Fiat	Bravo ii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	66	90	Mar 2008	Dec 2014	2024-03-01	3114
Austin	Maxi i fastback	1500	Schrägheck	Frontantrieb	Benzin	50	68	Apr 1969	Jul 1980	2024-03-01	3115
Austin	Maxi i fastback	1750	Schrägheck	Frontantrieb	Benzin	53	72	Apr 1969	Oct 1980	2024-03-01	3116
Austin	Maxi i fastback	1750 HL	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1972	Oct 1980	2024-03-01	3117
Austin	Allegro i	1.1	Schrägheck	Frontantrieb	Benzin	33	45	May 1973	Oct 1981	2024-03-01	3118
Austin	Allegro i	1.3	Schrägheck	Frontantrieb	Benzin	40	54	May 1973	Mar 1982	2024-03-01	3119
Austin	Allegro i	1.5 Super	Schrägheck	Frontantrieb	Benzin	50	68	May 1973	Mar 1982	2024-03-01	3120
Austin	Maestro	1.3	Schrägheck	Frontantrieb	Benzin	46	63	Mar 1983	Aug 1985	2024-03-01	3121
Austin	Maestro	1.3 LS	Schrägheck	Frontantrieb	Benzin	49	67	Mar 1983	Aug 1990	2024-03-01	3122
Austin	Maestro	1.6	Schrägheck	Frontantrieb	Benzin	59	80	Mar 1983	Oct 1984	2024-03-01	3123
Austin	Maestro	1.6 Mayfair HLS	Schrägheck	Frontantrieb	Benzin	61	83	Mar 1983	Aug 1990	2024-03-01	3124
Austin	Maestro	1.6 MG	Schrägheck	Frontantrieb	Benzin	72	98	Mar 1983	Aug 1985	2024-03-01	3125
Austin	Maestro	1.6 MG	Schrägheck	Frontantrieb	Benzin	73	99	Mar 1983	Aug 1990	2024-03-01	3126
Austin	Maestro	2.0 EFI	Schrägheck	Frontantrieb	Benzin	83	113	Oct 1984	Aug 1990	2024-03-01	3127
Austin	Princess	1800 HL	Stufenheck	Frontantrieb	Benzin	60	82	Apr 1976	Sep 1978	2024-03-01	3128
Austin	Princess	2200 HLS	Stufenheck	Frontantrieb	Benzin	81	110	Apr 1976	Sep 1978	2024-03-01	3129
Austin	Montego	1.6 LS, HL	Stufenheck	Frontantrieb	Benzin	61	83	Apr 1984	Aug 1988	2024-03-01	3130
Austin	Montego	2	Stufenheck	Frontantrieb	Benzin	74	101	Apr 1984	Aug 1988	2024-03-01	3131
Austin	Montego	2.0 Mayfair	Stufenheck	Frontantrieb	Benzin	83	113	Apr 1984	Aug 1988	2024-03-01	3132
Austin	Montego	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	110	150	Apr 1984	Aug 1988	2024-03-01	3133
Austin	Montego	1.6 LS	Kombi	Frontantrieb	Benzin	61	83	Oct 1984	Aug 1988	2024-03-01	3134
Austin	Montego	2.0 HLI	Kombi	Frontantrieb	Benzin	83	113	Oct 1984	Sep 1992	2024-03-01	3135
Rover	Montego	2.0 Gti/lxi	Kombi	Frontantrieb	Benzin	75	102	Dec 1990	Dec 1993	2024-03-01	3136
Jaguar	Xj	3.6	Coupe	Heckantrieb	Benzin	136	185	Jan 1988	May 1992	2024-03-01	3137
Jaguar	Xj	3.6	Coupe	Heckantrieb	Benzin	156	212	Oct 1983	Dec 1989	2024-03-01	3138
Jaguar	Xj	3.6	Coupe	Heckantrieb	Benzin	162	220	Oct 1983	Dec 1988	2024-03-01	3139
Jaguar	Xj	3.6	Coupe	Heckantrieb	Benzin	146	199	Jan 1988	May 1991	2024-03-01	3140
Jaguar	Xj	5.3 H.e.	Coupe	Heckantrieb	Benzin	194	264	Sep 1985	Sep 1992	2024-03-01	3141
Jaguar	Xj	5.3	Coupe	Heckantrieb	Benzin	197	268	Jan 1986	Dec 1989	2024-03-01	3142
Jaguar	Xj	5.3 H.e.	Coupe	Heckantrieb	Benzin	217	295	Jul 1981	Dec 1987	2024-03-01	3143
Jaguar	Xj	5.3	Coupe	Heckantrieb	Benzin	211	287	Sep 1973	May 1992	2024-03-01	3144
Jaguar	Xj	4	Coupe	Heckantrieb	Benzin	163	222	May 1991	Sep 1994	2024-03-01	3145
Jaguar	Xj	5.3	Coupe	Heckantrieb	Benzin	202	275	Jan 1988	Jun 1991	2024-03-01	3146
Jaguar	Xj	5.3	Coupe	Heckantrieb	Benzin	207	282	May 1991	Aug 1993	2024-03-01	3147
Jaguar	Xj	6	Coupe	Heckantrieb	Benzin	222	302	May 1993	Mar 1996	2024-03-01	3148
Jaguar	Xjsc convertible	3.6	Cabriolet	Heckantrieb	Benzin	136	185	Aug 1987	May 1991	2024-03-01	3149
Jaguar	Xjsc convertible	3.6	Cabriolet	Heckantrieb	Benzin	156	212	Aug 1987	May 1991	2024-03-01	3150
Jaguar	Xjsc convertible	3.6	Cabriolet	Heckantrieb	Benzin	162	220	Oct 1986	Dec 1988	2024-03-01	3151
Jaguar	Xjsc convertible	5.3 H.e.	Cabriolet	Heckantrieb	Benzin	194	264	Jul 1985	May 1992	2024-03-01	3152
Jaguar	Xjsc convertible	5.3	Cabriolet	Heckantrieb	Benzin	197	268	Jan 1986	May 1988	2024-03-01	3153
Jaguar	Xjsc convertible	5.3 H.e.	Cabriolet	Heckantrieb	Benzin	217	295	Sep 1985	Dec 1990	2024-03-01	3154
Jaguar	Xjsc convertible	5.3	Cabriolet	Heckantrieb	Benzin	211	287	Jan 1988	May 1992	2024-03-01	3155
Jaguar	Xjsc convertible	4	Cabriolet	Heckantrieb	Benzin	163	222	May 1991	Sep 1994	2024-03-01	3156
Jaguar	Xjsc convertible	5.3	Cabriolet	Heckantrieb	Benzin	202	275	Jan 1988	Sep 1991	2024-03-01	3157
Jaguar	Xjsc convertible	5.3	Cabriolet	Heckantrieb	Benzin	207	282	May 1991	Aug 1993	2024-03-01	3158
Jaguar	Xjsc convertible	6	Cabriolet	Heckantrieb	Benzin	222	302	May 1993	Mar 1996	2024-03-01	3159
Jaguar	Xj	6 2.9	Stufenheck	Heckantrieb	Benzin	108	147	Oct 1986	Aug 1990	2024-03-01	3160
Jaguar	Xj	6 2.9	Stufenheck	Heckantrieb	Benzin	117	159	Oct 1986	Aug 1990	2024-03-01	3161
Jaguar	Xj	3.6	Stufenheck	Heckantrieb	Benzin	136	185	Oct 1986	Aug 1989	2024-03-01	3162
Jaguar	Xj	6 3.4	Stufenheck	Heckantrieb	Benzin	119	162	May 1975	Oct 1986	2024-03-01	3163
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	127	173	Jan 1975	Dec 1979	2024-03-01	3164
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	130	177	Sep 1985	Dec 1986	2024-03-01	3165
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	133	181	Sep 1985	Dec 1986	2024-03-01	3166
Jaguar	Xj	12 5.3	Stufenheck	Heckantrieb	Benzin	186	253	Sep 1973	Dec 1976	2024-03-01	3167
Jaguar	Xj	12 5.3	Stufenheck	Heckantrieb	Benzin	187	254	Aug 1986	Sep 1989	2024-03-01	3168
Jaguar	Xj	Sovereign V12	Stufenheck	Heckantrieb	Benzin	197	268	Jul 1985	Dec 1992	2024-03-01	3169
Rover	Mini	1300	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1992	Nov 2000	2024-03-01	3171
Rover	200 i	213 S	Stufenheck	Frontantrieb	Benzin	54	73	Sep 1985	Sep 1989	2024-03-01	3172
Rover	200 i	216	Stufenheck	Frontantrieb	Benzin	61	83	Mar 1985	Sep 1989	2024-03-01	3173
Rover	200 i	216 Vitesse	Stufenheck	Frontantrieb	Benzin	75	102	Sep 1984	Sep 1989	2024-03-01	3174
Rover	2000-3500	2200	Stufenheck	Heckantrieb	Benzin	83	113	Oct 1973	May 1976	2024-03-01	3175
Rover	2000-3500	3500	Stufenheck	Heckantrieb	Benzin	104	141	Apr 1968	May 1976	2024-03-01	3176
Rover	2000-3500	3500	Stufenheck	Heckantrieb	Benzin	135	184	Apr 1968	May 1976	2024-03-01	3177
Rover	2000-3500	2600 S	Schrägheck	Heckantrieb	Benzin	93	126	Oct 1982	Oct 1986	2024-03-01	3178
Rover	2000-3500	2600	Schrägheck	Heckantrieb	Benzin	99	135	Sep 1977	Oct 1982	2024-03-01	3179
Rover	2000-3500	3500	Schrägheck	Heckantrieb	Benzin	115	156	Jun 1976	Oct 1986	2024-03-01	3180
Rover	800	820 I/si	Schrägheck	Frontantrieb	Benzin	103	140	Oct 1988	Dec 1991	2024-03-01	3181
Rover	800	825 Si/sterling	Stufenheck	Frontantrieb	Benzin	123	167	Oct 1986	Oct 1988	2024-03-01	3182
Rover	800	825 Si/sterling	Stufenheck	Frontantrieb	Benzin	127	173	Jan 1987	Dec 1991	2024-03-01	3183
Rover	800	827 Si/sterling	Stufenheck	Frontantrieb	Benzin	130	177	Feb 1988	Dec 1991	2024-03-01	3184
Rover	800	820 16 V I/si	Stufenheck	Frontantrieb	Benzin	103	140	Oct 1986	Oct 1988	2024-03-01	3185
Rover	800	827 Vitesse/sli	Schrägheck	Frontantrieb	Benzin	130	177	Oct 1988	Dec 1991	2024-03-01	3186
Rover	800	825 D/sd	Schrägheck	Frontantrieb	Diesel	87	118	Jan 1992	Feb 1999	2024-03-01	3187
Rover	800	825 D/sd	Stufenheck	Frontantrieb	Diesel	87	118	Jan 1990	Feb 1999	2024-03-01	3188
Rover	800	820 SI	Schrägheck	Frontantrieb	Benzin	98	133	Oct 1988	Dec 1991	2024-03-01	3189
Rover	800	820 SI	Stufenheck	Frontantrieb	Benzin	98	133	Oct 1988	Dec 1991	2024-03-01	3190
Rover	800	820 I/si	Stufenheck	Frontantrieb	Benzin	100	136	Jan 1992	Feb 1999	2024-03-01	3191
Rover	800	820 I/si	Schrägheck	Frontantrieb	Benzin	100	136	Jan 1991	Feb 1999	2024-03-01	3192
Rover	800	820 16V Turbo	Stufenheck	Frontantrieb	Benzin	132	180	Jan 1992	Feb 1999	2024-03-01	3193
Rover	800	820 16V Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Nov 1991	Feb 1999	2024-03-01	3194
Rover	800	825 Si/sterling Catalytic-conv	Stufenheck	Frontantrieb	Benzin	110	150	Oct 1986	Dec 1991	2024-03-01	3195
Rover	800	827 Vitesse Catalytic-conv	Schrägheck	Frontantrieb	Benzin	124	169	Oct 1988	Dec 1991	2024-03-01	3196
Rover	800	827 Si/sterling Catalytic-conv	Stufenheck	Frontantrieb	Benzin	124	169	Feb 1988	Feb 1999	2024-03-01	3197
Rover	800	827 24V I/si CAT	Schrägheck	Frontantrieb	Benzin	124	169	Jan 1992	Feb 1999	2024-03-01	3198
Rover	800	827 24V	Coupe	Frontantrieb	Benzin	124	169	Aug 1992	Feb 1999	2024-03-01	3199
Land Rover	Range rover i	3.5 Vogue 4X4	Geländewagen geschlossen	Allrad	Benzin	93	126	Aug 1981	Sep 1990	2024-03-01	3208
Land Rover	Range rover i	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	107	146	Jan 1987	Sep 1990	2024-03-01	3209
Land Rover	Range rover i	3.5 Vogue 4X4	Geländewagen geschlossen	Allrad	Benzin	120	163	Oct 1985	Sep 1990	2024-03-01	3210


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 Range Rover Sport L320 改款型与 Fiat Bravo II 198 两个尺寸组，分别覆盖 Ktype `3113`、`3114`。两者来源均明确给出不含后视镜车宽。([汽车目录][1])
* 确认 Princess ADO71 的普通外廓，并将 Ktype `3129` 按 1978 年 7 月前后的外廓变化拆为 `prefl`、`facelift` 两行；改款后的 HLS 复用普通 ADO71 尺寸组。([汽车目录][2])
* 闭合 Montego LM11 第二阶段旅行版、Rover P6 2200 TC 和 Rover SD1 Series 2 三个尺寸组。([汽车目录][3])
* Montego 第一阶段车型存在年份间约 2 mm 高度差异，暂不与第二阶段尺寸组混用。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：8 行，覆盖 7 个输入 Ktype
* PENDING 输入 Ktype：93
* 已确认尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3113	3113	SUV	Range Rover Sport I (facelift 2009)	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-01	HIGH		READY
3114	3114	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-01	HIGH		READY
3128	3128	Sedan	Princess 18-22 Series 1	ADO71	4	EU-PRINCESS-ADO71-SEDAN-01	HIGH		READY
3129_prefl	3129	Sedan	Princess 18-22 Series 1	ADO71	4	EU-PRINCESS-ADO71-SEDAN-HLS-PREFL-01	HIGH	HLS改款前外廓。	READY
3129_facelift	3129	Sedan	Princess 18-22 Series 2	ADO71	4	EU-PRINCESS-ADO71-SEDAN-01	HIGH	1978年7月起Princess 2外廓。	READY
3136	3136	Wagon	Montego phase II	LM11	5	EU-MONTEGO-LM11-WAGON-FACELIFT-01	HIGH		READY
3175	3175	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-2200-TC-01	HIGH	83kW版本对应2200 TC外廓。	READY
3178	3178	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1405115/range_rover_sport_5_0_v8_hse.html
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1456715/fiat_bravo_1_6_multijet_16v_90_dynamic_dpf.html
EU-PRINCESS-ADO71-SEDAN-01	4455	1730	1409	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/27590/princess_1800_hl.html
EU-PRINCESS-ADO71-SEDAN-HLS-PREFL-01	4481	1744	1409	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/35990/princess_2200_hls.html
EU-MONTEGO-LM11-WAGON-FACELIFT-01	4465	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1701815/rover_montego_2_0_gti_estate.html
EU-ROVER-P6-MARK-II-SEDAN-2200-TC-01	4586	1676	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2996360/rover_2200_tc.html
EU-ROVER-SD1-SERIES-2-HATCHBACK-01	4698	1768	1384	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/2996720/rover_2600_s.html
```

## 下一步优先处理

1. 聚类核对 Austin Metro、1000-Series Mk II 的门数及改款外廓。
2. 处理 Maxi、Allegro、Maestro 和 Montego 第一阶段的年份边界与尺寸差异。
3. 批量闭合 Jaguar XJ-S Coupe、XJ-SC/Convertible 分支，再处理 Rover 800 与 Range Rover I。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2009/1405115/range_rover_sport_5_0_v8_hse.html?utm_source=chatgpt.com "2009 Range Rover Sport 5.0 V8 HSE (aut. 6)"
[2]: https://www.automobile-catalog.com/car/1977/27590/princess_1800_hl.html?utm_source=chatgpt.com "1977 Princess 1800 HL Specs Review (61 kW / 83 PS / 82 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/model/austin/montego.html?utm_source=chatgpt.com "Austin Montego (LM11) data and specifications catalogue"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Metro phase I、phase II 两个尺寸组，新增 Ktype `3103`、`3105` 映射。([汽车目录][1])
* 闭合 Maxi ADO14、Maestro 标准车身及 MG 外部套件尺寸组，新增 Ktype `3115`–`3117`、`3121`、`3123`、`3125`–`3127` 映射。([汽车目录][2])
* 闭合 Montego phase I 标准轿车、MG Turbo 轿车及旅行版尺寸组，新增 Ktype `3130`–`3135` 映射。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：24 行，覆盖 23 个输入 Ktype
* PENDING 输入 Ktype：77
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3103	3103	Hatchback	Metro phase I		3	EU-AUSTIN-METRO-PHASE-I-HATCHBACK-01	HIGH		READY
3105	3105	Hatchback	Metro phase II		3	EU-AUSTIN-METRO-PHASE-II-HATCHBACK-01	HIGH		READY
3115	3115	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3116	3116	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3117	3117	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3121	3121	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	HIGH		READY
3123	3123	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	HIGH		READY
3125	3125	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	HIGH	MG 1600外部套件边界。	READY
3126	3126	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	HIGH	MG 1600外部套件边界。	READY
3127	3127	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-20-EFI-01	HIGH	MG 2.0 EFi外部套件边界。	READY
3130	3130	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3131	3131	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3132	3132	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3133	3133	Sedan	MG Montego phase I	LM11	4	EU-MG-MONTEGO-LM11-TURBO-SEDAN-PHASE-I-01	HIGH	MG Turbo外部套件及车高边界。	READY
3134	3134	Wagon	Montego phase I	LM11	5	EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	HIGH		READY
3135	3135	Wagon	Montego phase I	LM11	5	EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-METRO-PHASE-I-HATCHBACK-01	3405	1549	1369	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256970/austin_metro_1_3_hls.html
EU-AUSTIN-METRO-PHASE-II-HATCHBACK-01	3406	1546	1369	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1751960/austin_metro_1_3_l.html
EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	4022	1629	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1970/75200/austin_maxi_1500.html
EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	4049	1687	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/257525/austin_maestro_1_3_l.html
EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/28370/austin_maestro_1_6_l.html
EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/1699580/mg_maestro_1600.html
EU-MG-MAESTRO-LC10-HATCHBACK-20-EFI-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1699685/mg_maestro_2_0_efi.html
EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	4468	1710	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/258125/austin_montego_2_0_hls.html
EU-MG-MONTEGO-LM11-TURBO-SEDAN-PHASE-I-01	4468	1710	1418	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1700015/mg_montego_turbo.html
EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	4468	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/258485/austin_montego_estate_2_0i_vanden_plas.html
```

## 下一步优先处理

1. 闭合 Austin Metro 跨 phase Ktype、ADO16 门数与 Mk II/Mk III 边界。
2. 处理 Allegro、Maestro 跨后期改款 Ktype。
3. 批量闭合 Jaguar XJ-S Coupe、XJ-SC 和 full Convertible 外廓分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/256970/austin_metro_1_3_hls.html?utm_source=chatgpt.com "1980 Austin Metro 1.3 HLS Specs Review (46.5 kW / 63 PS ..."
[2]: https://www.automobile-catalog.com/car/1970/75200/austin_maxi_1500.html?utm_source=chatgpt.com "1970 Austin Maxi 1500 Specs Review (50 kW / 68 PS ..."
[3]: https://www.automobile-catalog.com/car/1985/258125/austin_montego_2_0_hls.html?utm_source=chatgpt.com "1985 Austin Montego 2.0 HLS (man. 5) (model up to mid-year ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Jaguar XJ-S/XJS 双门 Coupe 的改款前、改款后两个物理尺寸组。1991 年 5 月改款带来前后外观与保险杠变化，跨越该时间边界的 Ktype 已拆分为 `prefl`、`facelift` 派生行。([维基百科][1])
* 本轮完成 Ktype `3137`–`3148` 的 Coupe 映射；发动机与功率差异未额外创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：40 行，覆盖 35 个输入 Ktype
* PENDING 输入 Ktype：65
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3137_prefl	3137	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3137_facelift	3137	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH	1991年5月起改款外廓。	READY
3138	3138	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3139	3139	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3140	3140	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3141_prefl	3141	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3141_facelift	3141	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH	1991年5月起改款外廓。	READY
3142	3142	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3143	3143	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3144_prefl	3144	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3144_facelift	3144	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	MEDIUM	1991年5月至1992年5月改款外廓。	READY
3145	3145	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
3146_prefl	3146	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3146_facelift	3146	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	MEDIUM	生产末段覆盖1991年5月改款外廓。	READY
3147	3147	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
3148	3148	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1281830/jaguar_xj-s_3_6.html
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254	Auto-Data.net	https://www.auto-data.net/en/jaguar-xjs-coupe-6.0-302hp-232
```

## 下一步优先处理

1. 闭合 Jaguar XJ-SC 固定轮廓敞篷、XJ-S 全敞篷及 1991 年后 XJS Convertible 三个车身分支。
2. 批量映射 Ktype `3149`–`3159`，拆分跨 1988 年车顶结构和跨 1991 年改款边界的记录。
3. 随后处理 Jaguar XJ Sedan 与 Rover 800 轿车、掀背及 Coupe 车身簇。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Jaguar_XJS?utm_source=chatgpt.com "Jaguar XJS"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Jaguar XJ-S 敞篷车身簇的三个物理外廓：固定轮廓 XJ-SC、1988–1991 年改款前全敞篷、1991 年后 XJS 改款全敞篷。Jaguar Heritage 的变更节点与欧洲规格页支持这些车身边界及不含后视镜三维。
* 完成 Ktype `3149`–`3159` 映射；跨越固定轮廓、全敞篷及 1991 年改款边界的 V12 Ktype 已拆分，发动机功率差异未重复创建尺寸组。

## 当前批次进度

* READY 映射：59 行，覆盖 46 个输入 Ktype
* PENDING 输入 Ktype：54
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3149	3149	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	3.6版本对应固定轮廓XJ-SC车身。	READY
3150	3150	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	3.6版本对应固定轮廓XJ-SC车身。	READY
3151	3151	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	3.6版本对应固定轮廓XJ-SC车身。	READY
3152_targa	3152	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3152_fullconv_prefl	3152	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3152_fullconv_facelift	3152	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3153_targa	3153	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3153_fullconv_prefl	3153	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、改款前外廓。	READY
3154_targa	3154	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3154_fullconv_prefl	3154	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3155_targa	3155	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	生产初段固定轮廓XJ-SC分支。	READY
3155_fullconv_prefl	3155	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3155_fullconv_facelift	3155	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3156	3156	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
3157_targa	3157	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	生产初段固定轮廓XJ-SC分支。	READY
3157_fullconv_prefl	3157	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3157_fullconv_facelift	3157	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3158	3158	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
3159	3159	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1987/1282220/jaguar_xj-sc_3_6_cabriolet_automatic.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1989/1282460/jaguar_xj-s_v12_convertible.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1993/1284755/jaguar_xjs_4_0_convertible_automatic_cat.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
```

## 下一步优先处理

1. 按 XJ Series 2/3 与 XJ40 聚类处理 Ktype `3160`–`3169`。
2. 批量闭合 Rover P6、SD1、Mini 与 Rover 200 映射。
3. 随后集中处理 Rover 800 轿车、掀背和 Coupe 三个车身簇。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Jaguar XJ40、XJ Series II 长轴距及 XJ Series III 三个尺寸组，完成 Ktype `3160`–`3169` 映射；跨 Series II/III 的 Ktype 已拆分。([汽车目录][1])
* 闭合 Rover P6 3500 外廓，完成 Ktype `3176`、`3177` 映射。([汽车目录][2])
* Ktype `3179` 按 SD1 Series 1/Series 2 拆分；Series 2 直接复用既有尺寸组，仅新增 Series 1 尺寸组。([汽车目录][3])

## 当前批次进度

* READY 映射：75 行，覆盖 59 个输入 Ktype
* PENDING 输入 Ktype：41
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3160	3160	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3161	3161	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3162	3162	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3163_series2	3163	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	Series II长轴距外廓。	READY
3163_series3	3163	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	MEDIUM	1979年起Series III外廓。	READY
3164_series2	3164	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	Series II长轴距外廓。	READY
3164_series3	3164	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	MEDIUM	1979年生产末段Series III外廓。	READY
3165	3165	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3166	3166	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3167	3167	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	V12长轴距Series II外廓。	READY
3168	3168	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3169	3169	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3176	3176	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-3500-01	HIGH		READY
3177	3177	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-3500-01	HIGH		READY
3179_series1	3179	Hatchback	Rover SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-2600-01	MEDIUM	1982年3月改款前外廓。	READY
3179_series2	3179	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	MEDIUM	1982年3月起Series 2外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1282970/jaguar_xj6_2_9_automatic.html
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/1279445/jaguar_xj_3_4.html
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1372	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1280195/jaguar_xj6_3_4.html
EU-ROVER-P6-MARK-II-SEDAN-3500-01	4571	1676	1416	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2996375/rover_3500.html
EU-ROVER-SD1-SERIES-1-HATCHBACK-2600-01	4698	1768	1382	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/37475/rover_2600.html
```

## 下一步优先处理

1. 闭合 Rover Mini 与 Rover 200 SD3 改款前后外廓。
2. 集中处理 Rover 800 第一阶段、R17 改款、Fastback、Sedan 与 Coupe 尺寸组。
3. 最后处理 Range Rover I 三门/五门边界，以及剩余 Austin Metro、ADO16、Allegro、Maestro Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/1282970/jaguar_xj6_2_9_automatic.html?utm_source=chatgpt.com "1986 Jaguar XJ6 2.9 automatic (aut. 4) (model since mid-year ..."
[2]: https://www.automobile-catalog.com/car/1977/2996375/rover_3500.html?utm_source=chatgpt.com "1977 Rover 3500 Specs Review (106.6 kW / 145 PS ..."
[3]: https://www.automobile-catalog.com/car/1978/37475/rover_2600.html?utm_source=chatgpt.com "Detailed specs review of 1978 Rover 2600 model for Europe"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
ChatGPT 说：本轮集中闭合 Rover Mini、Rover 200 SD3 与 Rover 800 的轿车／掀背／Coupe 车身簇；Range Rover I 和剩余 Austin 车型留作下一轮收尾。消息流中的错误


--- 发送 / 推进信号纠偏 / Round 7 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Rover Mini Mk VI–VII 标准双门外廓，以及 Rover 200 SD3 改款前、改款后两个尺寸组。跨越 1987 年外观调整的 Ktype `3172`–`3174` 已按物理外廓拆分。([汽车目录][1])
* 闭合 Rover 800 Series 1 的 Sedan、Fastback，以及 Series 2 R17 的 Sedan、Fastback、Coupe 五个尺寸组；跨越 1991 年 11 月 R17 换代的 Ktype `3188`、`3192`、`3197` 已拆分。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：104 行，覆盖 82 个输入 Ktype
* PENDING 输入 Ktype：18
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3171	3171	Hatchback	Classic Mini Mk VI–VII		2	EU-ROVER-MINI-MK-VI-VII-HATCHBACK-2D-01	MEDIUM	Mk VI至Mk VII标准双门外廓共用尺寸组。	READY
3172_prefl	3172	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3172_facelift	3172	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3173_prefl	3173	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3173_facelift	3173	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3174_prefl	3174	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3174_facelift	3174	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3181	3181	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3182	3182	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3183	3183	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3184	3184	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3185	3185	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3186	3186	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3187	3187	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3188_prefl	3188	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3188_facelift	3188	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3189	3189	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3190	3190	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3191	3191	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	HIGH		READY
3192_prefl	3192	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3192_facelift	3192	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3193	3193	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	HIGH		READY
3194	3194	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3195	3195	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3196	3196	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3197_prefl	3197	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3197_facelift	3197	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3198	3198	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3199	3199	Coupe	Rover 800 Series 2	R17	2	EU-ROVER-800-R17-COUPE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ROVER-MINI-MK-VI-VII-HATCHBACK-2D-01	3054	1440	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1706615/mini_cooper_1_3i.html
EU-ROVER-200-SD3-SEDAN-PREFL-01	4156	1623	1378	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/3009440/rover_213_s.html
EU-ROVER-200-SD3-SEDAN-FACELIFT-01	4160	1635	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/3009590/rover_213_s_automatik.html
EU-ROVER-800-XX-SEDAN-PREFL-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2997065/rover_820_si.html
EU-ROVER-800-XX-HATCHBACK-PREFL-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2997575/rover_820_se_fastback.html
EU-ROVER-800-R17-SEDAN-FACELIFT-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2998475/rover_820_si_saloon.html
EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2998880/rover_825_sd_turbo_fastback.html
EU-ROVER-800-R17-COUPE-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2999660/rover_800_coupe.html
```

## 下一步优先处理

1. 闭合剩余 Austin Metro 跨 phase Ktype `3098`–`3102`、`3104`。
2. 处理 Austin 1000-Series Mk II、Allegro 与 Maestro 剩余 Ktype。
3. 闭合 Rover SD1 `3180` 和 Range Rover I 三门／五门分支 `3208`–`3210`，随后进入完整表机械收尾。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/1706615/mini_cooper_1_3i.html?utm_source=chatgpt.com "1997 Mini Cooper 1.3i Specs Review (46.2 kW / 63 PS ..."
[2]: https://www.automobile-catalog.com/car/1987/2997065/rover_820_si.html?utm_source=chatgpt.com "1987 Rover 820 Si Specs Review (103 kW / 140 PS / 138 ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Austin ADO16 Mk II、Mk III 的普通 2 门／4 门车身，以及 1300 GT 的 Mk II／Mk III 四门车身。两个阶段的长度和高度不同，因此分别建组。([汽车目录][1])
* 闭合 Austin Allegro ADO67 Series 1、Series 2、Series 3 的 2 门／4 门车身。Series 1、2、3 分别存在外廓尺寸变化，不能合并。([汽车目录][2])
* Ktype `3122`、`3124` 直接复用既有 Maestro 尺寸组；Ktype `3180` 按 SD1 Series 1 与 Series 2 拆分，其中 Series 2 复用既有组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：136 行，覆盖 91 个输入 Ktype
* PENDING 输入 Ktype：9
* 已确认尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3106_2dr_mk2	3106	Sedan	Austin 1100 ADO16 Mk II	ADO16	2	EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	MEDIUM	Mk II两门外廓。	READY
3106_4dr_mk2	3106	Sedan	Austin 1100 ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	MEDIUM	Mk II四门外廓。	READY
3106_2dr_mk3	3106	Sedan	Austin 1100 ADO16 Mk III	ADO16	2	EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	MEDIUM	Mk III两门外廓。	READY
3106_4dr_mk3	3106	Sedan	Austin 1100 ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	MEDIUM	Mk III四门外廓。	READY
3107_2dr_mk2	3107	Sedan	Austin 1300 ADO16 Mk II	ADO16	2	EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	MEDIUM	Mk II两门外廓。	READY
3107_4dr_mk2	3107	Sedan	Austin 1300 ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	MEDIUM	Mk II四门外廓。	READY
3107_2dr_mk3	3107	Sedan	Austin 1300 ADO16 Mk III	ADO16	2	EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	MEDIUM	Mk III两门外廓。	READY
3107_4dr_mk3	3107	Sedan	Austin 1300 ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	MEDIUM	Mk III四门外廓。	READY
3108_mk2	3108	Sedan	Austin 1300 GT ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-GT-SEDAN-4D-01	HIGH	Mk II GT四门外廓。	READY
3108_mk3	3108	Sedan	Austin 1300 GT ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-GT-SEDAN-4D-01	HIGH	Mk III GT四门外廓。	READY
3118_2dr_s1	3118	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3118_4dr_s1	3118	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3118_2dr_s2	3118	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3118_4dr_s2	3118	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3118_2dr_s3	3118	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3118_4dr_s3	3118	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3119_2dr_s1	3119	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3119_4dr_s1	3119	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3119_2dr_s2	3119	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3119_4dr_s2	3119	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3119_2dr_s3	3119	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3119_4dr_s3	3119	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3120_2dr_s1	3120	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3120_4dr_s1	3120	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3120_2dr_s2	3120	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3120_4dr_s2	3120	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3120_2dr_s3	3120	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3120_4dr_s3	3120	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3122	3122	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	HIGH		READY
3124	3124	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	HIGH		READY
3180_prefl	3180	Hatchback	Rover SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-3500-01	HIGH	Series 1 V8外廓。	READY
3180_facelift	3180	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	HIGH	Series 2外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	3727	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/74945/austin_1100.html
EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	3727	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/74945/austin_1100.html
EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256220/austin_1100.html
EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256220/austin_1100.html
EU-AUSTIN-ADO16-MK-II-GT-SEDAN-4D-01	3685	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/75005/austin_1300_gt.html
EU-AUSTIN-ADO16-MK-III-GT-SEDAN-4D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256340/austin_1300_gt_automatic.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	3853	1613	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/167900/austin_allegro_1100_deluxe.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	3853	1613	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/167900/austin_allegro_1100_deluxe.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	3853	1613	1388	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/168095/austin_allegro_1300_super.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	3853	1613	1388	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/168095/austin_allegro_1300_super.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	3908	1613	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256565/austin_allegro_1_1.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	3908	1613	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256565/austin_allegro_1_1.html
EU-ROVER-SD1-SERIES-1-HATCHBACK-3500-01	4698	1768	1354	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/26180/rover_3500.html
```

## 下一步优先处理

1. 闭合 Metro Ktype `3098`–`3102`、`3104` 的 phase I、phase II 与 Turbo 宽体分支。
2. 修正或补充 Metro phase II 三门／五门边界，避免把普通 Metro 与 MG Turbo 外廓混组。
3. 最后闭合 Range Rover I Ktype `3208`–`3210` 的 1985 年中期和 1986 年中期外廓变化，随后立即进入最终机械收尾。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1969/74990/austin_1300_automatic.html?utm_source=chatgpt.com "1969 Austin 1300 Mk II automatic (aut. 4)"
[2]: https://www.automobile-catalog.com/car/1974/167900/austin_allegro_1100_deluxe.html?utm_source=chatgpt.com "1974 Austin Allegro 1100 Deluxe Specs Review (35 kW / 48 PS / 47 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1977/26180/rover_3500.html?utm_source=chatgpt.com "1977 Rover 3500 Specs Review (115.6 kW / 157 PS / 155 hp) (for Europe )"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3001-3100_ktype_dimension_mapping_final.tsv
- all_3001-3100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 Austin Metro Phase I、Phase II、MG Metro Turbo 改款前后，以及三门／五门物理分支。([汽车目录][1])
* 已闭合 Range Rover I 早期三门、五门、1984–1985 Vogue、1985–1986 Vogue EFi，以及 1986、1988 两次外廓变化分支。([汽车目录][2])
* 已完成机械收尾：固定表头、唯一主键、全部外键引用闭合、尺寸和来源非空、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：166 行，覆盖全部 100 个输入 Ktype
* PENDING：0
* DIMENSION_GROUP：58 个
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 长宽高及来源完整：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3098_prefl	3098	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-1L-3D-01	MEDIUM	Phase I三门外廓。	READY
3098_3dr_facelift	3098	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门外廓。	READY
3098_5dr_facelift	3098	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门外廓。	READY
3099_prefl	3099	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-1L-3D-01	MEDIUM	Phase I三门外廓。	READY
3099_3dr_facelift	3099	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门外廓。	READY
3099_5dr_facelift	3099	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门外廓。	READY
3100_prefl	3100	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-1L-3D-01	MEDIUM	Phase I三门Surf外廓。	READY
3100_3dr_facelift	3100	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门Surf外廓。	READY
3100_5dr_facelift	3100	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门Surf外廓。	READY
3101_prefl	3101	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-13-3D-01	MEDIUM	Phase I三门外廓。	READY
3101_3dr_facelift	3101	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门外廓。	READY
3101_5dr_facelift	3101	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门外廓。	READY
3102_prefl	3102	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-13-3D-01	MEDIUM	Phase I三门外廓。	READY
3102_3dr_facelift	3102	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门外廓。	READY
3102_5dr_facelift	3102	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门外廓。	READY
3103_prefl	3103	Hatchback	Metro phase I	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-13-3D-01	MEDIUM	Phase I三门外廓。	READY
3103_3dr_facelift	3103	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门外廓。	READY
3103_5dr_facelift	3103	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门外廓。	READY
3104_prefl	3104	Hatchback	MG Metro Turbo phase I	LC8	3	EU-MG-METRO-LC8-TURBO-PHASE-I-HATCHBACK-3D-01	HIGH	改款前Turbo宽体外廓。	READY
3104_facelift	3104	Hatchback	MG Metro Turbo phase II	LC8	3	EU-MG-METRO-LC8-TURBO-PHASE-II-HATCHBACK-3D-01	HIGH	改款后Turbo宽体外廓。	READY
3105_3dr	3105	Hatchback	Metro phase II	LC8	3	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	MEDIUM	Phase II三门Surf外廓。	READY
3105_5dr	3105	Hatchback	Metro phase II	LC8	5	EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II五门Surf外廓。	READY
3106_2dr_mk2	3106	Sedan	Austin 1100 ADO16 Mk II	ADO16	2	EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	MEDIUM	Mk II两门外廓。	READY
3106_4dr_mk2	3106	Sedan	Austin 1100 ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	MEDIUM	Mk II四门外廓。	READY
3106_2dr_mk3	3106	Sedan	Austin 1100 ADO16 Mk III	ADO16	2	EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	MEDIUM	Mk III两门外廓。	READY
3106_4dr_mk3	3106	Sedan	Austin 1100 ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	MEDIUM	Mk III四门外廓。	READY
3107_2dr_mk2	3107	Sedan	Austin 1300 ADO16 Mk II	ADO16	2	EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	MEDIUM	Mk II两门外廓。	READY
3107_4dr_mk2	3107	Sedan	Austin 1300 ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	MEDIUM	Mk II四门外廓。	READY
3107_2dr_mk3	3107	Sedan	Austin 1300 ADO16 Mk III	ADO16	2	EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	MEDIUM	Mk III两门外廓。	READY
3107_4dr_mk3	3107	Sedan	Austin 1300 ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	MEDIUM	Mk III四门外廓。	READY
3108_mk2	3108	Sedan	Austin 1300 GT ADO16 Mk II	ADO16	4	EU-AUSTIN-ADO16-MK-II-GT-SEDAN-4D-01	HIGH	Mk II GT四门外廓。	READY
3108_mk3	3108	Sedan	Austin 1300 GT ADO16 Mk III	ADO16	4	EU-AUSTIN-ADO16-MK-III-GT-SEDAN-4D-01	HIGH	Mk III GT四门外廓。	READY
3113	3113	SUV	Range Rover Sport I (facelift 2009)	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-01	HIGH		READY
3114	3114	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-01	HIGH		READY
3115	3115	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3116	3116	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3117	3117	Hatchback	Maxi I	ADO14	5	EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	HIGH		READY
3118_2dr_s1	3118	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3118_4dr_s1	3118	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3118_2dr_s2	3118	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3118_4dr_s2	3118	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3118_2dr_s3	3118	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3118_4dr_s3	3118	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3119_2dr_s1	3119	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3119_4dr_s1	3119	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3119_2dr_s2	3119	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3119_4dr_s2	3119	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3119_2dr_s3	3119	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3119_4dr_s3	3119	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3120_2dr_s1	3120	Sedan	Allegro Series 1	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	MEDIUM	Series 1两门外廓。	READY
3120_4dr_s1	3120	Sedan	Allegro Series 1	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	MEDIUM	Series 1四门外廓。	READY
3120_2dr_s2	3120	Sedan	Allegro Series 2	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	MEDIUM	Series 2两门外廓。	READY
3120_4dr_s2	3120	Sedan	Allegro Series 2	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	MEDIUM	Series 2四门外廓。	READY
3120_2dr_s3	3120	Sedan	Allegro Series 3	ADO67	2	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	MEDIUM	Series 3两门外廓。	READY
3120_4dr_s3	3120	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	MEDIUM	Series 3四门外廓。	READY
3121	3121	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	HIGH		READY
3122	3122	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	HIGH		READY
3123	3123	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	HIGH		READY
3124	3124	Hatchback	Maestro	LC10	5	EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	HIGH		READY
3125	3125	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	HIGH	MG 1600外部套件边界。	READY
3126	3126	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	HIGH	MG 1600外部套件边界。	READY
3127	3127	Hatchback	MG Maestro	LC10	5	EU-MG-MAESTRO-LC10-HATCHBACK-20-EFI-01	HIGH	MG 2.0 EFi外部套件边界。	READY
3128	3128	Sedan	Princess 18-22 Series 1	ADO71	4	EU-PRINCESS-ADO71-SEDAN-01	HIGH		READY
3129_prefl	3129	Sedan	Princess 18-22 Series 1	ADO71	4	EU-PRINCESS-ADO71-SEDAN-HLS-PREFL-01	HIGH	HLS改款前外廓。	READY
3129_facelift	3129	Sedan	Princess 18-22 Series 2	ADO71	4	EU-PRINCESS-ADO71-SEDAN-01	HIGH	1978年7月起Princess 2外廓。	READY
3130	3130	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3131	3131	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3132	3132	Sedan	Montego phase I	LM11	4	EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	HIGH		READY
3133	3133	Sedan	MG Montego phase I	LM11	4	EU-MG-MONTEGO-LM11-TURBO-SEDAN-PHASE-I-01	HIGH	MG Turbo外部套件及车高边界。	READY
3134	3134	Wagon	Montego phase I	LM11	5	EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	HIGH		READY
3135	3135	Wagon	Montego phase I	LM11	5	EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	HIGH		READY
3136	3136	Wagon	Montego phase II	LM11	5	EU-MONTEGO-LM11-WAGON-FACELIFT-01	HIGH		READY
3137_prefl	3137	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3137_facelift	3137	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH	1991年5月起改款外廓。	READY
3138	3138	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3139	3139	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3140	3140	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3141_prefl	3141	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3141_facelift	3141	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH	1991年5月起改款外廓。	READY
3142	3142	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3143	3143	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH		READY
3144_prefl	3144	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3144_facelift	3144	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	MEDIUM	1991年5月至1992年5月改款外廓。	READY
3145	3145	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
3146_prefl	3146	Coupe	XJ-S Series 1 Coupe	XJ27	2	EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	HIGH	1991年5月改款前外廓。	READY
3146_facelift	3146	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	MEDIUM	生产末段覆盖1991年5月改款外廓。	READY
3147	3147	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
3148	3148	Coupe	XJS Series 2 Coupe	XJ27	2	EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	HIGH		READY
3149	3149	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC车身。	READY
3150	3150	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC车身。	READY
3151	3151	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC车身。	READY
3152_targa	3152	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3152_fullconv_prefl	3152	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3152_fullconv_facelift	3152	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3153_targa	3153	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3153_fullconv_prefl	3153	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、改款前外廓。	READY
3154_targa	3154	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	固定轮廓XJ-SC分支。	READY
3154_fullconv_prefl	3154	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3155_targa	3155	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	生产初段固定轮廓XJ-SC分支。	READY
3155_fullconv_prefl	3155	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3155_fullconv_facelift	3155	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3156	3156	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
3157_targa	3157	Convertible	XJ-SC Cabriolet	XJ27	2	EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	MEDIUM	生产初段固定轮廓XJ-SC分支。	READY
3157_fullconv_prefl	3157	Convertible	XJ-S Series 1 Convertible	XJ27	2	EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	MEDIUM	1988年全敞篷、1991年改款前外廓。	READY
3157_fullconv_facelift	3157	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	MEDIUM	1991年改款后全敞篷外廓。	READY
3158	3158	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
3159	3159	Convertible	XJS Series 2 Convertible	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
3160	3160	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3161	3161	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3162	3162	Sedan	XJ40	XJ40	4	EU-JAGUAR-XJ40-SEDAN-01	HIGH		READY
3163_series2	3163	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	Series II长轴距外廓。	READY
3163_series3	3163	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	MEDIUM	1979年起Series III外廓。	READY
3164_series2	3164	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	Series II长轴距外廓。	READY
3164_series3	3164	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	MEDIUM	1979年生产末段Series III外廓。	READY
3165	3165	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3166	3166	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3167	3167	Sedan	XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	MEDIUM	V12长轴距Series II外廓。	READY
3168	3168	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3169	3169	Sedan	XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3171	3171	Hatchback	Classic Mini Mk VI–VII		2	EU-ROVER-MINI-MK-VI-VII-HATCHBACK-2D-01	MEDIUM	Mk VI至Mk VII标准双门外廓共用尺寸组。	READY
3172_prefl	3172	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3172_facelift	3172	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3173_prefl	3173	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3173_facelift	3173	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3174_prefl	3174	Sedan	Rover 200 SD3 pre-facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-PREFL-01	MEDIUM	1987年外观调整前分支。	READY
3174_facelift	3174	Sedan	Rover 200 SD3 facelift	SD3	4	EU-ROVER-200-SD3-SEDAN-FACELIFT-01	MEDIUM	1987年外观调整后分支。	READY
3175	3175	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-2200-TC-01	HIGH	83kW版本对应2200 TC外廓。	READY
3176	3176	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-3500-01	HIGH		READY
3177	3177	Sedan	Rover P6 Mark II	P6	4	EU-ROVER-P6-MARK-II-SEDAN-3500-01	HIGH		READY
3178	3178	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	HIGH		READY
3179_series1	3179	Hatchback	Rover SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-2600-01	MEDIUM	1982年3月改款前外廓。	READY
3179_series2	3179	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	MEDIUM	1982年3月起Series 2外廓。	READY
3180_prefl	3180	Hatchback	Rover SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-3500-01	HIGH	Series 1 V8外廓。	READY
3180_facelift	3180	Hatchback	Rover SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	HIGH	Series 2外廓。	READY
3181	3181	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3182	3182	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3183	3183	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3184	3184	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3185	3185	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3186	3186	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3187	3187	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3188_prefl	3188	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3188_facelift	3188	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3189	3189	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3190	3190	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3191	3191	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	HIGH		READY
3192_prefl	3192	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3192_facelift	3192	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3193	3193	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	HIGH		READY
3194	3194	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3195	3195	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	HIGH		READY
3196	3196	Hatchback	Rover 800 Series 1	XX	5	EU-ROVER-800-XX-HATCHBACK-PREFL-01	HIGH		READY
3197_prefl	3197	Sedan	Rover 800 Series 1	XX	4	EU-ROVER-800-XX-SEDAN-PREFL-01	MEDIUM	1991年11月R17换代前分支。	READY
3197_facelift	3197	Sedan	Rover 800 Series 2	R17	4	EU-ROVER-800-R17-SEDAN-FACELIFT-01	MEDIUM	1991年11月R17换代后分支。	READY
3198	3198	Hatchback	Rover 800 Series 2	R17	5	EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	HIGH		READY
3199	3199	Coupe	Rover 800 Series 2	R17	2	EU-ROVER-800-R17-COUPE-01	HIGH		READY
3208_3dr_prefl	3208	SUV	Range Rover I pre-facelift		3	EU-LAND-ROVER-RANGE-ROVER-I-3D-PREFL-01	MEDIUM	早期三门Vogue外廓。	READY
3208_5dr_prefl	3208	SUV	Range Rover I pre-facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-PREFL-01	MEDIUM	1981年起五门外廓。	READY
3208_5dr_1984	3208	SUV	Range Rover I Vogue 1984–1985		5	EU-LAND-ROVER-RANGE-ROVER-I-VOGUE-5D-1984-85-01	MEDIUM	1984至1985年中期Vogue外廓。	READY
3208_5dr_facelift_pre88	3208	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1986-88-01	MEDIUM	1986年改款至1988年中期外廓。	READY
3208_5dr_facelift_post88	3208	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1988-90-01	MEDIUM	1988年中期后外廓。	READY
3209_pre88	3209	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1986-88-01	HIGH	催化版改款五门外廓。	READY
3209_post88	3209	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1988-90-01	HIGH	1988年中期后五门外廓。	READY
3210_pre86	3210	SUV	Range Rover I Vogue EFi pre-facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-VOGUE-EFI-5D-1985-86-01	HIGH	1985年中期EFi外廓。	READY
3210_facelift_pre88	3210	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1986-88-01	HIGH	1986年改款至1988年中期外廓。	READY
3210_facelift_post88	3210	SUV	Range Rover I facelift		5	EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1988-90-01	HIGH	1988年中期后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3001-3100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-1L-3D-01	3405	1549	1361	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/26495/austin_metro_1_0_l.html
EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-3D-01	3406	1546	1369	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/257195/austin_metro_1_0_l.html
EU-AUSTIN-METRO-LC8-PHASE-II-HATCHBACK-5D-01	3406	1546	1369	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/257195/austin_metro_1_0_l.html
EU-AUSTIN-METRO-LC8-PHASE-I-HATCHBACK-13-3D-01	3405	1549	1369	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256970/austin_metro_1_3_hls.html
EU-MG-METRO-LC8-TURBO-PHASE-I-HATCHBACK-3D-01	3405	1563	1359	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/1699145/mg_metro_turbo.html
EU-MG-METRO-LC8-TURBO-PHASE-II-HATCHBACK-3D-01	3403	1563	1378	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1699235/mg_metro_turbo.html
EU-AUSTIN-ADO16-MK-II-SEDAN-2D-01	3727	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/74945/austin_1100.html
EU-AUSTIN-ADO16-MK-II-SEDAN-4D-01	3727	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1969/74945/austin_1100.html
EU-AUSTIN-ADO16-MK-III-SEDAN-2D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256220/austin_1100.html
EU-AUSTIN-ADO16-MK-III-SEDAN-4D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256220/austin_1100.html
EU-AUSTIN-ADO16-MK-II-GT-SEDAN-4D-01	3685	1534	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/75005/austin_1300_gt.html
EU-AUSTIN-ADO16-MK-III-GT-SEDAN-4D-01	3704	1534	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/256340/austin_1300_gt_automatic.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1405115/range_rover_sport_5_0_v8_hse.html
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1456715/fiat_bravo_1_6_multijet_16v_90_dynamic_dpf.html
EU-AUSTIN-MAXI-I-ADO14-HATCHBACK-01	4022	1629	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1970/75200/austin_maxi_1500.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-2D-01	3853	1613	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/167900/austin_allegro_1100_deluxe.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-1-SEDAN-4D-01	3853	1613	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/167900/austin_allegro_1100_deluxe.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-2D-01	3853	1613	1388	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/168095/austin_allegro_1300_super.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-2-SEDAN-4D-01	3853	1613	1388	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/168095/austin_allegro_1300_super.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-2D-01	3908	1613	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256565/austin_allegro_1_1.html
EU-AUSTIN-ALLEGRO-ADO67-SERIES-3-SEDAN-4D-01	3908	1613	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/256565/austin_allegro_1_1.html
EU-AUSTIN-MAESTRO-LC10-HATCHBACK-13-01	4049	1687	1422	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/257525/austin_maestro_1_3_l.html
EU-AUSTIN-MAESTRO-LC10-HATCHBACK-16-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1984/28370/austin_maestro_1_6_l.html
EU-MG-MAESTRO-LC10-HATCHBACK-1600-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/1699580/mg_maestro_1600.html
EU-MG-MAESTRO-LC10-HATCHBACK-20-EFI-01	4049	1687	1429	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1699685/mg_maestro_2_0_efi.html
EU-PRINCESS-ADO71-SEDAN-01	4455	1730	1409	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/27590/princess_1800_hl.html
EU-PRINCESS-ADO71-SEDAN-HLS-PREFL-01	4481	1744	1409	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/35990/princess_2200_hls.html
EU-AUSTIN-MONTEGO-LM11-SEDAN-PHASE-I-01	4468	1710	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/258125/austin_montego_2_0_hls.html
EU-MG-MONTEGO-LM11-TURBO-SEDAN-PHASE-I-01	4468	1710	1418	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1700015/mg_montego_turbo.html
EU-AUSTIN-MONTEGO-LM11-WAGON-PHASE-I-01	4468	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/258485/austin_montego_estate_2_0i_vanden_plas.html
EU-MONTEGO-LM11-WAGON-FACELIFT-01	4465	1710	1447	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/1701815/rover_montego_2_0_gti_estate.html
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1281830/jaguar_xj-s_3_6.html
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254	Auto-Data.net	https://www.auto-data.net/en/jaguar-xjs-coupe-6.0-302hp-232
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1987/1282220/jaguar_xj-sc_3_6_cabriolet_automatic.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1989/1282460/jaguar_xj-s_v12_convertible.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276	Automobile-Catalog; Jaguar Daimler Heritage Trust	https://www.automobile-catalog.com/car/1993/1284755/jaguar_xjs_4_0_convertible_automatic_cat.html; https://www.jaguarheritage.com/uploads/RG001N-Jaguar-XJS-v.3-31-03-2020.pdf
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/1282970/jaguar_xj6_2_9_automatic.html
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375	Automobile-Catalog	https://www.automobile-catalog.com/car/1975/1279445/jaguar_xj_3_4.html
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1372	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1280195/jaguar_xj6_3_4.html
EU-ROVER-MINI-MK-VI-VII-HATCHBACK-2D-01	3054	1440	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1706615/mini_cooper_1_3i.html
EU-ROVER-200-SD3-SEDAN-PREFL-01	4156	1623	1378	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/3009440/rover_213_s.html
EU-ROVER-200-SD3-SEDAN-FACELIFT-01	4160	1635	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/3009590/rover_213_s_automatik.html
EU-ROVER-P6-MARK-II-SEDAN-2200-TC-01	4586	1676	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/2996360/rover_2200_tc.html
EU-ROVER-P6-MARK-II-SEDAN-3500-01	4571	1676	1416	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/2996375/rover_3500.html
EU-ROVER-SD1-SERIES-2-HATCHBACK-01	4698	1768	1384	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/2996720/rover_2600_s.html
EU-ROVER-SD1-SERIES-1-HATCHBACK-2600-01	4698	1768	1382	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/37475/rover_2600.html
EU-ROVER-SD1-SERIES-1-HATCHBACK-3500-01	4698	1768	1354	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/26180/rover_3500.html
EU-ROVER-800-XX-HATCHBACK-PREFL-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/2997575/rover_820_se_fastback.html
EU-ROVER-800-XX-SEDAN-PREFL-01	4693	1730	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/2997065/rover_820_si.html
EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2998880/rover_825_sd_turbo_fastback.html
EU-ROVER-800-R17-SEDAN-FACELIFT-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2998475/rover_820_si_saloon.html
EU-ROVER-800-R17-COUPE-01	4882	1730	1393	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/2999660/rover_800_coupe.html
EU-LAND-ROVER-RANGE-ROVER-I-3D-PREFL-01	4470	1778	1778	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/1397420/range_rover_2-door.html
EU-LAND-ROVER-RANGE-ROVER-I-5D-PREFL-01	4470	1778	1778	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/1397435/range_rover_4-door.html
EU-LAND-ROVER-RANGE-ROVER-I-VOGUE-5D-1984-85-01	4475	1800	1785	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1397510/range_rover_vouge.html
EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1986-88-01	4450	1818	1800	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1397660/range_rover_vouge_efi_automatic.html
EU-LAND-ROVER-RANGE-ROVER-I-5D-FACELIFT-1988-90-01	4450	1818	1790	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/1397825/range_rover_vouge_efi_automatic.html
EU-LAND-ROVER-RANGE-ROVER-I-VOGUE-EFI-5D-1985-86-01	4460	1800	1785	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/1397585/range_rover_vouge_efi.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3001-3100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1980/26495/austin_metro_1_0_l.html?utm_source=chatgpt.com "1980 Austin Metro 1.0 L Specs Review (32.2 kW / 44 PS ..."
[2]: https://www.automobile-catalog.com/car/1981/1397435/range_rover_4-door.html "https://www.automobile-catalog.com/car/1981/1397435/range_rover_4-door.html"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-JAGUAR-XJ-SERIES-III-SEDAN-01 的 HeightMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3001-3100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3001-3100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4574 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1324 行）

- 尺寸冲突协调：
  - EU-JAGUAR-XJ-SERIES-III-SEDAN-01 -> EU-JAGUAR-XJ-SERIES-III-SEDAN-02：4959x1770x1377 与 4959x1770x1372，创建新尺寸组
