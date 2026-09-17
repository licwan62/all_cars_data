# 任务：all 第 1601-1700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0017__d1b4d234


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1601-1700 行

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
all 第 1601-1700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Porsche	911	3.6 Turbo	Cabriolet	Allrad	Benzin	353	480	Sep 2007	Dec 2009	2024-03-01	23174
Fiat	500	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Jul 2007	-	2024-03-01	23175
Fiat	500	1.4	Schrägheck	Frontantrieb	Benzin	74	100	Oct 2007	-	2024-03-01	23176
Fiat	500	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2007	-	2024-03-01	23177
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	103	140	Sep 2007	Jul 2018	2024-03-01	23178
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	125	170	Sep 2007	Jul 2018	2024-03-01	23179
VW	Tiguan	2.0 Tfsi 4motion	SUV	Allrad	Benzin	147	200	Sep 2007	Jul 2018	2024-03-01	23180
VW	Tiguan	2.0 Tfsi 4motion	SUV	Allrad	Benzin	125	170	Sep 2007	Jul 2018	2024-03-01	23181
VW	Tiguan	1.4 TSI 4motion	SUV	Allrad	Benzin	110	150	Sep 2007	Jul 2018	2024-03-01	23182
Citroën	C3 i	1.4 I	Schrägheck	Frontantrieb	Benzin	54	73	Feb 2002	Nov 2010	2024-03-01	23183
Porsche	911	3.6 GT 2	Coupe	Heckantrieb	Benzin	390	530	Sep 2007	Dec 2012	2024-03-01	23184
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	80	109	Jan 2002	Apr 2006	2024-03-01	23185
Nissan	Primera	1.6	Schrägheck	Frontantrieb	Benzin	80	109	Jul 2002	Apr 2006	2024-03-01	23186
Audi	A6 c6	2.8 FSI Quattro	Stufenheck	Allrad	Benzin	154	210	Jun 2007	Oct 2008	2024-03-01	23187
Audi	A6 c6 avant	2.8 FSI Quattro	Kombi	Allrad	Benzin	154	210	Jun 2007	Oct 2008	2024-03-01	23188
Audi	A8 d3	2.8 FSI	Stufenheck	Frontantrieb	Benzin	154	210	Aug 2007	Jul 2010	2024-03-01	23189
Cadillac	Bls	2.0 T	Stufenheck	Frontantrieb	Benzin	129	175	Apr 2006	Dec 2010	2024-03-01	23190
Cadillac	Bls	2.0 T	Stufenheck	Frontantrieb	Benzin	154	210	Apr 2006	-	2024-03-01	23191
Cadillac	Bls	2.8 T	Stufenheck	Frontantrieb	Benzin	188	255	Apr 2006	-	2024-03-01	23192
Cadillac	Bls	1.9 D	Stufenheck	Frontantrieb	Diesel	110	150	Apr 2006	-	2024-03-01	23193
Fiat	Grande punto	1.4 T-jet	Schrägheck	Frontantrieb	Benzin	88	120	Sep 2007	-	2024-03-01	23194
VW	Golf v variant	1.4 TSI	Kombi	Frontantrieb	Benzin	125	170	Jun 2007	Jul 2009	2024-03-01	23195
Nissan	X-Trail ii	2.0 DCI 4X4	SUV	Allrad	Diesel	127	173	Jun 2007	Nov 2013	2024-03-01	23196
Nissan	X-Trail ii	2.0 4X4	SUV	Allrad	Benzin	104	141	Jun 2007	Nov 2013	2024-03-01	23197
Nissan	X-Trail ii	2.0 DCI 4X4	SUV	Allrad	Diesel	110	150	Jun 2007	Nov 2013	2024-03-01	23198
Nissan	X-Trail ii	2.5 4X4	SUV	Allrad	Benzin	124	169	Jun 2007	Nov 2013	2024-03-01	23199
Nissan	Primera	1.9 DCI	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2002	Oct 2007	2024-03-01	23200
Nissan	Primera	1.9 DCI	Stufenheck	Frontantrieb	Diesel	85	116	Aug 2002	Oct 2007	2024-03-01	23201
Nissan	Primera	1.9 DCI	Kombi	Frontantrieb	Diesel	85	116	Aug 2002	Oct 2007	2024-03-01	23202
VW	Polo	1.2	Schrägheck	Frontantrieb	Benzin	44	60	May 2007	Nov 2009	2024-03-01	23205
VW	Polo	1.2 12V	Schrägheck	Frontantrieb	Benzin	51	69	May 2007	Nov 2009	2024-03-01	23207
Fiat	Bravo ii	1.4 T-jet	Schrägheck	Frontantrieb	Benzin	88	120	Oct 2007	Dec 2014	2024-03-01	23225
Fiat	Bravo ii	1.4 T-jet	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2007	Dec 2014	2024-03-01	23226
Fiat	Linea	1.3 D Multijet	Stufenheck	Frontantrieb	Diesel	66	90	Jun 2007	-	2024-03-01	23227
Fiat	Linea	1.4	Stufenheck	Frontantrieb	Benzin	57	77	Jun 2007	-	2024-03-01	23228
Fiat	Linea	1.4 T-jet	Stufenheck	Frontantrieb	Benzin	88	120	May 2007	-	2024-03-01	23229
Peugeot	1007	1.6 HDI	Schrägheck	Frontantrieb	Diesel	80	109	Jun 2007	-	2024-03-01	23230
Ford	Transit	2.4 Tdci 4X4	Bus	Allrad	Diesel	103	140	Nov 2006	Aug 2014	2024-03-01	23231
Seat	Altea	1.8 Tfsi	Großraumlimousine	Frontantrieb	Benzin	118	160	Jan 2007	Jul 2015	2024-05-01	23232
Seat	Toledo	1.8 Tfsi	Großraumlimousine	Frontantrieb	Benzin	118	160	Jan 2007	May 2009	2024-03-01	23233
Dodge	Avenger	2	Stufenheck	Frontantrieb	Benzin	115	156	Jun 2007	Dec 2011	2024-03-01	23234
Dodge	Avenger	2.0 CRD	Stufenheck	Frontantrieb	Diesel	103	140	Jun 2007	Dec 2011	2024-03-01	23235
Skoda	Roomster	1.2	Kasten/Kombi	Frontantrieb	Benzin	51	70	Mar 2007	May 2015	2024-03-01	23240
Skoda	Roomster	1.4	Kasten/Kombi	Frontantrieb	Benzin	63	86	Mar 2007	May 2015	2024-03-01	23243
Skoda	Roomster	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	59	80	Mar 2007	Mar 2010	2024-03-01	23245
Skoda	Roomster	1.4 TDI	Kasten/Kombi	Frontantrieb	Diesel	51	70	Mar 2007	Mar 2010	2024-03-01	23247
VW	Golf v variant	1.4	Kombi	Frontantrieb	Benzin	59	80	Jun 2007	Jul 2009	2024-03-01	23263
Mazda	3	2.3 MPS Turbo	Schrägheck	Frontantrieb	Benzin	191	260	Dec 2006	Jun 2009	2024-03-01	23264
Opel	Movano a	2.5 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	73	99	Oct 2003	-	2024-03-01	23265
Opel	Movano a	3.0 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	100	136	Oct 2003	-	2024-03-01	23266
VW	Transporter t5	1.9 TDI	Kasten	Frontantrieb	Diesel	62	84	Jan 2006	Nov 2009	2024-03-01	23267
Skoda	Octavia	1.9 TDI	Kombi	Frontantrieb	Diesel	74	100	Aug 2000	Dec 2010	2024-03-01	23268
Opel	Vectra c caravan	2.8 V6 Turbo	Kombi	Frontantrieb	Benzin	206	280	Jul 2006	Aug 2008	2024-03-01	23276
Suzuki	Samurai	1.3 Allrad	Geländewagen geschlossen	Allrad	Benzin	59	80	Jan 2000	Dec 2004	2024-03-01	23277
Mercedes-benz	G-Klasse	G 320 CDI	Geländewagen offen	Allrad	Diesel	165	224	Sep 2006	Dec 2012	2024-03-01	23278
Smart	Roadster	0.7	Coupe	Heckantrieb	Benzin	45	61	Jun 2003	Nov 2005	2024-03-01	23279
BMW	X5	3.0 SI	SUV	Allrad	Benzin	200	272	Oct 2006	Sep 2008	2024-03-01	23280
BMW	X5	4.8 I Xdrive	SUV	Allrad	Benzin	261	355	Oct 2006	Sep 2008	2024-03-01	23281
BMW	X5	3.0 D	SUV	Allrad	Diesel	173	235	Dec 2006	Sep 2008	2024-03-01	23282
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	100	136	Mar 2002	Dec 2008	2024-03-01	23283
Mercedes-benz	E-Klasse	E 220 CDI	Kombi	Heckantrieb	Diesel	100	136	Mar 2003	Jul 2009	2024-03-01	23284
VW	Transporter t5	1.9 TDI	Bus	Frontantrieb	Diesel	62	84	Jan 2006	Nov 2009	2024-03-01	23285
VW	Transporter t5	1.9 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	62	84	Jan 2006	Nov 2009	2024-03-01	23286
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	412	560	Jun 2006	Apr 2011	2024-03-01	23287
KIA	Cee'd	2.0 Crdi 140	Kombi	Frontantrieb	Diesel	103	140	Jul 2007	Dec 2012	2024-03-01	23288
KIA	Cee'd	2.0 Crdi 140	Schrägheck	Frontantrieb	Diesel	103	140	Sep 2007	Dec 2012	2024-03-01	23289
Skoda	Octavia	1.4	Kombi	Frontantrieb	Benzin	59	80	May 2006	Jun 2013	2024-03-01	23290
Skoda	Octavia	1.9 TDI	Schrägheck	Frontantrieb	Diesel	74	100	Oct 2005	Dec 2010	2024-03-01	23291
Skoda	Roomster	1.2	Großraumlimousine	Frontantrieb	Benzin	51	70	Jan 2007	May 2015	2024-03-01	23292
Skoda	Superb i	1.9 TDI	Stufenheck	Frontantrieb	Diesel	85	115	Jan 2007	Mar 2008	2024-03-01	23293
Skoda	Superb i	1.9 TDI	Stufenheck	Frontantrieb	Diesel	77	105	Oct 2005	May 2007	2024-03-01	23294
VW	Jetta iii	1.4 TSI	Stufenheck	Frontantrieb	Benzin	90	122	May 2007	Oct 2010	2024-03-01	23295
KIA	Cerato i	1.6 Crdi	Stufenheck	Frontantrieb	Diesel	85	115	Jun 2005	Dec 2009	2024-03-01	23296
KIA	Cerato i	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	85	115	Jun 2005	Jun 2008	2024-03-01	23297
VW	Touareg	4.2 V8 FSI	SUV	Allrad	Benzin	257	350	Jun 2006	May 2010	2024-03-01	23298
Audi	A4 b8	1.8 Tfsi	Stufenheck	Frontantrieb	Benzin	118	160	Nov 2007	Mar 2012	2024-03-01	23299
Audi	A4 b8	3.2 FSI Quattro	Stufenheck	Allrad	Benzin	195	265	Nov 2007	Mar 2012	2024-03-01	23300
Audi	A4 b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	105	143	Nov 2007	Dec 2015	2024-03-01	23301
Audi	A4 b8	2.7 TDI	Stufenheck	Frontantrieb	Diesel	140	190	Nov 2007	Mar 2012	2024-03-01	23302
Audi	A4 b8	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	176	240	Nov 2007	Mar 2012	2024-03-01	23303
Bentley	Continental	6.0 GT Speed	Coupe	Allrad	Benzin	449	610	Sep 2007	Dec 2011	2024-03-01	23304
Renault	Clio i	1.2	Schrägheck	Frontantrieb	Benzin	44	60	May 1990	Mar 1996	2026-05-01	23305
Hyundai	Grandeur	2.2 Crdi	Stufenheck	Frontantrieb	Diesel	110	150	Jun 2006	Dec 2011	2024-03-01	23306
Hyundai	Grandeur	2.2 Crdi	Stufenheck	Frontantrieb	Diesel	114	155	Jun 2006	Oct 2010	2024-03-01	23307
Hyundai	Tucson	2.0 Crdi	SUV	Frontantrieb	Diesel	100	136	Jan 2006	Mar 2010	2024-03-01	23308
Hyundai	Tucson	2.0 Crdi Allrad	SUV	Allrad	Diesel	100	136	Jan 2006	Mar 2010	2024-03-01	23309
Hyundai	H-1 / starex	2.5 TD 4WD	Bus	Allrad	Diesel	73	99	Mar 2001	Apr 2004	2024-03-01	23310
Hyundai	H-1 / starex	2.5 TD 4WD	Bus	Allrad	Diesel	74	101	Nov 2001	Apr 2004	2024-03-01	23311
Hyundai	H-1 / starex	2.5 Crdi	Bus	Heckantrieb	Diesel	81	110	Jun 2006	Dec 2007	2024-03-01	23312
Hyundai	Sonata v	2.0 Crdi	Stufenheck	Frontantrieb	Diesel	100	136	Feb 2006	Dec 2010	2024-03-01	23314
Hyundai	H-1	2.5 Crdi	Kasten	Heckantrieb	Diesel	81	110	Jul 2001	Apr 2004	2024-03-01	23317
LTI	Tx	2.4 TDI	Schrägheck	Heckantrieb	Diesel	66	90	Oct 2002	-	2024-03-01	23318
LTI	Tx	2.5 TD	Schrägheck	Heckantrieb	Diesel	75	102	Jan 2006	-	2024-03-01	23319
Mitsubishi	Eclipse i	1.8	Coupe	Frontantrieb	Benzin	68	92	Dec 1989	Mar 1994	2024-03-01	23338
Fiat	Ulysse	2.0 D Multijet	Großraumlimousine	Frontantrieb	Diesel	88	120	May 2006	Jun 2011	2024-03-01	23353
Fiat	Ulysse	2.0 D Multijet	Großraumlimousine	Frontantrieb	Diesel	100	136	May 2006	Jun 2011	2024-03-01	23354
Alfa Romeo	159	1.8 MPI	Kombi	Frontantrieb	Benzin	103	140	Jun 2005	Nov 2011	2024-03-01	23355
Alfa Romeo	159	1.8 MPI	Stufenheck	Frontantrieb	Benzin	103	140	Jun 2005	Nov 2011	2024-03-01	23356
Lancia	Musa	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	66	90	Sep 2006	Sep 2012	2024-03-01	23357
Lancia	Phedra	2.0 D Multijet	Großraumlimousine	Frontantrieb	Diesel	100	136	Jul 2006	Nov 2010	2024-03-01	23358


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 **58 条 READY 映射**，首次闭合 **30 个 DIMENSION_GROUP**，覆盖 **45 个已完成 Ktype**。
* 已按外廓变化拆分 Tiguan 5N、X-Trail T31 的改款前后尺寸，以及 Citroën C3 I Phase I / Phase II；这些分支的车长或车高存在实质差异，不能合并。([汽车数据][1])
* Grande Punto 与 Polo 9N3 已按三门、五门拆分物理车身；即使三维相同，也不混用车身边界。
* Transit、Roomster Kasten/Kombi、Movano A 底盘和 Transporter T5 Kasten 暂不猜测轴距、车顶或驾驶室分支，保留 PENDING。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：53
* READY Ktype：45
* READY 映射：58
* PENDING Ktype／映射：8
* 已确认尺寸组：30
* 尚未开始处理：47 个 Ktype
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23174	23174	Convertible	911 (997)	997	2	EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	HIGH	997 Turbo Cabriolet外廓。	READY
23175	23175	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23176	23176	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23177	23177	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23178_prefl	23178	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23178_facelift	23178	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23179_prefl	23179	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23179_facelift	23179	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23180_prefl	23180	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23180_facelift	23180	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23181_prefl	23181	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23181_facelift	23181	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23182_prefl	23182	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23182_facelift	23182	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23183_phase1	23183	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-PHASE-I-01	MEDIUM	1.4i覆盖Phase I外廓。	READY
23183_phase2	23183	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-PHASE-II-01	MEDIUM	1.4i覆盖Phase II外廓。	READY
23184	23184	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-GT2-COUPE-01	HIGH	997 GT2双门外廓。	READY
23185	23185	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-01	HIGH	P12四门轿车外廓。	READY
23186	23186	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-01	HIGH	P12五门掀背外廓。	READY
23187	23187	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	HIGH	4F2改款前轿车外廓。	READY
23188	23188	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	HIGH	4F5改款前Avant外廓。	READY
23189	23189	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	4E短轴改款后轿车外廓。	READY
23190	23190	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23191	23191	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23192	23192	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23193	23193	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23194_3dr	23194	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	来源覆盖三门分支。	READY
23194_5dr	23194	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	来源覆盖五门分支。	READY
23195	23195	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-1K5-WAGON-01	HIGH	1K5旅行车外廓。	READY
23196_prefl	23196	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23196_facelift	23196	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23197_prefl	23197	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23197_facelift	23197	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23198_prefl	23198	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23198_facelift	23198	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23199_prefl	23199	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23199_facelift	23199	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23200	23200	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-01	HIGH	P12五门掀背外廓。	READY
23201	23201	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-01	HIGH	P12四门轿车外廓。	READY
23202	23202	Wagon	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-WAGON-01	HIGH	P12旅行车外廓。	READY
23205_3dr	23205	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-9N3-HATCHBACK-3D-01	MEDIUM	9N3三门分支。	READY
23205_5dr	23205	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-9N3-HATCHBACK-5D-01	MEDIUM	9N3五门分支。	READY
23207_3dr	23207	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-9N3-HATCHBACK-3D-01	MEDIUM	9N3三门分支。	READY
23207_5dr	23207	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-9N3-HATCHBACK-5D-01	MEDIUM	9N3五门分支。	READY
23225	23225	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背外廓。	READY
23226	23226	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背外廓。	READY
23227	23227	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23228	23228	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23229	23229	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23230	23230	MPV	1007		3	EU-PEUGEOT-1007-MPV-3D-01	HIGH	双侧滑门三门MPV外廓。	READY
23231	23231	MPV	Transit Mk7				LOW	候选含多轴距及多车顶4x4 Bus。	PENDING: 轴距和车顶分支未闭合
23232	23232	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门MPV外廓。	READY
23233	23233	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH	5P五门高顶车身外廓。	READY
23234	23234	Sedan	Avenger	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	HIGH	JS四门轿车外廓。	READY
23235	23235	Sedan	Avenger	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	HIGH	JS四门轿车外廓。	READY
23240	23240	Van	Roomster	5J			LOW	候选为Roomster或Praktik车身。	PENDING: Kasten/Kombi物理车身未区分
23243	23243	Van	Roomster	5J			LOW	候选为Roomster或Praktik车身。	PENDING: Kasten/Kombi物理车身未区分
23245	23245	Van	Roomster	5J			LOW	候选为Roomster或Praktik车身。	PENDING: Kasten/Kombi物理车身未区分
23247	23247	Van	Roomster	5J			LOW	候选为Roomster或Praktik车身。	PENDING: Kasten/Kombi物理车身未区分
23263	23263	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-1K5-WAGON-01	HIGH	1K5旅行车外廓。	READY
23264	23264	Hatchback	Mazda 3 I facelift	BK	5	EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	HIGH	BK MPS宽体五门外廓。	READY
23265	23265	Pickup	Movano A	X70			LOW	候选含多轴距及单/双排底盘。	PENDING: 驾驶室和轴距分支未闭合
23266	23266	Pickup	Movano A	X70			LOW	候选含多轴距及单/双排底盘。	PENDING: 驾驶室和轴距分支未闭合
23267	23267	Van	Transporter T5	7H			LOW	候选含短长轴及多车顶Kasten。	PENDING: 轴距和车顶分支未闭合
23268	23268	Wagon	Octavia I facelift	1U5	5	EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	HIGH	1U5前驱旅行车外廓。	READY
23276	23276	Wagon	Vectra C facelift	Z02	5	EU-OPEL-VECTRA-C-Z02-WAGON-FACELIFT-01	HIGH	Z02改款后Caravan外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2868170/porsche_911_turbo_cabriolet_tiptronic_s.html
EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-1.2-8v-69hp-16748
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tdi-140hp-4motion-44135
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-2.0-tdi-140hp-4motion-18455
EU-CITROEN-C3-I-HATCHBACK-PHASE-I-01	3850	1667	1529	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-i-2002-1.4i-73hp-15088
EU-CITROEN-C3-I-HATCHBACK-PHASE-II-01	3860	1667	1510	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.4i-73hp-6056
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-gt2-3.6-530hp-6584
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-p12-1.6-i-16v-109hp-592
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-hatch-p12-1.6-i-16v-109hp-599
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-wagon-p12-1.9-dci-120hp-608
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4f-c6-2.8-fsi-v6-210hp-4650
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463	Auto-Data.net	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.8-fsi-v6-210hp-quattro-tiptronic-26731
EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	5062	1894	1444	Auto-Data.net	https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2007-2.8-fsi-e-v6-210hp-multitronic-4810
EU-CADILLAC-BLS-SEDAN-01	4680	1752	1471	Auto-Data.net	https://www.auto-data.net/en/cadillac-bls-2.0-t-175hp-11689
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-t-jet-120hp-35742
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-t-jet-120hp-35742
EU-VW-GOLF-V-1K5-WAGON-01	4556	1781	1504	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.4-tsi-170hp-dsg-8642
EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	4630	1785	1685	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-ii-t31-2.0-dci-150hp-4x4-906
EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	4635	1790	1700	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-ii-t31-facelift-2010-2.0-dci-173hp-4x4-29962
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.2-70hp-3-d-8410
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.2-70hp-5-d-8411
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-ii-198-1.4-t-jet-120hp-dualogic-54964
EU-FIAT-LINEA-323-SEDAN-01	4560	1730	1494	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/729170/fiat_linea_1_4_t-jet_16v_emotion.html
EU-PEUGEOT-1007-MPV-3D-01	3731	1686	1620	Auto-Data.net	https://www.auto-data.net/en/peugeot-1007-model-566
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Auto-Data.net	https://www.auto-data.net/en/seat-altea-5p-1.8-tsi-160hp-dsg-16901
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data.net	https://www.auto-data.net/en/seat-toledo-iii-5p-1.8-tsi-160hp-13532
EU-DODGE-AVENGER-JS-SEDAN-01	4850	1843	1497	Auto-Data.net	https://www.auto-data.net/en/dodge-avenger-sedan-2.0-crd-140hp-dct-51161
EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	4435	1765	1465	Auto-Data.net	https://www.auto-data.net/en/mazda-3-i-hatchback-bk-facelift-2006-mps-2.3i-260hp-11481
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-facelift-2000-1.9-tdi-100hp-14266
EU-OPEL-VECTRA-C-Z02-WAGON-FACELIFT-01	4839	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-1.9-cdti-120hp-26130
```

## 下一步优先处理

1. 优先消除 8 个 PENDING：Transit 4×4 Bus、Roomster／Praktik、Movano A 底盘、Transporter T5 Kasten。
2. 随后从 Ktype `23277` 开始处理剩余 47 个 Ktype，优先按 Samurai、G-Klasse、Smart Roadster、BMW X5、Mercedes E-Klasse 等共用车身聚类。
3. 对重复出现的 X5、E-Klasse、Continental、Cee'd、Octavia、H-1／Starex 等，仅关联已闭合尺寸组，不重复抓取。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tdi-140hp-4motion-44135?utm_source=chatgpt.com "Volkswagen Tiguan I 2.0 TDI (140 Hp) 4MOTION /SUV 2009"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已将 4 个 Roomster `Kasten/Kombi` 阻塞 Ktype 闭合为 **Praktik 5J8 五门厢式车**。其中汽油版跨越 2010 年改款，按前期、改款后拆分；两款 1.4 TDI 在 2010 年改款前结束，仅关联前期组。前期尺寸为 4205 × 1684 × 1607 mm，改款后 Praktik 车长变为 4213 mm。 ([manualzz.com][1])
* 新增并闭合 Mercedes-Benz E-Class W211/S211 前期与改款后四个尺寸组；轿车及旅行车的改款前后车长、车高均发生变化，不能合并。 ([汽车数据][2])
* 新增 Bentley Continental GTC、Škoda Superb I 前期/改款后以及 Volkswagen Jetta V 映射。
* Ford Transit、Opel Movano A 和 Volkswagen Transporter T5 的 4 个既有 PENDING 仍保留：现有资料确认它们包含多轴距、车顶或驾驶室配置，不能压缩成单一尺寸组。 ([Dezo's Garage][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：59
* READY Ktype：55
* READY 映射：73
* PENDING Ktype／映射：4
* 尚未处理 Ktype：41
* 已确认尺寸组：40
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23240_prefl	23240	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	MEDIUM	5J8五门Praktik改款前外廓。	READY
23240_facelift	23240	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	MEDIUM	5J8五门Praktik改款后外廓。	READY
23243_prefl	23243	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	MEDIUM	5J8五门Praktik改款前外廓。	READY
23243_facelift	23243	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	MEDIUM	5J8五门Praktik改款后外廓。	READY
23245	23245	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	HIGH	5J8五门Praktik改款前外廓。	READY
23247	23247	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	HIGH	5J8五门Praktik改款前外廓。	READY
23283_prefl	23283	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFL-01	MEDIUM	W211四门改款前分支。	READY
23283_facelift	23283	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	W211四门改款后分支。	READY
23284_prefl	23284	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFL-01	MEDIUM	S211五门改款前分支。	READY
23284_facelift	23284	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	MEDIUM	S211五门改款后分支。	READY
23287	23287	Convertible	Continental GTC		2	EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	MEDIUM	第一代Continental GTC双门敞篷外廓。	READY
23293	23293	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	HIGH	3U4四门改款后外廓。	READY
23294_prefl	23294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-PREFL-01	MEDIUM	3U4四门改款前分支。	READY
23294_facelift	23294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	MEDIUM	3U4四门改款后分支。	READY
23295	23295	Sedan	Jetta V	1K2	4	EU-VW-JETTA-V-1K2-SEDAN-01	HIGH	1K2四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	4205	1684	1607	Škoda Roomster 2007 Owner's Manual	https://manualzz.com/doc/52177068/skoda-roomster--2007-05--owner-s-manual
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	4213	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3143120/skoda_praktik_1_2_htp_70.html
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFL-01	4818	1822	1452	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-e-220-cdi-150hp-12876
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	4856	1822	1483	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-200-cdi-136hp-12870
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFL-01	4850	1822	1496	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-220-cdi-150hp-12912
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	4888	1822	1506	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-220-cdi-170hp-12913
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398	Auto-Data.net	https://www.auto-data.net/en/bentley-continental-gtc-6.0-i-w12-48v-560hp-6754
EU-SKODA-SUPERB-I-3U4-SEDAN-PREFL-01	4803	1765	1469	Auto-Data.net	https://www.auto-data.net/en/skoda-superb-i-1.9-tdi-131hp-14115
EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	4803	1765	1469	Auto-Data.net	https://www.auto-data.net/en/skoda-superb-i-facelift-2006-1.9-tdi-115hp-44980
EU-VW-JETTA-V-1K2-SEDAN-01	4554	1781	1459	Auto-Data.net	https://www.auto-data.net/en/volkswagen-jetta-v-1.4-tsi-122hp-dsg-9073
```

