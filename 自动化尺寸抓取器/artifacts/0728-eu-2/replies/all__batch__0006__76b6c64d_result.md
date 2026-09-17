# 任务：all 第 501-600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0006__76b6c64d


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
GAZ	Volga	2.5	Stufenheck	Heckantrieb	Benzin	67	91	Feb 1972	Jan 1993	2024-03-01	19686
GAZ	Volga	2.5	Kombi	Heckantrieb	Benzin	67	91	Feb 1972	Jan 1993	2024-03-01	19687
GAZ	Volga	2.1 D	Stufenheck	Heckantrieb	Diesel	45	61	Feb 1972	Sep 1985	2024-03-01	19688
GAZ	Volga	2.1 D	Kombi	Heckantrieb	Diesel	45	61	Feb 1972	Sep 1985	2024-03-01	19689
GAZ	Volga	2.3 D	Stufenheck	Heckantrieb	Diesel	51	69	Oct 1985	Jan 1993	2024-03-01	19690
GAZ	Volga	2.3 D	Kombi	Heckantrieb	Diesel	51	69	Oct 1985	Jan 1993	2024-03-01	19691
VW	Caddy iii	2.0 Ecofuel	Kasten/Großraumlimousine	Frontantrieb	CNG	80	109	Apr 2006	May 2015	2024-03-01	19692
VW	Caddy iii	1.4	Großraumlimousine	Frontantrieb	Benzin	59	80	May 2006	Aug 2010	2024-03-01	19693
VW	Caddy iii	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	59	80	May 2006	Aug 2010	2024-03-01	19694
Daewoo	Tico	0.8	Schrägheck	Frontantrieb	Benzin	38	52	Jan 1996	Dec 2000	2024-03-01	19695
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	75	102	Jun 1993	Jan 1996	2024-03-01	19696
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	59	80	May 2006	Nov 2009	2024-03-01	19697
VW	Polo	1.6 16V	Schrägheck	Frontantrieb	Benzin	77	105	May 2006	Nov 2009	2024-03-01	19698
Chevrolet	Captiva	2.4	SUV	Frontantrieb	Benzin	100	136	Jun 2006	Feb 2011	2024-03-01	19700
Chevrolet	Captiva	2.4 4WD	SUV	Allrad	Benzin	100	136	Jun 2006	Feb 2011	2024-03-01	19701
Chevrolet	Captiva	3.2 4WD	SUV	Allrad	Benzin	169	230	Jun 2006	-	2024-03-01	19702
VW	Passat b6 variant	2.0 FSI 4motion	Kombi	Allrad	Benzin	110	150	Sep 2005	Nov 2010	2024-03-01	19703
VW	Sharan	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Nov 2005	Mar 2010	2024-03-01	19704
VW	Jetta iii	2.0 TDI	Stufenheck	Frontantrieb	Diesel	100	136	Sep 2005	Oct 2010	2024-03-01	19705
VW	Jetta iii	1.4 TSI	Stufenheck	Frontantrieb	Benzin	103	140	Jul 2006	Oct 2010	2024-03-01	19706
VW	Jetta iii	1.4 TSI	Stufenheck	Frontantrieb	Benzin	125	170	Jul 2006	Oct 2010	2024-03-01	19707
Ford	S-Max	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	92	125	May 2006	Dec 2014	2024-03-01	19708
Mercedes-benz	S-Klasse	S 320 CDI	Stufenheck	Heckantrieb	Diesel	173	235	Dec 2005	Jun 2009	2024-03-01	19709
Mercedes-benz	S-Klasse	S 450, S 450 L	Stufenheck	Heckantrieb	Benzin	250	340	Dec 2005	Dec 2013	2025-02-03	19710
Mercedes-benz	S-Klasse	S 450 4-matic	Stufenheck	Allrad	Benzin	250	340	Dec 2005	Dec 2013	2024-03-01	19711
Mercedes-benz	S-Klasse	S 600	Stufenheck	Heckantrieb	Benzin	380	517	Dec 2005	Dec 2013	2024-03-01	19712
Mercedes-benz	S-Klasse	S 65 AMG	Stufenheck	Heckantrieb	Benzin	450	612	Dec 2005	Dec 2013	2024-03-01	19713
Ford	Galaxy ii	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	92	125	May 2006	Jun 2015	2024-03-01	19714
Hyundai	Getz	1.1	Schrägheck	Frontantrieb	Benzin	49	67	Sep 2005	Jun 2009	2024-03-01	19715
Mitsubishi	L400	2	Kasten	Heckantrieb	Benzin	85	116	Jun 1996	Mar 2001	2024-03-01	19716
Jaguar	Xk ii	4.2 XKR	Coupe	Heckantrieb	Benzin	306	416	Mar 2006	Jul 2014	2024-03-01	19717
Jaguar	Xk ii	4.2 XKR	Cabriolet	Heckantrieb	Benzin	306	416	Mar 2006	Jul 2014	2024-03-01	19718
Mercedes-benz	Cls	CLS 350	Coupe	Heckantrieb	Benzin	215	292	Apr 2006	Dec 2010	2024-03-01	19719
Mercedes-benz	Cls	CLS 500	Coupe	Heckantrieb	Benzin	285	388	Apr 2006	Dec 2010	2024-03-01	19720
Mercedes-benz	Cls	CLS 63 AMG	Coupe	Heckantrieb	Benzin	378	514	Apr 2006	Dec 2010	2024-03-01	19721
Opel	Corsa d	1	Schrägheck	Frontantrieb	Benzin	44	60	Jul 2006	Dec 2010	2024-03-01	19722
Opel	Corsa d	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Jul 2006	Aug 2014	2024-03-01	19723
Opel	Corsa d	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Aug 2006	Dec 2011	2024-03-01	19724
Opel	Corsa d	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	55	75	Jul 2006	Aug 2014	2024-03-01	19725
Opel	Corsa d	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	66	90	Jul 2006	Jun 2011	2024-03-01	19726
Opel	Corsa d	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	92	125	Aug 2006	Dec 2011	2024-03-01	19727
Mercedes-benz	S-Klasse	CL 500	Coupe	Heckantrieb	Benzin	285	388	Jun 2006	Dec 2013	2024-03-01	19728
Mercedes-benz	S-Klasse	CL 600	Coupe	Heckantrieb	Benzin	380	517	May 2006	Dec 2013	2024-03-01	19729
Hyundai	Santa fé ii	2.7 4X4	SUV	Allrad	Benzin	125	170	Mar 2006	Dec 2012	2024-03-01	19730
Hyundai	Santa fé ii	2.7	SUV	Frontantrieb	Benzin	125	170	Mar 2006	Dec 2012	2024-03-01	19731
Hyundai	Santa fé ii	2.2 Crdi	SUV	Frontantrieb	Diesel	102	139	Mar 2006	Dec 2012	2024-03-01	19732
Hyundai	Santa fé ii	2.2 Crdi 4X4	SUV	Allrad	Diesel	102	139	Mar 2006	Dec 2012	2024-03-01	19733
Mercedes-benz	A-Klasse	A 200 Turbo	Schrägheck	Frontantrieb	Benzin	142	193	Sep 2005	Jun 2012	2024-03-01	19734
Mercedes-benz	M-Klasse	ML 420 CDI 4-matic	SUV	Allrad	Diesel	225	306	Feb 2006	Sep 2009	2024-03-01	19735
Mercedes-benz	Viano	CDI 2.2 4-matic	Bus	Allrad	Diesel	80	109	Jul 2005	-	2025-06-01	19736
Mercedes-benz	Viano	CDI 2.2 4-matic	Bus	Allrad	Diesel	110	150	Jul 2005	-	2024-03-01	19737
Mercedes-benz	Viano	CDI 3.0	Bus	Heckantrieb	Diesel	150	204	Feb 2006	-	2025-04-01	19738
Audi	A4 b7	S4 Quattro	Stufenheck	Allrad	Benzin	253	344	Nov 2004	Jun 2008	2024-03-01	19739
Audi	A4 b7 avant	S4 Quattro	Kombi	Allrad	Benzin	253	344	Nov 2004	Jun 2008	2024-03-01	19740
Citroën	C4 picasso i	1.8 I 16V	Großraumlimousine	Frontantrieb	Benzin	92	125	Feb 2007	Dec 2011	2024-03-01	19747
Citroën	C4 picasso i	2.0 I 16V	Großraumlimousine	Frontantrieb	Benzin	103	140	Sep 2007	Aug 2013	2024-03-01	19748
Citroën	C4 picasso i	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	80	109	Feb 2007	Aug 2013	2024-03-01	19749
Citroën	C4 picasso i	2.0 HDI 138	Großraumlimousine	Frontantrieb	Diesel	100	136	Oct 2006	Aug 2013	2024-03-01	19750
KIA	Carens iii	2.0 Cvvt	Großraumlimousine	Frontantrieb	Benzin	106	144	Sep 2006	Jun 2013	2024-05-01	19751
KIA	Carens iii	2.0 Crdi 140	Großraumlimousine	Frontantrieb	Diesel	103	140	Sep 2006	Mar 2013	2024-05-01	19752
Volvo	S80 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	147	200	Mar 2006	Dec 2011	2024-03-01	19753
Volvo	S80 ii	3.2	Stufenheck	Frontantrieb	Benzin	175	238	Mar 2006	Dec 2010	2024-03-01	19754
Land Rover	Freelander 2	3.2 4X4	Geländewagen geschlossen	Allrad	Benzin	171	233	Oct 2006	Oct 2014	2024-03-01	19755
Volvo	S80 ii	2.4 D	Stufenheck	Frontantrieb	Diesel	120	163	Mar 2006	Mar 2011	2024-03-01	19756
Land Rover	Freelander 2	2.2 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	118	160	Oct 2006	Oct 2014	2024-03-01	19757
Lotus	Exige	1.8 265 E	Coupe	Heckantrieb	Benzin	197	268	Aug 2006	Jun 2012	2024-03-01	19759
Lexus	Ls	460	Stufenheck	Heckantrieb	Benzin	280	381	Apr 2006	-	2024-03-01	19760
Jeep	Compass	2.4 4X4	SUV	Allrad	Benzin	125	170	Sep 2006	-	2024-03-01	19762
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	103	140	Sep 2006	-	2024-03-01	19763
Ford	Mondeo iii	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	110	150	Sep 2004	Mar 2007	2024-03-01	19764
Chevrolet	Rezzo	1.6	Großraumlimousine	Frontantrieb	Benzin	79	107	Aug 2005	-	2024-03-01	19767
Chevrolet	Rezzo	2	Großraumlimousine	Frontantrieb	Benzin	90	122	Aug 2005	Sep 2009	2024-03-01	19768
Chevrolet	Nubira	1.8	Kombi	Frontantrieb	Benzin	89	121	Aug 2005	Dec 2011	2024-03-01	19769
Chevrolet	Lacetti	1.8	Schrägheck	Frontantrieb	Benzin	89	121	Aug 2005	Dec 2011	2024-03-01	19770
Peugeot	807	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	100	136	Jun 2006	-	2024-03-01	19771
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	191	260	Nov 2005	Dec 2009	2024-03-01	19772
Ford	Mondeo iii	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	110	150	Sep 2004	Mar 2007	2024-03-01	19773
Citroën	C6	2.2 HDI	Stufenheck	Frontantrieb	Diesel	125	170	Jun 2006	Dec 2012	2024-03-01	19774
Mercedes-benz	Clk	CLK 63 AMG	Coupe	Heckantrieb	Benzin	354	481	Apr 2006	May 2009	2024-03-01	19775
Mercedes-benz	Clk	CLK 63 AMG	Cabriolet	Heckantrieb	Benzin	354	481	Apr 2006	Mar 2010	2024-03-01	19776
Mercedes-benz	E-Klasse	E 200 CDI	Stufenheck	Heckantrieb	Diesel	100	136	Apr 2006	Dec 2008	2024-03-01	19777
Mercedes-benz	E-Klasse	E 220 CDI	Stufenheck	Heckantrieb	Diesel	125	170	Apr 2006	Dec 2008	2024-03-01	19778
Mercedes-benz	E-Klasse	E 220 T CDI	Kombi	Heckantrieb	Diesel	125	170	Apr 2006	Jul 2009	2024-03-01	19779
Alfa Romeo	147	1.9 JTD 16V	Schrägheck	Frontantrieb	Diesel	93	126	Sep 2003	Sep 2004	2024-03-01	19780
Alfa Romeo	147	1.9 JTD 16V	Schrägheck	Frontantrieb	Diesel	100	136	Oct 2004	Mar 2010	2024-03-01	19781
Alfa Romeo	159	1.9 Jtdm 16V	Kombi	Frontantrieb	Diesel	100	136	Mar 2006	Nov 2011	2024-03-01	19783
Alfa Romeo	159	1.9 Jtdm 8V	Kombi	Frontantrieb	Diesel	85	115	Mar 2006	Nov 2011	2024-03-01	19784
Alfa Romeo	Brera	2.4 Jtdm 20V	Schrägheck	Frontantrieb	Diesel	147	200	Jan 2006	Mar 2011	2024-03-01	19785
Ford	Focus ii	1.8 Flexifuel	Stufenheck	Frontantrieb	Benzin/Ethanol	92	125	Jun 2006	Jul 2011	2024-03-01	19786
Saab	9-7x	4.2 AWD	SUV	Allrad	Benzin	213	290	Dec 2005	Jul 2012	2024-03-01	19787
Saab	9-7x	5.3 AWD	SUV	Allrad	Benzin	220	299	Jun 2004	Jul 2012	2024-03-01	19788
Mercedes-benz	E-Klasse	E 200 Kompressor	Stufenheck	Heckantrieb	Benzin	135	184	Apr 2006	Dec 2008	2024-03-01	19789
Mercedes-benz	E-Klasse	E 200 Kompressor	Kombi	Heckantrieb	Benzin	135	184	Apr 2006	Jul 2009	2024-03-01	19790
VW	New beetle	1.8 T	Schrägheck	Frontantrieb	Benzin	132	180	Nov 2001	Jun 2005	2024-03-01	19791
Mercedes-benz	E-Klasse	E 500 T	Kombi	Heckantrieb	Benzin	285	388	Apr 2006	Jul 2009	2024-03-01	19792
Mercedes-benz	E-Klasse	E 500 T 4-matic	Kombi	Allrad	Benzin	285	388	Apr 2006	Jul 2009	2024-03-01	19793
Mercedes-benz	E-Klasse	E 500 4-matic	Stufenheck	Allrad	Benzin	285	388	Apr 2006	Dec 2008	2024-03-01	19794
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	285	388	Apr 2006	Dec 2008	2024-03-01	19795
VW	Phaeton	6.0 W12 4motion	Stufenheck	Allrad	Benzin	331	450	May 2005	Mar 2016	2024-03-01	19796
KIA	Carnival ii	2.9 TDI	Großraumlimousine	Frontantrieb	Diesel	93	126	Aug 1999	Sep 2007	2024-03-01	19797


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **VW Polo IV 9N facelift** 的三门、五门外廓；两种门数的长度和高度不同，因此分别建立尺寸组。([汽车数据网][1])
* 已闭合 **Passat B6 Variant** 与 **Jetta V**，同发动机之外的 Ktype 直接复用对应车身尺寸组。([汽车数据网][2])
* 已闭合 **Ford S-MAX I** 与 **Galaxy II** 两个五门 MPV 尺寸组。([汽车数据网][3])
* 已闭合 **Audi S4 B7 Sedan/Avant**、**Volvo S80 II**；Audi 轿车与旅行车高度不同，分别建组。([汽车数据网][4])
* Opel Corsa D 按任务中已给出的官方资料，批量拆分并复用 L08 三门、L68 五门两个尺寸组。
* Captiva、Santa Fé II 暂未建组：现有页面存在宽高范围或版本尺寸冲突。Freelander II 后期页面只明确给出含后视镜宽度，未满足统一宽度口径。([汽车数据网][5])

