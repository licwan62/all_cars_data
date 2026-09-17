# 任务：all 第 401-500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0005__f5432364


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
Citroën	Jumper iii	2.2 HDI 120	Kasten	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2025-12-01	19582
Citroën	Jumper iii	3.0 HDI 160	Kasten	Frontantrieb	Diesel	116	157	Sep 2006	Dec 2015	2025-12-01	19583
Citroën	Jumper iii	2.2 HDI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Apr 2006	-	2025-12-01	19584
Citroën	Jumper iii	2.2 HDI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2025-12-01	19585
Ford	Transit	2.2 Tdci	Kasten	Frontantrieb	Diesel	63	85	Apr 2006	Aug 2014	2024-03-01	19586
Citroën	Jumper iii	3.0 HDI 160	Pritsche/Fahrgestell	Frontantrieb	Diesel	116	157	Sep 2006	Dec 2015	2025-12-01	19587
Ford	Transit	2.4 Tdci RWD	Kasten	Heckantrieb	Diesel	74	100	Apr 2006	Aug 2014	2024-03-01	19588
Ford	Transit	2.3 16V RWD	Kasten	Heckantrieb	Benzin	107	145	Apr 2006	Aug 2014	2024-03-01	19589
Ford	Transit	2.2 Tdci	Bus	Frontantrieb	Diesel	63	85	Apr 2006	Aug 2014	2024-03-01	19590
Ford	Transit	2.2 Tdci	Bus	Frontantrieb	Diesel	81	110	Apr 2006	Aug 2014	2024-03-01	19591
Ford	Transit	2.2 Tdci	Bus	Frontantrieb	Diesel	96	130	Apr 2006	Aug 2014	2024-03-01	19592
Ford	Transit	2.4 Tdci	Bus	Heckantrieb	Diesel	74	100	Apr 2006	Aug 2014	2024-03-01	19593
Opel	Combo tour	1.3 Cdti 16V	Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2005	Dec 2011	2024-03-01	19594
Opel	Combo	1.3 Cdti 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2005	Dec 2012	2024-03-01	19595
Ford	Transit	2.3 16V RWD	Pritsche/Fahrgestell	Heckantrieb	Benzin	107	145	Apr 2006	Aug 2014	2024-03-01	19596
Ford	Transit	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	81	110	Apr 2006	Aug 2014	2024-03-01	19597
Ford	Transit	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	63	85	Apr 2006	Aug 2014	2024-03-01	19598
Ford	Transit	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	130	Apr 2006	Aug 2014	2024-03-01	19599
Ford	Transit	2.4 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	74	100	Apr 2006	Aug 2014	2024-03-01	19600
Ford	Transit	2.4 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	85	115	Apr 2006	Aug 2014	2024-03-01	19601
Ford	Transit	2.4 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	103	140	Apr 2006	Aug 2014	2024-03-01	19602
Chevrolet	Epica	2	Stufenheck	Frontantrieb	Benzin	105	144	Jun 2006	Dec 2011	2024-03-01	19603
Chevrolet	Epica	2.5	Stufenheck	Frontantrieb	Benzin	115	156	Jun 2006	Dec 2011	2024-03-01	19604
Daihatsu	Terios	1.5 4X4	Geländewagen geschlossen	Allrad	Benzin	77	105	May 2006	-	2024-03-01	19605
Nissan	350z roadster	3.5	Cabriolet	Heckantrieb	Benzin	221	301	Nov 2004	Jan 2007	2024-03-01	19606
Hyundai	Santa fé i	2.0 Crdi 4X4	SUV	Allrad	Diesel	92	125	Aug 2003	Mar 2006	2024-03-01	19611
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	110	150	Mar 2000	Jul 2005	2024-03-01	19612
Bentley	Azure	6.8	Cabriolet	Heckantrieb	Benzin	336	456	Jun 2006	-	2024-03-01	19613
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Mar 2006	Aug 2012	2024-03-01	19614
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	125	170	Mar 2006	Aug 2012	2024-03-01	19615
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	Mar 2006	Mar 2013	2024-03-01	19616
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	125	170	Mar 2006	Mar 2013	2024-03-01	19617
Opel	Combo	1.6 CNG 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Jun 2006	-	2024-03-01	19618
Opel	Combo tour	1.6 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Jun 2006	Dec 2011	2024-03-01	19619
KIA	Sportage ii	2.0 Crdi	SUV	Frontantrieb	Diesel	103	140	Jan 2006	Oct 2008	2024-05-01	19620
Audi	A8 d3	4.2 TDI Quattro	Stufenheck	Allrad	Diesel	240	326	Jul 2005	Jul 2010	2024-03-01	19621
Audi	A8 d3	4.2 FSI Quattro	Stufenheck	Allrad	Benzin	257	350	Jun 2006	Jul 2010	2024-03-01	19622
Hyundai	Tucson	2.0 Crdi	SUV	Frontantrieb	Diesel	103	140	Jan 2006	Mar 2010	2024-03-01	19623
Hyundai	Tucson	2.0 Crdi Allrad	SUV	Allrad	Diesel	103	140	Jan 2006	Mar 2010	2024-03-01	19624
Toyota	Hiace iv	2.5 D-4d 4WD	Kasten	Allrad	Diesel	75	102	Aug 2001	Aug 2006	2024-03-01	19625
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	75	102	Jan 2006	Nov 2009	2024-11-01	19626
VW	Transporter t5	1.9 TDI	Bus	Frontantrieb	Diesel	75	102	Jan 2006	Nov 2009	2024-11-01	19627
VW	Transporter t5	1.9 TDI	Kasten	Frontantrieb	Diesel	75	102	Jan 2006	Nov 2009	2024-11-01	19628
VW	Transporter t5	1.9 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	75	102	Jan 2006	Nov 2009	2024-11-01	19629
VW	Passat b6	2.0 TDI 16V 4motion	Stufenheck	Allrad	Diesel	103	140	Mar 2005	Aug 2010	2024-03-01	19630
VW	Passat b6	2.0 FSI 4motion	Stufenheck	Allrad	Benzin	110	150	Sep 2005	Jul 2010	2024-03-01	19631
VW	Passat b6 variant	2.0 TDI 16V 4motion	Kombi	Allrad	Diesel	103	140	Aug 2005	Nov 2010	2024-03-01	19632
Peugeot	407	2.2 HDI 170	Kombi	Frontantrieb	Diesel	125	170	Mar 2006	Dec 2010	2024-03-01	19633
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Dec 2005	May 2010	2024-03-01	19634
Mercedes-benz	Sprinter 3-T	224	Bus	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2013	2024-03-01	19635
Mercedes-benz	Sprinter 3-T	224	Kasten	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2016	2024-03-01	19636
Mercedes-benz	Sprinter 3-T	224	Pritsche/Fahrgestell	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2016	2024-03-01	19637
VW	Touran	2.0 Ecofuel	Großraumlimousine	Frontantrieb	CNG	80	109	Feb 2006	May 2009	2024-03-01	19638
Mercedes-benz	Sprinter 3-T	209 CDI	Kasten	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19639
Mercedes-benz	Sprinter 3-T	209 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19640
Mercedes-benz	Sprinter 3-T	211 CDI	Bus	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19641
Mercedes-benz	Sprinter 3-T	211 CDI	Kasten	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19642
Mercedes-benz	Sprinter 3-T	211 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19643
Mercedes-benz	Sprinter 3-T	213 CDI	Kasten	Heckantrieb	Diesel	95	129	Jun 2006	Dec 2009	2024-03-01	19644
Mercedes-benz	Sprinter 3-T	213 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	95	129	Jun 2006	Dec 2009	2024-03-01	19645
Mercedes-benz	Sprinter 3-T	215 CDI	Bus	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19646
Mercedes-benz	Sprinter 3-T	215 CDI	Kasten	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19647
Mercedes-benz	Sprinter 3-T	215 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19648
Mercedes-benz	Sprinter 3-T	218 CDI	Kasten	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19649
Mercedes-benz	Sprinter 3-T	218 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19650
VW	Touran	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	103	140	Feb 2006	May 2010	2024-03-01	19651
Mercedes-benz	Sprinter 3,5-T	324	Bus	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2016	2024-03-01	19652
Mercedes-benz	Sprinter 3,5-T	311 CDI	Bus	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19653
Mercedes-benz	Sprinter 3,5-T	315 CDI	Bus	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19654
Mercedes-benz	Sprinter 3,5-T	324	Kasten	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2016	2024-03-01	19655
Mercedes-benz	Sprinter 3,5-T	311 CDI	Kasten	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19656
Mercedes-benz	Sprinter 3,5-T	315 CDI	Kasten	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19657
Mercedes-benz	Sprinter 3,5-T	324	Pritsche/Fahrgestell	Heckantrieb	Benzin	190	258	Jun 2006	Dec 2016	2024-03-01	19658
Mercedes-benz	Sprinter 3,5-T	311 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19659
Mercedes-benz	Sprinter 3,5-T	315 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19660
Mercedes-benz	Sprinter 3,5-T	309 CDI	Kasten	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19661
Mercedes-benz	Sprinter 3,5-T	309 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19662
Mercedes-benz	Sprinter 3,5-T	318 CDI	Kasten	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19663
Mercedes-benz	Sprinter 3,5-T	318 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19664
Nissan	Interstar	DCI 100	Bus	Frontantrieb	Diesel	73	99	Nov 2003	Mar 2006	2024-03-01	19665
VW	Caddy iii	2.0 Ecofuel	Großraumlimousine	Frontantrieb	CNG	80	109	Apr 2006	May 2015	2024-03-01	19666
Mercedes-benz	Sprinter 5-T	509 CDI	Kasten	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19667
Mercedes-benz	Sprinter 5-T	509 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	65	88	Jun 2006	Dec 2009	2024-03-01	19668
Mercedes-benz	Sprinter 5-T	511 CDI	Kasten	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19669
Mercedes-benz	Sprinter 5-T	511 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Jun 2006	Dec 2009	2024-03-01	19670
Mercedes-benz	Sprinter 5-T	515 CDI	Kasten	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19671
Mercedes-benz	Sprinter 5-T	515 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2006	Dec 2009	2024-03-01	19672
Mercedes-benz	Sprinter 5-T	518 CDI	Kasten	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19673
Mercedes-benz	Sprinter 5-T	518 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	135	184	Jun 2006	Dec 2009	2024-03-01	19674
Renault	Espace iv	2.2 DCI	Großraumlimousine	Frontantrieb	Diesel	102	139	Feb 2006	Dec 2015	2025-12-01	19675
Renault	Thalia i	1.2 16V	Stufenheck	Frontantrieb	Benzin	55	75	Apr 2002	Feb 2009	2025-12-01	19676
Renault	Thalia i	1.5 DCI	Stufenheck	Frontantrieb	Diesel	50	68	Feb 2003	Feb 2009	2025-12-01	19677
Renault	Megane ii coupé-	1.5 DCI	Cabriolet	Frontantrieb	Diesel	78	106	Mar 2006	Jan 2009	2024-03-01	19678
Citroën	C5	2.2 HDI	Schrägheck	Frontantrieb	Diesel	125	170	Apr 2006	Aug 2008	2024-07-01	19679
Citroën	C5	2.2 HDI	Kombi	Frontantrieb	Diesel	125	170	Apr 2006	Aug 2008	2024-07-01	19680
Citroën	C8	2.0 HDI 135	Großraumlimousine	Frontantrieb	Diesel	100	136	Mar 2006	-	2024-03-01	19681
Citroën	C2	1.4 16V	Schrägheck	Frontantrieb	Benzin	65	90	Apr 2005	Dec 2009	2024-03-01	19682
Nissan	Patrol gr v wagon	3.0 DTI	Geländewagen geschlossen	Allrad	Diesel	118	160	May 2000	-	2024-03-01	19683
GAZ	Volga	2.5	Stufenheck	Heckantrieb	Benzin	77	105	Feb 1972	Jan 1993	2024-03-01	19684
GAZ	Volga	2.5	Kombi	Heckantrieb	Benzin	77	105	Feb 1972	Jan 1993	2024-03-01	19685


