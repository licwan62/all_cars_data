# 任务：all 第 5501-5600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0056__530610ae


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5501-5600 行

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
all 第 5501-5600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-SPIDER-105-CONVERTIBLE-SERIES1-01	4250	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES2-01	4120	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES3-01	4245	1630	1290
EU-ALFA-ROMEO-SPIDER-115-CONVERTIBLE-SERIES4-01	4258	1630	1290
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-FACELIFT-01	4299	1776	1315
EU-ALFA-ROMEO-SPIDER-916-CONVERTIBLE-PREFL-01	4285	1780	1315
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440
EU-AUDI-A6-C4-S6-AVANT-WAGON-01	4797	1804	1440
EU-AUDI-A6-C4-S6-SEDAN-01	4797	1804	1430
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430
EU-FIAT-BRAVO-II-198-HATCHBACK-01	4336	1792	1498
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	3718	1567	1359
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	3609	1567	1360
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	3565	1567	1360
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	3718	1580	1371
EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	3648	1585	1376
EU-FORD-FIESTA-II-HATCHBACK-FACELIFT-01	3648	1585	1376
EU-FORD-FIESTA-II-HATCHBACK-PREFL-01	3648	1585	1334
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365
EU-FORD-FIESTA-II-XR2-FACELIFT-01	3711	1620	1362
EU-FORD-FIESTA-II-XR2-PREFL-01	3711	1620	1334
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-FACELIFT-01	3833	1634	1377
EU-FORD-FIESTA-IV-JA-HATCHBACK-3D-PREFL-01	3828	1634	1334
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-FACELIFT-01	3833	1634	1377
EU-FORD-FIESTA-IV-JB-HATCHBACK-5D-PREFL-01	3828	1634	1334
EU-FORD-GRANADA-II-SEDAN-2D-01	4633	1791	1416
EU-FORD-GRANADA-II-SEDAN-4D-01	4633	1791	1416
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380
EU-FORD-GRANADA-MK1-SEDAN-2D-01	4572	1791	1369
EU-FORD-GRANADA-MK1-SEDAN-4D-01	4572	1791	1369
EU-FORD-GRANADA-MK1-TURNIER-WAGON-01	4674	1791	1410
EU-FORD-MAVERICK-I-UDS-SUV-LWB-01	4585	1755	1810
EU-FORD-MAVERICK-I-UDS-SUV-SWB-01	4105	1755	1805
EU-FORD-USA-PROBE-II-ECP-COUPE-01	4544	1773	1310
EU-HYUNDAI-I30-II-GD-HATCHBACK-5D-01	4300	1780	1470
EU-HYUNDAI-IX20-JC-MPV-01	4100	1765	1600
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600
EU-HYUNDAI-IX20-MPV-FACELIFT-01	4115	1765	1600
EU-HYUNDAI-IX20-MPV-PREFL-01	4100	1765	1600
EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	4700	1770	1405
EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	4280	1692	1390
EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	4280	1692	1390
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-NISSAN-NAVARA-D40-DOUBLECAB-01	5296	1848	1795
EU-NISSAN-NAVARA-D40-KINGCAB-01	5296	1848	1783
EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	4192	1780	1721
EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	4692	1764	1753
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Fiat	Marea	1.9 TD 75	Kombi	Frontantrieb	Diesel	55	75	Sep 1996	May 2002	2024-03-01	5779
Fiat	Marea	1.9 TD 100	Kombi	Frontantrieb	Diesel	74	100	Sep 1996	Jun 2003	2024-03-01	5780
Fiat	Marea	2.4 TD 125	Kombi	Frontantrieb	Diesel	91	125	Sep 1996	Apr 1999	2024-03-01	5781
Lexus	Gs	350 AWD	Stufenheck	Allrad	Benzin	226	307	Sep 2006	Nov 2011	2024-03-01	5785
Ford	Maverick	2.4 I	SUV	Allrad	Benzin	85	116	Sep 1996	Apr 1998	2024-03-01	5788
Ford	Maverick	2.4 I	SUV	Allrad	Benzin	87	118	Sep 1996	Apr 1998	2024-03-01	5792
Ford	Maverick	2.7 TD	SUV	Allrad	Diesel	92	125	Sep 1996	Apr 1998	2024-03-01	5793
Ford	Fiesta i	1.1	Schrägheck	Frontantrieb	Benzin	40	55	Feb 1981	Aug 1983	2024-03-01	5796
Ford	Ka	1.3 I	Schrägheck	Frontantrieb	Benzin	37	50	Sep 1996	Oct 2002	2024-03-01	5801
Ford	Ka	1.3 I	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1996	Nov 2008	2024-03-01	5802
Audi	A6 c4	2.3	Stufenheck	Frontantrieb	Benzin	98	133	Jun 1994	Dec 1995	2024-03-01	5804
Ford	Granada	2.3	Stufenheck	Heckantrieb	Benzin	82	112	Jun 1981	Aug 1985	2024-03-01	5805
Toyota	Rav 4 iii	2.4 4WD	SUV	Allrad	Benzin	125	170	Nov 2005	Jun 2013	2024-03-01	5806
Caterham	Seven	2.0 R500	Cabriolet	Heckantrieb	Benzin	196	267	Sep 2004	-	2024-03-01	5807
Audi	A6 c4 avant	2.3	Kombi	Frontantrieb	Benzin	98	133	Jun 1994	Dec 1995	2024-03-01	5808
Audi	A6 c4	2.3 Quattro	Stufenheck	Allrad	Benzin	98	133	Jun 1994	Dec 1995	2024-03-01	5809
Caterham	Seven	2.3 CSR	Cabriolet	Heckantrieb	Benzin	149	203	Jan 2005	-	2024-03-01	5810
Ford	Granada	2.8	Stufenheck	Heckantrieb	Benzin	97	132	Jun 1981	Aug 1985	2024-03-01	5811
Audi	A6 c4 avant	2.3 Quattro	Kombi	Allrad	Benzin	98	133	Jun 1994	Dec 1995	2024-03-01	5812
Ford	Granada	2.3	Kombi	Heckantrieb	Benzin	82	111	Jun 1981	Jun 1985	2024-03-01	5813
Ford	Granada	2.8	Kombi	Heckantrieb	Benzin	97	132	Jun 1981	Aug 1985	2024-03-01	5814
Ford	Mondeo ii	1.6 I	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1996	Sep 2000	2024-03-01	5816
Ford	Mondeo ii	1.8 I	Schrägheck	Frontantrieb	Benzin	85	115	Aug 1996	Sep 2000	2024-03-01	5817
Ford	Mondeo ii	2.0 I	Schrägheck	Frontantrieb	Benzin	96	131	Aug 1996	Sep 2000	2024-03-01	5818
Ford	Mondeo ii	2.5 24V	Schrägheck	Frontantrieb	Benzin	125	170	Aug 1996	Sep 2000	2024-03-01	5819
Ford	Mondeo ii	1.8 TD	Schrägheck	Frontantrieb	Diesel	66	90	Aug 1996	Sep 2000	2024-03-01	5820
Ford	Mondeo ii	1.6 I	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1996	Sep 2000	2024-03-01	5821
Ford	Mondeo ii	1.8 I	Stufenheck	Frontantrieb	Benzin	85	115	Aug 1996	Sep 2000	2024-03-01	5822
Ford	Mondeo ii	2.0 I	Stufenheck	Frontantrieb	Benzin	96	131	Aug 1996	Sep 2000	2024-03-01	5823
Ford	Mondeo ii	2.5 24V	Stufenheck	Frontantrieb	Benzin	125	170	Aug 1996	Sep 2000	2024-03-01	5824
Ford	Mondeo ii	1.8 TD	Stufenheck	Frontantrieb	Diesel	66	90	Aug 1996	Sep 2000	2024-03-01	5825
Ford	Mondeo ii turnier	1.6 I	Kombi	Frontantrieb	Benzin	66	90	Aug 1996	Sep 2000	2024-03-01	5826
Ford	Mondeo ii turnier	1.8 I	Kombi	Frontantrieb	Benzin	85	115	Aug 1996	Sep 2000	2024-03-01	5827
Ford	Mondeo ii turnier	2.0 I	Kombi	Frontantrieb	Benzin	96	131	Aug 1996	Sep 2000	2024-03-01	5828
Ford	Mondeo ii turnier	2.5 24V	Kombi	Frontantrieb	Benzin	125	170	Aug 1996	Sep 2000	2024-03-01	5829
Ford	Mondeo ii turnier	1.8 TD	Kombi	Frontantrieb	Diesel	66	90	Aug 1996	Sep 2000	2024-03-01	5830
Audi	b3	1.8	Coupe	Frontantrieb	Benzin	82	112	Aug 1989	Jul 1991	2024-03-01	5831
Caterham	Seven	2.3 CSR	Cabriolet	Heckantrieb	Benzin	194	264	Jan 2005	-	2024-03-01	5832
Ford USA	Probe i	2.2 GT	Coupe	Frontantrieb	Benzin	108	147	Aug 1988	Dec 1992	2024-03-01	5833
Caterham	Seven	1.6	Cabriolet	Heckantrieb	Benzin	112	152	Apr 2008	-	2024-03-01	5835
Caterham	Seven	1.6	Cabriolet	Heckantrieb	Benzin	93	126	Apr 2007	-	2024-03-01	5836
Mclaren	Mp4	12C	Coupe	Heckantrieb	Benzin	441	600	Apr 2011	Apr 2014	2024-03-01	5837
Alfa Romeo	Mito	1.4 Turbo Multiair	Schrägheck	Frontantrieb	Benzin	120	163	Oct 2009	Oct 2018	2024-03-01	5838
Nissan	370z roadster	3.7	Cabriolet	Heckantrieb	Benzin	243	330	Dec 2009	-	2024-03-01	5839
Nissan	Cube	1.5 DCI	Schrägheck	Frontantrieb	Diesel	81	110	Mar 2010	-	2024-03-01	5840
Nissan	Navara	2.5 DCI	Pritsche/Fahrgestell	Allrad	Diesel	140	190	Mar 2010	-	2024-03-01	5841
Nissan	Navara	3.0 DCI	Pritsche/Fahrgestell	Allrad	Diesel	170	231	Mar 2010	-	2024-03-01	5842
Hyundai	Sonata iii	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	92	125	Jun 1996	Jun 1998	2024-03-01	5852
Renault	Scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	81	110	Apr 2009	Sep 2016	2024-05-01	5853
Hyundai	i	2.0 16V	Coupe	Frontantrieb	Benzin	102	139	Aug 1996	Apr 2002	2024-03-01	5854
Renault	Grand scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	81	110	Apr 2009	Sep 2016	2024-05-01	5855
Renault	Grand scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	63	86	Apr 2009	Sep 2016	2024-05-01	5856
Opel	Frontera	2.5 TDS	Geländewagen offen	Allrad	Diesel	85	115	Sep 1996	Oct 1998	2024-11-01	5857
Renault	Scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	63	86	Apr 2009	Sep 2016	2024-05-01	5858
Renault	Scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	70	95	Nov 2010	Sep 2016	2024-05-01	5859
Opel	Frontera	2.5 TDS	Geländewagen geschlossen	Allrad	Diesel	85	115	Sep 1996	Oct 1998	2024-11-01	5860
Renault	Grand scénic iii	1.5 DCI	Großraumlimousine	Frontantrieb	Diesel	70	95	Nov 2010	Sep 2016	2024-05-01	5861
Mercedes-benz	R-Klasse	R 350 CDI 4-matic	Großraumlimousine	Allrad	Diesel	195	265	Aug 2010	Dec 2014	2024-03-01	5880
Lancia	Phedra	2.2 JTD	Großraumlimousine	Frontantrieb	Diesel	120	163	Apr 2006	Nov 2010	2024-03-01	5883
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	51	69	Dec 2010	Jun 2020	2024-05-01	5887
VW	Golf iii variant	1.8 Syncro	Kombi	Allrad	Benzin	66	90	Oct 1994	Apr 1999	2024-03-01	5893
VW	Golf iii variant	2.9 VR6 Syncro	Kombi	Allrad	Benzin	140	190	Oct 1994	Apr 1999	2024-03-01	5894
Toyota	Land cruiser 200	4.6 V8	Geländewagen geschlossen	Allrad	Benzin	234	318	Jan 2012	-	2024-03-01	5898
Jaguar	Xk 8	4	Coupe	Heckantrieb	Benzin	209	284	Mar 1996	Jul 2005	2024-03-01	5900
Jaguar	Xk 8 convertible	4	Cabriolet	Heckantrieb	Benzin	209	284	Mar 1996	Dec 2002	2024-03-01	5902
Hyundai	I20 i	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	55	75	Sep 2008	Dec 2012	2024-03-01	5904
Opel	Vectra b	2.0 DI 16V	Stufenheck	Frontantrieb	Diesel	60	82	Nov 1996	Apr 2002	2024-03-01	5908
Opel	Vectra b cc	2.0 DI 16V	Schrägheck	Frontantrieb	Diesel	60	82	Nov 1996	Jun 2000	2024-03-01	5910
Opel	Vectra b caravan	1.6 I	Kombi	Frontantrieb	Benzin	55	75	Nov 1996	Jun 2000	2024-03-01	5913
Opel	Vectra b caravan	1.6 I 16V	Kombi	Frontantrieb	Benzin	74	100	Nov 1996	Jul 2002	2024-03-01	5914
Opel	Vectra b caravan	1.8 I 16V	Kombi	Frontantrieb	Benzin	85	115	Nov 1996	Sep 2000	2024-03-01	5916
Opel	Vectra b caravan	2.0 I 16V	Kombi	Frontantrieb	Benzin	100	136	Nov 1996	Jun 2000	2024-03-01	5917
Opel	Vectra b caravan	2.5 I V6	Kombi	Frontantrieb	Benzin	125	170	Nov 1996	Sep 2000	2024-03-01	5918
Opel	Vectra b caravan	2.0 DI 16V	Kombi	Frontantrieb	Diesel	60	82	Nov 1996	Jun 2000	2024-03-01	5921
Opel	Sintra	2.2 I 16V	Großraumlimousine	Frontantrieb	Benzin	104	141	Nov 1996	Apr 1999	2024-03-01	5922
Opel	Sintra	3.0 I 24V	Großraumlimousine	Frontantrieb	Benzin	148	201	Nov 1996	Apr 1999	2024-03-01	5924
Fiat	Bravo ii	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	85	116	Nov 2006	Dec 2009	2024-03-01	5925
Alfa Romeo	Brera	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	120	163	Mar 2008	Jun 2010	2024-03-01	5926
Alfa Romeo	Spider	2.0 Jtdm	Cabriolet	Frontantrieb	Diesel	120	163	Apr 2009	Mar 2011	2024-03-01	5927
Fiat	Punto	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jul 2009	Feb 2012	2024-03-01	5928
Skoda	Superb ii	1.8 TSI	Schrägheck	Frontantrieb	Benzin	112	152	Mar 2009	May 2015	2024-03-01	5929
Skoda	Superb ii	1.8 TSI 4X4	Schrägheck	Allrad	Benzin	112	152	Mar 2009	May 2015	2024-03-01	5930
Fiat	Grande punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	51	69	Jul 2008	-	2024-03-01	5931
Mercedes-benz	S-Klasse	S 300 Turbo-d	Stufenheck	Heckantrieb	Diesel	130	177	May 1996	Oct 1998	2024-03-01	5932
VW	Passat b3/b4	2.0 Syncro	Stufenheck	Allrad	Benzin	85	115	Oct 1990	Aug 1996	2024-03-01	5933
Mercedes-benz	C-Klasse	C 230	Stufenheck	Heckantrieb	Benzin	110	150	Jun 1996	Jun 1997	2024-03-01	5934
Skoda	Superb ii	1.8 TSI	Kombi	Frontantrieb	Benzin	112	152	Oct 2009	May 2015	2024-03-01	5935
Skoda	Superb ii	1.8 TSI 4X4	Kombi	Allrad	Benzin	112	152	Oct 2009	May 2015	2024-03-01	5936
KIA	Clarus	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	85	116	Jul 1996	Aug 2001	2024-03-01	5937
Fiat	Grande punto	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Oct 2005	Jul 2007	2024-03-01	5938
KIA	Clarus	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	98	133	Jul 1996	Nov 2001	2024-03-01	5939
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	51	69	Jul 2008	Feb 2012	2024-03-01	5940
VW	Jetta iv	1.2 TSI	Stufenheck	Frontantrieb	Benzin	77	105	Oct 2010	Dec 2017	2024-03-01	5941
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel	65	88	Oct 1996	May 2000	2024-03-01	5942
VW	Jetta iv	1.6 TDI	Stufenheck	Frontantrieb	Diesel	77	105	Apr 2010	Jul 2015	2024-03-01	5943
VW	Passat b3/b4 variant	2.0 Syncro	Kombi	Allrad	Benzin	85	115	Mar 1990	Dec 1996	2024-03-01	5944
KIA	Sephia	1.5 I	Stufenheck	Frontantrieb	Benzin	59	80	Feb 1996	Oct 1997	2024-03-01	5945
VW	Jetta iv	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Jul 2010	Dec 2017	2025-11-01	5946
Mercedes-benz	C-Klasse	C 200 Kompressor	Stufenheck	Heckantrieb	Benzin	141	192	Nov 1996	May 2000	2024-03-01	5947
KIA	Sephia	1.5 I	Schrägheck	Frontantrieb	Benzin	59	80	Feb 1996	Oct 1997	2024-03-01	5948


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 21 个输入 Ktype 的映射，共形成 25 条 `READY` 映射行。
* 复用了本批给定索引中的 Audi A6 C4、Hyundai Sonata III、Opel Frontera A、VW Golf III Variant、Opel Vectra B、Fiat Bravo II、Mercedes-Benz W202 和 Kia Sephia I 尺寸组。
* 本批 1996–1998 Ford Maverick 的三门、五门外廓分别为 `4185×1755×1830 mm` 和 `4665×1755×1850 mm`，与累计表中的既有 `-01` 组三维不同，因此未覆盖旧组，新建 `-02` 组。125 hp 柴油 Ktype 同时覆盖三门和五门，已拆为两个派生 id。([汽车数据网][1])
* Ford Ka I 已确认是 RBT 三门车身；1996 年规格给出车长 3620 mm、不含后视镜宽度 1631 mm、高度 1368 mm，因此首次建组。([汽车目录档案][2])
* Opel Frontera 2.5 TDS 的开放式 Sport 三门短轴和封闭式五门长轴已分别关联已有尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：21
* `READY` 映射行：25
* 尚待处理 Ktype：79
* 当前已引用尺寸组：16
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5788	5788	SUV	Maverick I		3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	HIGH	1996–1998三门短轴外廓。	READY
5792	5792	SUV	Maverick I		5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	HIGH	1996–1998五门长轴外廓。	READY
5793_3dr	5793	SUV	Maverick I		3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	HIGH	同一Ktype覆盖三门和五门，按门数拆分。	READY
5793_5dr	5793	SUV	Maverick I		5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	HIGH	同一Ktype覆盖三门和五门，按门数拆分。	READY
5801	5801	Hatchback	Ka I	RBT	3	EU-FORD-KA-I-RBT-HATCHBACK-3D-01	HIGH		READY
5802	5802	Hatchback	Ka I	RBT	3	EU-FORD-KA-I-RBT-HATCHBACK-3D-01	HIGH		READY
5804	5804	Sedan	A6 C4		4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
5808	5808	Wagon	A6 C4		5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
5809	5809	Sedan	A6 C4		4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
5812	5812	Wagon	A6 C4		5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
5852	5852	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
5857	5857	SUV	Frontera A Sport		3	EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	HIGH	开放式Sport三门短轴车身。	READY
5860	5860	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH	封闭式五门长轴车身。	READY
5893	5893	Wagon	Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
5894	5894	Wagon	Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
5908_prefl	5908	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5908_facelift	5908	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5925	5925	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
5934	5934	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	改款前生产区间。	READY
5942_prefl	5942	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5942_facelift	5942	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5945	5945	Sedan	Sephia I	FA	4	EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	HIGH		READY
5947_prefl	5947	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5947_facelift	5947	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5948	5948	Hatchback	Sephia I	FA	5	EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	4185	1755	1830	Auto-Data	https://www.auto-data.net/en/ford-maverick-uds-uns-2.4-i-3-dr-116hp-7550
EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	4665	1755	1850	Auto-Data	https://www.auto-data.net/en/ford-maverick-uds-uns-2.4-i-gls-5-dr-118hp-7551
EU-FORD-KA-I-RBT-HATCHBACK-3D-01	3620	1631	1368	Ford Ka 1996 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/12/Ford-Ka-1996-UK-.pdf
```

## 下一步优先处理

1. 集中闭合 Ford Mondeo I facelift 的 Hatchback、Sedan 和 Turnier 三个外廓，并批量关联 Ktype `5816–5830`。
2. 核对 Fiat Marea Weekend 不同规格来源中的 `4484/4485 mm`、`1740/1741 mm` 和 `1500/1510 mm` 冲突，避免按发动机错误拆组。
3. 处理 Renault Scénic III 与 Grand Scénic III、Opel Vectra B CC/Caravan，以及 Toyota、Jaguar、Caterham 等尚未闭合车型组。
4. 单独解决 Nissan Navara D40 facelift 的 King Cab、Double Cab边界及欧洲市场三维，避免误用累计表中尺寸不同的既有组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-maverick-uds-uns-2.4-i-3-dr-116hp-7550?utm_source=chatgpt.com "Ford Maverick (UDS,UNS) 2.4 i (3 dr) (116 Hp) /SUV 1996"
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/12/Ford-Ka-1996-UK-.pdf?utm_source=chatgpt.com "Ford-Ka-1996-UK-.pdf"
[3]: https://www.auto-data.net/en/opel-frontera-a-sport-2.5-tds-115hp-4x4-2567?utm_source=chatgpt.com "Opel Frontera A Sport 2.5 TDS (115 Hp) 4x4 /SUV 1996"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 16 条 `READY` 映射，覆盖 12 个 Ktype。
* Ford Granada 的轿车 Ktype 生产区间包含二门版停产前阶段，已按二门、四门外廓拆分；旅行版直接复用既有尺寸组。([motor-car.net][1])
* Nissan Navara D40 facelift 已按 King Cab、Double Cab 关联既有尺寸组；Fiat Punto Evo 已按三门、五门关联既有尺寸组。Punto Evo 1.4 同期存在三门和五门车身。([汽车目录][2])
* 首次闭合 Audi Coupe B3、McLaren MP4-12C、Nissan Cube Z12 和 Opel Sintra 四个尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：33
* `READY` 映射行：41
* `PENDING` Ktype：67
* 当前已引用尺寸组：27
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5805_2dr	5805	Sedan	Granada II		2	EU-FORD-GRANADA-II-SEDAN-2D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5805_4dr	5805	Sedan	Granada II		4	EU-FORD-GRANADA-II-SEDAN-4D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5811_2dr	5811	Sedan	Granada II		2	EU-FORD-GRANADA-II-SEDAN-2D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5811_4dr	5811	Sedan	Granada II		4	EU-FORD-GRANADA-II-SEDAN-4D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5813	5813	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
5814	5814	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
5831	5831	Coupe	Coupe B3	89	2	EU-AUDI-COUPE-B3-89-COUPE-01	HIGH		READY
5837	5837	Coupe	MP4-12C		2	EU-MCLAREN-MP4-12C-COUPE-01	HIGH		READY
5840	5840	Hatchback	Cube Z12	Z12	5	EU-NISSAN-CUBE-Z12-HATCHBACK-01	HIGH		READY
5841_kingcab	5841	Pickup	Navara D40 facelift	D40	2	EU-NISSAN-NAVARA-D40-KINGCAB-01	HIGH	同一Ktype覆盖King Cab与Double Cab，按驾驶室拆分。	READY
5841_doublecab	5841	Pickup	Navara D40 facelift	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH	同一Ktype覆盖King Cab与Double Cab，按驾驶室拆分。	READY
5842	5842	Pickup	Navara D40 facelift	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH		READY
5922	5922	MPV	Sintra		5	EU-OPEL-SINTRA-MPV-01	HIGH		READY
5924	5924	MPV	Sintra		5	EU-OPEL-SINTRA-MPV-01	HIGH		READY
5928_3dr	5928	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5928_5dr	5928	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-COUPE-B3-89-COUPE-01	4366	1716	1370	Auto-Data	https://www.auto-data.net/en/audi-coupe-b3-89-1.8-112hp-4456
EU-MCLAREN-MP4-12C-COUPE-01	4509	1908	1199	McLaren MP4-12C technical factsheet	https://cars.mclaren.press/assets/documents/original/3916-mclaren-mp4-12c-technical-factsheet.pdf
EU-NISSAN-CUBE-Z12-HATCHBACK-01	3980	1695	1670	Auto-Data	https://www.auto-data.net/en/nissan-cube-z12-1.5-dci-110hp-dpf-45620
EU-OPEL-SINTRA-MPV-01	4670	1830	1780	Auto-Data Opel Sintra 2.2i; Auto-Data Opel Sintra 3.0i	https://www.auto-data.net/en/opel-sintra-2.2i-16v-141hp-1754; https://www.auto-data.net/en/opel-sintra-3.0i-24v-201hp-automatic-1755
```

