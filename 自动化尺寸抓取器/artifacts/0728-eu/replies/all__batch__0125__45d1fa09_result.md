# 任务：all 第 12401-12500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0125__45d1fa09


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 12401-12500 行

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
all 第 12401-12500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1853	1456
EU-CITROEN-C5-II-X7-WAGON-5D-01	4829	1853	1491
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	5505	1998	2455
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	5505	1998	2470
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	5005	1998	2145
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	5005	1998	2465
EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	4655	1998	2450
EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	5620	2000	2096
EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	5120	2000	2093
EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	4770	2000	2093
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	5620	2000	2130
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	5120	2000	2124
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	4167	1698	1391
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405
EU-CITROEN-XSARA-I-N2-WAGON-5D-PREFL-01	4354	1698	1420
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-01	4660	1890	1760
EU-HYUNDAI-SANTA-FE-II-CM-FACELIFT-SUV-5D-V6-01	4676	1890	1725
EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	4200	1790	1624
EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	4251	1790	1625
EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	4240	1790	1623
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-FACELIFT-01	5066	1845	2033
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-PREFL-01	4922	1809	2035
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-FACELIFT-01	4616	1845	2033
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-PREFL-01	4472	1809	2045
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	5158	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-AMG-01	5252	1871	1478
EU-MERCEDES-BENZ-S-KLASSE-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-FACELIFT-01	5043	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-W220-SEDAN-SWB-PREFL-01	5038	1855	1444
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-AMG-01	5152	1871	1473
EU-MERCEDES-BENZ-S-KLASSE-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1300-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-FACELIFT-H1307-01	4390	1790	1307
EU-MERCEDES-BENZ-SL-R107-CONVERTIBLE-PREFL-01	4390	1790	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	4617	1877	1315
EU-MERCEDES-BENZ-SL-W113-CONVERTIBLE-01	4285	1760	1320
EU-MERCEDES-BENZ-SL-W121-CONVERTIBLE-01	4290	1740	1320
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-OPEL-COMBO-B-VAN-01	4230	1686	1805
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426
EU-PEUGEOT-206-PLUS-HATCHBACK-3D-01	3872	1655	1446
EU-PEUGEOT-206-PLUS-HATCHBACK-5D-01	3872	1655	1446
EU-PEUGEOT-406-COUPE-2D-01	4615	1780	1352
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412
EU-PEUGEOT-406-SEDAN-PREFL-01	4555	1764	1410
EU-PEUGEOT-PARTNER-II-B9-VAN-L1H1-01	4380	1810	1801
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827
EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	4803	1811	1445
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-PREFL-01	4129	1699	1420
EU-RENAULT-MEGANE-I-DA-COUPE-FACELIFT-01	3967	1698	1366
EU-RENAULT-MEGANE-I-DA-COUPE-PREFL-01	3931	1696	1366
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-FACELIFT-01	4082	1698	1368
EU-RENAULT-MEGANE-I-EA-CONVERTIBLE-PREFL-01	4028	1698	1368
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507
EU-RENAULT-MEGANE-III-HATCHBACK-01	4295	1808	1491
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420
EU-RENAULT-MEGANE-I-LA-SEDAN-PREFL-01	4440	1699	1420
EU-RENAULT-SCENIC-III-MPV-PHASE1-01	4343	1845	1624
EU-RENAULT-SCENIC-III-MPV-PHASE2-01	4366	1845	1640
EU-RENAULT-SCENIC-III-MPV-PHASE3-01	4366	1845	1640
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492
EU-SKODA-FABIA-II-5J-HATCHBACK-5D-FACELIFT-01	4000	1642	1498
EU-SKODA-FABIA-II-5J-WAGON-5D-FACELIFT-01	4247	1642	1498
EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	4833	1817	1462
EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	4838	1817	1462
EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	4838	1817	1510
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459
EU-VW-PASSAT-B5-3B5-WAGON-5D-01	4670	1740	1500
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	3	318 TI	Schrägheck	Heckantrieb	Benzin	105	143	Mar 2001	Dec 2004	2024-03-01	16189
BMW	3	320 TD	Schrägheck	Heckantrieb	Diesel	110	150	Sep 2001	Feb 2005	2024-03-01	16190
Opel	Combo	1.7 DI 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	48	65	Oct 2001	-	2024-03-01	16191
Opel	Corsa c	1.2 16V	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Sep 2000	Jul 2003	2024-03-01	16193
Opel	Corsa c	1.7 DI 16V	Kasten/Schrägheck	Frontantrieb	Diesel	48	65	Sep 2000	Jul 2003	2024-03-01	16194
Opel	Corsa c	1.7 DTI 16V	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Sep 2000	Jul 2003	2024-03-01	16195
Mercedes-benz	Mb	D	Pritsche/Fahrgestell	Frontantrieb	Diesel	55	75	Dec 1990	Feb 1996	2024-03-01	16196
Mercedes-benz	Mb	D	Pritsche/Fahrgestell	Frontantrieb	Diesel	53	72	Feb 1988	May 1992	2024-03-01	16197
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	105	143	Sep 2001	Feb 2005	2024-03-01	16198
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	105	143	Sep 2001	Feb 2004	2024-03-01	16199
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	110	150	Sep 2001	May 2005	2024-03-01	16201
BMW	3	320 D	Kombi	Heckantrieb	Diesel	110	150	Sep 2001	Feb 2005	2024-03-01	16202
Saab	9-5	3.0 TID	Stufenheck	Frontantrieb	Diesel	130	177	Jul 2001	Aug 2005	2024-03-01	16203
Saab	9-5	3.0 TID	Kombi	Frontantrieb	Diesel	130	177	Jul 2001	Aug 2005	2024-03-01	16204
Renault	Kangoo	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	70	95	Jun 2001	Mar 2018	2025-12-01	16205
Renault	Kangoo	1.6 16V 4X4	Großraumlimousine	Allrad	Benzin	70	95	Oct 2001	-	2024-03-01	16206
Opel	Combo	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	64	87	Oct 2001	-	2024-03-01	16207
Opel	Combo	1.7 DTI 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2001	-	2024-03-01	16208
Renault	Kangoo	1.2 16V	Großraumlimousine	Frontantrieb	Benzin	55	75	Jun 2001	-	2024-03-01	16209
Fiat	Stilo	2.4 20V	Schrägheck	Frontantrieb	Benzin	125	170	Oct 2001	Apr 2007	2024-03-01	16210
Renault	Megane iii grandtour	1.2 TCE	Kombi	Frontantrieb	Benzin	85	116	Mar 2012	Aug 2015	2024-03-01	16211
Hyundai	Matrix	1.8	Großraumlimousine	Frontantrieb	Benzin	90	122	Jun 2001	Aug 2010	2024-03-01	16212
Autobianchi	Y10	1	Schrägheck	Frontantrieb	Benzin	33	45	Mar 1985	Oct 1995	2024-03-01	16213
Autobianchi	Y10	1	Schrägheck	Frontantrieb	Benzin	41	56	Mar 1985	Oct 1995	2024-03-01	16214
Autobianchi	Y10	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	63	85	Mar 1985	Oct 1995	2024-03-01	16215
Autobianchi	Y10	1.0 4WD	Schrägheck	Allrad	Benzin	37	50	Dec 1986	Oct 1995	2024-03-01	16216
Autobianchi	Y10	1.0 CAT	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1987	Oct 1995	2024-03-01	16217
Autobianchi	Y10	1.3 I.e. GT	Schrägheck	Frontantrieb	Benzin	57	78	Jun 1989	Oct 1995	2024-03-01	16218
Autobianchi	Y10	1.1	Schrägheck	Frontantrieb	Benzin	42	57	Jun 1989	Oct 1995	2024-03-01	16219
Autobianchi	Y10	1.1 4WD	Schrägheck	Allrad	Benzin	42	57	Jun 1989	Oct 1995	2024-03-01	16220
Autobianchi	Y10	1.1 I.e. CAT	Schrägheck	Frontantrieb	Benzin	42	57	Sep 1990	Oct 1995	2024-03-01	16221
Autobianchi	Y10	1.3 I.e. GT	Schrägheck	Frontantrieb	Benzin	54	73	Jun 1989	Oct 1995	2024-03-01	16222
Jeep	Cherokee	2.4 4X4	Geländewagen geschlossen	Allrad	Benzin	108	147	Sep 2001	Jan 2008	2024-03-01	16223
Jeep	Cherokee	3.7 4X4	Geländewagen geschlossen	Allrad	Benzin	155	211	Sep 2001	Jan 2008	2024-03-01	16224
Jeep	Cherokee	2.5 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	105	143	Sep 2001	Jan 2008	2024-03-01	16225
Renault	Laguna ii	1.8 16V	Schrägheck	Frontantrieb	Benzin	88	120	Mar 2001	Sep 2007	2024-03-01	16226
Renault	Laguna ii	1.8 16V	Schrägheck	Frontantrieb	Benzin	85	116	Mar 2001	Dec 2007	2024-03-01	16227
Renault	Laguna ii grandtour	1.8 16V	Kombi	Frontantrieb	Benzin	85	116	Mar 2001	May 2005	2024-03-01	16228
Renault	Laguna ii grandtour	1.8 16V	Kombi	Frontantrieb	Benzin	88	120	Mar 2001	May 2005	2024-03-01	16229
Renault	Scénic i	1.8 16V	Großraumlimousine	Frontantrieb	Benzin	85	115	Jan 2001	Aug 2003	2024-03-01	16231
Renault	Megane i	1.8 16V	Schrägheck	Frontantrieb	Benzin	85	115	Jan 2001	Aug 2003	2024-03-01	16232
Renault	Megane i classic	1.8 16V	Stufenheck	Frontantrieb	Benzin	85	115	Jan 2001	Aug 2003	2024-03-01	16233
Renault	Megane i grandtour	1.8 16V	Kombi	Frontantrieb	Benzin	85	115	Jan 2001	Aug 2003	2024-03-01	16234
Mercedes-benz	Vaneo	1.6	Großraumlimousine	Frontantrieb	Benzin	60	82	Feb 2002	Jul 2005	2024-03-01	16242
Mercedes-benz	Vaneo	1.9	Großraumlimousine	Frontantrieb	Benzin	92	125	Feb 2002	Jul 2005	2024-03-01	16243
Mercedes-benz	Vaneo	1.7 CDI	Großraumlimousine	Frontantrieb	Diesel	67	91	Feb 2002	Jul 2005	2024-03-01	16244
Citroën	C5	1.8 16V	Kombi	Frontantrieb	Benzin	85	115	Jun 2001	Aug 2004	2024-07-01	16245
Citroën	Xsara	2.0 HDI 109	Schrägheck	Frontantrieb	Diesel	80	109	May 2001	Mar 2005	2024-03-01	16246
Citroën	Xsara	2.0 HDI 109	Coupe	Frontantrieb	Diesel	80	109	May 2001	Mar 2005	2024-03-01	16247
Citroën	Xsara	2.0 HDI 90	Coupe	Frontantrieb	Diesel	66	90	Feb 1999	Mar 2005	2024-03-01	16248
Citroën	Xsara	2.0 HDI 109	Kombi	Frontantrieb	Diesel	80	109	May 2001	Aug 2005	2024-03-01	16249
Mercedes-benz	S-Klasse	S 63 AMG	Stufenheck	Heckantrieb	Benzin	326	444	Sep 2001	Aug 2005	2024-03-01	16250
Mercedes-benz	S-Klasse	CL 63 AMG	Coupe	Heckantrieb	Benzin	326	444	Sep 2001	Mar 2006	2024-03-01	16251
Toyota	Rav 4 ii	2.0 D 4WD	SUV	Allrad	Diesel	85	116	May 2001	Nov 2005	2024-03-01	16252
VW	Golf iv	1.8 T GTI	Schrägheck	Frontantrieb	Benzin	132	180	Aug 2001	Jun 2005	2024-03-01	16253
Opel	Omega b	2.5 DTI	Stufenheck	Heckantrieb	Diesel	110	150	Sep 2001	Jul 2003	2024-03-01	16254
Opel	Omega b caravan	2.5 DTI	Kombi	Heckantrieb	Diesel	110	150	Sep 2001	Jul 2003	2024-03-01	16255
Mercedes-benz	Sl	55 AMG	Cabriolet	Heckantrieb	Benzin	350	476	Oct 2001	Jun 2002	2024-03-01	16258
Peugeot	406	2.0 16V HPI	Stufenheck	Frontantrieb	Benzin	103	140	May 2001	May 2004	2024-03-01	16259
Peugeot	406	2.0 16V HPI	Kombi	Frontantrieb	Benzin	103	140	May 2001	Oct 2004	2024-03-01	16260
Audi	A4 b6	1.9 TDI	Stufenheck	Frontantrieb	Diesel	74	101	May 2001	Dec 2004	2024-03-01	16261
Honda	Civic vii	1.7 I	Coupe	Frontantrieb	Benzin	88	120	May 2001	Dec 2005	2024-03-01	16262
Honda	Civic vii	1.7 I Vtec	Coupe	Frontantrieb	Benzin	92	125	May 2001	Dec 2005	2024-03-01	16263
Citroën	Jumper i	2.8 HDI	Bus	Frontantrieb	Diesel	94	128	Sep 2000	Apr 2002	2024-03-01	16264
Citroën	Jumper i	2.8 HDI 4X4	Bus	Allrad	Diesel	94	128	Sep 2000	Apr 2002	2024-03-01	16265
Citroën	Jumper i	2.8 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	94	128	Sep 2000	Apr 2002	2024-03-01	16266
Citroën	Jumper i	2.8 HDI	Kasten	Frontantrieb	Diesel	94	128	Sep 2000	Apr 2002	2024-03-01	16267
Citroën	Jumper i	2.8 HDI 4X4	Kasten	Allrad	Diesel	94	128	Sep 2000	Apr 2002	2024-03-01	16268
Peugeot	Partner	2.0 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Apr 2000	Jul 2008	2024-03-01	16269
Peugeot	206	1.4 HDI ECO 70	Schrägheck	Frontantrieb	Diesel	50	68	Sep 2001	Apr 2009	2024-03-01	16270
Maserati	4200 gt spyder	4.2	Cabriolet	Heckantrieb	Benzin	287	390	Oct 2001	-	2024-03-01	16271
Nissan	Primera	1.8	Stufenheck	Frontantrieb	Benzin	85	115	Mar 2002	Oct 2008	2024-03-01	16272
Nissan	Primera	2	Stufenheck	Frontantrieb	Benzin	103	140	Mar 2002	Oct 2008	2024-03-01	16273
Nissan	Primera	2.2 DI	Stufenheck	Frontantrieb	Diesel	93	126	Mar 2002	May 2007	2024-03-01	16274
Nissan	Primera	1.8	Kombi	Frontantrieb	Benzin	85	115	Mar 2002	May 2007	2024-03-01	16275
Nissan	Primera	2	Kombi	Frontantrieb	Benzin	103	140	Mar 2002	-	2024-03-01	16276
Nissan	Primera	2.2 DI	Kombi	Frontantrieb	Diesel	93	126	Mar 2002	Apr 2003	2024-03-01	16277
Daihatsu	Terios	1.3	Geländewagen geschlossen	Heckantrieb	Benzin	63	86	Jul 2000	Oct 2006	2024-03-01	16278
VW	Polo	1.4 TDI	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2001	Jun 2005	2024-03-01	16279
Chevrolet	Trailblazer	4.2 AWD	SUV	Allrad	Benzin	201	273	Sep 2001	Sep 2008	2024-03-01	16280
Peugeot	Partner	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	80	109	Jul 2001	Mar 2008	2024-03-01	16281
Hyundai	Santa fé i	2.0 Crdi	SUV	Frontantrieb	Diesel	83	113	Aug 2001	Mar 2006	2024-03-01	16282
Hyundai	I30	1.6 GDI	Schrägheck	Frontantrieb	Benzin	99	135	Dec 2011	Dec 2016	2024-03-01	16283
Hyundai	Terracan	2.5 TD	SUV	Allrad	Diesel	74	101	Dec 2001	Dec 2006	2024-03-01	16284
Renault	Kangoo	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	48	65	Dec 2001	-	2024-03-01	16285
Hyundai	Matrix	1.5 Crdi	Großraumlimousine	Frontantrieb	Diesel	60	82	Oct 2001	Aug 2010	2024-03-01	16286
Honda	Civic vii hatchback	2.0 Type-r	Schrägheck	Frontantrieb	Benzin	147	200	Sep 2001	Sep 2005	2024-03-01	16287
Peugeot	406	2.0 HDI 110	Stufenheck	Frontantrieb	Diesel	79	107	Aug 2001	May 2004	2024-03-01	16288
Peugeot	406	2.0 HDI 110	Kombi	Frontantrieb	Diesel	79	107	Aug 2001	Oct 2004	2024-03-01	16289
Skoda	Fabia i	2	Stufenheck	Frontantrieb	Benzin	85	116	Dec 1999	Dec 2007	2024-03-01	16290
Skoda	Superb i	1.8 T	Stufenheck	Frontantrieb	Benzin	110	150	Dec 2001	Mar 2008	2024-03-01	16291
Skoda	Superb i	2	Stufenheck	Frontantrieb	Benzin	85	115	Dec 2001	Mar 2008	2024-03-01	16292
Skoda	Superb i	2.8 V6	Stufenheck	Frontantrieb	Benzin	142	193	Dec 2001	Mar 2008	2024-03-01	16293
Skoda	Superb i	1.9 TDI	Stufenheck	Frontantrieb	Diesel	96	130	Dec 2001	Mar 2008	2024-03-01	16294
Skoda	Superb i	2.5 TDI	Stufenheck	Frontantrieb	Diesel	114	155	Dec 2001	Aug 2003	2024-03-01	16295
VW	Passat b5	2	Stufenheck	Frontantrieb	Benzin	88	120	Apr 2000	Nov 2000	2024-03-01	16296
VW	Passat b5	2.0 4motion	Stufenheck	Allrad	Benzin	88	120	Apr 2000	Nov 2000	2024-03-01	16297
VW	Passat b5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	74	101	Feb 2000	Nov 2000	2024-03-01	16298
VW	Passat b5 variant	1.9 TDI	Kombi	Frontantrieb	Diesel	74	101	Feb 2000	Nov 2000	2024-03-01	16299
VW	Polo	1.4 16V	Schrägheck	Frontantrieb	Benzin	55	75	Oct 2001	May 2008	2024-03-01	16300


