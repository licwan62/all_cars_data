# 任务：all 第 1501-1600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0016__53aaffb7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1501-1600 行

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
all 第 1501-1600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Skoda	Fabia ii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	51	70	Feb 2007	Mar 2010	2024-03-01	22948
Skoda	Fabia ii	1.4 TDI	Schrägheck	Frontantrieb	Diesel	59	80	Jan 2007	Mar 2010	2024-03-01	22949
Skoda	Fabia ii	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Apr 2007	Mar 2010	2024-03-01	22950
Alfa Romeo	159	2.4 Jtdm Q4	Kombi	Allrad	Diesel	154	210	May 2007	Nov 2011	2024-03-01	22951
Alfa Romeo	159	2.4 Jtdm Q4	Stufenheck	Allrad	Diesel	154	210	May 2007	Nov 2011	2024-03-01	22952
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	105	143	Sep 2006	Dec 2011	2024-03-01	22953
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	125	170	Mar 2007	Sep 2012	2024-03-01	22954
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	105	143	Sep 2006	Dec 2011	2024-03-01	22955
BMW	1	120 D	Schrägheck	Heckantrieb	Diesel	130	177	Mar 2007	Dec 2011	2024-03-01	22956
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	160	218	Dec 2006	Feb 2010	2024-03-01	22957
Mitsubishi	Diamante i	3	Stufenheck	Frontantrieb	Benzin	151	205	Oct 1992	Jul 1996	2024-03-01	22966
Honda	City	1.5 I-dsi	Stufenheck	Frontantrieb	Benzin	66	90	Dec 2002	Jul 2008	2024-03-01	22973
Honda	City	1.5 I-dsi	Stufenheck	Frontantrieb	Benzin	81	110	Oct 2004	Jul 2008	2024-03-01	22974
Toyota	Yaris	1.3	Stufenheck	Frontantrieb	Benzin	64	87	Sep 2005	Oct 2013	2024-03-01	22992
Toyota	Camry	2	Stufenheck	Frontantrieb	Benzin	110	150	Aug 2001	Nov 2006	2024-03-01	23011
Toyota	Camry	2.0 4WD	Stufenheck	Allrad	Benzin	94	128	Aug 1988	May 1991	2024-03-01	23014
Renault	Clio iii	1.2 16V	Schrägheck	Frontantrieb	Benzin	74	101	May 2007	Dec 2014	2026-05-01	23045
Renault	Modus / grand	1.2 16V	Schrägheck	Frontantrieb	Benzin	74	101	May 2007	Dec 2013	2025-12-01	23046
Renault	Modus / grand	1.5 DCI	Schrägheck	Frontantrieb	Diesel	76	103	May 2007	Dec 2013	2025-12-01	23047
Citroën	C8	2.0 HDI	Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2006	-	2024-03-01	23048
Land Rover	Freelander 2	2.2 TD4 4X4	Geländewagen geschlossen	Allrad	Diesel	112	152	Jan 2007	Oct 2014	2024-03-01	23049
Land Rover	Range rover iii	3.6 D 4X4	Geländewagen geschlossen	Allrad	Diesel	200	272	Apr 2006	Aug 2012	2024-03-01	23050
Land Rover	Range rover sport i	3.6 D 4X4	SUV	Allrad	Diesel	200	272	Apr 2006	Mar 2013	2024-03-01	23051
KIA	Opirus	3.8 V6	Stufenheck	Frontantrieb	Benzin	196	267	Oct 2006	Oct 2012	2024-05-01	23052
Nissan	Pathfinder iii	2.5 DCI 4WD	SUV	Allrad	Diesel	126	171	Oct 2006	-	2024-03-01	23053
Nissan	Navara	2.5 DCI 4WD	Pick-up	Allrad	Diesel	126	171	Oct 2006	-	2024-03-01	23054
Volvo	Xc90 i	3.2 AWD	SUV	Allrad	Benzin	175	238	Mar 2006	Dec 2010	2024-03-01	23056
Renault	Megane ii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	82	112	Jan 2006	Aug 2009	2024-03-01	23060
Renault	Megane ii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	76	103	Jan 2007	Jul 2009	2024-03-01	23061
Renault	Megane ii	1.6 16V	Stufenheck	Frontantrieb	Benzin	82	112	Jan 2006	-	2024-03-01	23062
Renault	Megane ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	76	103	Oct 2003	Dec 2010	2024-03-01	23063
Renault	Megane ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	76	103	Jan 2007	Mar 2009	2024-03-01	23064
Renault	Megane ii	1.6 16V	Schrägheck	Frontantrieb	Benzin	82	112	Jan 2006	Jun 2008	2024-03-01	23065
Renault	Megane ii	2.0 DCI	Schrägheck	Frontantrieb	Diesel	127	173	Jan 2007	Feb 2008	2024-03-01	23066
Renault	Megane ii coupé-	1.6 16V	Cabriolet	Frontantrieb	Benzin	82	112	Jan 2006	Jun 2008	2024-03-01	23069
Renault	Megane ii coupé-	1.5 DCI	Cabriolet	Frontantrieb	Diesel	76	103	Jan 2007	Jun 2009	2024-03-01	23070
Renault	Scénic ii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	76	103	Jan 2007	Nov 2008	2024-03-01	23071
Renault	Scénic ii	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	82	112	Oct 2005	Nov 2008	2024-03-01	23072
Renault	Master ii	2.5 DCI	Bus	Frontantrieb	Diesel	74	101	Sep 2006	Jan 2010	2024-08-01	23073
Renault	Master ii	2.5 DCI	Bus	Frontantrieb	Diesel	88	120	Jun 2006	Jan 2010	2024-08-01	23074
Renault	Master ii	2.5 DCI	Bus	Frontantrieb	Diesel	107	146	Aug 2006	Jan 2010	2024-08-01	23075
Renault	Master ii	2.5 DCI	Kasten	Frontantrieb	Diesel	74	101	Aug 2006	Jan 2010	2024-03-01	23076
Renault	Master ii	2.5 DCI	Kasten	Frontantrieb	Diesel	88	120	Aug 2006	Jan 2010	2024-08-01	23077
Renault	Master ii	2.5 DCI	Kasten	Frontantrieb	Diesel	107	146	Aug 2006	Jan 2010	2024-08-01	23078
Renault	Master ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Aug 2006	Jan 2010	2024-08-01	23079
Renault	Master ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2006	Jan 2011	2024-08-01	23080
Renault	Master ii	2.5 DCI	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	Jan 2010	2024-08-01	23081
Isuzu	D-Max i	2.5 Ditd	Pick-up	Heckantrieb	Diesel	74	101	Oct 2002	Jun 2012	2024-03-01	23083
Jeep	Grand cherokee i	5.2	Geländewagen geschlossen	Heckantrieb	Benzin	164	223	Oct 1996	Sep 1998	2024-03-01	23092
Jeep	Grand cherokee i	5.2 4X4	Geländewagen geschlossen	Allrad	Benzin	164	223	Oct 1996	Sep 1998	2024-03-01	23093
Jeep	Cherokee	5.9 4X4	Geländewagen geschlossen	Allrad	Benzin	128	174	Oct 1980	Sep 1986	2024-03-01	23094
Jeep	Cherokee	4.2 4X4	Geländewagen geschlossen	Allrad	Benzin	76	103	Sep 1979	Dec 1983	2024-03-01	23095
Jeep	Grand wagoneer	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	81	110	Oct 1983	Sep 1986	2024-03-01	23096
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	87	118	Oct 1984	Sep 1986	2024-03-01	23097
Jeep	Grand wagoneer	2.8 4WD	Geländewagen geschlossen	Allrad	Benzin	81	110	Oct 1983	Sep 1986	2024-03-01	23098
Jeep	Grand wagoneer	4.2 4WD	Geländewagen geschlossen	Allrad	Benzin	81	110	Oct 1983	Sep 1986	2024-03-01	23099
Land Rover	Discovery i	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	98	133	Jun 1989	Aug 1990	2024-03-01	23102
Peugeot	309 i	1.6	Schrägheck	Frontantrieb	Benzin	83	113	Jul 1986	Jun 1989	2024-03-01	23127
Seat	Ibiza iii	1.4 16V	Schrägheck	Frontantrieb	Benzin	63	86	May 2006	Nov 2009	2024-03-01	23128
Opel	Combo tour	1.7 Cdti 16V	Großraumlimousine	Frontantrieb	Diesel	74	101	Jul 2004	Dec 2011	2024-03-01	23132
Mercedes-benz	124	250 TD Turbo	Kombi	Heckantrieb	Diesel	93	126	Mar 1988	Jul 1993	2024-03-01	23133
Mercedes-benz	C-Klasse	C 230 4-matic	Stufenheck	Allrad	Benzin	150	204	Jul 2007	Jan 2014	2024-03-01	23135
Mercedes-benz	C-Klasse	C 280 4-matic	Stufenheck	Allrad	Benzin	170	231	Jul 2007	Jan 2014	2024-03-01	23136
Mercedes-benz	C-Klasse	C 350 4-matic	Stufenheck	Allrad	Benzin	200	272	Jul 2007	Jan 2014	2024-03-01	23137
Mercedes-benz	C-Klasse	C 320 CDI 4-matic	Stufenheck	Allrad	Diesel	165	224	Jul 2007	Jan 2014	2024-03-01	23138
Ford	Tourneo connect	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	81	110	Aug 2006	Dec 2013	2024-03-01	23139
Opel	Gt	2	Cabriolet	Heckantrieb	Benzin	194	264	Jun 2007	Dec 2011	2024-03-01	23140
Volvo	C30	T5	Schrägheck	Frontantrieb	Benzin	169	230	Mar 2007	Dec 2012	2024-03-01	23141
Volvo	S40 ii	T5	Stufenheck	Frontantrieb	Benzin	169	230	Mar 2007	Dec 2012	2024-03-01	23142
Volvo	S40 ii	T5 AWD	Stufenheck	Allrad	Benzin	169	230	Mar 2007	Dec 2010	2024-03-01	23143
Volvo	V50	T5	Kombi	Frontantrieb	Benzin	169	230	Mar 2007	Dec 2012	2024-03-01	23144
Volvo	V50	T5 AWD	Kombi	Allrad	Benzin	169	230	Mar 2007	Dec 2010	2024-03-01	23145
Volvo	S80 ii	3.2 AWD	Stufenheck	Allrad	Benzin	175	238	Jan 2007	Dec 2010	2024-03-01	23146
Volvo	S80 ii	T6 AWD	Stufenheck	Allrad	Benzin	210	286	Jan 2007	Dec 2010	2024-03-01	23147
Volvo	S80 ii	D5 AWD	Stufenheck	Allrad	Diesel	136	185	Jan 2007	May 2009	2024-03-01	23148
Volvo	C70 ii	T5	Cabriolet	Frontantrieb	Benzin	169	230	Mar 2007	Jun 2013	2024-03-01	23149
Volvo	V70 iii	2.5 T	Kombi	Frontantrieb	Benzin	147	200	Aug 2007	Dec 2009	2024-03-01	23150
Volvo	V70 iii	3.2 AWD	Kombi	Allrad	Benzin	175	238	Apr 2007	Dec 2010	2024-03-01	23151
Volvo	V70 iii	T6 AWD	Kombi	Allrad	Benzin	210	286	Aug 2007	Dec 2010	2024-03-01	23152
Volvo	V70 iii	2.4 D	Kombi	Frontantrieb	Diesel	120	163	Apr 2007	Dec 2010	2024-03-01	23153
Volvo	V70 iii	D5	Kombi	Frontantrieb	Diesel	136	185	Apr 2007	Dec 2009	2024-03-01	23154
Volvo	Xc70 ii	3.2 AWD	Kombi	Allrad	Benzin	175	238	Aug 2007	Dec 2011	2024-03-01	23155
Volvo	Xc70 ii	D5 AWD	Kombi	Allrad	Diesel	136	185	Apr 2007	Dec 2009	2024-03-01	23156
Mercedes-benz	Clk	CLK 200 Kompressor	Coupe	Heckantrieb	Benzin	135	184	Oct 2006	May 2009	2024-03-01	23157
Mercedes-benz	Clk	CLK 200 Kompressor	Cabriolet	Heckantrieb	Benzin	135	184	Oct 2006	Mar 2010	2024-03-01	23158
Mercedes-benz	Clk	CLK 500	Cabriolet	Heckantrieb	Benzin	285	388	Jun 2006	Mar 2010	2024-03-01	23159
Aston Martin	Vantage	4.3	Coupe	Heckantrieb	Benzin	283	385	Oct 2005	Dec 2008	2024-03-01	23160
Aston Martin	Vantage	4.3	Cabriolet	Heckantrieb	Benzin	283	385	Apr 2007	Dec 2008	2024-03-01	23161
VW	Golf v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	90	122	May 2007	Nov 2008	2024-03-01	23162
VW	Golf v variant	1.4 TSI	Kombi	Frontantrieb	Benzin	90	122	Jun 2007	Jul 2009	2024-03-01	23163
VW	Golf plus v	1.4 TSI	Schrägheck	Frontantrieb	Benzin	90	122	Jun 2007	Dec 2013	2024-03-01	23164
Skoda	Fabia ii combi	1.2	Kombi	Frontantrieb	Benzin	51	70	Oct 2007	Dec 2014	2024-03-01	23165
Skoda	Fabia ii combi	1.4	Kombi	Frontantrieb	Benzin	63	86	Oct 2007	Dec 2014	2024-03-01	23166
Skoda	Fabia ii combi	1.6	Kombi	Frontantrieb	Benzin	77	105	Oct 2007	Dec 2014	2024-03-01	23167
Skoda	Fabia ii combi	1.4 TDI	Kombi	Frontantrieb	Diesel	51	70	Oct 2007	Mar 2010	2024-03-01	23168
Skoda	Fabia ii combi	1.4 TDI	Kombi	Frontantrieb	Diesel	59	80	Oct 2007	Mar 2010	2024-03-01	23169
Skoda	Fabia ii combi	1.9 TDI	Kombi	Frontantrieb	Diesel	77	105	Oct 2007	Mar 2010	2024-03-01	23170
Alfa Romeo	Brera	2.4 Jtdm 20V	Schrägheck	Frontantrieb	Diesel	154	210	May 2007	Mar 2011	2024-03-01	23171
Alfa Romeo	159	2.4 Jtdm	Stufenheck	Frontantrieb	Diesel	154	210	Jul 2007	Nov 2011	2024-03-01	23172
Alfa Romeo	159	2.4 Jtdm	Kombi	Frontantrieb	Diesel	154	210	May 2007	Dec 2012	2024-03-01	23173


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 **14 个首次建组尺寸组**，新增 **25 条 READY 映射**。已闭合 Fabia II、BMW E93、Megane II Grandtour/CC、Scénic II、Opel GT II、Volvo S40/V70、Mercedes-Benz CLK A209、Aston Martin V8 Vantage、Golf V Variant 等外廓。([汽车数据网][1])
* Alfa Romeo 159 Sedan/Sportwagon 的具体 210 马力配置目前只能获得范围高度，未强行选取单值，相关映射保持 PENDING。([汽车数据网][2])
* 跨改款、门数不明及来源冲突的记录均未用单一尺寸覆盖。

