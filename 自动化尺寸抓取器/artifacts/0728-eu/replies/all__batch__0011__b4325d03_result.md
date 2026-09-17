# 任务：all 第 1001-1100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0011__b4325d03


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1001-1100 行

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
all 第 1001-1100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Rekord c	1.5	Stufenheck	Heckantrieb	Benzin	43	58	Aug 1966	Dec 1971	2024-03-01	1030
Ford	Transit	2.5 D	Bus	Heckantrieb	Diesel	50	68	Dec 1985	Jan 1989	2024-03-01	1031
Ford	Transit	2.5 D	Bus	Heckantrieb	Diesel	52	71	Sep 1988	Sep 1992	2024-03-01	1032
Opel	Rekord c	1.5	Stufenheck	Heckantrieb	Benzin	44	60	Feb 1968	Dec 1971	2024-03-01	1033
Opel	Rekord c	1.7	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1966	Dec 1971	2024-03-01	1034
Ford	Transit	2.5 D	Kasten	Heckantrieb	Diesel	52	71	Oct 1988	Sep 1991	2024-03-01	1035
Opel	Rekord c	1.7	Stufenheck	Heckantrieb	Benzin	49	66	Feb 1968	Dec 1971	2024-03-01	1036
Opel	Rekord c	1.7 S	Stufenheck	Heckantrieb	Benzin	55	75	Aug 1966	Dec 1971	2024-03-01	1037
Opel	Rekord c	1.7 S	Coupe	Heckantrieb	Benzin	55	75	Aug 1966	Dec 1971	2024-03-01	1038
Opel	Rekord c	1.9	Stufenheck	Heckantrieb	Benzin	66	90	Aug 1966	Dec 1971	2024-03-01	1039
Audi	50	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Aug 1974	Jul 1978	2024-03-01	1040
Ford	Fiesta ii	1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1983	Feb 1989	2024-03-01	1041
Ford	Fiesta ii	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Sep 1983	Feb 1989	2024-03-01	1042
Audi	50	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1974	Jul 1977	2024-03-01	1043
Ford	Fiesta ii	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Sep 1983	Jan 1987	2024-03-01	1044
Audi	50	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1977	Jul 1978	2024-03-01	1045
Fiat	Doblo cargo	1.6 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	77	105	Feb 2010	-	2024-03-01	1046
Audi	80	1.3	Stufenheck	Frontantrieb	Benzin	40	55	May 1972	Jul 1978	2024-03-01	1047
Audi	80	1.5	Stufenheck	Frontantrieb	Benzin	55	75	May 1972	Aug 1975	2024-03-01	1048
Audi	80	1.5	Stufenheck	Frontantrieb	Benzin	63	85	May 1972	Jul 1976	2024-03-01	1049
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1975	Jul 1978	2024-03-01	1050
Fiat	Doblo kombi	1.6 D Multijet	Bus	Frontantrieb	Diesel	66	90	Feb 2010	Dec 2023	2025-02-03	1051
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	132	180	Aug 2008	-	2024-03-01	1052
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	140	190	Aug 2008	-	2024-03-01	1053
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	103	140	Sep 2009	-	2024-03-01	1054
Audi	80	1.3	Stufenheck	Frontantrieb	Benzin	40	55	Sep 1978	Jul 1981	2024-03-01	1055
Audi	80	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1978	Jul 1986	2024-03-01	1056
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Feb 1986	Jul 1986	2024-03-01	1057
Ford	Fiesta ii	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Oct 1986	Feb 1989	2024-03-01	1058
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1978	Mar 1987	2024-03-01	1059
Abarth	Punto	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Mar 2012	-	2024-03-01	1060
Ford	Fiesta ii	1.4	Schrägheck	Frontantrieb	Benzin	54	73	Feb 1987	Feb 1989	2024-03-01	1061
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Aug 1978	Feb 1983	2024-03-01	1062
Audi	80	1.6 GLE	Stufenheck	Frontantrieb	Benzin	81	110	Aug 1978	Jul 1982	2024-03-01	1063
Ford	Fiesta ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1985	Nov 1989	2024-03-01	1064
Audi	b2	1.8	Coupe	Frontantrieb	Benzin	55	75	Aug 1981	Jul 1983	2024-03-01	1065
Audi	80	1.8	Stufenheck	Frontantrieb	Benzin	65	88	Feb 1986	Jul 1986	2024-03-01	1066
Ford	Fiesta ii	1.6 XR2	Schrägheck	Frontantrieb	Benzin	70	95	Mar 1984	Feb 1989	2024-03-01	1067
Audi	80	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1983	Aug 1986	2024-03-01	1068
Ford	Fiesta ii	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Apr 1984	Feb 1989	2024-03-01	1070
Ford	Fiesta iii	1.1	Schrägheck	Frontantrieb	Benzin	40	55	Mar 1989	Dec 1995	2024-03-01	1071
Cadillac	Cts	3.6	Coupe	Heckantrieb	Benzin	229	311	Jan 2008	-	2024-03-01	1072
Ford	Fiesta iii	1.4	Schrägheck	Frontantrieb	Benzin	54	73	Mar 1989	Dec 1995	2024-03-01	1073
Ford	Fiesta iii	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Mar 1989	Dec 1995	2024-03-01	1074
Ford	Fiesta iii	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Mar 1989	Dec 1995	2024-03-01	1075
Cadillac	Cts	3.6 AWD	Coupe	Allrad	Benzin	229	311	Jan 2008	Dec 2012	2024-03-01	1076
Audi	80	1.8 GTE	Stufenheck	Frontantrieb	Benzin	82	112	Oct 1984	Aug 1986	2024-03-01	1077
Ford	Fiesta iii	1.3 CAT	Schrägheck	Frontantrieb	Benzin	44	60	May 1991	Jan 1997	2024-03-01	1078
Ford	Fiesta iii	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Mar 1989	Dec 1995	2024-03-01	1079
Audi	80	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Aug 1980	Aug 1986	2024-03-01	1080
Ford	Fiesta iii	1.6 Xr2i	Schrägheck	Frontantrieb	Benzin	76	103	Mar 1989	Mar 1993	2024-03-01	1081
Audi	80	1.6 TD	Stufenheck	Frontantrieb	Diesel	51	70	Aug 1981	May 1986	2024-03-01	1082
Ford	Fiesta iii	1.8 16V	Schrägheck	Frontantrieb	Benzin	77	105	Feb 1992	Dec 1995	2024-03-01	1083
Ford	Fiesta iii	1.8 Xr2i 16V	Schrägheck	Frontantrieb	Benzin	96	130	Feb 1992	Dec 1995	2024-03-01	1084
Ford	Courier	1.8 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	44	60	Sep 1991	Feb 1996	2024-03-01	1085
Ford	Courier	1.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	44	60	Sep 1991	Feb 1996	2024-03-01	1086
Ford	Escort v	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Jul 1990	Jan 1995	2024-03-01	1087
Ford	Escort v	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Jul 1990	Jan 1995	2024-03-01	1088
Ford	Escort v	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Jul 1990	Jan 1995	2024-03-01	1089
Ford	Escort v	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Jul 1990	Aug 1993	2024-03-01	1090
Ford	Escort v	1.8 16V Xr3i	Schrägheck	Frontantrieb	Benzin	77	105	Feb 1992	Jan 1995	2024-03-01	1091
Ford	Escort v	1.8 16V Xr3i	Schrägheck	Frontantrieb	Benzin	96	130	Feb 1992	Jan 1995	2024-03-01	1092
Ford	Escort v	RS 2000	Schrägheck	Frontantrieb	Benzin	110	150	May 1991	Jan 1995	2024-03-01	1093
Ford	Orion iii	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Jul 1990	Dec 1993	2024-03-01	1094
Ford	Orion iii	1.8 D	Stufenheck	Frontantrieb	Diesel	44	60	Nov 1990	Dec 1993	2024-03-01	1095
Ford	Orion iii	1.8 TD	Stufenheck	Frontantrieb	Diesel	66	90	Mar 1992	Dec 1993	2024-03-01	1096
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	180	245	Apr 2010	Jul 2013	2024-03-01	1097
BMW	X5	Xdrive 40 D	SUV	Allrad	Diesel	225	306	Sep 2010	Jun 2013	2024-03-01	1098
Ford	Orion iii	1.4	Stufenheck	Frontantrieb	Benzin	52	71	Jul 1990	Dec 1993	2024-03-01	1099
Ford	Orion iii	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	66	90	Jul 1992	Dec 1993	2024-03-01	1100
Ford	Orion iii	1.6 I	Stufenheck	Frontantrieb	Benzin	77	105	Jul 1990	Sep 1992	2024-03-01	1101
Ford	Orion iii	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	77	105	Feb 1992	Dec 1993	2024-03-01	1102
BMW	X5	Xdrive 35 I	SUV	Allrad	Benzin	225	306	Apr 2010	Jul 2013	2024-03-01	1103
Cadillac	Cts	3	Stufenheck	Heckantrieb	Benzin	203	276	Jan 2008	Dec 2011	2026-03-01	1104
Cadillac	Cts	3.0 AWD	Stufenheck	Allrad	Benzin	203	276	Jan 2008	Dec 2010	2024-03-01	1105
Ford	Transit	2.0 I	Bus	Heckantrieb	Benzin	72	98	Sep 1991	Jul 1994	2024-03-01	1106
Audi	80	1.8 CC Quattro	Stufenheck	Allrad	Benzin	66	90	Aug 1984	Aug 1986	2024-03-01	1107
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	180	245	Apr 2010	Jul 2014	2024-03-01	1108
Audi	80	1.8 GTE Quattro	Stufenheck	Allrad	Benzin	82	112	Aug 1984	Aug 1986	2024-03-01	1109
Opel	Rekord c	1.9	Coupe	Heckantrieb	Benzin	66	90	Aug 1966	Dec 1971	2024-03-01	1110
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	1111
Audi	80	1.8	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1986	Jan 1990	2024-03-01	1112
Audi	80	1.8 S	Stufenheck	Frontantrieb	Benzin	65	88	Aug 1986	Jan 1990	2024-03-01	1113
Opel	Rekord c	1.9 Sprint	Coupe	Heckantrieb	Benzin	78	106	Aug 1967	Dec 1971	2024-03-01	1114
Audi	80	1.8 S	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1986	Oct 1991	2024-03-01	1115
Audi	80	1.8 E	Stufenheck	Frontantrieb	Benzin	82	112	Jun 1986	Aug 1991	2024-03-01	1116
Audi	80	1.8	Stufenheck	Frontantrieb	Benzin	83	113	Sep 1986	Jul 1988	2024-03-01	1117
Opel	Rekord c	1.9 Sprint	Stufenheck	Heckantrieb	Benzin	78	106	Aug 1967	Dec 1971	2024-03-01	1118
Audi	80	2.0 E	Stufenheck	Frontantrieb	Benzin	83	113	Aug 1988	Oct 1990	2024-03-01	1119
Opel	Rekord c caravan	1.5	Kombi	Heckantrieb	Benzin	43	58	Aug 1966	Dec 1971	2024-03-01	1120
Audi	80	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Feb 1987	Jul 1989	2024-03-01	1121
Ford	Transit	2.5 DI	Bus	Heckantrieb	Diesel	51	70	Aug 1991	Jul 1994	2024-03-01	1122
Audi	80	1.6 TD	Stufenheck	Frontantrieb	Diesel	59	80	Sep 1986	Aug 1991	2024-03-01	1123
Audi	80	1.9 D	Stufenheck	Frontantrieb	Diesel	50	68	Aug 1989	Aug 1991	2024-03-01	1124
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	51	70	Aug 1987	Sep 1991	2024-03-01	1125
Opel	Rekord c caravan	1.5	Kombi	Heckantrieb	Benzin	44	60	Feb 1968	Dec 1971	2024-03-01	1126
Opel	Rekord c caravan	1.7	Kombi	Heckantrieb	Benzin	44	60	Aug 1966	Dec 1971	2024-03-01	1127
Opel	Rekord c caravan	1.7	Kombi	Heckantrieb	Benzin	49	66	Feb 1968	Dec 1971	2024-03-01	1128
Opel	Rekord c caravan	1.7 S	Kombi	Heckantrieb	Benzin	55	75	Aug 1966	Dec 1971	2024-03-01	1129
Opel	Rekord c caravan	1.9	Kombi	Heckantrieb	Benzin	66	90	Aug 1966	Dec 1971	2024-03-01	1130


