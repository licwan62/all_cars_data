# 任务：all 第 1701-1800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0018__ac939363


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1701-1800 行

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
all 第 1701-1800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Scirocco	1.3	Coupe	Frontantrieb	Benzin	44	60	Aug 1979	Jul 1980	2024-03-01	1736
VW	Scirocco	1.5	Coupe	Frontantrieb	Benzin	51	70	Aug 1977	Jul 1980	2024-03-01	1737
VW	Scirocco	1.5	Coupe	Frontantrieb	Benzin	51	70	Feb 1974	Dec 1975	2024-03-01	1738
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	55	75	Aug 1975	Jul 1979	2024-03-01	1739
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	63	85	Aug 1975	Jul 1980	2024-03-01	1740
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	81	110	Jun 1976	Jul 1980	2024-03-01	1741
VW	Scirocco	1.3	Coupe	Frontantrieb	Benzin	44	60	Aug 1980	Dec 1983	2024-03-01	1742
VW	Scirocco	1.5	Coupe	Frontantrieb	Benzin	51	70	Aug 1980	Dec 1983	2024-03-01	1743
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	55	75	Jan 1983	Dec 1989	2024-03-01	1744
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	63	85	Aug 1980	Apr 1984	2024-03-01	1745
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	81	110	Aug 1980	Jul 1982	2024-03-01	1746
VW	Scirocco	1.6	Coupe	Frontantrieb	Benzin	53	72	Apr 1986	Jul 1990	2024-03-01	1747
VW	Scirocco	1.8	Coupe	Frontantrieb	Benzin	66	90	Aug 1983	Jul 1992	2024-03-01	1748
VW	Scirocco	1.8	Coupe	Frontantrieb	Benzin	70	95	Nov 1985	Jul 1992	2024-03-01	1749
VW	Scirocco	1.8	Coupe	Frontantrieb	Benzin	82	112	Aug 1982	Dec 1989	2024-03-01	1750
VW	Scirocco	1.8 16V	Coupe	Frontantrieb	Benzin	102	139	Oct 1985	Jul 1989	2024-03-01	1751
VW	Scirocco	1.8 16V	Coupe	Frontantrieb	Benzin	95	129	Mar 1986	Jul 1992	2024-03-01	1752
VW	Corrado	1.8 G60	Coupe	Frontantrieb	Benzin	118	160	Sep 1988	Sep 1993	2024-03-01	1753
VW	Corrado	2.0 I 16V	Coupe	Frontantrieb	Benzin	100	136	Aug 1991	Dec 1995	2024-03-01	1754
VW	Corrado	2.9 VR6	Coupe	Frontantrieb	Benzin	140	190	Aug 1991	Dec 1995	2024-03-01	1755
Fiat	Sedici	1.6 16V	SUV	Frontantrieb	Benzin	88	120	Jun 2006	Oct 2014	2024-03-01	1756
VW	181	1.6	Geländewagen offen	Heckantrieb	Benzin	32	44	Aug 1970	Jul 1973	2024-03-01	1757
VW	181	1.6	Geländewagen offen	Heckantrieb	Benzin	35	48	Mar 1973	Feb 1979	2024-03-01	1758
VW	Iltis	1.7	Geländewagen offen	Allrad	Benzin	55	75	Mar 1979	Dec 1988	2024-03-01	1759
VW	Transporter t2	1.6	Bus	Heckantrieb	Benzin	37	50	Aug 1970	Apr 1979	2024-03-01	1760
VW	Transporter t2	1.8	Bus	Heckantrieb	Benzin	50	68	Nov 1973	Jul 1975	2024-03-01	1761
VW	Transporter t2	2	Bus	Heckantrieb	Benzin	51	70	Aug 1975	Apr 1979	2024-03-01	1762
VW	Transporter / multivan t4	2.4 D Syncro	Bus	Allrad	Diesel	57	78	Oct 1992	Sep 1998	2025-11-01	1763
Opel	Monza a	2.0 E	Coupe	Heckantrieb	Benzin	85	115	Mar 1983	Oct 1984	2024-03-01	1764
Opel	Monza a	2.2 E	Coupe	Heckantrieb	Benzin	85	115	Nov 1984	Aug 1986	2024-03-01	1765
Opel	Monza a	2.5 E	Coupe	Heckantrieb	Benzin	100	136	May 1981	Aug 1986	2024-03-01	1766
Opel	Monza a	2.5 E	Coupe	Heckantrieb	Benzin	103	140	Jun 1984	Aug 1986	2024-03-01	1767
VW	Transporter / multivan t4	2.5 Syncro	Bus	Allrad	Benzin	81	110	Aug 1992	Apr 2003	2025-11-01	1768
VW	Transporter / multivan t4	2.5	Bus	Frontantrieb	Benzin	81	110	Sep 1990	Jun 2003	2025-11-01	1769
Opel	Monza a	2.8	Coupe	Heckantrieb	Benzin	103	140	Feb 1978	Apr 1981	2024-03-01	1770
Opel	Monza a	3	Coupe	Heckantrieb	Benzin	110	150	Apr 1978	Jul 1982	2024-03-01	1771
VW	Transporter t3	1.6	Bus	Heckantrieb	Benzin	37	50	May 1979	Dec 1982	2024-03-01	1772
Opel	Monza a	3.0 GSE	Coupe	Heckantrieb	Benzin	115	156	Sep 1985	Aug 1986	2024-03-01	1773
VW	Transporter t3	1.6 D	Bus	Heckantrieb	Diesel	37	50	Jan 1981	Jul 1987	2024-03-01	1774
VW	Transporter t3	1.6 TD	Bus	Heckantrieb	Diesel	51	70	Aug 1984	Jul 1992	2024-03-01	1775
Opel	Monza a	3.0 GSE	Coupe	Heckantrieb	Benzin	132	180	Feb 1978	Aug 1986	2024-03-01	1776
Vauxhall	Chevette	1300	Stufenheck	Heckantrieb	Benzin	39	53	Mar 1975	Dec 1985	2024-03-01	1777
Vauxhall	Chevette	1300	Stufenheck	Heckantrieb	Benzin	42	57	Sep 1974	Dec 1985	2024-03-01	1778
VW	Transporter t3	1.9	Bus	Heckantrieb	Benzin	44	60	Aug 1982	Jul 1992	2024-03-01	1779
Vauxhall	Chevette	1.3	Kombi	Heckantrieb	Benzin	39	53	Sep 1976	Dec 1985	2024-05-01	1780
VW	Transporter t3	1.9	Bus	Heckantrieb	Benzin	57	78	Aug 1982	Jul 1992	2024-03-01	1781
Vauxhall	Chevette	1300	Kombi	Heckantrieb	Benzin	42	57	Sep 1976	Dec 1985	2024-03-01	1782
Opel	Calibra a	2.0 I	Coupe	Frontantrieb	Benzin	85	115	Aug 1989	Dec 1996	2024-03-01	1783
Opel	Calibra a	2.0 I 4X4	Coupe	Allrad	Benzin	85	115	Jun 1990	Jul 1997	2024-03-01	1784
VW	Transporter t3	1.9	Bus	Heckantrieb	Benzin	61	83	Jan 1983	Jul 1985	2024-03-01	1785
Opel	Calibra a	2.0 I 16V	Coupe	Frontantrieb	Benzin	110	150	Jun 1990	Feb 1994	2024-03-01	1786
Opel	Calibra a	2.0 I 16V 4X4	Coupe	Allrad	Benzin	110	150	Jun 1990	Feb 1994	2024-03-01	1787
Opel	Calibra a	2.0 I Turbo 4X4	Coupe	Allrad	Benzin	150	204	Aug 1991	Jul 1997	2024-03-01	1788
Opel	Calibra a	2.5 I V6	Coupe	Frontantrieb	Benzin	125	170	Apr 1993	Jul 1997	2024-03-01	1789
Fiat	Sedici	1.6 16V 4X4	SUV	Allrad	Benzin	88	120	Jun 2006	Oct 2014	2024-03-01	1790
Opel	Astra f cc	1.7 TDS	Schrägheck	Frontantrieb	Diesel	60	82	Dec 1991	Jan 1998	2024-03-01	1791
Opel	Astra f	1.7 TDS	Stufenheck	Frontantrieb	Diesel	60	82	Mar 1992	Sep 1998	2024-03-01	1792
Opel	Astra f cc	1.7 D	Schrägheck	Frontantrieb	Diesel	42	57	Dec 1991	Sep 1992	2024-03-01	1793
Opel	Astra f	1.7 D	Stufenheck	Frontantrieb	Diesel	42	57	Mar 1992	Sep 1992	2024-03-01	1794
Opel	Astra f cc	1.7 D	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1992	Jan 1998	2024-03-01	1795
Opel	Astra f	1.7 D	Stufenheck	Frontantrieb	Diesel	44	60	Jul 1992	Sep 1998	2024-03-01	1796
Opel	Astra f cc	1.4 I	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1991	Jan 1998	2024-03-01	1797
Opel	Astra f	1.4 I	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1991	Sep 1998	2024-03-01	1798
Fiat	Sedici	2.0 D Multijet	SUV	Frontantrieb	Diesel	99	135	Jun 2006	Oct 2014	2024-03-01	1799
Fiat	Sedici	2.0 D Multijet 4X4	SUV	Allrad	Diesel	99	135	Jun 2006	Oct 2014	2024-03-01	1800
VW	Transporter t3	2	Bus	Heckantrieb	Benzin	51	70	May 1979	Dec 1982	2024-03-01	1801
VW	Transporter t3	2.1	Bus	Heckantrieb	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	1802
Opel	Astra f	1.4 SI	Stufenheck	Frontantrieb	Benzin	60	82	Mar 1992	Sep 1998	2024-03-01	1803
VW	Transporter t3	2.1	Bus	Heckantrieb	Benzin	82	112	Aug 1984	Jul 1992	2024-03-01	1804
Opel	Astra f cc	1.4 SI	Schrägheck	Frontantrieb	Benzin	60	82	Mar 1992	Jan 1998	2024-03-01	1805
Opel	Astra f	1.6 I	Cabriolet	Frontantrieb	Benzin	52	71	Mar 1993	Aug 1996	2024-03-01	1806
Opel	Astra f	1.6 I	Stufenheck	Frontantrieb	Benzin	52	71	May 1993	Jul 1996	2024-03-01	1807
Opel	Astra f cc	1.6 I	Schrägheck	Frontantrieb	Benzin	52	71	May 1993	Jul 1996	2024-03-01	1808
Opel	Astra f cc	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1991	Jan 1998	2024-03-01	1809
Opel	Astra f	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Mar 1992	Sep 1998	2024-03-01	1810
Opel	Astra f cc	1.6 SI	Schrägheck	Frontantrieb	Benzin	74	101	Mar 1992	Dec 1994	2024-03-01	1811
Opel	Astra f	1.6 SI	Stufenheck	Frontantrieb	Benzin	74	100	May 1992	Dec 1994	2024-03-01	1812
Opel	Astra f cc	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1991	Jan 1998	2024-03-01	1813
Opel	Astra f	1.8 I	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1992	Sep 1998	2024-03-01	1814
Opel	Astra f	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	92	125	Jun 1993	Oct 1994	2024-03-01	1815
Opel	Astra f	2.0 I	Cabriolet	Frontantrieb	Benzin	85	115	Mar 1993	Oct 1994	2024-03-01	1816
Opel	Astra f cc	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	Sep 1991	Jan 1998	2024-03-01	1817
Opel	Astra f	2.0 I	Stufenheck	Frontantrieb	Benzin	85	115	Mar 1992	Sep 1998	2024-03-01	1818
Opel	Astra f cc	2.0 GSI 16V	Schrägheck	Frontantrieb	Benzin	110	150	Sep 1991	Jan 1998	2024-03-01	1819
Opel	Astra f caravan	1.7 TDS	Kombi	Frontantrieb	Diesel	60	82	Dec 1991	Jan 1998	2024-03-01	1820
Opel	Astra f caravan	1.7 D	Kombi	Frontantrieb	Diesel	42	57	Dec 1991	Sep 1992	2024-03-01	1821
Opel	Astra f caravan	1.7 D	Kombi	Frontantrieb	Diesel	44	60	Jul 1992	Jan 1998	2024-03-01	1822
Opel	Astra f caravan	1.4 I	Kombi	Frontantrieb	Benzin	44	60	Sep 1991	Jan 1998	2024-03-01	1823
Opel	Astra f caravan	1.4 SI	Kombi	Frontantrieb	Benzin	60	82	Mar 1992	Jan 1998	2024-03-01	1824
Opel	Astra f caravan	1.6 I	Kombi	Frontantrieb	Benzin	52	71	May 1993	Jul 1996	2024-03-01	1825
Opel	Astra f caravan	1.6 I	Kombi	Frontantrieb	Benzin	55	75	Sep 1991	Jan 1998	2024-03-01	1826
Opel	Astra f caravan	1.6 SI	Kombi	Frontantrieb	Benzin	74	101	Mar 1992	Dec 1994	2024-03-01	1827
Opel	Astra f caravan	1.8 I	Kombi	Frontantrieb	Benzin	66	90	Sep 1991	Jan 1998	2024-03-01	1828
Opel	Astra f caravan	1.8 I 16V	Kombi	Frontantrieb	Benzin	92	125	Jun 1993	Jan 1998	2024-03-01	1829
Opel	Astra f caravan	2.0 I	Kombi	Frontantrieb	Benzin	85	115	Sep 1991	Jul 1994	2024-03-01	1830
Opel	Astra f caravan	2.0 I 16V	Kombi	Frontantrieb	Benzin	110	150	Mar 1993	Jan 1998	2024-03-01	1831
Opel	Frontera	2.3 TD	Geländewagen geschlossen	Allrad	Diesel	74	100	Mar 1992	Oct 1998	2024-11-01	1832
Opel	Frontera	2.0 I	Geländewagen offen	Allrad	Benzin	85	115	Mar 1992	Oct 1998	2024-11-01	1833
Opel	Frontera	2.4 I	Geländewagen geschlossen	Allrad	Benzin	92	125	Mar 1992	Oct 1998	2024-11-01	1834
Opel	Monterey a	3.1 TD	Geländewagen geschlossen	Allrad	Diesel	84	114	Sep 1991	Jul 1998	2024-03-01	1835