--- Round 1 / 首次发送 ---
## 更新点

* 已关闭首批单一外廓乘用车，并建立 **13 个尺寸组**。
* Audi A3 的 4 个 Ktype 均跨越 2008 年外观改款，且三门 8P、五门 8PA 在改款前后长度不同，因此每个 Ktype 拆成 `prefl`、`facelift` 两条派生映射。([汽车数据网][1])
* Hyundai Tucson 140 hp 前驱和四驱版本三维一致，复用同一个尺寸组，没有因驱动形式重复建组。([汽车数据网][2])
* Passat B6 Sedan 与 Variant 外廓不同，分别建组。([汽车数据网][3])
* Jumper、Transit、Sprinter、Transporter、Hiace、Interstar 等多轴距/多车顶商用车尚未建立猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：17
* READY 映射行：21
* 待处理 Ktype：83
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19603	19603	Sedan	Epica	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250四门轿车。	READY
19604	19604	Sedan	Epica	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250四门轿车。	READY
19605	19605	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH	J200五门SUV。	READY
19606	19606	Convertible	350Z	Z33	2	EU-NISSAN-350Z-Z33-CONVERTIBLE-PREFL-01	HIGH	Z33改款前双门Roadster。	READY
19611	19611	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH	SM五门SUV。	READY
19614_prefl	19614	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8P三门改款前外廓。	READY
19614_facelift	19614	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8P三门改款后外廓。	READY
19615_prefl	19615	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8P三门改款前外廓。	READY
19615_facelift	19615	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8P三门改款后外廓。	READY
19616_prefl	19616	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款前外廓。	READY
19616_facelift	19616	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款后外廓。	READY
19617_prefl	19617	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款前外廓。	READY
19617_facelift	19617	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款后外廓。	READY
19620	19620	SUV	Sportage II	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-01	HIGH	KM五门SUV。	READY
19621	19621	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH	标准轴距4E四门轿车。	READY
19622	19622	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH	标准轴距4E四门轿车。	READY
19623	19623	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	HIGH	140 hp前驱五门外廓。	READY
19624	19624	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	HIGH	140 hp四驱版与前驱版三维一致。	READY
19630	19630	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
19631	19631	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
19632	19632	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450	Auto-Data Chevrolet Epica generation	https://www.auto-data.net/en/chevrolet-epica-generation-3201
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740	Auto-Data Daihatsu Terios II J200	https://www.auto-data.net/en/daihatsu-terios-ii-j200-1.5-i-16v-4wd-105hp-42
EU-NISSAN-350Z-Z33-CONVERTIBLE-PREFL-01	4310	1815	1328	Auto-Data Nissan 350Z Roadster Z33	https://www.auto-data.net/en/nissan-350z-roadster-z33-generation-173
EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	4500	1820	1730	Auto-Data Hyundai Santa Fe I SM	https://www.auto-data.net/en/hyundai-santa-fe-i-sm-generation-2972
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-generation-8936
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-generation-5194
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA	https://www.auto-data.net/en/audi-a3-sportback-8pa-generation-1067
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423	Auto-Data Audi A3 Sportback 8PA facelift 2008	https://www.auto-data.net/en/audi-a3-sportback-8pa-facelift-2008-generation-5196
EU-KIA-SPORTAGE-II-KM-SUV-01	4350	1840	1730	Auto-Data Kia Sportage II 2.0 CRDi 140	https://www.auto-data.net/en/kia-sportage-ii-2.0-crdi-140hp-2720
EU-AUDI-A8-D3-4E-SEDAN-01	5062	1894	1444	Auto-Data Audi A8 D3 4.2 BiTDI; Auto-Data Audi A8 D3 4.2 FSI	https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2005-4.2-bitdi-v8-326hp-quattro-dpf-tiptronic-4819;https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2005-4.2-fsi-v8-350hp-quattro-tiptronic-43762
EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	4325	1830	1730	Auto-Data Hyundai Tucson I CRDi 140 FWD; Auto-Data Hyundai Tucson I CRDi 140 4WD	https://www.auto-data.net/en/hyundai-tucson-i-2.0-16v-crdi-140hp-13763;https://www.auto-data.net/en/hyundai-tucson-i-2.0-16v-crdi-4wd-140hp-automatic-24830
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 FSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-fsi-150hp-4motion-8881
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-tdi-16v-140hp-pde-4motion-8895
```

## 下一步优先处理

1. 关闭 Espace IV、Thalia I、Megane II Coupé-Cabriolet、C5、C8、C2、Patrol Y61、GAZ Volga 等剩余乘用车。
2. 处理 Combo、Caddy III、Touran 等 MPV/厢式车型，重点拆分改款与长轴版本。
3. 最后集中处理 Jumper、Transit、Sprinter、T5、Hiace、Interstar 的轴距、车顶高度及 Bus/Kasten/Fahrgestell 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-a3-model-496 "Audi A3 | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/hyundai-tucson-i-2.0-16v-crdi-140hp-13763 "Hyundai Tucson I 2.0 16V CRDi (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volkswagen-passat-b6-generation-1895?utm_source=chatgpt.com "Volkswagen Passat (B6) | Technical Specs, Fuel ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮关闭 7 个 Ktype，新增 8 条 READY 映射及 8 个尺寸组。
* 已确认 Azure II、Espace IV 标准轴距、Megane II CC、C5 I Phase II 两种车身、C2 I 三门车身及 Patrol Y61 改款前后外廓。([汽车数据网][1])
* Patrol Ktype `19683` 跨越 2004 年改款，五门车型改款前后长宽不同，拆为两条派生映射。([汽车数据网][2])
* C2 1.4 16V 改款前后该动力版本三维一致，保持单一尺寸组，不进行无意义拆分。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：24
* READY 映射：29
* PENDING Ktype：76
* 已确认尺寸组：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19613	19613	Convertible	Azure II		2	EU-BENTLEY-AZURE-II-CONVERTIBLE-01	HIGH	Azure II双门敞篷车。	READY
19675	19675	MPV	Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	HIGH	标准轴距Espace，非Grand Espace。	READY
19678	19678	Convertible	Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷车。	READY
19679	19679	Hatchback	C5 I Phase II		5	EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	HIGH	五门掀背式车身。	READY
19680	19680	Wagon	C5 I Break Phase II		5	EU-CITROEN-C5-I-PHASE-II-WAGON-01	HIGH	五门旅行车。	READY
19682	19682	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH	三门掀背车；改款前后该动力外廓尺寸一致。	READY
19683_prefl	19683	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	MEDIUM	Ktype跨越2004改款；本行为五门改款前外廓。	READY
19683_facelift	19683	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越2004改款；本行为五门改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-AZURE-II-CONVERTIBLE-01	5400	1910	1485	Auto-Data Bentley Azure II 6.7 i V8 457 Hp Automatic	https://www.auto-data.net/en/bentley-azure-ii-6.7-i-v8-457hp-automatic-6765
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	4656	1860	1728	Auto-Data Renault Espace IV Phase II 2.2 dCi 139 Hp	https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-2.2-dci-139hp-20260
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II; Automobile-Catalog Renault Megane CC 1.5 dCi 105	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-generation-5609;https://www.automobile-catalog.com/car/2009/2955005/renault_megane_cc_1_5_dci_105.html
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4745	1780	1476	Auto-Data Citroen C5 I Phase II	https://www.auto-data.net/en/citroen-c5-i-phase-ii-2004-generation-5347
EU-CITROEN-C5-I-PHASE-II-WAGON-01	4839	1780	1511	Auto-Data Citroen C5 I Break Phase II	https://www.auto-data.net/en/citroen-c5-i-break-phase-ii-2004-generation-5346
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474	Auto-Data Citroen C2 I Phase I 1.4i 16V; Auto-Data Citroen C2 I Phase II 1.4i 16V	https://www.auto-data.net/en/citroen-c2-i-phase-i-2003-1.4i-16v-88hp-sensodrive-stop-start-14987;https://www.auto-data.net/en/citroen-c2-i-phase-ii-2008-1.4i-16v-88hp-sensodrive-stop-start-27447
EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	5010	1930	1855	Auto-Data Nissan Patrol model specifications	https://www.auto-data.net/en/nissan-patrol-model-50
EU-NISSAN-PATROL-V-Y61-SUV-5D-FACELIFT-01	5080	1940	1855	Auto-Data Nissan Patrol model specifications	https://www.auto-data.net/en/nissan-patrol-model-50
```

## 下一步优先处理

