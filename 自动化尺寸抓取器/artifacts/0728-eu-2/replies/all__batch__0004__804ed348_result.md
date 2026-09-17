# 任务：all 第 301-400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0004__804ed348


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 301-400 行

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
all 第 301-400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6 avant	S6 Quattro	Kombi	Allrad	Benzin	320	435	Mar 2006	Aug 2011	2024-03-01	19457
Skoda	Octavia	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	147	200	Oct 2005	Feb 2013	2024-03-01	19458
Skoda	Octavia	2.0 Tfsi	Kombi	Frontantrieb	Benzin	147	200	Oct 2005	Feb 2013	2024-03-01	19459
Audi	A8 d3	S8 Quattro	Stufenheck	Allrad	Benzin	331	450	Jun 2006	Jul 2010	2024-03-01	19460
Ford	Sierra	2.0 I Dohc	Schrägheck	Heckantrieb	Benzin	85	115	Dec 1991	Feb 1993	2024-03-01	19461
Ford	Sierra	2.0 I Dohc	Stufenheck	Heckantrieb	Benzin	85	115	Dec 1991	Feb 1993	2024-03-01	19462
Ford	Sierra	2.0 I Dohc	Kombi	Heckantrieb	Benzin	85	115	Dec 1991	Feb 1993	2024-03-01	19463
Opel	Astra h gtc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	88	120	Sep 2005	Oct 2010	2024-03-01	19464
VW	Golf plus v	1.4 16V	Schrägheck	Frontantrieb	Benzin	59	80	May 2006	Dec 2013	2024-03-01	19465
VW	Golf plus v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	103	140	May 2006	Jun 2008	2024-03-01	19466
VW	Golf plus v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	125	170	May 2006	Jun 2008	2024-03-01	19467
VW	Golf v	1.4 16V	Schrägheck	Frontantrieb	Benzin	59	80	May 2006	Nov 2008	2024-03-01	19468
VW	Golf v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	103	140	May 2006	Nov 2008	2024-03-01	19469
Alfa Romeo	159	1.9 Jtdm 8V	Stufenheck	Frontantrieb	Diesel	85	115	Sep 2005	Nov 2011	2024-03-01	19470
Alfa Romeo	159	1.9 Jtdm 16V	Stufenheck	Frontantrieb	Diesel	100	136	Sep 2005	Nov 2011	2024-03-01	19471
Audi	A6 allroad c6	3.2 FSI Quattro	Kombi	Allrad	Benzin	188	255	May 2006	Oct 2008	2024-03-01	19472
Audi	A6 allroad c6	4.2 FSI Quattro	Kombi	Allrad	Benzin	257	350	May 2006	Dec 2010	2024-03-01	19473
Audi	A6 allroad c6	3.0 TDI Quattro	Kombi	Allrad	Diesel	171	233	May 2006	Oct 2008	2024-03-01	19474
Audi	A6 allroad c6	2.7 TDI Quattro	Kombi	Allrad	Diesel	132	180	Mar 2006	Oct 2008	2024-03-01	19475
Audi	A6 c6	4.2 FSI Quattro	Stufenheck	Allrad	Benzin	257	350	Jun 2006	Mar 2011	2024-03-01	19476
Audi	A6 c6	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	171	233	Jun 2006	Oct 2008	2024-03-01	19477
Audi	A6 c6 avant	4.2 FSI Quattro	Kombi	Allrad	Benzin	257	350	Jun 2006	Aug 2011	2024-03-01	19478
Audi	A6 c6 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	171	233	Jun 2006	Oct 2008	2024-03-01	19479
Fiat	Stilo	1.9 JTD	Schrägheck	Frontantrieb	Diesel	93	126	Sep 2003	Nov 2006	2024-03-01	19480
Fiat	Stilo	1.9 JTD	Kombi	Frontantrieb	Diesel	93	126	Sep 2003	Aug 2008	2024-03-01	19481
VW	Passat b6	3.2 FSI 4motion	Stufenheck	Allrad	Benzin	184	250	Nov 2005	Jul 2010	2024-03-01	19485
VW	Passat b6 variant	3.2 FSI 4motion	Kombi	Allrad	Benzin	184	250	Nov 2005	Nov 2010	2024-03-01	19486
Audi	A4 b7	2.0 Tfsi 16V	Cabriolet	Frontantrieb	Benzin	147	200	Jan 2006	Mar 2009	2024-03-01	19487
Audi	A4 b7	2.7 TDI	Cabriolet	Frontantrieb	Diesel	132	180	Jun 2006	Mar 2009	2024-03-01	19488
Audi	A4 b7	RS4 Quattro	Cabriolet	Allrad	Benzin	309	420	Feb 2006	Dec 2008	2024-03-01	19489
Audi	A4 b7 avant	RS4 Quattro	Kombi	Allrad	Benzin	309	420	Sep 2005	Jun 2008	2024-03-01	19490
Chevrolet	Corvette	Z06 7.0	Coupe	Heckantrieb	Benzin	377	512	Mar 2006	Aug 2013	2024-03-01	19491
Chevrolet	Corvette	6	Cabriolet	Heckantrieb	Benzin	298	405	Sep 2004	Aug 2013	2024-03-01	19492
Opel	Antara a	2.4	SUV	Allrad	Benzin	104	141	Aug 2006	Dec 2011	2024-03-01	19493
Renault	19 i chamade	1.8 16V	Stufenheck	Frontantrieb	Benzin	101	137	Jun 1989	Aug 1990	2025-12-01	19494
Opel	Antara a	2.0 Cdti 4X4	SUV	Allrad	Diesel	110	150	Aug 2006	Dec 2011	2024-03-01	19495
BMW	3	320 SI	Stufenheck	Heckantrieb	Benzin	127	173	Sep 2005	Aug 2006	2024-03-01	19496
Mercedes-benz	R-Klasse	R 280 CDI 4-matic	Großraumlimousine	Allrad	Diesel	140	190	May 2006	Dec 2012	2024-03-01	19497
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	125	170	May 2006	Dec 2012	2024-03-01	19499
Chevrolet	Aveo / kalos	1.2	Stufenheck	Frontantrieb	Benzin	53	72	Mar 2005	Dec 2007	2024-03-01	19500
Chevrolet	Aveo / kalos	1.4	Stufenheck	Frontantrieb	Benzin	69	94	Mar 2005	May 2013	2024-03-01	19501
LDV	Maxus	2.5 D	Bus	Frontantrieb	Diesel	70	95	Feb 2005	Dec 2008	2024-03-01	19502
LDV	Maxus	2.5 D	Bus	Frontantrieb	Diesel	88	120	Feb 2005	Dec 2009	2024-03-01	19503
LDV	Maxus	2.5 D	Kasten	Frontantrieb	Diesel	70	95	Feb 2005	Dec 2008	2024-03-01	19504
KIA	Sorento i	2.5 Crdi	SUV	Allrad	Diesel	125	170	Dec 2006	Dec 2011	2024-03-01	19506
KIA	Carnival / grand iii	2.7 V6	Großraumlimousine	Frontantrieb	Benzin	139	189	Jun 2006	Jun 2015	2024-05-01	19507
KIA	Carnival / grand iii	2.9 Crdi	Großraumlimousine	Frontantrieb	Diesel	136	185	Apr 2006	Jun 2015	2024-05-01	19508
Renault	Trafic ii	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	88	120	Mar 2001	Oct 2006	2024-03-01	19512
Renault	Trafic ii	1.9 DCI 80	Pritsche/Fahrgestell	Frontantrieb	Diesel	60	82	Mar 2001	Oct 2006	2024-03-01	19513
Renault	Trafic ii	1.9 DCI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Mar 2001	Oct 2006	2024-03-01	19514
Renault	Trafic ii	2.5 DCI 135	Pritsche/Fahrgestell	Frontantrieb	Diesel	99	135	Mar 2001	Oct 2006	2024-03-01	19515
Fiat	Sedici	1.9 D Multijet 4X4	SUV	Allrad	Diesel	88	120	Jun 2006	Oct 2011	2024-03-01	19516
Fiat	Sedici	1.6 16V 4X4	SUV	Allrad	Benzin	79	107	Jun 2006	Oct 2014	2024-03-01	19517
Peugeot	Partner	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 2005	Dec 2015	2024-03-01	19518
Ford	Focus ii	1.6	Cabriolet	Frontantrieb	Benzin	74	100	Oct 2006	Sep 2010	2024-03-01	19519
Ford	Focus ii	2	Cabriolet	Frontantrieb	Benzin	107	145	Oct 2006	Sep 2010	2024-03-01	19520
Peugeot	Partner	1.6 HDI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Aug 2005	Jul 2008	2024-03-01	19521
Ford	Focus ii	2.0 Tdci	Cabriolet	Frontantrieb	Diesel	100	136	Oct 2006	Sep 2010	2024-03-01	19522
Peugeot	Partner	1.6 HDI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Aug 2005	Dec 2011	2025-06-01	19523
Peugeot	Partner	1.6 HDI 90	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 2005	Dec 2015	2024-03-01	19524
Peugeot	607	2.2 HDI	Stufenheck	Frontantrieb	Diesel	125	170	May 2006	Jun 2010	2024-03-01	19525
Lancia	Phedra	2.0 JTD	Großraumlimousine	Frontantrieb	Diesel	88	120	Jun 2006	Nov 2010	2024-03-01	19526
Ferrari	599 gtb/gto	6.0 GTB	Coupe	Heckantrieb	Benzin	456	620	Jun 2006	-	2024-03-01	19528
Porsche	911	3.6 GT3	Coupe	Heckantrieb	Benzin	305	415	Mar 2006	Dec 2009	2024-03-01	19545
Porsche	Cayman	2.7	Coupe	Heckantrieb	Benzin	180	245	Jul 2006	Dec 2009	2024-03-01	19546
Suzuki	Sx4 / classic	1.6 VVT 4X4	Schrägheck	Allrad	Benzin	79	107	Jun 2006	-	2024-03-01	19547
Suzuki	Sx4 / classic	1.9 Ddis 4X4	Schrägheck	Allrad	Diesel	88	120	Jun 2006	-	2024-03-01	19548
Suzuki	Sx4 / classic	1.5	Schrägheck	Frontantrieb	Benzin	73	99	Jun 2006	Jul 2010	2024-03-01	19549
Suzuki	Sx4 / classic	1.6 VVT	Schrägheck	Frontantrieb	Benzin	79	107	Jun 2006	-	2024-03-01	19550
Suzuki	Sx4 / classic	1.9 Ddis	Schrägheck	Frontantrieb	Diesel	88	120	Jun 2006	-	2024-03-01	19551
Alfa Romeo	Spider	2.2 JTS	Cabriolet	Frontantrieb	Benzin	136	185	Mar 2006	Mar 2011	2024-03-01	19552
Alfa Romeo	Spider	3.2 JTS Q4	Cabriolet	Allrad	Benzin	191	260	Mar 2006	Mar 2011	2024-03-01	19553
Renault	Vel satis	2.0 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Aug 2005	Aug 2009	2025-12-01	19554
Renault	Vel satis	2.0 DCI	Schrägheck	Frontantrieb	Diesel	127	173	Jan 2006	Aug 2009	2025-12-01	19555
Renault	Vel satis	3.0 DCI	Schrägheck	Frontantrieb	Diesel	133	181	Jun 2006	Aug 2009	2024-03-01	19556
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Mar 2006	May 2010	2024-05-01	19557
Seat	Altea	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	147	200	Apr 2006	May 2009	2024-03-01	19558
Nissan	350z	3.5	Coupe	Heckantrieb	Benzin	221	301	Sep 2002	Dec 2008	2024-03-01	19559
Jeep	Commander	3.0 CRD 4X4	SUV	Allrad	Diesel	160	218	Apr 2006	Dec 2010	2024-03-01	19560
Volvo	C70 ii	2.4	Cabriolet	Frontantrieb	Benzin	103	140	Mar 2006	Oct 2009	2024-03-01	19561
Volvo	C70 ii	2.4 I	Cabriolet	Frontantrieb	Benzin	125	170	Mar 2006	Oct 2009	2024-03-01	19562
Volvo	C70 ii	T5	Cabriolet	Frontantrieb	Benzin	162	220	Mar 2006	Feb 2007	2024-03-01	19563
Volvo	C70 ii	D5	Cabriolet	Frontantrieb	Diesel	132	180	Mar 2006	Jun 2013	2024-03-01	19564
Volvo	S60 i	D5	Stufenheck	Frontantrieb	Diesel	136	185	Mar 2005	Apr 2010	2024-03-01	19565
Volvo	S60 i	2.4 D	Stufenheck	Frontantrieb	Diesel	93	126	Mar 2005	Apr 2010	2024-03-01	19566
BMW	3	335 I	Coupe	Heckantrieb	Benzin	225	306	Jun 2006	Jun 2013	2024-03-01	19567
Peugeot	407	2.2 HDI 170	Stufenheck	Frontantrieb	Diesel	125	170	Mar 2006	Dec 2010	2024-03-01	19568
Ssangyong	Musso	2.9 D 4X4	Pick-up	Allrad	Diesel	88	120	Aug 2004	-	2024-03-01	19569
Ford	Transit tourneo	2.2 Tdci	Bus	Frontantrieb	Diesel	81	110	Jul 2006	Aug 2014	2024-03-01	19570
Ford	Transit tourneo	2.2 Tdci	Bus	Frontantrieb	Diesel	96	131	Jul 2006	Aug 2014	2024-03-01	19571
Ford	Transit	2.4 Tdci	Bus	Heckantrieb	Diesel	85	115	Apr 2006	Aug 2014	2024-03-01	19572
Ford	Transit	2.4 Tdci	Bus	Heckantrieb	Diesel	103	140	Apr 2006	Aug 2014	2024-03-01	19573
Ford	Transit	2.2 Tdci	Kasten	Frontantrieb	Diesel	81	110	Apr 2006	Aug 2014	2024-03-01	19574
Ford	Transit	2.2 Tdci	Kasten	Frontantrieb	Diesel	96	130	Apr 2006	Aug 2014	2024-03-01	19575
Ford	Transit	2.4 Tdci RWD	Kasten	Heckantrieb	Diesel	85	115	Apr 2006	Aug 2014	2024-03-01	19576
Ford	Transit	2.4 Tdci RWD	Kasten	Heckantrieb	Diesel	103	140	Apr 2006	Aug 2014	2024-03-01	19577
Citroën	Jumper iii	2.2 HDI 100	Bus	Frontantrieb	Diesel	74	101	Apr 2006	-	2025-12-01	19578
Citroën	Jumper iii	2.2 HDI 120	Bus	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2025-12-01	19579
Citroën	Jumper iii	3.0 HDI 160	Bus	Frontantrieb	Diesel	116	157	Sep 2006	-	2025-12-01	19580
Citroën	Jumper iii	2.2 HDI 100	Kasten	Frontantrieb	Diesel	74	101	Apr 2006	Dec 2012	2025-12-01	19581