## 下一步优先处理

1. 闭合 Ford Mondeo II Hatchback、Sedan、Turnier 三个候选外廓，并批量关联 `5816–5830`。
2. 解决 Fiat Marea Weekend 来源间的毫米级长度、宽度及高度冲突，确认是否统一为一个物理尺寸组。
3. 集中处理 Renault Scénic III、Grand Scénic III，以及 Opel Vectra B CC、Caravan。
4. 继续处理 Toyota RAV4 III、Land Cruiser 200、Jaguar XK8 和 Caterham Seven 的版本边界。

推进信号：CONTINUE

[1]: https://motor-car.net/engine-types/straight-three-engines/item/11112-granada-mk-ii-1977-85 "https://motor-car.net/engine-types/straight-three-engines/item/11112-granada-mk-ii-1977-85"
[2]: https://www.automobile-catalog.com/car/2009/1229990/fiat_punto_evo_1_4_dynamic_startandstop.html "https://www.automobile-catalog.com/car/2009/1229990/fiat_punto_evo_1_4_dynamic_startandstop.html"
[3]: https://www.auto-data.net/en/audi-coupe-b3-89-1.8-112hp-4456 "https://www.auto-data.net/en/audi-coupe-b3-89-1.8-112hp-4456"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Ford Mondeo I facelift（欧洲市场常称 Mondeo Mk II）的 Hatchback、Sedan 和 Turnier 三个物理外廓。
* Ford 官方车型手册列出的三种车身长度分别为 `4556 / 4556 / 4671 mm`，不含后视镜宽度均为 `1749 mm`，高度分别为 `1372 / 1372 / 1391 mm`。本轮一次建组三组，并批量关联 Ktype `5816–5830`。([汽车目录档案][1])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：48
* `READY` 映射行：56
* `PENDING` Ktype：52
* 当前已引用尺寸组：30
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5816	5816	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5817	5817	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5818	5818	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5819	5819	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5820	5820	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5821	5821	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5822	5822	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5823	5823	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5824	5824	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5825	5825	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5826	5826	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5827	5827	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5828	5828	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5829	5829	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5830	5830	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	4556	1749	1372	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	4556	1749	1372	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-I-FACELIFT-WAGON-01	4671	1749	1391	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
```

## 下一步优先处理

1. 解决 Fiat Marea Weekend 官方资料中 `HeightMM=1500/1510` 的配置口径冲突。
2. 按改款边界拆分 Renault Scénic III 和 Grand Scénic III，集中关联 Ktype `5853、5855、5856、5858、5859、5861`。
3. 闭合 Opel Vectra B CC 与 Caravan；优先确认 Caravan 在改款前后是否保持同一组三维。
4. 处理 Toyota RAV4 III、Land Cruiser 200、Jaguar XK8 Coupe/Convertible 和 Caterham Seven 各版本。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf?utm_source=chatgpt.com "Ford Mondeo"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Fiat Marea Weekend 两种高度外廓：1.9 TD 75/100 共用 `4484×1741×1500 mm`；2.4 TD 125 为 `4484×1741×1495 mm`，因此单独建组。([汽车目录][1])
* 闭合 Opel Vectra B CC 改款前、改款后外廓。两阶段三维均为 `4495×1707×1425 mm`，但因改款外部边界不同，分别建组。([汽车数据网][2])
* 闭合 Opel Vectra B Caravan 改款前、改款后外廓。两阶段三维均为 `4490×1707×1490 mm`，对应 Ktype 按改款阶段拆分。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：58
* `READY` 映射行：73
* `PENDING` Ktype：42
* 当前已引用尺寸组：36
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5779	5779	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	HIGH		READY
5780	5780	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	HIGH		READY
5781	5781	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-24TD-01	HIGH	2.4 TD对应独立高度外廓。	READY
5910_prefl	5910	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5910_facelift	5910	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5913_prefl	5913	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5913_facelift	5913	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5914_prefl	5914	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5914_facelift	5914	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5916_prefl	5916	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5916_facelift	5916	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5917_prefl	5917	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5917_facelift	5917	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5918_prefl	5918	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5918_facelift	5918	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5921_prefl	5921	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5921_facelift	5921	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	4484	1741	1500	Automobile-Catalog Fiat Marea Weekend TD 75; Automobile-Catalog Fiat Marea Weekend TD 100	https://www.automobile-catalog.com/car/1997/722015/fiat_marea_weekend_td_75_sx.html; https://www.automobile-catalog.com/car/1997/722045/fiat_marea_weekend_td_100_sx.html
EU-FIAT-MAREA-185-WEEKEND-WAGON-24TD-01	4484	1741	1495	Auto-Data Fiat Marea Weekend 2.4 TD 125	https://www.auto-data.net/en/fiat-marea-weekend-185-2.4-td-125-125hp-7220
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425	Auto-Data Opel Vectra B CC 2.0 DI 16V	https://www.auto-data.net/en/opel-vectra-b-cc-2.0-di-16v-82hp-2290
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425	Auto-Data Opel Vectra B CC facelift 2.0 DI 16V	https://www.auto-data.net/en/opel-vectra-b-cc-facelift-1999-2.0-di-16v-82hp-26210
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan 1.6i	https://www.auto-data.net/en/opel-vectra-b-caravan-1.6i-75hp-2274
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan facelift 1.8i 16V	https://www.auto-data.net/en/opel-vectra-b-caravan-facelift-1999-1.8i-16v-115hp-26211
```

