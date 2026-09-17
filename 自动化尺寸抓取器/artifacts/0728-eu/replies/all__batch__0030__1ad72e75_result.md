# 任务：all 第 2901-3000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0030__1ad72e75


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2901-3000 行

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
all 第 2901-3000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Porsche	928	4.5	Coupe	Heckantrieb	Benzin	177	241	Sep 1977	Aug 1982	2024-03-01	2990
Porsche	928	4.7 S	Coupe	Heckantrieb	Benzin	221	301	Sep 1979	Jul 1983	2024-03-01	2991
Porsche	928	4.7 S	Coupe	Heckantrieb	Benzin	228	310	Aug 1983	Jul 1986	2024-03-01	2992
Porsche	928	5.0 S, S4	Coupe	Heckantrieb	Benzin	235	320	Aug 1986	Jul 1991	2024-03-01	2993
Porsche	928	5.0 S4 CAT	Coupe	Heckantrieb	Benzin	235	320	Aug 1986	Jul 1991	2024-03-01	2994
Porsche	928	5.0 GT	Coupe	Heckantrieb	Benzin	243	330	Jan 1989	Jul 1991	2024-03-01	2995
Porsche	928	5.4 GTS	Coupe	Heckantrieb	Benzin	257	350	Aug 1991	Nov 1995	2024-03-01	2996
Porsche	911	3.3 Turbo	Coupe	Heckantrieb	Benzin	235	320	Aug 1990	Sep 1993	2024-03-01	2997
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	184	250	Dec 1988	Sep 1993	2024-03-01	2998
Porsche	911	3.6 Carrera RS	Coupe	Heckantrieb	Benzin	191	260	Jun 1991	Sep 1993	2024-03-01	2999
Porsche	968	3	Coupe	Heckantrieb	Benzin	176	239	Jun 1991	Nov 1995	2024-03-01	3000
Porsche	968	3	Cabriolet	Heckantrieb	Benzin	176	239	Jun 1991	Nov 1995	2024-03-01	3001
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	200	272	Oct 1993	Aug 1995	2024-03-01	3002
Saab	900 i	2.0 I	Stufenheck	Frontantrieb	Benzin	81	110	Sep 1980	Aug 1990	2026-01-01	3003
Saab	900 i	2.0 I	Stufenheck	Frontantrieb	Benzin	85	115	Nov 1980	Aug 1990	2024-03-01	3004
Saab	900 i	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	107	146	Oct 1980	Jul 1985	2024-03-01	3005
Saab	900 i	2.0 Turbo-16	Cabriolet	Frontantrieb	Benzin	118	160	Nov 1986	Jun 1994	2024-03-01	3006
Saab	900 i	2.0 S Turbo-16	Cabriolet	Frontantrieb	Benzin	104	141	Sep 1991	Jun 1994	2024-03-01	3007
Saab	9000	2.0 -16 Turbo	Stufenheck	Frontantrieb	Benzin	118	160	May 1988	Aug 1993	2024-03-01	3008
Saab	9000	2.0 -16 CD	Stufenheck	Frontantrieb	Benzin	96	131	Sep 1993	Dec 1998	2024-03-01	3009
Saab	9000	2.0 -16 Turbo CD	Stufenheck	Frontantrieb	Benzin	108	147	Sep 1992	Dec 1998	2024-03-01	3010
Saab	9000	2.0 -16 CD	Stufenheck	Frontantrieb	Benzin	110	150	Sep 1993	Dec 1998	2024-03-01	3011
Saab	9000	2.0 -16 Turbo CD	Stufenheck	Frontantrieb	Benzin	120	163	Sep 1988	Aug 1993	2024-03-01	3012
Saab	9000	2.0 -16 Turbo CD	Stufenheck	Frontantrieb	Benzin	136	185	Sep 1989	Dec 1998	2024-03-01	3013
Saab	9000	2.3 -16 CD	Stufenheck	Frontantrieb	Benzin	107	146	Aug 1989	Dec 1998	2024-03-01	3014
Saab	9000	2.3 -16 CDE	Stufenheck	Frontantrieb	Benzin	108	147	Sep 1993	Dec 1998	2024-03-01	3015
Saab	9000	2.3 -16 CDE Eco-power	Stufenheck	Frontantrieb	Benzin	125	170	Sep 1993	Dec 1998	2024-03-01	3016
Saab	9000	2.3 -16 Turbo	Stufenheck	Frontantrieb	Benzin	143	195	Sep 1990	Dec 1998	2024-03-01	3017
Saab	9000	2.3 -16 CD Turbo	Stufenheck	Frontantrieb	Benzin	147	200	Jul 1990	Dec 1998	2024-03-01	3018
Porsche	911	3.2 Carrera Speedster	Cabriolet	Heckantrieb	Benzin	170	231	Aug 1986	Aug 1989	2024-03-01	3019
Skoda	Rapid	1.3	Coupe	Heckantrieb	Benzin	45	61	Mar 1985	Aug 1988	2024-03-01	3020
Skoda	100	1	Stufenheck	Heckantrieb	Benzin	31	42	Jan 1970	Dec 1977	2024-03-01	3021
Skoda	100	1	Stufenheck	Heckantrieb	Benzin	29	39	Jan 1970	Dec 1977	2024-03-01	3022
Skoda	105,120	1.0 105 S, L, GL	Stufenheck	Heckantrieb	Benzin	33	45	Aug 1976	Aug 1983	2024-03-01	3023
Skoda	105,120	1.0 105 S, L	Stufenheck	Heckantrieb	Benzin	34	46	Aug 1976	Dec 1990	2024-03-01	3024
Skoda	105,120	1.2 120 L	Stufenheck	Heckantrieb	Benzin	38	52	Aug 1976	Dec 1990	2024-03-01	3025
Skoda	105,120	1.2 120 LS	Stufenheck	Heckantrieb	Benzin	43	58	Aug 1976	Dec 1990	2024-03-01	3026
Skoda	105,120	1.0 105 S, L	Stufenheck	Heckantrieb	Benzin	32	44	Feb 1988	Dec 1990	2024-03-01	3027
Skoda	105,120	1.0 105 S, L, LS	Stufenheck	Heckantrieb	Benzin	33	45	Oct 1983	Dec 1990	2024-03-01	3028
Skoda	105,120	1.2 120 L	Stufenheck	Heckantrieb	Benzin	38	52	Oct 1983	Dec 1990	2024-03-01	3029
Skoda	Favorit	1.3 135l	Schrägheck	Frontantrieb	Benzin	43	58	May 1989	Sep 1994	2024-03-01	3030
Skoda	Favorit	1.3 135	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1990	Sep 1994	2024-03-01	3031
Skoda	Favorit	1.3 136	Schrägheck	Frontantrieb	Benzin	45	61	Oct 1990	Sep 1994	2024-03-01	3032
Skoda	Favorit	1.3 135	Schrägheck	Frontantrieb	Benzin	42	57	Dec 1991	Sep 1994	2024-03-01	3033
Skoda	Favorit	1.3 135	Schrägheck	Frontantrieb	Benzin	43	58	Dec 1991	Sep 1994	2024-03-01	3034
Skoda	Favorit	1.3 135 X, LX, GLX	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1990	Sep 1994	2024-03-01	3035
Skoda	Favorit	1.3	Kombi	Frontantrieb	Benzin	44	60	Dec 1991	Jun 1995	2024-03-01	3036
Skoda	Favorit	1.3	Kombi	Frontantrieb	Benzin	45	61	Aug 1991	Jun 1995	2024-03-01	3037
Skoda	Favorit	1.3	Kombi	Frontantrieb	Benzin	40	54	Sep 1991	Jun 1995	2024-03-01	3038
Citroën	Ax	14 4X4	Schrägheck	Allrad	Benzin	55	75	Aug 1991	Dec 1996	2024-03-01	3039
Mini	Mini	ONE D	Schrägheck	Frontantrieb	Diesel	66	90	Jul 2010	Nov 2013	2024-03-01	3040
Lada	1200-1600	1200 L/S	Stufenheck	Heckantrieb	Benzin	44	60	Jan 1970	Jun 1986	2024-03-01	3041
Lada	1200-1500	1200	Kombi	Heckantrieb	Benzin	44	60	Sep 1973	Aug 1984	2024-03-01	3042
Lada	1200-1600	1300	Stufenheck	Heckantrieb	Benzin	51	69	Aug 1974	Aug 1984	2024-03-01	3043
Lada	Toscana	1500	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1983	Feb 1993	2024-03-01	3044
Lada	1200-1600	1500	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1972	Aug 1984	2024-03-01	3045
Lada	1200-1500	1500	Kombi	Heckantrieb	Benzin	55	75	Sep 1973	Jun 1985	2024-03-01	3046
Lada	1200-1600	1600	Stufenheck	Heckantrieb	Benzin	58	79	Sep 1972	Aug 1984	2024-03-01	3047
Lada	Nova	1200 Junior/l	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1981	Apr 2012	2024-03-01	3048
Lada	Nova	1300 Spezial/l	Stufenheck	Heckantrieb	Benzin	48	65	May 1981	Apr 2012	2024-03-01	3049
Lada	Nova	1500 Special	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1985	Apr 2012	2024-03-01	3050
Lada	Nova	1300	Kombi	Heckantrieb	Benzin	48	65	Sep 1985	Dec 1994	2024-03-01	3051
Lada	Nova	1500	Kombi	Heckantrieb	Benzin	55	75	Sep 1985	Apr 1998	2024-03-01	3052
Lada	Samara	1300	Schrägheck	Frontantrieb	Benzin	46	63	Jun 1987	Dec 1996	2024-03-01	3053
Lada	Samara	1300	Schrägheck	Frontantrieb	Benzin	48	65	Jan 1986	Dec 1994	2024-03-01	3054
Lada	Samara	1500	Schrägheck	Frontantrieb	Benzin	53	72	Sep 1987	Dec 1996	2024-03-01	3056
Lada	Samara	1100	Schrägheck	Frontantrieb	Benzin	39	53	Feb 1988	Dec 1994	2024-03-01	3057
Lada	Samara	1300	Stufenheck	Frontantrieb	Benzin	48	65	May 1989	Jul 1997	2024-03-01	3058
Lada	Samara	1500	Stufenheck	Frontantrieb	Benzin	53	72	Sep 1991	Dec 1996	2024-03-01	3059
Lada	Samara	1300	Schrägheck	Frontantrieb	Benzin	45	61	Sep 1991	Aug 1999	2024-03-01	3060
Lada	Samara	1500	Schrägheck	Frontantrieb	Benzin	50	68	Sep 1991	Dec 1996	2024-03-01	3061
Lada	Niva	1600 4X4	Geländewagen geschlossen	Allrad	Benzin	54	73	Jan 1987	Mar 1995	2024-03-01	3063
Lada	Niva	1600	Geländewagen geschlossen	Allrad	Benzin	56	76	Dec 1976	Dec 1993	2024-03-01	3064
Lada	Samara	1300	Stufenheck	Frontantrieb	Benzin	46	63	May 1990	Aug 1999	2024-03-01	3065
Zastava	101	1.1	Schrägheck	Frontantrieb	Benzin	41	56	May 1975	Dec 1993	2024-03-01	3066
Zastava	Yugo	60 EFI	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1991	Jun 1995	2024-03-01	3067
Zastava	Yugo	65 EFI	Schrägheck	Frontantrieb	Benzin	48	65	Jul 1981	Jun 1995	2024-03-01	3068
Yugo	Florida	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Mar 1991	Nov 2008	2024-03-01	3069
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	124	169	Nov 1973	Jan 1980	2024-03-01	3070
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	151	205	Sep 1979	Dec 1987	2024-03-01	3071
Jaguar	Xj	12 5.3	Stufenheck	Heckantrieb	Benzin	211	287	May 1975	Feb 1993	2024-03-01	3073
Jaguar	Xj	12 H.e.	Stufenheck	Heckantrieb	Benzin	217	295	May 1981	Dec 1992	2024-03-01	3074
Jaguar	Xj	Sovereign V12	Stufenheck	Heckantrieb	Benzin	194	264	Oct 1986	Dec 1992	2024-03-01	3075
Jaguar	Xj	6 3.6	Stufenheck	Heckantrieb	Benzin	145	197	Oct 1986	Aug 1989	2024-03-01	3077
Jaguar	Xj	6 3.6	Stufenheck	Heckantrieb	Benzin	156	212	Oct 1986	Aug 1989	2024-03-01	3078
Jaguar	Xj	6 3.2 24V	Stufenheck	Heckantrieb	Benzin	146	199	Sep 1990	Nov 1994	2024-03-01	3079
Jaguar	Xj	6 4.0	Stufenheck	Heckantrieb	Benzin	163	222	Sep 1989	Nov 1994	2024-03-01	3080
Jaguar	Xj	V12 6.0	Stufenheck	Heckantrieb	Benzin	229	311	Mar 1993	Nov 1994	2024-03-01	3081
Citroën	Nemo	1.3 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2010	-	2024-03-01	3083
Austin	Mini	850	Schrägheck	Frontantrieb	Benzin	25	34	Jun 1959	Aug 1969	2024-03-01	3086
Austin	Mini	1000	Schrägheck	Frontantrieb	Benzin	26	35	Oct 1967	Sep 1984	2024-03-01	3088
Austin	Mini	1000	Schrägheck	Frontantrieb	Benzin	29	39	Oct 1967	Sep 1984	2024-03-01	3089
Austin	Mini	1000 Mayfair Sport	Schrägheck	Frontantrieb	Benzin	30	41	Sep 1988	Jun 1993	2024-03-01	3090
Austin	Mini	1000 Mayfair	Schrägheck	Frontantrieb	Benzin	31	42	Aug 1982	Jun 1993	2024-03-01	3091
Rover	Mini	1000	Schrägheck	Frontantrieb	Benzin	30	41	Aug 1990	Jun 1993	2024-03-01	3092
Austin	Mini	1100 Special	Schrägheck	Frontantrieb	Benzin	33	45	Jan 1976	Aug 1981	2024-03-01	3093
Austin	Mini	1275 GT	Schrägheck	Frontantrieb	Benzin	39	53	Oct 1969	Aug 1980	2024-03-01	3094
Rover	Mini	1300	Schrägheck	Frontantrieb	Benzin	45	61	Jan 1991	Dec 1991	2024-03-01	3095
Rover	Mini	1300	Schrägheck	Frontantrieb	Benzin	39	53	Jan 1992	Apr 1995	2024-03-01	3096
Rover	Mini	1300	Schrägheck	Frontantrieb	Benzin	46	63	Jan 1992	Nov 2000	2024-03-01	3097


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓闭合 Porsche 928 的早期型、S 300、S 310、S4/GT 和 GTS 五个尺寸组；其中 S4 与 GT 三维一致，复用同组，GTS 因宽体及长度变化独立建组。([汽车数据][1])
* 已闭合 Porsche 911 的 964 Turbo、964 Carrera 4、964 Carrera RS，以及 993 Carrera 外廓。([汽车数据][2])
* 911 Carrera 3.2 Speedster 已确认同时存在 Turbo-width 宽体和少量窄体；宽体已闭合，窄体高度缺少同配置直接来源，暂不创建尺寸组。([保时捷新闻网][3])
* Saab 900 I Sedan 已确认 1987 年改款前后外廓发生变化；改款后与 Cabriolet 已闭合，改款前长度存在来源冲突，相关分支保持 PENDING。([汽车数据][4])
* Saab 9000 CD/CDE Sedan 当前输入均复用同一已闭合尺寸组。([汽车数据][5])

