# 任务：all 第 4101-4200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0042__46acd166


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4101-4200 行

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
all 第 4101-4200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-HONDA-PRELUDE-I-COUPE-2D-01	4090	1635	1290
EU-HONDA-PRELUDE-II-COUPE-2D-01	4295	1690	1295
EU-HONDA-PRELUDE-II-COUPE-2D-FACELIFT-01	4375	1690	1295
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Honda	Prelude	2.0 I EX 16V CAT	Coupe	Frontantrieb	Benzin	101	137	Apr 1987	Jan 1992	2026-01-01	4237
Nissan	Laurel	2	Stufenheck	Heckantrieb	Benzin	71	97	Mar 1977	May 1983	2024-03-01	4238
Honda	Prelude	2.0 I EX 16V	Coupe	Frontantrieb	Benzin	103	140	Oct 1987	Jan 1992	2026-01-01	4239
Nissan	Laurel	2.4	Stufenheck	Heckantrieb	Benzin	83	113	Dec 1977	May 1983	2024-03-01	4240
Honda	Prelude	2.0 I 16V	Coupe	Frontantrieb	Benzin	98	133	Feb 1992	Sep 1996	2026-01-01	4241
Honda	Prelude	2.3 I 16V	Coupe	Frontantrieb	Benzin	118	160	Feb 1992	Sep 1996	2026-01-01	4242
Nissan	Laurel	2	Stufenheck	Heckantrieb	Benzin	71	97	Jan 1981	Jan 1984	2024-03-01	4243
Honda	Civic iii shuttle	1.5	Kombi	Frontantrieb	Benzin	63	86	Oct 1983	Oct 1987	2025-02-03	4244
Nissan	Laurel	2.4	Stufenheck	Heckantrieb	Benzin	83	113	Jan 1981	Jan 1984	2024-03-01	4245
Nissan	Laurel	2.4	Stufenheck	Heckantrieb	Benzin	88	120	Sep 1983	Dec 1985	2024-03-01	4246
Honda	Civic iii shuttle	1.5 4WD	Kombi	Allrad	Benzin	63	86	Jan 1985	Oct 1987	2025-02-03	4247
Nissan	Laurel	2.8 D	Stufenheck	Heckantrieb	Diesel	62	84	Jan 1981	Oct 1985	2024-03-01	4248
Nissan	Laurel	2.4	Stufenheck	Heckantrieb	Benzin	94	128	Jan 1985	Dec 1987	2024-03-01	4249
Honda	Civic iv shuttle	1.6 I 16V 4WD	Kombi	Allrad	Benzin	80	109	Jan 1988	Dec 1989	2025-02-03	4250
Honda	Civic iv shuttle	1.6 I 16V 4WD	Kombi	Allrad	Benzin	81	110	Jan 1988	Feb 1995	2025-02-03	4251
Honda	Accord iv	2.0 16V	Stufenheck	Frontantrieb	Benzin	66	90	Jan 1990	Mar 1993	2024-03-01	4252
Nissan	Laurel	2.8 D	Stufenheck	Heckantrieb	Diesel	62	84	Jan 1985	Dec 1987	2024-03-01	4253
Honda	Accord iv	2.0 16V	Stufenheck	Frontantrieb	Benzin	81	110	Jan 1990	Mar 1993	2024-03-01	4254
Nissan	Laurel	2.8 D	Stufenheck	Heckantrieb	Diesel	66	90	Jan 1985	Dec 1989	2024-03-01	4255
Honda	Accord iv	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	98	133	Jan 1990	Mar 1993	2024-03-01	4256
Honda	Accord iv	2.2 I 16V Automatik	Stufenheck	Frontantrieb	Benzin	108	147	Jan 1990	Mar 1993	2024-03-01	4257
Honda	Accord iv	2.2 I 16V	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1990	Mar 1993	2024-03-01	4258
Honda	Accord iv	2.0 I 16V	Coupe	Frontantrieb	Benzin	98	133	Jan 1992	Sep 1993	2024-03-01	4259
Honda	Accord iv aerodeck	2.2 I 16V	Kombi	Frontantrieb	Benzin	108	147	Jan 1991	Dec 1993	2024-03-01	4260
Honda	Accord iv aerodeck	2.2 I 16V	Kombi	Frontantrieb	Benzin	110	150	Jan 1991	Dec 1993	2024-03-01	4261
Honda	Civic v hatchback	1.3 16V	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1991	Nov 1995	2024-03-01	4262
Honda	Civic v hatchback	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	69	94	Oct 1991	Nov 1995	2024-03-01	4263
Nissan	Primera	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Jun 1990	Jan 1996	2024-03-01	4264
Honda	Civic v hatchback	1.6 16V Vtec	Schrägheck	Frontantrieb	Benzin	92	125	Oct 1991	Nov 1995	2024-03-01	4265
Nissan	Primera	2.0 16V	Stufenheck	Frontantrieb	Benzin	85	116	Jun 1990	Jan 1996	2024-03-01	4266
Honda	Civic v hatchback	1.6 VTI 16V	Schrägheck	Frontantrieb	Benzin	118	160	Oct 1991	Nov 1995	2024-03-01	4267
Nissan	Primera	2.0 GT	Stufenheck	Frontantrieb	Benzin	110	150	Jun 1990	Jan 1996	2024-03-01	4268
Nissan	Primera	2.0 D	Stufenheck	Frontantrieb	Diesel	55	75	Jan 1991	Jan 1996	2024-03-01	4269
Nissan	Primera	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1990	Jan 1996	2024-03-01	4270
Nissan	Primera	2.0 16V	Schrägheck	Frontantrieb	Benzin	85	116	Jun 1990	Jan 1996	2024-03-01	4271
Nissan	Primera	1.6 I	Kombi	Frontantrieb	Benzin	66	90	Jul 1990	Mar 1998	2024-03-01	4272
Nissan	Primera	2.0 I	Kombi	Frontantrieb	Benzin	85	116	Jul 1990	Mar 1998	2024-03-01	4273
Nissan	Primera	2.0 D	Kombi	Frontantrieb	Diesel	55	75	Jul 1990	Dec 1995	2024-03-01	4274
Honda	Civic v	1.5 I 16V	Stufenheck	Frontantrieb	Benzin	69	94	Oct 1991	Nov 1995	2024-03-01	4275
Honda	Civic v	1.6 16V Vtec	Stufenheck	Frontantrieb	Benzin	92	125	Oct 1991	Nov 1995	2024-03-01	4276
Honda	Civic v	1.6 VTI	Stufenheck	Frontantrieb	Benzin	118	160	Oct 1991	Nov 1995	2024-03-01	4277
Honda	Concerto	1.5 I 16V	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1989	Mar 1995	2024-03-01	4278
Honda	Concerto	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	82	112	Aug 1989	Mar 1995	2024-03-01	4279
Honda	Concerto	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	90	122	Aug 1989	Mar 1995	2024-03-01	4280
Honda	Accord v	2.0 I	Stufenheck	Frontantrieb	Benzin	85	116	Mar 1993	Jan 1996	2024-03-01	4281
Honda	Accord v	2.0 I S	Stufenheck	Frontantrieb	Benzin	96	131	Mar 1993	Jan 1996	2024-03-01	4282
Honda	Accord v	2.3 I SR	Stufenheck	Frontantrieb	Benzin	116	158	Mar 1993	Jan 1996	2024-03-01	4283
Honda	Accord iv aerodeck	2.0 I 16V	Kombi	Frontantrieb	Benzin	98	133	Mar 1993	Dec 1993	2024-03-01	4284
Nissan	280zx,zxt	2.8	Coupe	Heckantrieb	Benzin	103	140	Oct 1978	Jun 1983	2024-03-01	4285
Honda	Civic vi fastback	1.6 I	Schrägheck	Frontantrieb	Benzin	83	113	Sep 1994	Jan 1997	2024-03-01	4286
Nissan	280zx,zxt	2.8	Coupe	Heckantrieb	Benzin	108	147	Feb 1980	Sep 1982	2024-03-01	4287
Honda	Civic vi fastback	1.6 I Vtec	Schrägheck	Frontantrieb	Benzin	93	126	Sep 1994	Jan 1997	2024-03-01	4288
Honda	Civic vi fastback	1.5 I Vtec-e	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1994	Jan 1997	2024-03-01	4289
Nissan	280zx,zxt	2.8	Coupe	Heckantrieb	Benzin	110	150	Jan 1982	Feb 1984	2024-03-01	4290
Honda	Civic vi fastback	1.4 I	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1995	Feb 2001	2024-03-01	4291
Honda	Civic v	1.6 I Vtec	Coupe	Frontantrieb	Benzin	92	125	Jan 1994	Mar 1996	2024-03-01	4292
Honda	Civic v	1.5 I LSI	Coupe	Frontantrieb	Benzin	74	101	Aug 1993	Nov 1995	2024-03-01	4293
Nissan	300zx	3	Targa	Heckantrieb	Benzin	125	170	Jan 1984	Dec 1987	2024-03-01	4294
Honda	Accord v	2.2 I ES	Coupe	Frontantrieb	Benzin	110	150	Sep 1993	Feb 1998	2024-03-01	4295
Honda	Accord v aerodeck	2.0 I LS 16V	Kombi	Frontantrieb	Benzin	100	136	Sep 1993	Feb 1998	2024-03-01	4296
Honda	Accord v aerodeck	2.2 I ES	Kombi	Frontantrieb	Benzin	110	150	Sep 1993	Feb 1998	2024-03-01	4297
Nissan	300zx	3.0 Turbo	Targa	Heckantrieb	Benzin	149	203	May 1987	Oct 1990	2024-03-01	4298
Nissan	300zx	3.0 Twin Turbo	Coupe	Heckantrieb	Benzin	208	283	May 1990	Sep 1995	2024-03-01	4299
Nissan	300zx	3.0 Twin Turbo	Coupe	Heckantrieb	Benzin	197	268	May 1990	Sep 1995	2024-03-01	4300
Nissan	100nx	1.6	Coupe	Frontantrieb	Benzin	66	90	Mar 1990	Oct 1994	2024-03-01	4301
Nissan	100nx	2.0 GTI	Coupe	Frontantrieb	Benzin	105	143	Mar 1991	Oct 1994	2024-03-01	4302
Nissan	Silvia	2.0 GP	Coupe	Heckantrieb	Benzin	107	146	Apr 1984	Sep 1988	2024-03-01	4303
Nissan	200sx	1.8 Turbo	Coupe	Heckantrieb	Benzin	124	169	Jul 1988	Nov 1993	2024-03-01	4304
Nissan	Serena	2.3 D	Großraumlimousine	Heckantrieb	Diesel	55	75	Jan 1995	Sep 2001	2024-03-01	4305
Nissan	Serena	2	Großraumlimousine	Heckantrieb	Benzin	93	126	Nov 1992	Sep 2001	2024-03-01	4306
Nissan	Serena	1.6	Großraumlimousine	Heckantrieb	Benzin	71	97	Feb 1993	Sep 2001	2024-03-01	4307
Nissan	Serena	2.0 D	Großraumlimousine	Heckantrieb	Diesel	49	67	Jun 1991	Sep 2001	2024-03-01	4308
Honda	Nsx i	3.0 24V Vtec Automatik	Coupe	Heckantrieb	Benzin	188	256	Jun 1990	Sep 2005	2024-03-01	4309
Honda	Nsx i	3.0 24V Vtec	Coupe	Heckantrieb	Benzin	201	274	Jun 1990	Sep 2005	2024-03-01	4310
Nissan	100nx	1.6 SR	Coupe	Frontantrieb	Benzin	75	102	Sep 1993	Oct 1994	2024-03-01	4311
Nissan	Urvan	2.4 I	Bus	Heckantrieb	Benzin	74	101	May 1989	Sep 1993	2024-03-01	4312
Nissan	Urvan	2.5 D	Bus	Heckantrieb	Diesel	59	80	May 1989	Oct 1996	2024-03-01	4313
Nissan	Terrano	2.7 TD 4WD	Geländewagen geschlossen	Allrad	Diesel	74	101	Feb 1993	Jan 2002	2024-03-01	4314
Nissan	Terrano	2.4 I 12V 4WD	Geländewagen geschlossen	Allrad	Benzin	91	124	Feb 1993	Dec 1997	2024-03-01	4315
Nissan	Terrano	2.4 I 4WD	Geländewagen geschlossen	Allrad	Benzin	76	103	Oct 1987	Feb 1993	2024-03-01	4316
Nissan	Terrano	2.7 TD 4WD	Geländewagen geschlossen	Allrad	Diesel	73	99	Feb 1989	Feb 1996	2024-03-01	4317
Nissan	Patrol iii/1 station wagon	2.8	Geländewagen geschlossen	Allrad	Benzin	88	120	Jul 1980	Aug 1988	2024-03-01	4318
Nissan	Patrol iii/1 hardtop	2.8	Geländewagen geschlossen	Allrad	Benzin	88	120	Jul 1980	Aug 1988	2024-03-01	4319
Nissan	Patrol iii/1 hardtop	2.8	Geländewagen geschlossen	Allrad	Benzin	89	121	Jul 1980	Aug 1988	2024-03-01	4320
Nissan	Patrol iii/1 station wagon	3.3 D	Geländewagen geschlossen	Allrad	Diesel	70	95	Nov 1979	Aug 1988	2024-03-01	4321
Nissan	Patrol iii/1 hardtop	3.3 D	Geländewagen geschlossen	Allrad	Diesel	70	95	Nov 1979	Aug 1988	2024-03-01	4322
Nissan	Patrol iii/1 station wagon	3.3 TD	Geländewagen geschlossen	Allrad	Diesel	81	110	Jul 1983	Aug 1988	2024-03-01	4323
Nissan	Patrol iii/1 hardtop	3.3 TD	Geländewagen geschlossen	Allrad	Diesel	81	110	Jul 1983	Aug 1988	2024-03-01	4324
Nissan	Patrol iii/2 station wagon	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	85	116	Jun 1989	Nov 1995	2024-03-01	4325
Nissan	Patrol gr iv	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	85	116	Sep 1988	Jun 1997	2024-03-01	4326
Nissan	Prairie	1.8 SGL	Großraumlimousine	Frontantrieb	Benzin	65	88	Jul 1983	Dec 1985	2024-03-01	4327
Nissan	Prairie	1.8 SGL	Großraumlimousine	Frontantrieb	Benzin	66	90	May 1985	Oct 1987	2024-03-01	4328
Nissan	Prairie	2.0 4X4	Großraumlimousine	Allrad	Benzin	68	92	Jun 1986	Sep 1988	2024-03-01	4329
Nissan	Prairie	2.0 I	Großraumlimousine	Frontantrieb	Benzin	72	98	Oct 1988	Apr 1992	2024-03-01	4330
Nissan	Prairie	2.4 I	Großraumlimousine	Frontantrieb	Benzin	98	133	Jan 1990	Jul 1994	2024-03-01	4331
Nissan	Vanette	1.5	Bus	Heckantrieb	Benzin	51	69	Jan 1983	Dec 1987	2024-03-01	4332
Nissan	Vanette	2.4 I	Bus	Heckantrieb	Benzin	74	101	Oct 1986	Dec 1995	2024-03-01	4333
Nissan	Vanette	2.4 I	Bus	Heckantrieb	Benzin	77	105	Oct 1986	Dec 1995	2024-03-01	4334
Nissan	Vanette	2.0 D	Bus	Heckantrieb	Diesel	47	64	Oct 1986	Dec 1995	2024-03-01	4335
Nissan	Primera	1.6 I	Kombi	Frontantrieb	Benzin	75	102	Feb 1991	Mar 1998	2024-03-01	4337


