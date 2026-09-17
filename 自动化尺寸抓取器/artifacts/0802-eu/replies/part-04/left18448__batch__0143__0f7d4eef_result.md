# 任务：left18448 第 14201-14300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0143__0f7d4eef


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 14201-14300 行

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
left18448.tsv

【当前独立任务】
left18448 第 14201-14300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Renault	Master iii	2.3 DCI 125 FWD	Bus	Frontantrieb	Diesel	Feb 2011	Jun 2019	11038
Renault	Master iii	2.3 DCI 130 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2015	Dec 2020	802204
Renault	Master iii	2.3 DCI 130 4X4	Kasten	Allrad	Diesel	Jun 2016	Dec 2020	802205
Renault	Master iii	2.3 DCI 130 FWD	Kasten	Frontantrieb	Diesel	Jun 2016	Dec 2020	121779
Renault	Master iii	2.3 DCI 130 RWD	Kasten	Heckantrieb	Diesel	Jun 2016	Dec 2020	118804
Renault	Master iii	2.3 DCI 135 4X4	Kasten	Allrad	Diesel	Jul 2014	Jun 2019	802202
Renault	Master iii	2.3 DCI 135 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2014	Jun 2019	802203
Renault	Master iii	2.3 DCI 135 FWD	Bus	Frontantrieb	Diesel	Jul 2014	Dec 2024	108154
Renault	Master iii	2.3 DCI 135 FWD	Kasten	Frontantrieb	Diesel	Jul 2014	Dec 2025	108252
Renault	Master iii	2.3 DCI 135 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2014	Dec 2024	123447
Renault	Master iii	2.3 DCI 135 RWD	Kasten	Heckantrieb	Diesel	Jul 2014	Jun 2019	108153
Renault	Master iii	2.3 DCI 135 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2014	Jun 2019	108177
Renault	Master iii	2.3 DCI 145 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2015	Dec 2024	155738
Renault	Master iii	2.3 DCI 145 4X4	Kasten	Allrad	Diesel	Jul 2015	Dec 2024	155740
Renault	Master iii	2.3 DCI 145 FWD	Bus	Frontantrieb	Diesel	Feb 2011	Dec 2024	11043
Renault	Master iii	2.3 DCI 150 FWD	Kasten	Frontantrieb	Diesel	Mar 2013	-	58900
Renault	Master iii	2.3 DCI 150 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 2013	-	58903
Renault	Master iii	2.3 DCI 150 FWD	Bus	Frontantrieb	Diesel	Oct 2012	-	59333
Renault	Master iii	2.3 DCI 150 RWD	Kasten	Heckantrieb	Diesel	Mar 2013	Jun 2019	58901
Renault	Master iii	2.3 DCI 150 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Mar 2013	Jun 2019	58904
Renault	Master iii	2.3 DCI 165 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 2014	Dec 2024	155737
Renault	Master iii	2.3 DCI 165 4X4	Kasten	Allrad	Diesel	Jul 2014	Dec 2024	155739
Renault	Master iii	2.3 DCI 165 FWD	Bus	Frontantrieb	Diesel	Jul 2014	Dec 2024	108152
Renault	Master iii	2.3 DCI 165 FWD	Kasten	Frontantrieb	Diesel	Jul 2014	Dec 2024	108253
Renault	Master iii	2.3 DCI 165 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2014	Dec 2024	118600
Renault	Master iii	2.3 DCI 165 RWD	Kasten	Heckantrieb	Diesel	Jul 2014	Dec 2024	108151
Renault	Master iii	2.3 DCI 165 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	Jul 2014	Dec 2024	108178
Renault	Master iii	2.3 DCI 170 FWD	Bus	Frontantrieb	Diesel	Jul 2015	Dec 2020	116478
Renault	Master iii	2.3 DCI 170 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2016	Dec 2020	121778
Renault	Master iii	2.3 DCI 170 FWD	Kasten	Frontantrieb	Diesel	Jul 2015	Dec 2020	122129
Renault	Master iv	Blue DCI 105	Kasten	Frontantrieb	Diesel	Jun 2024	-	158677
Renault	Master iv	Blue DCI 130	Kasten	Frontantrieb	Diesel	Jun 2024	-	158678
Renault	Master iv	Blue DCI 130 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2024	-	800191
Renault	Master iv	Blue DCI 150	Kasten	Frontantrieb	Diesel	Jun 2024	-	158679
Renault	Master iv	Blue DCI 150	Bus	Frontantrieb	Diesel	Jun 2024	-	800194
Renault	Master iv	Blue DCI 150 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2024	-	800192
Renault	Master iv	Blue DCI 150 Heckantrieb	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2025	-	802362
Renault	Master iv	Blue DCI 170	Kasten	Frontantrieb	Diesel	Jun 2024	-	158680
Renault	Master iv	Blue DCI 170 Frontantrieb	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2024	-	800193
Renault	Master iv	Blue DCI 170 Heckantrieb	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2025	-	802363
Renault	Master iv	E-tech Electric	Kasten	Frontantrieb	Elektro	Sep 2024	-	800282
Renault	Master iv	E-tech Electric	Kasten	Frontantrieb	Elektro	Sep 2024	-	800283
Renault	Master iv	E-tech Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2024	-	800956
Renault	Master iv	E-tech Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	Nov 2024	-	800957
Renault	Megane cc	1.2 TCE	Cabriolet	Frontantrieb	Benzin	Jan 2013	Aug 2015	59338
Renault	Megane cc	1.6 16V Hi-flex	Cabriolet	Frontantrieb	Benzin/Ethanol	Jun 2010	Aug 2015	128492
Renault	Megane cc	1.6 DCI	Cabriolet	Frontantrieb	Diesel	Apr 2011	Aug 2015	15234
Renault	Megane e-Tech	Ev40	SUV	Frontantrieb	Elektro	Nov 2021	-	145693
Renault	Megane e-Tech	Ev60	SUV	Frontantrieb	Elektro	Nov 2021	-	145694
Renault	Megane e-Tech	Ev60	SUV	Frontantrieb	Elektro	Nov 2021	-	801426
Renault	Megane i	2	Schrägheck	Frontantrieb	Benzin	May 1998	May 2001	100432
Renault	Megane i	1.4 16V	Schrägheck	Frontantrieb	Benzin	Mar 1999	Aug 2003	11487
Renault	Megane i	1.4 16V	Cabriolet	Frontantrieb	Benzin	Mar 1999	Aug 2003	11494
Renault	Megane i	1.6 16V	Schrägheck	Frontantrieb	Benzin	Mar 1999	Aug 2002	11485
Renault	Megane i	1.6 16V	Cabriolet	Frontantrieb	Benzin	Mar 1999	Jul 2003	11490
Renault	Megane i	1.6 E	Cabriolet	Frontantrieb	Benzin	Oct 1996	Mar 1999	7881
Renault	Megane i	1.9 DCI	Schrägheck	Frontantrieb	Diesel	Feb 2001	Aug 2003	15761
Renault	Megane i	1.9 DTI	Schrägheck	Frontantrieb	Diesel	Feb 2001	Aug 2003	15766
Renault	Megane i	1.9 TDI	Schrägheck	Frontantrieb	Diesel	Sep 1996	Aug 2003	7884
Renault	Megane i	2.0 16V	Cabriolet	Frontantrieb	Benzin	Oct 1996	Nov 1999	7882
Renault	Megane i	2.0 16V	Schrägheck	Frontantrieb	Benzin	Jul 1996	Aug 2003	7883
Renault	Megane i	2.0 16V	Cabriolet	Frontantrieb	Benzin	Jan 2002	Aug 2003	16578
Renault	Megane i	2.0 16V IDE	Cabriolet	Frontantrieb	Benzin	Nov 1999	Aug 2003	14166
Renault	Megane i	2.0 I	Cabriolet	Frontantrieb	Benzin	Mar 1999	Aug 2003	11492
Renault	Megane i	2.0 I	Schrägheck	Frontantrieb	Benzin	Mar 1999	Aug 2003	11493
Renault	Megane i classic	1.6	Stufenheck	Frontantrieb	Benzin	Feb 2000	Sep 2000	58075
Renault	Megane i classic	2	Stufenheck	Frontantrieb	Benzin	May 1998	May 2001	100433
Renault	Megane i classic	1.4 16V	Stufenheck	Frontantrieb	Benzin	Mar 1999	Aug 2003	11488
Renault	Megane i classic	1.6 16V	Stufenheck	Frontantrieb	Benzin	Mar 1999	Jul 2003	11489
Renault	Megane i classic	1.9 DCI	Stufenheck	Frontantrieb	Diesel	Feb 2001	Aug 2003	15763
Renault	Megane i classic	1.9 DTI	Stufenheck	Frontantrieb	Diesel	Feb 2001	Aug 2003	15767
Renault	Megane i classic	2.0 I	Stufenheck	Frontantrieb	Benzin	Mar 1999	Aug 2003	11481
Renault	Megane i classic	2.0 RT	Stufenheck	Frontantrieb	Benzin	Mar 2001	Aug 2003	56041
Renault	Megane i coach	1.4 16V	Coupe	Frontantrieb	Benzin	Mar 1999	Jul 2003	11486
Renault	Megane i coach	1.6 16V	Coupe	Frontantrieb	Benzin	Mar 1999	Jul 2003	11484
Renault	Megane i coach	1.9 DCI	Coupe	Frontantrieb	Diesel	Feb 2001	Aug 2003	15765
Renault	Megane i coach	2.0 16V	Coupe	Frontantrieb	Benzin	Jan 2002	Aug 2003	16577
Renault	Megane i coach	2.0 16V IDE	Coupe	Frontantrieb	Benzin	Nov 1999	Aug 2003	14165
Renault	Megane i coach	2.0 I	Coupe	Frontantrieb	Benzin	Mar 1999	Aug 2003	11483
Renault	Megane i grandtour	1.4 16V	Kombi	Frontantrieb	Benzin	Mar 1999	Aug 2003	11479
Renault	Megane i grandtour	1.4 E	Kombi	Frontantrieb	Benzin	Mar 1999	Aug 2003	11264
Renault	Megane i grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	Mar 1999	Aug 2003	11480
Renault	Megane i grandtour	1.6 E	Kombi	Frontantrieb	Benzin	Mar 1999	Aug 2003	11265
Renault	Megane i grandtour	1.9 D	Kombi	Frontantrieb	Diesel	Apr 1999	Aug 2003	11266
Renault	Megane i grandtour	1.9 DCI	Kombi	Frontantrieb	Diesel	Feb 2001	Aug 2003	15764
Renault	Megane i grandtour	1.9 DTI	Kombi	Frontantrieb	Diesel	Mar 1999	Feb 2001	11267
Renault	Megane i grandtour	1.9 DTI	Kombi	Frontantrieb	Diesel	Feb 2001	Aug 2003	15768
Renault	Megane ii	1.4	Stufenheck	Frontantrieb	Benzin	Sep 2003	-	17724
Renault	Megane ii	1.4	Stufenheck	Frontantrieb	Benzin	Sep 2003	-	17725
Renault	Megane ii	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2003	-	17726
Renault	Megane ii	2	Stufenheck	Frontantrieb	Benzin	Sep 2003	-	17727
Renault	Megane ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Nov 2002	Feb 2008	16916
Renault	Megane ii	1.4 16V	Schrägheck	Frontantrieb	Benzin	Oct 2003	Feb 2008	17719
Renault	Megane ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Sep 2002	Feb 2008	16919
Renault	Megane ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	Oct 2003	Feb 2008	17718
Renault	Megane ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	Aug 2003	Dec 2010	17728
Renault	Megane ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	Feb 2004	Dec 2010	18219
Renault	Megane ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	May 2005	Dec 2010	18784
Renault	Megane ii	1.5 DCI	Stufenheck	Frontantrieb	Diesel	May 2005	Dec 2010	18785
Renault	Megane ii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	May 2005	Feb 2008	18790


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Mégane E-Tech Electric** 3 个 Ktype，共用 1 个尺寸组；官方规格确认车长 4200 mm、车身宽度 1768 mm（不含后视镜）、高度 1505 mm。
* 已完成 **Mégane I** Hatchback、Cabriolet、Classic、Coach、Grandtour 的 Phase I／Phase II 外廓划分。改款前后尺寸发生变化的 Ktype 已拆分为 `prefl` 和 `facelift` 派生行。([汽车数据网][1])
* 本轮新增 45 条 READY 映射，首次创建并闭合 9 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：40
* READY 映射：45
* 待处理输入 Ktype：60
* 已确认尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145693	145693	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
145694	145694	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
801426	801426	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
100432_prefl	100432	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
100432_facelift	100432	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
11487	11487	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
11494	11494	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11485	11485	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
11490	11490	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
7881	7881	Convertible	Megane I Phase I	EA	2	EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	MEDIUM	生产终点位于1999改款交界月。	READY
15761	15761	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
15766	15766	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
7884_prefl	7884	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7884_facelift	7884	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
7882_prefl	7882	Convertible	Megane I Phase I	EA	2	EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7882_facelift	7882	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
7883_prefl	7883	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7883_facelift	7883	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
16578	16578	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
14166	14166	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11492	11492	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11493	11493	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58075	58075	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
100433_prefl	100433	Sedan	Megane I Phase I	LA	4	EU-RENAULT-MEGANE-I-PHASE-I-SEDAN-4D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
100433_facelift	100433	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
11488	11488	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11489	11489	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
15763	15763	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
15767	15767	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11481	11481	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
56041	56041	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11486	11486	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11484	11484	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
15765	15765	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
16577	16577	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
14165	14165	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11483	11483	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11479	11479	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11264	11264	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11480	11480	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11265	11265	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11266	11266	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
15764	15764	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11267	11267	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
15768	15768	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	4200	1768	1505	Renault Suisse Megane E-Tech Electric official price/spec sheet	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Megane_E-Tech_Electric_PL_d.pdf
EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	4129	1699	1420	Auto-Data Renault Megane I (BA)	https://www.auto-data.net/en/renault-megane-i-ba-generation-2152
EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	4164	1698	1420	Auto-Data Renault Megane I Phase II	https://www.auto-data.net/en/renault-megane-i-phase-ii-1999-generation-5577
EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	4082	1698	1368	Auto-Data Renault Megane I Cabriolet Phase II	https://www.auto-data.net/en/renault-megane-i-cabriolet-phase-ii-1999-generation-5579
EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	4028	1698	1368	Auto-Data Renault Megane I Cabriolet (EA)	https://www.auto-data.net/en/renault-megane-i-cabriolet-ea-generation-2156
EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	4436	1698	1420	Auto-Data Renault Megane I Classic Phase II	https://www.auto-data.net/en/renault-megane-i-classic-phase-ii-1999-generation-5584
EU-RENAULT-MEGANE-I-PHASE-I-SEDAN-4D-01	4440	1699	1420	Auto-Data Renault Megane I Classic (LA)	https://www.auto-data.net/en/renault-megane-i-classic-la-generation-2153
EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	3967	1698	1366	Auto-Data Renault Megane I Coach Phase II	https://www.auto-data.net/en/renault-megane-i-coach-phase-ii-1999-generation-5576
EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-generation-5586
```

## 下一步优先处理

1. 闭合 Mégane II Sedan/Hatchback 的 3门、5门及 2006 年改款前后分支。
2. 处理 Mégane CC 的 Phase I、Phase II、Phase III 外廓边界。
3. 按聚类批量处理 Master III/IV：先 Kasten 和 Bus 的轴距/车顶组合，再处理 Pritsche/Fahrgestell 的 FWD、RWD、4×4 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-megane-i-ba-generation-2152 "Renault Megane I (BA) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Mégane III CC 的 3 个 Ktype，共用同一 Coupé-Cabriolet 外廓；尺寸为 4485 × 1811 × 1434 mm。([resource.digitaldealer.com.au][1])
* 闭合 Mégane II Sedan 的 8 个 Ktype，以及 Hatchback 3门、5门的 5 个 Ktype。16916、16919 对应 CM 三门车身；17718 与 18790 已确认属于五门车身。([cesaranoricambi.it][2])
* Mégane II 三门、五门和 Sedan 分别建组；2006 年改款没有造成这批车身三维变化，因此不创建重复改款尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：56
* READY 映射：61
* PENDING 输入 Ktype：44
* 已确认尺寸组：13
* 剩余记录全部为 Renault Master III／IV。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59338	59338	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
128492	128492	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
15234	15234	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
17724	17724	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17725	17725	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17726	17726	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17727	17727	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
16916	16916	Hatchback	Megane II	CM	3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH		READY
17719	17719	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
16919	16919	Hatchback	Megane II	CM	3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH		READY
17718	17718	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
17728	17728	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18219	18219	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18784	18784	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18785	18785	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18790	18790	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	4485	1811	1434	Renault Megane Coupe-Cabriolet official brochure; Auto-Data Renault Megane III CC	https://resource.digitaldealer.com.au/pdf/5444430215615c3e7030a1039769581.pdf;https://www.auto-data.net/en/renault-megane-iii-cc-generation-3773
EU-RENAULT-MEGANE-II-SEDAN-4D-01	4498	1777	1460	Automobile-Catalog Renault Megane Classic 2.0 16V; Auto-Data Renault Megane II Classic	https://www.automobile-catalog.com/car/2007/2954600/renault_megane_classic_2_0_16v.html;https://www.auto-data.net/en/renault-megane-ii-classic-1.5-dci-106hp-10543
EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	4209	1777	1457	Renault Drive.Place Megane II 3-door	https://renault.drive.place/megane/ii/group_hatchback_3d/245016
EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	4209	1777	1458	Automobile-Catalog Renault Megane 1.5 dCi 80; Carfolio Renault Megane II Hatchback 1.6 16V	https://www.automobile-catalog.com/car/2002/2953670/renault_megane_1_5_dci_80.html;https://www.carfolio.com/renault-megane-ii-hatchback-1.6-16v-96899
```

