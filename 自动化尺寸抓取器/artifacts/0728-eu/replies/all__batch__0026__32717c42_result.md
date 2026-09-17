# 任务：all 第 2501-2600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0026__32717c42


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2501-2600 行

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
all 第 2501-2600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	124	1600 Sport	Cabriolet	Heckantrieb	Benzin	74	100	Nov 1969	Aug 1973	2024-03-01	2569
Fiat	124	1600 Sport	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1969	Dec 1974	2024-03-01	2570
Fiat	124	1800 Sport	Cabriolet	Heckantrieb	Benzin	87	118	Jan 1972	Dec 1977	2024-03-01	2571
Pininfarina	Spidereuropa	2000	Cabriolet	Heckantrieb	Benzin	76	103	Nov 1984	Nov 1985	2024-03-01	2572
Pininfarina	Spidereuropa	2000 Volumex	Cabriolet	Heckantrieb	Benzin	99	135	Jun 1983	Nov 1985	2024-03-01	2573
Fiat	128	1.1	Stufenheck	Frontantrieb	Benzin	33	45	Feb 1975	Sep 1981	2024-03-01	2574
Fiat	128	1.1	Stufenheck	Frontantrieb	Benzin	40	55	Mar 1969	Dec 1984	2024-03-01	2575
Fiat	128	1.3 Berlinetta	Coupe	Frontantrieb	Benzin	54	73	Jun 1975	Dec 1979	2024-03-01	2576
Fiat	128	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1974	Dec 1984	2024-03-01	2577
Fiat	Ritmo	1	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1978	Sep 1982	2024-03-01	2578
Fiat	Ritmo	1.1	Schrägheck	Frontantrieb	Benzin	40	55	Oct 1982	Dec 1987	2024-03-01	2579
Fiat	Ritmo	1.1	Schrägheck	Frontantrieb	Benzin	43	58	Apr 1985	Dec 1987	2024-03-01	2580
Fiat	Ritmo	1.3	Schrägheck	Frontantrieb	Benzin	48	65	Jan 1978	Aug 1985	2024-03-01	2581
Fiat	Ritmo	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Jan 1983	Apr 1985	2024-03-01	2582
Fiat	Ritmo	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1981	Sep 1982	2024-03-01	2583
Fiat	Ritmo	1.5	Schrägheck	Frontantrieb	Benzin	60	82	Jan 1983	Dec 1987	2024-03-01	2585
Fiat	Ritmo	1.5	Schrägheck	Frontantrieb	Benzin	63	85	Jan 1981	May 1987	2024-03-01	2586
Fiat	Ritmo	1.6	Schrägheck	Frontantrieb	Benzin	77	105	May 1981	Dec 1987	2024-03-01	2587
Abarth	Ritmo	130 TC 2.0	Schrägheck	Frontantrieb	Benzin	96	130	Apr 1983	Dec 1987	2024-03-01	2589
Fiat	Ritmo	1.7 Diesel	Schrägheck	Frontantrieb	Diesel	44	60	May 1985	Dec 1987	2024-03-01	2590
Fiat	Ritmo	1.7 Diesel	Schrägheck	Frontantrieb	Diesel	40	55	Oct 1979	Sep 1982	2024-03-01	2591
Fiat	Ritmo	1.9 TD	Schrägheck	Frontantrieb	Diesel	59	80	Dec 1985	Dec 1987	2024-03-01	2593
Fiat	Tipo	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Jul 1987	Dec 1989	2024-03-01	2594
Fiat	Tipo	1.9 TD	Schrägheck	Frontantrieb	Diesel	59	80	Mar 1992	Jun 1993	2024-03-01	2595
Fiat	Tipo	1.9 TD	Schrägheck	Frontantrieb	Diesel	66	90	Sep 1990	Apr 1995	2024-03-01	2596
Fiat	Tipo	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	51	70	May 1989	Apr 1995	2024-03-01	2597
Fiat	Tipo	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1992	Apr 1995	2024-03-01	2598
Fiat	Tipo	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	57	78	Jul 1990	Jan 1993	2024-03-01	2599
Fiat	Tipo	1.6 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1988	May 1991	2024-03-01	2600
Fiat	Tipo	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	76	103	Apr 1993	Apr 1995	2024-03-01	2601
Fiat	Tipo	2.0 I.e.	Schrägheck	Frontantrieb	Benzin	80	109	Jun 1990	Mar 1992	2024-03-01	2602
Fiat	Tipo	2.0 I.e.	Schrägheck	Frontantrieb	Benzin	83	113	Mar 1990	Apr 1995	2024-03-01	2603
Fiat	Tipo	2.0 I.e. 16V Sport	Schrägheck	Frontantrieb	Benzin	102	139	Mar 1993	Apr 1995	2024-03-01	2604
Fiat	Tipo	2.0 16V	Schrägheck	Frontantrieb	Benzin	107	146	Jul 1991	Apr 1995	2024-03-01	2605
Fiat	Regata	70 1.3	Stufenheck	Frontantrieb	Benzin	48	65	Sep 1983	Jul 1989	2024-03-01	2606
Fiat	Regata	85 1.5	Stufenheck	Frontantrieb	Benzin	58	79	May 1985	Dec 1987	2024-03-01	2608
Fiat	Regata	85 Super 1.5	Stufenheck	Frontantrieb	Benzin	60	82	Sep 1983	Apr 1985	2024-03-01	2609
Fiat	Regata	90 I.e. 1.6	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1987	Jul 1989	2024-03-01	2610
Fiat	Regata	100 Super 1.6	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1983	Dec 1990	2024-03-01	2611
Fiat	Regata	60 Diesel 1.7	Stufenheck	Frontantrieb	Diesel	44	60	May 1985	Mar 1989	2024-03-01	2612
Fiat	Regata	60 Diesel 1.7	Stufenheck	Frontantrieb	Diesel	43	58	Sep 1983	Dec 1986	2024-03-01	2613
Fiat	Regata	65 Diesel 1.9	Stufenheck	Frontantrieb	Diesel	48	65	Apr 1984	Jul 1989	2024-03-01	2614
Fiat	Regata	80 Turbo Diesel 1.9	Stufenheck	Frontantrieb	Diesel	59	80	May 1986	Jul 1989	2024-03-01	2615
Fiat	Regata	75 1.5	Kombi	Frontantrieb	Benzin	55	75	Sep 1984	Jul 1989	2024-03-01	2616
Fiat	Regata	90 I.e. 1.6	Kombi	Frontantrieb	Benzin	66	90	Jan 1987	Jul 1989	2024-03-01	2617
Fiat	Regata	65 Diesel 1.9	Kombi	Frontantrieb	Diesel	48	65	Apr 1984	Jul 1989	2024-03-01	2618
Fiat	Regata	80 Turbo Diesel 1.9	Kombi	Frontantrieb	Diesel	59	80	May 1986	Jul 1989	2024-03-01	2619
Fiat	131	1.3 Mirafiori	Stufenheck	Heckantrieb	Benzin	40	54	Oct 1974	Sep 1981	2024-03-01	2620
Hyundai	Ix20	1.6	Schrägheck	Frontantrieb	Benzin	92	125	Nov 2010	Jul 2019	2024-03-01	2621
Fiat	131	1.3 Super Mirafiori	Stufenheck	Heckantrieb	Benzin	57	78	Mar 1978	Dec 1980	2024-03-01	2622
Fiat	131	1.4 Mirafiori	Stufenheck	Heckantrieb	Benzin	51	70	Nov 1980	Jan 1984	2024-03-01	2623
Fiat	131	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Oct 1974	Sep 1981	2024-03-01	2624
Fiat	131	1.6	Stufenheck	Heckantrieb	Benzin	63	85	Nov 1976	Dec 1984	2024-03-01	2625
Fiat	131	1.6 Super	Stufenheck	Heckantrieb	Benzin	71	97	Mar 1978	Jan 1984	2024-03-01	2626
Fiat	131	2.0 Super	Stufenheck	Heckantrieb	Benzin	83	113	Jan 1981	Dec 1984	2024-03-01	2627
Fiat	131	2.0 Racing	Stufenheck	Heckantrieb	Benzin	85	115	Jun 1978	Dec 1981	2024-03-01	2628
Fiat	131	2.5 D	Stufenheck	Heckantrieb	Diesel	53	72	Jun 1978	Feb 1984	2024-03-01	2629
Fiat	131	1.6	Kombi	Heckantrieb	Benzin	63	85	Nov 1980	Dec 1984	2024-03-01	2630
Fiat	132	2	Stufenheck	Heckantrieb	Benzin	83	113	Jan 1976	Jun 1981	2024-03-01	2631
Fiat	Argenta	2000 I.e.	Stufenheck	Heckantrieb	Benzin	90	122	Jun 1981	Jul 1986	2024-03-01	2632
Fiat	Argenta	2500 Diesel	Stufenheck	Heckantrieb	Diesel	53	72	Jun 1981	Nov 1985	2024-03-01	2633
Fiat	X	1.3	Targa	Heckantrieb	Benzin	54	73	Oct 1975	Jun 1978	2024-05-01	2634
Fiat	X	1.3	Targa	Heckantrieb	Benzin	55	75	May 1973	Dec 1979	2024-05-01	2635
Fiat	X	1.5	Targa	Heckantrieb	Benzin	63	85	Nov 1978	Dec 1989	2024-05-01	2636
Fiat	Uno	45 0.9	Schrägheck	Frontantrieb	Benzin	33	45	Mar 1983	Sep 1992	2024-03-01	2637
Fiat	Uno	45 1.0	Schrägheck	Frontantrieb	Benzin	32	44	Jun 1986	Dec 1993	2024-03-01	2638
Fiat	Uno	55 1.1	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1983	Aug 1989	2024-03-01	2639
Fiat	Uno	60 1.1	Schrägheck	Frontantrieb	Benzin	43	58	May 1985	Aug 1989	2024-03-01	2640
Fiat	Uno	70 1.3	Schrägheck	Frontantrieb	Benzin	48	65	May 1985	Aug 1989	2024-03-01	2641
Fiat	Uno	70 1.3	Schrägheck	Frontantrieb	Benzin	50	68	Jan 1983	Apr 1985	2024-03-01	2642
Fiat	Uno	1.3 Turbo I.e.	Schrägheck	Frontantrieb	Benzin	73	99	Jan 1987	Dec 1987	2024-03-01	2643
Fiat	Uno	1.3 Turbo I.e.	Schrägheck	Frontantrieb	Benzin	77	105	Apr 1985	Aug 1989	2024-03-01	2644
Fiat	Uno	1.3 Super Diesel	Schrägheck	Frontantrieb	Diesel	33	45	Jun 1983	Mar 1992	2024-03-01	2645
Lancia	A 112	0.9 Junior	Schrägheck	Frontantrieb	Benzin	29	40	Mar 1981	Jun 1986	2024-03-01	2646
Fiat	Uno	60 Diesel 1.7	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1986	Aug 1989	2024-03-01	2647
Lancia	A 112	1.0 LX	Schrägheck	Frontantrieb	Benzin	35	48	Mar 1984	Dec 1986	2024-03-01	2648
Lancia	Y10	1.0 Fire	Schrägheck	Frontantrieb	Benzin	32	44	Jun 1985	Jun 1991	2024-03-01	2649
Fiat	Uno	60 Diesel 1.7	Schrägheck	Frontantrieb	Diesel	42	57	Sep 1989	Dec 1993	2024-03-01	2650
Lancia	Y10	1.0 Fire Catalytic-conv	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1987	Feb 1992	2024-03-01	2651
Lancia	Y10	1.3 I.e.	Schrägheck	Frontantrieb	Benzin	53	72	Feb 1989	Dec 1995	2024-03-01	2652
Fiat	Uno	50 1.1	Schrägheck	Frontantrieb	Benzin	37	50	Jan 1986	Dec 1989	2024-03-01	2653
Lancia	Y10	1.1 I.e. Fire	Schrägheck	Frontantrieb	Benzin	37	50	Jul 1989	Sep 1995	2024-03-01	2654
Fiat	Uno	50 I.e. 1.1	Schrägheck	Frontantrieb	Benzin	36	49	Jun 1992	Dec 1993	2024-03-01	2655
Lancia	Y10	1.1 I.e. Fire Allrad	Schrägheck	Allrad	Benzin	37	50	Sep 1992	Dec 1995	2024-03-01	2656
Fiat	Uno	1.3 Turbo I.e.	Schrägheck	Frontantrieb	Benzin	74	101	Sep 1989	Mar 1991	2024-03-01	2657
Fiat	Uno	70 I.e. 1.4	Schrägheck	Frontantrieb	Benzin	51	70	Sep 1989	Jul 1996	2024-03-01	2658
Lancia	Trevi	2000 I.e.	Stufenheck	Frontantrieb	Benzin	90	122	May 1980	Jan 1987	2024-03-01	2659
Lancia	Beta	2000 I.e.	Schrägheck	Frontantrieb	Benzin	90	122	May 1981	Sep 1984	2024-03-01	2660
Fiat	Uno	1.4 Turbo I.e.	Schrägheck	Frontantrieb	Benzin	82	112	Sep 1989	Sep 1993	2024-03-01	2661
Lancia	Prisma	1.5	Stufenheck	Frontantrieb	Benzin	63	86	Jan 1983	Apr 1986	2024-03-01	2662
Fiat	Uno	75 I.e. 1.5	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1985	Dec 1993	2024-03-01	2663
Lancia	Prisma	1.6 I.e. Super	Stufenheck	Frontantrieb	Benzin	66	90	May 1987	Dec 1989	2024-03-01	2664
Lancia	Prisma	1.6	Stufenheck	Frontantrieb	Benzin	77	105	Jan 1983	Apr 1986	2024-03-01	2665
Lancia	Prisma	2.0 I.e. Allrad	Stufenheck	Allrad	Benzin	85	115	Apr 1986	Dec 1989	2024-03-01	2666
Lancia	Prisma	1.9 Turbo Diesel	Stufenheck	Frontantrieb	Diesel	59	80	May 1985	Dec 1989	2024-03-01	2667
Lancia	Delta i	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1979	Aug 1992	2024-03-01	2668
Lancia	Delta i	1.5	Schrägheck	Frontantrieb	Benzin	63	86	Sep 1979	Dec 1992	2024-03-01	2669
Lancia	Delta i	1.6 GT I.e.	Schrägheck	Frontantrieb	Benzin	66	90	May 1987	Aug 1992	2024-03-01	2670
Lancia	Delta i	1.6 GT	Schrägheck	Frontantrieb	Benzin	77	105	Nov 1982	Apr 1986	2024-03-01	2671
Lancia	Delta i	1.6 HF Turbo	Schrägheck	Frontantrieb	Benzin	97	132	Apr 1987	Mar 1989	2024-03-01	2672