--- Round 1 / 首次发送 ---
更新点

* 已按物理外廓完成 BMW E46 第一组聚类：Compact、Sedan、Coupe、Touring 分别闭合；其中 Sedan 复用已有尺寸组，Compact、Coupe、Touring 新建尺寸组。BMW 官方技术资料明确列出了相应门数和三维。
* 新建 Peugeot 406 facelift Break 尺寸组；2.0 HPi 与 2.0 HDi 110 对应资料均为 `4736 × 1760 × 1460 mm`，宽度口径不含后视镜。([汽车目录][1])
* 完成 Saab 9-5 YS3E Wagon、Renault Mégane I/III、VW Golf IV、Opel Omega B、Peugeot 206/406、Hyundai i30 GD、VW Passat B5 等已有尺寸组关联；Golf IV 与 Peugeot 206 的通用掀背 Ktype 按三门、五门物理分支派生。相关车身代号和边界已交叉核对。([维基百科][2])

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：23
* READY 映射行：25
* PENDING 输入 Ktype：77
* 已确认尺寸组：19，其中本轮新建 4 个、复用已有组 15 个
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16189	16189	Hatchback	3 Series E46 Compact	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH	E46/5 三门 Compact 车身。	READY
16190	16190	Hatchback	3 Series E46 Compact	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH	E46/5 三门 Compact 车身。	READY
16198	16198	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46 四门轿车车身。	READY
16199	16199	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-2D-01	HIGH	E46/2 双门 Coupe 车身。	READY
16201	16201	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46 四门轿车车身。	READY
16202	16202	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-5D-01	HIGH	E46/3 五门 Touring 车身。	READY
16204	16204	Wagon	9-5 I facelift (2001)	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	HIGH	YS3E 五门旅行车，2001 年改款外廓。	READY
16211	16211	Wagon	Mégane III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Mégane III Grandtour 五门车身。	READY
16232	16232	Hatchback	Mégane I facelift	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	BA0 五门掀背，Phase II 外廓。	READY
16233	16233	Sedan	Mégane I facelift	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	HIGH	LA0 四门 Classic，Phase II 外廓。	READY
16253_3dr	16253	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	MEDIUM	输入未给门数；按 1J1 三门物理分支派生。	READY
16253_5dr	16253	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	MEDIUM	输入未给门数；按 1J1 五门物理分支派生。	READY
16254	16254	Sedan	Omega B facelift	V94	4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH	V94 四门改款轿车。	READY
16255	16255	Wagon	Omega B facelift	V94	5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH	V94 五门 Caravan 改款车身。	READY
16259	16259	Sedan	406 facelift	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	8B 四门 Phase II 轿车。	READY
16260	16260	Wagon	406 facelift		5	EU-PEUGEOT-406-WAGON-FACELIFT-01	HIGH	五门 406 Break Phase II 车身。	READY
16270_3dr	16270	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	输入覆盖三门和五门；三门物理分支。	READY
16270_5dr	16270	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	输入覆盖三门和五门；五门物理分支。	READY
16283	16283	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD 五门掀背车身。	READY
16288	16288	Sedan	406 facelift	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	8B 四门 Phase II 轿车。	READY
16289	16289	Wagon	406 facelift		5	EU-PEUGEOT-406-WAGON-FACELIFT-01	HIGH	五门 406 Break Phase II 车身。	READY
16296	16296	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16297	16297	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16298	16298	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16299	16299	Wagon	Passat B5 pre-facelift	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH	3B5 五门 Variant 改款前车身。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E46-COUPE-2D-01	4488	1757	1369	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E46-TOURING-5D-01	4478	1739	1409	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-PEUGEOT-406-WAGON-FACELIFT-01	4736	1760	1460	Automobile-Catalog (406 Break 2.0 HPi);Automobile-Catalog (406 Break 2.0 HDi 110)	https://www.automobile-catalog.com/car/2002/2614760/peugeot_406_break_2_0_hpi.html;https://www.automobile-catalog.com/car/2002/2614940/peugeot_406_break_2_0_hdi_110.html
```

下一步优先处理

1. 闭合 Opel Combo C 与 Corsa C Van：不得误用已有 Combo B 组，需分别核对 Combo C、Corsa C 厢式车外廓。
2. 聚类 Renault Kangoo I 的改款前后、4×4 与 MPV 分支，并处理 Jumper I 的轴距、车顶和底盘车多外廓。
3. 继续闭合 Laguna II、Vaneo、Primera P12、Stilo、Matrix、Cherokee KJ 等当前尚无缓存的单一车身组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/2614760/peugeot_406_break_2_0_hpi.html?utm_source=chatgpt.com "2002 Peugeot 406 Break 2.0 HPi Specs Review (103 kW ..."
[2]: https://en.wikipedia.org/wiki/Saab_9-5?utm_source=chatgpt.com "Saab 9-5"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 首次闭合 Vaneo W414、Primera P12/WP12、Superb I 3U4、Audi A4 B6 Sedan、Honda Civic VII Coupe/Type-R 等 7 个乘用车外廓组。对应页面均直接提供不含后视镜宽度及完整三维。([汽车目录][1])
* Hyundai Matrix 两个 Ktype 均跨越 2008 年外廓改款，已分别派生 `prefl` 与 `facelift`：车长由 4025 mm 变为 4060 mm，宽高保持 1740/1685 mm。([汽车目录][1])
* 本轮共新增 22 条 READY 映射、9 个尺寸组；未重复输出上一轮已经闭合的尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：43
* READY 映射行：47
* PENDING 输入 Ktype：57
* 已确认尺寸组：28
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16212_prefl	16212	MPV	Matrix I pre-facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	HIGH	生产区间跨改款；改款前外廓。	READY
16212_facelift	16212	MPV	Matrix I facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	HIGH	生产区间跨改款；改款后加长外廓。	READY
16242	16242	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16243	16243	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16244	16244	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16261	16261	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH	8E2 四门轿车外廓。	READY
16262	16262	Coupe	Civic VII	EM2	2	EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	HIGH	EM2 双门 Coupe 外廓。	READY
16263	16263	Coupe	Civic VII	EM2	2	EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	HIGH	EM2 双门 Coupe 外廓。	READY
16272	16272	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16273	16273	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16274	16274	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16275	16275	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16276	16276	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16277	16277	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16286_prefl	16286	MPV	Matrix I pre-facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	HIGH	生产区间跨改款；改款前外廓。	READY
16286_facelift	16286	MPV	Matrix I facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	HIGH	生产区间跨改款；改款后加长外廓。	READY
16287	16287	Hatchback	Civic VII Type-R	EP3	3	EU-HONDA-CIVIC-VII-EP3-TYPE-R-HATCHBACK-3D-01	HIGH	EP3 三门 Type-R 外廓。	READY
16291	16291	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16292	16292	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16293	16293	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16294	16294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16295	16295	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	4025	1740	1685	Automobile-Catalog Hyundai Matrix 1.8 GLS	https://www.automobile-catalog.com/car/2002/1172420/hyundai_matrix_1_8_gls.html
EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	4060	1740	1685	Automobile-Catalog Hyundai Matrix 1.8 Style	https://www.automobile-catalog.com/car/2010/1172585/hyundai_matrix_1_8_style.html
EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	4192	1742	1830	Automobile-Catalog Mercedes-Benz Vaneo 1.7 CDI	https://www.automobile-catalog.com/car/2002/1533440/mercedes-benz_vaneo_1_7_cdi.html
EU-AUDI-A4-B6-8E2-SEDAN-4D-01	4548	1772	1428	Automobile-Catalog Audi A4 1.9 TDI	https://www.automobile-catalog.com/car/2002/246995/audi_a4_1_9_tdi.html
EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	4438	1695	1399	Automobile-Catalog Honda Civic Coupe 1.7i LS	https://www.automobile-catalog.com/car/2002/1134170/honda_civic_coupe_1_7i_ls.html
EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	4567	1760	1482	Automobile-Catalog Nissan Primera Sedan 1.8 Acenta	https://www.automobile-catalog.com/car/2002/2283875/nissan_primera_sedan_1_8_acenta.html
EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	4675	1760	1482	Automobile-Catalog Nissan Primera Traveller 1.8 Acenta	https://www.automobile-catalog.com/car/2002/2284265/nissan_primera_traveller_1_8_acenta.html
EU-HONDA-CIVIC-VII-EP3-TYPE-R-HATCHBACK-3D-01	4140	1695	1425	Automobile-Catalog Honda Civic Type-R	https://www.automobile-catalog.com/car/2002/1133960/honda_civic_type-r.html
EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	4803	1765	1469	Automobile-Catalog Skoda Superb 1.8 T	https://www.automobile-catalog.com/car/2002/3137180/skoda_superb_1_8_t.html
```