## 当前批次进度

* READY 映射行：**27**
* 已覆盖输入 Ktype：**19 / 100**
* 尚未闭合输入 Ktype：**81 / 100**
* 已确认尺寸组：**11**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19697_3dr	19697	Hatchback	Polo IV facelift	9N	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	MEDIUM	9N三门外廓。	READY
19697_5dr	19697	Hatchback	Polo IV facelift	9N	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	MEDIUM	9N五门外廓。	READY
19698_3dr	19698	Hatchback	Polo IV facelift	9N	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	MEDIUM	9N三门外廓。	READY
19698_5dr	19698	Hatchback	Polo IV facelift	9N	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	MEDIUM	9N五门外廓。	READY
19703	19703	Wagon	Passat B6		5	EU-VW-PASSAT-B6-VARIANT-WAGON-01	HIGH	B6 Variant五门外廓。	READY
19705	19705	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19706	19706	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19707	19707	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19708	19708	MPV	S-MAX I		5	EU-FORD-S-MAX-I-MPV-01	HIGH	第一代五门MPV外廓。	READY
19714	19714	MPV	Galaxy II		5	EU-FORD-GALAXY-II-MPV-01	HIGH	第二代五门MPV外廓。	READY
19722_3dr	19722	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19722_5dr	19722	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19723_3dr	19723	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19723_5dr	19723	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19724_3dr	19724	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19724_5dr	19724	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19725_3dr	19725	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19725_5dr	19725	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19726_3dr	19726	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19726_5dr	19726	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19727_3dr	19727	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19727_5dr	19727	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19739	19739	Sedan	S4 B7	8E	4	EU-AUDI-S4-B7-SEDAN-01	HIGH	8E B7四门轿车外廓。	READY
19740	19740	Wagon	S4 B7	8E	5	EU-AUDI-S4-B7-WAGON-01	HIGH	8E B7五门Avant外廓。	READY
19753	19753	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19754	19754	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19756	19756	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-3-d-8412
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-5-d-8413
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-i-16v-fsi-4wd-150hp-8899
EU-VW-JETTA-V-SEDAN-01	4554	1781	1459	Auto-Data	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-pde-140hp-9083
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658	Auto-Data	https://www.auto-data.net/en/ford-s-max-1.8-tdci-125hp-8112
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723	Auto-Data	https://www.auto-data.net/en/ford-galaxy-ii-1.8-tdci-125hp-7880
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-AUDI-S4-B7-SEDAN-01	4586	1781	1415	Auto-Data	https://www.auto-data.net/en/audi-s4-8e-b7-4.2-v8-344hp-quattro-27183
EU-AUDI-S4-B7-WAGON-01	4586	1781	1441	Auto-Data	https://www.auto-data.net/en/audi-s4-avant-8e-b7-4.2-v8-344hp-quattro-27194
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493	Auto-Data	https://www.auto-data.net/en/volvo-s80-ii-2.5-t-200hp-9365
```

## 下一步优先处理

1. 优先闭合 Mercedes-Benz W221、C216 与 W211/S211，高复用 Ktype 较多；其中 `19710` 必须拆分标准轴距与长轴距。
2. 处理 VW Caddy III、Mercedes-Benz Viano W639 的 SWB/LWB、车身长度及厢式/乘用边界。
3. 处理 Captiva、Santa Fé II、Jaguar XK II、Freelander II 的宽度口径或版本冲突。
4. 随后批量闭合 Citroën C4 Picasso、KIA Carens III、Ford Mondeo III 和其余单一车身车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-5-d-8413 "2005 Volkswagen Polo IV (9N, facelift 2005) 1.4 (80 Hp) 5-d | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-i-16v-fsi-4wd-150hp-8899 "Volkswagen Passat Variant (B6) 2.0 i 16V FSI 4WD (150 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/ford-s-max-1.8-tdci-125hp-8112 "Ford S-MAX 1.8 TDCi (125 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/audi-s4-8e-b7-4.2-v8-344hp-quattro-27183?utm_source=chatgpt.com "Audi S4 (8E, B7) 4.2 V8 (344 Hp) quattro | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/chevrolet-captiva-i-2.4i-16v-136hp-14611 "Chevrolet Captiva I 2.4i 16V (136 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 **Mercedes-Benz CLS C219** 改款前后两个尺寸组：改款后长度由 4913 mm 增至 4917 mm，高度由 1390 mm 增至 1430 mm，因此涉及的三个 Ktype 均拆分为 `prefl`、`facelift`。([汽车数据网][1])
* 闭合 **Mercedes-Benz CL C216** 改款前后两个尺寸组：改款后长度由 5065 mm 增至 5095 mm，高度由 1418 mm 增至 1419 mm。([汽车数据网][2])
* 闭合并批量复用 **W211 facelift Sedan** 与 **S211 facelift Wagon**；发动机和驱动形式差异未重复建组。([汽车数据网][3])

## 当前批次进度

* READY 映射行：**46**
* 已覆盖输入 Ktype：**33 / 100**
* 尚未闭合输入 Ktype：**67 / 100**
* 已确认尺寸组：**17**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19719_prefl	19719	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19719_facelift	19719	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19720_prefl	19720	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19720_facelift	19720	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19721_prefl	19721	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19721_facelift	19721	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19728_prefl	19728	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	HIGH	C216改款前双门Coupe外廓。	READY
19728_facelift	19728	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	HIGH	C216改款后双门Coupe外廓。	READY
19729_prefl	19729	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	HIGH	C216改款前双门Coupe外廓。	READY
19729_facelift	19729	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	HIGH	C216改款后双门Coupe外廓。	READY
19777	19777	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19778	19778	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19779	19779	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19789	19789	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19790	19790	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19792	19792	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19793	19793	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19794	19794	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19795	19795	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	4913	1873	1390	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-cls-350-cgi-v6-292hp-7g-tronic-47776
EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	4917	1873	1430	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-facellift-2008-cls-350-cgi-v6-292hp-7g-tronic-28295
EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	5065	1871	1418	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cl-c216-cl-500-v8-388hp-4matic-7g-tronic-12708
EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	5095	1871	1419	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673
EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	4856	1822	1483	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-200-cdi-136hp-12870
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	4888	1822	1506	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-200-cdi-136hp-12907
```