## 下一步优先处理

1. 先闭合 Master IV Kasten、Bus 的 L2H2／L3H2 外廓并批量关联柴油和电动 Ktype。
2. 再处理 Master IV Pritsche/Fahrgestell 的 FWD、RWD 和轴距分支。
3. 最后按 Master III 的 Bus、Kasten、Pritsche/Fahrgestell，集中拆分轴距、车顶高度和前后驱外廓。

推进信号：CONTINUE

[1]: https://resource.digitaldealer.com.au/pdf/5444430215615c3e7030a1039769581.pdf?utm_source=chatgpt.com "RENAULT
MEGANE
COUPE-CABRIOLET
DRIVE THE CHANGE"
[2]: https://cesaranoricambi.it/it/14-16v-ber-3p-b-1390cc/331694-porta-ant-sx-027-renault-megane-2a-serie-09-02-02-06-k4jd7-7751474349.html?utm_source=chatgpt.com "PORTA ANT. SX. 027 RENAULT MEGANE 2A SERIE (09/02-02/06 ..."
[3]: https://www.auto-data.net/en/renault-megane-ii-phase-ii-2006-1.5-dci-106hp-30418?utm_source=chatgpt.com "Renault Megane II (Phase II, 2006) 1.5 dCi (106 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Master IV `Kasten` 的 L2H2、L3H2、L3H3 三种外廓，6 个柴油／电动 Ktype 直接复用这 3 个尺寸组。
* 已确认 Master IV `Bus` Ktype `800194` 对应 L3H3 乘员运输车身。尺寸口径统一采用 2080 mm 不含后视镜宽度；长度和高度采用 Renault 官方车型尺寸。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：63
* READY 映射：80
* PENDING 输入 Ktype：37
* 已确认尺寸组：17
* 剩余：Master IV `Pritsche/Fahrgestell` 7 个 Ktype、Master III 30 个 Ktype。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
158677_l2h2	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158677_l3h2	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158677_l3h3	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
158678_l2h2	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158678_l3h2	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158678_l3h3	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
158679_l2h2	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158679_l3h2	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158679_l3h3	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800194	800194	Bus	Master IV	XDD		EU-RENAULT-MASTER-IV-BUS-L3H3-01	HIGH	L3H3乘员运输车身。	READY
158680_l2h2	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158680_l3h2	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158680_l3h3	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800282_l2h2	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
800282_l3h2	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
800282_l3h3	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800283_l2h2	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
800283_l3h2	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
800283_l3h3	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-IV-VAN-L2H2-01	5685	2080	2500	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-VAN-L3H2-01	6315	2080	2500	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-VAN-L3H3-01	6315	2080	2780	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-BUS-L3H3-01	6315	2080	2780	Renault All-New Master official passenger dimensions; Renault Master official e-brochure	https://renault.com.do/cars/master/dimensions.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
```

## 下一步优先处理

1. 闭合 Master IV `Pritsche/Fahrgestell` 的 platform cab、single chassis cab、double chassis cab 分支。
2. 分开处理 FWD 的 L2／L3 和 RWD 的 L3 长轴配置，避免把不同底盘长度合并。
3. 随后集中处理 Master III Bus、Kasten 和 Pritsche/Fahrgestell 的轴距、车顶及 FWD／RWD 外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Master IV Fahrgestell 的前驱单排 L2/L3、前驱双排 L3，以及后驱双后轮单排/双排 L3/L4，共新增 7 个尺寸组。
* 5 个前驱柴油或电动 Ktype 的 Platform-cab L2/L3 分支已保留为 PENDING：德国官方表给出了长度和宽度，但未直接列出同一配置的整车高度，不能拼接建组。其余底盘驾驶室分支均已关联完成。([雷诺商务][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：70
* READY 映射：101
* PENDING 映射：10
* PENDING 输入 Ktype：35
* 未开始处理的输入 Ktype：30，均为 Master III
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800191_platform_l2	800191	Pickup	Master IV	XDD	2		LOW	Platform-cab L2；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800191_platform_l3	800191	Pickup	Master IV	XDD	2		LOW	Platform-cab L3；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800191_single_l2	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	单排底盘驾驶室L2。	READY
800191_single_l3	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	单排底盘驾驶室L3。	READY
800191_double_l3	800191	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
800192_platform_l2	800192	Pickup	Master IV	XDD	2		LOW	Platform-cab L2；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800192_platform_l3	800192	Pickup	Master IV	XDD	2		LOW	Platform-cab L3；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800192_single_l2	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	单排底盘驾驶室L2。	READY
800192_single_l3	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	单排底盘驾驶室L3。	READY
800192_double_l3	800192	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
802362_single_l3_drw	802362	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L3。	READY
802362_single_l4_drw	802362	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L4。	READY
802362_double_l3_drw	802362	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L3。	READY
802362_double_l4_drw	802362	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L4。	READY
800193_platform_l2	800193	Pickup	Master IV	XDD	2		LOW	Platform-cab L2；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800193_platform_l3	800193	Pickup	Master IV	XDD	2		LOW	Platform-cab L3；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800193_single_l2	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	单排底盘驾驶室L2。	READY
800193_single_l3	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	单排底盘驾驶室L3。	READY
800193_double_l3	800193	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
802363_single_l3_drw	802363	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L3。	READY
802363_single_l4_drw	802363	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L4。	READY
802363_double_l3_drw	802363	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L3。	READY
802363_double_l4_drw	802363	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L4。	READY
800956_platform_l2	800956	Pickup	Master IV	XDD	2		LOW	Platform-cab L2；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800956_platform_l3	800956	Pickup	Master IV	XDD	2		LOW	Platform-cab L3；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800956_single_l2	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	电动前驱单排底盘驾驶室L2。	READY
800956_single_l3	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	电动前驱单排底盘驾驶室L3。	READY
800957_platform_l2	800957	Pickup	Master IV	XDD	2		LOW	Platform-cab L2；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800957_platform_l3	800957	Pickup	Master IV	XDD	2		LOW	Platform-cab L3；同一德国配置来源未直接给出整车高度。	PENDING: Platform-cab整车高度未闭合
800957_single_l2	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	电动前驱单排底盘驾驶室L2。	READY
800957_single_l3	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	电动前驱单排底盘驾驶室L3。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	5730	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	6940	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	6940	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
```