## 当前批次进度

* 输入 Ktype：100
* 已进入映射表：60
* READY 映射：25
* PENDING 映射：35
* 尚未进入本轮变化表：40
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22948	22948	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22949	22949	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22950	22950	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22951	22951	Wagon	159 Sportwagon		5		LOW	候选为159 Sportwagon 210 Q4。	PENDING: 具体配置高度仅有范围值
22952	22952	Sedan	159		4		LOW	候选为159 Sedan 210 Q4。	PENDING: 具体配置高度仅有范围值
22953	22953	Hatchback	1 Series E8x				LOW	候选为E81三门或E87五门。	PENDING: 门数与车身代码边界未确认
22954	22954	Hatchback	1 Series E8x				LOW	候选含E81三门、E87五门，结束日期并进入F20时期。	PENDING: 门数及代际覆盖边界未确认
22955	22955	Hatchback	1 Series E8x				LOW	候选为E81三门或E87五门。	PENDING: 门数与车身代码边界未确认
22956	22956	Hatchback	1 Series E8x				LOW	候选为E81三门或E87五门。	PENDING: 门数与车身代码边界未确认
22957	22957	Convertible	3 Series E93	E93	2	EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	HIGH	E93硬顶敞篷车身。	READY
23048	23048	MPV	C8 Phase I		5		LOW	候选为C8 Phase I 2.0 HDI。	PENDING: 具体量产配置高度仅有范围值
23060	23060	Wagon	Megane II Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
23061	23061	Wagon	Megane II Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
23062	23062	Sedan	Megane II		4		LOW	候选为Phase II Sedan。	PENDING: 结束日期缺失且改款覆盖边界未确认
23063	23063	Sedan	Megane II		4		LOW	生产区间跨Phase I与Phase II。	PENDING: 改款前后物理分支尚未拆分
23064	23064	Hatchback	Megane II Phase II				LOW	候选五门与三门Hatchback分支。	PENDING: 门数边界未确认
23065	23065	Hatchback	Megane II				LOW	生产区间与三门/五门及Phase I/II边界未闭合。	PENDING: 门数和改款分支未确认
23066	23066	Hatchback	Megane II Phase II				LOW	候选五门与三门Hatchback分支。	PENDING: 门数边界未确认
23069	23069	Convertible	Megane II Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	Coupe-Cabriolet物理车身。	READY
23070	23070	Convertible	Megane II Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	Coupe-Cabriolet物理车身。	READY
23071	23071	MPV	Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH		READY
23072	23072	MPV	Scenic II		5		LOW	生产起点早于Phase II，覆盖改款前后。	PENDING: prefl与facelift分支尚未拆分
23135	23135	Sedan	C-Class W204	W204	4		LOW	生产区间覆盖2011改款。	PENDING: prefl与facelift尺寸组尚未拆分
23136	23136	Sedan	C-Class W204	W204	4		LOW	生产区间覆盖2011改款。	PENDING: prefl与facelift尺寸组尚未拆分
23137	23137	Sedan	C-Class W204	W204	4		LOW	生产区间覆盖2011改款。	PENDING: prefl与facelift尺寸组尚未拆分
23138	23138	Sedan	C-Class W204	W204	4		LOW	生产区间覆盖2011改款。	PENDING: prefl与facelift尺寸组尚未拆分
23140	23140	Convertible	GT II		2	EU-OPEL-GT-II-CONVERTIBLE-2D-01	HIGH		READY
23141	23141	Hatchback	C30		3		LOW	生产区间覆盖2010改款。	PENDING: prefl与facelift尺寸组尚未拆分
23142	23142	Sedan	S40 II facelift		4	EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23143	23143	Sedan	S40 II facelift		4	EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23144	23144	Wagon	V50 facelift		5		LOW	候选为V50 facelift五门旅行车。	PENDING: facelift长度来源冲突未解决
23145	23145	Wagon	V50 facelift		5		LOW	候选为V50 facelift五门旅行车。	PENDING: facelift长度来源冲突未解决
23146	23146	Sedan	S80 II		4		LOW	生产区间覆盖2009改款。	PENDING: prefl与facelift尺寸组尚未拆分
23147	23147	Sedan	S80 II		4		LOW	生产区间覆盖2009改款。	PENDING: prefl与facelift尺寸组尚未拆分
23148	23148	Sedan	S80 II		4		LOW	生产区间覆盖2009改款。	PENDING: prefl与facelift尺寸组尚未拆分
23149	23149	Convertible	C70 II		2		LOW	生产区间覆盖2009改款。	PENDING: prefl与facelift尺寸组尚未拆分
23150	23150	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23151	23151	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23152	23152	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23153	23153	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23154	23154	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23155	23155	Wagon	XC70 II		5		LOW	生产区间覆盖2011改款。	PENDING: prefl与facelift尺寸组尚未拆分
23156	23156	Wagon	XC70 II		5		LOW	候选为改款前XC70 II。	PENDING: 具体D5 AWD高度尚未闭合
23157	23157	Coupe	CLK C209 facelift	C209	2		LOW	候选为C209 facelift CLK 200 Kompressor。	PENDING: 184马力具体车身高度未闭合
23158	23158	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	HIGH		READY
23159	23159	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	HIGH	CLK 500高度独立。	READY
23160	23160	Coupe	V8 Vantage 2005		2	EU-ASTON-MARTIN-V8-VANTAGE-2005-COUPE-2D-01	HIGH		READY
23161	23161	Convertible	V8 Vantage Roadster 2005		2	EU-ASTON-MARTIN-V8-VANTAGE-2005-ROADSTER-2D-01	HIGH		READY
23162	23162	Hatchback	Golf V				LOW	候选同时存在三门与五门车身。	PENDING: 门数物理分支未确认
23163	23163	Wagon	Golf V Variant		5	EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
23164	23164	MPV	Golf Plus		5		LOW	生产区间跨Golf V Plus与2009改款。	PENDING: 改款前后物理分支尚未拆分
23165	23165	Wagon	Fabia II Combi		5		LOW	生产区间覆盖2010改款。	PENDING: prefl与facelift尺寸组尚未拆分
23166	23166	Wagon	Fabia II Combi		5		LOW	生产区间覆盖2010改款。	PENDING: prefl与facelift尺寸组尚未拆分
23167	23167	Wagon	Fabia II Combi		5		LOW	生产区间覆盖2010改款。	PENDING: prefl与facelift尺寸组尚未拆分
23168	23168	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23169	23169	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23170	23170	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23171	23171	Coupe	Brera		3		LOW	候选为Brera 210马力三门Coupe。	PENDING: 年份覆盖与长度冲突未解决
23172	23172	Sedan	159		4		LOW	候选为159 Sedan 210前驱。	PENDING: 具体配置高度仅有范围值
23173	23173	Wagon	159 Sportwagon		5		LOW	候选为159 Sportwagon 210前驱。	PENDING: 具体配置高度仅有范围值
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	3992	1642	1498	Auto-Data Skoda Fabia II specifications	https://www.auto-data.net/en/skoda-fabia-ii-generation-3089
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384	Auto-Data BMW 3 Series Convertible E93 325i specifications	https://www.auto-data.net/en/bmw-3-series-convertible-e93-325i-218hp-9961
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II 1.6 16V specifications	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-30357
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II specifications	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-generation-5609
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620	Auto-Data Renault Scenic II Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-scenic-ii-phase-ii-1.5-dci-103hp-fap-39496
EU-OPEL-GT-II-CONVERTIBLE-2D-01	4100	1813	1274	Auto-Data Opel GT II 2.0 GT specifications	https://www.auto-data.net/en/opel-gt-ii-2.0-gt-264hp-1744
EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	4476	1770	1454	Auto-Data Volvo S40 II facelift T5 specifications	https://www.auto-data.net/en/volvo-s40-ii-facelift-2007-2.5-t5-230hp-geartronic-17554
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547	Auto-Data Volvo V70 III 2.5 T specifications	https://www.auto-data.net/en/volvo-v70-iii-2.5-t-200hp-9233
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413	Auto-Data Mercedes-Benz CLK A209 facelift CLK 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-clk-a209-facelift-2005-clk-200-kompressor-184hp-5g-tronic-52931
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415	Auto-Data Mercedes-Benz CLK A209 facelift CLK 500 specifications	https://www.auto-data.net/en/mercedes-benz-clk-a209-facelift-2005-clk-500-388hp-7g-tronic-23480
EU-ASTON-MARTIN-V8-VANTAGE-2005-COUPE-2D-01	4383	1866	1255	Auto-Data Aston Martin V8 Vantage 2005 4.3 specifications	https://www.auto-data.net/en/aston-martin-v8-vantage-2005-4.3-i-v8-32v-385hp-3054
EU-ASTON-MARTIN-V8-VANTAGE-2005-ROADSTER-2D-01	4383	1866	1255	Auto-Data Aston Martin V8 Vantage Roadster 2005 4.3 specifications	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-2005-4.3-i-v8-32v-385hp-3055
EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Auto-Data Volkswagen Golf V Variant 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.4-tsi-122hp-8638
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498	Auto-Data Skoda Fabia II Combi 1.4 TDI specifications	https://www.auto-data.net/en/skoda-fabia-ii-combi-1.4-tdi-70hp-14140
```

## 下一步优先处理

1. 批量闭合尚未进入映射表的 40 个 Ktype，优先处理可直接聚类复用的普通乘用车。
2. 集中拆分 BMW 1 Series、Megane II Hatchback、W204、Volvo 与 Fabia II Combi 的门数或改款分支。
3. 最后处理 Master II、Navara、D-Max 等多轴距、车顶、驾驶室或货斗组合。
4. 对 Alfa 159、C8、V50、Brera 等具体范围值或来源冲突只修复阻塞字段，不重复抓取已闭合尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/skoda-fabia-ii-1.4-tdi-80hp-14133?utm_source=chatgpt.com "Skoda Fabia II 1.4 TDI (80 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alfa-romeo-159-2.4-jtdm-20v-210hp-q4-42210 "Alfa Romeo 159 2.4 JTDM 20V (210 Hp) Q4 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 Diamante I、Honda City GD、Yaris/Belta、Camry XV30、Camry V20 4WD、Opirus、XC90 I 等乘用车尺寸组。([汽车数据网][1])
* 新增闭合 Megane II Classic Phase II、Scénic II Phase I、Grand Cherokee ZJ facelift、Combo Tour C facelift、W204 改款前尺寸组。([汽车目录][2])
* `23072` 已拆为 Phase I、Phase II 两个物理分支；Phase II 直接复用既有尺寸组。
* `23062`、`23135`–`23138` 已由 PENDING 转为 READY。
* 本轮新增或修改 17 条映射，首次创建 12 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：70
* READY 映射：42
* PENDING 映射：29
* 已确认尺寸组：26
* 尚未进入映射表的 Ktype：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22966	22966	Sedan	Diamante I		4	EU-MITSUBISHI-DIAMANTE-I-SEDAN-4D-01	MEDIUM		READY
22973	22973	Sedan	City IV (GD)		4	EU-HONDA-CITY-GD-SEDAN-4D-01	MEDIUM		READY
22974	22974	Sedan	City IV (GD)		4	EU-HONDA-CITY-GD-SEDAN-4D-01	HIGH		READY
22992	22992	Sedan	Belta XP90	SCP92	4	EU-TOYOTA-YARIS-BELTA-SCP92-SEDAN-4D-01	HIGH	Yaris三厢版对应Belta/SCP92。	READY
23011	23011	Sedan	Camry XV30		4	EU-TOYOTA-CAMRY-XV30-SEDAN-4D-01	MEDIUM		READY
23014	23014	Sedan	Camry V20		4	EU-TOYOTA-CAMRY-V20-SEDAN-4D-4WD-01	HIGH		READY
23052	23052	Sedan	Opirus facelift		4	EU-KIA-OPIRUS-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23056	23056	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	MEDIUM		READY
23062	23062	Sedan	Megane II Classic Phase II		4	EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	HIGH		READY
23072_prefl	23072	MPV	Scenic II Phase I		5	EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	MEDIUM	生产区间覆盖Phase I分支。	READY
23072_facelift	23072	MPV	Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	生产区间覆盖Phase II分支。	READY
23092	23092	SUV	Grand Cherokee I facelift	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	HIGH		READY
23132	23132	MPV	Combo Tour C facelift		5	EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	HIGH		READY
23135	23135	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23136	23136	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23137	23137	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23138	23138	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-DIAMANTE-I-SEDAN-4D-01	4740	1775	1410	Auto-Data Mitsubishi Diamante I 3.0 V6 specifications	https://www.auto-data.net/en/mitsubishi-diamante-i-3.0-i-v6-24v-210hp-15474
EU-HONDA-CITY-GD-SEDAN-4D-01	4310	1690	1485	Automobile-Catalog Honda City ZX 1.5 i-DSI;Automobile-Catalog Honda City 1.5V	https://www.automobile-catalog.com/car/2002/1270775/honda_city_zx_1_5a_i-dsi.html;https://www.automobile-catalog.com/car/2004/1270745/honda_city_1_5v.html
EU-TOYOTA-YARIS-BELTA-SCP92-SEDAN-4D-01	4300	1690	1460	Toyota 75 Years Belta official specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012570/index.html
EU-TOYOTA-CAMRY-XV30-SEDAN-4D-01	4815	1795	1500	Auto-Data Toyota Camry V XV30 generation specifications	https://www.auto-data.net/en/toyota-camry-v-xv30-generation-1011
EU-TOYOTA-CAMRY-V20-SEDAN-4D-4WD-01	4520	1710	1400	Toyota Camry GLi 4WD official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Camry-Gen2-4WD-archive-launch-pack-1988.pdf
EU-KIA-OPIRUS-FACELIFT-SEDAN-4D-01	4970	1850	1486	Auto-Data Kia Opirus 3.8 V6 specifications	https://www.auto-data.net/en/kia-opirus-3.8-i-v6-24v-266hp-2677
EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	4798	1898	1743	Auto-Data Volvo XC90 facelift 3.2 AWD specifications	https://www.auto-data.net/en/volvo-xc90-facelift-2007-3.2i-238hp-awd-automatic-9531
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460	Automobile-Catalog Renault Megane Classic 1.6 16V;Automobile-Catalog Renault Megane Classic body dimensions	https://www.automobile-catalog.com/car/2006/2954570/renault_megane_classic_1_6_16v.html;https://www.automobile-catalog.com/car/2006/2954600/renault_megane_classic_2_0_16v.html
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620	Automobile-Catalog Renault Scenic 1.6 16V specifications	https://www.automobile-catalog.com/car/2005/2955185/renault_scenic_1_6_16v.html
EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	4501	1760	1648	Auto-Data Jeep Grand Cherokee I ZJ 5.2 V8 specifications	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.2i-v8-223hp-automatic-31841
EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	4322	1684	1801	Auto-Data Opel Combo Tour C facelift 1.7 CDTI specifications	https://www.auto-data.net/de/opel-combo-tour-c-facelift-2003-1.7-cdti-100hp-1767
EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 280 4MATIC specifications	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-280-v6-231hp-4matic-7g-tronic-12545
```