下一步优先处理

1. 批量闭合 Opel Combo C、Corsa C Van 和 Peugeot Partner I 的 Van/MPV 外廓。
2. 处理 Laguna II Hatch/Grandtour、Scénic I、C5 I Wagon 与 Xsara facelift 分支。
3. 聚类 Cherokee KJ、RAV4 II、Santa Fe I、Terracan、Trailblazer及 Terios I SUV 组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/1172420/hyundai_matrix_1_8_gls.html?utm_source=chatgpt.com "2002 Hyundai Matrix 1.8 GLS Specs Review (90 kW / 122 ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 完成 Renault Laguna II 掀背改款前/后、Grandtour 改款前、Scénic I Phase II 与 Citroën C5 I Break 聚类；Laguna 掀背 Ktype 因覆盖 2005 年改款拆分为两个物理分支。([汽车目录][1])
* 完成 Jeep Cherokee KJ、Toyota RAV4 II、Daihatsu Terios I、Hyundai Santa Fe I 与 Terracan 聚类；RAV4 和 Santa Fe 因生产区间覆盖尺寸变化的改款节点拆分。([汽车目录][2])
* 本轮新增 13 个 READY 输入 Ktype、17 条 READY 映射和 12 个首次创建尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：56
* READY 映射行：64
* PENDING 输入 Ktype：44
* 已确认尺寸组：40
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16223	16223	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16224	16224	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16225	16225	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16226_prefl	16226	Hatchback	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16226_facelift	16226	Hatchback	Laguna II phase II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	HIGH	生产区间覆盖改款；Phase II外廓。	READY
16227_prefl	16227	Hatchback	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16227_facelift	16227	Hatchback	Laguna II phase II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	HIGH	生产区间覆盖改款；Phase II外廓。	READY
16228	16228	Wagon	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	HIGH	Phase I Grandtour五门外廓。	READY
16229	16229	Wagon	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	HIGH	Phase I Grandtour五门外廓。	READY
16231	16231	MPV	Scénic I phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE2-01	HIGH	Phase II五门MPV外廓。	READY
16245	16245	Wagon	C5 I phase I		5	EU-CITROEN-C5-I-BREAK-5D-PREFL-01	HIGH	第一代Phase I Break外廓。	READY
16252_prefl	16252	SUV	RAV4 II pre-facelift	XA20	5	EU-TOYOTA-RAV4-II-XA20-SUV-5D-PREFL-01	HIGH	生产区间覆盖改款；改款前五门外廓。	READY
16252_facelift	16252	SUV	RAV4 II facelift	XA20	5	EU-TOYOTA-RAV4-II-XA20-SUV-5D-FACELIFT-01	HIGH	生产区间覆盖改款；改款后五门外廓。	READY
16278	16278	SUV	Terios I facelift		5	EU-DAIHATSU-TERIOS-I-SUV-5D-FACELIFT-01	HIGH	第一代后期五门SUV外廓。	READY
16282_prefl	16282	SUV	Santa Fe I pre-facelift	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-PREFL-01	HIGH	生产区间覆盖改款；改款前外廓。	READY
16282_facelift	16282	SUV	Santa Fe I facelift	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-FACELIFT-01	HIGH	生产区间覆盖改款；改款后加宽外廓。	READY
16284	16284	SUV	Terracan I	HP	5	EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	HIGH	HP五门SUV标准外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	4496	1819	1866	Automobile-Catalog Jeep Cherokee Sport 2.5 CRD	https://www.automobile-catalog.com/car/2001/1324670/jeep_cherokee_sport_2_5_crd.html
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	4576	1772	1429	Automobile-Catalog Renault Laguna 1.8 16V	https://www.automobile-catalog.com/car/2001/2956595/renault_laguna_1_8_16v.html
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	4598	1772	1433	Automobile-Catalog Renault Laguna 2.0 16V phase II	https://www.automobile-catalog.com/car/2005/2957030/renault_laguna_2_0_16v.html
EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	4695	1772	1443	Automobile-Catalog Renault Laguna Grandtour 1.8 16V	https://www.automobile-catalog.com/car/2001/2956820/renault_laguna_wagon_grandtour_1_8_16v.html
EU-RENAULT-SCENIC-I-MPV-PHASE2-01	4169	1719	1600	Automobile-Catalog Renault Scenic 1.8 16V	https://www.automobile-catalog.com/car/2001/2947535/renault_scenic_1_8_16v.html
EU-CITROEN-C5-I-BREAK-5D-PREFL-01	4756	1770	1516	Automobile-Catalog Citroen C5 Break 2.0 HDi 90	https://www.automobile-catalog.com/car/2001/549350/citroen_c5_break_2_0_hdi_90_x.html
EU-TOYOTA-RAV4-II-XA20-SUV-5D-PREFL-01	4200	1735	1705	Auto-Data Toyota RAV4 II XA20 5-door generation	https://www.auto-data.net/en/toyota-rav4-ii-xa20-5-door-generation-7127
EU-TOYOTA-RAV4-II-XA20-SUV-5D-FACELIFT-01	4220	1735	1690	Auto-Data Toyota RAV4 II XA20 facelift 2.0 D-4D	https://www.auto-data.net/en/toyota-rav4-ii-xa20-facelift-2003-5-door-2.0-16v-d-4-d-116hp-4wd-37162
EU-DAIHATSU-TERIOS-I-SUV-5D-FACELIFT-01	3785	1555	1695	Automobile-Catalog Daihatsu Terios Pur 4WD	https://www.automobile-catalog.com/car/2001/570785/daihatsu_terios_pur_4wd.html
EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-PREFL-01	4500	1820	1730	Auto-Data Hyundai Santa Fe I SM 2.0 CRDi	https://www.auto-data.net/en/hyundai-santa-fe-i-sm-2.0-crdi-112hp-automatic-29379
EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-FACELIFT-01	4500	1845	1730	Automobile-Catalog Hyundai Santa Fe 2.0 CRDi GLS facelift	https://www.automobile-catalog.com/car/2005/1171430/hyundai_santa_fe_2_0_crdi_gls_2wd.html
EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	4710	1860	1795	Hyundai Heritage 2001 Terracan HP	https://www.hyundai.com/kr/ko/brand/brandstory/heritage/2000-terracan-hp
```

下一步优先处理

1. 闭合 Xsara facelift Hatchback、Coupe、Wagon 与 Mégane I Grandtour。
2. 处理 Opel Combo C、Corsa C Van、Peugeot Partner I 的 Van/MPV 分支。
3. 处理 Autobianchi Y10、Fiat Stilo、Maserati Spyder及 Mercedes-Benz MB/CL/SL 剩余外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/2956595/renault_laguna_1_8_16v.html?utm_source=chatgpt.com "2001 Renault Laguna 1.8 16V Specs Review (85 kW / 116 PS / 114 hp) (since January 2001 for Europe )"
[2]: https://www.automobile-catalog.com/car/2001/1324670/jeep_cherokee_sport_2_5_crd.html?utm_source=chatgpt.com "2001 Jeep Cherokee Sport 2.5 CRD (man. 5)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 完成 Xsara facelift Hatchback/Wagon、Mégane I Grandtour Phase II 聚类；Xsara Coupe 复用既有标准改款前及 VTS 改款后尺寸组。([汽车数据网][1])
* 完成 Combo C Van/MPV、Corsa C Van 及 Partner I Van/MPV 的改款前后物理分支；Partner Van 分支直接复用已有 M49、M59 尺寸组。([汽车数据网][2])
* 本轮新增 13 个 READY 输入 Ktype、21 条 READY 映射和 8 个首次创建尺寸组。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：69
* READY 映射行：85
* PENDING 输入 Ktype：31
* 已确认尺寸组：48
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16191_van	16191	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16191_mpv	16191	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16193	16193	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16194	16194	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16195	16195	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16207_van	16207	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16207_mpv	16207	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16208_van	16208	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16208_mpv	16208	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16234	16234	Wagon	Mégane I facelift		5	EU-RENAULT-MEGANE-I-GRANDTOUR-WAGON-5D-FACELIFT-01	HIGH	Phase II Grandtour五门外廓。	READY
16246	16246	Hatchback	Xsara I facelift	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-FACELIFT-01	HIGH	N1 Phase II/III五门外廓尺寸一致。	READY
16247	16247	Coupe	Xsara I facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	HIGH	N0 VTS HDi 109改款后外廓。	READY
16248_prefl	16248	Coupe	Xsara I pre-facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	生产区间覆盖改款；标准改款前外廓。	READY
16248_facelift	16248	Coupe	Xsara I facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	MEDIUM	生产区间覆盖改款；改款后同三维外廓。	READY
16249	16249	Wagon	Xsara I facelift	N2	5	EU-CITROEN-XSARA-I-N2-WAGON-5D-FACELIFT-01	HIGH	N2 Phase II/III旅行车外廓尺寸一致。	READY
16269_van_prefl	16269	Van	Partner I pre-facelift	M49	4	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH	组合车身及生产区间覆盖M49厢式车。	READY
16269_mpv_prefl	16269	MPV	Partner I pre-facelift	M49	5	EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	MEDIUM	组合车身及生产区间覆盖M49乘用分支。	READY
16269_van_facelift	16269	Van	Partner I facelift	M59	4	EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	HIGH	组合车身及生产区间覆盖M59厢式车。	READY
16269_mpv_facelift	16269	MPV	Partner I facelift	M59	5	EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	MEDIUM	组合车身及生产区间覆盖M59乘用分支。	READY
16281_prefl	16281	MPV	Partner I pre-facelift	M49	5	EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	HIGH	生产区间覆盖改款；M49乘用外廓。	READY
16281_facelift	16281	MPV	Partner I facelift	M59	5	EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	HIGH	生产区间覆盖改款；M59乘用外廓。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-COMBO-C-VAN-01	4332	1685	1801	Auto-Data Vauxhall Combo C generation	https://www.auto-data.net/en/vauxhall-combo-c-generation-5098
EU-OPEL-COMBO-C-MPV-01	4320	1685	1800	Auto-Data Opel Combo Tour C generation	https://www.auto-data.net/en/opel-combo-tour-c-generation-490
EU-OPEL-CORSA-C-VAN-3D-01	3817	1646	1440	Auto-Data Opel Corsa C generation	https://www.auto-data.net/en/opel-corsa-c-generation-526
EU-RENAULT-MEGANE-I-GRANDTOUR-WAGON-5D-FACELIFT-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-generation-5586
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-FACELIFT-01	4188	1705	1405	Auto-Data Citroen Xsara N1 Phase II	https://www.auto-data.net/en/citroen-xsara-n1-phase-ii-generation-9026
EU-CITROEN-XSARA-I-N2-WAGON-5D-FACELIFT-01	4369	1705	1420	Auto-Data Citroen Xsara Break N2 Phase II	https://www.auto-data.net/en/citroen-xsara-break-n2-phase-ii-generation-9025
EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	4110	1720	1915	Auto-Data Peugeot Partner I Phase I	https://www.auto-data.net/en/peugeot-partner-i-phase-i-generation-7967
EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-generation-1275
```

