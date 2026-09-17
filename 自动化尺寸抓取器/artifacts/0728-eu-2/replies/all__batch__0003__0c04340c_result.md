# 任务：all 第 201-300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0003__0c04340c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 201-300 行

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
all 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	307	1.6 HDI	Schrägheck	Frontantrieb	Diesel	66	90	Apr 2005	Mar 2009	2024-03-01	19341
Peugeot	Boxer	2.8 HDI	Kasten	Frontantrieb	Diesel	107	146	Apr 2004	Jun 2006	2024-03-01	19342
Peugeot	Boxer	2.8 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2004	Jun 2006	2024-03-01	19343
Mercedes-benz	Gl-Klasse	GL 450 4-matic	SUV	Allrad	Benzin	250	340	Sep 2006	Aug 2012	2024-03-01	19344
Mercedes-benz	Gl-Klasse	GL 500 4-matic	SUV	Allrad	Benzin	285	388	Sep 2006	Dec 2012	2024-03-01	19345
Mercedes-benz	Gl-Klasse	GL 420 CDI 4-matic	SUV	Allrad	Diesel	225	306	Sep 2006	May 2009	2024-03-01	19346
Mercedes-benz	Gl-Klasse	GL 320 CDI 4-matic	SUV	Allrad	Diesel	165	224	Sep 2006	May 2009	2024-03-01	19347
Peugeot	207/207+	1.4 16V	Schrägheck	Frontantrieb	Benzin	65	88	Feb 2006	Oct 2013	2024-03-01	19349
Peugeot	207/207+	1.6 16V	Schrägheck	Frontantrieb	Benzin	80	109	Feb 2006	Oct 2013	2024-03-01	19350
Peugeot	207/207+	1.6 16V Turbo	Schrägheck	Frontantrieb	Benzin	110	150	Feb 2006	Oct 2013	2024-03-01	19351
Peugeot	207/207+	1.6 HDI	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2006	Oct 2013	2024-03-01	19352
Peugeot	207/207+	1.6 HDI	Schrägheck	Frontantrieb	Diesel	80	109	Feb 2006	Oct 2013	2024-03-01	19353
Peugeot	207/207+	1.4 HDI	Schrägheck	Frontantrieb	Diesel	50	68	Feb 2006	Dec 2015	2024-03-01	19354
Renault	Clio iii	2.0 16V Sport	Schrägheck	Frontantrieb	Benzin	145	197	Feb 2006	Dec 2012	2026-05-01	19355
Renault	Laguna ii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	127	173	Jan 2006	Aug 2007	2024-03-01	19356
Renault	Laguna ii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	127	173	Jan 2006	Dec 2007	2024-03-01	19357
Renault	Espace iv	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2015	2025-12-01	19358
Renault	Espace iv	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	127	173	Jan 2006	Dec 2015	2025-12-01	19359
Renault	Espace iv	3.0 DCI	Großraumlimousine	Frontantrieb	Diesel	133	181	Jan 2006	Jan 2015	2024-03-01	19360
Opel	Signum cc	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Sep 2005	Dec 2008	2024-03-01	19361
Opel	Astra h twintop	1.8	Cabriolet	Frontantrieb	Benzin	103	140	Sep 2005	Oct 2010	2024-03-01	19362
Mitsubishi	Colt czc vi	1.5	Cabriolet	Frontantrieb	Benzin	80	109	May 2006	Jul 2009	2024-03-01	19363
Mitsubishi	Colt czc vi	1.5 Turbo	Cabriolet	Frontantrieb	Benzin	110	150	May 2006	Jul 2009	2024-03-01	19364
Mitsubishi	L200	2.5 Di-d 4WD	Pick-up	Allrad	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	19365
Mitsubishi	Lancer vii	EVO IX	Stufenheck	Allrad	Benzin	206	280	Jan 2005	Sep 2007	2024-03-01	19366
Lancia	Thesis	2.4 D Multijet	Stufenheck	Frontantrieb	Diesel	136	185	Apr 2006	Jul 2009	2024-03-01	19367
Dacia	Logan	1.6 16V	Stufenheck	Frontantrieb	Benzin	77	105	Feb 2006	-	2024-03-01	19368
Marcos	Tso convertible	5.7 V8	Cabriolet	Heckantrieb	Benzin	260	354	May 2004	-	2024-03-01	19369
Saab	9-3	1.9 TID	Cabriolet	Frontantrieb	Diesel	110	150	Jan 2006	Feb 2015	2024-03-01	19371
Marcos	Tso gt2	5.7 V8	Coupe	Heckantrieb	Benzin	354	481	Jul 2005	-	2024-03-01	19372
Saab	9-5	1.9 TID	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2009	2024-03-01	19374
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1983	Dec 1984	2024-03-01	19375
Saab	9-5	1.9 TID	Kombi	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2009	2024-03-01	19376
Lotus	Exige	1.8 16V	Coupe	Heckantrieb	Benzin	163	222	Apr 2006	Jun 2012	2024-03-01	19378
Lamborghini	Murciélago	LP 640	Coupe	Allrad	Benzin	471	641	Apr 2006	-	2024-03-01	19379
Lamborghini	Gallardo	5	Cabriolet	Allrad	Benzin	382	520	Aug 2005	-	2024-03-01	19380
VW	Jetta i	1.3	Stufenheck	Frontantrieb	Benzin	43	58	Aug 1982	Feb 1984	2024-03-01	19382
VW	Golf ii	1.8 GTI	Schrägheck	Frontantrieb	Benzin	77	105	Jan 1985	Jul 1985	2024-03-01	19383
Peugeot	407	2.7 HDI	Stufenheck	Frontantrieb	Diesel	150	204	Oct 2005	Dec 2010	2024-03-01	19387
Peugeot	407	2.7 HDI	Kombi	Frontantrieb	Diesel	150	204	Oct 2005	Dec 2010	2024-03-01	19388
Mercedes-benz	Sl	350	Cabriolet	Heckantrieb	Benzin	200	272	Mar 2006	Jan 2012	2024-03-01	19389
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	285	388	Mar 2006	Jan 2012	2024-03-01	19390
Mercedes-benz	Sl	600	Cabriolet	Heckantrieb	Benzin	380	517	Mar 2006	Jan 2012	2024-03-01	19391
Mercedes-benz	Sl	55 AMG	Cabriolet	Heckantrieb	Benzin	380	517	Mar 2006	Jan 2012	2024-03-01	19392
Suzuki	Grand vitara ii	1.9 Ddis Allrad	Geländewagen geschlossen	Allrad	Diesel	95	129	Oct 2005	Feb 2015	2024-03-01	19393
VW	Passat b6	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	147	200	Jul 2005	Jul 2010	2024-03-01	19395
VW	Passat b6 variant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	147	200	Aug 2005	Nov 2010	2024-03-01	19396
Renault	Megane ii coupé-	1.9 DCI	Cabriolet	Frontantrieb	Diesel	81	110	May 2005	Mar 2009	2024-03-01	19397
Renault	Megane ii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Sep 2005	Feb 2008	2024-03-01	19398
Renault	Megane ii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	110	150	Sep 2005	Jul 2009	2024-03-01	19399
Renault	Megane ii coupé-	2.0 DCI	Cabriolet	Frontantrieb	Diesel	110	150	Sep 2005	Mar 2009	2024-03-01	19400
Renault	Scénic ii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Sep 2005	Nov 2008	2024-03-01	19401
Volvo	V70 ii	D5	Kombi	Frontantrieb	Diesel	136	185	Apr 2005	Dec 2008	2024-03-01	19402
Volvo	V70 ii	D5 AWD	Kombi	Allrad	Diesel	136	185	May 2005	Aug 2007	2024-03-01	19403
Volvo	Xc70 i cross country	D5 AWD	Kombi	Allrad	Diesel	136	185	Dec 2005	Aug 2007	2024-03-01	19404
Peugeot	307	1.6 HDI	Kombi	Frontantrieb	Diesel	66	90	Apr 2005	Apr 2008	2024-03-01	19405
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19406
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19407
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19408
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19409
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19410
Citroën	Berlingo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	80	109	Oct 2000	Mar 2008	2024-03-01	19411
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19412
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19413
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19414
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19415
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19416
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19417
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19418
VW	Golf i	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1983	Feb 1984	2024-03-01	19419
Opel	Astra h	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Jan 2006	Oct 2010	2024-03-01	19427
Opel	Astra h gtc	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Jan 2006	Oct 2010	2024-03-01	19428
Daewoo	Leganza	2.0 16V	Stufenheck	Frontantrieb	Benzin	93	126	Jul 2000	Apr 2004	2024-03-01	19429
Daewoo	Nubira	2.0 16V	Stufenheck	Frontantrieb	Benzin	93	126	Dec 2000	-	2024-03-01	19430
Daewoo	Nubira	2.0 16V	Kombi	Frontantrieb	Benzin	93	126	Dec 2000	-	2024-03-01	19431
Daewoo	Nubira	1.6 16V	Kombi	Frontantrieb	Benzin	76	103	Dec 2000	-	2024-03-01	19432
Daewoo	Nubira	1.6 16V	Stufenheck	Frontantrieb	Benzin	76	103	Jul 2000	-	2024-03-01	19433
Daewoo	Nubira	1.6 16V	Kombi	Frontantrieb	Benzin	66	90	Jun 1997	-	2024-03-01	19434
Daewoo	Rezzo	1.8	Großraumlimousine	Frontantrieb	Benzin	67	91	Sep 2000	-	2024-03-01	19435
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	191	260	Jan 2006	Dec 2009	2024-03-01	19436
Ford	Galaxy ii	2	Großraumlimousine	Frontantrieb	Benzin	107	145	May 2006	Jun 2015	2024-03-01	19437
Ford	Galaxy ii	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	74	100	May 2006	Jun 2015	2024-03-01	19438
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	96	130	May 2006	Jun 2015	2024-03-01	19439
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2006	Jun 2015	2024-03-01	19440
Ford	S-Max	2	Großraumlimousine	Frontantrieb	Benzin	107	145	May 2006	Dec 2014	2024-03-01	19441
Ford	S-Max	2.5 ST	Großraumlimousine	Frontantrieb	Benzin	162	220	May 2006	Dec 2014	2024-03-01	19442
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	96	130	May 2006	Dec 2014	2024-03-01	19443
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2006	Dec 2014	2024-03-01	19444
Alfa Romeo	159	1.9 JTS	Kombi	Frontantrieb	Benzin	118	160	Mar 2006	Nov 2011	2024-03-01	19445
Alfa Romeo	159	2.2 JTS	Kombi	Frontantrieb	Benzin	136	185	Mar 2006	Nov 2011	2024-03-01	19446
Alfa Romeo	159	3.2 JTS Q4	Kombi	Allrad	Benzin	191	260	Mar 2006	Nov 2011	2024-03-01	19447
Alfa Romeo	159	1.9 Jtdm 8V	Kombi	Frontantrieb	Diesel	88	120	Mar 2006	Nov 2011	2024-03-01	19448
Alfa Romeo	159	1.9 Jtdm 16V	Kombi	Frontantrieb	Diesel	110	150	Mar 2006	Nov 2011	2024-03-01	19449
Alfa Romeo	159	2.4 Jtdm	Kombi	Frontantrieb	Diesel	147	200	Mar 2006	Nov 2011	2024-03-01	19450
Porsche	Cayenne	Turbo S 4.5	SUV	Allrad	Benzin	383	521	May 2002	May 2006	2025-06-01	19451
Porsche	911	3.6 Turbo	Coupe	Allrad	Benzin	353	480	Mar 2006	Dec 2009	2024-03-01	19452
Audi	Tt	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Aug 2006	Jun 2010	2024-03-01	19453
Audi	Tt	3.2 V6 Quattro	Coupe	Allrad	Benzin	184	250	Aug 2006	Jun 2010	2024-03-01	19454
VW	Touareg	3.6 V6 FSI	SUV	Allrad	Benzin	206	280	Oct 2005	May 2010	2024-03-01	19455
Audi	A6 c6	S6 Quattro	Stufenheck	Allrad	Benzin	320	435	Mar 2006	Mar 2011	2024-03-01	19456


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 100 个输入 Ktype 的首轮物理车身拆分，形成 122 条映射行。
* 已闭合 Peugeot 207 改款前后、Saab 9-3 敞篷改款前后、Passat B6 轿车/旅行版、Porsche 911 Turbo 997、Audi TT 8J、Audi S6 C6 等尺寸组。207 改款后页面明确区分车身宽度、折叠后视镜宽度和含镜宽度；Saab 9-3 改款前后也提供了不同外廓数据。([汽车数据网][1])
* Astra H 五门及 Astra H GTC 改款前后直接复用历史缓存，未重复输出尺寸来源。
* 严格拦截了宽度口径不明、单值高度无法确定及商用车轴距/车顶未拆分的候选。例如 S-Max 改款页面的 2154 mm 实际属于含镜量级，Galaxy 改款页面高度为范围，因此暂不建立完整尺寸组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：122
* READY 映射：68
* PENDING 映射：54
* 全部分支 READY 的 Ktype：46
* 部分 READY、部分 PENDING 的 Ktype：8
* 全部分支 PENDING 的 Ktype：46
* 已确认并被引用的尺寸组：43

  * 本轮首次创建：40
  * 复用历史缓存：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19341	19341	Hatchback	Peugeot 307 I facelift			EU-PEUGEOT-307-I-FACELIFT-HATCHBACK-01	HIGH	掀背外廓；门数不构成尺寸分支。	READY