## 当前批次进度

* 输入 Ktype：100
* 本轮新增 READY 映射：29 行
* 本轮新增 PENDING 映射：4 行
* 已确认尺寸组：15
* 已完整研究 Ktype：26
* 含部分 READY、但仍有未闭合派生分支的 Ktype：3
* 尚未研究 Ktype：70
* 当前仍需闭合的 Ktype：74
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2990	2990	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-EARLY-01	HIGH	早期4.5车型外廓。	READY
2991	2991	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S300-01	HIGH	4.7 S 300车型外廓。	READY
2992	2992	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S310-01	HIGH	4.7 S 310车型外廓。	READY
2993	2993	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	生产区间和功率对应S4外廓。	READY
2994	2994	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	催化配置不改变S4外廓。	READY
2995	2995	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	GT与S4复用相同外廓尺寸组。	READY
2996	2996	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-GTS-01	HIGH	GTS宽体外廓。	READY
2997	2997	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-TURBO-01	HIGH	964 Turbo宽体外廓。	READY
2998	2998	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-CARRERA-01	HIGH	964 Carrera 4标准车身外廓。	READY
2999	2999	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-RS-01	HIGH	964 Carrera RS独立规格外廓。	READY
3000	3000	Coupe	Porsche 968	968	2	EU-PORSCHE-968-COUPE-01	HIGH	968 Coupe外廓。	READY
3001	3001	Convertible	Porsche 968	968	2	EU-PORSCHE-968-CONVERTIBLE-01	HIGH	968 Cabriolet独立车身形式。	READY
3002	3002	Coupe	Porsche 911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH	993 Carrera标准车身外廓。	READY
3003_prefl	3003	Sedan	Saab 900 I		4		MEDIUM	已确认1987年前后外廓变化；改款前长度来源冲突待解决。	PENDING: 改款前车身长度来源冲突
3003_facelift	3003	Sedan	Saab 900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越1987年改款，保留改款后分支。	READY
3004_prefl	3004	Sedan	Saab 900 I		4		MEDIUM	已确认1987年前后外廓变化；改款前长度来源冲突待解决。	PENDING: 改款前车身长度来源冲突
3004_facelift	3004	Sedan	Saab 900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越1987年改款，保留改款后分支。	READY
3005	3005	Sedan	Saab 900 I		4		MEDIUM	生产期仅覆盖改款前车身，长度来源冲突待解决。	PENDING: 改款前车身长度来源冲突
3006	3006	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTERTIBLE-01	HIGH	Classic 900 Cabriolet外廓。	READY
3007	3007	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTERTIBLE-01	HIGH	低增压配置不改变Cabriolet外廓。	READY
3008	3008	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	MEDIUM	输入未写CD标记，按9000四门Sedan边界关联。	READY
3009	3009	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3010	3010	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 Turbo CD Sedan外廓。	READY
3011	3011	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3012	3012	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 Turbo CD Sedan外廓。	READY
3013	3013	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	功率差异不改变CD Sedan外廓。	READY
3014	3014	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3015	3015	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	CDE配置等级不改变CD Sedan外廓。	READY
3016	3016	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	Eco-power配置不改变CD Sedan外廓。	READY
3017	3017	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	MEDIUM	输入未写CD标记，按9000四门Sedan边界关联。	READY
3018	3018	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Turbo Sedan外廓。	READY
3019_narrow	3019	Convertible	Porsche 911 G-Series		2		MEDIUM	窄体Speedster分支已确认；同配置高度直接来源待闭合。	PENDING: 窄体Speedster高度直接来源缺失
3019_wide	3019	Convertible	Porsche 911 G-Series		2	EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	HIGH	Turbo-width Speedster物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-928-COUPE-EARLY-01	4447	1836	1313	Auto-Data Porsche 928 4.5 V8	https://www.auto-data.net/en/porsche-928-4.5-v8-240hp-automatic-42393
EU-PORSCHE-928-COUPE-S300-01	4450	1840	1280	Auto-Data Porsche 928 4.7 S 300	https://www.auto-data.net/en/porsche-928-4.7-s-300hp-6733
EU-PORSCHE-928-COUPE-S310-01	4447	1836	1282	Auto-Data Porsche 928 4.7 S V8 310	https://www.auto-data.net/en/porsche-928-4.7-s-v8-310hp-automatic-42391
EU-PORSCHE-928-COUPE-S4-GT-01	4520	1836	1282	Auto-Data Porsche 928 S4; Auto-Data Porsche 928 GT	https://www.auto-data.net/en/porsche-928-5.0-s4-320hp-6736; https://www.auto-data.net/en/porsche-928-5.0-gt-v8-330hp-6737
EU-PORSCHE-928-COUPE-GTS-01	4523	1890	1282	Auto-Data Porsche 928 GTS	https://www.auto-data.net/en/porsche-928-5.4-gts-v8-350hp-automatic-45289
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310	Auto-Data Porsche 911 964 Turbo 3.3	https://www.auto-data.net/en/porsche-911-964-turbo-3.3-320hp-6624
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310	Auto-Data Porsche 911 964 Carrera 4	https://www.auto-data.net/en/porsche-911-964-carrera-4-3.6-250hp-6627
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310	Auto-Data Porsche 911 964 Carrera RS	https://www.auto-data.net/en/porsche-911-964-carrera-rs-3.6-260hp-6628
EU-PORSCHE-968-COUPE-01	4320	1735	1275	Auto-Data Porsche 968 model specifications	https://www.auto-data.net/en/porsche-968-model-726
EU-PORSCHE-968-CONVERTIBLE-01	4320	1735	1275	Auto-Data Porsche 968 Cabrio specifications	https://www.auto-data.net/en/porsche-968-model-726
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315	Auto-Data Porsche 911 993 Carrera	https://www.auto-data.net/en/porsche-911-993-carrera-3.6-272hp-6607
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I facelift Sedan	https://www.auto-data.net/en/saab-900-i-facelift-1987-2.0i-16v-126hp-12004
EU-SAAB-900-I-CONVERTERTIBLE-01	4680	1690	1420	Auto-Data Saab 900 I Cabriolet	https://www.auto-data.net/en/saab-900-i-cabriolet-generation-2548
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420	Auto-Data Saab 9000 Sedan specifications	https://www.auto-data.net/en/saab-9000-generation-2534
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280	Porsche Newsroom G-Series history; Supercars 1989 Porsche 911 Speedster specifications	https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/50-Jahre-Porsche-911-%28G-Serie%29-%E2%80%93-Der-Dauerbrenner-von-Porsche.html; https://www.supercars.net/blog/1989-porsche-911-speedster/
```

## 下一步优先处理

1. 闭合 Saab 900 I 改款前 Sedan 的长度冲突，并补齐 3019 窄体 Speedster 的同配置高度来源。
2. 按尺寸组聚类处理 Skoda Rapid、100、105/120、Favorit/Forman。
3. 批量处理 Lada 经典后驱 Sedan/Wagon、Samara 三门/五门/Sedan 和 Niva，优先识别同一 Ktype 是否跨多个车身分支。
4. 随后处理 Jaguar XJ Series II/III、XJ40，避免将不同代际和轴距混入同组。
5. 最后闭合 Austin/Rover Mini、Citroën Nemo、Zastava/Yugo 等剩余车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/porsche-928-4.5-v8-240hp-automatic-42393 "Porsche 928 4.5 V8 (240 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/porsche-911-964-turbo-3.3-320hp-6624 "Porsche 911 (964) Turbo 3.3 (320 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/50-Jahre-Porsche-911-%28G-Serie%29-%E2%80%93-Der-Dauerbrenner-von-Porsche.html "50 years of the Porsche 911 (G-Series) – the evergreen Porsche sports car - Porsche Newsroom"
[4]: https://www.auto-data.net/en/saab-900-model-1277 "Saab 900 | Technical Specs, Fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/saab-9000-generation-2534 "Saab 9000 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已消除上轮 4 个阻塞分支：Saab 900 I 四门版进一步拆分为 1983 年前和 1983 年更新后两种外廓；Porsche 911 G-Series 窄体 Speedster 已闭合。欧洲版 Saab 900 Turbo 四门在两个阶段的尺寸分别为 `4740×1690×1420 mm` 和 `4740×1690×1425 mm`；窄体 Speedster 为 `4250×1652×1280 mm`。([汽车目录][1])
* 修正 Saab Cabriolet 尺寸组 ID 的 `CONVERTERTIBLE` 拼写错误，3006、3007 已改为引用 `EU-SAAB-900-I-CONVERTIBLE-01`。
* 已批量闭合 Skoda Rapid 130、100/110、105/120 改款前后、Favorit 781 和 Forman 785。Škoda 历史技术资料明确给出 105/120 在 1983 年前后由 `4160×1595×1400 mm` 变为 `4200×1610×1400 mm`；Forman 785 官方历史资料为 `4160×1620×1425 mm`。([汽车中心][2])

## 当前批次进度

* 已闭合输入 Ktype：49
* READY 映射：58 行
* PENDING／待处理输入：51 个 Ktype
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3003_pre83	3003	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	MEDIUM	输入生产期覆盖1983年前四门外廓。	READY
3003_post83_prefl	3003	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产期覆盖1983更新后、1987改款前外廓。	READY
3004_pre83	3004	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	MEDIUM	输入生产期覆盖1983年前四门外廓。	READY
3004_post83_prefl	3004	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产期覆盖1983更新后、1987改款前外廓。	READY
3005_pre83	3005	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	HIGH	1983年前Turbo四门外廓。	READY
3005_post83_prefl	3005	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	HIGH	1983更新后Turbo四门外廓。	READY
3006	3006	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH	修正尺寸组ID拼写。	READY
3007	3007	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH	修正尺寸组ID拼写。	READY
3019_narrow	3019	Convertible	Porsche 911 G-Series		2	EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	HIGH	窄体Speedster物理外廓。	READY
3020	3020	Coupe	Škoda Rapid 130	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH	Rapid 130 Type 743 Coupe。	READY
3021	3021	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-01	HIGH		READY
3022	3022	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-01	HIGH		READY
3023	3023	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	生产期结束于1983外廓更新前。	READY
3024_prefl	3024	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3024_facelift	3024	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3025_prefl	3025	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3025_facelift	3025	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3026_prefl	3026	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3026_facelift	3026	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3027	3027	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3028	3028	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3029	3029	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3030	3030	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3031	3031	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3032	3032	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3033	3033	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3034	3034	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3035	3035	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3036	3036	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
3037	3037	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
3038	3038	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420	Automobile-Catalog 1980 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1980/3020825/saab_900_turbo_4-door.html
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425	Automobile-Catalog 1985 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1985/3022820/saab_900_turbo_4-door.html
EU-SAAB-900-I-CONVERTIBLE-01	4680	1690	1420	Auto-Data Saab 900 I Cabriolet specifications	https://www.auto-data.net/en/saab-900-i-cabriolet-generation-2548
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280	Auto-Data Porsche 911 Speedster	https://www.auto-data.net/en/porsche-911-speedster-generation-8161
EU-SKODA-RAPID-743-COUPE-01	4200	1610	1380	Automobile-Catalog 1985 Skoda Rapid 130	https://www.automobile-catalog.com/car/1985/52625/skoda_rapid_130.html
EU-SKODA-100-110-SEDAN-01	4155	1620	1380	Automobile-Catalog 1970 Skoda 100	https://www.automobile-catalog.com/car/1970/39320/skoda_100.html
EU-SKODA-105-120-SEDAN-PREFL-01	4160	1595	1400	Škoda Auto historical technical sheet - Škoda 105 Type 742	https://www.allcarcentral.com/Skoda_pdf/Skoda_105_%28Type_742%29_1976_1987.pdf
EU-SKODA-105-120-SEDAN-FACELIFT-01	4200	1610	1400	Škoda Auto historical technical sheet - Škoda 105 Type 742	https://www.allcarcentral.com/Skoda_pdf/Skoda_105_%28Type_742%29_1976_1987.pdf
EU-SKODA-FAVORIT-781-HATCHBACK-01	3815	1620	1415	Automobile-Catalog 1989 Skoda Favorit 135 L	https://www.automobile-catalog.com/car/1989/3132785/skoda_favorit_135_l.html
EU-SKODA-FORMAN-785-WAGON-01	4160	1620	1425	Škoda Auto historical technical sheet - Forman Type 785	https://www.allcarcentral.com/Skoda_pdf/skoda_Forman_135_1990_1994.pdf
```

