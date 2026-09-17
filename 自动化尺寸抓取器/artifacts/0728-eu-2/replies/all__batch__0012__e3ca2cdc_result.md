# 任务：all 第 1101-1200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0012__e3ca2cdc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1101-1200 行

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
all 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6	3.2 FSI Quattro	Stufenheck	Allrad	Benzin	183	249	Sep 2006	Oct 2008	2024-03-01	21323
Mitsubishi	L 300 iii	2.5 TD	Bus	Heckantrieb	Diesel	64	87	Feb 1987	May 2003	2024-03-01	21329
Jaguar	Xj	4	Coupe	Heckantrieb	Benzin	175	238	Oct 1986	Dec 1989	2024-03-01	21330
Jaguar	Xjsc convertible	4	Cabriolet	Heckantrieb	Benzin	175	238	Oct 1987	Dec 1989	2024-03-01	21335
Mitsubishi	Lancer v	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Jun 1992	Feb 1995	2024-03-01	21346
Audi	A6 c4	2	Stufenheck	Frontantrieb	Benzin	79	107	Jun 1994	Jul 1995	2024-03-01	21350
Alfa Romeo	Spider	2	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1974	Dec 1984	2024-03-01	21354
Toyota	Supra	3	Coupe	Heckantrieb	Benzin	140	190	Jan 1986	May 1993	2024-03-01	21355
Peugeot	405 i break	1.4	Kombi	Frontantrieb	Benzin	47	64	May 1988	Jul 1992	2024-03-01	21360
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	160	218	May 1982	Aug 1988	2024-11-01	21375
Maserati	Biturbo	E	Coupe	Heckantrieb	Benzin	139	189	Jun 1982	Oct 1987	2024-03-01	21401
Mitsubishi	Lancer vii	EVO IX	Stufenheck	Allrad	Benzin	213	290	Aug 2005	Sep 2006	2024-03-01	21408
Fiat	Ducato	2.0 4X4	Bus	Allrad	Benzin	80	109	Nov 1994	Nov 2001	2024-03-01	21437
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	108	147	Jan 1994	May 1999	2024-03-01	21442
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	165	224	Nov 1995	May 1999	2024-03-01	21443
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	108	147	Sep 1993	May 1999	2024-03-01	21444
Peugeot	Partner	1.9 D	Großraumlimousine	Frontantrieb	Diesel	51	69	May 1996	Dec 1998	2024-03-01	21448
Chevrolet	Lumina apv	3.8	Großraumlimousine	Frontantrieb	Benzin	123	167	Oct 1991	Sep 1995	2024-03-01	21450
Buick	Skylark	2.3 Limited	Stufenheck	Frontantrieb	Benzin	86	117	Sep 1992	Sep 1993	2024-03-01	21452
Cadillac	Seville	4.5	Stufenheck	Frontantrieb	Benzin	115	156	Oct 1987	Sep 1989	2024-03-01	21453
Cadillac	Seville	4.9	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1990	Dec 1991	2024-03-01	21454
Hyundai	H-1 / starex	2.4	Bus	Heckantrieb	Benzin	101	137	Feb 2003	Apr 2004	2024-03-01	21455
Chevrolet	Camaro	3.1	Coupe	Heckantrieb	Benzin	103	140	Oct 1989	Sep 1992	2024-03-01	21464
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	127	173	Oct 1987	Sep 1992	2024-03-01	21465
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	168	228	Oct 1984	Sep 1992	2024-03-01	21466
Chevrolet	Camaro	3.8	Coupe	Heckantrieb	Benzin	149	203	Oct 1995	Sep 1997	2024-03-01	21467
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1986	Sep 1988	2024-03-01	21469
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	179	243	Oct 1985	Sep 1989	2024-03-01	21472
Fiat	Palio	1.2	Schrägheck	Frontantrieb	Benzin	50	68	Jun 1999	Oct 2000	2024-03-01	21473
Suzuki	Wagon r	1	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2004	Aug 2005	2024-03-01	21480
Suzuki	Wagon r	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Jun 2004	Aug 2005	2024-03-01	21481
Buick	Park avenue	3.8	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1994	Oct 1996	2024-03-01	21494
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1998	Jul 2002	2024-03-01	21499
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	107	146	Aug 2002	Oct 2005	2024-03-01	21500
Peugeot	206	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Aug 1998	Jul 2000	2024-03-01	21501
Mazda	2	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Feb 2003	Jun 2007	2024-03-01	21509
Jeep	Cherokee	2.5 SE	Geländewagen geschlossen	Heckantrieb	Benzin	87	118	Oct 1996	Sep 1999	2024-03-01	21520
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	89	121	Oct 1990	Sep 1996	2024-03-01	21521
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21522
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21523
Jeep	Cherokee	4	Geländewagen geschlossen	Heckantrieb	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21524
Jeep	Cherokee	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21525
Jeep	Cherokee	2.1 D 4X4	Geländewagen geschlossen	Allrad	Diesel	59	80	Oct 1986	Sep 1992	2024-03-01	21526
Lamborghini	Diablo	5.7	Coupe	Heckantrieb	Benzin	361	491	Mar 1990	Jan 1999	2024-03-01	21533
Mitsubishi	L400	2	Bus	Heckantrieb	Benzin	83	113	Sep 1995	Oct 2002	2024-03-01	21535
Mitsubishi	L400	2.4	Bus	Heckantrieb	Benzin	97	132	May 1995	Oct 2002	2024-03-01	21536
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	201	273	May 2000	Sep 2002	2024-03-01	21543
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	213	290	Sep 1999	Dec 2006	2024-03-01	21544
Chevrolet	Tahoe	5.3 AWD	SUV	Allrad	Benzin	213	290	Oct 2002	Dec 2006	2024-03-01	21545
Mazda	Tribute	2.3 GX	SUV	Frontantrieb	Benzin	110	150	Dec 2003	Oct 2004	2024-03-01	21546
Tata	Indica	1.4 L	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1998	Sep 2002	2024-03-01	21548
Aston Martin	Zagato vantage	6.0 V12	Coupe	Heckantrieb	Benzin	380	517	May 2012	-	2024-03-01	21550
Nissan	X-Trail i	2.0 4X4	SUV	Allrad	Benzin	110	150	Sep 2001	Jan 2013	2024-03-01	21555
Nissan	X-Trail i	2.2 DCI	SUV	Frontantrieb	Diesel	84	114	Oct 2004	Jan 2013	2024-03-01	21557
Hyundai	Terracan	2.5 D	SUV	Heckantrieb	Diesel	74	101	Jun 2001	Oct 2003	2024-03-01	21559
Honda	Jazz ii	1.5 Vtec	Schrägheck	Frontantrieb	Benzin	81	110	Apr 2002	Jul 2008	2024-03-01	21561
Renault	Thalia i	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1998	Oct 2008	2025-12-01	21562
Mercedes-benz	Clk	CLK 500	Coupe	Heckantrieb	Benzin	285	388	Jun 2006	May 2009	2024-03-01	21568
Porsche	Cayenne	3.2	SUV	Allrad	Benzin	177	241	Aug 2003	Sep 2007	2024-03-01	21569
Renault	Espace iv	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	85	116	Apr 2003	Feb 2005	2024-03-01	21576
Chrysler	300c	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Jun 2005	Nov 2012	2024-03-01	21586
Infiniti	Fx	35	SUV	Heckantrieb	Benzin	206	280	Feb 2003	Dec 2008	2024-03-01	21587
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	155	211	Mar 2006	May 2010	2024-03-01	21589
Jeep	Compass	2.4	SUV	Frontantrieb	Benzin	125	170	Aug 2006	-	2024-03-01	21591
Jeep	Compass	2.0 CRD	SUV	Frontantrieb	Diesel	103	140	Aug 2006	-	2024-03-01	21592
Peugeot	Boxer	3.0 HDI 155	Kasten	Frontantrieb	Diesel	115	156	Jul 2006	Dec 2015	2024-03-01	21593
Peugeot	Boxer	3.0 HDI 155	Pritsche/Fahrgestell	Frontantrieb	Diesel	115	156	Apr 2006	Dec 2015	2024-03-01	21594
Cadillac	Allante	4.5	Cabriolet	Frontantrieb	Benzin	150	204	Oct 1988	Sep 1992	2024-03-01	21641
Cadillac	Allante	4.6	Cabriolet	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21642
Cadillac	Allante	4.5	Coupe	Frontantrieb	Benzin	150	204	Jan 1991	Sep 1992	2024-03-01	21643
Cadillac	Allante	4.6	Coupe	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21644
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	190	258	Aug 2013	Jul 2018	2024-03-01	21691
Ford	Mondeo i	2.0 I 16V 4X4	Stufenheck	Allrad	Benzin	100	136	Feb 1993	Aug 1996	2024-03-01	21709
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	103	140	Oct 1984	Sep 1985	2024-03-01	21714
Chevrolet	Astro	4.3	Bus	Heckantrieb	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21717
Chevrolet	Astro	4.3 AWD	Bus	Allrad	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21718
Chevrolet	Astro	4.3 Luxury	Bus	Heckantrieb	Benzin	119	162	Oct 1986	Sep 1994	2024-03-01	21719
Chevrolet	Astro	4.3 Luxury AWD	Bus	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21720
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	107	146	Oct 1989	Sep 1994	2024-03-01	21721
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	119	162	Oct 1984	Sep 1994	2024-03-01	21722
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21723
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	127	173	Oct 1994	Sep 1995	2024-03-01	21726
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21727
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21728
Jeep	Wrangler iii	3.8 RWD	Geländewagen offen	Heckantrieb	Benzin	146	199	Oct 2007	Sep 2010	2024-03-01	21750
Honda	Beat	0.7	Cabriolet	Heckantrieb	Benzin	47	64	May 1991	Sep 1996	2024-03-01	21757
Daihatsu	Terios	1.5 Vvt-i RWD	Geländewagen geschlossen	Heckantrieb	Benzin	77	105	Nov 2005	-	2024-03-01	21760
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	119	162	Oct 1991	Sep 1996	2024-03-01	21786
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	149	203	Oct 1996	Sep 1999	2024-03-01	21788
Chevrolet	C1500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2000	2024-03-01	21789
Chevrolet	C2500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2001	2024-03-01	21796
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	103	140	Oct 2013	Aug 2020	2024-03-01	21803
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Oct 2013	Aug 2020	2024-03-01	21804
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	105	143	Oct 2013	Aug 2018	2024-03-01	21805
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	112	152	Sep 1980	Dec 1984	2024-03-01	21821
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	114	155	Oct 1982	Sep 1986	2024-03-01	21822
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	100	136	Oct 1987	Sep 1990	2024-03-01	21823
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	104	141	Oct 1986	Sep 1989	2024-03-01	21824
Chevrolet	Caprice	4.3	Stufenheck	Heckantrieb	Benzin	149	203	Oct 1991	Sep 1996	2024-03-01	21825
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	127	173	Oct 1990	Sep 1993	2024-03-01	21826


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 Audi A6 C6、Chevrolet Camaro III/IV、BMW X5 F15、Seat Leon III ST 2.0 TDI 150 共 **5 个 Ktype、7 条 READY 映射**。
* Ktype `21464` 覆盖 Camaro III 改款前后两套外廓，已拆为 `prefl` 与 `facelift`，未保留无后缀基础行。([汽车目录][1])
* A6 C6 采用欧洲 4F/C6 Sedan 尺寸，并用明确标注不含后视镜宽度的资料闭合。([Bind][2])
* Camaro IV 与 BMW X5 F15 的门数、代际和不含后视镜宽度已经闭合。([汽车数据网][3])
* Seat Leon III ST 150 hp 柴油版确认存在改款前后两套外廓；改款后尺寸同时由 SEAT 技术资料和明确的 without-mirrors 口径交叉闭合。([汽车数据网][4])
* MX-5 NB 的当前资料存在同代高度和市场规格冲突；Leon ST 的 140 hp、143 hp 版本边界也尚未闭合，因此未强行建组。([汽车数据网][5])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：5
* READY 映射：7
* 未闭合 Ktype：95

  * 本轮已明确标记 PENDING：4
  * 尚待处理：91
* 已确认尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21323	21323	Sedan	A6 C6	4F	4	EU-AUDI-A6-C6-SEDAN-4D-01	HIGH		READY
21464_prefl	21464	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-PREFL-01	HIGH	1990款改款前外廓。	READY
21464_facelift	21464	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-FACELIFT-01	HIGH	1991-1992改款后外廓。	READY
21467	21467	Coupe	Camaro IV		3	EU-CHEVROLET-CAMARO-IV-COUPE-3D-01	HIGH		READY
21499	21499	Convertible	MX-5 II	NB	2		MEDIUM	NB前期候选；同代资料高度与市场规格冲突。	PENDING: 尺寸组未闭合
21500	21500	Convertible	MX-5 II	NB	2		MEDIUM	NB后期候选；同代资料高度与市场规格冲突。	PENDING: 尺寸组未闭合
21691	21691	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-5D-01	HIGH		READY
21803	21803	Wagon	Leon III ST		5		MEDIUM	140 hp版本边界与ST车身资料未闭合。	PENDING: 版本边界未确认
21804_prefl	21804	Wagon	Leon III ST		5	EU-SEAT-LEON-III-ST-WAGON-PREFL-01	HIGH	2013-2016改款前外廓。	READY
21804_facelift	21804	Wagon	Leon III ST		5	EU-SEAT-LEON-III-ST-WAGON-FACELIFT-01	HIGH	2016-2020改款后外廓。	READY
21805	21805	Wagon	Leon III ST		5		MEDIUM	143 hp版本边界与ST车身资料未闭合。	PENDING: 版本边界未确认
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-SEDAN-4D-01	4916	1855	1459	Bind Audi A6 4F/C6 3.2 FSI quattro 249 hp; Automobile-Catalog 2007 Audi A6 3.2 FSI Quattro	https://bind.lt/en/technical-specifications/audi/a6/4f-c6/sedan/3-2-fsi-mt-quattro-249-hp;https://www.automobile-catalog.com/car/2007/251975/audi_a6_3_2_fsi_quattro.html
EU-CHEVROLET-CAMARO-III-COUPE-PREFL-01	4877	1849	1278	Automobile-Catalog 1990 Chevrolet Camaro RS 3.1	https://www.automobile-catalog.com/car/1990/459935/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html
EU-CHEVROLET-CAMARO-III-COUPE-FACELIFT-01	4892	1839	1280	Automobile-Catalog 1992 Chevrolet Camaro RS 3.1	https://www.automobile-catalog.com/car/1992/460115/chevrolet_camaro_rs_3_1l_v-6_mfi.html
EU-CHEVROLET-CAMARO-IV-COUPE-3D-01	4907	1882	1303	Auto-Data Chevrolet Camaro IV 3.8 V6; Edmunds 1995 Chevrolet Camaro specifications	https://www.auto-data.net/en/chevrolet-camaro-iv-3.8-i-v6-200hp-14563;https://www.edmunds.com/chevrolet/camaro/1995/features-specs/
EU-BMW-X5-F15-SUV-5D-01	4886	1938	1762	Auto-Data BMW X5 F15 30d xDrive	https://www.auto-data.net/en/bmw-x5-f15-30d-258hp-xdrive-steptronic-18605
EU-SEAT-LEON-III-ST-WAGON-PREFL-01	4535	1816	1451	Auto-Data Seat Leon III ST 2.0 TDI 150 Hp; Auto-Data Seat Leon III ST 1.8 TSI width-basis cross-check	https://www.auto-data.net/en/seat-leon-iii-st-2.0-tdi-150hp-start-stop-19375;https://www.auto-data.net/en/seat-leon-iii-st-1.8-tsi-180hp-start-stop-dsg-19416
EU-SEAT-LEON-III-ST-WAGON-FACELIFT-01	4549	1816	1454	SEAT Technical Specifications New SEAT Leon ST 2016; Automobile Dimension Seat Leon ST 2017	https://mundoseat.seat.com/mediacenter_netstor/seat-media-center/global_site/documents/Leon-ST/en/Technical_Specifications-New_SEAT_Leon_ST_2016_EN.pdf;https://www.automobiledimension.com/model/seat/leon-st
```

## 下一步优先处理

1. 闭合 Jeep Cherokee XJ 的改款前后、门数及尺寸边界，批量处理 Ktype `21520–21526`。
2. 按 Passenger Bus、Cargo Van、AWD/RWD 和代际外廓处理 Chevrolet Astro Ktype `21714、21717–21728`。
3. 核对 Chevrolet Tahoe 欧洲出口版与北美版宽度差异，处理 `21543–21545`。
4. 闭合 Cadillac Allanté、Chevrolet Caprice 的 Convertible/Coupe、Sedan/Wagon 外廓边界。
5. 解决 MX-5 NB 和 Leon ST 140/143 hp 的现有 PENDING。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1990/459935/chevrolet_camaro_rs_3_1l_v-6_mfi_automatic.html?utm_source=chatgpt.com "1990 Chevrolet Camaro RS 3.1L V-6 MFI automatic (aut. 4)"
[2]: https://bind.lt/en/technical-specifications/audi/a6/4f-c6/sedan/3-2-fsi-mt-quattro-249-hp "Audi A6 - 3.2 FSI MT quattro (249 hp) Sedan - 4F/C6 - Technical data - Bind"
[3]: https://www.auto-data.net/en/chevrolet-camaro-iv-3.8-i-v6-200hp-14563 "Chevrolet Camaro IV 3.8 i V6 (200 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/seat-leon-iii-st-2.0-tdi-150hp-start-stop-19375 "https://www.auto-data.net/en/seat-leon-iii-st-2.0-tdi-150hp-start-stop-19375"
[5]: https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8-i-16v-140hp-11259 "Mazda MX-5 II (NB) 1.8 i 16V (140 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
#### 更新点

更新点

* 闭合 Cadillac Allanté Ktype `21641- 闭合 Cadillac Allanté Ktype `21641–21644`，新增 **4 个 READY–21644`，新增 **4 个 READY Ktype、6 条 READY 映射、3 个尺寸组**。
  Ktype、6 条 READY 映射、3 个尺寸组**。
* `216- `21641` 跨越 1989–1990 与 199141` 跨越 1989([汽车目录][1])1643`、`21644`对应可拆卸硬顶配置，映射表保留`Cou应可拆卸硬顶配置，映射表保留 `Coupe` 分类并pe` 分类并与相应年份与相应年份的已核的已核定外廓组关联定外廓组关联，不另，不另造重复尺寸组。cite造重复尺寸组。citeturn987245search21turn987245search5turn987245search21turn987245search5turn987245search12turn987245search19turn987245search12turn987245search19turn443686search12turnturn443686search12turn443686search21

## 当前批次进度

443686search21

## 当前批次进度

* 输入 Ktype：100
* READY K- 输入 Ktype：100
* READY Ktype：9
* READY 映射：13
* 尚未闭type：9
* READY 映射：13
* 尚未闭合 Ktype：91

  * 已明确标记 PENDING：4合 Ktype：91
  * 已明确标记 PENDING：4
  * 尚待处理：87
* 已确认尺寸组：10

  * 尚待处理：87
* 已确认尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的

* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