## 下一步优先处理

1. 批量拆分 BMW E81/E87、Megane II Hatchback、Golf V 的三门与五门分支。
2. 处理 Master II、Navara、D-Max、Tourneo Connect 的轴距、车顶、驾驶室和货斗分支。
3. 关闭 Alfa 159、C8、Range Rover、XC70 等高度范围或宽度口径阻塞。
4. 将剩余尚未进入映射表的 30 个 Ktype 全部纳入处理。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-diamante-i-3.0-i-v6-24v-210hp-15474 "https://www.auto-data.net/en/mitsubishi-diamante-i-3.0-i-v6-24v-210hp-15474"
[2]: https://www.automobile-catalog.com/make/renault/megane_2gen/megane_2_2_sedan/2006.html "https://www.automobile-catalog.com/make/renault/megane_2gen/megane_2_2_sedan/2006.html"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 上一轮 29 条 PENDING 已全部处理为 READY。BMW `22953–22956` 均确认对应 E81 三门车身；Megane II `23064–23066` 则按 CM 三门、BM 五门拆分。([lakiauto.ee][1])
* Alfa Romeo 159 的 Q4 与前驱版本高度不同，已分别建组，未再用一个通用尺寸覆盖。([汽车目录][2])
* 新纳入此前未覆盖的 30 个 Ktype，其中 3 个完成 READY，27 个涉及门数、轴距、车顶、驾驶室或改款分支，保持 PENDING。
* 本轮新增或修改映射 66 行，首次创建尺寸组 23 个。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：100
* 当前映射行：108
* READY 映射：81
* PENDING 映射：27
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22951	22951	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	HIGH		READY
22952	22952	Sedan	159	939	4	EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	HIGH		READY
22953	22953	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22954	22954	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22955	22955	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22956	22956	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
23045	23045	Hatchback	Clio III				LOW	候选含三门与五门车身。	PENDING: 门数物理分支未闭合
23046	23046	MPV	Modus / Grand Modus		5		LOW	候选含标准Modus与Grand Modus。	PENDING: 长车身分支未闭合
23047	23047	MPV	Modus / Grand Modus		5		LOW	候选含标准Modus与Grand Modus。	PENDING: 长车身分支未闭合
23048	23048	MPV	C8 Phase I		5	EU-CITROEN-C8-PHASE-I-MPV-5D-01	HIGH		READY
23049	23049	SUV	Freelander 2	L359	5	EU-LAND-ROVER-FREELANDER-II-SUV-5D-01	MEDIUM		READY
23050	23050	SUV	Range Rover III	L322	5		LOW	生产区间覆盖后期改款。	PENDING: 改款分支及不含后视镜宽度未闭合
23051	23051	SUV	Range Rover Sport I	L320	5		LOW	生产区间覆盖改款。	PENDING: 改款分支及不含后视镜宽度未闭合
23053	23053	SUV	Pathfinder III	R51	5		LOW		PENDING: 改款外廓边界尚未闭合
23054	23054	Pickup	Navara	D40			LOW	候选含不同驾驶室与货斗。	PENDING: 驾驶室和货斗分支未闭合
23063	23063	Sedan	Megane II Classic	LM	4	EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	MEDIUM		READY
23064_3dr	23064	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23064_5dr	23064	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23065_3dr	23065	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23065_5dr	23065	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23066_3dr	23066	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23066_5dr	23066	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23073	23073	MPV	Master II				LOW	候选含多轴距与多车顶客运车。	PENDING: 轴距和车顶分支未闭合
23074	23074	MPV	Master II				LOW	候选含多轴距与多车顶客运车。	PENDING: 轴距和车顶分支未闭合
23075	23075	MPV	Master II				LOW	候选含多轴距与多车顶客运车。	PENDING: 轴距和车顶分支未闭合
23076	23076	Van	Master II				LOW	候选含多轴距与多车顶厢式车。	PENDING: 轴距和车顶分支未闭合
23077	23077	Van	Master II				LOW	候选含多轴距与多车顶厢式车。	PENDING: 轴距和车顶分支未闭合
23078	23078	Van	Master II				LOW	候选含多轴距与多车顶厢式车。	PENDING: 轴距和车顶分支未闭合
23079	23079	Pickup	Master II				LOW	候选含多轴距与驾驶室底盘。	PENDING: 轴距和驾驶室分支未闭合
23080	23080	Pickup	Master II				LOW	候选含多轴距与驾驶室底盘。	PENDING: 轴距和驾驶室分支未闭合
23081	23081	Pickup	Master II				LOW	候选含多轴距与驾驶室底盘。	PENDING: 轴距和驾驶室分支未闭合
23083	23083	Pickup	D-Max I				LOW	候选含不同驾驶室与货斗。	PENDING: 驾驶室和货斗分支未闭合
23093	23093	SUV	Grand Cherokee I facelift	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	HIGH		READY
23094	23094	SUV	Cherokee SJ	SJ			LOW	早期车型命名与车身边界待核。	PENDING: 门数和物理车身未闭合
23095	23095	SUV	Cherokee SJ	SJ			LOW	早期车型命名与车身边界待核。	PENDING: 门数和物理车身未闭合
23096	23096	SUV	Grand Wagoneer				LOW	输入年代与车型命名存在冲突。	PENDING: 平台和物理车身未闭合
23097	23097	SUV	Cherokee XJ	XJ			LOW	候选含三门与五门车身。	PENDING: 门数物理分支未闭合
23098	23098	SUV	Grand Wagoneer				LOW	输入年代与车型命名存在冲突。	PENDING: 平台和物理车身未闭合
23099	23099	SUV	Grand Wagoneer				LOW	输入年代与车型命名存在冲突。	PENDING: 平台和物理车身未闭合
23102	23102	SUV	Discovery I	LJ			LOW	候选含三门与五门车身。	PENDING: 门数物理分支未闭合
23127	23127	Hatchback	309 I				LOW	候选含三门与五门车身。	PENDING: 门数物理分支未闭合
23128	23128	Hatchback	Ibiza III	6L1			LOW	候选含三门与五门车身。	PENDING: 门数物理分支未闭合
23133	23133	Wagon	S124	S124	5	EU-MERCEDES-BENZ-S124-WAGON-5D-01	MEDIUM		READY
23139	23139	MPV	Tourneo Connect I		5		LOW	候选含短轴与长轴车身。	PENDING: 轴距和车顶分支未闭合
23141_prefl	23141	Hatchback	C30 pre-facelift		3	EU-VOLVO-C30-PREFL-HATCHBACK-3D-01	HIGH	改款前物理分支。	READY
23141_facelift	23141	Hatchback	C30 facelift		3	EU-VOLVO-C30-FACELIFT-HATCHBACK-3D-01	HIGH	改款后物理分支。	READY
23144	23144	Wagon	V50 facelift		5	EU-VOLVO-V50-FACELIFT-WAGON-5D-01	HIGH		READY
23145	23145	Wagon	V50 facelift		5	EU-VOLVO-V50-FACELIFT-WAGON-5D-01	HIGH		READY
23146	23146	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23147	23147	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23148	23148	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23149_prefl	23149	Convertible	C70 II pre-facelift		2	EU-VOLVO-C70-II-PREFL-CONVERTIBLE-2D-01	HIGH	改款前物理分支。	READY
23149_facelift	23149	Convertible	C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	改款后物理分支。	READY
23155	23155	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
23156	23156	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	MEDIUM		READY
23157	23157	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH		READY
23162_3dr	23162	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23162_5dr	23162	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23164_prefl	23164	MPV	Golf V Plus		5	EU-VOLKSWAGEN-GOLF-V-PLUS-MPV-5D-01	HIGH	改款前物理分支。	READY
23164_facelift	23164	MPV	Golf VI Plus		5	EU-VOLKSWAGEN-GOLF-VI-PLUS-MPV-5D-01	HIGH	改款后物理分支。	READY
23165	23165	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23166	23166	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23167	23167	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23171	23171	Coupe	Brera	939	3	EU-ALFA-ROMEO-BRERA-COUPE-3D-01	HIGH	来源车型资料归类为三门Coupe。	READY
23172	23172	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
23173	23173	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	4660	1828	1452	Auto-Data Alfa Romeo 159 Sportwagon 2.4 JTDM Q4 specifications;Automobile-Catalog Alfa Romeo 159 Sportwagon 2.4 JTDM Q4 specifications	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-2.4-jtdm-20v-210hp-q4-41981;https://www.automobile-catalog.com/car/2007/222440/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_q4_distinctive.html
EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	4660	1828	1452	Auto-Data Alfa Romeo 159 2.4 JTDM Q4 specifications;Automobile-Catalog Alfa Romeo 159 2.4 JTDM Q4 specifications	https://www.auto-data.net/en/alfa-romeo-159-2.4-jtdm-20v-210hp-q4-42210;https://www.automobile-catalog.com/car/2007/222215/alfa_romeo_159_2_4_jtdm_20v_dpf_q4_distinctive.html
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data BMW 1 Series E81 118i specifications	https://www.auto-data.net/en/bmw-1-series-hatchback-3dr-e81-118i-143hp-steptronic-9807
EU-CITROEN-C8-PHASE-I-MPV-5D-01	4727	1854	1752	Auto-Data Citroen C8 Phase I 2.0 HDi specifications;Automobile-Catalog Citroen C8 2.0 HDi 120 SX specifications	https://www.auto-data.net/en/citroen-c8-phase-i-2.0-hdi-16v-120hp-28089;https://www.automobile-catalog.com/car/2008/1217360/citroen_c8_2_0_hdi_120_sx.html
EU-LAND-ROVER-FREELANDER-II-SUV-5D-01	4500	1910	1740	Auto-Data Land Rover Freelander II 2.2 TD4 specifications	https://www.auto-data.net/bg/land-rover-freelander-ii-2.2-td4-160hp-5177
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458	Auto-Data Renault Megane II Coupe Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-megane-ii-coupe-phase-ii-2006-1.5-dci-103hp-fap-29763
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458	Auto-Data Renault Megane II Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-1.5-dci-103hp-fap-30417
EU-MERCEDES-BENZ-S124-WAGON-5D-01	4765	1740	1489	Auto-Data Mercedes-Benz S124 facelift 250 TD Turbo specifications	https://www.auto-data.net/en/mercedes-benz-s124-facelift-1989-250-td-turbo-126hp-42983
EU-VOLVO-C30-PREFL-HATCHBACK-3D-01	4252	1782	1447	Auto-Data Volvo C30 T5 specifications	https://www.auto-data.net/en/volvo-c30-2.5-i-20v-t5-230hp-43227
EU-VOLVO-C30-FACELIFT-HATCHBACK-3D-01	4266	1782	1447	Auto-Data Volvo C30 facelift T5 specifications	https://www.auto-data.net/en/volvo-c30-facelift-2010-2.5-t5-20v-230hp-43220
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457	Auto-Data Volvo V50 facelift T5 specifications;Auto-Data Volvo V50 facelift T5 AWD specifications	https://www.auto-data.net/en/volvo-v50-facelift-2007-2.5-t5-230hp-17172;https://www.auto-data.net/en/volvo-v50-facelift-2007-2.5-t5-230hp-awd-17174
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II generation specifications	https://www.auto-data.net/en/volvo-s80-ii-generation-1947
EU-VOLVO-C70-II-PREFL-CONVERTIBLE-2D-01	4582	1820	1457	Auto-Data Volvo C70 II T5 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-2.5-t5-20v-230hp-43193
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400	Auto-Data Volvo C70 II facelift T5 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-facelift-2009-2.5-t5-230hp-geartronic-17547
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604	Auto-Data Volvo XC70 II 3.2 AWD specifications	https://www.auto-data.net/en/volvo-xc70-ii-3.2-238hp-awd-9444
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413	Auto-Data Mercedes-Benz CLK C209 facelift CLK 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-clk-200-kompressor-184hp-23428
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-3D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-3-door-1.4-tsi-122hp-8618
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-5D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 5-door body specifications	https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.4-16v-75hp-51655
EU-VOLKSWAGEN-GOLF-V-PLUS-MPV-5D-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-plus-1.4-tsi-122hp-8651
EU-VOLKSWAGEN-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-tsi-122hp-17902
EU-ALFA-ROMEO-BRERA-COUPE-3D-01	4410	1830	1341	Auto-Data Alfa Romeo Brera 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-brera-2.4-jtdm-210hp-41976
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422	Auto-Data Alfa Romeo 159 2.4 JTDM specifications;Automobile-Catalog Alfa Romeo 159 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-159-2.4-jtdm-20v-210hp-42209;https://www.automobile-catalog.com/car/2007/222650/alfa_romeo_159_2_4_jtdm_20v_dpf_distinctive.html
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422	Auto-Data Alfa Romeo 159 Sportwagon 2.4 JTDM specifications;Automobile-Catalog Alfa Romeo 159 Sportwagon 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-2.4-jtdm-20v-210hp-41980;https://www.automobile-catalog.com/car/2007/222770/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_distinctive.html
```

## 下一步优先处理

1. 先闭合 Clio III、Peugeot 309、Ibiza III、Discovery I 的三门/五门分支。
2. 再处理 Modus/Grand Modus、Pathfinder、Range Rover 与 Tourneo Connect 的长短车身和改款边界。
3. 集中拆分 Navara、D-Max、Master II 的驾驶室、货斗、轴距和车顶组合。
4. 最后核对 1980 年代 Cherokee/Grand Wagoneer 的平台与车型命名冲突。

推进信号：CONTINUE

[1]: https://www.lakiauto.ee/admin/upload/Dokumendid/latt_compressed.pdf?utm_source=chatgpt.com "TecDoc"
[2]: https://www.automobile-catalog.com/car/2007/222770/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_distinctive.html "https://www.automobile-catalog.com/car/2007/222770/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_distinctive.html"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Clio III 改款前/后、三门/五门共四个物理分支；完成 Discovery I、Peugeot 309 I、Ibiza III 的门数分支。([汽车数据网][1])
* Modus/Grand Modus 的改款后标准车身与长车身已闭合；改款前车身存在 `1695 mm / 1709 mm` 宽度冲突，未按发动机重复建组，两个改款前分支继续 PENDING。([汽车数据网][2])
* 本轮新增或修改 16 条映射，首次创建 12 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：100
* 当前映射行：118
* READY 映射：95
* PENDING 映射：23
* 已确认尺寸组：61
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23045_prefl_3dr	23045	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	改款前三门物理分支。	READY
23045_prefl_5dr	23045	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	改款前五门物理分支。	READY
23045_facelift_3dr	23045	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	改款后三门物理分支。	READY
23045_facelift_5dr	23045	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	改款后五门物理分支。	READY
23046_modus_prefl	23046	MPV	Modus Phase I		5		LOW	标准短车身改款前分支。	PENDING: 不含后视镜宽度来源冲突
23046_modus_facelift	23046	MPV	Modus Phase II		5	EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	HIGH	标准短车身改款后分支。	READY
23046_grand	23046	MPV	Grand Modus Phase II		5	EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	HIGH	Grand长车身分支。	READY
23047_modus_prefl	23047	MPV	Modus Phase I		5		LOW	标准短车身改款前分支。	PENDING: 不含后视镜宽度来源冲突
23047_modus_facelift	23047	MPV	Modus Phase II		5	EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	HIGH	标准短车身改款后分支。	READY
23047_grand	23047	MPV	Grand Modus Phase II		5	EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	HIGH	Grand长车身分支。	READY
23102_3dr	23102	SUV	Discovery I	LJ	3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	MEDIUM	三门物理分支。	READY
23102_5dr	23102	SUV	Discovery I	LJ	5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	MEDIUM	五门物理分支。	READY
23127_3dr	23127	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
23127_5dr	23127	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
23128_3dr	23128	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
23128_5dr	23128	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-tce-100hp-25151
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 5-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-1.2-16v-tce-100hp-56129
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 3-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-1.2-16v-tce-100hp-35773
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 5-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-5-door-1.2-16v-tce-100hp-56157
EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	3874	1709	1589	Auto-Data Renault Modus Phase II 1.2 TCe specifications	https://www.auto-data.net/en/renault-modus-phase-ii-1.2-tce-16v-100hp-29882
EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	4034	1709	1589	Auto-Data Renault Grand Modus Phase II 1.2 TCe specifications	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-tce-16v-100hp-29937
EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	4520	1795	1915	Auto-Data Land Rover Discovery I 3-door specifications	https://www.auto-data.net/en/land-rover-discovery-i-3.5-i-v8-3-dr-166hp-5231
EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	4520	1795	1960	Auto-Data Land Rover Discovery I 5-door specifications	https://www.auto-data.net/en/land-rover-discovery-i-3.5-i-v8-5-dr-166hp-5233
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Auto-Data Peugeot 309 I 3-door specifications	https://www.auto-data.net/en/peugeot-309-10c-10a-3-door-1.6-105hp-46240
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Auto-Data Peugeot 309 I 5-door specifications	https://www.auto-data.net/en/peugeot-309-10c-10a-1.6-105hp-5442
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.4 86 Hp specifications	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.4-86hp-34934
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.4 86 Hp specifications	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.4-86hp-34934
```