--- Round 1 / 首次发送 ---
## 更新点

* 首轮闭合 Fiat 124 Sport Spider 欧洲版 1600/1800：发动机与变速箱差异不改变外廓，统一复用 `3971×1613×1250 mm` 尺寸组。([汽车目录][1])
* Pininfarina Spidereuropa 2000 与 Volumex 均属于 DS 两门敞篷车身，外廓一致，复用同一尺寸组。([汽车目录][2])
* 闭合 Fiat 128 3P Berlinetta 三门 Coupe 尺寸组。([汽车数据][3])
* 修正历史 Hyundai ix20 单组缓存：2015 年改款后车长由 `4100 mm` 增至 `4115 mm`，Ktype `2621` 拆为改款前、改款后两条映射；官方资料明确宽度 `1765 mm` 不含后视镜。([汽车数据][4])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：7/100
* READY 映射行：8
* PENDING 输入 Ktype：93/100
* 已确认尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2569	2569	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	MEDIUM	输入周期跨BS与CS目录阶段；欧洲标准外廓一致。	READY
2570	2570	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	MEDIUM	输入周期跨BS与CS目录阶段；欧洲标准外廓一致。	READY
2571	2571	Convertible	124 Sport Spider III	CS	2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	HIGH	CS两门敞篷外廓；发动机差异不另建组。	READY
2572	2572	Convertible	Pininfarina Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	DS两门敞篷标准车身。	READY
2573	2573	Convertible	Pininfarina Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	Volumex动力版本未改变DS车身外廓。	READY
2576	2576	Coupe	128 3P Berlinetta		3	EU-FIAT-128-3P-BERLINETTA-COUPE-01	HIGH	3P Berlinetta三门掀背式Coupe。	READY
2621_prefl	2621	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	HIGH	2010至2015年改款前五门Mini MPV外廓。	READY
2621_facelift	2621	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	HIGH	2015年改款后保险杠造型使车长增加。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	3971	1613	1250	Automobile-Catalog 1973 Fiat 124 Sport Spider 1600 Europe; Automobile-Catalog 1975 Fiat 124 Sport Spider 1800 5-speed Europe	https://www.automobile-catalog.com/car/1973/710405/fiat_124_sport_spider_1600.html; https://www.automobile-catalog.com/car/1975/710495/fiat_124_sport_spider_1800_5-speed.html
EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	4107	1613	1250	Automobile-Catalog 1984 Pininfarina Spidereuropa Europe; Automobile-Catalog 1984 Pininfarina Spidereuropa Volumex Europe	https://www.automobile-catalog.com/car/1984/712190/fiat_pinifarina_spidereuropa.html; https://www.automobile-catalog.com/car/1984/41390/fiat_pinifarina_spidereuropa_volumex.html
EU-FIAT-128-3P-BERLINETTA-COUPE-01	3826	1560	1310	Auto-Data Fiat 128 Coupe generation	https://www.auto-data.net/en/fiat-128-coupe-generation-1587
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600	Auto-Data Hyundai ix20 pre-facelift generation	https://www.auto-data.net/en/hyundai-ix20-generation-7098
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600	Hyundai Motor Europe ix20 facelift official technical specifications	https://www.hyundai.news/newsroom/dam/eu/press-kits/20150315_ix20/20150320_technical_data_ix20.pdf
```

## 下一步优先处理

1. 按外廓阶段闭合 Fiat 128 Sedan：区分第一系列、1974–1976 过渡外观及第二系列，并核对 2 门/4 门分支。
2. 批量处理 Fiat Ritmo 改款前、改款后及 Abarth 130 TC 外部套件差异。
3. 随后闭合 Fiat Tipo、Regata Sedan/Wagon，以已建尺寸组批量关联发动机 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1973/710405/fiat_124_sport_spider_1600.html?utm_source=chatgpt.com "1973 Fiat 124 Sport Spider 1600 Specs Review (76.5 kW / 104 PS / 103 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1984/712190/fiat_pinifarina_spidereuropa.html?utm_source=chatgpt.com "1984 Pinifarina Spidereuropa Specs Review (77 kW / 105 PS / 103 hp) (for Europe )"
[3]: https://www.auto-data.net/en/fiat-128-coupe-generation-1587 "Fiat 128 Coupe | Technical Specs, Fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/hyundai-ix20-model-2117?utm_source=chatgpt.com "Hyundai ix20 | Technical Specs, Fuel consumption, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 首次创建 Fiat Regata 138 四门轿车与 Regata Weekend 五门旅行车尺寸组，批量闭合 13 个 Ktype。([汽车数据][1])
* 首次创建 Fiat Tipo 160 的四个已确认外廓组：五门高 1450、三门高 1450、五门高 1445、三门高 1445；本轮闭合 9 个 Ktype。([汽车数据][2])
* `2595`、`2597`、`2598` 的生产周期覆盖 1993 年三门车身加入后的阶段，按三门、五门拆分映射；尺寸组按门数独立保存。

## 当前批次进度

* READY 输入 Ktype：29/100
* PENDING 输入 Ktype：71/100
* READY 映射行：33
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2594	2594	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	第一阶段五门车身。	READY
2595_3dr	2595	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	生产周期末段覆盖1993年新增三门车身。	READY
2595_5dr	2595	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身贯穿该动力版本周期。	READY
2597_3dr	2597	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	1993年后提供的三门车身分支。	READY
2597_5dr	2597	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身分支。	READY
2598_3dr	2598	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	1993年后提供的三门车身分支。	READY
2598_5dr	2598	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身分支。	READY
2599	2599	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	第一阶段五门车身。	READY
2600	2600	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	第一阶段五门车身。	READY
2601	2601	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	HIGH	第二阶段1.8 GT三门车身。	READY
2602	2602	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	1990至1992年第一阶段五门车身。	READY
2604	2604	Hatchback	Tipo 160	160.EF	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	HIGH	2.0 16V Sport三门车身。	READY
2606	2606	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2608	2608	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2609	2609	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2610	2610	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2611	2611	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2612	2612	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2613	2613	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2614	2614	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2615	2615	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2616	2616	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2617	2617	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2618	2618	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2619	2619	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160 1.4 71 Hp	https://www.auto-data.net/en/fiat-tipo-160-1.4-71hp-7067
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160 2.0 i.e. 16V Sport 160.EF	https://www.auto-data.net/en/fiat-tipo-160-2.0-i.e.-16v-sport-160.ef-139hp-7088
EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	3958	1700	1445	Automobile-Catalog 1990 Fiat Tipo 1.6 i.e. AGT	https://www.automobile-catalog.com/car/1990/718055/fiat_tipo_1_6_i_e__agt.html
EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	3958	1700	1445	Automobile-Catalog 1995 Fiat Tipo 1.8 i.e. GT	https://www.automobile-catalog.com/car/1995/718745/fiat_tipo_1_8_i_e__gt.html
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410	Auto-Data Fiat Regata 138 generation	https://www.auto-data.net/en/fiat-regata-138-generation-1604
EU-FIAT-REGATA-WEEKEND-WAGON-01	4267	1650	1450	Auto-Data Fiat Regata Weekend generation	https://www.auto-data.net/en/fiat-regata-weekend-generation-1605
```

## 下一步优先处理

1. 解决 Tipo `2596`、`2603`、`2605` 跨 1993 年改款及三门新增造成的分支和高度冲突。
2. 按改款前后批量闭合 Fiat Ritmo，并单独核对 Abarth 130 TC 外部套件。
3. 随后处理 Fiat 131 Sedan/Wagon、132、Argenta 与 X1/9。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-regata-138-generation-1604 "1984 Fiat Regata (138) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/fiat-tipo-160-1.4-71hp-7067 "Fiat Tipo (160) 1.4 (71 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1) 更新点

* 闭合 Fiat X1/9 的 1.3 与 1.5 动力记录；三条 Ktype 均关联 `128 AS` 两门 Targa 外廓，尺寸一致。([汽车数据][1])
* 首次建立 Lancia Prisma `831 AB` 四门轿车尺寸组，批量关联四条前驱 Ktype；暂不处理需要独立核对高度的 2.0 四驱版本。([汽车数据][2])
* Lancia Delta I 按 1982 改款、1986 改款普通车身及 1986 改款 HF Turbo 低车身拆为三个尺寸组。([汽车数据][3])

## 2) 当前批次进度

