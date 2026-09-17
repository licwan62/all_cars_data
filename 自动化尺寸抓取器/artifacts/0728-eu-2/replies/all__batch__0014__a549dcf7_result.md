# 任务：all 第 1301-1400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0014__a549dcf7


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1301-1400 行

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
all 第 1301-1400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	C-Klasse	C 220 CDI	Stufenheck	Heckantrieb	Diesel	125	170	Jan 2007	Nov 2008	2024-03-01	22458
Mercedes-benz	C-Klasse	C 320 CDI	Stufenheck	Heckantrieb	Diesel	165	224	Jan 2007	Jan 2014	2024-03-01	22459
Mercedes-benz	C-Klasse	C 180 Kompressor	Stufenheck	Heckantrieb	Benzin	115	156	Jan 2007	Jan 2009	2025-06-01	22460
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	135	184	Jan 2007	Jan 2014	2024-03-01	22461
Mercedes-benz	C-Klasse	C 230	Stufenheck	Heckantrieb	Benzin	150	204	Jan 2007	Jan 2014	2024-03-01	22462
Daihatsu	Materia	1.3	Großraumlimousine	Frontantrieb	Benzin	67	91	Oct 2006	-	2024-03-01	22463
Daihatsu	Materia	1.5	Großraumlimousine	Frontantrieb	Benzin	76	103	Oct 2006	-	2024-03-01	22464
Toyota	Auris	2.2 D	Schrägheck	Frontantrieb	Diesel	130	177	Nov 2006	Sep 2012	2024-03-01	22465
Toyota	Auris	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	93	126	Oct 2006	Sep 2012	2024-03-01	22466
Toyota	Auris	1.4 D-4d	Schrägheck	Frontantrieb	Diesel	66	90	Mar 2007	Sep 2012	2024-03-01	22467
Daihatsu	Materia	1.5 ECO 4WD	Großraumlimousine	Allrad	Benzin	76	103	Oct 2006	-	2024-03-01	22468
Toyota	Auris	1.6	Schrägheck	Frontantrieb	Benzin	91	124	Mar 2007	Sep 2012	2024-03-01	22469
Toyota	Auris	1.4	Schrägheck	Frontantrieb	Benzin	71	97	Mar 2007	Sep 2012	2024-03-01	22470
Daihatsu	Trevis	1	Schrägheck	Frontantrieb	Benzin	43	58	Jun 2006	-	2024-03-01	22471
Smart	Fortwo	1.0 Turbo	Coupe	Heckantrieb	Benzin	62	84	Jan 2007	-	2024-03-01	22472
Smart	Fortwo	1	Coupe	Heckantrieb	Benzin	45	61	Jan 2007	-	2024-03-01	22473
Smart	Fortwo	1	Coupe	Heckantrieb	Benzin	52	71	Jan 2007	-	2024-03-01	22474
Toyota	Yaris	1.8 Vvti	Schrägheck	Frontantrieb	Benzin	98	133	Jan 2007	Dec 2011	2024-03-01	22475
Smart	Fortwo	0.8 CDI	Coupe	Heckantrieb	Diesel	33	45	Jan 2007	-	2024-03-01	22476
Smart	Fortwo cabrio	1	Cabriolet	Heckantrieb	Benzin	52	71	Jan 2007	-	2024-03-01	22477
Smart	Fortwo cabrio	1.0 Turbo	Cabriolet	Heckantrieb	Benzin	62	84	Jan 2007	-	2024-03-01	22478
Smart	Fortwo cabrio	0.8 CDI	Cabriolet	Heckantrieb	Diesel	33	45	Jan 2007	-	2024-03-01	22479
Citroën	C-Crosser	2.2 HDI	SUV	Allrad	Diesel	115	156	Feb 2007	Dec 2012	2024-03-01	22480
Citroën	C4 grand picasso i	1.8 I 16V	Großraumlimousine	Frontantrieb	Benzin	92	125	Oct 2006	Dec 2010	2024-03-01	22481
Citroën	C4 grand picasso i	2.0 I 16V	Großraumlimousine	Frontantrieb	Benzin	103	140	Oct 2006	Aug 2013	2024-03-01	22482
Citroën	C4 grand picasso i	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	80	109	Oct 2006	Jun 2011	2024-03-01	22483
Citroën	C4 grand picasso i	2.0 HDI 138	Großraumlimousine	Frontantrieb	Diesel	100	136	Oct 2006	Dec 2013	2024-03-01	22484
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	70	95	Nov 2006	Mar 2010	2024-03-01	22485
Mini	Mini	Cooper D	Schrägheck	Frontantrieb	Diesel	80	109	Nov 2006	Sep 2010	2024-03-01	22486
Peugeot	4007	2.2 HDI	SUV	Allrad	Diesel	115	156	Feb 2007	Mar 2013	2024-03-01	22487
Renault	Espace iv	2.0 DCI	Großraumlimousine	Frontantrieb	Diesel	96	131	Jan 2006	Dec 2015	2025-12-01	22488
Renault	Trafic ii	2.0 16V	Bus	Frontantrieb	Benzin	86	117	Aug 2006	-	2024-03-01	22489
Renault	Trafic ii	2.0 16V	Kasten	Frontantrieb	Benzin	86	117	Aug 2006	-	2024-03-01	22490
Mitsubishi	Outlander ii	2.0 Di-d	SUV	Allrad	Diesel	103	140	Feb 2007	Nov 2012	2024-03-01	22491
Mitsubishi	Outlander ii	2.4 4WD	SUV	Allrad	Benzin	125	170	Sep 2007	Nov 2012	2024-03-01	22492
KIA	Cee'd	1.4	Kombi	Frontantrieb	Benzin	80	109	Sep 2007	Dec 2012	2024-03-01	22493
KIA	Cee'd	1.6	Kombi	Frontantrieb	Benzin	90	122	Sep 2007	Dec 2012	2024-03-01	22494
KIA	Cee'd	2	Kombi	Frontantrieb	Benzin	105	143	Sep 2007	Dec 2012	2024-03-01	22495
KIA	Cee'd	1.6 Crdi 90	Kombi	Frontantrieb	Diesel	66	90	Sep 2007	Dec 2012	2024-03-01	22496
KIA	Cee'd	1.6 Crdi 115	Kombi	Frontantrieb	Diesel	85	115	Sep 2007	Dec 2012	2024-03-01	22497
Isuzu	D-Max i	2.5 Ditd 4X4	Pick-up	Allrad	Diesel	100	136	Jan 2007	Jun 2012	2024-03-01	22498
Isuzu	D-Max i	3.0 Ditd 4X4	Pick-up	Allrad	Diesel	120	163	Jan 2007	Jun 2012	2024-03-01	22499
Seat	Altea	1.6	Großraumlimousine	Frontantrieb	Benzin	75	102	Oct 2006	Nov 2010	2024-05-01	22500
Seat	Altea	2.0 FSI	Großraumlimousine	Frontantrieb	Benzin	110	150	Oct 2006	Mar 2009	2024-03-01	22501
Seat	Altea	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	77	105	Oct 2006	Dec 2010	2024-03-01	22502
Seat	Altea	2.0 TDI 16V	Großraumlimousine	Frontantrieb	Diesel	103	140	Oct 2006	Jul 2015	2024-05-01	22503
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Oct 2006	Nov 2010	2024-05-01	22504
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Nov 2005	Nov 2010	2024-05-01	22505
Ford	Mondeo iv	1.6 TI	Schrägheck	Frontantrieb	Benzin	81	110	Mar 2007	Jan 2015	2024-03-01	22506
Ford	Mondeo iv	1.6 TI	Schrägheck	Frontantrieb	Benzin	92	125	Mar 2007	Jan 2015	2024-03-01	22507
Ford	Mondeo iv	2	Schrägheck	Frontantrieb	Benzin	107	145	Mar 2007	Jan 2015	2024-03-01	22508
Ford	Mondeo iv	2.5	Schrägheck	Frontantrieb	Benzin	162	220	Mar 2007	Jan 2015	2024-03-01	22509
Ford	Mondeo iv	1.8 Tdci	Schrägheck	Frontantrieb	Diesel	74	100	Mar 2007	Jan 2015	2024-03-01	22510
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	96	130	Mar 2007	Jan 2015	2024-03-01	22511
Ford	Mondeo iv	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	103	140	Mar 2007	Jan 2015	2024-03-01	22512
Ford	Mondeo iv turnier	1.6 TI	Kombi	Frontantrieb	Benzin	81	110	Mar 2007	Dec 2012	2024-03-01	22513
Ford	Mondeo iv turnier	1.6 TI	Kombi	Frontantrieb	Benzin	92	125	Mar 2007	Dec 2010	2024-03-01	22514
Ford	Mondeo iv turnier	2	Kombi	Frontantrieb	Benzin	107	145	Mar 2007	Jan 2015	2024-03-01	22515
Ford	Mondeo iv turnier	2.5	Kombi	Frontantrieb	Benzin	162	220	Mar 2007	Dec 2012	2024-03-01	22516
Ford	Mondeo iv turnier	1.8 Tdci	Kombi	Frontantrieb	Diesel	74	100	Mar 2007	Dec 2012	2024-03-01	22517
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	96	130	Mar 2007	Dec 2012	2024-03-01	22518
Ford	Mondeo iv turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	103	140	Mar 2007	Jan 2015	2024-03-01	22519
Ford	Mondeo iv	2	Stufenheck	Frontantrieb	Benzin	107	145	Mar 2007	Jan 2015	2024-03-01	22520
Ford	Mondeo iv	2.5	Stufenheck	Frontantrieb	Benzin	162	220	Mar 2007	Jan 2015	2024-03-01	22521
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	96	130	Mar 2007	Jan 2015	2024-03-01	22522
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	103	140	Mar 2007	Jan 2015	2024-03-01	22523
Ford	C-Max	1.6	Großraumlimousine	Frontantrieb	Benzin	74	100	Feb 2007	Sep 2010	2024-03-01	22524
Ford	C-Max	1.8	Großraumlimousine	Frontantrieb	Benzin	92	125	Feb 2007	Sep 2010	2024-03-01	22525
Ford	C-Max	1.8 Flexifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	92	125	Feb 2007	Sep 2010	2024-03-01	22526
Ford	C-Max	2	Großraumlimousine	Frontantrieb	Benzin	107	145	Feb 2007	Sep 2010	2024-03-01	22527
Ford	C-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	66	90	Feb 2007	Sep 2010	2024-03-01	22528
Ford	C-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	80	109	Feb 2007	Sep 2010	2024-03-01	22529
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	100	136	Feb 2007	Sep 2010	2024-03-01	22530
VW	Passat b6	3.6 R36 4motion	Stufenheck	Allrad	Benzin	220	300	Apr 2007	Jul 2010	2024-03-01	22531
VW	Passat b6 variant	3.6 R36 4motion	Kombi	Allrad	Benzin	220	300	Apr 2007	Nov 2010	2024-03-01	22532
BMW	3	320 I	Coupe	Heckantrieb	Benzin	125	170	Mar 2007	Jun 2013	2024-03-01	22533
BMW	3	320 D	Coupe	Heckantrieb	Diesel	130	177	Sep 2006	Feb 2010	2024-03-01	22534
BMW	3	320 I	Cabriolet	Heckantrieb	Benzin	125	170	Mar 2007	Oct 2013	2024-03-01	22535
BMW	3	325 I	Cabriolet	Heckantrieb	Benzin	160	218	Mar 2007	Dec 2013	2024-03-01	22536
BMW	3	330 I	Cabriolet	Heckantrieb	Benzin	200	272	Mar 2007	Oct 2013	2024-03-01	22537
BMW	3	335 I	Cabriolet	Heckantrieb	Benzin	225	306	Dec 2006	Oct 2013	2024-03-01	22538
BMW	3	330 D	Cabriolet	Heckantrieb	Diesel	170	231	Mar 2007	Dec 2013	2024-03-01	22539
Fiat	Panda	1.4	Schrägheck	Frontantrieb	Benzin	74	100	Oct 2006	-	2024-03-01	22540
Porsche	Boxster	2.7	Cabriolet	Heckantrieb	Benzin	180	245	Jul 2006	Dec 2009	2024-03-01	22541
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	217	295	Jul 2006	Dec 2009	2024-03-01	22542
BMW	3	325 D	Coupe	Heckantrieb	Diesel	145	197	Feb 2007	Feb 2010	2024-03-01	22543
Fiat	Bravo ii	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	88	120	Apr 2007	Dec 2014	2024-03-01	22544
Fiat	Bravo ii	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	110	150	Apr 2007	Dec 2014	2024-03-01	22545
Fiat	Bravo ii	1.4	Schrägheck	Frontantrieb	Benzin	66	90	Apr 2007	Dec 2014	2024-03-01	22546
Audi	A5	1.8 Tfsi	Coupe	Frontantrieb	Benzin	125	170	Oct 2007	Jan 2017	2024-03-01	22547
Audi	A5	3.2 FSI	Coupe	Frontantrieb	Benzin	195	265	Jun 2007	Mar 2012	2024-03-01	22548
Audi	A5	S5 Quattro	Coupe	Allrad	Benzin	260	354	Jun 2007	Mar 2012	2024-03-01	22549
Audi	A5	2.7 TDI	Coupe	Frontantrieb	Diesel	140	190	Jun 2007	Mar 2012	2024-03-01	22550
Audi	A5	3.0 TDI Quattro	Coupe	Allrad	Diesel	176	240	Jun 2007	Mar 2012	2024-03-01	22551
Audi	R8	4.2 FSI Quattro	Coupe	Allrad	Benzin	309	420	Apr 2007	Sep 2010	2024-03-01	22552
VW	Golf v variant	1.6	Kombi	Frontantrieb	Benzin	75	102	Jun 2007	Jul 2009	2024-03-01	22553
VW	Golf v variant	1.4 TSI	Kombi	Frontantrieb	Benzin	103	140	Jun 2007	Jul 2009	2024-03-01	22554
VW	Golf v variant	1.9 TDI	Kombi	Frontantrieb	Diesel	77	105	Jun 2007	Jul 2009	2024-03-01	22555
VW	Golf v variant	2.0 TDI 16V	Kombi	Frontantrieb	Diesel	103	140	Jun 2007	Jul 2009	2024-03-01	22556
VW	Golf plus v	1.4 FSI	Schrägheck	Frontantrieb	Benzin	66	90	Jul 2005	Nov 2006	2024-03-01	22557


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 10 个尺寸组，覆盖 25 个输入 Ktype、31 条 READY 映射。
* Auris 按官方资料拆分为普通车身高度 1515 mm 和 T180 高度 1505 mm；Yaris 1.8 SR/TS 按三门、五门建立派生映射，但两种门数共用尺寸组。
* Smart Fortwo Coupé/Cabrio、Materia、MINI R56、C-Crosser 等已完成三维与不含后视镜宽度核对。
* Mercedes-Benz C-Class W204 前期轿车已统一关联同一尺寸组。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：25
* READY 映射：31 行
* PENDING／未处理输入 Ktype：75
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22458	22458	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22459	22459	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22460	22460	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22461	22461	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22462	22462	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22463	22463	MPV	Materia I	M401	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M401五门车身。	READY
22464	22464	MPV	Materia I	M402	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M402五门车身。	READY
22465_3dr	22465	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	HIGH	T180三门物理分支；三维与五门一致。	READY
22465_5dr	22465	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	HIGH	T180五门物理分支；三维与三门一致。	READY
22466_3dr	22466	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支；三维与五门一致。	READY
22466_5dr	22466	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支；三维与三门一致。	READY
22467_3dr	22467	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支；三维与五门一致。	READY
22467_5dr	22467	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支；三维与三门一致。	READY
22468	22468	MPV	Materia I	M412	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M412四驱五门车身。	READY
22469_3dr	22469	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支；三维与五门一致。	READY
22469_5dr	22469	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支；三维与三门一致。	READY
22470_3dr	22470	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支；三维与五门一致。	READY
22470_5dr	22470	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支；三维与三门一致。	READY
22471	22471	Hatchback	Trevis I	L650	5	EU-DAIHATSU-TREVIS-I-HATCHBACK-5D-01	HIGH	L650五门车身。	READY
22472	22472	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22473	22473	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22474	22474	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22475_3dr	22475	Hatchback	Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	HIGH	1.8 SR/TS三门物理分支；三维与五门一致。	READY
22475_5dr	22475	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	HIGH	1.8 SR/TS五门物理分支；三维与三门一致。	READY
22476	22476	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22477	22477	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22478	22478	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22479	22479	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22480	22480	SUV	C-Crosser I		5	EU-CITROEN-C-CROSSER-I-SUV-5D-01	HIGH	五门SUV标准车身。	READY
22485	22485	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门标准车身。	READY
22486	22486	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门标准车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	4581	1770	1447	Mercedes-Benz Public Archive; Automobile-Catalog	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://www.automobile-catalog.com/car/2007/1550015/mercedes-benz_c_200_cdi.html
EU-DAIHATSU-MATERIA-I-MPV-5D-01	3800	1690	1635	Daihatsu Materia brochure; Automobile-Catalog	https://www.ademosthenous.com/documents/Daihatsu_Materia_Brochure.pdf;https://www.automobile-catalog.com/car/2007/581720/daihatsu_materia_1_3.html
EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	4220	1760	1505	Toyota Auris first-generation launch press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Auris-1st-gen-launch-press-pack.pdf
EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	4220	1760	1515	Toyota Auris first-generation launch press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Auris-1st-gen-launch-press-pack.pdf
EU-DAIHATSU-TREVIS-I-HATCHBACK-5D-01	3400	1475	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/581135/daihatsu_trevis.html
EU-SMART-FORTWO-II-COUPE-01	2695	1559	1542	smart fortwo technical data brochure; Automobile-Catalog	https://manuals.plus/m/6fac10729c057a642579716f82884368eb1a31c20d0e3a920c3ac7df599df96c.pdf;https://www.automobile-catalog.com/car/2007/3155000/smart_fortwo_coupe_84.html
EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	3800	1695	1530	Toyota Yaris SR second-generation press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen2-Yaris-SR-archive-press-pack.pdf
EU-SMART-FORTWO-II-CONVERTIBLE-01	2695	1559	1542	smart fortwo technical data brochure	https://manuals.plus/m/6fac10729c057a642579716f82884368eb1a31c20d0e3a920c3ac7df599df96c.pdf
EU-CITROEN-C-CROSSER-I-SUV-5D-01	4645	1805	1715	2007 Citroën C-Crosser UK brochure; Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-C-Crosser-UK.pdf;https://www.automobile-catalog.com/car/2007/552605/citroen_c-crosser_hdi_155_fap_tendace.html
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	BMW Group MINI Product Guide 2009; Automobile-Catalog	https://www.press.bmwgroup.com/canada/article/attachment/T0036807EN/56874;https://www.automobile-catalog.com/car/2007/1753085/mini_one.html
```

## 下一步优先处理

优先闭合 Ktype 22481–22492：C4 Grand Picasso I、Peugeot 4007、Espace IV、Trafic II 和 Outlander II。重点先解决 C4 Grand Picasso 高度口径，以及 Trafic II 的轴距、车顶和 Bus/Kasten 物理分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327&utm_source=chatgpt.com "204 series C-Class Saloons, 2007 - 2011"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 8 条 READY 映射，闭合 Grand C4 Picasso I、Peugeot 4007、Espace IV Phase II 标准轴距版及 Outlander II 前期型 4 个尺寸组。官方技术资料明确支持 Grand C4 Picasso 的 4590 × 1830 × 1710 mm，以及 Peugeot 4007 的 4637 × 1808 × 1715 mm。
* Espace IV 已排除 Grand Espace 长轴版本，当前 Ktype 关联标准轴距车身；不含后视镜宽度为 1860 mm。
* Outlander II 的 2.0 DI-D 与 2.4 4WD 复用同一前期尺寸组。([汽车数据网][1])
* Trafic II 的 Bus 与 Kasten 暂未 READY：该代同时存在两种轴距及两种车顶高度，而当前 Ktype 信息不足以锁定全部物理分支。([雷诺新闻中心][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：39 行，覆盖 33 个 Ktype
* 明确 PENDING 映射：2 行
* 尚未处理 Ktype：65
* PENDING／未完成 Ktype 合计：67
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22481	22481	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22482	22482	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22483	22483	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22484	22484	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22487	22487	SUV	4007 I		5	EU-PEUGEOT-4007-I-SUV-5D-01	HIGH	第一代五门SUV车身。	READY
22488	22488	MPV	Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	HIGH	标准轴距Espace；不含Grand Espace长轴车身。	READY
22489	22489	MPV	Trafic II Phase II				LOW	Bus存在SWB/LWB及车顶分支，当前Ktype尚不能锁定完整物理边界。	PENDING: 未确认轴距与车顶分支
22490	22490	Van	Trafic II Phase II				LOW	Kasten存在SWB/LWB及低顶/高顶分支，当前Ktype尚不能锁定完整物理边界。	PENDING: 未确认轴距与车顶分支
22491	22491	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	HIGH	第二代改款前五门车身。	READY
22492	22492	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	HIGH	第二代改款前五门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	4590	1830	1710	Citroën C4 Picasso and Grand C4 Picasso technical brochure	https://www.xr793.com/wp-content/uploads/2020/09/2012-Citroen-C4-Picasso-Grand-C4-Picasso.pdf
EU-PEUGEOT-4007-I-SUV-5D-01	4637	1808	1715	Peugeot 4007 UK official brochure	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-4007-UK.pdf
EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	4656	1860	1728	Renault Espace Phase II brochure; Auto-Data	https://forum.renaultespace.pl/plikownia/espace-4/prospekty/2008%20EN%20Ph2.pdf;https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-2.0-dci-150hp-20273
EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	4640	1800	1720	Auto-Data	https://www.auto-data.net/en/mitsubishi-outlander-ii-generation-3392
```