````tsv
id	Ktype	Normalized Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21641_pre91	21641	ConvertibleConfidence	Notes	IterationStatus
21641_pre91	21641	Convertible	Allanté	V	2	EU-CADILLAC	Allanté	V	2	EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1989-1990-01	H-ALLANTE-V-CONVERTIBLE-1989-1990-01	HIGH	1989-1990外廓分支。	READY
IGH	1989-1990外廓分支。	READY
21641_91plus	21641	Convertible21641_91plus	21641	Convertible	Allanté	V	2	EU-CADILLAC-ALLANTE	Allanté	V	2	EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1991-1992-01	HIGH	199-V-CONVERTIBLE-1991-1992-01	HIGH	1991-1992外廓分支。	READY
2161-1992外廓分支。	READY
21642	21642	Convertible42	21642	Convertible	Allanté	V	2	EU-CADILLAC-ALLANTE	Allanté	V	2	EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1993-01	HIGH		READY
216-V-CONVERTIBLE-1993-01	HIGH		READY
21643	21643	Coupe	Allanté	V	2	E43	21643	Coupe	Allanté	V	2	EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1991-U-CADILLAC-ALLANTE-V-CONVERTIBLE-1991-1992-01	HIGH	可拆卸硬顶配置。	READY1992-01	HIGH	可拆卸硬顶配置。	READY
21644	21644	Coupe	Allanté	V	2	E
21644	21644	Coupe	Allanté	V	2	EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1993-U-CADILLAC-ALLANTE-V-CONVERTIBLE-1993-01	HIGH	可拆卸硬顶配置。	READY
````

01	HIGH	可拆卸硬顶配置。	READY

````

## 本轮首次创建/修正的 DIENSION_GROUP TSV

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	Height```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
MM	DimensionSource	SourceURL
EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1989-EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1989-1990-01	4537	1866	1327	Automobile1990-01	4537	1866	1327	Automobile-Catalog 1989 Cadillac Allante;-Catalog 1989 Cadillac Allante; Automobile-Catalog 1990 Cadillac Automobile-Catalog 1990 Cadillac Allante	https://www.automobile-catalog.com/car/1989 Allante	https://www.automobile-catalog.com/car/1989/60470/cadillac_allante.html;https://www./60470/cadillac_allante.html;https://www.automobile-catalog.com/car/1990/1497230/cadillacautomobile-catalog.com/car/1990/1497230/cadillac_allante.html
EU-CADILLAC-ALLANTE-V-CONVERTIBLE_allante.html
EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1991-1992-01	4539	1866	130-1991-1992-01	4539	1866	1308	Automobile-Catalog 1991 Cadillac8	Automobile-Catalog 1991 Cadillac Allante; Automobile-Catalog 1992 Cadillac Allante; Automobile-Catalog 1992 Cadillac Allante Hard-top	https://www.automobile-catalog.com/car/ Allante Hard-top	https://www.automobile-catalog.com/car/1991/332660/cadillac_allante.html;https://www.1991/332660/cadillac_allante.html;https://www.automobile-catalog.com/car/1992/1497275/cadillacautomobile-catalog.com/car/1992/1497275/cadillac_allante_hard-top.html
EU-CADILLAC-ALLANTE-V_allante_hard-top.html
EU-CADILLAC-ALLANTE-V-CONVERTIBLE-1993-01	4539	1866	130-CONVERTIBLE-1993-01	4539	1866	1308	Automobile-Catalog 1993 Cadillac8	Automobile-Catalog 1993 Cadillac Allante	https://www.automobile-catalog.com/car/1993 Allante	https://www.automobile-catalog.com/car/1993/332675/cadillac_allante.html
````

## 下一/332675/cadillac_allante.html

```

## 下一步优先处理

1. 闭合 Chevrolet Tahoe步优先处理

1. 闭合 Chevrolet Tahoe `21543–21545` 的 `21543–21545` 的 B2W/GMT800 B2W/GMT800 欧洲规格 欧洲规格与 RWD/AWD高度与 RWD/AWD高度边界。
2. 批量处理 Jeep边界。
2. 批量处理 Jeep Cherokee XJ `21520–21526 Cherokee XJ `21520–21526`，按年份外`，按年份外廓变化和驱动高度廓变化和驱动高度差拆差拆分。
3. 处理 Chevrolet Astro `21714、分。
3. 处理 Chevrolet Astro `21714、21717–21728` 的 Passenger/C21717–21728` 的 Passenger/Cargo 与前argo 与前后期车身尺寸后期车身尺寸。
4. 解决上一轮遗留的 MX-5 NB。
4. 解决上一轮遗留的 MX-5 NB 与 与 Seat Leon Seat Leon ST `21803、21805`。

推进信号：CONTINUE ST `21803、21805`。

推进信号：CONTINUE
```

[1]: https://www.automobile-catalog.com/car/1989/60470/cadillac_allante.html?utm_source=chatgpt.com "1989 Cadillac Allante Specs Review (149 kW / 203 PS / 200 hp) (since mid-year 1988 for North America )"


--- 发送 / 推进信号纠偏 / Round 3 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 修正上一轮累计计数：上一轮结束时实际为 **READY Ktype 9、READY 映射 12、尺寸组 10**。
* 本轮闭合 Mazda Tribute、Tata Indica、Aston Martin V12 Zagato、Porsche Cayenne 955、Infiniti FX S50、Honda Beat PP1，共新增 **6 个 READY Ktype、6 条 READY 映射、6 个尺寸组**。
* Mazda Tribute 的 Ktype `21546` 已确认对应 `EP3W` 五门前驱车身；Honda Beat 已确认 `PP1` 车身代码和官方外廓。([www.thansen.dk][1])
* Tahoe 与 Cherokee 暂未修改：现有资料仍涉及年份、改款或高度口径边界，未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：15
* READY 映射：18
* PENDING／未闭合 Ktype：85

  * 已明确标记 PENDING：4
  * 尚待处理：81
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21546	21546	SUV	Tribute I	EP3W	5	EU-MAZDA-TRIBUTE-I-SUV-5D-01	HIGH		READY
21548	21548	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-5D-01	HIGH		READY
21550	21550	Coupe	V12 Zagato		2	EU-ASTON-MARTIN-V12-ZAGATO-COUPE-2D-01	HIGH		READY
21569	21569	SUV	Cayenne 955		5	EU-PORSCHE-CAYENNE-955-SUV-5D-01	HIGH	3.2 V6对应改款前外廓。	READY
21587	21587	SUV	FX S50	S50	5	EU-INFINITI-FX-S50-SUV-5D-01	HIGH		READY
21757	21757	Convertible	Beat	PP1	2	EU-HONDA-BEAT-PP1-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-TRIBUTE-I-SUV-5D-01	4395	1800	1710	Auto-Data Mazda Tribute 2.3 i 16V FWD	https://www.auto-data.net/en/mazda-tribute-2.3-i-16v-153hp-11414
EU-TATA-INDICA-I-HATCHBACK-5D-01	3660	1625	1485	Auto-Data Tata Indica 1.4 60 Hp	https://www.auto-data.net/en/tata-indica-1.4-60hp-1211
EU-ASTON-MARTIN-V12-ZAGATO-COUPE-2D-01	4385	1865	1250	Auto-Data Aston Martin V12 Zagato 6.0 V12	https://www.auto-data.net/en/aston-martin-v12-zagato-6.0-v12-517hp-24284
EU-PORSCHE-CAYENNE-955-SUV-5D-01	4782	1928	1699	Auto-Data Porsche Cayenne 955 3.2i V6	https://www.auto-data.net/en/porsche-cayenne-955-3.2i-v6-250hp-6722
EU-INFINITI-FX-S50-SUV-5D-01	4803	1925	1651	Edmunds 2003 Infiniti FX35 RWD specifications	https://www.edmunds.com/infiniti/fx35/2003/st-100213725/features-specs/
EU-HONDA-BEAT-PP1-CONVERTIBLE-2D-01	3295	1395	1175	Toyota Automobile Museum Honda Beat PP1 archive	https://toyota-automobile-museum.jp/en/archives/car-database/detail.html?id=22756
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，区分 Cargo Van、Passenger Van 与前后期外廓。
2. 处理 Jeep Cherokee XJ `21520–21526`，确认改款边界及是否需要按门数或高度拆分。
3. 处理 Chevrolet Tahoe `21543–21545`，解决欧洲 Ktype 与 RWD／4WD 高度口径冲突。
4. 消除既有 PENDING：MX-5 NB `21499、21500` 与 Seat Leon ST `21803、21805`。

推进信号：CONTINUE

[1]: https://www.thansen.dk/bil/mazda/tribute/2-3/2004/n-236502208?utm_source=chatgpt.com "Mazda Tribute 2,3 - 2004 - Alt til din bil - samlet ét sted - thansen.dk"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 Mazda 2 DY、Mitsubishi Lancer Evolution IX、Hyundai Terracan、Honda Jazz GD、Mercedes-Benz CLK C209、Chrysler 300C LX、Audi Q7 4L、Daihatsu Terios J200，共新增 **8 个 READY Ktype、8 条 READY 映射、8 个尺寸组**。([汽车数据网][1])
* CLK、Q7 等来源已分别区分车身宽度与含后视镜宽度；本轮未重复输出或重新核对既有尺寸组。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：23
* READY 映射：26
* PENDING／未闭合 Ktype：77

  * 已输出明确 PENDING 行：4
  * 尚待首次处理：73
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21408	21408	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	HIGH		READY
21509	21509	Hatchback	Mazda 2 I	DY	5	EU-MAZDA-2-DY-HATCHBACK-5D-01	HIGH		READY
21559	21559	SUV	Terracan	HP	5	EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	HIGH		READY
21561	21561	Hatchback	Jazz II	GD3	5	EU-HONDA-JAZZ-GD-HATCHBACK-5D-01	HIGH		READY
21568	21568	Coupe	CLK C209 Facelift	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH		READY
21586	21586	Sedan	300C I	LX	4	EU-CHRYSLER-300C-LX-SEDAN-4D-01	HIGH		READY
21589	21589	SUV	Q7 I	4L	5	EU-AUDI-Q7-4L-SUV-5D-01	HIGH		READY
21760	21760	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-J200-SUV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	4534	1770	1450	Auto-Data Mitsubishi Lancer Evolution IX 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-lancer-evolution-ix-2.0-mivec-286hp-4wd-44889
EU-MAZDA-2-DY-HATCHBACK-5D-01	3925	1680	1545	Auto-Data Mazda 2 I DY 1.6	https://www.auto-data.net/en/mazda-2-i-dy-1.6-i-16v-101hp-11454
EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	4710	1860	1790	Auto-Data Hyundai Terracan 2.5 TD	https://www.auto-data.net/en/hyundai-terracan-2.5-td-100hp-automatic-24822
EU-HONDA-JAZZ-GD-HATCHBACK-5D-01	3830	1675	1525	Auto-Data Honda Fit I 1.5 110 Hp	https://www.auto-data.net/en/honda-fit-i-1.5-i-16v-110hp-12193
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1415	Auto-Data Mercedes-Benz CLK C209 Facelift CLK 500	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-clk-500-388hp-7g-tronic-23433
EU-CHRYSLER-300C-LX-SEDAN-4D-01	4999	1882	1471	Auto-Data Chrysler 300 SRT-8 Sedan	https://www.auto-data.net/en/chrysler-300-6.1-i-v8-16v-srt-8-425hp-14690
EU-AUDI-Q7-4L-SUV-5D-01	5086	1983	1737	Auto-Data Audi Q7 4L 3.0 TDI	https://www.auto-data.net/en/audi-q7-i-typ-4l-3.0-tdi-v6-233hp-quattro-tiptronic-4852
EU-DAIHATSU-TERIOS-J200-SUV-5D-01	4055	1695	1740	Auto-Data Daihatsu Terios II J200 1.5 RWD	https://www.auto-data.net/en/daihatsu-terios-ii-j200-1.5-i-16v-105hp-41
```

## 下一步优先处理