* READY 输入 Ktype：39/100
* PENDING 输入 Ktype：61/100
* READY 映射行：43
* 已确认尺寸组：16
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2634	2634	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	128 AS两门Targa外廓。	READY
2635	2635	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	128 AS两门Targa外廓。	READY
2636	2636	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	1.5动力未改变128 AS车身外廓。	READY
2662	2662	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	MEDIUM	输入86 hp与资料85 hp属标注换算差异；四门外廓明确。	READY
2664	2664	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门前驱轿车外廓。	READY
2665	2665	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门前驱轿车外廓。	READY
2667	2667	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	涡轮柴油动力未改变四门外廓。	READY
2670	2670	Hatchback	Delta I (831, facelift 1986)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH	1986改款五门标准车身。	READY
2671	2671	Hatchback	Delta I (831, facelift 1982)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982改款五门GT车身。	READY
2672	2672	Hatchback	Delta I (831, facelift 1986)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH	HF Turbo车身高度与普通版本不同。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-X1-9-128-AS-TARGA-01	3970	1570	1180	Auto-Data Fiat X 1/9 128 AS 1.3 73 Hp; Auto-Data Fiat X 1/9 128 AS 1.5 Five Speed 85 Hp	https://www.auto-data.net/en/fiat-x-1-9-128-as-1.3-73hp-7266; https://www.auto-data.net/en/fiat-x-1-9-128-as-1.5-five-speed-85hp-7268
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385	Auto-Data Lancia Prisma 831 AB generation	https://www.auto-data.net/en/lancia-prisma-831-ab-generation-1164
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	3895	1620	1380	Auto-Data Lancia Delta I 831 facelift 1982 HF Turbo 1.6 130 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1982-hf-turbo-1.6-130hp-5067
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	3895	1620	1380	Auto-Data Lancia Delta I 831 facelift 1986 1.6 GT i.e. 90 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1986-1.6-gt-i.e.-90hp-5065
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	3895	1620	1355	Auto-Data Lancia Delta I 831 facelift 1986 HF Turbo 1.6 132 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1986-hf-turbo-1.6-132hp-5068
```

## 5) 下一步优先处理

1. 闭合 Fiat Uno 改款前后及 Turbo 分支。
2. 核对 Lancia Y10 普通前驱、四驱及改款尺寸组。
3. 处理 Fiat Ritmo 普通车身与 Abarth 130 TC，并继续解决 Tipo 剩余跨改款 Ktype。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-x-1-9-128-as-1.3-73hp-7266 "Fiat X 1/9 (128 AS) 1.3 (73 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/lancia-prisma-831-ab-generation-1164 "Lancia Prisma (831 AB) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/lancia-delta-i-831-facelift-1986-hf-turbo-1.6-132hp-5068 "Lancia Delta I (831, facelift 1986) HF Turbo 1.6 (132 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* 闭合 Lancia A112 两条晚期车身：第五系列长 `3228 mm`，第六系列因改款增至 `3268 mm`，宽高均保持 `1480×1360 mm`；跨系列的 Ktype `2646` 拆为两条映射。([汽车目录][1])
* 闭合 Lancia Y10 代码 `156` 的第一、第二、第三系列普通前驱车身，并单独建立第一/第二系列 1.3 i.e. 高度组及第三系列 4WD 高车身组。([汽车目录][2])
* 本轮完成 7 个输入 Ktype，共新增 13 条 READY 映射和 8 个尺寸组。

## 2) 当前批次进度

* READY 输入 Ktype：46/100
* PENDING 输入 Ktype：54/100
* READY 映射行：56
* 已确认尺寸组：24
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2646_s5	2646	Hatchback	A112 Series 5		3	EU-LANCIA-A112-SERIES-5-HATCHBACK-3D-01	HIGH	生产周期前段对应第五系列三门车身。	READY
2646_s6	2646	Hatchback	A112 Series 6		3	EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	HIGH	生产周期后段对应第六系列加长前后饰件车身。	READY
2648	2648	Hatchback	A112 Series 6		3	EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	HIGH	LX属于第六系列三门车身。	READY
2649_s1	2649	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	HIGH	1985至1989年第一系列分支。	READY
2649_s2	2649	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	1989至1991年第二系列分支。	READY
2651_s1	2651	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	HIGH	第一系列1.0催化版本分支。	READY
2651_s2	2651	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	第二系列1.0催化版本分支。	READY
2652_s1	2652	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	HIGH	1989年第一系列1.3 i.e.分支。	READY
2652_s2	2652	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	HIGH	1989至1992年第二系列GT i.e.分支。	READY
2652_s3	2652	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH	1992至1995年第三系列1.3分支。	READY
2654_s2	2654	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	第二系列1.1 i.e. Fire分支。	READY
2654_s3	2654	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH	第三系列1.1 i.e. Fire分支。	READY
2656	2656	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	HIGH	第三系列四驱高车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-A112-SERIES-5-HATCHBACK-3D-01	3228	1480	1360	Automobile-Catalog 1981 Autobianchi A-112 Junior Series 5	https://www.automobile-catalog.com/car/1981/168680/autobianchi_a-112_junior.html
EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	3268	1480	1360	Automobile-Catalog 1984 Autobianchi A-112 Junior; Automobile-Catalog 1984 Autobianchi A-112 LX	https://www.automobile-catalog.com/car/1984/168740/autobianchi_a-112_junior.html; https://www.automobile-catalog.com/car/1984/168770/autobianchi_a-112_lx.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423	Automobile-Catalog 1987 Lancia Y10 Fire LX	https://www.automobile-catalog.com/car/1987/1380920/lancia_y10_fire_lx.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424	Automobile-Catalog 1989 Lancia Y10 1.3 i.e. catalyst	https://www.automobile-catalog.com/car/1989/1380965/lancia_y10_1_3_i_e__cat.html
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440	Automobile-Catalog 1990 Lancia Y10 Fire 1.0	https://www.automobile-catalog.com/car/1990/1381070/lancia_y10_fire_1_0.html
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450	Automobile-Catalog 1989 Lancia Y10 GT i.e.	https://www.automobile-catalog.com/car/1989/1381130/lancia_y10_gt_i_e_.html
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440	Automobile-Catalog 1993 Lancia Y10 1.1 Elite; Automobile-Catalog 1994 Lancia Y10 1.3 Elite	https://www.automobile-catalog.com/car/1993/1381400/lancia_y10_1_1_elite.html; https://www.automobile-catalog.com/car/1994/1381430/lancia_y10_1_3_elite.html
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460	Automobile-Catalog 1994 Lancia Y10 4WD	https://www.automobile-catalog.com/car/1994/1381445/lancia_y10_4wd.html
```

## 5) 下一步优先处理

1. 按 1983–1989 与 1989–1993 改款阶段闭合 Fiat Uno 普通三门/五门车身。
2. 单独处理 Uno Turbo i.e. 的保险杠、车长和低车身差异。
3. 随后处理 Fiat Ritmo 普通车身、Abarth 130 TC 及剩余 Tipo 跨改款分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/168680/autobianchi_a-112_junior.html?utm_source=chatgpt.com "1981 Autobianchi A-112 Junior Specs Review (31 kW / 42 PS / 42 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1987/1380920/lancia_y10_fire_lx.html?utm_source=chatgpt.com "1987 Lancia Y10 Fire LX (man. 5) (model since mid-year ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1) 更新点

* 闭合 Fiat Uno `146A` 第一系列普通三门/五门车身：`3644×1555×1425 mm`；1989 年改款后的普通三门/五门车身为 `3689×1558×1420 mm`。宽度均为不含后视镜口径。([汽车目录][1])
* 第一系列 1.3 柴油版因高度 `1432 mm` 单独建组；1.7 Diesel 外廓与对应阶段普通车身一致。([汽车目录][2])
* Uno Turbo i.e. 为三门专属外廓：第一系列 `3644×1560×1370 mm`，1989 改款后 `3689×1558×1405 mm`。([Stellantis Heritage][3])
* 本轮闭合 15 个输入 Ktype，新增 32 条 READY 映射及 8 个尺寸组。

## 2) 当前批次进度

* READY 输入 Ktype：61/100
* PENDING 输入 Ktype：39/100
* READY 映射行：88
* 已确认尺寸组：32
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2639_3dr	2639	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2639_5dr	2639	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2640_3dr	2640	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2640_5dr	2640	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2641_3dr	2641	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2641_5dr	2641	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2642_3dr	2642	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2642_5dr	2642	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2643	2643	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	HIGH	Turbo i.e.三门专属外廓。	READY
2644	2644	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	HIGH	Turbo i.e.三门专属外廓。	READY
2645_prefl_3dr	2645	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	HIGH	第一系列1.3柴油三门高度分支。	READY
2645_prefl_5dr	2645	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	HIGH	第一系列1.3柴油五门高度分支。	READY
2645_facelift_3dr	2645	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期后段对应改款三门车身。	READY
2645_facelift_5dr	2645	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期后段对应改款五门车身。	READY
2647_3dr	2647	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列1.7柴油三门车身。	READY
2647_5dr	2647	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列1.7柴油五门车身。	READY
2650_3dr	2650	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后1.7柴油三门车身。	READY
2650_5dr	2650	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后1.7柴油五门车身。	READY
2653_prefl_3dr	2653	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	生产周期前段对应第一系列三门车身。	READY
2653_prefl_5dr	2653	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	生产周期前段对应第一系列五门车身。	READY
2653_facelift_3dr	2653	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期末段对应改款三门车身。	READY
2653_facelift_5dr	2653	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期末段对应改款五门车身。	READY
2655_3dr	2655	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后三门车身。	READY
2655_5dr	2655	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后五门车身。	READY
2657	2657	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	HIGH	改款后Turbo i.e.三门专属外廓。	READY
2658_3dr	2658	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后三门车身。	READY
2658_5dr	2658	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后五门车身。	READY
2661	2661	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	HIGH	1.4 Turbo i.e.三门专属外廓。	READY
2663_prefl_3dr	2663	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	生产周期前段对应第一系列三门车身。	READY
2663_prefl_5dr	2663	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	生产周期前段对应第一系列五门车身。	READY
2663_facelift_3dr	2663	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期后段对应改款三门车身。	READY
2663_facelift_5dr	2663	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期后段对应改款五门车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	3644	1555	1425	Automobile-Catalog 1986 Fiat Uno 60 S Europe	https://www.automobile-catalog.com/car/1986/25655/fiat_uno_60_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	3644	1555	1425	Automobile-Catalog 1986 Fiat Uno 60 S Europe	https://www.automobile-catalog.com/car/1986/25655/fiat_uno_60_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	3644	1555	1432	Automobile-Catalog 1988 Fiat Uno D Europe	https://www.automobile-catalog.com/car/1988/25850/fiat_uno_d.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	3644	1555	1432	Automobile-Catalog 1988 Fiat Uno D Europe	https://www.automobile-catalog.com/car/1988/25850/fiat_uno_d.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	3644	1560	1370	Automobile-Catalog 1986 Fiat Uno Turbo i.e. Europe; Stellantis Heritage Fiat Uno Turbo i.e.	https://www.automobile-catalog.com/car/1986/715940/fiat_uno_turbo_i_e_.html; https://www.stellantisheritage.com/en-uk/heritage/news/fiat-uno-turbo-ie
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420	Automobile-Catalog 1990 Fiat Uno 45 S Europe	https://www.automobile-catalog.com/car/1990/716135/fiat_uno_45_s.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420	Automobile-Catalog 1990 Fiat Uno 45 S Europe	https://www.automobile-catalog.com/car/1990/716135/fiat_uno_45_s.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	3689	1558	1405	Automobile-Catalog 1990 Fiat Uno Turbo i.e. Europe; Automobile-Catalog 1992 Fiat Uno Turbo i.e. Europe	https://www.automobile-catalog.com/car/1990/716405/fiat_uno_turbo_i_e_.html; https://www.automobile-catalog.com/car/1992/716525/fiat_uno_turbo_i_e_.html
```

## 5) 下一步优先处理

1. 解决 Uno `2637`、`2638` 低配外饰导致的 `1548/1555 mm` 宽度冲突。
2. 批量闭合 Fiat Ritmo 第一系列、1982 改款普通车身及 Abarth 130 TC。
3. 处理剩余 Fiat Tipo 跨改款分支，以及 Fiat 128 Sedan 的系列和门数边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/25655/fiat_uno_60_s.html?utm_source=chatgpt.com "Detailed specs review of 1986 Fiat Uno 60 S model for Europe"
[2]: https://www.automobile-catalog.com/car/1988/25850/fiat_uno_d.html?utm_source=chatgpt.com "Detailed specs review of 1988 Fiat Uno D model for Europe"
[3]: https://www.stellantisheritage.com/en-uk/heritage/news/fiat-uno-turbo-ie?utm_source=chatgpt.com "Fiat Uno Turbo i.e."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1) 更新点

* 闭合 Fiat Ritmo 第一系列普通三门/五门车身，外廓为 `3937×1650×1400 mm`；1.7 Diesel 第一系列五门版复用五门尺寸组。([汽车目录][1])
* 闭合第二系列 1.1 55 hp 普通三门/五门车身，以及 1.3 68 hp 五门高 `1407 mm` 分支。([汽车目录][2])
* 闭合第三系列 1.1 55/58 hp、1.7 Diesel 60 hp 五门车身，统一为 `3993×1650×1418 mm`。([汽车目录][3])
* Abarth Ritmo 130 TC 按第二、第三系列拆分；第三系列前后饰件令车长由 `4014 mm` 变为 `3993 mm`，高度也发生变化。([汽车目录][4])
* 闭合第三系列 1.9 Turbo Diesel 五门专属高度分支。([汽车目录][5])

## 2) 当前批次进度

* READY 输入 Ktype：70/100
* PENDING 输入 Ktype：30/100
* READY 映射行：102
* 已确认尺寸组：41
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2578_3dr	2578	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列三门车身。	READY
2578_5dr	2578	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列五门车身。	READY
2579_s2_3dr	2579	Hatchback	Ritmo I Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	HIGH	生产周期前段对应第二系列三门车身。	READY
2579_s2_5dr	2579	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	HIGH	生产周期前段对应第二系列五门车身。	READY
2579_s3_5dr	2579	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	生产周期后段对应第三系列五门车身。	READY
2580	2580	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列60 L/CL五门车身。	READY
2582	2582	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列70 Super五门车身。	READY
2583_3dr	2583	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列75三门车身。	READY
2583_5dr	2583	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列75五门车身。	READY
2589_s2	2589	Hatchback	Ritmo Abarth 130 TC Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	HIGH	第二系列Abarth 130 TC三门外廓。	READY
2589_s3	2589	Hatchback	Ritmo Abarth 130 TC Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	HIGH	第三系列Abarth 130 TC三门外廓。	READY
2590	2590	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列1.7 Diesel五门车身。	READY
2591	2591	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列Diesel五门车身。	READY
2593	2593	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	HIGH	第三系列Turbo Diesel五门外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 Europe	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html
EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 Europe; Automobile-Catalog 1980 Fiat Ritmo Diesel CL Europe	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html; https://www.automobile-catalog.com/car/1980/1369640/fiat_ritmo_diesel_cl.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	4014	1650	1405	Automobile-Catalog 1985 Fiat Ritmo 60 L Europe	https://www.automobile-catalog.com/car/1985/2068580/fiat_ritmo_60_l.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	4014	1650	1405	Automobile-Catalog 1985 Fiat Ritmo 60 L Europe	https://www.automobile-catalog.com/car/1985/2068580/fiat_ritmo_60_l.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	4014	1650	1407	Automobile-Catalog 1983 Fiat Ritmo 70 Super Europe	https://www.automobile-catalog.com/car/1983/31520/fiat_ritmo_70_super.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418	Automobile-Catalog 1986 Fiat Ritmo ES Europe; Automobile-Catalog 1986 Fiat Ritmo 60 L Europe; Automobile-Catalog 1986 Fiat Ritmo Diesel L Europe	https://www.automobile-catalog.com/car/1986/714695/fiat_ritmo_es.html; https://www.automobile-catalog.com/car/1986/714665/fiat_ritmo_60_l.html; https://www.automobile-catalog.com/car/1986/714875/fiat_ritmo_diesel_l.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	4014	1663	1363	Automobile-Catalog 1983 Fiat Ritmo Abarth 130 TC Europe	https://www.automobile-catalog.com/car/1983/49820/fiat_ritmo_abarth_130_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	3993	1663	1390	Automobile-Catalog 1986 Fiat Ritmo Abarth 130 TC Europe	https://www.automobile-catalog.com/car/1986/714965/fiat_ritmo_abarth_130_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	3993	1650	1410	Automobile-Catalog 1987 Fiat Ritmo Turbo Diesel S Europe	https://www.automobile-catalog.com/car/1987/53060/fiat_ritmo_turbo_diesel_s.html
```