--- Round 1 / 首次发送 ---
## 1. 更新点

* 已闭合 VW Scirocco I、Scirocco II 两个三门尺寸组，并批量关联 Ktype `1736–1752`。Auto-Data 分别给出 Scirocco I 的 `3885×1624×1309 mm` 和 Scirocco II 的 `4050×1645×1280 mm`。([汽车数据网][1])
* Corrado Ktype `1753` 的生产区间跨越 1991 年改款，已拆为 `prefl` 和 `facelift` 两条物理外廓；改款前资料为 `4048×1674×1318 mm`，改款后为 `4050×1690×1310 mm`。([Carfolio][2])
* 已建立 Fiat Sedici 4X2、4X4 两个尺寸组。Fiat 官方规格明确列出长度和宽度均为 `4115×1755 mm`，4X2 高度 `1605 mm`、4X4 高度 `1620 mm`；2.0 Multijet 4X4 页面亦支持 `4115×1755×1620 mm`。

## 2. 当前批次进度

* READY 输入 Ktype：23/100
* READY 映射行：24
* PENDING 输入 Ktype：77/100
* 本轮首次闭合尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1736	1736	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1737	1737	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1738	1738	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1739	1739	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1740	1740	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1741	1741	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1742	1742	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1743	1743	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1744	1744	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1745	1745	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1746	1746	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1747	1747	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1748	1748	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1749	1749	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1750	1750	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1751	1751	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1752	1752	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1753_prefl	1753	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-PREFL-01	HIGH	Ktype跨越1991改款，拆分改款前外廓。	READY
1753_facelift	1753	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	Ktype跨越1991改款，拆分改款后外廓。	READY
1754	1754	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	1991改款后三门外廓。	READY
1755	1755	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	1991改款后三门外廓。	READY
1756	1756	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X2-01	MEDIUM	4X2外廓；输入起始年月早于120PS改款资料。	READY
1790	1790	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	MEDIUM	4X4外廓；输入起始年月早于120PS改款资料。	READY
1800	1800	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	MEDIUM	4X4外廓；输入起始年月早于2.0 Multijet改款资料。	READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SCIROCCO-I-COUPE-3D-01	3885	1624	1309	Auto-Data Volkswagen Scirocco I (53)	https://www.auto-data.net/en/volkswagen-scirocco-i-53-generation-1889
EU-VW-SCIROCCO-II-COUPE-3D-01	4050	1645	1280	Auto-Data Volkswagen Scirocco II (53B)	https://www.auto-data.net/en/volkswagen-scirocco-ii-53b-generation-1888
EU-VW-CORRADO-53I-COUPE-PREFL-01	4048	1674	1318	Carfolio 1988 Volkswagen Corrado G60	https://www.carfolio.com/volkswagen-corrado-g60-automatic-602426
EU-VW-CORRADO-53I-COUPE-FACELIFT-01	4050	1690	1310	Auto-Data Volkswagen Corrado (53I, facelift 1991) 2.0i 16V	https://www.auto-data.net/en/volkswagen-corrado-53i-facelift-1991-2.0i-16v-136hp-9066
EU-FIAT-SEDICI-I-SUV-4X2-01	4115	1755	1605	Fiat Sedici official technical specifications	https://www.media.stellantis.com/uploads/gr/GR/2014/FIAT/SPECIFICATIONS/Fiat-Sedici-Tech-Specs.pdf
EU-FIAT-SEDICI-I-SUV-4X4-01	4115	1755	1620	Fiat Sedici official technical specifications; Auto-Data Fiat Sedici 2.0 Multijet 4x4	https://www.media.stellantis.com/uploads/gr/GR/2014/FIAT/SPECIFICATIONS/Fiat-Sedici-Tech-Specs.pdf; https://www.auto-data.net/en/fiat-sedici-facelift-2009-2.0-16v-multijet-135hp-4x4-18369
```

## 5. 下一步优先处理

优先按物理车身族集中闭合：

1. VW 181、Iltis、Transporter T2。
2. Transporter T3 的标准 Bus 外廓，以及 T4 的 SWB/LWB、车顶和改款边界。
3. Opel Monza A、Calibra A。
4. Astra F Hatchback、Sedan、Convertible、Wagon 的门数分支。
5. Frontera A、Monterey A 的 SWB/LWB 与开放式/封闭式车身。
6. 单独补齐 Fiat Sedici 2.0 Multijet 4X2 的直接配置来源。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-scirocco-i-53-generation-1889 "Volkswagen Scirocco I (53) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.carfolio.com/volkswagen-corrado-g60-automatic-602426?utm_source=chatgpt.com "1988 Volkswagen Corrado G60 Automatic"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新增 VW 181 与 Iltis 两个开放式越野车尺寸组；Iltis 厂内代码确认为 Type 183。([汽车数据网][1])
* Transporter T2 按前后期外廓拆组；T4 按 SWB/LWB 及 1996 改款前后拆为四个尺寸组，并批量关联三个宽泛 Bus Ktype。([维基百科][2])
* Opel Monza 按 A1/A2 两种不同外廓拆组；Calibra 普通、4×4、Turbo、V6 及改款车型三维一致，复用同一尺寸组。([汽车数据网][3])
* Vauxhall Chevette 三厢 Ktype 拆分为 2dr/4dr 映射但共用尺寸组；Estate 按三门旅行车关联独立尺寸组。([汽车数据网][4])
* Fiat Sedici 2.0 Multijet 前驱 Ktype `1799` 复用已确认的 4X2 尺寸组，本轮未重复输出该尺寸组。

## 2. 当前批次进度

* READY 输入 Ktype：52/100
* READY 映射行：67
* PENDING 输入 Ktype：48/100
* 已确认尺寸组：19
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1757	1757	SUV	VW 181	181	4	EU-VW-181-TYPE-181-SUV-OPEN-01	HIGH	Type 181开放式四门外廓。	READY
1758	1758	SUV	VW 181	181	4	EU-VW-181-TYPE-181-SUV-OPEN-01	HIGH	Type 181开放式四门外廓。	READY
1759	1759	SUV	Iltis	183		EU-VW-ILTIS-TYPE-183-SUV-OPEN-01	HIGH	Type 183开放式越野外廓。	READY
1760_prefl	1760	MPV	Transporter T2a	T2a		EU-VW-TRANSPORTER-T2-MPV-PREFL-01	MEDIUM	Ktype跨越T2前后期，改型前外廓。	READY
1760_facelift	1760	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	MEDIUM	Ktype跨越T2前后期，改型后外廓。	READY
1761	1761	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2后期Bus外廓。	READY
1762	1762	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2后期Bus外廓。	READY
1763_swb_prefl	1763	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1763_swb_facelift	1763	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1763_lwb_prefl	1763	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1763_lwb_facelift	1763	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1764	1764	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1765	1765	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1766_prefl	1766	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A1外廓。	READY
1766_facelift	1766	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A2外廓。	READY
1767	1767	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1768_swb_prefl	1768	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1768_swb_facelift	1768	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1768_lwb_prefl	1768	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1768_lwb_facelift	1768	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1769_swb_prefl	1769	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1769_swb_facelift	1769	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1769_lwb_prefl	1769	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1769_lwb_facelift	1769	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1770	1770	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	A1三门外廓。	READY
1771	1771	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	A1三门外廓。	READY
1773	1773	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1776_prefl	1776	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A1外廓。	READY
1776_facelift	1776	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A2外廓。	READY
1777_2dr	1777	Sedan	Chevette		2	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	两门三厢分支。	READY
1777_4dr	1777	Sedan	Chevette		4	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	四门三厢分支。	READY
1778_2dr	1778	Sedan	Chevette		2	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	两门三厢分支。	READY
1778_4dr	1778	Sedan	Chevette		4	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	四门三厢分支。	READY
1780	1780	Wagon	Chevette Estate		3	EU-VAUXHALL-CHEVETTE-WAGON-3D-01	HIGH	三门Estate外廓。	READY
1782	1782	Wagon	Chevette Estate		3	EU-VAUXHALL-CHEVETTE-WAGON-3D-01	HIGH	三门Estate外廓。	READY
1783	1783	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1784	1784	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	四驱未改变外廓。	READY
1785	1785	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1786	1786	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1787	1787	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	四驱未改变外廓。	READY
1788	1788	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	Turbo四驱外廓三维不变。	READY
1789	1789	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	V6外廓三维不变。	READY
1799	1799	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X2-01	MEDIUM	4X2外廓，复用既有尺寸组。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-181-TYPE-181-SUV-OPEN-01	3780	1641	1621	Auto-Data Volkswagen 181	https://www.auto-data.net/en/volkswagen-181-generation-1850
EU-VW-ILTIS-TYPE-183-SUV-OPEN-01	3880	1520	1840	Carfolio Volkswagen Iltis	https://www.carfolio.com/volkswagen-iltis-73007
EU-VW-TRANSPORTER-T2-MPV-PREFL-01	4420	1765	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	4505	1720	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	4655	1840	1940	Auto-Data Volkswagen Caravelle T4 2.5	https://www.auto-data.net/en/volkswagen-caravelle-t4-2.5-110hp-49330
EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	4789	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Syncro	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-110hp-syncro-49352
EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	5055	1840	1940	Auto-Data Volkswagen Caravelle T4 Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-long-2.5-110hp-49339
EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	5189	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.5-115hp-syncro-49368
EU-OPEL-MONZA-A1-COUPE-3D-01	4692	1734	1380	Auto-Data Opel Monza A1 2.8	https://www.auto-data.net/en/opel-monza-a1-2.8-140hp-1749
EU-OPEL-MONZA-A2-COUPE-3D-01	4720	1722	1380	Auto-Data Opel Monza A2 2.0 E	https://www.auto-data.net/en/opel-monza-a2-2.0-e-115hp-1745
EU-VAUXHALL-CHEVETTE-SEDAN-01	4188	1570	1313	Auto-Data Vauxhall Chevette Sedan	https://www.auto-data.net/en/vauxhall-chevette-generation-1409
EU-VAUXHALL-CHEVETTE-WAGON-3D-01	4188	1570	1323	Auto-Data Vauxhall Chevette Estate	https://www.auto-data.net/en/vauxhall-chevette-estate-1.3-n-53hp-6063
EU-OPEL-CALIBRA-A-COUPE-3D-01	4492	1688	1320	Auto-Data Opel Calibra 2.0; Auto-Data Opel Calibra facelift Turbo 4x4	https://www.auto-data.net/en/opel-calibra-2.0-115hp-2544; https://www.auto-data.net/en/opel-calibra-facelift-1994-2.0-16v-turbo-204hp-4x4-43405
```