1. 关闭 Yaris、407 SW、Thalia、C8、GAZ Volga 等剩余乘用车阻塞项。
2. 集中处理 Combo、Touran、Caddy III 的车身、改款和长轴边界。
3. 最后批量拆分 Jumper、Transit、Sprinter、T5、Hiace、Interstar 的轴距、车顶及车身形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bentley-azure-ii-6.7-i-v8-457hp-automatic-6765?utm_source=chatgpt.com "Bentley Azure II 6.7 i V8 (457 Hp) Automatic /Cabriolet 2005"
[2]: https://www.auto-data.net/en/nissan-patrol-model-50?utm_source=chatgpt.com "Nissan Patrol | Technical Specs, Fuel consumption, ..."
[3]: https://www.auto-data.net/en/citroen-c2-i-phase-i-2003-1.4i-16v-88hp-sensodrive-stop-start-14987?utm_source=chatgpt.com "Citroen C2 I (Phase I, 2003) 1.4i 16V (88 Hp) SensoDrive Stop/Start | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增关闭 6 个 Ktype，共形成 8 条 READY 映射。
* Yaris 150 hp TS Turbo 已确认存在三门和五门版本；两者长度、宽度相同，但高度分别为 1500 mm 和 1470 mm，因此拆成两个尺寸组。([汽车数据网][1])
* Touran 2.0 TDI 170 跨越 2006 年改款，改款前后车长由 4391 mm 变为 4407 mm，已拆分为两个物理分支。([汽车数据网][2])
* Combo Tour 1.3 CDTI 与 1.6 CNG 94 hp 的外廓均为 4322 × 1684 × 1801 mm，复用同一尺寸组。([汽车数据网][3])
* Thalia I 两个动力 Ktype 复用同一四门轿车尺寸组。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：30
* READY 映射：37
* PENDING Ktype：70
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19594	19594	MPV	Combo Tour C facelift 2003		5	EU-OPEL-COMBO-C-TOUR-MPV-01	HIGH	五门乘用型Combo Tour C。	READY
19612_3dr	19612	Hatchback	Yaris I facelift 2003	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	MEDIUM	150 hp TS Turbo三门外廓。	READY
19612_5dr	19612	Hatchback	Yaris I facelift 2003	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	MEDIUM	150 hp TS Turbo五门外廓。	READY
19619	19619	MPV	Combo Tour C facelift 2003		5	EU-OPEL-COMBO-C-TOUR-MPV-01	HIGH	五门乘用型Combo Tour C。	READY
19634_prefl	19634	MPV	Touran I	1T	5	EU-VW-TOURAN-I-MPV-PREFL-01	HIGH	Ktype跨越2006改款；本行为改款前外廓。	READY
19634_facelift	19634	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	Ktype跨越2006改款；本行为改款后外廓。	READY
19676	19676	Sedan	Thalia I facelift 2002		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	MEDIUM	四门轿车。	READY
19677	19677	Sedan	Thalia I facelift 2002		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	MEDIUM	四门轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-COMBO-C-TOUR-MPV-01	4322	1684	1801	Auto-Data Opel Combo Tour C 1.3 CDTI 75 Hp; Auto-Data Opel Combo Tour C 1.6 CNG 94 Hp ecoFLEX	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.3-cdti-75hp-25825;https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.6-cng-94hp-ecoflex-25842
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3660	1660	1500	Auto-Data Toyota Yaris I facelift 2003 3-door	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-generation-9796
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3660	1660	1470	Auto-Data Toyota Yaris I facelift 2003 5-door TS 1.5 Turbo	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-5-door-ts-1.5-turbo-150hp-50713
EU-VW-TOURAN-I-MPV-PREFL-01	4391	1794	1635	Auto-Data Volkswagen Touran I 2.0 TDI 170 Hp DPF	https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-170hp-dpf-57149
EU-VW-TOURAN-I-MPV-FACELIFT-01	4407	1794	1635	Auto-Data Volkswagen Touran I facelift 2006 2.0 TDI 170 Hp	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-2.0-tdi-170hp-44607
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 2002 generation	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-generation-2168
```

## 下一步优先处理

1. 关闭 Peugeot 407 SW、Citroën C8、GAZ Volga Sedan/Wagon，并解决高度范围或改款边界。
2. 处理 Combo Kasten、Caddy III、Touran EcoFuel/1.4 TSI 的车身和改款冲突。
3. 按车身集群集中拆分 Jumper、Transit、Sprinter、T5、Hiace 与 Interstar 的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-generation-9796 "Toyota Yaris I (facelift 2003) 3-door | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-170hp-dpf-57149 "Volkswagen Touran I 2.0 TDI (170 Hp) DPF | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.3-cdti-75hp-25825 "Opel Combo Tour C (facelift 2003) 1.3 CDTI (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/renault-symbol-i-facelift-2002-generation-2168?utm_source=chatgpt.com "Renault Symbol I (facelift 2002) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增关闭 6 个 Ktype，形成 7 条 READY 映射。
* Combo 两个混合车身类别 Ktype 与已确认 Combo C 标准外廓一致，直接复用既有尺寸组。
* Touran 2.0 EcoFuel 复用既有 facelift 尺寸组；1.4 TSI 对应另一套已明确外廓，首次创建新组。([汽车数据网][1])
* Caddy III 2.0 EcoFuel 跨越 2010 年改款，改款前后三维不同，拆分为两个物理分支。([汽车数据网][2])
* Peugeot 407 SW 2.2 HDI 已完成单一旅行车外廓闭合。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：36
* READY 映射：44
* PENDING Ktype：64
* 已确认尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19595	19595	Van	Combo C facelift 2003			EU-OPEL-COMBO-C-TOUR-MPV-01	MEDIUM	输入类别合并厢式与乘用型车身；外部标准车身边界一致。	READY
19618	19618	Van	Combo C facelift 2003			EU-OPEL-COMBO-C-TOUR-MPV-01	MEDIUM	输入类别合并厢式与乘用型车身；外部标准车身边界一致。	READY
19633	19633	Wagon	407 SW Phase I		5	EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	HIGH	五门旅行车。	READY
19638	19638	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	标准Touran MPV外廓。	READY
19651	19651	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-02	HIGH	1.4 TSI对应独立的facelift外廓分支。	READY
19666_prefl	19666	MPV	Caddy III	2K		EU-VW-CADDY-III-MPV-PREFL-01	HIGH	Ktype跨越2010改款；本行为改款前标准轴距车身。	READY
19666_facelift	19666	MPV	Caddy III facelift 2010	2K	5	EU-VW-CADDY-III-MPV-FACELIFT-01	HIGH	Ktype跨越2010改款；本行为改款后标准轴距车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486	Auto-Data Peugeot 407 SW 2.2 HDI 170 Hp	https://www.auto-data.net/en/peugeot-407-sw-2.2-hdi-170hp-37702
EU-VW-TOURAN-I-MPV-FACELIFT-02	4391	1794	1652	Auto-Data Volkswagen Touran I facelift 2006 1.4 TSI 140 Hp	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-1.4-tsi-140hp-8535
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833	Auto-Data Volkswagen Caddy III 2.0 EcoFuel 109 Hp CNG	https://www.auto-data.net/en/volkswagen-caddy-iii-2.0-ecofuel-109hp-cng-28338
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823	Auto-Data Volkswagen Caddy III facelift 2010 2.0 EcoFuel 109 Hp	https://www.auto-data.net/en/volkswagen-caddy-iii-facelift-2010-2.0-109hp-ecofuel-20527
```

## 下一步优先处理

1. 解决 Citroën C8 高度口径范围，避免将多个高度配置拼成一个尺寸组。
2. 关闭 GAZ Volga Sedan/Wagon 的 1972—1993 车身代际边界。
3. 集中处理 Jumper、Transit、Sprinter、T5、Hiace 和 Interstar 的轴距、车顶及车身形式分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-2.0-ecofuel-109hp-cng-47479 "Volkswagen Touran I (facelift 2006) 2.0 EcoFuel (109 Hp) CNG | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-caddy-iii-2.0-ecofuel-109hp-cng-28338 "Volkswagen Caddy III 2.0 EcoFuel (109 Hp) CNG | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/peugeot-407-sw-2.2-hdi-170hp-37702 "Peugeot 407 SW 2.2 HDI (170 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已关闭剩余 3 个乘用车 Ktype；未决项现集中于多轴距、多车顶商用车。
* Citroën C8 技术资料明确区分：不含后视镜宽度为 1854 mm，不含车顶行李杆高度为 1752 mm，因此不再使用此前数据库给出的高度范围。([Citroënët][1])
* GAZ Volga Ktype 跨越 GAZ-24 与 GAZ-24-10；轿车前后期高度不同。旅行车跨越 GAZ-24-02 与 GAZ-24-12，虽三维相同，但车身代码边界明确，分别建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：39
* READY 映射：49
* PENDING Ktype：61
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19681	19681	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH	五门大型MPV。	READY
19684_gaz24	19684	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-01	HIGH	Ktype跨越车型更新；本行为GAZ-24四门轿车。	READY
19684_gaz2410	19684	Sedan	Volga GAZ-24-10	GAZ-24-10	4	EU-GAZ-VOLGA-GAZ-24-10-SEDAN-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-10四门轿车。	READY
19685_gaz2402	19685	Wagon	Volga GAZ-24-02	GAZ-24-02	5	EU-GAZ-VOLGA-GAZ-24-02-WAGON-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-02旅行车。	READY
19685_gaz2412	19685	Wagon	Volga GAZ-24-12	GAZ-24-12	5	EU-GAZ-VOLGA-GAZ-24-12-WAGON-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-12旅行车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C8-I-MPV-01	4726	1854	1752	Citroën C8 technical information	https://www.citroenet.org.uk/passenger-cars/psa/c8/c8-14.html
EU-GAZ-VOLGA-GAZ-24-SEDAN-01	4735	1800	1490	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-10-SEDAN-01	4735	1800	1476	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-02-WAGON-01	4735	1800	1576	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-12-WAGON-01	4735	1800	1576	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
```

## 下一步优先处理

1. 按同平台聚类处理 Citroën Jumper III 的 Kasten 与 Pritsche/Fahrgestell，统一关闭轴距、长度和车顶分支。
2. 批量处理 Ford Transit 2006 的 Kasten、Bus 与 Fahrgestell，避免按发动机重复建组。
3. 随后处理 VW T5、Toyota Hiace IV、Nissan Interstar，再集中关闭 Mercedes-Benz Sprinter W906。

推进信号：CONTINUE

[1]: https://www.citroenet.org.uk/passenger-cars/psa/c8/c8-14.html?utm_source=chatgpt.com "Citroën C8 - technical information"
[2]: https://www.auto-data.net/en/gaz-24-model-1467 "GAZ 24 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已完成 Citroën Jumper III 车身集群，关闭 5 个 Ktype，新增 23 条 READY 映射和 12 个尺寸组。
* Kasten 按 `L1H1、L2H1、L2H2、L3H2、L3H3、L4H2、L4H3` 拆分；只把官方车型目录中对应发动机实际提供的分支关联到各 Ktype。([Dezo's Garage][1])
* Pritsche/Fahrgestell 按原厂 Chassis Cab 的 `L1、L2、L2S、L3、L4` 拆分；宽度统一采用不含后视镜的 2050 mm。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：44
* READY 映射：72
* PENDING Ktype：56
* 已确认尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19582_l1h1	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
19582_l2h1	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
19582_l2h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
19582_l3h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
19582_l3h3	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
19582_l4h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H2-01	HIGH	L4H2厢式车外廓。	READY
19582_l4h3	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H3-01	HIGH	L4H3厢式车外廓。	READY
19583_l3h2	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
19583_l3h3	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
19583_l4h2	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H2-01	HIGH	L4H2厢式车外廓。	READY
19583_l4h3	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H3-01	HIGH	L4H3厢式车外廓。	READY
19584_l1	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	HIGH	L1单排底盘驾驶室。	READY
19584_l2	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19584_l2s	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19585_l1	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	HIGH	L1单排底盘驾驶室。	READY
19585_l2	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19585_l2s	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19585_l3	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	HIGH	L3单排底盘驾驶室。	READY
19585_l4	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	MEDIUM	L4单排底盘驾驶室。	READY
19587_l2	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19587_l2s	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19587_l3	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	HIGH	L3单排底盘驾驶室。	READY
19587_l4	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	HIGH	L4单排底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-III-VAN-L1H1-01	4963	2050	2254	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L2H1-01	5413	2050	2254	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L2H2-01	5413	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L3H2-01	5998	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L3H3-01	5998	2050	2764	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L4H2-01	6363	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L4H3-01	6363	2050	2764	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	4908	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	5358	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	5708	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	5943	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	6208	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
```

## 下一步优先处理

1. 集中处理 Ford Transit 2006 的 Kasten、Bus 和 Pritsche/Fahrgestell，按前驱/后驱可用轴距、车顶和车身长度批量建组。
2. 随后处理 VW Transporter/Multivan T5、Toyota Hiace IV 与 Nissan Interstar。
3. 最后统一关闭 Mercedes-Benz Sprinter W906 的 3-T、3.5-T、5-T 车身分支。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf "Layout 1"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已关闭 Ford Transit 2006 **Kasten** 集群的 3 个 Ktype，按前驱/后驱、轴距、车顶高度及 Jumbo 单/双后轮拆分。
* `HeightMM` 采用官方车型资料所列整车高度范围的上限，符合“最大车身外部高度”口径；`WidthMM` 统一采用不含后视镜宽度。
* 2.3 汽油后驱版本直接复用本轮首次建立的 Transit 后驱尺寸组，没有重复建组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：47
* READY 映射：93
* PENDING Ktype：53
* 已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19586_swb_lowroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	HIGH	前驱短轴低顶厢式车。	READY
19586_swb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	HIGH	前驱短轴中顶厢式车。	READY
19586_mwb_lowroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	HIGH	前驱中轴低顶厢式车。	READY
19586_mwb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱中轴中顶厢式车。	READY
19586_mwb_highroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	HIGH	前驱中轴高顶厢式车。	READY
19586_lwb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	HIGH	前驱长轴中顶厢式车。	READY
19586_lwb_highroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	HIGH	前驱长轴高顶厢式车。	READY
19588_swb_lowroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	HIGH	后驱短轴低顶厢式车。	READY
19588_swb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	HIGH	后驱短轴中顶厢式车。	READY
19588_mwb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	HIGH	后驱中轴中顶厢式车。	READY
19588_mwb_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	HIGH	后驱中轴高顶厢式车。	READY
19588_lwb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱长轴中顶厢式车。	READY
19588_lwb_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	HIGH	后驱长轴高顶厢式车。	READY
19588_jumbo_srw_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	HIGH	后驱加长轴高顶单后轮车身。	READY
19588_jumbo_drw_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	HIGH	后驱加长轴高顶双后轮宽体车身。	READY
19589_swb_lowroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	HIGH	后驱短轴低顶厢式车。	READY
19589_swb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	HIGH	后驱短轴中顶厢式车。	READY
19589_mwb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	HIGH	后驱中轴中顶厢式车。	READY
19589_mwb_highroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	HIGH	后驱中轴高顶厢式车。	READY
19589_lwb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱长轴中顶厢式车。	READY
19589_lwb_highroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	HIGH	后驱长轴高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	5230	1974	2047	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	5230	1974	2594	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	5680	1974	2381	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	5680	1974	2590	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	5230	1974	2397	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	5230	1974	2611	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	5680	1974	2394	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	5680	1974	2606	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	6403	1974	2624	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	6403	2008	2624	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
```

## 下一步优先处理

1. 处理 Ford Transit Bus 的前驱/后驱、轴距和车顶分支。
2. 处理 Ford Transit Pritsche/Fahrgestell，并区分单排/双排驾驶室及单后轮/双后轮宽度。
3. 随后关闭 VW T5、Toyota Hiace IV 和 Nissan Interstar，再集中处理 Sprinter W906。

推进信号：CONTINUE


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已关闭 Ford Transit Bus 集群的 4 个 Ktype，新增 6 条 READY 映射。
* 前驱 9/12 座 Minibus 共用 MWB 中顶外廓，直接关联既有尺寸组。
* 后驱 15 座关联既有 LWB 中顶组；17 座按 DRW 中顶和 DRW 高顶拆分。Ford 规格表明确列出 17 座采用双后轮，并区分 2380 mm 中顶与 2624 mm 高顶。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：51
* READY 映射：99
* PENDING Ktype：49
* 已确认尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19590_mwb_medroof	19590	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	MEDIUM	前驱9/12座中轴中顶Minibus外廓。	READY
19591_mwb_medroof	19591	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱9/12座中轴中顶Minibus外廓。	READY
19592_mwb_medroof	19592	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱9/12座中轴中顶Minibus外廓。	READY
19593_lwb_medroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱15座长轴中顶Minibus外廓。	READY
19593_jumbo_drw_medroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	HIGH	后驱17座加长轴中顶双后轮外廓。	READY
19593_jumbo_drw_highroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	HIGH	后驱17座加长轴高顶双后轮外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380	Ford People Movers 2007 official brochure; Ford People Movers 2012 official brochure; Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2012-Ford-People-Movers-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
```

