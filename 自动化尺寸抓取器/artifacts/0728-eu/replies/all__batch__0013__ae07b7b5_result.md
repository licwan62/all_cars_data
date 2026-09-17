# 任务：all 第 1201-1300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0013__ae07b7b5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1201-1300 行

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
all 第 1201-1300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Omega a	2.0 I	Stufenheck	Heckantrieb	Benzin	85	115	Sep 1986	Mar 1994	2024-03-01	1231
Opel	Omega a	2.4 I	Stufenheck	Heckantrieb	Benzin	92	125	Sep 1988	Mar 1994	2024-03-01	1232
Opel	Omega a	2.6 I	Stufenheck	Heckantrieb	Benzin	110	150	Sep 1990	Mar 1994	2024-03-01	1233
Opel	Omega a	3	Stufenheck	Heckantrieb	Benzin	130	177	Mar 1987	Sep 1990	2024-03-01	1234
Opel	Omega a	3.0 24V	Stufenheck	Heckantrieb	Benzin	147	200	Sep 1989	Mar 1994	2024-03-01	1235
Opel	Omega a	3.0 24V	Stufenheck	Heckantrieb	Benzin	150	204	Sep 1989	Mar 1994	2024-03-01	1236
Opel	Omega a caravan	1.8 N	Kombi	Heckantrieb	Benzin	60	82	Sep 1986	Aug 1987	2024-03-01	1237
Opel	Omega a caravan	1.8	Kombi	Heckantrieb	Benzin	65	88	Sep 1987	Mar 1994	2024-03-01	1238
Opel	Omega a caravan	1.8 S	Kombi	Heckantrieb	Benzin	66	90	Sep 1986	Mar 1994	2024-03-01	1239
Opel	Omega a caravan	1.8	Kombi	Heckantrieb	Benzin	85	115	Sep 1986	Mar 1994	2024-03-01	1240
Opel	Omega a caravan	2	Kombi	Heckantrieb	Benzin	90	122	Sep 1986	Mar 1994	2024-03-01	1241
Opel	Omega a caravan	2.3 TD	Kombi	Heckantrieb	Diesel	66	90	Sep 1986	Aug 1988	2024-03-01	1242
Opel	Omega a caravan	2.3 D	Kombi	Heckantrieb	Diesel	54	73	Sep 1986	Mar 1994	2024-03-01	1243
Opel	Omega a caravan	2.3 TD Interc.	Kombi	Heckantrieb	Diesel	74	100	Sep 1988	Mar 1994	2024-03-01	1244
Opel	Omega a caravan	2	Kombi	Heckantrieb	Benzin	74	100	Sep 1990	Mar 1994	2024-03-01	1245
Opel	Omega a caravan	2.0 I	Kombi	Heckantrieb	Benzin	73	99	Sep 1990	Mar 1994	2024-03-01	1246
Opel	Omega a caravan	2.0 I	Kombi	Heckantrieb	Benzin	85	115	Sep 1986	Apr 1994	2024-03-01	1247
Opel	Omega a caravan	2.4 I	Kombi	Heckantrieb	Benzin	92	125	Sep 1988	Mar 1994	2024-03-01	1248
Opel	Omega a caravan	2.6 I	Kombi	Heckantrieb	Benzin	110	150	Sep 1990	Mar 1994	2024-03-01	1249
Opel	Omega a caravan	3.0 CAT	Kombi	Heckantrieb	Benzin	130	177	Mar 1987	Mar 1994	2024-03-01	1250
Opel	Omega a caravan	3.0 24V	Kombi	Heckantrieb	Benzin	147	200	Sep 1989	Mar 1994	2024-03-01	1251
Opel	Senator	2.0 E	Stufenheck	Heckantrieb	Benzin	85	115	Mar 1983	Oct 1984	2024-03-01	1252
Opel	Senator	2.2 E	Stufenheck	Heckantrieb	Benzin	85	115	Nov 1984	Aug 1987	2024-03-01	1253
Opel	Senator	2.5	Stufenheck	Heckantrieb	Benzin	85	115	May 1978	Dec 1980	2024-03-01	1254
Opel	Senator	2.5 E	Stufenheck	Heckantrieb	Benzin	100	136	Jan 1983	Aug 1984	2024-03-01	1255
Opel	Senator	2.5 E	Stufenheck	Heckantrieb	Benzin	103	140	Sep 1984	Aug 1987	2024-03-01	1256
Opel	Senator	2.8	Stufenheck	Heckantrieb	Benzin	103	140	Feb 1978	Apr 1981	2024-03-01	1257
Opel	Senator	3	Stufenheck	Heckantrieb	Benzin	110	150	Apr 1978	Jul 1982	2024-03-01	1258
Opel	Senator	3	Stufenheck	Heckantrieb	Benzin	115	156	Sep 1985	Aug 1987	2024-03-01	1259
Opel	Senator	3.0 E	Stufenheck	Heckantrieb	Benzin	132	180	Feb 1978	Dec 1986	2024-03-01	1260
Opel	Senator	2.2 TD	Stufenheck	Heckantrieb	Diesel	63	86	Nov 1984	Aug 1987	2024-03-01	1261
Opel	Senator	2.6 I	Stufenheck	Heckantrieb	Benzin	110	150	Sep 1990	Sep 1993	2024-03-01	1262
Opel	Senator	3	Stufenheck	Heckantrieb	Benzin	115	156	Sep 1987	Sep 1993	2024-03-01	1263
Opel	Senator	3	Stufenheck	Heckantrieb	Benzin	130	177	Jan 1988	Sep 1990	2024-03-01	1264
Opel	Senator	3.0 24V	Stufenheck	Heckantrieb	Benzin	150	204	Sep 1989	Sep 1993	2024-03-01	1265
Opel	Gt	1.1	Coupe	Heckantrieb	Benzin	44	60	Sep 1968	Dec 1970	2024-03-01	1266
Opel	Gt	1.9	Coupe	Heckantrieb	Benzin	66	90	Sep 1968	Aug 1973	2024-03-01	1267
Opel	Manta a	1.2	Coupe	Heckantrieb	Benzin	44	60	Apr 1972	Aug 1975	2024-03-01	1268
Opel	Manta a	1.6	Coupe	Heckantrieb	Benzin	44	60	Feb 1975	Aug 1975	2024-03-01	1269
Opel	Manta a	1.6	Coupe	Heckantrieb	Benzin	50	68	Sep 1970	Aug 1975	2024-03-01	1270
Opel	Manta a	1.6	Coupe	Heckantrieb	Benzin	55	75	Feb 1975	Aug 1975	2024-03-01	1271
Opel	Manta a	1.6 S	Coupe	Heckantrieb	Benzin	59	80	Sep 1970	Aug 1975	2024-03-01	1272
Opel	Manta a	1.9 S	Coupe	Heckantrieb	Benzin	65	88	Sep 1970	Aug 1975	2024-03-01	1273
Opel	Manta a	1.9 S	Coupe	Heckantrieb	Benzin	66	90	Sep 1970	Aug 1975	2024-03-01	1274
Opel	Manta a	1.9 Gt/e	Coupe	Heckantrieb	Benzin	77	105	Feb 1974	Aug 1975	2024-03-01	1275
Opel	Manta b cc	1.2 S	Coupe	Heckantrieb	Benzin	44	60	Sep 1975	Feb 1979	2024-03-01	1276
Opel	Manta b	1.3 N	Stufenheck	Heckantrieb	Benzin	44	60	Mar 1979	Dec 1980	2024-03-01	1277
Opel	Manta b cc	1.3 N	Coupe	Heckantrieb	Benzin	44	60	Mar 1979	Dec 1980	2024-03-01	1278
Opel	Manta b cc	1.3 S	Coupe	Heckantrieb	Benzin	55	75	Aug 1979	Aug 1986	2024-03-01	1279
Opel	Manta b	1.3 S	Stufenheck	Heckantrieb	Benzin	55	75	Aug 1981	Aug 1986	2024-03-01	1280
Opel	Manta b	1.6 N	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1975	Dec 1980	2024-03-01	1281
Opel	Manta b cc	1.6 N	Coupe	Heckantrieb	Benzin	44	60	Sep 1975	Dec 1980	2024-03-01	1282
Opel	Manta b	1.6 S	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1975	Dec 1981	2024-03-01	1283
Opel	Manta b cc	1.8 S	Coupe	Heckantrieb	Benzin	66	90	Jul 1982	Aug 1987	2024-03-01	1284
Opel	Manta b	1.8 S	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1982	Aug 1987	2024-03-01	1285
Opel	Manta b	1.9 N	Stufenheck	Heckantrieb	Benzin	55	75	Aug 1976	Dec 1981	2024-03-01	1286
Opel	Manta b cc	1.9 N	Coupe	Heckantrieb	Benzin	55	75	Aug 1976	Dec 1981	2024-03-01	1287
Opel	Manta b cc	1.9 S	Coupe	Heckantrieb	Benzin	66	90	Sep 1975	Dec 1980	2024-03-01	1288
Opel	Manta b	1.9 E	Stufenheck	Heckantrieb	Benzin	77	105	Sep 1975	Aug 1977	2024-03-01	1289
Opel	Manta b	2	Stufenheck	Heckantrieb	Benzin	66	90	Aug 1977	Dec 1980	2024-03-01	1290
Opel	Manta b cc	2	Coupe	Heckantrieb	Benzin	66	90	Aug 1977	Dec 1980	2024-03-01	1291
Opel	Manta b cc	2.0 S	Coupe	Heckantrieb	Benzin	74	100	Aug 1977	Aug 1984	2024-03-01	1292
Opel	Manta b	2.0 S	Stufenheck	Heckantrieb	Benzin	74	100	Aug 1977	Aug 1984	2024-03-01	1293
Opel	Manta b cc	2.0 E	Coupe	Heckantrieb	Benzin	81	110	Aug 1977	Aug 1988	2024-03-01	1294
Opel	Manta b	2.0 E	Stufenheck	Heckantrieb	Benzin	81	110	Aug 1977	Aug 1988	2024-03-01	1295
Ford	Mondeo i	1.8 TD	Schrägheck	Frontantrieb	Diesel	65	88	Jun 1993	Aug 1996	2024-03-01	1296
Audi	100	2	Stufenheck	Frontantrieb	Benzin	85	115	Jun 1976	Aug 1978	2024-03-01	1297
Audi	100	2.1	Stufenheck	Frontantrieb	Benzin	85	115	Oct 1977	Jul 1982	2024-03-01	1298
Audi	100	2.1	Stufenheck	Frontantrieb	Benzin	100	136	Mar 1977	Jul 1982	2024-03-01	1299
Ford	Mondeo i	1.8 TD	Stufenheck	Frontantrieb	Diesel	65	88	Jun 1993	Aug 1996	2024-03-01	1300
Alpina	B3	S Bi-turbo Allrad	Kombi	Allrad	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1301
Ford	Mondeo i	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1993	Aug 1996	2024-03-01	1302
Ford	Mondeo i	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1993	Aug 1996	2024-03-01	1303
Ford	Mondeo i	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	85	115	Feb 1993	Aug 1996	2024-03-01	1304
Ford	Mondeo i	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	85	115	Feb 1993	Aug 1996	2024-03-01	1305
Ford	Mondeo i	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	100	136	Feb 1993	Aug 1996	2024-03-01	1306
Ford	Mondeo i	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	100	136	Feb 1993	Aug 1996	2024-03-01	1307
Ford	Escort v	1.8 TD	Schrägheck	Frontantrieb	Diesel	66	90	Feb 1993	Jan 1995	2024-03-01	1308
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	65	88	Feb 1986	Jul 1988	2024-03-01	1309
Audi	100	1.8 CAT	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1985	Nov 1990	2024-03-01	1310
Audi	100	1.9	Stufenheck	Frontantrieb	Benzin	74	100	Aug 1982	Jul 1984	2024-03-01	1311
Audi	100	2	Stufenheck	Frontantrieb	Benzin	83	113	Aug 1986	Nov 1987	2024-03-01	1312
Audi	100	2.0 CAT	Stufenheck	Frontantrieb	Benzin	85	115	Jan 1988	Nov 1990	2024-03-01	1313
Audi	100	2.1	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1982	Jul 1984	2024-03-01	1314
Audi	100	2.2	Stufenheck	Frontantrieb	Benzin	85	115	Oct 1984	Sep 1986	2024-03-01	1315
Audi	100	2.2	Stufenheck	Frontantrieb	Benzin	101	137	Aug 1984	Dec 1988	2024-03-01	1316
Audi	100	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	121	165	Aug 1986	Nov 1990	2024-03-01	1318
Audi	100	2.3 E	Stufenheck	Frontantrieb	Benzin	100	136	Oct 1986	Nov 1990	2024-03-01	1319
Cadillac	Cts	3.6	Kombi	Heckantrieb	Benzin	229	311	Jan 2008	Dec 2011	2024-03-01	1320
Audi	100	2.0 D	Stufenheck	Frontantrieb	Diesel	51	70	Aug 1982	Jul 1988	2024-03-01	1321
Ford	Escort v	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1992	Jan 1995	2024-03-01	1322
Audi	100	2.0 D Turbo	Stufenheck	Frontantrieb	Diesel	64	87	Aug 1982	Jul 1988	2024-05-01	1323
Audi	100	2.0 D Turbo	Stufenheck	Frontantrieb	Diesel	74	100	Mar 1988	Nov 1990	2024-03-01	1324
Audi	100	2.5 TDI	Stufenheck	Frontantrieb	Diesel	88	120	Jan 1990	Nov 1990	2024-03-01	1325
Cadillac	Cts	3.6 AWD	Kombi	Allrad	Benzin	229	311	Jan 2008	Dec 2011	2024-03-01	1326
Audi	100	2.3 E	Stufenheck	Frontantrieb	Benzin	98	133	Jan 1990	Nov 1990	2024-03-01	1327
Alpina	B3	S Bi-turbo	Coupe	Heckantrieb	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1328
Audi	200 c2	2.1 5E	Stufenheck	Frontantrieb	Benzin	100	136	Oct 1979	Sep 1982	2024-03-01	1329
Audi	200 c2	2.1 5T	Stufenheck	Frontantrieb	Benzin	125	170	Oct 1979	Aug 1982	2024-03-01	1330
Audi	100	1.8 Quattro	Stufenheck	Allrad	Benzin	65	88	Aug 1986	Jul 1990	2024-03-01	1331


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Opel Senator A 前期、Senator A 改款、Senator B** 三个尺寸组。Senator A 改款前后长度和宽度不同；Ktype `1260` 覆盖两个物理外廓，已拆为 `1260_prefl` 与 `1260_facelift`。各组宽度来源均明确为不含后视镜。([汽车目录][1])
* 已闭合 **Opel GT 1968–1973** 普通 Coupe 尺寸组，1.1 与 1.9 共用同一外廓。([汽车目录][2])
* 已单独闭合 **Opel Manta A GT/E** 外廓；GT/E 的车身长度和宽度不同于普通基础版，因此暂不与其他 Manta A Ktype 合并。([汽车目录][3])
* Omega A 暂未落盘：资料显示早期与后期车型存在不同外廓数据，需要先按改款边界拆分，避免错误共组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：17
* READY 映射行：18
* PENDING Ktype：83
* 本轮首次闭合尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1252	1252	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1253	1253	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1254	1254	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1255	1255	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1256	1256	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1257	1257	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1258	1258	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1259	1259	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1260_prefl	1260	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH	同一Ktype跨越Senator A改款边界，拆分改款前外廓。	READY
1260_facelift	1260	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越Senator A改款边界，拆分改款后外廓。	READY
1261	1261	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1262	1262	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1263	1263	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1264	1264	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1265	1265	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1266	1266	Coupe	GT		2	EU-OPEL-GT-1968-COUPE-01	HIGH		READY
1267	1267	Coupe	GT		2	EU-OPEL-GT-1968-COUPE-01	HIGH		READY
1275	1275	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-GTE-01	HIGH	GT/E外部造型形成独立物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-SENATOR-A-SEDAN-PREFL-01	4811	1728	1415	Automobile-Catalog 1978 Opel Senator 2.5 S	https://www.automobile-catalog.com/car/1978/2437760/opel_senator_2_5_s.html
EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	4839	1722	1415	Automobile-Catalog 1983 Opel Senator 2.0 E	https://www.automobile-catalog.com/car/1983/48830/opel_senator_2_0_e.html
EU-OPEL-SENATOR-B-SEDAN-01	4845	1743	1450	Automobile-Catalog 1991 Opel Senator 2.6i	https://www.automobile-catalog.com/car/1991/2470160/opel_senator_2_6i.html
EU-OPEL-GT-1968-COUPE-01	4113	1580	1225	Automobile-Catalog 1969 Opel GT 1900	https://www.automobile-catalog.com/car/1969/2416685/opel_rallye_kadett_ls_1900_s.html
EU-OPEL-MANTA-A-COUPE-GTE-01	4343	1632	1360	Automobile-Catalog 1974 Opel Manta GT/E	https://www.automobile-catalog.com/car/1974/2421395/opel_manta_gte.html
```

## 下一步优先处理

1. 按改款前后聚类 Omega A Sedan 与 Caravan，识别跨越改款边界、需要派生拆行的 Ktype。
2. 核对 Manta A 普通版、L/Berlinetta 与 GT/E 的外廓边界，避免仅按发动机错误合并。
3. 批量闭合 Manta B notchback、Manta B CC hatchback 及其改款分支。
4. 随后处理 Mondeo I、Audi 100 C2/C3、Audi 200 C2、Escort V、Alpina B3 和 Cadillac CTS Wagon。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/2437760/opel_senator_2_5_s.html?utm_source=chatgpt.com "1978 Opel Senator 2.5 S Specs Review (84.5 kW / 115 PS / 113 hp) (since mid-year 1978 for Europe export)"
[2]: https://www.automobile-catalog.com/car/1969/2416670/opel_rallye_kadett_ls_1100_sr.html?utm_source=chatgpt.com "1969 Opel GT 1100 Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1974/2421395/opel_manta_gte.html?utm_source=chatgpt.com "1974 Opel Manta GT/E Specs Review (77 kW / 105 PS / 103 hp) (since March 1974 for Europe )"
[4]: https://www.automobile-catalog.com/car/1987/55745/opel_omega_2_0i_gl.html?utm_source=chatgpt.com "1987 Opel Omega GL 2.0i (man. 5) (model for Europe ) car ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1) 更新点

* 已闭合 **Opel Omega A phase I / phase II** 的标准 Sedan、Omega 3000 Sedan、标准 Caravan 和 3.0/24V Caravan 外廓，共新增 7 个尺寸组；宽度均明确为不含后视镜。([汽车目录][1])
* 已批量完成 Ktype `1231–1251` 的尺寸组关联。
* 跨越 1990 年 Omega A 改款且外廓发生变化的 Ktype 已拆为 `prefl`、`facelift` 派生行。
* Omega 3000 Sedan 与普通 Sedan、3.0/24V Caravan 与早期普通 Caravan 未错误共组。

## 2) 当前批次进度

* 输入 Ktype：100
* READY Ktype：38
* READY 映射行：53
* PENDING Ktype：62
* 已确认尺寸组：12
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1231_prefl	1231	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	HIGH	跨越Omega A改款边界，拆分改款前外廓。	READY
1231_facelift	1231	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH	跨越Omega A改款边界，拆分改款后外廓。	READY
1232_prefl	1232	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	HIGH	跨越Omega A改款边界，拆分改款前外廓。	READY
1232_facelift	1232	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH	跨越Omega A改款边界，拆分改款后外廓。	READY
1233	1233	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH		READY
1234	1234	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	Omega 3000外部造型。	READY
1235_prefl	1235	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	跨越Omega 3000改款边界，拆分改款前外廓。	READY
1235_facelift	1235	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	HIGH	跨越Omega 3000改款边界，拆分改款后外廓。	READY
1236_prefl	1236	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	跨越Omega 3000改款边界，拆分改款前外廓。	READY
1236_facelift	1236	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	HIGH	跨越Omega 3000改款边界，拆分改款后外廓。	READY
1237	1237	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH		READY
1238_prefl	1238	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1238_facelift	1238	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1239_prefl	1239	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1239_facelift	1239	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1240_prefl	1240	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1240_facelift	1240	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1241_prefl	1241	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1241_facelift	1241	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1242	1242	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH		READY
1243_prefl	1243	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1243_facelift	1243	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1244_prefl	1244	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1244_facelift	1244	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1245	1245	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1246	1246	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1247_prefl	1247	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1247_facelift	1247	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1248_prefl	1248	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1248_facelift	1248	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1249	1249	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1250_prefl	1250	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界；早期3.0外廓。	READY
1250_facelift	1250	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1251_prefl	1251	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界；早期24V外廓。	READY
1251_facelift	1251	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	4687	1772	1447	Automobile-Catalog 1987 Opel Omega GL 2.0i	https://www.automobile-catalog.com/car/1987/55745/opel_omega_2_0i_gl.html
EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	4738	1760	1445	Automobile-Catalog 1991 Opel Omega GL 2.0i	https://www.automobile-catalog.com/car/1991/2467835/opel_omega_2_0i_gl.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	4742	1772	1422	Automobile-Catalog 1989 Opel Omega 3000 24V	https://www.automobile-catalog.com/car/1989/64460/opel_omega_3000_24v_cat.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	4742	1772	1425	Automobile-Catalog 1991 Opel Omega 3000 24V automatic	https://www.automobile-catalog.com/car/1991/2468180/opel_omega_3000_24v_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	4730	1772	1481	Automobile-Catalog 1987 Opel Omega Caravan GL 2.0i	https://www.automobile-catalog.com/car/1987/57560/opel_omega_caravan_2_0i_gl.html
EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	4768	1760	1530	Automobile-Catalog 1991 Opel Omega Caravan 3.0i automatic	https://www.automobile-catalog.com/car/1991/2468240/opel_omega_caravan_3_0i_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	4730	1772	1530	Automobile-Catalog 1990 Opel Omega Caravan Sportive 3.0i automatic catalyst	https://www.automobile-catalog.com/car/1990/2469695/opel_omega_caravan_sportive_3_0i_automatic_cat.html
```