## 下一步优先处理

1. 闭合 Mercedes-Benz W221/V221 的标准轴距、长轴距及改款前后分支。
2. 闭合 Mercedes-Benz W169/C169、W164 与 CLK C209/A209 的门数及改款边界。
3. 批量处理 C4 Picasso I、Carens III、Santa Fé II 和 Chevrolet Captiva。
4. 随后处理 Viano W639、Caddy III 等多轴距或多车身长度车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-cls-350-cgi-v6-292hp-7g-tronic-47776 "Mercedes-Benz CLS coupe (C219) CLS 350 CGI V6 (292 Hp) 7G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-cl-c216-cl-500-v8-388hp-4matic-7g-tronic-12708 "Mercedes-Benz CL (C216) CL 500 V8 (388 Hp) 4MATIC 7G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-200-cdi-136hp-12870 "Mercedes-Benz E-class (W211, facelift 2006) E 200 CDI (136 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz S-Class W221/V221 的改款前后、标准轴距和长轴距分支。`19710` 明确包含 `S 450` 与 `S 450 L`，拆分为四条物理映射；S 600 与 S 65 AMG 按长轴距车身处理。([marsClassic][1])
* S 65 AMG 改款后车身尺寸不同于普通 V221 facelift，单独建立 AMG 长轴距尺寸组。([marsClassic][2])
* 闭合 CLK 63 AMG 的 C209 Coupe 与 A209 Convertible。两者虽三维相同，但车身形式和车身代码不同，分别建立尺寸组。([marsClassic][3])

## 当前批次进度

* READY 映射行：**59**
* 已覆盖输入 Ktype：**40 / 100**
* 尚未闭合输入 Ktype：**60 / 100**
* 已确认尺寸组：**24**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19709	19709	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19710_swb_prefl	19710	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19710_swb_facelift	19710	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	HIGH	W221标准轴距改款后外廓。	READY
19710_lwb_prefl	19710	Sedan	S-Class V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221长轴距改款前外廓。	READY
19710_lwb_facelift	19710	Sedan	S-Class V221 facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	HIGH	V221长轴距改款后外廓。	READY
19711_prefl	19711	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19711_facelift	19711	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	HIGH	W221标准轴距改款后外廓。	READY
19712_prefl	19712	Sedan	S-Class V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221长轴距改款前外廓。	READY
19712_facelift	19712	Sedan	S-Class V221 facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	HIGH	V221长轴距改款后外廓。	READY
19713_prefl	19713	Sedan	S-Class V221 AMG	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221 AMG长轴距改款前外廓。	READY
19713_facelift	19713	Sedan	S-Class V221 AMG facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-FACELIFT-LWB-01	HIGH	V221 AMG长轴距改款后外廓。	READY
19775	19775	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-01	HIGH	C209双门Coupe外廓。	READY
19776	19776	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	HIGH	A209双门敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	5076	1871	1473	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI-2005---2009-from-122008-S-320-CDI-BlueEFFICIENCY.xhtml?oid=191730140
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	5096	1871	1479	Automobile-Catalog; Mercedes-Benz Public Archive	https://www.automobile-catalog.com/car/2009/1555670/mercedes-benz_s_500_7g-tronic.html; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	5206	1871	1473	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-450-long-wheelbase-2006---2009.xhtml?oid=191730156
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	5226	1871	1479	Automobile-Catalog; Mercedes-Benz Public Archive	https://www.automobile-catalog.com/car/2009/1555790/mercedes-benz_s_450_lwb_7g-tronic.html; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-FACELIFT-LWB-01	5252	1871	1490	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-65-AMG-long-wheelbase-2009---2013.xhtml?oid=191730368
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400	Auto-Data	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-amg-clk-63-481hp-7g-tronic-23417
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-63-AMG-Cabriolet.xhtml?oid=2461920
```

## 下一步优先处理

1. 闭合 Caddy III 的标准轴距、Caddy Maxi 及厢式车/乘用车边界。
2. 闭合 Viano W639 的 Compact、Long、Extra Long 车身长度分支。
3. 集中解决 Captiva、Santa Fé II、M-Class W164 的高度或版本冲突。
4. 批量处理 C4 Picasso I、Carens III、Freelander II 及其余单一外廓车型。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI-2005---2009-from-122008-S-320-CDI-BlueEFFICIENCY.xhtml?oid=191730140 "S 320 CDI, 2005 - 2009 (from 12.2008: S 320 CDI BlueEFFICIENCY)"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-65-AMG-long-wheelbase-2009---2013.xhtml?oid=191730368 "S 65 AMG long wheelbase, 2009 - 2013"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-63-AMG-Cabriolet.xhtml?oid=2461920 "CLK 63 AMG Cabriolet"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz A 200 Turbo 的 **C169 三门、W169 五门以及改款前后**四个物理分支；改款后车长发生变化，因此不能合并为单一尺寸组。([marsClassic][1])
* 闭合 Mercedes-Benz ML 420 CDI 的 W164 改款前后分支；两阶段车长、宽度存在差异，分别建组。([marsClassic][2])
* Land Rover Freelander II 的汽油、柴油 Ktype 复用同一尺寸组；Jeep Compass I 的汽油、柴油 Ktype 复用同一尺寸组。([汽车数据网][3])

## 当前批次进度

* READY 映射行：**69**
* 已覆盖输入 Ktype：**46 / 100**
* 尚未闭合输入 Ktype：**54 / 100**
* 已确认尺寸组：**32**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19734_3dr_prefl	19734	Hatchback	A-Class C169	C169	3	EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-PREFL-01	HIGH	C169三门改款前外廓。	READY
19734_5dr_prefl	19734	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-PREFL-01	HIGH	W169五门改款前外廓。	READY
19734_3dr_facelift	19734	Hatchback	A-Class C169 facelift	C169	3	EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-FACELIFT-01	HIGH	C169三门改款后外廓。	READY
19734_5dr_facelift	19734	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-FACELIFT-01	HIGH	W169五门改款后外廓。	READY
19735_prefl	19735	SUV	M-Class W164	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	HIGH	W164改款前五门SUV外廓。	READY
19735_facelift	19735	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH	W164改款后五门SUV外廓。	READY
19755	19755	SUV	Freelander II		5	EU-LAND-ROVER-FREELANDER-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
19757	19757	SUV	Freelander II		5	EU-LAND-ROVER-FREELANDER-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
19762	19762	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	MK五门SUV外廓。	READY
19763	19763	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	MK五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-PREFL-01	3838	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-coupe-c169-generation-8171; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Coups-2004---2008.xhtml?oid=453317
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-PREFL-01	3838	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-w169-generation-2786; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Saloons-2004---2008.xhtml?oid=453316
EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-FACELIFT-01	3883	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-coupe-c169-facelift-2008-generation-8172; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Coups-2008---2010.xhtml?oid=2453092
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-FACELIFT-01	3883	1764	1593	Mercedes-Benz A-Class official brochure; Mercedes-Benz Public Archive	https://ragtop.org/mbbrochures/2012/ireland/20111011A-Class_WC169_0611_021.pdf; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Saloons-2008---2012.xhtml?oid=5990972
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	4788	1910	1815	Mercedes-Benz 2006 M-Class official brochure	https://ragtop.org/mbbrochures/2006/canada/2006_M-Class.pdf
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	4781	1911	1815	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-m-class-w164-facelift-2008-ml-420-cdi-v8-306hp-4matic-7g-tronic-43646; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/164-series-M-Class-2008---2011.xhtml?oid=4679089
EU-LAND-ROVER-FREELANDER-II-SUV-01	4500	1910	1740	Auto-Data	https://www.auto-data.net/en/land-rover-freelander-ii-3.2-i-24v-233hp-5178
EU-JEEP-COMPASS-I-MK-SUV-01	4405	1810	1630	Auto-Data	https://www.auto-data.net/en/jeep-compass-i-mk-2.4-170hp-4x4-1198
```

## 下一步优先处理