## 下一步优先处理

1. 补齐 Master IV Platform-cab L2/L3 的同配置整车高度，将当前 10 条 PENDING 转为 READY。
2. 集中闭合 Master III Kasten 的前驱、后驱及 4×4 长度和车顶分支。
3. 随后批量关联 Master III Bus 与 Pritsche/Fahrgestell Ktype。

推进信号：CONTINUE

[1]: https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html?utm_source=chatgpt.com "Renault Fahrgestell – der perfekte Transporter für Ihr ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已补齐 Master IV Platform-cab L2H1、L3H1 的完整外廓。Renault 官方页面明确给出长度 5682／6312 mm、车身宽度 2080 mm（不含后视镜）和高度 2260 mm。([Renault Professional][1])
* 上轮 10 条 Platform-cab `PENDING` 映射全部转为 `READY`，5 个柴油／电动 Ktype 复用同一对稳定尺寸组。
* 本轮未重复输出其他已确认的 Master IV 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：70
* READY 映射：111
* 待闭合输入 Ktype：30
* 已确认尺寸组：26
* 剩余记录全部为 Master III。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800191_platform_l2	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800191_platform_l3	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800192_platform_l2	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800192_platform_l3	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800193_platform_l2	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800193_platform_l3	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800956_platform_l2	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	电动Platform-cab L2H1。	READY
800956_platform_l3	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	电动Platform-cab L3H1。	READY
800957_platform_l2	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	电动Platform-cab L2H1。	READY
800957_platform_l3	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	电动Platform-cab L3H1。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	5682	2080	2260	Renault UK Master Platform and Chassis Cab official dimensions	https://business.renault.co.uk/master-range/chassis-cab.html
EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	6312	2080	2260	Renault UK Master Platform and Chassis Cab official dimensions	https://business.renault.co.uk/master-range/chassis-cab.html
```

## 下一步优先处理

1. 闭合 Master III `Bus` 的 FWD L2H2、L3H2 及 RWD 长车身分支。
2. 批量处理 Master III `Kasten` 的 FWD L1/L2/L3 与 H1/H2/H3组合。
3. 最后处理 Master III `Pritsche/Fahrgestell` 的 Platform、单排／双排底盘及 FWD／RWD／4×4边界。

推进信号：CONTINUE

[1]: https://business.renault.co.uk/master-range/chassis-cab.html?utm_source=chatgpt.com "Renault Master Platform and Chassis Cab"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Master III 后驱 `Kasten` Ktype `108153`、`58901`。
* 两个 Ktype 均按 L3/L4、H2/H3、单后轮/双后轮拆分，共新增 16 条 READY 映射。
* 官方尺寸表确认这些分支的车身宽度均为 **2070 mm，不含后视镜**；不同轮胎形式造成高度差异，因此单后轮和双后轮没有强行合并。([雷诺集团][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：72
* READY 映射：127
* 尚未闭合输入 Ktype：28
* 已确认尺寸组：34
* 剩余：Master III Bus 6 个、普通 Pritsche/Fahrgestell 7 个、4×4 Kasten/Pritsche 8 个，以及跨 2019 改款的 Kasten 7 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108153_l3h2_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	后驱L3H2单后轮封闭货厢。	READY
108153_l3h2_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	后驱L3H2双后轮封闭货厢。	READY
108153_l3h3_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	后驱L3H3单后轮封闭货厢。	READY
108153_l3h3_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	后驱L3H3双后轮封闭货厢。	READY
108153_l4h2_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	后驱L4H2单后轮封闭货厢。	READY
108153_l4h2_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	后驱L4H2双后轮封闭货厢。	READY
108153_l4h3_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	后驱L4H3单后轮封闭货厢。	READY
108153_l4h3_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	后驱L4H3双后轮封闭货厢。	READY
58901_l3h2_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	后驱L3H2单后轮封闭货厢。	READY
58901_l3h2_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	后驱L3H2双后轮封闭货厢。	READY
58901_l3h3_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	后驱L3H3单后轮封闭货厢。	READY
58901_l3h3_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	后驱L3H3双后轮封闭货厢。	READY
58901_l4h2_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	后驱L4H2单后轮封闭货厢。	READY
58901_l4h2_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	后驱L4H2双后轮封闭货厢。	READY
58901_l4h3_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	后驱L4H3单后轮封闭货厢。	READY
58901_l4h3_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	后驱L4H3双后轮封闭货厢。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	6198	2070	2527	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	6198	2070	2549	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	6198	2070	2786	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	6198	2070	2815	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	6848	2070	2527	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	6848	2070	2557	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	6848	2070	2786	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	6848	2070	2808	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
```

## 下一步优先处理

1. 闭合 Master III 前驱 Kasten 的 L1H1、L1H2、L2H2、L2H3、L3H2、L3H3。
2. 对跨越 2019 改款的 Ktype 拆分 `prefl` 与 `facelift`，避免把增加约 27 mm 前悬后的车身混为同组。
3. 随后批量关联 Master III Bus，并最后处理 4×4 升高底盘与 Pritsche/Fahrgestell。

推进信号：CONTINUE