## 下一步优先处理

1. 专门闭合 Trafic II 的 Bus/Kasten、SWB/LWB及低顶/高顶分支。
2. 随后批量处理 22493–22505：KIA Cee’d Wagon、Isuzu D-Max I 与 Seat Altea。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-outlander-ii-2.0-di-d-140hp-15451?utm_source=chatgpt.com "Mitsubishi Outlander II 2.0 DI-D (140 Hp)"
[2]: https://www.press.renault.co.uk/releases/2135?utm_source=chatgpt.com "New Renault Trafic and Master ranges - Press Information"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已消除 Trafic II 两个 PENDING Ktype：Bus 拆分为 SWB/LWB 低顶，Kasten 拆分为 SWB 低顶、LWB 低顶及 LWB 高顶，共新增 5 条 READY 映射和 3 个尺寸组。Ktype 22489、22490 分别对应 JL Bus 与 FL Van；该代存在两种轴距及低顶/高顶外廓。([梅耶尔摩托车][1])
* KIA Cee'd Wagon 22493–22497 已批量复用同一 ED 五门旅行车尺寸组，采用 Kia 产品资料中的 4480 × 1790 × 1490 mm。
* 已纠正 SEAT 输入名称边界：22500–22504 实际对应 Altea XL 5P5，22505 对应标准 Altea 5P1，分别建立两个尺寸组。([Allegro][2])
* Isuzu D-Max 22498、22499 已确认发动机及 TFS86/TFS85 边界，但现有 Ktype 资料未锁定 Single、Extended、Double Cab，暂不猜测建组。([Cromax][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：55 行，覆盖 46 个 Ktype
* 明确 PENDING：2 行，覆盖 2 个 Ktype
* 尚未处理 Ktype：52
* PENDING／未完成 Ktype 合计：54
* 已确认尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22489_swb	22489	MPV	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	MEDIUM	Bus短轴低顶物理分支。	READY
22489_lwb	22489	MPV	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	MEDIUM	Bus长轴低顶物理分支。	READY
22490_swb_lowroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	MEDIUM	Kasten短轴低顶物理分支。	READY
22490_lwb_lowroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	MEDIUM	Kasten长轴低顶物理分支。	READY
22490_lwb_highroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	MEDIUM	Kasten长轴高顶物理分支。	READY
22493	22493	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22494	22494	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22495	22495	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22496	22496	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22497	22497	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22498	22498	Pickup	D-Max I	TFS86			LOW	Ktype未区分Single、Extended及Double Cab物理分支。	PENDING: 驾驶室外廓未锁定
22499	22499	Pickup	D-Max I	TFS85			LOW	Ktype未区分Single、Extended及Double Cab物理分支。	PENDING: 驾驶室外廓未锁定
22500	22500	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22501	22501	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22502	22502	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22503	22503	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22504	22504	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22505	22505	MPV	Altea I	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	标准Altea 5P1车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-KIA-CEED-I-WAGON-5D-01	4480	1790	1490	Kia cee'd 2007 Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581	Auto-Data	https://www.auto-data.net/en/seat-altea-xl-1.9-tdi-105hp-13573
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	Automoli	https://www.automoli.com/au/vehicles/seat/altea/altea-5p-2916/
```

## 下一步优先处理

1. 集中解决 Isuzu D-Max I 的 Single、Extended、Double Cab 尺寸及 Ktype 覆盖边界。
2. 批量闭合 22506–22530：Mondeo IV Hatchback、Wagon、Sedan及第一代 C-Max。
3. 优先复用 Mondeo 同车身发动机组，避免按动力版本重复核对。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/fahrzeuge/22489/renault/trafic_2_bus_jl_/2_0_16v_jl02_jl0l_jl0w_jl0n_22489?utm_source=chatgpt.com "2.0 16V (JL02, JL0L, JL0W, JL0N) | Trafic 2 Bus (JL) | Renault | Herstellerübersicht | Meyer Motoren"
[2]: https://allegro.pl/produkt/fare-sa-28939-zamek-drzwi-b9ad6b35-f8d6-4713-83a6-ac80b019fe84?srsltid=AfmBOorKzg5Yzsmvb0-60zuJ_9Bva3QtqVxhodUu7frUdGf_wqq404m2&utm_source=chatgpt.com "VIKA 1P0839015A Zamek drzwi"
[3]: https://cromax.hu/adatlap/2128752?utm_source=chatgpt.com "Kavo Parts IGP3501 izzítógyertya 151,5mm Isuzu D-Max I 2002-2012"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增 43 条 READY 映射，覆盖 22506–22530 共 25 个 Ktype。
* Mondeo IV 的 18 个 Ktype 按 Hatchback、Wagon、Sedan 车身及改款前后拆分。官方资料显示改款后各车身长度分别增加 6–7 mm，因此不能继续共用改款前尺寸组；不含后视镜宽度均为 1886 mm。([Dezo's Garage][1])
* C-Max 22524–22530 均确认属于 DM2 改款后五门车身，统一关联 4372 × 1825 × 1588 mm 尺寸组。([Dezo's Garage][2])
* D-Max 22498、22499 本轮未修改，仍不在证据不足时猜测驾驶室尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：98 行，覆盖 71 个 Ktype
* 明确 PENDING：2 行，覆盖 2 个 Ktype
* 尚未处理 Ktype：27
* PENDING／未完成 Ktype 合计：29
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22506_prefl	22506	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22506_facelift	22506	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22507_prefl	22507	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22507_facelift	22507	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22508_prefl	22508	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22508_facelift	22508	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22509_prefl	22509	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22509_facelift	22509	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22510_prefl	22510	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22510_facelift	22510	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22511_prefl	22511	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22511_facelift	22511	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22512_prefl	22512	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22512_facelift	22512	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22513_prefl	22513	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22513_facelift	22513	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22514_prefl	22514	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22514_facelift	22514	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22515_prefl	22515	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22515_facelift	22515	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22516_prefl	22516	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22516_facelift	22516	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22517_prefl	22517	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22517_facelift	22517	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22518_prefl	22518	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22518_facelift	22518	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22519_prefl	22519	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22519_facelift	22519	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22520_prefl	22520	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22520_facelift	22520	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22521_prefl	22521	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22521_facelift	22521	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22522_prefl	22522	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22522_facelift	22522	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22523_prefl	22523	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22523_facelift	22523	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22524	22524	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22525	22525	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22526	22526	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22527	22527	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22528	22528	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22529	22529	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22530	22530	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Ford Mondeo 2012 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Ford Mondeo 2012 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500	Ford Mondeo 2012 Owner's Manual; Automobile-Catalog	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/ENUSA_CG3536_MND_og_201204.pdf;https://www.automobile-catalog.com/car/2011/1595000/ford_mondeo_5-dr_2_0_trend.html
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588	Ford C-MAX UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf
```

## 下一步优先处理

1. 继续解决 D-Max I 的历史欧洲驾驶室边界及对应三维。
2. 批量处理 22531–22542：Passat R36 Sedan/Wagon、BMW E92/E93、Fiat Panda及Porsche Boxster。
3. 随后处理 22543–22557，闭合剩余 BMW、Fiat、Audi及VW车身组。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf"
[2]: https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已消除 D-Max I 的最后两个 PENDING：22498、22499 均拆分为 Single Cab、Space Cab、Double Cab；Single Cab 和 Double Cab 复用共同尺寸组，2.5 与 3.0 Space Cab 因外廓不同分别建组。([汽车数据网][1])
* 已闭合 22531–22557：Passat R36、BMW E92/E93、Panda 100HP、Boxster 987、Bravo II、Audi A5/S5、R8、Golf V Variant 与 Golf Plus。BMW E92/E93 跨改款的 Ktype 已按改款前后长度差异拆分。([AUSmotive][2])
* 已完成机械收尾检查：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、全部映射引用闭合、尺寸与来源完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：137 行
* PENDING 映射：0
* 已确认尺寸组：45
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22458	22458	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22459	22459	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22460	22460	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22461	22461	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22462	22462	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	HIGH	W204前期四门轿车。	READY
22463	22463	MPV	Materia I	M401	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M401五门车身。	READY
22464	22464	MPV	Materia I	M402	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M402五门车身。	READY
22465_3dr	22465	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	HIGH	T180三门物理分支。	READY
22465_5dr	22465	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	HIGH	T180五门物理分支。	READY
22466_3dr	22466	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
22466_5dr	22466	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
22467_3dr	22467	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
22467_5dr	22467	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
22468	22468	MPV	Materia I	M412	5	EU-DAIHATSU-MATERIA-I-MPV-5D-01	HIGH	M412四驱五门车身。	READY
22469_3dr	22469	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
22469_5dr	22469	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
22470_3dr	22470	Hatchback	Auris I	E150	3	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	三门物理分支。	READY
22470_5dr	22470	Hatchback	Auris I	E150	5	EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	HIGH	五门物理分支。	READY
22471	22471	Hatchback	Trevis I	L650	5	EU-DAIHATSU-TREVIS-I-HATCHBACK-5D-01	HIGH	L650五门车身。	READY
22472	22472	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22473	22473	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22474	22474	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22475_3dr	22475	Hatchback	Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	HIGH	1.8 SR/TS三门物理分支。	READY
22475_5dr	22475	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	HIGH	1.8 SR/TS五门物理分支。	READY
22476	22476	Coupe	Fortwo II	W451	3	EU-SMART-FORTWO-II-COUPE-01	HIGH	W451三门硬顶车身。	READY
22477	22477	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22478	22478	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22479	22479	Convertible	Fortwo II	A451	2	EU-SMART-FORTWO-II-CONVERTIBLE-01	HIGH	A451双门敞篷车身。	READY
22480	22480	SUV	C-Crosser I		5	EU-CITROEN-C-CROSSER-I-SUV-5D-01	HIGH	五门SUV标准车身。	READY
22481	22481	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22482	22482	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22483	22483	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22484	22484	MPV	Grand C4 Picasso I		5	EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	HIGH	第一代五门七座车身。	READY
22485	22485	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门标准车身。	READY
22486	22486	Hatchback	MINI II	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	R56三门标准车身。	READY
22487	22487	SUV	4007 I		5	EU-PEUGEOT-4007-I-SUV-5D-01	HIGH	第一代五门SUV车身。	READY
22488	22488	MPV	Espace IV Phase II		5	EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	HIGH	标准轴距Espace；不含Grand Espace长轴车身。	READY
22489_swb	22489	MPV	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	MEDIUM	Bus短轴低顶物理分支。	READY
22489_lwb	22489	MPV	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	MEDIUM	Bus长轴低顶物理分支。	READY
22490_swb_lowroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	MEDIUM	Kasten短轴低顶物理分支。	READY
22490_lwb_lowroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	MEDIUM	Kasten长轴低顶物理分支。	READY
22490_lwb_highroof	22490	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	MEDIUM	Kasten长轴高顶物理分支。	READY
22491	22491	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	HIGH	第二代改款前五门车身。	READY
22492	22492	SUV	Outlander II		5	EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	HIGH	第二代改款前五门车身。	READY
22493	22493	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22494	22494	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22495	22495	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22496	22496	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22497	22497	Wagon	Cee'd I	ED	5	EU-KIA-CEED-I-WAGON-5D-01	HIGH	ED五门旅行车。	READY
22498_singlecab	22498	Pickup	D-Max I	TFS86	2	EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-4X4-01	MEDIUM	TFS86单排驾驶室分支。	READY
22498_spacecab	22498	Pickup	D-Max I	TFS86	2	EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-01	MEDIUM	TFS86加长驾驶室分支。	READY
22498_doublecab	22498	Pickup	D-Max I	TFS86	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-4X4-01	MEDIUM	TFS86双排驾驶室分支。	READY
22499_singlecab	22499	Pickup	D-Max I	TFS85	2	EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-4X4-01	MEDIUM	TFS85单排驾驶室分支。	READY
22499_spacecab	22499	Pickup	D-Max I	TFS85	2	EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-02	MEDIUM	TFS85加长驾驶室分支。	READY
22499_doublecab	22499	Pickup	D-Max I	TFS85	4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-4X4-01	MEDIUM	TFS85双排驾驶室分支。	READY
22500	22500	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22501	22501	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22502	22502	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22503	22503	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22504	22504	MPV	Altea XL I	5P5	5	EU-SEAT-ALTEA-XL-I-MPV-5D-01	HIGH	Ktype对应Altea XL 5P5。	READY
22505	22505	MPV	Altea I	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	标准Altea 5P1车身。	READY
22506_prefl	22506	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22506_facelift	22506	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22507_prefl	22507	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22507_facelift	22507	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22508_prefl	22508	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22508_facelift	22508	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22509_prefl	22509	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22509_facelift	22509	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22510_prefl	22510	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22510_facelift	22510	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22511_prefl	22511	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22511_facelift	22511	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22512_prefl	22512	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	HIGH	改款前五门掀背车身。	READY
22512_facelift	22512	Hatchback	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	HIGH	2010年改款后五门掀背车身。	READY
22513_prefl	22513	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22513_facelift	22513	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22514_prefl	22514	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22514_facelift	22514	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22515_prefl	22515	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22515_facelift	22515	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22516_prefl	22516	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22516_facelift	22516	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22517_prefl	22517	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22517_facelift	22517	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22518_prefl	22518	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22518_facelift	22518	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22519_prefl	22519	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-PREFL-01	HIGH	改款前五门旅行车身。	READY
22519_facelift	22519	Wagon	Mondeo IV	BA7	5	EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	HIGH	2010年改款后五门旅行车身。	READY
22520_prefl	22520	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22520_facelift	22520	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22521_prefl	22521	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22521_facelift	22521	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22522_prefl	22522	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22522_facelift	22522	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22523_prefl	22523	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-PREFL-01	HIGH	改款前四门轿车车身。	READY
22523_facelift	22523	Sedan	Mondeo IV	BA7	4	EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	HIGH	2010年改款后四门轿车车身。	READY
22524	22524	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22525	22525	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22526	22526	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22527	22527	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22528	22528	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22529	22529	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22530	22530	MPV	C-Max I facelift	DM2	5	EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	HIGH	DM2改款后五门MPV车身。	READY
22531	22531	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-R36-SEDAN-01	HIGH	R36四门轿车车身。	READY
22532	22532	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-R36-WAGON-01	HIGH	R36五门旅行车身。	READY
22533_prefl	22533	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	E92改款前双门Coupe。	READY
22533_facelift	22533	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	E92 LCI双门Coupe。	READY
22534	22534	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	130 kW版本对应E92改款前车身。	READY
22535_prefl	22535	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	E93改款前双门敞篷车身。	READY
22535_facelift	22535	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	E93 LCI双门敞篷车身。	READY
22536_prefl	22536	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	E93改款前双门敞篷车身。	READY
22536_facelift	22536	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	E93 LCI双门敞篷车身。	READY
22537_prefl	22537	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	E93改款前双门敞篷车身。	READY
22537_facelift	22537	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	E93 LCI双门敞篷车身。	READY
22538_prefl	22538	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	E93改款前双门敞篷车身。	READY
22538_facelift	22538	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	E93 LCI双门敞篷车身。	READY
22539	22539	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	170 kW版本对应E93改款前车身。	READY
22540	22540	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-HATCHBACK-100HP-01	HIGH	Panda 100HP五门低车身版本。	READY
22541	22541	Convertible	Boxster II	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	HIGH	987双门敞篷标准车身。	READY
22542	22542	Convertible	Boxster II	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	HIGH	987双门敞篷标准车身。	READY
22543	22543	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	145 kW版本对应E92改款前车身。	READY
22544	22544	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-HATCHBACK-5D-01	HIGH	198五门掀背车身。	READY
22545	22545	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-HATCHBACK-5D-01	HIGH	198五门掀背车身。	READY
22546	22546	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-HATCHBACK-5D-01	HIGH	198五门掀背车身。	READY
22547_prefl	22547	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	8T3改款前双门Coupe。	READY
22547_facelift	22547	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-FACELIFT-01	HIGH	8T3改款后双门Coupe。	READY
22548	22548	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	3.2 FSI对应改款前车身。	READY
22549	22549	Coupe	S5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	4.2 FSI S5改款前双门Coupe。	READY
22550	22550	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	2.7 TDI对应改款前车身。	READY
22551	22551	Coupe	A5 I	8T3	2	EU-AUDI-A5-8T3-COUPE-PREFL-01	HIGH	176 kW 3.0 TDI对应改款前车身。	READY
22552	22552	Coupe	R8 I	42	2	EU-AUDI-R8-I-COUPE-V8-PREFL-01	HIGH	42型V8双门Coupe。	READY
22553	22553	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH	1K5五门旅行车身。	READY
22554	22554	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH	1K5五门旅行车身。	READY
22555	22555	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH	1K5五门旅行车身。	READY
22556	22556	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH	1K5五门旅行车身。	READY
22557	22557	Hatchback	Golf Plus V	5M1	5	EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	HIGH	5M1五门高顶掀背车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1301-1400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-PREFL-01	4581	1770	1447	Mercedes-Benz Public Archive; Automobile-Catalog	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://www.automobile-catalog.com/car/2007/1550015/mercedes-benz_c_200_cdi.html
EU-DAIHATSU-MATERIA-I-MPV-5D-01	3800	1690	1635	Daihatsu Materia brochure; Automobile-Catalog	https://www.ademosthenous.com/documents/Daihatsu_Materia_Brochure.pdf;https://www.automobile-catalog.com/car/2007/581720/daihatsu_materia_1_3.html
EU-TOYOTA-AURIS-I-HATCHBACK-T180-01	4220	1760	1505	Toyota Auris first-generation launch press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Auris-1st-gen-launch-press-pack.pdf
EU-TOYOTA-AURIS-I-HATCHBACK-STANDARD-01	4220	1760	1515	Toyota Auris first-generation launch press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Auris-1st-gen-launch-press-pack.pdf
EU-DAIHATSU-TREVIS-I-HATCHBACK-5D-01	3400	1475	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/581135/daihatsu_trevis.html
EU-SMART-FORTWO-II-COUPE-01	2695	1559	1542	smart fortwo technical data brochure; Automobile-Catalog	https://manuals.plus/m/6fac10729c057a642579716f82884368eb1a31c20d0e3a920c3ac7df599df96c.pdf;https://www.automobile-catalog.com/car/2007/3155000/smart_fortwo_coupe_84.html
EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	3800	1695	1530	Toyota Yaris SR second-generation press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen2-Yaris-SR-archive-press-pack.pdf
EU-SMART-FORTWO-II-CONVERTIBLE-01	2695	1559	1542	smart fortwo technical data brochure	https://manuals.plus/m/6fac10729c057a642579716f82884368eb1a31c20d0e3a920c3ac7df599df96c.pdf
EU-CITROEN-C-CROSSER-I-SUV-5D-01	4645	1805	1715	2007 Citroën C-Crosser UK brochure; Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/09/2007-Citroen-C-Crosser-UK.pdf;https://www.automobile-catalog.com/car/2007/552605/citroen_c-crosser_hdi_155_fap_tendace.html
EU-CITROEN-GRAND-C4-PICASSO-I-MPV-5D-01	4590	1830	1710	Citroën C4 Picasso and Grand C4 Picasso technical brochure	https://www.xr793.com/wp-content/uploads/2020/09/2012-Citroen-C4-Picasso-Grand-C4-Picasso.pdf
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	BMW Group MINI Product Guide 2009; Automobile-Catalog	https://www.press.bmwgroup.com/canada/article/attachment/T0036807EN/56874;https://www.automobile-catalog.com/car/2007/1753085/mini_one.html
EU-PEUGEOT-4007-I-SUV-5D-01	4637	1808	1715	Peugeot 4007 UK official brochure	https://xr793.com/wp-content/uploads/2022/12/2007-Peugeot-4007-UK.pdf
EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	4656	1860	1728	Renault Espace Phase II brochure; Auto-Data	https://forum.renaultespace.pl/plikownia/espace-4/prospekty/2008%20EN%20Ph2.pdf;https://www.auto-data.net/en/renault-espace-iv-phase-ii-2006-2.0-dci-150hp-20273
EU-RENAULT-TRAFIC-II-PH2-VAN-SWB-LOWROOF-01	4782	1904	1960	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-LOWROOF-01	5182	1904	1969	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-RENAULT-TRAFIC-II-PH2-VAN-LWB-HIGHROOF-01	5182	1904	2464	Renault UK New Trafic range press information; Transit Center Trafic II technical specifications	https://www.press.renault.co.uk/releases/2135;https://www.transitcenter.uk/renault-traficii-technical-specifications-t-75.html
EU-MITSUBISHI-OUTLANDER-II-SUV-PREFL-01	4640	1800	1720	Auto-Data	https://www.auto-data.net/en/mitsubishi-outlander-ii-generation-3392
EU-KIA-CEED-I-WAGON-5D-01	4480	1790	1490	Kia cee'd 2007 Product Guide	https://www.kia-bg.com/docs/ceed/cee%27d_Product%20Guide.pdf
EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-4X4-01	5030	1720	1635	Auto-Data D-Max I 3.0 TD Single Cab 4WD	https://www.auto-data.net/en/isuzu-d-max-i-3.0-td-single-cab-163hp-4wd-15979
EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-01	5030	1800	1715	Auto-Data D-Max I 2.5 TD Space Cab	https://www.auto-data.net/gr/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-4X4-01	5035	1800	1735	Auto-Data D-Max I 2.5 TD Double Cab; Auto-Data D-Max I 3.0 TD Double Cab	https://www.auto-data.net/gr/isuzu-d-max-i-2.5-td-double-cab-136hp-15974;https://www.auto-data.net/es/isuzu-d-max-i-3.0-td-double-cab-163hp-15977
EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-02	5155	1800	1730	Auto-Data D-Max I 3.0 TD Space Cab 4WD	https://www.auto-data.net/en/isuzu-d-max-i-3.0-td-space-cab-163hp-4wd-15980
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581	Auto-Data	https://www.auto-data.net/en/seat-altea-xl-1.9-tdi-105hp-13573
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	Automoli	https://www.automoli.com/au/vehicles/seat/altea/altea-5p-2916/
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500	Ford Mondeo 2012 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512	Ford Mondeo 2012 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2012-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500	Ford Mondeo 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Mondeo-UK.pdf
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500	Ford Mondeo 2012 Owner's Manual; Automobile-Catalog	https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/ENUSA_CG3536_MND_og_201204.pdf;https://www.automobile-catalog.com/car/2011/1595000/ford_mondeo_5-dr_2_0_trend.html
EU-FORD-C-MAX-I-FACELIFT-MPV-5D-01	4372	1825	1588	Ford C-MAX UK brochure	https://xr793.com/wp-content/uploads/2022/09/2010-Ford-C-MAX-UK.pdf
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447	Volkswagen Passat R36 Specifications	https://www.ausmotive.com/downloads/Volkswagen/Passat-R36-specs.pdf
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456	Volkswagen Passat R36 Specifications	https://www.ausmotive.com/downloads/Volkswagen/Passat-R36-specs.pdf
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	BMW Group 3 Series Coupé Technical Data	https://www.press.bmwgroup.com/japan/article/attachment/T0013372JA/30239
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	BMW Group 3 Series Coupé LCI Technical Data	https://www.press.bmwgroup.com/spain/article/attachment/T0084820ES/132010
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384	BMW Group 3 Series Convertible Technical Data	https://www.press.bmwgroup.com/usa/article/attachment/T0018124EN_US/42510
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	Auto-Data BMW 3 Series Convertible E93 LCI	https://www.auto-data.net/en/bmw-3-series-convertible-e93-lci-facelift-2010-320i-170hp-17747
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522	Fiat Panda 2007 UK brochure	https://xr793.com/wp-content/uploads/2023/01/2007-Fiat-Panda-UK.pdf
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292	Porsche Boxster 2007 Owner's Manual	https://www.carmanualsonline.info/porsche-boxster-2007-2-g-owners-manual/?srch=dimensions
EU-FIAT-BRAVO-II-HATCHBACK-5D-01	4336	1792	1498	Fiat Bravo 2007 Owner's Manual	https://www.onlymanuals.com/fiat/bravo/fiat_bravo_owners_manual_2007_2007
EU-AUDI-A5-8T3-COUPE-PREFL-01	4625	1854	1372	Audi A5 3.2 FSI Technical Specifications; Audi S5 4.2 FSI Technical Specifications	https://www.australiancar.reviews/_pdfs/Audi_A5Coupe-32FSI_8T_TechnicalSpecifications_200712.pdf;https://www.audiworld.com/model/s5/11/11S5_cpe_tech.pdf
EU-AUDI-A5-8T3-COUPE-FACELIFT-01	4626	1854	1372	Audi UK A5 Coupé technical specification	https://press.audi.co.uk/assets/documents/original/15950-AudiUK00000101A5Coup%C3%A920TDImultitronic.pdf
EU-AUDI-R8-I-COUPE-V8-PREFL-01	4431	1904	1252	Audi UK R8 4.2 V8 Technical Specification	https://press.audi.co.uk/assets/documents/original/24227-AudiUK00000771R842V8TechnicalSpecification.pdf
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Volkswagen Newsroom Golf V Variant profile	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-5-variant-profile-19526
EU-VW-GOLF-PLUS-V-HATCHBACK-5D-01	4206	1759	1580	Volkswagen Golf Plus 2005 Service Training	https://volkswagen.manymanuals.com/cars/2005-golf-plus/service-manual-3890
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1301-1400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/isuzu-d-max-i-3.0-td-single-cab-163hp-4wd-15979 "https://www.auto-data.net/en/isuzu-d-max-i-3.0-td-single-cab-163hp-4wd-15979"
[2]: https://www.ausmotive.com/downloads/Volkswagen/Passat-R36-specs.pdf "https://www.ausmotive.com/downloads/Volkswagen/Passat-R36-specs.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1301-1400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1301-1400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1376 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（688 行）