下一步优先处理

1. 批量闭合 Autobianchi Y10 的标准前驱、4WD及早期 Turbo外廓分支。
2. 处理 Fiat Stilo、Saab 9-5 Sedan、Chevrolet Trailblazer与Maserati Spyder。
3. 最后处理 Mercedes-Benz MB底盘车、S 63/CL 63及SL 55 AMG和Citroën Jumper多轴距分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-xsara-n1-phase-ii-generation-9026 "Citroen Xsara (N1, Phase II) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/vauxhall-combo-c-generation-5098?utm_source=chatgpt.com "Vauxhall Combo C | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Saab 9-5 3.0 TiD、Fiat Stilo 2.4、Maserati Spyder，以及 Mercedes-Benz S 63 AMG、CL 63 AMG、SL 55 AMG；S 63 AMG 直接复用已有 V220 长轴距组，其余首次建组。Fiat 官方资料确认 2.4 20V 同时覆盖三门与五门 Stilo，且两者外廓不同。([汽车目录][1])
* 闭合 Polo IV：55 kW 1.4 TDI 仅落入 9N1；55 kW 1.4 16V 同时覆盖 9N1 与 9N3，并按三门、五门及改款边界完整派生。([Volkswagen Newsroom][2])
* Fabia I Sedan 因 2004 年改款后车长由 4222 mm 增至 4232 mm，拆分改款前、改款后两个尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：78
* READY 映射行：100
* PENDING 输入 Ktype：22
* 已确认尺寸组：60
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16203	16203	Sedan	9-5 I facelift (2001)	YS3E	4	EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	HIGH	YS3E四门轿车，2001年改款外廓。	READY
16210_3dr	16210	Hatchback	Stilo I	192	3	EU-FIAT-STILO-TYPE192-HATCHBACK-3D-01	HIGH	输入未给门数；三门物理分支。	READY
16210_5dr	16210	Hatchback	Stilo I	192	5	EU-FIAT-STILO-TYPE192-HATCHBACK-5D-01	HIGH	输入未给门数；五门物理分支。	READY
16250	16250	Sedan	S-Class W220 pre-facelift	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	HIGH	S 63 AMG长轴距车身。	READY
16251	16251	Coupe	CL-Class C215	C215	2	EU-MERCEDES-BENZ-CL-C215-COUPE-AMG-01	HIGH	C215双门CL 63 AMG外廓。	READY
16258	16258	Convertible	SL R230 pre-facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-CONVERTIBLE-PREFL-AMG-01	HIGH	R230早期SL 55 AMG外廓。	READY
16271	16271	Convertible	Spyder M138	M138	2	EU-MASERATI-SPYDER-M138-CONVERTIBLE-2D-01	HIGH	M138双门双座敞篷车身。	READY
16279_3dr	16279	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	MEDIUM	输入未给门数；9N1三门物理分支。	READY
16279_5dr	16279	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	MEDIUM	输入未给门数；9N1五门物理分支。	READY
16290_prefl	16290	Sedan	Fabia I pre-facelift	6Y3	4	EU-SKODA-FABIA-I-6Y3-SEDAN-4D-PREFL-01	MEDIUM	生产区间覆盖2004年改款；改款前四门外廓。	READY
16290_facelift	16290	Sedan	Fabia I facelift	6Y3	4	EU-SKODA-FABIA-I-6Y3-SEDAN-4D-FACELIFT-01	MEDIUM	生产区间覆盖2004年改款；改款后四门外廓。	READY
16300_3dr_prefl	16300	Hatchback	Polo IV pre-facelift	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	MEDIUM	生产区间覆盖改款；9N1三门分支。	READY
16300_3dr_facelift	16300	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	MEDIUM	生产区间覆盖改款；9N3三门分支。	READY
16300_5dr_prefl	16300	Hatchback	Polo IV pre-facelift	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	MEDIUM	生产区间覆盖改款；9N1五门分支。	READY
16300_5dr_facelift	16300	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	MEDIUM	生产区间覆盖改款；9N3五门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449	Automobile-Catalog Saab 9-5 3.0 TiD	https://www.automobile-catalog.com/car/2002/3033920/saab_9-5_3_0_tid.html
EU-FIAT-STILO-TYPE192-HATCHBACK-3D-01	4182	1784	1475	Fiat/Stellantis official Stilo technical data	https://www.media.stellantis.com/it-it/fiat/press/fiat-stilo-adotta-nuovi-motori-rispettosi-dell-ambiente
EU-FIAT-STILO-TYPE192-HATCHBACK-5D-01	4253	1756	1525	Fiat/Stellantis official Stilo technical data	https://www.media.stellantis.com/it-it/fiat/press/fiat-stilo-adotta-nuovi-motori-rispettosi-dell-ambiente
EU-MERCEDES-BENZ-CL-C215-COUPE-AMG-01	4993	1857	1390	Mercedes-Benz Public Archive CL 63 AMG	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CL-63-AMG.xhtml?oid=4512
EU-MERCEDES-BENZ-SL-R230-CONVERTIBLE-PREFL-AMG-01	4535	1815	1295	Mercedes-Benz Public Archive SL 55 AMG	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/SL-55-AMG.xhtml?oid=2461800
EU-MASERATI-SPYDER-M138-CONVERTIBLE-2D-01	4303	1822	1305	Maserati official Spyder model archive;Automobile-Catalog Maserati Spyder Cambiocorsa	https://www.maserati.com/sg/en/brand/maserati-classic-cars/gran-turismo/spyder;https://www.automobile-catalog.com/car/2002/1447160/maserati_spyder_cambiocorsa.html
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N 1.4 TDI	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-1.4-tdi-75hp-8444
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N 1.4 TDI	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-1.4-tdi-75hp-8444
EU-SKODA-FABIA-I-6Y3-SEDAN-4D-PREFL-01	4222	1646	1449	Automobile-Catalog Skoda Fabia Sedan 2.0	https://www.automobile-catalog.com/car/2002/3136490/skoda_fabia_sedan_2_0.html
EU-SKODA-FABIA-I-6Y3-SEDAN-4D-FACELIFT-01	4232	1646	1449	Automobile-Catalog Skoda Fabia Sedan 2.0 facelift	https://www.automobile-catalog.com/car/2005/3136955/skoda_fabia_sedan_2_0.html
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N3 three-door	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-3-d-8412
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N3 five-door	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.6-105hp-5-d-8421
```

## 下一步优先处理

1. 聚类 Autobianchi Y10 的标准前驱、Turbo、4WD及改款分支。
2. 闭合 Renault Kangoo I MPV/4×4、Chevrolet Trailblazer和 Citroën Jumper I 多轴距、多车顶分支。
3. 最后处理 Mercedes-Benz MB100底盘车及剩余特殊商用车映射。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/3033920/saab_9-5_3_0_tid.html?utm_source=chatgpt.com "2002 Saab 9-5 3.0 TiD Specs Review (129.5 kW / 176 PS / 174 hp) (for Europe )"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152 "Vehicle data Polo IV profile | Volkswagen Newsroom"
[3]: https://www.automobile-catalog.com/car/2001/3136205/skoda_fabia_sedan_2_0.html?utm_source=chatgpt.com "2001 Skoda Fabia Sedan 2.0 Specs Review (85 kW ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 Autobianchi Y10 第一、第二系列的标准车身、GT 与 4WD 外廓聚类。第一系列标准车身为 `3392×1507×1423`，第二系列标准车身高度增至 `1440`，第二系列 GT 高度为 `1450`，4WD 车身宽高为 `1537×1460`。([汽车目录][1])
* 完成 Kangoo I 普通 MPV 改款前后及 4×4 外廓；由于已有改款 MPV 组的高度为 `1885`，而当前普通 1.2/1.6/1.5 dCi 资料为 `1825`，按冲突规则新建序号 `-02`，未覆盖已有组。([汽车目录][2])
* Chevrolet TrailBlazer 4.2 AWD 拆分为 GMT360 标准轴距与 GMT370 EXT 长轴距两个外廓。([汽车目录][3])
* Citroën Jumper I 的两驱 Bus、Pritsche/Fahrgestell 和 Kasten 已直接关联跨批次缓存中的 230P、230、230L 尺寸组，未重复输出尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：96
* READY 映射行：134
* PENDING 输入 Ktype：4
* 已确认尺寸组：70
* 剩余 PENDING：`16196`、`16197`、`16265`、`16268`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16213_s1	16213	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	同一Ktype覆盖第一系列外廓。	READY
16213_s2	16213	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	同一Ktype覆盖第二系列外廓。	READY
16214	16214	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	第一系列三门标准外廓。	READY
16215	16215	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	第一系列Turbo三门外廓。	READY
16216	16216	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-4X4-01	HIGH	第一系列4WD外廓。	READY
16217_s1	16217	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	同一Ktype覆盖第一系列外廓。	READY
16217_s2	16217	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	同一Ktype覆盖第二系列外廓。	READY
16218	16218	Hatchback	Y10 Series II GT	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	HIGH	第二系列GT三门外廓。	READY
16219	16219	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	第二系列1.1三门外廓。	READY
16220	16220	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-4X4-01	HIGH	第二系列1.1 4WD外廓。	READY
16221	16221	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	第二系列1.1三门外廓。	READY
16222	16222	Hatchback	Y10 Series II GT	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	HIGH	第二系列GT催化版本外廓。	READY
16205_prefl	16205	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16205_facelift	16205	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
16206	16206	MPV	Kangoo I 4x4	KC	5	EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	HIGH	4x4专用外廓。	READY
16209_prefl	16209	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16209_facelift	16209	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
16264_swb_lowroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	Bus短轴低顶物理分支。	READY
16264_mwb_lowroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	Bus中轴低顶物理分支。	READY
16264_mwb_highroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	Bus中轴高顶物理分支。	READY
16266_swb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	MEDIUM	底盘车短轴14系列分支。	READY
16266_mwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	MEDIUM	底盘车中轴14系列分支。	READY
16266_lwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	MEDIUM	底盘车长轴14系列分支。	READY
16266_maxi_mwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	MEDIUM	底盘车Maxi中轴分支。	READY
16266_maxi_lwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	MEDIUM	底盘车Maxi长轴分支。	READY
16267_swb_highroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	MEDIUM	厢式车短轴高顶分支。	READY
16267_mwb_lowroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	MEDIUM	厢式车中轴低顶分支。	READY
16267_mwb_highroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	MEDIUM	厢式车中轴高顶分支。	READY
16267_lwb_h2455	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	MEDIUM	厢式车长轴2455毫米高分支。	READY
16267_lwb_h2470	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	MEDIUM	厢式车长轴2470毫米高分支。	READY
16280_swb	16280	SUV	TrailBlazer I	GMT360	5	EU-CHEVROLET-TRAILBLAZER-I-GMT360-SUV-SWB-01	MEDIUM	标准轴距五门SUV分支。	READY
16280_lwb	16280	SUV	TrailBlazer I EXT	GMT370	5	EU-CHEVROLET-TRAILBLAZER-I-GMT370-SUV-LWB-01	MEDIUM	EXT长轴距七座外廓分支。	READY
16285_prefl	16285	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16285_facelift	16285	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	3392	1507	1423	Automobile-Catalog Lancia Y10 Fire Series I	https://www.automobile-catalog.com/car/1985/51455/lancia_y10_fire.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	3392	1507	1440	Automobile-Catalog Lancia Y10 Fire 1.0 Series II	https://www.automobile-catalog.com/car/1990/1381070/lancia_y10_fire_1_0.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	3392	1507	1450	Automobile-Catalog Lancia Y10 GT i.e. Series II	https://www.automobile-catalog.com/car/1989/1381130/lancia_y10_gt_i_e_.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-4X4-01	3392	1537	1460	Automobile-Catalog Lancia Y10 4WD Series I	https://www.automobile-catalog.com/car/1986/1380740/lancia_y10_4wd.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-4X4-01	3392	1537	1460	Automobile-Catalog Lancia Y10 4WD i.e. Series II	https://www.automobile-catalog.com/car/1990/1381160/lancia_y10_4wd_i_e_.html
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	3995	1672	1835	Automobile-Catalog Renault Kangoo 1.6 16V phase I	https://www.automobile-catalog.com/car/2001/2948660/renault_kangoo_1_6_16v.html
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	4035	1672	1825	Automobile-Catalog Renault Kangoo 1.6 16V phase II	https://www.automobile-catalog.com/car/2004/2948810/renault_kangoo_1_6_16v.html
EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	4046	1672	1870	Automobile-Catalog Renault Kangoo 4x4 1.6 16V	https://www.automobile-catalog.com/car/2004/2948855/renault_kangoo_4x4_1_6_16v.html
EU-CHEVROLET-TRAILBLAZER-I-GMT360-SUV-SWB-01	4871	1897	1892	Automobile-Catalog Chevrolet TrailBlazer LT 4WD 4200	https://www.automobile-catalog.com/car/2003/1203845/chevrolet_trailblazer_lt_4wd_4200_v-8.html
EU-CHEVROLET-TRAILBLAZER-I-GMT370-SUV-LWB-01	5278	1897	1958	Automobile-Catalog Chevrolet TrailBlazer EXT LT 4WD 4200	https://www.automobile-catalog.com/car/2003/1203995/chevrolet_trailblazer_ext_lt_4wd_4200_v-8.html
```

