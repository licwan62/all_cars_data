# 任务：all 第 901-1000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0010__9080f553


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 901-1000 行

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
all 第 901-1000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A4 b8 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	180	245	Nov 2011	Dec 2015	2024-03-01	20119
VW	Jetta i	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1981	Jul 1983	2024-03-01	20120
Mercedes-benz	124	200 E	Stufenheck	Heckantrieb	Benzin	77	105	Nov 1992	May 1993	2024-03-01	20122
Mitsubishi	Colt iv	1.6 4WD	Schrägheck	Allrad	Benzin	84	114	Aug 1993	Aug 1995	2024-03-01	20133
Mercedes-benz	190	2.3	Stufenheck	Heckantrieb	Benzin	97	132	Sep 1987	Sep 1988	2024-03-01	20136
Mercedes-benz	190	2.3 E	Stufenheck	Heckantrieb	Benzin	100	136	Oct 1982	Sep 1988	2024-03-01	20137
Mercedes-benz	190	2.6	Stufenheck	Heckantrieb	Benzin	118	160	Oct 1982	Sep 1988	2024-03-01	20138
Seat	Cordoba	1.4	Stufenheck	Frontantrieb	Benzin	40	54	Dec 1997	Apr 1999	2024-03-01	20143
Citroën	Xm	3	Schrägheck	Frontantrieb	Benzin	123	167	May 1989	May 1994	2024-03-01	20152
Saab	9000	2.3	Stufenheck	Frontantrieb	Benzin	165	224	Sep 1990	Oct 1998	2024-03-01	20159
Porsche	911	3.6 S	Cabriolet	Heckantrieb	Benzin	331	450	Aug 2004	Aug 2005	2024-03-01	20165
Lada	Samara	1.5	Schrägheck	Frontantrieb	Benzin	56	76	Apr 1996	Dec 2013	2024-03-01	20166
Porsche	911	3.8 Carrera 4S	Cabriolet	Allrad	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20170
Peugeot	205 i	1.1	Cabriolet	Frontantrieb	Benzin	40	54	Aug 1987	Dec 1994	2024-03-01	20195
Peugeot	205 ii	1	Schrägheck	Frontantrieb	Benzin	37	50	Aug 1992	May 1997	2024-03-01	20204
Peugeot	205 ii	1.1 XA	Schrägheck	Frontantrieb	Benzin	40	54	Jul 1987	Oct 1988	2024-03-01	20205
Volvo	960	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	121	165	Sep 1990	Aug 1993	2024-03-01	20209
Volvo	960	2.8 GL	Stufenheck	Heckantrieb	Benzin	108	147	Sep 1990	May 1992	2024-03-01	20210
Volvo	960	2.3 Turbo	Kombi	Heckantrieb	Benzin	121	165	Sep 1990	Aug 1993	2024-03-01	20214
Fiat	Ducato	2.8 TD 4X4	Kasten	Allrad	Diesel	90	122	May 1998	Sep 2001	2024-03-01	20229
Mazda	323 ii	1.6 GLX	Stufenheck	Frontantrieb	Benzin	54	73	Jun 1986	Mar 1987	2024-03-01	20232
Mazda	323 iii	1.6 GLX	Stufenheck	Frontantrieb	Benzin	54	73	Jun 1986	Mar 1987	2024-03-01	20235
Fiat	Fiorino	1.7 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	46	63	Nov 1996	May 2000	2024-03-01	20266
Peugeot	605	3	Stufenheck	Frontantrieb	Benzin	123	167	Aug 1989	Jun 1994	2024-03-01	20280
Peugeot	605	3	Stufenheck	Frontantrieb	Benzin	147	200	Aug 1989	Jun 1994	2024-03-01	20281
Renault	19 i chamade	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1990	Apr 1992	2024-03-01	20302
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	82	111	Sep 1990	Aug 1992	2024-03-01	20317
Volvo	740	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	114	155	Sep 1990	Aug 1991	2024-03-01	20319
Citroën	C25	2.5 D	Bus	Frontantrieb	Diesel	55	75	Nov 1981	Jan 1994	2024-03-01	20326
Toyota	Camry	2.4	Stufenheck	Frontantrieb	Benzin	116	158	Jan 2006	Sep 2011	2024-03-01	20332
Honda	Civic viii	1.8	Stufenheck	Frontantrieb	Benzin	103	140	Sep 2005	Feb 2012	2024-03-01	20348
Nissan	Laurel	2.0 GL	Stufenheck	Heckantrieb	Benzin	75	102	Nov 1984	Dec 1985	2024-03-01	20358
Nissan	Laurel	2.0 GL	Stufenheck	Heckantrieb	Benzin	75	102	Nov 1984	Dec 1985	2024-03-01	20361
Nissan	Sunny	1.6 4X4	Stufenheck	Allrad	Benzin	66	90	Jul 1986	Oct 1988	2024-03-01	20366
Nissan	Primera	1.6 Visia	Kombi	Frontantrieb	Benzin	80	109	Jan 2002	Apr 2006	2024-03-01	20403
Honda	Crx ii	1.4 GL	Coupe	Frontantrieb	Benzin	66	90	Jan 1990	Dec 1991	2024-03-01	20415
Subaru	Impreza	2.0 AWD	Stufenheck	Allrad	Benzin	206	280	Sep 1996	Sep 2000	2025-06-01	20427
KIA	Sportage ii	2.0 Crdi	SUV	Frontantrieb	Diesel	83	113	Feb 2005	Dec 2006	2024-05-01	20433
Maserati	Biturbo	430	Stufenheck	Heckantrieb	Benzin	165	224	Oct 1991	Sep 1994	2024-03-01	20436
Honda	Civic vi hatchback	1.6	Schrägheck	Frontantrieb	Benzin	92	125	Nov 1998	Mar 2001	2024-03-01	20440
Proton	Persona 400	1.8	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2000	Dec 2001	2024-03-01	20442
Proton	Persona 400	416	Stufenheck	Frontantrieb	Benzin	70	95	Aug 2000	Feb 2002	2024-03-01	20443
Mitsubishi	Eclipse iv	2.4 GS	Coupe	Frontantrieb	Benzin	120	163	Apr 2005	Dec 2011	2024-03-01	20447
Volvo	S40 i	1.8	Stufenheck	Frontantrieb	Benzin	85	116	Jun 2001	Aug 2003	2024-03-01	20459
Mercedes-benz	C-Klasse	C 220	Coupe	Heckantrieb	Benzin	120	163	May 2002	May 2008	2024-03-01	20460
Peugeot	Expert	1.9 D	Bus	Frontantrieb	Diesel	51	69	Dec 2003	Dec 2006	2024-03-01	20469
Peugeot	Expert	2.0 HDI	Bus	Frontantrieb	Diesel	69	94	Oct 2000	Oct 2006	2024-03-01	20470
Mitsubishi	L200	2.5 TD	Pick-up	Heckantrieb	Diesel	66	90	Aug 2001	Nov 2005	2024-03-01	20474
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	48	65	Feb 2012	-	2024-03-01	20475
Fiat	Marea	1.6 SX	Stufenheck	Frontantrieb	Benzin	72	98	Sep 2000	Aug 2002	2024-03-01	20481
VW	Transporter t5	VR6 3.2 4motion	Kasten	Allrad	Benzin	173	235	Nov 2003	Nov 2009	2024-03-01	20485
VW	Transporter t4	2.8	Pritsche/Fahrgestell	Frontantrieb	Benzin	103	140	May 1996	May 2000	2024-03-01	20486
Lada	Samara	1.5	Stufenheck	Frontantrieb	Benzin	57	78	Jan 2000	Dec 2006	2024-03-01	20498
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20506
Honda	Civic vi fastback	1.6	Schrägheck	Frontantrieb	Benzin	92	125	Nov 1998	Feb 2001	2024-03-01	20511
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	160	218	Nov 1995	May 1999	2024-03-01	20516
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	225	306	Nov 1995	May 1999	2024-03-01	20517
Ford USA	Mustang convertible	4.6	Cabriolet	Heckantrieb	Benzin	160	218	Nov 1995	May 1999	2024-03-01	20518
Ford USA	Mustang convertible	4.6	Cabriolet	Heckantrieb	Benzin	228	310	Nov 1995	May 1999	2024-03-01	20519
Ssangyong	Korando	2.3 Tdic 4X4	Geländewagen geschlossen	Allrad	Diesel	74	101	Jul 1998	Nov 2006	2024-03-01	20521
Hyundai	H-1 / starex	2.5 TCI	Bus	Heckantrieb	Diesel	73	99	Oct 1997	Dec 2007	2024-03-01	20542
Hyundai	H-1 / starex	2.5 TCI	Bus	Heckantrieb	Diesel	74	101	May 2004	Dec 2007	2024-03-01	20543
Hyundai	H-1 / starex	2.5 Crdi	Bus	Heckantrieb	Diesel	103	140	Dec 2002	Sep 2007	2024-03-01	20544
Opel	Antara a	2.4 4X4	SUV	Allrad	Benzin	103	140	Aug 2006	Dec 2011	2024-03-01	20545
Hyundai	H-1 / starex	2.5 Crdi 4WD	Bus	Allrad	Diesel	103	140	Dec 2002	Apr 2004	2024-03-01	20546
Chevrolet	Beretta	2.8 GT	Coupe	Frontantrieb	Benzin	93	126	Oct 1988	Sep 1989	2024-03-01	20547
Chevrolet	Beretta	3.1 LT	Coupe	Frontantrieb	Benzin	103	140	Oct 1992	Sep 1993	2024-03-01	20548
Chevrolet	Beretta	3.1 Z26	Coupe	Frontantrieb	Benzin	119	162	Oct 1993	Sep 1996	2024-03-01	20549
Chevrolet	Corsica	3.1	Stufenheck	Frontantrieb	Benzin	106	144	Oct 1989	Sep 1992	2024-03-01	20553
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	110	150	Jun 2001	Jun 2006	2024-03-01	20556
Saab	9-5	2.0 T	Stufenheck	Frontantrieb	Benzin	136	185	Jul 2000	Dec 2009	2024-03-01	20565
Saab	9-5	2.0 Turbo SE	Stufenheck	Frontantrieb	Benzin	141	192	Oct 1998	Jul 2000	2024-03-01	20566
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	224	305	Jun 2003	Aug 2005	2024-03-01	20567
Fiat	Palio	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1997	Aug 2002	2024-03-01	20569
Fiat	Palio	1.3	Kombi	Frontantrieb	Benzin	59	80	Sep 2001	Oct 2004	2024-11-01	20576
Fiat	Palio	1.9 JTD	Kombi	Frontantrieb	Diesel	59	80	Sep 2001	-	2024-03-01	20581
Daewoo	Nubira	2.0 CDX	Schrägheck	Frontantrieb	Benzin	93	126	Aug 2002	Jul 2003	2024-03-01	20586
Chrysler	Voyager ii	3	Großraumlimousine	Frontantrieb	Benzin	104	141	Oct 1990	Sep 1995	2024-03-01	20618
Buick	Park avenue	3.8 Supercharged	Stufenheck	Frontantrieb	Benzin	179	243	Oct 1996	Dec 2005	2024-03-01	20620
Hyundai	Atos	1.1	Schrägheck	Frontantrieb	Benzin	43	58	Aug 2003	Dec 2008	2024-03-01	20623
Citroën	C25	1.9 D 1400	Kasten	Frontantrieb	Diesel	51	69	Jan 1988	Jan 1994	2024-03-01	20628
Citroën	C25	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	57	78	Nov 1981	Dec 1986	2024-03-01	20631
Citroën	C25	2.5 DT	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Jan 1987	Jan 1994	2024-03-01	20633
Daihatsu	Sirion	1.3 4WD	Schrägheck	Allrad	Benzin	64	87	Apr 2005	-	2024-03-01	20634
Saab	9-3	2.3	Schrägheck	Frontantrieb	Benzin	169	230	Sep 1999	Jan 2002	2024-03-01	20635
Saab	9-3	2.0 Turbo Performance	Cabriolet	Frontantrieb	Benzin	185	252	Apr 2004	Feb 2015	2024-03-01	20636
Saab	9-3	2.3	Cabriolet	Frontantrieb	Benzin	169	230	Sep 1999	Jan 2002	2024-03-01	20637
Mercedes-benz	Clk	CLK 320 CDI	Cabriolet	Heckantrieb	Diesel	165	224	Mar 2005	Mar 2010	2024-03-01	20640
Nissan	Pathfinder iii	2.5 DCI	SUV	Heckantrieb	Diesel	128	174	Jan 2005	Jan 2010	2024-05-01	20643
Toyota	Rav 4 iii	2.4	SUV	Frontantrieb	Benzin	125	170	Nov 2005	Dec 2013	2024-03-01	20645
Saab	9-5	2.0 T Biopower	Kombi	Frontantrieb	Benzin/Ethanol	132	179	Sep 2005	Dec 2009	2024-03-01	20646
Saab	9-5	2.0 T	Kombi	Frontantrieb	Benzin	136	185	Jul 2000	Jul 2001	2024-03-01	20647
Lotus	Esprit s4	2.0 GT3	Coupe	Heckantrieb	Benzin	179	243	Sep 1996	Jun 2000	2024-03-01	20649
Mazda	323 s vi	2.0 Ditd	Stufenheck	Frontantrieb	Diesel	74	101	Oct 2000	Oct 2002	2024-03-01	20654
VW	Vento	2.0 GL	Stufenheck	Frontantrieb	Benzin	79	107	May 1996	Dec 1997	2024-03-01	20659
VW	Transporter t5	3.2 V6 4motion	Bus	Allrad	Benzin	173	235	Nov 2003	Dec 2009	2024-03-01	20661
Honda	Accord vi	1.6 LS	Stufenheck	Frontantrieb	Benzin	79	107	Oct 1998	Dec 2002	2024-03-01	20663
Nissan	Patrol gr v wagon	4.8	Geländewagen geschlossen	Allrad	Benzin	180	245	Mar 2000	-	2024-03-01	20673
BMW	3	330 I	Coupe	Heckantrieb	Benzin	190	258	Mar 2010	Jun 2013	2024-03-01	20683
Peugeot	Boxer	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	81	110	Dec 2001	Apr 2002	2024-03-01	20693


--- Round 1 / 首次发送 ---
## 更新点

* 首轮按物理外廓聚类，已闭合 Audi A4 B8 Avant、Mercedes-Benz W124/W201、Seat Cordoba I、Citroën XM Y3、Saab 9000 CD、Peugeot 205、Volvo 960 共 **10 个尺寸组**。已确认的宽度均采用车身宽度，不使用含后视镜宽度。([汽车数据网][1])
* Peugeot 205 Cabriolet 与 facelift Hatchback 外廓不同，分别建组；Volvo 960 Sedan 与 Wagon 分别使用 964、965 尺寸组。([汽车数据网][2])
* 发动机功率差异未重复建组；同一代、同一物理车身的 Ktype 直接复用现有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：14
* READY 映射：14
* PENDING Ktype：86
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20119	20119	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-WAGON-FACELIFT-01	HIGH	8K5五门旅行车改款外廓。	READY
20122	20122	Sedan	W124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-01	MEDIUM	W124四门轿车外廓。	READY
20136	20136	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-01	HIGH		READY
20137	20137	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-01	HIGH		READY
20138	20138	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-01	HIGH		READY
20143	20143	Sedan	Cordoba I		4	EU-SEAT-CORDOBA-I-SEDAN-01	MEDIUM	第一代改款前四门轿车外廓。	READY
20152	20152	Hatchback	XM Y3	Y3	5	EU-CITROEN-XM-Y3-HATCHBACK-01	HIGH	Y3五门掀背外廓。	READY
20159	20159	Sedan	9000 CD	CD	4	EU-SAAB-9000-CD-SEDAN-01	MEDIUM	CD/CDE四门轿车外廓。	READY
20195	20195	Convertible	205 I Cabrio	20D	2	EU-PEUGEOT-205-I-CONVERTIBLE-01	MEDIUM	20D敞篷车外廓。	READY
20204	20204	Hatchback	205 I facelift			EU-PEUGEOT-205-I-HATCHBACK-FACELIFT-01	MEDIUM	该版本资料覆盖三门和五门；两者共用相同外廓，Ktype未限定门数。	READY
20205	20205	Hatchback	205 I facelift		3	EU-PEUGEOT-205-I-HATCHBACK-FACELIFT-01	MEDIUM	XA三门商用掀背外廓。	READY
20209	20209	Sedan	960 (964)	964	4	EU-VOLVO-960-964-SEDAN-01	HIGH		READY
20210	20210	Sedan	960 (964)	964	4	EU-VOLVO-960-964-SEDAN-01	HIGH		READY
20214	20214	Wagon	960 Kombi (965)	965	5	EU-VOLVO-960-965-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B8-WAGON-FACELIFT-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 facelift generation	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-generation-4134
EU-MERCEDES-BENZ-124-W124-SEDAN-01	4740	1740	1428	Auto-Data Mercedes-Benz W124 facelift 200 E	https://www.auto-data.net/en/mercedes-benz-w124-facelift-1989-200-e-118hp-43326
EU-MERCEDES-BENZ-190-W201-SEDAN-01	4420	1678	1390	Auto-Data Mercedes-Benz 190 W201 E 2.3	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808
EU-SEAT-CORDOBA-I-SEDAN-01	4109	1640	1408	Auto-Data Seat Cordoba I 1.4 i	https://www.auto-data.net/en/seat-cordoba-i-1.4-i-60hp-13446
EU-CITROEN-XM-Y3-HATCHBACK-01	4708	1794	1385	Auto-Data Citroen XM Y3 generation	https://www.auto-data.net/en/citroen-xm-y3-generation-3319
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420	Auto-Data Saab 9000 CDE sedan	https://www.auto-data.net/en/saab-9000-2.3-16v-cde-eco-power-170hp-11877
EU-PEUGEOT-205-I-CONVERTIBLE-01	3705	1590	1375	Auto-Data Peugeot 205 I Cabrio generation	https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276
EU-PEUGEOT-205-I-HATCHBACK-FACELIFT-01	3705	1560	1375	Auto-Data Peugeot 205 I facelift 1.0	https://www.auto-data.net/en/peugeot-205-i-20a-c-facelift-1987-1.0-45hp-5638
EU-VOLVO-960-964-SEDAN-01	4871	1750	1411	Auto-Data Volvo 960 model specifications	https://www.auto-data.net/en/volvo-960-model-926
EU-VOLVO-960-965-WAGON-01	4850	1750	1434	Auto-Data Volvo 960 Kombi 965 generation	https://www.auto-data.net/en/volvo-960-kombi-965-generation-1946
```

## 下一步优先处理

1. 闭合可批量复用的轿车/旅行车组：Peugeot 605、Volvo 740、Nissan Laurel、Nissan Sunny、Toyota Camry XV40、Honda Civic VIII、Nissan Primera P12。
2. 处理 Porsche 911 的 996 Turbo S Cabriolet、997 Carrera S Cabriolet及宽体 Carrera 4S Cabriolet，避免错误共组。
3. 将 Ducato、C25、Expert、Transporter T4/T5、H-1 等多轴距及多车顶商用车留到独立分支核对。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-generation-4134?utm_source=chatgpt.com "Audi A4 Avant (B8 8K, facelift 2011) | Technical Specs ..."
[2]: https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276 "Peugeot 205 I Cabrio (741B,20D) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 Peugeot 605、Renault 19 I Chamade、Volvo 740 Sedan、Toyota Camry XV40、Honda Civic VIII Sedan、Nissan Primera P12 Wagon 共 **6 个尺寸组**。
* 新增 **8 条 READY 映射**；相同外廓的发动机版本直接复用尺寸组。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：22
* PENDING Ktype：78
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20280	20280	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-01	HIGH		READY
20281	20281	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-01	HIGH		READY
20302	20302	Sedan	19 I Chamade	L53	4	EU-RENAULT-19-I-CHAMADE-SEDAN-01	HIGH	L53四门Chamade轿车外廓。	READY
20317	20317	Sedan	740	744	4	EU-VOLVO-740-744-SEDAN-01	MEDIUM		READY
20319	20319	Sedan	740	744	4	EU-VOLVO-740-744-SEDAN-01	MEDIUM		READY
20332	20332	Sedan	Camry VI	XV40	4	EU-TOYOTA-CAMRY-XV40-SEDAN-PREFL-01	HIGH	改款前XV40四门轿车外廓。	READY
20348	20348	Sedan	Civic VIII		4	EU-HONDA-CIVIC-VIII-SEDAN-01	HIGH		READY
20403	20403	Wagon	Primera P12	P12	5	EU-NISSAN-PRIMERA-P12-WAGON-01	HIGH	P12五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-605-6B-SEDAN-01	4765	1799	1418	Auto-Data Peugeot 605 (6B) generation	https://www.auto-data.net/en/peugeot-605-6b-generation-1231
EU-RENAULT-19-I-CHAMADE-SEDAN-01	4262	1694	1412	Auto-Data Renault 19 I Chamade (L53) generation	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-VOLVO-740-744-SEDAN-01	4785	1760	1430	Auto-Data Volvo 740 (744) generation	https://www.auto-data.net/en/volvo-740-744-generation-1954
EU-TOYOTA-CAMRY-XV40-SEDAN-PREFL-01	4815	1820	1480	Auto-Data Toyota Camry VI (XV40) generation	https://www.auto-data.net/en/toyota-camry-vi-xv40-generation-1008
EU-HONDA-CIVIC-VIII-SEDAN-01	4550	1753	1435	Auto-Data Honda Civic VIII Sedan generation	https://www.auto-data.net/en/honda-civic-viii-sedan-generation-2620
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480	Auto-Data Nissan Primera Wagon (P12) generation	https://www.auto-data.net/en/nissan-primera-wagon-p12-generation-182
```

## 下一步优先处理