--- Round 1 / 首次发送 ---
## 更新点

* 首轮闭合 13 个尺寸组，覆盖 18 个输入 Ktype、形成 24 条 READY 映射。
* Audi S6 Avant、A6 allroad、A6 Sedan 与 A6 Avant 在 2008 年改款前后存在长度或高度变化，因此拆分 `prefl` 与 `facelift`；未按发动机差异重复建组。([汽车数据网][1])
* Golf V 的三门与五门属于不同物理分支，因此拆分派生 `id`；两者三维均为 `4204 × 1759 × 1485 mm`，共用同一尺寸组。页面同时单列含后视镜宽度 `2010 mm`，本表采用不含后视镜的 `1759 mm`。([汽车数据网][2])
* Golf Plus 2008 年改款前后尺寸未变化，三个发动机 Ktype 直接复用同一尺寸组。
* Alfa Romeo 159 两个动力版本、Audi S8 D3 改款前后均未发现需要拆分的物理外廓变化。

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：18
* READY 映射：24
* PENDING／尚未闭合输入 Ktype：82
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19457_prefl	19457	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-S6-PREFL-01	HIGH	2008改款前S6 Avant外廓。	READY
19457_facelift	19457	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	HIGH	2008改款后S6 Avant外廓。	READY
19460	19460	Sedan	A8 D3		4	EU-AUDI-A8-D3-SEDAN-S8-01	HIGH	S8标准轴距四门车身。	READY
19464	19464	Hatchback	Astra H	L08	3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-01	HIGH	L08三门GTC外廓。	READY
19465	19465	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19466	19466	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19467	19467	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19468_3dr	19468	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1三门物理分支。	READY
19468_5dr	19468	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1五门物理分支。	READY
19469_3dr	19469	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1三门物理分支。	READY
19469_5dr	19469	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1五门物理分支。	READY
19470	19470	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
19471	19471	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
19472	19472	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19473_prefl	19473	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19473_facelift	19473	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH	2008改款后Allroad外廓。	READY
19474	19474	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19475	19475	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19476_prefl	19476	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-PREFL-01	HIGH	2008改款前四门外廓。	READY
19476_facelift	19476	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH	2008改款后四门外廓。	READY
19477	19477	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-PREFL-01	HIGH	改款前233马力版本外廓。	READY
19478_prefl	19478	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-PREFL-01	HIGH	2008改款前Avant外廓。	READY
19478_facelift	19478	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH	2008改款后Avant外廓。	READY
19479	19479	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-PREFL-01	HIGH	改款前233马力Avant外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453	Auto-Data Audi S6 Avant 4F C6	https://www.auto-data.net/en/audi-s6-avant-4f-c6-generation-1104
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446	Auto-Data Audi S6 Avant 4F C6 facelift	https://www.auto-data.net/en/audi-s6-avant-4f-c6-facelift-2008-generation-5240
EU-AUDI-A8-D3-SEDAN-S8-01	5062	1897	1424	Auto-Data Audi S8 D3;Auto-Data Audi S8 D3 facelift	https://www.auto-data.net/en/audi-s8-d3-generation-1126;https://www.auto-data.net/en/audi-s8-d3-facelift-2007-generation-5245
EU-OPEL-ASTRA-H-HATCHBACK-GTC-01	4290	1753	1435	Auto-Data Opel Astra H GTC;Auto-Data Opel Astra H GTC facelift	https://www.auto-data.net/en/opel-astra-h-gtc-1.9-cdti-150hp-2382;https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.9-cdti-ecotec-120hp-automatic-47425
EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	4204	1759	1592	Auto-Data Volkswagen Golf V Plus;Auto-Data Volkswagen Golf VI Plus	https://www.auto-data.net/en/volkswagen-golf-v-plus-1.4-80hp-16801;https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-80hp-17901
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door;Auto-Data Volkswagen Golf V 5-door	https://www.auto-data.net/en/volkswagen-golf-v-3-door-1.4-16v-80hp-8616;https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.4-16v-75hp-51655
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1422	Auto-Data Alfa Romeo 159 1.9 JTDM;Automobile-Catalog Alfa Romeo 159 1.9 JTDM	https://www.auto-data.net/en/alfa-romeo-159-1.9-jtdm-8v-120hp-1538;https://www.automobile-catalog.com/car/2008/1184810/alfa_romeo_159_1_9_jtdm_16v.html
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519	Auto-Data Audi A6 allroad 4F C6	https://www.auto-data.net/en/audi-a6-allroad-4f-c6-generation-5221
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521	Auto-Data Audi A6 allroad 4F C6 facelift	https://www.auto-data.net/en/audi-a6-allroad-4f-c6-facelift-2008-generation-5222
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459	Auto-Data Audi A6 4F C6	https://www.auto-data.net/en/audi-a6-4f-c6-generation-1115
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459	Auto-Data Audi A6 4F C6 facelift	https://www.auto-data.net/en/audi-a6-4f-c6-facelift-2008-generation-4369
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463	Auto-Data Audi A6 Avant 4F C6	https://www.auto-data.net/en/audi-a6-avant-4f-c6-generation-1116
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463	Auto-Data Audi A6 Avant 4F C6 facelift	https://www.auto-data.net/en/audi-a6-avant-4f-c6-facelift-2008-generation-4368
```

## 下一步优先处理

1. 闭合 Skoda Octavia II RS 掀背与旅行版的改款前后尺寸，确认 Ktype `19458`、`19459` 是否需要派生。
2. 批量处理 Ford Sierra 三种车身、Fiat Stilo 两种车身及 Passat B6 Sedan／Variant。
3. 随后处理 Audi A4 B7 Cabriolet／RS4、Corvette C6、Antara、BMW E90 等乘用车聚类。
4. 最后集中拆解 Trafic、Maxus、Transit、Jumper 的轴距、车顶高度及客车／厢式车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s6-avant-4f-c6-generation-1104?utm_source=chatgpt.com "Audi S6 Avant (4F,C6) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.4-16v-75hp-51655 "Volkswagen Golf V (5-door) 1.4 16V (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增完成 17 个输入 Ktype，形成 20 条 READY 映射；首次创建 18 个尺寸组。既有 13 个尺寸组未重复输出或核对。
* Octavia II RS 的掀背版和旅行版均按 2009 年改款前后拆分；改款导致长度或高度变化，不能合并为一个尺寸组。([汽车数据网][1])
* Fiat Stilo 掀背 Ktype 按三门、五门拆分，Multi Wagon 独立建组；三个车身外廓不同。([汽车目录][2])
* RS4 B7 Cabriolet 按宽体外廓独立于普通 A4 B7 Cabriolet 建组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：35
* READY 映射：44
* PENDING 输入 Ktype：65
* 已确认尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19458_prefl	19458	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	HIGH	2009改款前RS五门外廓。	READY
19458_facelift	19458	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	HIGH	2009改款后RS五门外廓。	READY
19459_prefl	19459	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	HIGH	2009改款前RS旅行版外廓。	READY
19459_facelift	19459	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	HIGH	2009改款后RS旅行版外廓。	READY
19480_3dr	19480	Hatchback	Stilo I	192	3	EU-FIAT-STILO-I-HATCHBACK-3D-01	MEDIUM	该Ktype覆盖三门物理分支。	READY
19480_5dr	19480	Hatchback	Stilo I	192	5	EU-FIAT-STILO-I-HATCHBACK-5D-01	MEDIUM	该Ktype覆盖五门物理分支。	READY
19481	19481	Wagon	Stilo I	192	5	EU-FIAT-STILO-I-WAGON-01	HIGH	Multi Wagon五门外廓。	READY
19485	19485	Sedan	Passat B6	3C2	4	EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	HIGH	3C2四门轿车外廓。	READY
19486	19486	Wagon	Passat B6	3C5	5	EU-VOLKSWAGEN-PASSAT-B6-WAGON-01	HIGH	3C5五门旅行版外廓。	READY
19487	19487	Convertible	A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	普通A4 B7双门敞篷外廓。	READY
19488	19488	Convertible	A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	普通A4 B7双门敞篷外廓。	READY
19489	19489	Convertible	RS4 B7	8HE	2	EU-AUDI-RS4-B7-CONVERTIBLE-01	HIGH	RS4宽体双门敞篷外廓。	READY
19490	19490	Wagon	RS4 B7	8ED	5	EU-AUDI-RS4-B7-WAGON-01	HIGH	RS4宽体五门旅行版外廓。	READY
19491	19491	Coupe	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	HIGH	Z06宽体双门硬顶外廓。	READY
19492	19492	Convertible	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	HIGH	C6双门敞篷外廓。	READY
19493	19493	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07五门SUV外廓。	READY
19494	19494	Sedan	Renault 19 I Chamade	L53	4	EU-RENAULT-19-I-SEDAN-01	MEDIUM	L53四门轿车外廓。	READY
19495	19495	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07五门SUV外廓。	READY
19496	19496	Sedan	3 Series E90	E90	4	EU-BMW-3-SERIES-E90-SEDAN-01	HIGH	E90四门轿车外廓。	READY
19499	19499	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FR-01	HIGH	1P1五门FR外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462	Auto-Data Skoda Octavia II RS 2.0 TFSI	https://www.auto-data.net/en/skoda-octavia-ii-rs-2.0-tfsi-200hp-14218
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift RS 2.0 TSI	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-rs-2.0-tsi-200hp-14193
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi RS 2.0 TFSI	https://www.auto-data.net/en/skoda-octavia-ii-combi-rs-2.0-tfsi-200hp-14233
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451	Auto-Data Skoda Octavia II Combi facelift RS 2.0 TSI	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-rs-2.0-tsi-200hp-55851
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475	UltimateSpecs Fiat Stilo 3-door	https://www.ultimatespecs.com/car-specs/Fiat/44738/Fiat-Stilo-3-door-19-JTD-80HP.html
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525	Automobile-Catalog Fiat Stilo 5-Porte	https://www.automobile-catalog.com/car/2005/725375/fiat_stilo_5-porte_1_9_jtd_140_dynamic.html
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570	UltimateSpecs Fiat Stilo MultiWagon	https://www.ultimatespecs.com/car-specs/Fiat/49146/Fiat-Stilo-MultiWagon-19-JTD-115HP-Dynamic.html
EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 3.2 V6 FSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-b6-3.2-v6-fsi-250hp-4motion-8887
EU-VOLKSWAGEN-PASSAT-B6-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 3.2 FSI 4WD	https://www.auto-data.net/en/volkswagen-passat-variant-b6-3.2-i-v6-24v-fsi-4wd-250hp-8903
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391	Auto-Data Audi A4 Cabriolet B7 2.0 TFSI	https://www.auto-data.net/en/audi-a4-cabriolet-b7-8h-2.0-tfsi-200hp-4293
EU-AUDI-RS4-B7-CONVERTIBLE-01	4555	1814	1391	Automobile-Catalog Audi RS4 Cabriolet	https://www.automobile-catalog.com/car/2007/249065/audi_rs4_cabriolet.html
EU-AUDI-RS4-B7-WAGON-01	4586	1816	1415	Auto-Data Audi RS4 Avant B7	https://www.auto-data.net/en/audi-rs4-avant-8e-b7-4.2-fsi-v8-32v-420hp-quattro-4531
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237	Auto-Data Chevrolet Corvette C6 Z06	https://www.auto-data.net/en/chevrolet-corvette-coupe-c6-z06-7.0-i-v8-505hp-14521
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246	Auto-Data Chevrolet Corvette C6 Convertible	https://www.auto-data.net/en/chevrolet-corvette-convertible-c6-6.0-i-v8-405hp-14524
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704	Auto-Data Opel Antara 2.0 CDTI 4x4	https://www.auto-data.net/en/opel-antara-2.0-cdti-150hp-4x4-57413
EU-RENAULT-19-I-SEDAN-01	4262	1694	1412	Auto-Data Renault 19 I Chamade L53	https://www.auto-data.net/en/renault-19-i-chamade-l53-1.7-l53c-90hp-10790
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421	Auto-Data BMW 3 Series E90 320si	https://www.auto-data.net/en/bmw-3-series-sedan-e90-320si-173hp-45533
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458	Auto-Data Seat Leon II 1P FR 2.0 TDI	https://www.auto-data.net/en/seat-leon-ii-1p-fr-2.0-tdi-170hp-dpf-13606
```

