# 任务：all 第 1501-1600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0016__d7d7fd79


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
Ford	Sierra	2.3 D	Kombi	Heckantrieb	Diesel	49	67	Aug 1982	Dec 1986	2024-03-01	1534
Ford	Sierra	1.8	Kombi	Heckantrieb	Benzin	64	87	May 1988	Feb 1993	2024-03-01	1535
Ford	Sierra	1.8	Kombi	Heckantrieb	Benzin	59	80	Oct 1987	May 1988	2024-03-01	1536
Ford	Sierra	1.8	Kombi	Heckantrieb	Benzin	66	90	Jan 1987	May 1988	2024-03-01	1537
Ford	Sierra	2	Kombi	Heckantrieb	Benzin	77	105	Jan 1987	Feb 1993	2024-03-01	1538
Ford	Sierra	2.0 I CAT	Kombi	Heckantrieb	Benzin	74	100	Jan 1987	Feb 1993	2024-03-01	1539
Ford	Sierra	1.8 TD	Kombi	Heckantrieb	Diesel	55	75	Aug 1988	Feb 1993	2024-03-01	1540
Ford	Sierra	2.3 D	Kombi	Heckantrieb	Diesel	49	67	Jan 1987	Feb 1993	2024-03-01	1541
Ford	Sierra	1.6	Kombi	Heckantrieb	Benzin	53	72	Jan 1988	Feb 1993	2024-03-01	1543
Ford	Sierra	1.6 I	Kombi	Heckantrieb	Benzin	59	80	Oct 1989	Feb 1993	2024-03-01	1544
Ford	Sierra	2.0 I	Kombi	Heckantrieb	Benzin	85	115	Jan 1987	Feb 1993	2024-03-01	1545
Ford	Sierra	2.0 I	Kombi	Heckantrieb	Benzin	88	120	May 1989	Feb 1993	2024-03-01	1546
Ford	Sierra	2.0 4X4	Kombi	Allrad	Benzin	88	120	Feb 1990	Feb 1993	2024-03-01	1547
Ford	Sierra	1.6	Kombi	Heckantrieb	Benzin	55	75	Jan 1987	Feb 1993	2024-03-01	1548
VW	Kaefer	1.2	Stufenheck	Heckantrieb	Benzin	22	30	Jan 1954	Jul 1965	2024-03-01	1549
VW	Kaefer	1200 1.2	Stufenheck	Heckantrieb	Benzin	25	34	Jan 1960	Dec 1985	2024-03-01	1550
Ford	Granada	2	Kombi	Heckantrieb	Benzin	74	101	Aug 1979	Aug 1985	2024-03-01	1551
VW	Kaefer	1300 1.3	Stufenheck	Heckantrieb	Benzin	29	40	Aug 1965	Jul 1975	2024-03-01	1552
Fiat	Panda	1.2 4X4	Schrägheck	Allrad	Benzin	51	69	Apr 2010	Aug 2013	2024-03-01	1553
Ford	Granada	2	Kombi	Heckantrieb	Benzin	77	105	Aug 1981	Aug 1985	2024-03-01	1554
VW	Kaefer	1500 1.5	Stufenheck	Heckantrieb	Benzin	32	44	Aug 1966	Nov 1973	2024-03-01	1555
VW	Kaefer	1303 1.6	Stufenheck	Heckantrieb	Benzin	35	48	Aug 1972	Dec 1979	2024-03-01	1556
Ford	Granada	2	Kombi	Heckantrieb	Benzin	66	90	Aug 1977	Jun 1985	2024-03-01	1557
VW	Kaefer	1303 LS, S 1.6	Stufenheck	Heckantrieb	Benzin	37	50	Aug 1972	Dec 1979	2024-03-01	1558
VW	Kaefer	1302,1303 1.6	Cabriolet	Heckantrieb	Benzin	37	50	Jul 1970	Jun 1979	2024-03-01	1559
VW	Kaefer	1500 1.6	Stufenheck	Heckantrieb	Benzin	37	50	Jul 1970	Jan 1973	2024-03-01	1560
VW	Kaefer	1302 1.6	Stufenheck	Heckantrieb	Benzin	37	50	Jan 1970	Jan 1973	2024-03-01	1561
Ford	Granada	2.3	Kombi	Heckantrieb	Benzin	79	107	Aug 1977	Jun 1979	2024-03-01	1562
VW	Kaefer	1500 1.5	Cabriolet	Heckantrieb	Benzin	32	44	Jan 1966	Dec 1970	2024-03-01	1563
Ford	Granada	2.3	Kombi	Heckantrieb	Benzin	84	114	Jun 1979	Aug 1985	2024-03-01	1564
Ford	Granada	2.8	Kombi	Heckantrieb	Benzin	99	135	Aug 1977	Aug 1985	2024-03-01	1565
VW	Kaefer	1303 1.3	Stufenheck	Heckantrieb	Benzin	32	44	Aug 1972	Jul 1975	2024-03-01	1566
Ford	Granada	2.8 I	Kombi	Heckantrieb	Benzin	108	147	Aug 1977	Aug 1985	2024-03-01	1567
VW	Kaefer	1300 1.3	Stufenheck	Heckantrieb	Benzin	32	44	Jan 1970	Jan 1973	2024-03-01	1568
Ford	Granada	2.8 I	Kombi	Heckantrieb	Benzin	110	150	Oct 1982	Aug 1985	2024-03-01	1569
Ford	Granada	2.8 I	Kombi	Heckantrieb	Benzin	118	160	Aug 1977	Aug 1981	2024-03-01	1570
Ford	Granada	2.5 D	Kombi	Heckantrieb	Diesel	51	69	Aug 1982	Aug 1985	2024-03-01	1571
VW	Kaefer	1302 1.2	Stufenheck	Heckantrieb	Benzin	25	34	Aug 1969	Aug 1972	2024-03-01	1572
VW	Kaefer	1303 1.2	Stufenheck	Heckantrieb	Benzin	25	34	Jul 1972	Feb 1976	2024-03-01	1573
Ford	Scorpio i turnier	2.5 TD	Kombi	Heckantrieb	Diesel	68	92	Sep 1991	Jul 1993	2024-03-01	1574
Ford	Scorpio i turnier	2.0 I	Kombi	Heckantrieb	Benzin	85	115	Sep 1991	Sep 1994	2024-03-01	1575
Ford	Scorpio i turnier	2.0 I	Kombi	Heckantrieb	Benzin	88	120	Sep 1991	Sep 1994	2024-03-01	1576
Ford	Scorpio i turnier	2.4 I	Kombi	Heckantrieb	Benzin	92	125	Sep 1991	Sep 1994	2024-03-01	1577
Ford	Scorpio i turnier	2.9 I	Kombi	Heckantrieb	Benzin	107	145	Sep 1991	Sep 1994	2024-03-01	1578
Ford	Escort v turnier	1.3	Kombi	Frontantrieb	Benzin	44	60	Sep 1991	Jan 1995	2024-03-01	1579
Ford	Escort v turnier	1.8 D	Kombi	Frontantrieb	Diesel	44	60	Jul 1990	Jan 1995	2024-03-01	1580
Ford	Escort v turnier	1.4	Kombi	Frontantrieb	Benzin	52	71	Jul 1990	Jan 1995	2024-03-01	1581
Ford	Escort v turnier	1.6	Kombi	Frontantrieb	Benzin	77	105	Jul 1990	Sep 1992	2024-03-01	1582
Ford	Escort v turnier	1.8 16V	Kombi	Frontantrieb	Benzin	77	105	Feb 1992	Jan 1995	2024-03-01	1583
Ford	Escort v	1.4	Cabriolet	Frontantrieb	Benzin	52	71	Jul 1990	Apr 1994	2024-03-01	1584
Ford	Escort v	1.6	Cabriolet	Frontantrieb	Benzin	77	105	Jul 1990	Aug 1993	2024-03-01	1585
Ford	Escort v	1.8 16V Xr3i	Cabriolet	Frontantrieb	Benzin	77	105	Feb 1992	Jan 1995	2024-03-01	1586
Ford	Escort v	1.8 16V Xr3i	Cabriolet	Frontantrieb	Benzin	96	130	Feb 1992	Jan 1995	2024-03-01	1587
Ford	Mondeo i turnier	1.8 TD	Kombi	Frontantrieb	Diesel	65	88	Jun 1993	Aug 1996	2024-03-01	1588
Ford	Mondeo i turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	66	90	Apr 1993	Aug 1996	2024-03-01	1589
Ford	Mondeo i turnier	1.8 I 16V	Kombi	Frontantrieb	Benzin	85	115	Apr 1993	Aug 1996	2024-03-01	1590
Ford	Mondeo i turnier	2.0 I 16V	Kombi	Frontantrieb	Benzin	100	136	Apr 1993	Aug 1996	2024-03-01	1591
VW	Polo	0.9	Schrägheck	Frontantrieb	Benzin	29	40	Sep 1975	Sep 1981	2024-03-01	1592
VW	Polo	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Mar 1975	Sep 1981	2024-03-01	1593
VW	Polo	1.1	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1975	Sep 1981	2024-03-01	1594
VW	Polo	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Dec 1976	Sep 1981	2024-03-01	1595
VW	Derby	0.9	Stufenheck	Frontantrieb	Benzin	29	40	Feb 1977	Sep 1981	2024-03-01	1596
VW	Derby	1.1	Stufenheck	Frontantrieb	Benzin	37	50	Feb 1977	Sep 1981	2024-03-01	1597
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Feb 1977	Sep 1981	2024-03-01	1598
VW	Polo	1	Schrägheck	Frontantrieb	Benzin	29	40	Oct 1981	Oct 1986	2024-03-01	1599
VW	Polo	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1981	Sep 1989	2024-03-01	1600
VW	Polo	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1981	Jul 1983	2024-03-01	1601
VW	Polo	1.3 D	Schrägheck	Frontantrieb	Diesel	33	45	Aug 1986	Jul 1990	2024-03-01	1602
VW	Polo	1.4 D	Schrägheck	Frontantrieb	Diesel	35	48	Oct 1990	Sep 1994	2024-03-01	1603
VW	Polo	1.3 CAT	Schrägheck	Frontantrieb	Benzin	40	55	Jul 1987	Sep 1994	2024-03-01	1604
VW	Polo	1.0 CAT	Schrägheck	Frontantrieb	Benzin	33	45	Aug 1989	Sep 1994	2024-03-01	1605
VW	Polo	1.3 CAT	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1989	Mar 1991	2024-03-01	1606
VW	Derby	1	Stufenheck	Frontantrieb	Benzin	29	40	Oct 1981	Dec 1984	2024-03-01	1607
VW	Derby	1.1	Stufenheck	Frontantrieb	Benzin	37	50	Oct 1981	Jul 1983	2024-03-01	1608
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	40	55	Aug 1983	Dec 1984	2024-03-01	1609
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1981	Jul 1983	2024-03-01	1610
Nissan	Navara	2.5 DCI 4WD	Pick-up	Allrad	Diesel	140	190	Dec 2009	-	2024-03-01	1611
VW	Golf i	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Apr 1974	Jul 1983	2024-03-01	1612
VW	Golf i	1.1	Schrägheck	Frontantrieb	Benzin	38	52	Aug 1976	Jul 1980	2024-03-01	1613
Ford USA	Explorer	4.0 V6 4WD	SUV	Allrad	Benzin	121	165	Jan 1993	Dec 1994	2024-03-01	1615
Ford	Escort v	1.6 16V Xr3i	Cabriolet	Frontantrieb	Benzin	66	90	Dec 1992	Jan 1995	2024-03-01	1616
VW	Golf i	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Aug 1979	Jul 1983	2024-03-01	1617
VW	Golf i	1.5	Cabriolet	Frontantrieb	Benzin	51	70	Jan 1979	Nov 1983	2024-03-01	1618
VW	Golf i	1.5	Schrägheck	Frontantrieb	Benzin	51	70	Aug 1977	Jul 1983	2024-03-01	1619
Nissan	Navara	3.0 DCI 4WD	Pick-up	Allrad	Diesel	170	231	Feb 2010	-	2024-03-01	1620
VW	Golf i	1.5	Schrägheck	Frontantrieb	Benzin	51	70	Apr 1974	Dec 1975	2024-03-01	1621
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	40	55	May 1975	Jul 1979	2024-03-01	1622
Chevrolet	Aveo / kalos	1.2	Schrägheck	Frontantrieb	Benzin	55	75	Apr 2008	-	2024-03-01	1623
VW	Golf i	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Aug 1975	Feb 1984	2024-03-01	1624
VW	Golf i	1.6 GTI	Schrägheck	Frontantrieb	Benzin	81	110	Aug 1976	Jul 1982	2024-03-01	1625
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	50	68	May 1975	Jul 1979	2024-03-01	1626
Aston Martin	Cygnet	1.3	Schrägheck	Frontantrieb	Benzin	72	98	Apr 2011	Oct 2013	2024-03-01	1627
VW	Golf i	1.8 GTI	Schrägheck	Frontantrieb	Benzin	82	112	Aug 1982	Dec 1983	2024-03-01	1628
VW	Golf i	1.5 D	Schrägheck	Frontantrieb	Diesel	37	50	Aug 1976	Jul 1980	2024-03-01	1629
Fiat	Bravo ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	103	140	Apr 2010	Dec 2014	2024-03-01	1630
VW	Golf i	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Aug 1980	Jul 1983	2024-03-01	1631
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	53	72	May 1975	Jul 1979	2024-03-01	1632
VW	Golf i	1.6 TD	Schrägheck	Frontantrieb	Diesel	51	70	Mar 1982	Jul 1983	2024-03-01	1633
Fiat	Doblo kombi	1.4 Natural Power	Bus	Frontantrieb	Benzin/Erdgas (CNG)	88	120	Feb 2010	Dec 2023	2025-02-03	1634
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	66	90	May 1975	Jul 1979	2024-03-01	1635


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Ford Sierra Turnier I/II、Ford Granada II Turnier、Fiat Panda II 4x4，以及 Volkswagen Käfer 1200、1300、1500、1600、1302、1303 Sedan/Cabriolet 的首轮物理外廓聚类。
* 首次创建并闭合 13 个尺寸组。Sierra、Granada、Panda 使用对应 Auto-Data 车型页；Käfer 使用 Volkswagen Newsroom 官方历史车型资料。([汽车数据][1])
* Ktype `1555`、`1563` 因 1967 年 8 月前后外廓变化拆分；Ktype `1559` 明确覆盖 1302/1303 Cabriolet，已拆为两个物理分支。([Volkswagen Newsroom][2])