--- Round 1 / 首次发送 ---
更新点

* 本轮闭合 6 个尺寸组，完成 19 个 Ktype 映射：Abarth 595/595C、Cadillac CTS II Coupe、BMW X5 E70 LCI、BMW X6 E71、Audi 80 B3。
* Abarth 官方技术数据表分别确认了 180 hp 三门 Hatchback 与 140 hp 595C 的完整外廓；两者高度不同，因此独立建组。
* Cadillac CTS Coupe 的规格明确区分“不含后视镜宽度”，后驱与四驱版本复用同一 Coupe 外廓。([Car and Driver][1])
* BMW 官方技术规格附件闭合了 X5 E70 LCI 与 X6 E71 两组；发动机版本不触发重复建组。([BMW Group PressClub][2])
* Audi 80 B3 本轮输入均为前驱四门 Sedan，统一关联 B3 Typ 89 尺寸组。([汽车数据网][3])

当前批次进度

* 输入 Ktype：100
* READY 映射：19
* PENDING 映射：81
* 本轮首次闭合尺寸组：6
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1052	1052	Hatchback	Abarth 500/595 (312)	312	3	EU-ABARTH-595-312-HATCHBACK-COMPETIZIONE-01	HIGH	132 kW/180 hp对应595 Competizione三门车身。	READY
1054	1054	Convertible	Abarth 500C/595C (312)	312	3	EU-ABARTH-595C-312-CONVERTIBLE-01	HIGH	103 kW/140 hp对应595C三门敞篷车身。	READY
1072	1072	Coupe	Cadillac CTS II		2	EU-CADILLAC-CTS-II-COUPE-01	HIGH	CTS II双门Coupe后驱车身。	READY
1076	1076	Coupe	Cadillac CTS II		2	EU-CADILLAC-CTS-II-COUPE-01	HIGH	CTS II双门Coupe；四驱不改变外廓。	READY
1097	1097	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；发动机版本共用外廓。	READY
1098	1098	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；发动机版本共用外廓。	READY
1103	1103	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；燃料和发动机版本不改变外廓。	READY
1108	1108	SUV	BMW X6 E71	E71	5	EU-BMW-X6-E71-SUV-01	HIGH	E71五门SUV车身。	READY
1111	1111	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1112	1112	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1113	1113	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1115	1115	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1116	1116	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1117	1117	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1119	1119	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1121	1121	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1123	1123	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1124	1124	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1125	1125	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ABARTH-595-312-HATCHBACK-COMPETIZIONE-01	3657	1627	1488	FCA Germany Abarth 595 und 595C technical data sheet	https://www.media.stellantis.com/uploads/de/DE/2015/ABARTH/Technische_Daten/150723_AB_595_595C_TD.pdf
EU-ABARTH-595C-312-CONVERTIBLE-01	3657	1627	1485	FCA Germany Abarth 595 und 595C technical data sheet	https://www.media.stellantis.com/uploads/de/DE/2015/ABARTH/Technische_Daten/150723_AB_595_595C_TD.pdf
EU-CADILLAC-CTS-II-COUPE-01	4788	1882	1422	Car and Driver 2011 Cadillac CTS Coupe specifications;J.D. Power 2011 Cadillac CTS Coupe specifications	https://www.caranddriver.com/cadillac/cts/specs/2011/cadillac_cts_cadillac-cts-coupe_2011;https://www.jdpower.com/cars/2011/cadillac/cts-v6/coupe-2d-performance-awd/specs
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776	BMW Group PressClub X5 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0078199EN/116809
EU-BMW-X6-E71-SUV-01	4877	1983	1690	BMW Group PressClub X6 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0082920EN/145153
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397	Auto-Data Audi 80 B3 model specifications	https://www.auto-data.net/en/audi-80-model-510
```

下一步优先处理

1. 优先拆解 Ford Transit Bus/Van 的轴距、车顶高度及改款边界，避免把多个物理货厢外廓错误合并。
2. 批量闭合 Opel Rekord C Sedan、Coupe、Caravan 的门数和车身分支。
3. 处理 Audi 80 B1/B2 的二门、四门及 facelift 前后尺寸边界，并单独核对 Audi B2 Coupe。
4. 随后处理 Fiesta II/III、Escort V、Courier、Orion III，以及 Fiat Doblo Cargo/Kombi 的不同车身长度分支。

推进信号：CONTINUE

[1]: https://www.caranddriver.com/cadillac/cts/specs/2011/cadillac_cts_cadillac-cts-coupe_2011?utm_source=chatgpt.com "2019 Cadillac CTS Review, Pricing, and Specs"
[2]: https://www.press.bmwgroup.com/global/article/detail/T0078199EN/specifications-of-the-new-bmw-x5-04/2010?forceSitePreference=MOBILE "Specifications of the new BMW X5, 04/2010"
[3]: https://www.auto-data.net/en/audi-80-model-510?utm_source=chatgpt.com "Audi 80 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Opel Rekord C 的 Sedan、Coupe、Caravan 三类外廓；Sedan 拆分 2/4 门，Caravan 拆分 3/5 门，但相同三维复用同一尺寸组。([汽车目录][1])
* 完成 Ford Fiesta II 普通 Hatchback 与 XR2 的 1986 年中期前后外廓拆分；XR2 因外部套件造成长度和宽度变化，使用独立尺寸组。([汽车目录][2])
* 完成 Abarth 695 Biposto、Abarth Punto Evo、Audi Coupe B2 前期和 Cadillac CTS II Sedan 映射及尺寸组。([汽车数据网][3])

## 当前批次进度

* 已处理输入 Ktype：48/100
* PENDING 输入 Ktype：52/100
* READY 映射行：67
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1030_2dr	1030	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1030_4dr	1030	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1033_2dr	1033	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1033_4dr	1033	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1034_2dr	1034	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1034_4dr	1034	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1036_2dr	1036	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1036_4dr	1036	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1037_2dr	1037	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1037_4dr	1037	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1038	1038	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1039_2dr	1039	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1039_4dr	1039	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1041_prefl	1041	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1041_facelift	1041	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1042_prefl	1042	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1042_facelift	1042	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1044_prefl	1044	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1044_facelift	1044	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1053	1053	Hatchback	Abarth 695 Biposto (312)	312	3	EU-ABARTH-695-BIPOSTO-312-HATCHBACK-01	HIGH	140 kW/190 hp对应695 Biposto宽体三门车身。	READY
1058	1058	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	1986年中期更新后三门Hatchback。	READY
1060	1060	Hatchback	Abarth Punto Evo (199)	199	3	EU-ABARTH-PUNTO-EVO-199-HATCHBACK-01	HIGH	120 kW/163 hp对应Punto Evo三门车身。	READY
1061	1061	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	1986年中期更新后三门Hatchback。	READY
1064_prefl	1064	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1064_facelift	1064	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1065	1065	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-PHASE-I-01	HIGH	B2前期三门Coupe车身。	READY
1067_prefl	1067	Hatchback	Fiesta II XR2		3	EU-FORD-FIESTA-II-XR2-PREFL-01	HIGH	XR2跨越1986年中期更新，保留更新前外部套件分支。	READY
1067_facelift	1067	Hatchback	Fiesta II XR2		3	EU-FORD-FIESTA-II-XR2-FACELIFT-01	HIGH	XR2跨越1986年中期更新，保留更新后外部套件分支。	READY
1070_prefl	1070	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1070_facelift	1070	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1104	1104	Sedan	Cadillac CTS II		4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH	CTS II四门Sedan；驱动形式不改变外廓。	READY
1105	1105	Sedan	Cadillac CTS II		4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH	CTS II四门Sedan；驱动形式不改变外廓。	READY
1110	1110	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1114	1114	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1118_2dr	1118	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1118_4dr	1118	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1120_3dr	1120	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1120_5dr	1120	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1126_3dr	1126	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1126_5dr	1126	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1127_3dr	1127	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1127_5dr	1127	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1128_3dr	1128	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1128_5dr	1128	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1129_3dr	1129	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1129_5dr	1129	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1130_3dr	1130	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1130_5dr	1130	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-REKORD-C-SEDAN-01	4550	1754	1456	Automobile-Catalog Opel Rekord C Sedan specifications	https://www.automobile-catalog.com/car/1969/2412260/opel_rekord_1500_3gang.html
EU-OPEL-REKORD-C-COUPE-01	4574	1754	1435	Automobile-Catalog Opel Rekord C Coupe specifications	https://www.automobile-catalog.com/car/1969/2413085/opel_rekord_coupe_1700_s.html
EU-OPEL-REKORD-C-CARAVAN-01	4550	1758	1456	Automobile-Catalog Opel Rekord C Caravan specifications	https://www.automobile-catalog.com/car/1969/2412710/opel_rekord_caravan_1700_s_3gang.html
EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	3648	1585	1334	Automobile-Catalog 1986 Ford Fiesta 1.1 Ghia specifications	https://www.automobile-catalog.com/car/1986/940700/ford_fiesta_1_1_ghia.html
EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	3648	1585	1376	Automobile-Catalog 1986 Ford Fiesta 1.1 L specifications	https://www.automobile-catalog.com/car/1986/941150/ford_fiesta_1_1_l.html
EU-ABARTH-695-BIPOSTO-312-HATCHBACK-01	3657	1647	1485	Auto-Data Abarth 695 Biposto specifications	https://www.auto-data.net/en/abarth-695-biposto-1.4-t-jet-190hp-24925
EU-ABARTH-PUNTO-EVO-199-HATCHBACK-01	4065	1721	1490	Auto-Data Abarth Punto Evo 163 Hp specifications	https://www.auto-data.net/en/abarth-punto-evo-199-1.4-turbo-multiair-163hp-46798
EU-AUDI-COUPE-B2-PHASE-I-01	4349	1682	1350	Automobile-Catalog Audi Coupe GL 1.8 specifications	https://www.automobile-catalog.com/car/1982/230420/audi_coupe_gl_1_8.html
EU-FORD-FIESTA-II-XR2-PREFL-01	3711	1620	1334	Automobile-Catalog 1986 Ford Fiesta XR-2 pre-update specifications	https://www.automobile-catalog.com/car/1986/62570/ford_fiesta_xr-2.html
EU-FORD-FIESTA-II-XR2-FACELIFT-01	3711	1620	1362	Automobile-Catalog 1986 Ford Fiesta XR-2 post-update specifications	https://www.automobile-catalog.com/car/1986/941495/ford_fiesta_xr-2.html
EU-CADILLAC-CTS-II-SEDAN-01	4867	1842	1473	Edmunds 2010 Cadillac CTS Sedan specifications	https://www.edmunds.com/cadillac/cts/2010/sedan/st-101196229/features-specs/
```