1. 批量闭合 Honda Civic VI Hatchback/Fastback、Honda Accord VI、Mazda 323 S VI 等乘用车组。
2. 处理 Porsche 911 Cabriolet 的 996、997 Carrera S 与宽体 Carrera 4S 分支。
3. 将 Ducato、C25、Expert、Transporter、H-1 等多轴距或多车顶商用车继续留作独立拆分。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-605-6b-generation-1231 "Peugeot 605 (6B) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新闭合 Honda Civic VI 三门 Hatchback、Honda Civic VI 五门 Fastback、Honda Accord VI 欧洲版 Sedan 共 **3 个尺寸组**。
* 新增 **3 条 READY 映射**；Civic VI 三门与五门 Fastback 外廓不同，分别建组。Honda 官方历史资料显示上一代 Civic 三门与五门在长度和高度上存在差异。([本田新闻][1])
* Accord VI 1.6 LS 已按欧洲四门车型边界闭合为 4595 × 1750 × 1430 mm。([本田新闻][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：25
* PENDING Ktype：75
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20440	20440	Hatchback	Civic VI		3	EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	HIGH	三门Hatchback物理外廓。	READY
20511	20511	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	五门Fastback物理外廓。	READY
20663	20663	Sedan	Accord VI Europe		4	EU-HONDA-ACCORD-VI-EUROPE-SEDAN-01	MEDIUM	欧洲版四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	4185	1695	1375	Honda Civic 01 3 Door official press information	https://hondanews.eu/eu/en/cars/media/pressreleases/34356/civic-01-3-door
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Honda Geneva Motor Show 2001 official press information	https://hondanews.eu/eu/en/cars/media/pressreleases/34365/geneva-motorshow-2001
EU-HONDA-ACCORD-VI-EUROPE-SEDAN-01	4595	1750	1430	Honda Geneva Motor Show 2000 official press information	https://hondanews.eu/eu/en/cars/media/pressreleases/34359/geneva-motorshow-2000
```

## 下一步优先处理

1. 闭合 Mazda 323 II/III Sedan、Mazda 323 S VI 与 VW Jetta I/Vento 可批量处理的乘用车组。
2. 处理 Porsche 911 996 Turbo S Cabriolet、997 Carrera S Cabriolet及宽体 Carrera 4S Cabriolet三个独立外廓。
3. 随后处理 Ford Mustang SN95 Coupe/Convertible、Chevrolet Beretta/Corsica等美系共平台车型。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/en/cars/media/pressreleases/34356/civic-01-3-door?utm_source=chatgpt.com "Civic 01 - 3 Door"
[2]: https://hondanews.eu/eu/en/cars/media/pressreleases/34359/geneva-motorshow-2000?utm_source=chatgpt.com "Geneva Motorshow 2000"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Porsche 911 的 996 Turbo S Cabriolet、997 Carrera S Cabriolet 与宽体 Carrera 4S Cabriolet 三个独立外廓；后驱 Carrera S 与四驱宽体 Carrera 4S 不共用尺寸组。([Stuttcars][1])
* 闭合 Mazda 323 S VI BJ 改款 Sedan 与 VW Vento 1H Sedan 两个尺寸组。([汽车数据网][2])
* 本轮新增 5 条 READY 映射、5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：30
* PENDING Ktype：70
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20165	20165	Convertible	911 Turbo S (996)	996	2	EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-01	HIGH	996 Turbo S宽体敞篷外廓。	READY
20170	20170	Convertible	911 Carrera 4S (997)	997	2	EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	HIGH	997 Carrera 4S宽体敞篷外廓。	READY
20506	20506	Convertible	911 Carrera S (997)	997	2	EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	HIGH	997 Carrera S后驱敞篷外廓。	READY
20654	20654	Sedan	323 S VI facelift	BJ	4	EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	HIGH	BJ改款四门轿车外廓。	READY
20659	20659	Sedan	Vento (1H)	1H2	4	EU-VW-VENTO-1H-SEDAN-01	MEDIUM	1H四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-01	4435	1830	1295	Stuttcars Porsche 911 Turbo S Cabriolet 996 specifications	https://www.stuttcars.com/porsche-911-turbo-s-cabriolet-996-2004-2005/
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300	Porsche 911 Carrera 4 and Carrera 4S Cabriolet specification sheet	https://autoinfo.jp/release/911_Carrera_4_Cabriolet_my07_spec.pdf
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300	Encycarpedia Porsche 911 Carrera S Cabriolet 997 specifications	https://www.encycarpedia.com/porsche/05-911-carrera-s-cabriolet-convertible
EU-MAZDA-323-BJ-SEDAN-FACELIFT-01	4390	1705	1410	Auto-Data Mazda 323 S VI BJ 2.0 DiTD 101 Hp	https://www.auto-data.net/en/mazda-323-s-vi-bj-2.0-ditd-101hp-11150
EU-VW-VENTO-1H-SEDAN-01	4380	1695	1415	Auto-Data Volkswagen Vento 1HX0 2.0	https://www.auto-data.net/en/volkswagen-vento-1hx0-2.0-115hp-8851
```

## 下一步优先处理

1. 处理 Mazda 323 II BD 与 323 III BF：两条 Ktype 的发动机和生产期相同，但车身代码不同，分别闭合物理外廓。
2. 闭合 VW Jetta I、Ford Mustang SN95 Coupe/Convertible 和 Chevrolet Beretta/Corsica。
3. 批量处理 Saab 9-5 Sedan/Wagon、Saab 9-3 Hatchback/Convertible 等可复用乘用车组。

推进信号：CONTINUE

[1]: https://www.stuttcars.com/porsche-911-turbo-s-cabriolet-996-2004-2005/?utm_source=chatgpt.com "Porsche 911 Turbo S Cabriolet (996) (2004)"
[2]: https://www.auto-data.net/en/mazda-323-s-vi-bj-2.0-ditd-101hp-11150?utm_source=chatgpt.com "Mazda 323 S VI (BJ) 2.0 DiTD (101 Hp) /Sedan 2000 - 2003"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 VW Jetta I Sedan 尺寸组，官方资料确认外廓为 4190 × 1610 × 1410 mm。([Volkswagen Newsroom][1])
* 闭合 Chevrolet Beretta 1989、1993 两个年份外廓；1991 年前后车身宽度和高度发生变化，因此未错误共组。
* 闭合 Chevrolet Corsica 1987–1993 Sedan 尺寸组。
* 1994–1996 Beretta Z26 官方尺寸存在年份差异，本轮不猜测落盘，留到下一轮拆分处理。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：34
* PENDING Ktype：66
* 已确认尺寸组：28
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20120	20120	Sedan	Jetta I	16		EU-VW-JETTA-I-SEDAN-01	HIGH	两门与四门版本采用相同外廓；Ktype未限定门数。	READY
20547	20547	Coupe	Beretta L-body	L	2	EU-CHEVROLET-BERETTA-L-COUPE-1988-1990-01	HIGH	1989款GT双门Coupe外廓。	READY
20548	20548	Coupe	Beretta L-body	L	2	EU-CHEVROLET-BERETTA-L-COUPE-1991-1993-01	HIGH	1993款双门Coupe外廓。	READY
20553	20553	Sedan	Corsica L-body	L	4	EU-CHEVROLET-CORSICA-L-SEDAN-1987-1993-01	HIGH	L平台四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-JETTA-I-SEDAN-01	4190	1610	1410	Volkswagen Newsroom Jetta I vehicle data profile	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-CHEVROLET-BERETTA-L-COUPE-1988-1990-01	4756	1733	1403	GM Heritage Archive 1989 Chevrolet Beretta Vehicle Information Kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1989-Chevrolet-Beretta.pdf
EU-CHEVROLET-BERETTA-L-COUPE-1991-1993-01	4757	1724	1346	GM Heritage Archive 1993 Chevrolet Beretta Vehicle Information Kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1993-Chevrolet-Beretta.pdf
EU-CHEVROLET-CORSICA-L-SEDAN-1987-1993-01	4660	1727	1371	GM Heritage Archive 1992 Chevrolet Corsica Vehicle Information Kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1992-Chevrolet-Corsica.pdf
```

## 下一步优先处理

1. 确认 Beretta Z26 在 1994、1995、1996 年的尺寸边界，并将 Ktype 20549 拆成稳定年份分支。
2. 闭合 Mazda 323 II BD、323 III BF 两个独立 Sedan 外廓。
3. 批量处理 Saab 9-5 Sedan/Wagon 的改款前、2001 facelift 和 2005 facelift 分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641?utm_source=chatgpt.com "Vehicle data Jetta I profile"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 新闭合 Fiat Panda III 标准前驱车身、Opel Antara A 改款前车身、VW Golf IV Variant 与 BMW 3 Series E92 facelift Coupé 共 **4 个尺寸组**。
* Panda 官方技术表明确区分标准车身与 Trekking/4x4 宽高，本 Ktype 使用标准前驱外廓 3653 × 1643 × 1551 mm；Antara 官方资料明确给出不含后视镜宽度 1850 mm。([Stellantis Media][1])
* Golf IV Variant 直接采用大众官方历史车型数据；BMW E92 使用 BMW 官方技术规格。([Volkswagen Newsroom][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：38
* PENDING Ktype：62
* 已确认尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20475	20475	Hatchback	Panda III		5	EU-FIAT-PANDA-III-HATCHBACK-01	MEDIUM	标准前驱五门外廓。	READY
20545	20545	SUV	Antara A pre-facelift		5	EU-OPEL-ANTARA-A-SUV-PREFL-01	HIGH	改款前五门SUV外廓。	READY
20556	20556	Wagon	Golf IV Variant	1J	5	EU-VW-GOLF-IV-VARIANT-WAGON-01	HIGH		READY
20683	20683	Coupe	3 Series E92 facelift	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	改款后双门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-PANDA-III-HATCHBACK-01	3653	1643	1551	Fiat Panda official technical specifications	https://www.media.stellantis.com/uploads/be/BE/2017/Fiat/files/140724_Panda_EN.pdf
EU-OPEL-ANTARA-A-SUV-PREFL-01	4575	1850	1704	Vauxhall Antara official product review	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/antara/Antara_Product_Review.pdf
EU-VW-GOLF-IV-VARIANT-WAGON-01	4397	1735	1485	Volkswagen Newsroom Golf IV Variant official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	BMW 3 Series Coupe official technical specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0079937EN_GB/119822
```

## 下一步优先处理

1. 批量闭合 Saab 9-5 Sedan 与 Wagon 的改款分支。
2. 处理 Ford Mustang SN95 Coupe、Convertible 及 Chevrolet Beretta Z26。
3. 随后处理 Nissan Pathfinder R51、Toyota RAV4 III、KIA Sportage II 等 SUV。
4. 商用车继续按轴距、车顶和车身形式独立拆分。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/be/BE/2017/Fiat/files/140724_Panda_EN.pdf "SchedeFiat_EN.xlsx"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523?utm_source=chatgpt.com "Vehicle data Golf IV Variant profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Saab 9-5 第一代 Sedan/Wagon 的 phase I 与 phase II/III 四个尺寸组。Ktype `20565` 覆盖尺寸变化前后两个阶段，已拆成两个派生映射；其余 Saab Ktype 直接关联对应物理外廓。
* 闭合 Kia Sportage II 五门 SUV 尺寸组。
* 本轮新增 **7 条 READY 映射行**，解决 **6 个 Ktype**，首次创建 **5 个尺寸组**。尺寸依据 Saab 原厂用户手册、Saab WIS 技术资料及 Auto-Data Sportage II 车型页。([汽车手册在线][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：44
* READY 映射行：45
* PENDING Ktype：56
* 已确认尺寸组：37
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20433	20433	SUV	Sportage II		5	EU-KIA-SPORTAGE-II-SUV-01	MEDIUM		READY
20565_prefl	20565	Sedan	9-5 I phase I	YS3E	4	EU-SAAB-9-5-YS3E-SEDAN-PHASE1-01	MEDIUM	Ktype覆盖改款前后外廓；本行为phase I。	READY
20565_facelift	20565	Sedan	9-5 I phase II/III	YS3E	4	EU-SAAB-9-5-YS3E-SEDAN-PHASE2-3-01	MEDIUM	Ktype覆盖改款前后外廓；本行为phase II/III。	READY
20566	20566	Sedan	9-5 I phase I	YS3E	4	EU-SAAB-9-5-YS3E-SEDAN-PHASE1-01	HIGH		READY
20567	20567	Sedan	9-5 I phase II	YS3E	4	EU-SAAB-9-5-YS3E-SEDAN-PHASE2-3-01	HIGH		READY
20646	20646	Wagon	9-5 I phase III	YS3E	5	EU-SAAB-9-5-YS3E-WAGON-PHASE2-3-01	HIGH		READY
20647	20647	Wagon	9-5 I phase I	YS3E	5	EU-SAAB-9-5-YS3E-WAGON-PHASE1-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SPORTAGE-II-SUV-01	4350	1840	1730	Auto-Data Kia Sportage II generation	https://www.auto-data.net/en/kia-sportage-ii-generation-619
EU-SAAB-9-5-YS3E-SEDAN-PHASE1-01	4805	1792	1449	Saab 9-5 MY2000 Owner's Manual	https://www.carmanualsonline.info/saab-9-5-2000-owners-manual/23
EU-SAAB-9-5-YS3E-SEDAN-PHASE2-3-01	4827	1792	1475	SAAB Workshop Information System 9-5 MY2002 General data	https://saabwisonline.com/9-5-9600/2002/0-general/general/technical-data/general-data
EU-SAAB-9-5-YS3E-WAGON-PHASE2-3-01	4828	1792	1501	SAAB Workshop Information System 9-5 MY2002 General data	https://saabwisonline.com/9-5-9600/2002/0-general/general/technical-data/general-data
EU-SAAB-9-5-YS3E-WAGON-PHASE1-01	4808	1792	1497	Saab 9-5 MY2000 Owner's Manual	https://www.carmanualsonline.info/saab-9-5-2000-owners-manual/23
```

## 下一步优先处理

1. 闭合 Ford Mustang SN95 Coupe、Convertible 及 Chevrolet Beretta Z26 年份分支。
2. 批量处理 Saab 9-3 Hatchback/Convertible、Mercedes-Benz CLK Cabriolet。
3. 继续处理 Hyundai H-1、VW Transporter、Citroën C25 等需要轴距或车身形式拆分的商用车。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/saab-9-5-2000-owners-manual/23 "SAAB 9-5 2000 Owners Manual (256 Pages), Page 230: 221 Maintenance and owner assistance Saab Ori ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Ford Mustang SN95 的 GT Coupé、SVT Cobra Coupé、GT Convertible、SVT Cobra Convertible 四个物理外廓。Ford 1998 技术资料显示普通 Mustang 与 Cobra 的长度分别为 181.5 英寸和 182.5 英寸，敞篷与硬顶高度也不同，因此不能合并为一个尺寸组。
* 闭合 Mercedes-Benz CLK 320 CDI A209 Cabriolet；采用 Mercedes-Benz 官方历史档案的 4652 × 1740 × 1415 mm 标准车身尺寸。([marsClassic][1])
* 本轮新增 5 条 READY 映射、首次创建 5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：49
* READY 映射行：50
* PENDING Ktype：51
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20516	20516	Coupe	Mustang IV SN95	SN95	2	EU-FORD-MUSTANG-SN95-COUPE-GT-01	HIGH	GT硬顶外廓。	READY
20517	20517	Coupe	Mustang IV SN95 SVT Cobra	SN95	2	EU-FORD-MUSTANG-SN95-COUPE-COBRA-01	HIGH	SVT Cobra前后外廓与GT不同。	READY
20518	20518	Convertible	Mustang IV SN95	SN95	2	EU-FORD-MUSTANG-SN95-CONVERTIBLE-GT-01	HIGH	GT敞篷外廓。	READY
20519	20519	Convertible	Mustang IV SN95 SVT Cobra	SN95	2	EU-FORD-MUSTANG-SN95-CONVERTIBLE-COBRA-01	HIGH	SVT Cobra敞篷外廓。	READY
20640	20640	Convertible	CLK II	A209	2	EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-320CDI-01	HIGH	A209双门敞篷车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MUSTANG-SN95-COUPE-GT-01	4610	1824	1351	Ford 1998 Mustang official sales brochure	https://xr793.com/wp-content/uploads/2016/10/1998-Ford-Mustang.pdf
EU-FORD-MUSTANG-SN95-COUPE-COBRA-01	4636	1824	1351	Ford 1998 SVT Mustang Cobra official technical data brochure	https://www.xr793.com/wp-content/uploads/2016/10/1998-Ford-Mustang-SVT-Cobra.pdf
EU-FORD-MUSTANG-SN95-CONVERTIBLE-GT-01	4610	1824	1356	Ford 1998 Mustang official sales brochure	https://xr793.com/wp-content/uploads/2016/10/1998-Ford-Mustang.pdf
EU-FORD-MUSTANG-SN95-CONVERTIBLE-COBRA-01	4636	1824	1354	Ford 1998 SVT Mustang Cobra official technical data brochure	https://www.xr793.com/wp-content/uploads/2016/10/1998-Ford-Mustang-SVT-Cobra.pdf
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-320CDI-01	4652	1740	1415	Mercedes-Benz Public Archive CLK 320 CDI Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-320-CDI-Cabriolet.xhtml?oid=2461903
```

## 下一步优先处理

1. 闭合 Saab 9-3 第一代 Hatchback、第一代 Cabriolet及第二代 Cabriolet 改款分支。
2. 处理 Nissan Pathfinder R51、Toyota RAV4 III、Nissan Patrol Y61 与 SsangYong Korando SUV。
3. 批量闭合 Fiat Palio Hatchback/Wagon、Daewoo Nubira、Proton Persona 400 和 Volvo S40 I。
4. 最后集中拆分多轴距、多车顶的 Ducato、C25、Expert、Transporter及H-1商用车。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CLK-320-CDI-Cabriolet.xhtml?oid=2461903 "CLK 320 CDI Cabriolet"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Saab 9-3 I Hatchback、Saab 9-3 I Cabriolet、Nissan Pathfinder R51、SsangYong Korando KJ、Daewoo Nubira II Hatchback、Proton Persona I Hatchback/Sedan、Nissan Patrol Y61 4.8 与 Toyota RAV4 XA30 Long 共 **9 个尺寸组**。
* Saab 9-3 Hatchback 与 Cabriolet 长宽相同但高度不同，分别建组；Proton Persona Hatchback 与 Sedan 长度不同，分别建组。([汽车数据网][1])
* Pathfinder R51、Korando KJ、Patrol Y61 4.8 和 RAV4 XA30 Long 均按明确车身代码及五门外廓闭合。([汽车数据网][2])
* 本轮新增 **9 条 READY 映射**、首次创建 **9 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：58
* READY 映射行：59
* PENDING Ktype：42
* 已确认尺寸组：51
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20442	20442	Hatchback	Persona I		5	EU-PROTON-PERSONA-I-HATCHBACK-01	MEDIUM	五门Hatchback外廓。	READY
20443	20443	Sedan	Persona I		4	EU-PROTON-PERSONA-I-SEDAN-01	MEDIUM	四门Sedan外廓。	READY
20521	20521	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-01	HIGH	KJ三门SUV外廓。	READY
20586	20586	Hatchback	Nubira II	J150	5	EU-DAEWOO-NUBIRA-II-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
20635	20635	Hatchback	9-3 I	YS3D		EU-SAAB-9-3-I-HATCHBACK-01	HIGH	三门与五门版本采用相同外廓；Ktype未限定门数。	READY
20637	20637	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-CONVERTIBLE-01	HIGH	第一代双门敞篷外廓。	READY
20643	20643	SUV	Pathfinder III	R51	5	EU-NISSAN-PATHFINDER-R51-SUV-PREFL-01	HIGH	改款前R51五门SUV外廓。	READY
20645	20645	SUV	RAV4 III Long	XA30	5	EU-TOYOTA-RAV4-XA30-LONG-SUV-PREFL-01	MEDIUM	XA30长轴五门改款前外廓。	READY
20673	20673	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-Y61-5D-4.8-PREFL-01	MEDIUM	Y61五门4.8改款前宽体外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PROTON-PERSONA-I-HATCHBACK-01	4270	1690	1385	Auto-Data Proton Persona I Hatchback specifications	https://www.auto-data.net/en/proton-persona-i-hatchback-1.6i-16v-416-glxi-113hp-8252
EU-PROTON-PERSONA-I-SEDAN-01	4360	1680	1385	Auto-Data Proton Persona I 416 GLXi specifications	https://www.auto-data.net/en/proton-persona-i-1.6-i-416-glxi-95hp-8257
EU-SSANGYONG-KORANDO-II-KJ-SUV-01	4260	1841	1840	Auto-Data SsangYong Korando II KJ 2.3 TD specifications	https://www.auto-data.net/en/ssangyong-korando-ii-kj-2.3-td-101hp-15995
EU-DAEWOO-NUBIRA-II-HATCHBACK-01	4280	1700	1430	Auto-Data Daewoo Nubira Hatchback II 2.0 CDX specifications	https://www.auto-data.net/en/daewoo-nubira-hatchback-ii-2.0-i-16v-cdx-126hp-16329
EU-SAAB-9-3-I-HATCHBACK-01	4629	1711	1428	Auto-Data Saab 9-3 I generation specifications	https://www.auto-data.net/en/saab-9-3-i-generation-2540
EU-SAAB-9-3-I-CONVERTIBLE-01	4629	1711	1423	Auto-Data Saab 9-3 Convertible I 2.3 T specifications	https://www.auto-data.net/en/saab-9-3-convertible-i-2.3-t-230hp-11970
EU-NISSAN-PATHFINDER-R51-SUV-PREFL-01	4877	1854	1879	Auto-Data Nissan Pathfinder III 2.5 DTi specifications	https://www.auto-data.net/en/nissan-pathfinder-iii-2.5-dti-174hp-4wd-924
EU-TOYOTA-RAV4-XA30-LONG-SUV-PREFL-01	4600	1815	1745	Auto-Data Toyota RAV4 III XA30 Long 2.4 VVT-i specifications	https://www.auto-data.net/en/toyota-rav4-iii-xa30-long-2.4-vvt-i-166hp-automatic-37237
EU-NISSAN-PATROL-Y61-5D-4.8-PREFL-01	5010	1930	1850	Auto-Data Nissan Patrol V Y61 4.8 5-door specifications	https://www.auto-data.net/en/nissan-patrol-v-5-door-y61-4.8-i-24v-5-dr-245hp-automatic-298
```

## 下一步优先处理

1. 闭合 Fiat Palio Hatchback/Weekend、Volvo S40 I、Fiat Marea 与 Hyundai Atos。
2. 处理 Mitsubishi Eclipse IV、Lotus Esprit S4、Honda CRX II 与 Maserati Biturbo 430。
3. 处理 Subaru Impreza高性能Sedan、Mitsubishi Colt IV和Nissan Sunny等日系乘用车。
4. 最后集中拆分 Ducato、C25、Expert、Transporter、H-1、L200及Boxer的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/saab-9-3-i-generation-2540?utm_source=chatgpt.com "Saab 9-3 I | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/nissan-pathfinder-iii-2.5-dti-174hp-4wd-924?utm_source=chatgpt.com "Nissan Pathfinder III 2.5 DTi (174 Hp) 4WD /SUV 2004"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Volvo S40 I facelift、Fiat Marea 185、Hyundai Atos、Lotus Esprit GT3、Maserati Biturbo 430 与 Honda CRX II 共 6 个尺寸组。([汽车数据网][1])
* Mitsubishi Eclipse IV 的 Ktype `20447` 跨越 2009 年改款，长度由 4565 mm 变为 4582 mm，拆为 `prefl` 与 `facelift` 两条 READY 映射。([汽车数据网][2])
* 本轮解决 7 个 Ktype，新增 8 条 READY 映射与 8 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* READY 映射行：67
* PENDING Ktype：35
* 已确认尺寸组：59
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20415	20415	Coupe	CRX II		3	EU-HONDA-CRX-II-COUPE-01	MEDIUM	三门掀背式Coupe外廓。	READY
20436	20436	Sedan	Biturbo 430		4	EU-MASERATI-BITURBO-430-SEDAN-01	MEDIUM	四门430轿车外廓。	READY
20447_prefl	20447	Coupe	Eclipse IV pre-facelift	4G	3	EU-MITSUBISHI-ECLIPSE-4G-COUPE-PREFL-01	HIGH	Ktype覆盖改款前后外廓；本行为改款前。	READY
20447_facelift	20447	Coupe	Eclipse IV facelift	4G	3	EU-MITSUBISHI-ECLIPSE-4G-COUPE-FACELIFT-01	HIGH	Ktype覆盖改款前后外廓；本行为2009改款后。	READY
20459	20459	Sedan	S40 I facelift	VS	4	EU-VOLVO-S40-VS-SEDAN-FACELIFT-01	MEDIUM	VS改款四门轿车外廓。	READY
20481	20481	Sedan	Marea	185	4	EU-FIAT-MAREA-185-SEDAN-01	MEDIUM	185四门轿车外廓。	READY
20623	20623	Hatchback	Atos		5	EU-HYUNDAI-ATOS-HATCHBACK-01	HIGH	五门高顶Hatchback外廓。	READY
20649	20649	Coupe	Esprit S4 GT3		2	EU-LOTUS-ESPRIT-S4-GT3-COUPE-01	HIGH	GT3双门Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CRX-II-COUPE-01	3815	1675	1270	Auto-Data Honda CRX II ED/EE generation	https://www.auto-data.net/en/honda-crx-ii-ed-ee-generation-2673
EU-MASERATI-BITURBO-430-SEDAN-01	4400	1730	1360	Auto-Data Maserati Biturbo Sedan generation	https://www.auto-data.net/en/maserati-biturbo-generation-2233
EU-MITSUBISHI-ECLIPSE-4G-COUPE-PREFL-01	4565	1835	1358	Auto-Data Mitsubishi Eclipse IV 4G generation	https://www.auto-data.net/en/mitsubishi-eclipse-iv-4g-generation-3430
EU-MITSUBISHI-ECLIPSE-4G-COUPE-FACELIFT-01	4582	1835	1358	Auto-Data Mitsubishi Eclipse IV 4G facelift 2.4L	https://www.auto-data.net/en/mitsubishi-eclipse-iv-4g-facelift-2009-2.4l-162hp-automatic-39372
EU-VOLVO-S40-VS-SEDAN-FACELIFT-01	4516	1716	1422	Auto-Data Volvo S40 VS 1.8 16V specifications	https://www.auto-data.net/en/volvo-s40-vs-1.8-16v-122hp-9565
EU-FIAT-MAREA-185-SEDAN-01	4390	1740	1420	Auto-Data Fiat Marea 185 1.6 16V specifications	https://www.auto-data.net/en/fiat-marea-185-1.6-16v-103hp-7193
EU-HYUNDAI-ATOS-HATCHBACK-01	3495	1495	1615	Auto-Data Hyundai Atos 1.1 i 12V specifications	https://www.auto-data.net/en/hyundai-atos-1.1-i-12v-59hp-13736
EU-LOTUS-ESPRIT-S4-GT3-COUPE-01	4369	1883	1150	Auto-Data Lotus Esprit 2.0 Turbo GT3 specifications	https://www.auto-data.net/en/lotus-esprit-2.0-i-16v-turbo-gt3-243hp-8298
```

## 下一步优先处理

1. 闭合 Mitsubishi Colt IV、Nissan Sunny、Subaru Impreza与Daihatsu Sirion等日系乘用车。
2. 处理 Fiat Palio Hatchback及Palio Weekend改款前后边界。
3. 闭合 Lada Samara Hatchback/Sedan、Peugeot 205及Mazda 323剩余车型。
4. 集中拆分 Ducato、C25、Expert、Transporter、H-1、L200与Boxer的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-s40-vs-1.8-16v-122hp-9565 "Volvo S40 (VS) 1.8 16V (122 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-eclipse-iv-4g-generation-3430 "Mitsubishi Eclipse IV (4G) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Chevrolet Beretta Z26 1994–1996 双门 Coupé 外廓；官方车型资料给出的外廓换算为 4757 × 1725 × 1346 mm。([汽车手册][1])
* 闭合 Fiat Palio Hatchback，以及两个尺寸不同的 Palio Weekend 旅行车外廓，未因车名相同而强行共组。([维尔解码器][2])
* 闭合 Buick Park Avenue II、Daihatsu Sirion II 4WD 与 Saab 9-3 II Cabriolet。Park Avenue 的首尾年份资料保持相同外廓。([汽车目录][3])
* 本轮解决 7 个 Ktype，新增 7 条 READY 映射和 7 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：72
* READY 映射行：74
* PENDING Ktype：28
* 已确认尺寸组：66
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20549	20549	Coupe	Beretta L-body	L	2	EU-CHEVROLET-BERETTA-L-COUPE-Z26-01	HIGH	Z26双门Coupe外廓。	READY
20569	20569	Hatchback	Palio I (178)	178		EU-FIAT-PALIO-178-HATCHBACK-01	MEDIUM	三门与五门采用相同外廓；Ktype未限定门数。	READY
20576	20576	Wagon	Palio Weekend Series 2	178	5	EU-FIAT-PALIO-WEEKEND-SERIES2-WAGON-01	HIGH	Series 2五门旅行车外廓。	READY
20581	20581	Wagon	Palio Weekend (178)	178	5	EU-FIAT-PALIO-WEEKEND-178-WAGON-01	MEDIUM	欧洲版五门旅行车外廓。	READY
20620	20620	Sedan	Park Avenue II	G	4	EU-BUICK-PARK-AVENUE-II-SEDAN-01	HIGH	第二代四门Sedan外廓。	READY
20634	20634	Hatchback	Sirion II	M2	5	EU-DAIHATSU-SIRION-M2-HATCHBACK-01	HIGH	M2五门4WD Hatchback外廓。	READY
20636	20636	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-01	MEDIUM	第二代双门Cabriolet；性能版本不改变外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-BERETTA-L-COUPE-Z26-01	4757	1725	1346	Chevrolet 1994 Beretta sales brochure	https://www.auto-brochures.com/makes/Chevrolet/Beretta/Chevrolet_US%20Beretta_1994.pdf
EU-FIAT-PALIO-178-HATCHBACK-01	3740	1626	1450	Auto-Data Fiat Palio 178 generation	https://www.auto-data.net/en/fiat-palio-178-generation-1573
EU-FIAT-PALIO-WEEKEND-SERIES2-WAGON-01	4142	1620	1518	Automobile-Catalog Fiat Palio Weekend ELX 1.3 16V	https://www.automobile-catalog.com/car/2004/733865/fiat_palio_weekend_elx_1_3_16v.html
EU-FIAT-PALIO-WEEKEND-178-WAGON-01	4130	1626	1515	Auto-Data Fiat Palio Weekend 178 1.9 JTD	https://www.auto-data.net/en/fiat-palio-weekend-178-1.9-jtd-80hp-6849
EU-BUICK-PARK-AVENUE-II-SEDAN-01	5253	1897	1458	Automobile-Catalog 1997 Buick Park Avenue Ultra;Automobile-Catalog 2005 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1997/323600/buick_park_avenue_ultra.html;https://www.automobile-catalog.com/car/2005/323870/buick_park_avenue_ultra.html
EU-DAIHATSU-SIRION-M2-HATCHBACK-01	3600	1665	1550	Auto-Data Daihatsu Sirion M2 1.3 i 4WD	https://www.auto-data.net/en/daihatsu-sirion-m2-1.3-i-4wd-87hp-82
EU-SAAB-9-3-II-CONVERTIBLE-01	4635	1762	1434	Automobile-Catalog 2006 Saab 9-3 2.0t Cabriolet	https://www.automobile-catalog.com/car/2006/3035720/saab_9-3_2_0t_cabriolet.html
```

## 下一步优先处理

1. 闭合 Mitsubishi Colt IV、Nissan Sunny、Subaru Impreza及两条 Nissan Laurel。
2. 处理 Mercedes-Benz C-Class Coupé、Chrysler Voyager II和Lada Samara Hatchback/Sedan。
3. 集中拆分剩余 Ducato、C25、Expert、Transporter、H-1、L200、Fiorino及Boxer商用车的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://www.auto-brochures.com/makes/Chevrolet/Beretta/Chevrolet_US%20Beretta_1994.pdf?utm_source=chatgpt.com "chevrolet beretta"
[2]: https://www.vindecoderz.com/EN/Fiat/Palio/1997/1.2%20MT/specs-features/8424?utm_source=chatgpt.com "1997 Fiat Palio 1.2 MT Specifications & Features, Performance | VinDecoderz.com"
[3]: https://www.automobile-catalog.com/car/1997/323600/buick_park_avenue_ultra.html?utm_source=chatgpt.com "1997 Buick Park Avenue Ultra (aut. 4)"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Mitsubishi Colt IV 1.6 4WD 三门 Hatchback、Fiat Fiorino II 1.7 TD Van、Nissan Laurel C32 Sedan 与 Chrysler Voyager II 标准轴距 MPV，共新增 **4 个尺寸组**。([汽车目录][1])
* 两条 Nissan Laurel Ktype 属于相同 C32 四门轿车外廓，直接复用同一尺寸组；未按发动机或 Ktype 重复建组。([日产汽车公司][2])
* 本轮解决 **5 个 Ktype**，新增 **5 条 READY 映射**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：77
* READY 映射行：79
* PENDING Ktype：23
* 已确认尺寸组：70
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20133	20133	Hatchback	Colt IV	CA0	3	EU-MITSUBISHI-COLT-IV-CA0-HATCHBACK-4WD-01	HIGH	CA0三门4WD外廓。	READY
20266	20266	Van	Fiorino II	146	3	EU-FIAT-FIORINO-II-146-VAN-01	MEDIUM	146厢式车外廓。	READY
20358	20358	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-C32-SEDAN-01	MEDIUM	C32四门Sedan外廓。	READY
20361	20361	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-C32-SEDAN-01	MEDIUM	C32四门Sedan外廓。	READY
20618	20618	MPV	Voyager II	AS		EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	MEDIUM	标准轴距Voyager外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-IV-CA0-HATCHBACK-4WD-01	3955	1690	1375	Automobile-Catalog 1993 Mitsubishi Colt 1600 GLXi 16V 4WD	https://www.automobile-catalog.com/car/1993/1952480/mitsubishi_colt_1600_glxi_16v_4wd.html
EU-FIAT-FIORINO-II-146-VAN-01	4159	1622	1904	Drive.Place Fiat Fiorino II 1.7 TD Van	https://fiat.drive.place/fiorino/ii/group_furgon/627227
EU-NISSAN-LAUREL-C32-SEDAN-01	4650	1690	1415	Nissan Heritage Collection Laurel 4-door Sedan Grand Extra	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/laurel_sedan_grand_extra.html
EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	4525	1830	1707	Auto-Data Chrysler Voyager II model specifications	https://www.auto-data.net/fr/chrysler-voyager-model-1665
```

## 下一步优先处理

1. 拆分 Ktype `20166` 覆盖的经典 Samara与Samara 2 Hatchback 外廓。
2. 处理 Mazda 323 II/III 标注冲突、Nissan Sunny 4WD 功率冲突及 Subaru Impreza 280 HP Sedan。
3. 随后集中闭合 C25、Expert、Ducato、Transporter、H-1、L200与Boxer等商用车的轴距、车顶和车身形式分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1993/1952480/mitsubishi_colt_1600_glxi_16v_4wd.html?utm_source=chatgpt.com "1993 Mitsubishi Colt 1600 GLXi 16V 4WD Specs Review ..."
[2]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/laurel_sedan_grand_extra.html?utm_source=chatgpt.com "Laurel 4-door Sedan Grand Extra (1985 : HJC32)"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz C-Class Sports Coupé `CL203` 尺寸组。Ktype `20460` 虽覆盖 2004 年改款，但官方资料显示车身侧面结构未改变，且仍属于同一 CL203 物理车身，因此不拆分改款前后尺寸组。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* READY 映射行：80
* PENDING Ktype：22
* 已确认尺寸组：71
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20460	20460	Coupe	C-Class Sports Coupe	CL203		EU-MERCEDES-BENZ-C-CLASS-CL203-COUPE-01	HIGH	CL203 Sports Coupe；2004改款不拆尺寸组。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-CL203-COUPE-01	4343	1728	1406	Mercedes-Benz Public Archive 203 series C-Class Sports Coupes	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/203-series-C-Class-Sports-Coups-2001---2004.xhtml?oid=453364
```

## 下一步优先处理

1. 处理 Nissan Sunny N13 1.6 4WD、Subaru Impreza GC8 STI 与 Mazda 323 BF Sedan。
2. 拆分 Lada Samara Hatchback 与 Sedan 的代际及门数外廓。
3. 集中处理剩余 Ducato、C25、Expert、Transporter、H-1、L200 与 Boxer 商用车的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/203-series-C-Class-Sports-Coups-2001---2004.xhtml?oid=453364 "203 series C-Class Sports Coupés, 2001 - 2004"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* Ktype `20166` 的生产覆盖期横跨 Samara I `21093` 与 Samara II `2114` 两套五门车身；结合两者独立尺寸记录，本轮按物理外廓拆成两条派生映射。该拆分属于基于生产期和车型边界的映射判断。([汽车数据网][1])
* Ktype `20498` 同理拆分为 Samara I `21099` 与 Samara II `2115` 两套四门 Sedan 外廓，未将不同车身错误合并。([汽车数据网][2])
* 闭合 Nissan Sunny N13 四门 4WD Sedan；来源明确给出四门车身及 4220 × 1640 × 1390 mm 外廓。([Ultimate Specs][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：81
* READY 映射行：85
* PENDING Ktype：19
* 已确认尺寸组：76
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20166_21093	20166	Hatchback	Samara I	21093	5	EU-LADA-SAMARA-21093-HATCHBACK-01	MEDIUM	Ktype覆盖两代五门车身；本行为21093外廓。	READY
20166_2114	20166	Hatchback	Samara II	2114	5	EU-LADA-SAMARA-2114-HATCHBACK-01	MEDIUM	Ktype覆盖两代五门车身；本行为2114外廓。	READY
20366	20366	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4WD-01	MEDIUM	N13四门4WD Sedan外廓。	READY
20498_21099	20498	Sedan	Samara I	21099	4	EU-LADA-SAMARA-21099-SEDAN-01	MEDIUM	Ktype覆盖两代四门车身；本行为21099外廓。	READY
20498_2115	20498	Sedan	Samara II	2115	4	EU-LADA-SAMARA-2115-SEDAN-01	MEDIUM	Ktype覆盖两代四门车身；本行为2115外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-SAMARA-21093-HATCHBACK-01	4006	1650	1402	Auto-Data Lada 21093-20 1.5 i	https://www.auto-data.net/en/lada-21093-20-1.5-i-78hp-13268
EU-LADA-SAMARA-2114-HATCHBACK-01	4100	1620	1415	Auto-Data Lada 2114 1.5 i	https://www.auto-data.net/en/lada-2114-1.5-i-79hp-13274
EU-NISSAN-SUNNY-N13-SEDAN-4WD-01	4220	1640	1390	Ultimate Specs Nissan Sunny N13 1.6 4WD	https://www.ultimatespecs.com/car-specs/Nissan/6796/Nissan-Sunny-N13-16-4WD.html
EU-LADA-SAMARA-21099-SEDAN-01	4205	1650	1402	Auto-Data Lada 21099-20 generation	https://www.auto-data.net/en/lada-21099-20-generation-2832
EU-LADA-SAMARA-2115-SEDAN-01	4330	1620	1415	Auto-Data Lada 2115 1.5	https://www.auto-data.net/en/lada-2115-1.5-76hp-13294
```

## 下一步优先处理

1. 闭合 Subaru Impreza GC8 280 PS Sedan，并确认 1996–2000 前后保险杠长度变化是否需要拆组。
2. 解决 Mazda 323 II/III 两条相同生产期记录的代际与车身代码冲突。
3. 集中处理 Ducato、C25、Expert、Transporter、H-1、L200 与 Boxer 等商用车的轴距、车顶和车身形式分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lada-21093-20-generation-2831?utm_source=chatgpt.com "Lada 21093-20 | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/lada-21099-20-generation-2832?utm_source=chatgpt.com "Lada 21099-20 | Technical Specs, Fuel consumption ..."
[3]: https://www.ultimatespecs.com/car-specs/Nissan/6796/Nissan-Sunny-N13-16-4WD.html "Nissan Sunny N13 1.6 4WD Specs, Performance, Comparisons"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* Ktype `20427` 的 280 PS Impreza GC8 覆盖两个不同车长阶段：早期 STI Version III/IV 为 4340 mm，后期 Version V/VI 为 4350 mm，因此拆为 `prefl`、`facelift` 两条物理外廓映射。两阶段宽度和高度均为 1690 × 1405 mm。([Carfolio][1])
* 闭合 Mazda 323 II BD 与 Mazda 323 III BF 两套独立四门 Sedan 外廓，没有因发动机功率及生产期相同而共组。Ktype 资料分别指向 BD 与 BF 车身。([b-parts.co.uk][2])
* 闭合 Hyundai H-1/Starex 第一代短轴 7 座 4WD Bus；Hyundai 2004 原厂手册明确列出 4WD 外廓为 4825 × 1820 × 1995 mm。([vanlife travel][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射行：90
* PENDING Ktype：15
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20232	20232	Sedan	323 II	BD	4	EU-MAZDA-323-BD-SEDAN-01	MEDIUM	BD四门Sedan外廓。	READY
20235	20235	Sedan	323 III	BF	4	EU-MAZDA-323-BF-SEDAN-PREFL-01	HIGH	BF改款前四门Sedan外廓。	READY
20427_prefl	20427	Sedan	Impreza I WRX STI Version III-IV	GC8	4	EU-SUBARU-IMPREZA-GC8-STI-SEDAN-PREFL-01	MEDIUM	Ktype覆盖两个车长阶段；本行为Version III-IV外廓。	READY
20427_facelift	20427	Sedan	Impreza I WRX STI Version V-VI	GC8	4	EU-SUBARU-IMPREZA-GC8-STI-SEDAN-FACELIFT-01	MEDIUM	Ktype覆盖两个车长阶段；本行为Version V-VI外廓。	READY
20546	20546	MPV	H-1 I Starex		5	EU-HYUNDAI-H1-I-STAREX-BUS-SWB-4WD-01	HIGH	短轴7座4WD Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-323-BD-SEDAN-01	4060	1630	1380	Drive.Place Mazda 323 II BD Sedan specifications	https://mazda.drive.place/323/ii/group_sedan/131025
EU-MAZDA-323-BF-SEDAN-PREFL-01	4195	1645	1390	Automobile-Catalog Mazda 323 BF 1.6i GLX Sedan specifications	https://www.automobile-catalog.com/car/1985/1630265/mazda_323_1_6i_glx_sedan_cat.html
EU-SUBARU-IMPREZA-GC8-STI-SEDAN-PREFL-01	4340	1690	1405	Carfolio 1996 Subaru Impreza WRX STI Version III specifications	https://www.carfolio.com/subaru-impreza-wrx-sti-version-iii-365310
EU-SUBARU-IMPREZA-GC8-STI-SEDAN-FACELIFT-01	4350	1690	1405	Goo-net Subaru Impreza WRX STI Version V catalog	https://www.goo-net-exchange.com/catalog/SUBARU__IMPREZA/4501983/
EU-HYUNDAI-H1-I-STAREX-BUS-SWB-4WD-01	4825	1820	1995	Hyundai H-1 2004 Owner's Manual	https://vanlife-travel.ru/wp-content/uploads/2020/02/hyundai-starex-h1-owners-manual-2004.pdf
```

## 下一步优先处理

1. 利用同一份 Hyundai 原厂手册拆分 H-1 的短轴与长轴 2WD Bus，处理 Ktype `20542`、`20543`、`20544`。
2. 根据 Volkswagen 原厂尺寸图处理 T5 Kasten 与 Bus 的 SWB/LWB、低顶/中顶分支。
3. 最后集中处理 Ducato、C25、Expert、Transporter T4、L200 与 Boxer等商用车。

推进信号：CONTINUE

[1]: https://www.carfolio.com/subaru-impreza-wrx-sti-version-iii-365310?utm_source=chatgpt.com "1996 Subaru Impreza WRX STi Version III GC8"
[2]: https://www.b-parts.co.uk/auto-parts/mazda-323-ii-bd-1-6-glx-20232-vv/categories?utm_source=chatgpt.com "Original Used MAZDA 323 II Saloon (BD) 1.6 GLX (73 hp) Parts | B-Parts"
[3]: https://vanlife-travel.ru/wp-content/uploads/2020/02/hyundai-starex-h1-owners-manual-2004.pdf?utm_source=chatgpt.com "hyundai-starex-h1-owners-manual-2004.pdf - vanlife travel"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
ChatGPT 说：Unusual activity has been detected from your device. Try again later. (6e3daf49-b652-4230-95a9-6ef5cbafdd4b)


--- 发送 / 推进信号纠偏 / Round 17 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 闭合 Hyundai H-1/Starex 第一代 2WD Bus 的短轴与长轴尺寸组：短轴 `4695 × 1820 × 1885 mm`，长轴 `5035 × 1820 × 1970 mm`。Hyundai 手册明确区分短轴和长轴 Minibus 外廓。([carmanualsonline.info][1])
* `20542` 对应 99 HP 短轴版本；`20543` 对应 101 HP 长轴版本。`20544` 的 140 HP CRDi 同时存在短轴和长轴 2WD 版本，因此拆成两条派生映射。([汽车数据网][2])
* 修正既有 `20546` 的 `Doors`：由 `5` 改为 `4`；尺寸组保持复用，不重新输出。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* READY 映射行：94
* PENDING Ktype：12
* 已确认尺寸组：83
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20542	20542	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-BUS-SWB-2WD-01	MEDIUM	短轴2WD Bus外廓。	READY
20543	20543	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-BUS-LWB-2WD-01	HIGH	长轴2WD Bus外廓。	READY
20544_swb	20544	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-BUS-SWB-2WD-01	MEDIUM	Ktype同时覆盖短轴与长轴；本行为短轴外廓。	READY
20544_lwb	20544	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-BUS-LWB-2WD-01	MEDIUM	Ktype同时覆盖短轴与长轴；本行为长轴外廓。	READY
20546	20546	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-BUS-SWB-4WD-01	HIGH	短轴7座4WD Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H1-I-STAREX-BUS-SWB-2WD-01	4695	1820	1885	Hyundai H-1 2004 Owner's Manual	https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2004-owner-s-manual/27
EU-HYUNDAI-H1-I-STAREX-BUS-LWB-2WD-01	5035	1820	1970	Hyundai H-1 2004 Owner's Manual	https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2004-owner-s-manual/27
```

## 下一步优先处理

1. 拆分 Volkswagen Transporter T5 `20485` Kasten 的 SWB/LWB 与可确认车顶分支，并处理 `20661` Bus。
2. 处理 Citroën C25 Bus、Van、Chassis Cab 的轴距和车身形式。
3. 最后闭合 Fiat Ducato、Peugeot Expert、Mitsubishi L200、VW T4 Chassis Cab 与 Peugeot Boxer Chassis Cab。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/hyundai-h-1-grand-starex-2004-owner-s-manual/?srch=height&utm_source=chatgpt.com "height Hyundai H-1 (Grand Starex) 2004 Owner's Manual (273 Pages)"
[2]: https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-lwb-101hp-13859 "Hyundai H-1 I Starex 2.5 TD LWB (101 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* Ktype `20485` 明确覆盖 T5 3.2 V6 4MOTION Panel Van 的五种物理外廓：L1H1、L1H2、L2H1、L2H2、L2H3，因此拆为五条派生映射。五种配置宽度均为不含后视镜的 `1904 mm`，长度和车顶高度分别建组。([汽车数据网][1])
* 本轮解决 **1 个 Ktype**，新增 **5 条 READY 映射**和 **5 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射行：99
* PENDING Ktype：11
* 已确认尺寸组：88
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20485_l1h1	20485	Van	Transporter T5 Panel Van			EU-VW-TRANSPORTER-T5-VAN-L1H1-01	HIGH	短轴低顶Panel Van外廓。	READY
20485_l1h2	20485	Van	Transporter T5 Panel Van			EU-VW-TRANSPORTER-T5-VAN-L1H2-01	HIGH	短轴中顶Panel Van外廓。	READY
20485_l2h1	20485	Van	Transporter T5 Panel Van			EU-VW-TRANSPORTER-T5-VAN-L2H1-01	HIGH	长轴低顶Panel Van外廓。	READY
20485_l2h2	20485	Van	Transporter T5 Panel Van			EU-VW-TRANSPORTER-T5-VAN-L2H2-01	HIGH	长轴中顶Panel Van外廓。	READY
20485_l2h3	20485	Van	Transporter T5 Panel Van			EU-VW-TRANSPORTER-T5-VAN-L2H3-01	HIGH	长轴高顶Panel Van外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T5-VAN-L1H1-01	4890	1904	1969	Auto-Data Volkswagen Transporter T5 Panel Van 3.2 V6 4MOTION L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l1h1-49901
EU-VW-TRANSPORTER-T5-VAN-L1H2-01	4890	1904	2170	Auto-Data Volkswagen Transporter T5 Panel Van 3.2 V6 4MOTION L1H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l1h2-49949
EU-VW-TRANSPORTER-T5-VAN-L2H1-01	5290	1904	1969	Auto-Data Volkswagen Transporter T5 Panel Van 3.2 V6 4MOTION L2H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l2h1-49906
EU-VW-TRANSPORTER-T5-VAN-L2H2-01	5290	1904	2170	Auto-Data Volkswagen Transporter T5 Panel Van 3.2 V6 4MOTION L2H2	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l2h2-49947
EU-VW-TRANSPORTER-T5-VAN-L2H3-01	5290	1904	2470	Auto-Data Volkswagen Transporter T5 Panel Van 3.2 V6 4MOTION L2H3	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l2h3-49928
```

## 下一步优先处理

1. 闭合 Ktype `20661` Transporter T5 Bus 的短轴、长轴和车顶分支，判断是否可复用本轮相同外廓尺寸事实。
2. 处理 Citroën C25 的 Bus、Van 与 Chassis Cab 分支。
3. 最后处理 Ducato、Expert、L200、Transporter T4和Boxer。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l2h1-49906 "Volkswagen Transporter (T5) Panel Van 3.2 V6 (235 Hp) 4MOTION L2H1 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* Ktype `20661` 的 3.2 V6 4MOTION Bus 同时存在短轴与长轴外廓，分别为 `4890 × 1904 × 1969 mm` 和 `5290 × 1904 × 1969 mm`。两套三维与已建档的 T5 `L1H1`、`L2H1` 尺寸组完全一致，因此直接复用，不重复创建尺寸组。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：101
* PENDING Ktype：10
* 已确认尺寸组：88
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20661_swb	20661	MPV	Transporter T5 Bus			EU-VW-TRANSPORTER-T5-VAN-L1H1-01	HIGH	Ktype覆盖短轴与长轴Bus；本行为短轴标准顶外廓。	READY
20661_lwb	20661	MPV	Transporter T5 Bus			EU-VW-TRANSPORTER-T5-VAN-L2H1-01	HIGH	Ktype覆盖短轴与长轴Bus；本行为长轴标准顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 批量闭合 Peugeot Expert I Bus 的 `20469`、`20470`，判断两条发动机版本是否共用同一外廓。
2. 处理 Mitsubishi L200 `20474` 的 Single Cab、Club Cab、Double Cab 分支。
3. 最后处理 Ducato、Citroën C25、Transporter T4 与 Boxer底盘车的轴距和驾驶室分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/de/volkswagen-caravelle-t5-long-3.2-v6-235hp-4motion-49265 "Volkswagen Caravelle (T5) Long 3.2 V6 (235 PS) 4MOTION | Technische Daten, Verbrauch, Eigenschaften und Spezifikationen, Maße"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* 闭合 Peugeot Expert I `224` Bus 尺寸组。Ktype `20469` 与 `20470` 均属于乘用 Bus 车身，发动机差异不改变外廓，统一关联 `4440 × 1810 × 1940 mm` 尺寸组。([autoonderdelen-direct.be][1])
* 闭合 Mitsubishi L200 III `K64T`。车型目录将 `K64T` 明确限定为后驱 Single Cab，未拆成 Club Cab 或 Double Cab；采用单排皮卡外廓 `5009 × 1694 × 1585 mm`。([PartSouq][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射行：104
* PENDING Ktype：7
* 已确认尺寸组：90
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20469	20469	MPV	Expert I	224		EU-PEUGEOT-EXPERT-I-224-MPV-01	HIGH	224乘用Bus外廓。	READY
20470	20470	MPV	Expert I	224		EU-PEUGEOT-EXPERT-I-224-MPV-01	HIGH	224乘用Bus外廓。	READY
20474	20474	Pickup	L200 III	K64T	2	EU-MITSUBISHI-L200-III-K64T-PICKUP-SINGLECAB-2WD-01	HIGH	K64T后驱Single Cab外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-I-224-MPV-01	4440	1810	1940	Drive.Place Peugeot Expert I 1.9 Minivan;Cars-Directory Peugeot Expert 2.0 TD 94 Hp	https://peugeot.drive.place/expert/i/group_minivan/230305;https://www.cars-directory.net/gallery/peugeot/expert/2004/
EU-MITSUBISHI-L200-III-K64T-PICKUP-SINGLECAB-2WD-01	5009	1694	1585	Mitsubishi Partsouq K64T vehicle catalog;AutoEvolution Mitsubishi L200 Single Cab specifications	https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&vid=0;https://www.autoevolution.com/cars/mitsubishi-l200-single-cab-1995.html
```

## 下一步优先处理

1. 闭合 Citroën C25 的 Bus、Van 与 Chassis Cab 分支：`20326`、`20628`、`20631`、`20633`。
2. 处理 Fiat Ducato 4×4 Van `20229`。
3. 最后处理 VW Transporter T4 Chassis Cab `20486` 与 Peugeot Boxer Chassis Cab `20693`。

推进信号：CONTINUE

[1]: https://www.autoonderdelen-direct.be/auto-onderdelen/peugeot/expert-224/1-9-d-51-kw/claxon-meertonige-hoorn/20469?utm_source=chatgpt.com "Claxon voor PEUGEOT Expert I (224) 1.9 D 69 Pk 12.2003 ..."
[2]: https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&srsltid=AfmBOoocNEisWFBLL2VrJWRva2hdYFhg6to0jqQYY1KMCmL5j22GVwTO&ssd=%24%2AKwFjV0ZCFjElBj4yEiYlVzsvDwgWZ2hlZHZwfzkQLHQ4cm07fWp2fXI0dGtyFG04NVhhEWESc3x1OCo8OBpmYwJzfHU2ZCQgcxUZBR1yKgAAAABqxdek%24&vid=0&utm_source=chatgpt.com "Mitsubishi L200 General (EXPORT) K64T Parts Catalogs"


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / 下一步 ---
## 更新点

* 闭合 Citroën C25 2.5 D 标准轴 Bus，外廓为 `4759 × 1965 × 2100 mm`。([Autocentrum.pl][1])
* 闭合 Citroën C25 1.9 D 1400 长轴高顶 Van，外廓为 `5489 × 1965 × 2420 mm`；未与标准轴、普通顶 C25 合并。([en.wheelsage.org][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：106
* PENDING Ktype：5
* 已确认尺寸组：92
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20326	20326	MPV	C25 I			EU-CITROEN-C25-I-MPV-STANDARD-01	MEDIUM	标准轴乘用Bus外廓。	READY
20628	20628	Van	C25 I			EU-CITROEN-C25-I-VAN-LWB-HIGHROOF-01	MEDIUM	1400载重级长轴高顶Van外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C25-I-MPV-STANDARD-01	4759	1965	2100	AutoCentrum Citroen C25 technical dimensions	https://www.autocentrum.pl/dane-techniczne/citroen/c25/
EU-CITROEN-C25-I-VAN-LWB-HIGHROOF-01	5489	1965	2420	WheelsAge Citroen C25 LWB High Roof Van specifications	https://en.wheelsage.org/twins/group/120233/specifications
```

## 下一步优先处理

1. 拆分 Citroën C25 Chassis Cab `20631`、`20633` 的轴距和底盘长度分支。
2. 闭合 Fiat Ducato 4×4 Van `20229`。
3. 处理 VW Transporter T4 Chassis Cab `20486` 与 Peugeot Boxer Chassis Cab `20693`。

推进信号：CONTINUE

[1]: https://www.autocentrum.pl/dane-techniczne/citroen/c25/?utm_source=chatgpt.com "Dane techniczne samochodów Citroen C25 – wybierz silnik"
[2]: https://en.wheelsage.org/twins/group/120233/specifications?utm_source=chatgpt.com "Citroën C25 LWB / Fiat Ducato Maxi / Peugeot J5 Van High ..."


--- 发送 / 继续到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / 下一步 ---
## 更新点

* 本轮未强行创建尺寸组。剩余 5 个 Ktype 均存在未闭合的商用车物理分支，已补充为明确 `PENDING` 映射行。
* Peugeot Boxer 2.0 Chassis Cab 同期至少覆盖 C、M、L、LL 等轴距/底盘分支，不能只取一套尺寸。([Zoomcar][1])
* VW Transporter T4 同期存在短轴、长轴以及单排/双排驾驶室差异；输入字段未限定具体分支。([维基百科][2])
* Ducato 2.8 TD 4×4 属于独立四驱版本，现有资料尚未同时闭合具体厢式车长度、车顶高度和四驱状态下的整车高度，因此暂不套用普通前驱 Ducato 尺寸。([Autogidas][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射行：106
* PENDING Ktype：5
* 已确认尺寸组：92
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20229	20229	Van	Ducato II	230			LOW	2.8 TD 4×4厢式车的轴距、车顶及四驱整车高度边界尚未闭合。	PENDING: 需确认具体轴距、车顶和4×4状态下完整三维
20486	20486	Pickup	Transporter T4				LOW	2.8平台底盘可能覆盖不同轴距及单排、双排驾驶室。	PENDING: 需确认T4平台底盘的驾驶室和轴距分支
20631	20631	Pickup	C25 I				LOW	早期2.0平台底盘的轴距、驾驶室和原厂货台配置尚未明确。	PENDING: 需确认C25 2.0平台底盘物理分支
20633	20633	Pickup	C25 I				LOW	2.5 DT平台底盘可能覆盖280、290及不同轴距配置。	PENDING: 需确认C25 2.5 DT平台底盘物理分支
20693	20693	Pickup	Boxer I	230			LOW	2.0汽油底盘车同期覆盖C、M、L及LL等不同外廓。	PENDING: 需闭合Boxer 230各轴距底盘车三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 先闭合 Boxer I 230 的 C、M、L、LL 底盘车分支及对应三维。
2. 再利用同平台资料批量处理 Ducato II 230 与 C25 280/290，避免重复核对相同 SEVEL 外廓。
3. 最后单独处理 T4 2.8 平台底盘的单排/双排驾驶室及轴距差异。

推进信号：CONTINUE

[1]: https://zoomcar.fr/fiche-technique-utilitaire/peugeot/boxer-CHA13-2001.html?utm_source=chatgpt.com "Fiches techniques Peugeot Boxer de 2001 | zoomcar.fr"
[2]: https://en.wikipedia.org/wiki/Volkswagen_Transporter_%28T4%29?utm_source=chatgpt.com "Volkswagen Transporter (T4)"
[3]: https://autogidas.lt/en/auto-katalogas/fiat/ducato/2.8-idtd-4x4-1998-2001-k109548?utm_source=chatgpt.com "Fiat Ducato 2.8 iDTD 4x4 1998-2001 | Autocatalog"


--- 发送 / 继续到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / 下一步 ---
## 更新点

* Ktype `20486` 已确认覆盖 T4 平台底盘的三种物理外廓：短轴单排驾驶室、长轴单排驾驶室、长轴双排驾驶室。
* Volkswagen 原厂车身制造指南分别给出三种底盘的完整外廓，因此拆为三条派生映射，不再保持 PENDING。宽度均为不含后视镜的 `1840 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20486_swb_singlecab	20486	Pickup	Transporter T4	70E	2	EU-VW-TRANSPORTER-T4-CHASSIS-SWB-SINGLECAB-01	MEDIUM	Ktype覆盖多种平台底盘；本行为短轴单排驾驶室。	READY
20486_lwb_singlecab	20486	Pickup	Transporter T4	70L	2	EU-VW-TRANSPORTER-T4-CHASSIS-LWB-SINGLECAB-01	MEDIUM	Ktype覆盖多种平台底盘；本行为长轴单排驾驶室。	READY
20486_lwb_doublecab	20486	Pickup	Transporter T4	70M	4	EU-VW-TRANSPORTER-T4-CHASSIS-LWB-DOUBLECAB-01	MEDIUM	Ktype覆盖多种平台底盘；本行为长轴双排驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T4-CHASSIS-SWB-SINGLECAB-01	4736	1840	1920	Volkswagen Commercial Vehicles Transporter T4 Body Builder Guidelines	https://www.volkswagen-nutzfahrzeuge.ch/idhub/content/dam/onehub_nfz/importers/ch/beratung-und-kauf/umbauloesungen_technische_informationen/aufbaurichtlinien/it/aufbaurichtlinien_transporter_t4_2007_it.pdf
EU-VW-TRANSPORTER-T4-CHASSIS-LWB-SINGLECAB-01	5136	1840	1920	Volkswagen Commercial Vehicles Transporter T4 Body Builder Guidelines	https://www.volkswagen-nutzfahrzeuge.ch/idhub/content/dam/onehub_nfz/importers/ch/beratung-und-kauf/umbauloesungen_technische_informationen/aufbaurichtlinien/it/aufbaurichtlinien_transporter_t4_2007_it.pdf
EU-VW-TRANSPORTER-T4-CHASSIS-LWB-DOUBLECAB-01	5136	1840	1910	Volkswagen Commercial Vehicles Transporter T4 Body Builder Guidelines	https://www.volkswagen-nutzfahrzeuge.ch/idhub/content/dam/onehub_nfz/importers/ch/beratung-und-kauf/umbauloesungen_technische_informationen/aufbaurichtlinien/it/aufbaurichtlinien_transporter_t4_2007_it.pdf
```

## 下一步优先处理

1. 闭合 Fiat Ducato II `230L` 2.8 TD 4×4 Van 的具体长度和车顶分支。
2. 批量处理同源 SEVEL 平台的 Citroën C25 Chassis Cab `20631`、`20633`。
3. 最后闭合 Peugeot Boxer I `230` Chassis Cab `20693` 的轴距和底盘长度分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 24 / 下一步 ---
## 更新点

* 修正 Ktype `20693` 的候选边界：Peugeot Boxer 2.0 汽油版平台/底盘车仅确认 **L 轴距**，不是此前记录的 C、M、L、LL 全范围。
* 该 Ktype 仍覆盖单排底盘、双排底盘、单排平台和双排平台四种物理分支。原厂手册已确认分支及长度、宽度，但平台车高度仅给出范围，底盘车高度取决于后续上装，暂不满足完整尺寸组建档条件。([carmanualsonline.info][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20693	20693	Pickup	Boxer I	230			LOW	原C/M/L/LL候选已纠正为L轴距；仍覆盖单排/双排平台车及单排/双排底盘车。	PENDING: 四个L轴距物理分支的精确外部高度尚未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 Boxer I 车身制造或型式认证资料，闭合四个 L 轴距分支的精确整车高度。
2. 处理 Ducato II 2.8 TD 4×4 Van 的轴距、车顶和四驱高度边界。
3. 最后处理 Citroën C25 两条平台底盘 Ktype 的轴距与驾驶室分支。

推进信号：CONTINUE

[1]: https://www.carmanualsonline.info/peugeot-boxer-2002-owners-manual/17 "PEUGEOT BOXER 2002 Owners Manual (182 Pages), Page 170: 16-09-2002 PRACTICAL INFORMATION159 ACCESSORI ..."


--- 发送 / 继续到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 25 / 下一步 ---
## 更新点

* Ktype `20229` 已进一步确认是 **Ducato II Van（230L）2.8 TD 4×4**，因此将 `BodyCode` 从 `230` 修正为 `230L`。但该 Ktype 仍涉及不同载重级及可能的车长、车顶组合，现有资料未闭合 4×4 状态下各分支的完整三维，暂不创建尺寸组。([自动文档][1])
* Ktype `20631` 的生产期和发动机版本已确认属于改款前 **C25 280** 平台，将 `BodyCode` 明确为 `280`。现有技术资料只提供 C25 系列的尺寸范围，未将具体轴距、驾驶室与平台车三维逐一对应，仍不能建组。([Autodoc][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20229	20229	Van	Ducato II	230L			LOW	已确认230L厢式车边界；不同载重级、轴距、车顶及4×4整车高度尚未完全对应。	PENDING: 需闭合230L 4×4 Van各物理分支的完整三维
20631	20631	Pickup	C25 I	280			LOW	已限定为改款前280平台底盘；具体轴距、驾驶室及原厂平台分支尚未闭合。	PENDING: 需闭合C25 280平台底盘物理分支
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 C25 280/290 原厂车身制造资料，将 `20631`、`20633` 按轴距和驾驶室一次性闭合。
2. 查找 Ducato 230L Dangel 4×4 配置表，确认 `20229` 实际提供的车长、车顶及升高后高度。
3. 查找 Boxer 230 车身制造指南，补齐 `20693` 平台车与底盘车的精确高度，避免使用“2100–2125 mm”范围值。

推进信号：CONTINUE

[1]: https://www.auto-doc.ie/car-parts/drive-shaft-10162/fiat/ducato/ducato-box-230l/20229-2-8-td-4x4?srsltid=AfmBOoqIcaaYJrllLHQMgjsS49qdw_lsQrfcgTwMdD7yCgN-oqKXAdKp&utm_source=chatgpt.com "Fiat Ducato 230L 2.8 TD 4x4 Drive shaft (122 hp Diesel 8140.43)"
[2]: https://www.autodoc.co.uk/car-parts/control-levers-cables-10735/citroen/c25/c25-platform-chassis-280-290/20631-2-0?utm_source=chatgpt.com "Citroen C25 280 2.0 Handbrake cable (78 hp Petrol 170A (XN1T))"


--- 发送 / 继续到 Round 26 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 26 / 下一步 ---
## 更新点

* 本轮未创建新尺寸组。`20229` 已找到与发动机、四驱系统和 `230L` 车身一致的完整尺寸候选，但唯一完整三维仍来自同一辆二手特种车辆的多平台转载，不能按规则单独支撑最终建组。该车辆记录为 2.8 Dangel 4×4、90 kW，并明确标注长轴高顶厢式车外廓；普通 Ducato 230 资料可独立支持 `1998 mm` 车身宽度，但仍不足以把整套三维落盘。([AutoWiki.org][1])
* `20633` 已确认其 TecDoc 边界为 C25 Platform/Chassis `280_, 290_`、发动机代码 `CRD93LS (U25/673)`，生产期 1987-01 至 1994-01；现有证据仍不能把该 Ktype可靠分配到单一 280 或 290 外廓，因此保持未拆分 PENDING。([自动文档][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20229	20229	Van	Ducato II	230L			LOW	已限定为Dangel 4×4长轴高顶厢式车候选，但仍缺符合落盘等级的完整三维来源。	PENDING: 需用厂商资料或可信规格数据库闭合230L 4×4完整三维
20633	20633	Pickup	C25 I				LOW	发动机代码U25/673对应280与290平台底盘，尚不能确认具体物理分支。	PENDING: 需区分C25 280与290平台底盘并闭合各分支三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 继续查找 Fiat/Dangel 历史技术资料，替换 `20229` 当前仅由二手车记录支持的完整三维。
2. 查找 C25 280/290 原厂车型手册或车身制造尺寸图，一次解决 `20631`、`20633`。
3. 查找第一代 Boxer 230 平台车/底盘车原厂车身制造资料，闭合 `20693` 四个 L 轴距分支。

推进信号：CONTINUE

[1]: https://www.auto-wiki.org/fiat/ducato/zfa-230/ducato-kombi-2-5-tdi-eco-80-kw-1074/ "[Tech. Daten] Fiat Ducato Kombi 2.5 TDI Eco (02/96 - 08/98) 80 kW/110 PS"
[2]: https://www.auto-doc.ie/spares/citroen/c25/c25-platform-chassis-280-290/20633-2-5-dt?utm_source=chatgpt.com "Parts Citroen C25 280 2.5 DT 95 hp Diesel 1987 - 1994 CRD93LS (U25/673) | C25 280_, 290_ parts catalogue AUTODOC"


--- 发送 / 继续到 Round 27 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 27 / 下一步 ---
## 更新点

* 修正 Ktype `20693` 的物理边界：该 `Boxer 2.0i 110 HP` 平台底盘资料明确对应 **2850 mm 轴距的 Chassis**，并非上一轮判断的 L 轴距，也没有证据支持拆成四个 L 轴距分支。现阶段恢复为一条基础映射。([Truck1][1])
* 来源仍未提供该裸底盘车完整的车长、车宽和车高，因此不能创建 DIMENSION_GROUP，继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20693	20693	Pickup	Boxer I	230	2		LOW	已纠正为2850mm轴距的2.0i单排Chassis候选；完整外部三维尚未闭合。	PENDING: 需补齐2850mm轴距Boxer 230 Chassis完整三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 Boxer I `230` 2850 mm 轴距 Chassis 的原厂尺寸图或型式认证记录。
2. 批量闭合 Citroën C25 `280/290` 平台底盘的车长、车宽和车高。
3. 查找 Ducato `230L` Dangel 4×4 历史技术表，确认完整量产外廓。

推进信号：CONTINUE

[1]: https://www.truck1.eu/blog/peugeot-boxer-truck-chassis-2-0i-110-hp-tech-specs-t30946?srsltid=AfmBOorl_7mYRnuJ2HXM4agCU7HFji9BKceredi34WVnAxBKAk9KmFV5 "www.truck1.eu"


--- 发送 / 继续到 Round 28 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 28 / 下一步 ---
## 更新点

* 修正 Ktype `20229` 的 `BodyCode`：由零件目录写法 `230L` 改为厂商型式认证使用的 `230`。
* 瑞士型式认证确认该车型为 90 kW、四驱、厢式车，覆盖 `27/27B/27E/27H` 多个变型；资料仍未给出各变型对应的完整长宽高，不能强行创建尺寸组。([Dauto][1])
* 其余 3 个 PENDING Ktype 本轮没有获得足以闭合完整三维的新证据。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20229	20229	Van	Ducato II	230			LOW	型式认证确认90kW四驱厢式车及27/27B/27E/27H多个变型，但各变型完整外廓尚未对应。	PENDING: 需闭合Ducato 230 4×4各实际物理分支的完整三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 追查 Ducato 型式认证变型 `27/27B/27E/27H` 对应的车长、车顶及完整三维。
2. 利用 C25 280/290 型式认证或车身制造资料，一次闭合 `20631`、`20633`。
3. 查找 Boxer 230、2850 mm 轴距单排 Chassis 的完整原厂外廓，闭合 `20693`。

推进信号：CONTINUE

[1]: https://www.dauto.ch/typenscheine/fiat-ducato14-2-8-td-4x4-1fa678-zfa23000005-e3-70-156-96-27-0025 "1FA678 - FIAT DUCATO14 2.8 TD 4X4 - ZFA23000005...... - e3*70/156-96/27*0025"


--- 发送 / 继续到 Round 29 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 29 / 下一步 ---
## 更新点

* 修正 Ktype `20693`：撤销上一轮“2850 mm 轴距单排底盘”的过度收窄。
* `20693` 实际只确定为 Boxer I `ZCT_` 平台/底盘、2.0 汽油 81 kW，不能由 Ktype 单独限定轴距和驾驶室。同期 RFL 发动机的型式资料至少覆盖 15Q、18Q、350L、单排及双排/原厂货台等不同物理分支。([AIC Germany][1])
* 本轮没有获得足以闭合三维的新尺寸证据，未创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20693	20693	Pickup	Boxer I	ZCT_			LOW	撤销2850mm单一底盘候选；该Ktype覆盖不同载重级、轴距及单排/双排平台底盘分支。	PENDING: 需枚举ZCT_ 2.0 81kW实际物理分支并闭合各分支完整三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 按 Boxer 15Q、18Q 型式批准逐项提取长宽高，闭合 `20693` 的平台底盘分支。
2. 按 C25 `280 H/G/B`、`290` 型式批准批量闭合 `20631`、`20633`。
3. 继续解析 Ducato 230 4×4 的 `27/27B/27E/27H` 变型尺寸，闭合 `20229`。

推进信号：CONTINUE

[1]: https://aic-germany.de/en/product-catalogue/6616?utm_source=chatgpt.com "Product catalogue from AIC Germany"


--- 发送 / 继续到 Round 30 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 30 / 下一步 ---
## 更新点

* 本轮未形成可落盘修改。
* 已再次确认剩余记录的车型边界：`20229` 为 Ducato 230L 2.8 TD 4×4 Van，`20631/20633` 属于 C25 280/290 Platform/Chassis，`20693` 为 Boxer 230 `ZCT_` 2.0 Platform/Chassis。现有页面仍只支持车型识别，未同时提供可对应到具体物理分支的完整长、无镜宽和高，因此不能创建尺寸组。([买汽车配件][1])
* Car.info 可确认 C25 同期存在 Chassis Cab 1400 等具体版本，但当前可检索内容仍缺少完整三维，不能据此把两个 C25 Ktype 强制关联到单一外廓。([car.info][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 C25 280/290 Chassis Cab 1400 的原厂销售手册或型式认证尺寸页，优先一次闭合 `20631`、`20633`。
2. 查找 Ducato 230 Dangel 4×4 的变型对照表，将 `27/27B/27E/27H` 对应到具体车长和车顶。
3. 查找 Boxer 230 `ZCT_` 2.0 平台底盘的车身制造指南，确认实际轴距、驾驶室及完整三维。

推进信号：CONTINUE

[1]: https://www.buycarparts.co.uk/fiat/ducato-box-230l/20229/15009/door-seal?utm_source=chatgpt.com "Door seal for Fiat Ducato 230L 2.8 TD 4x4 122 hp Diesel rear ..."
[2]: https://www.car.info/en-dk/citroen/c25/c25-chassi-cab-120196175?utm_source=chatgpt.com "Citroën C25 Chassi Cab 1400"


--- 发送 / 继续到 Round 31 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 已打开消息操作菜单，但没有找到【在新聊天中分支】


--- 脚本异常 ---
异常: Playwright browser 请求失败 (tab-new): {"ok":false,"error":"page.goto: net::ERR_CONNECTION_TIMED_OUT at https://chatgpt.com/c/6a6933b4-93ec-83ea-b5f5-9474ec3faec8\nCall log:\n\u001b[2m  - navigating to \"https://chatgpt.com/c/6a6933b4-93ec-83ea-b5f5-9474ec3faec8\", waiting until \"domcontentloaded\"\u001b[22m\n\n    at runAction (D:\\Licheng\\Repo\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:149:25)\n    at async Server. (D:\\Licheng\\Repo\\fitment_sheet_generation\\projects\\qclaw_fitment_automation\\playwright_browser_bridge.js:222:16)"}


--- 发送 / checkpoint 续跑到 Round 32 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 33 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 34 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 34 / checkpoint 续跑 ---
## 更新点

* 本轮未形成可落盘修改。
* 已再次确认剩余记录的车型边界：`20229` 为 Ducato 230L 2.8 TD 4×4 Van，`20631/20633` 属于 C25 280/290 Platform/Chassis，`20693` 为 Boxer 230 `ZCT_` 2.0 Platform/Chassis。现有页面仍只支持车型识别，未同时提供可对应到具体物理分支的完整长、无镜宽和高，因此不能创建尺寸组。([买汽车配件][1])
* Car.info 可确认 C25 同期存在 Chassis Cab 1400 等具体版本，但当前可检索内容仍缺少完整三维，不能据此把两个 C25 Ktype 强制关联到单一外廓。([car.info][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* READY 映射行：109
* PENDING Ktype：4
* 已确认尺寸组：95
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 查找 C25 280/290 Chassis Cab 1400 的原厂销售手册或型式认证尺寸页，优先一次闭合 `20631`、`20633`。
2. 查找 Ducato 230 Dangel 4×4 的变型对照表，将 `27/27B/27E/27H` 对应到具体车长和车顶。
3. 查找 Boxer 230 `ZCT_` 2.0 平台底盘的车身制造指南，确认实际轴距、驾驶室及完整三维。

推进信号：CONTINUE

[1]: https://www.buycarparts.co.uk/fiat/ducato-box-230l/20229/15009/door-seal?utm_source=chatgpt.com "Door seal for Fiat Ducato 230L 2.8 TD 4x4 122 hp Diesel rear ..."
[2]: https://www.car.info/en-dk/citroen/c25/c25-chassi-cab-120196175?utm_source=chatgpt.com "Citroën C25 Chassi Cab 1400"


--- 发送 / 继续到 Round 35 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 35 ---
【任务名称】
【全量表更新】all 第 901-1000 行

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
all 第 901-1000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400
EU-CHEVROLET-BERETTA-L-COUPE-2D-01	4757	1735	1346
EU-CHRYSLER-VOYAGER-III-MPV-LWB-01	5070	1950	1740
EU-CHRYSLER-VOYAGER-III-MPV-SWB-01	4733	1950	1740
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108
EU-CITROEN-XM-Y3-HATCHBACK-5D-01	4709	1793	1385
EU-CITROEN-XM-Y3-WAGON-5D-01	4963	1794	1464
EU-DAEWOO-NUBIRA-III-WAGON-5D-01	4580	1725	1460
EU-DAEWOO-NUBIRA-J100-HATCHBACK-5D-01	4280	1699	1430
EU-DAEWOO-NUBIRA-J100-WAGON-01	4514	1700	1432
EU-DAEWOO-NUBIRA-J150-SEDAN-01	4495	1700	1430
EU-DAEWOO-NUBIRA-J150-WAGON-01	4550	1720	1430
EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	3605	1665	1550
EU-DAIHATSU-SIRION-II-M3-SPORT-HATCHBACK-5D-01	3630	1665	1550
EU-DAIHATSU-SIRION-M1-HATCHBACK-01	3675	1595	1450
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	5681	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	5681	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	5181	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	5181	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	4831	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	5980	2040	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	5980	2040	2125
EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	5998	2050	2524
EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	5413	2050	2524
EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	4963	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779
EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	5599	2024	2470
EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	5099	2024	2470
EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	5099	2024	2480
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104
EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-DUCATO-X230-TRUCK-LWB-01	5620	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-MWB-01	5120	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-SWB-01	4770	2000	2100
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100
EU-FIAT-FIORINO-III-VAN-MPV-01	3864	1716	1721
EU-FIAT-MAREA-185-WEEKEND-WAGON-5D-01	4485	1740	1510
EU-FIAT-PALIO-I-178-HATCHBACK-01	3827	1634	1446
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420
EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	3538	1589	1540
EU-FIAT-PANDA-II-169-NATURAL-POWER-HATCHBACK-5D-01	3538	1589	1576
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359
EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	4653	1857	1351
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407
EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	4190	1695	1375
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460
EU-HONDA-CIVIC-VIII-SEDAN-IMA-01	4488	1753	1430
EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	3495	1485	1580
EU-KIA-SPORTAGE-II-KM-SUV-01	4350	1840	1730
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310
EU-MAZDA-323-III-BF-HATCHBACK-3D-01	3990	1645	1390
EU-MAZDA-323-III-BF-HATCHBACK-5D-01	3990	1645	1390
EU-MAZDA-323-III-BF-WAGON-5D-01	4219	1646	1430
EU-MERCEDES-BENZ-124-A124-CONVERTIBLE-2D-01	4655	1740	1391
EU-MERCEDES-BENZ-124-C124-COUPE-2D-01	4655	1740	1394
EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	4740	1740	1428
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-NISSAN-PATHFINDER-III-R51-SUV-01	4740	1850	1865
EU-NISSAN-PRIMERA-P10-SEDAN-01	4430	1715	1410
EU-NISSAN-PRIMERA-P12-HATCHBACK-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-SEDAN-01	4565	1760	1480
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480
EU-NISSAN-SUNNY-B14-SEDAN-4D-01	4295	1690	1385
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704
EU-OPEL-ANTARA-A-SUV-02	4575	1850	1704
EU-PEUGEOT-205-I-CABRIOLET-01	3705	1590	1375
EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	3705	1560	1375
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-HIGHROOF-01	5599	2024	2505
EU-PEUGEOT-BOXER-I-230L-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-230L-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-HIGHROOF-01	4749	2024	2515
EU-PEUGEOT-BOXER-I-230L-VAN-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-230P-BUS-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-230P-BUS-SWB-LOWROOF-01	4749	2024	2150
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-LWB-01	5506	2020	2150
EU-PEUGEOT-BOXER-I-244-CHASSIS-CAB-MWB-01	5006	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-LWB-01	5490	2020	2150
EU-PEUGEOT-BOXER-I-244-FLOOR-CAB-MWB-01	4990	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-CAB-LWB-01	5680	2020	2150
EU-PEUGEOT-BOXER-I-244-PLATFORM-DOUBLE-CAB-LWB-01	5710	2020	2150
EU-PEUGEOT-BOXER-I-244-VAN-LWB-HIGHROOF-01	5599	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2870
EU-PEUGEOT-BOXER-I-244-VAN-MWB-HIGHROOF-01	5099	2024	2505
EU-PEUGEOT-BOXER-I-244-VAN-MWB-LOWROOF-01	5099	2024	2150
EU-PEUGEOT-BOXER-I-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2690
EU-PEUGEOT-BOXER-I-244-VAN-SWB-HIGHROOF-01	4749	2024	2515
EU-PEUGEOT-BOXER-I-244-VAN-SWB-LOWROOF-01	4749	2024	2150
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
EU-PEUGEOT-EXPERT-I-BUS-01	4440	1810	1940
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	5016	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-LWB-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-SWB-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	4805	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	5135	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276
EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	4522	1844	1919
EU-PEUGEOT-EXPERT-I-VAN-01	4440	1810	1940
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459
EU-SEAT-CORDOBA-II-6L-SEDAN-01	4280	1698	1441
EU-SEAT-CORDOBA-II-SEDAN-6L2-01	4280	1698	1441
EU-SSANGYONG-KORANDO-III-C200-SUV-5D-01	4410	1830	1675
EU-SUBARU-IMPREZA-II-FACELIFT-SEDAN-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-FACELIFT1-01	4415	1740	1440
EU-SUBARU-IMPREZA-II-GD-SEDAN-PREFL-01	4405	1730	1440
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-STANDARD-01	4465	1695	1485
EU-SUBARU-IMPREZA-II-GG-WAGON-FACELIFT-WRX-01	4465	1695	1465
EU-SUBARU-IMPREZA-III-GH-HATCHBACK-5D-01	4415	1740	1475
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485
EU-TOYOTA-CAMRY-V20-SEDAN-4D-4WD-01	4520	1710	1400
EU-TOYOTA-CAMRY-XV30-SEDAN-4D-01	4815	1795	1500
EU-VOLVO-740-SEDAN-PREFL-01	4785	1760	1430
EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	4476	1770	1454
EU-VOLVO-S40-II-SEDAN-01	4468	1770	1452
EU-VOLVO-S40-II-SEDAN-MS-01	4476	1770	1454
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	5136	1840	1920
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	4736	1840	1920
EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	5136	1840	1910
EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	5271	1970	1910
EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	5271	1970	1910
EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	5271	1970	1910
EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	4871	1970	1910
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A4 b8 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	180	245	Nov 2011	Dec 2015	2024-03-01	20119
VW	Jetta i	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1981	Jul 1983	2024-03-01	20120
Mercedes-benz	124	200 E	Stufenheck	Heckantrieb	Benzin	77	105	Nov 1992	May 1993	2024-03-01	20122
Mitsubishi	Colt iv	1.6 4WD	Schrägheck	Allrad	Benzin	84	114	Aug 1993	Aug 1995	2024-03-01	20133
Mercedes-benz	190	2.3	Stufenheck	Heckantrieb	Benzin	97	132	Sep 1987	Sep 1988	2024-03-01	20136
Mercedes-benz	190	2.3 E	Stufenheck	Heckantrieb	Benzin	100	136	Oct 1982	Sep 1988	2024-03-01	20137
Mercedes-benz	190	2.6	Stufenheck	Heckantrieb	Benzin	118	160	Oct 1982	Sep 1988	2024-03-01	20138
Seat	Cordoba	1.4	Stufenheck	Frontantrieb	Benzin	40	54	Dec 1997	Apr 1999	2024-03-01	20143
Citroën	Xm	3	Schrägheck	Frontantrieb	Benzin	123	167	May 1989	May 1994	2024-03-01	20152
Saab	9000	2.3	Stufenheck	Frontantrieb	Benzin	165	224	Sep 1990	Oct 1998	2024-03-01	20159
Porsche	911	3.6 S	Cabriolet	Heckantrieb	Benzin	331	450	Aug 2004	Aug 2005	2024-03-01	20165
Lada	Samara	1.5	Schrägheck	Frontantrieb	Benzin	56	76	Apr 1996	Dec 2013	2024-03-01	20166
Porsche	911	3.8 Carrera 4S	Cabriolet	Allrad	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20170
Peugeot	205 i	1.1	Cabriolet	Frontantrieb	Benzin	40	54	Aug 1987	Dec 1994	2024-03-01	20195
Peugeot	205 ii	1	Schrägheck	Frontantrieb	Benzin	37	50	Aug 1992	May 1997	2024-03-01	20204
Peugeot	205 ii	1.1 XA	Schrägheck	Frontantrieb	Benzin	40	54	Jul 1987	Oct 1988	2024-03-01	20205
Volvo	960	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	121	165	Sep 1990	Aug 1993	2024-03-01	20209
Volvo	960	2.8 GL	Stufenheck	Heckantrieb	Benzin	108	147	Sep 1990	May 1992	2024-03-01	20210
Volvo	960	2.3 Turbo	Kombi	Heckantrieb	Benzin	121	165	Sep 1990	Aug 1993	2024-03-01	20214
Fiat	Ducato	2.8 TD 4X4	Kasten	Allrad	Diesel	90	122	May 1998	Sep 2001	2024-03-01	20229
Mazda	323 ii	1.6 GLX	Stufenheck	Frontantrieb	Benzin	54	73	Jun 1986	Mar 1987	2024-03-01	20232
Mazda	323 iii	1.6 GLX	Stufenheck	Frontantrieb	Benzin	54	73	Jun 1986	Mar 1987	2024-03-01	20235
Fiat	Fiorino	1.7 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	46	63	Nov 1996	May 2000	2024-03-01	20266
Peugeot	605	3	Stufenheck	Frontantrieb	Benzin	123	167	Aug 1989	Jun 1994	2024-03-01	20280
Peugeot	605	3	Stufenheck	Frontantrieb	Benzin	147	200	Aug 1989	Jun 1994	2024-03-01	20281
Renault	19 i chamade	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1990	Apr 1992	2024-03-01	20302
Volvo	740	2	Stufenheck	Heckantrieb	Benzin	82	111	Sep 1990	Aug 1992	2024-03-01	20317
Volvo	740	2.0 Turbo	Stufenheck	Heckantrieb	Benzin	114	155	Sep 1990	Aug 1991	2024-03-01	20319
Citroën	C25	2.5 D	Bus	Frontantrieb	Diesel	55	75	Nov 1981	Jan 1994	2024-03-01	20326
Toyota	Camry	2.4	Stufenheck	Frontantrieb	Benzin	116	158	Jan 2006	Sep 2011	2024-03-01	20332
Honda	Civic viii	1.8	Stufenheck	Frontantrieb	Benzin	103	140	Sep 2005	Feb 2012	2024-03-01	20348
Nissan	Laurel	2.0 GL	Stufenheck	Heckantrieb	Benzin	75	102	Nov 1984	Dec 1985	2024-03-01	20358
Nissan	Laurel	2.0 GL	Stufenheck	Heckantrieb	Benzin	75	102	Nov 1984	Dec 1985	2024-03-01	20361
Nissan	Sunny	1.6 4X4	Stufenheck	Allrad	Benzin	66	90	Jul 1986	Oct 1988	2024-03-01	20366
Nissan	Primera	1.6 Visia	Kombi	Frontantrieb	Benzin	80	109	Jan 2002	Apr 2006	2024-03-01	20403
Honda	Crx ii	1.4 GL	Coupe	Frontantrieb	Benzin	66	90	Jan 1990	Dec 1991	2024-03-01	20415
Subaru	Impreza	2.0 AWD	Stufenheck	Allrad	Benzin	206	280	Sep 1996	Sep 2000	2025-06-01	20427
KIA	Sportage ii	2.0 Crdi	SUV	Frontantrieb	Diesel	83	113	Feb 2005	Dec 2006	2024-05-01	20433
Maserati	Biturbo	430	Stufenheck	Heckantrieb	Benzin	165	224	Oct 1991	Sep 1994	2024-03-01	20436
Honda	Civic vi hatchback	1.6	Schrägheck	Frontantrieb	Benzin	92	125	Nov 1998	Mar 2001	2024-03-01	20440
Proton	Persona 400	1.8	Schrägheck	Frontantrieb	Benzin	99	135	Aug 2000	Dec 2001	2024-03-01	20442
Proton	Persona 400	416	Stufenheck	Frontantrieb	Benzin	70	95	Aug 2000	Feb 2002	2024-03-01	20443
Mitsubishi	Eclipse iv	2.4 GS	Coupe	Frontantrieb	Benzin	120	163	Apr 2005	Dec 2011	2024-03-01	20447
Volvo	S40 i	1.8	Stufenheck	Frontantrieb	Benzin	85	116	Jun 2001	Aug 2003	2024-03-01	20459
Mercedes-benz	C-Klasse	C 220	Coupe	Heckantrieb	Benzin	120	163	May 2002	May 2008	2024-03-01	20460
Peugeot	Expert	1.9 D	Bus	Frontantrieb	Diesel	51	69	Dec 2003	Dec 2006	2024-03-01	20469
Peugeot	Expert	2.0 HDI	Bus	Frontantrieb	Diesel	69	94	Oct 2000	Oct 2006	2024-03-01	20470
Mitsubishi	L200	2.5 TD	Pick-up	Heckantrieb	Diesel	66	90	Aug 2001	Nov 2005	2024-03-01	20474
Fiat	Panda	0.9	Schrägheck	Frontantrieb	Benzin	48	65	Feb 2012	-	2024-03-01	20475
Fiat	Marea	1.6 SX	Stufenheck	Frontantrieb	Benzin	72	98	Sep 2000	Aug 2002	2024-03-01	20481
VW	Transporter t5	VR6 3.2 4motion	Kasten	Allrad	Benzin	173	235	Nov 2003	Nov 2009	2024-03-01	20485
VW	Transporter t4	2.8	Pritsche/Fahrgestell	Frontantrieb	Benzin	103	140	May 1996	May 2000	2024-03-01	20486
Lada	Samara	1.5	Stufenheck	Frontantrieb	Benzin	57	78	Jan 2000	Dec 2006	2024-03-01	20498
Porsche	911	3.8 Carrera S	Cabriolet	Heckantrieb	Benzin	280	381	Aug 2005	Dec 2008	2024-03-01	20506
Honda	Civic vi fastback	1.6	Schrägheck	Frontantrieb	Benzin	92	125	Nov 1998	Feb 2001	2024-03-01	20511
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	160	218	Nov 1995	May 1999	2024-03-01	20516
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	225	306	Nov 1995	May 1999	2024-03-01	20517
Ford USA	Mustang convertible	4.6	Cabriolet	Heckantrieb	Benzin	160	218	Nov 1995	May 1999	2024-03-01	20518
Ford USA	Mustang convertible	4.6	Cabriolet	Heckantrieb	Benzin	228	310	Nov 1995	May 1999	2024-03-01	20519
Ssangyong	Korando	2.3 Tdic 4X4	Geländewagen geschlossen	Allrad	Diesel	74	101	Jul 1998	Nov 2006	2024-03-01	20521
Hyundai	H-1 / starex	2.5 TCI	Bus	Heckantrieb	Diesel	73	99	Oct 1997	Dec 2007	2024-03-01	20542
Hyundai	H-1 / starex	2.5 TCI	Bus	Heckantrieb	Diesel	74	101	May 2004	Dec 2007	2024-03-01	20543
Hyundai	H-1 / starex	2.5 Crdi	Bus	Heckantrieb	Diesel	103	140	Dec 2002	Sep 2007	2024-03-01	20544
Opel	Antara a	2.4 4X4	SUV	Allrad	Benzin	103	140	Aug 2006	Dec 2011	2024-03-01	20545
Hyundai	H-1 / starex	2.5 Crdi 4WD	Bus	Allrad	Diesel	103	140	Dec 2002	Apr 2004	2024-03-01	20546
Chevrolet	Beretta	2.8 GT	Coupe	Frontantrieb	Benzin	93	126	Oct 1988	Sep 1989	2024-03-01	20547
Chevrolet	Beretta	3.1 LT	Coupe	Frontantrieb	Benzin	103	140	Oct 1992	Sep 1993	2024-03-01	20548
Chevrolet	Beretta	3.1 Z26	Coupe	Frontantrieb	Benzin	119	162	Oct 1993	Sep 1996	2024-03-01	20549
Chevrolet	Corsica	3.1	Stufenheck	Frontantrieb	Benzin	106	144	Oct 1989	Sep 1992	2024-03-01	20553
VW	Golf iv variant	1.9 TDI	Kombi	Frontantrieb	Diesel	110	150	Jun 2001	Jun 2006	2024-03-01	20556
Saab	9-5	2.0 T	Stufenheck	Frontantrieb	Benzin	136	185	Jul 2000	Dec 2009	2024-03-01	20565
Saab	9-5	2.0 Turbo SE	Stufenheck	Frontantrieb	Benzin	141	192	Oct 1998	Jul 2000	2024-03-01	20566
Saab	9-5	2.3 Turbo	Stufenheck	Frontantrieb	Benzin	224	305	Jun 2003	Aug 2005	2024-03-01	20567
Fiat	Palio	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1997	Aug 2002	2024-03-01	20569
Fiat	Palio	1.3	Kombi	Frontantrieb	Benzin	59	80	Sep 2001	Oct 2004	2024-11-01	20576
Fiat	Palio	1.9 JTD	Kombi	Frontantrieb	Diesel	59	80	Sep 2001	-	2024-03-01	20581
Daewoo	Nubira	2.0 CDX	Schrägheck	Frontantrieb	Benzin	93	126	Aug 2002	Jul 2003	2024-03-01	20586
Chrysler	Voyager ii	3	Großraumlimousine	Frontantrieb	Benzin	104	141	Oct 1990	Sep 1995	2024-03-01	20618
Buick	Park avenue	3.8 Supercharged	Stufenheck	Frontantrieb	Benzin	179	243	Oct 1996	Dec 2005	2024-03-01	20620
Hyundai	Atos	1.1	Schrägheck	Frontantrieb	Benzin	43	58	Aug 2003	Dec 2008	2024-03-01	20623
Citroën	C25	1.9 D 1400	Kasten	Frontantrieb	Diesel	51	69	Jan 1988	Jan 1994	2024-03-01	20628
Citroën	C25	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	57	78	Nov 1981	Dec 1986	2024-03-01	20631
Citroën	C25	2.5 DT	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Jan 1987	Jan 1994	2024-03-01	20633
Daihatsu	Sirion	1.3 4WD	Schrägheck	Allrad	Benzin	64	87	Apr 2005	-	2024-03-01	20634
Saab	9-3	2.3	Schrägheck	Frontantrieb	Benzin	169	230	Sep 1999	Jan 2002	2024-03-01	20635
Saab	9-3	2.0 Turbo Performance	Cabriolet	Frontantrieb	Benzin	185	252	Apr 2004	Feb 2015	2024-03-01	20636
Saab	9-3	2.3	Cabriolet	Frontantrieb	Benzin	169	230	Sep 1999	Jan 2002	2024-03-01	20637
Mercedes-benz	Clk	CLK 320 CDI	Cabriolet	Heckantrieb	Diesel	165	224	Mar 2005	Mar 2010	2024-03-01	20640
Nissan	Pathfinder iii	2.5 DCI	SUV	Heckantrieb	Diesel	128	174	Jan 2005	Jan 2010	2024-05-01	20643
Toyota	Rav 4 iii	2.4	SUV	Frontantrieb	Benzin	125	170	Nov 2005	Dec 2013	2024-03-01	20645
Saab	9-5	2.0 T Biopower	Kombi	Frontantrieb	Benzin/Ethanol	132	179	Sep 2005	Dec 2009	2024-03-01	20646
Saab	9-5	2.0 T	Kombi	Frontantrieb	Benzin	136	185	Jul 2000	Jul 2001	2024-03-01	20647
Lotus	Esprit s4	2.0 GT3	Coupe	Heckantrieb	Benzin	179	243	Sep 1996	Jun 2000	2024-03-01	20649
Mazda	323 s vi	2.0 Ditd	Stufenheck	Frontantrieb	Diesel	74	101	Oct 2000	Oct 2002	2024-03-01	20654
VW	Vento	2.0 GL	Stufenheck	Frontantrieb	Benzin	79	107	May 1996	Dec 1997	2024-03-01	20659
VW	Transporter t5	3.2 V6 4motion	Bus	Allrad	Benzin	173	235	Nov 2003	Dec 2009	2024-03-01	20661
Honda	Accord vi	1.6 LS	Stufenheck	Frontantrieb	Benzin	79	107	Oct 1998	Dec 2002	2024-03-01	20663
Nissan	Patrol gr v wagon	4.8	Geländewagen geschlossen	Allrad	Benzin	180	245	Mar 2000	-	2024-03-01	20673
BMW	3	330 I	Coupe	Heckantrieb	Benzin	190	258	Mar 2010	Jun 2013	2024-03-01	20683
Peugeot	Boxer	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	81	110	Dec 2001	Apr 2002	2024-03-01	20693


--- 新建对话（分支降级） / Round 35 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6933b4-93ec-83ea-b5f5-9474ec3faec8
新对话：https://chatgpt.com/c/6a6cc18c-62a0-83ea-9e51-7e4566f7da4c

--- Round 35 / checkpoint 续跑 ---
## 更新点

* 已闭合 27 个 Ktype，共形成 29 条 READY 映射；其中 21 个既有尺寸组直接复用，未重复抓取。
* 首次创建 5 个尺寸组：Seat Cordoba I、Toyota Camry XV40、Mitsubishi Eclipse IV、Volvo S40 I、VW Golf IV Variant。([汽车目录][1])
* Mercedes-Benz 190/W201 的直接规格页面出现 `4420×1678×1390` 与 `4450×1690×1375` 两套冲突数据，Ktype `20136`–`20138` 本轮未强行建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：27
* READY 映射行：29
* PENDING Ktype：73
* 已确认尺寸组：26

  * 复用已有尺寸组：21
  * 本轮首次创建：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20119	20119	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	8K5 Avant 改款车身。	READY
20122	20122	Sedan	124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	HIGH	W124 四门轿车。	READY
20143	20143	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH	6K2 四门轿车。	READY
20152	20152	Hatchback	XM Y3	Y3	5	EU-CITROEN-XM-Y3-HATCHBACK-5D-01	HIGH	Y3 五门掀背车身。	READY
20170	20170	Convertible	911 997	997	2	EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	HIGH	Carrera 4S 宽体敞篷分支。	READY
20195	20195	Convertible	205 I		2	EU-PEUGEOT-205-I-CABRIOLET-01	HIGH	205 Cabriolet 双门车身。	READY
20302	20302	Sedan	19 I	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH	Chamade L53 四门轿车。	READY
20332	20332	Sedan	Camry VI	XV40	4	EU-TOYOTA-CAMRY-VI-XV40-SEDAN-4D-01	HIGH	XV40 四门轿车。	READY
20403	20403	Wagon	Primera P12	WP12	5	EU-NISSAN-PRIMERA-P12-WAGON-01	HIGH	WP12 五门旅行车。	READY
20433	20433	SUV	Sportage II	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-01	HIGH	KM 五门 SUV。	READY
20440	20440	Hatchback	Civic VI		3	EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	HIGH	三门 Hatchback 分支。	READY
20447	20447	Coupe	Eclipse IV	DK	2	EU-MITSUBISHI-ECLIPSE-IV-DK-COUPE-2D-01	HIGH	DK 双门 Coupe。	READY
20459	20459	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH	VS 四门轿车。	READY
20469	20469	MPV	Expert I			EU-PEUGEOT-EXPERT-I-BUS-01	HIGH	第一代乘用 Bus 外廓。	READY
20470	20470	MPV	Expert I			EU-PEUGEOT-EXPERT-I-BUS-01	HIGH	第一代乘用 Bus 外廓。	READY
20545	20545	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07 五门 SUV。	READY
20547	20547	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20548	20548	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20549	20549	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20556	20556	Wagon	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-VARIANT-1J5-WAGON-5D-01	HIGH	1J5 五门旅行车。	READY
20620_prefl	20620	Sedan	Park Avenue I	G	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	MEDIUM	生产区间跨外廓改款，拆分改款前。	READY
20620_facelift	20620	Sedan	Park Avenue I	G	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	MEDIUM	生产区间跨外廓改款，拆分改款后。	READY
20623	20623	Hatchback	Atos Prime	MX	5	EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	HIGH	MX 五门车身。	READY
20636_prefl	20636	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	MEDIUM	生产区间跨改款，拆分改款前敞篷车身。	READY
20636_facelift	20636	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	MEDIUM	生产区间跨改款，拆分改款后敞篷车身。	READY
20640	20640	Convertible	CLK II	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	HIGH	A209 改款敞篷车身。	READY
20643	20643	SUV	Pathfinder III	R51	5	EU-NISSAN-PATHFINDER-III-R51-SUV-01	HIGH	R51 五门 SUV。	READY
20646	20646	Wagon	9-5 I facelift 2005	YS3E	5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH	2005 改款五门旅行车。	READY
20683	20683	Coupe	3 Series E92 facelift	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	E92 改款双门 Coupe。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4142	1640	1408	Automobile-Catalog 1997 Seat Cordoba 1.4	https://www.automobile-catalog.com/car/1997/3065810/seat_cordoba_1_4.html
EU-TOYOTA-CAMRY-VI-XV40-SEDAN-4D-01	4805	1820	1460	Auto-Data Toyota Camry VI (XV40) 2.4i 158 hp	https://www.auto-data.net/en/toyota-camry-vi-xv40-2.4i-16v-158hp-31250
EU-MITSUBISHI-ECLIPSE-IV-DK-COUPE-2D-01	4565	1835	1358	Automobile-Catalog 2006 Mitsubishi Eclipse GS	https://www.automobile-catalog.com/car/2006/2007470/mitsubishi_eclipse_gs.html
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Auto-Data Volvo S40 (VS) generation	https://www.auto-data.net/en/volvo-s40-vs-generation-1972
EU-VW-GOLF-IV-VARIANT-1J5-WAGON-5D-01	4397	1735	1485	Volkswagen Newsroom Golf IV Variant vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
```

## 下一步优先处理

1. 先解决可批量闭合的普通乘用车组：Volvo 960、Saab 9000/9-5、Lada Samara、Proton Persona、Honda Accord及 Mazda 323。
2. 集中拆分商用车外廓：Fiat Ducato、Citroën C25、VW Transporter T4/T5、Hyundai H-1，按轴距、车顶和车身形式处理。
3. 单独处理存在来源冲突或门数不明的 W201、Jetta I、Peugeot 205、Peugeot 605、Fiat Marea、Chevrolet Corsica。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/3065810/seat_cordoba_1_4.html?utm_source=chatgpt.com "1997 Seat Cordoba 1.4 Specs Review (44 kW ..."
[2]: https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808?utm_source=chatgpt.com "Mercedes-Benz 190 (W201) E 2.3 CAT (132 Hp)"


--- 发送 / 继续到 Round 36 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 36 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 18 个 Ktype，形成 18 条 READY 映射。
* 首次创建 12 个尺寸组，覆盖 Volvo 960、Peugeot 605、Fiat Marea、Lada Samara、Porsche 911 Carrera S Cabriolet、Honda Civic Fastback、Saab 9-3 Cabriolet、Lotus Esprit GT3、Mazda 323 S VI、VW Vento 和 Honda Accord VI。([汽车数据网][1])
* 另外直接复用 3 个已有尺寸组，关联 Volvo 740、Maserati Biturbo 430 和 Daihatsu Sirion II；未重复输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：45
* READY 映射：47
* PENDING Ktype：55
* 当前批次已引用尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20209	20209	Sedan	960	964	4	EU-VOLVO-960-964-SEDAN-4D-01	HIGH	964 四门轿车外廓。	READY
20210	20210	Sedan	960	964	4	EU-VOLVO-960-964-SEDAN-4D-01	HIGH	964 四门轿车外廓。	READY
20214	20214	Wagon	960	965	5	EU-VOLVO-960-965-WAGON-5D-01	HIGH	965 五门旅行车外廓。	READY
20280	20280	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-4D-01	HIGH	6B 四门轿车外廓。	READY
20281	20281	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-4D-01	HIGH	6B 四门轿车外廓。	READY
20317	20317	Sedan	740	744	4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	744 四门轿车外廓。	READY
20319	20319	Sedan	740	744	4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	744 四门轿车外廓。	READY
20436	20436	Sedan	Biturbo			EU-MASERATI-BITURBO-420-SI-SEDAN-01	MEDIUM	430 四门长轴 Biturbo 外廓。	READY
20481	20481	Sedan	Marea 185 facelift	185	4	EU-FIAT-MAREA-185-FACELIFT-SEDAN-4D-01	MEDIUM	185 改款四门轿车外廓。	READY
20498	20498	Sedan	Samara I	21099	4	EU-LADA-SAMARA-I-21099-SEDAN-4D-01	HIGH	21099 四门轿车外廓。	READY
20506	20506	Convertible	911 997	997	2	EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	HIGH	997 Carrera S 后驱敞篷外廓。	READY
20511	20511	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	五门 Fastback 外廓。	READY
20634	20634	Hatchback	Sirion II	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	MEDIUM	M3 五门外廓。	READY
20637	20637	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷外廓。	READY
20649	20649	Coupe	Esprit S4		2	EU-LOTUS-ESPRIT-S4-GT3-COUPE-2D-01	HIGH	GT3 双门 Coupe 外廓。	READY
20654	20654	Sedan	323 S VI facelift	BJ	4	EU-MAZDA-323-S-VI-BJ-FACELIFT-SEDAN-4D-01	HIGH	BJ 改款四门轿车外廓。	READY
20659	20659	Sedan	Vento	1HX0	4	EU-VW-VENTO-1HX0-SEDAN-4D-01	HIGH	1HX0 四门轿车外廓。	READY
20663	20663	Sedan	Accord VI		4	EU-HONDA-ACCORD-VI-SEDAN-4D-01	HIGH	欧洲版 Accord VI 四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-960-964-SEDAN-4D-01	4871	1750	1411	Auto-Data Volvo 960 (964) 2.0 i 16V	https://www.auto-data.net/en/volvo-960-964-2.0-i-16v-190hp-9355
EU-VOLVO-960-965-WAGON-5D-01	4850	1750	1434	Auto-Data Volvo 960 Kombi (965) 3.0 i 24V	https://www.auto-data.net/en/volvo-960-kombi-965-3.0-i-24v-204hp-9362
EU-PEUGEOT-605-6B-SEDAN-4D-01	4765	1799	1415	Auto-Data Peugeot 605 (6B) 3.0	https://www.auto-data.net/en/peugeot-605-6b-3.0-167hp-5332
EU-FIAT-MAREA-185-FACELIFT-SEDAN-4D-01	4393	1740	1420	Auto-Data Fiat Marea (185) 1.8 i 16V	https://www.auto-data.net/en/fiat-marea-185-1.8-i-16v-132hp-7196
EU-LADA-SAMARA-I-21099-SEDAN-4D-01	4205	1650	1402	Auto-Data Lada 21099-20 generation	https://www.auto-data.net/en/lada-21099-20-generation-2832
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300	Auto-Data Porsche 911 Cabriolet (997) Carrera S 3.8	https://www.auto-data.net/en/porsche-911-cabriolet-997-carrera-s-3.8-355hp-6588
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Auto-Data Honda Civic VI Fastback	https://www.auto-data.net/en/honda-civic-model-1307
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1423	Auto-Data Saab 9-3 Convertible I 2.0 T	https://www.auto-data.net/en/saab-9-3-convertible-i-2.0-t-205hp-11967
EU-LOTUS-ESPRIT-S4-GT3-COUPE-2D-01	4369	1883	1150	Auto-Data Lotus Esprit 2.0 i 16V Turbo GT3	https://www.auto-data.net/en/lotus-esprit-2.0-i-16v-turbo-gt3-243hp-8298
EU-MAZDA-323-S-VI-BJ-FACELIFT-SEDAN-4D-01	4390	1705	1410	Auto-Data Mazda 323 S VI (BJ) 2.0 DiTD	https://www.auto-data.net/en/mazda-323-s-vi-bj-2.0-ditd-101hp-11150
EU-VW-VENTO-1HX0-SEDAN-4D-01	4380	1695	1415	Auto-Data Volkswagen Vento (1HX0) 2.0	https://www.auto-data.net/en/volkswagen-vento-1hx0-2.0-115hp-8851
EU-HONDA-ACCORD-VI-SEDAN-4D-01	4595	1750	1430	Auto-Data Honda Accord VI	https://www.auto-data.net/en/honda-accord-model-1282
```

## 下一步优先处理

1. 批量闭合 Lada Samara 掀背、Saab 9000/9-5、Proton Persona 400 和 Mazda 323 的剩余普通乘用车。
2. 处理 Porsche 911、Ford Mustang、Chevrolet Corsica 和 Nissan Laurel/Sunny 的代际及改款边界。
3. 最后集中拆分 Fiat Ducato、Citroën C25、VW Transporter T4/T5、Hyundai H-1 等商用车的轴距、车顶和车身形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volvo-960-model-926 "Volvo 960 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 37 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 37 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 8 个 Ktype，共新增 9 条 READY 映射。
* Mercedes-Benz 190/W201 按直接版本规格将 `2.3 CAT 132 hp` 与 `2.3 E/2.6 CAT` 分成两个尺寸组，不再强行合并冲突三维。([汽车数据网][1])
* Lada Samara 的输入生产区间覆盖 21093 与 2114 两种不同外廓，拆成两个派生映射。([汽车数据网][2])
* 新增闭合 Honda Civic VIII Sedan、Nissan Laurel C32 和 Proton Persona I Sedan。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：53
* READY 映射：56
* PENDING Ktype：47
* 当前批次已引用尺寸组：48
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20136	20136	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-01	HIGH	2.3 CAT 132 hp外廓。	READY
20137	20137	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	HIGH	2.3 E 136 hp外廓。	READY
20138	20138	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	HIGH	2.6 CAT 160 hp外廓。	READY
20166_21093	20166	Hatchback	Samara I	21093	5	EU-LADA-SAMARA-I-21093-HATCHBACK-5D-01	MEDIUM	Ktype生产区间覆盖21093与2114两种外廓。	READY
20166_2114	20166	Hatchback	Samara I	2114	5	EU-LADA-SAMARA-I-2114-HATCHBACK-5D-01	MEDIUM	Ktype生产区间覆盖21093与2114两种外廓。	READY
20348	20348	Sedan	Civic VIII		4	EU-HONDA-CIVIC-VIII-SEDAN-4D-01	HIGH	1.8四门轿车外廓。	READY
20358	20358	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	C32四门轿车外廓。	READY
20361	20361	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	C32四门轿车外廓。	READY
20443	20443	Sedan	Persona I		4	EU-PROTON-PERSONA-I-SEDAN-4D-01	HIGH	416四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-190-W201-SEDAN-4D-01	4420	1678	1390	Auto-Data Mercedes-Benz 190 W201 E 2.3 CAT 132 Hp	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808
EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	4450	1690	1375	Auto-Data Mercedes-Benz 190 W201 E 2.3 136 Hp;Auto-Data Mercedes-Benz 190 W201 E 2.6 CAT 160 Hp	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-136hp-12801;https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.6-cat-160hp-12806
EU-LADA-SAMARA-I-21093-HATCHBACK-5D-01	4006	1650	1402	Auto-Data Lada 21093 1.5 72 Hp	https://www.auto-data.net/en/lada-21093-1.5-72hp-13271
EU-LADA-SAMARA-I-2114-HATCHBACK-5D-01	4122	1620	1415	Auto-Data Lada 2114 1.6 i 8V 81 Hp	https://www.auto-data.net/en/lada-2114-1.6-i-8v-81hp-13273
EU-HONDA-CIVIC-VIII-SEDAN-4D-01	4545	1750	1435	Auto-Data Honda Civic VIII Sedan 1.8i 16V 140 Hp	https://www.auto-data.net/en/honda-civic-viii-sedan-1.8i-16v-140hp-12215
EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	4650	1690	1415	Nissan Heritage Collection Laurel C32 Sedan Grand Extra	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/laurel_sedan_grand_extra.html
EU-PROTON-PERSONA-I-SEDAN-4D-01	4360	1680	1385	Auto-Data Proton Persona I 1.6 i 416 GLXi 95 Hp	https://www.auto-data.net/en/proton-persona-i-1.6-i-416-glxi-95hp-8257
```

## 下一步优先处理

1. 闭合 Mitsubishi Colt IV、Honda CRX II、Subaru Impreza GC、Mercedes-Benz CL203 和 Toyota RAV4 III。
2. 处理 Saab 9000、Saab 9-5 Sedan/Wagon 的改款边界。
3. 最后集中拆分 Ducato、C25、Transporter T4/T5、Hyundai H-1 和 Boxer 商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808 "Mercedes-Benz 190 (W201) E 2.3 CAT (132 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/lada-21093-1.5-72hp-13271 "Lada 21093 1.5 (72 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/honda-civic-viii-sedan-1.8i-16v-140hp-12215?utm_source=chatgpt.com "Honda Civic VIII Sedan 1.8i 16V (140 Hp)"


--- 发送 / 继续到 Round 38 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 38 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 8 个 Ktype，新增 12 条 READY 映射。
* Peugeot 205 复用既有尺寸组；Mercedes-Benz CL203、Fiat Panda III、Saab 9-3 I 及 Saab 9-5 三个外廓阶段完成首次建组。([汽车数据网][1])
* Saab 9-5 跨改款 Ktype 按改款前、2001 改款和 2005 改款拆分；2005 改款尺寸组直接复用已有缓存。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：61
* READY 映射：68
* PENDING Ktype：39
* 当前批次已引用尺寸组：56
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20204_3dr	20204	Hatchback	205 I facelift	20A/C	3	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	1.0版本覆盖三门外廓。	READY
20204_5dr	20204	Hatchback	205 I facelift	20A/C	5	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	1.0版本覆盖五门外廓。	READY
20205_3dr	20205	Hatchback	205 I facelift	20A/C	3	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	XA三门商用衍生外廓。	READY
20460	20460	Coupe	C-Class Sport Coupe CL203	CL203	3	EU-MERCEDES-BENZ-C-CLASS-CL203-SPORT-COUPE-3D-01	MEDIUM	输入版本名称与功率标签不一致；CL203三门外廓已确认。	READY
20475	20475	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-5D-01	HIGH	319五门前驱车身。	READY
20565_prefl	20565	Sedan	9-5 I	YS3E	4	EU-SAAB-9-5-PREFL-SEDAN-4D-01	MEDIUM	Ktype生产区间覆盖改款前车身。	READY
20565_facelift2001	20565	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	MEDIUM	Ktype生产区间覆盖2001改款车身。	READY
20565_facelift2005	20565	Sedan	9-5 I facelift 2005	YS3E	4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	MEDIUM	Ktype生产区间覆盖2005改款车身。	READY
20566	20566	Sedan	9-5 I	YS3E	4	EU-SAAB-9-5-PREFL-SEDAN-4D-01	HIGH	改款前四门轿车外廓。	READY
20635_3dr	20635	Hatchback	9-3 I	YS3D	3	EU-SAAB-9-3-I-YS3D-HATCHBACK-01	HIGH	2.3T版本覆盖三门掀背外廓。	READY
20635_5dr	20635	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-01	HIGH	2.3T版本覆盖五门掀背外廓。	READY
20647	20647	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-PREFL-WAGON-5D-01	HIGH	改款前五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-CL203-SPORT-COUPE-3D-01	4343	1728	1406	Auto-Data Mercedes-Benz C-class Sport Coupe CL203 C 200 Kompressor 163 Hp;Auto-Data Mercedes-Benz C-class Sport Coupe CL203 facelift 2004 C 200 Kompressor 163 Hp	https://www.auto-data.net/en/mercedes-benz-c-class-sport-coupe-cl203-c-200-kompressor-163hp-12591;https://www.auto-data.net/en/mercedes-benz-c-class-sport-coupe-cl203-facelift-2004-c-200-kompressor-163hp-44250
EU-FIAT-PANDA-III-319-HATCHBACK-5D-01	3653	1643	1551	Auto-Data Fiat Panda III 319 0.9 TwinAir Turbo 85 Hp	https://www.auto-data.net/en/fiat-panda-iii-319-0.9-twin-air-turbo-85hp-start-stop-18364
EU-SAAB-9-5-PREFL-SEDAN-4D-01	4810	1790	1450	Auto-Data Saab 9-5 2.0 T 16V 185 Hp	https://www.auto-data.net/en/saab-9-5-2.0-t-16v-185hp-11844
EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	4827	1792	1475	Auto-Data Saab 9-5 facelift 2001 generation	https://www.auto-data.net/en/saab-9-5-facelift-2001-generation-7159
EU-SAAB-9-3-I-YS3D-HATCHBACK-01	4629	1711	1428	Auto-Data Saab 9-3 I 2.3 T 230 Hp	https://www.auto-data.net/en/saab-9-3-i-2.3-t-230hp-11965
EU-SAAB-9-5-PREFL-WAGON-5D-01	4808	1792	1497	Auto-Data Saab 9-5 Sport Combi generation	https://www.auto-data.net/en/saab-9-5-sport-combi-generation-2532
```

## 下一步优先处理

1. 闭合 Mitsubishi Colt IV、Honda CRX II、Subaru Impreza GC、Proton Persona Hatchback 和 Mazda 323 Sedan。
2. 处理 Ford Mustang SN95/New Edge、Porsche 911 Turbo S、Chevrolet Corsica、Nissan Sunny及 Patrol Y61 的改款边界。
3. 最后集中处理 Ducato、C25、Transporter T4/T5、Hyundai H-1、Voyager 和 Boxer 的轴距、车顶与车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-205-i-20a-c-facelift-1987-1.0-i-50hp-5639?utm_source=chatgpt.com "Peugeot 205 I (20A/C, facelift 1987) 1.0 i (50 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 39 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 39 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 9 个 Ktype，新增 10 条 READY 映射。
* 首次创建 8 个尺寸组；Saab 9-5 Ktype `20567` 直接复用已建的 2001 改款轿车尺寸组。
* Fiat Palio Hatchback 当前证据三维与累计表既有组不同，未覆盖旧组，按规则创建 `-02` 新组。([汽车数据网][1])
* Palio Weekend 汽油版与 JTD 版高度不同，分别建立尺寸组；Nubira II Hatchback 按直接版本页面新建 J150 组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：70
* READY 映射：78
* PENDING Ktype：30
* 当前批次已引用尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20133	20133	Hatchback	Colt IV	CA4A	3	EU-MITSUBISHI-COLT-IV-CA4A-HATCHBACK-3D-01	MEDIUM	CA4A三门掀背外廓。	READY
20415	20415	Coupe	CRX II		3	EU-HONDA-CRX-II-COUPE-3D-01	MEDIUM	CRX II三门车身外廓。	READY
20427	20427	Sedan	Impreza I WRX	GC8	4	EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	HIGH	GC8四门WRX外廓。	READY
20442	20442	Hatchback	Persona I Compact		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	HIGH	318i三门Compact外廓。	READY
20567	20567	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	MEDIUM	2001改款四门轿车外廓。	READY
20569_3dr	20569	Hatchback	Palio I	178	3	EU-FIAT-PALIO-I-178-HATCHBACK-02	MEDIUM	同一Ktype覆盖三门外廓。	READY
20569_5dr	20569	Hatchback	Palio I	178	5	EU-FIAT-PALIO-I-178-HATCHBACK-02	MEDIUM	同一Ktype覆盖五门外廓。	READY
20576	20576	Wagon	Palio Weekend	178	5	EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	MEDIUM	80 hp五门Weekend外廓。	READY
20581	20581	Wagon	Palio Weekend	178	5	EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	HIGH	1.9 JTD五门Weekend外廓。	READY
20586	20586	Hatchback	Nubira II	J150	5	EU-DAEWOO-NUBIRA-J150-HATCHBACK-5D-01	HIGH	J150五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-IV-CA4A-HATCHBACK-3D-01	3955	1690	1370	Auto-Data Mitsubishi Colt IV CAO generation	https://www.auto-data.net/en/mitsubishi-colt-iv-cao-generation-3469
EU-HONDA-CRX-II-COUPE-3D-01	3755	1675	1270	Auto-Data Honda CRX II ED EE 1.6 i 16V 124 Hp	https://www.auto-data.net/en/honda-crx-ii-ed-ee-1.6-i-16v-124hp-12375
EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	4340	1690	1405	Automobile-Catalog 1996 Subaru Impreza WRX 280 PS	https://www.automobile-catalog.com/car/1996/3239645/subaru_impreza_wrx.html
EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	3995	1710	1365	Auto-Data Proton Persona I Compact 1.8 318i 135 Hp	https://www.auto-data.net/en/proton-persona-i-compact-1.8-i-16v-318-i-135hp-8236
EU-FIAT-PALIO-I-178-HATCHBACK-02	3735	1626	1446	Auto-Data Fiat Palio 178 1.2 i 68 Hp	https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854
EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	4130	1626	1475	Auto-Data Fiat Palio Weekend 178 1.2 16V 80 Hp	https://www.auto-data.net/en/fiat-palio-weekend-178-1.2-16v-80hp-6839
EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	4130	1626	1515	Auto-Data Fiat Palio Weekend 178 1.9 JTD 80 Hp	https://www.auto-data.net/en/fiat-palio-weekend-178-1.9-jtd-80hp-6849
EU-DAEWOO-NUBIRA-J150-HATCHBACK-5D-01	4280	1700	1430	Auto-Data Daewoo Nubira Hatchback II 2.0 CDX 126 Hp	https://www.auto-data.net/en/daewoo-nubira-hatchback-ii-2.0-i-16v-cdx-126hp-16329
```

## 下一步优先处理

1. 闭合 Jetta I、Mazda 323 Sedan、Nissan Sunny、Chevrolet Corsica 和 Toyota RAV4 III。
2. 处理 Porsche 911、Ford Mustang、L200、Korando 和 Patrol 的特殊车身边界。
3. 最后集中拆分 Ducato、C25、Transporter T4/T5、Hyundai H-1、Voyager 和 Boxer 商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-colt-iv-cao-generation-3469 "Mitsubishi Colt IV (CAO) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854 "Fiat Palio (178) 1.2 i (68 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 40 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 40 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 **12 个 Ktype、12 条 READY 映射**。
* 首次创建 **7 个尺寸组**，覆盖 Porsche 911 Turbo S Cabriolet、Mazda 323 III BF Sedan、Fiat Fiorino 147、SsangYong Korando II、Chevrolet Corsica、Chrysler Voyager II 和 Nissan Patrol Y61。([汽车目录][1])
* Ford Mustang 的 4 个 Ktype 直接关联两个已有尺寸组，未重复输出尺寸组。
* Nissan Sunny `20366` 暂未闭合：输入标签同时出现 B12 与欧洲 N13 线索，且两者外廓不同，不能猜测性建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射：90
* PENDING Ktype：18
* 当前批次已引用尺寸组：71
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20165	20165	Convertible	911 996 facelift	996	2	EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	HIGH	996 Turbo S双门敞篷外廓。	READY
20232	20232	Sedan	323 III	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
20235	20235	Sedan	323 III	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
20266	20266	Van	Fiorino 147	147	3	EU-FIAT-FIORINO-147-VAN-MPV-3D-01	HIGH	147三门厢式乘用衍生外廓。	READY
20516	20516	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	4.6 GT双门Coupe外廓。	READY
20517	20517	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	4.6 Cobra双门Coupe外廓。	READY
20518	20518	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	4.6 GT双门敞篷外廓。	READY
20519	20519	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	4.6 Cobra双门敞篷外廓。	READY
20521	20521	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-3D-01	HIGH	KJ三门SUV外廓。	READY
20553	20553	Sedan	Corsica	L	4	EU-CHEVROLET-CORSICA-L-SEDAN-4D-01	MEDIUM	L-body四门轿车外廓。	READY
20618	20618	MPV	Voyager II	AS	3	EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	MEDIUM	AS短轴乘用MPV外廓。	READY
20673	20673	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	HIGH	Y61改款前五门4.8外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	4435	1830	1295	Automobile-Catalog 2005 Porsche 911 Turbo S Cabrio	https://www.automobile-catalog.com/car/2005/2867225/porsche_911_turbo_s_cabrio.html
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6 LX Sedan catalyst	https://www.automobile-catalog.com/car/1986/1630280/mazda_323_1_6_lx_sedan_cat.html
EU-FIAT-FIORINO-147-VAN-MPV-3D-01	4159	1622	1904	Auto-Data Fiat Fiorino 147 1.7 Diesel 63 Hp	https://www.auto-data.net/en/fiat-fiorino-147-1.7-diesel-63hp-6964
EU-SSANGYONG-KORANDO-II-KJ-SUV-3D-01	4260	1841	1840	Auto-Data SsangYong Korando II KJ 2.3 TD 101 Hp	https://www.auto-data.net/en/ssangyong-korando-ii-kj-2.3-td-101hp-15995
EU-CHEVROLET-CORSICA-L-SEDAN-4D-01	4660	1727	1371	Auto-Data Chevrolet Corsica 3.1 i V6 162 Hp	https://www.auto-data.net/en/chevrolet-corsica-3.1-i-v6-162hp-14493
EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	4525	1830	1707	Auto-Data Chrysler Voyager II	https://www.auto-data.net/en/chrysler-voyager-ii-generation-8878
EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	5010	1930	1855	Auto-Data Nissan Patrol V 5-door Y61	https://www.auto-data.net/en/nissan-patrol-v-5-door-y61-generation-83
```

## 下一步优先处理

1. 解决普通乘用车剩余边界：`20120` Jetta I 门数、`20159` Saab 9000 车身形式、`20366` Sunny B12/N13 冲突和 `20645` RAV4 III 精确三维。
2. 集中闭合商用车组：Fiat Ducato、Citroën C25、Mitsubishi L200、VW Transporter T4/T5、Hyundai H-1 和 Peugeot Boxer。
3. 商用车按车身形式、轴距及车顶高度一次建组，再批量关联剩余 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2005/2867225/porsche_911_turbo_s_cabrio.html?utm_source=chatgpt.com "2005 Porsche 911 Turbo S Cabrio Specs Review (331 kW / 450 PS / 444 hp) (up to mid-year 2005 for Europe )"
[2]: https://www.auto-data.net/en/nissan-sunny-ii-ga15de-b12-1.6-i-73hp-4x4-a-520?utm_source=chatgpt.com "Nissan Sunny II GA15DE (B12) 1.6 i (73 Hp) 4x4 (A)"


--- 发送 / 继续到 Round 41 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 41 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 7 个 Ktype，新增 12 条 READY 映射。
* Jetta I 和 Saab 9000 CD 已完成车身边界及尺寸组建档；Hyundai H-1 按短轴、长轴及高度差异建立 3 个尺寸组。([volkswagen-newsroom.com][1])
* VW Transporter T5 3.2 4Motion 厢式车按 L1H1、L1H2、L2H1、L2H2、L2H3 五个已存在尺寸组批量关联，未重复输出尺寸组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射：102
* PENDING Ktype：11
* 当前批次已引用尺寸组：76
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20120_2dr	20120	Sedan	Jetta I	16	2	EU-VW-JETTA-I-16-SEDAN-01	MEDIUM	Ktype覆盖两门与四门轿车；本行为两门分支。	READY
20120_4dr	20120	Sedan	Jetta I	16	4	EU-VW-JETTA-I-16-SEDAN-01	MEDIUM	Ktype覆盖两门与四门轿车；本行为四门分支。	READY
20159	20159	Sedan	9000 CD		4	EU-SAAB-9000-CD-SEDAN-4D-01	HIGH	CD四门轿车外廓。	READY
20485_l1h1	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	Ktype覆盖L1H1物理分支。	READY
20485_l1h2	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	Ktype覆盖L1H2物理分支。	READY
20485_l2h1	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	Ktype覆盖L2H1物理分支。	READY
20485_l2h2	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	Ktype覆盖L2H2物理分支。	READY
20485_l2h3	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖L2H3物理分支。	READY
20542	20542	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-02	HIGH	A1短轴乘用车身。	READY
20543	20543	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-LWB-01	HIGH	A1长轴乘用车身。	READY
20544	20544	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-01	HIGH	A1短轴乘用车身。	READY
20546	20546	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-01	MEDIUM	A1短轴四驱乘用车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-JETTA-I-16-SEDAN-01	4190	1610	1410	Volkswagen Newsroom Jetta I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-SAAB-9000-CD-SEDAN-4D-01	4790	1780	1420	UltimateSpecs Saab 9000 CD 2.3 Turbo	https://www.ultimatespecs.com/car-specs/Saab/6104/Saab-9000-CD-23-Turbo.html
EU-HYUNDAI-H1-I-A1-MPV-SWB-02	4695	1820	1885	Auto-Data Hyundai H-1 I Starex 2.5 TD 99 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-99hp-13857
EU-HYUNDAI-H1-I-A1-MPV-LWB-01	5035	1820	1965	Auto-Data Hyundai H-1 I Starex 2.5 TD LWB 101 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-lwb-101hp-13859
EU-HYUNDAI-H1-I-A1-MPV-SWB-01	4695	1820	1880	Auto-Data Hyundai H-1 I Starex 2.5 CRDI 140 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-crdi-140hp-13854
```

## 下一步优先处理

1. 闭合 Nissan Sunny `20366` 与 Toyota RAV4 III `20645` 的具体车身及改款边界。
2. 处理 VW Transporter T4 `20486` 和 T5 Bus `20661` 的轴距、车顶及乘用车身分支。
3. 集中处理 Fiat Ducato、Citroën C25、Mitsubishi L200 和 Peugeot Boxer 商用车分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641?utm_source=chatgpt.com "Vehicle data Jetta I profile"
[2]: https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-3.2-v6-235hp-4motion-l1h1-49901 "Volkswagen Transporter (T5) Panel Van 3.2 V6 (235 Hp) 4MOTION L1H1 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 42 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 42 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 2 个 Ktype，新增 3 条 READY 映射。
* `20366` 已确认是 Nissan Sunny N13 四门四驱轿车，外廓为 `4220 × 1640 × 1390 mm`。([Ultimate Specs][1])
* `20645` 的生产区间跨越 RAV4 III XA30 改款，改款前后车长分别为 `4395 mm` 和 `4445 mm`，因此拆成两个物理分支。两者均为五门前驱版本，宽高保持 `1815 × 1685 mm`。([CarSpecsGuru][2])
* 剩余商用车没有强行套用相近缓存：其轴距、车顶或驾驶室分支尚未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射：105
* PENDING Ktype：9
* 当前批次已引用尺寸组：79
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20366	20366	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	MEDIUM	N13四门四驱轿车外廓。	READY
20645_prefl	20645	SUV	RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-5D-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
20645_facelift	20645	SUV	RAV4 III facelift	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-5D-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4220	1640	1390	UltimateSpecs Nissan Sunny N13 1.6 4WD	https://www.ultimatespecs.com/car-specs/Nissan/6796/Nissan-Sunny-N13-16-4WD.html
EU-TOYOTA-RAV4-III-XA30-SUV-5D-PREFL-01	4395	1815	1685	CarSpecsGuru Toyota RAV4 III XA30 2.4 170 HP	https://www.carspecsguru.com/toyota/rav-4/4985/7471/modification-54180
EU-TOYOTA-RAV4-III-XA30-SUV-5D-FACELIFT-01	4445	1815	1685	CarSpecsGuru Toyota RAV4 III XA30 Facelift 2.4 170 HP	https://www.carspecsguru.com/toyota/rav-4/4984/7470/modification-54163
```

## 下一步优先处理

1. 集中闭合 Citroën C25 的 Bus、Van 和 chassis-cab 分支，优先关联已有尺寸组。
2. 处理 Fiat Ducato 230L、Peugeot Boxer 230 和 VW Transporter T4 的轴距、车顶及驾驶室分支。
3. 最后解决 Mitsubishi L200 K64T 与 VW Transporter T5 Bus 的具体车身组合。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Nissan/6796/Nissan-Sunny-N13-16-4WD.html "Nissan Sunny N13 1.6 4WD Specs, Performance, Comparisons"
[2]: https://www.carspecsguru.com/toyota/rav-4/4985/7471/modification-54180 "Toyota RAV4 III (XA30) 2.4 170 HP specifications and technical data | CarSpecsGuru.com"


--- 发送 / 继续到 Round 43 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 43 / checkpoint 续跑 ---
## 更新点

* 本轮新增闭合 3 个 Ktype，新增 10 条 READY 映射。
* `20474` 已确认是 `K64T`、两门、后驱单排驾驶室 L200，首次创建一个尺寸组。([PartSouq][1])
* `20486` 按 T4 平台/底盘车型已确认的 SWB、LWB、单排、双排和成品货斗分支，全部关联已有尺寸组，未重复抓取或建组。([维基百科][2])
* `20661` 的 3.2 V6 4Motion Bus 覆盖标准轴距与长轴 Caravelle 外廓，直接关联已有 T5 MPV 低顶尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射：115
* PENDING Ktype：6
* 当前批次已引用尺寸组：89
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20474	20474	Pickup	L200 III	K64T	2	EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	MEDIUM	K64T后驱单排驾驶室皮卡外廓。	READY
20486_chassis_swb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	MEDIUM	短轴单排底盘驾驶室分支。	READY
20486_chassis_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	MEDIUM	长轴单排底盘驾驶室分支。	READY
20486_doka_lwb	20486	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排底盘驾驶室分支。	READY
20486_pickup_swb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	MEDIUM	短轴单排成品货斗分支。	READY
20486_pickup_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	MEDIUM	长轴单排成品货斗分支。	READY
20486_pickup_doka_lwb	20486	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排成品货斗分支。	READY
20486_lowbed_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	MEDIUM	长轴低货台分支。	READY
20661_swb	20661	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	标准轴距低顶乘用Bus外廓。	READY
20661_lwb	20661	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	长轴低顶乘用Bus外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	5010	1695	1755	VehicleScore Mitsubishi L200 dimensions;PartSouq Mitsubishi L200 K64T parts catalog	https://vehiclescore.co.uk/car-dimensions-check/mitsubishi/l200;https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&vid=0
```

## 下一步优先处理

1. 集中闭合 `20326`、`20628`、`20631`、`20633` 四个 Citroën C25 Ktype，按 Bus、Van、SWB/MWB、LWB 及载重等级批量建组。
2. 处理 `20229` Fiat Ducato 230L 4x4 Van 的轴距和车顶组合。
3. 最后闭合 `20693` Peugeot Boxer ZCT 平台/底盘的 SWB、MWB、LWB 分支。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&srsltid=AfmBOopJ38tJggXECjv3lIlaM5PEyqnrKRnt6G4Uzl227lrC3jMn5HfY&ssd=%24%2AKwFjV0ZCFjElBj4yEiYlVzsvDwgWZ2hlZHZwfzkQLHQ4cm07fWp2fXI0dGtyFG04NVhhEWESc3x1OCo8OBpmYwJzfHU2ZCQgcxUZBR1yKgAAAABqxdek%24&vid=0&utm_source=chatgpt.com "Mitsubishi L200 General (EXPORT) K64T Parts Catalogs"
[2]: https://en.wikipedia.org/wiki/Volkswagen_Transporter_%28T4%29?utm_source=chatgpt.com "Volkswagen Transporter (T4)"
[3]: https://www.auto-data.net/en/volkswagen-caravelle-t5-3.2-v6-235hp-4motion-49250 "Volkswagen Caravelle (T5) 3.2 V6 (235 Hp) 4MOTION | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 44 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 44 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 `20326`。C25 2.5 D Combi/Bus 的标准乘用车外廓确认为 `4765 × 1965 × 2100 mm`，两个规格数据库数据一致。([Autoboom][1])
* 其余 5 个 Ktype 仍涉及发动机版本与轴距、车顶、载重等级或底盘形式的对应边界，未强行套用相近缓存。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射：116
* PENDING Ktype：5
* 当前批次已引用尺寸组：90
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20326	20326	MPV	C25 I		4	EU-CITROEN-C25-I-COMBI-MPV-01	HIGH	2.5 D标准轴距Combi乘用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C25-I-COMBI-MPV-01	4765	1965	2100	Drom Citroën C25 2.5D Combi dimensions;AutoBoom Citroën C25 dimensions	https://www.drom.ru/catalog/citroen/c25/specs/dimensions/;https://autoboom.co.il/en/catalog/cars/citroen/c25
```

## 下一步优先处理

1. 核对 `20628` 的 1.9 D 1400 是否覆盖短轴低顶、加高顶或长轴大容积车身，避免误用 2.5 D 的同名载重版本。
2. 闭合 `20229` Fiat Ducato 230 2.8 TD 4x4 Van 的具体 2.8t 车身尺寸。
3. 最后处理 `20631`、`20633` 和 `20693` 的 chassis-cab、platform-cab、轴距及载重分支。

推进信号：CONTINUE

[1]: https://autoboom.co.il/en/catalog/cars/citroen/c25?srsltid=AfmBOopfJOwShUNlvOEZzK-SbtStGD_cOu2dSsE9b0xopJBqJAjnF4Dd&utm_source=chatgpt.com "Citroen C25 in Israel"


--- 发送 / 继续到 Round 45 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 45 / checkpoint 续跑 ---
## 更新点

* `20631` 已按 C25 I 2.0、78 hp 的 1400 级底盘驾驶室边界，拆分为中轴和长轴两条映射，直接复用现有尺寸组。该版本属于 C25 chassis-cab 1400 系列，不纳入后期 1800 级分支。([Motor Doctor][1])
* `20633` 已按 2.5 DT、95 hp 底盘驾驶室覆盖范围，拆分为 1400 级中轴、1400 级长轴和 1800 级长轴三条映射，全部复用已有尺寸组。([car.info][2])
* 本轮未创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射：121
* PENDING Ktype：3
* 当前批次已引用尺寸组：90
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20631_mwb	20631	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	1400级中轴底盘驾驶室分支。	READY
20631_lwb	20631	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	1400级长轴底盘驾驶室分支。	READY
20633_1400_mwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	1400级中轴涡轮柴油底盘驾驶室分支。	READY
20633_1400_lwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	1400级长轴涡轮柴油底盘驾驶室分支。	READY
20633_1800_lwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	MEDIUM	1800级长轴涡轮柴油底盘驾驶室分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 确认 `20229` Fiat Ducato 230L 2.8 TD 4x4 Van 对应的轴距和车顶组合。
2. 确认 `20628` Citroën C25 1.9 D 1400 Van 是标准车身还是 Grand Volume 分支。
3. 为 `20693` Peugeot Boxer 230 2.0 chassis-cab 补齐可直接追溯的短轴三维来源。

[1]: https://www.motor-doctor.co.uk/citroen/c25/c25-platform-chassis-280-290/20631-2-0?utm_source=chatgpt.com "Parts catalogue Citroen C25 280 2.0 78 HP"
[2]: https://www.car.info/en-dk/citroen/c25/c25-chassi-cab-120196175?utm_source=chatgpt.com "Citroën C25 Chassi Cab 1400"


--- 发送 / 继续到 Round 46 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 46 / checkpoint 续跑 ---
## 更新点

* 本轮闭合 `20693`。瑞士 ASTRA 型式批准 `3PA246` 对应 Peugeot Boxer 230、2.0i 110 hp、双门底盘驾驶室，并明确列出短轴、中轴、长轴三种原厂外廓：`4770 / 5120 / 5600 × 2000 × 2100 mm`。([Typenscheinschweiz.ch][1])
* `20229` 与 `20628` 仍缺少将确切 Ktype 绑定到具体轴距、车顶或容积版本的直接证据，本轮未创建猜测性映射。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：124
* PENDING Ktype：2
* 当前批次已引用尺寸组：93
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20693_swb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	HIGH	230型短轴底盘驾驶室分支。	READY
20693_mwb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	HIGH	230型中轴底盘驾驶室分支。	READY
20693_lwb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	HIGH	230型长轴底盘驾驶室分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	4770	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	5120	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	5600	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
```

## 下一步优先处理

1. 闭合 `20229` Fiat Ducato 230L 2.8 TD 4x4，确认其属于标准低顶、加高顶还是 Maxi 车身。
2. 闭合 `20628` Citroën C25 1.9 D 1400 Van，确认短轴标准厢体与 Grand Volume 分支边界。

推进信号：CONTINUE

[1]: https://typenscheinschweiz.ch/typenschein/auto/3PA246 "Typenschein 3PA246 - PEUGEOT Boxer 2.0i 14Q | Gratis PDF"


--- 发送 / 继续到 Round 47 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 47 / checkpoint 续跑 ---
## 更新点

* 最后两个阻塞 Ktype 已闭合：

  * `20229` 确认为 Fiat Ducato II `230L` 2.8 TD 4x4 厢式车，建立独立四驱高顶长车身尺寸组。([AUTODOC][1])
  * `20628` 确认为 Citroën C25 `Typ 290`、1.9 D 1400 标准厢式车。([car.info][2])
* 已完成一次机械检查：表头固定、126 个 `id` 唯一、100 个输入 Ktype 全覆盖、105 个尺寸组唯一、映射引用全部闭合，尺寸和来源字段均非空。
* 当前批次不存在 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：126
* PENDING：0
* DIMENSION_GROUP：105
* 引用未闭合：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
20119	20119	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	8K5 Avant 改款车身。	READY
20120_2dr	20120	Sedan	Jetta I	16	2	EU-VW-JETTA-I-16-SEDAN-01	MEDIUM	Ktype覆盖两门与四门轿车；本行为两门分支。	READY
20120_4dr	20120	Sedan	Jetta I	16	4	EU-VW-JETTA-I-16-SEDAN-01	MEDIUM	Ktype覆盖两门与四门轿车；本行为四门分支。	READY
20122	20122	Sedan	124	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	HIGH	W124 四门轿车。	READY
20133	20133	Hatchback	Colt IV	CA4A	3	EU-MITSUBISHI-COLT-IV-CA4A-HATCHBACK-3D-01	MEDIUM	CA4A三门掀背外廓。	READY
20136	20136	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-01	HIGH	2.3 CAT 132 hp外廓。	READY
20137	20137	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	HIGH	2.3 E 136 hp外廓。	READY
20138	20138	Sedan	190 W201	W201	4	EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	HIGH	2.6 CAT 160 hp外廓。	READY
20143	20143	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	HIGH	6K2 四门轿车。	READY
20152	20152	Hatchback	XM Y3	Y3	5	EU-CITROEN-XM-Y3-HATCHBACK-5D-01	HIGH	Y3 五门掀背车身。	READY
20159	20159	Sedan	9000 CD		4	EU-SAAB-9000-CD-SEDAN-4D-01	HIGH	CD四门轿车外廓。	READY
20165	20165	Convertible	911 996 facelift	996	2	EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	HIGH	996 Turbo S双门敞篷外廓。	READY
20166_21093	20166	Hatchback	Samara I	21093	5	EU-LADA-SAMARA-I-21093-HATCHBACK-5D-01	MEDIUM	Ktype生产区间覆盖21093与2114两种外廓。	READY
20166_2114	20166	Hatchback	Samara I	2114	5	EU-LADA-SAMARA-I-2114-HATCHBACK-5D-01	MEDIUM	Ktype生产区间覆盖21093与2114两种外廓。	READY
20170	20170	Convertible	911 997	997	2	EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	HIGH	Carrera 4S 宽体敞篷分支。	READY
20195	20195	Convertible	205 I		2	EU-PEUGEOT-205-I-CABRIOLET-01	HIGH	205 Cabriolet 双门车身。	READY
20204_3dr	20204	Hatchback	205 I facelift	20A/C	3	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	1.0版本覆盖三门外廓。	READY
20204_5dr	20204	Hatchback	205 I facelift	20A/C	5	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	1.0版本覆盖五门外廓。	READY
20205_3dr	20205	Hatchback	205 I facelift	20A/C	3	EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	HIGH	XA三门商用衍生外廓。	READY
20209	20209	Sedan	960	964	4	EU-VOLVO-960-964-SEDAN-4D-01	HIGH	964 四门轿车外廓。	READY
20210	20210	Sedan	960	964	4	EU-VOLVO-960-964-SEDAN-4D-01	HIGH	964 四门轿车外廓。	READY
20214	20214	Wagon	960	965	5	EU-VOLVO-960-965-WAGON-5D-01	HIGH	965 五门旅行车外廓。	READY
20229	20229	Van	Ducato II	230L	3	EU-FIAT-DUCATO-II-230L-4X4-VAN-01	MEDIUM	230L四驱高顶长车身外廓。	READY
20232	20232	Sedan	323 III	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
20235	20235	Sedan	323 III	BF	4	EU-MAZDA-323-III-BF-SEDAN-4D-01	HIGH	BF四门轿车外廓。	READY
20266	20266	Van	Fiorino 147	147	3	EU-FIAT-FIORINO-147-VAN-MPV-3D-01	HIGH	147三门厢式乘用衍生外廓。	READY
20280	20280	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-4D-01	HIGH	6B 四门轿车外廓。	READY
20281	20281	Sedan	605	6B	4	EU-PEUGEOT-605-6B-SEDAN-4D-01	HIGH	6B 四门轿车外廓。	READY
20302	20302	Sedan	19 I	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH	Chamade L53 四门轿车。	READY
20317	20317	Sedan	740	744	4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	744 四门轿车外廓。	READY
20319	20319	Sedan	740	744	4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	744 四门轿车外廓。	READY
20326	20326	MPV	C25 I		4	EU-CITROEN-C25-I-COMBI-MPV-01	HIGH	2.5 D标准轴距Combi乘用外廓。	READY
20332	20332	Sedan	Camry VI	XV40	4	EU-TOYOTA-CAMRY-VI-XV40-SEDAN-4D-01	HIGH	XV40 四门轿车。	READY
20348	20348	Sedan	Civic VIII		4	EU-HONDA-CIVIC-VIII-SEDAN-4D-01	HIGH	1.8四门轿车外廓。	READY
20358	20358	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	C32四门轿车外廓。	READY
20361	20361	Sedan	Laurel V	C32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	C32四门轿车外廓。	READY
20366	20366	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	MEDIUM	N13四门四驱轿车外廓。	READY
20403	20403	Wagon	Primera P12	WP12	5	EU-NISSAN-PRIMERA-P12-WAGON-01	HIGH	WP12 五门旅行车。	READY
20415	20415	Coupe	CRX II		3	EU-HONDA-CRX-II-COUPE-3D-01	MEDIUM	CRX II三门车身外廓。	READY
20427	20427	Sedan	Impreza I WRX	GC8	4	EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	HIGH	GC8四门WRX外廓。	READY
20433	20433	SUV	Sportage II	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-01	HIGH	KM 五门 SUV。	READY
20436	20436	Sedan	Biturbo			EU-MASERATI-BITURBO-420-SI-SEDAN-01	MEDIUM	430 四门长轴 Biturbo 外廓。	READY
20440	20440	Hatchback	Civic VI		3	EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	HIGH	三门 Hatchback 分支。	READY
20442	20442	Hatchback	Persona I Compact		3	EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	HIGH	318i三门Compact外廓。	READY
20443	20443	Sedan	Persona I		4	EU-PROTON-PERSONA-I-SEDAN-4D-01	HIGH	416四门轿车外廓。	READY
20447	20447	Coupe	Eclipse IV	DK	2	EU-MITSUBISHI-ECLIPSE-IV-DK-COUPE-2D-01	HIGH	DK 双门 Coupe。	READY
20459	20459	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH	VS 四门轿车。	READY
20460	20460	Coupe	C-Class Sport Coupe CL203	CL203	3	EU-MERCEDES-BENZ-C-CLASS-CL203-SPORT-COUPE-3D-01	MEDIUM	输入版本名称与功率标签不一致；CL203三门外廓已确认。	READY
20469	20469	MPV	Expert I			EU-PEUGEOT-EXPERT-I-BUS-01	HIGH	第一代乘用 Bus 外廓。	READY
20470	20470	MPV	Expert I			EU-PEUGEOT-EXPERT-I-BUS-01	HIGH	第一代乘用 Bus 外廓。	READY
20474	20474	Pickup	L200 III	K64T	2	EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	MEDIUM	K64T后驱单排驾驶室皮卡外廓。	READY
20475	20475	Hatchback	Panda III	319	5	EU-FIAT-PANDA-III-319-HATCHBACK-5D-01	HIGH	319五门前驱车身。	READY
20481	20481	Sedan	Marea 185 facelift	185	4	EU-FIAT-MAREA-185-FACELIFT-SEDAN-4D-01	MEDIUM	185 改款四门轿车外廓。	READY
20485_l1h1	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	MEDIUM	Ktype覆盖L1H1物理分支。	READY
20485_l1h2	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	MEDIUM	Ktype覆盖L1H2物理分支。	READY
20485_l2h1	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	MEDIUM	Ktype覆盖L2H1物理分支。	READY
20485_l2h2	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	MEDIUM	Ktype覆盖L2H2物理分支。	READY
20485_l2h3	20485	Van	Transporter T5			EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	MEDIUM	Ktype覆盖L2H3物理分支。	READY
20486_chassis_swb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	MEDIUM	短轴单排底盘驾驶室分支。	READY
20486_chassis_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	MEDIUM	长轴单排底盘驾驶室分支。	READY
20486_doka_lwb	20486	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排底盘驾驶室分支。	READY
20486_pickup_swb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	MEDIUM	短轴单排成品货斗分支。	READY
20486_pickup_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	MEDIUM	长轴单排成品货斗分支。	READY
20486_pickup_doka_lwb	20486	Pickup	Transporter T4		4	EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排成品货斗分支。	READY
20486_lowbed_lwb	20486	Pickup	Transporter T4		2	EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	MEDIUM	长轴低货台分支。	READY
20498	20498	Sedan	Samara I	21099	4	EU-LADA-SAMARA-I-21099-SEDAN-4D-01	HIGH	21099 四门轿车外廓。	READY
20506	20506	Convertible	911 997	997	2	EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	HIGH	997 Carrera S 后驱敞篷外廓。	READY
20511	20511	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	五门 Fastback 外廓。	READY
20516	20516	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	4.6 GT双门Coupe外廓。	READY
20517	20517	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	HIGH	4.6 Cobra双门Coupe外廓。	READY
20518	20518	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	4.6 GT双门敞篷外廓。	READY
20519	20519	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	HIGH	4.6 Cobra双门敞篷外廓。	READY
20521	20521	SUV	Korando II	KJ	3	EU-SSANGYONG-KORANDO-II-KJ-SUV-3D-01	HIGH	KJ三门SUV外廓。	READY
20542	20542	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-02	HIGH	A1短轴乘用车身。	READY
20543	20543	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-LWB-01	HIGH	A1长轴乘用车身。	READY
20544	20544	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-01	HIGH	A1短轴乘用车身。	READY
20545	20545	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07 五门 SUV。	READY
20546	20546	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-A1-MPV-SWB-01	MEDIUM	A1短轴四驱乘用车身。	READY
20547	20547	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20548	20548	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20549	20549	Coupe	Beretta L	L	2	EU-CHEVROLET-BERETTA-L-COUPE-2D-01	HIGH	L-body 双门 Coupe。	READY
20553	20553	Sedan	Corsica	L	4	EU-CHEVROLET-CORSICA-L-SEDAN-4D-01	MEDIUM	L-body四门轿车外廓。	READY
20556	20556	Wagon	Golf IV Variant	1J5	5	EU-VW-GOLF-IV-VARIANT-1J5-WAGON-5D-01	HIGH	1J5 五门旅行车。	READY
20565_prefl	20565	Sedan	9-5 I	YS3E	4	EU-SAAB-9-5-PREFL-SEDAN-4D-01	MEDIUM	Ktype生产区间覆盖改款前车身。	READY
20565_facelift2001	20565	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	MEDIUM	Ktype生产区间覆盖2001改款车身。	READY
20565_facelift2005	20565	Sedan	9-5 I facelift 2005	YS3E	4	EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	MEDIUM	Ktype生产区间覆盖2005改款车身。	READY
20566	20566	Sedan	9-5 I	YS3E	4	EU-SAAB-9-5-PREFL-SEDAN-4D-01	HIGH	改款前四门轿车外廓。	READY
20567	20567	Sedan	9-5 I facelift 2001	YS3E	4	EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	MEDIUM	2001改款四门轿车外廓。	READY
20569_3dr	20569	Hatchback	Palio I	178	3	EU-FIAT-PALIO-I-178-HATCHBACK-02	MEDIUM	同一Ktype覆盖三门外廓。	READY
20569_5dr	20569	Hatchback	Palio I	178	5	EU-FIAT-PALIO-I-178-HATCHBACK-02	MEDIUM	同一Ktype覆盖五门外廓。	READY
20576	20576	Wagon	Palio Weekend	178	5	EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	MEDIUM	80 hp五门Weekend外廓。	READY
20581	20581	Wagon	Palio Weekend	178	5	EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	HIGH	1.9 JTD五门Weekend外廓。	READY
20586	20586	Hatchback	Nubira II	J150	5	EU-DAEWOO-NUBIRA-J150-HATCHBACK-5D-01	HIGH	J150五门掀背外廓。	READY
20618	20618	MPV	Voyager II	AS	3	EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	MEDIUM	AS短轴乘用MPV外廓。	READY
20620_prefl	20620	Sedan	Park Avenue I	G	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	MEDIUM	生产区间跨外廓改款，拆分改款前。	READY
20620_facelift	20620	Sedan	Park Avenue I	G	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	MEDIUM	生产区间跨外廓改款，拆分改款后。	READY
20623	20623	Hatchback	Atos Prime	MX	5	EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	HIGH	MX 五门车身。	READY
20628	20628	Van	C25 I	290	3	EU-CITROEN-C25-I-TYP290-VAN-1400-01	MEDIUM	1.9 D 1400 Typ 290标准厢式车身。	READY
20631_mwb	20631	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	1400级中轴底盘驾驶室分支。	READY
20631_lwb	20631	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	1400级长轴底盘驾驶室分支。	READY
20633_1400_mwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	MEDIUM	1400级中轴涡轮柴油底盘驾驶室分支。	READY
20633_1400_lwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	MEDIUM	1400级长轴涡轮柴油底盘驾驶室分支。	READY
20633_1800_lwb	20633	Pickup	C25 I		2	EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	MEDIUM	1800级长轴涡轮柴油底盘驾驶室分支。	READY
20634	20634	Hatchback	Sirion II	M3	5	EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	MEDIUM	M3 五门外廓。	READY
20635_3dr	20635	Hatchback	9-3 I	YS3D	3	EU-SAAB-9-3-I-YS3D-HATCHBACK-01	HIGH	2.3T版本覆盖三门掀背外廓。	READY
20635_5dr	20635	Hatchback	9-3 I	YS3D	5	EU-SAAB-9-3-I-YS3D-HATCHBACK-01	HIGH	2.3T版本覆盖五门掀背外廓。	READY
20636_prefl	20636	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	MEDIUM	生产区间跨改款，拆分改款前敞篷车身。	READY
20636_facelift	20636	Convertible	9-3 II	YS3F	2	EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	MEDIUM	生产区间跨改款，拆分改款后敞篷车身。	READY
20637	20637	Convertible	9-3 I	YS3D	2	EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	HIGH	YS3D 双门敞篷外廓。	READY
20640	20640	Convertible	CLK II	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	HIGH	A209 改款敞篷车身。	READY
20643	20643	SUV	Pathfinder III	R51	5	EU-NISSAN-PATHFINDER-III-R51-SUV-01	HIGH	R51 五门 SUV。	READY
20645_prefl	20645	SUV	RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-5D-PREFL-01	HIGH	Ktype生产区间覆盖改款前外廓。	READY
20645_facelift	20645	SUV	RAV4 III facelift	XA30	5	EU-TOYOTA-RAV4-III-XA30-SUV-5D-FACELIFT-01	HIGH	Ktype生产区间覆盖改款后外廓。	READY
20646	20646	Wagon	9-5 I facelift 2005	YS3E	5	EU-SAAB-9-5-FACELIFT-2005-WAGON-01	HIGH	2005 改款五门旅行车。	READY
20647	20647	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-PREFL-WAGON-5D-01	HIGH	改款前五门旅行车外廓。	READY
20649	20649	Coupe	Esprit S4		2	EU-LOTUS-ESPRIT-S4-GT3-COUPE-2D-01	HIGH	GT3 双门 Coupe 外廓。	READY
20654	20654	Sedan	323 S VI facelift	BJ	4	EU-MAZDA-323-S-VI-BJ-FACELIFT-SEDAN-4D-01	HIGH	BJ 改款四门轿车外廓。	READY
20659	20659	Sedan	Vento	1HX0	4	EU-VW-VENTO-1HX0-SEDAN-4D-01	HIGH	1HX0 四门轿车外廓。	READY
20661_swb	20661	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	HIGH	标准轴距低顶乘用Bus外廓。	READY
20661_lwb	20661	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	HIGH	长轴低顶乘用Bus外廓。	READY
20663	20663	Sedan	Accord VI		4	EU-HONDA-ACCORD-VI-SEDAN-4D-01	HIGH	欧洲版 Accord VI 四门轿车外廓。	READY
20673	20673	SUV	Patrol V	Y61	5	EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	HIGH	Y61改款前五门4.8外廓。	READY
20683	20683	Coupe	3 Series E92 facelift	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	E92 改款双门 Coupe。	READY
20693_swb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	HIGH	230型短轴底盘驾驶室分支。	READY
20693_mwb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	HIGH	230型中轴底盘驾驶室分支。	READY
20693_lwb	20693	Pickup	Boxer I	230	2	EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	HIGH	230型长轴底盘驾驶室分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_901-1000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 facelift 3.0 TDI quattro	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-3.0-tdi-v6-clean-diesel-245hp-quattro-s-tronic-18913
EU-VW-JETTA-I-16-SEDAN-01	4190	1610	1410	Volkswagen Newsroom Jetta I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	4740	1740	1428	Auto-Data Mercedes-Benz W124 facelift 200	https://www.auto-data.net/en/mercedes-benz-w124-facelift-1989-200-105hp-43325
EU-MITSUBISHI-COLT-IV-CA4A-HATCHBACK-3D-01	3955	1690	1370	Auto-Data Mitsubishi Colt IV CAO generation	https://www.auto-data.net/en/mitsubishi-colt-iv-cao-generation-3469
EU-MERCEDES-BENZ-190-W201-SEDAN-4D-01	4420	1678	1390	Auto-Data Mercedes-Benz 190 W201 E 2.3 CAT 132 Hp	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-cat-132hp-12808
EU-MERCEDES-BENZ-190-W201-SEDAN-4D-02	4450	1690	1375	Auto-Data Mercedes-Benz 190 W201 E 2.3 136 Hp;Auto-Data Mercedes-Benz 190 W201 E 2.6 CAT 160 Hp	https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.3-136hp-12801;https://www.auto-data.net/en/mercedes-benz-190-w201-e-2.6-cat-160hp-12806
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4142	1640	1408	Automobile-Catalog 1997 Seat Cordoba 1.4	https://www.automobile-catalog.com/car/1997/3065810/seat_cordoba_1_4.html
EU-CITROEN-XM-Y3-HATCHBACK-5D-01	4709	1793	1385	Auto-Data Citroën XM Y3 generation	https://www.auto-data.net/en/citroen-xm-y3-generation-3319
EU-SAAB-9000-CD-SEDAN-4D-01	4790	1780	1420	UltimateSpecs Saab 9000 CD 2.3 Turbo	https://www.ultimatespecs.com/car-specs/Saab/6104/Saab-9000-CD-23-Turbo.html
EU-PORSCHE-911-996-TURBO-S-CONVERTIBLE-2D-01	4435	1830	1295	Automobile-Catalog 2005 Porsche 911 Turbo S Cabrio	https://www.automobile-catalog.com/car/2005/2867225/porsche_911_turbo_s_cabrio.html
EU-LADA-SAMARA-I-21093-HATCHBACK-5D-01	4006	1650	1402	Auto-Data Lada 21093 1.5 72 Hp	https://www.auto-data.net/en/lada-21093-1.5-72hp-13271
EU-LADA-SAMARA-I-2114-HATCHBACK-5D-01	4122	1620	1415	Auto-Data Lada 2114 1.6 i 8V 81 Hp	https://www.auto-data.net/en/lada-2114-1.6-i-8v-81hp-13273
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300	Auto-Data Porsche 911 Cabriolet 997 Carrera 4S	https://www.auto-data.net/en/porsche-911-cabriolet-997-carrera-4s-3.8-355hp-36747
EU-PEUGEOT-205-I-CABRIOLET-01	3705	1590	1375	Auto-Data Peugeot 205 I Cabrio generation	https://www.auto-data.net/en/peugeot-205-i-cabrio-741b-20d-generation-1276
EU-PEUGEOT-205-I-FACELIFT-HATCHBACK-01	3705	1560	1375	Auto-Data Peugeot 205 I facelift 1.0	https://www.auto-data.net/en/peugeot-205-i-20a-c-facelift-1987-1.0-i-50hp-5639
EU-VOLVO-960-964-SEDAN-4D-01	4871	1750	1411	Auto-Data Volvo 960 (964) 2.0 i 16V	https://www.auto-data.net/en/volvo-960-964-2.0-i-16v-190hp-9355
EU-VOLVO-960-965-WAGON-5D-01	4850	1750	1434	Auto-Data Volvo 960 Kombi (965) 3.0 i 24V	https://www.auto-data.net/en/volvo-960-kombi-965-3.0-i-24v-204hp-9362
EU-FIAT-DUCATO-II-230L-4X4-VAN-01	5505	1998	2490	AutoDoc Fiat Ducato 230L 2.8 TD 4x4 vehicle boundary;Autogidas Fiat Ducato II Maxi specifications;TruckScout24 Fiat Ducato 230L 4x4 measured dimensions	https://www.autodoc.co.uk/car-parts/filter-set-13001/fiat/ducato/ducato-box-230l/20229-2-8-td-4x4;https://autogidas.lt/en/auto-katalogas/fiat/ducato/ii-maxi-232.620.1-1998-2002-k37953;https://www.truckscout24.com/tsp/ts-202-36-595
EU-MAZDA-323-III-BF-SEDAN-4D-01	4195	1645	1390	Automobile-Catalog 1986 Mazda 323 1.6 LX Sedan catalyst	https://www.automobile-catalog.com/car/1986/1630280/mazda_323_1_6_lx_sedan_cat.html
EU-FIAT-FIORINO-147-VAN-MPV-3D-01	4159	1622	1904	Auto-Data Fiat Fiorino 147 1.7 Diesel 63 Hp	https://www.auto-data.net/en/fiat-fiorino-147-1.7-diesel-63hp-6964
EU-PEUGEOT-605-6B-SEDAN-4D-01	4765	1799	1415	Auto-Data Peugeot 605 (6B) 3.0	https://www.auto-data.net/en/peugeot-605-6b-3.0-167hp-5332
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412	Auto-Data Renault 19 I Chamade L53 generation	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-VOLVO-740-SEDAN-PREFL-01	4785	1760	1430	Auto-Data Volvo 740 model	https://www.auto-data.net/en/volvo-740-model-930
EU-CITROEN-C25-I-COMBI-MPV-01	4765	1965	2100	Drom Citroën C25 2.5D Combi dimensions;AutoBoom Citroën C25 dimensions	https://www.drom.ru/catalog/citroen/c25/specs/dimensions/;https://autoboom.co.il/en/catalog/cars/citroen/c25
EU-TOYOTA-CAMRY-VI-XV40-SEDAN-4D-01	4805	1820	1460	Auto-Data Toyota Camry VI (XV40) 2.4i 158 hp	https://www.auto-data.net/en/toyota-camry-vi-xv40-2.4i-16v-158hp-31250
EU-HONDA-CIVIC-VIII-SEDAN-4D-01	4545	1750	1435	Auto-Data Honda Civic VIII Sedan 1.8i 16V 140 Hp	https://www.auto-data.net/en/honda-civic-viii-sedan-1.8i-16v-140hp-12215
EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	4650	1690	1415	Nissan Heritage Collection Laurel C32 Sedan Grand Extra	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/laurel_sedan_grand_extra.html
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4220	1640	1390	UltimateSpecs Nissan Sunny N13 1.6 4WD	https://www.ultimatespecs.com/car-specs/Nissan/6796/Nissan-Sunny-N13-16-4WD.html
EU-NISSAN-PRIMERA-P12-WAGON-01	4675	1760	1480	Auto-Data Nissan Primera Wagon P12 1.6	https://www.auto-data.net/en/nissan-primera-wagon-p12-1.6-i-16v-109hp-606
EU-HONDA-CRX-II-COUPE-3D-01	3755	1675	1270	Auto-Data Honda CRX II ED EE 1.6 i 16V 124 Hp	https://www.auto-data.net/en/honda-crx-ii-ed-ee-1.6-i-16v-124hp-12375
EU-SUBARU-IMPREZA-I-GC8-WRX-SEDAN-4D-01	4340	1690	1405	Automobile-Catalog 1996 Subaru Impreza WRX 280 PS	https://www.automobile-catalog.com/car/1996/3239645/subaru_impreza_wrx.html
EU-KIA-SPORTAGE-II-KM-SUV-01	4350	1840	1730	Auto-Data Kia Sportage II 2.0 CRDi	https://www.auto-data.net/en/kia-sportage-ii-2.0-crdi-113hp-4wd-2719
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360	Auto-Data Maserati Biturbo generation	https://www.auto-data.net/en/maserati-biturbo-generation-2233
EU-HONDA-CIVIC-VI-HATCHBACK-3D-01	4190	1695	1375	Auto-Data Honda Civic VI Hatchback generation	https://www.auto-data.net/en/honda-civic-vi-hatchback-generation-2630
EU-PROTON-PERSONA-I-COMPACT-HATCHBACK-3D-01	3995	1710	1365	Auto-Data Proton Persona I Compact 1.8 318i 135 Hp	https://www.auto-data.net/en/proton-persona-i-compact-1.8-i-16v-318-i-135hp-8236
EU-PROTON-PERSONA-I-SEDAN-4D-01	4360	1680	1385	Auto-Data Proton Persona I 1.6 i 416 GLXi 95 Hp	https://www.auto-data.net/en/proton-persona-i-1.6-i-416-glxi-95hp-8257
EU-MITSUBISHI-ECLIPSE-IV-DK-COUPE-2D-01	4565	1835	1358	Automobile-Catalog 2006 Mitsubishi Eclipse GS	https://www.automobile-catalog.com/car/2006/2007470/mitsubishi_eclipse_gs.html
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Auto-Data Volvo S40 (VS) generation	https://www.auto-data.net/en/volvo-s40-vs-generation-1972
EU-MERCEDES-BENZ-C-CLASS-CL203-SPORT-COUPE-3D-01	4343	1728	1406	Auto-Data Mercedes-Benz C-class Sport Coupe CL203 C 200 Kompressor 163 Hp;Auto-Data Mercedes-Benz C-class Sport Coupe CL203 facelift 2004 C 200 Kompressor 163 Hp	https://www.auto-data.net/en/mercedes-benz-c-class-sport-coupe-cl203-c-200-kompressor-163hp-12591;https://www.auto-data.net/en/mercedes-benz-c-class-sport-coupe-cl203-facelift-2004-c-200-kompressor-163hp-44250
EU-PEUGEOT-EXPERT-I-BUS-01	4440	1810	1940	Auto.ru Peugeot Expert I specifications	https://auto.ru/catalog/cars/peugeot/expert/specifications/
EU-MITSUBISHI-L200-III-K64T-SINGLE-CAB-PICKUP-01	5010	1695	1755	VehicleScore Mitsubishi L200 dimensions;PartSouq Mitsubishi L200 K64T parts catalog	https://vehiclescore.co.uk/car-dimensions-check/mitsubishi/l200;https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&q=&vid=0
EU-FIAT-PANDA-III-319-HATCHBACK-5D-01	3653	1643	1551	Auto-Data Fiat Panda III 319 0.9 TwinAir Turbo 85 Hp	https://www.auto-data.net/en/fiat-panda-iii-319-0.9-twin-air-turbo-85hp-start-stop-18364
EU-FIAT-MAREA-185-FACELIFT-SEDAN-4D-01	4393	1740	1420	Auto-Data Fiat Marea (185) 1.8 i 16V	https://www.auto-data.net/en/fiat-marea-185-1.8-i-16v-132hp-7196
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-SWB-01	4736	1840	1920	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-CHASSIS-CAB-LWB-01	5136	1840	1920	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-CHASSIS-DOUBLE-CAB-LWB-01	5136	1840	1910	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-PICKUP-SWB-01	4871	1970	1910	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-PICKUP-LWB-01	5271	1970	1910	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-PICKUP-DOUBLE-CAB-LWB-01	5271	1970	1910	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-VW-TRANSPORTER-T4-LOWBED-PICKUP-LWB-01	5271	1970	1910	Volkswagen Transporter T4 workshop manual	https://www.manualslib.com/manual/807945/Volkswagen-Transporter-T4-2007.html
EU-LADA-SAMARA-I-21099-SEDAN-4D-01	4205	1650	1402	Auto-Data Lada 21099-20 generation	https://www.auto-data.net/en/lada-21099-20-generation-2832
EU-PORSCHE-911-997-CARRERA-S-CONVERTIBLE-01	4427	1808	1300	Auto-Data Porsche 911 Cabriolet (997) Carrera S 3.8	https://www.auto-data.net/en/porsche-911-cabriolet-997-carrera-s-3.8-355hp-6588
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Auto-Data Honda Civic VI Fastback	https://www.auto-data.net/en/honda-civic-model-1307
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359	Auto-Data Ford Mustang IV generation	https://www.auto-data.net/en/ford-mustang-iv-generation-1716
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350	Auto-Data Ford Mustang IV Convertible generation	https://www.auto-data.net/en/ford-mustang-iv-convertible-generation-1715
EU-SSANGYONG-KORANDO-II-KJ-SUV-3D-01	4260	1841	1840	Auto-Data SsangYong Korando II KJ 2.3 TD 101 Hp	https://www.auto-data.net/en/ssangyong-korando-ii-kj-2.3-td-101hp-15995
EU-HYUNDAI-H1-I-A1-MPV-SWB-02	4695	1820	1885	Auto-Data Hyundai H-1 I Starex 2.5 TD 99 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-99hp-13857
EU-HYUNDAI-H1-I-A1-MPV-LWB-01	5035	1820	1965	Auto-Data Hyundai H-1 I Starex 2.5 TD LWB 101 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-td-lwb-101hp-13859
EU-HYUNDAI-H1-I-A1-MPV-SWB-01	4695	1820	1880	Auto-Data Hyundai H-1 I Starex 2.5 CRDI 140 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.5-crdi-140hp-13854
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704	Auto-Data Opel Antara 2.4 ECOTEC 4x4	https://www.auto-data.net/en/opel-antara-2.4-ecotec-140hp-4x4-1826
EU-CHEVROLET-BERETTA-L-COUPE-2D-01	4757	1735	1346	Auto-Data Chevrolet Beretta 3.1 i V6	https://www.auto-data.net/en/chevrolet-beretta-3.1-i-v6-162hp-14462
EU-CHEVROLET-CORSICA-L-SEDAN-4D-01	4660	1727	1371	Auto-Data Chevrolet Corsica 3.1 i V6 162 Hp	https://www.auto-data.net/en/chevrolet-corsica-3.1-i-v6-162hp-14493
EU-VW-GOLF-IV-VARIANT-1J5-WAGON-5D-01	4397	1735	1485	Volkswagen Newsroom Golf IV Variant vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-variant-profile-19523
EU-SAAB-9-5-PREFL-SEDAN-4D-01	4810	1790	1450	Auto-Data Saab 9-5 2.0 T 16V 185 Hp	https://www.auto-data.net/en/saab-9-5-2.0-t-16v-185hp-11844
EU-SAAB-9-5-FACELIFT-2001-SEDAN-4D-01	4827	1792	1475	Auto-Data Saab 9-5 facelift 2001 generation	https://www.auto-data.net/en/saab-9-5-facelift-2001-generation-7159
EU-SAAB-9-5-FACELIFT-2005-SEDAN-01	4836	1792	1448	Auto-Data Saab 9-5 facelift 2005 generation	https://www.auto-data.net/en/saab-9-5-facelift-2005-generation-8066
EU-FIAT-PALIO-I-178-HATCHBACK-02	3735	1626	1446	Auto-Data Fiat Palio 178 1.2 i 68 Hp	https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854
EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	4130	1626	1475	Auto-Data Fiat Palio Weekend 178 1.2 16V 80 Hp	https://www.auto-data.net/en/fiat-palio-weekend-178-1.2-16v-80hp-6839
EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	4130	1626	1515	Auto-Data Fiat Palio Weekend 178 1.9 JTD 80 Hp	https://www.auto-data.net/en/fiat-palio-weekend-178-1.9-jtd-80hp-6849
EU-DAEWOO-NUBIRA-J150-HATCHBACK-5D-01	4280	1700	1430	Auto-Data Daewoo Nubira Hatchback II 2.0 CDX 126 Hp	https://www.auto-data.net/en/daewoo-nubira-hatchback-ii-2.0-i-16v-cdx-126hp-16329
EU-CHRYSLER-VOYAGER-II-AS-MPV-SWB-01	4525	1830	1707	Auto-Data Chrysler Voyager II	https://www.auto-data.net/en/chrysler-voyager-ii-generation-8878
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400	Automobile-Catalog 1991 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1991/321530/buick_park_avenue_ultra.html
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400	Automobile-Catalog 1995 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1995/322025/buick_park_avenue_ultra.html
EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	3495	1485	1580	Auto-Data Hyundai Atos Prime 1.1	https://www.auto-data.net/en/hyundai-atos-prime-1.1-i-12v-59hp-automatic-24813
EU-CITROEN-C25-I-TYP290-VAN-1400-01	4765	1965	2100	Car.info Citroën C25 Van 1400 Typ 290;AutoBoom Citroën C25 dimensions	https://www.car.info/en-se/citroen/c25/c25-van-1400-typ-290-120201016;https://autoboom.co.il/en/catalog/cars/citroen/c25
EU-CITROEN-C25-I-CHASSIS-CAB-SWB-MWB-01	4989	1965	2108	Zoomcar Citroën C25 chassis cab 1400 medium	https://zoomcar.fr/fiche-technique-utilitaire/citroen/c25-chassis-cabine-c25-chassis-cab-1400-tbo-d-moyen-NAT57338.html
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1400-01	5442	1965	2108	Drom Citroën C25 2.5D Long	https://www.drom.ru/catalog/lcv/citroen/c25/290063/
EU-CITROEN-C25-I-CHASSIS-CAB-LWB-1800-01	5442	1965	2080	Zoomcar Citroën C25 chassis cab 1800 turbo diesel long	https://zoomcar.fr/fiche-technique-utilitaire/citroen/c25-chassis-cabine-c25-chassis-cab-1800-tbo-d-long-NAT56156.html
EU-DAIHATSU-SIRION-II-M3-FACELIFT-HATCHBACK-5D-01	3605	1665	1550	ADAC Daihatsu Sirion II facelift	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/daihatsu/sirion/2generation-facelift/211704/
EU-SAAB-9-3-I-YS3D-HATCHBACK-01	4629	1711	1428	Auto-Data Saab 9-3 I 2.3 T 230 Hp	https://www.auto-data.net/en/saab-9-3-i-2.3-t-230hp-11965
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data Saab 9-3 Convertible II	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.0-t-150hp-11947
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437	Auto-Data Saab 9-3 Convertible II facelift	https://www.auto-data.net/en/saab-9-3-convertible-ii-facelift-2007-2.8t-v6-280hp-54601
EU-SAAB-9-3-I-YS3D-CONVERTIBLE-2D-01	4629	1711	1423	Auto-Data Saab 9-3 Convertible I 2.0 T	https://www.auto-data.net/en/saab-9-3-convertible-i-2.0-t-205hp-11967
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413	Auto-Data Mercedes-Benz CLK A209 facelift	https://www.auto-data.net/en/mercedes-benz-clk-a209-facelift-2005-clk-280-231hp-23477
EU-NISSAN-PATHFINDER-III-R51-SUV-01	4740	1850	1865	Automobile-Catalog 2005 Nissan Pathfinder 2.5 dCi	https://www.automobile-catalog.com/car/2005/2313500/nissan_pathfinder_2_5_dci.html
EU-TOYOTA-RAV4-III-XA30-SUV-5D-PREFL-01	4395	1815	1685	CarSpecsGuru Toyota RAV4 III XA30 2.4 170 HP	https://www.carspecsguru.com/toyota/rav-4/4985/7471/modification-54180
EU-TOYOTA-RAV4-III-XA30-SUV-5D-FACELIFT-01	4445	1815	1685	CarSpecsGuru Toyota RAV4 III XA30 Facelift 2.4 170 HP	https://www.carspecsguru.com/toyota/rav-4/4984/7470/modification-54163
EU-SAAB-9-5-FACELIFT-2005-WAGON-01	4841	1792	1459	Auto-Data Saab 9-5 Sport Combi facelift 2005 generation	https://www.auto-data.net/en/saab-9-5-sport-combi-facelift-2005-generation-8067
EU-SAAB-9-5-PREFL-WAGON-5D-01	4808	1792	1497	Auto-Data Saab 9-5 Sport Combi generation	https://www.auto-data.net/en/saab-9-5-sport-combi-generation-2532
EU-LOTUS-ESPRIT-S4-GT3-COUPE-2D-01	4369	1883	1150	Auto-Data Lotus Esprit 2.0 i 16V Turbo GT3	https://www.auto-data.net/en/lotus-esprit-2.0-i-16v-turbo-gt3-243hp-8298
EU-MAZDA-323-S-VI-BJ-FACELIFT-SEDAN-4D-01	4390	1705	1410	Auto-Data Mazda 323 S VI (BJ) 2.0 DiTD	https://www.auto-data.net/en/mazda-323-s-vi-bj-2.0-ditd-101hp-11150
EU-VW-VENTO-1HX0-SEDAN-4D-01	4380	1695	1415	Auto-Data Volkswagen Vento (1HX0) 2.0	https://www.auto-data.net/en/volkswagen-vento-1hx0-2.0-115hp-8851
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959	Volkswagen Transporter T5.II specifications	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-HONDA-ACCORD-VI-SEDAN-4D-01	4595	1750	1430	Auto-Data Honda Accord VI	https://www.auto-data.net/en/honda-accord-model-1282
EU-NISSAN-PATROL-V-Y61-SUV-5D-PREFL-01	5010	1930	1855	Auto-Data Nissan Patrol V 5-door Y61	https://www.auto-data.net/en/nissan-patrol-v-5-door-y61-generation-83
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375	Auto-Data BMW 3 Series Coupe E92 LCI 330i	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-330i-272hp-17228
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	4770	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	5120	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	5600	2000	2100	Swiss ASTRA type approval 3PA246	https://typenscheinschweiz.ch/typenschein/auto/3PA246
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_901-1000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.co.uk/car-parts/filter-set-13001/fiat/ducato/ducato-box-230l/20229-2-8-td-4x4?utm_source=chatgpt.com "Fiat Ducato 230L 2.8 TD 4x4 Service kit (122 hp 8140.43)"
[2]: https://www.car.info/en-se/citroen/c25/c25-van-1400-typ-290-120201016?utm_source=chatgpt.com "Citroën C25 Van 1400 Typ 290 1991 - 1994"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5285 行）
- 累计尺寸组：dimension_groups_final.tsv（2302 行）