## 当前批次进度

* 已完成输入 Ktype：39/100
* READY 映射行：42
* PENDING 输入 Ktype：61/100
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1534	1534	Wagon	Sierra Turnier I		5	EU-FORD-SIERRA-TURNIER-I-01	HIGH		READY
1535	1535	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1536	1536	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1537	1537	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1538	1538	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1539	1539	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1540	1540	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1541	1541	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1543	1543	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1544	1544	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1545	1545	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1546	1546	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1547	1547	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1548	1548	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1549	1549	Sedan	Beetle 1200	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1550	1550	Sedan	Beetle 1200/1200L	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1551	1551	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1552	1552	Sedan	Beetle 1300	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	MEDIUM	输入结束期晚于官方1300分型期，按Type 11外廓关联。	READY
1553	1553	Hatchback	Panda II 4x4	169	5	EU-FIAT-PANDA-II-4X4-HATCHBACK-01	HIGH		READY
1554	1554	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1555_pre67	1555	Sedan	Beetle 1500	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH	1967年8月外廓变更前分支。	READY
1555_post67	1555	Sedan	Beetle 1500	Type 11	2	EU-VW-KAEFER-TYPE11-POST67-01	HIGH	1967年8月外廓变更后分支。	READY
1556	1556	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1557	1557	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1558	1558	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1559_1302	1559	Convertible	Beetle 1302 Cabriolet	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	原Ktype明确覆盖1302/1303，按1302物理车身拆分。	READY
1559_1303	1559	Convertible	Beetle 1303 Cabriolet	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	原Ktype明确覆盖1302/1303，按1303物理车身拆分。	READY
1560	1560	Sedan	Beetle 1600	Type 113	2	EU-VW-KAEFER-TYPE113-1600-01	MEDIUM	输入命名为1500 1.6，按同期Type 113 1.6外廓关联。	READY
1561	1561	Sedan	Beetle 1302	Type 11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
1562	1562	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1563_pre67	1563	Convertible	Beetle 1500 Cabriolet	Type 15	2	EU-VW-KAEFER-TYPE15-STD-01	HIGH	1967年8月外廓变更前分支。	READY
1563_post67	1563	Convertible	Beetle 1500 Cabriolet	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967年8月外廓变更后分支。	READY
1564	1564	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1565	1565	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1566	1566	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1567	1567	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1568	1568	Sedan	Beetle 1300	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1569	1569	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1570	1570	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1571	1571	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1572	1572	Sedan	Beetle 1302	Type 11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
1573	1573	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428	Auto-Data Ford Sierra generations	https://www.auto-data.net/en/ford-sierra-model-802
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428	Auto-Data Ford Sierra generations	https://www.auto-data.net/en/ford-sierra-model-802
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500	Volkswagen Newsroom Käfer 1200/1200L; Volkswagen Newsroom Käfer 1300	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-12001200l-profile-19585; https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1300-profile-19591
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380	Auto-Data Ford Granada Turnier (GNU)	https://www.auto-data.net/en/ford-granada-turnier-gnu-generation-1750
EU-FIAT-PANDA-II-4X4-HATCHBACK-01	3574	1605	1632	Auto-Data Fiat Panda II 4x4 1.2 8V	https://www.auto-data.net/de/fiat-panda-ii-4x4-1.2-8v-69hp-4x4-54402
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500	Volkswagen Newsroom Käfer 1500	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-profile-19600
EU-VW-KAEFER-1303-SEDAN-01	4080	1585	1500	Volkswagen Newsroom Käfer 1303	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1303-profile-19597
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500	Volkswagen Newsroom Käfer 1302 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-cabriolet-profile-19618
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500	Volkswagen Newsroom Käfer 1303 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1303-cabriolet-profile-19624
EU-VW-KAEFER-TYPE113-1600-01	4060	1550	1500	Volkswagen Newsroom Käfer 1600/1600i	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-16001600i-profile-19604
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500	Volkswagen Newsroom Käfer 1302	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-profile-19594
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500	Volkswagen Newsroom Käfer 1500 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-cabriolet-profile-19627
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500	Volkswagen Newsroom Käfer 1500 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-cabriolet-profile-19627
```

## 下一步优先处理

1. 优先闭合 Ford Scorpio I Turnier、Escort V Turnier/Cabriolet、Mondeo I Turnier，并批量关联相同车身 Ktype。
2. 随后处理 VW Polo I/II、Derby I/II、Golf I Hatchback/Cabriolet，重点拆分代际、改款及 Cabriolet 外廓。
3. 最后处理 Nissan Navara D40 的驾驶室/货斗分支，以及 Explorer、Taunus、Aveo/Kalos、Cygnet、Bravo II、Doblo 等独立车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-sierra-model-802 "Ford Sierra | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-profile-19600?utm_source=chatgpt.com "Vehicle data Beetle (Käfer) 1500 profile"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 本轮新增 59 条 READY 映射，覆盖 42 个输入 Ktype。
* 首次闭合 16 个尺寸组，覆盖 Scorpio I Turnier、Escort V/VI Turnier、Escort V/VI Cabrio、Mondeo I Turnier、Polo I、Derby I/II、Golf I、Golf I GTI/GTD 与 Golf I Cabriolet。Ford 各组按代际及改款外廓拆分。([汽车数据][1])
* Derby 按 1979 年尺寸变化拆分；Golf I 普通版和 GTI 按 1978 年尺寸变化拆分。([Volkswagen Newsroom][2])

## 2. 当前批次进度

* READY 输入 Ktype：81/100
* READY 映射：101
* PENDING 输入 Ktype：19/100
* 已确认尺寸组：29
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1574	1574	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1575	1575	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1576	1576	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1577	1577	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1578	1578	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1579_prefl	1579	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1579_facelift	1579	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1580_prefl	1580	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1580_facelift	1580	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1581_prefl	1581	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1581_facelift	1581	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1582	1582	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH		READY
1583_prefl	1583	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1583_facelift	1583	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1584_prefl	1584	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1584_facelift	1584	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1585_prefl	1585	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1585_facelift	1585	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1586_prefl	1586	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1586_facelift	1586	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1587_prefl	1587	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1587_facelift	1587	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1588	1588	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1589	1589	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1590	1590	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1591	1591	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1592	1592	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1593	1593	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1594	1594	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1595	1595	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1596_prefl	1596	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1596_facelift	1596	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1597_prefl	1597	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1597_facelift	1597	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1598_prefl	1598	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1598_facelift	1598	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1607	1607	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1608	1608	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1609	1609	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1610	1610	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1612_pre78	1612	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1612_post78	1612	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1613_pre78	1613	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1613_post78	1613	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1616	1616	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
1617	1617	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH		READY
1618	1618	Convertible	Golf I Cabriolet	TYPE155	2	EU-VW-GOLF-I-TYPE155-CONVERTIBLE-1P5-01	HIGH		READY
1619_pre78	1619	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1619_post78	1619	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1621	1621	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH		READY
1624_pre78	1624	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1624_post78	1624	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1625_pre78	1625	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1625_post78	1625	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1628	1628	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	HIGH		READY
1629_pre78	1629	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1629_post78	1629	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1631	1631	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH		READY
1633	1633	Hatchback	Golf I GTD	TYPE17		EU-VW-GOLF-I-TYPE17-GTD-HATCHBACK-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490	Auto-Data Ford Scorpio I Turnier (GGE)	https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-generation-1790
EU-FORD-ESCORT-V-WAGON-PREFL-01	4268	1690	1414	Automobile-Catalog 1991 Ford Escort Estate 1.8 D Ghia	https://www.automobile-catalog.com/car/1991/945605/ford_escort_estate_1_8_d_ghia.html
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier (GAL)	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	4036	1692	1395	Automobile-Catalog 1991 Ford Escort Cabrio 1.6i	https://www.automobile-catalog.com/car/1991/945740/ford_escort_cabrio_1_6i.html
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379	Auto-Data Ford Escort VI Cabrio (ALL)	https://www.auto-data.net/en/ford-escort-vi-cabrio-all-generation-1665
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510	Auto-Data Ford Mondeo I Wagon	https://www.auto-data.net/en/ford-mondeo-i-wagon-generation-1705
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344	Volkswagen Newsroom Polo I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-1-profile-19072
EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	3836	1560	1352	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	3915	1560	1352	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-II-TYPE87-SEDAN-01	3975	1600	1355	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	3705	1610	1410	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	3815	1610	1410	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-PRE78-01	3725	1630	1395	Volkswagen Newsroom Golf I GTI profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-gti-profile-19499
EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	3815	1630	1395	Volkswagen Newsroom Golf I GTI profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-gti-profile-19499
EU-VW-GOLF-I-TYPE17-GTD-HATCHBACK-01	3815	1630	1395	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE155-CONVERTIBLE-1P5-01	3815	1610	1410	Volkswagen Newsroom Golf I Cabriolet; Auto-Data Golf I Cabrio GLS 1.5	https://www.volkswagen-newsroom.com/en/golf-1-cabriolet-19791993-19488; https://www.auto-data.net/en/volkswagen-golf-i-cabrio-gls-1.5-70hp-8779
```