19342	19342	Van	Peugeot Boxer I facelift				LOW	需拆分短/中/长轴及车顶高度。	PENDING: Kasten轴距与车顶分支尚未闭合
19343	19343	Pickup	Peugeot Boxer I facelift				LOW	底盘驾驶室存在不同轴距与后部配置。	PENDING: Pritsche/Fahrgestell物理分支尚未闭合
19344_prefl	19344	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH	2009改款前外廓。	READY
19344_facelift	19344	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19345_prefl	19345	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH	2009改款前外廓。	READY
19345_facelift	19345	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19346	19346	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH		READY
19347	19347	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH		READY
19349_prefl	19349	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19349_facelift	19349	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19350_prefl	19350	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19350_facelift	19350	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19351_prefl	19351	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19351_facelift	19351	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19352_prefl	19352	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19352_facelift	19352	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19353_prefl	19353	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19353_facelift	19353	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19354_prefl	19354	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19354_facelift	19354	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；含207+延续外廓。	READY
19355	19355	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	HIGH	RS三门外廓。	READY
19356	19356	Hatchback	Renault Laguna II facelift		5	EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	HIGH		READY
19357	19357	Wagon	Renault Laguna II Grandtour facelift		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	HIGH		READY
19358	19358	MPV	Renault Espace IV				LOW	候选包含标准轴距与Grand Espace长轴。	PENDING: Ktype是否覆盖标准/Grand外廓尚未确认
19359	19359	MPV	Renault Espace IV				LOW	候选包含标准轴距与Grand Espace长轴。	PENDING: Ktype是否覆盖标准/Grand外廓尚未确认
19360	19360	MPV	Renault Espace IV				LOW	候选包含标准轴距与Grand Espace长轴。	PENDING: Ktype是否覆盖标准/Grand外廓尚未确认
19361	19361	Hatchback	Opel Signum facelift		5	EU-OPEL-SIGNUM-I-FACELIFT-HATCHBACK-01	HIGH		READY
19362	19362	Convertible	Opel Astra H TwinTop		2	EU-OPEL-ASTRA-H-TWINTOP-CONVERTIBLE-01	HIGH		READY
19363	19363	Convertible	Mitsubishi Colt VI CZC		2		LOW	自然吸气外廓；现有页面宽度标为含镜。	PENDING: 缺少without-mirrors宽度
19364	19364	Convertible	Mitsubishi Colt VI CZC		2		LOW	Turbo外廓与自然吸气不同；现有页面宽度标为含镜。	PENDING: 缺少without-mirrors宽度
19365	19365	Pickup	Mitsubishi L200 IV				LOW	需拆分Single/Club/Double Cab及货斗外廓。	PENDING: CAB/BED与改款分支尚未闭合
19366	19366	Sedan	Mitsubishi Lancer Evolution IX		4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-01	HIGH	标准280 hp外廓。	READY
19367	19367	Sedan	Lancia Thesis		4	EU-LANCIA-THESIS-I-SEDAN-01	HIGH		READY
19368_prefl	19368	Sedan	Dacia Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	HIGH	2008改款前外廓。	READY
19368_facelift	19368	Sedan	Dacia Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	2008改款后外廓。	READY
19369	19369	Convertible	Marcos TSO		2		LOW	TSO Convertible资料稀少。	PENDING: 缺少可追溯的完整三维及without-mirrors宽度
19371_prefl	19371	Convertible	Saab 9-3 Convertible II		2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH	2007改款前外廓。	READY
19371_facelift	19371	Convertible	Saab 9-3 Convertible II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH	2007改款后外廓。	READY
19372	19372	Coupe	Marcos TSO GT2		2		LOW	GT2与TSO其他版本外廓边界未闭合。	PENDING: 缺少可追溯的完整三维及without-mirrors宽度
19374	19374	Sedan	Saab 9-5 facelift 2005		4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH		READY
19375	19375	Sedan	Volkswagen Derby 86C	86C	2		LOW	精确1.3版本与代际总页车长存在冲突。	PENDING: 车长来源冲突尚未解决
19376	19376	Wagon	Saab 9-5 Sport Combi facelift 2005		5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH		READY
19378	19378	Coupe	Lotus Exige Series 2		2		LOW	222 hp版本不同资料高度不一致。	PENDING: 具体Exige S外廓高度尚未闭合
19379	19379	Coupe	Lamborghini Murciélago LP 640		2	EU-LAMBORGHINI-MURCIELAGO-LP640-COUPE-01	HIGH		READY
19380	19380	Convertible	Lamborghini Gallardo Spyder		2		LOW	现有规格页未明确宽度是否不含后视镜。	PENDING: Gallardo Spyder缺少明确without-mirrors宽度
19382	19382	Sedan	Volkswagen Jetta I		2		LOW	精确1.3页面与代际资料车长/宽度冲突。	PENDING: 三维来源冲突尚未解决
19383	19383	Hatchback	Volkswagen Golf II			EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-01	HIGH	三/五门外廓一致。	READY
19387_prefl	19387	Sedan	Peugeot 407 I		4	EU-PEUGEOT-407-I-SEDAN-PREFL-01	HIGH	2008改款前外廓。	READY
19387_facelift	19387	Sedan	Peugeot 407 I facelift		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH	2008改款后外廓。	READY
19388_prefl	19388	Wagon	Peugeot 407 SW		5	EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	HIGH	2008改款前外廓。	READY
19388_facelift	19388	Wagon	Peugeot 407 SW facelift		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH	2008改款后外廓。	READY
19389	19389	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19390	19390	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19391	19391	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19392	19392	Convertible	Mercedes-Benz SL R230 facelift	R230	2		LOW	AMG外部包围是否改变最大外廓尚未闭合。	PENDING: SL 55 AMG专属外廓待核
19393	19393	SUV	Suzuki Grand Vitara II		5		LOW	后挂备胎计入长度的口径与历史缓存ID需核对。	PENDING: 长度口径及既有尺寸组命中未闭合
19395	19395	Sedan	Volkswagen Passat B6	3C2	4	EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	HIGH		READY
19396	19396	Wagon	Volkswagen Passat Variant B6	3C5	5	EU-VOLKSWAGEN-PASSAT-B6-VARIANT-WAGON-01	HIGH		READY
19397	19397	Convertible	Renault Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	HIGH		READY
19398	19398	Hatchback	Renault Megane II Phase II			EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	HIGH	三/五门外廓一致。	READY
19399	19399	Wagon	Renault Megane II Grandtour Phase II		5	EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	HIGH		READY
19400	19400	Convertible	Renault Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	HIGH		READY
19401_phase1	19401	MPV	Renault Scenic II Phase I		5	EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	HIGH	2006改款前外廓。	READY
19401_phase2	19401	MPV	Renault Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	HIGH	2006改款后外廓。	READY
19402	19402	Wagon	Volvo V70 II facelift		5	EU-VOLVO-V70-II-FACELIFT-WAGON-01	HIGH	前驱外廓。	READY
19403	19403	Wagon	Volvo V70 II facelift		5		LOW	AWD悬架高度可能与前驱版本不同。	PENDING: D5 AWD精确高度尚未闭合
19404	19404	Wagon	Volvo XC70 I facelift		5	EU-VOLVO-XC70-I-FACELIFT-WAGON-01	HIGH		READY
19405	19405	Wagon	Peugeot 307 I SW facelift		5		LOW	直接来源高度为1560–1580范围。	PENDING: 具体车顶配置高度未闭合
19406	19406	MPV	Volkswagen Crafter I				LOW	Bus需拆分轴距与车顶高度。	PENDING: Bus轴距/车顶物理分支尚未闭合
19407	19407	MPV	Volkswagen Crafter I				LOW	Bus需拆分轴距与车顶高度。	PENDING: Bus轴距/车顶物理分支尚未闭合
19408	19408	MPV	Volkswagen Crafter I				LOW	Bus需拆分轴距与车顶高度。	PENDING: Bus轴距/车顶物理分支尚未闭合
19409	19409	MPV	Volkswagen Crafter I				LOW	Bus需拆分轴距与车顶高度。	PENDING: Bus轴距/车顶物理分支尚未闭合
19410	19410	Van	Volkswagen Crafter I				LOW	Kasten需拆分轴距与车顶高度。	PENDING: Kasten轴距/车顶物理分支尚未闭合
19411	19411	Van	Citroën Berlingo I facelift				LOW	输入合并Kasten/MPV，需确认Ktype是否覆盖两种外廓。	PENDING: 车身边界与完整三维尚未闭合
19412	19412	Van	Volkswagen Crafter I				LOW	Kasten需拆分轴距与车顶高度。	PENDING: Kasten轴距/车顶物理分支尚未闭合
19413	19413	Van	Volkswagen Crafter I				LOW	Kasten需拆分轴距与车顶高度。	PENDING: Kasten轴距/车顶物理分支尚未闭合
19414	19414	Van	Volkswagen Crafter I				LOW	Kasten需拆分轴距与车顶高度。	PENDING: Kasten轴距/车顶物理分支尚未闭合
19415	19415	Pickup	Volkswagen Crafter I				LOW	底盘驾驶室需拆分轴距与单双排配置。	PENDING: Pritsche/Fahrgestell物理分支尚未闭合
19416	19416	Pickup	Volkswagen Crafter I				LOW	底盘驾驶室需拆分轴距与单双排配置。	PENDING: Pritsche/Fahrgestell物理分支尚未闭合
19417	19417	Pickup	Volkswagen Crafter I				LOW	底盘驾驶室需拆分轴距与单双排配置。	PENDING: Pritsche/Fahrgestell物理分支尚未闭合
19418	19418	Pickup	Volkswagen Crafter I				LOW	底盘驾驶室需拆分轴距与单双排配置。	PENDING: Pritsche/Fahrgestell物理分支尚未闭合
19419	19419	Hatchback	Volkswagen Golf I				LOW	1.6版本精确页面尚未闭合三维。	PENDING: 精确版本三维与门数边界待核
19427	19427	Hatchback	Opel Astra H	L48	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	复用既有五门尺寸组。	READY
19428_prefl	19428	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	复用既有改款前三门尺寸组。	READY
19428_facelift	19428	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	复用既有改款后三门尺寸组。	READY
19429	19429	Sedan	Daewoo Leganza		4		LOW	精确欧洲版三维尚未闭合。	PENDING: 缺少可靠完整三维及without-mirrors口径
19430	19430	Sedan	Daewoo Nubira				LOW	Nubira轿车代际/改款边界待核。	PENDING: 精确代际与完整三维尚未闭合
19431	19431	Wagon	Daewoo Nubira				LOW	Nubira旅行版代际/改款边界待核。	PENDING: 精确代际与完整三维尚未闭合
19432	19432	Wagon	Daewoo Nubira				LOW	Nubira旅行版代际/改款边界待核。	PENDING: 精确代际与完整三维尚未闭合
19433	19433	Sedan	Daewoo Nubira				LOW	Nubira轿车代际/改款边界待核。	PENDING: 精确代际与完整三维尚未闭合
19434	19434	Wagon	Daewoo Nubira				LOW	早期Nubira旅行版与后期外廓不同。	PENDING: 精确代际与完整三维尚未闭合
19435	19435	MPV	Daewoo Rezzo		5		LOW	欧洲版车型代码与三维来源待闭合。	PENDING: 缺少可靠完整三维及without-mirrors口径
19436	19436	Wagon	Saab 9-5 Sport Combi facelift 2005		5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH		READY
19437_prefl	19437	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19437_facelift	19437	MPV	Ford Galaxy II facelift		5		LOW	改款后直接来源高度为范围。	PENDING: facelift具体高度配置未闭合
19438_prefl	19438	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19438_facelift	19438	MPV	Ford Galaxy II facelift		5		LOW	改款后直接来源高度为范围。	PENDING: facelift具体高度配置未闭合
19439_prefl	19439	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19439_facelift	19439	MPV	Ford Galaxy II facelift		5		LOW	改款后直接来源高度为范围。	PENDING: facelift具体高度配置未闭合
19440_prefl	19440	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19440_facelift	19440	MPV	Ford Galaxy II facelift		5		LOW	改款后直接来源高度为范围。	PENDING: facelift具体高度配置未闭合
19441_prefl	19441	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19441_facelift	19441	MPV	Ford S-Max I facelift		5		LOW	来源宽度2154 mm为含镜口径。	PENDING: facelift缺少without-mirrors宽度
19442_prefl	19442	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19442_facelift	19442	MPV	Ford S-Max I facelift		5		LOW	来源宽度2154 mm为含镜口径。	PENDING: facelift缺少without-mirrors宽度
19443_prefl	19443	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19443_facelift	19443	MPV	Ford S-Max I facelift		5		LOW	来源宽度2154 mm为含镜口径。	PENDING: facelift缺少without-mirrors宽度
19444_prefl	19444	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19444_facelift	19444	MPV	Ford S-Max I facelift		5		LOW	来源宽度2154 mm为含镜口径。	PENDING: facelift缺少without-mirrors宽度
19445	19445	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19446	19446	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19447	19447	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19448	19448	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19449	19449	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19450	19450	Wagon	Alfa Romeo 159 Sportwagon		5		LOW	直接来源高度为1417–1422范围。	PENDING: 具体悬架/轮胎配置高度未闭合
19451	19451	SUV	Porsche Cayenne 955	955	5	EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	HIGH	Turbo S专属外廓。	READY
19452	19452	Coupe	Porsche 911 Turbo 997	997	2	EU-PORSCHE-911-997-TURBO-COUPE-01	HIGH	Turbo宽体外廓。	READY
19453	19453	Coupe	Audi TT 8J	8J	2	EU-AUDI-TT-8J-COUPE-01	HIGH		READY
19454	19454	Coupe	Audi TT 8J	8J	2	EU-AUDI-TT-8J-COUPE-01	HIGH		READY
19455	19455	SUV	Volkswagen Touareg I facelift	7L	5		LOW	来源高度为1703–1726，涉及悬架高度分支。	PENDING: 具体悬架外廓高度未闭合
19456	19456	Sedan	Audi S6 C6	4F	4	EU-AUDI-S6-C6-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-307-I-FACELIFT-HATCHBACK-01	4212	1746	1510	Auto-Data Peugeot 307 facelift 1.6 HDi 90	https://www.auto-data.net/en/peugeot-307-facelift-2005-1.6-hdi-90hp-5274
EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	5088	1920	1840	Auto-Data Mercedes-Benz GL X164 generation	https://www.auto-data.net/en/mercedes-benz-gl-x164-generation-3865
EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	5099	1920	1840	Auto-Data Mercedes-Benz GL model	https://www.auto-data.net/en/mercedes-benz-gl-model-1369
EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.6 16V 110	https://www.auto-data.net/en/peugeot-207-1.6-i-16v-110hp-5355
EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 HDi 68	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-hdi-68hp-33973
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477	Auto-Data Renault Clio III Phase I RS 197	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-rs-2.0-16v-197hp-25037
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II generation	https://www.auto-data.net/en/renault-laguna-ii-generation-2120
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443	Auto-Data Renault Laguna model	https://www.auto-data.net/en/renault-laguna-model-1016
EU-OPEL-SIGNUM-I-FACELIFT-HATCHBACK-01	4651	1798	1466	Auto-Data Opel Signum facelift 1.8 140	https://www.auto-data.net/en/opel-signum-facelift-2005-1.8i-16v-140hp-2577
EU-OPEL-ASTRA-H-TWINTOP-CONVERTIBLE-01	4476	1759	1411	Auto-Data Opel Astra H TwinTop 1.8 140	https://www.auto-data.net/en/opel-astra-h-twintop-1.8i-16v-ecotec-140hp-2387
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-01	4490	1770	1450	Auto-Data Mitsubishi Lancer Evolution IX 280	https://www.auto-data.net/en/mitsubishi-lancer-evolution-ix-2.0-mivec-280hp-4wd-15649
EU-LANCIA-THESIS-I-SEDAN-01	4888	1830	1465	Auto-Data Lancia Thesis 2.4 Multijet 185	https://www.auto-data.net/en/lancia-thesis-2.4-multijet-20v-185hp-comfortronic-45951
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.6 16V 105	https://www.auto-data.net/ro/dacia-logan-i-1.6-16v-105hp-43234
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534	Auto-Data Dacia Logan model	https://www.auto-data.net/ro/dacia-logan-model-1791
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data Saab 9-3 Convertible II	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.0-t-150hp-11947
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437	Auto-Data Saab 9-3 Convertible II facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-3-convertible-ii-facelift-2007-1.9-tid-150hp-54589
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data Saab 9-5 facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-5-facelift-2005-1.9-tid-150hp-automatic-42738
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459	Auto-Data Saab 9-5 Sport Combi facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2005-1.9-tid-150hp-42747
EU-LAMBORGHINI-MURCIELAGO-LP640-COUPE-01	4610	2058	1135	Edmunds 2008 Lamborghini Murcielago LP640 specs	https://www.edmunds.com/lamborghini/murcielago/2008/st-100957891/features-specs/
EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-01	3985	1680	1415	Auto-Data Volkswagen Golf II GTI 8V	https://www.auto-data.net/fr/volkswagen-golf-ii-5-door-1.8-gti-8v-112hp-8769
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	4532	1827	1298	Auto-Data Mercedes-Benz SL R230 facelift SL 350; Auto-Data Mercedes-Benz SL R230 facelift SL 600	https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-sl-350-v6-272hp-7g-tronic-41263;https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-sl-600-v12-517hp-automatic-40991
EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 TFSI 200	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tfsi-200hp-40832
EU-VOLKSWAGEN-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TFSI 200	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0i-16v-tfsi-200hp-automatic-28714
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404	Auto-Data Renault Megane II CC generation	https://www.auto-data.net/en/renault-megane-ii-cc-generation-2150
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	4228	1777	1458	Auto-Data Renault Megane II Phase II generation	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-generation-5607
EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II generation	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-generation-5613
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620	Auto-Data Renault Scenic II Phase I 2.0 dCi 150	https://www.auto-data.net/en/renault-scenic-ii-phase-i-2.0-dci-150hp-39488
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620	Auto-Data Renault Scenic II Phase II generation	https://www.auto-data.net/en/renault-scenic-ii-phase-ii-generation-7615
EU-VOLVO-V70-II-FACELIFT-WAGON-01	4710	1804	1465	Auto-Data Volvo V70 II facelift 2.4D	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4d-126hp-42645
EU-VOLVO-XC70-I-FACELIFT-WAGON-01	4733	1860	1562	Auto-Data Volvo XC70 model	https://www.auto-data.net/en/volvo-xc70-model-933
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723	Auto-Data Ford Galaxy II 2.0 145	https://www.auto-data.net/fr/ford-galaxy-ii-2.0-i-16v-145hp-7881
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658	Auto-Data Ford S-Max 2.0 TDCi 140	https://www.auto-data.net/en/ford-s-max-2.0-tdci-140hp-8115
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699	Auto-Data Porsche Cayenne 955 Turbo S	https://www.auto-data.net/en/porsche-cayenne-955-turbo-s-4.5-v8-521hp-tiptronic-s-6727
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300	Auto-Data Porsche 911 997 Turbo 480	https://www.auto-data.net/en/porsche-911-997-turbo-3.6-480hp-6590
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352	Auto-Data Audi TT Coupe 8J 2.0 TFSI 200	https://www.auto-data.net/en/audi-tt-coupe-8j-2.0-tfsi-200hp-4877
EU-AUDI-S6-C6-SEDAN-01	4916	1864	1449	Auto-Data Audi S6 4F C6 5.2 FSI V10	https://www.auto-data.net/fr/audi-s6-4f-c6-5.2-fsi-v10-435hp-quattro-tiptronic-4534
```

## 下一步优先处理

1. 优先批量闭合 Crafter、Boxer、L200 的轴距、车顶和 CAB/BED 分支；这是当前 PENDING 数量最大的聚类。
2. 处理 Espace IV 标准轴距/Grand Espace，以及 Galaxy、S-Max 改款后的高度或不含镜宽度。
3. 解决 Alfa 159 Sportwagon、Touareg、307 SW、Volvo V70 AWD 的高度范围。
4. 最后处理 Marcos、老款 Derby/Jetta/Golf I、Daewoo 系列等低资料覆盖车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-hdi-68hp-33973 "https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-hdi-68hp-33973"
[2]: https://www.auto-data.net/en/ford-s-max-facelift-2010-2.0-duratorq-tdci-140hp-18026 "https://www.auto-data.net/en/ford-s-max-facelift-2010-2.0-duratorq-tdci-140hp-18026"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮将 6 条映射由 `PENDING` 转为 `READY`。
* 首次闭合 Colt CZC 1.5 自然吸气、Lotus Exige S、Gallardo Spyder 和 V70 II D5 AWD 四个尺寸组；其中 Colt、Lotus、Gallardo 的宽度来源明确为不含后视镜口径。([汽车目录][1])
* SL 55 AMG 复用当前批次已有 R230 facelift 尺寸组；其三维与同组记录一致。([汽车数据网][2])
* Grand Vitara II 五门直接复用历史缓存尺寸组，未重复输出尺寸来源。其缓存三维口径已有不含后视镜宽度支持。([汽车目录][3])
* Colt CZC Turbo、S-Max facelift、Alfa 159 Sportwagon 和 Touareg 暂未强行闭合，原因分别为来源冲突或高度配置仍未拆清。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：122
* READY 映射：74
* PENDING 映射：48
* 全部分支 READY 的 Ktype：52
* 部分 READY、部分 PENDING 的 Ktype：8
* 全部分支 PENDING 的 Ktype：40
* 已确认并被当前映射引用的尺寸组：48
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19363	19363	Convertible	Mitsubishi Colt VI CZC	Z36A	2	EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-NA-01	HIGH	Z36A自然吸气外廓。	READY
19378	19378	Coupe	Lotus Exige Series 2		2	EU-LOTUS-EXIGE-S2-S-COUPE-01	HIGH	Exige S量产外廓。	READY
19380	19380	Convertible	Lamborghini Gallardo Spyder		2	EU-LAMBORGHINI-GALLARDO-SPYDER-CONVERTIBLE-01	HIGH		READY
19392	19392	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19393	19393	SUV	Suzuki Grand Vitara II		5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	HIGH	五门封闭式车身。	READY
19403	19403	Wagon	Volvo V70 II facelift		5	EU-VOLVO-V70-II-FACELIFT-WAGON-AWD-01	HIGH	AWD高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-NA-01	3875	1695	1453	Automobile-Catalog 2008 Mitsubishi Colt CZC 1.5	https://www.automobile-catalog.com/car/2008/1993535/mitsubishi_colt_czc_1_5.html
EU-LOTUS-EXIGE-S2-S-COUPE-01	3797	1727	1163	Lotus Exige S official specifications (GG Lotus archive)	https://gglotus.org/gghotnews/body-exigenews.htm
EU-LAMBORGHINI-GALLARDO-SPYDER-CONVERTIBLE-01	4300	1900	1184	Automobile-Catalog 2006 Lamborghini Gallardo Spyder E-Gear	https://www.automobile-catalog.com/car/2006/1372220/lamborghini_gallardo_spyder_e-gear.html
EU-VOLVO-V70-II-FACELIFT-WAGON-AWD-01	4710	1804	1514	Auto-Data Volvo V70 II facelift D5 AWD	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4-d5-185hp-awd-9244
```