## 下一步优先处理

1. 处理 Range Rover L322、Range Rover Sport L320、Pathfinder R51 的改款分支。
2. 集中拆分 Navara D40、D-Max I、Tourneo Connect I 的驾驶室、货斗和轴距。
3. 批量处理 Master II 的 Bus、Van、底盘驾驶室轴距及车顶组合。
4. 最后闭合 Cherokee SJ/XJ、Grand Wagoneer 的车型命名和平台边界，并解决 Modus 改款前宽度冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-1.2-16v-tce-100hp-56129 "Renault Clio III (Phase I) 5-door 1.2 16V TCe (100 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-modus-phase-ii-1.2-tce-16v-100hp-29882?utm_source=chatgpt.com "Renault Modus (Phase II) 1.2 TCe 16V (100 Hp)"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已将 Modus 改款前宽度冲突闭合为 `1695 mm`，`23046_modus_prefl`、`23047_modus_prefl` 转为 READY。
* Range Rover L322 与 Range Rover Sport L320 均按改款前后拆分；Pathfinder R51 的 `171 PS` 版本闭合为改款前车身。([汽车目录][1])
* `23097` 按 Cherokee XJ 三门、五门拆分；`23096`、`23098` 确认为 Wagoneer XJ 五门并复用 XJ 五门尺寸组，`23099` 则按 4.2 发动机对应 Grand Wagoneer SJ 全尺寸车身独立建组。([汽车目录][2])
* `23139` 按 Tourneo Connect SWB、LWB 两种物理车身拆分。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：100
* 当前映射行：122
* READY 映射：109
* PENDING 映射：13
* 已确认尺寸组：72
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23046_modus_prefl	23046	MPV	Modus Phase I		5	EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	HIGH	标准短车身改款前分支。	READY
23047_modus_prefl	23047	MPV	Modus Phase I		5	EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	HIGH	标准短车身改款前分支。	READY
23050_prefl	23050	SUV	Range Rover III L322	L322	5	EU-LAND-ROVER-RANGE-ROVER-L322-PREFL-SUV-5D-01	HIGH	改款前物理分支。	READY
23050_facelift	23050	SUV	Range Rover III L322 facelift	L322	5	EU-LAND-ROVER-RANGE-ROVER-L322-FACELIFT-SUV-5D-01	HIGH	2010改款物理分支。	READY
23051_prefl	23051	SUV	Range Rover Sport I L320	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-PREFL-SUV-5D-01	HIGH	改款前物理分支。	READY
23051_facelift	23051	SUV	Range Rover Sport I L320 facelift	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-5D-01	HIGH	2009改款物理分支。	READY
23053	23053	SUV	Pathfinder III R51	R51	5	EU-NISSAN-PATHFINDER-R51-PREFL-SUV-5D-01	HIGH		READY
23096	23096	SUV	Wagoneer XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	XJ五门物理车身。	READY
23097_3dr	23097	SUV	Cherokee XJ Phase I	XJ	3	EU-JEEP-XJ-PHASE-I-SUV-3D-01	HIGH	三门物理分支。	READY
23097_5dr	23097	SUV	Cherokee XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	五门物理分支。	READY
23098	23098	SUV	Wagoneer XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	XJ五门物理车身。	READY
23099	23099	SUV	Grand Wagoneer SJ	SJ	5	EU-JEEP-GRAND-WAGONEER-SJ-SUV-5D-01	MEDIUM	4.2发动机对应SJ全尺寸车身。	READY
23139_swb	23139	MPV	Tourneo Connect I Phase II		5	EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-SWB-5D-01	HIGH	短轴物理分支。	READY
23139_lwb	23139	MPV	Tourneo Connect I Phase II		5	EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-LWB-5D-01	HIGH	长轴高车身物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	3792	1695	1589	UltimateSpecs Renault Modus 1.2 16V specifications	https://www.ultimatespecs.com/car-specs/Renault/988/Renault-Modus-12-16v-Base-Authentique.html
EU-LAND-ROVER-RANGE-ROVER-L322-PREFL-SUV-5D-01	4967	1956	1865	Automobile-Catalog 2007 Range Rover TDV8 Vogue specifications	https://www.automobile-catalog.com/car/2007/1404290/range_rover_tdv8_vouge.html
EU-LAND-ROVER-RANGE-ROVER-L322-FACELIFT-SUV-5D-01	4972	1956	1878	Automobile-Catalog 2010 Range Rover TDV8 Vogue DPF specifications	https://www.automobile-catalog.com/car/2010/1404410/range_rover_tdv8_vouge_dpf.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-PREFL-SUV-5D-01	4788	1928	1817	Automobile-Catalog 2008 Range Rover Sport TDV8 specifications	https://www.automobile-catalog.com/car/2008/1405010/range_rover_sport_tdv8_se_dpf.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-5D-01	4783	1928	1789	Automobile-Catalog 2010 Range Rover Sport 3.6 TDV8 specifications	https://www.automobile-catalog.com/car/2010/1405100/range_rover_sport_3_6_tdv8_hse.html
EU-NISSAN-PATHFINDER-R51-PREFL-SUV-5D-01	4740	1850	1783	Automobile-Catalog 2006 Nissan Pathfinder 2.5 dCi specifications	https://www.automobile-catalog.com/car/2006/2313530/nissan_pathfinder_2_5_dci.html
EU-JEEP-XJ-PHASE-I-SUV-3D-01	4200	1790	1624	Automobile-Catalog 1986 Jeep Cherokee Chief 2-door 2.5L specifications	https://www.automobile-catalog.com/car/1986/1309070/jeep_cherokee_chief_2-door_2_5l_5-speed.html
EU-JEEP-XJ-PHASE-I-SUV-5D-01	4200	1790	1609	Automobile-Catalog 1986 Jeep Cherokee 4WD 4-door 2.5L specifications	https://www.automobile-catalog.com/car/1986/1308965/jeep_cherokee_4wd_4-door_2_5l_5-speed.html
EU-JEEP-GRAND-WAGONEER-SJ-SUV-5D-01	4735	1900	1687	Automobile-Catalog 1986 Jeep Grand Wagoneer 4.2L specifications	https://www.automobile-catalog.com/car/1986/1308260/jeep_grand_wagoneer_4_2l.html
EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-SWB-5D-01	4324	1795	1837	Automobile-Catalog 2007 Ford Tourneo Connect SWB 1.8 TDCi 110 specifications	https://www.automobile-catalog.com/car/2007/980375/ford_tourneo_connect_swb_1_8_tdci_110.html
EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-LWB-5D-01	4571	1795	1982	Automobile-Catalog 2007 Ford Tourneo Connect LWB 1.8 TDCi 110 specifications	https://www.automobile-catalog.com/car/2007/980360/ford_tourneo_connect_lwb_1_8_tdci_110.html
```

## 下一步优先处理

1. 集中拆分 `23054` Navara D40 的 King Cab、Double Cab 与货斗外廓。
2. 集中拆分 `23083` D-Max I 的 Single Cab、Space Cab、Crew Cab。
3. 批量处理 `23073–23081` Master II 的 Bus、Van、驾驶室底盘轴距及车顶组合。
4. 最后闭合 `23094–23095` Cherokee SJ 的三门、五门及宽体边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/1404290/range_rover_tdv8_vouge.html?utm_source=chatgpt.com "2006 Range Rover TDV8 Vogue Specs Review (200 kW ..."
[2]: https://www.automobile-catalog.com/car/1986/1308965/jeep_cherokee_4wd_4-door_2_5l_5-speed.html?utm_source=chatgpt.com "1986 Jeep Cherokee 4WD 4-Door 2.5L 5-speed Specs Review (87.5 kW / 119 PS / 117 hp) (since mid-year 1985 for North America U.S.)"
[3]: https://www.automobile-catalog.com/car/2007/980375/ford_tourneo_connect_swb_1_8_tdci_110.html?utm_source=chatgpt.com "2007 Ford Tourneo Connect swb 1.8 TDCi (110) (man. 5)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* `23054` 已按 Navara D40 的 King Cab、Double Cab 两种驾驶室拆分；两者三维相同，但驾驶室与货斗比例不同，因此保留独立尺寸组。
* `23076–23078` 已一次性闭合 Master II 厢式车的 6 种轴距/车顶组合，并批量复用于三种发动机版本。宽度均采用官方资料明确标注的不含后视镜口径。
* `23094–23095` 已拆为 Cherokee SJ 两门标准宽体、两门 Wide-Track、四门标准车身三个分支；四门版本未套用 Wide-Track 外廓。([汽车目录档案][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：100
* 当前映射行：142
* READY 映射：135
* PENDING 映射：7
* 已确认尺寸组：83
* 剩余 PENDING：Master II Bus 3 条、Master II Pritsche/Fahrgestell 3 条、D-Max I 1 条
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
23054_kingcab	23054	Pickup	Navara III D40	D40		EU-NISSAN-NAVARA-D40-KING-CAB-PICKUP-01	MEDIUM	King Cab物理分支。	READY
23054_doublecab	23054	Pickup	Navara III D40	D40	4	EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-01	MEDIUM	Double Cab物理分支。	READY
23076_l1h1	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23076_l1h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23076_l2h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23076_l2h3	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23076_l3h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23076_l3h3	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23077_l1h1	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23077_l1h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23077_l2h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23077_l2h3	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23077_l3h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23077_l3h3	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23078_l1h1	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23078_l1h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23078_l2h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23078_l2h3	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23078_l3h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23078_l3h3	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23094_2dr	23094	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	MEDIUM	两门标准轮距物理分支。	READY
23094_2dr_widetrack	23094	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	MEDIUM	两门Wide-Track物理分支。	READY
23094_4dr	23094	SUV	Cherokee SJ	SJ	4	EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	MEDIUM	四门标准轮距物理分支。	READY
23095_2dr	23095	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	MEDIUM	两门标准轮距物理分支。	READY
23095_2dr_widetrack	23095	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	MEDIUM	两门Wide-Track物理分支。	READY
23095_4dr	23095	SUV	Cherokee SJ	SJ	4	EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	MEDIUM	四门标准轮距物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NAVARA-D40-KING-CAB-PICKUP-01	5220	1850	1774	Auto-Data Nissan Navara III D40 King Cab specifications	https://www.auto-data.net/de/nissan-navara-iii-d40-2.5-dci-king-cab-174hp-4wd-826
EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-01	5220	1850	1774	Auto-Data Nissan Navara III D40 Double Cab specifications	https://www.auto-data.net/fi/nissan-navara-iii-d40-2.5-dci-double-cab-174hp-4wd-824
EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	4899	1990	2253	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	4899	1990	2496	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	5399	1990	2493	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	5399	1990	2721	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	5899	1990	2490	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	5899	1990	2720	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
```

