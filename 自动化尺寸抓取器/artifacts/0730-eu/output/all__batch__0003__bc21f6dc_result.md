# 任务：all 第 201-300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0003__bc21f6dc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 201-300 行

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
all 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-E-TRON-I-GE-SUV-S-01	4902	1976	1629
EU-AUDI-R8-II-4S-SPYDER-01	4426	1940	1244
EU-AUDI-TT-8S-COUPE-01	4177	1832	1353
EU-AUDI-TT-8S-ROADSTER-01	4177	1832	1355
EU-AUDI-TT-8S-RS-COUPE-01	4191	1832	1344
EU-AUDI-TT-8S-RS-ROADSTER-01	4191	1832	1346
EU-BMW-2-F22-COUPE-01	4432	1774	1418
EU-BMW-2-F22-COUPE-M240-01	4454	1774	1408
EU-BMW-2-F23-CONVERTIBLE-01	4432	1774	1413
EU-BMW-2-F23-CONVERTIBLE-M240-01	4454	1774	1403
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1608
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-340-SEDAN-01	4600	1765	1630
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-M550D-01	4962	1868	1467
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-M550D-01	4962	1868	1488
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498
EU-BMW-502-SEDAN-01	4730	1780	1530
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4065	1735	1476
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940
EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	4635	1865	1484
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-T-ROC-I-A11-SUV-01	4234	1819	1573
EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	4426	1809	1703
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4427	1809	1686
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	127	173	Jul 1989	Mar 1997	2024-03-01	143218
Ford USA	Windstar	3.0 V6	Kasten/Großraumlimousine	Frontantrieb	Benzin	109	148	Mar 1995	Jun 1998	2024-03-01	143238
Suzuki	Swace	1.8 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	90	122	Oct 2020	-	2024-03-01	143239
BMW	3	330 I	Kombi	Heckantrieb	Benzin	200	272	Mar 2007	Jun 2012	2024-03-01	143242
Fiat	Fiorino	1.6 IE	Großraumlimousine	Frontantrieb	Benzin	55	75	Oct 1993	May 2000	2024-03-01	143244
Fiat	Fiorino	1.4	Großraumlimousine	Frontantrieb	Benzin	49	67	Nov 1996	May 2000	2024-03-01	143245
Chrysler	Voyager iv van	3.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	128	174	Oct 2000	Jun 2007	2024-03-01	143246
Chrysler	Voyager iv van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	160	218	Oct 2000	Jun 2007	2024-03-01	143247
Chrysler	Voyager iv van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	160	218	Oct 2000	Jun 2007	2024-03-01	143248
DS	Ds	1.5 Bluehdi 110	Schrägheck	Frontantrieb	Diesel	81	110	Jan 2021	Dec 2022	2024-03-01	143251
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	180	245	Jan 2021	Apr 2024	2025-06-01	143253
Peugeot	2008 ii	1.5 Bluehdi 110	SUV	Frontantrieb	Diesel	81	110	Jan 2021	-	2024-03-01	143254
VW	Touareg	3.0 Ehybrid 4motion	SUV	Allrad	Benzin/Elektro	280	381	Nov 2020	-	2024-03-01	143255
VW	Touareg	3.0 R 4motion	SUV	Allrad	Benzin/Elektro	340	462	Sep 2020	-	2024-03-01	143256
VW	Tiguan	1.4 Ehybrid	SUV	Frontantrieb	Benzin/Elektro	180	245	Nov 2020	Apr 2024	2025-06-01	143258
Mitsubishi	Eclipse cross	Plug-in Hybrid 4WD	SUV	Allrad	Benzin/Elektro	138	188	Jan 2021	-	2024-03-01	143259
VW	Caddy v	1.5 TSI EVO	Kasten/Großraumlimousine	Frontantrieb	Benzin	84	114	Jan 2021	Nov 2024	2024-05-01	143260
Fiat	Tipo	1	Stufenheck	Frontantrieb	Benzin	74	101	Nov 2020	-	2025-06-01	143261
VW	Caddy v	1.5 TSI EVO	Großraumlimousine	Frontantrieb	Benzin	84	114	Jan 2021	Nov 2024	2024-05-01	143264
Audi	A3	40 TDI Quattro	Stufenheck	Allrad	Diesel	147	200	Dec 2020	-	2024-03-01	143265
Audi	A3	40 TDI Quattro	Schrägheck	Allrad	Diesel	147	200	Dec 2020	-	2024-03-01	143266
VW	Golf viii variant	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	96	131	Dec 2020	-	2024-03-01	143268
VW	Golf viii variant	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	110	150	Dec 2020	-	2024-03-01	143269
Ford	Fiesta vii van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	70	95	Dec 2019	-	2024-03-01	143270
Mercedes-benz	V-Klasse	V 300 CDI / D	Bus	Heckantrieb	Diesel	174	237	Jan 2021	-	2024-03-01	143274
Mercedes-benz	V-Klasse	V 300 CDI / D 4-matic	Bus	Allrad	Diesel	174	237	Jan 2021	-	2024-03-01	143279
Mercedes-benz	Marco polo camper	300 CDI	Bus	Heckantrieb	Diesel	174	237	Jan 2021	-	2024-03-01	143280
Mercedes-benz	Marco polo camper	300 CDI 4-matic	Bus	Allrad	Diesel	174	237	Jan 2021	-	2024-03-01	143281
Mercedes-benz	Vito tourer	124 CDI	Bus	Heckantrieb	Diesel	174	237	Jan 2021	-	2024-03-01	143282
Mercedes-benz	Vito tourer	124 CDI 4-matic	Bus	Allrad	Diesel	174	237	Jan 2021	-	2024-03-01	143283
Mercedes-benz	Vito mixto	124 CDI	Kasten	Heckantrieb	Diesel	174	237	Jan 2021	-	2024-03-01	143284
Mercedes-benz	Vito mixto	124 CDI 4-matic	Kasten	Allrad	Diesel	174	237	Jan 2021	-	2024-03-01	143285
Lamborghini	Sian fkp 37 roadster	6.5 Mhev AWD	Targa	Allrad	Benzin/Elektro	602	818	Sep 2020	-	2024-03-01	143287
NIO	Et7	EV Allrad	Stufenheck	Allrad	Elektro	480	653	Jan 2023	-	2024-03-01	143290
VW	Golf alltrack viii variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	147	200	Nov 2020	-	2026-07-01	143294
Donkervoort	D8	2.5 Gto-rs	Cabriolet	Heckantrieb	Benzin	284	386	Jan 2017	-	2024-03-01	143296
Donkervoort	D8	2.5 Gto-jd70	Cabriolet	Heckantrieb	Benzin	310	421	Jan 2020	-	2024-03-01	143297
BYD	Tang	EV Allrad	SUV	Allrad	Elektro	380	517	Aug 2020	-	2024-03-01	143298
Volvo	S60 iii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	299	407	May 2019	Dec 2022	2024-05-01	143303
Volvo	S90 ii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	299	407	Oct 2017	Dec 2022	2024-05-01	143304
Toyota	Proace	Electric	Bus	Frontantrieb	Elektro	100	136	Jan 2021	Dec 2023	2024-08-01	143314
Toyota	Proace verso	Electric	Bus	Frontantrieb	Elektro	100	136	Jan 2021	Dec 2023	2024-08-01	143315
Skoda	Favorit	1.3	Kasten/Kombi	Frontantrieb	Benzin	40	54	Oct 1990	Dec 1992	2024-03-01	143317
Skoda	Favorit	1.3	Kasten/Kombi	Frontantrieb	Benzin	44	60	Jan 1989	Aug 1995	2024-03-01	143318
KIA	Ceed	1.5 T-gdi	Schrägheck	Frontantrieb	Benzin	118	160	Jan 2021	-	2024-03-01	143332
KIA	Ceed	1.5 T-gdi	Kombi	Frontantrieb	Benzin	118	160	Jan 2021	-	2024-03-01	143333
KIA	Xceed	1.5 T-gdi	SUV	Frontantrieb	Benzin	118	160	Jan 2021	-	2024-03-01	143334
KIA	Proceed	1.5 T-gdi	Kombi	Frontantrieb	Benzin	118	160	Jan 2021	-	2024-03-01	143335
MG	Hs	1.5 EHS Hybrid	SUV	Frontantrieb	Benzin/Elektro	190	258	Dec 2020	-	2025-12-01	143339
Austin	Mini	850	Schrägheck	Frontantrieb	Benzin	25	34	Sep 1969	Oct 1985	2024-03-01	143342
VW	Id.3	Pure	Schrägheck	Heckantrieb	Elektro	110	150	Mar 2020	May 2023	2024-03-01	143350
Fiat	Tempra	1.4	Kasten/Kombi	Frontantrieb	Benzin	54	73	Apr 1991	Jun 1993	2024-03-01	143380
Fiat	Tempra	1.6	Kasten/Kombi	Frontantrieb	Benzin	57	77	Apr 1991	Jun 1993	2024-03-01	143381
Fiat	Tempra	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	48	65	Jun 1993	Jul 1996	2024-03-01	143382
Mercedes-benz	S-Klasse	S 500 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	320	435	Sep 2020	-	2024-03-01	143384
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	270	367	Oct 2020	-	2024-03-01	143385
Citroën	Ami	Electric	Schrägheck	Frontantrieb	Elektro	6	8	Apr 2020	-	2024-03-01	143386
Mercedes-benz	S-Klasse	S 350 D	Stufenheck	Heckantrieb	Diesel	210	286	Sep 2020	-	2024-03-01	143387
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	210	286	Sep 2020	-	2024-03-01	143388
Mercedes-benz	S-Klasse	S 400 D 4-matic	Stufenheck	Allrad	Diesel	243	330	Sep 2020	-	2024-03-01	143389
Citroën	C4 iii	1.2 Puretech 155	Schrägheck	Frontantrieb	Benzin	114	155	Jan 2021	-	2024-03-01	143390
Mercedes-benz	G-Klasse	G 300 Diesel	Geländewagen geschlossen	Allrad	Diesel	83	113	Sep 1993	Aug 1994	2024-03-01	143391
Mercedes-benz	G-Klasse	G 300 Diesel	Geländewagen offen	Allrad	Diesel	83	113	Sep 1993	Aug 1994	2024-03-01	143392
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	421	573	Sep 2019	Apr 2026	2026-06-01	143399
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	599	815	Sep 2020	Apr 2026	2026-06-01	143400
Volvo	S60 iii	B3 Mhev	Stufenheck	Frontantrieb	Benzin/Elektro	120	163	Mar 2020	Dec 2023	2026-02-01	143402
Audi	R8	5.2 FSI	Cabriolet	Allrad	Benzin	419	570	Jul 2012	Jul 2015	2024-03-01	143409
BMW	5	M5 CS	Stufenheck	Allrad	Benzin	467	635	Mar 2021	Feb 2022	2024-03-01	143416
Ford	Fiesta vii	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	114	155	Jan 2021	-	2024-03-01	143418
Ford	Fiesta vii	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	92	125	Jan 2021	-	2024-03-01	143419
Ford	Focus iv	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	92	125	Jan 2021	Nov 2025	2026-02-01	143421
Skoda	Octavia	1.5 TSI E-tec	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Nov 2020	-	2024-03-01	143425
Skoda	Octavia	1.5 TSI E-tec	Kombi	Frontantrieb	Benzin/Elektro	110	150	Nov 2020	-	2024-03-01	143426
Audi	R8	5.2 FSI	Cabriolet	Allrad	Benzin	404	550	Jul 2012	Jul 2015	2025-06-01	143428
Volvo	S60 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	183	249	Jan 2013	Jan 2016	2024-03-01	143429
Volvo	V90 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Diesel/Elektro	145	197	Oct 2020	-	2024-03-01	143433
Fiat	Ducato	E-ducato	Kasten	Frontantrieb	Elektro	90	122	Dec 2020	Oct 2023	2024-05-01	143447
Ford	Kuga ii	1.5 Ecoboost E85	SUV	Frontantrieb	Ethanol	110	150	Feb 2019	Nov 2019	2024-03-01	143449
Volvo	Xc60 ii	T8 Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	246	334	May 2021	Dec 2022	2024-05-01	143450
BMW	2	220 I Xdrive	Coupe	Allrad	Benzin	131	178	Mar 2021	-	2024-03-01	143451
Volvo	Xc40	T3	SUV	Frontantrieb	Benzin	110	150	Dec 2020	Dec 2022	2024-05-01	143452
BMW	3	320 E Plug-in-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	150	204	Mar 2021	-	2024-03-01	143457
BMW	5	520 E Plug-in-hybrid	Kombi	Heckantrieb	Benzin/Elektro	150	204	Mar 2021	May 2022	2024-03-01	143459
Tesla	Model s	EV AWD	Schrägheck	Allrad	Elektro	421	573	Sep 2020	Apr 2026	2026-06-01	143463
Audi	A6 allroad c8	55 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	253	344	Nov 2020	-	2025-06-01	143472
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	366	498	Dec 2020	-	2024-03-01	143474
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	225	306	Feb 2019	-	2024-03-01	143475
Tesla	Model 3	EV	Stufenheck	Heckantrieb	Elektro	239	325	Dec 2019	-	2024-03-01	143476
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	360	490	Jun 2019	-	2024-03-01	143477
Tesla	Model 3	EV Performance AWD	Stufenheck	Allrad	Elektro	377	513	Dec 2019	-	2024-03-01	143478
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	355	482	Feb 2019	-	2024-03-01	143479
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	361	491	Dec 2019	-	2024-03-01	143480
VW	T-Roc	2.0 TDI SCR	SUV	Frontantrieb	Diesel	85	116	Nov 2020	-	2025-06-01	143481
Mercedes-benz	Eqa	EQA 250	SUV	Frontantrieb	Elektro	140	190	Feb 2021	-	2024-03-01	143485
Renault	Megane iv	1.0 TCE 115	Schrägheck	Frontantrieb	Benzin	84	114	Oct 2020	-	2024-03-01	143488
Audi	Tt	TTS Tfsi Quattro	Cabriolet	Allrad	Benzin	235	320	Nov 2020	-	2025-04-01	143490
Mercedes-benz	E-Klasse	E 300 D 4-matic	Kombi	Allrad	Diesel/Elektro	195	265	Jan 2021	Oct 2023	2024-03-01	143491
Audi	E-Tron	RS Quattro	Stufenheck	Allrad	Elektro	440	599	Feb 2021	Jul 2024	2026-07-01	143492
Audi	A6 c8 avant	S6 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	253	344	Nov 2020	-	2024-03-01	143493
Mercedes-benz	E-Klasse	E 300 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	195	265	Jan 2021	Oct 2023	2024-03-01	143498


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **48 个 Ktype 映射**，其中复用跨批次既有尺寸组 10 个，首次创建尺寸组 29 个。
* 已按改款、车身形式和驱动造成的高度差异拆分：Tiguan facelift FWD/4MOTION、Tesla Model 3 改款前/后分别建组。
* NIO ET7 使用官方用户手册确认三维，其中宽度明确为不含后视镜；Audi A3、Touareg、Tiguan、Volvo、Tesla 等使用官方或具体版本规格页闭合。([蔚来][1])
* 长轴、车顶高度或多种商用车身尚未闭合的记录未猜测派生，留待后续集中处理。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：48
* 待闭合 Ktype：52
* 当前已引用尺寸组：39

  * 本轮首次创建：29
  * 复用既有组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143239	143239	Wagon	Swace I		5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
