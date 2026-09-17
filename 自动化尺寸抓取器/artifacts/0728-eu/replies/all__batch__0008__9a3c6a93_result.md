# 任务：all 第 701-800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0008__9a3c6a93


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 701-800 行

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
all 第 701-800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Orion ii	1.6 I CAT	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1986	Jul 1990	2024-03-01	727
Ford	Orion ii	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Dec 1985	Jan 1989	2024-03-01	728
Ford	Orion ii	1.8 D	Stufenheck	Frontantrieb	Diesel	44	60	Jan 1989	Jul 1990	2024-03-01	729
Peugeot	508 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	103	140	Nov 2010	Dec 2018	2024-03-01	730
Peugeot	508 i	2.0 HDI	Stufenheck	Frontantrieb	Diesel	120	163	Nov 2010	Dec 2018	2024-03-01	731
Peugeot	508 sw i	2.0 HDI	Kombi	Frontantrieb	Diesel	120	163	Nov 2010	Dec 2018	2024-03-01	732
Peugeot	508 i	2.2 HDI	Stufenheck	Frontantrieb	Diesel	150	204	Nov 2010	Dec 2018	2024-03-01	733
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	43	58	Jul 1979	Jul 1982	2024-03-01	734
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	51	69	Jul 1979	Jul 1982	2024-03-01	735
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	54	73	Jul 1979	Jul 1982	2024-03-01	736
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	74	100	Jul 1979	Jul 1982	2024-03-01	737
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1979	Jul 1982	2024-03-01	738
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	84	114	Jul 1979	Jul 1982	2024-03-01	739
Ford	Sierra	1.6	Schrägheck	Heckantrieb	Benzin	55	75	Jan 1987	Feb 1993	2024-03-01	740
Ford	Sierra	1.6	Stufenheck	Heckantrieb	Benzin	55	75	Jan 1987	Feb 1993	2024-03-01	741
Ford	Sierra	1.8	Schrägheck	Heckantrieb	Benzin	64	87	May 1988	Feb 1993	2024-03-01	742
Ford	Sierra	1.8	Stufenheck	Heckantrieb	Benzin	64	87	May 1988	Feb 1993	2024-03-01	743
Ford	Sierra	1.8	Stufenheck	Heckantrieb	Benzin	59	80	Oct 1987	Sep 1989	2024-03-01	744
Ford	Sierra	1.8	Schrägheck	Heckantrieb	Benzin	59	80	Oct 1987	May 1988	2024-03-01	745
Ford	Sierra	1.8	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1987	May 1988	2024-03-01	746
Ford	Sierra	1.8	Schrägheck	Heckantrieb	Benzin	66	90	Jan 1987	May 1988	2024-03-01	747
Mercedes-benz	Sl	280 SL	Cabriolet	Heckantrieb	Benzin	136	185	Aug 1974	Jul 1985	2024-03-01	748
Ford	Sierra	2	Schrägheck	Heckantrieb	Benzin	77	105	Jan 1987	Feb 1993	2024-03-01	749
Ford	Sierra	2	Stufenheck	Heckantrieb	Benzin	77	105	Jan 1987	Feb 1993	2024-03-01	750
Ford	Sierra	2.0 RS Cosworth	Schrägheck	Heckantrieb	Benzin	150	204	Nov 1987	Jan 1990	2024-03-01	751
Mercedes-benz	Sl	300 SL	Cabriolet	Heckantrieb	Benzin	132	180	Sep 1985	Aug 1989	2024-03-01	752
Mercedes-benz	Sl	300 SL	Cabriolet	Heckantrieb	Benzin	138	188	Sep 1985	Aug 1989	2024-03-01	753
Peugeot	508 sw i	2.2 HDI	Kombi	Frontantrieb	Diesel	150	204	Nov 2010	Dec 2018	2024-03-01	754
Ford	Sierra	1.8 TD	Stufenheck	Heckantrieb	Diesel	55	75	Aug 1988	Feb 1993	2024-03-01	755
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Nov 2010	Dec 2012	2024-03-01	756
Ford	Sierra	1.8 TD	Schrägheck	Heckantrieb	Diesel	55	75	Aug 1988	Feb 1993	2024-03-01	757
Ford	Sierra	2.3 D	Stufenheck	Heckantrieb	Diesel	49	67	Jan 1987	Sep 1989	2024-03-01	758
Ford	Sierra	2.3 D	Schrägheck	Heckantrieb	Diesel	49	67	Jan 1987	Sep 1989	2024-03-01	759
Mercedes-benz	Sl	350 SL	Cabriolet	Heckantrieb	Benzin	143	195	May 1971	Feb 1980	2024-03-01	760
Ford	Sierra	1.6 I	Stufenheck	Heckantrieb	Benzin	59	80	Oct 1989	Feb 1993	2024-03-01	761
Seat	Leon	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Feb 2010	Dec 2012	2024-03-01	762
Ford	Sierra	1.6 I	Schrägheck	Heckantrieb	Benzin	59	80	Oct 1989	Feb 1993	2024-03-01	763
Ford	Sierra	1.6	Stufenheck	Heckantrieb	Benzin	53	72	Jan 1988	Feb 1993	2024-03-01	764
Ford	Sierra	1.6	Schrägheck	Heckantrieb	Benzin	53	72	Jan 1988	Feb 1993	2024-03-01	765
Mercedes-benz	Sl	380 SL	Cabriolet	Heckantrieb	Benzin	160	218	Sep 1980	Aug 1981	2024-03-01	766
Mercedes-benz	Sl	380 SL	Cabriolet	Heckantrieb	Benzin	150	204	Sep 1980	Aug 1985	2024-03-01	767
Ford	Sierra	2.0 I CAT	Schrägheck	Heckantrieb	Benzin	74	100	Jan 1987	Feb 1993	2024-03-01	768
Mercedes-benz	Sl	420 SL	Cabriolet	Heckantrieb	Benzin	150	204	Jan 1986	Aug 1989	2024-03-01	769
Mercedes-benz	Sl	420 SL	Cabriolet	Heckantrieb	Benzin	160	218	Jan 1986	Aug 1989	2024-03-01	770
Mercedes-benz	Sl	450 SL	Cabriolet	Heckantrieb	Benzin	160	218	Sep 1975	Oct 1980	2024-03-01	771
Mercedes-benz	Sl	450 SLC	Coupe	Heckantrieb	Benzin	160	218	Sep 1975	Aug 1979	2024-03-01	772
Mercedes-benz	Sl	450 SL	Cabriolet	Heckantrieb	Benzin	165	224	Oct 1972	Oct 1980	2024-03-01	773
Mercedes-benz	Sl	500 SL	Cabriolet	Heckantrieb	Benzin	164	223	Jan 1986	Aug 1989	2024-03-01	774
Mercedes-benz	Sl	500 SL	Cabriolet	Heckantrieb	Benzin	170	231	May 1980	Dec 1985	2024-03-01	775
Mercedes-benz	Sl	500 SL	Cabriolet	Heckantrieb	Benzin	177	241	May 1980	Dec 1981	2024-03-01	776
Mercedes-benz	Sl	500 SL	Cabriolet	Heckantrieb	Benzin	180	245	Jan 1986	Aug 1989	2024-03-01	777
Suzuki	Sx4	1.6	Stufenheck	Frontantrieb	Benzin	88	120	Oct 2007	-	2024-03-01	779
Ford	Sierra	2.0 I CAT	Stufenheck	Heckantrieb	Benzin	74	100	Jan 1987	Feb 1993	2024-03-01	780
Ford	Sierra	2.0 16V Cosworth CAT 4X4	Schrägheck	Allrad	Benzin	162	220	Jan 1990	Feb 1993	2024-03-01	781
Ford	Sierra	2.0 I	Schrägheck	Heckantrieb	Benzin	85	115	Jan 1987	Feb 1993	2024-03-01	782
Ford	Sierra	2.0 I	Stufenheck	Heckantrieb	Benzin	85	115	Jan 1987	Feb 1993	2024-03-01	783
Ford	Sierra	2.0 4X4	Stufenheck	Allrad	Benzin	88	120	Jan 1990	Feb 1993	2024-03-01	784
Ford	Sierra	2.0 I	Stufenheck	Heckantrieb	Benzin	88	120	Jan 1990	Feb 1993	2024-03-01	785
Ford	Sierra	2.0 I	Schrägheck	Heckantrieb	Benzin	88	120	Jun 1989	Feb 1993	2024-03-01	786
Mercedes-benz	123	230 CE	Coupe	Heckantrieb	Benzin	100	136	Apr 1980	Dec 1985	2024-03-01	787
Mercedes-benz	123	230 C	Coupe	Heckantrieb	Benzin	80	109	May 1977	Apr 1980	2024-03-01	788
Mercedes-benz	123	280 C	Coupe	Heckantrieb	Benzin	115	156	Mar 1977	Mar 1980	2024-03-01	789
Ford	Granada	1.7	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1972	Feb 1975	2024-03-01	790
Mercedes-benz	123	280 CE	Coupe	Heckantrieb	Benzin	130	177	Sep 1977	Aug 1979	2024-03-01	791
Mercedes-benz	123	280 CE	Coupe	Heckantrieb	Benzin	136	185	Mar 1977	Nov 1985	2024-03-01	792
Ford	Granada	2	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1975	Aug 1977	2024-03-01	793
Mercedes-benz	123	300 C Turbo-d	Coupe	Heckantrieb	Diesel	92	125	Sep 1981	Jul 1985	2024-03-01	794
Ford	Granada	2.3	Stufenheck	Heckantrieb	Benzin	79	108	Jan 1975	Aug 1977	2024-03-01	796
Land Rover	Discovery iv	2.7 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	140	190	Sep 2009	Dec 2018	2024-03-01	797
Ford	Granada	2	Kombi	Heckantrieb	Benzin	66	90	Jan 1975	Aug 1977	2024-03-01	798
Opel	Vectra a cc	1.6 I	Schrägheck	Frontantrieb	Benzin	52	71	Sep 1993	Nov 1995	2024-03-01	799
Land Rover	Discovery iv	3.0 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	155	211	May 2010	Dec 2018	2024-03-01	800
Mercedes-benz	124	230 CE	Coupe	Heckantrieb	Benzin	100	136	Mar 1987	Dec 1992	2024-03-01	801
Opel	Ascona c	1.3 N	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1981	Aug 1986	2024-03-01	802
Nissan	Np300 pickup	2.5 DCI 4X4	Pick-up	Allrad	Diesel	98	133	Apr 2008	-	2024-03-01	803
Mercedes-benz	124	300 CE	Coupe	Heckantrieb	Benzin	138	188	Mar 1987	Dec 1989	2024-03-01	804
Opel	Ascona c cc	1.3 N	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1981	Aug 1986	2024-03-01	805
Mercedes-benz	124	300 Ce-24	Coupe	Heckantrieb	Benzin	162	220	Sep 1989	Dec 1992	2024-03-01	806
Mercedes-benz	E-Klasse	E 200	Cabriolet	Heckantrieb	Benzin	100	136	Jun 1993	Mar 1998	2024-03-01	807
Opel	Ascona c	1.3 S	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1981	Aug 1988	2024-03-01	808
Mercedes-benz	E-Klasse	E 200	Coupe	Heckantrieb	Benzin	100	136	Jun 1993	Jun 1997	2024-03-01	809
Opel	Ascona c cc	1.3 S	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1981	Aug 1988	2024-03-01	810
Mercedes-benz	E-Klasse	E 220	Cabriolet	Heckantrieb	Benzin	110	150	Jun 1993	Mar 1998	2024-03-01	811
Opel	Ascona c cc	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1981	Aug 1988	2024-03-01	812
Mercedes-benz	E-Klasse	E 220	Coupe	Heckantrieb	Benzin	110	150	Jun 1993	Jun 1997	2024-03-01	813
Mercedes-benz	124	230 CE CAT	Coupe	Heckantrieb	Benzin	97	132	Jun 1989	Dec 1992	2024-03-01	814
Mercedes-benz	124	300 CE	Coupe	Heckantrieb	Benzin	132	180	Mar 1987	May 1993	2024-03-01	815
Suzuki	Sx4 / classic	1.5 VVT	Schrägheck	Frontantrieb	Benzin	82	112	Jul 2010	-	2024-03-01	816
Mercedes-benz	124	300 Ce-24	Cabriolet	Heckantrieb	Benzin	162	220	Apr 1992	Jun 1993	2024-03-01	817
Mercedes-benz	E-Klasse	E 320	Cabriolet	Heckantrieb	Benzin	162	220	Jun 1993	Mar 1998	2024-03-01	818
Mercedes-benz	E-Klasse	E 320	Coupe	Heckantrieb	Benzin	162	220	Jun 1993	Jun 1997	2024-03-01	819
Opel	Ascona c	1.6	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1981	Sep 1987	2024-03-01	820
Opel	Ascona c cc	1.6	Schrägheck	Frontantrieb	Benzin	60	82	Sep 1986	Aug 1988	2024-03-01	821
Opel	Ascona c	1.6	Stufenheck	Frontantrieb	Benzin	60	82	Sep 1986	Aug 1988	2024-03-01	822
Opel	Ascona c cc	1.6 S	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1981	Aug 1986	2024-03-01	823
Opel	Ascona c	1.6 S	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1981	Aug 1986	2024-03-01	824
Opel	Ascona c	1.8	Stufenheck	Frontantrieb	Benzin	62	84	Sep 1987	Aug 1988	2024-03-01	825
Opel	Ascona c cc	1.8	Schrägheck	Frontantrieb	Benzin	62	84	Sep 1987	Aug 1988	2024-03-01	826
Opel	Ascona c	1.8 E	Stufenheck	Frontantrieb	Benzin	74	100	Jan 1985	Aug 1986	2024-03-01	827
Opel	Ascona c cc	1.8 E	Schrägheck	Frontantrieb	Benzin	74	100	Jan 1985	Aug 1986	2024-03-01	828


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理车身聚类完成 Orion II、Peugeot 508 I、Ford Sierra 普通版、Mercedes-Benz R107/C107/C123/C124/A124、Seat Leon 1P facelift、Opel Ascona C 等车型的批量映射，共闭合 17 个尺寸组。Peugeot 508 Sedan 与 SW、Sierra Sedan 与 Hatchback 均按不同外廓独立建组。([汽车数据网][1])
* Ktype `801`、`804`、`814`、`815` 跨越 C124 外廓高度变化阶段，已分别派生为 `prefl` 和 `facelift`，没有保留无后缀基础行；A124 Convertible 独立建组。([汽车数据网][2])
* R107 facelift 根据具体车型三维拆为高度 `1300 mm` 和 `1307 mm` 两组，没有采用代际概览中不匹配具体车型的尺寸。([汽车数据网][3])
* Sierra Cosworth 的输入车身形式与已查到的量产车身证据存在冲突，且涉及特殊外部套件，因此 Ktype `751`、`781` 暂不复用普通 Sierra 尺寸组。([汽车数据网][4])
* Discovery IV 按硬性宽度口径复核后维持 `PENDING`：当前资料中的 `2022 mm` 是后视镜折叠状态宽度，不作为明确的不含外后视镜车身宽度落盘。([汽车数据网][5])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射行：86
* PENDING Ktype／映射行：18
* 已确认尺寸组：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
727	727	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
728	728	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
729	729	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
730	730	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
731	731	Sedan	508 I Phase I		4	EU-PEUGEOT-508-I-PHASE1-SEDAN-01	HIGH		READY
732	732	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
733	733	Sedan	508 I Phase I		4	EU-PEUGEOT-508-I-PHASE1-SEDAN-01	HIGH		READY
734	734	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
735	735	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
736	736	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
737	737	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
738	738	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
739	739	Sedan	Taunus 80				LOW	Taunus 80轿车门数分支及完整三维尚未闭合。	PENDING: Taunus 80轿车门数分支及完整三维尚未闭合。
740	740	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
741	741	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
742	742	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
743	743	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
744	744	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
745	745	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
746	746	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
747	747	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
748	748	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
749	749	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
750	750	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
751	751	Hatchback	Sierra II				LOW	输入Schrägheck与Cosworth实际车身分支存在冲突，特殊外观三维尚未闭合。	PENDING: 输入Schrägheck与Cosworth实际车身分支存在冲突，特殊外观三维尚未闭合。
752	752	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	HIGH		READY
753	753	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	HIGH		READY
754	754	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
755	755	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
756	756	Hatchback	Leon II facelift 2009	1P	5	EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	HIGH		READY
757	757	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
758	758	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
759	759	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
760	760	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
761	761	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
762	762	Hatchback	Leon II facelift 2009	1P	5	EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	HIGH		READY
763	763	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
764	764	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
765	765	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
766	766	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
767	767	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
768	768	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
769	769	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
770	770	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
771	771	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
772	772	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
773	773	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
774	774	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
775	775	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
776	776	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
777	777	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
779	779	Sedan	SX4 I Sedan		4		LOW	1.6 120 hp轿车生产阶段与不含镜三维尚未由同一配置闭合。	PENDING: 1.6 120 hp轿车生产阶段与不含镜三维尚未由同一配置闭合。
780	780	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
781	781	Hatchback	Sierra II				LOW	输入Schrägheck与Cosworth实际车身分支存在冲突，特殊外观三维尚未闭合。	PENDING: 输入Schrägheck与Cosworth实际车身分支存在冲突，特殊外观三维尚未闭合。
782	782	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
783	783	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
784	784	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
785	785	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
786	786	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
787	787	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
788	788	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
789	789	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
790	790	Sedan	Granada Mk I				LOW	Granada Mk I轿车门数分支及同一配置高度尚未闭合。	PENDING: Granada Mk I轿车门数分支及同一配置高度尚未闭合。
791	791	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
792	792	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
793	793	Sedan	Granada Mk I				LOW	Granada Mk I轿车门数分支及同一配置高度尚未闭合。	PENDING: Granada Mk I轿车门数分支及同一配置高度尚未闭合。
794	794	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
796	796	Sedan	Granada Mk I				LOW	Granada Mk I轿车门数分支及同一配置高度尚未闭合。	PENDING: Granada Mk I轿车门数分支及同一配置高度尚未闭合。
797	797	SUV	Discovery IV	L319	5		MEDIUM	现有来源仅给出折叠后视镜宽度，尚未取得明确不含后视镜WidthMM。	PENDING: 现有来源仅给出折叠后视镜宽度，尚未取得明确不含后视镜WidthMM。
798	798	Wagon	Granada Mk I Turnier				LOW	Granada Mk I旅行版同一配置三维尚未闭合。	PENDING: Granada Mk I旅行版同一配置三维尚未闭合。
799	799	Hatchback	Vectra A CC				LOW	Vectra A CC改款阶段、门数边界及完整三维尚未闭合。	PENDING: Vectra A CC改款阶段、门数边界及完整三维尚未闭合。
800	800	SUV	Discovery IV	L319	5		MEDIUM	现有来源仅给出折叠后视镜宽度，尚未取得明确不含后视镜WidthMM。	PENDING: 现有来源仅给出折叠后视镜宽度，尚未取得明确不含后视镜WidthMM。
801_prefl	801	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
801_facelift	801	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
802	802	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
803	803	Pickup	NP300 Pickup				LOW	输入未区分CAB、BED及对应车身代码，无法确定唯一物理外廓。	PENDING: 输入未区分CAB、BED及对应车身代码，无法确定唯一物理外廓。
804_prefl	804	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
804_facelift	804	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
805	805	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
806	806	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
807	807	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
808	808	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
809	809	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
810	810	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
811	811	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
812	812	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
813	813	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
814_prefl	814	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
814_facelift	814	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
815_prefl	815	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
815_facelift	815	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
816	816	Hatchback	SX4 I				LOW	1.5 VVT 112 hp的具体生产阶段与同一配置不含镜三维尚未闭合。	PENDING: 1.5 VVT 112 hp的具体生产阶段与同一配置不含镜三维尚未闭合。
817	817	Convertible	W124 A124	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
818	818	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
819	819	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
820	820	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
821	821	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
822	822	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
823	823	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
824	824	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1385-01	HIGH		READY
825	825	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
826	826	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
827	827	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
828	828	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ORION-II-SEDAN-01	4210	1640	1390	UltimateSpecs Ford Orion II	https://www.ultimatespecs.com/car-specs/Ford/M1192/Orion-II
EU-PEUGEOT-508-I-PHASE1-WAGON-01	4813	1920	1476	Auto-Data Peugeot 508 I SW (Phase I) 2.0 HDi 140 FAP	https://www.auto-data.net/en/peugeot-508-i-sw-phase-i-2010-2.0-hdi-140hp-fap-17661
EU-PEUGEOT-508-I-PHASE1-SEDAN-01	4792	1920	1456	Auto-Data Peugeot 508 I (Phase I) 2.0 HDi 140 FAP	https://www.auto-data.net/en/compare?carId1=17652&carId2=&carId3=
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407	Auto-Data Ford Sierra Hatchback II 1.6 (72 Hp)	https://www.auto-data.net/en/ford-sierra-hatchback-ii-1.6-72hp-7572
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407	Auto-Data Ford Sierra Sedan II 1.6 (75 Hp)	https://www.auto-data.net/en/ford-sierra-sedan-ii-1.6-75hp-7557
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300	Auto-Data Mercedes-Benz SL (R107) 280 SL (185 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-280-sl-185hp-42901
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300	Auto-Data Mercedes-Benz SL (R107 facelift 1985) 300 SL (188 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-300-sl-188hp-42865
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307	Auto-Data Mercedes-Benz SL (R107 facelift 1985) 420 SL CAT V8 (204 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-420-sl-cat-v8-204hp-automatic-43215
EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	4315	1768	1459	Auto-Data Seat Leon II (1P, facelift 2009) 1.6 TDI CR 90	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-1.6-tdi-cr-90hp-dpf-46482
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330	Auto-Data Mercedes-Benz SLC (C107)	https://www.auto-data.net/en/mercedes-benz-slc-c107-generation-8623
EU-MERCEDES-BENZ-W123-C123-COUPE-01	4763	1786	1395	Auto-Data Mercedes-Benz C123	https://www.auto-data.net/en/mercedes-benz-c123-generation-2728
EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	4655	1740	1410	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	4655	1740	1394	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
EU-OPEL-ASCONA-C-SEDAN-H1395-01	4366	1668	1395	Auto-Data Opel Ascona C 1.3 N (60 Hp)	https://www.auto-data.net/en/opel-ascona-c-1.3-n-60hp-2025
EU-OPEL-ASCONA-C-SEDAN-H1385-01	4366	1668	1385	Auto-Data Opel Ascona C 1.6 S (90 Hp)	https://www.auto-data.net/en/opel-ascona-c-1.6-s-90hp-2032
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385	Auto-Data Opel Ascona C CC 1.3 N (60 Hp)	https://www.auto-data.net/en/opel-ascona-c-cc-1.3-n-60hp-2040
EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	4655	1740	1391	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
```

## 下一步优先处理

1. 优先一次性闭合 Ford Taunus 80 与 Granada Mk I 的 Sedan／Wagon 外廓、门数分支及三维。
2. 核对 Sierra Cosworth Ktype `751`、`781` 的实际车身形式和特殊外部套件尺寸，并处理 Vectra A CC。
3. 补齐 Suzuki SX4 两条具体配置、Discovery IV 明确不含后视镜宽度，以及 NP300 Pickup 的 CAB／BED 物理分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/peugeot-508-i-sw-phase-i-2010-2.0-hdi-140hp-fap-17661 "Peugeot 508 I SW (Phase I, 2010) 2.0 HDI (140 Hp) FAP | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-w124-model-2893 "Mercedes-Benz W124 | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-500-sl-v8-245hp-automatic-43216 "Mercedes-Benz SL (R107, facelift 1985) 500 SL V8 (245 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/ford-sierra-hatchback-ii-2.0-rs-cosworth-204hp-7588 "Ford Sierra Hatchback II 2.0 RS Cosworth (204 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/land-rover-discovery-iv-2.7-lr-td-v6-190hp-awd-22952 "Land Rover Discovery IV 2.7 LR TD V6 (190 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Ktype `751`、`781` 已确认属于 Sierra Hatchback II；两款 Cosworth 的车身形式及外廓均可直接关联既有 Sierra Hatchback 尺寸组，不新建尺寸组。([汽车数据网][1])
* Ktype `779`、`816` 已分别闭合 SX4 I Sedan 1.6 120 hp 与 SX4 Classic 1.5 VVT 112 hp；后者采用 Suzuki 官方规格中的 `4120 × 1730 × 1565 mm`。([汽车目录][2])
* Discovery IV 两条 Ktype 已取得明确不含后视镜宽度 `1915 mm`，与长度 `4829 mm`、高度 `1887 mm` 闭合为同一尺寸组。([汽车目录][3])
* Vectra A CC facelift 已闭合；NP300 D22 的同一 2.5 dCi 133 hp Ktype 已确认覆盖 Single Cab、King Cab、Double Cab 三种外廓，替换原无后缀 PENDING 行。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射行：96
* PENDING Ktype／映射行：10
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
751	751	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
779	779	Sedan	SX4 I Sedan	RW416	4	EU-SUZUKI-SX4-I-SEDAN-01	HIGH		READY
781	781	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
797	797	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-SUV-01	HIGH		READY
799	799	Hatchback	Vectra A CC facelift 1992		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH		READY
800	800	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-SUV-01	HIGH		READY
803_singlecab	803	Pickup	NP300 Pickup D22	D22	2	EU-NISSAN-NP300-D22-PICKUP-SINGLE-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按Single Cab派生。	READY
803_kingcab	803	Pickup	NP300 Pickup D22	D22	2	EU-NISSAN-NP300-D22-PICKUP-KING-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按King Cab派生。	READY
803_doublecab	803	Pickup	NP300 Pickup D22	D22	4	EU-NISSAN-NP300-D22-PICKUP-DOUBLE-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按Double Cab派生。	READY
816	816	Hatchback	SX4 I facelift 2009	RW415	5	EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-1P5-2WD-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SX4-I-SEDAN-01	4490	1730	1545	Automobile-Catalog 2010 Suzuki SX4 Sedan 1.6 VVT 2WD	https://www.automobile-catalog.com/car/2010/3409070/suzuki_sx4_sedan_1_6_vvt_2wd.html
EU-LAND-ROVER-DISCOVERY-IV-SUV-01	4829	1915	1887	Automobile-Catalog Discovery 4 2.7 TDV6; Automobile-Catalog Discovery 4 3.0 TDV6	https://www.automobile-catalog.com/car/2009/1405895/land_rover_discovery_4_2_7_tdv6_gs.html;https://www.automobile-catalog.com/car/2015/2327405/land_rover_discovery_4_3_0_tdv6.html
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400	Auto-Data Opel Vectra A CC facelift 1992 1.6i	https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-1.6i-75hp-26303
EU-NISSAN-NP300-D22-PICKUP-SINGLE-CAB-01	5020	1825	1700	Auto-Data Nissan NP300 D22 2.5 dCi Single Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-single-cab-900
EU-NISSAN-NP300-D22-PICKUP-KING-CAB-01	5020	1825	1695	Auto-Data Nissan NP300 D22 2.5 dCi King Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-king-cab-898
EU-NISSAN-NP300-D22-PICKUP-DOUBLE-CAB-01	5020	1825	1710	Auto-Data Nissan NP300 D22 2.5 dCi Double Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-pickup-double-cab-899
EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-1P5-2WD-01	4120	1730	1565	Suzuki Motor Poland SX4 Classic official brochure	https://suzuki.pl/old-pdf/auto/katalogi/suzuki_sx4.pdf
```

## 下一步优先处理

优先闭合剩余 10 条：Taunus 80 的 2 门／4 门及标准／运动悬架外廓边界，以及 Granada Mk I Sedan 与 Turnier 的完整三维和门数分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-sierra-hatchback-ii-2.0-rs-cosworth-204hp-7588 "Ford Sierra Hatchback II 2.0 RS Cosworth (204 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2010/3409070/suzuki_sx4_sedan_1_6_vvt_2wd.html?utm_source=chatgpt.com "2010 Suzuki SX4 Sedan 1.6 VVT 2WD Specs Review (88 kW / 120 PS / 118 hp) (up to mid-year 2010 for Europe )"
[3]: https://www.automobile-catalog.com/car/2015/2327405/land_rover_discovery_4_3_0_tdv6.html?utm_source=chatgpt.com "2015 Land Rover Discovery 4 3.0 TDV6 Specs Review (155 kW / 211 PS / 208 hp) (up to end-year 2015 for Europe )"
[4]: https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-1.6i-75hp-26303?utm_source=chatgpt.com "Opel Vectra A CC (facelift 1992) 1.6i (75 Hp)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 6 个 Taunus Ktype 已按 GBTS 两门和 GBFS 四门派生。标准轿车组为 `4340 × 1706 × 1363 mm`；2.3 Ghia 因外廓长度增加，独立使用 `4382 × 1706 × 1363 mm` 尺寸组。([汽车目录][1])
* 剩余 Granada Ktype 已按 GGTL 两门 Sedan、GGFL 四门 Sedan 和 GGNL 五门 Turnier 闭合；Sedan 为 `4572 × 1791 × 1369 mm`，Turnier 为 `4674 × 1791 × 1410 mm`，宽度均采用不含后视镜口径。([汽车信息][2])
* 已完成轻量机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，映射外键全部闭合，尺寸和来源字段均非空。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：115
* PENDING：0
* 最终尺寸组：31
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
727	727	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
728	728	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
729	729	Sedan	Orion II		4	EU-FORD-ORION-II-SEDAN-01	HIGH		READY
730	730	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
731	731	Sedan	508 I Phase I		4	EU-PEUGEOT-508-I-PHASE1-SEDAN-01	HIGH		READY
732	732	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
733	733	Sedan	508 I Phase I		4	EU-PEUGEOT-508-I-PHASE1-SEDAN-01	HIGH		READY
734_2dr	734	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
734_4dr	734	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
735_2dr	735	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
735_4dr	735	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
736_2dr	736	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
736_4dr	736	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
737_2dr	737	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
737_4dr	737	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
738_2dr	738	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
738_4dr	738	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-01	HIGH	Ktype覆盖GBTS两门与GBFS四门轿车，按门数派生。	READY
739_2dr	739	Sedan	Taunus TC3	GBTS	2	EU-FORD-TAUNUS-TC3-SEDAN-2D-2P3-GHIA-01	HIGH	2.3 Ghia外廓较标准轿车更长；Ktype按两门与四门派生。	READY
739_4dr	739	Sedan	Taunus TC3	GBFS	4	EU-FORD-TAUNUS-TC3-SEDAN-4D-2P3-GHIA-01	HIGH	2.3 Ghia外廓较标准轿车更长；Ktype按两门与四门派生。	READY
740	740	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
741	741	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
742	742	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
743	743	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
744	744	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
745	745	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
746	746	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
747	747	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
748	748	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
749	749	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
750	750	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
751	751	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
752	752	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	HIGH		READY
753	753	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	HIGH		READY
754	754	Wagon	508 I Phase I		5	EU-PEUGEOT-508-I-PHASE1-WAGON-01	HIGH		READY
755	755	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
756	756	Hatchback	Leon II facelift 2009	1P	5	EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	HIGH		READY
757	757	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
758	758	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
759	759	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
760	760	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
761	761	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
762	762	Hatchback	Leon II facelift 2009	1P	5	EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	HIGH		READY
763	763	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
764	764	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
765	765	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
766	766	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
767	767	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
768	768	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
769	769	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
770	770	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
771	771	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
772	772	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
773	773	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
774	774	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
775	775	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
776	776	Convertible	SL R107	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	HIGH		READY
777	777	Convertible	SL R107 facelift 1985	R107	2	EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	HIGH		READY
779	779	Sedan	SX4 I Sedan	RW416	4	EU-SUZUKI-SX4-I-SEDAN-01	HIGH		READY
780	780	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
781	781	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
782	782	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
783	783	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
784	784	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
785	785	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-01	HIGH		READY
786	786	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
787	787	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
788	788	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
789	789	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
790_2dr	790	Sedan	Granada Mk I	GGTL	2	EU-FORD-GRANADA-MK1-SEDAN-2D-01	HIGH	Ktype生产期覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
790_4dr	790	Sedan	Granada Mk I	GGFL	4	EU-FORD-GRANADA-MK1-SEDAN-4D-01	HIGH	Ktype生产期覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
791	791	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
792	792	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
793_2dr	793	Sedan	Granada Mk I	GGTL	2	EU-FORD-GRANADA-MK1-SEDAN-2D-01	HIGH	Ktype覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
793_4dr	793	Sedan	Granada Mk I	GGFL	4	EU-FORD-GRANADA-MK1-SEDAN-4D-01	HIGH	Ktype覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
794	794	Coupe	W123 C123	C123	2	EU-MERCEDES-BENZ-W123-C123-COUPE-01	HIGH		READY
796_2dr	796	Sedan	Granada Mk I	GGTL	2	EU-FORD-GRANADA-MK1-SEDAN-2D-01	HIGH	Ktype覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
796_4dr	796	Sedan	Granada Mk I	GGFL	4	EU-FORD-GRANADA-MK1-SEDAN-4D-01	HIGH	Ktype覆盖GGTL两门与GGFL四门轿车，按门数派生。	READY
797	797	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-SUV-01	HIGH		READY
798	798	Wagon	Granada Mk I Turnier	GGNL	5	EU-FORD-GRANADA-MK1-TURNIER-WAGON-01	HIGH		READY
799	799	Hatchback	Vectra A CC facelift 1992		5	EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	HIGH		READY
800	800	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-SUV-01	HIGH		READY
801_prefl	801	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
801_facelift	801	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
802	802	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
803_singlecab	803	Pickup	NP300 Pickup D22	D22	2	EU-NISSAN-NP300-D22-PICKUP-SINGLE-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按Single Cab派生。	READY
803_kingcab	803	Pickup	NP300 Pickup D22	D22	2	EU-NISSAN-NP300-D22-PICKUP-KING-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按King Cab派生。	READY
803_doublecab	803	Pickup	NP300 Pickup D22	D22	4	EU-NISSAN-NP300-D22-PICKUP-DOUBLE-CAB-01	HIGH	Ktype覆盖多种驾驶室外廓，按Double Cab派生。	READY
804_prefl	804	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
804_facelift	804	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
805	805	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
806	806	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
807	807	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
808	808	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
809	809	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
810	810	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
811	811	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
812	812	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
813	813	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
814_prefl	814	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
814_facelift	814	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
815_prefl	815	Coupe	W124 C124	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
815_facelift	815	Coupe	W124 C124 facelift 1989	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH	Ktype跨越1989年C124外廓高度变化，按生产阶段派生。	READY
816	816	Hatchback	SX4 I facelift 2009	RW415	5	EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-1P5-2WD-01	HIGH		READY
817	817	Convertible	W124 A124	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
818	818	Convertible	E-Class A124 facelift 1993	A124	2	EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	HIGH		READY
819	819	Coupe	E-Class C124 facelift 1993	C124	2	EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	HIGH		READY
820	820	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
821	821	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
822	822	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
823	823	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
824	824	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1385-01	HIGH		READY
825	825	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
826	826	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
827	827	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-H1395-01	HIGH		READY
828	828	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_701-800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ORION-II-SEDAN-01	4210	1640	1390	UltimateSpecs Ford Orion II	https://www.ultimatespecs.com/car-specs/Ford/M1192/Orion-II
EU-PEUGEOT-508-I-PHASE1-WAGON-01	4813	1920	1476	Auto-Data Peugeot 508 I SW (Phase I) 2.0 HDi 140 FAP	https://www.auto-data.net/en/peugeot-508-i-sw-phase-i-2010-2.0-hdi-140hp-fap-17661
EU-PEUGEOT-508-I-PHASE1-SEDAN-01	4792	1920	1456	Auto-Data Peugeot 508 I (Phase I) 2.0 HDi 140 FAP	https://www.auto-data.net/en/compare?carId1=17652&carId2=&carId3=
EU-FORD-TAUNUS-TC3-SEDAN-2D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.6	https://www.automobile-catalog.com/car/1980/921965/ford_taunus_1_6.html
EU-FORD-TAUNUS-TC3-SEDAN-4D-01	4340	1706	1363	Automobile-Catalog 1980 Ford Taunus 1.6	https://www.automobile-catalog.com/car/1980/921965/ford_taunus_1_6.html
EU-FORD-TAUNUS-TC3-SEDAN-2D-2P3-GHIA-01	4382	1706	1363	Automobile-Catalog 1981 Ford Taunus 2.3 V6 Ghia	https://www.automobile-catalog.com/car/1981/921905/ford_taunus_2_3_v6_ghia.html
EU-FORD-TAUNUS-TC3-SEDAN-4D-2P3-GHIA-01	4382	1706	1363	Automobile-Catalog 1981 Ford Taunus 2.3 V6 Ghia	https://www.automobile-catalog.com/car/1981/921905/ford_taunus_2_3_v6_ghia.html
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407	Auto-Data Ford Sierra Hatchback II 1.6 (72 Hp)	https://www.auto-data.net/en/ford-sierra-hatchback-ii-1.6-72hp-7572
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407	Auto-Data Ford Sierra Sedan II 1.6 (75 Hp)	https://www.auto-data.net/en/ford-sierra-sedan-ii-1.6-75hp-7557
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300	Auto-Data Mercedes-Benz SL (R107) 280 SL (185 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-280-sl-185hp-42901
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300	Auto-Data Mercedes-Benz SL (R107 facelift 1985) 300 SL (188 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-300-sl-188hp-42865
EU-SEAT-LEON-II-1P-FACELIFT-HATCHBACK-01	4315	1768	1459	Auto-Data Seat Leon II (1P, facelift 2009) 1.6 TDI CR 90	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-1.6-tdi-cr-90hp-dpf-46482
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307	Auto-Data Mercedes-Benz SL (R107 facelift 1985) 420 SL CAT V8 (204 Hp)	https://www.auto-data.net/en/mercedes-benz-sl-r107-facelift-1985-420-sl-cat-v8-204hp-automatic-43215
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330	Auto-Data Mercedes-Benz SLC (C107)	https://www.auto-data.net/en/mercedes-benz-slc-c107-generation-8623
EU-SUZUKI-SX4-I-SEDAN-01	4490	1730	1545	Automobile-Catalog 2010 Suzuki SX4 Sedan 1.6 VVT 2WD	https://www.automobile-catalog.com/car/2010/3409070/suzuki_sx4_sedan_1_6_vvt_2wd.html
EU-MERCEDES-BENZ-W123-C123-COUPE-01	4763	1786	1395	Auto-Data Mercedes-Benz C123	https://www.auto-data.net/en/mercedes-benz-c123-generation-2728
EU-FORD-GRANADA-MK1-SEDAN-2D-01	4572	1791	1369	Car.info Ford Granada 2-door Sedan GGTL; Ford Granada I Sedan specifications	https://www.car.info/en-se/ford/granada/granada-2-door-sedan-mark-i-facelift-304510;https://ford.drive.place/granada/i/group_sedan/78224
EU-FORD-GRANADA-MK1-SEDAN-4D-01	4572	1791	1369	Automobile-Catalog 1975 Ford Granada 2000 GL	https://www.automobile-catalog.com/car/1975/918425/ford_granada_2000_gl.html
EU-LAND-ROVER-DISCOVERY-IV-SUV-01	4829	1915	1887	Automobile-Catalog Discovery 4 2.7 TDV6; Automobile-Catalog Discovery 4 3.0 TDV6	https://www.automobile-catalog.com/car/2009/1405895/land_rover_discovery_4_2_7_tdv6_gs.html;https://www.automobile-catalog.com/car/2015/2327405/land_rover_discovery_4_3_0_tdv6.html
EU-FORD-GRANADA-MK1-TURNIER-WAGON-01	4674	1791	1410	Automobile-Catalog 1974 Ford Granada Turnier 3000; Auto-Data Ford Granada Turnier GGNL 2.0	https://www.automobile-catalog.com/car/1974/914630/ford_granada_turnier_3000.html;https://www.auto-data.net/en/ford-granada-turnier-ggnl-2.0-90hp-7988
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400	Auto-Data Opel Vectra A CC facelift 1992 1.6i	https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-1.6i-75hp-26303
EU-MERCEDES-BENZ-W124-C124-COUPE-PREFL-01	4655	1740	1410	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
EU-MERCEDES-BENZ-W124-C124-COUPE-FACELIFT-01	4655	1740	1394	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
EU-OPEL-ASCONA-C-SEDAN-H1395-01	4366	1668	1395	Auto-Data Opel Ascona C 1.3 N (60 Hp)	https://www.auto-data.net/en/opel-ascona-c-1.3-n-60hp-2025
EU-NISSAN-NP300-D22-PICKUP-SINGLE-CAB-01	5020	1825	1700	Auto-Data Nissan NP300 D22 2.5 dCi Single Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-single-cab-900
EU-NISSAN-NP300-D22-PICKUP-KING-CAB-01	5020	1825	1695	Auto-Data Nissan NP300 D22 2.5 dCi King Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-king-cab-898
EU-NISSAN-NP300-D22-PICKUP-DOUBLE-CAB-01	5020	1825	1710	Auto-Data Nissan NP300 D22 2.5 dCi Double Cab	https://www.auto-data.net/en/nissan-np-300-pick-up-d22-2.5-dci-133hp-pickup-double-cab-899
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385	Auto-Data Opel Ascona C CC 1.3 N (60 Hp)	https://www.auto-data.net/en/opel-ascona-c-cc-1.3-n-60hp-2040
EU-MERCEDES-BENZ-W124-A124-CONVERTIBLE-01	4655	1740	1391	Auto-Data Mercedes-Benz W124 model overview	https://www.auto-data.net/en/mercedes-benz-w124-model-2893
EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-1P5-2WD-01	4120	1730	1565	Suzuki Motor Poland SX4 Classic official brochure	https://suzuki.pl/old-pdf/auto/katalogi/suzuki_sx4.pdf
EU-OPEL-ASCONA-C-SEDAN-H1385-01	4366	1668	1385	Auto-Data Opel Ascona C 1.6 S (90 Hp)	https://www.auto-data.net/en/opel-ascona-c-1.6-s-90hp-2032
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_701-800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1980/921965/ford_taunus_1_6.html "https://www.automobile-catalog.com/car/1980/921965/ford_taunus_1_6.html"
[2]: https://www.car.info/en-se/ford/granada/granada-2-door-sedan-mark-i-facelift-304510 "https://www.car.info/en-se/ford/granada/granada-2-door-sedan-mark-i-facelift-304510"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-FORD-ORION-II-SEDAN-01 的 LengthMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_701-800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_701-800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3967 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1103 行）

- 尺寸冲突协调：
  - EU-FORD-ORION-II-SEDAN-01 -> EU-FORD-ORION-II-SEDAN-02：4213x1640x1389 与 4210x1640x1390，创建新尺寸组