## 下一步优先处理

1. 处理 Ford Transit Pritsche/Fahrgestell 的 SWB、MWB、LWB、EF 及单排/双排驾驶室。
2. 优先解决底盘车 SRW/DRW 不含后视镜宽度，避免使用仅含长镜臂的宽度口径。
3. 随后关闭 VW T5、Toyota Hiace IV、Nissan Interstar，再集中处理 Sprinter W906。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已关闭 Ford Transit 2006 **Pritsche/Fahrgestell** 集群的 7 个 Ktype。
* 前驱车型覆盖 SWB、MWB 与 EF 单排底盘驾驶室；后驱车型覆盖 SWB、MWB、LWB、EF，并区分单排与双排驾驶室。
* 本轮新增 7 个外廓尺寸组。长度和最大高度采用 Ford Chassis Cab 车型表，宽度统一为同代底盘驾驶室不含后视镜的 1974 mm。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：58
* READY 映射：136
* PENDING Ktype：42
* 已确认尺寸组：71
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19596_swb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	MEDIUM	后驱短轴单排底盘驾驶室。	READY
19596_mwb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	后驱中轴单排底盘驾驶室。	READY
19596_mwb_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	MEDIUM	后驱中轴双排底盘驾驶室。	READY
19596_lwb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	MEDIUM	后驱长轴单排底盘驾驶室。	READY
19596_lwb_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	后驱长轴双排底盘驾驶室。	READY
19596_ef_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	后驱加长车架单排底盘驾驶室。	READY
19596_ef_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	MEDIUM	后驱加长车架双排底盘驾驶室。	READY
19597_swb_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19597_mwb_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19597_ef_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19598_swb_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19598_mwb_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19598_ef_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19599_swb_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19599_mwb_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19599_ef_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19600_swb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19600_mwb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19600_mwb_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19600_lwb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19600_lwb_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19600_ef_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19600_ef_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
19601_swb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19601_mwb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19601_mwb_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19601_lwb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19601_lwb_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19601_ef_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19601_ef_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
19602_swb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19602_mwb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19602_mwb_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19602_lwb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19602_lwb_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19602_ef_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19602_ef_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
```

## 下一步优先处理

1. 关闭 VW Multivan/Transporter T5 的 SWB、LWB、低顶和高顶分支。
2. 处理 Toyota Hiace IV 4WD 与 Nissan Interstar Bus。
3. 最后集中处理 Mercedes-Benz Sprinter W906 的 3-T、3.5-T、5-T 集群。

推进信号：CONTINUE


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已关闭 VW T5 的 Multivan、Transporter Bus 与 Transporter Kasten 共 3 个 Ktype，新增 11 条 READY 映射和 6 个尺寸组。Multivan 采用标准轴距标准顶；Transporter 按短轴/长轴及标准顶、中顶、高顶拆分。([Dezo's Garage][1])
* Transporter Pritsche/Fahrgestell 暂未关闭：单排/双排驾驶室及裸底盘、原厂货台的整车长度边界尚未完全对应。
* Toyota Hiace 4WD 的资料同时出现不同车长和车高组合，不能直接套用后驱官方尺寸；Nissan Interstar 100 hp Bus 也尚未锁定唯一乘用车身分支，因此两者继续保留待处理。([Dezo's Garage][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：61
* READY 映射：147
* PENDING Ktype：39
* 已确认尺寸组：77
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19626	19626	MPV	Multivan T5		5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	标准轴距标准顶乘用型车身。	READY
19627_swb_lowroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	MEDIUM	短轴标准顶Bus外廓。	READY
19627_swb_medroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	MEDIUM	短轴中顶Bus外廓。	READY
19627_lwb_lowroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	MEDIUM	长轴标准顶Bus外廓。	READY
19627_lwb_medroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
19627_lwb_highroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
19628_swb_lowroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19628_swb_medroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	HIGH	短轴中顶厢式车。	READY
19628_lwb_lowroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	HIGH	长轴标准顶厢式车。	READY
19628_lwb_medroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	HIGH	长轴中顶厢式车。	READY
19628_lwb_highroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Volkswagen Multivan 2006 official brochure	https://xr793.com/wp-content/uploads/2023/07/2006-VW-Multivan-AUS.pdf
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
```

## 下一步优先处理

1. 关闭 VW Transporter T5 Pritsche/Fahrgestell 的单排、双排及车架长度分支。
2. 解决 Toyota Hiace IV 4WD 的短轴/长轴与改款前后尺寸边界。
3. 关闭 Nissan Interstar Bus 后，集中批量处理剩余 Mercedes-Benz Sprinter W906 集群。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2023/07/2006-VW-Multivan-AUS.pdf "https://xr793.com/wp-content/uploads/2023/07/2006-VW-Multivan-AUS.pdf"
[2]: https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Hiace-UK.pdf "https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Hiace-UK.pdf"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已关闭 Toyota Hiace IV 4WD 与 Nissan Interstar Bus 共 2 个 Ktype，新增 3 条 READY 映射和 3 个尺寸组。
* Hiace Ktype `19625` 明确覆盖 `KLH18` 与 `KLH28` 两种物理车身，分别按标准车身和加长车身拆分；两者车宽均为 1800 mm。([AUTODOC][1])
* Interstar 2.5 dCi 100 乘用型车身对应中轴中顶配置，整车三维为 5399 × 1990 × 2486 mm。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：63
* READY 映射：150
* PENDING Ktype：37
* 已确认尺寸组：80
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19625_klh18	19625	Van	Hiace IV XH10	KLH18		EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	HIGH	KLH18标准车身厢式车。	READY
19625_klh28	19625	Van	Hiace IV XH10	KLH28		EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	HIGH	KLH28加长车身厢式车。	READY
19665_mwb_medroof	19665	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	MEDIUM	中轴中顶乘用型车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	4715	1800	1955	Drom Toyota Hiace KLH18 body specifications	https://www.drom.ru/catalog/toyota/frame/klh18/
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	5160	1800	1955	Drom Toyota Hiace KLH28 body specifications	https://www.drom.ru/catalog/toyota/frame/klh28/
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
```

## 下一步优先处理

1. 关闭 VW Transporter T5 Pritsche/Fahrgestell 的单排、双排及原厂货台外廓。
2. 集中创建 Mercedes-Benz Sprinter W906 Kasten 的轴距、车顶和 SRW/DRW 尺寸组。
3. 复用 Sprinter 已建尺寸组，批量关联 Bus 与 Pritsche/Fahrgestell Ktype。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/spares/toyota/hiace/hiace-iv-box-lxh1-rzh1-lh1/19625-2-5-d-4d-4wd-klh18-klh28?utm_source=chatgpt.com "Parts Toyota Hiace 4 2.5 D-4D 4WD 102 hp Diesel 2001"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已关闭 Mercedes-Benz Sprinter W906 **3-T Kasten** 集群的 6 个 Ktype，新增 30 条 READY 映射和 5 个尺寸组。
* 2006 年车身制造指南明确：3,000 kg Kasten 的短轴车身代码为 `906.611`，中轴为 `906.613`；同一指南确认 `209/211/213/215/218 CDI` 及 `224` 均属于 3-T 动力序列。([DIY Sprinter][1])
* 短轴按标准顶、高顶拆分；中轴按标准顶、高顶、超高顶拆分。车宽统一采用不含后视镜的 1993 mm。Sprinter 官方车型资料确认 W906 的轴距、车长及各车顶高度边界。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：69
* READY 映射：180
* PENDING Ktype：31
* 已确认尺寸组：85
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19636_swb_lowroof	19636	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19636_swb_highroof	19636	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19636_mwb_lowroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19636_mwb_highroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19636_mwb_superhighroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19639_swb_lowroof	19639	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19639_swb_highroof	19639	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19639_mwb_lowroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19639_mwb_highroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19639_mwb_superhighroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19642_swb_lowroof	19642	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19642_swb_highroof	19642	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19642_mwb_lowroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19642_mwb_highroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19642_mwb_superhighroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19644_swb_lowroof	19644	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19644_swb_highroof	19644	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19644_mwb_lowroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19644_mwb_highroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19644_mwb_superhighroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19647_swb_lowroof	19647	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19647_swb_highroof	19647	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19647_mwb_lowroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19647_mwb_highroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19647_mwb_superhighroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19649_swb_lowroof	19649	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19649_swb_highroof	19649	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19649_mwb_lowroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19649_mwb_highroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19649_mwb_superhighroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	5245	1993	2415	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	5245	1993	2700	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	5910	1993	2415	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	5910	1993	2700	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	5910	1993	2930	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
```

## 下一步优先处理