## 下一步优先处理

1. 闭合 Ford Sierra 掀背、轿车、旅行版三个车身簇。
2. 处理 Focus II Cabriolet、Volvo C70 II、Alfa Romeo Spider 等可批量复用的敞篷车簇。
3. 单独解决 R-Class 的 SWB／LWB 边界，以及 Aveo／Kalos 的 T200／T250 边界。
4. 最后集中拆解 Maxus、Trafic、Transit、Jumper 的轴距、车顶和客车／厢式车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-rs-2.0-tsi-200hp-55851 "Skoda Octavia II Combi (facelift 2009) RS 2.0 TSI (200 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2005/725375/fiat_stilo_5-porte_1_9_jtd_140_dynamic.html?utm_source=chatgpt.com "2005 Fiat Stilo 5-Porte 1.9 JTD 140 Dynamic (man. 6)"
[3]: https://www.automobile-catalog.com/car/2007/249065/audi_rs4_cabriolet.html?utm_source=chatgpt.com "2007 Audi RS4 Cabriolet Specs Review (309 kW / 420 PS / ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 29 条 `READY` 映射，覆盖 27 个输入 Ktype；首次创建 15 个尺寸组，既有尺寸组未重复输出。
* Seat Altea `19557` 覆盖改款前后两种外廓，三维分别为 `4325×1768×1568` 和 `4282×1768×1576`，因此拆分；`19558` 的 200 马力 TFSI 仅关联改款前分支。([汽车数据网][1])
* BMW 335i Coupe `19567` 同时覆盖 E92 改款前后，长度由 `4580 mm` 变为 `4612 mm`，因此拆分两个尺寸组。([汽车数据网][2])
* Focus II Coupe-Cabriolet 的三种动力共用同一外廓；Volvo C70、S60 采用官方规格中明确区别于含后视镜宽度的车身宽度。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：62
* READY 映射：73
* PENDING 输入 Ktype：38
* 已确认尺寸组：46
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19497	19497	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-SWB-01	HIGH	标准轴距W251五门车身。	READY
19516	19516	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	HIGH	五门四驱外廓。	READY
19517	19517	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	HIGH	五门四驱外廓。	READY
19519	19519	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19520	19520	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19522	19522	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19547	19547	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	HIGH	五门四驱外廓。	READY
19548	19548	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	HIGH	五门四驱外廓。	READY
19549	19549	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19550	19550	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19551	19551	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19552	19552	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
19553	19553	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
19554	19554	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19555	19555	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19556	19556	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19557_prefl	19557	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	HIGH	2009改款前FR外廓。	READY
19557_facelift	19557	MPV	Altea I facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19558	19558	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	HIGH	200马力FR改款前外廓。	READY
19559	19559	Coupe	350Z Z33	Z33	2	EU-NISSAN-350Z-Z33-COUPE-01	HIGH	Z33双门轿跑外廓。	READY
19560	19560	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-01	HIGH	XK五门SUV外廓。	READY
19561	19561	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19562	19562	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19563	19563	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19564	19564	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	MEDIUM	180马力D5对应改款前外廓。	READY
19565	19565	Sedan	S60 I facelift		4	EU-VOLVO-S60-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19566	19566	Sedan	S60 I facelift		4	EU-VOLVO-S60-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19567_prefl	19567	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-PREFL-01	HIGH	E92改款前双门轿跑外廓。	READY
19567_facelift	19567	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	HIGH	E92改款后双门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-SWB-01	4922	1922	1659	Auto-Data Mercedes-Benz R-Class W251 R 280 CDI 4MATIC	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-cdi-v6-190hp-4matic-g-tronic-37169
EU-FIAT-SEDICI-I-SUV-4X4-01	4115	1755	1620	Automobile-Catalog Fiat Sedici 4x4 1.6 16V	https://www.automobile-catalog.com/car/2006/728450/fiat_sedici_4x4_1_6_16v_emotion.html
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448	Auto-Data Ford Focus Cabriolet II 2.0 TDCi	https://www.auto-data.net/en/ford-focus-cabriolet-ii-2.0-tdci-136hp-7341
EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	4140	1755	1620	Global Suzuki SX4 official launch specifications	https://www.globalsuzuki.com/globalnews/2006/0228b.html
EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	4100	1730	1565	Global Suzuki SX4 official launch specifications	https://www.globalsuzuki.com/globalnews/2006/0228b.html
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Auto-Data Alfa Romeo Spider 939 2.2 JTS	https://www.auto-data.net/en/alfa-romeo-spider-939-2.2-jts-185hp-1437
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577	Automobile-Catalog Renault Vel Satis dCi 150	https://www.automobile-catalog.com/car/2006/2949875/renault_vel_satis_dci_150.html
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568	Auto-Data Seat Altea 5P FR 2.0 TDI	https://www.auto-data.net/en/seat-altea-5p-fr-2.0-tdi-170hp-dpf-13585
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Automobile-Catalog Seat Altea 2.0 TDI CR 170	https://www.automobile-catalog.com/car/2010/3082340/seat_altea_2_0_tdi_cr_170.html
EU-NISSAN-350Z-Z33-COUPE-01	4313	1815	1326	Automobile-Catalog Nissan 350Z Grand Touring	https://www.automobile-catalog.com/car/2006/2188805/nissan_350_z_grand_touring.html
EU-JEEP-COMMANDER-XK-SUV-01	4787	1899	1826	Automobile-Catalog Jeep Commander 3.0 CRD	https://www.automobile-catalog.com/car/2006/1327730/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	4582	1820	1400	Volvo C70 Model Year 2007 official specifications	https://www.volvoclub.org.uk/press/volvo2007uk/C70_2007_AllNew_Fullprod_spec.pdf
EU-VOLVO-S60-I-FACELIFT-SEDAN-01	4603	1813	1428	Volvo S60 Model Year 2007 official specifications	https://www.volvoclub.org.uk/press/volvo2007uk/S60_2007_Fullprod_spec.pdf
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395	Auto-Data BMW 335i Coupe E92	https://www.auto-data.net/en/bmw-3-series-coupe-e92-335i-306hp-9958
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data BMW 335i Coupe E92 LCI	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-335i-306hp-17230
```

## 下一步优先处理

1. 解决 Ford Sierra 1991–1993 后期保险杠尺寸与通用代际尺寸之间的冲突，再闭合掀背、轿车和旅行版。
2. 批量关闭 Aveo、Sorento、Carnival、Partner、607、Phedra、Ferrari、Porsche、407 和 Musso。
3. 最后集中拆解 Maxus、Trafic、Transit、Jumper 的轴距、车顶高度及客车／厢式车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-altea-5p-fr-2.0-tdi-170hp-dpf-13585 "Seat Altea (5P) FR 2.0 TDI (170 Hp) DPF | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-3-series-coupe-e92-335i-306hp-9958 "BMW 3 Series Coupe (E92) 335i (306 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/ford-focus-cabriolet-ii-2.0-tdci-136hp-7341 "Ford Focus Cabriolet II 2.0 TDCi (136 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮完成 11 个输入 Ktype，新增 13 条 READY 映射及 11 个尺寸组；既有尺寸组未重复核对或输出。
* Kia Carnival II 按短轴改款前、短轴改款后及 Grand 长轴三种物理外廓拆分；发动机差异未单独建组。([汽车数据网][1])
* Aveo／Kalos T200 的两个发动机 Ktype 共用四门轿车尺寸组；Sorento、607、Phedra、Ferrari 599、两款 Porsche 及 Musso Sports 分别完成建组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：73
* READY 映射：86
* PENDING 输入 Ktype：27
* 已确认尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19500	19500	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	MEDIUM	T200四门轿车外廓。	READY
19501	19501	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH	T200四门轿车外廓。	READY
19506	19506	SUV	Sorento I facelift	BL	5	EU-KIA-SORENTO-I-FACELIFT-SUV-01	HIGH	BL改款后五门SUV外廓。	READY
19507_prefl	19507	MPV	Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	HIGH	短轴改款前五门外廓。	READY
19507_facelift	19507	MPV	Carnival II facelift	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-FACELIFT-01	HIGH	短轴改款后五门外廓。	READY
19508_swb	19508	MPV	Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	MEDIUM	短轴Carnival物理分支。	READY
19508_lwb	19508	MPV	Grand Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-LWB-01	HIGH	长轴Grand Carnival物理分支。	READY
19525	19525	Sedan	607 Phase II		4	EU-PEUGEOT-607-PHASE-II-SEDAN-01	HIGH	Phase II四门轿车外廓。	READY
19526	19526	MPV	Phedra I	179	5	EU-LANCIA-PHEDRA-I-MPV-01	HIGH	179五门MPV外廓。	READY
19528	19528	Coupe	599 GTB Fiorano	F141	2	EU-FERRARI-599-GTB-FIORANO-COUPE-01	HIGH	F141双门GTB外廓。	READY
19545	19545	Coupe	911 997	997	2	EU-PORSCHE-911-997-COUPE-GT3-01	HIGH	997 GT3双门外廓。	READY
19546	19546	Coupe	Cayman 987C	987C	2	EU-PORSCHE-CAYMAN-987C-COUPE-01	HIGH	987C双门轿跑外廓。	READY
19569	19569	Pickup	Musso Sports		4	EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	HIGH	四门双排座皮卡外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495	Auto-Data Chevrolet Aveo Sedan 1.4 i 16V	https://www.auto-data.net/en/chevrolet-aveo-sedan-1.4-i-16v-94hp-14429
EU-KIA-SORENTO-I-FACELIFT-SUV-01	4590	1865	1811	Auto-Data Kia Sorento I facelift 2006	https://www.auto-data.net/en/kia-sorento-i-facelift-2006-generation-595
EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	4810	1985	1815	Auto-Data Kia Carnival II VQ 2.7i V6	https://www.auto-data.net/en/kia-carnival-ii-vq-2.7i-v6-189hp-2741
EU-KIA-CARNIVAL-II-MPV-SWB-FACELIFT-01	4810	1985	1760	Auto-Data Kia Carnival II VQ facelift 2.7 V6	https://www.auto-data.net/en/kia-carnival-ii-vq-facelift-2010-2.7-v6-16v-189hp-automatic-17865
EU-KIA-CARNIVAL-II-MPV-LWB-01	5130	1985	1780	Auto-Data Kia Grand Carnival II 2.9 CRDi	https://www.auto-data.net/en/kia-grand-carnival-ii-2.9-crdi-185hp-automatic-34233
EU-PEUGEOT-607-PHASE-II-SEDAN-01	4902	1800	1442	Auto-Data Peugeot 607 Phase II 2.2 HDi	https://www.auto-data.net/en/peugeot-607-phase-ii-2004-2.2-hdi-170hp-28801
EU-LANCIA-PHEDRA-I-MPV-01	4750	1863	1760	Auto-Data Lancia Phedra 2.0 JTD	https://www.auto-data.net/en/lancia-phedra-2.0-jtd-107hp-4933
EU-FERRARI-599-GTB-FIORANO-COUPE-01	4666	1961	1336	Auto-Data Ferrari 599 GTB Fiorano 6.0 V12	https://www.auto-data.net/en/ferrari-599-gtb-fiorano-6.0-v12-620hp-41025
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280	Auto-Data Porsche 911 997 GT3 3.6	https://www.auto-data.net/en/porsche-911-997-gt3-3.6-415hp-6585
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305	Auto-Data Porsche Cayman 987C 2.7	https://www.auto-data.net/en/porsche-cayman-987c-2.7-245hp-40902
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	4935	1864	1760	Autoevolution SsangYong Musso Sports	https://www.autoevolution.com/cars/ssangyong-musso-sports-1998.html
```

