# 任务：all 第 401-500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0005__500a7e64


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 401-500 行

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
all 第 401-500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1467
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1479
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4784	1897	1344
EU-CHEVROLET-CAMARO-VI-COUPE-01	4784	1880	1340
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L1H2-01	4963	2050	2522
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-II-FACELIFT-VAN-L4H3-01	6363	2050	2760
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
KIA	Soul ii	1.6 Cvvt	Schrägheck	Frontantrieb	Benzin	91	124	Feb 2014	Dec 2018	2024-03-01	120778
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	110	150	May 2016	Aug 2024	2025-02-03	120779
Subaru	Forester	2.5 AWD	SUV	Allrad	Benzin	126	171	Nov 2012	-	2024-03-01	120784
Tesla	Model s	60D AWD	Schrägheck	Allrad	Elektro	386	525	Oct 2014	Apr 2026	2026-06-01	120799
Tesla	Model s	60	Schrägheck	Heckantrieb	Elektro	285	388	Nov 2013	Apr 2026	2026-06-01	120800
VW	Multivan t6	2.0 TDI	Bus	Frontantrieb	Diesel	84	114	May 2016	Aug 2019	2024-03-01	120803
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	84	114	May 2016	Aug 2019	2024-03-01	120808
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	84	114	May 2016	Aug 2019	2024-03-01	120813
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	May 2016	Nov 2019	2024-03-01	120815
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	150	204	May 2016	Aug 2024	2025-02-03	120822
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	150	204	May 2016	Aug 2024	2025-02-03	120823
KIA	Optima	2.0 T-gdi	Stufenheck	Frontantrieb	Benzin	180	245	Sep 2015	Dec 2019	2024-03-01	120842
KIA	Niro i	1.6 GDI Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	104	141	Sep 2016	Aug 2022	2024-03-01	120843
Peugeot	Boxer	2.0 Bluehdi 110	Pritsche/Fahrgestell	Frontantrieb	Diesel	81	110	Mar 2016	Sep 2019	2025-02-03	120845
Peugeot	Boxer	2.0 Bluehdi 130	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	130	Mar 2016	Sep 2019	2025-02-03	120846
Peugeot	Boxer	2.0 Bluehdi 160	Pritsche/Fahrgestell	Frontantrieb	Diesel	120	163	Mar 2016	Dec 2023	2025-02-03	120847
Ford	Mondeo iv	1.6 Ecoboost	Stufenheck	Frontantrieb	Benzin	118	160	Nov 2010	Jan 2015	2024-03-01	120851
Subaru	Legacy vi	3.6 I AWD	Stufenheck	Allrad	Benzin	191	260	Jan 2015	-	2024-03-01	120853
Dongfeng Xiaokang	K02	1	Pritsche/Fahrgestell	Heckantrieb	Benzin	39	53	Jan 2008	-	2024-03-01	120880
VW	Passat alltrack b8 variant	1.4 TSI 4motion	Kombi	Allrad	Benzin	110	150	May 2015	Nov 2018	2025-02-03	120892
Audi	A4 b9	S4 Tfsi Quattro	Stufenheck	Allrad	Benzin	260	354	May 2016	-	2025-06-01	120900
Audi	A4 b9 avant	S4 Tfsi Quattro	Kombi	Allrad	Benzin	260	354	May 2016	-	2025-11-01	120901
Bugatti	Chiron	8.0 W16	Coupe	Allrad	Benzin	1103	1500	Apr 2016	-	2024-03-01	120920
Citroën	E-Mehari	Electric	Cabriolet	Frontantrieb	Elektro	50	68	Jun 2016	-	2024-03-01	121049
Hyundai	I20 ii	1.2	Coupe	Frontantrieb	Benzin	62	84	May 2015	Sep 2021	2025-06-01	121091
Hyundai	I20 ii	1.1 Crdi	Coupe	Frontantrieb	Diesel	55	75	May 2015	Sep 2021	2025-06-01	121094
BMW	3	323 I	Cabriolet	Heckantrieb	Benzin	140	190	Mar 2007	Sep 2011	2024-03-01	121100
BMW	3	335 I	Cabriolet	Heckantrieb	Benzin	240	326	May 2006	Oct 2013	2024-03-01	121102
Hyundai	Creta	2	SUV	Frontantrieb	Benzin	110	150	Jan 2016	Jan 2021	2024-03-01	121109
Alfa Romeo	Giulia	2	Stufenheck	Heckantrieb	Benzin	206	280	Aug 2016	-	2024-03-01	121146
Peugeot	3008 ii	2.0 Bluehdi 180	SUV	Frontantrieb	Diesel	133	181	May 2016	-	2024-11-01	121173
VW	Polo	1	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Jan 2014	Oct 2017	2024-03-01	121176
VW	Polo	1	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Jan 2014	Oct 2017	2024-03-01	121177
VW	Polo	1.0 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	70	95	Nov 2014	Oct 2017	2024-03-01	121180
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	66	90	Feb 2014	Oct 2017	2025-06-01	121181
VW	Polo	1.2 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	81	110	Jan 2014	Oct 2017	2024-03-01	121182
VW	Polo	1.4 TSI	Kasten/Schrägheck	Frontantrieb	Benzin	110	150	May 2014	Oct 2017	2024-03-01	121183
VW	Polo	1.4 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Mar 2014	Oct 2017	2024-03-01	121186
VW	Polo	1.4 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Feb 2014	Oct 2017	2024-03-01	121188
Cadillac	Ct6	3.0 Turbo AWD	Stufenheck	Allrad	Benzin	307	418	Jan 2016	Dec 2019	2024-03-01	121201
Toyota	C-Hr	1.2	SUV	Frontantrieb	Benzin	85	116	Oct 2016	-	2024-03-01	121220
Ford	Transit connect v408	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Aug 2015	-	2024-03-01	121226
Spyker	C8	4.2 Preliator	Coupe	Heckantrieb	Benzin	386	525	Mar 2016	-	2024-03-01	121228
Suzuki	Vitara	1.6 Allgrip	SUV	Allrad	Benzin	86	117	May 2015	-	2024-03-01	121230
Abarth	500c / 595c 695c	1.4	Cabriolet	Frontantrieb	Benzin	121	165	May 2016	-	2024-03-01	121235
Ford	Focus iii	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	74	100	Feb 2012	Dec 2017	2024-03-01	121236
Ford	Focus iii	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	92	125	Feb 2012	Dec 2017	2024-03-01	121237
Ford	Focus iii	1.5 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	110	150	Sep 2014	Dec 2017	2024-03-01	121238
Ford	Focus iii	1.5 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	134	182	Sep 2014	Dec 2017	2024-03-01	121239
Ford	Focus iii	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	70	95	Sep 2014	Dec 2017	2024-03-01	121240
Ford	Focus iii	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	88	120	Sep 2014	Dec 2017	2024-03-01	121242
Ford	Focus iii	2.0 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	110	150	Nov 2014	Dec 2017	2024-03-01	121243
Honda	Civic ix	1.6	Stufenheck	Frontantrieb	Benzin	92	125	Sep 2011	Dec 2016	2024-03-01	121249
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	96	131	Jan 1971	Dec 1977	2024-03-01	121297
Aston Martin	Vantage	4.3 N400	Coupe	Heckantrieb	Benzin	298	405	Jan 2008	Dec 2010	2024-03-01	121304
BMW	3	316 I Baur TC	Cabriolet	Heckantrieb	Benzin	73	99	Sep 1987	Dec 1989	2024-03-01	121337
Audi	A5	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	185	252	Jun 2016	-	2024-03-01	121416
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	130	177	Feb 2016	Apr 2025	2026-01-01	121440
Fiat	Tipo	1.4 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	88	120	May 2016	Oct 2020	2024-03-01	121442
Fiat	500	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	57	78	Jun 2016	-	2024-03-01	121445
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	120	163	Jun 2016	-	2024-03-01	121446
Chevrolet	Silverado 2500	6.6 D	Pick-up	Heckantrieb	Diesel	224	305	Oct 2001	Aug 2006	2024-03-01	121480
Chevrolet	Silverado 2500	6.6 D AWD	Pick-up	Allrad	Diesel	224	305	Oct 2001	Aug 2006	2024-03-01	121481
Audi	A5	S5 Tfsi Quattro	Coupe	Allrad	Benzin	260	354	Jul 2016	-	2025-11-01	121493
Audi	A5	2.0 TDI	Coupe	Frontantrieb	Diesel	140	190	Jul 2016	Feb 2020	2026-07-01	121494
Audi	A5	3.0 TDI Quattro	Coupe	Allrad	Diesel	160	218	Jul 2016	Aug 2018	2024-03-01	121495
Chevrolet	Avalanche	5.3 Flexfuel AWD	Pick-up	Allrad	Benzin/Ethanol	235	320	Sep 2006	Dec 2007	2024-03-01	121496
Ford	Courier	1.6	Pick-up	Frontantrieb	Benzin	74	101	Aug 2001	Dec 2011	2024-03-01	121499
Renault	Twizy	80	Schrägheck	Heckantrieb	Elektro	8	11	Apr 2012	-	2024-03-01	121500
Jeep	Cherokee	2.5 4X4	Geländewagen geschlossen	Allrad	Benzin	89	121	Oct 1990	Sep 1996	2024-03-01	121502
Smart	Fortwo cabrio	0.6	Cabriolet	Heckantrieb	Benzin	45	61	Jan 2004	Dec 2006	2024-03-01	121536
Seat	Altea	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	155	211	May 2009	Jul 2015	2024-05-01	121578
Suzuki	Sx4 s-Cross	1.4 T	Schrägheck	Frontantrieb	Benzin	103	140	Aug 2016	Jun 2022	2025-06-01	121586
Suzuki	Sx4 s-Cross	1.4 T Allgrip	Schrägheck	Allrad	Benzin	103	140	Aug 2016	Jun 2022	2025-06-01	121587
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	213	290	Jul 2016	Dec 2017	2024-03-01	121601
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	213	290	Jul 2016	Oct 2020	2024-03-01	121603
Audi	A3	S3 Quattro	Stufenheck	Allrad	Benzin	213	290	Aug 2016	Oct 2020	2024-03-01	121604
Audi	A3	S3 Quattro	Cabriolet	Allrad	Benzin	213	290	Jul 2016	Oct 2020	2024-03-01	121605
BMW	7	725 D, LD	Stufenheck	Heckantrieb	Diesel	170	231	Jul 2016	Feb 2019	2024-03-01	121616
BMW	X3	Xdrive 30 D	SUV	Allrad	Diesel	204	277	Jun 2016	Aug 2017	2024-03-01	121617
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	204	277	Apr 2014	Mar 2018	2024-03-01	121618
Mercedes-benz	Sprinter 4,6-T	414 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	105	143	May 2016	Dec 2018	2024-03-01	121619
Nissan	Gt-R	V6	Coupe	Allrad	Benzin	419	570	Jun 2016	-	2024-03-01	121620
Toyota	Dyna 100	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	54	73	May 1995	Jul 2001	2024-03-01	121636
Renault	Clio iv grandtour	1.5 DCI 110	Kombi	Frontantrieb	Diesel	81	110	Jun 2016	Aug 2021	2026-05-01	121645
Peugeot	3008 ii	1.6 Bluehdi 120	SUV	Frontantrieb	Diesel	88	120	May 2016	Dec 2019	2025-02-03	121646
Peugeot	3008 ii	2.0 Bluehdi 150	SUV	Frontantrieb	Diesel	110	150	May 2016	Sep 2020	2024-11-01	121648
Peugeot	3008 ii	1.6 THP 165	SUV	Frontantrieb	Benzin	121	165	May 2016	-	2024-11-01	121649
Peugeot	3008 ii	1.2 Thp/ Puretech 130	SUV	Frontantrieb	Benzin	96	131	May 2016	-	2024-11-01	121650
Renault	Trafic iii	1.6 DCI 125	Pritsche/Fahrgestell	Frontantrieb	Diesel	92	125	Jul 2015	-	2024-03-01	121651
Renault	Trafic iii	1.6 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jul 2015	-	2024-03-01	121652
Mercedes-benz	Sls amg	Electric Drive	Coupe	Allrad	Elektro	552	751	Jun 2013	-	2024-03-01	121671
Citroën	Zx	1.9 D	Kombi	Frontantrieb	Diesel	52	71	Oct 1993	Jul 1999	2024-03-01	121687
Citroën	Zx	1.9 D	Schrägheck	Frontantrieb	Diesel	52	71	Oct 1993	Jul 1999	2024-03-01	121688
Alfa Romeo	Giulia	2	Stufenheck	Heckantrieb	Benzin	147	200	Aug 2016	Oct 2022	2024-03-01	121698
Chevrolet	Camaro	2.0 Turbo	Coupe	Heckantrieb	Benzin	202	275	Aug 2016	-	2024-03-01	121704
Chevrolet	Camaro	2.0 Turbo	Cabriolet	Heckantrieb	Benzin	202	275	Aug 2016	-	2024-03-01	121706
Renault	Megane iii	1.6 16V	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2013	Aug 2015	2024-03-01	121722
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	245	333	Jun 2016	May 2018	2024-03-01	121726
Mercedes-benz	E-Klasse	E 220 D	Kombi	Heckantrieb	Diesel	120	163	Jul 2016	Oct 2023	2024-03-01	121773


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **45 个输入 Ktype、46 条 READY 映射**；其中 `121616` 因同时包含 725d 与 725Ld，拆分为 G11 短轴和 G12 长轴两条映射。
* 新建 **24 个 DIMENSION_GROUP**，并直接复用 **9 个跨批次既有尺寸组**，未重复抓取既有组。
* 已批量闭合 Peugeot 3008 II、Audi A3 8V facelift、Audi A5/S5 F5、Ford Focus III facelift 商用五门、Suzuki SX4 S-Cross 等聚类。新建尺寸组均采用直接车型规格页的不含后视镜宽度；N400 使用车型官方资料。([汽车目录][1])
* Aston Martin V8 Vantage N400 的三维采用其车型资料直接闭合。([阿斯顿马丁][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**45**
* PENDING Ktype：**55**
* READY 映射行：**46**
* 当前已引用尺寸组：**33**

  * 本轮新建：24
  * 复用既有：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120842	120842	Sedan	Optima IV (JF)	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
120851	120851	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
120900	120900	Sedan	S4 B9	B9	4	EU-AUDI-S4-B9-SEDAN-01	HIGH		READY
120920	120920	Coupe	Chiron I		2	EU-BUGATTI-CHIRON-COUPE-01	HIGH		READY
121049	121049	Convertible	E-Mehari		2	EU-CITROEN-E-MEHARI-CONVERTIBLE-01	HIGH		READY
121091	121091	Coupe	i20 II	GB	3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH		READY
121094	121094	Coupe	i20 II	GB	3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH		READY
121146	121146	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
121173	121173	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121201	121201	Sedan	CT6 I		4	EU-CADILLAC-CT6-I-SEDAN-01	HIGH		READY
121230	121230	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-01	HIGH		READY
121235	121235	Convertible	595C facelift	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH		READY
121238	121238	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121239	121239	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121240	121240	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121242	121242	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121243	121243	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121249	121249	Sedan	Civic IX	FB	4	EU-HONDA-CIVIC-IX-SEDAN-01	HIGH		READY
121304	121304	Coupe	V8 Vantage N400		2	EU-ASTON-MARTIN-V8-VANTAGE-N400-COUPE-01	HIGH		READY
121416	121416	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121442	121442	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH		READY
121445	121445	Hatchback	500 facelift	312	3	EU-FIAT-500-312-FACELIFT-HATCHBACK-3D-01	HIGH		READY
121446	121446	Hatchback	595 facelift	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-3D-01	HIGH		READY
121493	121493	Coupe	S5 II (F5)	F5	2	EU-AUDI-S5-F5-COUPE-01	HIGH		READY
121494	121494	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121495	121495	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121578	121578	MPV	Altea 5P	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH		READY
121586	121586	SUV	SX4 S-Cross I facelift		5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	HIGH		READY
121587	121587	SUV	SX4 S-Cross I facelift		5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	HIGH		READY
121601	121601	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门分支。	READY
121603	121603	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门分支。	READY
121604	121604	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
121605	121605	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
121616_swb	121616	Sedan	7 Series G11 pre-facelift	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	725d短轴G11分支。	READY
121616_lwb	121616	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	725Ld长轴G12分支。	READY
121617	121617	SUV	X3 F25 facelift	F25	5	EU-BMW-X3-F25-FACELIFT-SUV-01	HIGH		READY
121618	121618	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-01	HIGH		READY
121620	121620	Coupe	GT-R R35 phase III	R35	2	EU-NISSAN-GT-R-R35-PHASE-III-COUPE-01	HIGH		READY
121645	121645	Wagon	Clio IV facelift	K98	5	EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	HIGH		READY
121646	121646	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121648	121648	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121649	121649	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121650	121650	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121698	121698	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
121704	121704	Coupe	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH		READY
121706	121706	Convertible	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2534045/kia_optima_sx_2_0_t.html
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500	Automobile-Catalog	https://www.automobile-catalog.com/make/ford_europe/mondeo_4gen/mondeo_4gen2_sedan/2011.html
EU-AUDI-S4-B9-SEDAN-01	4745	1842	1404	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2223170/audi_s4.html
EU-BUGATTI-CHIRON-COUPE-01	4544	2038	1212	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2607230/bugatti_chiron.html
EU-CITROEN-E-MEHARI-CONVERTIBLE-01	3809	1728	1653	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2560220/citroen_e-mehari.html
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2161160/hyundai_i20_coupe_1_2.html
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Automobile-Catalog	https://www.automobile-catalog.com/make/peugeot/3008_2/3008_2_1_2wd/2017.html
EU-CADILLAC-CT6-I-SEDAN-01	5184	1879	1472	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2298170/cadillac_ct6_3_0l_twin_turbo_awd.html
EU-SUZUKI-VITARA-IV-SUV-01	4175	1775	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/3415805/suzuki_vitara_1_6_allgrip_automatic.html
EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	3660	1627	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2407535/abarth_595c_turismo_mt.html
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2082500/ford_focus_1_5_ecoboost_182.html
EU-HONDA-CIVIC-IX-SEDAN-01	4545	1755	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2084555/honda_civic_limousine_1_8_i-vtec.html
EU-ASTON-MARTIN-V8-VANTAGE-N400-COUPE-01	4380	1865	1255	Aston Martin V8 Vantage N400 official brochure	https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_V8_Vantage_N400_brochure.pdf
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2430740/audi_a5_coupe_2_0_tfsi_252_quattro_s-tronic.html
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2258690/fiat_tipo_1_4_16v.html
EU-FIAT-500-312-FACELIFT-HATCHBACK-3D-01	3571	1627	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2258765/fiat_500_1_3_multijet_ii_16v_95.html
EU-ABARTH-595-312-FACELIFT-HATCHBACK-3D-01	3660	1627	1485	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2407445/abarth_595_turismo_mt.html
EU-AUDI-S5-F5-COUPE-01	4692	1846	1368	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2430845/audi_s5_coupe.html
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/3082685/seat_altea_1_4_tsi.html
EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	4300	1765	1580	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/3416630/suzuki_sx4_s-cross_1_4_boosterjet_allgrip.html
EU-BMW-X3-F25-FACELIFT-SUV-01	4657	1881	1661	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2026115/bmw_x3_xdrive30d.html
EU-BMW-X4-F26-SUV-01	4671	1881	1624	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2036225/bmw_x4_xdrive30d.html
EU-NISSAN-GT-R-R35-PHASE-III-COUPE-01	4710	1895	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2409620/nissan_gt-r.html
EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	4267	1732	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2983790/renault_clio_estate_grandtour_energy_dci_110.html
```

## 下一步优先处理

1. 集中拆解 VW Transporter/Multivan T6 的 Bus、Kasten、Pritsche/Fahrgestell，以及短轴、长轴和驾驶室分支。
2. 闭合 Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter、Toyota Dyna 等底盘驾驶室尺寸。
3. 处理 Silverado 2500、Avalanche、Courier 等 CAB/货斗差异，以及 Tesla Model S 改款边界、Kia Soul 和其余历史车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2017/2534045/kia_optima_sx_2_0_t.html?utm_source=chatgpt.com "2017 Kia Optima SX 2.0 T Specs Review (182.7 kW ..."
[2]: https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_V8_Vantage_N400_brochure.pdf?utm_source=chatgpt.com "V8 VANTAGE N400"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Tesla Model S `120799`、`120800` 的改款边界拆分：改款前新建尺寸组，2016 facelift 分支直接复用已有缓存组。Tesla 官方旧款手册给出的车长、无后视镜宽度和高度为 `4970 × 1964 × 1445 mm`。([Tesla][1])
* 完成 Kia Niro I PHEV `120843`。官方技术规格明确为 `4355 × 1805 × 1535 mm`，宽度口径不含后视镜。([起亚新闻官网][2])
* 本轮首次创建 2 个尺寸组，另新增引用 1 个既有 Tesla facelift 尺寸组，未重复输出既有组来源。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**48**
* PENDING Ktype：**52**
* READY 映射行：**51**
* 当前已引用尺寸组：**36**
* 本轮首次创建尺寸组：**2**
* 本轮新增复用既有尺寸组：**1**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120799_prefl	120799	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款前物理外廓。	READY
120799_facelift	120799	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款后物理外廓。	READY
120800_prefl	120800	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款前物理外廓。	READY
120800_facelift	120800	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款后物理外廓。	READY
120843	120843	SUV	Niro I	DE	5	EU-KIA-NIRO-I-PHEV-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445	Tesla Model S Owner's Manual	https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-KIA-NIRO-I-PHEV-SUV-01	4355	1805	1535	Kia Motors Ireland Niro Plug-in Hybrid technical specifications	https://press.kia.com/ie/en/home/media-resouces/press-releases/2017/NiroPHEV_pressrelease.html
```

## 下一步优先处理

1. 闭合 VW Transporter/Multivan T6 的 Bus、Kasten、Pritsche/Fahrgestell，并按轴距、驾驶室和单双排底盘拆分。
2. 解决 Kia Soul II facelift 与已有尺寸组之间的宽度冲突，禁止覆盖既有组。
3. 集中处理 Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter、Toyota Dyna 等多轴距底盘车型。

推进信号：CONTINUE

[1]: https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html?utm_source=chatgpt.com "Dimensions and Weights"
[2]: https://press.kia.com/ie/en/home/media-resouces/press-releases/2017/NiroPHEV_pressrelease.html?utm_source=chatgpt.com "Kia Motors Ireland Launch Niro Plug In Hybrid"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增闭合 **11 个 Ktype、12 条 READY 映射**，首次创建 **12 个尺寸组**；未重复输出或重新抓取既有尺寸组。
* `121773` 覆盖 Mercedes-Benz E 220 d S213 改款前后两个不同外廓，已拆为 `prefl` 与 `facelift`：改款前为 `4933 × 1852 × 1475 mm`，改款后为 `4945 × 1852 × 1460 mm`。([汽车目录][1])
* Spyker C8 Preliator 采用官方发布资料的 `4628 × 1953 × 1202 mm`，其中宽度明确不含后视镜。([Payload Website Template][2])
* Renault Twizy 采用官方手册最大外廓 `2337 × 1237 × 1454 mm`；SLS AMG Electric Drive 按 Mercedes-Benz 官方档案确认的 197 系列双门外廓建组。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**59**
* PENDING Ktype：**41**
* READY 映射行：**63**
* 当前已引用尺寸组：**48**
* 本轮首次创建尺寸组：**12**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120784	120784	SUV	Forester IV (SJ)	SJ	5	EU-SUBARU-FORESTER-SJ-SUV-01	HIGH		READY
120853	120853	Sedan	Legacy VI	BN	4	EU-SUBARU-LEGACY-BN-SEDAN-01	HIGH		READY
120892	120892	Wagon	Passat B8 Alltrack	3G5	5	EU-VW-PASSAT-B8-ALLTRACK-WAGON-01	HIGH		READY
120901	120901	Wagon	S4 B9	8W5	5	EU-AUDI-S4-B9-AVANT-WAGON-01	HIGH		READY
121220	121220	SUV	C-HR I	NGX10	5	EU-TOYOTA-C-HR-I-SUV-01	HIGH	前驱1.2T NGX10分支。	READY
121228	121228	Coupe	C8 Preliator		2	EU-SPYKER-C8-PRELIATOR-COUPE-01	HIGH		READY
121500	121500	Hatchback	Twizy I	X09	2	EU-RENAULT-TWIZY-X09-HATCHBACK-01	MEDIUM	Twizy双座四轮车按输入Schrägheck归入Hatchback。	READY
121671	121671	Coupe	SLS AMG Electric Drive	N197	2	EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	MEDIUM	Electric Drive N197采用197系列量产双门外廓。	READY
121722	121722	Hatchback	Megane III	BZ0	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH		READY
121726	121726	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH		READY
121773_prefl	121773	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
121773_facelift	121773	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	2020改款后物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-FORESTER-SJ-SUV-01	4595	1795	1735	Automobile-Catalog 2014 Subaru Forester 2.5i AWD	https://www.automobile-catalog.com/car/2014/3293270/subaru_forester_2_5i_awd.html
EU-SUBARU-LEGACY-BN-SEDAN-01	4795	1840	1500	Automobile-Catalog 2016 Subaru Legacy 3.6R Limited AWD	https://www.automobile-catalog.com/car/2016/3307955/subaru_legacy_3_6r_limited_awd.html
EU-VW-PASSAT-B8-ALLTRACK-WAGON-01	4777	1832	1506	Volkswagen Passat Estate VIII brochure; Automoli Passat Alltrack B8 technical data	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf; https://www.automoli.com/au/vehicles/volkswagen/passat/passat-alltrack-b8-4676/
EU-AUDI-S4-B9-AVANT-WAGON-01	4745	1842	1411	Automobile-Catalog 2017 Audi S4 Avant	https://www.automobile-catalog.com/car/2017/2223185/audi_s4_avant.html
EU-TOYOTA-C-HR-I-SUV-01	4360	1795	1565	Toyota C-HR 2016 European Owner's Manual	https://www.carmanualsonline.info/toyota-c-hr-2016-owners-manual/77
EU-SPYKER-C8-PRELIATOR-COUPE-01	4628	1953	1202	Spyker C8 Preliator official press release	https://archive.spykercars.com/uploads/news/press_release_spyker_C8_preliator.pdf
EU-RENAULT-TWIZY-X09-HATCHBACK-01	2337	1237	1454	Renault Twizy official vehicle user manual	https://www.user-manual.renault.com/sites/renault/files/Twizy-913-19_ENG.pdf
EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	4638	1939	1262	Mercedes-Benz Public Archive SLS AMG Coupe technical data; Mercedes-Benz Public Archive SLS AMG 197 series history	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLS-AMG-Coup-2010---2014.xhtml?oid=192608215; https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/SLS-AMG-Coups-der-Baureihe-197-2010---2014.xhtml?oid=6016956
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4302	1808	1471	Automobile-Catalog 2014 Renault Megane Hatch 1.6 16V 110	https://www.automobile-catalog.com/car/2014/2960915/renault_megane_hatch_1_6_16v_110.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Automobile-Catalog 2016 Mercedes-Benz E 400 4MATIC	https://www.automobile-catalog.com/car/2016/2453300/mercedes-benz_e_400_4matic.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Automobile-Catalog 2016 Mercedes-Benz E 220 d T-Modell	https://www.automobile-catalog.com/car/2016/2453360/mercedes-benz_e_220_d_t-modell.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Automobile-Catalog 2021 Mercedes-Benz E 220 d T-Modell	https://www.automobile-catalog.com/car/2021/2968550/mercedes-benz_e_220_d_t-modell.html
```

## 下一步优先处理

1. 集中拆分 VW Transporter/Multivan T6 的短轴、长轴、Kasten、Bus、单排和双排底盘分支。
2. 处理 Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter 的底盘驾驶室及轴距组合。
3. 解决 Kia Soul、Hyundai Creta、Smart Fortwo Cabrio 等配置高度或宽度口径冲突，再处理 Silverado、Avalanche、Courier 等 CAB/货斗分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2016/2453360/mercedes-benz_e_220_d_t-modell.html?utm_source=chatgpt.com "2016 Mercedes-Benz E 220 d T-Modell Specs Review (143 kW / 194 PS / 192 hp) (since September 2016 for Europe )"
[2]: https://archive.spykercars.com/uploads/news/press_release_spyker_C8_preliator.pdf "Microsoft Word - press_release_spyker_C8_preliator.docx"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 BMW 3 Series E93 两个 Ktype，并按 2010 年 LCI 拆分：改款前外廓 `4580 × 1782 × 1384 mm`，改款后为 `4612 × 1782 × 1384 mm`。两套尺寸均来自 BMW Group 官方技术资料。([BMW Group PressClub][1])
* 闭合 Hyundai Creta I 2.0 前驱、Alfa Romeo Spider 2000、BMW E30 Baur TC 和 Smart Fortwo 450 Cabrio。([汽车手册在线][2])
* `121236`、`121237` 按 Focus III 改款前后拆分；两阶段三维相同，直接复用已闭合的五门商用外廓尺寸组，不重复输出尺寸组。Ford 官方资料确认五门 Focus 的无后视镜宽度为 1823 mm。([Ford From the Road][3])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**67**
* PENDING Ktype：**33**
* READY 映射行：**75**
* 当前已引用尺寸组：**54**
* 本轮首次创建尺寸组：**6**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121100_prefl	121100	Convertible	3 Series E93 pre-facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	2010 LCI前物理外廓。	READY
121100_facelift	121100	Convertible	3 Series E93 facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	2010 LCI后物理外廓。	READY
121102_prefl	121102	Convertible	3 Series E93 pre-facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	2010 LCI前物理外廓。	READY
121102_facelift	121102	Convertible	3 Series E93 facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	2010 LCI后物理外廓。	READY
121109	121109	SUV	Creta I	GS	5	EU-HYUNDAI-CRETA-I-SUV-01	HIGH	2.0前驱五门分支。	READY
121236_prefl	121236	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款前分支。	READY
121236_facelift	121236	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款后分支。	READY
121237_prefl	121237	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款前分支。	READY
121237_facelift	121237	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款后分支。	READY
121297	121297	Convertible	Spider Series 2	105	2	EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	HIGH	2000 Veloce方尾第二系列。	READY
121337	121337	Convertible	3 Series E30 Baur TC	E30	2	EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	HIGH	Baur Top-Cabrio物理外廓。	READY
121536	121536	Convertible	Fortwo I facelift	A450	2	EU-SMART-FORTWO-A450-CONVERTIBLE-01	HIGH	450系列Cabrio外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384	BMW Korea 2007 BMW 3 Series Convertible official specifications	https://www.press.bmwgroup.com/korea/article/detail/T0046055KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-3%EC%8B%9C%EB%A6%AC%EC%A6%88-%EC%BB%A8%EB%B2%84%ED%84%B0%EB%B8%94-%EA%B5%AD%EB%82%B4-%EC%B6%9C%EC%8B%9C
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	BMW Group 3 Series Convertible E93 official technical data 09/2010	https://www.press.bmwgroup.com/spain/article/attachment/T0084820ES/132013
EU-HYUNDAI-CRETA-I-SUV-01	4270	1780	1630	Hyundai Creta 2016 Owner's Manual; Auto.ru Hyundai Creta 2.0 150 hp specifications	https://www.carmanualsonline.info/hyundai-creta-2016-owner-s-manual/?srch=width; https://auto.ru/catalog/cars/hyundai/creta/20773960/20773995/specifications/20773995_21665614_20795509/
EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	4120	1630	1290	Automobile-Catalog 1971 Alfa Romeo 2000 Spider Veloce	https://www.automobile-catalog.com/car/1971/65285/alfa_romeo_2000_spider_veloce.html
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380	ADAC BMW 316i Baur Top-Cabrio E30 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/3er-reihe/e30/348035/
EU-SMART-FORTWO-A450-CONVERTIBLE-01	2500	1537	1549	Automobile-Catalog 2004 Smart Fortwo City-Cabrio Smart and Pulse 61	https://www.automobile-catalog.com/car/2004/3154625/smart_fortwo_city-cabrio_smart_and_pulse_61.html
```

## 下一步优先处理

1. 闭合 VW Transporter/Multivan T6 的 Bus、Kasten、短轴和长轴分支。
2. 拆分 VW Transporter T6、Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter 的单排/双排底盘和轴距组合。
3. 处理 Chevrolet Silverado 2500、Avalanche、Ford Courier 等驾驶室与货斗分支。
4. 闭合剩余边界较单一的 Kia Soul、VW Polo Van、Citroën ZX、Jeep Cherokee 和 Toyota Proace。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/korea/article/detail/T0046055KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-3%EC%8B%9C%EB%A6%AC%EC%A6%88-%EC%BB%A8%EB%B2%84%ED%84%B0%EB%B8%94-%EA%B5%AD%EB%82%B4-%EC%B6%9C%EC%8B%9C?utm_source=chatgpt.com "BMW 코리아, 뉴 3시리즈 컨버터블 국내 출시"
[2]: https://www.carmanualsonline.info/hyundai-creta-2016-owner-s-manual/?srch=width "width Hyundai Creta 2016 Owner's Manual (512 Pages)"
[3]: https://media.ford.com/content/dam/fordmedia/Europe/en/2013/Features/The%20Ecoboost%20Engine/Focus1.0-litre%20EcoBoost_TechSpecs_EU.pdf?utm_source=chatgpt.com "FORD FOCUS 1.0-LITRE ECOBOOST SPECIFICATIONS"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Toyota Proace II `121440`。官方车型范围显示 2.0D 180 的板式货车对应 Medium 车身，尺寸为 `4959 × 1920 × 1899 mm`，其中宽度不含后视镜。该三维与跨批次已有的 Proace Medium 尺寸组不一致，因此新建尺寸组，未覆盖已有组。([Toyota Media Site][1])
* VW Polo Kasten 暂未新增映射：官方数据区分普通车身与 BlueGT 高度，但当前资料尚未闭合商用车门数边界。Kia Soul II 也因官方资料显示高度随配置变化，本轮未猜测复用既有组。([volkswagen-newsroom.com][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**68**
* PENDING Ktype：**32**
* READY 映射行：**76**
* 已确认尺寸组：**55**
* 本轮首次创建尺寸组：**1**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121440	121440	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	HIGH	2.0D 180板式Kasten对应Medium车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
```

## 下一步优先处理

1. 闭合 VW Polo Kasten 的门数边界，并区分普通车身与 BlueGT 高度。
2. 集中拆分 VW Transporter/Multivan T6 的 Bus、Kasten、轴距及底盘驾驶室分支。
3. 处理 Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter 等多轴距底盘车型。
4. 最后处理 Silverado 2500、Avalanche、Courier 等驾驶室和货斗组合。

推进信号：CONTINUE

[1]: https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf "Microsoft Word - 210223M - Proace full release"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046 "Vehicle data Polo V profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 8 条 VW Polo V facelift CityVan 映射。普通动力分支采用 `3972 × 1682 × 1462 mm`；`121183` 的 1.4 TSI 150 PS 对应 BlueGT 高度分支 `3972 × 1682 × 1453 mm`。CityVan 按三门商用车身落盘。([volkswagen-newsroom.com][1])
* 闭合 Chevrolet Avalanche II、Jeep Cherokee XJ 五门和 Citroën ZX Break。Avalanche 的英寸规格已按 `1 in = 25.4 mm` 取整；Cherokee 与 ZX 均使用明确标注不含后视镜宽度的规格。([Edmunds][2])
* 本轮新增 **11 个 READY Ktype**、**5 个尺寸组**；未重新输出或修改既有尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**79**
* PENDING Ktype：**21**
* READY 映射行：**87**
* 已确认尺寸组：**60**
* 本轮首次创建尺寸组：**5**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
121176	121176	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121177	121177	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121180	121180	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121181	121181	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121182	121182	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121183	121183	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	MEDIUM	1.4 TSI 150 PS对应BlueGT高度分支。	READY
121186	121186	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121188	121188	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121496	121496	Pickup	Avalanche II	GMT900	4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
121502	121502	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-01	MEDIUM	欧洲2.5五门分支。	READY
121687	121687	Wagon	ZX	N2	5	EU-CITROEN-ZX-N2-WAGON-01	HIGH	Break五门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462	Volkswagen Newsroom Polo V vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453	Volkswagen Newsroom Polo V vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-CHEVROLET-AVALANCHE-II-PICKUP-01	5621	2009	1946	Edmunds 2007 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2007/features-specs/
EU-JEEP-CHEROKEE-XJ-SUV-5D-01	4200	1720	1621	Automobile-Catalog 1995 Jeep Cherokee 2.5 XLE; Automobile-Catalog 1994 Jeep Cherokee SE 4WD 4-Door 2.5L	https://www.automobile-catalog.com/car/1995/1314410/jeep_cherokee_2_5_xle.html; https://www.automobile-catalog.com/car/1994/1314590/jeep_cherokee_se_4wd_4-door_2_5l.html
EU-CITROEN-ZX-N2-WAGON-01	4260	1702	1421	Automobile-Catalog 1994 Citroen ZX Break Fugue Avantage 1.9 D	https://www.automobile-catalog.com/car/1994/2032115/citroen_zx_break_fugue_avantage_1_9_d.html
```

## 下一步优先处理

1. 集中闭合 VW Transporter/Multivan T6 的 Bus、Kasten、短轴和长轴分支。
2. 拆分 Transporter T6、Peugeot Boxer、Renault Trafic、Mercedes-Benz Sprinter 的底盘驾驶室及轴距组合。
3. 处理 Silverado 2500 的驾驶室/货斗分支，以及 Ford Courier、Toyota Dyna 和 Dongfeng K02。
4. 最后解决 Kia Soul II、Citroën ZX Hatchback、Transit Connect V408 的配置高度或车身边界。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046?utm_source=chatgpt.com "Vehicle data Polo V profile"
[2]: https://www.edmunds.com/chevrolet/avalanche/2007/features-specs/?utm_source=chatgpt.com "Used 2007 Chevrolet Avalanche Specs & Features"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Kia Soul II `120778`。官方规格确认同一五门车身存在 `1593 mm` 标准高度和 `1618 mm` 带车顶杆高位分支；高位分支复用已有尺寸组，仅新建标准高度组。([起亚新闻官网][1])
* 闭合 Ford Transit Connect V408 `121226`，按官方车型矩阵拆分为 Van L1、Van L2、DCIV L1、DCIV L2 和 Kombi L2 五种物理外廓。官方尺寸表明确给出全部车长、无后视镜宽度及高度。
* 闭合 Citroën ZX Hatchback `121688`，按三门/五门及中期改款前后拆成四个物理分支。改款前规格为 `4071 × 1688 × 1397 mm`，后期规格为 `4070 × 1688 × 1399 mm`。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**82**
* PENDING Ktype：**18**
* READY 映射行：**98**
* 已确认并引用尺寸组：**71**
* 本轮新增映射行：**11**
* 本轮首次创建尺寸组：**10**
* 本轮新增复用既有尺寸组：**1**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120778_noroofbars	120778	Hatchback	Soul II	PS	5	EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	MEDIUM	16英寸车轮且无车顶杆的标准高度分支。	READY
120778_roofbars	120778	Hatchback	Soul II	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	MEDIUM	18英寸车轮且带车顶杆的高位分支。	READY
121226_van_l1	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	HIGH	短轴板式货车分支。	READY
121226_van_l2	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	HIGH	长轴板式货车分支。	READY
121226_dciv_l1	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	HIGH	短轴双排座厢式车分支。	READY
121226_dciv_l2	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	HIGH	长轴双排座厢式车分支。	READY
121226_kombi_l2	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	HIGH	长轴七座Kombi分支。	READY
121688_3dr_prefl	121688	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
121688_5dr_prefl	121688	Hatchback	ZX Phase I	N2	5	EU-CITROEN-ZX-N2-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
121688_3dr_facelift	121688	Hatchback	ZX Phase II	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
121688_5dr_facelift	121688	Hatchback	ZX Phase II	N2	5	EU-CITROEN-ZX-N2-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	4140	1800	1593	Kia Europe 2014 Soul official technical specifications	https://press.kia.com/content/kiapress/eu/en/home/models/soul/soul-2014.html
EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	4418	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	4818	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	4418	1835	1836	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	4818	1835	1839	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	4818	1835	1840	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-CITROEN-ZX-N2-HATCHBACK-3D-PREFL-01	4071	1688	1397	Automobile-Catalog 1993 Citroen ZX Reflex 1.9 D	https://www.automobile-catalog.com/car/1993/1454570/citroen_zx_reflex_1_9_d.html
EU-CITROEN-ZX-N2-HATCHBACK-5D-PREFL-01	4071	1688	1397	Automobile-Catalog 1993 Citroen ZX Reflex 1.9 D	https://www.automobile-catalog.com/car/1993/1454570/citroen_zx_reflex_1_9_d.html
EU-CITROEN-ZX-N2-HATCHBACK-3D-FACELIFT-01	4070	1688	1399	Automobile-Catalog 1996 Citroen ZX 1.9 D X	https://www.automobile-catalog.com/car/1996/542855/citroen_zx_1_9_d_x.html
EU-CITROEN-ZX-N2-HATCHBACK-5D-FACELIFT-01	4070	1688	1399	Automobile-Catalog 1996 Citroen ZX 1.9 D X	https://www.automobile-catalog.com/car/1996/542855/citroen_zx_1_9_d_x.html
```

## 下一步优先处理

1. 闭合 VW Multivan/Transporter T6 的 Bus 与 Kasten 短轴、长轴和车顶高度分支。
2. 集中拆分 VW Transporter T6、Peugeot Boxer、Renault Trafic 和 Mercedes-Benz Sprinter 的底盘驾驶室与轴距组合。
3. 处理 Chevrolet Silverado 2500 的驾驶室/货斗组合。
4. 最后闭合 Ford Courier、Toyota Dyna 100 和 Dongfeng K02。

推进信号：CONTINUE

[1]: https://press.kia.com/content/kiapress/eu/en/home/models/soul/soul-2014.html "Soul"
[2]: https://www.automobile-catalog.com/car/1993/1454570/citroen_zx_reflex_1_9_d.html?utm_source=chatgpt.com "1993 Citroen ZX Reflex 1.9 D Specs Review (52 kW / 71 PS / 70 hp) (for Europe )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合本批剩余的 **7 个 Volkswagen T6 Ktype**，新增 24 条 READY 映射。
* `120803` 按 Multivan 短轴乘用车身关联；`120808` 拆分 Caravelle/Bus 短轴与长轴。官方规格给出短轴 `4904 × 1904 × 1970 mm`、长轴 `5304 × 1904 × 1990 mm`，宽度均明确不含后视镜。
* `120813` 按 T6 Kasten 的短轴低顶、短轴中顶、长轴低顶、长轴中顶、长轴高顶五种外廓拆分；高顶仅用于长轴车身。([汽车目录档案][1])
* `120779`、`120815`、`120822`、`120823` 分别拆为单排裸底盘、双排裸底盘、单排栏板和双排栏板四个物理分支；发动机功率及驱动形式不另建尺寸组。底盘和栏板尺寸采用 Volkswagen 官方 Transporter 规格。([大众汽车 澳洲][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**89**
* PENDING Ktype：**11**
* READY 映射行：**122**
* 已确认并引用尺寸组：**82**
* 本轮新增映射行：**24**
* 本轮首次创建尺寸组：**11**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120779_singlecab_chassis	120779	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120779_doublecab_chassis	120779	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120779_singlecab_dropside	120779	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120779_doublecab_dropside	120779	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120803	120803	MPV	Multivan T6			EU-VW-TRANSPORTER-T6-BUS-SWB-01	MEDIUM	Multivan短轴乘用车身。	READY
120808_swb	120808	MPV	Transporter T6			EU-VW-TRANSPORTER-T6-BUS-SWB-01	HIGH	Caravelle/Bus短轴分支。	READY
120808_lwb	120808	MPV	Transporter T6			EU-VW-TRANSPORTER-T6-BUS-LWB-01	HIGH	Caravelle/Bus长轴分支。	READY
120813_swb_lowroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-SWB-LOWROOF-01	HIGH	短轴低顶板式货车。	READY
120813_swb_medroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-SWB-MEDROOF-01	HIGH	短轴中顶板式货车。	READY
120813_lwb_lowroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-LOWROOF-01	HIGH	长轴低顶板式货车。	READY
120813_lwb_medroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-MEDROOF-01	HIGH	长轴中顶板式货车。	READY
120813_lwb_highroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶板式货车。	READY
120815_singlecab_chassis	120815	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120815_doublecab_chassis	120815	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120815_singlecab_dropside	120815	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120815_doublecab_dropside	120815	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120822_singlecab_chassis	120822	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120822_doublecab_chassis	120822	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120822_singlecab_dropside	120822	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120822_doublecab_dropside	120822	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120823_singlecab_chassis	120823	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120823_doublecab_chassis	120823	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120823_singlecab_dropside	120823	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120823_doublecab_dropside	120823	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	5300	1904	1948	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	5300	1904	1960	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	5500	1994	1848	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	5500	1994	1960	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-BUS-SWB-01	4904	1904	1970	Volkswagen Multivan official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-BUS-LWB-01	5304	1904	1990	Volkswagen Multivan official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-VAN-SWB-LOWROOF-01	4904	1904	1990	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-SWB-MEDROOF-01	4904	1904	2177	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-LOWROOF-01	5304	1904	1990	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-MEDROOF-01	5304	1904	2177	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-HIGHROOF-01	5304	1904	2476	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
```

## 下一步优先处理

1. Peugeot Boxer `120845`–`120847` 与 Renault Trafic `121651`–`121652` 的轴距、单双排驾驶室和栏板/裸底盘分支。
2. Mercedes-Benz Sprinter 4.6-T `121619` 的底盘长度及驾驶室边界。
3. Chevrolet Silverado 2500 `121480`、`121481` 的驾驶室和货斗组合。
4. 最后闭合 Dongfeng K02、Ford Courier 与 Toyota Dyna 100。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf?utm_source=chatgpt.com "VW-T6-Transporter-2017-UK.pdf"
[2]: https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf?srsltid=AfmBOoomLmvOLFvNMQVjBEEfGGXddQpAgsf6wsJKqzi1ygNOAaXvlYpL "https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf?srsltid=AfmBOoomLmvOLFvNMQVjBEEfGGXddQpAgsf6wsJKqzi1ygNOAaXvlYpL"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Peugeot Boxer `120845`–`120847`：按 L2 单排底盘、L3 单排底盘、L3 双排底盘拆分；160 PS 版本另包含 L4 单排底盘。官方 Boxer 转换底盘规格明确给出各分支的完整外廓及不含后视镜宽度。
* 闭合 Renault Trafic III `121651`、`121652`：两者均关联唯一的 L2H1 Platform Cab 外廓。官方 Trafic 尺寸资料给出 `5399 mm` 长、`1956 mm` 不含后视镜宽度；驾驶室高度采用同一 L2H1 基础车身的 `1971 mm`。([Installer Online][1])
* 本轮新增 **12 条 READY 映射、5 个尺寸组**；未重复抓取或输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**94**
* PENDING Ktype：**6**
* READY 映射行：**134**
* 已确认并引用尺寸组：**87**
* 本轮新增映射行：**12**
* 本轮首次创建尺寸组：**5**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120845_singlecab_l2	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	MEDIUM	L2单排驾驶室底盘分支。	READY
120845_singlecab_l3	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	MEDIUM	L3单排驾驶室底盘分支。	READY
120845_doublecab_l3	120845	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	MEDIUM	L3双排驾驶室底盘分支。	READY
120846_singlecab_l2	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120846_singlecab_l3	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120846_doublecab_l3	120846	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
120847_singlecab_l2	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120847_singlecab_l3	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120847_singlecab_l4	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	HIGH	L4单排驾驶室底盘分支。	READY
120847_doublecab_l3	120847	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
121651	121651	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
121652	121652	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	5358	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	5943	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	6308	2050	2270	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	5843	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971	Renault New Trafic official dimensions appendix	https://www.installeronline.co.uk/wp-content/uploads/2014/09/renault-trafic-2014-specs.pdf
```

## 下一步优先处理

1. Mercedes-Benz Sprinter 4.6-T `121619` 的 W906 单排/双排驾驶室及轴距分支。
2. Chevrolet Silverado 2500 `121480`、`121481` 的 Regular、Extended、Crew Cab 与货斗组合。
3. 最后闭合 Dongfeng K02 `120880`、Ford Courier `121499` 和 Toyota Dyna 100 `121636`。

推进信号：CONTINUE

[1]: https://www.installeronline.co.uk/wp-content/uploads/2014/09/renault-trafic-2014-specs.pdf "20140409_Appendix NewTrafic_ENG"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Peugeot Boxer `120845`–`120847`：按 L2 单排底盘、L3 单排底盘、L3 双排底盘拆分；160 PS 版本另包含 L4 单排底盘。官方 Boxer 转换底盘规格明确给出各分支的完整外廓及不含后视镜宽度。
* 闭合 Renault Trafic III `121651`、`121652`：两者均关联唯一的 L2H1 Platform Cab 外廓。官方 Trafic 尺寸资料给出 `5399 mm` 长、`1956 mm` 不含后视镜宽度；驾驶室高度采用同一 L2H1 基础车身的 `1971 mm`。([Installer Online][1])
* 本轮新增 **12 条 READY 映射、5 个尺寸组**；未重复抓取或输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**94**
* PENDING Ktype：**6**
* READY 映射行：**134**
* 已确认并引用尺寸组：**87**
* 本轮新增映射行：**12**
* 本轮首次创建尺寸组：**5**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120845_singlecab_l2	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	MEDIUM	L2单排驾驶室底盘分支。	READY
120845_singlecab_l3	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	MEDIUM	L3单排驾驶室底盘分支。	READY
120845_doublecab_l3	120845	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	MEDIUM	L3双排驾驶室底盘分支。	READY
120846_singlecab_l2	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120846_singlecab_l3	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120846_doublecab_l3	120846	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
120847_singlecab_l2	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120847_singlecab_l3	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120847_singlecab_l4	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	HIGH	L4单排驾驶室底盘分支。	READY
120847_doublecab_l3	120847	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
121651	121651	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
121652	121652	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	5358	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	5943	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	6308	2050	2270	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	5843	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971	Renault New Trafic official dimensions appendix	https://www.installeronline.co.uk/wp-content/uploads/2014/09/renault-trafic-2014-specs.pdf
```

## 下一步优先处理

1. Mercedes-Benz Sprinter 4.6-T `121619` 的 W906 单排/双排驾驶室及轴距分支。
2. Chevrolet Silverado 2500 `121480`、`121481` 的 Regular、Extended、Crew Cab 与货斗组合。
3. 最后闭合 Dongfeng K02 `120880`、Ford Courier `121499` 和 Toyota Dyna 100 `121636`。

推进信号：CONTINUE

[1]: https://www.installeronline.co.uk/wp-content/uploads/2014/09/renault-trafic-2014-specs.pdf "20140409_Appendix NewTrafic_ENG"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Dongfeng Xiaokang K02 `120880`，按 1.0 39 kW 可对应的短轴与标准轴距双排皮卡拆分；两者外廓分别为 `4000 × 1560 × 1870 mm` 和 `4160 × 1560 × 1870 mm`。([17Vin][1])
* 闭合 Ford Courier `121499`。巴西版单排 Courier 1.6 的规格为 `4457 × 1685 × 1477 mm`，资料明确说明宽度不含外后视镜。([todomecanica.com][2])
* 闭合 Mercedes-Benz Sprinter 4.6-T `121619`，按 W906 中轴/长轴、单排/双排，以及裸底盘/原厂栏板共拆分 8 个外廓。Mercedes-Benz 技术资料分别给出了底盘车和原厂栏板车的总长、车宽和驾驶室高度。([Dezo's Garage][3])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**97**
* PENDING Ktype：**3**
* READY 映射行：**145**
* 已确认并引用尺寸组：**98**
* 本轮新增映射行：**11**
* 本轮首次创建尺寸组：**11**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120880_swb	120880	Pickup	K-Series I	EQ1021NF	4	EU-DONGFENG-XIAOKANG-K02-PICKUP-SWB-01	MEDIUM	1.0短轴双排皮卡分支。	READY
120880_stdwb	120880	Pickup	K-Series I	EQ1021NF	4	EU-DONGFENG-XIAOKANG-K02-PICKUP-STANDARD-WB-01	MEDIUM	1.0标准轴距双排皮卡分支。	READY
121499	121499	Pickup	Courier Brazil Mk V		2	EU-FORD-COURIER-BRAZIL-MK-V-PICKUP-01	HIGH	巴西版Fiesta衍生单排皮卡。	READY
121619_singlecab_mwb_chassis	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	MEDIUM	中轴单排驾驶室裸底盘。	READY
121619_singlecab_lwb_chassis	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘。	READY
121619_doublecab_mwb_chassis	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-MWB-01	MEDIUM	中轴双排驾驶室裸底盘。	READY
121619_doublecab_lwb_chassis	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘。	READY
121619_singlecab_mwb_dropside	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-MWB-01	MEDIUM	中轴单排驾驶室原厂栏板。	READY
121619_singlecab_lwb_dropside	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室原厂栏板。	READY
121619_doublecab_mwb_dropside	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-MWB-01	MEDIUM	中轴双排驾驶室原厂栏板。	READY
121619_doublecab_lwb_dropside	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室原厂栏板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DONGFENG-XIAOKANG-K02-PICKUP-SWB-01	4000	1560	1870	17VIN Dongfeng Xiaokang K02 1.0 short-wheelbase specifications	https://en.17vin.com/model/k7bxe.html
EU-DONGFENG-XIAOKANG-K02-PICKUP-STANDARD-WB-01	4160	1560	1870	17VIN Dongfeng Xiaokang K02 1.0 standard-wheelbase specifications	https://en.17vin.com/model/7w8qb.html
EU-FORD-COURIER-BRAZIL-MK-V-PICKUP-01	4457	1685	1477	Ford Courier technical manual	https://www.todomecanica.com/component/k2/download/2970_51453e9e78423c968d30c16942c47ac0.html
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	6103	1990	2344	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	6863	1990	2335	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-MWB-01	6103	1990	2362	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-LWB-01	6863	1990	2351	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-MWB-01	6245	2130	2344	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-LWB-01	6945	2130	2335	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-MWB-01	6155	2130	2362	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-LWB-01	7055	2130	2351	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
```

## 下一步优先处理

1. 闭合 Chevrolet Silverado 2500 `121480`、`121481` 的 Regular、Extended、Crew Cab 与标准/长货斗组合，并分别确认后驱和四驱高度。
2. 闭合 Toyota Dyna 100 `121636` 的 LY100 单排/双排及底盘长度边界。
3. 三个剩余 Ktype 清零后，立即汇总两张最终完整 TSV 并生成指定下载文件。

推进信号：CONTINUE

[1]: https://en.17vin.com/model/k7bxe.html?utm_source=chatgpt.com "-〖2008 DongFeng DFSK K02 1.0L Short Wheelbase Edition Basic Type AF10-06〗parameter configuration-17vin.com"
[2]: https://www.todomecanica.com/component/k2/download/2970_51453e9e78423c968d30c16942c47ac0.html "https://www.todomecanica.com/component/k2/download/2970_51453e9e78423c968d30c16942c47ac0.html"
[3]: https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf "https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_401-500_ktype_dimension_mapping_final.tsv
- all_401-500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已闭合最后 3 个 Ktype：`121480`、`121481` 和 `121636`。
* Silverado 2500HD 已按 Regular Cab、Extended Cab、Crew Cab 及货斗长度拆分；后驱和四驱 Regular Cab 因高度不同使用独立尺寸组。Edmunds 规格页明确提供各分支的总长、不含后视镜宽度和高度。([Edmunds][1])
* Toyota Dyna 100 已确认 `LY100/LY100R`、1995–2001 年平台/底盘边界，并以 `4415 × 1695 × 1830 mm` 建组。([Carlist.my - Malaysia's No.1 Car Site][2])
* 已完成机械检查：表头正确、156 个 `id` 唯一、105 个尺寸组唯一、100 个输入 Ktype 全覆盖、映射引用全部闭合、无孤立尺寸组、无空尺寸或来源。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**100**
* PENDING Ktype：**0**
* 最终映射行：**156**
* 最终 DIMENSION_GROUP：**105**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120778_noroofbars	120778	Hatchback	Soul II	PS	5	EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	MEDIUM	16英寸车轮且无车顶杆的标准高度分支。	READY
120778_roofbars	120778	Hatchback	Soul II	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	MEDIUM	18英寸车轮且带车顶杆的高位分支。	READY
120779_singlecab_chassis	120779	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120779_doublecab_chassis	120779	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120779_singlecab_dropside	120779	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120779_doublecab_dropside	120779	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120784	120784	SUV	Forester IV (SJ)	SJ	5	EU-SUBARU-FORESTER-SJ-SUV-01	HIGH		READY
120799_prefl	120799	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款前物理外廓。	READY
120799_facelift	120799	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款后物理外廓。	READY
120800_prefl	120800	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款前物理外廓。	READY
120800_facelift	120800	Hatchback	Model S facelift 2016		5	EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	MEDIUM	跨2016改款，拆分改款后物理外廓。	READY
120803	120803	MPV	Multivan T6			EU-VW-TRANSPORTER-T6-BUS-SWB-01	MEDIUM	Multivan短轴乘用车身。	READY
120808_swb	120808	MPV	Transporter T6			EU-VW-TRANSPORTER-T6-BUS-SWB-01	HIGH	Caravelle/Bus短轴分支。	READY
120808_lwb	120808	MPV	Transporter T6			EU-VW-TRANSPORTER-T6-BUS-LWB-01	HIGH	Caravelle/Bus长轴分支。	READY
120813_swb_lowroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-SWB-LOWROOF-01	HIGH	短轴低顶板式货车。	READY
120813_swb_medroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-SWB-MEDROOF-01	HIGH	短轴中顶板式货车。	READY
120813_lwb_lowroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-LOWROOF-01	HIGH	长轴低顶板式货车。	READY
120813_lwb_medroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-MEDROOF-01	HIGH	长轴中顶板式货车。	READY
120813_lwb_highroof	120813	Van	Transporter T6			EU-VW-TRANSPORTER-T6-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶板式货车。	READY
120815_singlecab_chassis	120815	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120815_doublecab_chassis	120815	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120815_singlecab_dropside	120815	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120815_doublecab_dropside	120815	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120822_singlecab_chassis	120822	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120822_doublecab_chassis	120822	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120822_singlecab_dropside	120822	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120822_doublecab_dropside	120822	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120823_singlecab_chassis	120823	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘分支。	READY
120823_doublecab_chassis	120823	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘分支。	READY
120823_singlecab_dropside	120823	Pickup	Transporter T6		2	EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室栏板分支。	READY
120823_doublecab_dropside	120823	Pickup	Transporter T6		4	EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室栏板分支。	READY
120842	120842	Sedan	Optima IV (JF)	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
120843	120843	SUV	Niro I	DE	5	EU-KIA-NIRO-I-PHEV-SUV-01	HIGH		READY
120845_singlecab_l2	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	MEDIUM	L2单排驾驶室底盘分支。	READY
120845_singlecab_l3	120845	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	MEDIUM	L3单排驾驶室底盘分支。	READY
120845_doublecab_l3	120845	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	MEDIUM	L3双排驾驶室底盘分支。	READY
120846_singlecab_l2	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120846_singlecab_l3	120846	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120846_doublecab_l3	120846	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
120847_singlecab_l2	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	HIGH	L2单排驾驶室底盘分支。	READY
120847_singlecab_l3	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	HIGH	L3单排驾驶室底盘分支。	READY
120847_singlecab_l4	120847	Pickup	Boxer II facelift		2	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	HIGH	L4单排驾驶室底盘分支。	READY
120847_doublecab_l3	120847	Pickup	Boxer II facelift		4	EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	HIGH	L3双排驾驶室底盘分支。	READY
120851	120851	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
120853	120853	Sedan	Legacy VI	BN	4	EU-SUBARU-LEGACY-BN-SEDAN-01	HIGH		READY
120880_swb	120880	Pickup	K-Series I	EQ1021NF	4	EU-DONGFENG-XIAOKANG-K02-PICKUP-SWB-01	MEDIUM	1.0短轴双排皮卡分支。	READY
120880_stdwb	120880	Pickup	K-Series I	EQ1021NF	4	EU-DONGFENG-XIAOKANG-K02-PICKUP-STANDARD-WB-01	MEDIUM	1.0标准轴距双排皮卡分支。	READY
120892	120892	Wagon	Passat B8 Alltrack	3G5	5	EU-VW-PASSAT-B8-ALLTRACK-WAGON-01	HIGH		READY
120900	120900	Sedan	S4 B9	B9	4	EU-AUDI-S4-B9-SEDAN-01	HIGH		READY
120901	120901	Wagon	S4 B9	8W5	5	EU-AUDI-S4-B9-AVANT-WAGON-01	HIGH		READY
120920	120920	Coupe	Chiron I		2	EU-BUGATTI-CHIRON-COUPE-01	HIGH		READY
121049	121049	Convertible	E-Mehari		2	EU-CITROEN-E-MEHARI-CONVERTIBLE-01	HIGH		READY
121091	121091	Coupe	i20 II	GB	3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH		READY
121094	121094	Coupe	i20 II	GB	3	EU-HYUNDAI-I20-II-COUPE-3D-01	HIGH		READY
121100_prefl	121100	Convertible	3 Series E93 pre-facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	2010 LCI前物理外廓。	READY
121100_facelift	121100	Convertible	3 Series E93 facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	2010 LCI后物理外廓。	READY
121102_prefl	121102	Convertible	3 Series E93 pre-facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH	2010 LCI前物理外廓。	READY
121102_facelift	121102	Convertible	3 Series E93 facelift	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH	2010 LCI后物理外廓。	READY
121109	121109	SUV	Creta I	GS	5	EU-HYUNDAI-CRETA-I-SUV-01	HIGH	2.0前驱五门分支。	READY
121146	121146	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
121173	121173	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121176	121176	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121177	121177	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121180	121180	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121181	121181	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121182	121182	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121183	121183	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	MEDIUM	1.4 TSI 150 PS对应BlueGT高度分支。	READY
121186	121186	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121188	121188	Van	Polo V facelift	6C1	3	EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	MEDIUM	CityVan三门商用外廓。	READY
121201	121201	Sedan	CT6 I		4	EU-CADILLAC-CT6-I-SEDAN-01	HIGH		READY
121220	121220	SUV	C-HR I	NGX10	5	EU-TOYOTA-C-HR-I-SUV-01	HIGH	前驱1.2T NGX10分支。	READY
121226_van_l1	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	HIGH	短轴板式货车分支。	READY
121226_van_l2	121226	Van	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	HIGH	长轴板式货车分支。	READY
121226_dciv_l1	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	HIGH	短轴双排座厢式车分支。	READY
121226_dciv_l2	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	HIGH	长轴双排座厢式车分支。	READY
121226_kombi_l2	121226	MPV	Transit Connect II	V408		EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	HIGH	长轴七座Kombi分支。	READY
121228	121228	Coupe	C8 Preliator		2	EU-SPYKER-C8-PRELIATOR-COUPE-01	HIGH		READY
121230	121230	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-SUV-01	HIGH		READY
121235	121235	Convertible	595C facelift	312	2	EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	HIGH		READY
121236_prefl	121236	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款前分支。	READY
121236_facelift	121236	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款后分支。	READY
121237_prefl	121237	Van	Focus III pre-facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款前分支。	READY
121237_facelift	121237	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck五门商用外廓；改款后分支。	READY
121238	121238	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121239	121239	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121240	121240	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121242	121242	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121243	121243	Van	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	MEDIUM	Kasten/Schrägheck按五门商用外廓。	READY
121249	121249	Sedan	Civic IX	FB	4	EU-HONDA-CIVIC-IX-SEDAN-01	HIGH		READY
121297	121297	Convertible	Spider Series 2	105	2	EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	HIGH	2000 Veloce方尾第二系列。	READY
121304	121304	Coupe	V8 Vantage N400		2	EU-ASTON-MARTIN-V8-VANTAGE-N400-COUPE-01	HIGH		READY
121337	121337	Convertible	3 Series E30 Baur TC	E30	2	EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	HIGH	Baur Top-Cabrio物理外廓。	READY
121416	121416	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121440	121440	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	HIGH	2.0D 180板式Kasten对应Medium车身。	READY
121442	121442	Sedan	Tipo II	356	4	EU-FIAT-TIPO-356-SEDAN-01	HIGH		READY
121445	121445	Hatchback	500 facelift	312	3	EU-FIAT-500-312-FACELIFT-HATCHBACK-3D-01	HIGH		READY
121446	121446	Hatchback	595 facelift	312	3	EU-ABARTH-595-312-FACELIFT-HATCHBACK-3D-01	HIGH		READY
121480_regular_longbed	121480	Pickup	Silverado 2500HD I	GMT800	2	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-RWD-01	MEDIUM	后驱Regular Cab长货斗分支。	READY
121480_extended_shortbed	121480	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	MEDIUM	Extended Cab标准货斗分支。	READY
121480_extended_longbed	121480	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	MEDIUM	Extended Cab长货斗分支。	READY
121480_crew_shortbed	121480	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	MEDIUM	Crew Cab标准货斗分支。	READY
121480_crew_longbed	121480	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	MEDIUM	Crew Cab长货斗分支。	READY
121481_regular_longbed	121481	Pickup	Silverado 2500HD I	GMT800	2	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	MEDIUM	四驱Regular Cab长货斗分支。	READY
121481_extended_shortbed	121481	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	MEDIUM	四驱Extended Cab标准货斗分支。	READY
121481_extended_longbed	121481	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	MEDIUM	四驱Extended Cab长货斗分支。	READY
121481_crew_shortbed	121481	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	MEDIUM	四驱Crew Cab标准货斗分支。	READY
121481_crew_longbed	121481	Pickup	Silverado 2500HD I	GMT800	4	EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	MEDIUM	四驱Crew Cab长货斗分支。	READY
121493	121493	Coupe	S5 II (F5)	F5	2	EU-AUDI-S5-F5-COUPE-01	HIGH		READY
121494	121494	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121495	121495	Coupe	A5 II (F5)	F5	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
121496	121496	Pickup	Avalanche II	GMT900	4	EU-CHEVROLET-AVALANCHE-II-PICKUP-01	HIGH		READY
121499	121499	Pickup	Courier Brazil Mk V		2	EU-FORD-COURIER-BRAZIL-MK-V-PICKUP-01	HIGH	巴西版Fiesta衍生单排皮卡。	READY
121500	121500	Hatchback	Twizy I	X09	2	EU-RENAULT-TWIZY-X09-HATCHBACK-01	MEDIUM	Twizy双座四轮车按输入Schrägheck归入Hatchback。	READY
121502	121502	SUV	Cherokee XJ	XJ	5	EU-JEEP-CHEROKEE-XJ-SUV-5D-01	MEDIUM	欧洲2.5五门分支。	READY
121536	121536	Convertible	Fortwo I facelift	A450	2	EU-SMART-FORTWO-A450-CONVERTIBLE-01	HIGH	450系列Cabrio外廓。	READY
121578	121578	MPV	Altea 5P	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH		READY
121586	121586	SUV	SX4 S-Cross I facelift		5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	HIGH		READY
121587	121587	SUV	SX4 S-Cross I facelift		5	EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	HIGH		READY
121601	121601	Hatchback	A3 8V facelift	8V	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH	三门分支。	READY
121603	121603	Hatchback	A3 8V facelift	8V	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH	Sportback五门分支。	READY
121604	121604	Sedan	A3 8V facelift	8V	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
121605	121605	Convertible	A3 8V facelift	8V	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
121616_swb	121616	Sedan	7 Series G11 pre-facelift	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	725d短轴G11分支。	READY
121616_lwb	121616	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	725Ld长轴G12分支。	READY
121617	121617	SUV	X3 F25 facelift	F25	5	EU-BMW-X3-F25-FACELIFT-SUV-01	HIGH		READY
121618	121618	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-01	HIGH		READY
121619_singlecab_mwb_chassis	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	MEDIUM	中轴单排驾驶室裸底盘。	READY
121619_singlecab_lwb_chassis	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室裸底盘。	READY
121619_doublecab_mwb_chassis	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-MWB-01	MEDIUM	中轴双排驾驶室裸底盘。	READY
121619_doublecab_lwb_chassis	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室裸底盘。	READY
121619_singlecab_mwb_dropside	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-MWB-01	MEDIUM	中轴单排驾驶室原厂栏板。	READY
121619_singlecab_lwb_dropside	121619	Pickup	Sprinter II	W906	2	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-LWB-01	MEDIUM	长轴单排驾驶室原厂栏板。	READY
121619_doublecab_mwb_dropside	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-MWB-01	MEDIUM	中轴双排驾驶室原厂栏板。	READY
121619_doublecab_lwb_dropside	121619	Pickup	Sprinter II	W906	4	EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-LWB-01	MEDIUM	长轴双排驾驶室原厂栏板。	READY
121620	121620	Coupe	GT-R R35 phase III	R35	2	EU-NISSAN-GT-R-R35-PHASE-III-COUPE-01	HIGH		READY
121636	121636	Pickup	Dyna 100 Y100	LY100	2	EU-TOYOTA-DYNA-100-LY100-PICKUP-01	MEDIUM	LY100单排平台/栏板外廓。	READY
121645	121645	Wagon	Clio IV facelift	K98	5	EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	HIGH		READY
121646	121646	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121648	121648	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121649	121649	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121650	121650	SUV	3008 II		5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
121651	121651	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
121652	121652	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	HIGH	L2H1单排Platform Cab分支。	READY
121671	121671	Coupe	SLS AMG Electric Drive	N197	2	EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	MEDIUM	Electric Drive N197采用197系列量产双门外廓。	READY
121687	121687	Wagon	ZX	N2	5	EU-CITROEN-ZX-N2-WAGON-01	HIGH	Break五门外廓。	READY
121688_3dr_prefl	121688	Hatchback	ZX Phase I	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前分支。	READY
121688_5dr_prefl	121688	Hatchback	ZX Phase I	N2	5	EU-CITROEN-ZX-N2-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前分支。	READY
121688_3dr_facelift	121688	Hatchback	ZX Phase II	N2	3	EU-CITROEN-ZX-N2-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后分支。	READY
121688_5dr_facelift	121688	Hatchback	ZX Phase II	N2	5	EU-CITROEN-ZX-N2-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后分支。	READY
121698	121698	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
121704	121704	Coupe	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-COUPE-01	HIGH		READY
121706	121706	Convertible	Camaro VI		2	EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	HIGH		READY
121722	121722	Hatchback	Megane III	BZ0	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH		READY
121726	121726	Sedan	E-Class W213 pre-facelift	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH		READY
121773_prefl	121773	Wagon	E-Class S213 pre-facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
121773_facelift	121773	Wagon	E-Class S213 facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	2020改款后物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_401-500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	4140	1800	1593	Kia Europe 2014 Soul official technical specifications	https://press.kia.com/content/kiapress/eu/en/home/models/soul/soul-2014.html
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618	Auto-Data Kia Soul II facelift 2016	https://www.auto-data.net/en/kia-soul-ii-facelift-2016-generation-6006
EU-VW-TRANSPORTER-T6-CHASSIS-SINGLECAB-LWB-01	5300	1904	1948	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-CHASSIS-DOUBLECAB-LWB-01	5300	1904	1960	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-DROPSIDE-SINGLECAB-LWB-01	5500	1994	1848	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-DROPSIDE-DOUBLECAB-LWB-01	5500	1994	1960	Volkswagen Transporter official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Transporter_Range_Specs_Feb2020.pdf
EU-SUBARU-FORESTER-SJ-SUV-01	4595	1795	1735	Automobile-Catalog 2014 Subaru Forester 2.5i AWD	https://www.automobile-catalog.com/car/2014/3293270/subaru_forester_2_5i_awd.html
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445	Tesla Model S Owner's Manual	https://www.tesla.com/ownersmanual/2012_2020_models/en_cn/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445	Auto-Data Tesla Model S facelift 2016	https://www.auto-data.net/en/tesla-model-s-facelift-2016-generation-5637
EU-VW-TRANSPORTER-T6-BUS-SWB-01	4904	1904	1970	Volkswagen Multivan official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-BUS-LWB-01	5304	1904	1990	Volkswagen Multivan official specifications	https://www.volkswagen.com.au/idhub/content/dam/onehub_pkw/importers/au/pdfs/commercial-vehicles/Volkswagen_Multivan_Specs_Feb2020.pdf
EU-VW-TRANSPORTER-T6-VAN-SWB-LOWROOF-01	4904	1904	1990	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-SWB-MEDROOF-01	4904	1904	2177	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-LOWROOF-01	5304	1904	1990	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-MEDROOF-01	5304	1904	2177	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-VW-TRANSPORTER-T6-VAN-LWB-HIGHROOF-01	5304	1904	2476	Volkswagen Transporter 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-T6-Transporter-2017-UK.pdf
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2534045/kia_optima_sx_2_0_t.html
EU-KIA-NIRO-I-PHEV-SUV-01	4355	1805	1535	Kia Motors Ireland Niro Plug-in Hybrid technical specifications	https://press.kia.com/ie/en/home/media-resouces/press-releases/2017/NiroPHEV_pressrelease.html
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L2-01	5358	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L3-01	5943	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CREW-CAB-L3-01	5843	2050	2254	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-FACELIFT-CHASSIS-CAB-L4-01	6308	2050	2270	Peugeot Boxer conversion base vehicles official prices and specifications brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500	Automobile-Catalog	https://www.automobile-catalog.com/make/ford_europe/mondeo_4gen/mondeo_4gen2_sedan/2011.html
EU-SUBARU-LEGACY-BN-SEDAN-01	4795	1840	1500	Automobile-Catalog 2016 Subaru Legacy 3.6R Limited AWD	https://www.automobile-catalog.com/car/2016/3307955/subaru_legacy_3_6r_limited_awd.html
EU-DONGFENG-XIAOKANG-K02-PICKUP-SWB-01	4000	1560	1870	17VIN Dongfeng Xiaokang K02 1.0 short-wheelbase specifications	https://en.17vin.com/model/k7bxe.html
EU-DONGFENG-XIAOKANG-K02-PICKUP-STANDARD-WB-01	4160	1560	1870	17VIN Dongfeng Xiaokang K02 1.0 standard-wheelbase specifications	https://en.17vin.com/model/7w8qb.html
EU-VW-PASSAT-B8-ALLTRACK-WAGON-01	4777	1832	1506	Volkswagen Passat Estate VIII brochure; Automoli Passat Alltrack B8 technical data	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/passat/estate-v-iii/passat-estate-viii-brochure-dec-2016.pdf; https://www.automoli.com/au/vehicles/volkswagen/passat/passat-alltrack-b8-4676/
EU-AUDI-S4-B9-SEDAN-01	4745	1842	1404	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2223170/audi_s4.html
EU-AUDI-S4-B9-AVANT-WAGON-01	4745	1842	1411	Automobile-Catalog 2017 Audi S4 Avant	https://www.automobile-catalog.com/car/2017/2223185/audi_s4_avant.html
EU-BUGATTI-CHIRON-COUPE-01	4544	2038	1212	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2607230/bugatti_chiron.html
EU-CITROEN-E-MEHARI-CONVERTIBLE-01	3809	1728	1653	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2560220/citroen_e-mehari.html
EU-HYUNDAI-I20-II-COUPE-3D-01	4045	1730	1449	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2161160/hyundai_i20_coupe_1_2.html
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384	BMW Korea 2007 BMW 3 Series Convertible official specifications	https://www.press.bmwgroup.com/korea/article/detail/T0046055KO/bmw-%EC%BD%94%EB%A6%AC%EC%95%84-%EB%89%B4-3%EC%8B%9C%EB%A6%AC%EC%A6%88-%EC%BB%A8%EB%B2%84%ED%84%B0%EB%B8%94-%EA%B5%AD%EB%82%B4-%EC%B6%9C%EC%8B%9C
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	BMW Group 3 Series Convertible E93 official technical data 09/2010	https://www.press.bmwgroup.com/spain/article/attachment/T0084820ES/132013
EU-HYUNDAI-CRETA-I-SUV-01	4270	1780	1630	Hyundai Creta 2016 Owner's Manual; Auto.ru Hyundai Creta 2.0 150 hp specifications	https://www.carmanualsonline.info/hyundai-creta-2016-owner-s-manual/?srch=width; https://auto.ru/catalog/cars/hyundai/creta/20773960/20773995/specifications/20773995_21665614_20795509/
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436	Automobile-Catalog 2017 Alfa Romeo Giulia	https://www.automobile-catalog.com/car/2017/2398430/alfa_romeo_giulia2_2_multijet_ii_16v_150.html
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Automobile-Catalog	https://www.automobile-catalog.com/make/peugeot/3008_2/3008_2_1_2wd/2017.html
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462	Volkswagen Newsroom Polo V vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453	Volkswagen Newsroom Polo V vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-5-profile-20046
EU-CADILLAC-CT6-I-SEDAN-01	5184	1879	1472	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2298170/cadillac_ct6_3_0l_twin_turbo_awd.html
EU-TOYOTA-C-HR-I-SUV-01	4360	1795	1565	Toyota C-HR 2016 European Owner's Manual	https://www.carmanualsonline.info/toyota-c-hr-2016-owners-manual/77
EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	4418	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	4818	1835	1861	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	4418	1835	1836	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	4818	1835	1839	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	4818	1835	1840	Ford Transit Connect official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/commercial-vehicles/BRO-Transit_Connect.pdf
EU-SPYKER-C8-PRELIATOR-COUPE-01	4628	1953	1202	Spyker C8 Preliator official press release	https://archive.spykercars.com/uploads/news/press_release_spyker_C8_preliator.pdf
EU-SUZUKI-VITARA-IV-SUV-01	4175	1775	1610	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/3415805/suzuki_vitara_1_6_allgrip_automatic.html
EU-ABARTH-595C-312-FACELIFT-CONVERTIBLE-01	3660	1627	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2407535/abarth_595c_turismo_mt.html
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484	Automobile-Catalog	https://www.automobile-catalog.com/car/2015/2082500/ford_focus_1_5_ecoboost_182.html
EU-HONDA-CIVIC-IX-SEDAN-01	4545	1755	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2084555/honda_civic_limousine_1_8_i-vtec.html
EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	4120	1630	1290	Automobile-Catalog 1971 Alfa Romeo 2000 Spider Veloce	https://www.automobile-catalog.com/car/1971/65285/alfa_romeo_2000_spider_veloce.html
EU-ASTON-MARTIN-V8-VANTAGE-N400-COUPE-01	4380	1865	1255	Aston Martin V8 Vantage N400 official brochure	https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_V8_Vantage_N400_brochure.pdf
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380	ADAC BMW 316i Baur Top-Cabrio E30 technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/3er-reihe/e30/348035/
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2430740/audi_a5_coupe_2_0_tfsi_252_quattro_s-tronic.html
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2258690/fiat_tipo_1_4_16v.html
EU-FIAT-500-312-FACELIFT-HATCHBACK-3D-01	3571	1627	1488	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2258765/fiat_500_1_3_multijet_ii_16v_95.html
EU-ABARTH-595-312-FACELIFT-HATCHBACK-3D-01	3660	1627	1485	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2407445/abarth_595_turismo_mt.html
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-RWD-01	5641	2024	1935	Edmunds 2001 Chevrolet Silverado 2500HD Regular Cab Base specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/regular-cab/st-100000654/features-specs/
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-SHORTBED-01	5784	2024	1935	Edmunds 2001 Chevrolet Silverado 2500HD Extended Cab Base specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/extended-cab/st-100000661/features-specs/
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-EXTENDEDCAB-LONGBED-01	6264	2024	1935	Edmunds 2001 Chevrolet Silverado 2500HD Extended Cab long-bed specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/extended-cab/features-specs/
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-SHORTBED-01	6025	2024	1935	Edmunds 2001 Chevrolet Silverado 2500HD Crew Cab short-bed specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/crew-cab/st-100000677/features-specs/
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-CREWCAB-LONGBED-01	6505	2024	1935	Edmunds 2001 Chevrolet Silverado 2500HD Crew Cab long-bed specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/crew-cab/features-specs/
EU-CHEVROLET-SILVERADO-2500HD-GMT800-PICKUP-REGULARCAB-LONGBED-4WD-01	5641	2024	2024	Edmunds 2001 Chevrolet Silverado 2500HD Regular Cab 4WD specifications	https://www.edmunds.com/chevrolet/silverado-2500hd/2001/regular-cab/features-specs/
EU-AUDI-S5-F5-COUPE-01	4692	1846	1368	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2430845/audi_s5_coupe.html
EU-CHEVROLET-AVALANCHE-II-PICKUP-01	5621	2009	1946	Edmunds 2007 Chevrolet Avalanche specifications	https://www.edmunds.com/chevrolet/avalanche/2007/features-specs/
EU-FORD-COURIER-BRAZIL-MK-V-PICKUP-01	4457	1685	1477	Ford Courier technical manual	https://www.todomecanica.com/component/k2/download/2970_51453e9e78423c968d30c16942c47ac0.html
EU-RENAULT-TWIZY-X09-HATCHBACK-01	2337	1237	1454	Renault Twizy official vehicle user manual	https://www.user-manual.renault.com/sites/renault/files/Twizy-913-19_ENG.pdf
EU-JEEP-CHEROKEE-XJ-SUV-5D-01	4200	1720	1621	Automobile-Catalog 1995 Jeep Cherokee 2.5 XLE; Automobile-Catalog 1994 Jeep Cherokee SE 4WD 4-Door 2.5L	https://www.automobile-catalog.com/car/1995/1314410/jeep_cherokee_2_5_xle.html; https://www.automobile-catalog.com/car/1994/1314590/jeep_cherokee_se_4wd_4-door_2_5l.html
EU-SMART-FORTWO-A450-CONVERTIBLE-01	2500	1537	1549	Automobile-Catalog 2004 Smart Fortwo City-Cabrio Smart and Pulse 61	https://www.automobile-catalog.com/car/2004/3154625/smart_fortwo_city-cabrio_smart_and_pulse_61.html
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/3082685/seat_altea_1_4_tsi.html
EU-SUZUKI-SX4-S-CROSS-I-FACELIFT-SUV-01	4300	1765	1580	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/3416630/suzuki_sx4_s-cross_1_4_boosterjet_allgrip.html
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424	Automobile-Catalog 2017 Audi A3 3-door	https://www.automobile-catalog.com/car/2017/2502140/audi_a3_1_0_tfsi_115.html
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426	Automobile-Catalog 2017 Audi A3 Sportback	https://www.automobile-catalog.com/car/2017/2600975/audi_a3_sportback_1_6_tdi_115.html
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416	Automobile-Catalog 2017 Audi A3 Sedan	https://www.automobile-catalog.com/car/2017/2503130/audi_a3_sedan_2_0_t_quattro.html
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409	Automobile-Catalog 2017 Audi A3 Cabriolet	https://www.automobile-catalog.com/car/2017/2502770/audi_a3_cabriolet_1_4_tfsi_150_cod_s-tronic.html
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1467	Carfolio BMW 725d G11 specifications	https://www.carfolio.com/bmw-725d-534996
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1479	Carfolio BMW 725Ld G12 specifications	https://www.carfolio.com/bmw-725ld-534985
EU-BMW-X3-F25-FACELIFT-SUV-01	4657	1881	1661	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2026115/bmw_x3_xdrive30d.html
EU-BMW-X4-F26-SUV-01	4671	1881	1624	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2036225/bmw_x4_xdrive30d.html
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-01	6103	1990	2344	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-01	6863	1990	2335	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-MWB-01	6103	1990	2362	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-DOUBLECAB-LWB-01	6863	1990	2351	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-MWB-01	6245	2130	2344	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-SINGLECAB-LWB-01	6945	2130	2335	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-MWB-01	6155	2130	2362	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-DROPSIDE-DOUBLECAB-LWB-01	7055	2130	2351	Mercedes-Benz Sprinter Cab Chassis official technical brochure	https://xr793.com/wp-content/uploads/2023/10/2014-Mercedes-Benz-Sprinter-Cab-Chassisand-Motorhome-AUS.pdf
EU-NISSAN-GT-R-R35-PHASE-III-COUPE-01	4710	1895	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2409620/nissan_gt-r.html
EU-TOYOTA-DYNA-100-LY100-PICKUP-01	4415	1695	1830	Carlist.my 1996 Toyota Dyna LY100R specifications; RBrake vehicle catalog	https://www.carlist.my/used-cars/1997-toyota-dyna-2-5-lorry/8290360; https://catalogonuevo.rbrake.com/Vehiculo/Details?idTipoVehiculo=2&idVehiculo=121636
EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	4267	1732	1445	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2983790/renault_clio_estate_grandtour_energy_dci_110.html
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971	Renault New Trafic official dimensions appendix	https://www.installeronline.co.uk/wp-content/uploads/2014/09/renault-trafic-2014-specs.pdf
EU-MERCEDES-BENZ-SLS-AMG-197-COUPE-01	4638	1939	1262	Mercedes-Benz Public Archive SLS AMG Coupe technical data; Mercedes-Benz Public Archive SLS AMG 197 series history	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLS-AMG-Coup-2010---2014.xhtml?oid=192608215; https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/SLS-AMG-Coups-der-Baureihe-197-2010---2014.xhtml?oid=6016956
EU-CITROEN-ZX-N2-WAGON-01	4260	1702	1421	Automobile-Catalog 1994 Citroen ZX Break Fugue Avantage 1.9 D	https://www.automobile-catalog.com/car/1994/2032115/citroen_zx_break_fugue_avantage_1_9_d.html
EU-CITROEN-ZX-N2-HATCHBACK-3D-PREFL-01	4071	1688	1397	Automobile-Catalog 1993 Citroen ZX Reflex 1.9 D	https://www.automobile-catalog.com/car/1993/1454570/citroen_zx_reflex_1_9_d.html
EU-CITROEN-ZX-N2-HATCHBACK-5D-PREFL-01	4071	1688	1397	Automobile-Catalog 1993 Citroen ZX Reflex 1.9 D	https://www.automobile-catalog.com/car/1993/1454570/citroen_zx_reflex_1_9_d.html
EU-CITROEN-ZX-N2-HATCHBACK-3D-FACELIFT-01	4070	1688	1399	Automobile-Catalog 1996 Citroen ZX 1.9 D X	https://www.automobile-catalog.com/car/1996/542855/citroen_zx_1_9_d_x.html
EU-CITROEN-ZX-N2-HATCHBACK-5D-FACELIFT-01	4070	1688	1399	Automobile-Catalog 1996 Citroen ZX 1.9 D X	https://www.automobile-catalog.com/car/1996/542855/citroen_zx_1_9_d_x.html
EU-CHEVROLET-CAMARO-VI-COUPE-01	4784	1880	1340	Automoli Chevrolet Camaro VI vehicle specifications	https://www.automoli.com/en/vehicles/chevrolet/camaro/camaro-vi-4993/
EU-CHEVROLET-CAMARO-VI-CONVERTIBLE-01	4784	1897	1344	Automobile-Catalog 2017 Chevrolet Camaro LT Convertible 2.0L Turbo	https://www.automobile-catalog.com/car/2017/2496245/chevrolet_camaro_lt_convertible_2_0l_turbo_automatic.html
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4302	1808	1471	Automobile-Catalog 2014 Renault Megane Hatch 1.6 16V 110	https://www.automobile-catalog.com/car/2014/2960915/renault_megane_hatch_1_6_16v_110.html
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Automobile-Catalog 2016 Mercedes-Benz E 400 4MATIC	https://www.automobile-catalog.com/car/2016/2453300/mercedes-benz_e_400_4matic.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Automobile-Catalog 2016 Mercedes-Benz E 220 d T-Modell	https://www.automobile-catalog.com/car/2016/2453360/mercedes-benz_e_220_d_t-modell.html
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1460	Automobile-Catalog 2021 Mercedes-Benz E 220 d T-Modell	https://www.automobile-catalog.com/car/2021/2968550/mercedes_benz_e_220_d_t-modell.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_401-500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.edmunds.com/chevrolet/silverado-2500hd/2001/regular-cab/features-specs/ "https://www.edmunds.com/chevrolet/silverado-2500hd/2001/regular-cab/features-specs/"
[2]: https://www.carlist.my/used-cars/1997-toyota-dyna-2-5-lorry/8290360 "https://www.carlist.my/used-cars/1997-toyota-dyna-2-5-lorry/8290360"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_401-500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_401-500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（466 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（249 行）