1. 确认 C4 Picasso I 标准悬架与后空气悬架的高度分支及适用 Ktype。
2. 解决 Carens III 的车高口径冲突，排除车顶行李架或市场规格差异。
3. 确认 Viano W639 各发动机对应的 Compact、Long、Extra Long 分支。
4. 处理 Caddy III 标准轴距与 Maxi、厢式车与乘用车边界。
5. 随后闭合 Captiva、Santa Fé II、Jaguar XK II 及其余单一外廓车型。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Coups-2004---2008.xhtml?oid=453317 "169 series A-Class Coupés, 2004 - 2008"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/164-series-M-Class-2005---2008.xhtml?oid=453319&utm_source=chatgpt.com "164 series M-Class, 2005 - 2008"
[3]: https://www.auto-data.net/en/land-rover-freelander-ii-2.2-td4-160hp-automatic-28760 "Land Rover Freelander II 2.2 TD4 (160 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 **Kia Carens III（UN）**，两个发动机 Ktype 复用同一五门 MPV 尺寸组。2006 年车型在欧洲目录中归为 Carens III，车身代码为 UN。([ADAC][1])
* 闭合 **Hyundai Santa Fé II（CM）**，前驱、四驱及汽油、柴油版本均未形成不同外廓，四个 Ktype 复用同一尺寸组。([汽车数据网][2])
* 闭合 **Jaguar XKR X150** Coupe 与 Convertible；两者长宽一致，但车高分别为 1322 mm 和 1329 mm，因此独立建组。1892 mm 宽度已交叉确认是不含后视镜宽度。([汽车数据网][3])
* 闭合 **Daewoo Tico KLY3**、**Saab 9-7X** 与 **Citroën C6 I**；同车身不同发动机直接复用尺寸组。([汽车数据网][4])

## 当前批次进度

* READY 映射行：**81**
* 已覆盖输入 Ktype：**58 / 100**
* PENDING 输入 Ktype：**42 / 100**
* 已确认尺寸组：**39**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19695	19695	Hatchback	Tico	KLY3	5	EU-DAEWOO-TICO-KLY3-HATCHBACK-01	MEDIUM	KLY3五门掀背外廓。	READY
19717	19717	Coupe	XK II	X150	2	EU-JAGUAR-XK-X150-COUPE-01	HIGH	X150双门Coupe外廓。	READY
19718	19718	Convertible	XK II	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-01	HIGH	X150双门敞篷外廓。	READY
19730	19730	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19731	19731	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19732	19732	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19733	19733	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19751	19751	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH	UN五门MPV外廓。	READY
19752	19752	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH	UN五门MPV外廓。	READY
19774	19774	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH	第一代四门轿车外廓。	READY
19787	19787	SUV	9-7X		5	EU-SAAB-9-7X-SUV-01	MEDIUM	五门SUV外廓。	READY
19788	19788	SUV	9-7X		5	EU-SAAB-9-7X-SUV-01	MEDIUM	五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAEWOO-TICO-KLY3-HATCHBACK-01	3340	1400	1395	Auto-Data	https://www.auto-data.net/en/daewoo-tico-kly3-0.8-48hp-16339
EU-JAGUAR-XK-X150-COUPE-01	4791	1892	1322	Auto-Data; Edmunds	https://www.auto-data.net/en/jaguar-xk-coupe-x150-r-4.2-v8-416hp-automatic-270; https://www.edmunds.com/jaguar/xk-series/2007/xkr/features-specs/
EU-JAGUAR-XK-X150-CONVERTIBLE-01	4791	1892	1329	Auto-Data; Edmunds	https://www.auto-data.net/en/jaguar-xk-convertible-x150-r-4.2-v8-416hp-automatic-272; https://www.edmunds.com/jaguar/xk-series/2007/st-100793918/features-specs/
EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	4650	1890	1725	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-2.7-i-v6-24v-189hp-4wd-automatic-13754
EU-KIA-CARENS-III-UN-MPV-01	4545	1820	1650	Auto-Data	https://www.auto-data.net/en/kia-carens-ii-2.0-crdi-140hp-automatic-28531
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464	Auto-Data	https://www.auto-data.net/en/citroen-c6-i-2.2-hdi-biturbo-16v-170hp-27938
EU-SAAB-9-7X-SUV-01	4922	1915	1791	Auto-Data	https://www.auto-data.net/en/saab-9-7x-4.2-i-24v-279hp-11971
```

## 下一步优先处理

1. Caddy III 标准轴距、Maxi、厢式车与乘用车边界。
2. Viano W639 Compact、Long、Extra Long 与发动机适用范围。
3. C4 Picasso I 的 1660/1680 mm 高度配置边界。
4. Captiva I 的 1850/1870 mm 宽度和 1720/1755 mm 高度配置边界。
5. GAZ Volga Sedan/Wagon、Mondeo III、Alfa Romeo 147/159 与 Chevrolet/Daewoo 共平台车型。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/kia/carens/?utm_source=chatgpt.com "Kia Carens: Modelle, Technische Daten, Preise | ADAC"
[2]: https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-2.7-i-v6-24v-189hp-4wd-automatic-13754 "Hyundai Santa Fe II (CM) 2.7 i V6 24V (189 Hp) 4WD Automatic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/jaguar-xk-convertible-x150-r-4.2-v8-416hp-automatic-272 "Jaguar XK Convertible (X150) R 4.2 V8 (416 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/daewoo-tico-kly3-0.8-48hp-16339 "Daewoo Tico (KLY3) 0.8 (48 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮新增 **19 条 READY 映射**，覆盖 **18 个 Ktype**，首次创建 **14 个尺寸组**。
* GAZ Volga 轿车按前期 GAZ-24 与后期 GAZ-2410 拆分：车高分别为 1490 mm 和 1476 mm；旅行车前后期三维一致，继续复用同一尺寸组。([汽车数据网][1])
* 已批量闭合 Primera P10、Mondeo Sedan/Hatchback、Rezzo、Nubira Wagon、Lacetti Hatchback、807、Saab 9-5、Brera、Focus II Sedan 与 New Beetle 9C。([汽车数据网][2])

## 当前批次进度

* READY 映射行：**100**
* 已覆盖输入 Ktype：**76 / 100**
* PENDING 输入 Ktype：**24 / 100**
* 已确认尺寸组：**53**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19686_prefl	19686	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	MEDIUM	前期GAZ-24轿车外廓。	READY
19686_facelift	19686	Sedan	Volga GAZ-2410	GAZ-2410	4	EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	MEDIUM	后期GAZ-2410轿车外廓。	READY
19687	19687	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车前后期三维一致。	READY
19688	19688	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	MEDIUM	前期GAZ-24轿车外廓。	READY
19689	19689	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车外廓。	READY
19690	19690	Sedan	Volga GAZ-2410	GAZ-2410	4	EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	MEDIUM	后期GAZ-2410轿车外廓。	READY
19691	19691	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车外廓。	READY
19696	19696	Sedan	Primera P10	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门轿车外廓。	READY
19764	19764	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-01	HIGH	B4Y四门轿车外廓。	READY
19767	19767	MPV	Rezzo	KLAU	5	EU-CHEVROLET-REZZO-KLAU-MPV-01	HIGH	KLAU五门MPV外廓。	READY
19768	19768	MPV	Rezzo	KLAU	5	EU-CHEVROLET-REZZO-KLAU-MPV-01	HIGH	KLAU五门MPV外廓。	READY
19769	19769	Wagon	Nubira J200	J200	5	EU-CHEVROLET-NUBIRA-J200-WAGON-01	HIGH	J200五门旅行车外廓。	READY
19770	19770	Hatchback	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200五门掀背外廓。	READY
19771	19771	MPV	807		5	EU-PEUGEOT-807-MPV-01	MEDIUM	五门MPV外廓。	READY
19772	19772	Sedan	9-5 facelift 2005		4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19773	19773	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	HIGH	B5Y五门掀背外廓。	READY
19785	19785	Coupe	Brera	939	2	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	939双门Coupe外廓。	READY
19786	19786	Sedan	Focus II		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19791	19791	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-01	MEDIUM	9C三门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	4735	1800	1490	Auto-Data	https://www.auto-data.net/en/gaz-24-2.4-95hp-13671
EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	4735	1800	1476	Auto-Data	https://www.auto-data.net/en/gaz-2410-2.4-100hp-13666
EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	4735	1800	1576	Auto-Data; Auto-Data	https://www.auto-data.net/en/gaz-2402-2.4-95hp-13670; https://www.auto-data.net/en/gaz-2412-2.4-100hp-13662
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-p10-generation-186
EU-FORD-MONDEO-III-B4Y-SEDAN-01	4731	1812	1429	Auto-Data	https://www.auto-data.net/en/ford-mondeo-ii-sedan-2.2-tdci-155hp-7682
EU-CHEVROLET-REZZO-KLAU-MPV-01	4350	1755	1580	Auto-Data	https://www.auto-data.net/en/chevrolet-rezzo-1.6-i-16v-105hp-14444
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460	Auto-Data	https://www.auto-data.net/en/chevrolet-nubira-station-wagon-1.8-i-16v-122hp-14358
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data	https://www.auto-data.net/en/chevrolet-lacetti-hatchback-1.8-i-16v-122hp-14438
EU-PEUGEOT-807-MPV-01	4730	1850	1750	Auto-Data	https://www.auto-data.net/en/peugeot-807-2.0-16v-136hp-5524
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data	https://www.auto-data.net/en/saab-9-5-facelift-2005-2.3-turbo-260hp-42735
EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	4731	1812	1429	Auto-Data	https://www.auto-data.net/en/ford-mondeo-ii-hatchback-2.2-tdci-155hp-7693
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4413	1830	1372	Auto-Data	https://www.auto-data.net/en/alfa-romeo-brera-2.4-jtd-200hp-1566
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497	Auto-Data	https://www.auto-data.net/en/ford-focus-ii-sedan-1.8-i-16v-125hp-7333
EU-VW-NEW-BEETLE-9C-HATCHBACK-01	4081	1725	1500	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-9c-1.8-t-150hp-8807
```

## 下一步优先处理