143253	143253	SUV	Tiguan II Facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
143254	143254	SUV	2008 II	P24	5	EU-PEUGEOT-2008-II-P24-SUV-01	HIGH		READY
143255	143255	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PREFL-01	HIGH		READY
143256	143256	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PREFL-01	HIGH	R eHybrid与同代标准轴距外廓一致。	READY
143258	143258	SUV	Tiguan II Facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-FWD-01	HIGH		READY
143259	143259	SUV	Eclipse Cross I Facelift		5	EU-MITSUBISHI-ECLIPSE-CROSS-I-FACELIFT-SUV-01	HIGH		READY
143261	143261	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	356四门轿车外廓。	READY
143265	143265	Sedan	A3 8Y	8Y	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
143266	143266	Hatchback	A3 8Y	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
143270	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	三门厢式衍生车，复用相同三门外廓。	READY
143287	143287	Convertible	Sián Roadster		2	EU-LAMBORGHINI-SIAN-ROADSTER-CONVERTIBLE-01	HIGH	Roadster两门开放式外廓。	READY
143290	143290	Sedan	ET7 I		4	EU-NIO-ET7-I-SEDAN-01	HIGH		READY
143296	143296	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	GTO-RS两门开放式外廓。	READY
143297	143297	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	GTO-JD70两门开放式外廓。	READY
143298	143298	SUV	Tang II Facelift		5	EU-BYD-TANG-II-FACELIFT-SUV-01	HIGH		READY
143303	143303	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
143304	143304	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
143332	143332	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-HATCHBACK-01	HIGH		READY
143333	143333	Wagon	Ceed III Sportswagon	CD	5	EU-KIA-CEED-III-WAGON-01	HIGH		READY
143334	143334	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-SUV-01	HIGH		READY
143335	143335	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-WAGON-01	HIGH	五门shooting-brake外廓。	READY
143339	143339	SUV	HS I Facelift		5	EU-MG-HS-I-FACELIFT-SUV-01	HIGH		READY
143350	143350	Hatchback	ID.3 I Pre-facelift	E11	5	EU-VW-ID3-I-HATCHBACK-PREFL-01	HIGH	2020-2023改款前五门车身。	READY
143386	143386	Hatchback	Ami I		2	EU-CITROEN-AMI-I-HATCHBACK-01	HIGH	双门轻型四轮车外廓。	READY
143390	143390	Hatchback	C4 III Phase I	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	按输入Schrägheck归一为Hatchback。	READY
143399	143399	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH		READY
143400	143400	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH		READY
143402	143402	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
143425	143425	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
143426	143426	Wagon	Octavia IV Combi	NX	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
143433	143433	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
143451	143451	Coupe	2 Series G42	G42	2	EU-BMW-2-G42-COUPE-01	MEDIUM	输入220i xDrive动力标签与欧洲常见配置不一致；物理车身按G42 Coupe闭合。	READY
143452	143452	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
143459	143459	Wagon	5 Series G31 Facelift	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门旅行车。	READY
143463	143463	Hatchback	Model S I Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
143474	143474	Sedan	Model 3 I Facelift 2020		4	EU-TESLA-MODEL-3-I-SEDAN-FACELIFT-2020-01	HIGH	2020改款后四门外廓。	READY
143475	143475	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143476	143476	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143477	143477	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143478	143478	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143479	143479	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143480	143480	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143481	143481	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
143485	143485	SUV	EQA I	H243	5	EU-MERCEDES-BENZ-EQA-I-H243-SUV-01	HIGH		READY
143488	143488	Hatchback	Megane IV Phase II		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	Phase II五门掀背车。	READY
143492	143492	Sedan	e-tron GT I	F83	4	EU-AUDI-E-TRON-GT-I-RS-SEDAN-01	HIGH	RS四门GT外廓。	READY
143493	143493	Wagon	S6 C8 Avant	4K5	5	EU-AUDI-S6-C8-AVANT-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SWACE-I-WAGON-01	4655	1790	1460	Auto-Data Suzuki Swace I 1.8 Hybrid CVT	https://www.auto-data.net/en/suzuki-swace-i-1.8-122hp-hybrid-cvt-41312
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	4509	1839	1684	Auto-Data Volkswagen Tiguan II facelift 2.0 TSI 4MOTION	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-2.0-tsi-245hp-4motion-dsg-44395
EU-PEUGEOT-2008-II-P24-SUV-01	4300	1770	1550	Auto-Data Peugeot 2008 II 1.5 BlueHDi 110	https://www.auto-data.net/en/peugeot-2008-ii-1.5-bluehdi-110hp-47192
EU-VW-TOUAREG-III-CR-SUV-PREFL-01	4878	1984	1717	Auto-Data Volkswagen Touareg III eHybrid; Auto-Data Volkswagen Touareg III R eHybrid	https://www.auto-data.net/en/volkswagen-touareg-iii-cr-3.0-v6-tsi-381hp-ehybrid-4motion-tiptronic-41524;https://www.auto-data.net/en/volkswagen-touareg-iii-cr-r-3.0-v6-tsi-462hp-ehybrid-4motion-tiptronic-41523
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-FWD-01	4509	1839	1675	Auto-Data Volkswagen Tiguan II facelift 1.4 eHybrid	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-1.4-tsi-245hp-ehybrid-dsg-41793
EU-MITSUBISHI-ECLIPSE-CROSS-I-FACELIFT-SUV-01	4545	1805	1685	Mitsubishi Eclipse Cross official specifications	https://www.mitsubishi-motors.co.jp/lineup/eclipse-cross/spec/spe_02.html
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425	Audi A3 2020 official facts and figures	https://www.audi.com/de/dynamisch-wie-nie-der-neue-audi-a3-sportback-und-die-neue-a3-limousine-2020-12974/fakten-12977
EU-AUDI-A3-8Y-SPORTBACK-5D-01	4343	1816	1449	Audi A3 2020 official facts and figures	https://www.audi.com/de/dynamisch-wie-nie-der-neue-audi-a3-sportback-und-die-neue-a3-limousine-2020-12974/fakten-12977
EU-LAMBORGHINI-SIAN-ROADSTER-CONVERTIBLE-01	4979	2080	1158	Auto-Data Lamborghini Sián Roadster	https://www.auto-data.net/en/lamborghini-sian-roadster-generation-9600
EU-NIO-ET7-I-SEDAN-01	5101	1987	1509	NIO ET7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET7/index.html
EU-BYD-TANG-II-FACELIFT-SUV-01	4870	1950	1725	Auto-Data BYD Tang II facelift EV 517 hp AWD	https://www.auto-data.net/en/byd-tang-ii-facelift-2021-ev-86.4-kwh-517hp-awd-46808
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Auto-Data Volvo S60 III generation	https://www.auto-data.net/en/volvo-s60-iii-generation-6352
EU-KIA-CEED-III-HATCHBACK-01	4310	1800	1447	Automobile-Catalog 2021 Kia Ceed 1.5 T-GDI 160	https://www.automobile-catalog.com/car/2021/3002660/kia_ceed_1_5_t-gdi_160.html
EU-KIA-CEED-III-WAGON-01	4600	1800	1465	Automobile-Catalog 2021 Kia Ceed Sportswagon 1.5 T-GDI 160	https://www.automobile-catalog.com/car/2021/3002780/kia_ceed_sportswagon_1_5_t-gdi_160.html
EU-KIA-XCEED-I-SUV-01	4395	1826	1495	Auto-Data Kia XCeed 1.5 T-GDI 160	https://www.auto-data.net/en/kia-xceed-1.5-t-gdi-160hp-44840
EU-KIA-PROCEED-III-WAGON-01	4605	1800	1422	Auto-Data Kia ProCeed III 1.5 T-GDI 160	https://www.auto-data.net/en/kia-proceed-iii-facelift-2021-1.5-t-gdi-160hp-44812
EU-MG-HS-I-FACELIFT-SUV-01	4574	1876	1685	Auto-Data MG HS I facelift EHS Plug-in Hybrid	https://www.auto-data.net/en/mg-hs-i-facelift-2020-1.5-t-gdi-258hp-plug-in-hybrid-automatic-48931
EU-VW-ID3-I-HATCHBACK-PREFL-01	4261	1809	1568	EV Database Volkswagen ID.3 1st	https://ev-database.org/car/1300/Volkswagen-ID3-1st
EU-CITROEN-AMI-I-HATCHBACK-01	2410	1390	1525	Auto-Data Citroën Ami Electric	https://www.auto-data.net/en/citroen-ami-electric-model-3328
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Auto-Data Citroën C4 III 1.2 PureTech 155	https://www.auto-data.net/en/citroen-c4-iii-phase-i-2020-1.2-puretech-155hp-automatic-42198
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470	Auto-Data Skoda Octavia IV 1.5 TSI e-TEC	https://www.auto-data.net/en/skoda-octavia-iv-1.5-tsi-evo-e-tec-150hp-mild-hybrid-dsg-38015
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468	Auto-Data Skoda Octavia IV Combi 1.5 TSI e-TEC	https://www.auto-data.net/en/skoda-octavia-iv-combi-1.5-tsi-evo-e-tec-150hp-mild-hybrid-dsg-38025
EU-BMW-2-G42-COUPE-01	4537	1838	1390	Auto-Data BMW 2 Series Coupe G42 220i	https://www.auto-data.net/en/bmw-2-series-coupe-g42-220i-184hp-steptronic-43834
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Auto-Data Volvo XC40 T3 163	https://www.auto-data.net/en/volvo-xc40-1.5-t3-163hp-40921
EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	4694	1849	1443	Auto-Data Tesla Model 3 pre-facelift generation	https://www.auto-data.net/en/tesla-model-3-generation-6100
EU-TESLA-MODEL-3-I-SEDAN-FACELIFT-2020-01	4694	1849	1443	Auto-Data Tesla Model 3 facelift 2020 generation	https://www.auto-data.net/en/tesla-model-3-facelift-2020-generation-8587
EU-MERCEDES-BENZ-EQA-I-H243-SUV-01	4463	1834	1620	Auto-Data Mercedes-Benz EQA H243 EQA 250	https://www.auto-data.net/en/mercedes-benz-eqa-h243-eqa-250-69.7-kwh-190hp-42117
EU-AUDI-E-TRON-GT-I-RS-SEDAN-01	4989	1964	1396	Automobile-Catalog 2021 Audi RS e-tron GT	https://www.automobile-catalog.com/car/2021/3006515/audi_rs_e-tron_gt.html
EU-AUDI-S6-C8-AVANT-WAGON-01	4954	1886	1481	Automobile-Catalog 2021 Audi S6 Avant TDI	https://www.automobile-catalog.com/car/2021/3005840/audi_s6_avant_tdi.html
```

## 下一步优先处理

1. 集中拆分 Mercedes-Benz V-Class、Marco Polo、Vito Tourer/Mixto 的轴距、车顶和乘用/厢式边界。
2. 处理 VW Caddy V、Toyota Proace Electric 和 Fiat E-Ducato 的标准轴距、加长轴及不同车顶。
3. 再闭合 Pontiac Trans Sport、Ford Windstar、Chrysler Voyager、Fiat Fiorino 等旧款 MPV/Van。
4. 最后处理 S-Class、G-Class、R8、Fiesta Active、Focus Active 等改款或特殊外观版本。

推进信号：CONTINUE

[1]: https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET7/index.html "https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET7/index.html"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **9 条 READY 映射**，闭合 **8 个 Ktype**；其中 `143242` 因 E91 改款前后长度不同拆为两个物理分支。
* 首次创建 5 个尺寸组：Golf VIII Variant、BMW M5 CS、BMW G21 320e xDrive Touring、Ford Kuga II facelift、Mercedes-Benz E-Class S213 facelift。
* 复用 3 个既有尺寸组：BMW E91 改款前、BMW E91 改款后、Volvo XC60 II。
* Golf Variant、BMW M5 CS、BMW G21、Kuga 和 E-Class Estate 的三维均由厂商官方规格或官方 brochure 闭合，宽度采用不含后视镜口径。([volkswagen-newsroom.com][1])
* XC60 Polestar Engineered 未发现形成独立车身外廓的证据，继续复用既有 XC60 II 尺寸组。([沃尔沃汽车媒体][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：56
* READY 映射：57
* PENDING Ktype：44
* 当前已引用尺寸组：47
* 本轮首次创建尺寸组：5
* 本轮新增复用既有尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143242_prefl	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
143242_facelift	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
143268	143268	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
143269	143269	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
143416	143416	Sedan	M5 F90 CS	F90	4	EU-BMW-5-F90-M5-CS-SEDAN-01	HIGH		READY
143449	143449	SUV	Kuga II Facelift		5	EU-FORD-KUGA-II-SUV-FACELIFT-01	HIGH		READY
143450	143450	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	MEDIUM	Polestar Engineered未形成已确认的独立外廓分支。	READY
143457	143457	Wagon	3 Series G21 Pre-facelift	G21	5	EU-BMW-3-G21-WAGON-PREFL-PHEV-XDRIVE-01	HIGH		READY
143491	143491	Wagon	E-Class S213 Facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VIII-VARIANT-WAGON-01	4633	1789	1498	Volkswagen Golf Variant official design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-variant-and-golf-alltrack-international-media-drive-6540/design-and-dimensions-6543
EU-BMW-5-F90-M5-CS-SEDAN-01	5001	1903	1468	BMW M5 CS official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0325152EN/471027
EU-FORD-KUGA-II-SUV-FACELIFT-01	4531	1838	1689	Ford Kuga official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Kuga.pdf
EU-BMW-3-G21-WAGON-PREFL-PHEV-XDRIVE-01	4709	1827	1442	BMW 320e xDrive Touring official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0325532EN/471539
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Mercedes-Benz E-Class Estate official brochure	https://uat-msl-21.clients.cemacdigital.com/assets/1/product-brochures/mercedes-benz/e-class-estate-brochure.pdf
```