## 下一步优先处理

1. 按 Phase I、Phase II、Phase III 闭合 Renault Scénic III 与 Grand Scénic III，并判断 86、95、110 hp 各 Ktype 实际覆盖的阶段。
2. 处理 Toyota RAV4 III、Land Cruiser 200 和 Lexus GS 350 AWD。
3. 闭合 Jaguar XK8 Coupe、XK8 Convertible、Nissan 370Z Roadster。
4. 集中处理 Caterham Seven R500、CSR 与 1.6 版本的车宽和车高边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/722015/fiat_marea_weekend_td_75_sx.html?utm_source=chatgpt.com "1997 Fiat Marea Weekend TD 75 SX (man. 5)"
[2]: https://www.auto-data.net/en/opel-vectra-b-cc-2.0-di-16v-82hp-2290 "Opel Vectra B CC 2.0 DI 16V (82 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-vectra-b-caravan-1.6i-75hp-2274 "1996 Opel Vectra B Caravan 1.6i (75 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已一次性闭合 Renault Scénic III 与 Grand Scénic III 的 Phase I、Phase II、Phase III 共 6 个物理外廓组。
* Phase I 至 Phase II 的车长和高度均发生变化；Phase II 与 Phase III 虽然三维相同，但前后外观边界不同，因此分别建组，不合并尺寸组。
* Ktype `5853、5855、5856、5858、5859、5861` 的生产区间跨越多个外观阶段，均已拆为稳定的阶段派生行。Scénic 三阶段三维依次为 `4343×1845×1624`、`4366×1845×1640`、`4366×1845×1640 mm`；Grand Scénic 三阶段依次为 `4560×1845×1675`、`4573×1845×1645`、`4573×1845×1645 mm`。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：64
* `READY` 映射行：91
* `PENDING` Ktype：36
* 当前已引用尺寸组：42
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5853_phase1	5853	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5853_phase2	5853	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5853_phase3	5853	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5855_phase1	5855	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5855_phase2	5855	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5855_phase3	5855	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5856_phase1	5856	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5856_phase2	5856	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5856_phase3	5856	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5858_phase1	5858	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5858_phase2	5858	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5858_phase3	5858	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5859_phase1	5859	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	生产始于Phase I后期；Phase I分支。	READY
5859_phase2	5859	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨阶段外廓；Phase II分支。	READY
5859_phase3	5859	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨阶段外廓；Phase III分支。	READY
5861_phase1	5861	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	生产始于Phase I后期；Phase I分支。	READY
5861_phase2	5861	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨阶段外廓；Phase II分支。	READY
5861_phase3	5861	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨阶段外廓；Phase III分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-SCENIC-III-MPV-PHASE1-01	4343	1845	1624	Auto-Data Renault Scenic III Phase I 1.5 dCi	https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.5-dci-110hp-fap-edc-39511
EU-RENAULT-SCENIC-III-MPV-PHASE2-01	4366	1845	1640	Auto-Data Renault Scenic III Phase II 1.5 dCi	https://www.auto-data.net/en/renault-scenic-iii-phase-ii-collection-2012-1.5-dci-110hp-fap-17459
EU-RENAULT-SCENIC-III-MPV-PHASE3-01	4366	1845	1640	Automobile-Catalog Renault Scenic III Phase III 1.5 dCi 95	https://www.automobile-catalog.com/car/2013/2982200/renault_scenic_1_5_dci_95.html
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	4560	1845	1675	Auto-Data Renault Grand Scenic III Phase I 1.5 dCi	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-i-1.5-dci-110hp-fap-7-seat-39526
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase II	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-ii-collection-2012-tce-130hp-17460
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase III 1.5 dCi	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-iii-1.5-dci-110hp-fap-stop-start-7-seat-38568
```

## 下一步优先处理

1. 闭合 Lexus GS 350 AWD 与 Toyota RAV4 III 的改款前后物理外廓。
2. 处理 Nissan 370Z Roadster、Jaguar XK8 Coupe/Convertible 的改款边界。
3. 集中核对 Caterham Seven R500、CSR、标准/SV 车架差异。
4. 批量处理可高复用的 Skoda Superb II、VW Passat/Jetta、Fiat Punto/Grande Punto 车型组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.5-dci-110hp-fap-edc-39511?utm_source=chatgpt.com "Renault Scenic III (Phase I) 1.5 dCi (110 Hp) FAP EDC"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Lexus GS III 350 AWD 改款前、改款后两个外廓阶段。两阶段三维均为 `4825×1820×1435 mm`，但外观改款边界不同，分别建组。([汽车数据网][1])
* 闭合 Nissan 370Z Roadster 早期 330 hp 外廓，使用官方 2010 年车型资料中的 `4250×1845×1325 mm`。([Amazon Web Services, Inc.][2])
* 闭合 Alfa Romeo Brera 939 三门 Coupe 外廓，使用官方车主手册中的 `4410×1830×1341 mm`。([alfaclub.ro][3])
* 闭合 Skoda Superb II Liftback、Combi 在 2013 年改款前后的四个外廓组，并批量关联前驱、四驱 Ktype。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：71
* `READY` 映射行：103
* `PENDING` Ktype：29
* 当前已引用尺寸组：50
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5785_prefl	5785	Sedan	GS III		4	EU-LEXUS-GS-III-S190-SEDAN-AWD-PREFL-01	HIGH	生产区间跨2008年改款；改款前分支。	READY
5785_facelift	5785	Sedan	GS III facelift		4	EU-LEXUS-GS-III-S190-SEDAN-AWD-FACELIFT-01	HIGH	生产区间跨2008年改款；改款后分支。	READY
5839	5839	Convertible	370Z Roadster	Z34	2	EU-NISSAN-370Z-Z34-ROADSTER-PREFL-01	HIGH	330 hp早期Roadster外廓。	READY
5926	5926	Coupe	Brera	939	3	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	输入Schrägheck，按Brera 939三门Coupe归类。	READY
5929_prefl	5929	Hatchback	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5929_facelift	5929	Hatchback	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5930_prefl	5930	Hatchback	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5930_facelift	5930	Hatchback	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5935_prefl	5935	Wagon	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5935_facelift	5935	Wagon	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5936_prefl	5936	Wagon	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5936_facelift	5936	Wagon	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LEXUS-GS-III-S190-SEDAN-AWD-PREFL-01	4825	1820	1435	Auto-Data Lexus GS III 350 AWD	https://www.auto-data.net/en/lexus-gs-iii-350-v6-307hp-awd-automatic-36777
EU-LEXUS-GS-III-S190-SEDAN-AWD-FACELIFT-01	4825	1820	1435	Auto-Data Lexus GS III facelift 350 AWD	https://www.auto-data.net/en/lexus-gs-iii-facelift-2008-350-v6-307hp-awd-automatic-5908
EU-NISSAN-370Z-Z34-ROADSTER-PREFL-01	4250	1845	1325	Nissan 370Z 2010 official brochure	https://s3.amazonaws.com/cdn.autoipacket.com/brochures/nissan/2010/2010-nissan-370z.pdf
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4410	1830	1341	Alfa Romeo Brera owner handbook	https://www.alfaclub.ro/manuals/Brera.pdf
EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	4838	1817	1462	Auto-Data Skoda Superb II 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-1.8-tsi-160hp-4x4-14107
EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	4833	1817	1462	Auto-Data Skoda Superb II facelift 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-facelift-2013-1.8-tsi-160hp-4x4-19292
EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	4838	1817	1510	Auto-Data Skoda Superb II Combi 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-combi-1.8-tsi-160hp-4x4-56489
EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	4833	1817	1511	Auto-Data Skoda Superb II Combi facelift 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-combi-facelift-2013-1.8-tsi-160hp-4x4-19308
```