## 下一步优先处理

1. 集中拆分 Boxer、Crafter 和 L200 的轴距、车顶及驾驶室分支。
2. 闭合 Espace IV 标准版与 Grand Espace 长轴版边界。
3. 处理 Colt CZC Turbo、Galaxy/S-Max facelift、307 SW 和 Alfa 159 Sportwagon 的冲突尺寸。
4. 最后处理 Marcos、老款 Derby/Jetta/Golf I 和 Daewoo 低资料覆盖车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/1993535/mitsubishi_colt_czc_1_5.html "https://www.automobile-catalog.com/car/2008/1993535/mitsubishi_colt_czc_1_5.html"
[2]: https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-amg-sl-55-v8-517hp-automatic-41264 "https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-amg-sl-55-v8-517hp-automatic-41264"
[3]: https://www.automobile-catalog.com/car/2006/3415070/suzuki_grand_vitara_2_7_v6_awd.html?utm_source=chatgpt.com "2006 Suzuki Grand Vitara 2.7 V6 AWD Specs Review (138 kW / 188 PS / 185 hp) (since mid-year 2005 for North America )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 将 `19360` 从标准版/Grand 版候选中闭合为 **Espace IV Phase II 标准轴距车身**，首次创建对应尺寸组。
* `19438`、`19439` 的动力版本仅属于 Galaxy II 改款前车型，删除原先无依据的 facelift 派生分支，改回单一基础 `id`。([汽车目录][1])
* `19442`、`19443` 的动力版本生产周期止于 2010 年，不跨入 S-Max facelift，删除原 facelift 派生分支并复用现有改款前尺寸组。([汽车数据网][2])
* 本轮未重复输出 Galaxy II、S-Max I 已有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：118
* READY 映射：75
* PENDING 映射：43
* 全部分支 READY 的 Ktype：57
* 部分 READY、部分 PENDING 的 Ktype：4
* 全部分支 PENDING 的 Ktype：39
* 已确认并被引用的尺寸组：49
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19360	19360	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	3.0 dCi 181仅对应Phase II标准轴距外廓。	READY
19438	19438	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	1.8 TDCi 100仅对应改款前外廓。	READY
19439	19439	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2.0 TDCi 130仅对应改款前外廓。	READY
19442	19442	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2.5 ST 220仅对应改款前外廓。	READY
19443	19443	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2.0 TDCi 130仅对应改款前外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	4656	1860	1728	Auto-Data Renault Espace IV Phase II 3.0 dCi V6 181	https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-3.0-dci-v6-181hp-automatic-20280
```

该来源分别列出车身宽度与含后视镜宽度，落盘的 `1860 mm` 为不含后视镜口径。([汽车数据网][3])

## 下一步优先处理

1. 批量拆分并闭合 Boxer、Crafter、L200 的轴距、车顶、驾驶室和货斗分支。
2. 处理 Espace IV 2.0 dCi 跨 Phase II、Phase III 的外廓边界。
3. 闭合 Galaxy 2.0/140 与 S-Max 2.0/140 的 facelift 分支。
4. 继续处理 307 SW、Alfa 159 Sportwagon、Touareg 的高度配置分支。
5. 最后处理 Marcos、老款大众和 Daewoo 低资料覆盖车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/976040/ford_galaxy_1_8_tdci_100_trend.html?utm_source=chatgpt.com "2006 Ford Galaxy 1.8 TDCi (100) Trend (man. 5)"
[2]: https://www.auto-data.net/en/ford-s-max-2.5-i-20v-220hp-8120?utm_source=chatgpt.com "Ford S-MAX 2.5 i 20V (220 Hp) /Minivan 2006 - 2010"
[3]: https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-3.0-dci-v6-181hp-automatic-20280 "Renault Espace IV (Phase II, 2006) 3.0 dCi V6 (181 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 `19405` Peugeot 307 Break 1.6 HDI 90 的旅行版外廓，明确采用 `4432 × 1757 × 1544 mm`，宽度为不含后视镜口径。([汽车目录][1])
* 闭合 Alfa Romeo 159 Sportwagon 六个 Ktype。官方技术资料将标准外廓区分为 `1417 mm` 与 `1422 mm` 两种高度，本轮创建两个稳定尺寸组并按具体动力版本关联。
* 本轮新增 3 个尺寸组；未重复输出任何既有缓存尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：118
* READY 映射：82
* PENDING 映射：36
* 全部分支 READY 的 Ktype：64
* 部分 READY、部分 PENDING 的 Ktype：4
* 全部分支 PENDING 的 Ktype：32
* 已确认并被当前映射引用的尺寸组：52
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19405	19405	Wagon	Peugeot 307 I Break facelift		5	EU-PEUGEOT-307-I-FACELIFT-WAGON-01	HIGH	Break五门旅行外廓。	READY
19445	19445	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19446	19446	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	标准1422毫米高度分支。	READY
19447	19447	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	Q4标准1422毫米高度分支。	READY
19448	19448	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19449	19449	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19450	19450	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	标准1422毫米高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-307-I-FACELIFT-WAGON-01	4432	1757	1544	Automobile-Catalog Peugeot 307 Break 1.6 HDi 90	https://www.automobile-catalog.com/car/2006/2618015/peugeot_307_break_estate_1_6_hdi_90.html
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	4660	1828	1417	Alfa Romeo UK 159 and 159 Sportwagon Technical Data; Auto-Data Alfa Romeo 159 Sportwagon 1.9 JTS	https://allcarcentral.com/alfa_pdf/Alfa_Romeo_159_159_Sportwagon_2010_Technical_Specification.pdf;https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.9-jts-160hp-1530
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	4660	1828	1422	Alfa Romeo UK 159 and 159 Sportwagon Technical Data	https://allcarcentral.com/alfa_pdf/Alfa_Romeo_159_159_Sportwagon_2010_Technical_Specification.pdf
```

## 下一步优先处理