## 5) 下一步优先处理

1. 闭合剩余 Ritmo `2581`、`2585`、`2586`、`2587` 的跨系列及运动版分支。
2. 解决 Tipo `2596`、`2603`、`2605` 的三门/五门和跨改款边界。
3. 处理 Fiat 128 Sedan、Fiat 131 Sedan/Wagon，以及 132、Argenta、Trevi、Beta 和 Prisma 四驱分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html?utm_source=chatgpt.com "1980 Fiat Ritmo 60 Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1985/2068580/fiat_ritmo_60_l.html?utm_source=chatgpt.com "1985 Fiat Ritmo 60 L Specs Review (40.5 kW / 55 PS / 54 hp) (up to May 1985 for Europe )"
[3]: https://www.automobile-catalog.com/car/1986/714695/fiat_ritmo_es.html?utm_source=chatgpt.com "1986 Fiat Ritmo ES Specs Review (40.5 kW / 55 PS / 54 hp) (for Europe )"
[4]: https://www.automobile-catalog.com/car/1983/49820/fiat_ritmo_abarth_130_tc.html?utm_source=chatgpt.com "1983 Fiat Ritmo Abarth 130 TC Specs Review (95.5 kW ..."
[5]: https://www.automobile-catalog.com/car/1987/53060/fiat_ritmo_turbo_diesel_s.html?utm_source=chatgpt.com "1987 Fiat Ritmo Turbo Diesel S Specs Review (59 kW ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1) 更新点

* 闭合剩余 Fiat Tipo 三条 Ktype：`2596` 按三门/五门拆分，`2603` 为五门，`2605` 的 107 kW 16V 对应五门车身；全部复用既有 `3958×1700×1445 mm` 尺寸组，不重复建组。([汽车目录][1])
* 闭合 Fiat Uno `2637`、`2638`：改款前基础外饰宽度为 `1548 mm`，与此前已确认的 `1555 mm` 普通外饰组分开；1989 改款后直接复用既有三门/五门组。([汽车目录][2])
* 首次创建 Fiat Argenta、Lancia Trevi、Lancia Beta HPE 尺寸组；Prisma 2.0 4WD 核对后确认外廓与既有 Prisma 四门组一致，直接复用。([汽车目录][3])

## 2) 当前批次进度

* READY 输入 Ktype：80/100
* PENDING 输入 Ktype：20/100
* READY 映射行：117
* 已确认尺寸组：46
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2596_3dr	2596	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	HIGH	1993年后提供的三门1.9 TD分支。	READY
2596_5dr	2596	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	五门1.9 TD分支贯穿输入周期。	READY
2603	2603	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	2.0 i.e.五门车身。	READY
2605	2605	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	107 kW 16V对应五门车身；输入结束月晚于该功率资料周期。	READY
2632	2632	Sedan	Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
2633	2633	Sedan	Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	2500 Diesel未改变132A四门外廓。	READY
2637_prefl	2637	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	HIGH	改款前0.9基础外饰三门车身。	READY
2637_facelift	2637	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后0.9三门车身。	READY
2638_prefl_3dr	2638	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	HIGH	改款前1.0基础外饰三门车身。	READY
2638_prefl_5dr	2638	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	HIGH	改款前1.0基础外饰五门车身。	READY
2638_facelift_3dr	2638	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后1.0三门车身。	READY
2638_facelift_5dr	2638	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	1989改款后1.0五门车身。	READY
2659	2659	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-01	MEDIUM	828四门Trevi外廓；输入周期早于已确认2.0 i.e.资料。	READY
2660	2660	Hatchback	Beta H.P.E. Series 4	828 BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH	H.P. Executive三门掀背式旅行车外廓。	READY
2666	2666	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门4WD外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420	Automobile-Catalog 1982 Fiat Argenta 2000 Iniezione; Auto-Specifikacio Fiat Argenta 2500 Diesel	https://www.automobile-catalog.com/car/1982/716645/fiat_argenta_2000_iniezione.html; https://www.auto-specifikacio.hu/fiat-argenta-2500-diesel-auto-muszaki-adatok/
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	3644	1548	1425	Automobile-Catalog 1988 Fiat Uno 45 Sting; Automobile-Catalog 1986 Fiat Uno 45 Fire	https://www.automobile-catalog.com/car/1988/715955/fiat_uno_45_sting.html; https://www.automobile-catalog.com/car/1986/53330/fiat_uno_45_fire.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	3644	1548	1425	Automobile-Catalog 1986 Fiat Uno 45 Fire	https://www.automobile-catalog.com/car/1986/53330/fiat_uno_45_fire.html
EU-LANCIA-TREVI-828-SEDAN-01	4355	1706	1400	Auto-Data Lancia Trevi 828 2.0 i.e. 122 Hp	https://www.auto-data.net/en/lancia-trevi-828-2.0-i.e-122hp-automatic-45737
EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	4285	1650	1310	EncyCARpedia 1984 Lancia HPE 2000 i.e.; Stellantis Heritage Lancia Beta HPE	https://www.encycarpedia.com/lancia/84-hpe-2000-i-e-estate; https://www.stellantisheritage.com/en-uk/heritage/stories/lancia-beta-hpe
```

## 5) 下一步优先处理

1. 闭合 Fiat Ritmo `2581`、`2585`、`2586`、`2587` 的第一、第二、第三系列分支。
2. 处理 Fiat 128 Sedan `2574`、`2575`、`2577` 的系列与两门/四门边界。
3. 集中处理 Fiat 131 Sedan/Wagon、Fiat 132，以及 Lancia Delta I `2668`、`2669` 的跨改款分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1991/718445/fiat_tipo_2_0_i_e__16v.html?utm_source=chatgpt.com "1991 Fiat Tipo 2.0 i.e. 16V Specs Review (107 kW / 146 PS / 143 hp) (since March 1991 for Europe )"
[2]: https://www.automobile-catalog.com/car/1988/715955/fiat_uno_45_sting.html?utm_source=chatgpt.com "1988 Fiat Uno 45 Sting Specs Review (33 kW / 45 PS / 44 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1982/716645/fiat_argenta_2000_iniezione.html?utm_source=chatgpt.com "1982 Fiat Argenta 2000 Iniezione Specs Review (90 kW ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1) 更新点

* 闭合 Fiat Ritmo 剩余 4 个 Ktype：第一系列 1.3/1.5 普通车身直接复用既有组；105 TC 第一、第二系列独立建组；第三系列 100 S 按三门、五门分支处理。第一系列 105 TC 为 `3937×1688×1390 mm`，第二系列为 `4014×1663×1390 mm`。([汽车目录][1])
* 闭合 Fiat 128 三条 Sedan Ktype：1975 年前标准外廓为 `3840×1590×1420 mm`，1975 年后为 `3860×1590×1420 mm`；两阶段均按两门、四门分别落盘。([汽车目录][2])
* 闭合 Lancia Delta I `2668`、`2669`：初期车身长 `3885 mm`，1982 年改款后长 `3895 mm`；1986 年改款未产生新的三维组，继续复用既有改款后尺寸组。([汽车数据][3])

## 2) 当前批次进度

* READY 输入 Ktype：89/100
* PENDING 输入 Ktype：11/100
* READY 映射行：147
* 已确认尺寸组：54
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2574_2dr	2574	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	第二系列两门轿车外廓。	READY
2574_4dr	2574	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	第二系列四门轿车外廓。	READY
2575_s1_2dr	2575	Sedan	128 Series 1	128	2	EU-FIAT-128-S1-SEDAN-2D-01	HIGH	生产周期前段对应第一系列两门车身。	READY
2575_s1_4dr	2575	Sedan	128 Series 1	128	4	EU-FIAT-128-S1-SEDAN-4D-01	HIGH	生产周期前段对应第一系列四门车身。	READY
2575_s2_2dr	2575	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	1975年后第二系列两门车身。	READY
2575_s2_4dr	2575	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	1975年后第二系列四门车身。	READY
2577_s1_2dr	2577	Sedan	128 Series 1	128	2	EU-FIAT-128-S1-SEDAN-2D-01	MEDIUM	生产周期开始阶段覆盖第一系列两门车身。	READY
2577_s1_4dr	2577	Sedan	128 Series 1	128	4	EU-FIAT-128-S1-SEDAN-4D-01	MEDIUM	生产周期开始阶段覆盖第一系列四门车身。	READY
2577_s2_2dr	2577	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	第二系列1.3两门轿车。	READY
2577_s2_4dr	2577	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	第二系列1.3四门轿车。	READY
2581_s1_3dr	2581	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列1.3三门普通车身。	READY
2581_s1_5dr	2581	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列1.3五门普通车身。	READY
2581_s2_3dr	2581	Hatchback	Ritmo I Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	HIGH	第二系列1.3三门普通车身。	READY
2581_s2_5dr	2581	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	HIGH	第二系列1.3五门普通车身。	READY
2581_s3_5dr	2581	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	生产周期末段覆盖第三系列70五门车身。	READY
2585_s2	2585	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列85 Super五门车身。	READY
2585_s3	2585	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列85 S五门车身。	READY
2586_s1	2586	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	MEDIUM	第一系列85 Super五门分支。	READY
2586_s2	2586	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列85 Super五门车身。	READY
2586_s3	2586	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列85 S五门车身。	READY
2587_s1	2587	Hatchback	Ritmo 105 TC Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	HIGH	第一系列105 TC三门专属外廓。	READY
2587_s2	2587	Hatchback	Ritmo 105 TC Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	HIGH	第二系列105 TC三门专属外廓。	READY
2587_s3_3dr	2587	Hatchback	Ritmo 100 S Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	HIGH	第三系列100 S三门车身。	READY
2587_s3_5dr	2587	Hatchback	Ritmo 100 S Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列100 S五门车身。	READY
2668_prefl	2668	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	HIGH	1979至1982年初期五门车身。	READY
2668_fl1982	2668	Hatchback	Delta I facelift 1982	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982年改款五门车身。	READY
2668_fl1986	2668	Hatchback	Delta I facelift 1986	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1986年改款未改变标准车身三维。	READY
2669_prefl	2669	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	HIGH	1979至1982年初期五门车身。	READY
2669_fl1982	2669	Hatchback	Delta I facelift 1982	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982年改款五门车身。	READY
2669_fl1986	2669	Hatchback	Delta I facelift 1986	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1986年改款未改变标准车身三维。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-128-S1-SEDAN-2D-01	3840	1590	1420	Automobile-Catalog 1974 Fiat 128 1100 low compression	https://www.automobile-catalog.com/car/1974/711170/fiat_128_low_compr_.html
EU-FIAT-128-S1-SEDAN-4D-01	3840	1590	1420	Automobile-Catalog 1974 Fiat 128 1100 low compression	https://www.automobile-catalog.com/car/1974/711170/fiat_128_low_compr_.html
EU-FIAT-128-S2-SEDAN-2D-01	3860	1590	1420	Automobile-Catalog 1976 Fiat 128 1100 CL	https://www.automobile-catalog.com/car/1976/44570/fiat_128_1100_cl.html
EU-FIAT-128-S2-SEDAN-4D-01	3860	1590	1420	Automobile-Catalog 1976 Fiat 128 1100 CL	https://www.automobile-catalog.com/car/1976/44570/fiat_128_1100_cl.html
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	3937	1688	1390	Automobile-Catalog 1981 Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1981/714155/fiat_ritmo_105_tc.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	4014	1663	1390	Automobile-Catalog 1983 Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1983/714560/fiat_ritmo_105_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418	Automobile-Catalog 1986 Fiat Ritmo-Strada Series III hatchback range	https://www.automobile-catalog.com/make/fiat/ritmo_strada/ritmo_strada_series_iii_hatchback/1986.html
EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	3885	1620	1380	Auto-Data Lancia Delta I 831 1300 1.3 75 Hp	https://www.auto-data.net/en/lancia-delta-i-831-1300-1.3-75hp-5061
```