## 5. 下一步优先处理

1. 解决 Transporter T3 的 Transporter/Caravelle 车身长度、保险杠及高度口径差异。
2. 批量闭合 Astra F Hatchback、Sedan、Convertible、Wagon 四个车身族及门数边界。
3. 处理 Frontera A 开放式/封闭式与 SWB/LWB 分支。
4. 处理 Monterey A 的短轴、长轴车身边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-181-generation-1850?utm_source=chatgpt.com "Volkswagen 181 | Technical Specs, Fuel consumption ..."
[2]: https://de.wikipedia.org/wiki/VW_T2?utm_source=chatgpt.com "VW T2"
[3]: https://www.auto-data.net/en/opel-monza-a1-2.8-140hp-1749 "Opel Monza A1 2.8 (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/vauxhall-chevette-model-675?utm_source=chatgpt.com "Vauxhall Chevette | Technical Specs, Fuel consumption ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1701-1800_ktype_dimension_mapping_final.tsv
- all_1701-1800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 已闭合剩余 VW Transporter T3、Opel Astra F、Frontera A 和 Monterey A 物理分支；Astra F 已按三门/五门掀背、三厢、旅行车、敞篷改款前后及 GSi 特殊外廓拆组。([汽车数据网][1])
* Frontera A 已区分五门长轴封闭式和三门短轴 Sport；Monterey A 已区分三门短轴和五门长轴。([汽车数据网][2])
* 已纠正上一轮 Ktype `1785` 被误写为 Calibra 的问题，现正确关联 Transporter T3 尺寸组。
* 已完成轻量机械检查：两个固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有外键闭合，尺寸和来源字段均非空。