1. Caddy III：`19692–19694` 的标准轴距、Maxi、厢式车和乘用车分支。
2. Captiva I、C4 Picasso I：分别解决配置高度与标准版/Grand 版边界。
3. Viano W639、Mitsubishi L400：处理多车长、轴距和车顶分支。
4. Alfa Romeo 147、159 Sportwagon：闭合门数、改款和精确车高。
5. 最后处理 Sharan、Getz、Exige、Lexus LS、Phaeton及Carnival。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/gaz-24-model-1467?utm_source=chatgpt.com "GAZ 24 | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/nissan-primera-p10-generation-186 "Nissan Primera (P10) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Caddy III 标准轴距乘用 MPV 分支 `19693`；含 `Kasten/Großraumlimousine` 的 `19692`、`19694` 暂不强行归入乘用组，等待厢式车外廓直接来源闭合。Caddy III 乘用版三维为 4405 × 1802 × 1833 mm。([汽车数据网][1])
* 闭合 Sharan I facelift 2.0 TDI，采用该发动机直接页面的 4634 × 1810 × 1730 mm，不套用其他发动机页面的车高。([汽车数据网][2])
* 闭合 Lotus Exige 265E 专属外廓，车高采用该具体版本的 1149 mm，而非普通 Exige II 的 1175 mm。([汽车数据网][3])
* 闭合 Alfa Romeo 159 Sportwagon 两个前驱柴油 Ktype；标准前驱车高采用 1417 mm，未使用 Q4 四驱版本的 1422 mm。([汽车数据网][4])
* VW Phaeton W12 按 2010 年改款前后拆分；标准轴距车长由 5055 mm 变为 5059 mm。([汽车数据网][5])

## 当前批次进度

* READY 映射行：**107**
* 已覆盖输入 Ktype：**82 / 100**
* PENDING 输入 Ktype：**18 / 100**
* 已确认尺寸组：**59**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19693	19693	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	HIGH	标准轴距乘用MPV外廓；滑门配置导致门数可变。	READY
19704	19704	MPV	Sharan I facelift	7M	5	EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	HIGH	改款后五门MPV外廓。	READY
19759	19759	Coupe	Exige II 265E	Type 111	2	EU-LOTUS-EXIGE-II-TYPE111-COUPE-265E-01	HIGH	265E专属双门Coupe外廓。	READY
19783	19783	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	MEDIUM	939前驱五门旅行车外廓。	READY
19784	19784	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	MEDIUM	939前驱五门旅行车外廓。	READY
19796_prefl	19796	Sedan	Phaeton	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	2010年改款前标准轴距四门轿车外廓。	READY
19796_facelift	19796	Sedan	Phaeton facelift 2010	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	2010年改款后标准轴距四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833	Auto-Data	https://www.auto-data.net/en/volkswagen-caddy-iii-1.4-80hp-28287
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730	Auto-Data	https://www.auto-data.net/en/volkswagen-sharan-i-facelift-2004-2.0-tdi-140hp-44855
EU-LOTUS-EXIGE-II-TYPE111-COUPE-265E-01	3797	1727	1149	Ultimatecarpage	https://www.ultimatecarpage.com/spec/2867/Lotus-Exige-265E.html
EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	4660	1828	1417	Auto-Data; Automotyw	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.9-jtdm-16v-150hp-1528; https://automotyw.com/katalog-samochodow/alfa-romeo/159/1/sportwagon
EU-VW-PHAETON-3D-SEDAN-PREFL-01	5055	1903	1450	Auto-Data	https://www.auto-data.net/en/volkswagen-phaeton-6.0-w12-48v-450hp-tiptronic-4motion-9157
EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	5059	1903	1450	Auto-Data	https://www.auto-data.net/en/volkswagen-phaeton-facelift-2010-6.0-w12-450hp-4motion-tiptronic-16868
```

## 下一步优先处理

1. 解决 Captiva I 的 1850/1870 mm 宽度及 1720/1755 mm 高度配置边界。
2. 区分 C4 Picasso I 标准五座、Grand 七座及悬架车高分支。
3. 闭合 Caddy III 厢式车、Viano W639 三种车长和 Mitsubishi L400 多轴距/车顶分支。
4. 最后处理 Getz facelift、Alfa Romeo 147、Lexus LS 460 与 Carnival 的改款、门数或长轴距边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-caddy-iii-1.4-80hp-28287 "Volkswagen Caddy III 1.4 (80 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-sharan-i-facelift-2004-2.0-tdi-140hp-44855 "Volkswagen Sharan I (facelift 2004) 2.0 TDI (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/lotus-exige-ii-generation-4417 "Lotus Exige II | Technical Specs, Fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.9-jtdm-8v-120hp-1527 "Alfa Romeo 159 Sportwagon 1.9 JTDM 8V (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/volkswagen-phaeton-6.0-w12-48v-450hp-tiptronic-4motion-9157?utm_source=chatgpt.com "Specs of Volkswagen Phaeton 6.0 W12 48V (450 Hp) ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 新增 **23 条 READY 映射**，覆盖 **13 个 Ktype**，首次创建 **13 个尺寸组**。
* 闭合 Caddy III 的标准轴距厢式车/乘用车以及改款前后分支；未无证据扩展至 Caddy Maxi。闭合 Captiva I、Getz facelift，并按门数或阶段拆分必要映射。([汽车数据网][1])
* Viano W639 的 80 kW、110 kW 四驱版本按长轴距分别建组；150 kW CDI 3.0 确认存在 Compact、Long、Extra Long 三种外廓。([marsClassic][2])
* 闭合 Lexus LS 460 标准轴距、Alfa Romeo 147 改款前后及三门/五门映射、Kia Carnival GQ 改款前后分支。([Lexus Media Site][3])
* C4 Picasso I 的可靠资料仍给出 `1660–1680 mm` 高度范围，未满足单一正整数尺寸要求，本轮不强行建组。([汽车数据网][4])

## 当前批次进度

* READY 映射行：**130**
* 已覆盖输入 Ktype：**95 / 100**
* PENDING 输入 Ktype：**5 / 100**
* 已确认尺寸组：**72**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19692_van_prefl	19692	Van	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距厢式车改款前外廓。	READY
19692_mpv_prefl	19692	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距乘用车改款前外廓。	READY
19692_van_facelift	19692	Van	Caddy III facelift	2K		EU-VW-CADDY-III-2K-SWB-FACELIFT-01	MEDIUM	标准轴距厢式车改款后外廓。	READY
19692_mpv_facelift	19692	MPV	Caddy III facelift	2K		EU-VW-CADDY-III-2K-SWB-FACELIFT-01	MEDIUM	标准轴距乘用车改款后外廓。	READY
19694_van	19694	Van	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距厢式车外廓。	READY
19694_mpv	19694	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距乘用车外廓。	READY
19700	19700	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19701	19701	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19702	19702	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19715_3dr	19715	Hatchback	Getz facelift	TB	3	EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	MEDIUM	TB改款后三门掀背外廓。	READY
19715_5dr	19715	Hatchback	Getz facelift	TB	5	EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	MEDIUM	TB改款后五门掀背外廓。	READY
19736	19736	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	MEDIUM	80kW四驱长轴距外廓。	READY
19737	19737	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	HIGH	110kW四驱长轴距外廓。	READY
19738_compact	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	HIGH	CDI 3.0紧凑车身外廓。	READY
19738_long	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	HIGH	CDI 3.0长车身外廓。	READY
19738_extralong	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	HIGH	CDI 3.0超长车身外廓。	READY
19760	19760	Sedan	LS IV	USF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH	USF40标准轴距四门轿车外廓。	READY
19780_3dr	19780	Hatchback	147	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	MEDIUM	937改款前三门外廓。	READY
19780_5dr	19780	Hatchback	147	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	MEDIUM	937改款前五门外廓。	READY
19781_3dr	19781	Hatchback	147 facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	MEDIUM	937改款后三门外廓。	READY
19781_5dr	19781	Hatchback	147 facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	MEDIUM	937改款后五门外廓。	READY
19797_prefl	19797	MPV	Carnival GQ	GQ	5	EU-KIA-CARNIVAL-GQ-MPV-PREFL-01	MEDIUM	GQ改款前五门MPV外廓。	READY
19797_facelift	19797	MPV	Carnival GQ facelift	GQ	5	EU-KIA-CARNIVAL-GQ-MPV-FACELIFT-01	MEDIUM	GQ改款后五门MPV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823	Auto-Data	https://www.auto-data.net/en/volkswagen-caddy-iii-facelift-2010-2.0-109hp-ecofuel-20527
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/559985/chevrolet_captiva_2_4_4wd_lt.html
EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	3825	1665	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1172975/hyundai_getz_1_1.html
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-20-4MATIC-long-2006---2010.xhtml?oid=193898977
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-long-2006---2010.xhtml?oid=193898985
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-compact-2006---2010.xhtml?oid=193898989
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-long-2006---2010.xhtml?oid=193898990
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-extra-long-2006---2010.xhtml?oid=193898991
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465	Lexus Media Site	https://media.lexus.co.uk/the-new-lexus-ls-460/
EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	4170	1729	1442	Auto-Data	https://www.auto-data.net/en/alfa-romeo-147-5-doors-1.6-twin-spark-16v-105hp-1311
EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	4223	1729	1442	Auto-Data	https://www.auto-data.net/en/alfa-romeo-147-facelift-2004-5-doors-generation-5035
EU-KIA-CARNIVAL-GQ-MPV-PREFL-01	4890	1900	1730	Auto-Data	https://www.auto-data.net/en/kia-carnival-i-up-gq-generation-625
EU-KIA-CARNIVAL-GQ-MPV-FACELIFT-01	4925	1900	1730	Auto-Data	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.9-td-130hp-2750
```

## 下一步优先处理