1. 批量闭合 Boxer、Crafter 和 L200 的轴距、车顶、驾驶室及货斗分支。
2. 拆分 Espace IV 2.0 dCi 的标准轴距、Grand 长轴及 Phase II–IV 改款边界。
3. 处理 Galaxy II、S-Max facelift 与 Touareg 的高度或宽度口径问题。
4. 最后处理 Marcos、Colt CZC Turbo、老款 Derby/Jetta/Golf I 和 Daewoo 系列。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/2618015/peugeot_307_break_estate_1_6_hdi_90.html?utm_source=chatgpt.com "2006 Peugeot 307 Break (Estate) 1.6 HDi FAP 90 Specs Review (66 kW / 90 PS / 89 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Colt CZC 1.5 与 Turbo 三维一致，纠正原尺寸组中带发动机含义的 `NA` 后缀，统一为中性的物理外廓尺寸组；`19363`、`19364` 共同引用新稳定 ID。([汽车目录][1])
* 闭合 Daewoo Leganza、Nubira J100/J150 轿车与旅行版、Rezzo 共 7 个 Ktype。Nubira 按代际和车身形式拆组，不按发动机重复建组。([汽车目录][2])
* 闭合 Volkswagen Jetta I 1.3、Golf I 1.6，以及 Ford S-Max facelift 的 2.0 汽油和 2.0 TDCi 140 分支。([汽车目录][3])
* 本轮共将 12 条映射由 `PENDING` 转为 `READY`；新增 8 个尺寸组，并修正 1 个尺寸组稳定 ID。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：118
* READY 映射：94
* PENDING 映射：24
* 全部分支 READY 的 Ktype：76
* 部分 READY、部分 PENDING 的 Ktype：2
* 全部分支 PENDING 的 Ktype：22
* 已确认并被当前映射引用的尺寸组：60
* 本轮首次创建/修正尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19363	19363	Convertible	Mitsubishi Colt VI CZC	Z36A	2	EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	HIGH	Z36A自然吸气版本。	READY
19364	19364	Convertible	Mitsubishi Colt VI CZC		2	EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	HIGH	Turbo与自然吸气版外廓一致。	READY
19382	19382	Sedan	Volkswagen Jetta I			EU-VOLKSWAGEN-JETTA-I-SEDAN-01	MEDIUM	输入未限定门数；门数不改变外廓三维。	READY
19419	19419	Hatchback	Volkswagen Golf I			EU-VOLKSWAGEN-GOLF-I-HATCHBACK-01	HIGH	输入未限定门数；门数不改变外廓三维。	READY
19429	19429	Sedan	Daewoo Leganza	V100	4	EU-DAEWOO-LEGANZA-V100-SEDAN-01	HIGH		READY
19430	19430	Sedan	Daewoo Nubira J150	J150	4	EU-DAEWOO-NUBIRA-J150-SEDAN-01	HIGH		READY
19431	19431	Wagon	Daewoo Nubira J150	J150	5	EU-DAEWOO-NUBIRA-J150-WAGON-01	HIGH		READY
19432	19432	Wagon	Daewoo Nubira J150	J150	5	EU-DAEWOO-NUBIRA-J150-WAGON-01	HIGH		READY
19433	19433	Sedan	Daewoo Nubira J150	J150	4	EU-DAEWOO-NUBIRA-J150-SEDAN-01	HIGH		READY
19434	19434	Wagon	Daewoo Nubira J100	J100	5	EU-DAEWOO-NUBIRA-J100-WAGON-01	MEDIUM	早期J100旅行版外廓。	READY
19435	19435	MPV	Daewoo Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
19441_facelift	19441	MPV	Ford S-Max I facelift		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19444_facelift	19444	MPV	Ford S-Max I facelift		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	3875	1695	1453	Automobile-Catalog Mitsubishi Colt CZC 1.5; Automobile-Catalog Mitsubishi Colt CZC Turbo	https://www.automobile-catalog.com/car/2008/1993535/mitsubishi_colt_czc_1_5.html;https://www.automobile-catalog.com/car/2007/1993550/mitsubishi_colt_czc_turbo.html
EU-VOLKSWAGEN-JETTA-I-SEDAN-01	4190	1610	1410	Automobile-Catalog 1983 Volkswagen Jetta 1300	https://www.automobile-catalog.com/car/1983/31940/volkswagen_jetta_1300.html
EU-VOLKSWAGEN-GOLF-I-HATCHBACK-01	3815	1610	1410	Volkswagen Newsroom Golf I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-DAEWOO-LEGANZA-V100-SEDAN-01	4671	1779	1437	Automobile-Catalog 2001 Daewoo Leganza 2.0 SX	https://www.automobile-catalog.com/car/2001/557255/daewoo_leganza_2_0_sx.html
EU-DAEWOO-NUBIRA-J150-SEDAN-01	4495	1700	1430	Automobile-Catalog 2000 Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/2000/556820/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-J150-WAGON-01	4550	1720	1430	Automobile-Catalog 2000 Daewoo Nubira 2.0 CDX Wagon; Automobile-Catalog 2001 Daewoo Nubira 1.6 SE Wagon	https://www.automobile-catalog.com/car/2000/556835/daewoo_nubira_2_0_cdx_wagon.html;https://www.automobile-catalog.com/car/2001/556850/daewoo_nubira_1_6_se_wagon.html
EU-DAEWOO-NUBIRA-J100-WAGON-01	4514	1700	1432	Automobile-Catalog 1998 Daewoo Nubira 2.0 CDX Wagon	https://www.automobile-catalog.com/car/1998/556625/daewoo_nubira_2_0_cdx_wagon.html
EU-DAEWOO-REZZO-KLAU-MPV-01	4350	1755	1580	Auto-Data Daewoo Rezzo KLAU 1.8	https://www.auto-data.net/en/daewoo-rezzo-klau-1.8-i-101hp-16287
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Automobile-Catalog 2013 Ford S-Max 2.0 TDCi 140 Titanium	https://www.automobile-catalog.com/car/2013/1234955/ford_s-max_2_0_tdci_140_titanium.html
```

## 下一步优先处理

1. 批量拆分 Boxer、Crafter、L200 的轴距、车顶、驾驶室和货斗分支。
2. 闭合 Espace IV 2.0 dCi 的 Phase II、Phase III 与标准轴距边界。
3. 处理 Galaxy II facelift、Touareg 悬架高度和 Berlingo Kasten/MPV 分支。
4. 最后处理 Marcos、Derby 及剩余低资料覆盖车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2007/1993550/mitsubishi_colt_czc_turbo.html?utm_source=chatgpt.com "2007 Mitsubishi Colt CZC Turbo Specs Review (110 kW ..."
[2]: https://www.automobile-catalog.com/car/2001/557255/daewoo_leganza_2_0_sx.html?utm_source=chatgpt.com "2001 Daewoo Leganza 2.0 SX Specs Review (93 kW ..."
[3]: https://www.automobile-catalog.com/car/1983/31940/volkswagen_jetta_1300.html?utm_source=chatgpt.com "1983 Volkswagen Jetta 1300 Specs Review (44 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* `19358`、`19359` 已确认同时覆盖标准轴距 Espace 与 Grand Espace，并跨越 2010 年外廓调整；各拆为标准轴距/长轴、调整前/调整后四个稳定分支。([Red Desguace][1])
* `19411` Berlingo 的 Kasten 与 Multispace 使用相同基础外壳三维，闭合为一个共享尺寸组。([汽车目录][2])
* `19455` Touareg 3.6 V6 FSI 已闭合；采用明确区分车身宽度与含镜宽度的规格，落盘宽度为不含后视镜的 `1928 mm`。([汽车数据网][3])
* 本轮新增 5 个尺寸组；Espace IV Phase II 标准轴距分支直接复用已有尺寸组，未重复输出。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：104
* PENDING 映射：20
* 全部分支 READY 的 Ktype：80
* 部分 READY、部分 PENDING 的 Ktype：2
* 全部分支 PENDING 的 Ktype：18
* 已确认并被当前映射引用的尺寸组：65
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19358_swb_phase2	19358	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	标准轴距，2010年外廓调整前。	READY
19358_swb_phase3plus	19358	MPV	Renault Espace IV Phase III-IV		5	EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	标准轴距，2010年外廓调整后。	READY
19358_lwb_phase2	19358	MPV	Renault Grand Espace IV Phase II		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	HIGH	Grand长轴，2010年外廓调整前。	READY
19358_lwb_phase3plus	19358	MPV	Renault Grand Espace IV Phase III-IV		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	Grand长轴，2010年外廓调整后。	READY
19359_swb_phase2	19359	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	标准轴距，2010年外廓调整前。	READY
19359_swb_phase3plus	19359	MPV	Renault Espace IV Phase III-IV		5	EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	标准轴距，2010年外廓调整后。	READY
19359_lwb_phase2	19359	MPV	Renault Grand Espace IV Phase II		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	HIGH	Grand长轴，2010年外廓调整前。	READY
19359_lwb_phase3plus	19359	MPV	Renault Grand Espace IV Phase III-IV		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	Grand长轴，2010年外廓调整后。	READY
19411	19411	Van/MPV	Citroën Berlingo I		5	EU-CITROEN-BERLINGO-I-VAN-MPV-01	MEDIUM	Kasten与Multispace共用基础外壳三维。	READY
19455	19455	SUV	Volkswagen Touareg I	7L	5	EU-VOLKSWAGEN-TOUAREG-I-7L-V6-FSI-SUV-01	HIGH	3.6 V6 FSI对应标准悬架外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	4856	1860	1746	Auto-Data Renault Grand Espace IV Phase II 2.0 dCi 150	https://www.auto-data.net/en/renault-grand-espace-iv-phase-ii-2006-2.0-dci-150hp-automatic-29842
EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	4661	1860	1728	Renault Espace 2011 UK brochure; VehicleScore Renault Espace dimensions	https://autocatalogarchive.com/wp-content/uploads/2023/04/Renault-Espace-2011-UK.pdf;https://vehiclescore.co.uk/car-dimensions-check/renault/espace
EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	4861	1860	1746	Renault Espace 2011 UK brochure; VehicleScore Renault Espace dimensions	https://autocatalogarchive.com/wp-content/uploads/2023/04/Renault-Espace-2011-UK.pdf;https://vehiclescore.co.uk/car-dimensions-check/renault/espace
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810	Automobile-Catalog Citroen Berlingo Multispace; Drive.Place Citroen Berlingo I facelift Van	https://www.automobile-catalog.com/car/2004/550190/citroen_berlingo_multispace_2_0_hdi.html;https://citroen.drive.place/berlingo/i_res/group_furgon/579315
EU-VOLKSWAGEN-TOUAREG-I-7L-V6-FSI-SUV-01	4754	1928	1726	Auto-Data Volkswagen Touareg I 3.6 FSI; Volkswagen UK Touareg press kit	https://www.auto-data.net/en/volkswagen-touareg-i-7l-3.6-fsi-280hp-4motion-8517;https://www.vwpress.co.uk/press-kits/150
```

## 下一步优先处理

1. 批量拆分 Crafter Bus、Kasten、Pritsche/Fahrgestell 的轴距与车顶分支。
2. 闭合 Peugeot Boxer Kasten 和底盘驾驶室的轴距、车顶配置。
3. 处理 Mitsubishi L200 的 Single Cab、Club Cab、Double Cab 外廓。
4. 解决 Galaxy II facelift、Marcos TSO、Volkswagen Derby 等剩余低覆盖车型。

推进信号：CONTINUE

[1]: https://www.reddesguace.com/pieza/renault/espace-iv-jk0/1111699_piloto-lateral-izquierdo-8200394722?utm_source=chatgpt.com "PILOTO LATERAL IZQUIERDO RENAULT ESPACE IV (JK0 ..."
[2]: https://www.automobile-catalog.com/car/2004/550190/citroen_berlingo_multispace_2_0_hdi.html?utm_source=chatgpt.com "2004 Citroen Berlingo Multispace 2.0 HDi (man. 5)"
[3]: https://www.auto-data.net/en/volkswagen-touareg-i-7l-3.6-fsi-280hp-4motion-8517?utm_source=chatgpt.com "Volkswagen Touareg I (7L) 3.6 FSI (280 Hp) 4MOTION"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Marcos TSO Convertible 与 TSO GT2。两种车身三维均为 `4020 × 1680 × 1150 mm`，但敞篷与封闭式 Coupe 属于不同物理车身，分别建组。([汽车目录][1])
* 闭合 Volkswagen Derby 86C 1.3，确认两门轿车外廓为 `3975 × 1580 × 1355 mm`。([汽车数据网][2])
* 闭合 Ford Galaxy II facelift 的 2.0 汽油与 2.0 TDCi 140 分支，共用改款后 MPV 尺寸组。改款后规格为 `4819 × 1884 × 1758 mm`。([Auto ABC][3])
* 本轮新增 4 个尺寸组，未重复输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：124
* READY 映射：109
* PENDING 映射：15
* 全部分支 READY 的 Ktype：85
* 部分 READY、部分 PENDING 的 Ktype：0
* 全部分支 PENDING 的 Ktype：15
* 已确认并被当前映射引用的尺寸组：69
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19369	19369	Convertible	Marcos TSO		2	EU-MARCOS-TSO-CONVERTIBLE-01	HIGH	敞篷物理车身。	READY
19372	19372	Coupe	Marcos TSO GT2		3	EU-MARCOS-TSO-GT2-COUPE-01	HIGH	GT2封闭式车身。	READY
19375	19375	Sedan	Volkswagen Derby 86C	86C	2	EU-VOLKSWAGEN-DERBY-86C-SEDAN-01	HIGH		READY
19437_facelift	19437	MPV	Ford Galaxy II facelift		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19440_facelift	19440	MPV	Ford Galaxy II facelift		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MARCOS-TSO-CONVERTIBLE-01	4020	1680	1150	Automobile-Catalog 2004 Marcos TSO	https://www.automobile-catalog.com/car/2004/1442630/marcos_tso.html
EU-MARCOS-TSO-GT2-COUPE-01	4020	1680	1150	Automobile-Catalog 2005 Marcos TSO GT2	https://www.automobile-catalog.com/car/2005/1442660/marcos_tso_gt2.html
EU-VOLKSWAGEN-DERBY-86C-SEDAN-01	3975	1580	1355	Auto-Data Volkswagen Derby 86C 1.3	https://www.auto-data.net/en/volkswagen-derby-86c-1.3-60hp-8341
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758	Automobile-Catalog 2011 Ford Galaxy 2.0 TDCi 140 Titanium	https://www.automobile-catalog.com/car/2011/1234670/ford_galaxy_2_0_tdci_140_titanium.html
```

## 下一步优先处理

1. 集中拆分 12 个 Crafter Bus、Kasten、Pritsche/Fahrgestell Ktype 的轴距、车顶及驾驶室分支。
2. 闭合 Peugeot Boxer Kasten 与底盘驾驶室的长度、车顶和轴距分支。
3. 最后拆分 Mitsubishi L200 的 Single Cab、Club Cab、Double Cab、宽体配置及 facelift 外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2004/1442630/marcos_tso.html?utm_source=chatgpt.com "2004 Marcos TSO Specs Review (261 kW / 355 PS / 350 hp) (since mid-year 2004 for Europe )"
[2]: https://www.auto-data.net/en/volkswagen-derby-86c-1.3-60hp-8341 "Volkswagen Derby (86C) 1.3 (60 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-abc.eu/ford-galaxy/g397-2010?utm_source=chatgpt.com "Ford Galaxy 2010 (2010 - 2015) reviews, technical data, ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: Playwright browser 请求失败 (eval): {"ok":false,"error":"locator.waitFor: Timeout 20000ms exceeded.\nCall log:\n\u001b[2m  - waiting for locator('body')\u001b[22m\n\n    at runAction (D:\\Licheng\\Repo\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:167:32)\n    at async Server. (D:\\Licheng\\Repo\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:207:16)"}


--- 发送 / checkpoint 续跑到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
## 更新点

* `19342` Peugeot Boxer Kasten 已按官方外廓表拆为短轴、中轴、长轴及三种车顶组合，共 7 个物理分支。官方手册分别列明每个厢式车配置的长宽高。
* `19406`–`19409` Crafter Bus 已按中轴高顶、长轴高顶拆分；四个发动机 Ktype 复用两个尺寸组。
* `19415`–`19418` Crafter Pritsche/Fahrgestell 已按中轴/长轴、单排/双排、SRW/DRW 拆分；四个发动机 Ktype 复用六个尺寸组。官方尺寸图明确区分单后轮和双后轮的长度及高度，并给出不含后视镜车身宽度。([AutoSynergy][1])
* 仅剩 `19343` Boxer Pritsche/Fahrgestell。官方资料的底盘车高度为 `2100–2125 mm` 或“取决于改装车身”，无法按要求落盘单一高度，因此本轮不创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：214
* READY 映射：213
* PENDING 映射：1
* 全部分支 READY 的 Ktype：99
* 全部分支 PENDING 的 Ktype：1
* 已确认并被当前映射引用的尺寸组：101
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19342_swb_lowroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶外廓。	READY
19342_swb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19342_mwb_lowroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶外廓。	READY
19342_mwb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶外廓。	READY
19342_mwb_superhighroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶外廓。	READY
19342_lwb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
19342_lwb_superhighroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶外廓。	READY
19406_mwb_highroof	19406	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19406_lwb_highroof	19406	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19407_mwb_highroof	19407	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19407_lwb_highroof	19407	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19408_mwb_highroof	19408	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19408_lwb_highroof	19408	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19409_mwb_highroof	19409	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19409_lwb_highroof	19409	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19415_mwb_chassis_srw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19415_mwb_chassis_drw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19415_lwb_chassis_srw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19415_lwb_chassis_drw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19415_lwb_doublecab_srw	19415	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19415_lwb_doublecab_drw	19415	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19416_mwb_chassis_srw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19416_mwb_chassis_drw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19416_lwb_chassis_srw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19416_lwb_chassis_drw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19416_lwb_doublecab_srw	19416	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19416_lwb_doublecab_drw	19416	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19417_mwb_chassis_srw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19417_mwb_chassis_drw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19417_lwb_chassis_srw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19417_lwb_chassis_drw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19417_lwb_doublecab_srw	19417	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19417_lwb_doublecab_drw	19417	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19418_mwb_chassis_srw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19418_mwb_chassis_drw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19418_lwb_chassis_srw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19418_lwb_chassis_drw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19418_lwb_doublecab_srw	19418	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19418_lwb_doublecab_drw	19418	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	4749	2024	2515	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	5599	2024	2505	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	5905	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	6940	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	5865	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	6082	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	6675	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	6842	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	6675	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	6842	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
```