## 下一步优先处理

1. 优先闭合 Audi 80 B1、B2 的前期、中期、1984 facelift 和 Quattro 高度分支。
2. 批量处理 Ford Fiesta III、Escort V、Orion III 与 Courier，共用底盘但按 Hatchback、Sedan、Van 分组。
3. 随后处理 Ford Transit Bus/Van 的轴距与车顶分支，以及 Fiat Doblo Cargo/Kombi 的 SWB/LWB 和车顶边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1969/2412260/opel_rekord_1500_3gang.html?utm_source=chatgpt.com "1969 Opel Rekord 1500 3Gang Specs Review (44 kW / 60 PS / 59 hp) (up to August 1969 for Europe )"
[2]: https://www.automobile-catalog.com/car/1986/940700/ford_fiesta_1_1_ghia.html?utm_source=chatgpt.com "1986 Ford Fiesta 1.1 Ghia Specs Review (37 kW / 50 PS / 50 hp) (up to mid-year 1986 for Europe )"
[3]: https://www.auto-data.net/en/abarth-695-biposto-1.4-t-jet-190hp-24925 "Abarth 695 Biposto 1.4 T-Jet (190 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1) 更新点

* 闭合 Audi 80 B1 的改款前 `Typ 80` 与改款后 `Typ 82`，按二门、四门派生映射；改款后车身长度、高度发生变化，因此独立建组。([汽车目录][1])
* 闭合 Audi 80 B2 的改款前、1984 facelift 前驱及 facelift quattro 三类外廓。B2 普通前驱 facelift 长度增加至 4406 mm；quattro 高度为 1350 mm，单独建组。([汽车数据网][2])
* Ktype `1059` 跨越 B2 改款及 B3 换代，新增 B2 改款前、B2 改款后及 B3 三类物理分支；B3 直接复用已确认尺寸组，不重复输出尺寸事实。