## 5) 下一步优先处理

1. 集中闭合最后 10 个 Fiat 131 Ktype，按第一、第二、第三系列及两门、四门、Panorama 分支处理。
2. 闭合 Fiat 132 `2631` 的 1977 年与 1979 年外饰改款尺寸分支。
3. 完成后立即进行一次机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/714155/fiat_ritmo_105_tc.html?utm_source=chatgpt.com "1981 Fiat Ritmo 105 TC Specs Review (77 kW / 105 PS / 103 hp) (since mid-year 1981 for Europe )"
[2]: https://www.automobile-catalog.com/car/1974/711170/fiat_128_low_compr_.html?utm_source=chatgpt.com "1974 Fiat 128 1100 (low compr.) Specs Review ..."
[3]: https://www.auto-data.net/en/lancia-delta-i-831-1300-1.3-75hp-5061?utm_source=chatgpt.com "Lancia Delta I (831) 1300 1.3 (75 Hp)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1) 更新点

* 闭合 Fiat 131 1.4 Mirafiori：确认属于第三系列两门轿车外廓，尺寸为 `4264×1650×1400 mm`。([汽车数据][1])
* 闭合 Fiat 131 2.0 Racing：两门运动车身的加宽外廓为 `4231×1663×1400 mm`，不与普通 Mirafiori 共组。([汽车数据][2])
* 闭合 Fiat 131 1.6 Panorama：确认五门旅行车外廓为 `4264×1650×1400 mm`。([汽车数据][3])
* 闭合 Fiat 132 2.0：确认四门第三系列轿车外廓为 `4404×1641×1425 mm`。([autoevolution][4])

## 2) 当前批次进度

* READY 输入 Ktype：93/100
* PENDING 输入 Ktype：7/100
* READY 映射行：151
* 已确认尺寸组：58
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2623	2623	Sedan	131 Series 3	131	2	EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	HIGH	第三系列Mirafiori两门轿车外廓。	READY
2628	2628	Sedan	131 Series 2 Racing	131	2	EU-FIAT-131-S2-SEDAN-2D-RACING-01	HIGH	Racing两门宽体及外部套件外廓。	READY
2630	2630	Wagon	131 Panorama		5	EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	HIGH	第三系列Panorama五门旅行车外廓。	READY
2631	2631	Sedan	132 Series 3	132	4	EU-FIAT-132-S3-SEDAN-4D-2000-01	HIGH	第三系列2.0四门轿车外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	4264	1650	1400	Auto-Data Fiat 131 1.4 Mirafiori 70 Hp	https://www.auto-data.net/en/fiat-131-1.4-mirafiori-70hp-7092
EU-FIAT-131-S2-SEDAN-2D-RACING-01	4231	1663	1400	Auto-Data Fiat 131 2.0 Racing 115 Hp	https://www.auto-data.net/en/fiat-131-2.0-racing-115hp-7100
EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	4264	1650	1400	Auto-Data Fiat 131 Familiare/Panorama 1.6 Mirafiori 85 Hp	https://www.auto-data.net/en/fiat-131-familiare-panorama-1.6-mirafiori-85hp-7106
EU-FIAT-132-S3-SEDAN-4D-2000-01	4404	1641	1425	Autoevolution Fiat 132 specifications	https://www.autoevolution.com/cars/fiat-132-1974.html
```

## 5) 下一步优先处理

1. 处理 `2622`、`2626`、`2627` 的 Super/Supermirafiori 两门与四门边界及系列差异。
2. 处理 `2629` 的 2.5 Diesel 普通轿车高度与柴油专用外饰。
3. 最后拆分跨多个系列的 `2620`、`2624`、`2625`；完成后立即进入一次机械收尾。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-131-1.4-mirafiori-70hp-7092?utm_source=chatgpt.com "Fiat 131 1.4 Mirafiori (70 Hp) /Coupe 1980"
[2]: https://www.auto-data.net/en/fiat-131-2.0-racing-115hp-7100?utm_source=chatgpt.com "Fiat 131 2.0 Racing (115 Hp) /Coupe 1978"
[3]: https://www.auto-data.net/en/fiat-131-familiare-panorama-1.6-mirafiori-85hp-7106?utm_source=chatgpt.com "Fiat 131 Familiare/panorama 1.6 Mirafiori (85 Hp)"
[4]: https://www.autoevolution.com/cars/fiat-132-1974.html "FIAT 132 Specs, Performance & Photos - 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981 - autoevolution"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1) 更新点

* 闭合 `2622`：第二系列 1.3 Supermirafiori 仅关联四门轿车外廓 `4231×1651×1381 mm`。([汽车目录][1])
* 闭合 `2626`：生产周期跨第二、第三系列，拆分为两个四门 Supermirafiori 外廓；第三系列宽度变为 `1645 mm`、高度变为 `1405 mm`。([汽车目录][2])
* 闭合 `2627`：2.0 Super 对应第三系列四门 Supermirafiori，复用第三系列尺寸组。([汽车目录][3])
* 闭合 `2629`：2.5 Diesel 按 1981 年系列切换拆成第二、第三系列四门分支，分别复用上述两个尺寸组。([汽车目录][4])

## 2) 当前批次进度

* READY 输入 Ktype：97/100
* PENDING 输入 Ktype：3/100
* READY 映射行：157
* 已确认尺寸组：60
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2622	2622	Sedan	131 Series 2 Supermirafiori	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	第二系列Supermirafiori四门轿车。	READY
2626_s2	2626	Sedan	131 Series 2 Supermirafiori	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	生产周期前段对应第二系列四门车身。	READY
2626_s3	2626	Sedan	131 Series 3 Supermirafiori	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	生产周期后段对应第三系列四门车身。	READY
2627	2627	Sedan	131 Series 3 Supermirafiori	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	第三系列2.0 Super四门车身。	READY
2629_s2	2629	Sedan	131 Series 2 Supermirafiori Diesel	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	1981年3月以前第二系列柴油四门外廓。	READY
2629_s3	2629	Sedan	131 Series 3 Supermirafiori Diesel	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	1981年4月以后第三系列柴油四门外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	4231	1651	1381	Automobile-Catalog Fiat 131 Series 2 Supermirafiori 1300/1600 TC and Diesel 2500 Super	https://www.automobile-catalog.com/car/1979/712625/fiat_131_supermirafiori_1300.html; https://www.automobile-catalog.com/car/1979/32870/fiat_131_supermirafiori_1600.html; https://www.automobile-catalog.com/car/1979/36710/fiat_131_diesel_2500_super.html
EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	4231	1645	1405	Automobile-Catalog Fiat 131 Series 3 Supermirafiori 1600/2000 TC and Diesel Super 2500	https://www.automobile-catalog.com/car/1982/713105/fiat_131_supermirafiori_1600_tc.html; https://www.automobile-catalog.com/car/1982/713135/fiat_131_supermirafiori_2000_tc.html; https://www.automobile-catalog.com/car/1982/713060/fiat_131_diesel_super_2500.html
```

## 5) 下一步优先处理