## 下一步优先处理

1. Citroën AX 4×4、MINI R56 ONE D。
2. Lada 经典后驱 Sedan/Wagon，按 2101、2102、2103、2104、2105、2106、2107 物理车身边界聚类。
3. Lada Samara 三门、五门与 Sedan，以及 Niva 2121。
4. Zastava/Yugo、Jaguar XJ Series II/III 和 XJ40。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/3020825/saab_900_turbo_4-door.html?utm_source=chatgpt.com "1980 Saab 900 Turbo 4-door Specs Review (106.7 kW / 145 PS / 143 hp) (since mid-year 1980 for Europe )"
[2]: https://www.allcarcentral.com/Skoda_pdf/Skoda_105_%28Type_742%29_1976_1987.pdf "(Microsoft Word - \212koda 105.doc)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Citroën AX 14 4×4 的 1992 年前后两种外廓；同一 Ktype 覆盖三门和五门，因此按门数分别派生映射，但相同阶段共用尺寸组。改款前后尺寸分别为 `3495×1596×1340 mm` 和 `3525×1555×1355 mm`。([汽车数据][1])
* 已闭合 MINI Hatch R56 ONE D 三门车型。([Autohaus24][2])
* 已批量闭合 Lada VAZ-2101、21011、2102、2103、2104、2105、2106 和 Niva 2121；相同旅行车或轿车外廓的不同发动机版本直接复用尺寸组。([汽车数据][3])