## 2. 当前批次进度

* 输入 Ktype：100/100
* READY 输入 Ktype：100/100
* 最终映射行：128
* PENDING：0
* 最终尺寸组：31
* 当前批次已完成。

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1736	1736	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1737	1737	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1738	1738	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1739	1739	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1740	1740	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1741	1741	Coupe	Scirocco I	53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Typ 53三门外廓。	READY
1742	1742	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1743	1743	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1744	1744	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1745	1745	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1746	1746	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1747	1747	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1748	1748	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1749	1749	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1750	1750	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1751	1751	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1752	1752	Coupe	Scirocco II	53B	3	EU-VW-SCIROCCO-II-COUPE-3D-01	HIGH	Typ 53B三门外廓。	READY
1753_prefl	1753	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-PREFL-01	HIGH	Ktype跨越1991改款，拆分改款前外廓。	READY
1753_facelift	1753	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	Ktype跨越1991改款，拆分改款后外廓。	READY
1754	1754	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	1991改款后三门外廓。	READY
1755	1755	Coupe	Corrado	53I	3	EU-VW-CORRADO-53I-COUPE-FACELIFT-01	HIGH	1991改款后三门外廓。	READY
1756	1756	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X2-01	MEDIUM	4X2外廓。	READY
1757	1757	SUV	VW 181	181	4	EU-VW-181-TYPE-181-SUV-OPEN-01	HIGH	Type 181开放式四门外廓。	READY
1758	1758	SUV	VW 181	181	4	EU-VW-181-TYPE-181-SUV-OPEN-01	HIGH	Type 181开放式四门外廓。	READY
1759	1759	SUV	Iltis	183		EU-VW-ILTIS-TYPE-183-SUV-OPEN-01	HIGH	Type 183开放式越野外廓。	READY
1760_prefl	1760	MPV	Transporter T2a	T2a		EU-VW-TRANSPORTER-T2-MPV-PREFL-01	MEDIUM	Ktype跨越T2前后期，改型前外廓。	READY
1760_facelift	1760	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	MEDIUM	Ktype跨越T2前后期，改型后外廓。	READY
1761	1761	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2后期Bus外廓。	READY
1762	1762	MPV	Transporter T2b	T2b		EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2后期Bus外廓。	READY
1763_swb_prefl	1763	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1763_swb_facelift	1763	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1763_lwb_prefl	1763	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1763_lwb_facelift	1763	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1764	1764	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1765	1765	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1766_prefl	1766	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A1外廓。	READY
1766_facelift	1766	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A2外廓。	READY
1767	1767	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1768_swb_prefl	1768	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1768_swb_facelift	1768	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1768_lwb_prefl	1768	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1768_lwb_facelift	1768	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1769_swb_prefl	1769	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	MEDIUM	SWB改款前外廓。	READY
1769_swb_facelift	1769	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	MEDIUM	SWB改款后外廓。	READY
1769_lwb_prefl	1769	MPV	Transporter T4	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	MEDIUM	LWB改款前外廓。	READY
1769_lwb_facelift	1769	MPV	Transporter T4 facelift	T4		EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	MEDIUM	LWB改款后外廓。	READY
1770	1770	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	A1三门外廓。	READY
1771	1771	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	A1三门外廓。	READY
1772	1772	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1773	1773	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	A2三门外廓。	READY
1774	1774	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1775	1775	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1776_prefl	1776	Coupe	Monza A1		3	EU-OPEL-MONZA-A1-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A1外廓。	READY
1776_facelift	1776	Coupe	Monza A2		3	EU-OPEL-MONZA-A2-COUPE-3D-01	HIGH	Ktype跨越A1/A2，A2外廓。	READY
1777_2dr	1777	Sedan	Chevette		2	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	两门三厢分支。	READY
1777_4dr	1777	Sedan	Chevette		4	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	四门三厢分支。	READY
1778_2dr	1778	Sedan	Chevette		2	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	两门三厢分支。	READY
1778_4dr	1778	Sedan	Chevette		4	EU-VAUXHALL-CHEVETTE-SEDAN-01	MEDIUM	四门三厢分支。	READY
1779	1779	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1780	1780	Wagon	Chevette Estate		3	EU-VAUXHALL-CHEVETTE-WAGON-3D-01	HIGH	三门Estate外廓。	READY
1781	1781	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1782	1782	Wagon	Chevette Estate		3	EU-VAUXHALL-CHEVETTE-WAGON-3D-01	HIGH	三门Estate外廓。	READY
1783	1783	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1784	1784	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1785	1785	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；纠正上一轮误映射。	READY
1786	1786	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1787	1787	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1788	1788	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1789	1789	Coupe	Calibra A		3	EU-OPEL-CALIBRA-A-COUPE-3D-01	HIGH	三门掀背式Coupe外廓。	READY
1790	1790	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	MEDIUM	4X4外廓。	READY
1791_3dr	1791	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1791_5dr	1791	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1792	1792	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1793_3dr	1793	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1793_5dr	1793	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1794	1794	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1795_3dr	1795	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1795_5dr	1795	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1796	1796	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1797_3dr	1797	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1797_5dr	1797	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1798	1798	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1799	1799	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X2-01	MEDIUM	4X2外廓。	READY
1800	1800	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	MEDIUM	4X4外廓。	READY
1801	1801	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1802	1802	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1803	1803	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1804	1804	MPV	Transporter T3	T3		EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	MEDIUM	标准Bus外廓；门数未细分。	READY
1805_3dr	1805	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1805_5dr	1805	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1806_prefl	1806	Convertible	Astra F Cabrio		2	EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	MEDIUM	Ktype跨越1994改款，改款前两门敞篷外廓。	READY
1806_facelift	1806	Convertible	Astra F Cabrio facelift		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越1994改款，改款后两门敞篷外廓。	READY
1807	1807	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1808_3dr	1808	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1808_5dr	1808	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1809_3dr	1809	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1809_5dr	1809	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1810	1810	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1811_3dr	1811	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1811_5dr	1811	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1812	1812	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1813_3dr	1813	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1813_5dr	1813	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1814	1814	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1815	1815	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1816_prefl	1816	Convertible	Astra F Cabrio		2	EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	MEDIUM	Ktype跨越1994改款，改款前两门敞篷外廓。	READY
1816_facelift	1816	Convertible	Astra F Cabrio facelift		2	EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	MEDIUM	Ktype跨越1994改款，改款后两门敞篷外廓。	READY
1817_3dr	1817	Hatchback	Astra F		3	EU-OPEL-ASTRA-F-HATCHBACK-3D-01	MEDIUM	三门掀背外廓。	READY
1817_5dr	1817	Hatchback	Astra F		5	EU-OPEL-ASTRA-F-HATCHBACK-5D-01	MEDIUM	五门掀背外廓。	READY
1818	1818	Sedan	Astra F		4	EU-OPEL-ASTRA-F-SEDAN-4D-01	HIGH	四门三厢外廓。	READY
1819	1819	Hatchback	Astra F GSi		3	EU-OPEL-ASTRA-F-HATCHBACK-GSI-3D-01	HIGH	GSi三门宽保险杠外廓。	READY
1820	1820	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1821	1821	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1822	1822	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1823	1823	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1824	1824	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1825	1825	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1826	1826	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1827	1827	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1828	1828	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1829	1829	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1830	1830	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1831	1831	Wagon	Astra F Caravan		5	EU-OPEL-ASTRA-F-WAGON-5D-01	HIGH	五门旅行车外廓。	READY
1832	1832	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH	五门长轴封闭式外廓。	READY
1833	1833	SUV	Frontera A Sport		3	EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	HIGH	三门短轴开放式Sport外廓。	READY
1834	1834	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH	五门长轴封闭式外廓。	READY
1835_3dr	1835	SUV	Monterey A		3	EU-OPEL-MONTEREY-A-SUV-3D-SWB-01	MEDIUM	Ktype覆盖三门短轴分支。	READY
1835_5dr	1835	SUV	Monterey A		5	EU-OPEL-MONTEREY-A-SUV-5D-LWB-01	MEDIUM	Ktype覆盖五门长轴分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1701-1800_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SCIROCCO-I-COUPE-3D-01	3885	1624	1309	Auto-Data Volkswagen Scirocco I (53)	https://www.auto-data.net/en/volkswagen-scirocco-i-53-generation-1889
EU-VW-SCIROCCO-II-COUPE-3D-01	4050	1645	1280	Auto-Data Volkswagen Scirocco II (53B)	https://www.auto-data.net/en/volkswagen-scirocco-ii-53b-generation-1888
EU-VW-CORRADO-53I-COUPE-PREFL-01	4048	1674	1318	Carfolio 1988 Volkswagen Corrado G60	https://www.carfolio.com/volkswagen-corrado-g60-automatic-602426
EU-VW-CORRADO-53I-COUPE-FACELIFT-01	4050	1690	1310	Auto-Data Volkswagen Corrado facelift 1991 2.0i 16V	https://www.auto-data.net/en/volkswagen-corrado-53i-facelift-1991-2.0i-16v-136hp-9066
EU-FIAT-SEDICI-I-SUV-4X2-01	4115	1755	1605	Fiat Sedici official technical specifications	https://www.media.stellantis.com/uploads/gr/GR/2014/FIAT/SPECIFICATIONS/Fiat-Sedici-Tech-Specs.pdf
EU-FIAT-SEDICI-I-SUV-4X4-01	4115	1755	1620	Fiat Sedici official technical specifications; Auto-Data Fiat Sedici 2.0 Multijet 4x4	https://www.media.stellantis.com/uploads/gr/GR/2014/FIAT/SPECIFICATIONS/Fiat-Sedici-Tech-Specs.pdf; https://www.auto-data.net/en/fiat-sedici-facelift-2009-2.0-16v-multijet-135hp-4x4-18369
EU-VW-181-TYPE-181-SUV-OPEN-01	3780	1641	1621	Auto-Data Volkswagen 181	https://www.auto-data.net/en/volkswagen-181-generation-1850
EU-VW-ILTIS-TYPE-183-SUV-OPEN-01	3880	1520	1840	Carfolio Volkswagen Iltis	https://www.carfolio.com/volkswagen-iltis-73007
EU-VW-TRANSPORTER-T2-MPV-PREFL-01	4420	1765	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	4505	1720	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	4655	1840	1940	Auto-Data Volkswagen Caravelle T4 2.5	https://www.auto-data.net/en/volkswagen-caravelle-t4-2.5-110hp-49330
EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	4789	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Syncro	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-2.5-110hp-syncro-49352
EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	5055	1840	1940	Auto-Data Volkswagen Caravelle T4 Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-long-2.5-110hp-49339
EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	5189	1840	1940	Auto-Data Volkswagen Caravelle T4 facelift Long	https://www.auto-data.net/en/volkswagen-caravelle-t4-facelift-1996-long-2.5-115hp-syncro-49368
EU-OPEL-MONZA-A1-COUPE-3D-01	4692	1734	1380	Auto-Data Opel Monza A1 2.8	https://www.auto-data.net/en/opel-monza-a1-2.8-140hp-1749
EU-OPEL-MONZA-A2-COUPE-3D-01	4720	1722	1380	Auto-Data Opel Monza A2 2.0 E	https://www.auto-data.net/en/opel-monza-a2-2.0-e-115hp-1745
EU-VAUXHALL-CHEVETTE-SEDAN-01	4188	1570	1313	Auto-Data Vauxhall Chevette Sedan	https://www.auto-data.net/en/vauxhall-chevette-generation-1409
EU-VAUXHALL-CHEVETTE-WAGON-3D-01	4188	1570	1323	Auto-Data Vauxhall Chevette Estate	https://www.auto-data.net/en/vauxhall-chevette-estate-1.3-n-53hp-6063
EU-OPEL-CALIBRA-A-COUPE-3D-01	4492	1688	1320	Auto-Data Opel Calibra 2.0; Auto-Data Opel Calibra facelift Turbo 4x4	https://www.auto-data.net/en/opel-calibra-2.0-115hp-2544; https://www.auto-data.net/en/opel-calibra-facelift-1994-2.0-16v-turbo-204hp-4x4-43405
EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	4600	1845	1950	Auto-Data Volkswagen Caravelle T3 1.6 D	https://www.auto-data.net/en/volkswagen-caravelle-t3-1.6-d-50hp-manual-4-speed-49401
EU-OPEL-ASTRA-F-HATCHBACK-3D-01	4051	1688	1410	Auto-Data Opel Astra F 1.6 Si	https://www.auto-data.net/en/opel-astra-f-1.6-si-100hp-automatic-34944
EU-OPEL-ASTRA-F-HATCHBACK-5D-01	4051	1688	1410	Auto-Data Opel Astra F 1.6 Si	https://www.auto-data.net/en/opel-astra-f-1.6-si-100hp-automatic-34944
EU-OPEL-ASTRA-F-SEDAN-4D-01	4239	1688	1410	Auto-Data Opel Astra F Classic 1.7 D	https://www.auto-data.net/en/opel-astra-f-classic-1.7-d-57hp-2461
EU-OPEL-ASTRA-F-CONVERTIBLE-PREFL-01	4239	1688	1400	CarAraC Opel Astra Cabriolet 1993 specifications	https://cararac.com/spec/opel/astra/cabriolet-1993/
EU-OPEL-ASTRA-F-CONVERTIBLE-FACELIFT-01	4239	1684	1400	Auto-Data Opel Astra F Cabrio facelift 1.6i	https://www.auto-data.net/en/opel-astra-f-cabrio-facelift-1994-1.6i-75hp-automatic-35102
EU-OPEL-ASTRA-F-HATCHBACK-GSI-3D-01	4086	1688	1410	Auto-Data Opel Astra F GSi 2.0 16V	https://www.auto-data.net/en/opel-astra-f-gsi-2.0-16v-150hp-2510
EU-OPEL-ASTRA-F-WAGON-5D-01	4278	1688	1475	Auto-Data Opel Astra F Caravan 1.7 D	https://www.auto-data.net/en/opel-astra-f-caravan-1.7-d-57hp-2485
EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	4692	1764	1753	Auto-Data Opel Frontera A 2.3 TD 4x4	https://www.auto-data.net/en/opel-frontera-a-2.3-td-100hp-4x4-2563
EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	4192	1780	1721	Auto-Data Opel Frontera A Sport 2.0i	https://www.auto-data.net/en/opel-frontera-a-sport-2.0i-115hp-25874
EU-OPEL-MONTEREY-A-SUV-3D-SWB-01	4270	1745	1835	AutoData24 Opel Monterey A 3.1 TD 3-door	https://autodata24.com/opel/monterey/monterey-a/31-td-3-dr-114-hp/details
EU-OPEL-MONTEREY-A-SUV-5D-LWB-01	4700	1745	1840	Auto-Data Opel Monterey LTD 3.1 TD	https://www.auto-data.net/en/opel-monterey-ltd-3.1-td-114hp-4x4-2574
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1701-1800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volkswagen-caravelle-t3-1.6-d-50hp-manual-4-speed-49401 "Volkswagen Caravelle (T3) 1.6 D (50 Hp) Manual 4-speed | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-frontera-a-2.3-td-100hp-4x4-2563 "Opel Frontera A 2.3 TD (100 Hp) 4x4 | Technical specs, data, fuel consumption, Dimensions"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1701-1800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1701-1800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2278 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（563 行）