[1]: https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf "14797_CH-FR_MAGAZINE_B_Master_X62_Ph1_PDF_WEB.pdf"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 4 个跨越 2019 年改款的 Master III 前驱 `Kasten` Ktype，并按 L1H1、L1H2、L2H2、L2H3、L3H2、L3H3 拆分改款前后外廓。
* Renault 官方资料确认改款前长度为 5048／5548／6198 mm，改款后对应为 5075／5575／6225 mm；车身宽度统一为不含后视镜的 2070 mm。([雷诺集团][1])
* 本轮新增 48 条 READY 映射和 12 个尺寸组，后续相同外廓直接复用。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：76
* READY 映射：175
* 尚未闭合输入 Ktype：24
* 已确认尺寸组：46
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121779_l1h1_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
121779_l1h1_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
121779_l1h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
121779_l1h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
121779_l2h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
121779_l2h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
121779_l2h3_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
121779_l2h3_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
121779_l3h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
121779_l3h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
121779_l3h3_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
121779_l3h3_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
108252_l1h1_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
108252_l1h1_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
108252_l1h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
108252_l1h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
108252_l2h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
108252_l2h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
108252_l2h3_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
108252_l2h3_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
108252_l3h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
108252_l3h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
108252_l3h3_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
108252_l3h3_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
108253_l1h1_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
108253_l1h1_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
108253_l1h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
108253_l1h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
108253_l2h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
108253_l2h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
108253_l2h3_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
108253_l2h3_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
108253_l3h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
108253_l3h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
108253_l3h3_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
108253_l3h3_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
122129_l1h1_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
122129_l1h1_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
122129_l1h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
122129_l1h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
122129_l2h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
122129_l2h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
122129_l2h3_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
122129_l2h3_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
122129_l3h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
122129_l3h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
122129_l3h3_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
122129_l3h3_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	5048	2070	2307	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	5075	2070	2307	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	5048	2070	2500	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	5075	2070	2500	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	5548	2070	2499	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	5575	2070	2499	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	5548	2070	2749	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	5575	2070	2749	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	6198	2070	2488	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	6225	2070	2488	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	6198	2070	2744	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	6225	2070	2744	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
```

## 下一步优先处理

1. 闭合 Ktype `58900` 的生产阶段边界并关联现有前驱 Kasten 尺寸组。
2. 批量处理 Master III Bus 的改款前后 L2H2、L3H2／L3H3 外廓。
3. 随后处理跨改款的 RWD Kasten、4×4 Kasten 和 Pritsche/Fahrgestell。

推进信号：CONTINUE

[1]: https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf "14797_CH-FR_MAGAZINE_B_Master_X62_Ph1_PDF_WEB.pdf"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Ktype `58900` 已按改款前后拆分，并直接复用现有前驱 Kasten 的 12 个尺寸组。
* Ktype `118804`、`108151` 已闭合后驱 Kasten 分支：改款前复用既有 L3/L4、H2/H3、SRW/DRW 尺寸组；改款后新增 4 个稳定尺寸组。
* Renault 官方改款后尺寸表确认后驱 Kasten 的 L3/L4 长度为 6225/6875 mm、宽度为不含后视镜的 2070 mm；相同 L/H 下不再因 SRW/DRW 重复建组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：79
* READY 映射：211
* 尚未闭合输入 Ktype：21
* 已确认尺寸组：50
* 剩余：Master III Bus 6 个、Pritsche/Fahrgestell 7 个、4×4 Kasten/Pritsche 8 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58900_l1h1_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
58900_l1h1_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
58900_l1h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
58900_l1h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
58900_l2h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
58900_l2h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
58900_l2h3_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
58900_l2h3_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
58900_l3h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
58900_l3h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
58900_l3h3_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
58900_l3h3_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
118804_l3h2_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前后驱L3H2单后轮封闭货厢。	READY
118804_l3h2_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前后驱L3H2双后轮封闭货厢。	READY
118804_l3h3_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前后驱L3H3单后轮封闭货厢。	READY
118804_l3h3_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前后驱L3H3双后轮封闭货厢。	READY
118804_l4h2_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前后驱L4H2单后轮封闭货厢。	READY
118804_l4h2_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前后驱L4H2双后轮封闭货厢。	READY
118804_l4h3_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前后驱L4H3单后轮封闭货厢。	READY
118804_l4h3_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前后驱L4H3双后轮封闭货厢。	READY
118804_l3h2_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后后驱L3H2封闭货厢。	READY
118804_l3h3_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后后驱L3H3封闭货厢。	READY
118804_l4h2_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后后驱L4H2封闭货厢。	READY
118804_l4h3_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后后驱L4H3封闭货厢。	READY
108151_l3h2_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前后驱L3H2单后轮封闭货厢。	READY
108151_l3h2_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前后驱L3H2双后轮封闭货厢。	READY
108151_l3h3_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前后驱L3H3单后轮封闭货厢。	READY
108151_l3h3_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前后驱L3H3双后轮封闭货厢。	READY
108151_l4h2_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前后驱L4H2单后轮封闭货厢。	READY
108151_l4h2_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前后驱L4H2双后轮封闭货厢。	READY
108151_l4h3_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前后驱L4H3单后轮封闭货厢。	READY
108151_l4h3_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前后驱L4H3双后轮封闭货厢。	READY
108151_l3h2_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后后驱L3H2封闭货厢。	READY
108151_l3h3_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后后驱L3H3封闭货厢。	READY
108151_l4h2_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后后驱L4H2封闭货厢。	READY
108151_l4h3_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后后驱L4H3封闭货厢。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	6225	2070	2549	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	6225	2070	2815	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	6875	2070	2557	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	6875	2070	2808	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
```

## 下一步优先处理