## 下一步优先处理

1. 确认 Mercedes-Benz MB W631 Pritsche/Fahrgestell 的短轴、长轴及改款边界，处理 `16196`、`16197`。
2. 确认 Jumper I Dangel 4×4 Bus 与 Van 实际开放的轴距、车顶组合，处理 `16265`、`16268`；不直接假定所有两驱分支均可复用。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1985/30905/lancia_y10_turbo.html?utm_source=chatgpt.com "1985 Lancia Y10 Turbo (man. 5) (model since mid-year ..."
[2]: https://www.automobile-catalog.com/car/2001/2948660/renault_kangoo_1_6_16v.html?utm_source=chatgpt.com "2001 Renault Kangoo 1.6 16V Specs Review (70 kW / 95 ..."
[3]: https://www.automobile-catalog.com/car/2003/1203995/chevrolet_trailblazer_ext_lt_4wd_4200_v-8.html?utm_source=chatgpt.com "2003 Chevrolet Trailblazer Ext LT 4WD 4200 (aut. 4)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
更新点

* 已闭合 `16268` 的 Jumper I 2.8 HDi 4×4 厢式车分支。可确认的改款前配置包括短轴低顶 `31C`、中轴高顶 `31MH` 和高载重中轴高顶 `35MH`；其外廓分别为 `4670×2000×2150`、`5010×2000×2470`、`5010×2000×2550 mm`。因三维与已有两驱缓存组不完全一致，按冲突规则新建 4×4 专用尺寸组，未覆盖原组。([www.largus.fr][1])
* `16196`、`16197` 仍缺 MB100 W631 Pritsche/Fahrgestell 各轴距和改款阶段的同配置完整三维；`16265` 仍缺 Jumper I 2.8 HDi 4×4 Bus 的直接配置边界，未用厢式车资料替代。