1. 闭合 `2620` 的第一、第二系列及两门/四门 Mirafiori 分支。
2. 闭合 `2624` 的第一、第二系列 1.6 标准车身分支。
3. 闭合 `2625` 的 85 hp Mirafiori 跨系列边界；完成后立即输出两张最终完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1979/712625/fiat_131_supermirafiori_1300.html?utm_source=chatgpt.com "1979 Fiat 131 Supermirafiori 1300/TC Specs Review (60 kW / 82 PS / 80 hp) (since mid-year 1979 for Europe )"
[2]: https://www.automobile-catalog.com/car/1979/32870/fiat_131_supermirafiori_1600.html?utm_source=chatgpt.com "1979 Fiat 131 Supermirafiori 1600/TC Specs Review (70.5 kW / 96 PS / 95 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1982/713135/fiat_131_supermirafiori_2000_tc.html?utm_source=chatgpt.com "1982 Fiat 131 Supermirafiori 2000 TC Specs Review (83 kW / 113 PS / 111 hp) (for Europe )"
[4]: https://www.automobile-catalog.com/car/1981/36710/fiat_131_diesel_2500_super.html?utm_source=chatgpt.com "1981 Fiat 131 Diesel 2500 Super Specs Review (53 kW / 72 PS / 71 hp) (up to March 1981 for Europe )"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 最后 3 个 PENDING Ktype 已闭合：`2620`、`2624` 按 Fiat 131 第一/第二系列及两门/四门拆分；`2625` 关联第三系列 Mirafiori CL([AUTODOC UK][1])([autodoc.co.uk][1])
* 已完成轻量机械收尾：固定表头、唯一主键、外键闭合、尺寸与来源非空、无孤立尺寸组。
* 已生成两个任务指定文件。

## 当前批次进度

