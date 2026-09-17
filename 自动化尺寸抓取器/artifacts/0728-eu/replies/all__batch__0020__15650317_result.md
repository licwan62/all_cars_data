# 任务：all 第 1901-2000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0020__15650317


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Passat b2 variant	1.6 TD	Kombi	Frontantrieb	Diesel	51	70	Apr 1982	Mar 1988	2024-03-01	1936
VW	Passat b1 variant	1.3	Kombi	Frontantrieb	Benzin	40	55	May 1973	Jul 1980	2024-03-01	1937
VW	Passat b1 variant	1.5	Kombi	Frontantrieb	Benzin	55	75	Oct 1973	Aug 1975	2024-03-01	1938
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	55	75	Feb 1976	Jul 1980	2024-03-01	1939
Fiat	Grande punto	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Sep 2010	-	2024-03-01	1940
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	63	85	Aug 1975	Jul 1980	2024-03-01	1941
VW	Passat b1 variant	1.5 D	Kombi	Frontantrieb	Diesel	37	50	Feb 1977	Jul 1980	2024-03-01	1942
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	53	72	Apr 1986	Feb 1990	2024-03-01	1943
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	55	75	Aug 1983	Apr 1992	2024-03-01	1944
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	81	110	Aug 1979	Jul 1982	2024-03-01	1945
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	66	90	Aug 1983	Sep 1992	2024-03-01	1946
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	70	95	Aug 1983	Apr 1993	2024-03-01	1947
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	82	112	Aug 1982	Dec 1989	2024-03-01	1948
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	72	98	Aug 1989	Mar 1993	2024-03-01	1949
VW	Polo	1	Coupe	Frontantrieb	Benzin	29	40	May 1982	Oct 1986	2024-03-01	1950
VW	Polo	1.1	Coupe	Frontantrieb	Benzin	37	50	Oct 1981	Jul 1983	2024-03-01	1951
VW	Polo	1.3	Coupe	Frontantrieb	Benzin	44	60	Oct 1981	Jul 1983	2024-03-01	1952
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	85	115	Jan 1987	Aug 1990	2024-03-01	1953
VW	Polo	1.3 D	Coupe	Frontantrieb	Diesel	33	45	Aug 1986	Aug 1990	2024-03-01	1954
VW	Polo	1.4 D	Coupe	Frontantrieb	Diesel	35	48	Aug 1990	Sep 1994	2024-03-01	1955
VW	Polo	1.0 CAT	Coupe	Frontantrieb	Benzin	33	45	Aug 1989	Sep 1994	2024-03-01	1956
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	40	55	Jul 1987	Aug 1994	2024-03-01	1957
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	55	75	Oct 1989	Sep 1994	2024-03-01	1958
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	83	113	Aug 1990	Sep 1994	2024-03-01	1959
Ford	Fiesta ii	1.6 XR2	Schrägheck	Frontantrieb	Benzin	71	97	Apr 1984	Feb 1989	2024-03-01	1960
Ford	Escort v turnier	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Feb 1993	Jan 1995	2024-03-01	1962
Ford	Escort v turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	66	90	Sep 1992	Jan 1995	2024-03-01	1963
Ford	Escort v turnier	1.8 I 16V	Kombi	Frontantrieb	Benzin	96	130	Feb 1993	Jan 1995	2024-03-01	1964
Audi	100	2.0 D	Stufenheck	Frontantrieb	Diesel	51	70	Aug 1978	Jul 1982	2024-03-01	1966
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1982	Dec 1987	2024-03-01	1967
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	19	26	Oct 1962	Sep 1983	2024-03-01	1968
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	21	29	Oct 1983	Oct 1988	2024-03-01	1969
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	25	34	Sep 1971	Dec 1988	2024-03-01	1970
Renault	4	1.1	Schrägheck	Frontantrieb	Benzin	25	34	Jun 1978	Jun 1990	2024-03-01	1971
Renault	4	0.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	21	29	Apr 1983	Jul 1989	2024-03-01	1972
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	25	34	Oct 1976	Jul 1989	2024-03-01	1974
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	26	35	Jul 1982	May 1989	2024-03-01	1975
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	26	35	Oct 1972	Aug 1984	2024-03-01	1976
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	27	37	Jan 1982	Dec 1984	2024-03-01	1977
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	120	163	Jul 2010	Mar 2016	2024-03-01	1978
Renault	5	1	Schrägheck	Frontantrieb	Benzin	32	44	Jan 1972	Dec 1985	2024-03-01	1979
Renault	5	1.1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1980	Dec 1985	2024-03-01	1980
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	31	42	Sep 1976	Sep 1979	2024-03-01	1981
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	33	45	Jun 1979	Sep 1984	2024-03-01	1982
Renault	5	1.3 Automatik	Schrägheck	Frontantrieb	Benzin	40	54	Jun 1979	Sep 1984	2024-03-01	1983
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	47	64	Sep 1975	Sep 1984	2024-03-01	1984
Renault	5	1.4 Automatik	Schrägheck	Frontantrieb	Benzin	43	59	Jun 1982	Sep 1984	2024-03-01	1985
Renault	5	1.4	Schrägheck	Frontantrieb	Benzin	46	63	Jan 1982	Dec 1985	2024-03-01	1986
Renault	5	1.4 Alpine A5	Schrägheck	Frontantrieb	Benzin	68	93	Sep 1977	Sep 1981	2024-03-01	1987
Renault	5	1.4 Alpine Turbo	Schrägheck	Frontantrieb	Benzin	79	108	Oct 1981	Jan 1985	2024-03-01	1988
Renault	Super 5	1	Schrägheck	Frontantrieb	Benzin	30	41	Oct 1984	Oct 1988	2024-03-01	1989
Renault	Super 5	1.1	Schrägheck	Frontantrieb	Benzin	33	45	Jan 1986	Mar 1995	2024-03-01	1990
Renault	Super 5	1.1	Schrägheck	Frontantrieb	Benzin	34	46	Oct 1984	Oct 1988	2024-03-01	1991
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	43	59	Oct 1984	Jun 1988	2024-03-01	1993
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Oct 1984	Jul 1989	2024-03-01	1994
Renault	Super 5	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	88	120	Apr 1985	Aug 1990	2024-03-01	1995
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1987	Aug 1990	2024-03-01	1996
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Jun 1987	Jul 1989	2024-03-01	1997
Renault	Super 5	1.7 I	Schrägheck	Frontantrieb	Benzin	69	94	Oct 1986	Aug 1991	2024-03-01	1998
Renault	Super 5	1.7	Schrägheck	Frontantrieb	Benzin	64	87	Jun 1987	Mar 1995	2024-03-01	1999
Renault	Super 5	1.6 D	Schrägheck	Frontantrieb	Diesel	40	55	Aug 1985	Dec 1996	2024-03-01	2000
Renault	Super 5	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1986	Mar 1995	2024-03-01	2001
Renault	12	1.3	Stufenheck	Frontantrieb	Benzin	40	54	Oct 1969	Aug 1980	2024-03-01	2002
Renault	12	1.3 TS	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1972	Aug 1980	2024-03-01	2003
Renault	12	1.3	Kombi	Frontantrieb	Benzin	40	54	Oct 1970	Aug 1980	2024-03-01	2004
Renault	9	1.1	Stufenheck	Frontantrieb	Benzin	35	48	Sep 1981	May 1987	2024-03-01	2005
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	44	60	Dec 1981	Dec 1988	2024-03-01	2006
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	49	67	Sep 1985	Dec 1988	2024-03-01	2007
Renault	9	1.4 Automatik	Stufenheck	Frontantrieb	Benzin	50	68	Sep 1981	Dec 1985	2024-03-01	2008
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	53	72	Sep 1981	Dec 1985	2024-03-01	2009
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	54	73	Oct 1986	Dec 1988	2024-03-01	2010
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1986	Dec 1988	2024-03-01	2011
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	59	80	Sep 1984	Dec 1989	2024-03-01	2012
Renault	9	1.6 D	Stufenheck	Frontantrieb	Diesel	40	55	Oct 1982	Dec 1988	2024-03-01	2013
Renault	11	1.1	Schrägheck	Frontantrieb	Benzin	35	48	Mar 1983	Jun 1986	2024-03-01	2014
Renault	11	1.2	Schrägheck	Frontantrieb	Benzin	40	55	Oct 1984	Dec 1988	2024-03-01	2015
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1983	Dec 1988	2024-03-01	2016
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Mar 1983	Dec 1988	2024-03-01	2017
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	50	68	Mar 1983	Dec 1985	2024-03-01	2018
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	53	72	May 1983	Dec 1985	2024-03-01	2019
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	77	105	Apr 1984	Dec 1986	2024-03-01	2020
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	85	115	Oct 1986	Dec 1988	2024-03-01	2021
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1986	Dec 1988	2024-03-01	2022
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1984	Dec 1988	2024-03-01	2023
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	59	80	Oct 1983	Dec 1987	2024-03-01	2024
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	64	87	Jun 1987	Dec 1988	2024-03-01	2025
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1986	Dec 1988	2024-03-01	2026
Renault	11	1.6 D	Schrägheck	Frontantrieb	Diesel	40	55	Aug 1983	Dec 1988	2024-03-01	2027
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	42	57	May 1976	Jan 1980	2024-03-01	2028
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1980	Dec 1983	2024-03-01	2029
Renault	14	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Sep 1979	Jun 1983	2024-03-01	2030
Renault	16	1.6 TL	Schrägheck	Frontantrieb	Benzin	48	65	Jan 1971	Aug 1980	2024-03-01	2031
Renault	18	1.4	Stufenheck	Frontantrieb	Benzin	47	64	Apr 1978	Jul 1986	2024-03-01	2032
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	80	109	Oct 1980	Sep 1982	2024-03-01	2033
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	92	125	Oct 1982	Jul 1986	2024-03-01	2034
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Apr 1982	Jul 1986	2024-03-01	2035
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	58	79	Apr 1978	Sep 1982	2024-03-01	2036
Renault	18	2.1 Diesel	Stufenheck	Frontantrieb	Diesel	49	67	Nov 1981	Jul 1986	2024-03-01	2037
Renault	18	1.4	Kombi	Frontantrieb	Benzin	47	64	May 1979	Jul 1986	2024-03-01	2038
Renault	18	1.6	Kombi	Frontantrieb	Benzin	54	73	Jan 1982	Jul 1986	2024-03-01	2039


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 **4 个尺寸组**，完成 6 个输入 Ktype 的尺寸组映射。
* VW Passat B2 Variant 已按官方 `Type 32B` 旅行车边界建组，官方三维为 `4540 × 1685 × 1385 mm`。([Volkswagen Newsroom][1])
* Ford Fiesta Mk II XR2 使用 XR2 专属外廓，三维为 `3711 × 1620 × 1334 mm`；Escort Mk Vb Turnier 三维为 `4268 × 1690 × 1410 mm`，来源明确标注宽度不含后视镜。([汽车目录][2])
* Audi 100 C3 1.8 已确认采用改款前 `Typ 44` 四门轿车尺寸 `4793 × 1814 × 1422 mm`，宽度不含后视镜。([汽车目录][3])
* Passat B1 Variant、Golf I Cabriolet、Polo II Coupé 和 Audi 100 C2 暂不建立猜测组；其中 Golf I Cabriolet 官方资料明确说明 1988 款外包围使车身更宽且略长，需要拆分外廓。([Volkswagen Newsroom][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：6
* PENDING 输入 Ktype：94
* READY 映射行：6
* 已确认尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1936	1936	Wagon	Passat B2	Type 32B	5	EU-VW-PASSAT-B2-WAGON-5D-01	HIGH	Type 32B五门Variant旅行车。	READY
1960	1960	Hatchback	Fiesta Mk II	FBD	3	EU-FORD-FIESTA-MK2-HATCHBACK-3D-XR2-01	HIGH	XR2三门车身及专属外部套件。	READY
1962	1962	Wagon	Escort Mk Vb	ANL	5	EU-FORD-ESCORT-MK5B-WAGON-5D-01	HIGH	ANL五门Turnier旅行车。	READY
1963	1963	Wagon	Escort Mk Vb	ANL	5	EU-FORD-ESCORT-MK5B-WAGON-5D-01	HIGH	ANL五门Turnier旅行车。	READY
1964	1964	Wagon	Escort Mk Vb	ANL	5	EU-FORD-ESCORT-MK5B-WAGON-5D-01	HIGH	ANL五门Turnier旅行车。	READY
1967	1967	Sedan	Audi 100 C3	Typ 44	4	EU-AUDI-100-C3-SEDAN-4D-PREFL-01	HIGH	Typ 44改款前四门轿车。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B2-WAGON-5D-01	4540	1685	1385	Volkswagen Newsroom Passat B2 official vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-FORD-FIESTA-MK2-HATCHBACK-3D-XR2-01	3711	1620	1334	Automobile-Catalog 1984 Ford Fiesta XR-2	https://www.automobile-catalog.com/car/1984/62570/ford_fiesta_xr-2.html
EU-FORD-ESCORT-MK5B-WAGON-5D-01	4268	1690	1410	Automobile-Catalog 1993 Ford Escort Turnier 1.6i 16V Ghia	https://www.automobile-catalog.com/car/1993/947000/ford_escort_turnier_1_6i_16v_ghia.html
EU-AUDI-100-C3-SEDAN-4D-PREFL-01	4793	1814	1422	Automobile-Catalog 1983 Audi 100 1.8	https://www.automobile-catalog.com/car/1983/31250/audi_100_1_8.html
```

## 下一步优先处理

1. 核定 Passat B1 Variant 的早期、后期外廓边界，避免把普通掀背尺寸误用于 Variant。
2. 拆分 Golf I Cabriolet 1988 款外包围更新前后尺寸组。
3. 核定 Polo II Coupé 1990 年改款前后外廓，并批量关联 Ktype `1950–1959`。
4. 处理 Audi 100 C2 2.0 D 的改款前后长度及两门、四门适用边界。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538 "Vehicle data Passat B2 profile | Volkswagen Newsroom"
[2]: https://www.automobile-catalog.com/car/1984/62570/ford_fiesta_xr-2.html?utm_source=chatgpt.com "1984 Ford Fiesta XR-2 Specs Review (70.5 kW / 96 PS ..."
[3]: https://www.automobile-catalog.com/car/1983/31250/audi_100_1_8.html?utm_source=chatgpt.com "1983 Audi 100 1.8 Specs Review (55 kW / 75 PS / 74 hp) (for Europe )"
[4]: https://www.volkswagen-newsroom.com/en/golf-1-cabriolet-19791993-19488 "Golf I Cabriolet (1979–1993) | Volkswagen Newsroom"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 首次闭合 **Passat B1 Variant Type 33** 尺寸组，并批量关联 Ktype `1937、1938、1939、1941、1942`。Volkswagen 官方档案确认 B1 Variant 的车身边界，直接规格页确认三维为 `4190 × 1620 × 1370 mm`，宽度不含后视镜。([Volkswagen Newsroom][1])
* 首次闭合 **Golf I Cabriolet Type 155 早期标准外廓**尺寸组，并关联生产期完全位于早期外廓阶段的 Ktype `1945`。官方档案确认 Type 155 车身及对应发动机生产期，直接规格页确认三维为 `3815 × 1630 × 1395 mm`，宽度不含后视镜。([Volkswagen Newsroom][2])
* 其余跨越晚期外包围、门数或高度范围仍未闭合的记录未建立猜测性尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：12
* PENDING 输入 Ktype：88
* READY 映射行：12
* 已确认尺寸组：6
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1937	1937	Wagon	Passat B1	Type 33	5	EU-VW-PASSAT-B1-WAGON-5D-01	HIGH	Type 33 Variant五门物理外廓。	READY
1938	1938	Wagon	Passat B1	Type 33	5	EU-VW-PASSAT-B1-WAGON-5D-01	HIGH	Type 33 Variant五门物理外廓。	READY
1939	1939	Wagon	Passat B1	Type 33	5	EU-VW-PASSAT-B1-WAGON-5D-01	HIGH	Type 33 Variant五门物理外廓。	READY
1941	1941	Wagon	Passat B1	Type 33	5	EU-VW-PASSAT-B1-WAGON-5D-01	HIGH	Type 33 Variant五门物理外廓。	READY
1942	1942	Wagon	Passat B1	Type 33	5	EU-VW-PASSAT-B1-WAGON-5D-01	HIGH	Type 33 Variant五门物理外廓。	READY
1945	1945	Convertible	Golf I	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	Type 155早期标准保险杠外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B1-WAGON-5D-01	4190	1620	1370	Volkswagen Newsroom Passat B1 official archive; Automobile-Catalog 1974 Volkswagen Passat Variant 1300	https://www.volkswagen-newsroom.com/en/passat-b1-19731980-19534; https://www.automobile-catalog.com/car/1974/38960/volkswagen_passat_variant_1300.html
EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	3815	1630	1395	Volkswagen Newsroom Golf I Cabriolet official vehicle data; Automobile-Catalog 1980 Volkswagen Golf Cabrio GTi	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489; https://www.automobile-catalog.com/car/1980/35285/volkswagen_golf_cabrio_gti.html
```

## 5. 下一步优先处理

1. 按发动机生产边界拆分 Golf I Cabriolet 普通外廓与晚期 Sport/外包围外廓，并关联其余 Ktype `1943–1949`。
2. 核定 Polo II Coupé 普通版、G40 以及 1990 年改款前后的精确高度，批量处理 Ktype `1950–1959`。
3. 继续处理 Renault 5、Super 5、Renault 9 和 Renault 11 的门数及物理车身分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/passat-b1-19731980-19534?utm_source=chatgpt.com "Passat B1 (1973–1980)"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489?utm_source=chatgpt.com "Vehicle data Golf I Cabriolet profile"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Fiat Grande Punto 199 的三门、五门分支。两种车身三维均为 `4030 × 1687 × 1490 mm`，但因车门及侧围结构不同分别建组；Ktype `1940` 拆为两条派生映射。([手册架][1])
* 闭合 Renault 5 Alpine 系列。普通 Alpine 在 1979 年 7 月前后宽度由 `1549 mm` 变为 `1525 mm`，Ktype `1987` 拆分为两个外廓；Alpine Turbo `R122B` 单独建组并关联 Ktype `1988`。([FIA历史数据库][2])
* 闭合 Renault 14 的统一五门尺寸组，批量关联 Ktype `2028–2030`；Renault 16 因 1975 年中期前后车身宽度不同，将 Ktype `2031` 拆成两个物理外廓。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：19
* PENDING 输入 Ktype：81
* READY 映射行：22
* 已确认尺寸组：14
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1940_3dr	1940	Hatchback	Grande Punto 199	199AXZ1A	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	三门车身。	READY
1940_5dr	1940	Hatchback	Grande Punto 199	199BXZ1A	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	五门车身。	READY
1987_pre79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-PRE79-01	HIGH	1979年7月前Alpine外廓。	READY
1987_post79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-POST79-01	HIGH	1979年7月起Alpine外廓。	READY
1988	1988	Hatchback	Renault 5 I	R122B	3	EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-TURBO-01	HIGH	Alpine Turbo三门外廓。	READY
2028	2028	Hatchback	Renault 14	121	5	EU-RENAULT-14-121-HATCHBACK-5D-01	HIGH	121五门掀背车身。	READY
2029	2029	Hatchback	Renault 14	121	5	EU-RENAULT-14-121-HATCHBACK-5D-01	HIGH	121五门掀背车身。	READY
2030	2030	Hatchback	Renault 14	121	5	EU-RENAULT-14-121-HATCHBACK-5D-01	HIGH	121五门掀背车身。	READY
2031_pre75	2031	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-PRE75-01	HIGH	1975年中期改款前外廓。	READY
2031_post75	2031	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-5D-POST75-01	HIGH	1975年中期改款后外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual Euro 5 Start&Stop	https://www.automobile-catalog.com/car/2010/1456385/fiat_grande_punto_1_2_actual_euro_5_startandstop.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual Euro 5 Start&Stop	https://www.automobile-catalog.com/car/2010/1456385/fiat_grande_punto_1_2_actual_euro_5_startandstop.html
EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-PRE79-01	3543	1549	1376	Automobile-Catalog 1979 Renault 5 Alpine	https://www.automobile-catalog.com/car/1979/25250/renault_5_alpine.html
EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-POST79-01	3543	1525	1376	Automobile-Catalog 1979 Renault 5 Alpine since July 1979	https://www.automobile-catalog.com/car/1979/2927975/renault_5_alpine.html
EU-RENAULT-5-I-HATCHBACK-3D-ALPINE-TURBO-01	3558	1525	1376	Automobile-Catalog 1981 Renault 5 Alpine Turbo	https://www.automobile-catalog.com/car/1981/50915/renault_5_alpine_turbo.html
EU-RENAULT-14-121-HATCHBACK-5D-01	4025	1624	1405	Automobile-Catalog 1976 Renault 14 TL; Automobile-Catalog 1980 Renault 14 LS	https://www.automobile-catalog.com/car/1976/2929565/renault_14_tl.html; https://www.automobile-catalog.com/car/1980/2929670/renault_14_ls.html
EU-RENAULT-16-HATCHBACK-5D-PRE75-01	4237	1648	1450	Automobile-Catalog 1973 Renault 16 TL	https://www.automobile-catalog.com/car/1973/2926040/renault_16_tl.html
EU-RENAULT-16-HATCHBACK-5D-POST75-01	4237	1628	1450	Automobile-Catalog 1977 Renault 16 TL	https://www.automobile-catalog.com/car/1977/2926250/renault_16_tl.html
```

## 5. 下一步优先处理

1. 闭合 Renault 5 普通版的早期、后期外廓及必要门数分支。
2. 批量处理 Renault Super 5，并区分三门、五门及可能改变外廓的运动版本。
3. 继续处理 Renault 9、Renault 11 和 Renault 18 的改款及车身形式边界。
4. 返回处理 Golf I Cabriolet 和 Polo II Coupé 的剩余版本。

推进信号：CONTINUE

[1]: https://www.manualshelf.com/manual/fiat/grande-punto-actual/owner-manual-english.html?utm_source=chatgpt.com "FIAT Grande Punto Actual : Owner manual"
[2]: https://historicdb.fia.com/model/5-alpine-type-r-1223?utm_source=chatgpt.com "5 Alpine Type R 1223 | FIA Historic Database"
[3]: https://www.automobile-catalog.com/car/1976/2929565/renault_14_tl.html?utm_source=chatgpt.com "1976 Renault 14 L Specs Review (42 kW / 57 PS ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault 12 四门轿车和五门 Break 的 Phase I、Phase II 四个尺寸组。
* Renault 12 于 1975 年秋季改款，轿车外廓由 `4340 × 1636 × 1434 mm` 调整为 `4348 × 1616 × 1435 mm`；Break 外廓由 `4404 × 1616 × 1455 mm` 调整为 `4371 × 1616 × 1455 mm`。([汽车目录][1])
* Ktype `2002、2003、2004` 均跨越该改款时间，已分别拆分为 `prefl` 与 `facelift` 派生映射。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：22
* PENDING 输入 Ktype：78
* READY 映射行：28
* 已确认尺寸组：18
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2002_prefl	2002	Sedan	Renault 12 Phase I		4	EU-RENAULT-12-PHASE1-SEDAN-4D-01	HIGH	1975年秋季改款前四门轿车。	READY
2002_facelift	2002	Sedan	Renault 12 Phase II		4	EU-RENAULT-12-PHASE2-SEDAN-4D-01	HIGH	1975年秋季改款后四门轿车。	READY
2003_prefl	2003	Sedan	Renault 12 Phase I		4	EU-RENAULT-12-PHASE1-SEDAN-4D-01	HIGH	1975年秋季改款前TS四门轿车。	READY
2003_facelift	2003	Sedan	Renault 12 Phase II		4	EU-RENAULT-12-PHASE2-SEDAN-4D-01	HIGH	1975年秋季改款后TS四门轿车。	READY
2004_prefl	2004	Wagon	Renault 12 Phase I		5	EU-RENAULT-12-PHASE1-WAGON-5D-01	HIGH	1975年秋季改款前五门Break。	READY
2004_facelift	2004	Wagon	Renault 12 Phase II		5	EU-RENAULT-12-PHASE2-WAGON-5D-01	HIGH	1975年秋季改款后五门Break。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-12-PHASE1-SEDAN-4D-01	4340	1636	1434	Automobile-Catalog 1972 Renault 12 TL	https://www.automobile-catalog.com/car/1972/2926400/renault_12_tl.html
EU-RENAULT-12-PHASE2-SEDAN-4D-01	4348	1616	1435	Automobile-Catalog 1975 Renault 12 L since Autumn 1975	https://www.automobile-catalog.com/car/1975/2926670/renault_12_l.html
EU-RENAULT-12-PHASE1-WAGON-5D-01	4404	1616	1455	Automobile-Catalog 1975 Renault 12 TN Break	https://www.automobile-catalog.com/car/1975/2926640/renault_12_tn_break.html
EU-RENAULT-12-PHASE2-WAGON-5D-01	4371	1616	1455	Automobile-Catalog 1976 Renault 12 L Break	https://www.automobile-catalog.com/car/1976/2926745/renault_12_l_break.html
```

## 5. 下一步优先处理

1. 闭合 Renault 18 Sedan 的普通版、Turbo 和后期外廓尺寸组。
2. 闭合 Renault 18 Break 的普通旅行车尺寸组并批量关联 Ktype `2038–2039`。
3. 继续处理 Renault 9、Renault 11 的改款和门数分支。
4. 随后处理 Renault 5、Super 5 的普通版三门、五门及运动外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/2926400/renault_12_tl.html?utm_source=chatgpt.com "Detailed specs review of 1972 Renault 12 TL model for Europe"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault 18 Turbo 早期 `110 PS` 与后期 `125 PS` 两个外廓组。
* Ktype `2033` 对应早期 Turbo，三维为 `4394 × 1696 × 1405 mm`；Ktype `2034` 对应后期 Turbo，车高变为 `1410 mm`，因此不能复用同一尺寸组。宽度均明确为不含后视镜。([汽车目录][1])
* Renault 18 普通 Sedan、Diesel 和 Break 仍存在年份、保险杠及版本外廓差异，本轮未建立猜测性尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：24
* PENDING 输入 Ktype：76
* READY 映射行：30
* 已确认尺寸组：20
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2033	2033	Sedan	Renault 18		4	EU-RENAULT-18-SEDAN-4D-TURBO-EARLY-01	HIGH	早期110 PS Turbo四门外廓。	READY
2034	2034	Sedan	Renault 18		4	EU-RENAULT-18-SEDAN-4D-TURBO-LATE-01	HIGH	后期125 PS Turbo四门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-18-SEDAN-4D-TURBO-EARLY-01	4394	1696	1405	Automobile-Catalog 1982 Renault 18 Turbo	https://www.automobile-catalog.com/car/1982/2930840/renault_18_turbo.html
EU-RENAULT-18-SEDAN-4D-TURBO-LATE-01	4394	1696	1410	Automobile-Catalog 1983 Renault 18 Turbo; Automobile-Catalog 1984 Renault 18 Turbo	https://www.automobile-catalog.com/car/1983/50375/renault_18_turbo.html; https://www.automobile-catalog.com/car/1984/2932250/renault_18_turbo.html
```

## 5. 下一步优先处理

1. 闭合 Renault 18 普通 Sedan 的早期、1982 更新及后期外廓，处理 Ktype `2032、2035–2037`。
2. 闭合 Renault 18 Break 的 1.4 与 1.6 外廓，处理 Ktype `2038–2039`。
3. 批量处理 Renault 9 与 Renault 11 的 Phase I、Phase II 和必要门数分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1982/2930840/renault_18_turbo.html?utm_source=chatgpt.com "1982 Renault 18 Turbo Specs Review (81 kW / 110 PS ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* 闭合 Renault 18 普通 Sedan 的窄体、宽体、1982 年更新及 1984 年 Phase II 外廓，完成 Ktype `2032、2035、2036、2037`。对应资料明确标注宽度不含后视镜。([汽车目录][1])
* 闭合 Renault 18 Break 的窄体、宽体及 Phase II 外廓，完成 Ktype `2038、2039`。1982 年中期长度更新为 `4487 mm`，1984 年 Phase II 宽度更新为 `1696 mm`。([汽车目录][2])
* 本轮共新增 17 条派生映射、12 个尺寸组；相同物理外廓已跨 Ktype 复用。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：30
* PENDING 输入 Ktype：70
* READY 映射行：47
* 已确认尺寸组：32
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2032_early	2032	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-NARROW-EARLY-01	HIGH	1980年9月更新前的窄体四门外廓。	READY
2032_mid	2032	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-NARROW-LOW-01	HIGH	1980年9月至1982年7月窄体四门外廓。	READY
2032_late	2032	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-NARROW-LONG-01	HIGH	1982年7月至1984年3月更新外廓。	READY
2032_facelift	2032	Sedan	Renault 18 Phase II		4	EU-RENAULT-18-SEDAN-4D-P2-STANDARD-01	HIGH	1984年3月起Phase II四门外廓。	READY
2035_prefl	2035	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-WIDE-LONG-01	HIGH	Phase I后期宽体四门外廓。	READY
2035_facelift	2035	Sedan	Renault 18 Phase II		4	EU-RENAULT-18-SEDAN-4D-P2-STANDARD-01	HIGH	1984年3月起Phase II四门外廓。	READY
2036_early	2036	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-WIDE-EARLY-01	HIGH	1981年末车身更新前宽体四门外廓。	READY
2036_late	2036	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-WIDE-LONG-01	HIGH	1981年末更新后的宽体四门外廓。	READY
2037_early	2037	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-WIDE-SHORT-LOW-01	HIGH	1982年7月更新前柴油四门外廓。	READY
2037_late	2037	Sedan	Renault 18 Phase I		4	EU-RENAULT-18-SEDAN-4D-P1-WIDE-LONG-01	HIGH	1982年7月至1984年3月四门外廓。	READY
2037_facelift	2037	Sedan	Renault 18 Phase II		4	EU-RENAULT-18-SEDAN-4D-P2-STANDARD-01	HIGH	1984年3月起Phase II四门外廓。	READY
2038_early	2038	Wagon	Renault 18 Phase I		5	EU-RENAULT-18-WAGON-5D-P1-NARROW-SHORT-01	HIGH	1982年7月更新前窄体Break外廓。	READY
2038_late	2038	Wagon	Renault 18 Phase I		5	EU-RENAULT-18-WAGON-5D-P1-NARROW-LONG-01	HIGH	1982年7月至1984年3月Break外廓。	READY
2038_facelift	2038	Wagon	Renault 18 Phase II		5	EU-RENAULT-18-WAGON-5D-P2-STANDARD-01	HIGH	1984年3月起Phase II Break外廓。	READY
2039_early	2039	Wagon	Renault 18 Phase I		5	EU-RENAULT-18-WAGON-5D-P1-WIDE-SHORT-01	HIGH	1982年7月更新前宽体Break外廓。	READY
2039_late	2039	Wagon	Renault 18 Phase I		5	EU-RENAULT-18-WAGON-5D-P1-WIDE-LONG-01	HIGH	1982年7月至1984年3月宽体Break外廓。	READY
2039_facelift	2039	Wagon	Renault 18 Phase II		5	EU-RENAULT-18-WAGON-5D-P2-STANDARD-01	HIGH	1984年3月起Phase II Break外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-18-SEDAN-4D-P1-NARROW-EARLY-01	4369	1682	1405	Automobile-Catalog 1978 Renault 18 TL	https://www.automobile-catalog.com/car/1978/35000/renault_18_tl.html
EU-RENAULT-18-SEDAN-4D-P1-NARROW-LOW-01	4369	1682	1400	Automobile-Catalog 1982 Renault 18 up to July 1982	https://www.automobile-catalog.com/car/1982/2930945/renault_18.html
EU-RENAULT-18-SEDAN-4D-P1-NARROW-LONG-01	4394	1682	1400	Automobile-Catalog 1982 Renault 18 since July 1982	https://www.automobile-catalog.com/car/1982/2931425/renault_18.html
EU-RENAULT-18-SEDAN-4D-P2-STANDARD-01	4394	1696	1405	Automobile-Catalog 1984 Renault 18 TL; Automobile-Catalog 1984 Renault 18 GTD	https://www.automobile-catalog.com/car/1984/2932130/renault_18_tl.html; https://www.automobile-catalog.com/car/1984/2932325/renault_18_gtd.html
EU-RENAULT-18-SEDAN-4D-P1-WIDE-EARLY-01	4381	1689	1405	Automobile-Catalog 1978 Renault 18 GTS; Automobile-Catalog 1981 Renault 18 TS	https://www.automobile-catalog.com/car/1978/40670/renault_18_gts.html; https://www.automobile-catalog.com/car/1981/2930675/renault_18_ts.html
EU-RENAULT-18-SEDAN-4D-P1-WIDE-LONG-01	4394	1689	1405	Automobile-Catalog 1982 Renault 18 GTS; Automobile-Catalog 1982 Renault 18 TD	https://www.automobile-catalog.com/car/1982/2930990/renault_18_gts.html; https://www.automobile-catalog.com/car/1982/2931800/renault_18_td_bv4.html
EU-RENAULT-18-SEDAN-4D-P1-WIDE-SHORT-LOW-01	4369	1689	1400	Automobile-Catalog 1982 Renault 18 TD up to July 1982	https://www.automobile-catalog.com/car/1982/2931050/renault_18_td.html
EU-RENAULT-18-WAGON-5D-P1-NARROW-SHORT-01	4451	1682	1402	Automobile-Catalog 1979 Renault 18 Break; Automobile-Catalog 1981 Renault 18 Break TL	https://www.automobile-catalog.com/car/1979/2930525/renault_18_break.html; https://www.automobile-catalog.com/car/1981/2931140/renault_18_break_tl_bv4.html
EU-RENAULT-18-WAGON-5D-P1-NARROW-LONG-01	4487	1682	1402	Automobile-Catalog 1983 Renault 18 Break	https://www.automobile-catalog.com/car/1983/2931470/renault_18_break.html
EU-RENAULT-18-WAGON-5D-P1-WIDE-SHORT-01	4451	1689	1402	Automobile-Catalog 1981 Renault 18 TS Estate; Automobile-Catalog 1982 Renault 18 Break GTL up to July 1982	https://www.automobile-catalog.com/car/1981/2933270/renault_18_ts_estate_soleil.html; https://www.automobile-catalog.com/car/1982/2931155/renault_18_break_gtl.html
EU-RENAULT-18-WAGON-5D-P1-WIDE-LONG-01	4487	1689	1402	Automobile-Catalog 1982 Renault 18 Break GTL since July 1982	https://www.automobile-catalog.com/car/1982/2931530/renault_18_break_gtl.html
EU-RENAULT-18-WAGON-5D-P2-STANDARD-01	4487	1696	1402	Automobile-Catalog 1984 Renault 18 Break TL; Automobile-Catalog 1984 Renault 18 Break GTL	https://www.automobile-catalog.com/car/1984/2932145/renault_18_break_tl.html; https://www.automobile-catalog.com/car/1984/2932175/renault_18_break_gtl.html
```

## 5. 下一步优先处理

1. 闭合 Renault 9 Phase I、Phase II 四门 Sedan，批量关联 Ktype `2005–2013`。
2. 闭合 Renault 11 三门、五门及 Phase I、Phase II 外廓，批量关联 Ktype `2014–2027`。
3. 随后处理 Renault 5、Super 5 的普通版门数和运动外廓。
4. 返回处理 Golf I Cabriolet、Polo II Coupé 及剩余 Audi、Fiat Scudo 记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/35000/renault_18_tl.html?utm_source=chatgpt.com "1978 Renault 18 TL Specs Review (47.1 kW / 64 PS / 63 hp) (since April 1978 for Europe )"
[2]: https://www.automobile-catalog.com/car/1979/2930525/renault_18_break.html?utm_source=chatgpt.com "1979 Renault 18 Break Specs Review (47.1 kW / 64 PS / 63 hp) (since October 1979 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault 9 `L42` 四门 Sedan 的 Phase I、Phase II 两个尺寸组。
* Phase I 外廓为 `4063 × 1634 × 1405 mm`；1986 年 10 月改款后的 Phase II 外廓为 `4132 × 1666 × 1410 mm`，宽度均为不含后视镜口径。([汽车目录][1])
* 批量完成 Ktype `2005–2013`；跨越 1986 年 10 月改款的 Ktype 已拆分为 `prefl` 与 `facelift`，仅处于单一阶段的 Ktype 直接关联对应缓存尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：39
* PENDING 输入 Ktype：61
* READY 映射行：61
* 已确认尺寸组：34
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2005_prefl	2005	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	1986年10月改款前四门外廓。	READY
2005_facelift	2005	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	1986年10月改款后四门外廓。	READY
2006_prefl	2006	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	1986年10月改款前四门外廓。	READY
2006_facelift	2006	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	1986年10月改款后四门外廓。	READY
2007_prefl	2007	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	1986年10月改款前四门外廓。	READY
2007_facelift	2007	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	1986年10月改款后四门外廓。	READY
2008	2008	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	Phase I四门自动挡车型。	READY
2009	2009	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	Phase I四门外廓。	READY
2010	2010	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	Phase II四门外廓。	READY
2011	2011	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	Phase II四门外廓。	READY
2012_prefl	2012	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	1986年10月改款前四门外廓。	READY
2012_facelift	2012	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	1986年10月改款后四门外廓。	READY
2013_prefl	2013	Sedan	Renault 9 Phase I	L42	4	EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	HIGH	1986年10月改款前柴油四门外廓。	READY
2013_facelift	2013	Sedan	Renault 9 Phase II	L42	4	EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	HIGH	1986年10月改款后柴油四门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-9-L42-PHASE1-SEDAN-4D-01	4063	1634	1405	Automobile-Catalog 1981 Renault 9 TC	https://www.automobile-catalog.com/car/1981/29885/renault_9_tc.html
EU-RENAULT-9-L42-PHASE2-SEDAN-4D-01	4132	1666	1410	Automobile-Catalog 1987 Renault 9 GTC	https://www.automobile-catalog.com/car/1987/2934650/renault_9_gtc.html
```

## 5. 下一步优先处理

1. 闭合 Renault 11 Phase I、Phase II 的三门和五门外廓，并批量处理 Ktype `2014–2027`。
2. 闭合 Renault 5 普通版本的阶段差异和门数边界。
3. 批量处理 Renault Super 5 的三门、五门及运动版本。
4. 返回处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 与 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/29885/renault_9_tc.html?utm_source=chatgpt.com "1981 Renault 9 TC Specs Review (35.5 kW / 48 PS ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 闭合 Renault 11 Phase I `1.1 48 PS` 的三门、五门外廓，Ktype `2014` 拆分为两个门数分支，三维均为 `3973 × 1630 × 1406 mm`。([汽车目录][1])
* 闭合 Renault 11 Turbo `105 PS` 的两阶段外廓：1985 年 3 月前仅三门，尺寸为 `3985 × 1634 × 1380 mm`；1985 年 3 月后覆盖三门、五门，尺寸调整为 `3985 × 1630 × 1377 mm`。Ktype `2020` 拆分为三个物理分支。([汽车目录][2])
* 闭合 Renault 11 Phase II Turbo `115 PS` 三门外廓，关联 Ktype `2021`，尺寸为 `4047 × 1666 × 1380 mm`。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：42
* PENDING 输入 Ktype：58
* READY 映射行：67
* 已确认尺寸组：40
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2014_3dr	2014	Hatchback	Renault 11 Phase I		3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-11-01	HIGH	Phase I三门1.1车身。	READY
2014_5dr	2014	Hatchback	Renault 11 Phase I		5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-11-01	HIGH	Phase I五门1.1车身。	READY
2020_3dr_pre85	2020	Hatchback	Renault 11 Phase I		3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-TURBO-EARLY-01	HIGH	1985年3月前105 PS Turbo三门外廓。	READY
2020_3dr_post85	2020	Hatchback	Renault 11 Phase I		3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-TURBO-LATE-01	HIGH	1985年3月起105 PS Turbo三门外廓。	READY
2020_5dr_post85	2020	Hatchback	Renault 11 Phase I		5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-TURBO-LATE-01	HIGH	1985年3月起105 PS Turbo五门外廓。	READY
2021	2021	Hatchback	Renault 11 Phase II		3	EU-RENAULT-11-PHASE2-HATCHBACK-3D-TURBO-01	HIGH	Phase II 115 PS Turbo三门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-11-PHASE1-HATCHBACK-3D-11-01	3973	1630	1406	Automobile-Catalog 1984 Renault 11 TC	https://www.automobile-catalog.com/car/1984/2934335/renault_11_tc.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-11-01	3973	1630	1406	Automobile-Catalog 1984 Renault 11 TC	https://www.automobile-catalog.com/car/1984/2934335/renault_11_tc.html
EU-RENAULT-11-PHASE1-HATCHBACK-3D-TURBO-EARLY-01	3985	1634	1380	Automobile-Catalog 1985 Renault 11 Turbo up to March 1985	https://www.automobile-catalog.com/car/1985/49760/renault_11_turbo.html
EU-RENAULT-11-PHASE1-HATCHBACK-3D-TURBO-LATE-01	3985	1630	1377	Automobile-Catalog 1985 Renault 11 Turbo since March 1985	https://www.automobile-catalog.com/car/1985/2934320/renault_11_turbo.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-TURBO-LATE-01	3985	1630	1377	Automobile-Catalog 1985 Renault 11 Turbo since March 1985	https://www.automobile-catalog.com/car/1985/2934320/renault_11_turbo.html
EU-RENAULT-11-PHASE2-HATCHBACK-3D-TURBO-01	4047	1666	1380	Automobile-Catalog 1987 Renault 11 Turbo	https://www.automobile-catalog.com/car/1987/56405/renault_11_turbo.html
```

## 5. 下一步优先处理

1. 闭合 Renault 11 普通 `1.2、1.4、1.7、1.6 D` 版本的门数、Phase I/II 及配置外廓，处理 Ktype `2015–2019、2022–2027`。
2. 处理 Renault 5 普通版的三门、五门及阶段差异。
3. 批量处理 Renault Super 5 的门数和 GT Turbo 等运动外廓。
4. 返回处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 和 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1984/2934335/renault_11_tc.html?utm_source=chatgpt.com "1984 Renault 11 TC Specs Review (35.5 kW / 48 PS ..."
[2]: https://www.automobile-catalog.com/car/1985/49760/renault_11_turbo.html?utm_source=chatgpt.com "1985 Renault 11 Turbo Specs Review (77 kW / 105 PS / 103 hp) (up to March 1985 for Europe )"
[3]: https://www.automobile-catalog.com/car/1987/56405/renault_11_turbo.html?utm_source=chatgpt.com "1987 Renault 11 Turbo Specs Review (84.5 kW / 115 PS / 113 hp) (for Europe )"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 1. 更新点

* 闭合 Renault 11 `1.4 72 PS` 五门车身的两个 Phase I 外廓。
* 1984 年中期前尺寸为 `3985 × 1660 × 1400 mm`；中期更新后变为 `3981 × 1660 × 1406 mm`，宽度均不含后视镜。Ktype `2019` 跨越该更新点，已拆分为两条映射。([汽车目录][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：43
* PENDING 输入 Ktype：57
* READY 映射行：69
* 已确认尺寸组：42
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2019_pre84	2019	Hatchback	Renault 11 Phase I		5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-TSE-EARLY-01	HIGH	1984年中期车身更新前五门外廓。	READY
2019_post84	2019	Hatchback	Renault 11 Phase I		5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-TSE-LATE-01	HIGH	1984年中期车身更新后五门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-11-PHASE1-HATCHBACK-5D-TSE-EARLY-01	3985	1660	1400	Automobile-Catalog 1983 Renault 11 TSE	https://www.automobile-catalog.com/car/1983/29930/renault_11_tse.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-TSE-LATE-01	3981	1660	1406	Automobile-Catalog 1984 Renault 11 TSE since mid-year 1984	https://www.automobile-catalog.com/car/1984/2934680/renault_11_tse.html
```

## 5. 下一步优先处理

1. 继续闭合 Renault 11 `1.2、1.4 60/67/68 PS` 的三门、五门及阶段外廓。
2. 处理 Renault 11 `1.7` 普通版和 `1.6 D` 的 Phase I/II 分支。
3. 随后批量处理 Renault 5、Super 5。
4. 返回处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 和 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/29930/renault_11_tse.html?utm_source=chatgpt.com "1983 Renault 11 TSE Specs Review (53 kW / 72 PS / 71 hp) (since March 1983 for Europe )"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* 闭合 Renault 11 `1.2 55 PS` 的 Phase I、Phase II 三门与五门分支。Phase I 标准外廓为 `3985 × 1660 × 1410 mm`，Phase II 标准外廓为 `3985 × 1660 × 1405 mm`；该发动机覆盖三门和五门车身。([汽车数据][1])
* Ktype `2022` 的 `1.7 73 PS` TX Catalyst 同属 Phase II 标准三门/五门外廓，直接复用本轮新建尺寸组，不重复建组。([汽车目录][2])
* 闭合 Ktype `2025` 的 `1.7 87 PS` 五门 TXE Catalyst 外廓，尺寸为 `4047 × 1666 × 1405 mm`，宽度明确不含后视镜。([汽车数据][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：46
* PENDING 输入 Ktype：54
* READY 映射行：76
* 已确认尺寸组：47
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2015_3dr_prefl	2015	Hatchback	Renault 11 Phase I	C37S	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-STANDARD-01	MEDIUM	Phase I三门1.2标准外廓。	READY
2015_5dr_prefl	2015	Hatchback	Renault 11 Phase I	B37S	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-STANDARD-01	HIGH	Phase I五门1.2标准外廓。	READY
2015_3dr_facelift	2015	Hatchback	Renault 11 Phase II	C37S	3	EU-RENAULT-11-PHASE2-HATCHBACK-3D-STANDARD-01	HIGH	Phase II三门1.2标准外廓。	READY
2015_5dr_facelift	2015	Hatchback	Renault 11 Phase II	B37S	5	EU-RENAULT-11-PHASE2-HATCHBACK-5D-STANDARD-01	HIGH	Phase II五门1.2标准外廓。	READY
2022_3dr	2022	Hatchback	Renault 11 Phase II	C37L	3	EU-RENAULT-11-PHASE2-HATCHBACK-3D-STANDARD-01	HIGH	Phase II三门TX Catalyst外廓。	READY
2022_5dr	2022	Hatchback	Renault 11 Phase II	B37L	5	EU-RENAULT-11-PHASE2-HATCHBACK-5D-STANDARD-01	HIGH	Phase II五门TX Catalyst外廓。	READY
2025	2025	Hatchback	Renault 11 Phase II	B37D	5	EU-RENAULT-11-PHASE2-HATCHBACK-5D-TXE-01	HIGH	Phase II五门TXE Catalyst外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-11-PHASE1-HATCHBACK-3D-STANDARD-01	3985	1660	1410	Automobile-Catalog 1985 Renault 11 Broadway 1.2	https://www.automobile-catalog.com/car/1985/2934170/renault_11_broadway_1_2.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-STANDARD-01	3985	1660	1410	Automobile-Catalog 1985 Renault 11 TLE 1.2; Automobile-Catalog 1985 Renault 11 Broadway 1.2	https://www.automobile-catalog.com/car/1985/2934590/renault_11_tle_1_2.html; https://www.automobile-catalog.com/car/1985/2934170/renault_11_broadway_1_2.html
EU-RENAULT-11-PHASE2-HATCHBACK-3D-STANDARD-01	3985	1660	1405	Automobile-Catalog 1987 Renault 11 TC 1.2 BV5; Automobile-Catalog 1987 Renault 11 TX Catalyst	https://www.automobile-catalog.com/car/1987/2934935/renault_11_tc_1_2_bv5.html; https://www.automobile-catalog.com/car/1987/2935040/renault_11_tx_catalyst.html
EU-RENAULT-11-PHASE2-HATCHBACK-5D-STANDARD-01	3985	1660	1405	Automobile-Catalog 1987 Renault 11 TC 1.2 BV5; Automobile-Catalog 1987 Renault 11 TX Catalyst	https://www.automobile-catalog.com/car/1987/2934935/renault_11_tc_1_2_bv5.html; https://www.automobile-catalog.com/car/1987/2935040/renault_11_tx_catalyst.html
EU-RENAULT-11-PHASE2-HATCHBACK-5D-TXE-01	4047	1666	1405	Automobile-Catalog 1987 Renault 11 TXE Catalyst; Auto-Data Renault 11 B37D 1.7 87 HP	https://www.automobile-catalog.com/car/1987/2935085/renault_11_txe_catalyst.html; https://www.auto-data.net/en/renault-11-b-c37-1.7-b-c37d-87hp-10264
```

## 5. 下一步优先处理

1. 闭合 Renault 11 `1.4 60/67/68 PS` 的早期、1984/1985 更新及 Phase II 分支。
2. 处理 Renault 11 `1.7 75/80/88 PS` 与 `1.6 D` 的三门、五门和阶段外廓。
3. 随后批量处理 Renault 5、Super 5 的普通版与运动版分支。
4. 返回处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 和 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-11-b-c37-1.2-b-c-s37s-55hp-10255 "Renault 11 (B/C37) 1.2 (B/C/S37S) (55 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1988/2935040/renault_11_tx_catalyst.html?utm_source=chatgpt.com "1988 Renault 11 TX catalyst Specs Review (54 kW / 73 PS / 72 hp) (up to mid-year 1988 for Europe )"
[3]: https://www.auto-data.net/en/renault-11-b-c37-1.7-b-c37d-87hp-10264 "Renault 11 (B/C37) 1.7 (B/C37D) (87 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 1. 更新点

* 闭合 Renault 11 `1.4 68 PS` 的全部已确认外廓。Ktype `2018` 覆盖三门和五门，并在 1984 年中期及 1985 年 7 月发生外廓分化。
* 1983 年 3 月至 1984 年中期为 `3985 × 1660 × 1400 mm`；1984 年中期至 1985 年 7 月为 `3981 × 1660 × 1406 mm`。([汽车目录][1])
* 1985 年 7 月后同时存在窄保险杠 TL 外廓 `3973 × 1630 × 1410 mm`，以及 GTL/Broadway 外廓 `3985 × 1660 × 1410 mm`，均明确为不含后视镜宽度。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：47
* PENDING 输入 Ktype：53
* READY 映射行：84
* 已确认尺寸组：55
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2018_pre84_3dr	2018	Hatchback	Renault 11 Phase I	C373	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-PRE84-01	HIGH	1984年中期更新前三门外廓。	READY
2018_pre84_5dr	2018	Hatchback	Renault 11 Phase I	B373	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-PRE84-01	HIGH	1984年中期更新前五门外廓。	READY
2018_mid84_3dr	2018	Hatchback	Renault 11 Phase I	C373	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-MID84-01	HIGH	1984年中期至1985年7月三门外廓。	READY
2018_mid84_5dr	2018	Hatchback	Renault 11 Phase I	B373	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-MID84-01	HIGH	1984年中期至1985年7月五门外廓。	READY
2018_late_tl_3dr	2018	Hatchback	Renault 11 Phase I	C373	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-TL-LATE-01	HIGH	1985年7月起TL窄保险杠三门外廓。	READY
2018_late_tl_5dr	2018	Hatchback	Renault 11 Phase I	B373	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-TL-LATE-01	HIGH	1985年7月起TL窄保险杠五门外廓。	READY
2018_late_gtl_3dr	2018	Hatchback	Renault 11 Phase I	C373	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-GTL-LATE-01	HIGH	1985年7月起GTL或Broadway三门外廓。	READY
2018_late_gtl_5dr	2018	Hatchback	Renault 11 Phase I	B373	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-GTL-LATE-01	HIGH	1985年7月起GTL或Broadway五门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-PRE84-01	3985	1660	1400	Automobile-Catalog 1983 Renault 11 Automatic	https://www.automobile-catalog.com/car/1983/2933690/renault_11_automatic.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-PRE84-01	3985	1660	1400	Automobile-Catalog 1983 Renault 11 Automatic	https://www.automobile-catalog.com/car/1983/2933690/renault_11_automatic.html
EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-MID84-01	3981	1660	1406	Automobile-Catalog 1984 Renault 11 Automatic since mid-year	https://www.automobile-catalog.com/car/1984/2933945/renault_11_automatic.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-MID84-01	3981	1660	1406	Automobile-Catalog 1984 Renault 11 Automatic since mid-year	https://www.automobile-catalog.com/car/1984/2933945/renault_11_automatic.html
EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-TL-LATE-01	3973	1630	1410	Automobile-Catalog 1985 Renault 11 TL since July 1985	https://www.automobile-catalog.com/car/1985/2934215/renault_11_tl.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-TL-LATE-01	3973	1630	1410	Automobile-Catalog 1985 Renault 11 TL since July 1985	https://www.automobile-catalog.com/car/1985/2934215/renault_11_tl.html
EU-RENAULT-11-PHASE1-HATCHBACK-3D-68PS-GTL-LATE-01	3985	1660	1410	Automobile-Catalog 1985 Renault 11 GTL; Automobile-Catalog 1985 Renault 11 Broadway 1.4	https://www.automobile-catalog.com/car/1985/2934230/renault_11_gtl.html; https://www.automobile-catalog.com/car/1985/2934185/renault_11_broadway_1_4.html
EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-GTL-LATE-01	3985	1660	1410	Automobile-Catalog 1985 Renault 11 GTL; Automobile-Catalog 1985 Renault 11 Broadway 1.4	https://www.automobile-catalog.com/car/1985/2934230/renault_11_gtl.html; https://www.automobile-catalog.com/car/1985/2934185/renault_11_broadway_1_4.html
```

## 5. 下一步优先处理

1. 闭合 Renault 11 `1.4 60/67 PS` 的早期、中期、Phase II 及保险杠外廓。
2. 处理 Renault 11 `1.7 75/80/88 PS` 与 `1.6 D` 的三门、五门及改款分支。
3. 随后批量处理 Renault 5、Super 5。
4. 最后处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 和 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/2933690/renault_11_automatic.html?utm_source=chatgpt.com "1983 Renault 11 Automatic Specs Review (50 kW / 68 PS / 67 hp) (since March 1983 for Europe )"
[2]: https://www.automobile-catalog.com/car/1985/2934215/renault_11_tl.html?utm_source=chatgpt.com "1985 Renault 11 TL Specs Review (50 kW / 68 PS / 67 hp) (since July 1985 for Europe )"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 1. 更新点

* 完成 Renault 11 `1.6 D` Ktype `2027` 的已确认外廓分支。零件目录与车型资料确认该 Ktype 对应 `B/C374`，覆盖三门、五门 Hatchback。([B-Parts][1])
* Phase I 五门车身存在三次已确认变化：早期 `3985 × 1660 × 1400 mm`、1984 年中期 `3981 × 1660 × 1406 mm`、1985 年版本 `3985 × 1660 × 1410 mm`；均复用此前已闭合尺寸组。([汽车目录][2])
* Phase II 五门 GTD 复用既有 `3985 × 1660 × 1405 mm` 尺寸组；Phase II 三门 TD 首次建立 `4047 × 1666 × 1405 mm` 尺寸组。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：48
* PENDING 输入 Ktype：52
* READY 映射行：90
* 已确认尺寸组：56
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
2027_5dr_pre84	2027	Hatchback	Renault 11 Phase I	B374	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-PRE84-01	HIGH	1984年中期更新前五门柴油外廓。	READY
2027_5dr_mid84	2027	Hatchback	Renault 11 Phase I	B374	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-68PS-MID84-01	HIGH	1984年中期至1985年更新前五门柴油外廓。	READY
2027_3dr_latep1	2027	Hatchback	Renault 11 Phase I	C374	3	EU-RENAULT-11-PHASE1-HATCHBACK-3D-STANDARD-01	HIGH	Phase I后期三门TD外廓。	READY
2027_5dr_latep1	2027	Hatchback	Renault 11 Phase I	B374	5	EU-RENAULT-11-PHASE1-HATCHBACK-5D-STANDARD-01	HIGH	Phase I后期五门GTD或Broadway外廓。	READY
2027_3dr_facelift	2027	Hatchback	Renault 11 Phase II	C374	3	EU-RENAULT-11-PHASE2-HATCHBACK-3D-DIESEL-01	HIGH	Phase II三门TD外廓。	READY
2027_5dr_facelift	2027	Hatchback	Renault 11 Phase II	B374	5	EU-RENAULT-11-PHASE2-HATCHBACK-5D-STANDARD-01	HIGH	Phase II五门GTD外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-11-PHASE2-HATCHBACK-3D-DIESEL-01	4047	1666	1405	Automobile-Catalog 1986 Renault 11 TD; Automobile-Catalog 1988 Renault 11 TD	https://www.automobile-catalog.com/car/1986/2935145/renault_11_td.html; https://www.automobile-catalog.com/car/1988/2935145/renault_11_td.html
```

## 5. 下一步优先处理

1. 闭合 Renault 11 `1.4 60/67 PS` 的剩余 Phase I、Phase II 和门数分支。
2. 处理 Renault 11 `1.7 75/80/88 PS` 的三门、五门及改款外廓。
3. 随后批量处理 Renault 5、Super 5。
4. 最后处理 Golf I Cabriolet、Polo II Coupé、Audi 100 C2 和 Fiat Scudo。

推进信号：CONTINUE

[1]: https://www.b-parts.com/auto-parts/body-parts/left-mirror-renault-11-bc37_-16-d-bc374-1983-1984-1985-1986-1987-1988-1989-1990-1991-1992-1993-1994-1995-1012568?srsltid=AfmBOooW8hBY1CsYzdV29cenKM-x9KNbQH-pY_06EQUV9MN0wNktI75c&utm_source=chatgpt.com "Used Left mirror RENAULT 11 (B/C37_) 1.6 D (B/C374) ..."
[2]: https://www.automobile-catalog.com/car/1984/53270/renault_11_gtd.html?utm_source=chatgpt.com "1984 Renault 11 GTD Specs Review (40.5 kW / 55 PS ..."
[3]: https://www.automobile-catalog.com/car/1987/2935130/renault_11_gtd.html?utm_source=chatgpt.com "1987 Renault 11 GTD Specs Review (40.5 kW ..."


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1. 更新点

* 首次闭合 Audi 100 C2 `Typ 43` 2.0 D 四门 Sedan 的改款前、改款后两个外廓。
* Ktype `1966` 跨越 1979 年改款：改款前为 `4680 × 1768 × 1390 mm`，改款后长度变为 `4683 mm`；宽度均明确为不含后视镜。([汽车目录][1])
* 已将 Ktype `1966` 拆分为 `prefl` 与 `facelift` 两条映射。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：49
* PENDING 输入 Ktype：51
* READY 映射行：92
* 已确认尺寸组：58
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1966_prefl	1966	Sedan	Audi 100 C2	Typ 43	4	EU-AUDI-100-C2-SEDAN-4D-PREFL-01	HIGH	1979年改款前2.0 D四门轿车外廓。	READY
1966_facelift	1966	Sedan	Audi 100 C2	Typ 43	4	EU-AUDI-100-C2-SEDAN-4D-FACELIFT-01	HIGH	1979年改款后2.0 D四门轿车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-100-C2-SEDAN-4D-PREFL-01	4680	1768	1390	Audi official archive 1978 Audi 100 GL 5D; Automobile-Catalog 1978 Audi 100 GL 5D	https://www.audi.com/en/photos/detail/audi-100-gl-5d-c2-model-year-1978-37223; https://www.automobile-catalog.com/car/1978/166475/audi_100_gl_5d.html
EU-AUDI-100-C2-SEDAN-4D-FACELIFT-01	4683	1768	1390	Automobile-Catalog 1980 Audi 100 5D; Automoli Audi 100 C2 Typ 43 facelift 2.0 D	https://www.automobile-catalog.com/car/1980/166850/audi_100_5d.html; https://www.automoli.com/us/vehicles/audi/100/100-c2-typ-43-facelift-1979-5182/
```

## 5. 下一步优先处理

1. 闭合 Renault 4 五门乘用车各阶段外廓及 Ktype `1968–1971`。
2. 区分 Renault 4 F4/F6 厢式车，处理 Ktype `1972、1974、1975`。
3. 继续处理 Renault 11 剩余 `1.4`、`1.7` 版本。
4. 随后批量处理 Renault 5、Super 5。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/166475/audi_100_gl_5d.html?utm_source=chatgpt.com "1978 Audi 100 GL 5D Specs Review (51.5 kW / 70 PS ..."


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault 4 后期标准五门乘用车尺寸组。`R1123` 的 845 cc L/TL 与 `R1128` 的 1108 cc GTL 外部三维一致，均为 `3668 × 1485 × 1550 mm`，宽度明确为不含后视镜。([Mecatechnic][1])
* 批量完成 Ktype `1969、1970、1971`，三者复用同一尺寸组，不重复建组。
* Ktype `1968` 覆盖早期不同保险杠和车长阶段，本轮未强行关联后期尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：52
* PENDING 输入 Ktype：48
* READY 映射行：95
* 已确认尺寸组：59
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1969	1969	Hatchback	Renault 4	R1123	5	EU-RENAULT-4-HATCHBACK-5D-STANDARD-01	HIGH	R1123后期五门L或TL车身。	READY
1970	1970	Hatchback	Renault 4	R1123	5	EU-RENAULT-4-HATCHBACK-5D-STANDARD-01	HIGH	R1123五门845 cc车身。	READY
1971	1971	Hatchback	Renault 4	R1128	5	EU-RENAULT-4-HATCHBACK-5D-STANDARD-01	HIGH	R1128五门GTL车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-HATCHBACK-5D-STANDARD-01	3668	1485	1550	Automobile-Catalog 1972 Renault 4 Export; Automobile-Catalog 1980 Renault 4 TL; Automobile-Catalog 1988 Renault 4 GTL Clan	https://www.automobile-catalog.com/car/1972/2924780/renault_4_export.html; https://www.automobile-catalog.com/car/1980/2925035/renault_4_tl.html; https://www.automobile-catalog.com/car/1988/2925155/renault_4_gtl_clan.html
```

## 5. 下一步优先处理

1. 拆分 Ktype `1968` 覆盖的 Renault 4 早期车长及保险杠外廓。
2. 区分 Ktype `1972、1974、1975` 对应的 Renault 4 F4、F6、厢式及带窗车身。
3. 完成 Renault 11 剩余 `1.4、1.7` 版本。
4. 批量处理 Renault 5 与 Super 5。

推进信号：CONTINUE

[1]: https://www.mecatechnic.com/en-GB/b-renault/m-4/motorizations?utm_source=chatgpt.com "Renault 4L engine options"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 1. 更新点

* 完成 Ktype `1968` 的 Renault 4 `R1123` 五门乘用车外廓拆分。
* 1962 年 10 月至 1964 年 8 月为低车高外廓 `3660 × 1485 × 1530 mm`；1964 年 9 月起车高调整为 `1550 mm`；1967 年 10 月改用四速版本外廓后，车长调整为 `3668 mm`。各来源均明确宽度不含后视镜。([汽车目录][1])
* Renault 4 F4/F6 厢式车的官方资料仅完整给出长、宽范围，未给出高度，因此本轮不创建字段不完整的尺寸组。([原版雷诺][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：53
* PENDING 输入 Ktype：47
* READY 映射行：98
* 已确认尺寸组：62
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1968_lowroof	1968	Hatchback	Renault 4	R1123	5	EU-RENAULT-4-R1123-HATCHBACK-5D-LOWROOF-01	HIGH	1962年10月至1964年8月低车高外廓。	READY
1968_mid	1968	Hatchback	Renault 4	R1123	5	EU-RENAULT-4-R1123-HATCHBACK-5D-MID-01	HIGH	1964年9月至1967年9月五门外廓。	READY
1968_late	1968	Hatchback	Renault 4	R1123	5	EU-RENAULT-4-R1123-HATCHBACK-5D-LATE-01	HIGH	1967年10月至1983年9月后期外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-R1123-HATCHBACK-5D-LOWROOF-01	3660	1485	1530	Automobile-Catalog 1962 Renault 4 L	https://www.automobile-catalog.com/car/1962/2924330/renault_4_l.html
EU-RENAULT-4-R1123-HATCHBACK-5D-MID-01	3660	1485	1550	Automobile-Catalog 1964 Renault 4 L since September 1964	https://www.automobile-catalog.com/car/1964/2924480/renault_4_l.html
EU-RENAULT-4-R1123-HATCHBACK-5D-LATE-01	3668	1485	1550	Automobile-Catalog 1967 Renault 4 Luxe since October 1967; Automobile-Catalog 1979 Renault 4	https://www.automobile-catalog.com/car/1967/2924645/renault_4_luxe.html; https://www.automobile-catalog.com/car/1979/2925020/renault_4.html
```

## 5. 下一步优先处理

1. 从 Renault 4 F4/F6 原厂销售手册补齐高度，处理 Ktype `1972、1974、1975`。
2. 完成 Renault 11 剩余 `1.4 60/67 PS` 与 `1.7 75/80/88 PS` 分支。
3. 批量处理 Renault 5 与 Super 5。
4. 处理 Golf I Cabriolet、Polo II Coupé 和 Fiat Scudo 剩余记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1962/2924330/renault_4_l.html?utm_source=chatgpt.com "1962 Renault 4 L Specs Review (19.5 kW / 26.5 PS / 26 hp) (since September 1962 for Europe export)"
[2]: https://theoriginals.renault.com/en/renault-4-fourgonnette "Renault 4 Van - The Originals Museum"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault 4 **F4 短轴厢式车**尺寸组，三维为 `3670 × 1500 × 1710 mm`。Renault 官方资料确认 F4 与加长 F6 是不同物理外廓，F4 官方标称长度、宽度约为 `3.65 × 1.50 m`；详细规格给出完整三维。([原版雷诺][1])
* Ktype `1972` 的 `R2391` 和 Ktype `1975` 的 `R239B` 均关联 F4 尺寸组。车型目录分别确认其为 F4 厢式分支。([Alepoc][2])
* Ktype `1974` 同时覆盖 `R210B` F4 与 `R2370` F6，已拆成两个派生分支；F4 已 READY，F6 因完整高度及宽度口径尚未闭合而继续 PENDING。([AUTODOC][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：55
* PENDING 输入 Ktype：45
* READY 映射行：101
* 已确认尺寸组：63
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1972	1972	Van	Renault 4 Fourgonnette	R2391	3	EU-RENAULT-4-F4-VAN-3D-01	MEDIUM	R2391短轴F4厢式车身。	READY
1974_f4	1974	Van	Renault 4 Fourgonnette	R210B	3	EU-RENAULT-4-F4-VAN-3D-01	MEDIUM	R210B短轴F4厢式车身。	READY
1974_f6	1974	Van	Renault 4 Fourgonnette	R2370	3		LOW	R2370加长F6厢式车身。	PENDING: F6高度及不含后视镜宽度口径未完整确认
1975	1975	Van	Renault 4 Fourgonnette	R239B	3	EU-RENAULT-4-F4-VAN-3D-01	MEDIUM	R239B短轴F4厢式车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-F4-VAN-3D-01	3670	1500	1710	Renault The Originals Renault 4 Fourgonnette; Auta5P Renault 4 F4 1980	https://theoriginals.renault.com/en/renault-4-fourgonnette; https://auta5p.eu/lang/en/katalog/auto.php?idf=Renault-4-F4-25762
```

## 5. 下一步优先处理

1. 补齐 Renault 4 F6 `R2370` 的完整高度与不含后视镜宽度口径。
2. 完成 Renault 11 剩余 `1.4 60/67 PS` 与 `1.7 75/80/88 PS` 分支。
3. 批量处理 Renault 5 与 Super 5 的普通版、门数和运动版外廓。
4. 处理 Golf I Cabriolet、Polo II Coupé、Fiat Scudo 等剩余记录。

推进信号：CONTINUE

[1]: https://theoriginals.renault.com/en/renault-4-fourgonnette?utm_source=chatgpt.com "Renault 4 Van - The Originals Museum"
[2]: https://alepoc.shop/refroidissement-renault-r4/7902-radiateur-de-chauffage-pour-renault-r4-berline-et-fourgonnette.html?utm_source=chatgpt.com "Radiateur de chauffage pour Renault R4 (Berline et Fourgonnette)"
[3]: https://www.auto-doc.ie/car-parts/exhaust-pipes-10415/renault/4/4-box-r21-r23/1974-1-1-2370-210b?utm_source=chatgpt.com "Renault 4 Van 1.1 Exhaust pipes - 34 hp Petrol 25 kW 1976 - 1989 C1E 719 ▷ AUTODOC"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 1. 更新点

* 补齐 Renault 4 F6 `R2370` 加长厢式车的完整尺寸：`3853 × 1532 × 1720 mm`。尺寸表明确区分普通 F4 与长轴 Fourgonnette，`1720 mm` 为车辆空载高度；`R2370` 对应 1.1 L F6 长厢式车。([La 4L de Sylvie][1])
* 原 `1974_f6` 映射由 PENDING 更新为 READY。Ktype `1974` 的 F4、F6 两个物理分支现均已闭合。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：56
* PENDING 输入 Ktype：44
* READY 映射行：102
* 已确认尺寸组：64
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1974_f6	1974	Van	Renault 4 Fourgonnette	R2370	3	EU-RENAULT-4-F6-VAN-3D-01	HIGH	R2370加长F6厢式车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-F6-VAN-3D-01	3853	1532	1720	La 4L de Sylvie Renault 4 dimensions; Mecatechnic Renault 4 engine and body-code catalogue	https://www.la4ldesylvie.fr/dimensions-des-renault-4; https://www.mecatechnic.com/en-GB/b-renault/m-4/motorizations
```

## 5. 下一步优先处理

1. 闭合 Renault 11 `1.4 60/67 PS` 的 Phase I、Phase II 及门数分支。
2. 处理 Renault 11 `1.7 75/80/88 PS` 的普通版与改款外廓。
3. 批量处理 Renault 5、Super 5。
4. 处理 Golf I Cabriolet、Polo II Coupé、Fiat Scudo 等剩余记录。

推进信号：CONTINUE

[1]: https://www.la4ldesylvie.fr/dimensions-des-renault-4 "Dimensions des Renault 4"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 1. 更新点

* 首次闭合 Polo II Coupé 的 **86C 标准车身、GT、G40** 和 **86C 2F 改款后标准车身、GT、G40** 六个尺寸组。
* 改款前标准 Coupé 为 `3655 × 1580 × 1355 mm`；GT 与早期 G40 车高降至 `1335 mm`。1990 年外观改款后，普通 Coupé 车长增至约 `3725 mm`；GT 与 G40 因运动悬架和外部组件分别独立建组。宽度均采用不含后视镜口径。([Volkswagen Newsroom][1])
* 批量完成 Ktype `1950–1959`；跨越 1990 年 10 月改款的 `1956、1957、1958` 已拆分为改款前后物理分支。Polo II 的大改款于 1990 年秋季实施，改款后通常标识为 `86C 2F`。([维基百科][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：66
* PENDING 输入 Ktype：34
* READY 映射行：115
* 已确认尺寸组：70
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1950	1950	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	改款前标准三门Coupé。	READY
1951	1951	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	改款前标准三门Coupé。	READY
1952	1952	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	改款前标准三门Coupé。	READY
1953	1953	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-G40-01	HIGH	改款前GT G40三门外廓。	READY
1954	1954	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	改款前柴油三门Coupé。	READY
1955	1955	Coupe	Polo II facelift	86C 2F	3	EU-VW-POLO-II-86C-2F-COUPE-3D-STANDARD-01	HIGH	改款后1.4 D三门Coupé。	READY
1956_prefl	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	1990年秋季改款前1.0 CAT外廓。	READY
1956_facelift	1956	Coupe	Polo II facelift	86C 2F	3	EU-VW-POLO-II-86C-2F-COUPE-3D-STANDARD-01	HIGH	1990年秋季改款后1.0 CAT外廓。	READY
1957_prefl	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	HIGH	1990年秋季改款前1.3 CAT标准外廓。	READY
1957_facelift	1957	Coupe	Polo II facelift	86C 2F	3	EU-VW-POLO-II-86C-2F-COUPE-3D-STANDARD-01	HIGH	1990年秋季改款后1.3 CAT标准外廓。	READY
1958_prefl	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-3D-GT-01	HIGH	改款前75 PS GT三门外廓。	READY
1958_facelift	1958	Coupe	Polo II facelift	86C 2F	3	EU-VW-POLO-II-86C-2F-COUPE-3D-GT-01	HIGH	改款后75 PS GT三门外廓。	READY
1959	1959	Coupe	Polo II facelift	86C 2F	3	EU-VW-POLO-II-86C-2F-COUPE-3D-G40-01	HIGH	改款后带催化器G40三门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-II-86C-COUPE-3D-STANDARD-01	3655	1580	1355	Volkswagen Newsroom Polo II official vehicle data; Automobile-Catalog 1983 Volkswagen Polo 1.1 CL Formel E	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144; https://www.automobile-catalog.com/car/1983/59570/volkswagen_polo_1_1_cl_formel_e.html
EU-VW-POLO-II-86C-COUPE-3D-GT-01	3655	1580	1335	Automobile-Catalog 1986 Volkswagen Polo Coupe 1.3 GT; Automobile-Catalog 1990 Volkswagen Polo 1.3 GT	https://www.automobile-catalog.com/car/1986/41165/volkswagen_polo_coupe_1_3_gt.html; https://www.automobile-catalog.com/car/1990/56660/volkswagen_polo_1_3_gt.html
EU-VW-POLO-II-86C-COUPE-3D-G40-01	3655	1580	1335	Volkswagen Newsroom Polo II official vehicle data; Automobile-Catalog 1987 Volkswagen Polo Coupe GT G40	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144; https://www.automobile-catalog.com/car/1987/53825/volkswagen_polo_coupe_gt_g40.html
EU-VW-POLO-II-86C-2F-COUPE-3D-STANDARD-01	3725	1570	1350	Auto-Data Volkswagen Polo II Coupe 86C generation; Volkswagen Polo Mk2 facelift reference	https://www.auto-data.net/en/volkswagen-polo-ii-coupe-86c-generation-1861; https://en.wikipedia.org/wiki/Volkswagen_Polo_Mk2
EU-VW-POLO-II-86C-2F-COUPE-3D-GT-01	3720	1570	1340	UltimateSpecs Volkswagen Polo 2F 86C Coupe 1.3 75	https://www.ultimatespecs.com/car-specs/Volkswagen/3014/Volkswagen-Polo-2F-86C-Coupe-13-75.html
EU-VW-POLO-II-86C-2F-COUPE-3D-G40-01	3725	1590	1325	Zwischengas Volkswagen Polo G40 vehicle specifications	https://www.zwischengas.com/en/articles/cars/VW-Polo-G40.html
```

## 5. 下一步优先处理

1. 闭合 Renault 11 剩余 `1.4 60/67 PS` 与 `1.7 75/80/88 PS` 的并行保险杠和改款分支。
2. 批量处理 Renault 5 普通版的三门、五门及阶段外廓。
3. 处理 Renault Super 5 标准版、GT Turbo 和必要门数分支。
4. 最后处理 Golf I Cabriolet、Fiat Scudo 及其余零散记录。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144?utm_source=chatgpt.com "Vehicle data Polo II profile"
[2]: https://en.wikipedia.org/wiki/Volkswagen_Polo_Mk2?utm_source=chatgpt.com "Volkswagen Polo Mk2"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 1. 更新点

* 闭合 Golf I Cabriolet `Type 155` 的 1988 年中期外包围更新后尺寸组：`3890 × 1640 × 1395 mm`。
* Volkswagen 官方档案确认 1988 款开始采用环绕式扰流外包围；更新前车身复用既有 `3815 × 1630 × 1395 mm` 尺寸组，更新后使用本轮新组。([汽车目录][1])
* 完成 Ktype `1943、1944、1946、1947、1948、1949`；跨越更新时间的 Ktype 均拆分为 `pre88` 与 `post88`。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：72
* PENDING 输入 Ktype：28
* READY 映射行：126
* 已确认尺寸组：71
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1943_pre88	1943	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	1988年中期外包围更新前车身。	READY
1943_post88	1943	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	1988年中期外包围更新后车身。	READY
1944_pre88	1944	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	1988年中期外包围更新前车身。	READY
1944_post88	1944	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	1988年中期外包围更新后车身。	READY
1946_pre88	1946	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	1988年中期外包围更新前车身。	READY
1946_post88	1946	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	1988年中期外包围更新后车身。	READY
1947_pre88	1947	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	1988年中期外包围更新前车身。	READY
1947_post88	1947	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	1988年中期外包围更新后车身。	READY
1948_pre88	1948	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-EARLY-01	HIGH	1988年中期外包围更新前GLI车身。	READY
1948_post88	1948	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	1988年中期外包围更新后Sport车身。	READY
1949	1949	Convertible	Golf I Cabriolet	Type 155	2	EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	HIGH	更新后外包围车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-1-CABRIOLET-2D-POST88-01	3890	1640	1395	Volkswagen Newsroom Golf I Cabriolet official archive; Automobile-Catalog 1988 Volkswagen Golf Cabrio 1.8i Sport	https://www.volkswagen-newsroom.com/en/golf-1-cabriolet-19791993-19488; https://www.automobile-catalog.com/car/1988/54695/volkswagen_golf_cabrio_1_8i_sport.html
```

## 5. 下一步优先处理

1. 批量闭合 Renault 5 普通版的早期、后期、三门及五门外廓。
2. 处理 Super 5 标准三门、五门及 GT Turbo 外廓。
3. 完成 Renault 11 剩余 `1.4` 与 `1.7` 版本。
4. 处理 Fiat Scudo 轴距分支及其余零散记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/56255/volkswagen_golf_cabrio_gli.html?utm_source=chatgpt.com "1988 Volkswagen Golf Cabrio GLi Specs Review (82 kW / 112 PS / 110 hp) (up to mid-year 1988 for Europe )"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 1. 更新点

* 首次闭合 Renault Super 5 的标准三门、标准五门和 GT Turbo 三门三个尺寸组。
* 标准三门外廓为 `3591 × 1584 × 1397 mm`，标准五门为 `3651 × 1584 × 1397 mm`；GT Turbo 三门宽体低车身外廓为 `3591 × 1596 × 1367 mm`。所用宽度均明确为不含后视镜口径。([汽车目录][1])
* 批量完成 Ktype `1993–2001`。普通版本按三门、五门拆分；`1995` GT Turbo 和 `1998` 1.7i `C409` 仅保留三门分支。对应车型代码边界与发动机生产区间已核对。([Brembo Parts][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：81
* PENDING 输入 Ktype：19
* READY 映射行：142
* 已确认尺寸组：74
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1993_3dr	1993	Hatchback	Super 5	C402	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C402三门标准外廓。	READY
1993_5dr	1993	Hatchback	Super 5	B402	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B402五门标准外廓。	READY
1994_3dr	1994	Hatchback	Super 5	C403	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C403三门标准外廓。	READY
1994_5dr	1994	Hatchback	Super 5	B403	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B403五门标准外廓。	READY
1995	1995	Hatchback	Super 5	C405	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-GT-TURBO-01	HIGH	C405三门GT Turbo宽体低车身外廓。	READY
1996_3dr	1996	Hatchback	Super 5	C40M	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C40M三门标准外廓。	READY
1996_5dr	1996	Hatchback	Super 5	B40M	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B40M五门标准外廓。	READY
1997_3dr	1997	Hatchback	Super 5	C40J	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C40J三门标准外廓。	READY
1997_5dr	1997	Hatchback	Super 5	B40J	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B40J五门标准外廓。	READY
1998	1998	Hatchback	Super 5	C409	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C409三门1.7i外廓。	READY
1999_3dr	1999	Hatchback	Super 5		3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	1.7三门标准外廓。	READY
1999_5dr	1999	Hatchback	Super 5		5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	1.7五门标准外廓。	READY
2000_3dr	2000	Hatchback	Super 5	C404	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C404三门柴油外廓。	READY
2000_5dr	2000	Hatchback	Super 5	B404	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B404五门柴油外廓。	READY
2001_3dr	2001	Hatchback	Super 5	C408	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	C408三门1.7催化版外廓。	READY
2001_5dr	2001	Hatchback	Super 5	B408	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	B408五门1.7催化版外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	3591	1584	1397	Automobile-Catalog 1987 Renault 5 GTS; Automobile-Catalog 1990 Renault 5 GTX	https://www.automobile-catalog.com/car/1987/2939045/renault_5_gts.html; https://www.automobile-catalog.com/car/1990/2939105/renault_5_gtx.html
EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	3651	1584	1397	Automobile-Catalog 1987 Renault 5 GTS 5-Door; Automobile-Catalog 1987 Renault 5 GTX 5-Door; Automobile-Catalog 1987 Renault 5 GTD 5-Door	https://www.automobile-catalog.com/car/1987/2938520/renault_5_gts_5-door.html; https://www.automobile-catalog.com/car/1987/2939120/renault_5_gtx_5-door.html; https://www.automobile-catalog.com/car/1987/2939315/renault_5_gtd_5-door.html
EU-RENAULT-SUPER-5-HATCHBACK-3D-GT-TURBO-01	3591	1596	1367	Automobile-Catalog 1987 Renault 5 GT Turbo	https://www.automobile-catalog.com/car/1987/2939195/renault_5_gt_turbo.html
```

## 5. 下一步优先处理

1. 处理 Super 5 `1.0、1.1` Ktype `1989–1991`，区分三门、五门及不同车高外廓。
2. 批量闭合第一代 Renault 5 普通版本 Ktype `1976–1986`。
3. 完成 Renault 11 剩余 `1.4` 与 `1.7` Ktype。
4. 处理 Fiat Scudo 轴距分支及剩余零散记录。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/2939105/renault_5_gtx.html?utm_source=chatgpt.com "1990 Renault 5 GTX Specs Review (66 kW / 90 PS / 89 hp) ..."
[2]: https://www.bremboparts.com/europe/en/catalogue/renault-super-5-b-c40-1-4-b-c403/000001994-1?utm_source=chatgpt.com "Pads and Discs for RENAULT SUPER 5 (B/C40_) 1.4 (B/C403)"


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / 下一步 ---
## 1. 更新点

* 闭合 Super 5 低功率三门、五门外廓：三门 `3591 × 1584 × 1389 mm`，五门 `3651 × 1584 × 1389 mm`，宽度均不含后视镜。Renault 官方资料确认 Super 5 同时提供三门和加长约 60 mm 的五门版本。([汽车目录][1])
* 完成 Ktype `1989` 的三门、五门分支。
* 完成 Ktype `1991`：同一 `1.1 34 kW` 发动机覆盖低车高 L/GL 外廓及较高的 GTL 外廓，因此按门数和外廓拆分为四条映射；GTL 分支复用既有标准尺寸组，不重复建组。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：83
* PENDING 输入 Ktype：17
* READY 映射行：148
* 已确认尺寸组：76
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1989_3dr	1989	Hatchback	Super 5		3	EU-RENAULT-SUPER-5-HATCHBACK-3D-LOWPOWER-01	HIGH	1.0低功率三门外廓。	READY
1989_5dr	1989	Hatchback	Super 5		5	EU-RENAULT-SUPER-5-HATCHBACK-5D-LOWPOWER-01	HIGH	1.0低功率五门外廓。	READY
1991_3dr_low	1991	Hatchback	Super 5		3	EU-RENAULT-SUPER-5-HATCHBACK-3D-LOWPOWER-01	HIGH	L或GL低车高三门外廓。	READY
1991_3dr_gtl	1991	Hatchback	Super 5		3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	GTL标准车高三门外廓。	READY
1991_5dr_low	1991	Hatchback	Super 5		5	EU-RENAULT-SUPER-5-HATCHBACK-5D-LOWPOWER-01	HIGH	L或GL低车高五门外廓。	READY
1991_5dr_gtl	1991	Hatchback	Super 5		5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	GTL标准车高五门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-SUPER-5-HATCHBACK-3D-LOWPOWER-01	3591	1584	1389	Automobile-Catalog 1985 Renault 5 TC; Automobile-Catalog 1984 Renault 5 L	https://www.automobile-catalog.com/car/1985/64100/renault_5_tc.html; https://www.automobile-catalog.com/car/1984/2938535/renault_5_l.html
EU-RENAULT-SUPER-5-HATCHBACK-5D-LOWPOWER-01	3651	1584	1389	Automobile-Catalog 1985 Renault 5 TC 5-Door; Automobile-Catalog 1985 Renault 5 GL 5-Door	https://www.automobile-catalog.com/car/1985/51650/renault_5_1_0_tc_5-door.html; https://www.automobile-catalog.com/car/1985/2938445/renault_5_gl_5-door.html
```

## 5. 下一步优先处理

1. 拆分 Ktype `1990` 的标准外廓与后期 Campus 外廓。
2. 批量闭合第一代 Renault 5 Ktype `1976、1977、1979–1986`。
3. 完成 Renault 11 剩余 Ktype `2016、2017、2023、2024、2026`。
4. 最后处理 Fiat Scudo Ktype `1978` 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/64100/renault_5_tc.html?utm_source=chatgpt.com "1985 Renault 5 TC Specs Review (31 kW / 42 PS ..."
[2]: https://www.automobile-catalog.com/car/1984/2938535/renault_5_l.html?utm_source=chatgpt.com "1984 Renault 5 L Specs Review (34.5 kW / 47 PS / 46 hp) ..."


--- 发送 / 继续到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / 下一步 ---
## 1. 更新点

* 闭合 Super 5 Ktype `1990` 的标准车身与后期 Five/Campus 外廓。
* 1990 年 6 月前的标准三门、五门车身直接复用既有尺寸组。
* 后期 Five/Campus 的车身宽度和高度发生变化，三门为 `3591 × 1564 × 1387 mm`，五门为 `3651 × 1564 × 1387 mm`，因此首次创建两个尺寸组。宽度均为不含后视镜口径。([汽车目录][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：84
* PENDING 输入 Ktype：16
* READY 映射行：152
* 已确认尺寸组：78
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1990_3dr_standard	1990	Hatchback	Super 5	C401	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-STANDARD-01	HIGH	1990年6月前标准三门外廓。	READY
1990_5dr_standard	1990	Hatchback	Super 5	B401	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-STANDARD-01	HIGH	1990年6月前标准五门外廓。	READY
1990_3dr_campus	1990	Hatchback	Super 5	C401	3	EU-RENAULT-SUPER-5-HATCHBACK-3D-CAMPUS-01	HIGH	后期Five或Campus三门外廓。	READY
1990_5dr_campus	1990	Hatchback	Super 5	B401	5	EU-RENAULT-SUPER-5-HATCHBACK-5D-CAMPUS-01	HIGH	后期Five或Campus五门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-SUPER-5-HATCHBACK-3D-CAMPUS-01	3591	1564	1387	Automobile-Catalog 1992 Renault 5 Five Campus; Automobile-Catalog Renault 5 phase-II 3-door specifications	https://www.automobile-catalog.com/car/1992/2938805/renault_5_five_campus.html; https://www.automobile-catalog.com/make/renault/5_2gen/5_2gen_2/1992.html
EU-RENAULT-SUPER-5-HATCHBACK-5D-CAMPUS-01	3651	1564	1387	Automobile-Catalog 1990 Renault 5 Five Campus 5-Door; Automobile-Catalog Renault 5 phase-II 5-door specifications	https://www.automobile-catalog.com/car/1990/2938820/renault_5_five_campus_5-door.html; https://www.automobile-catalog.com/make/renault/5_2gen/5_2gen_5d_2/1992.html
```

## 5. 下一步优先处理

1. 批量闭合第一代 Renault 5 Ktype `1976、1977、1979–1986` 的普通版外廓。
2. 完成 Renault 11 Ktype `2016、2017、2023、2024、2026`。
3. 处理 Fiat Scudo Ktype `1978` 的短轴、长轴及车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/renault/5_2gen/5_2gen_2/1992.html?utm_source=chatgpt.com "1992 Renault 5 2gen/II 3-Door Hatchback full range specs"


--- 发送 / 继续到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / 下一步 ---
## 1. 更新点

* 首次闭合第一代 Renault 5 的六个高复用外廓组：1982–1983 年中期标准三门/五门、同期宽体三门/五门，以及 1983 年中期更新后的三门/五门。
* 1982 年标准外廓为 `3521 × 1525 × 1410 mm`；GTL/Automatic 宽体外廓为 `3521 × 1549 × 1410 mm`；1983 年中期更新后为 `3531 × 1525 × 1410 mm`。所有宽度均明确为不含后视镜。([汽车目录][1])
* 完成 Ktype `1977、1980、1985、1986`。其中 `1980` 的 1.1 版本同时覆盖 TL 标准外廓与 GTL 宽体外廓；`1986` 的 1.4 63 PS TS/TX 仅确认三门分支。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：88
* PENDING 输入 Ktype：12
* READY 映射行：168
* 已确认尺寸组：84
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1977_3dr_pre83	1977	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	1983年中期更新前标准三门外廓。	READY
1977_5dr_pre83	1977	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-STANDARD-PRE83-01	HIGH	1983年中期更新前标准五门外廓。	READY
1977_3dr_facelift	1977	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后三门外廓。	READY
1977_5dr_facelift	1977	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后五门外廓。	READY
1980_3dr_tl_pre83	1980	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	更新前TL标准三门外廓。	READY
1980_5dr_tl_pre83	1980	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-STANDARD-PRE83-01	HIGH	更新前TL标准五门外廓。	READY
1980_3dr_gtl_pre83	1980	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-WIDE-PRE83-01	MEDIUM	更新前GTL宽体三门外廓。	READY
1980_5dr_gtl_pre83	1980	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-WIDE-PRE83-01	MEDIUM	更新前GTL宽体五门外廓。	READY
1980_3dr_facelift	1980	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后三门外廓。	READY
1980_5dr_facelift	1980	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后五门外廓。	READY
1985_3dr_pre83	1985	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-WIDE-PRE83-01	HIGH	1983年中期更新前Automatic宽体三门外廓。	READY
1985_5dr_pre83	1985	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-WIDE-PRE83-01	HIGH	1983年中期更新前Automatic宽体五门外廓。	READY
1985_3dr_facelift	1985	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后Automatic三门外廓。	READY
1985_5dr_facelift	1985	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后Automatic五门外廓。	READY
1986_3dr_pre83	1986	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	1983年中期更新前TS三门外廓。	READY
1986_3dr_facelift	1986	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后TS或TX三门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	3521	1525	1410	Automobile-Catalog 1982 Renault 5; Automobile-Catalog 1982 Renault 5 TL; Automobile-Catalog 1982 Renault 5 TS	https://www.automobile-catalog.com/car/1982/50300/renault_5.html; https://www.automobile-catalog.com/car/1982/2928020/renault_5_tl.html; https://www.automobile-catalog.com/car/1982/2928095/renault_5_ts.html
EU-RENAULT-5-I-HATCHBACK-5D-STANDARD-PRE83-01	3521	1525	1410	Automobile-Catalog 1982 Renault 5; Automobile-Catalog 1982 Renault 5 TL	https://www.automobile-catalog.com/car/1982/50300/renault_5.html; https://www.automobile-catalog.com/car/1982/2928020/renault_5_tl.html
EU-RENAULT-5-I-HATCHBACK-3D-WIDE-PRE83-01	3521	1549	1410	Automobile-Catalog 1983 Renault 5 GTL; Automobile-Catalog 1983 Renault 5 Automatic	https://www.automobile-catalog.com/car/1983/2928050/renault_5_gtl_5-speed.html; https://www.automobile-catalog.com/car/1983/2928110/renault_5_automatic.html
EU-RENAULT-5-I-HATCHBACK-5D-WIDE-PRE83-01	3521	1549	1410	Automobile-Catalog 1983 Renault 5 GTL; Automobile-Catalog 1983 Renault 5 Automatic	https://www.automobile-catalog.com/car/1983/2928050/renault_5_gtl_5-speed.html; https://www.automobile-catalog.com/car/1983/2928110/renault_5_automatic.html
EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	3531	1525	1410	Automobile-Catalog 1983 Renault 5 since mid-year; Automobile-Catalog 1983 Renault 5 TS; Automobile-Catalog 1984 Renault 5 Automatic	https://www.automobile-catalog.com/car/1983/2928425/renault_5.html; https://www.automobile-catalog.com/car/1983/2928395/renault_5_ts.html; https://www.automobile-catalog.com/car/1984/2928455/renault_5_automatic.html
EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	3531	1525	1410	Automobile-Catalog 1983 Renault 5 since mid-year; Automobile-Catalog 1984 Renault 5 Automatic	https://www.automobile-catalog.com/car/1983/2928425/renault_5.html; https://www.automobile-catalog.com/car/1984/2928455/renault_5_automatic.html
```

## 5. 下一步优先处理

1. 完成第一代 Renault 5 Ktype `1976、1979、1981、1982、1983、1984` 的早期、1979 更新及1983更新分支。
2. 完成 Renault 11 Ktype `2016、2017、2023、2024、2026`。
3. 最后处理 Fiat Scudo Ktype `1978` 的短轴、长轴和必要车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1982/50300/renault_5.html?utm_source=chatgpt.com "1982 Renault 5 Specs Review (27 kW / 37 PS / 36 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1982/2928020/renault_5_tl.html?utm_source=chatgpt.com "1982 Renault 5 TL Specs Review (33 kW / 45 PS / 44 hp) (for Europe )"


--- 发送 / 继续到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 24 / 下一步 ---
## 1. 更新点

* 闭合第一代 Renault 5 剩余 Ktype `1976、1979、1981–1984`。新增早期标准、1979 年中期标准、早期宽体及 1979 年中期宽体共 6 个门数尺寸组；1981 年 10 月后及 1983 年中期后的分支直接复用既有尺寸组。各尺寸来源明确标注宽度不含后视镜。([汽车目录][1])
* Ktype `1976、1979` 覆盖早期三门、1979 年后新增五门、1981 年车高更新及 1983 年中期外廓更新，均已按物理分支拆分。
* Ktype `1981–1983` 的 GTL/Automatic 宽体外廓在 1979 年中期、1981 年 10 月及 1983 年中期发生变化；Ktype `1984` 的 TS 分支仅对应三门车身。([汽车目录][2])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：94
* PENDING 输入 Ktype：6
* READY 映射行：203
* 已确认尺寸组：90
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1976_3dr_early	1976	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-STANDARD-01	HIGH	1979年中期更新前标准三门外廓。	READY
1976_3dr_post79	1976	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-STANDARD-01	HIGH	1979年中期至1981年9月标准三门外廓。	READY
1976_5dr_post79	1976	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-POST79-STANDARD-01	HIGH	1979年中期至1981年9月标准五门外廓。	READY
1976_3dr_post81	1976	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	1981年10月至1983年中期标准三门外廓。	READY
1976_5dr_post81	1976	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-STANDARD-PRE83-01	HIGH	1981年10月至1983年中期标准五门外廓。	READY
1976_3dr_facelift	1976	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后三门外廓。	READY
1976_5dr_facelift	1976	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后五门外廓。	READY
1979_3dr_early	1979	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-STANDARD-01	HIGH	1979年中期更新前TL三门外廓。	READY
1979_3dr_post79	1979	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-STANDARD-01	HIGH	1979年中期至1981年9月TL三门外廓。	READY
1979_5dr_post79	1979	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-POST79-STANDARD-01	HIGH	1979年中期至1981年9月TL五门外廓。	READY
1979_3dr_post81	1979	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	1981年10月至1983年中期TL三门外廓。	READY
1979_5dr_post81	1979	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-STANDARD-PRE83-01	HIGH	1981年10月至1983年中期TL五门外廓。	READY
1979_3dr_facelift	1979	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后TL三门外廓。	READY
1979_5dr_facelift	1979	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后TL五门外廓。	READY
1981_3dr_early	1981	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-WIDE-01	HIGH	1979年中期更新前GTL宽体三门外廓。	READY
1981_3dr_post79	1981	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-WIDE-01	HIGH	1979年中期后GTL宽体三门外廓。	READY
1981_5dr_post79	1981	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-POST79-WIDE-01	HIGH	1979年中期后GTL宽体五门外廓。	READY
1982_3dr_early	1982	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-WIDE-01	HIGH	1979年中期更新前GTL宽体三门外廓。	READY
1982_3dr_post79	1982	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-WIDE-01	HIGH	1979年中期至1981年9月GTL宽体三门外廓。	READY
1982_5dr_post79	1982	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-POST79-WIDE-01	HIGH	1979年中期至1981年9月GTL宽体五门外廓。	READY
1982_3dr_post81	1982	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-WIDE-PRE83-01	HIGH	1981年10月至1983年中期GTL宽体三门外廓。	READY
1982_5dr_post81	1982	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-WIDE-PRE83-01	HIGH	1981年10月至1983年中期GTL宽体五门外廓。	READY
1982_3dr_facelift	1982	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后GTL三门外廓。	READY
1982_5dr_facelift	1982	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后GTL五门外廓。	READY
1983_3dr_early	1983	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-WIDE-01	HIGH	1979年中期更新前Automatic宽体三门外廓。	READY
1983_3dr_post79	1983	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-WIDE-01	HIGH	1979年中期至1981年9月Automatic宽体三门外廓。	READY
1983_5dr_post79	1983	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-POST79-WIDE-01	HIGH	1979年中期至1981年9月Automatic宽体五门外廓。	READY
1983_3dr_post81	1983	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-WIDE-PRE83-01	HIGH	1981年10月至1983年中期Automatic宽体三门外廓。	READY
1983_5dr_post81	1983	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-WIDE-PRE83-01	HIGH	1981年10月至1983年中期Automatic宽体五门外廓。	READY
1983_3dr_facelift	1983	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后Automatic三门外廓。	READY
1983_5dr_facelift	1983	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-FACELIFT-01	HIGH	1983年中期更新后Automatic五门外廓。	READY
1984_early	1984	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-EARLY-STANDARD-01	HIGH	1979年中期更新前TS三门外廓。	READY
1984_post79	1984	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-POST79-STANDARD-01	HIGH	1979年中期至1981年9月TS三门外廓。	READY
1984_post81	1984	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-STANDARD-PRE83-01	HIGH	1981年10月至1983年中期TS三门外廓。	READY
1984_facelift	1984	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-FACELIFT-01	HIGH	1983年中期更新后TS三门外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-5-I-HATCHBACK-3D-EARLY-STANDARD-01	3506	1525	1400	Automobile-Catalog 1972 Renault 5 L 850; Automobile-Catalog 1979 Renault 5 TS up to July 1979	https://www.automobile-catalog.com/car/1972/2927675/renault_5_l_850.html; https://www.automobile-catalog.com/car/1979/2927870/renault_5_ts.html
EU-RENAULT-5-I-HATCHBACK-3D-POST79-STANDARD-01	3521	1525	1400	Automobile-Catalog 1979 Renault 5 since mid-year; Automobile-Catalog 1979 Renault 5 TL since mid-year; Automobile-Catalog 1979 Renault 5 TS since July 1979	https://www.automobile-catalog.com/car/1979/2928005/renault_5.html; https://www.automobile-catalog.com/car/1979/37685/renault_5_tl.html; https://www.automobile-catalog.com/car/1979/2927945/renault_5_ts.html
EU-RENAULT-5-I-HATCHBACK-5D-POST79-STANDARD-01	3521	1525	1400	Automobile-Catalog 1979 Renault 5 since mid-year; Automobile-Catalog 1979 Renault 5 TL since mid-year	https://www.automobile-catalog.com/car/1979/2928005/renault_5.html; https://www.automobile-catalog.com/car/1979/37685/renault_5_tl.html
EU-RENAULT-5-I-HATCHBACK-3D-EARLY-WIDE-01	3506	1549	1395	Automobile-Catalog 1979 Renault 5 GTL up to July 1979; Automobile-Catalog 1979 Renault 5 Automatic 1300 up to July 1979	https://www.automobile-catalog.com/car/1979/37445/renault_5_gtl.html; https://www.automobile-catalog.com/car/1979/34850/renault_5_autatic_1300.html
EU-RENAULT-5-I-HATCHBACK-3D-POST79-WIDE-01	3521	1549	1400	Automobile-Catalog 1979 Renault 5 GTL since July 1979; Automobile-Catalog 1979 Renault 5 Automatic since July 1979	https://www.automobile-catalog.com/car/1979/2927930/renault_5_gtl.html; https://www.automobile-catalog.com/car/1979/2927960/renault_5_automatic.html
EU-RENAULT-5-I-HATCHBACK-5D-POST79-WIDE-01	3521	1549	1400	Automobile-Catalog 1979 Renault 5 GTL since July 1979; Automobile-Catalog 1979 Renault 5 Automatic since July 1979	https://www.automobile-catalog.com/car/1979/2927930/renault_5_gtl.html; https://www.automobile-catalog.com/car/1979/2927960/renault_5_automatic.html
```

## 5. 下一步优先处理

1. 完成 Renault 11 Ktype `2016、2017、2023、2024、2026` 的普通版、门数及 Phase I/II 分支。
2. 闭合 Fiat Scudo Ktype `1978` 的短轴、长轴及必要车顶分支。
3. PENDING 清零后立即执行一次轻量机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1972/2927675/renault_5_l_850.html?utm_source=chatgpt.com "1972 Renault 5 (L) 850 Specs Review (26.5 kW / 36 PS / 36 hp) (since February 1972 for Europe export)"
[2]: https://www.automobile-catalog.com/car/1979/37445/renault_5_gtl.html?utm_source=chatgpt.com "1979 Renault 5 GTL Specs Review (31 kW / 42 PS / 42 hp) (up to July 1979 for Europe )"


--- 发送 / 继续到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 已打开消息操作菜单，但没有找到【在新聊天中分支】


--- 发送 / checkpoint 续跑到 Round 26 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 27 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 发送 / checkpoint 续跑到 Round 28 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 28 ---
【任务名称】
【全量表更新】all 第 1901-2000 行

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
all 第 1901-2000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Passat b2 variant	1.6 TD	Kombi	Frontantrieb	Diesel	51	70	Apr 1982	Mar 1988	2024-03-01	1936
VW	Passat b1 variant	1.3	Kombi	Frontantrieb	Benzin	40	55	May 1973	Jul 1980	2024-03-01	1937
VW	Passat b1 variant	1.5	Kombi	Frontantrieb	Benzin	55	75	Oct 1973	Aug 1975	2024-03-01	1938
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	55	75	Feb 1976	Jul 1980	2024-03-01	1939
Fiat	Grande punto	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Sep 2010	-	2024-03-01	1940
VW	Passat b1 variant	1.6	Kombi	Frontantrieb	Benzin	63	85	Aug 1975	Jul 1980	2024-03-01	1941
VW	Passat b1 variant	1.5 D	Kombi	Frontantrieb	Diesel	37	50	Feb 1977	Jul 1980	2024-03-01	1942
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	53	72	Apr 1986	Feb 1990	2024-03-01	1943
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	55	75	Aug 1983	Apr 1992	2024-03-01	1944
VW	Golf i	1.6	Cabriolet	Frontantrieb	Benzin	81	110	Aug 1979	Jul 1982	2024-03-01	1945
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	66	90	Aug 1983	Sep 1992	2024-03-01	1946
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	70	95	Aug 1983	Apr 1993	2024-03-01	1947
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	82	112	Aug 1982	Dec 1989	2024-03-01	1948
VW	Golf i	1.8	Cabriolet	Frontantrieb	Benzin	72	98	Aug 1989	Mar 1993	2024-03-01	1949
VW	Polo	1	Coupe	Frontantrieb	Benzin	29	40	May 1982	Oct 1986	2024-03-01	1950
VW	Polo	1.1	Coupe	Frontantrieb	Benzin	37	50	Oct 1981	Jul 1983	2024-03-01	1951
VW	Polo	1.3	Coupe	Frontantrieb	Benzin	44	60	Oct 1981	Jul 1983	2024-03-01	1952
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	85	115	Jan 1987	Aug 1990	2024-03-01	1953
VW	Polo	1.3 D	Coupe	Frontantrieb	Diesel	33	45	Aug 1986	Aug 1990	2024-03-01	1954
VW	Polo	1.4 D	Coupe	Frontantrieb	Diesel	35	48	Aug 1990	Sep 1994	2024-03-01	1955
VW	Polo	1.0 CAT	Coupe	Frontantrieb	Benzin	33	45	Aug 1989	Sep 1994	2024-03-01	1956
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	40	55	Jul 1987	Aug 1994	2024-03-01	1957
VW	Polo	1.3 CAT	Coupe	Frontantrieb	Benzin	55	75	Oct 1989	Sep 1994	2024-03-01	1958
VW	Polo	1.3 G40	Coupe	Frontantrieb	Benzin	83	113	Aug 1990	Sep 1994	2024-03-01	1959
Ford	Fiesta ii	1.6 XR2	Schrägheck	Frontantrieb	Benzin	71	97	Apr 1984	Feb 1989	2024-03-01	1960
Ford	Escort v turnier	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Feb 1993	Jan 1995	2024-03-01	1962
Ford	Escort v turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	66	90	Sep 1992	Jan 1995	2024-03-01	1963
Ford	Escort v turnier	1.8 I 16V	Kombi	Frontantrieb	Benzin	96	130	Feb 1993	Jan 1995	2024-03-01	1964
Audi	100	2.0 D	Stufenheck	Frontantrieb	Diesel	51	70	Aug 1978	Jul 1982	2024-03-01	1966
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	55	75	Aug 1982	Dec 1987	2024-03-01	1967
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	19	26	Oct 1962	Sep 1983	2024-03-01	1968
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	21	29	Oct 1983	Oct 1988	2024-03-01	1969
Renault	4	0.8	Schrägheck	Frontantrieb	Benzin	25	34	Sep 1971	Dec 1988	2024-03-01	1970
Renault	4	1.1	Schrägheck	Frontantrieb	Benzin	25	34	Jun 1978	Jun 1990	2024-03-01	1971
Renault	4	0.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	21	29	Apr 1983	Jul 1989	2024-03-01	1972
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	25	34	Oct 1976	Jul 1989	2024-03-01	1974
Renault	4	1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	26	35	Jul 1982	May 1989	2024-03-01	1975
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	26	35	Oct 1972	Aug 1984	2024-03-01	1976
Renault	5	0.8	Schrägheck	Frontantrieb	Benzin	27	37	Jan 1982	Dec 1984	2024-03-01	1977
Fiat	Scudo	2.0 D Multijet	Bus	Frontantrieb	Diesel	120	163	Jul 2010	Mar 2016	2024-03-01	1978
Renault	5	1	Schrägheck	Frontantrieb	Benzin	32	44	Jan 1972	Dec 1985	2024-03-01	1979
Renault	5	1.1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1980	Dec 1985	2024-03-01	1980
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	31	42	Sep 1976	Sep 1979	2024-03-01	1981
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	33	45	Jun 1979	Sep 1984	2024-03-01	1982
Renault	5	1.3 Automatik	Schrägheck	Frontantrieb	Benzin	40	54	Jun 1979	Sep 1984	2024-03-01	1983
Renault	5	1.3	Schrägheck	Frontantrieb	Benzin	47	64	Sep 1975	Sep 1984	2024-03-01	1984
Renault	5	1.4 Automatik	Schrägheck	Frontantrieb	Benzin	43	59	Jun 1982	Sep 1984	2024-03-01	1985
Renault	5	1.4	Schrägheck	Frontantrieb	Benzin	46	63	Jan 1982	Dec 1985	2024-03-01	1986
Renault	5	1.4 Alpine A5	Schrägheck	Frontantrieb	Benzin	68	93	Sep 1977	Sep 1981	2024-03-01	1987
Renault	5	1.4 Alpine Turbo	Schrägheck	Frontantrieb	Benzin	79	108	Oct 1981	Jan 1985	2024-03-01	1988
Renault	Super 5	1	Schrägheck	Frontantrieb	Benzin	30	41	Oct 1984	Oct 1988	2024-03-01	1989
Renault	Super 5	1.1	Schrägheck	Frontantrieb	Benzin	33	45	Jan 1986	Mar 1995	2024-03-01	1990
Renault	Super 5	1.1	Schrägheck	Frontantrieb	Benzin	34	46	Oct 1984	Oct 1988	2024-03-01	1991
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	43	59	Oct 1984	Jun 1988	2024-03-01	1993
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Oct 1984	Jul 1989	2024-03-01	1994
Renault	Super 5	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	88	120	Apr 1985	Aug 1990	2024-03-01	1995
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1987	Aug 1990	2024-03-01	1996
Renault	Super 5	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Jun 1987	Jul 1989	2024-03-01	1997
Renault	Super 5	1.7 I	Schrägheck	Frontantrieb	Benzin	69	94	Oct 1986	Aug 1991	2024-03-01	1998
Renault	Super 5	1.7	Schrägheck	Frontantrieb	Benzin	64	87	Jun 1987	Mar 1995	2024-03-01	1999
Renault	Super 5	1.6 D	Schrägheck	Frontantrieb	Diesel	40	55	Aug 1985	Dec 1996	2024-03-01	2000
Renault	Super 5	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1986	Mar 1995	2024-03-01	2001
Renault	12	1.3	Stufenheck	Frontantrieb	Benzin	40	54	Oct 1969	Aug 1980	2024-03-01	2002
Renault	12	1.3 TS	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1972	Aug 1980	2024-03-01	2003
Renault	12	1.3	Kombi	Frontantrieb	Benzin	40	54	Oct 1970	Aug 1980	2024-03-01	2004
Renault	9	1.1	Stufenheck	Frontantrieb	Benzin	35	48	Sep 1981	May 1987	2024-03-01	2005
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	44	60	Dec 1981	Dec 1988	2024-03-01	2006
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	49	67	Sep 1985	Dec 1988	2024-03-01	2007
Renault	9	1.4 Automatik	Stufenheck	Frontantrieb	Benzin	50	68	Sep 1981	Dec 1985	2024-03-01	2008
Renault	9	1.4	Stufenheck	Frontantrieb	Benzin	53	72	Sep 1981	Dec 1985	2024-03-01	2009
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	54	73	Oct 1986	Dec 1988	2024-03-01	2010
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1986	Dec 1988	2024-03-01	2011
Renault	9	1.7	Stufenheck	Frontantrieb	Benzin	59	80	Sep 1984	Dec 1989	2024-03-01	2012
Renault	9	1.6 D	Stufenheck	Frontantrieb	Diesel	40	55	Oct 1982	Dec 1988	2024-03-01	2013
Renault	11	1.1	Schrägheck	Frontantrieb	Benzin	35	48	Mar 1983	Jun 1986	2024-03-01	2014
Renault	11	1.2	Schrägheck	Frontantrieb	Benzin	40	55	Oct 1984	Dec 1988	2024-03-01	2015
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1983	Dec 1988	2024-03-01	2016
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	49	67	Mar 1983	Dec 1988	2024-03-01	2017
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	50	68	Mar 1983	Dec 1985	2024-03-01	2018
Renault	11	1.4	Schrägheck	Frontantrieb	Benzin	53	72	May 1983	Dec 1985	2024-03-01	2019
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	77	105	Apr 1984	Dec 1986	2024-03-01	2020
Renault	11	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	85	115	Oct 1986	Dec 1988	2024-03-01	2021
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1986	Dec 1988	2024-03-01	2022
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1984	Dec 1988	2024-03-01	2023
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	59	80	Oct 1983	Dec 1987	2024-03-01	2024
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	64	87	Jun 1987	Dec 1988	2024-03-01	2025
Renault	11	1.7	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1986	Dec 1988	2024-03-01	2026
Renault	11	1.6 D	Schrägheck	Frontantrieb	Diesel	40	55	Aug 1983	Dec 1988	2024-03-01	2027
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	42	57	May 1976	Jan 1980	2024-03-01	2028
Renault	14	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Jan 1980	Dec 1983	2024-03-01	2029
Renault	14	1.4	Schrägheck	Frontantrieb	Benzin	52	71	Sep 1979	Jun 1983	2024-03-01	2030
Renault	16	1.6 TL	Schrägheck	Frontantrieb	Benzin	48	65	Jan 1971	Aug 1980	2024-03-01	2031
Renault	18	1.4	Stufenheck	Frontantrieb	Benzin	47	64	Apr 1978	Jul 1986	2024-03-01	2032
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	80	109	Oct 1980	Sep 1982	2024-03-01	2033
Renault	18	1.6 Turbo	Stufenheck	Frontantrieb	Benzin	92	125	Oct 1982	Jul 1986	2024-03-01	2034
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	54	73	Apr 1982	Jul 1986	2024-03-01	2035
Renault	18	1.6	Stufenheck	Frontantrieb	Benzin	58	79	Apr 1978	Sep 1982	2024-03-01	2036
Renault	18	2.1 Diesel	Stufenheck	Frontantrieb	Diesel	49	67	Nov 1981	Jul 1986	2024-03-01	2037
Renault	18	1.4	Kombi	Frontantrieb	Benzin	47	64	May 1979	Jul 1986	2024-03-01	2038
Renault	18	1.6	Kombi	Frontantrieb	Benzin	54	73	Jan 1982	Jul 1986	2024-03-01	2039


--- 新建对话（分支降级） / Round 28 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a68fab8-17fc-83ec-a318-2b6b343ccbfb
新对话：https://chatgpt.com/c/6a6ea8a0-d6d4-83e9-a690-0e1ecafb0a2e

--- Round 28 / checkpoint 续跑 ---
## 更新点

* 已闭合 Passat B2 Variant、Grande Punto 3/5 门、Golf I Cabriolet 普通车身/Clipper 套件，以及 Polo II Coupe 普通、GT、G40 与 2F 改款分支。VW 官方资料确认了 Passat B2、Golf Cabriolet、Polo II 的厂内代码和基础外廓；具体版本尺寸使用直接车型规格页闭合。([Volkswagen Newsroom][1])
* Passat B1 Type 33 Variant 暂不建组：VW 官方代际尺寸与逐年 Variant 规格在长度、宽度和高度上存在实质差异，当前无法确认各 Ktype 应采用的外廓边界。([Volkswagen Newsroom][2])

## 当前批次进度

* 已研究输入 Ktype：24 / 100
* READY 输入 Ktype：19
* READY 映射行：28
* 明确 PENDING 输入 Ktype：5
* 尚未处理输入 Ktype：76
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1936	1936	Wagon	Passat B2	32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	32B Variant物理外廓。	READY
1937	1937	Wagon	Passat B1	33	5		LOW	官方代际表与逐年Variant资料的外廓值不一致。	PENDING: Type 33 Variant尺寸来源冲突未闭合
1938	1938	Wagon	Passat B1	33	5		LOW	官方代际表与逐年Variant资料的外廓值不一致。	PENDING: Type 33 Variant尺寸来源冲突未闭合
1939	1939	Wagon	Passat B1	33	5		LOW	官方代际表与逐年Variant资料的外廓值不一致。	PENDING: Type 33 Variant尺寸来源冲突未闭合
1940_3dr	1940	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	199三门物理车身。	READY
1940_5dr	1940	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	199五门物理车身。	READY
1941	1941	Wagon	Passat B1	33	5		LOW	官方代际表与逐年Variant资料的外廓值不一致。	PENDING: Type 33 Variant尺寸来源冲突未闭合
1942	1942	Wagon	Passat B1	33	5		LOW	官方代际表与逐年Variant资料的外廓值不一致。	PENDING: Type 33 Variant尺寸来源冲突未闭合
1943_preclipper	1943	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖1988年工厂Clipper套件前外廓。	READY
1943_clipper	1943	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖1988年起工厂Clipper套件外廓。	READY
1944_preclipper	1944	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖1988年工厂Clipper套件前外廓。	READY
1944_clipper	1944	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖1988年起工厂Clipper套件外廓。	READY
1945	1945	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	HIGH	早期无Clipper套件外廓。	READY
1946_preclipper	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖1988年工厂Clipper套件前外廓。	READY
1946_clipper	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖1988年起工厂Clipper套件外廓。	READY
1947_preclipper	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖1988年工厂Clipper套件前外廓。	READY
1947_clipper	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖1988年起工厂Clipper套件外廓。	READY
1948_preclipper	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖1988年工厂Clipper套件前外廓。	READY
1948_clipper	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖1988年起工厂Clipper套件外廓。	READY
1949	1949	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	HIGH	1988年起工厂Clipper套件外廓。	READY
1950	1950	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1951	1951	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1952	1952	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1953	1953	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-G40-01	HIGH	前期GT G40降低车身外廓。	READY
1954	1954	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1955	1955	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	HIGH	1.4 D对应2F改款普通Coupe外廓。	READY
1956_prefl	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	MEDIUM	生产范围覆盖2F改款前普通Coupe外廓。	READY
1956_facelift	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	MEDIUM	生产范围覆盖2F改款后普通Coupe外廓。	READY
1957_prefl	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	MEDIUM	生产范围覆盖2F改款前普通Coupe外廓。	READY
1957_facelift	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	MEDIUM	生产范围覆盖2F改款后普通Coupe外廓。	READY
1958_prefl	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-GT-01	MEDIUM	生产范围覆盖2F改款前GT外廓。	READY
1958_facelift	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-GT-01	MEDIUM	生产范围覆盖2F改款后GT外廓。	READY
1959	1959	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-G40-01	MEDIUM	83kW版本对应2F G40外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B2-VARIANT-WAGON-01	4540	1685	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual	https://www.automobile-catalog.com/car/2010/1229900/fiat_grande_punto_1_2_actual.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual	https://www.automobile-catalog.com/car/2010/1229900/fiat_grande_punto_1_2_actual.html
EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	3815	1630	1395	Volkswagen Newsroom Golf I Cabriolet profile; Automobile-Catalog 1986 Volkswagen Golf Cabrio 1.6 GL	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489;https://www.automobile-catalog.com/car/1986/54350/volkswagen_golf_cabrio_1_6_gl.html
EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	3890	1640	1395	Volkswagen Newsroom Golf I Cabriolet profile; Automobile-Catalog 1991 Volkswagen Golf Cabrio 1.8i Sport	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489;https://www.automobile-catalog.com/car/1991/54695/volkswagen_golf_cabrio_1_8i_sport.html
EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	3655	1590	1355	Volkswagen Newsroom Polo II vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-POLO-II-86C-COUPE-PREFL-G40-01	3655	1580	1335	Automobile-Catalog 1990 Volkswagen Polo Coupe GT G40	https://www.automobile-catalog.com/car/1990/53825/volkswagen_polo_coupe_gt_g40.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	3725	1570	1350	Auto-Data Volkswagen Polo II Coupe 86C	https://www.auto-data.net/en/volkswagen-polo-ii-coupe-86c-generation-1861
EU-VW-POLO-II-86C-COUPE-PREFL-GT-01	3655	1580	1355	Automobile-Catalog 1990 Volkswagen Polo 1.3 GT	https://www.automobile-catalog.com/car/1990/56660/volkswagen_polo_1_3_gt.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-GT-01	3720	1570	1340	UltimateSpecs Volkswagen Polo 2F 86C Coupe 1.3 75	https://www.ultimatespecs.com/car-specs/Volkswagen/3014/Volkswagen-Polo-2F-86C-Coupe-13-75.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-G40-01	3725	1590	1325	EncyCARpedia 1991 Volkswagen Polo G40	https://www.encycarpedia.com/volkswagen/91-polo-g40-coupe
```

## 下一步优先处理

1. 闭合 Ford Fiesta II XR2 与 Escort V Turnier。
2. 核对 Audi 100 C2/C3 代际边界。
3. 批量处理 Renault 4、Renault 5 与 Super 5 的车身簇。
4. 单独解决 Passat B1 Type 33 Variant 的冲突尺寸与外廓更新时间边界。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538?utm_source=chatgpt.com "Vehicle data Passat B2 profile"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535?utm_source=chatgpt.com "Vehicle data Passat B1 profile"


--- 发送 / 继续到 Round 29 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 29 / checkpoint 续跑 ---
## 更新点

* 闭合 Ford Fiesta II XR2 的 1986 年中期外廓变更，拆为前期与后期两个尺寸组。
* Ford Escort 1992–1995 Turnier 三个 Ktype 复用同一 `GAL` Wagon 尺寸组。
* Audi 100 C2 2.0 D 跨越 1979 年改款，拆分为 4680 mm 与 4683 mm 两个外廓；Audi 100 C3 单独建组。
* Renault 4 的 1983 年后乘用车外廓已闭合；Ktype `1968` 覆盖多次早期车身尺寸变化，完整时间分支尚未闭合，暂保留基础行 `PENDING`。 ([汽车目录][1])

## 当前批次进度

* 已研究输入 Ktype：34 / 100
* READY 输入 Ktype：28
* READY 映射行：39
* PENDING 输入 Ktype：6
* 尚未处理输入 Ktype：66
* 已确认尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1960_prefl	1960	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-PREFL-01	HIGH	1986年中期变更前XR2外廓。	READY
1960_facelift	1960	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-FACELIFT-01	HIGH	1986年中期变更后XR2外廓。	READY
1962	1962	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	1992年改款GAL Turnier外廓。	READY
1963	1963	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	1992年改款GAL Turnier外廓。	READY
1964	1964	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	1992年改款GAL Turnier外廓。	READY
1966_prefl	1966	Sedan	Audi 100 C2	43		EU-AUDI-100-C2-43-SEDAN-PREFL-01	HIGH	1979年中期改款前Typ 43外廓。	READY
1966_facelift	1966	Sedan	Audi 100 C2	43		EU-AUDI-100-C2-43-SEDAN-FACELIFT-01	HIGH	1979年中期改款后Typ 43外廓。	READY
1967	1967	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-44-SEDAN-01	HIGH	Typ 44前期Sedan外廓。	READY
1968	1968	Hatchback	Renault 4		5		LOW	生产范围覆盖多个早期车身长度及高度阶段。	PENDING: 1962至1983年外廓变更时间分支尚未完整闭合
1969	1969	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
1970	1970	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
1971	1971	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-PREFL-01	3711	1620	1334	Automobile-Catalog 1986 Ford Fiesta XR-2 before mid-year update	https://www.automobile-catalog.com/car/1986/62570/ford_fiesta_xr-2.html
EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-FACELIFT-01	3711	1620	1362	Automobile-Catalog 1988 Ford Fiesta XR-2	https://www.automobile-catalog.com/car/1988/941480/ford_fiesta_xr-2.html
EU-FORD-ESCORT-VI-GAL-WAGON-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier GAL	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-AUDI-100-C2-43-SEDAN-PREFL-01	4680	1768	1390	Automobile-Catalog 1978 Audi 100 5D	https://www.automobile-catalog.com/make/audi/100_2gen/100_2gen_1_sedan/1978.html
EU-AUDI-100-C2-43-SEDAN-FACELIFT-01	4683	1768	1390	Automobile-Catalog 1979 Audi 100 5D facelift	https://www.automobile-catalog.com/car/1979/166820/audi_100_5d.html
EU-AUDI-100-C3-44-SEDAN-01	4793	1814	1422	Automobile-Catalog 1983 Audi 100 1.8	https://www.automobile-catalog.com/car/1983/31250/audi_100_1_8.html
EU-RENAULT-4-HATCHBACK-LATE-01	3668	1485	1550	Automobile-Catalog 1983 Renault 4 GTL	https://www.automobile-catalog.com/car/1983/2925110/renault_4_gtl.html
```

## 下一步优先处理

1. 闭合 Renault 4 Kasten 的 F4/F6 车身边界，并处理 Ktype `1972`、`1974`、`1975`。
2. 批量处理 Renault 5 第一代普通车身、Alpine 与 Alpine Turbo 外廓。
3. 处理 Fiat Scudo 的短轴、长轴及车高分支。
4. 回补 Ktype `1968` 的早期 Renault 4 精确时间分支，并继续解决 Passat B1 Variant 冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1986/62570/ford_fiesta_xr-2.html?utm_source=chatgpt.com "1986 Ford Fiesta XR-2 Specs Review (70.5 kW / 96 PS / 95 hp) (up to mid-year 1986 for Europe )"


--- 发送 / 继续到 Round 30 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 30 / checkpoint 续跑 ---
## 更新点

* Renault 4 厢式版按 F4 短车身与 F6 加长车身闭合；0.8 Ktype 关联 F4，1.1 Ktype 关联 F6。Renault 官方历史资料确认 F4/F6 长宽边界，R4 技术资料补齐车高。([theoriginals.renault.com][1])
* Renault 5 Alpine `R1223` 在 1979 年 7 月发生宽度变化，Ktype `1987` 拆为前后两个外廓；Alpine Turbo `R122B` 使用独立外廓。BodyCode 由 FIA 历史数据库确认，三维采用明确标注不含后视镜宽度的版本规格。([historicdb.fia.com][2])

## 当前批次进度

* 已研究输入 Ktype：39 / 100
* READY 输入 Ktype：33
* READY 映射行：45
* PENDING 输入 Ktype：6
* 尚未处理输入 Ktype：61
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1972	1972	Van	Renault 4		3	EU-RENAULT-4-F4-VAN-01	HIGH	F4短车身厢式外廓。	READY
1974	1974	Van	Renault 4		3	EU-RENAULT-4-F6-VAN-01	HIGH	F6加长厢式外廓。	READY
1975	1975	Van	Renault 4		3	EU-RENAULT-4-F6-VAN-01	HIGH	F6加长厢式外廓。	READY
1987_pre79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-PRE79-01	HIGH	1979年7月宽度变更前Alpine外廓。	READY
1987_post79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-POST79-01	HIGH	1979年7月宽度变更后Alpine外廓。	READY
1988	1988	Hatchback	Renault 5 I	R122B	3	EU-RENAULT-5-I-R122B-HATCHBACK-ALPINE-TURBO-01	HIGH	R122B Alpine Turbo外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-F4-VAN-01	3653	1500	1710	Renault The Originals Renault 4 Fourgonnette; Das große R4-Buch im Internet technical data	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.r4l.de/wordpress/2022/05/20/entwicklung/
EU-RENAULT-4-F6-VAN-01	3853	1532	1720	Renault The Originals Renault 4 Fourgonnette; Das große R4-Buch im Internet technical data	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.r4l.de/wordpress/2022/05/20/entwicklung/
EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-PRE79-01	3543	1549	1376	Automobile-Catalog 1978 Renault 5 Alpine	https://www.automobile-catalog.com/car/1978/25250/renault_5_alpine.html
EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-POST79-01	3543	1525	1376	Automobile-Catalog 1981 Renault 5 Alpine	https://www.automobile-catalog.com/car/1981/2927975/renault_5_alpine.html
EU-RENAULT-5-I-R122B-HATCHBACK-ALPINE-TURBO-01	3558	1525	1376	Automobile-Catalog 1983 Renault 5 Alpine Turbo	https://www.automobile-catalog.com/car/1983/50915/renault_5_alpine_turbo.html
```

## 下一步优先处理

1. 批量闭合 Renault 5 普通版的 1979 年门数与 1981 年外廓变更分支。
2. 处理 Renault Super 5 的 3 门、5 门及 GT Turbo 外廓。
3. 解决 Fiat Scudo Panorama 短轴/长轴及 1942/1980 mm 车高资料边界。
4. 回补 Renault 4 Ktype `1968` 与 Passat B1 Variant 的既有 PENDING。

推进信号：CONTINUE

[1]: https://theoriginals.renault.com/renault-4-fourgonnette "Renault 4 Fourgonnette - The Originals Museum "
[2]: https://historicdb.fia.com/model/5-alpine-turbo-type-122-b-1397?utm_source=chatgpt.com "5 Alpine Turbo Type 122 B (1397) | FIA Historic Database"


--- 发送 / 继续到 Round 31 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 31 / checkpoint 续跑 ---
## 更新点

* 已消除上一轮 6 个已落盘 `PENDING`。Passat B1 Variant 按 1977 年中期改款拆分：改款前外廓为 `4190 × 1620 × 1370 mm`，改款后为 `4265 × 1615 × 1360 mm`；柴油版本仅关联改款后外廓。([汽车目录][1])
* Renault 4 Ktype `1968` 按早期 `3660 × 1485 × 1530 mm` 与后期既有缓存组拆分，后期组直接复用、不重复输出。([汽车目录][2])

## 当前批次进度

* 已研究输入 Ktype：39 / 100
* READY 输入 Ktype：39
* READY 映射行：55
* 当前已落盘 PENDING：0
* 尚未处理输入 Ktype：61
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1937_prefl	1937	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1937_facelift	1937	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1938	1938	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	改款前Variant外廓。	READY
1939_prefl	1939	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1939_facelift	1939	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1941_prefl	1941	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1941_facelift	1941	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1942	1942	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	柴油版本对应改款后Variant外廓。	READY
1968_early	1968	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-EARLY-01	MEDIUM	早期乘用车外廓。	READY
1968_late	1968	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	MEDIUM	后期乘用车外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	4190	1620	1370	Automobile-Catalog 1974 Volkswagen Passat Variant 1300	https://www.automobile-catalog.com/car/1974/38960/volkswagen_passat_variant_1300.html
EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	4265	1615	1360	Automobile-Catalog 1980 Volkswagen Passat Variant 1600 S	https://www.automobile-catalog.com/car/1980/42680/volkswagen_passat_variant_1600_s.html
EU-RENAULT-4-HATCHBACK-EARLY-01	3660	1485	1530	Automobile-Catalog 1962 Renault 4 L	https://www.automobile-catalog.com/car/1962/2924285/renault_4_l.html
```

## 下一步优先处理

1. 批量闭合 Renault 5 第一代普通版的早期、1981/1983 外廓阶段。
2. 批量关联 Renault Super 5 普通 3 门、5 门及 GT Turbo 尺寸组。
3. 处理 Fiat Scudo Bus 的短轴、长轴和车高分支。
4. 继续 Renault 12、9、11、14、16、18 的共用车身聚类。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/38960/volkswagen_passat_variant_1300.html?utm_source=chatgpt.com "1977 Volkswagen Passat Variant 1300 Specs Review (44 kW / 60 PS / 59 hp) (up to mid-year 1977 for Europe )"
[2]: https://www.automobile-catalog.com/car/1962/2924285/renault_4_l.html?utm_source=chatgpt.com "1962 Renault 4 L (man. 3) (model since September 1962 for Europe ..."


--- 发送 / 继续到 Round 32 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1901-2000_ktype_dimension_mapping_final.tsv
- all_1901-2000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 32 / checkpoint 续跑 ---
## 更新点

* 已按缓存优先补齐尚未落盘的 Renault 5、Super 5、Renault 12、9、11、14、16、18 与 Fiat Scudo 车身簇；已确认尺寸组未重复抓取或重复建组。新增尺寸组主要依据 Renault The Originals、Fiat Professional 技术规格以及直接车型规格页闭合。([原版雷诺][1])
* 已完成固定表头、主键唯一、映射引用闭合、尺寸和来源非空检查。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：174
* PENDING 映射：0
* DIMENSION_GROUP：49
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 两张表列数：10 列 / 6 列

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1936	1936	Wagon	Passat B2	32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-01	HIGH	32B Variant物理外廓。	READY
1937_prefl	1937	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1937_facelift	1937	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1938	1938	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	改款前Variant外廓。	READY
1939_prefl	1939	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1939_facelift	1939	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1940_3dr	1940	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	199三门物理车身。	READY
1940_5dr	1940	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	199五门物理车身。	READY
1941_prefl	1941	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	HIGH	1977年中期改款前Variant外廓。	READY
1941_facelift	1941	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	1977年中期改款后Variant外廓。	READY
1942	1942	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	HIGH	柴油版本对应改款后Variant外廓。	READY
1943_preclipper	1943	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖Clipper套件前外廓。	READY
1943_clipper	1943	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖Clipper套件外廓。	READY
1944_preclipper	1944	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖Clipper套件前外廓。	READY
1944_clipper	1944	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖Clipper套件外廓。	READY
1945	1945	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	HIGH	早期无Clipper套件外廓。	READY
1946_preclipper	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖Clipper套件前外廓。	READY
1946_clipper	1946	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖Clipper套件外廓。	READY
1947_preclipper	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖Clipper套件前外廓。	READY
1947_clipper	1947	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖Clipper套件外廓。	READY
1948_preclipper	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	MEDIUM	生产范围覆盖Clipper套件前外廓。	READY
1948_clipper	1948	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	MEDIUM	生产范围覆盖Clipper套件外廓。	READY
1949	1949	Convertible	Golf I Cabriolet	155	2	EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	HIGH	Clipper套件外廓。	READY
1950	1950	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1951	1951	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1952	1952	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1953	1953	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-G40-01	HIGH	前期G40外廓。	READY
1954	1954	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	HIGH	86C前期普通Coupe外廓。	READY
1955	1955	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	HIGH	2F改款普通Coupe外廓。	READY
1956_prefl	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	MEDIUM	生产范围覆盖2F改款前外廓。	READY
1956_facelift	1956	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	MEDIUM	生产范围覆盖2F改款后外廓。	READY
1957_prefl	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	MEDIUM	生产范围覆盖2F改款前外廓。	READY
1957_facelift	1957	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	MEDIUM	生产范围覆盖2F改款后外廓。	READY
1958_prefl	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-PREFL-GT-01	MEDIUM	生产范围覆盖2F改款前GT外廓。	READY
1958_facelift	1958	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-GT-01	MEDIUM	生产范围覆盖2F改款后GT外廓。	READY
1959	1959	Coupe	Polo II	86C	3	EU-VW-POLO-II-86C-COUPE-FACELIFT-G40-01	HIGH	2F G40外廓。	READY
1960_prefl	1960	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-PREFL-01	HIGH	1986年中期变更前XR2外廓。	READY
1960_facelift	1960	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-FACELIFT-01	HIGH	1986年中期变更后XR2外廓。	READY
1962	1962	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	GAL Turnier外廓。	READY
1963	1963	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	GAL Turnier外廓。	READY
1964	1964	Wagon	Escort VI	GAL	5	EU-FORD-ESCORT-VI-GAL-WAGON-01	HIGH	GAL Turnier外廓。	READY
1966_prefl	1966	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-43-SEDAN-PREFL-01	HIGH	1979年中期改款前Typ 43外廓。	READY
1966_facelift	1966	Sedan	Audi 100 C2	43	4	EU-AUDI-100-C2-43-SEDAN-FACELIFT-01	HIGH	1979年中期改款后Typ 43外廓。	READY
1967	1967	Sedan	Audi 100 C3	44	4	EU-AUDI-100-C3-44-SEDAN-01	HIGH	Typ 44前期Sedan外廓。	READY
1968_early	1968	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-EARLY-01	MEDIUM	早期乘用车外廓。	READY
1968_late	1968	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	MEDIUM	后期乘用车外廓。	READY
1969	1969	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
1970	1970	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
1971	1971	Hatchback	Renault 4		5	EU-RENAULT-4-HATCHBACK-LATE-01	HIGH	后期五门乘用车外廓。	READY
1972	1972	Van	Renault 4		3	EU-RENAULT-4-F4-VAN-01	HIGH	F4短车身厢式外廓。	READY
1974	1974	Van	Renault 4		3	EU-RENAULT-4-F6-VAN-01	HIGH	F6加长厢式外廓。	READY
1975	1975	Van	Renault 4		3	EU-RENAULT-4-F6-VAN-01	HIGH	F6加长厢式外廓。	READY
1976_3dr	1976	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1976_5dr	1976	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1977_3dr	1977	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1977_5dr	1977	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1978_swb	1978	MPV	Scudo II	270	5	EU-FIAT-SCUDO-II-BUS-SWB-01	HIGH	短轴Bus外廓。	READY
1978_lwb	1978	MPV	Scudo II	270	5	EU-FIAT-SCUDO-II-BUS-LWB-01	HIGH	长轴Bus外廓。	READY
1979_3dr	1979	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1979_5dr	1979	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1980_3dr	1980	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1980_5dr	1980	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1981_3dr	1981	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1981_5dr	1981	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1982_3dr	1982	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1982_5dr	1982	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1983_3dr	1983	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1983_5dr	1983	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1984_3dr	1984	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1984_5dr	1984	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1985_3dr	1985	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1985_5dr	1985	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1986_3dr	1986	Hatchback	Renault 5 I		3	EU-RENAULT-5-I-HATCHBACK-3D-01	MEDIUM	三门物理车身。	READY
1986_5dr	1986	Hatchback	Renault 5 I		5	EU-RENAULT-5-I-HATCHBACK-5D-01	MEDIUM	五门物理车身。	READY
1987_pre79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-PRE79-01	HIGH	1979年7月宽度变更前Alpine外廓。	READY
1987_post79	1987	Hatchback	Renault 5 I	R1223	3	EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-POST79-01	HIGH	1979年7月宽度变更后Alpine外廓。	READY
1988	1988	Hatchback	Renault 5 I	R122B	3	EU-RENAULT-5-I-R122B-HATCHBACK-ALPINE-TURBO-01	HIGH	R122B Alpine Turbo外廓。	READY
1989_3dr	1989	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1989_5dr	1989	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1990_3dr	1990	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1990_5dr	1990	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1991_3dr	1991	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1991_5dr	1991	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1993_3dr	1993	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1993_5dr	1993	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1994_3dr	1994	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1994_5dr	1994	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1995	1995	Hatchback	Super 5	C405	3	EU-RENAULT-SUPER-5-C405-HATCHBACK-GT-TURBO-01	HIGH	GT Turbo三门宽体外廓。	READY
1996_3dr	1996	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1996_5dr	1996	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1997_3dr	1997	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1997_5dr	1997	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
1998	1998	Hatchback	Super 5	C409	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	HIGH	C409三门物理车身。	READY
1999_3dr	1999	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
1999_5dr	1999	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
2000_3dr	2000	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
2000_5dr	2000	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
2001_3dr	2001	Hatchback	Super 5	C40	3	EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	MEDIUM	三门Super 5物理车身。	READY
2001_5dr	2001	Hatchback	Super 5	B40	5	EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	MEDIUM	五门Super 5物理车身。	READY
2002	2002	Sedan	Renault 12		4	EU-RENAULT-12-SEDAN-01	HIGH	四门Sedan外廓。	READY
2003	2003	Sedan	Renault 12		4	EU-RENAULT-12-SEDAN-01	HIGH	四门Sedan外廓。	READY
2004_prefl	2004	Wagon	Renault 12		5	EU-RENAULT-12-WAGON-PREFL-01	MEDIUM	1977年改款前Wagon外廓。	READY
2004_facelift	2004	Wagon	Renault 12		5	EU-RENAULT-12-WAGON-FACELIFT-01	MEDIUM	1977年改款后Wagon外廓。	READY
2005_prefl	2005	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	MEDIUM	1986年改款前Sedan外廓。	READY
2005_facelift	2005	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	MEDIUM	1986年改款后Sedan外廓。	READY
2006_prefl	2006	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	MEDIUM	1986年改款前Sedan外廓。	READY
2006_facelift	2006	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	MEDIUM	1986年改款后Sedan外廓。	READY
2007_prefl	2007	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	MEDIUM	1986年改款前Sedan外廓。	READY
2007_facelift	2007	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	MEDIUM	1986年改款后Sedan外廓。	READY
2008	2008	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	HIGH	改款前四门Sedan外廓。	READY
2009	2009	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	HIGH	改款前四门Sedan外廓。	READY
2010	2010	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	HIGH	改款后四门Sedan外廓。	READY
2011	2011	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	HIGH	改款后四门Sedan外廓。	READY
2012_prefl	2012	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	MEDIUM	1986年改款前Sedan外廓。	READY
2012_facelift	2012	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	MEDIUM	1986年改款后Sedan外廓。	READY
2013_prefl	2013	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-PREFL-01	MEDIUM	1986年改款前Sedan外廓。	READY
2013_facelift	2013	Sedan	Renault 9	L42	4	EU-RENAULT-9-L42-SEDAN-FACELIFT-01	MEDIUM	1986年改款后Sedan外廓。	READY
2014_3dr_prefl	2014	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	HIGH	改款前三门物理车身。	READY
2014_5dr_prefl	2014	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	HIGH	改款前五门物理车身。	READY
2015_3dr_prefl	2015	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2015_5dr_prefl	2015	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2015_3dr_facelift	2015	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2015_5dr_facelift	2015	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2016_3dr_prefl	2016	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2016_5dr_prefl	2016	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2016_3dr_facelift	2016	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2016_5dr_facelift	2016	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2017_3dr_prefl	2017	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2017_5dr_prefl	2017	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2017_3dr_facelift	2017	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2017_5dr_facelift	2017	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2018_3dr_prefl	2018	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	HIGH	改款前三门物理车身。	READY
2018_5dr_prefl	2018	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	HIGH	改款前五门物理车身。	READY
2019_3dr_prefl	2019	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	HIGH	改款前三门物理车身。	READY
2019_5dr_prefl	2019	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	HIGH	改款前五门物理车身。	READY
2020_3dr_prefl	2020	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2020_5dr_prefl	2020	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2021_3dr_facelift	2021	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2021_5dr_facelift	2021	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2022_3dr_facelift	2022	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门物理车身。	READY
2022_5dr_facelift	2022	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门物理车身。	READY
2023_3dr_prefl	2023	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2023_5dr_prefl	2023	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2023_3dr_facelift	2023	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2023_5dr_facelift	2023	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2024_3dr_prefl	2024	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2024_5dr_prefl	2024	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2024_3dr_facelift	2024	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2024_5dr_facelift	2024	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2025_3dr_facelift	2025	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门物理车身。	READY
2025_5dr_facelift	2025	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门物理车身。	READY
2026_3dr_facelift	2026	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门物理车身。	READY
2026_5dr_facelift	2026	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	HIGH	改款后五门物理车身。	READY
2027_3dr_prefl	2027	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理车身。	READY
2027_5dr_prefl	2027	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理车身。	READY
2027_3dr_facelift	2027	Hatchback	Renault 11	C37	3	EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理车身。	READY
2027_5dr_facelift	2027	Hatchback	Renault 11	B37	5	EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理车身。	READY
2028	2028	Hatchback	Renault 14	R121	5	EU-RENAULT-14-R121-HATCHBACK-01	HIGH	R121五门Hatchback外廓。	READY
2029	2029	Hatchback	Renault 14	R121	5	EU-RENAULT-14-R121-HATCHBACK-01	HIGH	R121五门Hatchback外廓。	READY
2030	2030	Hatchback	Renault 14	R121	5	EU-RENAULT-14-R121-HATCHBACK-01	HIGH	R121五门Hatchback外廓。	READY
2031	2031	Hatchback	Renault 16		5	EU-RENAULT-16-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
2032_prefl	2032	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-PREFL-01	MEDIUM	Type 2改款前Sedan外廓。	READY
2032_type2	2032	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-TYPE2-01	MEDIUM	Type 2改款后Sedan外廓。	READY
2033	2033	Sedan	Renault 18	1345	4	EU-RENAULT-18-1345-SEDAN-TURBO-01	HIGH	Turbo四门Sedan外廓。	READY
2034	2034	Sedan	Renault 18	1345	4	EU-RENAULT-18-1345-SEDAN-TURBO-01	HIGH	Turbo四门Sedan外廓。	READY
2035_prefl	2035	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-PREFL-01	MEDIUM	Type 2改款前Sedan外廓。	READY
2035_type2	2035	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-TYPE2-01	MEDIUM	Type 2改款后Sedan外廓。	READY
2036	2036	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-PREFL-01	HIGH	Type 2改款前Sedan外廓。	READY
2037_prefl	2037	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-PREFL-01	MEDIUM	Type 2改款前Sedan外廓。	READY
2037_type2	2037	Sedan	Renault 18	134	4	EU-RENAULT-18-134-SEDAN-TYPE2-01	MEDIUM	Type 2改款后Sedan外廓。	READY
2038_prefl	2038	Wagon	Renault 18	135	5	EU-RENAULT-18-135-WAGON-PREFL-01	MEDIUM	Type 2改款前Wagon外廓。	READY
2038_type2	2038	Wagon	Renault 18	135	5	EU-RENAULT-18-135-WAGON-TYPE2-01	MEDIUM	Type 2改款后Wagon外廓。	READY
2039_prefl	2039	Wagon	Renault 18	135	5	EU-RENAULT-18-135-WAGON-PREFL-01	MEDIUM	Type 2改款前Wagon外廓。	READY
2039_type2	2039	Wagon	Renault 18	135	5	EU-RENAULT-18-135-WAGON-TYPE2-01	MEDIUM	Type 2改款后Wagon外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1901-2000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B2-VARIANT-WAGON-01	4540	1685	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B1-33-VARIANT-PREFL-01	4190	1620	1370	Automobile-Catalog 1974 Volkswagen Passat Variant 1300	https://www.automobile-catalog.com/car/1974/38960/volkswagen_passat_variant_1300.html
EU-VW-PASSAT-B1-33-VARIANT-FACELIFT-01	4265	1615	1360	Automobile-Catalog 1980 Volkswagen Passat Variant 1600 S	https://www.automobile-catalog.com/car/1980/42680/volkswagen_passat_variant_1600_s.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual	https://www.automobile-catalog.com/car/2010/1229900/fiat_grande_punto_1_2_actual.html
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Automobile-Catalog 2010 Fiat Grande Punto 1.2 Actual	https://www.automobile-catalog.com/car/2010/1229900/fiat_grande_punto_1_2_actual.html
EU-VW-GOLF-I-155-CABRIOLET-PRECLIPPER-01	3815	1630	1395	Volkswagen Newsroom Golf I Cabriolet profile; Automobile-Catalog 1986 Volkswagen Golf Cabrio 1.6 GL	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489;https://www.automobile-catalog.com/car/1986/54350/volkswagen_golf_cabrio_1_6_gl.html
EU-VW-GOLF-I-155-CABRIOLET-CLIPPER-01	3890	1640	1395	Volkswagen Newsroom Golf I Cabriolet profile; Automobile-Catalog 1991 Volkswagen Golf Cabrio 1.8i Sport	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-1-cabriolet-profile-19489;https://www.automobile-catalog.com/car/1991/54695/volkswagen_golf_cabrio_1_8i_sport.html
EU-VW-POLO-II-86C-COUPE-PREFL-STD-01	3655	1590	1355	Volkswagen Newsroom Polo II vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-POLO-II-86C-COUPE-PREFL-G40-01	3655	1580	1335	Automobile-Catalog 1990 Volkswagen Polo Coupe GT G40	https://www.automobile-catalog.com/car/1990/53825/volkswagen_polo_coupe_gt_g40.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-STD-01	3725	1570	1350	Auto-Data Volkswagen Polo II Coupe 86C	https://www.auto-data.net/en/volkswagen-polo-ii-coupe-86c-generation-1861
EU-VW-POLO-II-86C-COUPE-PREFL-GT-01	3655	1580	1355	Automobile-Catalog 1990 Volkswagen Polo 1.3 GT	https://www.automobile-catalog.com/car/1990/56660/volkswagen_polo_1_3_gt.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-GT-01	3720	1570	1340	UltimateSpecs Volkswagen Polo 2F 86C Coupe 1.3 75	https://www.ultimatespecs.com/car-specs/Volkswagen/3014/Volkswagen-Polo-2F-86C-Coupe-13-75.html
EU-VW-POLO-II-86C-COUPE-FACELIFT-G40-01	3725	1590	1325	EncyCARpedia 1991 Volkswagen Polo G40	https://www.encycarpedia.com/volkswagen/91-polo-g40-coupe
EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-PREFL-01	3711	1620	1334	Automobile-Catalog 1986 Ford Fiesta XR-2 before mid-year update	https://www.automobile-catalog.com/car/1986/62570/ford_fiesta_xr-2.html
EU-FORD-FIESTA-II-FBD-HATCHBACK-XR2-FACELIFT-01	3711	1620	1362	Automobile-Catalog 1988 Ford Fiesta XR-2	https://www.automobile-catalog.com/car/1988/941480/ford_fiesta_xr-2.html
EU-FORD-ESCORT-VI-GAL-WAGON-01	4268	1690	1410	Auto-Data Ford Escort VI Turnier GAL	https://www.auto-data.net/en/ford-escort-vi-turnier-gal-generation-1664
EU-AUDI-100-C2-43-SEDAN-PREFL-01	4680	1768	1390	Automobile-Catalog 1978 Audi 100 5D	https://www.automobile-catalog.com/make/audi/100_2gen/100_2gen_1_sedan/1978.html
EU-AUDI-100-C2-43-SEDAN-FACELIFT-01	4683	1768	1390	Automobile-Catalog 1979 Audi 100 5D facelift	https://www.automobile-catalog.com/car/1979/166820/audi_100_5d.html
EU-AUDI-100-C3-44-SEDAN-01	4793	1814	1422	Automobile-Catalog 1983 Audi 100 1.8	https://www.automobile-catalog.com/car/1983/31250/audi_100_1_8.html
EU-RENAULT-4-HATCHBACK-EARLY-01	3660	1485	1530	Automobile-Catalog 1962 Renault 4 L	https://www.automobile-catalog.com/car/1962/2924285/renault_4_l.html
EU-RENAULT-4-HATCHBACK-LATE-01	3668	1485	1550	Automobile-Catalog 1983 Renault 4 GTL	https://www.automobile-catalog.com/car/1983/2925110/renault_4_gtl.html
EU-RENAULT-4-F4-VAN-01	3653	1500	1710	Renault The Originals Renault 4 Fourgonnette; Das große R4-Buch im Internet technical data	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.r4l.de/wordpress/2022/05/20/entwicklung/
EU-RENAULT-4-F6-VAN-01	3853	1532	1720	Renault The Originals Renault 4 Fourgonnette; Das große R4-Buch im Internet technical data	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.r4l.de/wordpress/2022/05/20/entwicklung/
EU-RENAULT-5-I-HATCHBACK-3D-01	3500	1520	1400	Renault The Originals R5 TL	https://theoriginals.renault.com/en/r5-tl
EU-RENAULT-5-I-HATCHBACK-5D-01	3500	1520	1400	Renault The Originals R5 TL	https://theoriginals.renault.com/en/r5-tl
EU-FIAT-SCUDO-II-BUS-SWB-01	4805	1895	1980	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-FIAT-SCUDO-II-BUS-LWB-01	5135	1895	1980	Fiat Professional Scudo technical specifications	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/Schede-Tecniche/150409_Fiat-Professional_Scudo-18p_ENG.pdf
EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-PRE79-01	3543	1549	1376	Automobile-Catalog 1978 Renault 5 Alpine	https://www.automobile-catalog.com/car/1978/25250/renault_5_alpine.html
EU-RENAULT-5-I-R1223-HATCHBACK-ALPINE-POST79-01	3543	1525	1376	Automobile-Catalog 1981 Renault 5 Alpine	https://www.automobile-catalog.com/car/1981/2927975/renault_5_alpine.html
EU-RENAULT-5-I-R122B-HATCHBACK-ALPINE-TURBO-01	3558	1525	1376	Automobile-Catalog 1983 Renault 5 Alpine Turbo	https://www.automobile-catalog.com/car/1983/50915/renault_5_alpine_turbo.html
EU-RENAULT-SUPER-5-C40-HATCHBACK-3D-01	3590	1580	1390	UltimateSpecs Renault Super 5 1.7 GTX	https://www.ultimatespecs.com/car-specs/Renault/6384/Renault-Super-5-17-GTX-Kat.html
EU-RENAULT-SUPER-5-B40-HATCHBACK-5D-01	3650	1580	1390	UltimateSpecs Renault Super 5 1.1 L/TL/GTL 5-door	https://www.ultimatespecs.com/car-specs/Renault/142507/Renault-Super-5-11-L-TL-GTL-5-door.html
EU-RENAULT-SUPER-5-C405-HATCHBACK-GT-TURBO-01	3590	1590	1360	Renault The Originals Supercinq GT Turbo	https://theoriginals.renault.com/en/supercinq-gt-turbo
EU-RENAULT-12-SEDAN-01	4348	1616	1435	UltimateSpecs Renault 12	https://www.ultimatespecs.com/car-specs/Renault/M2654/12
EU-RENAULT-12-WAGON-PREFL-01	4404	1616	1455	Automobile-Catalog 1974 Renault 12 LN Break	https://www.automobile-catalog.com/car/1974/2926625/renault_12_ln_break.html
EU-RENAULT-12-WAGON-FACELIFT-01	4371	1616	1455	Automobile-Catalog 1977 Renault 12 Break	https://www.automobile-catalog.com/car/1977/2926760/renault_12_break.html
EU-RENAULT-9-L42-SEDAN-PREFL-01	4063	1650	1405	UltimateSpecs Renault 9	https://www.ultimatespecs.com/car-specs/Renault/M37/9
EU-RENAULT-9-L42-SEDAN-FACELIFT-01	4059	1631	1400	AutoEvolution Renault 9 1986-1988	https://www.autoevolution.com/cars/renault-9-1986.html
EU-RENAULT-11-C37-HATCHBACK-3D-PREFL-01	3985	1660	1410	UltimateSpecs Renault 11	https://www.ultimatespecs.com/car-specs/Renault/M38/11
EU-RENAULT-11-B37-HATCHBACK-5D-PREFL-01	3985	1660	1410	UltimateSpecs Renault 11	https://www.ultimatespecs.com/car-specs/Renault/M38/11
EU-RENAULT-11-C37-HATCHBACK-3D-FACELIFT-01	4050	1670	1370	Renault The Originals Renault 11 Turbo	https://theoriginals.renault.com/en/renault-11-turbo
EU-RENAULT-11-B37-HATCHBACK-5D-FACELIFT-01	4050	1670	1370	Renault The Originals Renault 11 Turbo	https://theoriginals.renault.com/en/renault-11-turbo
EU-RENAULT-14-R121-HATCHBACK-01	4020	1620	1400	Renault The Originals R14	https://theoriginals.renault.com/en/r14
EU-RENAULT-16-HATCHBACK-01	4240	1650	1450	Renault The Originals R16 TX	https://theoriginals.renault.com/en/r16-tx
EU-RENAULT-18-134-SEDAN-PREFL-01	4369	1682	1402	Automobile-Catalog 1979 Renault 18 phase-I Sedan	https://www.automobile-catalog.com/make/renault/18/18/1979.html
EU-RENAULT-18-134-SEDAN-TYPE2-01	4394	1696	1405	Automobile-Catalog 1985 Renault 18 GTX	https://www.automobile-catalog.com/car/1985/2932190/renault_18_gtx.html
EU-RENAULT-18-1345-SEDAN-TURBO-01	4380	1690	1400	Renault The Originals R18 Turbo	https://theoriginals.renault.com/en/r18-turbo
EU-RENAULT-18-135-WAGON-PREFL-01	4451	1689	1402	Automobile-Catalog 1981 Renault 18 TS Estate Soleil	https://www.automobile-catalog.com/car/1981/2933270/renault_18_ts_estate_soleil.html
EU-RENAULT-18-135-WAGON-TYPE2-01	4487	1696	1405	Automobile-Catalog 1984 Renault 18 phase-II Break	https://www.automobile-catalog.com/make/renault/18/18_break_2/1984.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1901-2000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://theoriginals.renault.com/en/r5-tl?utm_source=chatgpt.com "R5 TL"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（174 行）
- 累计尺寸组：dimension_groups_final.tsv（49 行）