1. 关闭 Sprinter W906 3.5-T Kasten 的短轴、中轴、长轴及加长车身分支。
2. 关闭 Sprinter W906 5-T Kasten 的中轴、长轴及双后轮高度分支。
3. 随后批量处理 Sprinter Bus、Pritsche/Fahrgestell，并最后解决 VW Transporter T5 底盘车。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "Body/Equipment Mounting Directives for Sprinter Model ..."


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **3.5-T 柴油 Kasten** 的 4 个 Ktype：`19656`、`19657`、`19661`、`19663`。
* 短轴、中轴标准顶/高顶直接复用既有尺寸组；本轮仅首次创建长轴和加长车身的 4 个尺寸组。
* 311 CDI 覆盖短轴、中轴、长轴；315 CDI 覆盖中轴、长轴、加长车身；309 CDI 覆盖短轴和中轴；318 CDI 覆盖中轴和长轴。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：73
* READY 映射：200
* PENDING Ktype：27
* 已确认尺寸组：89
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19656_swb_lowroof	19656	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19656_swb_highroof	19656	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
19656_mwb_lowroof	19656	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19656_mwb_highroof	19656	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19656_lwb_highroof	19656	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19656_lwb_superhighroof	19656	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19657_mwb_lowroof	19657	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19657_mwb_highroof	19657	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19657_lwb_highroof	19657	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19657_lwb_superhighroof	19657	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19657_exl_highroof	19657	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	HIGH	加长车身高顶厢式车。	READY
19657_exl_superhighroof	19657	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长车身超高顶厢式车。	READY
19661_swb_lowroof	19661	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19661_swb_highroof	19661	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
19661_mwb_lowroof	19661	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19661_mwb_highroof	19661	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19663_mwb_lowroof	19663	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19663_mwb_highroof	19663	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19663_lwb_highroof	19663	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19663_lwb_superhighroof	19663	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	6945	1993	2700	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	6945	1993	2930	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	7345	1993	2700	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	7345	1993	2935	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
```

## 下一步优先处理

1. 关闭 Sprinter 3.5-T `324` 汽油 Kasten 的实际车长和车顶组合。
2. 关闭 Sprinter 5-T Kasten 的中轴、长轴、SRW/DRW 与高度分支。
3. 批量处理 Sprinter Bus 和 Pritsche/Fahrgestell，最后解决 Transporter T5 底盘车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 `3.5-T 324 Kasten` 的 Ktype `19655`，新增 6 条 READY 映射。
* Mercedes-Benz 2006 车身指南显示：`324` 汽油版仅覆盖中轴标准顶/高顶/超高顶、长轴超高顶，以及加长轴高顶/超高顶；短轴和长轴高顶普通分支不包含 `MC9`，因此没有错误扩展分支。([DIY Sprinter][1])
* 6 个外廓均已在前轮首次建立，直接复用现有尺寸组，本轮没有重复抓取或新建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：74
* READY 映射：206
* PENDING Ktype：26
* 已确认尺寸组：89
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19655_mwb_lowroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19655_mwb_highroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19655_mwb_superhighroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
19655_lwb_superhighroof	19655	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19655_exl_highroof	19655	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	HIGH	加长车身高顶厢式车。	READY
19655_exl_superhighroof	19655	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长车身超高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 首次建立 Sprinter 5-T Kasten 的中轴、长轴和加长轴尺寸组；重载底盘车高与现有 3-T/3.5-T 组不同，不能直接误复用。
2. 批量关联 `509 CDI、511 CDI、515 CDI、518 CDI` 四个 Kasten Ktype。
3. 随后关闭 Sprinter Bus、Pritsche/Fahrgestell 和最后的 VW Transporter T5 底盘车。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "Body/Equipment Mounting Directives for Sprinter Model ..."


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **5-T Kasten** 的 4 个 Ktype：`19667`、`19669`、`19671`、`19673`。
* 四个动力版本均覆盖 `906.653`、`906.655`、`906.657` 三种车身代码；按中轴、长轴、加长轴及标准顶/高顶/超高顶拆分为 7 个物理外廓。([汽车医生][1])
* 本轮尺寸统一采用 5.0 吨车型数据；资料同时明确车宽为不含后视镜的车身宽度，高度为厂家给出的空载最大高度。([doczz.net][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：78
* READY 映射：234
* PENDING Ktype：22
* 已确认尺寸组：96
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19667_mwb_lowroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19667_mwb_highroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19667_mwb_superhighroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19667_lwb_highroof	19667	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19667_lwb_superhighroof	19667	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19667_exl_highroof	19667	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19667_exl_superhighroof	19667	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19669_mwb_lowroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19669_mwb_highroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19669_mwb_superhighroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19669_lwb_highroof	19669	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19669_lwb_superhighroof	19669	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19669_exl_highroof	19669	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19669_exl_superhighroof	19669	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19671_mwb_lowroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19671_mwb_highroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19671_mwb_superhighroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19671_lwb_highroof	19671	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19671_lwb_superhighroof	19671	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19671_exl_highroof	19671	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19671_exl_superhighroof	19671	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19673_mwb_lowroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19673_mwb_highroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19673_mwb_superhighroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19673_lwb_highroof	19673	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19673_lwb_superhighroof	19673	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19673_exl_highroof	19673	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19673_exl_superhighroof	19673	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	5910	1993	2510	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	5910	1993	2795	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	5910	1993	3030	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	6945	1993	2795	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	6945	1993	3025	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	7345	1993	2800	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	7345	1993	3030	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
```

## 下一步优先处理

1. 关闭 Sprinter W906 3-T 与 3.5-T Bus 的中轴、长轴及车顶分支。
2. 批量处理 Sprinter 3-T、3.5-T、5-T Pritsche/Fahrgestell，优先复用相同驾驶室外廓。
3. 最后解决 VW Transporter T5 Pritsche/Fahrgestell，并进行剩余 PENDING 清零检查。

推进信号：CONTINUE

[1]: https://www.motor-doctor.co.uk/rocker-panel/mercedes-benz/sprinter/sprinter-5-t-box-906/19667-509-cdi-906-653-906-655-906-657?utm_source=chatgpt.com "Rocker panel Mercedes Sprinter 5t 509 CDI 2.2 (906.653, ..."
[2]: https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz "Sprinter paketti- ja kuorma-autoumpimallin - Mercedes-Benz"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **3.5-T Bus** 的 3 个 Ktype：`19652`、`19653`、`19654`。
* `324` 对应 `906.733、906.735`；`311 CDI` 与 `315 CDI` 对应 `906.731、906.733、906.735`。按短轴、中轴、长轴及标准顶/高顶拆成 5 个外廓。([Rolling][1])
* 长度与车身边界采用 Mercedes-Benz W906 车身制造指南，宽度统一为不含后视镜的 1993 mm；Transfer Minibus 标准顶和高顶高度分别采用 2485 mm、2770 mm。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：81
* READY 映射：247
* PENDING Ktype：19
* 已确认尺寸组：101
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19652_mwb_lowroof	19652	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19652_mwb_highroof	19652	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19652_lwb_highroof	19652	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19653_swb_lowroof	19653	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19653_swb_highroof	19653	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19653_mwb_lowroof	19653	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19653_mwb_highroof	19653	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19653_lwb_highroof	19653	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19654_swb_lowroof	19654	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19654_swb_highroof	19654	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19654_mwb_lowroof	19654	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19654_mwb_highroof	19654	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19654_lwb_highroof	19654	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	5245	1993	2485	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	5245	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	5910	1993	2485	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	5910	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	6945	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
```

## 下一步优先处理

1. 关闭 Sprinter 3-T Bus 的 `224、211 CDI、215 CDI`，按 `906.711、906.713` 和两种车顶拆分。
2. 集中处理 Sprinter 3-T、3.5-T、5-T Pritsche/Fahrgestell 的单排与双排驾驶室。
3. 最后关闭 VW Transporter T5 Pritsche/Fahrgestell，并执行 PENDING 清零检查。

推进信号：CONTINUE

[1]: https://shop.rolling.hu/catalog/SCHAEFFLER/mercedes-benz-sprinter-35-t-bus-b906-324-906733-906735?utm_source=chatgpt.com "MERCEDES-BENZ SPRINTER 3,5-t Bus (B906) 324 (906.733, 906.735) Part list - Rolling Kft. webshop"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **3-T Bus** 的 3 个 Ktype：`19635`、`19641`、`19646`。
* Mercedes-Benz 车身指南确认：3-T Bus 的短轴代码为 `906.711`、中轴代码为 `906.713`；`224` 仅对应中轴，`211 CDI` 与 `215 CDI` 同时覆盖短轴和中轴。两种车身均有标准顶和高顶分支。([DIY Sprinter][1])
* 这些外廓与已建立的 Sprinter Bus 尺寸组完全一致，本轮全部直接复用，不新增尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：84
* READY 映射：257
* PENDING Ktype：16
* 已确认尺寸组：101
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19635_mwb_lowroof	19635	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19635_mwb_highroof	19635	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19641_swb_lowroof	19641	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19641_swb_highroof	19641	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19641_mwb_lowroof	19641	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19641_mwb_highroof	19641	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19646_swb_lowroof	19646	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19646_swb_highroof	19646	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19646_mwb_lowroof	19646	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19646_mwb_highroof	19646	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中关闭 Sprinter 3-T、3.5-T、5-T 的 15 个 Pritsche/Fahrgestell Ktype，按单排/双排驾驶室和轴距批量建组、复用。
2. 最后关闭 VW Transporter T5 Pritsche/Fahrgestell。
3. 完成后执行一次机械闭合检查，并在 `PENDING=0` 的下一轮直接输出两张最终完整 TSV 与指定下载文件。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "Body/Equipment Mounting Directives for Sprinter Model ..."


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **3.5-T 与 5-T Pritsche/Fahrgestell** 共 9 个 Ktype。
* 3.5-T 按 `906.131/133/135` 单排驾驶室和 `906.231/233/235` 双排驾驶室拆分；5-T 按 `906.153/155` 与 `906.253/255` 拆分。车身长度采用 Mercedes-Benz 车身制造指南，驾驶室高度采用同代官方 Sprinter 车型资料。
* 本轮新增 44 条 READY 映射和 10 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：93
* READY 映射：301
* PENDING Ktype：7
* 已确认尺寸组：111
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19658_mwb_singlecab	19658	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19658_mwb_doublecab	19658	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19658_lwb_singlecab	19658	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19658_lwb_doublecab	19658	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19659_swb_singlecab	19659	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19659_swb_doublecab	19659	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19659_mwb_singlecab	19659	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19659_mwb_doublecab	19659	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19659_lwb_singlecab	19659	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19659_lwb_doublecab	19659	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19660_swb_singlecab	19660	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19660_swb_doublecab	19660	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19660_mwb_singlecab	19660	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19660_mwb_doublecab	19660	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19660_lwb_singlecab	19660	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19660_lwb_doublecab	19660	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19662_swb_singlecab	19662	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19662_swb_doublecab	19662	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19662_mwb_singlecab	19662	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19662_mwb_doublecab	19662	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19662_lwb_singlecab	19662	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19662_lwb_doublecab	19662	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19664_swb_singlecab	19664	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19664_swb_doublecab	19664	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19664_mwb_singlecab	19664	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19664_mwb_doublecab	19664	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19664_lwb_singlecab	19664	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19664_lwb_doublecab	19664	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19668_mwb_singlecab	19668	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19668_mwb_doublecab	19668	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19668_lwb_singlecab	19668	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19668_lwb_doublecab	19668	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19670_mwb_singlecab	19670	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19670_mwb_doublecab	19670	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19670_lwb_singlecab	19670	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19670_lwb_doublecab	19670	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19672_mwb_singlecab	19672	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19672_mwb_doublecab	19672	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19672_lwb_singlecab	19672	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19672_lwb_doublecab	19672	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19674_mwb_singlecab	19674	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19674_mwb_doublecab	19674	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19674_lwb_singlecab	19674	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19674_lwb_doublecab	19674	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	5305	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	5305	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	5870	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	5870	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	6680	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	6680	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	6085	1993	2385	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	6085	1993	2405	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	6845	1993	2385	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	6845	1993	2405	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
```

## 下一步优先处理