## 下一步优先处理

1. 闭合 Toyota RAV4 III、Land Cruiser 200、Yaris III 和 Hyundai i20 I。
2. 处理 Jaguar XK8 Coupe/Convertible、Alfa Romeo Spider 939 和 Alfa Romeo MiTo 的改款边界。
3. 批量闭合 Fiat Grande Punto/Punto、VW Jetta VI、Passat B3/B4 Sedan/Variant。
4. 最后集中处理 Caterham Seven 多车架、Mercedes-Benz R-Class/S-Class、Lancia Phedra及剩余历史车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lexus-gs-iii-350-v6-307hp-awd-automatic-36777?utm_source=chatgpt.com "Lexus GS III 350 V6 (307 Hp) AWD Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://s3.amazonaws.com/cdn.autoipacket.com/brochures/nissan/2010/2010-nissan-370z.pdf "Brochure: Nissan Z34 370Z (October 2010)"
[3]: https://www.alfaclub.ro/manuals/Brera.pdf "001-040 Alfa BRERA GB 3ed"
[4]: https://www.auto-data.net/en/skoda-superb-ii-1.8-tsi-160hp-4x4-14107 "Skoda Superb II 1.8 TSI (160 Hp) 4x4 | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 Ford Probe I、Hyundai Coupe I 改款前/后共 3 个 Coupe 尺寸组。Hyundai Coupe 两阶段三维相同，但外观改款边界不同，因此分别建组。([汽车数据网][1])
* 已闭合 Mercedes-Benz R-Class W251 facelift、Lancia Phedra、Alfa Romeo Spider 939 和 Mercedes-Benz S-Class W140 facelift。各组宽度均采用不含后视镜口径。([汽车数据网][2])
* Hyundai i20 I 1.4 CRDi 75 的资料明确覆盖三门、五门车身，已拆为两个派生 id；该发动机在 2012 年改款前停产，未创建 facelift 分支。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：78
* `READY` 映射行：112
* `PENDING` Ktype：22
* 当前已引用尺寸组：59
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5833	5833	Coupe	Probe I		3	EU-FORD-USA-PROBE-I-COUPE-01	HIGH		READY
5854_prefl	5854	Coupe	Coupe I	RD	3	EU-HYUNDAI-COUPE-I-RD-COUPE-PREFL-01	HIGH	生产区间跨1999年改款；改款前分支。	READY
5854_facelift	5854	Coupe	Coupe I facelift	RD2	3	EU-HYUNDAI-COUPE-I-RD2-COUPE-FACELIFT-01	HIGH	生产区间跨1999年改款；改款后分支。	READY
5880	5880	MPV	R-Class facelift	W251	5	EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	HIGH	标准轴距W251车身。	READY
5883	5883	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
5904_3dr	5904	Hatchback	i20 I	PB	3	EU-HYUNDAI-I20-I-PB-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5904_5dr	5904	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5927	5927	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
5932	5932	Sedan	S-Class W140 facelift	W140	4	EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-PROBE-I-COUPE-01	4520	1740	1320	Auto-Data Ford Probe I 2.2 GT	https://www.auto-data.net/en/ford-probe-i-2.2-gt-147hp-7996
EU-HYUNDAI-COUPE-I-RD-COUPE-PREFL-01	4345	1730	1310	Auto-Data Hyundai Coupe I RD 2.0 i 16V	https://www.auto-data.net/en/hyundai-coupe-i-rd-2.0-i-16v-139hp-13848
EU-HYUNDAI-COUPE-I-RD2-COUPE-FACELIFT-01	4345	1730	1310	Auto-Data Hyundai Coupe I RD2 facelift 2.0 i 16V	https://www.auto-data.net/en/hyundai-coupe-i-rd2-facelift-1999-2.0-i-16v-139hp-automatic-29323
EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	4922	1922	1674	Auto-Data Mercedes-Benz R-Class W251 facelift R 350 CDI	https://www.auto-data.net/en/mercedes-benz-r-class-w251-facelift-2010-r-350-cdi-v6-265hp-4matic-g-tronic-37240
EU-LANCIA-PHEDRA-179-MPV-01	4750	1863	1759	Auto-Data Lancia Phedra 2.2 Multijet	https://www.auto-data.net/en/lancia-phedra-2.2-multijet-170hp-automatic-45955
EU-HYUNDAI-I20-I-PB-HATCHBACK-3D-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.4 CRDi 75	https://www.auto-data.net/en/hyundai-i20-i-pb-1.4-crdi-75hp-31441
EU-HYUNDAI-I20-I-PB-HATCHBACK-5D-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.4 CRDi 75	https://www.auto-data.net/en/hyundai-i20-i-pb-1.4-crdi-75hp-31441
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Auto-Data Alfa Romeo Spider 939 2.0 JTDM	https://www.auto-data.net/en/alfa-romeo-spider-939-2.0-jtdm-170hp-42171
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486	Auto-Data Mercedes-Benz S-Class W140 facelift S 300 Turbodiesel	https://www.auto-data.net/en/mercedes-benz-s-class-w140-facelift-1994-s-300-turbodiesel-177hp-5g-tronic-13081
```

## 下一步优先处理

1. 闭合 Toyota RAV4 III 2.4 4WD 的普通车身、两次改款及市场尺寸边界。
2. 处理 Toyota Yaris III、Land Cruiser 200 与 Jaguar XK8 Coupe/Convertible。
3. 批量闭合 VW Passat B3/B4 Sedan/Variant、VW Jetta VI 和 Fiat Grande Punto/Punto。
4. 最后处理 Caterham Seven 多车架、Ford Fiesta I 保险杠分支、Kia Clarus 与 Alfa Romeo MiTo。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-probe-i-2.2-gt-147hp-7996 "Ford Probe I 2.2 GT (147 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mercedes-benz-r-class-w251-facelift-2010-r-350-cdi-v6-265hp-4matic-g-tronic-37240?utm_source=chatgpt.com "Mercedes-Benz R-class (W251, facelift 2010) R 350 CDI ..."
[3]: https://www.automobile-catalog.com/car/2012/1606805/hyundai_i20_1_4_crdi_75.html?utm_source=chatgpt.com "2012 Hyundai i20 1.4 CRDi 75 Comfort Specs Review (55 kW / 75 PS / 74 hp) (up to July 2012 for Europe )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Jaguar XK8 4.0 的 X100 Coupe 与 Convertible 两个外廓。4.0 升 209 kW 版本对应 1996–2002 年车身，Coupe 高度为 1296 mm，Convertible 为 1306 mm。([汽车数据网][1])
* 闭合 Fiat Grande Punto 199 的三门、五门外廓；两种车身三维均为 `4030×1687×1490 mm`，但车身侧围和门数不同，因此分别建组。([汽车目录档案][2])
* 闭合 Kia Clarus 改款前 K9A 与改款后 GC 两个轿车外廓，并批量关联 1.8、2.0 两个 Ktype。([汽车数据网][3])
* 闭合 VW Passat B3/B4 的 Sedan、Variant 四个外廓。B3 与 B4 的车长、宽度及外部造型均不同，两个跨代 Ktype 已分别派生。([Volkswagen Newsroom][4])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：86
* `READY` 映射行：126
* `PENDING` Ktype：14
* 当前已引用尺寸组：69
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5900	5900	Coupe	XK8 X100	X100	2	EU-JAGUAR-XK8-X100-COUPE-40-01	HIGH		READY
5902	5902	Convertible	XK8 X100	X100	2	EU-JAGUAR-XK8-X100-CONVERTIBLE-40-01	HIGH		READY
5931_3dr	5931	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5931_5dr	5931	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5933_b3	5933	Sedan	Passat B3	35I	4	EU-VW-PASSAT-B3-35I-SEDAN-01	HIGH	生产区间跨B3与B4，B3分支。	READY
5933_b4	5933	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-3A-SEDAN-01	HIGH	生产区间跨B3与B4，B4分支。	READY
5937_prefl	5937	Sedan	Clarus I	K9A	4	EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	HIGH	生产区间跨1998年改款，改款前分支。	READY
5937_facelift	5937	Sedan	Clarus I facelift	GC	4	EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	HIGH	生产区间跨1998年改款，改款后分支。	READY
5938_3dr	5938	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5938_5dr	5938	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5939_prefl	5939	Sedan	Clarus I	K9A	4	EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	HIGH	生产区间跨1998年改款，改款前分支。	READY
5939_facelift	5939	Sedan	Clarus I facelift	GC	4	EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	HIGH	生产区间跨1998年改款，改款后分支。	READY
5944_b3	5944	Wagon	Passat B3	35I	5	EU-VW-PASSAT-B3-35I-VARIANT-WAGON-01	HIGH	生产区间跨B3与B4，B3 Variant分支。	READY
5944_b4	5944	Wagon	Passat B4	3A	5	EU-VW-PASSAT-B4-3A-VARIANT-WAGON-01	HIGH	生产区间跨B3与B4，B4 Variant分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XK8-X100-COUPE-40-01	4760	1829	1296	Auto-Data Jaguar XK Coupe X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x100-4.0-v8-284hp-automatic-240
EU-JAGUAR-XK8-X100-CONVERTIBLE-40-01	4760	1829	1306	Auto-Data Jaguar XK Convertible X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-convertible-x100-4.0-v8-284hp-automatic-236
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Fiat Grande Punto official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2005-UK.pdf
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Fiat Grande Punto official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2005-UK.pdf
EU-VW-PASSAT-B3-35I-SEDAN-01	4575	1705	1430	Auto-Data Volkswagen Passat B3 2.0 Syncro	https://www.auto-data.net/en/volkswagen-passat-b3-2.0-syncro-115hp-8971
EU-VW-PASSAT-B4-3A-SEDAN-01	4605	1720	1430	Volkswagen Classic Passat B4 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	4696	1770	1420	Auto-Data Kia Clarus K9A	https://www.auto-data.net/en/kia-clarus-k9a-generation-600
EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	4731	1770	1420	Auto-Data Kia Clarus GC	https://www.auto-data.net/en/kia-clarus-gc-generation-598
EU-VW-PASSAT-B3-35I-VARIANT-WAGON-01	4570	1705	1450	Volkswagen Classic Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B4-3A-VARIANT-WAGON-01	4595	1720	1445	Volkswagen Classic Passat B4 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
```