* 输入 Ktype：100/100
* READY 输入 Ktype：100/100
* PENDING 输入 Ktype：0/100
* READY 映射行：166
* DIMENSION_GROUP：65
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一及引用闭合：通过
* 三维为正整数、来源与 URL 非空：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2569	2569	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	MEDIUM	输入周期跨BS与CS目录阶段；欧洲标准外廓一致。	READY
2570	2570	Convertible	124 Sport Spider		2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	MEDIUM	输入周期跨BS与CS目录阶段；欧洲标准外廓一致。	READY
2571	2571	Convertible	124 Sport Spider III	CS	2	EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	HIGH	CS两门敞篷外廓；发动机差异不另建组。	READY
2572	2572	Convertible	Pininfarina Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	DS两门敞篷标准车身。	READY
2573	2573	Convertible	Pininfarina Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	Volumex动力版本未改变DS车身外廓。	READY
2574_2dr	2574	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	第二系列两门轿车外廓。	READY
2574_4dr	2574	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	第二系列四门轿车外廓。	READY
2575_s1_2dr	2575	Sedan	128 Series 1	128	2	EU-FIAT-128-S1-SEDAN-2D-01	HIGH	生产周期前段对应第一系列两门车身。	READY
2575_s1_4dr	2575	Sedan	128 Series 1	128	4	EU-FIAT-128-S1-SEDAN-4D-01	HIGH	生产周期前段对应第一系列四门车身。	READY
2575_s2_2dr	2575	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	1975年后第二系列两门车身。	READY
2575_s2_4dr	2575	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	1975年后第二系列四门车身。	READY
2576	2576	Coupe	128 3P Berlinetta		3	EU-FIAT-128-3P-BERLINETTA-COUPE-01	HIGH	3P Berlinetta三门掀背式Coupe。	READY
2577_s1_2dr	2577	Sedan	128 Series 1	128	2	EU-FIAT-128-S1-SEDAN-2D-01	MEDIUM	生产周期开始阶段覆盖第一系列两门车身。	READY
2577_s1_4dr	2577	Sedan	128 Series 1	128	4	EU-FIAT-128-S1-SEDAN-4D-01	MEDIUM	生产周期开始阶段覆盖第一系列四门车身。	READY
2577_s2_2dr	2577	Sedan	128 Series 2	128	2	EU-FIAT-128-S2-SEDAN-2D-01	HIGH	第二系列1.3两门轿车。	READY
2577_s2_4dr	2577	Sedan	128 Series 2	128	4	EU-FIAT-128-S2-SEDAN-4D-01	HIGH	第二系列1.3四门轿车。	READY
2578_3dr	2578	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列三门车身。	READY
2578_5dr	2578	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列五门车身。	READY
2579_s2_3dr	2579	Hatchback	Ritmo I Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	HIGH	生产周期前段对应第二系列三门车身。	READY
2579_s2_5dr	2579	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	HIGH	生产周期前段对应第二系列五门车身。	READY
2579_s3_5dr	2579	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	生产周期后段对应第三系列五门车身。	READY
2580	2580	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列60 L/CL五门车身。	READY
2581_s1_3dr	2581	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列1.3三门普通车身。	READY
2581_s1_5dr	2581	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列1.3五门普通车身。	READY
2581_s2_3dr	2581	Hatchback	Ritmo I Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	HIGH	第二系列1.3三门普通车身。	READY
2581_s2_5dr	2581	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	HIGH	第二系列1.3五门普通车身。	READY
2581_s3_5dr	2581	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	生产周期末段覆盖第三系列70五门车身。	READY
2582	2582	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列70 Super五门车身。	READY
2583_3dr	2583	Hatchback	Ritmo I Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	HIGH	第一系列75三门车身。	READY
2583_5dr	2583	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列75五门车身。	READY
2585_s2	2585	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列85 Super五门车身。	READY
2585_s3	2585	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列85 S五门车身。	READY
2586_s1	2586	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	MEDIUM	第一系列85 Super五门分支。	READY
2586_s2	2586	Hatchback	Ritmo I Series 2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	HIGH	第二系列85 Super五门车身。	READY
2586_s3	2586	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列85 S五门车身。	READY
2587_s1	2587	Hatchback	Ritmo 105 TC Series 1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	HIGH	第一系列105 TC三门专属外廓。	READY
2587_s2	2587	Hatchback	Ritmo 105 TC Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	HIGH	第二系列105 TC三门专属外廓。	READY
2587_s3_3dr	2587	Hatchback	Ritmo 100 S Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	HIGH	第三系列100 S三门车身。	READY
2587_s3_5dr	2587	Hatchback	Ritmo 100 S Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列100 S五门车身。	READY
2589_s2	2589	Hatchback	Ritmo Abarth 130 TC Series 2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	HIGH	第二系列Abarth 130 TC三门外廓。	READY
2589_s3	2589	Hatchback	Ritmo Abarth 130 TC Series 3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	HIGH	第三系列Abarth 130 TC三门外廓。	READY
2590	2590	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	HIGH	第三系列1.7 Diesel五门车身。	READY
2591	2591	Hatchback	Ritmo I Series 1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	HIGH	第一系列Diesel五门车身。	READY
2593	2593	Hatchback	Ritmo I Series 3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	HIGH	第三系列Turbo Diesel五门外廓。	READY
2594	2594	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	第一阶段五门车身。	READY
2595_3dr	2595	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	生产周期末段覆盖1993年新增三门车身。	READY
2595_5dr	2595	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身贯穿该动力版本周期。	READY
2596_3dr	2596	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	HIGH	1993年后提供的三门1.9 TD分支。	READY
2596_5dr	2596	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	五门1.9 TD分支贯穿输入周期。	READY
2597_3dr	2597	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	1993年后提供的三门车身分支。	READY
2597_5dr	2597	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身分支。	READY
2598_3dr	2598	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	1993年后提供的三门车身分支。	READY
2598_5dr	2598	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门车身分支。	READY
2599	2599	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	第一阶段五门车身。	READY
2600	2600	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	第一阶段五门车身。	READY
2601	2601	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	HIGH	第二阶段1.8 GT三门车身。	READY
2602	2602	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	1990至1992年第一阶段五门车身。	READY
2603	2603	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	HIGH	2.0 i.e.五门车身。	READY
2604	2604	Hatchback	Tipo 160	160.EF	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	HIGH	2.0 16V Sport三门车身。	READY
2605	2605	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	MEDIUM	107 kW 16V对应五门车身；输入结束月晚于该功率资料周期。	READY
2606	2606	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2608	2608	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2609	2609	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2610	2610	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2611	2611	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2612	2612	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2613	2613	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2614	2614	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2615	2615	Sedan	Regata (138)	138	4	EU-FIAT-REGATA-138-SEDAN-01	HIGH	138四门轿车外廓。	READY
2616	2616	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2617	2617	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2618	2618	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2619	2619	Wagon	Regata Weekend	138	5	EU-FIAT-REGATA-WEEKEND-WAGON-01	HIGH	Weekend五门旅行车外廓。	READY
2620_s1_2dr	2620	Sedan	131 Series 1 Mirafiori	131	2	EU-FIAT-131-S1-MIRAFIORI-SEDAN-2D-STD-01	HIGH	第一系列1.3 Mirafiori两门标准车身。	READY
2620_s1_4dr	2620	Sedan	131 Series 1 Mirafiori	131	4	EU-FIAT-131-S1-MIRAFIORI-SEDAN-4D-STD-01	HIGH	第一系列1.3 Mirafiori四门标准车身。	READY
2620_s2_2dr	2620	Sedan	131 Series 2 Mirafiori	131	2	EU-FIAT-131-S2-MIRAFIORI-SEDAN-2D-STD-01	HIGH	第二系列1.3 Mirafiori两门标准车身。	READY
2620_s2_4dr	2620	Sedan	131 Series 2 Mirafiori	131	4	EU-FIAT-131-S2-MIRAFIORI-SEDAN-4D-STD-01	HIGH	第二系列1.3 Mirafiori四门标准车身。	READY
2621_prefl	2621	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	HIGH	2010至2015年改款前五门Mini MPV外廓。	READY
2621_facelift	2621	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	HIGH	2015年改款后保险杠造型使车长增加。	READY
2622	2622	Sedan	131 Series 2 Supermirafiori	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	第二系列Supermirafiori四门轿车。	READY
2623	2623	Sedan	131 Series 3	131	2	EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	HIGH	第三系列Mirafiori两门轿车外廓。	READY
2624_s1_2dr	2624	Sedan	131 Series 1 Mirafiori	131	2	EU-FIAT-131-S1-MIRAFIORI-SEDAN-2D-STD-01	HIGH	第一系列1.6 Mirafiori两门标准车身。	READY
2624_s1_4dr	2624	Sedan	131 Series 1 Mirafiori	131	4	EU-FIAT-131-S1-MIRAFIORI-SEDAN-4D-STD-01	HIGH	第一系列1.6 Mirafiori四门标准车身。	READY
2624_s2_2dr	2624	Sedan	131 Series 2 Mirafiori	131	2	EU-FIAT-131-S2-MIRAFIORI-SEDAN-2D-STD-01	HIGH	第二系列1.6 Mirafiori两门标准车身。	READY
2624_s2_4dr	2624	Sedan	131 Series 2 Mirafiori	131	4	EU-FIAT-131-S2-MIRAFIORI-SEDAN-4D-STD-01	HIGH	第二系列1.6 Mirafiori四门标准车身。	READY
2625	2625	Sedan	131 Series 3 Mirafiori CL	131	4	EU-FIAT-131-S3-MIRAFIORI-CL-SEDAN-4D-01	MEDIUM	131 C2.000在欧洲目录对应第三系列CL四门车身；输入周期早于目录实车阶段。	READY
2626_s2	2626	Sedan	131 Series 2 Supermirafiori	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	生产周期前段对应第二系列四门车身。	READY
2626_s3	2626	Sedan	131 Series 3 Supermirafiori	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	生产周期后段对应第三系列四门车身。	READY
2627	2627	Sedan	131 Series 3 Supermirafiori	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	第三系列2.0 Super四门车身。	READY
2628	2628	Sedan	131 Series 2 Racing	131	2	EU-FIAT-131-S2-SEDAN-2D-RACING-01	HIGH	Racing两门宽体及外部套件外廓。	READY
2629_s2	2629	Sedan	131 Series 2 Supermirafiori Diesel	131	4	EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	1981年3月以前第二系列柴油四门外廓。	READY
2629_s3	2629	Sedan	131 Series 3 Supermirafiori Diesel	131	4	EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	HIGH	1981年4月以后第三系列柴油四门外廓。	READY
2630	2630	Wagon	131 Panorama		5	EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	HIGH	第三系列Panorama五门旅行车外廓。	READY
2631	2631	Sedan	132 Series 3	132	4	EU-FIAT-132-S3-SEDAN-4D-2000-01	HIGH	第三系列2.0四门轿车外廓。	READY
2632	2632	Sedan	Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	132A四门轿车外廓。	READY
2633	2633	Sedan	Argenta	132A	4	EU-FIAT-ARGENTA-132A-SEDAN-01	HIGH	2500 Diesel未改变132A四门外廓。	READY
2634	2634	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	128 AS两门Targa外廓。	READY
2635	2635	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	128 AS两门Targa外廓。	READY
2636	2636	Targa	X 1/9 (128 AS)	128 AS	2	EU-FIAT-X1-9-128-AS-TARGA-01	HIGH	1.5动力未改变128 AS车身外廓。	READY
2637_prefl	2637	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	HIGH	改款前0.9基础外饰三门车身。	READY
2637_facelift	2637	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后0.9三门车身。	READY
2638_prefl_3dr	2638	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	HIGH	改款前1.0基础外饰三门车身。	READY
2638_prefl_5dr	2638	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	HIGH	改款前1.0基础外饰五门车身。	READY
2638_facelift_3dr	2638	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后1.0三门车身。	READY
2638_facelift_5dr	2638	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	1989改款后1.0五门车身。	READY
2639_3dr	2639	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2639_5dr	2639	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2640_3dr	2640	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2640_5dr	2640	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2641_3dr	2641	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2641_5dr	2641	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2642_3dr	2642	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列三门车身。	READY
2642_5dr	2642	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列五门车身。	READY
2643	2643	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	HIGH	Turbo i.e.三门专属外廓。	READY
2644	2644	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	HIGH	Turbo i.e.三门专属外廓。	READY
2645_prefl_3dr	2645	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	HIGH	第一系列1.3柴油三门高度分支。	READY
2645_prefl_5dr	2645	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	HIGH	第一系列1.3柴油五门高度分支。	READY
2645_facelift_3dr	2645	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期后段对应改款三门车身。	READY
2645_facelift_5dr	2645	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期后段对应改款五门车身。	READY
2646_s5	2646	Hatchback	A112 Series 5		3	EU-LANCIA-A112-SERIES-5-HATCHBACK-3D-01	HIGH	生产周期前段对应第五系列三门车身。	READY
2646_s6	2646	Hatchback	A112 Series 6		3	EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	HIGH	生产周期后段对应第六系列加长前后饰件车身。	READY
2647_3dr	2647	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	第一系列1.7柴油三门车身。	READY
2647_5dr	2647	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	第一系列1.7柴油五门车身。	READY
2648	2648	Hatchback	A112 Series 6		3	EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	HIGH	LX属于第六系列三门车身。	READY
2649_s1	2649	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	HIGH	1985至1989年第一系列分支。	READY
2649_s2	2649	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	1989至1991年第二系列分支。	READY
2650_3dr	2650	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后1.7柴油三门车身。	READY
2650_5dr	2650	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后1.7柴油五门车身。	READY
2651_s1	2651	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	HIGH	第一系列1.0催化版本分支。	READY
2651_s2	2651	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	第二系列1.0催化版本分支。	READY
2652_s1	2652	Hatchback	Y10 Series 1	156	3	EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	HIGH	1989年第一系列1.3 i.e.分支。	READY
2652_s2	2652	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	HIGH	1989至1992年第二系列GT i.e.分支。	READY
2652_s3	2652	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH	1992至1995年第三系列1.3分支。	READY
2653_prefl_3dr	2653	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	生产周期前段对应第一系列三门车身。	READY
2653_prefl_5dr	2653	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	生产周期前段对应第一系列五门车身。	READY
2653_facelift_3dr	2653	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期末段对应改款三门车身。	READY
2653_facelift_5dr	2653	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期末段对应改款五门车身。	READY
2654_s2	2654	Hatchback	Y10 Series 2	156	3	EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	HIGH	第二系列1.1 i.e. Fire分支。	READY
2654_s3	2654	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	HIGH	第三系列1.1 i.e. Fire分支。	READY
2655_3dr	2655	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后三门车身。	READY
2655_5dr	2655	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后五门车身。	READY
2656	2656	Hatchback	Y10 Series 3	156	3	EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	HIGH	第三系列四驱高车身。	READY
2657	2657	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	HIGH	改款后Turbo i.e.三门专属外廓。	READY
2658_3dr	2658	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	改款后三门车身。	READY
2658_5dr	2658	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	改款后五门车身。	READY
2659	2659	Sedan	Trevi	828	4	EU-LANCIA-TREVI-828-SEDAN-01	MEDIUM	828四门Trevi外廓；输入周期早于已确认2.0 i.e.资料。	READY
2660	2660	Hatchback	Beta H.P.E. Series 4	828 BF	3	EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	HIGH	H.P. Executive三门掀背式旅行车外廓。	READY
2661	2661	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	HIGH	1.4 Turbo i.e.三门专属外廓。	READY
2662	2662	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	MEDIUM	输入86 hp与资料85 hp属标注换算差异；四门外廓明确。	READY
2663_prefl_3dr	2663	Hatchback	Uno I	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	HIGH	生产周期前段对应第一系列三门车身。	READY
2663_prefl_5dr	2663	Hatchback	Uno I	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	HIGH	生产周期前段对应第一系列五门车身。	READY
2663_facelift_3dr	2663	Hatchback	Uno I facelift 1989	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	生产周期后段对应改款三门车身。	READY
2663_facelift_5dr	2663	Hatchback	Uno I facelift 1989	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	生产周期后段对应改款五门车身。	READY
2664	2664	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门前驱轿车外廓。	READY
2665	2665	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门前驱轿车外廓。	READY
2666	2666	Sedan	Prisma	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	831 AB四门4WD外廓。	READY
2667	2667	Sedan	Prisma (831 AB)	831 AB	4	EU-LANCIA-PRISMA-831-AB-SEDAN-01	HIGH	涡轮柴油动力未改变四门外廓。	READY
2668_prefl	2668	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	HIGH	1979至1982年初期五门车身。	READY
2668_fl1982	2668	Hatchback	Delta I facelift 1982	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982年改款五门车身。	READY
2668_fl1986	2668	Hatchback	Delta I facelift 1986	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1986年改款未改变标准车身三维。	READY
2669_prefl	2669	Hatchback	Delta I	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	HIGH	1979至1982年初期五门车身。	READY
2669_fl1982	2669	Hatchback	Delta I facelift 1982	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982年改款五门车身。	READY
2669_fl1986	2669	Hatchback	Delta I facelift 1986	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1986年改款未改变标准车身三维。	READY
2670	2670	Hatchback	Delta I (831, facelift 1986)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	HIGH	1986改款五门标准车身。	READY
2671	2671	Hatchback	Delta I (831, facelift 1982)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	HIGH	1982改款五门GT车身。	READY
2672	2672	Hatchback	Delta I (831, facelift 1986)	831	5	EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	HIGH	HF Turbo车身高度与普通版本不同。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2501-2600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-124-SPORT-SPIDER-CONVERTIBLE-EU-01	3971	1613	1250	Automobile-Catalog 1973 Fiat 124 Sport Spider 1600 Europe; Automobile-Catalog 1975 Fiat 124 Sport Spider 1800 5-speed Europe	https://www.automobile-catalog.com/car/1973/710405/fiat_124_sport_spider_1600.html; https://www.automobile-catalog.com/car/1975/710495/fiat_124_sport_spider_1800_5-speed.html
EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	4107	1613	1250	Automobile-Catalog 1984 Pininfarina Spidereuropa Europe; Automobile-Catalog 1984 Pininfarina Spidereuropa Volumex Europe	https://www.automobile-catalog.com/car/1984/712190/fiat_pinifarina_spidereuropa.html; https://www.automobile-catalog.com/car/1984/41390/fiat_pinifarina_spidereuropa_volumex.html
EU-FIAT-128-S2-SEDAN-2D-01	3860	1590	1420	Automobile-Catalog 1976 Fiat 128 1100 CL	https://www.automobile-catalog.com/car/1976/44570/fiat_128_1100_cl.html
EU-FIAT-128-S2-SEDAN-4D-01	3860	1590	1420	Automobile-Catalog 1976 Fiat 128 1100 CL	https://www.automobile-catalog.com/car/1976/44570/fiat_128_1100_cl.html
EU-FIAT-128-S1-SEDAN-2D-01	3840	1590	1420	Automobile-Catalog 1974 Fiat 128 1100 low compression	https://www.automobile-catalog.com/car/1974/711170/fiat_128_low_compr_.html
EU-FIAT-128-S1-SEDAN-4D-01	3840	1590	1420	Automobile-Catalog 1974 Fiat 128 1100 low compression	https://www.automobile-catalog.com/car/1974/711170/fiat_128_low_compr_.html
EU-FIAT-128-3P-BERLINETTA-COUPE-01	3826	1560	1310	Auto-Data Fiat 128 Coupe generation	https://www.auto-data.net/en/fiat-128-coupe-generation-1587
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 Europe	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html
EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	3937	1650	1400	Automobile-Catalog 1980 Fiat Ritmo 60 Europe; Automobile-Catalog 1980 Fiat Ritmo Diesel CL Europe	https://www.automobile-catalog.com/car/1980/31625/fiat_ritmo_60.html; https://www.automobile-catalog.com/car/1980/1369640/fiat_ritmo_diesel_cl.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	4014	1650	1405	Automobile-Catalog 1985 Fiat Ritmo 60 L Europe	https://www.automobile-catalog.com/car/1985/2068580/fiat_ritmo_60_l.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	4014	1650	1405	Automobile-Catalog 1985 Fiat Ritmo 60 L Europe	https://www.automobile-catalog.com/car/1985/2068580/fiat_ritmo_60_l.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418	Automobile-Catalog 1986 Fiat Ritmo ES Europe; Automobile-Catalog 1986 Fiat Ritmo 60 L Europe; Automobile-Catalog 1986 Fiat Ritmo Diesel L Europe	https://www.automobile-catalog.com/car/1986/714695/fiat_ritmo_es.html; https://www.automobile-catalog.com/car/1986/714665/fiat_ritmo_60_l.html; https://www.automobile-catalog.com/car/1986/714875/fiat_ritmo_diesel_l.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	4014	1650	1407	Automobile-Catalog 1983 Fiat Ritmo 70 Super Europe	https://www.automobile-catalog.com/car/1983/31520/fiat_ritmo_70_super.html
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	3937	1688	1390	Automobile-Catalog 1981 Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1981/714155/fiat_ritmo_105_tc.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	4014	1663	1390	Automobile-Catalog 1983 Fiat Ritmo 105 TC	https://www.automobile-catalog.com/car/1983/714560/fiat_ritmo_105_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418	Automobile-Catalog 1986 Fiat Ritmo-Strada Series III hatchback range	https://www.automobile-catalog.com/make/fiat/ritmo_strada/ritmo_strada_series_iii_hatchback/1986.html
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	4014	1663	1363	Automobile-Catalog 1983 Fiat Ritmo Abarth 130 TC Europe	https://www.automobile-catalog.com/car/1983/49820/fiat_ritmo_abarth_130_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	3993	1663	1390	Automobile-Catalog 1986 Fiat Ritmo Abarth 130 TC Europe	https://www.automobile-catalog.com/car/1986/714965/fiat_ritmo_abarth_130_tc.html
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	3993	1650	1410	Automobile-Catalog 1987 Fiat Ritmo Turbo Diesel S Europe	https://www.automobile-catalog.com/car/1987/53060/fiat_ritmo_turbo_diesel_s.html
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160 1.4 71 Hp	https://www.auto-data.net/en/fiat-tipo-160-1.4-71hp-7067
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160 2.0 i.e. 16V Sport 160.EF	https://www.auto-data.net/en/fiat-tipo-160-2.0-i.e.-16v-sport-160.ef-139hp-7088
EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	3958	1700	1445	Automobile-Catalog 1995 Fiat Tipo 1.8 i.e. GT	https://www.automobile-catalog.com/car/1995/718745/fiat_tipo_1_8_i_e__gt.html
EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	3958	1700	1445	Automobile-Catalog 1990 Fiat Tipo 1.6 i.e. AGT	https://www.automobile-catalog.com/car/1990/718055/fiat_tipo_1_6_i_e__agt.html
EU-FIAT-REGATA-138-SEDAN-01	4260	1650	1410	Auto-Data Fiat Regata 138 generation	https://www.auto-data.net/en/fiat-regata-138-generation-1604
EU-FIAT-REGATA-WEEKEND-WAGON-01	4267	1650	1450	Auto-Data Fiat Regata Weekend generation	https://www.auto-data.net/en/fiat-regata-weekend-generation-1605
EU-FIAT-131-S1-MIRAFIORI-SEDAN-2D-STD-01	4238	1632	1400	Automobile-Catalog Fiat 131 Series I Mirafiori 2-Door range	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_i_mirafiori_2p/1974.html
EU-FIAT-131-S1-MIRAFIORI-SEDAN-4D-STD-01	4238	1632	1400	Automobile-Catalog Fiat 131 Series I Mirafiori 4-Door range; Automobile-Catalog Fiat 131 Mirafiori 1300 low compression	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_i_mirafiori_sedan/1975.html; https://www.automobile-catalog.com/car/1975/712295/fiat_131_mirafiori_1300_low_compr_.html
EU-FIAT-131-S2-MIRAFIORI-SEDAN-2D-STD-01	4264	1651	1381	Automobile-Catalog Fiat 131 Series II Mirafiori 2-Door range; Automobile-Catalog 1979 Fiat 131 Mirafiori L 1300 2 Porte	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_ii_mirafiori_2p/1980.html; https://www.automobile-catalog.com/car/1979/2067470/fiat_131_mirafiori_l_1300_2_porte.html
EU-FIAT-131-S2-MIRAFIORI-SEDAN-4D-STD-01	4264	1651	1381	Automobile-Catalog Fiat 131 Series II Mirafiori 4-Door range; Automobile-Catalog 1979 Fiat 131 Mirafiori CL 1300	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_ii_mirafiori_sedan/1980.html; https://www.automobile-catalog.com/car/1979/28460/fiat_131_mirafiori_cl_1300.html
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600	Auto-Data Hyundai ix20 pre-facelift generation	https://www.auto-data.net/en/hyundai-ix20-generation-7098
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600	Hyundai Motor Europe ix20 facelift official technical specifications	https://www.hyundai.news/newsroom/dam/eu/press-kits/20150315_ix20/20150320_technical_data_ix20.pdf
EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	4231	1651	1381	Automobile-Catalog Fiat 131 Series 2 Supermirafiori 1300/1600 TC and Diesel 2500 Super	https://www.automobile-catalog.com/car/1979/712625/fiat_131_supermirafiori_1300.html; https://www.automobile-catalog.com/car/1979/32870/fiat_131_supermirafiori_1600.html; https://www.automobile-catalog.com/car/1979/36710/fiat_131_diesel_2500_super.html
EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	4264	1650	1400	Auto-Data Fiat 131 1.4 Mirafiori 70 Hp	https://www.auto-data.net/en/fiat-131-1.4-mirafiori-70hp-7092
EU-FIAT-131-S3-MIRAFIORI-CL-SEDAN-4D-01	4264	1645	1411	Automobile-Catalog 1982 Fiat 131 Series III Mirafiori 4-Door range; Autotecnica Fiat 131 third series technical dimensions	https://www.automobile-catalog.com/make/fiat/131_mirafiori/131_series_iii_mirafiori_sedan/1982.html; https://www.autotecnica.org/fiat-131-terza-serie-indimenticabile/
EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	4231	1645	1405	Automobile-Catalog Fiat 131 Series 3 Supermirafiori 1600/2000 TC and Diesel Super 2500	https://www.automobile-catalog.com/car/1982/713105/fiat_131_supermirafiori_1600_tc.html; https://www.automobile-catalog.com/car/1982/713135/fiat_131_supermirafiori_2000_tc.html; https://www.automobile-catalog.com/car/1982/713060/fiat_131_diesel_super_2500.html
EU-FIAT-131-S2-SEDAN-2D-RACING-01	4231	1663	1400	Auto-Data Fiat 131 2.0 Racing 115 Hp	https://www.auto-data.net/en/fiat-131-2.0-racing-115hp-7100
EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	4264	1650	1400	Auto-Data Fiat 131 Familiare/Panorama 1.6 Mirafiori 85 Hp	https://www.auto-data.net/en/fiat-131-familiare-panorama-1.6-mirafiori-85hp-7106
EU-FIAT-132-S3-SEDAN-4D-2000-01	4404	1641	1425	Autoevolution Fiat 132 specifications	https://www.autoevolution.com/cars/fiat-132-1974.html
EU-FIAT-ARGENTA-132A-SEDAN-01	4449	1650	1420	Automobile-Catalog 1982 Fiat Argenta 2000 Iniezione; Auto-Specifikacio Fiat Argenta 2500 Diesel	https://www.automobile-catalog.com/car/1982/716645/fiat_argenta_2000_iniezione.html; https://www.auto-specifikacio.hu/fiat-argenta-2500-diesel-auto-muszaki-adatok/
EU-FIAT-X1-9-128-AS-TARGA-01	3970	1570	1180	Auto-Data Fiat X 1/9 128 AS 1.3 73 Hp; Auto-Data Fiat X 1/9 128 AS 1.5 Five Speed 85 Hp	https://www.auto-data.net/en/fiat-x-1-9-128-as-1.3-73hp-7266; https://www.auto-data.net/en/fiat-x-1-9-128-as-1.5-five-speed-85hp-7268
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	3644	1548	1425	Automobile-Catalog 1988 Fiat Uno 45 Sting; Automobile-Catalog 1986 Fiat Uno 45 Fire	https://www.automobile-catalog.com/car/1988/715955/fiat_uno_45_sting.html; https://www.automobile-catalog.com/car/1986/53330/fiat_uno_45_fire.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420	Automobile-Catalog 1990 Fiat Uno 45 S Europe	https://www.automobile-catalog.com/car/1990/716135/fiat_uno_45_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	3644	1548	1425	Automobile-Catalog 1986 Fiat Uno 45 Fire	https://www.automobile-catalog.com/car/1986/53330/fiat_uno_45_fire.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420	Automobile-Catalog 1990 Fiat Uno 45 S Europe	https://www.automobile-catalog.com/car/1990/716135/fiat_uno_45_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	3644	1555	1425	Automobile-Catalog 1986 Fiat Uno 60 S Europe	https://www.automobile-catalog.com/car/1986/25655/fiat_uno_60_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	3644	1555	1425	Automobile-Catalog 1986 Fiat Uno 60 S Europe	https://www.automobile-catalog.com/car/1986/25655/fiat_uno_60_s.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	3644	1560	1370	Automobile-Catalog 1986 Fiat Uno Turbo i.e. Europe; Stellantis Heritage Fiat Uno Turbo i.e.	https://www.automobile-catalog.com/car/1986/715940/fiat_uno_turbo_i_e_.html; https://www.stellantisheritage.com/en-uk/heritage/news/fiat-uno-turbo-ie
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	3644	1555	1432	Automobile-Catalog 1988 Fiat Uno D Europe	https://www.automobile-catalog.com/car/1988/25850/fiat_uno_d.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	3644	1555	1432	Automobile-Catalog 1988 Fiat Uno D Europe	https://www.automobile-catalog.com/car/1988/25850/fiat_uno_d.html
EU-LANCIA-A112-SERIES-5-HATCHBACK-3D-01	3228	1480	1360	Automobile-Catalog 1981 Autobianchi A-112 Junior Series 5	https://www.automobile-catalog.com/car/1981/168680/autobianchi_a-112_junior.html
EU-LANCIA-A112-SERIES-6-HATCHBACK-3D-01	3268	1480	1360	Automobile-Catalog 1984 Autobianchi A-112 Junior; Automobile-Catalog 1984 Autobianchi A-112 LX	https://www.automobile-catalog.com/car/1984/168740/autobianchi_a-112_junior.html; https://www.automobile-catalog.com/car/1984/168770/autobianchi_a-112_lx.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423	Automobile-Catalog 1987 Lancia Y10 Fire LX	https://www.automobile-catalog.com/car/1987/1380920/lancia_y10_fire_lx.html
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440	Automobile-Catalog 1990 Lancia Y10 Fire 1.0	https://www.automobile-catalog.com/car/1990/1381070/lancia_y10_fire_1_0.html
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424	Automobile-Catalog 1989 Lancia Y10 1.3 i.e. catalyst	https://www.automobile-catalog.com/car/1989/1380965/lancia_y10_1_3_i_e__cat.html
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450	Automobile-Catalog 1989 Lancia Y10 GT i.e.	https://www.automobile-catalog.com/car/1989/1381130/lancia_y10_gt_i_e_.html
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440	Automobile-Catalog 1993 Lancia Y10 1.1 Elite; Automobile-Catalog 1994 Lancia Y10 1.3 Elite	https://www.automobile-catalog.com/car/1993/1381400/lancia_y10_1_1_elite.html; https://www.automobile-catalog.com/car/1994/1381430/lancia_y10_1_3_elite.html
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460	Automobile-Catalog 1994 Lancia Y10 4WD	https://www.automobile-catalog.com/car/1994/1381445/lancia_y10_4wd.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	3689	1558	1405	Automobile-Catalog 1990 Fiat Uno Turbo i.e. Europe; Automobile-Catalog 1992 Fiat Uno Turbo i.e. Europe	https://www.automobile-catalog.com/car/1990/716405/fiat_uno_turbo_i_e_.html; https://www.automobile-catalog.com/car/1992/716525/fiat_uno_turbo_i_e_.html
EU-LANCIA-TREVI-828-SEDAN-01	4355	1706	1400	Auto-Data Lancia Trevi 828 2.0 i.e. 122 Hp	https://www.auto-data.net/en/lancia-trevi-828-2.0-i.e-122hp-automatic-45737
EU-LANCIA-BETA-HPE-828-BF-HATCHBACK-3D-01	4285	1650	1310	EncyCARpedia 1984 Lancia HPE 2000 i.e.; Stellantis Heritage Lancia Beta HPE	https://www.encycarpedia.com/lancia/84-hpe-2000-i-e-estate; https://www.stellantisheritage.com/en-uk/heritage/stories/lancia-beta-hpe
EU-LANCIA-PRISMA-831-AB-SEDAN-01	4180	1620	1385	Auto-Data Lancia Prisma 831 AB generation	https://www.auto-data.net/en/lancia-prisma-831-ab-generation-1164
EU-LANCIA-DELTA-I-831-HATCHBACK-PREFL-01	3885	1620	1380	Auto-Data Lancia Delta I 831 1300 1.3 75 Hp	https://www.auto-data.net/en/lancia-delta-i-831-1300-1.3-75hp-5061
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1982-01	3895	1620	1380	Auto-Data Lancia Delta I 831 facelift 1982 HF Turbo 1.6 130 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1982-hf-turbo-1.6-130hp-5067
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-01	3895	1620	1380	Auto-Data Lancia Delta I 831 facelift 1986 1.6 GT i.e. 90 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1986-1.6-gt-i.e.-90hp-5065
EU-LANCIA-DELTA-I-831-HATCHBACK-FL1986-HF-TURBO-01	3895	1620	1355	Auto-Data Lancia Delta I 831 facelift 1986 HF Turbo 1.6 132 Hp	https://www.auto-data.net/en/lancia-delta-i-831-facelift-1986-hf-turbo-1.6-132hp-5068
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2501-2600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.co.uk/car-parts/handles-10791/fiat/131/131-1974/2620-1-3-mirafiori?utm_source=chatgpt.com "FIAT 131 Saloon (131) 1.3 Mirafiori Door handle - 54 hp Petrol 40 kW 1974 - 1981 131 A6.000 ▷ AUTODOC"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2501-2600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2501-2600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3050 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（783 行）