--- Round 1 / 首次发送 ---
## 更新点

* 完成 29 条 Ktype 映射，闭合 12 个尺寸组，其中新建 11 个、复用既有 `EU-HONDA-PRELUDE-III-COUPE-2D-01` 1 个。
* Prelude III/IV 已按 BA4、BB2、BB3 及对应代际外廓归组。([Auto Data][1])
* Civic III Shuttle 前驱与四驱因长度、高度不同独立建组；Civic IV Shuttle EE4 共用四驱旅行车组。([kmh.lt][2])
* Accord IV 的 Sedan、Coupe、Wagon 已按不同物理车身分别建组。([Auto Data][3])
* Civic V Hatchback、Sedan、Coupe 以及 Concerto Hatch 已分别闭合尺寸组。([Auto Data][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：29
* PENDING 映射：71
* 已确认尺寸组：12
* 本轮首次创建尺寸组：11
* 本轮复用既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4237	4237	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	BA4双门轿跑物理外廓。	READY
4239	4239	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	BA4双门轿跑物理外廓。	READY
4241	4241	Coupe	Prelude IV	BB3	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH	BB3双门轿跑物理外廓。	READY
4242	4242	Coupe	Prelude IV	BB2	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH	BB2双门轿跑与同代BB外廓共组。	READY
4244	4244	Wagon	Civic III Shuttle		5	EU-HONDA-CIVIC-III-SHUTTLE-WAGON-FWD-01	MEDIUM	前驱五门Shuttle外廓。	READY
4247	4247	Wagon	Civic III Shuttle	AR	5	EU-HONDA-CIVIC-III-SHUTTLE-WAGON-4WD-01	HIGH	AR四驱五门Shuttle外廓。	READY
4250	4250	Wagon	Civic IV Shuttle	EE4	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE4四驱五门Shuttle外廓。	READY
4251	4251	Wagon	Civic IV Shuttle	EE4	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE4四驱五门Shuttle外廓。	READY
4252	4252	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4254	4254	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4256	4256	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4257	4257	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4258	4258	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4259	4259	Coupe	Accord IV Coupe	CC1	2	EU-HONDA-ACCORD-IV-COUPE-2D-01	MEDIUM	CC1双门轿跑外廓。	READY
4260	4260	Wagon	Accord IV Wagon	CB8	5	EU-HONDA-ACCORD-IV-WAGON-5D-01	HIGH	CB8五门旅行车外廓。	READY
4261	4261	Wagon	Accord IV Wagon	CB8	5	EU-HONDA-ACCORD-IV-WAGON-5D-01	HIGH	CB8五门旅行车外廓。	READY
4262	4262	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4263	4263	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4265	4265	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4267	4267	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4275	4275	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4276	4276	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4277	4277	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4278	4278	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4279	4279	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4280	4280	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4284	4284	Wagon	Accord IV Wagon		5	EU-HONDA-ACCORD-IV-WAGON-5D-01	MEDIUM	五门旅行车外廓。	READY
4292	4292	Coupe	Civic V Coupe		2	EU-HONDA-CIVIC-V-COUPE-2D-01	HIGH	双门轿跑外廓。	READY
4293	4293	Coupe	Civic V Coupe		2	EU-HONDA-CIVIC-V-COUPE-2D-01	HIGH	双门轿跑外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-PRELUDE-IV-COUPE-2D-01	4440	1765	1290	Auto-Data.net Honda Prelude IV (BB)	https://www.auto-data.net/en/honda-prelude-iv-bb-generation-2615
EU-HONDA-CIVIC-III-SHUTTLE-WAGON-FWD-01	3990	1645	1490	KMH.lt Honda Civic Shuttle 55J catalog	https://www.kmh.lt/automobiliu-techniniai-duomenys/automobilis/6823/civic-shuttle-55j-e-ak
EU-HONDA-CIVIC-III-SHUTTLE-WAGON-4WD-01	4040	1645	1510	Automobile-Catalog 1987 Honda Civic 4WD Wagon	https://www.automobile-catalog.com/car/1987/1421525/honda_civic_4wd_wagon.html
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	4105	1690	1515	Auto-Data.net Honda Civic IV Shuttle	https://www.auto-data.net/en/honda-civic-iv-shuttle-generation-2637
EU-HONDA-ACCORD-IV-SEDAN-4D-01	4685	1695	1390	Auto-Data.net Honda Accord IV (CB3,CB7) 2.0 16V	https://www.auto-data.net/en/honda-accord-iv-cb3-cb7-2.0-16v-90hp-12086
EU-HONDA-ACCORD-IV-COUPE-2D-01	4685	1695	1375	Auto-Data.net Honda Accord IV Coupe (CC1)	https://www.auto-data.net/en/honda-accord-iv-coupe-cc1-2.2-i-16v-150hp-12083
EU-HONDA-ACCORD-IV-WAGON-5D-01	4725	1725	1400	Auto-Data.net Honda Accord IV Wagon (CB8)	https://www.auto-data.net/en/honda-accord-iv-wagon-cb8-2.2-i-16v-150hp-12090
EU-HONDA-CIVIC-V-HATCHBACK-3D-01	4080	1695	1345	Auto-Data.net Honda Civic V Hatchback	https://www.auto-data.net/en/honda-civic-v-hatchback-generation-2634
EU-HONDA-CIVIC-V-SEDAN-4D-01	4405	1695	1375	Auto-Data.net Honda Civic V Sedan	https://www.auto-data.net/en/honda-civic-v-generation-2635
EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	4265	1690	1395	Auto-Data.net Honda Concerto Hatch (HW)	https://www.auto-data.net/en/honda-concerto-hatch-hw-generation-2652
EU-HONDA-CIVIC-V-COUPE-2D-01	4400	1695	1345	Auto-Data.net Honda Civic V Coupe	https://www.auto-data.net/en/honda-civic-v-coupe-generation-2633
```

## 下一步优先处理

1. 按 Laurel C230、C31、C32 代际及改款边界批量闭合 Ktype 4238、4240、4243、4245、4246、4248、4249、4253、4255。
2. 闭合 Primera P10 的 Sedan、Hatchback、Wagon 三类外廓，并批量关联 Ktype 4264、4266、4268—4274、4337。
3. 继续处理 Accord V Sedan/Coupe/Wagon、Civic VI Fastback 与日产 Z 系列尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-prelude-iii-ba-2.0-i-ex-16v-ba4-cat-137hp-12208?utm_source=chatgpt.com "Honda Prelude III (BA) 2.0 i EX 16V (BA4) CAT (137 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.kmh.lt/automobiliu-techniniai-duomenys/automobilis/6823/civic-shuttle-55j-e-ak?utm_source=chatgpt.com "Honda Civic Shuttle 55J {E-AK} (1983)"
[3]: https://www.auto-data.net/en/honda-accord-iv-cb3-cb7-2.0-16v-90hp-12086?utm_source=chatgpt.com "Honda Accord IV (CB3,CB7) 2.0 16V (90 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/honda-civic-v-hatchback-generation-2634?utm_source=chatgpt.com "Honda Civic V Hatchback | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Nissan Laurel C230、C31 两个轿车尺寸组，新增 6 条映射。C230 使用明确标注不含后视镜宽度的欧洲规格；C31 按欧洲 2.4/2.8 D 共用轿车外廓处理。([汽车目录][1])
* 闭合 Nissan Primera 第一代的 P10 Sedan、P10 Hatchback、W10 Wagon 三个尺寸组，新增 10 条映射。([Auto Data][2])
* 闭合 Honda Accord V 的 CC7 Sedan、CD7 Coupe、CE Wagon 三个尺寸组，新增 6 条映射。([Auto Data][3])
* 闭合 Honda Civic V Fastback 与 Civic VI Fastback 两个尺寸组，新增 4 条映射。([Auto Data][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：55
* PENDING 映射：45
* 已确认尺寸组：22
* 本轮新增 READY 映射：26
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4238	4238	Sedan	Laurel III	C230	4	EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	HIGH	C230四门轿车外廓。	READY
4240	4240	Sedan	Laurel III	C230	4	EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	HIGH	C230四门轿车外廓。	READY
4243	4243	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4245	4245	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4246	4246	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4248	4248	Sedan	Laurel IV	JC31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	JC31柴油四门轿车外廓。	READY
4264	4264	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4266	4266	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4268	4268	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4269	4269	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4270	4270	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓。	READY
4271	4271	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓。	READY
4272	4272	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4273	4273	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4274	4274	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4281	4281	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4282	4282	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4283	4283	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4286	4286	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4288	4288	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4289	4289	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4291	4291	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4295	4295	Coupe	Accord V Coupe	CD7	2	EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	HIGH	CD7双门轿跑外廓。	READY
4296	4296	Wagon	Accord V Wagon	CE2	5	EU-HONDA-ACCORD-V-CE-WAGON-5D-01	HIGH	CE2五门旅行车外廓。	READY
4297	4297	Wagon	Accord V Wagon	CE1	5	EU-HONDA-ACCORD-V-CE-WAGON-5D-01	HIGH	CE1五门旅行车外廓。	READY
4337	4337	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	4525	1685	1405	Automobile-Catalog 1977 Nissan Laurel 4Door Sedan 2000 SGL-E	https://www.automobile-catalog.com/car/1977/2120480/nissan_laurel_4door_sedan_2000_sgl-e_5-speed.html
EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	4635	1690	1400	Automobile-Catalog 1984 Nissan Laurel SGL 2.4	https://www.automobile-catalog.com/car/1984/2123675/nissan_laurel_sgl_2_4.html
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390	Auto-Data.net Nissan Primera P10 1.6	https://www.auto-data.net/en/nissan-primera-p10-1.6-90hp-635
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390	Auto-Data.net Nissan Primera Hatch P10 1.6	https://www.auto-data.net/en/nissan-primera-hatch-p10-1.6-90hp-642
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500	Automobile-Catalog 1992 Nissan Primera 2.0 SLX Diesel Traveller	https://www.automobile-catalog.com/car/1992/2263370/nissan_primera_2_0_slx_diesel_traveller.html
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380	Auto-Data.net Honda Accord V CC7 2.0 i	https://www.auto-data.net/en/honda-accord-v-cc7-2.0-i-115hp-12074
EU-HONDA-CIVIC-V-FASTBACK-5D-01	4315	1695	1390	Auto-Data.net Honda Civic V Fastback 1.6i	https://www.auto-data.net/en/honda-civic-v-fastback-1.6i-113hp-12257
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Auto-Data.net Honda Civic VI Fastback 1.4 16V	https://www.auto-data.net/en/honda-civic-vi-fastback-1.4-16v-90hp-12242
EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	4675	1780	1390	Auto-Data.net Honda Accord V Coupe CD7 2.2i ES	https://www.auto-data.net/en/honda-accord-v-coupe-cd7-2.2i-es-150hp-12081
EU-HONDA-ACCORD-V-CE-WAGON-5D-01	4770	1780	1425	Auto-Data.net Honda Accord V Wagon CE 2.0i LS 16V	https://www.auto-data.net/en/honda-accord-v-wagon-ce-2.0i-ls-16v-ce2-136hp-12079
```

## 下一步优先处理

1. 闭合 Laurel C32 欧洲轿车的 2.4 与 2.8 D 高度口径冲突，处理 Ktype 4249、4253、4255。
2. 按 S130、Z31、Z32 分别闭合 Nissan 280ZX、300ZX Targa 与 300ZX Twin Turbo。
3. 批量闭合 Nissan 100NX、Silvia S12、200SX S13 与 Honda NSX I。
4. 随后处理 Serena、Urvan、Terrano、Patrol、Prairie 和 Vanette 等 MPV、Van、SUV 车身簇。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/2120480/nissan_laurel_4door_sedan_2000_sgl-e_5-speed.html?utm_source=chatgpt.com "1977 Nissan Laurel 4Door Sedan 2000 SGL-E 5-speed ..."
[2]: https://www.auto-data.net/en/nissan-primera-p10-1.6-90hp-635?utm_source=chatgpt.com "Nissan Primera (P10) 1.6 (90 Hp) /Sedan 1990"
[3]: https://www.auto-data.net/en/honda-accord-v-cc7-2.0-i-115hp-12074?utm_source=chatgpt.com "Honda Accord V (CC7) 2.0 i (115 Hp) /Sedan 1993"
[4]: https://www.auto-data.net/en/honda-civic-v-fastback-1.6i-113hp-12257?utm_source=chatgpt.com "Honda Civic V Fastback 1.6i (113 Hp)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增 24 条 READY 映射，首次闭合 13 个尺寸组，覆盖 Laurel C32、280ZX/300ZX、100NX、Silvia/200SX、Serena 与 Prairie 车型簇。([Auto Data][1])
* 280ZX 的 `HGS130` 按日产官方 2+2 车身修正为 `4620 × 1690 × 1305 mm`，未采用较短的双座车身尺寸。([日产汽车公司][2])
* NSX I 暂未落盘：输入生产区间横跨多次外廓变化，不能错误地仅按自动挡和手动挡拆组。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：79
* PENDING 映射：21
* 已确认尺寸组：35
* 本轮新增 READY 映射：24
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4249	4249	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4253	4253	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4255	4255	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4285	4285	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4287	4287	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4290	4290	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4294	4294	Targa	300ZX Z31	Z31	2	EU-NISSAN-300ZX-Z31-COUPE-2D-01	HIGH	Z31双门Targa外廓。	READY
4298	4298	Targa	300ZX Z31	Z31	2	EU-NISSAN-300ZX-Z31-COUPE-2D-01	HIGH	Z31双门Targa外廓。	READY
4299	4299	Coupe	300ZX Z32	Z32	2	EU-NISSAN-300ZX-Z32-COUPE-2D-01	HIGH	Z32双门轿跑外廓。	READY
4300	4300	Coupe	300ZX Z32	Z32	2	EU-NISSAN-300ZX-Z32-COUPE-2D-01	HIGH	Z32双门轿跑外廓。	READY
4301	4301	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4302	4302	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4303	4303	Coupe	Silvia S12	S12	2	EU-NISSAN-SILVIA-S12-COUPE-2D-01	HIGH	S12双门轿跑外廓。	READY
4304	4304	Coupe	200SX S13	S13	2	EU-NISSAN-200SX-S13-COUPE-2D-01	HIGH	S13双门轿跑外廓。	READY
4305	4305	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4306	4306	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4307	4307	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-02	HIGH	C23M四门MPV另一高度外廓。	READY
4308	4308	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4311	4311	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4327	4327	MPV	Prairie M10	M10	5	EU-NISSAN-PRAIRIE-M10-MPV-5D-01	HIGH	M10前驱五门MPV外廓。	READY
4328	4328	MPV	Prairie M10	M10	5	EU-NISSAN-PRAIRIE-M10-MPV-5D-01	HIGH	M10前驱五门MPV外廓。	READY
4329	4329	MPV	Prairie M10	NM10	5	EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	HIGH	NM10四驱五门MPV外廓。	READY
4330	4330	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-01	HIGH	M11五门MPV外廓。	READY
4331	4331	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-02	HIGH	M11另一外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	4650	1690	1425	Auto-Data.net Nissan Laurel JC32 2.4;Auto-Data.net Nissan Laurel JC32 2.8 D	https://www.auto-data.net/en/nissan-laurel-jc32-2.4-128hp-automatic-395;https://www.auto-data.net/en/nissan-laurel-jc32-2.8-d-84hp-394
EU-NISSAN-280ZX-S130-COUPE-3D-01	4620	1690	1305	Nissan Heritage Collection Fairlady 280Z-T HGS130	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/fairlady_280z_t.html
EU-NISSAN-300ZX-Z31-COUPE-2D-01	4540	1725	1310	Auto-Data.net Nissan 300 ZX Z31	https://www.auto-data.net/en/nissan-300-zx-z31-generation-155
EU-NISSAN-300ZX-Z32-COUPE-2D-01	4520	1800	1255	Auto-Data.net Nissan 300 ZX Z32	https://www.auto-data.net/en/nissan-300-zx-z32-generation-154
EU-NISSAN-100NX-B13-COUPE-2D-01	4135	1680	1315	Auto-Data.net Nissan 100 NX B13	https://www.auto-data.net/en/nissan-100-nx-b13-generation-78
EU-NISSAN-SILVIA-S12-COUPE-2D-01	4350	1660	1330	Auto-Data.net Nissan Silvia S12 2.0 GP	https://www.auto-data.net/en/nissan-silvia-s12-2.0-gp-145hp-321
EU-NISSAN-200SX-S13-COUPE-2D-01	4535	1690	1290	Auto-Data.net Nissan 200 SX S13 1.8 Turbo	https://www.auto-data.net/en/nissan-200-sx-s13-1.8-turbo-169hp-381
EU-NISSAN-SERENA-C23M-MPV-4D-01	4315	1710	1835	Auto-Data.net Nissan Serena C23M 2.0;Auto-Data.net Nissan Serena C23M 2.3 D	https://www.auto-data.net/en/nissan-serena-c23m-2.0-16v-126hp-937;https://www.auto-data.net/en/nissan-serena-c23m-2.3-d-75hp-941
EU-NISSAN-SERENA-C23M-MPV-4D-02	4315	1710	1840	Auto-Data.net Nissan Serena C23M 1.6 16V	https://www.auto-data.net/en/nissan-serena-c23m-1.6-16v-97hp-936
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650	Auto-Data.net Nissan Prairie M10 1.8 SGL	https://www.auto-data.net/en/nissan-prairie-m10-nm10-1.8-sgl-m10-90hp-413
EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	4230	1665	1685	Auto-Data.net Nissan Prairie NM10 2.0 4X4	https://www.auto-data.net/en/nissan-prairie-m10-nm10-2.0-4x4-nm10-97hp-414
EU-NISSAN-PRAIRIE-M11-MPV-5D-01	4350	1690	1625	Auto-Data.net Nissan Prairie M11 2.0 i	https://www.auto-data.net/en/nissan-prairie-m11-2.0-i-98hp-407
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630	Auto-Data.net Nissan Prairie M11 2.4 i	https://www.auto-data.net/en/nissan-prairie-m11-2.4-i-133hp-409
```

## 下一步优先处理

1. 闭合 Urvan E24 与 Vanette C22/C220 的短轴、长轴及乘用车身边界，处理 Ktype 4312、4313、4332—4335。
2. 拆分 Terrano WD21/R20 的三门、五门物理外廓，处理 Ktype 4314—4317。
3. 闭合 Patrol K160/W160、K260/W260 与 Y60 的 Hardtop、Station Wagon 分支，处理 Ktype 4318—4326。
4. 最后处理 NSX I 跨年份外廓派生分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/nissan-300-zx-z31-generation-155 "Nissan 300 ZX (Z31) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.nissan-global.com/EN/HERITAGE_COLLECTION/fairlady_280z_t.html "Nissan | Heritage Collection | Fairlady 280Z-T"
[3]: https://en.wikipedia.org/wiki/Honda_NSX_%28first_generation%29?utm_source=chatgpt.com "Honda NSX (first generation)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成剩余 NSX I、Urvan E24、Terrano WD21/R20、Patrol 160/260/Y60 和 Vanette C120/C22 车型簇。
* `4309` 按 2002 年改款前后拆分；Terrano 与 Patrol 按三门/五门、Hardtop/Station Wagon 分支拆分。
* 最后一项 Vanette 1.5 欧洲 C120 已闭合为 `3965 × 1690 × 1930 mm`，宽度为不含后视镜口径。([汽车目录][1])
* 最终机械检查通过：表头固定、106 个 `id` 唯一、49 个尺寸组唯一、全部引用闭合、无孤立组、尺寸和来源均完整。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：106
* PENDING 映射：0
* 已确认尺寸组：49
* 映射覆盖 Ktype：100/100
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4237	4237	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	BA4双门轿跑物理外廓。	READY
4238	4238	Sedan	Laurel III	C230	4	EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	HIGH	C230四门轿车外廓。	READY
4239	4239	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	BA4双门轿跑物理外廓。	READY
4240	4240	Sedan	Laurel III	C230	4	EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	HIGH	C230四门轿车外廓。	READY
4241	4241	Coupe	Prelude IV	BB3	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH	BB3双门轿跑物理外廓。	READY
4242	4242	Coupe	Prelude IV	BB2	2	EU-HONDA-PRELUDE-IV-COUPE-2D-01	HIGH	BB2双门轿跑与同代BB外廓共组。	READY
4243	4243	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4244	4244	Wagon	Civic III Shuttle		5	EU-HONDA-CIVIC-III-SHUTTLE-WAGON-FWD-01	MEDIUM	前驱五门Shuttle外廓。	READY
4245	4245	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4246	4246	Sedan	Laurel IV	C31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	C31四门轿车外廓。	READY
4247	4247	Wagon	Civic III Shuttle	AR	5	EU-HONDA-CIVIC-III-SHUTTLE-WAGON-4WD-01	HIGH	AR四驱五门Shuttle外廓。	READY
4248	4248	Sedan	Laurel IV	JC31	4	EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	HIGH	JC31柴油四门轿车外廓。	READY
4249	4249	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4250	4250	Wagon	Civic IV Shuttle	EE4	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE4四驱五门Shuttle外廓。	READY
4251	4251	Wagon	Civic IV Shuttle	EE4	5	EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	HIGH	EE4四驱五门Shuttle外廓。	READY
4252	4252	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4253	4253	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4254	4254	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4255	4255	Sedan	Laurel V	JC32	4	EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	HIGH	JC32四门轿车外廓。	READY
4256	4256	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4257	4257	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4258	4258	Sedan	Accord IV		4	EU-HONDA-ACCORD-IV-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4259	4259	Coupe	Accord IV Coupe	CC1	2	EU-HONDA-ACCORD-IV-COUPE-2D-01	MEDIUM	CC1双门轿跑外廓。	READY
4260	4260	Wagon	Accord IV Wagon	CB8	5	EU-HONDA-ACCORD-IV-WAGON-5D-01	HIGH	CB8五门旅行车外廓。	READY
4261	4261	Wagon	Accord IV Wagon	CB8	5	EU-HONDA-ACCORD-IV-WAGON-5D-01	HIGH	CB8五门旅行车外廓。	READY
4262	4262	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4263	4263	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4264	4264	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4265	4265	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4266	4266	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4267	4267	Hatchback	Civic V Hatchback		3	EU-HONDA-CIVIC-V-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
4268	4268	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4269	4269	Sedan	Primera I	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车外廓。	READY
4270	4270	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓。	READY
4271	4271	Hatchback	Primera I	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背外廓。	READY
4272	4272	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4273	4273	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4274	4274	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
4275	4275	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4276	4276	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4277	4277	Sedan	Civic V		4	EU-HONDA-CIVIC-V-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
4278	4278	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4279	4279	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4280	4280	Hatchback	Concerto Hatch	HW	5	EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	HIGH	HW五门掀背外廓。	READY
4281	4281	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4282	4282	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4283	4283	Sedan	Accord V	CC7	4	EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	HIGH	CC7四门轿车外廓。	READY
4284	4284	Wagon	Accord IV Wagon		5	EU-HONDA-ACCORD-IV-WAGON-5D-01	MEDIUM	五门旅行车外廓。	READY
4285	4285	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4286	4286	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4287	4287	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4288	4288	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4289	4289	Hatchback	Civic V Fastback		5	EU-HONDA-CIVIC-V-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4290	4290	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-3D-01	HIGH	HGS130三门2+2轿跑外廓。	READY
4291	4291	Hatchback	Civic VI Fastback		5	EU-HONDA-CIVIC-VI-FASTBACK-5D-01	HIGH	五门Fastback外廓。	READY
4292	4292	Coupe	Civic V Coupe		2	EU-HONDA-CIVIC-V-COUPE-2D-01	HIGH	双门轿跑外廓。	READY
4293	4293	Coupe	Civic V Coupe		2	EU-HONDA-CIVIC-V-COUPE-2D-01	HIGH	双门轿跑外廓。	READY
4294	4294	Targa	300ZX Z31	Z31	2	EU-NISSAN-300ZX-Z31-COUPE-2D-01	HIGH	Z31双门Targa外廓。	READY
4295	4295	Coupe	Accord V Coupe	CD7	2	EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	HIGH	CD7双门轿跑外廓。	READY
4296	4296	Wagon	Accord V Wagon	CE2	5	EU-HONDA-ACCORD-V-CE-WAGON-5D-01	HIGH	CE2五门旅行车外廓。	READY
4297	4297	Wagon	Accord V Wagon	CE1	5	EU-HONDA-ACCORD-V-CE-WAGON-5D-01	HIGH	CE1五门旅行车外廓。	READY
4298	4298	Targa	300ZX Z31	Z31	2	EU-NISSAN-300ZX-Z31-COUPE-2D-01	HIGH	Z31双门Targa外廓。	READY
4299	4299	Coupe	300ZX Z32	Z32	2	EU-NISSAN-300ZX-Z32-COUPE-2D-01	HIGH	Z32双门轿跑外廓。	READY
4300	4300	Coupe	300ZX Z32	Z32	2	EU-NISSAN-300ZX-Z32-COUPE-2D-01	HIGH	Z32双门轿跑外廓。	READY
4301	4301	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4302	4302	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4303	4303	Coupe	Silvia S12	S12	2	EU-NISSAN-SILVIA-S12-COUPE-2D-01	HIGH	S12双门轿跑外廓。	READY
4304	4304	Coupe	200SX S13	S13	2	EU-NISSAN-200SX-S13-COUPE-2D-01	HIGH	S13双门轿跑外廓。	READY
4305	4305	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4306	4306	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4307	4307	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-02	HIGH	C23M四门MPV另一高度外廓。	READY
4308	4308	MPV	Serena C23M	C23M	4	EU-NISSAN-SERENA-C23M-MPV-4D-01	HIGH	C23M四门MPV标准外廓。	READY
4309_prefl	4309	Coupe	NSX I pre-facelift	NA1	2	EU-HONDA-NSX-I-NA1-COUPE-2D-PREFL-01	HIGH	NA1自动挡，2002改款前外廓。	READY
4309_facelift	4309	Coupe	NSX I facelift 2002	NA1	2	EU-HONDA-NSX-I-NA1-COUPE-2D-FACELIFT-01	HIGH	NA1 F-matic，2002改款后外廓。	READY
4310	4310	Coupe	NSX I pre-facelift	NA1	2	EU-HONDA-NSX-I-NA1-COUPE-2D-PREFL-01	HIGH	NA1 3.0手动挡命中改款前外廓。	READY
4311	4311	Coupe	100NX B13	B13	2	EU-NISSAN-100NX-B13-COUPE-2D-01	HIGH	B13双门轿跑外廓。	READY
4312	4312	MPV	Urvan III	E24	4	EU-NISSAN-URVAN-E24-MPV-4D-01	MEDIUM	E24四门乘用Bus外廓。	READY
4313	4313	MPV	Urvan III	E24	4	EU-NISSAN-URVAN-E24-MPV-4D-01	MEDIUM	E24四门乘用Bus外廓。	READY
4314_3dr	4314	SUV	Terrano II	R20	3	EU-NISSAN-TERRANO-II-R20-SUV-3D-01	HIGH	R20三门短车身外廓。	READY
4314_5dr	4314	SUV	Terrano II	R20	5	EU-NISSAN-TERRANO-II-R20-SUV-5D-01	HIGH	R20五门长车身外廓。	READY
4315_3dr	4315	SUV	Terrano II	R20	3	EU-NISSAN-TERRANO-II-R20-SUV-3D-01	HIGH	R20三门短车身外廓。	READY
4315_5dr	4315	SUV	Terrano II	R20	5	EU-NISSAN-TERRANO-II-R20-SUV-5D-01	HIGH	R20五门长车身外廓。	READY
4316_3dr	4316	SUV	Terrano I	WD21	3	EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	MEDIUM	WD21三门物理分支。	READY
4316_5dr	4316	SUV	Terrano I	WD21	5	EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	MEDIUM	WD21五门物理分支。	READY
4317_3dr	4317	SUV	Terrano I	WD21	3	EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	MEDIUM	WD21三门物理分支。	READY
4317_5dr	4317	SUV	Terrano I	WD21	5	EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	MEDIUM	WD21五门物理分支。	READY
4318	4318	SUV	Patrol III/1	W160	5	EU-NISSAN-PATROL-III-W160-SUV-5D-01	HIGH	W160五门Station Wagon外廓。	READY
4319	4319	SUV	Patrol III/1	K160	3	EU-NISSAN-PATROL-III-K160-SUV-3D-01	HIGH	K160三门Hardtop外廓。	READY
4320	4320	SUV	Patrol III/1	K160	3	EU-NISSAN-PATROL-III-K160-SUV-3D-01	HIGH	K160三门Hardtop外廓。	READY
4321	4321	SUV	Patrol III/1	W160	5	EU-NISSAN-PATROL-III-W160-SUV-5D-01	HIGH	W160五门Station Wagon外廓。	READY
4322	4322	SUV	Patrol III/1	K160	3	EU-NISSAN-PATROL-III-K160-SUV-3D-01	HIGH	K160三门Hardtop外廓。	READY
4323	4323	SUV	Patrol III/1	W160	5	EU-NISSAN-PATROL-III-W160-SUV-5D-01	HIGH	W160五门Station Wagon外廓。	READY
4324	4324	SUV	Patrol III/1	K160	3	EU-NISSAN-PATROL-III-K160-SUV-3D-01	HIGH	K160三门Hardtop外廓。	READY
4325	4325	SUV	Patrol III/2	W260	5	EU-NISSAN-PATROL-III-W260-SUV-5D-01	MEDIUM	W260五门Station Wagon外廓。	READY
4326_3dr	4326	SUV	Patrol IV GR	Y60	3	EU-NISSAN-PATROL-IV-Y60-SUV-3D-01	HIGH	Y60三门Hardtop物理分支。	READY
4326_5dr	4326	SUV	Patrol IV GR	Y60	5	EU-NISSAN-PATROL-IV-Y60-SUV-5D-01	HIGH	Y60五门Station Wagon物理分支。	READY
4327	4327	MPV	Prairie M10	M10	5	EU-NISSAN-PRAIRIE-M10-MPV-5D-01	HIGH	M10前驱五门MPV外廓。	READY
4328	4328	MPV	Prairie M10	M10	5	EU-NISSAN-PRAIRIE-M10-MPV-5D-01	HIGH	M10前驱五门MPV外廓。	READY
4329	4329	MPV	Prairie M10	NM10	5	EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	HIGH	NM10四驱五门MPV外廓。	READY
4330	4330	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-01	HIGH	M11五门MPV外廓。	READY
4331	4331	MPV	Prairie M11	M11	5	EU-NISSAN-PRAIRIE-M11-MPV-5D-02	HIGH	M11另一外廓分支。	READY
4332	4332	MPV	Vanette I	C120	4	EU-NISSAN-VANETTE-C120-MPV-4D-01	HIGH	欧洲C120四门1.5乘用车外廓。	READY
4333	4333	MPV	Vanette II	C22	4	EU-NISSAN-VANETTE-C22-MPV-4D-01	HIGH	C22四门乘用车外廓。	READY
4334	4334	MPV	Vanette II	C22	4	EU-NISSAN-VANETTE-C22-MPV-4D-01	HIGH	C22四门乘用车外廓。	READY
4335	4335	MPV	Vanette II	C22	4	EU-NISSAN-VANETTE-C22-MPV-4D-01	HIGH	C22四门乘用车外廓。	READY
4337	4337	Wagon	Primera I	W10	5	EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	HIGH	W10五门旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4101-4200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295	Auto-Data.net Honda Prelude III (BA)	https://www.auto-data.net/en/honda-prelude-iii-ba-generation-2616
EU-NISSAN-LAUREL-III-C230-SEDAN-4D-01	4525	1685	1405	Automobile-Catalog 1977 Nissan Laurel 4Door Sedan 2000 SGL-E	https://www.automobile-catalog.com/car/1977/2120480/nissan_laurel_4door_sedan_2000_sgl-e_5-speed.html
EU-HONDA-PRELUDE-IV-COUPE-2D-01	4440	1765	1290	Auto-Data.net Honda Prelude IV (BB)	https://www.auto-data.net/en/honda-prelude-iv-bb-generation-2615
EU-NISSAN-LAUREL-IV-C31-SEDAN-4D-01	4635	1690	1400	Automobile-Catalog 1984 Nissan Laurel SGL 2.4	https://www.automobile-catalog.com/car/1984/2123675/nissan_laurel_sgl_2_4.html
EU-HONDA-CIVIC-III-SHUTTLE-WAGON-FWD-01	3990	1645	1490	KMH.lt Honda Civic Shuttle 55J catalog	https://www.kmh.lt/automobiliu-techniniai-duomenys/automobilis/6823/civic-shuttle-55j-e-ak
EU-HONDA-CIVIC-III-SHUTTLE-WAGON-4WD-01	4040	1645	1510	Automobile-Catalog 1987 Honda Civic 4WD Wagon	https://www.automobile-catalog.com/car/1987/1421525/honda_civic_4wd_wagon.html
EU-NISSAN-LAUREL-V-C32-SEDAN-4D-01	4650	1690	1425	Auto-Data.net Nissan Laurel JC32 2.4;Auto-Data.net Nissan Laurel JC32 2.8 D	https://www.auto-data.net/en/nissan-laurel-jc32-2.4-128hp-automatic-395;https://www.auto-data.net/en/nissan-laurel-jc32-2.8-d-84hp-394
EU-HONDA-CIVIC-IV-SHUTTLE-WAGON-4WD-01	4105	1690	1515	Auto-Data.net Honda Civic IV Shuttle	https://www.auto-data.net/en/honda-civic-iv-shuttle-generation-2637
EU-HONDA-ACCORD-IV-SEDAN-4D-01	4685	1695	1390	Auto-Data.net Honda Accord IV (CB3,CB7) 2.0 16V	https://www.auto-data.net/en/honda-accord-iv-cb3-cb7-2.0-16v-90hp-12086
EU-HONDA-ACCORD-IV-COUPE-2D-01	4685	1695	1375	Auto-Data.net Honda Accord IV Coupe (CC1)	https://www.auto-data.net/en/honda-accord-iv-coupe-cc1-2.2-i-16v-150hp-12083
EU-HONDA-ACCORD-IV-WAGON-5D-01	4725	1725	1400	Auto-Data.net Honda Accord IV Wagon (CB8)	https://www.auto-data.net/en/honda-accord-iv-wagon-cb8-2.2-i-16v-150hp-12090
EU-HONDA-CIVIC-V-HATCHBACK-3D-01	4080	1695	1345	Auto-Data.net Honda Civic V Hatchback	https://www.auto-data.net/en/honda-civic-v-hatchback-generation-2634
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390	Auto-Data.net Nissan Primera P10 1.6	https://www.auto-data.net/en/nissan-primera-p10-1.6-90hp-635
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390	Auto-Data.net Nissan Primera Hatch P10 1.6	https://www.auto-data.net/en/nissan-primera-hatch-p10-1.6-90hp-642
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500	Automobile-Catalog 1992 Nissan Primera 2.0 SLX Diesel Traveller	https://www.automobile-catalog.com/car/1992/2263370/nissan_primera_2_0_slx_diesel_traveller.html
EU-HONDA-CIVIC-V-SEDAN-4D-01	4405	1695	1375	Auto-Data.net Honda Civic V Sedan	https://www.auto-data.net/en/honda-civic-v-generation-2635
EU-HONDA-CONCERTO-HW-HATCHBACK-5D-01	4265	1690	1395	Auto-Data.net Honda Concerto Hatch (HW)	https://www.auto-data.net/en/honda-concerto-hatch-hw-generation-2652
EU-HONDA-ACCORD-V-CC7-SEDAN-4D-01	4675	1715	1380	Auto-Data.net Honda Accord V CC7 2.0 i	https://www.auto-data.net/en/honda-accord-v-cc7-2.0-i-115hp-12074
EU-NISSAN-280ZX-S130-COUPE-3D-01	4620	1690	1305	Nissan Heritage Collection Fairlady 280Z-T HGS130	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/fairlady_280z_t.html
EU-HONDA-CIVIC-V-FASTBACK-5D-01	4315	1695	1390	Auto-Data.net Honda Civic V Fastback 1.6i	https://www.auto-data.net/en/honda-civic-v-fastback-1.6i-113hp-12257
EU-HONDA-CIVIC-VI-FASTBACK-5D-01	4325	1695	1390	Auto-Data.net Honda Civic VI Fastback 1.4 16V	https://www.auto-data.net/en/honda-civic-vi-fastback-1.4-16v-90hp-12242
EU-HONDA-CIVIC-V-COUPE-2D-01	4400	1695	1345	Auto-Data.net Honda Civic V Coupe	https://www.auto-data.net/en/honda-civic-v-coupe-generation-2633
EU-NISSAN-300ZX-Z31-COUPE-2D-01	4540	1725	1310	Auto-Data.net Nissan 300 ZX Z31	https://www.auto-data.net/en/nissan-300-zx-z31-generation-155
EU-HONDA-ACCORD-V-CD7-COUPE-2D-01	4675	1780	1390	Auto-Data.net Honda Accord V Coupe CD7 2.2i ES	https://www.auto-data.net/en/honda-accord-v-coupe-cd7-2.2i-es-150hp-12081
EU-HONDA-ACCORD-V-CE-WAGON-5D-01	4770	1780	1425	Auto-Data.net Honda Accord V Wagon CE 2.0i LS 16V	https://www.auto-data.net/en/honda-accord-v-wagon-ce-2.0i-ls-16v-ce2-136hp-12079
EU-NISSAN-300ZX-Z32-COUPE-2D-01	4520	1800	1255	Auto-Data.net Nissan 300 ZX Z32	https://www.auto-data.net/en/nissan-300-zx-z32-generation-154
EU-NISSAN-100NX-B13-COUPE-2D-01	4135	1680	1315	Auto-Data.net Nissan 100 NX B13	https://www.auto-data.net/en/nissan-100-nx-b13-generation-78
EU-NISSAN-SILVIA-S12-COUPE-2D-01	4350	1660	1330	Auto-Data.net Nissan Silvia S12 2.0 GP	https://www.auto-data.net/en/nissan-silvia-s12-2.0-gp-145hp-321
EU-NISSAN-200SX-S13-COUPE-2D-01	4535	1690	1290	Auto-Data.net Nissan 200 SX S13 1.8 Turbo	https://www.auto-data.net/en/nissan-200-sx-s13-1.8-turbo-169hp-381
EU-NISSAN-SERENA-C23M-MPV-4D-01	4315	1710	1835	Auto-Data.net Nissan Serena C23M 2.0;Auto-Data.net Nissan Serena C23M 2.3 D	https://www.auto-data.net/en/nissan-serena-c23m-2.0-16v-126hp-937;https://www.auto-data.net/en/nissan-serena-c23m-2.3-d-75hp-941
EU-NISSAN-SERENA-C23M-MPV-4D-02	4315	1710	1840	Auto-Data.net Nissan Serena C23M 1.6 16V	https://www.auto-data.net/en/nissan-serena-c23m-1.6-16v-97hp-936
EU-HONDA-NSX-I-NA1-COUPE-2D-PREFL-01	4430	1810	1170	Honda NSX 1990 official specifications;Honda NSX 2001 official archive	https://www.honda.co.jp/factbook/auto/NSX/19900913/ns90-036.html;https://www.honda.co.jp/auto-archive/nsx/2001/shogen-nsx99.html
EU-HONDA-NSX-I-NA1-COUPE-2D-FACELIFT-01	4425	1810	1170	Auto-Data.net Honda NSX I Coupe facelift 2002 3.0 F-matic	https://www.auto-data.net/en/honda-nsx-i-coupe-facelift-2002-3.0-v6-vtec-256hp-f-matic-42232
EU-NISSAN-URVAN-E24-MPV-4D-01	4690	1690	1965	Drive.Place Nissan Urvan III E24 2.4;Drive.Place Nissan Urvan III E24 2.5 D	https://nissan.drive.place/urvan/iii/group_furgon/600589;https://nissan.drive.place/urvan/iii/group_furgon/600602
EU-NISSAN-TERRANO-II-R20-SUV-3D-01	4105	1735	1805	Auto-Data.net Terrano II R20 2.7 TD 3-dr;Auto-Data.net Terrano II R20 2.4 i 12V 3-dr	https://www.auto-data.net/en/nissan-terrano-ii-r20-2.7-td-3-dr-100hp-657;https://www.auto-data.net/en/nissan-terrano-ii-r20-2.4-i-12v-4wd-3-dr-124hp-653
EU-NISSAN-TERRANO-II-R20-SUV-5D-01	4585	1735	1810	Auto-Data.net Terrano II R20 2.7 TD 5-dr;Auto-Data.net Terrano II R20 2.4 i 12V 5-dr	https://www.auto-data.net/en/nissan-terrano-ii-r20-2.7-td-5-dr-100hp-658;https://www.auto-data.net/en/nissan-terrano-ii-r20-2.4-i-12v-4wd-5-dr-124hp-654
EU-NISSAN-TERRANO-I-WD21-SUV-3D-01	4365	1690	1680	Auto-Data.net Nissan Terrano I WD21 2.4 i;Auto-Data.net Nissan Terrano I WD21 2.7 TD	https://www.auto-data.net/en/nissan-terrano-i-wd21-2.4-i-4wd-103hp-661;https://www.auto-data.net/en/nissan-terrano-i-wd21-2.7-td-4wd-99hp-662
EU-NISSAN-TERRANO-I-WD21-SUV-5D-01	4365	1690	1680	Auto-Data.net Nissan Terrano I WD21 2.4 i;Auto-Data.net Nissan Terrano I WD21 2.7 TD	https://www.auto-data.net/en/nissan-terrano-i-wd21-2.4-i-4wd-103hp-661;https://www.auto-data.net/en/nissan-terrano-i-wd21-2.7-td-4wd-99hp-662
EU-NISSAN-PATROL-III-W160-SUV-5D-01	4720	1690	1800	UltimateSpecs Nissan Patrol K160 Wagon 2.8;UltimateSpecs Nissan Patrol K160 Wagon 3.3 D	https://www.ultimatespecs.com/car-specs/Nissan/6740/Nissan-Patrol-K160-Wagon-28.html;https://www.ultimatespecs.com/car-specs/Nissan/6739/Nissan-Patrol-K160-Wagon-33-D.html
EU-NISSAN-PATROL-III-K160-SUV-3D-01	4110	1690	1840	UltimateSpecs Nissan Patrol K160 HardTop 2.8;UltimateSpecs Nissan Patrol K160 HardTop 3.3 D	https://www.ultimatespecs.com/car-specs/Nissan/6743/Nissan-Patrol-K160-HardTop-28.html;https://www.ultimatespecs.com/car-specs/Nissan/6742/Nissan-Patrol-K160-HardTop-33-D.html
EU-NISSAN-PATROL-III-W260-SUV-5D-01	4770	1690	1805	Auto-Data.net Patrol Station Wagon W260;Nissan Patrol 260-series specification summary	https://www.auto-data.net/en/nissan-patrol-station-wagon-w260-generation-84;https://en.wikipedia.org/wiki/Nissan_Patrol
EU-NISSAN-PATROL-IV-Y60-SUV-3D-01	4250	1800	1800	UltimateSpecs Nissan Patrol GR Y60 HardTop 2.8 Turbo D	https://www.ultimatespecs.com/car-specs/Nissan/6745/Nissan-Patrol-GR-%28Y60%29-HardTop-28-Turbo-D.html
EU-NISSAN-PATROL-IV-Y60-SUV-5D-01	4920	1930	1790	Auto-Data.net Nissan Patrol IV 5-door Y60	https://www.auto-data.net/en/nissan-patrol-iv-5-door-y60-generation-8355
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650	Auto-Data.net Nissan Prairie M10 1.8 SGL	https://www.auto-data.net/en/nissan-prairie-m10-nm10-1.8-sgl-m10-90hp-413
EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	4230	1665	1685	Auto-Data.net Nissan Prairie NM10 2.0 4X4	https://www.auto-data.net/en/nissan-prairie-m10-nm10-2.0-4x4-nm10-97hp-414
EU-NISSAN-PRAIRIE-M11-MPV-5D-01	4350	1690	1625	Auto-Data.net Nissan Prairie M11 2.0 i	https://www.auto-data.net/en/nissan-prairie-m11-2.0-i-98hp-407
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630	Auto-Data.net Nissan Prairie M11 2.4 i	https://www.auto-data.net/en/nissan-prairie-m11-2.4-i-133hp-409
EU-NISSAN-VANETTE-C120-MPV-4D-01	3965	1690	1930	Automobile-Catalog 1984 Nissan Vanette 1.5 Europe	https://www.automobile-catalog.com/car/1984/48710/nissan_vanette_1_5.html
EU-NISSAN-VANETTE-C22-MPV-4D-01	4365	1690	1900	Auto-Data.net Nissan Vanette generation;Auto-Data.net Nissan Vanette 2.4 i	https://www.auto-data.net/en/nissan-vanette-generation-231;https://www.auto-data.net/en/nissan-vanette-2.4-i-105hp-795
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4101-4200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1984/48710/nissan_vanette_1_5.html "https://www.automobile-catalog.com/car/1984/48710/nissan_vanette_1_5.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4101-4200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4101-4200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5537 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1668 行）