## 下一步优先处理

1. 闭合 VW Jetta VI 改款前、改款后外廓，并按发动机实际供应阶段关联 `5941、5943、5946`。
2. 处理 Toyota RAV4 III、Yaris III 和 Land Cruiser 200 的多次改款及配置高度边界。
3. 解决 Fiat Ktype `5940` 横跨 Grande Punto 与 Punto Evo 的车系命名边界。
4. 集中处理 Alfa Romeo MiTo、Ford Fiesta I，以及 Caterham Seven 标准、SV、CSR 车架差异。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jaguar-xk-convertible-x100-4.0-v8-284hp-automatic-236?utm_source=chatgpt.com "Jaguar XK Convertible (X100) 4.0 V8 (284 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2005-UK.pdf?utm_source=chatgpt.com "Grande Punto"
[3]: https://www.auto-data.net/en/kia-clarus-model-280?utm_source=chatgpt.com "Kia Clarus | Technical Specs, Fuel consumption, Dimensions"
[4]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541?utm_source=chatgpt.com "Vehicle data Passat B3 profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 VW Jetta VI 改款前、改款后两个尺寸组：改款前为 `4644×1778×1482 mm`，改款后为 `4659×1778×1482 mm`。改款后数据由 Volkswagen UK 官方手册确认，图示同时给出含镜宽度 `2020 mm` 和车身宽度 `1778 mm`。([汽车数据网][1])
* Ktype `5941` 的 1.2 TSI 105 hp 同时覆盖改款前后，拆为两行；Ktype `5943` 的 1.6 TDI 105 hp 和 `5946` 的 2.0 TDI 140 hp 仅关联改款前组，不将改款后的 110/150 hp 发动机错误视为同一 Ktype。([汽车数据网][2])
* Ktype `5940` 的生产区间横跨 Grande Punto 与 Punto Evo，并同时覆盖三门、五门车身，已拆为四个物理分支，全部复用已确认尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：90
* `READY` 映射行：134
* `PENDING` Ktype：10
* 当前已引用尺寸组：71
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5940_grande_3dr	5940	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Grande Punto三门分支。	READY
5940_grande_5dr	5940	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Grande Punto五门分支。	READY
5940_evo_3dr	5940	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Punto Evo三门分支。	READY
5940_evo_5dr	5940	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Punto Evo五门分支。	READY
5941_prefl	5941	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	1.2 TSI生产区间跨2014年改款；改款前分支。	READY
5941_facelift	5941	Sedan	Jetta VI facelift		4	EU-VW-JETTA-VI-SEDAN-FACELIFT-01	HIGH	1.2 TSI生产区间跨2014年改款；改款后分支。	READY
5943	5943	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	1.6 TDI 105 hp对应改款前车身。	READY
5946	5946	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	2.0 TDI 140 hp对应改款前车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-JETTA-VI-SEDAN-PREFL-01	4644	1778	1482	Auto-Data Volkswagen Jetta VI 1.2 TSI	https://www.auto-data.net/en/volkswagen-jetta-vi-1.2-tsi-105hp-16809
EU-VW-JETTA-VI-SEDAN-FACELIFT-01	4659	1778	1482	Volkswagen UK Jetta 2014-2018 official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/jetta-2014-2018/vw_jetta_2014-2018_dec_2015.pdf
```

## 下一步优先处理

1. 集中闭合 Toyota RAV4 III、Yaris III 和 Land Cruiser 200 的门数、改款及高度边界。
2. 处理 Alfa Romeo MiTo 跨 2013、2016 两次改款的物理分支。
3. 判断 Ford Fiesta I 1.1 是否同时覆盖标准保险杠与长保险杠外廓，并优先复用已有尺寸组。
4. 最后集中解决 Caterham Seven R500、CSR、标准车架和 SV 车架的尺寸边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-jetta-vi-1.6-tdi-105hp-16810?utm_source=chatgpt.com "Volkswagen Jetta VI 1.6 TDI (105 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-jetta-vi-facelift-2014-generation-4323?utm_source=chatgpt.com "Volkswagen Jetta VI (facelift 2014) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 Alfa Romeo MiTo 955 的初期、2013 改款及 2016 改款三个外廓阶段。三个阶段三维均为 `4063×1720×1446 mm`，但前脸及外部造型边界不同，因此分别建组。([Stellantis Media][1])
* 已闭合 Toyota Yaris III 1.0 VVT-i 的初期、2014 改款及 2017 改款阶段，长度依次为 `3885 / 3950 / 3945 mm`，宽度和高度均为 `1695×1510 mm`。Ktype 未区分门数，各阶段按三门、五门物理车身拆分。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：92
* `READY` 映射行：143
* `PENDING` Ktype：8
* 当前已引用尺寸组：80
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5838_prefl	5838	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	HIGH	生产区间跨两次改款；初期外廓分支。	READY
5838_facelift2013	5838	Hatchback	MiTo facelift 2013	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	HIGH	生产区间跨两次改款；2013改款分支。	READY
5838_facelift2016	5838	Hatchback	MiTo facelift 2016	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2016-01	HIGH	生产区间跨两次改款；2016改款分支。	READY
5887_prefl_3dr	5887	Hatchback	Yaris III	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	HIGH	生产区间跨两次改款；初期三门分支。	READY
5887_prefl_5dr	5887	Hatchback	Yaris III	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	HIGH	生产区间跨两次改款；初期五门分支。	READY
5887_facelift2014_3dr	5887	Hatchback	Yaris III facelift 2014	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	HIGH	2014改款三门分支。	READY
5887_facelift2014_5dr	5887	Hatchback	Yaris III facelift 2014	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	HIGH	2014改款五门分支。	READY
5887_facelift2017_3dr	5887	Hatchback	Yaris III facelift 2017	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	HIGH	2017改款三门分支。	READY
5887_facelift2017_5dr	5887	Hatchback	Yaris III facelift 2017	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	HIGH	2017改款五门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	4063	1720	1446	Alfa Romeo MiTo UK official press pack	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-mito-in-uk-press-pack
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2013	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2013-generation-4997
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2016-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2016 1.4 TB MultiAir	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2016-1.4-tb-multiair-170hp-tct-32429
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	3885	1695	1510	Auto-Data Toyota Yaris III 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.0-vvt-i-69hp-17109
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	3885	1695	1510	Auto-Data Toyota Yaris III 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.0-vvt-i-69hp-17109
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	3950	1695	1510	Auto-Data Toyota Yaris III facelift 2014 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2014-1.0-vvt-i-69hp-24219
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	3950	1695	1510	Auto-Data Toyota Yaris III facelift 2014 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2014-1.0-vvt-i-69hp-24219
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 2017 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.0-vvt-i-69hp-29056
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 2017 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.0-vvt-i-69hp-29056
```

## 下一步优先处理