## 下一步优先处理

1. 集中拆分 VW Caddy V、Toyota Proace、Mercedes-Benz V-Class、Marco Polo 和 Vito 的轴距、车顶及乘用/厢式分支。
2. 闭合 Mercedes-Benz S-Class W223/V223 的短轴与长轴 Ktype 边界。
3. 处理 Fiat E-Ducato 的长度、轴距和车顶高度组合。
4. 再处理 Audi R8 Spyder、Audi TT Roadster及旧款 Pontiac、Ford、Chrysler MPV。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/the-new-golf-variant-and-golf-alltrack-international-media-drive-6540/design-and-dimensions-6543 "Design and dimensions | Volkswagen Newsroom"
[2]: https://www.media.volvocars.com/ca/en-ca/media/pressreleases/230382/volvo-cars-and-polestar-launch-new-polestar-engineered-electrified-performance-offer?utm_source=chatgpt.com "Volvo Cars and Polestar launch new Polestar Engineered electrified performance offer - Volvo Cars of Canada Media Newsroom"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 **11 条 READY 映射**，闭合 DS 3 Crossback、Mercedes-Benz S-Class V223、Audi R8 Spyder、Audi TTS Roadster、Volvo S60 II 和 Mercedes-Benz E-Class W213。
* 5 个 S-Class Ktype 均确认属于长轴距 V223，并按各自明确的车身子代码映射至同一尺寸组；尺寸采用奔驰官方公布的长轴车身外廓。([Carparts Onlineshop][1])
* 两个 Audi R8 Ktype 均为第一代改款 V10 Spyder，官方尺寸图确认三维为 `4440 × 1904 × 1244 mm`。
* DS 3 Crossback、TTS Roadster 和 E 300 d 4MATIC Sedan 的门数、代际及不含后视镜宽度已闭合。([DieselFixNeuss][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：67
* READY 映射：68
* PENDING Ktype：33
* 当前已引用尺寸组：53
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143251	143251	Hatchback	DS 3 Crossback I		5	EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	HIGH		READY
143384	143384	Sedan	S-Class V223	223.163	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143385	143385	Sedan	S-Class V223	223.161	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143387	143387	Sedan	S-Class V223	223.130	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143388	143388	Sedan	S-Class V223	223.131	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143389	143389	Sedan	S-Class V223	223.133	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143409	143409	Convertible	R8 I 42 Facelift		2	EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	HIGH		READY
143428	143428	Convertible	R8 I 42 Facelift		2	EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	HIGH		READY
143429	143429	Sedan	S60 II Facelift	134	4	EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	HIGH		READY
143490	143490	Convertible	TTS 8S Facelift	8S	2	EU-AUDI-TT-8S-FACELIFT-TTS-ROADSTER-01	HIGH		READY
143498	143498	Sedan	E-Class W213 Facelift	213.019	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	4118	1791	1534	DS Automobiles DS 3 Crossback official dimensions	https://www.media.stellantis.com/uk-en/ds/press/ds-3-crossback-icon-of-high-tech-style
EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	5289	1954	1503	Mercedes-Benz S-Class Long V223 official vehicle dimensions	https://www.mercedes-benz-mena.com/ksa/en/services/manuals/s-class-saloon-long-2026-02-v223-mbux/vehicle-data/vehicle-dimensions
EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	4440	1904	1244	Audi R8 official UK pricing and specification guide	https://press.audi.co.uk/assets/documents/original/24231-AudiUK00001684AudiR8PricingandSpecification.pdf
EU-AUDI-TT-8S-FACELIFT-TTS-ROADSTER-01	4199	1832	1341	Auto-Data Audi TTS Roadster 8S facelift 320	https://www.auto-data.net/en/audi-tts-roadster-8s-facelift-2018-2.0-tfsi-320hp-quattro-s-tronic-50560
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift E 300 d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43736
```

## 下一步优先处理

1. 集中拆分 V-Class、Marco Polo、Vito Tourer 和 Vito Mixto 的轴距、车顶及乘用/厢式外廓。
2. 闭合 Caddy V、Proace Electric和 E-Ducato 的长度及车顶组合。
3. 处理 Pontiac Trans Sport、Ford Windstar、Chrysler Voyager、Fiat Fiorino等剩余旧款 MPV/Van。

推进信号：CONTINUE

[1]: https://www.carparts-onlineshop.com/amfile/file/download/file/673/product/42423/?utm_source=chatgpt.com "Linked vehicles"
[2]: https://dieselfixneuss.de/en/products/bosch-injector-445110954-for-fiat-ds-citreon-ford-opel-toyota-peugeot?srsltid=AfmBOopu1fno8GKiIbvxAE1ZNVgiDwyvrbelXE0d-TTqqeGOQpVazLpj&utm_source=chatgpt.com "Bosch injector 445110954 for Fiat, DS, Citreon, Ford, Opel, ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增 **15 条 READY 映射**，闭合 **14 个 Ktype**。
* `143391` 确认同时覆盖 W463 短轴三门和长轴五门封闭车身，拆分为两个派生 `id`；`143392` 对应短轴双门 Cabriolet。([Ultimate Specs][1])
* Golf VIII Alltrack、Fiesta Active、Focus Active 和 Audi A6 allroad C8 已按各自独立外廓建组，不复用普通 Variant、Fiesta、Focus 或 A6 Avant 尺寸。([汽车数据网][2])
* Skoda Favorit Forman、Austin Mini 和 Fiat Tempra SW 的发动机差异不改变外廓，同车型 Ktype 复用对应尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：81
* READY 映射：83
* PENDING Ktype：19
* 当前已引用尺寸组：63
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143294	143294	Wagon	Golf VIII Alltrack	CG5	5	EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	HIGH	Alltrack抬高旅行车外廓。	READY
143317	143317	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	HIGH	Forman及其厢式衍生车共用外廓。	READY
143318	143318	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	MEDIUM	Forman及其厢式衍生车共用外廓。	READY
143342	143342	Hatchback	Classic Mini		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-01	MEDIUM	覆盖Mk II末期及后续经典Mini，外廓尺寸一致。	READY
143380	143380	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143381	143381	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143382	143382	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143391_swb	143391	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	HIGH	短轴三门封闭车身。	READY
143391_lwb	143391	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH	长轴五门封闭车身。	READY
143392	143392	Convertible	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-SWB-01	HIGH	短轴双门开放式车身。	READY
143418	143418	Hatchback	Fiesta VII Active		5	EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143419	143419	Hatchback	Fiesta VII Active		5	EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143421	143421	Hatchback	Focus IV Active		5	EU-FORD-FOCUS-IV-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143472	143472	Wagon	A6 allroad C8		5	EU-AUDI-A6-C8-ALLROAD-WAGON-01	HIGH	Allroad抬高旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	4639	1795	1510	Auto-Data Volkswagen Golf VIII Alltrack 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-golf-viii-alltrack-2.0-tdi-200hp-4motion-dsg-41835
EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	4160	1620	1425	Auto-Data Skoda Favorit Forman 785 1.3	https://www.auto-data.net/en/skoda-favorit-forman-785-1.3-135-e-54hp-14291
EU-AUSTIN-MINI-CLASSIC-HATCHBACK-01	3054	1410	1346	Automobile-Catalog 1969 Austin Mini 850 Mk II; Automobile-Catalog 1969 Mini 850 Mk III	https://www.automobile-catalog.com/car/1969/256370/austin_mini_850_mk_ii.html;https://www.automobile-catalog.com/car/1969/1705160/mini_850.html
EU-FIAT-TEMPRA-159-WAGON-01	4472	1695	1500	Automobile-Catalog 1991 Fiat Tempra S.W.	https://www.automobile-catalog.com/car/1991/719255/fiat_tempra_s__w__2_0_i_e__sx_automatic.html
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	4180	1690	1931	UltimateSpecs Mercedes-Benz G-Class SWB W463 300 Diesel	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2635/Mercedes-Benz-G-Class-SWB-%28W463%29-300-Diesel.html
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4630	1690	1935	UltimateSpecs Mercedes-Benz G-Class LWB W463 300 Diesel	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2655/Mercedes-Benz-G-Class-LWB-%28W463%29-300-Diesel.html
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-SWB-01	4225	1690	1942	UltimateSpecs Mercedes-Benz G-Class SWB W463 300 Diesel Cabrio	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2646/Mercedes-Benz-G-Class-SWB-%28W463%29-300-Diesel-Cabrio.html
EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	4068	1756	1498	Ford Fiesta official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Fiesta.pdf
EU-FORD-FOCUS-IV-ACTIVE-HATCHBACK-01	4397	1844	1502	Ford Focus official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
EU-AUDI-A6-C8-ALLROAD-WAGON-01	4951	1902	1497	Audi A6 allroad 55 TDI official technical data; Automobile-Catalog Audi A6 allroad 55 TDI MHEV	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1179/file_en/be073dab2b00611d12009596d727db4f92159435/eTD-Audi-A6-allroad-quattro-55-TDI-tiptronic-253kW-MHEV_240613.pdf?1718367298=&disposition=attachment;https://www.automobile-catalog.com/car/2020/3005750/audi_a6_allroad_quattro_55_tdi_mhev.html
```

## 下一步优先处理

1. VW Caddy V 的标准车身、Maxi 长轴及乘用/厢式边界。
2. Mercedes-Benz V-Class、Marco Polo、Vito Tourer 与 Vito Mixto 的紧凑、长轴和超长轴分支。
3. Toyota Proace、Proace Verso Electric 与 Fiat E-Ducato 的长度和车顶组合。
4. 最后闭合 Pontiac Trans Sport、Ford Windstar、Chrysler Voyager IV 与旧款 Fiat Fiorino。

推进信号：CONTINUE

[1]: https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2635/Mercedes-Benz-G-Class-SWB-%28W463%29-300-Diesel.html "Mercedes Benz G Class SWB (W463) 300 Diesel Specs, Performance, Comparisons"
[2]: https://www.auto-data.net/en/volkswagen-golf-viii-alltrack-2.0-tdi-200hp-4motion-dsg-41835 "Volkswagen Golf VIII Alltrack 2.0 TDI (200 Hp) 4MOTION DSG | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/skoda-favorit-forman-785-1.3-135-e-54hp-14291 "Skoda Favorit Forman (785) 1.3 (135 E) (54 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 机械重算修正上一轮进度：上一轮实际已闭合 **80 个 Ktype**，不是 81 个。
* 本轮闭合 **12 个 Ktype**，新增 **28 条 READY 映射**。
* Caddy V 按厢式/乘用及标准轴距/Maxi 长轴拆成四种外廓；官方资料同时确认 1.5 TSI 存在标准轴距和 Maxi 版本。([Cordwallis Group][1])
* V 300 d/4MATIC 按 Long、Extra Long 拆分；Vito Tourer 与 Mixto 按 L1、L2、L3 拆分，并复用相同外部三维组。
* Proace Electric 与 Proace Verso Electric 直接复用跨批次已有 Medium、Long 乘用尺寸组，没有重复建组。
* E-Ducato 暂未落盘：官方资料显示其高度同时受车顶、47/79 kWh 电池和 3.5/4.25 吨等级影响，不能用普通 Ducato 的单一高度代替。([Rea][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：92
* READY 映射：110
* PENDING Ktype：8
* 当前已引用尺寸组：75
* 本轮首次创建尺寸组：10
* 本轮新增复用跨批次既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143260_van_swb	143260	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-SWB-01	MEDIUM	标准轴距厢式外廓。	READY
143260_mpv_swb	143260	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	MEDIUM	标准轴距乘用外廓。	READY
143260_van_lwb	143260	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-LWB-01	MEDIUM	Maxi长轴厢式外廓。	READY
143260_mpv_lwb	143260	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	MEDIUM	Maxi长轴乘用外廓。	READY
143264_swb	143264	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	HIGH	标准轴距乘用外廓。	READY
143264_lwb	143264	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	HIGH	Maxi长轴乘用外廓。	READY
143274_long	143274	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	长轴乘用外廓。	READY
143274_extralong	143274	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	HIGH	超长轴乘用外廓。	READY
143279_long	143279	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	长轴四驱乘用外廓。	READY
143279_extralong	143279	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	HIGH	超长轴四驱乘用外廓。	READY
143280	143280	MPV	Marco Polo W447 Facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	MEDIUM	长轴升顶露营车外廓。	READY
143281	143281	MPV	Marco Polo W447 Facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	MEDIUM	长轴四驱升顶露营车外廓。	READY
143282_l1	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴乘用外廓。	READY
143282_l2	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴乘用外廓。	READY
143282_l3	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴乘用外廓。	READY
143283_l1	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴四驱乘用外廓。	READY
143283_l2	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴四驱乘用外廓。	READY
143283_l3	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴四驱乘用外廓。	READY
143284_l1	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴Mixto外廓。	READY
143284_l2	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴Mixto外廓。	READY
143284_l3	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴Mixto外廓。	READY
143285_l1	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴四驱Mixto外廓。	READY
143285_l2	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴四驱Mixto外廓。	READY
143285_l3	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴四驱Mixto外廓。	READY
143314_medium	143314	MPV	Proace II	K0	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	MEDIUM	Medium电动乘用外廓。	READY
143314_long	143314	MPV	Proace II	K0	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	MEDIUM	Long电动乘用外廓。	READY
143315_medium	143315	MPV	Proace Verso II	K0	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium电动乘用外廓。	READY
143315_long	143315	MPV	Proace Verso II	K0	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long电动乘用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CADDY-V-VAN-SWB-01	4500	1855	1856	Volkswagen Caddy Cargo official brochure	https://www.cordwallis.com/wp-content/uploads/Caddy-Cargo-brochure-May-2021.pdf
EU-VW-CADDY-V-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy and Caddy Life official brochure	https://www.vwpress.co.uk/assets/documents/original/30530-caddylifebrochure.pdf
EU-VW-CADDY-V-VAN-LWB-01	4853	1855	1860	Volkswagen Caddy Cargo official brochure	https://www.cordwallis.com/wp-content/uploads/Caddy-Cargo-brochure-May-2021.pdf
EU-VW-CADDY-V-MPV-LWB-01	4853	1855	1800	Volkswagen Caddy and Caddy Life official brochure	https://www.vwpress.co.uk/assets/documents/original/30530-caddylifebrochure.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz V-Class and Marco Polo official brochure	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	5370	1928	1908	Mercedes-Benz V-Class and Marco Polo official brochure	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	5140	1928	1980	Mercedes-Benz V-Class and Marco Polo official brochure; Engine in Detail Marco Polo 300 d 2021; Engine in Detail Marco Polo 300 d 4MATIC 2021	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-9g-tronic-2021;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2021
EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	5140	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	5370	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
```

## 下一步优先处理

1. 按 E-Ducato 的车长、车顶、电池容量和总质量等级闭合完整外廓矩阵。
2. 集中处理 Pontiac Trans Sport、Ford Windstar 和 Chrysler Voyager IV 的短轴/长轴及驱动高度边界。
3. 闭合旧款 Fiat Fiorino 1.4、1.6 IE 的乘用/厢式外廓。

推进信号：CONTINUE

[1]: https://www.cordwallis.com/wp-content/uploads/Caddy-Cargo-brochure-May-2021.pdf "Caddy Cargo brochure May 2021"
[2]: https://rea.as/wp-content/uploads/E-Ducato-Brochure-Technical-Characteristics-june20.pdf?utm_source=chatgpt.com "A SUSTAINABLE NEW ENERGY"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合剩余 8 个 Ktype：Pontiac Trans Sport、Ford Windstar、Fiat Fiorino、Chrysler Voyager IV 与 Fiat E-Ducato。
* E-Ducato 按官方技术表拆分为 16 个长度、车顶、电池及车辆等级外廓；其余旧款 MPV 按已确认的标准车身尺寸组复用。([汽车数据网][1])
* 已完成机械检查：两张表表头固定，133 个 `id` 唯一，95 个尺寸组唯一，所有引用闭合，无孤立尺寸组、空尺寸、空来源或 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：100
* READY 映射：133
* PENDING：0
* DIMENSION_GROUP：95
* 映射引用闭合：95/95
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143218	143218	MPV	Trans Sport I	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-MPV-01	HIGH		READY
143238	143238	MPV	Windstar I	WIN88	4	EU-FORD-USA-WINDSTAR-I-MPV-01	HIGH		READY
143239	143239	Wagon	Swace I		5	EU-SUZUKI-SWACE-I-WAGON-01	HIGH		READY
143242_prefl	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
143242_facelift	143242	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
143244	143244	MPV	Fiorino 147	147		EU-FIAT-FIORINO-147-MPV-01	HIGH		READY
143245	143245	MPV	Fiorino 147	147		EU-FIAT-FIORINO-147-MPV-01	HIGH		READY
143246	143246	MPV	Voyager IV	RG	5	EU-CHRYSLER-VOYAGER-IV-RG-MPV-SWB-01	HIGH		READY
143247	143247	MPV	Voyager IV	RG	5	EU-CHRYSLER-VOYAGER-IV-RG-MPV-SWB-01	HIGH		READY
143248	143248	MPV	Voyager IV	RG	5	EU-CHRYSLER-VOYAGER-IV-RG-MPV-SWB-01	HIGH		READY
143251	143251	Hatchback	DS 3 Crossback I		5	EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	HIGH		READY
143253	143253	SUV	Tiguan II Facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
143254	143254	SUV	2008 II	P24	5	EU-PEUGEOT-2008-II-P24-SUV-01	HIGH		READY
143255	143255	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PREFL-01	HIGH		READY
143256	143256	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PREFL-01	HIGH	R eHybrid与同代标准轴距外廓一致。	READY
143258	143258	SUV	Tiguan II Facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-FWD-01	HIGH		READY
143259	143259	SUV	Eclipse Cross I Facelift		5	EU-MITSUBISHI-ECLIPSE-CROSS-I-FACELIFT-SUV-01	HIGH		READY
143260_van_swb	143260	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-SWB-01	MEDIUM	标准轴距厢式外廓。	READY
143260_mpv_swb	143260	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	MEDIUM	标准轴距乘用外廓。	READY
143260_van_lwb	143260	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-LWB-01	MEDIUM	Maxi长轴厢式外廓。	READY
143260_mpv_lwb	143260	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	MEDIUM	Maxi长轴乘用外廓。	READY
143261	143261	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH	356四门轿车外廓。	READY
143264_swb	143264	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	HIGH	标准轴距乘用外廓。	READY
143264_lwb	143264	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	HIGH	Maxi长轴乘用外廓。	READY
143265	143265	Sedan	A3 8Y	8Y	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
143266	143266	Hatchback	A3 8Y	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
143268	143268	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
143269	143269	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
143270	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	三门厢式衍生车，复用相同三门外廓。	READY
143274_long	143274	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	长轴乘用外廓。	READY
143274_extralong	143274	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	HIGH	超长轴乘用外廓。	READY
143279_long	143279	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	HIGH	长轴四驱乘用外廓。	READY
143279_extralong	143279	MPV	V-Class W447 Facelift	W447	5	EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	HIGH	超长轴四驱乘用外廓。	READY
143280	143280	MPV	Marco Polo W447 Facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	MEDIUM	长轴升顶露营车外廓。	READY
143281	143281	MPV	Marco Polo W447 Facelift	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	MEDIUM	长轴四驱升顶露营车外廓。	READY
143282_l1	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴乘用外廓。	READY
143282_l2	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴乘用外廓。	READY
143282_l3	143282	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴乘用外廓。	READY
143283_l1	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴四驱乘用外廓。	READY
143283_l2	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴四驱乘用外廓。	READY
143283_l3	143283	MPV	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴四驱乘用外廓。	READY
143284_l1	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴Mixto外廓。	READY
143284_l2	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴Mixto外廓。	READY
143284_l3	143284	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴Mixto外廓。	READY
143285_l1	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	MEDIUM	L1短轴四驱Mixto外廓。	READY
143285_l2	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	MEDIUM	L2长轴四驱Mixto外廓。	READY
143285_l3	143285	Van	Vito W447 Facelift	W447		EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	MEDIUM	L3超长轴四驱Mixto外廓。	READY
143287	143287	Convertible	Sián Roadster		2	EU-LAMBORGHINI-SIAN-ROADSTER-CONVERTIBLE-01	HIGH	Roadster两门开放式外廓。	READY
143290	143290	Sedan	ET7 I		4	EU-NIO-ET7-I-SEDAN-01	HIGH		READY
143294	143294	Wagon	Golf VIII Alltrack	CG5	5	EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	HIGH	Alltrack抬高旅行车外廓。	READY
143296	143296	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	GTO-RS两门开放式外廓。	READY
143297	143297	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	GTO-JD70两门开放式外廓。	READY
143298	143298	SUV	Tang II Facelift		5	EU-BYD-TANG-II-FACELIFT-SUV-01	HIGH		READY
143303	143303	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
143304	143304	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
143314_medium	143314	MPV	Proace II	K0	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	MEDIUM	Medium电动乘用外廓。	READY
143314_long	143314	MPV	Proace II	K0	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	MEDIUM	Long电动乘用外廓。	READY
143315_medium	143315	MPV	Proace Verso II	K0	5	EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium电动乘用外廓。	READY
143315_long	143315	MPV	Proace Verso II	K0	5	EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long电动乘用外廓。	READY
143317	143317	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	HIGH	Forman及其厢式衍生车共用外廓。	READY
143318	143318	Wagon	Favorit Forman	785	5	EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	MEDIUM	Forman及其厢式衍生车共用外廓。	READY
143332	143332	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-HATCHBACK-01	HIGH		READY
143333	143333	Wagon	Ceed III Sportswagon	CD	5	EU-KIA-CEED-III-WAGON-01	HIGH		READY
143334	143334	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-SUV-01	HIGH		READY
143335	143335	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-WAGON-01	HIGH	五门shooting-brake外廓。	READY
143339	143339	SUV	HS I Facelift		5	EU-MG-HS-I-FACELIFT-SUV-01	HIGH		READY
143342	143342	Hatchback	Classic Mini		2	EU-AUSTIN-MINI-CLASSIC-HATCHBACK-01	MEDIUM	覆盖Mk II末期及后续经典Mini，外廓尺寸一致。	READY
143350	143350	Hatchback	ID.3 I Pre-facelift	E11	5	EU-VW-ID3-I-HATCHBACK-PREFL-01	HIGH	2020-2023改款前五门车身。	READY
143380	143380	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143381	143381	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143382	143382	Wagon	Tempra	159	5	EU-FIAT-TEMPRA-159-WAGON-01	MEDIUM	Tempra SW及Marengo厢式衍生车共用外廓。	READY
143384	143384	Sedan	S-Class V223	223.163	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143385	143385	Sedan	S-Class V223	223.161	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143386	143386	Hatchback	Ami I		2	EU-CITROEN-AMI-I-HATCHBACK-01	HIGH	双门轻型四轮车外廓。	READY
143387	143387	Sedan	S-Class V223	223.130	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143388	143388	Sedan	S-Class V223	223.131	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143389	143389	Sedan	S-Class V223	223.133	4	EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	HIGH		READY
143390	143390	Hatchback	C4 III Phase I	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	按输入Schrägheck归一为Hatchback。	READY
143391_swb	143391	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	HIGH	短轴三门封闭车身。	READY
143391_lwb	143391	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	HIGH	长轴五门封闭车身。	READY
143392	143392	Convertible	G-Class W463	W463	2	EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-SWB-01	HIGH	短轴双门开放式车身。	READY
143399	143399	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH		READY
143400	143400	SUV	Model X I		5	EU-TESLA-MODEL-X-I-SUV-01	HIGH		READY
143402	143402	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
143409	143409	Convertible	R8 I 42 Facelift		2	EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	HIGH		READY
143416	143416	Sedan	M5 F90 CS	F90	4	EU-BMW-5-F90-M5-CS-SEDAN-01	HIGH		READY
143418	143418	Hatchback	Fiesta VII Active		5	EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143419	143419	Hatchback	Fiesta VII Active		5	EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143421	143421	Hatchback	Focus IV Active		5	EU-FORD-FOCUS-IV-ACTIVE-HATCHBACK-01	HIGH	Active五门抬高车身。	READY
143425	143425	Hatchback	Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
143426	143426	Wagon	Octavia IV Combi	NX	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
143428	143428	Convertible	R8 I 42 Facelift		2	EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	HIGH		READY
143429	143429	Sedan	S60 II Facelift	134	4	EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	HIGH		READY
143433	143433	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
143447_l2h1_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L2H1-47KWH-N1-01	HIGH	L2H1 47 kWh N1厢式外廓。	READY
143447_l2h2_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L2H2-47KWH-N1-01	HIGH	L2H2 47 kWh N1厢式外廓。	READY
143447_l2h2_79kwh	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L2H2-79KWH-01	HIGH	L2H2 79 kWh厢式外廓。	READY
143447_l2h2_47kwh_n2	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L2H2-47KWH-N2-01	HIGH	L2H2 47 kWh N2厢式外廓。	READY
143447_l3h2_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H2-47KWH-N1-01	HIGH	L3H2 47 kWh N1厢式外廓。	READY
143447_l3h2_79kwh	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H2-79KWH-01	HIGH	L3H2 79 kWh厢式外廓。	READY
143447_l3h2_47kwh_n2	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H2-47KWH-N2-01	HIGH	L3H2 47 kWh N2厢式外廓。	READY
143447_l3h3_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H3-47KWH-N1-01	HIGH	L3H3 47 kWh N1厢式外廓。	READY
143447_l3h3_79kwh	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H3-79KWH-01	HIGH	L3H3 79 kWh厢式外廓。	READY
143447_l3h3_47kwh_n2	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L3H3-47KWH-N2-01	HIGH	L3H3 47 kWh N2厢式外廓。	READY
143447_l4h2_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H2-47KWH-N1-01	HIGH	L4H2 47 kWh N1厢式外廓。	READY
143447_l4h2_79kwh	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H2-79KWH-01	HIGH	L4H2 79 kWh厢式外廓。	READY
143447_l4h2_47kwh_n2	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H2-47KWH-N2-01	HIGH	L4H2 47 kWh N2厢式外廓。	READY
143447_l4h3_47kwh_n1	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H3-47KWH-N1-01	HIGH	L4H3 47 kWh N1厢式外廓。	READY
143447_l4h3_79kwh	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H3-79KWH-01	HIGH	L4H3 79 kWh厢式外廓。	READY
143447_l4h3_47kwh_n2	143447	Van	E-Ducato X290	X290		EU-FIAT-E-DUCATO-X290-VAN-L4H3-47KWH-N2-01	HIGH	L4H3 47 kWh N2厢式外廓。	READY
143449	143449	SUV	Kuga II Facelift		5	EU-FORD-KUGA-II-SUV-FACELIFT-01	HIGH		READY
143450	143450	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	MEDIUM	Polestar Engineered未形成已确认的独立外廓分支。	READY
143451	143451	Coupe	2 Series G42	G42	2	EU-BMW-2-G42-COUPE-01	MEDIUM	输入220i xDrive动力标签与欧洲常见配置不一致；物理车身按G42 Coupe闭合。	READY
143452	143452	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
143457	143457	Wagon	3 Series G21 Pre-facelift	G21	5	EU-BMW-3-G21-WAGON-PREFL-PHEV-XDRIVE-01	HIGH		READY
143459	143459	Wagon	5 Series G31 Facelift	G31	5	EU-BMW-5-G31-WAGON-FACELIFT-01	HIGH	G31改款后五门旅行车。	READY
143463	143463	Hatchback	Model S I Facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	HIGH		READY
143472	143472	Wagon	A6 allroad C8		5	EU-AUDI-A6-C8-ALLROAD-WAGON-01	HIGH	Allroad抬高旅行车外廓。	READY
143474	143474	Sedan	Model 3 I Facelift 2020		4	EU-TESLA-MODEL-3-I-SEDAN-FACELIFT-2020-01	HIGH	2020改款后四门外廓。	READY
143475	143475	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143476	143476	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143477	143477	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143478	143478	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143479	143479	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143480	143480	Sedan	Model 3 I Pre-facelift		4	EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	HIGH	改款前四门外廓。	READY
143481	143481	SUV	T-Roc I	A11	5	EU-VW-T-ROC-I-A11-SUV-01	HIGH		READY
143485	143485	SUV	EQA I	H243	5	EU-MERCEDES-BENZ-EQA-I-H243-SUV-01	HIGH		READY
143488	143488	Hatchback	Megane IV Phase II		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH	Phase II五门掀背车。	READY
143490	143490	Convertible	TTS 8S Facelift	8S	2	EU-AUDI-TT-8S-FACELIFT-TTS-ROADSTER-01	HIGH		READY
143491	143491	Wagon	E-Class S213 Facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH		READY
143492	143492	Sedan	e-tron GT I	F83	4	EU-AUDI-E-TRON-GT-I-RS-SEDAN-01	HIGH	RS四门GT外廓。	READY
143493	143493	Wagon	S6 C8 Avant	4K5	5	EU-AUDI-S6-C8-AVANT-WAGON-01	HIGH		READY
143498	143498	Sedan	E-Class W213 Facelift	213.019	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_201-300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PONTIAC-TRANS-SPORT-I-MPV-01	4946	1886	1670	Auto-Data Pontiac Trans Sport 3.8 i V6	https://www.auto-data.net/en/pontiac-trans-sport-3.8-i-v6-175hp-5988
EU-FORD-USA-WINDSTAR-I-MPV-01	5126	1915	1789	Automobile-Catalog 1995 Ford Windstar Europe export	https://www.automobile-catalog.com/car/1995/886490/ford_windstar.html
EU-SUZUKI-SWACE-I-WAGON-01	4655	1790	1460	Auto-Data Suzuki Swace I 1.8 Hybrid CVT	https://www.auto-data.net/en/suzuki-swace-i-1.8-122hp-hybrid-cvt-41312
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418	BMW 3 Series Touring E91 official technical data	https://tomic.ba/fs/cjenik/E91%20ACEA%20Technik%200307.pdf
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-generation-4365
EU-FIAT-FIORINO-147-MPV-01	4159	1622	1904	Auto-Data Fiat Fiorino 147	https://www.auto-data.net/en/fiat-fiorino-147-generation-1592
EU-CHRYSLER-VOYAGER-IV-RG-MPV-SWB-01	4805	1995	1750	Auto-Data Chrysler Voyager IV 3.3 i V6; Auto-Data Chrysler Voyager IV 3.8 i V6 AWD	https://www.auto-data.net/en/chrysler-voyager-iv-3.3-i-v6-174hp-automatic-14829;https://www.auto-data.net/en/chrysler-voyager-iv-3.8-i-v6-218hp-awd-14831
EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	4118	1791	1534	DS Automobiles DS 3 Crossback official dimensions	https://www.media.stellantis.com/uk-en/ds/press/ds-3-crossback-icon-of-high-tech-style
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	4509	1839	1684	Auto-Data Volkswagen Tiguan II facelift 2.0 TSI 4MOTION	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-2.0-tsi-245hp-4motion-dsg-44395
EU-PEUGEOT-2008-II-P24-SUV-01	4300	1770	1550	Auto-Data Peugeot 2008 II 1.5 BlueHDi 110	https://www.auto-data.net/en/peugeot-2008-ii-1.5-bluehdi-110hp-47192
EU-VW-TOUAREG-III-CR-SUV-PREFL-01	4878	1984	1717	Auto-Data Volkswagen Touareg III eHybrid; Auto-Data Volkswagen Touareg III R eHybrid	https://www.auto-data.net/en/volkswagen-touareg-iii-cr-3.0-v6-tsi-381hp-ehybrid-4motion-tiptronic-41524;https://www.auto-data.net/en/volkswagen-touareg-iii-cr-r-3.0-v6-tsi-462hp-ehybrid-4motion-tiptronic-41523
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-FWD-01	4509	1839	1675	Auto-Data Volkswagen Tiguan II facelift 1.4 eHybrid	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-1.4-tsi-245hp-ehybrid-dsg-41793
EU-MITSUBISHI-ECLIPSE-CROSS-I-FACELIFT-SUV-01	4545	1805	1685	Mitsubishi Eclipse Cross official specifications	https://www.mitsubishi-motors.co.jp/lineup/eclipse-cross/spec/spe_02.html
EU-VW-CADDY-V-VAN-SWB-01	4500	1855	1856	Volkswagen Caddy Cargo official brochure	https://www.cordwallis.com/wp-content/uploads/Caddy-Cargo-brochure-May-2021.pdf
EU-VW-CADDY-V-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy and Caddy Life official brochure	https://www.vwpress.co.uk/assets/documents/original/30530-caddylifebrochure.pdf
EU-VW-CADDY-V-VAN-LWB-01	4853	1855	1860	Volkswagen Caddy Cargo official brochure	https://www.cordwallis.com/wp-content/uploads/Caddy-Cargo-brochure-May-2021.pdf
EU-VW-CADDY-V-MPV-LWB-01	4853	1855	1800	Volkswagen Caddy and Caddy Life official brochure	https://www.vwpress.co.uk/assets/documents/original/30530-caddylifebrochure.pdf
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Auto-Data Fiat Tipo 356 facelift 1.0 Turbo	https://www.auto-data.net/en/fiat-tipo-356-facelift-2020-1.0-turbo-100hp-54096
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425	Audi A3 2020 official facts and figures	https://www.audi.com/de/dynamisch-wie-nie-der-neue-audi-a3-sportback-und-die-neue-a3-limousine-2020-12974/fakten-12977
EU-AUDI-A3-8Y-SPORTBACK-5D-01	4343	1816	1449	Audi A3 2020 official facts and figures	https://www.audi.com/de/dynamisch-wie-nie-der-neue-audi-a3-sportback-und-die-neue-a3-limousine-2020-12974/fakten-12977
EU-VW-GOLF-VIII-VARIANT-WAGON-01	4633	1789	1498	Volkswagen Golf Variant official design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-variant-and-golf-alltrack-international-media-drive-6540/design-and-dimensions-6543
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford Fiesta official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Fiesta.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-LONG-01	5140	1928	1901	Mercedes-Benz V-Class and Marco Polo official brochure	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf
EU-MERCEDES-BENZ-V-CLASS-W447-MPV-EXTRALONG-01	5370	1928	1908	Mercedes-Benz V-Class and Marco Polo official brochure	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf
EU-MERCEDES-BENZ-MARCO-POLO-W447-CAMPER-LONG-01	5140	1928	1980	Mercedes-Benz V-Class and Marco Polo official brochure; Engine in Detail Marco Polo 300 d 2021; Engine in Detail Marco Polo 300 d 4MATIC 2021	https://www.poptop.nl/wp-content/uploads/2021/11/v-classmarcopolo-2021.pdf;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-9g-tronic-2021;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2021
EU-MERCEDES-BENZ-VITO-W447-BODY-L1-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
EU-MERCEDES-BENZ-VITO-W447-BODY-L2-01	5140	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
EU-MERCEDES-BENZ-VITO-W447-BODY-L3-01	5370	1928	1910	Mercedes-Benz Vito Tourer official brochure; Mercedes-Benz Vito Panel and Crew Van official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf;https://bluesky-cogcms.cdn.imgeng.in/media/87150/mb-vans-vito-panel-and-vito-crew-may-2021-sml.pdf
EU-LAMBORGHINI-SIAN-ROADSTER-CONVERTIBLE-01	4979	2080	1158	Auto-Data Lamborghini Sián Roadster	https://www.auto-data.net/en/lamborghini-sian-roadster-generation-9600
EU-NIO-ET7-I-SEDAN-01	5101	1987	1509	NIO ET7 official user manual	https://www.nio.com/cdn-static/www/user-instructions/en_EU/ET7/index.html
EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	4639	1795	1510	Auto-Data Volkswagen Golf VIII Alltrack 2.0 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-golf-viii-alltrack-2.0-tdi-200hp-4motion-dsg-41835
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140	Donkervoort D8 GTO official heritage	https://www.donkervoort.com/en/models/heritage/donkervoort-d8-gto/
EU-BYD-TANG-II-FACELIFT-SUV-01	4870	1950	1725	Auto-Data BYD Tang II facelift EV 517 hp AWD	https://www.auto-data.net/en/byd-tang-ii-facelift-2021-ev-86.4-kwh-517hp-awd-46808
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Auto-Data Volvo S60 III generation	https://www.auto-data.net/en/volvo-s60-iii-generation-6352
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Auto-Data Volvo S90	https://www.auto-data.net/en/volvo-s90-model-932
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota Proace Verso official brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-archive/proace-verso/proace-verso-feb-22.pdf
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910	Toyota Proace Verso official brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-archive/proace-verso/proace-verso-feb-22.pdf
EU-SKODA-FAVORIT-FORMAN-785-WAGON-01	4160	1620	1425	Auto-Data Skoda Favorit Forman 785 1.3	https://www.auto-data.net/en/skoda-favorit-forman-785-1.3-135-e-54hp-14291
EU-KIA-CEED-III-HATCHBACK-01	4310	1800	1447	Automobile-Catalog 2021 Kia Ceed 1.5 T-GDI 160	https://www.automobile-catalog.com/car/2021/3002660/kia_ceed_1_5_t-gdi_160.html
EU-KIA-CEED-III-WAGON-01	4600	1800	1465	Automobile-Catalog 2021 Kia Ceed Sportswagon 1.5 T-GDI 160	https://www.automobile-catalog.com/car/2021/3002780/kia_ceed_sportswagon_1_5_t-gdi_160.html
EU-KIA-XCEED-I-SUV-01	4395	1826	1495	Auto-Data Kia XCeed 1.5 T-GDI 160	https://www.auto-data.net/en/kia-xceed-1.5-t-gdi-160hp-44840
EU-KIA-PROCEED-III-WAGON-01	4605	1800	1422	Auto-Data Kia ProCeed III 1.5 T-GDI 160	https://www.auto-data.net/en/kia-proceed-iii-facelift-2021-1.5-t-gdi-160hp-44812
EU-MG-HS-I-FACELIFT-SUV-01	4574	1876	1685	Auto-Data MG HS I facelift EHS Plug-in Hybrid	https://www.auto-data.net/en/mg-hs-i-facelift-2020-1.5-t-gdi-258hp-plug-in-hybrid-automatic-48931
EU-AUSTIN-MINI-CLASSIC-HATCHBACK-01	3054	1410	1346	Automobile-Catalog 1969 Austin Mini 850 Mk II; Automobile-Catalog 1969 Mini 850 Mk III	https://www.automobile-catalog.com/car/1969/256370/austin_mini_850_mk_ii.html;https://www.automobile-catalog.com/car/1969/1705160/mini_850.html
EU-VW-ID3-I-HATCHBACK-PREFL-01	4261	1809	1568	EV Database Volkswagen ID.3 1st	https://ev-database.org/car/1300/Volkswagen-ID3-1st
EU-FIAT-TEMPRA-159-WAGON-01	4472	1695	1500	Automobile-Catalog 1991 Fiat Tempra S.W.	https://www.automobile-catalog.com/car/1991/719255/fiat_tempra_s__w__2_0_i_e__sx_automatic.html
EU-MERCEDES-BENZ-S-CLASS-V223-SEDAN-01	5289	1954	1503	Mercedes-Benz S-Class Long V223 official vehicle dimensions	https://www.mercedes-benz-mena.com/ksa/en/services/manuals/s-class-saloon-long-2026-02-v223-mbux/vehicle-data/vehicle-dimensions
EU-CITROEN-AMI-I-HATCHBACK-01	2410	1390	1525	Auto-Data Citroën Ami Electric	https://www.auto-data.net/en/citroen-ami-electric-model-3328
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Auto-Data Citroën C4 III 1.2 PureTech 155	https://www.auto-data.net/en/citroen-c4-iii-phase-i-2020-1.2-puretech-155hp-automatic-42198
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-01	4180	1690	1931	UltimateSpecs Mercedes-Benz G-Class SWB W463 300 Diesel	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2635/Mercedes-Benz-G-Class-SWB-%28W463%29-300-Diesel.html
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-01	4630	1690	1935	UltimateSpecs Mercedes-Benz G-Class LWB W463 300 Diesel	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2655/Mercedes-Benz-G-Class-LWB-%28W463%29-300-Diesel.html
EU-MERCEDES-BENZ-G-CLASS-W463-CONVERTIBLE-SWB-01	4225	1690	1942	UltimateSpecs Mercedes-Benz G-Class SWB W463 300 Diesel Cabrio	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2646/Mercedes-Benz-G-Class-SWB-%28W463%29-300-Diesel-Cabrio.html
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684	Auto-Data Tesla Model X Performance	https://www.auto-data.net/en/tesla-model-x-performance-100-kwh-611hp-dual-motor-awd-42397
EU-AUDI-R8-I-42-SPYDER-FACELIFT-01	4440	1904	1244	Audi R8 official UK pricing and specification guide	https://press.audi.co.uk/assets/documents/original/24231-AudiUK00001684AudiR8PricingandSpecification.pdf
EU-BMW-5-F90-M5-CS-SEDAN-01	5001	1903	1468	BMW M5 CS official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0325152EN/471027
EU-FORD-FIESTA-VII-ACTIVE-HATCHBACK-01	4068	1756	1498	Ford Fiesta official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Fiesta.pdf
EU-FORD-FOCUS-IV-ACTIVE-HATCHBACK-01	4397	1844	1502	Ford Focus official technical specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-ford-focus-new.pdf
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470	Auto-Data Skoda Octavia IV 1.5 TSI e-TEC	https://www.auto-data.net/en/skoda-octavia-iv-1.5-tsi-evo-e-tec-150hp-mild-hybrid-dsg-38015
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468	Auto-Data Skoda Octavia IV Combi 1.5 TSI e-TEC	https://www.auto-data.net/en/skoda-octavia-iv-combi-1.5-tsi-evo-e-tec-150hp-mild-hybrid-dsg-38025
EU-VOLVO-S60-II-FACELIFT-POLESTAR-SEDAN-01	4635	1865	1484	Auto-Data Volvo S60 II facelift Polestar	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-polestar-3.0-t6-350hp-awd-geartronic-21715
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data Volvo V90	https://www.auto-data.net/en/volvo-v90-model-923
EU-FIAT-E-DUCATO-X290-VAN-L2H1-47KWH-N1-01	5413	2050	2309	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L2H2-47KWH-N1-01	5413	2050	2579	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L2H2-79KWH-01	5413	2050	2589	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L2H2-47KWH-N2-01	5413	2050	2599	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H2-47KWH-N1-01	5998	2050	2579	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H2-79KWH-01	5998	2050	2589	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H2-47KWH-N2-01	5998	2050	2599	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H3-47KWH-N1-01	5998	2050	2814	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H3-79KWH-01	5998	2050	2824	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L3H3-47KWH-N2-01	5998	2050	2834	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H2-47KWH-N1-01	6363	2050	2579	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H2-79KWH-01	6363	2050	2589	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H2-47KWH-N2-01	6363	2050	2599	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H3-47KWH-N1-01	6363	2050	2814	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H3-79KWH-01	6363	2050	2824	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-E-DUCATO-X290-VAN-L4H3-47KWH-N2-01	6363	2050	2834	Fiat Professional E-Ducato MY20 official technical information	https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FORD-KUGA-II-SUV-FACELIFT-01	4531	1838	1689	Ford Kuga official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Kuga.pdf
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data Volvo XC60 II	https://www.auto-data.net/en/volvo-xc60-ii-generation-5397
EU-BMW-2-G42-COUPE-01	4537	1838	1390	Auto-Data BMW 2 Series Coupe G42 220i	https://www.auto-data.net/en/bmw-2-series-coupe-g42-220i-184hp-steptronic-43834
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Auto-Data Volvo XC40 T3 163	https://www.auto-data.net/en/volvo-xc40-1.5-t3-163hp-40921
EU-BMW-3-G21-WAGON-PREFL-PHEV-XDRIVE-01	4709	1827	1442	BMW 320e xDrive Touring official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0325532EN/471539
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498	BMW 5 Series Touring G31 LCI official brochure	https://www.bmw.hr/content/dam/bmw/marketB4R1/bmw_hr/topics/pricelists-brochures/brochures/2020_10/BMW%205%20Series%20Touring%20%28G31%20LCI%29.pdf
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445	Auto-Data Tesla Model S facelift 2016	https://www.auto-data.net/en/tesla-model-s-model-2013
EU-AUDI-A6-C8-ALLROAD-WAGON-01	4951	1902	1497	Audi A6 allroad 55 TDI official technical data; Automobile-Catalog Audi A6 allroad 55 TDI MHEV	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1179/file_en/be073dab2b00611d12009596d727db4f92159435/eTD-Audi-A6-allroad-quattro-55-TDI-tiptronic-253kW-MHEV_240613.pdf?1718367298=&disposition=attachment;https://www.automobile-catalog.com/car/2020/3005750/audi_a6_allroad_quattro_55_tdi_mhev.html
EU-TESLA-MODEL-3-I-SEDAN-FACELIFT-2020-01	4694	1849	1443	Auto-Data Tesla Model 3 facelift 2020 generation	https://www.auto-data.net/en/tesla-model-3-facelift-2020-generation-8587
EU-TESLA-MODEL-3-I-SEDAN-PREFL-01	4694	1849	1443	Auto-Data Tesla Model 3 pre-facelift generation	https://www.auto-data.net/en/tesla-model-3-generation-6100
EU-VW-T-ROC-I-A11-SUV-01	4234	1819	1573	Auto-Data Volkswagen T-Roc I 1.5 TSI	https://www.auto-data.net/en/volkswagen-t-roc-i-1.5-tsi-150hp-act-36112
EU-MERCEDES-BENZ-EQA-I-H243-SUV-01	4463	1834	1620	Auto-Data Mercedes-Benz EQA H243 EQA 250	https://www.auto-data.net/en/mercedes-benz-eqa-h243-eqa-250-69.7-kwh-190hp-42117
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Auto-Data Renault Megane IV 1.5 Energy dCi	https://www.auto-data.net/en/renault-megane-iv-1.5-energy-dci-110hp-22559
EU-AUDI-TT-8S-FACELIFT-TTS-ROADSTER-01	4199	1832	1341	Auto-Data Audi TTS Roadster 8S facelift 320	https://www.auto-data.net/en/audi-tts-roadster-8s-facelift-2018-2.0-tfsi-320hp-quattro-s-tronic-50560
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Mercedes-Benz E-Class Estate official brochure	https://uat-msl-21.clients.cemacdigital.com/assets/1/product-brochures/mercedes-benz/e-class-estate-brochure.pdf
EU-AUDI-E-TRON-GT-I-RS-SEDAN-01	4989	1964	1396	Automobile-Catalog 2021 Audi RS e-tron GT	https://www.automobile-catalog.com/car/2021/3006515/audi_rs_e-tron_gt.html
EU-AUDI-S6-C8-AVANT-WAGON-01	4954	1886	1481	Automobile-Catalog 2021 Audi S6 Avant TDI	https://www.automobile-catalog.com/car/2021/3005840/audi_s6_avant_tdi.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-FACELIFT-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift E 300 d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43736
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_201-300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/pontiac-trans-sport-3.8-i-v6-175hp-5988 "https://www.auto-data.net/en/pontiac-trans-sport-3.8-i-v6-175hp-5988"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_201-300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_201-300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2173 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1044 行）