## 下一步优先处理

1. 关闭 Peugeot 407 的改款前后分支，并解决标准高度的单值口径。
2. 处理 Ford Sierra 掀背、轿车和旅行版三个后期车身。
3. 批量拆分 Peugeot Partner 的乘用版与厢式版。
4. 集中处理 Maxus、Trafic、Transit、Jumper 的轴距、车顶高度及 Bus／Van 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-carnival-ii-vq-generation-6527?utm_source=chatgpt.com "Kia Carnival II (VQ) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/chevrolet-aveo-sedan-1.4-i-16v-94hp-14429?utm_source=chatgpt.com "Chevrolet Aveo Sedan 1.4 i 16V (94 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮完成 Ford Sierra 三种车身、Peugeot Partner I Phase II 四个 Ktype，以及 Peugeot 407 改款前后分支。
* Sierra 掀背、轿车、旅行版外廓分别为 `4458×1694×1407`、`4501×1698×1407`、`4544×1720×1488 mm`，不能合并。([汽车目录][1])
* Partner Combispace 与同代厢式车使用相同基础外廓，四个 Ktype 复用一个尺寸组；Ktype `19524` 的来源分类同时包含 Box Body/MPV，因此映射层按输入中的 Kasten 主类归为 Van。([百得欣][2])
* Peugeot 407 `19568` 跨越 2008 年改款，长度由 `4676 mm` 变为 `4691 mm`；两组宽度均采用明确不含后视镜的 `1811 mm`。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：81
* READY 映射：95
* PENDING 输入 Ktype：19
* 已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19461	19461	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-01	HIGH	后期五门掀背外廓。	READY
19462	19462	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH	Sapphire四门轿车外廓。	READY
19463	19463	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-01	HIGH	五门旅行版外廓。	READY
19518	19518	MPV	Partner I Phase II	5F		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5F乘用版外廓。	READY
19521	19521	MPV	Partner I Phase II	5F		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5F乘用版外廓。	READY
19523	19523	Van	Partner I Phase II	5	4	EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5系厢式车外廓。	READY
19524	19524	Van	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	5_/G_箱式与乘用版本共用外廓，按Van归类。	READY
19568_prefl	19568	Sedan	407 Phase I		4	EU-PEUGEOT-407-PHASE-I-SEDAN-01	HIGH	2008改款前四门外廓。	READY
19568_facelift	19568	Sedan	407 Phase II		4	EU-PEUGEOT-407-PHASE-II-SEDAN-01	HIGH	2008改款后四门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-II-HATCHBACK-5D-01	4458	1694	1407	Automobile-Catalog Ford Sierra 2.0i DOHC GLX	https://www.automobile-catalog.com/car/1992/935660/ford_sierra_2_0i_dohc_glx.html
EU-FORD-SIERRA-II-SEDAN-01	4501	1698	1407	Automobile-Catalog Ford Sierra Sapphire 2.0i DOHC GLS	https://www.automobile-catalog.com/car/1992/935525/ford_sierra_sapphire_2_0i_dohc_gls.html
EU-FORD-SIERRA-II-WAGON-01	4544	1720	1488	Automobile-Catalog Ford Sierra Estate 2.0i DOHC Ghia	https://www.automobile-catalog.com/car/1992/935600/ford_sierra_estate_2_0i_dohc_ghia.html
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II 1.6 HDi 75;Auto-Data Peugeot Partner I Phase II 1.6 HDi 90	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.6-hdi-75hp-5625;https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.6-hdi-90hp-5626
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455	Automobile-Catalog Peugeot 407 2.2 HDi FAP 170	https://www.automobile-catalog.com/car/2006/2619440/peugeot_407_2_2_hdi_170.html
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455	Automobile-Catalog Peugeot 407 Phase II 2.2 HDi FAP 170	https://www.automobile-catalog.com/car/2008/2619605/peugeot_407_2_2_hdi_170.html
```

## 下一步优先处理

1. 集中拆分 LDV Maxus 的客车、厢式车、轴距和车顶分支。
2. 处理 Renault Trafic II 底盘驾驶室的短轴、长轴边界。
3. 批量闭合 Ford Transit／Tourneo 的前驱、后驱、Bus、Van、轴距和车顶组合。
4. 最后处理 Citroën Jumper III Bus／Van 的轴距与车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1992/935660/ford_sierra_2_0i_dohc_glx.html?utm_source=chatgpt.com "1992 Ford Sierra 2.0i (DOHC) GLX (man. 5)"
[2]: https://www.bendix.co.id/catalogue/peugeot/partner/partner-box-body-mpv-5-g/16-hdi-90?id=19524&tab=Passenger&utm_source=chatgpt.com "PEUGEOT PARTNER Box Body/MPV (5_, G_) 1.6 HDi 90"
[3]: https://www.automobile-catalog.com/car/2008/2619605/peugeot_407_2_2_hdi_170.html?utm_source=chatgpt.com "2008 Peugeot 407 2.2 HDi FAP 170 Specs Review (125 kW / 170 PS / 168 hp) (since September 2008 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮完成 Ford Transit／Tourneo 8 个输入 Ktype，新增 38 条 READY 映射及 19 个尺寸组；既有尺寸组未重复核对或输出。
* Tourneo 为 SWB 低顶单一外廓；Transit Minibus 按 15 座 LWB 中顶、17 座 Jumbo 中顶和 Jumbo 高顶拆分。17 座 T430 使用双后轮外廓宽度。
* Transit 厢式车按前驱／后驱、SWB／MWB／LWB／Jumbo、车顶高度及 SRW／DRW 拆分；发动机功率差异未重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：89
* READY 映射：133
* PENDING 输入 Ktype：11
* 已确认尺寸组：82
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19570	19570	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH	SWB低顶Tourneo外廓。	READY
19571	19571	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH	SWB低顶Tourneo外廓。	READY
19572_15seat	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	HIGH	15座LWB中顶分支。	READY
19572_17seat_medroof	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	HIGH	17座Jumbo中顶双后轮分支。	READY
19572_17seat_highroof	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	HIGH	17座Jumbo高顶双后轮分支。	READY
19573_15seat	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	HIGH	15座LWB中顶分支。	READY
19573_17seat_medroof	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	HIGH	17座Jumbo中顶双后轮分支。	READY
19573_17seat_highroof	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	HIGH	17座Jumbo高顶双后轮分支。	READY
19574_swb_lowroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱SWB低顶分支。	READY
19574_swb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱SWB中顶分支。	READY
19574_mwb_lowroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	HIGH	前驱MWB低顶分支。	READY
19574_mwb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱MWB中顶分支。	READY
19574_mwb_highroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱MWB高顶分支。	READY
19574_lwb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱LWB中顶分支。	READY
19574_lwb_highroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱LWB高顶分支。	READY
19575_swb_lowroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱SWB低顶分支。	READY
19575_swb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱SWB中顶分支。	READY
19575_mwb_lowroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	HIGH	前驱MWB低顶分支。	READY
19575_mwb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱MWB中顶分支。	READY
19575_mwb_highroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱MWB高顶分支。	READY
19575_lwb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱LWB中顶分支。	READY
19575_lwb_highroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱LWB高顶分支。	READY
19576_swb_lowroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	HIGH	后驱SWB低顶分支。	READY
19576_swb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	HIGH	后驱SWB中顶分支。	READY
19576_mwb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	HIGH	后驱MWB中顶分支。	READY
19576_mwb_highroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	HIGH	后驱MWB高顶分支。	READY
19576_lwb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	HIGH	后驱LWB中顶分支。	READY
19576_lwb_highroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	HIGH	后驱LWB高顶分支。	READY
19576_jumbo_highroof_srw	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	HIGH	Jumbo高顶单后轮分支。	READY
19576_jumbo_highroof_drw	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	HIGH	Jumbo高顶双后轮分支。	READY
19577_swb_lowroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	HIGH	后驱SWB低顶分支。	READY
19577_swb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	HIGH	后驱SWB中顶分支。	READY
19577_mwb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	HIGH	后驱MWB中顶分支。	READY
19577_mwb_highroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	HIGH	后驱MWB高顶分支。	READY
19577_lwb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	HIGH	后驱LWB中顶分支。	READY
19577_lwb_highroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	HIGH	后驱LWB高顶分支。	READY
19577_jumbo_highroof_srw	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	HIGH	Jumbo高顶单后轮分支。	READY
19577_jumbo_highroof_drw	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	HIGH	Jumbo高顶双后轮分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	6403	2084	2380	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	6403	2084	2624	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	6403	2084	2629	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
```

## 下一步优先处理

1. 闭合 LDV Maxus Bus／Van 的 SWB、LWB、标准顶、高顶和超高顶分支。
2. 确认 Renault Trafic II `EL` 平台底盘的固定 LWB 驾驶室外廓，避免把后装货台尺寸混入尺寸组。
3. 最后一次性拆分 Citroën Jumper III Bus／Van 的 L1–L4 与 H1–H3 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已关闭剩余 11 个输入 Ktype：LDV Maxus、Renault Trafic II 平台驾驶室及 Citroën Jumper III。
* Maxus 按 SWB/LWB、标准顶/高顶/超高顶拆分；Trafic 平台驾驶室采用 LWB 基础外廓；Jumper 按官方车型范围拆分为 L1H1、L2H1、L2H2、L3H2、L4H2。([Anchor Vans][1])
* 已完成固定表头、唯一主键、映射引用闭合、尺寸及来源非空检查。
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射：157
* PENDING：0
* DIMENSION_GROUP：92
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19457_prefl	19457	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-S6-PREFL-01	HIGH	2008改款前S6 Avant外廓。	READY
19457_facelift	19457	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	HIGH	2008改款后S6 Avant外廓。	READY
19458_prefl	19458	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	HIGH	2009改款前RS五门外廓。	READY
19458_facelift	19458	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	HIGH	2009改款后RS五门外廓。	READY
19459_prefl	19459	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	HIGH	2009改款前RS旅行版外廓。	READY
19459_facelift	19459	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	HIGH	2009改款后RS旅行版外廓。	READY
19460	19460	Sedan	A8 D3		4	EU-AUDI-A8-D3-SEDAN-S8-01	HIGH	S8标准轴距四门车身。	READY
19461	19461	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-5D-01	HIGH	后期五门掀背外廓。	READY
19462	19462	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH	Sapphire四门轿车外廓。	READY
19463	19463	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-01	HIGH	五门旅行版外廓。	READY
19464	19464	Hatchback	Astra H	L08	3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-01	HIGH	L08三门GTC外廓。	READY
19465	19465	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19466	19466	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19467	19467	MPV	Golf Plus I		5	EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	HIGH	Golf Plus五门高顶车身。	READY
19468_3dr	19468	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1三门物理分支。	READY
19468_5dr	19468	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1五门物理分支。	READY
19469_3dr	19469	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1三门物理分支。	READY
19469_5dr	19469	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	MEDIUM	1K1五门物理分支。	READY
19470	19470	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
19471	19471	Sedan	159	939	4	EU-ALFA-ROMEO-159-SEDAN-01	HIGH	939四门轿车外廓。	READY
19472	19472	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19473_prefl	19473	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19473_facelift	19473	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	HIGH	2008改款后Allroad外廓。	READY
19474	19474	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19475	19475	Wagon	A6 C6	4FH	5	EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	HIGH	2008改款前Allroad外廓。	READY
19476_prefl	19476	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-PREFL-01	HIGH	2008改款前四门外廓。	READY
19476_facelift	19476	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-FACELIFT-01	HIGH	2008改款后四门外廓。	READY
19477	19477	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-PREFL-01	HIGH	改款前233马力版本外廓。	READY
19478_prefl	19478	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-PREFL-01	HIGH	2008改款前Avant外廓。	READY
19478_facelift	19478	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-FACELIFT-01	HIGH	2008改款后Avant外廓。	READY
19479	19479	Wagon	A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-PREFL-01	HIGH	改款前233马力Avant外廓。	READY
19480_3dr	19480	Hatchback	Stilo I	192	3	EU-FIAT-STILO-I-HATCHBACK-3D-01	MEDIUM	该Ktype覆盖三门物理分支。	READY
19480_5dr	19480	Hatchback	Stilo I	192	5	EU-FIAT-STILO-I-HATCHBACK-5D-01	MEDIUM	该Ktype覆盖五门物理分支。	READY
19481	19481	Wagon	Stilo I	192	5	EU-FIAT-STILO-I-WAGON-01	HIGH	Multi Wagon五门外廓。	READY
19485	19485	Sedan	Passat B6	3C2	4	EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	HIGH	3C2四门轿车外廓。	READY
19486	19486	Wagon	Passat B6	3C5	5	EU-VOLKSWAGEN-PASSAT-B6-WAGON-01	HIGH	3C5五门旅行版外廓。	READY
19487	19487	Convertible	A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	普通A4 B7双门敞篷外廓。	READY
19488	19488	Convertible	A4 B7	8HE	2	EU-AUDI-A4-B7-CONVERTIBLE-01	HIGH	普通A4 B7双门敞篷外廓。	READY
19489	19489	Convertible	RS4 B7	8HE	2	EU-AUDI-RS4-B7-CONVERTIBLE-01	HIGH	RS4宽体双门敞篷外廓。	READY
19490	19490	Wagon	RS4 B7	8ED	5	EU-AUDI-RS4-B7-WAGON-01	HIGH	RS4宽体五门旅行版外廓。	READY
19491	19491	Coupe	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	HIGH	Z06宽体双门硬顶外廓。	READY
19492	19492	Convertible	Corvette C6	C6	2	EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	HIGH	C6双门敞篷外廓。	READY
19493	19493	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07五门SUV外廓。	READY
19494	19494	Sedan	Renault 19 I Chamade	L53	4	EU-RENAULT-19-I-SEDAN-01	MEDIUM	L53四门轿车外廓。	READY
19495	19495	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	L07五门SUV外廓。	READY
19496	19496	Sedan	3 Series E90	E90	4	EU-BMW-3-SERIES-E90-SEDAN-01	HIGH	E90四门轿车外廓。	READY
19497	19497	MPV	R-Class W251	W251	5	EU-MERCEDES-BENZ-R-CLASS-W251-MPV-SWB-01	HIGH	标准轴距W251五门车身。	READY
19499	19499	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-FR-01	HIGH	1P1五门FR外廓。	READY
19500	19500	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	MEDIUM	T200四门轿车外廓。	READY
19501	19501	Sedan	Aveo/Kalos T200	T200	4	EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	HIGH	T200四门轿车外廓。	READY
19502_swb_highroof	19502	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶客车分支。	READY
19502_lwb_highroof	19502	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶客车分支。	READY
19502_lwb_xhighroof	19502	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-XHIGHROOF-01	MEDIUM	长轴超高顶17座客车分支。	READY
19503_swb_highroof	19503	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-SWB-HIGHROOF-01	MEDIUM	短轴高顶客车分支。	READY
19503_lwb_highroof	19503	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶客车分支。	READY
19503_lwb_xhighroof	19503	MPV	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-XHIGHROOF-01	HIGH	长轴超高顶17座客车分支。	READY
19504_swb_lowroof	19504	Van	Maxus I			EU-LDV-MAXUS-I-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车分支。	READY
19504_swb_highroof	19504	Van	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车分支。	READY
19504_lwb_highroof	19504	Van	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车分支。	READY
19504_lwb_xhighroof	19504	Van	Maxus I			EU-LDV-MAXUS-I-BUS-VAN-LWB-XHIGHROOF-01	HIGH	长轴超高顶厢式车分支。	READY
19506	19506	SUV	Sorento I facelift	BL	5	EU-KIA-SORENTO-I-FACELIFT-SUV-01	HIGH	BL改款后五门SUV外廓。	READY
19507_prefl	19507	MPV	Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	HIGH	短轴改款前五门外廓。	READY
19507_facelift	19507	MPV	Carnival II facelift	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-FACELIFT-01	HIGH	短轴改款后五门外廓。	READY
19508_swb	19508	MPV	Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	MEDIUM	短轴Carnival物理分支。	READY
19508_lwb	19508	MPV	Grand Carnival II	VQ	5	EU-KIA-CARNIVAL-II-MPV-LWB-01	HIGH	长轴Grand Carnival物理分支。	READY
19512	19512	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	HIGH	EL长轴平台驾驶室外廓。	READY
19513	19513	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	EL长轴平台驾驶室外廓。	READY
19514	19514	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	EL长轴平台驾驶室外廓。	READY
19515	19515	Pickup	Trafic II	EL	2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	MEDIUM	EL长轴平台驾驶室外廓。	READY
19516	19516	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	HIGH	五门四驱外廓。	READY
19517	19517	SUV	Sedici I		5	EU-FIAT-SEDICI-I-SUV-4X4-01	HIGH	五门四驱外廓。	READY
19518	19518	MPV	Partner I Phase II	5F		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5F乘用版外廓。	READY
19519	19519	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19520	19520	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19521	19521	MPV	Partner I Phase II	5F		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5F乘用版外廓。	READY
19522	19522	Convertible	Focus II Coupe-Cabriolet		2	EU-FORD-FOCUS-II-CONVERTIBLE-01	HIGH	双门硬顶敞篷外廓。	READY
19523	19523	Van	Partner I Phase II	5	4	EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	HIGH	5系厢式车外廓。	READY
19524	19524	Van	Partner I Phase II			EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	MEDIUM	5_/G_箱式与乘用版本共用外廓，按Van归类。	READY
19525	19525	Sedan	607 Phase II		4	EU-PEUGEOT-607-PHASE-II-SEDAN-01	HIGH	Phase II四门轿车外廓。	READY
19526	19526	MPV	Phedra I	179	5	EU-LANCIA-PHEDRA-I-MPV-01	HIGH	179五门MPV外廓。	READY
19528	19528	Coupe	599 GTB Fiorano	F141	2	EU-FERRARI-599-GTB-FIORANO-COUPE-01	HIGH	F141双门GTB外廓。	READY
19545	19545	Coupe	911 997	997	2	EU-PORSCHE-911-997-COUPE-GT3-01	HIGH	997 GT3双门外廓。	READY
19546	19546	Coupe	Cayman 987C	987C	2	EU-PORSCHE-CAYMAN-987C-COUPE-01	HIGH	987C双门轿跑外廓。	READY
19547	19547	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	HIGH	五门四驱外廓。	READY
19548	19548	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	HIGH	五门四驱外廓。	READY
19549	19549	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19550	19550	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19551	19551	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	HIGH	五门前驱外廓。	READY
19552	19552	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
19553	19553	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
19554	19554	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19555	19555	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19556	19556	Hatchback	Vel Satis I facelift		5	EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	HIGH	改款后五门掀背外廓。	READY
19557_prefl	19557	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	HIGH	2009改款前FR外廓。	READY
19557_facelift	19557	MPV	Altea I facelift	5P	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	2009改款后外廓。	READY
19558	19558	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	HIGH	200马力FR改款前外廓。	READY
19559	19559	Coupe	350Z Z33	Z33	2	EU-NISSAN-350Z-Z33-COUPE-01	HIGH	Z33双门轿跑外廓。	READY
19560	19560	SUV	Commander XK	XK	5	EU-JEEP-COMMANDER-XK-SUV-01	HIGH	XK五门SUV外廓。	READY
19561	19561	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19562	19562	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19563	19563	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH	第二代改款前硬顶敞篷外廓。	READY
19564	19564	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	MEDIUM	180马力D5对应改款前外廓。	READY
19565	19565	Sedan	S60 I facelift		4	EU-VOLVO-S60-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19566	19566	Sedan	S60 I facelift		4	EU-VOLVO-S60-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
19567_prefl	19567	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-PREFL-01	HIGH	E92改款前双门轿跑外廓。	READY
19567_facelift	19567	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	HIGH	E92改款后双门轿跑外廓。	READY
19568_prefl	19568	Sedan	407 Phase I		4	EU-PEUGEOT-407-PHASE-I-SEDAN-01	HIGH	2008改款前四门外廓。	READY
19568_facelift	19568	Sedan	407 Phase II		4	EU-PEUGEOT-407-PHASE-II-SEDAN-01	HIGH	2008改款后四门外廓。	READY
19569	19569	Pickup	Musso Sports		4	EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	HIGH	四门双排座皮卡外廓。	READY
19570	19570	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH	SWB低顶Tourneo外廓。	READY
19571	19571	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	HIGH	SWB低顶Tourneo外廓。	READY
19572_15seat	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	HIGH	15座LWB中顶分支。	READY
19572_17seat_medroof	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	HIGH	17座Jumbo中顶双后轮分支。	READY
19572_17seat_highroof	19572	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	HIGH	17座Jumbo高顶双后轮分支。	READY
19573_15seat	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	HIGH	15座LWB中顶分支。	READY
19573_17seat_medroof	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	HIGH	17座Jumbo中顶双后轮分支。	READY
19573_17seat_highroof	19573	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	HIGH	17座Jumbo高顶双后轮分支。	READY
19574_swb_lowroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱SWB低顶分支。	READY
19574_swb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱SWB中顶分支。	READY
19574_mwb_lowroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	HIGH	前驱MWB低顶分支。	READY
19574_mwb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱MWB中顶分支。	READY
19574_mwb_highroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱MWB高顶分支。	READY
19574_lwb_medroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱LWB中顶分支。	READY
19574_lwb_highroof	19574	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱LWB高顶分支。	READY
19575_swb_lowroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	HIGH	前驱SWB低顶分支。	READY
19575_swb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	HIGH	前驱SWB中顶分支。	READY
19575_mwb_lowroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	HIGH	前驱MWB低顶分支。	READY
19575_mwb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	HIGH	前驱MWB中顶分支。	READY
19575_mwb_highroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	HIGH	前驱MWB高顶分支。	READY
19575_lwb_medroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	HIGH	前驱LWB中顶分支。	READY
19575_lwb_highroof	19575	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	HIGH	前驱LWB高顶分支。	READY
19576_swb_lowroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	HIGH	后驱SWB低顶分支。	READY
19576_swb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	HIGH	后驱SWB中顶分支。	READY
19576_mwb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	HIGH	后驱MWB中顶分支。	READY
19576_mwb_highroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	HIGH	后驱MWB高顶分支。	READY
19576_lwb_medroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	HIGH	后驱LWB中顶分支。	READY
19576_lwb_highroof	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	HIGH	后驱LWB高顶分支。	READY
19576_jumbo_highroof_srw	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	HIGH	Jumbo高顶单后轮分支。	READY
19576_jumbo_highroof_drw	19576	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	HIGH	Jumbo高顶双后轮分支。	READY
19577_swb_lowroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	HIGH	后驱SWB低顶分支。	READY
19577_swb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	HIGH	后驱SWB中顶分支。	READY
19577_mwb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	HIGH	后驱MWB中顶分支。	READY
19577_mwb_highroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	HIGH	后驱MWB高顶分支。	READY
19577_lwb_medroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	HIGH	后驱LWB中顶分支。	READY
19577_lwb_highroof	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	HIGH	后驱LWB高顶分支。	READY
19577_jumbo_highroof_srw	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	HIGH	Jumbo高顶单后轮分支。	READY
19577_jumbo_highroof_drw	19577	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	HIGH	Jumbo高顶双后轮分支。	READY
19578_l1h1	19578	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L1H1-01	HIGH	L1H1客车分支。	READY
19579_l1h1	19579	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L1H1-01	HIGH	L1H1客车分支。	READY
19579_l2h1	19579	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L2H1-01	HIGH	L2H1客车分支。	READY
19579_l2h2	19579	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L2H2-01	HIGH	L2H2客车分支。	READY
19579_l3h2	19579	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L3H2-01	HIGH	L3H2客车分支。	READY
19580_l3h2	19580	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L3H2-01	HIGH	L3H2客车分支。	READY
19580_l4h2	19580	MPV	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L4H2-01	HIGH	L4H2客车分支。	READY
19581_l1h1	19581	Van	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L1H1-01	HIGH	L1H1厢式车分支。	READY
19581_l2h1	19581	Van	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L2H1-01	HIGH	L2H1厢式车分支。	READY
19581_l2h2	19581	Van	Jumper III			EU-CITROEN-JUMPER-III-BUS-VAN-L2H2-01	HIGH	L2H2厢式车分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453	Auto-Data Audi S6 Avant 4F C6	https://www.auto-data.net/en/audi-s6-avant-4f-c6-generation-1104
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446	Auto-Data Audi S6 Avant 4F C6 facelift	https://www.auto-data.net/en/audi-s6-avant-4f-c6-facelift-2008-generation-5240
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462	Auto-Data Skoda Octavia II RS 2.0 TFSI	https://www.auto-data.net/en/skoda-octavia-ii-rs-2.0-tfsi-200hp-14218
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462	Auto-Data Skoda Octavia II facelift RS 2.0 TSI	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-rs-2.0-tsi-200hp-14193
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi RS 2.0 TFSI	https://www.auto-data.net/en/skoda-octavia-ii-combi-rs-2.0-tfsi-200hp-14233
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451	Auto-Data Skoda Octavia II Combi facelift RS 2.0 TSI	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-rs-2.0-tsi-200hp-55851
EU-AUDI-A8-D3-SEDAN-S8-01	5062	1897	1424	Auto-Data Audi S8 D3;Auto-Data Audi S8 D3 facelift	https://www.auto-data.net/en/audi-s8-d3-generation-1126;https://www.auto-data.net/en/audi-s8-d3-facelift-2007-generation-5245
EU-FORD-SIERRA-II-HATCHBACK-5D-01	4458	1694	1407	Automobile-Catalog Ford Sierra 2.0i DOHC GLX	https://www.automobile-catalog.com/car/1992/935660/ford_sierra_2_0i_dohc_glx.html
EU-FORD-SIERRA-II-SEDAN-01	4501	1698	1407	Automobile-Catalog Ford Sierra Sapphire 2.0i DOHC GLS	https://www.automobile-catalog.com/car/1992/935525/ford_sierra_sapphire_2_0i_dohc_gls.html
EU-FORD-SIERRA-II-WAGON-01	4544	1720	1488	Automobile-Catalog Ford Sierra Estate 2.0i DOHC Ghia	https://www.automobile-catalog.com/car/1992/935600/ford_sierra_estate_2_0i_dohc_ghia.html
EU-OPEL-ASTRA-H-HATCHBACK-GTC-01	4290	1753	1435	Auto-Data Opel Astra H GTC;Auto-Data Opel Astra H GTC facelift	https://www.auto-data.net/en/opel-astra-h-gtc-1.9-cdti-150hp-2382;https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.9-cdti-ecotec-120hp-automatic-47425
EU-VOLKSWAGEN-GOLF-PLUS-V-MPV-01	4204	1759	1592	Auto-Data Volkswagen Golf V Plus;Auto-Data Volkswagen Golf VI Plus	https://www.auto-data.net/en/volkswagen-golf-v-plus-1.4-80hp-16801;https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-80hp-17901
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door;Auto-Data Volkswagen Golf V 5-door	https://www.auto-data.net/en/volkswagen-golf-v-3-door-1.4-16v-80hp-8616;https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.4-16v-75hp-51655
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1422	Auto-Data Alfa Romeo 159 1.9 JTDM;Automobile-Catalog Alfa Romeo 159 1.9 JTDM	https://www.auto-data.net/en/alfa-romeo-159-1.9-jtdm-8v-120hp-1538;https://www.automobile-catalog.com/car/2008/1184810/alfa_romeo_159_1_9_jtdm_16v.html
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519	Auto-Data Audi A6 allroad 4F C6	https://www.auto-data.net/en/audi-a6-allroad-4f-c6-generation-5221
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521	Auto-Data Audi A6 allroad 4F C6 facelift	https://www.auto-data.net/en/audi-a6-allroad-4f-c6-facelift-2008-generation-5222
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459	Auto-Data Audi A6 4F C6	https://www.auto-data.net/en/audi-a6-4f-c6-generation-1115
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459	Auto-Data Audi A6 4F C6 facelift	https://www.auto-data.net/en/audi-a6-4f-c6-facelift-2008-generation-4369
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463	Auto-Data Audi A6 Avant 4F C6	https://www.auto-data.net/en/audi-a6-avant-4f-c6-generation-1116
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463	Auto-Data Audi A6 Avant 4F C6 facelift	https://www.auto-data.net/en/audi-a6-avant-4f-c6-facelift-2008-generation-4368
EU-FIAT-STILO-I-HATCHBACK-3D-01	4182	1784	1475	UltimateSpecs Fiat Stilo 3-door	https://www.ultimatespecs.com/car-specs/Fiat/44738/Fiat-Stilo-3-door-19-JTD-80HP.html
EU-FIAT-STILO-I-HATCHBACK-5D-01	4253	1756	1525	Automobile-Catalog Fiat Stilo 5-Porte	https://www.automobile-catalog.com/car/2005/725375/fiat_stilo_5-porte_1_9_jtd_140_dynamic.html
EU-FIAT-STILO-I-WAGON-01	4516	1756	1570	UltimateSpecs Fiat Stilo MultiWagon	https://www.ultimatespecs.com/car-specs/Fiat/49146/Fiat-Stilo-MultiWagon-19-JTD-115HP-Dynamic.html
EU-VOLKSWAGEN-PASSAT-B6-SEDAN-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 3.2 V6 FSI 4MOTION	https://www.auto-data.net/en/volkswagen-passat-b6-3.2-v6-fsi-250hp-4motion-8887
EU-VOLKSWAGEN-PASSAT-B6-WAGON-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 3.2 FSI 4WD	https://www.auto-data.net/en/volkswagen-passat-variant-b6-3.2-i-v6-24v-fsi-4wd-250hp-8903
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391	Auto-Data Audi A4 Cabriolet B7 2.0 TFSI	https://www.auto-data.net/en/audi-a4-cabriolet-b7-8h-2.0-tfsi-200hp-4293
EU-AUDI-RS4-B7-CONVERTIBLE-01	4555	1814	1391	Automobile-Catalog Audi RS4 Cabriolet	https://www.automobile-catalog.com/car/2007/249065/audi_rs4_cabriolet.html
EU-AUDI-RS4-B7-WAGON-01	4586	1816	1415	Auto-Data Audi RS4 Avant B7	https://www.auto-data.net/en/audi-rs4-avant-8e-b7-4.2-fsi-v8-32v-420hp-quattro-4531
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237	Auto-Data Chevrolet Corvette C6 Z06	https://www.auto-data.net/en/chevrolet-corvette-coupe-c6-z06-7.0-i-v8-505hp-14521
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246	Auto-Data Chevrolet Corvette C6 Convertible	https://www.auto-data.net/en/chevrolet-corvette-convertible-c6-6.0-i-v8-405hp-14524
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704	Auto-Data Opel Antara 2.0 CDTI 4x4	https://www.auto-data.net/en/opel-antara-2.0-cdti-150hp-4x4-57413
EU-RENAULT-19-I-SEDAN-01	4262	1694	1412	Auto-Data Renault 19 I Chamade L53	https://www.auto-data.net/en/renault-19-i-chamade-l53-1.7-l53c-90hp-10790
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421	Auto-Data BMW 3 Series E90 320si	https://www.auto-data.net/en/bmw-3-series-sedan-e90-320si-173hp-45533
EU-MERCEDES-BENZ-R-CLASS-W251-MPV-SWB-01	4922	1922	1659	Auto-Data Mercedes-Benz R-Class W251 R 280 CDI 4MATIC	https://www.auto-data.net/en/mercedes-benz-r-class-w251-r-280-cdi-v6-190hp-4matic-g-tronic-37169
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458	Auto-Data Seat Leon II 1P FR 2.0 TDI	https://www.auto-data.net/en/seat-leon-ii-1p-fr-2.0-tdi-170hp-dpf-13606
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495	Auto-Data Chevrolet Aveo Sedan 1.4 i 16V	https://www.auto-data.net/en/chevrolet-aveo-sedan-1.4-i-16v-94hp-14429
EU-LDV-MAXUS-I-BUS-VAN-SWB-HIGHROOF-01	4920	1991	2315	Anchor Vans LDV Maxus specifications	https://www.anchorvans.co.uk/specifications/maxus
EU-LDV-MAXUS-I-BUS-VAN-LWB-HIGHROOF-01	5670	1991	2315	Anchor Vans LDV Maxus specifications	https://www.anchorvans.co.uk/specifications/maxus
EU-LDV-MAXUS-I-BUS-VAN-LWB-XHIGHROOF-01	5670	1991	2540	VehicleScore LDV Maxus dimensions;What Van LDV Maxus 17-Seater Minibus	https://vehiclescore.co.uk/car-dimensions-check/ldv/maxus;https://www.whatvan.co.uk/van-reviews/ldv-maxus-17-seater-minibus-tested-march-2007/
EU-LDV-MAXUS-I-VAN-SWB-LOWROOF-01	4920	1991	2070	Anchor Vans LDV Maxus specifications	https://www.anchorvans.co.uk/specifications/maxus
EU-KIA-SORENTO-I-FACELIFT-SUV-01	4590	1865	1811	Auto-Data Kia Sorento I facelift 2006	https://www.auto-data.net/en/kia-sorento-i-facelift-2006-generation-595
EU-KIA-CARNIVAL-II-MPV-SWB-PREFL-01	4810	1985	1815	Auto-Data Kia Carnival II VQ 2.7i V6	https://www.auto-data.net/en/kia-carnival-ii-vq-2.7i-v6-189hp-2741
EU-KIA-CARNIVAL-II-MPV-SWB-FACELIFT-01	4810	1985	1760	Auto-Data Kia Carnival II VQ facelift 2.7 V6	https://www.auto-data.net/en/kia-carnival-ii-vq-facelift-2010-2.7-v6-16v-189hp-automatic-17865
EU-KIA-CARNIVAL-II-MPV-LWB-01	5130	1985	1780	Auto-Data Kia Grand Carnival II 2.9 CRDi	https://www.auto-data.net/en/kia-grand-carnival-ii-2.9-crdi-185hp-automatic-34233
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-LWB-01	5038	1904	1967	Renault Conversions & Accessories technical manual	https://manualmachine.com/renault/conversionsaccessoires/10318077-user-manual/
EU-FIAT-SEDICI-I-SUV-4X4-01	4115	1755	1620	Automobile-Catalog Fiat Sedici 4x4 1.6 16V	https://www.automobile-catalog.com/car/2006/728450/fiat_sedici_4x4_1_6_16v_emotion.html
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II 1.6 HDi 75;Auto-Data Peugeot Partner I Phase II 1.6 HDi 90	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.6-hdi-75hp-5625;https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.6-hdi-90hp-5626
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448	Auto-Data Ford Focus Cabriolet II 2.0 TDCi	https://www.auto-data.net/en/ford-focus-cabriolet-ii-2.0-tdci-136hp-7341
EU-PEUGEOT-607-PHASE-II-SEDAN-01	4902	1800	1442	Auto-Data Peugeot 607 Phase II 2.2 HDi	https://www.auto-data.net/en/peugeot-607-phase-ii-2004-2.2-hdi-170hp-28801
EU-LANCIA-PHEDRA-I-MPV-01	4750	1863	1760	Auto-Data Lancia Phedra 2.0 JTD	https://www.auto-data.net/en/lancia-phedra-2.0-jtd-107hp-4933
EU-FERRARI-599-GTB-FIORANO-COUPE-01	4666	1961	1336	Auto-Data Ferrari 599 GTB Fiorano 6.0 V12	https://www.auto-data.net/en/ferrari-599-gtb-fiorano-6.0-v12-620hp-41025
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280	Auto-Data Porsche 911 997 GT3 3.6	https://www.auto-data.net/en/porsche-911-997-gt3-3.6-415hp-6585
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305	Auto-Data Porsche Cayman 987C 2.7	https://www.auto-data.net/en/porsche-cayman-987c-2.7-245hp-40902
EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	4140	1755	1620	Global Suzuki SX4 official launch specifications	https://www.globalsuzuki.com/globalnews/2006/0228b.html
EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	4100	1730	1565	Global Suzuki SX4 official launch specifications	https://www.globalsuzuki.com/globalnews/2006/0228b.html
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Auto-Data Alfa Romeo Spider 939 2.2 JTS	https://www.auto-data.net/en/alfa-romeo-spider-939-2.2-jts-185hp-1437
EU-RENAULT-VEL-SATIS-I-FACELIFT-HATCHBACK-01	4860	1860	1577	Automobile-Catalog Renault Vel Satis dCi 150	https://www.automobile-catalog.com/car/2006/2949875/renault_vel_satis_dci_150.html
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568	Auto-Data Seat Altea 5P FR 2.0 TDI	https://www.auto-data.net/en/seat-altea-5p-fr-2.0-tdi-170hp-dpf-13585
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	Automobile-Catalog Seat Altea 2.0 TDI CR 170	https://www.automobile-catalog.com/car/2010/3082340/seat_altea_2_0_tdi_cr_170.html
EU-NISSAN-350Z-Z33-COUPE-01	4313	1815	1326	Automobile-Catalog Nissan 350Z Grand Touring	https://www.automobile-catalog.com/car/2006/2188805/nissan_350_z_grand_touring.html
EU-JEEP-COMMANDER-XK-SUV-01	4787	1899	1826	Automobile-Catalog Jeep Commander 3.0 CRD	https://www.automobile-catalog.com/car/2006/1327730/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	4582	1820	1400	Volvo C70 Model Year 2007 official specifications	https://www.volvoclub.org.uk/press/volvo2007uk/C70_2007_AllNew_Fullprod_spec.pdf
EU-VOLVO-S60-I-FACELIFT-SEDAN-01	4603	1813	1428	Volvo S60 Model Year 2007 official specifications	https://www.volvoclub.org.uk/press/volvo2007uk/S60_2007_Fullprod_spec.pdf
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395	Auto-Data BMW 335i Coupe E92	https://www.auto-data.net/en/bmw-3-series-coupe-e92-335i-306hp-9958
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data BMW 335i Coupe E92 LCI	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-335i-306hp-17230
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455	Automobile-Catalog Peugeot 407 2.2 HDi FAP 170	https://www.automobile-catalog.com/car/2006/2619440/peugeot_407_2_2_hdi_170.html
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455	Automobile-Catalog Peugeot 407 Phase II 2.2 HDi FAP 170	https://www.automobile-catalog.com/car/2008/2619605/peugeot_407_2_2_hdi_170.html
EU-SSANGYONG-MUSSO-SPORTS-PICKUP-01	4935	1864	1760	Autoevolution SsangYong Musso Sports	https://www.autoevolution.com/cars/ssangyong-musso-sports-1998.html
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	6403	2084	2380	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	6403	2084	2624	Ford People Movers 2007 UK official brochure;Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-People-Movers-V1-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	6403	2084	2629	Ford Transit 2010 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Transit-UK.pdf
EU-CITROEN-JUMPER-III-BUS-VAN-L1H1-01	4963	2050	2254	Citroën Relay Product & Technical Information October 2008	https://xr793.com/wp-content/uploads/2022/09/2008-Citroen-Relay-Tech-Specs-UK.pdf
EU-CITROEN-JUMPER-III-BUS-VAN-L2H1-01	5413	2050	2254	Citroën Relay Product & Technical Information October 2008	https://xr793.com/wp-content/uploads/2022/09/2008-Citroen-Relay-Tech-Specs-UK.pdf
EU-CITROEN-JUMPER-III-BUS-VAN-L2H2-01	5413	2050	2524	Citroën Relay Product & Technical Information October 2008	https://xr793.com/wp-content/uploads/2022/09/2008-Citroen-Relay-Tech-Specs-UK.pdf
EU-CITROEN-JUMPER-III-BUS-VAN-L3H2-01	5998	2050	2524	Citroën Relay Product & Technical Information October 2008	https://xr793.com/wp-content/uploads/2022/09/2008-Citroen-Relay-Tech-Specs-UK.pdf
EU-CITROEN-JUMPER-III-BUS-VAN-L4H2-01	6363	2050	2524	Citroën Relay Product & Technical Information October 2008	https://xr793.com/wp-content/uploads/2022/09/2008-Citroen-Relay-Tech-Specs-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.anchorvans.co.uk/specifications/maxus "https://www.anchorvans.co.uk/specifications/maxus"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-JEEP-COMMANDER-XK-SUV-01 的 WidthMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_301-400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_301-400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1915 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（964 行）

- 尺寸冲突协调：
  - EU-JEEP-COMMANDER-XK-SUV-01 -> EU-JEEP-COMMANDER-XK-SUV-02：4787x1900x1826 与 4787x1899x1826，创建新尺寸组