## 下一步优先处理

1. 优先拆分并闭合剩余 4 个 PENDING：`23231` Transit Bus、`23265`／`23266` Movano A 底盘、`23267` Transporter T5 Kasten。
2. 随后处理 `23277` 起尚未覆盖的车型，优先闭合可批量复用的 X5 E70、Cee'd、Octavia II、Audi A4 B8、Hyundai H-1／Starex 和 Ulysse／Phedra 车身组。
3. BMW X5 E70 暂不落盘：不同动力资料出现 1739 mm 与1766 mm 两种高度，需先确认是否由车顶构件或悬架配置造成，不能仅按发动机拆组。

推进信号：CONTINUE

[1]: https://manualzz.com/doc/52177068/skoda-roomster--2007-05--owner-s-manual "Skoda Roomster (2007/05) Owner's Manual | Manualzz"
[2]: https://www.auto-data.net/en/mercedes-benz-e-class-w211-e-220-cdi-150hp-12876 "Mercedes-Benz E-class (W211) E 220 CDI (150 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf?utm_source=chatgpt.com "Volkswagen Transporter Van"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* `23231` 已闭合为 Transit Mk7 15 座 LWB 中顶四驱 Minibus，车宽采用不含后视镜口径。
* `23267` 已按 T5 Kasten 的 SWB／LWB 和低顶／中顶／高顶拆成 5 个物理分支；原无后缀 PENDING 行取消。
* 新增并闭合 Kia Cee'd I 两个车身组：五门掀背和五门旅行车。([汽车数据][1])
* `23265`、`23266` 已确认涉及普通驾驶室、双排驾驶室及多轴距底盘，但各物理分支的完整三维仍未闭合，继续保留 PENDING。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：61
* READY Ktype：59
* READY 映射：81
* PENDING Ktype／映射：2
* 尚未处理 Ktype：39
* 已确认尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23231	23231	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	HIGH	15座LWB中顶四驱Minibus外廓。	READY
23265	23265	Pickup	Movano A facelift	X70			LOW	已确认含普通驾驶室、双排驾驶室及多轴距平台底盘。	PENDING: 底盘驾驶室与轴距分支尺寸未闭合
23266	23266	Pickup	Movano A facelift	X70			LOW	已确认含普通驾驶室、双排驾驶室及多轴距平台底盘。	PENDING: 底盘驾驶室与轴距分支尺寸未闭合
23267_swb_lowroof	23267	Van	Transporter T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶Kasten外廓。	READY
23267_swb_medroof	23267	Van	Transporter T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	SWB中顶Kasten外廓。	READY
23267_lwb_lowroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶Kasten外廓。	READY
23267_lwb_medroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	LWB中顶Kasten外廓。	READY
23267_lwb_highroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶Kasten外廓。	READY
23288	23288	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-ED-WAGON-01	HIGH	ED五门旅行车外廓。	READY
23289	23289	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-01	HIGH	ED五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	5680	1974	2393	Ford Transit People Movers 2007 brochure;Ford Transit Panel Vans Specifications 2007	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-KIA-CEED-I-ED-WAGON-01	4470	1790	1490	Auto-Data.net	https://www.auto-data.net/en/kia-ceed-sw-i-2.0-crdi-140hp-42444
EU-KIA-CEED-I-ED-HATCHBACK-01	4235	1790	1480	Auto-Data.net	https://www.auto-data.net/en/kia-ceed-i-2.0-crdi-140hp-42284
```

## 下一步优先处理

1. 只继续补齐 `23265`、`23266` 的 Movano A 普通驾驶室／双排驾驶室、轴距及平台底盘尺寸分支。
2. 同步处理尚未覆盖的乘用车聚类，优先闭合 Octavia II、Audi A4 B8、Hyundai H-1／Starex、Ulysse／Phedra。
3. Movano 两个 PENDING 清零后，立即进入剩余映射补齐，不重新核对本轮已创建的尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-ceed-i-2.0-crdi-140hp-42284 "Kia Cee'd I 2.0 CRDi (140 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Movano A 的车身边界已收紧为 UD0 单排底盘、HD0 双排底盘、ED0 低地板驾驶室和 UD4 前围底盘。官方资料已闭合部分 MWB/LWB 单排及双排尺寸，但 ED0、UD4 与全部轴距组合仍未完整闭合，因此 `23265`、`23266` 不强行拆成猜测性 READY 行。
* 完成 `23291` Octavia I Tour 五门掀背，以及 `23292` Roomster MPV 改款前后尺寸组。([汽车数据][1])
* 完成 `23296`、`23297` Kia Cerato I 轿车和掀背车的改款前后物理分支。2007 年改款后轿车和掀背车车长分别增加至 4500 mm 与 4350 mm。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：65
* READY Ktype：63
* READY 映射：88
* PENDING Ktype／映射：2
* 尚未处理 Ktype：35
* 已确认尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23265	23265	Pickup	Movano A facelift	X70			LOW	UD0单排底盘、HD0双排、ED0低地板和UD4前围分支已确认。	PENDING: ED0/UD4外廓及全部轴距分支尺寸未闭合
23266	23266	Pickup	Movano A facelift	X70			LOW	UD0单排底盘、HD0双排、ED0低地板和UD4前围分支已确认。	PENDING: ED0/UD4外廓及全部轴距分支尺寸未闭合
23291	23291	Hatchback	Octavia I facelift	1U2	5	EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	HIGH	1U2五门Tour掀背外廓。	READY
23292_prefl	23292	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-PREFL-01	MEDIUM	5J五门MPV改款前外廓。	READY
23292_facelift	23292	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	MEDIUM	5J五门MPV改款后外廓。	READY
23296_prefl	23296	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	MEDIUM	LD四门改款前外廓。	READY
23296_facelift	23296	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	MEDIUM	LD四门改款后外廓。	READY
23297_prefl	23297	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-PREFL-01	MEDIUM	LD五门改款前外廓。	READY
23297_facelift	23297	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-FACELIFT-01	MEDIUM	LD五门改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-i-tour-facelift-2000-1.9-tdi-100hp-55861
EU-SKODA-ROOMSTER-5J-MPV-PREFL-01	4205	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-1.2-12v-64hp-14270
EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	4214	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-facelift-2010-1.2-htp-70hp-19231
EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	4480	1735	1470	Auto-Data.net	https://www.auto-data.net/en/kia-cerato-i-sedan-1.6-105hp-32542
EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	4500	1735	1470	Kia Cerato 2007 Owner's Manual	https://www.carmanualsonline.info/kia-cerato-2007-owners-manual/?srch=dimensions
EU-KIA-CERATO-I-LD-HATCHBACK-PREFL-01	4340	1735	1470	Auto-Data.net	https://www.auto-data.net/en/kia-cerato-i-hatchback-1.6-105hp-32535
EU-KIA-CERATO-I-LD-HATCHBACK-FACELIFT-01	4350	1735	1470	Kia Cerato 2007 Owner's Manual	https://www.carmanualsonline.info/kia-cerato-2007-owners-manual/?srch=dimensions
```