1. 关闭剩余 6 个 Sprinter 3-T Pritsche/Fahrgestell Ktype，解决 3-T 单排/双排驾驶室的独立高度口径。
2. 关闭 VW Transporter T5 Pritsche/Fahrgestell 的单排、双排及原厂货台分支。
3. 达到 `PENDING=0` 后，仅进行一次机械闭合检查并直接输出最终两张完整 TSV 和指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 已关闭 Sprinter W906 **3-T Pritsche/Fahrgestell** 的 6 个 Ktype。
* Mercedes-Benz 车身指南确认：3-T 单排驾驶室代码为 `906.111/906.113`，双排驾驶室代码为 `906.211/906.213`；`224` 仅覆盖中轴，其余 209/211/213/215/218 CDI 覆盖短轴和中轴。([DIY Sprinter][1])
* 官方车身图所示 3-T 与已建 3.5-T 对应驾驶室具有相同外部长度和驾驶室几何边界，因此本轮复用现有 4 个尺寸组，没有重复建组。此处是依据官方车型图作出的同外廓判断。([DIY Sprinter][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：99
* READY 映射：323
* PENDING Ktype：1
* 已确认尺寸组：111
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19637_mwb_singlecab	19637	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19637_mwb_doublecab	19637	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19640_swb_singlecab	19640	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19640_swb_doublecab	19640	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19640_mwb_singlecab	19640	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19640_mwb_doublecab	19640	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19643_swb_singlecab	19643	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19643_swb_doublecab	19643	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19643_mwb_singlecab	19643	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19643_mwb_doublecab	19643	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19645_swb_singlecab	19645	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19645_swb_doublecab	19645	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19645_mwb_singlecab	19645	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19645_mwb_doublecab	19645	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19648_swb_singlecab	19648	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19648_swb_doublecab	19648	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19648_mwb_singlecab	19648	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19648_mwb_doublecab	19648	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19650_swb_singlecab	19650	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19650_swb_doublecab	19650	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19650_mwb_singlecab	19650	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19650_mwb_doublecab	19650	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 关闭最后的 Ktype `19629`：VW Transporter T5 Pritsche/Fahrgestell。
2. 从官方 Chassis Cab 资料锁定长轴单排、长轴双排的裸底盘外廓，以及该 75 kW 动力实际提供的分支。
3. PENDING 清零后立即进行一次机械闭合检查，并输出两张最终完整 TSV、两个指定下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf?utm_source=chatgpt.com "ABR.boo"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* 最后一个 Ktype `19629` 已关闭，拆分为 T5 长轴单排与双排底盘驾驶室。
* 已完成一次机械收尾检查：固定表头、主键唯一、映射引用闭合、尺寸及来源完整、下载文件名均通过。
* 当前批次已达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：325
* PENDING：0
* DIMENSION_GROUP：113
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19582_l1h1	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
19582_l2h1	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
19582_l2h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
19582_l3h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
19582_l3h3	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
19582_l4h2	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H2-01	HIGH	L4H2厢式车外廓。	READY
19582_l4h3	19582	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H3-01	HIGH	L4H3厢式车外廓。	READY
19583_l3h2	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
19583_l3h3	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
19583_l4h2	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H2-01	HIGH	L4H2厢式车外廓。	READY
19583_l4h3	19583	Van	Jumper III			EU-CITROEN-JUMPER-III-VAN-L4H3-01	HIGH	L4H3厢式车外廓。	READY
19584_l1	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	HIGH	L1单排底盘驾驶室。	READY
19584_l2	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19584_l2s	19584	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19585_l1	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	HIGH	L1单排底盘驾驶室。	READY
19585_l2	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19585_l2s	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19585_l3	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	HIGH	L3单排底盘驾驶室。	READY
19585_l4	19585	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	MEDIUM	L4单排底盘驾驶室。	READY
19586_swb_lowroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	HIGH	前驱短轴低顶厢式车。	READY
19586_swb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	HIGH	前驱短轴中顶厢式车。	READY
19586_mwb_lowroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	HIGH	前驱中轴低顶厢式车。	READY
19586_mwb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱中轴中顶厢式车。	READY
19586_mwb_highroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	HIGH	前驱中轴高顶厢式车。	READY
19586_lwb_medroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	HIGH	前驱长轴中顶厢式车。	READY
19586_lwb_highroof	19586	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	HIGH	前驱长轴高顶厢式车。	READY
19587_l2	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	HIGH	L2单排底盘驾驶室。	READY
19587_l2s	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	HIGH	L2S单排底盘驾驶室。	READY
19587_l3	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	HIGH	L3单排底盘驾驶室。	READY
19587_l4	19587	Pickup	Jumper III		2	EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	HIGH	L4单排底盘驾驶室。	READY
19588_swb_lowroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	HIGH	后驱短轴低顶厢式车。	READY
19588_swb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	HIGH	后驱短轴中顶厢式车。	READY
19588_mwb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	HIGH	后驱中轴中顶厢式车。	READY
19588_mwb_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	HIGH	后驱中轴高顶厢式车。	READY
19588_lwb_medroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱长轴中顶厢式车。	READY
19588_lwb_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	HIGH	后驱长轴高顶厢式车。	READY
19588_jumbo_srw_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	HIGH	后驱加长轴高顶单后轮车身。	READY
19588_jumbo_drw_highroof	19588	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	HIGH	后驱加长轴高顶双后轮宽体车身。	READY
19589_swb_lowroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	HIGH	后驱短轴低顶厢式车。	READY
19589_swb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	HIGH	后驱短轴中顶厢式车。	READY
19589_mwb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	HIGH	后驱中轴中顶厢式车。	READY
19589_mwb_highroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	HIGH	后驱中轴高顶厢式车。	READY
19589_lwb_medroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱长轴中顶厢式车。	READY
19589_lwb_highroof	19589	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	HIGH	后驱长轴高顶厢式车。	READY
19590_mwb_medroof	19590	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	MEDIUM	前驱9/12座中轴中顶Minibus外廓。	READY
19591_mwb_medroof	19591	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱9/12座中轴中顶Minibus外廓。	READY
19592_mwb_medroof	19592	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	HIGH	前驱9/12座中轴中顶Minibus外廓。	READY
19593_lwb_medroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	HIGH	后驱15座长轴中顶Minibus外廓。	READY
19593_jumbo_drw_medroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	HIGH	后驱17座加长轴中顶双后轮外廓。	READY
19593_jumbo_drw_highroof	19593	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	HIGH	后驱17座加长轴高顶双后轮外廓。	READY
19594	19594	MPV	Combo Tour C facelift 2003		5	EU-OPEL-COMBO-C-TOUR-MPV-01	HIGH	五门乘用型Combo Tour C。	READY
19595	19595	Van	Combo C facelift 2003			EU-OPEL-COMBO-C-TOUR-MPV-01	MEDIUM	输入类别合并厢式与乘用型车身；外部标准车身边界一致。	READY
19596_swb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	MEDIUM	后驱短轴单排底盘驾驶室。	READY
19596_mwb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	后驱中轴单排底盘驾驶室。	READY
19596_mwb_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	MEDIUM	后驱中轴双排底盘驾驶室。	READY
19596_lwb_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	MEDIUM	后驱长轴单排底盘驾驶室。	READY
19596_lwb_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	后驱长轴双排底盘驾驶室。	READY
19596_ef_singlecab	19596	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	后驱加长车架单排底盘驾驶室。	READY
19596_ef_doublecab	19596	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	MEDIUM	后驱加长车架双排底盘驾驶室。	READY
19597_swb_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19597_mwb_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19597_ef_singlecab	19597	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19598_swb_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19598_mwb_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19598_ef_singlecab	19598	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19599_swb_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	前驱短轴单排底盘驾驶室。	READY
19599_mwb_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	前驱中轴单排底盘驾驶室。	READY
19599_ef_singlecab	19599	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	前驱加长车架单排底盘驾驶室。	READY
19600_swb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19600_mwb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19600_mwb_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19600_lwb_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19600_lwb_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19600_ef_singlecab	19600	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19600_ef_doublecab	19600	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
19601_swb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19601_mwb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19601_mwb_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19601_lwb_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19601_lwb_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19601_ef_singlecab	19601	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19601_ef_doublecab	19601	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
19602_swb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	HIGH	后驱短轴单排底盘驾驶室。	READY
19602_mwb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	HIGH	后驱中轴单排底盘驾驶室。	READY
19602_mwb_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	后驱中轴双排底盘驾驶室。	READY
19602_lwb_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	HIGH	后驱长轴单排底盘驾驶室。	READY
19602_lwb_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	后驱长轴双排底盘驾驶室。	READY
19602_ef_singlecab	19602	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	HIGH	后驱加长车架单排底盘驾驶室。	READY
19602_ef_doublecab	19602	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	HIGH	后驱加长车架双排底盘驾驶室。	READY
19603	19603	Sedan	Epica	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250四门轿车。	READY
19604	19604	Sedan	Epica	V250	4	EU-CHEVROLET-EPICA-V250-SEDAN-01	HIGH	V250四门轿车。	READY
19605	19605	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH	J200五门SUV。	READY
19606	19606	Convertible	350Z	Z33	2	EU-NISSAN-350Z-Z33-CONVERTIBLE-PREFL-01	HIGH	Z33改款前双门Roadster。	READY
19611	19611	SUV	Santa Fe I	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	HIGH	SM五门SUV。	READY
19612_3dr	19612	Hatchback	Yaris I facelift 2003	XP10	3	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	MEDIUM	150 hp TS Turbo三门外廓。	READY
19612_5dr	19612	Hatchback	Yaris I facelift 2003	XP10	5	EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	MEDIUM	150 hp TS Turbo五门外廓。	READY
19613	19613	Convertible	Azure II		2	EU-BENTLEY-AZURE-II-CONVERTIBLE-01	HIGH	Azure II双门敞篷车。	READY
19614_prefl	19614	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8P三门改款前外廓。	READY
19614_facelift	19614	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8P三门改款后外廓。	READY
19615_prefl	19615	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8P三门改款前外廓。	READY
19615_facelift	19615	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8P三门改款后外廓。	READY
19616_prefl	19616	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款前外廓。	READY
19616_facelift	19616	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款后外廓。	READY
19617_prefl	19617	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款前外廓。	READY
19617_facelift	19617	Hatchback	A3 II	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype跨越2008改款；本行为8PA五门改款后外廓。	READY
19618	19618	Van	Combo C facelift 2003			EU-OPEL-COMBO-C-TOUR-MPV-01	MEDIUM	输入类别合并厢式与乘用型车身；外部标准车身边界一致。	READY
19619	19619	MPV	Combo Tour C facelift 2003		5	EU-OPEL-COMBO-C-TOUR-MPV-01	HIGH	五门乘用型Combo Tour C。	READY
19620	19620	SUV	Sportage II	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-01	HIGH	KM五门SUV。	READY
19621	19621	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH	标准轴距4E四门轿车。	READY
19622	19622	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-01	HIGH	标准轴距4E四门轿车。	READY
19623	19623	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	HIGH	140 hp前驱五门外廓。	READY
19624	19624	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	HIGH	140 hp四驱版与前驱版三维一致。	READY
19625_klh18	19625	Van	Hiace IV XH10	KLH18		EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	HIGH	KLH18标准车身厢式车。	READY
19625_klh28	19625	Van	Hiace IV XH10	KLH28		EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	HIGH	KLH28加长车身厢式车。	READY
19626	19626	MPV	Multivan T5		5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH	标准轴距标准顶乘用型车身。	READY
19627_swb_lowroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	MEDIUM	短轴标准顶Bus外廓。	READY
19627_swb_medroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	MEDIUM	短轴中顶Bus外廓。	READY
19627_lwb_lowroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	MEDIUM	长轴标准顶Bus外廓。	READY
19627_lwb_medroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
19627_lwb_highroof	19627	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
19628_swb_lowroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19628_swb_medroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	HIGH	短轴中顶厢式车。	READY
19628_lwb_lowroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	HIGH	长轴标准顶厢式车。	READY
19628_lwb_medroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	HIGH	长轴中顶厢式车。	READY
19628_lwb_highroof	19628	Van	Transporter T5			EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19629_lwb_singlecab	19629	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19629_lwb_doublecab	19629	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19630	19630	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
19631	19631	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH	3C2四门轿车。	READY
19632	19632	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH	3C5五门旅行车。	READY
19633	19633	Wagon	407 SW Phase I		5	EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	HIGH	五门旅行车。	READY
19634_prefl	19634	MPV	Touran I	1T	5	EU-VW-TOURAN-I-MPV-PREFL-01	HIGH	Ktype跨越2006改款；本行为改款前外廓。	READY
19634_facelift	19634	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	Ktype跨越2006改款；本行为改款后外廓。	READY
19635_mwb_lowroof	19635	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19635_mwb_highroof	19635	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19636_swb_lowroof	19636	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19636_swb_highroof	19636	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19636_mwb_lowroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19636_mwb_highroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19636_mwb_superhighroof	19636	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19637_mwb_singlecab	19637	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19637_mwb_doublecab	19637	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19638	19638	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	标准Touran MPV外廓。	READY
19639_swb_lowroof	19639	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19639_swb_highroof	19639	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19639_mwb_lowroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19639_mwb_highroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19639_mwb_superhighroof	19639	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19640_swb_singlecab	19640	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19640_swb_doublecab	19640	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19640_mwb_singlecab	19640	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19640_mwb_doublecab	19640	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19641_swb_lowroof	19641	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19641_swb_highroof	19641	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19641_mwb_lowroof	19641	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19641_mwb_highroof	19641	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19642_swb_lowroof	19642	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19642_swb_highroof	19642	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19642_mwb_lowroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19642_mwb_highroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19642_mwb_superhighroof	19642	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19643_swb_singlecab	19643	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19643_swb_doublecab	19643	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19643_mwb_singlecab	19643	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19643_mwb_doublecab	19643	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19644_swb_lowroof	19644	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19644_swb_highroof	19644	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19644_mwb_lowroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19644_mwb_highroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19644_mwb_superhighroof	19644	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19645_swb_singlecab	19645	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19645_swb_doublecab	19645	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19645_mwb_singlecab	19645	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19645_mwb_doublecab	19645	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19646_swb_lowroof	19646	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19646_swb_highroof	19646	MPV	Sprinter W906	906.711		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19646_mwb_lowroof	19646	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19646_mwb_highroof	19646	MPV	Sprinter W906	906.713		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19647_swb_lowroof	19647	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19647_swb_highroof	19647	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19647_mwb_lowroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19647_mwb_highroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19647_mwb_superhighroof	19647	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19648_swb_singlecab	19648	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19648_swb_doublecab	19648	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19648_mwb_singlecab	19648	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19648_mwb_doublecab	19648	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19649_swb_lowroof	19649	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式车。	READY
19649_swb_highroof	19649	Van	Sprinter W906	906.611		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式车。	READY
19649_mwb_lowroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	MEDIUM	中轴标准顶厢式车。	READY
19649_mwb_highroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	MEDIUM	中轴高顶厢式车。	READY
19649_mwb_superhighroof	19649	Van	Sprinter W906	906.613		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	MEDIUM	中轴超高顶厢式车。	READY
19650_swb_singlecab	19650	Pickup	Sprinter W906	906.111	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排3-T底盘驾驶室。	READY
19650_swb_doublecab	19650	Pickup	Sprinter W906	906.211	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排3-T底盘驾驶室。	READY
19650_mwb_singlecab	19650	Pickup	Sprinter W906	906.113	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排3-T底盘驾驶室。	READY
19650_mwb_doublecab	19650	Pickup	Sprinter W906	906.213	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排3-T底盘驾驶室。	READY
19651	19651	MPV	Touran I facelift 2006	1T	5	EU-VW-TOURAN-I-MPV-FACELIFT-02	HIGH	1.4 TSI对应独立的facelift外廓分支。	READY
19652_mwb_lowroof	19652	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19652_mwb_highroof	19652	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19652_lwb_highroof	19652	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19653_swb_lowroof	19653	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19653_swb_highroof	19653	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19653_mwb_lowroof	19653	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19653_mwb_highroof	19653	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19653_lwb_highroof	19653	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19654_swb_lowroof	19654	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	HIGH	短轴标准顶Bus外廓。	READY
19654_swb_highroof	19654	MPV	Sprinter W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	HIGH	短轴高顶Bus外廓。	READY
19654_mwb_lowroof	19654	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	HIGH	中轴标准顶Bus外廓。	READY
19654_mwb_highroof	19654	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶Bus外廓。	READY
19654_lwb_highroof	19654	MPV	Sprinter W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	HIGH	长轴高顶Bus外廓。	READY
19655_mwb_lowroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19655_mwb_highroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19655_mwb_superhighroof	19655	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
19655_lwb_superhighroof	19655	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19655_exl_highroof	19655	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	HIGH	加长车身高顶厢式车。	READY
19655_exl_superhighroof	19655	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长车身超高顶厢式车。	READY
19656_swb_lowroof	19656	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19656_swb_highroof	19656	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
19656_mwb_lowroof	19656	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19656_mwb_highroof	19656	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19656_lwb_highroof	19656	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19656_lwb_superhighroof	19656	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19657_mwb_lowroof	19657	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19657_mwb_highroof	19657	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19657_lwb_highroof	19657	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19657_lwb_superhighroof	19657	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19657_exl_highroof	19657	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	HIGH	加长车身高顶厢式车。	READY
19657_exl_superhighroof	19657	Van	Sprinter W906	906.637		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长车身超高顶厢式车。	READY
19658_mwb_singlecab	19658	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19658_mwb_doublecab	19658	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19658_lwb_singlecab	19658	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19658_lwb_doublecab	19658	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19659_swb_singlecab	19659	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19659_swb_doublecab	19659	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19659_mwb_singlecab	19659	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19659_mwb_doublecab	19659	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19659_lwb_singlecab	19659	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19659_lwb_doublecab	19659	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19660_swb_singlecab	19660	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19660_swb_doublecab	19660	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19660_mwb_singlecab	19660	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19660_mwb_doublecab	19660	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19660_lwb_singlecab	19660	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19660_lwb_doublecab	19660	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19661_swb_lowroof	19661	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
19661_swb_highroof	19661	Van	Sprinter W906	906.631		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
19661_mwb_lowroof	19661	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19661_mwb_highroof	19661	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19662_swb_singlecab	19662	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19662_swb_doublecab	19662	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19662_mwb_singlecab	19662	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19662_mwb_doublecab	19662	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19662_lwb_singlecab	19662	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19662_lwb_doublecab	19662	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19663_mwb_lowroof	19663	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
19663_mwb_highroof	19663	Van	Sprinter W906	906.633		EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
19663_lwb_highroof	19663	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
19663_lwb_superhighroof	19663	Van	Sprinter W906	906.635		EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
19664_swb_singlecab	19664	Pickup	Sprinter W906	906.131	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	HIGH	短轴单排底盘驾驶室。	READY
19664_swb_doublecab	19664	Pickup	Sprinter W906	906.231	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	HIGH	短轴双排底盘驾驶室。	READY
19664_mwb_singlecab	19664	Pickup	Sprinter W906	906.133	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	HIGH	中轴单排底盘驾驶室。	READY
19664_mwb_doublecab	19664	Pickup	Sprinter W906	906.233	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排底盘驾驶室。	READY
19664_lwb_singlecab	19664	Pickup	Sprinter W906	906.135	2	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	HIGH	长轴单排底盘驾驶室。	READY
19664_lwb_doublecab	19664	Pickup	Sprinter W906	906.235	4	EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排底盘驾驶室。	READY
19665_mwb_medroof	19665	MPV	Interstar I	X70		EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	MEDIUM	中轴中顶乘用型车身。	READY
19666_prefl	19666	MPV	Caddy III	2K		EU-VW-CADDY-III-MPV-PREFL-01	HIGH	Ktype跨越2010改款；本行为改款前标准轴距车身。	READY
19666_facelift	19666	MPV	Caddy III facelift 2010	2K	5	EU-VW-CADDY-III-MPV-FACELIFT-01	HIGH	Ktype跨越2010改款；本行为改款后标准轴距车身。	READY
19667_mwb_lowroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19667_mwb_highroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19667_mwb_superhighroof	19667	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19667_lwb_highroof	19667	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19667_lwb_superhighroof	19667	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19667_exl_highroof	19667	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19667_exl_superhighroof	19667	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19668_mwb_singlecab	19668	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19668_mwb_doublecab	19668	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19668_lwb_singlecab	19668	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19668_lwb_doublecab	19668	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19669_mwb_lowroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19669_mwb_highroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19669_mwb_superhighroof	19669	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19669_lwb_highroof	19669	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19669_lwb_superhighroof	19669	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19669_exl_highroof	19669	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19669_exl_superhighroof	19669	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19670_mwb_singlecab	19670	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19670_mwb_doublecab	19670	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19670_lwb_singlecab	19670	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19670_lwb_doublecab	19670	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19671_mwb_lowroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19671_mwb_highroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19671_mwb_superhighroof	19671	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19671_lwb_highroof	19671	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19671_lwb_superhighroof	19671	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19671_exl_highroof	19671	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19671_exl_superhighroof	19671	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19672_mwb_singlecab	19672	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19672_mwb_doublecab	19672	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19672_lwb_singlecab	19672	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19672_lwb_doublecab	19672	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19673_mwb_lowroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶5-T厢式车。	READY
19673_mwb_highroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶5-T厢式车。	READY
19673_mwb_superhighroof	19673	Van	Sprinter W906	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶5-T厢式车。	READY
19673_lwb_highroof	19673	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶5-T厢式车。	READY
19673_lwb_superhighroof	19673	Van	Sprinter W906	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶5-T厢式车。	READY
19673_exl_highroof	19673	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	HIGH	加长轴高顶5-T厢式车。	READY
19673_exl_superhighroof	19673	Van	Sprinter W906	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	HIGH	加长轴超高顶5-T厢式车。	READY
19674_mwb_singlecab	19674	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	HIGH	中轴单排5-T底盘驾驶室。	READY
19674_mwb_doublecab	19674	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	HIGH	中轴双排5-T底盘驾驶室。	READY
19674_lwb_singlecab	19674	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	HIGH	长轴单排5-T底盘驾驶室。	READY
19674_lwb_doublecab	19674	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	HIGH	长轴双排5-T底盘驾驶室。	READY
19675	19675	MPV	Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	HIGH	标准轴距Espace，非Grand Espace。	READY
19676	19676	Sedan	Thalia I facelift 2002		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	MEDIUM	四门轿车。	READY
19677	19677	Sedan	Thalia I facelift 2002		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	MEDIUM	四门轿车。	READY
19678	19678	Convertible	Megane II CC Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷车。	READY
19679	19679	Hatchback	C5 I Phase II		5	EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	HIGH	五门掀背式车身。	READY
19680	19680	Wagon	C5 I Break Phase II		5	EU-CITROEN-C5-I-PHASE-II-WAGON-01	HIGH	五门旅行车。	READY
19681	19681	MPV	C8 I		5	EU-CITROEN-C8-I-MPV-01	HIGH	五门大型MPV。	READY
19682	19682	Hatchback	C2 I		3	EU-CITROEN-C2-I-HATCHBACK-3D-01	HIGH	三门掀背车；改款前后该动力外廓尺寸一致。	READY
19683_prefl	19683	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	MEDIUM	Ktype跨越2004改款；本行为五门改款前外廓。	READY
19683_facelift	19683	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越2004改款；本行为五门改款后外廓。	READY
19684_gaz24	19684	Sedan	Volga GAZ-24	GAZ-24	4	EU-GAZ-VOLGA-GAZ-24-SEDAN-01	HIGH	Ktype跨越车型更新；本行为GAZ-24四门轿车。	READY
19684_gaz2410	19684	Sedan	Volga GAZ-24-10	GAZ-24-10	4	EU-GAZ-VOLGA-GAZ-24-10-SEDAN-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-10四门轿车。	READY
19685_gaz2402	19685	Wagon	Volga GAZ-24-02	GAZ-24-02	5	EU-GAZ-VOLGA-GAZ-24-02-WAGON-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-02旅行车。	READY
19685_gaz2412	19685	Wagon	Volga GAZ-24-12	GAZ-24-12	5	EU-GAZ-VOLGA-GAZ-24-12-WAGON-01	HIGH	Ktype跨越车型更新；本行为GAZ-24-12旅行车。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_401-500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-III-VAN-L1H1-01	4963	2050	2254	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L2H1-01	5413	2050	2254	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L2H2-01	5413	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L3H2-01	5998	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L3H3-01	5998	2050	2764	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L4H2-01	6363	2050	2524	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-VAN-L4H3-01	6363	2050	2764	Citroën New Relay 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-Relay-UK.pdf
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L1-01	4908	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2-01	5358	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L2S-01	5708	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L3-01	5943	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-CITROEN-JUMPER-III-CHASSIS-CAB-L4-01	6208	2050	2153	Citroën Jumper 2008.5 Owner's Manual	https://www.carmanualsonline.info/citroen-jumper-2008-5-2-g-owner-s-manual/?srch=dimensions
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	5230	1974	2047	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	5230	1974	2594	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	5680	1974	2381	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	5680	1974	2590	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	5230	1974	2397	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	5230	1974	2611	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	5680	1974	2394	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	5680	1974	2606	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	6403	1974	2624	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	6403	2008	2624	Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380	Ford People Movers 2007 official brochure; Ford People Movers 2012 official brochure; Ford Transit Van 2007 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2012-Ford-People-Movers-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf
EU-OPEL-COMBO-C-TOUR-MPV-01	4322	1684	1801	Auto-Data Opel Combo Tour C 1.3 CDTI 75 Hp; Auto-Data Opel Combo Tour C 1.6 CNG 94 Hp ecoFLEX	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.3-cdti-75hp-25825;https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.6-cng-94hp-ecoflex-25842
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025	Ford Transit Chassis Cab 2007 official brochure; Ford Transit Cab Chassis 2012 official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Chassis-Cab-V1-UK.pdf;https://xr793.com/wp-content/uploads/2024/03/2012-Ford-Transit-Chassis-Cab-AUS.pdf
EU-CHEVROLET-EPICA-V250-SEDAN-01	4805	1810	1450	Auto-Data Chevrolet Epica generation	https://www.auto-data.net/en/chevrolet-epica-generation-3201
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740	Auto-Data Daihatsu Terios II J200	https://www.auto-data.net/en/daihatsu-terios-ii-j200-1.5-i-16v-4wd-105hp-42
EU-NISSAN-350Z-Z33-CONVERTIBLE-PREFL-01	4310	1815	1328	Auto-Data Nissan 350Z Roadster Z33	https://www.auto-data.net/en/nissan-350z-roadster-z33-generation-173
EU-HYUNDAI-SANTA-FE-I-SM-SUV-01	4500	1820	1730	Auto-Data Hyundai Santa Fe I SM	https://www.auto-data.net/en/hyundai-santa-fe-i-sm-generation-2972
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3660	1660	1500	Auto-Data Toyota Yaris I facelift 2003 3-door	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-3-door-generation-9796
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3660	1660	1470	Auto-Data Toyota Yaris I facelift 2003 5-door TS 1.5 Turbo	https://www.auto-data.net/en/toyota-yaris-i-facelift-2003-5-door-ts-1.5-turbo-150hp-50713
EU-BENTLEY-AZURE-II-CONVERTIBLE-01	5400	1910	1485	Auto-Data Bentley Azure II 6.7 i V8 457 Hp Automatic	https://www.auto-data.net/en/bentley-azure-ii-6.7-i-v8-457hp-automatic-6765
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-generation-8936
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 8P facelift 2008	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-generation-5194
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA	https://www.auto-data.net/en/audi-a3-sportback-8pa-generation-1067
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423	Auto-Data Audi A3 Sportback 8PA facelift 2008	https://www.auto-data.net/en/audi-a3-sportback-8pa-facelift-2008-generation-5196
EU-KIA-SPORTAGE-II-KM-SUV-01	4350	1840	1730	Auto-Data Kia Sportage II 2.0 CRDi 140	https://www.auto-data.net/en/kia-sportage-ii-2.0-crdi-140hp-2720
EU-AUDI-A8-D3-4E-SEDAN-01	5062	1894	1444	Auto-Data Audi A8 D3 4.2 BiTDI; Auto-Data Audi A8 D3 4.2 FSI	https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2005-4.2-bitdi-v8-326hp-quattro-dpf-tiptronic-4819;https://www.auto-data.net/en/audi-a8-d3-4e-facelift-2005-4.2-fsi-v8-350hp-quattro-tiptronic-43762
EU-HYUNDAI-TUCSON-I-JM-SUV-140HP-01	4325	1830	1730	Auto-Data Hyundai Tucson I CRDi 140 FWD; Auto-Data Hyundai Tucson I CRDi 140 4WD	https://www.auto-data.net/en/hyundai-tucson-i-2.0-16v-crdi-140hp-13763;https://www.auto-data.net/en/hyundai-tucson-i-2.0-16v-crdi-4wd-140hp-automatic-24830
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	4715	1800	1955	Drom Toyota Hiace KLH18 body specifications	https://www.drom.ru/catalog/toyota/frame/klh18/
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	5160	1800	1955	Drom Toyota Hiace KLH28 body specifications	https://www.drom.ru/catalog/toyota/frame/klh28/
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Volkswagen Multivan 2006 official brochure	https://xr793.com/wp-content/uploads/2023/07/2006-VW-Multivan-AUS.pdf
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter Van 2008 official brochure	https://xr793.com/wp-content/uploads/2023/07/2008-VW-Transporter-AUS.pdf
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963	Volkswagen Chassis and Double Cabs 2009 official brochure	https://xr793.com/wp-content/uploads/2023/07/2009-VW-Chassis-Cabs-UK.pdf
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949	Volkswagen Chassis and Double Cabs 2009 official brochure	https://xr793.com/wp-content/uploads/2023/07/2009-VW-Chassis-Cabs-UK.pdf
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 FSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-fsi-150hp-4motion-8881
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-tdi-16v-140hp-pde-4motion-8895
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486	Auto-Data Peugeot 407 SW 2.2 HDI 170 Hp	https://www.auto-data.net/en/peugeot-407-sw-2.2-hdi-170hp-37702
EU-VW-TOURAN-I-MPV-PREFL-01	4391	1794	1635	Auto-Data Volkswagen Touran I 2.0 TDI 170 Hp DPF	https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-170hp-dpf-57149
EU-VW-TOURAN-I-MPV-FACELIFT-01	4407	1794	1635	Auto-Data Volkswagen Touran I facelift 2006 2.0 TDI 170 Hp	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-2.0-tdi-170hp-44607
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-LOWROOF-01	5910	1993	2485	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-MWB-HIGHROOF-01	5910	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-LOWROOF-01	5245	1993	2415	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-SWB-HIGHROOF-01	5245	1993	2700	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-LOWROOF-01	5910	1993	2415	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-HIGHROOF-01	5910	1993	2700	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-3T-VAN-MWB-SUPERHIGHROOF-01	5910	1993	2930	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Sprinter brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://www.yumpu.com/en/document/view/36058966/sprinter-brochure-pdf-mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-MWB-01	5870	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-MWB-01	5870	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-SWB-01	5305	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-SWB-01	5305	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-LOWROOF-01	5245	1993	2485	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-SWB-HIGHROOF-01	5245	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-VW-TOURAN-I-MPV-FACELIFT-02	4391	1794	1652	Auto-Data Volkswagen Touran I facelift 2006 1.4 TSI 140 Hp	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-1.4-tsi-140hp-8535
EU-MERCEDES-BENZ-SPRINTER-W906-35T-BUS-LWB-HIGHROOF-01	6945	1993	2770	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-SUPERHIGHROOF-01	6945	1993	2930	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-HIGHROOF-01	7345	1993	2700	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-EXL-SUPERHIGHROOF-01	7345	1993	2935	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-VAN-LWB-HIGHROOF-01	6945	1993	2700	Mercedes-Benz Van Range 2008 official brochure; Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-CAB-LWB-01	6680	1993	2350	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-35T-CHASSIS-DOUBLE-CAB-LWB-01	6680	1993	2360	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-NISSAN-INTERSTAR-I-X70-BUS-MWB-MEDROOF-01	5399	1990	2486	Nissan Interstar official brochure	https://www.carparisonleasing.co.uk/files/bb4/interstar.pdf
EU-VW-CADDY-III-MPV-PREFL-01	4405	1802	1833	Auto-Data Volkswagen Caddy III 2.0 EcoFuel 109 Hp CNG	https://www.auto-data.net/en/volkswagen-caddy-iii-2.0-ecofuel-109hp-cng-28338
EU-VW-CADDY-III-MPV-FACELIFT-01	4406	1794	1823	Auto-Data Volkswagen Caddy III facelift 2010 2.0 EcoFuel 109 Hp	https://www.auto-data.net/en/volkswagen-caddy-iii-facelift-2010-2.0-109hp-ecofuel-20527
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-LOWROOF-01	5910	1993	2510	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-HIGHROOF-01	5910	1993	2795	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-MWB-SUPERHIGHROOF-01	5910	1993	3030	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-HIGHROOF-01	6945	1993	2795	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-LWB-SUPERHIGHROOF-01	6945	1993	3025	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-HIGHROOF-01	7345	1993	2800	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-VAN-EXL-SUPERHIGHROOF-01	7345	1993	3030	Mercedes-Benz Finland Sprinter closed-van body dimensions 2015	https://doczz.net/doc/7059254/sprinter-paketti--ja-kuorma-autoumpimallin---mercedes-benz
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-MWB-01	6085	1993	2385	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-MWB-01	6085	1993	2405	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-CAB-LWB-01	6845	1993	2385	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-5T-CHASSIS-DOUBLE-CAB-LWB-01	6845	1993	2405	Mercedes-Benz Sprinter Body/Equipment Mounting Directives 2006; Mercedes-Benz Van Range 2008 official brochure	https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf;https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Van-Range-AUS.pdf
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	4656	1860	1728	Auto-Data Renault Espace IV Phase II 2.2 dCi 139 Hp	https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-2.2-dci-139hp-20260
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437	Auto-Data Renault Symbol I facelift 2002 generation	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-generation-2168
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II; Automobile-Catalog Renault Megane CC 1.5 dCi 105	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-generation-5609;https://www.automobile-catalog.com/car/2009/2955005/renault_megane_cc_1_5_dci_105.html
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4745	1780	1476	Auto-Data Citroen C5 I Phase II	https://www.auto-data.net/en/citroen-c5-i-phase-ii-2004-generation-5347
EU-CITROEN-C5-I-PHASE-II-WAGON-01	4839	1780	1511	Auto-Data Citroen C5 I Break Phase II	https://www.auto-data.net/en/citroen-c5-i-break-phase-ii-2004-generation-5346
EU-CITROEN-C8-I-MPV-01	4726	1854	1752	Citroën C8 technical information	https://www.citroenet.org.uk/passenger-cars/psa/c8/c8-14.html
EU-CITROEN-C2-I-HATCHBACK-3D-01	3666	1659	1474	Auto-Data Citroen C2 I Phase I 1.4i 16V; Auto-Data Citroen C2 I Phase II 1.4i 16V	https://www.auto-data.net/en/citroen-c2-i-phase-i-2003-1.4i-16v-88hp-sensodrive-stop-start-14987;https://www.auto-data.net/en/citroen-c2-i-phase-ii-2008-1.4i-16v-88hp-sensodrive-stop-start-27447
EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	5010	1930	1855	Auto-Data Nissan Patrol model specifications	https://www.auto-data.net/en/nissan-patrol-model-50
EU-NISSAN-PATROL-V-Y61-SUV-5D-FACELIFT-01	5080	1940	1855	Auto-Data Nissan Patrol model specifications	https://www.auto-data.net/en/nissan-patrol-model-50
EU-GAZ-VOLGA-GAZ-24-SEDAN-01	4735	1800	1490	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-10-SEDAN-01	4735	1800	1476	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-02-WAGON-01	4735	1800	1576	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GAZ-VOLGA-GAZ-24-12-WAGON-01	4735	1800	1576	Auto-Data GAZ 24 model specifications	https://www.auto-data.net/en/gaz-24-model-1467
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_401-500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_401-500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_401-500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（609 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（286 行）