1. 闭合 `19747–19750` C4 Picasso I 的悬架配置与确定车高边界。
2. 闭合 `19716` Mitsubishi L400 欧洲后驱 2.0 厢式车的轴距、车顶及车长分支。
3. 达到 `PENDING=0` 后，仅执行一次两张完整表的机械闭合检查并直接输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-caddy-iii-2.0-ecofuel-109hp-cng-28338 "Volkswagen Caddy III 2.0 EcoFuel (109 Hp) CNG | Technical specs, data, fuel consumption, Dimensions"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-20-4MATIC-long-2006---2010.xhtml?ls=L2VuL2luc3RhbmNlL2tvLzYzOS1zZXJpZXMtVmlhbm8tTXVsdGktUHVycG9zZS1WZWhpY2xlcy0yMDAzLS0tMjAxMC54aHRtbD9vaWQ9NDUzMzEyJnJlbElkPTEwMDEmZnJvbU9pZD00NTMzMTImcmVzdWx0SW5mb1R5cGVJZD0xNzImdmlld1R5cGU9dGh1bWJzJnNvcnREZWZpbml0aW9uPW1hbnVhbHNvcnQtMSZ0aHVtYlNjYWxlSW5kZXg9MSZyb3dDb3VudHNJbmRleD01JmZyb21JbmZvVHlwZUlkPTIyNDU%21&oid=193898977&rs=31 "Viano CDI 2.0 4MATIC long, 2006 - 2010"
[3]: https://media.lexus.co.uk/the-new-lexus-ls-460/ "The New Lexus LS 460 - Lexus Media Site"
[4]: https://www.auto-data.net/en/citroen-c4-i-picasso-phase-i-2007-2.0-hdi-136hp-fap-automatic-27586 "2007 Citroen C4 I Picasso (Phase I, 2007) 2.0 HDi (136 Hp) FAP Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合最后 5 个 Ktype。C4 Picasso I（UD）按金属后悬架与 Exclusive 空气后悬架拆分，车高分别为 1680 mm、1660 mm。([PC Group][1])
* Mitsubishi L400 2.0 厢式车按欧洲 PA3V 短轴距与 PB3V 长轴距拆分，并采用对应型式批准尺寸。([PartSouq][2])
* 已完成机械收尾检查：固定表头正确、140 个 `id` 唯一、100 个输入 Ktype 全覆盖、76 个尺寸组唯一、映射引用全部闭合、无孤立尺寸组，所有映射均为 `READY`。

## 当前批次进度