当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* READY 映射行：137
* PENDING 输入 Ktype：3
* 已确认尺寸组：73
* 剩余 PENDING：`16196`、`16197`、`16265`
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16268_swb_lowroof	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-SWB-H2150-01	HIGH	31C短轴低顶4×4厢式车分支。	READY
16268_mwb_highroof	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2470-01	HIGH	31MH中轴高顶4×4厢式车分支。	READY
16268_mwb_highroof_35	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2550-01	HIGH	35MH高载重中轴高顶4×4厢式车分支。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPER-I-230L-VAN-4X4-SWB-H2150-01	4670	2000	2150	L'Argus Citroën Jumper Fg 31C 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/31C%2B28HDi%2B4x4-3294.html
EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2470-01	5010	2000	2470	L'Argus Citroën Jumper Fg 31MH 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/31MH%2B28HDi%2B4x4-3322.html
EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2550-01	5010	2000	2550	L'Argus Citroën Jumper Fg 35MH 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/35MH%2B28HDi%2B4x4-3344.html
```

下一步优先处理

1. 从 MB100 W631 原厂或车身型录确认 Pritsche/Fahrgestell 的短轴、长轴以及 1992 年改款前后完整外廓，处理 `16196`、`16197`。
2. 查明 Jumper I 2.8 HDi 4×4 Bus 实际销售的短轴/中轴及车顶组合，处理 `16265`，不直接套用厢式车分支。

推进信号：CONTINUE

[1]: https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/35MH%2B28HDi%2B4x4-3344.html "www.largus.fr"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12401-12500_ktype_dimension_mapping_final.tsv
- all_12401-12500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 剩余 `16196`、`16197`、`16265` 已闭合并转为 `READY`。
* 已完成轻量机械收尾：固定表头、主键唯一、映射引用闭合、尺寸及来源非空、下载文件存在。
* 两张表不存在 `PENDING`、缺失引用、孤立尺寸组或重复主键。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：140
* PENDING：0
* DIMENSION_GROUP：93
* 引用缺失：0
* 孤立尺寸组：0
* 重复主键：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16189	16189	Hatchback	3 Series E46 Compact	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH	E46/5 三门 Compact 车身。	READY
16190	16190	Hatchback	3 Series E46 Compact	E46/5	3	EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	HIGH	E46/5 三门 Compact 车身。	READY
16191_van	16191	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16191_mpv	16191	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16193	16193	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16194	16194	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16195	16195	Van	Corsa C		3	EU-OPEL-CORSA-C-VAN-3D-01	HIGH	三门Corsa C厢式车外廓。	READY
16196	16196	Pickup	MB100 W631	631.340	2	EU-MERCEDES-BENZ-MB100-W631-PICKUP-LWB-01	HIGH	631.340长轴距双门平台/底盘车外廓。	READY
16197	16197	Pickup	MB100 W631	631.340	2	EU-MERCEDES-BENZ-MB100-W631-PICKUP-LWB-01	HIGH	631.340长轴距双门平台/底盘车外廓。	READY
16198	16198	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46 四门轿车车身。	READY
16199	16199	Coupe	3 Series E46	E46/2	2	EU-BMW-3-E46-COUPE-2D-01	HIGH	E46/2 双门 Coupe 车身。	READY
16201	16201	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46 四门轿车车身。	READY
16202	16202	Wagon	3 Series E46	E46/3	5	EU-BMW-3-E46-TOURING-5D-01	HIGH	E46/3 五门 Touring 车身。	READY
16203	16203	Sedan	9-5 I facelift (2001)	YS3E	4	EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	HIGH	YS3E四门轿车，2001年改款外廓。	READY
16204	16204	Wagon	9-5 I facelift (2001)	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	HIGH	YS3E 五门旅行车，2001 年改款外廓。	READY
16205_prefl	16205	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16205_facelift	16205	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
16206	16206	MPV	Kangoo I 4x4	KC	5	EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	HIGH	4x4专用外廓。	READY
16207_van	16207	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16207_mpv	16207	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16208_van	16208	Van	Combo C		4	EU-OPEL-COMBO-C-VAN-01	HIGH	Combo C厢式车外廓。	READY
16208_mpv	16208	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-01	MEDIUM	组合车身字段覆盖Combo Tour乘用分支。	READY
16209_prefl	16209	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16209_facelift	16209	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
16210_3dr	16210	Hatchback	Stilo I	192	3	EU-FIAT-STILO-TYPE192-HATCHBACK-3D-01	HIGH	输入未给门数；三门物理分支。	READY
16210_5dr	16210	Hatchback	Stilo I	192	5	EU-FIAT-STILO-TYPE192-HATCHBACK-5D-01	HIGH	输入未给门数；五门物理分支。	READY
16211	16211	Wagon	Mégane III		5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Mégane III Grandtour 五门车身。	READY
16212_prefl	16212	MPV	Matrix I pre-facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	HIGH	生产区间跨改款；改款前外廓。	READY
16212_facelift	16212	MPV	Matrix I facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	HIGH	生产区间跨改款；改款后加长外廓。	READY
16213_s1	16213	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	同一Ktype覆盖第一系列外廓。	READY
16213_s2	16213	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	同一Ktype覆盖第二系列外廓。	READY
16214	16214	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	第一系列三门标准外廓。	READY
16215	16215	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	第一系列Turbo三门外廓。	READY
16216	16216	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-4X4-01	HIGH	第一系列4WD外廓。	READY
16217_s1	16217	Hatchback	Y10 Series I	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	HIGH	同一Ktype覆盖第一系列外廓。	READY
16217_s2	16217	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	同一Ktype覆盖第二系列外廓。	READY
16218	16218	Hatchback	Y10 Series II GT	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	HIGH	第二系列GT三门外廓。	READY
16219	16219	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	第二系列1.1三门外廓。	READY
16220	16220	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-4X4-01	HIGH	第二系列1.1 4WD外廓。	READY
16221	16221	Hatchback	Y10 Series II	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	HIGH	第二系列1.1三门外廓。	READY
16222	16222	Hatchback	Y10 Series II GT	156	3	EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	HIGH	第二系列GT催化版本外廓。	READY
16223	16223	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16224	16224	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16225	16225	SUV	Cherokee III	KJ	5	EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	HIGH	KJ五门SUV外廓。	READY
16226_prefl	16226	Hatchback	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16226_facelift	16226	Hatchback	Laguna II phase II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	HIGH	生产区间覆盖改款；Phase II外廓。	READY
16227_prefl	16227	Hatchback	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16227_facelift	16227	Hatchback	Laguna II phase II		5	EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	HIGH	生产区间覆盖改款；Phase II外廓。	READY
16228	16228	Wagon	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	HIGH	Phase I Grandtour五门外廓。	READY
16229	16229	Wagon	Laguna II phase I		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	HIGH	Phase I Grandtour五门外廓。	READY
16231	16231	MPV	Scénic I phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE2-01	HIGH	Phase II五门MPV外廓。	READY
16232	16232	Hatchback	Mégane I facelift	BA0	5	EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	HIGH	BA0 五门掀背，Phase II 外廓。	READY
16233	16233	Sedan	Mégane I facelift	LA0	4	EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	HIGH	LA0 四门 Classic，Phase II 外廓。	READY
16234	16234	Wagon	Mégane I facelift		5	EU-RENAULT-MEGANE-I-GRANDTOUR-WAGON-5D-FACELIFT-01	HIGH	Phase II Grandtour五门外廓。	READY
16242	16242	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16243	16243	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16244	16244	MPV	Vaneo	W414	5	EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	HIGH	W414 五门 MPV 外廓。	READY
16245	16245	Wagon	C5 I phase I		5	EU-CITROEN-C5-I-BREAK-5D-PREFL-01	HIGH	第一代Phase I Break外廓。	READY
16246	16246	Hatchback	Xsara I facelift	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-FACELIFT-01	HIGH	N1 Phase II/III五门外廓尺寸一致。	READY
16247	16247	Coupe	Xsara I facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	HIGH	N0 VTS HDi 109改款后外廓。	READY
16248_prefl	16248	Coupe	Xsara I pre-facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	生产区间覆盖改款；标准改款前外廓。	READY
16248_facelift	16248	Coupe	Xsara I facelift	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	MEDIUM	生产区间覆盖改款；改款后同三维外廓。	READY
16249	16249	Wagon	Xsara I facelift	N2	5	EU-CITROEN-XSARA-I-N2-WAGON-5D-FACELIFT-01	HIGH	N2 Phase II/III旅行车外廓尺寸一致。	READY
16250	16250	Sedan	S-Class W220 pre-facelift	V220	4	EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	HIGH	S 63 AMG长轴距车身。	READY
16251	16251	Coupe	CL-Class C215	C215	2	EU-MERCEDES-BENZ-CL-C215-COUPE-AMG-01	HIGH	C215双门CL 63 AMG外廓。	READY
16252_prefl	16252	SUV	RAV4 II pre-facelift	XA20	5	EU-TOYOTA-RAV4-II-XA20-SUV-5D-PREFL-01	HIGH	生产区间覆盖改款；改款前五门外廓。	READY
16252_facelift	16252	SUV	RAV4 II facelift	XA20	5	EU-TOYOTA-RAV4-II-XA20-SUV-5D-FACELIFT-01	HIGH	生产区间覆盖改款；改款后五门外廓。	READY
16253_3dr	16253	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	MEDIUM	输入未给门数；按 1J1 三门物理分支派生。	READY
16253_5dr	16253	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	MEDIUM	输入未给门数；按 1J1 五门物理分支派生。	READY
16254	16254	Sedan	Omega B facelift	V94	4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH	V94 四门改款轿车。	READY
16255	16255	Wagon	Omega B facelift	V94	5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH	V94 五门 Caravan 改款车身。	READY
16258	16258	Convertible	SL R230 pre-facelift	R230	2	EU-MERCEDES-BENZ-SL-R230-CONVERTIBLE-PREFL-AMG-01	HIGH	R230早期SL 55 AMG外廓。	READY
16259	16259	Sedan	406 facelift	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	8B 四门 Phase II 轿车。	READY
16260	16260	Wagon	406 facelift		5	EU-PEUGEOT-406-WAGON-FACELIFT-01	HIGH	五门 406 Break Phase II 车身。	READY
16261	16261	Sedan	A4 B6	8E2	4	EU-AUDI-A4-B6-8E2-SEDAN-4D-01	HIGH	8E2 四门轿车外廓。	READY
16262	16262	Coupe	Civic VII	EM2	2	EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	HIGH	EM2 双门 Coupe 外廓。	READY
16263	16263	Coupe	Civic VII	EM2	2	EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	HIGH	EM2 双门 Coupe 外廓。	READY
16264_swb_lowroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	MEDIUM	Bus短轴低顶物理分支。	READY
16264_mwb_lowroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	MEDIUM	Bus中轴低顶物理分支。	READY
16264_mwb_highroof	16264	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	MEDIUM	Bus中轴高顶物理分支。	READY
16265	16265	MPV	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-4X4-MWB-H2550-01	MEDIUM	35MH中轴高顶4×4 Bus外廓。	READY
16266_swb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	MEDIUM	底盘车短轴14系列分支。	READY
16266_mwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	MEDIUM	底盘车中轴14系列分支。	READY
16266_lwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	MEDIUM	底盘车长轴14系列分支。	READY
16266_maxi_mwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	MEDIUM	底盘车Maxi中轴分支。	READY
16266_maxi_lwb	16266	Pickup	Jumper I	230	2	EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	MEDIUM	底盘车Maxi长轴分支。	READY
16267_swb_highroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	MEDIUM	厢式车短轴高顶分支。	READY
16267_mwb_lowroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	MEDIUM	厢式车中轴低顶分支。	READY
16267_mwb_highroof	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	MEDIUM	厢式车中轴高顶分支。	READY
16267_lwb_h2455	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	MEDIUM	厢式车长轴2455毫米高分支。	READY
16267_lwb_h2470	16267	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	MEDIUM	厢式车长轴2470毫米高分支。	READY
16268_swb_lowroof	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-SWB-H2150-01	HIGH	31C短轴低顶4×4厢式车分支。	READY
16268_mwb_highroof	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2470-01	HIGH	31MH中轴高顶4×4厢式车分支。	READY
16268_mwb_highroof_35	16268	Van	Jumper I	230L		EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2550-01	HIGH	35MH高载重中轴高顶4×4厢式车分支。	READY
16269_van_prefl	16269	Van	Partner I pre-facelift	M49	4	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	HIGH	组合车身及生产区间覆盖M49厢式车。	READY
16269_mpv_prefl	16269	MPV	Partner I pre-facelift	M49	5	EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	MEDIUM	组合车身及生产区间覆盖M49乘用分支。	READY
16269_van_facelift	16269	Van	Partner I facelift	M59	4	EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	HIGH	组合车身及生产区间覆盖M59厢式车。	READY
16269_mpv_facelift	16269	MPV	Partner I facelift	M59	5	EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	MEDIUM	组合车身及生产区间覆盖M59乘用分支。	READY
16270_3dr	16270	Hatchback	206 I		3	EU-PEUGEOT-206-I-HATCHBACK-3D-01	HIGH	输入覆盖三门和五门；三门物理分支。	READY
16270_5dr	16270	Hatchback	206 I		5	EU-PEUGEOT-206-I-HATCHBACK-5D-01	HIGH	输入覆盖三门和五门；五门物理分支。	READY
16271	16271	Convertible	Spyder M138	M138	2	EU-MASERATI-SPYDER-M138-CONVERTIBLE-2D-01	HIGH	M138双门双座敞篷车身。	READY
16272	16272	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16273	16273	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16274	16274	Sedan	Primera III	P12	4	EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	HIGH	P12 四门轿车外廓。	READY
16275	16275	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16276	16276	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16277	16277	Wagon	Primera III	WP12	5	EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	HIGH	WP12 五门旅行车外廓。	READY
16278	16278	SUV	Terios I facelift		5	EU-DAIHATSU-TERIOS-I-SUV-5D-FACELIFT-01	HIGH	第一代后期五门SUV外廓。	READY
16279_3dr	16279	Hatchback	Polo IV	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	MEDIUM	输入未给门数；9N1三门物理分支。	READY
16279_5dr	16279	Hatchback	Polo IV	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	MEDIUM	输入未给门数；9N1五门物理分支。	READY
16280_swb	16280	SUV	TrailBlazer I	GMT360	5	EU-CHEVROLET-TRAILBLAZER-I-GMT360-SUV-SWB-01	MEDIUM	标准轴距五门SUV分支。	READY
16280_lwb	16280	SUV	TrailBlazer I EXT	GMT370	5	EU-CHEVROLET-TRAILBLAZER-I-GMT370-SUV-LWB-01	MEDIUM	EXT长轴距七座外廓分支。	READY
16281_prefl	16281	MPV	Partner I pre-facelift	M49	5	EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	HIGH	生产区间覆盖改款；M49乘用外廓。	READY
16281_facelift	16281	MPV	Partner I facelift	M59	5	EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	HIGH	生产区间覆盖改款；M59乘用外廓。	READY
16282_prefl	16282	SUV	Santa Fe I pre-facelift	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-PREFL-01	HIGH	生产区间覆盖改款；改款前外廓。	READY
16282_facelift	16282	SUV	Santa Fe I facelift	SM	5	EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-FACELIFT-01	HIGH	生产区间覆盖改款；改款后加宽外廓。	READY
16283	16283	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	HIGH	GD 五门掀背车身。	READY
16284	16284	SUV	Terracan I	HP	5	EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	HIGH	HP五门SUV标准外廓。	READY
16285_prefl	16285	MPV	Kangoo I phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	生产区间覆盖改款；Phase I外廓。	READY
16285_facelift	16285	MPV	Kangoo I phase II	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	HIGH	生产区间覆盖改款；Phase II普通MPV外廓。	READY
16286_prefl	16286	MPV	Matrix I pre-facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	HIGH	生产区间跨改款；改款前外廓。	READY
16286_facelift	16286	MPV	Matrix I facelift	FC	5	EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	HIGH	生产区间跨改款；改款后加长外廓。	READY
16287	16287	Hatchback	Civic VII Type-R	EP3	3	EU-HONDA-CIVIC-VII-EP3-TYPE-R-HATCHBACK-3D-01	HIGH	EP3 三门 Type-R 外廓。	READY
16288	16288	Sedan	406 facelift	8B	4	EU-PEUGEOT-406-SEDAN-FACELIFT-01	HIGH	8B 四门 Phase II 轿车。	READY
16289	16289	Wagon	406 facelift		5	EU-PEUGEOT-406-WAGON-FACELIFT-01	HIGH	五门 406 Break Phase II 车身。	READY
16290_prefl	16290	Sedan	Fabia I pre-facelift	6Y3	4	EU-SKODA-FABIA-I-6Y3-SEDAN-4D-PREFL-01	MEDIUM	生产区间覆盖2004年改款；改款前四门外廓。	READY
16290_facelift	16290	Sedan	Fabia I facelift	6Y3	4	EU-SKODA-FABIA-I-6Y3-SEDAN-4D-FACELIFT-01	MEDIUM	生产区间覆盖2004年改款；改款后四门外廓。	READY
16291	16291	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16292	16292	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16293	16293	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16294	16294	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16295	16295	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	HIGH	3U4 四门轿车外廓。	READY
16296	16296	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16297	16297	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16298	16298	Sedan	Passat B5 pre-facelift	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	3B2 四门改款前轿车。	READY
16299	16299	Wagon	Passat B5 pre-facelift	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	HIGH	3B5 五门 Variant 改款前车身。	READY
16300_3dr_prefl	16300	Hatchback	Polo IV pre-facelift	9N1	3	EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	MEDIUM	生产区间覆盖改款；9N1三门分支。	READY
16300_3dr_facelift	16300	Hatchback	Polo IV facelift	9N3	3	EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	MEDIUM	生产区间覆盖改款；9N3三门分支。	READY
16300_5dr_prefl	16300	Hatchback	Polo IV pre-facelift	9N1	5	EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	MEDIUM	生产区间覆盖改款；9N1五门分支。	READY
16300_5dr_facelift	16300	Hatchback	Polo IV facelift	9N3	5	EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	MEDIUM	生产区间覆盖改款；9N3五门分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_12401-12500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E46-COMPACT-HATCHBACK-3D-01	4262	1751	1408	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-OPEL-COMBO-C-VAN-01	4332	1685	1801	Auto-Data Vauxhall Combo C generation	https://www.auto-data.net/en/vauxhall-combo-c-generation-5098
EU-OPEL-COMBO-C-MPV-01	4320	1685	1800	Auto-Data Opel Combo Tour C generation	https://www.auto-data.net/en/opel-combo-tour-c-generation-490
EU-OPEL-CORSA-C-VAN-3D-01	3817	1646	1440	Auto-Data Opel Corsa C generation	https://www.auto-data.net/en/opel-corsa-c-generation-526
EU-MERCEDES-BENZ-MB100-W631-PICKUP-LWB-01	4996	2008	1985	Swiss type approval 3M5145 Mercedes-Benz MB100 D 631.340 bridge	https://www.dauto.ch/typenscheine/mercedes-benz-mb100-d-3m5145-vsa63134013-x
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E46-COUPE-2D-01	4488	1757	1369	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-BMW-3-E46-TOURING-5D-01	4478	1739	1409	BMW Belgium official E46 technical data MY2004	https://www.press.bmwgroup.com/belux/article/attachment/T0032927FR/53363
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449	Automobile-Catalog Saab 9-5 3.0 TiD	https://www.automobile-catalog.com/car/2002/3033920/saab_9-5_3_0_tid.html
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501	Auto-Data Saab 9-5 model technical specifications	https://www.auto-data.net/en/saab-9-5-model-1271
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	3995	1672	1835	Automobile-Catalog Renault Kangoo 1.6 16V phase I	https://www.automobile-catalog.com/car/2001/2948660/renault_kangoo_1_6_16v.html
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	4035	1672	1825	Automobile-Catalog Renault Kangoo 1.6 16V phase II	https://www.automobile-catalog.com/car/2004/2948810/renault_kangoo_1_6_16v.html
EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	4046	1672	1870	Automobile-Catalog Renault Kangoo 4x4 1.6 16V	https://www.automobile-catalog.com/car/2004/2948855/renault_kangoo_4x4_1_6_16v.html
EU-FIAT-STILO-TYPE192-HATCHBACK-3D-01	4182	1784	1475	Fiat/Stellantis official Stilo technical data	https://www.media.stellantis.com/it-it/fiat/press/fiat-stilo-adotta-nuovi-motori-rispettosi-dell-ambiente
EU-FIAT-STILO-TYPE192-HATCHBACK-5D-01	4253	1756	1525	Fiat/Stellantis official Stilo technical data	https://www.media.stellantis.com/it-it/fiat/press/fiat-stilo-adotta-nuovi-motori-rispettosi-dell-ambiente
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Automobile-Catalog Renault Megane Estate Grandtour 1.5 dCi 110	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-HYUNDAI-MATRIX-FC-MPV-5D-PREFL-01	4025	1740	1685	Automobile-Catalog Hyundai Matrix 1.8 GLS	https://www.automobile-catalog.com/car/2002/1172420/hyundai_matrix_1_8_gls.html
EU-HYUNDAI-MATRIX-FC-MPV-5D-FACELIFT-01	4060	1740	1685	Automobile-Catalog Hyundai Matrix 1.8 Style	https://www.automobile-catalog.com/car/2010/1172585/hyundai_matrix_1_8_style.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-01	3392	1507	1423	Automobile-Catalog Lancia Y10 Fire Series I	https://www.automobile-catalog.com/car/1985/51455/lancia_y10_fire.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-01	3392	1507	1440	Automobile-Catalog Lancia Y10 Fire 1.0 Series II	https://www.automobile-catalog.com/car/1990/1381070/lancia_y10_fire_1_0.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES1-4X4-01	3392	1537	1460	Automobile-Catalog Lancia Y10 4WD Series I	https://www.automobile-catalog.com/car/1986/1380740/lancia_y10_4wd.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-GT-01	3392	1507	1450	Automobile-Catalog Lancia Y10 GT i.e. Series II	https://www.automobile-catalog.com/car/1989/1381130/lancia_y10_gt_i_e_.html
EU-AUTOBIANCHI-Y10-156-HATCHBACK-3D-SERIES2-4X4-01	3392	1537	1460	Automobile-Catalog Lancia Y10 4WD i.e. Series II	https://www.automobile-catalog.com/car/1990/1381160/lancia_y10_4wd_i_e_.html
EU-JEEP-CHEROKEE-III-KJ-SUV-5D-01	4496	1819	1866	Automobile-Catalog Jeep Cherokee Sport 2.5 CRD	https://www.automobile-catalog.com/car/2001/1324670/jeep_cherokee_sport_2_5_crd.html
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-PREFL-01	4576	1772	1429	Automobile-Catalog Renault Laguna 1.8 16V	https://www.automobile-catalog.com/car/2001/2956595/renault_laguna_1_8_16v.html
EU-RENAULT-LAGUNA-II-HATCHBACK-5D-FACELIFT-01	4598	1772	1433	Automobile-Catalog Renault Laguna 2.0 16V phase II	https://www.automobile-catalog.com/car/2005/2957030/renault_laguna_2_0_16v.html
EU-RENAULT-LAGUNA-II-GRANDTOUR-5D-PREFL-01	4695	1772	1443	Automobile-Catalog Renault Laguna Grandtour 1.8 16V	https://www.automobile-catalog.com/car/2001/2956820/renault_laguna_wagon_grandtour_1_8_16v.html
EU-RENAULT-SCENIC-I-MPV-PHASE2-01	4169	1719	1600	Automobile-Catalog Renault Scenic 1.8 16V	https://www.automobile-catalog.com/car/2001/2947535/renault_scenic_1_8_16v.html
EU-RENAULT-MEGANE-I-BA0-HATCHBACK-5D-FACELIFT-01	4164	1698	1420	Auto-Data Renault Megane model technical specifications	https://www.auto-data.net/en/renault-megane-model-1026
EU-RENAULT-MEGANE-I-LA-SEDAN-FACELIFT-01	4436	1698	1420	Auto-Data Renault Megane model technical specifications	https://www.auto-data.net/en/renault-megane-model-1026
EU-RENAULT-MEGANE-I-GRANDTOUR-WAGON-5D-FACELIFT-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-generation-5586
EU-MERCEDES-BENZ-VANEO-W414-MPV-5D-01	4192	1742	1830	Automobile-Catalog Mercedes-Benz Vaneo 1.7 CDI	https://www.automobile-catalog.com/car/2002/1533440/mercedes-benz_vaneo_1_7_cdi.html
EU-CITROEN-C5-I-BREAK-5D-PREFL-01	4756	1770	1516	Automobile-Catalog Citroen C5 Break 2.0 HDi 90	https://www.automobile-catalog.com/car/2001/549350/citroen_c5_break_2_0_hdi_90_x.html
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-FACELIFT-01	4188	1705	1405	Auto-Data Citroen Xsara N1 Phase II	https://www.auto-data.net/en/citroen-xsara-n1-phase-ii-generation-9026
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405	Auto-Data Citroen Xsara model technical specifications	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405	Auto-Data Citroen Xsara model technical specifications	https://www.auto-data.net/en/citroen-xsara-model-1693
EU-CITROEN-XSARA-I-N2-WAGON-5D-FACELIFT-01	4369	1705	1420	Auto-Data Citroen Xsara Break N2 Phase II	https://www.auto-data.net/en/citroen-xsara-break-n2-phase-ii-generation-9025
EU-MERCEDES-BENZ-S-KLASSE-V220-SEDAN-LWB-PREFL-01	5158	1855	1444	Mercedes-Benz Public Archive S 63 AMG long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-63-AMG-long-wheelbase.xhtml?oid=191377590
EU-MERCEDES-BENZ-CL-C215-COUPE-AMG-01	4993	1857	1390	Mercedes-Benz Public Archive CL 63 AMG	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/CL-63-AMG.xhtml?oid=4512
EU-TOYOTA-RAV4-II-XA20-SUV-5D-PREFL-01	4200	1735	1705	Auto-Data Toyota RAV4 II XA20 5-door generation	https://www.auto-data.net/en/toyota-rav4-ii-xa20-5-door-generation-7127
EU-TOYOTA-RAV4-II-XA20-SUV-5D-FACELIFT-01	4220	1735	1690	Auto-Data Toyota RAV4 II XA20 facelift 2.0 D-4D	https://www.auto-data.net/en/toyota-rav4-ii-xa20-facelift-2003-5-door-2.0-16v-d-4-d-116hp-4wd-37162
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439	Volkswagen Newsroom Golf IV vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439	Volkswagen Newsroom Golf IV vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-4-profile-19478
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455	Auto-Data Opel Omega B facelift sedan	https://www.auto-data.net/en/opel-omega-b-facelift-1999-2.5i-v6-170hp-26927
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540	Auto-Data Opel Omega B Caravan facelift	https://www.auto-data.net/en/opel-omega-b-caravan-facelift-1999-2.5i-v6-170hp-automatic-26063
EU-MERCEDES-BENZ-SL-R230-CONVERTIBLE-PREFL-AMG-01	4535	1815	1295	Mercedes-Benz Public Archive SL 55 AMG	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/SL-55-AMG.xhtml?oid=2461800
EU-PEUGEOT-406-SEDAN-FACELIFT-01	4598	1765	1412	Automobile-Catalog Peugeot 406 1.8i facelift	https://www.automobile-catalog.com/car/2000/2614175/peugeot_406_1_8i.html
EU-PEUGEOT-406-WAGON-FACELIFT-01	4736	1760	1460	Automobile-Catalog (406 Break 2.0 HPi);Automobile-Catalog (406 Break 2.0 HDi 110)	https://www.automobile-catalog.com/car/2002/2614760/peugeot_406_break_2_0_hpi.html;https://www.automobile-catalog.com/car/2002/2614940/peugeot_406_break_2_0_hdi_110.html
EU-AUDI-A4-B6-8E2-SEDAN-4D-01	4548	1772	1428	Automobile-Catalog Audi A4 1.9 TDI	https://www.automobile-catalog.com/car/2002/246995/audi_a4_1_9_tdi.html
EU-HONDA-CIVIC-VII-EM2-COUPE-2D-01	4438	1695	1399	Automobile-Catalog Honda Civic Coupe 1.7i LS	https://www.automobile-catalog.com/car/2002/1134170/honda_civic_coupe_1_7i_ls.html
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230P-MPV-4X4-MWB-H2550-01	5010	2000	2550	L'Argus Citroën Jumper 35MH 2.8 HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper/I/2001/Fourgon%2B4%2BPortes/35MH%2B28HDi%2B4x4-3344.html
EU-CITROEN-JUMPER-I-230-PICKUP-14-SWB-01	4770	2000	2093	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230-PICKUP-14-MWB-01	5120	2000	2093	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230-PICKUP-14-LWB-01	5620	2000	2096	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-MWB-01	5120	2000	2124	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230-PICKUP-MAXI-LWB-01	5620	2000	2130	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-SWB-H2450-01	4655	1998	2450	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2145-01	5005	1998	2145	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-MWB-H2465-01	5005	1998	2465	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2455-01	5505	1998	2455	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-LWB-H2470-01	5505	1998	2470	Car.info Citroen Jumper I facelift variant specifications	https://www.car.info/en-no/citroen/jumper/1st-generation-1st-facelift-93122460?view=list_small
EU-CITROEN-JUMPER-I-230L-VAN-4X4-SWB-H2150-01	4670	2000	2150	L'Argus Citroën Jumper Fg 31C 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/31C%2B28HDi%2B4x4-3294.html
EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2470-01	5010	2000	2470	L'Argus Citroën Jumper Fg 31MH 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/31MH%2B28HDi%2B4x4-3322.html
EU-CITROEN-JUMPER-I-230L-VAN-4X4-MWB-H2550-01	5010	2000	2550	L'Argus Citroën Jumper Fg 35MH 2.8HDi 4x4	https://www.largus.fr/fiche-technique/Citroen/Jumper%2BFg/I/2001/Fourgon%2B4%2BPortes/35MH%2B28HDi%2B4x4-3344.html
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800	Auto-Data Peugeot Partner I Phase I	https://www.auto-data.net/en/peugeot-partner-i-phase-i-generation-7967
EU-PEUGEOT-PARTNER-I-M49-MPV-PREFL-01	4110	1720	1915	Auto-Data Peugeot Partner I Phase I	https://www.auto-data.net/en/peugeot-partner-i-phase-i-generation-7967
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810	Auto-Data Peugeot Partner I Phase II	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-generation-1275
EU-PEUGEOT-PARTNER-I-M59-MPV-FACELIFT-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-generation-1275
EU-PEUGEOT-206-I-HATCHBACK-3D-01	3835	1652	1426	Auto-Data Peugeot 206 1.1i	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-PEUGEOT-206-I-HATCHBACK-5D-01	3835	1652	1426	Auto-Data Peugeot 206 1.1i	https://www.auto-data.net/en/peugeot-206-1.1i-60hp-5247
EU-MASERATI-SPYDER-M138-CONVERTIBLE-2D-01	4303	1822	1305	Maserati official Spyder model archive;Automobile-Catalog Maserati Spyder Cambiocorsa	https://www.maserati.com/sg/en/brand/maserati-classic-cars/gran-turismo/spyder;https://www.automobile-catalog.com/car/2002/1447160/maserati_spyder_cambiocorsa.html
EU-NISSAN-PRIMERA-III-P12-SEDAN-4D-01	4567	1760	1482	Automobile-Catalog Nissan Primera Sedan 1.8 Acenta	https://www.automobile-catalog.com/car/2002/2283875/nissan_primera_sedan_1_8_acenta.html
EU-NISSAN-PRIMERA-III-WP12-WAGON-5D-01	4675	1760	1482	Automobile-Catalog Nissan Primera Traveller 1.8 Acenta	https://www.automobile-catalog.com/car/2002/2284265/nissan_primera_traveller_1_8_acenta.html
EU-DAIHATSU-TERIOS-I-SUV-5D-FACELIFT-01	3785	1555	1695	Automobile-Catalog Daihatsu Terios Pur 4WD	https://www.automobile-catalog.com/car/2001/570785/daihatsu_terios_pur_4wd.html
EU-VW-POLO-IV-9N1-HATCHBACK-3D-01	3897	1650	1465	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N 1.4 TDI	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-1.4-tdi-75hp-8444
EU-VW-POLO-IV-9N1-HATCHBACK-5D-01	3897	1650	1465	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N 1.4 TDI	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-1.4-tdi-75hp-8444
EU-CHEVROLET-TRAILBLAZER-I-GMT360-SUV-SWB-01	4871	1897	1892	Automobile-Catalog Chevrolet TrailBlazer LT 4WD 4200	https://www.automobile-catalog.com/car/2003/1203845/chevrolet_trailblazer_lt_4wd_4200_v-8.html
EU-CHEVROLET-TRAILBLAZER-I-GMT370-SUV-LWB-01	5278	1897	1958	Automobile-Catalog Chevrolet TrailBlazer EXT LT 4WD 4200	https://www.automobile-catalog.com/car/2003/1203995/chevrolet_trailblazer_ext_lt_4wd_4200_v-8.html
EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-PREFL-01	4500	1820	1730	Auto-Data Hyundai Santa Fe I SM 2.0 CRDi	https://www.auto-data.net/en/hyundai-santa-fe-i-sm-2.0-crdi-112hp-automatic-29379
EU-HYUNDAI-SANTA-FE-I-SM-SUV-5D-FACELIFT-01	4500	1845	1730	Automobile-Catalog Hyundai Santa Fe 2.0 CRDi GLS facelift	https://www.automobile-catalog.com/car/2005/1171430/hyundai_santa_fe_2_0_crdi_gls_2wd.html
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470	Auto-Data Hyundai i30 II 1.6 GDI	https://www.auto-data.net/en/hyundai-i30-ii-1.6-gdi-135hp-automatic-18538
EU-HYUNDAI-TERRACAN-HP-SUV-5D-01	4710	1860	1795	Hyundai Heritage 2001 Terracan HP	https://www.hyundai.com/kr/ko/brand/brandstory/heritage/2000-terracan-hp
EU-HONDA-CIVIC-VII-EP3-TYPE-R-HATCHBACK-3D-01	4140	1695	1425	Automobile-Catalog Honda Civic Type-R	https://www.automobile-catalog.com/car/2002/1133960/honda_civic_type-r.html
EU-SKODA-FABIA-I-6Y3-SEDAN-4D-PREFL-01	4222	1646	1449	Automobile-Catalog Skoda Fabia Sedan 2.0	https://www.automobile-catalog.com/car/2002/3136490/skoda_fabia_sedan_2_0.html
EU-SKODA-FABIA-I-6Y3-SEDAN-4D-FACELIFT-01	4232	1646	1449	Automobile-Catalog Skoda Fabia Sedan 2.0 facelift	https://www.automobile-catalog.com/car/2005/3136955/skoda_fabia_sedan_2_0.html
EU-SKODA-SUPERB-I-3U4-SEDAN-4D-01	4803	1765	1469	Automobile-Catalog Skoda Superb 1.8 T	https://www.automobile-catalog.com/car/2002/3137180/skoda_superb_1_8_t.html
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	Auto-Data Volkswagen Passat B5 1.9 TDI	https://www.auto-data.net/en/volkswagen-passat-b5-1.9-tdi-90hp-8913
EU-VW-PASSAT-B5-3B5-WAGON-PREFL-01	4669	1740	1496	Drive.Place Volkswagen Passat B5 wagon 2.5 MT	https://volkswagen.drive.place/passat/b5/group_wagon_5/322967
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N3 three-door	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.4-80hp-3-d-8412
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467	Volkswagen Newsroom Polo IV vehicle data;Auto-Data Volkswagen Polo IV 9N3 five-door	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-4-profile-19152;https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-1.6-105hp-5-d-8421
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_12401-12500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_12401-12500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_12401-12500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（11072 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3473 行）