## 当前批次进度

* 已闭合输入 Ktype：64
* READY 映射：76 行
* PENDING／待处理输入 Ktype：36
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3039_3dr_pre92	3039	Hatchback	Citroën AX Phase I	ZA	3	EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	MEDIUM	1992年前三门外廓分支。	READY
3039_5dr_pre92	3039	Hatchback	Citroën AX Phase I	ZA	5	EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	MEDIUM	1992年前五门外廓分支。	READY
3039_3dr_post92	3039	Hatchback	Citroën AX Phase II	ZA	3	EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	MEDIUM	1992年更新后三门外廓分支。	READY
3039_5dr_post92	3039	Hatchback	Citroën AX Phase II	ZA	5	EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	MEDIUM	1992年更新后五门外廓分支。	READY
3040	3040	Hatchback	MINI Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-01	HIGH		READY
3041	3041	Sedan	Lada 2101	VAZ-2101	4	EU-LADA-2101-SEDAN-01	HIGH		READY
3042	3042	Wagon	Lada 2102	VAZ-2102	5	EU-LADA-2102-WAGON-01	HIGH		READY
3043	3043	Sedan	Lada 21011	VAZ-21011	4	EU-LADA-21011-SEDAN-01	MEDIUM	1300版本对应VAZ-21011外廓。	READY
3045	3045	Sedan	Lada 2103	VAZ-2103	4	EU-LADA-2103-SEDAN-01	HIGH		READY
3046	3046	Wagon	Lada 2102	VAZ-2102	5	EU-LADA-2102-WAGON-01	HIGH	1500动力版本不改变VAZ-2102旅行车外廓。	READY
3047	3047	Sedan	Lada 2106	VAZ-2106	4	EU-LADA-2106-SEDAN-01	HIGH		READY
3048	3048	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	HIGH		READY
3049	3049	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	HIGH		READY
3050	3050	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	MEDIUM	Nova 1500 Special对应VAZ-2105轿车外廓。	READY
3051	3051	Wagon	Lada 2104	VAZ-2104	5	EU-LADA-2104-WAGON-01	HIGH		READY
3052	3052	Wagon	Lada 2104	VAZ-2104	5	EU-LADA-2104-WAGON-01	HIGH		READY
3063	3063	SUV	Lada Niva 2121	VAZ-2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
3064	3064	SUV	Lada Niva 2121	VAZ-2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	3495	1596	1340	Automobile-Catalog 1991 Citroen AX 4x4; Auto-Data Citroen AX GT 4x4	https://www.automobile-catalog.com/car/1991/540980/citroen_ax_4x4.html; https://www.auto-data.net/en/citroen-ax-gt-1.4-cat-75hp-4x4-15074
EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	3525	1555	1355	Automobile-Catalog 1992 Citroen AX 4x4; Auto-Data Citroen AX 1992 4x4	https://www.automobile-catalog.com/car/1992/541265/citroen_ax_4x4.html; https://www.auto-data.net/en/citroen-ax-phase-i-1992-14-cat-1.4-75hp-4x4-27305
EU-MINI-HATCH-R56-HATCHBACK-3D-01	3709	1683	1407	Auto-Data MINI Hatch R56 One D 1.6	https://www.auto-data.net/en/mini-hatch-r56-one-d-1.6-90hp-21497
EU-LADA-2101-SEDAN-01	4073	1611	1440	Auto-Data Lada 2101 1.2	https://www.auto-data.net/en/lada-2101-1.2-62hp-13242
EU-LADA-2102-WAGON-01	4059	1611	1458	Auto-Data Lada 2102 model specifications	https://www.auto-data.net/en/lada-2102-model-1412
EU-LADA-21011-SEDAN-01	4043	1611	1440	Auto-Data Lada 2101 model specifications	https://www.auto-data.net/en/lada-2101-model-1407
EU-LADA-2103-SEDAN-01	4116	1611	1440	Auto-Data Lada 2103 1.5	https://www.auto-data.net/en/lada-2103-1.5-73hp-13266
EU-LADA-2106-SEDAN-01	4166	1611	1440	Auto-Data Lada 2106 1.6	https://www.auto-data.net/en/lada-2106-1.6-75hp-13225
EU-LADA-2105-SEDAN-01	4130	1620	1446	Auto-Data Lada 2105 1.3	https://www.auto-data.net/en/lada-2105-1.3-64hp-13306
EU-LADA-2104-WAGON-01	4115	1620	1443	Auto-Data Lada 2104 1.3	https://www.auto-data.net/en/lada-2104-1.3-64hp-13282
EU-LADA-NIVA-2121-SUV-3D-01	3720	1680	1640	Auto-Data Lada Niva 3-door 1.6 4x4	https://www.auto-data.net/en/lada-niva-3-door-1.6-78hp-4x4-43354
```

## 下一步优先处理

1. 确认 Lada Toscana 3044 对应 VAZ-2105 或 VAZ-2107 的准确物理边界。
2. 按三门 Hatchback、五门 Hatchback、Sedan 聚类闭合 Lada Samara 3053–3061、3065。
3. 批量处理 Zastava 101、Yugo、Florida。
4. 闭合 Jaguar XJ Series II、Series III 与 XJ40，按代际和轴距差异拆组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-ax-gt-1.4-cat-75hp-4x4-15074 "Citroen AX GT 1.4 CAT (75 Hp) 4x4 | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.ah-24.com/Brake-technology/EBC-brake-discs-brake-pads/EBC-Standardbremsscheiben-for/Mini/Mini/VA-vorne-front/EBC-Premium-Disc-fits-for-Mini-Mini-R56%3A%3A157812.html?utm_source=chatgpt.com "EBC Premium Disc fits for Mini Mini R56 - Autohaus24"
[3]: https://www.auto-data.net/en/lada-2101-1.2-62hp-13242?utm_source=chatgpt.com "Lada 2101 1.2 (62 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Lada Toscana 1500，对应 VAZ-2107 Sedan 外廓。
* 已按 VAZ-2108 三门、VAZ-2109 五门和 VAZ-21099 Sedan 三类物理车身，批量关联 Lada Samara Ktype；发动机和功率差异不再重复建组。([汽车数据][1])
* 已闭合 Zastava 101、Yugo 60/65 EFI。
* Yugo Florida Ktype 3069 的生产期跨越 2003 年外廓更新，已拆为更新前后两个派生分支。([汽车数据][2])

## 当前批次进度

* 已闭合输入 Ktype：78
* READY 映射：97 行
* PENDING／待处理输入 Ktype：22
* 已确认尺寸组：43
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3044	3044	Sedan	Lada 2107	VAZ-2107	4	EU-LADA-2107-SEDAN-01	HIGH	Toscana 1500对应VAZ-2107。	READY
3053_3dr	3053	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3053_5dr	3053	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3054_3dr	3054	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3054_5dr	3054	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3056_3dr	3056	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3056_5dr	3056	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3057_3dr	3057	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门1100分支。	READY
3057_5dr	3057	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门1100分支。	READY
3058	3058	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3059	3059	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3060_3dr	3060	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3060_5dr	3060	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3061_3dr	3061	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3061_5dr	3061	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3065	3065	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3066	3066	Hatchback	Zastava 101	101	5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
3067	3067	Hatchback	Zastava Yugo EFI		3	EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	HIGH		READY
3068	3068	Hatchback	Zastava Yugo EFI		3	EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	HIGH		READY
3069_pre03	3069	Hatchback	Zastava Yugo Florida		5	EU-ZASTAVA-FLORIDA-HATCHBACK-PRE03-01	HIGH	输入生产期覆盖2003年更新前外廓。	READY
3069_post03	3069	Hatchback	Zastava Yugo Florida facelift		5	EU-ZASTAVA-FLORIDA-HATCHBACK-POST03-01	HIGH	输入生产期覆盖2003年更新后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-2107-SEDAN-01	4145	1620	1435	Auto-Data Lada 2107 1.5	https://www.auto-data.net/en/lada-2107-1.5-72hp-13246
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402	Auto-Data Lada 2108 1.3	https://www.auto-data.net/en/lada-2108-1.3-65hp-13261
EU-LADA-SAMARA-I-HATCHBACK-5D-01	4006	1650	1402	Auto-Data Lada 2109 1.3	https://www.auto-data.net/en/lada-2109-1.3-64hp-13272
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402	Auto-Data Lada 21099	https://www.auto-data.net/en/lada-21099-generation-2833
EU-ZASTAVA-101-HATCHBACK-5D-01	3890	1590	1345	Auto-Data Zastava 101 1.1	https://www.auto-data.net/en/zastava-101-1100-1.1-56hp-11657
EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	3490	1550	1390	UltimateSpecs Yugo 65A EFI; Auto-Data Zastava Yugo EFI generation	https://www.ultimatespecs.com/car-specs/Yugo/5464/Yugo-Yugo-65A-EFi.html; https://www.auto-data.net/en/zastava-yugo-generation-2473
EU-ZASTAVA-FLORIDA-HATCHBACK-PRE03-01	3930	1660	1410	Auto-Data Zastava Yugo Florida 1.3 103A	https://www.auto-data.net/en/zastava-yugo-florida-1.3-103-a-68hp-11662
EU-ZASTAVA-FLORIDA-HATCHBACK-POST03-01	4030	1658	1428	Auto-Data Zastava Yugo Florida 1.3i	https://www.auto-data.net/en/zastava-yugo-florida-1.3-i-68hp-11663
```