## 2) 当前批次进度

* READY 输入 Ktype：65/100
* PENDING 输入 Ktype：35/100
* READY 映射行：114
* 已确认尺寸组：22
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1047_2dr_prefl	1047	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	跨B1改款，改款前2门分支。	READY
1047_4dr_prefl	1047	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	跨B1改款，改款前4门分支。	READY
1047_2dr_facelift	1047	Sedan	Audi 80 B1	82	2	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	跨B1改款，改款后2门分支。	READY
1047_4dr_facelift	1047	Sedan	Audi 80 B1	82	4	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	跨B1改款，改款后4门分支。	READY
1048_2dr	1048	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前2门分支。	READY
1048_4dr	1048	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前4门分支。	READY
1049_2dr	1049	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前2门分支。	READY
1049_4dr	1049	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前4门分支。	READY
1050_2dr_prefl	1050	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	MEDIUM	生产期跨B1改款，改款前2门分支。	READY
1050_4dr_prefl	1050	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	MEDIUM	生产期跨B1改款，改款前4门分支。	READY
1050_2dr_facelift	1050	Sedan	Audi 80 B1	82	2	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	生产期跨B1改款，改款后2门分支。	READY
1050_4dr_facelift	1050	Sedan	Audi 80 B1	82	4	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	生产期跨B1改款，改款后4门分支。	READY
1055_2dr	1055	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1055_4dr	1055	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1056_2dr_prefl	1056	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1056_4dr_prefl	1056	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1056_2dr_facelift	1056	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1056_4dr_facelift	1056	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1057_2dr	1057	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	B2改款后2门分支。	READY
1057_4dr	1057	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后4门分支。	READY
1059_2dr_prefl	1059	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	Ktype跨B2改款及B3换代，B2改款前2门分支。	READY
1059_4dr_prefl	1059	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	Ktype跨B2改款及B3换代，B2改款前4门分支。	READY
1059_2dr_facelift	1059	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	Ktype跨B2改款及B3换代，B2改款后2门分支。	READY
1059_4dr_facelift	1059	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	Ktype跨B2改款及B3换代，B2改款后4门分支。	READY
1059_b3	1059	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	Ktype跨B2/B3换代，B3四门分支。	READY
1062_2dr	1062	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1062_4dr	1062	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1063_2dr	1063	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1063_4dr	1063	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1066_2dr	1066	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	B2改款后2门分支。	READY
1066_4dr	1066	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后4门分支。	READY
1068_2dr_prefl	1068	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1068_4dr_prefl	1068	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1068_2dr_facelift	1068	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1068_4dr_facelift	1068	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1077_2dr	1077	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后GTE 2门分支。	READY
1077_4dr	1077	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后GTE 4门分支。	READY
1080_2dr_prefl	1080	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1080_4dr_prefl	1080	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1080_2dr_facelift	1080	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1080_4dr_facelift	1080	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1082_2dr_prefl	1082	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1082_4dr_prefl	1082	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1082_2dr_facelift	1082	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1082_4dr_facelift	1082	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1107	1107	Sedan	Audi 80 B2	85	4	EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	HIGH	B2改款后quattro四门车身。	READY
1109	1109	Sedan	Audi 80 B2	85	2	EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	HIGH	B2改款后GTE quattro二门车身。	READY
```

## 4) 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362	Automobile-Catalog 1975 Audi 80 LS specifications	https://www.automobile-catalog.com/car/1975/165320/audi_80_ls.html
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360	Auto-Data Audi 80 B1 Typ 82 1.6 GLS specifications	https://www.auto-data.net/en/audi-80-b1-typ-82-1.6-gls-75hp-4629
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365	Auto-Data Audi 80 B2 Typ 81/85 specifications	https://www.auto-data.net/en/audi-80-b2-typ-81-85-1.6-85hp-4602
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365	Automobile-Catalog 1985 Audi 80 1.6 CC specifications	https://www.automobile-catalog.com/car/1985/230975/audi_80_1_6_cc.html
EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	4406	1682	1350	Automobile-Catalog 1985 Audi 80 GTE Quattro specifications	https://www.automobile-catalog.com/car/1985/230810/audi_80_gte_quattro.html
```

## 5) 下一步优先处理

1. 闭合 Ford Fiesta III 的普通三门、五门、1994 facelift 与 XR2i 外部套件分支。
2. 批量处理 Escort V Hatchback、Orion III Sedan 和 Courier Van 的改款前后外廓。
3. 随后处理 Audi 50 的不同保险杠长度，以及 Transit Bus/Van 和 Doblo Cargo/Kombi 的轴距、车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1975/165320/audi_80_ls.html?utm_source=chatgpt.com "1975 Audi 80 LS Specs Review (55 kW / 75 PS / 74 hp) ..."
[2]: https://www.auto-data.net/en/audi-80-b2-typ-81-85-1.6-85hp-4602 "Audi 80 (B2, Typ 81,85) 1.6 (85 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* Audi 50 按具体动力对应的外廓差异闭合为三组：1.1 37 kW、1.1 44 kW、1.3 44 kW 的宽度和高度相同，但长度分别为 3500、3525、3538 mm。([汽车目录][1])
* Ford Fiesta III `GFJ` 普通三门/五门车型共用标准尺寸组；XR2i 的保险杠及外部套件改变长宽高，因此独立建组。
* Ford Orion III `GAL` 本批车型均为四门 Sedan，发动机和功率差异不改变外廓，统一关联同一尺寸组。([AIC 德国汽车部件][2])