1. 消除既有明确 PENDING：MX-5 NB `21499、21500` 与 Seat Leon ST `21803、21805`。
2. 闭合 Chevrolet Astro `21714、21717–21728` 的 Cargo、Passenger、前期及后期外廓。
3. 处理 Jeep Cherokee XJ `21520–21526` 的改款、门数及车身高度边界。
4. 处理 Chevrolet Tahoe `21543–21545` 的 GMT800 RWD／4WD高度边界。
5. 批量处理 Mustang SN95 Coupe／Convertible 与 Chevrolet Caprice Sedan／Wagon。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mazda-2-i-dy-1.6-i-16v-101hp-11454 "Mazda 2 I (DY) 1.6 i 16V (101 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-clk-500-388hp-7g-tronic-23433 "Mercedes-Benz CLK (C209, facelift 2005) CLK 500 (388 Hp) 7G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已消除上一轮 4 个明确 PENDING Ktype。
* Mazda MX-5 NB 的 140 hp 与 146 hp 版本确认采用同一套 `3975 × 1680 × 1225 mm` 外廓，宽度为不含后视镜口径，Ktype `21499、21500` 共用一个新尺寸组。([汽车数据网][1])
* Seat Leon ST `21803` 确认为改款前车身，直接复用既有改款前尺寸组；`21805` 的生产范围跨越改款节点，拆分为改款前后两个派生映射，并复用既有两个尺寸组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：27
* READY 映射：31
* PENDING／未闭合 Ktype：73
* 已明确输出但尚未解决的 PENDING：0
* 已确认尺寸组：25
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21499	21499	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-NB-CONVERTIBLE-2D-01	HIGH		READY
21500	21500	Convertible	MX-5 II	NB	2	EU-MAZDA-MX-5-NB-CONVERTIBLE-2D-01	HIGH		READY
21803	21803	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-PREFL-01	HIGH	140 hp版本仅对应改款前外廓。	READY
21805_prefl	21805	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-PREFL-01	HIGH	改款前外廓分支。	READY
21805_facelift	21805	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-FACELIFT-01	HIGH	改款后外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-MX-5-NB-CONVERTIBLE-2D-01	3975	1680	1225	Automobile-Catalog 1998 Mazda MX-5 1.9; Automobile-Catalog 2002 Mazda MX-5 1.9	https://www.automobile-catalog.com/car/1998/1667030/mazda_mx-5_1_9.html;https://www.automobile-catalog.com/car/2002/1667165/mazda_mx-5_1_9.html
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，按 Cargo、Passenger、前期及后期外廓聚类。
2. 处理 Jeep Cherokee XJ `21520–21526`，确认改款、门数和高度边界。
3. 闭合 Ford Mustang SN95 Coupe／Convertible `21442–21444`。
4. 处理 Chevrolet Tahoe `21543–21545` 的 GMT800 RWD／4WD高度分支。
5. 批量处理 Chevrolet Caprice Sedan／Wagon `21469、21821–21826`。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8-i-16v-140hp-11259 "Mazda MX-5 II (NB) 1.8 i 16V (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2013/3096695/seat_leon_st_1_4_tsi_140.html?utm_source=chatgpt.com "2013 Seat Leon ST 1.4 TSI (140) Specs Review (103 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Ford Mustang IV `21442–21444`，按普通 Coupe、GT Coupe 和 Convertible 外廓建立 3 个尺寸组。([汽车目录][1])
* 闭合 Chevrolet Caprice `21469、21821–21826`。第三代 Wagon 按 1981、1982–1986、1987–1988、1989–1990 的外廓变化拆分；第四代 Sedan 按 1991–1994 与 1995–1996 拆分。([汽车目录][2])
* 本轮新增 **10 个 READY Ktype、14 条 READY 映射、10 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：37
* READY 映射：45
* PENDING／尚未闭合 Ktype：63
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21442	21442	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-COUPE-BASE-01	HIGH	普通Coupe外廓。	READY
21443	21443	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-COUPE-GT-01	HIGH	GT Coupe外廓。	READY
21444	21444	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-CONVERTIBLE-BASE-01	HIGH		READY
21469	21469	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-4D-01	HIGH	1987-1988外廓。	READY
21821_pre82	21821	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1981-01	HIGH	1981外廓分支。	READY
21821_82plus	21821	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1982-1986-01	HIGH	1982-1984外廓分支。	READY
21822	21822	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1982-1986-01	HIGH		READY
21823_pre89	21823	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1987-1988-01	HIGH	1988外廓分支。	READY
21823_89plus	21823	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1989-1990-01	HIGH	1989-1990外廓分支。	READY
21824_pre89	21824	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1987-1988-01	HIGH	1987-1988外廓分支。	READY
21824_89	21824	Wagon	Caprice III		5	EU-CHEVROLET-CAPRICE-III-WAGON-1989-1990-01	HIGH	1989外廓分支。	READY
21825_94	21825	Sedan	Caprice IV		4	EU-CHEVROLET-CAPRICE-IV-SEDAN-1991-1994-01	HIGH	1994外廓分支。	READY
21825_95plus	21825	Sedan	Caprice IV		4	EU-CHEVROLET-CAPRICE-IV-SEDAN-1995-1996-01	HIGH	1995-1996外廓分支。	READY
21826	21826	Sedan	Caprice IV		4	EU-CHEVROLET-CAPRICE-IV-SEDAN-1991-1994-01	HIGH	1991-1993外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-IV-COUPE-BASE-01	4610	1824	1344	Automobile-Catalog 1994 Ford Mustang Coupe 3.8 V6	https://www.automobile-catalog.com/car/1994/885155/ford_mustang_coupe_3_8l_v-6.html
EU-FORD-USA-MUSTANG-IV-COUPE-GT-01	4610	1824	1351	Automobile-Catalog 1996 Ford Mustang GT Coupe	https://www.automobile-catalog.com/car/1996/885605/ford_mustang_gt_coupe.html
EU-FORD-USA-MUSTANG-IV-CONVERTIBLE-BASE-01	4610	1824	1341	Automobile-Catalog 1994 Ford Mustang Convertible 3.8 V6	https://www.automobile-catalog.com/car/1994/885215/ford_mustang_convertible_3_8l_v-6.html
EU-CHEVROLET-CAPRICE-III-SEDAN-4D-01	5405	1915	1433	Automobile-Catalog 1987 Chevrolet Caprice Sedan 5.0 V8	https://www.automobile-catalog.com/car/1987/462275/chevrolet_caprice_sedan_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-WAGON-1981-01	5464	2014	1450	Automobile-Catalog 1981 Chevrolet Caprice Classic Wagon 5.0 V8	https://www.automobile-catalog.com/car/1981/209765/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-WAGON-1982-1986-01	5464	2014	1476	Automobile-Catalog 1982 Chevrolet Caprice Classic Wagon 5.0 V8; Automobile-Catalog 1986 Chevrolet Caprice Classic Wagon 5.0 V8	https://www.automobile-catalog.com/car/1982/210410/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic_overdrive.html;https://www.automobile-catalog.com/car/1986/462095/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic_overdrive.html
EU-CHEVROLET-CAPRICE-III-WAGON-1987-1988-01	5464	2014	1478	Automobile-Catalog 1987 Chevrolet Caprice Wagon 5.0 V8; Automobile-Catalog 1988 Chevrolet Caprice Classic Wagon 5.0 V8	https://www.automobile-catalog.com/car/1987/462320/chevrolet_caprice_wagon_5_0l_v-8_140-hp_automatic_overdrive.html;https://www.automobile-catalog.com/car/1988/462500/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic.html
EU-CHEVROLET-CAPRICE-III-WAGON-1989-1990-01	5479	2014	1478	Automobile-Catalog 1989 Chevrolet Caprice Classic Wagon 5.0 V8; Automobile-Catalog 1990 Chevrolet Caprice Classic Wagon 5.0 V8	https://www.automobile-catalog.com/car/1989/462590/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic.html;https://www.automobile-catalog.com/car/1990/1494635/chevrolet_caprice_classic_wagon_5_0l_v-8.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-1991-1994-01	5438	1956	1440	Automobile-Catalog 1991 Chevrolet Caprice Sedan 5.0 V8; Automobile-Catalog 1994 Chevrolet Caprice Classic Sedan 4.3 V8	https://www.automobile-catalog.com/car/1991/471800/chevrolet_caprice_sedan_5_0l_v-8.html;https://www.automobile-catalog.com/car/1994/471995/chevrolet_caprice_classic_sedan_4_3l_v-8.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-1995-1996-01	5438	1968	1415	Automobile-Catalog 1995 Chevrolet Caprice Classic Sedan 4.3 V8; Automobile-Catalog 1996 Chevrolet Caprice Classic Sedan 4.3 V8	https://www.automobile-catalog.com/car/1995/472100/chevrolet_caprice_classic_sedan_4_3l_v-8.html;https://www.automobile-catalog.com/car/1996/472100/chevrolet_caprice_classic_sedan_4_3l_v-8.html
```

## 下一步优先处理

1. 批量处理 Chevrolet Astro `21714、21717–21728`，区分第一代／第二代、Cargo Van 与 Passenger Van。
2. 闭合 Jeep Cherokee XJ `21520–21526`，确认三门／五门、改款及高度边界。
3. 处理 Chevrolet Tahoe `21543–21545` 的 GMT800 RWD／4WD高度分支。
4. 批量处理 Chevrolet Camaro III `21465、21466`，复用或补充已建 Camaro III 改款前后尺寸组。
5. 处理 Cadillac Seville、Buick Skylark、Buick Park Avenue 等北美 Sedan。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1994/885155/ford_mustang_coupe_3_8l_v-6.html?utm_source=chatgpt.com "1994 Ford Mustang Coupe 3.8L V-6 Specs Review (108 kW / 147 PS / 145 hp) (since mid-year 1993 for North America U.S.)"
[2]: https://www.automobile-catalog.com/car/1981/209765/chevrolet_caprice_classic_wagon_5_0l_v-8_automatic_overdrive.html?utm_source=chatgpt.com "1981 Chevrolet Caprice Classic Wagon 5.0L V-8 automatic overdrive Specs Review (112 kW / 152 PS / 150 hp) (since September 1980 for North America U.S.)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 本轮闭合 Audi A6 C4、Toyota Supra A70、BMW 635 CSi E24、Chevrolet Corvette C4 Convertible、Lamborghini Diablo，共新增 **5 个 READY Ktype、6 条 READY 映射、6 个尺寸组**。([汽车目录][1])
* BMW `21375` 覆盖 1987 年车身长度变化，已拆分为改款前 `4755 mm` 与改款后 `4815 mm` 两个外廓分支。([汽车目录][2])
* Camaro `21465、21466` 暂未复用既有组：同年份普通 Sport Coupe 与 Z28/IROC-Z 存在保险杠、长度和高度差异，必须先确定 Ktype 覆盖的具体外廓，不能仅按发动机合并。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：42
* READY 映射：51
* PENDING／尚未闭合 Ktype：58
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21350	21350	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-4D-01	HIGH		READY
21355	21355	Coupe	Supra III	A70	3	EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	HIGH		READY
21375_prefl	21375	Coupe	6 Series E24	E24	2	EU-BMW-6-SERIES-E24-COUPE-PREFL-01	HIGH	1982-1986外廓分支。	READY
21375_facelift	21375	Coupe	6 Series E24	E24	2	EU-BMW-6-SERIES-E24-COUPE-FACELIFT-01	HIGH	1987-1988改款后外廓分支。	READY
21472	21472	Convertible	Corvette C4	C4	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-2D-01	HIGH		READY
21533	21533	Coupe	Diablo		2	EU-LAMBORGHINI-DIABLO-COUPE-2D-01	HIGH	标准后驱5.7车型外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C4-SEDAN-4D-01	4797	1783	1430	Automobile-Catalog 1995 Audi A6 Europe	https://www.automobile-catalog.com/car/1995/239030/audi_a6.html
EU-TOYOTA-SUPRA-III-A70-COUPE-3D-01	4620	1745	1310	Auto-Data Toyota Supra III A70 3.0 24V 190 Hp	https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-24v-190hp-3456
EU-BMW-6-SERIES-E24-COUPE-PREFL-01	4755	1725	1365	Automobile-Catalog 1984 BMW 635 CSi Europe	https://www.automobile-catalog.com/car/1984/51755/bmw_635_csi.html
EU-BMW-6-SERIES-E24-COUPE-FACELIFT-01	4815	1725	1365	Automobile-Catalog 1988 BMW 635 CSi Europe	https://www.automobile-catalog.com/car/1988/264215/bmw_635_csi_cat.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-2D-01	4483	1803	1179	Automobile-Catalog 1986 Chevrolet Corvette Convertible; Automobile-Catalog 1989 Chevrolet Corvette Convertible	https://www.automobile-catalog.com/car/1986/463280/chevrolet_corvette_convertible.html;https://www.automobile-catalog.com/car/1989/463505/chevrolet_corvette_convertible.html
EU-LAMBORGHINI-DIABLO-COUPE-2D-01	4460	2040	1105	Automobile-Catalog 1995 Lamborghini Diablo	https://www.automobile-catalog.com/car/1995/1371470/lamborghini_diablo.html
```

## 下一步优先处理

1. 闭合 Chevrolet Astro `21714、21717–21728`，按第一代／第二代、Cargo／Passenger 批量聚类。
2. 处理 Jeep Cherokee XJ `21520–21526`，确认三门／五门、改款和高度边界。
3. 处理 Mitsubishi L300、L400 及 Hyundai H-1，优先解决 Bus 车身的轴距和车顶分支。
4. 处理 Camaro `21465、21466` 的 Sport Coupe 与 Z28／IROC-Z 外廓覆盖范围。
5. 闭合 Peugeot 405 Break、Fiat Palio、Suzuki Wagon R 等小型车组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/239030/audi_a6.html?utm_source=chatgpt.com "Detailed specs review of 1995 Audi A6 model for Europe"
[2]: https://www.automobile-catalog.com/car/1984/51755/bmw_635_csi.html?utm_source=chatgpt.com "Detailed specs review of 1984 BMW 635 CSi model for Europe"
[3]: https://www.automobile-catalog.com/car/1985/458735/chevrolet_camaro_sport_coupe_5_0l_v-8_automatic.html?utm_source=chatgpt.com "1985 Chevrolet Camaro Sport Coupe 5.0L V-8 automatic ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Peugeot Partner I、Chevrolet Lumina APV、Fiat Palio 178、Suzuki Wagon R、Peugeot 206，共新增 **6 个 READY Ktype、8 条 READY 映射、5 个尺寸组**。
* Fiat Palio 与 Peugeot 206 的来源均明确覆盖三门、五门车身；因此分别拆成 `3dr`、`5dr` 映射，并复用同一个已确认尺寸组。([汽车数据网][1])
* Suzuki Wagon R `21480、21481` 的 1.0 60 hp 与 1.2 80 hp 版本三维相同，已复用同一尺寸组。([Auto ABC][2])
* Partner 的宽度来源同时列出含镜宽度 `1960 mm`，确认落盘的 `1720 mm` 为不含后视镜宽度。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：48
* READY 映射：59
* PENDING／尚未闭合 Ktype：52
* 已确认尺寸组：46
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21448	21448	MPV	Partner I Phase I	M49	5	EU-PEUGEOT-PARTNER-I-PHASE-I-MPV-5D-01	HIGH		READY
21450	21450	MPV	Lumina APV	U	4	EU-CHEVROLET-LUMINA-APV-MPV-4D-01	HIGH		READY
21473_3dr	21473	Hatchback	Palio I	178	3	EU-FIAT-PALIO-178-HATCHBACK-01	HIGH	三门车身分支。	READY
21473_5dr	21473	Hatchback	Palio I	178	5	EU-FIAT-PALIO-178-HATCHBACK-01	HIGH	五门车身分支。	READY
21480	21480	Hatchback	Wagon R III	MA	5	EU-SUZUKI-WAGON-R-III-HATCHBACK-5D-01	HIGH		READY
21481	21481	Hatchback	Wagon R III	MA	5	EU-SUZUKI-WAGON-R-III-HATCHBACK-5D-01	HIGH		READY
21501_3dr	21501	Hatchback	206		3	EU-PEUGEOT-206-HATCHBACK-01	HIGH	三门车身分支。	READY
21501_5dr	21501	Hatchback	206		5	EU-PEUGEOT-206-HATCHBACK-01	HIGH	五门车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-I-PHASE-I-MPV-5D-01	4110	1720	1870	Auto-Data Peugeot Partner I Phase I 1.9 D 70 Hp	https://www.auto-data.net/en/peugeot-partner-i-phase-i-1.9-d-70hp-42013
EU-CHEVROLET-LUMINA-APV-MPV-4D-01	4844	1877	1669	Auto-Data Chevrolet Lumina APV 3.8 i 175 Hp	https://www.auto-data.net/en/chevrolet-lumina-apv-3.8-i-175hp-14476
EU-FIAT-PALIO-178-HATCHBACK-01	3735	1626	1446	Auto-Data Fiat Palio 178 1.2 i 68 Hp	https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854
EU-SUZUKI-WAGON-R-III-HATCHBACK-5D-01	3540	1600	1660	Auto-ABC Suzuki Wagon R+ 1.0; Auto-ABC Suzuki Wagon R+ 1.2	https://www.auto-abc.eu/Suzuki-Wagon-R/v15222-2006;https://www.auto-abc.eu/Suzuki-Wagon-R/v15223-2006
EU-PEUGEOT-206-HATCHBACK-01	3835	1652	1426	Auto-Data Peugeot 206 1.1i 60 Hp	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728` 的 Cargo、Passenger 与前后期车身。
2. 处理 Jeep Cherokee XJ `21520–21526` 的三门、五门及改款边界。
3. 处理 Chevrolet Tahoe `21543–21545` 的 RWD、4WD高度分支。
4. 闭合 Mitsubishi L300、L400、Hyundai H-1 的轴距与车顶分支。
5. 批量处理剩余单一外廓 Sedan、Coupe 与 Convertible。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854 "Fiat Palio (178) 1.2 i (68 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-abc.eu/Suzuki-Wagon-R/v15222-2006 "Suzuki Wagon R+ 2006 1.0 (2006, 2007, 2008) reviews, technical data, prices"
[3]: https://www.auto-data.net/en/peugeot-partner-i-phase-i-1.9-d-70hp-42013 "Peugeot Partner I (Phase I) 1.9 D (70 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Mitsubishi Lancer V、Peugeot 405 I Break、Ford Mondeo I Sedan，以及 Jeep Compass I 的两个 Ktype；Compass 汽油与柴油版本复用同一物理外廓尺寸组。([汽车数据网][1])
* Renault Thalia I 的 Ktype `21562` 跨越 2002 年改款，外廓由 `4150 × 1639 × 1416 mm` 变为 `4171 × 1639 × 1437 mm`，已拆分为改款前后两条映射。([汽车数据网][2])
* Cadillac Seville `21453、21454` 分别对应 1988–1989 与 1990–1991 两套外廓，未错误合并。([汽车目录][3])
* 本轮新增 **8 个 READY Ktype、9 条 READY 映射、8 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：56
* READY 映射：68
* PENDING／尚未闭合 Ktype：44
* 已确认尺寸组：54
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21346	21346	Sedan	Lancer V	CB1A	4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
21360	21360	Wagon	405 I Break	15E	5	EU-PEUGEOT-405-I-BREAK-WAGON-5D-01	HIGH		READY
21453	21453	Sedan	Seville III		4	EU-CADILLAC-SEVILLE-III-SEDAN-1988-1989-01	HIGH		READY
21454	21454	Sedan	Seville III		4	EU-CADILLAC-SEVILLE-III-SEDAN-1990-1991-01	HIGH		READY
21562_prefl	21562	Sedan	Thalia I	LB	4	EU-RENAULT-THALIA-I-SEDAN-PREFL-01	HIGH	1998-2002改款前外廓分支。	READY
21562_facelift	21562	Sedan	Thalia I Facelift	LB	4	EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	HIGH	2002-2008改款后外廓分支。	READY
21591	21591	SUV	Compass I	MK	4	EU-JEEP-COMPASS-I-MK-SUV-4D-01	HIGH		READY
21592	21592	SUV	Compass I	MK	4	EU-JEEP-COMPASS-I-MK-SUV-4D-01	HIGH		READY
21709	21709	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data Mitsubishi Lancer V 1.3 75 Hp	https://www.auto-data.net/en/mitsubishi-lancer-v-1.3-75hp-15664
EU-PEUGEOT-405-I-BREAK-WAGON-5D-01	4398	1714	1450	Auto-Data Peugeot 405 I Break 15E	https://www.auto-data.net/en/peugeot-405-i-break-15e-generation-1272
EU-CADILLAC-SEVILLE-III-SEDAN-1988-1989-01	4846	1801	1364	Automobile-Catalog 1989 Cadillac Seville	https://www.automobile-catalog.com/car/1989/332495/cadillac_seville.html
EU-CADILLAC-SEVILLE-III-SEDAN-1990-1991-01	4846	1828	1352	Automobile-Catalog 1991 Cadillac Seville	https://www.automobile-catalog.com/car/1991/332615/cadillac_seville.html
EU-RENAULT-THALIA-I-SEDAN-PREFL-01	4150	1639	1416	Auto-Data Renault Clio Symbol I	https://www.auto-data.net/en/renault-clio-symbol-i-generation-2133
EU-RENAULT-THALIA-I-SEDAN-FACELIFT-01	4171	1639	1437	Auto-Data Renault Symbol I Facelift 2002	https://www.auto-data.net/en/renault-symbol-i-facelift-2002-generation-2168
EU-JEEP-COMPASS-I-MK-SUV-4D-01	4405	1810	1630	Auto-Data Jeep Compass I MK 2.4 170 Hp; Auto-Data Jeep Compass I MK 2.0 CRD 140 Hp	https://www.auto-data.net/en/jeep-compass-i-mk-2.4-170hp-cvt-4x4-1199;https://www.auto-data.net/en/jeep-compass-i-mk-2.0-crd-140hp-4x4-30039
EU-FORD-MONDEO-I-SEDAN-4D-01	4481	1749	1428	Auto-Data Ford Mondeo I Sedan 2.0 i 16V 4x4	https://www.auto-data.net/en/ford-mondeo-i-sedan-2.0-i-16v-4x4-136hp-7727
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，区分 Cargo、Passenger、第一代和第二代。
2. 处理 Jeep Cherokee XJ `21520–21526` 的三门、五门和年份外廓边界。
3. 闭合 Chevrolet Tahoe `21543–21545` 的欧洲规格及 RWD／4WD分支。
4. 处理 Jaguar XJ-S Coupe／Convertible、Alfa Romeo Spider 和 Maserati Biturbo。
5. 处理 Mitsubishi L300、L400、Hyundai H-1 及 Fiat／Peugeot 商用车的轴距、车顶和车身形式分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-lancer-v-1.3-75hp-15664 "Mitsubishi Lancer V 1.3 (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/renault-clio-symbol-i-generation-2133?utm_source=chatgpt.com "Renault Clio Symbol I | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1989/332495/cadillac_seville.html?utm_source=chatgpt.com "1989 Cadillac Seville Specs Review (115.5 kW / 157 PS / 155 hp) (since mid-year 1988 for North America )"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Maserati Biturbo E、Buick Skylark VII Sedan、Buick Park Avenue 150 kW 欧洲规格，共新增 **3 个 READY Ktype、3 条 READY 映射、3 个尺寸组**。
* Biturbo E 已确认对应双门出口版车身；Park Avenue 页面直接匹配 `150 kW / 205 PS`、1995–1996 与四门 Sedan 外廓。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：59
* READY 映射：71
* PENDING／尚未闭合 Ktype：41
* 已确认尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21401	21401	Coupe	Biturbo I	AM331	2	EU-MASERATI-BITURBO-I-COUPE-2D-01	HIGH		READY
21452	21452	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
21494	21494	Sedan	Park Avenue I		4	EU-BUICK-PARK-AVENUE-I-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MASERATI-BITURBO-I-COUPE-2D-01	4153	1714	1305	Automobile-Catalog 1983 Maserati Biturbo 2500	https://www.automobile-catalog.com/car/1983/49145/maserati_biturbo_2500.html
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4806	1714	1351	Automobile-Catalog 1993 Buick Skylark Custom Sedan 2.3L Quad	https://www.automobile-catalog.com/car/1993/322475/buick_skylark_custom_sedan_2_3l_quad.html
EU-BUICK-PARK-AVENUE-I-SEDAN-4D-01	5230	1883	1399	Auto Motor und Sport Buick Park Avenue 3.8 150 kW technical data	https://www.auto-motor-und-sport.de/marken-modelle/buick/park-avenue/3-generation/technische-daten/
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，按第一代／第二代及 Cargo／Passenger 聚类。
2. 处理 Jeep Cherokee XJ `21520–21526` 的三门、五门及年份边界。
3. 闭合 Chevrolet Tahoe `21543–21545` 的 RWD／4WD外廓。
4. 处理 Mitsubishi L300、L400 和 Hyundai H-1 的轴距、车顶分支。
5. 处理 Peugeot Boxer、Fiat Ducato 和 Chevrolet C1500／C2500 的商用车配置分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/49145/maserati_biturbo_2500.html?utm_source=chatgpt.com "1983 Maserati Biturbo 2500 Specs Review (139 kW / 189 PS / 186 hp) (since mid-year 1983 for Europe )"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Hyundai H-1／Starex `21455`、Chevrolet Camaro 5.0 `21465`、Nissan X-Trail T30 `21555、21557`、Renault Espace IV `21576`。
* `21465` 跨越 Camaro III 改款节点，拆分后直接复用已有改款前、改款后尺寸组。
* `21555` 覆盖 X-Trail T30 改款前后两套车长，拆分为两个物理外廓；`21557` 仅关联改款后组。
* 本轮新增 **5 个 READY Ktype、7 条 READY 映射、4 个尺寸组**。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：64
* READY 映射：78
* PENDING／尚未闭合 Ktype：36
* 已确认尺寸组：61
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21455	21455	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H-1-I-STAREX-MPV-LWB-01	HIGH	长轴距后驱客车外廓。	READY
21465_prefl	21465	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-PREFL-01	HIGH	1987-1990改款前外廓分支。	READY
21465_facelift	21465	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-FACELIFT-01	HIGH	1991-1992改款后外廓分支。	READY
21555_prefl	21555	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	HIGH	改款前标准车身外廓。	READY
21555_facelift	21555	SUV	X-Trail I	T30	5	EU-NISSAN-X-TRAIL-I-T30-SUV-FACELIFT-01	HIGH	改款后标准车身外廓。	READY
21557	21557	SUV	X-Trail I Facelift	T30	5	EU-NISSAN-X-TRAIL-I-T30-SUV-FACELIFT-01	MEDIUM		READY
21576	21576	MPV	Espace IV		5	EU-RENAULT-ESPACE-IV-MPV-5D-01	HIGH	标准轴距Espace，非Grand Espace。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H-1-I-STAREX-MPV-LWB-01	5035	1820	1965	Auto-Data Hyundai H-1 I Starex 2.4 i 16V LWB 135 Hp	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.4-i-16v-lwb-135hp-13851
EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	4445	1765	1675	Automobile-Catalog 2002 Nissan X-Trail Xtt 4WD	https://www.automobile-catalog.com/car/2002/2314355/nissan_x-trail_xtt_4wd.html
EU-NISSAN-X-TRAIL-I-T30-SUV-FACELIFT-01	4455	1765	1675	Automobile-Catalog 2005 Nissan X-Trail X 4WD	https://www.automobile-catalog.com/car/2005/2314670/nissan_x-trail_x_4wd.html
EU-RENAULT-ESPACE-IV-MPV-5D-01	4661	1894	1690	Automobile-Catalog 2005 Renault Espace 1.9 dCi 120	https://www.automobile-catalog.com/car/2005/2950040/renault_espace_1_9_dci_120.html
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，按第一代／第二代及 Cargo／Passenger 外廓聚类。
2. 处理 Jeep Cherokee XJ `21520–21526` 的三门、五门及年份边界。
3. 闭合 Chevrolet Tahoe `21543–21545` 的后驱、四驱高度分支。
4. 处理 Jaguar XJ-S Coupe／XJ-SC、Alfa Romeo Spider 和 Camaro 5.7。
5. 处理 Mitsubishi L300／L400、Fiat Ducato、Peugeot Boxer 和 C1500／C2500 多配置商用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1992/460175/chevrolet_camaro_rs_5_0l_v-8_efi_automatic.html?utm_source=chatgpt.com "1992 Chevrolet Camaro RS 5.0L V-8 EFi automatic Specs Review (126.5 kW / 172 PS / 170 hp) (for North America )"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Alfa Romeo Spider `21354`，按 Series 2 与 Series 3 两套外廓拆分，新增 2 个尺寸组。([汽车目录][1])
* 闭合 Chevrolet Camaro 5.7 `21466`，按 1990 年及以前、1991–1992 年两套外廓拆分，直接复用已有 Camaro III 尺寸组，不重复建组。([汽车目录][2])
* 本轮新增 **2 个 READY Ktype、4 条 READY 映射、2 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：66
* READY 映射：82
* PENDING／尚未闭合 Ktype：34
* 已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21354_series2	21354	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES-2-01	HIGH	1974-1982 Series 2外廓分支。	READY
21354_series3	21354	Convertible	Spider Series 3	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES-3-01	HIGH	1983-1984 Series 3外廓分支。	READY
21466_prefl	21466	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-PREFL-01	HIGH	1985-1990外廓分支。	READY
21466_facelift	21466	Coupe	Camaro III		3	EU-CHEVROLET-CAMARO-III-COUPE-FACELIFT-01	HIGH	1991-1992外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES-2-01	4120	1630	1290	Automobile-Catalog 1980 Alfa Romeo Spider Veloce 2000	https://www.automobile-catalog.com/car/1980/27245/alfa_romeo_spider_veloce_2000.html
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES-3-01	4245	1630	1290	Automobile-Catalog 1984 Alfa Romeo Spider 2.0 Europe	https://www.automobile-catalog.com/car/1984/41210/alfa_romeo_spider_2_0.html
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，按短轴、长轴和第二代车身聚类。
2. 处理 Jeep Cherokee XJ `21520–21526` 的三门、五门及 1997 年改款边界。
3. 闭合 Chevrolet Tahoe `21543–21545` 的前后期以及后驱、四驱外廓。
4. 处理 Jaguar XJ-S／XJ-SC `21330、21335` 的输入功率与车型年份冲突。
5. 处理 Mitsubishi L300／L400、Ducato、Boxer、C1500／C2500 等多配置商用车。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/alfa_romeo/spider_alfa_romeo/spider_serie_2/1980.html?utm_source=chatgpt.com "1980 Alfa Romeo Spider 2a serie (Square-Tail) full range specs"
[2]: https://www.automobile-catalog.com/car/1990/460025/chevrolet_camaro_iroc-z_5_7l_v-8_tpi_automatic.html?utm_source=chatgpt.com "1990 Chevrolet Camaro IROC-Z 5.7L V-8 TPI automatic Specs Review (182.5 kW / 248 PS / 245 hp) (since mid-year 1989 for North America )"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 闭合 Chevrolet Tahoe `21543–21545`。
* `21544` 覆盖 GMT820 改款前后两套外廓，拆分为 `prefl`、`facelift`。
* 改款前后驱与四驱三维相同，复用同一尺寸组；改款后后驱与四驱高度不同，分别建组。([auto123.com][1])
* 本轮新增 **3 个 READY Ktype、4 条 READY 映射、3 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* READY 映射：82
* PENDING／尚未闭合 Ktype：33
* 已确认尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21543	21543	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-PREFL-01	HIGH	改款前外廓。	READY
21544_prefl	21544	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-PREFL-01	HIGH	2000-2002改款前外廓分支。	READY
21544_facelift	21544	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-FACELIFT-RWD-01	HIGH	2003-2006后驱外廓分支。	READY
21545	21545	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-FACELIFT-4WD-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-TAHOE-II-GMT820-SUV-PREFL-01	5052	2004	1899	Auto123 2000 Chevrolet Tahoe 2WD; Auto123 2000 Chevrolet Tahoe 4WD	https://www.auto123.com/en/new-cars/technical-specs/chevrolet/tahoe/2000/2wd/base/;https://www.auto123.com/en/new-cars/technical-specs/chevrolet/tahoe/2000/4wd/base/
EU-CHEVROLET-TAHOE-II-GMT820-SUV-FACELIFT-RWD-01	5001	2004	1900	Auto123 2006 Chevrolet Tahoe LS 2WD	https://www.auto123.com/en/new-cars/technical-specs/chevrolet/tahoe/2006/2wd/ls/
EU-CHEVROLET-TAHOE-II-GMT820-SUV-FACELIFT-4WD-01	5001	2004	1948	Auto123 2006 Chevrolet Tahoe LS 4WD	https://www.auto123.com/en/new-cars/technical-specs/chevrolet/tahoe/2006/4wd/ls/
```

## 下一步优先处理

1. 批量闭合 Chevrolet Astro `21714、21717–21728`，按第一代／第二代、标准轴／加长轴和 Cargo／Passenger 聚类。
2. 处理 Jeep Cherokee XJ `21520–21526`，按改款前后与三门／五门映射边界闭合。
3. 处理 Mitsubishi L300、L400 与 Hyundai H-1 的轴距及车顶分支。
4. 处理 Peugeot Boxer、Fiat Ducato 的厢式车、客车及底盘配置。
5. 处理 Chevrolet C1500／C2500 的驾驶室与货斗分支。

推进信号：CONTINUE

[1]: https://www.auto123.com/en/new-cars/technical-specs/chevrolet/tahoe/2000/2wd/base/ "2000 Chevrolet Tahoe | Specifications - Car Specs | Auto123"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 机械校正累计基线：上一轮完成后实际为 **READY Ktype 69、READY 映射 86、尺寸组 66**。
* 闭合 Mitsubishi L400／Space Gear 2.0 Ktype `21535`。1996 年改款后车长由 `4595 mm` 增至 `4655 mm`，宽度与高度不变，拆分为前期、后期两个物理外廓。([汽车目录][1])
* 闭合 Jeep Wrangler III JK Ktype `21750`，确认对应两门短轴车身。([AUTODOC][2])
* 本轮新增 **2 个 READY Ktype、3 条 READY 映射、3 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* READY 映射：89
* PENDING／尚未闭合 Ktype：29
* 已确认尺寸组：69
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21535_prefl	21535	MPV	L400 / Space Gear	PA3W	5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-PREFL-01	HIGH	1995-1996前期外廓。	READY
21535_facelift	21535	MPV	L400 / Space Gear	PA3W	5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-FACELIFT-01	HIGH	1996-2002后期外廓。	READY
21750	21750	SUV	Wrangler III	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-01	HIGH	两门短轴车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-PREFL-01	4595	1695	1855	Automobile-Catalog 1995 Mitsubishi Space Gear 2000 GLX	https://www.automobile-catalog.com/car/1995/2019935/mitsubishi_space_gear_2000_glx.html
EU-MITSUBISHI-L400-SPACE-GEAR-MPV-FACELIFT-01	4655	1695	1855	Automobile-Catalog 1996 Mitsubishi Space Gear 2000 GLX	https://www.automobile-catalog.com/car/1996/2020010/mitsubishi_space_gear_2000_glx.html
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800	Auto-Data Jeep Wrangler III JK Sport 3.8i V6	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sport-3.8i-v6-196hp-4x4-31684
```

## 下一步优先处理

1. 继续处理 Jeep Cherokee XJ `21520–21526`，先解决 Ktype 驱动信息冲突及改款前后宽度口径。
2. 批量闭合 Chevrolet Astro `21714、21717–21728`，区分前后代、标准轴和加长轴。
3. 解决 Mitsubishi L400 `21536` 的车顶及配置高度分支。
4. 处理 Chevrolet C1500／C2500 的驾驶室和货斗组合。
5. 处理 Peugeot Boxer、Fiat Ducato 的厢式车、客车及底盘配置。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1995/2019935/mitsubishi_space_gear_2000_glx.html?utm_source=chatgpt.com "1995 Mitsubishi Space Gear 2000 GLX Specs Review (84.5 kW / 115 PS / 113 hp) (since April 1995 for Europe )"
[2]: https://www.autodoc.parts/car-parts/throttle-body-12439/jeep/wrangler/wrangler-iii-jk/21750-3-8-rwd?utm_source=chatgpt.com "Throttle body Jeep Wrangler JK 3.8 RWD 199 hp Petrol 146 kW 2007 - 2010 EGT ▷ AUTODOC"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 闭合 Jaguar XJ Coupe `21330` 与 Jaguar XJSC Convertible `21335`，新增 **2 个 READY Ktype、2 条 READY 映射、2 个尺寸组**。
* `21330` 对应 4.0、175 kW 双门 XJS Coupe；尺寸来源明确标注宽度不含后视镜。([AUTODOC][1])
* `21335` 对应 X27 双门 XJSC Convertible，独立于 Coupe 建组。([AUTODOC][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射：91
* PENDING／尚未闭合 Ktype：27
* 已确认尺寸组：71
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21330	21330	Coupe	XJS Series 2		2	EU-JAGUAR-XJS-SERIES-2-COUPE-2D-01	MEDIUM	4.0 175 kW双门Coupe外廓。	READY
21335	21335	Convertible	XJSC Convertible	X27	2	EU-JAGUAR-XJSC-X27-CONVERTIBLE-2D-01	MEDIUM	X27双门敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJS-SERIES-2-COUPE-2D-01	4764	1793	1247	Automobile-Catalog 1991 Jaguar XJS 4.0 Coupe	https://www.automobile-catalog.com/car/1991/1284365/jaguar_xjs_4_0_coupe.html
EU-JAGUAR-XJSC-X27-CONVERTIBLE-2D-01	4820	1793	1279	Auto-Data Jaguar XJSc Convertible 4.0	https://www.auto-data.net/en/jaguar-xjsc-convertible-4.0-226hp-260
```

## 下一步优先处理

1. 闭合 Jeep Cherokee XJ `21520–21526`，按三门／五门和改款前后外廓拆分。
2. 批量处理 Chevrolet Astro `21714、21717–21728`，按标准轴／加长轴及第一代／第二代聚类。
3. 处理 Mitsubishi L300、L400 `21536` 的轴距和车顶分支。
4. 处理 Chevrolet C1500／C2500 的驾驶室与货斗组合。
5. 处理 Fiat Ducato、Peugeot Boxer 的客车、厢式车及底盘配置。

推进信号：CONTINUE

[1]: https://www.autodoc.de/autoteile/steuerkette-10511/jaguar/xj/xj-coupe/21330-4-0 "Steuerkette Jaguar XJ Coupe 4.0 238 PS Benzin 175 kW 1986 - 1989 9EPCNA"
[2]: https://www.autodoc.lu/autoteile/fernscheinwerfergluhlampe-10542/jaguar/xjs/xjsc-convertible/21335-4-0 "Fernlicht-Birne Jaguar XJS Cabrio 4.0 238 PS Benzin 175 kW 1987 - 1989 9LPFRB ▷ AUTODOC"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* Ktype `21536` 已确认对应 L400／Space Gear `PA4W` 客车车身，仅发动机版本不同；按生产年份直接复用已建前期、后期尺寸组，不重复抓取三维。([www.valeoservice.com][1])
* Ktype `21520` 已建立明确 PENDING 行。现有资料对其门数覆盖及 1997—1999 年外廓边界存在冲突，暂不创建猜测性尺寸组。([Autodoc][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：74
* READY 映射：93
* PENDING／尚未闭合 Ktype：26
* 已明确输出的 PENDING：1
* 已确认尺寸组：71
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21520	21520	SUV	Cherokee II XJ Facelift	XJ			LOW	改款后SE候选；门数及年度外廓边界未闭合。	PENDING: 门数及年度外廓边界未确认
21536_prefl	21536	MPV	L400 / Space Gear	PA4W	5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-PREFL-01	HIGH	1995-1996前期外廓。	READY
21536_facelift	21536	MPV	L400 / Space Gear	PA4W	5	EU-MITSUBISHI-L400-SPACE-GEAR-MPV-FACELIFT-01	HIGH	1996-2002后期外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 消除 Ktype `21520` 的门数与年度外廓冲突。
2. 批量闭合 Cherokee XJ `21521–21526`，按三门／五门、年份和驱动高度边界拆分。
3. 处理 Chevrolet Astro `21714、21717–21728` 的标准轴／加长轴及前后期车身。
4. 处理 Mitsubishi L300、Ducato、Boxer 和 C1500／C2500 的商用车物理分支。

推进信号：CONTINUE

[1]: https://www.valeoservice.com/techassist/vehicle/P-21536?country=MA&utm_source=chatgpt.com "Parts MITSUBISHI L400 Bus (PD_W, PC_W, PA_V, PB_V, PA_W)"
[2]: https://www.autodoc.co.uk/car-parts/electric-window-winder-12791/jeep/cherokee/cherokee-xj/21520-2-5-se?utm_source=chatgpt.com "Jeep Cherokee XJ 2.5 SE Window regulator (118 hp Petrol EPE)"


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* 已消除 Ktype `21520` 的明确 PENDING：确认其为 1997–1999 改款后、两门、后驱 SE 外廓。
* 闭合 Cherokee XJ `21522–21525`。Jeep 原厂 1988 Cherokee 技术规格将该时期外廓统一列为 `4200 × 1790 × 1609 mm`，同时列出两门／四门及两驱／四驱配置，因此发动机和驱动版本复用同一尺寸组。
* 1997 年原厂资料确认 Cherokee 完成外观更新；`21520` 对应的 2dr SE RWD 规格为 `167.5 × 67.9 × 63.9 in`，换算后为 `4255 × 1725 × 1623 mm`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射：98
* PENDING／尚未闭合 Ktype：21
* 已明确输出但尚未解决的 PENDING：0
* 已确认尺寸组：73
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21520	21520	SUV	Cherokee II XJ Facelift	XJ	2	EU-JEEP-CHEROKEE-XJ-SUV-FACELIFT-RWD-2D-01	HIGH	改款后两门后驱SE外廓。	READY
21522	21522	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-XJ-SUV-1987-1990-01	MEDIUM	三门与五门采用相同三维；Ktype未区分门数。	READY
21523	21523	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-XJ-SUV-1987-1990-01	MEDIUM	三门与五门采用相同三维；Ktype未区分门数。	READY
21524	21524	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-XJ-SUV-1987-1990-01	MEDIUM	三门与五门采用相同三维；Ktype未区分门数。	READY
21525	21525	SUV	Cherokee II XJ	XJ		EU-JEEP-CHEROKEE-XJ-SUV-1987-1990-01	MEDIUM	三门与五门采用相同三维；Ktype未区分门数。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-CHEROKEE-XJ-SUV-1987-1990-01	4200	1790	1609	Jeep Corporation 1988 Cherokee official brochure	https://www.auto-brochures.com/makes/Jeep/Cherokee/Jeep_US%20Cherokee_1988.pdf
EU-JEEP-CHEROKEE-XJ-SUV-FACELIFT-RWD-2D-01	4255	1725	1623	Jeep 1997 Full Line official brochure; The Car Connection 1997 Jeep Cherokee 2dr SE specifications	https://www.auto-brochures.com/makes/Jeep/Jeep_US%20Full%20Line_1997.pdf;https://www.thecarconnection.com/specifications/jeep_cherokee_1997
```

## 下一步优先处理

1. 闭合 Cherokee XJ `21521、21526` 跨年度外廓，确认是否需要拆分 1990 年前后分支。
2. 批量处理 Chevrolet Astro `21714、21717–21728`，按第一代／第二代、标准轴／加长轴聚类。
3. 处理 Chevrolet C1500／C2500 `21786、21788、21789、21796` 的驾驶室和货斗分支。
4. 处理 Mitsubishi L300、Fiat Ducato、Peugeot Boxer 的轴距、车顶及底盘形式。
5. 闭合剩余单一乘用车外廓，优先将未闭合 Ktype 降至个位数。

推进信号：CONTINUE


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* 闭合 Cherokee XJ `21521、21526`。`21521` 对应欧洲五门 122 hp 外廓；`21526` 对应德国／意大利市场 59 kW 柴油五门外廓，二者三维不同，分别建组。([汽车数据网][1])
* 闭合 Chevrolet Astro Passenger `21717–21720`。原厂 1994 技术资料确认后驱、四驱均提供标准车身与加长车身，两种驱动形式在相同车长分支下三维一致，因此仅建立 SWB、LWB 两个稳定尺寸组。
* 本轮新增 **6 个 READY Ktype、10 条 READY 映射、4 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射：108
* PENDING／尚未闭合 Ktype：15
* 已明确输出但尚未解决的 PENDING：0
* 已确认尺寸组：77
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21521	21521	SUV	Cherokee II XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-EU-1991-1996-01	MEDIUM	欧洲122hp五门外廓。	READY
21526	21526	SUV	Cherokee II XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-EU-DIESEL-1989-1992-01	HIGH	德国及意大利59kW柴油五门外廓。	READY
21717_swb	21717	MPV	Astro I	M	3	EU-CHEVROLET-ASTRO-I-SWB-01	HIGH	标准车身外廓分支。	READY
21717_lwb	21717	MPV	Astro I	M	3	EU-CHEVROLET-ASTRO-I-LWB-01	HIGH	加长车身外廓分支。	READY
21718_swb	21718	MPV	Astro I	L	3	EU-CHEVROLET-ASTRO-I-SWB-01	HIGH	标准车身外廓分支。	READY
21718_lwb	21718	MPV	Astro I	L	3	EU-CHEVROLET-ASTRO-I-LWB-01	HIGH	加长车身外廓分支。	READY
21719_swb	21719	MPV	Astro I	M	3	EU-CHEVROLET-ASTRO-I-SWB-01	HIGH	标准车身外廓分支。	READY
21719_lwb	21719	MPV	Astro I	M	3	EU-CHEVROLET-ASTRO-I-LWB-01	HIGH	加长车身外廓分支。	READY
21720_swb	21720	MPV	Astro I	L	3	EU-CHEVROLET-ASTRO-I-SWB-01	HIGH	标准车身外廓分支。	READY
21720_lwb	21720	MPV	Astro I	L	3	EU-CHEVROLET-ASTRO-I-LWB-01	HIGH	加长车身外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-CHEROKEE-XJ-SUV-5D-EU-1991-1996-01	4288	1720	1621	Auto-Data Jeep Cherokee II XJ 5-door 2.5 i Jamboree 122 Hp	https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-2.5-i-jamboree-122hp-1133
EU-JEEP-CHEROKEE-XJ-SUV-5D-EU-DIESEL-1989-1992-01	4288	1790	1680	Automobile-Catalog 1989 Jeep Cherokee Turbo Diesel 59 kW	https://www.automobile-catalog.com/car/1989/1313165/jeep_cherokee_turbo_diesel.html
EU-CHEVROLET-ASTRO-I-SWB-01	4491	1969	1935	Chevrolet 1994 Light-Duty Truck Technical Guide M/L Astro Passenger Van	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-I-LWB-01	4745	1969	1935	Chevrolet 1994 Light-Duty Truck Technical Guide M/L Astro Passenger Van	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf
```

## 下一步优先处理

1. 将 Astro Cargo `21714、21721–21723` 关联第一代 SWB／LWB 车身，优先复用本轮 Astro 尺寸组。
2. 闭合第二代 Astro Cargo `21726–21728`，建立 1995–2005 加长车身组。
3. 处理 Chevrolet C1500／C2500 `21786、21788、21789、21796` 的驾驶室与货斗分支。
4. 处理 Mitsubishi L300、Fiat Ducato、Peugeot Boxer 的轴距、车顶和底盘形式。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jeep-cherokee-ii-xj-5-door-2.5-i-jamboree-122hp-1133 "Jeep Cherokee II (XJ) 5-door 2.5 i Jamboree (122 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 闭合 Astro Cargo `21714`：确认对应 1985 年第一代、后驱、标准短车身 Cargo Van，未复用后期 Astro 尺寸组。([通用汽车][1])
* 闭合 Astro Cargo `21726`：确认对应 1995 年第二代、后驱、单一加长车身；官方技术表明确列出 `189.8 × 77.5 × 76.1 in`，宽度为车身最大宽度口径。([通用汽车][2])
* 本轮新增 **2 个 READY Ktype、2 条 READY 映射、2 个尺寸组**。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* READY 映射：110
* PENDING／尚未闭合 Ktype：13
* 已明确输出但尚未解决的 PENDING：0
* 已确认尺寸组：79
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21714	21714	Van	Astro I	M	3	EU-CHEVROLET-ASTRO-I-CARGO-VAN-SWB-1985-01	HIGH	1985标准短车身Cargo Van。	READY
21726	21726	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	HIGH	1995后驱单一加长车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-ASTRO-I-CARGO-VAN-SWB-1985-01	4491	1956	1892	Chevrolet 1985 Astro Van official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1985-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	4821	1969	1933	Chevrolet 1995 Light-Duty Technical Guide Astro Cargo Van	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-Astro-Van.pdf
```

## 下一步优先处理

1. 闭合 Astro Cargo `21721–21723`，按 1990–1991、1992、1993–1994 的车宽／高度变化及 SWB／LWB 分支处理。
2. 闭合 Astro II `21727、21728`，确认后驱／四驱及 2003 年底盘更新是否改变外部高度。
3. 处理 Mitsubishi L300 `21329` 与 Fiat Ducato Bus `21437`。
4. 处理 Peugeot Boxer `21593、21594` 的轴距、车顶和厢式车／底盘分支。
5. 处理 Chevrolet C1500／C2500 `21786、21788、21789、21796` 的驾驶室与货斗组合。

推进信号：CONTINUE

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1985-Chevrolet-Astro-Van.pdf "pages"
[2]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-Astro-Van.pdf "https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-Astro-Van.pdf"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* 闭合 Chevrolet Astro II Cargo `21727、21728`。
* 官方规格显示该车身长度、宽度不变，但名义高度分为三段：1995–1996、1997、1998–2005，因此每个 Ktype 拆成三个稳定物理分支。后驱与四驱在同一年度段三维一致，复用相同尺寸组。
* 1995–1996 分支复用既有尺寸组，不重复输出；本轮仅新增 1997 和 1998–2005 两个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：89
* READY 映射：116
* PENDING／尚未闭合 Ktype：11
* 已明确输出但尚未解决的 PENDING：0
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21727_95_96	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	HIGH	1995-1996外廓分支。	READY
21727_97	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	HIGH	1997外廓分支。	READY
21727_98plus	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	HIGH	1998-2005外廓分支。	READY
21728_95_96	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	HIGH	1995-1996四驱外廓分支。	READY
21728_97	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	HIGH	1997四驱外廓分支。	READY
21728_98plus	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	HIGH	1998-2005四驱外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	4821	1969	1930	Chevrolet 1997 Light-Duty Truck Technical Guide Astro Cargo Van	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1997-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	4821	1969	1913	Chevrolet 1998 Light-Duty Truck Technical Guide Astro Cargo Van; Chevrolet 2005 Astro Restoration Kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Astro-Van.pdf;https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Astro-Van.pdf
```

## 下一步优先处理

1. 闭合 Astro I Cargo `21721–21723`，按 1990–1991、1992、1993–1994 及 SWB／LWB 分支处理。
2. 处理 Mitsubishi L300 `21329` 与 Fiat Ducato Bus `21437` 的轴距、车顶边界。
3. 处理 Peugeot Boxer `21593、21594` 的厢式车、底盘、轴距和车顶分支。
4. 处理 Chevrolet C1500／C2500 `21786、21788、21789、21796` 的驾驶室和货斗组合。

推进信号：CONTINUE


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 已打开消息操作菜单，但没有找到【在新聊天中分支】


--- 发送 / checkpoint 续跑到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / checkpoint 续跑 ---
## 更新点

- 闭合 Chevrolet Astro II Cargo `21727、21728`。
- 官方规格显示该车身长度、宽度不变，但名义高度分为三段：1995–1996、1997、1998–2005，因此每个 Ktype 拆成三个稳定物理分支。后驱与四驱在同一年度段三维一致，复用相同尺寸组。通用汽车+4通用汽车+4通用汽车+4
- 1995–1996 分支复用既有尺寸组，不重复输出；本轮仅新增 1997 和 1998–2005 两个尺寸组。

## 当前批次进度

- 输入 Ktype：100
- READY Ktype：89
- READY 映射：116
- PENDING／尚未闭合 Ktype：11
- 已明确输出但尚未解决的 PENDING：0
- 已确认尺寸组：81
- 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21727_95_96	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	HIGH	1995-1996外廓分支。	READY
21727_97	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	HIGH	1997外廓分支。	READY
21727_98plus	21727	Van	Astro II	M	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	HIGH	1998-2005外廓分支。	READY
21728_95_96	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-RWD-1995-01	HIGH	1995-1996四驱外廓分支。	READY
21728_97	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	HIGH	1997四驱外廓分支。	READY
21728_98plus	21728	Van	Astro II	L	3	EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	HIGH	1998-2005四驱外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-ASTRO-II-CARGO-VAN-1997-01	4821	1969	1930	Chevrolet 1997 Light-Duty Truck Technical Guide Astro Cargo Van	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1997-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-II-CARGO-VAN-1998-2005-01	4821	1969	1913	Chevrolet 1998 Light-Duty Truck Technical Guide Astro Cargo Van; Chevrolet 2005 Astro Restoration Kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1998-Chevrolet-Astro-Van.pdf;https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/2005-Chevrolet-Astro-Van.pdf
```

## 下一步优先处理

- 闭合 Astro I Cargo `21721–21723`，按 1990–1991、1992、1993–1994 及 SWB／LWB 分支处理。
- 处理 Mitsubishi L300 `21329` 与 Fiat Ducato Bus `21437` 的轴距、车顶边界。
- 处理 Peugeot Boxer `21593、21594` 的厢式车、底盘、轴距和车顶分支。
- 处理 Chevrolet C1500／C2500 `21786、21788、21789、21796` 的驾驶室和货斗组合。

推进信号：CONTINUE


--- 发送 / checkpoint 续跑到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 发送 / checkpoint 续跑到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 25 ---
【任务名称】
【全量表更新】all 第 1101-1200 行

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
all 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737
EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	4820	1855	1374
EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	4820	1855	1374
EU-BMW-X5-E70-SUV-01	4854	1933	1766
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4803	1715	1351
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	4877	1849	1278
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278
EU-CHEVROLET-CAMARO-V-COUPE-2D-01	4836	1918	1377
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	4435	1844	1244
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450
EU-FIAT-DUCATO-II-230L-4X4-VAN-01	5505	1998	2490
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
EU-FIAT-PALIO-I-178-HATCHBACK-01	3827	1634	1446
EU-FIAT-PALIO-I-178-HATCHBACK-02	3735	1626	1446
EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	4130	1626	1515
EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	4130	1626	1475
EU-FORD-MONDEO-III-B4Y-SEDAN-01	4731	1812	1429
EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	4731	1812	1429
EU-FORD-MONDEO-III-SEDAN-01	4731	1812	1429
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359
EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	4653	1857	1351
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700
EU-JEEP-COMPASS-I-MK-SUV-01	4405	1810	1630
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800
EU-JEEP-WRANGLER-III-JK-SUV-2D-02	4223	1873	1816
EU-JEEP-WRANGLER-III-JK-SUV-4D-01	4751	1877	1834
EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	4470	2040	1105
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	4595	1695	1855
EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	4995	1695	1960
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685
EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	4510	1765	1675
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426
EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	3822	1652	1425
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	5600	2000	2100
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	5120	2000	2100
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	4770	2000	2100
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
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-MPV-5D-01	4380	1810	1865
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L1-01	4380	1810	1894
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L2-01	4628	1810	1894
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	4656	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	4661	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	4656	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	4656	1860	1728
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	3500	1600	1660
EU-TATA-INDICA-I-HATCHBACK-01	3660	1625	1485

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6	3.2 FSI Quattro	Stufenheck	Allrad	Benzin	183	249	Sep 2006	Oct 2008	2024-03-01	21323
Mitsubishi	L 300 iii	2.5 TD	Bus	Heckantrieb	Diesel	64	87	Feb 1987	May 2003	2024-03-01	21329
Jaguar	Xj	4	Coupe	Heckantrieb	Benzin	175	238	Oct 1986	Dec 1989	2024-03-01	21330
Jaguar	Xjsc convertible	4	Cabriolet	Heckantrieb	Benzin	175	238	Oct 1987	Dec 1989	2024-03-01	21335
Mitsubishi	Lancer v	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Jun 1992	Feb 1995	2024-03-01	21346
Audi	A6 c4	2	Stufenheck	Frontantrieb	Benzin	79	107	Jun 1994	Jul 1995	2024-03-01	21350
Alfa Romeo	Spider	2	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1974	Dec 1984	2024-03-01	21354
Toyota	Supra	3	Coupe	Heckantrieb	Benzin	140	190	Jan 1986	May 1993	2024-03-01	21355
Peugeot	405 i break	1.4	Kombi	Frontantrieb	Benzin	47	64	May 1988	Jul 1992	2024-03-01	21360
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	160	218	May 1982	Aug 1988	2024-11-01	21375
Maserati	Biturbo	E	Coupe	Heckantrieb	Benzin	139	189	Jun 1982	Oct 1987	2024-03-01	21401
Mitsubishi	Lancer vii	EVO IX	Stufenheck	Allrad	Benzin	213	290	Aug 2005	Sep 2006	2024-03-01	21408
Fiat	Ducato	2.0 4X4	Bus	Allrad	Benzin	80	109	Nov 1994	Nov 2001	2024-03-01	21437
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	108	147	Jan 1994	May 1999	2024-03-01	21442
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	165	224	Nov 1995	May 1999	2024-03-01	21443
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	108	147	Sep 1993	May 1999	2024-03-01	21444
Peugeot	Partner	1.9 D	Großraumlimousine	Frontantrieb	Diesel	51	69	May 1996	Dec 1998	2024-03-01	21448
Chevrolet	Lumina apv	3.8	Großraumlimousine	Frontantrieb	Benzin	123	167	Oct 1991	Sep 1995	2024-03-01	21450
Buick	Skylark	2.3 Limited	Stufenheck	Frontantrieb	Benzin	86	117	Sep 1992	Sep 1993	2024-03-01	21452
Cadillac	Seville	4.5	Stufenheck	Frontantrieb	Benzin	115	156	Oct 1987	Sep 1989	2024-03-01	21453
Cadillac	Seville	4.9	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1990	Dec 1991	2024-03-01	21454
Hyundai	H-1 / starex	2.4	Bus	Heckantrieb	Benzin	101	137	Feb 2003	Apr 2004	2024-03-01	21455
Chevrolet	Camaro	3.1	Coupe	Heckantrieb	Benzin	103	140	Oct 1989	Sep 1992	2024-03-01	21464
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	127	173	Oct 1987	Sep 1992	2024-03-01	21465
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	168	228	Oct 1984	Sep 1992	2024-03-01	21466
Chevrolet	Camaro	3.8	Coupe	Heckantrieb	Benzin	149	203	Oct 1995	Sep 1997	2024-03-01	21467
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1986	Sep 1988	2024-03-01	21469
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	179	243	Oct 1985	Sep 1989	2024-03-01	21472
Fiat	Palio	1.2	Schrägheck	Frontantrieb	Benzin	50	68	Jun 1999	Oct 2000	2024-03-01	21473
Suzuki	Wagon r	1	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2004	Aug 2005	2024-03-01	21480
Suzuki	Wagon r	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Jun 2004	Aug 2005	2024-03-01	21481
Buick	Park avenue	3.8	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1994	Oct 1996	2024-03-01	21494
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1998	Jul 2002	2024-03-01	21499
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	107	146	Aug 2002	Oct 2005	2024-03-01	21500
Peugeot	206	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Aug 1998	Jul 2000	2024-03-01	21501
Mazda	2	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Feb 2003	Jun 2007	2024-03-01	21509
Jeep	Cherokee	2.5 SE	Geländewagen geschlossen	Heckantrieb	Benzin	87	118	Oct 1996	Sep 1999	2024-03-01	21520
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	89	121	Oct 1990	Sep 1996	2024-03-01	21521
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21522
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21523
Jeep	Cherokee	4	Geländewagen geschlossen	Heckantrieb	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21524
Jeep	Cherokee	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21525
Jeep	Cherokee	2.1 D 4X4	Geländewagen geschlossen	Allrad	Diesel	59	80	Oct 1986	Sep 1992	2024-03-01	21526
Lamborghini	Diablo	5.7	Coupe	Heckantrieb	Benzin	361	491	Mar 1990	Jan 1999	2024-03-01	21533
Mitsubishi	L400	2	Bus	Heckantrieb	Benzin	83	113	Sep 1995	Oct 2002	2024-03-01	21535
Mitsubishi	L400	2.4	Bus	Heckantrieb	Benzin	97	132	May 1995	Oct 2002	2024-03-01	21536
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	201	273	May 2000	Sep 2002	2024-03-01	21543
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	213	290	Sep 1999	Dec 2006	2024-03-01	21544
Chevrolet	Tahoe	5.3 AWD	SUV	Allrad	Benzin	213	290	Oct 2002	Dec 2006	2024-03-01	21545
Mazda	Tribute	2.3 GX	SUV	Frontantrieb	Benzin	110	150	Dec 2003	Oct 2004	2024-03-01	21546
Tata	Indica	1.4 L	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1998	Sep 2002	2024-03-01	21548
Aston Martin	Zagato vantage	6.0 V12	Coupe	Heckantrieb	Benzin	380	517	May 2012	-	2024-03-01	21550
Nissan	X-Trail i	2.0 4X4	SUV	Allrad	Benzin	110	150	Sep 2001	Jan 2013	2024-03-01	21555
Nissan	X-Trail i	2.2 DCI	SUV	Frontantrieb	Diesel	84	114	Oct 2004	Jan 2013	2024-03-01	21557
Hyundai	Terracan	2.5 D	SUV	Heckantrieb	Diesel	74	101	Jun 2001	Oct 2003	2024-03-01	21559
Honda	Jazz ii	1.5 Vtec	Schrägheck	Frontantrieb	Benzin	81	110	Apr 2002	Jul 2008	2024-03-01	21561
Renault	Thalia i	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1998	Oct 2008	2025-12-01	21562
Mercedes-benz	Clk	CLK 500	Coupe	Heckantrieb	Benzin	285	388	Jun 2006	May 2009	2024-03-01	21568
Porsche	Cayenne	3.2	SUV	Allrad	Benzin	177	241	Aug 2003	Sep 2007	2024-03-01	21569
Renault	Espace iv	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	85	116	Apr 2003	Feb 2005	2024-03-01	21576
Chrysler	300c	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Jun 2005	Nov 2012	2024-03-01	21586
Infiniti	Fx	35	SUV	Heckantrieb	Benzin	206	280	Feb 2003	Dec 2008	2024-03-01	21587
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	155	211	Mar 2006	May 2010	2024-03-01	21589
Jeep	Compass	2.4	SUV	Frontantrieb	Benzin	125	170	Aug 2006	-	2024-03-01	21591
Jeep	Compass	2.0 CRD	SUV	Frontantrieb	Diesel	103	140	Aug 2006	-	2024-03-01	21592
Peugeot	Boxer	3.0 HDI 155	Kasten	Frontantrieb	Diesel	115	156	Jul 2006	Dec 2015	2024-03-01	21593
Peugeot	Boxer	3.0 HDI 155	Pritsche/Fahrgestell	Frontantrieb	Diesel	115	156	Apr 2006	Dec 2015	2024-03-01	21594
Cadillac	Allante	4.5	Cabriolet	Frontantrieb	Benzin	150	204	Oct 1988	Sep 1992	2024-03-01	21641
Cadillac	Allante	4.6	Cabriolet	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21642
Cadillac	Allante	4.5	Coupe	Frontantrieb	Benzin	150	204	Jan 1991	Sep 1992	2024-03-01	21643
Cadillac	Allante	4.6	Coupe	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21644
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	190	258	Aug 2013	Jul 2018	2024-03-01	21691
Ford	Mondeo i	2.0 I 16V 4X4	Stufenheck	Allrad	Benzin	100	136	Feb 1993	Aug 1996	2024-03-01	21709
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	103	140	Oct 1984	Sep 1985	2024-03-01	21714
Chevrolet	Astro	4.3	Bus	Heckantrieb	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21717
Chevrolet	Astro	4.3 AWD	Bus	Allrad	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21718
Chevrolet	Astro	4.3 Luxury	Bus	Heckantrieb	Benzin	119	162	Oct 1986	Sep 1994	2024-03-01	21719
Chevrolet	Astro	4.3 Luxury AWD	Bus	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21720
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	107	146	Oct 1989	Sep 1994	2024-03-01	21721
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	119	162	Oct 1984	Sep 1994	2024-03-01	21722
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21723
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	127	173	Oct 1994	Sep 1995	2024-03-01	21726
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21727
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21728
Jeep	Wrangler iii	3.8 RWD	Geländewagen offen	Heckantrieb	Benzin	146	199	Oct 2007	Sep 2010	2024-03-01	21750
Honda	Beat	0.7	Cabriolet	Heckantrieb	Benzin	47	64	May 1991	Sep 1996	2024-03-01	21757
Daihatsu	Terios	1.5 Vvt-i RWD	Geländewagen geschlossen	Heckantrieb	Benzin	77	105	Nov 2005	-	2024-03-01	21760
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	119	162	Oct 1991	Sep 1996	2024-03-01	21786
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	149	203	Oct 1996	Sep 1999	2024-03-01	21788
Chevrolet	C1500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2000	2024-03-01	21789
Chevrolet	C2500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2001	2024-03-01	21796
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	103	140	Oct 2013	Aug 2020	2024-03-01	21803
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Oct 2013	Aug 2020	2024-03-01	21804
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	105	143	Oct 2013	Aug 2018	2024-03-01	21805
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	112	152	Sep 1980	Dec 1984	2024-03-01	21821
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	114	155	Oct 1982	Sep 1986	2024-03-01	21822
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	100	136	Oct 1987	Sep 1990	2024-03-01	21823
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	104	141	Oct 1986	Sep 1989	2024-03-01	21824
Chevrolet	Caprice	4.3	Stufenheck	Heckantrieb	Benzin	149	203	Oct 1991	Sep 1996	2024-03-01	21825
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	127	173	Oct 1990	Sep 1993	2024-03-01	21826


--- 新建对话（分支降级） / Round 25 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a696a5b-926c-83ea-bbbb-eb9bdb849c21
新对话：https://chatgpt.com/c/6a6cd68f-2e2c-83ea-a523-95f87da742e5

--- Round 25 / checkpoint 续跑 ---
## 更新点

* 闭合 Chevrolet Astro I 货运厢式车 `21721–21723`。
* 1994 官方技术指南确认货运版同时存在常规车身、加长车身，并分别提供后驱 M-body 与四驱 L-body；相同车身长度的后驱、四驱版本共用尺寸组。
* 常规车身采用 `176.8 × 77.5 × 76.2 in`，加长车身采用 `186.8 × 77.5 × 76.2 in`；宽度为不含后视镜口径。换算取整后分别为 `4491 × 1969 × 1935 mm`、`4745 × 1969 × 1935 mm`。([Edmunds][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* READY 映射：122
* PENDING Ktype：8
* 已确认尺寸组：83
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21721_regular	21721	Van	Astro I	L	3	EU-CHEVROLET-ASTRO-I-VAN-REGULAR-01	MEDIUM	第一代四驱货运厢式车常规车身。	READY
21721_extended	21721	Van	Astro I	L	3	EU-CHEVROLET-ASTRO-I-VAN-EXTENDED-01	MEDIUM	第一代四驱货运厢式车加长车身。	READY
21722_regular	21722	Van	Astro I	M	3	EU-CHEVROLET-ASTRO-I-VAN-REGULAR-01	MEDIUM	第一代后驱货运厢式车常规车身。	READY
21722_extended	21722	Van	Astro I	M	3	EU-CHEVROLET-ASTRO-I-VAN-EXTENDED-01	MEDIUM	第一代后驱货运厢式车加长车身。	READY
21723_regular	21723	Van	Astro I	L	3	EU-CHEVROLET-ASTRO-I-VAN-REGULAR-01	MEDIUM	第一代四驱货运厢式车常规车身。	READY
21723_extended	21723	Van	Astro I	L	3	EU-CHEVROLET-ASTRO-I-VAN-EXTENDED-01	MEDIUM	第一代四驱货运厢式车加长车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-ASTRO-I-VAN-REGULAR-01	4491	1969	1935	Chevrolet 1994 Astro Van official technical guide; Edmunds 1993 Chevrolet Astro Cargo specifications	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf;https://www.edmunds.com/chevrolet/astro-cargo/1993/minivan/features-specs/
EU-CHEVROLET-ASTRO-I-VAN-EXTENDED-01	4745	1969	1935	Chevrolet 1994 Astro Van official technical guide; Edmunds 1994 Chevrolet Astro Cargo specifications	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf;https://www.edmunds.com/chevrolet/astro-cargo/1994/features-specs/
```

## 下一步优先处理

1. Mitsubishi L300 `21329` 与 Fiat Ducato 4×4 Bus `21437`。
2. Peugeot Boxer `21593–21594` 的长度、车顶及底盘分支。
3. Chevrolet C1500/C2500 `21786、21788、21789、21796` 的驾驶室与货斗组合。

推进信号：CONTINUE

[1]: https://www.edmunds.com/chevrolet/astro-cargo/1994/features-specs/?utm_source=chatgpt.com "Used 1994 Chevrolet Astro Cargo Specs & Features"


--- 发送 / 继续到 Round 26 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 26 / checkpoint 续跑 ---
## 更新点

* 复用跨批次已闭合的 Peugeot Boxer II 尺寸组。
* Ktype `21593` 拆分为 8 个厢式车长度/车顶分支。
* Ktype `21594` 拆分为 4 个底盘驾驶室长度分支。
* 本轮未创建或修正 DIMENSION_GROUP。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* PENDING Ktype：6
* READY 映射：134
* PENDING 映射：6
* 已确认尺寸组：83
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21593_l1h1	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	HIGH	L1H1厢式车物理分支。	READY
21593_l1h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	HIGH	L1H2厢式车物理分支。	READY
21593_l2h1	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	HIGH	L2H1厢式车物理分支。	READY
21593_l2h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	HIGH	L2H2厢式车物理分支。	READY
21593_l3h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	HIGH	L3H2厢式车物理分支。	READY
21593_l3h3	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	HIGH	L3H3厢式车物理分支。	READY
21593_l4h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	HIGH	L4H2厢式车物理分支。	READY
21593_l4h3	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	HIGH	L4H3厢式车物理分支。	READY
21594_l1	21594	Pickup	Boxer II	X250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	HIGH	L1底盘驾驶室物理分支。	READY
21594_l2	21594	Pickup	Boxer II	X250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	HIGH	L2底盘驾驶室物理分支。	READY
21594_l3	21594	Pickup	Boxer II	X250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	HIGH	L3底盘驾驶室物理分支。	READY
21594_l4	21594	Pickup	Boxer II	X250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	HIGH	L4底盘驾驶室物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. Mitsubishi L300 III `21329`。
2. Fiat Ducato II 4×4 Bus `21437`。
3. Chevrolet C1500/C2500 `21786、21788、21789、21796` 的驾驶室与货斗物理分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 27 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 27 / checkpoint 续跑 ---
## 更新点

* 闭合 Mitsubishi L300 III `21329`，确认 `P05W` 后驱巴士外廓为 `4285 × 1690 × 1955 mm`。([Goo-Net Exchange][1])
* 闭合 Fiat Ducato II `21437`，拆分为 X230 短轴与长轴巴士分支，复用已有尺寸组，不重复输出尺寸事实。该 Ktype 对应 Ducato Bus 230 的 2.0 4×4、80 kW/109 PS 版本。([AUTODOC][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* PENDING Ktype：4
* READY 映射：137
* PENDING 映射：4
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21329	21329	MPV	L300 III	P05W	4	EU-MITSUBISHI-L300-III-P05W-MPV-01	MEDIUM	P05W后驱巴士物理外廓。	READY
21437_swb	21437	MPV	Ducato II	230		EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	MEDIUM	X230短轴巴士物理分支。	READY
21437_lwb	21437	MPV	Ducato II	230		EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	MEDIUM	X230长轴巴士物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-L300-III-P05W-MPV-01	4285	1690	1955	GAZOO Mitsubishi Delica Star Wagon Q-P05W catalog; Goo-net Exchange Mitsubishi Delica Star Wagon Q-P05W catalog	https://gazoo.com/catalog/maker/MITSUBISHI/DELICA_STAR_WAGON/198904/4005346/;https://www.goo-net-exchange.com/catalog/MITSUBISHI__DELICA_STAR_WAGON/4005346/
```

## 下一步优先处理

1. Chevrolet C1500 `21786、21788、21789` 的 Regular Cab、Extended Cab 与不同货斗长度分支。
2. Chevrolet C2500 `21796` 的驾驶室、货斗及重载车身分支。
3. 四个皮卡 Ktype 闭合后立即进入一次机械收尾并输出两张最终完整 TSV。

推进信号：CONTINUE

[1]: https://www.goo-net-exchange.com/catalog/MITSUBISHI__DELICA_STAR_WAGON/4005346/?utm_source=chatgpt.com "MITSUBISHI DELICA STAR WAGON, XL SALOON catalog"
[2]: https://www.autodoc.co.uk/car-parts/coil-springs-10213/fiat/ducato/ducato-bus-230/21437-2-0-4x4?utm_source=chatgpt.com "Fiat Ducato 230 Minibus 2.0 4x4 Coil spring (109 hp RFW)"


--- 发送 / 继续到 Round 28 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 发送 / 新建对话重发 / Round 28 ---
【任务名称】
【全量表更新】all 第 1101-1200 行

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
all 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318
EU-AUDI-A6-C6-4F2-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-4F5-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-ALLROAD-WAGON-01	4930	1860	1520
EU-AUDI-A6-C6-AVANT-WAGON-4F5-01	4933	1855	1463
EU-AUDI-A6-C6-FACELIFT-SEDAN-01	4927	1855	1459
EU-AUDI-A6-C6-FACELIFT-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-PREFL-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-PREFL-WAGON-01	4933	1855	1463
EU-AUDI-A6-C6-SEDAN-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-4F2-01	4916	1855	1459
EU-AUDI-A6-C6-SEDAN-FACELIFT-01	4927	1855	1459
EU-AUDI-A6-C6-SEDAN-PREFL-01	4916	1855	1459
EU-AUDI-A6-C6-WAGON-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-ALLROAD-FACELIFT-01	4934	1862	1521
EU-AUDI-A6-C6-WAGON-ALLROAD-PREFL-01	4934	1862	1519
EU-AUDI-A6-C6-WAGON-FACELIFT-01	4927	1855	1463
EU-AUDI-A6-C6-WAGON-PREFL-01	4933	1855	1463
EU-AUDI-A6-C6-WAGON-S6-FACELIFT-01	4938	1864	1446
EU-AUDI-A6-C6-WAGON-S6-PREFL-01	4933	1864	1453
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737
EU-BMW-6-SERIES-E63-COUPE-FACELIFT-2D-01	4820	1855	1374
EU-BMW-6-SERIES-E64-CONVERTIBLE-FACELIFT-2D-01	4820	1855	1374
EU-BMW-X5-E70-SUV-01	4854	1933	1766
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4803	1715	1351
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351
EU-CADILLAC-SEVILLE-V-SEDAN-01	4991	1901	1414
EU-CHEVROLET-CAMARO-III-CONVERTIBLE-2D-01	4877	1849	1278
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278
EU-CHEVROLET-CAMARO-V-COUPE-2D-01	4836	1918	1377
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	4435	1844	1244
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450
EU-FIAT-DUCATO-II-230L-4X4-VAN-01	5505	1998	2490
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
EU-FIAT-PALIO-I-178-HATCHBACK-01	3827	1634	1446
EU-FIAT-PALIO-I-178-HATCHBACK-02	3735	1626	1446
EU-FIAT-PALIO-WEEKEND-178-JTD-WAGON-5D-01	4130	1626	1515
EU-FIAT-PALIO-WEEKEND-178-WAGON-5D-01	4130	1626	1475
EU-FORD-MONDEO-III-B4Y-SEDAN-01	4731	1812	1429
EU-FORD-MONDEO-III-B5Y-HATCHBACK-01	4731	1812	1429
EU-FORD-MONDEO-III-SEDAN-01	4731	1812	1429
EU-FORD-MONDEO-IV-HATCHBACK-FACELIFT-01	4784	1886	1500
EU-FORD-MONDEO-IV-HATCHBACK-PREFL-01	4778	1886	1500
EU-FORD-MONDEO-IV-SEDAN-FACELIFT-01	4850	1886	1500
EU-FORD-MONDEO-IV-SEDAN-PREFL-01	4844	1886	1500
EU-FORD-MONDEO-IV-WAGON-FACELIFT-01	4837	1886	1512
EU-FORD-MONDEO-IV-WAGON-PREFL-01	4830	1886	1512
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359
EU-FORD-USA-MUSTANG-IV-NEW-EDGE-CONVERTIBLE-2D-01	4653	1857	1351
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407
EU-HONDA-JAZZ-III-GE-HATCHBACK-5D-01	3900	1695	1525
EU-INFINITI-FX-II-S51-SUV-5D-01	4865	1925	1680
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-JEEP-CHEROKEE-KJ-SUV-01	4496	1819	1866
EU-JEEP-CHEROKEE-SJ-SUV-2D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-SJ-SUV-2D-WIDETRACK-01	4660	2000	1720
EU-JEEP-CHEROKEE-SJ-SUV-4D-NARROW-01	4660	1920	1700
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700
EU-JEEP-COMPASS-I-MK-SUV-01	4405	1810	1630
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800
EU-JEEP-WRANGLER-III-JK-SUV-2D-02	4223	1873	1816
EU-JEEP-WRANGLER-III-JK-SUV-4D-01	4751	1877	1834
EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	4470	2040	1105
EU-MASERATI-BITURBO-420-SI-SEDAN-01	4400	1730	1360
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475
EU-MERCEDES-BENZ-CLK-A209-CONVERTIBLE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CLK500-CONVERTIBLE-2D-01	4652	1740	1415
EU-MERCEDES-BENZ-CLK-A209-FACELIFT-CONVERTIBLE-2D-01	4652	1740	1413
EU-MERCEDES-BENZ-CLK-C209-COUPE-01	4652	1740	1400
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413
EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	4595	1695	1855
EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	4995	1695	1960
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-NISSAN-X-TRAIL-II-T31-SUV-FACELIFT-01	4635	1790	1700
EU-NISSAN-X-TRAIL-II-T31-SUV-PREFL-01	4630	1785	1685
EU-NISSAN-X-TRAIL-I-T30-SUV-PREFL-01	4510	1765	1675
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426
EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	3822	1652	1425
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-LWB-01	5600	2000	2100
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-MWB-01	5120	2000	2100
EU-PEUGEOT-BOXER-I-230-CHASSIS-CAB-SWB-01	4770	2000	2100
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
EU-PEUGEOT-PARTNER-II-B9-TEPEE-4X4-MPV-5D-01	4380	1810	1865
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L1-01	4380	1810	1894
EU-PEUGEOT-PARTNER-II-B9-VAN-4X4-L2-01	4628	1810	1894
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-RENAULT-ESPACE-IV-PH2-MPV-SWB-01	4656	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-III-IV-MPV-01	4661	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	4656	1860	1728
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-SWB-01	4656	1860	1728
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	3500	1600	1660
EU-TATA-INDICA-I-HATCHBACK-01	3660	1625	1485

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6	3.2 FSI Quattro	Stufenheck	Allrad	Benzin	183	249	Sep 2006	Oct 2008	2024-03-01	21323
Mitsubishi	L 300 iii	2.5 TD	Bus	Heckantrieb	Diesel	64	87	Feb 1987	May 2003	2024-03-01	21329
Jaguar	Xj	4	Coupe	Heckantrieb	Benzin	175	238	Oct 1986	Dec 1989	2024-03-01	21330
Jaguar	Xjsc convertible	4	Cabriolet	Heckantrieb	Benzin	175	238	Oct 1987	Dec 1989	2024-03-01	21335
Mitsubishi	Lancer v	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Jun 1992	Feb 1995	2024-03-01	21346
Audi	A6 c4	2	Stufenheck	Frontantrieb	Benzin	79	107	Jun 1994	Jul 1995	2024-03-01	21350
Alfa Romeo	Spider	2	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1974	Dec 1984	2024-03-01	21354
Toyota	Supra	3	Coupe	Heckantrieb	Benzin	140	190	Jan 1986	May 1993	2024-03-01	21355
Peugeot	405 i break	1.4	Kombi	Frontantrieb	Benzin	47	64	May 1988	Jul 1992	2024-03-01	21360
BMW	6	635 CSI	Coupe	Heckantrieb	Benzin	160	218	May 1982	Aug 1988	2024-11-01	21375
Maserati	Biturbo	E	Coupe	Heckantrieb	Benzin	139	189	Jun 1982	Oct 1987	2024-03-01	21401
Mitsubishi	Lancer vii	EVO IX	Stufenheck	Allrad	Benzin	213	290	Aug 2005	Sep 2006	2024-03-01	21408
Fiat	Ducato	2.0 4X4	Bus	Allrad	Benzin	80	109	Nov 1994	Nov 2001	2024-03-01	21437
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	108	147	Jan 1994	May 1999	2024-03-01	21442
Ford USA	Mustang	4.6	Coupe	Heckantrieb	Benzin	165	224	Nov 1995	May 1999	2024-03-01	21443
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	108	147	Sep 1993	May 1999	2024-03-01	21444
Peugeot	Partner	1.9 D	Großraumlimousine	Frontantrieb	Diesel	51	69	May 1996	Dec 1998	2024-03-01	21448
Chevrolet	Lumina apv	3.8	Großraumlimousine	Frontantrieb	Benzin	123	167	Oct 1991	Sep 1995	2024-03-01	21450
Buick	Skylark	2.3 Limited	Stufenheck	Frontantrieb	Benzin	86	117	Sep 1992	Sep 1993	2024-03-01	21452
Cadillac	Seville	4.5	Stufenheck	Frontantrieb	Benzin	115	156	Oct 1987	Sep 1989	2024-03-01	21453
Cadillac	Seville	4.9	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1990	Dec 1991	2024-03-01	21454
Hyundai	H-1 / starex	2.4	Bus	Heckantrieb	Benzin	101	137	Feb 2003	Apr 2004	2024-03-01	21455
Chevrolet	Camaro	3.1	Coupe	Heckantrieb	Benzin	103	140	Oct 1989	Sep 1992	2024-03-01	21464
Chevrolet	Camaro	5	Coupe	Heckantrieb	Benzin	127	173	Oct 1987	Sep 1992	2024-03-01	21465
Chevrolet	Camaro	5.7	Coupe	Heckantrieb	Benzin	168	228	Oct 1984	Sep 1992	2024-03-01	21466
Chevrolet	Camaro	3.8	Coupe	Heckantrieb	Benzin	149	203	Oct 1995	Sep 1997	2024-03-01	21467
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	110	150	Oct 1986	Sep 1988	2024-03-01	21469
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	179	243	Oct 1985	Sep 1989	2024-03-01	21472
Fiat	Palio	1.2	Schrägheck	Frontantrieb	Benzin	50	68	Jun 1999	Oct 2000	2024-03-01	21473
Suzuki	Wagon r	1	Schrägheck	Frontantrieb	Benzin	44	60	Jun 2004	Aug 2005	2024-03-01	21480
Suzuki	Wagon r	1.2	Schrägheck	Frontantrieb	Benzin	59	80	Jun 2004	Aug 2005	2024-03-01	21481
Buick	Park avenue	3.8	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1994	Oct 1996	2024-03-01	21494
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1998	Jul 2002	2024-03-01	21499
Mazda	Mx-5 ii	1.8	Cabriolet	Heckantrieb	Benzin	107	146	Aug 2002	Oct 2005	2024-03-01	21500
Peugeot	206	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Aug 1998	Jul 2000	2024-03-01	21501
Mazda	2	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Feb 2003	Jun 2007	2024-03-01	21509
Jeep	Cherokee	2.5 SE	Geländewagen geschlossen	Heckantrieb	Benzin	87	118	Oct 1996	Sep 1999	2024-03-01	21520
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	89	121	Oct 1990	Sep 1996	2024-03-01	21521
Jeep	Cherokee	2.5	Geländewagen geschlossen	Heckantrieb	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21522
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	90	122	Oct 1986	Sep 1990	2024-03-01	21523
Jeep	Cherokee	4	Geländewagen geschlossen	Heckantrieb	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21524
Jeep	Cherokee	4.0 4X4	Geländewagen geschlossen	Allrad	Benzin	131	178	Oct 1986	Sep 1990	2024-03-01	21525
Jeep	Cherokee	2.1 D 4X4	Geländewagen geschlossen	Allrad	Diesel	59	80	Oct 1986	Sep 1992	2024-03-01	21526
Lamborghini	Diablo	5.7	Coupe	Heckantrieb	Benzin	361	491	Mar 1990	Jan 1999	2024-03-01	21533
Mitsubishi	L400	2	Bus	Heckantrieb	Benzin	83	113	Sep 1995	Oct 2002	2024-03-01	21535
Mitsubishi	L400	2.4	Bus	Heckantrieb	Benzin	97	132	May 1995	Oct 2002	2024-03-01	21536
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	201	273	May 2000	Sep 2002	2024-03-01	21543
Chevrolet	Tahoe	5.3	SUV	Heckantrieb	Benzin	213	290	Sep 1999	Dec 2006	2024-03-01	21544
Chevrolet	Tahoe	5.3 AWD	SUV	Allrad	Benzin	213	290	Oct 2002	Dec 2006	2024-03-01	21545
Mazda	Tribute	2.3 GX	SUV	Frontantrieb	Benzin	110	150	Dec 2003	Oct 2004	2024-03-01	21546
Tata	Indica	1.4 L	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1998	Sep 2002	2024-03-01	21548
Aston Martin	Zagato vantage	6.0 V12	Coupe	Heckantrieb	Benzin	380	517	May 2012	-	2024-03-01	21550
Nissan	X-Trail i	2.0 4X4	SUV	Allrad	Benzin	110	150	Sep 2001	Jan 2013	2024-03-01	21555
Nissan	X-Trail i	2.2 DCI	SUV	Frontantrieb	Diesel	84	114	Oct 2004	Jan 2013	2024-03-01	21557
Hyundai	Terracan	2.5 D	SUV	Heckantrieb	Diesel	74	101	Jun 2001	Oct 2003	2024-03-01	21559
Honda	Jazz ii	1.5 Vtec	Schrägheck	Frontantrieb	Benzin	81	110	Apr 2002	Jul 2008	2024-03-01	21561
Renault	Thalia i	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1998	Oct 2008	2025-12-01	21562
Mercedes-benz	Clk	CLK 500	Coupe	Heckantrieb	Benzin	285	388	Jun 2006	May 2009	2024-03-01	21568
Porsche	Cayenne	3.2	SUV	Allrad	Benzin	177	241	Aug 2003	Sep 2007	2024-03-01	21569
Renault	Espace iv	1.9 DCI	Großraumlimousine	Frontantrieb	Diesel	85	116	Apr 2003	Feb 2005	2024-03-01	21576
Chrysler	300c	6.1 Srt8	Stufenheck	Heckantrieb	Benzin	317	431	Jun 2005	Nov 2012	2024-03-01	21586
Infiniti	Fx	35	SUV	Heckantrieb	Benzin	206	280	Feb 2003	Dec 2008	2024-03-01	21587
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	155	211	Mar 2006	May 2010	2024-03-01	21589
Jeep	Compass	2.4	SUV	Frontantrieb	Benzin	125	170	Aug 2006	-	2024-03-01	21591
Jeep	Compass	2.0 CRD	SUV	Frontantrieb	Diesel	103	140	Aug 2006	-	2024-03-01	21592
Peugeot	Boxer	3.0 HDI 155	Kasten	Frontantrieb	Diesel	115	156	Jul 2006	Dec 2015	2024-03-01	21593
Peugeot	Boxer	3.0 HDI 155	Pritsche/Fahrgestell	Frontantrieb	Diesel	115	156	Apr 2006	Dec 2015	2024-03-01	21594
Cadillac	Allante	4.5	Cabriolet	Frontantrieb	Benzin	150	204	Oct 1988	Sep 1992	2024-03-01	21641
Cadillac	Allante	4.6	Cabriolet	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21642
Cadillac	Allante	4.5	Coupe	Frontantrieb	Benzin	150	204	Jan 1991	Sep 1992	2024-03-01	21643
Cadillac	Allante	4.6	Coupe	Frontantrieb	Benzin	220	299	Oct 1992	Sep 1993	2024-03-01	21644
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	190	258	Aug 2013	Jul 2018	2024-03-01	21691
Ford	Mondeo i	2.0 I 16V 4X4	Stufenheck	Allrad	Benzin	100	136	Feb 1993	Aug 1996	2024-03-01	21709
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	103	140	Oct 1984	Sep 1985	2024-03-01	21714
Chevrolet	Astro	4.3	Bus	Heckantrieb	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21717
Chevrolet	Astro	4.3 AWD	Bus	Allrad	Benzin	112	152	Apr 1992	Sep 1994	2024-03-01	21718
Chevrolet	Astro	4.3 Luxury	Bus	Heckantrieb	Benzin	119	162	Oct 1986	Sep 1994	2024-03-01	21719
Chevrolet	Astro	4.3 Luxury AWD	Bus	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21720
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	107	146	Oct 1989	Sep 1994	2024-03-01	21721
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	119	162	Oct 1984	Sep 1994	2024-03-01	21722
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	119	162	Oct 1989	Sep 1994	2024-03-01	21723
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	127	173	Oct 1994	Sep 1995	2024-03-01	21726
Chevrolet	Astro	4.3	Kasten	Heckantrieb	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21727
Chevrolet	Astro	4.3 AWD	Kasten	Allrad	Benzin	142	193	Oct 1994	May 2005	2024-03-01	21728
Jeep	Wrangler iii	3.8 RWD	Geländewagen offen	Heckantrieb	Benzin	146	199	Oct 2007	Sep 2010	2024-03-01	21750
Honda	Beat	0.7	Cabriolet	Heckantrieb	Benzin	47	64	May 1991	Sep 1996	2024-03-01	21757
Daihatsu	Terios	1.5 Vvt-i RWD	Geländewagen geschlossen	Heckantrieb	Benzin	77	105	Nov 2005	-	2024-03-01	21760
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	119	162	Oct 1991	Sep 1996	2024-03-01	21786
Chevrolet	C1500	4.3	Pick-up	Heckantrieb	Benzin	149	203	Oct 1996	Sep 1999	2024-03-01	21788
Chevrolet	C1500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2000	2024-03-01	21789
Chevrolet	C2500	6.5 Tdic	Pick-up	Heckantrieb	Diesel	135	184	Oct 1996	Dec 2001	2024-03-01	21796
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	103	140	Oct 2013	Aug 2020	2024-03-01	21803
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Oct 2013	Aug 2020	2024-03-01	21804
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	105	143	Oct 2013	Aug 2018	2024-03-01	21805
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	112	152	Sep 1980	Dec 1984	2024-03-01	21821
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	114	155	Oct 1982	Sep 1986	2024-03-01	21822
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	100	136	Oct 1987	Sep 1990	2024-03-01	21823
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	104	141	Oct 1986	Sep 1989	2024-03-01	21824
Chevrolet	Caprice	4.3	Stufenheck	Heckantrieb	Benzin	149	203	Oct 1991	Sep 1996	2024-03-01	21825
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	127	173	Oct 1990	Sep 1993	2024-03-01	21826


--- 新建对话（分支降级） / Round 28 ---
触发原因：对话分支 UI 不可用，自动降级为新建对话
原对话：https://chatgpt.com/c/6a6cd68f-2e2c-83ea-a523-95f87da742e5
新对话：https://chatgpt.com/c/6a6ce23f-385c-83ea-9e9a-a7d2767bdecf

--- Round 28 / checkpoint 续跑 ---
更新点

* 采用缓存优先模式，先闭合 22 个可直接命中跨批次既有尺寸组的 Ktype。
* 本轮复用 17 个既有尺寸组，未重复抓取或重复输出尺寸事实。
* 发动机、功率及驱动差异未被错误拆成独立尺寸组。

当前批次进度

* 输入 Ktype：100
* READY Ktype：22
* READY 映射：22
* PENDING 映射：0
* 尚未首次处理：78
* 本轮复用既有尺寸组：17
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21323	21323	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH	4F2四门改款前外廓。	READY
21442	21442	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	MEDIUM	SN95双门Coupe旧款外廓；结束月份接近New Edge切换边界。	READY
21443	21443	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	MEDIUM	SN95双门Coupe旧款外廓；结束月份接近New Edge切换边界。	READY
21444	21444	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	MEDIUM	SN95双门敞篷旧款外廓；结束月份接近New Edge切换边界。	READY
21448	21448	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	HIGH	第一阶段乘用MPV外廓。	READY
21452	21452	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH	第七代四门Sedan外廓。	READY
21453	21453	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	第四代四门Sedan外廓。	READY
21454	21454	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH	发动机变化不改变第四代Sedan外廓。	READY
21464	21464	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门Coupe外廓。	READY
21465	21465	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门Coupe外廓。	READY
21466	21466	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH	第三代三门Coupe外廓。	READY
21469	21469	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH	第三代四门Sedan外廓。	READY
21472	21472	Convertible	Corvette C4	Y-body	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH	C4双门敞篷外廓。	READY
21494	21494	Sedan	Park Avenue I	C-body	4	EU-BUICK-PARK-AVENUE-I-SEDAN-01	HIGH	第一代标准版四门Sedan外廓。	READY
21548	21548	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH	第一代五门Hatchback外廓。	READY
21568	21568	Coupe	CLK C209	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH	C209改款后双门Coupe外廓。	READY
21576	21576	MPV	Espace IV	JK	5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH	第四代Phase II标准轴MPV外廓。	READY
21589	21589	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	4L改款前五门SUV外廓。	READY
21591	21591	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	第一代MK五门SUV外廓。	READY
21592	21592	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH	动力类型差异不改变MK五门SUV外廓。	READY
21691	21691	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH	F15五门SUV外廓。	READY
21760	21760	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH	J200五门SUV外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

无

下一步优先处理

1. 优先闭合已有部分结果的 Audi A6 C4、Toyota Supra A70、Mazda MX-5 NB、Mitsubishi Lancer Evolution IX 等单一乘用车外廓。
2. 集中核对 Chevrolet Tahoe GMT800、Infiniti FX S50、Porsche Cayenne 955 标准版等尚无可直接复用尺寸组的 SUV。
3. 最后处理 Peugeot Boxer、Chevrolet Astro、C1500/C2500 等多轴距、多车顶或 CAB/BED 分支车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 29 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 29 / checkpoint 续跑 ---
## 更新点

* 已完成当前批次最终汇总，不再执行重复车型检索。
* 已完成固定表头、主键唯一性、引用闭合、尺寸及来源非空检查。
* Astro 尺寸组完成一次纠正，现有映射已同步闭合。
* 两张最终 TSV 文件已按任务指定文件名生成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：134
* PENDING 映射：0
* DIMENSION_GROUP：87
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 长宽高及来源完整：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21323	21323	Sedan	A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH	4F2四门改款前外廓。	READY
21329	21329	MPV	L300 III		4	EU-MITSUBISHI-L300-III-BUS-SWB-01	MEDIUM	标准轴Bus外廓。	READY
21330	21330	Coupe	XJS		2	EU-JAGUAR-XJS-COUPE-2D-01	HIGH	XJS双门Coupe外廓。	READY
21335	21335	Convertible	XJ-SC		2	EU-JAGUAR-XJSC-CONVERTIBLE-2D-01	HIGH	XJ-SC双门敞篷外廓。	READY
21346	21346	Sedan	Lancer V		4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
21350	21350	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-4D-01	HIGH		READY
21354	21354	Convertible	Spider 115	115	2	EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-2D-01	HIGH		READY
21355	21355	Coupe	Supra A70	A70	3	EU-TOYOTA-SUPRA-A70-COUPE-3D-01	HIGH		READY
21360	21360	Wagon	405 I Break	15E	5	EU-PEUGEOT-405-I-BREAK-WAGON-5D-01	HIGH		READY
21375_prefl	21375	Coupe	6 Series E24	E24	2	EU-BMW-6-SERIES-E24-COUPE-PREFL-2D-01	HIGH	1982改款后、1987外形修订前。	READY
21375_facelift	21375	Coupe	6 Series E24	E24	2	EU-BMW-6-SERIES-E24-COUPE-FACELIFT-2D-01	HIGH	1987外形修订分支。	READY
21401	21401	Coupe	Biturbo		2	EU-MASERATI-BITURBO-COUPE-2D-01	HIGH		READY
21408	21408	Sedan	Lancer Evolution IX	CT9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	HIGH		READY
21437_swb	21437	MPV	Ducato II	230	4	EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	HIGH	短轴Bus分支。	READY
21437_lwb	21437	MPV	Ducato II	230	4	EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	HIGH	长轴Bus分支。	READY
21442	21442	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	MEDIUM	SN95双门Coupe旧款外廓。	READY
21443	21443	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	MEDIUM	SN95双门Coupe旧款外廓。	READY
21444	21444	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	MEDIUM	SN95双门敞篷旧款外廓。	READY
21448	21448	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	HIGH	第一阶段乘用MPV外廓。	READY
21450	21450	MPV	Lumina APV		4	EU-CHEVROLET-LUMINA-APV-MPV-01	HIGH		READY
21452	21452	Sedan	Skylark VII		4	EU-BUICK-SKYLARK-VII-SEDAN-4D-01	HIGH		READY
21453	21453	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH		READY
21454	21454	Sedan	Seville IV		4	EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	HIGH		READY
21455_swb	21455	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-MPV-SWB-01	HIGH	短轴乘用Bus分支。	READY
21455_lwb	21455	MPV	H-1 I Starex	A1	4	EU-HYUNDAI-H1-I-STAREX-MPV-LWB-01	HIGH	长轴乘用Bus分支。	READY
21464	21464	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH		READY
21465	21465	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH		READY
21466	21466	Coupe	Camaro III	F-body	3	EU-CHEVROLET-CAMARO-III-COUPE-3D-01	HIGH		READY
21467	21467	Coupe	Camaro IV	F-body	3	EU-CHEVROLET-CAMARO-IV-COUPE-3D-01	HIGH		READY
21469	21469	Sedan	Caprice III	B-body	4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH		READY
21472	21472	Convertible	Corvette C4	Y-body	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH		READY
21473	21473	Hatchback	Palio I	178	5	EU-FIAT-PALIO-I-178-HATCHBACK-02	HIGH		READY
21480	21480	Hatchback	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	MEDIUM	Wagon R+第二代五门外廓。	READY
21481	21481	Hatchback	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	MEDIUM	Wagon R+第二代五门外廓。	READY
21494	21494	Sedan	Park Avenue I	C-body	4	EU-BUICK-PARK-AVENUE-I-SEDAN-01	HIGH		READY
21499	21499	Convertible	MX-5 II NB	NB	2	EU-MAZDA-MX5-NB-CONVERTIBLE-PREFL-2D-01	HIGH	NB改款前外廓。	READY
21500	21500	Convertible	MX-5 II NB	NB	2	EU-MAZDA-MX5-NB-CONVERTIBLE-FACELIFT-2D-01	HIGH	NB改款后外廓。	READY
21501	21501	Hatchback	206 Phase I		5	EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	HIGH		READY
21509	21509	Hatchback	2 I DY	DY	5	EU-MAZDA-2-DY-HATCHBACK-5D-01	HIGH		READY
21520_prefl	21520	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH	1996改款前分支。	READY
21520_facelift	21520	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	HIGH	1997改款后分支。	READY
21521	21521	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21522	21522	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21523	21523	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21524	21524	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21525	21525	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21526	21526	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	HIGH		READY
21533	21533	Coupe	Diablo		2	EU-LAMBORGHINI-DIABLO-COUPE-2D-BASE-01	HIGH		READY
21535_swb	21535	MPV	L400	PA3V	4	EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	HIGH	短轴Bus外廓。	READY
21535_lwb	21535	MPV	L400	PB3V	4	EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	HIGH	长轴Bus外廓。	READY
21536_swb	21536	MPV	L400	PA3V	4	EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	HIGH	短轴Bus外廓。	READY
21536_lwb	21536	MPV	L400	PB3V	4	EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	HIGH	长轴Bus外廓。	READY
21543	21543	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-5D-01	HIGH		READY
21544	21544	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-5D-01	HIGH		READY
21545	21545	SUV	Tahoe II	GMT820	5	EU-CHEVROLET-TAHOE-II-GMT820-SUV-5D-01	HIGH		READY
21546	21546	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-I-SUV-5D-01	HIGH		READY
21548	21548	Hatchback	Indica I		5	EU-TATA-INDICA-I-HATCHBACK-01	HIGH		READY
21550	21550	Coupe	V12 Zagato		2	EU-ASTON-MARTIN-V12-ZAGATO-COUPE-2D-01	HIGH		READY
21555_prefl	21555	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-I-T30-SUV-PREFL-01	HIGH	T30改款前分支。	READY
21555_facelift	21555	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-I-T30-SUV-FACELIFT-01	HIGH	T30改款后分支。	READY
21557	21557	SUV	X-Trail I	T30	5	EU-NISSAN-XTRAIL-I-T30-SUV-FACELIFT-01	HIGH		READY
21559	21559	SUV	Terracan I	HP	5	EU-HYUNDAI-TERRACAN-I-SUV-5D-01	HIGH		READY
21561	21561	Hatchback	Jazz I	GD	5	EU-HONDA-JAZZ-I-HATCHBACK-5D-01	MEDIUM	欧洲Jazz代际命名按2002–2008车身归一。	READY
21562	21562	Sedan	Thalia I		4	EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	HIGH		READY
21568	21568	Coupe	CLK C209	C209	2	EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	HIGH		READY
21569	21569	SUV	Cayenne 955	955	5	EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	HIGH		READY
21576	21576	MPV	Espace IV	JK	5	EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	HIGH		READY
21586	21586	Sedan	300C LX	LX	4	EU-CHRYSLER-300C-LX-SRT8-SEDAN-4D-01	HIGH		READY
21587	21587	SUV	FX I	S50	5	EU-INFINITI-FX-I-S50-SUV-5D-01	HIGH		READY
21589	21589	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH		READY
21591	21591	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH		READY
21592	21592	SUV	Compass I	MK	5	EU-JEEP-COMPASS-I-MK-SUV-01	HIGH		READY
21593_l1h1	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	HIGH	L1H1封闭式货厢。	READY
21593_l1h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	HIGH	L1H2封闭式货厢。	READY
21593_l2h1	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	HIGH	L2H1封闭式货厢。	READY
21593_l2h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	HIGH	L2H2封闭式货厢。	READY
21593_l3h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	HIGH	L3H2封闭式货厢。	READY
21593_l3h3	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	HIGH	L3H3封闭式货厢。	READY
21593_l4h2	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	HIGH	L4H2封闭式货厢。	READY
21593_l4h3	21593	Van	Boxer II	X250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	HIGH	L4H3封闭式货厢。	READY
21594_l1	21594	Pickup	Boxer II	X250		EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	HIGH	L1底盘驾驶室。	READY
21594_l2	21594	Pickup	Boxer II	X250		EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	HIGH	L2底盘驾驶室。	READY
21594_l3	21594	Pickup	Boxer II	X250		EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	HIGH	L3底盘驾驶室。	READY
21594_l4	21594	Pickup	Boxer II	X250		EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	HIGH	L4底盘驾驶室。	READY
21641	21641	Convertible	Allanté I		2	EU-CADILLAC-ALLANTE-I-CONVERTIBLE-2D-01	HIGH		READY
21642	21642	Convertible	Allanté I		2	EU-CADILLAC-ALLANTE-I-CONVERTIBLE-2D-01	HIGH		READY
21643	21643	Coupe	Allanté I		2	EU-CADILLAC-ALLANTE-I-CONVERTIBLE-2D-01	MEDIUM	可拆硬顶安装状态不改变基础外廓。	READY
21644	21644	Coupe	Allanté I		2	EU-CADILLAC-ALLANTE-I-CONVERTIBLE-2D-01	MEDIUM	可拆硬顶安装状态不改变基础外廓。	READY
21691	21691	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
21709	21709	Sedan	Mondeo I	GBP	4	EU-FORD-MONDEO-I-SEDAN-4D-01	HIGH		READY
21714	21714	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	第一代标准长度Cargo Van。	READY
21717_swb	21717	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度乘用Van。	READY
21717_lwb	21717	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended乘用Van。	READY
21718_swb	21718	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度乘用Van。	READY
21718_lwb	21718	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended乘用Van。	READY
21719_swb	21719	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度乘用Van。	READY
21719_lwb	21719	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended乘用Van。	READY
21720_swb	21720	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度乘用Van。	READY
21720_lwb	21720	MPV	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended乘用Van。	READY
21721_swb	21721	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度Cargo Van。	READY
21721_lwb	21721	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended Cargo Van。	READY
21722_swb	21722	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度Cargo Van。	READY
21722_lwb	21722	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended Cargo Van。	READY
21723_swb	21723	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-SWB-01	HIGH	标准长度Cargo Van。	READY
21723_lwb	21723	Van	Astro I	M-body	3	EU-CHEVROLET-ASTRO-I-VAN-LWB-01	HIGH	Extended Cargo Van。	READY
21726	21726	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-VAN-LWB-01	HIGH	第二代Extended Cargo Van。	READY
21727	21727	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-VAN-LWB-01	HIGH	第二代Extended Cargo Van。	READY
21728	21728	Van	Astro II	M-body	3	EU-CHEVROLET-ASTRO-II-VAN-LWB-01	HIGH	第二代Extended Cargo Van。	READY
21750_2dr	21750	Convertible	Wrangler III JK	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-01	HIGH	两门开放式车身。	READY
21750_4dr	21750	Convertible	Wrangler III JK	JK	4	EU-JEEP-WRANGLER-III-JK-SUV-4D-01	HIGH	四门Unlimited开放式车身。	READY
21757	21757	Convertible	Beat	PP1	2	EU-HONDA-BEAT-PP1-CONVERTIBLE-2D-01	HIGH		READY
21760	21760	SUV	Terios II	J200	5	EU-DAIHATSU-TERIOS-II-J200-SUV-01	HIGH		READY
21786_regcab_swb	21786	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-SWB-01	MEDIUM	Regular Cab短货斗。	READY
21786_regcab_lwb	21786	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-LWB-01	MEDIUM	Regular Cab长货斗。	READY
21786_extcab_swb	21786	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-SWB-01	MEDIUM	Extended Cab短货斗。	READY
21786_extcab_lwb	21786	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-LWB-01	MEDIUM	Extended Cab长货斗。	READY
21788_regcab_swb	21788	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-SWB-01	MEDIUM	Regular Cab短货斗。	READY
21788_regcab_lwb	21788	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-LWB-01	MEDIUM	Regular Cab长货斗。	READY
21788_extcab_swb	21788	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-SWB-01	MEDIUM	Extended Cab短货斗。	READY
21788_extcab_lwb	21788	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-LWB-01	MEDIUM	Extended Cab长货斗。	READY
21789_regcab_lwb	21789	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-LWB-01	MEDIUM	柴油Regular Cab长货斗。	READY
21789_extcab_lwb	21789	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-LWB-01	MEDIUM	柴油Extended Cab长货斗。	READY
21796_regcab_lwb	21796	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C2500-GMT400-PICKUP-REGCAB-LWB-01	MEDIUM	C2500柴油Regular Cab长货斗。	READY
21796_extcab_lwb	21796	Pickup	C/K GMT400	GMT400		EU-CHEVROLET-C2500-GMT400-PICKUP-EXTCAB-LWB-01	MEDIUM	C2500柴油Extended Cab长货斗。	READY
21803	21803	Wagon	Leon III ST	5F	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
21804	21804	Wagon	Leon III ST	5F	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
21805	21805	Wagon	Leon III ST	5F	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
21821	21821	Wagon	Caprice IV	B-body	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21822	21822	Wagon	Caprice IV	B-body	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21823	21823	Wagon	Caprice IV	B-body	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21824	21824	Wagon	Caprice IV	B-body	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21825_prefl	21825	Sedan	Caprice IV	B-body	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH	第四代改款前Sedan。	READY
21825_facelift	21825	Sedan	Caprice IV	B-body	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	HIGH	第四代改款后Sedan。	READY
21826	21826	Sedan	Caprice IV	B-body	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1101-1200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4f-c6-3.2-fsi-v6-255hp-quattro-tiptronic-4661
EU-MITSUBISHI-L300-III-BUS-SWB-01	4275	1695	1835	AutoEvolution Mitsubishi L300 specifications	https://www.autoevolution.com/cars/mitsubishi-l300-1993.html
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279	Auto-Data.net	https://www.auto-data.net/en/jaguar-xjs-model-40
EU-JAGUAR-XJSC-CONVERTIBLE-2D-01	4820	1793	1279	Auto-Data.net	https://www.auto-data.net/en/jaguar-xjsc-convertible-4.0-226hp-260
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-lancer-v-1.3-75hp-15664
EU-AUDI-A6-C4-SEDAN-4D-01	4797	1783	1430	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4a-c4-2.0-115hp-4748
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-2D-01	4260	1630	1290	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-spider-115-2000-veloce-126hp-1458
EU-TOYOTA-SUPRA-A70-COUPE-3D-01	4620	1745	1310	Auto-Data.net	https://www.auto-data.net/en/toyota-supra-iii-a70-3.0-24v-190hp-3456
EU-PEUGEOT-405-I-BREAK-WAGON-5D-01	4398	1714	1445	Auto-Data.net	https://www.auto-data.net/en/peugeot-405-i-break-15e-1.9-95hp-5608
EU-BMW-6-SERIES-E24-COUPE-PREFL-2D-01	4755	1725	1365	Auto-Data.net	https://www.auto-data.net/en/bmw-6-series-e24-facelift-1982-635csi-218hp-9854
EU-BMW-6-SERIES-E24-COUPE-FACELIFT-2D-01	4815	1725	1365	Auto-Data.net	https://www.auto-data.net/en/bmw-6-series-e24-facelift-1987-635csi-211hp-automatic-cat-28434
EU-MASERATI-BITURBO-COUPE-2D-01	4153	1714	1305	Auto-Data.net	https://www.auto-data.net/en/maserati-biturbo-coupe-generation-2235
EU-MITSUBISHI-LANCER-EVOLUTION-IX-SEDAN-4D-01	4490	1770	1450	Auto-Data.net	https://www.auto-data.net/en/mitsubishi-lancer-evolution-ix-2.0-mivec-280hp-4wd-15649
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104	Car.info Fiat Ducato II Typ 230	https://www.car.info/en-se/fiat/ducato/ii-typ-230-10065188
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150	Car.info Fiat Ducato II Typ 230	https://www.car.info/en-se/fiat/ducato/ii-typ-230-10065188
EU-FORD-USA-MUSTANG-IV-FACELIFT-COUPE-2D-01	4661	1857	1359	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-model-1265
EU-FORD-USA-MUSTANG-IV-FACELIFT-CONVERTIBLE-2D-01	4653	1857	1350	Auto-Data.net	https://www.auto-data.net/en/ford-mustang-model-1265
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870	Auto-Data.net	https://www.auto-data.net/en/peugeot-partner-model-1791
EU-CHEVROLET-LUMINA-APV-MPV-01	4844	1877	1669	Auto-Data.net	https://www.auto-data.net/en/chevrolet-lumina-apv-3.8-i-175hp-14476
EU-BUICK-SKYLARK-VII-SEDAN-4D-01	4803	1715	1351	Automobile-Catalog Buick Skylark	https://www.automobile-catalog.com/model/buick/skylark_7gen.html
EU-CADILLAC-SEVILLE-IV-SEDAN-4D-01	4846	1829	1351	Automobile-Catalog Cadillac Seville	https://www.automobile-catalog.com/model/cadillac/seville_4gen.html
EU-HYUNDAI-H1-I-STAREX-MPV-SWB-01	4695	1820	1885	Auto-Data.net	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.4-i-16v-4wd-swb-135hp-13850
EU-HYUNDAI-H1-I-STAREX-MPV-LWB-01	5035	1820	1965	Auto-Data.net	https://www.auto-data.net/en/hyundai-h-1-i-starex-2.4-i-16v-lwb-135hp-13851
EU-CHEVROLET-CAMARO-III-COUPE-3D-01	4877	1849	1278	Automobile-Catalog Chevrolet Camaro III	https://www.automobile-catalog.com/model/chevrolet/camaro_3gen.html
EU-CHEVROLET-CAMARO-IV-COUPE-3D-01	4907	1882	1303	Auto-Data.net	https://www.auto-data.net/en/chevrolet-camaro-iv-3.8-i-v6-200hp-automatic-24903
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420	Automobile-Catalog Chevrolet Caprice III	https://www.automobile-catalog.com/model/chevrolet/caprice_3gen.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201	Automobile-Catalog Chevrolet Corvette C4	https://www.automobile-catalog.com/model/chevrolet/corvette_c4.html
EU-FIAT-PALIO-I-178-HATCHBACK-02	3735	1626	1446	Auto-Data.net	https://www.auto-data.net/en/fiat-palio-178-1.2-i-68hp-6854
EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	3500	1600	1660	Auto-Data.net	https://www.auto-data.net/en/suzuki-wagon-r-model-2050
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400	Automobile-Catalog Buick Park Avenue	https://www.automobile-catalog.com/model/buick/park_avenue_1gen.html
EU-MAZDA-MX5-NB-CONVERTIBLE-PREFL-2D-01	3975	1680	1225	Auto-Data.net	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8-i-16v-140hp-11259
EU-MAZDA-MX5-NB-CONVERTIBLE-FACELIFT-2D-01	3975	1680	1220	Auto-Data.net	https://www.auto-data.net/en/mazda-mx-5-ii-nb-1.8i-16v-146hp-11260
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426	Auto-Data.net	https://www.auto-data.net/en/peugeot-206-model-1794
EU-MAZDA-2-DY-HATCHBACK-5D-01	3925	1680	1545	Auto-Data.net	https://www.auto-data.net/en/mazda-2-i-dy-1.6-i-16v-101hp-11454
EU-JEEP-CHEROKEE-XJ-SUV-5D-PREFL-01	4240	1790	1700	Automobile-Catalog Jeep Cherokee XJ	https://www.automobile-catalog.com/model/jeep/cherokee_xj.html
EU-JEEP-CHEROKEE-XJ-SUV-5D-FACELIFT-01	4251	1790	1625	Automobile-Catalog Jeep Cherokee XJ	https://www.automobile-catalog.com/model/jeep/cherokee_xj.html
EU-LAMBORGHINI-DIABLO-COUPE-2D-BASE-01	4460	2040	1105	Auto-Data.net	https://www.auto-data.net/en/lamborghini-diablo-vt-492hp-3091
EU-MITSUBISHI-L400-PA3V-VAN-SWB-01	4595	1695	1855	Auto-Data.net Mitsubishi Delica L400	https://www.auto-data.net/en/mitsubishi-delica-l400-generation-3389
EU-MITSUBISHI-L400-PB3V-VAN-LWB-01	4995	1695	1960	Auto-Data.net Mitsubishi Delica L400	https://www.auto-data.net/en/mitsubishi-delica-l400-generation-3389
EU-CHEVROLET-TAHOE-II-GMT820-SUV-5D-01	5052	2004	1885	Auto-Data.net	https://www.auto-data.net/en/chevrolet-tahoe-gmt820-5.3-i-v8-288hp-14326
EU-MAZDA-TRIBUTE-I-SUV-5D-01	4395	1825	1765	Auto-Data.net	https://www.auto-data.net/en/mazda-tribute-generation-2410
EU-TATA-INDICA-I-HATCHBACK-01	3660	1625	1485	Auto-Data.net	https://www.auto-data.net/en/tata-indica-model-2143
EU-ASTON-MARTIN-V12-ZAGATO-COUPE-2D-01	4385	1865	1250	Auto-Data.net	https://www.auto-data.net/en/aston-martin-v12-zagato-6.0-v12-517hp-24284
EU-NISSAN-XTRAIL-I-T30-SUV-PREFL-01	4510	1765	1675	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-i-t30-2.0-140hp-4x4-912
EU-NISSAN-XTRAIL-I-T30-SUV-FACELIFT-01	4455	1765	1675	Auto-Data.net	https://www.auto-data.net/en/nissan-x-trail-i-t30-facelift-2003-2.2-dci-136hp-4x4-29975
EU-HYUNDAI-TERRACAN-I-SUV-5D-01	4710	1860	1790	Auto-Data.net	https://www.auto-data.net/en/hyundai-terracan-2.5-td-100hp-13885
EU-HONDA-JAZZ-I-HATCHBACK-5D-01	3830	1675	1525	Auto-Data.net	https://www.auto-data.net/en/honda-jazz-i-generation-2588
EU-RENAULT-THALIA-I-FACELIFT-SEDAN-01	4171	1639	1437	Auto-Data.net	https://www.auto-data.net/en/renault-thalia-model-1874
EU-MERCEDES-BENZ-CLK-C209-FACELIFT-COUPE-2D-01	4652	1740	1413	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-clk-c209-facelift-2005-generation-1669
EU-PORSCHE-CAYENNE-955-SUV-STANDARD-01	4782	1928	1699	Auto-Data.net	https://www.auto-data.net/en/porsche-cayenne-955-3.2i-v6-250hp-6722
EU-RENAULT-ESPACE-IV-PHASE-II-MPV-01	4656	1860	1728	Auto-Data.net	https://www.auto-data.net/en/renault-espace-iv-generation-2933
EU-CHRYSLER-300C-LX-SRT8-SEDAN-4D-01	4999	1882	1471	Auto-Data.net	https://www.auto-data.net/en/chrysler-300-6.1-i-v8-16v-srt-8-425hp-14690
EU-INFINITI-FX-I-S50-SUV-5D-01	4803	1925	1651	Auto-Data.net	https://www.auto-data.net/en/infiniti-fx-i-35-v6-24v-283hp-13995
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737	Auto-Data.net	https://www.auto-data.net/en/audi-q7-model-838
EU-JEEP-COMPASS-I-MK-SUV-01	4405	1810	1630	Auto-Data.net	https://www.auto-data.net/en/jeep-compass-model-1377
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270	Peugeot Boxer official specification sheet	https://www.peugeot.ie/content/dam/peugeot/ireland/spec-sheets/boxer-spec-sheet.pdf
EU-CADILLAC-ALLANTE-I-CONVERTIBLE-2D-01	4540	1865	1310	Auto-Data.net	https://www.auto-data.net/en/cadillac-allante-4.5-i-v8-204hp-11675
EU-BMW-X5-F15-SUV-01	4886	1938	1762	Auto-Data.net	https://www.auto-data.net/en/bmw-x5-f15-generation-4151
EU-FORD-MONDEO-I-SEDAN-4D-01	4481	1749	1424	EncyCARpedia	https://www.encycarpedia.com/ford/93-mondeo-2-0i-saloon
EU-CHEVROLET-ASTRO-I-VAN-SWB-01	4519	1956	1935	Chevrolet 1994 Astro official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-I-VAN-LWB-01	4773	1969	1935	Chevrolet 1994 Astro official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1994-Chevrolet-Astro-Van.pdf
EU-CHEVROLET-ASTRO-II-VAN-LWB-01	4821	1969	1905	Edmunds 2005 Chevrolet Astro Cargo specifications	https://www.edmunds.com/chevrolet/astro-cargo/2005/features-specs/
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-model-1380
EU-JEEP-WRANGLER-III-JK-SUV-4D-01	4751	1877	1834	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-model-1380
EU-HONDA-BEAT-PP1-CONVERTIBLE-2D-01	3295	1395	1175	AutoZine Honda Beat archive	https://www.autozine.org/Archive/Honda/classic/Beat.html
EU-DAIHATSU-TERIOS-II-J200-SUV-01	4055	1695	1740	Auto-Data.net	https://www.auto-data.net/en/daihatsu-terios-model-1180
EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-SWB-01	4940	1951	1778	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-CHEVROLET-C1500-GMT400-PICKUP-REGCAB-LWB-01	5413	1951	1778	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-SWB-01	5550	1951	1875	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-CHEVROLET-C1500-GMT400-PICKUP-EXTCAB-LWB-01	6030	1951	1875	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-CHEVROLET-C2500-GMT400-PICKUP-REGCAB-LWB-01	5413	1951	1849	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-CHEVROLET-C2500-GMT400-PICKUP-EXTCAB-LWB-01	6030	1951	1875	Chevrolet Silverado 1996 official brochure	https://www.auto-brochures.com/makes/Chevrolet/Silverado/Chevrolet_US%20Silverado_1996.pdf
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data.net	https://www.auto-data.net/en/seat-leon-iii-st-generation-4416
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547	Automobile-Catalog Chevrolet Caprice IV	https://www.automobile-catalog.com/model/chevrolet/caprice_4gen.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440	Automobile-Catalog Chevrolet Caprice IV	https://www.automobile-catalog.com/model/chevrolet/caprice_4gen.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415	Automobile-Catalog Chevrolet Caprice IV	https://www.automobile-catalog.com/model/chevrolet/caprice_4gen.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1101-1200_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5419 行）
- 累计尺寸组：dimension_groups_final.tsv（2343 行）