1. 按 `JV` 车身代码闭合 6 个 Master III Bus 的 L1H1、L2H2、L3H2 分支，并复用对应标准车身尺寸。
2. 集中处理 8 个 Master III 4×4 Kasten/Pritsche，单独计算官方升高悬架造成的高度变化。
3. 最后闭合 7 个普通 Pritsche/Fahrgestell 的 Platform、单排、双排及 FWD/RWD 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 6 个 Master III `Bus` Ktype。按实际乘员车外廓拆分为 L1H1 Combi、L2H2 Combi 与 L3H2 Bus；发动机版本未覆盖的分支没有强行派生。2016 年 Renault 乘用版目录明确区分 145/170 hp 的 L1H1、L2H2 Combi，以及 145/165 hp 的 L3H2 17座 Minibus。
* L1H1、L2H2 外廓直接复用现有 Master III 前驱尺寸组；仅首次创建改款前、改款后两个 L3H2 Bus 尺寸组。
* 改款后 L3H2 Bus 官方尺寸为 6225 × 2070 × 2496 mm，其中 2070 mm 为不含后视镜宽度。([雷诺集团][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：85
* READY 映射：234
* 尚未闭合输入 Ktype：15
* 已确认尺寸组：52
* 剩余：Master III 4×4 Kasten/Pritsche 8 个、普通 Pritsche/Fahrgestell 7 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11038_l1h1_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1乘员车外廓。	READY
11038_l2h2_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2乘员车外廓。	READY
11038_l3h2_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
108154_l1h1_prefl	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
108154_l1h1_facelift	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
108154_l2h2_prefl	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
108154_l2h2_facelift	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
11043_l1h1_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
11043_l1h1_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
11043_l2h2_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
11043_l2h2_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
11043_l3h2_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
11043_l3h2_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
59333_l3h2_prefl	59333	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Minibus外廓。	READY
59333_l3h2_facelift	59333	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
108152_l2h2_prefl	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
108152_l2h2_facelift	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
108152_l3h2_prefl	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
108152_l3h2_facelift	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
116478_l1h1_prefl	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
116478_l1h1_facelift	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
116478_l2h2_prefl	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
116478_l2h2_facelift	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	6198	2070	2496	Renault Master & Master Z.E. official passenger dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	6225	2070	2496	Renault Master official brochure 2023	https://cdn.group.renault.com/ren/ma/ebrochure-2023/master/ct-mobile-master-21072023.pdf
```

## 下一步优先处理

1. 闭合 4 个 Master III 4×4 `Kasten` Ktype，按 L3/L4、H2/H3 及升高悬架拆分。
2. 处理 4 个 4×4 `Pritsche/Fahrgestell` Ktype，复用同一套官方 4×4 底盘外廓。
3. 最后闭合 7 个普通 `Pritsche/Fahrgestell` Ktype，并进入最终机械检查。

推进信号：CONTINUE

[1]: https://cdn.group.renault.com/ren/ma/ebrochure-2023/master/ct-mobile-master-21072023.pdf?utm_source=chatgpt.com "RENAULT MASTER"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 8 个 Master III 4×4 Ktype：4 个 `Kasten`、4 个 `Pritsche/Fahrgestell`。
* 官方 4×4 规格表确认，封闭货厢的外部长宽高与对应后驱基础车身一致，因此直接复用既有 L3/L4、H2/H3、SRW/DRW 尺寸组，不重复建组。底盘驾驶室按单排／双排、L2/L3/L4、SRW/DRW 及 2019 改款前后闭合，共首次创建 16 个尺寸组。([Diacfa][1])
* 2019 改款后底盘驾驶室长度较改款前增加 27 mm；车身宽度保持 2070 mm，不含后视镜。([Diacfa][1])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：93
* READY 映射：330
* PENDING 输入 Ktype：7
* 已确认尺寸组：68
* 剩余均为普通 Master III `Pritsche/Fahrgestell`。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
802204_single_l2_srw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
802204_single_l3_srw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
802204_single_l3_drw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
802204_single_l4_drw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
802204_double_l2_srw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
802204_double_l3_srw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
802204_double_l3_drw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
802204_double_l4_drw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
802204_single_l2_srw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
802204_single_l3_srw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
802204_single_l3_drw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
802204_single_l4_drw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
802204_double_l2_srw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
802204_double_l3_srw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
802204_double_l3_drw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
802204_double_l4_drw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
802205_l3h2_srw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
802205_l3h2_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
802205_l3h3_srw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
802205_l3h3_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
802205_l4h2_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
802205_l4h3_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
802205_l3h2_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
802205_l3h3_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
802205_l4h2_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
802205_l4h3_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
802202_l3h2_srw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	4×4 L3H2单后轮封闭货厢。	READY
802202_l3h2_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	4×4 L3H2双后轮封闭货厢。	READY
802202_l3h3_srw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	4×4 L3H3单后轮封闭货厢。	READY
802202_l3h3_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	4×4 L3H3双后轮封闭货厢。	READY
802202_l4h2_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	4×4 L4H2双后轮封闭货厢。	READY
802202_l4h3_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	4×4 L4H3双后轮封闭货厢。	READY
802203_single_l2_srw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	4×4单排L2单后轮底盘。	READY
802203_single_l3_srw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	4×4单排L3单后轮底盘。	READY
802203_single_l3_drw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	4×4单排L3双后轮底盘。	READY
802203_single_l4_drw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	4×4单排L4双后轮底盘。	READY
802203_double_l2_srw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	4×4双排L2单后轮底盘。	READY
802203_double_l3_srw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	4×4双排L3单后轮底盘。	READY
802203_double_l3_drw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	4×4双排L3双后轮底盘。	READY
802203_double_l4_drw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	4×4双排L4双后轮底盘。	READY
155738_single_l2_srw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
155738_single_l3_srw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
155738_single_l3_drw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
155738_single_l4_drw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
155738_double_l2_srw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
155738_double_l3_srw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
155738_double_l3_drw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
155738_double_l4_drw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
155738_single_l2_srw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
155738_single_l3_srw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
155738_single_l3_drw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
155738_single_l4_drw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
155738_double_l2_srw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
155738_double_l3_srw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
155738_double_l3_drw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
155738_double_l4_drw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
155740_l3h2_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
155740_l3h2_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
155740_l3h3_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
155740_l3h3_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
155740_l4h2_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前4×4 L4H2单后轮封闭货厢。	READY
155740_l4h2_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
155740_l4h3_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前4×4 L4H3单后轮封闭货厢。	READY
155740_l4h3_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
155740_l3h2_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
155740_l3h3_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
155740_l4h2_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
155740_l4h3_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
155737_single_l2_srw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
155737_single_l3_srw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
155737_single_l3_drw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
155737_single_l4_drw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
155737_double_l2_srw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
155737_double_l3_srw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
155737_double_l3_drw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
155737_double_l4_drw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
155737_single_l2_srw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
155737_single_l3_srw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
155737_single_l3_drw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
155737_single_l4_drw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
155737_double_l2_srw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
155737_double_l3_srw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
155737_double_l3_drw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
155737_double_l4_drw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
155739_l3h2_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
155739_l3h2_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
155739_l3h3_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
155739_l3h3_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
155739_l4h2_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前4×4 L4H2单后轮封闭货厢。	READY
155739_l4h2_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
155739_l4h3_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前4×4 L4H3单后轮封闭货厢。	READY
155739_l4h3_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
155739_l3h2_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
155739_l3h3_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
155739_l4h2_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
155739_l4h3_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	5643	2070	2284	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	6293	2070	2276	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	6193	2070	2283	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	6843	2070	2273	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	5643	2070	2295	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	6293	2070	2285	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	6193	2070	2301	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	6843	2070	2286	Renault Master official brochure October 2017—specific 4×4 chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	5670	2070	2284	Renault New Master official e-brochure—chassis single-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	6320	2070	2276	Renault New Master official e-brochure—chassis single-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	6220	2070	2283	Renault New Master official e-brochure—chassis single-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	6870	2070	2273	Renault New Master official e-brochure—chassis single-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	5670	2070	2295	Renault New Master official e-brochure—chassis double-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	6320	2070	2285	Renault New Master official e-brochure—chassis double-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	6220	2070	2301	Renault New Master official e-brochure—chassis double-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	6870	2070	2286	Renault New Master official e-brochure—chassis double-cab dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
```

## 下一步优先处理

1. 将 `123447`、`58903`、`118600`、`121778` 的前驱底盘分支关联至 L2/L3 单排、双排及 Platform 外廓。
2. 将 `108177`、`58904`、`108178` 的后驱分支关联至本轮已闭合的单排／双排、SRW／DRW 尺寸组。
3. PENDING 清零后，下一条回复直接进行一次机械检查并输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf "Acr10432996900800-167307.tmp.pdf"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_14201-14300_ktype_dimension_mapping_final.tsv
- left18448_14201-14300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已闭合剩余 7 个 Master III `Pritsche/Fahrgestell` Ktype。4 个前驱 Ktype 按 Platform-cab、单排及双排底盘、L2/L3、改款前后拆分；3 个后驱 Ktype 复用既有单排／双排、SRW／DRW、L2/L3/L4 尺寸组。
* 首次创建 8 个 Master III Platform-cab 尺寸组。改款前与改款后官方图表分别确认了 L2/L3、H1/H2 的完整外廓和不含后视镜宽度。([Diacfa][1])
* 已完成机械检查：两张表列数正确，426 个 `id` 唯一，76 个 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，无孤立组、空尺寸或 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：426
* PENDING 映射：0
* 已确认尺寸组：76
* 当前批次已全部完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11038_l1h1_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1乘员车外廓。	READY
11038_l2h2_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2乘员车外廓。	READY
11038_l3h2_prefl	11038	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
802204_single_l2_srw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
802204_single_l3_srw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
802204_single_l3_drw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
802204_single_l4_drw_prefl	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
802204_double_l2_srw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
802204_double_l3_srw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
802204_double_l3_drw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
802204_double_l4_drw_prefl	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
802204_single_l2_srw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
802204_single_l3_srw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
802204_single_l3_drw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
802204_single_l4_drw_facelift	802204	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
802204_double_l2_srw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
802204_double_l3_srw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
802204_double_l3_drw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
802204_double_l4_drw_facelift	802204	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
802205_l3h2_srw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
802205_l3h2_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
802205_l3h3_srw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
802205_l3h3_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
802205_l4h2_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
802205_l4h3_drw_prefl	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
802205_l3h2_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
802205_l3h3_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
802205_l4h2_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
802205_l4h3_facelift	802205	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
121779_l1h1_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
121779_l1h1_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
121779_l1h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
121779_l1h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
121779_l2h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
121779_l2h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
121779_l2h3_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
121779_l2h3_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
121779_l3h2_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
121779_l3h2_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
121779_l3h3_prefl	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
121779_l3h3_facelift	121779	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
118804_l3h2_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前L3H2单后轮封闭货厢。	READY
118804_l3h2_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前L3H2双后轮封闭货厢。	READY
118804_l3h3_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前L3H3单后轮封闭货厢。	READY
118804_l3h3_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前L3H3双后轮封闭货厢。	READY
118804_l4h2_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前L4H2单后轮封闭货厢。	READY
118804_l4h2_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前L4H2双后轮封闭货厢。	READY
118804_l4h3_srw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前L4H3单后轮封闭货厢。	READY
118804_l4h3_drw_prefl	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前L4H3双后轮封闭货厢。	READY
118804_l3h2_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后L3H2封闭货厢。	READY
118804_l3h3_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后L3H3封闭货厢。	READY
118804_l4h2_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后L4H2封闭货厢。	READY
118804_l4h3_facelift	118804	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后L4H3封闭货厢。	READY
802202_l3h2_srw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	4×4 L3H2单后轮封闭货厢。	READY
802202_l3h2_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	4×4 L3H2双后轮封闭货厢。	READY
802202_l3h3_srw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	4×4 L3H3单后轮封闭货厢。	READY
802202_l3h3_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	4×4 L3H3双后轮封闭货厢。	READY
802202_l4h2_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	4×4 L4H2双后轮封闭货厢。	READY
802202_l4h3_drw	802202	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	4×4 L4H3双后轮封闭货厢。	READY
802203_single_l2_srw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	4×4单排L2单后轮底盘。	READY
802203_single_l3_srw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	4×4单排L3单后轮底盘。	READY
802203_single_l3_drw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	4×4单排L3双后轮底盘。	READY
802203_single_l4_drw	802203	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	4×4单排L4双后轮底盘。	READY
802203_double_l2_srw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	4×4双排L2单后轮底盘。	READY
802203_double_l3_srw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	4×4双排L3单后轮底盘。	READY
802203_double_l3_drw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	4×4双排L3双后轮底盘。	READY
802203_double_l4_drw	802203	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	4×4双排L4双后轮底盘。	READY
108154_l1h1_prefl	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
108154_l1h1_facelift	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
108154_l2h2_prefl	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
108154_l2h2_facelift	108154	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
108252_l1h1_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
108252_l1h1_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
108252_l1h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
108252_l1h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
108252_l2h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
108252_l2h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
108252_l2h3_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
108252_l2h3_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
108252_l3h2_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
108252_l3h2_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
108252_l3h3_prefl	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
108252_l3h3_facelift	108252	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
123447_platform_l2h1_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H1-FWD-01	MEDIUM	改款前Platform-cab L2H1。	READY
123447_platform_l2h1_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H1-FWD-01	MEDIUM	2019改款后Platform-cab L2H1。	READY
123447_platform_l2h2_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H2-FWD-01	MEDIUM	改款前Platform-cab L2H2。	READY
123447_platform_l2h2_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H2-FWD-01	MEDIUM	2019改款后Platform-cab L2H2。	READY
123447_platform_l3h1_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H1-FWD-01	MEDIUM	改款前Platform-cab L3H1。	READY
123447_platform_l3h1_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H1-FWD-01	MEDIUM	2019改款后Platform-cab L3H1。	READY
123447_platform_l3h2_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H2-FWD-01	MEDIUM	改款前Platform-cab L3H2。	READY
123447_platform_l3h2_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H2-FWD-01	MEDIUM	2019改款后Platform-cab L3H2。	READY
123447_single_l2_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前前驱单排L2底盘驾驶室。	READY
123447_single_l2_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后前驱单排L2底盘驾驶室。	READY
123447_single_l3_prefl	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前前驱单排L3底盘驾驶室。	READY
123447_single_l3_facelift	123447	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后前驱单排L3底盘驾驶室。	READY
123447_double_l2_prefl	123447	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前前驱双排L2底盘驾驶室。	READY
123447_double_l2_facelift	123447	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后前驱双排L2底盘驾驶室。	READY
123447_double_l3_prefl	123447	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前前驱双排L3底盘驾驶室。	READY
123447_double_l3_facelift	123447	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后前驱双排L3底盘驾驶室。	READY
108153_l3h2_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	后驱L3H2单后轮封闭货厢。	READY
108153_l3h2_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	后驱L3H2双后轮封闭货厢。	READY
108153_l3h3_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	后驱L3H3单后轮封闭货厢。	READY
108153_l3h3_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	后驱L3H3双后轮封闭货厢。	READY
108153_l4h2_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	后驱L4H2单后轮封闭货厢。	READY
108153_l4h2_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	后驱L4H2双后轮封闭货厢。	READY
108153_l4h3_srw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	后驱L4H3单后轮封闭货厢。	READY
108153_l4h3_drw	108153	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	后驱L4H3双后轮封闭货厢。	READY
108177_single_l2_srw	108177	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	后驱单排L2单后轮底盘。	READY
108177_single_l3_srw	108177	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	后驱单排L3单后轮底盘。	READY
108177_single_l3_drw	108177	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	后驱单排L3双后轮底盘。	READY
108177_single_l4_drw	108177	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	后驱单排L4双后轮底盘。	READY
108177_double_l2_srw	108177	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	后驱双排L2单后轮底盘。	READY
108177_double_l3_srw	108177	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	后驱双排L3单后轮底盘。	READY
108177_double_l3_drw	108177	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	后驱双排L3双后轮底盘。	READY
108177_double_l4_drw	108177	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	后驱双排L4双后轮底盘。	READY
155738_single_l2_srw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
155738_single_l3_srw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
155738_single_l3_drw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
155738_single_l4_drw_prefl	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
155738_double_l2_srw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
155738_double_l3_srw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
155738_double_l3_drw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
155738_double_l4_drw_prefl	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
155738_single_l2_srw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
155738_single_l3_srw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
155738_single_l3_drw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
155738_single_l4_drw_facelift	155738	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
155738_double_l2_srw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
155738_double_l3_srw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
155738_double_l3_drw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
155738_double_l4_drw_facelift	155738	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
155740_l3h2_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
155740_l3h2_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
155740_l3h3_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
155740_l3h3_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
155740_l4h2_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前4×4 L4H2单后轮封闭货厢。	READY
155740_l4h2_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
155740_l4h3_srw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前4×4 L4H3单后轮封闭货厢。	READY
155740_l4h3_drw_prefl	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
155740_l3h2_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
155740_l3h3_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
155740_l4h2_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
155740_l4h3_facelift	155740	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
11043_l1h1_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
11043_l1h1_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
11043_l2h2_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
11043_l2h2_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
11043_l3h2_prefl	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
11043_l3h2_facelift	11043	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
58900_l1h1_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
58900_l1h1_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
58900_l1h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
58900_l1h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
58900_l2h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
58900_l2h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
58900_l2h3_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
58900_l2h3_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
58900_l3h2_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
58900_l3h2_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
58900_l3h3_prefl	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
58900_l3h3_facelift	58900	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
58903_platform_l2h1_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H1-FWD-01	MEDIUM	改款前Platform-cab L2H1。	READY
58903_platform_l2h1_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H1-FWD-01	MEDIUM	2019改款后Platform-cab L2H1。	READY
58903_platform_l2h2_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H2-FWD-01	MEDIUM	改款前Platform-cab L2H2。	READY
58903_platform_l2h2_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H2-FWD-01	MEDIUM	2019改款后Platform-cab L2H2。	READY
58903_platform_l3h1_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H1-FWD-01	MEDIUM	改款前Platform-cab L3H1。	READY
58903_platform_l3h1_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H1-FWD-01	MEDIUM	2019改款后Platform-cab L3H1。	READY
58903_platform_l3h2_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H2-FWD-01	MEDIUM	改款前Platform-cab L3H2。	READY
58903_platform_l3h2_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H2-FWD-01	MEDIUM	2019改款后Platform-cab L3H2。	READY
58903_single_l2_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前前驱单排L2底盘驾驶室。	READY
58903_single_l2_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后前驱单排L2底盘驾驶室。	READY
58903_single_l3_prefl	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前前驱单排L3底盘驾驶室。	READY
58903_single_l3_facelift	58903	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后前驱单排L3底盘驾驶室。	READY
58903_double_l2_prefl	58903	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前前驱双排L2底盘驾驶室。	READY
58903_double_l2_facelift	58903	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后前驱双排L2底盘驾驶室。	READY
58903_double_l3_prefl	58903	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前前驱双排L3底盘驾驶室。	READY
58903_double_l3_facelift	58903	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后前驱双排L3底盘驾驶室。	READY
59333_l3h2_prefl	59333	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Minibus外廓。	READY
59333_l3h2_facelift	59333	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
58901_l3h2_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	后驱L3H2单后轮封闭货厢。	READY
58901_l3h2_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	后驱L3H2双后轮封闭货厢。	READY
58901_l3h3_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	后驱L3H3单后轮封闭货厢。	READY
58901_l3h3_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	后驱L3H3双后轮封闭货厢。	READY
58901_l4h2_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	后驱L4H2单后轮封闭货厢。	READY
58901_l4h2_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	后驱L4H2双后轮封闭货厢。	READY
58901_l4h3_srw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	后驱L4H3单后轮封闭货厢。	READY
58901_l4h3_drw	58901	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	后驱L4H3双后轮封闭货厢。	READY
58904_single_l2_srw	58904	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	后驱单排L2单后轮底盘。	READY
58904_single_l3_srw	58904	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	后驱单排L3单后轮底盘。	READY
58904_single_l3_drw	58904	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	后驱单排L3双后轮底盘。	READY
58904_single_l4_drw	58904	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	后驱单排L4双后轮底盘。	READY
58904_double_l2_srw	58904	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	后驱双排L2单后轮底盘。	READY
58904_double_l3_srw	58904	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	后驱双排L3单后轮底盘。	READY
58904_double_l3_drw	58904	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	后驱双排L3双后轮底盘。	READY
58904_double_l4_drw	58904	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	后驱双排L4双后轮底盘。	READY
155737_single_l2_srw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前4×4单排L2单后轮底盘。	READY
155737_single_l3_srw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前4×4单排L3单后轮底盘。	READY
155737_single_l3_drw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前4×4单排L3双后轮底盘。	READY
155737_single_l4_drw_prefl	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前4×4单排L4双后轮底盘。	READY
155737_double_l2_srw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前4×4双排L2单后轮底盘。	READY
155737_double_l3_srw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前4×4双排L3单后轮底盘。	READY
155737_double_l3_drw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前4×4双排L3双后轮底盘。	READY
155737_double_l4_drw_prefl	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前4×4双排L4双后轮底盘。	READY
155737_single_l2_srw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后4×4单排L2单后轮底盘。	READY
155737_single_l3_srw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后4×4单排L3单后轮底盘。	READY
155737_single_l3_drw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后4×4单排L3双后轮底盘。	READY
155737_single_l4_drw_facelift	155737	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后4×4单排L4双后轮底盘。	READY
155737_double_l2_srw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后4×4双排L2单后轮底盘。	READY
155737_double_l3_srw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后4×4双排L3单后轮底盘。	READY
155737_double_l3_drw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后4×4双排L3双后轮底盘。	READY
155737_double_l4_drw_facelift	155737	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后4×4双排L4双后轮底盘。	READY
155739_l3h2_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前4×4 L3H2单后轮封闭货厢。	READY
155739_l3h2_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前4×4 L3H2双后轮封闭货厢。	READY
155739_l3h3_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前4×4 L3H3单后轮封闭货厢。	READY
155739_l3h3_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前4×4 L3H3双后轮封闭货厢。	READY
155739_l4h2_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前4×4 L4H2单后轮封闭货厢。	READY
155739_l4h2_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前4×4 L4H2双后轮封闭货厢。	READY
155739_l4h3_srw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前4×4 L4H3单后轮封闭货厢。	READY
155739_l4h3_drw_prefl	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前4×4 L4H3双后轮封闭货厢。	READY
155739_l3h2_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后4×4 L3H2封闭货厢。	READY
155739_l3h3_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后4×4 L3H3封闭货厢。	READY
155739_l4h2_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后4×4 L4H2封闭货厢。	READY
155739_l4h3_facelift	155739	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后4×4 L4H3封闭货厢。	READY
108152_l2h2_prefl	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
108152_l2h2_facelift	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
108152_l3h2_prefl	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2 Bus外廓。	READY
108152_l3h2_facelift	108152	MPV	Master III	JV		EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2 Bus外廓。	READY
108253_l1h1_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
108253_l1h1_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
108253_l1h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
108253_l1h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
108253_l2h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
108253_l2h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
108253_l2h3_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
108253_l2h3_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
108253_l3h2_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
108253_l3h2_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
108253_l3h3_prefl	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
108253_l3h3_facelift	108253	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
118600_platform_l2h1_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H1-FWD-01	MEDIUM	改款前Platform-cab L2H1。	READY
118600_platform_l2h1_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H1-FWD-01	MEDIUM	2019改款后Platform-cab L2H1。	READY
118600_platform_l2h2_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H2-FWD-01	MEDIUM	改款前Platform-cab L2H2。	READY
118600_platform_l2h2_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H2-FWD-01	MEDIUM	2019改款后Platform-cab L2H2。	READY
118600_platform_l3h1_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H1-FWD-01	MEDIUM	改款前Platform-cab L3H1。	READY
118600_platform_l3h1_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H1-FWD-01	MEDIUM	2019改款后Platform-cab L3H1。	READY
118600_platform_l3h2_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H2-FWD-01	MEDIUM	改款前Platform-cab L3H2。	READY
118600_platform_l3h2_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H2-FWD-01	MEDIUM	2019改款后Platform-cab L3H2。	READY
118600_single_l2_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前前驱单排L2底盘驾驶室。	READY
118600_single_l2_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后前驱单排L2底盘驾驶室。	READY
118600_single_l3_prefl	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前前驱单排L3底盘驾驶室。	READY
118600_single_l3_facelift	118600	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后前驱单排L3底盘驾驶室。	READY
118600_double_l2_prefl	118600	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前前驱双排L2底盘驾驶室。	READY
118600_double_l2_facelift	118600	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后前驱双排L2底盘驾驶室。	READY
118600_double_l3_prefl	118600	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前前驱双排L3底盘驾驶室。	READY
118600_double_l3_facelift	118600	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后前驱双排L3底盘驾驶室。	READY
108151_l3h2_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	MEDIUM	改款前L3H2单后轮封闭货厢。	READY
108151_l3h2_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	MEDIUM	改款前L3H2双后轮封闭货厢。	READY
108151_l3h3_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	MEDIUM	改款前L3H3单后轮封闭货厢。	READY
108151_l3h3_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	MEDIUM	改款前L3H3双后轮封闭货厢。	READY
108151_l4h2_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	MEDIUM	改款前L4H2单后轮封闭货厢。	READY
108151_l4h2_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	MEDIUM	改款前L4H2双后轮封闭货厢。	READY
108151_l4h3_srw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	MEDIUM	改款前L4H3单后轮封闭货厢。	READY
108151_l4h3_drw_prefl	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	MEDIUM	改款前L4H3双后轮封闭货厢。	READY
108151_l3h2_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	MEDIUM	2019改款后L3H2封闭货厢。	READY
108151_l3h3_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	MEDIUM	2019改款后L3H3封闭货厢。	READY
108151_l4h2_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	MEDIUM	2019改款后L4H2封闭货厢。	READY
108151_l4h3_facelift	108151	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	MEDIUM	2019改款后L4H3封闭货厢。	READY
108178_single_l2_srw_prefl	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前后驱单排L2单后轮底盘。	READY
108178_single_l3_srw_prefl	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前后驱单排L3单后轮底盘。	READY
108178_single_l3_drw_prefl	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	MEDIUM	改款前后驱单排L3双后轮底盘。	READY
108178_single_l4_drw_prefl	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	MEDIUM	改款前后驱单排L4双后轮底盘。	READY
108178_double_l2_srw_prefl	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前后驱双排L2单后轮底盘。	READY
108178_double_l3_srw_prefl	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前后驱双排L3单后轮底盘。	READY
108178_double_l3_drw_prefl	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	MEDIUM	改款前后驱双排L3双后轮底盘。	READY
108178_double_l4_drw_prefl	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	MEDIUM	改款前后驱双排L4双后轮底盘。	READY
108178_single_l2_srw_facelift	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后后驱单排L2单后轮底盘。	READY
108178_single_l3_srw_facelift	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后后驱单排L3单后轮底盘。	READY
108178_single_l3_drw_facelift	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	MEDIUM	2019改款后后驱单排L3双后轮底盘。	READY
108178_single_l4_drw_facelift	108178	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	MEDIUM	2019改款后后驱单排L4双后轮底盘。	READY
108178_double_l2_srw_facelift	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后后驱双排L2单后轮底盘。	READY
108178_double_l3_srw_facelift	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后后驱双排L3单后轮底盘。	READY
108178_double_l3_drw_facelift	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	MEDIUM	2019改款后后驱双排L3双后轮底盘。	READY
108178_double_l4_drw_facelift	108178	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	MEDIUM	2019改款后后驱双排L4双后轮底盘。	READY
116478_l1h1_prefl	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1 Combi外廓。	READY
116478_l1h1_facelift	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1 Combi外廓。	READY
116478_l2h2_prefl	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2 Combi外廓。	READY
116478_l2h2_facelift	116478	MPV	Master III	JV		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2 Combi外廓。	READY
121778_platform_l2h1_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H1-FWD-01	MEDIUM	改款前Platform-cab L2H1。	READY
121778_platform_l2h1_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H1-FWD-01	MEDIUM	2019改款后Platform-cab L2H1。	READY
121778_platform_l2h2_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H2-FWD-01	MEDIUM	改款前Platform-cab L2H2。	READY
121778_platform_l2h2_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H2-FWD-01	MEDIUM	2019改款后Platform-cab L2H2。	READY
121778_platform_l3h1_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H1-FWD-01	MEDIUM	改款前Platform-cab L3H1。	READY
121778_platform_l3h1_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H1-FWD-01	MEDIUM	2019改款后Platform-cab L3H1。	READY
121778_platform_l3h2_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H2-FWD-01	MEDIUM	改款前Platform-cab L3H2。	READY
121778_platform_l3h2_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H2-FWD-01	MEDIUM	2019改款后Platform-cab L3H2。	READY
121778_single_l2_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	MEDIUM	改款前前驱单排L2底盘驾驶室。	READY
121778_single_l2_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	MEDIUM	2019改款后前驱单排L2底盘驾驶室。	READY
121778_single_l3_prefl	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	MEDIUM	改款前前驱单排L3底盘驾驶室。	READY
121778_single_l3_facelift	121778	Pickup	Master III	X62	2	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	MEDIUM	2019改款后前驱单排L3底盘驾驶室。	READY
121778_double_l2_prefl	121778	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	MEDIUM	改款前前驱双排L2底盘驾驶室。	READY
121778_double_l2_facelift	121778	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	MEDIUM	2019改款后前驱双排L2底盘驾驶室。	READY
121778_double_l3_prefl	121778	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	MEDIUM	改款前前驱双排L3底盘驾驶室。	READY
121778_double_l3_facelift	121778	Pickup	Master III	X62	4	EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	MEDIUM	2019改款后前驱双排L3底盘驾驶室。	READY
122129_l1h1_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	MEDIUM	改款前L1H1前驱封闭货厢。	READY
122129_l1h1_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	MEDIUM	2019改款后L1H1前驱封闭货厢。	READY
122129_l1h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	MEDIUM	改款前L1H2前驱封闭货厢。	READY
122129_l1h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	MEDIUM	2019改款后L1H2前驱封闭货厢。	READY
122129_l2h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	MEDIUM	改款前L2H2前驱封闭货厢。	READY
122129_l2h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	MEDIUM	2019改款后L2H2前驱封闭货厢。	READY
122129_l2h3_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	MEDIUM	改款前L2H3前驱封闭货厢。	READY
122129_l2h3_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	MEDIUM	2019改款后L2H3前驱封闭货厢。	READY
122129_l3h2_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	MEDIUM	改款前L3H2前驱封闭货厢。	READY
122129_l3h2_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	MEDIUM	2019改款后L3H2前驱封闭货厢。	READY
122129_l3h3_prefl	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	MEDIUM	改款前L3H3前驱封闭货厢。	READY
122129_l3h3_facelift	122129	Van	Master III	X62		EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	MEDIUM	2019改款后L3H3前驱封闭货厢。	READY
158677_l2h2	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158677_l3h2	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158677_l3h3	158677	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
158678_l2h2	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158678_l3h2	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158678_l3h3	158678	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800191_platform_l2	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800191_platform_l3	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800191_single_l2	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	前驱单排底盘驾驶室L2。	READY
800191_single_l3	800191	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	前驱单排底盘驾驶室L3。	READY
800191_double_l3	800191	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
158679_l2h2	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158679_l3h2	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158679_l3h3	158679	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800194	800194	Bus	Master IV	XDD		EU-RENAULT-MASTER-IV-BUS-L3H3-01	HIGH	L3H3乘员运输车身。	READY
800192_platform_l2	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800192_platform_l3	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800192_single_l2	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	前驱单排底盘驾驶室L2。	READY
800192_single_l3	800192	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	前驱单排底盘驾驶室L3。	READY
800192_double_l3	800192	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
802362_single_l3_drw	802362	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L3。	READY
802362_single_l4_drw	802362	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L4。	READY
802362_double_l3_drw	802362	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L3。	READY
802362_double_l4_drw	802362	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L4。	READY
158680_l2h2	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
158680_l3h2	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
158680_l3h3	158680	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800193_platform_l2	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	Platform-cab L2H1。	READY
800193_platform_l3	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	Platform-cab L3H1。	READY
800193_single_l2	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	前驱单排底盘驾驶室L2。	READY
800193_single_l3	800193	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	前驱单排底盘驾驶室L3。	READY
800193_double_l3	800193	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	HIGH	双排底盘驾驶室L3。	READY
802363_single_l3_drw	802363	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L3。	READY
802363_single_l4_drw	802363	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	HIGH	后驱双后轮单排底盘驾驶室L4。	READY
802363_double_l3_drw	802363	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L3。	READY
802363_double_l4_drw	802363	Pickup	Master IV	XDD	4	EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	HIGH	后驱双后轮双排底盘驾驶室L4。	READY
800282_l2h2	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
800282_l3h2	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
800282_l3h3	800282	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800283_l2h2	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L2H2-01	HIGH	L2H2封闭式货厢外廓。	READY
800283_l3h2	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H2-01	HIGH	L3H2封闭式货厢外廓。	READY
800283_l3h3	800283	Van	Master IV	XDD		EU-RENAULT-MASTER-IV-VAN-L3H3-01	HIGH	L3H3封闭式货厢外廓。	READY
800956_platform_l2	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	电动Platform-cab L2H1。	READY
800956_platform_l3	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	电动Platform-cab L3H1。	READY
800956_single_l2	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	电动前驱单排底盘驾驶室L2。	READY
800956_single_l3	800956	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	电动前驱单排底盘驾驶室L3。	READY
800957_platform_l2	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	HIGH	电动Platform-cab L2H1。	READY
800957_platform_l3	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	HIGH	电动Platform-cab L3H1。	READY
800957_single_l2	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	HIGH	电动前驱单排底盘驾驶室L2。	READY
800957_single_l3	800957	Pickup	Master IV	XDD	2	EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	HIGH	电动前驱单排底盘驾驶室L3。	READY
59338	59338	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
128492	128492	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
15234	15234	Convertible	Megane III CC	EZ	2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
145693	145693	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
145694	145694	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
801426	801426	SUV	Megane E-Tech Electric		5	EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	HIGH		READY
100432_prefl	100432	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
100432_facelift	100432	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
11487	11487	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
11494	11494	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11485	11485	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
11490	11490	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
7881	7881	Convertible	Megane I Phase I	EA	2	EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	MEDIUM	生产终点位于1999改款交界月。	READY
15761	15761	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
15766	15766	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
7884_prefl	7884	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7884_facelift	7884	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
7882_prefl	7882	Convertible	Megane I Phase I	EA	2	EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7882_facelift	7882	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
7883_prefl	7883	Hatchback	Megane I Phase I	BA	5	EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
7883_facelift	7883	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
16578	16578	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
14166	14166	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11492	11492	Convertible	Megane I Phase II	EA	2	EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	HIGH		READY
11493	11493	Hatchback	Megane I Phase II	BA	5	EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	HIGH		READY
58075	58075	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
100433_prefl	100433	Sedan	Megane I Phase I	LA	4	EU-RENAULT-MEGANE-I-PHASE-I-SEDAN-4D-01	MEDIUM	跨越1999改款，分列改款前外廓。	READY
100433_facelift	100433	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	MEDIUM	跨越1999改款，分列改款后外廓。	READY
11488	11488	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11489	11489	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
15763	15763	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
15767	15767	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11481	11481	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
56041	56041	Sedan	Megane I Phase II	LA	4	EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	HIGH		READY
11486	11486	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11484	11484	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
15765	15765	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
16577	16577	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
14165	14165	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11483	11483	Coupe	Megane I Phase II	DA	3	EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	HIGH		READY
11479	11479	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11264	11264	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11480	11480	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11265	11265	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11266	11266	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
15764	15764	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
11267	11267	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
15768	15768	Wagon	Megane I Phase II	KA	5	EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	HIGH		READY
17724	17724	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17725	17725	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17726	17726	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
17727	17727	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
16916	16916	Hatchback	Megane II	CM	3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH		READY
17719	17719	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
16919	16919	Hatchback	Megane II	CM	3	EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	HIGH		READY
17718	17718	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
17728	17728	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18219	18219	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18784	18784	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18785	18785	Sedan	Megane II	LM	4	EU-RENAULT-MEGANE-II-SEDAN-4D-01	HIGH		READY
18790	18790	Hatchback	Megane II	BM	5	EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_14201-14300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-E-TECH-ELECTRIC-SUV-5D-01	4200	1768	1505	Renault Suisse Megane E-Tech Electric official price/spec sheet	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Megane_E-Tech_Electric_PL_d.pdf
EU-RENAULT-MEGANE-I-PHASE-I-HATCHBACK-5D-01	4129	1699	1420	Auto-Data Renault Megane I (BA)	https://www.auto-data.net/en/renault-megane-i-ba-generation-2152
EU-RENAULT-MEGANE-I-PHASE-II-HATCHBACK-5D-01	4164	1698	1420	Auto-Data Renault Megane I Phase II	https://www.auto-data.net/en/renault-megane-i-phase-ii-1999-generation-5577
EU-RENAULT-MEGANE-I-PHASE-II-CONVERTIBLE-2D-01	4082	1698	1368	Auto-Data Renault Megane I Cabriolet Phase II	https://www.auto-data.net/en/renault-megane-i-cabriolet-phase-ii-1999-generation-5579
EU-RENAULT-MEGANE-I-PHASE-I-CONVERTIBLE-2D-01	4028	1698	1368	Auto-Data Renault Megane I Cabriolet (EA)	https://www.auto-data.net/en/renault-megane-i-cabriolet-ea-generation-2156
EU-RENAULT-MEGANE-I-PHASE-II-SEDAN-4D-01	4436	1698	1420	Auto-Data Renault Megane I Classic Phase II	https://www.auto-data.net/en/renault-megane-i-classic-phase-ii-1999-generation-5584
EU-RENAULT-MEGANE-I-PHASE-I-SEDAN-4D-01	4440	1699	1420	Auto-Data Renault Megane I Classic (LA)	https://www.auto-data.net/en/renault-megane-i-classic-la-generation-2153
EU-RENAULT-MEGANE-I-PHASE-II-COUPE-3D-01	3967	1698	1366	Auto-Data Renault Megane I Coach Phase II	https://www.auto-data.net/en/renault-megane-i-coach-phase-ii-1999-generation-5576
EU-RENAULT-MEGANE-I-PHASE-II-WAGON-5D-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-generation-5586
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	4485	1811	1434	Renault Megane Coupe-Cabriolet official brochure; Auto-Data Renault Megane III CC	https://resource.digitaldealer.com.au/pdf/5444430215615c3e7030a1039769581.pdf;https://www.auto-data.net/en/renault-megane-iii-cc-generation-3773
EU-RENAULT-MEGANE-II-SEDAN-4D-01	4498	1777	1460	Automobile-Catalog Renault Megane Classic 2.0 16V; Auto-Data Renault Megane II Classic	https://www.automobile-catalog.com/car/2007/2954600/renault_megane_classic_2_0_16v.html;https://www.auto-data.net/en/renault-megane-ii-classic-1.5-dci-106hp-10543
EU-RENAULT-MEGANE-II-HATCHBACK-3D-01	4209	1777	1457	Renault Drive.Place Megane II 3-door	https://renault.drive.place/megane/ii/group_hatchback_3d/245016
EU-RENAULT-MEGANE-II-HATCHBACK-5D-01	4209	1777	1458	Automobile-Catalog Renault Megane 1.5 dCi 80; Carfolio Renault Megane II Hatchback 1.6 16V	https://www.automobile-catalog.com/car/2002/2953670/renault_megane_1_5_dci_80.html;https://www.carfolio.com/renault-megane-ii-hatchback-1.6-16v-96899
EU-RENAULT-MASTER-IV-VAN-L2H2-01	5685	2080	2500	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-VAN-L3H2-01	6315	2080	2500	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-VAN-L3H3-01	6315	2080	2780	Renault UK Master panel van official dimensions; Renault Master official e-brochure	https://business.renault.co.uk/master-range/master-panel-van.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-BUS-L3H3-01	6315	2080	2780	Renault All-New Master official passenger dimensions; Renault Master official e-brochure	https://renault.com.do/cars/master/dimensions.html;https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/van-ebrochures/MASTER-eBrochure.pdf.asset.pdf/84801569e7.pdf
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L2-FWD-01	5730	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-FWD-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-FWD-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L3-RWD-DRW-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-SINGLE-L4-RWD-DRW-01	6940	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L3-RWD-DRW-01	6360	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-DOUBLE-L4-RWD-DRW-01	6940	2080	2260	Renault Deutschland Master Fahrgestell official dimensions	https://geschaeftskunden.renault.de/master-modelluebersicht/fahrgestell.html
EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L2-FWD-01	5682	2080	2260	Renault UK Master Platform and Chassis Cab official dimensions	https://business.renault.co.uk/master-range/chassis-cab.html
EU-RENAULT-MASTER-IV-PICKUP-PLATFORM-L3-FWD-01	6312	2080	2260	Renault UK Master Platform and Chassis Cab official dimensions	https://business.renault.co.uk/master-range/chassis-cab.html
EU-RENAULT-MASTER-III-VAN-L3H2-RWD-SRW-01	6198	2070	2527	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H2-RWD-DRW-01	6198	2070	2549	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H3-RWD-SRW-01	6198	2070	2786	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L3H3-RWD-DRW-01	6198	2070	2815	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H2-RWD-SRW-01	6848	2070	2527	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H2-RWD-DRW-01	6848	2070	2557	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H3-RWD-SRW-01	6848	2070	2786	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-L4H3-RWD-DRW-01	6848	2070	2808	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L1H1-FWD-01	5048	2070	2307	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H1-FWD-01	5075	2070	2307	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L1H2-FWD-01	5048	2070	2500	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L1H2-FWD-01	5075	2070	2500	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L2H2-FWD-01	5548	2070	2499	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H2-FWD-01	5575	2070	2499	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L2H3-FWD-01	5548	2070	2749	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L2H3-FWD-01	5575	2070	2749	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L3H2-FWD-01	6198	2070	2488	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-FWD-01	6225	2070	2488	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-PREFL-L3H3-FWD-01	6198	2070	2744	Renault Master & Master Z.E. official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-FWD-01	6225	2070	2744	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H2-RWD-01	6225	2070	2549	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L3H3-RWD-01	6225	2070	2815	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H2-RWD-01	6875	2070	2557	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-VAN-FACELIFT-L4H3-RWD-01	6875	2070	2808	Renault Master official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-BUS-PREFL-L3H2-FWD-01	6198	2070	2496	Renault Master & Master Z.E. official passenger dimensions	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Master_BR_f.pdf
EU-RENAULT-MASTER-III-BUS-FACELIFT-L3H2-FWD-01	6225	2070	2496	Renault Master official brochure 2023	https://cdn.group.renault.com/ren/ma/ebrochure-2023/master/ct-mobile-master-21072023.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L2-SRW-01	5643	2070	2284	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-SRW-01	6293	2070	2276	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L3-DRW-01	6193	2070	2283	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-SINGLE-L4-DRW-01	6843	2070	2273	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L2-SRW-01	5643	2070	2295	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-SRW-01	6293	2070	2285	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L3-DRW-01	6193	2070	2301	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-DOUBLE-L4-DRW-01	6843	2070	2286	Renault Master official brochure October 2017—specific chassis dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L2-SRW-01	5670	2070	2284	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-SRW-01	6320	2070	2276	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L3-DRW-01	6220	2070	2283	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-SINGLE-L4-DRW-01	6870	2070	2273	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L2-SRW-01	5670	2070	2295	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-SRW-01	6320	2070	2285	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L3-DRW-01	6220	2070	2301	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-DOUBLE-L4-DRW-01	6870	2070	2286	Renault New Master official e-brochure—chassis dimensions	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H1-FWD-01	5530	2070	2270	Renault Master official brochure October 2017—platform cab dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L2H2-FWD-01	5530	2070	2469	Renault Master official brochure October 2017—platform cab dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H1-FWD-01	6180	2070	2264	Renault Master official brochure October 2017—platform cab dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-PREFL-PLATFORM-L3H2-FWD-01	6180	2070	2457	Renault Master official brochure October 2017—platform cab dimensions	https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H1-FWD-01	5557	2100	2270	Renault Master official brochure April 2022—platform cab dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L2H2-FWD-01	5557	2100	2463	Renault Master official brochure April 2022—platform cab dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H1-FWD-01	6207	2100	2264	Renault Master official brochure April 2022—platform cab dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
EU-RENAULT-MASTER-III-PICKUP-FACELIFT-PLATFORM-L3H2-FWD-01	6207	2100	2457	Renault Master official brochure April 2022—platform cab dimensions	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_14201-14300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf "https://www.diacfa.com/wp-content/uploads/RENAULT_MASTER_ENG.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（732 行）
- 累计尺寸组：dimension_groups_final.tsv（139 行）