## 下一步优先处理

1. 闭合 `23073–23075` Master II Bus 的轴距与车顶组合，并确认哪些厢式车尺寸组可合法复用。
2. 闭合 `23079–23081` Master II Pritsche/Fahrgestell 的中轴、长轴以及平台车身边界。
3. 最后拆分 `23083` D-Max I 的 Single Cab、Space Cab、Crew Cab，并统一后驱版本的不含后视镜宽度口径。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf?utm_source=chatgpt.com "Jeep Cherokee (1980) USA"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合最后 7 个 PENDING Ktype。Master II Bus 复用已确认的 6 个轴距/车顶外廓组；Master II 底盘驾驶室新增 MWB、LWB 两组；D-Max I 按 Single Cab、Space Cab、Double Cab 拆分。Master II 的宽度均采用官方资料明确标注的不含后视镜口径。([Vauxhall][1])
* 已完成轻量机械检查：两张表列数正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、无孤立尺寸组、尺寸和来源字段完整。
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* 最终 Ktype 映射行：162
* READY 映射：162
* PENDING 映射：0
* 最终 DIMENSION_GROUP：88
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22948	22948	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22949	22949	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22950	22950	Hatchback	Fabia II		5	EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	HIGH		READY
22951	22951	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	HIGH		READY
22952	22952	Sedan	159	939	4	EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	HIGH		READY
22953	22953	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22954	22954	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22955	22955	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22956	22956	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
22957	22957	Convertible	3 Series E93	E93	2	EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	HIGH	E93硬顶敞篷车身。	READY
22966	22966	Sedan	Diamante I		4	EU-MITSUBISHI-DIAMANTE-I-SEDAN-4D-01	MEDIUM		READY
22973	22973	Sedan	City IV (GD)		4	EU-HONDA-CITY-GD-SEDAN-4D-01	MEDIUM		READY
22974	22974	Sedan	City IV (GD)		4	EU-HONDA-CITY-GD-SEDAN-4D-01	HIGH		READY
22992	22992	Sedan	Belta XP90	SCP92	4	EU-TOYOTA-YARIS-BELTA-SCP92-SEDAN-4D-01	HIGH	Yaris三厢版对应Belta/SCP92。	READY
23011	23011	Sedan	Camry XV30		4	EU-TOYOTA-CAMRY-XV30-SEDAN-4D-01	MEDIUM		READY
23014	23014	Sedan	Camry V20		4	EU-TOYOTA-CAMRY-V20-SEDAN-4D-4WD-01	HIGH		READY
23045_prefl_3dr	23045	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	MEDIUM	改款前三门物理分支。	READY
23045_prefl_5dr	23045	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	MEDIUM	改款前五门物理分支。	READY
23045_facelift_3dr	23045	Hatchback	Clio III Phase II		3	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	MEDIUM	改款后三门物理分支。	READY
23045_facelift_5dr	23045	Hatchback	Clio III Phase II		5	EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	MEDIUM	改款后五门物理分支。	READY
23046_modus_prefl	23046	MPV	Modus Phase I		5	EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	HIGH	标准短车身改款前分支。	READY
23046_modus_facelift	23046	MPV	Modus Phase II		5	EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	HIGH	标准短车身改款后分支。	READY
23046_grand	23046	MPV	Grand Modus Phase II		5	EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	HIGH	Grand长车身分支。	READY
23047_modus_prefl	23047	MPV	Modus Phase I		5	EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	HIGH	标准短车身改款前分支。	READY
23047_modus_facelift	23047	MPV	Modus Phase II		5	EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	HIGH	标准短车身改款后分支。	READY
23047_grand	23047	MPV	Grand Modus Phase II		5	EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	HIGH	Grand长车身分支。	READY
23048	23048	MPV	C8 Phase I		5	EU-CITROEN-C8-PHASE-I-MPV-5D-01	HIGH		READY
23049	23049	SUV	Freelander 2	L359	5	EU-LAND-ROVER-FREELANDER-II-SUV-5D-01	MEDIUM		READY
23050_prefl	23050	SUV	Range Rover III L322	L322	5	EU-LAND-ROVER-RANGE-ROVER-L322-PREFL-SUV-5D-01	HIGH	改款前物理分支。	READY
23050_facelift	23050	SUV	Range Rover III L322 facelift	L322	5	EU-LAND-ROVER-RANGE-ROVER-L322-FACELIFT-SUV-5D-01	HIGH	2010改款物理分支。	READY
23051_prefl	23051	SUV	Range Rover Sport I L320	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-PREFL-SUV-5D-01	HIGH	改款前物理分支。	READY
23051_facelift	23051	SUV	Range Rover Sport I L320 facelift	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-5D-01	HIGH	2009改款物理分支。	READY
23052	23052	Sedan	Opirus facelift		4	EU-KIA-OPIRUS-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23053	23053	SUV	Pathfinder III R51	R51	5	EU-NISSAN-PATHFINDER-R51-PREFL-SUV-5D-01	HIGH		READY
23054_kingcab	23054	Pickup	Navara III D40	D40		EU-NISSAN-NAVARA-D40-KING-CAB-PICKUP-01	MEDIUM	King Cab物理分支。	READY
23054_doublecab	23054	Pickup	Navara III D40	D40	4	EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-01	MEDIUM	Double Cab物理分支。	READY
23056	23056	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	MEDIUM		READY
23060	23060	Wagon	Megane II Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
23061	23061	Wagon	Megane II Phase II		5	EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	HIGH		READY
23062	23062	Sedan	Megane II Classic Phase II		4	EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	HIGH		READY
23063	23063	Sedan	Megane II Classic	LM	4	EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	MEDIUM		READY
23064_3dr	23064	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23064_5dr	23064	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23065_3dr	23065	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23065_5dr	23065	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23066_3dr	23066	Hatchback	Megane II Phase II	CM	3	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23066_5dr	23066	Hatchback	Megane II Phase II	BM	5	EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23069	23069	Convertible	Megane II Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	Coupe-Cabriolet物理车身。	READY
23070	23070	Convertible	Megane II Phase II		2	EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	HIGH	Coupe-Cabriolet物理车身。	READY
23071	23071	MPV	Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH		READY
23072_prefl	23072	MPV	Scenic II Phase I		5	EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	MEDIUM	生产区间覆盖Phase I分支。	READY
23072_facelift	23072	MPV	Scenic II Phase II		5	EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	HIGH	生产区间覆盖Phase II分支。	READY
23073_l1h1	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴标准顶客运车分支。	READY
23073_l1h2	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶客运车分支。	READY
23073_l2h2	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶客运车分支。	READY
23073_l2h3	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶客运车分支。	READY
23073_l3h2	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶客运车分支。	READY
23073_l3h3	23073	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶客运车分支。	READY
23074_l1h1	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴标准顶客运车分支。	READY
23074_l1h2	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶客运车分支。	READY
23074_l2h2	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶客运车分支。	READY
23074_l2h3	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶客运车分支。	READY
23074_l3h2	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶客运车分支。	READY
23074_l3h3	23074	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶客运车分支。	READY
23075_l1h1	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴标准顶客运车分支。	READY
23075_l1h2	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶客运车分支。	READY
23075_l2h2	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶客运车分支。	READY
23075_l2h3	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶客运车分支。	READY
23075_l3h2	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶客运车分支。	READY
23075_l3h3	23075	MPV	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶客运车分支。	READY
23076_l1h1	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23076_l1h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23076_l2h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23076_l2h3	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23076_l3h2	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23076_l3h3	23076	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23077_l1h1	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23077_l1h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23077_l2h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23077_l2h3	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23077_l3h2	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23077_l3h3	23077	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23078_l1h1	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶物理分支。	READY
23078_l1h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶物理分支。	READY
23078_l2h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	MEDIUM	L2H2中轴高顶物理分支。	READY
23078_l2h3	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	MEDIUM	L2H3中轴超高顶物理分支。	READY
23078_l3h2	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	MEDIUM	L3H2长轴高顶物理分支。	READY
23078_l3h3	23078	Van	Master II Phase II			EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	MEDIUM	L3H3长轴超高顶物理分支。	READY
23079_mwb	23079	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-MWB-2D-01	MEDIUM	中轴底盘驾驶室分支。	READY
23079_lwb	23079	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-LWB-2D-01	MEDIUM	长轴底盘驾驶室分支。	READY
23080_mwb	23080	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-MWB-2D-01	MEDIUM	中轴底盘驾驶室分支。	READY
23080_lwb	23080	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-LWB-2D-01	MEDIUM	长轴底盘驾驶室分支。	READY
23081_mwb	23081	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-MWB-2D-01	MEDIUM	中轴底盘驾驶室分支。	READY
23081_lwb	23081	Pickup	Master II Phase II		2	EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-LWB-2D-01	MEDIUM	长轴底盘驾驶室分支。	READY
23083_singlecab	23083	Pickup	D-Max I	TFR	2	EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	MEDIUM	Single Cab物理分支。	READY
23083_spacecab	23083	Pickup	D-Max I	TFR	2	EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	MEDIUM	Space Cab物理分支。	READY
23083_doublecab	23083	Pickup	D-Max I	TFR	4	EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	MEDIUM	Double Cab物理分支。	READY
23092	23092	SUV	Grand Cherokee I facelift	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	HIGH		READY
23093	23093	SUV	Grand Cherokee I facelift	ZJ	5	EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	HIGH		READY
23094_2dr	23094	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	MEDIUM	两门标准轮距物理分支。	READY
23094_2dr_widetrack	23094	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	MEDIUM	两门Wide-Track物理分支。	READY
23094_4dr	23094	SUV	Cherokee SJ	SJ	4	EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	MEDIUM	四门标准轮距物理分支。	READY
23095_2dr	23095	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	MEDIUM	两门标准轮距物理分支。	READY
23095_2dr_widetrack	23095	SUV	Cherokee SJ	SJ	2	EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	MEDIUM	两门Wide-Track物理分支。	READY
23095_4dr	23095	SUV	Cherokee SJ	SJ	4	EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	MEDIUM	四门标准轮距物理分支。	READY
23096	23096	SUV	Wagoneer XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	XJ五门物理车身。	READY
23097_3dr	23097	SUV	Cherokee XJ Phase I	XJ	3	EU-JEEP-XJ-PHASE-I-SUV-3D-01	HIGH	三门物理分支。	READY
23097_5dr	23097	SUV	Cherokee XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	五门物理分支。	READY
23098	23098	SUV	Wagoneer XJ Phase I	XJ	5	EU-JEEP-XJ-PHASE-I-SUV-5D-01	HIGH	XJ五门物理车身。	READY
23099	23099	SUV	Grand Wagoneer SJ	SJ	5	EU-JEEP-GRAND-WAGONEER-SJ-SUV-5D-01	MEDIUM	4.2发动机对应SJ全尺寸车身。	READY
23102_3dr	23102	SUV	Discovery I	LJ	3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	MEDIUM	三门物理分支。	READY
23102_5dr	23102	SUV	Discovery I	LJ	5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	MEDIUM	五门物理分支。	READY
23127_3dr	23127	Hatchback	309 I	10C	3	EU-PEUGEOT-309-I-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
23127_5dr	23127	Hatchback	309 I	10A	5	EU-PEUGEOT-309-I-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
23128_3dr	23128	Hatchback	Ibiza III facelift	6L1	3	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
23128_5dr	23128	Hatchback	Ibiza III facelift	6L1	5	EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
23132	23132	MPV	Combo Tour C facelift		5	EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	HIGH		READY
23133	23133	Wagon	S124	S124	5	EU-MERCEDES-BENZ-S124-WAGON-5D-01	MEDIUM		READY
23135	23135	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23136	23136	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23137	23137	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23138	23138	Sedan	C-Class W204 pre-facelift	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	MEDIUM	版本名称限定改款前W204外廓。	READY
23139_swb	23139	MPV	Tourneo Connect I Phase II		5	EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-SWB-5D-01	HIGH	短轴物理分支。	READY
23139_lwb	23139	MPV	Tourneo Connect I Phase II		5	EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-LWB-5D-01	HIGH	长轴高车身物理分支。	READY
23140	23140	Convertible	GT II		2	EU-OPEL-GT-II-CONVERTIBLE-2D-01	HIGH		READY
23141_prefl	23141	Hatchback	C30 pre-facelift		3	EU-VOLVO-C30-PREFL-HATCHBACK-3D-01	HIGH	改款前物理分支。	READY
23141_facelift	23141	Hatchback	C30 facelift		3	EU-VOLVO-C30-FACELIFT-HATCHBACK-3D-01	HIGH	改款后物理分支。	READY
23142	23142	Sedan	S40 II facelift		4	EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23143	23143	Sedan	S40 II facelift		4	EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	MEDIUM		READY
23144	23144	Wagon	V50 facelift		5	EU-VOLVO-V50-FACELIFT-WAGON-5D-01	HIGH		READY
23145	23145	Wagon	V50 facelift		5	EU-VOLVO-V50-FACELIFT-WAGON-5D-01	HIGH		READY
23146	23146	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23147	23147	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23148	23148	Sedan	S80 II		4	EU-VOLVO-S80-II-SEDAN-4D-01	HIGH		READY
23149_prefl	23149	Convertible	C70 II pre-facelift		2	EU-VOLVO-C70-II-PREFL-CONVERTIBLE-2D-01	HIGH	改款前物理分支。	READY
23149_facelift	23149	Convertible	C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	改款后物理分支。	READY
23150	23150	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23151	23151	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23152	23152	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23153	23153	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23154	23154	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-5D-PREFL-01	HIGH		READY
23155	23155	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
23156	23156	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	MEDIUM		READY
23157	23157	Coupe	CLK C209 facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH		READY
23158	23158	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	HIGH		READY
23159	23159	Convertible	CLK A209 facelift	A209	2	EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	HIGH	CLK 500高度独立。	READY
23160	23160	Coupe	V8 Vantage 2005		2	EU-ASTON-MARTIN-V8-VANTAGE-2005-COUPE-2D-01	HIGH		READY
23161	23161	Convertible	V8 Vantage Roadster 2005		2	EU-ASTON-MARTIN-V8-VANTAGE-2005-ROADSTER-2D-01	HIGH		READY
23162_3dr	23162	Hatchback	Golf V	1K1	3	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
23162_5dr	23162	Hatchback	Golf V	1K1	5	EU-VOLKSWAGEN-GOLF-V-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
23163	23163	Wagon	Golf V Variant		5	EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
23164_prefl	23164	MPV	Golf V Plus		5	EU-VOLKSWAGEN-GOLF-V-PLUS-MPV-5D-01	HIGH	改款前物理分支。	READY
23164_facelift	23164	MPV	Golf VI Plus		5	EU-VOLKSWAGEN-GOLF-VI-PLUS-MPV-5D-01	HIGH	改款后物理分支。	READY
23165	23165	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23166	23166	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23167	23167	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	MEDIUM		READY
23168	23168	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23169	23169	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23170	23170	Wagon	Fabia II Combi		5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH		READY
23171	23171	Coupe	Brera	939	3	EU-ALFA-ROMEO-BRERA-COUPE-3D-01	HIGH	来源车型资料归类为三门Coupe。	READY
23172	23172	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
23173	23173	Wagon	159 Sportwagon	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1501-1600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FABIA-II-HATCHBACK-5D-PREFL-01	3992	1642	1498	Auto-Data Skoda Fabia II specifications	https://www.auto-data.net/en/skoda-fabia-ii-generation-3089
EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	4660	1828	1452	Auto-Data Alfa Romeo 159 Sportwagon 2.4 JTDM Q4 specifications;Automobile-Catalog Alfa Romeo 159 Sportwagon 2.4 JTDM Q4 specifications	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-2.4-jtdm-20v-210hp-q4-41981;https://www.automobile-catalog.com/car/2007/222440/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_q4_distinctive.html
EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	4660	1828	1452	Auto-Data Alfa Romeo 159 2.4 JTDM Q4 specifications;Automobile-Catalog Alfa Romeo 159 2.4 JTDM Q4 specifications	https://www.auto-data.net/en/alfa-romeo-159-2.4-jtdm-20v-210hp-q4-42210;https://www.automobile-catalog.com/car/2007/222215/alfa_romeo_159_2_4_jdtm_20v_dpf_q4_distinctive.html
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data BMW 1 Series E81 118i specifications	https://www.auto-data.net/en/bmw-1-series-hatchback-3dr-e81-118i-143hp-steptronic-9807
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384	Auto-Data BMW 3 Series Convertible E93 325i specifications	https://www.auto-data.net/en/bmw-3-series-convertible-e93-325i-218hp-9961
EU-MITSUBISHI-DIAMANTE-I-SEDAN-4D-01	4740	1775	1410	Auto-Data Mitsubishi Diamante I 3.0 V6 specifications	https://www.auto-data.net/en/mitsubishi-diamante-i-3.0-i-v6-24v-210hp-15474
EU-HONDA-CITY-GD-SEDAN-4D-01	4310	1690	1485	Automobile-Catalog Honda City ZX 1.5 i-DSI;Automobile-Catalog Honda City 1.5V	https://www.automobile-catalog.com/car/2002/1270775/honda_city_zx_1_5a_i-dsi.html;https://www.automobile-catalog.com/car/2004/1270745/honda_city_1_5v.html
EU-TOYOTA-YARIS-BELTA-SCP92-SEDAN-4D-01	4300	1690	1460	Toyota 75 Years Belta official specifications	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60012570/index.html
EU-TOYOTA-CAMRY-XV30-SEDAN-4D-01	4815	1795	1500	Auto-Data Toyota Camry V XV30 generation specifications	https://www.auto-data.net/en/toyota-camry-v-xv30-generation-1011
EU-TOYOTA-CAMRY-V20-SEDAN-4D-4WD-01	4520	1710	1400	Toyota Camry GLi 4WD official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Camry-Gen2-4WD-archive-launch-pack-1988.pdf
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.2-16v-tce-100hp-25151
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 5-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-1.2-16v-tce-100hp-56129
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 3-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-3-door-1.2-16v-tce-100hp-35773
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497	Auto-Data Renault Clio III Phase II 5-door 1.2 TCe specifications	https://www.auto-data.net/en/renault-clio-iii-phase-ii-2009-5-door-1.2-16v-tce-100hp-56157
EU-RENAULT-MODUS-PHASE-I-MPV-5D-01	3792	1695	1589	UltimateSpecs Renault Modus 1.2 16V specifications	https://www.ultimatespecs.com/car-specs/Renault/988/Renault-Modus-12-16v-Base-Authentique.html
EU-RENAULT-MODUS-PHASE-II-MPV-5D-01	3874	1709	1589	Auto-Data Renault Modus Phase II 1.2 TCe specifications	https://www.auto-data.net/en/renault-modus-phase-ii-1.2-tce-16v-100hp-29882
EU-RENAULT-GRAND-MODUS-PHASE-II-MPV-5D-01	4034	1709	1589	Auto-Data Renault Grand Modus Phase II 1.2 TCe specifications	https://www.auto-data.net/en/renault-grand-modus-phase-ii-2008-1.2-tce-16v-100hp-29937
EU-CITROEN-C8-PHASE-I-MPV-5D-01	4727	1854	1752	Auto-Data Citroen C8 Phase I 2.0 HDi specifications;Automobile-Catalog Citroen C8 2.0 HDi 120 SX specifications	https://www.auto-data.net/en/citroen-c8-phase-i-2.0-hdi-16v-120hp-28089;https://www.automobile-catalog.com/car/2008/1217360/citroen_c8_2_0_hdi_120_sx.html
EU-LAND-ROVER-FREELANDER-II-SUV-5D-01	4500	1910	1740	Auto-Data Land Rover Freelander II 2.2 TD4 specifications	https://www.auto-data.net/bg/land-rover-freelander-ii-2.2-td4-160hp-5177
EU-LAND-ROVER-RANGE-ROVER-L322-PREFL-SUV-5D-01	4967	1956	1865	Automobile-Catalog 2007 Range Rover TDV8 Vogue specifications	https://www.automobile-catalog.com/car/2007/1404290/range_rover_tdv8_vouge.html
EU-LAND-ROVER-RANGE-ROVER-L322-FACELIFT-SUV-5D-01	4972	1956	1878	Automobile-Catalog 2010 Range Rover TDV8 Vogue DPF specifications	https://www.automobile-catalog.com/car/2010/1404410/range_rover_tdv8_vouge_dpf.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-PREFL-SUV-5D-01	4788	1928	1817	Automobile-Catalog 2008 Range Rover Sport TDV8 specifications	https://www.automobile-catalog.com/car/2008/1405010/range_rover_sport_tdv8_se_dpf.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-L320-FACELIFT-SUV-5D-01	4783	1928	1789	Automobile-Catalog 2010 Range Rover Sport 3.6 TDV8 specifications	https://www.automobile-catalog.com/car/2010/1405100/range_rover_sport_3_6_tdv8_hse.html
EU-KIA-OPIRUS-FACELIFT-SEDAN-4D-01	4970	1850	1486	Auto-Data Kia Opirus 3.8 V6 specifications	https://www.auto-data.net/en/kia-opirus-3.8-i-v6-24v-266hp-2677
EU-NISSAN-PATHFINDER-R51-PREFL-SUV-5D-01	4740	1850	1783	Automobile-Catalog 2006 Nissan Pathfinder 2.5 dCi specifications	https://www.automobile-catalog.com/car/2006/2313530/nissan_pathfinder_2_5_dci.html
EU-NISSAN-NAVARA-D40-KING-CAB-PICKUP-01	5220	1850	1774	Auto-Data Nissan Navara III D40 King Cab specifications	https://www.auto-data.net/de/nissan-navara-iii-d40-2.5-dci-king-cab-174hp-4wd-826
EU-NISSAN-NAVARA-D40-DOUBLE-CAB-PICKUP-4D-01	5220	1850	1774	Auto-Data Nissan Navara III D40 Double Cab specifications	https://www.auto-data.net/fi/nissan-navara-iii-d40-2.5-dci-double-cab-174hp-4wd-824
EU-VOLVO-XC90-I-FACELIFT-SUV-5D-01	4798	1898	1743	Auto-Data Volvo XC90 facelift 3.2 AWD specifications	https://www.auto-data.net/en/volvo-xc90-facelift-2007-3.2i-238hp-awd-automatic-9531
EU-RENAULT-MEGANE-II-GRANDTOUR-PHASE-II-WAGON-5D-01	4500	1777	1467	Auto-Data Renault Megane II Grandtour Phase II 1.6 16V specifications	https://www.auto-data.net/en/renault-megane-ii-grandtour-phase-ii-2006-1.6-16v-112hp-30357
EU-RENAULT-MEGANE-II-CLASSIC-PHASE-II-SEDAN-4D-01	4498	1777	1460	Automobile-Catalog Renault Megane Classic 1.6 16V;Automobile-Catalog Renault Megane Classic body dimensions	https://www.automobile-catalog.com/car/2006/2954570/renault_megane_classic_1_6_16v.html;https://www.automobile-catalog.com/car/2006/2954600/renault_megane_classic_2_0_16v.html
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-3D-01	4209	1777	1458	Auto-Data Renault Megane II Coupe Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-megane-ii-coupe-phase-ii-2006-1.5-dci-103hp-fap-29763
EU-RENAULT-MEGANE-II-PHASE-II-HATCHBACK-5D-01	4209	1777	1458	Auto-Data Renault Megane II Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-1.5-dci-103hp-fap-30417
EU-RENAULT-MEGANE-II-CC-PHASE-II-CONVERTIBLE-2D-01	4355	1777	1404	Auto-Data Renault Megane II CC Phase II specifications	https://www.auto-data.net/en/renault-megane-ii-cc-phase-ii-2006-generation-5609
EU-RENAULT-SCENIC-II-PHASE-II-MPV-5D-01	4263	1805	1620	Auto-Data Renault Scenic II Phase II 1.5 dCi specifications	https://www.auto-data.net/en/renault-scenic-ii-phase-ii-1.5-dci-103hp-fap-39496
EU-RENAULT-SCENIC-II-PHASE-I-MPV-5D-01	4259	1810	1620	Automobile-Catalog Renault Scenic 1.6 16V specifications	https://www.automobile-catalog.com/car/2005/2955185/renault_scenic_1_6_16v.html
EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H1-01	4899	1990	2253	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L1H2-01	4899	1990	2496	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H2-01	5399	1990	2493	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L2H3-01	5399	1990	2721	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H2-01	5899	1990	2490	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-VAN-L3H3-01	5899	1990	2720	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-MWB-2D-01	5369	1990	2200	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-RENAULT-MASTER-II-PHASE-II-CHASSIS-CAB-LWB-2D-01	5869	1990	2195	Vauxhall Movano 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf
EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	5030	1720	1635	Auto-Data Isuzu D-Max I 2.5 TD Single Cab specifications	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-single-cab-136hp-15975
EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	5030	1800	1715	Auto-Data Isuzu D-Max I 2.5 TD Space Cab specifications	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	5035	1800	1735	Auto-Data Isuzu D-Max I 2.5 TD Double Cab specifications	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974
EU-JEEP-GRAND-CHEROKEE-ZJ-FACELIFT-SUV-5D-01	4501	1760	1648	Auto-Data Jeep Grand Cherokee I ZJ 5.2 V8 specifications	https://www.auto-data.net/en/jeep-grand-cherokee-i-zj-5.2i-v8-223hp-automatic-31841
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700	Jeep Cherokee 1980 official brochure;CarBackCatalogue brochure specifications	https://autocatalogarchive.com/wp-content/uploads/2017/03/Jeep-Cherokee-1980-USA-.pdf;https://carbackcatalogue.com/cars/jeep/models/cherokee/1980-1989/1980/1980-jeep-cherokee-us-brochure-specs-info.html
EU-JEEP-XJ-PHASE-I-SUV-5D-01	4200	1790	1609	Automobile-Catalog 1986 Jeep Cherokee 4WD 4-door 2.5L specifications	https://www.automobile-catalog.com/car/1986/1308965/jeep_cherokee_4wd_4-door_2_5l_5-speed.html
EU-JEEP-XJ-PHASE-I-SUV-3D-01	4200	1790	1624	Automobile-Catalog 1986 Jeep Cherokee Chief 2-door 2.5L specifications	https://www.automobile-catalog.com/car/1986/1309070/jeep_cherokee_chief_2-door_2_5l_5-speed.html
EU-JEEP-GRAND-WAGONEER-SJ-SUV-5D-01	4735	1900	1687	Automobile-Catalog 1986 Jeep Grand Wagoneer 4.2L specifications	https://www.automobile-catalog.com/car/1986/1308260/jeep_grand_wagoneer_4_2l.html
EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	4520	1795	1915	Auto-Data Land Rover Discovery I 3-door specifications	https://www.auto-data.net/en/land-rover-discovery-i-3.5-i-v8-3-dr-166hp-5231
EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	4520	1795	1960	Auto-Data Land Rover Discovery I 5-door specifications	https://www.auto-data.net/en/land-rover-discovery-i-3.5-i-v8-5-dr-166hp-5233
EU-PEUGEOT-309-I-HATCHBACK-3D-01	4051	1628	1380	Auto-Data Peugeot 309 I 3-door specifications	https://www.auto-data.net/en/peugeot-309-10c-10a-3-door-1.6-105hp-46240
EU-PEUGEOT-309-I-HATCHBACK-5D-01	4051	1628	1380	Auto-Data Peugeot 309 I 5-door specifications	https://www.auto-data.net/en/peugeot-309-10c-10a-1.6-105hp-5442
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.4 86 Hp specifications	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.4-86hp-34934
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	3977	1698	1441	Auto-Data Seat Ibiza III facelift 1.4 86 Hp specifications	https://www.auto-data.net/en/seat-ibiza-iii-facelift-2006-1.4-86hp-34934
EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	4322	1684	1801	Auto-Data Opel Combo Tour C facelift 1.7 CDTI specifications	https://www.auto-data.net/de/opel-combo-tour-c-facelift-2003-1.7-cdti-100hp-1767
EU-MERCEDES-BENZ-S124-WAGON-5D-01	4765	1740	1489	Auto-Data Mercedes-Benz S124 facelift 250 TD Turbo specifications	https://www.auto-data.net/en/mercedes-benz-s124-facelift-1989-250-td-turbo-126hp-42983
EU-MERCEDES-BENZ-C-CLASS-W204-PREFL-SEDAN-4D-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 280 4MATIC specifications	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-280-v6-231hp-4matic-7g-tronic-12545
EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-SWB-5D-01	4324	1795	1837	Automobile-Catalog 2007 Ford Tourneo Connect SWB 1.8 TDCi 110 specifications	https://www.automobile-catalog.com/car/2007/980375/ford_tourneo_connect_swb_1_8_tdci_110.html
EU-FORD-TOURNEO-CONNECT-I-PHASE-II-MPV-LWB-5D-01	4571	1795	1982	Automobile-Catalog 2007 Ford Tourneo Connect LWB 1.8 TDCi 110 specifications	https://www.automobile-catalog.com/car/2007/980360/ford_tourneo_connect_lwb_1_8_tdci_110.html
EU-OPEL-GT-II-CONVERTIBLE-2D-01	4100	1813	1274	Auto-Data Opel GT II 2.0 GT specifications	https://www.auto-data.net/en/opel-gt-ii-2.0-gt-264hp-1744
EU-VOLVO-C30-PREFL-HATCHBACK-3D-01	4252	1782	1447	Auto-Data Volvo C30 T5 specifications	https://www.auto-data.net/en/volvo-c30-2.5-i-20v-t5-230hp-43227
EU-VOLVO-C30-FACELIFT-HATCHBACK-3D-01	4266	1782	1447	Auto-Data Volvo C30 facelift T5 specifications	https://www.auto-data.net/en/volvo-c30-facelift-2010-2.5-t5-20v-230hp-43220
EU-VOLVO-S40-II-FACELIFT-SEDAN-4D-01	4476	1770	1454	Auto-Data Volvo S40 II facelift T5 specifications	https://www.auto-data.net/en/volvo-s40-ii-facelift-2007-2.5-t5-230hp-geartronic-17554
EU-VOLVO-V50-FACELIFT-WAGON-5D-01	4522	1770	1457	Auto-Data Volvo V50 facelift T5 specifications;Auto-Data Volvo V50 facelift T5 AWD specifications	https://www.auto-data.net/en/volvo-v50-facelift-2007-2.5-t5-230hp-17172;https://www.auto-data.net/en/volvo-v50-facelift-2007-2.5-t5-230hp-awd-17174
EU-VOLVO-S80-II-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II generation specifications	https://www.auto-data.net/en/volvo-s80-ii-generation-1947
EU-VOLVO-C70-II-PREFL-CONVERTIBLE-2D-01	4582	1820	1457	Auto-Data Volvo C70 II T5 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-2.5-t5-20v-230hp-43193
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400	Auto-Data Volvo C70 II facelift T5 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-facelift-2009-2.5-t5-230hp-geartronic-17547
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547	Auto-Data Volvo V70 III 2.5 T specifications	https://www.auto-data.net/en/volvo-v70-iii-2.5-t-200hp-9233
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604	Auto-Data Volvo XC70 II 3.2 AWD specifications	https://www.auto-data.net/en/volvo-xc70-ii-3.2-238hp-awd-9444
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413	Auto-Data Mercedes-Benz CLK C209 facelift CLK 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-clk-200-kompressor-184hp-23428
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413	Auto-Data Mercedes-Benz CLK A209 facelift CLK 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-clk-a209-facelift-2005-clk-200-kompressor-184hp-5g-tronic-52931
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415	Auto-Data Mercedes-Benz CLK A209 facelift CLK 500 specifications	https://www.auto-data.net/en/mercedes-benz-clk-a209-facelift-2005-clk-500-388hp-7g-tronic-23480
EU-ASTON-MARTIN-V8-VANTAGE-2005-COUPE-2D-01	4383	1866	1255	Auto-Data Aston Martin V8 Vantage 2005 4.3 specifications	https://www.auto-data.net/en/aston-martin-v8-vantage-2005-4.3-i-v8-32v-385hp-3054
EU-ASTON-MARTIN-V8-VANTAGE-2005-ROADSTER-2D-01	4383	1866	1255	Auto-Data Aston Martin V8 Vantage Roadster 2005 4.3 specifications	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-2005-4.3-i-v8-32v-385hp-3055
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-3D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-3-door-1.4-tsi-122hp-8618
EU-VOLKSWAGEN-GOLF-V-HATCHBACK-5D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 5-door body specifications	https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.4-16v-75hp-51655
EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Auto-Data Volkswagen Golf V Variant 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.4-tsi-122hp-8638
EU-VOLKSWAGEN-GOLF-V-PLUS-MPV-5D-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-v-plus-1.4-tsi-122hp-8651
EU-VOLKSWAGEN-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus 1.4 TSI specifications	https://www.auto-data.net/en/volkswagen-golf-vi-plus-1.4-tsi-122hp-17902
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498	Auto-Data Skoda Fabia II Combi 1.4 TDI specifications	https://www.auto-data.net/en/skoda-fabia-ii-combi-1.4-tdi-70hp-14140
EU-ALFA-ROMEO-BRERA-COUPE-3D-01	4410	1830	1341	Auto-Data Alfa Romeo Brera 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-brera-2.4-jtdm-210hp-41976
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422	Auto-Data Alfa Romeo 159 2.4 JTDM specifications;Automobile-Catalog Alfa Romeo 159 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-159-2.4-jtdm-20v-210hp-42209;https://www.automobile-catalog.com/car/2007/222650/alfa_romeo_159_2_4_jdtm_20v_dpf_distinctive.html
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422	Auto-Data Alfa Romeo 159 Sportwagon 2.4 JTDM specifications;Automobile-Catalog Alfa Romeo 159 Sportwagon 2.4 JTDM specifications	https://www.auto-data.net/en/alfa-romeo-159-sportwagon-2.4-jtdm-20v-210hp-41980;https://www.automobile-catalog.com/car/2007/222770/alfa_romeo_159_sportwagon_2_4_jdtm_20v_dpf_distinctive.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1501-1600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf "https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_August_2007.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1501-1600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1501-1600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1538 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（774 行）