## 下一步优先处理

1. 仅处理 `19343` Peugeot Boxer Pritsche/Fahrgestell。
2. 按平台车、单排底盘、双排底盘和轴距分支，寻找能够把 `2100–2125 mm` 高度范围落实到具体配置的直接资料。
3. 闭合后立即进行一次机械检查，并输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf "Layout 1"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / checkpoint 续跑 ---
## 更新点

* `19343` 已拆分并闭合为中轴/长轴低地板驾驶室、单排底盘驾驶室、单排平台车和双排平台车 6 个物理分支；官方资料确认中轴、长轴底盘边界，精确 146 hp 规格页补齐对应三维。([Dezo's Garage][1])
* 将 `19411` 的混合车身标准化为 `Van` 与 `MPV` 两条映射，共用同一尺寸组。
* 已完成机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，无孤立尺寸组，三维和来源字段完整。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：220
* PENDING 映射：0
* DIMENSION_GROUP：107
* 所有映射均为 `READY`。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19341	19341	Hatchback	Peugeot 307 I facelift			EU-PEUGEOT-307-I-FACELIFT-HATCHBACK-01	HIGH	掀背外廓；门数不构成尺寸分支。	READY
19342_swb_lowroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶外廓。	READY
19342_swb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19342_mwb_lowroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶外廓。	READY
19342_mwb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶外廓。	READY
19342_mwb_superhighroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶外廓。	READY
19342_lwb_highroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
19342_lwb_superhighroof	19342	Van	Peugeot Boxer I Typ 244	244		EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶外廓。	READY
19343_mwb_floorcab	19343	Pickup	Peugeot Boxer I Typ 244	244	2	EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-MWB-01	HIGH	中轴低地板驾驶室。	READY
19343_lwb_floorcab	19343	Pickup	Peugeot Boxer I Typ 244	244	2	EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-LWB-01	HIGH	长轴低地板驾驶室。	READY
19343_mwb_chassis	19343	Pickup	Peugeot Boxer I Typ 244	244	2	EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19343_lwb_chassis	19343	Pickup	Peugeot Boxer I Typ 244	244	2	EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19343_lwb_platform	19343	Pickup	Peugeot Boxer I Typ 244	244	2	EU-PEUGEOT-BOXER-I-244-PLATFORM-CAB-LWB-01	HIGH	长轴单排平台车。	READY
19343_lwb_doublecab	19343	Pickup	Peugeot Boxer I Typ 244	244	4	EU-PEUGEOT-BOXER-I-244-PLATFORM-DOUBLE-CAB-LWB-01	HIGH	长轴双排平台车。	READY
19344_prefl	19344	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH	2009改款前外廓。	READY
19344_facelift	19344	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19345_prefl	19345	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH	2009改款前外廓。	READY
19345_facelift	19345	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19346	19346	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH		READY
19347	19347	SUV	Mercedes-Benz GL-Class X164	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	HIGH		READY
19349_prefl	19349	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19349_facelift	19349	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19350_prefl	19350	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19350_facelift	19350	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19351_prefl	19351	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19351_facelift	19351	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19352_prefl	19352	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19352_facelift	19352	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19353_prefl	19353	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19353_facelift	19353	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；三/五门外廓一致。	READY
19354_prefl	19354	Hatchback	Peugeot 207 I			EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	HIGH	2009改款前；三/五门外廓一致。	READY
19354_facelift	19354	Hatchback	Peugeot 207 I facelift			EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	MEDIUM	2009改款后；含207+延续外廓。	READY
19355	19355	Hatchback	Renault Clio III Phase I		3	EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	HIGH	RS三门外廓。	READY
19356	19356	Hatchback	Renault Laguna II facelift		5	EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	HIGH		READY
19357	19357	Wagon	Renault Laguna II Grandtour facelift		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	HIGH		READY
19358_swb_phase2	19358	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	标准轴距，2010年外廓调整前。	READY
19358_swb_phase3plus	19358	MPV	Renault Espace IV Phase III-IV		5	EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	标准轴距，2010年外廓调整后。	READY
19358_lwb_phase2	19358	MPV	Renault Grand Espace IV Phase II		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	HIGH	Grand长轴，2010年外廓调整前。	READY
19358_lwb_phase3plus	19358	MPV	Renault Grand Espace IV Phase III-IV		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	Grand长轴，2010年外廓调整后。	READY
19359_swb_phase2	19359	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	标准轴距，2010年外廓调整前。	READY
19359_swb_phase3plus	19359	MPV	Renault Espace IV Phase III-IV		5	EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	标准轴距，2010年外廓调整后。	READY
19359_lwb_phase2	19359	MPV	Renault Grand Espace IV Phase II		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	HIGH	Grand长轴，2010年外廓调整前。	READY
19359_lwb_phase3plus	19359	MPV	Renault Grand Espace IV Phase III-IV		5	EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	HIGH	Grand长轴，2010年外廓调整后。	READY
19360	19360	MPV	Renault Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	3.0 dCi 181仅对应Phase II标准轴距外廓。	READY
19361	19361	Hatchback	Opel Signum facelift		5	EU-OPEL-SIGNUM-I-FACELIFT-HATCHBACK-01	HIGH		READY
19362	19362	Convertible	Opel Astra H TwinTop		2	EU-OPEL-ASTRA-H-TWINTOP-CONVERTIBLE-01	HIGH		READY
19363	19363	Convertible	Mitsubishi Colt VI CZC	Z36A	2	EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	HIGH	Z36A自然吸气版本。	READY
19364	19364	Convertible	Mitsubishi Colt VI CZC		2	EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	HIGH	Turbo版本物理外廓。	READY
19365	19365	Pickup	Mitsubishi L200 IV	KB4T	4	EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	HIGH	KB4T双排长货斗外廓。	READY
19366	19366	Sedan	Mitsubishi Lancer Evolution IX		4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-01	HIGH	标准280 hp外廓。	READY
19367	19367	Sedan	Lancia Thesis		4	EU-LANCIA-THESIS-I-SEDAN-01	HIGH		READY
19368_prefl	19368	Sedan	Dacia Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	HIGH	2008改款前外廓。	READY
19368_facelift	19368	Sedan	Dacia Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	HIGH	2008改款后外廓。	READY
19369	19369	Convertible	Marcos TSO		2	EU-MARCOS-TSO-CONVERTIBLE-01	HIGH	敞篷物理车身。	READY
19371_prefl	19371	Convertible	Saab 9-3 Convertible II		2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH	2007改款前外廓。	READY
19371_facelift	19371	Convertible	Saab 9-3 Convertible II facelift		2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	HIGH	2007改款后外廓。	READY
19372	19372	Coupe	Marcos TSO GT2		3	EU-MARCOS-TSO-GT2-COUPE-01	HIGH	GT2封闭式车身。	READY
19374	19374	Sedan	Saab 9-5 facelift 2005		4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH		READY
19375	19375	Sedan	Volkswagen Derby 86C	86C	2	EU-VOLKSWAGEN-DERBY-86C-SEDAN-01	HIGH		READY
19376	19376	Wagon	Saab 9-5 Sport Combi facelift 2005		5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH		READY
19378	19378	Coupe	Lotus Exige Series 2		2	EU-LOTUS-EXIGE-S2-S-COUPE-01	HIGH	Exige S量产外廓。	READY
19379	19379	Coupe	Lamborghini Murciélago LP 640		2	EU-LAMBORGHINI-MURCIELAGO-LP640-COUPE-01	HIGH		READY
19380	19380	Convertible	Lamborghini Gallardo Spyder		2	EU-LAMBORGHINI-GALLARDO-SPYDER-CONVERTIBLE-01	HIGH		READY
19382	19382	Sedan	Volkswagen Jetta I			EU-VOLKSWAGEN-JETTA-I-SEDAN-01	MEDIUM	输入未限定门数；门数不改变外廓三维。	READY
19383	19383	Hatchback	Volkswagen Golf II			EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-01	HIGH	三/五门外廓一致。	READY
19387_prefl	19387	Sedan	Peugeot 407 I		4	EU-PEUGEOT-407-I-SEDAN-PREFL-01	HIGH	2008改款前外廓。	READY
19387_facelift	19387	Sedan	Peugeot 407 I facelift		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH	2008改款后外廓。	READY
19388_prefl	19388	Wagon	Peugeot 407 SW		5	EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	HIGH	2008改款前外廓。	READY
19388_facelift	19388	Wagon	Peugeot 407 SW facelift		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH	2008改款后外廓。	READY
19389	19389	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19390	19390	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19391	19391	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19392	19392	Convertible	Mercedes-Benz SL R230 facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	HIGH		READY
19393	19393	SUV	Suzuki Grand Vitara II		5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	HIGH	五门封闭式车身。	READY
19395	19395	Sedan	Volkswagen Passat B6	3C2	4	EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	HIGH		READY
19396	19396	Wagon	Volkswagen Passat Variant B6	3C5	5	EU-VOLKSWAGEN-PASSAT-B6-VARIANT-WAGON-01	HIGH		READY
19397	19397	Convertible	Renault Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	HIGH		READY
19398	19398	Hatchback	Renault Megane II Phase II			EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	HIGH	三/五门外廓一致。	READY
19399	19399	Wagon	Renault Megane II Grandtour Phase II		5	EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	HIGH		READY
19400	19400	Convertible	Renault Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	HIGH		READY
19401_phase1	19401	MPV	Renault Scenic II Phase I		5	EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	HIGH	2006改款前外廓。	READY
19401_phase2	19401	MPV	Renault Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	HIGH	2006改款后外廓。	READY
19402	19402	Wagon	Volvo V70 II facelift		5	EU-VOLVO-V70-II-FACELIFT-WAGON-01	HIGH	前驱外廓。	READY
19403	19403	Wagon	Volvo V70 II facelift		5	EU-VOLVO-V70-II-FACELIFT-WAGON-AWD-01	HIGH	AWD高度分支。	READY
19404	19404	Wagon	Volvo XC70 I facelift		5	EU-VOLVO-XC70-I-FACELIFT-WAGON-01	HIGH		READY
19405	19405	Wagon	Peugeot 307 I Break facelift		5	EU-PEUGEOT-307-I-FACELIFT-WAGON-01	HIGH	Break五门旅行外廓。	READY
19406_mwb_highroof	19406	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19406_lwb_highroof	19406	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19407_mwb_highroof	19407	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19407_lwb_highroof	19407	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19408_mwb_highroof	19408	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19408_lwb_highroof	19408	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19409_mwb_highroof	19409	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19409_lwb_highroof	19409	MPV	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19410_swb_lowroof	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
19410_swb_highroof	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19410_mwb_lowroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-SRW-01	HIGH	中轴低顶单后轮外廓。	READY
19410_mwb_lowroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-DRW-01	HIGH	中轴低顶双后轮外廓。	READY
19410_mwb_highroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-SRW-01	HIGH	中轴高顶单后轮外廓。	READY
19410_mwb_highroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-DRW-01	HIGH	中轴高顶双后轮外廓。	READY
19410_mwb_superhighroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-SRW-01	HIGH	中轴超高顶单后轮外廓。	READY
19410_mwb_superhighroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-DRW-01	HIGH	中轴超高顶双后轮外廓。	READY
19410_lwb_highroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-SRW-01	HIGH	长轴高顶单后轮外廓。	READY
19410_lwb_highroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-DRW-01	HIGH	长轴高顶双后轮外廓。	READY
19410_lwb_superhighroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-SRW-01	HIGH	长轴超高顶单后轮外廓。	READY
19410_lwb_superhighroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-DRW-01	HIGH	长轴超高顶双后轮外廓。	READY
19410_lwbmaxi_highroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-SRW-01	HIGH	加长轴高顶单后轮外廓。	READY
19410_lwbmaxi_highroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-DRW-01	HIGH	加长轴高顶双后轮外廓。	READY
19410_lwbmaxi_superhighroof_srw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-SRW-01	HIGH	加长轴超高顶单后轮外廓。	READY
19410_lwbmaxi_superhighroof_drw	19410	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-DRW-01	HIGH	加长轴超高顶双后轮外廓。	READY
19411_van	19411	Van	Citroën Berlingo I			EU-CITROEN-BERLINGO-I-VAN-MPV-01	MEDIUM	Kasten分支。	READY
19411_mpv	19411	MPV	Citroën Berlingo I		5	EU-CITROEN-BERLINGO-I-VAN-MPV-01	MEDIUM	Großraumlimousine分支。	READY
19412_swb_lowroof	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
19412_swb_highroof	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19412_mwb_lowroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-SRW-01	HIGH	中轴低顶单后轮外廓。	READY
19412_mwb_lowroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-DRW-01	HIGH	中轴低顶双后轮外廓。	READY
19412_mwb_highroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-SRW-01	HIGH	中轴高顶单后轮外廓。	READY
19412_mwb_highroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-DRW-01	HIGH	中轴高顶双后轮外廓。	READY
19412_mwb_superhighroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-SRW-01	HIGH	中轴超高顶单后轮外廓。	READY
19412_mwb_superhighroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-DRW-01	HIGH	中轴超高顶双后轮外廓。	READY
19412_lwb_highroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-SRW-01	HIGH	长轴高顶单后轮外廓。	READY
19412_lwb_highroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-DRW-01	HIGH	长轴高顶双后轮外廓。	READY
19412_lwb_superhighroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-SRW-01	HIGH	长轴超高顶单后轮外廓。	READY
19412_lwb_superhighroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-DRW-01	HIGH	长轴超高顶双后轮外廓。	READY
19412_lwbmaxi_highroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-SRW-01	HIGH	加长轴高顶单后轮外廓。	READY
19412_lwbmaxi_highroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-DRW-01	HIGH	加长轴高顶双后轮外廓。	READY
19412_lwbmaxi_superhighroof_srw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-SRW-01	HIGH	加长轴超高顶单后轮外廓。	READY
19412_lwbmaxi_superhighroof_drw	19412	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-DRW-01	HIGH	加长轴超高顶双后轮外廓。	READY
19413_swb_lowroof	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
19413_swb_highroof	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19413_mwb_lowroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-SRW-01	HIGH	中轴低顶单后轮外廓。	READY
19413_mwb_lowroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-DRW-01	HIGH	中轴低顶双后轮外廓。	READY
19413_mwb_highroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-SRW-01	HIGH	中轴高顶单后轮外廓。	READY
19413_mwb_highroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-DRW-01	HIGH	中轴高顶双后轮外廓。	READY
19413_mwb_superhighroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-SRW-01	HIGH	中轴超高顶单后轮外廓。	READY
19413_mwb_superhighroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-DRW-01	HIGH	中轴超高顶双后轮外廓。	READY
19413_lwb_highroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-SRW-01	HIGH	长轴高顶单后轮外廓。	READY
19413_lwb_highroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-DRW-01	HIGH	长轴高顶双后轮外廓。	READY
19413_lwb_superhighroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-SRW-01	HIGH	长轴超高顶单后轮外廓。	READY
19413_lwb_superhighroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-DRW-01	HIGH	长轴超高顶双后轮外廓。	READY
19413_lwbmaxi_highroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-SRW-01	HIGH	加长轴高顶单后轮外廓。	READY
19413_lwbmaxi_highroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-DRW-01	HIGH	加长轴高顶双后轮外廓。	READY
19413_lwbmaxi_superhighroof_srw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-SRW-01	HIGH	加长轴超高顶单后轮外廓。	READY
19413_lwbmaxi_superhighroof_drw	19413	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-DRW-01	HIGH	加长轴超高顶双后轮外廓。	READY
19414_swb_lowroof	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-LOWROOF-01	HIGH	短轴低顶外廓。	READY
19414_swb_highroof	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶外廓。	READY
19414_mwb_lowroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-SRW-01	HIGH	中轴低顶单后轮外廓。	READY
19414_mwb_lowroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-DRW-01	HIGH	中轴低顶双后轮外廓。	READY
19414_mwb_highroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-SRW-01	HIGH	中轴高顶单后轮外廓。	READY
19414_mwb_highroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-DRW-01	HIGH	中轴高顶双后轮外廓。	READY
19414_mwb_superhighroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-SRW-01	HIGH	中轴超高顶单后轮外廓。	READY
19414_mwb_superhighroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-DRW-01	HIGH	中轴超高顶双后轮外廓。	READY
19414_lwb_highroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-SRW-01	HIGH	长轴高顶单后轮外廓。	READY
19414_lwb_highroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-DRW-01	HIGH	长轴高顶双后轮外廓。	READY
19414_lwb_superhighroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-SRW-01	HIGH	长轴超高顶单后轮外廓。	READY
19414_lwb_superhighroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-DRW-01	HIGH	长轴超高顶双后轮外廓。	READY
19414_lwbmaxi_highroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-SRW-01	HIGH	加长轴高顶单后轮外廓。	READY
19414_lwbmaxi_highroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-DRW-01	HIGH	加长轴高顶双后轮外廓。	READY
19414_lwbmaxi_superhighroof_srw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-SRW-01	HIGH	加长轴超高顶单后轮外廓。	READY
19414_lwbmaxi_superhighroof_drw	19414	Van	Volkswagen Crafter I	2E		EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-DRW-01	HIGH	加长轴超高顶双后轮外廓。	READY
19415_mwb_chassis_srw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19415_mwb_chassis_drw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19415_lwb_chassis_srw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19415_lwb_chassis_drw	19415	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19415_lwb_doublecab_srw	19415	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19415_lwb_doublecab_drw	19415	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19416_mwb_chassis_srw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19416_mwb_chassis_drw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19416_lwb_chassis_srw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19416_lwb_chassis_drw	19416	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19416_lwb_doublecab_srw	19416	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19416_lwb_doublecab_drw	19416	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19417_mwb_chassis_srw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19417_mwb_chassis_drw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19417_lwb_chassis_srw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19417_lwb_chassis_drw	19417	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19417_lwb_doublecab_srw	19417	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19417_lwb_doublecab_drw	19417	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19418_mwb_chassis_srw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	HIGH	中轴单排单后轮底盘。	READY
19418_mwb_chassis_drw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	HIGH	中轴单排双后轮底盘。	READY
19418_lwb_chassis_srw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	HIGH	长轴单排单后轮底盘。	READY
19418_lwb_chassis_drw	19418	Pickup	Volkswagen Crafter I	2E	2	EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	HIGH	长轴单排双后轮底盘。	READY
19418_lwb_doublecab_srw	19418	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	HIGH	长轴双排单后轮底盘。	READY
19418_lwb_doublecab_drw	19418	Pickup	Volkswagen Crafter I	2E	4	EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	HIGH	长轴双排双后轮底盘。	READY
19419	19419	Hatchback	Volkswagen Golf I			EU-VOLKSWAGEN-GOLF-I-HATCHBACK-01	HIGH	输入未限定门数；门数不改变外廓三维。	READY
19427	19427	Hatchback	Opel Astra H	L48	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	L48五门物理外廓。	READY
19428_prefl	19428	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	改款前三门外廓。	READY
19428_facelift	19428	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门外廓。	READY
19429	19429	Sedan	Daewoo Leganza	V100	4	EU-DAEWOO-LEGANZA-V100-SEDAN-01	HIGH		READY
19430	19430	Sedan	Daewoo Nubira J150	J150	4	EU-DAEWOO-NUBIRA-J150-SEDAN-01	HIGH		READY
19431	19431	Wagon	Daewoo Nubira J150	J150	5	EU-DAEWOO-NUBIRA-J150-WAGON-01	HIGH		READY
19432	19432	Wagon	Daewoo Nubira J150	J150	5	EU-DAEWOO-NUBIRA-J150-WAGON-01	HIGH		READY
19433	19433	Sedan	Daewoo Nubira J150	J150	4	EU-DAEWOO-NUBIRA-J150-SEDAN-01	HIGH		READY
19434	19434	Wagon	Daewoo Nubira J100	J100	5	EU-DAEWOO-NUBIRA-J100-WAGON-01	MEDIUM	早期J100旅行版外廓。	READY
19435	19435	MPV	Daewoo Rezzo	KLAU	5	EU-DAEWOO-REZZO-KLAU-MPV-01	HIGH		READY
19436	19436	Wagon	Saab 9-5 Sport Combi facelift 2005		5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH		READY
19437_prefl	19437	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19437_facelift	19437	MPV	Ford Galaxy II facelift		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19438	19438	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	1.8 TDCi 100仅对应改款前外廓。	READY
19439	19439	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2.0 TDCi 130仅对应改款前外廓。	READY
19440_prefl	19440	MPV	Ford Galaxy II		5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19440_facelift	19440	MPV	Ford Galaxy II facelift		5	EU-FORD-GALAXY-II-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19441_prefl	19441	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19441_facelift	19441	MPV	Ford S-Max I facelift		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19442	19442	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2.5 ST 220仅对应改款前外廓。	READY
19443	19443	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2.0 TDCi 130仅对应改款前外廓。	READY
19444_prefl	19444	MPV	Ford S-Max I		5	EU-FORD-S-MAX-I-MPV-PREFL-01	HIGH	2010改款前外廓。	READY
19444_facelift	19444	MPV	Ford S-Max I facelift		5	EU-FORD-S-MAX-I-FACELIFT-MPV-01	HIGH	2010改款后外廓。	READY
19445	19445	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19446	19446	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	标准1422毫米高度分支。	READY
19447	19447	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	Q4标准1422毫米高度分支。	READY
19448	19448	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19449	19449	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	HIGH	标准16英寸配置外廓。	READY
19450	19450	Wagon	Alfa Romeo 159 Sportwagon		5	EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	HIGH	标准1422毫米高度分支。	READY
19451	19451	SUV	Porsche Cayenne 955	955	5	EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	HIGH	Turbo S专属外廓。	READY
19452	19452	Coupe	Porsche 911 Turbo 997	997	2	EU-PORSCHE-911-997-TURBO-COUPE-01	HIGH	Turbo宽体外廓。	READY
19453	19453	Coupe	Audi TT 8J	8J	2	EU-AUDI-TT-8J-COUPE-01	HIGH		READY
19454	19454	Coupe	Audi TT 8J	8J	2	EU-AUDI-TT-8J-COUPE-01	HIGH		READY
19455	19455	SUV	Volkswagen Touareg I	7L	5	EU-VOLKSWAGEN-TOUAREG-I-7L-V6-FSI-SUV-01	HIGH	3.6 V6 FSI对应标准悬架外廓。	READY
19456	19456	Sedan	Audi S6 C6	4F	4	EU-AUDI-S6-C6-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_201-300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-307-I-FACELIFT-HATCHBACK-01	4212	1746	1510	Auto-Data Peugeot 307 facelift 1.6 HDi 90	https://www.auto-data.net/en/peugeot-307-facelift-2005-1.6-hdi-90hp-5274
EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	4749	2024	2150	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	4749	2024	2515	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	5099	2024	2150	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	5099	2024	2505	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	5599	2024	2505	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870	Peugeot Boxer official owner's manual	https://www.autojm.fr/pdf/notices/PEUGEOT/boxer.pdf
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-MWB-01	4990	2020	2150	AutoScout24 Peugeot Boxer PC 350 M 2.8 HDi 146	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-pc-350-m-2-8-hdi-146-utilitaire-diesel-2461/
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-LWB-01	5490	2020	2150	AutoScout24 Peugeot Boxer PC 350 L 2.8 HDi 146	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-pc-350-l-2-8-hdi-146-utilitaire-diesel-2461/
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-MWB-01	5006	2020	2150	Peugeot Boxer 2004 official UK brochure; AutoScout24 Peugeot Boxer CC 350 M 2.8 HDi 146	https://xr793.com/wp-content/uploads/2022/12/2004-Peugeot-Vans-UK.pdf;https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-cc-350-m-2-8-hdi-146-autres-diesel-2459/
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-LWB-01	5506	2020	2150	Peugeot Boxer 2004 official UK brochure; AutoScout24 Peugeot Boxer CC 350 L 2.8 HDi 146	https://xr793.com/wp-content/uploads/2022/12/2004-Peugeot-Vans-UK.pdf;https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-cc-350-l-2-8-hdi-146-autres-diesel-2459/
EU-PEUGEOT-BOXER-I-244-PLATFORM-CAB-LWB-01	5680	2020	2150	AutoScout24 Peugeot Boxer PLC 350 L 2.8 HDi 146	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-plc-350-l-2-8-hdi-146-utilitaire-diesel-2462/
EU-PEUGEOT-BOXER-I-244-PLATFORM-DOUBLE-CAB-LWB-01	5710	2020	2150	AutoScout24 Peugeot Boxer PLDC 350 L 2.8 HDi 146	https://www.autoscout24.fr/voiture/caracteristiques-techniques/peugeot/boxer/boxer-pldc-350-l-2-8-hdi-146-utilitaire-diesel-2463/
EU-MERCEDES-BENZ-GL-X164-SUV-PREFL-01	5088	1920	1840	Auto-Data Mercedes-Benz GL X164 generation	https://www.auto-data.net/en/mercedes-benz-gl-x164-generation-3865
EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	5099	1920	1840	Auto-Data Mercedes-Benz GL model	https://www.auto-data.net/en/mercedes-benz-gl-model-1369
EU-PEUGEOT-207-I-HATCHBACK-PREFL-01	4030	1720	1472	Auto-Data Peugeot 207 1.6 16V 110	https://www.auto-data.net/en/peugeot-207-1.6-i-16v-110hp-5355
EU-PEUGEOT-207-I-HATCHBACK-FACELIFT-01	4045	1748	1472	Auto-Data Peugeot 207 facelift 1.4 HDi 68	https://www.auto-data.net/en/peugeot-207-facelift-2009-1.4-hdi-68hp-33973
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477	Auto-Data Renault Clio III Phase I RS 197	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-rs-2.0-16v-197hp-25037
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429	Auto-Data Renault Laguna II generation	https://www.auto-data.net/en/renault-laguna-ii-generation-2120
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443	Auto-Data Renault Laguna model	https://www.auto-data.net/en/renault-laguna-model-1016
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	4656	1860	1728	Auto-Data Renault Espace IV Phase II 3.0 dCi V6 181	https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-3.0-dci-v6-181hp-automatic-20280
EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	4661	1860	1728	Renault Espace 2011 UK brochure; VehicleScore Renault Espace dimensions	https://autocatalogarchive.com/wp-content/uploads/2023/04/Renault-Espace-2011-UK.pdf;https://vehiclescore.co.uk/car-dimensions-check/renault/espace
EU-RENAULT-GRAND-ESPACE-IV-PHASE-II-MPV-01	4856	1860	1746	Auto-Data Renault Grand Espace IV Phase II 2.0 dCi 150	https://www.auto-data.net/en/renault-grand-espace-iv-phase-ii-2006-2.0-dci-150hp-automatic-29842
EU-RENAULT-GRAND-ESPACE-IV-PHASE-III-IV-MPV-01	4861	1860	1746	Renault Espace 2011 UK brochure; VehicleScore Renault Espace dimensions	https://autocatalogarchive.com/wp-content/uploads/2023/04/Renault-Espace-2011-UK.pdf;https://vehiclescore.co.uk/car-dimensions-check/renault/espace
EU-OPEL-SIGNUM-I-FACELIFT-HATCHBACK-01	4651	1798	1466	Auto-Data Opel Signum facelift 1.8 140	https://www.auto-data.net/en/opel-signum-facelift-2005-1.8i-16v-140hp-2577
EU-OPEL-ASTRA-H-TWINTOP-CONVERTIBLE-01	4476	1759	1411	Auto-Data Opel Astra H TwinTop 1.8 140	https://www.auto-data.net/en/opel-astra-h-twintop-1.8i-16v-ecotec-140hp-2387
EU-MITSUBISHI-COLT-VI-CZC-CONVERTIBLE-01	3875	1695	1453	Automobile-Catalog Mitsubishi Colt CZC 1.5; Automobile-Catalog Mitsubishi Colt CZC Turbo	https://www.automobile-catalog.com/car/2008/1993535/mitsubishi_colt_czc_1_5.html;https://www.automobile-catalog.com/car/2007/1993550/mitsubishi_colt_czc_turbo.html
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775	Mitsubishi L200 official UK brochure	https://blog.le-parnass.com/catalogue_pdf/mitsubishi_l200.pdf
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-01	4490	1770	1450	Auto-Data Mitsubishi Lancer Evolution IX 280	https://www.auto-data.net/en/mitsubishi-lancer-evolution-ix-2.0-mivec-280hp-4wd-15649
EU-LANCIA-THESIS-I-SEDAN-01	4888	1830	1465	Auto-Data Lancia Thesis 2.4 Multijet 185	https://www.auto-data.net/en/lancia-thesis-2.4-multijet-20v-185hp-comfortronic-45951
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534	Auto-Data Dacia Logan I 1.6 16V 105	https://www.auto-data.net/ro/dacia-logan-i-1.6-16v-105hp-43234
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1534	Auto-Data Dacia Logan model	https://www.auto-data.net/ro/dacia-logan-model-1791
EU-MARCOS-TSO-CONVERTIBLE-01	4020	1680	1150	Automobile-Catalog 2004 Marcos TSO	https://www.automobile-catalog.com/car/2004/1442630/marcos_tso.html
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data Saab 9-3 Convertible II	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.0-t-150hp-11947
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437	Auto-Data Saab 9-3 Convertible II facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-3-convertible-ii-facelift-2007-1.9-tid-150hp-54589
EU-MARCOS-TSO-GT2-COUPE-01	4020	1680	1150	Automobile-Catalog 2005 Marcos TSO GT2	https://www.automobile-catalog.com/car/2005/1442660/marcos_tso_gt2.html
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data Saab 9-5 facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-5-facelift-2005-1.9-tid-150hp-automatic-42738
EU-VOLKSWAGEN-DERBY-86C-SEDAN-01	3975	1580	1355	Auto-Data Volkswagen Derby 86C 1.3	https://www.auto-data.net/en/volkswagen-derby-86c-1.3-60hp-8341
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459	Auto-Data Saab 9-5 Sport Combi facelift 1.9 TiD	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2005-1.9-tid-150hp-42747
EU-LOTUS-EXIGE-S2-S-COUPE-01	3797	1727	1163	Lotus Exige S official specifications (GG Lotus archive)	https://gglotus.org/gghotnews/body-exigenews.htm
EU-LAMBORGHINI-MURCIELAGO-LP640-COUPE-01	4610	2058	1135	Edmunds 2008 Lamborghini Murcielago LP640 specs	https://www.edmunds.com/lamborghini/murcielago/2008/st-100957891/features-specs/
EU-LAMBORGHINI-GALLARDO-SPYDER-CONVERTIBLE-01	4300	1900	1184	Automobile-Catalog 2006 Lamborghini Gallardo Spyder E-Gear	https://www.automobile-catalog.com/car/2006/1372220/lamborghini_gallardo_spyder_e-gear.html
EU-VOLKSWAGEN-JETTA-I-SEDAN-01	4190	1610	1410	Automobile-Catalog 1983 Volkswagen Jetta 1300	https://www.automobile-catalog.com/car/1983/31940/volkswagen_jetta_1300.html
EU-VOLKSWAGEN-GOLF-II-GTI-HATCHBACK-01	3985	1680	1415	Auto-Data Volkswagen Golf II GTI 8V	https://www.auto-data.net/fr/volkswagen-golf-ii-5-door-1.8-gti-8v-112hp-8769
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460	Auto-Data Peugeot 407 model	https://www.auto-data.net/en/peugeot-407-model-574
EU-MERCEDES-BENZ-SL-R230-FACELIFT-CONVERTIBLE-01	4532	1827	1298	Auto-Data Mercedes-Benz SL R230 facelift SL 350; Auto-Data Mercedes-Benz SL R230 facelift SL 600	https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-sl-350-v6-272hp-7g-tronic-41263;https://www.auto-data.net/en/mercedes-benz-sl-r230-facelift-2006-sl-600-v12-517hp-automatic-40991
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695	Automobile-Catalog 2006 Suzuki Grand Vitara 2.7 V6 5-Door 4WD	https://www.automobile-catalog.com/car/2006/3414920/suzuki_grand_vitara_2_7_v6_5-door_4wd_automatic.html
EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 TFSI 200	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tfsi-200hp-40832
EU-VOLKSWAGEN-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TFSI 200	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0i-16v-tfsi-200hp-automatic-28714
EU-RENAULT-MEGANE-II-PHASE-II-CC-CONVERTIBLE-01	4355	1777	1404	Auto-Data Renault Megane II CC generation	https://www.auto-data.net/en/renault-megane-ii-cc-generation-2150
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-01	4228	1777	1458	Auto-Data Renault Megane II Phase II generation	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-generation-5607
EU-RENAULT-MEGANE-II-PHASE-II-GRANDTOUR-WAGON-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II generation	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-generation-5613
EU-RENAULT-SCENIC-II-PHASE-I-MPV-01	4259	1810	1620	Auto-Data Renault Scenic II Phase I 2.0 dCi 150	https://www.auto-data.net/en/renault-scenic-ii-phase-i-2.0-dci-150hp-39488
EU-RENAULT-SCENIC-II-PHASE-II-MPV-01	4263	1805	1620	Auto-Data Renault Scenic II Phase II generation	https://www.auto-data.net/en/renault-scenic-ii-phase-ii-generation-7615
EU-VOLVO-V70-II-FACELIFT-WAGON-01	4710	1804	1465	Auto-Data Volvo V70 II facelift 2.4D	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4d-126hp-42645
EU-VOLVO-V70-II-FACELIFT-WAGON-AWD-01	4710	1804	1514	Auto-Data Volvo V70 II facelift D5 AWD	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4-d5-185hp-awd-9244
EU-VOLVO-XC70-I-FACELIFT-WAGON-01	4733	1860	1562	Auto-Data Volvo XC70 model	https://www.auto-data.net/en/volvo-xc70-model-933
EU-PEUGEOT-307-I-FACELIFT-WAGON-01	4432	1757	1544	Automobile-Catalog Peugeot 307 Break 1.6 HDi 90	https://www.automobile-catalog.com/car/2006/2618015/peugeot_307_break_estate_1_6_hdi_90.html
EU-VOLKSWAGEN-CRAFTER-I-BUS-MWB-HIGHROOF-01	5905	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-BUS-LWB-HIGHROOF-01	6940	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-LOWROOF-01	5240	1993	2415	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-SWB-HIGHROOF-01	5240	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-SRW-01	5905	1993	2415	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-LOWROOF-DRW-01	5905	1993	2415	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-SRW-01	5905	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-HIGHROOF-DRW-01	5905	1993	2755	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-SRW-01	5905	1993	2940	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-MWB-SUPERHIGHROOF-DRW-01	5905	1993	2990	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-SRW-01	6940	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-HIGHROOF-DRW-01	6940	1993	2755	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-SRW-01	6940	1993	2940	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWB-SUPERHIGHROOF-DRW-01	6940	1993	2990	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-SRW-01	7340	1993	2705	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-HIGHROOF-DRW-01	7340	1993	2755	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-SRW-01	7340	1993	2940	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-VAN-LWBMAXI-SUPERHIGHROOF-DRW-01	7340	1993	2990	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-CITROEN-BERLINGO-I-VAN-MPV-01	4137	1724	1810	Automobile-Catalog Citroen Berlingo Multispace; Drive.Place Citroen Berlingo I facelift Van	https://www.automobile-catalog.com/car/2004/550190/citroen_berlingo_multispace_2_0_hdi.html;https://citroen.drive.place/berlingo/i_res/group_furgon/579315
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-SRW-01	5865	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-MWB-DRW-01	6082	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-SRW-01	6675	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-CHASSIS-CAB-LWB-DRW-01	6842	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-SRW-01	6675	1990	2345	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-CRAFTER-I-DOUBLE-CAB-LWB-DRW-01	6842	1990	2395	Volkswagen Crafter official UK brochure	https://www.autosynergy.co.uk/assets/brochures/volkswagen-crafter.pdf
EU-VOLKSWAGEN-GOLF-I-HATCHBACK-01	3815	1610	1410	Volkswagen Newsroom Golf I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1460	Automobile-Catalog 2006 Opel Astra 1.8	https://www.automobile-catalog.com/car/2006/2526785/opel_astra_1_8.html
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	4290	1753	1415	Auto-Data Opel Astra H GTC 1.8i 140	https://www.auto-data.net/en/opel-astra-h-gtc-1.8i-140hp-2379
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	4290	1753	1435	Auto-Data Opel Astra H GTC facelift 1.8 ECOTEC 140	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.8-ecotec-140hp-47430
EU-DAEWOO-LEGANZA-V100-SEDAN-01	4671	1779	1437	Automobile-Catalog 2001 Daewoo Leganza 2.0 SX	https://www.automobile-catalog.com/car/2001/557255/daewoo_leganza_2_0_sx.html
EU-DAEWOO-NUBIRA-J150-SEDAN-01	4495	1700	1430	Automobile-Catalog 2000 Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/2000/556820/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-J150-WAGON-01	4550	1720	1430	Automobile-Catalog 2000 Daewoo Nubira 2.0 CDX Wagon; Automobile-Catalog 2001 Daewoo Nubira 1.6 SE Wagon	https://www.automobile-catalog.com/car/2000/556835/daewoo_nubira_2_0_cdx_wagon.html;https://www.automobile-catalog.com/car/2001/556850/daewoo_nubira_1_6_se_wagon.html
EU-DAEWOO-NUBIRA-J100-WAGON-01	4514	1700	1432	Automobile-Catalog 1998 Daewoo Nubira 2.0 CDX Wagon	https://www.automobile-catalog.com/car/1998/556625/daewoo_nubira_2_0_cdx_wagon.html
EU-DAEWOO-REZZO-KLAU-MPV-01	4350	1755	1580	Auto-Data Daewoo Rezzo KLAU 1.8	https://www.auto-data.net/en/daewoo-rezzo-klau-1.8-i-101hp-16287
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1854	1723	Auto-Data Ford Galaxy II 2.0 145	https://www.auto-data.net/fr/ford-galaxy-ii-2.0-i-16v-145hp-7881
EU-FORD-GALAXY-II-FACELIFT-MPV-01	4819	1884	1758	Automobile-Catalog 2011 Ford Galaxy 2.0 TDCi 140 Titanium	https://www.automobile-catalog.com/car/2011/1234670/ford_galaxy_2_0_tdci_140_titanium.html
EU-FORD-S-MAX-I-MPV-PREFL-01	4768	1884	1658	Auto-Data Ford S-Max 2.0 TDCi 140	https://www.auto-data.net/en/ford-s-max-2.0-tdci-140hp-8115
EU-FORD-S-MAX-I-FACELIFT-MPV-01	4772	1884	1660	Automobile-Catalog 2013 Ford S-Max 2.0 TDCi 140 Titanium	https://www.automobile-catalog.com/car/2013/1234955/ford_s-max_2_0_tdci_140_titanium.html
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	4660	1828	1417	Alfa Romeo UK 159 and 159 Sportwagon Technical Data; Auto-Data Alfa Romeo 159 Sportwagon 1.9 JTS	https://allcarcentral.com/alfa_pdf/Alfa_Romeo_159_159_Sportwagon_2010_Technical_Specification.pdf;https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.9-jts-160hp-1530
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	4660	1828	1422	Alfa Romeo UK 159 and 159 Sportwagon Technical Data	https://allcarcentral.com/alfa_pdf/Alfa_Romeo_159_159_Sportwagon_2010_Technical_Specification.pdf
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699	Auto-Data Porsche Cayenne 955 Turbo S	https://www.auto-data.net/en/porsche-cayenne-955-turbo-s-4.5-v8-521hp-tiptronic-s-6727
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300	Auto-Data Porsche 911 997 Turbo 480	https://www.auto-data.net/en/porsche-911-997-turbo-3.6-480hp-6590
EU-AUDI-TT-8J-COUPE-01	4178	1842	1352	Auto-Data Audi TT Coupe 8J 2.0 TFSI 200	https://www.auto-data.net/en/audi-tt-coupe-8j-2.0-tfsi-200hp-4877
EU-VOLKSWAGEN-TOUAREG-I-7L-V6-FSI-SUV-01	4754	1928	1726	Auto-Data Volkswagen Touareg I 3.6 FSI; Volkswagen UK Touareg press kit	https://www.auto-data.net/en/volkswagen-touareg-i-7l-3.6-fsi-280hp-4motion-8517;https://www.vwpress.co.uk/press-kits/150
EU-AUDI-S6-C6-SEDAN-01	4916	1864	1449	Auto-Data Audi S6 4F C6 5.2 FSI V10	https://www.auto-data.net/fr/audi-s6-4f-c6-5.2-fsi-v10-435hp-quattro-tiptronic-4534
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_201-300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://xr793.com/wp-content/uploads/2022/12/2004-Peugeot-Vans-UK.pdf "GB_GAMVU_3"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-OPEL-ASTRA-H-HATCHBACK-5D-01 的 HeightMM 与既有最终值冲突


--- 发送 / checkpoint 丢失对话 / 重发完整任务 ---
【任务名称】
【全量表更新】all 第 201-300 行

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
- 如果当前批次得到的三维与累计表中同名 `DIMENSION_GROUP_ID` 不同，禁止覆盖已有组；应使用同系列下一个可用序号创建新尺寸组，并将当前批次所有相关 Ktype 映射同步指向新组。
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
all 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	4660	1828	1417
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422
EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	4660	1828	1452
EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	4660	1828	1452
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349
EU-CITROEN-BERLINGO-I-M59-MPV-01	4137	1724	1810
EU-CITROEN-BERLINGO-I-M59-VAN-01	4137	1724	1819
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674
EU-DAEWOO-NUBIRA-III-WAGON-5D-01	4580	1725	1460
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658
EU-LOTUS-EXIGE-II-TYPE111-COUPE-265E-01	3797	1727	1149
EU-MERCEDES-BENZ-SLR-C199-COUPE-722-01	4656	1908	1261
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	4290	1753	1435
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	4290	1753	1415
EU-OPEL-ASTRA-H-HATCHBACK-3D-01	4290	1753	1415
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1467
EU-OPEL-ASTRA-H-WAGON-01	4515	1753	1500
EU-OPEL-ASTRA-H-WAGON-L35-01	4515	1753	1500
EU-PEUGEOT-307-WAGON-PREFL-01	4419	1757	1544
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486
EU-PEUGEOT-BOXER-II-BUS-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-BUS-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-BUS-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	4656	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	4656	1860	1728
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695
EU-SUZUKI-GRAND-VITARA-II-3D-PREFL-SUV-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Peugeot	307	1.6 HDI	Schrägheck	Frontantrieb	Diesel	66	90	Apr 2005	Mar 2009	2024-03-01	19341
Peugeot	Boxer	2.8 HDI	Kasten	Frontantrieb	Diesel	107	146	Apr 2004	Jun 2006	2024-03-01	19342
Peugeot	Boxer	2.8 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2004	Jun 2006	2024-03-01	19343
Mercedes-benz	Gl-Klasse	GL 450 4-matic	SUV	Allrad	Benzin	250	340	Sep 2006	Aug 2012	2024-03-01	19344
Mercedes-benz	Gl-Klasse	GL 500 4-matic	SUV	Allrad	Benzin	285	388	Sep 2006	Dec 2012	2024-03-01	19345
Mercedes-benz	Gl-Klasse	GL 420 CDI 4-matic	SUV	Allrad	Diesel	225	306	Sep 2006	May 2009	2024-03-01	19346
Mercedes-benz	Gl-Klasse	GL 320 CDI 4-matic	SUV	Allrad	Diesel	165	224	Sep 2006	May 2009	2024-03-01	19347
Peugeot	207/207+	1.4 16V	Schrägheck	Frontantrieb	Benzin	65	88	Feb 2006	Oct 2013	2024-03-01	19349
Peugeot	207/207+	1.6 16V	Schrägheck	Frontantrieb	Benzin	80	109	Feb 2006	Oct 2013	2024-03-01	19350
Peugeot	207/207+	1.6 16V Turbo	Schrägheck	Frontantrieb	Benzin	110	150	Feb 2006	Oct 2013	2024-03-01	19351
Peugeot	207/207+	1.6 HDI	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2006	Oct 2013	2024-03-01	19352
Peugeot	207/207+	1.6 HDI	Schrägheck	Frontantrieb	Diesel	80	109	Feb 2006	Oct 2013	2024-03-01	19353
Peugeot	207/207+	1.4 HDI	Schrägheck	Frontantrieb	Diesel	50	68	Feb 2006	Dec 2015	2024-03-01	19354
Renault	Clio iii	2.0 16V Sport	Schrägheck	Frontantrieb	Benzin	145	197	Feb 2006	Dec 2012	2026-05-01	19355
Renault	Laguna ii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	127	173	Jan 2006	Aug 2007	2024-03-01	19356
Renault	Laguna ii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	127	173	Jan 2006	Dec 2007	2024-03-01	19357
Renault	Espace iv	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2015	2025-12-01	19358
Renault	Espace iv	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	127	173	Jan 2006	Dec 2015	2025-12-01	19359
Renault	Espace iv	3.0 DCI	Großraumlimousine	Frontantrieb	Diesel	133	181	Jan 2006	Jan 2015	2024-03-01	19360
Opel	Signum cc	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Sep 2005	Dec 2008	2024-03-01	19361
Opel	Astra h twintop	1.8	Cabriolet	Frontantrieb	Benzin	103	140	Sep 2005	Oct 2010	2024-03-01	19362
Mitsubishi	Colt czc vi	1.5	Cabriolet	Frontantrieb	Benzin	80	109	May 2006	Jul 2009	2024-03-01	19363
Mitsubishi	Colt czc vi	1.5 Turbo	Cabriolet	Frontantrieb	Benzin	110	150	May 2006	Jul 2009	2024-03-01	19364
Mitsubishi	L200	2.5 Di-d 4WD	Pick-up	Allrad	Diesel	100	136	Nov 2005	Dec 2015	2024-03-01	19365
Mitsubishi	Lancer vii	EVO IX	Stufenheck	Allrad	Benzin	206	280	Jan 2005	Sep 2007	2024-03-01	19366
Lancia	Thesis	2.4 D Multijet	Stufenheck	Frontantrieb	Diesel	136	185	Apr 2006	Jul 2009	2024-03-01	19367
Dacia	Logan	1.6 16V	Stufenheck	Frontantrieb	Benzin	77	105	Feb 2006	-	2024-03-01	19368
Marcos	Tso convertible	5.7 V8	Cabriolet	Heckantrieb	Benzin	260	354	May 2004	-	2024-03-01	19369
Saab	9-3	1.9 TID	Cabriolet	Frontantrieb	Diesel	110	150	Jan 2006	Feb 2015	2024-03-01	19371
Marcos	Tso gt2	5.7 V8	Coupe	Heckantrieb	Benzin	354	481	Jul 2005	-	2024-03-01	19372
Saab	9-5	1.9 TID	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2009	2024-03-01	19374
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1983	Dec 1984	2024-03-01	19375
Saab	9-5	1.9 TID	Kombi	Frontantrieb	Diesel	110	150	Jan 2006	Dec 2009	2024-03-01	19376
Lotus	Exige	1.8 16V	Coupe	Heckantrieb	Benzin	163	222	Apr 2006	Jun 2012	2024-03-01	19378
Lamborghini	Murciélago	LP 640	Coupe	Allrad	Benzin	471	641	Apr 2006	-	2024-03-01	19379
Lamborghini	Gallardo	5	Cabriolet	Allrad	Benzin	382	520	Aug 2005	-	2024-03-01	19380
VW	Jetta i	1.3	Stufenheck	Frontantrieb	Benzin	43	58	Aug 1982	Feb 1984	2024-03-01	19382
VW	Golf ii	1.8 GTI	Schrägheck	Frontantrieb	Benzin	77	105	Jan 1985	Jul 1985	2024-03-01	19383
Peugeot	407	2.7 HDI	Stufenheck	Frontantrieb	Diesel	150	204	Oct 2005	Dec 2010	2024-03-01	19387
Peugeot	407	2.7 HDI	Kombi	Frontantrieb	Diesel	150	204	Oct 2005	Dec 2010	2024-03-01	19388
Mercedes-benz	Sl	350	Cabriolet	Heckantrieb	Benzin	200	272	Mar 2006	Jan 2012	2024-03-01	19389
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	285	388	Mar 2006	Jan 2012	2024-03-01	19390
Mercedes-benz	Sl	600	Cabriolet	Heckantrieb	Benzin	380	517	Mar 2006	Jan 2012	2024-03-01	19391
Mercedes-benz	Sl	55 AMG	Cabriolet	Heckantrieb	Benzin	380	517	Mar 2006	Jan 2012	2024-03-01	19392
Suzuki	Grand vitara ii	1.9 Ddis Allrad	Geländewagen geschlossen	Allrad	Diesel	95	129	Oct 2005	Feb 2015	2024-03-01	19393
VW	Passat b6	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	147	200	Jul 2005	Jul 2010	2024-03-01	19395
VW	Passat b6 variant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	147	200	Aug 2005	Nov 2010	2024-03-01	19396
Renault	Megane ii coupé-	1.9 DCI	Cabriolet	Frontantrieb	Diesel	81	110	May 2005	Mar 2009	2024-03-01	19397
Renault	Megane ii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Sep 2005	Feb 2008	2024-03-01	19398
Renault	Megane ii grandtour	2.0 DCI	Kombi	Frontantrieb	Diesel	110	150	Sep 2005	Jul 2009	2024-03-01	19399
Renault	Megane ii coupé-	2.0 DCI	Cabriolet	Frontantrieb	Diesel	110	150	Sep 2005	Mar 2009	2024-03-01	19400
Renault	Scénic ii	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	110	150	Sep 2005	Nov 2008	2024-03-01	19401
Volvo	V70 ii	D5	Kombi	Frontantrieb	Diesel	136	185	Apr 2005	Dec 2008	2024-03-01	19402
Volvo	V70 ii	D5 AWD	Kombi	Allrad	Diesel	136	185	May 2005	Aug 2007	2024-03-01	19403
Volvo	Xc70 i cross country	D5 AWD	Kombi	Allrad	Diesel	136	185	Dec 2005	Aug 2007	2024-03-01	19404
Peugeot	307	1.6 HDI	Kombi	Frontantrieb	Diesel	66	90	Apr 2005	Apr 2008	2024-03-01	19405
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19406
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19407
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19408
VW	Crafter 30-35	2.5 TDI	Bus	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19409
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19410
Citroën	Berlingo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	80	109	Oct 2000	Mar 2008	2024-03-01	19411
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19412
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19413
VW	Crafter 30-50	2.5 TDI	Kasten	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19414
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Apr 2006	Jul 2011	2024-03-01	19415
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Apr 2006	May 2013	2024-03-01	19416
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	100	136	Apr 2006	May 2013	2024-03-01	19417
VW	Crafter 30-50	2.5 TDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	120	163	Apr 2006	Jul 2011	2024-03-01	19418
VW	Golf i	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1983	Feb 1984	2024-03-01	19419
Opel	Astra h	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Jan 2006	Oct 2010	2024-03-01	19427
Opel	Astra h gtc	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Jan 2006	Oct 2010	2024-03-01	19428
Daewoo	Leganza	2.0 16V	Stufenheck	Frontantrieb	Benzin	93	126	Jul 2000	Apr 2004	2024-03-01	19429
Daewoo	Nubira	2.0 16V	Stufenheck	Frontantrieb	Benzin	93	126	Dec 2000	-	2024-03-01	19430
Daewoo	Nubira	2.0 16V	Kombi	Frontantrieb	Benzin	93	126	Dec 2000	-	2024-03-01	19431
Daewoo	Nubira	1.6 16V	Kombi	Frontantrieb	Benzin	76	103	Dec 2000	-	2024-03-01	19432
Daewoo	Nubira	1.6 16V	Stufenheck	Frontantrieb	Benzin	76	103	Jul 2000	-	2024-03-01	19433
Daewoo	Nubira	1.6 16V	Kombi	Frontantrieb	Benzin	66	90	Jun 1997	-	2024-03-01	19434
Daewoo	Rezzo	1.8	Großraumlimousine	Frontantrieb	Benzin	67	91	Sep 2000	-	2024-03-01	19435
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	191	260	Jan 2006	Dec 2009	2024-03-01	19436
Ford	Galaxy ii	2	Großraumlimousine	Frontantrieb	Benzin	107	145	May 2006	Jun 2015	2024-03-01	19437
Ford	Galaxy ii	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	74	100	May 2006	Jun 2015	2024-03-01	19438
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	96	130	May 2006	Jun 2015	2024-03-01	19439
Ford	Galaxy ii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2006	Jun 2015	2024-03-01	19440
Ford	S-Max	2	Großraumlimousine	Frontantrieb	Benzin	107	145	May 2006	Dec 2014	2024-03-01	19441
Ford	S-Max	2.5 ST	Großraumlimousine	Frontantrieb	Benzin	162	220	May 2006	Dec 2014	2024-03-01	19442
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	96	130	May 2006	Dec 2014	2024-03-01	19443
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	May 2006	Dec 2014	2024-03-01	19444
Alfa Romeo	159	1.9 JTS	Kombi	Frontantrieb	Benzin	118	160	Mar 2006	Nov 2011	2024-03-01	19445
Alfa Romeo	159	2.2 JTS	Kombi	Frontantrieb	Benzin	136	185	Mar 2006	Nov 2011	2024-03-01	19446
Alfa Romeo	159	3.2 JTS Q4	Kombi	Allrad	Benzin	191	260	Mar 2006	Nov 2011	2024-03-01	19447
Alfa Romeo	159	1.9 Jtdm 8V	Kombi	Frontantrieb	Diesel	88	120	Mar 2006	Nov 2011	2024-03-01	19448
Alfa Romeo	159	1.9 Jtdm 16V	Kombi	Frontantrieb	Diesel	110	150	Mar 2006	Nov 2011	2024-03-01	19449
Alfa Romeo	159	2.4 Jtdm	Kombi	Frontantrieb	Diesel	147	200	Mar 2006	Nov 2011	2024-03-01	19450
Porsche	Cayenne	Turbo S 4.5	SUV	Allrad	Benzin	383	521	May 2002	May 2006	2025-06-01	19451
Porsche	911	3.6 Turbo	Coupe	Allrad	Benzin	353	480	Mar 2006	Dec 2009	2024-03-01	19452
Audi	Tt	2.0 Tfsi	Coupe	Frontantrieb	Benzin	147	200	Aug 2006	Jun 2010	2024-03-01	19453
Audi	Tt	3.2 V6 Quattro	Coupe	Allrad	Benzin	184	250	Aug 2006	Jun 2010	2024-03-01	19454
VW	Touareg	3.6 V6 FSI	SUV	Allrad	Benzin	206	280	Oct 2005	May 2010	2024-03-01	19455
Audi	A6 c6	S6 Quattro	Stufenheck	Allrad	Benzin	320	435	Mar 2006	Mar 2011	2024-03-01	19456


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_201-300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_201-300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1758 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（875 行）

- 尺寸冲突协调：
  - EU-OPEL-ASTRA-H-HATCHBACK-5D-01 -> EU-OPEL-ASTRA-H-HATCHBACK-5D-02：4249x1753x1467 与 4249x1753x1460，创建新尺寸组