## 下一步优先处理

1. 继续补齐 Movano A 的 ED0、UD4 外廓以及 MWB/LWB 单排、双排分支；未闭合的配置不创建临时尺寸组。
2. 批量处理 Audi A4 B8、BMW X5 E70、Hyundai H-1／Starex、Fiat Ulysse／Lancia Phedra。
3. 补齐 `23290` Octavia II Combi 改款前尺寸，再关联已闭合的改款后尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/skoda-octavia-i-tour-facelift-2000-1.9-tdi-100hp-55861 "Skoda Octavia I Tour (facelift 2000) 1.9 TDI (100 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/kia-cerato-i-sedan-1.6-105hp-32542 "Kia Cerato I Sedan 1.6 (105 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Movano A 官方规格已闭合 **MWB 单排底盘、LWB 单排底盘和 LWB 双排底盘**三类外廓，宽度均明确为不含后视镜；但输入 Ktype 中 `ED / HD / UD0 / UD4` 与这三类外廓的逐项对应关系仍未闭合，因此 `23265`、`23266` 暂不猜测拆行。([Vauxhall][1])
* 完成 BMW X5 E70 的 3.0si、4.8i 和 3.0d 共用尺寸组，官方资料一致为 `4854 × 1933 × 1766 mm`。([宝马集团新闻][2])
* 完成 Volkswagen Touareg I 4.2 V8 FSI 映射；Volkswagen 官方档案确认车身代码 `7L` 及三维。([Volkswagen Newsroom][3])
* 完成 Audi A4 B8 四个改款前 Ktype，并将跨越改款周期的 `23301` 拆为改款前、改款后两个物理分支。Audi 官方资料确认改款前后车长及车高发生变化。([Audi 新闻中心][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：74
* READY Ktype：72
* READY 映射：98
* PENDING Ktype／映射：2
* 尚未处理 Ktype：26
* 已确认尺寸组：59
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23265	23265	Pickup	Movano A facelift	X70			LOW	官方已闭合MWB/LWB单排及LWB双排外廓；车型代码与分支对应关系未闭合。	PENDING: ED/HD/UD0/UD4与驾驶室及轴距分支对应关系未闭合
23266	23266	Pickup	Movano A facelift	X70			LOW	官方已闭合MWB/LWB单排及LWB双排外廓；车型代码与分支对应关系未闭合。	PENDING: ED/HD/UD0/UD4与驾驶室及轴距分支对应关系未闭合
23280	23280	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23281	23281	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23282	23282	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23298	23298	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	7L改款后五门SUV外廓。	READY
23299	23299	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23300	23300	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23301_prefl	23301	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23301_facelift	23301	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	该Ktype覆盖改款后外廓。	READY
23302	23302	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23303	23303	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X5-E70-SUV-01	4854	1933	1766	BMW Group PressClub X5 gasoline technical data;BMW Group PressClub X5 3.0d technical data	https://www.press.bmwgroup.com/korea/article/detail/T0046106KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-x5-%EA%B0%80%EC%86%94%EB%A6%B0-%EB%AA%A8%EB%8D%B8-%EC%B6%9C%EC%8B%9C?language=ko;https://www.press.bmwgroup.com/korea/article/detail/T0046065KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EC%8A%A4%ED%8F%AC%EC%B8%A0-%EB%9F%AD%EC%85%94%EB%A6%AC-%EC%82%AC%EB%A5%9C%EA%B5%AC%EB%8F%99-%EB%89%B4-x5-%EC%B6%9C%EC%8B%9C?language=ko
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726	Volkswagen Newsroom Touareg I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-touareg-1-profile-19718
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Audi UK The New A4 Saloon press information	https://press.audi.co.uk/assets/documents/original/13844-AudiUK00000262ThenewAudiA4Saloon2008.pdf
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Audi UK A4 3.0 TDI quattro technical data	https://press.audi.co.uk/assets/documents/original/13834-AudiUK00000070A430TDIquattroStronic.pdf
```

## 下一步优先处理

1. 继续确认 Movano A 的 `ED / HD / UD0 / UD4` 与 MWB 单排、LWB 单排及 LWB 双排的对应关系；仅在对应闭合后创建三个已核实尺寸组。
2. 批量处理 Volkswagen Transporter T5 Bus／底盘、Škoda Octavia II Combi 和 Hyundai H-1／Starex 商用车分支。
3. 随后闭合 Bentley Continental GT Speed、Hyundai Grandeur／Tucson／Sonata、Fiat Ulysse／Lancia Phedra及 Alfa Romeo 159 等乘用车组。

推进信号：CONTINUE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf "https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf"
[2]: https://www.press.bmwgroup.com/korea/article/detail/T0046106KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-x5-%EA%B0%80%EC%86%94%EB%A6%B0-%EB%AA%A8%EB%8D%B8-%EC%B6%9C%EC%8B%9C?language=ko "https://www.press.bmwgroup.com/korea/article/detail/T0046106KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-x5-%EA%B0%80%EC%86%94%EB%A6%B0-%EB%AA%A8%EB%8D%B8-%EC%B6%9C%EC%8B%9C?language=ko"
[3]: https://www.volkswagen-newsroom.com/en/vehicle-data-touareg-1-profile-19718 "https://www.volkswagen-newsroom.com/en/vehicle-data-touareg-1-profile-19718"
[4]: https://press.audi.co.uk/assets/documents/original/13844-AudiUK00000262ThenewAudiA4Saloon2008.pdf "https://press.audi.co.uk/assets/documents/original/13844-AudiUK00000262ThenewAudiA4Saloon2008.pdf"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Movano A 官方资料已闭合 UD0 单排底盘和 HD0 双排底盘的部分轴距尺寸，但 `23265`、`23266` 同时覆盖 ED0 低地板驾驶室及 UD4 前围底盘；后两类外廓仍不完整，因此本轮未改写这两条 PENDING，也未建立猜测性尺寸组。([Vauxhall][1])
* 本轮新增完成 Suzuki Samurai SJ413、Mercedes-Benz G-Class W463 Cabriolet、Bentley Continental GT Speed、Hyundai Grandeur TG、Tucson JM、Sonata NF，以及 Mitsubishi Eclipse 1G。([汽车数据][2])
* `23338` Mitsubishi Eclipse I 覆盖 1992 年改款前后两种外廓；车高由 1321 mm 变为 1306 mm，已拆为两个派生映射和两个尺寸组。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：83
* READY Ktype：81
* READY 映射：108
* PENDING Ktype／映射：2
* 尚未处理 Ktype：17
* 已确认尺寸组：67
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23277	23277	SUV	Samurai (SJ)	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	MEDIUM	SJ413三门硬顶外廓；输入功率高于常见欧洲资料，车身边界一致。	READY
23278	23278	Convertible	G-Class Cabriolet W463 facelift 2007	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-2007-01	HIGH	W463短轴双门敞篷越野车外廓。	READY
23304	23304	Coupe	Continental GT I	3W	2	EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	HIGH	第一代GT Speed双门外廓。	READY
23306	23306	Sedan	Grandeur/Azera IV	TG	4	EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	MEDIUM	TG四门轿车外廓；150 hp早期版本沿用同一车身。	READY
23307	23307	Sedan	Grandeur/Azera IV	TG	4	EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	HIGH	TG四门轿车外廓。	READY
23308	23308	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH	JM五门SUV外廓。	READY
23309	23309	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH	JM五门SUV外廓。	READY
23314	23314	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-NF-SEDAN-01	MEDIUM	NF四门轿车外廓；136 hp版本沿用同一车身。	READY
23338_prefl	23338	Coupe	Eclipse I	1G	3	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-PREFL-01	MEDIUM	该Ktype覆盖1G改款前外廓。	READY
23338_facelift	23338	Coupe	Eclipse I facelift	1G	3	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-FACELIFT-01	MEDIUM	该Ktype覆盖1992改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680	Auto-Data.net	https://www.auto-data.net/en/suzuki-samurai-sj-generation-3690
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-2007-01	4257	1760	1941	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w463-facelift-2007-g-320-cdi-v6-224hp-4matic-7g-tronic-17398
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380	Auto-Data.net	https://www.auto-data.net/en/bentley-continental-gt-speed-6.0i-w12-48v-twin-turbo-610hp-6753
EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	4895	1865	1490	Auto-Data.net	https://www.auto-data.net/en/hyundai-grandeur-azera-iv-tg-2.2-crdi-155hp-automatic-13800
EU-HYUNDAI-TUCSON-JM-SUV-01	4325	1830	1730	Auto-Data.net	https://www.auto-data.net/en/hyundai-tucson-model-2083
EU-HYUNDAI-SONATA-NF-SEDAN-01	4800	1832	1475	Auto-Data.net	https://www.auto-data.net/en/hyundai-sonata-v-nf-2.0-crdi-16v-140hp-13816
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-PREFL-01	4390	1695	1321	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-generation-3435
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-FACELIFT-01	4390	1695	1306	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-facelift-1992-1.8-92hp-43092
```

## 下一步优先处理

1. 继续补齐 Movano A 的 ED0、UD4 外廓，以及四种车身代码与单排／双排、轴距分支的完整对应关系。
2. 处理 Transporter T5 Bus／底盘和 Hyundai H-1／Starex 的多轴距、多车身分支。
3. 批量闭合其余乘用车：Smart Roadster、Octavia II Combi、Clio I、LTI TX、Ulysse／Phedra、Alfa Romeo 159和Lancia Musa。

推进信号：CONTINUE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf "untitled"
[2]: https://www.auto-data.net/en/suzuki-samurai-sj-generation-3690 "Suzuki Samurai (SJ) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-generation-3435 "Mitsubishi Eclipse I (1G) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* `23265`、`23266` 已取消无后缀基础 PENDING 行，按已确认的 Movano A 车身代码拆分。`UD0` 单排底盘的 MWB、LWB，以及 `HD0` 双排底盘 LWB 已闭合并转为 READY；`ED0` 低地板驾驶室和 `UD4` 前围底盘缺少固定量产完整外廓，继续保留派生 PENDING 行。官方规格表明确给出了三个可闭合分支的不含后视镜宽度及完整长宽高。
* 新增 Smart Roadster Coupé `452` 尺寸组。
* 新增 Škoda Octavia II Combi `1Z5` 改款前、改款后两个尺寸组；该 Ktype 跨越改款周期，按物理外廓拆分。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：85
* READY Ktype：83
* READY 映射：117
* PENDING Ktype：2
* PENDING 映射：4
* 尚未处理 Ktype：15
* 已确认尺寸组：73
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23265_ud0_mwb	23265	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	UD0单排中轴底盘外廓。	READY
23265_ud0_lwb	23265	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	UD0单排长轴底盘外廓。	READY
23265_hd0_lwb	23265	Pickup	Movano A facelift	HD0	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	HD0双排长轴底盘外廓。	READY
23265_ed0	23265	Pickup	Movano A facelift	ED0			LOW	ED0低地板驾驶室，完整外廓取决于最终车身。	PENDING: ED0量产完整外廓无固定三维
23265_ud4	23265	Pickup	Movano A facelift	UD4			LOW	UD4前围底盘，完整外廓尚未闭合。	PENDING: UD4量产完整外廓无固定三维
23266_ud0_mwb	23266	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	UD0单排中轴底盘外廓。	READY
23266_ud0_lwb	23266	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	UD0单排长轴底盘外廓。	READY
23266_hd0_lwb	23266	Pickup	Movano A facelift	HD0	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	HD0双排长轴底盘外廓。	READY
23266_ed0	23266	Pickup	Movano A facelift	ED0			LOW	ED0低地板驾驶室，完整外廓取决于最终车身。	PENDING: ED0量产完整外廓无固定三维
23266_ud4	23266	Pickup	Movano A facelift	UD4			LOW	UD4前围底盘，完整外廓尚未闭合。	PENDING: UD4量产完整外廓无固定三维
23279	23279	Coupe	Roadster Coupé	452	2	EU-SMART-ROADSTER-452-COUPE-01	MEDIUM	452双门Roadster Coupé外廓。	READY
23290_prefl	23290	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	MEDIUM	该Ktype覆盖改款前1Z5旅行车外廓。	READY
23290_facelift	23290	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	MEDIUM	该Ktype覆盖改款后1Z5旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	5369	1990	2200	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	5869	1990	2195	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	5869	1990	2203	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-SMART-ROADSTER-452-COUPE-01	3427	1615	1207	Auto-Data.net	https://www.auto-data.net/en/smart-roadster-coupe-0.7-i-82hp-14883
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/3137930/skoda_octavia_combi_1_4_16v_80.html
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462	Autodata24	https://autodata24.com/skoda/octavia/octavia-ii-fl-combi-1z5/14-mpi-80-hp/details
```

## 下一步优先处理

1. 仅继续核对 Movano A `ED0`、`UD4` 是否存在可追溯的固定量产外廓；若属于车身制造商后装且无统一三维，则按实际不可闭合原因处理，不再反复检索。
2. 批量处理 Transporter T5 Bus／底盘和 Hyundai H-1／Starex 的轴距、车顶及厢式车分支。
3. 闭合剩余乘用车：Renault Clio I、LTI TX、Fiat Ulysse／Lancia Phedra、Alfa Romeo 159和Lancia Musa。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/smart-roadster-coupe-0.7-i-82hp-14883?utm_source=chatgpt.com "Specs of Smart Roadster coupe 0.7 i (82 Hp) /2002, 2003, ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Movano A 的 `ED0` 低地板驾驶室和 `UD4` 前围底盘属于后续改装基础车，官方资料没有固定的完整量产外廓；本轮不创建临时尺寸组，4 条派生 PENDING 保持不变。([Vauxhall][1])
* 完成 Renault Clio I Phase I／Phase II 的三门、五门分支。Phase II 车宽由 1616 mm 变为 1625 mm，因此不能与 Phase I 合并。([汽车数据][2])
* 完成 Fiat Ulysse II 改款前后、Lancia Musa 改款前后尺寸组；两款车型改款后外廓均发生变化。([汽车数据][3])
* 完成 LTI TXII、LTI TX4 和 Lancia Phedra 映射。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：92
* READY Ktype：90
* READY 映射：130
* PENDING Ktype：2
* PENDING 映射：4
* 尚未处理 Ktype：8
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23305_3dr_phase1	23305	Hatchback	Clio I Phase I		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-I-01	MEDIUM	Phase I三门物理外廓。	READY
23305_5dr_phase1	23305	Hatchback	Clio I Phase I		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	Phase I五门物理外廓。	READY
23305_3dr_phase2	23305	Hatchback	Clio I Phase II		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	MEDIUM	Phase II三门物理外廓。	READY
23305_5dr_phase2	23305	Hatchback	Clio I Phase II		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	Phase II五门物理外廓。	READY
23318	23318	Sedan	TXII		4	EU-LTI-TXII-SEDAN-01	HIGH	TXII四门出租车车身外廓。	READY
23319	23319	Sedan	TX4		4	EU-LTI-TX4-SEDAN-01	HIGH	TX4四门出租车车身外廓。	READY
23353_prefl	23353	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	MEDIUM	179五门改款前外廓。	READY
23353_facelift	23353	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	MEDIUM	179五门改款后外廓。	READY
23354_prefl	23354	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	MEDIUM	179五门改款前外廓。	READY
23354_facelift	23354	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	MEDIUM	179五门改款后外廓。	READY
23357_prefl	23357	MPV	Musa I		5	EU-LANCIA-MUSA-I-MPV-PREFL-01	MEDIUM	五门改款前外廓。	READY
23357_facelift	23357	MPV	Musa I facelift		5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
23358	23358	MPV	Phedra I		5	EU-LANCIA-PHEDRA-I-MPV-01	HIGH	五门MPV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-I-01	3709	1616	1395	Auto-Data.net	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-I-01	3709	1616	1395	Auto-Data.net	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	3709	1625	1395	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Renault/6417/Renault-Clio-1-Phase-2-12.html
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	3709	1625	1395	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Renault/6417/Renault-Clio-1-Phase-2-12.html
EU-LTI-TXII-SEDAN-01	4580	1800	1834	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/338720/lti_tx_ii_automatic.html
EU-LTI-TX4-SEDAN-01	4580	1800	1834	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/338750/lti_tx4.html
EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	4719	1863	1752	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-ii-179-2.0-jtd-multijet-16v-136hp-53052
EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	4719	1863	1759	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-ii-179-facelift-2008-2.0-jtd-multijet-16v-136hp-53053
EU-LANCIA-MUSA-I-MPV-PREFL-01	3985	1698	1688	Auto-Data.net	https://www.auto-data.net/en/lancia-musa-1.3-multijet-90hp-31785
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660	Auto-Data.net	https://www.auto-data.net/en/lancia-musa-facelift-2007-1.3-multijet-90hp-automatic-31788
EU-LANCIA-PHEDRA-I-MPV-01	4750	1863	1759	Auto-Data.net	https://www.auto-data.net/en/lancia-phedra-2.0-multijet-16v-136hp-dpf-45952
```

## 下一步优先处理

1. 对 Movano A 的 `ED0`、`UD4` 做最终映射层处置，避免把无固定完整外廓的改装基础车继续作为尺寸分支。
2. 补齐 `23285` Transporter T5 Bus、`23286` T5 底盘和 `23310`–`23317` Hyundai H-1／Starex 的轴距、车顶及车身分支。
3. 闭合 `23355`、`23356` Alfa Romeo 159 Sportwagon／Sedan 的精确单值高度。

推进信号：CONTINUE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf "untitled"
[2]: https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134 "https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134"
[3]: https://www.auto-data.net/en/fiat-ulysse-ii-179-2.0-jtd-multijet-16v-136hp-53052 "https://www.auto-data.net/en/fiat-ulysse-ii-179-2.0-jtd-multijet-16v-136hp-53052"
[4]: https://www.automobile-catalog.com/car/2004/338720/lti_tx_ii_automatic.html "https://www.automobile-catalog.com/car/2004/338720/lti_tx_ii_automatic.html"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 撤销此前缺乏可靠车型代码对应证据的 `23265_ed0`、`23265_ud4`、`23266_ed0`、`23266_ud4` 四条猜测性派生行。`23265`、`23266` 仅保留已由官方规格闭合的 UD0 单排和 HD0 双排底盘分支，因此 Movano 两个 Ktype 不再存在 PENDING。该处理是对上一轮过度拆分的纠正。
* 完成 Transporter T5 Bus 的 SWB／LWB 低顶分支，直接复用已闭合的 T5 低顶车身尺寸组；T5 底盘则新增 LWB 单排驾驶室和 LWB 双排驾驶室两个尺寸组。([Allegro][1])
* 完成 Hyundai H-1／Starex A1 两个 4WD SWB Ktype；`23312` 客车和 `23317` 厢式车仍无法确认属于 SWB 还是 LWB，因此保留 PENDING，不凭发动机版本猜测。([lakiauto.ee][2])
* 完成 Alfa Romeo 159 Sedan 与 Sportwagon 映射，并按不同物理车身分别建组。标准量产状态采用不含后视镜宽度和不含选装车顶行李架的高度。([汽车数据][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：100
* READY Ktype：98
* PENDING Ktype：2
* READY 映射：138
* PENDING 映射：2
* 已确认尺寸组：89
* 尚未处理 Ktype：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23285_swb	23285	MPV	Transporter T5	7HB		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	7HB短轴低顶Bus外廓。	READY
23285_lwb	23285	MPV	Transporter T5	7HJ		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	7HJ长轴低顶Bus外廓。	READY
23286_singlecab_lwb	23286	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	MEDIUM	LWB单排驾驶室底盘外廓。	READY
23286_doublecab_lwb	23286	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	MEDIUM	LWB双排驾驶室底盘外廓。	READY
23310	23310	MPV	H-1 / Starex I	A1	4	EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	MEDIUM	A1短轴四驱客车外廓。	READY
23311	23311	MPV	H-1 / Starex I	A1	4	EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	HIGH	A1短轴四驱客车外廓。	READY
23312	23312	MPV	H-1 / Starex I	A1			LOW	A1客车候选含SWB和LWB外廓。	PENDING: 110 hp版本轴距分支未闭合
23317	23317	Van	H-1 / Starex I	A1			LOW	A1厢式车候选含不同轴距外廓。	PENDING: 110 hp版本轴距分支未闭合
23355	23355	Wagon	159	939	5	EU-ALFA-ROMEO-159-SPORTWAGON-01	HIGH	939五门Sportwagon外廓。	READY
23356	23356	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1949	Volkswagen Transporter T5 specifications March 2014;Volkswagen Transporter January 2008 price list	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf;https://www.vwpress.co.uk/assets/documents/original/16899-transporter_prices_1.pdf
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963	Volkswagen Transporter T5 specifications March 2014;Volkswagen Transporter January 2008 price list	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf;https://www.vwpress.co.uk/assets/documents/original/16899-transporter_prices_1.pdf
EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	4695	1820	1880	Auto-Data.net	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-4wd-swb-101hp-13858
EU-ALFA-ROMEO-159-SPORTWAGON-01	4660	1828	1417	Alfa Romeo 159 and 159 Sportwagon official specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1417	Alfa Romeo 159 and 159 Sportwagon official specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
```

## 下一步优先处理

1. 仅处理 `23312` 与 `23317`：确认各自对应 SWB、LWB，或是否确实覆盖两个轴距分支。
2. 若两个 Ktype 的轴距边界闭合，立即清零 PENDING，并在下一轮直接执行一次机械收尾、生成两张完整 TSV 和指定下载文件。
3. 不再重新核对本批已闭合的 89 个尺寸组。

推进信号：CONTINUE

[1]: https://allegro.pl/produkt/blokada-ciegna-vw-transporter-t5-7h0711761b-01fccfbc-012b-48e1-9d11-9efe25cf4f64?fromInactiveOffer=archived&utm_source=chatgpt.com "BLOKADA CIĘGNA VW TRANSPORTER T5 7H0711761B • Opinie - Allegro"
[2]: https://www.lakiauto.ee/admin/upload/Dokumendid/pump_compressed.pdf?utm_source=chatgpt.com "TecDoc ktype 3822 | Manufacturer ALFA ROMEO | Mode"
[3]: https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.8-mpi-140hp-1526?utm_source=chatgpt.com "Alfa Romeo 159 Sportwagon 1.8 MPI (140 Hp)"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1601-1700_ktype_dimension_mapping_final.tsv
- all_1601-1700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 最后两个 PENDING 已闭合：`23312` 确认为 A1 改款后标准轴距客车，`23317` 确认为 A1 标准轴距厢式车。对应车身分别采用 `4625 × 1820 × 1880 mm` 和 `4695 × 1820 × 1880 mm`，宽度均为不含后视镜口径。([Autodoc][1])
* 已删除所有过期 PENDING 和猜测性派生行。
* 已完成机械检查：两张表表头正确、`id` 和 `DIMENSION_GROUP_ID` 唯一、所有映射引用闭合、尺寸和来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：140
* PENDING：0
* DIMENSION_GROUP：91
* 孤立尺寸组：0
* 缺失尺寸组引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23174	23174	Convertible	911 (997)	997	2	EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	HIGH	997 Turbo Cabriolet外廓。	READY
23175	23175	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23176	23176	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23177	23177	Hatchback	500 (312)	312	3	EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	HIGH	312三门掀背前期外廓。	READY
23178_prefl	23178	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23178_facelift	23178	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23179_prefl	23179	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23179_facelift	23179	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23180_prefl	23180	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23180_facelift	23180	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23181_prefl	23181	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23181_facelift	23181	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23182_prefl	23182	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23182_facelift	23182	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-5N-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖2011改款后外廓。	READY
23183_phase1	23183	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-PHASE-I-01	MEDIUM	1.4i覆盖Phase I外廓。	READY
23183_phase2	23183	Hatchback	C3 I		5	EU-CITROEN-C3-I-HATCHBACK-PHASE-II-01	MEDIUM	1.4i覆盖Phase II外廓。	READY
23184	23184	Coupe	911 (997)	997	2	EU-PORSCHE-911-997-GT2-COUPE-01	HIGH	997 GT2双门外廓。	READY
23185	23185	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-01	HIGH	P12四门轿车外廓。	READY
23186	23186	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-01	HIGH	P12五门掀背外廓。	READY
23187	23187	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	HIGH	4F2改款前轿车外廓。	READY
23188	23188	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	HIGH	4F5改款前Avant外廓。	READY
23189	23189	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	4E短轴改款后轿车外廓。	READY
23190	23190	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23191	23191	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23192	23192	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23193	23193	Sedan	BLS		4	EU-CADILLAC-BLS-SEDAN-01	HIGH	BLS四门轿车外廓。	READY
23194_3dr	23194	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	来源覆盖三门分支。	READY
23194_5dr	23194	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	来源覆盖五门分支。	READY
23195	23195	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-1K5-WAGON-01	HIGH	1K5旅行车外廓。	READY
23196_prefl	23196	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23196_facelift	23196	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23197_prefl	23197	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23197_facelift	23197	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23198_prefl	23198	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23198_facelift	23198	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23199_prefl	23199	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	MEDIUM	该Ktype覆盖T31改款前外廓。	READY
23199_facelift	23199	SUV	X-Trail II	T31	5	EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	MEDIUM	该Ktype覆盖T31改款后外廓。	READY
23200	23200	Hatchback	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-HATCHBACK-01	HIGH	P12五门掀背外廓。	READY
23201	23201	Sedan	Primera P12	P12	4	EU-NISSAN-PRIMERA-P12-SEDAN-01	HIGH	P12四门轿车外廓。	READY
23202	23202	Wagon	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-WAGON-01	HIGH	P12旅行车外廓。	READY
23205_3dr	23205	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-9N3-HATCHBACK-3D-01	MEDIUM	9N3三门分支。	READY
23205_5dr	23205	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-9N3-HATCHBACK-5D-01	MEDIUM	9N3五门分支。	READY
23207_3dr	23207	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-9N3-HATCHBACK-3D-01	MEDIUM	9N3三门分支。	READY
23207_5dr	23207	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-9N3-HATCHBACK-5D-01	MEDIUM	9N3五门分支。	READY
23225	23225	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背外廓。	READY
23226	23226	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH	198五门掀背外廓。	READY
23227	23227	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23228	23228	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23229	23229	Sedan	Linea	323	4	EU-FIAT-LINEA-323-SEDAN-01	HIGH	323四门轿车外廓。	READY
23230	23230	MPV	1007		3	EU-PEUGEOT-1007-MPV-3D-01	HIGH	双侧滑门三门MPV外廓。	READY
23231	23231	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	HIGH	15座LWB中顶四驱Minibus外廓。	READY
23232	23232	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门MPV外廓。	READY
23233	23233	MPV	Toledo III	5P	5	EU-SEAT-TOLEDO-III-5P-MPV-01	HIGH	5P五门高顶车身外廓。	READY
23234	23234	Sedan	Avenger	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	HIGH	JS四门轿车外廓。	READY
23235	23235	Sedan	Avenger	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	HIGH	JS四门轿车外廓。	READY
23240_prefl	23240	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	MEDIUM	5J8五门Praktik改款前外廓。	READY
23240_facelift	23240	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	MEDIUM	5J8五门Praktik改款后外廓。	READY
23243_prefl	23243	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	MEDIUM	5J8五门Praktik改款前外廓。	READY
23243_facelift	23243	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	MEDIUM	5J8五门Praktik改款后外廓。	READY
23245	23245	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	HIGH	5J8五门Praktik改款前外廓。	READY
23247	23247	Van	Roomster Praktik	5J8	5	EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	HIGH	5J8五门Praktik改款前外廓。	READY
23263	23263	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-1K5-WAGON-01	HIGH	1K5旅行车外廓。	READY
23264	23264	Hatchback	Mazda 3 I facelift	BK	5	EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	HIGH	BK MPS宽体五门外廓。	READY
23265_ud0_mwb	23265	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	UD0单排中轴底盘外廓。	READY
23265_ud0_lwb	23265	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	UD0单排长轴底盘外廓。	READY
23265_hd0_lwb	23265	Pickup	Movano A facelift	HD0	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	HD0双排长轴底盘外廓。	READY
23266_ud0_mwb	23266	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	HIGH	UD0单排中轴底盘外廓。	READY
23266_ud0_lwb	23266	Pickup	Movano A facelift	UD0	2	EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	HIGH	UD0单排长轴底盘外廓。	READY
23266_hd0_lwb	23266	Pickup	Movano A facelift	HD0	4	EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	HIGH	HD0双排长轴底盘外廓。	READY
23267_swb_lowroof	23267	Van	Transporter T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	SWB低顶Kasten外廓。	READY
23267_swb_medroof	23267	Van	Transporter T5	7HA		EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	SWB中顶Kasten外廓。	READY
23267_lwb_lowroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	LWB低顶Kasten外廓。	READY
23267_lwb_medroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	LWB中顶Kasten外廓。	READY
23267_lwb_highroof	23267	Van	Transporter T5	7HH		EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶Kasten外廓。	READY
23268	23268	Wagon	Octavia I facelift	1U5	5	EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	HIGH	1U5前驱旅行车外廓。	READY
23276	23276	Wagon	Vectra C facelift	Z02	5	EU-OPEL-VECTRA-C-Z02-WAGON-FACELIFT-01	HIGH	Z02改款后Caravan外廓。	READY
23277	23277	SUV	Samurai (SJ)	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	MEDIUM	SJ413三门硬顶外廓；输入功率高于常见欧洲资料，车身边界一致。	READY
23278	23278	Convertible	G-Class Cabriolet W463 facelift 2007	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-2007-01	HIGH	W463短轴双门敞篷越野车外廓。	READY
23279	23279	Coupe	Roadster Coupé	452	2	EU-SMART-ROADSTER-452-COUPE-01	MEDIUM	452双门Roadster Coupé外廓。	READY
23280	23280	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23281	23281	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23282	23282	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-01	HIGH	E70五门SUV外廓。	READY
23283_prefl	23283	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFL-01	MEDIUM	W211四门改款前分支。	READY
23283_facelift	23283	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	MEDIUM	W211四门改款后分支。	READY
23284_prefl	23284	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFL-01	MEDIUM	S211五门改款前分支。	READY
23284_facelift	23284	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	MEDIUM	S211五门改款后分支。	READY
23285_swb	23285	MPV	Transporter T5	7HB		EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	7HB短轴低顶Bus外廓。	READY
23285_lwb	23285	MPV	Transporter T5	7HJ		EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	7HJ长轴低顶Bus外廓。	READY
23286_singlecab_lwb	23286	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	MEDIUM	LWB单排驾驶室底盘外廓。	READY
23286_doublecab_lwb	23286	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	MEDIUM	LWB双排驾驶室底盘外廓。	READY
23287	23287	Convertible	Continental GTC		2	EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	MEDIUM	第一代Continental GTC双门敞篷外廓。	READY
23288	23288	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-ED-WAGON-01	HIGH	ED五门旅行车外廓。	READY
23289	23289	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-ED-HATCHBACK-01	HIGH	ED五门掀背外廓。	READY
23290_prefl	23290	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	MEDIUM	该Ktype覆盖改款前1Z5旅行车外廓。	READY
23290_facelift	23290	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	MEDIUM	该Ktype覆盖改款后1Z5旅行车外廓。	READY
23291	23291	Hatchback	Octavia I facelift	1U2	5	EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	HIGH	1U2五门Tour掀背外廓。	READY
23292_prefl	23292	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-PREFL-01	MEDIUM	5J五门MPV改款前外廓。	READY
23292_facelift	23292	MPV	Roomster	5J	5	EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	MEDIUM	5J五门MPV改款后外廓。	READY
23293	23293	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	HIGH	3U4四门改款后外廓。	READY
23294_prefl	23294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-PREFL-01	MEDIUM	3U4四门改款前分支。	READY
23294_facelift	23294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	MEDIUM	3U4四门改款后分支。	READY
23295	23295	Sedan	Jetta V	1K2	4	EU-VW-JETTA-V-1K2-SEDAN-01	HIGH	1K2四门轿车外廓。	READY
23296_prefl	23296	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	MEDIUM	LD四门改款前外廓。	READY
23296_facelift	23296	Sedan	Cerato I	LD	4	EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	MEDIUM	LD四门改款后外廓。	READY
23297_prefl	23297	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-PREFL-01	MEDIUM	LD五门改款前外廓。	READY
23297_facelift	23297	Hatchback	Cerato I	LD	5	EU-KIA-CERATO-I-LD-HATCHBACK-FACELIFT-01	MEDIUM	LD五门改款后外廓。	READY
23298	23298	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH	7L改款后五门SUV外廓。	READY
23299	23299	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23300	23300	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23301_prefl	23301	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	MEDIUM	该Ktype覆盖改款前外廓。	READY
23301_facelift	23301	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	MEDIUM	该Ktype覆盖改款后外廓。	READY
23302	23302	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23303	23303	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	8K2四门改款前外廓。	READY
23304	23304	Coupe	Continental GT I	3W	2	EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	HIGH	第一代GT Speed双门外廓。	READY
23305_3dr_phase1	23305	Hatchback	Clio I Phase I		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-I-01	MEDIUM	Phase I三门物理外廓。	READY
23305_5dr_phase1	23305	Hatchback	Clio I Phase I		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-I-01	MEDIUM	Phase I五门物理外廓。	READY
23305_3dr_phase2	23305	Hatchback	Clio I Phase II		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	MEDIUM	Phase II三门物理外廓。	READY
23305_5dr_phase2	23305	Hatchback	Clio I Phase II		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	Phase II五门物理外廓。	READY
23306	23306	Sedan	Grandeur/Azera IV	TG	4	EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	MEDIUM	TG四门轿车外廓；150 hp早期版本沿用同一车身。	READY
23307	23307	Sedan	Grandeur/Azera IV	TG	4	EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	HIGH	TG四门轿车外廓。	READY
23308	23308	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH	JM五门SUV外廓。	READY
23309	23309	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-JM-SUV-01	HIGH	JM五门SUV外廓。	READY
23310	23310	MPV	H-1 / Starex I	A1	4	EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	MEDIUM	A1短轴四驱客车外廓。	READY
23311	23311	MPV	H-1 / Starex I	A1	4	EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	HIGH	A1短轴四驱客车外廓。	READY
23312	23312	MPV	H-1 / Starex I facelift	A1	4	EU-HYUNDAI-H1-A1-BUS-SWB-FACELIFT-01	MEDIUM	A1改款后标准轴距客车外廓。	READY
23314	23314	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-NF-SEDAN-01	MEDIUM	NF四门轿车外廓；136 hp版本沿用同一车身。	READY
23317	23317	Van	H-1 / Starex I	A1	4	EU-HYUNDAI-H1-A1-VAN-SWB-PREFL-01	MEDIUM	A1标准轴距厢式车外廓。	READY
23318	23318	Sedan	TXII		4	EU-LTI-TXII-SEDAN-01	HIGH	TXII四门出租车车身外廓。	READY
23319	23319	Sedan	TX4		4	EU-LTI-TX4-SEDAN-01	HIGH	TX4四门出租车车身外廓。	READY
23338_prefl	23338	Coupe	Eclipse I	1G	3	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-PREFL-01	MEDIUM	该Ktype覆盖1G改款前外廓。	READY
23338_facelift	23338	Coupe	Eclipse I facelift	1G	3	EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-FACELIFT-01	MEDIUM	该Ktype覆盖1992改款后外廓。	READY
23353_prefl	23353	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	MEDIUM	179五门改款前外廓。	READY
23353_facelift	23353	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	MEDIUM	179五门改款后外廓。	READY
23354_prefl	23354	MPV	Ulysse II	179	5	EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	MEDIUM	179五门改款前外廓。	READY
23354_facelift	23354	MPV	Ulysse II facelift	179	5	EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	MEDIUM	179五门改款后外廓。	READY
23355	23355	Wagon	159	939	5	EU-ALFA-ROMEO-159-SPORTWAGON-01	HIGH	939五门Sportwagon外廓。	READY
23356	23356	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
23357_prefl	23357	MPV	Musa I		5	EU-LANCIA-MUSA-I-MPV-PREFL-01	MEDIUM	五门改款前外廓。	READY
23357_facelift	23357	MPV	Musa I facelift		5	EU-LANCIA-MUSA-I-MPV-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
23358	23358	MPV	Phedra I		5	EU-LANCIA-PHEDRA-I-MPV-01	HIGH	五门MPV外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1601-1700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2868170/porsche_911_turbo_cabriolet_tiptronic_s.html
EU-FIAT-500-312-HATCHBACK-3D-PREFL-01	3546	1627	1488	Auto-Data.net	https://www.auto-data.net/en/fiat-500-312-1.2-8v-69hp-16748
EU-VW-TIGUAN-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-i-2.0-tdi-140hp-4motion-44135
EU-VW-TIGUAN-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-2.0-tdi-140hp-4motion-18455
EU-CITROEN-C3-I-HATCHBACK-PHASE-I-01	3850	1667	1529	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-i-2002-1.4i-73hp-15088
EU-CITROEN-C3-I-HATCHBACK-PHASE-II-01	3860	1667	1510	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.4i-73hp-6056
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285	Auto-Data.net	https://www.auto-data.net/en/porsche-911-997-gt2-3.6-530hp-6584
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-p12-1.6-i-16v-109hp-592
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-hatch-p12-1.6-i-16v-109hp-599
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4f-c6-2.8-fsi-v6-210hp-4650
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463	Auto-Data.net	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.8-fsi-v6-210hp-quattro-tiptronic-26731
EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	5062	1894	1444	Auto-Data.net	https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2007-2.8-fsi-e-v6-210hp-multitronic-4810
EU-CADILLAC-BLS-SEDAN-01	4680	1752	1471	Auto-Data.net	https://www.auto-data.net/en/cadillac-bls-2.0-t-175hp-11689
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-t-jet-120hp-35742
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-t-jet-120hp-35742
EU-VW-GOLF-V-1K5-WAGON-01	4556	1781	1504	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.4-tsi-170hp-dsg-8642
EU-NISSAN-X-TRAIL-T31-SUV-PREFL-01	4630	1785	1685	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-ii-t31-2.0-dci-150hp-4x4-906
EU-NISSAN-X-TRAIL-T31-SUV-FACELIFT-01	4635	1790	1700	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-ii-t31-facelift-2010-2.0-dci-173hp-4x4-29962
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480	Auto-Data.net	https://www.auto-data.net/en/nissan-primera-wagon-p12-1.9-dci-120hp-608
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.2-70hp-3-d-8410
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.2-70hp-5-d-8411
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data.net	https://www.auto-data.net/en/fiat-bravo-ii-198-1.4-t-jet-120hp-dualogic-54964
EU-FIAT-LINEA-323-SEDAN-01	4560	1730	1494	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/729170/fiat_linea_1_4_t-jet_16v_emotion.html
EU-PEUGEOT-1007-MPV-3D-01	3731	1686	1620	Auto-Data.net	https://www.auto-data.net/en/peugeot-1007-model-566
EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	5680	1974	2393	Ford Transit People Movers 2007 brochure;Ford Transit Panel Vans Specifications 2007	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Auto-Data.net	https://www.auto-data.net/en/seat-altea-5p-1.8-tsi-160hp-dsg-16901
EU-SEAT-TOLEDO-III-5P-MPV-01	4458	1768	1568	Auto-Data.net	https://www.auto-data.net/en/seat-toledo-iii-5p-1.8-tsi-160hp-13532
EU-DODGE-AVENGER-JS-SEDAN-01	4850	1843	1497	Auto-Data.net	https://www.auto-data.net/en/dodge-avenger-sedan-2.0-crd-140hp-dct-51161
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-PREFL-01	4205	1684	1607	Škoda Roomster 2007 Owner's Manual	https://manualzz.com/doc/52177068/skoda-roomster--2007-05--owner-s-manual
EU-SKODA-ROOMSTER-PRAKTIK-5J8-VAN-FACELIFT-01	4213	1684	1607	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3143120/skoda_praktik_1_2_htp_70.html
EU-MAZDA-3-BK-MPS-HATCHBACK-5D-01	4435	1765	1465	Auto-Data.net	https://www.auto-data.net/en/mazda-3-i-hatchback-bk-facelift-2006-mps-2.3i-260hp-11481
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	5369	1990	2200	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	5869	1990	2195	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	5869	1990	2203	Vauxhall Movano February 2007 brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Feb_2007.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter Van March 2008 brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-i-combi-tour-facelift-2000-1.9-tdi-100hp-14266
EU-OPEL-VECTRA-C-Z02-WAGON-FACELIFT-01	4839	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-1.9-cdti-120hp-26130
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680	Auto-Data.net	https://www.auto-data.net/en/suzuki-samurai-sj-generation-3690
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-FACELIFT-2007-01	4257	1760	1941	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w463-facelift-2007-g-320-cdi-v6-224hp-4matic-7g-tronic-17398
EU-SMART-ROADSTER-452-COUPE-01	3427	1615	1207	Auto-Data.net	https://www.auto-data.net/en/smart-roadster-coupe-0.7-i-82hp-14883
EU-BMW-X5-E70-SUV-01	4854	1933	1766	BMW Group PressClub X5 gasoline technical data;BMW Group PressClub X5 3.0d technical data	https://www.press.bmwgroup.com/korea/article/detail/T0046106KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-x5-%EA%B0%80%EC%86%94%EB%A6%B0-%EB%AA%A8%EB%8D%B8-%EC%B6%9C%EC%8B%9C?language=ko;https://www.press.bmwgroup.com/korea/article/detail/T0046065KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EC%8A%A4%ED%8F%AC%EC%B8%A0-%EB%9F%AD%EC%85%94%EB%A6%AC-%EC%82%AC%EB%A5%9C%EA%B5%AC%EB%8F%99-%EB%89%B4-x5-%EC%B6%9C%EC%8B%9C?language=ko
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-PREFL-01	4818	1822	1452	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-e-220-cdi-150hp-12876
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-FACELIFT-01	4856	1822	1483	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-200-cdi-136hp-12870
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-PREFL-01	4850	1822	1496	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-220-cdi-150hp-12912
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-FACELIFT-01	4888	1822	1506	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-220-cdi-170hp-12913
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1949	Volkswagen Transporter T5 specifications March 2014;Volkswagen Transporter January 2008 price list	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf;https://www.vwpress.co.uk/assets/documents/original/16899-transporter_prices_1.pdf
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963	Volkswagen Transporter T5 specifications March 2014;Volkswagen Transporter January 2008 price list	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf;https://www.vwpress.co.uk/assets/documents/original/16899-transporter_prices_1.pdf
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398	Auto-Data.net	https://www.auto-data.net/en/bentley-continental-gtc-6.0-i-w12-48v-560hp-6754
EU-KIA-CEED-I-ED-WAGON-01	4470	1790	1490	Auto-Data.net	https://www.auto-data.net/en/kia-ceed-sw-i-2.0-crdi-140hp-42444
EU-KIA-CEED-I-ED-HATCHBACK-01	4235	1790	1480	Auto-Data.net	https://www.auto-data.net/en/kia-ceed-i-2.0-crdi-140hp-42284
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/3137930/skoda_octavia_combi_1_4_16v_80.html
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462	Autodata24	https://autodata24.com/skoda/octavia/octavia-ii-fl-combi-1z5/14-mpi-80-hp/details
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-i-tour-facelift-2000-1.9-tdi-100hp-55861
EU-SKODA-ROOMSTER-5J-MPV-PREFL-01	4205	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-1.2-12v-64hp-14270
EU-SKODA-ROOMSTER-5J-MPV-FACELIFT-01	4214	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-facelift-2010-1.2-htp-70hp-19231
EU-SKODA-SUPERB-I-3U4-SEDAN-FACELIFT-01	4803	1765	1469	Auto-Data.net	https://www.auto-data.net/en/skoda-superb-i-facelift-2006-1.9-tdi-115hp-44980
EU-SKODA-SUPERB-I-3U4-SEDAN-PREFL-01	4803	1765	1469	Auto-Data.net	https://www.auto-data.net/en/skoda-superb-i-1.9-tdi-131hp-14115
EU-VW-JETTA-V-1K2-SEDAN-01	4554	1781	1459	Auto-Data.net	https://www.auto-data.net/en/volkswagen-jetta-v-1.4-tsi-122hp-dsg-9073
EU-KIA-CERATO-I-LD-SEDAN-PREFL-01	4480	1735	1470	Auto-Data.net	https://www.auto-data.net/en/kia-cerato-i-sedan-1.6-105hp-32542
EU-KIA-CERATO-I-LD-SEDAN-FACELIFT-01	4500	1735	1470	Kia Cerato 2007 Owner's Manual	https://www.carmanualsonline.info/kia-cerato-2007-owners-manual/?srch=dimensions
EU-KIA-CERATO-I-LD-HATCHBACK-PREFL-01	4340	1735	1470	Auto-Data.net	https://www.auto-data.net/en/kia-cerato-i-hatchback-1.6-105hp-32535
EU-KIA-CERATO-I-LD-HATCHBACK-FACELIFT-01	4350	1735	1470	Kia Cerato 2007 Owner's Manual	https://www.carmanualsonline.info/kia-cerato-2007-owners-manual/?srch=dimensions
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726	Volkswagen Newsroom Touareg I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-touareg-1-profile-19718
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Audi UK The New A4 Saloon press information	https://press.audi.co.uk/assets/documents/original/13844-AudiUK00000262ThenewAudiA4Saloon2008.pdf
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Audi UK A4 3.0 TDI quattro technical data	https://press.audi.co.uk/assets/documents/original/13834-AudiUK00000070A430TDIquattroStronic.pdf
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380	Auto-Data.net	https://www.auto-data.net/en/bentley-continental-gt-speed-6.0i-w12-48v-twin-turbo-610hp-6753
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-I-01	3709	1616	1395	Auto-Data.net	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-I-01	3709	1616	1395	Auto-Data.net	https://www.auto-data.net/en/renault-clio-i-phase-i-generation-2134
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	3709	1625	1395	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Renault/6417/Renault-Clio-1-Phase-2-12.html
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	3709	1625	1395	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Renault/6417/Renault-Clio-1-Phase-2-12.html
EU-HYUNDAI-GRANDEUR-TG-SEDAN-01	4895	1865	1490	Auto-Data.net	https://www.auto-data.net/en/hyundai-grandeur-azera-iv-tg-2.2-crdi-155hp-automatic-13800
EU-HYUNDAI-TUCSON-JM-SUV-01	4325	1830	1730	Auto-Data.net	https://www.auto-data.net/en/hyundai-tucson-model-2083
EU-HYUNDAI-H1-A1-BUS-SWB-4WD-01	4695	1820	1880	Auto-Data.net	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-4wd-swb-101hp-13858
EU-HYUNDAI-H1-A1-BUS-SWB-FACELIFT-01	4625	1820	1880	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/1179740/hyundai_h-1_sv_2_5_crdi.html
EU-HYUNDAI-SONATA-NF-SEDAN-01	4800	1832	1475	Auto-Data.net	https://www.auto-data.net/en/hyundai-sonata-v-nf-2.0-crdi-16v-140hp-13816
EU-HYUNDAI-H1-A1-VAN-SWB-PREFL-01	4695	1820	1880	Auto.ae Hyundai H-1 I Van specifications	https://auto.ae/catalog/hyundai/h_1/1997-2004-i/van/
EU-LTI-TXII-SEDAN-01	4580	1800	1834	Automobile-Catalog	https://www.automobile-catalog.com/car/2004/338720/lti_tx_ii_automatic.html
EU-LTI-TX4-SEDAN-01	4580	1800	1834	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/338750/lti_tx4.html
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-PREFL-01	4390	1695	1321	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-generation-3435
EU-MITSUBISHI-ECLIPSE-I-1G-COUPE-FACELIFT-01	4390	1695	1306	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-eclipse-i-1g-facelift-1992-1.8-92hp-43092
EU-FIAT-ULYSSE-II-179-MPV-PREFL-01	4719	1863	1752	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-ii-179-2.0-jtd-multijet-16v-136hp-53052
EU-FIAT-ULYSSE-II-179-MPV-FACELIFT-01	4719	1863	1759	Auto-Data.net	https://www.auto-data.net/en/fiat-ulysse-ii-179-facelift-2008-2.0-jtd-multijet-16v-136hp-53053
EU-ALFA-ROMEO-159-SPORTWAGON-01	4660	1828	1417	Alfa Romeo 159 and 159 Sportwagon official specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1417	Alfa Romeo 159 and 159 Sportwagon official specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-LANCIA-MUSA-I-MPV-PREFL-01	3985	1698	1688	Auto-Data.net	https://www.auto-data.net/en/lancia-musa-1.3-multijet-90hp-31785
EU-LANCIA-MUSA-I-MPV-FACELIFT-01	4035	1698	1660	Auto-Data.net	https://www.auto-data.net/en/lancia-musa-facelift-2007-1.3-multijet-90hp-automatic-31788
EU-LANCIA-PHEDRA-I-MPV-01	4750	1863	1759	Auto-Data.net	https://www.auto-data.net/en/lancia-phedra-2.0-multijet-16v-136hp-dpf-45952
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1601-1700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.co.uk/car-parts/blower-motor-sesistor-10965/hyundai/h-1-kasten/h-1-box/23317-2-5-crdi "https://www.autodoc.co.uk/car-parts/blower-motor-sesistor-10965/hyundai/h-1-kasten/h-1-box/23317-2-5-crdi"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01 的 HeightMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1601-1700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1601-1700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2532 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1339 行）

- 尺寸冲突协调：
  - EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01 -> EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02：5292x1904x1963 与 5292x1904x1949，创建新尺寸组
  - EU-HYUNDAI-SONATA-NF-SEDAN-01 -> EU-HYUNDAI-SONATA-NF-SEDAN-02：4800x1830x1480 与 4800x1832x1475，创建新尺寸组
  - EU-ALFA-ROMEO-159-SEDAN-01 -> EU-ALFA-ROMEO-159-SEDAN-02：4660x1828x1422 与 4660x1828x1417，创建新尺寸组
  - EU-LANCIA-PHEDRA-I-MPV-01 -> EU-LANCIA-PHEDRA-I-MPV-02：4750x1863x1760 与 4750x1863x1759，创建新尺寸组