## 下一步优先处理

1. Jaguar XJ Series II、Series III 和 XJ40，优先拆分短轴、长轴及代际边界。
2. Citroën Nemo Kasten与乘用 MPV 双分支。
3. Austin/Rover Mini，核对 Mk I、Clubman 1275 GT 与后期经典 Mini 的外廓差异。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lada-2108-1.3-65hp-13261?utm_source=chatgpt.com "Lada 2108 1.3 (65 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/zastava-yugo-florida-1.3-i-68hp-11663?utm_source=chatgpt.com "Zastava Yugo Florida 1.3 i (68 Hp) /Hatchback 2003 - 2008"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2901-3000_ktype_dimension_mapping_final.tsv
- all_2901-3000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 Jaguar XJ：Series II、Series III、XJ40/XJ81 分别建立稳定尺寸组；跨代的 Ktype 3073 已拆分为 Series II 与 Series III 两个物理分支。([CarsGuide][1])
* Citroën Nemo Ktype 3083 已拆分为 Panel Van 与 Multispace，两种车身长度不同，宽度和高度一致。([汽车数据][2])
* Austin/Rover Mini 已按经典圆头车身、1275 GT 加长前部车身及后期 Rover Mini 三个尺寸组闭合。([汽车目录][3])
* 已完成一次机械收尾：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：121 行
* PENDING 映射：0
* DIMENSION_GROUP：51 个
* 映射引用未闭合：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2990	2990	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-EARLY-01	HIGH	早期4.5车型外廓。	READY
2991	2991	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S300-01	HIGH	4.7 S 300车型外廓。	READY
2992	2992	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S310-01	HIGH	4.7 S 310车型外廓。	READY
2993	2993	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	生产区间和功率对应S4外廓。	READY
2994	2994	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	催化配置不改变S4外廓。	READY
2995	2995	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-S4-GT-01	HIGH	GT与S4复用相同外廓尺寸组。	READY
2996	2996	Coupe	Porsche 928	928	2	EU-PORSCHE-928-COUPE-GTS-01	HIGH	GTS宽体外廓。	READY
2997	2997	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-TURBO-01	HIGH	964 Turbo宽体外廓。	READY
2998	2998	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-CARRERA-01	HIGH	964 Carrera 4标准车身外廓。	READY
2999	2999	Coupe	Porsche 911 964	964	2	EU-PORSCHE-911-964-COUPE-RS-01	HIGH	964 Carrera RS独立规格外廓。	READY
3000	3000	Coupe	Porsche 968	968	2	EU-PORSCHE-968-COUPE-01	HIGH	968 Coupe外廓。	READY
3001	3001	Convertible	Porsche 968	968	2	EU-PORSCHE-968-CONVERTIBLE-01	HIGH	968 Cabriolet独立车身形式。	READY
3002	3002	Coupe	Porsche 911 993	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH	993 Carrera标准车身外廓。	READY
3003_pre83	3003	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	MEDIUM	输入生产期覆盖1983年前四门外廓。	READY
3003_post83_prefl	3003	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产期覆盖1983更新后、1987改款前外廓。	READY
3003_facelift	3003	Sedan	Saab 900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越1987年改款，保留改款后分支。	READY
3004_pre83	3004	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	MEDIUM	输入生产期覆盖1983年前四门外廓。	READY
3004_post83_prefl	3004	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产期覆盖1983更新后、1987改款前外廓。	READY
3004_facelift	3004	Sedan	Saab 900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越1987年改款，保留改款后分支。	READY
3005_pre83	3005	Sedan	Saab 900 I early		4	EU-SAAB-900-I-SEDAN-PRE83-01	HIGH	1983年前Turbo四门外廓。	READY
3005_post83_prefl	3005	Sedan	Saab 900 I 1983 update		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	HIGH	1983更新后Turbo四门外廓。	READY
3006	3006	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH		READY
3007	3007	Convertible	Saab 900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH		READY
3008	3008	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	MEDIUM	输入未写CD标记，按9000四门Sedan边界关联。	READY
3009	3009	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3010	3010	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 Turbo CD Sedan外廓。	READY
3011	3011	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3012	3012	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 Turbo CD Sedan外廓。	READY
3013	3013	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	功率差异不改变CD Sedan外廓。	READY
3014	3014	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Sedan外廓。	READY
3015	3015	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	CDE配置等级不改变CD Sedan外廓。	READY
3016	3016	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	Eco-power配置不改变CD Sedan外廓。	READY
3017	3017	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	MEDIUM	输入未写CD标记，按9000四门Sedan边界关联。	READY
3018	3018	Sedan	Saab 9000	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH	9000 CD Turbo Sedan外廓。	READY
3019_narrow	3019	Convertible	Porsche 911 G-Series		2	EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	HIGH	窄体Speedster物理外廓。	READY
3019_wide	3019	Convertible	Porsche 911 G-Series		2	EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	HIGH	Turbo-width Speedster物理外廓。	READY
3020	3020	Coupe	Škoda Rapid 130	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH	Rapid 130 Type 743 Coupe。	READY
3021	3021	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-01	HIGH		READY
3022	3022	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-01	HIGH		READY
3023	3023	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	生产期结束于1983外廓更新前。	READY
3024_prefl	3024	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3024_facelift	3024	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3025_prefl	3025	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3025_facelift	3025	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3026_prefl	3026	Sedan	Škoda 105/120 pre-facelift	742	4	EU-SKODA-105-120-SEDAN-PREFL-01	HIGH	输入生产期跨越1983外廓更新。	READY
3026_facelift	3026	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH	输入生产期跨越1983外廓更新。	READY
3027	3027	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3028	3028	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3029	3029	Sedan	Škoda 105/120 facelift	744	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
3030	3030	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3031	3031	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3032	3032	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3033	3033	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3034	3034	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3035	3035	Hatchback	Škoda Favorit	781	5	EU-SKODA-FAVORIT-781-HATCHBACK-01	HIGH		READY
3036	3036	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
3037	3037	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
3038	3038	Wagon	Škoda Forman	785	5	EU-SKODA-FORMAN-785-WAGON-01	HIGH	输入Favorit Kombi对应Forman Estate。	READY
3039_3dr_pre92	3039	Hatchback	Citroën AX Phase I	ZA	3	EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	MEDIUM	1992年前三门外廓分支。	READY
3039_5dr_pre92	3039	Hatchback	Citroën AX Phase I	ZA	5	EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	MEDIUM	1992年前五门外廓分支。	READY
3039_3dr_post92	3039	Hatchback	Citroën AX Phase II	ZA	3	EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	MEDIUM	1992年更新后三门外廓分支。	READY
3039_5dr_post92	3039	Hatchback	Citroën AX Phase II	ZA	5	EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	MEDIUM	1992年更新后五门外廓分支。	READY
3040	3040	Hatchback	MINI Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-01	HIGH		READY
3041	3041	Sedan	Lada 2101	VAZ-2101	4	EU-LADA-2101-SEDAN-01	HIGH		READY
3042	3042	Wagon	Lada 2102	VAZ-2102	5	EU-LADA-2102-WAGON-01	HIGH		READY
3043	3043	Sedan	Lada 21011	VAZ-21011	4	EU-LADA-21011-SEDAN-01	MEDIUM	1300版本对应VAZ-21011外廓。	READY
3044	3044	Sedan	Lada 2107	VAZ-2107	4	EU-LADA-2107-SEDAN-01	HIGH	Toscana 1500对应VAZ-2107。	READY
3045	3045	Sedan	Lada 2103	VAZ-2103	4	EU-LADA-2103-SEDAN-01	HIGH		READY
3046	3046	Wagon	Lada 2102	VAZ-2102	5	EU-LADA-2102-WAGON-01	HIGH	1500动力版本不改变VAZ-2102旅行车外廓。	READY
3047	3047	Sedan	Lada 2106	VAZ-2106	4	EU-LADA-2106-SEDAN-01	HIGH		READY
3048	3048	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	HIGH		READY
3049	3049	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	HIGH		READY
3050	3050	Sedan	Lada 2105	VAZ-2105	4	EU-LADA-2105-SEDAN-01	MEDIUM	Nova 1500 Special对应VAZ-2105轿车外廓。	READY
3051	3051	Wagon	Lada 2104	VAZ-2104	5	EU-LADA-2104-WAGON-01	HIGH		READY
3052	3052	Wagon	Lada 2104	VAZ-2104	5	EU-LADA-2104-WAGON-01	HIGH		READY
3053_3dr	3053	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3053_5dr	3053	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3054_3dr	3054	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3054_5dr	3054	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3056_3dr	3056	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3056_5dr	3056	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3057_3dr	3057	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门1100分支。	READY
3057_5dr	3057	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门1100分支。	READY
3058	3058	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3059	3059	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3060_3dr	3060	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3060_5dr	3060	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3061_3dr	3061	Hatchback	Lada Samara I	VAZ-2108	3	EU-LADA-SAMARA-I-HATCHBACK-3D-01	MEDIUM	Ktype覆盖三门Samara分支。	READY
3061_5dr	3061	Hatchback	Lada Samara I	VAZ-2109	5	EU-LADA-SAMARA-I-HATCHBACK-5D-01	MEDIUM	Ktype覆盖五门Samara分支。	READY
3063	3063	SUV	Lada Niva 2121	VAZ-2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
3064	3064	SUV	Lada Niva 2121	VAZ-2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
3065	3065	Sedan	Lada Samara I	VAZ-21099	4	EU-LADA-SAMARA-I-SEDAN-01	HIGH		READY
3066	3066	Hatchback	Zastava 101	101	5	EU-ZASTAVA-101-HATCHBACK-5D-01	HIGH		READY
3067	3067	Hatchback	Zastava Yugo EFI		3	EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	HIGH		READY
3068	3068	Hatchback	Zastava Yugo EFI		3	EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	HIGH		READY
3069_pre03	3069	Hatchback	Zastava Yugo Florida		5	EU-ZASTAVA-FLORIDA-HATCHBACK-PRE03-01	HIGH	输入生产期覆盖2003年更新前外廓。	READY
3069_post03	3069	Hatchback	Zastava Yugo Florida facelift		5	EU-ZASTAVA-FLORIDA-HATCHBACK-POST03-01	HIGH	输入生产期覆盖2003年更新后外廓。	READY
3070	3070	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	HIGH	4.2 169 PS版本对应Series II长轴四门外廓。	READY
3071	3071	Sedan	Jaguar XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3073_series2	3073	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	HIGH	5.3发动机生产期覆盖Series II长轴分支。	READY
3073_series3	3073	Sedan	Jaguar XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH	5.3发动机生产期覆盖Series III分支。	READY
3074	3074	Sedan	Jaguar XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH		READY
3075	3075	Sedan	Jaguar XJ Series III		4	EU-JAGUAR-XJ-SERIES-III-SEDAN-01	HIGH	Sovereign V12属于Series III四门外廓。	READY
3077	3077	Sedan	Jaguar XJ40	XJ40	4	EU-JAGUAR-XJ40-XJ81-SEDAN-01	HIGH		READY
3078	3078	Sedan	Jaguar XJ40	XJ40	4	EU-JAGUAR-XJ40-XJ81-SEDAN-01	HIGH		READY
3079	3079	Sedan	Jaguar XJ40	XJ40	4	EU-JAGUAR-XJ40-XJ81-SEDAN-01	HIGH		READY
3080	3080	Sedan	Jaguar XJ40	XJ40	4	EU-JAGUAR-XJ40-XJ81-SEDAN-01	HIGH		READY
3081	3081	Sedan	Jaguar XJ81	XJ81	4	EU-JAGUAR-XJ40-XJ81-SEDAN-01	HIGH	XJ81 V12外部三维与标准轴距XJ40一致。	READY
3083_panel	3083	Van	Citroën Nemo Panel Van			EU-CITROEN-NEMO-PANEL-VAN-01	HIGH	输入BodyStyle同时覆盖Kasten分支。	READY
3083_multispace	3083	MPV	Citroën Nemo Multispace		5	EU-CITROEN-NEMO-MULTISPACE-MPV-01	HIGH	输入BodyStyle同时覆盖乘用Multispace分支。	READY
3086	3086	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3088	3088	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3089	3089	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3090	3090	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3091	3091	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3092	3092	Hatchback	Rover Mini classic		2	EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3093	3093	Hatchback	Austin Mini classic		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3094	3094	Hatchback	Austin Mini 1275 GT		2	EU-AUSTIN-MINI-1275-GT-HATCHBACK-2D-01	HIGH	1275 GT采用加长Clubman式前部外廓。	READY
3095	3095	Hatchback	Rover Mini classic		2	EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3096	3096	Hatchback	Rover Mini classic		2	EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
3097	3097	Hatchback	Rover Mini classic		2	EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2901-3000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-928-COUPE-EARLY-01	4447	1836	1313	Auto-Data Porsche 928 4.5 V8	https://www.auto-data.net/en/porsche-928-4.5-v8-240hp-automatic-42393
EU-PORSCHE-928-COUPE-S300-01	4450	1840	1280	Auto-Data Porsche 928 4.7 S 300	https://www.auto-data.net/en/porsche-928-4.7-s-300hp-6733
EU-PORSCHE-928-COUPE-S310-01	4447	1836	1282	Auto-Data Porsche 928 4.7 S V8 310	https://www.auto-data.net/en/porsche-928-4.7-s-v8-310hp-automatic-42391
EU-PORSCHE-928-COUPE-S4-GT-01	4520	1836	1282	Auto-Data Porsche 928 S4; Auto-Data Porsche 928 GT	https://www.auto-data.net/en/porsche-928-5.0-s4-320hp-6736; https://www.auto-data.net/en/porsche-928-5.0-gt-v8-330hp-6737
EU-PORSCHE-928-COUPE-GTS-01	4523	1890	1282	Auto-Data Porsche 928 GTS	https://www.auto-data.net/en/porsche-928-5.4-gts-v8-350hp-automatic-45289
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310	Auto-Data Porsche 911 964 Turbo 3.3	https://www.auto-data.net/en/porsche-911-964-turbo-3.3-320hp-6624
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310	Auto-Data Porsche 911 964 Carrera 4	https://www.auto-data.net/en/porsche-911-964-carrera-4-3.6-250hp-6627
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310	Auto-Data Porsche 911 964 Carrera RS	https://www.auto-data.net/en/porsche-911-964-carrera-rs-3.6-260hp-6628
EU-PORSCHE-968-COUPE-01	4320	1735	1275	Auto-Data Porsche 968 model specifications	https://www.auto-data.net/en/porsche-968-model-726
EU-PORSCHE-968-CONVERTIBLE-01	4320	1735	1275	Auto-Data Porsche 968 Cabrio specifications	https://www.auto-data.net/en/porsche-968-model-726
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315	Auto-Data Porsche 911 993 Carrera	https://www.auto-data.net/en/porsche-911-993-carrera-3.6-272hp-6607
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420	Automobile-Catalog 1980 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1980/3020825/saab_900_turbo_4-door.html
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425	Automobile-Catalog 1985 Saab 900 Turbo 4-door	https://www.automobile-catalog.com/car/1985/3022820/saab_900_turbo_4-door.html
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I facelift Sedan	https://www.auto-data.net/en/saab-900-i-facelift-1987-2.0i-16v-126hp-12004
EU-SAAB-900-I-CONVERTIBLE-01	4680	1690	1420	Auto-Data Saab 900 I Cabriolet specifications	https://www.auto-data.net/en/saab-900-i-cabriolet-generation-2548
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420	Auto-Data Saab 9000 Sedan specifications	https://www.auto-data.net/en/saab-9000-generation-2534
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280	Auto-Data Porsche 911 Speedster	https://www.auto-data.net/en/porsche-911-speedster-generation-8161
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280	Porsche Newsroom G-Series history; Supercars 1989 Porsche 911 Speedster specifications	https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/50-Jahre-Porsche-911-%28G-Serie%29-%E2%80%93-Der-Dauerbrenner-von-Porsche.html; https://www.supercars.net/blog/1989-porsche-911-speedster/
EU-SKODA-RAPID-743-COUPE-01	4200	1610	1380	Automobile-Catalog 1985 Skoda Rapid 130	https://www.automobile-catalog.com/car/1985/52625/skoda_rapid_130.html
EU-SKODA-100-110-SEDAN-01	4155	1620	1380	Automobile-Catalog 1970 Skoda 100	https://www.automobile-catalog.com/car/1970/39320/skoda_100.html
EU-SKODA-105-120-SEDAN-PREFL-01	4160	1595	1400	Škoda Auto historical technical sheet - Škoda 105 Type 742	https://www.allcarcentral.com/Skoda_pdf/Skoda_105_%28Type_742%29_1976_1987.pdf
EU-SKODA-105-120-SEDAN-FACELIFT-01	4200	1610	1400	Škoda Auto historical technical sheet - Škoda 105 Type 742	https://www.allcarcentral.com/Skoda_pdf/Skoda_105_%28Type_742%29_1976_1987.pdf
EU-SKODA-FAVORIT-781-HATCHBACK-01	3815	1620	1415	Automobile-Catalog 1989 Skoda Favorit 135 L	https://www.automobile-catalog.com/car/1989/3132785/skoda_favorit_135_l.html
EU-SKODA-FORMAN-785-WAGON-01	4160	1620	1425	Škoda Auto historical technical sheet - Forman Type 785	https://www.allcarcentral.com/Skoda_pdf/skoda_Forman_135_1990_1994.pdf
EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	3495	1596	1340	Automobile-Catalog 1991 Citroen AX 4x4; Auto-Data Citroen AX GT 4x4	https://www.automobile-catalog.com/car/1991/540980/citroen_ax_4x4.html; https://www.auto-data.net/en/citroen-ax-gt-1.4-cat-75hp-4x4-15074
EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	3525	1555	1355	Automobile-Catalog 1992 Citroen AX 4x4; Auto-Data Citroen AX 1992 4x4	https://www.automobile-catalog.com/car/1992/541265/citroen_ax_4x4.html; https://www.auto-data.net/en/citroen-ax-phase-i-1992-14-cat-1.4-75hp-4x4-27305
EU-MINI-HATCH-R56-HATCHBACK-3D-01	3709	1683	1407	Auto-Data MINI Hatch R56 One D 1.6	https://www.auto-data.net/en/mini-hatch-r56-one-d-1.6-90hp-21497
EU-LADA-2101-SEDAN-01	4073	1611	1440	Auto-Data Lada 2101 1.2	https://www.auto-data.net/en/lada-2101-1.2-62hp-13242
EU-LADA-2102-WAGON-01	4059	1611	1458	Auto-Data Lada 2102 model specifications	https://www.auto-data.net/en/lada-2102-model-1412
EU-LADA-21011-SEDAN-01	4043	1611	1440	Auto-Data Lada 2101 model specifications	https://www.auto-data.net/en/lada-2101-model-1407
EU-LADA-2107-SEDAN-01	4145	1620	1435	Auto-Data Lada 2107 1.5	https://www.auto-data.net/en/lada-2107-1.5-72hp-13246
EU-LADA-2103-SEDAN-01	4116	1611	1440	Auto-Data Lada 2103 1.5	https://www.auto-data.net/en/lada-2103-1.5-73hp-13266
EU-LADA-2106-SEDAN-01	4166	1611	1440	Auto-Data Lada 2106 1.6	https://www.auto-data.net/en/lada-2106-1.6-75hp-13225
EU-LADA-2105-SEDAN-01	4130	1620	1446	Auto-Data Lada 2105 1.3	https://www.auto-data.net/en/lada-2105-1.3-64hp-13306
EU-LADA-2104-WAGON-01	4115	1620	1443	Auto-Data Lada 2104 1.3	https://www.auto-data.net/en/lada-2104-1.3-64hp-13282
EU-LADA-SAMARA-I-HATCHBACK-3D-01	4006	1650	1402	Auto-Data Lada 2108 1.3	https://www.auto-data.net/en/lada-2108-1.3-65hp-13261
EU-LADA-SAMARA-I-HATCHBACK-5D-01	4006	1650	1402	Auto-Data Lada 2109 1.3	https://www.auto-data.net/en/lada-2109-1.3-64hp-13272
EU-LADA-SAMARA-I-SEDAN-01	4205	1650	1402	Auto-Data Lada 21099	https://www.auto-data.net/en/lada-21099-generation-2833
EU-LADA-NIVA-2121-SUV-3D-01	3720	1680	1640	Auto-Data Lada Niva 3-door 1.6 4x4	https://www.auto-data.net/en/lada-niva-3-door-1.6-78hp-4x4-43354
EU-ZASTAVA-101-HATCHBACK-5D-01	3890	1590	1345	Auto-Data Zastava 101 1.1	https://www.auto-data.net/en/zastava-101-1100-1.1-56hp-11657
EU-ZASTAVA-YUGO-EFI-HATCHBACK-3D-01	3490	1550	1390	UltimateSpecs Yugo 65A EFI; Auto-Data Zastava Yugo EFI generation	https://www.ultimatespecs.com/car-specs/Yugo/5464/Yugo-Yugo-65A-EFi.html; https://www.auto-data.net/en/zastava-yugo-generation-2473
EU-ZASTAVA-FLORIDA-HATCHBACK-PRE03-01	3930	1660	1410	Auto-Data Zastava Yugo Florida 1.3 103A	https://www.auto-data.net/en/zastava-yugo-florida-1.3-103-a-68hp-11662
EU-ZASTAVA-FLORIDA-HATCHBACK-POST03-01	4030	1658	1428	Auto-Data Zastava Yugo Florida 1.3i	https://www.auto-data.net/en/zastava-yugo-florida-1.3-i-68hp-11663
EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375	CarsGuide Jaguar XJ6 1975 dimensions	https://www.carsguide.com.au/jaguar/xj6/car-dimensions/1975
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1377	CarsGuide Jaguar XJ6 1979 dimensions	https://www.carsguide.com.au/jaguar/xj6/car-dimensions/1979
EU-JAGUAR-XJ40-XJ81-SEDAN-01	4988	1798	1380	Automobile-Catalog 1988 Jaguar XJ6 3.6; Jaguar Enthusiasts Club XJ40 Saloons	https://www.automobile-catalog.com/car/1988/57905/jaguar_xj6_3_6.html; https://jec.org.uk/models/xj40-saloons/
EU-CITROEN-NEMO-PANEL-VAN-01	3864	1716	1721	Auto-Data Citroën Nemo Panel Van 1.3 HDi 75	https://www.auto-data.net/en/citroen-nemo-panel-van-1.3-hdi-75hp-54959
EU-CITROEN-NEMO-MULTISPACE-MPV-01	3959	1716	1721	Auto-Data Citroën Nemo Multispace 1.3 HDi 75	https://www.auto-data.net/en/citroen-nemo-multispace-1.3-hdi-75hp-54982
EU-AUSTIN-MINI-CLASSIC-HATCHBACK-2D-01	3054	1410	1346	Automobile-Catalog 1965 Austin Mini 850	https://www.automobile-catalog.com/car/1965/1705025/austin_mini_850.html
EU-AUSTIN-MINI-1275-GT-HATCHBACK-2D-01	3181	1410	1346	Carfolio Austin Mini 1275 GT	https://www.carfolio.com/austin-mini-1275-gt-50820
EU-ROVER-MINI-CLASSIC-HATCHBACK-2D-01	3100	1440	1351	Auto-Data Rover Mini Mk I specifications	https://www.auto-data.net/en/rover-mini-mk-i-generation-2447
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2901-3000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carsguide.com.au/jaguar/xj6/car-dimensions/1975?utm_source=chatgpt.com "Jaguar XJ6 Dimensions 1975 - Length, Width, Height ..."
[2]: https://www.auto-data.net/en/citroen-nemo-panel-van-1.3-hdi-75hp-54959 "Citroen Nemo Panel Van 1.3 HDi (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1965/1705025/austin_mini_850.html?utm_source=chatgpt.com "1965 Austin Mini 850 (man. 4) (model for Europe ) car ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2901-3000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2901-3000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3604 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（970 行）