## 2) 当前批次进度

* READY 输入 Ktype：84/100
* PENDING 输入 Ktype：16/100
* READY 映射行：140
* 已确认尺寸组：28
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1040	1040	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-LS-01	HIGH	1.1 37 kW三门车身。	READY
1043	1043	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-GL-01	HIGH	1.1 44 kW三门车身。	READY
1045	1045	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-13-01	HIGH	1.3 44 kW三门车身。	READY
1071_3dr	1071	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1071_5dr	1071	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1073_3dr	1073	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1073_5dr	1073	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1074_3dr	1074	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1074_5dr	1074	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1075_3dr	1075	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1075_5dr	1075	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1078_3dr	1078	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1078_5dr	1078	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1079_3dr	1079	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1079_5dr	1079	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1081	1081	Hatchback	Fiesta III XR2i	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	XR2i三门外部套件车身。	READY
1083_3dr	1083	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1083_5dr	1083	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1084	1084	Hatchback	Fiesta III XR2i	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	XR2i 16V三门外部套件车身。	READY
1094	1094	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1095	1095	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1096	1096	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1099	1099	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1100	1100	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1101	1101	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1102	1102	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-50-TYP86-HATCHBACK-LS-01	3500	1560	1344	Automobile-Catalog 1975 Audi 50 1.1 LS specifications	https://www.automobile-catalog.com/car/1975/38195/audi_50_1_1_ls.html
EU-AUDI-50-TYP86-HATCHBACK-GL-01	3525	1560	1344	Automobile-Catalog 1976 Audi 50 1.1 GL specifications	https://www.automobile-catalog.com/car/1976/164960/audi_50_1_1_gl.html
EU-AUDI-50-TYP86-HATCHBACK-13-01	3538	1560	1344	Automobile-Catalog 1977 Audi 50 1.3 LS specifications	https://www.automobile-catalog.com/car/1977/164990/audi_50_1_3_ls.html
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389	Automobile-Catalog 1990 Ford Fiesta 1.1 LX specifications	https://www.automobile-catalog.com/car/1990/943460/ford_fiesta_1_1_lx.html
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365	Automobile-Catalog 1991 Ford Fiesta XR2i specifications	https://www.automobile-catalog.com/car/1991/943715/ford_fiesta_xr2i.html
EU-FORD-ORION-III-GAL-SEDAN-01	4229	1690	1395	Automobile-Catalog 1991 Ford Orion 1.3i CL specifications	https://www.automobile-catalog.com/car/1991/945830/ford_orion_1_3i_cl.html
```

## 5) 下一步优先处理

1. 闭合 Ford Escort V 普通 Hatchback、1992 改款后车身及 XR3i/RS2000 外部套件分支。
2. 闭合 Ford Courier `F3L/F5L` Van 尺寸组。
3. 最后处理 Ford Transit Bus/Van 的轴距、车顶高度分支，以及 Fiat Doblo Cargo/Kombi 的短轴、长轴和车顶边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1975/38195/audi_50_1_1_ls.html?utm_source=chatgpt.com "1975 Audi 50 1.1 LS (man. 4) (model for Europe ) car ..."
[2]: https://www.aic-germany.de/en/product-catalogue/4592?utm_source=chatgpt.com "Product catalogue from AIC Germany"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1001-1100_ktype_dimension_mapping_final.tsv
- all_1001-1100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 16 个输入 Ktype：Ford Transit、Fiat Doblò、Ford Courier 与 Ford Escort V。
* Transit 按 Mk3/Mk4 的轴距和车顶外廓拆分；车宽使用 Ford 1991 官方资料中的 1974 mm 无后视镜口径。([Transit Center Ford Transit Spare Parts][1])
* Doblò 根据 Fiat Professional 2010 与 2015 官方资料拆分短轴、长轴、低顶、高顶及 XL；未创建官方资料未支持的改款前长轴高顶组。([Stellantis Media][2])
* Escort V 已区分改款前后以及 XR3i、RS2000 外部套件；Courier 区分 Van 与 Kombi 高度。([汽车目录][3])
* 已完成固定表头、唯一主键、外键闭合、尺寸及来源非空检查。

## 当前批次进度

* 输入 Ktype：100/100
* READY 映射：199
* PENDING 映射：0
* DIMENSION_GROUP：50
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 缺失或孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1030_2dr	1030	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1030_4dr	1030	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1031_swb_lowroof	1031	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	SWB低顶分支。	READY
1031_lwb_midroof	1031	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	LWB中顶分支。	READY
1031_xlwb_highroof	1031	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长高顶分支。	READY
1032_swb_lowroof	1032	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	SWB低顶分支。	READY
1032_lwb_midroof	1032	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	LWB中顶分支。	READY
1032_xlwb_highroof	1032	MPV	Transit VE6			EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长高顶分支。	READY
1032_swb_lowroof_facelift	1032	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	1991改款SWB低顶分支。	READY
1032_swb_midroof_facelift	1032	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	1991改款SWB中顶分支。	READY
1032_lwb_midroof_facelift	1032	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	1991改款LWB中顶分支。	READY
1032_lwb_highroof_facelift	1032	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	1991改款LWB高顶分支。	READY
1033_2dr	1033	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1033_4dr	1033	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1034_2dr	1034	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1034_4dr	1034	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1035_swb_lowroof	1035	Van	Transit VE6			EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	SWB低顶分支。	READY
1035_lwb_midroof	1035	Van	Transit VE6			EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	LWB中顶分支。	READY
1035_xlwb_highroof	1035	Van	Transit VE6			EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长高顶分支。	READY
1036_2dr	1036	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1036_4dr	1036	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1037_2dr	1037	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1037_4dr	1037	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1038	1038	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1039_2dr	1039	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1039_4dr	1039	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1040	1040	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-LS-01	HIGH	1.1 37 kW三门车身。	READY
1041_prefl	1041	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1041_facelift	1041	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1042_prefl	1042	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1042_facelift	1042	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1043	1043	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-GL-01	HIGH	1.1 44 kW三门车身。	READY
1044_prefl	1044	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1044_facelift	1044	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1045	1045	Hatchback	Audi 50	86	3	EU-AUDI-50-TYP86-HATCHBACK-13-01	HIGH	1.3 44 kW三门车身。	READY
1046_prefl_swb_lowroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	MEDIUM	改款前短轴低顶分支。	READY
1046_prefl_swb_highroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	MEDIUM	改款前短轴高顶分支。	READY
1046_prefl_lwb_lowroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	MEDIUM	改款前长轴低顶分支。	READY
1046_facelift_swb_lowroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	MEDIUM	2015改款短轴低顶分支。	READY
1046_facelift_swb_highroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	MEDIUM	2015改款短轴高顶分支。	READY
1046_facelift_lwb_lowroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	MEDIUM	2015改款长轴低顶分支。	READY
1046_facelift_lwb_highroof	1046	Van	Doblò II (263)	263		EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	MEDIUM	2015改款长轴高顶分支。	READY
1047_2dr_prefl	1047	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	跨B1改款，改款前2门分支。	READY
1047_4dr_prefl	1047	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	跨B1改款，改款前4门分支。	READY
1047_2dr_facelift	1047	Sedan	Audi 80 B1	82	2	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	跨B1改款，改款后2门分支。	READY
1047_4dr_facelift	1047	Sedan	Audi 80 B1	82	4	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	跨B1改款，改款后4门分支。	READY
1048_2dr	1048	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前2门分支。	READY
1048_4dr	1048	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前4门分支。	READY
1049_2dr	1049	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前2门分支。	READY
1049_4dr	1049	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	HIGH	B1改款前4门分支。	READY
1050_2dr_prefl	1050	Sedan	Audi 80 B1	80	2	EU-AUDI-80-B1-SEDAN-PREFL-01	MEDIUM	生产期跨B1改款，改款前2门分支。	READY
1050_4dr_prefl	1050	Sedan	Audi 80 B1	80	4	EU-AUDI-80-B1-SEDAN-PREFL-01	MEDIUM	生产期跨B1改款，改款前4门分支。	READY
1050_2dr_facelift	1050	Sedan	Audi 80 B1	82	2	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	生产期跨B1改款，改款后2门分支。	READY
1050_4dr_facelift	1050	Sedan	Audi 80 B1	82	4	EU-AUDI-80-B1-SEDAN-FACELIFT-01	HIGH	生产期跨B1改款，改款后4门分支。	READY
1051_swb_prefl	1051	MPV	Doblò II (263)	263	5	EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	MEDIUM	改款前短轴Kombi分支。	READY
1051_lwb_prefl	1051	MPV	Doblò II (263)	263	5	EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	MEDIUM	改款前长轴Kombi分支。	READY
1051_swb_facelift	1051	MPV	Doblò II (263)	263	5	EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	MEDIUM	2015改款短轴Kombi分支。	READY
1051_lwb_facelift	1051	MPV	Doblò II (263)	263	5	EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	MEDIUM	2015改款长轴Kombi分支。	READY
1051_xl_facelift	1051	MPV	Doblò II (263)	263	5	EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	MEDIUM	2015改款长轴高顶Combi XL分支。	READY
1052	1052	Hatchback	Abarth 500/595 (312)	312	3	EU-ABARTH-595-312-HATCHBACK-COMPETIZIONE-01	HIGH	132 kW/180 hp对应595 Competizione三门车身。	READY
1053	1053	Hatchback	Abarth 695 Biposto (312)	312	3	EU-ABARTH-695-BIPOSTO-312-HATCHBACK-01	HIGH	140 kW/190 hp对应695 Biposto宽体三门车身。	READY
1054	1054	Convertible	Abarth 500C/595C (312)	312	3	EU-ABARTH-595C-312-CONVERTIBLE-01	HIGH	103 kW/140 hp对应595C三门敞篷车身。	READY
1055_2dr	1055	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1055_4dr	1055	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1056_2dr_prefl	1056	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1056_4dr_prefl	1056	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1056_2dr_facelift	1056	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1056_4dr_facelift	1056	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1057_2dr	1057	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	B2改款后2门分支。	READY
1057_4dr	1057	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后4门分支。	READY
1058	1058	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	1986年中期更新后三门Hatchback。	READY
1059_2dr_prefl	1059	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	Ktype跨B2改款及B3换代，B2改款前2门分支。	READY
1059_4dr_prefl	1059	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	Ktype跨B2改款及B3换代，B2改款前4门分支。	READY
1059_2dr_facelift	1059	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	Ktype跨B2改款及B3换代，B2改款后2门分支。	READY
1059_4dr_facelift	1059	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	Ktype跨B2改款及B3换代，B2改款后4门分支。	READY
1059_b3	1059	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	Ktype跨B2/B3换代，B3四门分支。	READY
1060	1060	Hatchback	Abarth Punto Evo (199)	199	3	EU-ABARTH-PUNTO-EVO-199-HATCHBACK-01	HIGH	120 kW/163 hp对应Punto Evo三门车身。	READY
1061	1061	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	1986年中期更新后三门Hatchback。	READY
1062_2dr	1062	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1062_4dr	1062	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1063_2dr	1063	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前2门分支。	READY
1063_4dr	1063	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	B2改款前4门分支。	READY
1064_prefl	1064	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1064_facelift	1064	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1065	1065	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-PHASE-I-01	HIGH	B2前期三门Coupe车身。	READY
1066_2dr	1066	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	B2改款后2门分支。	READY
1066_4dr	1066	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后4门分支。	READY
1067_prefl	1067	Hatchback	Fiesta II XR2		3	EU-FORD-FIESTA-II-XR2-PREFL-01	HIGH	XR2跨越1986年中期更新，保留更新前外部套件分支。	READY
1067_facelift	1067	Hatchback	Fiesta II XR2		3	EU-FORD-FIESTA-II-XR2-FACELIFT-01	HIGH	XR2跨越1986年中期更新，保留更新后外部套件分支。	READY
1068_2dr_prefl	1068	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1068_4dr_prefl	1068	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1068_2dr_facelift	1068	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1068_4dr_facelift	1068	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1070_prefl	1070	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新前分支。	READY
1070_facelift	1070	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1986年中期外廓更新，保留更新后分支。	READY
1071_3dr	1071	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1071_5dr	1071	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1072	1072	Coupe	Cadillac CTS II		2	EU-CADILLAC-CTS-II-COUPE-01	HIGH	CTS II双门Coupe后驱车身。	READY
1073_3dr	1073	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1073_5dr	1073	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1074_3dr	1074	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1074_5dr	1074	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1075_3dr	1075	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1075_5dr	1075	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1076	1076	Coupe	Cadillac CTS II		2	EU-CADILLAC-CTS-II-COUPE-01	HIGH	CTS II双门Coupe；四驱不改变外廓。	READY
1077_2dr	1077	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后GTE 2门分支。	READY
1077_4dr	1077	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	B2改款后GTE 4门分支。	READY
1078_3dr	1078	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1078_5dr	1078	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1079_3dr	1079	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1079_5dr	1079	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1080_2dr_prefl	1080	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1080_4dr_prefl	1080	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1080_2dr_facelift	1080	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1080_4dr_facelift	1080	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1081	1081	Hatchback	Fiesta III XR2i	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	XR2i三门外部套件车身。	READY
1082_2dr_prefl	1082	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前2门分支。	READY
1082_4dr_prefl	1082	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-PREFL-01	HIGH	跨B2改款，改款前4门分支。	READY
1082_2dr_facelift	1082	Sedan	Audi 80 B2	81	2	EU-AUDI-80-B2-SEDAN-FACELIFT-01	MEDIUM	跨B2改款，改款后2门分支。	READY
1082_4dr_facelift	1082	Sedan	Audi 80 B2	81	4	EU-AUDI-80-B2-SEDAN-FACELIFT-01	HIGH	跨B2改款，改款后4门分支。	READY
1083_3dr	1083	Hatchback	Fiesta III	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
1083_5dr	1083	Hatchback	Fiesta III	GFJ	5	EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
1084	1084	Hatchback	Fiesta III XR2i	GFJ	3	EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	HIGH	XR2i 16V三门外部套件车身。	READY
1085_van	1085	Van	Courier I (Fiesta-based)		3	EU-FORD-COURIER-I-VAN-01	MEDIUM	厢式货车外廓分支。	READY
1085_kombi	1085	MPV	Courier I (Fiesta-based)		5	EU-FORD-COURIER-I-KOMBI-01	MEDIUM	带后排座椅Kombi外廓分支。	READY
1086_van	1086	Van	Courier I (Fiesta-based)		3	EU-FORD-COURIER-I-VAN-01	MEDIUM	厢式货车外廓分支。	READY
1086_kombi	1086	MPV	Courier I (Fiesta-based)		5	EU-FORD-COURIER-I-KOMBI-01	MEDIUM	带后排座椅Kombi外廓分支。	READY
1087_3dr_prefl	1087	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	3门改款前物理分支。	READY
1087_5dr_prefl	1087	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	5门改款前物理分支。	READY
1087_3dr_facelift	1087	Hatchback	Escort V facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	3门改款后物理分支。	READY
1087_5dr_facelift	1087	Hatchback	Escort V facelift	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	5门改款后物理分支。	READY
1088_3dr_prefl	1088	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	3门改款前物理分支。	READY
1088_5dr_prefl	1088	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	5门改款前物理分支。	READY
1088_3dr_facelift	1088	Hatchback	Escort V facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	3门改款后物理分支。	READY
1088_5dr_facelift	1088	Hatchback	Escort V facelift	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	5门改款后物理分支。	READY
1089_3dr_prefl	1089	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	3门改款前物理分支。	READY
1089_5dr_prefl	1089	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	5门改款前物理分支。	READY
1089_3dr_facelift	1089	Hatchback	Escort V facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	3门改款后物理分支。	READY
1089_5dr_facelift	1089	Hatchback	Escort V facelift	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	5门改款后物理分支。	READY
1090_3dr_prefl	1090	Hatchback	Escort V	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	3门改款前物理分支。	READY
1090_5dr_prefl	1090	Hatchback	Escort V	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	HIGH	5门改款前物理分支。	READY
1090_3dr_facelift	1090	Hatchback	Escort V facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	3门改款后物理分支。	READY
1090_5dr_facelift	1090	Hatchback	Escort V facelift	GAL	5	EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	HIGH	5门改款后物理分支。	READY
1091_prefl	1091	Hatchback	Escort V XR3i	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-PREFL-01	HIGH	XR3i改款前三门外部套件分支。	READY
1091_facelift	1091	Hatchback	Escort V XR3i facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH	XR3i改款后三门外部套件分支。	READY
1092_prefl	1092	Hatchback	Escort V XR3i	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-PREFL-01	HIGH	XR3i改款前三门外部套件分支。	READY
1092_facelift	1092	Hatchback	Escort V XR3i facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	HIGH	XR3i改款后三门外部套件分支。	READY
1093_prefl	1093	Hatchback	Escort V RS2000	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	HIGH	RS2000改款前三门外部套件分支。	READY
1093_facelift	1093	Hatchback	Escort V RS2000 facelift	GAL	3	EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	HIGH	RS2000改款后三门外部套件分支。	READY
1094	1094	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1095	1095	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1096	1096	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1097	1097	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；发动机版本共用外廓。	READY
1098	1098	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；发动机版本共用外廓。	READY
1099	1099	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1100	1100	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1101	1101	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1102	1102	Sedan	Orion III	GAL	4	EU-FORD-ORION-III-GAL-SEDAN-01	HIGH	四门Sedan车身。	READY
1103	1103	SUV	BMW X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH	E70 LCI五门SUV；燃料和发动机版本不改变外廓。	READY
1104	1104	Sedan	Cadillac CTS II		4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH	CTS II四门Sedan；驱动形式不改变外廓。	READY
1105	1105	Sedan	Cadillac CTS II		4	EU-CADILLAC-CTS-II-SEDAN-01	HIGH	CTS II四门Sedan；驱动形式不改变外廓。	READY
1106_swb_lowroof_facelift	1106	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	1991改款SWB低顶分支。	READY
1106_swb_midroof_facelift	1106	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	1991改款SWB中顶分支。	READY
1106_lwb_midroof_facelift	1106	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	1991改款LWB中顶分支。	READY
1106_lwb_highroof_facelift	1106	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	1991改款LWB高顶分支。	READY
1107	1107	Sedan	Audi 80 B2	85	4	EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	HIGH	B2改款后quattro四门车身。	READY
1108	1108	SUV	BMW X6 E71	E71	5	EU-BMW-X6-E71-SUV-01	HIGH	E71五门SUV车身。	READY
1109	1109	Sedan	Audi 80 B2	85	2	EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	HIGH	B2改款后GTE quattro二门车身。	READY
1110	1110	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1111	1111	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1112	1112	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1113	1113	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1114	1114	Coupe	Rekord C		2	EU-OPEL-REKORD-C-COUPE-01	HIGH	Rekord C双门Coupe车身。	READY
1115	1115	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1116	1116	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1117	1117	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1118_2dr	1118	Sedan	Rekord C		2	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 2门Sedan物理分支。	READY
1118_4dr	1118	Sedan	Rekord C		4	EU-OPEL-REKORD-C-SEDAN-01	MEDIUM	Rekord C 4门Sedan物理分支。	READY
1119	1119	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1120_3dr	1120	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1120_5dr	1120	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1121	1121	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1122_swb_lowroof_facelift	1122	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	1991改款SWB低顶分支。	READY
1122_swb_midroof_facelift	1122	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	1991改款SWB中顶分支。	READY
1122_lwb_midroof_facelift	1122	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	1991改款LWB中顶分支。	READY
1122_lwb_highroof_facelift	1122	MPV	Transit VE6 facelift			EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	1991改款LWB高顶分支。	READY
1123	1123	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1124	1124	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan；柴油动力不改变外廓。	READY
1125	1125	Sedan	Audi 80 B3	89	4	EU-AUDI-80-B3-SEDAN-01	HIGH	B3 Typ 89四门Sedan。	READY
1126_3dr	1126	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1126_5dr	1126	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1127_3dr	1127	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1127_5dr	1127	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1128_3dr	1128	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1128_5dr	1128	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1129_3dr	1129	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1129_5dr	1129	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
1130_3dr	1130	Wagon	Rekord C Caravan		3	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 3门Wagon物理分支。	READY
1130_5dr	1130	Wagon	Rekord C Caravan		5	EU-OPEL-REKORD-C-CARAVAN-01	MEDIUM	Rekord C Caravan 5门Wagon物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1001-1100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-REKORD-C-SEDAN-01	4550	1754	1456	Automobile-Catalog Opel Rekord C Sedan specifications	https://www.automobile-catalog.com/car/1969/2412260/opel_rekord_1500_3gang.html
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974	Transit Center Ford Transit Mk3 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk3-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653	Transit Center Ford Transit Mk3 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk3-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653	Transit Center Ford Transit Mk3 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk3-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Transit Center Ford Transit Mk4 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk4-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Transit Center Ford Transit Mk4 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk4-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Transit Center Ford Transit Mk4 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk4-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Transit Center Ford Transit Mk4 specifications;Ford Transit 1991 official brochure	https://www.transitcenter.uk/transit-mk4-data-specification.php;https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-OPEL-REKORD-C-COUPE-01	4574	1754	1435	Automobile-Catalog Opel Rekord C Coupe specifications	https://www.automobile-catalog.com/car/1969/2413085/opel_rekord_coupe_1700_s.html
EU-AUDI-50-TYP86-HATCHBACK-LS-01	3500	1560	1344	Automobile-Catalog 1975 Audi 50 1.1 LS specifications	https://www.automobile-catalog.com/car/1975/38195/audi_50_1_1_ls.html
EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	3648	1585	1334	Automobile-Catalog 1986 Ford Fiesta 1.1 Ghia specifications	https://www.automobile-catalog.com/car/1986/940700/ford_fiesta_1_1_ghia.html
EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	3648	1585	1376	Automobile-Catalog 1986 Ford Fiesta 1.1 L specifications	https://www.automobile-catalog.com/car/1986/941150/ford_fiesta_1_1_l.html
EU-AUDI-50-TYP86-HATCHBACK-GL-01	3525	1560	1344	Automobile-Catalog 1976 Audi 50 1.1 GL specifications	https://www.automobile-catalog.com/car/1976/164960/audi_50_1_1_gl.html
EU-AUDI-50-TYP86-HATCHBACK-13-01	3538	1560	1344	Automobile-Catalog 1977 Audi 50 1.3 LS specifications	https://www.automobile-catalog.com/car/1977/164990/audi_50_1_3_ls.html
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	4390	1832	1845	Fiat Professional New Doblò Cargo press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	4390	1832	2100	Fiat Professional New Doblò Cargo press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	4740	1832	1880	Fiat Professional New Doblò Cargo press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	4406	1832	1845	Fiat Professional New Doblò Cargo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	4406	1832	2125	Fiat Professional New Doblò Cargo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	4756	1832	1880	Fiat Professional New Doblò Cargo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	4756	1832	2125	Fiat Professional New Doblò Cargo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362	Automobile-Catalog 1975 Audi 80 LS specifications	https://www.automobile-catalog.com/car/1975/165320/audi_80_ls.html
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360	Auto-Data Audi 80 B1 Typ 82 1.6 GLS specifications	https://www.auto-data.net/en/audi-80-b1-typ-82-1.6-gls-75hp-4629
EU-ABARTH-595-312-HATCHBACK-COMPETIZIONE-01	3657	1627	1488	FCA Germany Abarth 595 und 595C technical data sheet	https://www.media.stellantis.com/uploads/de/DE/2015/ABARTH/Technische_Daten/150723_AB_595_595C_TD.pdf
EU-ABARTH-695-BIPOSTO-312-HATCHBACK-01	3657	1647	1485	Auto-Data Abarth 695 Biposto specifications	https://www.auto-data.net/en/abarth-695-biposto-1.4-t-jet-190hp-24925
EU-ABARTH-595C-312-CONVERTIBLE-01	3657	1627	1485	FCA Germany Abarth 595 und 595C technical data sheet	https://www.media.stellantis.com/uploads/de/DE/2015/ABARTH/Technische_Daten/150723_AB_595_595C_TD.pdf
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365	Auto-Data Audi 80 B2 Typ 81/85 specifications	https://www.auto-data.net/en/audi-80-b2-typ-81-85-1.6-85hp-4602
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365	Automobile-Catalog 1985 Audi 80 1.6 CC specifications	https://www.automobile-catalog.com/car/1985/230975/audi_80_1_6_cc.html
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397	Auto-Data Audi 80 B3 model specifications	https://www.auto-data.net/en/audi-80-model-510
EU-ABARTH-PUNTO-EVO-199-HATCHBACK-01	4065	1721	1490	Auto-Data Abarth Punto Evo 163 Hp specifications	https://www.auto-data.net/en/abarth-punto-evo-199-1.4-turbo-multiair-163hp-46798
EU-AUDI-COUPE-B2-PHASE-I-01	4349	1682	1350	Automobile-Catalog Audi Coupe GL 1.8 specifications	https://www.automobile-catalog.com/car/1982/230420/audi_coupe_gl_1_8.html
EU-FORD-FIESTA-II-XR2-PREFL-01	3711	1620	1334	Automobile-Catalog 1986 Ford Fiesta XR-2 pre-update specifications	https://www.automobile-catalog.com/car/1986/62570/ford_fiesta_xr-2.html
EU-FORD-FIESTA-II-XR2-FACELIFT-01	3711	1620	1362	Automobile-Catalog 1986 Ford Fiesta XR-2 post-update specifications	https://www.automobile-catalog.com/car/1986/941495/ford_fiesta_xr-2.html
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389	Automobile-Catalog 1990 Ford Fiesta 1.1 LX specifications	https://www.automobile-catalog.com/car/1990/943460/ford_fiesta_1_1_lx.html
EU-CADILLAC-CTS-II-COUPE-01	4788	1882	1422	Car and Driver 2011 Cadillac CTS Coupe specifications;J.D. Power 2011 Cadillac CTS Coupe specifications	https://www.caranddriver.com/cadillac/cts/specs/2011/cadillac_cts_cadillac-cts-coupe_2011;https://www.jdpower.com/cars/2011/cadillac/cts-v6/coupe-2d-performance-awd/specs
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365	Automobile-Catalog 1991 Ford Fiesta XR2i specifications	https://www.automobile-catalog.com/car/1991/943715/ford_fiesta_xr2i.html
EU-FORD-COURIER-I-VAN-01	4115	1650	1835	IKZ Haustechnik Ford Fiesta Courier specifications	https://www.ikz.de/ikz-archiv/1999/22/9922056.php
EU-FORD-COURIER-I-KOMBI-01	4115	1650	1819	IKZ Haustechnik Ford Fiesta Courier specifications	https://www.ikz.de/ikz-archiv/1999/22/9922056.php
EU-FORD-ESCORT-V-GAL-HATCHBACK-PREFL-01	4036	1692	1395	Automobile-Catalog 1991 Ford Escort 1.3 L specifications	https://www.automobile-catalog.com/car/1991/944735/ford_escort_1_3_l.html
EU-FORD-ESCORT-V-GAL-HATCHBACK-FACELIFT-01	4104	1696	1397	Automobile-Catalog 1993 Ford Escort 1.3i CL specifications	https://www.automobile-catalog.com/car/1993/946130/ford_escort_1_3i_cl_l.html
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-PREFL-01	4036	1692	1389	Automobile-Catalog 1992 Ford Escort XR3i 105 specifications	https://www.automobile-catalog.com/car/1992/945905/ford_escort_xr3i_105.html
EU-FORD-ESCORT-V-GAL-HATCHBACK-XR3I-FACELIFT-01	4108	1696	1370	Automobile-Catalog 1993 Ford Escort XR3i specifications	https://www.automobile-catalog.com/car/1993/946430/ford_escort_xr3i.html
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-PREFL-01	4040	1692	1389	Automobile-Catalog 1991 Ford Escort RS 2000 specifications	https://www.automobile-catalog.com/car/1991/945860/ford_escort_rs_2000.html
EU-FORD-ESCORT-V-GAL-HATCHBACK-RS2000-FACELIFT-01	4108	1696	1379	Automobile-Catalog 1992 Ford Escort RS 2000 specifications	https://www.automobile-catalog.com/car/1992/946415/ford_escort_rs_2000.html
EU-FORD-ORION-III-GAL-SEDAN-01	4229	1690	1395	Automobile-Catalog 1991 Ford Orion 1.3i CL specifications	https://www.automobile-catalog.com/car/1991/945830/ford_orion_1_3i_cl.html
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776	BMW Group PressClub X5 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0078199EN/116809
EU-CADILLAC-CTS-II-SEDAN-01	4867	1842	1473	Edmunds 2010 Cadillac CTS Sedan specifications	https://www.edmunds.com/cadillac/cts/2010/sedan/st-101196229/features-specs/
EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	4406	1682	1350	Automobile-Catalog 1985 Audi 80 GTE Quattro specifications	https://www.automobile-catalog.com/car/1985/230810/audi_80_gte_quattro.html
EU-BMW-X6-E71-SUV-01	4877	1983	1690	BMW Group PressClub X6 technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0082920EN/145153
EU-OPEL-REKORD-C-CARAVAN-01	4550	1758	1456	Automobile-Catalog Opel Rekord C Caravan specifications	https://www.automobile-catalog.com/car/1969/2412710/opel_rekord_caravan_1700_s_3gang.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1001-1100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.transitcenter.uk/transit-mk3-data-specification.php "FORD TRANSIT MK3 - SPECIFICATIONS"
[2]: https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf "Doblo Press Pack for CD.indd"
[3]: https://www.automobile-catalog.com/make/ford_europe/escort_europe_6gen/escort_europe_6gen_hatchback/1992.html?utm_source=chatgpt.com "1992 Ford (Europe) Escort Mk Vb Hatchback full range specs"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1001-1100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1001-1100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1536 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（363 行）