* 输入 Ktype：**100 / 100**
* READY 映射行：**140**
* PENDING：**0**
* DIMENSION_GROUP：**76**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19686_prefl	19686	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	MEDIUM	前期GAZ-24轿车外廓。	READY
19686_facelift	19686	Sedan	Volga GAZ-2410	GAZ-2410	4	EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	MEDIUM	后期GAZ-2410轿车外廓。	READY
19687	19687	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车前后期三维一致。	READY
19688	19688	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	MEDIUM	前期GAZ-24轿车外廓。	READY
19689	19689	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车外廓。	READY
19690	19690	Sedan	Volga GAZ-2410	GAZ-2410	4	EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	MEDIUM	后期GAZ-2410轿车外廓。	READY
19691	19691	Wagon	Volga GAZ-24 series		5	EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	MEDIUM	五门旅行车外廓。	READY
19692_van_prefl	19692	Van	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距厢式车改款前外廓。	READY
19692_mpv_prefl	19692	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距乘用车改款前外廓。	READY
19692_van_facelift	19692	Van	Caddy III facelift	2K		EU-VW-CADDY-III-2K-SWB-FACELIFT-01	MEDIUM	标准轴距厢式车改款后外廓。	READY
19692_mpv_facelift	19692	MPV	Caddy III facelift	2K		EU-VW-CADDY-III-2K-SWB-FACELIFT-01	MEDIUM	标准轴距乘用车改款后外廓。	READY
19693	19693	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	HIGH	标准轴距乘用MPV外廓；滑门配置导致门数可变。	READY
19694_van	19694	Van	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距厢式车外廓。	READY
19694_mpv	19694	MPV	Caddy III	2K		EU-VW-CADDY-III-2K-MPV-SWB-01	MEDIUM	标准轴距乘用车外廓。	READY
19695	19695	Hatchback	Tico	KLY3	5	EU-DAEWOO-TICO-KLY3-HATCHBACK-01	MEDIUM	KLY3五门掀背外廓。	READY
19696	19696	Sedan	Primera P10	P10	4	EU-NISSAN-PRIMERA-P10-SEDAN-01	HIGH	P10四门轿车外廓。	READY
19697_3dr	19697	Hatchback	Polo IV facelift	9N	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	MEDIUM	9N三门外廓。	READY
19697_5dr	19697	Hatchback	Polo IV facelift	9N	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	MEDIUM	9N五门外廓。	READY
19698_3dr	19698	Hatchback	Polo IV facelift	9N	3	EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	MEDIUM	9N三门外廓。	READY
19698_5dr	19698	Hatchback	Polo IV facelift	9N	5	EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	MEDIUM	9N五门外廓。	READY
19700	19700	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19701	19701	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19702	19702	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	HIGH	C100五门SUV标准外廓。	READY
19703	19703	Wagon	Passat B6		5	EU-VW-PASSAT-B6-VARIANT-WAGON-01	HIGH	B6 Variant五门外廓。	READY
19704	19704	MPV	Sharan I facelift	7M	5	EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	HIGH	改款后五门MPV外廓。	READY
19705	19705	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19706	19706	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19707	19707	Sedan	Jetta V		4	EU-VW-JETTA-V-SEDAN-01	HIGH	Jetta V四门轿车外廓。	READY
19708	19708	MPV	S-MAX I		5	EU-FORD-S-MAX-I-MPV-01	HIGH	第一代五门MPV外廓。	READY
19709	19709	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19710_swb_prefl	19710	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19710_swb_facelift	19710	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	HIGH	W221标准轴距改款后外廓。	READY
19710_lwb_prefl	19710	Sedan	S-Class V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221长轴距改款前外廓。	READY
19710_lwb_facelift	19710	Sedan	S-Class V221 facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	HIGH	V221长轴距改款后外廓。	READY
19711_prefl	19711	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	HIGH	W221标准轴距改款前外廓。	READY
19711_facelift	19711	Sedan	S-Class W221 facelift	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	HIGH	W221标准轴距改款后外廓。	READY
19712_prefl	19712	Sedan	S-Class V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221长轴距改款前外廓。	READY
19712_facelift	19712	Sedan	S-Class V221 facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	HIGH	V221长轴距改款后外廓。	READY
19713_prefl	19713	Sedan	S-Class V221 AMG	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	HIGH	V221 AMG长轴距改款前外廓。	READY
19713_facelift	19713	Sedan	S-Class V221 AMG facelift	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-FACELIFT-LWB-01	HIGH	V221 AMG长轴距改款后外廓。	READY
19714	19714	MPV	Galaxy II		5	EU-FORD-GALAXY-II-MPV-01	HIGH	第二代五门MPV外廓。	READY
19715_3dr	19715	Hatchback	Getz facelift	TB	3	EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	MEDIUM	TB改款后三门掀背外廓。	READY
19715_5dr	19715	Hatchback	Getz facelift	TB	5	EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	MEDIUM	TB改款后五门掀背外廓。	READY
19716_swb	19716	Van	L400	PA3V		EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	HIGH	PA3V欧洲短轴距厢式车外廓。	READY
19716_lwb	19716	Van	L400	PB3V		EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	HIGH	PB3V欧洲长轴距厢式车外廓。	READY
19717	19717	Coupe	XK II	X150	2	EU-JAGUAR-XK-X150-COUPE-01	HIGH	X150双门Coupe外廓。	READY
19718	19718	Convertible	XK II	X150	2	EU-JAGUAR-XK-X150-CONVERTIBLE-01	HIGH	X150双门敞篷外廓。	READY
19719_prefl	19719	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19719_facelift	19719	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19720_prefl	19720	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19720_facelift	19720	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19721_prefl	19721	Coupe	CLS C219	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	HIGH	C219改款前四门Coupe外廓。	READY
19721_facelift	19721	Coupe	CLS C219 facelift	C219	4	EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	HIGH	C219改款后四门Coupe外廓。	READY
19722_3dr	19722	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19722_5dr	19722	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19723_3dr	19723	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19723_5dr	19723	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19724_3dr	19724	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19724_5dr	19724	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19725_3dr	19725	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19725_5dr	19725	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19726_3dr	19726	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19726_5dr	19726	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19727_3dr	19727	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	L08三门物理外廓。	READY
19727_5dr	19727	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	HIGH	L68五门物理外廓。	READY
19728_prefl	19728	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	HIGH	C216改款前双门Coupe外廓。	READY
19728_facelift	19728	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	HIGH	C216改款后双门Coupe外廓。	READY
19729_prefl	19729	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	HIGH	C216改款前双门Coupe外廓。	READY
19729_facelift	19729	Coupe	CL C216 facelift	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	HIGH	C216改款后双门Coupe外廓。	READY
19730	19730	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19731	19731	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19732	19732	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19733	19733	SUV	Santa Fé II	CM	5	EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	HIGH	CM五门SUV外廓。	READY
19734_3dr_prefl	19734	Hatchback	A-Class C169	C169	3	EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-PREFL-01	HIGH	C169三门改款前外廓。	READY
19734_5dr_prefl	19734	Hatchback	A-Class W169	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-PREFL-01	HIGH	W169五门改款前外廓。	READY
19734_3dr_facelift	19734	Hatchback	A-Class C169 facelift	C169	3	EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-FACELIFT-01	HIGH	C169三门改款后外廓。	READY
19734_5dr_facelift	19734	Hatchback	A-Class W169 facelift	W169	5	EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-FACELIFT-01	HIGH	W169五门改款后外廓。	READY
19735_prefl	19735	SUV	M-Class W164	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	HIGH	W164改款前五门SUV外廓。	READY
19735_facelift	19735	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH	W164改款后五门SUV外廓。	READY
19736	19736	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	MEDIUM	80kW四驱长轴距外廓。	READY
19737	19737	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	HIGH	110kW四驱长轴距外廓。	READY
19738_compact	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	HIGH	CDI 3.0紧凑车身外廓。	READY
19738_long	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	HIGH	CDI 3.0长车身外廓。	READY
19738_extralong	19738	MPV	Viano W639	W639	4	EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	HIGH	CDI 3.0超长车身外廓。	READY
19739	19739	Sedan	S4 B7	8E	4	EU-AUDI-S4-B7-SEDAN-01	HIGH	8E B7四门轿车外廓。	READY
19740	19740	Wagon	S4 B7	8E	5	EU-AUDI-S4-B7-WAGON-01	HIGH	8E B7五门Avant外廓。	READY
19747_coil	19747	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	UD五门金属后悬架外廓。	READY
19747_airsusp	19747	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	UD五门Exclusive空气后悬架外廓。	READY
19748_coil	19748	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	UD五门金属后悬架外廓。	READY
19748_airsusp	19748	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	UD五门Exclusive空气后悬架外廓。	READY
19749_coil	19749	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	UD五门金属后悬架外廓。	READY
19749_airsusp	19749	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	UD五门Exclusive空气后悬架外廓。	READY
19750_coil	19750	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	UD五门金属后悬架外廓。	READY
19750_airsusp	19750	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	UD五门Exclusive空气后悬架外廓。	READY
19751	19751	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH	UN五门MPV外廓。	READY
19752	19752	MPV	Carens III	UN	5	EU-KIA-CARENS-III-UN-MPV-01	HIGH	UN五门MPV外廓。	READY
19753	19753	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19754	19754	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19755	19755	SUV	Freelander II		5	EU-LAND-ROVER-FREELANDER-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
19756	19756	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19757	19757	SUV	Freelander II		5	EU-LAND-ROVER-FREELANDER-II-SUV-01	HIGH	第二代五门SUV外廓。	READY
19759	19759	Coupe	Exige II 265E	Type 111	2	EU-LOTUS-EXIGE-II-TYPE111-COUPE-265E-01	HIGH	265E专属双门Coupe外廓。	READY
19760	19760	Sedan	LS IV	USF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH	USF40标准轴距四门轿车外廓。	READY
19762	19762	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	MK五门SUV外廓。	READY
19763	19763	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	MK五门SUV外廓。	READY
19764	19764	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-01	HIGH	B4Y四门轿车外廓。	READY
19767	19767	MPV	Rezzo	KLAU	5	EU-CHEVROLET-REZZO-KLAU-MPV-01	HIGH	KLAU五门MPV外廓。	READY
19768	19768	MPV	Rezzo	KLAU	5	EU-CHEVROLET-REZZO-KLAU-MPV-01	HIGH	KLAU五门MPV外廓。	READY
19769	19769	Wagon	Nubira J200	J200	5	EU-CHEVROLET-NUBIRA-J200-WAGON-01	HIGH	J200五门旅行车外廓。	READY
19770	19770	Hatchback	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	HIGH	J200五门掀背外廓。	READY
19771	19771	MPV	807		5	EU-PEUGEOT-807-MPV-01	MEDIUM	五门MPV外廓。	READY
19772	19772	Sedan	9-5 facelift 2005		4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19773	19773	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	HIGH	B5Y五门掀背外廓。	READY
19774	19774	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH	第一代四门轿车外廓。	READY
19775	19775	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-COUPE-01	HIGH	C209双门Coupe外廓。	READY
19776	19776	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	HIGH	A209双门敞篷外廓。	READY
19777	19777	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19778	19778	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19779	19779	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19780_3dr	19780	Hatchback	147	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	MEDIUM	937改款前三门外廓。	READY
19780_5dr	19780	Hatchback	147	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	MEDIUM	937改款前五门外廓。	READY
19781_3dr	19781	Hatchback	147 facelift	937	3	EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	MEDIUM	937改款后三门外廓。	READY
19781_5dr	19781	Hatchback	147 facelift	937	5	EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	MEDIUM	937改款后五门外廓。	READY
19783	19783	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	MEDIUM	939前驱五门旅行车外廓。	READY
19784	19784	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	MEDIUM	939前驱五门旅行车外廓。	READY
19785	19785	Coupe	Brera	939	2	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	939双门Coupe外廓。	READY
19786	19786	Sedan	Focus II		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH	第二代四门轿车外廓。	READY
19787	19787	SUV	9-7X		5	EU-SAAB-9-7X-SUV-01	MEDIUM	五门SUV外廓。	READY
19788	19788	SUV	9-7X		5	EU-SAAB-9-7X-SUV-01	MEDIUM	五门SUV外廓。	READY
19789	19789	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19790	19790	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19791	19791	Hatchback	New Beetle 9C	9C	3	EU-VW-NEW-BEETLE-9C-HATCHBACK-01	MEDIUM	9C三门掀背外廓。	READY
19792	19792	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19793	19793	Wagon	E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	HIGH	S211改款后五门旅行车外廓。	READY
19794	19794	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19795	19795	Sedan	E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	HIGH	W211改款后四门轿车外廓。	READY
19796_prefl	19796	Sedan	Phaeton	3D	4	EU-VW-PHAETON-3D-SEDAN-PREFL-01	HIGH	2010年改款前标准轴距四门轿车外廓。	READY
19796_facelift	19796	Sedan	Phaeton facelift 2010	3D	4	EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	HIGH	2010年改款后标准轴距四门轿车外廓。	READY
19797_prefl	19797	MPV	Carnival GQ	GQ	5	EU-KIA-CARNIVAL-GQ-MPV-PREFL-01	MEDIUM	GQ改款前五门MPV外廓。	READY
19797_facelift	19797	MPV	Carnival GQ facelift	GQ	5	EU-KIA-CARNIVAL-GQ-MPV-FACELIFT-01	MEDIUM	GQ改款后五门MPV外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_501-600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GAZ-VOLGA-GAZ-24-SEDAN-PREFL-01	4735	1800	1490	Auto-Data	https://www.auto-data.net/en/gaz-24-2.4-95hp-13671
EU-GAZ-VOLGA-GAZ-2410-SEDAN-FACELIFT-01	4735	1800	1476	Auto-Data	https://www.auto-data.net/en/gaz-2410-2.4-100hp-13666
EU-GAZ-VOLGA-GAZ-24-SERIES-WAGON-01	4735	1800	1576	Auto-Data; Auto-Data	https://www.auto-data.net/en/gaz-2402-2.4-95hp-13670; https://www.auto-data.net/en/gaz-2412-2.4-100hp-13662
EU-VW-CADDY-III-2K-MPV-SWB-01	4405	1802	1833	Auto-Data	https://www.auto-data.net/en/volkswagen-caddy-iii-1.4-80hp-28287
EU-VW-CADDY-III-2K-SWB-FACELIFT-01	4406	1794	1823	Auto-Data	https://www.auto-data.net/en/volkswagen-caddy-iii-facelift-2010-2.0-109hp-ecofuel-20527
EU-DAEWOO-TICO-KLY3-HATCHBACK-01	3340	1400	1395	Auto-Data	https://www.auto-data.net/en/daewoo-tico-kly3-0.8-48hp-16339
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410	Auto-Data	https://www.auto-data.net/en/nissan-primera-p10-generation-186
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-3-d-8412
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465	Auto-Data	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-5-d-8413
EU-CHEVROLET-CAPTIVA-I-C100-SUV-01	4635	1850	1720	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/559985/chevrolet_captiva_2_4_4wd_lt.html
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517	Auto-Data	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-i-16v-fsi-4wd-150hp-8899
EU-VW-SHARAN-I-7M-FACELIFT-MPV-01	4634	1810	1730	Auto-Data	https://www.auto-data.net/en/volkswagen-sharan-i-facelift-2004-2.0-tdi-140hp-44855
EU-VW-JETTA-V-SEDAN-01	4554	1781	1459	Auto-Data	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-pde-140hp-9083
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658	Auto-Data	https://www.auto-data.net/en/ford-s-max-1.8-tdci-125hp-8112
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-PREFL-SWB-01	5076	1871	1473	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI-2005---2009-from-122008-S-320-CDI-BlueEFFICIENCY.xhtml?oid=191730140
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-FACELIFT-SWB-01	5096	1871	1479	Automobile-Catalog; Mercedes-Benz Public Archive	https://www.automobile-catalog.com/car/2009/1555670/mercedes-benz_s_500_7g-tronic.html; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-PREFL-LWB-01	5206	1871	1473	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-450-long-wheelbase-2006---2009.xhtml?oid=191730156
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-FACELIFT-LWB-01	5226	1871	1479	Automobile-Catalog; Mercedes-Benz Public Archive	https://www.automobile-catalog.com/car/2009/1555790/mercedes-benz_s_450_lwb_7g-tronic.html; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889
EU-MERCEDES-BENZ-S-CLASS-V221-AMG-SEDAN-FACELIFT-LWB-01	5252	1871	1490	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-65-AMG-long-wheelbase-2009---2013.xhtml?oid=191730368
EU-FORD-GALAXY-II-MPV-01	4820	1854	1723	Auto-Data	https://www.auto-data.net/en/ford-galaxy-ii-1.8-tdci-125hp-7880
EU-HYUNDAI-GETZ-TB-FACELIFT-HATCHBACK-01	3825	1665	1490	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/1172975/hyundai_getz_1_1.html
EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	4595	1695	1855	Mitsubishi Europe parts catalog; Swiss Federal Roads Office type approval 1M4160	https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD314950; https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/1M4160_F.pdf
EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	4995	1695	1960	Mitsubishi Europe parts catalog; Swiss Federal Roads Office type approval 1M4161	https://partsouq.com/en/catalog/genuine/diagram?c=MMC202403&number=MR179821; https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/1M4161_F.pdf
EU-JAGUAR-XK-X150-COUPE-01	4791	1892	1322	Auto-Data; Edmunds	https://www.auto-data.net/en/jaguar-xk-coupe-x150-r-4.2-v8-416hp-automatic-270; https://www.edmunds.com/jaguar/xk-series/2007/xkr/features-specs/
EU-JAGUAR-XK-X150-CONVERTIBLE-01	4791	1892	1329	Auto-Data; Edmunds	https://www.auto-data.net/en/jaguar-xk-convertible-x150-r-4.2-v8-416hp-automatic-272; https://www.edmunds.com/jaguar/xk-series/2007/st-100793918/features-specs/
EU-MERCEDES-BENZ-CLS-C219-COUPE-PREFL-01	4913	1873	1390	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-cls-350-cgi-v6-292hp-7g-tronic-47776
EU-MERCEDES-BENZ-CLS-C219-COUPE-FACELIFT-01	4917	1873	1430	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c219-facellift-2008-cls-350-cgi-v6-292hp-7g-tronic-28295
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-MERCEDES-BENZ-CL-C216-COUPE-PREFL-01	5065	1871	1418	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cl-c216-cl-500-v8-388hp-4matic-7g-tronic-12708
EU-MERCEDES-BENZ-CL-C216-COUPE-FACELIFT-01	5095	1871	1419	Auto-Data	https://www.auto-data.net/en/mercedes-benz-cl-c216-facelift-2010-cl-500-blueefficiency-v8-435hp-4matic-7g-tronic-plus-18673
EU-HYUNDAI-SANTA-FE-II-CM-SUV-01	4650	1890	1725	Auto-Data	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-2.7-i-v6-24v-189hp-4wd-automatic-13754
EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-PREFL-01	3838	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-coupe-c169-generation-8171; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Coups-2004---2008.xhtml?oid=453317
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-PREFL-01	3838	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-w169-generation-2786; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Saloons-2004---2008.xhtml?oid=453316
EU-MERCEDES-BENZ-A-CLASS-C169-HATCHBACK-3D-FACELIFT-01	3883	1764	1595	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-a-class-coupe-c169-facelift-2008-generation-8172; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Coups-2008---2010.xhtml?oid=2453092
EU-MERCEDES-BENZ-A-CLASS-W169-HATCHBACK-5D-FACELIFT-01	3883	1764	1593	Mercedes-Benz A-Class official brochure; Mercedes-Benz Public Archive	https://ragtop.org/mbbrochures/2012/ireland/20111011A-Class_WC169_0611_021.pdf; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/169-series-A-Class-Saloons-2008---2012.xhtml?oid=5990972
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-PREFL-01	4788	1910	1815	Mercedes-Benz 2006 M-Class official brochure	https://ragtop.org/mbbrochures/2006/canada/2006_M-Class.pdf
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	4781	1911	1815	Auto-Data; Mercedes-Benz Public Archive	https://www.auto-data.net/en/mercedes-benz-m-class-w164-facelift-2008-ml-420-cdi-v8-306hp-4matic-7g-tronic-43646; https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/164-series-M-Class-2008---2011.xhtml?oid=4679089
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-80KW-01	4993	1901	1935	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-20-4MATIC-long-2006---2010.xhtml?oid=193898977
EU-MERCEDES-BENZ-VIANO-W639-LONG-4MATIC-110KW-01	4993	1901	1942	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-4MATIC-long-2006---2010.xhtml?oid=193898985
EU-MERCEDES-BENZ-VIANO-W639-COMPACT-3.0CDI-01	4748	1901	1875	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-compact-2006---2010.xhtml?oid=193898989
EU-MERCEDES-BENZ-VIANO-W639-LONG-3.0CDI-01	4993	1901	1875	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-long-2006---2010.xhtml?oid=193898990
EU-MERCEDES-BENZ-VIANO-W639-EXTRALONG-3.0CDI-01	5223	1901	1872	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-30-extra-long-2006---2010.xhtml?oid=193898991
EU-AUDI-S4-B7-SEDAN-01	4586	1781	1415	Auto-Data	https://www.auto-data.net/en/audi-s4-8e-b7-4.2-v8-344hp-quattro-27183
EU-AUDI-S4-B7-WAGON-01	4586	1781	1441	Auto-Data	https://www.auto-data.net/en/audi-s4-avant-8e-b7-4.2-v8-344hp-quattro-27194
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680	Citroën C4 Picasso and Grand C4 Picasso official brochure	https://pcgroup.rs/wp-content/uploads/2018/03/uputstvo-citroen-c4-picasso-1.pdf
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660	Citroën C4 Picasso and Grand C4 Picasso official brochure	https://pcgroup.rs/wp-content/uploads/2018/03/uputstvo-citroen-c4-picasso-1.pdf
EU-KIA-CARENS-III-UN-MPV-01	4545	1820	1650	Auto-Data	https://www.auto-data.net/en/kia-carens-ii-2.0-crdi-140hp-automatic-28531
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493	Auto-Data	https://www.auto-data.net/en/volvo-s80-ii-2.5-t-200hp-9365
EU-LAND-ROVER-FREELANDER-II-SUV-01	4500	1910	1740	Auto-Data	https://www.auto-data.net/en/land-rover-freelander-ii-3.2-i-24v-233hp-5178
EU-LOTUS-EXIGE-II-TYPE111-COUPE-265E-01	3797	1727	1149	Ultimatecarpage	https://www.ultimatecarpage.com/spec/2867/Lotus-Exige-265E.html
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465	Lexus Media Site	https://media.lexus.co.uk/the-new-lexus-ls-460/
EU-JEEP-COMPASS-I-MK-SUV-01	4405	1810	1630	Auto-Data	https://www.auto-data.net/en/jeep-compass-i-mk-2.4-170hp-4x4-1198
EU-FORD-MONDEO-III-B4Y-SEDAN-01	4731	1812	1429	Auto-Data	https://www.auto-data.net/en/ford-mondeo-ii-sedan-2.2-tdci-155hp-7682
EU-CHEVROLET-REZZO-KLAU-MPV-01	4350	1755	1580	Auto-Data	https://www.auto-data.net/en/chevrolet-rezzo-1.6-i-16v-105hp-14444
EU-CHEVROLET-NUBIRA-J200-WAGON-01	4580	1725	1460	Auto-Data	https://www.auto-data.net/en/chevrolet-nubira-station-wagon-1.8-i-16v-122hp-14358
EU-CHEVROLET-LACETTI-J200-HATCHBACK-01	4295	1725	1445	Auto-Data	https://www.auto-data.net/en/chevrolet-lacetti-hatchback-1.8-i-16v-122hp-14438
EU-PEUGEOT-807-MPV-01	4730	1850	1750	Auto-Data	https://www.auto-data.net/en/peugeot-807-2.0-16v-136hp-5524
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data	https://www.auto-data.net/en/saab-9-5-facelift-2005-2.3-turbo-260hp-42735
EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	4731	1812	1429	Auto-Data	https://www.auto-data.net/en/ford-mondeo-ii-hatchback-2.2-tdci-155hp-7693
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464	Auto-Data	https://www.auto-data.net/en/citroen-c6-i-2.2-hdi-biturbo-16v-170hp-27938
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400	Auto-Data	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-amg-clk-63-481hp-7g-tronic-23417
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-63-AMG-Cabriolet.xhtml?oid=2461920
EU-MERCEDES-BENZ-E-CLASS-W211-FACELIFT-SEDAN-01	4856	1822	1483	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-200-cdi-136hp-12870
EU-MERCEDES-BENZ-E-CLASS-S211-FACELIFT-WAGON-01	4888	1822	1506	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-200-cdi-136hp-12907
EU-ALFA-ROMEO-147-937-HATCHBACK-PREFL-01	4170	1729	1442	Auto-Data	https://www.auto-data.net/en/alfa-romeo-147-5-doors-1.6-twin-spark-16v-105hp-1311
EU-ALFA-ROMEO-147-937-HATCHBACK-FACELIFT-01	4223	1729	1442	Auto-Data	https://www.auto-data.net/en/alfa-romeo-147-facelift-2004-5-doors-generation-5035
EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	4660	1828	1417	Auto-Data; Automotyw	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-1.9-jtdm-16v-150hp-1528; https://automotyw.com/katalog-samochodow/alfa-romeo/159/1/sportwagon
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4413	1830	1372	Auto-Data	https://www.auto-data.net/en/alfa-romeo-brera-2.4-jtd-200hp-1566
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497	Auto-Data	https://www.auto-data.net/en/ford-focus-ii-sedan-1.8-i-16v-125hp-7333
EU-SAAB-9-7X-SUV-01	4922	1915	1791	Auto-Data	https://www.auto-data.net/en/saab-9-7x-4.2-i-24v-279hp-11971
EU-VW-NEW-BEETLE-9C-HATCHBACK-01	4081	1725	1500	Auto-Data	https://www.auto-data.net/en/volkswagen-new-beetle-9c-1.8-t-150hp-8807
EU-VW-PHAETON-3D-SEDAN-PREFL-01	5055	1903	1450	Auto-Data	https://www.auto-data.net/en/volkswagen-phaeton-6.0-w12-48v-450hp-tiptronic-4motion-9157
EU-VW-PHAETON-3D-SEDAN-FACELIFT-2010-01	5059	1903	1450	Auto-Data	https://www.auto-data.net/en/volkswagen-phaeton-facelift-2010-6.0-w12-450hp-4motion-tiptronic-16868
EU-KIA-CARNIVAL-GQ-MPV-PREFL-01	4890	1900	1730	Auto-Data	https://www.auto-data.net/en/kia-carnival-i-up-gq-generation-625
EU-KIA-CARNIVAL-GQ-MPV-FACELIFT-01	4925	1900	1730	Auto-Data	https://www.auto-data.net/en/kia-carnival-i-up-gq-facelift-2001-2.9-td-130hp-2750
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_501-600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://pcgroup.rs/wp-content/uploads/2018/03/uputstvo-citroen-c4-picasso-1.pdf "C4 Picasso_Grand C4 Picasso STéFi Brochure Cover"
[2]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD314950&srsltid=AfmBOopdnWHGW9kIP-z2wQc-3bQkZC86QaHrrdjn-oPIeywqdiFOsuJJ&ssd=%24%2AKwHm0sPTnYKqo-2dgaXo2r6qio2T4u3g4fP1-ryVqfG99-i--O_z-Pex8e73kOa9sN7s5eKS9vnwva-5vYSU4YX2-fCz4aGluqC-v6kAAAAAHuFPww%24 "https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD314950&srsltid=AfmBOopdnWHGW9kIP-z2wQc-3bQkZC86QaHrrdjn-oPIeywqdiFOsuJJ&ssd=%24%2AKwHm0sPTnYKqo-2dgaXo2r6qio2T4u3g4fP1-ryVqfG99-i--O_z-Pex8e73kOa9sN7s5eKS9vnwva-5vYSU4YX2-fCz4aGluqC-v6kAAAAAHuFPww%24"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_501-600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_501-600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（749 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（358 行）