## 5) 下一步优先处理

1. 闭合 Manta A 普通车身、Luxus/Berlinetta 与 GT/E 的外廓边界。
2. 按 notchback 与 CC 三门车身分别聚类 Manta B，并处理 1982 年外观改款。
3. 随后批量处理 Mondeo I Sedan/Hatchback、Audi 100 C2/C3 与 Audi 200 C2。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1987/55745/opel_omega_2_0i_gl.html?utm_source=chatgpt.com "1987 Opel Omega GL 2.0i (man. 5) (model for Europe ) car ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1) 更新点

* 已确认 Manta A 普通车身与 L/SR 长保险杠外廓尺寸不同，Ktype `1268–1274` 均拆分为 `base` 与 `l_sr` 两个稳定分支。([汽车目录][1])
* 已闭合 Manta B 的改款前后 notchback、CC 三门以及 GT/E 低车身外廓。1982 年改款前后长宽发生变化；notchback GT/E 高度也与普通版本不同。([汽车目录][2])
* Ktype `1294`、`1295` 的 2.0 E 覆盖普通版与 GT/E/GSi 外廓，已按车身形式、改款阶段和运动型低车身完整派生。CC 改款前 GT/E 与普通版三维一致，因此复用同一尺寸组。([汽车目录][3])

## 2) 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* READY 映射行：96
* PENDING Ktype：35
* 已确认尺寸组：21
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1268_base	1268	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1268_l_sr	1268	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1269_base	1269	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1269_l_sr	1269	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1270_base	1270	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1270_l_sr	1270	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1271_base	1271	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1271_l_sr	1271	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1272_base	1272	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1272_l_sr	1272	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1273_base	1273	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1273_l_sr	1273	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1274_base	1274	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1274_l_sr	1274	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1276	1276	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1277	1277	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1278	1278	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1279_prefl	1279	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	跨越1982改款边界；改款前三门外廓。	READY
1279_facelift	1279	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后三门外廓。	READY
1280_prefl	1280	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	跨越1982改款边界；改款前notchback外廓。	READY
1280_facelift	1280	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后notchback外廓。	READY
1281	1281	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1282	1282	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1283	1283	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1284	1284	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	CC三门改款后外廓。	READY
1285	1285	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	二门notchback改款后外廓。	READY
1286	1286	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1287	1287	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1288	1288	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1289	1289	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	HIGH	1.9E对应GT/E低车身外廓。	READY
1290	1290	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1291	1291	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1292_prefl	1292	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	跨越1982改款边界；改款前三门外廓。	READY
1292_facelift	1292	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后三门外廓。	READY
1293_prefl	1293	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	跨越1982改款边界；改款前notchback外廓。	READY
1293_facelift	1293	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后notchback外廓。	READY
1294_prefl	1294	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	MEDIUM	改款前CC普通版与GT/E三维一致。	READY
1294_facelift_standard	1294	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	MEDIUM	改款后标准高度CC外廓。	READY
1294_facelift_gte	1294	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-GTE-01	MEDIUM	改款后GT/E或GSi低车身CC外廓。	READY
1295_prefl_standard	1295	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	MEDIUM	改款前标准高度notchback外廓。	READY
1295_prefl_gte	1295	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	MEDIUM	改款前GT/E低车身notchback外廓。	READY
1295_facelift_standard	1295	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	MEDIUM	改款后标准高度notchback外廓。	READY
1295_facelift_gte	1295	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-GTE-01	MEDIUM	改款后GT/E或GSi低车身notchback外廓。	READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MANTA-A-COUPE-BASE-01	4292	1626	1360	Automobile-Catalog 1970 Opel Manta 16	https://www.automobile-catalog.com/car/1970/2420960/opel_manta_16.html
EU-OPEL-MANTA-A-COUPE-L-SR-01	4343	1632	1360	Automobile-Catalog 1970 Opel Manta L 16	https://www.automobile-catalog.com/car/1970/2420810/opel_manta_l_16.html
EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	4445	1670	1330	Automobile-Catalog 1979 Opel Manta 2.0 S	https://www.automobile-catalog.com/car/1979/2427095/opel_manta_2_0_s.html
EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	4445	1670	1325	Automobile-Catalog 1977 Opel Manta GT/E	https://www.automobile-catalog.com/car/1977/2427185/opel_manta_gte.html
EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	4443	1686	1330	Automobile-Catalog 1983 Opel Manta GT/J 1.8 S 5-speed	https://www.automobile-catalog.com/car/1983/2430230/opel_manta_gtj_1_8_s_5-speed.html
EU-OPEL-MANTA-B-SEDAN-FACELIFT-GTE-01	4443	1686	1310	Automobile-Catalog 1982 Opel Manta GT/E	https://www.automobile-catalog.com/car/1982/2429990/opel_manta_gte.html
EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	4376	1670	1340	Automobile-Catalog 1980 Opel Manta CC 1.9 N	https://www.automobile-catalog.com/car/1980/2429135/opel_manta_cc_1_9_n.html
EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	4384	1686	1340	Automobile-Catalog 1982 Opel Manta CC Berlinetta 2.0 S 5-speed	https://www.automobile-catalog.com/car/1982/2429765/opel_manta_cc_berlinetta_2_0_s_5-speed.html
EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-GTE-01	4384	1686	1320	Automobile-Catalog 1982 Opel Manta CC GT/E	https://www.automobile-catalog.com/car/1982/2430050/opel_manta_cc_gte.html
```

## 5) 下一步优先处理

1. 批量闭合 Ford Mondeo I Hatchback 与 Sedan，并复用相同发动机下的车身组。
2. 处理 Audi 100 C2、Audi 200 C2 与 Audi 100 C3，优先识别跨代同名车型。
3. 随后完成 Escort V、Alpina B3、Cadillac CTS Wagon 等剩余低数量车型组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1970/2420960/opel_manta_16.html?utm_source=chatgpt.com "1970 Opel Manta 16 Specs Review (50 kW / 68 PS / 67 hp) (since September 1970 for Europe )"
[2]: https://www.automobile-catalog.com/car/1979/2427095/opel_manta_2_0_s.html?utm_source=chatgpt.com "1979 Opel Manta 2.0 S Specs Review (73.5 kW / 100 PS / 99 hp) (up to August 1979 for Europe )"
[3]: https://www.automobile-catalog.com/car/1980/2429435/opel_manta_cc_gte.html?utm_source=chatgpt.com "1980 Opel Manta CC GT/E Specs Review (81 kW / 110 PS / 109 hp) (for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* 已闭合 Ford Mondeo I Hatchback、Sedan 两个尺寸组，并批量完成 Ktype `1296`、`1300`、`1302–1307` 的关联。([汽车目录档案][1])
* 已按三门、五门物理车身拆分 Ford Escort V Hatchback，完成 Ktype `1308`、`1322` 的派生映射。([汽车目录档案][2])
* 已分别闭合 Audi 100 C2、Audi 100 C3、Audi 200 C2 Sedan；Audi 100 C3 前驱和 Quattro 在本批确认的外部三维一致，复用同一尺寸组。([汽车目录档案][3])
* 已闭合 Cadillac CTS II Sport Wagon 尺寸组，RWD 与 AWD 共用该组。
* 剩余 PENDING 仅为 Alpina B3 S Bi-Turbo Touring Allrad 与 Coupe 两种物理车身。

## 2) 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：131
* PENDING Ktype：2
* 已确认尺寸组：29
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1296	1296	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1297	1297	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1298	1298	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1299	1299	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1300	1300	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1302	1302	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1303	1303	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1304	1304	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1305	1305	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1306	1306	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1307	1307	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1308_3dr	1308	Hatchback	Escort V facelift 1992	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分三门与五门；三门物理车身。	READY
1308_5dr	1308	Hatchback	Escort V facelift 1992	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分三门与五门；五门物理车身。	READY
1309	1309	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1310	1310	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1311	1311	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1312	1312	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1313	1313	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1314	1314	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1315	1315	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1316	1316	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1318	1318	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1319	1319	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1320	1320	Wagon	CTS II		5	EU-CADILLAC-CTS-II-SPORT-WAGON-01	HIGH		READY
1321	1321	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1322_3dr	1322	Hatchback	Escort V facelift 1992	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分三门与五门；三门物理车身。	READY
1322_5dr	1322	Hatchback	Escort V facelift 1992	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分三门与五门；五门物理车身。	READY
1323	1323	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1324	1324	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1325	1325	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1326	1326	Wagon	CTS II		5	EU-CADILLAC-CTS-II-SPORT-WAGON-01	HIGH		READY
1327	1327	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1329	1329	Sedan	Audi 200 C2	43	4	EU-AUDI-200-C2-SEDAN-01	HIGH		READY
1330	1330	Sedan	Audi 200 C2	43	4	EU-AUDI-200-C2-SEDAN-01	HIGH		READY
1331	1331	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
```