1. 集中处理 Caterham Seven 的标准、SV、CSR 车架及 R500 外廓，共 5 个剩余 Ktype。
2. 闭合 Toyota RAV4 III 2.4 4WD 的短轴、长轴及改款覆盖边界。
3. 闭合 Toyota Land Cruiser 200 4.6 V8 的 2012、2015 改款分支。
4. 最后判断 Ford Fiesta I 1.1 对应已有标准保险杠或长保险杠尺寸组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-mito-in-uk-press-pack?utm_source=chatgpt.com "NEW ALFA MiTo IN UK (PRESS PACK) | Alfa Romeo | Stellantis Media"
[2]: https://www.auto-data.net/en/toyota-yaris-iii-1.0-vvt-i-69hp-17109 "Toyota Yaris III 1.0 VVT-i (69 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* Ford Fiesta I 1.1 已确认对应 1981–1983 改款后三门标准保险杠外廓，直接复用既有尺寸组 `EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01`；该版本三维为 `3648×1567×1359 mm`。([汽车目录][1])
* Caterham Seven R500 267 hp 已闭合为标准 S3/Superlight 外廓，首次创建 `3100×1575×800 mm` 尺寸组。([Ultimate Specs][2])
* Caterham CSR 203 hp 与 264 hp 属于同一 CSR 车身，统一关联 `3300×1685×1140 mm` 尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：96
* `READY` 映射行：147
* `PENDING` Ktype：4
* 当前已引用尺寸组：82
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5796	5796	Hatchback	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	HIGH	1981–1983改款后三门标准保险杠外廓。	READY
5807	5807	Convertible	Seven Superlight R500	CF	2	EU-CATERHAM-SEVEN-CF-CONVERTIBLE-R500-01	HIGH	R500标准S3/Superlight车身。	READY
5810	5810	Convertible	Seven CSR		2	EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	HIGH	CSR 200车身。	READY
5832	5832	Convertible	Seven CSR		2	EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	HIGH	CSR 260车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CATERHAM-SEVEN-CF-CONVERTIBLE-R500-01	3100	1575	800	UltimateSpecs Caterham Seven Superlight R500	https://www.ultimatespecs.com/car-specs/Caterham/33398/Caterham-7-Seven-Superlight-R-500.html
EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	3300	1685	1140	Auto-Data Caterham CSR 200; Auto-Data Caterham CSR 260 Superlight	https://www.auto-data.net/en/caterham-csr-csr-200hp-12482; https://www.auto-data.net/en/caterham-csr-csr-260hp-superlight-12483
```

## 下一步优先处理

1. 确认 Caterham Seven 1.6 152 hp、126 hp 是否同时覆盖标准 S3 与较宽 SV 车架，并闭合对应三维。
2. 拆分 Toyota RAV4 III 2.4 4WD Ktype `5806` 所覆盖的 `ACA31` 与 `ACA33` 物理车身边界。
3. 闭合 Toyota Land Cruiser 200 4.6 V8 Ktype `5898` 的 2012 与 2015 改款外廓和统一高度口径。
4. 上述四个 Ktype 完成后，立即执行一次机械收尾并输出两张最终完整 TSV 和指定下载链接。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/922805/ford_fiesta_1_1.html?utm_source=chatgpt.com "1981 Ford Fiesta 1.1 (man. 4) (model since September ..."
[2]: https://www.ultimatespecs.com/car-specs/Caterham/33398/Caterham-7-Seven-Superlight-R-500.html?utm_source=chatgpt.com "Caterham 7 Seven Superlight R 500 Specs"
[3]: https://www.auto-data.net/en/caterham-csr-csr-200hp-12482?utm_source=chatgpt.com "Caterham CSR CSR (200 Hp) | Technical specs, data, fuel ..."


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5501-5600_ktype_dimension_mapping_final.tsv
- all_5501-5600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 最后 4 个 Ktype 已全部闭合。
* Toyota RAV4 III 2.4 4WD 按改款前标准版、改款前 Sport、改款后 Style、改款后 X、改款后 Sport 拆为 5 个确定外廓分支。([丰田][1])
* Caterham Seven 1.6 的 125 hp 与 150 hp 均覆盖标准 S3 和加宽 SV 车架，两个 Ktype 各拆为两行，并共同复用两个尺寸组。([汽车目录][2])
* Toyota Land Cruiser 200 的 234 kW / 318 hp 版本关联 2012 年改款 J200 外廓；未错误追加功率不同的后续版本。([newsroom.toyota.eu][3])
* 已完成固定表头、唯一主键、引用闭合、正整数三维、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：157
* `READY` 映射行：157
* `PENDING` 映射：0
* 最终尺寸组：91
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5779	5779	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	HIGH		READY
5780	5780	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	HIGH		READY
5781	5781	Wagon	Marea 185	185	5	EU-FIAT-MAREA-185-WEEKEND-WAGON-24TD-01	HIGH	2.4 TD对应独立高度外廓。	READY
5785_prefl	5785	Sedan	GS III		4	EU-LEXUS-GS-III-S190-SEDAN-AWD-PREFL-01	HIGH	生产区间跨2008年改款；改款前分支。	READY
5785_facelift	5785	Sedan	GS III facelift		4	EU-LEXUS-GS-III-S190-SEDAN-AWD-FACELIFT-01	HIGH	生产区间跨2008年改款；改款后分支。	READY
5788	5788	SUV	Maverick I		3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	HIGH	1996–1998三门短轴外廓。	READY
5792	5792	SUV	Maverick I		5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	HIGH	1996–1998五门长轴外廓。	READY
5793_3dr	5793	SUV	Maverick I		3	EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	HIGH	同一Ktype覆盖三门和五门，按门数拆分。	READY
5793_5dr	5793	SUV	Maverick I		5	EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	HIGH	同一Ktype覆盖三门和五门，按门数拆分。	READY
5796	5796	Hatchback	Fiesta I facelift	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	HIGH	1981–1983改款后三门标准保险杠外廓。	READY
5801	5801	Hatchback	Ka I	RBT	3	EU-FORD-KA-I-RBT-HATCHBACK-3D-01	HIGH		READY
5802	5802	Hatchback	Ka I	RBT	3	EU-FORD-KA-I-RBT-HATCHBACK-3D-01	HIGH		READY
5804	5804	Sedan	A6 C4		4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
5805_2dr	5805	Sedan	Granada II		2	EU-FORD-GRANADA-II-SEDAN-2D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5805_4dr	5805	Sedan	Granada II		4	EU-FORD-GRANADA-II-SEDAN-4D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5806_prefl_standard	5806	SUV	RAV4 III	ACA31W	5	EU-TOYOTA-RAV4-III-ACA31W-SUV-PREFL-STANDARD-01	HIGH	改款前标准车身。	READY
5806_prefl_sport	5806	SUV	RAV4 III	ACA31W	5	EU-TOYOTA-RAV4-III-ACA31W-SUV-PREFL-SPORT-01	HIGH	改款前Sport宽体外廓。	READY
5806_facelift_style	5806	SUV	RAV4 III facelift	ACA31W	5	EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-STYLE-01	HIGH	改款后Style短保险杠外廓。	READY
5806_facelift_x	5806	SUV	RAV4 III facelift	ACA31W	5	EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-X-01	HIGH	改款后X长保险杠外廓。	READY
5806_facelift_sport	5806	SUV	RAV4 III facelift	ACA31W	5	EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-SPORT-01	HIGH	改款后Sport宽体外廓。	READY
5807	5807	Convertible	Seven Superlight R500	CF	2	EU-CATERHAM-SEVEN-CF-CONVERTIBLE-R500-01	HIGH	R500标准S3/Superlight车身。	READY
5808	5808	Wagon	A6 C4		5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
5809	5809	Sedan	A6 C4		4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
5810	5810	Convertible	Seven CSR		2	EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	HIGH	CSR 200车身。	READY
5811_2dr	5811	Sedan	Granada II		2	EU-FORD-GRANADA-II-SEDAN-2D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5811_4dr	5811	Sedan	Granada II		4	EU-FORD-GRANADA-II-SEDAN-4D-01	MEDIUM	同一Ktype覆盖二门与四门轿车，按门数拆分。	READY
5812	5812	Wagon	A6 C4		5	EU-AUDI-A6-C4-AVANT-WAGON-01	HIGH		READY
5813	5813	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
5814	5814	Wagon	Granada II		5	EU-FORD-GRANADA-II-WAGON-01	HIGH		READY
5816	5816	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5817	5817	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5818	5818	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5819	5819	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5820	5820	Hatchback	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	HIGH		READY
5821	5821	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5822	5822	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5823	5823	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5824	5824	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5825	5825	Sedan	Mondeo I facelift		4	EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	HIGH		READY
5826	5826	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5827	5827	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5828	5828	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5829	5829	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5830	5830	Wagon	Mondeo I facelift		5	EU-FORD-MONDEO-I-FACELIFT-WAGON-01	HIGH		READY
5831	5831	Coupe	Coupe B3	89	2	EU-AUDI-COUPE-B3-89-COUPE-01	HIGH		READY
5832	5832	Convertible	Seven CSR		2	EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	HIGH	CSR 260车身。	READY
5833	5833	Coupe	Probe I		3	EU-FORD-USA-PROBE-I-COUPE-01	HIGH		READY
5835_s3	5835	Convertible	Seven Roadsport 150	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	HIGH	标准S3车架。	READY
5835_sv	5835	Convertible	Seven Roadsport 150	SV	2	EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	HIGH	加长加宽SV车架。	READY
5836_s3	5836	Convertible	Seven Roadsport 125	S3	2	EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	HIGH	标准S3车架。	READY
5836_sv	5836	Convertible	Seven Roadsport 125	SV	2	EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	HIGH	加长加宽SV车架。	READY
5837	5837	Coupe	MP4-12C		2	EU-MCLAREN-MP4-12C-COUPE-01	HIGH		READY
5838_prefl	5838	Hatchback	MiTo	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	HIGH	生产区间跨两次改款；初期外廓分支。	READY
5838_facelift2013	5838	Hatchback	MiTo facelift 2013	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	HIGH	生产区间跨两次改款；2013改款分支。	READY
5838_facelift2016	5838	Hatchback	MiTo facelift 2016	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2016-01	HIGH	生产区间跨两次改款；2016改款分支。	READY
5839	5839	Convertible	370Z Roadster	Z34	2	EU-NISSAN-370Z-Z34-ROADSTER-PREFL-01	HIGH	330 hp早期Roadster外廓。	READY
5840	5840	Hatchback	Cube Z12	Z12	5	EU-NISSAN-CUBE-Z12-HATCHBACK-01	HIGH		READY
5841_kingcab	5841	Pickup	Navara D40 facelift	D40	2	EU-NISSAN-NAVARA-D40-KINGCAB-01	HIGH	同一Ktype覆盖King Cab与Double Cab，按驾驶室拆分。	READY
5841_doublecab	5841	Pickup	Navara D40 facelift	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH	同一Ktype覆盖King Cab与Double Cab，按驾驶室拆分。	READY
5842	5842	Pickup	Navara D40 facelift	D40	4	EU-NISSAN-NAVARA-D40-DOUBLECAB-01	HIGH		READY
5852	5852	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
5853_phase1	5853	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5853_phase2	5853	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5853_phase3	5853	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5854_prefl	5854	Coupe	Coupe I	RD	3	EU-HYUNDAI-COUPE-I-RD-COUPE-PREFL-01	HIGH	生产区间跨1999年改款；改款前分支。	READY
5854_facelift	5854	Coupe	Coupe I facelift	RD2	3	EU-HYUNDAI-COUPE-I-RD2-COUPE-FACELIFT-01	HIGH	生产区间跨1999年改款；改款后分支。	READY
5855_phase1	5855	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5855_phase2	5855	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5855_phase3	5855	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5856_phase1	5856	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5856_phase2	5856	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5856_phase3	5856	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5857	5857	SUV	Frontera A Sport		3	EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	HIGH	开放式Sport三门短轴车身。	READY
5858_phase1	5858	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	跨三阶段外廓；Phase I分支。	READY
5858_phase2	5858	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨三阶段外廓；Phase II分支。	READY
5858_phase3	5858	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨三阶段外廓；Phase III分支。	READY
5859_phase1	5859	MPV	Scenic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE1-01	HIGH	生产始于Phase I后期；Phase I分支。	READY
5859_phase2	5859	MPV	Scenic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE2-01	HIGH	跨阶段外廓；Phase II分支。	READY
5859_phase3	5859	MPV	Scenic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE3-01	HIGH	跨阶段外廓；Phase III分支。	READY
5860	5860	SUV	Frontera A		5	EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	HIGH	封闭式五门长轴车身。	READY
5861_phase1	5861	MPV	Grand Scenic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	HIGH	生产始于Phase I后期；Phase I分支。	READY
5861_phase2	5861	MPV	Grand Scenic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	HIGH	跨阶段外廓；Phase II分支。	READY
5861_phase3	5861	MPV	Grand Scenic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	HIGH	跨阶段外廓；Phase III分支。	READY
5880	5880	MPV	R-Class facelift	W251	5	EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	HIGH	标准轴距W251车身。	READY
5883	5883	MPV	Phedra	179	5	EU-LANCIA-PHEDRA-179-MPV-01	HIGH		READY
5887_prefl_3dr	5887	Hatchback	Yaris III	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	HIGH	生产区间跨两次改款；初期三门分支。	READY
5887_prefl_5dr	5887	Hatchback	Yaris III	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	HIGH	生产区间跨两次改款；初期五门分支。	READY
5887_facelift2014_3dr	5887	Hatchback	Yaris III facelift 2014	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	HIGH	2014改款三门分支。	READY
5887_facelift2014_5dr	5887	Hatchback	Yaris III facelift 2014	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	HIGH	2014改款五门分支。	READY
5887_facelift2017_3dr	5887	Hatchback	Yaris III facelift 2017	KSP130	3	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	HIGH	2017改款三门分支。	READY
5887_facelift2017_5dr	5887	Hatchback	Yaris III facelift 2017	KSP130	5	EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	HIGH	2017改款五门分支。	READY
5893	5893	Wagon	Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
5894	5894	Wagon	Golf III	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
5898	5898	SUV	Land Cruiser 200 facelift 2012	J200	5	EU-TOYOTA-LAND-CRUISER-200-J200-SUV-FACELIFT2012-01	HIGH	234 kW/318 hp对应2012年改款外廓。	READY
5900	5900	Coupe	XK8 X100	X100	2	EU-JAGUAR-XK8-X100-COUPE-40-01	HIGH		READY
5902	5902	Convertible	XK8 X100	X100	2	EU-JAGUAR-XK8-X100-CONVERTIBLE-40-01	HIGH		READY
5904_3dr	5904	Hatchback	i20 I	PB	3	EU-HYUNDAI-I20-I-PB-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5904_5dr	5904	Hatchback	i20 I	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5908_prefl	5908	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5908_facelift	5908	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5910_prefl	5910	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5910_facelift	5910	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5913_prefl	5913	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5913_facelift	5913	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5914_prefl	5914	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5914_facelift	5914	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5916_prefl	5916	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5916_facelift	5916	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5917_prefl	5917	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5917_facelift	5917	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5918_prefl	5918	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5918_facelift	5918	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5921_prefl	5921	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	生产区间跨1999年改款，按改款前外廓拆分。	READY
5921_facelift	5921	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	生产区间跨1999年改款，按改款后外廓拆分。	READY
5922	5922	MPV	Sintra		5	EU-OPEL-SINTRA-MPV-01	HIGH		READY
5924	5924	MPV	Sintra		5	EU-OPEL-SINTRA-MPV-01	HIGH		READY
5925	5925	Hatchback	Bravo II	198	5	EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	HIGH		READY
5926	5926	Coupe	Brera	939	3	EU-ALFA-ROMEO-BRERA-939-COUPE-01	HIGH	输入Schrägheck，按Brera 939三门Coupe归类。	READY
5927	5927	Convertible	Spider 939	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH		READY
5928_3dr	5928	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5928_5dr	5928	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5929_prefl	5929	Hatchback	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5929_facelift	5929	Hatchback	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5930_prefl	5930	Hatchback	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5930_facelift	5930	Hatchback	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5931_3dr	5931	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5931_5dr	5931	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5932	5932	Sedan	S-Class W140 facelift	W140	4	EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	HIGH		READY
5933_b3	5933	Sedan	Passat B3	35I	4	EU-VW-PASSAT-B3-35I-SEDAN-01	HIGH	生产区间跨B3与B4，B3分支。	READY
5933_b4	5933	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-3A-SEDAN-01	HIGH	生产区间跨B3与B4，B4分支。	READY
5934	5934	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	改款前生产区间。	READY
5935_prefl	5935	Wagon	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5935_facelift	5935	Wagon	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5936_prefl	5936	Wagon	Superb II	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产区间跨2013年改款；改款前分支。	READY
5936_facelift	5936	Wagon	Superb II facelift	3T	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产区间跨2013年改款；改款后分支。	READY
5937_prefl	5937	Sedan	Clarus I	K9A	4	EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	HIGH	生产区间跨1998年改款，改款前分支。	READY
5937_facelift	5937	Sedan	Clarus I facelift	GC	4	EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	HIGH	生产区间跨1998年改款，改款后分支。	READY
5938_3dr	5938	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5938_5dr	5938	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	同一Ktype覆盖三门与五门，按门数拆分。	READY
5939_prefl	5939	Sedan	Clarus I	K9A	4	EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	HIGH	生产区间跨1998年改款，改款前分支。	READY
5939_facelift	5939	Sedan	Clarus I facelift	GC	4	EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	HIGH	生产区间跨1998年改款，改款后分支。	READY
5940_grande_3dr	5940	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Grande Punto三门分支。	READY
5940_grande_5dr	5940	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Grande Punto五门分支。	READY
5940_evo_3dr	5940	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Punto Evo三门分支。	READY
5940_evo_5dr	5940	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	HIGH	生产区间覆盖Grande Punto与Punto Evo；Punto Evo五门分支。	READY
5941_prefl	5941	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	1.2 TSI生产区间跨2014年改款；改款前分支。	READY
5941_facelift	5941	Sedan	Jetta VI facelift		4	EU-VW-JETTA-VI-SEDAN-FACELIFT-01	HIGH	1.2 TSI生产区间跨2014年改款；改款后分支。	READY
5942_prefl	5942	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5942_facelift	5942	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5943	5943	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	1.6 TDI 105 hp对应改款前车身。	READY
5944_b3	5944	Wagon	Passat B3	35I	5	EU-VW-PASSAT-B3-35I-VARIANT-WAGON-01	HIGH	生产区间跨B3与B4，B3 Variant分支。	READY
5944_b4	5944	Wagon	Passat B4	3A	5	EU-VW-PASSAT-B4-3A-VARIANT-WAGON-01	HIGH	生产区间跨B3与B4，B4 Variant分支。	READY
5945	5945	Sedan	Sephia I	FA	4	EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	HIGH		READY
5946	5946	Sedan	Jetta VI		4	EU-VW-JETTA-VI-SEDAN-PREFL-01	HIGH	2.0 TDI 140 hp对应改款前车身。	READY
5947_prefl	5947	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	HIGH	生产区间跨改款，按改款前外廓拆分。	READY
5947_facelift	5947	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	HIGH	生产区间跨改款，按改款后外廓拆分。	READY
5948	5948	Hatchback	Sephia I	FA	5	EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5501-5600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-MAREA-185-WEEKEND-WAGON-19TD-01	4484	1741	1500	Automobile-Catalog Fiat Marea Weekend TD 75; Automobile-Catalog Fiat Marea Weekend TD 100	https://www.automobile-catalog.com/car/1997/722015/fiat_marea_weekend_td_75_sx.html; https://www.automobile-catalog.com/car/1997/722045/fiat_marea_weekend_td_100_sx.html
EU-FIAT-MAREA-185-WEEKEND-WAGON-24TD-01	4484	1741	1495	Auto-Data Fiat Marea Weekend 2.4 TD 125	https://www.auto-data.net/en/fiat-marea-weekend-185-2.4-td-125-125hp-7220
EU-LEXUS-GS-III-S190-SEDAN-AWD-PREFL-01	4825	1820	1435	Auto-Data Lexus GS III 350 AWD	https://www.auto-data.net/en/lexus-gs-iii-350-v6-307hp-awd-automatic-36777
EU-LEXUS-GS-III-S190-SEDAN-AWD-FACELIFT-01	4825	1820	1435	Auto-Data Lexus GS III facelift 350 AWD	https://www.auto-data.net/en/lexus-gs-iii-facelift-2008-350-v6-307hp-awd-automatic-5908
EU-FORD-MAVERICK-I-UDS-SUV-SWB-02	4185	1755	1830	Auto-Data Ford Maverick 3-door	https://www.auto-data.net/en/ford-maverick-uds-uns-2.4-i-3-dr-116hp-7550
EU-FORD-MAVERICK-I-UDS-SUV-LWB-02	4665	1755	1850	Auto-Data Ford Maverick 5-door	https://www.auto-data.net/en/ford-maverick-uds-uns-2.4-i-gls-5-dr-118hp-7551
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359	Automobile-Catalog Ford Fiesta 1.1	https://www.automobile-catalog.com/car/1981/922805/ford_fiesta_1_1.html
EU-FORD-KA-I-RBT-HATCHBACK-3D-01	3620	1631	1368	Ford Ka 1996 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/12/Ford-Ka-1996-UK-.pdf
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Auto-Data Audi A6 C4 2.3	https://www.auto-data.net/en/audi-a6-4a-c4-2.3-133hp-4751
EU-FORD-GRANADA-II-SEDAN-2D-01	4633	1791	1416	Motor-Car Ford Granada Mk II	https://motor-car.net/ford-eu/item/11112-granada-mk-ii-1977-85
EU-FORD-GRANADA-II-SEDAN-4D-01	4633	1791	1416	Motor-Car Ford Granada Mk II	https://motor-car.net/ford-eu/item/11112-granada-mk-ii-1977-85
EU-TOYOTA-RAV4-III-ACA31W-SUV-PREFL-STANDARD-01	4335	1815	1685	Toyota RAV4 official history	https://global.toyota/en/detail/257506
EU-TOYOTA-RAV4-III-ACA31W-SUV-PREFL-SPORT-01	4335	1855	1685	Toyota RAV4 Sport vehicle catalog	https://toyota.jp/ucar/catalog/brand-TOYOTA/car-RAV4/200511/10030650/
EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-STYLE-01	4335	1815	1685	GAZOO Toyota RAV4 Style catalog	https://gazoo.com/catalog/maker/TOYOTA/RAV4/200511/10068788/
EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-X-01	4365	1815	1685	GAZOO Toyota RAV4 X catalog	https://gazoo.com/catalog/maker/TOYOTA/RAV4/200511/10068806/
EU-TOYOTA-RAV4-III-ACA31W-SUV-FACELIFT-SPORT-01	4365	1855	1685	GAZOO Toyota RAV4 Sport catalog	https://gazoo.com/catalog/maker/TOYOTA/RAV4/200511/10068803/
EU-CATERHAM-SEVEN-CF-CONVERTIBLE-R500-01	3100	1575	800	UltimateSpecs Caterham Seven Superlight R500	https://www.ultimatespecs.com/car-specs/Caterham/33398/Caterham-7-Seven-Superlight-R-500.html
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440	Auto-Data Audi A6 C4 Avant 2.3	https://www.auto-data.net/en/audi-a6-avant-4a-c4-2.3-133hp-4769
EU-CATERHAM-SEVEN-CSR-CONVERTIBLE-01	3300	1685	1140	Auto-Data Caterham CSR 200; Auto-Data Caterham CSR 260 Superlight	https://www.auto-data.net/en/caterham-csr-csr-200hp-12482; https://www.auto-data.net/en/caterham-csr-csr-260hp-superlight-12483
EU-FORD-GRANADA-II-WAGON-01	4630	1740	1380	Motor-Car Ford Granada Mk II	https://motor-car.net/ford-eu/item/11112-granada-mk-ii-1977-85
EU-FORD-MONDEO-I-FACELIFT-HATCHBACK-01	4556	1749	1372	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-I-FACELIFT-SEDAN-01	4556	1749	1372	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-I-FACELIFT-WAGON-01	4671	1749	1391	Ford Mondeo 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-AUDI-COUPE-B3-89-COUPE-01	4366	1716	1370	Auto-Data Audi Coupe B3 1.8	https://www.auto-data.net/en/audi-coupe-b3-89-1.8-112hp-4456
EU-FORD-USA-PROBE-I-COUPE-01	4520	1740	1320	Auto-Data Ford Probe I 2.2 GT	https://www.auto-data.net/en/ford-probe-i-2.2-gt-147hp-7996
EU-CATERHAM-SEVEN-S3-CONVERTIBLE-ROADSPORT-01	3380	1575	1115	Automobile-Catalog Caterham Seven Roadsport 125; Automobile-Catalog Caterham Seven Roadsport 150	https://www.automobile-catalog.com/car/2007/338090/caterham_7_roadsport_125.html; https://www.automobile-catalog.com/car/2008/338120/caterham_7_roadsport_150.html
EU-CATERHAM-SEVEN-SV-CONVERTIBLE-ROADSPORT-01	3460	1685	1115	Automobile-Catalog Caterham Seven SV Roadsport 125; Automobile-Catalog Caterham Seven SV Roadsport 150	https://www.automobile-catalog.com/car/2007/338210/caterham_7_sv_roadsport_sigma_125.html; https://www.automobile-catalog.com/car/2008/338300/caterham_7_sv_roadsport_sigma_150_6-speed.html
EU-MCLAREN-MP4-12C-COUPE-01	4509	1908	1199	McLaren MP4-12C technical factsheet	https://cars.mclaren.press/assets/documents/original/3916-mclaren-mp4-12c-technical-factsheet.pdf
EU-ALFA-ROMEO-MITO-955-HATCHBACK-PREFL-01	4063	1720	1446	Alfa Romeo MiTo UK official press pack	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-mito-in-uk-press-pack
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2013-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2013	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2013-generation-4997
EU-ALFA-ROMEO-MITO-955-HATCHBACK-FACELIFT2016-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2016	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2016-1.4-tb-multiair-170hp-tct-32429
EU-NISSAN-370Z-Z34-ROADSTER-PREFL-01	4250	1845	1325	Nissan 370Z 2010 official brochure	https://s3.amazonaws.com/cdn.autoipacket.com/brochures/nissan/2010/2010-nissan-370z.pdf
EU-NISSAN-CUBE-Z12-HATCHBACK-01	3980	1695	1670	Auto-Data Nissan Cube Z12 1.5 dCi	https://www.auto-data.net/en/nissan-cube-z12-1.5-dci-110hp-dpf-45620
EU-NISSAN-NAVARA-D40-KINGCAB-01	5296	1848	1783	Auto-Data Nissan Navara D40 King Cab	https://www.auto-data.net/en/nissan-navara-d40-king-cab-facelift-2010-generation-4581
EU-NISSAN-NAVARA-D40-DOUBLECAB-01	5296	1848	1795	Auto-Data Nissan Navara D40 Double Cab	https://www.auto-data.net/en/nissan-navara-d40-double-cab-facelift-2010-generation-4580
EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	4700	1770	1405	Auto-Data Hyundai Sonata III Y3 facelift	https://www.auto-data.net/en/hyundai-sonata-iii-y3-facelift-1996-2.0-gsi-16v-125hp-29655
EU-RENAULT-SCENIC-III-MPV-PHASE1-01	4343	1845	1624	Auto-Data Renault Scenic III Phase I	https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.5-dci-110hp-fap-edc-39511
EU-RENAULT-SCENIC-III-MPV-PHASE2-01	4366	1845	1640	Auto-Data Renault Scenic III Phase II	https://www.auto-data.net/en/renault-scenic-iii-phase-ii-collection-2012-1.5-dci-110hp-fap-17459
EU-RENAULT-SCENIC-III-MPV-PHASE3-01	4366	1845	1640	Automobile-Catalog Renault Scenic III Phase III	https://www.automobile-catalog.com/car/2013/2982200/renault_scenic_1_5_dci_95.html
EU-HYUNDAI-COUPE-I-RD-COUPE-PREFL-01	4345	1730	1310	Auto-Data Hyundai Coupe I RD	https://www.auto-data.net/en/hyundai-coupe-i-rd-2.0-i-16v-139hp-13848
EU-HYUNDAI-COUPE-I-RD2-COUPE-FACELIFT-01	4345	1730	1310	Auto-Data Hyundai Coupe I RD2 facelift	https://www.auto-data.net/en/hyundai-coupe-i-rd2-facelift-1999-2.0-i-16v-139hp-automatic-29323
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE1-01	4560	1845	1675	Auto-Data Renault Grand Scenic III Phase I	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-i-1.5-dci-110hp-fap-7-seat-39526
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE2-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase II	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-ii-collection-2012-tce-130hp-17460
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE3-01	4573	1845	1645	Auto-Data Renault Grand Scenic III Phase III	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-iii-1.5-dci-110hp-fap-stop-start-7-seat-38568
EU-OPEL-FRONTERA-A-SPORT-SUV-3D-SWB-01	4192	1780	1721	Auto-Data Opel Frontera A Sport	https://www.auto-data.net/en/opel-frontera-a-sport-2.5-tds-115hp-4x4-2567
EU-OPEL-FRONTERA-A-SUV-5D-LWB-01	4692	1764	1753	Auto-Data Opel Frontera A	https://www.auto-data.net/en/opel-frontera-a-2.5-tds-115hp-4x4-2565
EU-MERCEDES-BENZ-R-KLASSE-W251-MPV-FACELIFT-01	4922	1922	1674	Auto-Data Mercedes-Benz R-Class W251 facelift	https://www.auto-data.net/en/mercedes-benz-r-class-w251-facelift-2010-r-350-cdi-v6-265hp-4matic-g-tronic-37240
EU-LANCIA-PHEDRA-179-MPV-01	4750	1863	1759	Auto-Data Lancia Phedra 2.2 Multijet	https://www.auto-data.net/en/lancia-phedra-2.2-multijet-170hp-automatic-45955
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-PREFL-01	3885	1695	1510	Auto-Data Toyota Yaris III 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.0-vvt-i-69hp-17109
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-PREFL-01	3885	1695	1510	Auto-Data Toyota Yaris III 1.0 VVT-i	https://www.auto-data.net/en/toyota-yaris-iii-1.0-vvt-i-69hp-17109
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2014-01	3950	1695	1510	Auto-Data Toyota Yaris III facelift 2014	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2014-1.0-vvt-i-69hp-24219
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2014-01	3950	1695	1510	Auto-Data Toyota Yaris III facelift 2014	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2014-1.0-vvt-i-69hp-24219
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-3D-FACELIFT2017-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 2017	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.0-vvt-i-69hp-29056
EU-TOYOTA-YARIS-III-KSP130-HATCHBACK-5D-FACELIFT2017-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 2017	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.0-vvt-i-69hp-29056
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant Syncro	https://www.auto-data.net/en/volkswagen-golf-iii-variant-1.8-syncro-90hp-8647
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-FACELIFT2012-01	4950	1970	1865	Toyota Europe Land Cruiser V8 2012; Auto-Data Land Cruiser J200 4.6 V8 318	https://newsroom.toyota.eu/2019-land-cruiser-v8-2012-powertrains/; https://www.auto-data.net/en/toyota-land-cruiser-j200-facelift-2013-4.6-v8-318hp-automatic-18526
EU-JAGUAR-XK8-X100-COUPE-40-01	4760	1829	1296	Auto-Data Jaguar XK Coupe X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-coupe-x100-4.0-v8-284hp-automatic-240
EU-JAGUAR-XK8-X100-CONVERTIBLE-40-01	4760	1829	1306	Auto-Data Jaguar XK Convertible X100 4.0 V8	https://www.auto-data.net/en/jaguar-xk-convertible-x100-4.0-v8-284hp-automatic-236
EU-HYUNDAI-I20-I-PB-HATCHBACK-3D-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.4 CRDi	https://www.auto-data.net/en/hyundai-i20-i-pb-1.4-crdi-75hp-31441
EU-HYUNDAI-I20-I-PB-HATCHBACK-5D-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.4 CRDi	https://www.auto-data.net/en/hyundai-i20-i-pb-1.4-crdi-75hp-31441
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425	Auto-Data Opel Vectra B sedan	https://www.auto-data.net/en/opel-vectra-b-2.0-di-16v-82hp-2288
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425	Auto-Data Opel Vectra B sedan facelift	https://www.auto-data.net/en/opel-vectra-b-facelift-1999-2.0-di-16v-82hp-26208
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425	Auto-Data Opel Vectra B CC	https://www.auto-data.net/en/opel-vectra-b-cc-2.0-di-16v-82hp-2290
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425	Auto-Data Opel Vectra B CC facelift	https://www.auto-data.net/en/opel-vectra-b-cc-facelift-1999-2.0-di-16v-82hp-26210
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan	https://www.auto-data.net/en/opel-vectra-b-caravan-1.6i-75hp-2274
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490	Auto-Data Opel Vectra B Caravan facelift	https://www.auto-data.net/en/opel-vectra-b-caravan-facelift-1999-1.8i-16v-115hp-26211
EU-OPEL-SINTRA-MPV-01	4670	1830	1780	Auto-Data Opel Sintra 2.2i; Auto-Data Opel Sintra 3.0i	https://www.auto-data.net/en/opel-sintra-2.2i-16v-141hp-1754; https://www.auto-data.net/en/opel-sintra-3.0i-24v-201hp-automatic-1755
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498	Auto-Data Fiat Bravo II 1.9 Multijet	https://www.auto-data.net/en/fiat-bravo-ii-198-1.9-multijet-120hp-7173
EU-ALFA-ROMEO-BRERA-939-COUPE-01	4410	1830	1341	Alfa Romeo Brera owner handbook	https://www.alfaclub.ro/manuals/Brera.pdf
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Auto-Data Alfa Romeo Spider 939 2.0 JTDM	https://www.auto-data.net/en/alfa-romeo-spider-939-2.0-jtdm-170hp-42171
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490	Auto-Data Fiat Punto Evo	https://www.auto-data.net/en/fiat-punto-evo-1.4-8v-77hp-start-stop-7273
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490	Auto-Data Fiat Punto Evo	https://www.auto-data.net/en/fiat-punto-evo-1.4-8v-77hp-start-stop-7273
EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	4838	1817	1462	Auto-Data Skoda Superb II 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-1.8-tsi-160hp-4x4-14107
EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	4833	1817	1462	Auto-Data Skoda Superb II facelift 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-facelift-2013-1.8-tsi-160hp-4x4-19292
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Fiat Grande Punto official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2005-UK.pdf
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Fiat Grande Punto official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2005-UK.pdf
EU-MERCEDES-BENZ-S-KLASSE-W140-SEDAN-FACELIFT-01	5113	1886	1486	Auto-Data Mercedes-Benz S-Class W140 facelift	https://www.auto-data.net/en/mercedes-benz-s-class-w140-facelift-1994-s-300-turbodiesel-177hp-5g-tronic-13081
EU-VW-PASSAT-B3-35I-SEDAN-01	4575	1705	1430	Auto-Data Volkswagen Passat B3 2.0 Syncro	https://www.auto-data.net/en/volkswagen-passat-b3-2.0-syncro-115hp-8971
EU-VW-PASSAT-B4-3A-SEDAN-01	4605	1720	1430	Volkswagen Classic Passat B4 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414	Auto-Data Mercedes-Benz C-Class W202	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-230-150hp-12342
EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	4838	1817	1510	Auto-Data Skoda Superb II Combi 1.8 TSI 4x4	https://www.auto-data.net/en/skoda-superb-ii-combi-1.8-tsi-160hp-4x4-56489
EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	4833	1817	1511	Auto-Data Skoda Superb II Combi facelift	https://www.auto-data.net/en/skoda-superb-ii-combi-facelift-2013-1.8-tsi-160hp-4x4-19308
EU-KIA-CLARUS-I-K9A-SEDAN-PREFL-01	4696	1770	1420	Auto-Data Kia Clarus K9A	https://www.auto-data.net/en/kia-clarus-k9a-generation-600
EU-KIA-CLARUS-I-GC-SEDAN-FACELIFT-01	4731	1770	1420	Auto-Data Kia Clarus GC	https://www.auto-data.net/en/kia-clarus-gc-generation-598
EU-VW-JETTA-VI-SEDAN-PREFL-01	4644	1778	1482	Auto-Data Volkswagen Jetta VI 1.2 TSI	https://www.auto-data.net/en/volkswagen-jetta-vi-1.2-tsi-105hp-16809
EU-VW-JETTA-VI-SEDAN-FACELIFT-01	4659	1778	1482	Volkswagen UK Jetta 2014-2018 official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/jetta-2014-2018/vw_jetta_2014-2018_dec_2015.pdf
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427	Auto-Data Mercedes-Benz C-Class W202 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-w202-facelift-1997-c-200-cdi-102hp-12409
EU-VW-PASSAT-B3-35I-VARIANT-WAGON-01	4570	1705	1450	Volkswagen Classic Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B4-3A-VARIANT-WAGON-01	4595	1720	1445	Volkswagen Classic Passat B4 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b4-profile-19544
EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	4280	1692	1390	Auto-Data Kia Sephia I sedan	https://www.auto-data.net/en/kia-sephia-fa-generation-601
EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	4280	1692	1390	Auto-Data Kia Sephia I hatchback	https://www.auto-data.net/en/kia-sephia-fa-generation-601
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5501-5600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.toyota.co.jp/jpn/company/history/75years/vehicle_lineage/car/id60012608/index.html "トヨタ企業サイト | トヨタ自動車75年史 | 車両系統図 | 車両詳細情報"
[2]: https://www.automobile-catalog.com/car/2008/338120/caterham_7_roadsport_150.html "https://www.automobile-catalog.com/car/2008/338120/caterham_7_roadsport_150.html"
[3]: https://newsroom.toyota.eu/2019-land-cruiser-v8-2012-powertrains/ "https://newsroom.toyota.eu/2019-land-cruiser-v8-2012-powertrains/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5501-5600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5501-5600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7140 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2229 行）