## 5. 下一步优先处理

1. 优先处理 Ktype `1599–1606` 的 Polo II Type 86C，确认输入 `Schrägheck` 对应 Steilheck 或 Coupé 外廓，并批量建立关联。
2. 处理 Navara D40 的驾驶室及货斗分支，以及 Explorer 的门数物理分支。
3. 闭合 Taunus、Aveo/Kalos、Cygnet、Bravo II、Doblo Ktype 的独立尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-generation-1790 "Ford Scorpio I Turnier (GGE) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-1-profile-19072 "Vehicle data Polo I profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 19 个 Ktype 已全部闭合。
* 本轮新增 30 条 READY 映射、14 个首次确认尺寸组。
* 已完成轻量机械检查：固定表头、主键唯一、100 个输入 Ktype 全覆盖、映射外键闭合、尺寸组无孤立记录、三维与来源均非空。

## 当前批次进度

* READY 输入 Ktype：100/100
* READY 映射：131
* PENDING：0/100
* DIMENSION_GROUP：43
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 两张最终文件：已生成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1534	1534	Wagon	Sierra Turnier I		5	EU-FORD-SIERRA-TURNIER-I-01	HIGH		READY
1535	1535	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1536	1536	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1537	1537	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1538	1538	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1539	1539	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1540	1540	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1541	1541	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1543	1543	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1544	1544	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1545	1545	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1546	1546	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1547	1547	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1548	1548	Wagon	Sierra Turnier II		5	EU-FORD-SIERRA-TURNIER-II-01	HIGH		READY
1549	1549	Sedan	Beetle 1200	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1550	1550	Sedan	Beetle 1200/1200L	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1551	1551	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1552	1552	Sedan	Beetle 1300	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	MEDIUM	输入结束期晚于官方1300分型期，按Type 11外廓关联。	READY
1553	1553	Hatchback	Panda II 4x4	169	5	EU-FIAT-PANDA-II-4X4-HATCHBACK-01	HIGH		READY
1554	1554	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1555_pre67	1555	Sedan	Beetle 1500	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH	1967年8月外廓变更前分支。	READY
1555_post67	1555	Sedan	Beetle 1500	Type 11	2	EU-VW-KAEFER-TYPE11-POST67-01	HIGH	1967年8月外廓变更后分支。	READY
1556	1556	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1557	1557	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1558	1558	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1559_1302	1559	Convertible	Beetle 1302 Cabriolet	Type 15	2	EU-VW-KAEFER-1302-CONVERTIBLE-01	HIGH	原Ktype明确覆盖1302/1303，按1302物理车身拆分。	READY
1559_1303	1559	Convertible	Beetle 1303 Cabriolet	Type 15	2	EU-VW-KAEFER-1303-CONVERTIBLE-01	HIGH	原Ktype明确覆盖1302/1303，按1303物理车身拆分。	READY
1560	1560	Sedan	Beetle 1600	Type 113	2	EU-VW-KAEFER-TYPE113-1600-01	MEDIUM	输入命名为1500 1.6，按同期Type 113 1.6外廓关联。	READY
1561	1561	Sedan	Beetle 1302	Type 11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
1562	1562	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1563_pre67	1563	Convertible	Beetle 1500 Cabriolet	Type 15	2	EU-VW-KAEFER-TYPE15-STD-01	HIGH	1967年8月外廓变更前分支。	READY
1563_post67	1563	Convertible	Beetle 1500 Cabriolet	Type 15	2	EU-VW-KAEFER-TYPE15-POST67-01	HIGH	1967年8月外廓变更后分支。	READY
1564	1564	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1565	1565	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1566	1566	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1567	1567	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1568	1568	Sedan	Beetle 1300	Type 11	2	EU-VW-KAEFER-TYPE11-STD-01	HIGH		READY
1569	1569	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1570	1570	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1571	1571	Wagon	Granada II Turnier	GNU	5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
1572	1572	Sedan	Beetle 1302	Type 11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH		READY
1573	1573	Sedan	Beetle 1303	Type 11	2	EU-VW-KAEFER-1303-SEDAN-01	HIGH		READY
1574	1574	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1575	1575	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1576	1576	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1577	1577	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1578	1578	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-01	HIGH		READY
1579_prefl	1579	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1579_facelift	1579	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1580_prefl	1580	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1580_facelift	1580	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1581_prefl	1581	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1581_facelift	1581	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1582	1582	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH		READY
1583_prefl	1583	Wagon	Escort V Turnier		5	EU-FORD-ESCORT-V-WAGON-PREFL-01	HIGH	Ktype跨越1992年外廓改款，改款前分支。	READY
1583_facelift	1583	Wagon	Escort VI Turnier	GAL	5	EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	HIGH	Ktype跨越1992年外廓改款，改款后分支。	READY
1584_prefl	1584	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1584_facelift	1584	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1585_prefl	1585	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1585_facelift	1585	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1586_prefl	1586	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1586_facelift	1586	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1587_prefl	1587	Convertible	Escort V Cabrio	ALL	2	EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	HIGH	Ktype跨越1993年外廓改款，改款前分支。	READY
1587_facelift	1587	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH	Ktype跨越1993年外廓改款，改款后分支。	READY
1588	1588	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1589	1589	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1590	1590	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1591	1591	Wagon	Mondeo I Turnier	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-01	HIGH		READY
1592	1592	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1593	1593	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1594	1594	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1595	1595	Hatchback	Polo I	TYPE86	3	EU-VW-POLO-I-TYPE86-HATCHBACK-01	HIGH		READY
1596_prefl	1596	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1596_facelift	1596	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1597_prefl	1597	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1597_facelift	1597	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1598_prefl	1598	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	HIGH	Ktype跨越1979年外廓改款，改款前分支。	READY
1598_facelift	1598	Sedan	Derby I	TYPE87	2	EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	HIGH	Ktype跨越1979年外廓改款，改款后分支。	READY
1599	1599	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
1600	1600	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
1601	1601	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
1602	1602	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
1603	1603	Hatchback	Polo II facelift	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH		READY
1604_prefl	1604	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	Ktype跨越1990年外廓改款，改款前分支。	READY
1604_facelift	1604	Hatchback	Polo II facelift	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1990年外廓改款，改款后分支。	READY
1605_prefl	1605	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	Ktype跨越1990年外廓改款，改款前分支。	READY
1605_facelift	1605	Hatchback	Polo II facelift	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1990年外廓改款，改款后分支。	READY
1606_prefl	1606	Hatchback	Polo II	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	Ktype跨越1990年外廓改款，改款前分支。	READY
1606_facelift	1606	Hatchback	Polo II facelift	TYPE86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH	Ktype跨越1990年外廓改款，改款后分支。	READY
1607	1607	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1608	1608	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1609	1609	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1610	1610	Sedan	Derby II	TYPE87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH		READY
1611_kingcab	1611	Pickup	Navara D40	D40	4	EU-NISSAN-NAVARA-D40-KINGCAB-01	HIGH	King Cab物理车身分支。	READY
1611_doublecab	1611	Pickup	Navara D40	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH	Double Cab物理车身分支。	READY
1612_pre78	1612	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1612_post78	1612	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1613_pre78	1613	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1613_post78	1613	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1615_3dr	1615	SUV	Explorer I	UN46	3	EU-FORD-USA-EXPLORER-I-UN46-SUV-3D-01	HIGH	三门短车身分支。	READY
1615_5dr	1615	SUV	Explorer I	UN46	5	EU-FORD-USA-EXPLORER-I-UN46-SUV-5D-01	HIGH	五门长车身分支。	READY
1616	1616	Convertible	Escort VI Cabrio	ALL	2	EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	HIGH		READY
1617	1617	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH		READY
1618	1618	Convertible	Golf I Cabriolet	TYPE155	2	EU-VW-GOLF-I-TYPE155-CONVERTIBLE-1P5-01	HIGH		READY
1619_pre78	1619	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1619_post78	1619	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1620	1620	Pickup	Navara D40	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH	3.0 dCi V6仅对应Double Cab外廓。	READY
1621	1621	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH		READY
1622_2dr	1622	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	两门轿车物理分支。	READY
1622_4dr	1622	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
1623_3dr	1623	Hatchback	Aveo I facelift	T255	3	EU-CHEVROLET-AVEO-I-T255-HATCHBACK-3D-01	HIGH	三门掀背物理分支。	READY
1623_5dr	1623	Hatchback	Aveo I facelift	T255	5	EU-CHEVROLET-AVEO-I-T255-HATCHBACK-5D-01	HIGH	五门掀背物理分支。	READY
1624_pre78	1624	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1624_post78	1624	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1625_pre78	1625	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1625_post78	1625	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1626_2dr	1626	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	两门轿车物理分支。	READY
1626_4dr	1626	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
1627	1627	Hatchback	Cygnet		2	EU-ASTON-MARTIN-CYGNET-HATCHBACK-2D-01	HIGH		READY
1628	1628	Hatchback	Golf I GTI	TYPE17	3	EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	HIGH		READY
1629_pre78	1629	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	HIGH	Ktype跨越1978年外廓变更，1978年前分支。	READY
1629_post78	1629	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH	Ktype跨越1978年外廓变更，1978年起分支。	READY
1630	1630	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
1631	1631	Hatchback	Golf I	TYPE17		EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	HIGH		READY
1632_2dr	1632	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	两门轿车物理分支。	READY
1632_4dr	1632	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
1633	1633	Hatchback	Golf I GTD	TYPE17		EU-VW-GOLF-I-TYPE17-GTD-HATCHBACK-01	HIGH		READY
1634_prefl	1634	MPV	Doblò II	263	5	EU-FIAT-DOBLO-II-263-MPV-PREFL-01	HIGH	2015年外廓改款前分支。	READY
1634_facelift	1634	MPV	Doblò II facelift	263	5	EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	HIGH	2015年外廓改款后分支。	READY
1635_2dr	1635	Sedan	Taunus TC2		2	EU-FORD-TAUNUS-TC2-SEDAN-2D-01	HIGH	两门轿车物理分支。	READY
1635_4dr	1635	Sedan	Taunus TC2		4	EU-FORD-TAUNUS-TC2-SEDAN-4D-01	HIGH	四门轿车物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1501-1600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428	Auto-Data Ford Sierra generations	https://www.auto-data.net/en/ford-sierra-model-802
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428	Auto-Data Ford Sierra generations	https://www.auto-data.net/en/ford-sierra-model-802
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500	Volkswagen Newsroom Käfer 1200/1200L; Volkswagen Newsroom Käfer 1300	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-12001200l-profile-19585; https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1300-profile-19591
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380	Auto-Data Ford Granada Turnier (GNU)	https://www.auto-data.net/en/ford-granada-turnier-gnu-generation-1750
EU-FIAT-PANDA-II-4X4-HATCHBACK-01	3574	1605	1632	Auto-Data Fiat Panda II 4x4 1.2 8V	https://www.auto-data.net/de/fiat-panda-ii-4x4-1.2-8v-69hp-4x4-54402
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500	Volkswagen Newsroom Käfer 1500	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-profile-19600
EU-VW-KAEFER-1303-SEDAN-01	4080	1585	1500	Volkswagen Newsroom Käfer 1303	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1303-profile-19597
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500	Volkswagen Newsroom Käfer 1302 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-cabriolet-profile-19618
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500	Volkswagen Newsroom Käfer 1303 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1303-cabriolet-profile-19624
EU-VW-KAEFER-TYPE113-1600-01	4060	1550	1500	Volkswagen Newsroom Käfer 1600/1600i	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-16001600i-profile-19604
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500	Volkswagen Newsroom Käfer 1302	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-profile-19594
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500	Volkswagen Newsroom Käfer 1500 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-cabriolet-profile-19627
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500	Volkswagen Newsroom Käfer 1500 Cabriolet	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-cabriolet-profile-19627
EU-FORD-SCORPIO-I-GGE-WAGON-01	4744	1760	1490	Auto-Data Ford Scorpio I Turnier (GGE)	https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-generation-1790
EU-FORD-ESCORT-V-WAGON-PREFL-01	4268	1690	1414	Automobile-Catalog 1991 Ford Escort Estate 1.8 D Ghia	https://www.automobile-catalog.com/car/1991/945605/ford_escort_estate_1_8_d_ghia.html
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier (GAL)	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-FORD-ESCORT-V-ALL-CONVERTIBLE-PREFL-01	4036	1692	1395	Automobile-Catalog 1991 Ford Escort Cabrio 1.6i	https://www.automobile-catalog.com/car/1991/945740/ford_escort_cabrio_1_6i.html
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379	Auto-Data Ford Escort VI Cabrio (ALL)	https://www.auto-data.net/en/ford-escort-vi-cabrio-all-generation-1665
EU-FORD-MONDEO-I-BNP-WAGON-01	4671	1751	1510	Auto-Data Ford Mondeo I Wagon	https://www.auto-data.net/en/ford-mondeo-i-wagon-generation-1705
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344	Volkswagen Newsroom Polo I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-1-profile-19072
EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	3836	1560	1352	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	3915	1560	1352	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-II-TYPE87-SEDAN-01	3975	1600	1355	Volkswagen Newsroom Derby profile	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-GOLF-I-TYPE17-HATCHBACK-PRE78-01	3705	1610	1410	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE17-HATCHBACK-POST78-01	3815	1610	1410	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-PRE78-01	3725	1630	1395	Volkswagen Newsroom Golf I GTI profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-gti-profile-19499
EU-VW-GOLF-I-TYPE17-GTI-HATCHBACK-POST78-01	3815	1630	1395	Volkswagen Newsroom Golf I GTI profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-gti-profile-19499
EU-VW-GOLF-I-TYPE17-GTD-HATCHBACK-01	3815	1630	1395	Volkswagen Newsroom Golf I profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-profile-19468
EU-VW-GOLF-I-TYPE155-CONVERTIBLE-1P5-01	3815	1610	1410	Volkswagen Newsroom Golf I Cabriolet; Auto-Data Golf I Cabrio GLS 1.5	https://www.volkswagen-newsroom.com/en/golf-1-cabriolet-19791993-19488; https://www.auto-data.net/en/volkswagen-golf-i-cabrio-gls-1.5-70hp-8779
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355	Volkswagen Newsroom Polo II profile	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350	Auto-Data Volkswagen Polo II 1.4 D	https://www.auto-data.net/en/volkswagen-polo-ii-86c-1.4-d-48hp-8488
EU-NISSAN-NAVARA-D40-KINGCAB-01	5296	1848	1783	Nissan Navara 2011 UK brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Navara-UK.pdf
EU-NISSAN-NAVARA-D40-DOUBLECAB-01	5296	1848	1795	Nissan Navara 2013 UK brochure	https://xr793.com/wp-content/uploads/2022/10/2013-Nissan-Navara-UK.pdf
EU-FORD-USA-EXPLORER-I-UN46-SUV-3D-01	4430	1783	1715	Ford 1994 Explorer brochure	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_1994.pdf
EU-FORD-USA-EXPLORER-I-UN46-SUV-5D-01	4681	1783	1709	Ford 1994 Explorer brochure	https://www.auto-brochures.com/makes/Ford/Explorer/Ford_US%20Explorer_1994.pdf
EU-FORD-TAUNUS-TC2-SEDAN-2D-01	4380	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 GL	https://www.automobile-catalog.com/car/1976/920975/ford_taunus_1_3_gl.html
EU-FORD-TAUNUS-TC2-SEDAN-4D-01	4380	1700	1362	Automobile-Catalog 1976 Ford Taunus 1.3 GL	https://www.automobile-catalog.com/car/1976/920975/ford_taunus_1_3_gl.html
EU-CHEVROLET-AVEO-I-T255-HATCHBACK-3D-01	3920	1680	1505	Automobile-Catalog 2008 Chevrolet Aveo 1.2 LS Hatchback	https://www.automobile-catalog.com/car/2008/559205/chevrolet_aveo_1_2_ls_hatchback.html
EU-CHEVROLET-AVEO-I-T255-HATCHBACK-5D-01	3920	1680	1505	Automobile-Catalog 2008 Chevrolet Aveo 1.2 LS Hatchback	https://www.automobile-catalog.com/car/2008/559205/chevrolet_aveo_1_2_ls_hatchback.html
EU-ASTON-MARTIN-CYGNET-HATCHBACK-2D-01	3078	1680	1500	Aston Martin Cygnet official brochure	https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_int-Cygnet_2012-v1.pdf
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Automobile-Catalog 2010 Fiat Bravo 1.4 T-Jet	https://www.automobile-catalog.com/car/2010/1456655/fiat_bravo_1_4_t-jet_16v_120_emotion_euro_5.html
EU-FIAT-DOBLO-II-263-MPV-PREFL-01	4390	1832	1845	Auto-Data Fiat Doblò II (263)	https://www.auto-data.net/en/fiat-doblo-ii-263-generation-4059
EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	4406	1832	1899	Auto-Data Fiat Doblò II facelift 1.4 T-JET CNG	https://www.auto-data.net/en/fiat-doblo-ii-263-facelift-2015-1.4-t-jet-120hp-cng-22104
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1501-1600_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1501-1600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1501-1600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2033 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（505 行）