## 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424	Ford Mondeo 1995 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1995-UK-.pdf
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390	Audi 100 1978 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/11/Audi-100-1978-UK.pdf
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424	Ford Mondeo 1995 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1995-UK-.pdf
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	4104	1696	1397	Ford Range 1992 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/04/Ford-Range-1992-UK.pdf
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	4104	1696	1397	Ford Range 1992 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/04/Ford-Range-1992-UK.pdf
EU-AUDI-100-C3-SEDAN-01	4793	1814	1421	Audi AG product history – Audi 100 TDI C3	https://www.audi.com/en/ascent-to-the-premium-segment-17326
EU-CADILLAC-CTS-II-SPORT-WAGON-01	4878	1842	1463	Cadillac CTS Range 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Cadillac-CTS-UK.pdf
EU-AUDI-200-C2-SEDAN-01	4695	1768	1390	Automobile-Catalog 1980 Audi 200 5T	https://www.automobile-catalog.com/car/1980/167885/audi_200_5t_automatic.html
```

## 5) 下一步优先处理

1. 闭合 Alpina B3 S Bi-Turbo E91 Touring Allrad 尺寸组并关联 Ktype `1301`。
2. 闭合 Alpina B3 S Bi-Turbo E92 Coupe 尺寸组并关联 Ktype `1328`。
3. PENDING 清零后立即进行一次机械收尾，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1995-UK-.pdf?utm_source=chatgpt.com "The Ford Mondeo featuring the new Si and Ghia 4x4 models"
[2]: https://autocatalogarchive.com/wp-content/uploads/2024/04/Ford-Range-1992-UK.pdf?utm_source=chatgpt.com "escort"
[3]: https://autocatalogarchive.com/wp-content/uploads/2016/11/Audi-100-1978-UK.pdf?utm_source=chatgpt.com "Audi 100 (1978) UK"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1) 更新点

* 已闭合最后两个 Alpina 尺寸组。
* `1301` 对应 E91 Touring Allrad：`4541 × 1817 × 1465 mm`。
* `1328` 输入为后驱 Coupe，因此采用 E92 后驱外廓 `4623 × 1782 × 1395 mm`；修正了处理中曾临时报出的 Allrad 高度数据。([汽车目录][1])
* 已完成固定表头、唯一主键、Ktype 覆盖、外键闭合、尺寸正整数、来源非空及孤立尺寸组检查。

## 2) 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：133
* PENDING Ktype：0
* DIMENSION_GROUP：31
* 映射缺失尺寸组：0
* 孤立尺寸组：0
* 当前批次已完成。

## 3) 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1231_prefl	1231	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	HIGH	跨越Omega A改款边界，拆分改款前外廓。	READY
1231_facelift	1231	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH	跨越Omega A改款边界，拆分改款后外廓。	READY
1232_prefl	1232	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	HIGH	跨越Omega A改款边界，拆分改款前外廓。	READY
1232_facelift	1232	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH	跨越Omega A改款边界，拆分改款后外廓。	READY
1233	1233	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	HIGH		READY
1234	1234	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	Omega 3000外部造型。	READY
1235_prefl	1235	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	跨越Omega 3000改款边界，拆分改款前外廓。	READY
1235_facelift	1235	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	HIGH	跨越Omega 3000改款边界，拆分改款后外廓。	READY
1236_prefl	1236	Sedan	Omega A phase I		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	HIGH	跨越Omega 3000改款边界，拆分改款前外廓。	READY
1236_facelift	1236	Sedan	Omega A phase II		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	HIGH	跨越Omega 3000改款边界，拆分改款后外廓。	READY
1237	1237	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH		READY
1238_prefl	1238	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1238_facelift	1238	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1239_prefl	1239	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1239_facelift	1239	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1240_prefl	1240	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1240_facelift	1240	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1241_prefl	1241	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1241_facelift	1241	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1242	1242	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH		READY
1243_prefl	1243	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1243_facelift	1243	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1244_prefl	1244	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1244_facelift	1244	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1245	1245	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1246	1246	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1247_prefl	1247	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1247_facelift	1247	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1248_prefl	1248	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界，拆分改款前外廓。	READY
1248_facelift	1248	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1249	1249	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH		READY
1250_prefl	1250	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界；早期3.0外廓。	READY
1250_facelift	1250	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1251_prefl	1251	Wagon	Omega A phase I		5	EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	HIGH	跨越Omega A Caravan改款边界；早期24V外廓。	READY
1251_facelift	1251	Wagon	Omega A phase II		5	EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	HIGH	跨越Omega A Caravan改款边界，拆分改款后外廓。	READY
1252	1252	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1253	1253	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1254	1254	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1255	1255	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1256	1256	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1257	1257	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1258	1258	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH		READY
1259	1259	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1260_prefl	1260	Sedan	Senator A		4	EU-OPEL-SENATOR-A-SEDAN-PREFL-01	HIGH	同一Ktype跨越Senator A改款边界，拆分改款前外廓。	READY
1260_facelift	1260	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH	同一Ktype跨越Senator A改款边界，拆分改款后外廓。	READY
1261	1261	Sedan	Senator A (facelift 1982)		4	EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	HIGH		READY
1262	1262	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1263	1263	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1264	1264	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1265	1265	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
1266	1266	Coupe	GT		2	EU-OPEL-GT-1968-COUPE-01	HIGH		READY
1267	1267	Coupe	GT		2	EU-OPEL-GT-1968-COUPE-01	HIGH		READY
1268_base	1268	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1268_l_sr	1268	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1269_base	1269	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1269_l_sr	1269	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1270_base	1270	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1270_l_sr	1270	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1271_base	1271	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1271_l_sr	1271	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1272_base	1272	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1272_l_sr	1272	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1273_base	1273	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1273_l_sr	1273	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1274_base	1274	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-BASE-01	MEDIUM	输入未区分装饰级；普通短保险杠外廓。	READY
1274_l_sr	1274	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-L-SR-01	MEDIUM	输入未区分装饰级；L/SR长保险杠外廓。	READY
1275	1275	Coupe	Manta A		2	EU-OPEL-MANTA-A-COUPE-GTE-01	HIGH	GT/E外部造型形成独立物理外廓。	READY
1276	1276	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1277	1277	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1278	1278	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1279_prefl	1279	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	跨越1982改款边界；改款前三门外廓。	READY
1279_facelift	1279	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后三门外廓。	READY
1280_prefl	1280	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	跨越1982改款边界；改款前notchback外廓。	READY
1280_facelift	1280	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后notchback外廓。	READY
1281	1281	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1282	1282	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1283	1283	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1284	1284	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	CC三门改款后外廓。	READY
1285	1285	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	二门notchback改款后外廓。	READY
1286	1286	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1287	1287	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1288	1288	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1289	1289	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	HIGH	1.9E对应GT/E低车身外廓。	READY
1290	1290	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	二门notchback外廓。	READY
1291	1291	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	CC三门外廓。	READY
1292_prefl	1292	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	HIGH	跨越1982改款边界；改款前三门外廓。	READY
1292_facelift	1292	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后三门外廓。	READY
1293_prefl	1293	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	HIGH	跨越1982改款边界；改款前notchback外廓。	READY
1293_facelift	1293	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	HIGH	跨越1982改款边界；改款后notchback外廓。	READY
1294_prefl	1294	Coupe	Manta B phase I		3	EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	MEDIUM	改款前CC普通版与GT/E三维一致。	READY
1294_facelift_standard	1294	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	MEDIUM	改款后标准高度CC外廓。	READY
1294_facelift_gte	1294	Coupe	Manta B facelift 1982		3	EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-GTE-01	MEDIUM	改款后GT/E或GSi低车身CC外廓。	READY
1295_prefl_standard	1295	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	MEDIUM	改款前标准高度notchback外廓。	READY
1295_prefl_gte	1295	Sedan	Manta B phase I		2	EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	MEDIUM	改款前GT/E低车身notchback外廓。	READY
1295_facelift_standard	1295	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	MEDIUM	改款后标准高度notchback外廓。	READY
1295_facelift_gte	1295	Sedan	Manta B facelift 1982		2	EU-OPEL-MANTA-B-SEDAN-FACELIFT-GTE-01	MEDIUM	改款后GT/E或GSi低车身notchback外廓。	READY
1296	1296	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1297	1297	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1298	1298	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1299	1299	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-SEDAN-01	HIGH		READY
1300	1300	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1301	1301	Wagon	B3 S Bi-Turbo (E91)	E91	5	EU-ALPINA-B3-S-BITURBO-E91-TOURING-ALLRAD-01	HIGH	Touring Allrad物理外廓。	READY
1302	1302	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1303	1303	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1304	1304	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1305	1305	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1306	1306	Hatchback	Mondeo I		5	EU-FORD-MONDEO-I-HATCHBACK-01	HIGH		READY
1307	1307	Sedan	Mondeo I		4	EU-FORD-MONDEO-I-SEDAN-01	HIGH		READY
1308_3dr	1308	Hatchback	Escort V facelift 1992	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分三门与五门；三门物理车身。	READY
1308_5dr	1308	Hatchback	Escort V facelift 1992	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分三门与五门；五门物理车身。	READY
1309	1309	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1310	1310	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1311	1311	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1312	1312	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1313	1313	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1314	1314	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1315	1315	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1316	1316	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1318	1318	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1319	1319	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1320	1320	Wagon	CTS II		5	EU-CADILLAC-CTS-II-SPORT-WAGON-01	HIGH		READY
1321	1321	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1322_3dr	1322	Hatchback	Escort V facelift 1992	GAL	3	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分三门与五门；三门物理车身。	READY
1322_5dr	1322	Hatchback	Escort V facelift 1992	GAL	5	EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分三门与五门；五门物理车身。	READY
1323	1323	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1324	1324	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1325	1325	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1326	1326	Wagon	CTS II		5	EU-CADILLAC-CTS-II-SPORT-WAGON-01	HIGH		READY
1327	1327	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
1328	1328	Coupe	B3 S Bi-Turbo (E92)	E92	2	EU-ALPINA-B3-S-BITURBO-E92-COUPE-01	HIGH	Coupe物理外廓。	READY
1329	1329	Sedan	Audi 200 C2	43	4	EU-AUDI-200-C2-SEDAN-01	HIGH		READY
1330	1330	Sedan	Audi 200 C2	43	4	EU-AUDI-200-C2-SEDAN-01	HIGH		READY
1331	1331	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1201-1300_ktype_dimension_mapping_final.tsv)

## 4) 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	4687	1772	1447	Automobile-Catalog 1987 Opel Omega GL 2.0i	https://www.automobile-catalog.com/car/1987/55745/opel_omega_2_0i_gl.html
EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	4738	1760	1445	Automobile-Catalog 1991 Opel Omega GL 2.0i	https://www.automobile-catalog.com/car/1991/2467835/opel_omega_2_0i_gl.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	4742	1772	1422	Automobile-Catalog 1989 Opel Omega 3000 24V	https://www.automobile-catalog.com/car/1989/64460/opel_omega_3000_24v_cat.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	4742	1772	1425	Automobile-Catalog 1991 Opel Omega 3000 24V automatic	https://www.automobile-catalog.com/car/1991/2468180/opel_omega_3000_24v_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	4730	1772	1481	Automobile-Catalog 1987 Opel Omega Caravan GL 2.0i	https://www.automobile-catalog.com/car/1987/57560/opel_omega_caravan_2_0i_gl.html
EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	4768	1760	1530	Automobile-Catalog 1991 Opel Omega Caravan 3.0i automatic	https://www.automobile-catalog.com/car/1991/2468240/opel_omega_caravan_3_0i_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	4730	1772	1530	Automobile-Catalog 1990 Opel Omega Caravan Sportive 3.0i automatic catalyst	https://www.automobile-catalog.com/car/1990/2469695/opel_omega_caravan_sportive_3_0i_automatic_cat.html
EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	4839	1722	1415	Automobile-Catalog 1983 Opel Senator 2.0 E	https://www.automobile-catalog.com/car/1983/48830/opel_senator_2_0_e.html
EU-OPEL-SENATOR-A-SEDAN-PREFL-01	4811	1728	1415	Automobile-Catalog 1978 Opel Senator 2.5 S	https://www.automobile-catalog.com/car/1978/2437760/opel_senator_2_5_s.html
EU-OPEL-SENATOR-B-SEDAN-01	4845	1743	1450	Automobile-Catalog 1991 Opel Senator 2.6i	https://www.automobile-catalog.com/car/1991/2470160/opel_senator_2_6i.html
EU-OPEL-GT-1968-COUPE-01	4113	1580	1225	Automobile-Catalog 1969 Opel GT 1900	https://www.automobile-catalog.com/car/1969/2416685/opel_rallye_kadett_ls_1900_s.html
EU-OPEL-MANTA-A-COUPE-BASE-01	4292	1626	1360	Automobile-Catalog 1970 Opel Manta 16	https://www.automobile-catalog.com/car/1970/2420960/opel_manta_16.html
EU-OPEL-MANTA-A-COUPE-L-SR-01	4343	1632	1360	Automobile-Catalog 1970 Opel Manta L 16	https://www.automobile-catalog.com/car/1970/2420810/opel_manta_l_16.html
EU-OPEL-MANTA-A-COUPE-GTE-01	4343	1632	1360	Automobile-Catalog 1974 Opel Manta GT/E	https://www.automobile-catalog.com/car/1974/2421395/opel_manta_gte.html
EU-OPEL-MANTA-B-CC-COUPE-PREFL-STD-01	4376	1670	1340	Automobile-Catalog 1980 Opel Manta CC 1.9 N	https://www.automobile-catalog.com/car/1980/2429135/opel_manta_cc_1_9_n.html
EU-OPEL-MANTA-B-SEDAN-PREFL-STD-01	4445	1670	1330	Automobile-Catalog 1979 Opel Manta 2.0 S	https://www.automobile-catalog.com/car/1979/2427095/opel_manta_2_0_s.html
EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-STD-01	4384	1686	1340	Automobile-Catalog 1982 Opel Manta CC Berlinetta 2.0 S 5-speed	https://www.automobile-catalog.com/car/1982/2429765/opel_manta_cc_berlinetta_2_0_s_5-speed.html
EU-OPEL-MANTA-B-SEDAN-FACELIFT-STD-01	4443	1686	1330	Automobile-Catalog 1983 Opel Manta GT/J 1.8 S 5-speed	https://www.automobile-catalog.com/car/1983/2430230/opel_manta_gtj_1_8_s_5-speed.html
EU-OPEL-MANTA-B-SEDAN-PREFL-GTE-01	4445	1670	1325	Automobile-Catalog 1977 Opel Manta GT/E	https://www.automobile-catalog.com/car/1977/2427185/opel_manta_gte.html
EU-OPEL-MANTA-B-CC-COUPE-FACELIFT-GTE-01	4384	1686	1320	Automobile-Catalog 1982 Opel Manta CC GT/E	https://www.automobile-catalog.com/car/1982/2430050/opel_manta_cc_gte.html
EU-OPEL-MANTA-B-SEDAN-FACELIFT-GTE-01	4443	1686	1310	Automobile-Catalog 1982 Opel Manta GT/E	https://www.automobile-catalog.com/car/1982/2429990/opel_manta_gte.html
EU-FORD-MONDEO-I-HATCHBACK-01	4481	1747	1424	Ford Mondeo 1995 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1995-UK-.pdf
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390	Audi 100 1978 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/11/Audi-100-1978-UK.pdf
EU-FORD-MONDEO-I-SEDAN-01	4481	1747	1424	Ford Mondeo 1995 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1995-UK-.pdf
EU-ALPINA-B3-S-BITURBO-E91-TOURING-ALLRAD-01	4541	1817	1465	Automobile-Catalog 2010 Alpina B3 S Biturbo Touring Allrad	https://www.automobile-catalog.com/car/2010/1339685/alpina_b3_s_biturbo_touring_allrad.html
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-3D-01	4104	1696	1397	Ford Range 1992 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/04/Ford-Range-1992-UK.pdf
EU-FORD-ESCORT-V-FACELIFT-HATCHBACK-5D-01	4104	1696	1397	Ford Range 1992 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2024/04/Ford-Range-1992-UK.pdf
EU-AUDI-100-C3-SEDAN-01	4793	1814	1421	Audi AG product history – Audi 100 TDI C3	https://www.audi.com/en/ascent-to-the-premium-segment-17326
EU-CADILLAC-CTS-II-SPORT-WAGON-01	4878	1842	1463	Cadillac CTS Range 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Cadillac-CTS-UK.pdf
EU-ALPINA-B3-S-BITURBO-E92-COUPE-01	4623	1782	1395	Automobile-Catalog 2011 Alpina B3 S Biturbo Coupe	https://www.automobile-catalog.com/car/2011/1339700/alpina_b3_s_biturbo_coupe.html
EU-AUDI-200-C2-SEDAN-01	4695	1768	1390	Automobile-Catalog 1980 Audi 200 5T	https://www.automobile-catalog.com/car/1980/167885/audi_200_5t_automatic.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1201-1300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2010/1339685/alpina_b3_s_biturbo_touring_allrad.html?utm_source=chatgpt.com "2010 Alpina B3 S Biturbo Touring Allrad Specs Review (294 kW / 400 PS / 394 hp) (since mid-year 2010 for Europe )"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-AUDI-100-C3-SEDAN-01 的 HeightMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1201-1300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1201-1300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4100 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1134 行）

- 尺寸冲突协调：
  - EU-AUDI-100-C3-SEDAN-01 -> EU-AUDI-100-C3-SEDAN-02：4793x1814x1422 与 4793x1814x1421，创建新尺寸组
